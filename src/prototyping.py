# %%
# Currently just 2D
from random import randint
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


# %%
square = RectangluarRoom(10, 10)
rectangle = RectangluarRoom(20, 10)
# circle = CircularRoom(20)
# passage_1 = RectangluarRoom(20, 5)
# passage_2 = RectangluarRoom(10, 5)
# passage_2 = RectangluarRoom(10, 5)

# dungeon = nx.MultiGraph()
# dungeon.add_edge(square, rectangle, passage=passage_1)
# dungeon.add_edge(rectangle, circle, passage=passage_2)

to_pydot(square.graph).write_png('../out/square.png')
to_pydot(rectangle.graph).write_png('../out/rectangle.png')
# to_pydot(dungeon).write_png('../out/dungeon.png')

# %%
# Let's do it without networkx since I could just code it all myself
# 20 x 10 rectangular room coords
all_nodes = [[x, y] for x, y in product(range(20), range(10))]


# Function to find NESW neighbours of a given cell
def get_neighbours(node):
  directions = {
      "N": [0, 1],
      "E": [1, 0],
      "S": [0, -1],
      "W": [-1, 0],
      # "SW": [-1, -1],
      # "NW": [-1, 1],
      # "SE": [1, -1],
      # "NE": [1, 1]
  }

  result = []
  for d in directions.values():
    neighbour = [node[0] + d[0], node[1] + d[1]]
    if neighbour in all_nodes:  # checking outer scope here!
      result.append(neighbour)

  return result


# Plot
fig, axes = plt.subplots(1, 2)

cols = list(zip(*all_nodes))
x_grid, y_grid = cols[0], cols[1]

# Initial condition
axes[0].plot(x_grid, y_grid, 'r.')
initial_node = all_nodes[0]
axes[0].plot(initial_node[0], initial_node[1], 'bx')
neighbours = get_neighbours(initial_node)
for node in neighbours:
  axes[0].plot(node[0], node[1], 'gs')

# Pick a different node (random)
axes[1].plot(x_grid, y_grid, 'r.')
new_node = all_nodes[randint(0, len(all_nodes) - 1)]
axes[1].plot(new_node[0], new_node[1], 'bx')
neighbours = get_neighbours(new_node)
for node in neighbours:
  axes[1].plot(node[0], node[1], 'gs')

plt.show()

# %%