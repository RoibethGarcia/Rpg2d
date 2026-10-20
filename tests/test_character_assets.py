"""Sustitución estática: PNG propios, escala proporcional y pie lógico estable."""
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

import pygame

from game.app import LastValveGame
from game.model import Motion
from game.render import WorldRenderer

ROOT = Path(__file__).resolve().parents[1]
NAMES = {f'{role}_{view}' for role in ('vera', 'guard', 'boss') for view in ('front', 'rear')}


class CharacterAssetTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)
        self.renderer = self.game.scenes['play'].renderer

    def tearDown(self):
        pygame.quit()

    def records(self):
        images = self.game.manifest['images']
        self.assertTrue(NAMES <= images.keys(), 'Faltan los seis PNG exclusivos de personajes')
        return {name: images[name] for name in NAMES}

    def test_originals_are_local_unchanged_and_provenance_is_not_an_invented_license(self):
        for name, record in self.records().items():
            with self.subTest(name=name):
                self.assertEqual(record['source_type'], 'user_supplied')
                self.assertEqual(record['redistribution_status'], 'pending_confirmation')
                self.assertNotIn('license_file', record)
                path = ROOT / record['path']
                self.assertTrue(path.resolve().is_relative_to(ROOT / 'assets/images/characters'))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['sha256'])
                self.assertTrue((ROOT / record['provenance_file']).is_file())
                self.assertNotIn('Downloads', record['path'])
                self.assertTrue(record['original_path'].endswith('.png'))

    def test_prepared_views_are_their_own_png_without_tint_or_deformation(self):
        for name, record in self.records().items():
            with self.subTest(name=name):
                role, view = name.split('_')
                original = self.game.assets.get_image(name)
                frame = original.subsurface(record['frame'])
                height = record['render_height']
                size = (round(frame.get_width() * height / frame.get_height()), height)
                expected = pygame.transform.smoothscale(frame, size)
                actual = self.renderer.frames[role][view]
                self.assertEqual(actual.get_size(), size)
                self.assertEqual(pygame.image.tobytes(actual, 'RGBA'), pygame.image.tobytes(expected, 'RGBA'))
                self.assertLessEqual(abs(actual.get_width() / actual.get_height() - frame.get_width() / frame.get_height()), 1 / height)
                expected_anchor = (round(record['anchor'][0] * size[0] / frame.get_width()),
                                   round(record['anchor'][1] * size[1] / frame.get_height()))
                self.assertEqual(self.renderer.anchors[role][view], expected_anchor)
                self.assertEqual(actual.get_at((0, 0)).a, 0)

    def test_all_roles_switch_view_with_stable_foot_and_do_not_reload(self):
        from game.content import new_legacy_game
        self.records()
        self.game.start_new_game()
        # Fixture visual explícita con todos los roles; Hondonada no tiene rivales.
        self.game.state = new_legacy_game()
        self.game.scenes['play'].reset()
        state = self.game.state
        with patch.object(self.game.assets, 'load_image') as load:
            for role in ('vera', 'guard', 'boss'):
                unit = state.player if role == 'vera' else next(u for u in state.enemies.values() if u.boss == (role == 'boss'))
                for direction, view in ((1, 'front'), (-1, 'rear')):
                    start = unit.cell
                    end = (start[0] + direction, start[1])
                    state.motions[unit.id] = Motion(start, end, elapsed=.07, duration=.14)
                    self.game.draw_game_elements()
                    actor = self.renderer.actors[unit.id]
                    self.assertIs(actor.image, self.renderer.frames[role][view])
                    self.assertEqual(actor.facing, view)
                    anchor = self.renderer.anchors[role][view]
                    self.assertEqual(actor.rect.topleft, (round(actor.foot[0] - anchor[0]), round(actor.foot[1] - anchor[1])))
                    self.assertEqual(actor.foot, self.renderer.projection.center((start[0] + direction * .5, start[1])))
                    self.assertEqual(unit.cell, start)
                    del state.motions[unit.id]
        load.assert_not_called()

    def test_missing_character_resource_is_not_silently_replaced_with_legacy(self):
        self.records()
        del self.game.assets.images['vera_front']
        with self.assertRaises(KeyError):
            WorldRenderer(self.game)

    def test_health_and_role_markers_remain_above_the_art(self):
        self.records()
        self.game.start_new_game()
        self.game.draw_game_elements()
        for actor in self.renderer.actors.values():
            target = pygame.Surface((1280, 800), pygame.SRCALPHA)
            with patch('game.render.bar') as draw_bar:
                actor.draw(target)
            rect = draw_bar.call_args.args[1]
            self.assertLessEqual(rect.bottom, actor.rect.top)


if __name__ == '__main__':
    unittest.main()
