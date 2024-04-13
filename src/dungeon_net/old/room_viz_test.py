# 2D shape generation for rooms
import random
from typing import List, Tuple
from collections import defaultdict
import math
import networkx as nx
import plotly.graph_objects as go


class Coord:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


def are_neighbours(coord1: Coord, coord2: Coord, allow_diag=True) -> bool:
    # checks if 'coord1' and 'coord2' are next to each other
    # Calculate the absolute difference between x and y coordinates
    dx = abs(coord1.x - coord2.x)
    dy = abs(coord1.y - coord2.y)

    # If diagonal moves are allowed, check if both dx and dy are less than or equal to 1
    if allow_diag:
        return dx <= 1 and dy <= 1
    # If diagonal moves are not allowed, check if either dx or dy is exactly 1 (but not both)
    else:
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)


class Room:
    # defined by its "coords", the (x, y) positions that form the interior
    # of the room
    def __init__(self, coords: List[Coord], doors=None,
                 generate_doors=False) -> None:
        # Note on performance: Make sure to store the "tiles" contiguously
        # since it will make creating the network graph easier
        self.coords = coords
        self.doors = doors
        if generate_doors:
            self.generate_doors_from_tiles()

        # assert doors are on the edges

        self.create_room_graph()  # creates the room_graph

    def create_room_graph(self) -> nx.MultiGraph:
        room_graph = nx.MultiGraph()
        for coord1 in self.coords:
            for coord2 in self.coords:
                if are_neighbours(coord1, coord2, allow_diag=True):
                    room_graph.add_edge(coord1, coord2)
                    # door flag?

        self.room_graph = room_graph

    def generate_doors_from_tiles(self):
        # TODO: Find a good metric for where to place doors and how many,
        # then just pick a tile to be a door-tile
        pass

    @classmethod
    def rectangular(cls, length: int, width: int):
        # generate a rectangular room from bottom-left to top-right
        coords: List[Coord] = []
        for x in range(length):
            for y in range(width):
                coords.append(Coord(x, y))
        return cls(coords)

    @classmethod
    def circular(cls, radius: int):
        # generate circular room, starting by creating potential points as
        # a square and then checking if we are within the allowed radius
        coords: List[Coord] = []
        for x in range(radius):
            for y in range(radius):
                if x**2 + y**2 <= radius**2:
                    coords.append(Coord(x, y))

        return cls(coords)


def generate_neighbors(coord: Coord, allow_diag=True) -> List[Coord]:
    if not allow_diag:
        # [left, right, down, up] only
        coords = [
            Coord(coord.x - 1, coord.y),
            Coord(coord.x + 1, coord.y),
            Coord(coord.x, coord.y - 1),
            Coord(coord.x, coord.y + 1),
        ]
    else:
        coords = []
        for x in range(coord.x - 1, coord.x + 2):
            for y in range(coord.y - 1, coord.y + 2):
                coords.append(Coord(x, y))

    return coords


def visualize_room(room: Room, bg_color="black", floor_color="grey",
                   border_color="blue", wall_color="red") -> go.Figure:
    # Draw 1x1 rects for each tile, using the correct floor_color for the
    # floor (coord centers), border_color (between tiles inside) and
    # wall_color (the outer wall)
    fig = go.Figure()
    fig.update_layout(plot_bgcolor=bg_color, grid=None)

    # Initialize border and wall coordinate lists
    borders, walls = {}, {}

    # Iterate over coords
    room_graph: nx.MultiGraph = room.room_graph
    for coord in room.coords:
        x, y = coord.x, coord.y
        # Floor tile
        fig.add_shape(
            type="rect",
            x0=x - 0.5,
            y0=y - 0.5,
            x1=x + 0.5,
            y1=y + 0.5,
            fillcolor=floor_color,
            line=dict(width=0)
        )
        # Check for neighbours in 4 dirs (exclude diagonals here regardless
        # of storage bc we want to draw the correct borders)
        potential_neighbors: List[Coord] = generate_neighbors(coord,
                                                              allow_diag=False)
        actual_neighbors: List[Coord] = list(room_graph.neighbors(coord))
        for neighbor in potential_neighbors:
            dx = neighbor.x - x
            dy = neighbor.y - y
            # if abs(dx) + abs(dy) == 1:
            if dx == 1:  # right neighbor
                line_start, line_end = (x + 0.5, y - 0.5), (x + 0.5, y + 0.5)
            elif dx == -1:  # left neighbor
                line_start, line_end = (x - 0.5, y - 0.5), (x - 0.5, y + 0.5)
            elif dy == 1:  # upper neighbor
                line_start, line_end = (x - 0.5, y + 0.5), (x + 0.5, y + 0.5)
            elif dy == -1:  # lower neighbor
                line_start, line_end = (x - 0.5, y - 0.5), (x + 0.5, y - 0.5)
            # Check if it's a border or a wall node
            is_border = False
            for an in actual_neighbors:
                if neighbor.x == an.x and neighbor.y == an.y:
                    is_border = True
            if is_border:
                borders[line_start] = line_end
            else:  # neighbor does not exist, wall
                walls[line_start] = line_end

    # Draw borders
    for bline_start, bline_end in borders.items():
        fig.add_shape(
            type="line",
            x0=bline_start[0],
            y0=bline_start[1],
            x1=bline_end[0],
            y1=bline_end[1],
            line=dict(color=border_color, width=1)
        )

    # Draw walls
    for wline_start, wline_end in walls.items():
        fig.add_shape(
            type="line",
            x0=wline_start[0],
            y0=wline_start[1],
            x1=wline_end[0],
            y1=wline_end[1],
            line=dict(color=wall_color, width=1)
        )

    return fig


def main():
    rectangular_room: Room = Room.rectangular(10, 5)
    circular_room: Room = Room.circular(4)

    rectangular_room_fig = visualize_room(rectangular_room)
    rectangular_room_fig.show()
    # for coord in rectangular_room.coords:
    #     print(coord)
    #     print([n for n in rectangular_room.room_graph.neighbors(coord)])
    # print(rectangular_room.room_graph.adj)
    # print(circular_room.room_graph.adj)


if __name__ == "__main__":
    main()
