"""Fondo vivo del menú: el paisaje de la planta + el mismo sistema ambiental del juego.

Reutiliza `EnvironmentalEffects` (agua, aves, humo) con zonas autoradas en
`data/menu.json`. Es solo presentación: no conoce el estado de la partida, no
usa audio y todo se prepara UNA vez al construirse, nunca al dibujar.
"""
import json
from pathlib import Path

import pygame

from game.ambient import BackgroundProjection, EnvironmentalEffects

ROOT = Path(__file__).resolve().parents[1]
SCREEN = pygame.Rect(0, 0, 1280, 800)
SHADE = (7, 11, 15)


def _shade():
    """Velo oscuro: más cerrado arriba y abajo, y un halo suave tras el bloque central."""
    shade = pygame.Surface(SCREEN.size, pygame.SRCALPHA)
    for y in range(SCREEN.h):
        edge = abs(y - SCREEN.centery) / SCREEN.centery
        pygame.draw.line(shade, (*SHADE, round(38 + 120 * edge ** 3)), (0, y), (SCREEN.w, y))
    # Halo radial con caída gradual (sin borde): se calcula chico y se escala.
    halo = pygame.Surface((80, 50), pygame.SRCALPHA)
    for x in range(80):
        for y in range(50):
            distance = min(1.0, (((x - 39.5) / 40) ** 2 + ((y - 24.5) / 25) ** 2) ** .5)
            halo.set_at((x, y), (*SHADE, round(135 * (1 - distance) ** 1.6)))
    shade.blit(pygame.transform.smoothscale(halo, (1100, 690)), (90, 55))
    return shade


class MenuBackdrop:
    def __init__(self, game):
        data = json.loads((ROOT / 'data/menu.json').read_text())['ambient']
        landscape = game.assets.get_image('planta_background').convert()
        # Escala "cover" y recorte centrado, igual que el paisaje de los mapas.
        scale = max(SCREEN.w / landscape.get_width(), SCREEN.h / landscape.get_height())
        size = (max(SCREEN.w, round(landscape.get_width() * scale)),
                max(SCREEN.h, round(landscape.get_height() * scale)))
        landscape = pygame.transform.smoothscale(landscape, size)
        crop = pygame.Rect((0, 0), SCREEN.size)
        crop.center = landscape.get_rect().center
        self.image = landscape.subsurface(crop).copy()
        projection = BackgroundProjection(scale, (-crop.x, -crop.y))
        self.effects = EnvironmentalEffects(data, projection, projection, SCREEN)
        self.shade = _shade()

    def reset(self):
        self.effects.reset()

    def update(self, dt):
        self.effects.update(dt)

    def draw(self, surface):
        surface.blit(self.image, (0, 0))
        self.effects.draw_background(surface)
        self.effects.draw_smoke(surface)
        surface.blit(self.shade, (0, 0))
