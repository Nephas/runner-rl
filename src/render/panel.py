from bearlibterminal import terminal as term

from src.globals import *
from src.actor.ai import AI


class Rectangle:  # a rectangle on the map. used to characterize a room or a window
    def __init__(self, pos, w, h):
        self.pos = np.array(pos)
        self.size = np.array([w, h])
        self.x = [pos[X], pos[X] + w]
        self.y = [pos[Y], pos[Y] + h]
        self.center = (self.pos + self.size / 2).round().astype('int')
        self.area = w * h

    def intersects(self, other):  # returns true if this rectangle intersects with another one
        return not (self.x[MAX] <= other.x[MIN] or other.x[MAX] <= self.x[MIN] or self.y[MAX] <= other.y[MIN] or
                    other.y[MAX] <= self.y[MIN])

    def contains(self, pos):
        return pos[X] in range(*self.x) and pos[Y] in range(*self.y)

    def border(self):
        positions = []
        for x in range(self.x[MIN], self.x[MAX]):
            positions.append([x, self.y[MIN]])
            positions.append([x, self.y[MAX] - 1])
        for y in range(self.y[MIN], self.y[MAX]):
            positions.append([self.x[MIN], y])
            positions.append([self.x[MAX] - 1, y])
        return positions

    def drawFrame(self, map, color):
        for pos in self.border():
            map.getTile().bg = color

    def getPositions(self):
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                yield [x, y]

    def getCells(self, map):
        for x in range(max(0, self.x[MIN]), min(self.x[MAX], map.WIDTH)):
            for y in range(max(0, self.y[MIN]), min(self.y[MAX], map.HEIGHT)):
                yield map.tile[x][y]

    def getObjects(self, map):
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                for obj in map.tile[x][y].object:
                    yield obj


class Panel(object):
    def __init__(self, main, pos, w, h, layer=0):
        self.main = main
        self.pos = np.array(pos)
        self.size = np.array([w, h])
        self.x = [pos[X], pos[X] + w]
        self.y = [pos[Y], pos[Y] + h]
        self.center = (self.pos + self.size / 2).round().astype('int')
        self.layer = layer
        self.cursor = False

    def updateCursor(self, pos):
        self.cursor = self.contains(pos)

    def handleScroll(self, offset=0):
        pass

    def handleClick(self, event=0):
        pass

    def contains(self, pos):
        return pos[X] in range(*self.x) and pos[Y] in range(*self.y)

    def border(self):
        positions = []
        for x in range(self.x[MIN], self.x[MAX]):
            positions.append([x, self.y[MIN]])
            positions.append([x, self.y[MAX] - 1])
        for y in range(self.y[MIN], self.y[MAX]):
            positions.append([self.x[MIN], y])
            positions.append([self.x[MAX] - 1, y])
        return positions

    def bracket(self):
        positions = []
        for x in range(self.x[MIN] - 2, self.x[MIN] + self.size[X] * 2 // 3, 2):
            positions.append([x, self.y[MIN] - 1])
        for y in range(self.y[MIN] - 1, self.y[MIN] + self.size[Y] * 2 // 3):
            positions.append([self.x[MIN] - 2, y])
        return positions

    def clear(self, color=COLOR['BLACK']):
        term.layer(0)
        term.bkcolor(term.color_from_argb(255, *color))
        term.clear_area(self.pos[X], self.pos[Y], *self.size)

    def printString(self, pos, string, color=COLOR['WHITE']):
        term.color(term.color_from_argb(255, *color))
        pos += self.pos
        term.printf(pos[X], pos[Y], string)

    def printChar(self, pos, char, color=COLOR['WHITE']):
        term.color(term.color_from_argb(255, *color))
        pos += self.pos
        term.put(pos[X], pos[Y], char)

    def render(self):
        self.clear()
        term.layer(10)

        if self.cursor:
            term.color(term.color_from_argb(255, 64, 64, 64))
            term.color
            for pos in self.bracket():
                term.put(pos[X], pos[Y], 0x10FA)


class MapPanel(Panel):
    SCALE = np.array([2, 1])

    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)
        self.map = main.map

        self.backLayer = 0
        self.effectLayer = 1
        self.objectLayer = 2

        self.mapOffset = np.array([0, 0])
        self.cursorPos = np.array([64, 64])
        self.cursorDir = np.array([1, 1])
        self.camera = Rectangle(self.mapOffset, 0, 0)

    def handleClick(self, button='LEFT'):
        self.main.player.actions = []

        if button is 'LEFT' and len(self.main.player.actions) < 2:
            self.main.player.actions = AI.findPath(
                self.map, self.main.player.cell.pos, self.cursorPos, False)
        elif button is 'RIGHT' and len(self.main.player.actions) < 2:
            self.main.player.actions = AI.findPath(
                self.map, self.main.player.cell.pos, self.cursorPos, True)

    def handleScroll(self, offY):
        offset = np.array([0, offY])
        self.moveOffset(offset)

    def render(self):
        super(MapPanel, self).render()

        for cell in self.camera.getCells(self.map):
            self.draw(cell, self.SCALE *
                      (cell.pos - self.mapOffset) + self.pos)

        for mapPos in [self.main.player.cell.pos + self.cursorDir, self.cursorPos]:
            try:
                cell = self.map.getTile(mapPos)
                panelPos = self.SCALE * (cell.pos - self.mapOffset) + self.pos
                self.highlight(cell, panelPos)
            except:
                pass

    def draw(self, cell, panelPos):
        term.composition(True)

        i = 0
        for color, tile in zip(cell.color, cell.stack):
            if tile is not None:
                term.layer(i)
                term.color(term.color_from_argb(255, *color))
                term.put(panelPos[X], panelPos[Y], tile)
            i += 1

    def highlight(self, cell, panelPos):
        term.layer(3)
        term.color(term.color_from_argb(255, *COLOR['WHITE']))
        term.put(panelPos[X], panelPos[Y], 0x1020)

    def updateCursor(self, terminalPos=np.array([8, 8])):
        super(MapPanel, self).updateCursor(terminalPos)

        mapPos = (terminalPos - self.pos) // self.SCALE + self.mapOffset

        if self.main.map.contains(mapPos):
            self.cursorPos = mapPos

        ray = mapPos - self.main.player.cell.pos
        length = np.linalg.norm(ray)
        if length > 0:
            self.cursorDir = (ray / length).round().astype('int')

    def moveOffset(self, dir=np.array([0, 0])):
        self.mapOffset += dir
        self.cursorPos += dir
        (panelX, panelY) = self.size
        self.camera = Rectangle(self.mapOffset, panelX // 2, panelY)
        self.updateRender(self.map)

    def updateRender(self, map):
        for cell in self.camera.getCells(map):
            cell.updateRender()


class InfoPanel(Panel):
    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

    def render(self):
        super(InfoPanel, self).render()

        row = 1

        self.printString(np.array([1, row]), 'Tics:  ')

        actions = ''
        for i in range(1 + (self.main.tic % self.main.TIC_SEC)):
            actions += '>'
        actions += ' '
        for i in range(self.main.player.cooldown):
            actions += '-'
        self.printString(np.array([7, row]), actions)

        row = 2

        # lighting bar
        self.printString(np.array([1, row]), 'Light: ')

#        for i in range(6):
#            self.printChar(np.array([7 + 2 * i, row]), 0x10FF)
        for i in range(int(float(self.main.player.cell.light) / MAX_LIGHT * 6)):
            self.printChar(np.array([7 + 2 * i, row]), 0x1007)

        mapPanel = self.main.render.mapPanel

        row = 3

        if self.main.map.contains(mapPanel.cursorPos):
            cursorTile = self.main.map.getTile(mapPanel.cursorPos)
            if cursorTile.vision[LOS] is True:
                if cursorTile.room is not None:
                    self.printString(
                        np.array([1, row]), cursorTile.room.describe())

                row = 4

                for i, obj in enumerate(cursorTile.object + cursorTile.effect):
                    self.printChar(np.array([1, row + i]), obj.char)
                    self.printString(np.array([4, row + i]), obj.describe())


class MessagePanel(Panel):
    MESSAGES = [
        ('The hum from the vents reminds you of a TV tuned to a dead channel.', COLOR['GREEN'])]

    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

        self.messageOffset = 0

    @staticmethod
    def pushMessage(string, color=COLOR['WHITE']):
        if not self.MESSAGES[0][0] == string:
            self.MESSAGES.insert(0, (string, color))

    def render(self):
        super(MessagePanel, self).render()

        pos = 0

        for string, color in self.MESSAGES[self.messageOffset:]:
            # line wrapping in list comprehension
            block = [string[i:i + self.size[X] - 2] for i in range(0, len(string), self.size[X] - 2)]
            for line in block:
                pos += 1
                if pos >= self.size[Y] - 1:
                    break
                self.printString(np.array([1, pos]), line)

#            pos += 1
#            if pos >= self.size[Y] - 1:
#                break

    def handleScroll(self, offset):
        self.messageOffset += offset
        self.messageOffset = max(0, self.messageOffset)



class InventoryPanel(Panel):
    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

        self.player = main.player
        self.inventoryOffset = 0

    def render(self):
        super(InventoryPanel, self).render()

        for i, item in enumerate(self.player.inventory[self.inventoryOffset:]):
            pos = i + 1
            if pos >= self.size[Y] - 1:
                break

            if i == 0:
                self.printString(np.array([1, pos]),
                                 'SPACE: ' + item.describe(), item.fg)
            elif i <= 4:
                self.printString(
                    np.array([1, pos]), '    {:}: '.format(i) + item.describe())
            else:
                self.printString(np.array([1, pos]),
                                 '       ' + item.describe())

    def handleScroll(self, offset):
        self.inventoryOffset += offset
        self.inventoryOffset = max(0, self.inventoryOffset)
