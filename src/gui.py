import numpy as np

class Gui:
    def __init__(self, parent):
        self.parent = parent
        self.mapOffset = np.array([10,10])
        self.cursorPos = np.array([0,0])
