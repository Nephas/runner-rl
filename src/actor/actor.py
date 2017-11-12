from src.globals import *

from src.object.object import Object, Effect
from src.object.item import Item, Key

from src.actor.ai import AI, Idle

import random as rd




class Actor(Object):
    def __init__(self, cell=None, main=None, char='@', ai=None):
        Object.__init__(self, cell, char=char)

        self.main = main
        self.actions = []
        self.inventory = []

        self.block = [True, False]
        self.cooldown = 0
        self.main.actor.append(self)

        self.ai = ai

    def describe(self):
        return "Someone"

    def moveDir(self, dir):
        targetPos = self.cell.pos + dir
        if self.moveTo(targetPos):
            return np.abs(dir[X]) + np.abs(dir[Y]) + 1
        else:
            return 0

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.die()
            return 10
        else:
            return 0

    def die(self):
        self.cell.object.remove(self)
        self.main.actor.remove(self)
        Corpse(self.cell, self)
        self.main.gui.pushMessage(self.describe() + " dies")

    def interactDir(self, map, dir, type=None):
        if map.contains(self.cell.pos + dir):
            tile = map.getTile(self.cell.pos + dir)
            if type is 'ATTACK':
                tile.addObject(Effect(char='X', color=self.fg, time=2))

            if len(tile.object) > 0:
                return tile.object[0].interact(self, dir, type)
        return 0

    def act(self, map=None):
        if self.cooldown > 0:
            self.cooldown -= 1
        elif len(self.actions) > 0:
            act = self.actions.pop(0)
            if act['TYPE'] is 'MOVE':
                dir = act['DIR']
                self.cooldown += self.moveDir(act['DIR'])
            elif act['TYPE'] in ['USE','ATTACK']:
                dir = act['DIR']
                self.cooldown += self.interactDir(tileMap, act['DIR'], act['TYPE'])


class Player(Actor):
    def __init__(self, cell=None, main=None):
        Actor.__init__(self, cell, main, char='@')

        self.ai = None
        self.fg = [225, 150, 50]
        self.inventory = [Item(carrier=self), Key(carrier=self,tier=5), Key(carrier=self,tier=4), Key(carrier=self,tier=3)]

    def act(self, tileMap=None):
        if self.cooldown > 0:
            self.cooldown -= 1
        elif len(self.actions) > 0:
            act = self.actions.pop(0)
            if act['TYPE'] is 'MOVE':
                dir = act['DIR']
                self.cooldown += self.moveDir(act['DIR'])
            elif act['TYPE'] is 'ITEM':
                self.cooldown += self.inventory[act['INDEX']].use()
            elif act['TYPE'] in ['USE','ATTACK']:
                dir = act['DIR']
                self.cooldown += self.interactDir(tileMap, act['DIR'], act['TYPE'])

    def moveDir(self, dir):
        targetPos = self.cell.pos + dir
        if self.moveTo(targetPos):
            self.main.gui.moveOffset(dir)
            return np.abs(dir[X]) + np.abs(dir[Y])
        else:
            return self.interactDir(self.main.map, dir)

    def describe(self):
        return "You"

class NPC(Actor):
    def __init__(self, cell=None, main=None):
        Actor.__init__(self, cell, main, char='@')

        self.ai = Idle(self)

    def act(self, map=None):
        if self.cooldown > 0:
            self.cooldown -= 1
        elif len(self.actions) > 0:
            act = self.actions.pop(0)
            if act['TYPE'] is 'MOVE':
                dir = act['DIR']
                self.cooldown += self.moveDir(act['DIR'])
            elif act['TYPE'] in ['USE','ATTACK']:
                dir = act['DIR']
                self.cooldown += self.interactDir(tileMap, act['DIR'], act['TYPE'])

        elif len(self.actions) == 0:
            self.actions = self.ai.decide(map)

    def describe(self):
        return "Someone" + self.ai.describe()


class Corpse(Object):
    def __init__(self, cell=None, actor=None):
        Object.__init__(self, cell, char='%', color=(150, 150, 150))

        self.actor = actor

    def interact(self, actor, dir, type):
        self.moveDir(dir)
        actor.moveDir(dir)
        return 3

    def describe(self):
        return "Corpse of " + self.actor.describe()
