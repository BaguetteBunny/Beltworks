import pygame as pg
import os, json

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

player = Player()
factory = Factory(screen = SCREEN)
factory_background = Background(C.BACKGROUNDS[player.current_background])
storage_background = Storage()

artifact_storage_button = Button(image = C.BUTTON["artifact"], pos = (1450*C.SCALE_X, 350*C.SCALE_Y))
ingredient_storage_button = Button(image =  C.BUTTON["ingredient"], pos = (1450*C.SCALE_X, 475*C.SCALE_Y))
shop_button = Button(image =  C.BUTTON["shop"], pos = (1605*C.SCALE_X, 350*C.SCALE_Y))
factory_button = Button(image =  C.BUTTON["factory"], pos = (1738*C.SCALE_X, 350*C.SCALE_Y))

collision_box = pg.Rect(0, 850*C.SCALE_Y, 1920*C.SCALE_X, 100*C.SCALE_Y)
sell_box = SellBox(1284*C.SCALE_X, 831*C.SCALE_Y, 60*C.SCALE_X, 10*C.SCALE_Y)

if os.path.getsize(C.FACTORY_JSON_PATH) > 0:
    for item in json.loads(open(C.FACTORY_JSON_PATH).read()):
        player.item_group.add(Item(player, player.items, item))

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
            player.item_group.add(Item(player, player.items))

    elif player.state == State.INGREDIENT_STORAGE: ...

    if (ingredient_storage_button.clicked(player, 128)) or player.state == State.INGREDIENT_STORAGE_REFRESH:
        player.stored_ingredient_group = pg.sprite.Group()
        player.state = State.INGREDIENT_STORAGE
        if player.ingredients:
            i, j, x, y = 0, 0, 0, 0
            data: dict = player.ingredients

            for _, assets in data.items():
                assets: dict
                for path, amount in assets.items():
                    x = 224 + 96 * i
                    y = 304 + 96 * j
                    player.stored_ingredient_group.add(player.main_ingredient if (player.main_ingredient and player.main_ingredient.path == path) else IngredientItem(path = path, amount = amount, pos = (x, y)))
                    i = (i + 1) % 10
                    if not i:
                        j += 1
            del i, j, x, y, data

    elif (artifact_storage_button.clicked(player, 128)) or player.state == State.ARTIFACT_STORAGE_REFRESH:
        stored_artifact_group = pg.sprite.Group()
        player.state = State.ARTIFACT_STORAGE
        if player.artifacts:
            i, j, x, y = 0, 0, 0, 0
            data: dict = player.artifacts

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
        for item in player.stored_ingredient_group:
            item: IngredientItem
            item.draw(screen = SCREEN)

        for item in player.stored_ingredient_group:
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
            with open(C.INGREDIENT_JSON_PATH, 'w') as file:
                json.dump(player.ingredients, file, indent=1)
            with open(C.ARTIFACT_JSON_PATH, 'w') as file:
                json.dump(player.artifacts, file, indent=1)
            pg.quit()
            exit()