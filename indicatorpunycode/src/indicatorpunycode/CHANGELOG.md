# Indicator Punycode changelog

## v1.0.16 (2025-10-18)

- Reinstated the autostart option in Preferences with the addition of a optional
  delay to start up.
- Now includes a symbolic icon allowing the colour to be adjusted for the
  current theme.
- Overhauled to adhere to the pyproject.toml standard.
- Deployment using the .deb format is superceded; PyPI (pip) is used with
  operating system packages and file copy.
- Now includes an opt-in check during start up for the latest version at PyPI.


## v1.0.15 (2023-01-09)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu Unity 22.04


## v1.0.14 (2022-11-03)

- Bug fix: When reducing the maximum results in the Preferences, the results
  were not actually reduced until the next conversion.
- Bug fix: Fixed a deprecation warning when creating menu items.
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


## v1.0.13 (2022-10-29)

- Code refactor caused base class variables to be uninitialised.


## v1.0.12 (2022-05-09)

- Update release to bionic as xenial is end of life.


## v1.0.11 (2020-11-05)

- On computer startup when the indicator is set to autostart, sometimes the
  indicator can become unresponsive. The end user can set the property

        X-GNOME-Autostart-Delay=120
    in

        ~/.config/autostart/indicator-lunar.py.desktop

    to delay the indicator startup (for two minutes) avoiding the issue. For new
    installations, by default, the value is set to zero.
- Removed the preference for autostart. To change indicator autostart (off or
  on), open the file

        ~/.config/autostart/indicator-lunar.py.desktop

    and add/edit the setting to either

        X-GNOME-Autostart-enabled=true

    or

        X-GNOME-Autostart-enabled=false

    Alternatively, add the indicator using Startup Applications. For new
    installations, by default, autostart will be set to true.


## v1.0.10 (2020-04-26)

- Added Yaru icon.
- Fixed deprecation warnings.


## v1.0.9 (2020-01-06)

- Bug fix: Erroneous call to logging.


## v1.0.8 (2019-09-23)

- Bug fix: Dialogs now have a parent specified.
- Now uses a base class to share functionality amongst indicators.
- Whilst starting up, a single menu item "Initialising..." is displayed. Once
  fully initialised, the menu proper is shown.
- When an update is underway or the About/Preferences dialogs are displayed, the
  About/Preferences/Quit menu items are disabled.
- About dialog now shows copyright, artists and corrected URL for website.
- Update debian/compat to 9.


## v1.0.7 (2019-05-02)

- Tidy up load config of user preferences.
- Added hyperlink to the About dialog which links to the error log text file
  (only visible if the underlying file is present).
- About dialog now pulls the changelog directly from /usr/share/doc rather than
  a redundant duplicate in the installation directory.
- Update release to xenial as trusty is end of life.
- Update debian/control Standards-Version to 3.9.7.


## v1.0.6 (2018-03-27)

- Removed user config migration code.


## v1.0.5 (2017-10-06)

- Bug fix: In Ubuntu 16.04 and greater, icons for ubuntu-mono-dark and
  ubuntu-mono-light would not load due to directories not present in the
  underlying index.theme file.


## v1.0.4 (2017-05-01)

- Corrected warnings in .desktop file.
- Tidied up tooltips in the Preferences dialog.
- About/Preferences dialogs now block each other - only show one at a time.
- User settings now stored in the directory specified by the environment
  variable XDG_CONFIG_HOME, or, if not present, $HOME/.config (existing user
  settings stored in $HOME are migrated to the new location).
- Update release to trusty as precise is end of life.


## v1.0.3 (2017-02-16)

- Removed superfluous "General" tab from Preferences dialog.


## v1.0.2 (2016-07-24)

- Bug fix: Now uses the X-GNOME-Autostart-enabled tag for autostart.
- Added utf-8 encoding line.
- Fixed PyGIWarnings on imports.
- Overhaul of icons: only the hicolor icon is required and all theme icons are
  created from the hicolor via the build script.
- Overhaul of build script: extracted common functions into a separate script
  used by all indicators.


## v1.0.1 (2016-06-15)

- If a conversion result already exists in the menu, the result is simply moved
  to the top of the menu.
- Removed unnecessary 'Name' translation from .desktop file.
- Added translation capability to 'Unicode' and 'ASCII'.


## v1.0.0 (2016-06-11)

- Initial release - collaboration and inspiration from Oleg Moiseichuk.
