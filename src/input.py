from src.globals import *

import numpy as np
import collections as coll

from src.actor.ai import AI
from src.render.render import Render

from bearlibterminal import terminal as term


class Input:
    MOVEMAP = {'UP': np.array([0, -1]),
               'DOWN': np.array([0, 1]),
               'LEFT': np.array([-1, 0]),
               'RIGHT': np.array([1, 0])}

    # [function, qualifier, help string]
    KEYMAP = coll.OrderedDict([
        (term.TK_ESCAPE, ('toggleQuit', None, "Quit game")),
        (term.TK_SPACE,  ('useItem', 0, "Use item slot")),
        ('TEXT_p', ('togglePause', None, "Pause Game")),
        ('TEXT_t', ('toggleDebug', None, "Enter debug console")),
        ('TEXT_m', ('cycleMap', None, "Cycle Map modes")),
        ('TEXT_h', ('cycleHelp', None, "Show help window")),
        (term.TK_UP,     ('moveMap', 'UP', "Move map")),
        (term.TK_DOWN,   ('moveMap', 'DOWN', "Move map")),
        (term.TK_LEFT,   ('moveMap', 'LEFT', "Move map")),
        (term.TK_RIGHT,  ('moveMap', 'RIGHT', "Move map")),
        (term.TK_W, ('movePlayer', 'UP', "Player Movement")),
        (term.TK_S, ('movePlayer', 'DOWN', "Player Movement")),
        (term.TK_A, ('movePlayer', 'LEFT', "Player Movement")),
        (term.TK_D, ('movePlayer', 'RIGHT', "Player Movement")),
        ('TEXT_r', ('restart', None, "Reload Level")),
        ('TEXT_1', ('dialogChoice', 1, "Answer Dialogue")),
        ('TEXT_2', ('dialogChoice', 2, "Answer Dialogue")),
        ('TEXT_3', ('dialogChoice', 3, "Answer Dialogue")),
        ('TEXT_0', ('dialogChoice', 0, "Answer Dialogue"))])

    def __init__(self, main):
        self.main = main
        self.quit = False
        self.debug = False
        self.pause = False
        self.help = 0

        term.set("input: filter=[keyboard,mouse];")

    def handleEvents(self):
        while term.has_input():
            event = term.read()
            if event in self.KEYMAP:
                self.handleKey(event)

            elif event is term.TK_MOUSE_MOVE:
                self.handleMouse(event)
            elif event is term.TK_MOUSE_LEFT:
                self.handleClick(event)
            print(event)


        # try:
        #     while True:
        #         event = tdl.event.get().next()
        #
        #         if event.type is 'KEYDOWN':
        #             self.handleKey(event)
        #         elif event.type is 'MOUSEUP':
        #             self.handleClick(event)
        #         elif event.type is 'MOUSEMOTION':
        #             self.handleMouse(event)
        #         elif event.type is 'MOUSEDOWN':
        #             self.handleScroll(event)
        # except:
        #     pass

    def handleKey(self, event):
        # idString = event.key
        # if event.key == 'TEXT':
        #     idString += '_' + event.text
        getattr(self, self.KEYMAP[event][0]).__call__(self.KEYMAP[event][1])

    def toggleQuit(self, qualifier=None):
        self.quit = not self.quit

    def toggleDebug(self, qualifier=None):
        self.quit = not self.quit

    def togglePause(self, qualifier=None):
        self.pause = not self.pause

    def restart(self, qualifier=None):
        self.main.initialize()
        self.main.run()

    def cycleHelp(self, qualifier=None):
        self.help = (self.help + 1) % 8

    def cycleMap(self, qualifier=None):
        self.main.render.mapLayer = (self.main.render.mapLayer + 1) % 3

    def playerAttack(self, qualifier=None):
        self.main.player.actions = [{'TYPE': 'ATTACK',
                                     'DIR': self.main.render.mapPanel.cursorDir,
                                     'TARGET': self.main.render.mapPanel.cursorPos}]

    def movePlayer(self, direction):
        self.main.player.actions = [{'TYPE': 'MOVE', 'DIR': Input.MOVEMAP[direction]}]
        self.main.render.mapPanel.cursorDir = Input.MOVEMAP[direction]

    def moveMap(self, direction):
        self.main.render.mapPanel.moveOffset(3 * Input.MOVEMAP[direction])

    def useItem(self, index):
        if index < len(self.main.player.inventory):
            self.main.player.actions = [{'TYPE': 'ITEM',
                                         'INDEX': index + self.main.render.mapPanel.inventoryOffset,
                                         'DIR': self.main.render.mapPanel.cursorDir,
                                         'TARGET': self.main.render.mapPanel.cursorPos}]

    def dialogChoice(self, index):
        self.main.player.actions = [{'TYPE': 'TALK',
                                     'INDEX': index,
                                     'DIR': self.main.render.mapPanel.cursorDir,
                                     'TARGET': self.main.player.ai.mind['TARGET']}]

    def handleMouse(self, event=None):
        mouse = self.getMouse()

        self.main.render.mapPanel.updateCursor(mouse)
        self.main.render.infoPanel.updateCursor(mouse)
        self.main.render.inventoryPanel.updateCursor(mouse)
        self.main.render.messagePanel.updateCursor(mouse)



    def handleClick(self, event):
        self.main.player.actions = []

#        if self.main.render.mapLayer == 0:
        if len(self.main.player.actions) < 2:
            self.main.player.actions = AI.findPath(self.main.map, self.main.player.cell.pos, self.main.render.mapPanel.cursorPos, True)
#            elif event.button is 'RIGHT' and len(self.main.player.actions) < 2:
#                self.main.player.actions = AI.findPath(self.main.map, self.main.player.cell.pos, self.main.render.mapPanel.cursorPos, True)
        # elif self.main.render.mapLayer == 1:
        #     self.main.player.actions = [{'TYPE': 'GRID',
        #                                  'DIR': self.main.render.mapPanel.cursorDir,
        #                                  'TARGET': self.main.render.mapPanel.cursorPos}]

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

    def getMouse(self):
        return np.array([term.state(term.TK_MOUSE_X), term.state(term.TK_MOUSE_Y)])
