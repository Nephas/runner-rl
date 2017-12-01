from globals import *
import numpy as np

from src.render import Render
from src.input import Input
from src.level.map import Map, Rectangle


class Gui:
    MESSAGES = [('The hum from the vents reminds you of a TV tuned to a dead channel.', COLOR['GREEN'])]

    def __init__(self, main):
        self.main = main
        self.mapOffset = np.array([0, 0])
        self.messageOffset = 0
        self.inventoryOffset = 0
        self.cursorPos = np.array([64, 64])
        self.cursorDir = np.array([1, 1])
        self.mapRectangle = Rectangle(self.mapOffset, 0, 0)

    @staticmethod
    def pushMessage(string, color=COLOR['WHITE']):
        if not Gui.MESSAGES[0][0] == string:
            Gui.MESSAGES.insert(0, (string, color))

    def updateCursor(self, terminalPos=np.array([8, 8])):
        if not Render.inMap(terminalPos):
            return

        mapPos = np.array(terminalPos) + self.mapOffset - \
            Render.MAPINSET
        if self.main.map.contains(mapPos):
            self.cursorPos = mapPos

        ray = mapPos - self.main.player.cell.pos
        length = np.linalg.norm(ray)
        if length > 0:
            self.cursorDir = (ray / length).round().astype('int')

    def moveOffset(self, dir=np.array([0, 0])):
        self.mapOffset += dir
        self.cursorPos += dir
        (panelX, panelY) = self.main.render.mapPanel.size
        self.mapRectangle = Rectangle(self.mapOffset, panelX, panelY)

    def getCells(self, map):
        return self.mapRectangle.getCells(map)

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
            panel.draw_char(1 + i, 3, 7, self.main.player.cell.bg)
        for i in range(int(float(self.main.player.cell.light) / MAX_LIGHT * 6)):
            panel.draw_char(1 + i, 3, 15)

        if self.main.map.contains(self.cursorPos):
            cursorTile = self.main.map.getTile(self.cursorPos)
            if cursorTile.vision[LOS] is True:
                if cursorTile.room is not None:
                    panel.draw_str(1, 5, cursorTile.room.describe())
                for i, obj in enumerate(cursorTile.object + cursorTile.effect):
                    panel.draw_str(1, 7 + 2 * i, obj.describe(), obj.fg)

    def renderInventory(self, panel):
        panel.clear(bg=COLOR['BLACK'])

        for i, item in enumerate(self.main.player.inventory[self.inventoryOffset:]):
            pos = 1 + 2 * i
            if pos >= panel.height - 1:
                break

            if i == 0:
                panel.draw_str(1, pos, 'SPACE: ' + item.describe(), item.fg, COLOR['DARKGRAY'])
            elif i <= 4:
                panel.draw_str(1, pos, '    {:}: '.format(i) + item.describe(), item.fg)
            else:
                panel.draw_str(1, pos, '       ' + item.describe(), item.fg)


    def renderMessage(self, panel):
        panel.clear(bg=COLOR['BLACK'])
        pos = 0

        for string, color in Gui.MESSAGES[self.messageOffset:]:
            # line wrapping in list comprehension
            block = [string[i:i + panel.width - 2]
                     for i in range(0, len(string), panel.width - 2)]
            for line in block:
                pos += 1
                if pos >= panel.height - 1:
                    break
                panel.draw_str(1, pos, line, color)

            pos += 1
            if pos >= panel.height - 1:
                break

    def renderHelp(self, panel, page=0):
        panel.clear(bg=COLOR['BLACK'])
        pos = [1, 3]
        panel.draw_str(1, 1, "===== Help page {:} =====".format(page))

        if page == 1:
            for key in Input.KEYMAP:
                panel.draw_str(pos[X], pos[Y], "{: >5}: ".format(key.split('_')[-1]) + Input.KEYMAP[key][2])

                pos[Y] += 2
                if pos[Y] >= panel.height - 1:
                    pos = [panel.width // 2, 3]

        elif page >= 2:
            for i in range((page - 2) * 100, (page - 1) * 100):
                if i > 255:
                    break
                try:
                    panel.draw_str(pos[X], pos[Y], "{:03}:".format(i))
                    panel.draw_char(pos[X] + 5, pos[Y], i)
                except:
                    pass

                pos[Y] += 2
                if pos[Y] >= panel.height - 1:
                    pos[X] += 8
                    pos[Y] = 3
