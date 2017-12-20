from src.globals import *

import random as rd
import numpy as np

from src.object.object import Object
from src.render.geometry import Geometry, Light


class Lamp(Object):
    def __init__(self, cell=None, brightness=7):
        Object.__init__(self, cell, char=0x1007)

        self.on = True
        self.brightness = brightness

    def physics(self, map):
        if self.on:
            Light.cast(map, self.cell.pos, self.brightness)

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5
        else:
            # Gui.pushMessage('You switch the ' + self.describe())
            self.on = not self.on
            return 3

    def describe(self):
        return "Lamp"


class DoorLamp(Lamp):
    def __init__(self, cell=None, brightness=5):
        Lamp.__init__(self, cell, brightness=brightness)

        self.fg = COLOR['RED']
        self.counter = 0

    def physics(self, map):
        self.counter += 1
        if self.counter % 10 == 0:
            self.on = not self.on
        if self.on:
            self.fg = COLOR['WHITE']
            Light.cast(map, self.cell.pos, self.brightness)
        else:
            self.fg = COLOR['RED']

    def describe(self):
        return "Emergency Light"



class FlickerLamp(Lamp):
    def __init__(self, cell=None, brightness=7):
        Lamp.__init__(self, cell, brightness=brightness)

        self.counter = 0

    def physics(self, map):
        self.counter += rd.randint(0,2)

        if self.counter > 100:
            self.counter = 0
            self.on = False
        else:
            self.on = True

        if self.on:
            Light.cast(map, self.cell.pos, self.brightness)

class SpotLight(Lamp):
    def __init__(self, cell=None, direction=0, brightness=12):
        Lamp.__init__(self, cell, brightness=brightness)

        self.direction = direction
        self.lightmap = Geometry.coneMap(brightness, direction, width=np.pi*0.25)
