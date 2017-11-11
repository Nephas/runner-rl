from src.globals import *

import random as rd

from src.object.object import Object
from src.render import Render


class Lamp(Object):
    def __init__(self, cell=None, brightness=12):
        Object.__init__(self, cell, char=7)

        self.on = True
        self.brightness = brightness
        self.lightmap = Render.rayMap(brightness, brightness*3)

    def physics(self, map):
        if self.on:
            self.castLight(map)

    def castLight(self, map):
        self.cell.light =  max(self.brightness, self.cell.light)
        for baseLine in self.lightmap:
            line = baseLine + self.cell.pos
            for i, point in enumerate(line):
                cell = map.getTile(point)
                if not cell.block[LOS]:
                    cell.light = max((self.brightness - i), cell.light)
                else:
                    break

    def interact(self, actor=None, dir=None, type=None):
        if type is 'ATTACK':
            self.destroy()
            return 5
        else:
            self.on = not self.on
            return 3

    def describe(self):
        return "Lamp"


class DoorLamp(Lamp):
    def __init__(self, cell=None, brightness=4):
        Lamp.__init__(self, cell, brightness=brightness)

        self.fg = COLOR['RED']
        self.counter = 0

    def physics(self, map):
        self.counter += 1
        if self.counter % 4 == 0:
            self.on = not self.on
        if self.on:
            self.fg = COLOR['WHITE']
            self.castLight(map)
        else:
            self.fg = COLOR['RED']

    def describe(self):
        return "Emergency Light"



class FlickerLamp(Lamp):
    def __init__(self, cell=None, brightness=8):
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
            self.castLight(map)

class SpotLight(Lamp):
    def __init__(self, cell=None, brightness=16):
        Lamp.__init__(self, cell, brightness=brightness)

        self.lightmap = Render.coneMap(brightness, 12, 1.2)
