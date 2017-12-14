#!/usr/bin/env bash

pyinstaller --name=runner --clean  --noconfirm \
    --add-data="graphics/exp_24x24.png:graphics" \
    --add-data="graphics/font_12x24.png:graphics" \
    --add-data="graphics/title.png:graphics" \
    --add-data="gif/levelgen.gif:gif" \
    --add-binary="/usr/local/lib/python2.7/dist-packages/bearlibterminal/libBearLibTerminal.so:./" \
    --workpath=/home/marco/Dropbox/runner/build \
    --distpath=/home/marco/Dropbox/runner/dist \
    main.py
