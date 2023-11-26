# indicator-tide changelog

## v1.0.30 (2023-11-22)

- Reinstated the autostart option in Preferences with the addition of a optional delay to start up.

## v1.0.29 (2023-01-09)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu Unity 22.04

## v1.0.28 (2022-11-03)

- Rather than throw an exception, gracefully handle when there is no user script specified (typically first time the indicator is run).
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

## v1.0.27 (2022-10-29)

- Code refactor caused base class variables to be uninitialised.

## v1.0.26 (2022-10-29)

- Increased size of icon to take up entire permissible area.

## v1.0.25 (2022-08-04)

- Around the middle of 2021, the UKHO reduced their coverage of tidal data from globally to only UK ports.  As no other source for global tidal data has been found, the indicator has been radically overhauled. The end user must now write a Python3 script which downloads/obtains tidal data and pass that data back to the indicator. See the file 'tidedatagetterbase.py' located in the installation directory (typically /usr/share/indicator-tide) as an example. Your script must extend the base class 'TideDataGetterBase' and implement the function 'getTideData' to obtain your tidal data, returning a list of 'tide.Reading' objects. Specify the script path/name and the class name in the Preferences.
- Update release to bionic as xenial is end of life.

## v1.0.24 (2021-02-03)

- Removed the notification when the tidal data is (successfully) updated. Instead a message is presented on the About dialog to inform the user if the tidal data is in user local time or the time zone of the port. Any errors are shown as a notification to the user and logged to file.

## v1.0.23 (2020-11-05)

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

## v1.0.22 (2020-09-05)

- Annual renewal of UKHO licence.

## v1.0.21 (2020-04-26)

- Added Yaru icon.
- Fixed deprecation warnings.

## v1.0.20 (2020-02-08)

- Bug fix: Cache backend generated bad paths with a double slash. 

## v1.0.19 (2019-12-30)

- On-click URL now takes into account daylight savings.

## v1.0.18 (2019-12-29)

- Bug fix: Rollover year to year was incrementing the year for each reading.
- Bug fix: Removed spurious hard coded string throwing out readings.

## v1.0.17 (2019-09-23)

- Now able to reset date/tide formatting to factory default.
- Now uses a base class to share functionality amongst indicators.
- Whilst starting up, a single menu item "Initialising..." is displayed. Once fully initialised, the menu proper is shown.
- When an update is underway or the About/Preferences dialogs are displayed, the About/Preferences/Quit menu items are disabled.
- About dialog now shows copyright, artists and corrected URL for website.
- Update debian/compat to 9.

## v1.0.16 (2019-09-21)

- Fixed typo in tooltip.

## v1.0.15 (2019-05-02)

- Annual renewal of UKHO licence.
- Corrected the indents for menu items for GNOME Shell.
- Tidy up load config of user preferences.
- Added hyperlink to the About dialog which links to the error log text file (only visible if the underlying file is present).
- About dialog now pulls the changelog directly from /usr/share/doc rather than a redundant duplicate in the installation directory.
- Update release to xenial as trusty is end of life.
- Update debian/control Standards-Version to 3.9.7.
- Added logging for when the license has expired and data unavailable.

## v1.0.14 (2018-10-03)

- Fixed incorrect grammar in About dialog.
- Now uses a global URL timeout when attempting downloads.

## v1.0.13 (2018-08-14)

- Annual renewal of UKHO licence.

## v1.0.12 (2018-04-29)

- Bug fix: the [TYPE] and [LEVEL] tags could potentially be translated.

## v1.0.11 (2017-10-23)

- Updated Russian translation.  Thanks to Oleg Moiseichuk.
- Now checks for an internet connection before downloading tidal data. This stops the log file cluttering up with failed connection messages.
- Removed user config migration code.

## v1.0.10 (2017-10-06)

- Bug fix: In Ubuntu 16.04 and greater, icons for ubuntu-mono-dark and ubuntu-mono-light would not load due to directories not present in the underlying index.theme file.

## v1.0.9 (2017-09-25)

- Bug fix: Handle year changeover when tidal data contains both December and January.

## v1.0.8 (2017-05-02)

- Bug fix: Tidal readings are now displayed based on the date/time. If all of a port's readings contain both date and time, each reading is converted to user local date/time. If at least one of a port's readings is missing the time, all of the readings are shown in port local date/time (as per original source).
- Corrected warnings in .desktop file.
- Changed the format of the tide type, time and level to have the type first (rather than time first) to match the data source.
- Added a preference to format the display when a reading has no time.
- Split the Preferences dialog over two tabs (ports and general).
- About/Preferences dialogs now block each other - only show one at a time.
- User settings now stored in the directory specified by the environment variable XDG_CONFIG_HOME, or, if not present, $HOME/.config (existing user settings stored in $HOME are migrated to the new location).
- Tidal data is now cached for up to 24 hours for offline usage.
- Annual renewal of UKHO licence.
- Port listings have been updated - some additions, some deletions.
- Update release to trusty as precise is end of life.

## v1.0.7 (2017-02-10)

- Bug fix: Missing python3-notify2 from the debian/control file. Also added a gi.require_version to the source.

## v1.0.6 (2016-12-06)

- Bug fix: Corrected debian/install file to reflect changes to source files.

## v1.0.5 (2016-09-27)

- Bug fix: Now uses the X-GNOME-Autostart-enabled tag for autostart.
- Updated UKHO port data to 2016/2017 listing. The UKHO port data is split into two parts - UK ports, which does not expire and non-UK ports for which data expires annually. If the license date is exceeded, only the UK ports will be available.
- Now displays the country next to the port city/town.
- Shows a notification if the tidal information could not be obtained.
- Added an option to show the first day's tidal information in full and subsequent days as submenus - useful for small screens.
- By default, tidal data is displayed as submenus, except for the first day.
- The daylight savings offset is now automatically calculated (based on the computer's time zone and DST tables). The user preference has been removed.
- Fixed PyGIWarnings on imports.
- Overhaul of icons: only the hicolor icon is required and all theme icons are created from the hicolor via the build script.
- Overhaul of build script: extracted common functions into a separate script used by all indicators.

## v1.0.4 (2016-09-26)

- Renewed United Kingdom Hydrographic Office annual data access license.

## v1.0.3 (2016-06-06)

- Fixed Lintian warnings - added extended description to control file and copyright file now refers to common license file for GPL-3.
- Icon for ubuntu-mono-dark theme was incorrect colour.
- Updated comment of desktop file.

## v1.0.2 (2016-02-25)

- Bug fix: Incorrectly handled Feb 29.

## v1.0.1 (2016-02-05)

- Bug fix: Only the first update would occur, subsequent updates did not occur.  Now updates every twelve hours or just after (local) midnight.

## v1.0.0 (2015-09-23)

- Initial release.

