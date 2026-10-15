# engine/asset_manager.py
import pygame

from engine.spritesheet import Spritesheet


class AssetManager:
    def __init__(self):
        self.spritesheets = {}
        self.images = {}
        self.sounds = {}

    def load_spritesheet(self, name, json_path):
        """Carga un spritesheet desde un JSON y lo guarda con un nombre clave."""
        self.spritesheets[name] = Spritesheet(json_path)
    def load_image(self, name, image_path):
        """Carga una imagen suelta y la guarda con un nombre clave."""
        self.images[name] = pygame.image.load(image_path).convert_alpha()
    def get_sprite(self, sheet_name, sprite_name):
        """Obtiene un sprite específico de un spritesheet ya cargado."""
        if sheet_name not in self.spritesheets:
            raise KeyError(f"No se ha cargado un spritesheet con el nombre '{sheet_name}'")
        return self.spritesheets[sheet_name].get_sprite(sprite_name)

    def get_animation(self, sheet_name, anim_name):
        """Obtiene los frames de una animación de un spritesheet ya cargado."""
        if sheet_name not in self.spritesheets:
            raise KeyError(f"No se ha cargado un spritesheet con el nombre '{sheet_name}'")
        return self.spritesheets[sheet_name].get_animation_frames(anim_name)

    def get_image(self, name):
        """Obtiene una imagen suelta ya cargada."""
        if name not in self.images:
            raise KeyError(f"No se ha cargado una imagen con el nombre '{name}'")
        return self.images[name]

    def load_sound(self, name, sound_path):
        """Carga audio real; los errores de SDL/archivo se propagan."""
        self.sounds[name] = pygame.mixer.Sound(str(sound_path))

    def get_sound(self, name):
        """Obtiene un sonido previamente cargado."""
        if name not in self.sounds:
            raise KeyError(f"No se ha cargado un sonido con el nombre '{name}'")
        return self.sounds[name]
