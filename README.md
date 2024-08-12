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

To install the indicator, refer to installation instructions at the indicator's `PyPI` page in the *Introduction*.

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

Various operating system packages will likely need to be installed; refer to installation instructions at the indicator's `PyPI` page in the *Introduction*.


## Installing a Wheel Directly

A wheel may be installed from the local file system.  For `indicatortest`, the `.whl` is assumed to be in `release/wheel/dist_indicatortest` and will be installed into a virtual environment at `$HOME/.local/venv_indicatortest`.

```
    python3 tools/install_indicator_from_wheel.py release indicatortest
```

Additional indicators may be appended.

Various operating system packages will likely need to be installed; refer to installation instructions at the indicator's `PyPI` page in the *Introduction*.


## Run an Indicator

To run the indicator, open the applications menu (via the `Super` / `Windows` key) and select the indicator.  If this is the first time the indicator has been installed, you may have to log out and log in.

To run from a terminal (so that any errors or messages may be observed):

```
    . $HOME/.local/venv_indicatortest/bin/activate && \
    python3 $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/indicatortest.py && \
    deactivate
```

Alternatively to running in a terminal, edit `$HOME/.local/share/applications/indicatortest.py.desktop` such that `Terminal=false` is changed to `Terminal=true` and then log out and log in.  Run the indicator as normal from the applications menu and a terminal window should display.


## Uninstall an Indicator

```
    python3 tools/uninstall_indicator.py indicatortest
```

Additional indicators may be appended to the above command.


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
