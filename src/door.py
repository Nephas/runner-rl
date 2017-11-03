from globals import *

from object import Object
from item import Key

class Vent(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char='#', color=(100, 100, 100))

        self.block = [False, True]

    def interact(self, actor=None, dir=None):
        self.cell.object.remove(self)
        return 10

    def describe(self):
        return "Vent"


class Door(Object):
    def __init__(self, cell=None, tier=0):
        Object.__init__(self, cell, char=178, color=TIERCOLOR[tier])

        self.tier = tier
        self.closed = True
        self.block = [True, True]

    def open(self):
        self.closed = False
        self.block = [False, False]
        self.char = 177

    def close(self):
        self.closed = True
        self.block = [True, True]
        self.char = 178

    def interact(self, actor=None, dir=None):
        if self.closed:
            self.open()
        else:
            self.close()
        return 3

    def describe(self):
        return "Door ({:})".format(self.tier)

class SecDoor(Door):
    def __init__(self, cell=None, tier=0):
        Door.__init__(self, cell, tier)

    def open(self, actor):
        if self.authorize(actor):
            self.closed = False
            self.block = [False, False]
            self.char = 177

    def close(self, actor):
        if self.authorize(actor):
            self.closed = True
            self.block = [True, True]
            self.char = 178

    def authorize(self, actor):
        for item in actor.inventory:
            if isinstance(item, Key) and item.tier == self.tier:
                actor.main.gui.pushMessage("Access granted")
                return True
        actor.main.gui.pushMessage("Access denied")
        return False

    def interact(self, actor=None, dir=None):
        if self.closed:
            self.open(actor)
        else:
            self.close(actor)
        return 3

    def describe(self):
        return "SecDoor ({:})".format(self.tier)


class AutoDoor(Door):
    def __init__(self, cell=None, tier=0):
        Door.__init__(self, cell, tier=tier)

    def physics(self, map):
        obj = 0
        for cell in map.getNeighborhood(self.cell.pos) + [self.cell]:
            obj += len(cell.object)
        if obj > 1:
            self.open()
        else:
            self.close()

    def interact(self, actor=None, dir=None):
        return 0

    def describe(self):
        return "Autodoor ({:})".format(self.tier)
