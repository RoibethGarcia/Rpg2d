"""Ventana modal: skin cacheada y texto dinámico, sin reglas de campaña."""
import pygame

from game.render import TEXT, AMBER, WATER


class DialogueView:
    def __init__(self, game):
        record = game.manifest['images']['dialogue_frame']
        source = game.assets.get_image('dialogue_frame')
        width = 1240
        scale = width / source.get_width()
        self.skin = pygame.transform.smoothscale(source, (width, round(source.get_height()*scale)))
        self.rect = self.skin.get_rect(midbottom=(640,790))
        self.regions = {}
        for name, (x,y,w,h) in record['layout'].items():
            region = pygame.Rect(round(x*scale),round(y*scale),round(w*scale),round(h*scale))
            region.move_ip(self.rect.topleft)
            if not self.rect.contains(region):
                raise ValueError(f'Región de diálogo fuera del marco: {name}')
            self.regions[name] = region
        self.continue_rect = self.regions['continue_button']
        self.body_font = pygame.font.Font(None,30)
        self.name_font = pygame.font.Font(None,32)
        self.small_font = pygame.font.Font(None,20)
        self.button_font = pygame.font.Font(None,26)
        self.shade = pygame.Surface((1280,800),pygame.SRCALPHA)
        self.shade.fill((3,8,11,110))
        self._page_key = None
        self._lines = []

    def _prepare(self, dialogue):
        key = (dialogue.npc_id,dialogue.speaker,dialogue.index,dialogue.text,len(dialogue.pages))
        if key == self._page_key:
            return
        width = self.regions['body'].width
        lines = []
        line = ''
        for word in dialogue.text.split():
            candidate = f'{line} {word}'.strip()
            if self.body_font.size(candidate)[0] > width:
                if not line or self.body_font.size(word)[0] > width:
                    raise ValueError('Palabra de diálogo demasiado ancha para el marco')
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        if len(lines)*(self.body_font.get_linesize()+3) > self.regions['body'].height:
            raise ValueError('Página de diálogo demasiado larga: dividir el texto en los datos')
        self._lines = [self.body_font.render(line,True,TEXT) for line in lines]
        self._name = self.name_font.render(dialogue.speaker,True,TEXT)
        if self._name.get_width() > self.regions['name'].width:
            raise ValueError('Nombre de interlocutor demasiado ancho para el marco')
        last = dialogue.index+1 == len(dialogue.pages)
        self._button = self.button_font.render('Cerrar  >' if last else 'Continuar  >',True,TEXT)
        self._hint = self.small_font.render(f'{dialogue.index+1}/{len(dialogue.pages)}  ·  E / Enter / Espacio  ·  Esc: cerrar',True,AMBER)
        self._page_key = key

    def draw(self, surface, dialogue):
        self._prepare(dialogue)
        surface.blit(self.shade,(0,0))
        surface.blit(self.skin,self.rect)
        surface.blit(self._name,self._name.get_rect(midleft=self.regions['name'].midleft))
        x,y = self.regions['body'].topleft
        for line in self._lines:
            surface.blit(line,(x,y))
            y += self.body_font.get_linesize()+3
        if self.continue_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface,WATER,self.continue_rect,1,border_radius=4)
        surface.blit(self._button,self._button.get_rect(center=self.continue_rect.center))
        surface.blit(self._hint,self.regions['hint'].topleft)
