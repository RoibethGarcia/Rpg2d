"""Clips de presentación: tiempo en segundos, sin callbacks ni reglas de combate."""
from dataclasses import dataclass
from math import isfinite

import pygame


@dataclass(frozen=True)
class AttackClip:
    """Frames cacheados en ambas orientaciones; consultar nunca muta el mundo."""
    durations: tuple[float, ...]
    right: tuple
    left: tuple

    def frame_index(self, elapsed):
        if not isfinite(elapsed) or elapsed < -1e-9:
            return None
        elapsed = max(0, elapsed)  # Resta de relojes puede producir -1e-16 al empezar.
        boundary = 0
        for index, duration in enumerate(self.durations):
            boundary += duration
            if elapsed + 1e-9 < boundary:
                return index
        return None  # one-shot: no módulo, cola ni evento de impacto.

    def sample(self, elapsed, *, mirrored=False):
        index = self.frame_index(elapsed)
        return None if index is None else (self.left if mirrored else self.right)[index]


def isolate_attack_frames(sheet, record):
    """Máscaras de aislamiento sobre huecos entre poses; conserva RGBA interior."""
    frames = []
    if record['body_height'] <= 0 or not record['frames']:
        raise ValueError('Ataque sin escala corporal o frames')
    for frame in record['frames']:
        rect = pygame.Rect(frame['rect'])
        polygon = frame['isolation_polygon']
        duration = frame['duration']
        anchor = frame['anchor']
        if (rect.width <= 0 or rect.height <= 0 or not sheet.get_rect().contains(rect)
                or not isfinite(duration) or duration <= 0
                or not (0 <= anchor[0] <= rect.width and 0 <= anchor[1] <= rect.height)
                or len(polygon) < 3
                or any(not (0 <= x < rect.width and 0 <= y < rect.height) for x, y in polygon)):
            raise ValueError('Metadatos de ataque inválidos')
        image = sheet.subsurface(rect).copy()
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), polygon)
        image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        frames.append(image)
    return tuple(frames)


def prepare_attack_clip(sources, record, body_height):
    """La escala depende del cuerpo, NO de armas elevadas ni polvo de impacto."""
    factor = body_height / record['body_height']
    right, left = [], []
    for source, frame in zip(sources, record['frames']):
        size = tuple(max(1, round(n * factor)) for n in source.get_size())
        image = pygame.transform.smoothscale(source, size)
        anchor = tuple(round(n * factor) for n in frame['anchor'])
        right.append((image, anchor))
        left.append((pygame.transform.flip(image, True, False),
                     (image.get_width() - anchor[0], anchor[1])))
    return AttackClip(tuple(f['duration'] for f in record['frames']), tuple(right), tuple(left))
