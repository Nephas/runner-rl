from src.globals import *

from src.object.object import Object
from src.object.item import Item, Key, FogCloak, Canister, Lighter, Explosive, Gun, Shotgun
from src.effect.effect import Effect

from src.actor.ai import AI, Idle, Follow
from src.actor.body import Body
from src.gui import Gui

import random as rd




class Actor(Object):
    def __init__(self, cell=None, main=None, char='@', ai=None):
        Object.__init__(self, cell, char=char)

        self.main = main
        self.actions = []
        self.inventory = []

        self.block = [True, False, False]
        self.cooldown = 0
        self.main.actor.append(self)

        self.ai = AI(self)
        self.body = Body(self)

    def describe(self):
        return "Someone"

    def moveDir(self, dir, speed=1):
        targetPos = self.cell.pos + dir
        if self.moveTo(targetPos):
            return np.abs(dir[X]) + np.abs(dir[Y]) + 2 - speed
        else:
            return 0

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.die()
            return 10
        else:
            return 0

    def destroy(self):
        self.die()

    def die(self):
        self.cell.object.remove(self)
        for item in self.inventory:
            item.drop()
        self.main.actor.remove(self)
        Corpse(self.cell, self)
        Gui.pushMessage(self.describe() + " dies")

    def interactDir(self, map, dir, type=None):
        tile = map.getTile(self.cell.pos + dir)
        if type is 'ATTACK':
            tile.addEffect(Effect(char='X', time=2))

        if len(tile.object) > 0:
            return tile.object[0].interact(self, dir, type)
        return 0

    def act(self, tileMap=None):
        if self.cooldown > 0:
            self.cooldown -= 1
        elif len(self.actions) > 0:
            act = self.actions.pop(0)
            if act['TYPE'] is 'MOVE':
                dir = act['DIR']
                self.cooldown += self.moveDir(act['DIR'])
            elif act['TYPE'] is 'ITEM':
                self.cooldown += self.inventory[act['INDEX']].use(act)
            elif act['TYPE'] in ['USE','ATTACK']:
                dir = act['DIR']
                self.cooldown += self.interactDir(tileMap, act['DIR'], act['TYPE'])


class Player(Actor):
    def __init__(self, cell=None, main=None):
        Actor.__init__(self, cell, main, char='@')

        self.fg = [225, 150, 50]
        self.inventory = [FogCloak(carrier=self), Canister(carrier=self), Lighter(carrier=self),
                          Key(carrier=self,tier=5), Shotgun(carrier=self), Explosive(carrier=self)]

    def moveDir(self, dir):
        targetPos = self.cell.pos + dir
        if self.moveTo(targetPos):
            self.main.gui.moveOffset(dir)
            return np.abs(dir[X]) + np.abs(dir[Y])
        else:
            return self.interactDir(self.main.map, dir)

    def castFov(self, map):
        self.ai.castFov(map, self.cell.pos)

    def describe(self):
        return "You"


class Corpse(Object):
    def __init__(self, cell=None, actor=None):
        Object.__init__(self, cell, char='%', color=(150, 150, 150))

        self.actor = actor
        self.flammable = -1

    def interact(self, actor, dir, type):
        self.moveDir(dir)
        actor.moveDir(dir)
        return 3

    def describe(self):
        return "Corpse of " + self.actor.describe()
