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


#TODO Current thinking/plan for creating snaps et al...
#
# Ideally, want a well-behaved/formed Python project from the outset using pyproject.toml
# and from that all other builds (DEB source for LaunchPad, snap, et al) come from that.
#
# Each indicator comprises pure Python and so on the face of it,
# should be candidates for installation via PyPI.
# However, given the additional files requiring installation such as icons, .desktop, et al 
# which MUST go into the file system, it seems that a .deb is the only option.
# I have seen discussion of this situation on StackOverflow et al...an OS package is best. 
#
# So, convert all indicators to use a pyproject.toml, 
# despite not being used to create the .deb file.
#
# The theory/hope is that when creating a snap/rpm/flatpak/appimage
# the pyproject.toml will make life easier,
# although I suspect for each snap/rpm/flatpak/appimage I will likely
# need a script to prepare the files/layout before calling the specific
# tool to build (as I do in my new buildDebian.py which ultimately calls debuild.


#TODO The only outstanding issue for moving to pyproject.toml
# is obtaining the version/name/author/description.
# For a Pip installed package, those tags are accessible at run time.
# The idea is to have the version et al in one place and that is pyproject.toml.
#
# If the packages are now .deb file, the pyproject.toml is not available.
# So what to do...include the pyproject.toml in the installation directory
# and in say indicatorbase.py parse the file at run time?


#TODO Single version number location
#   https://packaging.python.org/en/latest/guides/single-sourcing-package-version/
#   https://stackoverflow.com/questions/72357031/set-version-of-module-from-a-file-when-configuring-setuptools-using-setup
#   https://stackoverflow.com/questions/60430112/single-sourcing-package-version-for-setup-cfg-python-projects


#TODO Shared project layout
#   https://stackoverflow.com/questions/18087122/python-sharing-common-code-among-a-family-of-scripts
#   https://stackoverflow.com/questions/73580708/how-to-share-code-between-python-internals-projects
#   https://stackoverflow.com/questions/48954870/how-to-share-code-between-python-projects
#   https://discuss.python.org/t/multiple-related-programs-one-pyproject-toml-or-multiple-projects/17427/2


#TODO Need a LICENSE.TXT or md or similar
# See pyproject.toml and what are the options.
# Is the license the same as the debian/copyright file?
# If so, need to mofidy the buildDebian.py
# use a common license file at the top of the project.  
#   https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#license-txt


#TODO Ideally include the project name in the CHANGELOG.md
# but that means we need to skip it in the convertMarkdowntoDebian.py script.
# Something like:
#   
#   # Changelog for indicator-fortune
#   
# Or:
#   
#   # Changelog
#   This is the changelog for indicator-fortune


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


#TODO 
# Need to move the unittests for each in to a tests sub directory and call them test_indicator_whatever.py
# After that, make the unitests look like that of playlistmaker.
# Should the unit tests be included in the build/release?


#TODO May be useful in indicatorbase for finding user dirs and simlar in a os-independent manner:
#   https://pypi.org/project/platformdirs/


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
