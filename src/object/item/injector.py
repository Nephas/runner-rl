from src.globals import *

from src.object.item.item import Item
from src.actor.body import SlowMo

import numpy as np


class Injector(Item):
    def __init__(self, cell=None, carrier=None, tier=0):
        Item.__init__(self, cell, carrier, char=0x103A)

        self.amount = 3
        self.content = SlowMo(self.carrier)

    def describe(self):
        return self.content.describe() + ' ({:})'.format(self.amount)

    def use(self, action=None):
        if self.amount > 0:
            self.carrier.body.addStatus(cp.copy(self.content))
            self.amount -= 1
            return 1
        else:
            return 0
