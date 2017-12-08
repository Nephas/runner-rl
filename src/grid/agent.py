from src.globals import *

from src.grid.grid import Wire

class Agent(object):
    def __init__(self, actor=None, cell=None, char=0x1040, color=COLOR['WHITE']):
        self.actor = actor
        self.cooldown = 0
        self.actions = []
        self.route = []

        self.char = char
        self.fg = list(color)

        self.create(cell)

    def create(self, cell):
        self.actor.main.agent.append(self)
        self.actor.agent = self
        self.grid = cell.grid
        self.grid.agent.append(self)
        self.route = [cell.grid]

    def destroy(self):
        self.actor.main.agent.remove(self)
        self.actor.agent = None
        self.grid.agent.remove(self)
        self.actor.main.render.mapPanel.layer = 'MAP'

    def moveTo(self, newGrid):
        if newGrid.object == [] or not hasattr(newGrid.object[0], 'connection'):
            return 0
        elif newGrid.object[0] in self.grid.object[0].connection:
            self.grid.agent.remove(self)
            newGrid.agent.append(self)
            self.grid = newGrid

            if newGrid.object[0] in self.route:
                self.route.pop(-1)
            else:
                self.route.append(newGrid.object[0])

            return 2
        else:
            return 0

    def describe(self):
        return 'Agent'

    def act(self, tileMap=None):
        if not self.checkRoute():
            self.destroy()
            return
        if self.cooldown > 0:
            self.cooldown -= 1
        elif len(self.actions) > 0:
            act = self.actions.pop(0)
            if act['TYPE'] is 'MOVE':
                self.cooldown += self.moveTo(tileMap.getTile(act['TARGET']).grid)
                for cell in tileMap.allTiles():
                    cell.grid.updatePhysics()
            elif act['TYPE'] is 'USE':
                self.cooldown += self.command(tileMap.getTile(act['TARGET']).grid)

    def castFov(self, tileMap):
        Wire.exploreRoom(tileMap, self.grid.cell.room)

        for obj in self.grid.object[0].connection:
            Wire.seeWire(tileMap, self.grid.cell.pos, obj.cell.pos)
        for obj1, obj2 in zip(self.route, self.route[1:]):
            Wire.seeWire(tileMap, obj1.cell.pos, obj2.cell.pos)
            Wire.createTraffic(tileMap, self, obj1.cell.pos, obj2.cell.pos)

    def checkRoute(self):
        if np.linalg.norm(self.route[0].cell.pos - self.actor.cell.pos) >= 2:
            return False
        else:
            return True

    def command(self, grid):
        if grid.object == []:
            return 0
        else:
            return grid.object[0].interact(self.actor, None, 'USE')
