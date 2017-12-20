from src.globals import *

import numpy as np
import collections as coll

from src.actor.ai import AI

from bearlibterminal import terminal as term


class Input:
    MOVEMAP = {'UP': np.array([0, -1]),
               'DOWN': np.array([0, 1]),
               'LEFT': np.array([-1, 0]),
               'RIGHT': np.array([1, 0])}

    # [function, qualifier, help string]
    KEYMAP = coll.OrderedDict([
        (term.TK_ESCAPE, ('toggleQuit', None, "Quit game")),
        (term.TK_SPACE,  ('hotkey', 'R', "Use item slot")),
        (term.TK_CONTROL,  ('hotkey', 'L', "Use item slot")),
#        (term.TK_TAB, ('toggleSlow', None, "Pause Game")),
        (term.TK_P, ('togglePause', None, "Pause Game")),
        (term.TK_T, ('toggleDebug', None, "Enter debug console")),
        (term.TK_TAB, ('cycleMap', None, "Cycle Map modes")),
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
        (term.TK_1, ('hotkey', '1', "Answer Dialogue")),
        (term.TK_2, ('hotkey', '2', "Answer Dialogue")),
        (term.TK_3, ('hotkey', '3', "Answer Dialogue")),
        (term.TK_4, ('hotkey', '4', "Answer Dialogue"))])

    def __init__(self, main):
        self.main = main
        self.quit = False
        self.debug = False
        self.pause = False
        self.slow = False
        self.help = 0
        self.activePanel = None
        self.activeButton = None

        term.set("input: filter=[keyboard,mouse];")

    def handleEvents(self):
        while term.has_input():
            event = term.read()
            if event in self.KEYMAP:
                self.handleKey(event)
            elif event is term.TK_MOUSE_MOVE:
                self.handleMouse(event)
            elif event in [term.TK_MOUSE_LEFT, term.TK_MOUSE_RIGHT]:
                self.handleClick(event)
            elif event in [term.TK_MOUSE_SCROLL]:
                self.handleScroll(event)

    def handleKey(self, event):
        getattr(self, self.KEYMAP[event][0]).__call__(self.KEYMAP[event][1])

    def hotkey(self, qualifier):
        if self.activePanel is self.main.panel['MAP']:
            if qualifier in ['L','R']:
                index = self.main.player.inventory.index(self.main.panel['INVENTORY'].hand[qualifier])
            else:
                index = self.main.player.inventory.index(self.main.panel['INVENTORY'].belt[qualifier])
#                self.main.player.cooldown += 3
            self.useItem(index)

        if self.activePanel is self.main.panel['INVENTORY']:
            for button in filter(lambda b: b.key is qualifier, self.main.panel['INVENTORY'].button):
                button.key = ''
            if qualifier in ['L','R']:
                self.main.panel['INVENTORY'].hand[qualifier] = self.activeButton.link
            else:
                self.main.panel['INVENTORY'].belt[qualifier] = self.activeButton.link
        self.main.panel['INVENTORY'].updateRender()

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
        self.main.panel['MAP'].cycleLayer()

    def playerAttack(self, qualifier=None):
        self.main.player.actions = [{'TYPE': 'ATTACK',
                                     'DIR': self.main.panel['MAP'].cursorDir,
                                     'TARGET': self.main.panel['MAP'].cursorPos}]

    def movePlayer(self, direction):
        self.main.player.actions = [
            {'TYPE': 'MOVE', 'DIR': Input.MOVEMAP[direction]}]
        self.main.panel['MAP'].cursorDir = Input.MOVEMAP[direction]

    def moveMap(self, direction):
        self.main.panel['MAP'].moveOffset(3 * Input.MOVEMAP[direction])

    def useItem(self, index):
        if index < len(self.main.player.inventory):
            self.main.player.actions = [{'TYPE': 'ITEM',
                                         'INDEX': index,
                                         'DIR': self.main.panel['MAP'].cursorDir,
                                         'TARGET': self.main.panel['MAP'].cursorPos}]

    def dialogChoice(self, index):
        self.main.player.actions = [{'TYPE': 'TALK',
                                     'INDEX': index,
                                     'DIR': self.main.panel['MAP'].cursorDir,
                                     'TARGET': self.main.player.ai.mind['TARGET']}]

    def handleMouse(self, event=None):
        mouse = self.getMouse()
        for panel in self.main.panel:
            self.main.panel[panel].updateCursor(mouse)

    def handleClick(self, event):
        button = {term.TK_MOUSE_LEFT: 'LEFT',
                  term.TK_MOUSE_RIGHT: 'RIGHT'}

        for panel in self.main.panel:
            if self.main.panel[panel].cursor:
                self.main.panel[panel].handleClick(button[event])

    def handleScroll(self, event):
        for panel in self.main.panel:
            if self.main.panel[panel].cursor:
                self.main.panel[panel].handleScroll(term.state(term.TK_MOUSE_WHEEL))

    def getMouse(self):
        return np.array([term.state(term.TK_MOUSE_X), term.state(term.TK_MOUSE_Y)])
