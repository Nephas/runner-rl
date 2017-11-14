from src.globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it

from src.level.map import Map, Rectangle
from src.level.room import Room

from src.object.object import Object, Obstacle
from src.object.server import Terminal, Server
from src.object.light import Lamp, DoorLamp
from src.object.item import Item, Key
from src.object.door import Vent, SecDoor, AutoDoor

from src.render import Render
from src.actor.actor import Player, Actor


class Level(Map):
    ROOM_SIZE = [[10, 20], [5, 15], [20, 40], [20, 30], [10, 20], [7, 15]]
    N_CHILD = [[0, 0], [1, 1], [2, 4], [2, 4], [3, 4], [4, 6]]
    ROOM_TYPE = [['Room'], ['Corridor'], ['Corridor'], [
        'Corridor', 'Dome', 'Hall'], ['Corridor', 'Room'], ['Room']]

    def __init__(self, main=None):
        Map.__init__(self, main)

        self.tier = [[]]
        self.forbidden = []

    def contains(self, target):
        """Returns whether the target is fully contained inside the map, excluding the forbidden regions.
        Takes 2D pos lists and Rectangle objects
        """
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

    def generate(self, seed):
        rd.seed(seed)

        self.generateShape()
        self.generateStart()

        stats = {'DEADENDS': -1, 'VENTS': - 1}
        while stats['VENTS'] < 5 or stats['ROOMS'] < 10:
            self.map = Level(self)
            self.generateRooms()
            self.generateVents()

            stats = self.countMetrics()
            print(stats)

        self.finalize()

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
        """Propagate every single room according to the N_CHILD and ROOM_SIZE specifications."""
        # recursively spread room
        Render.printImage(self, "gif/levelgen{:02}.bmp".format(0))

        for i in range(1, len(Level.ROOM_TYPE)):
            Render.printImage(self, "gif/levelgen{:02}.bmp".format(i))

            self.tier.append([])
            for j, room in enumerate(self.tier[i - 1]):
                room.propagate(
                    self, Level.N_CHILD[i], Level.ROOM_SIZE[i], Level.ROOM_TYPE[i])

        # extend boss room
        self.tier[0][0].propagate(self, [2, 4], [7, 10], ['Room'])
        Render.printImage(self, "gif/levelgen90.bmp")

        # remove deadends
        for tier in reversed(self.tier):
            for room in tier:
                if room.__class__.__name__ is 'Corridor' and room.children == []:
                    room.fill(self)
                    tier.remove(room)
        Render.printImage(self, "gif/levelgen91.bmp")

    def generateVents(self):
        for pair in it.combinations(self.tier[-1] + self.tier[-2], 2):
            if pair[0] not in pair[1].children and pair[1] not in pair[0].children:
                if np.linalg.norm(pair[0].center - pair[1].center) < Map.WIDTH / 3:
                    if not self.carveVent(pair[0], pair[1], True):
                        self.carveVent(pair[0], pair[1], False)

    def countMetrics(self):
        stats = {'ROOMS': 0, 'VENTS': 0, 'CORRIDORS': 0}
        stats['VENTS'] = len(self.getAll('Vent')) / 2
        for tier in self.tier:
            for room in tier:
                stats['ROOMS'] += 1
                if room.__class__.__name__ is 'Corridor':
                    stats['CORRIDORS'] += 1
        return stats

    def finalize(self):
        for x in range(0, Map.WIDTH):
            for y in range(0, Map.HEIGHT):
                if self.contains([x, y]) and not self.tile[x][y].wall is False:
                    self.tile[x][y].makeWall()

        for room in self.getRooms():
            room.carve(self)
            room.updateTier(self)
            room.generateContent(self)

        # connect terminals
        for pair in it.combinations(self.getAll(Server) + self.getAll(Terminal), 2):
            if rd.randint(0, 2) <= 2:
                if np.linalg.norm(pair[0].cell.pos - pair[1].cell.pos) < Map.WIDTH / 8:
                    pair[0].connect(pair[1])
                    self.layCable(pair[0].cell.pos, pair[1].cell.pos)

        # set start and extraction rooms
        start = rd.choice(self.tier[-1])
        start.function = "start"

        player = Player(self.getTile(start.center), self.main)
        self.main.player = player

        exRooms = filter(lambda r: r.function is None, self.tier[-1])
        rd.shuffle(exRooms)
        for i in range(3):
            exRooms.pop().function = "extraction"

        Render.printImage(self, "gif/levelgen99.bmp")

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

        # carve wide tunnels for corridors and circular rooms
#        if room1.__class__.__name__ in ['Corridor', 'Dome'] or room2.__class__.__name__ in ['Corridor', 'Dome']:
        for pos in positions:
            if pos not in room1.border() or pos in room2.border():
                for cell in self.getNeighborhood(pos, shape=8):
                    if list(cell.pos) not in room1.border():
                        cell.removeWall()
                        cell.tier = room2.tier

        # place door and Terminal
        door = SecDoor(tier=tunnelTier)
        for pos in positions:
            cell = self.getTile(pos)
            cell.removeWall()
            cell.tier = tunnelTier
            if pos in room1.border():
                cell.addObject(door)
            if pos in room2.border():
                flag = False
                for cell in self.getNeighborhood(pos, shape=4):
                    if list(cell.pos) in room2.border():
                        if not flag:
                            term = Terminal(cell)
                            term.connect(door)
                            flag = True
                        else:
                            cell.addObject(DoorLamp())
                            break
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
        """Returns a list of position coorinates in a right-angled connection between two points. The third argument
        states whether the connection starts in horizontal or vertical direction.
        """
        if horizontal:            # horizontal first:
            return [[x, pos1[Y]] for x in range(min(pos1[X], pos2[X]), max(
                pos1[X], pos2[X]) + 1)] + [[pos2[X], y] for y in range(min(pos1[Y], pos2[Y]), max(pos1[Y], pos2[Y]) + 1)]
        else:             # vertical first:
            return [[pos1[X], y] for y in range(min(pos1[Y], pos2[Y]), max(
                pos1[Y], pos2[Y]) + 1)] + [[x, pos2[Y]] for x in range(min(pos1[X], pos2[X]), max(pos1[X], pos2[X]) + 1)]
