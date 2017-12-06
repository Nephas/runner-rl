from src.globals import *

import math as m
import numpy as np
import random as rd
import itertools as it

from bearlibterminal import terminal as term


class Map:
    WIDTH = 128
    HEIGHT = 128

    PHYSICSRANGE = np.array([20, 20])

    def __init__(self, main=None):
        self.main = main
        self.tile = [[Cell(self, [x, y]) for y in range(Map.HEIGHT)]
                     for x in range(Map.WIDTH)]

    def clear(self):
        self.tile = [[Cell(self, [x, y]) for y in range(Map.HEIGHT)]
                     for x in range(Map.WIDTH)]

    def getTile(self, pos):
        return self.tile[pos[X]][pos[Y]]

    def allTiles(self):
        for x in range(0, Map.WIDTH):
            for y in range(0, Map.HEIGHT):
                yield self.tile[x][y]

    def allPositions(self):
        for x in range(0, Map.WIDTH):
            for y in range(0, Map.HEIGHT):
                yield np.array([x, y])

    def updatePhysics(self):
        rect = Rectangle(self.main.player.cell.pos -
                         Map.PHYSICSRANGE, *(2 * Map.PHYSICSRANGE))

        for cell in rect.getCells(self):
            cell.light = BASE_LIGHT
            cell.vision[LOS] = False

        for cell in rect.getCells(self):
            cell.updatePhysics()

        self.main.player.castFov(self)

    def updateRender(self):
        for cell in self.main.render.mapPanel.camera.getCells(self):
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

    @staticmethod
    def contains(pos):
        return pos[X] in range(0, Map.WIDTH) and pos[Y] in range(0, Map.HEIGHT)


class Rectangle:  # a rectangle on the map. used to characterize a room or a window
    def __init__(self, pos, w, h):
        self.pos = np.array(pos)
        self.size = np.array([w, h])
        self.x = [max(0, pos[X]), min(Map.WIDTH, pos[X] + w)]
        self.y = [max(0, pos[Y]), min(Map.HEIGHT, pos[Y] + h)]
        self.center = (self.pos + self.size / 2).round().astype('int')
        self.area = w * h

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

    def getObjects(self, map):
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                for obj in map.tile[x][y].object:
                    yield obj


class Cell:
    FLOOR = 0x10B2
    GRATE = 0x1000

    def __init__(self, map, pos, wall=None):
        self.map = map
        self.room = None
        self.pos = np.array(pos)
        self.wall = wall
        self.light = BASE_LIGHT
        self.grid = None

        # [MOVE, LOS, LIGHT]
        self.block = [False, False, False]
        # [EXP, LOS]
        self.vision = [False, False]

        # contents
        self.object = []
        self.effect = []

        # graphics attributes [FLOOR, EFFECT, OBJECT]
        self.stack = [Cell.FLOOR, None, None]
        self.color = [COLOR['BLACK'], COLOR['WHITE'], COLOR['WHITE']]

        self.neighborhood = {'SMALL': [],
                             'LARGE': []}
        self.calcNeighborhood()

    def calcNeighborhood(self):
        self.neighborhood['SMALL'] = filter(lambda p: Map.contains(p),
                                            map(lambda off: off + self.pos,
                                                np.array([[0, -1], [1, 0], [0, 1], [-1, 0]])))
        self.neighborhood['LARGE'] = self.neighborhood['SMALL'] + filter(lambda p: Map.contains(p),
                                                                         map(lambda off: off + self.pos,
                                                                             np.array([[1, 1], [1, -1], [-1, -1], [-1, 1]])))

    def addObject(self, obj):
        self.object.append(obj)
        obj.cell = self

    def addEffect(self, newEffect):
        for eff in self.effect:
            if eff.__class__ is newEffect.__class__:
                eff.stack(newEffect)
                return
        self.effect.append(newEffect)
        newEffect.cell = self

    def isEmpty(self):
        return self.object == [] and not self.wall

    def hasDoor(self):
        for obj in self.object:
            if obj.__class__.__name__ in ['Door', 'SecDoor', 'Vent']:
                return True
        return False

    def atWall(self):
        for n in self.getNeighborhood():
            if n.wall:
                return True
        return False

    def updateRender(self):
        if not self.vision[EXP]:
            self.color = [COLOR['BLACK'], COLOR['BLACK'], COLOR['BLACK']]
            return

        if not self.vision[LOS]:
            self.color = [COLOR['NIGHT'], COLOR['NIGHT'], COLOR['NIGHT']]
            return

        if self.room is None:
            self.stack[0] = self.GRATE
            roomCol = np.array(COLOR['WHITE'])
        else:
            roomCol = self.map.palette[self.room.tier]

        self.color[0] = roomCol * self.light // MAX_LIGHT // 2

        if self.wall:
            self.color[1] = roomCol * self.light // MAX_LIGHT
            self.color[2] = self.color[1]#COLOR['WHITE']
            return

        self.stack[1] = None
        self.stack[2] = None

        if len(self.object) != 0:
            obj = max(self.object, key=lambda obj: obj.priority)
            self.stack[2] = obj.char
            self.color[2] = obj.fg
            if self.hasDoor():
                self.color[2] = roomCol * self.light // MAX_LIGHT

        if len(self.effect) != 0:
            eff = max(self.effect, key=lambda eff: eff.priority)
            self.stack[1] = eff.char
            self.color[1] = eff.fg

    def makeWall(self):
        self.object = []
        self.wall = True
        self.block = [True, True, True]
        self.stack[1] = Wall.getChar(self.pos, self.map)

    def removeWall(self):
        self.wall = False
        self.block = [False, False, False]
        self.stack[1] = None

    def getNeighborhood(self, shape='SMALL'):
        if shape in self.neighborhood:
            for cell in map(lambda p: self.map.getTile(p), self.neighborhood[shape]):
                yield cell
        else:
            offsets = [np.array([i, j]) for i in range(-1 * shape, shape)
                       for j in range(-1 * shape, shape)]
            offsets = filter(lambda off: np.linalg.norm(off) < shape, offsets)
            positions = map(lambda off: off + self.pos, offsets)
            for pos in positions:
                yield self.map.getTile(pos)

    def updatePhysics(self):
        if self.wall:
            self.block = [True, True, True]
        else:
            self.block = [False, False, False]

        for obj in self.object + self.effect:
            if obj.block[MOVE]:
                self.block[MOVE] = True
            if obj.block[LOS]:
                self.block[LOS] = True
            if obj.block[LIGHT]:
                self.block[LIGHT] = True
            obj.physics(self.map)


class Wall:
    ALIGNMAP = {'CENTER': 0x10CD,
                'UP_LEFT': 0x10BC,
                'UP_RIGHT': 0x10C8,
                'DOWN_LEFT': 0x10BB,
                'DOWN_RIGHT': 0x10C9,
                'UP': 0x10CB,
                'DOWN': 0x10CA,
                'LEFT': 0x10CC,
                'RIGHT': 0x10B9,
                'UP_DOWN': 0x1194,
                'LEFT_RIGHT': 0x1194}

    def __init__(self):
        pass

    @staticmethod
    def getChar(pos, tileMap):
        align = ''
        cell = tileMap.getTile(pos)
        neighborhood = list(cell.getNeighborhood('LARGE'))

        surfaceString = 'CENTER'

        floorCells = filter(lambda c: not (c.wall or c.hasDoor()), cell.getNeighborhood('SMALL'))
        if len(floorCells) == 1:
            surfaceDir = floorCells[0].pos - cell.pos

            if surfaceDir[Y] == 1:
                surfaceString = 'DOWN'
            elif surfaceDir[Y] == -1:
                surfaceString = 'UP'
            elif surfaceDir[X] == 1:
                surfaceString = 'RIGHT'
            elif surfaceDir[X] == -1:
                surfaceString = 'LEFT'

        if len(floorCells) == 2:
            surfaceDir = floorCells[0].pos - cell.pos
            if surfaceDir[Y] == 1:
                surfaceString = 'CENTER'
            elif surfaceDir[Y] == 0:
                surfaceString = 'CENTER'

        else:
            floorCells = filter(lambda c: not (c.wall or c.hasDoor()), cell.getNeighborhood('LARGE'))
            if len(floorCells) == 1:
                surfaceDir = floorCells[0].pos - cell.pos

                if surfaceDir[Y] > 0:
                    surfaceString = 'DOWN'
                else:
                    surfaceString = 'UP'

                if surfaceDir[X] > 0:
                    surfaceString += '_RIGHT'
                else:
                    surfaceString += '_LEFT'

        return Wall.ALIGNMAP[surfaceString]
