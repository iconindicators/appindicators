# AppIndicators for Ubuntu et al...


## Introduction

This project contains application indicators written in `Python3` for `Ubuntu 20.04` or equivalent:
- `indicatorfortune` - [https://pypi.org/project/indicatorfortune](https://pypi.org/project/indicatorfortune)
- `indicatorlunar` - [https://pypi.org/project/indicatorlunar](https://pypi.org/project/indicatorlunar)
- `indicatoronthisday` - [https://pypi.org/project/indicatoronthisday](https://pypi.org/project/indicatoronthisday)
- `indicatorppadownloadstatistics` - [https://pypi.org/project/indicatorppadownloadstatistics](https://pypi.org/project/indicatorppadownloadstatistics)
- `indicatorpunycode` - [https://pypi.org/project/indicatorpunycode](https://pypi.org/project/indicatorpunycode)
- `indicatorscriptrunner` - [https://pypi.org/project/indicatorscriptrunner](https://pypi.org/project/indicatorscriptrunner)
- `indicatorstardate` - [https://pypi.org/project/indicatorstardate](https://pypi.org/project/indicatorstardate)
- `indicatortest` - [https://pypi.org/project/indicatortest](https://pypi.org/project/indicatortest)
- `indicatortide` - [https://pypi.org/project/indicatortide](https://pypi.org/project/indicatortide)
- `indicatorvirtualbox` - [https://pypi.org/project/indicatorvirtualbox](https://pypi.org/project/indicatorvirtualbox)

Each indicator shares the common code `indicatorbase`.


## Reminder

- `indicatorppadownloadstatistics` - requires updating approximately every six months with the latest `Ubuntu` series name.


## Run an Indicator (from Source)

To run `indicatortest` in a terminal at the source root:

```
    indicator=indicatortest && \
    if [ ! -d venv ]; then python3 -m venv venv; fi && \
    . venv/bin/activate && \
    python3 -m pip install PyGObject && \
    PYTHONPATH="indicatorbase/src/indicatorbase" python3 ${indicator}/src/${indicator}/${indicator}.py && \
    deactivate
```

Some indicators, such as `indicatorlunar`, require additional packages specified in the `dependencies` field of the respective `pyproject.toml`.  Include additional packages after `PyGObject` in the above command.


## Development Under Geany

Ensure `indicatortest` runs in a terminal from source as per the previous section.

Assuming the source code is located in `/home/bernard/Programming/Indicators`, create the project et al:
  
TODO See if $HOME can be used instead of /home/bernard

```
    Project > New
        Name: Indicators
        Filename: /home/bernard/Programming/Indicators/project.geany
        Basepath: /home/bernard/Programming/Indicators

    Build > Set Build Commands > Execute Commands
        Execute: /home/bernard/Programming/Indicators/venv/bin/python3 "%f"

    Edit > Preferences > Tools > Tool Paths > Terminal
        x-terminal-emulator -e "env PYTHONPATH=/home/bernard/Programming/Indicators/indicatorbase/src/indicatorbase /bin/sh %c"
```

`indicatortest` should now run under `Geany`.

References:

- [https://stackoverflow.com/questions/42013705/using-geany-with-python-virtual-environment](https://stackoverflow.com/questions/42013705/using-geany-with-python-virtual-environment)
- [https://stackoverflow.com/questions/23951042/append-new-pythonpath-permanently-in-geany-ide](https://stackoverflow.com/questions/23951042/append-new-pythonpath-permanently-in-geany-ide)


## Build a Wheel

To build a wheel for `indicatortest`:

```
    python3 tools/build_wheel.py release indicatortest
```

which updates locale files (`.pot` and `.po`) and creates a `.whl` / `.tar.gz` for `indicatortest` in `release/wheel/dist_indicatortest`. Additional indicators may be appended to the above command.


## Install a Wheel

To install the `.whl` for `indicatortest` located in `release/wheel/dist_indicatortest`:

```
    python3 tools/install_wheel.py release indicatortest
```

The `.whl` will be installed into a virtual environment at `$HOME/.local/venv_indicators`. Additional indicators may be appended.

Various operating system packages will likely need to be installed; refer to the installation instructions at the indicator's `PyPI` page listed in the *Introduction* above.


## Run an Indicator (installed to a Virtual Environment)

To run an indicator, open the applications menu (via the `Super` key) and select the indicator.  If this is the first time the indicator has been installed, you may have to log out/in for the indicator icon to appear in the list of applications.

To run from a terminal (so that any messages/errors may be observed):

```
    indicator=indicatortest && \
    venv=$HOME/.local/venv_indicators && \
    . ${venv}/bin/activate && \
    python3 $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/${indicator}.py && \
    deactivate
```

Alternatively to running in a terminal, edit `$HOME/.local/share/applications/indicatortest.py.desktop` and modify `Terminal=false` to `Terminal=true`. Run the indicator as normal from the applications menu and a terminal window should display.  If the terminal window does not display, refresh the `.desktop` by renaming to a bogus name and then rename back, or log out/in.


## Release to PyPI

To upload a `.whl` / `.tar.gz` for `indicatortest` to `PyPI`:

```
    indicator=indicatortest && \
    if [ ! -d venv ]; then python3 -m venv venv; fi && \
    . venv/bin/activate && \
    python3 -m pip install pip twine && \
    python3 -m twine upload --username __token__ release/wheel/dist_${indicator}/* && \
    deactivate
```

which assumes the username `__token__` and prompts for the password (starts with `pypi-`) and uploads the `.whl` / `.tar.gz` to `PyPI`.  Only one indicator may be uploaded at a time.

To install the indicator from `PyPI` (to a virtual environment in `$HOME/.local/venv_indicators`), refer to the indicator's `PyPI` page listed in the *Introduction* above.

References:
- [https://twine.readthedocs.io/en/latest](https://twine.readthedocs.io/en/latest)
- [https://packaging.python.org/en/latest/tutorials/packaging-projects](https://packaging.python.org/en/latest/tutorials/packaging-projects)


## Release to TestPyPI (and then Installing)

For testing purposes, a `.whl` / `.tar.gz` for `indicatortest` may be uploaded to `TestPyPI`:

```
    indicator=indicatortest && \
    if [ ! -d venv ]; then python3 -m venv venv; fi && \
    . venv/bin/activate && \
    python3 -m pip install pip twine && \
    python3 -m twine upload --username __token__ --repository testpypi release/wheel/dist_${indicator}/* && \
    deactivate
```

To install `indicatortest` from `TestPyPI` to a virtual environment in `$HOME/.local/venv_indicators`:

```
    indicator=indicatortest && \
    venv=$HOME/.local/venv_indicators && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install --force-reinstall --extra-index-url https://test.pypi.org/simple ${indicator} && \
    deactivate && \
    $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/install.sh
```

Additional operating system packages may be needed; refer to the installation instructions at the indicator's `PyPI` page listed in the *Introduction* above.


## Uninstall an Indicator

```
    python3 tools/uninstall_indicator.py indicatortest
```

Additional indicators may be appended to the above command.


## Convert this Document from MD to HTML

```
    if [ ! -d venv ]; then python3 -m venv venv; fi && \
    . venv/bin/activate && \
    python3 -m pip install readme_renderer[md] && \
    python3 -m readme_renderer README.md -o README.html && \
    deactivate
```

## License

This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license.

Copyright 2012-2024 Bernard Giannetti.
