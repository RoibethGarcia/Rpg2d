"""Viajes y presentación con SDL dummy, sin certificación audiovisual."""
import unittest
import pygame
from game.app import LastValveGame


class CampaignSceneTests(unittest.TestCase):
    def setUp(self):
        self.game = LastValveGame(audio_enabled=False)
        self.game.start_new_game()

    def tearDown(self):
        pygame.quit()

    def test_e_travel_clears_hover_and_stale_actor_cache_without_reloading_assets(self):
        from unittest.mock import patch
        state = self.game.state
        scene = self.game.scenes['play']
        self.game.draw_game_elements()
        old_actor = scene.renderer.actors['vera']
        scene.hover_cell = (15, 12)
        state.player.cell = (4, 10)
        with patch.object(self.game.assets, 'load_image') as load:
            self.game.handle_specific_events(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
            self.assertEqual(state.map_id, 'puesto')
            self.assertIsNone(scene.hover_cell)
            self.assertFalse(scene.renderer.actors)
            self.game.draw_game_elements()
        load.assert_not_called()
        self.assertIsNot(scene.renderer.actors['vera'], old_actor)
        self.assertIs(scene.renderer.actors['guard1'].unit, state.enemies['guard1'])
        self.assertFalse(state.route or state.motions)

    def test_direct_facade_travel_also_clears_presentation_on_next_update(self):
        state = self.game.state
        scene = self.game.scenes['play']
        self.game.draw_game_elements()
        scene.hover_cell = (15, 12)
        state.player.cell = (4, 10)
        self.assertTrue(state.travel('to_puesto'))
        self.game.update_game_logic(0)
        self.assertIsNone(scene.hover_cell)
        self.assertFalse(scene.renderer.actors)
