from src.globals import *

import numpy as np
import copy as cp
import time as t


class Geometry:
    def __init__(self, main):
        pass

    @staticmethod
    def rayCast(start, end):
        nPoints = np.max(np.abs(end - start)) + 1

        xLine = np.linspace(start[X], end[X], nPoints)
        yLine = np.linspace(start[Y], end[Y], nPoints)
        line = [[x, y] for x, y in zip(xLine, yLine)]
        return np.array(line).round().astype('int')

    @staticmethod
    def rayMap(r):
        lines = []
        start = np.array([0, 0])
        for end in Geometry.circleCast(r):
            lines.append(Geometry.rayCast(start, end)[1:r])
        return lines

    @staticmethod
    def circleCast(r):
        circle = []

        for phi in np.linspace(0, 2. * np.pi, int(r) * 30):
            end = (r * np.array([np.cos(phi), np.sin(phi)])).astype('int')
            if len(circle) == 0 or not all(circle[-1] == end):
                circle.append(end)
        return np.array(circle)

    @staticmethod
    def rayBresenham(start, end):
        line = []
        delta = end - start
        if delta[X] == 0:
            return np.array([[0, y] for y in range(start[Y], end[Y], np.sign(delta[Y]))] + [end])

        deltaerr = abs(delta[Y] / float(delta[X]))
        error = 0.0

        y = start[Y]
        for x in range(start[X], end[X]):
            line.append([x, y])
            error = error + deltaerr
            while error >= 0.5:
                y = y + np.sign(delta[Y])
                error = error - 1.0
        return np.array(line + [end])

    @staticmethod
    def midpointCircle(center, radius):
        (x0, y0) = center
        (x, y) = (0, radius)

        f = 1 - radius
        ddf_x = 1
        ddf_y = -2 * radius

        circle = [[x0, y0 + radius], [x0, y0 - radius],
                  [x0 + radius, y0], [x0 - radius, y0]]

        while x < y:
            if f >= 0:
                y -= 1
                ddf_y += 2
                f += ddf_y
            x += 1
            ddf_x += 2
            f += ddf_x
            circle += [[x0 + x, y0 + y],
                       [x0 - x, y0 + y],
                       [x0 + x, y0 - y],
                       [x0 - x, y0 - y],
                       [x0 + y, y0 + x],
                       [x0 - y, y0 + x],
                       [x0 + y, y0 - x],
                       [x0 - y, y0 - x]]
        return np.array(circle)

    @staticmethod
    def coneMap(r, dir, width=np.pi * 0.5):
        arc = []
        cone = []
        start = np.array([0, 0])

        for phi in np.linspace(dir - width / 2, dir + width / 2, int(r) * 20):
            end = (r * np.array([np.cos(phi), np.sin(phi)])).astype('int')
            if len(cone) == 0 or not all(cone[-1] == end):
                arc.append(end)

        for end in arc:
            cone.append(Geometry.rayCast(start, end)[1:r])
        return np.array(cone)


class Light:
    LIGHTMAP = [Geometry.rayMap(brightness) for brightness in range(0, 20)]

    def __init__(self):
        pass

    @staticmethod
    def cast(map, pos, brightness=1):
        cell = map.getTile(pos)
        cell.light = max(brightness, cell.light)
        for baseLine in Light.LIGHTMAP[brightness]:
            try:
                line = baseLine + pos
                strength = brightness
                for point in line:
                    cell = map.getTile(point)
                    cell.light = max(strength, cell.light)

                    if cell.block[LIGHT]:
                        strength -= 4
                    if cell.block[LOS] or strength < 0:
                        break
                    else:
                        strength -= 1
            except IndexError:
                pass
