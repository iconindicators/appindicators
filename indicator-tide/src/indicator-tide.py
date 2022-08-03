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


INDICATOR_NAME = "indicator-tide"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gtk, Notify
from indicatorbase import IndicatorBase

import datetime, importlib.util, sys, webbrowser


class IndicatorTide( IndicatorBase ):

    CONFIG_SHOW_AS_SUBMENUS = "showAsSubmenus"
    CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY = "showAsSubmenusExceptFirstDay"
    CONFIG_USER_SCRIPT_MODLUE_NAME = "userScriptModuleName"
    CONFIG_USER_SCRIPT_PATH_AND_FILENAME = "userScriptPathAndFilename"


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.26",
            copyrightStartYear = "2015",
            comments = _( "Displays tidal information." ) )


    def update( self, menu ):
        # import importlib
        # import sys
        
        # from getTideDataFromBOM import GetTideDataFromBOM
        # GetTideDataFromBOM.getTideData()


        # module = importlib.import_module( "getTideDataFromBOM" )
        # x = userGetTideDataFunction.getTideData()
        # print( x )


        spec = importlib.util.spec_from_file_location( "GetTideDataFromBOM", "/home/bernard/Downloads/getTideDataFromBOM.py" )
        module = importlib.util.module_from_spec( spec )
        sys.modules[ "GetTideDataFromBOM" ] = module
        spec.loader.exec_module( module )
        klazz = getattr( module, "GetTideDataFromBOM" )
        tidalReadings = klazz.getTideData( self.getLogging() )

        # try:
        #     dyn.mymethod() # How to check whether this exists or not
        #     # Method exists and was used.  
        # except AttributeError:
        #     # Method does not exist; What now?

        # spec = importlib.util.spec_from_loader( "GetTideDataFromBOM", importlib.machinery.SourceFileLoader( "GetTideDataFromBOM", "getTideDataFromBOM.py" ) )
        # module = importlib.util.module_from_spec(spec)
        # spec.loader.exec_module(module)
        # sys.modules["GetTideDataFromBOM"] = module
        # module.getTideData

        # spec = importlib.util.spec_from_file_location( "GetTideDataFromBOM", "getTideDataFromBOM.py" )
        # module = importlib.util.module_from_spec( spec )
        # sys.modules[ "GetTideDataFromBOM" ] = module            
        # spec.loader.exec_module( module )
        # module.getTideData
        
        # loadedModule = spec.loader.load_module( module )
        # klass = getattr(module, "getTideData")
        # x = module.getTideData()

        
        # import types
        # import importlib.machinery
        # loader = importlib.machinery.SourceFileLoader( "getTideDataFromBOM", "getTideDataFromBOM.py" )
        # mod = types.ModuleType( loader.name )
        # loader.exec_module( mod )            
        
        
        if tidalReadings:
            self.buildMenu( menu, tidalReadings )

        else:
            menu.append( Gtk.MenuItem.new_with_label( _( "No tidal data available!" ) ) )
            summary = _( "Error" )
            message = _( "No tidal data available!" )
            self.getLogging().error( message )
            Notify.Notification.new( summary, message, self.icon ).show()

        return self.getNextUpdateTimeInSeconds( tidalReadings )


    def buildMenu( self, menu, tidalReadings ):
        indent = "" 
        self.portName = tidalReadings[ 0 ].getLocation()
        if self.portName:
            self.__createAndAppendMenuItem( menu, self.portName, tidalReadings[ 0 ].getURL() )
            indent = self.getMenuIndent( 1 )

        url = tidalReadings[ 0 ].getURL()
        if self.showAsSubMenus:
            if self.showAsSubMenusExceptFirstDay:
                firstDateTidalReadings, afterFirstDateTidalReadings = self.splitTidalReadingsAfterFirstDate( tidalReadings )
                self.__createMenuFlat( firstDateTidalReadings, menu, indent )
                self.__createMenuSub( afterFirstDateTidalReadings, menu, indent )

            else:
                self.__createMenuSub( tidalReadings, menu, indent )

        else:
            self.__createMenuFlat( tidalReadings, menu, indent )


    def __createMenuFlat( self, tidalReadings, menu, indent ):
        todayDate = ""
        shownToday = False
        for tidalReading in tidalReadings:
            if todayDate != tidalReading.getDate():
                shownToday = False
        
            menuText = indent + self.getMenuIndent( 1 ) + ( _( "HIGH" ) if tidalReading.isHigh() else _( "LOW" ) ) + "  " + tidalReading.getTime()
            if shownToday:
                self.__createAndAppendMenuItem( menu, menuText, tidalReading.getURL() )
        
            else:
                self.__createAndAppendMenuItem( menu, indent + tidalReading.getDate(), tidalReading.getURL() )
                self.__createAndAppendMenuItem( menu, menuText, tidalReading.getURL() )
                todayDate = tidalReading.getDate()
                shownToday = True


    def __createMenuSub( self, tidalReadings, menu, indent ):
        todayDate = ""
        shownToday = False
        for tidalReading in tidalReadings:
            if todayDate != tidalReading.getDate():
                shownToday = False

            menuText = indent + self.getMenuIndent( 1 ) + ( _( "HIGH" ) if tidalReading.isHigh() else _( "LOW" ) ) + "  " + tidalReading.getTime()
            if shownToday:
                self.__createAndAppendMenuItem( subMenu, menuText, tidalReading.getURL() )

            else:
                subMenu = Gtk.Menu()
                self.__createAndAppendMenuItem( menu, indent + tidalReading.getDate(), None ).set_submenu( subMenu )
                self.__createAndAppendMenuItem( subMenu, menuText, tidalReading.getURL() )
                todayDate = tidalReading.getDate()
                shownToday = True


    def __createAndAppendMenuItem( self, menu, menuItemText, url ):
        menuItem = Gtk.MenuItem.new_with_label( menuItemText )
        menu.append( menuItem )
        if url is not None:
            menuItem.connect( "activate", lambda widget: webbrowser.open( widget.props.name ) )
            menuItem.set_name( url )

        return menuItem


    def splitTidalReadingsAfterFirstDate( self, tidalReadings ):
        firstDateReadings = [ ]
        afterFirstDateReadings = [ ]
        for tidalReading in tidalReadings:
            if tidalReading.getDate() == tidalReadings[ 0 ].getDate():
                firstDateReadings.append( tidalReading )

            else:
                afterFirstDateReadings.append( tidalReading )

        return firstDateReadings, afterFirstDateReadings


    def getNextUpdateTimeInSeconds( self, tidalReadings ):
        # Update a little after midnight...best guess as to when the user's data source will update.
        now = datetime.datetime.now()
        fiveMinutesAfterMidnight = ( now + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 )
        return ( fiveMinutesAfterMidnight - now ).total_seconds()


    def onPreferences( self, dialog ):
        grid = self.createGrid()

        showAsSubmenusCheckbutton = Gtk.CheckButton.new_with_label( _( "Show as submenus" ) )
        showAsSubmenusCheckbutton.set_active( self.showAsSubMenus )
        showAsSubmenusCheckbutton.set_tooltip_text( _( "Show each day's tides in a submenu." ) )

        grid.attach( showAsSubmenusCheckbutton, 0, 0, 1, 1 )

        showAsSubmenusExceptFirstDayCheckbutton = Gtk.CheckButton.new_with_label( _( "Except first day" ) )
        showAsSubmenusExceptFirstDayCheckbutton.set_sensitive( showAsSubmenusCheckbutton.get_active() )
        showAsSubmenusExceptFirstDayCheckbutton.set_active( self.showAsSubMenusExceptFirstDay )
        showAsSubmenusExceptFirstDayCheckbutton.set_margin_left( self.INDENT_WIDGET_LEFT )
        showAsSubmenusExceptFirstDayCheckbutton.set_tooltip_text( _( "Show the first day's tide in full." ) )

        grid.attach( showAsSubmenusExceptFirstDayCheckbutton, 0, 1, 1, 1 )

        showAsSubmenusCheckbutton.connect( "toggled", self.onRadioOrCheckbox, True, showAsSubmenusExceptFirstDayCheckbutton )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )
        
        box.pack_start( Gtk.Label.new( _( "User script" ) ), False, False, 0 )
        
        userScript = Gtk.Entry()
        # userScript.set_text( self.menuItemDateFormat )
        userScript.set_hexpand( True )
        userScript.set_tooltip_text( _(
            "Formatting options for the date:\n\n" + \
            "    https://docs.python.org/3/library/datetime.html\n\n" + \
            "Leave empty to reset back to default." ) ) #TODO Fix

        box.pack_start( userScript, True, True, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )
        
        box.pack_start( Gtk.Label.new( _( "User class" ) ), False, False, 0 )
        
        userClass = Gtk.Entry()
        # userClass.set_text( self.menuItemDateFormat )
        userClass.set_hexpand( True )
        userClass.set_tooltip_text( _(
            "Formatting options for the date:\n\n" + \
            "    https://docs.python.org/3/library/datetime.html\n\n" + \
            "Leave empty to reset back to default." ) ) #TODO Fix

        box.pack_start( userClass, True, True, 0 )

        grid.attach( box, 0, 3, 1, 1 )

        # label = Gtk.Label.new( _( "Tide format" ) )
        # label.set_margin_top( 10 )
        # label.set_halign( Gtk.Align.START )
        #
        # grid.attach( label, 0, 3, 1, 1 )
        #
        # box = Gtk.Box( spacing = 6 )
        # box.set_margin_left( self.INDENT_WIDGET_LEFT )
        #
        # box.pack_start( Gtk.Label.new( _( "Default" ) ), False, False, 0 )
        #
        # tideFormat = Gtk.Entry()
        # tideFormat.set_text( self.menuItemTideFormat )
        # tideFormat.set_hexpand( True )
        # tideFormat.set_tooltip_text( _(
        #     "Tide information is specified using:\n\n" + \
        #     "    {0} - the tide is high or low.\n" + \
        #     "    {1} - the tide level, measured in metres.\n\n" + \
        #     "Formatting options for the time:\n\n" + \
        #     "    https://docs.python.org/3/library/datetime.html\n\n" + \
        #     "Leave empty to reset back to default." ).format( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG ) )
        # box.pack_start( tideFormat, True, True, 0 )
        #
        # grid.attach( box, 0, 4, 1, 1 )
        #
        # box = Gtk.Box( spacing = 6 )
        # box.set_margin_left( self.INDENT_WIDGET_LEFT )
        #
        # box.pack_start( Gtk.Label.new( _( "Missing time" ) ), False, False, 0 )
        #
        # tideFormatSansTime = Gtk.Entry()
        # tideFormatSansTime.set_text( self.menuItemTideFormatSansTime )
        # tideFormatSansTime.set_hexpand( True )
        # tideFormatSansTime.set_tooltip_text( _(
        #     "Tide information is specified using:\n\n" + \
        #     "    {0} - the tide is high or low.\n" + \
        #     "    {1} - the tide level, measured in metres.\n\n" + \
        #     "This format is used when there is no time\n" + \
        #     "component in a tide reading.\n\n" + \
        #     "Leave empty to reset back to default." ).format( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG ) )
        # box.pack_start( tideFormatSansTime, True, True, 0 )
        #
        # grid.attach( box, 0, 5, 1, 1 )

        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            country = countriesComboBox.get_active_text()
            model, treeiter = portsTree.get_selection().get_selected()
            port = model[ treeiter ][ COLUMN_PORT ]
            self.portID = ports.getPortIDForCountryAndPortName( country, port )
            self.showAsSubMenus = showAsSubmenusCheckbutton.get_active()
            self.showAsSubMenusExceptFirstDay = showAsSubmenusExceptFirstDayCheckbutton.get_active()

            if userScript.get_text():
                self.menuItemDateFormat = userScript.get_text()

            else:
                self.menuItemDateFormat = IndicatorTide.MENU_ITEM_DATE_DEFAULT_FORMAT


            if tideFormat.get_text():
                self.menuItemTideFormat = tideFormat.get_text()

            else:
                self.menuItemTideFormat = IndicatorTide.MENU_ITEM_TIDE_DEFAULT_FORMAT

            if tideFormatSansTime.get_text():
                self.menuItemTideFormatSansTime = tideFormatSansTime.get_text()

            else:
                self.menuItemTideFormatSansTime = IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT_SANS_TIME

        return responseType


    def loadConfig( self, config ):
        self.showAsSubMenus = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS, True )
        self.showAsSubMenusExceptFirstDay = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY, True )
        self.userScriptPathAndFilename = config.get( IndicatorTide.CONFIG_USER_SCRIPT_PATH_AND_FILENAME, "" )
        self.userScriptModuleName = config.get( IndicatorTide.CONFIG_USER_SCRIPT_MODLUE_NAME, "" )


    def saveConfig( self ):
        return {
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS : self.showAsSubMenus,
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY : self.showAsSubMenusExceptFirstDay,
            IndicatorTide.CONFIG_USER_SCRIPT_MODLUE_NAME : self.userScriptModuleName,
            IndicatorTide.CONFIG_USER_SCRIPT_PATH_AND_FILENAME : self.userScriptPathAndFilename
        }


IndicatorTide().main()