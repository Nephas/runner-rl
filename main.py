#!/usr/bin/env python

from src.globals import *
from src.map import Map
from src.input import Input
from src.gui import Gui
from src.render import Render
from src.actor import Player

import sys
import time as t
import tdl


class Game:
    def __init__(self):
        self.player = None
        self.actor = []
        self.render = Render(self)
        self.input = Input(self)
        self.gui = Gui(self)
        self.map = Map(self)

        self.lastTic = t.time()
        self.tic = 0

    def initialize(self):
        self.render.renderStart()

        stats = {'DEADENDS' : -1, 'VENTS' : - 1}
#        while stats['DEADENDS'] != 0 or stats['VENTS'] < 16:
        self.map = Map(self)
        stats = self.map.generateLevel()
        print(stats)

        self.player = Player(None, self)
        self.map.finalize(self.player)
        self.render.printImage(self.map, "levelgen.bmp")

        self.gui.mapOffset = self.player.cell.pos - (SEPARATOR / 2)
        self.map.updatePhysics()
        self.map.updateRender()

    def run(self):
        while True:
            t.sleep(0.0001)
            if tdl.event.isWindowClosed() or game.input.quit:
                sys.exit()
            if t.time() >= TIC_SIZE + self.lastTic:
                self.map.updatePhysics()
                for actor in self.actor:
                    actor.act(self.map)
                self.tic += 1
                self.lastTic = t.time()
            if t.time() >= FRAME_LENGTH + self.lastTic:
                self.render.renderAll(self.map, self.gui)
                self.input.handleEvents()

game = Game()
game.initialize()

game.run()
