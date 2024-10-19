# Indicator PPA Download Statistics changelog

## v1.0.81 (2024-09-04)

- Reinstated the autostart option in Preferences with the addition of a optional delay to start up.
- Added plucky to the list of series.
- Added oracular to the list of series.
- Now includes a symbolic icon allowing the colour to be adjusted for the current theme.
- Overhaul of all indicators to adhere to the pyproject.toml standard.  Further, indicators are no longer deployed using the .deb format.  Rather, PyPI (pip) is now used, along with commands, to install operating system packages and copy files.  In theory, this allows for indicators to be deployed on any platform which supports both pip and the AyatanaAppIndicator3 / AppIndicator3 library.
- Now includes an opt-in check during indicator start up for the latest version at PyPI.


## v1.0.80 (2023-01-09)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu Unity 22.04
- Added noble to the list of series.
- Added mantic to the list of series.


## v1.0.79 (2022-12-04)

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
- Changed default series from focal to jammy.


## v1.0.78 (2022-10-29)

- Code refactor caused base class variables to be uninitialised.


## v1.0.77 (2022-10-29)

- Increased size of icon to take up entire permissible area.
- Added lunar to the list of series.


## v1.0.76 (2022-06-22)

- The debian/compat file had version 11 whereas should have been version 10 which caused build problems.


## v1.0.75 (2022-06-21)

- Increased URL timeout from 5 seconds to 20 seconds.
- Added kinetic to the list of series.


## v1.0.74 (2021-10-16)

- Updated LaunchPad PPA URL to include "ubuntu".
- PPA menu items now have a more specific URL.
- Added impish to the list of series.
- Added jammy to the list of series.
- Update release to bionic as xenial is end of life.


## v1.0.73 (2020-11-05)

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


## v1.0.72 (2020-10-25)

- Added hirsute to the list of series.


## v1.0.71 (2020-04-27)

- Changed the icon as it was difficult to read on Ubuntu 20.04.
- Fixed deprecation warnings.


## v1.0.70 (2020-04-26)

- Added Yaru icon.
- Changed default series from bionic to focal.
- Fixed deprecation warnings.


## v1.0.69 (2020-04-24)

- Added groovy to the list of series.


## v1.0.68 (2019-12-17)

- Added an option to reduce the network access when on low bandwidth.
- Removed code which bridged the change in filter format.


## v1.0.67 (2019-09-23)

- Bug fix: When no config was present, some variables were not initialised.
- Bug fix: Dialogs now have a parent specified.
- Removed somewhat redundant notification.
- Filters now match to a full PPA (user, name, series and architecture).
- Now uses a base class to share functionality amongst indicators.
- Whilst starting up, a single menu item "Initialising..." is displayed. Once fully initialised, the menu proper is shown.
- When an update is underway or the About/Preferences dialogs are displayed, the About/Preferences/Quit menu items are disabled.
- About dialog now shows copyright, artists and corrected URL for website.
- Added focal to the list of series.
- Update debian/compat to 9.


## v1.0.66 (2019-06-26)

- For Unity, the icon has been changed to an empty icon and uses "PPA" in the label text to match other indicators with a label. No change for GNOME Shell as empty icons are treated as full size.
- Added hyperlink to the About dialog which links to the error log text file (only visible if the underlying file is present).
- About dialog now pulls the changelog directly from /usr/share/doc rather than a redundant duplicate in the installation directory.
- Corrected the indents for menu items for GNOME Shell.
- Tidy up load config of user preferences.


## v1.0.65 (2019-05-02)

- Update release to xenial as trusty is end of life.
- Update debian/control Standards-Version to 3.9.7.
- Added eoan to the list of series.
- When only one PPA is present, enable middle mouse click on the icon to open the PPA in the browser.


## v1.0.64 (2019-03-27)

- Testing...ignore!


## v1.0.63 (2018-12-19)

- Added a URL timeout when attempting downloads.


## v1.0.62 (2018-05-13)

- Added disco to the list of series.
- Changed default series from xenial to bionic.
- Bug fix: Removed duplicate 'utopic' from list of series.


## v1.0.61 (2017-11-19)

- Added cosmic to the list of series.
- Removed redundant check for results in the thread pool executer.
- Now checks for an internet connection before downloading PPA data. This stops the log file cluttering up with failed connection messages.
- Removed user config migration code.


## v1.0.60 (2017-10-21)

- Added bionic to the list of series.
- Added Czech translation.  Thanks to Pavel Rehak.
- Updated Russian translation.  Thanks to Oleg Moiseichuk.


## v1.0.59 (2017-10-03)

- Bug fix: Downloading within a PPA ended prematurely.
- Bug fix: In Ubuntu 16.04 and greater, icons for ubuntu-mono-dark and ubuntu-mono-light would not load due to directories not present in the underlying index.theme file.


## v1.0.58 (2017-05-02)

- Bug fix: When multiple filters were in use, if one filter resulted in no matches, all other filters became redundant.
- Corrected warnings in .desktop file.
- About/Preferences dialogs now block each other - only show one at a time.
- Added a drop shadow to the icon.
- Update release to trusty as precise is end of life.


## v1.0.57 (2017-02-16)

- Added artful to list of series.
- The download notification is shown at most once every six hours, hence the option to hide/show has been removed.  The notification will be shown (as usual) when the download statistics differ between updates.
- Clicking on any PPA item opens that item's PPA page in a web browser. The option to turn on/off this feature has been removed and the feature is permanently enabled.


## v1.0.56 (2016-07-24)

- Bug fix: Now uses the X-GNOME-Autostart-enabled tag for autostart.
- Added zesty to list of series.
- Added utf-8 encoding line.
- Fixed PyGIWarnings on imports.
- Overhaul of icons: only the hicolor icon is required and all theme icons are created from the hicolor via the build script.
- Overhaul of build script: extracted common functions into a separate script used by all indicators.


## v1.0.55 (2016-06-18)

- Added indicator-punycode and indicator-script-runner to list of default filters.
- Removed parentheses from around version numbers to increase readability.


## v1.0.54 (2016-06-06)

- Added spacing to each download count menu item to increase readability.
- Fixed Lintian warnings - added extended description to control file and copyright file now refers to common license file for GPL-3.
- Updated comment of desktop file.


## v1.0.53 (2016-04-19)

- Added yakkety to list of series.
- Added indicator-tide to the sample filter.
- Made the default PPA xenial.


## v1.0.52 (2015-09-30)

- Bug fix: When a filter was added which resulted in no published binaries, subsequent entries within a PPA were lost.
- Changes to API for showing message dialogs.
- Added "xenial" to list of series.


## v1.0.51 (2015-05-26)

- Bug fix: Omitted the '_' from 'translator-credits' in the About dialog.


## v1.0.50 (2015-05-22)

- Bug fix: The changelog was not added to the debian/rules file.


## v1.0.49 (2015-05-22)

- Bug fix: The changelog path was incorrect.


## v1.0.48 (2015-05-20)

- GTK.AboutDialog now uses a Stack rather than Notebook to hold the underlying widgets.  Rather than try to (constantly) reverse engineer the GTK.AboutDialog to retrofit the changelog tab, the default GTK.AboutDialog is used with a hyperlink to the changelog inserted.


## v1.0.47 (2015-04-10)

- Added 'wily' to list of series.
- Tidy up of tooltips and code clean up.


## v1.0.46 (2015-02-13)

- Internationalisation.  Many thanks to Oleg Moiseichuk who was instrumental in this miracle!
- Added Russian translation.  Thanks to Oleg Moiseichuk.
- About dialog changed to accept translator information.
- Overhaul of repository structure and build script.


## v1.0.45 (2014-12-26)

- Added 'vivid' to the list of series.


## v1.0.44 (2014-12-25)

- Neatened up the left alignment changelog text in the About dialog.
- Added spacing and tidied tooltips in the Preferences dialog.


## v1.0.43 (2014-08-11)

- Now shows the screen notification only if there is a difference in the statistics between downloads.


## v1.0.42 (2014-08-10)

- Fixed a bug: The download status was sometimes obscured if filtering was enabled.


## v1.0.41 (2014-08-09)

- Fixed a bug: When a PPA had more than one filter, the results were completely filtered out.


## v1.0.40 (2014-07-21)

- Now passes filter text to the URL which retrieves the published binary information...results in much faster download for large PPAs!


## v1.0.39 (2014-07-08)

- Bug fix: Handle 'add_credit_section' on Ubuntu 12.04 (was causing a segmentation fault).


## v1.0.38 (2014-06-12)

- Updated some labels/tooltips in the user preferences dialog.
- New log handler which truncates the log file to 10,000 bytes.
- Removed legacy code to support old appindicator framework.


## v1.0.37 (2014-05-01)

- Added 'utopic' to list of series.
- Fixed blocking of preferences - when a download is underway the preferences cannot be opened.


## v1.0.36 (2014-03-15)

- Set autoupdate to every 6 hours to not burden LaunchPad.


## v1.0.35 (2014-03-15)

- Fixed a bug where non-toggle buttons (the close button) were having the toggled signal set.
- Put in a fix for Ubuntu 12.04 (Python 3.2) which does not handle AboutDialog::add_credit_section().
- Fixed quit during download (was causing a core dump).


## v1.0.34 (2014-03-07)

- Now lets the user quit the indicator during the download.
- Changed the default PPA series to Trusty.


## v1.0.33 (2014-03-04)

- Fixed a bug: after hitting OK on preferences, only do a download if the ppas/filters have been modified.


## v1.0.32 (2014-03-04)

- Fixed a bug: after modifying ppas/filters, a download is kicked off. If the user opens the preferences before the download starts, the download is aborted.  Now the download is scheduled later.


## v1.0.31 (2014-03-03)

- Fixed a bug when saving preferences and rebuilding the menu.


## v1.0.30 (2014-02-19)

- Uses AboutDialog and showMessage from common library.
- Adding filtering of PPA packages.  A filter comprises one or more strings, on a per PPA user/name basis, used to match package names.  A matched package name is kept whereas unmatched package names are dropped. Filters are applied at download time.
- Added a notification option for when statistics have been updated.
- Added an option when combining PPAs on how to handle versions for architecture specific packages.
- Moved the add/edit/remove of PPAs into the preferences dialog.
- Now uses icons for ubuntu-mono-dark and ubuntu-mono-light rather than text and hicolor icon.


## v1.0.29 (2013-12-17)

- Created a new About dialog showing the changelog.


## v1.0.28 (2013-12-07)

- Added 'trusty' to list of series.
- Updated the About dialog to use Gtk+ 3.


## v1.0.27 (2013-11-01)

- Changed text/tooltip for checkbox to open a PPA in a browser.
- In Ubuntu 13.10 the initial value set by the spinner adjustment was not appearing in the spinner field. Need to force the initial value by explicitly setting it.


## v1.0.26 (2013-10-23)

- Ubuntu 13.10 requires an icon to be set - now uses a dynamically created 1 pixel SVG icon (resides in the user's HOME directory).


## v1.0.25 (2013-07-05)

- Added a new message type when PPAs are combined.  When anything other than statistics appear in the results, write out a warning message to the user so the user can uncombine PPAs to see individual messages.
- Added all series of Ubuntu (including those no longer supported).
- Only create the log file when needed. Thanks to Rafael Cavalcanti <rafael.kavalkanti@gmail.com>.


## v1.0.24 (2013-05-15)

- Fixed a bug when a PPA was changed and the PPA download data was still under the old PPA.
- Added 'saucy' and all removed unsupported series.


## v1.0.23 (2013-05-04)

- Now logs to a file in the user's HOME directory.
- Attempt to bring about/preferences to front.
- Placed autostart preference at bottom of preferences dialog to be consistent with other indicators.
- Removed redundant onAutoStart function.


## v1.0.22 (2013-04-10)

- Icons for Add/Edit now show for Lubuntu/Xubuntu.


## v1.0.21 (2013-04-10)

- Icons for Preferences/About now show for Lubuntu/Xubuntu.


## v1.0.20 (2013-02-25)

- Replaced deprecated GObject calls with GLib.
- Better handling when the download count is not a number.
- Simplify the thread locking during downloads.


## v1.0.19 (2013-01-17)

- Now handles the retrieval of result sets larger than 75.
- Changed the initial (no information...) text to (downloading data...).
- Added option to sort within each PPA by download amount (and truncate the results).
- Thanks to Boaz Dodin for spotting the bug and suggesting the truncate/sort.


## v1.0.18 (2012-12-20)

- Using threads for each statistic sometimes results in the package names being out of (alphabetical) order...now fixed.
- Added logging to exceptions.


## v1.0.17 (2012-12-18)

- Fixed the add/edit PPA dialog to show the correct title (was erroneously showing "Preferences").
- Uses multiple threads to do the download...now significantly faster!


## v1.0.16 (2012-12-01)

- When PPAs were combined, the "no information" message was shown regardless if the situation was no information or an error in downloading the PPA.
- Removed natty from the list of PPAs.
- Changed the sample PPA series to Precise as it's supported for 5 years.


## v1.0.15 (2012-11-27)

- Modified the download counts for architecture independent binary packages. If a binary package exists in two (or more) places but has different versions, the download count for each binary package is counted (for the first instance of a given version number).  This means that different versions are treated as separate packages but are still combined under the common name.


## v1.0.14 (2012-11-22)

- Add a combine PPA option which combines the statistics when the PPA user/name are the same. If a published binary is architecture specific (such as compiled C), the download count is summed across all instances of that published binary. If a published binary is not architecture specific (such as Python), the download count is not summed (as it is assumed to be the same binary). The version number is retained only if it is identical across all instances of a published binary.


## v1.0.13 (2012-11-19)

- Fixed warning when updating the menu and GTK complains of missing child.


## v1.0.12 (2012-11-19)

- Was only updating the menu for a specific case in the preferences - now fixed!


## v1.0.11 (2012-11-16)

- Added python3-gi to debian/control Depends (for Precise support).
- Swapped out python-appindicator for gir1.2-appindicator3-0.1 in debian/control Depends.
- Simpler handling for creating the indicator - should hopefully sustain more environments.


## v1.0.10 (2012-10-24)

- Changes for Python3 and PyGObject.
- Dropped requirement for launchpadlib - now makes a direct call for statistics.  Many thanks to Barry Warsaw (https://launchpad.net/~barry) for the suggestion and pointers in the right direction!
- Added raring to series list and removed unsupported series.


## v1.0.9 (2012-08-26)

- Constant removing/adding of menu items was leaking memory, so combined menu build/rebuild methods.  Still get the (presumed benign) warning "Trying to remove a child that doesn't believe we're it's parent" warning.
- Now logs in once to LaunchPad - each login uses an excessive amount of memory.


## v1.0.8 (2012-08-09)

- Fixed a bug where the PPA owner/name was not preselected when editting.


## v1.0.7 (2012-08-09)

- Add/Edit of PPAs shows current PPA owners/names to save typing.
- Selecting a PPA or PPA child from the menu launches the browser to the PPA page.
- Preferences now contained within a dialog.


## v1.0.6 (2012-08-07)

- Handle the case where the directory ~/.config/autostart does not exist.


## v1.0.5 (2012-07-27)

- Fixed the PPA URL in the About dialog.


## v1.0.4 (2012-07-25)

- Changed the sample PPA to reflect the new single PPA.
- The GtkWarning 'IA__gtk_widget_event' no longer appears (fixed from previous release).
- Changed the build process to use a single PPA.


## v1.0.3 (2012-07-13)

- Hide the menu during refresh (using popdown).
- Added the PPA for VirtualBox Indicator to the sample PPAs.


## v1.0.2 (2012-07-10)

- Fixed a bug where the add/edit dialog was not preventing other dialogs from being launched.


## v1.0.1 (2012-07-07)

- Put in spacing either side of the "PPA" text for Ubuntu Unity.
- Removed incorrect setting of stock icon.
- Simplified the menu build/update.
- Updated comment for a warning on Lubuntu.
- Removed borders of icons.


## v1.0.0 (2012-07-04)

- Initial release.
- Tested on Ubuntu and Lubuntu.

