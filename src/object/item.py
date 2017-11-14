from src.globals import *

from src.object.object import Object
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

    def use(self):
        Gui.pushMessage('This Item has no use')
        return 0

    def describe(self):
        return 'generic item'


class Key(Item):
    def __init__(self, cell=None, carrier=None, tier=0):
        Item.__init__(self, cell, carrier, char='$', color=TIERCOLOR[tier])

        self.tier = tier

    def describe(self):
        return "Key ({:})".format(self.tier)

    def use(self):
        Gui.pushMessage('Use this key to open doors of level {:}.'.format(self.tier))
        return 0
