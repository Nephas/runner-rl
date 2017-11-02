from globals import *
import numpy as np
import tdl


class Input:

    MOVEMAP = {'w': np.array([0, -1]),
               'a': np.array([-1, 0]),
               's': np.array([0, 1]),
               'd': np.array([1, 0]),
               'q': np.array([-1, -1]),
               'e': np.array([1, -1]),
               'y': np.array([-1, 1]),
               'c': np.array([1, 1])}

    def __init__(self, main):
        self.main = main
        self.quit = False
        self.actions = []

    def handleEvents(self):
        try:
            while True:
                event = tdl.event.get().next()

                if event.type is 'KEYDOWN':
                    self.handleKey(event.key, event.char)
                elif event.type is 'MOUSEUP':
                    self.handleClick(event)
                elif event.type is 'MOUSEMOTION':
                    self.handleMouse(event.cell)
        except:
            pass

    def handleKey(self, key, char):
        if key == 'ESCAPE':
            self.quit = True
        elif key == 'UP':
            self.main.gui.moveOffset(np.array([0, -3]))
        elif key == 'DOWN':
            self.main.gui.moveOffset(np.array([0, 3]))
        elif key == 'LEFT':
            self.main.gui.moveOffset(np.array([-3, 0]))
        elif key == 'RIGHT':
            self.main.gui.moveOffset(np.array([3, 0]))

        elif key == 'CHAR' and len(self.actions) < 2:
            self.actions.append({'TYPE': 'MOVE', 'DIR': Input.MOVEMAP[char]})

        elif key == 'SPACE' and len(self.actions) < 2:
            ray = self.main.gui.cursorPos - self.main.player.cell.pos
            dir = (ray / np.linalg.norm(ray)).round().astype('int')
            self.actions.append({'TYPE': 'USE', 'DIR': dir})

    #
    # def playerMovement(self, dir):
    #     cost = np.abs(dir[X]) + np.abs(dir[Y])
    #
    #     if self.main.player.moveDir(dir):
    #         self.main.player.cooldown += cost
    #         self.main.gui.mapOffset = self.main.gui.mapOffset + dir
    #     else:
    #         self.playerInteraction(dir)
    #
    # def playerInteraction(self, dir):
    #     pos = self.main.player.cell.pos + dir
    #     for obj in self.main.map.tile[pos[X]][pos[Y]].object:
    #         self.main.player.cooldown += obj.interact(self.main.player, dir)

    def handleMouse(self, terminalPos):
        self.main.gui.updateCursor(terminalPos)

    def handleClick(self, event):
        if event.button is 'LEFT' and len(self.actions) < 2:
            self.actions.append({'TYPE': 'MOVE', 'DIR': self.main.gui.cursorDir})
        elif event.button is 'RIGHT' and len(self.actions) < 2:
            self.actions.append({'TYPE': 'USE', 'DIR': self.main.gui.cursorDir})
