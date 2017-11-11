import numpy as np
import time as t

X = 0
Y = 1
MIN = 0
MAX = 1
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
MOVE = 0
EXP = 0
LOS = 1
WIDTH = 0
HEIGHT = 1

NEIGHBORHOOD = [np.array([i, j]) for i in [-1, 0, 1] for j in [-1, 0, 1]]

MAX_LIGHT = 16
BASE_LIGHT = 2

COLOR = {'BLACK': (0, 0, 0),
         'WHITE': (255, 255, 255),
         'RED'	: (255, 0, 0),
         'LIME'	: (0, 255, 0),
         'BLUE'	: (0, 0, 255),
         'YELLOW': (255, 255, 0),
         'CYAN'	: (0, 255, 255),
         'MAGENTA': (255, 0, 255),
         'SILVER': (192, 192, 192),
         'GRAY'	: (128, 128, 128),
         'DARKGRAY'	: (32, 32, 32),
         'MAROON': (128, 0, 0),
         'OLIVE': (128, 128, 0),
         'GREEN': (0, 255, 0),
         'MEDIUMGREEN': (0, 128, 0),
         'PURPLE': (128, 0, 128),
         'TEAL': (0, 128, 128),
         'NAVY': (0, 0, 128)}

TIERCOLOR = [np.array([40 * i, 255 - 40 * i, 255]) for i in range(10)]
TIERCOLOR[-1] = np.array((10,10,10))
