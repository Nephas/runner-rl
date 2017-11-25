from src.globals import *

import numpy as np
import collections as coll
import tdl

from src.actor.ai import AI
from src.render import Render


class Input:
    MOVEMAP = {'UP': np.array([0, -1]),
               'DOWN': np.array([0, 1]),
               'LEFT': np.array([-1, 0]),
               'RIGHT': np.array([1, 0])}

    # [function, qualifier, help string]
    KEYMAP = coll.OrderedDict([
        ('ESCAPE', ('toggleQuit', None, "Quit game")),
        ('SPACE',  ('playerAttack', None, "Attack Cursor Position")),
        ('TEXT_p', ('togglePause', None, "Pause Game")),
        ('TEXT_t', ('toggleDebug', None, "Enter debug console")),
        ('TEXT_m', ('cycleMap', None, "Cycle Map modes")),
        ('TEXT_h', ('cycleHelp', None, "Show help window")),
        ('UP',     ('moveMap', 'UP', "Move map")),
        ('DOWN',   ('moveMap', 'DOWN', "Move map")),
        ('LEFT',   ('moveMap', 'LEFT', "Move map")),
        ('RIGHT',  ('moveMap', 'RIGHT', "Move map")),
        ('TEXT_w', ('movePlayer', 'UP', "Player Movement")),
        ('TEXT_s', ('movePlayer', 'DOWN', "Player Movement")),
        ('TEXT_a', ('movePlayer', 'LEFT', "Player Movement")),
        ('TEXT_d', ('movePlayer', 'RIGHT', "Player Movement")),
        ('TEXT_1', ('useItem', 1, "Use item slot")),
        ('TEXT_2', ('useItem', 2, "Use item slot")),
        ('TEXT_3', ('useItem', 3, "Use item slot")),
        ('TEXT_4', ('useItem', 4, "Use item slot")),
        ('TEXT_5', ('useItem', 5, "Use item slot"))])

    def __init__(self, main):
        self.main = main
        self.quit = False
        self.debug = False
        self.pause = False
        self.help = 0

    def handleEvents(self):
        try:
            while True:
                event = tdl.event.get().next()

                if event.type is 'KEYDOWN':
                    self.handleKey(event)
                elif event.type is 'MOUSEUP':
                    self.handleClick(event)
                elif event.type is 'MOUSEMOTION':
                    self.handleMouse(event)
                elif event.type is 'MOUSEDOWN':
                    self.handleScroll(event)
        except:
            pass

    def handleKey(self, event):
        idString = event.key
        if event.key == 'TEXT':
            idString += '_' + event.text

        getattr(self, self.KEYMAP[idString][0]).__call__(self.KEYMAP[idString][1])

    def toggleQuit(self, qualifier=None):
        self.quit = not self.quit

    def toggleDebug(self, qualifier=None):
        self.quit = not self.quit

    def togglePause(self, qualifier=None):
        self.pause = not self.pause

    def cycleHelp(self, qualifier=None):
        self.help = (self.help + 1) % 8

    def cycleMap(self, qualifier=None):
        self.main.render.mapLayer = (self.main.render.mapLayer + 1) % 3

    def playerAttack(self, qualifier=None):
        self.main.player.actions = [{'TYPE': 'ATTACK',
                                     'DIR': self.main.gui.cursorDir,
                                     'TARGET': self.main.gui.cursorPos}]

    def movePlayer(self, direction):
        self.main.player.actions = [{'TYPE': 'MOVE', 'DIR': Input.MOVEMAP[direction]}]
        self.main.gui.cursorDir = Input.MOVEMAP[direction]

    def moveMap(self, direction):
        self.main.gui.moveOffset(3 * Input.MOVEMAP[direction])

    def useItem(self, index):
        if index < len(self.main.player.inventory):
            self.main.player.actions = [{'TYPE': 'ITEM',
                                         'INDEX': index,
                                         'DIR': self.main.gui.cursorDir,
                                         'TARGET': self.main.gui.cursorPos}]


    def handleMouse(self, event):
        self.main.gui.updateCursor(event.cell)

    def handleClick(self, event):
        self.main.player.actions = []

        if event.button is 'LEFT' and len(self.main.player.actions) < 2:
            self.main.player.actions = AI.findPath(self.main.map, self.main.player.cell.pos, self.main.gui.cursorPos, False)
        elif event.button is 'RIGHT' and len(self.main.player.actions) < 2:
            self.main.player.actions = AI.findPath(self.main.map, self.main.player.cell.pos, self.main.gui.cursorPos, True)

    def handleScroll(self, event):
        if event.button is 'SCROLLUP':
            if event.cell[X] <= Render.SEPARATOR[X]:
                self.main.gui.messageOffset += 1
            else:
                self.main.gui.inventoryOffset += 1
        elif event.button is 'SCROLLDOWN':
            if event.cell[X] <= Render.SEPARATOR[X]:
                self.main.gui.messageOffset -= 1
            else:
                self.main.gui.inventoryOffset -= 1

        self.main.gui.messageOffset = max(0, self.main.gui.messageOffset)
        self.main.gui.inventoryOffset = max(0, self.main.gui.inventoryOffset)
