from bearlibterminal import terminal as term

from src.globals import *

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
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                yield map.tile[x][y]

    def getObjects(self, map):
        for x in range(self.x[MIN], self.x[MAX]):
            for y in range(self.y[MIN], self.y[MAX]):
                for obj in map.tile[x][y].object:
                    yield obj

class Panel:
    def __init__(self, main, pos, w, h, layer=0):
        self.main = main
        self.pos = np.array(pos)
        self.size = np.array([w, h])
        self.x = [pos[X], pos[X] + w]
        self.y = [pos[Y], pos[Y] + h]
        self.center = (self.pos + self.size / 2).round().astype('int')
        self.layer = layer

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

    def clear(self, color=COLOR['BLACK']):
        term.layer = self.layer
        term.bkcolor(term.color_from_argb(255, *color))
        term.clear_area(self.pos[X], self.pos[Y], *self.size)

    def printString(self, pos, string, color=COLOR['WHITE']):
        term.layer = self.layer
        term.color(term.color_from_argb(255, *color))
        pos += self.pos
        term.printf(pos[X], pos[Y], string)

    def render(self):
        pass


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


    def render(self, map):
        self.clear()
#        if self.mapLayer == 0:
        for cell in self.camera.getCells(map):
            self.draw(cell, self.SCALE*(cell.pos + self.pos - self.mapOffset))
#        elif self.mapLayer == 1:
#        for cell in gui.getCells(map):
#            cell.drawNet(self, cell.pos - gui.mapOffset)

        try:
            cell = map.getTile(self.main.player.cell.pos + self.cursorDir)
            cursorPos = self.SCALE*(cell.pos - self.mapOffset + self.pos)
            self.highlight(cell, cursorPos)

            cell = map.getTile(self.cursorPos)
            cursorPos = self.SCALE*(cell.pos - self.mapOffset) + self.pos
            self.highlight(cell, cursorPos)
        except:
            pass

    def draw(self, cell, panelPos):
        term.layer = self.backLayer
        term.bkcolor(term.color_from_argb(255, *cell.bg))
        term.color(term.color_from_argb(255, *cell.fg))

        term.layer = self.objectLayer
        if cell.vision[LOS]:
            term.put(panelPos[X], panelPos[Y], cell.char[VIS])
        elif cell.vision[EXP]:
            term.put(panelPos[X], panelPos[Y], cell.char[VIS])

    def highlight(self, cell, panelPos):
        term.layer = self.backLayer
        term.color(term.color_from_argb(255, *cell.fg))
        term.put(panelPos[X], panelPos[Y], 0x1001)

    def updateCursor(self, terminalPos=np.array([8, 8])):
#        if not Render.inMap(terminalPos):
#            return

        mapPos = (terminalPos - self.pos)
        mapPos[X] = mapPos[X] // 2

        mapPos += self.mapOffset

        if self.main.map.contains(mapPos):
            self.cursorPos = mapPos

        print(self.cursorPos)

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

    def getCells(self, map):
        return


class InfoPanel(Panel):
    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

    def render(self, gui, main):
        self.clear()
#        self.printString(np.array([1, 1]), "Hello World")

        actions = ''
        for i in range(1 + (main.tic % main.TIC_SEC)):
            actions += '>'
        actions += ' '
        for i in range(main.player.cooldown):
            actions += '-'
        self.printString(np.array([1, 1]), actions)

        # lighting bar
        # for i in range(6):
        #     self.draw_char(1 + i, 3, 7, self.main.player.cell.bg)
        # for i in range(int(float(self.main.player.cell.light) / MAX_LIGHT * 6)):
        # #     panel.draw_char(1 + i, 3, 15)

        if self.main.map.contains(gui.cursorPos):
            cursorTile = self.main.map.getTile(gui.cursorPos)
            if cursorTile.vision[LOS] is True:
                if cursorTile.room is not None:
                    self.printString(np.array([1, 5]), cursorTile.room.describe())
                for i, obj in enumerate(cursorTile.object + cursorTile.effect):
                    self.printString(np.array([1, 7 + 2 * i]), obj.describe())


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

    def render(self, main):
        self.clear()
        pos = 0

        for string, color in self.MESSAGES[self.messageOffset:]:
            # line wrapping in list comprehension
            block = [string[i:i + self.size[X] - 2]
                     for i in range(0, len(string), self.size[Y] - 2)]
            for line in block:
                pos += 1
                if pos >= self.size[Y] - 1:
                    break
                self.printString(np.array([1, pos]), line)

            pos += 1
            if pos >= self.size[Y] - 1:
                break


class InventoryPanel(Panel):
    def __init__(self, main, pos, w, h, layer=0):
        Panel.__init__(self, main, pos, w, h, layer=0)

    def render(self, gui, player):
        self.clear()

        for i, item in enumerate(player.inventory[gui.inventoryOffset:]):
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
