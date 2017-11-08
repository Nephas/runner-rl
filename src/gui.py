from globals import *
import numpy as np

from render import Render
from map import Map, Rectangle


class Gui:
    def __init__(self, main):
        self.main = main
        self.mapOffset = np.array([0, 0])
        self.cursorPos = np.array([64, 64])
        self.cursorDir = np.array([1, 1])
        self.mapRange = [[0, Map.WIDTH], [0, Map.HEIGHT]]
        self.mapRectangle = Rectangle(self.mapOffset, 0, 0)

        self.messages = ['The hum from the vents reminds you of a TV tuned to a dead channel.']

    def updateCursor(self, terminalPos=np.array([8, 8])):
        if not Render.inMap(terminalPos):
            return

        mapPos = np.array(terminalPos) + self.mapOffset - \
            self.main.render.MAPINSET
        if self.main.map.contains(mapPos):
            self.cursorPos = mapPos

        ray = mapPos - self.main.player.cell.pos
        length = np.linalg.norm(ray)
        if length > 0:
            self.cursorDir = (ray / length).round().astype('int')

    def moveOffset(self, dir=np.array([0, 0])):
        self.mapOffset += dir
        (panelX, panelY) = self.main.render.mapPanel.get_size()
        self.mapRectangle = Rectangle(self.mapOffset, panelX, panelY)

    def getCells(self, map):
        return self.mapRectangle.getCells(map)

    def pushMessage(self, string):
        self.messages.insert(0, string)

    def renderInfo(self, panel):
        panel.clear(bg=COLOR['BLACK'])

        # action point counter
        actions = ''
        for i in range(1 + (self.main.tic % self.main.TIC_SEC)):
            actions += '>'
        actions += ' '
        for i in range(self.main.player.cooldown):
            actions += '-'
        panel.draw_str(1, 1, actions)

        # lighting bar
        for i in range(6):
            panel.draw_char(1 + i, 5, 7)
        for i in range(int(float(self.main.player.cell.light) / MAX_LIGHT * 6)):
            panel.draw_char(1 + i, 5, 15)

#        panel.draw_str(1, 7, '{:5}'.format(t.time()))

        cursorTile = self.main.map.getTile(self.cursorPos)
        for i, obj in enumerate(cursorTile.object):
            panel.draw_str(1, 7 + 2 * i, obj.describe(), obj.fg)

        for i, item in enumerate(self.main.player.inventory):
            panel.draw_str(1, 20 + 2 * i, item.describe(), item.fg)

    def renderMessage(self, panel):
        panel.clear(bg=COLOR['BLACK'])
        pos = 0

        for string in self.messages:
            # line wrapping in list comprehension
            block = [string[i:i + panel.width - 2] for i in range(0, len(string), panel.width - 2)]
            for line in block:
                pos += 1
                if pos >= panel.height - 1:
                    break
                panel.draw_str(1, pos, line, COLOR['WHITE'])

            pos += 1
            if pos >= panel.height - 1:
                break
