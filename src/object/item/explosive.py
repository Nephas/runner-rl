from src.globals import *

from src.object.item.item import Item
from src.effect.effect import Fog, Fluid, Fire, Fuel, Shot, Flash, Slash, EMP

import numpy as np


class Explosive(Item):
    def __init__(self, cell=None, carrier=None, strength=6):
        Item.__init__(self, cell, carrier)

        self.counter = -1
        self.radius = strength

    def use(self, action=None):
        self.drop()
        self.counter = 20
        # Gui.pushMessage('You set the counter to {}'.format(self.counter))
        return 3

    def detonate(self, map):
        #        map.main.sound['EXPLOSION'].play()
        self.cell.addEffect(Flash(self.cell, 14))
        for cell in self.cell.getNeighborhood(shape=self.radius - 2):
            cell.removeWall()

        for cell in self.cell.getNeighborhood(shape=self.radius):
            for obj in cell.object:
                obj.destroy()
            cell.addEffect(Fire(amount=1))
        self.destroy()

    def describe(self):
        return 'Bomb'

    def physics(self, map):
        if self.counter > 0:
            self.counter -= 1
        elif self.counter == 0:
            self.detonate(map)


class Grenade(Explosive):
    def __init__(self, cell=None, carrier=None):
        Explosive.__init__(self, cell, carrier, strength=4)

        self.path = []

    def describe(self):
        return 'Grenade'

    def throw(self, start, target):
        self.path = [start]
        blocked = False
        for i, cell in enumerate(map(lambda p: self.carrier.main.map.getTile(p), self.rayCast(start, target)[1:])):
            if i % 2 == 0:
                self.path.append(cell.pos)
            if cell.block[MOVE]:
                blocked = True
                break
        if not blocked:
            self.path.append(target)
        self.drop()

    def physics(self, map):
        if len(self.path) > 0:
            self.moveTo(self.path[0])
            del self.path[0]
        super(Grenade, self).physics(map)

    def use(self, action):
        super(self.__class__, self).use()        
        self.counter = 10
        self.throw(self.carrier.cell.pos, action['TARGET'])
        return 5

    @staticmethod
    def rayCast(start, end):
        nPoints = np.max(np.abs(end - start)) + 1

        xLine = np.linspace(start[X], end[X], nPoints).round()
        yLine = np.linspace(start[Y], end[Y], nPoints).round()
        line = [[x, y] for x, y in zip(xLine, yLine)]
        return np.array(line).astype('int')


class EMPGrenade(Grenade):
    def __init__(self, cell=None, carrier=None):
        Grenade.__init__(self, cell, carrier)

    def detonate(self, map):
        self.cell.addEffect(Flash(self.cell, 14))

        for cell in self.cell.getNeighborhood(shape=self.radius):
            cell.addEffect(EMP(cell))
        self.destroy()

    def describe(self):
        return 'Grenade'
