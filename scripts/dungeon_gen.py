# Just testing connectivity and generation algorithm with networkx
# Nodes = [Rooms, Corridors, Junctions]
# Rooms = node with 1+ edges
# Corridors = node with 2 edges
# Junction = node with 2+ edges
# Generation rules:
# Rooms can connect to corridors
# Corridors can connect to rooms or junctions
# Junctions can connect to corridors
# This is codified through probability matrices to allow for us changing it
# later if we find it is not what we want, e.g. we may want to allow
# junctions and rooms to connect directly
#
# let "Entrance" have 2 edges to corridors
# The algorithm idea:
# 1. Starting from "Entrance", generate a chain of nodes from edge1
# 2. Starting from "Entrance", generate a secondary chain of nodes from
#    edge2
# 3. Pick a node from 1 and a node from 2 and connect them together with
#    a short tertiary chain, including a junction that branches off into
#    small chain (minimize rooms in this process). Add a "Goal" node that
#    is a suitable distance from the "Entrance"
# 4. Repeat 1-3 as many times as necessary, but move "Entrance" (origin) to
#    a different node
# 5. Place enemies, keys, locks, treasure, asserting that pathways are
#    possible throughout the dungeon.
# NOTE: When generating a "chain" of nodes, specify a weighted DiGraph and
#       assign potential locks. If a pathway is locked, the key must be
#       accessible from another route for the chain to be valid. Rather
#       continuously looping through the chains, can check potential
#       pathways from "Entrance" to "Goal", and if lock/key is
#       inaccessible, just move them around
import networkx as nx
import numpy as np

from dungeon_net.generation.node import Room, Corridor, Junction
from dungeon_net.numerics.array_utils import normalize_matrix
from dungeon_net.generation.dungeon import generate_chain_dungeon
from dungeon_net.viz.pgv_nx import visualize_dungeon


def main():
    entrance = Room(2)  # min of 2
    entrance.name = "Entrance"
    node_types = [Room, Corridor, Junction]
    previous_nodes = [entrance]
    # set up the probability matrix for generation
    chain_prob_matrix = np.zeros((len(node_types), len(node_types)))
    # All values should be proportionate, here they are just straight up
    # probabilities and pre-normalized (rows/cols sum to 1)
    # prob_matrix[0, 0] = 0.0  # room -> room
    chain_prob_matrix[0, 1] = 1.0  # room -> corridor
    # prob_matrix[0, 2] = 0.0  # room -> junction
    chain_prob_matrix[1, 0] = 0.9  # corridor -> room
    # prob_matrix[1, 1] = 0.0  # corridor -> corridor
    chain_prob_matrix[1, 2] = 0.1  # corridor -> junction
    # prob_matrix[2, 0] = 0.0  # junction -> room
    chain_prob_matrix[2, 1] = 1.0  # junction -> corridor
    # prob_matrix[2, 2] = 0.0  # junction -> junction
    chain_prob_matrix = normalize_matrix(chain_prob_matrix)
    # New probability matrix that minimizes rooms
    join_prob_matrix = np.zeros_like(chain_prob_matrix)
    # join_prob_matrix[0, 0] = 0.0  # room -> room
    join_prob_matrix[0, 1] = 1.0  # room -> corridor
    # join_prob_matrix[0, 2] = 0.0  # room -> junction
    join_prob_matrix[1, 0] = 0.3  # corridor -> room
    # join_prob_matrix[1, 1] = 0.0  # corridor -> corridor
    join_prob_matrix[1, 2] = 0.7  # corridor -> junction
    # join_prob_matrix[2, 0] = 0.0  # junction -> room
    join_prob_matrix[2, 1] = 1.0  # junction -> corridor
    chain_lengths = {
        0: (7, 4),
        1: (6, 3),
        2: (6, 3),
    }
    dungeon, chain_dict = generate_chain_dungeon(3, chain_lengths,
                                                 node_types, node_types,
                                                 chain_prob_matrix,
                                                 join_prob_matrix,
                                                 debug=True)
    print(f"\nDungeon: {dungeon}")
    visualize_dungeon(dungeon, "../out/dungeon.png")
    # join_prob_matrix[2, 2] = 0.0  # junction -> junction
    # # 1. chain 1
    # chain_length = 7
    # print(f"Chain 1 ({chain_length} nodes)")
    # chain_1, previous_nodes = generate_node_chain(chain_length, node_types,
    #                                               chain_prob_matrix, entrance,
    #                                               previous_nodes,
    #                                               0,
    #                                               debug=True)
    # # 2. chain 2
    # chain_length = 7
    # print(f"\nChain 2 ({chain_length} nodes)")
    # chain_2, previous_nodes = generate_node_chain(chain_length, node_types,
    #                                               chain_prob_matrix, entrance,
    #                                               previous_nodes,
    #                                               1,
    #                                               debug=True)

    # # 2.5: Join chains 1 and 2
    # joining_chain_1, previous_nodes = generate_chain_join(chain_1, chain_2,
    #                                                       4, node_types,
    #                                                       join_prob_matrix,
    #                                                       previous_nodes,
    #                                                       2,
    #                                                       start_node=None,
    #                                                       end_node=None,
    #                                                       debug=True)
    # # Join the entire graph
    # chains = nx.compose(chain_1, chain_2)
    # dungeon = nx.compose(chains, joining_chain_1)
    # visualize_dungeon(chains, "../out/chains.png")


if __name__ == "__main__":
    main()


"""
TODO:
  - visualize_dungeon() function that styles the graph and writes out a png
    - extension: interactive plot instead
  - fill_chain() function that fills in all empty edges with a 'complexity'
    parameter that controls how long each subchain should be
    - allow for generating small loops
  - Add chance for loops in a chain (basically do a chain_join from one node
    to another in the same chain), can do this with fill_chain
  - room templates for each, random choice can then pick one of those
  - Do step 3 properly with a "Goal" node
  - generating "num_edges" should be weighted
  - Add "data" to each node describing when it was generated, what it
    contains and anything else that may be useful
  - could make chain_num a float so that e.g. join between chain 1 and 2 is
    1.5
"""
