#!/bin/sh

venv=$HOME/.local/venv_indicators
cd $HOME  #TODO Is this needed?
. ${venv}/bin/activate
python3 $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/{indicator_name}/{indicator_name}.py
deactivate
