# Indicator Script Runner changelog

## v1.0.25 (2024-09-04)

- Groups may now be copied, includig all scripts within the group.
- Group names may now be changed.
- Groups (and all scripts within) may now be removed.
- Reinstated the autostart option in Preferences with the addition of a optional
  delay to start up.
- Now includes a symbolic icon allowing the colour to be adjusted for the
  current theme.
- Overhauled to adhere to the pyproject.toml standard.
- Deployment using the .deb format is superceded; PyPI (pip) is used with
  operating system packages and file copy.
- Now includes an opt-in check during start up for the latest version at PyPI.


## v1.0.24 (2023-11-08)

- Bug fix: Added missing 'libnotify-bin' and 'pulseaudio-utils' to
  debian/control "Depends".


## v1.0.23 (2023-01-09)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu Unity 22.04


## v1.0.22 (2022-12-04)

- Now works on the following Ubuntu variants/versions...
  - Kubuntu 20.04
  - Kubuntu 22.04
  - Ubuntu 20.04
  - Ubuntu 22.04
  - Ubuntu Budgie 22.04
  - Ubuntu MATE 20.04
  - Ubuntu MATE 22.04
  - Ubuntu Unity 20.04
  - Xubuntu 20.04
  - Xubuntu 22.04
- Limited functionality on the following Ubuntu variants/versions...
  - Lubuntu 20.04 - No label; tooltip is not dynamic (no background scripts).
  - Lubuntu 22.04 - No label; tooltip is not dynamic (no background scripts).
  - Ubuntu Budgie 20.04 - No mouse middle click (no default script).


## v1.0.21 (2022-10-29)

- Code refactor caused base class variables to be uninitialised.


## v1.0.20 (2022-10-29)

- Haphazard cut/paste resulted in missing code.


## v1.0.19 (2022-10-29)

- Increased size of icon to take up entire permissible area.


## v1.0.18 (2022-09-26)

- Workaround for odd focus behaviour; in the Preferences dialog, when switching
  tabs, the TextEntry on the third tab would have the focus and highlight the
  text.  If the user hits the space bar (or any regular key), the text would be
  overwritten. Refer to:

    https://stackoverflow.com/questions/68931638/remove-focus-from-textentry

    https://gitlab.gnome.org/GNOME/gtk/-/issues/4249


## v1.0.17 (2022-06-27)

- Added a preference to write out the full command to the log file when a script
  is executed.


## v1.0.16 (2021-09-30)

- Background script functionality added.  Existing scripts are now referred to
  as non-background scripts and remain functionally as they were.

    A background script contains a command/script, just as a non-background
    script.  Rather than direct execution by the user through the menu, a
    background script is run at a specified interval (in minutes), similarly to
    cron.  The background script must be added to the icon text for the script
    to be run.

    Example: If a background script computes the amount of free memory, the text
    output will always be non-empty.  Enabling the sound and notification
    options for the script are of no value.

    Example: If a background script checks for the presence of a log file (the
    log file representing an exception condition), the script will produce no
    text output if the log file is absent, yet produce non-empty text output if
    the log file is present.  Enabling the sound and notification options for
    the script are of value.

    Each background script is updated according to its respective interval and
    only if the background script has been added to the icon text.  The result
    of the background script is cached and the icon text is updated.

    As background scripts may have different update intervals, one script may
    update and another script will not.  The icon text will be updated using
    both the immediate result from the script which updated and the cached
    result from scripts which did not update (at that time).  If one script
    updates every five minutes and another script updates hourly, the result
    shown in the icon text for the hourly script may be stale due to the cached
    result.  Consequently, a script can be optionally forced to update quicker
    than its specified interval.  This option would typically be used for a
    script which reports exception conditions.


## v1.0.15 (2021-07-15)

- Bug fix: Script Info class constructor had changed and some calls were not
  updated accordingly.


## v1.0.14 (2021-04-05)

- Removed the directory attribute from scripts. Any script which had a directory
  specified now has that value prepended to the corresponding command attribute.
  If a directory need be specified for a (new) script, prepend the following to
  the command:

      "cd /the/directory/you/want ; "

- Update release to bionic as xenial is end of life.


## v1.0.13 (2020-11-05)

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


## v1.0.12 (2020-04-26)

- Added Yaru icon.
- Fixed deprecation warnings.


## v1.0.11 (2019-09-23)

- Bug fix: Dialogs now have a parent specified.
- Now uses a base class to share functionality amongst indicators.
- Whilst starting up, a single menu item "Initialising..." is displayed. Once
  fully initialised, the menu proper is shown.
- When an update is underway or the About/Preferences dialogs are displayed, the
  About/Preferences/Quit menu items are disabled.
- About dialog now shows copyright, artists and corrected URL for website.
- Update debian/compat to 9.


## v1.0.10 (2019-09-20)

- Bug fix: Indentation error.


## v1.0.9 (2019-05-02)

- Correction of text in tooltip in Preferences.
- Corrected the indents for menu items for GNOME Shell.
- Added hyperlink to the About dialog which links to the error log text file
  (only visible if the underlying file is present).
- About dialog now pulls the changelog directly from /usr/share/doc rather than
  a redundant duplicate in the installation directory.
- Tidy up load config of user preferences.
- Update release to xenial as trusty is end of life.
- Update debian/control Standards-Version to 3.9.7.


## v1.0.8 (2018-09-13)

- Bug fix: The terminal flag '--' does not work on Xubuntu/Lubuntu. The terminal
  flag is dynamically set depending on the terminal in use.


## v1.0.7 (2018-03-27)

- Handle the deprecation of the -e option in gnome-terminal and simplify.
  Consequently, gnome-terminal is used (rather than x-terminal-emulator),
  /bin/bash is used (rather than $SHELL) and any text (used for example in the
  notifications) may need to be checked for correct escape characters.
- Removed user config migration code.


## v1.0.6 (2018-01-22)

- When a script was removed, the next script selected would be from the first script of the first group, rather than the first script of the same group, causing confusion when deleting multiple scripts.


## v1.0.5 (2018-01-20)

- Bug fix: Script group names were not being sorted case insensitively,
  resulting in incorrect script group indexes being selected in the Preferences.


## v1.0.4 (2017-10-06)

- Bug fix: In Ubuntu 16.04 and greater, icons for ubuntu-mono-dark and
  ubuntu-mono-light would not load due to directories not present in the
  underlying index.theme file.


## v1.0.3 (2017-05-02)

- Bug fix: Updates were being called twice!
- Corrected warnings in .desktop file.
- Added option to only show script names when scripts are shown grouped.
- About/Preferences dialogs now block each other - only show one at a time.
- User settings now stored in the directory specified by the environment
  variable XDG_CONFIG_HOME, or, if not present, $HOME/.config (existing user
  settings stored in $HOME are migrated to the new location).
- Update release to trusty as precise is end of life.


## v1.0.2 (2016-07-24)

- Bug fix: Now uses the X-GNOME-Autostart-enabled tag for autostart.
- One script can be marked as 'default' and will be executed upon a middle mouse
  click of the indicator icon.
- Each script can optionally play a generic sound and/or display a generic
  notification upon completion.
- Updated the sample scripts to use the generic sound/notification where
  relevant.
- Renamed 'name' to 'group' and 'description' to 'name' to better describe
  scripts and their groupings.  Renamed internally many settings - as a result,
  some user settings may be reset to default.
- Added utf-8 encoding line.
- Fixed PyGIWarnings on imports.
- Overhaul of icons: only the hicolor icon is required and all theme icons are
  created from the hicolor via the build script.
- Overhaul of build script: extracted common functions into a separate script
  used by all indicators.


## v1.0.1 (2016-06-14)

- Bug fix: The sample script for 'update' incorrectly escaped the message in
  notify-send.
- Icon for lubuntu theme was incorrect colour.
- Updated comment of desktop file.


## v1.0.0 (2016-05-23)

- Initial release.
- Many thanks to Oleg Moiseichuk for providing the magic to launch scripts!
