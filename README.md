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
1. To build a wheel for one or more indicators:

    `python3 tools/build_wheel.py release indicatortest`

    which creates a `.whl` and `.tar.gz` for `indicatortest` in `release/wheel/dist_indicatortest`.

2. Upload the wheel to `PyPI`:

    `python3 tools/upload_wheel.py release/wheel/dist_indicatortest`

    which (assumes the username \_\_token\_\_ and) prompts for the password (which starts with 'pypi-') and then uploads the `.whl` and `.tar.gz` to `PyPI`.

A directory called `venv` will be created and can be safely deleted or otherwise will be reused on the next build/upload.


## Release to TestPyPI and then Installing
For testing purposes, a wheel can be uploaded to `TestPyPI`:

```
    python3 tools/build_wheel.py release indicatortest
    python3 -m venv venv
    . /venv/bin/activate
    python3 -m pip install --upgrade twine
    python3 -m twine upload --username __token__ --repository testpypi release/wheel/dist_indicatortest
    deactivate
```

Because the dependencies (listed in `pyproject.toml`) will most likely be unavailable at `TestPyPI`, the install command is slightly modified:

```
    python3 -m venv $HOME/.local/venv_indicatortest
    . /$HOME/.local/venv_indicatortest/bin/activate
    python3 -m pip install --upgrade --force-reinstall --extra-index-url https://test.pypi.org/simple indicatortest
    deactivate
```


## Installing a Wheel Directly
A wheel can be installed directly:

```
    python3 -m venv $HOME/.local/venv_indicatortest && \
    . /$HOME/.local/venv_indicatortest/bin/activate && \
    python3 -m pip install --upgrade --force-reinstall release/wheel/dist_indicatortest/indicatortest-*-py3-none-any.whl && \
    deactivate
```


## Run an Indicator

```
    . /$HOME/.local/venv_indicatortest/bin/activate && \
    python3 $HOME/.local/venv_indicatortest/lib/python3.x/site-packages/indicatortest/indicatortest.py && \
    deactivate
```

noting the `x` in the second line which must be changed to match the version of `Python` in the `venv`.


## License
This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license.
Copyright 2012-2024 Bernard Giannetti.
