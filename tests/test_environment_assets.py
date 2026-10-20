"""Arte modular de campaña: caché, profundidad y cero cambios de dominio."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import pygame
from game.app import LastValveGame
from game.render import WorldRenderer, WorldActor


class EnvironmentAssetTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)
        self.game.start_new_game()
        self.renderer = self.game.scenes['play'].renderer

    def tearDown(self):
        pygame.quit()

    def art(self):
        self.assertTrue(hasattr(self.renderer, 'environment'), 'Falta el renderer modular de escenarios')
        return self.renderer.environment

    def test_atlas_props_remain_available_and_all_campaign_maps_use_layers(self):
        art = self.art()
        floor = art.frames[art.styles['planta']['floor']][0]
        self.assertEqual(floor.get_size(), (48,24))
        self.assertEqual(floor.get_at((0,0)).a,0)
        self.assertGreater(len({floor.get_at((x,y))[:3] for x in range(48) for y in range(24) if floor.get_at((x,y)).a}),20)
        for map_id in ('hondonada','puesto','planta'):
            self.assertEqual(art.style(map_id)['kind'],'layered')
            self.assertEqual(art.style(map_id)['placements'],[])

    def test_transition_selects_current_map_without_reload_or_domain_mutation(self):
        art = self.art()
        state = self.game.state
        state.player.cell = (4, 10)
        self.assertTrue(state.travel('to_puesto'))
        before = deepcopy(state.__dict__)
        with patch.object(self.game.assets, 'get_image', side_effect=AssertionError('lectura durante draw')):
            with patch.object(art, 'style', wraps=art.style) as style:
                for _ in range(2):
                    self.renderer.draw(self.game.screen, state, None)
                self.assertTrue(all(c.args[0] == 'puesto' for c in style.call_args_list))
        self.assertEqual(state.__dict__, before)

    def test_campaign_has_no_silent_legacy_fallback(self):
        art = self.art()
        with self.assertRaisesRegex(ValueError, 'escenario'):
            art.style('unknown_map')
        self.assertIsNone(art.style('legacy'))
        del self.game.manifest['environment_sets']['planta']
        with self.assertRaisesRegex(ValueError, 'planta'):
            WorldRenderer(self.game)

    def test_missing_atlas_is_an_explicit_failure(self):
        self.art()
        del self.game.assets.images['environment_atlas']
        with self.assertRaises(KeyError):
            WorldRenderer(self.game)

    def test_all_placements_use_blocked_footprints_away_from_spawns_objects_exits(self):
        art = self.art()
        for map_id, world in self.game.state.maps.items():
            reserved = world.reserved_spawns | {o['cell'] for o in world.objects} | {e.cell for e in world.exits.values()}
            for p in art.style(map_id)['placements']:
                footprint = {tuple(c) for c in p['footprint']}
                self.assertTrue(footprint <= world.grid.blocked)
                self.assertFalse(footprint & reserved)
        # El validador modular sigue rechazando huellas incompatibles;
        # las ilustraciones activas no colocan esos módulos sobre el suelo.
        style = {'placements': [{'cell': [2,10], 'footprint': [[2,10]], 'frame': 'tank'}]}
        with self.assertRaisesRegex(ValueError, 'huella'):
            art.placements(self.game.state, style)

    def test_hondonada_cutouts_interleave_with_actor_by_foot_depth(self):
        state = self.game.state
        art = self.renderer.hondonada
        calls = []
        def record_art(surface, layer):
            calls.append(('art', layer['screen_depth']))
        with patch.object(art, 'blit_layer', side_effect=record_art):
            with patch.object(WorldActor, 'draw', side_effect=lambda surface: calls.append(('actor', self.renderer.projection.center(state.player.cell)[1]))):
                self.renderer.draw(self.game.screen, state, None)
        index = next(i for i, value in enumerate(calls) if value[0] == 'actor')
        actor_y = calls[index][1]
        self.assertTrue(any(y > actor_y for _, y in calls[index + 1:]))
        self.assertTrue(all(y <= actor_y for _, y in calls[:index]))
        self.assertTrue(all(y >= actor_y for _, y in calls[index + 1:]))

    def test_frames_are_bounded_nonempty_and_anchors_fit(self):
        art = self.art()
        atlas = self.game.assets.get_image('environment_atlas')
        for name, record in self.game.manifest['environment_frames'].items():
            self.assertTrue(atlas.get_rect().contains(pygame.Rect(record['frame'])), name)
            image, anchor = art.frames[name]
            self.assertGreater(image.get_bounding_rect().width, 0)
            self.assertTrue(0 <= anchor[0] <= image.get_width())
            self.assertTrue(0 <= anchor[1] <= image.get_height())
