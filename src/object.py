from globals import *
from render import Render
import random as rd

class Object:
    def __init__(self, cell=None, char=None, color=WHITE):
        self.cell = cell
        if cell is not None:
            self.cell.object.append(self)
        self.block = [False, False]

        self.char = char
        self.fg = list(color)

    def moveTo(self, pos):
        if self.cell.map.tile[pos[X]][pos[Y]].block[MOVE]:
            return False
        self.cell.object.remove(self)
        self.cell = self.cell.map.tile[pos[X]][pos[Y]]
        self.cell.map.tile[pos[X]][pos[Y]].object.append(self)
        return True

    def moveDir(self, dir):
        targetPos = self.cell.pos + dir
        return self.moveTo(targetPos)

    def interact(self, actor=None, dir=None):
        return 0

    def describe(self):
        return "something"

    def physics(self, map):
        pass


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
        Object.__init__(self, cell, char=177, color=TIERCOLOR[tier])

        self.tier = tier
        self.closed = True
        self.block = [True, True]

    def open(self):
        self.closed = False
        self.block = [False, False]
        self.char = 95

    def close(self):
        self.closed = True
        self.block = [True, True]
        self.char = 177

    def interact(self, actor=None, dir=None):
        if self.closed:
            self.open()
        else:
            self.close()
        return 3

    def describe(self):
        return "Door ({:})".format(self.tier)


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


class Obstacle(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char=10, color=(200, 200, 200))

        self.block = [True, True]

    def interact(self, actor, dir):
        if self.moveDir(dir):
            actor.moveDir(dir)
            return 3
        else:
            return 0

    def describe(self):
        return "Chest"


class Lamp(Object):
    def __init__(self, cell=None, brightness=8):
        Object.__init__(self, cell, char=7)

        self.on = True
        self.brightness = brightness
        self.lightmap = Render.rayMap(brightness, 32)

    def physics(self, map):
        if self.on:
            self.castLight(map)

    def castLight(self, map):
        self.cell.light = 2*self.brightness
        for line in self.lightmap:
            for i, point in enumerate(line):
                cell = map.getTile(point + self.cell.pos)
                if not cell.block[LOS]:
                    cell.light = max(2*(self.brightness - i), cell.light)
                else:
                    break

    def interact(self, actor=None, dir=None):
        self.on = not self.on
        return 3

    def describe(self):
        return "Lamp"


class Terminal(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char=20)

        self.on = True
        self.connections = []

    def describe(self):
        return "Terminal"
