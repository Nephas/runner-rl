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


class Terminal(Object):
    def __init__(self, cell):
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


class Server(Terminal):
    def __init__(self, cell):
        Terminal.__init__(self, cell)

        self.char = 19
        self.fg = COLOR['GREEN']
        self.block = [True, True]

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5

        for obj in self.connection:
            obj.cell.vision = [True, True]
            actor.main.gui.pushMessage(obj.describe(), obj.fg)
        return 5

    def physics(self, map):
        self.fg = rd.choice([COLOR['GREEN'], COLOR['DARKGRAY']])

    def describe(self):
        return "Server"
