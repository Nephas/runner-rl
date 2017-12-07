from src.globals import *

import random as rd

from src.grid.agent import Agent
from src.object.object import Object
from src.render.render import Render


class Terminal(Object):
    ANIMATION = [0x102C, 0x102D, 0x102E, 0x102F]

    def __init__(self, cell=None, tier=0):
        Object.__init__(self, cell, char=0x1014)

        self.block = [True, True, True]

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

    def physics(self, map):
        self.char = self.animation.next()

class MasterSwitch(Terminal):
    CHAR_ON = 0x1018
    CHAR_OFF = 0x1019

    def __init__(self, cell=None):
        Terminal.__init__(self, cell)

        self.char = self.CHAR_OFF
        self.block = [False, False, False]

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5

        self.toggle(actor.main.map)
        return 5

    def toggle(self, map):
        if self.on:
            self.char = self.CHAR_ON
            for obj in self.cell.room.getObjects(map):
                setattr(obj, 'on', False)
        elif not self.on:
            self.char = self.CHAR_OFF
            for obj in self.cell.room.getObjects(map):
                setattr(obj, 'on', True)

    def describe(self):
        return "Switch"

    def physics(self, map):
        pass

class Server(Terminal):
    ANIMATION = [0x100C, 0x100D, 0x100E, 0x100F]

    def __init__(self, cell=None):
        Terminal.__init__(self, cell)

        self.on = True
        self.block = [True, True, True]

    def physics(self, map):
        self.char = self.animation.next()

    def describe(self):
        return "Server"


class Rack(Object):
    ANIMATION = [0x100C, 0x100D, 0x100E, 0x100F]

    def __init__(self, cell=None):
        Object.__init__(self, cell, 0x100C)

        self.on = True
        self.block = [True, True, True]

    def physics(self, map):
        self.char = self.animation.next()

    def connect(self, obj):
        self.cell.grid = self

    def describe(self):
        return "Server Rack"
