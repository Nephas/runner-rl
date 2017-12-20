#!/usr/bin/env bash

rm -r /home/marco/Dropbox/runner/build_win
rm -r /home/marco/Dropbox/runner/win_64

wine ~/.wine/drive_c/Python27/Scripts/pyinstaller.exe --onefile --name=runner --clean --noconfirm \
    --hidden-import=bearlibterminal\
    --hidden-import=numpy\
    --workpath=/home/marco/Dropbox/runner/build_win \
    --distpath=/home/marco/Dropbox/runner/win_64 \
    main.py

cp -r graphics/ /home/marco/Dropbox/runner/win_64
