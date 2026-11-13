"""Agua animada en Puesto y Planta: caídas y piletas pintadas, solo decorativas.

SDL dummy comprueba que el dibujo cambia donde debe; NO certifica cómo se ve.
"""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import unittest

import pygame

from game.ambient import BackgroundProjection, EnvironmentalEffects
from game.app import LastValveGame
from game.render import WORLD_RECT

ROOT = Path(__file__).resolve().parents[1]
BASE_AMBIENT = {'settings': {}, 'emitters': [], 'river': []}
SQUARE = [[10, 10], [60, 10], [60, 90], [10, 90]]


def flow(kind='fall', **extra):
    return {'kind': kind, 'rect': [10, 10, 50, 80], 'opacity': 120,
            'polygon': SQUARE, **extra}


class FlowDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = LastValveGame(audio_enabled=False)
        cls.projection = cls.game.scenes['play'].renderer.puesto.projection

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def build(self, **data):
        return EnvironmentalEffects({**BASE_AMBIENT, **data}, self.projection,
                                    BackgroundProjection(1, (0, 0)), WORLD_RECT)

    def test_flows_are_optional_so_hondonada_data_keeps_working(self):
        self.assertEqual(self.build().flows, ())

    def test_unknown_flow_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            self.build(flows=[flow('lava')])

    def test_falls_and_ripples_have_cached_distinct_looping_frames(self):
        for kind in ('fall', 'ripple'):
            fx = self.build(flows=[flow(kind)])
            animation = fx.flows[0]
            self.assertEqual(len(animation.frames), 16)
            distinct = {pygame.image.tobytes(f, 'RGBA') for f in animation.frames}
            self.assertGreaterEqual(len(distinct), 8, kind)
            loop = len(animation.frames) * animation.frame_seconds
            self.assertEqual(animation.frame_index(0), animation.frame_index(loop))

    def test_river_entries_may_be_falls_in_background_space(self):
        fx = self.build(river=[flow('fall')])
        self.assertEqual(len(fx.river), 1)
        self.assertEqual(fx.flows, ())
        surface = pygame.Surface((WORLD_RECT.right, WORLD_RECT.bottom), pygame.SRCALPHA)
        fx.draw_background(surface)
        before = pygame.image.tobytes(surface, 'RGBA')
        fx.update(.2)
        fx.draw_background(surface)
        self.assertNotEqual(before, pygame.image.tobytes(surface, 'RGBA'))

    def test_disabled_effects_and_zero_speed_freeze_flows(self):
        fx = self.build(flows=[flow('fall')])
        canvas = lambda: pygame.Surface((WORLD_RECT.right, WORLD_RECT.bottom), pygame.SRCALPHA)
        fx.config = replace(fx.config, water_speed=0)
        fx.update(.7)
        a, b = canvas(), canvas()
        fx.draw_flows(a)
        fx.update(.7)
        fx.draw_flows(b)
        self.assertEqual(pygame.image.tobytes(a, 'RGBA'), pygame.image.tobytes(b, 'RGBA'))
        fx.config = replace(fx.config, enabled=False, water_speed=1)
        c = canvas()
        fx.draw_flows(c)
        self.assertEqual(pygame.image.tobytes(c, 'RGBA'), pygame.image.tobytes(canvas(), 'RGBA'))

    def test_authored_zones_are_valid_and_inside_their_images(self):
        for map_id in ('puesto', 'planta'):
            data = json.loads((ROOT / f'data/{map_id}.json').read_text())['ambient']
            width, height = json.loads((ROOT / f'data/{map_id}.json').read_text())['image_size']
            zones = [*data.get('flows', ()), *data['river']]
            self.assertGreater(len(zones), 0, map_id)
            for zone in zones:
                x, y, w, h = zone['rect']
                self.assertGreater(w, 0)
                self.assertGreater(h, 0)
                self.assertTrue(0 <= x and x + w <= width and 0 <= y and y + h <= height,
                                (map_id, zone['rect']))
                self.assertIn(zone['kind'], ('fall', 'ripple'))
                self.assertGreaterEqual(len(zone['polygon']), 3)
                for px, py in zone['polygon']:
                    self.assertTrue(x <= px <= x + w and y <= py <= y + h, (map_id, zone['rect'], px, py))


class MapWaterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = LastValveGame(audio_enabled=False)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def open_map(self, map_id):
        self.game.start_new_game(map_id)
        renderer = self.game.scenes['play'].renderer
        art = renderer.layered_maps[map_id]
        fx = art.effects
        self.assertIsNotNone(fx, f'{map_id} debería animar su agua')
        fx.config = replace(fx.config, max_birds=0, particle_intensity=0)
        fx.reset()
        return renderer, fx

    def render(self, renderer):
        self.game.screen.fill((0, 0, 0))
        renderer.draw(self.game.screen, self.game.state, None)
        return self.game.screen.copy()

    def test_puesto_and_planta_declare_falls_and_pools_and_hondonada_is_unchanged(self):
        for map_id in ('puesto', 'planta'):
            _, fx = self.open_map(map_id)
            self.assertTrue(any(f for f in fx.flows), map_id)
        self.game.start_new_game()
        hondonada = self.game.scenes['play'].renderer.hondonada.effects
        self.assertEqual(hondonada.flows, ())

    def test_water_moves_between_frames_and_only_inside_authored_zones(self):
        for map_id in ('puesto', 'planta'):
            renderer, fx = self.open_map(map_id)
            before = self.render(renderer)
            fx.update(.13)
            after = self.render(renderer)
            zones = [pygame.Rect(w.position, w.frames[0].get_size()) for w in (*fx.flows, *fx.river)]
            changed = [(x, y) for x in range(WORLD_RECT.left, WORLD_RECT.right)
                       for y in range(WORLD_RECT.top, WORLD_RECT.bottom)
                       if before.get_at((x, y)) != after.get_at((x, y))]
            self.assertGreater(len(changed), 50, f'{map_id}: el agua no se mueve')
            for x, y in changed:
                self.assertTrue(any(z.collidepoint(x, y) for z in zones), (map_id, x, y))

    def test_water_never_touches_gameplay_state(self):
        for map_id in ('puesto', 'planta'):
            renderer, fx = self.open_map(map_id)
            state = deepcopy(self.game.state.__dict__)
            for _ in range(5):
                fx.update(.1)
                self.render(renderer)
            self.assertEqual(state, self.game.state.__dict__)

    def test_scene_ticks_only_the_active_map_water(self):
        renderer_puesto, fx_puesto = self.open_map('puesto')
        scene = self.game.scenes['play']
        scene.update(.2)
        self.assertAlmostEqual(fx_puesto.time, .2)
        self.game.start_new_game('planta')
        self.assertEqual(fx_puesto.time, 0)


if __name__ == '__main__':
    unittest.main()
