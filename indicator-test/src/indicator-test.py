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

import datetime, random


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

        menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.MenuItem.new_with_label( "Switch to dynamic icon in user cache" )
        menuItem.connect( "activate", lambda widget: self.__useIconFromUserCache() )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( "Switch to default icon" )
        menuItem.connect( "activate", lambda widget: self.__useIconDefault() )
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

        menu.append( Gtk.MenuItem.new_with_label( _( "X: " + str( self.X ) ) ) )


    def __useIconFromUserCache( self ):
#TOOO Remove the check below on Lubuntu to see if using the same icon as used in startup actually works.        
        if not self.isDesktopEnvironmentLXQt(): # Lubuntu becomes confused and drops the icon if set after the indicator is initialised.
            #TODO Put this back on release.
            # with open( "/usr/share/icons/hicolor/scalable/apps/" + self.icon + IndicatorTest.CACHE_ICON_EXTENSION, 'r' ) as fIn:
            #     svg = fIn.read()
            with open( "../icons/indicator-test.svg", 'r' ) as fIn:
                svg = fIn.read()

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