from globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it

from map import Map
from object import Object, Obstacle, Lamp
from door import Vent, SecDoor, AutoDoor
from item import Item, Key
from actor import Actor


class Level(Map):
    ROOM_SIZE = [[10, 20], [5, 5], [10, 20], [
    15, 30], [20, 40], [10, 15], [10, 15]]
    N_CHILD = [[0, 0], [1, 1], [1, 1], [2, 3], [3, 5], [4, 6], [6, 10]]
    ROOM_TYPE = [["rectangle"], ["gallery"], ["corridor"], ["corridor"], [
    "round", "rectangle", "corridor"], ["rectangle", "square", "corner"], ["rectangle"]]

    def __init__(self, main=None):
        Map.__init__(self, main)

        self.tier = [[]]

    def generate(self):
        stats = {'ROOMS': 0, 'VENTS': 0, 'CORRIDORS': 0, 'DEADENDS': 0}

        # create boss room
        w = rd.randint(Level.ROOM_SIZE[0][MIN], Level.ROOM_SIZE[0][MAX])
        h = rd.randint(Level.ROOM_SIZE[0][MIN], Level.ROOM_SIZE[0][MAX])
        margin = 32
        pos = [rd.randint(margin, Map.WIDTH - w - margin),
               rd.randint(margin, Map.HEIGHT - h - margin)]
        self.tier[0].append(Room(0, None, pos, w, h))
        self.tier[0][0].carve(self)

        # create rooms
        for i in range(1, len(Level.ROOM_SIZE)):
            self.tier.append([])
            for room in self.tier[i - 1]:
                room.propagate(self, Level.N_CHILD[i], Level.ROOM_SIZE[i], Level.ROOM_TYPE[i])

        # carve vents
        for pair in it.combinations(self.tier[-1], 2):
            if rd.randint(0, 2) <= 2:
                if np.linalg.norm(pair[0].center - pair[1].center) < Map.WIDTH / 3:
                    if self.carveTunnel(pair[0], pair[1], "horizontal", vent=True):
                        stats['VENTS'] += 1
                    elif self.carveTunnel(pair[0], pair[1], "vertical", vent=True):
                        stats['VENTS'] += 1

        # count dungeon metrics
        for tier in self.tier:
            for room in tier:
                stats['ROOMS'] += 1
                if room.shape in ["corridor", "gallery"]:
                    stats['CORRIDORS'] += 1
                if room.shape in ["corridor", "gallery"] and room.children == []:
                    stats['DEADENDS'] += 1
        return stats

    def finalize(self, player):
        # smooth out level walls
        for i in range(2):
            cells = []
            for x in range(0, Map.WIDTH):
                for y in range(0, Map.HEIGHT):
                    if self.tile[x][y].wall:
                        for cell in self.getNeighborhood([x, y]):
                            if cell.wall is None:
                                cells.append(cell)
            for cell in cells:
                cell.wall = True

        for x in range(0, Map.WIDTH):
            for y in range(0, Map.HEIGHT):
                if self.tile[x][y].wall:
                    self.tile[x][y].makeWall()

        # scatter things
        self.updatePhysics()

        for tier in self.tier:
            for room in tier:
                count = room.distribute(
                    self, Lamp(), rd.randint(12, 20), rd.randint(12, 20))
                if count == 0:
                    self.getTile(room.randomSpot()).addObject(Lamp())

                room.scatter(self, Obstacle(), rd.randint(1, 5))
                room.scatter(self, Key(tier=rd.randint(3, 5)),
                             rd.randint(0, 1))
                self.getTile(room.randomSpot()).addObject(
                    Actor(None, self.main))
            room = rd.choice(tier)
            room.scatter(self, Key(tier=room.tier - 1), 1)

        # set start and extraction rooms
        start = rd.choice(self.tier[-1])
        start.function = "start"
        self.getTile(start.center).addObject(player)

        exRooms = filter(lambda r: r.function is None, self.tier[-1])
        rd.shuffle(exRooms)
        for i in range(3):
            exRooms.pop().function = "extraction"

    def carveTunnel(self, room1, room2, direction, tunnelTier=-1, door=False, vent=False):
        positions = []
        pos1 = room1.center
        pos2 = room2.center

        # get the positions along the tunnel
        if direction is "horizontal":            # horizontal first:
            positions = [[x, pos1[Y]] for x in range(min(pos1[X], pos2[X]), max(
                pos1[X], pos2[X]) + 1)] + [[pos2[X], y] for y in range(min(pos1[Y], pos2[Y]), max(pos1[Y], pos2[Y]) + 1)]
        elif direction is "vertical":             # vertical first:
            positions = [[pos1[X], y] for y in range(min(pos1[Y], pos2[Y]), max(
                pos1[Y], pos2[Y]) + 1)] + [[x, pos2[Y]] for x in range(min(pos1[X], pos2[X]), max(pos1[X], pos2[X]) + 1)]

        # check if the tunnel crosses a room or border
        crossings = 0
        for pos in positions:
            if pos in room1.border() or pos in room2.border():
                crossings += 1
            for tier in self.tier:
                for room in tier:
                    if room is not room1 and room is not room2:
                        if room.contains(pos):
                            return False
            if crossings > 2:
                return False

        # carve connection
        for cell in map(lambda p: self.getTile(p), positions):
            cell.removeWall()
            cell.tier = tunnelTier

        # carve wide tunnels for corridors and circular rooms
        if (room1.shape in ["corridor", "gallery"] and room2.shape in ["corridor", "gallery"]) or room1.shape is "round" or room2.shape is "round":
            for pos in positions:
                if not pos in room1.border() or pos in room2.border():
                    for cell in self.getNeighborhood(pos):
                        cell.removeWall()
                        cell.tier = room2.tier

        # place doors and vents
        for pos in positions:
            cell = self.getTile(pos)
            if pos in room1.border():
                if vent and cell.isEmpty():
                    cell.addObject(Vent())
                if door:
                    cell.addObject(SecDoor(tier=tunnelTier))
            if pos in room2.border():
                if vent and cell.isEmpty():
                    cell.addObject(Vent())

            # walls for vent tunnels
            for cell in self.getNeighborhood(pos):
                if cell.wall is None:
                    cell.makeWall()

        room1.updateTier(self)
        room2.updateTier(self)
        return True


class Rectangle:  # a rectangle on the map. used to characterize a room.
    def __init__(self, pos, w, h):
        self.pos = np.array(pos)
        self.size = np.array([w, h])
        self.x = [pos[X], pos[X] + w]
        self.y = [pos[Y], pos[Y] + h]
        self.center = (self.pos + self.size / 2).round().astype('int')

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

    def tiles(self):
        positions = []
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                positions.append([x, y])
        return positions

    def inmap(self):
        return (self.x[MAX] < Map.WIDTH and self.x[MIN] > 0 and self.y[MAX] < Map.HEIGHT and self.y[MIN] > 0)


class Room(Rectangle):
    def __init__(self, tier, parent, pos, w, h, shape="rectangle"):
        Rectangle.__init__(self, pos, w, h)
        self.shape = shape
        self.tier = tier
        self.function = None
        self.parent = parent
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
                        offset = [self.size[X] - w, -h]
                elif direction is RIGHT:
                    if alignment is MIN:
                        offset = [self.size[X], 0]
                    elif alignment is MAX:
                        offset = [self.size[X],
                                  self.size[Y] - h]
                elif direction is DOWN:
                    if alignment is MIN:
                        offset = [0, self.size[Y]]
                    elif alignment is MAX:
                        offset = [self.size[X] -
                                  w, self.size[Y]]
                elif direction is LEFT:
                    if alignment is MIN:
                        offset = [-w, 0]
                    elif alignment is MAX:
                        offset = [-w, self.size[Y] - h]

                rectangle = Rectangle(
                    self.pos + np.array(offset), w, h)

                for tier in map.tier:
                    for room in tier:
                        if rectangle is not None:
                            if rectangle.intersects(room) or not rectangle.inmap():
                                rectangle = None

                if rectangle is not None:
                    break

            if rectangle is not None:
                if direction is UP or direction is DOWN:
                    if rectangle.size[X] < self.size[X]:
                        tunnelDirection = "vertical"
                    else:
                        tunnelDirection = "horizontal"
                elif direction is LEFT or direction is RIGHT:
                    if rectangle.size[Y] < self.size[Y]:
                        tunnelDirection = "horizontal"
                    else:
                        tunnelDirection = "vertical"

                nextRoom = Room(self.tier + 1, self, rectangle.pos, rectangle.size[X], rectangle.size[Y], shape)
                self.children.append(nextRoom)
                map.tier[nextRoom.tier].append(nextRoom)
                nextRoom.carve(map)

                if not map.carveTunnel(nextRoom, self, tunnelDirection, self.tier, True):
                    map.carveTunnel(
                        nextRoom, self, not tunnelDirection, self.tier, True)

    def randomSpot(self, margin=1):
        x = rd.randint(self.x[MIN] +
                       margin, self.x[MAX] - margin)
        y = rd.randint(self.y[MIN] +
                       margin, self.y[MAX] - margin)
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
        for x in range(self.x[MIN] + margin, self.x[MAX] - margin):
            for y in range(self.y[MIN] + margin, self.y[MAX] - margin):
                if (x % dx == 0) and (y % dy == 0):
                    cell = map.tile[x][y]
                    if not cell.wall or cell.object != []:
                        cell.addObject(cp.copy(obj))
                        count += 1
        return count

    def updateTier(self, map):
        for x in range(*self.x):
            for y in range(*self.y):
                cell = map.tile[x][y]
                if not cell.wall:
                    cell.tier = self.tier

    def carve(self, map):
        # create a boundary wall
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                if map.tile[x][y].wall is None:
                    map.tile[x][y].makeWall()

        # carve basic rectangle or circle
        for x in range(self.x[MIN] + 1, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 1, self.y[MAX] - 1):
                if self.shape is not "round":
                    map.tile[x][y].removeWall()
                    map.tile[x][y].tier = self.tier
                elif np.linalg.norm([x, y] - (self.center - np.array([0.5, 0.5]))) < self.size[X] / 2.0 - 1:
                    map.tile[x][y].removeWall()
                    map.tile[x][y].tier = self.tier

        if self.shape is "corner":
            cutLen = self.center - self.pos
            cutLen[X] = rd.choice([0, cutLen[X] + 1])
            cutLen[Y] = rd.choice([0, cutLen[Y] + 1])

            cutStart = self.pos + cutLen
            cutEnd = self.center + cutLen

            for x in range(cutStart[X], cutEnd[X]):
                for y in range(cutStart[Y], cutEnd[Y]):
                    map.tile[x][y].wall = True
                    map.tile[x][y].tier = -1
