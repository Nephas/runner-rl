#!/usr/bin/env python

from src.globals import *
from src.map import Map
from src.input import Input
from src.gui import Gui
from src.render import Render
from src.object import Player

import sys
import time as t
import tdl


class Game:
    def __init__(self):
        self.render = Render(self)
        self.input = Input(self)
        self.gui = Gui(self)
        self.map = Map(self)
        self.player = None

        self.lastTic = t.time()
        self.tic = 0

        self.initialize()

    def initialize(self):
        stats = [0, 0, 0]
        # while not (stats[0] >= 30 and stats[1] >= 12 and stats[2] >= 6 and stats[3] <= 1):
        self.player = Player(None, self)
        stats = self.map.generateLevel()
        self.render.printImage(self.map, "levelgen.bmp")
        print(stats)

        self.gui.mapOffset = self.player.cell.pos - (SEPARATOR / 2)
        self.map.updatePhysics()
        self.map.updateRender()

    def run(self):
        if t.time() >= TIC_SIZE + self.lastTic:
            self.map.updatePhysics()

            self.tic += 1
            self.lastTic = t.time()
            if self.input.actions > 0:
                self.input.actions -= 1
        self.render.renderAll(self.map, self.gui)
        self.input.handleEvents()

game = Game()
while True:
    t.sleep(0.001)
    if tdl.event.isWindowClosed() or game.input.quit:
        sys.exit()
    else:
        game.run()
