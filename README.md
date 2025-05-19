# AppIndicators for Ubuntu et al...


## Introduction

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

Each indicator shares the common code `indicatorbase`.


## Build a Wheel

To build a wheel for `indicatortest` in the root of the source tree:

```
    python3 -m tools.build_wheel release indicatortest
```

which creates a virtual environment `venv_build`, updates locale files `.pot` / `.po` and creates a `.whl` / `.tar.gz` for `indicatortest` in `release/wheel/dist_indicatortest`. Additional indicators may be appended to the above command.


## Run an Indicator (within the source tree)

To run an indicator within the source tree, the indicator's `.whl` must first be built as above.

Next, create a symbolic link to `indicatorbase.py` via the terminal, from the source tree root:

```
    for dirs in indicator*; do if [ ! -f $dirs/src/$dirs/indicatorbase.py ]; then ln -sr indicatorbase/src/indicatorbase/indicatorbase.py $dirs/src/$dirs/indicatorbase.py; fi ; done;
```

which will create a symbolic link to `indicatorbase.py` for all the indicators.

To run `indicatortest` from the source tree root:

```
    indicator=indicatortest && \
    venv=venv_run && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
#TODO Why is PyGObject here?
    python3 -m pip install packaging PyGObject\<=3.50.0 && \
    cd ${indicator}/src && \
    python3 -m ${indicator}.${indicator} && \
    deactivate && \
    cd ../..
```

THIS assumes that the indicator is already installed in .local because the icons/locale/etc will be present.


if cat /etc/os-release | grep -q 'ID=ubuntu'; then
  echo "matched"
fi




pygobject="PyGObject"
etc_os_release="$(cat /etc/os-release)"
if echo "$etc_os_release" | grep -q 'ID=ubuntu'; then
  echo "matched ID=ubuntu"
  
  if echo "$etc_os_release" | grep -q 'VERSION_ID=\"20.04\"'; then
    echo "matched VERSION_ID=\"20.04\""
    pygobject="PyGObject\<=3.50.0"
  fi
else
  echo "no match"
fi
echo $pygobject




pygobject="PyGObject"
etc_os_release="$(cat /etc/os-release)"
if echo "$etc_os_release" | grep -q 'ID=debian'; then
  if echo "$etc_os_release" | grep -q 'VERSION_ID=\"12\"'; then
    pygobject="PyGObject\<=3.50.0"
  fi
fi
echo $pygobject



pygobject="PyGObject"
etc_os_release="$(cat /etc/os-release)"
if echo "$etc_os_release" | grep -q 'ID=debian'; then
  if echo "$etc_os_release" | grep -q 'VERSION_ID=\"12\"'; then
    pygobject="PyGObject\<=3.50.0"
  fi
fi
echo $pygobject





pygobject="PyGObject" && \
etc_os_release="$(cat /etc/os-release)" && \
if [ "$(echo "$etc_os_release" | grep 'ID=debian')" == "ID=debian" ] && [ "$(echo "$etc_os_release" | grep 'ID=debian')" == "ID=debian" ]; then pygobject="debian"; fi && \
echo $pygobject



XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

pygobject="PyGObject" && \
etc_os_release="$(cat /etc/os-release)" && \
if [ "$(echo "$etc_os_release" | grep 'ID=debian')" == "ID=debian" ] && [ "$(echo "$etc_os_release" | grep 'VERSION_ID=\"12\"')" == "VERSION_ID=\"12\"" ]; then pygobject="debian"; fi && \
echo $pygobject


XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


pygobject="PyGObject" && \
etc_os_release="$(cat /etc/os-release)" && \
if [ "$(echo "$etc_os_release" | grep 'ID=debian')" == "ID=debian" ]; then pygobject="debian"; fi && \
echo $pygobject







pygobject="abc" && \
etc_os_release="$(cat /etc/os-release)" && \
if echo "$etc_os_release" | grep -q 'ID=ubuntu'; then && \
  if echo "$etc_os_release" | grep -q 'VERSION_ID=\"20.04\"'; then && \
    pygobject="def" && \
  fi && \
fi && \
echo $pygobject





VERSION_ID="20.04"


etc_os_release="$(cat /etc/os-release)"
if [ echo "$etc_os_release" | grep -q 'ID=ubuntu' ] && [ echo "$etc_os_release" | grep -q 'ID_LIKE=debian' ]; then
  echo "matched"
else
  echo "no match"
fi




if [ $STATUS -ne 200 ] -a [[ "$STRING" != "$VALUE" ]];


etc_os_release="$(cat /etc/os-release)"

result="$($etc_os_release | grep -q 'ID=ubuntu')"


echo $etc_os_release

echo result

OUTPUT="$(ls -1)"

 | grep -q 'ID=ubuntu' ] && [ cat /etc/os-release | grep -q 'ID=ubuntu' ]; then
  echo "matched"
fi

if [ cat /etc/os-release | grep -q 'ID=ubuntu' ] && [ cat /etc/os-release | grep -q 'ID=ubuntu' ]; then
  echo "matched"
fi


indicator=indicatortest && \
venv=venv_run && \
if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
. ${venv}/bin/activate && \
python3 -m pip install packaging PyGObject && \
cd ${indicator}/src && \
python3 -m ${indicator}.${indicator} && \
deactivate && \
cd ../..


TODO Check below
TODO Also mention the icon will not display unless installed in .local

Running the indicator from source is done in the same way when run from installed to reproduce the same conditions/environment.

The above command is for `Debian 11/12` or `Ubuntu 20.04/22.04`, which uses `libgirepository1.0-dev` and only works with `PyGObject` version `3.50.0` or below. For `Ubuntu 24.04+` or `Debian 13+`, which use `libgirepository-2.0`, remove the version restriction on `PyGObject`.

Some indicators, such as `indicatorlunar`, require additional packages, specified in the `dependencies` field of `pyproject.toml`.  Include those additional packages in the `pip install` above.


## Development under Geany

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


## Development under Eclipse

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

If `utils.initialise_virtual_environment` will be called by the tool, temporarily comment out the call.

Under `Run Configuration` for the tool, ensure that `Working Directory` is set to `Default` and the `Python` interpreter is set to `venv_build`.

References:

- [https://www.pydev.org/manual_101_interpreter.html](https://www.pydev.org/manual_101_interpreter.html)


## Install a Wheel

To install a `.whl` for `indicatortest` located in `release/wheel/dist_indicatortest` at the source tree root:

```
    python3 -m tools.install_wheel release indicatortest
```

The `.whl` will be installed into a virtual environment at `$HOME/.local/venv_indicators`. Additional indicators may be appended.

Various operating system packages will likely need to be installed; refer to the installation instructions at the indicator's `PyPI` page listed in the introduction above.


## Run an Installed Indicator

To run an indicator, open the applications menu (via the `Super` key) and select the indicator.  If this is the first time the indicator has been installed, you may have to log out/in for the indicator icon to appear in the list of applications.

To run from a terminal (observe any messages/errors) from any directory:

```
    indicator=indicatortest && \
    venv=$HOME/.local/venv_indicators && \
    . ${venv}/bin/activate && \
    cd $(ls -d ${venv}/lib/python3.* | head -1)/site-packages && \
    python3 -m ${indicator}.${indicator} && \
    deactivate
```

Alternatively to running in a terminal, edit `$HOME/.local/share/applications/indicatortest.py.desktop` and change `Terminal=false` to `Terminal=true`. Run the indicator as normal from the applications menu and a terminal window should display.  If the terminal window does not display, refresh the `.desktop` by renaming to a bogus name and then rename back, or log out/in.


## Release to PyPI

TODO Check this section

To upload a `.whl` / `.tar.gz` for `indicatortest` to `PyPI`, in a terminal at the source tree root:

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
- [https://packaging.python.org/en/latest/tutorials/packaging-projects](https://packaging.python.org/en/latest/tutorials/packaging-projects)


## Install from PyPI

TODO Check this section

To install the indicator from `PyPI` to a virtual environment in `$HOME/.local/venv_indicators`, refer to the indicator's `PyPI` page listed in the introduction.


## Release to TestPyPI

TODO Check this section

For testing purposes, a `.whl` / `.tar.gz` for `indicatortest` may be uploaded to `TestPyPI`.  In a terminal at the source tree root:

```
    indicator=indicatortest && \
    venv=venv_build && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install pip twine && \
    python3 -m twine upload --username __token__ --repository testpypi release/wheel/dist_${indicator}/* && \
    deactivate
```


## Install from TestPyPI

TODO Check this section

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

Additional operating system packages may be needed; refer to the installation instructions at the indicator's `PyPI` page listed in the Introduction.


## Uninstall an Indicator

TODO Check this section

In a terminal at the source tree root:

```
    python3 -m tools.uninstall_indicator indicatortest
```

Additional indicators may be appended to the above command.


## Remove all Symbolic Links to indicatorbase.py

In a terminal from the source tree root:

```
    for dirs in indicator*; do if [ -L $dirs/src/$dirs/indicatorbase.py ]; then rm $dirs/src/$dirs/indicatorbase.py; fi ; done;
```


## Pylint

In a terminal, one directory above source tree root (assumed to the directory `Indicators`):

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


## Convert this Document from MD to HTML

In a terminal at the source tree root:

 ```
    venv=venv_build && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install readme_renderer[md] && \
    python3 -m readme_renderer README.md -o README.html && \
    deactivate
```


## License

This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license.

Copyright 2012-2025 Bernard Giannetti.
