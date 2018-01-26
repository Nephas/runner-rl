from src.globals import *

from bearlibterminal import terminal as term

from src.render.panel.panel import Panel, Rectangle
from src.actor.ai import AI

import numpy as np
import itertools as it


class MapPanel(Panel):
    SCALE = np.array([2, 1])
    LAYER = it.cycle(['MAP', 'GRID'])

    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)
        self.map = main.map

        self.layer = self.LAYER.next()

        self.mapOffset = np.array([0, 0])
        self.cursorPos = np.array([64, 64])
        self.cursorDir = np.array([1, 1])
        self.camera = Rectangle(self.mapOffset, 0, 0)

    def handleClick(self, button='LEFT'):
        self.main.player.actions = []

        if self.layer is 'MAP':
            if button is 'LEFT' and len(self.main.player.actions) < 2:
                self.main.player.actions = AI.findPath(
                    self.map, self.main.player.cell.pos, self.cursorPos, False)
            elif button is 'RIGHT' and len(self.main.player.actions) < 2:
                self.main.player.actions = AI.findPath(
                    self.map, self.main.player.cell.pos, self.cursorPos, True)

        elif self.layer is 'GRID':
            if button is 'LEFT' and len(self.main.player.actions) < 2:
                self.main.player.agent.actions = [{'TYPE': 'MOVE',
                                                   'TARGET': self.cursorPos}]
            elif button is 'RIGHT' and len(self.main.player.actions) < 2:
                self.main.player.agent.actions = [{'TYPE': 'USE',
                                                   'TARGET': self.cursorPos}]

    def handleScroll(self, off):
        if term.check(term.TK_SHIFT):
            offset = np.array([off, 0])
        else:
            offset = np.array([0, off])
        self.moveOffset(offset)

    def cycleLayer(self):
        nextLayer = self.LAYER.next()
        if nextLayer is self.layer:
            nextLayer = self.LAYER.next()
        self.layer = nextLayer
        self.updateRender()

    def updateRender(self):
        if self.layer is 'MAP':
            for cell in self.camera.getCells(self.map):
                cell.updateRender()
        elif self.layer is 'GRID':
            for cell in self.camera.getCells(self.map):
                cell.grid.updateRender()

    def render(self):
        super(MapPanel, self).render()

        if self.layer is 'MAP':
            self.renderMap()
        elif self.layer is 'GRID':
            self.renderGrid()

    def renderMap(self):
        for cell in self.camera.getCells(self.map):
            self.drawCell(cell, self.SCALE *
                      (cell.pos - self.mapOffset) + self.pos)

        for mapPos in [self.main.player.cell.pos + self.cursorDir, self.cursorPos]:
            try:
                cell = self.map.getTile(mapPos)
                panelPos = self.SCALE * (cell.pos - self.mapOffset) + self.pos
                self.highlight(panelPos)
            except:
                pass

        for actor in self.main.player.ai.mind['AWARE']:
            try:
                panelPos = self.SCALE * (actor.cell.pos - self.mapOffset) + self.pos
                self.highlight(panelPos, actor.ai.color)
            except:
                pass

    def renderGrid(self):
        player = self.main.player
        connected = []
        route = []
        if player.agent is not None:
            connected = [
                obj.cell.pos for obj in player.agent.grid.object[0].connection]
            route = player.agent.route

        self.drawCell(player.cell, self.SCALE *
                  (player.cell.pos - self.mapOffset) + self.pos)

        for cell in self.camera.getCells(self.map):
            self.drawCell(cell.grid, self.SCALE *
                      (cell.pos - self.mapOffset) + self.pos)

        for mapPos in [self.cursorPos] + connected:
            try:
                cell = self.map.getTile(mapPos)
                panelPos = self.SCALE * (cell.pos - self.mapOffset) + self.pos
                self.highlight(panelPos, self.map.complement[2])
            except:
                pass

        for grid in route:
            panelPos = self.SCALE * (grid.cell.pos - self.mapOffset) + self.pos
            self.highlight(panelPos)

    def drawCell(self, cell, panelPos):
        i = 0
        for color, tile in zip(cell.color, cell.stack):
            term.layer(i)
            term.color(term.color_from_argb(255, *color))
            if type(tile) is int:
                term.put(panelPos[X], panelPos[Y], tile)
            elif type(tile) is str:
                term.printf(panelPos[X], panelPos[Y], tile)
            i += 1

    def highlight(self, panelPos, color=COLOR['WHITE']):
        if not self.contains(panelPos):
            return
        term.layer(3)
        term.color(term.color_from_argb(255, *color))
        term.put(panelPos[X], panelPos[Y], 0x1020)

    def updateCursor(self, terminalPos=np.array([8, 8])):
        super(MapPanel, self).updateCursor(terminalPos)

        mapPos = (terminalPos - self.pos) // self.SCALE + self.mapOffset

        if self.main.map.contains(mapPos):
            self.cursorPos = mapPos

        ray = mapPos - self.main.player.cell.pos
        length = np.linalg.norm(ray)
        if length > 0:
            self.cursorDir = (ray / length).round().astype('int')

    def moveOffset(self, dir=np.array([0, 0])):
        self.mapOffset += dir
        self.cursorPos += dir
        (panelX, panelY) = self.size
        self.camera = Rectangle(self.mapOffset, panelX // 2, panelY)
        self.updateRender()
