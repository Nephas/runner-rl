from src.globals import *

from src.object.item.item import Item
from src.effect.effect import Fog, Fluid, Fire, Fuel, Shot, Flash, Slash, EMP

import numpy as np


class Gun(Item):
    ANIMATION = [0x2001, 0x2011, 0x2021, 0x2031]

    def __init__(self, cell=None, carrier=None, char=0x103B):
        Item.__init__(self, cell, carrier, char=char, icon=0x2001)

        self.magazine = 6

    def describe(self):
        return "Gun ({:})".format(self.magazine)

    def shoot(self, start, target):
        #        self.carrier.main.sound['SHOT'].play()
        self.carrier.cell.addEffect(Flash(self.carrier.cell))

        for cell in map(lambda p: self.carrier.main.map.getTile(p), self.rayCast(start, target)[1:]):
            cell.addEffect(Shot(cell))
            if cell.block[LOS]:
                break

    def use(self, action):
        if self.magazine == 0:
            return 1

        self.shoot(self.carrier.cell.pos, action['TARGET'])
        self.magazine -= 1

        super(self.__class__, self).use()
        return 5

    @staticmethod
    def rayCast(start, end):
        nPoints = np.max(np.abs(end - start)) + 1

        xLine = np.linspace(start[X], end[X], nPoints).round()
        yLine = np.linspace(start[Y], end[Y], nPoints).round()
        line = [[x, y] for x, y in zip(xLine, yLine)]
        return np.array(line).astype('int')


class Knife(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier)

    def describe(self):
        return "Knife"

    def slash(self, dir):
        cell = self.carrier.main.map.getTile(self.carrier.cell.pos + dir)
        cell.addEffect(Slash(cell))

    def use(self, action):
        super(self.__class__, self).use()
        self.slash(action['DIR'])
        return 5


class Shotgun(Gun):
    def __init__(self, cell=None, carrier=None):
        Gun.__init__(self, cell, carrier)

    def shoot(self, start, target):
        #        self.carrier.main.sound['SHOT'].play()
        self.carrier.cell.addEffect(Flash(self.carrier.cell))

        offsets = np.array([[0, -1], [1, 0], [0, 1], [-1, 0]])

        for off in offsets:
            for cell in map(lambda p: self.carrier.main.map.getTile(p), self.rayCast(start, target + off)[1:]):
                cell.addEffect(Shot(cell))
                if cell.block[LOS]:
                    break


class Taser(Gun):
    def __init__(self, cell=None, carrier=None):
        Gun.__init__(self, cell, carrier, char=0x104A)

    def shoot(self, start, target):
        #        self.carrier.main.sound['SHOT'].play()
        self.carrier.cell.addEffect(Flash(self.carrier.cell))

        for cell in map(lambda p: self.carrier.main.map.getTile(p), self.rayCast(start, target)[1:]):
            cell.addEffect(EMP(cell))
            if cell.block[LOS]:
                break

    def describe(self):
        return "Taser ({:})".format(self.magazine)
