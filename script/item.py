import pygame as pg
import random, os, json, math, time
from pathlib import Path

import constants as C
from configs import RainbowConfig, State
from text import Text
from player import Player

class Item(pg.sprite.Sprite):
    def __init__(self, item_dict: dict, preexisting_item: dict | None = None) -> None:
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
            
            if not isinstance(self.rarity['color'], list):
                self.rarity['color'] = RainbowConfig(True, self.rarity['color']['hue_step'], self.rarity['color']['fixed_lightness'])
            if not isinstance(self.durability['color'], list):
                self.durability['color'] = RainbowConfig(True, self.durability['color']['hue_step'], self.durability['color']['fixed_lightness'])
        else:
            category_picked = random.choice(self.select_category(random.randint(1,100_000_000)))
            self.path: str = random.choice(item_dict[category_picked])
            pure_path = Path(self.path)
            self.category = pure_path.parts[2]
            self.name = pure_path.parts[3].replace(".png", "").replace("_", " ").title()
            self.durability = self.select_durability(random.gauss(50, 15))
            self.rarity = self.select_rarity(random.randint(1,1_000_000_000))
            self.weight = 2.5
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

        # Text
        self.text = {
            'name': Text(text = f"{self.name}", font = C.FONTS["XS"], color = (255,255,255), pos = (self.x, self.y), is_centered = True, is_bold = True),
            'rarity' : Text(text = f"Rarity: {self.rarity['label'].title()}", font = C.FONTS["S"], color = self.rarity['color'], pos = (self.x, self.y), is_centered = True),
            'durability' : Text(text = f"Durability: {self.durability['label'].title()}", font = C.FONTS["S"], color = self.durability['color'], pos = (self.x, self.y), is_centered = True),
            'value' : Text(text = f"{self.value}", is_number_formatting = True)
        }
        self.text['labeled_value'] = Text(text = f"Value: {self.text['value'].text} ¤", font = C.FONTS["S"], color = (255,255,255), pos = (self.x, self.y), is_centered = True)

    def update(self,
               player: Player,
               group: pg.sprite.Group,
               collision_box: pg.Rect,
               sell_box: pg.Rect,
               storage_path: str = C.STORAGE_JSON_PATH) -> None:

        self.y += self.y_velocity
        self.x += self.x_velocity
        self.y_velocity += 0.5 * self.weight
        self.rect.topleft = (self.x, self.y)
        
        self.check_sell(sell_box, player, group)
        self.check_collision(collision_box, player, group)
        self.check_store_item(player, group, storage_path)

    def check_sell(self, sell_box: pg.Rect, player: Player, group: pg.sprite.Group) -> None:
        if self.rect.colliderect(sell_box):
            player.currency += self.value

            group.remove(self)
            del self

    def check_collision(self, collision_box: pg.Rect, player: Player, group: pg.sprite.Group) -> None:
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
        if (self.rect.colliderect(player.rect) and player.left_clicked and not player.is_dragging) or (self.dragged and player.left_clicked):
            self.dragged = True
            player.is_dragging = True

            target_x = player.pos[0] - self.rect.width / 2
            target_y = player.pos[1] - self.rect.height / 2

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
            item: Item
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

    def check_store_item(self, player: Player, group: pg.sprite.Group, storage_path: str) -> None:
        if self.dragged and player.right_clicked:
            if not os.path.exists(storage_path) or os.path.getsize(storage_path) == 0:
                data = []
            else:
                with open(storage_path, 'r') as file:
                    data = json.load(file)

            if len(data) < player.max_storage_page * 80:
                data.append(self.storage_serialize())
                with open(storage_path, 'w') as file:
                    json.dump(data, file, indent=1)
                group.remove(self)
                del self

    def draw(self, screen: pg.Surface, player: Player, gui: pg.Surface):
        rotated_image = pg.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect.topleft)

        if self.rect.colliderect(player.rect):
            centerx = self.rect.centerx - gui.get_width() // 2
            centery = self.rect.centery - gui.get_height() - 20*C.SCALE_Y
            screen.blit(gui, (centerx, centery))

            self.text['name'].draw(screen, new_pos = (self.rect.centerx, centery+389*C.SCALE_Y))
            self.text['rarity'].draw(screen, new_pos = (self.rect.centerx, centery+120*C.SCALE_Y))
            self.text['durability'].draw(screen, new_pos = (self.rect.centerx, centery+145*C.SCALE_Y))
            self.text['labeled_value'].draw(screen, new_pos = (self.rect.centerx, centery+170*C.SCALE_Y))

    def select_rarity(self, selector: float) -> dict:
        if selector == 1: return {'label': 'supreme', 'value': 1000000000, 'color': RainbowConfig(True)} # 1 in 1B
        elif selector <= 100: return {'label': 'mythic', 'value': 100000000, 'color': (212, 76, 115)} # 1 in 100M
        elif selector <= 1_000: return {'label': 'fabled', 'value': 10000000, 'color': (255, 5, 5)} # 1 in 10M
        elif selector <= 10_000: return {'label': 'legendary', 'value': 1000000, 'color': (240, 203, 58)} # 1 in 100K
        elif selector <= 100_000: return {'label': 'epic', 'value': 100000, 'color': (152, 47, 222)} # 1 in 10K
        elif selector <= 1_000_000: return {'label': 'rare', 'value': 10000, 'color': (56, 107, 194)} # 1 in 1K
        elif selector <= 10_000_000: return {'label': 'uncommon', 'value': 1000, 'color': (56, 194, 93)} # 1 in 100 
        else: return {'label': 'common', 'value': 10, 'color': (255,255,255)} # Guarenteed
    
    def select_durability(self, selector: float) -> dict:
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
        else: return {"label": "Perfect", 'multiplier': 1_000, 'color': RainbowConfig(True)}

    def select_category(self, selector: float) -> list:
        if selector == 1: return ["ingredients"] # 1 in 100M
        elif selector <= 10: return ["ingredients"] # 1 in 10M
        elif selector <= 100: return ["ingredients"]# 1 in 1M
        elif selector <= 1_000: return ["ingredients"] # 1 in 100K
        elif selector <= 10_000: return ["fossil", "onyx", "amethyst"] # 1 in 10K
        elif selector <= 150_150: return ["amber", "emerald", "jade", "silver", "sapphire"] # 1 in 666
        elif selector <= 5_000_000: return ["leather", "bronze"] # 1 in 20
        else: return ["ingredients"] # Guarenteed

    def serialize(self) -> dict:
        serialization = self.storage_serialize()
        serialization['x'] = self.x
        serialization['y'] = self.y
        serialization['angle'] = self.angle
        return serialization
    
    def storage_serialize(self) -> dict:
        rarity_color = vars(self.rarity["color"]) if isinstance(self.rarity['color'], RainbowConfig) else self.rarity['color']
        durability_color = vars(self.durability["color"]) if isinstance(self.durability['color'], RainbowConfig) else self.durability['color']

        return {
            'path': self.path,
            'name': self.name,
            'rarity': {
                'label': self.rarity['label'],
                'value': self.rarity['value'],
                'color': rarity_color,
            },
            'durability': {
                'label': self.durability['label'],
                'multiplier': self.durability['multiplier'],
                'color': durability_color,
            },
            'weight': self.weight,
            'mutations': self.mutations,
        }

    def __repr__(self) -> str:
        return f"Item: {self.name}, Rarity: {self.rarity['label'].title()}, Durability: {self.durability['label'].title()}, Weight: {self.weight}, Mutations: {self.mutations}"

class StorageItem(pg.sprite.Sprite):
    def __init__(self, stored_dict: dict, pos: tuple[float | int, float | int], current_time: time) -> None:
        pg.sprite.Sprite.__init__(self)

        self.path = stored_dict['path']
        self.name = stored_dict['name']
        self.rarity = stored_dict['rarity']
        self.durability = stored_dict['durability']
        self.weight = stored_dict['weight']
        self.mutations = stored_dict['mutations']
            
        if not isinstance(self.rarity['color'], list):
            self.rarity['color'] = RainbowConfig(True, self.rarity['color']['hue_step'], self.rarity['color']['fixed_lightness'])
        if not isinstance(self.durability['color'], list):
            self.durability['color'] = RainbowConfig(True, self.durability['color']['hue_step'], self.durability['color']['fixed_lightness'])

        self.old_mouse_pos = ()
        self.og_x, self.og_y = pos
        self.current_time = current_time
        self.x = pos[0] * C.SCALE_X
        self.y = pos[1] * C.SCALE_Y
        self.random_y_offset = math.pi * random.random() * (-1)**(random.randint(1,2))

        # Image
        self.image = pg.image.load(self.path).convert_alpha()
        self.image = pg.transform.smoothscale_by(self.image, C.SCALE_X*0.75)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.value = self.rarity["value"] * self.durability["multiplier"]

        # Text
        self.text = {
            'name': Text(text = f"{self.name}", font = C.FONTS["XS"], color = (255,255,255), pos = (self.x, self.y), is_centered = True, is_bold = True),
            'rarity' : Text(text = f"Rarity: {self.rarity['label'].title()}", font = C.FONTS["S"], color = self.rarity['color'], pos = (self.x, self.y), is_centered = True),
            'durability' : Text(text = f"Durability: {self.durability['label'].title()}", font = C.FONTS["S"], color = self.durability['color'], pos = (self.x, self.y), is_centered = True),
            'value' : Text(text = f"{self.value}", is_number_formatting = True)
        }
        self.text['labeled_value'] = Text(text = f"Value: {self.text['value'].text} ¤", font = C.FONTS["S"], color = (255,255,255), pos = (self.x, self.y), is_centered = True)
    
    def draw(self, screen: pg.Surface):
        self.random_y_offset = (self.random_y_offset+0.08) % (2*math.pi)
        new_y = self.y + 2*math.sin(self.random_y_offset)
        self.rect = self.image.get_rect(topleft=(self.x, new_y))
        screen.blit(self.image, self.rect)

    def update_and_draw_gui(self, screen: pg.Surface, player: Player, stored_item_list: list, gui: pg.Surface, json_path: str = C.STORAGE_JSON_PATH):
        if self.rect.colliderect(player.rect):
            centerx = self.rect.centerx - gui.get_width() // 2
            centery = self.rect.centery - gui.get_height() - 20*C.SCALE_Y
            if self.og_y == 304:
                centery += 450 * C.SCALE_Y
            screen.blit(gui, (centerx, centery))

            self.text['name'].draw(screen, new_pos = (self.rect.centerx, centery+389*C.SCALE_Y))
            self.text['rarity'].draw(screen, new_pos = (self.rect.centerx, centery+120*C.SCALE_Y))
            self.text['durability'].draw(screen, new_pos = (self.rect.centerx, centery+145*C.SCALE_Y))
            self.text['labeled_value'].draw(screen, new_pos = (self.rect.centerx, centery+170*C.SCALE_Y))

            if player.right_clicked and (time.time() - self.current_time >= 0.5):
                with open(json_path, "r") as f:
                    data = json.load(f)
                index_to_remove = int((10 * (self.og_y - 304) + (self.og_x - 224)) / 96)
                del data[index_to_remove]
                with open(json_path, "w") as f:
                    json.dump(data, f, indent=1)

                player.currency += self.value
                player.state = State.ITEM_STORAGE_REFRESH
                stored_item_list.remove(self)
                del self

    def __repr__(self) -> str:
        return f"Item: {self.name}, Rarity: {self.rarity['label'].title()}, Durability: {self.durability['label'].title()}, Weight: {self.weight}, Mutations: {self.mutations}"

class CraftableItem(pg.sprite.Sprite):
    def __init__(self, path: str, amount: int, pos: tuple[float | int, float | int]) -> None:
        pg.sprite.Sprite.__init__(self)

        self.path = path
        pure_path = Path(self.path)
        self.category = pure_path.parts[2].title()
        self.name = pure_path.parts[3].replace(".png", "").replace("_", " ").title()
        self.amount = amount

        self.old_mouse_pos = ()
        self.og_x, self.og_y = pos
        self.x = pos[0] * C.SCALE_X
        self.y = pos[1] * C.SCALE_Y
        self.random_y_offset = math.pi * random.random() * (-1)**(random.randint(1,2))

        # Image
        self.image = pg.image.load(self.path).convert_alpha()
        self.image = pg.transform.smoothscale_by(self.image, C.SCALE_X*0.75)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        # Text
        self.text = {
            'name': Text(text = f"{self.name}", font = C.FONTS["XS"], color = (255,255,255), pos = (self.x, self.y), is_centered = True, is_bold = True),
            'amount' : Text(text = f"{self.amount}", is_number_formatting = True)
        }
        self.text['labeled_amount'] = Text(text = f"Quantity: {self.text['amount'].text}", font = C.FONTS["S"], color = (255,255,255), pos = (self.x, self.y), is_centered = True)
    
    def draw(self, screen: pg.Surface):
        self.random_y_offset = (self.random_y_offset+0.08) % (2*math.pi)
        new_y = self.y + 2*math.sin(self.random_y_offset)
        self.rect = self.image.get_rect(topleft=(self.x, new_y))
        new_image = self.image if self.amount else pg.transform.grayscale(self.image)
        screen.blit(new_image, self.rect)

    def update_and_draw_gui(self, screen: pg.Surface, player: Player, gui: pg.Surface):
        if self.rect.colliderect(player.rect):
            centerx = self.rect.centerx - gui.get_width() // 2
            centery = self.rect.centery - gui.get_height() - 20*C.SCALE_Y
            if self.og_y == 304:
                centery += 450 * C.SCALE_Y
            screen.blit(gui, (centerx, centery))

            self.text['name'].draw(screen, new_pos = (self.rect.centerx, centery+389*C.SCALE_Y))
            self.text['labeled_amount'].draw(screen, new_pos = (self.rect.centerx, centery+120*C.SCALE_Y))

    def __repr__(self) -> str:
        return f"Item: {self.name}, Quantity: {self.amount}, Category: {self.category}"
