#!/bin/sh


# The full path to the virtual environment directory must be passed as the
# first argument.  For example:
#       $HOME/.local/venv_indicators


indicator_path=$(ls -d $1/lib/python3.* | head -1)/site-packages/{indicator}

bin_path=$HOME/.local/bin
mkdir -p ${bin_path}
cp --remove-destination ${indicator_path}/platform/linux/{indicator}.sh ${bin_path}
sed -i "3s,^,venv=$1\n," ${bin_path}/{indicator}.sh

applications_path=$HOME/.local/share/applications
mkdir -p ${applications_path}
cp --remove-destination ${indicator_path}/platform/linux/{indicator}.py.desktop ${applications_path}

icons_path=$HOME/.local/share/icons/hicolor/scalable/apps
mkdir -p ${icons_path}
cp --remove-destination ${indicator_path}/icons/*.svg ${icons_path}
