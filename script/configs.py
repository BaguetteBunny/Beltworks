import enum

class RainbowConfig:
    def __init__(self, enabled: bool = False, hue_step: int = 10, fixed_lightness: int = 80) -> None:
        self.enabled = enabled
        self.hue_step = hue_step
        self.fixed_lightness = fixed_lightness

class Shapes(enum.Enum):
    CIRCLE = 0
    SQUARE = 1
    TRIANGLE = 2

class State(enum.Enum):
    FACTORY = 0
    ITEM_STORAGE = 1
    ITEM_STORAGE_REFRESH = 1.5
    CRAFTABLE_STORAGE = 2
    CRAFTABLE_STORAGE_REFRESH = 2.5