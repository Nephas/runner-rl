from src.globals import *

from src.object.object import Object
from src.effect.effect import Fog, Fluid, Fire, Fuel, Shot, Flash, Slash

import copy as cp
import random as rd
import numpy as np
import itertools as it


class Item(Object):
    ANIMATION = [0x2000, 0x2010, 0x2020, 0x2030]

    def __init__(self, cell=None, carrier=None, char=0x1021, icon=0x2000, color=COLOR['WHITE']):
        Object.__init__(self, cell, char=char, color=color)

        self.carrier = carrier
        self.icon = icon
        self.frame = 0

        if hasattr(self.__class__, 'ANIMATION'):
            self.animation = it.cycle(self.__class__.ANIMATION)

    def interact(self, actor=None, dir=None, type=None):
        # Gui.pushMessage('You pickup ' + self.describe(), self.fg)
        self.take(actor)
        return 1

    def get(self):
        return self

    def destroy(self):
        if self.carrier is not None and self in self.carrier.inventory:
            self.carrier.inventory.remove(self)
        if self.cell is not None and self in self.cell.object:
            self.cell.object.remove(self)

    def take(self, actor):
        self.carrier = actor
        actor.inventory.append(self)
        self.cell.object.remove(self)
        self.cell = self.carrier.cell

    def drop(self):
        if self.carrier is not None:
            cells = filter(lambda c: c.isEmpty(),
                           self.carrier.cell.getNeighborhood('LARGE'))
            if len(cells) != 0:
                rd.choice(cells).addObject(self)
            else:
                self.carrier.cell.addObject(self)

            self.carrier.inventory.remove(self)
            self.carrier = None

    def use(self, action=None):
        self.frame = len(self.ANIMATION)
        # Gui.pushMessage('This Item has no use')
        return 0

    def physics(self, map):
        if self.frame > 0:
            self.icon = self.animation.next()
            self.frame -= 1

    def describe(self):
        return 'generic item'


class PlotDevice(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier, char=0x102B)

    def take(self, actor):
        # Gui.pushMessage('You got it! Now to the extraction point!')
        self.carrier = actor
        actor.inventory.append(self)
        self.cell.object.remove(self)
        self.cell = self.carrier.cell

    def use(self, action=None):
        # Gui.pushMessage('This Item has no use')
        return 0

    def describe(self):
        return 'MacGuffin'


class FogCloak(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier)

    def use(self, action=None):
        # Gui.pushMessage('You release a Gas grenade')
        self.carrier.cell.addEffect(Fog(amount=16))
        return 3

    def describe(self):
        return 'Fog Cloak'


class Canister(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier)

    def use(self, action=None):
        # Gui.pushMessage('You empty the canister')
        cell = self.carrier.main.map.getTile(
            self.carrier.cell.pos + action['DIR'])
        cell.addEffect(Fuel(amount=4))
        return 3

    def describe(self):
        return 'Canister'


class Lighter(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier)

    def use(self, action=None):
        # Gui.pushMessage('You light a Fire')
        cell = self.carrier.main.map.getTile(
            self.carrier.cell.pos + action['DIR'])
        cell.addEffect(Fire(amount=2))
        return 3

    def describe(self):
        return 'Lighter'


class Key(Item):
    def __init__(self, cell=None, carrier=None, tier=0, color=COLOR['WHITE']):
        Item.__init__(self, cell, carrier, char=0x102A, color=color)

        self.tier = tier

    def describe(self):
        return "Key ({:})".format(self.tier)

    def use(self, action=None):
        # Gui.pushMessage('Use this key to open doors of level {:}.'.format(self.tier))
        return 0
