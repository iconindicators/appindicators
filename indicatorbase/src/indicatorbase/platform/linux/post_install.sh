#!/bin/sh

INDICATOR_PATH=$(ls -d $HOME/.local/venv_{indicator_name}/lib/python3.* | head -1)/site-packages/{indicator_name}
mkdir -p $HOME/.local/bin && \
cp --remove-destination INDICATOR_PATH/platform/linux/{indicator_name}.sh $HOME/.local/bin && \
mkdir -p $HOME/.local/share/applications && \
cp --remove-destination INDICATOR_PATH/platform/linux/{indicator_name}.py.desktop $HOME/.local/share/applications && \
mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps && \
cp --remove-destination INDICATOR_PATH/icons/*.svg $HOME/.local/share/icons/hicolor/scalable/apps
