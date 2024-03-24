#!/bin/sh

cd $HOME && \
. .local/venv_{indicator_name}/bin/activate && \
python3 $(ls -d $HOME/.local/venv_{indicator_name}/lib/python3.* | head -1)/site-packages/{indicator_name}/ {indicator_name}.py && \
deactivate
