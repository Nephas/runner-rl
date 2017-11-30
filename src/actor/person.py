import numpy as np
import random as rd

class Person:
    FIRST = {'Male': ['Reed', 'Jaime', 'Dewitt', 'Jewel', 'Rogelio',
                      'Theo', 'Man', 'Freddie', 'Russel', 'Jan', 'Erin',
                      'Frances', 'Hubert', 'Walker', 'Dale', 'Sydney',
                      'Dorsey', 'Carmen', 'Diego', 'Darren'],
             'Female': ['Dione', 'Shara', 'Pamula', 'Roselia', 'Mora', 'Laura',
                        'Hui', 'Bernice', 'Shalonda', 'Su', 'Earnestine',
                        'Ellena', 'Giselle', 'Kelle', 'Salley', 'Bernetta',
                        'Sharonda', 'Johnna', 'Reina', 'Ellen']}
    FIRST['Inter'] = FIRST['Male'] + FIRST['Female']

    LAST = ['Plyler', 'Northway', 'Rector', 'Terry', 'Corns',
            'Pusey', 'Padua', 'Osburn', 'Nisbet', 'January',
            'Tong', 'Ransome', 'Sweeten', 'Buel', 'Friar',
            'Gardener', 'Olmsted', 'Shemwell', 'Maloney', 'Jessup']
    NICK = ['Hack', 'Print', 'Friction', 'Impulse', 'Memory',
            'Bolt', 'Dapper', 'Beetle', 'Canine', 'Status']

    INTEREST = ['Hacking', 'Games', 'Sports', 'Music', 'Travel', 'Art']

    def __init__(self, actor, function=None):
        self.actor = actor

        self.gender = np.random.choice(['Male', 'Female', 'Inter'], p=[0.45, 0.45, 0.1])
        self.orientation = np.random.choice(['Hetero', 'Homo'], p=[0.9, 0.1])
        self.name = {'FIRST': rd.choice(Person.FIRST[self.gender]),
                     'LAST': rd.choice(Person.LAST),
                     'NICK': rd.choice([None, rd.choice(Person.NICK)])}

        self.function = function
        self.interest = list(set([rd.choice(Person.INTEREST), rd.choice(Person.INTEREST)]))

        self.rank = 0
        self.command = []
        self.friend = []
        self.lover = []

    def getName(self):
        string = self.name['FIRST'] + ' '
        if self.name['NICK'] is not None:
            string += '"{:}" '.format(self.name['NICK'])
        string += self.name['LAST']
        return string

    def getProfile(self):
        string = " Name: {:}\n".format(self.getName())
        string += "  Job: {:}\n".format(self.function)
        string += "Interests: " + reduce(lambda s1,s2: '{:}, {:}'.format(s1,s2), self.interest) + "\n"
        return string
