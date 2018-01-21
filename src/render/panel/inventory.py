from src.globals import *

from src.render.panel.panel import Panel, Button

import numpy as np
import itertools as it
import collections as coll


class InventoryPanel(Panel):
    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

        self.player = main.player
        self.hand = coll.OrderedDict([('L', None), ('R', None)])
        self.belt = coll.OrderedDict([('1', None), ('2', None), ('3', None), ('4', None)])

        self.inventoryOffset = 0
        self.inventoryLength = 0

        self.updateRender()

    def updateRender(self):
        self.button = []
        self.player.inventory = sorted(self.player.inventory, key=lambda i: i.describe())

        for i, key in enumerate(self.hand):
            if not self.hand[key] in self.player.inventory:
                self.hand[key] = None

            item = self.hand[key]
            if item is not None:
                button = Button(self.pos + np.array([2, 1 + 2*i]), 5, 1, item.describe(), item.drop)
                button.link = item
                button.key = key
                self.button.append(button)

        for i, key in enumerate(self.belt):
            if not self.belt[key] in self.player.inventory:
                self.belt[key] = None

            item = self.belt[key]
            if item is not None:
                button = Button(self.pos + np.array([2, 6 + i]), 5, 1, item.describe(), item.drop)
                button.link = item
                button.key = key
                self.button.append(button)

        for i, item in enumerate(self.player.inventory[self.inventoryOffset:]):
            button = Button(self.pos + np.array([self.size[X] // 2, 1 + i]), 5, 1, item.describe(), item.drop)
            button.link = item
            button.key = '$'
            self.button.append(button)

    def render(self):
        super(InventoryPanel, self).render()

        for i, key in enumerate(self.hand):
            item = self.hand[key]
            if item is not None:
                self.printChar(np.array([2, 2 + 2*i]), item.icon)

    def handleClick(self, event=0):
        super(InventoryPanel, self).handleClick(event)
        self.updateRender()

    def handleScroll(self, offset):
        self.inventoryOffset += offset
        self.inventoryOffset = max(0, self.inventoryOffset)
        self.updateRender()
