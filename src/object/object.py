from src.globals import *

import random as rd
import copy as cp
import itertools as it

from src.effect.effect import Fuel

class Object(object):
    PRIORITY = {'Object': 4,
                'Debris': 1,
                'Item': 8,
                'Actor': 16,
                'NPC': 16,
                'Worker': 16,
                'Guard': 24,
                'Grenade': 24,
                'Obstacle': 16,
                'Player': 32}

    def __init__(self, cell=None, char=0x100A, color=COLOR['WHITE']):
        self.cell = cell
        if cell is not None:
            self.cell.object.append(self)

        self.block = [False, False, False]  # [MOVE, LOS, LIGHT]
        self.char = char
        self.fg = np.array(color)

        self.flammable = 8

        if self.__class__.__name__ in Object.PRIORITY:
            self.priority = Object.PRIORITY[self.__class__.__name__]
        else:
            self.priority = 4

        if hasattr(self.__class__, 'ANIMATION'):
            self.animation = it.cycle(self.__class__.ANIMATION)
            for i in range(rd.randint(0, len(self.__class__.ANIMATION))):
                self.animation.next()

    def moveTo(self, pos):
        if self.cell.map.tile[pos[X]][pos[Y]].block[MOVE]:
            return False
        self.cell.object.remove(self)
        self.cell = self.cell.map.tile[pos[X]][pos[Y]]
        self.cell.map.tile[pos[X]][pos[Y]].object.append(self)
        return True

    def moveDir(self, dir):
        targetPos = self.cell.pos + dir
        return self.moveTo(targetPos)

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5
        return 0

    def describe(self):
        return "something"

    def physics(self, map):
        pass

    def destroy(self):
        if self.__class__.__name__ in ['Debris','Corpse']:
            return
        else:
#            Gui.pushMessage('The ' + self.describe() + ' is destroyed')
            self.cell.object.remove(self)
            Debris(self.cell, self)

class Debris(Object):
    def __init__(self, cell=None, obj=None):
        Object.__init__(self, cell, char=0x1025, color=(200, 200, 200))

        self.block = [False, False, False]
        self.obj = obj
        self.flammable = -1

    def interact(self, actor=None, dir=None, type=None):
        return 0

    def describe(self):
        return "Destroyed " + self.obj.describe()


class Desk(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, color=COLOR['WHITE'], char=np.random.choice([0x100A, 0x100B], p=[0.25,0.75]))

        self.block = [True, False, True]

    def describe(self):
        return "Desk"


class Hydroponics(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, color=COLOR['GREEN'])

        self.block = [False, True, True]

    def describe(self):
        return "Hydroponics"


class Obstacle(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, color=COLOR['GRAY'])

        self.block = [True, True, True]

    def interact(self, actor=None, dir=None, type=None):
        oldCell = self.cell

        if type is 'ATTACK':
            self.destroy()
            return 5
        elif self.moveDir(dir):
#            Gui.pushMessage('You push the ' + self.describe())
            oldCell.updatePhysics()
            actor.moveDir(dir)
            return 3
        else:
            return 0

    def describe(self):
        return "Chest"

class Barrel(Object):
    def __init__(self, cell=None, content=None):
        Object.__init__(self, cell, char=0x1009, color=COLOR['WHITE'])

        self.block = [True, False, True]

        if content is None:
            self.content = Fuel(amount=16)

    def interact(self, actor=None, dir=None, type=None):
        oldCell = self.cell

        if type is 'ATTACK':
            self.destroy()
            return 5
        elif self.moveDir(dir):
            # Gui.pushMessage('You push the ' + self.describe())
            oldCell.updatePhysics()
            actor.moveDir(dir)
            return 3
        else:
            return 0

    def describe(self):
        return "Barrel of " + self.content.describe()

    def destroy(self):
        # Gui.pushMessage('The ' + self.describe() + ' is destroyed')
        self.cell.object.remove(self)
        self.cell.addEffect(self.content)
        Debris(self.cell, self)
