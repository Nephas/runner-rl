from src.globals import *

from src.object.object import Object
from src.object.item import Item, Key, Knife, FogCloak, Canister, Lighter, Explosive, Gun, Injector, Shotgun, Grenade
from src.effect.effect import Effect, Blood

from src.actor.ai import AI, Idle, Follow
from src.actor.person import Person
from src.actor.conversation import Conversation
from src.actor.body import Body

import random as rd


class Actor(Object):
    def __init__(self, cell=None, main=None, char=0x1031, ai=None):
        Object.__init__(self, cell, char=char)

        self.main = main
        self.actions = []
        self.inventory = []

        self.block = [True, False, False]
        self.cooldown = 0
        self.main.actor.append(self)

        self.ai = AI(self)
        self.person = Person(self)
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
        elif type is 'USE' and self.__class__.__name__ is not 'Player':
            self.ai.switchState(Conversation)
            self.ai.mind['TARGET'] = actor
            actor.ai.mind['TARGET'] = self
            return 3
        else:
            return 0

    def destroy(self):
        if self.__class__.__name__ in ['Corpse', 'Debris']:
            return
        self.die()

    def die(self):
        if self.__class__.__name__ in ['Corpse', 'Debris']:
            return
        else:
            self.cell.object.remove(self)
            for item in self.inventory:
                item.drop()
            self.main.actor.remove(self)
            Corpse(self.cell, self)
            self.cell.addEffect(Blood(amount=rd.randint(1, 3)))
            # Gui.pushMessage(self.describe() + " dies")

    def interactWith(self, map, dir, type=None):
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
            elif act['TYPE'] in ['USE', 'ATTACK']:
                dir = act['DIR']
                self.cooldown += self.interactWith(tileMap,
                                                   act['DIR'], act['TYPE'])
            elif act['TYPE'] is 'TALK' and act['TARGET'] is not None:
                self.cooldown += act['TARGET'].ai.chooseOption(act['INDEX'])
            elif act['TYPE'] is 'GRID':
                self.cooldown += self.agent.moveTo(act['TARGET'])

        elif len(self.actions) == 0:
            self.actions = self.ai.decide(tileMap)

    def physics(self, map):
        self.body.physics(map)


class Player(Actor):
    ANIMATION = [0x1031, 0x1031, 0x1041, 0x1041]

    def __init__(self, cell=None, main=None):
        Actor.__init__(self, cell, main, char=0x1031)

#        self.fg = COLOR[]# [225, 150, 50]
        self.inventory = [Knife(carrier=self), Canister(carrier=self), Grenade(carrier=self),
                          Lighter(carrier=self), Key(carrier=self,
                                                     tier=4), Shotgun(carrier=self),
                          Explosive(carrier=self), Injector(carrier=self)]

        self.agent = None

    def moveDir(self, dir):
        targetPos = self.cell.pos + dir
        if self.moveTo(targetPos):
            self.main.render.mapPanel.moveOffset(dir)
            return np.abs(dir[X]) + np.abs(dir[Y])
        else:
            return self.interactWith(self.main.map, dir)

    def castFov(self, map):
        self.ai.castFov(map, self.cell.pos)
        if self.agent is not None:
            self.agent.castFov(map)

    def physics(self, map):
        self.char = self.animation.next()

    def describe(self):
        return "You"


class Corpse(Object):
    def __init__(self, cell=None, actor=None):
        Object.__init__(self, cell, char=0x1011, color=(150, 150, 150))

        self.actor = actor
        self.flammable = -1

    def interact(self, actor, dir, type):
        self.moveDir(dir)
        actor.moveDir(dir)
        return 3

    def describe(self):
        return "Corpse of " + self.actor.describe()
