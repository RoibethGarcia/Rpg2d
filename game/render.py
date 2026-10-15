"""Proyección y dibujo; ninguna regla de acciones depende de estos píxeles."""
import pygame
from engine.game_object import GameObject
from game.world import Projection

BG = (17, 24, 29)
PANEL = (26, 36, 42)
EDGE = (65, 81, 85)
TEXT = (230, 229, 211)
MUTED = (151, 171, 173)
WATER = (89, 209, 206)
AMBER = (235, 176, 89)
RED = (223, 113, 92)
WORLD_RECT = pygame.Rect(24, 96, 968, 528)


class Typography:
    def __init__(self):
        self.fonts = {size: pygame.font.Font(None, size) for size in (18, 20, 22, 24, 26, 30, 34, 40, 48, 64, 80)}

    def text(self, surface, text, position, size=24, color=TEXT):
        image = self.fonts[size].render(str(text), True, color)
        surface.blit(image, position)
        return image.get_rect(topleft=position)

    def wrapped(self, surface, text, position, width, size=24, color=TEXT, spacing=4):
        x, y = position
        font = self.fonts[size]
        line = ''
        for word in str(text).split():
            candidate = f'{line} {word}'.strip()
            if line and font.size(candidate)[0] > width:
                self.text(surface, line, (x, y), size, color)
                y += font.get_height() + spacing
                line = word
            else:
                line = candidate
        if line:
            self.text(surface, line, (x, y), size, color)
            y += font.get_height() + spacing
        return y


def bar(surface, rect, value, maximum, color):
    pygame.draw.rect(surface, (12, 19, 23), rect, border_radius=3)
    if value > 0:
        pygame.draw.rect(surface, color, (rect.x, rect.y, int(rect.w * value / maximum), rect.h), border_radius=3)


class WorldActor(GameObject):
    """Adaptador visual; la única casilla verdadera pertenece a Unit."""
    def __init__(self, unit, frames):
        super().__init__(0, 0, frames['front'])
        self.unit = unit
        self.directions = frames
        self.facing = 'front'
        self.foot = (0, 0)

    def sync(self, state, projection):
        col, row = self.unit.cell
        motion = state.motions.get(self.unit.id)
        if motion:
            fraction = min(1, motion.elapsed / motion.duration)
            col = motion.start[0] + (motion.end[0] - motion.start[0]) * fraction
            row = motion.start[1] + (motion.end[1] - motion.start[1]) * fraction
            dx, dy = motion.end[0] - motion.start[0], motion.end[1] - motion.start[1]
            self.facing = 'rear' if dy < 0 or dx < 0 else 'front'
        self.image = self.directions[self.facing]
        self.foot = projection.center((col, row))
        self.rect = self.image.get_rect()
        # Manifest humano: ancla (16,31), escala 2. Pie estable al cambiar sprite.
        self.rect.topleft = (round(self.foot[0] - 32), round(self.foot[1] - 62))

    def draw(self, surface):
        x, y = self.foot
        color = WATER if self.unit.id == 'vera' else RED
        pygame.draw.ellipse(surface, (11, 16, 19), (x - 17, y - 5, 34, 12))
        pygame.draw.ellipse(surface, color, (x - 16, y - 4, 32, 10), 2)
        super().draw(surface)
        if self.unit.boss:
            # Insignia y hombros: el jefe no se distingue solamente por color.
            pygame.draw.polygon(surface, AMBER, [(x - 7, y - 59), (x, y - 67), (x + 7, y - 59), (x, y - 51)])
            pygame.draw.line(surface, AMBER, (x - 15, y - 43), (x + 15, y - 43), 4)
        if self.unit.id == 'vera':
            pygame.draw.polygon(surface, WATER, [(x, y - 76), (x - 5, y - 84), (x + 5, y - 84)])
        bar(surface, pygame.Rect(round(x - 16), round(y - 49), 32, 4), self.unit.hp, self.unit.max_hp, color)


class WorldRenderer:
    def __init__(self, game):
        self.game = game
        self.type = Typography()
        self.projection = Projection(48, 24, origin=(400, 110))
        self.actors = {}
        self.frames = {}
        for role, tint in [('vera', (155, 242, 231)), ('guard', (225, 177, 144)), ('boss', (234, 193, 125))]:
            self.frames[role] = {}
            for facing in ('front', 'rear'):
                image = game.assets.get_image('human_' + facing).copy()
                image.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
                self.frames[role][facing] = pygame.transform.scale(image, (64, 64))
        record = game.manifest['images']['pipes']
        self.pipe = pygame.transform.scale(game.assets.get_image('pipes').subsurface(record['frame']), (48, 48))

    def reset(self):
        self.actors.clear()

    def diamond(self, cell):
        x, y = self.projection.project(*cell)
        return [(x, y), (x + 24, y + 12), (x, y + 24), (x - 24, y + 12)]

    def tile(self, surface, cell, state):
        sector = min(2, cell[0] // 8)
        shades = [(68, 69, 62), (66, 76, 73), (66, 76, 83)]
        color = shades[sector]
        if (cell[0] + cell[1]) % 2:
            color = tuple(v + 5 for v in color)
        points = self.diamond(cell)
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (44, 52, 52), points, 1)
        if cell[0] in (7, 15) and cell not in state.grid.blocked:
            pygame.draw.line(surface, (148, 116, 66), points[0], points[1], 2)

    def wall(self, surface, cell):
        points = self.diamond(cell)
        top = [(x, y - 15) for x, y in points]
        pygame.draw.polygon(surface, (52, 60, 61), [top[3], top[2], points[2], points[3]])
        pygame.draw.polygon(surface, (76, 71, 62), [top[2], top[1], points[1], points[2]])
        pygame.draw.polygon(surface, (104, 104, 87), top)
        pygame.draw.polygon(surface, (124, 118, 87), top, 1)
        x, y = self.projection.center(cell)
        pygame.draw.line(surface, (153, 113, 66), (x - 9, y - 15), (x + 7, y - 7), 2)

    def prop(self, surface, obj, state):
        x, y = self.projection.center(tuple(obj['cell']))
        kind = obj['kind']
        if kind == 'medkit':
            pygame.draw.rect(surface, (190, 194, 164), (x - 10, y - 17, 20, 16), border_radius=3)
            pygame.draw.line(surface, (150, 64, 49), (x, y - 15), (x, y - 3), 3)
            pygame.draw.line(surface, (150, 64, 49), (x - 6, y - 9), (x + 6, y - 9), 3)
        elif kind == 'panel':
            pygame.draw.rect(surface, (47, 66, 74), (x - 13, y - 37, 26, 36), border_radius=3)
            pygame.draw.rect(surface, WATER if state.credential else AMBER, (x - 9, y - 32, 18, 13))
            for offset in (-6, 0, 6):
                pygame.draw.circle(surface, (149, 162, 142), (int(x + offset), int(y - 10)), 2)
        elif kind in ('mechanism', 'maintenance'):
            surface.blit(self.pipe, (x - 24, y - 42))
            pygame.draw.circle(surface, WATER if obj['id'] in state.opened else AMBER, (int(x), int(y - 18)), 9, 3)
            pygame.draw.line(surface, AMBER, (x - 6, y - 24), (x + 6, y - 12), 2)
        elif kind == 'note':
            pygame.draw.rect(surface, (187, 176, 139), (x - 6, y - 13, 12, 12))
            pygame.draw.line(surface, (88, 78, 57), (x - 3, y - 9), (x + 3, y - 9), 1)
        elif kind in ('pump', 'tank'):
            pygame.draw.rect(surface, (66, 100, 104), (x - 15, y - 30, 30, 29), border_radius=8)
            pygame.draw.ellipse(surface, (115, 141, 134), (x - 15, y - 35, 30, 12))
            surface.blit(self.pipe, (x - 24, y - 25))

    def draw(self, surface, state, hover):
        surface.fill(BG)
        for row in range(state.grid.height):
            for col in range(state.grid.width):
                self.tile(surface, (col, row), state)
        path = state.preview_path(hover) if hover is not None else list(state.route)
        budget = state.player.ap if state.mode == 'combat' else len(path)
        for index, cell in enumerate(path):
            pygame.draw.polygon(surface, WATER if index < budget else (131, 109, 77), self.diamond(cell), 2)
            x, y = self.projection.center(cell)
            pygame.draw.circle(surface, WATER if index < budget else AMBER, (int(x), int(y)), 3)
        if hover is not None and state.grid.in_bounds(hover):
            pygame.draw.polygon(surface, TEXT, self.diamond(hover), 2)
        layers = []
        for cell in state.grid.blocked:
            layers.append((self.projection.center(cell)[1], 0, cell, None))
        for obj in state.objects:
            if obj['id'] not in state.collected:
                layers.append((self.projection.center(tuple(obj['cell']))[1], 1, tuple(obj['cell']), obj))
        for unit in [state.player, *state.enemies.values()]:
            if unit.hp <= 0:
                continue
            role = 'vera' if unit.id == state.player.id else ('boss' if unit.boss else 'guard')
            if unit.id not in self.actors:
                self.actors[unit.id] = WorldActor(unit, self.frames[role])
            actor = self.actors[unit.id]
            actor.sync(state, self.projection)
            layers.append((actor.foot[1], 2, unit.cell, actor))
        # Desempate por capa y casilla: sin dependencia del orden de sets/dicts.
        for _, layer, cell, value in sorted(layers, key=lambda item: (item[0], item[1], item[2])):
            if layer == 0:
                self.wall(surface, cell)
            elif layer == 1:
                self.prop(surface, value, state)
            else:
                value.draw(surface)
        return path, min(len(path), budget)
