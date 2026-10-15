# engine/game_object.py
import pygame


class GameObject(pygame.sprite.Sprite):
    """
    Clase base mejorada que maneja imágenes estáticas y animaciones.
    """

    def __init__(self, x, y, frames):
        super().__init__()

        # frames puede ser una sola Surface o una lista de Surfaces
        if isinstance(frames, list):
            self.frames = frames
            self.is_animated = True
            self.current_frame = 0
            self.image = self.frames[self.current_frame]
            self.anim_speed = 6.0  # Frames por segundo; equivale a 0.1 por tick a 60 FPS.
            self.anim_timer = 0
        else:
            self.frames = [frames]
            self.is_animated = False
            self.image = frames

        self.rect = self.image.get_rect(center=(x, y))

    def update_animation(self, dt):
        """Actualiza el frame de la animación si es necesario."""
        if not self.is_animated or len(self.frames) < 2:
            return

        self.anim_timer += self.anim_speed * dt
        steps = int(self.anim_timer)
        if steps:
            self.anim_timer -= steps
            self.current_frame = (self.current_frame + steps) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def update(self, dt=0):
        """El método update ahora también se encarga de la animación."""
        self.update_animation(dt)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
