from src.globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it

from src.object.object import Object, Obstacle, Barrel, Desk
from src.object.server import Terminal, Server
from src.object.light import Lamp, FlickerLamp, SpotLight
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

    def propagate(self, map, nChildren, size, shapeList):
        # number of child rooms
        for i in range(rd.randint(nChildren[MIN], nChildren[MAX])):
            shape = rd.choice(shapeList)

            # number of tries to find a valid child
            for i in range(500):
                direction = rd.choice([UP, DOWN, LEFT, RIGHT])
                alignment = rd.choice([MIN, MAX])

                w = rd.randint(*size)
                h = rd.randint(*size)

                if shape is 'Corridor':
                    if direction in [UP, DOWN]:
                        w = 5
                        h = int(1.5*rd.randint(*size))
                    else:
                        w = int(1.5*rd.randint(*size))
                        h = 5

                if shape is 'Dome':
                    w = rd.randint(*size)
                    h = w

                offset = np.array(self.getOffset(direction, alignment, w, h))
                rect = Rectangle(self.pos + offset, w, h)

                for room in map.getRooms():
                    if rect is not None:
                        if rect.intersects(room) or not map.contains(rect):
                            rect = None
                            break

                if rect is not None:
                    break

            if rect is not None:
                roomClass = globals()[shape]
                nextRoom = roomClass(self.tier + 1, self, rect.pos, rect.size[X], rect.size[Y])
                self.children.append(nextRoom)
                map.tier[self.tier + 1].append(nextRoom)
                nextRoom.carve(map)

                # carve a connection
                if direction in (UP, DOWN):
                    map.carveDoorway(nextRoom, self, self.tier, not rect.size[X] < self.size[X])
                elif direction in (LEFT, RIGHT):
                    map.carveDoorway(nextRoom, self, self.tier, rect.size[Y] < self.size[Y])
        return self.children

    def getOffset(self, direction, alignment, w, h):
        if (direction, alignment) == (UP, MIN):
            return [0, -h]
        elif (direction, alignment) == (UP, MAX):
            return [self.size[X] - w, -h]
        elif (direction, alignment) == (RIGHT, MIN):
            return [self.size[X], 0]
        elif (direction, alignment) == (RIGHT, MAX):
            return [self.size[X], self.size[Y] - h]
        elif (direction, alignment) == (DOWN, MIN):
            return [0, self.size[Y]]
        elif (direction, alignment) == (DOWN, MAX):
            return [self.size[X] - w, self.size[Y]]
        elif (direction, alignment) == (LEFT, MIN):
            return [-w, 0]
        elif (direction, alignment) == (LEFT, MAX):
            return [-w, self.size[Y] - h]

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
        map.getTile(self.randomSpot(3)).addObject(Lamp())
        Server(map.getTile(self.randomSpot()))

        NPC(map.getTile(self.randomSpot(3)), map.main)

        self.scatter(map, Obstacle(), rd.randint(0, 1))
        self.scatter(map, Barrel(), rd.randint(1, 2))
        self.scatter(map, Key(tier=rd.randint(3, 5)), rd.randint(0, 1))

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

class Corridor(Room):
    def __init__(self, tier, parent, pos, w, h):
        Room.__init__(self, tier, parent, pos, w, h)

    def generateContent(self, map):
        map.getTile(self.center).addObject(Lamp())

    def carve(self, map):
        pass

class Office(Room):
    def __init__(self, tier, parent, pos, w, h):
        Room.__init__(self, tier, parent, pos, w, h)

    def generateContent(self, map):
        deskTile = map.getTile(self.randomSpot(3))
        neighbors = filter(lambda c: not c.wall, deskTile.getNeighborhood())
        rd.shuffle(neighbors)

        try:
            for cell in ([deskTile] + neighbors)[0:3]:
                cell.addObject(cp.deepcopy(Desk()))
        except IndexError:
            pass

        self.scatter(map, Lamp(), margin=2)

class Hall(Room):
    def __init__(self, tier, parent, pos, w, h):
        Room.__init__(self, tier, parent, pos, w, h)

    def generateContent(self, map):
        offset = (2*(self.center - self.pos) // 3).round().astype('int')
        pos = self.pos - (offset/2).round().astype('int')

        for x in range(self.x[MIN] + 3, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 1):
                if (x - pos[X]) % offset[X] == 0 and (y - pos[Y]) % offset[Y] == 0:
                    map.tile[x][y].addObject(FlickerLamp())

        for x in range(self.x[MIN] + 3, self.x[MAX] - 3):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 3):
                if x % 3 == 0 and y % 5 != 0:
                    cell = map.tile[x][y]
                    if cell.isEmpty():
                        Server(cell)

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

        offset = (2*(self.center - self.pos) // 3).round().astype('int')

        for x in range(self.x[MIN] + 3, self.x[MAX] - 3):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 3):
                if (x - self.pos[X]) % offset[X] == 0 and (y - self.pos[Y]) % offset[Y] == 0:
                    map.tile[x][y].makeWall()


class Dome(Room):
    def __init__(self, tier, parent, pos, w, h):
        Room.__init__(self, tier, parent, pos, w, h)

    def generateContent(self, map):
        offset = (2*(self.center - self.pos) // 3).round().astype('int')
        pos = self.pos - (offset/2).round().astype('int')

        for x in range(self.x[MIN] + 3, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 3, self.y[MAX] - 1):
                if (x - pos[X]) % offset[X] == 0 and (y - pos[Y]) % offset[Y] == 0:
                    map.tile[x][y].addObject(Lamp())

        for i in range(rd.randint(4,8)):
            self.cluster(map, self.randomSpot(3), rd.choice([Barrel(), Obstacle()]), rd.randint(2,12))

    def carve(self, map):
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
    def __init__(self, tier, parent, pos, w, h):
        Room.__init__(self, tier, parent, pos, w, h)

    def generateContent(self, map):
        map.getTile(self.center).addObject(PlotDevice())
