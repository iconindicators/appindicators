# Immediate

## No autostart on Kubuntu and Manjaro
Given there is no autostart on Kubuntu 24.04 and Manjaro 24.04.7,
should the autostart checkbox and delay spinner be hidden?
If some fix through an OS update appears in the meantime,
will need to release ALL indicators again unhiding checkbox and spinner.
Could have a tooltip...but if the fix comes, don't need to re-release but should.
Otherwise just leave as is...and keep the entry in the changelog.
What to do?


## Update date CHANGELOG.md
For each indicator's CHANGELOG.md, at release time, update the release date in
the latest entry to the date of release.


## When finally released, or at least indicatortest is released, post a note to
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

Whilsts installing via .deb/.rpm is easier for the end-user,
it would be even easier (for the end-user) if each indicator was present in
a distro's package repository (Debian, Fedora, openSUSE).

May need to change the venv location to /opt rather than the user $HOME,
particulary given icons/locale/.desktop will then be installed under /usr/share.

https://github.com/jordansissel/fpm
Takes a Python project and converts to .deb/.rpm
Does not yet support pyproject.toml
