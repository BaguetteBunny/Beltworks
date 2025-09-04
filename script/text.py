import pygame as pg
import colorsys

import constants as C
from configs import RainbowConfig

class Text:
    def __init__(self,
                 text: str = 'Empty Text Layer',
                 font: pg.font.Font = C.FONTS["M"] ,
                 color: tuple[int, int, int] | RainbowConfig = (0, 0, 0),
                 pos: tuple[float, float] = (0.0, 0.0),
                 opacity: int = 255,
                 is_centered: bool = False,
                 is_bold: bool = False,
                 is_italic: bool = False,
                 is_underline: bool = False,
                 is_number_formatting: bool = False) -> None:
        
        self.text = text
        self.font = font
        self.color = color
        self.x = pos[0]*C.SCALE_X
        self.y = pos[1]*C.SCALE_Y
        self.opacity = opacity
        self.centered = is_centered
        self.bold = is_bold
        self.italic = is_italic
        self.underline = is_underline
        self.rendered_images = []
        
        pg.font.Font.set_bold(self.font, False)
        pg.font.Font.set_italic(self.font, False)
        pg.font.Font.set_underline(self.font, False)
        if self.bold: pg.font.Font.set_bold(font, True)
        if self.italic: pg.font.Font.set_italic(font, True)
        if self.underline: pg.font.Font.set_underline(font, True)
        if is_number_formatting: self.text = self.format_long_number()

        if not "\n" in self.text:
            self.rendered_images.append(self.render_text(self.text))
        else:
            for word in self.text.split('\n'):
                self.rendered_images.append(self.render_text(word))
        
    def draw(self, screen: pg.Surface, new_pos: tuple[float | int, float | int] | None = None) -> None:
        x, y = (new_pos[0], new_pos[1]) if new_pos else (self.x, self.y)

        for img in self.rendered_images:
            if isinstance(self.color, (tuple, list)):
                img: pg.Surface
                screen.blit(img, (img.get_rect(center=(x, y)) if self.centered else (x, y)))
                y += img.get_height()

            else:
                img: list[pg.Surface]
                x = new_pos[0] if new_pos else self.x
                if self.centered:
                    x -= (self.image.get_width() - img[0].get_width())/2

                for char in img:
                    char: pg.Surface
                    screen.blit(char, (char.get_rect(center=(x, y)) if self.centered else (x, y)))
                    x += char.get_width()

                y += img[0].get_height()

    def format_long_number(self) -> str:
        string_number = str(int(float(self.text)))
        format_list = ['k', 'M', 'B', 'T']
        
        number_length = len(string_number)
        number_magnitude = ((number_length-1)//3)-1
        return string_number if number_magnitude < 0 else string_number[:(3 if number_length%3==0 else number_length%3)] + (('.')+string_number[1] if number_length%4 == 0 else '') +f'{format_list[number_magnitude]}'
    
    def render_text(self, text: str) -> pg.Surface:
        if isinstance(self.color, RainbowConfig) and self.color.enabled:
            image_array = []
            rainbow_iter = self.rainbow_generator()
            for char in text:
                new_color = next(rainbow_iter)
                image = self.font.render(char, True, new_color)
                image.set_alpha(self.opacity)
                image_array.append(image)
            self.image = self.font.render(text, True, (0,0,0))
            return image_array
        
        else:
            self.image = self.font.render(text, True, self.color)
            self.image.set_alpha(self.opacity)
            return self.image
    
    def rainbow_generator(self):
        hue = 0
        while True:
            rainbow_colour = [int(c*255) for c in colorsys.hsv_to_rgb(hue / 360.0, 1, self.color.fixed_lightness / 100.0)]
            yield rainbow_colour
            hue = (hue + self.color.hue_step) % 360
