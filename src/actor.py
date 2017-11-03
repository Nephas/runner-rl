from globals import *
from object import Object
from item import Item, Key

import random as rd

class AI:
    def __init__(self):
        pass

    @staticmethod
    def decide(actor, map):
        return actor.moveDir(rd.choice(NEIGHBORHOOD))
#            return 2
#        else:
#            return 0

class Actor(Object):
    def __init__(self, cell=None, main=None, char='@'):
        Object.__init__(self, cell, char=char)

        self.main = main
        self.block = [True, False]
        self.cooldown = 0
        self.main.actor.append(self)

    def describe(self):
        return "Someone"

    def moveDir(self, dir):
        targetPos = self.cell.pos + dir
        if self.moveTo(targetPos):
            return np.abs(dir[X]) + np.abs(dir[Y]) + 1
        else:
            return 0

    def interact(self, actor=None, dir=None):
        self.die()
        return 10

    def die(self):
        self.cell.object.remove(self)
        self.main.actor.remove(self)
        Corpse(self.cell, self)
        self.main.gui.pushMessage(self.describe() + " dies")

    def interactDir(self, map, dir):
        tile = map.getTile(self.cell.pos + dir)
        if len(tile.object) > 0:
            return tile.object[0].interact(self, dir)
        else:
            return 0

    def act(self, map=None):
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            self.cooldown += AI.decide(self, map)


class Player(Actor):
    def __init__(self, cell=None, main=None):
        Actor.__init__(self, cell, main, char='@')

        self.fg = [225, 200, 100]
        self.inventory = [Item(), Key(tier=5)]

    def act(self, tileMap=None):
        actions = self.main.input.actions

        if self.cooldown > 0:
            self.cooldown -= 1
        elif len(actions) > 0:
            if actions[0]['TYPE'] is 'MOVE':
                dir = sum(map(lambda a: a['DIR'], actions))
                for coord in [X,Y]:
                    if np.abs(dir[coord]) > 1:
                        dir[coord] /= np.abs(dir[coord])
                self.cooldown += self.moveDir(dir)
            elif actions[0]['TYPE'] is 'USE':
                dir = actions[0]['DIR']
                self.cooldown += self.interactDir(tileMap, dir)
            self.main.input.actions = []

    def moveDir(self, dir):
        targetPos = self.cell.pos + dir
        if self.moveTo(targetPos):
            self.main.gui.moveOffset(dir)
            return np.abs(dir[X]) + np.abs(dir[Y]) + 1
        else:
            return self.interactDir(self.main.map,dir)

    def describe(self):
        return "You"


class Corpse(Object):
    def __init__(self, cell=None, actor=None):
        Object.__init__(self, cell, char='%', color=(150, 150, 150))

        self.actor = actor

    def interact(self, actor, dir):
        self.moveDir(dir)
        actor.moveDir(dir)
        return 3

    def describe(self):
        return "Corpse of " + self.actor.describe()
