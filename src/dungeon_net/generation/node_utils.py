# Useful functions for operating on and with Nodes
from dungeon_net.generation.node import Node, Corridor
from typing import List


def new_node_name(node: Node, previous_nodes: List[Node]) -> str:
    # Generate a numeric name for the node based on how many previous types
    # of the node there were (always increasing so will always be unique
    # so long as previous_nodes is correctly updated)
    node_base_name = node.classname()
    node_count = len([n for n in previous_nodes
                      if n.classname() == node_base_name])
    node_name = f"{node_base_name}_{node_count+1}"
    return node_name


def choose_node_shape(node: Node) -> str:
    # Chooses a shape based on how many filled and max edges there are, if
    # it's a corridor, no shape
    if isinstance(node, Corridor):
        return "none"
    shape_mapper = {
        1: "square",
        2: "rect",
        3: "invtriangle",
        4: "diamond",
        5: "house"
    }
    shape = shape_mapper[node.num_edges] if node.num_edges in shape_mapper else "circle"
    return shape


def choose_node_style(node: Node) -> str:
    if node.has_free_edges():
        style = "dashed"
    else:
        style = "solid"
    return style
