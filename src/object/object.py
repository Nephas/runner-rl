from src.globals import *

import random as rd
import copy as cp

from src.render import Render
from src.gui import Gui
from src.effect.effect import Fuel

class Object(object):
    PRIORITY = {'Object': 4,
                'Debris': 4,
                'Item': 8,
                'Actor': 16,
                'NPC': 16,
                'Obstacle': 16,
                'Player': 32}

    def __init__(self, cell=None, char=None, color=COLOR['WHITE']):
        self.cell = cell
        if cell is not None:
            self.cell.object.append(self)
        self.block = [False, False, False]  # [MOVE, LOS]

        self.char = char
        self.basechar = char
        self.fg = list(color)

        self.flammable = 8

        try:
            self.priority = Object.PRIORITY[self.__class__.__name__]
        except KeyError:
            self.priority = 1

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


class Debris(Object):
    def __init__(self, cell=None, obj=None):
        Object.__init__(self, cell, char='%', color=(200, 200, 200))

        self.block = [False, False, False]
        self.obj = obj
        self.flammable = -1

    def interact(self, actor=None, dir=None, type=None):
        #        self.moveDir(dir)
        #        actor.moveDir(dir)
        return 0

    def describe(self):
        return "Destroyed " + self.obj.describe()

class Desk(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char=178, color=COLOR['MAROON'])

        self.block = [True, False, True]

    def describe(self):
        return "Desk"

class Obstacle(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char=10, color=(200, 200, 200))

        self.block = [True, True, True]

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

class Barrel(Object):
    def __init__(self, cell=None, content=None):
        Object.__init__(self, cell, char=9, color=(200, 200, 200))

        self.block = [True, False, True]

        if content is None:
            self.content = Fuel(amount=16)

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
        return "Barrel of " + self.content.describe()

    def destroy(self):
        Gui.pushMessage('The ' + self.describe() + ' is destroyed')
        self.cell.object.remove(self)
        self.cell.addEffect(self.content)
        Debris(self.cell, self)
