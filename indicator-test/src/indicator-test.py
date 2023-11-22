#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Application indicator to test stuff.


#TODO Future work...
# Port indicators to Ubuntu variants:
#    https://www.linuxmint.com/
#    https://www.bodhilinux.com/
#    https://elementary.io/
#    https://zorin.com/os/
#    https://www.ubuntukylin.com/downloads/download-en.html
#
# Port indicators to non-Ubuntu but GNOME based variants...
#    https://www.ubuntupit.com/best-gnome-based-linux-distributions/
#    https://www.fosslinux.com/43280/the-10-best-gnome-based-linux-distributions.htm
#
# Is it possible to port to FreeBSD and/or NetBSD?
#
# Miscellaneous:
#    https://blog.tingping.se/2019/09/07/how-to-design-a-modern-status-icon.html
#    https://itsfoss.com/enable-applet-indicator-gnome/
#
# External hosting of source code and deployment other than PPA...
#    https://github.com/alexmurray/indicator-sensors
#    https://yktoo.com/en/software/sound-switcher-indicator/#installation
#    https://snapcraft.io/about
#    https://flathub.org/home
# What about SourceForge?  Still uses SVN which is a good thing.
# Are the download stats available through an API?
# If so, add/amend the PPA Download Statistic indicator.
# https://sourceforge.net/p/forge/documentation/Download%20Stats%20API/


#TODO Single version number location
#   https://packaging.python.org/en/latest/guides/single-sourcing-package-version/
#   https://stackoverflow.com/questions/72357031/set-version-of-module-from-a-file-when-configuring-setuptools-using-setup
#   https://stackoverflow.com/questions/60430112/single-sourcing-package-version-for-setup-cfg-python-projects


#TODO Shared project layout
#   https://stackoverflow.com/questions/18087122/python-sharing-common-code-among-a-family-of-scripts
#   https://stackoverflow.com/questions/73580708/how-to-share-code-between-python-internals-projects
#   https://stackoverflow.com/questions/48954870/how-to-share-code-between-python-projects
#   https://discuss.python.org/t/multiple-related-programs-one-pyproject-toml-or-multiple-projects/17427/2


#TODO Packaging
#   https://setuptools.pypa.io/en/latest/setuptools.html
#   https://packaging.python.org/en/latest/
#   https://pypa-build.readthedocs.io/en/stable/
#   https://ianhopkinson.org.uk/2022/02/understanding-setup-py-setup-cfg-and-pyproject-toml-in-python/
#   http://ivory.idyll.org/blog/2021-transition-to-pyproject.toml-example.html
#   https://stackoverflow.com/questions/7110604/is-there-a-standard-way-to-create-debian-packages-for-distributing-python-progra
#   https://www.wefearchange.org/2010/05/from-python-package-to-ubuntu-package.html
#   https://stackoverflow.com/questions/63304163/how-to-create-a-deb-package-for-a-python-project-without-setup-py
#   https://stackoverflow.com/questions/1382569/how-do-i-do-debian-packaging-of-a-python-package?rq=3
#   https://stackoverflow.com/questions/72352801/migration-from-setup-py-to-pyproject-toml-how-to-specify-package-name
#   https://manpages.debian.org/unstable/dh-python/pybuild.1.en.html
#   https://stackoverflow.com/questions/64345965/how-can-i-debian-package-a-python-application-with-a-systemd-unit-using-stdeb3-p
#   https://stackoverflow.com/questions/76208149/build-python-debian-package-with-setuptools
#   https://stackoverflow.com/questions/63304163/how-to-create-a-deb-package-for-a-python-project-without-setup-py
#   https://discuss.python.org/t/looking-for-an-up-to-date-step-by-step-guide-to-create-a-deb-from-a-python-package/15766/4
#   https://www.debian.org/doc/packaging-manuals/python-policy/
#   https://pypi.org/project/wheel2deb/
#   https://github.com/upciti/wheel2deb/issues/54
#   https://stackoverflow.com/questions/12079607/make-virtualenv-inherit-specific-packages-from-your-global-site-packages
#   https://stackoverflow.com/questions/71976246/how-add-default-packages-to-all-new-pythons-venvs
#   https://stackoverflow.com/questions/70272023/using-pyproject-toml-with-flexible-version-from-datetime
#   https://stackoverflow.com/questions/75526020/dynamically-version-a-pyproject-toml-package-without-importing-runtime-dependenc
#   https://stackoverflow.com/questions/74608905/single-source-of-truth-for-python-project-version-in-presence-of-pyproject-toml
#   https://stackoverflow.com/questions/76041299/using-values-generated-by-python-scripts-in-dynamic-fields-in-pyproject-toml
#   https://stackoverflow.com/questions/76081078/using-the-return-value-of-a-python-function-as-the-value-for-version-field-in-py


#TODO Good background on Python build/env
#   https://chriswarrick.com/blog/2023/01/15/how-to-improve-python-packaging/
#   https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html
#   https://sinoroc.gitlab.io/kb/python/package_data.html


#TODO i18n
# https://discuss.python.org/t/how-to-package-translation-files-po-mo-in-a-future-proof-way/20096
# https://stackoverflow.com/questions/22958245/what-is-the-correct-way-to-include-localisation-in-python-packages
# https://stackoverflow.com/questions/53285634/is-there-a-portable-way-to-provide-localization-of-a-package-distributed-on-pypi?noredirect=1&lq=1
# https://github.com/s-ball/mo_installer
# https://stackoverflow.com/questions/55365356/how-to-include-localized-message-in-python-setuptools?noredirect=1&lq=1
# https://stackoverflow.com/questions/34070103/how-to-compile-po-gettext-translations-in-setup-py-python-script
# https://stackoverflow.com/questions/34070103/how-to-compile-po-gettext-translations-in-setup-py-python-script
#
# May be of use too for i18n
# https://github.com/thinkle/gourmet/blob/master/setup.py
# https://github.com/PythonOT/POT/blob/master/setup.py
# https://github.com/moinwiki/moin/blob/master/setup.py
# https://github.com/GourmandRecipeManager/gourmand/blob/main/setup.py
#
# https://www.mattlayman.com/blog/2015/i18n/
#
# https://stackoverflow.com/questions/32609248/setuptools-adding-additional-files-outside-package


#TODO
# Should the src directory be replaced with src/indicator-test?
# Hopefully will be okay as is...but maybe snap et al require it?


#TODO Still need __init__.py given now using pyproject.toml AND will likely never be installing via Pip?
# Based on this, yes:
#    https://stackoverflow.com/a/48804718/2156453
#
# Also from distutils introduction link above:
#
#    package
#        a module that contains other modules; typically contained in a directory in the filesystem
#        and distinguished from other directories by the presence of a file __init__.py.


#TODO AppImage
# https://appimage.org/


#TODO Flathub
# https://github.com/PlaintextGroup/oss-virtual-incubator/blob/main/proposals/flathub-linux-app-store.md


#TODO Snap
#   https://snapcraft.io/docs/python-apps
#   https://forum.snapcraft.io/t/parse-info-on-pythonpart-utilizing-pyproject-toml/33294
#   https://forum.snapcraft.io/t/building-a-core20-python-snap-using-pyproject-toml/22028
#   https://stackoverflow.com/questions/73310069/should-i-be-using-only-pyproject-toml
#   https://stackoverflow.com/questions/72352801/migration-from-setup-py-to-pyproject-toml-how-to-specify-package-name
#   https://stackoverflow.com/questions/71193095/questions-on-pyproject-toml-vs-setup-py
#   https://stackoverflow.com/questions/62983756/what-is-pyproject-toml-file-for
#   https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
#   https://pypi.org/project/poetry2setup/


#TODO Debian install from PPA
#   https://unix.stackexchange.com/questions/248367/how-to-install-ppas-from-launchpad-on-non-ubuntu-distros-like-debian


#TODO 
# Look at sound-switcher which does several interesting things...
#    https://yktoo.com/en/software/sound-switcher-indicator/#installation
#
#    Autostart indicator...how does it do this?
#
#    Creates snap and other packages for deployment.
#
#    It tries first to import AyatanaAppIndicator3.
#
# https://snapcraft.io/docs/snapcraft-overview
#
# https://askubuntu.com/questions/40011/how-to-let-dpkg-i-install-dependencies-for-me
# https://askubuntu.com/questions/1090826/deb-package-cant-install-its-dependencies-when-using-dpkg
#
# https://github.com/yktoo/indicator-sound-switcher/blob/dev/debian/control
# https://github.com/yktoo/indicator-sound-switcher/blob/dev/snap/local/launch.sh
#
# For autostart with a snap, see how this works...need to do something different?


#TODO May be useful in indicatorbase for finding user dirs and similar in a os-independent manner:
#   https://pypi.org/project/platformdirs/


#TODO When installing indicator-lunar on Debian bookworm, got an error:
#
#     error: externally-managed-environment
#
#     × This environment is externally managed
#     ╰─> To install Python packages system-wide, try apt install
#     python3-xyz, where xyz is the package you are trying to
#     install.
#
#     If you wish to install a non-Debian-packaged Python package,
#     create a virtual environment using python3 -m venv path/to/venv.
#     Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
#     sure you have python3-full installed.
#
#     If you wish to install a non-Debian packaged Python application,
#     it may be easiest to use pipx install xyz, which will manage a
#     virtual environment for you. Make sure you have pipx installed.
#
#     See /usr/share/doc/python3.11/README.venv for more information.
#
#     note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
#     hint: See PEP 668 for the detailed specification.
#
# This will affect Ubuntu 24.04 onward as Pip has been changed such that
# Python packages need to be installed into a virtual environment.
#
# So for ephem/sgp4 and eventually skyfield, need to make a change.
# 
#   https://stackoverflow.com/a/75696359/2156453
#
# Perhaps in the debian/postinst all we need to do is modify
#   sudo pip3 install --ignore-installed --upgrade ephem sgp4 || true
# to be instead something that can do the following...
#   
#    71  cd /home/bernard
#    72  python3 -m venv .venv
#    73  sudo apt install python3.11-venv 
#    74  python3 -m venv .venv
#    75  source .venv/bin/activate
#    76  python3 -m pip install --upgrade pip
#    77  cd Programming/PlayListMaker/
#    78  python3 -m pip install -e .
#    79  playlistmaker 
#
# More on this issue
#   https://stackoverflow.com/questions/76873955/pip-install-user-doesnt-work-on-debian-12
#   https://stackoverflow.com/questions/76465606/why-is-pip3-9-trying-to-use-the-debian-12-python3-11
#   https://stackoverflow.com/questions/75608323/how-do-i-solve-error-externally-managed-environment-every-time-i-use-pip-3
#   https://stackoverflow.com/questions/75602063/pip-install-r-requirements-txt-is-failing-this-environment-is-externally-mana
#   https://stackoverflow.com/questions/77253338/best-practice-using-python-packages-not-developing-on-debian-12
#   https://www.reddit.com/r/debian/comments/14g9np9/debian_12_pip_makes_trouble/
#   https://stackoverflow.com/questions/64005822/how-to-specify-external-system-dependencies-to-a-python-package
#   https://stackoverflow.com/questions/5729051/python-package-external-dependencies?rq=3
#   https://stackoverflow.com/questions/55293003/how-to-handle-external-dependencies-in-python
#
# If the postinst will no longer work in kicking off an install to a venv,
# will have to do a runtime check in the indicator to look for ephem et al
# and if not present, explain to the user how to install via pip into a venv.
#
# If the postinst does work, likely need a postrm to clean up the pip installation.
#
#
# Maybe go with a modified postinst (and a new postrm) but ALSO have a runtime check
# to ensure ephem et al are installed and if not, point user to a readme on how to install
# (but at this stage if ephem is not present, the installation should be assumed to be broken).
#
# How permanent is a venv?  Do we need a venv for each indicator as needed,
# and even then one for each version of each indicator?
#
# Can Python script in /usr/share/indicator-lunar refer to a Python library in a venv?
# Need the full path to the venv?


#TODO What about support for other Linux distributions?  Do I build an equivalent .deb for these?
#   https://en.wikipedia.org/wiki/Arch_Linux
#
#   https://en.wikipedia.org/wiki/Fedora_Linux
#   https://stackoverflow.com/questions/59248180/how-to-install-rpmdev-tools-on-ubuntu
#   https://superuser.com/questions/615023/how-to-build-rpm-package-correctly
#   https://stackoverflow.com/questions/29038961/how-can-i-build-an-rpm-package-in-a-debian-based-system
#   https://rpm-packaging-guide.github.io/#packaging-software
#   https://blog.jwf.io/2017/11/first-rpm-package-fedora/
#   https://rpm-guide.readthedocs.io/en/latest/index.html
#   https://discuss.python.org/t/tool-to-build-a-rpm-package-backed-by-pep-517/4020/14
#   https://stackoverflow.com/questions/42286786/how-to-create-a-rpm-for-python-application
#   https://rpm.org/documentation.html
#   https://refspecs.linuxbase.org/LSB_4.1.0/LSB-Core-generic/LSB-Core-generic/pkgformat.html
#   https://opensource.com/article/18/9/how-build-rpm-packages
#   https://www.howtoforge.com/tutorial/how-to-convert-packages-between-deb-and-rpm/
#   https://developers.redhat.com/blog/2019/03/18/rpm-packaging-guide-creating-rpm#creating_the_rpm_package_for_vitetris
#   https://www.reddit.com/r/Fedora/comments/trwdok/new_to_fedora_how_to_show_app_indicator_icons_on/
#   https://www.reddit.com/r/Fedora/comments/ucbunn/no_application_icons_displayed_in_the_tray/
#   https://www.reddit.com/r/Fedora/comments/z0wz53/libayatanaappindicator3dev_package_on_fedora/
#   https://packages.fedoraproject.org/pkgs/gnome-shell-extension-appindicator/gnome-shell-extension-appindicator/
#   https://unix.stackexchange.com/questions/6766/is-there-is-a-ppa-service-equivalent-in-the-fedora-world
#   https://forums.fedoraforum.org/showthread.php?330198-To-PPA-or-not-to-PPA
#
#   https://en.wikipedia.org/wiki/Gentoo_Linux
#
#   https://en.wikipedia.org/wiki/Slackware


#TODO Need to figure out for indicator-lunar how to install pyephem et al 
# via the preinst/postinst scripts working given how `pip` has changed things.
# If I cannot, need to add something about how to install and remove on the main README.md


#TODO Need to go through each pyproject.toml and update name/description/version/classifiers.


INDICATOR_NAME = "indicator-test"
import gettext
gettext.install( INDICATOR_NAME )

from indicatorbase import IndicatorBase  #TODO MOved to up top...is this safe?  
# What about _() already in indicatorbase.py... 
# ...they will miss out on being pulled in from po/mo.
# If the indicator name can be obtained from say the new pyproject.toml
# (by parsing directly and not via Pip as that is now impossible due to a deb install)
# then in indicatorbase.py we can get the indicator name and initialise gettext et al.


# import gi #TODO Is this needed as it is in IndicatorBase?
# gi.require_version( "Gtk", "3.0" ) #TODO Is this needed as it is in IndicatorBase?
# gi.require_version( "Notify", "0.7" ) #TODO Is this needed as it is in IndicatorBase?

from gi.repository import Gtk, Notify
from pathlib import Path
from threading import Thread

import datetime, os, random


class IndicatorTest( IndicatorBase ):

    CACHE_ICON_BASENAME = "-icon"
    CACHE_ICON_EXTENSION = ".svg"
    CACHE_ICON_MAXIMUM_AGE_HOURS = 0

    CONFIG_X = "x"


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.6",
            copyrightStartYear = "2016",
            comments = _( "Test" ) )

        self.requestMouseWheelScrollEvents()
        self.flushCache( IndicatorTest.CACHE_ICON_BASENAME, IndicatorTest.CACHE_ICON_MAXIMUM_AGE_HOURS )


    def update( self, menu ):
        self.__buildMenu( menu )
        self.setLabel( "Test Indicator" )


    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        self.setLabel( self.__getCurrentTime() )
        print( "Mouse wheel is scrolling..." )


    def __buildMenu( self, menu ):
        self.__buildMenuDesktop( menu )
        self.__buildMenuIconDefault( menu )
        self.__buildMenuIconDynamic( menu )
        self.__buildMenuLabelTooltipOSD( menu )
        self.__buildMenuTerminal( menu )
        self.__buildMenuPreferences( menu )
        self.__buildMenuLabelIconUpdating( menu )
        self.__buildMenuExecuteCommand( menu )
        self.__buildMenuUbuntuVariant( menu )


    def __buildMenuDesktop( self, menu ):
        subMenu = Gtk.Menu()

        subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Gtk.Settings().get_default().get_property( \"gtk-icon-theme-name\" ): " + self.getIconThemeName() ) )

        command = "gsettings get org.gnome.desktop.interface "
        subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + command + "icon-theme: " + self.processGet( command + "icon-theme" ).replace( '"', '' ).replace( '\'', '' ).strip() ) )
        subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + command + "gtk-theme: " + self.processGet( command + "gtk-theme" ).replace( '"', '' ).replace( '\'', '' ).strip() ) )

        subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + "echo $XDG_CURRENT_DESKTOP" + ": " + self.getDesktopEnvironment() ) )

        menuItem = Gtk.MenuItem.new_with_label( "Desktop" )
        menuItem.set_submenu( subMenu )
        menu.append( menuItem )


    def __buildMenuIconDefault( self, menu ):
        subMenu = Gtk.Menu()

        menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Use default icon" )
        menuItem.connect( "activate", lambda widget: self.__useIconDefault() )
        subMenu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Use default icon copied to user cache with colour change" )
        menuItem.connect( "activate", lambda widget: self.__useIconCopiedFromDefault() )
        subMenu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Icon (default)" )
        menuItem.set_submenu( subMenu )
        menu.append( menuItem )


    def __buildMenuIconDynamic( self, menu ):
        subMenu = Gtk.Menu()
        cacheDirectory = self.getCacheDirectory()
        icons = [ "FULL_MOON",
                  "WANING_GIBBOUS",
                  "THIRD_QUARTER",
                  "NEW_MOON",
                  "WAXING_CRESCENT" ]

        for icon in icons:
            menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Use " + icon + " dynamically created in " + cacheDirectory )
            menuItem.set_name( icon )
            menuItem.connect( "activate", lambda widget: self.__useIconDynamicallyCreated( widget.props.name ) )
            subMenu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Icon (dynamic)" )
        menuItem.set_submenu( subMenu )
        menu.append( menuItem )


    def __buildMenuLabelTooltipOSD( self, menu ):
        subMenu = Gtk.Menu()

        menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Show current time in label" )
        menuItem.connect( "activate", lambda widget: ( print( "mouse middle click" ), self.setLabel( self.__getCurrentTime() ) ) )
        self.secondaryActivateTarget = menuItem
        subMenu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Show current time in OSD" )
        menuItem.connect( "activate", lambda widget: Notify.Notification.new( "Current time...", self.__getCurrentTime(), self.icon ).show() )
        subMenu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Label / Tooltip / OSD" )
        menuItem.set_submenu( subMenu )
        menu.append( menuItem )


    def __buildMenuTerminal( self, menu ):
        subMenu = Gtk.Menu()

        terminal, executionFlag = self.getTerminalAndExecutionFlag()
        subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Terminal: " + str( terminal ) ) )
        subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Execution flag: " + str( executionFlag ) ) )

        menuItem = Gtk.MenuItem.new_with_label( "Terminal" )
        menuItem.set_submenu( subMenu )
        menu.append( menuItem )


    def __buildMenuPreferences( self, menu ):
        subMenu = Gtk.Menu()

        subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + "X: " + str( self.X ) ) )

        menuItem = Gtk.MenuItem.new_with_label( "Preferences" )
        menuItem.set_submenu( subMenu )
        menu.append( menuItem )


    def __buildMenuLabelIconUpdating( self, menu ):
        subMenu = Gtk.Menu()

        subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Icon: " + str( self.isIconUpdateSupported() ) ) )
        subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Label / Tooltip: " + str( self.isLabelUpdateSupported() ) ) )

        menuItem = Gtk.MenuItem.new_with_label( "Label / Tooltip / Icon Updating" )
        menuItem.set_submenu( subMenu )
        menu.append( menuItem )


    def __buildMenuExecuteCommand( self, menu ):
        subMenu = Gtk.Menu()

        menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Run \'ls\' and display results." )
        menuItem.connect( "activate", lambda widget: self.__executeCommand() )
        subMenu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Execute Command" )
        menuItem.set_submenu( subMenu )
        menu.append( menuItem )


    def __buildMenuUbuntuVariant( self, menu ):
        subMenu = Gtk.Menu()

        menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Is Ubuntu variant 20.04: " + str( self.isUbuntuVariant2004() ) )
        subMenu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Ubuntu Variant" )
        menuItem.set_submenu( subMenu )
        menu.append( menuItem )


    def __useIconCopiedFromDefault( self ):
        if self.isIconUpdateSupported():
            with open( "/usr/share/icons/hicolor/scalable/apps/" + self.icon + IndicatorTest.CACHE_ICON_EXTENSION, 'r' ) as fIn:
                svg = fIn.read()

            # If testing locally (without being installed via PPA/deb)...
            # with open( "../icons/indicator-test.svg", 'r' ) as fIn:
            #     svg = fIn.read()

            randomColour = \
                "{:02x}".format( random.randint( 0, 255 ) ) + \
                "{:02x}".format( random.randint( 0, 255 ) ) + \
                "{:02x}".format( random.randint( 0, 255 ) )

            svg = svg.replace( "6496dc", randomColour )
            fOut = self.writeCacheText( svg, IndicatorTest.CACHE_ICON_BASENAME, IndicatorTest.CACHE_ICON_EXTENSION )
            self.indicator.set_icon_full( fOut, "" )


    def __useIconDefault( self ):
        self.indicator.set_icon_full( self.icon, "" )


    def __getCurrentTime( self ):
        return datetime.datetime.now().strftime( "%H:%M:%S" )


    def __useIconDynamicallyCreated( self, phase ):
        illuminationPercentage = 35
        brightLimbAngleInDegrees = 65
        svgIconText = self.__getSVGIconText( phase, illuminationPercentage, brightLimbAngleInDegrees )
        iconFilename = self.writeCacheText( svgIconText, IndicatorTest.CACHE_ICON_BASENAME, IndicatorTest.CACHE_ICON_EXTENSION )
        self.indicator.set_icon_full( iconFilename, "" )


    def __useIconInHomeDirectory( self, iconName ):
        iconFile = os.getenv( "HOME" ) + '/' + iconName
        if Path( iconFile ).is_file():
            self.indicator.set_icon_full( iconFile, "" )

        else:
            Notify.Notification.new( "Cannot locate " + iconFile, "Please ensure the file is present.", self.icon ).show()


    # Virtually a direct copy from Indicator Lunar to test dynamically created SVG icons in the user cache.
    # phase The current phase of the moon.
    # illuminationPercentage The brightness ranging from 0 to 100 inclusive.
    #                        Ignored when phase is full/new or first/third quarter.
    # brightLimbAngleInDegrees Bright limb angle, relative to zenith, ranging from 0 to 360 inclusive.
    #                          Ignored when phase is full/new.
    def __getSVGIconText( self, phase, illuminationPercentage, brightLimbAngleInDegrees ):
        width = 100
        height = width
        radius = float( width / 2 )
        colour = self.getIconThemeColour( defaultColour = "fff200" ) # Default to hicolor.
        if phase == "FULL_MOON" or phase == "NEW_MOON":
            body = '<circle cx="' + str( width / 2 ) + '" cy="' + str( height / 2 ) + '" r="' + str( radius )
            if phase == "NEW_MOON":
                body += '" fill="none" stroke="#' + colour + '" stroke-width="2" />'

            else: # Full
                body += '" fill="#' + colour + '" />'

        else: # First/Third Quarter or Waning/Waxing Crescent or Waning/Waxing Gibbous
            body = '<path d="M ' + str( width / 2 - radius ) + ' ' + str( height / 2 ) + ' ' + \
                   'A ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + \
                   str( width / 2 + radius ) + ' ' + str( height / 2 )

            if phase == "FIRST_QUARTER" or phase == "THIRD_QUARTER":
                body += ' Z"'

            elif phase == "WANING_CRESCENT" or phase == "WAXING_CRESCENT":
                body += ' A ' + str( radius ) + ' ' + str( radius * ( 50 - illuminationPercentage ) / 50 ) + ' 0 0 0 ' + \
                        str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            else: # Waning/Waxing Gibbous
                body += ' A ' + str( radius ) + ' ' + str( radius * ( illuminationPercentage - 50 ) / 50 ) + ' 0 0 1 ' + \
                        str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            body += ' transform="rotate(' + str( -brightLimbAngleInDegrees ) + ' ' + \
                    str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="#' + colour + '" />'

        return '<?xml version="1.0" standalone="no"?>' \
               '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "https://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
               '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100" width="22" height="22">' + body + '</svg>'


    def __executeCommand( self ):
        terminal, terminalExecutionFlag = self.getTerminalAndExecutionFlag()
        if terminal is None:
            message = _( "Cannot run script as no terminal and/or terminal execution flag found; please install gnome-terminal." )
            self.getLogging().error( message )
            Notify.Notification.new( "Cannot run script", message, self.icon ).show()

        elif self.isTerminalQTerminal():
            # As a result of this issue
            #    https://github.com/lxqt/qterminal/issues/335
            # the default terminal in Lubuntu (qterminal) fails to parse argument.
            # Although a fix has been made, it is unlikely the repository will be updated any time soon.
            # So the quickest/easiest workaround is to install gnome-terminal. 
            message = _( "Cannot run script as qterminal incorrectly parses arguments; please install gnome-terminal instead." )
            self.getLogging().error( message )
            Notify.Notification.new( "Cannot run script", message, self.icon ).show()

        else:
            command = terminal + " " + terminalExecutionFlag + " ${SHELL} -c '"
            command += "ls -la"
            command += "; ${SHELL}"
            command += "'"
            Thread( target = self.processCall, args = ( command, ) ).start()
            print( "Executing command: " + command )


    def onPreferences( self, dialog ):
        grid = self.createGrid()

        xCheckbutton = Gtk.CheckButton.new_with_label( _( "Enable/disable X" ) )
        xCheckbutton.set_active( self.X )
        xCheckbutton.set_tooltip_text( _( "Enable/disable X" ) )
        grid.attach( xCheckbutton, 0, 0, 1, 1 )

        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.X = xCheckbutton.get_active()

        return responseType


    def loadConfig( self, config ):
        self.X = config.get( IndicatorTest.CONFIG_X, True )


    def saveConfig( self ):
        return {
            IndicatorTest.CONFIG_X : self.X
        }


IndicatorTest().main()
