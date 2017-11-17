from src.globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it

from src.object.object import Object, Obstacle, Barrel, Desk
from src.object.server import Terminal, Server
from src.object.door import Vent, SecDoor, AutoDoor
from src.object.item import Item, Key, PlotDevice

from src.actor.actor import Actor, NPC

from src.render import Render
from src.level.map import Rectangle


class Room(Rectangle):
    def __init__(self, tier, parent, pos, w, h):
        Rectangle.__init__(self, pos, w, h)
        self.tier = tier
        self.function = None
        self.parent = parent
        self.children = []

    def carve(self, map):
        # create a boundary wall
        for cell in self.getCells(map):
            if cell.wall is None:
                cell.makeWall()

        # carve basic rectangle
        for x in range(self.x[MIN] + 1, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 1, self.y[MAX] - 1):
                map.tile[x][y].removeWall()
                map.tile[x][y].tier = self.tier

    def fill(self, map):
        for cell in self.getCells(map):
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
        while i < n:
            cell = map.getTile(self.randomSpot(margin))
            if cell.isEmpty():
                cell.addObject(cp.deepcopy(obj))
                i += 1

    def cluster(self, map, pos, obj, n = 0):
        if n > 0:
            cell = map.getTile(pos)
            if cell.isEmpty():
                cell.addObject(cp.deepcopy(obj))
                n -= 1
            self.cluster(map, rd.choice(map.getNeighborhood(pos)).pos, obj, n)

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

    def updateTier(self, map):
        for cell in self.getCells(map):
            if not cell.wall:
                cell.tier = self.tier
