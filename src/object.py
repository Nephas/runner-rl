from globals import *


class Object:
    def __init__(self, cell=None, char=None, color=WHITE):
        self.cell = cell
        if cell is not None:
            self.cell.object.append(self)
        self.block = [False, False]

        self.char = char
        self.fg = color

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

    def interact(self, actor=None, dir=None):
        return 0

    def physics(self, map):
        pass

class Player(Object):
    def __init__(self, cell=None, parent=None):
        Object.__init__(self, cell, char='@')

        self.parent = parent

    def moveTo(self, pos):
        if self.cell.map.tile[pos[X]][pos[Y]].block[MOVE]:
            return False
        self.cell.object.remove(self)
        self.cell = self.cell.map.tile[pos[X]][pos[Y]]
        self.cell.map.tile[pos[X]][pos[Y]].object.append(self)
        return True


class Vent(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char='#', color=(100, 100, 100))

        self.block = [False, True]

    def interact(self,actor=None, dir=None):
        return 10


class Door(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char=225, color=[220, 220, 220])

        self.closed = True
        self.block = [True, True]

    def interact(self, actor=None,dir=None):
        self.block = [not self.closed, not self.closed]
        self.closed = not self.closed

        if self.closed:
            self.char = 225
        else:
            self.char = 224

        return 5


class Obstacle(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char=206, color=(200, 200, 200))

        self.block = [True, True]

    def interact(self, actor, dir):
        self.moveDir(dir)
        actor.moveDir(dir)
        return 5

class Lamp(Object):
    def __init__(self, cell=None):
        Object.__init__(self, cell, char='*')

    def physics(self, map):
        map.castLight(self.cell.pos)
