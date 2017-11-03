import numpy as np
import time as t

# Constants
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

TIERCOLOR = [np.array([40 * i, 255 - 40 * i, 255]) for i in range(10)]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
