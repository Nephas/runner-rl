from src.globals import *


class AI:
    def __init__(self):
        pass

    @staticmethod
    def decide(actor, map):
        return actor.moveDir(rd.choice(NEIGHBORHOOD))
#            return 2
#        else:
#            return 0
