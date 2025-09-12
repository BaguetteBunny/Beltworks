import pygame as pg
import os, json
from pathlib import Path

pg.init()
largest_size = pg.display.list_modes()[0]
SCREEN = pg.display.set_mode(largest_size, pg.FULLSCREEN | pg.HWACCEL | pg.HWSURFACE)

import constants as C
from configs import State
from item import Item, IngredientItem, ArtifactItem
from text import Text
from player import Player
from menu import Factory, Background, SellBox, Storage
from button import Button
from particle import Particle

clock = pg.time.Clock()
pg.display.set_caption(f"Boltworks | {C.VERSION}")

# Functions
def build_item_image_dict(root_folder: str) -> dict:
    root = Path(root_folder)
    result = {}

    for category in root.iterdir():
        if category.is_dir():
            slots = {}

            for slot in category.iterdir():
                if slot.is_dir():
                    images = [
                        str(file) for file in slot.iterdir()
                        if file.is_file() and file.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
                    ]
                    slots[slot.name] = images

            result[category.name] = slots

    return result

def build_ingredients_json(root_folder: str, json_path: str) -> dict:
    root = Path(root_folder)
    result = {}

    for subfolder in root.iterdir():
        if subfolder.is_dir():
            files = {
                str(file): 0
                for file in subfolder.iterdir()
                if file.is_file() and file.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
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
    order = ["raw_ore", "powder", "gemstone", "ruby", "aventurine", "aquamarine", "jasper"]
    ordered_data = {key: final_data[key] for key in order if key in final_data}

    for key in final_data:
        if key not in ordered_data:
            ordered_data[key] = final_data[key]

    with open(json_path, "w") as f:
        json.dump(ordered_data, f, indent=1)

    return ordered_data

ITEMS = build_item_image_dict(C.ASSETS_PATH + "items")
INGREDIENTS = build_ingredients_json(C.ASSETS_PATH + "ingredient", C.INGREDIENT_JSON_PATH)
ARTIFACTS = json.loads(open(C.ARTIFACT_JSON_PATH).read())

player = Player()
factory = Factory(screen = SCREEN)
factory_background = Background(C.BACKGROUNDS[player.current_background])
storage_background = Storage()

artifact_storage_button = Button(image = pg.image.load(C.BUTTON_PATH + "Artifacts.png").convert_alpha(), pos = (1450*C.SCALE_X, 350*C.SCALE_Y))
ingredient_storage_button = Button(image = pg.image.load(C.BUTTON_PATH + "Ingredients.png").convert_alpha(), pos = (1450*C.SCALE_X, 475*C.SCALE_Y))
shop_button = Button(image = pg.image.load(C.BUTTON_PATH + "Shop.png").convert_alpha(), pos = (1605*C.SCALE_X, 350*C.SCALE_Y))
factory_button = Button(image = pg.image.load(C.BUTTON_PATH + "Return.png").convert_alpha(), pos = (1738*C.SCALE_X, 350*C.SCALE_Y))

collision_box = pg.Rect(0, 850*C.SCALE_Y, 1920*C.SCALE_X, 100*C.SCALE_Y)
sell_box = SellBox(1284*C.SCALE_X, 831*C.SCALE_Y, 60*C.SCALE_X, 10*C.SCALE_Y)

if os.path.getsize(C.FACTORY_JSON_PATH) > 0:
    for item in json.loads(open(C.FACTORY_JSON_PATH).read()):
        player.item_group.add(Item(player, ITEMS, item))

# Loop
while True:
    pg.display.flip()
    clock.tick(C.FPS)

    # Update ---------------------------------------------------------------------------------------------
    pg.display.update()
    player.update()
    if player.state == State.FACTORY:
        player.item_group.update(player, collision_box, sell_box)
        factory.update()
        sell_box.update(player.particles)
        if player.do_drop_items():
            player.item_group.add(Item(player, ITEMS))

    elif player.state == State.INGREDIENT_STORAGE: ...

    if (ingredient_storage_button.clicked(player, 128)) or player.state == State.INGREDIENT_STORAGE_REFRESH:
        stored_ingredient_group = pg.sprite.Group()
        player.state = State.INGREDIENT_STORAGE
        if os.path.getsize(C.INGREDIENT_JSON_PATH) > 0:
            i, j, x, y = 0, 0, 0, 0
            data: dict = json.loads(open(C.INGREDIENT_JSON_PATH).read())

            for _, assets in data.items():
                assets: dict
                for path, amount in assets.items():
                    x = 224 + 96 * i
                    y = 304 + 96 * j
                    stored_ingredient_group.add(IngredientItem(path = path, amount = amount, pos = (x, y)))
                    i = (i + 1) % 10
                    if not i:
                        j += 1
            del i, j, x, y, data

    elif (artifact_storage_button.clicked(player, 128)) or player.state == State.ARTIFACT_STORAGE_REFRESH:
        stored_artifact_group = pg.sprite.Group()
        player.state = State.ARTIFACT_STORAGE
        if os.path.getsize(C.ARTIFACT_JSON_PATH) > 0:
            i, j, x, y = 0, 0, 0, 0
            data: dict = json.loads(open(C.ARTIFACT_JSON_PATH).read())

            for _, assets in data.items():
                assets: dict
                for path, info in assets.items():
                    x = 224 + 96 * i
                    y = 304 + 96 * j
                    stored_artifact_group.add(ArtifactItem(path = path, owned = True if info[0] else False, description = info[1], pos = (x, y)))
                    i = (i + 1) % 10
                    if not i:
                        j += 1
            del i, j, x, y, data

    elif factory_button.clicked(player, 128):
        player.state = State.FACTORY
    #shop_button.clicked(player, 128)

    # Draw -----------------------------------------------------------------------------------------------
    SCREEN.fill((0, 0, 0))
    factory_background.draw(SCREEN)
    for item in player.item_group:
        item: Item
        item.draw(SCREEN, player, C.GUI["item_menu"])
    factory.draw(SCREEN)
    currency_text = Text(text = f"{player.currency}", color = (255, 202, 0), pos = (1920*C.SCALE_X, 200*C.SCALE_Y), font=C.FONTS['XL'], is_centered = True, is_number_formatting = True)
    currency_text.draw(screen = SCREEN)

    ingredient_storage_button.draw(SCREEN, player)
    factory_button.draw(SCREEN, player)
    shop_button.draw(SCREEN, player)
    artifact_storage_button.draw(SCREEN, player)

    if player.state == State.INGREDIENT_STORAGE:
        storage_background.draw(screen = SCREEN)
        for item in stored_ingredient_group:
            item: IngredientItem
            item.draw(screen = SCREEN)

        for item in stored_ingredient_group:
            item: IngredientItem
            item.update_and_draw_gui(screen = SCREEN, player = player, gui = C.GUI["item_menu"])

    elif player.state == State.ARTIFACT_STORAGE:
        storage_background.draw(screen = SCREEN)
        for item in stored_artifact_group:
            item: ArtifactItem
            item.draw(screen = SCREEN)

        for item in stored_artifact_group:
            item: ArtifactItem
            item.update_and_draw_gui(screen = SCREEN, player = player, gui = C.GUI["item_menu"])


    for particle in player.particles:
        particle: Particle
        particle.update_and_draw(screen = SCREEN, particle_list = player.particles)

    # Event Handling -------------------------------------------------------------------------------------
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            ...

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                ...

        if event.type == pg.QUIT:
            with open(C.FACTORY_JSON_PATH, 'w') as file:
                json.dump([item.serialize() for item in player.item_group], file, indent=1)
            with open(C.PLAYER_JSON_PATH, 'w') as file:
                json.dump([player.serialize()], file, indent=1)
            pg.quit()
            exit()