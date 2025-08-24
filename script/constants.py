import ctypes
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# Size Constants
SCREEN_WIDTH = screensize[0]
SCREEN_HEIGHT = screensize[1]

SCALE_X=SCREEN_WIDTH / 1920
SCALE_Y=SCREEN_HEIGHT / 1080

FPS = 60