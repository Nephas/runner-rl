from src.globals import *

import math as m
import numpy as np
import random as rd
import itertools as it

from src.render import Render

class Map:
    WIDTH = 128
    HEIGHT = 128

    FOVMAP = Render.rayMap(24, 96)
    FOV_NEIGHBORHOOD = np.array([[0,1],[1,0],[0,-1],[-1,0],[1,1],[1,-1],[-1,-1],[-1,1]])

    PHYSICSRANGE = np.array([24, 24])

    def __init__(self, main=None):
        self.main = main
        self.tile = [[Cell(self, [x, y]) for y in range(Map.HEIGHT)]
                     for x in range(Map.WIDTH)]

    def clear(self):
        self.tile = [[Cell(self, [x, y]) for y in range(Map.HEIGHT)]
                     for x in range(Map.WIDTH)]

    def getTile(self, pos):
        return self.tile[pos[X]][pos[Y]]

    def updatePhysics(self):
        rect = Rectangle(self.main.player.cell.pos -
                         Map.PHYSICSRANGE, *(2 * Map.PHYSICSRANGE))

        for cell in rect.getCells(self):
            cell.light = BASE_LIGHT
            cell.vision[LOS] = False

        self.castFov(self.main.player.cell.pos)

        for cell in rect.getCells(self):
            cell.updatePhysics()

    def updateRender(self):
        for cell in self.main.gui.getCells(self):
            cell.updateRender()

    def getObjects(self):
        for x in range(Map.WIDTH):
            for y in range(Map.HEIGHT):
                for obj in self.tile[x][y].object:
                    yield obj

    def getAll(self, objClass=None):
        if type(objClass) is str:
            return filter(lambda o: o.__class__.__name__ == objClass, self.getObjects())
        elif objClass is not None:
            return filter(lambda o: isinstance(o, objClass), self.getObjects())
        else:
            return self.getObjects()

    def getNeighborhood(self, pos, shape=4):
        if shape == 4:
            offsets = np.array([[0, -1], [1, 0], [0, 1], [-1, 0]])
        if shape == 8:
            offsets = [np.array([i, j]) for i in [-1, 0, 1]
                       for j in [-1, 0, 1]]
        positions = map(lambda off: off + pos, offsets)
        return map(lambda p: self.getTile(p), filter(lambda p: self.contains(p), positions))

    def contains(self, pos):
        return pos[X] in range(0, Map.WIDTH) and pos[Y] in range(0, Map.HEIGHT)

    def castFov(self, pos):
        try:
            self.getTile(pos).vision = [True, True]

            blockIndex = 0
            blockPoint = [0, 0]

            for baseLine in self.FOVMAP:
                if not all(baseLine[blockIndex] == blockPoint):
                    line = baseLine + pos
                    for i, point in enumerate(line):
                        if not self.getTile(point).block[LOS]:
                            self.getTile(point).vision = [True, True]
                            for neighbor in map(lambda p: self.getTile(p), Map.FOV_NEIGHBORHOOD + point):
                                if neighbor.block[LOS]:
                                    neighbor.vision = [True, True]
                        else:
                            blockIndex = i
                            blockPoint = baseLine[i]
                            break
        except IndexError:
            pass


class Rectangle:  # a rectangle on the map. used to characterize a room or a window
    def __init__(self, pos, w, h):
        self.pos = np.array(pos)
        self.size = np.array([w, h])
        self.x = [max(0, pos[X]), min(Map.WIDTH, pos[X] + w)]
        self.y = [max(0, pos[Y]), min(Map.HEIGHT, pos[Y] + h)]
        self.center = (self.pos + self.size / 2).round().astype('int')

    def intersects(self, other):  # returns true if this rectangle intersects with another one
        return not (self.x[MAX] <= other.x[MIN] or other.x[MAX] <= self.x[MIN] or self.y[MAX] <= other.y[MIN] or
                    other.y[MAX] <= self.y[MIN])

    def contains(self, pos):
        return pos[X] in range(*self.x) and pos[Y] in range(*self.y)

    def border(self):
        positions = []
        for x in range(self.x[MIN], self.x[MAX]):
            positions.append([x, self.y[MIN]])
            positions.append([x, self.y[MAX] - 1])
        for y in range(self.y[MIN], self.y[MAX]):
            positions.append([self.x[MIN], y])
            positions.append([self.x[MAX] - 1, y])
        return positions

    def drawFrame(self, map, color):
        for pos in self.border():
            map.getTile().bg = color

    def getPositions(self):
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                yield [x, y]

    def getCells(self, map):
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                yield map.tile[x][y]


class Cell:
    def __init__(self, map, pos, wall=None):
        self.map = map
        self.pos = np.array(pos)
        self.wall = wall
        self.tier = -1
        self.light = BASE_LIGHT
        self.grid = None

        # [MOVE, LOS]
        self.block = [False, False]
        self.vision = [False, False]

        self.object = []

        # graphics attributes
        self.char = ' '
        self.bg = COLOR['BLACK']
        self.fg = COLOR['WHITE']

    def addObject(self, obj):
        self.object.append(obj)
        obj.cell = self

    def isEmpty(self):
        return self.object == [] and not self.wall

    def updateRender(self):
        if not self.vision[EXP]:
            return

        if not self.vision[LOS]:
            self.fg = (25, 25, 25)
            self.bg = (10, 10, 10)
            return

        if self.wall:
            self.bg = (40, 40, 40)
            self.fg = (85, 85, 85)
            return

        self.bg = tuple(self.light * TIERCOLOR[self.tier] / MAX_LIGHT)
        self.char = ' '

        for object in self.object:
            self.char = object.char
            self.fg = object.fg

    def makeWall(self):
        self.object = []
        self.wall = True
        self.block = [True, True]
        self.char = Wall.getChar(self.pos, self.map)

    def removeWall(self):
        self.object = []
        self.wall = False
        self.block = [False, False]
        self.char = ' '

    def updatePhysics(self):
        self.block = [False, False]
        if self.wall:
            self.block[MOVE] = True
            self.block[LOS] = True
        for obj in self.object:
            if obj.block[MOVE]:
                self.block[MOVE] = True
            if obj.block[LOS]:
                self.block[LOS] = True
            obj.physics(self.map)

    def drawMap(self, window, pos):
        if self.vision[EXP]:
            window.draw_char(pos[X], pos[Y], self.char, self.fg, self.bg)

    def drawNet(self, window, pos):
        if self.grid is None:
            window.draw_char(pos[X], pos[Y], ' ', self.fg,
                             list(TIERCOLOR[self.tier]))
        elif not self.grid:
            window.draw_char(pos[X], pos[Y], 254,
                             COLOR['GREEN'], list(TIERCOLOR[self.tier]))
        elif self.grid:
            window.draw_char(pos[X], pos[Y], ' ', list(
                TIERCOLOR[self.tier]), COLOR['GREEN'])

    def drawHighlight(self, window, pos, color=COLOR['WHITE']):
        if self.vision[EXP]:
            window.draw_char(pos[X], pos[Y], self.char, self.fg, color)
        else:
            window.draw_char(pos[X], pos[Y], ' ', self.fg, color)


class Wall:
    ALIGNMAP = {'ffff': 206,
                'tttt': 206,
                'tftf': 186,
                'ftft': 205,
                'ttff': 200,
                'fftt': 187,
                'fttf': 201,
                'tfft': 188,
                'tfff': 186,
                'ftff': 205,
                'fftf': 186,
                'ffft': 205,
                'fttt': 203,
                'tftt': 185,
                'ttft': 202,
                'tttf': 204}

    def __init__(self):
        pass

    @staticmethod
    def getChar(pos, tileMap):
        align = ''
        neighborhood = tileMap.getNeighborhood(pos)

        if len(neighborhood) == 4:
            for cell in neighborhood:
                if cell.wall is None or cell.wall:
                    align += 't'
                else:
                    align += 'f'
            return Wall.ALIGNMAP[align]
        else:
            return 0
