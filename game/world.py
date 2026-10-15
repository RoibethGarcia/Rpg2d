"""Rejilla pura y proyección isométrica; el ancla es el vértice superior."""
from collections import deque
from dataclasses import dataclass, field
from math import floor

Cell = tuple[int, int]
DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))  # W, D, S, A


def distance(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


@dataclass
class GridMap:
    width: int
    height: int
    blocked: set[Cell] = field(default_factory=set)

    def in_bounds(self, cell: Cell) -> bool:
        return 0 <= cell[0] < self.width and 0 <= cell[1] < self.height

    def walkable(self, cell: Cell) -> bool:
        return self.in_bounds(cell) and cell not in self.blocked

    def neighbors(self, cell: Cell) -> list[Cell]:
        return [p for dx, dy in DIRECTIONS if self.walkable(p := (cell[0] + dx, cell[1] + dy))]

    def find_path(self, start: Cell, goal: Cell, occupied=(), allow_goal=False) -> list[Cell]:
        """BFS estable; no incluye origen. [] significa origen=destino o sin ruta."""
        occupied = set(occupied)
        if not self.walkable(start) or not self.walkable(goal) or (goal in occupied and not allow_goal):
            return []
        previous = {start: None}
        pending = deque([start])
        while pending:
            current = pending.popleft()
            if current == goal:
                path = []
                while current != start:
                    path.append(current)
                    current = previous[current]
                return path[::-1]
            for neighbor in self.neighbors(current):
                if neighbor in previous or (neighbor in occupied and not (allow_goal and neighbor == goal)):
                    continue
                previous[neighbor] = current
                pending.append(neighbor)
        return []


@dataclass
class Projection:
    tile_width: float = 64
    tile_height: float = 32
    origin: tuple[float, float] = (0, 0)
    camera: tuple[float, float] = (0, 0)

    def __post_init__(self):
        if self.tile_width <= 0 or self.tile_height <= 0:
            raise ValueError("Las dimensiones del tile deben ser positivas")

    def project(self, col, row):
        return ((col - row) * self.tile_width / 2 + self.origin[0] - self.camera[0],
                (col + row) * self.tile_height / 2 + self.origin[1] - self.camera[1])

    def inverse(self, x, y):
        u, v = x - self.origin[0] + self.camera[0], y - self.origin[1] + self.camera[1]
        return u / self.tile_width + v / self.tile_height, v / self.tile_height - u / self.tile_width

    def center(self, cell):
        return self.project(cell[0] + .5, cell[1] + .5)

    def pick(self, x, y):
        """Bordes semiabiertos: floor; negativos no se truncan hacia cero."""
        return tuple(floor(value) for value in self.inverse(x, y))
