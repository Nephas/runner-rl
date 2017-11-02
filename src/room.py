from globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
from src.object import Obstacle


class Rectangle:  # a rectangle on the map. used to characterize a room.
    def __init__(self, anchor, w, h):
        self.anchor = np.array(anchor)
        self.size = np.array([w, h])
        self.x = [anchor[X], anchor[X] + w]
        self.y = [anchor[Y], anchor[Y] + h]
        self.center = (self.anchor + self.size / 2).round()

    def intersects(self, other):  # returns true if this rectangle intersects with another one
        return not (self.x[MAX] <= other.x[MIN] or other.x[MAX] <= self.x[MIN] or self.y[MAX] <= other.y[MIN] or
                    other.y[MAX] <= self.y[MIN])

    def contains(self, pos):
        return (pos[X] <= self.x[MAX] and pos[X] >= self.x[MIN] and pos[Y] <= self.y[MAX] and pos[Y] >= self.y[MIN])

    def border(self):
        positions = []
        for x in range(self.x[MIN], self.x[MAX]):
            positions.append([x, self.y[MIN]])
            positions.append([x, self.y[MAX] - 1])
        for y in range(self.y[MIN], self.y[MAX]):
            positions.append([self.x[MIN], y])
            positions.append([self.x[MAX] - 1, y])
        return positions

    def tiles(self):
        positions = []
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                positions.append([x, y])
        return positions

    def inmap(self):
        return (self.x[MAX] < MAP[WIDTH] and self.x[MIN] > 0 and self.y[MAX] < MAP[HEIGHT] and self.y[MIN] > 0)


class Room:
    def __init__(self, tier, parent, rectangle, shape="rectangle"):
        self.shape = shape
        self.tier = tier
        self.function = None
        self.parent = parent
        self.rectangle = rectangle
        self.children = []

    def propagate(self, map, nChildren, size, shapeList):
        # number of child rooms
        for i in range(rd.randint(nChildren[MIN], nChildren[MAX])):
            # number of tries to find a valid child
            for i in range(100):
                direction = rd.choice([UP, DOWN, LEFT, RIGHT])
                alignment = rd.choice([MIN, MAX])
                shape = rd.choice(shapeList)

                w = rd.randint(*size)
                h = rd.randint(*size)
                if shape is "round" or shape is "square":
                    h = w
                elif shape is "corridor" or shape is "gallery":
                    if direction in [UP, DOWN]:
                        w = 5
                    else:
                        h = 5

                if direction is UP:
                    if alignment is MIN:
                        offset = [0, -h]
                    elif alignment is MAX:
                        offset = [self.rectangle.size[X] - w, -h]
                elif direction is RIGHT:
                    if alignment is MIN:
                        offset = [self.rectangle.size[X], 0]
                    elif alignment is MAX:
                        offset = [self.rectangle.size[X],
                                  self.rectangle.size[Y] - h]
                elif direction is DOWN:
                    if alignment is MIN:
                        offset = [0, self.rectangle.size[Y]]
                    elif alignment is MAX:
                        offset = [self.rectangle.size[X] -
                                  w, self.rectangle.size[Y]]
                elif direction is LEFT:
                    if alignment is MIN:
                        offset = [-w, 0]
                    elif alignment is MAX:
                        offset = [-w, self.rectangle.size[Y] - h]

                rectangle = Rectangle(
                    self.rectangle.anchor + np.array(offset), w, h)

                for tier in map.tier:
                    for room in tier:
                        if rectangle is not None:
                            if rectangle.intersects(room.rectangle) or not rectangle.inmap():
                                rectangle = None

                if rectangle is not None:
                    break

            if rectangle is not None:
                if direction is UP or direction is DOWN:
                    if rectangle.size[X] < self.rectangle.size[X]:
                        tunnelDirection = "vertical"
                    else:
                        tunnelDirection = "horizontal"
                elif direction is LEFT or direction is RIGHT:
                    if rectangle.size[Y] < self.rectangle.size[Y]:
                        tunnelDirection = "horizontal"
                    else:
                        tunnelDirection = "vertical"

                nextRoom = Room(self.tier + 1, self, rectangle, shape)
                self.children.append(nextRoom)
                map.tier[nextRoom.tier].append(nextRoom)
                nextRoom.carve(map)

                if not map.carveTunnel(nextRoom, self, tunnelDirection, self.tier, True):
                    map.carveTunnel(
                        nextRoom, self, not tunnelDirection, self.tier, True)

    def getCenter(self):
        return self.rectangle.center.astype('int')

    def randomSpot(self, margin=1):
        x = rd.randint(self.rectangle.x[MIN] +
                       margin, self.rectangle.x[MAX] - margin)
        y = rd.randint(self.rectangle.y[MIN] +
                       margin, self.rectangle.y[MAX] - margin)
        return np.array([x, y])

    def scatter(self, map, obj, n):
        i = 0
        while i < n:
            cell = map.getTile(self.randomSpot())
            if cell.isEmpty():
                cell.addObject(cp.copy(obj))
                i += 1

    def distribute(self, map, obj, dx=5, dy=5, margin=1):
        count = 0
        for x in range(self.rectangle.x[MIN] + margin, self.rectangle.x[MAX] - margin):
            for y in range(self.rectangle.y[MIN] + margin, self.rectangle.y[MAX] - margin):
                if (x % dx == 0) and (y % dy == 0):
                    cell = map.tile[x][y]
                    if not cell.wall or cell.object != []:
                        cell.addObject(cp.copy(obj))
                        count += 1
        return count


    def updateTier(self, map):
        for x in range(*self.rectangle.x):
            for y in range(*self.rectangle.y):
                cell = map.tile[x][y]
                if not cell.wall:
                    cell.tier = self.tier

    def carve(self, map):
        # create a boundary wall
        for x in range(self.rectangle.x[MIN], self.rectangle.x[MAX]):
            for y in range(self.rectangle.y[MIN], self.rectangle.y[MAX]):
                if map.tile[x][y].wall is None:
                    map.tile[x][y].makeWall()

        # carve basic rectangle or circle
        for x in range(self.rectangle.x[MIN] + 1, self.rectangle.x[MAX] - 1):
            for y in range(self.rectangle.y[MIN] + 1, self.rectangle.y[MAX] - 1):
                if self.shape is not "round":
                    map.tile[x][y].removeWall()
                    map.tile[x][y].tier = self.tier
                elif np.linalg.norm([x, y] - (self.rectangle.center - np.array([0.5, 0.5]))) < self.rectangle.size[X] / 2.0 - 1:
                    map.tile[x][y].removeWall()
                    map.tile[x][y].tier = self.tier

        if self.shape is "corner":
            cutLen = self.getCenter() - self.rectangle.anchor
            cutLen[X] = rd.choice([0, cutLen[X] + 1])
            cutLen[Y] = rd.choice([0, cutLen[Y] + 1])

            cutStart = self.rectangle.anchor + cutLen
            cutEnd = self.getCenter() + cutLen

            for x in range(cutStart[X], cutEnd[X]):
                for y in range(cutStart[Y], cutEnd[Y]):
                    map.tile[x][y].wall = True
                    map.tile[x][y].tier = -1

#         if self.shape is "gallery":
#             for x in range(self.rectangle.x[MIN] + 1, self.rectangle.x[MAX] - 1):
#                 for y in range(self.rectangle.y[MIN] + 1, self.rectangle.y[MAX] - 1):
# #                    if (x % 3 == 0) and (y % 3 == 0):
#                     map.tile[x][y].wall = True
#                     map.tile[x][y].tier = -1


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
