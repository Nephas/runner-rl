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


# Graphics
SCREEN = np.array([70, 50])  # [WIDTH, HEIGHT]
SEPARATOR = (3. / 4. * SCREEN).astype('int')

LIMIT_FPS = 30
TIC_SEC = 10
TIC_SIZE = 1. / TIC_SEC

# Map
MAP = [128, 128]  # [WIDTH, HEIGHT]

ROOM_SIZE = [[10, 20], [5, 5], [10, 20], [
    15, 30], [20, 40], [10, 15], [10, 15]]
N_CHILD = [[0, 0], [1, 1], [1, 1], [2, 3], [3, 5], [4, 6], [6, 10]]
ROOM_TYPE = [["rectangle"], ["gallery"], ["corridor"], ["corridor"], [
    "round", "rectangle", "corridor"], ["rectangle", "square", "corner"], ["rectangle"]]

NEIGHBORHOOD = [np.array([i, j]) for i in [-1, 0, 1] for j in [-1, 0, 1]]

TIERCOLOR = [np.array([40 * i, 255 - 40 * i, 255]) for i in range(10)]
WHITE = (255,255,255)
BLACK = (0,0,0)
#np.array([[0,0],[1,0],[0,1],[-1,0],[0,-1]])

def add(x1, x2):
    return [x1[X] + x2[X], x1[Y] + x2[Y]]


def distance(x1, x2):
    return ((x1[X] - x2[X])**2 + (x1[Y] - x2[Y])**2)**0.5


def timing(f):
    def wrap(*args):
        time1 = t.time()
        ret = f(*args)
        time2 = t.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap
