# AppIndicators for Ubuntu et al...


## Introduction
This project contains application indicators written in `Python3` for `Ubuntu 20.04` or equivalent as follows:
- `indicatorfortune` - (https://pypi.org/project/indicatorfortune/)[https://pypi.org/project/indicatorfortune/]
- `indicatorlunar` - (https://pypi.org/project/indicatorlunar/)[https://pypi.org/project/indicatorlunar/]
- `indicatoronthisday` - (https://pypi.org/project/indicatoronthisday/)[https://pypi.org/project/indicatoronthisday/]
- `indicatorppadownloadstatistics` - (https://pypi.org/project/indicatorppadownloadstatistics/)[https://pypi.org/project/indicatorppadownloadstatistics/]
- `indicatorpunycode` - (https://pypi.org/project/indicatorpunycode/)[https://pypi.org/project/indicatorpunycode/]
- `indicatorscriptrunner` - (https://pypi.org/project/indicatorscriptrunner/)[https://pypi.org/project/indicatorscriptrunner/]
- `indicatorstardate` - (https://pypi.org/project/indicatorstardate/)[https://pypi.org/project/indicatorstardate/]
- `indicatortest` - (https://pypi.org/project/indicatortest/)[https://pypi.org/project/indicatortest/]
- `indicatortide` - (https://pypi.org/project/indicatortide/)[https://pypi.org/project/indicatortide/]
- `indicatorvirtualbox` - (https://pypi.org/project/indicatorvirtualbox/)[https://pypi.org/project/indicatorvirtualbox/]

Each indicator shares the common code base `indicatorbase`.


## Release Procedure
A release involves building a `Python` wheel and uploading to `PyPI`.
1. To build a wheel for one or more indicators, open a terminal and...
`python3 tools/build_wheel.py release indicatorfortune`
which will create a `.whl` and `.tar.gz` for `indicatorfortune` in `release/wheel/dist_indicatorfortune`. 

2. Upload the wheel to `PyPI`, open a terminal and...
`python3 tools/upload_wheel.py release/wheel/dist_indicatorfortune`
which prompt for the username (__token__) and password (which starts with 'pypi-') and then upload the `.whl` and `.tar.gz` to `PyPI`.


## Testing on TestPyPI
A wheel can be uploaded to `TestPyPI`.
TODO Figure out the upload command to TestPyPI (from history...also must be a venv in there somewhere).

To install: TODO...
Because the dependencies (listed in `pyproject.toml`) will be unavailable at `TestPyPI`, will need to specify an alternate install command.  To upload say `indicatortest`:
python3 -m venv venv
. ./venv/bin/activate
python3 -m pip install --extra-index-url https://test.pypi.org/simple/ indicatortest
 #   python3 venv_indicatortest/lib/python3.8/site-packages/indicatortest/indicatortest.py 
 #
 # https://stackoverflow.com/questions/60868060/module-on-test-pypi-cant-install-dependencies-even-though-they-exist
 #
 # https://test.pypi.org/project/indicatortest/
 # https://packaging.python.org/en/latest/tutorials/packaging-projects/


## Testing a Local Wheel
- Document how to build/install/run a wheel locally for testing
  python3 utils/buildWheel.py release indicatortest
  . /venv/bin/activate
  python3 -m pip install release/wheel/indicatortest-1.0.6-py3-none-any.whl
  python3 venv/lib/python3.8/site-packages/indicatortest/indicatortest.py
  python3 -m pip uninstall indicatortest


## TODO
- Do high level renaming according to standards.
  Naming of project, naming of modules (files), naming of classes.
  Then naming of globals, naming of functions, naming of variables.
  - https://peps.python.org/pep-0008/
  - https://docs.python-guide.org/writing/style/
  - https://guicommits.com/organize-python-code-like-a-pro/

- Port indicators to other distributions...
  - Pop!_OS
  - Solus
  - OpenSUSE
  - CentOS

- External hosting of source code
	- https://github.com/alexmurray/indicator-sensors
    - What about SourceForge?  Still uses SVN which is a good thing.


## License
This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license. 
Copyright 2012-2024 Bernard Giannetti.
