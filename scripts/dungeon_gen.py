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
from typing import Dict

from dungeon_net.generation.node import Room, Corridor, Junction, Node
from dungeon_net.numerics.array_utils import normalize_matrix
from dungeon_net.generation.dungeon import generate_chain_dungeon
from dungeon_net.viz.pgv_nx import visualize_dungeon


def count_node_types(chain_dict: Dict[str, nx.MultiDiGraph]) -> Dict[Node, int]:
    # Describe the different kinds of chains
    node_count = {"type": {}, "base": {}}
    for k, chain in chain_dict.items():
        for node in chain.nodes:
            node_type = type(node)
            if node_type in node_count["type"]:
                node_count["type"][node_type] += 1
            else:
                node_count["type"][node_type] = 1
            node_base_name = node.base_name
            if node_base_name in node_count["base"]:
                node_count["base"][node_base_name] += 1
            else:
                node_count["base"][node_base_name] = 1

    return node_count


def main():
    SEED = 420
    np.random.seed(SEED)
    entrance = Room(2)  # min of 2
    entrance.name = "Entrance"
    node_types = [Room, Corridor, Junction]
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
        0: (4, 2),
        1: (3, 2),
        2: (3, 2),
        3: (3, 2),
        4: (3, 2),
    }
    num_iter = 5
    dungeon, chain_dict = generate_chain_dungeon(num_iter, chain_lengths,
                                                 node_types, node_types,
                                                 chain_prob_matrix,
                                                 join_prob_matrix,
                                                 max_fill_chain_length=2,
                                                 debug=True)
    print(f"\nDungeon: {dungeon}")
    visualize_dungeon(dungeon, f"../out/dungeon_{SEED}_{num_iter}.png")
    node_type_count = count_node_types(chain_dict)
    print(node_type_count)


if __name__ == "__main__":
    main()


"""
TODO:
  - visualize_dungeon() function that styles the graph and writes out a png
    - extension: interactive plot instead
  - Add chance for loops in a chain (two corridors with the same start and
    end)
  - room templates for each, random choice can then pick one of those
  - Do step 3 properly with a "Goal" node
    - Generally place this about 85% of the way through the dungeon, and
      then generate one-way paths back from the Goal to a random node in
      chains 1 & 2 and (guaranteed to connect back to entrance)
  - Add "data" to each node describing when it was generated, what it
    contains and anything else that may be useful
  - Recursively adding nodes was getting difficult, lots of spaghetti with
    keeping track of "previous_nodes", definitely need to add more helper
    functions and maybe store dungeon data in a struct
  - Write a description function for the dungeon / chain_dict that says
    how many of each kind of Node there are (how many Rooms, Junctions, etc)
NOTE:
  - Running 3 iterations to get 59 nodes and 122 edges is still super fast,
    it will be slower in Godot when we have meshes and creatures, but maybe
    there can be some clever rendering going on there too
  - For "tower defense" missions, the Goal node is just at the entrance
  - one-way paths need to allow the player to "fail forwards", i.e. they
    need to still be able to reach the Goal, and then there needs to be a
    loop back to the start
"""
