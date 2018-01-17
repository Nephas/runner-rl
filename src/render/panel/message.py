from src.globals import *

from src.render.panel.panel import Panel

import numpy as np
import itertools as it


class MessagePanel(Panel):
    MESSAGES = [
        ('The hum from the vents reminds you of a TV tuned to a dead channel.', COLOR['GREEN'])]

    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

        self.messageOffset = 0

    @staticmethod
    def pushMessage(string, color=COLOR['WHITE']):
        if not self.MESSAGES[0][0] == string:
            self.MESSAGES.insert(0, (string, color))

    def render(self):
        super(MessagePanel, self).render()

        pos = 0

        for string, color in self.MESSAGES[self.messageOffset:]:
            # line wrapping in list comprehension
            block = [string[i:i + self.size[X] - 2]
                     for i in range(0, len(string), self.size[X] - 2)]
            for line in block:
                pos += 1
                if pos >= self.size[Y] - 1:
                    break
                self.printString(np.array([1, pos]), line)

    def handleScroll(self, offset):
        self.messageOffset += offset
        self.messageOffset = max(0, self.messageOffset)
