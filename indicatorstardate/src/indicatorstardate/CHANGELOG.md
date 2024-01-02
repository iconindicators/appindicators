# Indicator Stardate changelog

## v1.0.45 (2023-11-22)

- Now uses

        datetime.datetime.now( datetime.timezone.utc )
    rather than deprecated

        datetime.datetime.utcnow()

- Reinstated the autostart option in Preferences with the addition of a optional delay to start up.
- Overhaul of all indicators to adhere to the pyproject.toml standard.  Further, indicators are no longer deployed using the .deb format.  Rather, PyPI (pip) is now used, along with commands, to install operating system packages and copy files.  In theory, this allows for indicators to be deployed on any platform which supports both pip and the AppIndicator library.
- Now works (full or in part) on the following distributions/versions:
  - Debian 11 / 12
  - Fedora 38 / 39
  - Linux Mint 21 Cinnamon
  - Manjaro 22.1 GNOME No calendar.
  - openSUSE Tumbleweed No clipboard; no wmctrl; no calendar.
  - openSUSE Tumbleweed GNOME on Xorg No calendar.


## v1.0.44 (2023-01-09)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu Unity 22.04


## v1.0.43 (2022-11-03)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu 20.04
  - Ubuntu 22.04
  - Ubuntu Budgie 20.04
  - Ubuntu Budgie 22.04
  - Ubuntu MATE 20.04
  - Ubuntu MATE 22.04
  - Ubuntu Unity 20.04
- Limited functionality on the following Ubuntu variants/versions...
  - Kubuntu 20.04 - No mouse wheel scroll.
  - Kubuntu 22.04 - No mouse wheel scroll.
  - Lubuntu 20.04 - No label; no dynamic tooltip (uses a menu item).
  - Lubuntu 22.04 - No label; no dynamic tooltip (uses a menu item).
  - Xubuntu 20.04 - No mouse wheel scroll.
  - Xubuntu 22.04 - No mouse wheel scroll.


## v1.0.42 (2022-10-29)

- Code refactor caused base class variables to be uninitialised.


## v1.0.41 (2022-10-29)

- Increased size of icon to take up entire permissible area.
- Update release to bionic as xenial is end of life.


## v1.0.40 (2020-11-05)

- On computer startup when the indicator is set to autostart, sometimes the indicator can become unresponsive. The end user can set the property

        X-GNOME-Autostart-Delay=120
    in
   
        ~/.config/autostart/indicator-lunar.py.desktop

    to delay the indicator startup (for two minutes) avoiding the issue. For new installations, by default, the value is set to zero.
- Removed the preference for autostart. To change indicator autostart (off or on), open the file

        ~/.config/autostart/indicator-lunar.py.desktop

    and add/edit the setting to either

        X-GNOME-Autostart-enabled=true

    or

        X-GNOME-Autostart-enabled=false

    Alternatively, add the indicator using Startup Applications. For new installations, by default, autostart will be set to true.


## v1.0.39 (2020-04-26)

- Added Yaru icon.
- Fixed deprecation warnings.


## v1.0.38 (2019-09-23)

- Bug fix: On some variants of Lubuntu/Xubuntu, the icon label is absent. As a workaround, show the stardate in the mouse hover tooltip.
- Bug fix: Dialogs now have a parent specified.
- Now uses a base class to share functionality amongst indicators.
- Whilst starting up, a single menu item "Initialising..." is displayed. Once fully initialised, the menu proper is shown.
- When an update is underway or the About/Preferences dialogs are displayed, the About/Preferences/Quit menu items are disabled.
- The stardate library now computes when the next update will occur.
- About dialog now shows copyright, artists and corrected URL for website.
- Update debian/compat to 9.


## v1.0.37 (2019-05-02)

- Tidy up load config of user preferences.
- Added hyperlink to the About dialog which links to the error log text file (only visible if the underlying file is present).
- About dialog now pulls the changelog directly from /usr/share/doc rather than a redundant duplicate in the installation directory.
- Update release to xenial as trusty is end of life.
- Update debian/control Standards-Version to 3.9.7.


## v1.0.36 (2017-10-23)

- Updated Russian translation.  Thanks to Oleg Moiseichuk.
- Removed user config migration code.


## v1.0.35 (2017-10-06)

- Bug fix: In Ubuntu 16.04 and greater, icons for ubuntu-mono-dark and ubuntu-mono-light would not load due to directories not present in the underlying index.theme file.


## v1.0.34 (2017-04-27)

- Bug fix: Underlying Stardate API incorrectly converted from '2009 revised' stardate to Gregorian datetime.datetime (was off by one day).
- Removed the "show in menu" option as all supported platforms allow a label next to the icon.
- Corrected warnings in .desktop file.
- Tidied up tool tip text in Preferences dialog.
- Simplified the Stardate API to provide getters for conversion between Gregorian datetime.datetime and 'classic stardate and '2009 revised' stardates.
- Reduced icon to a single colour.
- About/Preferences dialogs now block each other - only show one at a time.
- User settings now stored in the directory specified by the environment variable XDG_CONFIG_HOME, or, if not present, $HOME/.config (existing user settings stored in $HOME are migrated to the new location).
- Update release to trusty as precise is end of life.


## v1.0.33 (2016-07-24)

- Bug fix: Now uses the X-GNOME-Autostart-enabled tag for autostart.
- Scrolling the mouse wheel over the icon/label cycles through all formats.
- Fixed PyGIWarnings on imports.
- Overhaul of icons: only the hicolor icon is required and all theme icons are created from the hicolor via the build script.
- Overhaul of build script: extracted common functions into a separate script used by all indicators.


## v1.0.32 (2016-06-06)

- Fixed Lintian warnings - added extended description to control file and copyright file now refers to common license file for GPL-3.
- Updated comment of desktop file.


## v1.0.31 (2015-05-26)

- Bug fix: Omitted the '_' from 'translator-credits' in the About dialog.


## v1.0.30 (2015-05-22)

- Bug fix: The changelog was not added to the debian/rules file.


## v1.0.29 (2015-05-22)

- Bug fix: The changelog path was incorrect.


## v1.0.28 (2015-05-20)

- GTK.AboutDialog now uses a Stack rather than Notebook to hold the underlying widgets.  Rather than try to (constantly) reverse engineer the GTK.AboutDialog to retrofit the changelog tab, the default GTK.AboutDialog is used with a hyperlink to the changelog inserted.


## v1.0.27 (2015-04-10)

- Tidy up of tooltips and code clean up.


## v1.0.26 (2015-02-12)

- Internationalisation.  Many thanks to Oleg Moiseichuk who was instrumental in this miracle!
- Added Russian translation.  Thanks to Oleg Moiseichuk. 
- About dialog changed to accept translator information.
- Overhaul of repository structure and build script.


## v1.0.25 (2014-12-25)

- Neatened up the left alignment changelog text in the About dialog.
- Cleaned up tooltips and added spacing in the Preferences dialog.


## v1.0.24 (2014-08-25)

- Bug fix: Corrected the '2009 revised' stardate; was out by one.


## v1.0.23 (2014-07-08)

- Bug fix: Handle 'add_credit_section' on Ubuntu 12.04 (was causing a segmentation fault).


## v1.0.22 (2014-06-12)

- Optionally shows the stardate in the menu for desktop environments which don't support text labels next to the icon (Lubuntu 14.04).
- New log handler which truncates the log file to 10,000 bytes.
- Removed legacy code to support old appindicator framework.


## v1.0.21 (2014-03-15)

- Fixed a bug where non-toggle buttons (the close button) were having the toggled signal set.
- Put in a fix for Ubuntu 12.04 (Python 3.2) which does not handle AboutDialog::add_credit_section().


## v1.0.20 (2014-03-01)

- Uses UTC rather than the local date/time.
- AboutDialog is now resizable - makes reading the changelog easier.


## v1.0.19 (2014-02-28)

- Fixed a bug when calculating present day stardates.
- Added option to pad the INTEGER part of classic stardates.


## v1.0.18 (2014-02-27)

- Neglected to update the install file!


## v1.0.17 (2014-02-25)

- Uses AboutDialog from common library.


## v1.0.16 (2013-12-16)

- Created a new About dialog showing the changelog.
- Removed tabbed preferences dialog - tabs were too much.


## v1.0.15 (2013-12-15)

- Updated the About dialog to use Gtk+ 3.


## v1.0.14 (2013-07-05)

- Only create the log file when needed. Thanks to Rafael Cavalcanti <rafael.kavalkanti@gmail.com>.


## v1.0.13 (2013-04-04)

- Now logs to a file in the user's HOME directory.
- Attempt to bring about/preferences to front.


## v1.0.12 (2013-03-15)

- Revised the icons to fill in a square boundary; no longer stretched on Lubuntu/Xubuntu.
- Updated labels/tooltips on Preferences.
- Icons for Preferences/About now show for Lubuntu/Xubuntu.


## v1.0.11 (2013-03-05)

- Major change to API - now supports two types of conversion:
    1. 'classic' (STARDATES IN STAR TREK FAQ V1.6 by Andrew Main)
    2. '2009 revised' (http://en.wikipedia.org/wiki/Stardate).

- Underlying API/example now set to Python 3.


## v1.0.10 (2012-11-16)

- Added python3-gi to debian/control Depends (for Precise support).
- Swapped out python-appindicator for gir1.2-appindicator3-0.1 in debian/control Depends.
- Simpler handling for creating the indicator - should hopefully sustain more environments. 


## v1.0.9 (2012-10-25)

- Changes for Python3 and PyGObject.
- Added a preferences dialog.


## v1.0.8 (2012-08-07)

- Handle the case where the directory ~/.config/autostart does not exist.


## v1.0.7 (2012-07-27)

- Fixed the PPA URL in the About dialog.


## v1.0.6 (2012-07-25)

- Changed the build process to use a single PPA.


## v1.0.5 (2012-07-11)

- Now included example.py in the release to demonstrate the use of the Stardate API.
- Corrected the API version such that it matches the Java API version.


## v1.0.4 (2012-06-25)

- Icon for Elementary theme incorrectly set at 46 (should have been 48).
- Icons in Elementary theme should have been in Lubuntu.
- New icons for Elementary (used by Xubuntu).
- Lubuntu/Xubuntu: User needs to manually remove spurious directory

        /usr/share/icons/elementary/status/48/untitled
        
    then rebuild the image cache:

        sudo gtk-update-icon-cache -f /usr/share/icons/elementary

- If the warning 'Unable to locate theme engine in module_path: "pixmap"' appears on execution, install:

        sudo apt-get install gtk2-engines-pixbuf


## v1.0.3 (2012-06-25)

- Put in detection of Unity to handle the case where python-appindicator is installed but should not be used (Lubuntu) and GTK icon used instead.


## v1.0.2 (2012-06-24)

- Updated package to install icons for Lubuntu and Ubuntu.


## v1.0.1 (2012-06-24)

- Somewhat tested (on Lubuntu).
- Trying to figure out PPA!


## v1.0.0 (2012-06-23)

- Initial release.
- Untested!

