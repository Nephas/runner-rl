from src.globals import *


class Agent(object):
    def __init__(self, actor=None, terminal=None, char='@', color=COLOR['BLACK']):
        self.actor = actor
        self.terminal = terminal

        self.supplyRoute = []

        self.char = char
        self.fg = list(color)

    def moveTo(self, cell):
        print(cell)
        print(cell.grid)
        if cell.grid in [None, True]:
            return 0
        else:
            newTerm = cell.grid
            newTerm.agents.append(self)
            self.terminal.agents.remove(self)
            self.terminal = Term
            return 2
