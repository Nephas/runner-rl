from src.globals import *

import random as rd
import numpy as np


class AI:
    def __init__(self, actor):

        self.actor = actor
        self.room = None

    def updateRoom(self, map):
        cell = self.actor.cell
        for room in map.tier[cell.tier]:
            if room.contains(cell.pos):
                self.room = room
                break

    @staticmethod
    def decide(map):
        return []

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

    def describe(self):
        return ''


class Idle(AI):
    def __init__(self, actor):
        AI.__init__(self, actor)

        self.state = 'WAIT'
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

    def describe(self):
        return "(Idle)"
