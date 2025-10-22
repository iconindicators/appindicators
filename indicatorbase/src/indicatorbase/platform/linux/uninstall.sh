#!/bin/sh

rm -f $HOME/.local/bin/{indicator}.sh
rm -f $HOME/.local/share/applications/{indicator}.py.desktop
rm -f $HOME/.local/share/icons/hicolor/scalable/apps/{indicator}*.svg
rm -f -r $HOME/.cache/{indicator}
# Keep $HOME/.config/{indicator} as it may contain information the user wants.
