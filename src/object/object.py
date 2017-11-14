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


class Effect(object):
    def __init__(self, cell=None, char='+', color=COLOR['RED'], bgColor=None, time=1):
        self.cell = cell
        if cell is not None:
            self.cell.effect.append(self)
        self.block = [False, False]  # [MOVE, LOS]

        self.char = char
        self.fg = list(color)
        self.bg = bgColor

        self.time = time

    def describe(self):
        return ''

    def physics(self, map):
        self.time -= 1
        if self.time <= 0:
            self.cease()

    def cease(self):
        self.cell.effect.remove(self)

class Fog(Effect):
    def __init__(self, cell=None, time=32):
        Effect.__init__(self, cell, char='~', color=COLOR['WHITE'], bgColor=COLOR['DARKGRAY'], time=time)

        self.block = [False, True]

    def describe(self):
        return 'Fog'

    def physics(self, map):
        """Slowly decay and spawn new fog."""
        if self.time <= 0:
            self.cease()
        elif self.time % 4 == 0:
            for cell in filter(lambda c: not any(c.block), self.cell.getNeighborhood()):
                cell.addEffect(Fog(time=self.time - 2))
        self.time -= 1

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
