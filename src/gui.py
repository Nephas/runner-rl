import numpy as np


class Gui:
    def __init__(self, main):
        self.main = main
        self.mapOffset = np.array([10, 10])
        self.cursorPos = np.array([0, 0])

    def updateCursor(self, pos):
        mapPos = np.array(pos) + self.mapOffset - self.main.render.MAPINSET
        if self.main.map.contains(mapPos):
            self.cursorPos = mapPos
