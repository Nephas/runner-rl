from globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it

from map import Map, Rectangle
from object import Object, Obstacle, Lamp, Terminal
from render import Render
from door import Vent, SecDoor, AutoDoor
from item import Item, Key
from actor import Actor


class Level(Map):
    ROOM_SIZE = [[10, 20], [10, 15], [20, 40], [20, 30], [7, 15]]
    N_CHILD = [[0, 0], [1, 1], [1, 2], [2, 3], [3, 4]]
    ROOM_TYPE = [['Room'], ['Corridor'], ['Corridor'], ['Dome'], ['Room']]

    def __init__(self, main=None):
        Map.__init__(self, main)

        self.tier = [[]]*len(Level.ROOM_TYPE)
        self.forbidden = []

    def contains(self, target):
        """Returns whether the target is fully contained inside the map, excluding the forbidden regions.
        Takes 2D pos lists and Rectangle objects"""
        if target.__class__.__name__ in ['Rectangle', 'Room']:
            for rect in self.forbidden:
                if target.intersects(rect):
                    return False
            return (target.x[MAX] < Map.WIDTH and target.x[MIN] > 0 and target.y[MAX] < Map.HEIGHT and target.y[MIN] > 0)
        else:
            for rect in self.forbidden:
                if rect.contains(target):
                    return False
            return target[X] in range(0, Map.WIDTH) and target[Y] in range(0, Map.HEIGHT)

    def getRooms(self):
        for tier in self.tier:
            for room in tier:
                yield room

    def generate(self):
        print(self.generateShape())

        self.generateStart()
        self.generateRooms()
        self.generateVents()

        return self.countMetrics()

    def generateShape(self):
        shape = rd.choice(['CROSS', 'CORNER', 'RING', 'DUAL'])
        self.forbidden = []
        if shape is 'CORNER':
            self.forbidden = [Rectangle(
                [Map.WIDTH // 3, Map.HEIGHT // 3], 2 * Map.WIDTH // 3, 2 * Map.HEIGHT / 3)]
        elif shape is 'DUAL':
            self.forbidden = [Rectangle([0, 0], Map.WIDTH // 3, Map.HEIGHT // 3),
                              Rectangle([2 * Map.WIDTH // 3, 2 * Map.HEIGHT // 3], Map.WIDTH // 3, Map.HEIGHT // 3)]
        elif shape is 'CROSS':
            self.forbidden = [Rectangle([2 * Map.WIDTH // 3, 2 * Map.HEIGHT // 3], Map.WIDTH // 3, Map.HEIGHT // 3),
                              Rectangle([0, 0], Map.WIDTH //
                                        3, Map.HEIGHT // 3),
                              Rectangle([0, 2 * Map.HEIGHT // 3],
                                        Map.WIDTH // 3, Map.HEIGHT // 3),
                              Rectangle([2 * Map.WIDTH // 3, 0], Map.WIDTH // 3, Map.HEIGHT // 3)]
        elif shape is 'RING':
            self.forbidden = [
                Rectangle([Map.WIDTH // 3, Map.HEIGHT // 3], Map.WIDTH // 3, Map.HEIGHT // 3)]
        return shape

    def generateStart(self):
        w = rd.randint(*Level.ROOM_SIZE[0])
        h = rd.randint(*Level.ROOM_SIZE[0])
        margin = 8

        while True:
            pos = [rd.randint(margin, Map.WIDTH - w - margin),
                   rd.randint(margin, Map.HEIGHT - h - margin)]
            start = Room(0, None, pos, w, h)
            if self.contains(start):
                self.tier[0].append(start)
                start.carve(self)
                break

    def generateRooms(self):
        """Propagate every single room according to the N_CHILD and ROOM_SIZE specifications. If a corridor produces
        a dead end, generation breaks."""
        for i in range(len(self.tier)):
            print i
            for room in self.tier[i]:
                room.propagate(self, Level.N_CHILD[i+1], Level.ROOM_SIZE[i+1], Level.ROOM_TYPE[i+1])

                Render.printImage(self, "levelgen.bmp")
        self.tier[0][0].propagate(self, [2, 4], [7, 10], ['Room'])
        Render.printImage(self, "levelgen.bmp")

    def generateVents(self):
        for pair in it.combinations(self.tier[-1] + self.tier[-2], 2):
            if pair[0] not in pair[1].children and pair[1] not in pair[0].children:
                if np.linalg.norm(pair[0].center - pair[1].center) < Map.WIDTH / 2:
                    if not self.carveVent(pair[0], pair[1], True):
                        self.carveVent(pair[0], pair[1], False)

    def countMetrics(self):
        stats = {'ROOMS': 0, 'VENTS': 0, 'CORRIDORS': 0, 'DEADENDS': 0}
        stats['VENTS'] = len(self.getAll('Vent')) / 2
        for tier in self.tier:
            for room in tier:
                stats['ROOMS'] += 1
                if room.__class__.__name__ is 'Corridor':
                    stats['CORRIDORS'] += 1
                if room.__class__.__name__ is 'Corridor' and room.children == []:
                    stats['DEADENDS'] += 1
        return stats

    def finalize(self, player):
        for x in range(0, Map.WIDTH):
            for y in range(0, Map.HEIGHT):
                if self.contains([x, y]) and not self.tile[x][y].wall is False:
                    self.tile[x][y].wall = True

        for x in range(0, Map.WIDTH):
            for y in range(0, Map.HEIGHT):
                if self.tile[x][y].wall:
                    self.tile[x][y].makeWall()

        for tier in self.tier:
            for room in tier:
                count = room.distribute(
                    self, Lamp(), rd.randint(8, 16), rd.randint(8, 16), 5)
                if count == 0:
                    self.getTile(room.randomSpot()).addObject(Lamp())

                room.scatter(self, Obstacle(), rd.randint(1, 5))
                room.scatter(self, Key(tier=rd.randint(3, 5)),
                             rd.randint(0, 1))
                self.getTile(room.randomSpot()).addObject(
                    Actor(None, self.main))
                room.updateTier(self)
            room = rd.choice(tier)
            room.scatter(self, Key(tier=room.tier - 1), 1)

        # place door terminals
        for door in self.getAll(SecDoor):
            for cell in self.getNeighborhood(door.cell.pos, shape=8):
                if cell.isEmpty() and np.linalg.norm(cell.pos - door.cell.pos) > 1:
                    term = Terminal(cell)
                    term.connect(door)
                    break

        # connect terminals
        for pair in it.combinations(self.getAll(Terminal), 2):
            if rd.randint(0, 2) <= 2:
                if np.linalg.norm(pair[0].cell.pos - pair[1].cell.pos) < Map.WIDTH / 6:
                    pair[0].connect(pair[1])
                    self.layCable(pair[0].cell.pos, pair[1].cell.pos)

        # set start and extraction rooms
        start = rd.choice(self.tier[-1])
        start.function = "start"
        self.getTile(start.center).addObject(player)

        exRooms = filter(lambda r: r.function is None, self.tier[-1])
        rd.shuffle(exRooms)
        for i in range(3):
            exRooms.pop().function = "extraction"

    def layCable(self, pos1, pos2, horizontal=True):
        for pos in self.getConnection(pos1, pos2, horizontal):
            if not self.contains(pos):
                return False
            cell = self.getTile(pos)
            if cell.grid is None:
                cell.grid = False
        return True

    def carveDoorway(self, room1, room2, tunnelTier=-1, horizontal=True):
        positions = self.getConnection(room1.center, room2.center, horizontal)

        # carve connection
        for cell in map(lambda p: self.getTile(p), positions):
            cell.removeWall()
            cell.tier = tunnelTier

        # carve wide tunnels for corridors and circular rooms
        if (room1.__class__.__name__ is 'Corridor' and room2.__class__.__name__ is 'Corridor') or room1.__class__.__name__ is 'Dome' or room2.__class__.__name__ is 'Dome':
            for pos in positions:
                if pos not in room1.border() or pos in room2.border():
                    for cell in self.getNeighborhood(pos):
                        cell.removeWall()
                        cell.tier = room2.tier

        # place doors
        for pos in positions:
            cell = self.getTile(pos)
            if pos in room1.border():
                cell.addObject(SecDoor(tier=tunnelTier))
        return True

    def carveVent(self, room1, room2, horizontal=True):
        positions = self.getConnection(room1.center, room2.center, horizontal)

        # check if the tunnel crosses a room or border
        crossings = 0
        for pos in positions:
            if not self.contains(pos):
                return False
            if pos in room1.border() or pos in room2.border():
                crossings += 1
            for tier in self.tier:
                for room in tier:
                    if room is not room1 and room is not room2:
                        if room.contains(pos):
                            return False
            if crossings > 2:
                return False
            for neighbor in self.getNeighborhood(pos):
                if neighbor.object != []:
                    return False

        # carve connection
        for cell in map(lambda p: self.getTile(p), positions):
            cell.removeWall()
            cell.tier = -1

        # place vents
        for pos in positions:
            if pos in room1.border():
                self.getTile(pos).addObject(Vent())
            if pos in room2.border():
                self.getTile(pos).addObject(Vent())

            # walls for vent tunnels
            for cell in self.getNeighborhood(pos):
                if cell.wall is None:
                    cell.makeWall()
        return True

    def getConnection(self, pos1, pos2, horizontal=True):
        if horizontal:            # horizontal first:
            return [[x, pos1[Y]] for x in range(min(pos1[X], pos2[X]), max(
                pos1[X], pos2[X]) + 1)] + [[pos2[X], y] for y in range(min(pos1[Y], pos2[Y]), max(pos1[Y], pos2[Y]) + 1)]
        else:             # vertical first:
            return [[pos1[X], y] for y in range(min(pos1[Y], pos2[Y]), max(
                pos1[Y], pos2[Y]) + 1)] + [[x, pos2[Y]] for x in range(min(pos1[X], pos2[X]), max(pos1[X], pos2[X]) + 1)]


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
                        h = rd.randint(*size)
                    else:
                        w = rd.randint(*size)
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
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                if map.tile[x][y].wall is None:
                    map.tile[x][y].makeWall()

        # carve basic rectangle
        for x in range(self.x[MIN] + 1, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 1, self.y[MAX] - 1):
                map.tile[x][y].removeWall()
                map.tile[x][y].tier = self.tier

    def randomSpot(self, margin=1):
        x = rd.randint(self.x[MIN] +
                       margin, self.x[MAX] - margin - 1)
        y = rd.randint(self.y[MIN] +
                       margin, self.y[MAX] - margin - 1)
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


class Dome(Room):
    def __init__(self, tier, parent, pos, w, h):
        Room.__init__(self, tier, parent, pos, w, h)


    def carve(self, map):
        print(self.x,self.y)
        # carve basic rectangle or circle
        for x in range(self.x[MIN] + 1, self.x[MAX] - 1):
            for y in range(self.y[MIN] + 1, self.y[MAX] - 1):
                if np.linalg.norm([x, y] - (self.center - np.array([0.5, 0.5]))) < self.size[X] / 2.0 - 1:
                    map.tile[x][y].removeWall()
                    map.tile[x][y].tier = self.tier
                else:
                    map.tile[x][y].makeWall()
