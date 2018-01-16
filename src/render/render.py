from src.globals import *

import numpy as np
import copy as cp
import time as t

from bearlibterminal import terminal as term

from src.render.panel import MapPanel, InfoPanel, InventoryPanel, MessagePanel, MenuPanel, ExitPanel


class Render:  # a rectangle on the map. used to characterize a room.
    GRAPHICSPATH = './graphics/'
    TILES = 'exp_24x24.png'
    FONT = 'font_12x24.png'
    LOADSCREEN = 'load_1364x768.png'
    TITLE = 'title.png'
    LOGO = 'graphics/logo.txt'

    SCREEN = np.array([110, 25])  # [WIDTH, HEIGHT]
    SEPARATOR = (3. / 4. * SCREEN).astype('int')
    MAPINSET = np.array([2, 1])

    def __init__(self, main):
        self.main = main

        term.open()

        term.set("window: size={:}x{:}".format(
            Render.SCREEN[WIDTH], Render.SCREEN[HEIGHT]))
        term.set("font: " + Render.GRAPHICSPATH +
                 Render.FONT + ", size=12x24, codepage=437")
        term.set("0x1000: " + Render.GRAPHICSPATH + Render.TILES +
                 ", size=24x24, spacing=2x1, align=center")
#        term.set("0x2000: " + Render.GRAPHICSPATH + Render.LOADSCREEN +
#                 ", size=1364x768, align=top-left")
        term.set("0x3000: " + Render.GRAPHICSPATH + Render.TITLE +
                 ", size=800x285, align=center")

        term.composition(True)
        term.refresh()

    def getMenuPanel(self, main):
        return {'MENU': MenuPanel(main, self.MAPINSET, *self.SCREEN - 2*self.MAPINSET)}

    def getGamePanels(self, main):
        return {'MAP': MapPanel(main, self.MAPINSET, *(self.SEPARATOR - np.array([4, 2]))),
                'INFO': InfoPanel(main, self.SEPARATOR, *(self.SCREEN - self.SEPARATOR - np.array([2, 1]))),
                'INVENTORY': InventoryPanel(main, [self.SEPARATOR[X], 1], self.SCREEN[X] - self.SEPARATOR[X] - 2, self.SEPARATOR[Y] - 2),
                'MESSAGE': MessagePanel(main, [self.MAPINSET[X], self.SEPARATOR[Y]], self.SEPARATOR[X] - 4, self.SCREEN[Y] - self.SEPARATOR[Y] - 1)}

    def getExitPanel(self, main):
        return {'EXIT': ExitPanel(main, [self.MAPINSET[X], self.SEPARATOR[Y]], self.SEPARATOR[X] - 4, self.SCREEN[Y] - self.SEPARATOR[Y] - 1)}

    def renderMenu(self):
        term.bkcolor(term.color_from_argb(255, 25, 25, 25))
        term.clear()

        self.main.panel['MENU'].render()
        term.refresh()

    def renderGame(self, map):
        term.bkcolor(term.color_from_argb(255, 25, 25, 25))
        term.clear()

        for panel in self.main.panel:
            self.main.panel[panel].render()
        term.refresh()

    @staticmethod
    def inMap(terminalPos):
        if terminalPos[X] < Render.MAPINSET[X] or terminalPos[Y] < Render.MAPINSET[Y]:
            return False
        elif terminalPos[X] >= Render.SEPARATOR[X] - 1 or terminalPos[Y] >= Render.SEPARATOR[Y] - 1:
            return False
        else:
            return True
