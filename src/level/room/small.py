from src.globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it

from src.level.room.room import Room

from src.object.furniture import Container, Barrel, Desk, Hydroponics, Locker
from src.grid.electronics import Terminal, Server, MasterSwitch, Rack
from src.object.lamp import Lamp, FlickerLamp, SpotLight
from src.object.item import Item, Key, PlotDevice
from src.object.door import Outlet

from src.actor.npc import Guard, Worker, Drone


class Corridor(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        guard = Guard(map.getTile(self.randomSpot(1)), map.main)

        self.placeAtWall(map, Locker())
        map.getTile(self.center).addObject(Lamp())

    def carve(self, tileMap):
        self.updateCells(tileMap)

        # create a boundary wall
        for cell in map(lambda p: tileMap.getTile(p), self.border()):
            if cell.wall is None:
                cell.makeWall()


class Lobby(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        self.placeAtWall(map, Server())
        self.placeAtWall(map, MasterSwitch())
        self.placeAtWall(map, Outlet())

        guard = Guard(map.getTile(self.randomSpot(1)), map.main)

        map.getTile(self.center).addObject(Lamp())


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
                desk = Desk()
                cell.addObject(desk)
        except IndexError:
            pass

        Worker(map.getTile(self.randomSpot(2)), map.main)
        self.scatter(map, Key(tier=rd.randint(3, 5)), rd.randint(0, 1))
        self.scatter(map, Lamp(), margin=2)
        self.scatter(map, Barrel())


class Lab(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        self.placeAtWall(map, Server())
        self.placeAtWall(map, MasterSwitch())

        for i in range(3):
            deskTile = self.placeAtWall(map, Desk())
            neighbors = filter(lambda c: not c.wall,
                               deskTile.getNeighborhood())
            rd.shuffle(neighbors)
            for cell in neighbors:
                cell.addObject(cp.deepcopy(Desk()))

        Worker(map.getTile(self.randomSpot(2)), map.main)
        self.scatter(map, Lamp(), margin=2)


class Vault(Room):
    def __init__(self, pos, w, h, tier, parent):
        Room.__init__(self, pos, w, h, tier, parent)

    def generateContent(self, map):
        map.getTile(self.center).addObject(PlotDevice())
