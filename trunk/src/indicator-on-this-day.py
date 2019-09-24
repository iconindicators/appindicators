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


# Application indicator which displays calendar events.


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


INDICATOR_NAME = "indicator-on-this-day"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "Notify", "0.7" )

from event import Event
from gi.repository import AppIndicator3, Gdk, GLib, Gtk, Notify
from datetime import date, datetime, timedelta
import fnmatch, logging, os, pythonutils, threading, webbrowser


class IndicatorOnThisDay:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.5"
    ICON = INDICATOR_NAME
    COPYRIGHT_START_YEAR = "2017"
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa"
    COMMENTS = _( "Calls the 'calendar' program and displays events in the menu." )

    CACHE_CALENDAR_FILENAME = "calendars"
    CACHE_CALENDAR_FULL_PATH = pythonutils.getCachePathname( INDICATOR_NAME, CACHE_CALENDAR_FILENAME )

    DEFAULT_CALENDAR = "/usr/share/calendar/calendar.history"

    TAG_EVENT = "["+ _( "EVENT" )+ "]"
    SEARCH_URL_DEFAULT = "https://www.google.com/search?q=" + TAG_EVENT

    CONFIG_CALENDARS = "calendars"
    CONFIG_COPY_TO_CLIPBOARD = "copyToClipboard"
    CONFIG_LINES = "lines"
    CONFIG_NOTIFY = "notify"
    CONFIG_SEARCH_URL = "searchURL"


    def __init__( self ):
        logging.basicConfig( format = pythonutils.LOGGING_BASIC_CONFIG_FORMAT, level = pythonutils.LOGGING_BASIC_CONFIG_LEVEL, handlers = [ pythonutils.TruncatedFileHandler( IndicatorOnThisDay.LOG ) ] )
        self.lock = threading.Lock()

        Notify.init( INDICATOR_NAME )
        self.loadConfig()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorOnThisDay.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

        self.update()


    def main( self ): Gtk.main()


    def update( self ):
        with lock:
            events = self.getEvents()
            self.buildMenu( events )

            now = datetime.now()
            justAfterMidnight = ( now + timedelta( days = 1 ) ).replace( hour = 0, minute = 0, second = 5 )
            fiveSecondsAfterMidnight = int( ( justAfterMidnight - now ).total_seconds() )
            self.updateTimerID = GLib.timeout_add_seconds( fiveSecondsAfterMidnight, self.update )

            if self.notify:
                today = pythonutils.processGet( "date +'%b %d'" ).strip() # It is assumed/hoped the dates in the calendar result are short date format.
                for event in events:
                    if today == event.getDate():
                        Notify.Notification.new( _( "On this day..." ), event.getDescription(), IndicatorOnThisDay.ICON ).show()


    def buildMenu( self, events ):
        menuItemMaximum = self.lines - 3 # Less three to account for About, Preferences and Quit.
        menuItemCount = 0
        menu = Gtk.Menu()
        lastDate = ""
        for event in events:
            if event.getDate() != lastDate:
                if ( menuItemCount + 2 ) <= menuItemMaximum: # Ensure there is room for the date menu item and an event menu item.
                    menu.append( Gtk.MenuItem( event.getDate() ) )
                    lastDate = event.getDate()
                    menuItemCount += 1
                else:
                    break # Don't add the menu item for the new date and don't add a subsequent event.

            menuItem = Gtk.MenuItem( "    " + event.getDescription() )
            menuItem.props.name = event.getDate() # Allows the month/day to be passed to the copy/search functions below.
            menu.append( menuItem )
            menuItemCount += 1

            if self.copyToClipboard:
                menuItem.connect( "activate", lambda widget: Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( widget.props.name + " " + widget.props.label.strip(), -1 ) )

            elif len( self.searchURL ) > 0: # If the user enters an empty URL this means "no internet search" but also means the clipboard will not be modified. 
                menuItem.connect( "activate", lambda widget: webbrowser.open( self.searchURL.replace( IndicatorOnThisDay.TAG_EVENT, ( widget.props.name + " " + widget.props.label ).replace( " ", "+" ) ) ) )

            if menuItemCount == menuItemMaximum:
                break

        pythonutils.createPreferencesAboutQuitMenuItems( menu, len( events ) > 0, self.onPreferences, self.onAbout, Gtk.main_quit )
        menu.show_all()
        self.indicator.set_menu( menu )


    def getEvents( self ):
        # Write the path of each calendar file to a temporary file - allows for one call to calendar.
        content = ""
        for calendar in self.calendars:
            if os.path.isfile( calendar ):
                content += "#include <" +calendar + ">\n"

        pythonutils.writeCacheText( INDICATOR_NAME, IndicatorOnThisDay.CACHE_CALENDAR_FILENAME, content, logging )

        # Run the calendar command and parse the results, one event per line, sometimes...
        events = [ ]
        command = "calendar -f " + IndicatorOnThisDay.CACHE_CALENDAR_FULL_PATH + " -A 366"
        for line in pythonutils.processGet( command ).splitlines():
            if( line is None or len( line.strip() ) == 0 ):
                continue # Ubuntu 17.04 inserts an empty line between events.

            if line.startswith( "\t" ): # When a line starts with a TAB, this is a continuation of the previous event.
                date = events[ -1 ].getDate()
                description = events[ -1 ].getDescription() + " " + line.strip()
                del events[ -1 ]
                events.append( Event( date, description ) )

            else:
                line = line.split( "\t" ) # This is a regular line with the month/day separated by TAB from the event.
                date = line[ 0 ].replace( "*", "" ).strip()
                description = line[ -1 ].strip() # Take the last element as there may be more than one TAB character throwing out the index of the event in the line.
                events.append( Event( date, description ) )

        # Sort events of the same date by description.
        sortedEvents = [ ]
        currentDate = ""
        i = 0
        j = 1
        while( j < len( events ) ):
            if events[ j ].getDate() == events[ i ].getDate():
                j += 1

            else:
                sortedEvents += sorted( events[ i : j ], key = lambda event: event.getDescription() )
                i = j
                j += 1

        if len( events ) > len( sortedEvents ):
            sortedEvents += sorted( events[ i : ], key = lambda event: event.getDescription() )

        # Remove duplicate events.
        sortedEventsWithoutDuplicates = [ ]
        for event in sortedEvents:
            if event not in sortedEventsWithoutDuplicates:
                sortedEventsWithoutDuplicates.append( event )

        return sortedEventsWithoutDuplicates


    def onAbout( self, widget ):
        if self.lock.acquire( blocking = False ):
            pythonutils.showAboutDialog(
                [ IndicatorOnThisDay.AUTHOR + " " + IndicatorOnThisDay.WEBSITE ],
                [ IndicatorOnThisDay.AUTHOR + " " + IndicatorOnThisDay.WEBSITE ],
                IndicatorOnThisDay.COMMENTS,
                IndicatorOnThisDay.AUTHOR,
                IndicatorOnThisDay.COPYRIGHT_START_YEAR,
                [ ],
                "",
                Gtk.License.GPL_3_0,
                IndicatorOnThisDay.ICON,
                INDICATOR_NAME,
                IndicatorOnThisDay.WEBSITE,
                IndicatorOnThisDay.VERSION,
                _( "translator-credits" ),
                _( "View the" ),
                _( "text file." ),
                _( "changelog" ),
                IndicatorOnThisDay.LOG,
                _( "View the" ),
                _( "text file." ),
                _( "error log" ) )

            self.lock.release()


    def onPreferences( self, widget ):
        if self.lock.acquire( blocking = False ):
            GLib.source_remove( self.updateTimerID )
            self._onPreferences( widget )
            self.lock.release()
            GLib.idle_add( self.update )


    def _onPreferences( self, widget ):
        notebook = Gtk.Notebook()

        # Calendar file settings.
        grid = pythonutils.createGrid()

        store = Gtk.ListStore( str, str ) # Path to calendar file; tick icon (Gtk.STOCK_APPLY) or error icon (Gtk.STOCK_DIALOG_ERROR) or None.
        for calendar in self.getCalendars():
            if calendar not in self.calendars:
                store.append( [ calendar, None ] )

        for calendar in self.calendars:
            if os.path.isfile( calendar ):
                store.append( [ calendar, Gtk.STOCK_APPLY ] )
            else:
                store.append( [ calendar, Gtk.STOCK_DIALOG_ERROR ] )

        storeSort = Gtk.TreeModelSort( model = store )
        storeSort.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( storeSort )
        tree.expand_all()
        tree.set_hexpand( True )
        tree.set_vexpand( True )

        treeViewColumn = Gtk.TreeViewColumn( _( "Calendar" ), Gtk.CellRendererText(), text = 0 )
        treeViewColumn.set_sort_column_id( 0 )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Enabled" ), Gtk.CellRendererPixbuf(), stock_id = 1 )
        treeViewColumn.set_sort_column_id( 1 )
        tree.append_column( treeViewColumn )

        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onCalendarDoubleClick )
        tree.set_tooltip_text( _( "Double click to edit a calendar." ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        grid.attach( scrolledWindow, 0, 0, 1, 25 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )

        addButton = Gtk.Button( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new calendar." ) )
        addButton.connect( "clicked", self.onCalendarAdd, tree )
        box.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected calendar." ) )
        removeButton.connect( "clicked", self.onCalendarRemove, tree )
        box.pack_start( removeButton, True, True, 0 )

        resetButton = Gtk.Button( _( "Reset" ) )
        resetButton.set_tooltip_text( _( "Reset to factory default." ) )
        resetButton.connect( "clicked", self.onCalendarReset, tree )
        box.pack_start( resetButton, True, True, 0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 26, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Calendars" ) ) )

        # General settings.
        grid = pythonutils.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Lines" ) ), False, False, 0 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.lines, 1, 1000, 1, 10, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinner.set_value( self.lines ) # ...so need to force the initial value by explicitly setting it.
        spinner.set_tooltip_text( _( "The number of menu items available for display." ) )

        box.pack_start( spinner, False, False, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        label = Gtk.Label( _( "On event click" ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 1, 1, 1 )

        radioCopyToClipboard = Gtk.RadioButton.new_with_label_from_widget( None, _( "Copy event to clipboard" ) )
        radioCopyToClipboard.set_tooltip_text( _( "Copy the event text and date to the clipboard." ) )
        radioCopyToClipboard.set_active( self.copyToClipboard )
        radioCopyToClipboard.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )
        grid.attach( radioCopyToClipboard, 0, 2, 1, 1 )

        radioInternetSearch = Gtk.RadioButton.new_with_label_from_widget( radioCopyToClipboard, _( "Search event on the internet" ) )
        radioInternetSearch.set_tooltip_text( _( "Open the default web browser and search for the event." ) )
        radioInternetSearch.set_active( not self.copyToClipboard )
        radioInternetSearch.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )
        grid.attach( radioInternetSearch, 0, 3, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True )
        box.set_margin_left( pythonutils.INDENT_WIDGET_LEFT * 2 )

        label = Gtk.Label( _( "URL" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        searchEngineEntry = Gtk.Entry()
        searchEngineEntry.set_tooltip_text( _( 
            "The URL to search for the event.\n\n" + \
            "Use {0} in the URL to specify the\n" + \
            "position of the event text/date.\n\n" + \
            "If the URL is empty and 'search' is selected,\n" + \
            "the search will effectively be ignored.\n\n" + \
            "If the URL is empty and 'copy' is selected,\n" + \
            "the URL is reset back to factory default." ).format( IndicatorOnThisDay.TAG_EVENT ) )
        searchEngineEntry.set_text( self.searchURL )
        searchEngineEntry.set_sensitive( not self.copyToClipboard )
        box.pack_start( searchEngineEntry, True, True, 0 )

        grid.attach( box, 0, 4, 1, 1 )

        radioCopyToClipboard.connect( "toggled", self.onEventClickRadio, radioCopyToClipboard, radioInternetSearch, searchEngineEntry )
        radioInternetSearch.connect( "toggled", self.onEventClickRadio, radioCopyToClipboard, radioInternetSearch, searchEngineEntry )

        notifyCheckbox = Gtk.CheckButton( _( "Notify" ) )
        notifyCheckbox.set_tooltip_text( _(
            "On startup or when saving preferences,\n" + \
            "show a notification for each of today's events." ) )
        notifyCheckbox.set_active( self.notify )
        notifyCheckbox.set_margin_top( 10 )
        grid.attach( notifyCheckbox, 0, 5, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorOnThisDay.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 6, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        dialog = Gtk.Dialog( _( "Preferences" ), None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorOnThisDay.ICON )
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:

            self.lines = spinner.get_value_as_int()

            self.calendars = [ ]
            treeiter = store.get_iter_first()
            while treeiter != None:
                if store[ treeiter ][ 1 ] is not None:
                    self.calendars.append( store[ treeiter ][ 0 ] )

                treeiter = store.iter_next( treeiter )

            self.copyToClipboard = radioCopyToClipboard.get_active()
            self.searchURL = searchEngineEntry.get_text().strip()
            self.notify = notifyCheckbox.get_active()
            self.saveConfig()
            pythonutils.setAutoStart( IndicatorOnThisDay.DESKTOP_FILE, autostartCheckbox.get_active(), logging )

        dialog.destroy()


    def onEventClickRadio( self, source, radioCopyToClipboard, radioInternetSearch, searchEngineEntry ):
        searchEngineEntry.set_sensitive( source == radioInternetSearch )
        if source == radioCopyToClipboard and len( searchEngineEntry.get_text() ) == 0:
            searchEngineEntry.set_text( IndicatorOnThisDay.SEARCH_URL_DEFAULT )


    def getCalendars( self ):
        calendars = [ ]
        for root, directories, filenames in os.walk( "/usr/share/calendar" ):
            for filename in fnmatch.filter( filenames, "calendar.*" ):
                calendars.append( os.path.join( root, filename ) )

        calendars.sort()
        return calendars


    def onCalendarReset( self, button, treeview ):
        if pythonutils.showOKCancel( None, _( "Reset calendars to factory default?" ), INDICATOR_NAME ) == Gtk.ResponseType.OK:
            listStore = treeview.get_model().get_model()
            listStore.clear()
            for calendar in self.getCalendars():
                if calendar == IndicatorOnThisDay.DEFAULT_CALENDAR:
                    listStore.append( [ IndicatorOnThisDay.DEFAULT_CALENDAR, Gtk.STOCK_APPLY ] )
                else:
                    listStore.append( [ calendar, None ] )


    def onCalendarRemove( self, button, treeview ):
        model, treeiter = treeview.get_selection().get_selected()
        if treeiter is None:
            pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "No calendar has been selected." ), INDICATOR_NAME )
        elif model[ treeiter ][ 0 ] in self.getCalendars():
            pythonutils.showMessage( None, Gtk.MessageType.WARNING, _( "This calendar is part of your system\nand cannot be removed." ), INDICATOR_NAME )
        elif pythonutils.showOKCancel( None, _( "Remove the selected calendar?" ), INDICATOR_NAME ) == Gtk.ResponseType.OK: # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) )


    def onCalendarAdd( self, button, treeview ): self.onCalendarDoubleClick( treeview, None, None )


    def onCalendarDoubleClick( self, treeview, rowNumber, treeViewColumn ):
        model, treeiter = treeview.get_selection().get_selected()

        if rowNumber is None: # This is an add.
            isSystemCalendar = False
        else: # This is an edit.
            isSystemCalendar = model[ treeiter ][ 0 ] in self.getCalendars()

        grid = pythonutils.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Calendar file" ) ), False, False, 0 )

        fileEntry = Gtk.Entry()
        fileEntry.set_editable( False )

        if rowNumber is not None: # This is an edit.
            fileEntry.set_text( model[ treeiter ][ 0 ] )
            fileEntry.set_width_chars( len( fileEntry.get_text() ) * 5 / 4 ) # Sometimes the length is shorter than set due to packing, so make it longer.

        fileEntry.set_tooltip_text( _( "The path to a calendar file." ) )
        box.pack_start( fileEntry, True, True, 0 )

        browseButton = Gtk.Button( _( "Browse" ) )
        browseButton.set_sensitive( not isSystemCalendar )
        if isSystemCalendar:
            browseButton.set_tooltip_text( _(
                "This calendar is part of your\n" + \
                "system and cannot be modified." ) )
        else:
            browseButton.set_tooltip_text( _( 
                "Choose a calendar file.\n\n" + \
                "Ensure the calendar file is\n" + \
                "valid by running through\n" + \
                "'calendar' in a terminal." ) )

        box.pack_start( browseButton, False, False, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        enabledCheckbox = Gtk.CheckButton( _( "Enabled" ) )
        if rowNumber is None: # This is an add.
            enabledCheckbox.set_active( True )
        else:
            enabledCheckbox.set_active( model[ treeiter ][ 1 ] == Gtk.STOCK_APPLY )

        grid.attach( enabledCheckbox, 0, 1, 1, 1 )

        if rowNumber is None:
            title = _( "Add Calendar" )
        else:
            title = _( "Edit Calendar" )

        dialog = Gtk.Dialog( title, None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorOnThisDay.ICON )

        # Need to set these here as the dialog had not been created at the point the buttons were defined.
        browseButton.connect( "clicked", self.onBrowseCalendar, dialog, fileEntry )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:

                if not isSystemCalendar and fileEntry.get_text().strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The calendar path cannot be empty." ), INDICATOR_NAME )
                    fileEntry.grab_focus()
                    continue
    
                if not isSystemCalendar and not os.path.exists( fileEntry.get_text().strip() ):
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The calendar path does not exist." ), INDICATOR_NAME )
                    fileEntry.grab_focus()
                    continue

                if rowNumber is not None:
                    model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) ) # This is an edit...remove the old value and append new value.  
    
                model.get_model().append( [ fileEntry.get_text().strip(), Gtk.STOCK_APPLY if enabledCheckbox.get_active() else None ] )

            break

        dialog.destroy()


    def onBrowseCalendar( self, button, addEditDialog, calendarFile ):
        systemCalendars = self.getCalendars()
        dialog = Gtk.FileChooserDialog( _( "Choose a calendar file" ), addEditDialog, Gtk.FileChooserAction.OPEN, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK ) )
        dialog.set_modal( True ) # In Ubuntu 14.04 the underlying add/edit dialog is still clickable, but behaves in Ubuntu 16.04/17.04.
        dialog.set_filename( calendarFile.get_text() )
        while( True ):
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if dialog.get_filename() in systemCalendars:
                    pythonutils.showMessage( dialog, Gtk.MessageType.INFO, _( "The calendar is part of your system\nand is already included." ), INDICATOR_NAME )
                else:
                    calendarFile.set_text( dialog.get_filename() )
                    break
            else:
                break

        dialog.destroy()


    def loadConfig( self ):
        config = pythonutils.loadConfig( INDICATOR_NAME, INDICATOR_NAME, logging )

        self.calendars = config.get( IndicatorOnThisDay.CONFIG_CALENDARS, [ IndicatorOnThisDay.DEFAULT_CALENDAR ] )
        self.copyToClipboard = config.get( IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD, True )
        self.lines = config.get( IndicatorOnThisDay.CONFIG_LINES, pythonutils.getMenuItemsGuess() )
        self.notify = config.get( IndicatorOnThisDay.CONFIG_NOTIFY, True )
        self.searchURL = config.get( IndicatorOnThisDay.CONFIG_SEARCH_URL, IndicatorOnThisDay.SEARCH_URL_DEFAULT )


    def saveConfig( self ):
        config = {
            IndicatorOnThisDay.CONFIG_CALENDARS: self.calendars,
            IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD: self.copyToClipboard,
            IndicatorOnThisDay.CONFIG_LINES: self.lines,
            IndicatorOnThisDay.CONFIG_NOTIFY: self.notify,
            IndicatorOnThisDay.CONFIG_SEARCH_URL: self.searchURL,
        }

        pythonutils.saveConfig( config, INDICATOR_NAME, INDICATOR_NAME, logging )


if __name__ == "__main__": IndicatorOnThisDay().main()