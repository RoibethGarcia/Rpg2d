"""Presentación modular y por capas cacheada; no modifica reglas de campaña."""
import pygame


class EnvironmentArt:
    REQUIRED_MAPS = ('planta',)
    PROP_FRAMES = {'medkit': 'medkit', 'panel': 'panel', 'maintenance': 'valve',
                   'mechanism': 'valve', 'tank': 'tank', 'pump': 'pump'}

    def __init__(self, game):
        self.styles = game.manifest.get('environment_sets', {})
        records = game.manifest.get('environment_frames', {})
        for map_id in self.REQUIRED_MAPS:
            if map_id not in self.styles:
                raise ValueError(f'Falta configuración de escenario: {map_id}')
            for field in ('floor', 'wall', 'placements'):
                if field not in self.styles[map_id]:
                    raise ValueError(f'Escenario {map_id}: falta {field}')
        atlas = game.assets.get_image('environment_atlas')
        self.frames = {}
        for name, record in records.items():
            rect = pygame.Rect(record['frame'])
            if not atlas.get_rect().contains(rect) or min(rect.size) <= 0:
                raise ValueError(f'Frame de escenario inválido: {name}')
            source = atlas.subsurface(rect)
            width = record['render_width']
            if width <= 0:
                raise ValueError(f'Escala de escenario inválida: {name}')
            floor = record['kind'] == 'floor'
            size = (48, 24) if floor else (width, round(source.get_height() * width / source.get_width()))
            image = pygame.transform.smoothscale(source, size)
            if floor:
                # Máscara de presentación intencional: rejilla 2:1 exacta, no colisiones.
                mask = pygame.Surface(size, pygame.SRCALPHA)
                pygame.draw.polygon(mask, 'white', [(24, 0), (47, 12), (24, 23), (0, 12)])
                image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            anchor = record['anchor']
            if not (0 <= anchor[0] <= rect.width and 0 <= anchor[1] <= rect.height):
                raise ValueError(f'Ancla de escenario inválida: {name}')
            self.frames[name] = (image, (round(anchor[0] * size[0] / rect.width),
                                         round(anchor[1] * size[1] / rect.height)))
        for map_id in self.REQUIRED_MAPS:
            style = self.styles[map_id]
            names = [style['floor'], style['wall'], *self.PROP_FRAMES.values(),
                     *(p['frame'] for p in style['placements'])]
            for name in names:
                if name not in self.frames:
                    raise ValueError(f'Escenario {map_id}: falta frame {name}')

    def style(self, map_id):
        if map_id in ('hondonada', 'puesto', 'planta'):
            return {'kind': 'layered', 'image': f'{map_id}_plate', 'placements': []}
        if map_id == 'legacy':
            return None  # Fixture explícita del prototipo geométrico original.
        if map_id not in self.styles:
            raise ValueError(f'No hay arte para el escenario: {map_id}')
        return self.styles[map_id]

    def placements(self, state, style):
        placements = []
        reserved = (state.world.reserved_spawns | {tuple(o['cell']) for o in state.objects}
                    | {e.cell for e in state.world.exits.values()})
        for placement in style['placements']:
            footprint = {tuple(cell) for cell in placement['footprint']}
            cell = tuple(placement['cell'])
            if not footprint or cell not in footprint or not footprint <= state.grid.blocked or footprint & reserved:
                raise ValueError(f'Escenario {state.map_id}: huella visual incompatible {cell}')
            placements.append(placement)
        return placements

    def blit(self, surface, name, foot):
        image, anchor = self.frames[name]
        surface.blit(image, (round(foot[0] - anchor[0]), round(foot[1] - anchor[1])))


class LayeredEnvironmentArt:
    """Plate conservado + siluetas RGBA preparadas UNA vez, sin IO al dibujar.

    Los polígonos son máscaras de presentación, nunca colisiones ni niveles.
    La imagen completa conserva el suelo; sus objetos delanteros se intercalan
    de nuevo sobre los actores según el apoyo, igual que sprites de decorado.
    """
    def __init__(self, game, viewport, map_id='hondonada'):
        from game.hondonada import AuthoredLayout, AuthoredProjection
        self.layout = AuthoredLayout.load(map_id)
        self.projection = AuthoredProjection(self.layout, viewport)
        source = game.assets.get_image(f'{map_id}_plate')
        if source.get_size() != tuple(self.layout.data['image_size']):
            raise ValueError(f'{map_id}: dimensiones de plate incompatibles con navegación')
        self.base = pygame.transform.smoothscale(source, self.projection.size)
        self.layers = []
        for record in self.layout.data['layers']:
            mask = pygame.Surface(source.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(mask, (255, 255, 255, 255), record['polygon'])
            image = source.copy()
            image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.layers.append({**record,
                'image': pygame.transform.smoothscale(image, self.projection.size),
                'screen_depth': self.projection.screen((0, record['depth']))[1]})

    def blit_base(self, surface):
        surface.blit(self.base, self.projection.origin)

    def blit_layer(self, surface, layer):
        surface.blit(layer['image'], self.projection.origin)


# Compatibilidad para callers y pruebas del primer escenario.
LayeredHondonadaArt = LayeredEnvironmentArt
