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


INDICATOR_NAME = "indicator-tide"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "Notify", "0.7" )

from gi.repository import AppIndicator3, GLib, Gtk, Notify
from urllib.request import urlopen
import datetime, json, locale, logging, os, ports, pythonutils, threading, tide, time, webbrowser


class IndicatorTide:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.8"
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"
    COMMENTS = _( "Displays tidal information.\nNon-UK ports will be unavailable after {0}." ).format( ports.getExpiry() )
    CREDIT_UKHO_UK_PORTS =     _( "Tidal information for UK ports licensed under the\nOpen Government Licence for Public Sector Information. http://www.nationalarchives.gov.uk/doc/open-government-licence" )
    CREDIT_UKHO_UK_NON_PORTS = _( "Tidal information for non-UK ports reproduced by\npermission of the Controller of Her Majesty’s Stationery Office\nand the UK Hydrographic Office. http://www.ukho.gov.uk" )
    CREDITS = [ CREDIT_UKHO_UK_PORTS, CREDIT_UKHO_UK_NON_PORTS ]

    URL_TIMEOUT_IN_SECONDS = 10

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
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
        self.dialogLock = threading.Lock()

        Notify.init( INDICATOR_NAME )
        self.loadSettings()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorTide.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling!
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

        self.scheduledUpdate()

        if ports.isExpired():
            message = _(
                "The license for non-UK ports has expired. " + 
                "Until you upgrade to the latest version of the indicator, only UK ports will be available." )

            Notify.Notification.new( _( "Warning" ), message, IndicatorTide.ICON ).show()


    def main( self ): Gtk.main()


    def buildMenu( self, tidalReadings ):
        indent = "    "
        menu = Gtk.Menu()

        if tidalReadings is None or len( tidalReadings ) == 0:
            menu.append( Gtk.MenuItem( _( "No port data available for {0}!" ).format( ports.getPortName( self.portID ) ) ) )
        else:
            previousMonth = -1
            previousDay = -1
            firstTideReading = True
            for tideReading in tidalReadings:
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


    def onTideMenuItem( self, widget ): webbrowser.open( widget.props.name ) # This returns a boolean indicating success or failure - showing the user a message on a false return value causes a dialogLock up!


    # Called ad hoc when an update needs to be forced - internally clears the existing timer.
    def unscheduledUpdate( self ):
        with threading.Lock():
            GLib.source_remove( self.updateTimerID )
            self._update()


    # Called from a timer event only.
    def scheduledUpdate( self ):
        with threading.Lock():
            self._update()


    def _update( self ):
        tidalReadings = self.getTidalDataFromUnitedKingdomHydrographicOffice( self.portID, self.getDaylightSavingsOffsetInMinutes() )
        self.buildMenu( tidalReadings )
        self.updateTimerID = GLib.timeout_add_seconds( self.getNextUpdateTimeInSeconds(), self.scheduledUpdate )

        if tidalReadings is None or len( tidalReadings ) == 0:
            message = _( "No port data available for {0}!" ).format( ports.getPortName( self.portID ) )
            Notify.Notification.new( _( "Error" ), message, IndicatorTide.ICON ).show()


    # Determines if the computer is currently in daylight savings or not (for the given time zone)
    # and if so, computer the offset amount in minutes.
    # If the computer is not in daylight savings, the offset is zero.
    # http://stackoverflow.com/questions/13464009/calculate-tm-isdst-from-date-and-timezone
    def getDaylightSavingsOffsetInMinutes( self ):
        offsetInMinutes = 0
        isDST = time.daylight and time.localtime().tm_isdst > 0
        if isDST:
            utcOffsetInSecondsDST = - ( time.altzone if isDST else time.timezone )
            utcOffsetInSeconds = - ( time.altzone if not isDST else time.timezone )
            offsetInMinutes = int( ( utcOffsetInSecondsDST - utcOffsetInSeconds ) / 60 )

        return offsetInMinutes


    def getNextUpdateTimeInSeconds( self ):
        now = datetime.datetime.now()
        fiveMinutesAfterMidnight = ( now + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 ) # Tidal information (appears to be) updated not long after local midnight.
        numberOfSecondsUntilFiveMinutesAfterMidnight = ( fiveMinutesAfterMidnight - now ).total_seconds()
        numberOfSecondsInTwelveHours = 12 * 60 * 60 # Automatically update the tidal information at least every 12 hours.

        return int( min( numberOfSecondsInTwelveHours, numberOfSecondsUntilFiveMinutesAfterMidnight ) )


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
            self._onPreferencesInternal( widget )
            self.dialogLock.release()


    def _onPreferencesInternal( self, widget ):
        notebook = Gtk.Notebook()

        # Port settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )
        grid.set_row_homogeneous( False )
        grid.set_column_homogeneous( False )

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
        showAsSubmenusExceptFirstDayCheckbox.set_margin_left( 15 )
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
            "Formatting options are specified at\n" + \
            "http://docs.python.org/3/library/datetime.html" ) )

        box.pack_start( dateFormat, True, True, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Tide format" ) ), False, False, 0 )

        tideFormat = Gtk.Entry()
        tideFormat.set_text( self.menuItemTideFormat )
        tideFormat.set_hexpand( True )
        tideFormat.set_tooltip_text( _(
            "Tide information is specified using:\n\n" + \
            "    [TYPE] - the tide is high or low.\n" + \
            "    [LEVEL] - the tide level, measured in metres.\n\n" + \
            "Formatting options for the time are specified at\n" + \
            "http://docs.python.org/3/library/datetime.html" ) )
        box.pack_start( tideFormat, True, True, 0 )

        grid.attach( box, 0, 3, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorTide.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 4, 1, 1 )

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
            self.menuItemDateFormat = dateFormat.get_text().strip()
            self.menuItemTideFormat = tideFormat.get_text().strip()
            self.saveSettings()
            pythonutils.setAutoStart( IndicatorTide.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            GLib.idle_add( self.unscheduledUpdate )

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


    def loadSettings( self ):
        self.menuItemDateFormat = IndicatorTide.MENU_ITEM_DATE_DEFAULT_FORMAT
        self.menuItemTideFormat = IndicatorTide.MENU_ITEM_TIDE_DEFAULT_FORMAT
        self.portID = None
        self.showAsSubMenus = True
        self.showAsSubMenusExceptFirstDay = True

        if os.path.isfile( IndicatorTide.SETTINGS_FILE ):
            try:
                with open( IndicatorTide.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.menuItemDateFormat = settings.get( IndicatorTide.SETTINGS_MENU_ITEM_DATE_FORMAT, self.menuItemDateFormat )
                self.menuItemTideFormat = settings.get( IndicatorTide.SETTINGS_MENU_ITEM_TIDE_FORMAT, self.menuItemTideFormat )
                self.portID = settings.get( IndicatorTide.SETTINGS_PORT_ID, self.portID )
                self.showAsSubMenus = settings.get( IndicatorTide.SETTINGS_SHOW_AS_SUBMENUS, self.showAsSubMenus )
                self.showAsSubMenusExceptFirstDay = settings.get( IndicatorTide.SETTINGS_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY, self.showAsSubMenusExceptFirstDay )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorTide.SETTINGS_FILE )

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

        if self.menuItemDateFormat is None:
            self.menuItemDateFormat = IndicatorTide.MENU_ITEM_DATE_DEFAULT_FORMAT

        if self.menuItemTideFormat is None:
            self.menuItemTideFormat = MENU_ITEM_TIDE_DEFAULT_FORMAT


    def saveSettings( self ):
        settings = {
            IndicatorTide.SETTINGS_MENU_ITEM_DATE_FORMAT: self.menuItemDateFormat,
            IndicatorTide.SETTINGS_MENU_ITEM_TIDE_FORMAT: self.menuItemTideFormat,
            IndicatorTide.SETTINGS_PORT_ID: self.portID,
            IndicatorTide.SETTINGS_SHOW_AS_SUBMENUS: self.showAsSubMenus,
            IndicatorTide.SETTINGS_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY: self.showAsSubMenusExceptFirstDay
        }

        try:
            with open( IndicatorTide.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorTide.SETTINGS_FILE )


    def getTidalDataFromUnitedKingdomHydrographicOffice( self, portID, daylightSavingOffset ):
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
            tidalReadings = [ ]
            today = datetime.datetime.now().replace( hour = 0, minute = 0, second = 0, microsecond = 0 )
            todayMonth = today.strftime( "%b" ).upper() # "SEP"
            lines = urlopen( url, timeout = IndicatorTide.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
            for index, line in enumerate( lines ):
                if "class=\"PortName\"" in line:
                    portName = line[ line.find( ">" ) + 1 : line.find( "</span>" ) ].title()
                    country = line[ line.find( "class=\"CountryPredSummary\">" ) + len( "class=\"CountryPredSummary\">" ) : line.find( "</span></li>" ) ].title()

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
                    for item in line.split( "<td class=\"HWLWTableCellPrintFriendly\">" ):
                        if len( item.strip() ) > 0:
                            times.append( item[ 0 : 6 ].strip() )

                    waterLevelsInMetres = [ ]
                    line = lines[ index + 6 ]
                    for item in line.split( "<td class=\"HWLWTableCellPrintFriendly\">" ):
                        if len( item.strip() ) > 0:
                            waterLevelsInMetres.append( item[ 0 : 3 ] )

                    for index, item in enumerate( waterLevelTypes ):
                        tideTime = datetime.datetime.strptime( times[ index ], "%H:%M" )
                        tidalReadings.append( tide.Reading( ( portName + ", " + country ), tideDate.month, tideDate.day, tideTime.hour, tideTime.minute, waterLevelsInMetres[ index ], waterLevelTypes[ index ], url ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error retrieving/parsing tidal data from " + str( url ) )
            tidalReadings = None

        locale.setlocale( locale.LC_TIME, defaultLocale )
        return tidalReadings


if __name__ == "__main__": IndicatorTide().main()