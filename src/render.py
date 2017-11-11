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

        tdl.set_font(Render.GRAPHICSPATH + Render.TILESET,
                     greyscale=True)

        self.console = tdl.init(
            self.SCREEN[X], self.SCREEN[Y], title="RunnerRL", fullscreen=False)
        self.console.clear(bg=[25, 25, 25])

        self.back = tdl.Window(self.console, 0, 0, None, None)
        self.back.clear(bg=[25, 25, 25])

        self.mapPanel = tdl.Window(
            self.console, self.MAPINSET[X], self.MAPINSET[Y], self.SEPARATOR[X] - 2, self.SEPARATOR[Y] - 2)
        self.infoPanel = tdl.Window(
            self.console, self.SEPARATOR[X], 1, self.SCREEN[X] - self.SEPARATOR[X] - 1, self.SCREEN[Y] - 2)
        self.messagePanel = tdl.Window(
            self.console, self.MAPINSET[X], self.SEPARATOR[Y], self.SEPARATOR[X] - 2, self.SCREEN[Y] - self.SEPARATOR[Y] - 1)

        self.mapLayer = 0

        self.raymap = Render.rayMap(24, 96)
        self.lightmap = Render.rayMap(8, 32)

    def renderStart(self):
        self.mapPanel.clear(bg=COLOR['BLACK'])
        self.infoPanel.clear(bg=COLOR['BLACK'])
        self.messagePanel.clear(bg=COLOR['BLACK'])

        self.mapPanel.draw_str(2, 2, "Generating Level")

        self.console.blit(self.mapPanel, 1, 1)
        self.console.blit(self.infoPanel, self.SEPARATOR[X], 1)

        tdl.flush()

    def renderAll(self, map, gui):
        self.renderMap(map, gui.mapOffset)
        gui.renderInfo(self.infoPanel)
        gui.renderMessage(self.messagePanel)

        self.console.blit(self.mapPanel, 1, 1)
        self.console.blit(self.infoPanel, self.SEPARATOR[WIDTH], 1)
        tdl.flush()

    def renderMap(self, map, mapOffset):
        self.mapPanel.clear(bg=COLOR['BLACK'])

        if self.mapLayer == 0:
            for cell in self.main.gui.getCells(map):
                cell.drawMap(self.mapPanel, cell.pos - mapOffset)
        elif self.mapLayer == 1:
            for cell in self.main.gui.getCells(map):
                cell.drawNet(self.mapPanel, cell.pos - mapOffset)

        try:
            cell = map.getTile(self.main.player.cell.pos + self.main.gui.cursorDir)
            cursorPos = cell.pos - mapOffset
            cell.drawHighlight(self.mapPanel, cursorPos)

            cell = map.getTile(self.main.gui.cursorPos)
            cursorPos = cell.pos - mapOffset
            cell.drawHighlight(self.mapPanel, cursorPos)
        except AssertionError:
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

        ray = 0.25 * direction
        while np.linalg.norm(ray) <= np.linalg.norm(delta):
            if len(line) == 0 or np.linalg.norm(line[-1] - ray.round().astype('int')) != 0:
                line.append(ray.round().astype('int'))
            ray += 0.25 * direction
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
