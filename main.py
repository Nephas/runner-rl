#!/usr/bin/env python

from src.globals import *
from src.level.level import Level
from src.input import Input
from src.render.render import Render
from src.actor.actor import Player

import sys
import pygame as pg
import time as t
import random as rd

from bearlibterminal import terminal as term


class Game:
    LIMIT_FPS = 20
    TIC_SEC = 10
    TIC_SIZE = 1. / TIC_SEC
    FRAME_LENGTH = 1. / LIMIT_FPS

    def __init__(self):
        self.panel = {}
        self.actor = []
        self.agent = []

        self.map = Level(self)
        self.player = Player(None, self)
        self.render = Render(self)
        self.input = Input(self)

        self.lastTic = t.time()
        self.tic = 0

    def reset(self):
        self.panel = {}
        self.actor = []
        self.agent = []

        self.map = Level(self)
        self.player = Player(None, self)
        self.render = Render(self)
        self.input = Input(self)

        self.lastTic = t.time()
        self.tic = 0

    def initialize(self):
        self.actor = [self.player]
        self.panel = self.render.getGamePanels(self)

        self.map.load(random=True)

        self.panel['MAP'].moveOffset(self.player.cell.pos - (self.render.SEPARATOR // 4))
        self.panel['MAP'].updateCursor()
        self.panel['MAP'].layer = 'MAP'

        self.map.updatePhysics()
        self.run()

    def menu(self):
        self.input.debug = False
        self.input.quit = False

        self.panel = self.render.getMenuPanel(self)

        while True:
            if self.input.quit:
                term.close()
                sys.exit()
            if self.input.debug:
                break
            if t.time() >= self.FRAME_LENGTH + self.lastTic:
                self.render.renderMenu()
                self.input.handleEvents()

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
                    for agent in self.agent:
                        agent.act(self.map)
                    self.map.updatePhysics()
                    self.panel['MAP'].updateRender()

                    self.tic += 1
                    self.lastTic = t.time()
            if t.time() >= self.FRAME_LENGTH + self.lastTic:
                self.render.renderGame(self.map)
                self.input.handleEvents()


game = Game()
game.menu()
