from src.globals import *

import random as rd
import numpy as np

from src.render import Render
from src.level.map import Map, Rectangle

class AI:
    FOVMAP = Render.rayMap(24)
    FOV_NEIGHBORHOOD = np.array(
        [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [1, -1], [-1, -1], [-1, 1]])

    def __init__(self, actor, mind=None):
        self.actor = actor
        self.char = actor.char
        self.color = COLOR['WHITE']
        self.distmap = np.ones((Map.HEIGHT, Map.WIDTH)) * -1

        if mind is None:
            self.mind = {'AWARE': [self],
                         'TARGET': None,
                         'ROOM': None,
                         'ENEMY': [],
                         'FRIEND': []}
        else:
            self.mind = mind

    def lookAround(self, map):
        self.mind['AWARE'] = []
        self.updateRoom(map)
        actors = []

        for cell in self.mind['ROOM'].getCells(map):
            if cell.light > BASE_LIGHT:
                actors += filter(lambda obj: hasattr(obj, 'ai'), cell.object)

        for obj in actors:
            if self.hasLos(map, self.actor.cell.pos, obj.cell.pos):
                self.mind['AWARE'] += [obj]

        for cell in self.actor.cell.getNeighborhood('LARGE'):
            self.mind['AWARE'] += filter(lambda obj: hasattr(obj, 'ai')
                                         and not obj in self.mind['AWARE'], cell.object)

    def makeEnemy(self, actor):
        if actor in self.mind['FRIEND']:
            self.mind['FRIEND'].remove(actor)
        self.mind['ENEMY'].append(actor)

    def makeFriend(self, actor):
        if actor in self.mind['ENEMY']:
            self.mind['ENEMY'].remove(actor)
        self.mind['FRIEND'].append(actor)

    def updateRoom(self, map):
        self.mind['ROOM'] = self.actor.cell.room

    def switchState(self, aiState, target=None):
        self.actor.ai = aiState(self.actor, self.mind, target)
        self.actor.fg = self.actor.ai.color

    def describe(self):
        return " (" + self.__class__.__name__ + ") "

    def switchChar(self):
        if self.actor.char is not self.actor.basechar:
            self.actor.char = self.actor.basechar
        elif self.actor.char is self.actor.basechar:
            if self.actor.main.player in self.mind['ENEMY']:
                self.actor.char = '!'
            elif self.actor.main.player in self.mind['FRIEND']:
                self.actor.char = 003
            else:
                self.actor.char = '?'

    def decide(map):
        return []

    def updateDist(self, tileMap, radius=10):
        self.distmap = np.ones((Map.HEIGHT, Map.WIDTH)) * -1
        boundary = [self.actor.cell]

        for i in range(int(radius)):
            newBound = []
            for cell in boundary:
                newBound += cell.getNeighborhood()

            boundary = filter(lambda c: self.distmap[c.pos[Y], c.pos[X]] < 0 and not c.block[MOVE], newBound)
            for cell in boundary:
                self.distmap[cell.pos[Y], cell.pos[X]] = i
        cell = self.actor.cell
        self.distmap[cell.pos[Y], cell.pos[X]] = 0

    @staticmethod
    def castFov(tileMap, pos):
        blockIndex = 0
        blockPoint = [0, 0]

        for baseLine in AI.FOVMAP:
            try:
                if not all(baseLine[blockIndex] == blockPoint):
                    line = baseLine + pos
                    for i, point in enumerate(line):
                        cell = tileMap.getTile(point)
                        if cell.block[LOS]:
                            blockIndex = i
                            blockPoint = baseLine[i]
                            break
                        else:
                            neighbors = map(lambda p: tileMap.getTile(p), AI.FOV_NEIGHBORHOOD + point) + [cell]

                            if cell.light > BASE_LIGHT:
                                cell.vision = [True, True]
                                for neighbor in filter(lambda n: n.block[LOS], neighbors):
                                    neighbor.vision = [True, True]
                            else:
                                for neighbor in filter(lambda n: n.block[LOS], neighbors):
                                    neighbor.vision = [True, False]
            except IndexError:
                pass
        for cell in tileMap.getTile(pos).getNeighborhood('LARGE'):
            cell.vision = [True, True]

    @staticmethod
    def hasLos(map, start, end):
        for pos in Render.rayCast(start, end):
            if map.getTile(pos).block[LOS]:
                return False
        return True

    @staticmethod
    def findPath(map, start, target, interact=False):
        """Calculate a route from start to target, and return a list of actions to take."""
        path = AI.simplePath(map, start, target)
        return AI.pathToActions(path, target, interact)

    @staticmethod
    def simplePath(map, start, target):
        """Just trying to minimize distance."""
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
        return path

    @staticmethod
    def pathToActions(path, target, interact=False):
        actions = [{'TYPE': 'MOVE', 'DIR': path[i] - path[i - 1]}
                   for i in range(1, len(path))]

        if interact:
            actions.append({'TYPE': 'USE', 'DIR': target - path[-1]})
        return actions


    def findFloodPath(self, tileMap, start, target, interact=False):
        """Calculate a route from start to target, and return a list of actions to take."""
        dist = np.linalg.norm(start - target)
        self.updateDist(tileMap, 2*dist)
        path = [target]

        for i in range(int(2*dist)):
            possibleCells = filter(lambda c: self.distmap[c.pos[Y], c.pos[X]] >= 0, tileMap.getNeighborhood(path[-1], shape=8))
            lowestCell = min(possibleCells, key=lambda c: self.distmap[c.pos[Y], c.pos[X]])
            path.append(lowestCell.pos)
            if all(path[-1] == start):
                break

        return pathToActions(reversed(path), interact)

class Idle(AI):
    def __init__(self, actor, mind=None, target=None):
        AI.__init__(self, actor, mind)

        self.counter = 0
        self.color = COLOR['GREEN']

    def decide(self, map):
        for cell in self.actor.cell.getNeighborhood('LARGE'):
            for obj in cell.object:
                if not obj in self.mind['AWARE'] and obj is not self.mind['TARGET'] and obj in self.mind['ENEMY']:
                    self.switchState(Stunned)
                    self.mind['AWARE'].append(obj)
                    self.mind['TARGET'] == obj
                    return []
                elif obj is self.mind['TARGET']:
                    self.switchState(Attack, obj)
                    return []

        if len(self.actor.actions) == 0:
            if self.counter > 0:
                self.lookAround(map)
                for actor in self.mind['AWARE']:
                    if actor in self.mind['ENEMY']:
                        self.mind['TARGET'] = actor
                        self.switchState(Attack, actor)
                        break
                self.counter -= 1
                return []
            else:
                self.updateRoom(map)
                self.counter = rd.randint(8, 32)
                return AI.findPath(map, self.actor.cell.pos, self.mind['ROOM'].randomSpot(2))


class Stunned(AI):
    def __init__(self, actor, mind=None, target=None):
        AI.__init__(self, actor, mind)

        self.counter = 10
        self.color = COLOR['YELLOW']

    def decide(self, map):
        self.actor.actions = []
        if self.counter > 0:
            self.counter -= 1
        else:
            self.switchState(Idle)
        return []


class Follow(AI):
    def __init__(self, actor, mind, target):
        AI.__init__(self, actor, mind)

        self.target = target

    def decide(self, map):
        if len(self.actor.actions) == 0:
            if np.linalg.norm(self.actor.cell.pos - self.target.cell.pos) < 5:
                return []
            else:
                return AI.findPath(map, self.actor.cell.pos, self.target.cell.pos)[0:3]


class Attack(AI):
    def __init__(self, actor, mind, target):
        AI.__init__(self, actor, mind)

        self.target = target
        self.color = COLOR['RED']

    def decide(self, map):
        if len(self.actor.actions) == 0:
            self.lookAround(map)
            if self.target in self.mind['AWARE']:
                direction = self.target.cell.pos - self.actor.cell.pos
                if np.linalg.norm(direction) < 2:
                    return [{'TYPE': 'ATTACK', 'DIR': direction}]
                else:
                    return AI.findPath(map, self.actor.cell.pos, self.target.cell.pos)[0:3]
            else:
                self.switchState(Chase, self.target)
                return []


class Chase(AI):
    def __init__(self, actor, mind, target):
        AI.__init__(self, actor, mind)

        self.target = target
        self.lastPos = target.cell.pos
        self.color = COLOR['ORANGE']

    def decide(self, map):
        if len(self.actor.actions) == 0:
            self.lookAround(map)
            if self.target in self.mind['AWARE']:
                self.switchState(Attack, self.target)
                return AI.findPath(map, self.actor.cell.pos, self.target.cell.pos)[0:3]
            else:
                if all(self.actor.cell.pos == self.lastPos):
                    self.switchState(Idle)
                    return []
                else:
                    return AI.findPath(map, self.actor.cell.pos, self.lastPos)[0:3]
