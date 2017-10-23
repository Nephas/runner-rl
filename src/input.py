from globals import *
import numpy as np
import tdl


class Input:

    MOVEMAP = { 'w': np.array([0, -1]),
                'a': np.array([-1, 0]),
                's': np.array([0, 1]),
                'd': np.array([1, 0]),
                'q': np.array([-1, -1]),
                'e': np.array([1, -1]),
                'y': np.array([-1, 1]),
                'c': np.array([1, 1])}

    def __init__(self, parent):
        self.parent = parent
        self.quit = False
        self.actions = 0

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
            self.parent.gui.mapOffset[Y] -= 3
        elif key == 'DOWN':
            self.parent.gui.mapOffset[Y] += 3
        elif key == 'LEFT':
            self.parent.gui.mapOffset[X] -= 3
        elif key == 'RIGHT':
            self.parent.gui.mapOffset[X] += 3

        elif key == 'CHAR' and self.actions == 0:
            dir = Input.MOVEMAP[char]
            self.playerMovement(dir)

    def playerMovement(self, dir):
        cost = np.abs(dir[X]) + np.abs(dir[Y]) + 1

        if self.parent.player.moveDir(dir):
            self.actions += cost
            self.parent.gui.mapOffset = self.parent.gui.mapOffset + dir
        else:
            self.playerInteraction(dir)

    def playerInteraction(self, dir):
        pos = self.parent.player.cell.pos + dir
        for obj in self.parent.map.tile[pos[X]][pos[Y]].object:
            self.actions += obj.interact(self.parent.player, dir)


    def handleMouse(self, terminalPos):
        mapPos = np.array(terminalPos) + self.parent.gui.mapOffset - self.parent.render.MAPINSET
        self.parent.gui.cursorPos = mapPos
        print(self.parent.map.getTile(mapPos).object)

    def handleClick(self, event):
        mapPos = np.array(event.cell) + self.parent.gui.mapOffset - self.parent.render.MAPINSET
        self.parent.gui.cursorPos = mapPos

        ray = mapPos - self.parent.player.cell.pos
        dir = (ray/np.linalg.norm(ray)).round().astype('int')

        if event.button is 'LEFT':
            self.playerMovement(dir)

        if event.button is 'RIGHT':
            self.playerInteraction(dir)
