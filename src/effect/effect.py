from src.globals import *

import random as rd

from src.render import Render
from src.gui import Gui

class Effect(object):
    PRIORITY = {'Effect': 24,
                'Fluid': 2,
                'Fog': 24}

    def __init__(self, cell=None, char='+', color=COLOR['RED'], bgColor=None, time=1):
        self.cell = cell
        if cell is not None:
            self.cell.effect.append(self)
        self.block = [False, False]  # [MOVE, LOS]

        self.char = char
        self.fg = list(color)

        self.time = time

        self.flammable = 4

        try:
            self.priority = Effect.PRIORITY[self.__class__.__name__]
        except KeyError:
            self.priority = 2

    def describe(self):
        return ''

    def physics(self, map):
        self.time -= 1
        if self.time <= 0:
            self.cease()

    def cease(self):
        self.cell.effect.remove(self)

    def destroy(self):
        self.cell.effect.remove(self)

    def stack(self, other):
        pass

class Fire(Effect):
    def __init__(self, cell=None, amount=1, color=COLOR['YELLOW']):
        Effect.__init__(self, cell, char='^', color=color, time=0)

        self.amount = amount
        self.flammable = -1

    def describe(self):
        return 'Fire ({:})'.format(self.amount)

    def physics(self, map):
        """Slowly decay and spawn new fog."""
        for obj in self.cell.object + self.cell.effect:
            self.burn(obj)

        if self.amount > 1:
            neigbors = filter(lambda c: not c.wall, self.cell.getNeighborhood())
            rd.shuffle(neigbors)
            for cell in neigbors:
                if self.amount > 1:
                    cell.addEffect(Fire(amount=1))
                    self.amount -= 1
        elif rd.randint(0,4) < 1:
            self.cease()

        self.cell.light += self.amount

    def burn(self, obj):
        if obj.flammable > 0:
            obj.flammable -= 1
            self.amount += 1
        if obj.flammable == 0:
            obj.destroy()

    def stack(self, other):
        self.amount += other.amount


class Fluid(Effect):
    def __init__(self, cell=None, amount=1, color=COLOR['BLUE']):
        Effect.__init__(self, cell, char='~', color=color, time=0)

        self.amount = amount

    def describe(self):
        return 'Fluid ({:})'.format(self.amount)

    def physics(self, map):
        """Slowly decay and spawn new fog."""
        if self.amount > 1:
            neigbors = filter(lambda c: not c.block[MOVE], self.cell.getNeighborhood())
            rd.shuffle(neigbors)
            for cell in neigbors:
                if self.amount > 1:
                    cell.addEffect(Fluid(amount=1))
                    self.amount -= 1
        elif rd.randint(0,500) < 1:
            self.cease()

    def stack(self, other):
        self.amount += other.amount


class Fog(Fluid):
    def __init__(self, cell=None, amount=1):
        Fluid.__init__(self, cell=cell, amount=amount, color=COLOR['WHITE'])

        self.block = [False, True]

    def describe(self):
        return 'Fog'

    def physics(self, map):
        """Slowly decay and spawn new fog."""
        if self.amount > 1:
            neigbors = filter(lambda c: not c.block[MOVE], self.cell.getNeighborhood())
            for cell in neigbors:
                if self.amount > 1 and rd.randint(0,4) < 1:
                    cell.addEffect(Fog(amount=1))
                    self.amount -= 1
        elif rd.randint(0,100) < 1:
            self.cease()
