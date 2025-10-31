## Introduction

This project produces the following `appindicators` for `Ubuntu 20.04` et al:
- `indicatorfortune`
- `indicatorlunar`
- `indicatoronthisday`
- `indicatorppadownloadstatistics`
- `indicatorpunycode`
- `indicatorscriptrunner`
- `indicatorstardate`
- `indicatortest`
- `indicatortide`
- `indicatorvirtualbox`

where each indicator is built upon `indicatorbase`.

Rather than have a project for each indicator, `indicatorbase` has
`pyprojectbase.toml` which covers the fields common to all indicators and each
indicator has its own `pyprojectspecific.toml` for variations.  When building a
`.whl`, `pyprojectbase.toml` and `pyprojectspecific.toml` are merged to create a
`pyproject.toml`.

Similarly for `MANIFESTbase.in` and `MANIFESTspecific.in`, if an indicator uses
a manifest.

Files such as `.desktop` and various `bash` scripts are common enough across all
indicators that they only need tags replaced during the build to create
specific versions for an indicator.

---

## Build an Indicator's Wheel

To build a wheel for `indicatortest`, at the root of the source tree:

```
  python3 -m tools.build_wheel tag indicatortest
```

which creates a virtual environment `venv_build`, updates locale files
`.pot` / `.po` and creates a `.whl` / `.tar.gz` for `indicatortest` in
`release/wheel/dist_indicatortest`.

Additional indicators may be appended to the above command.

The `tag` argument is the tag value (say 1.0) created at the time a release is
created on `GitHub`.  When building a wheel for testing/development purposes,
the tag value is irrelevant.  However, when building wheels for a release,
the tag value must match that of the intended release.

---

## Run an Indicator (from within the source tree)

**Prerequisite:** the indicator's `.whl` must be built.

**Prerequisite:** various operating system packages are needed.
For `indicatortest`, refer to the installation [instructions](https://github.com/iconindicators/appindicators),
choose `indicatortest` and for your distribution, install the specified packages.

To run `indicatortest`:

```
  python3 -m tools.run_indicator_from_source indicatortest
```

The virtual environment `venv_run` will be created.

If the indicator has not previously been installed to `$HOME/.local/venv_indicators`,
the icon and locale will be absent.

As part of running the indicator, a symbolic link to `indicatorbase.py` is
created for all indicators.  To remove:

```
  for dirs in indicator*; do \
  if [ -L $dirs/src/$dirs/indicatorbase.py ]; \
  then rm $dirs/src/$dirs/indicatorbase.py; fi ; \
  done;
```

---

## Install an Indicator's Wheel

**Prerequisite:** the indicator's `.whl` must be built.

**Prerequisite:** various operating system packages are needed.
For `indicatortest`, refer to the installation [instructions](https://github.com/iconindicators/appindicators),
choose `indicatortest` and for your distribution, install the specified packages.

To install a `.whl` for `indicatortest` located in
`release/wheel/dist_indicatortest`:

```
  python3 -m tools.install_wheel indicatortest
```

The `.whl` will be installed into a virtual environment at `$HOME/.local/venv_indicators`.

Additional indicators may be appended to the above command.

---

## Run an Installed Indicator

**Prerequisite:** the indicator's `.whl` must be built and installed.

**Prerequisite:** various operating system packages are needed.
For `indicatortest`, refer to the installation [instructions](https://github.com/iconindicators/appindicators),
choose `indicatortest` and for your distribution, install the specified packages.

To run an indicator, open the applications menu (via the `Super` key) and
select the indicator.  If this is the first time the indicator has been
installed, you may have to log out/in for the indicator icon to appear in the
list of applications.

To run from a terminal (to observe any messages/errors) from any directory:

```
  . $HOME/.local/bin/indicatortest.sh
```

Alternatively to running in a terminal, edit `$HOME/.local/share/applications/indicatortest.py.desktop`
and change `Terminal=false` to `Terminal=true`. Run the indicator as normal
from the applications menu and a terminal window should display.  If the
terminal window does not display, refresh the `.desktop` by renaming to a bogus
name and then rename back, or log out/in.

---

## Release to GitHub

**Prerequisite:** ALL indicators' `.whl` / `.tar.gz` must be built with the
corresponing release `tag` from `GitHub`.

On `GitHub` create a new release with version tag and upload the `.whl` and
`.tar.gz` for **all** indicators.

---

## Uninstall an Indicator

```
    python3 -m tools.uninstall_indicator indicatortest
```

Additional indicators may be appended to the above command.

Note that any operating system packages installed for the indicator(s) will
still be present.

---

## Updating README.md

There are two types of `README.md`:
1. The `README.md` for the `GitHub` main landing page.
1. A `README.md` for each indicator, containing specific installation
instructions.

The `GitHub` main `README.md` is updated as needed, for example, if an
indicator's comment is changed.  To update the main `README.md` run:

```
  python3 -m tools.build_readme
```

Each indicator's `GitHub` `README.md` is rebuilt as part of the `build_wheel`
process described earlier.

Any time any `README.md` is altered it must be committed.

---

## Pylint

To run `Pylint` over the entire project:

```
  python3 -m tools.pylint
```

Several checks have been disabled; re-enable by editing the script.

---

## Development under Geany

**Prerequisite:** the indicator's `.whl` must be built and run within the
source tree.

**Geany Setup**

Run `Geany` then:

```
  Build > Set Build Commands > Execute Commands
    Execute: cd /home/bernard/Programming/Indicators/%e/src ; /home/bernard/Programming/Indicators/venv_run/bin/python3 -m "%e.%e"
```

NOTE: Because of `%e` variable above, running any of the `tools` is not
possible, nor any other non-indicator code, such as `example.py` in
`indicatorstardate`.

**Project Setup**

```
  Project > New
    Name: Indicators
    Filename: /home/bernard/Programming/Indicators/project.geany
    Basepath: /home/bernard/Programming/Indicators
```

The indicator should now run via `Build > Execute` or `F5`.

NOTE: If editing `README.md` or any `markdown` document under `Geany`, using
two spaces to insert an empty line may not work as `Geany` removes trailing
spaces by default.

References:

- [https://stackoverflow.com/questions/42013705/using-geany-with-python-virtual-environment](https://stackoverflow.com/questions/42013705/using-geany-with-python-virtual-environment)
- [https://stackoverflow.com/questions/23951042/append-new-pythonpath-permanently-in-geany-ide](https://stackoverflow.com/questions/23951042/append-new-pythonpath-permanently-in-geany-ide)

---

## Development under Eclipse

**Prerequisite:** the indicator's `.whl` must be built and run within the
source tree.

**Eclipse Setup**

Run `Eclipse` and install [Liclipse](https://www.liclipse.com/) via the update
site.

Create a `Python` interpreter which uses `venv_run`:

```
  Window > Preferences
    PyDev > Interpreters > Python Interpreter
      New > Browse for python/pypy exe
        Browse to venv_run/bin/python3
        Interpreter Name: python3 venv_run
        Check site-packages within venv_run

    PyDev > Run
      Check Launch modules with 'python -m mod.name'
```

**Project Setup**

```
  File > New > PyDev Project
    Project Name: Indicators
    Use default: Uncheck
    Directory: /home/bernard/Programming/Indicators
    Interpreter Name: python3 venv_run
    Finish
```

**Run Indicator**

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

**Run Tool**

Under `Run Configurations...` for the tool, ensure that `Working Directory` is
set to `Default` and the `Python` interpreter is set to `python3`.

References:

- [https://www.pydev.org/manual_101_interpreter.html](https://www.pydev.org/manual_101_interpreter.html)

---

## Convert this Document from MD to HTML

```
  python3 -m tools.markdown_to_html CONTRIBUTING.md
```

Any `markdown` document may be converted to `html` using the same script.

---

## Migraton from Subversion

Documentation of the process used to bring the legacy `Subversion` repository
into `GitHub`.

Check out a working copy of the `Subversion` repository and verify list of
authors (should only be `bernard =`):

```
  cd <svn working copy of indicators>
  svn log --xml --quiet | grep author | sort -u | perl -pe 's/.*>(.*?)<.*/$1 = /'

    bernard = 
```

Create `users.txt` to match the list of authors:

```
  echo "bernard = Bernard Giannetti <thebernmeister@hotmail.com>" > users.txt
```

Convert `Subversion` repository (at internal IP address) to a `Git` repository
(note there is no `trunk`, `branches`, `tags`):

```
  cd ..
  git svn clone http://192.168.1.102/indicators \
    --authors-file=users.txt \
    --no-metadata \
    --prefix "" \
    indicatorsgit
```

Clone the main repository from `GitHub`:

```
  git clone https://github.com/iconindicators/appindicators appindicatorsgithub
```

Insert the converted `Git` repository from above to the clone (roundabout way as
`git subtree` does not allow adding to the root), then push back up to `GitHub`:

```
cd appindicatorsgithub
git remote add indicatorsgit $(pwd)/../indicatorsgit/.git
git subtree add -P temp indicatorsgit HEAD
git mv -f temp/* .
git add .
git commit -m "Moved files from temp to root."
rm -r temp
git push origin main
```

References
- [https://git-scm.com/book/ms/v2/Git-and-Other-Systems-Migrating-to-Git](https://git-scm.com/book/ms/v2/Git-and-Other-Systems-Migrating-to-Git)

---

## Useful Links

- [https://markdownlivepreview.com](https://markdownlivepreview.com)
- [https://dillinger.io](https://dillinger.io)
