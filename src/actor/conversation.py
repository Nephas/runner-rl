import random as rd

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

        self.next = [Loop(self, actor),
                     Goodbye(self, actor)]


class Loop(Node):
    def __init__(self, parent, actor=None):
        Node.__init__(self, None, statement='Wanna know anything?', actor=actor)

        self.short = 'Ask more.'
        self.next = [Goodbye(self, actor),
                     Introduce(self, actor),
                     Interests(self, actor),
                     Provoke(self, actor)]

        for node in self.next:
            if node.next is None:
                node.next = self.next


class Introduce(Node):
    def __init__(self, parent, actor=None):
        Node.__init__(self, parent, statement=None, actor=actor)

        self.short = 'Introduce'
        self.statement = 'I am {:}. Nice to meet you.'.format(self.actor.person.getName())
        self.next = None


class Interests(Node):
    def __init__(self, parent, actor=None):
        Node.__init__(self, parent, statement=None, actor=actor)

        self.short = 'Interests'
        self.statement = 'My favorite pastime is {:}.'.format(rd.choice(self.actor.person.interest))
        self.next = None


class Provoke(Node):
    def __init__(self, parent, actor=None):
        Node.__init__(self, parent, statement='You bastard!', actor=actor)

        self.short = 'Provoke'
        self.next = []

    def effect(self):
        self.actor.ai.say(self.statement)
        self.actor.main.gui.pushMessage('-' * 20)
        self.actor.ai.switchState(Attack)


class Goodbye(Node):
    def __init__(self, parent, actor=None):
        Node.__init__(self, parent, statement='Goodbye', actor=actor)

        self.short = 'Goodbye'

    def effect(self):
        self.actor.ai.say(self.statement)
        self.actor.main.gui.pushMessage('-' * 20)
        self.actor.ai.switchState(Idle)
        self.actor.ai.mind['TARGET'] = None
