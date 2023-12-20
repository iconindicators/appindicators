# Indicator Fortune changelog

## v1.0.43 (2023-11-22)

- Corrections made to install and run scripts to avoid globbing paths.  Many thanks to Oleg Moiseichuck!


## v1.0.42 (2023-11-22)

- Bug fix: Remove characters/glyphs which appear as hexadecimal.
- Reinstated the autostart option in Preferences with the addition of a optional delay to start up.
- Overhaul of all indicators to adhere to the pyproject.toml standard.  Further, indicators are no longer deployed using the .deb format.  Rather, PyPI (pip) is now used, along with commands, to install operating system packages and copy files.  In theory, this allows for indicators to be deployed on any platform which supports both pip and the AppIndicator library.


## v1.0.41 (2023-01-09)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu Unity 22.04


## v1.0.40 (2022-12-04)

- Now works on the following Ubuntu variants/versions...
  - Kubuntu 20.04
  - Kubuntu 22.04
  - Lubuntu 20.04
  - Lubuntu 22.04
  - Ubuntu 20.04
  - Ubuntu 22.04
  - Ubuntu Budgie 22.04
  - Ubuntu MATE 20.04
  - Ubuntu MATE 22.04
  - Ubuntu Unity 20.04
  - Xubuntu 20.04
  - Xubuntu 22.04
- Limited functionality on the following Ubuntu variants/versions...
  - Ubuntu Budgie 20.04 - No mouse middle click.


## v1.0.39 (2022-10-29)

- Code refactor caused base class variables to be uninitialised.


## v1.0.38 (2022-10-29)

- Increased size of icon to take up entire permissible area.


## v1.0.37 (2022-06-22)

- The debian/compat file had version 11 whereas should have been version 10 which caused build problems.


## v1.0.36 (2022-06-21)

- Added the ".txt" extension to the history file located in the user cache.
- Update release to bionic as xenial is end of life.


## v1.0.35 (2020-11-05)

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


## v1.0.34 (2020-04-27)

- Bug fix: Remove characters/glyphs which appear as hexadecimal.
- Fixed deprecation warnings.


## v1.0.33 (2020-04-26)

- Added Yaru icon.
- Fixed deprecation warnings.


## v1.0.32 (2020-04-25)

- Fortune history dialog now scrolls to the end. 


## v1.0.31 (2020-02-08)

- Can now display the fortune history (for the session) in a dialog.
- Bug fix: Cache backend generated bad paths with a double slash. 


## v1.0.30 (2019-09-23)

- Bug fix: Default fortune would cause a crash on a reset.
- Bug fix: Dialogs now have a parent specified.
- Now uses a base class to share functionality amongst indicators.
- Whilst starting up, a single menu item "Initialising..." is displayed. Once fully initialised, the menu proper is shown.
- When an update is underway or the About/Preferences dialogs are displayed, the About/Preferences/Quit menu items are disabled.
- About dialog now shows copyright, artists and corrected URL for website.
- Update debian/compat to 9.


## v1.0.29 (2019-05-02)

- Tidy up load config of user preferences.
- Added hyperlink to the About dialog which links to the error log text file (only visible if the underlying file is present).
- About dialog now pulls the changelog directly from /usr/share/doc rather than a redundant duplicate in the installation directory.
- Update release to xenial as trusty is end of life.
- Update debian/control Standards-Version to 3.9.7.


## v1.0.28 (2018-03-27)

- Removed user config migration code.


## v1.0.27 (2017-10-06)

- Bug fix: In Ubuntu 16.04 and greater, icons for ubuntu-mono-dark and ubuntu-mono-light would not load due to directories not present in the underlying index.theme file.


## v1.0.26 (2017-04-25)

- Bug fix: Reset in Preferences did not actually reset!
- Corrected warnings in .desktop file.
- Corrections and updates to the tool tip text in the Preferences dialog.
- Can now sort fortunes in the Preferences.
- Changed default function of middle mouse button click from showing a new fortune to showing the current fortune.
- Handle bogus/missing fortune locations.
- Reduced icon to a single colour.
- About/Preferences dialogs now block each other - only show one at a time.
- User settings now stored in the directory specified by the environment variable XDG_CONFIG_HOME, or, if not present, $HOME/.config (existing user settings stored in $HOME are migrated to the new location).
- Update release to trusty as precise is end of life.


## v1.0.25 (2016-12-14)

- Bug fix: Attempting to delete the history file if it did not exist caused a crash.


## v1.0.24 (2016-07-24)

- Bug fix: Now uses the X-GNOME-Autostart-enabled tag for autostart.
- When adding a new fortune, it is enabled by default.
- Displayed fortunes are now written to ~/.indicator-fortune-history. Each time the indicator is started the file is reset.
- Clicking OK in the Preferences initiates a new fortune.
- Added utf-8 encoding line.
- Fixed PyGIWarnings on imports.
- Overhaul of icons: only the hicolor icon is required and all theme icons are created from the hicolor via the build script.
- Overhaul of build script: extracted common functions into a separate script used by all indicators.


## v1.0.23 (2015-09-30)

- Fixed Lintian warnings - added extended description to control file and copyright file now refers to common license file for GPL-3.
- Cleaned up imports.
- Updated comment of desktop file.
- Changes to API for showing message dialogs.


## v1.0.22 (2015-05-26)

- Bug fix: Omitted the '_' from 'translator-credits' in the About dialog.


## v1.0.21 (2015-05-22)

- Bug fix: The changelog was not added to the debian/rules file.


## v1.0.20 (2015-05-22)

- Bug fix: The changelog path was incorrect.


## v1.0.19 (2015-05-20)

- GTK.AboutDialog now uses a Stack rather than Notebook to hold the underlying widgets.  Rather than try to (constantly) reverse engineer the GTK.AboutDialog to retrofit the changelog tab, the default GTK.AboutDialog is used with a hyperlink to the changelog inserted.


## v1.0.18 (2015-05-06)

- Bug fix: Incorrectly called the process to get fortunes.


## v1.0.17 (2015-04-10)

- Tidy up of tooltips and code clean up.


## v1.0.16 (2015-03-07)

- Added a tooltip to suggest other fortune packages may be available, other than the English default.
- Made the default directory when adding to be /usr/share/games/fortunes.


## v1.0.15 (2015-02-13)

- Internationalisation.  Many thanks to Oleg Moiseichuk who was instrumental in this miracle!
- Added Russian translation.  Thanks to Oleg Moiseichuk. 
- About dialog changed to accept translator information.
- Overhaul of repository structure and build script.


## v1.0.14 (2014-12-26)

- Tidied tooltips in the Preferences dialog.
- Cleaned up menu code.


## v1.0.13 (2014-09-13)

- Neatened up the left alignment changelog text in the About dialog.
- Removed redundant option to show screen notification!
- Overhaul of Preferences dialog.


## v1.0.12 (2014-07-08)

- Bug fix: Handle 'add_credit_section' on Ubuntu 12.04 (was causing a segmentation fault).


## v1.0.11 (2014-06-12)

- Now supports a middle mouse click on the icon to trigger one of the New/Copy/Show fortune menu items (not supported on all versions/derivatives of Ubuntu).
- New log handler which truncates the log file to 10,000 bytes.
- Removed legacy code to support old appindicator framework.


## v1.0.10 (2014-05-12)

- Added "Show Last Fortune" menu option.


## v1.0.9 (2014-03-15)

- Fixed a bug where non-toggle buttons (the close button) were having the toggled signal set.
- Put in a fix for Ubuntu 12.04 (Python 3.2) which does not handle AboutDialog::add_credit_section().


## v1.0.8 (2014-03-01)

- Fixed the ok/cancel when add/edit of fortunes in the preferences.


## v1.0.7 (2014-02-25)

- Now sorts fortunes by path name in the add/edit/remove list.
- Uses AboutDialog and showMessage from common library.


## v1.0.6 (2013-12-16)

- Created a new About dialog showing the changelog.


## v1.0.5 (2013-12-15)

- Updated the About dialog to use Gtk+ 3.


## v1.0.4 (2013-12-05)

- Capitalised menu items.
- Cleaned up layout of preferences.
- Added file/directory browsing for finding fortunes.


## v1.0.3 (2013-12-04)

- Fixed bug when the fortune path contained spaces.
- Made the text field containing the fortune path wide enough to display the path.


## v1.0.2 (2013-12-02)

- Fixed bug when the notification summary is empty.


## v1.0.1 (2013-12-02)

- Fixed bug when dealing with .dat files - needed to remove the .dat extension.
- Fixed bug when adding a directory and no trailing slash was included.
- Added tooltips.


## v1.0.0 (2013-12-01)

- First release.

