"""Presentación modular y por capas cacheada; no modifica reglas de campaña."""
from math import isfinite

import pygame


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


class WaterfallAnimation:
    """Superposición local cacheada: nunca avanza el reloj ni modifica el mundo.

    Un único recorte relativo para TODAS las celdas conserva el anclaje. Los
    límites enteros de la grilla absorben el píxel sobrante de la hoja original.
    La máscara autorada limita el agua a la caída, sin pintar caño ni rocas.
    """
    def __init__(self, sheet, record, placement, projection):
        cols, rows = record['grid']
        crop = pygame.Rect(record['crop'])
        self.frame_seconds = record['frame_seconds']
        target = pygame.Rect(placement['rect'])
        if (cols <= 0 or rows <= 0 or min(crop.size) <= 0
                or min(target.size) <= 0 or not isfinite(self.frame_seconds)
                or self.frame_seconds <= 0 or not 0 <= placement['opacity'] <= 255):
            raise ValueError('Configuración de cascada inválida')
        self.position = tuple(round(v) for v in projection.screen(target.topleft))
        size = tuple(max(1, round(v * projection.scale)) for v in target.size)
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.polygon(mask, 'white', [
            (round((x - target.x) * size[0] / target.w),
             round((y - target.y) * size[1] / target.h))
            for x, y in placement['polygon']])
        frames, source_rects = [], []
        for row in range(rows):
            for col in range(cols):
                x, y = col * sheet.get_width() // cols, row * sheet.get_height() // rows
                cell = pygame.Rect(x, y, (col + 1) * sheet.get_width() // cols - x,
                                   (row + 1) * sheet.get_height() // rows - y)
                rect = crop.move(x, y)
                if not cell.contains(rect):
                    raise ValueError('Recorte de cascada fuera de su celda')
                image = pygame.transform.smoothscale(sheet.subsurface(rect), size)
                image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                image.set_alpha(placement['opacity'])
                frames.append(image)
                source_rects.append(rect)
        self.frames = tuple(frames)
        self.source_rects = tuple(source_rects)

    def frame_index(self, elapsed):
        if not isfinite(elapsed) or elapsed < 0:
            raise ValueError('Tiempo de cascada debe ser finito y no negativo')
        # Tolerancia solo para restas/acumulaciones del reloj en fronteras exactas.
        return int((elapsed + 1e-9) / self.frame_seconds) % len(self.frames)

    def blit(self, surface, elapsed):
        surface.blit(self.frames[self.frame_index(elapsed)], self.position)


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

    def blit_base(self, surface):
        surface.blit(self.base, self.projection.origin)

    def blit_ambient(self, surface, elapsed):
        # Agua decorativa detrás de actores/primeros planos; sin reglas nuevas.
        if self.waterfall is not None:
            self.waterfall.blit(surface, elapsed)

    def blit_layer(self, surface, layer):
        surface.blit(layer['image'], self.projection.origin)


# Compatibilidad para callers y pruebas del primer escenario.
LayeredHondonadaArt = LayeredEnvironmentArt
