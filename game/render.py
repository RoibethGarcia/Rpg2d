"""Proyección y dibujo; ninguna regla de acciones depende de estos píxeles."""
import pygame
from engine.game_object import GameObject
from game.world import Projection
from game.environment import EnvironmentArt, LayeredEnvironmentArt
from game.animation import isolate_attack_frames, prepare_attack_clip

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
    def __init__(self, unit, frames, anchors, attack_clip=None):
        super().__init__(0, 0, frames['front'])
        self.unit = unit
        self.directions = frames
        self.anchors = anchors
        self.facing = 'front'
        self.foot = (0, 0)
        self.attack_clip = attack_clip

    def sync(self, state, projection):
        self.foot = projection.center(self.unit.cell)
        motion = state.motions.get(self.unit.id)
        if motion:
            fraction = min(1, motion.elapsed / motion.duration)
            start, end = projection.center(motion.start), projection.center(motion.end)
            # Interpolar apoyos proyectados, no IDs de casillas de un grafo.
            self.foot = tuple(a + (b - a) * fraction for a, b in zip(start, end))
            if hasattr(projection, 'layout'):
                self.facing = 'rear' if end[1] < start[1] else 'front'
            else:
                dx, dy = motion.end[0] - motion.start[0], motion.end[1] - motion.start[1]
                self.facing = 'rear' if dy < 0 or dx < 0 else 'front'
        self.image = self.directions[self.facing]
        self.rect = self.image.get_rect()
        # Ancla local de cada vista ya escalada, independiente de la caja del arma.
        anchor = self.anchors[self.facing]
        action = state.last_attacks.get(self.unit.id)
        if action is not None and self.attack_clip is not None and state.mode == 'combat' and not motion:
            target = projection.center(action.target_cell)
            frame = self.attack_clip.sample(state.elapsed - action.occurred_at,
                                            mirrored=target[0] < self.foot[0])
            if frame is not None:
                self.image, anchor = frame
                self.rect = self.image.get_rect()
        self.rect.topleft = (round(self.foot[0] - anchor[0]), round(self.foot[1] - anchor[1]))

    def draw(self, surface):
        x, y = self.foot
        color = WATER if self.unit.id == 'vera' else RED
        pygame.draw.ellipse(surface, (11, 16, 19), (x - 17, y - 5, 34, 12))
        pygame.draw.ellipse(surface, color, (x - 16, y - 4, 32, 10), 2)
        super().draw(surface)
        if self.unit.boss:
            # Insignia externa: no pintar encima de la ilustración original.
            top = self.rect.top - 18
            pygame.draw.polygon(surface, AMBER, [(x - 5, top + 4), (x, top), (x + 5, top + 4), (x, top + 8)])
        if self.unit.id == 'vera':
            top = self.rect.top - 18
            pygame.draw.polygon(surface, WATER, [(x, top + 8), (x - 5, top), (x + 5, top)])
        bar(surface, pygame.Rect(round(x - 16), self.rect.top - 7, 32, 4), self.unit.hp, self.unit.max_hp, color)


class WorldVillager(GameObject):
    """Habitante estático sin barra de vida, PA, arma ni representación hostil."""
    def __init__(self, npc, image, anchor, foot):
        super().__init__(0, 0, image)
        self.npc = npc
        self.foot = foot
        self.rect.topleft = (round(foot[0] - anchor[0]), round(foot[1] - anchor[1]))

    def draw(self, surface):
        x,y = self.foot
        pygame.draw.ellipse(surface, (11,16,19), (x-9,y-3,18,6))
        super().draw(surface)
        pygame.draw.circle(surface, AMBER, (round(x), self.rect.top-5), 3, 1)


class WorldRenderer:
    def __init__(self, game):
        self.game = game
        self.type = Typography()
        self.projection = Projection(48, 24, origin=(400, 110))
        self.actors = {}
        self.villagers = {}
        self.environment = EnvironmentArt(game)
        self.hondonada = LayeredEnvironmentArt(game, WORLD_RECT)
        self.puesto = LayeredEnvironmentArt(game, WORLD_RECT, 'puesto')
        self.planta = LayeredEnvironmentArt(game, WORLD_RECT, 'planta')
        self.layered_maps = {'hondonada': self.hondonada, 'puesto': self.puesto,
                             'planta': self.planta}
        self.debug_navigation = False
        self._map_id = None
        self.frames = {}
        self.anchors = {}
        record = game.manifest['images']['villager']
        self.villager_source = game.assets.get_image('villager').subsurface(record['frame'])
        self.villager_anchor = record['anchor']
        for role in ('vera', 'guard', 'boss'):
            self.frames[role] = {}
            self.anchors[role] = {}
            for facing in ('front', 'rear'):
                name = f'{role}_{facing}'
                record = game.manifest['images'][name]
                image = game.assets.get_image(name).subsurface(record['frame'])
                height = record['render_height']
                size = (round(image.get_width() * height / image.get_height()), height)
                # Preparar una sola vez. No deformar el cuerpo ni teñir los PNG.
                self.frames[role][facing] = pygame.transform.smoothscale(image, size)
                self.anchors[role][facing] = (
                    round(record['anchor'][0] * size[0] / image.get_width()),
                    round(record['anchor'][1] * size[1] / image.get_height()))
        record = game.manifest['images']['pipes']
        self.pipe = pygame.transform.scale(game.assets.get_image('pipes').subsurface(record['frame']), (48, 48))
        self.attack_clips = {}
        # Preparar todos los contextos al cargar; nada de I/O, máscaras o escalas por frame.
        for role in ('vera', 'guard', 'boss'):
            record = game.manifest['images'][f'{role}_attack']
            sources = isolate_attack_frames(game.assets.get_image(f'{role}_attack'), record)
            for map_id in ('legacy', *self.layered_maps):
                height = self.frames[role]['front'].get_height()
                if map_id in self.layered_maps:
                    art = self.layered_maps[map_id]
                    base = round(art.layout.data['actor_height'] * art.projection.scale)
                    height *= base / self.frames['vera']['front'].get_height()
                self.attack_clips[map_id, role] = prepare_attack_clip(sources, record, height)

    def attack_active(self, state):
        if state.mode != 'combat':
            return False
        for uid, action in state.last_attacks.items():
            unit = state.player if uid == state.player.id else state.enemies.get(uid)
            if unit is None or unit.hp <= 0:
                continue
            role = 'vera' if uid == state.player.id else ('boss' if unit.boss else 'guard')
            clip = self.attack_clips[state.map_id, role]
            if clip.frame_index(state.elapsed - action.occurred_at) is not None:
                return True
        return False

    def configure(self, state):
        map_id = state.map_id if state is not None else 'legacy'
        if map_id != self._map_id:
            self.actors.clear()
            self.villagers.clear()
            self.projection = (self.layered_maps[map_id].projection if map_id in self.layered_maps
                               else Projection(48, 24, origin=(400, 110)))
            self._map_id = map_id

    def reset(self):
        self.actors.clear()
        self.villagers.clear()
        self.configure(self.game.state)

    def diamond(self, cell):
        if hasattr(self.projection, 'polygon'):
            return self.projection.polygon(cell)
        x, y = self.projection.project(*cell)
        return [(x, y), (x + 24, y + 12), (x, y + 24), (x - 24, y + 12)]

    def tile(self, surface, cell, state, style=None):
        if style is not None:
            # Underlay explícito para las juntas del rombo; la textura viene del atlas.
            pygame.draw.polygon(surface, style['underlay'], self.diamond(cell))
            self.environment.blit(surface, style['floor'], self.projection.center(cell))
            return
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

    def wall(self, surface, cell, style=None):
        if style is not None:
            self.environment.blit(surface, style['wall'], self.projection.center(cell))
            return
        points = self.diamond(cell)
        top = [(x, y - 15) for x, y in points]
        pygame.draw.polygon(surface, (52, 60, 61), [top[3], top[2], points[2], points[3]])
        pygame.draw.polygon(surface, (76, 71, 62), [top[2], top[1], points[1], points[2]])
        pygame.draw.polygon(surface, (104, 104, 87), top)
        pygame.draw.polygon(surface, (124, 118, 87), top, 1)
        x, y = self.projection.center(cell)
        pygame.draw.line(surface, (153, 113, 66), (x - 9, y - 15), (x + 7, y - 7), 2)

    def prop(self, surface, obj, state, style=None):
        if obj.get('presentation') == 'valve':
            x, y = self.projection.center(tuple(obj['cell']))
            active = obj['id'] in state.opened
            color = WATER if active or state.credential else AMBER
            self.environment.blit(surface, 'valve', (x, y))
            pygame.draw.circle(surface, color, (round(x), round(y - 20)), 10, 2)
            self.type.text(surface, 'E: Válvula', (x - 29, y - 44), 18, color)
            return
        if style is not None and obj['kind'] in self.environment.PROP_FRAMES:
            foot = self.projection.center(tuple(obj['cell']))
            self.environment.blit(surface, self.environment.PROP_FRAMES[obj['kind']], foot)
            if obj['kind'] in ('panel', 'mechanism', 'maintenance'):
                active = state.credential if obj['kind'] == 'panel' else obj['id'] in state.opened
                pygame.draw.circle(surface, WATER if active else AMBER, (round(foot[0]), round(foot[1] - 28)), 4)
            return
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
        self.configure(state)
        if state.map_id in self.layered_maps:
            return self.draw_layered(surface, state, hover)
        style = self.environment.style(state.map_id)
        placements = self.environment.placements(state, style) if style is not None else []
        surface.fill(BG)
        for row in range(state.grid.height):
            for col in range(state.grid.width):
                self.tile(surface, (col, row), state, style)
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
        for placement in placements:
            cell = tuple(placement['cell'])
            layers.append((self.projection.center(cell)[1], 1, cell, placement))
        for obj in state.objects:
            if obj['id'] not in state.collected:
                layers.append((self.projection.center(tuple(obj['cell']))[1], 1, tuple(obj['cell']), obj))
        for unit in [state.player, *state.enemies.values()]:
            if unit.hp <= 0:
                continue
            role = 'vera' if unit.id == state.player.id else ('boss' if unit.boss else 'guard')
            if unit.id not in self.actors:
                self.actors[unit.id] = WorldActor(unit, self.frames[role], self.anchors[role],
                                                   self.attack_clips['legacy', role])
            actor = self.actors[unit.id]
            actor.sync(state, self.projection)
            layers.append((actor.foot[1], 2, unit.cell, actor))
        # Desempate por capa y casilla: sin dependencia del orden de sets/dicts.
        for _, layer, cell, value in sorted(layers, key=lambda item: (item[0], item[1], item[2])):
            if layer == 0:
                self.wall(surface, cell, style)
            elif layer == 1:
                if 'frame' in value:
                    self.environment.blit(surface, value['frame'], self.projection.center(cell))
                else:
                    self.prop(surface, value, state, style)
            else:
                value.draw(surface)
        return path, min(len(path), budget)


    def draw_layered(self, surface, state, hover):
        surface.fill(BG)
        art, projection = self.layered_maps[state.map_id], self.projection
        art.blit_base(surface)
        path = state.preview_path(hover) if hover is not None else list(state.route)
        budget = state.player.ap if state.mode == 'combat' else len(path)
        previous = projection.center(state.player.cell)
        for index, cell in enumerate(path):
            point = projection.center(cell)
            color = WATER if index < budget else AMBER
            pygame.draw.line(surface, color, previous, point, 2)
            pygame.draw.circle(surface, color, point, 2)
            previous = point
        if hover in art.layout.nodes:
            pygame.draw.polygon(surface, TEXT, self.diamond(hover), 1)
        layers = [(layer['screen_depth'], 1, layer['id'], layer) for layer in art.layers]
        # La nota existente conserva su regla e identidad, con marcador discreto.
        for obj in state.objects:
            if obj['id'] not in state.collected:
                if obj['kind'] == 'npc':
                    if obj['id'] not in self.villagers:
                        height = round(art.layout.data['actor_height'] * projection.scale)
                        source = self.villager_source
                        factor = height / source.get_height()
                        image = pygame.transform.smoothscale(source, (round(source.get_width()*factor),height))
                        anchor = tuple(round(v*factor) for v in self.villager_anchor)
                        self.villagers[obj['id']] = WorldVillager(obj, image, anchor, projection.center(obj['cell']))
                    actor = self.villagers[obj['id']]
                    layers.append((actor.foot[1], 2, obj['id'], actor))
                else:
                    layers.append((projection.center(tuple(obj['cell']))[1], 0, obj['id'], obj))
        for unit in [state.player, *state.enemies.values()]:
            if unit.hp <= 0:
                continue
            role = 'vera' if unit.id == state.player.id else ('boss' if unit.boss else 'guard')
            if unit.id not in self.actors:
                frames, anchors = {}, {}
                for facing in ('front', 'rear'):
                    source = self.frames[role][facing]
                    # Mantener la escala relativa aprobada del jefe, no igualar
                    # todas las siluetas ni deformar su arma para encajarla.
                    relative = source.get_height() / self.frames['vera'][facing].get_height()
                    height = round(art.layout.data['actor_height'] * projection.scale * relative)
                    factor = height / source.get_height()
                    size = (round(source.get_width() * factor), height)
                    frames[facing] = pygame.transform.smoothscale(source, size)
                    anchors[facing] = tuple(round(v * factor) for v in self.anchors[role][facing])
                self.actors[unit.id] = WorldActor(unit, frames, anchors,
                                                   self.attack_clips[state.map_id, role])
            actor = self.actors[unit.id]
            actor.sync(state, projection)
            layers.append((actor.foot[1], 2, unit.id, actor))
        old_clip = surface.get_clip()
        surface.set_clip(WORLD_RECT)
        for _, kind, _, value in sorted(layers, key=lambda item: item[:3]):
            if kind == 1:
                art.blit_layer(surface, value)
            elif kind == 2:
                value.draw(surface)
            else:
                if state.map_id in ('puesto', 'planta'):
                    self.prop(surface, value, state, {'kind': 'layered'})
                else:
                    x, y = projection.center(tuple(value['cell']))
                    pygame.draw.circle(surface, AMBER, (round(x), round(y - 5)), 3)
        if self.debug_navigation:
            for route in art.layout.routes:
                color = AMBER if route['stair'] else WATER
                pygame.draw.lines(surface, color, False,
                                  [projection.screen(p) for p in route['points']], 1)
                for p in route['points']:
                    pygame.draw.circle(surface, color, projection.screen(p), 2)
            for route in art.layout.routes:
                if route['stair']:
                    x, y = projection.screen(route['points'][0])
                    self.type.text(surface, route['id'].replace('escalera_', ''), (x, y), 18, TEXT)
        for npc in self.villagers.values():
            if (state.interaction_distance(npc.npc['cell'], occupied_goal=True) in (1, 2)
                    and state.active_dialogue is None):
                self.type.text(surface, 'E: Hablar', (npc.foot[0]-25, npc.rect.top-22), 18, AMBER)
        surface.set_clip(old_clip)
        return path, min(len(path), budget)
