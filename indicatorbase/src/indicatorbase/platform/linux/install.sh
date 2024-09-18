#!/bin/sh

indicator_path=$(ls -d $HOME/.local/venv_indicators/lib/python3.* | head -1)/site-packages/{indicator_name}

bin_path=$HOME/.local/bin
mkdir -p ${bin_path}
cp --remove-destination ${indicator_path}/platform/linux/{indicator_name}.sh ${bin_path} 

applications_path=$HOME/.local/share/applications
mkdir -p ${applications_path}
cp --remove-destination ${indicator_path}/platform/linux/{indicator_name}.py.desktop ${applications_path}

icons_path=$HOME/.local/share/icons/hicolor/scalable/apps
mkdir -p ${icons_path}
cp --remove-destination ${indicator_path}/icons/*.svg ${icons_path}
