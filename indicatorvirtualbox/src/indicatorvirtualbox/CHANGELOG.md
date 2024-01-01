# Indicator VirtualBox™ changelog

## v1.0.75 (2023-11-22)

- Reinstated the autostart option in Preferences with the addition of a optional delay to start up.
- Overhaul of all indicators to adhere to the pyproject.toml standard.  Further, indicators are no longer deployed using the .deb format.  Rather, PyPI (pip) is now used, along with commands, to install operating system packages and copy files.  In theory, this allows for indicators to be deployed on any platform which supports both pip and the AppIndicator library.
- Now supports Debian 11/12, Fedora 38/39, Manjaro 22.1 GNOME, openSUSE Tumbleweed.


## v1.0.74 (2023-01-09)

- Now works on the following Ubuntu variants/versions...
  - Ubuntu Unity 22.04


## v1.0.73 (2022-12-04)

- Now works on the following Ubuntu variants/versions...
  - Lubuntu 20.04
  - Lubuntu 22.04
  - Ubuntu 20.04
  - Ubuntu 22.04
  - Ubuntu Budgie 22.04
  - Ubuntu MATE 20.04
  - Ubuntu MATE 22.04
  - Ubuntu Unity 20.04
- Limited functionality on the following Ubuntu variants/versions...
  - Kubuntu 20.04 - No mouse wheel scroll.
  - Kubuntu 22.04 - No mouse wheel scroll.
  - Ubuntu Budgie 20.04 - No mouse middle click.
  - Xubuntu 20.04 - No mouse wheel scroll.
  - Xubuntu 22.04 - No mouse wheel scroll.


## v1.0.71 (2022-10-29)

- Increased size of icon to take up entire permissible area.


## v1.0.70 (2022-10-29)

- Bug fix: nested groups were unsorted and additionally, the indicator menu was sorted differently to that in the Preferences dialog. A new preference has been added to either sort groups and virtual machines equally, or instead, sort groups first, then followed by virtual machines.


## v1.0.69 (2021-11-06)

- Bug fix: When bringing a running virtual machine window to front fails (unable to uniquely identify the window), a notification informing the user subsequently failed to display.
- Virtual machine name, UUID and group information now obtained directly from VBoxManage rather than the XML configuration file which is somewhat of a moving target.  As the sort order cannot be obtained from VBoxManage, group names are sorted alphabetically along with machine names.
- Removed the delay inserted on virtual machine autostart if the virtual machine is already running and only needs its window brought to front.


## v1.0.68 (2021-09-30)

- Bug fix: VirtualBox 6 contains "n=GLOBAL" in the configuration file which breaks parsing of the configuration.


## v1.0.67 (2021-09-28)

- Removed support for VirtualBox™ 4 (and earlier) configuration files.
- Update release to bionic as xenial is end of life.


## v1.0.66 (2020-11-05)

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


## v1.0.65 (2020-04-26)

- Added Yaru icon.
- Fixed deprecation warnings.


## v1.0.64 (2020-04-25)

- Tidied up tooltips.


## v1.0.63 (2020-02-01)

- The auto-start delay has been changed to commence BEFORE a VM starts up, rather than after, giving the host time to start up before starting a VM.
- Increased the default time to wait when auto-starting one VM to the next from 5 seconds to 10 seconds.


## v1.0.62 (2019-09-23)

- Bug fix: When a VM hangs during boot the indicator would also hang.
- Bug fix: Dialogs now have a parent specified.
- Now uses a base class to share functionality amongst indicators.
- Whilst starting up, a single menu item "Initialising..." is displayed. Once fully initialised, the menu proper is shown.
- When an update is underway or the About/Preferences dialogs are displayed, the About/Preferences/Quit menu items are disabled.
- About dialog now shows copyright, artists and corrected URL for website.
- Middle mouse click on icon will launch VirtualBox™ Manager.
- Update debian/compat to 9.


## v1.0.61 (2019-05-02)

- Bug fix: The executable for VirtualBox™ may have a different path to that which is ultimately displayed in a process list, rendering the fix in the previous version to show the VirtualBox™ Manager window useless. Instead, add a text field and the user manually specifies the window name.
- Corrected the indents for menu items for GNOME Shell.
- Tidy up load config of user preferences.
- Added hyperlink to the About dialog which links to the error log text file (only visible if the underlying file is present).
- About dialog now pulls the changelog directly from /usr/share/doc rather than a redundant duplicate in the installation directory.
- Update release to xenial as trusty is end of life.
- Update debian/control Standards-Version to 3.9.7.


## v1.0.60 (2019-03-25)

- Bug fix: Handle different locations of the VirtualBox™ executable as it can vary depending on version and method of installation.


## v1.0.59 (2019-01-31)

- Bug fix: Zealous mouse wheel scrolling can cause too many notifications, subsequently popping the graphics stack.


## v1.0.58 (2017-10-23)

- Updated Russian translation.  Thanks to Oleg Moiseichuk.
- Removed user config migration code.


## v1.0.57 (2017-09-30)

- Bug fix: An exception occurred when no VirtualBox™ config file was present.
- Bug fix: In Ubuntu 16.04 and greater, icons for ubuntu-mono-dark and ubuntu-mono-light would not load due to directories not present in the underlying index.theme file.


## v1.0.56 (2017-05-02)

- Support for VirtualBox™ 4.3/5.x or greater.
- Removed the option to alphabetically sort.
- Removed outdated Czech translation.
- About/Preferences dialogs now block each other - only show one at a time.
- User settings now stored in the directory specified by the environment variable XDG_CONFIG_HOME, or, if not present, $HOME/.config (existing user settings stored in $HOME are migrated to the new location).
- Update release to trusty as precise is end of life.


## v1.0.55 (2017-04-18)

- Bug fix: Bringing VirtualBox™ Manager to front only worked in English locales.


## v1.0.54 (2017-03-20)

- Bug fix: Group names in the Preferences dialog inadvertently contained configuration file text "GUI/GroupDefinitions/"


## v1.0.53 (2017-02-10)

- Bug fix: Missing python3-notify2 from the debian/control file. Also added a gi.require_version to the source.


## v1.0.52 (2016-12-28)

- Bug fix: When choosing a VM from the menu which is already running, attempting to bring the window to front would fail if the window name could not be found or multiple names were found.


## v1.0.51 (2016-06-30)

- Bug fix: Now uses the X-GNOME-Autostart-enabled tag for autostart.
- Can use the mouse wheel to scroll through running VMs to successively bring to front their respective window.
- Removed running status information from virtualmachine class - running status for a VM now obtained from VBoxManage as required.
- Changed the delay between (manually) starting a VM to updating the menu from 60s to 10s.
- Changed the delay between clicking OK on the Preferences to updating the menu from 5s to 1s.
- When starting/selecting a VM, if an error occurs, any message will appear in the OSD (and possibly log) rather than in a dialog.
- Removed extra spacing in comments of About dialog.
- Fixed PyGIWarnings on imports.
- Overhaul of icons: only the hicolor icon is required and all theme icons are created from the hicolor via the build script.
- Overhaul of build script: extracted common functions into a separate script used by all indicators.


## v1.0.50 (2016-06-18)

- Updated ru translations - thanks to Oleg Moiseichuk for making these corrections.


## v1.0.49 (2016-06-06)

- Fixed Lintian warnings - added extended description to control file and copyright file now refers to common license file for GPL-3.
- Cleaned up imports.
- Icon for lubuntu theme was incorrect colour.
- Updated comment of desktop file.


## v1.0.48 (2016-02-06)

- Bug fix: Handle previously installed (older) versions of VirtualBox™ which have their config file in a different location.


## v1.0.47 (2015-09-30)

- Bug fix: Handle empty lines when calling "VBoxManage --version". Thanks to Piotr Szuszkiewicz <piotr@szuszkiewi.cz> for the fix!
- Changes to API for showing message dialogs.


## v1.0.46 (2015-07-02)

- Added Czech translation.  Thanks to Filip Oščádal.
- Report to the user (rather than log) when a VM cannot be located.


## v1.0.45 (2015-05-26)

- Bug fix: When a corrupt/missing VM is present, VBoxManage can give back empty results.  All calls now to VBoxManage now handle this situation.
- Bug fix: Omitted the '_' from 'translator-credits' in the About dialog.


## v1.0.44 (2015-05-22)

- Bug fix: The changelog was not added to the debian/rules file.


## v1.0.43 (2015-05-22)

- Bug fix: The changelog path was incorrect.


## v1.0.42 (2015-05-20)

- Bug fix: The test to determine if VBoxManage is installed failed if VBoxManage was not in fact installed!
- Bug fix: If VBoxManage was not installed the Preferences dialog crashed.
- GTK.AboutDialog now uses a Stack rather than Notebook to hold the underlying widgets.  Rather than try to (constantly) reverse engineer the GTK.AboutDialog to retrofit the changelog tab, the default GTK.AboutDialog is used with a hyperlink to the changelog inserted.


## v1.0.41 (2015-05-18)

- Bug fix: When autostarting a VM (or VMs), the time delay of 5 seconds after the VM is started and before updating the menu was insufficient when the host was cold booting.  The delay has been increased to 1 minute to give ample time for the host to start up and VBoxManage to correctly identify running VMs.


## v1.0.40 (2015-05-06)

- Bug fix: Incorrectly calling processes to list/run VMs.
- Bug fix: Incorrectly referring to the VirtualBox™ manage GUI.
- Bug fix: The update interval was reset when starting a VM.


## v1.0.39 (2015-05-02)

- Bug fix: Handle the case when the VirtualBox™ configuration file does not contain any VMs (typically when the user has made no sort order changes via VBoxManage).


## v1.0.38 (2015-04-10)

- Bug fix: Submenus were not correctly rendering the tree of VMs.
- Bug fix: Tree of VMs in the Preferences was not correctly rendered.
- Bug fix: When editing a VM's properties, was testing incorrectly for None.
- Bug fix: When bringing the VirtualBox™ Manager window to front, the name of the window would only work for English.
- Greatly simplified the reading of virtual machine config files.
- Tidy up of tooltips and code clean up.


## v1.0.37 (2015-02-13)

- Internationalisation.  Many thanks to Oleg Moiseichuk who was instrumental in this miracle!
- Added Russian translation.  Thanks to Oleg Moiseichuk. 
- About dialog changed to accept translator information.
- Overhaul of repository structure and build script.


## v1.0.36 (2014-12-25)

- Neatened up the left alignment changelog text in the About dialog.
- Tidied up tooltips and spacing in the Preferences dialog.
- Only show the "groups as submenus" option in the Preferences dialog if groups exist.
- Only show the "sort VMs alphabetically" option in the Preferences dialog if groups do not exist.
- Removed the before/after group text as this was a legacy feature.
- Reorganised the Preferences dialog as per consolidated preferences.


## v1.0.35 (2014-07-08)

- Bug fix: Handle 'add_credit_section' on Ubuntu 12.04 (was causing a segmentation fault).


## v1.0.34 (2014-06-12)

- Removed legacy code to support old appindicator framework.
- New log handler which truncates the log file to 10,000 bytes.


## v1.0.33 (2014-06-09)

- It has become apparent the VirtualBox™ configuration file can exist in different places, sometimes simultaneously, depending on the version of VirtualBox™.  Now handles the different cases...hopefully!
- Handle a warning message from VBoxManage when obtaining a list of VMs.


## v1.0.32 (2014-06-07)

- The VirtualBox™ configuration file is now located in .config directory. Updated internals to handle the change.


## v1.0.31 (2014-03-15)

- Fixed a bug where non-toggle buttons (the close button) were having the toggled signal set.
- Put in a fix for Ubuntu 12.04 (Python 3.2) which does not handle AboutDialog::add_credit_section().


## v1.0.30 (2014-03-01)

- The VM properties dialog was not cancelling!


## v1.0.29 (2014-03-01)

- Changed checking of Gtk.ResponseType.CANCEL to Gtk.ResponseType.OK as it was possible to simulate Gtk.ResponseType.OK by hitting the escape key.


## v1.0.28 (2014-02-28)

- Fixed typo in delay preference - the value is in seconds, not minutes.
- VM edit dialog now has focus when displayed.


## v1.0.27 (2014-02-27)

- Neglected to update the install file!


## v1.0.26 (2014-01-27)

- Removed duplicate showMessage function.
- Uses AboutDialog and showMessage from common library.
- Moved virtual machine information into a separate file.


## v1.0.25 (2013-12-17)

- Created a new About dialog showing the changelog.


## v1.0.24 (2013-12-15)

- Updated the About dialog to use Gtk+ 3.


## v1.0.23 (2013-12-02)

- If the list of VMs in the Preferences is less than or equal to 15, don't add a vertical scrollbar.
- Made the text field containing the start command wide enough to display the start command.


## v1.0.22 (2013-11-17)

- Put the list of VMs in the Preferences into a scrolled window.


## v1.0.21 (2013-10-13)

- Put in a refresh to ensure the list of VMs is updated when the preferences are displayed.
- Put in a delay between each VM starting up.


## v1.0.20 (2013-10-01)

- In Ubuntu 13.10 the initial value set by the spinner adjustment was not appearing in the spinner field. Need to force the initial value by explicitly setting it.


## v1.0.19 (2013-07-05)

- Only create the log file when needed. Thanks to Rafael Cavalcanti <rafael.kavalkanti@gmail.com>.


## v1.0.18 (2013-04-15)

- Only brings up one VirtualBox™ manager at a time.
- User can customise the launch command for a VM, allowing VBoxHeadless to be used instead of VBoxManage.
- User can set a VM to automatically start when the indicator starts. Each VM will start up before the indicator displays, with a five second delay between each VM.
- Now logs to a file in the user's HOME directory.
- Attempt to bring about/preferences to front.


## v1.0.17 (2013-04-10)

- Replaced deprecated GObject calls with GLib.
- Icons for Preferences/About now show for Lubuntu/Xubuntu.


## v1.0.16 (2012-11-16)

- Added python3-gi to debian/control Depends (for Precise support).
- Swapped out python-appindicator for gir1.2-appindicator3-0.1 in debian/control Depends.
- Simpler handling for creating the indicator - should hopefully sustain more environments.


## v1.0.15 (2012-11-06)

- Changes for Python3 and PyGObject.
- Now supports VirtualBox™ 4.2 and specifically groups.
- Handle the case when VirtualBox™ is not installed.
- Handle the case when VirtualBox™ is installed but has not yet been run (and so $HOME/.VirtualBox/VirtualBox.xml does not exist).
- Moved the preferences into a tabbed view.
- Now uses a radio button to indicate a running VM as standard. Removed the (legacy) show text before/after a VM.
- Added option to show text before/after a group name.
- Known issue: If a VM exists in a group (and there is another VM of the same name but not in a group) and you ungroup, the VM in the group is not removed from the group.  This appears to be a bug in the VirtualBox™ UI and as such the indicator displays the VM (from the group) alongside the other VMs.


## v1.0.14 (2012-09-24)

- Addresses the case in which a VM which has been renamed/deleted and is selected in the menu but a refresh has not occurred.


## v1.0.13 (2012-08-25)

- Fixed the menu (incorrectly initialised) which caused a crash under GTK (non Unity).
- Removed duplicate preferences menu item.


## v1.0.12 (2012-08-24)

- Noted that memory was leaking - strongly suspect it was due to removing/adding menu items on each update.  As a result, the menu is now completely rebuilt on each update.  Unfortunately, if the preferences/about dialogs are showing during an update, the warning "Trying to remove a child that doesn't believe we're it's parent" is emitted, which appears to be benign.


## v1.0.11 (2012-08-07)

- Handle the case where the directory ~/.config/autostart does not exist.


## v1.0.10 (2012-07-27)

- Fixed the PPA URL in the About dialog.
- Consolidated all options into a preferences dialog.
- Default sort now matches that given by the VirtualBox™ UI (rather than VBoxManage).
- The update of the running status of the VMs in the menu is now configurable between 1 and 60 minutes.  Note that an update also occurs each time a VM is started and when the preferences dialog is ok'd/cancelled.
- Big thanks to Pascal De Vuyst (https://launchpad.net/~pascal-devuyst) for suggestions/patches for preferences and sorting!


## v1.0.9 (2012-07-27)

- On selecting a VM which is already running, the VM window is brought to the front (using wmctrl).
- Removed the refresh menu item.  The list of VMs in the menu are now automatically refreshed every 15 minutes.
- Fixed an issue where the indicator believes a VM is running but is in fact not.


## v1.0.8 (2012-07-25)

- Changed the build process to use a single PPA.


## v1.0.7 (2012-07-16)

- Added option to use the "radio" indicator to flag running VMs.


## v1.0.6 (2012-07-13)

- Hide the menu during refresh (using popdown). 
- Renamed menu item 'Frontend' to be 'VirtualBox™'...makes more sense.


## v1.0.5 (2012-07-10)

- Added menu option to add before/after text to the virtual machine menu items.


## v1.0.4 (2012-07-10)

- Added menu option to sort virtual machine names alphabetically or by default (as given by VirtualBox™).


## v1.0.3 (2012-07-09)

- Added menu option to launch the GUI frontend.
- Fixed a bug when displaying a message when no virtual machines exist.


## v1.0.2 (2012-07-07)

- Unity appindicator does not support styling in the menu items. To indicate a running VM "---" is placed either side of the VM name.


## v1.0.1 (2012-07-07)

- The bold/italic tags are not being rendered in the menu to indicate a running VM.  For now, will use "---" either side of the VM name.


## v1.0.0 (2012-07-07)

- Initial release.
- Tested on Ubuntu but should work for Lubuntu/Xubuntu.
- On Lubuntu/Xubuntu, user needs to manually remove spurious directory

        /usr/share/icons/elementary/status/48/untitled

    then rebuild the image cache

        sudo gtk-update-icon-cache -f /usr/share/icons/elementary

- If 'Unable to locate theme engine in module_path: "pixmap"' appears on execution, install "sudo apt-get install gtk2-engines-pixbuf".
- The indicator will run without VirtualBox™ installed...but it'll do nothing useful!
