from globals import *
from object import Object

import random as rd

class AI:
    def __init__(self):
        pass

    @staticmethod
    def decide(actor, map):
        if actor.moveDir(rd.choice(NEIGHBORHOOD)):
            return 2
        else:
            return 0

class Actor(Object):
    def __init__(self, cell=None, main=None, char='@'):
        Object.__init__(self, cell, char=char)

        self.main = main
        self.block = [True, False]
        self.cooldown = 0
        self.main.actor.append(self)

    def describe(self):
        return "Someone"

    def act(self, map=None):
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            self.cooldown += AI.decide(self, map)


class Player(Actor):
    def __init__(self, cell=None, main=None):
        Actor.__init__(self, cell, main, char='@')

        self.fg = [225, 200, 100]

    def act(self, map=None):
        if self.cooldown > 0:
            self.cooldown -= 1

    def describe(self):
        return "You"
