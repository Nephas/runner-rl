from src.globals import *

import math as m
import numpy as np
import random as rd
import copy as cp
import itertools as it
import colorsys as cs
import hashlib as hl

from src.level.map import Map, Rectangle, Cell
from src.level.corp import Corp
from src.level.room import Room
from src.level.roomtypes import BossRoom, Corridor, Office, Dome, Hall, ServerFarm, GreenHouse, Lab, Storage

from src.grid.server import Terminal, Server, MasterSwitch
from src.object.light import Lamp, DoorLamp
from src.object.door import Vent, SecDoor

from src.render.render import Render
from src.actor.actor import Player
from src.actor.npc import Drone


class Level(Map):
    SHAPE = {'CORNER': [Rectangle([Map.WIDTH // 3, Map.HEIGHT // 3], 2 * Map.WIDTH // 3, 2 * Map.HEIGHT / 3)],
             'DUAL': [Rectangle([0, 0], Map.WIDTH // 3, Map.HEIGHT // 3),
                      Rectangle([2 * Map.WIDTH // 3, 2 * Map.HEIGHT // 3], Map.WIDTH // 3, Map.HEIGHT // 3)],
             'CROSS': [Rectangle([2 * Map.WIDTH // 3, 2 * Map.HEIGHT // 3], Map.WIDTH // 3, Map.HEIGHT // 3),
                       Rectangle([0, 0], Map.WIDTH // 3, Map.HEIGHT // 3),
                       Rectangle([0, 2 * Map.HEIGHT // 3], Map.WIDTH // 3, Map.HEIGHT // 3),
                       Rectangle([2 * Map.WIDTH // 3, 0], Map.WIDTH // 3, Map.HEIGHT // 3)],
             'RING': [Rectangle([Map.WIDTH // 3, Map.HEIGHT // 3], Map.WIDTH // 3, Map.HEIGHT // 3)]}

    def __init__(self, main=None):
        Map.__init__(self, main)

        self.tier = [[]]
        self.forbidden = []

    def contains(self, target):
        """Returns whether the target is fully contained inside the map, excluding the forbidden regions.
        Takes 2D pos lists and Rectangle objects
        """
        if target.__class__.__name__ in ['Rectangle', 'BossRoom', 'Room']:
            for rect in self.forbidden:
                if target.intersects(rect):
                    return False
            return (target.x[MAX] < Map.WIDTH and target.x[MIN] > 0 and target.y[MAX] < Map.HEIGHT and target.y[MIN] > 0)
        else:
            for rect in self.forbidden:
                if rect.contains(target):
                    return False
            return target[X] in range(0, Map.WIDTH) and target[Y] in range(0, Map.HEIGHT)

    def clear(self):
        self.tile = [[Cell(self, [x, y]) for y in range(Map.HEIGHT)]
                     for x in range(Map.WIDTH)]
        self.tier = [[]]

    def getRooms(self):
        for tier in self.tier:
            for room in tier:
                yield room

    def load(self, seed='Test', random=False, debug = False):
        self.clear()

        if not random:
            seed = int(hl.sha1(seed).hexdigest(), 16) % (10 ** 8)
            rd.seed(seed)
            np.random.seed(seed)

        self.corp = Corp()
        self.forbidden = Level.SHAPE[self.corp.layout]
        self.palette = self.corp.palette
        print(self.corp)
        print('\n')
        self.generate(debug)

    def generate(self, debug = False):
        if debug:
            self.clear()
            self.generateStart()
            self.getTile(self.tier[0][0].center).addObject(self.main.player)
            return

        stats = {'ROOMS': -1, 'VENTS': -1, 'CORRIDORS': -1, 'AREA': -1}
        while stats['VENTS'] < 10 or stats['ROOMS'] < 20 or stats['CORRIDORS'] < 5 or stats['AREA'] < 4000:
            self.clear()
            self.generateStart()
            self.generateRooms()
            self.generateVents()

            stats = self.countMetrics()
            print(stats)

        self.finalize()

    def generateStart(self):
        self.tier = [[]]

        w = rd.randint(*self.corp.struct[0]['SIZES'])
        h = rd.randint(*self.corp.struct[0]['SIZES'])
        margin = 8

        while True:
            pos = [rd.randint(margin, Map.WIDTH - w - margin),
                   rd.randint(margin, Map.HEIGHT - h - margin)]
            start = BossRoom(pos, w, h, 0, None)
            if self.contains(start):
                self.tier[0].append(start)
                start.carve(self)
                break

    def generateRooms(self):
        """Propagate every single room according to the N_CHILD and ROOM_SIZE specifications."""
        # recursively spread room
        Render.printImage(self, "gif/levelgen{:02}.bmp".format(0))

        for i in range(1, len(self.corp.struct)):
            Render.printImage(self, "gif/levelgen{:02}.bmp".format(i))

            self.tier.append([])
            for room in self.tier[i - 1]:
                self.propagateRoom(room, i)

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
        stats = {'ROOMS': 0, 'VENTS': 0, 'CORRIDORS': 0, 'AREA': 0}
        stats['VENTS'] = len(self.getAll('Vent')) / 2
        for tier in self.tier:
            for room in tier:
                stats['ROOMS'] += 1
                stats['AREA'] += room.area
                if room.__class__.__name__ is 'Corridor':
                    stats['CORRIDORS'] += 1
        return stats

    def finalize(self):
        self.forbidden = []
        self.smoothWalls(2)

        for room in self.getRooms():
            room.carve(self)
            room.updateCells(self)
            room.generateContent(self)

        # connect terminals
        for pair in it.combinations(self.getAll(Server) + self.getAll(Terminal) + self.getAll(MasterSwitch), 2):
            if rd.randint(0, 2) <= 2:
                if np.linalg.norm(pair[0].cell.pos - pair[1].cell.pos) < Map.WIDTH / 8:
                    pair[0].connect(pair[1])
                    self.layCable(pair[0].cell.pos, pair[1].cell.pos)

        # set start and extraction rooms
        start = rd.choice(self.tier[-1])
        start.function = "start"

        self.getTile(start.center).addObject(self.main.player)

        for actor in self.main.actor:
            if actor.__class__.__name__ is 'Guard':
                actor.ai.makeEnemy(self.main.player)

        drone = Drone(self.getTile(start.randomSpot()), self.main, self.main.player)
        drone.ai.makeFriend(self.main.player)

        exRooms = filter(lambda r: r.function is None, self.tier[-1])
        rd.shuffle(exRooms)
        for i in range(3):
            exRooms.pop().function = "extraction"

        Render.printImage(self, "gif/levelgen99.bmp")

    def smoothWalls(self, times=2):
        for i in range(times):
            wallMap = np.zeros((Map.WIDTH, Map.HEIGHT))
            for cell in self.allTiles():
                if cell.wall:
                    for neighbor in cell.getNeighborhood('LARGE'):
                        if neighbor.wall is None:
                            wallMap[neighbor.pos[X],neighbor.pos[Y]] = 1

            for cell in self.allTiles():
                if wallMap[cell.pos[X], cell.pos[Y]] != 0:
                    cell.makeWall()

        for cell in self.allTiles():
            if cell.wall is None and len(filter(lambda c: c.wall, cell.getNeighborhood('LARGE'))) >= 6:
                cell.makeWall()
            elif cell.wall is True:
                cell.makeWall()


    def layCable(self, pos1, pos2, horizontal=True):
        for pos in self.getConnection(pos1, pos2, horizontal):
            if not self.contains(pos):
                return False
            cell = self.getTile(pos)
            if cell.grid is None:
                cell.grid = True
        return True

    def carveDoorway(self, room1, room2, tunnelTier=-1, horizontal=True):
        positions = self.getConnection(room1.center, room2.center, horizontal)

        # carve wide tunnels for corridors and circular rooms
        for pos in positions:
            if pos not in room1.border() or pos in room2.border():
                for cell in self.getTile(pos).getNeighborhood(shape='LARGE'):
                    if list(cell.pos) not in room1.border():
                        cell.removeWall()

        # place door and Terminal
        door = SecDoor(tier=tunnelTier)
        for pos in positions:
            cell = self.getTile(pos)
            cell.removeWall()
            if pos in room1.border():
                cell.addObject(door)
            if pos in room2.border():
                flag = False
                for cell in self.getTile(pos).getNeighborhood():
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
            for neighbor in self.getTile(pos).getNeighborhood():
                if neighbor.object != []:
                    return False

        # carve connection
        for cell in map(lambda p: self.getTile(p), positions):
            cell.removeWall()

        # place vents
        for pos in positions:
            if pos in room1.border():
                self.getTile(pos).addObject(Vent())
            if pos in room2.border():
                self.getTile(pos).addObject(Vent())

            # walls for vent tunnels
            for cell in self.getTile(pos).getNeighborhood('LARGE'):
                if cell.wall is None:
                    cell.makeWall()
        return True

    def propagateRoom(self, room, tier):
        children = self.corp.struct[tier]['CHILDREN']
        sizes = self.corp.struct[tier]['SIZES']
        shapes = self.corp.struct[tier]['SHAPES']

        directions = [UP, DOWN, LEFT, RIGHT]

        # number of child rooms
        for i in range(rd.randint(*children)):
            shape = rd.choice(shapes)

            # number of tries to find a valid child
            for i in range(100):
                direction = rd.choice(directions)
                alignment = rd.choice([MIN, MAX])

                w = rd.randint(*sizes)
                h = rd.randint(*sizes)

                if shape is 'Corridor':
                    if direction in [UP, DOWN]:
                        w = 5
                        h = int(1.5 * rd.randint(*sizes))
                    else:
                        w = int(1.5 * rd.randint(*sizes))
                        h = 5

                if shape is 'Dome':
                    w = rd.randint(*sizes)
                    h = w

                offset = np.array(self.getOffset(room, direction, alignment, w, h))
                rect = Rectangle(room.pos + offset, w, h)

                for other in list(self.getRooms()) + room.children:
                    if rect is not None and rect.intersects(other) or not self.contains(rect):
                        rect = None
                        break

                if rect is not None:
                    break

            if rect is not None:
                if shape is 'Corridor':
                    directions.remove(direction)

                roomClass = globals()[shape]
                nextRoom = roomClass(
                    rect.pos, rect.size[X], rect.size[Y], room.tier + 1, room)
                room.children.append(nextRoom)
                self.tier[room.tier + 1].append(nextRoom)
                nextRoom.carve(self)

                # carve a connection
                if direction in (UP, DOWN):
                    self.carveDoorway(nextRoom, room, room.tier,
                                      not rect.size[X] < room.size[X])
                elif direction in (LEFT, RIGHT):
                    self.carveDoorway(nextRoom, room, room.tier,
                                      rect.size[Y] < room.size[Y])
        return room.children

    @staticmethod
    def getOffset(room, direction, alignment, w, h):
        if (direction, alignment) == (UP, MIN):
            return [0, -h]
        elif (direction, alignment) == (UP, MAX):
            return [room.size[X] - w, -h]
        elif (direction, alignment) == (RIGHT, MIN):
            return [room.size[X], 0]
        elif (direction, alignment) == (RIGHT, MAX):
            return [room.size[X], room.size[Y] - h]
        elif (direction, alignment) == (DOWN, MIN):
            return [0, room.size[Y]]
        elif (direction, alignment) == (DOWN, MAX):
            return [room.size[X] - w, room.size[Y]]
        elif (direction, alignment) == (LEFT, MIN):
            return [-w, 0]
        elif (direction, alignment) == (LEFT, MAX):
            return [-w, room.size[Y] - h]

    @staticmethod
    def getConnection(pos1, pos2, horizontal=True):
        """Returns a list of position coorinates in a right-angled connection between two points. The third argument
        states whether the connection starts in horizontal or vertical direction.
        """
        if horizontal:            # horizontal first:
            return [[x, pos1[Y]] for x in range(min(pos1[X], pos2[X]), max(
                pos1[X], pos2[X]) + 1)] + [[pos2[X], y] for y in range(min(pos1[Y], pos2[Y]), max(pos1[Y], pos2[Y]) + 1)]
        else:             # vertical first:
            return [[pos1[X], y] for y in range(min(pos1[Y], pos2[Y]), max(
                pos1[Y], pos2[Y]) + 1)] + [[x, pos2[Y]] for x in range(min(pos1[X], pos2[X]), max(pos1[X], pos2[X]) + 1)]

    @staticmethod
    def randColorPalette(length):
        startcol = [rd.random(), 0.5, 0.9]

        colors = []
        for i in np.linspace(0, 1 / 12., length):
            col = startcol
            col[0] = (col[0] + i) % 1.0
            colors.append((255 * np.array(cs.hsv_to_rgb(*col))).astype('int'))

        startcol[0] += 0.5
        startcol[1] = 0.9

        complement = []
        for i in np.linspace(0, 1 / 12., length):
            col = startcol
            col[0] = (col[0] + i) % 1.0
            complement.append(
                (255 * np.array(cs.hsv_to_rgb(*col))).astype('int'))

        return (colors + [np.array((10, 10, 10))], complement + [np.array((10, 10, 10))])
