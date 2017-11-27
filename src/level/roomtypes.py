from src.globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it

from src.level.room import Room

from src.object.object import Object, Obstacle, Barrel, Desk, Hydroponics
from src.object.server import Terminal, Server, MasterSwitch, Rack
from src.object.light import Lamp, FlickerLamp, SpotLight
from src.object.item import Item, Key, PlotDevice

from src.actor.npc import Guard, Worker


class Corridor(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        Guard(map.getTile(self.randomSpot(1)), map.main)
        map.getTile(self.center).addObject(Lamp())

    def carve(self, map):
        self.updateCells(map)
        pass


class Office(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        self.placeAtWall(map, Server())
        self.placeAtWall(map, MasterSwitch())

        deskTile = map.getTile(self.randomSpot(2))
        neighbors = filter(lambda c: not c.wall, deskTile.getNeighborhood())
        rd.shuffle(neighbors)

        try:
            for cell in ([deskTile] + neighbors)[0:3]:
                cell.addObject(cp.deepcopy(Desk()))
        except IndexError:
            pass

        Worker(map.getTile(self.randomSpot(2)), map.main)
        self.scatter(map, Key(tier=rd.randint(3, 5)), rd.randint(0, 1))
        self.scatter(map, Lamp(), margin=2)


class Lab(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        self.placeAtWall(map, Server())
        self.placeAtWall(map, MasterSwitch())

        for i in range(3):
            deskTile = self.placeAtWall(map, Desk())
            neighbors = filter(lambda c: not c.wall, deskTile.getNeighborhood())
            rd.shuffle(neighbors)
            for cell in neighbors:
                cell.addObject(cp.deepcopy(Desk()))

        Worker(map.getTile(self.randomSpot(2)), map.main)
        self.scatter(map, Lamp(), margin=2)


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
        self.updateCells(map)

        # create a boundary wall
        for cell in self.getCells(map):
            if cell.wall is None:
                cell.makeWall()

        # carve basic rectangle
        for x in range(self.x[MIN] + 1, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 1, self.y[MAX] - 1):
                map.tile[x][y].removeWall()
                map.tile[x][y].tier = self.tier

        offset = (2 * (self.center - self.pos) // 3).round().astype('int')

        for x in range(self.x[MIN] + 3, self.x[MAX] - 3):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 3):
                if (x - self.pos[X]) % offset[X] == 0 and (y - self.pos[Y]) % offset[Y] == 0:
                    map.tile[x][y].makeWall()


class ServerFarm(Hall):
    def __init__(self, pos, w, h, tier, parent):
        Hall.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        offset = (2 * (self.center - self.pos) // 3).round().astype('int')
        pos = self.pos - (offset / 2).round().astype('int')

        for x in range(self.x[MIN] + 3, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 1):
                if (x - pos[X]) % offset[X] == 0 and (y - pos[Y]) % offset[Y] == 0:
                    map.tile[x][y].addObject(FlickerLamp())

        for x in range(self.x[MIN] + 3, self.x[MAX] - 3):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 3):
                if x % 3 == 0 and y % 5 != 0:
                    cell = map.tile[x][y]
                    if cell.isEmpty():
                        Rack(cell)


class GreenHouse(Hall):
    def __init__(self, pos, w, h, tier, parent):
        Hall.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        offset = (2 * (self.center - self.pos) // 3).round().astype('int')
        pos = self.pos - (offset / 2).round().astype('int')

        for x in range(self.x[MIN] + 3, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 1):
                if (x - pos[X]) % offset[X] == 0 and (y - pos[Y]) % offset[Y] == 0:
                    map.tile[x][y].addObject(FlickerLamp())

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
        offset = (2 * (self.center - self.pos) // 3).round().astype('int')
        pos = self.pos - (offset / 2).round().astype('int')

        for x in range(self.x[MIN] + 3, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 1):
                if (x - pos[X]) % offset[X] == 0 and (y - pos[Y]) % offset[Y] == 0:
                    map.tile[x][y].addObject(FlickerLamp())

        for i in range(rd.randint(4, 8)):
            self.cluster(map, self.randomSpot(3), rd.choice(
                [Barrel(), Obstacle()]), rd.randint(2, 12))


class Dome(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

        self.radius = w // 2

    def generateContent(self, map):
        offset = (2 * (self.center - self.pos) // 3).round().astype('int')
        pos = self.pos - (offset / 2).round().astype('int')

        r = self.radius - 1

        for phi in np.linspace(0, 2. * np.pi, 8)[1:]:
            pos = (self.center + r *
                   np.array([np.cos(phi), np.sin(phi)])).astype('int')
            map.getTile(pos).addObject(SpotLight(direction=phi + np.pi))

        for i in range(rd.randint(4, 8)):
            self.cluster(map, self.randomSpot(3), rd.choice(
                [Barrel(), Obstacle()]), rd.randint(2, 12))

    def carve(self, map):
        self.updateCells(map)

        # create a boundary wall
        for cell in self.getCells(map):
            if cell.wall is None:
                cell.makeWall()

        # carve basic rectangle or circle
        for x in range(self.x[MIN] + 1, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 1, self.y[MAX] - 1):
                if np.linalg.norm([x, y] - (self.center - np.array([0.5, 0.5]))) < self.size[X] / 2.0 - 1:
                    map.tile[x][y].removeWall()
                    map.tile[x][y].tier = self.tier


class BossRoom(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        map.getTile(self.center).addObject(PlotDevice())
