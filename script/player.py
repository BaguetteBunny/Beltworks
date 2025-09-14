import pygame as pg
from pathlib import Path
import json

import constants as C
from configs import State

class Player(pg.sprite.Sprite):
    def __build_item_image_dict(self, root_folder: str) -> dict:
        root = Path(root_folder)
        result = {}

        for category in root.iterdir():
            if category.is_dir():
                slots = {}

                for slot in category.iterdir():
                    if slot.is_dir():
                        images = [
                            str(file) for file in slot.iterdir()
                            if file.is_file() and file.suffix.lower() == ".png"
                        ]
                        slots[slot.name] = images

                result[category.name] = slots

        return result

    def __build_ingredients_json(self, root_folder: str, json_path: str) -> dict:
        root = Path(root_folder)
        result = {}

        for subfolder in root.iterdir():
            if subfolder.is_dir():
                files = {
                    str(file): 0
                    for file in subfolder.iterdir()
                    if file.is_file() and file.suffix.lower() == ".png"
                }
                if files:
                    result[subfolder.name] = files

        if Path(json_path).exists():
            with open(json_path, "r") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = {}
        else:
            existing = {}

        final_data = result if not existing else existing
        order = C.INGREDIENT_DISPLAY_ORDER
        ordered_data = {key: final_data[key] for key in order if key in final_data}

        for key in final_data:
            if key not in ordered_data:
                ordered_data[key] = final_data[key]

        with open(json_path, "w") as f:
            json.dump(ordered_data, f, indent=1)

        return ordered_data

    def __init__(self, preexisting_stats_path: str = C.PLAYER_JSON_PATH, menu_state: State = State.FACTORY) -> None:
        super().__init__()
        self.rect = pg.Rect(0, 0, 1, 1)
        self.pos = ()
        self.is_dragging = False
        self.path = preexisting_stats_path
        self.state = menu_state

        self.items = self.__build_item_image_dict(C.ASSETS_PATH + "items")
        self.ingredients = self.__build_ingredients_json(C.ASSETS_PATH + "ingredient", C.INGREDIENT_JSON_PATH)
        self.artifacts = json.loads(open(C.ARTIFACT_JSON_PATH).read())

        self.particles = []
        self.item_group = pg.sprite.Group()
        self.stored_ingredient_group = pg.sprite.Group()
        self.stored_artifact_group = pg.sprite.Group()

        data: dict = self.deserialize()[0]

        self.currency = data.get("currency")
        if not self.currency:
            self.currency = 0

        self.max_droprate = self.droprate = data.get("droprate")
        if not self.max_droprate:
            self.max_droprate = self.droprate = 300

        self.current_background = data.get("bg")
        if not self.current_background:
            self.current_background = "default"

        self.max_storage_page = data.get("storage")
        if not self.max_storage_page:
            self.max_storage_page = 1

        self.rarity_multiplier = data.get("rarity_multiplier")
        if not self.rarity_multiplier:
            self.rarity_multiplier = 1

        self.durability_multiplier = data.get("durability_multiplier")
        if not self.durability_multiplier:
            self.durability_multiplier = 1

        self.category_multiplier = data.get("category_multiplier")
        if not self.category_multiplier:
            self.category_multiplier = 1

        self.ingredient_multiplier = data.get("ingredient_multiplier")
        if not self.ingredient_multiplier:
            self.ingredient_multiplier = 1

        self.value_multiplier = data.get("value_multiplier")
        if not self.value_multiplier:
            self.value_multiplier = 1

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
    
    def do_drop_items(self) -> bool:
        self.droprate -= 1
        if self.droprate <= 0:
            self.droprate = self.max_droprate
            return True
        return False

    def serialize(self) -> dict:
        return {
            'currency': self.currency,
            'droprate': self.max_droprate,
            'bg': self.current_background,
            'storage': self.max_storage_page,
            'rarity_multiplier': self.rarity_multiplier,
            'durability_multiplier': self.durability_multiplier,
            'category_multiplier': self.category_multiplier,
            'ingredient_multiplier': self.ingredient_multiplier,
            'value_multiplier': self.value_multiplier,
        }
    
    def deserialize(self) -> dict:
        try:
            with open(f"{self.path}", "r") as f:
                return json.load(f)
        except:
            return {}