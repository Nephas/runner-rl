from src.globals import *

from src.object.object import Object
from src.effect.effect import Fog, Fluid, Fire, Fuel, Shot, Flash
from src.gui import Gui

import pygame as pg


class Item(Object):
    def __init__(self, cell=None, carrier=None, char='i', color=COLOR['WHITE']):
        Object.__init__(self, cell, char=char, color=color)

        self.carrier = carrier

    def interact(self, actor=None, dir=None, type=None):
        Gui.pushMessage('You pickup ' + self.describe(), self.fg)
        self.take(actor)
        return 1

    def take(self, actor):
        self.carrier = actor
        actor.inventory.append(self)
        self.cell.object.remove(self)
        self.cell = self.carrier.cell

    def drop(self):
        if self.carrier is not None:
            self.carrier.cell.addObject(self)
            self.carrier.inventory.remove(self)
            self.carrier = None

    def use(self, action=None):
        Gui.pushMessage('This Item has no use')
        return 0

    def describe(self):
        return 'generic item'

class PlotDevice(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier, char='!', color=COLOR['RED'])

    def take(self, actor):
        Gui.pushMessage('You got it! Now to the extraction point!')
        self.carrier = actor
        actor.inventory.append(self)
        self.cell.object.remove(self)
        self.cell = self.carrier.cell

    def use(self, action=None):
        Gui.pushMessage('This Item has no use')
        return 0

    def describe(self):
        return 'MacGuffin'

class FogCloak(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier, char='*')

    def use(self, action=None):
        Gui.pushMessage('You release a Gas grenade')
        self.carrier.cell.addEffect(Fog(amount=16))
        return 3

    def describe(self):
        return 'Fog Cloak'

class Canister(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier, char='*')

    def use(self, action=None):
        Gui.pushMessage('You empty the canister')
        cell = self.carrier.main.map.getTile(self.carrier.cell.pos + action['DIR'])
        cell.addEffect(Fuel(amount=4))
        return 3

    def describe(self):
        return 'Canister'

class Lighter(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier, char=';')

    def use(self, action=None):
        Gui.pushMessage('You light a Fire')
        cell = self.carrier.main.map.getTile(self.carrier.cell.pos + action['DIR'])
        cell.addEffect(Fire(amount=2))
        return 3

    def describe(self):
        return 'Lighter'

class Explosive(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier, char='=')

        self.counter = -1

    def use(self, action=None):
        self.drop()
        self.counter = 20
        Gui.pushMessage('You set the counter to {}'.format(self.counter))
        return 3

    def detonate(self, map):
        map.main.sound['EXPLOSION'].play()
        self.cell.addEffect(Flash(self.cell, 14))

        for cell in self.cell.getNeighborhood(shape=4):
            cell.removeWall()
            for obj in cell.object:
                obj.destroy()
            cell.addEffect(Fire(amount=1))

    def describe(self):
        return 'Bomb'

    def physics(self, map):
        if self.counter > 0:
            self.counter -= 1
        elif self.counter == 0:
            self.detonate(map)

class Gun(Item):
    def __init__(self, cell=None, carrier=None, tier=0):
        Item.__init__(self, cell, carrier, char='$', color=TIERCOLOR[tier])

        self.tier = tier
        self.magazine = 12

    def describe(self):
        return "Gun ({:})".format(self.magazine)

    def shoot(self, start, target):
        self.carrier.main.sound['SHOT'].play()
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
        return 5

    @staticmethod
    def rayCast(start, end):
        nPoints = np.max(np.abs(end - start)) + 1

        xLine = np.linspace(start[X], end[X], nPoints).round().astype('int')
        yLine = np.linspace(start[Y], end[Y], nPoints).round().astype('int')

        line = [[x, y] for x, y in zip(xLine, yLine)]
        return np.array(line)

class Key(Item):
    def __init__(self, cell=None, carrier=None, tier=0):
        Item.__init__(self, cell, carrier, char='$', color=TIERCOLOR[tier])

        self.tier = tier

    def describe(self):
        return "Key ({:})".format(self.tier)

    def use(self, action=None):
        Gui.pushMessage('Use this key to open doors of level {:}.'.format(self.tier))
        return 0
