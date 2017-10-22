from globals import *
import numpy as np
import tdl


class Input:
    def __init__(self, parent):
        self.parent = parent
        self.quit = False
        self.active = True
        self.actions = 0

    def handleEvents(self):
        event = None
        try:
            event = tdl.event.get().next()
            while True:
                tdl.event.get().next()
        except:
            if event is None:
                return

        if event.type is 'KEYDOWN':
            self.handleKey(event.key, event.char)
        elif event.type is 'MOUSEUP':
            self.handleMouse(event.cell)

    def handleKey(self, key, char):
        if key == 'ESCAPE':
            self.quit = True
        elif key == 'UP':
            self.parent.gui.mapOffset[Y] -= 3
        elif key == 'DOWN':
            self.parent.gui.mapOffset[Y] += 3
        elif key == 'LEFT':
            self.parent.gui.mapOffset[X] -= 3
        elif key == 'RIGHT':
            self.parent.gui.mapOffset[X] += 3

        elif key == 'CHAR' and self.actions == 0:
            dir = [0, 0]
            cost = 0
            if char == 'w':
                dir = [0, -1]
                cost = 2
            elif char == 'a':
                dir = [-1, 0]
                cost = 2
            elif char == 's':
                dir = [0, 1]
                cost = 2
            elif char == 'd':
                dir = [1, 0]
                cost = 2
            elif char == 'q':
                dir = [-1, -1]
                cost = 3
            elif char == 'e':
                dir = [1, -1]
                cost = 3
            elif char == 'y':
                dir = [-1, 1]
                cost = 3
            elif char == 'c':
                dir = [1, 1]
                cost = 3

            dir = np.array(dir)

            if self.parent.player.moveDir(dir):
                self.actions += cost
                self.parent.gui.mapOffset = self.parent.gui.mapOffset + dir
            else:
                pos = self.parent.player.cell.pos + dir
                for obj in self.parent.map.tile[pos[X]][pos[Y]].object:
                    self.actions += obj.interact(dir)

    def handleMouse(self, cell):
        print(cell)
