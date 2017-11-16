from src.globals import *

import random as rd

from src.object.object import Object
from src.render import Render

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
        self.block = [True, False, True]

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
