# Functions for generating dungeons
from typing import Dict, List, Union, Tuple
import networkx as nx
import numpy as np

from dungeon_net.generation.node import Node, Room, Corridor
from dungeon_net.generation.chain import generate_node_chain, generate_chain_join


def generate_chain_dungeon(num_iter: int, chain_lengths: Union[Tuple, Dict],
                           chain_node_types: List[Node],
                           join_node_types: List[Node],
                           chain_prob_matrix: np.ndarray,
                           join_prob_matrix: np.ndarray,
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
    entrance.name = "Entrance"
    previous_nodes = [entrance]
    chain_steps = 3  # how many chain generation steps are in each iter
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
                                     if n.has_free_edges() and n.num_edges < 5]
            start_node = np.random.choice(potential_start_nodes)
            if start_node.num_edges - start_node.filled_edges < 2:
                start_node.num_edges += 2
        chain_num = chain_steps * i
        # 1. Chain 1 from start_node
        chain_1, previous_nodes = generate_node_chain(chain_length,
                                                      chain_node_types,
                                                      chain_prob_matrix,
                                                      start_node,
                                                      previous_nodes,
                                                      chain_num,
                                                      debug=debug)
        chain_num += 1
        chain_dict[f"{i}_C1"] = chain_1
        # 2. Chain 2 from start_node
        chain_2, previous_nodes = generate_node_chain(chain_length,
                                                      chain_node_types,
                                                      chain_prob_matrix,
                                                      start_node,
                                                      previous_nodes,
                                                      chain_num,
                                                      debug=debug)
        chain_num += 1
        chain_dict[f"{i}_C2"] = chain_2
        # 2.5 Join chains 1 & 2 (randomly picks start and end points)
        joining_chain, previous_nodes = generate_chain_join(chain_1, chain_2,
                                                            join_length,
                                                            join_node_types,
                                                            join_prob_matrix,
                                                            previous_nodes,
                                                            chain_num,
                                                            start_node=None,
                                                            end_node=None,
                                                            debug=debug)
        # Update overall dungeon
        chain_dict[f"{i}_J1"] = joining_chain
        dungeon = nx.compose(dungeon, nx.compose(
            nx.compose(chain_1, chain_2), joining_chain))

    return dungeon, chain_dict
