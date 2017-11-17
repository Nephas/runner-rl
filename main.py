#!/usr/bin/env python

from src.globals import *
from src.level.level import Level
from src.input import Input
from src.gui import Gui
from src.render import Render

import sys
import time as t
import tdl

class Game:
    LIMIT_FPS = 20
    TIC_SEC = 10
    TIC_SIZE = 1. / TIC_SEC
    FRAME_LENGTH = 1. / LIMIT_FPS

    def __init__(self):
        self.player = None
        self.render = Render(self)
        self.input = Input(self)
        self.gui = Gui(self)
        self.map = Level(self)

        self.actor = []

        self.lastTic = t.time()
        self.tic = 0

    def initialize(self):
        tdl.setFPS(self.LIMIT_FPS)
        self.render.renderStart()

        self.map.generate('Evil-Corp7')

        self.gui.moveOffset(self.player.cell.pos - (self.render.SEPARATOR / 2))
        self.gui.updateCursor()
        self.map.updatePhysics()
        self.map.updateRender()

    def run(self):
        self.input.debug = False
        self.input.quit = False

        while True:
            if self.input.debug:
                break
            if tdl.event.isWindowClosed() or self.input.quit:
                sys.exit()
            if (self.input.pause and self.player.actions != []) or not self.input.pause:
                if t.time() >= self.TIC_SIZE + self.lastTic:
                    for actor in self.actor:
                        actor.act(self.map)
                    self.map.updatePhysics()
                    self.map.updateRender()

                    self.tic += 1
                    self.lastTic = t.time()
            if t.time() >= self.FRAME_LENGTH + self.lastTic:
                self.render.renderAll(self.map, self.gui)
                self.input.handleEvents()


game = Game()
game.initialize()
game.run()
