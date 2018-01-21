from src.globals import *

from bearlibterminal import terminal as term

from src.render.panel.panel import Panel, Button

import numpy as np
import itertools as it


class MenuPanel(Panel):
    ANIMATION = it.cycle([0x3000, 0x3001, 0x3002, 0x3003,
                          0x3004, 0x3005, 0x3006, 0x3007, 0x3008, 0x3009])

    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

        self.picture = self.ANIMATION.next()
        self.frame = 0
        self.button = [Button(self.pos + np.array([2, 2]), 5, 1, "Start", self.generate),
                       Button(self.pos + np.array([2, 4]), 5, 1, "Quit", self.quit)]

    def render(self):
        self.frame += 1
        if self.frame % 5 == 0:
            self.animate()
        term.layer(1)
        term.color(term.color_from_argb(255, *COLOR['WHITE']))
        term.put(self.center[X], self.center[Y], self.picture)
        super(MenuPanel, self).render()

    def animate(self):
        self.picture = MenuPanel.ANIMATION.next()

    def generate(self):
        self.main.initialize()
        self.main.run()

    def quit(self):
        self.main.input.quit = True
