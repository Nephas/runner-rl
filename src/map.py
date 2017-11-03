from globals import *

import math as m
import numpy as np
import random as rd
import itertools as it
from room import Room, Rectangle, Wall
from object import Object, Obstacle, Lamp
from door import Vent, SecDoor, AutoDoor
from item import Item, Key
from actor import Actor


class Map:
    def __init__(self, main=None):
        self.main = main
        self.tier = [[]]
        self.tile = [[Cell(self, [x, y]) for y in range(MAP[HEIGHT])]
                     for x in range(MAP[WIDTH])]

    def getTile(self, pos):
        return self.tile[pos[X]][pos[Y]]

    def generateLevel(self):
        stats = {'ROOMS': 0, 'VENTS': 0, 'CORRIDORS': 0, 'DEADENDS': 0}

        # create boss room
        w = rd.randint(ROOM_SIZE[0][MIN], ROOM_SIZE[0][MAX])
        h = rd.randint(ROOM_SIZE[0][MIN], ROOM_SIZE[0][MAX])
        margin = 32
        pos = [rd.randint(margin, MAP[WIDTH] - w - margin),
               rd.randint(margin, MAP[HEIGHT] - h - margin)]
        self.tier[0].append(Room(0, None, Rectangle(pos, w, h)))
        self.tier[0][0].carve(self)

        # create rooms
        for i in range(1, len(ROOM_SIZE)):
            self.tier.append([])
            for room in self.tier[i - 1]:
                room.propagate(self, N_CHILD[i], ROOM_SIZE[i], ROOM_TYPE[i])

        # carve vents
        for pair in it.combinations(self.tier[-1], 2):
            if rd.randint(0, 2) <= 2:
                if np.linalg.norm(pair[0].rectangle.center - pair[1].rectangle.center) < MAP[WIDTH] / 3:
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
            for x in range(0, MAP[WIDTH]):
                for y in range(0, MAP[HEIGHT]):
                    if self.tile[x][y].wall:
                        for cell in self.getNeighborhood([x, y]):
                            if cell.wall is None:
                                cells.append(cell)
            for cell in cells:
                cell.wall = True

        for x in range(0, MAP[WIDTH]):
            for y in range(0, MAP[HEIGHT]):
                if self.tile[x][y].wall:
                    self.tile[x][y].makeWall()

        # scatter things
        self.updatePhysics()

        for tier in self.tier:
            for room in tier:
                count = room.distribute(self, Lamp(), rd.randint(12, 20), rd.randint(12, 20))
                if count == 0:
                    self.getTile(room.randomSpot()).addObject(Lamp())

                room.scatter(self, Obstacle(), rd.randint(1, 5))
                room.scatter(self, Key(tier=rd.randint(3,5)), 1)
                self.getTile(room.randomSpot()).addObject(
                    Actor(None, self.main))
            room = rd.choice(tier)
            room.scatter(self, Key(tier=room.tier-1), 1)

        # set start and extraction rooms
        start = rd.choice(self.tier[-1])
        start.function = "start"
        self.getTile(start.getCenter()).addObject(player)

        exRooms = filter(lambda r: r.function is None, self.tier[-1])
        rd.shuffle(exRooms)
        for i in range(3):
            exRooms.pop().function = "extraction"

    def updatePhysics(self):
        for cell in self.main.gui.mapCells:
            cell.light = 2
            cell.vision[LOS] = False

        self.castFov(self.main.player.cell.pos)

        for cell in self.main.gui.mapCells:
            cell.updatePhysics()

    def updateRender(self):
        for cell in self.main.gui.mapCells:
            cell.updateRender()

    def carveTunnel(self, room1, room2, direction, tunnelTier=-1, door=False, vent=False):
        positions = []
        pos1 = room1.getCenter()
        pos2 = room2.getCenter()

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
            if pos in room1.rectangle.border() or pos in room2.rectangle.border():
                crossings += 1
            for tier in self.tier:
                for room in tier:
                    if room is not room1 and room is not room2:
                        if room.rectangle.contains(pos):
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
                if not pos in room1.rectangle.border() or pos in room2.rectangle.border():
                    for cell in self.getNeighborhood(pos):
                        cell.removeWall()
                        cell.tier = room2.tier

        # place doors and vents
        for pos in positions:
            cell = self.getTile(pos)
            if pos in room1.rectangle.border():
                if vent and cell.isEmpty():
                    cell.addObject(Vent())
                if door:
                    cell.addObject(SecDoor(tier=tunnelTier))
            if pos in room2.rectangle.border():
                if vent and cell.isEmpty():
                    cell.addObject(Vent())

            # walls for vent tunnels
            for cell in self.getNeighborhood(pos):
                if cell.wall is None:
                    cell.makeWall()

        room1.updateTier(self)
        room2.updateTier(self)
        return True

    def getNeighborhood(self, pos, shape=None):
        positions = [pos + np.array([0, -1]), pos + np.array([1, 0]),
                     pos + np.array([0, 1]), pos + np.array([-1, 0])]
        return map(lambda p: self.getTile(p), filter(lambda p: self.contains(p), positions))

    def contains(self, pos):
        return pos[X] in range(0, MAP[WIDTH]) and pos[Y] in range(0, MAP[HEIGHT])

    def castFov(self, pos):
        for n in NEIGHBORHOOD:
            self.getTile(pos + n).vision = [True, True]

        blockIndex = 0
        blockPoint = [0, 0]

        for line in self.main.render.raymap:
            if not all(line[blockIndex] == blockPoint):
                for i, point in enumerate(line):
                    if not self.getTile(point + pos).block[LOS]:
                        for n in NEIGHBORHOOD:
                            self.getTile(point + pos + n).vision = [True, True]
                    else:
                        blockIndex = i
                        blockPoint = point
                        break

    def castLight(self, pos):
        self.getTile(pos).light = 16

        for line in self.main.render.lightmap:
            for i, point in enumerate(line):
                cell = self.getTile(point + pos)
                if not cell.block[LOS]:
                    cell.light = max(16 - 2*i, cell.light)
                else:
                    break


class Cell:
    def __init__(self, map, pos, wall=None):
        self.map = map
        self.pos = np.array(pos)
        self.wall = wall
        self.tier = -1
        self.light = 2

        # [MOVE, LOS]
        self.block = [False, False]
        self.vision = [False, False]

        self.object = []

        # graphics attributes
        self.char = ' '
#        self.fog = '0'
        self.bg = BLACK
        self.fg = WHITE

    def addObject(self, obj):
        self.object.append(obj)
        obj.cell = self

    def isEmpty(self):
        return self.object == [] and not self.wall

    def updateRender(self):
        if not self.vision[EXP]:
            return

        if not self.vision[LOS]:
            self.fg = (25, 25, 25)
            self.bg = (10, 10, 10)
            return

        if self.wall:
            self.bg = (40, 40, 40)
            self.fg = (85, 85, 85)
            return

        self.char = ' '
        self.bg = tuple(self.light * TIERCOLOR[self.tier] / 16)
        if self.tier == -1:
            self.bg = (40, 40, 40)

        for object in self.object:
            self.char = object.char
            self.fg = object.fg

    def makeWall(self):
        self.object = []
        self.wall = True
        self.block = [True, True]
        self.char = Wall.getChar(self.pos, self.map)

    def removeWall(self):
        self.object = []
        self.wall = False
        self.block = [False, False]
        self.char = ' '

    def updatePhysics(self):
        self.block = [False, False]
        if self.wall:
            self.block[MOVE] = True
            self.block[LOS] = True
        for obj in self.object:
            if obj.block[MOVE]:
                self.block[MOVE] = True
            if obj.block[LOS]:
                self.block[LOS] = True
            obj.physics(self.map)

    def draw(self, window, pos):
        if self.vision[EXP]:
            window.draw_char(pos[X], pos[Y], self.char, self.fg, self.bg)

    def drawHighlight(self, window, pos, color=WHITE):
        if self.vision[EXP]:
            window.draw_char(pos[X], pos[Y], self.char, self.fg, color)
        else:
            window.draw_char(pos[X], pos[Y], ' ', self.fg, color)

#        elif self.wall is None:
#            window.draw_char(pos[X], pos[Y], self.fog, self.fg, BLACK)
