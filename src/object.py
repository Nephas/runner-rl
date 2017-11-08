from globals import *
from render import Render
import random as rd


class Object(object):
    def __init__(self, cell=None, char=None, color=COLOR['WHITE']):
        self.cell = cell
        if cell is not None:
            self.cell.object.append(self)
        self.block = [False, False]  # [MOVE, LOS]

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

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5
        return 0

    def describe(self):
        return "something"

    def physics(self, map):
        pass

    def destroy(self):
        self.cell.object.remove(self)
        Debris(self.cell, self)


class Debris(Object):
    def __init__(self, cell=None, obj=None):
        Object.__init__(self, cell, char='%', color=(200, 200, 200))

        self.block = [False, False]
        self.obj = obj

    def interact(self, actor=None, dir=None, type=None):
        #        self.moveDir(dir)
        #        actor.moveDir(dir)
        return 0

    def describe(self):
        return "Destroyed " + self.obj.describe()


class Obstacle(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char=10, color=(200, 200, 200))

        self.block = [True, True]

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5
        elif self.moveDir(dir):
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
        self.cell.light = 2 * self.brightness
        for line in self.lightmap:
            for i, point in enumerate(line):
                cell = map.getTile(point + self.cell.pos)
                if not cell.block[LOS]:
                    cell.light = max(2 * (self.brightness - i), cell.light)
                else:
                    break

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5
        else:
            self.on = not self.on
            return 3

    def describe(self):
        return "Lamp"


class Terminal(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char=20, color=COLOR['MEDIUMGREEN'])

        self.on = True
        self.cell.grid = True
        self.connection = []

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5

        self.connection[0].interact(actor)
        return 3

    def describe(self):
        return "Terminal"

    def connect(self, obj):
        self.cell.grid = True
        self.connection.append(obj)
        if isinstance(obj, Terminal):
            obj.connection.append(self)
            obj.cell.grid = True

    def disconnect(self, obj):
        self.connection.remove(obj)
        if isinstance(obj, Terminal):
            obj.connection.remove(self)
