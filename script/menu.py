import pygame as pg
import random

import constants as C
from particle import Particle

class Factory:
    def __init__(self, screen: pg.Surface, menu_path: str = C.MENU_PATH) -> None:
        self.background = pg.Surface(screen.get_size())
        self.background.fill((0, 0, 0))
        self.background.set_alpha(0)
        self.background.convert()

        self.animation_cooldown = 0
        
        self.spritesheet = pg.image.load(menu_path + "Factory.png").convert_alpha()
        self.animation_list = []
        for frame in range(4):
            current_frame = pg.transform.smoothscale_by(self.spritesheet.subsurface(frame*1920, 0, 1920, 1080), C.SCALE_X)
            self.animation_list.append(current_frame)
        self.current_frame = 0
        self.image = self.animation_list[self.current_frame]

    def update(self) -> None:
        self.animation_cooldown = (self.animation_cooldown+1)%6
        if not self.animation_cooldown:
            self.update_animation()

    def update_animation(self) -> None:
        self.current_frame = (self.current_frame+1)%len(self.animation_list)
        self.image = self.animation_list[self.current_frame]

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.background, (0, 0))
        screen.blit(self.image, (0,0))

class SellBox(pg.Rect):
    def __init__(self, left: float, top: float, width: float, height: float):
        super().__init__(left, top, width, height)
        self.left = left
        self.top = top
        self.height = height
        self.width = width

    def update(self, particle_list: list):
        for i in range(0, int(self.width), 2):
            rv = random.random()**2 / 1.5
            particle_list.append(Particle(color = [255,254,181,255], pos = (self.left + i, self.top + self.height), size = 1, velocity = (0.5,-2), gravity = 0, timer = rv, is_randomized = (True, False)))

class Background:
    def __init__(self, data: list) -> None:
        self.image: pg.Surface = data[0]
        self.x = -data[1][0]*C.SCALE_X
        self.y = -data[1][1]*C.SCALE_Y
        self.rect = self.image.get_rect(topleft=(self.x,self.y))

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)

class Storage:
    def __init__(self, menu_path: str = C.MENU_PATH):
        self.image = pg.transform.scale_by(pg.image.load(menu_path + "Storage.png").convert_alpha(), C.SCALE_X)

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, (0,0))