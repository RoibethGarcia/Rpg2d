"""Cámara de presentación: recorte entero y su transformación inversa exacta."""


class ZoomCamera:
    LEVELS = (1.0, 1.25, 1.5)

    def __init__(self, viewport):
        self.viewport = tuple(viewport)
        self.level = 0
        self.crop = self.viewport

    @property
    def zoom(self):
        return self.LEVELS[self.level]

    def step(self, direction):
        self.level = max(0, min(len(self.LEVELS) - 1, self.level + direction))

    def follow(self, point):
        x, y, width, height = self.viewport
        w, h = round(width / self.zoom), round(height / self.zoom)
        # No mostrar fuera de la vista general; cerca del borde Vera deja de
        # estar centrada, pero no sale de pantalla por mover la cámara.
        left = max(x, min(x + width - w, round(point[0] - w / 2)))
        top = max(y, min(y + height - h, round(point[1] - h / 2)))
        self.crop = (left, top, w, h)

    def screen(self, point):
        x, y, width, height = self.viewport
        left, top, w, h = self.crop
        return (x + (point[0] - left) * width / w,
                y + (point[1] - top) * height / h)

    def source(self, point):
        x, y, width, height = self.viewport
        left, top, w, h = self.crop
        return (left + (point[0] - x) * w / width,
                top + (point[1] - y) * h / height)
