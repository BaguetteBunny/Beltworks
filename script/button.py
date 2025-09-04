import pygame as pg
import time

import constants as C
from player import Player

class Button:
    def __init__(self,
                 image: pg.Surface,
                 pos: tuple[float | int, float | int] = (0.0, 0.0),
                 click_side: tuple = (True, False),
                 cd: float = 0.33,
                 animated: tuple[int, int] = (0, 0)) -> None:
        
        self.image = image
        self.pos = pos
        self.animated = None
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

        self.original_opacity = self.opacity = 1
        self.hover = 1
        self.cooldown = cd
        self.left_click_enabled = True if click_side[0] or (not click_side[0] and not click_side[1]) else False
        self.right_click_enabled = click_side[1]
        self.last_left_click_time = 0
        self.last_right_click_time = 0

        if all(animated):
            self.animated = animated
            self.animated_frames = self.animated[0]
            self.animated_cd = self.animated[1]

            self.current_frame = pg.time.get_ticks()
            self.animation_list = []
            size = self.image.get_height()
            for frame in range(self.animated_frames):
                current_frame = self.image.subsurface(frame*size, 0, size, size)
                self.animation_list.append(pg.transform.smoothscale_by(current_frame, C.SCALE_X*2))
            
            self.frame = 0
            self.image = self.animation_list[self.frame]

    def draw(self, screen: pg.Surface, rescale: float | int | None = None, opacity: int = 255, rotation: float | int | None = None) -> None:
        # Button Animation
        if self.animated:
            self.image = self.animation_list[self.frame]
            if pg.time.get_ticks() - self.current_frame >= self.animated_cd:
                self.frame = (self.frame+1)%self.animated_frames
                self.current_frame = pg.time.get_ticks()

        # Dynamic Button Rescaling
        if isinstance(rescale, (int, float)):
            self.image = pg.transform.smoothscale_by(self.image, rescale)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
        
        # Dynamic Button Opacity
        self.image.set_alpha(self.opacity)
        if self.is_cooldownless():
            self.opacity = opacity

        # Dynamic Button Rotation
        if rotation:
            self.image = pg.transform.rotate(self.image, rotation)
        
        # Button Draw
        screen.blit(self.image, self.rect)

    def clicked(self, player: Player, click_opacity: float | int = 0) -> bool:
        current_time = time.time()
        
        if self.left_click_enabled and player.left_clicked and self.rect.collidepoint(player.pos):
            if self.is_cooldownless(current_time, self.last_left_click_time):
                self.last_left_click_time = current_time
                if isinstance(click_opacity, (int, float)):
                    self.opacity = click_opacity
                return True

        if self.right_click_enabled and player.right_clicked and self.rect.collidepoint(player.pos):
            if self.is_cooldownless(current_time, self.last_right_click_time):
                self.last_right_click_time = current_time
                if isinstance(click_opacity, (int, float)):
                    self.opacity = click_opacity
                return True
    
        return False
            
    def is_cooldownless(self, current_time: float | None = None, click_type_time: float | None = None) -> bool:
        if not current_time:
            current_time = time.time()

        if not click_type_time:
            return (current_time - self.last_left_click_time >= self.cooldown) and (current_time - self.last_right_click_time >= self.cooldown) 
        
        return current_time - click_type_time >= self.cooldown
