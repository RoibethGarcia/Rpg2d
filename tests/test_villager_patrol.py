"""Recorrido ambiental del aldeano de la plaza, sin convertirlo en enemigo."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from game.model import GameState, Motion


class PlazaWalkTests(unittest.TestCase):
    def setUp(self):
        self.state = GameState.new()
        self.npc = next(o for o in self.state.objects if o['id'] == 'villager_plaza')

    def start_walk(self):
        for _ in range(200):
            self.state.update(.02)
            motions = getattr(self.state.world, 'npc_motions', {})
            if self.npc['id'] in motions:
                return motions[self.npc['id']]
        self.fail('El ciudadano de la plaza no comenzó a caminar')

    def test_plaza_repeats_authored_round_trip_without_moving_terrace_or_resources(self):
        state = self.state
        terrace = next(o for o in state.objects if o['id'] == 'villager_terrace')
        resources = (state.player.hp, state.player.ap, state.medkits, state.credential)
        expected = [(16, 1), (15, 1), (14, 1), (13, 1), (14, 1), (15, 1)]
        self.assertIn('patrol', self.npc, 'Falta la ruta predeterminada del ciudadano')
        self.assertEqual([tuple(c) for c in self.npc['patrol']['cells']], expected)
        visited = []
        for _ in range(2):
            for target in expected[1:] + expected[:1]:
                motion = self.start_walk()
                self.assertEqual(motion.end, target)
                self.assertTrue(state.grid.can_step(motion.start, motion.end))
                state.update(motion.duration)
                self.assertEqual(self.npc['cell'], target)
                visited.append(target)
        self.assertEqual(visited[:6], visited[6:])
        self.assertEqual(terrace['cell'], (6, 2))
        self.assertEqual((state.player.hp, state.player.ap, state.medkits, state.credential), resources)
        self.assertEqual(state.mode, 'exploration')
        self.assertFalse(state.enemies or state.motions)

    def test_origin_and_destination_block_player_until_step_finishes(self):
        state = self.state
        motion = self.start_walk()
        self.assertTrue({motion.start, motion.end} <= state.occupied('vera'))
        state.player.cell = (14, 1)
        self.assertFalse(state.preview_path(motion.end))
        self.assertFalse(state._start_step(state.player, motion.end))
        state.update(motion.duration)
        self.assertNotIn(motion.start, state.occupied('vera'))
        self.assertIn(motion.end, state.occupied('vera'))
        self.assertIsNone(state.active_dialogue)
        self.assertEqual(state.mode, 'exploration')

    def test_waits_for_vera_or_her_reserved_destination_and_retries_same_step(self):
        for reserved in (False, True):
            with self.subTest(reserved=reserved):
                self.setUp()
                state = self.state
                state.player.cell = (14, 1) if reserved else (15, 1)
                if reserved:
                    state.motions['vera'] = Motion((14, 1), (15, 1), duration=20)
                state.update(3)
                self.assertEqual(self.npc['cell'], (16, 1))
                self.assertFalse(state.world.npc_motions)
                self.assertEqual(state.mode, 'exploration')
                state.motions.clear()
                state.player.cell = (2, 10)
                self.assertEqual(self.start_walk().end, (15, 1))

    def test_dialogue_freezes_mid_step_and_resumes_after_closing(self):
        state = self.state
        self.start_walk()
        state.player.cell = (14, 1)
        self.assertTrue(state.interact())
        self.assertEqual(state.active_dialogue.npc_id, self.npc['id'])
        before = deepcopy(vars(state))
        state.update(4)
        self.assertEqual(vars(state), before)
        self.assertTrue(state.close_dialogue())
        state.update(.1)
        self.assertGreater(state.world.npc_motions[self.npc['id']].elapsed, 0)

    def test_walking_does_not_block_travel_and_map_progress_persists_but_new_game_resets(self):
        state = self.state
        motion = self.start_walk()
        state.update(.1)
        village = deepcopy(state.world)
        state.player.cell = (4, 10)
        self.assertTrue(state.travel('to_puesto'))
        state.update(.1)
        self.assertEqual(state.maps['hondonada'], village)
        state.player.cell = (1, 10)
        self.assertTrue(state.travel('to_hondonada'))
        self.assertEqual(state.world, village)
        state.update(motion.duration)
        self.assertEqual(self.npc['cell'], motion.end)
        clean = GameState.new()
        self.assertFalse(clean.world.npc_motions or clean.world.patrol_index or clean.world.patrol_wait)
        self.assertEqual(next(o['cell'] for o in clean.objects if o['id'] == self.npc['id']), (16, 1))

    def test_frame_partition_does_not_change_walk_progress(self):
        other = GameState.new()
        self.state.update(7.2)
        for _ in range(360):
            other.update(.02)
        self.assertEqual(self.state.objects, other.objects)
        self.assertEqual(self.state.world.npc_motions, other.world.npc_motions)
        self.assertEqual(self.state.world.patrol_index, other.world.patrol_index)
        self.assertEqual(self.state.world.patrol_wait, other.world.patrol_wait)

    def test_invalid_routes_are_rejected_during_campaign_validation(self):
        bad_routes = (
            {'cells': []},
            {'cells': [[16, 1]]},
            {'cells': [[16, 1], [6, 2]]},
            {'cells': [[15, 1], [16, 1]]},
            {'cells': [[16, 1], [15, 1]], 'duration': 0},
            {'cells': [[16, 1], [15, 1]], 'pause': -1},
        )
        for patrol in bad_routes:
            with self.subTest(patrol=patrol):
                self.npc['patrol'] = patrol
                with self.assertRaisesRegex(ValueError, 'recorrido.*villager_plaza'):
                    self.state.validate_campaign()


class PlazaWalkRenderingTests(unittest.TestCase):
    def test_cached_actor_tracks_interpolated_feet_without_io_or_domain_mutation(self):
        import pygame
        from game.app import LastValveGame
        game = LastValveGame(audio_enabled=False)
        self.addCleanup(pygame.quit)
        game.start_new_game()
        scene, state = game.scenes['play'], game.state
        game.draw_game_elements()
        actor = scene.renderer.villagers['villager_plaza']
        origin = actor.foot
        state.update(1.3)
        self.assertIn('villager_plaza', getattr(state.world, 'npc_motions', {}),
                      'Falta movimiento interpolado del ciudadano')
        motion = state.world.npc_motions['villager_plaza']
        projection = scene.renderer.projection
        start, end = projection.center(motion.start), projection.center(motion.end)
        fraction = motion.elapsed / motion.duration
        expected = tuple(a + (b-a)*fraction for a, b in zip(start, end))
        before = deepcopy(vars(state))
        image = actor.image
        with patch.object(game.assets, 'get_image', side_effect=AssertionError('IO por frame')):
            game.draw_game_elements()
        self.assertIs(scene.renderer.villagers['villager_plaza'], actor)
        self.assertIs(actor.image, image)
        self.assertNotEqual(actor.foot, origin)
        self.assertEqual(actor.foot, expected)
        self.assertEqual(vars(state), before)
        state.update(motion.duration)
        game.draw_game_elements()
        self.assertEqual(actor.foot, projection.center(motion.end))
