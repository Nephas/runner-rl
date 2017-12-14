from src.globals import *

from PIL import Image
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

    @staticmethod
    def printImage(map, fileName):
        # create a new black image
        img = Image.new('RGB', [3 * map.WIDTH, 3 * map.HEIGHT], "black")
        pixels = img.load()  # create the pixel map
        for x in range(map.WIDTH):    # for every pixel:
            for y in range(map.HEIGHT):
                tile = [[i, j] for i in range(3 * x, 3 * x + 3)
                        for j in range(3 * y, 3 * y + 3)]

                if map.tile[x][y].wall is False and map.tile[x][y].room is not None:
                    # set the colour accordingly
                    for p in tile:
                        pixels[p[X], p[Y]] = tuple(
                            map.palette[map.tile[x][y].room.tier])
                elif map.tile[x][y].wall is True:
                    for p in tile:
                        # set the colour accordingly
                        pixels[p[X], p[Y]] = COLOR['DARKGRAY']
                elif map.tile[x][y].wall is None:
                    for p in tile:
                        # set the colour accordingly
                        pixels[p[X], p[Y]] = COLOR['BLACK']

                if map.tile[x][y].grid.wire:
                    # set the colour accordingly
                    pixels[3 * x + 1, 3 * y +
                           1] = tuple(map.corp.complement[0])
                elif map.tile[x][y].grid.object != []:
                    for p in tile:
                        # set the colour accordingly
                        pixels[p[X], p[Y]] = tuple(
                            (0.5 * map.corp.complement[0]).astype('int'))

        for room in map.tier[-1]:
            if room.function is not None:
                for pos in room.border():
                    if map.getTile(pos).wall:
                        if room.function is "start":
                            for i in range(3):
                                pixels[3 * pos[X] + i, 3 *
                                       pos[Y] + i] = COLOR['RED']
                        elif room.function is "extraction":
                            for i in range(3):
                                pixels[3 * pos[X] + i, 3 *
                                       pos[Y] + i] = COLOR['BLUE']

        for lamp in map.getAll('Lamp'):
            pixels[3 * lamp.cell.pos[X] + 1, 3 *
                   lamp.cell.pos[Y] + 1] = COLOR['WHITE']

        img.save(fileName)
