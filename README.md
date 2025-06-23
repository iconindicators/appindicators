# AppIndicators for Ubuntu et al...


### Introduction

This project contains application indicators written in `Python3` for `Ubuntu 20.04` or similar:
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

Each indicator shares the common code `indicatorbase` and `shared`.


### Build a Wheel

To build a wheel for `indicatortest` from the root of the source tree:

```
    python3 -m tools.build_wheel indicatortest
```

which creates a virtual environment `venv_build`, updates locale files `.pot` / `.po` and creates a `.whl` / `.tar.gz` for `indicatortest` in `release/wheel/dist_indicatortest`. Additional indicators may be appended to the above command.


### Install a Wheel

To install a `.whl` for `indicatortest` located in `release/wheel/dist_indicatortest`:

```
    python3 -m tools.install_wheel indicatortest
```

The `.whl` will be installed into a virtual environment at `$HOME/.local/venv_indicators`. Additional indicators may be appended to the above command.

Various operating system packages will likely need to be installed; refer to the installation instructions at the indicator's `PyPI` page listed in the introduction above.


### Run an Indicator (from within the source tree)

Prerequisite: the indicator's `.whl` must be built as above.

To run a `indicatortest`:

```
    python3 -m tools.run_indicator_from_source indicatortest
```

A virtual environment will be created at `venv_run`. Additional indicators may be appended to the above command.

Various operating system packages will likely need to be installed; refer to the installation instructions at the indicator's `PyPI` page listed in the introduction above.

As part of running the indicator, a symbolic link to `indicatorbase.py` and `shared.py` is created for all indicators.

If the indicator has not previously been installed to `$HOME/.local/venv_indicators`, the icon and locale will be absent.

To remove all the symbolic links to `indicatorbase.py` and `shared.py`:

```
	for dirs in indicator*; \
	do if [ -L $dirs/src/$dirs/indicatorbase.py ]; \
	then rm $dirs/src/$dirs/indicatorbase.py; fi ; done && \
	for dirs in indicator*; \
	do if [ -L $dirs/src/$dirs/shared.py ]; \
	then rm $dirs/src/$dirs/shared.py; fi ; done;
```

### Development under Geany

#### Geany Setup

Ensure `indicatortest` runs in a terminal within the source tree as per the earlier section and `venv_run` exists.

Run `Geany`:

```
    Build > Set Build Commands > Execute Commands
        Execute: cd /home/bernard/Programming/Indicators/%e/src ; /home/bernard/Programming/Indicators/venv_run/bin/python3 -m "%e.%e"
```

#### Project Setup

```
    Project > New
        Name: Indicators
        Filename: /home/bernard/Programming/Indicators/project.geany
        Basepath: /home/bernard/Programming/Indicators
```

The indicator should now run via `Build > Execute` or `F5`.

NOTE: If editing `README.md` or any `markdown` document under `Geany`, using two spaces to insert an empty line may not work as `Geany` removes trailing spaces by default.

NOTE: May be possible to run the `tools` scripts within `Geany`; however this has not been investigated.

References:

- [https://stackoverflow.com/questions/42013705/using-geany-with-python-virtual-environment](https://stackoverflow.com/questions/42013705/using-geany-with-python-virtual-environment)
- [https://stackoverflow.com/questions/23951042/append-new-pythonpath-permanently-in-geany-ide](https://stackoverflow.com/questions/23951042/append-new-pythonpath-permanently-in-geany-ide)


### Development under Eclipse

#### Eclipse Setup

Ensure `indicatortest` runs in a terminal within the source tree as per the earlier section and `venv_run` exists.

Run `Eclipse` and install [Liclipse](https://www.liclipse.com/) via the update site.

Create a `Python` interpreter which uses `venv_run`:

```
    Window > Preferences
        PyDev > Python Interpreter
            New > Browse for python/pypy exe
                Browse to venv_run/bin/python3
                Interpreter Name: python3 venv_run
                Check site-packages within venv_run

        PyDev > Run
            Check Launch modules with 'python -m mod.name'
```

#### Project Setup

```
    File > New > PyDev Project
        Project Name: Indicators
        Use default: Uncheck
        Directory: /home/bernard/Programming/Indicators
        Interpreter Name: python3 venv_run
        Finish
```

#### Run Indicator

```
    Right click on indicatortest.py
        Run As > Python Run
```

which should fail, then:

```
    Run > Run Configurations
        Python Run: Indicators.indicatortest
            Arguments
                Working Directory:
                    Other: ${workspace_loc:Indicators/indicatortest/src}
            Interpreter
                Interpreter: python3 venv_run
```

Repeat for each indicator, or as each indicator is run.

#### Run Tool

Ensure a `.whl` for `indicatortest` is built as per the earlier section on building a wheel and `venv_build` exists.

Create a `Python` interpreter similarly to above which uses `venv_build`:

TODO utils.initialise_virtual_environment no longer exists, so check the line below...

If `utils.initialise_virtual_environment` will be called by the tool, temporarily comment out the call.

Under `Run Configuration` for the tool, ensure that `Working Directory` is set to `Default` and the `Python` interpreter is set to `venv_build`.

References:

- [https://www.pydev.org/manual_101_interpreter.html](https://www.pydev.org/manual_101_interpreter.html)


### Run an Installed Indicator

To run an indicator, open the applications menu (via the `Super` key) and select the indicator.  If this is the first time the indicator has been installed, you may have to log out/in for the indicator icon to appear in the list of applications.

To run from a terminal (to observe any messages/errors) from any directory:

```
    . $HOME/.local/bin/indicatortest.sh
```

Alternatively to running in a terminal, edit `$HOME/.local/share/applications/indicatortest.py.desktop` and change `Terminal=false` to `Terminal=true`. Run the indicator as normal from the applications menu and a terminal window should display.  If the terminal window does not display, refresh the `.desktop` by renaming to a bogus name and then rename back, or log out/in.


### Release to PyPI

TODO
	Test
	Maybe have a release_wheel.py which takes a flag for PyPI or TestPyPI?

To upload a `.whl` / `.tar.gz` for `indicatortest` to `PyPI`:

```
    indicator=indicatortest && \
    venv=venv_build && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install pip twine && \
    python3 -m twine upload --username __token__ release/wheel/dist_${indicator}/* && \
    deactivate
```

which assumes the username `__token__` and prompts for the password (starts with `pypi-`) and uploads the `.whl` / `.tar.gz` to `PyPI`.  Only one indicator may be uploaded at a time.

References:
- [https://twine.readthedocs.io/en/latest](https://twine.readthedocs.io/en/latest)


### Install from PyPI

To install the indicator from `PyPI` to a virtual environment in `$HOME/.local/venv_indicators`, refer to the indicator's `PyPI` page listed in the introduction.


### Release to TestPyPI

TODO
	Test
	Maybe have a release_wheel.py which takes a flag for PyPI or TestPyPI?

For testing purposes, a `.whl` / `.tar.gz` for `indicatortest` may be uploaded to `TestPyPI`:

```
    indicator=indicatortest && \
    venv=venv_build && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install pip twine && \
    python3 -m twine upload --username __token__ --repository testpypi release/wheel/dist_${indicator}/* && \
    deactivate
```


### Install from TestPyPI

TODO
	Test

To install `indicatortest` from `TestPyPI` to a virtual environment in `$HOME/.local/venv_indicators`,
first, install the operating system packages listed at the indicator's `PyPI` page listed in the Introduction.

Then install `indicatortest`:

TODO
	Should I have --upgrade after install?
	See similar note in utils_readme.py
	Should this be put into a script...and combine with install from PyPI but with a switch?
```
    indicator=indicatortest && \
    venv=$HOME/.local/venv_indicators && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install --force-reinstall --extra-index-url https://test.pypi.org/simple ${indicator} && \
    deactivate && \
    $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/install.sh
```


### Uninstall an Indicator

```
    python3 -m tools.uninstall_indicator indicatortest
```

Additional indicators may be appended to the above command.


### Pylint

In a terminal, one directory **above** the source tree root (assumed to the directory `Indicators`):

```
    pylint \
    --recursive=y \
    --ignore=release,venv_build,venv_run \
    Indicators \
    --output=pylint.txt ; \
    sort --output=pylint.txt -t ":" --key=4,4 --key=1,1 --key=2,2n pylint.txt
```

As above, but with several checks disabled:

```
    pylint \
    --disable=line-too-long \
    --disable=missing-function-docstring \
    --disable=too-many-lines \
    --disable=wrong-import-position \
    --disable=import-error \
    --disable=undefined-variable \
    --disable=no-name-in-module \
    --disable=no-member \
    --disable=too-many-instance-attributes \
    --disable=too-many-branches \
    --disable=too-many-arguments \
    --disable=too-many-locals \
    --disable=too-many-statements \
    --disable=too-many-boolean-expressions \
    --disable=too-many-nested-blocks \
    --disable=attribute-defined-outside-init \
    --disable=unused-argument \
    --disable=f-string-without-interpolation \
    --disable=too-few-public-methods \
    --disable=too-many-public-methods \
    --disable=unused-variable \
    --disable=fixme \
    --recursive=y \
    --ignore=release,venv_build,venv_run \
    Indicators \
    --output=pylint.txt ; \
    sort --output=pylint.txt -t ":" --key=4,4 --key=1,1 --key=2,2n pylint.txt
```


### Convert this Document from MD to HTML

```
    python3 -m tools.markdown_to_html
```


### License

This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license.

Copyright 2012-2025 Bernard Giannetti.
