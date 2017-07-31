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


#TODO...
# For most ports, each tidal reading contains date/type/time/level (Tue 25 Jul / HW / 05:38 / 0.4 m )
# For these ports, convert the date/time from the port standard local time to (UTC and then to) user local time. 
# Further, it seems every tidal reading will have at least the date and the type.
# 
# Some port tidal readings do not have a level (but still have date/time/type). 
# In this case, the [LEVEL] tag is dropped out - is a separate user preference needed?
# Date/time/level is shown as normal.
# 
# Some port tidal readings do not have the time and level.
# In this case drop that specific tidal reading.
# Assuming the remaining tidal readings have the date/time and optionally the level, proceed as above.
# If all tidal readings have been dropped, there is no data to show and message the user.
# 
# Some port tidal readings do not have the time (date/type/level are present).
# If all the port's tidal readings do not have the time, then display using just the date (as port standard local).
# If there is a mix of tidal readings with date/time and some with only time, what to do?
# Drop the time from date/time readings and show only date for all readings, or,
# drop readings if they don't have a time (and keep the date/time readings).
#
# User preferences:
#    A format to show the date (already present).
#    A format to show each time/type/level (already present).
#    A format to show each time/type (not present).
#    When some readings contain date and some contain date/time, choose either
#        a) drop the time from date/time readings and show all readings using only date, or
#        b) drop readings that only have a date (missing time) and show only readings with a date/time.


class IndicatorTide:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.8"
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"
    COMMENTS = _( "Displays tidal information.\nNon-UK ports will be unavailable after {0}." ).format( ports.getExpiry() )

    CREDIT_UKHO_UK_PORTS = _( "Tidal information for UK ports licensed under the\nOpen Government Licence for Public Sector Information. http://www.nationalarchives.gov.uk/doc/open-government-licence" )
    CREDIT_UKHO_UK_NON_PORTS = _( "Tidal information for non-UK ports reproduced by\npermission of the Controller of Her Majesty’s Stationery Office\nand the UK Hydrographic Office. http://www.ukho.gov.uk" )
    CREDITS = [ CREDIT_UKHO_UK_PORTS, CREDIT_UKHO_UK_NON_PORTS ]

    URL_TIMEOUT_IN_SECONDS = 10

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_MENU_ITEM_DATE_FORMAT = "menuItemDateFormat"
    SETTINGS_MENU_ITEM_TIDE_FORMAT = "menuItemTideFormat"
    SETTINGS_MENU_ITEM_TIDE_FORMAT_SANS_TIME = "menuItemTideFormatSansTime"
    SETTINGS_PORT_ID = "portID"
    SETTINGS_SHOW_AS_SUBMENUS = "showAsSubmenus"
    SETTINGS_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY = "showAsSubmenusExceptFirstDay"

    MENU_ITEM_DATE_DEFAULT_FORMAT = "%A, %d %B"
    MENU_ITEM_TIME_DEFAULT_FORMAT = "%I:%M %p"
    MENU_ITEM_TIDE_LEVEL_TAG = "[LEVEL]" # The level of the tide in metres.
    MENU_ITEM_TIDE_TYPE_TAG = "[TYPE]" # The tide type, either high or low.
    MENU_ITEM_TIDE_DEFAULT_FORMAT = MENU_ITEM_TIME_DEFAULT_FORMAT + "    " + MENU_ITEM_TIDE_TYPE_TAG + "    " + MENU_ITEM_TIDE_LEVEL_TAG
    MENU_ITEM_TIDE_DEFAULT_FORMAT_SANS_TIME = "                         " + MENU_ITEM_TIDE_TYPE_TAG + "    " + MENU_ITEM_TIDE_LEVEL_TAG


    def __init__( self ):
        logging.basicConfig( format = pythonutils.LOGGING_BASIC_CONFIG_FORMAT, level = pythonutils.LOGGING_BASIC_CONFIG_LEVEL, handlers = [ pythonutils.TruncatedFileHandler( IndicatorTide.LOG ) ] )
        self.dialogLock = threading.Lock()

        Notify.init( INDICATOR_NAME )
        self.loadSettings()

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
            self.buildMenu( tidalReadings )
            self.updateTimerID = GLib.timeout_add_seconds( self.getNextUpdateTimeInSeconds(), self.update, True )
    
            if len( tidalReadings ) == 0:
                message = _( "No port data available for {0}!" ).format( ports.getPortName( self.portID ) )
                Notify.Notification.new( _( "Error" ), message, IndicatorTide.ICON ).show()


    def buildMenu( self, tidalReadings ):
        menu = Gtk.Menu()
        if len( tidalReadings ) == 0:
            menu.append( Gtk.MenuItem( _( "No port data available for {0}!" ).format( ports.getPortName( self.portID ) ) ) )
        else:
            menuItemText = _( "{0}, {1}" ).format( ports.getPortName( tidalReadings[ 0 ].getPortID() ), ports.getCountry( tidalReadings[ 0 ].getPortID() ) )
            self.createAndAppendMenuItem( menu, menuItemText, tidalReadings[ 0 ].getURL() )

            indent = "    "
            if self.showAsSubMenus:
                self.buildMenuSubmenus( menu, indent, tidalReadings )
            else:
                self.buildMenuVanilla( menu, indent, tidalReadings )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, True, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    # If all tidal readings are datetimes
    #    Convert datetimes to user local
    #
    # Elif all tidal readings are dates
    #    Display dates as is
    #
    # Else (mix of datetimes and dates)
    #    If drop tidal readings containing dates
    #        Drop tidal readings containing dates
    #        Convert remaining datetimes to user local
    #
    #    Elif show only dates
    #        Drop time from tidal readings containing datetimes
    #        Display as dates
    #
    #    Else
    #        Show datetimes and dates in port standard time.
    def sanitiseTidalReadings( self, tidalReadings, dropTimeFromDateTime ):
        allDates = True
        allDateTimes = True
        for tidalReading in tidalReadings:
            if isinstance( tidalReading.getDateTime(), datetime.datetime ):
                allDates = False
            else: # Must be datetime.date
                allDateTimes = False

        if not allDates and not allDateTimes: # A mix of datetime.datetime and datetime.date
            if dropTimeFromDateTime: # Drop the time from tidal readings which contain datetime.datetime
                
#TODO
                pass

            else: # Drop tidal readings which contain datetime.date
                for tidalReading in list( tidalReadings ):
                    if isinstance( tidalReading.getDateTime(), datetime.date ):
                        tidalReadings.remove( tidalReading )

        return tidalReadings


    def buildMenuVanilla( self, menu, indent, tidalReadings ):

        # If all tidal readings are datetimes
        #    Convert datetimes to user local
        #
        # Elif all tidal readings are dates
        #    Display dates as is
        #
        # Else (mix of datetimes and dates)
        #    If drop tidal readings containing dates
        #        Drop tidal readings containing dates
        #        Convert remaining datetimes to user local
        #
        #    Else (show only dates)
        #        Drop time from tidal readings containing datetimes
        #        Display as dates

        previousMonth = -1
        previousDay = -1
        for tidalReading in tidalReadings:

            if isinstance( tidalReading.getDateTimeUTC(), datetime.datetime ):
                tidalDateTimeLocal = tidalReading.getDateTimeUTC().astimezone() # Date/time now in local time zone.
            else:
                tidalDateTimeLocal = tidalReading.getDateTimeUTC() # There is no time component.  #TODO Test port 1894A which hits this problem - make sure the days/dates match up and are make sense. 

            if not( tidalDateTimeLocal.month == previousMonth and tidalDateTimeLocal.day == previousDay ):
                menuItemText = indent + tidalDateTimeLocal.strftime( self.menuItemDateFormat )
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

            self.createAndAppendMenuItem( menu, indent + indent + menuItemText, tidalReading.getURL() )

            previousMonth = tidalDateTimeLocal.month
            previousDay = tidalDateTimeLocal.day


    def buildMenuSubmenus( self, menu, indent, tidalReadings ):
        previousMonth = -1
        previousDay = -1
        firstTidalReading = True
        for tidalReading in tidalReadings:

            if type( tidalReading.getDateTimeUTC() ) == datetime.datetime:
                tidalDateTimeLocal = tidalReading.getDateTimeUTC().astimezone() # Date/time now in local time zone.
            else:
                tidalDateTimeLocal = tidalReading.getDateTimeUTC() # There is no time component.  #TODO Test port 1894A which hits this problem - make sure the days/dates match up and are make sense. 

            if firstTidalReading:
                firstMonth = tidalDateTimeLocal.month
                firstDay = tidalDateTimeLocal.day
                firstTidalReading = False

            if not( tidalDateTimeLocal.month == previousMonth and tidalDateTimeLocal.day == previousDay ):
                menuItemText = indent + tidalDateTimeLocal.strftime( self.menuItemDateFormat )
                if self.showAsSubMenusExceptFirstDay and firstMonth == tidalDateTimeLocal.month and firstDay == tidalDateTimeLocal.day:
                    self.createAndAppendMenuItem( menu, menuItemText, tidalReading.getURL() )
                else:
                    subMenu = Gtk.Menu()
                    self.createAndAppendMenuItem( menu, menuItemText, None ).set_submenu( subMenu )

            if isinstance( tidalDateTimeLocal, datetime.datetime ):
                menuItemText = tidalDateTimeLocal.strftime( self.menuItemTideFormat )
            else:
                menuItemText = self.menuItemTideFormatSansTime

            if tidalReading.getType() == tide.Type.H:
                menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, _( "H" ) )
            else: # The type must be either H or L - cannot be None.
                menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_TYPE_TAG, _( "L" ) )

            if tidalReading.getLevelInMetres() is None:
                menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG, "" )
            else:
                menuItemText = menuItemText.replace( IndicatorTide.MENU_ITEM_TIDE_LEVEL_TAG, str( tidalReading.getLevelInMetres() ) + " m" )

            if self.showAsSubMenusExceptFirstDay and firstMonth == tidalDateTimeLocal.month and firstDay == tidalDateTimeLocal.day:
                self.createAndAppendMenuItem( menu, indent + indent + menuItemText, tidalReading.getURL() )
            else:
                self.createAndAppendMenuItem( subMenu, menuItemText, tidalReading.getURL() )

            previousMonth = tidalDateTimeLocal.month
            previousDay = tidalDateTimeLocal.day


    def createAndAppendMenuItem( self, menu, menuItemText, url ):
        menuItem = Gtk.MenuItem( menuItemText )
        menu.append( menuItem )

        if url is not None:
            menuItem.connect( "activate", lambda widget: webbrowser.open( widget.props.name ) ) # This returns a boolean indicating success or failure - showing the user a message on a false return value causes a dialog lock up!
            menuItem.set_name( url )

        return menuItem


    def tidalReadingsContainDates( self, tidalReadings ):
        containDates = False
        for tidalReading in tidalReadings:
            if isinstance( tidalReading.getDateTime(), datetime.date ):
                containDates = True
                break

        return containDates


    def tidalReadingsContainDateTimes( self, tidalReadings ):
        containDateTimes = False
        for tidalReading in tidalReadings:
            if isinstance( tidalReading.getDateTime(), datetime.datetime ):
                containDateTimes = True
                break

        return containDateTimes


    def getNextUpdateTimeInSeconds( self ):
        # No way of knowing when a port's data will be updated.
        # Simplest solution is ensure the user does not look at stale data.
        # Doing an update just after (local) midnight will drop out any data prior to (local) today.
        now = datetime.datetime.now()
        fiveMinutesAfterMidnight = ( now + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 )
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

        box.pack_start( Gtk.Label( _( "In absentia" ) ), False, False, 0 )

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
            self.saveSettings()
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


    def loadSettings( self ):
        self.menuItemDateFormat = IndicatorTide.MENU_ITEM_DATE_DEFAULT_FORMAT
        self.menuItemTideFormat = IndicatorTide.MENU_ITEM_TIDE_DEFAULT_FORMAT
        self.menuItemTideFormatSansTime = IndicatorTide.MENU_ITEM_TIDE_DEFAULT_FORMAT_SANS_TIME
        self.portID = None
        self.showAsSubMenus = True
        self.showAsSubMenusExceptFirstDay = True

        if os.path.isfile( IndicatorTide.SETTINGS_FILE ):
            try:
                with open( IndicatorTide.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.menuItemDateFormat = settings.get( IndicatorTide.SETTINGS_MENU_ITEM_DATE_FORMAT, self.menuItemDateFormat )
                self.menuItemTideFormat = settings.get( IndicatorTide.SETTINGS_MENU_ITEM_TIDE_FORMAT, self.menuItemTideFormat )
                self.menuItemTideFormatSansTime = settings.get( IndicatorTide.SETTINGS_MENU_ITEM_TIDE_FORMAT_SANS_TIME, self.menuItemTideFormatSansTime )
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


    def saveSettings( self ):
        settings = {
            IndicatorTide.SETTINGS_MENU_ITEM_DATE_FORMAT: self.menuItemDateFormat,
            IndicatorTide.SETTINGS_MENU_ITEM_TIDE_FORMAT: self.menuItemTideFormat,
            IndicatorTide.SETTINGS_MENU_ITEM_TIDE_FORMAT_SANS_TIME: self.menuItemTideFormatSansTime,
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


    def getTidalDataFromUnitedKingdomHydrographicOffice( self, portID ):
        if portID[ -1 ].isalpha():
            portIDForURL = portID[ 0 : -1 ].rjust( 4, "0" ) + portID[ -1 ]
        else:
            portIDForURL = portID.rjust( 4, "0" )

        # TODO Testing...
#         portIDForURL = "1800" # LW time missing.
#         portIDForURL = "1894A" # LW time missing.
#         portIDForURL = "3983" # LW time is missing.
#
#         portIDForURL = "2168" # HW/LW time missing.
#         portIDForURL = "5088" # HW/LW time missing.
#
#         portIDForURL = "0839" # HW/LW reading is missing.
#
#         portIDForURL = "4000" # LW time/reading is missing.
#         portIDForURL = "3578" # LW time/reading is missing.
#
#         portIDForURL = "4273" # HW/LW reading is missing; LW time is missing.
#
#         portIDForURL = "1411" # LW reading is negative.
#
#         portIDForURL = "2168" # UTC offset negative.
#         portIDForURL = "4000" # UTC offset positive.

        url = "http://www.ukho.gov.uk/easytide/EasyTide/ShowPrediction.aspx?PortID=" + portIDForURL + \
              "&PredictionLength=7&DaylightSavingOffset=0&PrinterFriendly=True&HeightUnits=0&GraphSize=7"

        print( "port id", portIDForURL )

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

                    from datetime import datetime, timedelta
                    
                    result = datetime.utcnow() + timedelta( minutes = int( utcOffset[ 0 ] + utcOffset[ 3 : 5 ] ), hours = int( utcOffset[ 0 ] + utcOffset[ 1 : 3 ] ) )
                    print( "min", int( utcOffset[ 1 : 3 ] ) )
                    print( "hours", int( utcOffset[ 3 : 5 ] ) )
                    print( "utc offset", utcOffset )
                    print( type( result) , result )
                    print( "year", result.year )
                    print( "year", ( datetime.utcnow() + timedelta( minutes = int( utcOffset[ 0 ] + utcOffset[ 3 : 5 ] ), hours = int( utcOffset[ 0 ] + utcOffset[ 1 : 3 ] ) ) ).year )
                    return []
                    


                if "PredictionSummary1_lblPredictionStart" in line:
                    startDate = line[ line.index( "Today" ) + len( "Today - " ) : line.index( "<small>" ) ].strip().split() # Monday 17th July 2017 (standard local time of the port)
                    startYear = startDate[ 3 ] # 2017
                    startMonth = str( datetime.datetime.strptime( startDate[ 2 ], "%B" ).month ) # 7

#TODO The start date seems to be relative to GMT.
# That means port data for Sydney (GMT +10) can have a start date of the previous day,
# until GMT midnight comes around (when tidal readings are updated).
# Only need the year from the start date...
# ...or is there a way to get the year from the system date and ensure the year makes sense for the port in question?
# Only need to worry about an incorrect year if Dec 31 or Jan 1...but how?
# Maybe get current date/time for the UTC of the port and then get the year.
                if "HWLWTableHeaderCell" in line:
                    date = line[ line.find( ">" ) + 1 : line.find( "</th>" ) ] # Mon 17 Jul (standard local time)
                    dayOfMonth = date[ 4 : 6 ] # 17
                    month = str( datetime.datetime.strptime( date[ -3 : ], "%b" ).month ) # 7
                    year = startYear
                    if month < startMonth:
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
                                dateTimes.append( datetime.date( year, month, dayOfMonth ) )

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
                        if levels[ index ] is None and isinstance( dateTimes[ index ], datetime.date ): #TODO Test this with a port that has missing time and level.
                            continue # Drop a tidal reading if missing both the time and level.

                        if isinstance( dateTimes[ index ], datetime.datetime ):
                            tidalReadings.append( tide.Reading( portID, dateTimes[ index ].year, dateTimes[ index ].month, dateTimes[ index ].day, dateTimes[ index ].hour, dateTimes[ index ].minute, dateTimes[ index ].tzname(), levels[ index ], tideType, url ) )
                        else:
                            tidalReadings.append( tide.Reading( portID, dateTimes[ index ].year, dateTimes[ index ].month, dateTimes[ index ].day, None, None, None, levels[ index ], tideType, url ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error retrieving/parsing tidal data from " + str( url ) )
            tidalReadings = [ ]

#         for t in tidalReadings: print( t )
        
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

            if type( tidalReading.getDateTimeUTC() ) is datetime.datetime:
                if tidalReading.getDateTimeUTC().astimezone() < todayLocalMidnight:
                    tidalReadings.remove( tidalReading )

            else:
                if tidalReading.getDateTimeUTC() < todayLocalMidnight.date():
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