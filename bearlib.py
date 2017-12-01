from bearlibterminal import terminal

terminal.open()

terminal.setf("window: size=100x80, title='runner'")
terminal.setf("font: graphics/ext_12x24.png, size=12x24, codepage=437")
terminal.setf("0x1000: graphics/ext_24x24.png, size=24x24, align=top-left")


terminal.printf(2, 1, "Hello, world!")
terminal.put(2, 2, 0x1002)

terminal.refresh()
while terminal.read() != terminal.TK_CLOSE:
    pass
terminal.close()
