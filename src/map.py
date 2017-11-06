from globals import *

import math as m
import numpy as np
import random as rd


class Map:
    WIDTH = 128
    HEIGHT = 128

    def __init__(self, main=None):
        self.main = main
        self.tile = [[Cell(self, [x, y]) for y in range(Map.HEIGHT)]
                     for x in range(Map.WIDTH)]

    def getTile(self, pos):
        return self.tile[pos[X]][pos[Y]]

    def updatePhysics(self):
        for cell in self.main.gui.mapCells:
            cell.light = 2
            cell.vision[LOS] = False

        self.castFov(self.main.player.cell.pos)

        for cell in self.main.gui.mapCells:
            cell.updatePhysics()

    def updateRender(self):
        for cell in self.main.gui.mapCells:
            cell.updateRender()

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
        for n in NEIGHBORHOOD:
            self.getTile(pos + n).vision = [True, True]

        blockIndex = 0
        blockPoint = [0, 0]

        for line in self.main.render.raymap:
            if not all(line[blockIndex] == blockPoint):
                for i, point in enumerate(line):
                    if not self.getTile(point + pos).block[LOS]:
                        for n in NEIGHBORHOOD:
                            self.getTile(point + pos + n).vision = [True, True]
                    else:
                        blockIndex = i
                        blockPoint = point
                        break

    def castLight(self, pos):
        self.getTile(pos).light = MAX_LIGHT

        for line in self.main.render.lightmap:
            for i, point in enumerate(line):
                cell = self.getTile(point + pos)
                if not cell.block[LOS]:
                    cell.light = max(MAX_LIGHT - 2 * i, cell.light)
                else:
                    break


class Cell:
    def __init__(self, map, pos, wall=None):
        self.map = map
        self.pos = np.array(pos)
        self.wall = wall
        self.tier = -1
        self.light = 2

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

        self.char = ' '
        self.bg = tuple(self.light * TIERCOLOR[self.tier] / 16)
        if self.tier == -1:
            self.bg = (40, 40, 40)

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

    def draw(self, window, pos):
        if self.vision[EXP]:
            window.draw_char(pos[X], pos[Y], self.char, self.fg, self.bg)

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
                if cell.wall is not None and cell.wall:
                    align += 't'
                else:
                    align += 'f'
            return Wall.ALIGNMAP[align]
        else:
            return 0
