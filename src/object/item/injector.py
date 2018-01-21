from src.globals import *

from src.object.item.item import Item
from src.actor.body import SlowMo

import numpy as np
import copy as cp


class Injector(Item):
    ANIMATION = [0x2002, 0x2012, 0x2022, 0x2032, 0x2042, 0x2052, 0x2002]

    def __init__(self, cell=None, carrier=None, tier=0):
        Item.__init__(self, cell, carrier, char=0x103A, icon=0x2002)

        self.amount = 3
        self.content = SlowMo(self.carrier)

    def describe(self):
        return self.content.describe() + ' ({:})'.format(self.amount)

    def use(self, action=None):
        if self.amount <= 0:
            return 1

        super(self.__class__, self).use()

        self.carrier.body.addStatus(cp.copy(self.content))
        self.amount -= 1
        return 5
