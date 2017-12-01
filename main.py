#!/usr/bin/env python

from src.globals import *
from src.level.level import Level
from src.input import Input
from src.gui import Gui
from src.render import Render
from src.actor.actor import Player

import sys
import pygame as pg
import time as t
import random as rd
import tdl
from bearlibterminal import terminal as term

class Game:
    LIMIT_FPS = 20
    TIC_SEC = 10
    TIC_SIZE = 1. / TIC_SEC
    FRAME_LENGTH = 1. / LIMIT_FPS

    def __init__(self):
        self.render = Render(self)
        self.input = Input(self)
        self.gui = Gui(self)
        self.map = Level(self)
        self.sound = {}

        self.actor = []
        self.player = Player(None, self)

        self.lastTic = t.time()
        self.tic = 0

    def initialize(self):
        self.actor = [self.player]

#        tdl.setFPS(self.LIMIT_FPS)
        pg.init()
        # self.sound = {'SHOT': pg.mixer.Sound('sounds/shot.wav'),
        #               'EXPLOSION': pg.mixer.Sound('sounds/explosion.wav'),
        #               'DOOR': pg.mixer.Sound('sounds/door.wav'),
        #               'PUNCH': pg.mixer.Sound('sounds/punch.wav'),
        #               'STEP': pg.mixer.Sound('sounds/step.wav')}

        self.map.load(debug=True)

        self.gui.moveOffset(self.player.cell.pos - (self.render.SEPARATOR / 2))
        self.gui.updateCursor()
        self.map.updatePhysics()
        self.map.updateRender()

    def run(self):
        self.input.debug = False
        self.input.quit = False

        while True:
            if self.input.quit:
                term.close()
                sys.exit()
            if self.input.debug:
                break
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
