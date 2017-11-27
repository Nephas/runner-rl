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
    LOGO = 'graphics/logo.txt'

    SCREEN = np.array([100, 40])  # [WIDTH, HEIGHT]
    SEPARATOR = (5. / 8. * SCREEN).astype('int')
    MAPINSET = np.array([1, 1])

    def __init__(self, main):
        self.main = main

        tdl.set_font(Render.GRAPHICSPATH + Render.TILESET, greyscale=True)

        self.console = tdl.init(
            *self.SCREEN, title="RunnerRL", fullscreen=False)
        self.console.clear(bg=[25, 25, 25])

        self.mapPanel = tdl.Window(
            self.console, self.MAPINSET[X], self.MAPINSET[Y], *(self.SEPARATOR - np.array([2, 2])))
        self.infoPanel = tdl.Window(
            self.console, self.SEPARATOR[X], self.SEPARATOR[Y], *(self.SCREEN - self.SEPARATOR - np.array([1, 1])))
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
        elif self.mapLayer == 2:
            for cell in gui.getCells(map):
                cell.drawDist(panel, cell.pos - gui.mapOffset,
                              self.main.player.ai.distmap)

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
        nPoints = np.max(np.abs(end - start)) + 1

        xLine = np.linspace(start[X], end[X], nPoints)
        yLine = np.linspace(start[Y], end[Y], nPoints)
        line = [[x, y] for x, y in zip(xLine, yLine)]
        return np.array(line).round().astype('int')

    @staticmethod
    def rayMap(r):
        lines = []
        start = np.array([0, 0])
        for end in Render.circleCast(r):
            lines.append(Render.rayCast(start, end)[1:r])
        return lines

    @staticmethod
    def circleCast(r):
        circle = []

        for phi in np.linspace(0, 2. * np.pi, int(r) * 30):
            end = (r * np.array([np.cos(phi), np.sin(phi)])).astype('int')
            if len(circle) == 0 or not all(circle[-1] == end):
                circle.append(end)
        return np.array(circle)

    @staticmethod
    def rayBresenham(start, end):
        line = []
        delta = end - start
        if delta[X] == 0:
            return np.array([[0, y] for y in range(start[Y], end[Y], np.sign(delta[Y]))] + [end])

        deltaerr = abs(delta[Y] / float(delta[X]))
        error = 0.0

        y = start[Y]
        for x in range(start[X], end[X]):
            line.append([x, y])
            error = error + deltaerr
            while error >= 0.5:
                y = y + np.sign(delta[Y])
                error = error - 1.0
        return np.array(line + [end])

    @staticmethod
    def midpointCircle(center, radius):
        (x0, y0) = center
        (x, y) = (0, radius)

        f = 1 - radius
        ddf_x = 1
        ddf_y = -2 * radius

        circle = [[x0, y0 + radius], [x0, y0 - radius],
                  [x0 + radius, y0], [x0 - radius, y0]]

        while x < y:
            if f >= 0:
                y -= 1
                ddf_y += 2
                f += ddf_y
            x += 1
            ddf_x += 2
            f += ddf_x
            circle += [[x0 + x, y0 + y],
                       [x0 - x, y0 + y],
                       [x0 + x, y0 - y],
                       [x0 - x, y0 - y],
                       [x0 + y, y0 + x],
                       [x0 - y, y0 + x],
                       [x0 + y, y0 - x],
                       [x0 - y, y0 - x]]
        return np.array(circle)

    @staticmethod
    def coneMap(r, dir, width=np.pi * 0.5):
        arc = []
        cone = []
        start = np.array([0, 0])

        for phi in np.linspace(dir - width / 2, dir + width / 2, int(r) * 20):
            end = (r * np.array([np.cos(phi), np.sin(phi)])).astype('int')
            if len(cone) == 0 or not all(cone[-1] == end):
                arc.append(end)

        for end in arc:
            cone.append(Render.rayCast(start, end)[1:r])
        return np.array(cone)

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
                            map.PALETTE[map.tile[x][y].room.tier])
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
                    pixels[3 * x + 1, 3 * y + 1] = tuple(map.COMPLEMENT[0])
                elif map.tile[x][y].grid is True:
                    for p in tile:
                        # set the colour accordingly
                        pixels[p[X], p[Y]] = tuple(
                            (0.5 * map.COMPLEMENT[0]).astype('int'))

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


class Light():
    LIGHTMAP = [Render.rayMap(brightness) for brightness in range(0, 20)]

    def __init__(self):
        pass

    @staticmethod
    def cast(map, pos, brightness=1):
        cell = map.getTile(pos)
        cell.light = max(brightness, cell.light)
        for baseLine in Light.LIGHTMAP[brightness]:
            try:
                line = baseLine + pos
                strength = brightness
                for point in line:
                    cell = map.getTile(point)
                    cell.light = max(strength, cell.light)

                    if cell.block[LIGHT]:
                        strength -= 4
                    if cell.block[LOS] or strength < 0:
                        break
                    else:
                        strength -= 1
            except IndexError:
                pass
