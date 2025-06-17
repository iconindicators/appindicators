# Immediate

## No autostart on Kubuntu and Manjaro
Given there is no autostart on Kubuntu 24.04 and Manjaro 24.04.7,
should the autostart checkbox and delay spinner be hidden?
If some fix through an OS update appears in the meantime,
will need to release ALL indicators again unhiding checkbox and spinner.
Could have a tooltip...but if the fix comes, don't need to re-release but should.
Otherwise just leave as is...and keep the entry in the changelog.
What to do?


## Update date in CHANGELOG.md
For each indicator's CHANGELOG.md, at release time, update the release date in
the latest entry to the date of release.


## When indicatortest is released
Post a note to
  https://github.com/AyatanaIndicators/libayatana-appindicator/issues/76
to help the guy out.


## Update the PPA description at
  https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa
with the following:

This PPA no longer provides releases for indicators.
Instead, for Ubuntu 20.04 and forward, all releases are made via pip (PyPI).

Refer to the new URL for each indicator:

indicator-fortune: https://pypi.org/project/indicatorfortune
indicator-lunar: https://pypi.org/project/indicatorlunar
indicator-on-this-day: https://pypi.org/project/indicatoronthisday
indicator-ppa-download-statistics: https://pypi.org/project/indicatorppadownloadstatistics
indicator-punycode: https://pypi.org/project/indicatorpunycode
indicator-script-runner: https://pypi.org/project/indicatorscriptrunner
indicator-stardate: https://pypi.org/project/indicatorstardate
indicator-test: https://pypi.org/project/indicatortest
indicator-tide: https://pypi.org/project/indicatortide
indicator-virtual-box: https://pypi.org/project/indicatorvirtualbox

Screenshots for the indicators can be found at https://askubuntu.com/q/30334/67335


## For each indicator at
  https://askubuntu.com/questions/30334/what-application-indicators-are-available?answertab=modifieddes
update the URL at the top with the relevant URL at PyPI.

Also update the indicator name (remove the hyphen from the name).

  https://pypi.org/project/indicatorfortune/
  https://pypi.org/project/indicatorlunar/
  https://pypi.org/project/indicatoronthisday/
  https://pypi.org/project/indicatorppadownloadstatistics/
  https://pypi.org/project/indicatorpunycode/
  https://pypi.org/project/indicatorscriptrunner/
  https://pypi.org/project/indicatorstardate/
  https://pypi.org/project/indicatortide/
  https://pypi.org/project/indicatorvirtualbox/


When indicators released to pypi, update description at
  https://sourceforge.net/p/appindicators/admin/overview
to read:

Source code repository for:
 - indicatorfortune
 - indicatorlunar
 - indicatoronthisday
 - indicatorppadownloadstatistics
 - indicatorpunycode
 - indicatorscriptrunner
 - indicatorstardate
 - indicatortest
 - indicatortide
 - indicatorvirtualbox

More details and screenshots:
 -  https://askubuntu.com/q/30334/67335

Releases:
- https://pypi.org/project/indicatorfortune
- https://pypi.org/project/indicatorlunar
- https://pypi.org/project/indicatoronthisday
- https://pypi.org/project/indicatorppadownloadstatistics
- https://pypi.org/project/indicatorpunycode
- https://pypi.org/project/indicatorscriptrunner
- https://pypi.org/project/indicatorstardate
- https://pypi.org/project/indicatortest
- https://pypi.org/project/indicatortide
- https://pypi.org/project/indicatorvirtualbox


# Long Term

## Create non-symbolic icons
Some distros/desktops do not utilise the GNOME symbolic icon mechanism.
Determine which distros/desktops these are and if anything can be done.


## Replacement for wmctrl for indicatorvirtualbox on Wayland
https://git.sr.ht/~brocellous/wlrctl is a work-in-progress wmctrl replacement.
Tested wlrctl on Ubuntu 24.04 but does not work when attempting to access
window information:
  error message: Foreign Toplevel Management interface not found!

https://github.com/CZ-NIC/run-or-raise 
GNOME extension; maybe could be used but only works on GNOME presumably.

https://github.com/ickyicky/window-calls
GNOME extension; maybe could be used but only works on GNOME presumably.


## Access Data at Runtime
Reading
    https://setuptools.pypa.io/en/latest/userguide/datafiles.html#accessing-data-files-at-runtime
it appears that data files which are part of the installation should be accessed
via importlib.resources which is available since Python 3.10.
Would only apply to locale and stars.dat / planets.bsp (for astroskyfield).
Consider this once Ubuntu 20.04 / Debian 11 (et al) are no longer supported.


## Migrate to GTK4
May need to continue to run as GTK3 simulataneously.
- https://discourse.gnome.org/t/migrating-gtk3-treestore-to-gtk4-liststore-and-handling-child-rows/12159
- https://stackoverflow.com/questions/73006299/unable-to-get-application-icons-to-display-with-gtk4-under-ubuntu


## Installation other than via PyPI
Current implementation builds a self-contained wheel uploaded to PyPI.

An end-user installs an indicator by:
- installing OS packages
- creating a venv
- installing wheel from PyPI
- copy icons/desktop/locale
- some distros require setting an extension

Consider either building a .deb/.rpm or even adding to each major distro's
package repository.

I read on Debian's documentation for getting a package into the repository 
requires that there must be a "need" for the package.
So it is possible some but not all indicators are accepted.
No point in that; all or nothing.

If installing via a .deb/.rpm (or repository package), will likely need to
change the venv location to /opt rather than the user $HOME, particulary given
icons/locale/.desktop will then be installed under /usr/share.

https://github.com/jordansissel/fpm
Takes a Python project and converts to .deb/.rpm
Does not yet support pyproject.toml

Where to distribute the .deb/.rpm?  Does Sourceforge or Github allow this?
