# Immediate

### Debian 13 / Ubuntu 26.04

When these versions are released, will likely have to switch to
libgirepository-2.0-dev and so changes need to be made in:
 - build_wheel
 - utils_readme
and possibly elsewhere!


### Update date in CHANGELOG.md
For each indicator's CHANGELOG.md, at release time, update the release date in
the latest entry to the date of release.


### When indicatortest is released
Post a note to
  https://github.com/AyatanaIndicators/libayatana-appindicator/issues/76
to help the guy out.


### Update the PPA description
At
	https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa
change the description to the following:

For releases for Ubuntu 20.04 and forward:

    https://github.com/iconindicators/appindicators


### For each indicator at
	https://askubuntu.com/questions/30334/what-application-indicators-are-available
update the URL at the top with:

    https://github.com/iconindicators/appindicators

Also update the indicator name (remove the hyphen from the name).


### Test on distros dropping X11 support
If wmctrl is no longer available in a given distro's packages,
will need a new entry in the installation instructions dropping wmctrl.
  https://www.theregister.com/2025/06/12/ubuntu_2510_to_drop_x11/
Fedora 43 is expected to drop X11; when released (Nov 2025)
Ubuntu 25.10 is expected to drop X11; when released (Oct 2025)
Ubuntu 26.04 is expected to drop X11; when released (Apr 2026)


# Long Term

### Deprecation of libayatana-appindicator
When running indicator on Manjaro 25 got a deprecation warning that
libayatana-appindicator is deprecated and to use libayatana-appindicator-glib
instead.

However, there is no package for that and some internet searching suggests
that perhaps the deprecation message is quite early and package managers
for ALL distros are yet to upgrade.

Will need to eventually swap over each distro as it is released with
libayatana-appindicator-glib and update the install instructions.


### Migration of Indicators from Subversion to GitHub

Created an organisation:

  https://github.com/iconindicators

Created a respository for the Python3 appindicators:

  https://github.com/iconindicators/appindicators

Import Subversion to GitHub; include commit history?

  https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/importing-a-subversion-repository
  https://git-scm.com/book/ms/v2/Git-and-Other-Systems-Migrating-to-Git
  http://esr.ibiblio.org/?p=6778
  http://www.catb.org/~esr/reposurgeon/repository-editing.html#conversion
  https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/importing-a-subversion-repository
  https://stackoverflow.com/questions/22931404/import-svn-repo-to-git-without-history
  https://stackoverflow.com/questions/43362551/import-svn-folder-structure-to-git-repo-without-history-users
  https://stackoverflow.com/questions/747075/how-to-git-svn-clone-the-last-n-revisions-from-a-subversion-repository
  https://stackoverflow.com/questions/79165/how-do-i-migrate-an-svn-repository-with-history-to-a-new-git-repository
  https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/importing-a-subversion-repository
  https://git-scm.com/docs/git-svn
  https://stackoverflow.com/questions/6695783/import-subversion-repository-into-git


### Migration of Sourceforge projects to GitHub

Need to create a repository for each stardatesystemtray and worldtimesystemtray
on GitHub, perhaps:

  https://github.com/iconindicators/stardatesystemtray
  https://github.com/iconindicators/worldtimesystemtray

Need to import from SourceForge

  https://sourceforge.net/projects/stardatesystray
  https://sourceforge.net/projects/wrldtimesystray

into GitHub repositories; include commit history?

When done, need to at least leave a note on the SourceForge pages
and/or remove code.

Can the issues be migrated?

Need to look into what version of Java and/or Windows to support.
Windows XP is no longer supported and neither is Java 6.
So maybe look at supporting only Windows 10/11 (check for the EOL dates),
along with the versions of Java supported for those versions of Windows.
Consider also one or more versions prior to Windows 10 and whatever version of
Java was last supported.

Windows EOL
    Vista 2017
    7 2020
    8 2016
    8.1 2023
    10 2025
    11 ...?

Java EOL
    1.6 2013
    1.7 2015
    8 2019...2026
    9 2018
    10 2018
    11 2019...2027
    12 2019
    13 2020
    14 2020
    15 2021
    16 2021
    17 2024...2027
    18 2022
    19 2023
    20 2023
    21 2028...2029
    22 2024
    23 2025
    24 2025
    25 2030

Downloaded Java for Windows 11; was recommended by the Oracle website to
download Java 8.
Installed Java 8.
Installed Stardate System Tray.
Installed World Time System Tray.
Both work!


### Swap Joda Time for Java 8 or Better

According to
  https://www.joda.org/joda-time
if Java 8 or better is used, consider using standard Java library instead of
Joda Time.

Need to see if the required libraries (the chronologies) are available in Java 8
and if so, look at migrating.

Perhaps could even move to Java 11.

The file in question is
  stardatesystemtray/src/TrayIcon.java

  https://stackoverflow.com/questions/74994050/converting-joda-datetime-to-javatime
  https://www.securecodewarrior.com/article/migrating-joda-time-to-java-time
  https://blog.joda.org/2014/11/converting-from-joda-time-to-javatime.html
  https://stackoverflow.com/questions/35043788/migrate-from-joda-time-library-to-java-time-java-8
  https://stackoverflow.com/questions/45348503/joda-time-to-java-8-conversion
  https://stackoverflow.com/questions/73472548/converting-from-joda-to-java-time
  https://docs.openrewrite.org/recipes/java/migrate/joda/jodatimerecipe


### Create non-symbolic icons
Some distros/desktops do not utilise the GNOME symbolic icon mechanism.
Determine which distros/desktops these are and if anything can be done.


### Replacement for wmctrl for indicatorvirtualbox on Wayland
https://git.sr.ht/~brocellous/wlrctl
https://launchpad.net/ubuntu/+source/wlroots
is a work-in-progress wmctrl replacement.
Tested wlrctl on Ubuntu 24.04 but does not work when attempting to access
window information:
  error message: Foreign Toplevel Management interface not found!
Maybe wlroots was not installed and/or Wayland on Ubuntu 20.04 is no good...
...I have a memory of being unable to switch to Wayland on Ubuntu 20.04
but that could have been on the VM and not the desktop itself.
So could check on the desktop, but also Ubuntu 22.04/24.04.
I think possibly the issue was a Gnome bug that wl-paste/wl-copy crashes
on Wayland Ubuntu 20.04

https://github.com/CZ-NIC/run-or-raise
GNOME extension; maybe could be used but only works on GNOME presumably.

https://github.com/ickyicky/window-calls
GNOME extension; maybe could be used but only works on GNOME presumably.

https://unix.stackexchange.com/questions/688583/focus-window-by-title-in-gnome-shell-41-under-wayland
https://github.com/lucaswerkmeister/activate-window-by-title

https://wiki.python.org/moin/DbusExamples

https://unix.stackexchange.com/questions/702236/how-to-list-all-object-paths-under-a-dbus-service-only-usign-dbus-command-line-u

https://unix.stackexchange.com/questions/656729/wmctrl-like-tool-or-alternative-for-kde-wayland
https://unix.stackexchange.com/questions/684461/fedora-36-wmctrl-does-not-work-at-all
https://unix.stackexchange.com/questions/706477/is-there-a-way-to-get-list-of-windows-on-kde-wayland
https://bbs.archlinux.org/viewtopic.php?id=306439
https://github.com/jinliu/kdotool


### Release astroskyfield for indicatorlunar

There is still some work to be done to clean up and finalise astroskyfield
in regards to satellites, comets, and minor planets.  For the most part,
astroskyfield could be released as it runs accurately and fast enough on a good
system.

However, on the 32 bit laptop running Debian 12, I was unable to install both
numpy and pandas, both required for skyfield.  I was able to achieve this on a
virtual machine running 32 bit Debian 12 on a physical 64 bit host, so I don't
know if there was a specific issue with the laptop installation or somehow
the virtual machine installation seemed to be treated as 64 bit or something
else again.

When installing on the laptop I even pinned the versions of pandas/numpy back to
quite old levels in an attempt to install what should be a 32 bit equivalent,
but that didn't work.

Until installing pandas/numpy on 32 bit is resolved and given astroskyfield
still needs tidying up, defer the release of astroskyfield for now.

One option is to clean up astroskyfield for release but release both
astroskyfield and astropyphem.  The Python pip install instructions will have
to include a bash command to determine if 32 bit (so install ephem) or 64 bit
(so install skyfield and pandas/numpy).  In indicatorlunar, internally switch
between astropyephem and astroskyfield if on 32 bit or 64 bit respectively.


### Access Data at Runtime
Reading
    https://setuptools.pypa.io/en/latest/userguide/datafiles.html#accessing-data-files-at-runtime
it appears that data files which are part of the installation should be accessed
via importlib.resources which is available since Python 3.10.
Applies to locale (which works fine as is) and stars.dat / planets.bsp for
astroskyfield.
Consider this once Ubuntu 20.04 / Debian 11 (et al) are no longer supported.


### Migrate to GTK4
May need to continue to run as GTK3 simulataneously.
- https://discourse.gnome.org/t/migrating-gtk3-treestore-to-gtk4-liststore-and-handling-child-rows/12159
- https://stackoverflow.com/questions/73006299/unable-to-get-application-icons-to-display-with-gtk4-under-ubuntu


### Installation other than via PyPI
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


### Add meteor shower information to indicatorlunar
Already have some elementary code: meteorshower.py
