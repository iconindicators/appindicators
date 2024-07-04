# AppIndicators for Ubuntu et al...


## Introduction
This project contains application indicators written in `Python3` for `Ubuntu 20.04` or equivalent as follows:
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

    which creates a `.whl` and `.tar.gz` for `indicatortest` in `release/wheel/dist_indicatortest`.  Multiple indicators may be specified and will be built sequentially:

    `python3 tools/build_wheel.py release indicatortest indicatorfortune indicatorlunar`


2. Upload the wheel to `PyPI`:

    `python3 tools/upload_wheel.py release/wheel/dist_indicatortest`

    which (assumes the username \_\_token\_\_ and) prompts for the password (which starts with 'pypi-') and uploads the `.whl` and `.tar.gz` to `PyPI`.

A directory called `venv` will be created and may be deleted, or otherwise will be reused on the next build/upload.


## Release to TestPyPI (and then Installing)
For testing purposes, a wheel may be uploaded to `TestPyPI`:

```
    python3 tools/build_wheel.py release indicatortest && \
    . ./venv/bin/activate && \
    python3 -m pip install --upgrade twine && \
    python3 -m twine upload --username __token__ --repository testpypi release/wheel/dist_indicatortest/* && \
    deactivate
```

As this is a compound command, only one indicator may be built and uploaded at a time. Replace `indicatortest` with the indicator to be build/uploaded.

Because the `Python` dependencies (listed in `pyproject.toml`) will be likely unavailable at `TestPyPI`, the install command is slightly modified:

```
    if [ ! -d $HOME/.local/venv_indicatortest ]; then python3 -m venv $HOME/.local/venv_indicatortest; fi && \
    . $HOME/.local/venv_indicatortest/bin/activate && \
    python3 -m pip install --upgrade --force-reinstall --extra-index-url https://test.pypi.org/simple indicatortest && \
    deactivate
```

You will likely need to also install various operating system packages; refer to the installation instructions for the given indicator at [https://pypi.org](https://pypi.org).


## Installing a Wheel Directly
Rather than install via `PyPI` or `TestPyPI`, you may install a wheel in the local file system:

```
    if [ ! -d $HOME/.local/venv_indicatortest ]; then python3 -m venv $HOME/.local/venv_indicatortest; fi && \
    . $HOME/.local/venv_indicatortest/bin/activate && \
    python3 -m pip install --upgrade --force-reinstall $(ls -d release/wheel/dist_indicatortest/indicatortest*.whl | head -1) && \
    deactivate
```

Copy icon, run script and desktop file to `$HOME/.local`:
```
    mkdir -p $HOME/.local/bin && \
    cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.sh $HOME/.local/bin && \
    mkdir -p $HOME/.local/share/applications && \
    cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.py.desktop $HOME/.local/share/applications && \
    mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps && \
    cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/icons/*.svg $HOME/.local/share/icons/hicolor/scalable/apps
```

You will likely need to also install various operating system packages; refer to the installation instructions for the given indicator at [https://pypi.org](https://pypi.org).

To install the wheel for multiple indicators, use the script:
```
    python3 tools/install_wheel.py release indicatortest indicatorfortune`.
```


## Run an Indicator

```
    . $HOME/.local/venv_indicatortest/bin/activate && \
    python3 $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/indicatortest.py && \
    deactivate
```


## Convert this Document from MD to HTML
```
    if [ ! -d venv ]; then python3 -m venv venv; fi && \
    . ./venv/bin/activate && \
    python3 -m pip install --upgrade readme_renderer readme_renderer[md] && \
    python3 -m readme_renderer README.md -o README.html && \
    deactivate
```


## License
This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license.

Copyright 2012-2024 Bernard Giannetti.
