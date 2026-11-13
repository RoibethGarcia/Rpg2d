"""Une motor, escenas y dominio sin crear un segundo bucle principal."""
import json
from pathlib import Path
import pygame

from engine.asset_manager import AssetManager
from engine.game_loop import GameLoop
from game.menu_backdrop import MenuBackdrop
from game.model import GameState
from game.ending import EndingScene
from game.howto import HowToPlayScene
from game.scenes import MenuScene, OptionsScene, PauseScene, PlayScene, VictoryScene, DefeatScene

ROOT = Path(__file__).resolve().parents[1]


class LastValveGame(GameLoop):
    def __init__(self, audio_enabled=True):
        super().__init__(1280, 800, 'La última válvula', 60, audio_enabled=audio_enabled)
        # Ganancias relativas: 100 % conserva el balance original de cada recurso.
        self.music_volume = 1.0
        self.effects_volume = 1.0
        self.assets = AssetManager()
        self.manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
        for name, resource in self.manifest['images'].items():
            self.assets.load_image(name, ROOT / resource['path'])
        if audio_enabled:
            pygame.mixer.set_reserved(1)
            self.ui_channel = pygame.mixer.Channel(0)
            for name, resource in self.manifest['sounds'].items():
                self.assets.load_sound(name, ROOT / resource['path'])
            for kind, resource in self.manifest['combat_sounds'].items():
                self.assets.load_sound(f'combat_{kind}', ROOT / resource['path'])
            self.set_effects_volume(self.effects_volume)
        self.state = None
        self._ambience_map = None
        self.backdrop = MenuBackdrop(self)
        self.scenes = {'menu': MenuScene(self), 'options': OptionsScene(self), 'howto': HowToPlayScene(self), 'ending': EndingScene(self),
                       'play': PlayScene(self), 'pause': PauseScene(self),
                       'victory': VictoryScene(self), 'defeat': DefeatScene(self)}
        self.current_scene = self.scenes['menu']

    def set_effects_volume(self, volume):
        self.effects_volume = max(0.0, min(1.0, volume))
        if not self.audio_enabled:
            return
        for name in self.manifest['sounds']:
            self.assets.get_sound(name).set_volume(.35 * self.effects_volume)
        for kind, resource in self.manifest['combat_sounds'].items():
            self.assets.get_sound(f'combat_{kind}').set_volume(
                resource['volume'] * self.effects_volume)

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        if self.audio_enabled and self._ambience_map is not None:
            resource = self.manifest['ambiences'][self._ambience_map]
            pygame.mixer.music.set_volume(resource['volume'] * self.music_volume)

    def sound(self, name):
        if self.audio_enabled:
            self.ui_channel.play(self.assets.get_sound(name))

    def combat_sound(self, kind):
        if self.audio_enabled:
            # Sound.play usa canales libres, nunca el canal 0 reservado a UI.
            # Permite solapar las colas de varios golpes sin reiniciar el anterior.
            self.assets.get_sound(f'combat_{kind}').play()

    def stop_combat_sounds(self):
        if self.audio_enabled:
            for kind in self.manifest['combat_sounds']:
                self.assets.get_sound(f'combat_{kind}').stop()

    def _stop_ambience(self):
        if self.audio_enabled and self._ambience_map is not None:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            self._ambience_map = None

    def _sync_ambience(self):
        """Solo cargar al cambiar de mapa; el stream no usa el canal de UI."""
        if not self.audio_enabled:
            return
        map_id = (self.state.map_id if self._in_gameplay()
                  and self.state is not None else None)
        resource = self.manifest['ambiences'].get(map_id)
        target = map_id if resource is not None else None
        if target == self._ambience_map:
            return
        self._stop_ambience()
        if resource is not None:
            pygame.mixer.music.load(str(ROOT / resource['path']))
            pygame.mixer.music.set_volume(resource['volume'] * self.music_volume)
            pygame.mixer.music.play(loops=-1)
            self._ambience_map = target

    def _in_gameplay(self):
        """Pausa y sus opciones conservan la partida y la pista actual."""
        return (self.current_scene in (self.scenes['play'], self.scenes['pause'])
                or (self.current_scene is self.scenes['options']
                    and self.scenes['options'].return_scene == 'pause'))

    def start_new_game(self, map_id='hondonada'):
        if map_id not in ('hondonada', 'puesto', 'planta'):
            raise ValueError('Mapa inicial de prueba no permitido')
        self._stop_ambience()
        self.state = GameState.new()
        self.state.medkits = 3  # Temporal para pruebas; el balance base conserva 1.
        if map_id == 'puesto':
            self.state.player.cell = (4, 10)
            if not self.state.travel('to_puesto'):
                raise ValueError('Aparición inicial del puesto inválida')
        elif map_id == 'planta':
            # Acceso de prueba explícito: no abrir mantenimiento, curar una
            # partida existente ni conceder bajas/credencial para saltar reglas.
            self.state.map_id = 'planta'
            self.state.player.cell = self.state.maps['puesto'].exits['to_planta'].spawn
            self.state.validate_campaign()
            self.state.message = 'Planta: explora las escaleras, busca botiquines y vence al jefe. Después activa la válvula con E.'
        self.scenes['play'].reset()
        self.change_scene('play')
        self.sound('confirm')

    def change_scene(self, scene_name):
        previous = self.current_scene
        if self._in_gameplay() and scene_name not in ('play', 'pause', 'options'):
            # Dejar terminar el golpe letal al mostrar derrota; no reproducirlo otra vez.
            self.scenes['play'].reset(stop_audio=scene_name != 'defeat')
        elif scene_name == 'menu':
            self.stop_combat_sounds()
        if scene_name == 'options':
            self.scenes['options'].on_enter('pause' if previous is self.scenes['pause'] else 'menu')
        if scene_name == 'pause' and previous is self.scenes['play']:
            self.scenes['pause'].on_enter()
        self.current_scene = self.scenes[scene_name]
        if scene_name == 'ending':
            self.scenes['ending'].on_enter()
        if scene_name == 'menu' and previous not in (self.scenes['options'], self.scenes['howto']):
            self.scenes['menu'].on_enter()
        self._sync_ambience()

    def stop(self):
        self._stop_ambience()
        self.scenes['play'].reset()
        super().stop()

    def handle_specific_events(self, event):
        self.current_scene.handle_events([event])
        self._sync_ambience()

    def update_game_logic(self, dt):
        self.current_scene.update(dt)
        if self.current_scene is self.scenes['play'] and self.state.mode in ('victory', 'defeat'):
            # La victoria pasa por la pantalla de cierre antes de los créditos.
            self.change_scene('ending' if self.state.mode == 'victory' else self.state.mode)
            self.sound('confirm' if self.state.mode == 'victory' else 'error')
        self._sync_ambience()

    def draw_game_elements(self):
        self.current_scene.draw(self.screen)
