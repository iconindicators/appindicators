# Indicator Lunar changelog

## v1.0.101 (2023-11-22)

- Bug fix: Minor planets would display in the preferences despite missing apparent magnitude data.
- Now uses

        datetime.datetime.now( datetime.timezone.utc )
    rather than deprecated

        datetime.datetime.utcnow()

- Reinstated comets; a tremendous thank you to Jure Zakrajšek @ COBS!
- Reinstated the autostart option in Preferences with the addition of a optional delay to start up.
- Now includes a symbolic icon allowing the colour to be adjusted for the current theme.
- Overhaul of all indicators to adhere to the pyproject.toml standard.  Further, indicators are no longer deployed using the .deb format.  Rather, PyPI (pip) is now used, along with commands, to install operating system packages and copy files.  In theory, this allows for indicators to be deployed on any platform which supports both pip and the AppIndicator library.
- Removed old eclipse information.
- Now works (full or in part) on the following distributions/versions:
  - Debian 11 / 12
  - Fedora 38 / 39
  - Linux Mint 21 Cinnamon
  - Manjaro 22.1 GNOME No calendar.
  - openSUSE Tumbleweed No clipboard; no wmctrl; no calendar.
  - openSUSE Tumbleweed GNOME on Xorg No calendar.


## v1.0.100 (2023-01-09)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu Unity 22.04


## v1.0.99 (2022-11-03)

- Now works on the following Ubuntu variants/versions...
  - Kubuntu 20.04
  - Kubuntu 22.04
  - Ubuntu 20.04
  - Ubuntu 22.04
  - Ubuntu Budgie 20.04
  - Ubuntu Budgie 22.04
  - Ubuntu MATE 22.04
  - Ubuntu Unity 20.04
  - Xubuntu 20.04
  - Xubuntu 22.04
- Limited functionality on the following Ubuntu variants/versions...
  - Lubuntu 20.04 - No label; tooltip is not dynamic; icon is not dynamic.
  - Lubuntu 22.04 - No label; tooltip is not dynamic; icon is not dynamic.
  - Ubuntu MATE 20.04 - Dynamic icon is truncated (set to fixed).


## v1.0.98 (2022-10-29)

- Code refactor caused base class variables to be uninitialised.


## v1.0.97 (2022-10-29)

- Increased size of icon to take up entire permissible area.


## v1.0.96 (2022-10-23)

- Bug fix: PyEphem/XEphem credit omitted from previous release.
- Over the years, PyEphem's list of stars has accumulated duplicates and misspellings, which must be kept for backward compatibility. The list of stars has now been sanitised using the IAU CSN Catalog at http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt
- Replaced '--' with '-' in cache filenames for minor planet apparent magnitude and satellite general perturbations.
- The equinox and solstice are now displayed in order of occurrence.
- Added separators to moon/sun menus to improve readability.
- Added option that if that body's set is before sunset, show that body's immediate next rise.
- Updated Celestrak URL.


## v1.0.95 (2022-08-24)

- Satellite data now uses OMM format rather than TLE. As a result, the international designator will look slightly different. Requires PIP3 package 'sgp4' which should be automatically installed. If not:

            sudo pip3 install --upgrade sgp4


## v1.0.94 (2022-08-17)

- Bug fix: Full moon icon was not appearing in the werewolf notification.
- Minor planets are back!  Many thanks to Lowell Minor Planet Services.
- Removed Pluto from planets list and is now accessible as a minor planet, when its apparent magnitude is 15 or less.
- Consolidated the Preferences dialog: planets, minor planets, comets (to be reinstated) and stars are now on a single tab called 'Natural Bodies'.
- Increased URL timeout from 5 seconds to 20 seconds.


## v1.0.93 (2022-07-05)

- Due to suspected stale data, computing the apparent magnitude for comets and minor planets is no longer reliable.  As such, comet and minor planet functionality has been disabled.
- Increased the minimal required version of PyEphem to 4.1.3.
- Removed old eclipse information.


## v1.0.92 (2021-12-13)

- Now uses PyEphem 4.1.2 which should be automatically installed via the PPA process.  If not, the manual instructions are:

            sudo apt-get install -y python3-pip
            sudo pip3 install --ignore-installed --upgrade ephem


## v1.0.91 (2021-11-28)

- Bug fix: Improved the accuracy/coverage of the on-click URL for comets and minor planets names (hopefully all variants are now covered).
- Comets and Minor Planets displayed in the menu and preferences are no longer upper cased, but rather displayed as shown in the data files.


## v1.0.90 (2021-10-26)

- Bug fix: Removed separator character following empty { } in icon text.
- Bug fix: Satellites sometimes not showing set information when in transit.
- Bug fix: Satellite rise time was omitted when computing next update time.
- New preference to limit satellite passes to a time range.


## v1.0.89 (2021-07-09)

- Added dh-python to debian/control Build-Depends to satisfy LaunchPad:   https://askubuntu.com/q/1263305/67335


## v1.0.88 (2021-04-05)

- Bug fix: Tags not enclosed by surrounding { } were left in the label.
- Update release to bionic as xenial is end of life.
- Removed old eclipse information.


## v1.0.87 (2021-03-04)

- Bug fix: Missing magnitude values in the Minor Planet Center data files coupled with incorrect handling within PyEphem produced spurious magnitude values, causing comets and minor planets to appear when they should not. Will take up to four days for your cache to clear and see changes.
- Bug fix: Satellites would not display if the user changed the preferences from no satellites checked to one or more satellites checked.
- Reduced search time for visible satellite passes.


## v1.0.86 (2021-01-05)

- Bug fix: Sorting satellites by name omitted rise/set information.
- Bug fix: Handle exception when OE data contains spurious '****'.
- Bug fix: Handle exception when TLE data omits the launch year.
- PyEphem 3.7.7.0 added additional stars, with some duplicates/errors. The list of stars will appear as defined by PyEphem for 3.7.7.0.
- Removed old eclipse information.


## v1.0.85 (2020-05-31)

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
- Removed old eclipse information.


## v1.0.84 (2020-05-29)

- Bug fix: On-click function not working for comets and minor planets.


## v1.0.83 (2020-04-30)

- Bug fix: Icon incorrectly rendered on Ubuntu 20.04.


## v1.0.82 (2020-04-26)

- Bug fix: Under Ubuntu 20.04, SVG header only supports http, not https.
- Added Yaru icon.
- Fixed deprecation warnings.


## v1.0.81 (2019-05-02)

- Under GNOME Shell, the indicator grinds to a halt and if menu items extend beyond the bottom of the screen, scrolling does not work. Consequently, any item/attribute/preference not directly assisting the home astronomer to locate an object has been removed. The exceptions are the attributes moon phase, eclipse, solstice/equinox.
- Removed decimal degrees from azimuth/altitude.
- Removed right ascension and declination; azimuth/altitude are sufficient.
- Removed planetary moons; each moon's azimuth/altitude is effectively the same as the parent planet for the purposes of the indicator.
- Removed werewolf warning percentage from preferences and fixed at 96%.
- Removed date/time format from preferences; uses ISO 8601 without seconds.
- TLE/OE data file sources are no longer configurable.
- Bodies which are 'never up' are not displayed.
- Bodies which are 'always up' only display azimuth/altitude.
- Bodies below the horizon only display the rise date/time.
- Bodies above the horizon display the set date/time and azimuth/altitude.
- Only visible satellite passes (at dawn/dusk for most latitudes) are shown.
- Added minor planets courtesy of the Minor Planet Center.
- Magnitude filtering extended to include planets and stars.
- Added on-click URL for the moon, sun, planets, stars and minor planets.
- Added preference to hide a body if it is below the horizon (yet to rise).
- Removed old eclipse information.
- Dynamically created icons are stored in user cache rather than /tmp.
- Added hyperlink to the About dialog which links to the error log text file (only visible if the underlying file is present).
- About dialog now pulls the changelog directly from /usr/share/doc rather than a redundant duplicate in the installation directory.
- About dialog now shows copyright, artists and corrected URL for website.
- Now uses a base class to share functionality amongst indicators.
- Whilst starting up, a single menu item "Initialising..." is displayed. Once fully initialised, the menu proper is shown.
- When an update is underway or the About/Preferences dialogs are displayed, the About/Preferences/Quit menu items are disabled.
- Update release to xenial as trusty is end of life.
- Update debian/control Standards-Version to 3.9.7.
- Update debian/compat to 9.
- Created an archive PPA to hold a version of each indicator prior to the switch over: https://launchpad.net/~thebernmeister/+archive/ubuntu/archive


## v1.0.80 (2018-12-19)

- Remove extraneous whitespace from comet names.
- Now uses a global URL timeout when downloading.
- Removed old eclipse information.


## v1.0.79 (2018-09-05)

- Bug fix: When a comet was 'always up' or 'never up', only that information was displayed whereas the remaining information was omitted.
- Bug fix: When a user had the default URLs for TLE/OE data, those URLs would still use http rather than https.


## v1.0.78 (2018-09-04)

- The comet data source no longer accepts http and so changed to https (along with all other URLs).  Well spotted Oleg Moiseichuk!
- Removed old eclipse information.


## v1.0.77 (2018-02-18)

- Now checks for an internet connection before downloading TLE/OE data. This stops the log file cluttering up with failed connection messages.
- Reduced the download period for TLE/OE data.
- Removed old eclipse information.
- Removed user config migration code.


## v1.0.76 (2017-10-21)

- Whitespace padding can now be added to the front/rear of the icon text. This is useful in Ubuntu 17.10 as the icon and text are too close together.
- Updated Russian translation.  Thanks to Oleg Moiseichuk.


## v1.0.75 (2017-10-06)

- Bug fix: In Ubuntu 16.04 and greater, icons for ubuntu-mono-dark and ubuntu-mono-light would not load due to directories not present in the underlying index.theme file.
- Added options to specify the date/time format for attributes.


## v1.0.74 (2017-03-01)

- Corrected warnings in .desktop file.
- Removed expired eclipse information.
- About/Preferences dialogs now block each other - only show one at a time.
- User settings now stored in the directory specified by the environment variable XDG_CONFIG_HOME, or, if not present, $HOME/.config (existing user settings stored in $HOME are migrated to the new location).
- Update release to trusty as precise is end of life.


## v1.0.73 (2017-03-01)

- Bug fix: Date/Time objects returned from the pyephem backend may have a zero component for milliseconds which is dropped. When parsing from string to a Date/Time a format exception occurs.
- Removed expired eclipse information.


## v1.0.72 (2017-02-08)

- Bug fix: Bad comet data was causing a core dump. Ideally the underlying data would be screened for bad data, but the data format is long and convoluted. Instead, each comet is computed and if certain attributes are NaN, namely earth_distance, phase, size and sun_distance, the comet is deemed to have bad data.


## v1.0.71 (2017-01-20)

- Bug fix: If the moon was unchecked, the icon could not be created nor the full moon notification be computed.


## v1.0.70 (2016-12-14)

- Bug fix: Mixing of round and int caused a mismatch between the moon's phase and illumination.


## v1.0.69 (2016-07-24)

- Bug fix: Now uses the X-GNOME-Autostart-enabled tag for autostart.
- The satellite notification has been simplified to show the rise/set time (rather than date and time) and the rise/set azimuth is rounded.
- The dynamically created icon is updated only as needed (when the lunar illumination, bright limb or theme change values).
- Changes to formats/rounding of several attributes to improve readability.
- Minor change to tool tip in the Preferences.
- Removed expired eclipse information.
- Fixed PyGIWarnings on imports.
- Overhaul of icons: only the hicolor icon is required and all theme icons are created from the hicolor via the build script.
- Overhaul of build script: extracted common functions into a separate script used by all indicators.


## v1.0.68 (2016-06-16)

- Fixed tooltip on sort satellite by date/time option to reflect the default value.
- Added tooltip to 'group stars by constellation' option.


## v1.0.67 (2016-06-06)

- Fixed Lintian warnings - added extended description to control file and copyright file now refers to common license file for GPL-3.
- Icons for elementary and ubuntu-mono-light theme were incorrect colours.
- Updated comment of desktop file.


## v1.0.66 (2015-09-23)

- Bug fix: Tags in which the underlying object is unchecked or no longer exists (such as a comet/satellite) are stripped from the indicator text. Thanks to Oleg Moiseichuk for the regular expression code and testing!
- Bug fix: "Orbital Element" renamed to "Comet".  Some user preferences will likely need to be reset.
- The default text for the summary/message for satellite notification now includes the Number and International Designator.
- The satellite menu text has been hard-coded to the format 'Satellite Name : Number : International Designator'.  The corresponding user preference has been removed.
- Removed the user preferences to specify the satellite on-click URL; satellite on-click still remains.
- Added on-click URL look-up for comets.
- Added latitude/longitude/elevation of user's location to icon text tags.
- Added user preference to hide the moon/sun.
- When computing moon/sun/planets/stars/comets, if the body is never up and the user preference is to hide on never up, the remaining computations for that body are omitted.
- Removed expired eclipse information.
- Use the process wrapper utilities rather than direct calls.
- Changes to API for showing message dialogs.


## v1.0.65 (2015-08-24)

- New release of pyephem 3.7.6.0.
- Removed the getBodyCopy() functionality which was a workaround for issue https://github.com/brandon-rhodes/pyephem/issues/44


## v1.0.64 (2015-08-04)

- Bug fix: The values for date/time were appearing in UTC in the Preferences dialog.  Although valid values, they should strictly appear in local date/time to match the values in the indicator menu.
- Bug fix: Some textual values were not being translated in the Preferences dialog.
- Removed DD:MM:SS from satellite notification as the notification looked too crowded/busy.


## v1.0.63 (2015-07-23)

- Bug fix: The calculation to determine when the full moon notification should be displayed was incorrectly determining the illumination percentage and the hourly frequency.
- Bug fix: The satellite notification would sometimes appear multiple times for a given satellite's transit.
- Made the satellite notification appear about a minute prior to when the satellite rises.
- Added a separator between RA/Dec and Az/Alt as these are independent.
- Swapped order of RA/Dec and Az/Alt around as Az/Alt is easier to apply.
- Added the constellation adjacent to each star in the preferences.
- Stars can now be grouped by their constellation - when activated the constellation will be dropped from the star's information.


## v1.0.62 (2015-05-26)

- Bug fix: Omitted the '_' from 'translator-credits' in the About dialog.
- Bug fix: Satellite notification rise/set azimuth mixed degrees with HMS.
- Satellite notification rise/set time now in local rather than UTC.


## v1.0.61 (2015-05-22)

- Bug fix: The changelog was not added to the debian/rules file.


## v1.0.60 (2015-05-22)

- Bug fix: Satellite notification failed due to badly parsed strings.
- Bug fix: The changelog path was incorrect.


## v1.0.59 (2015-05-13)

- Bug fix: The Icon Text was incorrectly parsing nested brackets.
- Bug fix: The declination attribute was incorrectly including the '-' when the value was South.
- GTK.AboutDialog now uses a Stack rather than Notebook to hold the underlying widgets.  Rather than try to (constantly) reverse engineer the GTK.AboutDialog to retrofit the changelog tab, the default GTK.AboutDialog is used with a hyperlink to the changelog inserted.
- Removed all display formatting from backend and put into frontend.


## v1.0.58 (2015-03-04)

- Bug fix: The Icon Text tag list in the Preferences dialog was missing the Tropical Sign tag for stars and all tags for planetary moons.
- Bug fix: The Right Ascension in degrees was incorrect for all objects.
- Bug fix: The Bright Limb angle calculation was erroneous due to mixing of degrees and radians!
- Only write out the list of orbital elements and satellites if the user elects to not add new.  This reduces the volume of information stored in the preferences file by an order of magnitude.
- The option to automatically add new satellites and orbital elements now also works when clicking OK in the preferences.
- Added distance to Earth in kilometres for the Moon's menu item.
- Added timeouts to the TLE/OE download.
- Added caching of TLE/OE downloaded data to avoid over-taxing the respective data sources and to run the indicator off-line.
- Added warnings to some tooltips about having too many bodies might slow down the indicator.
- Removed elapsed eclipse data.
- Removed redundant functions to convert hours/minutes/seconds and degrees/minutes/seconds to decimal degrees as PyEphem does it for free!
- Changed some defaults to reduce the amount of data that is displayed. When loading satellites or orbital elements, these are not checked. Stars are not checked on initial run of the indicator.
- The lookahead period for computing satellite passes has been reduced to two days (previously it was ten days).  This significantly reduces the time to refresh whilst only dropping a handful of satellites.
- For Saturn, added the earth tilt and sun tilt angles.


## v1.0.57 (2015-02-16)

- Bug fix: The last update for satellite TLE data and orbital element data was not being set to the current time after an update.
- Bug fix: In the Preferences, if a bad URL for satellite TLE data or orbital element data was entered, the resulting bad data was carried through to the indicator proper.
- Option to automatically add new satellites and/or orbital elements from the respective data source.
- Changed astronomical unit abbreviation from AU to ua to keep in line with SI (http://en.wikipedia.org/wiki/Non-SI_units_mentioned_in_the_SI).
- Dynamically created icons (the full moon notification when testing in the preferences; the indicator icon which changes according to the current; lunar illumination percentage) are now saved to the /tmp directory (or equivalent).
- Eclipse type information uses a class, so no longer reliant on strings.
- Internationalisation.  Many thanks to Oleg Moiseichuk who was instrumental in this miracle!
- Added Russian translation.  Thanks to Oleg Moiseichuk.
- About dialog changed to accept translator information.
- Overhaul of repository structure and build script.


## v1.0.56 (2015-01-08)

- Bug fix: The 'visible' flag was missing in the satellite notification.


## v1.0.55 (2015-01-01)

- Added orbital elements (comets, et al). Many thanks to the Minor Planet Center for making the data available!
- Added sorting to the list of tags (icon text) and the list of satellites in the Preferences dialog.
- Prevent the credits section in the About dialog from scrolling.


## v1.0.54 (2014-12-28)

- Bug fix: Removed a bogus import which prevented running on Xubuntu.


## v1.0.53 (2014-09-12)

- Bug fix: When checking (adding) a planet in the preferences, the magnitude, right ascension, declination, azimuth and altitude were omitted from indicator text tags table.
- Bug fix: When checking (adding) a star in the preferences, the constellation, rise time and set time were omitted from indicator text tags table.
- Satellites can now be sorted by rise date/time.  This is now the default.
- Satellite notification now optionally includes the rise time, set time, set azimuth and visibility.
- Satellite notification now shows satellites in name/number order or rise time order, depending on user preference.
- The URL which is opened on satellite selection is now configurable.
- Planets/stars which 'never rise' can now be hidden.
- The TLE data source may be specified as a URL (including local file).
- Removed the satellite subsequent pass information as it slowed down the update of the indicator (noticable when many satellites are checked).
- When showing only visible passes, satellites which are circumpolar or 'always up' are included, despite not actually transiting.
- Added Tropical Sign to stars.
- Added attributes of the major moons to Mars, Jupiter, Saturn and Uranus.
- Added dawn/dusk for sun.
- Overhaul of the Preferences dialog.
- Neatened up the left alignment changelog text in the About dialog.


## v1.0.52 (2014-07-29)

- Full moon (werewolf) notification message now supports multiple lines. For formatting restrictions, refer to https://wiki.ubuntu.com/NotifyOSD.
- Satellite info object now provides international designator.
- Renamed some preferences - the user may need to set their preferences particularly if defaults were changed.
- Reorganisation and overhaul of the Preferences dialog.
- Satellite menu text is now configurable.
- Satellite rise notification summary and message are now configurable. For formatting restrictions, refer to https://wiki.ubuntu.com/NotifyOSD.
- Clicking on a satellite's child menu items will open that satellite at http://www.n2yo.com.


## v1.0.51 (2014-07-12)

- Ensure that the full moon notification happens approximately hourly and not more frequently.
- Removed debug print statement.


## v1.0.50 (2014-07-08)

- Bug fix: Handle 'add_credit_section' on Ubuntu 12.04 (was causing a segmentation fault).
- Bug fix: Using the same name for the icon causes the icon to appear the same and so appindicator (or something) decides not to reload the icon. The workaround is to alternate the icon name on each refresh. https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620


## v1.0.49 (2014-07-07)

- Removed legacy code to support old appindicator framework.


## v1.0.48 (2014-06-26)

- Can now distinguish satellites when they never rise or are circumpolar. https://github.com/brandon-rhodes/pyephem/issues/45 Thanks to Brandon Rhodes, author of pyephem!
- Implement workaround for body copy segmentation fault issue https://github.com/brandon-rhodes/pyephem/issues/44.


## v1.0.47 (2014-06-24)

- Bug fix: When switching to show visible satellite passes to show all passes, data for the visibility was not initialised.
- Moved magnitude from the RA/Dec section to the main section as magnitude has nothing to do with location.
- Added the azimuth to the satellite notification.


## v1.0.46 (2014-06-23)

- Put in a fix to handle Gtk.TreeModelSort bug reported at  https://bugs.launchpad.net/ubuntu/+source/pygobject/+bug/1114406.
- When showing only visible satellites, the visible label is now dropped.
- Added option to hide satellites when no transit information is available.


## v1.0.45 (2014-06-22)

- A segmentation fault occurs when running with the new version of PyEphem 3.7.5.3.  This is a quick release which avoids calling the offending code.


## v1.0.44 (2014-06-12)

- New log handler which truncates the log file to 10,000 bytes.
- Added spacing between rise/set and other data in the stars menu.
- Added the option to show each planet/star/satellite as a submenu.
- Added the option to show only visible satellite passes.
- Added the option to limit the display to only upcoming satellite passes.


## v1.0.43 (2014-06-08)

- Bug fix: Now handles the situation when the next rise/set time for a satellite is calculated to be None.


## v1.0.42 (2014-05-30)

- Bug fix: The star data was not being removed after a star was unchecked.
- Bug fix: Each time the preferences was closed (on clicking OK) an update was kicked off (in addition to the main update).
- Bug fix: Handle "extreme" latitudes when encountering always up or never up for rise/set of a body.
- Planets can now be chosen by the user (for display in the menu).
- Added rise/set times and constellation to stars.
- Added URLs to credits section in About dialog.
- Added satellite/station rise and set times - requires intermittent internet access for satellite TLE data.


## v1.0.41 (2014-05-24)

- An import fell off somehow...adding back in!


## v1.0.40 (2014-05-24)

- Added azimuth/altitude/magnitude information for all bodies.
- Can now choose stars to display from the ephem catalog.


## v1.0.39 (2014-04-04)

- Fixed a bug where the eclipse data (the month) was incorrectly parsed in non-English locales.


## v1.0.38 (2014-03-15)

- Fixed a bug where non-toggle buttons (the close button) were having the toggled signal set.
- Put in a fix for Ubuntu 12.04 (Python 3.2) which does not handle AboutDialog::add_credit_section().


## v1.0.37 (2014-03-01)

- Preferences loop was incorrectly handling OK/cancel.


## v1.0.36 (2014-03-01)

- Changed checking of Gtk.ResponseType.CANCEL to Gtk.ResponseType.OK as it was possible to simulate Gtk.ResponseType.OK by hitting the escape key.


## v1.0.35 (2014-02-27)

- Neglected to update the install file!


## v1.0.34 (2013-12-26)

- Added RA/Dec in hh:mm:ss/dd:mm:ss respectively.
- Uses AboutDialog and showMessage from common library.
- Moved theme methods to common library.
- Moved eclipse information into a separate file and removed Ephem dependency.


## v1.0.33 (2013-12-18)

- Bright limb angle was sometimes negative and needed to be "folded" into the correct quadrant by adding 360.
- Changed the RA/Dec calculations in the bright limb to use Apparent Geocentric Position as this gives a closer value to that calculated by Meeus.
- Added RA/Dec to sun and planetary bodies.
- Thanks to Alan Eliasen (http://futureboy.us) for bright limb and RA/Dec.


## v1.0.32 (2013-12-16)

- Created a new About dialog showing the changelog.


## v1.0.31 (2013-12-15)

- Removed the option to run using GTKStatusIcon. When enabled and the indicator was run on a system which supports AppIndicator3, the icon would not appear.


## v1.0.30 (2013-12-15)

- Updated the About dialog to use Gtk+ 3.


## v1.0.29 (2013-12-02)

- Added the bright limb angle for the moon and planets.  Thanks to 'Astronomical Algorithms' by Jean Meeus (and Jürgen Giesen for pointers).
- The icon is now rotated to reflect the bright limb angle (and reality).
- The icon text (the tooltip for GTKStatusIcon) is configurable.
- Changed the control file 'Depends' from Python to Python3.
- Increased the size of the werewolf summary/body text fields.
- Modified the Tropical Sign function to use a copy of the body as downstream calculations were getting trashed.
- Put in a preference to use GTKStatusIcon instead of AppIndicator. On Lubuntu 12.04 it was found that AppIndicator would be created but the tooltip would not render.  This preference lets the user fall back to GTK.


## v1.0.28 (2013-10-24)

- Added the upcoming solar/lunar eclipse (until 2099). Thanks to Fred Espenak and Jean Meeus and NASA!
- Updated About dialog to reflect various authors and shoulders of giants.
- In Ubuntu 13.10 the initial value set by the spinner adjustment (for illumination %) was not appearing in the spinner field. Need to force the initial value by explicitly setting it.


## v1.0.27 (2013-10-17)

- Displays the tropical sign for each planetary body calculated at midnight UTC.  Useful for the astrological enthusiast. Thanks to Ignius Drake (elespector@gmail.com) for the code!


## v1.0.26 (2013-08-28)

- Put in a test button to show the notification text.


## v1.0.25 (2013-08-21)

- The notification text (summary and body) is now configurable.
- The full moon screen notification is no longer fixed to hourly. The indicator updates according to the next date/time for any object's rise/set/phase change.  Therefore the full moon notification may occur more frequently than hourly.


## v1.0.24 (2013-08-02)

- Fixed another update bug: the timeout call was not being refreshed on each update with the correct amount.


## v1.0.23 (2013-07-31)

- The update sometimes occurred slightly earlier than when appropriate, likely due to truncating a float to int.


## v1.0.22 (2013-07-08)

- Fixed a bug: GLib.timeout_add_seconds() requires an integer for the time value.


## v1.0.21 (2013-07-05)

- Only updates when the next rise/set/phase/etc is due.
- Only create the log file when needed. Thanks to Rafael Cavalcanti <rafael.kavalkanti@gmail.com>.


## v1.0.20 (2013-05-04)

- Seems the bug fixed to handle a missing city was not quite fixed!
- Now logs to a file in the user's HOME directory.
- Attempt to bring about/preferences to front.


## v1.0.19 (2013-04-10)

- Revised the icons to fill in a square boundary - no longer stretched on Lubuntu/Xubuntu.
- Icons for Preferences/About now show for Lubuntu/Xubuntu.


## v1.0.18 (2013-02-05)

- Replaced deprecated GObject calls with GLib.
- Fixed a bug: if a city (from the timezone) was not found, the default crashed.  Also added a feature to strip "_" from timezones such as America/New_York.


## v1.0.17 (2012-12-13)

- Ensured all calculations are based from the same date/time.
- Added constellation/distance information to sun menu item.
- Added spacing to all menu items.
- Adjusted each SVG such that the image is horizontally centred and has the same left/right margin for each image.


## v1.0.16 (2012-11-29)

- Added indent for next moon phases.
- Consolidate the first and third quarter SVG functions.


## v1.0.15 (2012-11-28)

- The next phases of the moon were being dropped out before the phase actually arrived!


## v1.0.14 (2012-11-26)

- Now creates the lunar phase icon on the fly for each percentage of illumination!
- Works on Ubuntu 12.04/12.10 and Lubuntu 12.10.   Untested on Xubuntu 12.04/12.10.
- On Lubuntu 12.04, the icon fails to update, the icon label/tooltip does not display and menu separators look odd.  This occurs because AppIndicator3 successfully creates the indicator but then quietly fails to update the icon and so on.  The fix is to put in an override (to use GTK indicator)...which will only be done if a user screams for it. No idea if this occurs on Xubuntu 12.04.


## v1.0.13 (2012-11-20)

- Now runs as Python 3 and requires python3-ephem (from same PPA).
- Kept getting GTK missing child warnings so put menu update back to how it was.


## v1.0.12 (2012-11-19)

- Changed how the update/menu was kicked off in the preferences.


## v1.0.11 (2012-11-16)

- Added python3-gi to debian/control Depends (for Precise support).
- Swapped out python-appindicator for gir1.2-appindicator3-0.1 in debian/control Depends.
- Simpler handling for creating the indicator - should hopefully sustain more environments.


## v1.0.10 (2012-10-22)

- Changes for Python3 (but still runs as Python2) and PyGObject. Have to run as Python 2 since PPA won't/can't build a Python 3 version of Ephem.
- Switched back to using localtime!
- Added option to start the werewolf warning at a particular illumination.
- Using the PyEphem list of cities with latitude/longitude/elevation information, now displays sun/moon/planet data such as rise and set times.


## v1.0.9 (2012-08-09)

- Noticed the dates for next phases were out by hours/days.  Removed the conversion to localtime (ephem.localtime) and got better/closer reality.


## v1.0.8 (2012-08-09)

- Fixed a bug where the phase and illumination did not match due to rounding error.


## v1.0.7 (2012-08-07)

- Handle the case where the directory ~/.config/autostart does not exist.
- Increased the indent of the submenu items by one space.


## v1.0.6 (2012-08-03)

- Adjusted phase calculations to precisely match definitions: Full moon is 100%, new moon is 0 %, 1st/3rd quarter are 50%.  As a result, the icons/labels are only present for a few hours, but overall it's mathematically correct!
- Added additional information to the menu including next phases and the next solstice and equinox.


## v1.0.5 (2012-07-27)

- Consolidated all options into a preferences dialog.
- Fixed the PPA URL in the About dialog.


## v1.0.4 (2012-07-25)

- Changed the build process to use a single PPA.


## v1.0.3 (2012-07-24)

- Added distance from earth/sun and constellation information to the menu.
- Updated main icon to be a crescent.


## v1.0.2 (2012-07-24)

- Added a generic icon to appear in the menu and unity search.


## v1.0.1 (2012-07-23)

- Changed update rate to be hourly.


## v1.0.0 (2012-07-23)

- First release.

