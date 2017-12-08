from src.globals import *

import numpy as np


class Grid:
    BACK = 0x1001

    def __init__(self, cell):
        self.cell = cell
        self.wire = None
        self.traffic = None

        self.object = []
        self.agent = []

        # [EXP, LOS]
        self.vision = [False, False, False]

        # graphics attributes [BACK, WIRE, AGENT]
        self.stack = [None, None, None]
        self.color = [COLOR['BLACK'], COLOR['BLACK'], COLOR['BLACK']]

    def addObject(self, obj):
        if obj not in self.object:
            self.object.append(obj)
        obj.grid = self

    def addAgent(self, agent):
        if agent not in self.agent:
            self.agent.append(agent)
        agent.grid = self

    def updatePhysics(self):
        self.vision[LOS] = False
        self.traffic = None

    def updateRender(self):
        if not self.vision[EXP]:
            self.color = [COLOR['BLACK'], COLOR['BLACK'], COLOR['BLACK']]
            return

        if not self.vision[LOS]:
            self.color = [COLOR['NIGHT'], COLOR['NIGHT'], COLOR['NIGHT']]
            return

        if self.cell.wall or self.cell.room is None:
            self.color[0] = np.array(COLOR['BLACK'])
        else:
            self.stack[0] = Grid.BACK
            self.color[0] = np.array(self.cell.room.color) // 4

        if self.traffic is None:
            self.color[1] = self.cell.map.complement[0]
        else:
            self.color[1] = self.traffic.fg

        self.stack[2] = None

        if len(self.object) != 0:
            obj = self.object[0]
            self.stack[1] = obj.char

        if len(self.agent) != 0:
            agent = self.agent[0]
            self.stack[2] = agent.char
            self.color[2] = agent.fg

    def makeWire(self, char=0x10F5):
        self.wire = True
        self.stack[1] = char

    def removeWire(self):
        self.wire = False
        self.stack[1] = None


class Wire:
    ALIGNMAP = {'CROSS': 0x10F5,
                'T_UP': 0x10F1,
                'T_DOWN': 0x10F2,
                'T_LEFT': 0x10E1,
                'T_RIGHT': 0x10F3,
                'UP_LEFT': 0x10E3,
                'UP_RIGHT': 0x10F0,
                'DOWN_LEFT': 0x10E2,
                'DOWN_RIGHT': 0x10E3,
                'UP_DOWN': 0x10E0,
                'LEFT_RIGHT': 0x10F4}

    def __init__(self):
        pass

    @staticmethod
    def getChar(cell):
        neighborhood = list(cell.getNeighborhood())
        wireString = 'CROSS'

        noneCells = filter(lambda c: not c.grid.wire,
                           cell.getNeighborhood('SMALL'))
        if len(noneCells) == 1:
            noneDir = noneCells[0].pos - cell.pos

            if noneDir[Y] == 1:
                wireString = 'T_UP'
            elif noneDir[Y] == -1:
                wireString = 'T_DOWN'
            elif noneDir[X] == 1:
                wireString = 'T_LEFT'
            elif noneDir[X] == -1:
                wireString = 'T_RIGHT'

        elif len(noneCells) == 2:
            noneDir = noneCells[0].pos - noneCells[1].pos

            if np.abs(noneDir[X]) == 2:
                wireString = 'UP_DOWN'
            elif np.abs(noneDir[Y]) == 2:
                wireString = 'LEFT_RIGHT'

        return Wire.ALIGNMAP[wireString]

    @staticmethod
    def getConnection(pos1, pos2):
        pos = tuple(sorted([pos1, pos2], key=lambda p: p[Y]))
        (pos1, pos2) = pos
        positions = [[x, pos1[Y]] for x in range(min(pos1[X], pos2[X]), max(pos1[X], pos2[X]) + 1)] + [[pos2[X], y] for y in range(min(pos1[Y], pos2[Y]), max(pos1[Y], pos2[Y]) + 1)]
        for pos in positions:
            yield pos

    @staticmethod
    def getCable(pos1, pos2):
        """Returns a list of position coorinates in a right-angled connection between two points. The third argument
        states whether the connection starts in horizontal or vertical direction.
        """
        pos = sorted([pos1, pos2], key=lambda p: p[Y])
        (pos1, pos2) = pos

        return [([x, pos1[Y]], 'LEFT_RIGHT') for x in range(min(pos1[X], pos2[X]) + 1, max(pos1[X], pos2[X]))] + [([pos2[X], y], 'UP_DOWN') for y in range(min(pos1[Y], pos2[Y]) + 1, max(pos1[Y], pos2[Y]))] + [([min(pos1[X], pos2[X]), pos1[Y]], 'CROSS'), ([max(pos1[X], pos2[X]), pos1[Y]], 'CROSS')] + [([pos2[X], min(pos1[Y], pos2[Y])], 'CROSS'), ([pos2[X], max(pos1[Y], pos2[Y])], 'CROSS')]

    @staticmethod
    def createTraffic(tileMap, agent, pos1, pos2):
        for pos in Wire.getConnection(pos1, pos2):
            tileMap.getTile(pos).grid.traffic = agent

    @staticmethod
    def seeWire(tileMap, pos1, pos2):
        for pos in Wire.getConnection(pos1, pos2):
            tileMap.getTile(pos).grid.vision = [True, True]

    @staticmethod
    def exploreWire(tileMap, pos1, pos2):
        for pos in Wire.getConnection(pos1, pos2):
            tileMap.getTile(pos).grid.vision = [True, False]
        for pos in [pos1, pos2]:
            tileMap.getTile(pos).grid.vision = [True, True]

    @staticmethod
    def exploreRoom(tileMap, room):
        for cell in room.getCells(tileMap):
            cell.grid.vision = [True, True]

    @staticmethod
    def layCable(tileMap, pos1, pos2):
        for (pos, align) in Wire.getCable(pos1, pos2):
            if not tileMap.contains(pos):
                return False
            cell = tileMap.getTile(pos)
            if not cell.grid.wire or align is 'CROSS':
                cell.grid.makeWire(Wire.ALIGNMAP[align])
        return True
