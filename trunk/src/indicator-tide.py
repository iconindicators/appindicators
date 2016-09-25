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
gi.require_version( "AppIndicator3", "0.1" )

from gi.repository import AppIndicator3, GLib, Gtk
from urllib.request import urlopen

import datetime, json, locale, locations, logging, os, pythonutils, tide, webbrowser


class IndicatorTide:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.4"
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    EXPIRY = "2016-09-28" # The license for the UKHO data expires one year from 2015-09-28.
    URL_TIMEOUT_IN_SECONDS = 10

    COMMENTS = _( "Displays tidal information.\n(this software will expire after {0})" ).format( EXPIRY )
    CREDIT_UNITED_KINGDOM_HYDROGRAPHIC_OFFICE = _( "Tidal information reproduced by permission of the\nController of Her Majesty’s Stationery Office\nand the UK Hydrographic Office. http://www.ukho.gov.uk" )
    CREDITS = [ CREDIT_UNITED_KINGDOM_HYDROGRAPHIC_OFFICE ]

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_DAYLIGHT_SAVINGS_OFFSET = "daylightSavingsOffset"
    SETTINGS_MENU_ITEM_DATE_FORMAT = "menuItemDateFormat"
    SETTINGS_MENU_ITEM_TIDE_FORMAT = "menuItemTideFormat"
    SETTINGS_PORT_ID = "portID"
    SETTINGS_SHOW_AS_SUBMENUS = "showAsSubmenus"
    SETTINGS_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY = "showAsSubmenusExceptFirstDay"

    MENU_ITEM_DATE_DEFAULT_FORMAT = "%A, %d %B"
    MENU_ITEM_TIME_DEFAULT_FORMAT = "%I:%M %p"
    MENU_ITEM_TIDE_LEVEL_TAG = "[LEVEL]" # The level of the tide in metres.
    MENU_ITEM_TIDE_TYPE_TAG = "[TYPE]" # The tide type, either high or low.
    MENU_ITEM_TIDE_DEFAULT_FORMAT = MENU_ITEM_TIME_DEFAULT_FORMAT + "    " + MENU_ITEM_TIDE_TYPE_TAG + "    " + MENU_ITEM_TIDE_LEVEL_TAG


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorTide.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )

        self.dialog = None
        self.loadSettings()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorTide.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling!
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.update()


    def main( self ): Gtk.main()


    def buildMenu( self, tideReadings ):
        indent = "    "
        menu = Gtk.Menu()

        if tideReadings is None or len( tideReadings ) == 0:
            menu.append( Gtk.MenuItem( _( "No port data available for {0}!" ).format( locations.getPort( self.portID ).title() ) ) )
        else:
            previousMonth = -1
            previousDay = -1
            firstTideReading = True
            for tideReading in tideReadings:
                if firstTideReading:
                    firstMonth = tideReading.getMonth()
                    firstDay = tideReading.getDay()
                    self.createMenuItem( menu, tideReading.getPortName(), tideReading.getURL() )

                tideDateTime = datetime.datetime( datetime.datetime.now().year, tideReading.getMonth(), tideReading.getDay(), tideReading.getHour(), tideReading.getMinute(), 0 )

                if not( tideReading.getMonth() == previousMonth and tideReading.getDay() == previousDay ):
                    menuItemText = indent + tideDateTime.strftime( self.menuItemDateFormat )
                    if self.showAsSubMenus:
                        if self.showAsSubMenusExceptFirstDay and firstMonth == tideReading.getMonth() and firstDay == tideReading.getDay():
                            self.createMenuItem( menu, menuItemText, tideReading.getURL() )
                        else:
                            subMenu = Gtk.Menu()
                            self.createMenuItem( menu, menuItemText, None ).set_submenu( subMenu )
                    else:
                        self.createMenuItem( menu, menuItemText, tideReading.getURL() )

                menuItemText = tideDateTime.strftime( self.menuItemTideFormat )

                if tideReading.getType() == tide.Type.H:
                    menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, _( "H" ) )
                else:
                    menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, _( "L" ) )

                menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG, str( tideReading.getLevelInMetres() ) + " m" )

                if self.showAsSubMenus:
                    if self.showAsSubMenusExceptFirstDay and firstMonth == tideReading.getMonth() and firstDay == tideReading.getDay():
                        self.createMenuItem( menu, indent + indent + menuItemText, tideReading.getURL() )
                    else:
                        self.createMenuItem( subMenu, menuItemText, tideReading.getURL() )
                else:
                    self.createMenuItem( menu, indent + indent + menuItemText, tideReading.getURL() )

                firstTideReading = False
                previousMonth = tideReading.getMonth()
                previousDay = tideReading.getDay()

        pythonutils.createPreferencesAboutQuitMenuItems( menu, True, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def createMenuItem( self, menu, menuItemText, url ):
        menuItem = Gtk.MenuItem( menuItemText )

        if url is not None:
            menuItem.connect( "activate", self.onTideMenuItem )
            menuItem.set_name( url )

        menu.append( menuItem )
        return menuItem


    def update( self ):
        self.buildMenu( self.getTidalDataFromUnitedKingdomHydrographicOffice( self.portID, self.daylightSavingsOffset ) )
        self.timeoutID = GLib.timeout_add_seconds( self.getNextUpdateTimeInSeconds(), self.update )


    def onTideMenuItem( self, widget ): webbrowser.open( widget.props.name ) # This returns a boolean indicating success or failure - showing the user a message on a false return value causes a lock up!


    def getNextUpdateTimeInSeconds( self ):
        now = datetime.datetime.now()
        fiveMinutesAfterMidnight = ( now + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 ) # Tidal information (appears to be) updated not long after local midnight.
        numberOfSecondsUntilFiveMinutesAfterMidnight = ( fiveMinutesAfterMidnight - now ).total_seconds()
        numberOfSecondsInTwelveHours = 12 * 60 * 60 # Automatically update the tidal information at least every 12 hours.

        return int( min( numberOfSecondsInTwelveHours, numberOfSecondsUntilFiveMinutesAfterMidnight ) )


    def onAbout( self, widget ):
        if self.dialog is None:
            self.dialog = pythonutils.createAboutDialog(
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

            self.dialog.run()
            self.dialog.destroy()
            self.dialog = None
        else:
            self.dialog.present()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        grid = Gtk.Grid()
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Country" ) ), False, False, 0 )

        countriesComboBox = Gtk.ComboBoxText()
        countriesComboBox.set_tooltip_text( _( "Choose your country." ) )
        countries = sorted( locations.getCountries() )
        for country in countries:
            countriesComboBox.append_text( country )

        box.pack_start( countriesComboBox, True, True, 1 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box()

        ports = Gtk.ListStore( str ) # Port.
        ports.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        portsTree = Gtk.TreeView( ports )
        portsTree.set_tooltip_text( _( "Choose your port." ) )
        portsTree.set_hexpand( True )
        portsTree.set_vexpand( True )
        portsTree.append_column( Gtk.TreeViewColumn( _( "Port" ), Gtk.CellRendererText(), text = 0 ) )
        portsTree.get_selection().set_mode( Gtk.SelectionMode.BROWSE )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( portsTree )
 
        countriesComboBox.connect( "changed", self.onCountry, ports, portsTree )
        countriesComboBox.set_active( countries.index( locations.getCountry( self.portID ) ) )

        box.pack_start( scrolledWindow, True, True, 0 )

        grid.attach( box, 0, 1, 1, 20 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Daylight savings offset" ) ), False, False, 0 )

        spinnerDaylightSavingsOffset = Gtk.SpinButton()
        spinnerDaylightSavingsOffset.set_adjustment( Gtk.Adjustment( int( self.daylightSavingsOffset ), 0, 180, 1, 10, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerDaylightSavingsOffset.set_value( int( self.daylightSavingsOffset ) ) # ...so need to force the initial value by explicitly setting it.
        spinnerDaylightSavingsOffset.set_tooltip_text( _(
            "If your timezone is currently in daylight savings,\n" + \
            "specify the offset amount, in minutes." ) )

        box.pack_start( spinnerDaylightSavingsOffset, True, True, 1 )
        grid.attach( box, 0, 21, 1, 1 )

        box = Gtk.Box()
        box.set_margin_top( 10 )

        showAsSubmenusCheckbox = Gtk.CheckButton( _( "Show as submenus" ) )
        showAsSubmenusCheckbox.set_active( self.showAsSubMenus )
        showAsSubmenusCheckbox.set_tooltip_text( _( "Show each day's tides in a submenu." ) )

        box.pack_start( showAsSubmenusCheckbox, True, True, 1 )
        grid.attach( box, 0, 22, 1, 1 )

        box = Gtk.Box()

        showAsSubmenusExceptFirstDayCheckbox = Gtk.CheckButton( _( "Except first day" ) )
        showAsSubmenusExceptFirstDayCheckbox.set_sensitive( showAsSubmenusCheckbox.get_active() )
        showAsSubmenusExceptFirstDayCheckbox.set_active( self.showAsSubMenusExceptFirstDay )
        showAsSubmenusExceptFirstDayCheckbox.set_margin_left( 15 )
        showAsSubmenusExceptFirstDayCheckbox.set_tooltip_text( _( "Show the first day's tide in full." ) )

        box.pack_start( showAsSubmenusExceptFirstDayCheckbox, True, True, 1 )
        grid.attach( box, 0, 23, 1, 1 )

        showAsSubmenusCheckbox.connect( "toggled", self.onShowAsSubmenusCheckbox, showAsSubmenusExceptFirstDayCheckbox )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Date format" ) ), False, False, 0 )

        dateFormat = Gtk.Entry()
        dateFormat.set_text( self.menuItemDateFormat )
        dateFormat.set_tooltip_text( _(
            "Formatting options are specified at\n" + \
            "http://docs.python.org/3/library/datetime.html" ) )

        box.pack_start( dateFormat, True, True, 0 )

        grid.attach( box, 0, 24, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Tide format" ) ), False, False, 0 )

        tideFormat = Gtk.Entry()
        tideFormat.set_text( self.menuItemTideFormat )
        tideFormat.set_tooltip_text( _(
            "Tide information is specified using:\n\n" + \
            "    [TYPE] - the tide is high or low.\n" + \
            "    [LEVEL] - the tide level, measured in metres.\n\n" + \
            "Formatting options for the time are specified at\n" + \
            "http://docs.python.org/3/library/datetime.html" ) )
        box.pack_start( tideFormat, True, True, 0 )

        grid.attach( box, 0, 25, 1, 1 )

        box = Gtk.Box()
        box.set_margin_top( 10 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorTide.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )

        box.pack_start( autostartCheckbox, True, True, 1 )
        grid.attach( box, 0, 26, 1, 1 )

        self.dialog = Gtk.Dialog( _( "Preferences" ), None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( grid, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorTide.ICON )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            country = countriesComboBox.get_active_text()
            model, treeiter = portsTree.get_selection().get_selected()
            port = model[ treeiter ][ 0 ]
            self.portID = locations.getPortIDForCountryAndPort( country, port )
            self.daylightSavingsOffset = spinnerDaylightSavingsOffset.get_value_as_int()
            self.showAsSubMenus = showAsSubmenusCheckbox.get_active()
            self.showAsSubMenusExceptFirstDay = showAsSubmenusExceptFirstDayCheckbox.get_active()
            self.menuItemDateFormat = dateFormat.get_text().strip()
            self.menuItemTideFormat = tideFormat.get_text().strip()
            self.saveSettings()
            pythonutils.setAutoStart( IndicatorTide.DESKTOP_FILE, autostartCheckbox.get_active(), logging )

            GLib.source_remove( self.timeoutID )
            self.timeoutID = GLib.timeout_add_seconds( self.getNextUpdateTimeInSeconds(), self.update )
            self.update()

        self.dialog.destroy()
        self.dialog = None


    def onCountry( self, countriesComboBox, portsListStore, portsTree ):
        country = countriesComboBox.get_active_text()
        portsListStore.clear()
        ports = sorted( locations.getPortsForCountry( country ) ) 
        for port in ports:
            portsListStore.append( [ port ] )

        portIndex = "0"
        if locations.getCountry( self.portID ) == country:
            portIndex = str( ports.index( locations.getPort( self.portID ) ) )

        portsTree.get_selection().select_path( portIndex )
        portsTree.scroll_to_cell( Gtk.TreePath.new_from_string( portIndex ) )


    def onShowAsSubmenusCheckbox( self, source, showAsSubmenusExceptFirstDayCheckbox ):
        showAsSubmenusExceptFirstDayCheckbox.set_sensitive( source.get_active() )


    def loadSettings( self ):
        self.daylightSavingsOffset = "0"
        self.menuItemDateFormat = IndicatorTide.MENU_ITEM_DATE_DEFAULT_FORMAT
        self.menuItemTideFormat = IndicatorTide.MENU_ITEM_TIDE_DEFAULT_FORMAT
        self.portID = None
        self.showAsSubMenus = False
        self.showAsSubMenusExceptFirstDay = True

        if os.path.isfile( IndicatorTide.SETTINGS_FILE ):
            try:
                with open( IndicatorTide.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.daylightSavingsOffset = settings.get( IndicatorTide.SETTINGS_DAYLIGHT_SAVINGS_OFFSET, self.daylightSavingsOffset )
                self.menuItemDateFormat = settings.get( IndicatorTide.SETTINGS_MENU_ITEM_DATE_FORMAT, self.menuItemDateFormat )
                self.menuItemTideFormat = settings.get( IndicatorTide.SETTINGS_MENU_ITEM_TIDE_FORMAT, self.menuItemTideFormat )
                self.portID = settings.get( IndicatorTide.SETTINGS_PORT_ID, self.portID )
                self.showAsSubMenus = settings.get( IndicatorTide.SETTINGS_SHOW_AS_SUBMENUS, self.showAsSubMenus )
                self.showAsSubMenusExceptFirstDay = settings.get( IndicatorTide.SETTINGS_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY, self.showAsSubMenusExceptFirstDay )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorTide.SETTINGS_FILE )

        # Validate the port...
        if not locations.isValidPortID( self.portID ):
            country = None
            try: # Set a geographically sensible default...
                timezone = pythonutils.processGet( "cat /etc/timezone" )
                country = timezone[ 0 : timezone.find( "/" ) ]

            except Exception as e:
                logging.exception( e )
                logging.error( "Error getting country/city from timezone." )

            self.portID = locations.getPortIDForCountry( country )

        # Ensure the daylight savings is numeric and sensible...
        try:
            if int( self.daylightSavingsOffset ) < 0:
                self.daylightSavingsOffset = "0" 
        except ValueError:
            self.daylightSavingsOffset = "0" 

        # Ensure the daylight savings is numeric and sensible...
        try:
            bool( self.showAsSubMenus )
        except ValueError:
            self.showAsSubMenus = False

        if self.menuItemDateFormat is None:
            self.menuItemDateFormat = ""


    def saveSettings( self ):
        try:
            settings = {
                IndicatorTide.SETTINGS_DAYLIGHT_SAVINGS_OFFSET: self.daylightSavingsOffset,
                IndicatorTide.SETTINGS_MENU_ITEM_DATE_FORMAT: self.menuItemDateFormat,
                IndicatorTide.SETTINGS_MENU_ITEM_TIDE_FORMAT: self.menuItemTideFormat,
                IndicatorTide.SETTINGS_PORT_ID: self.portID,
                IndicatorTide.SETTINGS_SHOW_AS_SUBMENUS: self.showAsSubMenus,
                IndicatorTide.SETTINGS_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY: self.showAsSubMenusExceptFirstDay
            }

            with open( IndicatorTide.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorTide.SETTINGS_FILE )


#TODO
# Get the timezone from the computer (which reflects the current, possibly adjusted for Summer, timezone): date +%z
# Get the timezone from the UKHO page (which is NEVER adjusted).
# If the timezones match, burp if the DST offset != 0.
# If the timezones do not match, burp if the UKHO timezone != computer timezone + DST offset.  Ensure it works for -ve timezones (such as South America).


    def getTidalDataFromUnitedKingdomHydrographicOffice( self, portID, daylightSavingOffset ):
        tidalReadings = [ ]
        defaultLocale = locale.getlocale( locale.LC_TIME )
        locale.setlocale( locale.LC_ALL, "POSIX" ) # Used to convert the date in English to a DateTime object in a non-English locale.

        if portID[ -1 ].isalpha():
            portIDForURL = portID[ 0 : -1 ].rjust( 4, "0" ) + portID[ -1 ]
        else:
            portIDForURL = portID.rjust( 4, "0" )

        url = "http://www.ukho.gov.uk/easytide/EasyTide/ShowPrediction.aspx?PortID=" + \
               portIDForURL + "&PredictionLength=7&DaylightSavingOffset=" + \
               str( daylightSavingOffset ) + \
               "&PrinterFriendly=True&HeightUnits=0&GraphSize=7"

        try:
            today = datetime.datetime.now().replace( hour = 0, minute = 0, second = 0, microsecond = 0 )
            todayMonth = today.strftime( "%b" ).upper() # "SEP"
            lines = urlopen( url, timeout = IndicatorTide.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
            for index, line in enumerate( lines ):
                if "class=\"PortName\"" in line:
                    portName = line[ line.find( ">" ) + 1 : line.find( "</span>" ) ]
                    country = line[ line.find( "class=\"CountryPredSummary\">" ) + len( "class=\"CountryPredSummary\">" ) : line.find( "</span></li>" ) ]

                if "HWLWTableHeaderCell" in line:
                    tideDate = line[ line.find( ">" ) + 1 : line.find( "</th>" ) ] # "Sat 24 Sep"
                    tideMonth = tideDate[ -3 : ].upper() # "SEP"
                    tideYear = today.year
                    if tideMonth == "JAN" and todayMonth == "DEC":
                        tideYear = today.year + 1
                    elif tideMonth == "DEC" and todayMonth == "JAN":
                        tideYear = today.year - 1

                    tideDate = datetime.datetime.strptime( tideDate + " " + str( tideYear ), "%a %d %b %Y" )
                    if tideDate < today: # Only add data from today onward. 
                        continue

                    waterLevelTypes = [ ]
                    line = lines[ index + 2 ]
                    for item in line.split( "<th class=\"HWLWTableHWLWCellPrintFriendly\">" ):
                        if len( item.strip() ) > 0:
                            waterLevelTypes.append( item[ 0 : 1 ] )

                    times = [ ]
                    line = lines[ index + 4 ]
                    for item in line.split( "<td class=\"HWLWTableCellPrintFriendly\"> " ):
                        if len( item.strip() ) > 0:
                            times.append( item[ 0 : 5 ] )

                    waterLevelsInMetres = [ ]
                    line = lines[ index + 6 ]
                    for item in line.split( "<td class=\"HWLWTableCellPrintFriendly\">" ):
                        if len( item.strip() ) > 0:
                            waterLevelsInMetres.append( item[ 0 : 3 ] )

                    for index, item in enumerate( waterLevelTypes ):
                        tideTime = datetime.datetime.strptime( times[ index ], "%H:%M" )
                        tidalReadings.append( tide.Reading( ( portName + ", " + country ).title(), tideDate.month, tideDate.day, tideTime.hour, tideTime.minute, waterLevelsInMetres[ index ], waterLevelTypes[ index ], url ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error retrieving/parsing tidal data from " + str( url ) )
            tidalReadings = None

        locale.setlocale( locale.LC_TIME, defaultLocale )
        return tidalReadings


if __name__ == "__main__":
    if datetime.datetime.now().strftime( "%Y-%m-%d" ) >= IndicatorTide.EXPIRY:
        pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "The tidal data license has expired!\n\nPlease download the latest version of this software." ), INDICATOR_NAME )
    else:
        IndicatorTide().main()