from src.globals import *

from src.render.panel.panel import Panel, Button

import numpy as np
import itertools as it


class ExitPanel(Panel):
    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

        self.message = 'Exit'
        self.button = [Button(self.pos + np.array([2, 3]),
                              5, 1, "Main Menu", self.reset)]

    def render(self):
        super(ExitPanel, self).render()

        self.printString(np.array([2, 2]), self.message)

    def reset(self):
        self.main.reset()
        self.main.menu()
