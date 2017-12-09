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
                [Barrel(), Container()]), rd.randint(2, 12))

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
