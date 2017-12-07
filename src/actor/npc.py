import random as rd

from src.object.object import Object
from src.object.item import Item, Key, FogCloak, Canister, Lighter, Explosive, Gun
from src.effect.effect import Effect, Fuel

from src.actor.ai import AI, Idle, Follow
from src.actor.actor import Actor, Corpse


class NPC(Actor):
    def __init__(self, cell=None, main=None, char=0x1040):
        Actor.__init__(self, cell, main, char=char)

        self.ai = Idle(self)

    def describe(self, detail=False):
        name = self.__class__.__name__
        if detail:
            name += self.ai.describe()
        return name


class Guard(NPC):
    def __init__(self, cell=None, main=None, owner=None):
        NPC.__init__(self, cell, main)

        self.ai = Idle(self)
        self.inventory = [Key(carrier=self, tier=3), Key(
            carrier=self, tier=4), Gun(carrier=self)]

class Worker(NPC):
    def __init__(self, cell=None, main=None, owner=None):
        NPC.__init__(self, cell, main)

        self.ai = Idle(self)
        self.inventory = [Key(carrier=self, tier=5)]

class Drone(NPC):
    ANIMATION = [0x101C, 0x101D, 0x101E, 0x101F]

    def __init__(self, cell=None, main=None, owner=None):
        NPC.__init__(self, cell, main, char=0x10CF)

        self.owner = owner

        if self.owner is not None:
            self.ai = Follow(self, None)
            self.ai.setLeader(owner)
        else:
            self.ai = Idle(self)

    def physics(self, map):
        self.char = self.animation.next()

    def die(self):
        if self.__class__.__name__ in ['Corpse', 'Debris']:
            return
        else:
            self.cell.object.remove(self)
            for item in self.inventory:
                item.drop()
            self.main.actor.remove(self)
            Corpse(self.cell, self)
            self.cell.addEffect(Fuel(amount=rd.randint(1,3)))
