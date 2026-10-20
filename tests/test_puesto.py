"""Puesto ilustrado: geometría autorada y dos rivales reales persistentes."""
import unittest
from game.model import GameState


class PuestoNavigationTests(unittest.TestCase):
    def enter(self):
        state = GameState.new()
        state.player.cell = (4, 10)
        self.assertTrue(state.travel('to_puesto'))
        return state

    def test_puesto_has_two_guards_and_authored_walkable_road(self):
        state = self.enter()
        self.assertEqual(set(state.enemies), {'guard1', 'guard2'})
        self.assertTrue(state.grid.adjacency, 'El puesto necesita suelo autorado, no atlas genérico')
        self.assertEqual(set(state.maps['planta'].enemies), {'guard3', 'guard4', 'guard5', 'boss'})
        for uid, patrol in state.patrols.items():
            cells = [tuple(c) for c in patrol['cells']]
            self.assertNotIn(state.enemies[uid].cell, state.world.reserved_spawns)
            self.assertTrue(all(state.grid.can_step(a,b) for a,b in zip(cells,cells[1:]+cells[:1])))
        occupied = {u.cell for u in state.enemies.values()}
        for obj in state.objects:
            approaches = [c for c in state.grid.neighbors(obj['cell']) if c not in occupied]
            self.assertTrue(any(state.grid.find_path(state.player.cell,c,occupied) for c in approaches),obj)
        self.assertTrue(state.grid.find_path(state.player.cell,(1,10),occupied))
        self.assertTrue(state.grid.find_path(state.player.cell,(9,8),occupied))

    def test_contact_both_guards_uses_existing_duel_and_retains_defeat(self):
        for uid in ('guard1','guard2'):
            state = self.enter()
            self.assertIn(uid, state.enemies)
            enemy = state.enemies[uid]
            state.player.cell = next(c for c in state.grid.neighbors(enemy.cell)
                                     if sum(abs(a-b) for a,b in zip(c,enemy.cell)) == 1)
            hp, items = state.player.hp, state.medkits
            self.assertTrue(state._start_step(state.player,enemy.cell))
            self.assertEqual((state.mode,state.active_enemy_id,state.player.ap),('combat',uid,6))
            self.assertFalse(state.motions)
            enemy.hp = 7
            self.assertTrue(state.attack(True))
            self.assertEqual((state.mode,enemy.hp),('exploration',0))
            state.player.cell=(1,10)
            self.assertTrue(state.travel('to_hondonada'))
            self.assertTrue(state.travel('to_puesto'))
            self.assertIs(state.enemies[uid],enemy)
            self.assertEqual((enemy.hp,state.player.hp,state.medkits),(0,hp,items))

    def test_kit_unique_and_maintenance_persistent_without_guard_kills(self):
        state = self.enter()
        kit = next(o for o in state.objects if o['id']=='kit1')
        state.player.cell=kit['cell']
        state.player.hp=20
        self.assertTrue(state.interact())
        self.assertEqual((state.medkits,state.player.hp),(2,20))
        state.player.cell=(9,8)
        self.assertFalse(state.travel('to_planta'))
        state.player.cell=(6,8)
        self.assertTrue(state.interact())
        state.player.cell=(9,8)
        self.assertTrue(state.travel('to_planta'))
        self.assertTrue(state.travel('to_puesto'))
        self.assertIn('maintenance',state.opened)
        self.assertIn('kit1',state.collected)
        state.player.cell=kit['cell']
        self.assertFalse(state.interact())
        self.assertEqual((state.medkits,state.player.hp),(2,20))
        self.assertTrue(all(u.hp==16 for u in state.enemies.values()))
    def test_access_uses_actual_stair_landings_not_southwest_cliff_shortcut(self):
        from game.hondonada import AuthoredLayout
        layout=AuthoredLayout.load('puesto')
        stairs=layout.stairs['escalera_acceso']
        self.assertEqual(layout.nodes[(2,10)]['center'],[570,782])
        self.assertEqual(layout.nodes[(9,11)]['center'],[480,610])
        self.assertIn((12,11),stairs)
        state=self.enter()
        self.assertGreaterEqual(len(state.grid.find_path((2,10),(6,10))),12)
        self.assertFalse(state.grid.can_step((2,10),(6,10)))
        for a,b in zip(stairs,stairs[1:]):
            self.assertTrue(state.grid.can_step(a,b))
            self.assertTrue(state.grid.can_step(b,a))

    def test_road_and_stair_edges_do_not_cross_foreground_obstacles(self):
        from game.hondonada import AuthoredLayout,point_in_polygon
        layout=AuthoredLayout.load('puesto')
        for a,b in layout.data['edges']:
            start,end=(layout.nodes[tuple(c)]['center'] for c in (a,b))
            for fraction in (0,.25,.5,.75,1):
                point=tuple(x+(y-x)*fraction for x,y in zip(start,end))
                self.assertFalse(any(point_in_polygon(point,l['polygon']) for l in layout.data['layers']),
                                 (a,b,fraction))

    def test_each_patrol_can_initiate_only_its_real_duel_and_others_freeze(self):
        for uid in ('guard1','guard2'):
            state=self.enter()
            target=tuple(state.patrols[uid]['cells'][1])
            state.player.cell=target
            for other in state.enemies:state._patrol_wait[other]=100
            state._patrol_wait[uid]=0
            hp=state.enemies[uid].hp
            state.update(.02)
            self.assertEqual((state.mode,state.active_enemy_id,state.player.ap),('combat',uid,6))
            self.assertEqual((state.player.cell,state.enemies[uid].hp),(target,hp))
            self.assertFalse(state.motions)
            timers=dict(state._patrol_wait)
            state.update(2)
            self.assertEqual(state._patrol_wait,timers)



class PuestoRenderingTests(unittest.TestCase):
    def setUp(self):
        import pygame
        from game.app import LastValveGame
        self.pygame=pygame
        self.game=LastValveGame(audio_enabled=False)
        self.game.start_new_game()
        self.scene=self.game.scenes['play']
        self.state=self.game.state
        self.state.player.cell=(4,10)
        self.assertTrue(self.state.travel('to_puesto'))
        self.scene.reset()
        self.renderer=self.scene.renderer

    def tearDown(self):
        self.pygame.quit()

    def test_puesto_projection_active_before_draw_and_centers_selectable(self):
        projection=self.renderer.projection
        self.assertTrue(hasattr(projection,'layout'),'El puesto debe mostrar su ilustración navegable')
        for cell in projection.layout.nodes:
            self.assertEqual(projection.pick(*projection.center(cell)),cell,cell)
        for p in ((30,30),(750,180),(900,780),(1330,500),(250,220)):
            self.assertEqual(projection.pick(*projection.screen(p)),(-1,-1))

    def test_both_guards_draw_once_cached_and_steps_interpolate_source_centers(self):
        from unittest.mock import patch
        from game.model import Motion
        from game.render import WorldActor
        self.assertTrue(hasattr(self.renderer,'puesto'),'Falta arte de puesto por capas')
        self.state.player.cell=(2,10)
        self.state.motions['vera']=Motion((2,10),(3,10),elapsed=.07,duration=.14)
        calls=[]
        real_draw=WorldActor.draw
        def draw(actor,surface):
            calls.append(actor.unit.id)
            real_draw(actor,surface)
        with patch.object(self.game.assets,'get_image',side_effect=AssertionError('IO por frame')):
            with patch.object(self.renderer,'tile',side_effect=AssertionError('tiles fantasma')):
                with patch.object(WorldActor,'draw',draw):
                    self.game.draw_game_elements()
        self.assertCountEqual(calls,['vera','guard1','guard2'])
        a,b=(self.renderer.projection.center(c) for c in ((2,10),(3,10)))
        self.assertEqual(self.renderer.actors['vera'].foot,tuple((x+y)/2 for x,y in zip(a,b)))
        self.assertEqual(self.state.player.cell,(2,10))
        self.assertLess(self.renderer.actors['guard1'].image.get_height(),45)

    def test_foregrounds_use_alpha_and_sort_with_guards_by_their_feet(self):
        from unittest.mock import patch
        from game.render import WorldActor
        self.assertTrue(hasattr(self.renderer,'puesto'))
        art=self.renderer.puesto
        calls=[]
        for layer in art.layers:
            self.assertEqual(layer['image'].get_at((0,0)).a,0)
        def layer(surface,record):calls.append(('art',record['screen_depth']))
        def actor(unit,surface):calls.append(('actor',unit.foot[1]))
        with patch.object(art,'blit_layer',side_effect=layer),patch.object(WorldActor,'draw',actor):
            self.game.draw_game_elements()
        depths=[d for kind,d in calls]
        self.assertEqual(depths,sorted(depths))
        self.assertEqual(sum(kind=='actor' for kind,_ in calls),3)
    def test_combat_path_preview_reports_only_affordable_steps(self):
        self.state.player.cell=(7,10)
        self.state._begin_combat(self.state.enemies['guard1'])
        self.state.player.ap=2
        path,reachable=self.renderer.draw(self.game.screen,self.state,(12,10))
        self.assertGreater(len(path),2)
        self.assertEqual(reachable,2)
        self.assertEqual(self.state.player.ap,2)
        self.assertFalse(self.state.motions)

    def test_front_truck_lane_keeps_actor_visible_at_node_and_midpoint(self):
        from unittest.mock import patch
        from game.render import WorldActor
        from game.model import Motion
        real_draw=WorldActor.draw
        for moving in (False,True):
            self.state.player.cell=(15,9) if moving else (16,9)
            self.state.motions.clear()
            if moving:
                self.state.motions['vera']=Motion((15,9),(16,9),elapsed=.07,duration=.14)
            expected={}
            def capture(actor,surface):
                real_draw(actor,surface)
                if actor.unit.id=='vera':expected['surface']=surface.copy()
            with patch.object(WorldActor,'draw',capture):
                self.renderer.draw(self.game.screen,self.state,None)
            actor=self.renderer.actors['vera']
            visible=opaque=0
            for x in range(actor.image.get_width()):
                for y in range(actor.image.get_height()):
                    if actor.image.get_at((x,y)).a>=128:
                        opaque+=1
                        point=(actor.rect.x+x,actor.rect.y+y)
                        visible+=self.game.screen.get_at(point)==expected['surface'].get_at(point)
            self.assertGreater(visible/opaque,.65,(moving,visible/opaque))



class AuthoredCombatRangeTests(unittest.TestCase):
    def combat(self,player_cell,enemy_cell):
        state=GameState.new()
        state.player.cell=(4,10)
        self.assertTrue(state.travel('to_puesto'))
        state.player.cell=player_cell
        enemy=state.enemies['guard1']
        enemy.cell=enemy_cell
        state._begin_combat(enemy)
        return state,enemy

    def test_attacks_use_graph_adjacency_not_numeric_cell_labels(self):
        state,enemy=self.combat((17,9),(6,9))
        self.assertTrue(state.grid.can_step(state.player.cell,enemy.cell))
        self.assertTrue(state.attack())
        self.assertEqual((enemy.hp,state.player.ap),(12,4))
        state,enemy=self.combat((11,9),(11,10))
        self.assertFalse(state.grid.can_step(state.player.cell,enemy.cell))
        self.assertFalse(state.attack())
        self.assertEqual((enemy.hp,state.player.ap),(16,6))

    def test_enemy_attacks_only_across_real_connected_edge(self):
        state,enemy=self.combat((17,9),(6,9))
        self.assertTrue(state.end_turn())
        state._enemy_action()
        self.assertEqual((state.player.hp,enemy.ap),(27,4))
        state,enemy=self.combat((11,9),(11,10))
        self.assertTrue(state.end_turn())
        state._enemy_action()
        self.assertEqual(state.player.hp,30)
