from src.actor.ai import AI, Idle, Attack


class Conversation(AI):
    def __init__(self, actor, mind):
        AI.__init__(self, actor, mind)

        self.actor.main.gui.pushMessage('-' * 20)

        self.counter = 100
        self.node = None
        self.choice = Greeting(self.actor)

    def decide(self, map):
        self.counter -= 1

        if self.choice is not None:
            self.node = self.choice
            self.node.printOptions(self.actor.main.gui)
            self.node.effect()
            self.choice = None
            self.counter += 20

        if self.counter <= 0:
            self.cut(self.actor.main.gui)
        return []

    def cut(self, gui):
        self.switchState(Idle)
        self.mind['TARGET'] = None
        self.say("Huh, seems like I'm not getting any answer.")
        self.actor.main.gui.pushMessage('-' * 20)

    def say(self, string):
        self.actor.main.gui.pushMessage(self.actor.describe() + ': ' + string)

    def chooseOption(self, index):
        try:
            self.choice = self.node.next[index]
        except IndexError:
            self.choice = None
        return 1

class Node(object):
    def __init__(self, parent, statement='Hi', actor=None):
        self.actor = actor
        self.short = None
        self.statement = statement

        self.parent = parent
        self.next = []

    def printOptions(self, gui):
        for i, option in enumerate(self.next):
            gui.pushMessage('{:>4}: '.format(i) + option.short)

    def effect(self):
        self.actor.ai.say(self.statement)


class Greeting(Node):
    def __init__(self, actor=None):
        Node.__init__(self, None, statement='Hi', actor=actor)

        self.next = [Goodbye(self, actor),
                     Provoke(self, actor)]

class Provoke(Node):
    def __init__(self, parent, actor=None):
        Node.__init__(self, parent, statement='You bastard!', actor=actor)

        self.short = 'Provoke'
        self.next = []

    def effect(self):
        self.actor.main.gui.pushMessage('-' * 20)
        self.actor.ai.say(self.statement)
        self.actor.ai.switchState(Attack)

class Goodbye(Node):
    def __init__(self, parent, actor=None):
        Node.__init__(self, parent, statement='Goodbye', actor=actor)

        self.short = 'Goodbye'

    def effect(self):
        self.actor.main.gui.pushMessage('-' * 20)
        self.actor.ai.say(self.statement)
        self.actor.ai.switchState(Idle)
        self.actor.ai.mind['TARGET'] = None
