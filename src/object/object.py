from src.globals import *

import random as rd

from src.render import Render
from src.gui import Gui

class Object(object):
    def __init__(self, cell=None, char=None, color=COLOR['WHITE']):
        self.cell = cell
        if cell is not None:
            self.cell.object.append(self)
        self.block = [False, False]  # [MOVE, LOS]

        self.char = char
        self.fg = list(color)

    def moveTo(self, pos):
        if self.cell.map.tile[pos[X]][pos[Y]].block[MOVE]:
            return False
        self.cell.object.remove(self)
        self.cell = self.cell.map.tile[pos[X]][pos[Y]]
        self.cell.map.tile[pos[X]][pos[Y]].object.append(self)
        return True

    def moveDir(self, dir):
        targetPos = self.cell.pos + dir
        return self.moveTo(targetPos)

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5
        return 0

    def describe(self):
        return "something"

    def physics(self, map):
        pass

    def destroy(self):
        Gui.pushMessage('The ' + self.describe() + ' is destroyed')
        self.cell.object.remove(self)
        Debris(self.cell, self)


class Effect(Object):
    def __init__(self, cell=None, char='+', color=COLOR['RED'], time=1):
        Object.__init__(self, cell, char=char, color=color)

        self.time = time

    def interact(self, actor=None, dir=None, type=None):
        return 0

    def describe(self):
        return ''

    def physics(self, map):
        self.time -= 1
        if self.time <= 0:
            self.cell.object.remove(self)

    def destroy(self):
        self.cell.object.remove(self)


class Debris(Object):
    def __init__(self, cell=None, obj=None):
        Object.__init__(self, cell, char='%', color=(200, 200, 200))

        self.block = [False, False]
        self.obj = obj

    def interact(self, actor=None, dir=None, type=None):
        #        self.moveDir(dir)
        #        actor.moveDir(dir)
        return 0

    def describe(self):
        return "Destroyed " + self.obj.describe()


class Obstacle(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char=10, color=(200, 200, 200))

        self.block = [True, True]

    def interact(self, actor=None, dir=None, type=None):
        oldCell = self.cell

        if type is 'ATTACK':
            self.destroy()
            return 5
        elif self.moveDir(dir):
            Gui.pushMessage('You push the ' + self.describe())
            oldCell.updatePhysics()
            actor.moveDir(dir)
            return 3
        else:
            return 0

    def describe(self):
        return "Chest"
