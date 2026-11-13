"""Escenas concretas; input de UI nunca atraviesa hasta el mundo."""
import math
import pygame
from engine.ui import Scene, Button
from game.render import (Typography, WorldRenderer, WORLD_RECT, BG, PANEL,
                         EDGE, TEXT, MUTED, WATER, AMBER, RED, bar)
from game.dialogue import DialogueView
from game.guidance import combat_hint, end_turn_advised, medkit_status, objective
from game.menu_nav import MenuSelection, reveal
from game.model import ActionResult


class ClickCue:
    """Button conserva su contrato play(), pero usa el canal UI reservado."""
    def __init__(self, game):
        self.game = game

    def play(self):
        self.game.sound('click')


def make_button(game, x, y, width, height, text, callback, size=24):
    button = Button(x, y, width, height, text, callback,
                    ClickCue(game) if game.audio_enabled else None)
    button.font = pygame.font.Font(None, size)
    button.color = (49, 65, 71)
    button.hover_color = (69, 94, 98)
    return button


def emblem(surface, center, radius=90, water=False, angle=0.0):
    x, y = center
    color = WATER if water else AMBER
    pygame.draw.circle(surface, (35, 47, 52), center, radius + 9)
    pygame.draw.circle(surface, color, center, radius, 7)
    pygame.draw.circle(surface, color, center, radius // 3, 7)
    for turn in range(4):  # Rayos del volante; angle=0 es la figura original.
        a = math.radians(angle + 90 * turn)
        dx, dy = math.cos(a), math.sin(a)
        pygame.draw.line(surface, color, (x + dx * radius // 3, y + dy * radius // 3),
                         (x + dx * radius, y + dy * radius), 10)


def glass_button(surface, layer, topleft, text, font, selected, primary, amount=1.0):
    """Botón de cristal oscuro con borde ámbar al seleccionarlo; el primario destaca."""
    rect = layer.get_rect()
    layer.fill((0, 0, 0, 0))
    if primary and selected:
        fill, edge, ink = (*AMBER, 240), (255, 226, 160), (22, 26, 28)
    elif primary:
        fill, edge, ink = (44, 36, 24, 215), AMBER, AMBER
    elif selected:
        fill, edge, ink = (58, 78, 84, 235), AMBER, TEXT
    else:
        fill, edge, ink = (22, 31, 36, 190), EDGE, TEXT
    pygame.draw.rect(layer, fill, rect, border_radius=10)
    pygame.draw.rect(layer, edge, rect, 2, border_radius=10)
    if selected and not primary:
        pygame.draw.rect(layer, AMBER, (0, 8, 5, rect.height - 16), border_radius=3)
    image = font.render(text, True, ink)
    layer.blit(image, image.get_rect(center=rect.center))
    layer.set_alpha(round(255 * amount))
    surface.blit(layer, (topleft[0], topleft[1] + round((1 - amount) * 12)))


class MenuScene(Scene):
    """Menú sobre el fondo vivo: entrada escalonada, teclado y emblema que gira."""
    FADE_SECONDS = .9
    SPIN_DEGREES_PER_SECOND = 14
    REVEALS = {'emblem': (.15, .5), 'title': (.35, .5), 'subtitle': (.65, .5), 'buttons': (.85, .45)}
    footer_lines = ('Taller de Videojuegos 2D · 2026',)

    def __init__(self, game):
        super().__init__(game)
        self.type = Typography()
        self.backdrop = game.backdrop
        self.fade = 0.0
        self.elapsed = 0.0
        self.angle = 0.0
        self.selection = MenuSelection(4)
        self.veil = pygame.Surface((1280, 800))
        self.buttons = [make_button(game, 460, 412, 360, 56, 'Comenzar', game.start_new_game, 30),
                        make_button(game, 460, 480, 360, 46, 'Cómo jugar',
                                    lambda: game.change_scene('howto'), 26),
                        make_button(game, 460, 532, 360, 46, 'Opciones',
                                    lambda: game.change_scene('options'), 26),
                        make_button(game, 460, 584, 360, 46, 'Salir', game.stop, 26)]
        self.emblem_layer = pygame.Surface((160, 160), pygame.SRCALPHA)
        self.entry_layers = [pygame.Surface(b.rect.size, pygame.SRCALPHA) for b in self.buttons]

    def reveal_of(self, name, delay=0.0):
        start, duration = self.REVEALS[name]
        return reveal(self.elapsed, start + delay, duration)

    def on_enter(self):
        """Al volver desde la partida: fondo, fundido, entrada y selección desde el principio."""
        self.fade = 0.0
        self.elapsed = 0.0
        self.angle = 0.0
        self.selection.set(0)
        self.backdrop.reset()

    def update(self, dt):
        self.fade = min(1.0, self.fade + dt / self.FADE_SECONDS)
        self.elapsed += dt
        self.angle = (self.angle + self.SPIN_DEGREES_PER_SECOND * dt) % 360
        self.backdrop.update(dt)

    def activate(self):
        button = self.buttons[self.selection.index]
        if button.click_sound is not None:
            button.click_sound.play()
        button.callback()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION or (event.type == pygame.MOUSEBUTTONDOWN
                                                    and event.button == 1):
                for index, button in enumerate(self.buttons):
                    if button.rect.collidepoint(event.pos):
                        self.selection.set(index)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selection.move(1)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selection.move(-1)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self.activate()
                    return
            for button in self.buttons:
                button.handle_event(event)
            if self.game.current_scene is not self:
                return

    def shadowed(self, surface, text, size, color, alpha=255, dy=0, **anchor):
        """Texto con sombra corta: se lee sobre cualquier zona del paisaje."""
        if alpha <= 0:
            return
        font = self.type.fonts[size]
        image, shade = font.render(text, True, color), font.render(text, True, (4, 7, 10))
        image.set_alpha(alpha)
        shade.set_alpha(alpha)
        rect = image.get_rect(**anchor).move(0, dy)
        surface.blit(shade, rect.move(2, 2))
        surface.blit(image, rect)

    def draw_entry(self, surface, index, amount):
        button = self.buttons[index]
        glass_button(surface, self.entry_layers[index], button.rect.topleft, button.text,
                     button.font, self.selection.index == index, index == 0, amount)

    def draw(self, surface):
        self.backdrop.draw(surface)
        pygame.draw.line(surface, AMBER, (80, 84), (1200, 84), 2)
        self.shadowed(surface, 'LA HONDONADA / PLANTA DE DISTRIBUCIÓN', 22, MUTED, topleft=(80, 49))
        shown = self.reveal_of('emblem')
        if shown > 0:
            self.emblem_layer.fill((0, 0, 0, 0))
            emblem(self.emblem_layer, (80, 80), 60, angle=self.angle)
            self.emblem_layer.set_alpha(round(255 * shown))
            surface.blit(self.emblem_layer, (560, 115 + round((1 - shown) * 12)))
        shown = self.reveal_of('title')
        self.shadowed(surface, 'LA ÚLTIMA VÁLVULA', 80, TEXT, round(255 * shown),
                      round((1 - shown) * 14), center=(640, 322))
        shown = self.reveal_of('subtitle')
        self.shadowed(surface, 'El agua no pertenece a La Custodia. Devuélvela a La Hondonada.',
                      26, TEXT, round(255 * shown), round((1 - shown) * 10), center=(640, 373))
        for index in range(len(self.buttons)):
            amount = self.reveal_of('buttons', .08 * index)
            if amount > 0:
                self.draw_entry(surface, index, amount)
        self.shadowed(surface, 'Flechas o W/S: elegir   ·   Enter: confirmar', 20, MUTED,
                      round(255 * self.reveal_of('buttons', .3)), center=(640, 664))
        for index, line in enumerate(self.footer_lines):
            self.shadowed(surface, line, 20, MUTED, topleft=(80, 745 + 24 * index))
        if self.fade < 1:
            eased = self.fade * self.fade * (3 - 2 * self.fade)
            self.veil.set_alpha(round(255 * (1 - eased)))
            surface.blit(self.veil, (0, 0))


class OptionsScene(Scene):
    """Ajustes de sesión; reutiliza botones y el mismo bucle del menú."""
    def __init__(self, game):
        super().__init__(game)
        self.type = Typography()
        self.backdrop = game.backdrop
        self.return_scene = 'menu'
        self.panel = pygame.Surface((760, 540), pygame.SRCALPHA)
        pygame.draw.rect(self.panel, (*PANEL, 222), self.panel.get_rect(), border_radius=12)
        pygame.draw.rect(self.panel, EDGE, self.panel.get_rect(), 2, border_radius=12)
        self.buttons = [
            make_button(game, 320, 310, 160, 48, 'Música −', lambda: self.change_music(-.1)),
            make_button(game, 800, 310, 160, 48, 'Música +', lambda: self.change_music(.1)),
            make_button(game, 320, 430, 160, 48, 'Efectos −', lambda: self.change_effects(-.1)),
            make_button(game, 800, 430, 160, 48, 'Efectos +', lambda: self.change_effects(.1)),
            make_button(game, 460, 545, 360, 50, 'Volver al menú', self.go_back, 26),
        ]

    def on_enter(self, return_scene):
        self.return_scene = return_scene
        self.buttons[-1].text = 'Volver a la pausa' if return_scene == 'pause' else 'Volver al menú'

    def change_music(self, delta):
        self.game.set_music_volume(round(self.game.music_volume + delta, 2))

    def change_effects(self, delta):
        self.game.set_effects_volume(round(self.game.effects_volume + delta, 2))

    def go_back(self):
        self.game.sound('back')
        self.game.change_scene(self.return_scene)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not getattr(event, 'repeat', False):
                    self.go_back()
                return
            for button in self.buttons:
                button.handle_event(event)
            if self.game.current_scene is not self:
                return

    def update(self, dt):
        if self.return_scene == 'menu':
            self.backdrop.update(dt)

    def draw(self, surface):
        if self.return_scene == 'pause':
            self.game.scenes['pause'].draw_background(surface)
        else:
            self.backdrop.draw(surface)
        surface.blit(self.panel, (260, 180))
        self.type.text(surface, 'OPCIONES DE AUDIO', (360, 210), 40, AMBER)
        for label, volume, y, color in (('Música', self.game.music_volume, 265, WATER),
                                        ('Efectos', self.game.effects_volume, 385, AMBER)):
            self.type.text(surface, f'{label}: {round(volume * 100)} %', (500, y), 30)
            bar(surface, pygame.Rect(500, y + 60, 280, 14), volume, 1, color)
        self.type.text(surface, 'Efectos incluye botones y golpes de combate.', (360, 500), 22, MUTED)
        for button in self.buttons:
            button.draw(surface)
        self.type.text(surface, '0 % silencia · 100 % conserva la mezcla original', (360, 655), 24, MUTED)
        self.type.text(surface, 'Escape: volver · Ajustes hasta cerrar el juego.'
                       if self.return_scene == 'menu' else 'Escape: volver a la pausa · La partida sigue pausada.',
                       (360, 692), 22, MUTED)


class PauseScene(Scene):
    """Congela la presentación; solo PlayScene actualiza la simulación."""
    def __init__(self, game):
        super().__init__(game)
        self.type = Typography()
        self.background = pygame.Surface((1280, 800))
        self.shade = pygame.Surface((1280, 800), pygame.SRCALPHA)
        self.shade.fill((3, 8, 11, 170))
        self.buttons = [
            make_button(game, 460, 340, 360, 54, 'Continuar', self.resume, 28),
            make_button(game, 460, 410, 360, 54, 'Opciones',
                        lambda: game.change_scene('options'), 28),
            make_button(game, 460, 480, 360, 54, 'Volver al menú', self.to_menu, 28),
        ]

    def on_enter(self):
        self.game.scenes['play'].draw(self.background)

    def resume(self):
        self.game.sound('back')
        self.game.change_scene('play')

    def to_menu(self):
        self.game.sound('back')
        self.game.change_scene('menu')

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not getattr(event, 'repeat', False):
                    self.resume()
                return
            for button in self.buttons:
                button.handle_event(event)
            if self.game.current_scene is not self:
                return

    def draw_background(self, surface):
        surface.blit(self.background, (0, 0))
        surface.blit(self.shade, (0, 0))

    def draw(self, surface):
        self.draw_background(surface)
        pygame.draw.rect(surface, PANEL, (400, 220, 480, 400), border_radius=12)
        pygame.draw.rect(surface, EDGE, (400, 220, 480, 400), 2, border_radius=12)
        self.type.text(surface, 'PAUSA', (562, 260), 48, AMBER)
        for button in self.buttons:
            button.draw(surface)
        self.type.text(surface, 'Escape: continuar', (548, 570), 22, MUTED)


class PlayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.type = Typography()
        self.renderer = WorldRenderer(game)
        self.dialogue_view = DialogueView(game)
        self.hover_cell = None
        self._pointer_pos = None
        self._context = None
        self.buttons = [
            make_button(game, 28, 693, 166, 46, 'Llave · 2 PA / 4', lambda: self.command('attack')),
            make_button(game, 206, 693, 178, 46, 'Potente · 3 PA / 7', lambda: self.command('attack', True)),
            make_button(game, 396, 693, 190, 46, 'Botiquín · 2 PA / +8', lambda: self.command('heal'), 22),
            make_button(game, 598, 693, 180, 46, 'Espacio · Fin turno', lambda: self.command('end_turn')),
            make_button(game, 790, 693, 190, 46, 'E · Interactuar', lambda: self.command('interact')),
            make_button(game, 1034, 734, 214, 42, 'Volver al menú', self.to_menu),
            make_button(game, 714, 55, 108, 30, 'Zoom −', lambda: self.change_zoom(-1), 22),
            make_button(game, 884, 55, 108, 30, 'Zoom +', lambda: self.change_zoom(1), 22),
        ]

    def reset(self, reset_zoom=True, stop_audio=True):
        self.hover_cell = None
        self._pointer_pos = None
        self.renderer.reset(reset_zoom)
        state = self.game.state
        if state is not None:
            state.last_attacks.clear()
            state.drain_attack_events()
        if stop_audio:
            self.game.stop_combat_sounds()
        self._context = (id(state), state.context_revision) if state is not None else None

    def change_zoom(self, direction):
        self.renderer.camera.step(direction)
        self._refresh_camera()

    def _refresh_camera(self):
        self.renderer.update_camera(self.game.state)
        self.hover_cell = (self.renderer.pick(self._pointer_pos)
                           if self._pointer_pos is not None else None)

    def _sync_context(self):
        state = self.game.state
        if self._context != (id(state), state.context_revision):
            self.reset(reset_zoom=self._context is None or self._context[0] != id(state))

    def to_menu(self):
        self.game.sound('back')
        self.game.change_scene('menu')

    def _play_attack_sounds(self):
        # No usar last_attacks: pierde golpes de un mismo tick y los letales.
        state = self.game.state
        for action in state.drain_attack_events():
            self.game.combat_sound(action.kind)
            if action.damage:  # Número flotante: solo presentación del hecho ya aplicado.
                color = AMBER if action.attacker_id == state.player.id else RED
                self.renderer.add_floater(action.target_cell, f'-{action.damage}', color,
                                          action.occurred_at)

    def command(self, name, *args):
        self._sync_context()
        state = self.game.state
        if (name in ('attack', 'heal', 'end_turn', 'move_direction', 'set_destination', 'interact')
                and self.renderer.attack_active(state)):
            state.message = 'Espera a que termine la animación del ataque.'
            result = ActionResult(False, state.message)
        else:
            hp_before = state.player.hp
            result = getattr(state, name)(*args)
            if name == 'heal' and result.ok:
                self.renderer.add_floater(state.player.cell, f'+{state.player.hp - hp_before}',
                                          WATER, state.elapsed)
        self._play_attack_sounds()
        self._sync_context()
        if name != 'attack' or not result.ok:
            self.game.sound('confirm' if result.ok else 'error')
        return result

    def handle_events(self, events):
        self._sync_context()
        self._refresh_camera()
        state = self.game.state
        for event in events:
            if state.active_dialogue is not None:
                # La ventana captura TODO el input de partida: ningún clic o
                # tecla de avance llega a botones, rutas ni interacciones.
                if event.type == pygame.KEYDOWN and not getattr(event, 'repeat', False):
                    if event.key == pygame.K_ESCAPE:
                        self.command('close_dialogue')
                    elif event.key in (pygame.K_e,pygame.K_RETURN,pygame.K_SPACE):
                        self.command('advance_dialogue')
                elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                      and self.dialogue_view.continue_rect.collidepoint(event.pos)):
                    self.command('advance_dialogue')
                if state.active_dialogue is None:
                    self.hover_cell = None
                    return  # También consume el resto del lote al cerrar.
                continue
            if event.type == pygame.MOUSEMOTION:
                self._pointer_pos = event.pos
                self.hover_cell = self.renderer.pick(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._pointer_pos = event.pos
                # Los paneles completos, no solo sus botones, capturan los clics.
                if not WORLD_RECT.collidepoint(event.pos):
                    for button in self.buttons:
                        button.handle_event(event)
                    continue
                cell = self.renderer.pick(event.pos)
                if not state.grid.in_bounds(cell):
                    continue
                self.hover_cell = cell
                target = next((u for u in state.enemies.values() if u.hp > 0 and u.cell == cell), None)
                if state.mode == 'combat' and target is not None:
                    if target.id == state.active_enemy_id and state.grid.can_step(state.player.cell, cell):
                        self.command('attack')  # Clic en el rival vecino = Llave (ataque básico).
                    else:
                        state.message = 'Está lejos: acércate a una casilla vecina (1 PA por paso) y haz clic de nuevo.'
                        self.game.sound('click')
                else:
                    self.command('set_destination', cell)
            elif event.type == pygame.KEYDOWN:
                directions = {pygame.K_w: (0, -1), pygame.K_s: (0, 1),
                              pygame.K_a: (-1, 0), pygame.K_d: (1, 0)}
                if event.key in directions:
                    self.command('move_direction', directions[event.key])
                elif event.key == pygame.K_ESCAPE:
                    if not getattr(event, 'repeat', False):
                        self.game.change_scene('pause')
                    return
                elif event.key == pygame.K_SPACE:
                    self.command('end_turn')
                elif event.key == pygame.K_e:
                    self.command('interact')
                elif event.key == pygame.K_F3:
                    self.renderer.debug_navigation = not self.renderer.debug_navigation

    def update(self, dt):
        self._sync_context()
        before = self.game.state.elapsed
        self.game.state.update(dt)
        self._play_attack_sounds()
        self._sync_context()
        self.renderer.update_ambient(self.game.state.elapsed - before, self.game.state)
        self._refresh_camera()

    def draw(self, surface):
        self._sync_context()
        state = self.game.state
        self._refresh_camera()
        path, reachable = self.renderer.draw(surface, state, self.hover_cell)
        pygame.draw.rect(surface, PANEL, (0, 0, 1008, 90))
        self.type.text(surface, 'LA ÚLTIMA VÁLVULA', (28, 20), 34)
        self.type.text(surface, state.world.name, (28, 63), 20, AMBER)
        self.type.text(surface, 'Suelo conectado · F3: rutas' if state.map_id in self.renderer.layered_maps else 'E vecino: viajar', (430, 63), 20, MUTED)
        self.type.text(surface, f'{self.renderer.camera.zoom:.0%}', (831, 63), 20, TEXT)
        mode = 'COMBATE' if state.mode == 'combat' else 'EXPLORACIÓN'
        self.type.text(surface, mode, (714, 25), 24, RED if state.mode == 'combat' else WATER)
        pygame.draw.rect(surface, PANEL, (1008, 0, 272, 800))
        pygame.draw.line(surface, EDGE, (1008, 0), (1008, 800), 2)
        t = self.type
        t.text(surface, 'VERA', (1034, 28), 34, WATER)
        t.text(surface, f'Vida  {state.player.hp} / {state.player.max_hp}', (1034, 73), 26)
        bar(surface, pygame.Rect(1034, 107, 214, 12), state.player.hp, state.player.max_hp, WATER)
        if state.mode == 'combat':
            t.text(surface, f'PA  {state.player.ap} / 6', (1034, 137), 30, AMBER)
            turn = 'Tu turno' if state.turn == 'player' else 'Turno enemigo'
            t.text(surface, turn, (1034, 174), 24, TEXT)
        else:
            t.text(surface, 'Movimiento libre', (1034, 142), 26, WATER)
            t.text(surface, 'Sin gasto de PA', (1034, 177), 22, MUTED)
        t.text(surface, f'Botiquines: {state.medkits}', (1034, 218), 26)
        t.text(surface, 'Credencial: ' + ('SÍ' if state.credential else 'NO'), (1034, 252), 24, WATER if state.credential else AMBER)
        pygame.draw.line(surface, EDGE, (1034, 290), (1248, 290))
        t.text(surface, 'OBJETIVO', (1034, 312), 24, AMBER)
        t.wrapped(surface, objective(state), (1034, 347), 214, 24)
        enemy = state.enemies.get(state.active_enemy_id)
        hovered = next((u for u in state.enemies.values() if u.hp > 0 and u.cell == self.hover_cell), None)
        enemy = hovered or enemy
        if enemy:
            t.text(surface, 'LA CUSTODIA', (1034, 432), 22, RED)
            t.wrapped(surface, enemy.name, (1034, 464), 210, 24)
            t.text(surface, f'Vida {enemy.hp} / {enemy.max_hp}', (1034, 502), 24)
            bar(surface, pygame.Rect(1034, 534, 214, 9), enemy.hp, enemy.max_hp, RED)
        elif state.map_id == 'hondonada':
            t.wrapped(surface, 'La Hondonada lleva días sin agua. Abre el paso de mantenimiento y busca suministros.', (1034, 431), 214, 22, MUTED)
        t.text(surface, 'WASD / clic: mover', (1034, 588), 22, MUTED)
        t.text(surface, 'Escape: pausa / opciones', (1034, 616), 22, MUTED)
        t.text(surface, 'E: recoger / activar', (1034, 644), 22, MUTED)
        t.text(surface, 'Espacio: fin de turno', (1034, 672), 22, MUTED)
        pygame.draw.rect(surface, PANEL, (0, 640, 1008, 160))
        pygame.draw.line(surface, EDGE, (0, 640), (1008, 640), 2)
        route = (combat_hint(state) if state.mode == 'combat'
                 else 'Selecciona una casilla · Verde: alcance disponible · Ámbar: resto')
        if path:
            if state.mode == 'combat':
                route = f'Ruta: {len(path)} pasos · costo {reachable} PA · quedan {state.player.ap - reachable} PA · ámbar: descartado'
            else:
                route = f'Ruta: {len(path)} pasos · exploración sin gasto de PA'
        t.text(surface, route, (28, 660), 22, WATER if path else MUTED)
        for button in self.buttons:
            combat_only = button in self.buttons[:4]
            button.color = (49, 65, 71) if not combat_only or state.mode == 'combat' else (34, 43, 47)
            button.hover_color = (69, 94, 98)
            if button is self.buttons[3] and end_turn_advised(state):
                # Ámbar apagado: lo único útil que queda es terminar el turno.
                button.color, button.hover_color = (126, 92, 40), (160, 118, 52)
            if button is self.buttons[2]:
                button.text, usable = medkit_status(state)
                if state.mode == 'combat' and not usable:
                    button.color = (34, 43, 47)
            button.draw(surface)
        if state.active_dialogue is None:
            t.wrapped(surface, state.message or 'Busca suministros y avanza hacia la sala de control.', (28, 755), 952, 22, TEXT)
        # Procedencia visible: no se presentan las geometrías propias como pack terminado.
        t.text(surface, 'Ilustración por capas · F3: navegación' if state.map_id in self.renderer.layered_maps else 'Escenarios: módulos de atlas · layout provisional', (28, 611), 18, MUTED)
        if state.active_dialogue is not None:
            self.dialogue_view.draw(surface,state.active_dialogue)


class TerminalScene(Scene):
    won = False
    def __init__(self, game):
        super().__init__(game)
        self.type = Typography()
        self.buttons = [make_button(game, 460, 465, 360, 56, 'Nueva partida', game.start_new_game, 30),
                        make_button(game, 460, 540, 360, 50, 'Volver al menú', self.to_menu, 26)]

    def to_menu(self):
        self.game.sound('back')
        self.game.change_scene('menu')

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.to_menu()

    def draw(self, surface):
        surface.fill(BG)
        emblem(surface, (640, 205), 78, self.won)
        title = 'EL AGUA VUELVE' if self.won else 'LA PLANTA NO CEDE'
        image = self.type.fonts[64].render(title, True, WATER if self.won else RED)
        surface.blit(image, image.get_rect(center=(640, 342)))
        subtitle = 'Vera restauró el suministro. La Hondonada vuelve a tener futuro.' if self.won else 'Vera cayó. Cada paso y cada punto de acción importan.'
        image = self.type.fonts[26].render(subtitle, True, MUTED)
        surface.blit(image, image.get_rect(center=(640, 400)))
        for button in self.buttons:
            button.draw(surface)
        self.type.text(surface, 'La última válvula · Primera iteración', (80, 745), 22, MUTED)


class VictoryScene(Scene):
    """Créditos aportados intactos, con escala proporcional y botón ilustrado."""
    def __init__(self, game):
        super().__init__(game)
        source = game.assets.get_image('credits')
        self.image_rect = source.get_rect().fit(game.screen.get_rect())
        self.image_rect.center = game.screen.get_rect().center
        # Es arte RGB opaco: evitar alfa interpolado al escalar convert_alpha().
        self.image = pygame.transform.smoothscale(source.convert(), self.image_rect.size)
        # Coordenadas de autoría del botón: misma transformación que la imagen.
        x, y, width, height = game.manifest['images']['credits']['menu_button']
        sx = self.image_rect.width / source.get_width()
        sy = self.image_rect.height / source.get_height()
        self.return_rect = pygame.Rect(self.image_rect.x + round(x * sx),
                                       self.image_rect.y + round(y * sy),
                                       round(width * sx), round(height * sy))

    def to_menu(self):
        self.game.sound('back')
        self.game.change_scene('menu')

    def handle_events(self, events):
        for event in events:
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    and self.return_rect.collidepoint(event.pos)):
                self.to_menu()
                return
            if (event.type == pygame.KEYDOWN
                    and event.key in (pygame.K_ESCAPE, pygame.K_RETURN)):
                self.to_menu()
                return

    def draw(self, surface):
        surface.fill((0, 0, 0))
        surface.blit(self.image, self.image_rect)


class DefeatScene(TerminalScene):
    won = False
