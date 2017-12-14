from src.globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it

from src.object.furniture import Container, Barrel, Desk
from src.object.door import Vent, SecDoor, AutoDoor
from src.object.item import Item, Key, PlotDevice

from src.level.map import Rectangle


class Room(Rectangle):
    def __init__(self, pos, w, h, tier=-1, parent=None, color=COLOR['WHITE']):
        Rectangle.__init__(self, pos, w, h)
        self.tier = tier
        self.function = None
        self.parent = parent
        self.children = []
        self.color = color

    def carve(self, map):
        self.updateCells(map)

        # create a boundary wall
        for cell in self.getCells(map):
            cell.room = self
            if cell.wall is None:
                cell.makeWall()

        # carve basic rectangle
        for x in range(self.x[MIN] + 1, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 1, self.y[MAX] - 1):
                map.tile[x][y].removeWall()

    def fill(self, map):
        for cell in self.getCells(map):
            cell.room = None
            cell.makeWall()

    def generateContent(self, map):
        pass

    def randomSpot(self, margin=1):
        x = rd.randint(self.x[MIN] +
                       margin, self.x[MAX] - margin - 1)
        y = rd.randint(self.y[MIN] +
                       margin, self.y[MAX] - margin - 1)
        return np.array([x, y])

    def scatter(self, map, obj, n=1, margin=1):
        i = 0
        for j in range(500):
            cell = map.getTile(self.randomSpot(margin))
            if cell.isEmpty():
                cell.addObject(cp.copy(obj))
                i += 1
            if i >= n:
                break
                return True
        return False

    def edge(self):
        positions = []
        for x in range(self.x[MIN] + 1, self.x[MAX] - 1):
            positions.append([x, self.y[MIN] + 1])
            positions.append([x, self.y[MAX] - 2])
        for y in range(self.y[MIN] + 1, self.y[MAX] - 1):
            positions.append([self.x[MIN] + 1, y])
            positions.append([self.x[MAX] - 2, y])
        return positions

    def placeAtWall(self, tileMap, obj):
        cells = map(lambda p: tileMap.getTile(p), self.edge())
        cells = filter(lambda c: c.isEmpty() and c.atWall(), cells)
        cell = rd.choice(cells)
        cell.addObject(cp.copy(obj))
        return cell

    def cluster(self, map, pos, obj, n=0):
        if n > 0:
            cell = map.getTile(pos)
            if cell.isEmpty():
                cell.addObject(cp.copy(obj))
                n -= 1
            self.cluster(map, rd.choice(
                list(map.getTile(pos).getNeighborhood())).pos, obj, n)

    def distribute(self, map, obj, dx=5, dy=5, margin=1):
        count = 0
        for x in range(self.x[MIN] + margin, self.x[MAX] - margin):
            for y in range(self.y[MIN] + margin, self.y[MAX] - margin):
                if (x % dx == 0) and (y % dy == 0):
                    cell = map.tile[x][y]
                    if cell.isEmpty():
                        cell.addObject(cp.copy(obj))
                        count += 1
        return count

    def describe(self):
        return self.__class__.__name__

    def updateCells(self, map):
        for cell in self.getCells(map):
            cell.room = self
            cell.stack[0] = cell.FLOOR
