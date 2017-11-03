from globals import *
from object import Object


class Item(Object):
    def __init__(self, cell=None, carrier=None, char='i', color=WHITE):
        Object.__init__(self, cell, char=char, color=color)

        self.carrier = None
        if carrier is not None:
            self.take(carrier)

    def interact(self, actor=None, dir=None):
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
        pass

    def describe(self):
        return "generic item"


class Key(Item):
    def __init__(self, cell=None, carrier=None, tier=0):
        Object.__init__(self, cell, char='$', color=TIERCOLOR[tier])

        self.tier = tier

    def describe(self):
        return "Key ({:})".format(self.tier)
