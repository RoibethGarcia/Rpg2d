"""Contrato del escenario ilustrado: grafo, escaleras y selección de superficies."""
import unittest
from game.model import GameState


class HondonadaNavigationTests(unittest.TestCase):
    def test_hondonada_has_explicit_adjacency_not_implicit_cliff_shortcuts(self):
        state = GameState.new()
        self.assertTrue(getattr(state.grid, 'adjacency', None),
                        'La ilustración necesita conectividad explícita entre sus niveles')
        self.assertEqual(set(state.grid.neighbors(state.player.cell)),
                         set(state.grid.adjacency[state.player.cell]))
        self.assertTrue(state.grid.find_path(state.player.cell, (4, 10)))
        self.assertTrue(state.grid.find_path(state.player.cell, (2, 11)))
        other = state.maps['puesto'].grid
        self.assertTrue(other.adjacency)
        self.assertTrue(state.maps['planta'].grid.adjacency)

    def test_six_stairs_have_intermediate_treads_and_bidirectional_motion(self):
        from game.hondonada import HondonadaLayout
        layout = HondonadaLayout.load()
        self.assertEqual(set(layout.stairs), {'escalera_anden_madera', 'escalera_anden_piedra',
            'escalera_oeste', 'escalera_sur', 'escalera_entrada', 'escalera_terraza_este'})
        state = GameState.new()
        for name, stairs in layout.stairs.items():
            self.assertGreaterEqual(len(stairs), 4, name)
            self.assertTrue(state.grid.find_path((2, 10), stairs[0]), name)
            for a, b in zip(stairs, stairs[1:]):
                for start, end in ((a, b), (b, a)):
                    state.player.cell = start
                    self.assertTrue(state._start_step(state.player, end), (name, start, end))
                    state.update(.14)
                    self.assertEqual(state.player.cell, end)
                    self.assertEqual(state.player.ap, 6)
                    self.assertIn(end, state.grid.step_directions[start].values())

    def test_authored_levels_describe_both_landings_and_intermediate_stair_heights(self):
        from game.hondonada import HondonadaLayout
        layout = HondonadaLayout.load()
        expected = {'escalera_anden_madera': (1,2), 'escalera_anden_piedra': (2,1),
                    'escalera_oeste': (1,0), 'escalera_sur': (1,0),
                    'escalera_entrada': (0,-1), 'escalera_terraza_este': (1,2)}
        for name, cells in layout.stairs.items():
            levels = [layout.nodes[c]['level'] for c in cells]
            self.assertEqual((levels[0],levels[-1]), expected[name], name)
            self.assertTrue(all(min(levels) <= value <= max(levels) for value in levels))
            self.assertGreater(len(set(levels)),2,name)

    def test_unlinked_logical_neighbors_cannot_cross_cliffs_and_routes_respect_reservations(self):
        state = GameState.new()
        start = state.player.cell
        illegal = next((start[0] + x, start[1] + y) for x, y in ((0,1),(0,-1),(-1,0),(1,0))
                       if not state.grid.can_step(start,(start[0]+x,start[1]+y)))
        self.assertFalse(state._start_step(state.player, illegal))
        self.assertFalse(state.motions)
        for cell in state.grid.adjacency:
            self.assertTrue(cell == start or state.grid.find_path(start, cell), cell)
        neighbor = state.grid.neighbors(start)[0]
        self.assertEqual(state.grid.find_path(start, neighbor, {neighbor}), [])


class HondonadaRenderingTests(unittest.TestCase):
    def setUp(self):
        import pygame
        from game.app import LastValveGame
        self.pygame = pygame
        self.game = LastValveGame(audio_enabled=False)
        self.game.start_new_game()
        self.scene = self.game.scenes['play']
        self.renderer = self.scene.renderer

    def tearDown(self):
        self.pygame.quit()

    def test_plate_projection_active_before_first_draw_and_all_centers_pick(self):
        self.assertTrue(hasattr(self.renderer.projection, 'layout'),
                        'La proyección tabulada debe estar activa ANTES del primer clic')
        projection = self.renderer.projection
        for cell in projection.layout.nodes:
            self.assertEqual(projection.pick(*projection.center(cell)), cell, cell)
        for source in ((0,0),(400,100),(900,60),(1400,1000)):
            self.assertFalse(self.game.state.grid.in_bounds(projection.pick(*projection.screen(source))))

    def test_cached_foreground_layers_are_real_transparent_cutouts_and_no_floor_tiles_draw(self):
        from unittest.mock import patch
        self.assertTrue(hasattr(self.renderer, 'hondonada'))
        art = self.renderer.hondonada
        self.assertGreaterEqual(len(art.layers), 6)
        for layer in art.layers:
            image = layer['image']
            self.assertEqual(image.get_at((0,0)).a,0)
            self.assertGreater(image.get_bounding_rect().width,0)
        with patch.object(self.game.assets, 'get_image', side_effect=AssertionError('IO por frame')):
            with patch.object(self.renderer, 'tile', side_effect=AssertionError('tiles fantasma')):
                self.game.draw_game_elements()
                self.game.draw_game_elements()
        self.assertLess(self.renderer.actors['vera'].image.get_height(), 45)

    def test_stair_actor_interpolates_projected_endpoints_without_mutating_cell(self):
        from game.model import Motion
        from game.hondonada import HondonadaLayout
        start, end = HondonadaLayout.load().stairs['escalera_sur'][:2]
        state = self.game.state
        state.player.cell = start
        state.motions['vera'] = Motion(start,end,elapsed=.07,duration=.14)
        self.game.draw_game_elements()
        a,b = self.renderer.projection.center(start), self.renderer.projection.center(end)
        self.assertEqual(self.renderer.actors['vera'].foot,tuple((x+y)/2 for x,y in zip(a,b)))
        self.assertEqual(state.player.cell,start)

    def test_transition_reconfigures_projection_before_mouse_pick(self):
        state = self.game.state
        state.player.cell = (4,10)
        self.assertTrue(state.travel('to_puesto'))
        # No frame/update previo: se procesa directamente el evento de ratón.
        target = (2,10)
        point = self.renderer.puesto.projection.center(target)
        self.scene.handle_events([self.pygame.event.Event(self.pygame.MOUSEMOTION,pos=point)])
        self.assertEqual(self.scene.hover_cell,target)
        state.player.cell=(1,10)
        self.assertTrue(state.travel('to_hondonada'))
        self.scene.handle_events([self.pygame.event.Event(self.pygame.MOUSEMOTION,pos=(0,0))])
        self.assertTrue(hasattr(self.renderer.projection,'layout'))

    def test_bridge_and_west_porch_do_not_lose_vera_behind_their_own_facades(self):
        layout = self.renderer.hondonada.layout
        cells = {tuple(c) for route in layout.routes if route['id'] in ('puente', 'barrio_oeste')
                 for c in route['cells']}
        from game.render import WorldActor
        from unittest.mock import patch
        real_draw = WorldActor.draw
        expected = {}
        def capture(actor, surface):
            real_draw(actor, surface)
            expected['surface'] = surface.copy()
        for cell in sorted(cells):
            self.game.state.player.cell = cell
            with patch.object(WorldActor, 'draw', capture):
                self.game.draw_game_elements()
            actor = self.renderer.actors['vera']
            visible = opaque = 0
            for x in range(actor.image.get_width()):
                for y in range(actor.image.get_height()):
                    color = actor.image.get_at((x,y))
                    if color.a >= 128:
                        opaque += 1
                        point = (actor.rect.x+x,actor.rect.y+y)
                        visible += self.game.screen.get_at(point) == expected['surface'].get_at(point)
            self.assertGreater(visible / opaque, .3, (cell,layout.nodes[cell]['center']))
