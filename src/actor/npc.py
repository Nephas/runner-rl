from src.object.object import Object
from src.object.item import Item, Key, FogCloak, Canister, Lighter, Explosive, Gun
from src.effect.effect import Effect

from src.actor.ai import AI, Idle, Follow
from src.actor.actor import Actor


class NPC(Actor):
    def __init__(self, cell=None, main=None, char='@'):
        Actor.__init__(self, cell, main, char=char)

        self.ai = Idle(self)

    def act(self, map=None):
        if self.main.tic % 3 == 0:
            self.ai.switchChar()

        if self.cooldown > 0:
            self.cooldown -= 1
        elif len(self.actions) > 0:
            act = self.actions.pop(0)
            if act['TYPE'] is 'MOVE':
                dir = act['DIR']
                self.cooldown += self.moveDir(act['DIR'])
            elif act['TYPE'] in ['USE', 'ATTACK']:
                dir = act['DIR']
                self.cooldown += self.interactDir(map, act['DIR'], act['TYPE'])

        elif len(self.actions) == 0:
            self.actions = self.ai.decide(map)

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.die()
            return 10
        elif type is 'USE':
            Gui.pushMessage('Hi, how are you?', (50, 255, 50))
            self.ai = Waiting(self)
            return 5
        else:
            return 0

    def describe(self):
        return "Someone" + self.ai.describe()


class Guard(NPC):
    def __init__(self, cell=None, main=None, owner=None):
        NPC.__init__(self, cell, main, char='@')

        self.ai = Idle(self)
        self.inventory = [Key(carrier=self, tier=3), Key(
            carrier=self, tier=4), Gun(carrier=self)]

    def describe(self):
        return "Guard" + self.ai.describe()


class Worker(NPC):
    def __init__(self, cell=None, main=None, owner=None):
        NPC.__init__(self, cell, main, char='@')

        self.ai = Idle(self)
        self.inventory = [Key(carrier=self, tier=5)]

    def describe(self):
        return "Worker" + self.ai.describe()


class Drone(NPC):
    def __init__(self, cell=None, main=None, owner=None):
        NPC.__init__(self, cell, main, char='*')

        self.ai = Follow(self, None, target=owner)

    def describe(self):
        return "Your trusty drone" + self.ai.describe()
