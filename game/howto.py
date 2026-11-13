"""Pantalla «Cómo jugar»: las reglas salen de game.config para no desactualizarse."""
import pygame
from engine.ui import Scene
from game.config import (BASIC_COST, BASIC_DAMAGE, HEAL_AMOUNT, HEAL_COST,
                         POWER_COST, POWER_DAMAGE, TURN_AP)
from game.render import AMBER, EDGE, PANEL, Typography
from game.scenes import make_button

HOW_TO_PLAY = (
    ('Moverte', 'WASD o clic para caminar por la rejilla. E recoge objetos, activa '
                'mecanismos y usa salidas. Escape cancela la ruta.'),
    ('Combate por turnos', f'El combate empieza cuando un enemigo y Vera se tocan. Cada turno '
                           f'tienes {TURN_AP} PA: un paso cuesta 1 PA y solo se ataca desde una '
                           f'casilla vecina. El turno termina al quedarte sin PA o con Espacio.'),
    ('Ataques', f'Llave: {BASIC_COST} PA, daño {BASIC_DAMAGE}. Potente: {POWER_COST} PA, '
                f'daño {POWER_DAMAGE}, el que más rinde por PA. Clic en el enemigo vecino = Llave.'),
    ('Botiquín', f'Botiquín: cuesta {HEAL_COST} PA y cura {HEAL_AMOUNT}. El botón muestra cuántos '
                 f'quedan y, si no se puede usar, por qué.'),
    ('Jefe de la planta', 'Ataca varias veces por turno. Retrocede al empezar para que gaste '
                          'sus PA caminando y luego remata con Potente. Llega con vida y botiquines.'),
    ('Objetivo', 'Puesto: pulsa E junto a «Mantenimiento» y cruza a la planta. Planta: derrota '
                 'al jefe, toma su credencial y activa la válvula.'),
)


class HowToPlayScene(Scene):
    PANEL = pygame.Rect(140, 96, 1000, 590)

    def __init__(self, game):
        super().__init__(game)
        self.type = Typography()
        self.backdrop = game.backdrop
        self.panel = pygame.Surface(self.PANEL.size, pygame.SRCALPHA)
        pygame.draw.rect(self.panel, (*PANEL, 228), self.panel.get_rect(), border_radius=12)
        pygame.draw.rect(self.panel, EDGE, self.panel.get_rect(), 2, border_radius=12)
        self.buttons = [make_button(game, 460, 705, 360, 50, 'Volver al menú', self.to_menu, 26)]

    def to_menu(self):
        self.game.sound('back')
        self.game.change_scene('menu')

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.to_menu()
                return
            for button in self.buttons:
                button.handle_event(event)
            if self.game.current_scene is not self:
                return

    def update(self, dt):
        self.backdrop.update(dt)

    def draw(self, surface):
        self.backdrop.draw(surface)
        surface.blit(self.panel, self.PANEL.topleft)
        self.type.text(surface, 'CÓMO JUGAR', (172, 120), 48, AMBER)
        pygame.draw.line(surface, AMBER, (172, 172), (1108, 172), 2)
        for index, (title, text) in enumerate(HOW_TO_PLAY):
            x = 172 + (index % 2) * 470
            y = 196 + (index // 2) * 160
            self.type.text(surface, title.upper(), (x, y), 26, AMBER)
            self.type.wrapped(surface, text, (x, y + 34), 430, 24)
        for button in self.buttons:
            button.draw(surface)
