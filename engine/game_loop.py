import pygame


class GameLoop:
    """
    Clase base que gestiona el bucle principal, eventos, actualizaciones y dibujado.
    Los juegos específicos deben heredar de esta clase.
    """

    def __init__(self, screen_width, screen_height, title, fps, audio_enabled=True):
        pygame.display.init()
        pygame.font.init()
        self.audio_enabled = audio_enabled
        if audio_enabled:
            pygame.mixer.init()

        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.running = False

    def _handle_events(self):
        """Maneja eventos globales como cerrar la ventana."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                break
            # Pasa los eventos a la clase hija para manejo específico
            self.handle_specific_events(event)

    def _update(self, dt):
        """Llama al método de actualización de la clase hija."""
        self.update_game_logic(dt)

    def _draw(self):
        """Llama al método de dibujado de la clase hija."""
        self.draw_game_elements()
        pygame.display.flip()

    def run(self):
        """El bucle principal del juego."""
        self.running = True
        try:
            while self.running:
                dt = self.clock.tick(self.fps) / 1000.0
                self._handle_events()
                if not self.running:
                    break
                self._update(dt)
                if self.running:
                    self._draw()
        finally:
            pygame.quit()

    def stop(self):
        self.running = False

    # --- Métodos para ser sobreescritos por las clases hijas ---
    def handle_specific_events(self, event):
        """Maneja los eventos específicos del juego (input, etc.)."""
        pass

    def update_game_logic(self, dt):
        """Actualiza la lógica específica del juego."""
        pass

    def draw_game_elements(self):
        """Dibuja los elementos específicos del juego."""
        pass
