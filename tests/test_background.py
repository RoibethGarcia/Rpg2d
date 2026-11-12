"""Paisajes fijos por mapa: composición visual, nunca superficie jugable."""
from copy import deepcopy
import hashlib
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pygame

from game import environment
from game.app import LastValveGame, ROOT
from game.render import BG, WORLD_RECT


class ExteriorTransparencyTests(unittest.TestCase):
    def test_only_border_connected_black_becomes_transparent_without_mutating_source(self):
        self.assertTrue(hasattr(environment, 'transparent_exterior'))
        source = pygame.Surface((9, 9), pygame.SRCALPHA)
        source.fill((2, 1, 3, 255))
        pygame.draw.rect(source, (80, 70, 60, 255), (2, 2, 5, 5))
        source.set_at((4, 4), (0, 0, 0, 255))  # Sombra interior cerrada.
        source.set_at((3, 3), (50, 60, 70, 128))
        source.set_at((0, 1), (100, 90, 80, 0))  # Alfa original.
        before = pygame.image.tobytes(source, 'RGBA')
        result = environment.transparent_exterior(source)
        self.assertEqual(pygame.image.tobytes(source, 'RGBA'), before)
        self.assertEqual(result.get_at((0, 0)).a, 0)
        self.assertEqual(result.get_at((8, 8)).a, 0)
        self.assertEqual(result.get_at((0, 1)).a, 0)
        for point in ((4, 4), (3, 3), (2, 2)):
            self.assertEqual(result.get_at(point), source.get_at(point))

    def test_disconnected_exterior_regions_are_all_removed_but_dark_art_is_kept(self):
        self.assertTrue(hasattr(environment, 'transparent_exterior'))
        source = pygame.Surface((9, 9), pygame.SRCALPHA)
        source.fill((0, 0, 0, 255))
        pygame.draw.line(source, (40, 35, 30, 255), (4, 0), (4, 8))
        result = environment.transparent_exterior(source)
        self.assertEqual(result.get_at((0, 4)).a, 0)
        self.assertEqual(result.get_at((8, 4)).a, 0)
        self.assertEqual(result.get_at((4, 4)), source.get_at((4, 4)))

    def test_authored_seed_clears_only_selected_enclosed_region_not_other_shadows(self):
        source = pygame.Surface((15, 9), pygame.SRCALPHA)
        source.fill((70, 60, 50, 255))
        pygame.draw.rect(source, (0, 0, 0, 255), (2, 2, 3, 5))
        pygame.draw.rect(source, (0, 0, 0, 255), (10, 2, 3, 5))
        result = environment.transparent_exterior(source, [(3, 4)])
        self.assertEqual(result.get_at((3, 4)).a, 0)
        self.assertEqual(result.get_at((11, 4)), source.get_at((11, 4)))
        self.assertEqual(result.get_at((0, 0)), source.get_at((0, 0)))
        self.assertEqual(source.get_at((3, 4)).a, 255)


class BackgroundTests(unittest.TestCase):
    MAP_ID = 'hondonada'

    @classmethod
    def setUpClass(cls):
        cls.game = LastValveGame(audio_enabled=False)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.game.start_new_game(self.MAP_ID)
        self.renderer = self.game.scenes['play'].renderer

    def test_registered_landscape_is_opaque_and_cached_for_current_map(self):
        name = f'{self.MAP_ID}_background'
        self.assertIn(name, self.game.manifest['images'])
        record = self.game.manifest['images'][name]
        self.assertEqual(record['usage'], f'{self.MAP_ID}_static_background')
        self.assertEqual(record['background'], 'opaque')
        self.assertEqual(self.renderer.layered_maps[self.MAP_ID].background.get_size(), WORLD_RECT.size)

    def test_current_plate_has_transparent_exterior_and_opaque_floor_without_mutating_source(self):
        art = self.renderer.layered_maps[self.MAP_ID]
        self.assertEqual(art.base.get_at((0, 0)).a, 0)
        self.assertGreaterEqual(art.base.get_at((art.base.get_width() // 2,
                                               art.base.get_height() // 2)).a, 250)
        source = self.game.assets.get_image(f'{self.MAP_ID}_plate')
        self.assertEqual(source.get_at((0, 0)).a, 255)  # Fuente RGB original intacta.
        self.renderer.draw(self.game.screen, self.game.state, None)
        self.assertEqual(self.game.screen.get_at(WORLD_RECT.topleft), art.background.get_at((0, 0)))
        self.assertNotEqual(self.game.screen.get_at(WORLD_RECT.topleft)[:3], BG)

    def test_background_is_fixed_across_zoom_camera_and_time_without_per_frame_loading(self):
        # Aislar la capa de fondo: el mundo transparente no debe taparla al ampliar.
        state = SimpleNamespace(map_id=self.MAP_ID, world=SimpleNamespace(exits={}), objects=[])
        def clear_world(surface, state, hover):
            surface.fill((0, 0, 0, 0))
            return [], 0
        with (patch.object(self.renderer, 'update_camera'),
              patch.object(self.renderer, '_draw_world', side_effect=clear_world),
              patch.object(self.game.assets, 'get_image', side_effect=AssertionError('IO por frame')),
              patch('pygame.image.load', side_effect=AssertionError('Carga por frame'))):
            reference = None
            for level in range(3):
                self.renderer.camera.level = level
                for foot in (WORLD_RECT.topleft, WORLD_RECT.center, WORLD_RECT.bottomright):
                    self.renderer.camera.follow(foot)
                    self.renderer.draw(self.game.screen, state, None)
                    pixels = pygame.image.tobytes(self.game.screen.subsurface(WORLD_RECT), 'RGB')
                    if reference is None:
                        reference = pixels
                    self.assertEqual(pixels, reference)
            self.assertGreater(len(set(reference)), 20)  # Es imagen, no relleno liso.

    def test_draw_preserves_domain_picking_actor_anchors_and_ui_outside_viewport(self):
        state = self.game.state
        before = deepcopy(state.__dict__)
        scene = self.game.scenes['play']
        scene.draw(self.game.screen)
        rects = [(0, 0, 1280, 96), (0, 624, 1280, 176), (992, 96, 288, 528)]
        ui = [pygame.image.tobytes(self.game.screen.subsurface(r), 'RGB') for r in rects]
        art = self.renderer.layered_maps[self.MAP_ID]
        self.assertIsNotNone(art.background)
        background = art.background
        with patch.object(art, 'background', background.copy()):
            art.background.fill('magenta')
            scene.draw(self.game.screen)
        self.assertEqual(state.__dict__, before)
        self.assertEqual(ui, [pygame.image.tobytes(self.game.screen.subsurface(r), 'RGB') for r in rects])
        for cell in self.renderer.projection.layout.nodes:
            self.assertEqual(self.renderer.pick(self.renderer.projection.center(cell)), cell)
        for point in (WORLD_RECT.topleft, (991, 96), (24, 623)):
            self.assertFalse(state.grid.in_bounds(self.renderer.pick(point)))
        self.assertEqual(self.renderer.actors['vera'].foot,
                         self.renderer.projection.center(state.player.cell))


class PuestoBackgroundTests(BackgroundTests):
    MAP_ID = 'puesto'

    def test_sky_gap_enclosed_by_tower_cable_is_transparent_without_erasing_cable(self):
        art = self.renderer.puesto
        source = self.game.assets.get_image('puesto_plate')
        self.assertEqual(source.get_at((100, 240)), (0, 0, 0, 255))
        point = tuple(round(v * art.projection.scale) for v in (100, 240))
        self.assertEqual(art.base.get_at(point).a, 0)
        # El cable sigue separando el hueco del exterior; no es colorkey global.
        prepared = environment.transparent_exterior(source,
            self.game.manifest['images']['puesto_plate']['exterior_seeds'])
        self.assertEqual(prepared.get_at((80, 240)), source.get_at((80, 240)))
        self.assertEqual(source.get_at((100, 240)).a, 255)

    def test_round_trip_switches_background_without_reload_or_changing_zoom(self):
        self.assertIsNotNone(self.renderer.puesto.background)
        self.assertNotEqual(pygame.image.tobytes(self.renderer.puesto.background, 'RGB'),
                            pygame.image.tobytes(self.renderer.hondonada.background, 'RGB'))
        self.game.start_new_game()
        state = self.game.state
        self.renderer.camera.level = 1
        with patch.object(self.game.assets, 'get_image', side_effect=AssertionError('Recarga al viajar')):
            state.player.cell = (4, 10)
            self.assertTrue(state.travel('to_puesto'))
            self.renderer.draw(self.game.screen, state, None)
            self.assertEqual(self.renderer.camera.zoom, 1.25)
            self.assertIs(self.renderer.projection, self.renderer.puesto.projection)
            self.assertEqual(self.game.screen.get_at(WORLD_RECT.topleft),
                             self.renderer.puesto.background.get_at((0, 0)))
            state.player.cell = (1, 10)
            self.assertTrue(state.travel('to_hondonada'))
            self.renderer.draw(self.game.screen, state, None)
            self.assertEqual(self.renderer.camera.zoom, 1.25)
            self.assertIs(self.renderer.projection, self.renderer.hondonada.projection)
            self.assertEqual(self.game.screen.get_at(WORLD_RECT.topleft),
                             self.renderer.hondonada.background.get_at((0, 0)))


class PlantaBackgroundTests(BackgroundTests):
    MAP_ID = 'planta'

    def test_canyon_replaces_the_superseded_lake_background_with_original_bytes(self):
        record = self.game.manifest['images']['planta_background']
        self.assertEqual(record['original_path'], 'Cañón industrial al atardecer (1).png')
        expected = '5fc84f8a883db3426783f9c85c10e476d50572eb52b76074647eeea430cc4763'
        self.assertEqual(record['sha256'], expected)
        self.assertEqual(hashlib.sha256((ROOT / record['path']).read_bytes()).hexdigest(), expected)

    def test_landscape_gap_enclosed_by_entry_gantry_preserves_the_beam(self):
        art = self.renderer.planta
        source = self.game.assets.get_image('planta_plate')
        self.assertEqual(source.get_at((150, 420)), (0, 0, 0, 255))
        point = tuple(round(v * art.projection.scale) for v in (150, 420))
        self.assertEqual(art.base.get_at(point).a, 0)
        prepared = environment.transparent_exterior(source,
            self.game.manifest['images']['planta_plate']['exterior_seeds'])
        self.assertEqual(prepared.get_at((140, 420)), source.get_at((140, 420)))
        self.assertEqual(source.get_at((150, 420)).a, 255)

    def test_round_trip_switches_planta_and_puesto_background_without_reload(self):
        self.assertIsNotNone(self.renderer.planta.background)
        self.assertNotEqual(pygame.image.tobytes(self.renderer.planta.background, 'RGB'),
                            pygame.image.tobytes(self.renderer.puesto.background, 'RGB'))
        self.game.start_new_game('puesto')
        state = self.game.state
        state.player.cell = (6, 8)
        self.assertTrue(state.interact())  # Abrir mantenimiento, no saltar reglas de viaje.
        self.renderer.camera.level = 1
        with patch.object(self.game.assets, 'get_image', side_effect=AssertionError('Recarga al viajar')):
            state.player.cell = (9, 8)
            self.assertTrue(state.travel('to_planta'))
            self.renderer.draw(self.game.screen, state, None)
            self.assertEqual(self.renderer.camera.zoom, 1.25)
            self.assertIs(self.renderer.projection, self.renderer.planta.projection)
            self.assertEqual(self.game.screen.get_at(WORLD_RECT.topleft),
                             self.renderer.planta.background.get_at((0, 0)))
            state.player.cell = (9, 8)
            self.assertTrue(state.travel('to_puesto'))
            self.renderer.draw(self.game.screen, state, None)
            self.assertEqual(self.renderer.camera.zoom, 1.25)
            self.assertIs(self.renderer.projection, self.renderer.puesto.projection)
            self.assertEqual(self.game.screen.get_at(WORLD_RECT.topleft),
                             self.renderer.puesto.background.get_at((0, 0)))


if __name__ == '__main__':
    unittest.main()
