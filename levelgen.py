#!/usr/bin/env python

from src.globals import *
from src.map import Map
from src.render import Renderer
import tdl

map = Map()

stats = [0, 0, 0]
while not (stats[0] >= 30 and stats[1] >= 12 and stats[2] >= 6 and stats[3] <= 1):
    stats = map.generateLevel()
    print stats

Renderer.printImage(map, "levelgen.bmp")
