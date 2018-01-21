from bearlibterminal import terminal as term

from src.globals import *

import numpy as np


class Rectangle(object):  # a rectangle on the map. used to characterize a room or a window
    def __init__(self, pos, w, h):
        self.pos = np.array(pos)
        self.size = np.array([w, h])
        self.x = [pos[X], pos[X] + w]
        self.y = [pos[Y], pos[Y] + h]
        self.center = (self.pos + self.size / 2).round().astype('int')
        self.area = w * h

    def intersects(self, other):  # returns true if this rectangle intersects with another one
        return not (self.x[MAX] <= other.x[MIN] or other.x[MAX] <= self.x[MIN] or self.y[MAX] <= other.y[MIN] or
                    other.y[MAX] <= self.y[MIN])

    def contains(self, pos):
        return pos[X] in range(*self.x) and pos[Y] in range(*self.y)

    def border(self):
        positions = []
        for x in range(self.x[MIN], self.x[MAX]):
            positions.append([x, self.y[MIN]])
            positions.append([x, self.y[MAX] - 1])
        for y in range(self.y[MIN], self.y[MAX]):
            positions.append([self.x[MIN], y])
            positions.append([self.x[MAX] - 1, y])
        return positions

    def getPositions(self):
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                yield [x, y]

    def getCells(self, map):
        for x in range(max(0, self.x[MIN]), min(self.x[MAX], map.WIDTH)):
            for y in range(max(0, self.y[MIN]), min(self.y[MAX], map.HEIGHT)):
                yield map.tile[x][y]


class Button(Rectangle):
    def __init__(self, pos, w, h, text='Button', function=None):
        w = max(len(text), w)
        Rectangle.__init__(self, pos, w, h)

        self.key = ' '
        self.link = None
        self.cursor = False
        self.text = text
        self.handleClick = function

    def printString(self, string, color=COLOR['WHITE']):
        term.color(term.color_from_argb(255, *color))
        term.printf(self.pos[X], self.pos[Y], string)

    def render(self):
        if self.cursor:
            color = COLOR['GRAY']
        else:
            color = COLOR['DARKGRAY']

        string = '  ' + self.text

        term.layer(19)
        self.printString(len(string) * '#', color)
        self.printString('#')

        term.layer(20)
        self.printString(string)
        self.printString(self.key, COLOR['BLACK'])

    def updateCursor(self, pos):
        self.cursor = self.contains(pos)

    def handleClick(self):
        pass


class Panel(Rectangle):
    def __init__(self, main, pos, w, h, layer=0):
        Rectangle.__init__(self, pos, w, h)

        self.main = main
        self.layer = layer
        self.cursor = False
        self.button = []

    def describe(self):
        return self.__class__.__name__

    def updateCursor(self, pos):
        self.cursor = self.contains(pos)
        if self.cursor:
            self.main.input.activePanel = self
            for button in self.button:
                button.updateCursor(pos)
                if button.cursor:
                    self.main.input.activeButton = button

    def handleScroll(self, offset=0):
        pass

    def handleClick(self, event=0):
        for button in self.button:
            if button.cursor:
                button.handleClick()

    def bracket(self):
        positions = []
        for x in range(self.x[MIN] - 2, self.x[MIN] + self.size[X] * 2 // 3, 2):
            positions.append([x, self.y[MIN] - 1])
        for y in range(self.y[MIN] - 1, self.y[MIN] + self.size[Y] * 2 // 3):
            positions.append([self.x[MIN] - 2, y])
        return positions

    def clear(self, color=COLOR['BLACK']):
        term.layer(0)
        term.bkcolor(term.color_from_argb(255, *color))
        term.clear_area(self.pos[X], self.pos[Y], *self.size)

    def printString(self, pos, string, color=COLOR['WHITE']):
        term.color(term.color_from_argb(255, *color))
        pos += self.pos
        term.printf(pos[X], pos[Y], string)

    def printChar(self, pos, char, color=COLOR['WHITE']):
        term.color(term.color_from_argb(255, *color))
        pos += self.pos
        term.put(pos[X], pos[Y], char)

    def render(self):
        self.clear()
        term.layer(10)

        if self.cursor:
            term.color(term.color_from_argb(255, 64, 64, 64))
            term.color
            for pos in self.bracket():
                term.put(pos[X], pos[Y], 0x10FA)

        self.printString(np.array([2, -1]),
                         "=== {:} ===".format(self.describe()))

        for button in self.button:
            button.render()
