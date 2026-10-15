# engine/ui.py
import pygame

class Scene:
    """Clase base para todas las escenas del juego."""
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        pass
    def update(self, dt):
        pass
    def draw(self, surface):
        pass

class Button:
    def __init__(self, x, y, width, height, text, callback, click_sound=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.click_sound = click_sound
        self.font = pygame.font.Font(None, 40)
        self.color = (50, 50, 80)
        self.hover_color = (80, 80, 110)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.click_sound is not None:
                    self.click_sound.play()
                self.callback()

    def draw(self, surface):
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))
