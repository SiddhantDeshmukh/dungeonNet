# Functions for generating dungeons
from typing import Dict, List, Union, Tuple
import networkx as nx
import numpy as np

from dungeon_net.generation.node import Node, Room, Corridor
from dungeon_net.generation.node_utils import new_node_name
from dungeon_net.generation.chain import generate_node_chain, generate_chain_join, add_edge_to_chain


def generate_chain_dungeon(num_iter: int, chain_lengths: Union[Tuple, Dict],
                           chain_node_types: List[Node],
                           join_node_types: List[Node],
                           chain_prob_matrix: np.ndarray,
                           join_prob_matrix: np.ndarray,
                           max_fill_chain_length: int,
                           fill_complexity=0.5,
                           fill_self_loop_prob=0.1,
                           debug=False) -> Tuple[nx.MultiDiGraph, Dict[str, nx.MultiDiGraph]]:
    # Generates a dungeon with "num_iter" iterations, meant to be a quick
    # way to generate a bunch of interconnected chains
    # "chain_lengths" is either a Tuple[int, int] (chain, join) where the
    # first entry is the chain length of all initial chains, second entry
    # is the chain length of all joins, or it is a Dict[int: Tuple[int, int]]
    # where the keys are the iteration number (and must therefore match with
    # num_iter), and each value is a Tuple as defined above
    # Each iteration creates 2 chains from a starting node and joins them
    # "chain_prob_matrix" is used for all chains, "join_prob_matrix" is
    # used for all joins
    # For finer control in generating dungeons, use the other generating
    # functions directly
    entrance = Room(2)
    entrance.base_name = "Entrance"
    entrance.name = "Entrance"
    previous_nodes = [entrance]
    chain_num = 1
    # Storage for generated dungeon
    dungeon = nx.MultiDiGraph()  # the full graph
    chain_dict = {}  # all the individual chains

    for i in range(num_iter):
        if isinstance(chain_lengths, Dict):
            chain_length, join_length = chain_lengths[i]
        elif isinstance(chain_lengths, Tuple):
            chain_length, join_length = chain_lengths
        else:
            print(
                f"Error, `chain_lengths`  must have type Dict or Tuple but has type{type(chain_lengths)}")
            return -1
        # Choose the starting node for chains 1 & 2
        if i == 0:
            start_node = entrance
        else:
            potential_start_nodes = [n for n in previous_nodes
                                     if not isinstance(n, Corridor)
                                     if n.num_edges < 5]
            start_node = np.random.choice(potential_start_nodes)
            if start_node.num_edges - start_node.filled_edges < 2:
                start_node.num_edges += 2
        if debug:
            print(f"\nIter {i+1}/{num_iter}: Starting from {start_node}")
        # 1.: Chain 1 from start_node
        if debug:
            print(f"\nIter {i+1}/{num_iter}: Chain 1")
        chain_1, previous_nodes = generate_node_chain(chain_length,
                                                      chain_node_types,
                                                      chain_prob_matrix,
                                                      start_node,
                                                      previous_nodes,
                                                      chain_num,
                                                      debug=debug)
        chain_num += 1
        chain_dict[f"{i}_C"] = chain_1
        # 2.: Chain 2 from start_node
        if debug:
            print(f"\nIter {i+1}/{num_iter}: Chain 2")
        chain_2, previous_nodes = generate_node_chain(chain_length,
                                                      chain_node_types,
                                                      chain_prob_matrix,
                                                      start_node,
                                                      previous_nodes,
                                                      chain_num,
                                                      debug=debug)
        chain_num += 1
        chain_dict[f"{i}_C2"] = chain_2
        # 3.: Join chains 1 & 2 (randomly picks start and end points)
        if debug:
            print(f"\nIter {i+1}/{num_iter}: Joining Chain")
        joining_chain, previous_nodes = generate_chain_join(chain_1, chain_2,
                                                            join_length,
                                                            join_node_types,
                                                            join_prob_matrix,
                                                            previous_nodes,
                                                            chain_num,
                                                            start_node=None,
                                                            end_node=None,
                                                            debug=debug)
        chain_dict[f"{i}_J1"] = joining_chain
        chain_num += 1
        # Update overall dungeon
        # dungeon = nx.compose(dungeon, nx.compose(chain_1, chain_2))
        dungeon = nx.compose(dungeon, nx.compose(
            nx.compose(chain_1, chain_2), joining_chain))
        # Fill dungeon
        nodes_to_fill: List[Node] = [n for n in dungeon.nodes
                                     if n.has_free_edges() and not n.name == "Entrance"]
        dungeon, chain_dict, previous_nodes = fill_dungeon(dungeon,
                                                           chain_dict,
                                                           nodes_to_fill,
                                                           max_fill_chain_length,
                                                           chain_node_types,
                                                           chain_prob_matrix,
                                                           previous_nodes,
                                                           chain_num,
                                                           num_iter,
                                                           fill_complexity=fill_complexity,
                                                           fill_self_loop_prob=fill_self_loop_prob,
                                                           debug=debug)
        chain_num += 1

    # Add a goal node towards the end of the dungeon (penultimate chain)
    goal_start_node = list(chain_dict[f"{num_iter-1}_C2"].nodes)[-1]
    goal_start_node.num_edges += 1
    if debug:
        print(f"Adding goal to {goal_start_node.name}")
    goal_chain, previous_nodes = generate_node_chain(2, chain_node_types,
                                                     chain_prob_matrix,
                                                     goal_start_node,
                                                     previous_nodes,
                                                     chain_num, debug=debug)
    chain_num += 1

    goal_node = list(goal_chain.nodes)[-1]
    goal_node.base_name = "Goal"
    goal_node.name = "Goal"
    chain_dict["Goal"] = goal_chain
    dungeon = nx.compose(dungeon, goal_chain)

    return dungeon, chain_dict


def fill_dungeon(dungeon: nx.MultiDiGraph,
                 chain_dict: Dict[str, nx.MultiDiGraph],
                 nodes_to_fill: List[Node],
                 max_chain_length: int,
                 node_types: List[Node],
                 prob_matrix: np.ndarray,
                 previous_nodes: List[Node],
                 chain_num: int,
                 num_iter: int,
                 fill_complexity=0.5,
                 fill_self_loop_prob=0.1,
                 skip_node_names=["Entrance"],
                 debug=False) -> Tuple[nx.MultiDiGraph, Dict[str, nx.MultiDiGraph], List[Node]]:
    # Fill a generated dungeon recursively, sewing up all the empty edges
    # with smaller extra chains
    if debug:
        for n in nodes_to_fill:
            print(f"{n.name} to fill ({n.filled_edges}/{n.num_edges})")

    if not nodes_to_fill:
        return dungeon, chain_dict, previous_nodes
    for node in nodes_to_fill:
        while node.has_free_edges():
            if max_chain_length == 1:
                # Single room to dead-end generation
                new_node = Room(1)
                new_node.name = new_node_name(new_node, previous_nodes)
                if not isinstance(node, Corridor):
                    # Add a corridor
                    corridor = Corridor()
                    corridor.name = new_node_name(corridor, previous_nodes)
                    add_edge_to_chain(dungeon, node, corridor, chain_num)
                    previous_nodes.append(corridor)
                    add_edge_to_chain(dungeon, corridor, new_node, chain_num)
                else:
                    add_edge_to_chain(dungeon, node, new_node, chain_num)
                previous_nodes.append(new_node)
                continue
            chain_length = int(np.random.randint(1,
                                                 max_chain_length + 1) * fill_complexity)
            if chain_length < 1:
                chain_length = 1
            chain, previous_nodes = generate_node_chain(chain_length, node_types,
                                                        prob_matrix, node,
                                                        previous_nodes, chain_num,
                                                        debug=debug)
            dungeon = nx.compose(dungeon, chain)
            chain_dict[f"{num_iter}_F1"] = chain
            # Recurse for newly generated nodes
            new_nodes_to_fill = [n for n in chain if n.has_free_edges()
                                 and not n.name in skip_node_names]
            if debug:
                for n in new_nodes_to_fill:
                    print(
                        f"new {n.name} to fill ({n.filled_edges}/{n.num_edges})")
            # increase complexity, decrease self-loop prob and recurse
            fill_complexity *= 0.95
            fill_self_loop_prob *= 1.05
            max_chain_length -= 2
            if max_chain_length <= 0:
                max_chain_length = 1
            dungeon, chain_dict, previous_nodes = fill_dungeon(dungeon, chain_dict,
                                                               new_nodes_to_fill,
                                                               max_chain_length,
                                                               node_types,
                                                               prob_matrix,
                                                               previous_nodes,
                                                               chain_num,
                                                               num_iter,
                                                               fill_complexity=fill_complexity,
                                                               fill_self_loop_prob=fill_self_loop_prob,
                                                               debug=debug)

    return dungeon, chain_dict, previous_nodes
