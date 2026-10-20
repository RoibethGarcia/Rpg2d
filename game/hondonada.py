"""Contrato de la ilustración: navegación lógica y coordenadas de autoría separadas.

El JSON declara CADA arista válida. Ninguna cercanía en pantalla conecta pisos.
Las bandas de selección pertenecen al suelo de rutas explícitas, no al bitmap.
"""
import json
from math import hypot
from itertools import permutations
from pathlib import Path

from game.world import GridMap, DIRECTIONS

DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'hondonada.json'
OUTSIDE = (-1, -1)


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > y) != (b[1] > y):
            crossing = (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]
            if x < crossing:
                inside = not inside
    return inside


def segment_distance(point, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = dx * dx + dy * dy
    t = max(0, min(1, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / length)) if length else 0
    return hypot(point[0] - a[0] - t * dx, point[1] - a[1] - t * dy)


class HondonadaLayout:
    def __init__(self, data):
        self.data = data
        self.nodes = {tuple(n['cell']): n for n in data['nodes']}
        self.routes = data['routes']
        self.stairs = {r['id']: [tuple(c) for c in r['cells']] for r in self.routes if r['stair']}
        if len(self.nodes) != len(data['nodes']):
            raise ValueError('Hondonada: casilla duplicada')
        self.adjacency = {cell: [] for cell in self.nodes}
        for a, b in data['edges']:
            a, b = tuple(a), tuple(b)
            if a not in self.nodes or b not in self.nodes or a == b:
                raise ValueError('Hondonada: arista inválida')
            self.adjacency[a].append(b)
            self.adjacency[b].append(a)
        for cell, n in self.nodes.items():
            x, y = n['center']
            if not (0 <= cell[0] < 24 and 0 <= cell[1] < 16
                    and 0 <= x < data['image_size'][0] and 0 <= y < data['image_size'][1]):
                raise ValueError('Hondonada: nodo fuera de límites')
        reached = set()
        pending = [next(iter(self.nodes))]
        while pending:
            cell = pending.pop()
            if cell not in reached:
                reached.add(cell)
                pending.extend(self.adjacency[cell])
        if reached != self.nodes.keys():
            raise ValueError('Hondonada: suelo o escalera desconectados')

    @classmethod
    def load(cls, map_id='hondonada'):
        path = DATA_PATH.with_name(f'{map_id}.json')
        return cls(json.loads(path.read_text(encoding='utf-8')))

    def grid(self):
        all_cells = {(x, y) for x in range(24) for y in range(16)}
        # WASD mantiene los ejes isométricos: W=NE, D=SE, S=SO, A=NO.
        axes = ((1, -1), (1, 1), (-1, 1), (-1, -1))
        directions = {}
        for cell, neighbors in self.adjacency.items():
            center = self.nodes[cell]['center']
            def alignment(target, axis):
                end = self.nodes[target]['center']
                dx, dy = end[0] - center[0], end[1] - center[1]
                return (dx * axis[0] + dy * 2 * axis[1]) / max(.001, hypot(dx, dy * 2))
            if len(neighbors) > 4:
                raise ValueError('Hondonada: cruce con más de cuatro direcciones')
            # Asignación conjunta: el landing de una escalera no pierde su tecla
            # ante una calle ligeramente más alineada con ese mismo cuadrante.
            allocation = max(permutations(range(4), len(neighbors)),
                             key=lambda indices: sum(alignment(target, axes[i])
                                 for target, i in zip(neighbors, indices)))
            choices = {DIRECTIONS[i]: target for target, i in zip(neighbors, allocation)}
            directions[cell] = choices
        return GridMap(24, 16, all_cells - self.nodes.keys(),
                       {c: tuple(v) for c, v in self.adjacency.items()}, directions)


class HondonadaProjection:
    """Adaptador de pantalla para casillas tabuladas y superficies seleccionables."""
    def __init__(self, layout, viewport):
        self.layout = layout
        w, h = layout.data['image_size']
        self.scale = min(viewport[2] / w, viewport[3] / h)
        self.size = (round(w * self.scale), round(h * self.scale))
        self.origin = (viewport[0] + (viewport[2] - self.size[0]) / 2,
                       viewport[1] + (viewport[3] - self.size[1]) / 2)

    def screen(self, point):
        return (self.origin[0] + point[0] * self.scale,
                self.origin[1] + point[1] * self.scale)

    def source(self, point):
        return ((point[0] - self.origin[0]) / self.scale,
                (point[1] - self.origin[1]) / self.scale)

    def center(self, cell):
        return self.screen(self.layout.nodes[cell]['center'])

    def polygon(self, cell):
        x, y = self.layout.nodes[cell]['center']
        return [self.screen(p) for p in ((x, y - 10), (x + 18, y), (x, y + 10), (x - 18, y))]

    def pick(self, x, y):
        point = self.source((x, y))
        # No selección a través de edificios; las máscaras sólo cubren sus siluetas.
        if any(point_in_polygon(point, layer['polygon']) for layer in self.layout.data['layers']):
            return OUTSIDE
        candidates = {cell for area in self.layout.data.get('areas', [])
                      if point_in_polygon(point, area['polygon'])
                      for cell, node in self.layout.nodes.items() if node['surface'] == area['surface']}
        for route in self.layout.routes:
            if any(segment_distance(point, a, b) <= route['width'] / 2
                   for a, b in zip(route['points'], route['points'][1:])):
                candidates.update(tuple(c) for c in route['cells'])
        if not candidates:
            return OUTSIDE
        return min(candidates, key=lambda c: (hypot(point[0] - self.layout.nodes[c]['center'][0],
                                                   point[1] - self.layout.nodes[c]['center'][1]), c))


# Alias semánticos: el mismo contrato de grafo sirve a ambos escenarios.
AuthoredLayout = HondonadaLayout
AuthoredProjection = HondonadaProjection
