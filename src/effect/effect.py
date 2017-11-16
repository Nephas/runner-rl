from src.globals import *

import random as rd

from src.render import Render
from src.gui import Gui

class Effect(object):
    PRIORITY = {'Effect': 24,
                'Fluid': 2,
                'Fuel': 4,
                'Fog': 24,
                'Fire': 24}

    def __init__(self, cell=None, char='+', color=COLOR['RED'], bgColor=None, time=1):
        self.cell = cell
        if cell is not None:
            self.cell.effect.append(self)
        self.block = [False, False, False]  # [MOVE, LOS]

        self.char = char
        self.fg = list(color)

        self.time = time

        self.flammable = -1

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
        try:
            self.cell.effect.remove(self)
        except:
            pass

    def destroy(self):
        self.cease()

    def stack(self, other):
        self.amount = min(16, self.amount + other.amount)

class Fire(Effect):
    def __init__(self, cell=None, amount=1, color=COLOR['YELLOW']):
        Effect.__init__(self, cell, char='^', color=color, time=0)

        self.time = rd.randint(0,10)
        self.amount = amount
        self.flammable = -1

        self.bg = COLOR['FIRE']

    def describe(self):
        return 'Fire ({:})'.format(self.amount)

    def physics(self, map):
        """Slowly decay and spawn new fire."""
        if self.time % 5 == 0:
            for obj in self.cell.object + self.cell.effect:
                self.burn(obj)

            if self.amount > 1:
                neigbors = filter(lambda c: not c.wall, self.cell.getNeighborhood())
                rd.shuffle(neigbors)
                for cell in neigbors:
                    if self.amount > 1 and rd.randint(0,4) < 1:
                        cell.addEffect(Fire(amount=1))
                        self.amount -= 1
            elif rd.randint(1,2) == 1:
                self.cease()
                self.cell.addEffect(Smoke())


        self.time += 1
        self.cell.light = min(self.cell.light + self.amount, MAX_LIGHT)

    def burn(self, obj):
        if obj.flammable > 0:
            obj.flammable -= 1
            self.amount += 1
        if obj.flammable == 0:
            obj.destroy()


class Fluid(Effect):
    def __init__(self, cell=None, char=247, amount=1, color=COLOR['BLUE']):
        Effect.__init__(self, cell, char, color=color)

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
        elif rd.randint(0,1000) < 1:
            self.cease()


class Fuel(Fluid):
    def __init__(self, cell=None, amount=1):
        Fluid.__init__(self, cell=cell, char=126, amount=amount, color=COLOR['PURPLE'])

        self.block = [False, False, False]
        self.bg = COLOR['PURPLE']
        self.flammable = 8

    def describe(self):
        return 'Fuel'

    def physics(self, map):
        """Slowly decay and spawn new fog."""
        if self.amount > 1:
            neigbors = filter(lambda c: not c.block[MOVE], self.cell.getNeighborhood())
            rd.shuffle(neigbors)
            for cell in neigbors:
                if self.amount > 1:
                    cell.addEffect(Fuel(amount=1))
                    self.amount -= 1
        elif rd.randint(0,500) < 1:
            self.cease()

class Smoke(Fluid):
    def __init__(self, cell=None, amount=1):
        Fluid.__init__(self, cell=cell, char=126, amount=amount, color=COLOR['WHITE'])

        self.block = [False, False, True]
        self.bg = COLOR['WHITE']
        self.flammable = -1

    def describe(self):
        return 'Smoke'

    def physics(self, map):
        """Slowly decay and spawn new fog."""
        if self.amount > 1:
            neigbors = filter(lambda c: not c.block[MOVE], self.cell.getNeighborhood())
            for cell in neigbors:
                if self.amount > 1 and rd.randint(0,4) < 1:
                    cell.addEffect(Smoke(amount=1))
                    self.amount -= 1
        elif rd.randint(0,50) < 1:
            self.cease()

class Fog(Fluid):
    def __init__(self, cell=None, amount=1):
        Fluid.__init__(self, cell=cell, char=126, amount=amount, color=COLOR['WHITE'])

        self.block = [False, True, True]
        self.bg = COLOR['WHITE']
        self.flammable = -1

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
