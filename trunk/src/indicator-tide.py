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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Application indicator which displays tidal information.


INDICATOR_NAME = "indicator-tide"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gtk, Notify
from urllib.request import urlopen

import datetime, indicatorbase, locale, ports, re, tide, time, webbrowser


class IndicatorTide( indicatorbase.IndicatorBase ):

    CONFIG_MENU_ITEM_DATE_FORMAT = "menuItemDateFormat"
    CONFIG_MENU_ITEM_TIDE_FORMAT = "menuItemTideFormat"
    CONFIG_MENU_ITEM_TIDE_FORMAT_SANS_TIME = "menuItemTideFormatSansTime"
    CONFIG_PORT_ID = "portID"
    CONFIG_SHOW_AS_SUBMENUS = "showAsSubmenus"
    CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY = "showAsSubmenusExceptFirstDay"

    MENU_ITEM_DATE_DEFAULT_FORMAT = "%A, %d %B"
    MENU_ITEM_TIME_DEFAULT_FORMAT = "%I:%M %p"
    MENU_ITEM_TIDE_LEVEL_TAG = "[LEVEL]" # The level of the tide in metres.
    MENU_ITEM_TIDE_TYPE_TAG = "[TYPE]" # The tide type, either high or low.
    MENU_ITEM_TIDE_DEFAULT_FORMAT = MENU_ITEM_TIDE_TYPE_TAG + "    " + MENU_ITEM_TIME_DEFAULT_FORMAT + "    " + MENU_ITEM_TIDE_LEVEL_TAG
    MENU_ITEM_TIDE_DEFAULT_FORMAT_SANS_TIME = MENU_ITEM_TIDE_TYPE_TAG + "    " + MENU_ITEM_TIDE_LEVEL_TAG

    CACHE_BASENAME = "tidal-"
    CACHE_MAXIMUM_AGE_HOURS = 24


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.19",
            copyrightStartYear = "2015",
            comments = _( "Displays tidal information.\nPort data is licensed and will expire after {0}." ).format( ports.getExpiry() ),
            creditz = [ _( "© Crown Copyright and/or database rights.\nReproduced by permission of the\nController of Her Majesty’s Stationery Office and the\nUK Hydrographic Office. http://www.GOV.uk/UKHO" ),
                        _( "Click on any menu item to display the ‘Admiralty EasyTide’\nport page to verify the results produced." ) ] )

        if ports.isExpired():
            message = _(
                "The license for non-UK ports has expired. " + 
                "Until you upgrade to the latest version of the indicator, only UK ports will be available." )

            Notify.Notification.new( _( "Warning" ), message, self.icon ).show()
            self.getLogging().warning( message )


    def update( self, menu ):
        tidalReadings = self.getTidalData( self.portID )
        if tidalReadings:
            self.buildMenu( menu, tidalReadings )
            summary = _( "Tidal data ready" )
            message = _( "Tidal data is presented in the time zone of the port." )
            if self.tidalReadingsAreAllDateTimes( tidalReadings ):
                message = _( "Tidal data is presented in your local time zone." )

        else:
            menu.append( Gtk.MenuItem( _( "No tidal data available for {0}!" ).format( ports.getPortName( self.portID ) ) ) )
            summary = _( "Error" )
            message = _( "No tidal data available for {0}!" ).format( ports.getPortName( self.portID ) )
            self.getLogging().error( message )

        Notify.Notification.new( summary, message, self.icon ).show()

        return self.getNextUpdateTimeInSeconds( tidalReadings )


    def buildMenu( self, menu, tidalReadings ):
        menuItemText = _( "{0}, {1}" ).format( ports.getPortName( self.portID ), ports.getCountry( self.portID ) )
        self.createAndAppendMenuItem( menu, menuItemText, tidalReadings[ 0 ].getURL() )

        dateChangeIndices = [ ]
        currentMonthDay = str( tidalReadings[ 0 ].getDateTime().month ) + '-' + str( tidalReadings[ 0 ].getDateTime().day )
        for tidalReading in tidalReadings:
            tidalDateTimeLocal = tidalReading.getDateTime()
            print( tidalDateTimeLocal.month, tidalDateTimeLocal.day )

        return


        allDateTimes = self.tidalReadingsAreAllDateTimes( tidalReadings )
        previousMonth = -1
        previousDay = -1
        firstTidalReading = True # Used for subMenu build.
        for tidalReading in tidalReadings:
            if allDateTimes:
                tidalDateTimeLocal = tidalReading.getDateTime().astimezone() # Date/time now in local time zone.

            else:
                tidalDateTimeLocal = tidalReading.getDateTime() # There may or may not be a time component; the result will be in port local.

            if self.showAsSubMenus and firstTidalReading:
                firstMonth = tidalDateTimeLocal.month
                firstDay = tidalDateTimeLocal.day
                firstTidalReading = False

            if not( tidalDateTimeLocal.month == previousMonth and tidalDateTimeLocal.day == previousDay ):
                menuItemText = self.indent( 1, 1 ) + tidalDateTimeLocal.strftime( self.menuItemDateFormat )
                if self.showAsSubMenus:
                    if self.showAsSubMenusExceptFirstDay and firstMonth == tidalDateTimeLocal.month and firstDay == tidalDateTimeLocal.day:
                        self.createAndAppendMenuItem( menu, menuItemText, tidalReading.getURL() )

                    else:
                        subMenu = Gtk.Menu()
                        self.createAndAppendMenuItem( menu, menuItemText, None ).set_submenu( subMenu )

                else:
                    self.createAndAppendMenuItem( menu, menuItemText, tidalReading.getURL() )

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

            if self.showAsSubMenus:
                if self.showAsSubMenusExceptFirstDay and firstMonth == tidalDateTimeLocal.month and firstDay == tidalDateTimeLocal.day:
                    self.createAndAppendMenuItem( menu, self.indent( 2, 2 ) + menuItemText, tidalReading.getURL() )

                else:
                    self.createAndAppendMenuItem( subMenu, self.indent( 0, 2 ) + menuItemText, tidalReading.getURL() )

            else:
                self.createAndAppendMenuItem( menu, self.indent( 2, 2 ) + menuItemText, tidalReading.getURL() )

            previousMonth = tidalDateTimeLocal.month
            previousDay = tidalDateTimeLocal.day


    def buildMenuORIGINAL( self, menu, tidalReadings ):
        menuItemText = _( "{0}, {1}" ).format( ports.getPortName( self.portID ), ports.getCountry( self.portID ) )
        self.createAndAppendMenuItem( menu, menuItemText, tidalReadings[ 0 ].getURL() )
        allDateTimes = self.tidalReadingsAreAllDateTimes( tidalReadings )
        previousMonth = -1
        previousDay = -1
        firstTidalReading = True # Used for subMenu build.
        for tidalReading in tidalReadings:
            if allDateTimes:
                tidalDateTimeLocal = tidalReading.getDateTime().astimezone() # Date/time now in local time zone.

            else:
                tidalDateTimeLocal = tidalReading.getDateTime() # There may or may not be a time component; the result will be in port local.

            if self.showAsSubMenus and firstTidalReading:
                firstMonth = tidalDateTimeLocal.month
                firstDay = tidalDateTimeLocal.day
                firstTidalReading = False

            if not( tidalDateTimeLocal.month == previousMonth and tidalDateTimeLocal.day == previousDay ):
                menuItemText = self.indent( 1, 1 ) + tidalDateTimeLocal.strftime( self.menuItemDateFormat )
                if self.showAsSubMenus:
                    if self.showAsSubMenusExceptFirstDay and firstMonth == tidalDateTimeLocal.month and firstDay == tidalDateTimeLocal.day:
                        self.createAndAppendMenuItem( menu, menuItemText, tidalReading.getURL() )

                    else:
                        subMenu = Gtk.Menu()
                        self.createAndAppendMenuItem( menu, menuItemText, None ).set_submenu( subMenu )

                else:
                    self.createAndAppendMenuItem( menu, menuItemText, tidalReading.getURL() )

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

            if self.showAsSubMenus:
                if self.showAsSubMenusExceptFirstDay and firstMonth == tidalDateTimeLocal.month and firstDay == tidalDateTimeLocal.day:
                    self.createAndAppendMenuItem( menu, self.indent( 2, 2 ) + menuItemText, tidalReading.getURL() )

                else:
                    self.createAndAppendMenuItem( subMenu, self.indent( 0, 2 ) + menuItemText, tidalReading.getURL() )

            else:
                self.createAndAppendMenuItem( menu, self.indent( 2, 2 ) + menuItemText, tidalReading.getURL() )

            previousMonth = tidalDateTimeLocal.month
            previousDay = tidalDateTimeLocal.day


    def createAndAppendMenuItem( self, menu, menuItemText, url ):
        menuItem = Gtk.MenuItem( menuItemText )
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

        box.pack_start( Gtk.Label( _( "Country" ) ), False, False, 0 )

        countriesComboBox = Gtk.ComboBoxText()
        countriesComboBox.set_tooltip_text( _( "Choose your country." ) )
        countries = sorted( ports.getCountries() )
        for country in countries:
            countriesComboBox.append_text( country )

        box.pack_start( countriesComboBox, True, True, 1 )

        grid.attach( box, 0, 0, 1, 1 )

        portsList = Gtk.ListStore( str ) # Port.
        portsList.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        portsTree = Gtk.TreeView( portsList )
        portsTree.set_tooltip_text( _( "Choose your port." ) )
        portsTree.set_hexpand( True )
        portsTree.set_vexpand( True )
        portsTree.append_column( Gtk.TreeViewColumn( _( "Port" ), Gtk.CellRendererText(), text = 0 ) )
        portsTree.get_selection().set_mode( Gtk.SelectionMode.BROWSE )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( portsTree )

        countriesComboBox.connect( "changed", self.onCountry, portsList, portsTree )
        countriesComboBox.set_active( countries.index( ports.getCountry( self.portID ) ) )

        grid.attach( scrolledWindow, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Ports" ) ) )

        # General settings.
        grid = self.createGrid()

        showAsSubmenusCheckbox = Gtk.CheckButton( _( "Show as submenus" ) )
        showAsSubmenusCheckbox.set_active( self.showAsSubMenus )
        showAsSubmenusCheckbox.set_tooltip_text( _( "Show each day's tides in a submenu." ) )

        grid.attach( showAsSubmenusCheckbox, 0, 0, 1, 1 )

        showAsSubmenusExceptFirstDayCheckbox = Gtk.CheckButton( _( "Except first day" ) )
        showAsSubmenusExceptFirstDayCheckbox.set_sensitive( showAsSubmenusCheckbox.get_active() )
        showAsSubmenusExceptFirstDayCheckbox.set_active( self.showAsSubMenusExceptFirstDay )
        showAsSubmenusExceptFirstDayCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        showAsSubmenusExceptFirstDayCheckbox.set_tooltip_text( _( "Show the first day's tide in full." ) )

        grid.attach( showAsSubmenusExceptFirstDayCheckbox, 0, 1, 1, 1 )

        showAsSubmenusCheckbox.connect( "toggled", self.onShowAsSubmenusCheckbox, showAsSubmenusExceptFirstDayCheckbox )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Date format" ) ), False, False, 0 )

        dateFormat = Gtk.Entry()
        dateFormat.set_text( self.menuItemDateFormat )
        dateFormat.set_hexpand( True )
        dateFormat.set_tooltip_text( _(
            "Formatting options for the date:\n\n" + \
            "    http://docs.python.org/3/library/datetime.html\n\n" + \
            "Leave empty to reset back to default." ) )

        box.pack_start( dateFormat, True, True, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        label = Gtk.Label( _( "Tide format" ) )
        label.set_margin_top( 10 )
        label.set_halign( Gtk.Align.START )

        grid.attach( label, 0, 3, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label( _( "Default" ) ), False, False, 0 )

        tideFormat = Gtk.Entry()
        tideFormat.set_text( self.menuItemTideFormat )
        tideFormat.set_hexpand( True )
        tideFormat.set_tooltip_text( _(
            "Tide information is specified using:\n\n" + \
            "    {0} - the tide is high or low.\n" + \
            "    {1} - the tide level, measured in metres.\n\n" + \
            "Formatting options for the time:\n\n" + \
            "    http://docs.python.org/3/library/datetime.html\n\n" + \
            "Leave empty to reset back to default." ).format( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG ) )
        box.pack_start( tideFormat, True, True, 0 )

        grid.attach( box, 0, 4, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label( _( "Missing time" ) ), False, False, 0 )

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

        autostartCheckbox = self.createAutostartCheckbox() 
        grid.attach( autostartCheckbox, 0, 6, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            country = countriesComboBox.get_active_text()
            model, treeiter = portsTree.get_selection().get_selected()
            port = model[ treeiter ][ 0 ]
            self.portID = ports.getPortIDForCountryAndPortName( country, port )
            self.showAsSubMenus = showAsSubmenusCheckbox.get_active()
            self.showAsSubMenusExceptFirstDay = showAsSubmenusExceptFirstDayCheckbox.get_active()
            
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

            self.setAutoStart( autostartCheckbox.get_active() )

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


    def onShowAsSubmenusCheckbox( self, source, showAsSubmenusExceptFirstDayCheckbox ): showAsSubmenusExceptFirstDayCheckbox.set_sensitive( source.get_active() )


    def getTidalData( self, portID ):
        tidalReadings = [ ]
        self.removeOldFilesFromCache( IndicatorTide.CACHE_BASENAME, IndicatorTide.CACHE_MAXIMUM_AGE_HOURS )
        tidalReadings = self.readCacheBinary( IndicatorTide.CACHE_BASENAME ) # Either valid or None; empty data is never cached.
        if tidalReadings:
            tidalReadings = self.removeTidalReadingsPriorToToday( tidalReadings )
            if not tidalReadings:
                tidalReadings = None

        # Ensure the port ID is the same as that in the cached data.
        if tidalReadings:
            for tidalReading in list( tidalReadings ):
                if portID != tidalReading.getPortID():
                    tidalReadings.remove( tidalReading )

            if not tidalReadings:
                tidalReadings = None

        if tidalReadings is None: # There was no cached version or the cached version was stale; either way, need to do a download.
            tidalReadings = self.removeTidalReadingsPriorToToday( self.__getTidalDataFromUnitedKingdomHydrographicOffice( portID ) ) # Either empty or non-empty.
            if tidalReadings:
                self.writeCacheBinary( tidalReadings, IndicatorTide.CACHE_BASENAME )

        return tidalReadings


    def __getTidalDataFromUnitedKingdomHydrographicOffice( self, portID ):
        if portID[ -1 ].isalpha():
            portIDForURL = portID[ 0 : -1 ].rjust( 4, "0" ) + portID[ -1 ]

        else:
            portIDForURL = portID.rjust( 4, "0" )

        # Port IDs for testing...
        #    LW time missing: 1800, 1894A, 3983
        #    HW/LW time missing: 2168, 5088
        #    HW/LW reading is missing: 0839
        #    LW time/reading is missing: 4000, 3578
        #    HW/LW reading is missing; LW time is missing: 4273
        #    LW reading is negative: 1411
        #    UTC offset negative: 2168
        #    UTC offset positive: 4000

        url = "http://www.ukho.gov.uk/easytide/EasyTide/ShowPrediction.aspx?PortID=" + portIDForURL + \
              "&PredictionLength=7&DaylightSavingOffset=0&PrinterFriendly=True&HeightUnits=0&GraphSize=7"

        defaultLocale = locale.getlocale( locale.LC_TIME )
        locale.setlocale( locale.LC_TIME, "POSIX" ) # Used to convert the date in English to a DateTime object when in a non-English locale.

        try:
            tidalReadings = [ ]
            levelPositivePattern = re.compile( "^[0-9]\.[0-9]" )
            levelNegativePattern = re.compile( "^-?[0-9]\.[0-9]" )
            hourMinutePattern = re.compile( "^[0-9][0-9]:[0-9][0-9]" )
            lines = urlopen( url, timeout = self.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
            for index, line in enumerate( lines ): # The tidal data is presented in date/time order.

                if "Port predictions" in line: # Tidal dateTimes are in the standard local time of the port - need to obtain the UTC offset for the port in the format +HHMM or -HHMM.
                    if "equal to UTC" in line: # Example: "Port predictions (Standard Local Time) are equal to UTC"
                        utcOffset = "+0000"

                    elif "hour from UTC" in line or "hours from UTC" in line:
                        utcOffset = line[ line.index( "are" ) + 4 : line.index( "hour" ) - 1 ]
                        if len( utcOffset ) == 3: # Example: "Port predictions (Standard Local Time) are +10 hours from UTC"
                            utcOffset += "00"

                        else:
                            utcOffset = utcOffset[ 0 ] + "0" + utcOffset[ 1 ] + "00" # Example: "Port predictions (Standard Local Time) are -3 hours from UTC"

                    elif "mins from UTC" in line:
                        hours = line[ line.index( "are" ) + 4 : line.index( "hours" ) - 1 ] 
                        if len( hours ) == 2:
                            hours = hours[ 0 ] + "0" + hours[ 1 ]

                        minutes = line[ line.index( "hours" ) + 6 : line.index( "mins" ) - 1 ] 
                        utcOffset = hours + minutes

                    else:
                        raise ValueError( "Unable to obtain UTC from '" + line + "' in " + url )

                if "PredictionSummary1_lblPredictionStart" in line:
                    startDate = line[ line.index( "Today" ) + len( "Today - " ) : line.index( "<small>" ) ].strip().split() # Monday 17th July 2017 (standard local time of the port)
                    year = startDate[ 3 ] # 2017
                    startMonth = str( datetime.datetime.strptime( startDate[ 2 ], "%B" ).month ) # 7

                if "HWLWTableHeaderCell" in line:
                    date = line[ line.find( ">" ) + 1 : line.find( "</th>" ) ] # Mon 17 Jul (standard local time)
                    dayOfMonth = date[ 4 : 6 ] # 17
                    month = str( datetime.datetime.strptime( date[ -3 : ], "%b" ).month ) # 7
                    if month == "1" and startMonth == "12": # Account for the year change when rolling from December to January.
                        year = str( int( year ) + 1 )
                        startMonth = 1 # Set to January to stop the year from incrementing on each subsequent iteration.

                    types = [ ]
                    line = lines[ index + 2 ]
                    for item in line.split( "<th class=\"HWLWTableHWLWCellPrintFriendly\">" ):
                        if len( item.strip() ) > 0:
                            if item[ 0 ] == "H":
                                types.append( tide.Type.H )

                            elif item[ 0 ] == "L":
                                types.append( tide.Type.L )

                            else:
                                raise ValueError( "Unknown type '" + item[ 0 ] + "' in " + url )

                    dateTimes = [ ]
                    line = lines[ index + 4 ]
                    for item in line.split( "<td class=\"HWLWTableCellPrintFriendly\">" ):
                        if len( item.strip() ) > 0:
                            hourMinute = item.strip()[ 0 : 5 ]
                            if hourMinutePattern.match( hourMinute ):
                                dateTimes.append( datetime.datetime.strptime( year + " " + month +  " " + dayOfMonth +  " " + hourMinute + " " + utcOffset, "%Y %m %d %H:%M %z" ) )

                            else:
                                dateTimes.append( datetime.date( int( year ), int( month ), int( dayOfMonth ) ) ) # When no time is present, just add the date.

                    levels = [ ]
                    line = lines[ index + 6 ]
                    for item in line.split( "<td class=\"HWLWTableCellPrintFriendly\">" ):
                        if len( item.strip() ) > 0:
                            if levelPositivePattern.match( item ):
                                levels.append( float( item[ 0 : 3 ] ) )

                            elif levelNegativePattern.match( item ):
                                levels.append( float( item[ 0 : 4 ] ) )

                            else:
                                levels.append( None )

                    for index, tideType in enumerate( types ):
                        if levels[ index ] is None and isinstance( dateTimes[ index ], datetime.date ):
                            continue # Drop a tidal reading if missing both the time and level.

                        # As some ports only have the date component (no time is specified),
                        # can only store date/time in the port local timezone (rather than say, UTC).
                        if isinstance( dateTimes[ index ], datetime.datetime ):
                            tidalReadings.append( tide.Reading( portID, dateTimes[ index ].year, dateTimes[ index ].month, dateTimes[ index ].day, dateTimes[ index ].hour, dateTimes[ index ].minute, dateTimes[ index ].tzname()[ 3 : 6 ] + dateTimes[ index ].tzname()[ 7 : ], levels[ index ], tideType, url ) )

                        else:
                            tidalReadings.append( tide.Reading( portID, dateTimes[ index ].year, dateTimes[ index ].month, dateTimes[ index ].day, None, None, None, levels[ index ], tideType, url ) )

        except Exception as e:
            self.getLogging().exception( e )
            self.getLogging().error( "Error retrieving/parsing tidal data from " + str( url ) )
            tidalReadings = [ ]

        locale.setlocale( locale.LC_TIME, defaultLocale )

        return tidalReadings


    # If all tidal readings comprise both a date and time, convert each reading to user local date and time,
    # then remove a reading if prior to user local today.
    #
    # Otherwise, tidal readings contain a mix of date and date/time or are date only.
    # Compare each reading to UTC midnight date only and remove if older. 
    def removeTidalReadingsPriorToToday( self, tidalReadings ):
        if self.tidalReadingsAreAllDateTimes( tidalReadings ):
            todayLocalMidnight = datetime.datetime.now( datetime.timezone.utc ).astimezone().replace( hour = 0, minute = 0, second = 0 )
            for tidalReading in list( tidalReadings ):
                if tidalReading.getDateTime().astimezone() < todayLocalMidnight:
                    tidalReadings.remove( tidalReading )

        else:
            utcMidnightDate = datetime.datetime.utcnow().replace( hour = 0, minute = 0, second = 0 ).date()
            for tidalReading in list( tidalReadings ):
                if isinstance( tidalReading.getDateTime(), datetime.datetime ):
                    theDate = tidalReading.getDateTime().date()

                else:
                    theDate = tidalReading.getDateTime()

                if theDate < utcMidnightDate:
                    tidalReadings.remove( tidalReading )

        return tidalReadings


    def loadConfig( self, config ):
        self.menuItemDateFormat = config.get( IndicatorTide.CONFIG_MENU_ITEM_DATE_FORMAT, IndicatorTide.MENU_ITEM_DATE_DEFAULT_FORMAT )
        self.menuItemTideFormat = config.get( IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT, IndicatorTide.MENU_ITEM_TIDE_DEFAULT_FORMAT )
        self.menuItemTideFormatSansTime = config.get( IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT_SANS_TIME, IndicatorTide.MENU_ITEM_TIDE_DEFAULT_FORMAT_SANS_TIME )
        self.portID = config.get( IndicatorTide.CONFIG_PORT_ID, None )
        self.showAsSubMenus = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS, True )
        self.showAsSubMenusExceptFirstDay = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY, True )

        # Validate the port...
        if not ports.isValidPortID( self.portID ):
            try: # Set a geographically sensible default...
                timezone = self.processGet( "cat /etc/timezone" )
                country = timezone[ 0 : timezone.find( "/" ) ]

            except Exception as e:
                self.getLogging().exception( e )
                self.getLogging().error( "Error getting country/city from timezone." )
                country = ""

            self.portID = ports.getPortIDForCountry( country )
            if self.portID is None:
                self.portID = ports.getFirstPortID()


    def saveConfig( self ):
        return {
            IndicatorTide.CONFIG_MENU_ITEM_DATE_FORMAT: self.menuItemDateFormat,
            IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT: self.menuItemTideFormat,
            IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT_SANS_TIME: self.menuItemTideFormatSansTime,
            IndicatorTide.CONFIG_PORT_ID: self.portID,
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS: self.showAsSubMenus,
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY: self.showAsSubMenusExceptFirstDay
        }


IndicatorTide().main()