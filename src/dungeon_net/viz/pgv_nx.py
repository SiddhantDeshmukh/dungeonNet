# Plotting NetworkX as PyGraphViz
import networkx as nx
import matplotlib as mpl

from dungeon_net.generation.node_utils import choose_node_shape, choose_node_style
from dungeon_net.viz.color_utils import tabcmapper


def visualize_dungeon(dungeon: nx.MultiDiGraph,
                      filename: str, cmap=mpl.colormaps["tab20"],
                      cmap_mod=19):
    # Write the dungeon into a PNG, naming the nodes with their names
    # color by chain number
    attrs = {n: {
        "color": tabcmapper(i, cmap=cmap, mod=cmap_mod),
        "shape": choose_node_shape(n),
        "style": choose_node_style(n)
    }
        for n, i in dungeon.nodes(data="chain_num")}
    nx.set_node_attributes(dungeon, attrs)
    A = nx.nx_agraph.to_agraph(dungeon)
    A.layout("dot")
    A.draw(filename)
