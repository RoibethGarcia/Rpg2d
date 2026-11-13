"""Cierre del primer nivel: aparece en secuencia sobre el paisaje vivo y lleva a los créditos."""
import math
import pygame
from engine.ui import Scene
from game.menu_nav import MenuSelection, reveal
from game.render import AMBER, EDGE, MUTED, TEXT, WATER, Typography
from game.scenes import emblem, glass_button, make_button


def glow(radius, color):
    """Halo radial suave, preparado una sola vez."""
    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -4):
        pygame.draw.circle(surface, (*color, int(80 * (1 - r / radius) ** 2)), (radius, radius), r)
    return surface


class EndingScene(Scene):
    READY = 3.6  # Hasta aquí la secuencia termina; antes, la primera entrada solo la salta.
    FADE_SECONDS = .8
    REVEALS = {'emblem': (.3, .6), 'title': (.9, .6), 'subtitle': (1.6, .6),
               'stats': (2.2, .6), 'note': (2.8, .5), 'buttons': (3.1, .5)}
    title = 'FIN DEL PRIMER NIVEL'
    subtitle = 'El agua vuelve a La Hondonada.'
    note = 'Prueba del juego · se vienen más niveles'

    def __init__(self, game):
        super().__init__(game)
        self.type = Typography()
        self.backdrop = game.backdrop
        self.elapsed = 0.0
        self.angle = 0.0
        self.selection = MenuSelection(2)
        self.veil = pygame.Surface((1280, 800))
        self.buttons = [make_button(game, 460, 585, 360, 56, 'Ver créditos', self.to_credits, 30),
                        make_button(game, 460, 655, 360, 46, 'Volver al menú', self.to_menu, 26)]
        self.layers = [pygame.Surface(b.rect.size, pygame.SRCALPHA) for b in self.buttons]
        self.emblem_layer = pygame.Surface((160, 160), pygame.SRCALPHA)
        self.halo = glow(210, WATER)
        self.card = pygame.Surface((200, 66), pygame.SRCALPHA)
        pygame.draw.rect(self.card, (22, 31, 36, 190), self.card.get_rect(), border_radius=10)
        pygame.draw.rect(self.card, EDGE, self.card.get_rect(), 2, border_radius=10)

    def reveal_of(self, name, delay=0.0):
        start, duration = self.REVEALS[name]
        return reveal(self.elapsed, start + delay, duration)

    def on_enter(self):
        self.elapsed = 0.0
        self.angle = 0.0
        self.selection.set(0)

    def to_credits(self):
        self.game.sound('confirm')
        self.game.change_scene('victory')

    def to_menu(self):
        self.game.sound('back')
        self.game.change_scene('menu')

    def update(self, dt):
        self.elapsed += dt
        self.angle = (self.angle + 8 * dt) % 360
        self.backdrop.update(dt)

    def activate(self):
        (self.to_credits, self.to_menu)[self.selection.index]()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.to_menu()
                return
            pressed = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (
                event.type == pygame.KEYDOWN and event.key in
                (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE))
            if pressed and self.elapsed < self.READY:
                self.elapsed = self.READY  # Saltar la animación; no salir por accidente.
                return
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

    def shadowed(self, surface, text, size, color, amount, dy=0, **anchor):
        if amount <= 0:
            return
        font = self.type.fonts[size]
        image, shade = font.render(text, True, color), font.render(text, True, (4, 7, 10))
        for item in (image, shade):
            item.set_alpha(round(255 * amount))
        rect = image.get_rect(**anchor).move(0, dy + round((1 - amount) * 12))
        surface.blit(shade, rect.move(2, 2))
        surface.blit(image, rect)

    def stats(self):
        state = self.game.state
        if state is None:
            return ()
        return (('VIDA', f'{state.player.hp} / {state.player.max_hp}'),
                ('BOTIQUINES', str(state.medkits)),
                ('CREDENCIAL', 'Recuperada' if state.credential else 'No'))

    def draw(self, surface):
        self.backdrop.draw(surface)
        shown = self.reveal_of('emblem')
        if shown > 0:
            pulse = .75 + .25 * math.sin(self.elapsed * 1.6)
            self.halo.set_alpha(round(255 * shown * pulse))
            surface.blit(self.halo, self.halo.get_rect(center=(640, 150)))
            self.emblem_layer.fill((0, 0, 0, 0))
            emblem(self.emblem_layer, (80, 80), 60, water=True, angle=self.angle)
            self.emblem_layer.set_alpha(round(255 * shown))
            surface.blit(self.emblem_layer, (560, 70 + round((1 - shown) * 12)))
        self.shadowed(surface, self.title, 80, TEXT, self.reveal_of('title'), center=(640, 292))
        if self.reveal_of('title') >= 1:
            pygame.draw.line(surface, AMBER, (440, 336), (840, 336), 2)
        self.shadowed(surface, self.subtitle, 34, TEXT, self.reveal_of('subtitle'), center=(640, 372))
        shown = self.reveal_of('stats')
        for index, (label, value) in enumerate(self.stats()):
            left = 640 + (index - 1) * 216 - 100
            self.card.set_alpha(round(255 * shown))
            surface.blit(self.card, (left, 415 + round((1 - shown) * 12)))
            if shown >= 1:
                for text, size, color, y in ((label, 20, MUTED, 432), (value, 30, TEXT, 456)):
                    image = self.type.fonts[size].render(text, True, color)
                    surface.blit(image, image.get_rect(center=(left + 100, y)))
        self.shadowed(surface, self.note, 26, AMBER, self.reveal_of('note'), center=(640, 530))
        for index, button in enumerate(self.buttons):
            amount = self.reveal_of('buttons', .1 * index)
            if amount > 0:
                glass_button(surface, self.layers[index], button.rect.topleft, button.text,
                             button.font, self.selection.index == index, index == 0, amount)
        self.shadowed(surface, 'La última válvula · Taller de Videojuegos 2D · 2026', 20, MUTED, 1,
                      topleft=(80, 745))
        if self.elapsed < self.FADE_SECONDS:
            t = self.elapsed / self.FADE_SECONDS
            self.veil.set_alpha(round(255 * (1 - t * t * (3 - 2 * t))))
            surface.blit(self.veil, (0, 0))
