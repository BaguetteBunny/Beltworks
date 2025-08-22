import pygame as pg
import constants as C
import random, math, colorsys, os, json, time

# Text
def blit_text(img, x, y, centered, split=False, noblit = False):
    word_width, word_height = img.get_size()
    if not noblit:
        screen.blit(img, (img.get_rect(center=(x,y)) if centered else (x,y)))
    else:
        return (img, (img.get_rect(center=(x,y)) if centered else (x,y)))
    return (y+word_height+5 if split else y)
def draw_text(text, font, text_col, x, y, centered=False, linebreak = False, noblit = False, opacity=None, underline=False, bold=False, italic=False, rainbow_time_offset=0):
    pg.font.Font.set_underline(font, False)
    pg.font.Font.set_bold(font, False)
    pg.font.Font.set_italic(font, False)
    if underline:
        pg.font.Font.set_underline(font, True)
    if bold:
        pg.font.Font.set_bold(font, True)
    if italic:
        pg.font.Font.set_italic(font, True)
    if text_col == 'RAINBOW' and rainbow_time_offset:
        return draw_rainbow_text(text, font, x, y, centered, linebreak, noblit, opacity, rainbow_time_offset)
    if not linebreak and '\n' not in text:
        img = font.render(text, True, text_col)
        if opacity:
            img.set_alpha(opacity)
        bliting = blit_text(img, x, y, centered, noblit=noblit)
        if bliting:
            return bliting

    elif '\n' in text:
        for word in text.split('\n'):
            img = font.render(word, True, text_col)
            y = blit_text(img, x, y, centered, split = True)

    elif linebreak:
        next_word = ''
        for word in text.split():
            if len(word) <= 3:
                next_word = f'{word} '
            else:
                word = next_word + word
                img = font.render(word, True, text_col)
                y = blit_text(img, x, y, centered, split = True)
def draw_rainbow_text(text, font, x, y, centered=False, linebreak=False, noblit=False, opacity=None, time_offset=0):
    """
    Renders text with a rainbow animation effect.
    Each character's hue is slightly shifted, and the colors transition over time.
    """
    hue_shift = 10  # Hue shift between characters
    speed = 0.5     # Speed of hue transition
    lightness = 80  # Fixed lightness value for HSL

    images = []
    total_width = 0

    for i, char in enumerate(text):
        hue = (time_offset * speed + i * hue_shift) % 360
        r, g, b = [int(c * 255) for c in colorsys.hls_to_rgb(hue / 360, lightness / 100, 1)]
        color = (r, g, b)

        img = font.render(char, True, color)
        if opacity:
            img.set_alpha(opacity)
        images.append(img)
        total_width += img.get_width()

    if centered:
        x -= total_width // 2

    for img in images:
        blit_text(img, x, y=y-10*C.SCALE_Y, centered=False, noblit=noblit)
        x += img.get_width()

    return y + images[0].get_height() + 5 if linebreak else y
def format_long_number(number: int):
    string_number = str(number)
    format_list = ['k', 'M', 'B', 'T']

    number_length = len(str(number))
    number_magnitude = ((number_length-1)//3)-1

    return string_number if number_magnitude < 0 else string_number[:(3 if number_length%3==0 else number_length%3)] + (('.')+string_number[1] if number_length%4 == 0 else '') +f'{format_list[number_magnitude]}'


pg.init()
clock = pg.time.Clock()

largest_size = pg.display.list_modes()[0]
screen = pg.display.set_mode(largest_size, pg.FULLSCREEN | pg.HWACCEL | pg.HWSURFACE)
pg.display.set_caption("Testing")

# Assets
ASSETS_PATH = "assets/"
MENU_PATH = ASSETS_PATH + "menu/"
FONTS_PATH = ASSETS_PATH + "fonts/"
BACKGROUNDS_PATH = ASSETS_PATH + "backgrounds/"

GUI = {
    'item_menu': pg.transform.smoothscale_by(pg.image.load(MENU_PATH + "Item_Menu.png").convert_alpha(), C.SCALE_X*1.5),
}
ITEMS = {
    "common": [],
    "uncommon": [],
    "rare": [],
    "epic": [],
    "legendary": [],
    "fabled": [],
    "mythic": [],
    "supreme": [],
}

# Dynamically populate the "common" list with items from the assets/items/common folder
ITEMS["common"] = [
    item for item in os.listdir("assets/items/common")
    if item.endswith(".png") and not item.startswith("z")
]
FONTS = {
    "tiny": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 15),
    "small": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 20),
    "medium": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 30),
}
BACKGROUNDS = {
    "ocean_1": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "ocean_1.png").convert_alpha(), C.SCALE_X), (250,250)],
    "island_1": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "island_1.png").convert_alpha(), C.SCALE_X), (250,250)],
    "island_2": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "island_2.png").convert_alpha(), C.SCALE_X), (250,250)],
    "island_3": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "island_3.png").convert_alpha(), C.SCALE_X), (250,250)],
    "cloud_1": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "cloud_1.png").convert_alpha(), C.SCALE_X), (250,250)],
    "cloud_2": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "cloud_2.png").convert_alpha(), C.SCALE_X), (250,250)],
    "cloud_3": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "cloud_3.png").convert_alpha(), C.SCALE_X), (250,250)],
}

class Factory():
    def __init__(self):
        self.background = pg.Surface(screen.get_size())
        self.background.fill((0, 0, 0))
        self.background.set_alpha(0)
        self.background.convert()

        self.animation_cooldown = 0
        
        self.spritesheet = pg.image.load("assets/menu/Factory.png").convert_alpha()
        self.animation_list = []
        for frame in range(4):
            current_frame = pg.transform.smoothscale_by(self.spritesheet.subsurface(frame*1920, 0, 1920, 1080), C.SCALE_X)
            self.animation_list.append(current_frame)
        self.current_frame = 0
        self.image = self.animation_list[self.current_frame]

    def update(self):
        self.animation_cooldown = (self.animation_cooldown+1)%6
        if not self.animation_cooldown:
            self.update_animation()


    def update_animation(self):
        self.current_frame = (self.current_frame+1)%len(self.animation_list)
        self.image = self.animation_list[self.current_frame]

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        surface.blit(self.image, (0,0))

class Item(pg.sprite.Sprite):
    def __init__(self, asset_paths, preexisting_item=None):
        pg.sprite.Sprite.__init__(self)
        if preexisting_item:
            self.path = preexisting_item['path']
            self.name = preexisting_item['name']
            self.rarity = preexisting_item['rarity']
            self.durability = preexisting_item['durability']
            self.weight = preexisting_item['weight']
            self.mutations = preexisting_item['mutations']
            self.x = preexisting_item['x']
            self.y = preexisting_item['y']
            self.angle = preexisting_item['angle']
        else:
            self.rarity = self.select_rarity(random.randint(1,1_000_000_000))
            item_picked = random.choice(asset_paths[self.rarity['label']])
            self.path = "assets/items/" + self.rarity['label'] + "/" + item_picked
            self.name = item_picked.replace(".png", "").replace("_", " ").title()
            self.durability = self.select_durability(random.gauss(50, 15))
            self.weight = (1+random.random())*random.randint(1,2)
            self.mutations = []
            
            # Motion
            self.x = 100*C.SCALE_X
            self.y = -100*C.SCALE_Y
            self.angle = 0


        self.dragged = False
        self.old_mouse_pos = ()
        self.y_velocity = 0
        self.x_velocity = 0
        self.rotation_speed = (1/self.weight)*60

        # Image
        self.image = pg.image.load(self.path).convert_alpha()
        self.image = pg.transform.smoothscale_by(self.image, C.SCALE_X*0.75)
        self.rect = self.image.get_rect(topleft=(100*C.SCALE_X, -100))

        self.value = self.rarity["value"] * self.durability["multiplier"]

        self.rainbow_offset = 1 if self.rarity["color"] == "RAINBOW" or self.durability["color"] == "RAINBOW" else 0

    def update(self, collision_box, mouse, group):
        self.y += self.y_velocity
        self.x += self.x_velocity
        self.y_velocity += 0.5 * self.weight
        self.rect.topleft = (self.x, self.y)
        
        self.check_collision(collision_box, mouse, group)

    def check_collision(self, collision_box, mouse, group):
        # Check for window collision
        if self.x < 0:
            self.x = 0
            self.x_velocity *= -0.7/self.weight
        elif self.x + self.rect.width > 1340*C.SCALE_X:
            self.x = 1340*C.SCALE_X - self.rect.width
            self.x_velocity *= -0.7/self.weight

        # Check for ground collision
        if self.rect.colliderect(collision_box):
            self.y = collision_box.top - self.rect.height
            self.rect.topleft = (self.x, self.y)

            if self.y_velocity < 2.1*self.weight:
                self.y_velocity = 0
            else:
                self.y_velocity *= -0.7/self.weight
                self.angle += self.rotation_speed
                self.angle %= 360

            self.x_velocity = 4/self.weight

        # Check for mouse collision
        if (self.rect.colliderect(mouse.rect) and mouse.left_clicked and not mouse.is_dragging) or (self.dragged and mouse.left_clicked):
            self.dragged = True
            mouse.is_dragging = True

            target_x = mouse.pos[0] - self.rect.width / 2
            target_y = mouse.pos[1] - self.rect.height / 2

            # Spring Force
            spring_strength = 0.3
            self.x_velocity += (target_x - self.x) * spring_strength
            self.y_velocity += (target_y - self.y) * spring_strength

            # Friction
            self.x_velocity *= 0.85/self.weight
            self.y_velocity *= 0.85/self.weight

            # Rotation
            self.angle += (self.x_velocity+self.y_velocity)/(1.5*self.weight)
            self.angle %= 360
        else:
            self.dragged = False

        for item in group:
            if item != self and self.rect.colliderect(item.rect):
                dx = self.rect.centerx - item.rect.centerx
                dy = self.rect.centery - item.rect.centery
                distance = math.hypot(dx, dy) or 1

                nx, ny = dx / distance, dy / distance

                bounce = 0.5/self.weight + 0.5*item.weight
                bounce *= 0.5 * (self.weight + item.weight) / distance
                bounce = max(bounce, 0.1)

                self.x_velocity += nx * bounce
                self.y_velocity += ny * bounce
                item.x_velocity -= nx * bounce
                item.y_velocity -= ny * bounce

                overlap = (self.rect.width + item.rect.width) / 2 - distance
                separation = overlap / 2
                self.x += nx * separation
                self.y += ny * separation
                item.x -= nx * separation
                item.y -= ny * separation

                self.angle += (self.x_velocity+self.y_velocity)/(1.5*self.weight)
                self.angle %= 360
                item.angle += (item.x_velocity+item.y_velocity)/(1.5*item.weight)
                item.angle %= 360

    def draw(self, screen, gui):
        rotated_image = pg.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect.topleft)

        if self.dragged:
            centerx = self.rect.centerx - gui.get_width() // 2
            centery = self.rect.centery - gui.get_height() - 20*C.SCALE_Y
            screen.blit(gui, (centerx, centery))

            self.rainbow_offset = 10+(self.rainbow_offset)%3600 if self.rainbow_offset else 0
            draw_text(f"{self.name}", FONTS["tiny"], (255, 255, 255), self.rect.centerx,centery+389*C.SCALE_Y, centered=True, bold=True, underline=False)
            draw_text(f"Rarity: {self.rarity['label'].title()}", FONTS["small"], self.rarity['color'], self.rect.centerx, centery+120*C.SCALE_Y, centered=True, rainbow_time_offset=self.rainbow_offset)
            draw_text(f"Durability: {self.durability['label'].title()}", FONTS["small"], self.durability['color'], self.rect.centerx, centery+145*C.SCALE_Y, centered=True, rainbow_time_offset=self.rainbow_offset)
            draw_text(f"Value: {format_long_number(self.value)} ¤", FONTS["small"], (255, 255, 255), self.rect.centerx, centery+170*C.SCALE_Y, centered=True)

    def select_rarity(self, selector):
        if selector == 1: return {'label': 'supreme', 'value': 1000000000, 'color': 'RAINBOW'} # 1 in 1B
        elif selector <= 100: return {'label': 'mythic', 'value': 100000000, 'color': (212, 76, 115)} # 1 in 10M
        elif selector <= 1_000: return {'label': 'fabled', 'value': 10000000, 'color': (255, 5, 5)} # 1 in 100M
        elif selector <= 10_000: return {'label': 'legendary', 'value': 1000000, 'color': (240, 203, 58)} # 1 in 100K
        elif selector <= 100_000: return {'label': 'epic', 'value': 100000, 'color': (152, 47, 222)} # 1 in 10K
        elif selector <= 1_000_000: return {'label': 'rare', 'value': 10000, 'color': (56, 107, 194)} # 1 in 1K
        elif selector <= 10_000_000: return {'label': 'uncommon', 'value': 1000, 'color': (56, 194, 93)} # 1 in 100 
        else: return {'label': 'common', 'value': 10, 'color': (255,255,255)} # Guarenteed
    
    def select_durability(self, selector):
        if selector <= 1: return {'label': "Cursed", 'multiplier': 0, 'color': (31, 9, 10)}
        elif selector <= 10: return {'label': "Shattered", 'multiplier': 0.1, 'color': (89, 12, 16)}
        elif selector <= 20: return {'label': "Broken", 'multiplier': 0.25, 'color': (130, 23, 29)}
        elif selector <= 35: return {'label': "Damaged", 'multiplier': 0.5, 'color': (207, 54, 62)}
        elif selector <= 45: return {'label': "Bad", 'multiplier': 0.75, 'color': (247, 171, 175)}
        elif selector <= 55: return {"label": "Average", 'multiplier': 1, 'color': (255, 255, 255)}
        elif selector <= 65: return {"label": "Decent", 'multiplier': 2, 'color': (187, 250, 202)}
        elif selector <= 75: return {"label": "Good", 'multiplier': 5, 'color': (128, 255, 158)}
        elif selector <= 85: return {"label": "Great", 'multiplier': 10, 'color': (24, 219, 112)}
        elif selector <= 95: return {"label": "Pristine", 'multiplier': 25, 'color': (93, 224, 49)}
        elif selector <= 99: return {"label": "Divine", 'multiplier': 50, 'color': (106, 255, 0)}
        else: return {"label": "Perfect", 'multiplier': 1_000, 'color': 'RAINBOW'}

    def serialize(self):
        return {
            'path': self.path,
            'name': self.name,
            'rarity': self.rarity,
            'durability': self.durability,
            'weight': self.weight,
            'mutations': self.mutations,
            'x': self.x,
            'y': self.y,
            'angle': self.angle
        },

    def __str__(self):
        return f"Item: {self.name}, Rarity: {self.rarity['label'].title()}, Durability: {self.durability_label}, Weight: {self.weight}, Mutations: {self.mutations}"

class Background():
    def __init__(self, data):
        self.image = data[0]
        self.x = -data[1][0]*C.SCALE_X
        self.y = -data[1][1]*C.SCALE_Y
        self.rect = self.image.get_rect(topleft=(self.x,self.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Mouse(pg.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.rect = pg.Rect(0, 0, 1, 1)
        self.pos = ()
        self.is_dragging = False

    def update(self) -> None:
        self.rect.topleft = self.pos = pg.mouse.get_pos()
        buttons = pg.mouse.get_pressed()
        self.left_clicked = buttons[0]
        self.right_clicked = buttons[2]
        self.middle_clicked = buttons[1]
        self.wheel_up = pg.mouse.get_rel()[1] < 0
        self.wheel_down = pg.mouse.get_rel()[1] > 0

        if not self.left_clicked and self.is_dragging:
            self.is_dragging = False

class Button():
    def __init__(self, x, y, image, cd=0.33, right_click=False, animated: tuple = (), opacity = None):
        self.image = image
        self.pos = (x,y)
        self.animated = None
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

        self.opacity = opacity
        self.hover = 1
        self.cooldown = cd  # Cooldown in seconds
        self.right_click_enabled = right_click
        self.last_left_click_time = 0
        self.last_right_click_time = 0
        self.clicked = False

        if animated:
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


    def draw(self, screen, mouse, rescale = None, opacity = None, rotation = None, hover = None):
        # Button Animation
        if self.animated:
            self.image = self.animation_list[self.frame]
            if pg.time.get_ticks() - self.current_frame >= self.animated_cd:
                self.frame = (self.frame+1)%self.animated_frames
                self.current_frame = pg.time.get_ticks()

        # Dynamic Button Rescaling
        if rescale:
            self.image = pg.transform.smoothscale_by(self.image, rescale)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
        self.opacity = opacity if opacity else self.opacity

        # Dynamic Button Opacity
        if self.opacity:
            self.image.set_alpha(self.opacity)

        # Dynamic Button Rotation
        if rotation:
            self.image = pg.transform.rotate(self.image, rotation)

        # Button Hover Animation
        

        # Button Draw
        screen.blit(self.image, self.rect)

    def check_click(self, mouse):
        current_time = time.time()
        self.clicked = False
        
        if mouse.left_clicked and not mouse.right_clicked and self.rect.collidepoint(mouse.pos):
            if current_time - self.last_left_click_time >= self.cooldown:
                self.last_left_click_time = current_time
                self.clicked = True

        if self.right_click_enabled and mouse.right_clicked and self.rect.collidepoint(mouse.pos):
            if current_time - self.last_right_click_time >= self.cooldown:
                self.last_right_click_time = current_time
                self.clicked = True

button_1 = Button(200, 200, pg.image.load(MENU_PATH + "Achievement.png").convert_alpha())

mouse = Mouse()
factory = Factory()
collision_box = pg.Rect(0, 850*C.SCALE_X, 1920*C.SCALE_X, 100*C.SCALE_Y)

item_group = pg.sprite.Group()
if os.path.getsize('factory_items.json') > 0:
    for item in json.loads(open('factory_items.json').read()):
        item_group.add(Item(ITEMS, item[0]))

background = Background(BACKGROUNDS[random.choice(list(BACKGROUNDS.keys()))])

# Loop
while True:
    pg.display.flip()
    clock.tick(60)

    # Update ---------------------------------------------------------------------------------------------
    pg.display.update()
    mouse.update()
    item_group.update(collision_box, mouse, item_group)
    factory.update()

    # Draw -----------------------------------------------------------------------------------------------
    screen.fill((0, 0, 0))
    background.draw(screen)
    for item in item_group:
        item.draw(screen, GUI["item_menu"])
    factory.draw(screen)
    button_1.draw(screen, mouse, hover = 0.8)

    # Event Handling -------------------------------------------------------------------------------------
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            ...

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                item_group.add(Item(ITEMS))

        if event.type == pg.QUIT:
            open('factory_items', 'w').close()
            with open('factory_items.json', 'w') as file:
                    json.dump([item.serialize() for item in item_group], file, indent=1)
            pg.quit()
            exit()