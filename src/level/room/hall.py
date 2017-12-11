from src.globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it

from src.level.room.room import Room

from src.object.furniture import Container, Barrel, Desk, Hydroponics
from src.grid.electronics import Terminal, Server, MasterSwitch, Rack
from src.object.lamp import Lamp, FlickerLamp, SpotLight
from src.object.item import Item, Key, PlotDevice

from src.actor.npc import Guard, Worker, Drone


class Hall(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        offset = (2 * (self.center - self.pos) // 3).round().astype('int')
        pos = self.pos - (offset / 2).round().astype('int')

        for x in range(self.x[MIN] + 3, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 1):
                if (x - pos[X]) % offset[X] == 0 and (y - pos[Y]) % offset[Y] == 0:
                    map.tile[x][y].addObject(FlickerLamp())

    def carve(self, map):
        super(Hall, self).carve(map)

        offset = (2 * (self.center - self.pos) // 3).round().astype('int')
        for x in range(self.x[MIN] + 3, self.x[MAX] - 3):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 3):
                if (x - self.pos[X]) % offset[X] == 0 and (y - self.pos[Y]) % offset[Y] == 0:
                    map.tile[x][y].makeWall()


class ServerFarm(Hall):
    def __init__(self, pos, w, h, tier, parent):
        Hall.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        super(ServerFarm, self).generateContent(map)

        for x in range(self.x[MIN] + 3, self.x[MAX] - 3):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 3):
                if x % 3 == 0 and y % 5 != 0:
                    cell = map.tile[x][y]
                    if cell.isEmpty():
                        Rack(cell)

        for i in range(rd.randint(2, 5)):
            Drone(map.getTile(self.randomSpot(2)), map.main)


class GreenHouse(Hall):
    def __init__(self, pos, w, h, tier, parent):
        Hall.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        super(GreenHouse, self).generateContent(map)

        for x in range(self.x[MIN] + 3, self.x[MAX] - 3):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 3):
                if (x % 4 in [0, 1, 2]) and y % 5 != 0:
                    cell = map.tile[x][y]
                    if cell.isEmpty():
                        cell.addObject(Hydroponics())


class Storage(Hall):
    def __init__(self, pos, w, h, tier, parent):
        Hall.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        super(Storage, self).generateContent(map)

        for x in range(self.x[MIN] + 3, self.x[MAX] - 3):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 3):
                if (x % 4 in [0, 1, 2]) and y % 5 != 0:
                    cell = map.tile[x][y]
                    if cell.isEmpty() and not rd.randint(1,4) == 1:
                        cell.addObject(Container())

#        for i in range(rd.randint(4, 8)):
#            self.cluster(map, self.randomSpot(3), rd.choice(
#                [Barrel(), Obstacle()]), rd.randint(2, 12))
