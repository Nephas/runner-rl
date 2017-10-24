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

    def __init__(self, main):
        self.main = main
        self.quit = False

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
            self.main.gui.mapOffset[Y] -= 3
        elif key == 'DOWN':
            self.main.gui.mapOffset[Y] += 3
        elif key == 'LEFT':
            self.main.gui.mapOffset[X] -= 3
        elif key == 'RIGHT':
            self.main.gui.mapOffset[X] += 3

        elif key == 'CHAR' and self.main.player.cooldown == 0:
            dir = Input.MOVEMAP[char]
            self.playerMovement(dir)

    def playerMovement(self, dir):
        cost = np.abs(dir[X]) + np.abs(dir[Y]) + 1

        if self.main.player.moveDir(dir):
            self.main.player.cooldown += cost
            self.main.gui.mapOffset = self.main.gui.mapOffset + dir
        else:
            self.playerInteraction(dir)

    def playerInteraction(self, dir):
        pos = self.main.player.cell.pos + dir
        for obj in self.main.map.tile[pos[X]][pos[Y]].object:
            self.main.player.cooldown += obj.interact(self.main.player, dir)


    def handleMouse(self, terminalPos):
        mapPos = np.array(terminalPos) + self.main.gui.mapOffset - self.main.render.MAPINSET
        self.main.gui.cursorPos = mapPos
        print(self.main.map.getTile(mapPos).object)

    def handleClick(self, event):
        mapPos = np.array(event.cell) + self.main.gui.mapOffset - self.main.render.MAPINSET
        self.main.gui.cursorPos = mapPos

        ray = mapPos - self.main.player.cell.pos
        dir = (ray/np.linalg.norm(ray)).round().astype('int')

        if event.button is 'LEFT':
            self.playerMovement(dir)

        if event.button is 'RIGHT':
            self.playerInteraction(dir)
