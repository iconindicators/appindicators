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


# Application indicator which displays tidal information.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import datetime
import gi
import importlib.util
import sys

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

try:
    gi.require_version( "Notify", "0.7" )
except ValueError:
    gi.require_version( "Notify", "0.8" )
from gi.repository import Notify

from pathlib import Path


class IndicatorTide( IndicatorBase ):

    CONFIG_SHOW_AS_SUBMENUS = "showAsSubmenus"
    CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY = "showAsSubmenusExceptFirstDay"
    CONFIG_USER_SCRIPT_CLASS_NAME = "userScriptClassName"
    CONFIG_USER_SCRIPT_PATH_AND_FILENAME = "userScriptPathAndFilename"


    def __init__( self ):
        super().__init__(
            comments = _( "Displays tidal information." ) )


    def update( self, menu ):
        if self.userScriptPathAndFilename == "" and self.userScriptClassName == "":
            # First time the indicator is run, or really,
            # when there is no preference/json file,
            # there will be no user script specified,
            # so there will be no tidal data,
            # so do not treat this an exception.
            label = _( "No user script specified!" )
            summary = _( "No user script specified!" )
            message = _( "Please specify a user script and class name in the preferences." )
            menu.append( Gtk.MenuItem.new_with_label( label ) )
            Notify.Notification.new( summary, message, self.get_icon_name() ).show()

        else:
            tidalReadings = [ ]
            try:
                spec = importlib.util.spec_from_file_location( self.userScriptClassName, self.userScriptPathAndFilename )
                module = importlib.util.module_from_spec( spec )
                sys.modules[ self.userScriptClassName ] = module
                spec.loader.exec_module( module )
                klazz = getattr( module, self.userScriptClassName )
                tidalReadings = klazz.getTideData( self.getLogging() )
                self.buildMenu( menu, tidalReadings )

            except FileNotFoundError as e:
                label = _( "User script could not be found!" )
                summary = _( "User script could not be found!" )
                message = _( "Please check the user script in the preferences." )

            except AttributeError as e:
                label = _( "User script class name could not be found!" )
                summary = _( "User script class name could not be found!" )
                message = _( "Please check the user script class name in the preferences." )

            except Exception as e:
                label = _( "Error running user script!" )
                summary = _( "Error running user script!" )
                message = _( "Check the log file in your home directory." )
                self.getLogging().error( "Error running user script: " + self.userScriptPathAndFilename + " | " + self.userScriptClassName )
                self.getLogging().exception( e )

            if not tidalReadings:
                menu.append( Gtk.MenuItem.new_with_label( label ) )
                Notify.Notification.new( summary, message, self.get_icon_name() ).show()

        # Update a little after midnight...best guess as to when the user's data source will update.
        today = datetime.datetime.now()
        fiveMinutesAfterMidnight = ( today + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 )
        return ( fiveMinutesAfterMidnight - today ).total_seconds()


    def buildMenu( self, menu, tidalReadings ):
        indent = ""
        self.portName = tidalReadings[ 0 ].getLocation()
        if self.portName:
            self.createAndAppendMenuItem(
                menu,
                self.portName,
                name = tidalReadings[ 0 ].getURL(),
                onClickFunction = self.getOnClickMenuItemOpenBrowserFunction() )

            indent = self.getMenuIndent()

        if self.showAsSubMenus:
            if self.showAsSubMenusExceptFirstDay:
                firstDateTidalReadings, afterFirstDateTidalReadings = \
                    self.__splitTidalReadingsAfterFirstDate( tidalReadings )

                self.__createMenuFlat( firstDateTidalReadings, menu, indent )
                self.__createMenuSub( afterFirstDateTidalReadings, menu, indent )

            else:
                self.__createMenuSub( tidalReadings, menu, indent )

        else:
            self.__createMenuFlat( tidalReadings, menu, indent )


    def __createMenuFlat( self, tidalReadings, menu, indent ):
        todayDate = ""
        for tidalReading in tidalReadings:
            if todayDate != tidalReading.getDate():
                shownToday = False

            menuText = \
                indent + self.getMenuIndent() + \
                ( _( "HIGH" ) if tidalReading.isHigh() else _( "LOW" ) ) + "  " + \
                tidalReading.getTime() + "  " + tidalReading.getLevel()

            if shownToday:
                self.createAndAppendMenuItem(
                    menu,
                    menuText,
                    name = tidalReading.getURL(),
                    onClickFunction = self.getOnClickMenuItemOpenBrowserFunction() )

            else:
                self.createAndAppendMenuItem(
                    menu,
                    indent + tidalReading.getDate(),
                    name = tidalReading.getURL(),
                    onClickFunction = self.getOnClickMenuItemOpenBrowserFunction() )

                self.createAndAppendMenuItem(
                    menu,
                    menuText,
                    name = tidalReading.getURL(),
                    onClickFunction = self.getOnClickMenuItemOpenBrowserFunction() )

                todayDate = tidalReading.getDate()
                shownToday = True


    def __createMenuSub( self, tidalReadings, menu, indent ):
        todayDate = ""
        shownToday = False
        subMenu = None # Only declared here to keep the compiler happy.
        for tidalReading in tidalReadings:
            if todayDate != tidalReading.getDate():
                shownToday = False

            menuText = \
                indent + self.getMenuIndent() + \
                ( _( "HIGH" ) if tidalReading.isHigh() else _( "LOW" ) ) + "  " + \
                tidalReading.getTime() + "  " + tidalReading.getLevel()

            if shownToday:
                self.createAndAppendMenuItem(
                    subMenu,
                    menuText,
                    name = tidalReading.getURL(),
                    onClickFunction = self.getOnClickMenuItemOpenBrowserFunction() )

            else:
                subMenu = Gtk.Menu()
                self.createAndAppendMenuItem(
                    menu,
                    indent + tidalReading.getDate() ).set_submenu( subMenu )

                self.createAndAppendMenuItem(
                    subMenu,
                    menuText,
                    name = tidalReading.getURL(),
                    onClickFunction = self.getOnClickMenuItemOpenBrowserFunction() )

                todayDate = tidalReading.getDate()
                shownToday = True


    def __splitTidalReadingsAfterFirstDate( self, tidalReadings ):
        firstDateReadings = [ ]
        afterFirstDateReadings = [ ]
        for tidalReading in tidalReadings:
            if tidalReading.getDate() == tidalReadings[ 0 ].getDate():
                firstDateReadings.append( tidalReading )

            else:
                afterFirstDateReadings.append( tidalReading )

        return firstDateReadings, afterFirstDateReadings


    def onPreferences( self, dialog ):
        grid = self.createGrid()

        label = Gtk.Label.new( _( "User Script" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label.new( _( "Path and filename" ) ), False, False, 0 )

        userScriptPathAndFilename = Gtk.Entry()
        userScriptPathAndFilename.set_text( self.userScriptPathAndFilename )
        userScriptPathAndFilename.set_hexpand( True )
        userScriptPathAndFilename.set_tooltip_text( _( "Full path and filename\nof user's Python3 script." ) )

        box.pack_start( userScriptPathAndFilename, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label.new( _( "Class name" ) ), False, False, 0 )

        userScriptClassName = Gtk.Entry()
        userScriptClassName.set_text( self.userScriptClassName )
        userScriptClassName.set_hexpand( True )
        userScriptClassName.set_tooltip_text( _(
            "Class name within the user script\n" + \
            "which must contain the function\n\n" + \
            "    getTideData()\n\n" + \
            "implemented by the user to obtain\n" + \
            "the tidal data." ) )

        box.pack_start( userScriptClassName, True, True, 0 )

        box.set_margin_bottom( 10 )

        grid.attach( box, 0, 2, 1, 1 )

        showAsSubmenusCheckbutton = Gtk.CheckButton.new_with_label( _( "Show as submenus" ) )
        showAsSubmenusCheckbutton.set_active( self.showAsSubMenus )
        showAsSubmenusCheckbutton.set_tooltip_text( _( "Show each day's tides in a submenu." ) )

        grid.attach( showAsSubmenusCheckbutton, 0, 3, 1, 1 )

        showAsSubmenusExceptFirstDayCheckbutton = Gtk.CheckButton.new_with_label( _( "Except first day" ) )
        showAsSubmenusExceptFirstDayCheckbutton.set_sensitive( showAsSubmenusCheckbutton.get_active() )
        showAsSubmenusExceptFirstDayCheckbutton.set_active( self.showAsSubMenusExceptFirstDay )
        showAsSubmenusExceptFirstDayCheckbutton.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        showAsSubmenusExceptFirstDayCheckbutton.set_tooltip_text( _( "Show the first day's tide in full." ) )

        grid.attach( showAsSubmenusExceptFirstDayCheckbutton, 0, 4, 1, 1 )

        showAsSubmenusCheckbutton.connect( "toggled", self.onRadioOrCheckbox, True, showAsSubmenusExceptFirstDayCheckbutton )

        autostartCheckbox, delaySpinner, box = self.createAutostartCheckboxAndDelaySpinner()
        grid.attach( box, 0, 5, 1, 1 )

        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.show_all()

        while True:
            responseType = dialog.run()
            if responseType == Gtk.ResponseType.OK:
                self.showAsSubMenus = showAsSubmenusCheckbutton.get_active()
                self.showAsSubMenusExceptFirstDay = showAsSubmenusExceptFirstDayCheckbutton.get_active()

                if userScriptPathAndFilename.get_text() and userScriptClassName.get_text():
                    if not Path( userScriptPathAndFilename.get_text().strip() ).is_file():
                        self.showMessage( dialog, _( "The user script path/filename cannot be found." ) )
                        userScriptPathAndFilename.grab_focus()
                        continue

                elif userScriptPathAndFilename.get_text() or userScriptClassName.get_text(): # Cannot have one empty and the other not.
                    if not userScriptPathAndFilename.get_text():
                        self.showMessage( dialog, _( "The user script path/filename cannot be empty." ) )
                        userScriptPathAndFilename.grab_focus()
                        continue

                    else:
                        self.showMessage( dialog, _( "The user script class name cannot be empty." ) )
                        userScriptClassName.grab_focus()
                        continue

                self.userScriptPathAndFilename = userScriptPathAndFilename.get_text().strip()
                self.userScriptClassName = userScriptClassName.get_text().strip()

            self.setAutostartAndDelay( autostartCheckbox.get_active(), delaySpinner.get_value_as_int() )
            break

        return responseType


    def loadConfig( self, config ):
        self.showAsSubMenus = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS, True )
        self.showAsSubMenusExceptFirstDay = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY, True )
        self.userScriptPathAndFilename = config.get( IndicatorTide.CONFIG_USER_SCRIPT_PATH_AND_FILENAME, "" )
        self.userScriptClassName = config.get( IndicatorTide.CONFIG_USER_SCRIPT_CLASS_NAME, "" )


    def saveConfig( self ):
        return {
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS : self.showAsSubMenus,
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY : self.showAsSubMenusExceptFirstDay,
            IndicatorTide.CONFIG_USER_SCRIPT_CLASS_NAME : self.userScriptClassName,
            IndicatorTide.CONFIG_USER_SCRIPT_PATH_AND_FILENAME : self.userScriptPathAndFilename
        }


IndicatorTide().main()
