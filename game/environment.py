"""Presentación modular y por capas cacheada; no modifica reglas de campaña."""
import pygame

from game.ambient import BackgroundProjection, EnvironmentalEffects, WaterfallAnimation


def transparent_exterior(source, seeds=()):
    """Retira solo el casi negro (RGB <= 12) conectado al borde, no sombras.

    Máscara de presentación preparada antes de escalar; conserva el alfa y los
    píxeles interiores y nunca modifica la imagen del AssetManager. Las semillas
    autoradas permiten marcar huecos de paisaje cerrados por cables o barandas.
    """
    dark = pygame.mask.from_threshold(source, (0, 0, 0, 255), (13, 13, 13, 255))
    transparent = pygame.mask.from_surface(source, threshold=0)
    transparent.invert()
    dark.draw(transparent, (0, 0))
    exterior = pygame.Mask(source.get_size())
    width, height = source.get_size()
    border = [(x, y) for x in range(width) for y in (0, height - 1)]
    border += [(x, y) for y in range(height) for x in (0, width - 1)]
    border.extend(seeds)
    for point in border:
        if dark.get_at(point) and not exterior.get_at(point):
            exterior.draw(dark.connected_component(point), (0, 0))
    if source.get_masks()[3]:
        result = source.copy()
    else:
        result = pygame.Surface(source.get_size(), pygame.SRCALPHA)
        result.blit(source, (0, 0))
    mask = exterior.to_surface(setcolor=(255, 255, 255, 0),
                               unsetcolor=(255, 255, 255, 255))
    result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return result


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
        self.background = None
        if map_id in ('hondonada', 'puesto', 'planta'):
            seeds = game.manifest['images'][f'{map_id}_plate'].get('exterior_seeds', ())
            source = transparent_exterior(source, seeds)
            # Fondo fijo al viewport: escala proporcional para cubrir, sin bandas
            # ni deformación. No participa en la proyección ni en la cámara.
            landscape = game.assets.get_image(f'{map_id}_background').convert()
            scale = max(viewport.width / landscape.get_width(),
                        viewport.height / landscape.get_height())
            size = (max(viewport.width, round(landscape.get_width() * scale)),
                    max(viewport.height, round(landscape.get_height() * scale)))
            landscape = pygame.transform.smoothscale(landscape, size)
            crop = pygame.Rect((0, 0), viewport.size)
            crop.center = landscape.get_rect().center
            self.background = landscape.subsurface(crop).copy()
            background_projection = BackgroundProjection(scale,
                (viewport.x - crop.x, viewport.y - crop.y))
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
        placement = self.layout.data.get('waterfall')
        self.waterfall = None
        if placement is not None:
            name = placement['image']
            self.waterfall = WaterfallAnimation(game.assets.get_image(name),
                game.manifest['images'][name], placement, self.projection)
        self.effects = None
        ambient = self.layout.data.get('ambient')
        if ambient is not None:
            bird_name = ambient.get('bird_image')
            self.effects = EnvironmentalEffects(ambient, self.projection,
                background_projection, viewport,
                game.assets.get_image(bird_name) if bird_name else None,
                game.manifest['images'][bird_name] if bird_name else None)

    def blit_base(self, surface):
        surface.blit(self.base, self.projection.origin)

    def blit_ambient(self, surface, elapsed):
        # Agua decorativa detrás de actores/primeros planos; sin reglas nuevas.
        if self.effects is not None and not self.effects.config.enabled:
            return
        if self.waterfall is not None:
            speed = self.effects.config.water_speed if self.effects is not None else 1
            self.waterfall.blit(surface, elapsed * speed)
        if self.effects is not None:
            self.effects.draw_flows(surface)
            self.effects.draw_smoke(surface)

    def blit_layer(self, surface, layer):
        surface.blit(layer['image'], self.projection.origin)


# Compatibilidad para callers y pruebas del primer escenario.
LayeredHondonadaArt = LayeredEnvironmentArt
