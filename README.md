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

    which will create a `.whl` and `.tar.gz` for `indicatortest` in `release/wheel/dist_indicatortest`. 

2. Upload the wheel to `PyPI`:

    `python3 tools/upload_wheel.py release/wheel/dist_indicatortest`

    which prompts for the username (\_\_token\_\_) and password (which starts with 'pypi-') and then uploads the `.whl` and `.tar.gz` to `PyPI`.


## Testing on TestPyPI
A wheel can be uploaded to `TestPyPI` for testing purposes:

```
    python3 utils/buildWheel.py release indicatortest
    python3 -m venv venv
    . /venv/bin/activate
    python3 -m pip install --upgrade twine
    python3 -m twine upload --username __token__ --repository testpypi dist_indicatortest/*
```

Because the dependencies, listed in `pyproject.toml`, will be unavailable at `TestPyPI`, need to adjust the install command:

```
    python3 -m venv venv
    . /venv/bin/activate
    python3 -m pip install --upgrade --force-reinstall --extra-index-url https://test.pypi.org/simple/ indicatortest
```


## Installing a Wheel Directly
A wheel can be installed directly for testing:

```
    python3 utils/buildWheel.py release indicatortest
    python3 -m venv venv
    . /venv/bin/activate
    python3 -m pip install --upgrade --force-reinstall release/wheel/indicatortest-*-py3-none-any.whl
    python3 venv/lib/python3.x/site-packages/indicatortest/indicatortest.py
```


## License
This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license. 
Copyright 2012-2024 Bernard Giannetti.
