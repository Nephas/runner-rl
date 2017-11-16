from src.globals import *

from src.object.object import Object
from src.effect.effect import Fog, Fluid, Fire, Fuel
from src.gui import Gui


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
        if carrier is not None:
            self.carrier.cell.addObject(self)
            self.carrier.inventory.remove(self)
            self.carrier = None

    def use(self, dir=None):
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

    def use(self, dir=None):
        Gui.pushMessage('This Item has no use')
        return 0

    def describe(self):
        return 'MacGuffin'

class FogCloak(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier, char='*')

    def use(self, dir=None):
        Gui.pushMessage('You release a Gas grenade')
        self.carrier.cell.addEffect(Fog(amount=16))
        return 3

    def describe(self):
        return 'Fog Cloak'

class Canister(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier, char='*')

    def use(self, dir=None):
        Gui.pushMessage('You empty the canister')
        cell = self.carrier.main.map.getTile(self.carrier.cell.pos + dir)
        cell.addEffect(Fuel(amount=4))
        return 3

    def describe(self):
        return 'Canister'

class Lighter(Item):
    def __init__(self, cell=None, carrier=None):
        Item.__init__(self, cell, carrier, char=';')

    def use(self, dir=None):
        Gui.pushMessage('You light a Fire')
        cell = self.carrier.main.map.getTile(self.carrier.cell.pos + dir)
        cell.addEffect(Fire(amount=2))
        return 3

    def describe(self):
        return 'Lighter'

class Key(Item):
    def __init__(self, cell=None, carrier=None, tier=0):
        Item.__init__(self, cell, carrier, char='$', color=TIERCOLOR[tier])

        self.tier = tier

    def describe(self):
        return "Key ({:})".format(self.tier)

    def use(self, dir=None):
        Gui.pushMessage('Use this key to open doors of level {:}.'.format(self.tier))
        return 0
