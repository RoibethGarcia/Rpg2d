"""Decoración acotada: sprites RGBA cacheados, reloj visual y dos espacios.

Sin acceso al GameState, RNG global, audio, colisiones ni navegación. Los sprites
procedurales se preparan SOLO al cargar. Dibujar no avanza la simulación.
"""
from dataclasses import dataclass
from math import exp, isfinite, pi, sin
from random import Random

import pygame


@dataclass(frozen=True)
class AmbientConfig:
    enabled: bool = True
    particle_intensity: float = .65
    max_particles: int = 36
    max_birds: int = 3
    smoke_frequency: float = 1
    water_speed: float = 1

    def __post_init__(self):
        if type(self.enabled) is not bool:
            raise ValueError('enabled debe ser booleano')
        for name, maximum in (('max_birds', 5), ('max_particles', 64)):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value <= maximum:
                raise ValueError(f'{name} debe ser entero entre 0 y {maximum}')
        for name, maximum in (('particle_intensity', 1), ('smoke_frequency', 3),
                              ('water_speed', 3)):
            value = getattr(self, name)
            if not isfinite(value) or not 0 <= value <= maximum:
                raise ValueError(f'{name} debe estar entre 0 y {maximum}')


@dataclass(frozen=True)
class BackgroundProjection:
    """La MISMA escala cover y recorte que usa la imagen de paisaje fijo."""
    scale: float
    origin: tuple

    def screen(self, point):
        return tuple(o + v * self.scale for o, v in zip(self.origin, point))


def _curve(points, count=16):
    a, b, c, d = points
    result = []
    for i in range(count + 1):
        t = i / count
        weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
        result.append([sum(w*p[axis] for w, p in zip(weights, (a, b, c, d)))
                       for axis in (0, 1)])
    return result


def _bird_sheet():
    """Doce siluetas de ave distante, alas curvas y cuerpo; no iconos en 'V'."""
    sheet = pygame.Surface((48 * 12, 32), pygame.SRCALPHA)
    color = (237, 232, 211, 225)
    for frame in range(12):
        image = sheet.subsurface((frame * 48, 0, 48, 32))
        wing = 11 * sin(frame * 2 * pi / 12)
        for side in (-1, 1):
            upper = _curve(((24, 17), (24 + side*6, 9 + wing*.25),
                            (24 + side*15, 13 + wing), (24 + side*22, 12 + wing)))
            lower = _curve(((24 + side*22, 12 + wing), (24 + side*13, 19 + wing),
                            (24 + side*6, 15), (24, 20)))
            pygame.draw.polygon(image, color, upper + lower)
        pygame.draw.ellipse(image, color, (22, 13, 5, 11))
        pygame.draw.polygon(image, color, ((23, 22), (21, 26), (27, 24)))
    return sheet


def _prepare_birds(sheet, grid):
    """PNG opcional: grilla uniforme, mismo lienzo/ancla en todas las poses."""
    cols, rows = grid
    if (type(cols) is not int or type(rows) is not int or min(cols, rows) <= 0
            or cols * rows > 64 or cols > sheet.get_width() or rows > sheet.get_height()
            or not sheet.get_masks()[3]):
        raise ValueError('Hoja de aves requiere grilla válida (máximo 64 poses) y alfa')
    variants = []
    for width in (11, 14):
        frames = []
        for fade in range(8):
            for index in range(cols * rows):
                row, col = divmod(index, cols)
                left, top = col * sheet.get_width() // cols, row * sheet.get_height() // rows
                cell = pygame.Rect(left, top, (col+1)*sheet.get_width()//cols-left,
                                   (row+1)*sheet.get_height()//rows-top)
                image = pygame.transform.smoothscale(sheet.subsurface(cell),
                    (width, max(1, round(width * cell.height / cell.width))))
                image.set_alpha(round(255 * fade / 7))
                frames.append(image)
        variants.append(tuple(frames))
    return tuple(variants)


def _smoke_frames(scale):
    """Textura suave irregular: suma de lóbulos gaussianos con borde disipado."""
    rng = Random(408)
    lobes = [(rng.uniform(-.35, .35), rng.uniform(-.35, .35), rng.uniform(.25, .4))
             for _ in range(7)]
    texture = pygame.Surface((48, 48), pygame.SRCALPHA)
    for x in range(48):
        for y in range(48):
            u, v = (x-23.5)/23.5, (y-23.5)/23.5
            edge = max(0, 1 - u*u - v*v)**2
            density = sum(exp(-((u-a)**2 + (v-b)**2) / (2*r*r)) for a, b, r in lobes)
            alpha = min(160, round(40 * density * edge * rng.uniform(.85, 1)))
            texture.set_at((x, y), (206, 208, 197, alpha))
    frames = []
    for stage in range(24):
        age = stage / 23
        size = max(2, round((18 + 75 * age) * scale))
        image = pygame.transform.smoothscale(texture, (size, size))
        # Fade-in corto y disipación larga, ya aplicados al alfa por píxel.
        opacity = min(1, age * 8) * (1 - age)**1.25
        image.fill((255, 255, 255, round(230 * opacity)), special_flags=pygame.BLEND_RGBA_MULT)
        frames.append(image)
    return tuple(frames)


def _ripple_sheet():
    """Hoja RGBA cíclica de reflejos, SIN relleno azul ni fondo opaco."""
    sheet = pygame.Surface((128 * 16, 32), pygame.SRCALPHA)
    for frame in range(16):
        image = sheet.subsurface((128 * frame, 0, 128, 32))
        phase = frame / 16
        for i, (x, y) in enumerate(((12, 7), (46, 19), (78, 13), (114, 25))):
            center = (x - phase * 128) % 128
            alpha = round(90 + 45 * sin((phase + i/4) * 2*pi))
            points = [(center + dx, y + sin(dx*pi/16 + i)*1.2) for dx in range(-12, 13)]
            # Copias envueltas: al salir un reflejo entra por el otro borde.
            for offset in (-128, 0, 128):
                pygame.draw.aalines(image, (192, 226, 220, alpha), False,
                                    [(a + offset, b) for a, b in points])
        for x in range(128):
            fade = min(1, x / 10, (127-x) / 10)
            for y in range(32):
                color = image.get_at((x, y))
                color.a = round(color.a * fade)
                image.set_at((x, y), color)
    return sheet


def _fall_sheet():
    """Hoja RGBA cíclica de estelas verticales claras, SIN fondo opaco.

    Cada estela baja un número entero de vueltas por ciclo (1 o 2), de modo que
    el último cuadro enlaza con el primero sin salto.
    """
    width, height, frames = 48, 160, 16
    sheet = pygame.Surface((width * frames, height), pygame.SRCALPHA)
    rng = Random(6021)
    streaks = [(rng.uniform(3, width - 3), rng.uniform(0, height), rng.choice((1, 1, 2)),
                rng.uniform(14, 34), rng.uniform(.6, 1)) for _ in range(11)]
    for frame in range(frames):
        image = sheet.subsurface((width * frame, 0, width, height))
        phase = frame / frames
        for index, (x, y0, speed, length, strength) in enumerate(streaks):
            y = (y0 + phase * height * speed) % height
            x += 1.2 * sin(phase * 2 * pi * speed + index)
            length = round(length * 1.3)
            for step in range(length):
                # Cabeza y cola se desvanecen: se lee como agua, no como un palito.
                taper = sin(pi * (step + .5) / length)
                color = (222, 244, 248, round(150 * strength * taper))
                # Copia envuelta: la cola que sale por abajo entra por arriba.
                for offset in (-height, 0):
                    pygame.draw.line(image, color, (x, y + offset + step),
                                     (x, y + offset + step + 1), 2)
    return sheet


_FLOW_RECORDS = {
    'ripple': {'grid': [16, 1], 'crop': [0, 0, 128, 32], 'frame_seconds': .125},
    'fall': {'grid': [16, 1], 'crop': [0, 0, 48, 160], 'frame_seconds': .06},
}


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


class EnvironmentalEffects:
    """Cupos finitos y trayectorias analíticas: no acumula partículas ni dt perdido.

    Poses: (x, y, variante, frame) para aves, (x, y, etapa) para humo. Posiciones
    redondeadas al muestrear; todas las superficies se comparten entre poses.
    """
    def __init__(self, data, projection, background_projection, viewport,
                 bird_sheet=None, bird_record=None):
        self.config = AmbientConfig(**data.get('settings', {}))
        self.viewport = pygame.Rect(viewport)
        self.projection = projection
        self.emitters = tuple(data['emitters'])
        self.bird_frame_seconds = (bird_record or {}).get('frame_seconds', .085)
        if not isfinite(self.bird_frame_seconds) or self.bird_frame_seconds <= 0:
            raise ValueError('Duración de pose de aves inválida')
        grid = (bird_record or {}).get('grid', (12, 1))
        self.bird_count = grid[0] * grid[1]
        self.bird_frames = _prepare_birds(bird_sheet if bird_sheet is not None else _bird_sheet(), grid)
        self.smoke_frames = _smoke_frames(projection.scale)
        sheets = {'ripple': _ripple_sheet(), 'fall': _fall_sheet()}

        def zone(placement, space, default_kind=None):
            kind = placement.get('kind', default_kind)
            if kind not in _FLOW_RECORDS:
                raise ValueError(f'Tipo de zona de agua inválido: {kind!r}')
            return WaterfallAnimation(sheets[kind], _FLOW_RECORDS[kind], placement, space)

        # `river`: espacio del paisaje, detrás de la placa; sin `kind` es un reflejo.
        self.river = tuple(zone(placement, background_projection, 'ripple')
                           for placement in data['river'])
        # `flows`: espacio de la placa, encima de ella; `kind` es obligatorio.
        self.flows = tuple(zone(placement, projection) for placement in data.get('flows', ()))
        # Carriles laterales, pares próximos para una pequeña bandada. Ni la
        # cámara del jugador ni el zoom alteran el paisaje o sus aves.
        self._tracks = ((-.015, .23, .20, .015, 27.3, 8.1, 6.2, 0),
                        (-.015, .23, .22, .012, 28.1, 9.2, 5.1, 1),
                        (1.015, .77, .32, .023, 31.7, 11.3, 12.0, 0),
                        (.77, 1.015, .47, .016, 34.9, 12.6, -8, 1),
                        (.23, -.015, .39, .018, 26.2, 10.4, -15, 0))
        rng = Random(810)
        self._slots = []
        for slot in range(12):
            for emitter in self.emitters:
                steam = emitter['kind'] == 'steam'
                period = emitter['period'] if steam else 8.6 + rng.random()*1.3
                offset = -slot * (.12 if steam else .67)
                if not steam:
                    offset += 5
                gaps = tuple(period * factor for factor in (.87, 1.12, .96, 1.31)) if steam else ()
                self._slots.append((emitter, period, offset, 3.2 if steam else 5.1,
                                    rng.uniform(12, 27), rng.uniform(52, 85), gaps))
        self.reset()

    def reset(self):
        self.time = 0.0
        self.bird_poses = self.smoke_poses = ()
        self._sample()

    def update(self, dt):
        if not isfinite(dt) or dt < 0:
            raise ValueError('dt ambiental debe ser finito y no negativo')
        if self.config.enabled:
            self.time += dt
        self._sample()

    def _sample(self):
        if not self.config.enabled:
            self.bird_poses = self.smoke_poses = ()
            return
        birds = []
        for start, end, y, bend, duration, gap, offset, variant in self._tracks[:self.config.max_birds]:
            age = round((self.time + offset) % (duration + gap), 9)
            if self.time + offset < 0 or age >= duration:
                continue
            u = age / duration
            fade = round(7 * min(1, age / 1.5, (duration-age) / 1.5))
            frame = int((self.time + offset + 1e-9) / self.bird_frame_seconds) % self.bird_count
            birds.append((round(self.viewport.x + (start + (end-start)*u)*self.viewport.w),
                          round(self.viewport.y + (y + bend*sin(u*pi*2))*self.viewport.h),
                          variant, fade*self.bird_count + frame))
        smoke = []
        cap = round(self.config.max_particles * self.config.particle_intensity)
        frequency = self.config.smoke_frequency
        if frequency:
            for emitter, period, offset, life, wind, rise, gaps in self._slots[:cap]:
                if gaps:
                    # Ráfagas compartidas por un emisor, separadas por silencios
                    # de distinta duración; no se genera azar dependiente de FPS.
                    phase = (self.time * frequency) % sum(gaps)
                    for gap in gaps:
                        if phase < gap:
                            break
                        phase -= gap
                    age = (phase + offset) / frequency
                else:
                    # El cupo NO permite reciclar una plaza aún visible. Al
                    # saturar la emisión, conservar la vida y su fade-out.
                    cycle = max(period / frequency, life + .02)
                    age = (self.time + offset / frequency) % cycle
                age = round(age, 9)
                if age < 0 or age >= life:
                    continue
                u = age / life
                x, y = self.projection.screen(emitter['point'])
                smoke.append((round(x + (wind*u + 3*sin(u*pi*2))*self.projection.scale),
                              round(y - rise*u*self.projection.scale),
                              min(23, int(u * 24))))
        self.bird_poses, self.smoke_poses = tuple(birds), tuple(smoke)

    def draw_background(self, surface):
        if not self.config.enabled:
            return
        clip = surface.get_clip()
        surface.set_clip(clip.clip(self.viewport))
        for water in self.river:
            water.blit(surface, self.time * self.config.water_speed)
        for x, y, variant, frame in self.bird_poses:
            image = self.bird_frames[variant][frame]
            surface.blit(image, (x-image.get_width()//2, y-image.get_height()//2))
        surface.set_clip(clip)

    def draw_flows(self, surface):
        """Caídas y piletas pintadas en la placa: se dibuja sobre ella, bajo los actores."""
        if not self.config.enabled:
            return
        clip = surface.get_clip()
        surface.set_clip(clip.clip(self.viewport))
        for water in self.flows:
            water.blit(surface, self.time * self.config.water_speed)
        surface.set_clip(clip)

    def draw_smoke(self, surface):
        if not self.config.enabled:
            return
        clip = surface.get_clip()
        surface.set_clip(clip.clip(self.viewport))
        for x, y, stage in self.smoke_poses:
            image = self.smoke_frames[stage]
            surface.blit(image, (x-image.get_width()//2, y-image.get_height()//2))
        surface.set_clip(clip)
