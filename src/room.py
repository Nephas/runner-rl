from globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
from src.object import Obstacle

class Rectangle:  # a rectangle on the map. used to characterize a room.
    def __init__(self, anchor, w, h):
        self.anchor = anchor
        self.size = [w, h]
        self.x = [anchor[X], anchor[X] + w]
        self.y = [anchor[Y], anchor[Y] + h]
        self.center = [(self.x[MIN] + self.x[MAX]) / 2.,
                       (self.y[MIN] + self.y[MAX]) / 2.]

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
        for i in range(rd.randint(nChildren[MIN], nChildren[MAX])):
            rectangle = None
            invalid = True
            counter = 0
            direction = 0
            alignment = 0
            while invalid:
                direction = rd.randint(0, 3)
                alignment = rd.randint(0, 1)
                shape = rd.choice(shapeList)

                w = rd.randint(size[MIN], size[MAX])
                h = rd.randint(size[MIN], size[MAX])
                if shape is "round" or shape is "square":
                    h = w
                if shape is "corridor" or shape is "gallery":
                    if direction is UP or direction is DOWN:
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

                rectangle = Rectangle(add(self.rectangle.anchor, offset), w, h)

                counter += 1
                if counter >= 100:
                    rectangle = None
                    break

                invalid = False
                for tier in map.tier:
                    for room in tier:
                        if rectangle.intersects(room.rectangle) or not rectangle.inmap():
                            invalid = True

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
        return [int(m.floor(self.rectangle.center[X])), int(m.floor(self.rectangle.center[Y]))]

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
            if not cell.wall or cell.object != []:
                cell.addObject(cp.copy(obj))
                i += 1

    def carve(self, map):
        for x in range(self.rectangle.x[MIN], self.rectangle.x[MAX]):
            for y in range(self.rectangle.y[MIN], self.rectangle.y[MAX]):
                if map.tile[x][y].wall is None:
                    map.tile[x][y].wall = True
        for x in range(self.rectangle.x[MIN] + 1, self.rectangle.x[MAX] - 1):
            for y in range(self.rectangle.y[MIN] + 1, self.rectangle.y[MAX] - 1):
                if self.shape is not "round":
                    map.tile[x][y].wall = False
                    map.tile[x][y].tier = self.tier
                elif distance([x, y], add([-0.5, -0.5], self.rectangle.center)) < self.rectangle.size[X] / 2.0 - 1:
                    map.tile[x][y].wall = False
                    map.tile[x][y].tier = self.tier
        if self.shape is "gallery":
            pos = self.getCenter()
            map.tile[pos[X]][pos[Y]].tier = -1
            map.tile[pos[X]][pos[Y]].wall = True
