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


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://developer.gnome.org/gnome-devel-demos
#  http://python-gtk-3-tutorial.readthedocs.org
#  http://wiki.gnome.org/Projects/PyGObject/Threading
#  http://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/AppIndicator3-0.1
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://www.ukho.gov.uk/easytide


INDICATOR_NAME = "indicator-tide"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "Notify", "0.7" )

from gi.repository import AppIndicator3, GLib, Gtk, Notify
from urllib.request import urlopen
import datetime, json, locale, logging, os, ports, pythonutils, re, threading, tide, time, webbrowser


#TODO Renew license!


# #TODO
# Should indicator files go into .config?
# The directory exists under Ubuntu GNOME and Ubuntu 14.04.
# If so, apply to all indicators!


class IndicatorTide:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.8"
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"
    COMMENTS = _( "Displays tidal information.\nNon-UK ports will be unavailable after {0}." ).format( ports.getExpiry() )

#TODO This should not be translated...check with Oleg.
    CREDIT_UKHO_UK_PORTS = _( "Tidal information for UK ports licensed under the Open\nGovernment Licence for Public Sector Information. http://www.nationalarchives.gov.uk/doc/open-government-licence" )
    CREDIT_UKHO_UK_NON_PORTS = _( "Tidal information for non-UK ports reproduced by\npermission of the Controller of Her Majesty’s Stationery\nOffice and the UK Hydrographic Office. http://www.ukho.gov.uk" )
    CREDITS = [ CREDIT_UKHO_UK_PORTS, CREDIT_UKHO_UK_NON_PORTS ]

    URL_TIMEOUT_IN_SECONDS = 10

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


    def __init__( self ):
        logging.basicConfig( format = pythonutils.LOGGING_BASIC_CONFIG_FORMAT, level = pythonutils.LOGGING_BASIC_CONFIG_LEVEL, handlers = [ pythonutils.TruncatedFileHandler( IndicatorTide.LOG ) ] )
        self.dialogLock = threading.Lock()

        Notify.init( INDICATOR_NAME )
        pythonutils.migrateConfig( INDICATOR_NAME ) # Migrate old user configuration to new location.
        self.loadConfig()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorTide.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling!
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

        self.update( True )

        if ports.isExpired():
            message = _(
                "The license for non-UK ports has expired. " + 
                "Until you upgrade to the latest version of the indicator, only UK ports will be available." )

            Notify.Notification.new( _( "Warning" ), message, IndicatorTide.ICON ).show()


    def main( self ): Gtk.main()


    def update( self, scheduled ):
        with threading.Lock():
            if not scheduled:
                GLib.source_remove( self.updateTimerID )

            tidalReadings = self.getTidalDataFromUnitedKingdomHydrographicOffice( self.portID )
            if len( tidalReadings ) == 0:
                message = _( "No port data available for {0}!" ).format( ports.getPortName( self.portID ) )
                Notify.Notification.new( _( "Error" ), message, IndicatorTide.ICON ).show()

            self.buildMenu( tidalReadings )
            self.updateTimerID = GLib.timeout_add_seconds( self.getNextUpdateTimeInSeconds(), self.update, True )


    def buildMenu( self, tidalReadings ):
        menu = Gtk.Menu()
        if len( tidalReadings ) == 0:
            menu.append( Gtk.MenuItem( _( "No port data available for {0}!" ).format( ports.getPortName( self.portID ) ) ) )
        else:
            menuItemText = _( "{0}, {1}" ).format( ports.getPortName( tidalReadings[ 0 ].getPortID() ), ports.getCountry( tidalReadings[ 0 ].getPortID() ) )
            self.createAndAppendMenuItem( menu, menuItemText, tidalReadings[ 0 ].getURL() )
            self._buildMenu( menu, "    ", tidalReadings )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, True, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def _buildMenu( self, menu, indent, tidalReadings ):
        previousMonth = -1
        previousDay = -1
        firstTidalReading = True # Used for subMenu build.
        for tidalReading in tidalReadings:
            if isinstance( tidalReading.getDateTime(), datetime.datetime ):
                tidalDateTimeLocal = tidalReading.getDateTime().astimezone() # Date/time now in local time zone.
            else:
                tidalDateTimeLocal = tidalReading.getDateTime() # There is no time component.

            if self.showAsSubMenus and firstTidalReading:
                firstMonth = tidalDateTimeLocal.month
                firstDay = tidalDateTimeLocal.day
                firstTidalReading = False

            if not( tidalDateTimeLocal.month == previousMonth and tidalDateTimeLocal.day == previousDay ):
                menuItemText = indent + tidalDateTimeLocal.strftime( self.menuItemDateFormat )
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
                    self.createAndAppendMenuItem( menu, indent + indent + menuItemText, tidalReading.getURL() )
                else:
                    self.createAndAppendMenuItem( subMenu, menuItemText, tidalReading.getURL() )
            else:
                self.createAndAppendMenuItem( menu, indent + indent + menuItemText, tidalReading.getURL() )

            previousMonth = tidalDateTimeLocal.month
            previousDay = tidalDateTimeLocal.day


    def createAndAppendMenuItem( self, menu, menuItemText, url ):
        menuItem = Gtk.MenuItem( menuItemText )
        menu.append( menuItem )

        if url is not None:
            menuItem.connect( "activate", lambda widget: webbrowser.open( widget.props.name ) ) # This returns a boolean indicating success or failure - showing the user a message on a false return value causes a dialog lock up!
            menuItem.set_name( url )

        return menuItem


    def getNextUpdateTimeInSeconds( self ):
        # UKHO appears to update port data at GMT midnight.
        # Do an update shortly after GMT midnight but also shortly after local midnight to drop stale data.
        utcnow = datetime.datetime.utcnow()
        fiveMinutesAfterUTCMidnight = ( utcnow + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 )
        numberOfSecondsUntilFiveMinutesAfterUTCMidnight = ( fiveMinutesAfterUTCMidnight - utcnow ).total_seconds()

        now = datetime.datetime.now()
        fiveMinutesAfterLocalMidnight = ( now + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 )
        numberOfSecondsUntilFiveMinutesAfterLocalMidnight = ( fiveMinutesAfterLocalMidnight - now ).total_seconds()

        return int( min( numberOfSecondsUntilFiveMinutesAfterUTCMidnight, numberOfSecondsUntilFiveMinutesAfterLocalMidnight ) )


    def onAbout( self, widget ):
        if self.dialogLock.acquire( blocking = False ):
            pythonutils.showAboutDialog(
                [ IndicatorTide.AUTHOR ],
                IndicatorTide.COMMENTS, 
                IndicatorTide.CREDITS,
                _( "Credits" ),
                Gtk.License.GPL_3_0,
                IndicatorTide.ICON,
                INDICATOR_NAME,
                IndicatorTide.WEBSITE,
                IndicatorTide.VERSION,
                _( "translator-credits" ),
                _( "View the" ),
                _( "text file." ),
                _( "changelog" ) )

            self.dialogLock.release()


    def onPreferences( self, widget ):
        if self.dialogLock.acquire( blocking = False ):
            self._onPreferences( widget )
            self.dialogLock.release()


    def _onPreferences( self, widget ):
        notebook = Gtk.Notebook()

        # Port settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

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
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showAsSubmenusCheckbox = Gtk.CheckButton( _( "Show as submenus" ) )
        showAsSubmenusCheckbox.set_active( self.showAsSubMenus )
        showAsSubmenusCheckbox.set_tooltip_text( _( "Show each day's tides in a submenu." ) )

        grid.attach( showAsSubmenusCheckbox, 0, 0, 1, 1 )

        showAsSubmenusExceptFirstDayCheckbox = Gtk.CheckButton( _( "Except first day" ) )
        showAsSubmenusExceptFirstDayCheckbox.set_sensitive( showAsSubmenusCheckbox.get_active() )
        showAsSubmenusExceptFirstDayCheckbox.set_active( self.showAsSubMenusExceptFirstDay )
        showAsSubmenusExceptFirstDayCheckbox.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )
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
            "    http://docs.python.org/3/library/datetime.html" ) )

        box.pack_start( dateFormat, True, True, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        label = Gtk.Label( _( "Tide format" ) )
        label.set_margin_top( 10 )
        label.set_halign( Gtk.Align.START )

        grid.attach( label, 0, 3, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label( _( "General" ) ), False, False, 0 )

        tideFormat = Gtk.Entry()
        tideFormat.set_text( self.menuItemTideFormat )
        tideFormat.set_hexpand( True )
        tideFormat.set_tooltip_text( _(
            "Tide information is specified using:\n\n" + \
            "    [TYPE] - the tide is high or low.\n" + \
            "    [LEVEL] - the tide level, measured in metres.\n\n" + \
            "Formatting options for the time:\n\n" + \
            "    http://docs.python.org/3/library/datetime.html" ) )
        box.pack_start( tideFormat, True, True, 0 )

        grid.attach( box, 0, 4, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label( _( "Missing time" ) ), False, False, 0 )

        tideFormatSansTime = Gtk.Entry()
        tideFormatSansTime.set_text( self.menuItemTideFormatSansTime )
        tideFormatSansTime.set_hexpand( True )
        tideFormatSansTime.set_tooltip_text( _(
            "Tide information is specified using:\n\n" + \
            "    [TYPE] - the tide is high or low.\n" + \
            "    [LEVEL] - the tide level, measured in metres.\n\n" + \
            "This format is used when a tide reading\n" + \
            "contains no time component." ) )
        box.pack_start( tideFormatSansTime, True, True, 0 )

        grid.attach( box, 0, 5, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorTide.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 6, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        dialog = Gtk.Dialog( _( "Preferences" ), None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorTide.ICON )
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            country = countriesComboBox.get_active_text()
            model, treeiter = portsTree.get_selection().get_selected()
            port = model[ treeiter ][ 0 ]
            self.portID = ports.getPortIDForCountryAndPortName( country, port )
            self.showAsSubMenus = showAsSubmenusCheckbox.get_active()
            self.showAsSubMenusExceptFirstDay = showAsSubmenusExceptFirstDayCheckbox.get_active()
            self.menuItemDateFormat = dateFormat.get_text()
            self.menuItemTideFormat = tideFormat.get_text()
            self.menuItemTideFormatSansTime = tideFormatSansTime.get_text()
            self.saveConfig()
            pythonutils.setAutoStart( IndicatorTide.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            GLib.idle_add( self.update, False )

        dialog.destroy()


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


    def loadConfig( self ):
        self.menuItemDateFormat = IndicatorTide.MENU_ITEM_DATE_DEFAULT_FORMAT
        self.menuItemTideFormat = IndicatorTide.MENU_ITEM_TIDE_DEFAULT_FORMAT
        self.menuItemTideFormatSansTime = IndicatorTide.MENU_ITEM_TIDE_DEFAULT_FORMAT_SANS_TIME
        self.portID = None
        self.showAsSubMenus = True
        self.showAsSubMenusExceptFirstDay = True

        config = pythonutils.loadConfig( INDICATOR_NAME, INDICATOR_NAME, logging )

        self.menuItemDateFormat = config.get( IndicatorTide.CONFIG_MENU_ITEM_DATE_FORMAT, self.menuItemDateFormat )
        self.menuItemTideFormat = config.get( IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT, self.menuItemTideFormat )
        self.menuItemTideFormatSansTime = config.get( IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT_SANS_TIME, self.menuItemTideFormatSansTime )
        self.portID = config.get( IndicatorTide.CONFIG_PORT_ID, self.portID )
        self.showAsSubMenus = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS, self.showAsSubMenus )
        self.showAsSubMenusExceptFirstDay = config.get( IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY, self.showAsSubMenusExceptFirstDay )

        # Validate the port...
        if not ports.isValidPortID( self.portID ):
            try: # Set a geographically sensible default...
                timezone = pythonutils.processGet( "cat /etc/timezone" )
                country = timezone[ 0 : timezone.find( "/" ) ]

            except Exception as e:
                logging.exception( e )
                logging.error( "Error getting country/city from timezone." )
                country = ""

            self.portID = ports.getPortIDForCountry( country )
            if self.portID is None:
                self.portID = ports.getFirstPortID()


    def saveConfig( self ):
        config = {
            IndicatorTide.CONFIG_MENU_ITEM_DATE_FORMAT: self.menuItemDateFormat,
            IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT: self.menuItemTideFormat,
            IndicatorTide.CONFIG_MENU_ITEM_TIDE_FORMAT_SANS_TIME: self.menuItemTideFormatSansTime,
            IndicatorTide.CONFIG_PORT_ID: self.portID,
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS: self.showAsSubMenus,
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY: self.showAsSubMenusExceptFirstDay
        }

        pythonutils.saveConfig( config, INDICATOR_NAME, INDICATOR_NAME, logging )


    def getTidalDataFromUnitedKingdomHydrographicOffice( self, portID ):
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
            lines = urlopen( url, timeout = IndicatorTide.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
            for index, line in enumerate( lines ): # The tidal data is presented in date/time order.

                if "Port predictions" in line: # Tidal dateTimes are in the standard local time of the port - need to obtain the UTC offset for the port in the format +HHMM or -HHMM.
                    if "equal to UTC" in line: # "Port predictions (Standard Local Time) are equal to UTC"
                        utcOffset = "+0000"

                    elif "hour from UTC" in line or "hours from UTC" in line:
                        utcOffset = line[ line.index( "are" ) + 4 : line.index( "hour" ) - 1 ]
                        if len( utcOffset ) == 3: # "Port predictions (Standard Local Time) are +10 hours from UTC"
                            utcOffset += "00"
                        else:
                            utcOffset = utcOffset[ 0 ] + "0" + utcOffset[ 1 ] + "00" # "Port predictions (Standard Local Time) are -3 hours from UTC"

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
                    if month < startMonth: # Take into account tidal data changing from December to January.
                        year = startYear + 1

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
                        # can only store date/time in the port local timezone rather than UTC.
                        if isinstance( dateTimes[ index ], datetime.datetime ):
                            tidalReadings.append( tide.Reading( portID, dateTimes[ index ].year, dateTimes[ index ].month, dateTimes[ index ].day, dateTimes[ index ].hour, dateTimes[ index ].minute, dateTimes[ index ].tzname()[ 3 : 6 ] + dateTimes[ index ].tzname()[ 7 : ], levels[ index ], tideType, url ) )
                        else:
                            tidalReadings.append( tide.Reading( portID, dateTimes[ index ].year, dateTimes[ index ].month, dateTimes[ index ].day, None, None, None, levels[ index ], tideType, url ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error retrieving/parsing tidal data from " + str( url ) )
            tidalReadings = [ ]

#TODO Test all ports from above:
#     Check subMenus and not subMenus option.
#     Verify dates/times
        for t in tidalReadings: print( t ) # TODO Ensure raw data is correctly scraped.

        locale.setlocale( locale.LC_TIME, defaultLocale )

        return self.washTidalDataThroughCache( self.removeTidalReadingsPriorToToday( tidalReadings ) )


    def removeTidalReadingsPriorToToday( self, tidalReadings ):
#TODO Not sure how this should now work given the use of either datetime or just dates.
# Maybe only touch tidal readings containing datetime and leave those with date alone?
#Perhaps for date only tidal readings, compare each date (which is in the port's local timezone)
#to the current date of the port...does that make sense?
        if True: return tidalReadings
        
        todayLocalMidnight = datetime.datetime.now( datetime.timezone.utc ).astimezone().replace( hour = 0, minute = 0, second = 0 )
        for tidalReading in list( tidalReadings ):

            if isinstance( tidalReading.getDateTime(), datetime.datetime ):
                if tidalReading.getDateTime().astimezone() < todayLocalMidnight:
                    tidalReadings.remove( tidalReading )

            else:
                if tidalReading.getDateTime() < todayLocalMidnight.date():
                    tidalReadings.remove( tidalReading )

        return tidalReadings


    # Takes a list of tidal readings and...
    # If there is data, write to the cache.  It is assumed that all the tidal data is date sorted and of today's date or newer.
    # If there is no data, read from the cache (discarding data older than today).
    def washTidalDataThroughCache( self, tidalReadings ):
        cachePath = os.getenv( "HOME" ) + "/.cache/" + INDICATOR_NAME + "/"
        cacheDateBasename = "tidal-"
        cacheMaximumDateTime = datetime.datetime.now() - datetime.timedelta( hours = ( 24 * 8 ) ) # The UKHO shows tidal readings for one week from today.

        if len( tidalReadings ) > 0:
            pythonutils.writeToCache( tidalReadings, cachePath, cacheDateBasename, cacheMaximumDateTime, logging )
        else:
            tidalReadings, cacheDateTime = pythonutils.readFromCache( cachePath, cacheDateBasename, cacheMaximumDateTime, logging )
            if tidalReadings is None or len( tidalReadings ) == 0:
                tidalReadings = [ ]

            tidalReadings = self.removeTidalReadingsPriorToToday( tidalReadings )

        return tidalReadings


if __name__ == "__main__": IndicatorTide().main()