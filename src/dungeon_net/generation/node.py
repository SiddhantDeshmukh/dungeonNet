import random
# v abstract for now, not dealing with shapes or prefabs, literally just
# connectivity


class Node:
    def __init__(self, num_edges: int) -> None:
        self.num_edges = num_edges
        self.filled_edges = 0  # counts how many edges have been connected
        self.name = ""
        # maybe name edges and check if locked here

    def __str__(self) -> str:
        # for debugging
        return self.desc()
        return f"{self.name}"

    def desc(self) -> str:
        return f"{self.name} ({(self.__class__.__name__)}) ({self.filled_edges}/{self.num_edges} filled edges)"

    def classname(self) -> str:
        # TODO: make sure this works with room subtypes like "round_room"
        # or "rectangular_room"
        return f"{self.__class__.__name__}"

    def has_free_edges(self) -> bool:
        return self.filled_edges < self.num_edges


class Room(Node):
    def __init__(self, num_edges: int) -> None:
        super().__init__(num_edges)

    @ classmethod
    def random(cls, min_edges=1, max_edges=4):
        return cls(random.randint(min_edges, max_edges))


class Corridor(Node):
    def __init__(self) -> None:
        super().__init__(2)


class Junction(Node):
    def __init__(self, num_edges: int) -> None:
        # min of 2 edges
        if num_edges < 3:
            num_edges = 3
        super().__init__(num_edges)

    @ classmethod
    def random(cls, min_edges=3, max_edges=6):
        return cls(random.randint(min_edges, max_edges))
