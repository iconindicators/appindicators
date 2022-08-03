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


#TODO Looks like the UKHO is dropping all ports other than those of the UK.
# If so, need another source, possible ones (local and/or global) are...
    # https://tidesnear.me/tide_stations/6671                    Matches EXACTLY with BOM.
    # https://www.tidetime.org/australia-pacific/australia/palm-beach.htm        Matches with BOM.
    # http://www.bom.gov.au/australia/tides/#!/nsw-sand-point-pittwater
    # http://www.bom.gov.au/australia/tides/print.php?aac=NSW_TP032&type=tide&date=29-8-2021&region=NSW&tz=Australia/Sydney&tz_js=AEDT&days=7
    # https://www.aquatera.co.uk/tools/tidal-database        Sells data and got no repsone to email.
    # https://www.thetidetimes.com/            Domain no longer exists.
    # https://www.tideschart.com/                Matches with BOM.
    # https://www.tide-forecast.com/            Could not find Fort Denison (to compare with BOM).


#TODO Some of the above links use Javascript to post render the page,
# so parsing the HTML source may not contain tide data until the Javascript is executed.
# Possible solutions are:
    # http://theautomatic.net/2019/01/19/scraping-data-from-javascript-webpage-python/
    # https://stackoverflow.com/questions/29996001/using-python-requests-get-to-parse-html-code-that-does-not-load-at-once
    # https://selenium-python.readthedocs.io/
    # https://pypi.org/project/requests-html/
    # https://stackoverflow.com/questions/26393231/using-python-requests-with-javascript-pages


INDICATOR_NAME = "indicator-tide"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gtk, Notify
from indicatorbase import IndicatorBase
from urllib.request import urlopen

import datetime, locale, ports, re, tide, time, webbrowser


class IndicatorTide( IndicatorBase ):

    CONFIG_PORT_NAME = "portName"
    CONFIG_SHOW_AS_SUBMENUS = "showAsSubmenus"
    CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY = "showAsSubmenusExceptFirstDay"
    CONFIG_USER_SCRIPT_PATH_AND_FILENAME = "userScriptPathAndFilename"
    CONFIG_USER_SCRIPT_CLASSNAME = "userScriptClassname"


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


        import importlib.util, sys
        spec = importlib.util.spec_from_file_location( "GetTideDataFromBOM", "getTideDataFromBOM.py" )
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

        # return self.getNextUpdateTimeInSeconds( tidalReadings )


# Tue 2 Aug | 5:13 am | False | 0.14 m | file:///home/bernard/Downloads/tide.html, 
# Tue 2 Aug | 11:25 am | True | 1.27 m | file:///home/bernard/Downloads/tide.html, 
# Tue 2 Aug | 5:09 pm | False | 0.31 m | file:///home/bernard/Downloads/tide.html, 
# Tue 2 Aug | 11:23 pm | True | 1.48 m | file:///home/bernard/Downloads/tide.html, 
# Wed 3 Aug | 5:51 am | False | 0.15 m | file:///home/bernard/Downloads/tide.html, 
# Wed 3 Aug | 12:09 pm | True | 1.31 m | file:///home/bernard/Downloads/tide.html, 
# Wed 3 Aug | 6:00 pm | False | 0.34 m | file:///home/bernard/Downloads/tide.html, 
# Thu 4 Aug | 12:10 am | True | 1.39 m | file:///home/bernard/Downloads/tide.html, 
# Thu 4 Aug | 6:33 am | False | 0.18 m | file:///home/bernard/Downloads/tide.html, 
# Thu 4 Aug | 12:58 pm | True | 1.36 m | file:///home/bernard/Downloads/tide.html, 
# Thu 4 Aug | 7:00 pm | False | 0.37 m | file:///home/bernard/Downloads/tide.html, Fri 5 Aug | 1:03 am | True | 1.29 m | file:///home/bernard/Downloads/tide.html, Fri 5 Aug | 7:20 am | False | 0.24 m | file:///home/bernard/Downloads/tide.html, Fri 5 Aug | 1:52 pm | True | 1.43 m | file:///home/bernard/Downloads/tide.html, Fri 5 Aug | 8:06 pm | False | 0.40 m | file:///home/bernard/Downloads/tide.html, Sat 6 Aug | 2:07 am | True | 1.22 m | file:///home/bernard/Downloads/tide.html, Sat 6 Aug | 8:12 am | False | 0.30 m | file:///home/bernard/Downloads/tide.html, Sat 6 Aug | 2:52 pm | True | 1.51 m | file:///home/bernard/Downloads/tide.html, Sat 6 Aug | 9:22 pm | False | 0.40 m | file:///home/bernard/Downloads/tide.html, Sun 7 Aug | 3:20 am | True | 1.18 m | file:///home/bernard/Downloads/tide.html, Sun 7 Aug | 9:11 am | False | 0.36 m | file:///home/bernard/Downloads/tide.html, Sun 7 Aug | 3:55 pm | True | 1.61 m | file:///home/bernard/Downloads/tide.html, Sun 7 Aug | 10:38 pm | False | 0.36 m | file:///home/bernard/Downloads/tide.html, Mon 8 Aug | 4:33 am | True | 1.20 m | file:///home/bernard/Downloads/tide.html, Mon 8 Aug | 10:15 am | False | 0.39 m | file:///home/bernard/Downloads/tide.html, Mon 8 Aug | 4:57 pm | True | 1.73 m | file:///home/bernard/Downloads/tide.html, Mon 8 Aug | 11:45 pm | False | 0.29 m | file:///home/bernard/Downloads/tide.html]

    def buildMenu( self, menu, tidalReadings ):
        indent = "" 
        self.portName = tidalReadings[ 0 ].getLocation()
        self.portName = ""
        if self.portName:
            self.__createAndAppendMenuItemNEW( menu, self.portName, tidalReadings[ 0 ].getURL() )
            indent = self.getMenuIndent( 1 )

        url = tidalReadings[ 0 ].getURL()
        if not self.showAsSubMenus:
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
                self.__createAndAppendMenuItemNEW( menu, menuText, tidalReading.getURL() )
        
            else:
                self.__createAndAppendMenuItemNEW( menu, indent + tidalReading.getDate(), tidalReading.getURL() )
                self.__createAndAppendMenuItemNEW( menu, menuText, tidalReading.getURL() )
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
                self.__createAndAppendMenuItemNEW( subMenu, menuText, tidalReading.getURL() )

            else:
                subMenu = Gtk.Menu()
                self.__createAndAppendMenuItemNEW( menu, indent + tidalReading.getDate(), None ).set_submenu( subMenu )
                self.__createAndAppendMenuItemNEW( subMenu, menuText, tidalReading.getURL() )
                todayDate = tidalReading.getDate()
                shownToday = True


    def __createAndAppendMenuItemNEW( self, menu, menuItemText, url ):
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


    def buildMenuORIGINAL( self, menu, tidalReadings ):
        menuItemText = _( "{0}, {1}" ).format( ports.getPortName( self.portID ), ports.getCountry( self.portID ) )
        self.__createAndAppendMenuItem( menu, menuItemText, tidalReadings[ 0 ].getURL() )

        menuItemTexts = self.__createMenuItemTexts( tidalReadings )
        url = tidalReadings[ 0 ].getURL()
        if self.showAsSubMenus:
            firstTidalReading = True
            for item in menuItemTexts:
                if isinstance( item, str ):
                    if self.showAsSubMenusExceptFirstDay and firstTidalReading:
                        self.__createAndAppendMenuItem( menu, self.getMenuIndent( 1 ) + item, url )

                    else:
                        subMenu = Gtk.Menu()
                        self.__createAndAppendMenuItem( menu, self.getMenuIndent( 1 ) + item, None ).set_submenu( subMenu )

                else:
                    if self.showAsSubMenusExceptFirstDay and firstTidalReading:
                        firstTidalReading = False
                        for menuItemText in item:
                            self.__createAndAppendMenuItem( menu, self.getMenuIndent( 2 ) + menuItemText, url )

                    else:
                        for menuItemText in item:
                            self.__createAndAppendMenuItem( subMenu, self.getMenuIndent( 2 ) + menuItemText, url )

        else:
            for item in menuItemTexts:
                if isinstance( item, str ):
                    self.__createAndAppendMenuItem( menu, self.getMenuIndent( 1 ) + item, url )

                else:
                    for menuItemText in item:
                        self.__createAndAppendMenuItem( menu, self.getMenuIndent( 2 ) + menuItemText, url )


    # Returns a list of data...
    #    First element contains the menu item text representing the date for the first tidal reading.
    #    Second element contains a list of menu text items representing the tidal readings for the data in the previous element.
    #    Repeat...!
    def __createMenuItemTexts( self, tidalReadings ):
        menuItemTexts = [ ]
        allDateTimes = self.tidalReadingsAreAllDateTimes( tidalReadings )
        previousDate = datetime.datetime.utcnow().date().replace( year = 1900 ) # Set bogus year in the past.
        for tidalReading in tidalReadings:
            if allDateTimes:
                tidalDateTimeLocal = tidalReading.getDateTime().astimezone() # Date/time now in local time zone.

            else:
                tidalDateTimeLocal = tidalReading.getDateTime() # There may or may not be a time component; the result will be in port local.

            if tidalDateTimeLocal.date() != previousDate:
                menuItemText = tidalDateTimeLocal.strftime( self.menuItemDateFormat )
                menuItemTexts.append( menuItemText )
                previousDate = tidalDateTimeLocal.date()
                menuItemTexts.append( [ ] ) # Will hold the menu item text for each tidal reading for the current date.

            if isinstance( tidalDateTimeLocal, datetime.datetime ):
                menuItemText = tidalDateTimeLocal.strftime( self.menuItemTideFormat )

            else:
                menuItemText = self.menuItemTideFormatSansTime

            if tidalReading.getType() == tide.Type.H:
                menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, _( "H" ) )

            else: # The type must be either H or L - cannot be anything else.
                menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, _( "L" ) )

            if tidalReading.getLevelInMetres() is None:
                menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG, "" )

            else:
                menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG, str( tidalReading.getLevelInMetres() ) + " m" )

            menuItemTexts[ -1 ].append( menuItemText )

        return menuItemTexts


    def __createAndAppendMenuItem( self, menu, menuItemText, url ):
        menuItem = Gtk.MenuItem.new_with_label( menuItemText )
        menu.append( menuItem )

        if url:
            menuItem.connect( "activate", lambda widget: webbrowser.open( widget.props.name ) )
            daylightSavingsOffset = str( int( ( time.localtime().tm_gmtoff - -time.timezone ) / 60 ) )
            menuItem.set_name( url.replace( "DaylightSavingOffset=0", "DaylightSavingOffset=" + daylightSavingsOffset ) )

        return menuItem


    def tidalReadingsAreAllDateTimes( self, tidalReadings ):
        allDateTimes = True
        for tidalReading in tidalReadings:
            if not isinstance( tidalReading.getDateTime(), datetime.datetime ):
                allDateTimes = False
                break

        return allDateTimes


    def getNextUpdateTimeInSeconds( self, tidalReadings ):
        # UKHO appears to update port data at GMT midnight (so update shortly after GMT midnight).
        utcnow = datetime.datetime.utcnow()
        fiveMinutesAfterUTCMidnight = ( utcnow + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 )
        fiveMinutesAfterUTCMidnightInSeconds = ( fiveMinutesAfterUTCMidnight - utcnow ).total_seconds()

        # Remove stale data (data from days prior to user local today); only makes sense for ports with date/time.
        now = datetime.datetime.now()
        fiveMinutesAfterLocalMidnight = ( now + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 )
        fiveMinutesAfterLocalMidnightInSeconds = ( fiveMinutesAfterLocalMidnight - now ).total_seconds()

        if self.tidalReadingsAreAllDateTimes( tidalReadings ):
            nextUpdateTimeInSeconds = int( min( fiveMinutesAfterUTCMidnightInSeconds, fiveMinutesAfterLocalMidnightInSeconds ) )
        else:
            nextUpdateTimeInSeconds = fiveMinutesAfterUTCMidnightInSeconds

        return nextUpdateTimeInSeconds


    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

        # Port settings.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Country" ) ), False, False, 0 )

        countriesComboBox = Gtk.ComboBoxText()
        countriesComboBox.set_tooltip_text( _( "Choose your country." ) )
        countries = sorted( ports.getCountries() )
        for country in countries:
            countriesComboBox.append_text( country )

        box.pack_start( countriesComboBox, True, True, 1 )

        grid.attach( box, 0, 0, 1, 1 )

        COLUMN_PORT = 0

        portsList = Gtk.ListStore( str ) # Port.
        portsList.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        portsTree = Gtk.TreeView.new_with_model( portsList )
        portsTree.set_tooltip_text( _( "Choose your port." ) )
        portsTree.set_hexpand( True )
        portsTree.set_vexpand( True )
        portsTree.append_column( Gtk.TreeViewColumn( _( "Port" ), Gtk.CellRendererText(), text = COLUMN_PORT ) )
        portsTree.get_selection().set_mode( Gtk.SelectionMode.BROWSE )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( portsTree )

        countriesComboBox.connect( "changed", self.onCountry, portsList, portsTree )
        countriesComboBox.set_active( countries.index( ports.getCountry( self.portID ) ) )

        grid.attach( scrolledWindow, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Ports" ) ) )

        # General settings.
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

        box.pack_start( Gtk.Label.new( _( "Date format" ) ), False, False, 0 )

        dateFormat = Gtk.Entry()
        dateFormat.set_text( self.menuItemDateFormat )
        dateFormat.set_hexpand( True )
        dateFormat.set_tooltip_text( _(
            "Formatting options for the date:\n\n" + \
            "    https://docs.python.org/3/library/datetime.html\n\n" + \
            "Leave empty to reset back to default." ) )

        box.pack_start( dateFormat, True, True, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        label = Gtk.Label.new( _( "Tide format" ) )
        label.set_margin_top( 10 )
        label.set_halign( Gtk.Align.START )

        grid.attach( label, 0, 3, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label.new( _( "Default" ) ), False, False, 0 )

        tideFormat = Gtk.Entry()
        tideFormat.set_text( self.menuItemTideFormat )
        tideFormat.set_hexpand( True )
        tideFormat.set_tooltip_text( _(
            "Tide information is specified using:\n\n" + \
            "    {0} - the tide is high or low.\n" + \
            "    {1} - the tide level, measured in metres.\n\n" + \
            "Formatting options for the time:\n\n" + \
            "    https://docs.python.org/3/library/datetime.html\n\n" + \
            "Leave empty to reset back to default." ).format( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG ) )
        box.pack_start( tideFormat, True, True, 0 )

        grid.attach( box, 0, 4, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label.new( _( "Missing time" ) ), False, False, 0 )

        tideFormatSansTime = Gtk.Entry()
        tideFormatSansTime.set_text( self.menuItemTideFormatSansTime )
        tideFormatSansTime.set_hexpand( True )
        tideFormatSansTime.set_tooltip_text( _(
            "Tide information is specified using:\n\n" + \
            "    {0} - the tide is high or low.\n" + \
            "    {1} - the tide level, measured in metres.\n\n" + \
            "This format is used when there is no time\n" + \
            "component in a tide reading.\n\n" + \
            "Leave empty to reset back to default." ).format( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG ) )
        box.pack_start( tideFormatSansTime, True, True, 0 )

        grid.attach( box, 0, 5, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            country = countriesComboBox.get_active_text()
            model, treeiter = portsTree.get_selection().get_selected()
            port = model[ treeiter ][ COLUMN_PORT ]
            self.portID = ports.getPortIDForCountryAndPortName( country, port )
            self.showAsSubMenus = showAsSubmenusCheckbutton.get_active()
            self.showAsSubMenusExceptFirstDay = showAsSubmenusExceptFirstDayCheckbutton.get_active()

            if dateFormat.get_text():
                self.menuItemDateFormat = dateFormat.get_text()

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


    def onCountry( self, countriesComboBox, portsListStore, portsTree ):
        country = countriesComboBox.get_active_text()
        portsListStore.clear()
        portsList = sorted( ports.getPortNamesForCountry( country ) )
        for port in portsList:
            portsListStore.append( [ port ] )

        portIndex = "0"
        if ports.getCountry( self.portID ) == country:
            portIndex = str( portsList.index( ports.getPortName( self.portID ) ) )

        portsTree.get_selection().select_path( portIndex )
        portsTree.scroll_to_cell( Gtk.TreePath.new_from_string( portIndex ) )


    def loadConfig( self, config ):
        self.portName = config.get( IndicatorTide.CONFIG_PORT_NAME, "" ) #TODO Is "" okay for default?
        self.showAsSubMenus = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS, True )
        self.showAsSubMenusExceptFirstDay = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY, True )


    def saveConfig( self ):
        return {
            # IndicatorTide.CONFIG_MENU_ITEM_DATE_FORMAT : self.menuItemDateFormat,
            # IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT : self.menuItemTideFormat,
            # IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT_SANS_TIME : self.menuItemTideFormatSansTime,
            # IndicatorTide.CONFIG_PORT_ID : self.portID,
            # IndicatorTide.CONFIG_SHOW_AS_SUBMENUS : self.showAsSubMenus,
            # IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY : self.showAsSubMenusExceptFirstDay
        }


IndicatorTide().main()