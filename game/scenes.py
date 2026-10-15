"""Escenas concretas; input de UI nunca atraviesa hasta el mundo."""
import pygame
from engine.ui import Scene, Button
from game.render import (Typography, WorldRenderer, WORLD_RECT, BG, PANEL,
                         EDGE, TEXT, MUTED, WATER, AMBER, RED, bar)


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


def emblem(surface, center, radius=90, water=False):
    x, y = center
    color = WATER if water else AMBER
    pygame.draw.circle(surface, (35, 47, 52), center, radius + 9)
    pygame.draw.circle(surface, color, center, radius, 7)
    pygame.draw.circle(surface, color, center, radius // 3, 7)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        pygame.draw.line(surface, color, (x + dx * radius // 3, y + dy * radius // 3),
                         (x + dx * radius, y + dy * radius), 10)


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.type = Typography()
        self.buttons = [make_button(game, 460, 412, 360, 56, 'Comenzar', game.start_new_game, 30),
                        make_button(game, 460, 486, 360, 50, 'Salir', game.stop, 26)]

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game.start_new_game()

    def draw(self, surface):
        surface.fill(BG)
        for x in range(0, 1280, 80):
            pygame.draw.line(surface, (25, 34, 39), (x, 0), (x - 180, 800), 1)
        pygame.draw.line(surface, AMBER, (80, 84), (1200, 84), 2)
        self.type.text(surface, 'LA HONDONADA / PLANTA DE DISTRIBUCIÓN', (80, 49), 22, MUTED)
        emblem(surface, (640, 205), 65)
        title = self.type.fonts[64].render('LA ÚLTIMA VÁLVULA', True, TEXT)
        surface.blit(title, title.get_rect(center=(640, 325)))
        subtitle = 'El agua no pertenece a La Custodia. Devuélvela a La Hondonada.'
        line = self.type.fonts[26].render(subtitle, True, MUTED)
        surface.blit(line, line.get_rect(center=(640, 373)))
        for button in self.buttons:
            button.draw(surface)
        self.type.text(surface, 'EXPLORA', (270, 618), 26, WATER)
        self.type.text(surface, 'DECIDE', (590, 618), 26, AMBER)
        self.type.text(surface, 'RESTAURA', (910, 618), 26, WATER)
        self.type.text(surface, 'WASD o clic · Rejilla isométrica', (225, 656), 22, MUTED)
        self.type.text(surface, 'Combate por turnos · 6 PA', (545, 656), 22, MUTED)
        self.type.text(surface, 'Credencial y panel final', (865, 656), 22, MUTED)
        self.type.text(surface, 'Primera iteración · Arte industrial provisional y recursos acreditados', (80, 745), 20, MUTED)


class PlayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.type = Typography()
        self.renderer = WorldRenderer(game)
        self.hover_cell = None
        self.buttons = [
            make_button(game, 28, 693, 166, 46, 'Llave · 2 PA / 4', lambda: self.command('attack')),
            make_button(game, 206, 693, 178, 46, 'Potente · 3 PA / 7', lambda: self.command('attack', True)),
            make_button(game, 396, 693, 190, 46, 'Botiquín · 2 PA / +8', lambda: self.command('heal')),
            make_button(game, 598, 693, 180, 46, 'Espacio · Fin turno', lambda: self.command('end_turn')),
            make_button(game, 790, 693, 190, 46, 'E · Interactuar', lambda: self.command('interact')),
            make_button(game, 1034, 734, 214, 42, 'Volver al menú', self.to_menu),
        ]

    def reset(self):
        self.hover_cell = None
        self.renderer.reset()

    def to_menu(self):
        self.game.sound('back')
        self.game.change_scene('menu')

    def command(self, name, *args):
        result = getattr(self.game.state, name)(*args)
        self.game.sound('confirm' if result.ok else 'error')
        return result

    def handle_events(self, events):
        state = self.game.state
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.hover_cell = self.renderer.projection.pick(*event.pos) if WORLD_RECT.collidepoint(event.pos) else None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Los paneles completos, no solo sus botones, capturan los clics.
                if not WORLD_RECT.collidepoint(event.pos):
                    for button in self.buttons:
                        button.handle_event(event)
                    continue
                cell = self.renderer.projection.pick(*event.pos)
                if not state.grid.in_bounds(cell):
                    continue
                self.hover_cell = cell
                if state.mode == 'combat' and any(u.hp > 0 and u.cell == cell for u in state.enemies.values()):
                    state.message = 'Enemigo seleccionado. Usa Llave o Potente desde una casilla vecina.'
                    self.game.sound('click')
                else:
                    self.command('set_destination', cell)
            elif event.type == pygame.KEYDOWN:
                directions = {pygame.K_w: (0, -1), pygame.K_s: (0, 1),
                              pygame.K_a: (-1, 0), pygame.K_d: (1, 0)}
                if event.key in directions:
                    self.command('move_direction', directions[event.key])
                elif event.key == pygame.K_ESCAPE:
                    self.command('cancel_route')
                elif event.key == pygame.K_SPACE:
                    self.command('end_turn')
                elif event.key == pygame.K_e:
                    self.command('interact')

    def update(self, dt):
        self.game.state.update(dt)

    def draw(self, surface):
        state = self.game.state
        path, reachable = self.renderer.draw(surface, state, self.hover_cell)
        pygame.draw.rect(surface, PANEL, (0, 0, 1008, 90))
        self.type.text(surface, 'LA ÚLTIMA VÁLVULA', (28, 20), 34)
        self.type.text(surface, '01  Acceso industrial', (28, 63), 20, AMBER)
        self.type.text(surface, '02  Patio de distribución', (354, 63), 20, AMBER)
        self.type.text(surface, '03  Sala de control', (720, 63), 20, AMBER)
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
        objective = 'Activa con E el panel de la sala de control.' if state.credential else 'Cruza la planta y recupera la credencial del jefe.'
        t.wrapped(surface, objective, (1034, 347), 214, 24)
        enemy = state.enemies.get(state.active_enemy_id)
        hovered = next((u for u in state.enemies.values() if u.hp > 0 and u.cell == self.hover_cell), None)
        enemy = hovered or enemy
        if enemy:
            t.text(surface, 'LA CUSTODIA', (1034, 432), 22, RED)
            t.wrapped(surface, enemy.name, (1034, 464), 210, 24)
            t.text(surface, f'Vida {enemy.hp} / {enemy.max_hp}', (1034, 502), 24)
            bar(surface, pygame.Rect(1034, 534, 214, 9), enemy.hp, enemy.max_hp, RED)
        else:
            t.wrapped(surface, 'La Hondonada lleva días sin agua. Abre el paso de mantenimiento y busca suministros.', (1034, 431), 214, 22, MUTED)
        t.text(surface, 'WASD / clic: mover', (1034, 588), 22, MUTED)
        t.text(surface, 'Escape: cancelar ruta', (1034, 616), 22, MUTED)
        t.text(surface, 'E: recoger / activar', (1034, 644), 22, MUTED)
        t.text(surface, 'Espacio: fin de turno', (1034, 672), 22, MUTED)
        pygame.draw.rect(surface, PANEL, (0, 640, 1008, 160))
        pygame.draw.line(surface, EDGE, (0, 640), (1008, 640), 2)
        route = 'Selecciona una casilla · Verde: alcance disponible · Ámbar: resto'
        if path:
            if state.mode == 'combat':
                route = f'Ruta: {len(path)} pasos · costo {reachable} PA · quedan {state.player.ap - reachable} PA · ámbar: descartado'
            else:
                route = f'Ruta: {len(path)} pasos · exploración sin gasto de PA'
        t.text(surface, route, (28, 660), 22, WATER if path else MUTED)
        for button in self.buttons:
            combat_only = button in self.buttons[:4]
            button.color = (49, 65, 71) if not combat_only or state.mode == 'combat' else (34, 43, 47)
            button.draw(surface)
        t.wrapped(surface, state.message or 'Busca suministros y avanza hacia la sala de control.', (28, 755), 952, 22, TEXT)
        # Procedencia visible: no se presentan las geometrías propias como pack terminado.
        t.text(surface, 'Suelo y maquinaria: geometría provisional', (28, 611), 18, MUTED)


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


class VictoryScene(TerminalScene):
    won = True


class DefeatScene(TerminalScene):
    won = False
