import pygame as pg
import random

import constants as C
from configs import Shapes

class Particle:
    def __init__(self,
                 shape: Shapes = Shapes.CIRCLE,
                 color: list[int, int, int, int] = [0, 0, 0, 255],
                 pos: tuple[float, float] = (0.0, 0.0),
                 size: float = 1.0,
                 velocity: tuple[float, float] = (0.0, 0.0),
                 gravity: float = 1,
                 timer: int = 3,
                 is_randomized: tuple[bool, bool] = (True, True),
                 is_decreasing_opacity: bool = True) -> None:
        
        self.shape = shape
        self.color = color
        self.max_opacity = self.color[3]
        self.size = size
        self.x, self.y = pos
        self.x_velocity, self.y_velocity = velocity
        self.has_random_x, self.has_random_y = is_randomized
        self.gravity = gravity
        self.max_timer = self.timer = timer*C.FPS
        self.decrease_opacity = is_decreasing_opacity
        
        self.x_velocity = self.set_random_velocity(self.has_random_x, self.x_velocity)
        self.y_velocity = self.set_random_velocity(self.has_random_y, self.y_velocity)

    def update_and_draw(self, screen: pg.Surface, particle_list: list) -> None:
        self.timer -= 1
        if self.timer <= 0:
            particle_list.remove(self)
            del self
            return
        
        self.x += self.x_velocity
        self.y += self.y_velocity + self.gravity

        self.x_velocity -= self.x_velocity/self.max_timer
        self.y_velocity -= self.y_velocity/self.max_timer

        if self.decrease_opacity:
            self.color[3] -= self.max_opacity/self.max_timer
        
        match self.shape:
            case Shapes.CIRCLE:
                if not self.decrease_opacity:
                    pg.draw.circle(screen, self.color, (self.x, self.y), self.size)
                else:
                    particle_surface = pg.Surface((self.size*2, self.size*2), pg.SRCALPHA)
                    pg.draw.circle(particle_surface, self.color, (self.size, self.size), self.size)
                    screen.blit(particle_surface, (self.x - self.size, self.y - self.size))

    def set_random_velocity(self, condition: bool, value: float) -> float:
        if condition:
            rand_val = random.random()
            value *= (rand_val**2 + rand_val) * (-1)**random.randint(1, 2)
        return value