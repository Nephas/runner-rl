from src.globals import *

import random as rd
import numpy as np

from src.render.geometry import Light
#from src.grid.electronics import Electronics
#from src.actor.actor import actor


class Effect(object):
    PRIORITY = {'Effect': 24,
                'Fluid': 2,
                'Fuel': 12,
                'Fog': 24,
                'Fire': 24,
                'Shot': 24}

    def __init__(self, cell=None, char=0x1004, color=COLOR['RED'], time=1):
        self.cell = cell
        if cell is not None:
            self.cell.effect.append(self)
        self.block = [False, False, False]  # [MOVE, LOS]

        self.char = char
        self.fg = np.array(color)

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
    BASE_COLOR = np.array(COLOR['FIRE'])

    def __init__(self, cell=None, amount=1, color=COLOR['FIRE']):
        Effect.__init__(self, cell, char=0x1003, color=color, time=0)

        self.time = rd.randint(0, 10)
        self.amount = amount
        self.flammable = -1

        self.fg = (min(self.amount + 4, MAX_LIGHT) /
                   float(MAX_LIGHT) * self.BASE_COLOR).astype('int')

    def describe(self):
        return 'Fire ({:})'.format(self.amount)

    def physics(self, map):
        """Slowly decay and spawn new fire."""
        if self.time % 5 == 0:
            for obj in self.cell.object + self.cell.effect:
                self.burn(obj)

            if self.amount > 1:
                neigbors = filter(lambda c: not c.wall,
                                  self.cell.getNeighborhood())
                rd.shuffle(neigbors)
                for cell in neigbors:
                    if self.amount > 1 and rd.randint(0, 4) < 1:
                        cell.addEffect(Fire(amount=1))
                        self.amount -= 1
            elif rd.randint(1, 2) == 1:
                self.cease()
                self.cell.addEffect(Smoke())

        self.time += 1
        self.cell.light = min(self.cell.light + self.amount, MAX_LIGHT)
        self.fg = (min(self.amount + 4, MAX_LIGHT) /
                   float(MAX_LIGHT) * self.BASE_COLOR).astype('int')

    def burn(self, obj):
        if obj.flammable > 0:
            obj.flammable -= 1
            self.amount += 1
        if obj.flammable == 0:
            obj.destroy()


class EMP(Effect):
    def __init__(self, cell=None, amount=1, color=COLOR['GRAY']):
        Effect.__init__(self, cell, char=0x1006, color=color)

        self.amount = amount

    def describe(self):
        return 'EMP'

    def physics(self, map):
        if self.amount <= 0:
            self.cease()
        self.amount -= 1
        for obj in self.cell.object:
            if hasattr(obj, 'on'):
                obj.destroy()
            if hasattr(obj, 'ai'):
                obj.ai.stun()


class Shot(Effect):
    def __init__(self, cell=None, char=0x10FA, amount=1, color=COLOR['GRAY']):
        Effect.__init__(self, cell, char, color=color)

        self.amount = amount

    def describe(self):
        return 'Shot'

    def physics(self, map):
        if self.amount <= 0:
            self.cease()
        self.amount -= 1
        for obj in self.cell.object:
            obj.destroy()


class Slash(Effect):
    def __init__(self, cell=None, char=0x1025, amount=1, color=COLOR['BLOOD']):
        Effect.__init__(self, cell, char, color=color)

        self.amount = amount

    def describe(self):
        return 'Slash'

    def physics(self, map):
        if self.amount <= 0:
            self.cease()
        self.amount -= 1
        for obj in self.cell.object:
            obj.destroy()


class Fluid(Effect):
    BASE_COLOR = np.array(COLOR['BLUE'])

    def __init__(self, cell=None, char=0x1004, amount=1, decay=0.001, color=COLOR['BLUE']):
        Effect.__init__(self, cell, char, color=color)

        self.amount = amount
        self.decay = decay
        self.fg = (min(self.amount + 4, MAX_LIGHT) /
                   float(MAX_LIGHT) * self.BASE_COLOR).astype('int')
        self.flammable = -1

    def describe(self):
        return 'Fluid ({:})'.format(self.amount)

    def physics(self, map):
        if self.amount > 1:
            neigbors = filter(
                lambda c: not c.block[MOVE], self.cell.getNeighborhood())
            rd.shuffle(neigbors)
            for cell in neigbors:
                if self.amount > 1:
                    cell.addEffect(self.__class__(amount=1))
                    self.amount -= 1
                    self.fg = (min(self.amount + 4, MAX_LIGHT) /
                               float(MAX_LIGHT) * self.BASE_COLOR).astype('int')
        elif rd.random() <= self.decay:
            self.cease()


class GrayGoo(Effect):
    BASE_COLOR = np.array(COLOR['PURPLE'])

    def __init__(self, cell=None, amount=1):
        Fluid.__init__(self, cell=cell, char=0x1004,
                       amount=amount, color=COLOR['PURPLE'])

        self.block = [False, False, False]
        self.flammable = 8

    def describe(self):
        return 'Fuel'


class Fuel(Fluid):
    BASE_COLOR = np.array(COLOR['PURPLE'])

    def __init__(self, cell=None, amount=1):
        Fluid.__init__(self, cell=cell, char=0x1004,
                       amount=amount, color=COLOR['PURPLE'])

        self.block = [False, False, False]
        self.flammable = 8

    def describe(self):
        return 'Fuel'


class Blood(Fluid):
    BASE_COLOR = np.array(COLOR['BLOOD'])

    def __init__(self, cell=None, amount=1):
        Fluid.__init__(self, cell=cell, char=0x1004,
                       amount=amount, color=COLOR['BLOOD'])

        self.block = [False, False, False]
        self.flammable = -1

    def describe(self):
        return 'Blood'


class Smoke(Fluid):
    BASE_COLOR = np.array(COLOR['GRAY'])

    def __init__(self, cell=None, amount=1):
        Fluid.__init__(self, cell=cell, char=0x1005,
                       amount=amount, decay=0.2, color=COLOR['WHITE'])

        self.block = [False, False, True]
        self.flammable = -1

    def describe(self):
        return 'Smoke'


class Fog(Fluid):
    BASE_COLOR = np.array(COLOR['WHITE'])

    def __init__(self, cell=None, amount=1):
        Fluid.__init__(self, cell=cell, char=0x1005,
                       amount=amount, decay=0.01, color=COLOR['WHITE'])

        self.block = [False, True, True]
        self.flammable = -1

    def describe(self):
        return 'Fog'


class Flash(Effect):
    def __init__(self, cell=None, brightness=7):
        Effect.__init__(self, cell, char=0x1007, color=COLOR['WHITE'])

        self.brightness = brightness
        self.amount = 1

    def physics(self, map):
        if self.amount <= 0:
            self.cease()
        self.amount -= 1

        Light.cast(map, self.cell.pos, self.brightness)


class Holotext(Effect):
    def __init__(self, cell=None, text='Holo', length=8, color=COLOR['WHITE']):
        Effect.__init__(self, cell, color=color)

        self.amount = 1
        self.text = text
        self.length = length
        self.char = text
        self.offset = 0

    def physics(self, map):
        if self.cell.map.main.tic % 2 == 0:
            self.offset = (self.offset + 1) % len(self.text)
            self.char = (2*self.text)[self.offset:self.offset + self.length]

        if self.amount <= 0:
            self.cease()
        self.amount -= 1

    def stack(self, other):
        self.amount = min(16, self.amount + other.amount)
