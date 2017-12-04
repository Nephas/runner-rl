from src.globals import *

import random as rd

from src.grid.agent import Agent
from src.object.object import Object
from src.render.render import Render


class Terminal(Object):
    def __init__(self, cell=None, tier=0):
        Object.__init__(self, cell, char=0x1014, color=COLOR['MEDIUMGREEN'])

        self.on = True
        self.connection = []
        self.agents = []

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5

        self.enter(actor)
        return 3

    def describe(self):
        return "Terminal"

    def authorize(self, actor):
        for item in actor.inventory:
            if isinstance(item, Key) and item.tier == self.tier:
                Gui.pushMessage("Access granted")
                return True
        Gui.pushMessage("Access denied", COLOR['RED'])
        return False

    def enter(self, actor):
        actor.agent = Agent(actor, self)
        self.agents.append(actor.agent)
        actor.main.render.mapLayer = 1

    def connect(self, obj):
        self.cell.grid = self
        self.connection.append(obj)
        if isinstance(obj, Terminal):
            obj.connection.append(self)
            obj.cell.grid = obj

    def disconnect(self, obj):
        self.connection.remove(obj)
        if isinstance(obj, Terminal):
            obj.connection.remove(self)


class MasterSwitch(Terminal):
    def __init__(self, cell=None):
        Terminal.__init__(self, cell)

        self.char = 0x1021
        self.block = [False, False, False]

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5

        self.toggle(actor.main.map)
        return 5

    def toggle(self, map):
        if self.on:
            self.char = 0x1021
            for obj in self.cell.room.getObjects(map):
                setattr(obj, 'on', False)
        elif not self.on:
            self.char = 0x10AD
            for obj in self.cell.room.getObjects(map):
                setattr(obj, 'on', True)

    def describe(self):
        return "Switch"


class Server(Terminal):
    def __init__(self, cell=None):
        Terminal.__init__(self, cell)

        self.char = 0x1013
        self.fg = COLOR['GREEN']
        self.block = [True, True, True]

    def physics(self, map):
        self.fg = rd.choice([COLOR['GREEN'], COLOR['DARKGRAY']])

    def describe(self):
        return "Server"


class Rack(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, 0x1013)

        self.on = True
        self.fg = COLOR['GREEN']
        self.block = [True, True, True]

    def physics(self, map):
        self.fg = rd.choice([COLOR['GREEN'], COLOR['DARKGRAY']])

    def connect(self, obj):
        self.cell.grid = self

    def describe(self):
        return "Server Rack"
