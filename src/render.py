from src.globals import *
from PIL import Image
import numpy as np
import copy as cp
import tdl
import tcod
import time as t

class Render:  # a rectangle on the map. used to characterize a room.
    GRAPHICSPATH = './graphics/'
    TILESET = 'experimental_12x16.png'

    SCREEN = np.array([100, 40])  # [WIDTH, HEIGHT]
    SEPARATOR = (5. / 8. * SCREEN).astype('int')
    MAPINSET = np.array([1, 1])

    def __init__(self, main):
        self.main = main

        tdl.set_font(Render.GRAPHICSPATH + Render.TILESET, greyscale=True)

        self.console = tdl.init(*self.SCREEN, title="RunnerRL", fullscreen=False)
        self.console.clear(bg=[25, 25, 25])

        self.mapPanel = tdl.Window(
            self.console, self.MAPINSET[X], self.MAPINSET[Y], *(self.SEPARATOR - np.array([2,2])) )
        self.infoPanel = tdl.Window(
            self.console, self.SEPARATOR[X], self.SEPARATOR[Y], *(self.SCREEN - self.SEPARATOR - np.array([1,1])) )
        self.inventoryPanel = tdl.Window(
            self.console, self.SEPARATOR[X], 1, self.SCREEN[X] - self.SEPARATOR[X] - 1, self.SEPARATOR[Y] - 2)
        self.messagePanel = tdl.Window(
            self.console, self.MAPINSET[X], self.SEPARATOR[Y], self.SEPARATOR[X] - 2, self.SCREEN[Y] - self.SEPARATOR[Y] - 1)
        self.helpPanel = tdl.Window(
            self.console, self.MAPINSET[X], self.MAPINSET[Y], self.SEPARATOR[X] - 2, self.SCREEN[Y] - 2)

        self.mapLayer = 0

    def renderStart(self):
        self.helpPanel.clear(bg=COLOR['BLACK'])
        self.infoPanel.clear(bg=COLOR['BLACK'])
        self.inventoryPanel.clear(bg=COLOR['BLACK'])
        self.messagePanel.clear(bg=COLOR['BLACK'])

        self.helpPanel.draw_str(1, 1, "===== Generating Level =====")

        tdl.flush()

    def renderAll(self, map, gui):
        self.console.clear(bg=[25, 25, 25])

        gui.renderInfo(self.infoPanel)
        gui.renderInventory(self.inventoryPanel)

        if self.main.input.help != 0:
            gui.renderHelp(self.helpPanel, self.main.input.help)

            self.console.blit(self.helpPanel, *self.MAPINSET)
        else:
            gui.renderMessage(self.messagePanel)
            self.renderMap(self.mapPanel, map, gui)

            self.console.blit(self.mapPanel, *self.MAPINSET)

        tdl.flush()

    def renderMap(self, panel, map, gui):
        panel.clear(bg=COLOR['BLACK'])

        if self.mapLayer == 0:
            for cell in gui.getCells(map):
                cell.drawMap(panel, cell.pos - gui.mapOffset)
        elif self.mapLayer == 1:
            for cell in gui.getCells(map):
                cell.drawNet(panel, cell.pos - gui.mapOffset)

        try:
            cell = map.getTile(self.main.player.cell.pos + gui.cursorDir)
            cursorPos = cell.pos - gui.mapOffset
            cell.drawHighlight(panel, cursorPos)

            cell = map.getTile(gui.cursorPos)
            cursorPos = cell.pos - gui.mapOffset
            cell.drawHighlight(panel, cursorPos)
        except:
            pass

    @staticmethod
    def inMap(terminalPos):
        if terminalPos[X] < Render.MAPINSET[X] or terminalPos[Y] < Render.MAPINSET[Y]:
            return False
        elif terminalPos[X] >= Render.SEPARATOR[X] - 1 or terminalPos[Y] >= Render.SEPARATOR[Y] - 1:
            return False
        else:
            return True

    @staticmethod
    def rayCast(start, end):
        delta = end - start
        direction = delta / np.linalg.norm(delta)
        line = []

        ray = 0.1 * direction
        while np.linalg.norm(ray) <= np.linalg.norm(delta):
            if len(line) == 0 or np.linalg.norm(line[-1] - ray.round().astype('int')) != 0:
                line.append(ray.round().astype('int'))
            ray += 0.1 * direction
        return np.array(line)

    @staticmethod
    def rayMap(r, num):
        lines = []
        start = np.array([0., 0.])
        phi0 = 2 * np.pi * np.random.random()
        for phi in np.linspace(phi0, phi0 + 2. * np.pi, num):
            end = r * np.array([np.cos(phi), np.sin(phi)])
            lines.append(Render.rayCast(start, end)[1:int(r)])
        return lines

    @staticmethod
    def coneMap(r, num, angle):
        lines = []
        start = np.array([0., 0.])
        phi0 = 2 * np.pi * np.random.random()
        for phi in np.linspace(phi0, phi0 + angle, num):
            end = r * np.array([np.cos(phi), np.sin(phi)])
            lines.append(Render.rayCast(start, end)[1:int(r)])
        return lines

    @staticmethod
    def printImage(map, fileName):
        # create a new black image
        img = Image.new('RGB', [3 * map.WIDTH, 3 * map.HEIGHT], "black")
        pixels = img.load()  # create the pixel map
        for x in range(map.WIDTH):    # for every pixel:
            for y in range(map.HEIGHT):
                tile = [[i, j] for i in range(3 * x, 3 * x + 3)
                        for j in range(3 * y, 3 * y + 3)]

                if map.tile[x][y].wall is False:
                    # set the colour accordingly
                    for p in tile:
                        pixels[p[X], p[Y]] = tuple(
                            TIERCOLOR[map.tile[x][y].tier])
                elif map.tile[x][y].wall is True:
                    for p in tile:
                        # set the colour accordingly
                        pixels[p[X], p[Y]] = COLOR['DARKGRAY']
                elif map.tile[x][y].wall is None:
                    for p in tile:
                        # set the colour accordingly
                        pixels[p[X], p[Y]] = COLOR['BLACK']

                if map.tile[x][y].grid is False:
                    # set the colour accordingly
                    pixels[3 * x + 1, 3 * y + 1] = COLOR['GREEN']
                elif map.tile[x][y].grid is True:
                    for p in tile:
                        # set the colour accordingly
                        pixels[p[X], p[Y]] = COLOR['MEDIUMGREEN']

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
