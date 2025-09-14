import pygame as pg
import random, math
from pathlib import Path

import constants as C
import recipe as R
from configs import RainbowConfig
from text import Text
from player import Player
from button import Button

class Item(pg.sprite.Sprite):
    def __init__(self, player: Player, item_dict: dict, preexisting_item: dict | None = None) -> None:
        pg.sprite.Sprite.__init__(self)

        self.player_multipliers = {
            "rarity": player.rarity_multiplier,
            "durability": player.durability_multiplier,
            "value": player.value_multiplier,
            "ingredient": player.ingredient_multiplier,
            "category": player.category_multiplier,
        }

        if preexisting_item:
            self.path = preexisting_item['path']
            self.name = preexisting_item['name']

            pure_path = Path(self.path)
            self.category = pure_path.parts[2]
            self.tier = int(pure_path.parts[3])

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
            self.category, self.tier = random.choice(self.select_category(random.randint(1,100_000_000)))
            # Failsafe
            while not item_dict[self.category][f"{self.tier}"]:
                self.category, self.tier = random.choice(self.select_category(random.randint(1,100_000_000)))
            
            self.path: str = random.choice(item_dict[self.category][f"{self.tier}"])
            pure_path = Path(self.path)
            
            self.name = pure_path.parts[4].replace(".png", "").replace("_", " ").title()
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

        # Value
        self.value = self.player_multipliers["value"] + (self.rarity["value"] * self.durability["multiplier"])

        # Text
        self.text = {
            'name': Text(text = f"{self.name}", font = C.FONTS["XS"], color = (255,255,255), pos = (self.x, self.y), is_centered = True, is_bold = True),
            'rarity' : Text(text = f"Rarity: {self.rarity['label'].title()}", font = C.FONTS["S"], color = self.rarity['color'], pos = (self.x, self.y), is_centered = True),
            'durability' : Text(text = f"Durability: {self.durability['label'].title()}", font = C.FONTS["S"], color = self.durability['color'], pos = (self.x, self.y), is_centered = True),
            'value' : Text(text = f"{self.value}", is_number_formatting = True)
        }
        self.text['labeled_value'] = Text(text = f"Value: {self.text['value'].text} ¤", font = C.FONTS["S"], color = (255,255,255), pos = (self.x, self.y), is_centered = True)

    def update(self, player: Player, collision_box: pg.Rect, sell_box: pg.Rect) -> None:
        self.y += self.y_velocity
        self.x += self.x_velocity
        self.y_velocity += 0.5 * self.weight
        self.rect.topleft = (self.x, self.y)
        
        self.check_sell(sell_box, player)
        self.check_collision(collision_box, player)

    def check_sell(self, sell_box: pg.Rect, player: Player) -> None:
        if self.rect.colliderect(sell_box):
            player.currency += self.value

            self.serialize_ingredient(player)

            player.item_group.remove(self)
            del self

    def check_collision(self, collision_box: pg.Rect, player: Player) -> None:
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

        for item in player.item_group:
            item: Item
            if item != self and self.rect.colliderect(item.rect):
                dx = self.rect.centerx - item.rect.centerx
                dy = self.rect.centery - item.rect.centery
                distance = math.hypot(dx, dy) or 1

                nx, ny = dx / distance, dy / distance

                bounce = 0.5/self.weight + 0.5*item.weight
                bounce *= 0.1 * (self.weight + item.weight) / distance
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

                self.angle += (self.x_velocity+self.y_velocity)/(3*self.weight)
                self.angle %= 360
                item.angle += (item.x_velocity+item.y_velocity)/(3*item.weight)
                item.angle %= 360

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
        if selector == 1: return {'label': 'supreme', 'value': 10_000, 'color': RainbowConfig(True)} # 1 in 1B
        elif selector <= 100: return {'label': 'mythic', 'value': 5_000, 'color': (212, 76, 115)} # 1 in 100M
        elif selector <= 1_000: return {'label': 'fabled', 'value': 1_000, 'color': (255, 5, 5)} # 1 in 10M
        elif selector <= 10_000: return {'label': 'legendary', 'value': 500, 'color': (240, 203, 58)} # 1 in 100K
        elif selector <= 100_000: return {'label': 'epic', 'value': 100, 'color': (152, 47, 222)} # 1 in 10K
        elif selector <= 1_000_000: return {'label': 'rare', 'value': 50, 'color': (56, 107, 194)} # 1 in 1K
        elif selector <= 10_000_000: return {'label': 'uncommon', 'value': 10, 'color': (56, 194, 93)} # 1 in 100 
        else: return {'label': 'common', 'value': 1, 'color': (255,255,255)} # Guarenteed
    
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

    def select_category(self, selector: float) -> list[tuple[str, int]]:
        if selector == 1: # 1 in 100M
            return [("ingredients", 5), ("onyx", 5), ("amethyst", 5)]
        
        elif selector <= 10: # 1 in 10M
            return [("amber", 5), ("emerald", 5), ("sapphire", 5), ("fossil", 5), ("onyx", 4), ("amethyst", 4)]
        
        elif selector <= 100: # 1 in 1M
            return [("ingredients", 4), ("leather", 5), ("bronze", 5), ("silver", 5), ("amber", 4), ("emerald", 4), ("sapphire", 4), ("fossil", 4), ("onyx", 3), ("amethyst", 3)]
        
        elif selector <= 1_000: # 1 in 100K
            return [("leather", 4), ("bronze", 4), ("silver", 4), ("amber", 3), ("emerald", 3), ("sapphire", 3), ("fossil", 3), ("onyx", 2), ("amethyst", 2)]
        
        elif selector <= 10_000: # 1 in 10K
            return [("ingredients", 3), ("leather", 3), ("bronze", 3), ("silver", 3), ("amber", 2), ("emerald", 2), ("sapphire", 2), ("fossil", 2), ("onyx", 1), ("amethyst", 1)]
        
        elif selector <= 150_150: # 1 in 666
            return [("leather", 2), ("bronze", 2), ("silver", 2), ("amber", 1), ("emerald", 1), ("sapphire", 1), ("fossil", 1)]
        
        elif selector <= 50_000_000: # 1 in 20
            return [("ingredients", 2), ("leather", 1), ("bronze", 1), ("silver", 1)]
        
        else: # Guarenteed
            return [("trash", 1), ("ingredients", 1)]

    def serialize(self) -> dict:
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
            'x': self.x,
            'y': self.y,
            'angle': self.angle
        }

    def serialize_ingredient(self, player: Player, json_path: str = C.INGREDIENT_JSON_PATH):
        if self.category in {"ingredients", "trash", "fossil", "leather"}:
            return
        
        # Generate random quantity
        T = self.tier + 1
        bias = random.random() ** 5
        hard_min = T * 2 - 3    # 1     3       5       7       9
        hard_max = T ** 3       # 8     27      64      125     216
        quantity = int(bias * (hard_max - hard_min)) + 1

        # Generate random tier
        id_tier = T
        for _ in range(5): id_tier -= random.random()
        id_tier = int(id_tier)

        # Generate random ingredient
        if self.category in {"bronze", "silver", "gold", "amber", "emerald", "sapphire", "onyx", "amethyst"}:
            if id_tier <= 0:
                image_name = "raw_" + self.category + "_ore"
                category = "raw_ore"
            elif id_tier == 1:
                image_name = self.category + "_powder"
                category = "powder"
            elif id_tier == 2:
                image_name = self.category + "_gemstone"
                category = "gemstone"
            elif id_tier == 3:
                image_name = "refined_" + self.category + "_gemstone"
                category = "gemstone"
            else:
                raise ValueError("How the fuck did this even happen? @ gemstone -> serialize_ingredient")
            
        player.ingredients[category][f"assets\\ingredient\\{category}\\{image_name}.png"] += quantity
        
    def __repr__(self) -> str:
        return f"Item: {self.name}, Rarity: {self.rarity['label'].title()}, Durability: {self.durability['label'].title()}, Weight: {self.weight}, Mutations: {self.mutations}"

class IngredientItem(pg.sprite.Sprite):
    def __init__(self, path: str, amount: int, pos: tuple[float | int, float | int]) -> None:
        pg.sprite.Sprite.__init__(self)

        self.path = path
        pure_path = Path(self.path)
        self.category = pure_path.parts[2]
        self.id = pure_path.parts[3].replace(".png", "")
        self.name = self.id.replace("_", " ").title()
        self.amount = amount

        self.old_mouse_pos = ()
        self.og_x, self.og_y = pos
        self.x = pos[0] * C.SCALE_X
        self.y = pos[1] * C.SCALE_Y
        self.random_y_offset = math.pi * random.random() * (-1)**(random.randint(1,2))

        # Recipe
        try: probable_recipes = R.INGREDIENT_RECIPE_FETCHER[self.category]
        except: self.recipe = None
        else: self.recipe = CraftableComponent(probable_recipes[self.id], self.path) if self.id in probable_recipes.keys() else None
        self.display_recipe = False

        # Image
        self.image = pg.image.load(self.path).convert_alpha()
        self.image = pg.transform.smoothscale_by(self.image, C.SCALE_X*0.75)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        # Text
        self.text = {
            'name': Text(text = f"{self.name}", font = C.FONTS["XS"], color = (255,255,255), pos = (self.x, self.y), is_centered = True, is_bold = True),
            'amount': Text(text = f"{self.amount}", is_number_formatting = True)
        }
        self.text['labeled_amount'] = Text(text = f"Quantity: {self.text['amount'].text}", font = C.FONTS["S"], color = (255,255,255), pos = (self.x, self.y), is_centered = True)
    
    def draw(self, screen: pg.Surface):
        self.random_y_offset = (self.random_y_offset+0.08) % (2*math.pi)
        new_y = self.y + 2*math.sin(self.random_y_offset)
        self.rect = self.image.get_rect(topleft=(self.x, new_y))

        if self.amount:
            new_image = self.image
        else:
            new_image = pg.transform.grayscale(self.image)
            new_image.set_alpha(120)
        screen.blit(new_image, self.rect)

    def update_and_draw_gui(self, screen: pg.Surface, player: Player, gui: pg.Surface):
        if self.display_recipe and self.recipe:
            self.recipe.display(screen = screen, player = player)

        if self.rect.colliderect(player.rect):
            centerx = self.rect.centerx - gui.get_width() // 2
            centery = self.rect.centery - gui.get_height() - 20*C.SCALE_Y
            if self.og_y == 304:
                centery += 450 * C.SCALE_Y
            screen.blit(gui, (centerx, centery))

            self.text['name'].draw(screen, new_pos = (self.rect.centerx, centery+389*C.SCALE_Y))
            self.text['labeled_amount'].draw(screen, new_pos = (self.rect.centerx, centery+120*C.SCALE_Y))

        if player.left_clicked:
            self.display_recipe = False
            if self.rect.colliderect(player.rect):
                self.display_recipe = not self.display_recipe

    def __repr__(self) -> str:
        return f"Item: {self.name}, Quantity: {self.amount}, Category: {self.category.title()}"

class ArtifactItem(pg.sprite.Sprite):
    def __init__(self, path: str, owned: bool, description: str, pos: tuple[float | int, float | int]) -> None:
        pg.sprite.Sprite.__init__(self)

        self.path = path
        pure_path = Path(self.path)
        self.category = pure_path.parts[2].title()
        self.name = pure_path.parts[3].replace(".png", "").replace("_", " ").title()
        self.owned = owned
        self.description = description if self.owned else "? ? ?"

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
            'description' : Text(text = f"{self.description}", font = C.FONTS["S"], color = (255,255,255), pos = (self.x, self.y), is_centered = True)
        }
    
    def draw(self, screen: pg.Surface):
        self.random_y_offset = (self.random_y_offset+0.08) % (2*math.pi)
        new_y = self.y + 2*math.sin(self.random_y_offset)
        self.rect = self.image.get_rect(topleft=(self.x, new_y))
        new_image = self.image if self.owned else pg.transform.grayscale(self.image)
        screen.blit(new_image, self.rect)

    def update_and_draw_gui(self, screen: pg.Surface, player: Player, gui: pg.Surface):
        if self.rect.colliderect(player.rect):
            centerx = self.rect.centerx - gui.get_width() // 2
            centery = self.rect.centery - gui.get_height() - 20*C.SCALE_Y
            if self.og_y == 304:
                centery += 450 * C.SCALE_Y
            screen.blit(gui, (centerx, centery))

            self.text['name'].draw(screen, new_pos = (self.rect.centerx, centery+389*C.SCALE_Y))
            self.text['description'].draw(screen, new_pos = (self.rect.centerx, centery+120*C.SCALE_Y))

    def __repr__(self) -> str:
        return f"Item: {self.name}, Owned: {self.owned}, Category: {self.category}"

class CraftableComponent:
    def __init__(self, image_name_input: list[tuple[str, str, int]], image_name_output: str):
        self.criteria_unmet_text = Text(text = f"Not enough materials!", font = C.FONTS["S"], color = (255,255,255), pos = (0, 0), is_centered = True)
        self.output_path = image_name_output
        self.output_button = Button(image = pg.transform.smoothscale_by(pg.image.load(self.output_path).convert_alpha(), C.SCALE_X), pos = (1024 * C.SCALE_X, 56 * C.SCALE_Y))

        OUTPUT_PUREPATH = Path(self.output_path).parts
        self.output_type = OUTPUT_PUREPATH[1]
        self.output_category = OUTPUT_PUREPATH[2]

        self.inputs: list[dict] = []
        for input in image_name_input:
            if not input:
                continue

            input_dictionary = {
                "id": input[0],
                "quantity": input[2],
                "formated_quantity": Text(text = f"{input[2]}", is_number_formatting = True)
            }
            input_dictionary["path"] = f"assets/{self.output_type}/{input[1]}/{input_dictionary['id']}.png"
            input_dictionary["image"] = pg.image.load(input_dictionary["path"]).convert_alpha()
            input_dictionary["labeled_quantity"] = Text(text = f"x {input_dictionary['formated_quantity'].text}", font = C.FONTS["S"], color = (255,255,255), pos = (0, 0), is_centered = True)

            self.inputs.append(input_dictionary)

    def display(self, screen: pg.Surface, player: Player):
        y = 88 * C.SCALE_Y
        label_y = 132 * C.SCALE_Y

        craft_slot_x = 416 * C.SCALE_X
        gap_between_slot = 196*C.SCALE_X
        for input in self.inputs:
            input_image = pg.transform.smoothscale_by(input['image'], C.SCALE_X*0.75)
            input_rect = input_image.get_rect(center=(craft_slot_x, y))
            screen.blit(input_image, input_rect)

            input['labeled_quantity'].draw(screen, new_pos = (craft_slot_x, label_y))
            
            craft_slot_x += gap_between_slot

        self.output_button.draw(screen = screen)
        if self.output_button.clicked(player = player, click_opacity = 125):
            if self.has_requirements():
                ...

    def has_requirements(self) -> bool:
        for input in self.inputs: ... 


        return True


        

        

