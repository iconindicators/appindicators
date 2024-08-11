#!/bin/sh

rm -f $HOME/.local/bin/{indicator_name}.sh && \
rm -f $HOME/.local/share/applications/{indicator_name}.py.desktop && \
rm -f $HOME/.local/share/icons/hicolor/scalable/apps/{indicator_name}*.svg && \
rm -f -r $HOME/.local/venv_{indicator_name} && \
rm -f -r $HOME/.cache/{indicator_name} && \
rm -f -r $HOME/.config/{indicator_name}
