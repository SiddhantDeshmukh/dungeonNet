# Currently just 2D
from random import randint
from PIL.Image import init
from networkx.generators.community import random_partition_graph
import numpy as np
from typing import Tuple
import networkx as nx
from networkx.drawing.nx_pydot import to_pydot
from dataclasses import dataclass
from itertools import product
import math
import matplotlib.pyplot as plt


X_GRID_CELL_SIZE = 1
Y_GRID_CELL_SIZE = 1

# "primitive" types that construct a dungeon:
# - rooms (+ secret)
#   - rectangular (& square)
#   - circular
#   - polygonal
# - corridors (+ secret)

# Each of these has to be a graph (grid) and specify entry/exit points
# Then the separate graphs need to be connected up into the master
# dungeon graph (grid).

# Any of these primitive types can connect to one another. Logic:
# Rooms most often connected by corridors
# Corridors connected to other corridors mean a change in direction


# Have floor tiles, wall tiles, door tiles, etc

class Tile:
    def __init__(self, position: Tuple[int, int],
                 colour='red'):
        # Replace 'colour' with texture
        self.position = position


class RectangluarRoom:
    def __init__(self, length: float, width: float) -> None:
        self.length = length
        self.width = width
        self.num_x_cells = int(math.ceil(length / X_GRID_CELL_SIZE))
        self.num_y_cells = int(math.ceil(width / Y_GRID_CELL_SIZE))
        self.create_room_graph()

    def create_room_graph(self) -> nx.MultiGraph:
        # Create grid as graph
        room_graph = nx.MultiGraph()
        for x, y in product(range(self.num_x_cells), range(self.num_y_cells)):
            current_tile = Tile((x, y))

            # Create neighbour tiles
            for i in range(x - 1, x + 1):
                if i < 0 or i > self.num_x_cells:
                    continue
                for j in range(y - 1, y + 1):
                    if j < 0 or j > self.num_y_cells:
                        continue
                    neighbour_tile = Tile((i, j))
                    room_graph.add_edge(current_tile, neighbour_tile)

        self.graph = room_graph


class CircularRoom:
    def __init__(self, radius: float) -> None:
        self.radius = radius


square = RectangluarRoom(10, 10)
rectangle = RectangluarRoom(20, 10)
# circle = CircularRoom(20)
# passage_1 = RectangluarRoom(20, 5)
# passage_2 = RectangluarRoom(10, 5)
# passage_2 = RectangluarRoom(10, 5)

# dungeon = nx.MultiGraph()
# dungeon.add_edge(square, rectangle, passage=passage_1)
# dungeon.add_edge(rectangle, circle, passage=passage_2)

# to_pydot(square.graph).write_png('../out/square.png')
# to_pydot(rectangle.graph).write_png('../out/rectangle.png')
# to_pydot(dungeon).write_png('../out/dungeon.png')
# Let's do it without networkx since I could just code it all myself
# 20 x 10 rectangular room coords


def rectangle(length: int, width: int):
    nodes = [[x, y] for x, y in product(range(length), range(width))]
    return nodes


# Function to find NESW neighbours of a given cell
def get_neighbours(node):
    directions = {
        "N": [0, 1],
        "E": [1, 0],
        "S": [0, -1],
        "W": [-1, 0],
        "SW": [-1, -1],
        "NW": [-1, 1],
        "SE": [1, -1],
        "NE": [1, 1]
    }

    result = []
    for d in directions.values():
        neighbour = [node[0] + d[0], node[1] + d[1]]
        if neighbour in all_nodes:  # checking outer scope here!
            result.append(neighbour)

    return result

# Plotting functions


def plot_node(ax, node, style='r.'):
    ax.plot(*node, style)


def plot_grid(ax, grid_nodes):
    cols = list(zip(*grid_nodes))
    ax.plot(*cols, 'r.')


def plot_neighbours(ax, node):
    neighbours = get_neighbours(node)
    for neighbour in neighbours:
        plot_node(ax, neighbour, style='gs')


# Plot
fig, axes = plt.subplots(1, 2)
all_nodes = rectangle(20, 10)

# Initial condition
plot_grid(axes[0], all_nodes)
initial_node = all_nodes[0]
plot_node(axes[0], initial_node, 'bx')
plot_neighbours(axes[0], initial_node)

# Pick a different node (random)
plot_grid(axes[1], all_nodes)
new_node = all_nodes[randint(0, len(all_nodes) - 1)]
plot_node(axes[1], new_node, 'bx')
plot_neighbours(axes[1], new_node)

plt.show()

# So I'm able to generate a grid very easily, the 'get_neighbours()' function
# is essentially getting the edges.
# Let's try a circular room


def circle(radius: int):
    nodes = []
    X = int(radius)
    for x in range(-X, X + 1):
        Y = int((radius*radius - x*x)**0.5)  # bound for y
        for y in range(-Y, Y + 1):
            nodes.append([x, y])

    return nodes


def ellipse(a: int, b: int):
    nodes = []
    X = int(a)
    for x in range(-X, X+1):
        Y = int((b*b - x*x)**0.5)
        for y in range(-Y, Y+1):
            nodes.append([x, y])

    return nodes


radius = 10
all_nodes = circle(radius)
fig, axes = plt.subplots(1, 2)
# Initial condition
plot_grid(axes[0], all_nodes)
initial_node = all_nodes[0]
plot_node(axes[0], initial_node, 'bx')
plot_neighbours(axes[0], initial_node)

# Pick a node at random
plot_grid(axes[1], all_nodes)
new_node = all_nodes[randint(0, len(all_nodes) - 1)]
plot_node(axes[1], new_node, 'bx')
plot_neighbours(axes[1], new_node)

plt.show()
