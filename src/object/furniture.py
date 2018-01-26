from src.globals import *

import random as rd
import numpy as np
import copy as cp
import itertools as it

from src.effect.effect import Fuel, Holotext
from src.object.object import Object, Debris
from src.text.news import News


class Desk(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, color=COLOR['WHITE'], char=np.random.choice(
            [0x100A, 0x100B], p=[0.25, 0.75]))

        self.block = [True, False, True]


class Hydroponics(Object):
    ANIMATION = [0x105C, 0x105C, 0x105D,
                 0x105D, 0x105E, 0x105E, 0x105F, 0x105F]

    def __init__(self, cell=None):
        Object.__init__(self, cell, color=COLOR['WHITE'])

        self.block = [False, True, False]
        self.flammable = -1

    def physics(self, map):
        self.char = self.animation.next()


class Container(Object):
    def __init__(self, cell=None, char=0x1017, color=COLOR['WHITE'], content=None):
        Object.__init__(self, cell, char, color)

        self.content = content
        self.block = [True, True, True]

    def interact(self, actor=None, dir=None, type=None):
        oldCell = self.cell

        if type is 'ATTACK':
            self.destroy()
            return 5
        elif self.moveDir(dir):
            oldCell.updatePhysics()
            actor.moveDir(dir)
            return 3
        else:
            return 0

    def describe(self):
        return "Chest"


class Locker(Object):
    def __init__(self, cell=None, char=0x1008, color=COLOR['WHITE'], content=None):
        Object.__init__(self, cell, char, color)

        self.content = content
        self.block = [True, True, True]

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5
        elif type is 'USE':
            self.enter(actor)
            return 3
        else:
            return 0

    def describe(self):
        return "Locker"

    def enter(self, actor):
        actor.cell.object.remove(actor)
        actor.cell = self.cell
        self.cell.object.append(actor)

    def destroy(self):
        self.cell.object.remove(self)
        self.cell.addEffect(self.content)
        Debris(self.cell, self)


class Barrel(Container):
    def __init__(self, cell=None, content=None):
        Container.__init__(self, cell, 0x1009, content=content)

        self.block = [True, False, True]

        if self.content is None:
            self.content = Fuel(amount=16)

    def describe(self):
        return "Barrel of " + self.content.describe()

    def destroy(self):
        self.cell.object.remove(self)
        self.cell.addEffect(self.content)
        Debris(self.cell, self)


class Projector(Object):
    ANIMATION = [0x100C, 0x100D, 0x100E, 0x100F]

    def __init__(self, cell=None):
        Object.__init__(self, cell)

        self.text = News.continuousBlurb('NORMAL')
        self.block = [True, True, True]
        self.holoCell = None

    def physics(self, map):
        if self.holoCell is None:
            self.holoCell = self.cell.map.getTile(self.cell.pos + np.array([1, 0]))
        self.holoCell.addEffect(Holotext(self.holoCell, self.text, color=COLOR['GREEN']))
        self.char = self.animation.next()
