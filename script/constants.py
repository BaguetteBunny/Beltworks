import ctypes
import pygame as pg
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# Size Constants
SCREEN_WIDTH = screensize[0]
SCREEN_HEIGHT = screensize[1]

SCALE_X=SCREEN_WIDTH / 1920
SCALE_Y=SCREEN_HEIGHT / 1080

FPS = 60

# Assets
ASSETS_PATH = "./assets/"
MENU_PATH = ASSETS_PATH + "./menu/"
BUTTON_PATH = MENU_PATH + "button/"
FONTS_PATH = ASSETS_PATH + "./fonts/"
BACKGROUNDS_PATH = ASSETS_PATH + "./backgrounds/"

DB_PATH = "db/"
FACTORY_JSON_PATH = DB_PATH + "factory_items.json"
ARTIFACT_JSON_PATH = DB_PATH + "artifact_items.json"
INGREDIENT_JSON_PATH = DB_PATH + "ingredient_items.json"
PLAYER_JSON_PATH = DB_PATH + "stats.json"

GUI = {
    'item_menu': pg.transform.smoothscale_by(pg.image.load(MENU_PATH + "Item_Menu.png").convert_alpha(), SCALE_X*1.5),
}

FONTS = {
    "4XS": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 2),
    "3XS": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 5),
    "2XS": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 10),
    "XS": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 15),
    "S": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 20),
    "M": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 30),
    "L": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 40),
    "XL": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 50),
    "2XL": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 60),
    "3XL": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 70),
    "4XL": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 80),
    "5XL": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 90),
    "6XL": pg.font.Font(FONTS_PATH + "monogram-extended.ttf", 100),
}
BACKGROUNDS = {
    "azur": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "azur.png").convert_alpha(), SCALE_X), (250,250)],
    "brewing_storm": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "brewing_storm.png").convert_alpha(), SCALE_X), (250,250)],
    "default": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "default.png").convert_alpha(), SCALE_X), (250,250)],
    "night_sea": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "night_sea.png").convert_alpha(), SCALE_X), (250,250)],
    "rocky": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "rocky.png").convert_alpha(), SCALE_X), (250,250)],
    "shore": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "shore.png").convert_alpha(), SCALE_X), (250,250)],
    "sunset": [pg.transform.smoothscale_by(pg.image.load(BACKGROUNDS_PATH + "sunset.png").convert_alpha(), SCALE_X), (250,250)],
}