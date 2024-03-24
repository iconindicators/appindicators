# Indicator On This Day changelog

## v1.0.17 (2023-11-22)

- Reinstated the autostart option in Preferences with the addition of a optional delay to start up.
- Now includes a symbolic icon allowing the colour to be adjusted for the current theme.
- Overhaul of all indicators to adhere to the pyproject.toml standard.  Further, indicators are no longer deployed using the .deb format.  Rather, PyPI (pip) is now used, along with commands, to install operating system packages and copy files.  In theory, this allows for indicators to be deployed on any platform which supports both pip and the AppIndicator library.
- Fixed PyGObject 3.11 deprecation warnings.
- Now works (full or in part) on the following distributions/versions:
  - Debian 11 / 12
  - Fedora 38 / 39
  - Linux Mint 21 Cinnamon
  - Manjaro 22.1 GNOME No calendar.
  - openSUSE Tumbleweed No clipboard; no wmctrl; no calendar.
  - openSUSE Tumbleweed GNOME on Xorg No calendar.


## v1.0.16 (2023-11-08)

- Bug fix: Added missing 'calendar' to debian/control "Depends".
- Lowered the initial guess for numbers of menu items as the menu would flow off the screen at times.


## v1.0.15 (2023-01-09)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu Unity 22.04


## v1.0.14 (2022-12-04)

- Now works on the following Ubuntu variants/versions...
  - Kubuntu 20.04
  - Kubuntu 22.04
  - Lubuntu 20.04
  - Lubuntu 22.04
  - Ubuntu 20.04
  - Ubuntu 22.04
  - Ubuntu Budgie 20.04
  - Ubuntu Budgie 22.04
  - Ubuntu MATE 20.04
  - Ubuntu MATE 22.04
  - Ubuntu Unity 20.04
  - Xubuntu 20.04
  - Xubuntu 22.04


## v1.0.13 (2022-10-29)

- Code refactor caused base class variables to be uninitialised.


## v1.0.12 (2022-10-29)

- Increased size of icon to take up entire permissible area.


## v1.0.11 (2022-06-22)

- The debian/compat file had version 11 whereas should have been version 10 which caused build problems.


## v1.0.10 (2022-05-21)

- Added the ".txt" extension to the calendars file located in the user cache.
- Update release to bionic as xenial is end of life.


## v1.0.9 (2020-11-05)

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


## v1.0.8 (2020-05-02)

- Removed leading zero from day in date.


## v1.0.7 (2020-04-26)

- Added Yaru icon.
- Fixed deprecation warnings.


## v1.0.6 (2019-12-05)

- Bug fix: Midnight update caused a crash.


## v1.0.5 (2019-09-23)

- Bug fix: Dialogs now have a parent specified.
- Now uses a base class to share functionality amongst indicators.
- Whilst starting up, a single menu item "Initialising..." is displayed. Once fully initialised, the menu proper is shown.
- When an update is underway or the About/Preferences dialogs are displayed, the About/Preferences/Quit menu items are disabled.
- About dialog now shows copyright, artists and corrected URL for website.
- Update debian/compat to 9.


## v1.0.4 (2019-05-02)

- The estimate for the number of menu items (lines) was off for GNOME Shell.
- Tidy up load config of user preferences.
- Added hyperlink to the About dialog which links to the error log text file (only visible if the underlying file is present).
- About dialog now pulls the changelog directly from /usr/share/doc rather than a redundant duplicate in the installation directory.
- Update release to xenial as trusty is end of life.
- Update debian/control Standards-Version to 3.9.7.


## v1.0.3 (2018-08-13)

- Allow the user to limit the number of events such that a scroll bar does not appear.  Removed the 'Days' preference as it is now redundant.


## v1.0.2 (2018-06-08)

- Removed duplicate calendar entries from the result set.


## v1.0.1 (2017-10-06)

- Bug fix: In Ubuntu 16.04 and greater, icons for ubuntu-mono-dark and ubuntu-mono-light would not load due to directories not present in the underlying index.theme file.


## v1.0.0 (2017-09-16)

- Initial release.

