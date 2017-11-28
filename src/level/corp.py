import math as m
import numpy as np
import random as rd
import itertools as it

import colorsys as cs


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
               'Nutrition',
               'Robotics',
               'Data Services']

#               'Electronics',
#               'Medicare',
#               'Biotech',
#               'Logistics'

    PALETTE = {'Tyrell': 0.1,
               'Weyland': 0.2,
               'Yutani': 0.3,
               'Thyssen': 0.5,
               'Yamaha': 0.6,
               'Intel': 0.8,
               'Exxon': 1.0}

    STRUCT = {'Aerospace': [{'CHILDREN': [0, 0], 'SIZES': [10, 20], 'SHAPES': ['Room']},
                            {'CHILDREN': [1, 1], 'SIZES': [5, 15], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 40], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 30], 'SHAPES': ['Corridor', 'Dome', 'Hall']},
                            {'CHILDREN': [3, 4], 'SIZES': [10, 20], 'SHAPES': ['Corridor', 'Room']},
                            {'CHILDREN': [4, 6], 'SIZES': [7, 15], 'SHAPES': ['Office', 'Lab']}],
                'Defense': [{'CHILDREN': [0, 0], 'SIZES': [10, 20], 'SHAPES': ['Room']},
                            {'CHILDREN': [1, 1], 'SIZES': [5, 15], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 40], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 30], 'SHAPES': ['Corridor', 'Dome', 'Hall']},
                            {'CHILDREN': [3, 4], 'SIZES': [10, 20], 'SHAPES': ['Corridor', 'Room']},
                            {'CHILDREN': [4, 6], 'SIZES': [7, 12], 'SHAPES': ['Office', 'Lab']}],
               'Robotics': [{'CHILDREN': [0, 0], 'SIZES': [10, 20], 'SHAPES': ['Room']},
                            {'CHILDREN': [1, 1], 'SIZES': [5, 15], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 40], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 30], 'SHAPES': ['Corridor', 'Storage', 'Hall', 'ServerFarm']},
                            {'CHILDREN': [3, 4], 'SIZES': [10, 20], 'SHAPES': ['Corridor', 'Room']},
                            {'CHILDREN': [4, 6], 'SIZES': [7, 15], 'SHAPES': ['Office', 'Lab']}],
          'Data Services': [{'CHILDREN': [0, 0], 'SIZES': [10, 20], 'SHAPES': ['Room']},
                            {'CHILDREN': [1, 1], 'SIZES': [5, 15], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 40], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 30], 'SHAPES': ['ServerFarm']},
                            {'CHILDREN': [3, 4], 'SIZES': [10, 20], 'SHAPES': ['Corridor', 'Room']},
                            {'CHILDREN': [4, 6], 'SIZES': [5, 12], 'SHAPES': ['Office']}],
              'Nutrition': [{'CHILDREN': [0, 0], 'SIZES': [10, 20], 'SHAPES': ['Room']},
                            {'CHILDREN': [1, 1], 'SIZES': [5, 15], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 40], 'SHAPES': ['Corridor']},
                            {'CHILDREN': [2, 4], 'SIZES': [20, 30], 'SHAPES': ['Dome', 'GreenHouse']},
                            {'CHILDREN': [3, 4], 'SIZES': [10, 20], 'SHAPES': ['Corridor', 'Room']},
                            {'CHILDREN': [4, 6], 'SIZES': [7, 10], 'SHAPES': ['Lab']}]}

    LAYOUT = ['CROSS', 'CORNER', 'RING', 'DUAL']

    def __init__(self, main=None):

        self.facility = rd.choice(Corp.NAMES) + ' ' + rd.choice(Corp.SECTORS)

        self.places = []
        self.people = []

        self.randomize()

    def randomize(self):
        self.name = rd.choice(Corp.NAMES)
        self.sector = rd.choice(Corp.SECTORS)

        self.layout = rd.choice(Corp.LAYOUT)
        self.struct = Corp.STRUCT[self.sector]
        self.palette, self.complement = Corp.randColorPalette(len(self.struct) + 1, Corp.PALETTE[self.name])


    def __repr__(self):
        string = 'Name:   ' + str(self.facility) + '\n'
        string += 'Shape:  ' + str(self.layout) + '\n'
        string += 'Struct: ' + str(self.struct)
        return string

    @staticmethod
    def randColorPalette(length, start):
        startcol = [start, 0.5, 0.9]

        colors = []
        for i in np.linspace(0, 1 / 12., length):
            col = startcol
            col[0] = (col[0] + i) % 1.0
            colors.append((255 * np.array(cs.hsv_to_rgb(*col))).astype('int'))

        startcol[0] += 0.5
        startcol[1] = 0.9

        complement = []
        for i in np.linspace(0, 1 / 12., length):
            col = startcol
            col[0] = (col[0] + i) % 1.0
            complement.append(
                (255 * np.array(cs.hsv_to_rgb(*col))).astype('int'))

        return (colors + [np.array((10, 10, 10))], complement + [np.array((10, 10, 10))])
