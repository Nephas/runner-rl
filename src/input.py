from src.globals import *

import numpy as np
import tdl

from src.actor.ai import AI

class Input:

    MOVEMAP = {'w': np.array([0, -1]),
               'a': np.array([-1, 0]),
               's': np.array([0, 1]),
               'd': np.array([1, 0]),
               'q': np.array([-1, -1]),
               'e': np.array([1, -1]),
               'y': np.array([-1, 1]),
               'c': np.array([1, 1])}

    def __init__(self, main):
        self.main = main
        self.quit = False

    def handleEvents(self):
        try:
            while True:
                event = tdl.event.get().next()

                if event.type is 'KEYDOWN':
                    self.handleKey(event.key, event.char)
                elif event.type is 'MOUSEUP':
                    self.handleClick(event)
                elif event.type is 'MOUSEMOTION':
                    self.handleMouse(event.cell)
        except:
            pass

    def handleKey(self, key, char):
        if key == 'ESCAPE':
            self.quit = True
        elif key == 'UP':
            self.main.gui.moveOffset(np.array([0, -3]))
        elif key == 'DOWN':
            self.main.gui.moveOffset(np.array([0, 3]))
        elif key == 'LEFT':
            self.main.gui.moveOffset(np.array([-3, 0]))
        elif key == 'RIGHT':
            self.main.gui.moveOffset(np.array([3, 0]))

        elif key == 'SPACE' and len(self.main.player.actions) < 2:
            self.main.player.actions = []
            ray = self.main.gui.cursorPos - self.main.player.cell.pos
            dir = (ray / np.linalg.norm(ray)).round().astype('int')
            self.main.player.actions.append({'TYPE': 'ATTACK', 'DIR': dir})

        if key == 'CHAR':
            self.main.player.actions = []
            if char == 'r':
                self.main.gui.pushMessage("Waiting")
                self.main.player.cooldown += 2
            if char == 'm':
                self.main.gui.pushMessage("Switching Map")
                self.main.render.mapLayer = (self.main.render.mapLayer + 1) % 3
            if char in "wasdqeyc" and len(self.main.player.actions) < 2:
                self.main.player.actions.append({'TYPE': 'MOVE', 'DIR': Input.MOVEMAP[char]})

    def handleMouse(self, terminalPos):
        self.main.gui.updateCursor(terminalPos)

    def handleClick(self, event):
        self.main.player.actions = []

        if event.button is 'LEFT' and len(self.main.player.actions) < 2:
            self.main.player.actions = AI.findPath(self.main.map, self.main.player.cell.pos, self.main.gui.cursorPos)
        elif event.button is 'RIGHT' and len(self.main.player.actions) < 2:
            self.main.player.actions = AI.findPath(self.main.map, self.main.player.cell.pos, self.main.gui.cursorPos, True)

#            self.actions.append(
#                {'TYPE': 'USE', 'DIR': self.main.gui.cursorDir})

    def findPath(self, map, start, target, interact=False):
        path = [start]

        dist = Input.eucDist(path[-1], target)
        while dist != 0 and len(path) < 32:
            possibleCells = filter(lambda c: not c.block[MOVE], map.getNeighborhood(path[-1], shape=8))
            closestCell = min(possibleCells, key = lambda c: Input.eucDist(target, c.pos))
            if dist <= 1.5 and map.getTile(target).block[MOVE]:
                break
            if all(closestCell.pos == path[-1]):
                break
            path.append(closestCell.pos)
            dist = Input.eucDist(path[-1], target)

        for i in range(1, len(path)):
            self.main.player.actions.append({'TYPE': 'MOVE', 'DIR': path[i] - path[i - 1]})

        if interact:
            self.main.player.actions.append({'TYPE': 'USE', 'DIR': target - path[-1]})


    @staticmethod
    def manDist(pos1, pos2):
        return np.sum(np.abs(pos1 - pos2))

    @staticmethod
    def eucDist(pos1, pos2):
        return np.linalg.norm(pos1 - pos2)
