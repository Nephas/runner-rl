from src.globals import *


class Body:
    def __init__(self, actor):
        self.actor = actor
        self.status = []

    def takeHit(self):
        pass

    def physics(self, map):
        for stat in self.status:
            stat.physics(map)

    def addStatus(self, newStatus):
        for stat in self.status:
            if stat.__class__ is newStatus.__class__:
                stat.stack(newStatus)
                return
        self.status.append(newStatus)
        newStatus.cell = self


class Status:
    def __init__(self, actor):
        self.actor = actor

    def physics(self, map):
        pass

    def stack(self, other):
        self.amount = min(16, self.amount + other.amount)


class SlowMo(Status):
    def __init__(self, actor, amount=20):
        Status.__init__(self, actor)
        self.amount = amount

    def physics(self, map):
        if self.amount > 0:
            self.actor.main.input.pause = True
            self.amount -= 1
        else:
            self.actor.main.input.pause = False
