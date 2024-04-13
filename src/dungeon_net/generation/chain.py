# Functions for generating nodes and node chains
import numpy as np
import networkx as nx
from typing import List, Tuple

from dungeon_net.generation.node import Node, Corridor, Room, Junction
from dungeon_net.generation.node_utils import new_node_name


def generate_node(node_types: List[Node], prev_node: Node,
                  prob_matrix: np.ndarray, previous_nodes: List[Node],
                  num_edges=None,
                  random_edges={Room: {"min_edges": 1, "max_edges": 4},
                                Junction: {"min_edges": 3, "max_edges": 6}}) -> Node:
    # Generates a new node based on probability matrix and previous node
    # Names node based on previous nodes provided, does not add node to the
    # previous_nodes list to return
    prev_node_type = type(prev_node)
    row_idx = node_types.index(prev_node_type)
    node_type = np.random.choice(node_types, p=prob_matrix[row_idx])
    if node_type == Corridor:
        node = Corridor()
    else:
        if num_edges is None:
            num_edges = np.random.randint(random_edges[node_type]["min_edges"],
                                          random_edges[node_type]["max_edges"])
        node = node_type(num_edges)

    node.name = new_node_name(node, previous_nodes)
    return node

def generate_node_chain(chain_length: int, node_types: List[Node],
                        prob_matrix: np.ndarray, start_node: Node,
                        previous_nodes: List[Node], chain_num: int,
                        debug=False) -> Tuple[nx.MultiDiGraph, List]:
    # "chain_length" is how many nodes
    # "node_types" is a list of node types to consider and is the ordering
    # of the "prob_matrix"
    # "prob_matrix" is an NxN matrix with the rows and cols ordered the
    # same way as "node_types", the (ij)th entry is the transition
    # probability from i -> j
    # "start_node" seeds the probability matrix, must be a node within
    # "node_types"
    # "previous_nodes" is a list of _all_ previous nodes to consider when
    # naming (and later generating) the new node, the ones in the generated
    # chain will be added and the new "previous_nodes" list will be
    # returned
    # "chain_num" is the iteration within the overall creation algorithm
    # and is both stored in the node data and used for the color
    G = nx.MultiDiGraph()
    prev_node = start_node
    G.add_node(start_node, chain_num=chain_num)
    for i in range(chain_length):
        node = generate_node(node_types, prev_node, prob_matrix,
                             previous_nodes, num_edges=None)
        if isinstance(node, Room) and node.num_edges < 2 and i < chain_length - 1:
            # Ensure no dead-ends before
            node.num_edges = 2
        # Add nodes with 'chain_num' data
        G.add_node(node, chain_num=chain_num)
        # for now, consider bidirectional movement across all nodes with
        # uniform weights
        G.add_edge(prev_node, node)
        G.add_edge(node, prev_node)
        prev_node.filled_edges += 1
        node.filled_edges += 1

        if debug:
            print(
                f"Iter {i+1} / {chain_length}: Connected new ({node}) to previous ({prev_node})")

        prev_node = node
        previous_nodes.append(prev_node)

    return G, previous_nodes


def generate_chain_join(chain_1: nx.MultiDiGraph,
                        chain_2: nx.MultiDiGraph,
                        chain_length: int,
                        node_types: List[Node],
                        prob_matrix: np.ndarray,
                        previous_nodes: List[Node],
                        chain_num: int,
                        start_node=None, end_node=None,
                        debug=False) -> Tuple[nx.MultiDiGraph, List[Node]]:
    # Join two independent chains by creating a new chain between
    # start_node and end_node. start_node must be in chain_1, end_node
    # must be in chain_2. If either is None, picks a random node that has
    # an available edge
    # Note that the prob_matrix used here should ideally be a different one
    # than that used
    # previous_nodes should be a sequence [[chain_1_nodes], [chain_2_nodes]]
    potential_c1_nodes = [n for n in chain_1.nodes if n.has_free_edges()]
    potential_c2_nodes = [n for n in chain_2.nodes if n.has_free_edges()]
    if not potential_c1_nodes:
        # Pick a random room or junction and add a max edge
        potential_c1_nodes = [n for n in chain_1.nodes if isinstance(
            n, Room) or isinstance(n, Junction)]
        potential_c1_nodes = [np.random.choice(potential_c1_nodes)]
        potential_c1_nodes[0].num_edges += 1
    if not potential_c2_nodes:
        # Pick a random room or junction and add a max edge
        potential_c2_nodes = [n for n in chain_2.nodes if isinstance(
            n, Room) or isinstance(n, Junction)]
        potential_c2_nodes = [np.random.choice(potential_c2_nodes)]
        potential_c2_nodes[0].num_edges += 1

    while start_node is None:
        potential_node = np.random.choice(potential_c1_nodes)
        if potential_node in potential_c2_nodes:
            continue
        start_node = potential_node
    while end_node is None:
        potential_node = np.random.choice(potential_c2_nodes)
        if potential_node in potential_c1_nodes:
            continue
        end_node = potential_node

    if debug:
        print(f"\nJoining Chain ({chain_length} nodes)")
    # Generate a chain with the desired probability matrix starting on
    # start_node
    G, previous_nodes = generate_node_chain(chain_length, node_types,
                                            prob_matrix, start_node,
                                            previous_nodes, chain_num,
                                            debug=debug)
    # Join the last node
    # NOTE: I'm not checking to see if it's possible based on free_edges,
    # this needs to be done!
    G.add_edge(previous_nodes[-1], end_node)
    G.add_edge(end_node, previous_nodes[-1])
    previous_nodes[-1].filled_edges += 1
    end_node.filled_edges += 1
    if debug:
        print(f"Endpoint: Connected ({previous_nodes[-1]}) to ({end_node})")

    # joined_graph = nx.compose(nx.compose(chain_1, chain_2), G)

    return G, previous_nodes

