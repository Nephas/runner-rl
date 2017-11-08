import math as m
import numpy as np
import random as rd
import itertools as it


class Corp:

    NAMES = ['Tyrell',
             'Weyland',
             'Yutani',
             'Thyssen',
             'Yamaha',
             'Intel',
             'Exxon']

    SECTORS = ['Aerospace',
               'Defense',
               'Bio-Tech',
               'Medicare',
               'Nutrition',
               'Electronics',
               'Robotics',
               'Data Services',
               'Logistics']

    def __init__(self, main=None):

        self.name = rd.choice(Corp.NAMES) + ' ' + rd.choice(Corp.SECTORS)

        self.places = []
        self.people = []
