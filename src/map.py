from globals import *

import math as m
import numpy as np
import random as rd
import itertools as it
from room import Room, Rectangle
from object import Object, Vent, Door, Obstacle, Lamp


class Map:
    def __init__(self, parent=None):
        self.parent = parent
        self.tile = [[Cell(self, [x, y]) for y in range(MAP[HEIGHT])]
                     for x in range(MAP[WIDTH])]
        self.tier = [[]]
        self.updateRender()

    def getTile(self, pos):
        return self.tile[pos[X]][pos[Y]]

    def generateLevel(self):
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
        nVents = 0
        nCorridor = 0
        nRooms = 0
        nDeadend = 0
        for pair in it.combinations(self.tier[-1], 2):
            if rd.randint(0, 2) <= 2:
                if distance(pair[0].rectangle.center, pair[1].rectangle.center) < MAP[WIDTH] / 3:
                    carved = self.carveTunnel(
                        pair[0], pair[1], "horizontal", -2, vent=True)
                    if not carved:
                        carved = self.carveTunnel(
                            pair[0], pair[1], "vertical", -2, vent=True)
                    if carved:
                        nVents += 1

        # count dungeon metrics
        for tier in self.tier:
            for room in tier:
                nRooms += 1
                if room.shape in ["corridor", "gallery"]:
                    nCorridor += 1
                if room.shape in ["corridor", "gallery"] and room.children == []:
                    nDeadend += 1
        return {'ROOMS': nRooms, 'VENTS': nVents, 'CORRIDORS': nCorridor, 'DEADENDS': nDeadend}

    def finalize(self, player):
        # smooth out level walls
        for i in range(1, 6):
            cells = []
            for x in range(0, MAP[WIDTH]):
                for y in range(0, MAP[HEIGHT]):
                    if self.tile[x][y].wall:
                        for cell in self.getNeighborhood([x, y]):
                            if cell.wall is None:
                                cells.append(cell)
            for cell in cells:
                cell.wall = True

        self.updatePhysics()

        for tier in self.tier:
            for room in tier:
                room.scatter(self, Obstacle(), rd.randint(1, 5))
                room.distribute(self, Lamp(), rd.randint(
                    3, 8), rd.randint(3, 8))

        # set start and extraction rooms
        start = rd.choice(self.tier[-1])
        start.function = "start"
        self.getTile(start.getCenter()).addObject(player)
        nExtraction = 3
        while nExtraction > 0:
            room = rd.choice(self.tier[-1])
            if room.function is None:
                room.function = "extraction"
                nExtraction -= 1


    def updatePhysics(self, x=[0, MAP[WIDTH]], y=[0, MAP[HEIGHT]]):
        for i in range(x[MIN], x[MAX]):
            for j in range(y[MIN], y[MAX]):
                cell = self.tile[i][j]
                cell.light = 2
                cell.vision[LOS] = False

        for i in range(x[MIN], x[MAX]):
            for j in range(y[MIN], y[MAX]):
                self.tile[i][j].updatePhysics()

    def updateRender(self, x=[0, MAP[WIDTH]], y=[0, MAP[HEIGHT]]):
        if self.parent.player is not None:
            self.castFov(self.parent.player.cell.pos)

        for i in range(x[MIN], x[MAX]):
            for j in range(y[MIN], y[MAX]):
                self.tile[i][j].updateRender()

    def carveTunnel(self, room1, room2, direction, tunnelTier=-1, door=False, vent=False):
        valid = True

        if vent:
            tunnelTier = -1

        positions = []
        pos1 = room1.getCenter()
        pos2 = room2.getCenter()

        # get the positions along the tunnel
        if direction is "horizontal":            # horizontal first:
            for x in range(min(pos1[X], pos2[X]), max(pos1[X], pos2[X]) + 1):
                positions.append([x, pos1[Y]])
            for y in range(min(pos1[Y], pos2[Y]), max(pos1[Y], pos2[Y]) + 1):
                positions.append([pos2[X], y])
        elif direction is "vertical":             # vertical first:
            for y in range(min(pos1[Y], pos2[Y]), max(pos1[Y], pos2[Y]) + 1):
                positions.append([pos1[X], y])
            for x in range(min(pos1[X], pos2[X]), max(pos1[X], pos2[X]) + 1):
                positions.append([x, pos2[Y]])

        # check if the tunnel crosses a room or border
        crossings = 0
        for pos in positions:
            if pos in room1.rectangle.border() or pos in room2.rectangle.border():
                crossings += 1
            for tier in self.tier:
                for room in tier:
                    if room is not room1 and room is not room2:
                        if room.rectangle.contains(pos):
                            valid = False
            if crossings > 2:
                valid = False

        if valid:
            # carve connection
            for pos in positions:
                if self.tile[pos[X]][pos[Y]].wall or self.tile[pos[X]][pos[Y]].wall is None:
                    self.tile[pos[X]][pos[Y]].wall = False
                    self.tile[pos[X]][pos[Y]].tier = tunnelTier

            # connect corridors
            if room1.shape in ["corridor", "gallery"] and room2.shape in ["corridor", "gallery"]:
                for pos in positions:
                    if pos in room2.rectangle.border():
                        for cell in self.getNeighborhood(pos):
                            cell.wall = False
                            cell.tier = room2.tier

            # connect circular rooms
            if room1.shape is "round" or room2.shape is "round":
                for pos in positions:
                    if not pos in room1.rectangle.border() or pos in room2.rectangle.border():
                        for cell in self.getNeighborhood(pos):
                            cell.wall = False
                            cell.tier = room2.tier

            # place door
            for pos in positions:
                if pos in room1.rectangle.border():
                    if vent:
                        self.tile[pos[X]][pos[Y]].addObject(Vent())
                    if door:
                        self.tile[pos[X]][pos[Y]].addObject(
                            Door(tier=tunnelTier))
                if pos in room2.rectangle.border():
                    if vent:
                        self.tile[pos[X]][pos[Y]].addObject(Vent())
                for cell in self.getNeighborhood(pos):
                    if cell.wall is None:
                        cell.wall = True

            room1.updateTier(self)
            room2.updateTier(self)
        return valid

    def getNeighborhood(self, pos, shape=None):
        positions = [add(pos, [0, 1]), add(pos, [0, -1]),
                     add(pos, [1, 0]), add(pos, [-1, 0])]
        cells = []
        for pos in positions:
            if self.contains(pos):
                cells.append(self.getTile(pos))
        return cells

    def contains(self, pos):
        return pos[X] in range(0, MAP[WIDTH]) and pos[Y] in range(0, MAP[HEIGHT])

    def castFov(self, pos):
        self.getTile(pos).vision = [True, True]

        blockIndex = 0
        blockPoint = [0, 0]

        for line in self.parent.render.raymap:
            if not all(line[blockIndex] == blockPoint):
                for i, point in enumerate(line):
                    if not self.getTile(point + pos).block[LOS]:
                        for n in NEIGHBORHOOD:
                            cell = self.getTile(point + pos + n)
                            cell.vision = [True, True]
                    else:
                        blockIndex = i
                        blockPoint = point
                        break

    def castLight(self, pos):
        self.getTile(pos).light = 16

        for line in self.parent.render.lightmap:
            for i, point in enumerate(line):
                if not self.getTile(point + pos).block[LOS]:
                    cell = self.getTile(point + pos)
                    cell.light = min(cell.light + 8 - 2 * i, 16)
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
        self.bg = [0, 0, 0]
        self.fg = [255, 255, 255]

    def addObject(self, obj):
        self.object.append(obj)
        obj.cell = self

    def updateRender(self):
        if self.vision[EXP] == False:
            return

        self.bg = (10, 10, 10)

        if self.vision[LOS] == False:
            self.fg = (25, 25, 25)
            return

        self.char = ' '
        if self.vision[LOS]:
            self.bg = tuple(self.light * TIERCOLOR[self.tier] / 16)
            if self.tier == -1:
                self.bg = (40, 40, 40)

        if self.wall:
            self.char = 203
            if self.vision[LOS]:
                self.fg = (85, 85, 85)
            return

        for object in self.object:
            self.char = object.char
            self.fg = object.fg

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
        window.draw_char(pos[X], pos[Y], self.char, self.fg, self.bg)
