#!/usr/bin/env bash

rm -r /home/marco/Dropbox/runner/build_linux
rm -r /home/marco/Dropbox/runner/linux_64

pyinstaller --name=runner --clean --onefile --noconfirm \
    --add-data="graphics/exp_24x24.png:graphics" \
    --add-data="graphics/font_12x24.png:graphics" \
    --add-data="graphics/title.png:graphics" \
    --add-binary="/usr/local/lib/python2.7/dist-packages/bearlibterminal/libBearLibTerminal.so:./" \
    --workpath=/home/marco/Dropbox/runner/build_linux \
    --distpath=/home/marco/Dropbox/runner/linux_64 \
    main.py

cp -r graphics/ /home/marco/Dropbox/runner/linux_64
tar -cf /home/marco/Dropbox/runner/linux_64.tar /home/marco/Dropbox/runner/linux_64/
