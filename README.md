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

Each indicator shares the common code base `indicatorbase`.


## Reminder

- `indicatorppadownloadstatistics` - requires updating approximately every six months with the latest `Ubuntu` series name.


## Release Procedure

A release involves building a `Python` wheel and uploading to `PyPI`.
1. To build a wheel for `indicatortest`:

    `python3 tools/build_wheel.py release indicatortest`

    which updates locale files (`.pot` and `.po`), creates a `.whl` and `.tar.gz` for `indicatortest` in `release/wheel/dist_indicatortest`. Additional indicators may be appended to the above command.


2. Upload the wheel to `PyPI`:

    ```
    if [ ! -d venv ]; then python3 -m venv venv; fi && \
    . ./venv/bin/activate && \
    python3 -m pip install --upgrade pip twine && \
    python3 -m twine upload --username __token__ release/wheel/dist_indicatortest/* && \
    deactivate
    ```

    which assumes the username `__token__` and prompts for the password (starts with `pypi-`) and uploads the `.whl` and `.tar.gz` to `PyPI`.  Only one indicator may be uploaded at a time.

The build/upload creates a virtual environment in `venv` which may be deleted afterwards; otherwise, the virtual environment will be reused on subsequent builds/uploads.

To install the indicator, refer to the installation instructions at the indicator's `PyPI` page listed in the *Introduction* above.

References:
- [https://twine.readthedocs.io/en/latest](https://twine.readthedocs.io/en/latest)
- [https://packaging.python.org/en/latest/tutorials/packaging-projects](https://packaging.python.org/en/latest/tutorials/packaging-projects)


## Release to TestPyPI (and then Installing)

For testing purposes, a wheel for `indicatortest` may be uploaded to `TestPyPI`:

```
    if [ ! -d venv ]; then python3 -m venv venv; fi && \
    . ./venv/bin/activate && \
    python3 -m pip install --upgrade pip twine && \
    python3 -m twine upload --username __token__ --repository testpypi release/wheel/dist_indicatortest/* && \
    deactivate
```

To install `indicatortest` from `TestPyPI` to a virtual environment in `$HOME/.local/venv_indicatortest`:

```
    if [ ! -d $HOME/.local/venv_indicatortest ]; then python3 -m venv $HOME/.local/venv_indicatortest; fi && \
    . $HOME/.local/venv_indicatortest/bin/activate && \
    python3 -m pip install --upgrade --force-reinstall --extra-index-url https://test.pypi.org/simple indicatortest && \
    deactivate && \
    $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/post_install.sh
```

Various operating system packages will likely need to be installed; refer to the installation instructions at the indicator's `PyPI` page listed in the *Introduction* above.


## Installing a Wheel Directly

A wheel may be installed from the local file system.  For `indicatortest`, the `.whl` is assumed to be in `release/wheel/dist_indicatortest` and will be installed into a virtual environment at `$HOME/.local/venv_indicatortest`.

```
    python3 tools/install_wheel.py release indicatortest
```

Additional indicators may be appended.

Various operating system packages will likely need to be installed; refer to the installation instructions at the indicator's `PyPI` page listed in the *Introduction* above.


## Run an Indicator (Installed to a Virtual Environment)

To run the indicator, open the applications menu (via the `Super` key) and select the indicator.  If this is the first time the indicator has been installed, you may have to log out/in for the indicator icon to appear in the list of applications.

To run from a terminal (so that any messages/errors may be observed):

```
    . $HOME/.local/venv_indicatortest/bin/activate && \
    python3 $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/indicatortest.py && \
    deactivate
```

Alternatively to running in a terminal, edit `$HOME/.local/share/applications/indicatortest.py.desktop` and modify `Terminal=false` to `Terminal=true`. Run the indicator as normal from the applications menu and a terminal window should display.  If the terminal window does not display, refresh the `.desktop` by renaming to a bogus name and then rename back, or log out/in.


#TOOO I suspect this needs to change somewhat...
# I don't think indicatorlunar (which requires ephem) will work
# unless a venv is created first and ephem et al are installed.
# In Ubuntu 20.04 indicatorlunar runs under Eclipse because ephem is installed as an OS package.
# But in Debian 12 (and presumably Ubuntu 24.04) must use a venv...
# ...so need to figure out how to run
# ......via a terminal, need to copy Python file being edited to the venv?
# ......via an IDE, I guess need to tell the IDE about the venv...then what?
https://stackoverflow.com/questions/42013705/using-geany-with-python-virtual-environment
https://lists.geany.org/hyperkitty/list/users@lists.geany.org/thread/MHKCINVA3ZGSQNE5EV2QWSVUT7ZB35TF/
#
# For indicatorlunar
# In the terminal at the project root,
# create a venv (python3 -m venv) which should already be present after a build,
# then install dependencies
#      python3 -m pip install ephem requests sgp4
# then can run the indicator using development files in place using the command below as normal.
# For all other indicators, no need for the venv, just run in place.
#
#Under Geany,
# https://stackoverflow.com/a/26366357/2156453
# In short, Edit - Preferences - Tools - Terminal
# prepend
#    env PYTHONPATH=/home/bernard/Programming/Indicators/indicatorbase/src/indicatorbase
# to the /bin/sh
#
# x-terminal-emulator -e "/bin/sh %c"
#
# x-terminal-emulator -e "env PYTHONPATH=/home/bernard/Programming/Indicators/indicatorbase/src/indicatorbase /bin/sh %c"
#


## Run an Indicator (Within the Development Environment)



To run the indicator from an Integrated Development Environment (IDE) such as `Eclipse`, the IDE should take care of all paths et cetera.

To run the indicator from a terminal, ensure you are in the directory at the root of the project and:

```
    PYTHONPATH="indicatorbase/src/indicatorbase" python3 indicatortest/src/indicatortest/indicatortest.py
```

## ORIGINAL Run an Indicator (Within the Development Environment)

To run the indicator from an Integrated Development Environment (IDE) such as `Eclipse`, the IDE should take care of all paths et cetera.

To run the indicator from a terminal, ensure you are in the directory at the root of the project and:

```
    PYTHONPATH="indicatorbase/src/indicatorbase" python3 indicatortest/src/indicatortest/indicatortest.py
```

## Uninstall an Indicator

```
    python3 tools/uninstall_indicator.py indicatortest
```

Additional indicators may be appended to the above command.


## Convert this Document from MD to HTML

```
    if [ ! -d venv ]; then python3 -m venv venv; fi && \
    . ./venv/bin/activate && \
    python3 -m pip install --upgrade readme_renderer[md] && \
    python3 -m readme_renderer README.md -o README.html && \
    deactivate
```

## License

This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license.

Copyright 2012-2024 Bernard Giannetti.
