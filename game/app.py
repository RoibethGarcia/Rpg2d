"""Une motor, escenas y dominio sin crear un segundo bucle principal."""
import json
from pathlib import Path
import pygame

from engine.asset_manager import AssetManager
from engine.game_loop import GameLoop
from game.model import GameState
from game.scenes import MenuScene, PlayScene, VictoryScene, DefeatScene

ROOT = Path(__file__).resolve().parents[1]


class LastValveGame(GameLoop):
    def __init__(self, audio_enabled=True):
        super().__init__(1280, 800, 'La última válvula', 60, audio_enabled=audio_enabled)
        self.assets = AssetManager()
        self.manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
        for name, resource in self.manifest['images'].items():
            self.assets.load_image(name, ROOT / resource['path'])
        if audio_enabled:
            pygame.mixer.set_reserved(1)
            self.ui_channel = pygame.mixer.Channel(0)
            for name, resource in self.manifest['sounds'].items():
                self.assets.load_sound(name, ROOT / resource['path'])
                self.assets.get_sound(name).set_volume(.35)
        self.state = None
        self.scenes = {'menu': MenuScene(self), 'play': PlayScene(self),
                       'victory': VictoryScene(self), 'defeat': DefeatScene(self)}
        self.current_scene = self.scenes['menu']

    def sound(self, name):
        if self.audio_enabled:
            self.ui_channel.play(self.assets.get_sound(name))

    def start_new_game(self):
        self.state = GameState.new()
        self.scenes['play'].reset()
        self.change_scene('play')
        self.sound('confirm')

    def change_scene(self, scene_name):
        self.current_scene = self.scenes[scene_name]

    def handle_specific_events(self, event):
        self.current_scene.handle_events([event])

    def update_game_logic(self, dt):
        self.current_scene.update(dt)
        if self.current_scene is self.scenes['play'] and self.state.mode in ('victory', 'defeat'):
            self.change_scene(self.state.mode)
            self.sound('confirm' if self.state.mode == 'victory' else 'error')

    def draw_game_elements(self):
        self.current_scene.draw(self.screen)
