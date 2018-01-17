from src.globals import *

from src.render.panel.panel import Panel

import numpy as np
import itertools as it


class InfoPanel(Panel):
    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

    def render(self):
        super(InfoPanel, self).render()

        row = 1

        self.printString(np.array([1, row]), 'Tics:  ')

        actions = ''
        for i in range(1 + (self.main.tic % self.main.TIC_SEC)):
            actions += '>'
        actions += ' '
        for i in range(self.main.player.cooldown):
            actions += '-'
        self.printString(np.array([7, row]), actions)

        row = 2

        # lighting bar
        self.printString(np.array([1, row]), 'Light: ')

#        for i in range(6):
#            self.printChar(np.array([7 + 2 * i, row]), 0x10FF)
        for i in range(int(float(self.main.player.cell.light) / MAX_LIGHT * 6)):
            self.printChar(np.array([7 + 2 * i, row]), 0x1007)

        mapPanel = self.main.panel['MAP']

        row = 3

        if self.main.map.contains(mapPanel.cursorPos):
            cursorTile = self.main.map.getTile(mapPanel.cursorPos)
            if cursorTile.room is not None:
                self.printString(np.array([1, row]),
                                 cursorTile.room.describe())

                row = 4

            if mapPanel.layer is 'MAP' and cursorTile.vision[LOS]:
                for i, obj in enumerate(cursorTile.object + cursorTile.effect):
                    self.printChar(np.array([1, row + i]), obj.char)
                    self.printString(
                        np.array([4, row + i]), obj.describe())
            elif mapPanel.layer is 'GRID' and cursorTile.grid.vision[EXP]:
                for i, obj in enumerate(cursorTile.grid.object + cursorTile.grid.agent):
                    self.printChar(np.array([1, row + i]), obj.char)
                    self.printString(
                        np.array([4, row + i]), obj.describe())
