#!/bin/sh

venv={venv_indicators}
. ${venv}/bin/activate
cd $(ls -d ${venv}/lib/python3.* | head -1)/site-packages
python3 -m {indicator_name}.{indicator_name}
deactivate
cd - > /dev/null
