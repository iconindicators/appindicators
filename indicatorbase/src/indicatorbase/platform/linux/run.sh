#!/bin/sh

. ${venv}/bin/activate
cd $(ls -d ${venv}/lib/python3.* | head -1)/site-packages
python3 -m {indicator}.{indicator}
deactivate
cd - > /dev/null
