from src.object.object import Object
from src.object.item import Item, Key, FogCloak, Canister, Lighter, Explosive, Gun
from src.effect.effect import Effect

from src.actor.ai import AI, Idle, Follow
from src.actor.actor import Actor


class NPC(Actor):
    def __init__(self, cell=None, main=None, char='@'):
        Actor.__init__(self, cell, main, char=char)

        self.ai = Idle(self)

    def describe(self, detail=False):
        name = self.__class__.__name__
        if detail:
            name += self.ai.describe()
        return name


class Guard(NPC):
    def __init__(self, cell=None, main=None, owner=None):
        NPC.__init__(self, cell, main, char='@')

        self.ai = Idle(self)
        self.inventory = [Key(carrier=self, tier=3), Key(
            carrier=self, tier=4), Gun(carrier=self)]

class Worker(NPC):
    def __init__(self, cell=None, main=None, owner=None):
        NPC.__init__(self, cell, main, char='@')

        self.ai = Idle(self)
        self.inventory = [Key(carrier=self, tier=5)]

class Drone(NPC):
    def __init__(self, cell=None, main=None, owner=None):
        NPC.__init__(self, cell, main, char='*')

        self.ai = Follow(self, None)
        self.ai.setLeader(owner)
