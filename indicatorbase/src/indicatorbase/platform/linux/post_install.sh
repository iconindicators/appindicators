#!/bin/sh

indicator_path=$(ls -d $HOME/.local/venv_indicators/lib/python3.* | head -1)/site-packages/{indicator_name}
mkdir -p $HOME/.local/bin
cp --remove-destination ${indicator_path}/platform/linux/{indicator_name}.sh $HOME/.local/bin
mkdir -p $HOME/.local/share/applications
cp --remove-destination ${indicator_path}/platform/linux/{indicator_name}.py.desktop $HOME/.local/share/applications
mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps
cp --remove-destination ${indicator_path}/icons/*.svg $HOME/.local/share/icons/hicolor/scalable/apps
