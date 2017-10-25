from src.globals import *
from PIL import Image
import numpy as np
import copy as cp
import tdl
import tcod
import time as t


class Render:  # a rectangle on the map. used to characterize a room.
    GRAPHICSPATH = './graphics/'
    TILESET = 'extended16x16.png'

    MAPINSET = np.array([1,1])

    def __init__(self, main):
        self.main = main

        tdl.set_font(Render.GRAPHICSPATH + Render.TILESET,
                     greyscale=True)
        tdl.setFPS(LIMIT_FPS)

        self.console = tdl.init(
            SCREEN[WIDTH], SCREEN[HEIGHT], title="RunnerRL", fullscreen=False)
        self.console.clear(bg=[50, 50, 50])

        self.back = tdl.Window(self.console, 0, 0, None, None)
        self.back.clear(bg=[50, 50, 50])

        self.mapPanel = tdl.Window(
            self.console, Render.MAPINSET[X], Render.MAPINSET[Y], SEPARATOR[WIDTH] - 2, SEPARATOR[HEIGHT] - 2)
        self.infoPanel = tdl.Window(
            self.console, SEPARATOR[WIDTH], 1, SCREEN[WIDTH] - SEPARATOR[WIDTH] - 1, SCREEN[HEIGHT] - 2)

        self.raymap = Render.rayMap(16,32)
        self.lightmap = Render.rayMap(6,16)

    def renderStart(self):
        self.mapPanel.clear(bg=BLACK)
        self.infoPanel.clear(bg=BLACK)

        self.mapPanel.draw_str(2,2, "Generating Level")

        self.console.blit(self.mapPanel, 1, 1)
        self.console.blit(self.infoPanel, SEPARATOR[WIDTH], 1)

        tdl.flush()

    def renderAll(self, map, gui):
        self.renderMap(map, gui.mapOffset)
        self.renderInfo()

        self.console.blit(self.mapPanel, 1, 1)
        self.console.blit(self.infoPanel, SEPARATOR[WIDTH], 1)

        tdl.flush()

    def renderMap(self, map, mapOffset):
        self.mapPanel.clear(bg=BLACK)
        (panelX, panelY) = self.mapPanel.get_size()

        mapX = [max(0, mapOffset[X]), min(mapOffset[X] + panelX, MAP[WIDTH])]
        mapY = [max(0, mapOffset[Y]), min(mapOffset[Y] + panelY, MAP[HEIGHT])]
        map.updateRender(mapX, mapY)

        cursorTile = map.getTile(self.main.gui.cursorPos)
        if cursorTile.vision[LOS]:
            cursorTile.bg = WHITE

        for x in range(mapX[MIN], mapX[MAX]):
            for y in range(mapY[MIN], mapY[MAX]):
                map.tile[x][y].draw(
                    self.mapPanel, np.array([x, y]) - mapOffset)

    def renderInfo(self):
        self.infoPanel.clear(bg = BLACK)
        for i in range(1 + (self.main.tic % TIC_SEC)):
            self.infoPanel.draw_str(1 + i, 1, "o")
        for i in range(self.main.player.cooldown):
            self.infoPanel.draw_str(1 + i, 3, "o")

        self.infoPanel.draw_str(1, 5, '{:5}'.format(t.time()))

        cursorTile = self.main.map.getTile(self.main.gui.cursorPos)
        for i, obj in enumerate(cursorTile.object):
            self.infoPanel.draw_str(1, 7 + 2*i, obj.describe())
        # for i in range(255):
        #     self.infoPanel.draw_str(2 + 6 * int(i / 32), i % 32, str(i))
        #     self.infoPanel.draw_char(6 + 6 * int(i / 32), i % 32, i)

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
        for phi in np.linspace(0., 2. * np.pi, num):
            end = r * np.array([np.cos(phi), np.sin(phi)])
            lines.append(Render.rayCast(start, end)[1:int(r)])
        return lines

    @staticmethod
    def printImage(map, fileName):
        img = Image.new('RGB', MAP, "black")  # create a new black image
        pixels = img.load()  # create the pixel map
        for x in range(MAP[WIDTH]):    # for every pixel:
            for y in range(MAP[HEIGHT]):
                if map.tile[x][y].wall is False:
                    # set the colour accordingly
                    pixels[x, y] = (40 * map.tile[x][y].tier,
                                    255 - 40 * map.tile[x][y].tier, 255)
                elif map.tile[x][y].wall is True:
                    pixels[x, y] = (25, 25, 25)  # set the colour accordingly
                elif map.tile[x][y].wall is None:
                    pixels[x, y] = (0, 0, 0)  # set the colour accordingly

                if map.tile[x][y].tier == -2:
                    pixels[x, y] = (55, 55, 55)  # set the colour accordingly

        for room in map.tier[-1]:
            if room.function is not None:
                for pos in room.rectangle.border():
                    if map.getTile(pos).wall:
                        if room.function is "start":
                            pixels[pos[X], pos[Y]] = (50, 250, 50)
                        elif room.function is "extraction":
                            pixels[pos[X], pos[Y]] = (250, 50, 50)
        img.save(fileName)
