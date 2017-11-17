from src.globals import *

import random as rd
import numpy as np

from src.render import Render

class AI:
    FOVMAP = Render.rayMap(30)
    FOV_NEIGHBORHOOD = np.array([[0,1],[1,0],[0,-1],[-1,0],[1,1],[1,-1],[-1,-1],[-1,1]])

    def __init__(self, actor):

        self.actor = actor
        self.room = None

        self.aware = [self]

        self.enemy = []
        self.friend = []
        self.neutral = []

    def lookAround(self, map):
        self.aware = []
        for cell in self.room.getCells(map):
            self.aware += filter(lambda obj: hasattr(obj, 'ai'), cell.object)

    def updateRoom(self, map):
        cell = self.actor.cell
        for room in map.tier[cell.tier]:
            if room.contains(cell.pos):
                self.room = room
                break

    def switchState(self, ai):
        self.actor.ai = ai(self.actor)

    def describe(self):
        return " (" + self.__class__.__name__ + ") "

    def decide(map):
        return []

    @staticmethod
    def castFov(tileMap, pos, radius=20):
        blockIndex = 0
        blockPoint = [0, 0]

        for baseLine in AI.FOVMAP:
            try:
                if not all(baseLine[blockIndex] == blockPoint):
                    line = baseLine + pos
                    for i, point in enumerate(line):
                        cell = tileMap.getTile(point)
                        if cell.block[LOS] or i > radius:
                            blockIndex = i
                            blockPoint = baseLine[i]
                            break
                        else:
                            if cell.light > BASE_LIGHT:
                                cell.vision = [True, True]
                                for neighbor in map(lambda p: tileMap.getTile(p), AI.FOV_NEIGHBORHOOD + point):
                                    neighbor.vision = [True, True]
                            else:
                                tileMap.getTile(point).vision = [True, False]
                                for neighbor in map(lambda p: tileMap.getTile(p), AI.FOV_NEIGHBORHOOD + point):
                                    if neighbor.block[LOS]:
                                        neighbor.vision = [True, False]
            except IndexError:
                pass
        for cell in tileMap.getTile(pos).getNeighborhood(shape=8):
            cell.vision = [True, True]

    @staticmethod
    def findPath(map, start, target, interact=False):
        """Calculate a route from start to target, and return a list of actions to take."""
        path = [start]

        dist = np.linalg.norm(path[-1] - target)
        while dist != 0 and len(path) < 32:
            possibleCells = filter(
                lambda c: not c.block[MOVE], map.getNeighborhood(path[-1], shape=8))
            closestCell = min(
                possibleCells, key=lambda c: np.linalg.norm(target - c.pos))
            if dist <= 1.5 and map.getTile(target).block[MOVE]:
                break
            if all(closestCell.pos == path[-1]):
                break
            path.append(closestCell.pos)
            dist = np.linalg.norm(path[-1] - target)

        actions = [{'TYPE': 'MOVE', 'DIR': path[i] - path[i - 1]}
                   for i in range(1, len(path))]

        if interact:
            actions.append({'TYPE': 'USE', 'DIR': target - path[-1]})

        return actions

class Idle(AI):
    def __init__(self, actor):
        AI.__init__(self, actor)

        self.counter = 0

    def decide(self, map):
        if len(self.actor.actions) == 0:
            if self.counter > 0:
                self.counter -= 1
                return []
            else:
                self.updateRoom(map)
                self.counter = rd.randint(8, 32)
                return AI.findPath(map, self.actor.cell.pos, self.room.randomSpot(2))

class Follow(AI):
    def __init__(self, actor, target):
        AI.__init__(self, actor)

        self.target = target

    def decide(self, map):
        if len(self.actor.actions) == 0:
            if np.linalg.norm(self.actor.cell.pos - self.target.cell.pos) < 5:
                return []
            else:
                return AI.findPath(map, self.actor.cell.pos, self.target.cell.pos)[0:3]


class Waiting(AI):
    def __init__(self, actor, time=32):
        AI.__init__(self, actor)

        self.state = 'WAIT'
        self.counter = time

    def decide(self, map):
        if self.counter > 0:
            self.counter -= 1
        else:
            self.actor.ai = Idle(self.actor)
        return []
