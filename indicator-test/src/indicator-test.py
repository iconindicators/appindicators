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


INDICATOR_NAME = "indicator-test"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gtk, Notify
from indicatorbase import IndicatorBase

import datetime, os, random


class IndicatorTest( IndicatorBase ):

    CACHE_ICON_BASENAME = "-icon"
    CACHE_ICON_EXTENSION = ".svg"
    CACHE_ICON_MAXIMUM_AGE_HOURS = 0

    CONFIG_X = "x"


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.5",
            copyrightStartYear = "2016",
            comments = _( "Test" ) )

        self.requestMouseWheelScrollEvents()
        self.flushCache( IndicatorTest.CACHE_ICON_BASENAME, IndicatorTest.CACHE_ICON_MAXIMUM_AGE_HOURS )


    def update( self, menu ):
        self.__buildMenu( menu )
        self.setLabel( "Test Indicator" )


    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        self.setLabel( self.__getCurrentTime() )


    def __buildMenu( self, menu ):
        menu.append( Gtk.MenuItem.new_with_label( "Gtk.Settings().get_default().get_property( \"gtk-icon-theme-name\" ): " + self.getIconThemeName() ) )

        command = "gsettings get org.gnome.desktop.interface "
        menu.append( Gtk.MenuItem.new_with_label( command + "icon-theme: " + self.processGet( command + "icon-theme" ).replace( '"', '' ).replace( '\'', '' ).strip() ) )
        menu.append( Gtk.MenuItem.new_with_label( command + "gtk-theme: " + self.processGet( command + "gtk-theme" ).replace( '"', '' ).replace( '\'', '' ).strip() ) )

        command = "echo $XDG_CURRENT_DESKTOP"
        menu.append( Gtk.MenuItem.new_with_label( command + ": " + self.processGet( command ).strip() ) )

        menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.MenuItem.new_with_label( "Use default icon" )
        menuItem.connect( "activate", lambda widget: self.__useIconDefault() )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Use default icon copied to user cache with colour change" )
        menuItem.connect( "activate", lambda widget: self.__useIconCopiedFromDefault() )
        menu.append( menuItem )

        menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.MenuItem.new_with_label( "Use on-the-fly icon created in user cache (FULL_MOON)" )
        menuItem.connect( "activate", lambda widget: self.__useIconDynamicallyCreated( "FULL_MOON" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Use on-the-fly icon created in user cache (WANING_GIBBOUS)" )
        menuItem.connect( "activate", lambda widget: self.__useIconDynamicallyCreated( "WANING_GIBBOUS" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Use on-the-fly icon created in user cache (THIRD_QUARTER)" )
        menuItem.connect( "activate", lambda widget: self.__useIconDynamicallyCreated( "THIRD_QUARTER" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Use on-the-fly icon created in user cache (NEW_MOON)" )
        menuItem.connect( "activate", lambda widget: self.__useIconDynamicallyCreated( "NEW_MOON" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Use on-the-fly icon created in user cache (WAXING_CRESCENT)" )
        menuItem.connect( "activate", lambda widget: self.__useIconDynamicallyCreated( "WAXING_CRESCENT" ) )
        menu.append( menuItem )

        menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-fortune.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-fortune.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-lunar.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-lunar.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-lunar-satellite.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-lunar-satellite.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-on-this-day.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-on-this-day.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-ppa-download-statistics.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-ppa-download-statistics.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-punycode.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-punycode.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-script-runner.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-script-runner.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-stardate.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-stardate.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-test.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-test.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-tide.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-tide.svg" ) )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Use indicator-virtual-box.svg in $HOME" ) )
        menuItem.connect( "activate", lambda widget: self.__useIconInHomeDirectory( "indicator-virtual-box.svg" ) )
        menu.append( menuItem )

        menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.MenuItem.new_with_label( _( "Show current time in label" ) )
        menuItem.connect( "activate", lambda widget: self.setLabel( self.__getCurrentTime() ) )
        menu.append( menuItem )
        self.secondaryActivateTarget = menuItem

        menuItem = Gtk.MenuItem.new_with_label( "Show current time in OSD" )
        menuItem.connect( "activate", lambda widget: Notify.Notification.new( "Current time...", self.__getCurrentTime(), self.icon ).show() )
        menu.append( menuItem )

        menu.append( Gtk.SeparatorMenuItem() )

#TODO Not sure if this is valid now.
        # menu.append( Gtk.MenuItem.new_with_label( "Middle mouse button click supported: " + str( self.isMouseMiddleButtonClickSupported() ) ) )

        menu.append( Gtk.SeparatorMenuItem() )

        menu.append( Gtk.MenuItem.new_with_label( _( "X: " + str( self.X ) ) ) )


    def __useIconCopiedFromDefault( self ):
#TODO Revisit this function.        
        # if not self.isDesktopEnvironmentLXQt(): # Lubuntu becomes confused and drops the icon if set via a full path.
        #     with open( "/usr/share/icons/hicolor/scalable/apps/" + self.icon + IndicatorTest.CACHE_ICON_EXTENSION, 'r' ) as fIn:
        #         svg = fIn.read()
        #
        #     # If testing locally (without being installed via PPA/deb)...
        #     # with open( "../icons/indicator-test.svg", 'r' ) as fIn:
        #     #     svg = fIn.read()
        #
        #     randomColour = \
        #         "{:02x}".format( random.randint( 0, 255 ) ) + \
        #         "{:02x}".format( random.randint( 0, 255 ) ) + \
        #         "{:02x}".format( random.randint( 0, 255 ) )
        #
        #     svg = svg.replace( "6496dc", randomColour )
        #     fOut = self.writeCacheText( svg, IndicatorTest.CACHE_ICON_BASENAME, IndicatorTest.CACHE_ICON_EXTENSION )
        #     self.indicator.set_icon_full( fOut, "" )
        pass


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
        self.indicator.set_icon_full( os.getenv( "HOME" ) + '/' + iconName, "" )


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
               '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 22 22" width="22" height="22">' + body + '</svg>'


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