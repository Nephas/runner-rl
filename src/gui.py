from globals import *
from render import Render
import numpy as np


class Gui:
    def __init__(self, main):
        self.main = main
        self.mapOffset = np.array([0, 0])
        self.cursorPos = np.array([64, 64])
        self.cursorDir = np.array([1, 1])
        self.mapRange = [[0, MAP[WIDTH]], [0, MAP[HEIGHT]]]
        self.mapCells = []

        self.messages = ['test1', 'test2']

    def updateCursor(self, terminalPos=np.array([8,8])):
        if not Render.inMap(terminalPos):
            return

        mapPos = np.array(terminalPos) + self.mapOffset - self.main.render.MAPINSET
        if self.main.map.contains(mapPos):
            self.cursorPos = mapPos

        ray = mapPos - self.main.player.cell.pos
        length = np.linalg.norm(ray)
        if length > 0:
            self.cursorDir = (ray / length).round().astype('int')

    def moveOffset(self, dir=np.array([0, 0])):
        self.mapOffset += dir
        (panelX, panelY) = self.main.render.mapPanel.get_size()
        self.mapRange[X] = [max(0, self.mapOffset[X]), min(
            self.mapOffset[X] + panelX, MAP[WIDTH])]
        self.mapRange[Y] = [max(0, self.mapOffset[Y]), min(
            self.mapOffset[Y] + panelY, MAP[HEIGHT])]

        self.mapCells = []
        for i in range(*self.mapRange[X]):
            for j in range(*self.mapRange[Y]):
                self.mapCells.append(self.main.map.tile[i][j])

    def pushMessage(self, string):
        self.messages.insert(0, string)

    def renderInfo(self, panel):
        panel.clear(bg=BLACK)
        for i in range(1 + (self.main.tic % TIC_SEC)):
            panel.draw_str(1 + i, 1, "o")
        for i in range(self.main.player.cooldown):
            panel.draw_str(1 + i, 3, "o")

        panel.draw_str(1, 5, '{:5}'.format(t.time()))

        cursorTile = self.main.map.getTile(self.cursorPos)
        for i, obj in enumerate(cursorTile.object):
            panel.draw_str(1, 7 + 2 * i, obj.describe(), obj.fg)

        for i, item in enumerate(self.main.player.inventory):
            panel.draw_str(1, 20 + 2 * i, item.describe(), item.fg)

    def renderMessage(self, panel):
        panel.clear(bg=BLACK)
        for i, line in enumerate(self.messages):
            pos = 1 + 2*i
            if pos >= panel.height:
                break
            panel.draw_str(1, pos, line)
