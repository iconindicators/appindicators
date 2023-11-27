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


# Application indicator which displays calendar events.


INDICATOR_NAME = "indicator-on-this-day"
import gettext
gettext.install( INDICATOR_NAME )

import fnmatch

import gi
gi.require_version( "Gdk", "3.0" )
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

import os, webbrowser

from event import Event
from datetime import date, datetime, timedelta
from gi.repository import Gdk, Gtk, Notify
from indicatorbase import IndicatorBase


class IndicatorOnThisDay( IndicatorBase ):

    CONFIG_CALENDARS = "calendars"
    CONFIG_COPY_TO_CLIPBOARD = "copyToClipboard"
    CONFIG_LINES = "lines"
    CONFIG_NOTIFY = "notify"
    CONFIG_SEARCH_URL = "searchURL"

    # Data model columns used in the Preferences dialog.
    COLUMN_CALENDAR_FILE = 0 # Path to calendar file.
    COLUMN_CALENDAR_ENABLED = 1 # tick icon (Gtk.STOCK_APPLY) or error icon (Gtk.STOCK_DIALOG_ERROR) or None.

    CALENDARS_FILENAME = "calendars.txt"

    DEFAULT_CALENDAR = "/usr/share/calendar/calendar.history"
    TAG_EVENT = "["+ _( "EVENT" )+ "]"
    SEARCH_URL_DEFAULT = "https://www.google.com/search?q=" + TAG_EVENT


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            copyrightStartYear = "2017",
            comments = _( "Calls the 'calendar' program and displays events in the menu." ) )


    def update( self, menu ):
        events = self.getEvents()
        self.buildMenu( menu, events )

        # Set next update just after midnight.
        today = datetime.now()
        justAfterMidnight = ( today + timedelta( days = 1 ) ).replace( hour = 0, minute = 0, second = 5 )
        fiveSecondsAfterMidnight = int( ( justAfterMidnight - today ).total_seconds() )
        self.requestUpdate( delay = fiveSecondsAfterMidnight )

        if self.notify:
            todayInShortDateFormat = today.strftime( '%b %d' ) # It is assumed/hoped the dates in the calendar result are always short date format irrespective of locale.
            for event in events:
                if todayInShortDateFormat == event.getDate():
                    Notify.Notification.new( _( "On this day..." ), event.getDescription(), self.icon ).show()


    def buildMenu( self, menu, events ):
        menuItemMaximum = self.lines - 3 # Less three to account for About, Preferences and Quit.
        menuItemCount = 0
        lastDate = ""
        for event in events:
            if event.getDate() != lastDate:
                if ( menuItemCount + 2 ) <= menuItemMaximum: # Ensure there is room for the date menu item and an event menu item.
                    menu.append( Gtk.MenuItem.new_with_label( self.removeLeadingZeroFromDate( event.getDate() ) ) )
                    lastDate = event.getDate()
                    menuItemCount += 1

                else:
                    break # Don't add the menu item for the new date and don't add a subsequent event.

            menuItem = Gtk.MenuItem.new_with_label( "    " + event.getDescription() )
            menuItem.props.name = self.removeLeadingZeroFromDate( event.getDate() ) # Allows the month/day to be passed to the copy/search functions below.
            menu.append( menuItem )
            menuItemCount += 1

            if self.copyToClipboard:
                menuItem.connect( "activate", lambda widget: Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( widget.props.name + " " + widget.props.label.strip(), -1 ) )

            elif len( self.searchURL ) > 0: # If the user enters an empty URL this means "no internet search" but also means the clipboard will not be modified.
                menuItem.connect( "activate", lambda widget: webbrowser.open( self.searchURL.replace( IndicatorOnThisDay.TAG_EVENT, ( widget.props.name + " " + widget.props.label ).replace( " ", "+" ) ) ) )

            if menuItemCount == menuItemMaximum:
                break


    def removeLeadingZeroFromDate( self, date ):
        return date[ 0 : -3 ] + ' ' + date[ -1 ] if date[ -2 ] == '0' else date[ 0 : -3 ] + ' ' + date[ -2 : ]


    def getEvents( self ):
        # Write the path of each calendar file to a temporary file - allows for one call to calendar.
        content = ""
        for calendar in self.calendars:
            if os.path.isfile( calendar ):
                content += "#include <" +calendar + ">\n"

        self.writeCacheTextWithoutTimestamp( content, IndicatorOnThisDay.CALENDARS_FILENAME )

        # Run the calendar command and parse the results.
        eventsSortedByDate = [ ]
        command = "calendar -f " + self.getCacheDirectory() + IndicatorOnThisDay.CALENDARS_FILENAME + " -A 366"
        for line in self.processGet( command ).splitlines():
            if line is None or len( line.strip() ) == 0:
                continue

            if line.startswith( "\t" ): # Continuation of the previous event.
                date = eventsSortedByDate[ -1 ].getDate()
                description = eventsSortedByDate[ -1 ].getDescription() + " " + line.strip()
                del eventsSortedByDate[ -1 ]
                eventsSortedByDate.append( Event( date, description ) )

            else:
                line = line.split( "\t" ) # Start of event: the month/day are separated from the event by a TAB.
                date = line[ 0 ].replace( "*", "" ).strip()
                description = line[ -1 ].strip() # Take the last element as there may be more than one TAB character throwing out the index of the event in the line.
                eventsSortedByDate.append( Event( date, description ) )

        # Sort events further by description.
        i = 0
        j = i + 1
        eventsSortedByDateThenDescription = [ ]
        while True:
            if j == len( eventsSortedByDate ):
                eventsSortedByDateThenDescription += sorted( eventsSortedByDate[ i : j ], key = lambda event: event.getDescription() )
                break

            if eventsSortedByDate[ j ].getDate() == eventsSortedByDate[ i ].getDate():
                j += 1

            else:
                eventsSortedByDateThenDescription += sorted( eventsSortedByDate[ i : j ], key = lambda event: event.getDescription() )
                i = j
                j = i + 1

        # Remove duplicate events.
        eventsSortedByDateThenDescriptionWithoutDuplicates = [ ]
        for event in eventsSortedByDateThenDescription:
            if event not in eventsSortedByDateThenDescriptionWithoutDuplicates:
                eventsSortedByDateThenDescriptionWithoutDuplicates.append( event )

        return eventsSortedByDateThenDescriptionWithoutDuplicates


    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

        # Calendar file settings.
        grid = self.createGrid()

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

        tree = Gtk.TreeView.new_with_model( storeSort )
        tree.expand_all()
        tree.set_hexpand( True )
        tree.set_vexpand( True )

        treeViewColumn = Gtk.TreeViewColumn( _( "Calendar" ), Gtk.CellRendererText(), text = IndicatorOnThisDay.COLUMN_CALENDAR_FILE )
        treeViewColumn.set_sort_column_id( 0 )
        treeViewColumn.set_expand( True )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Enabled" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED )
        treeViewColumn.set_sort_column_id( 1 )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
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

        addButton = Gtk.Button.new_with_label( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new calendar." ) )
        addButton.connect( "clicked", self.onCalendarAdd, tree )
        box.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected calendar." ) )
        removeButton.connect( "clicked", self.onCalendarRemove, tree )
        box.pack_start( removeButton, True, True, 0 )

        resetButton = Gtk.Button.new_with_label( _( "Reset" ) )
        resetButton.set_tooltip_text( _( "Reset to factory default." ) )
        resetButton.connect( "clicked", self.onCalendarReset, tree )
        box.pack_start( resetButton, True, True, 0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 26, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Calendars" ) ) )

        # General settings.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Lines" ) ), False, False, 0 )

        spinner = self.createSpinButton( self.lines, 1, 1000, toolTip = _( "The number of menu items available for display." ) )

        box.pack_start( spinner, False, False, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        label = Gtk.Label.new( _( "On event click" ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 1, 1, 1 )

        radioCopyToClipboard = Gtk.RadioButton.new_with_label_from_widget( None, _( "Copy event to clipboard" ) )
        radioCopyToClipboard.set_tooltip_text( _( "Copy the event text and date to the clipboard." ) )
        radioCopyToClipboard.set_active( self.copyToClipboard )
        radioCopyToClipboard.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        grid.attach( radioCopyToClipboard, 0, 2, 1, 1 )

        radioInternetSearch = Gtk.RadioButton.new_with_label_from_widget( radioCopyToClipboard, _( "Search event on the internet" ) )
        radioInternetSearch.set_tooltip_text( _( "Open the default web browser and search for the event." ) )
        radioInternetSearch.set_active( not self.copyToClipboard )
        radioInternetSearch.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        grid.attach( radioInternetSearch, 0, 3, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True )
        box.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT * 2 )

        label = Gtk.Label.new( _( "URL" ) )
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

        notifyCheckbutton = Gtk.CheckButton.new_with_label( _( "Notify" ) )
        notifyCheckbutton.set_tooltip_text( _(
            "On startup or when saving preferences,\n" + \
            "show a notification for each of today's events." ) )
        notifyCheckbutton.set_active( self.notify )
        notifyCheckbutton.set_margin_top( 10 )
        grid.attach( notifyCheckbutton, 0, 5, 1, 1 )

        autostartCheckbox, delaySpinner, box = self.createAutostartCheckboxAndDelaySpinner()
        grid.attach( box, 0, 6, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.lines = spinner.get_value_as_int()

            self.calendars = [ ]
            treeiter = store.get_iter_first()
            while treeiter != None:
                if store[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED ]:
                    self.calendars.append( store[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] )

                treeiter = store.iter_next( treeiter )

            self.copyToClipboard = radioCopyToClipboard.get_active()
            self.searchURL = searchEngineEntry.get_text().strip()
            self.notify = notifyCheckbutton.get_active()
            self.setAutostartAndDelay( autostartCheckbox.get_active(), delaySpinner.get_value_as_int() )

        return responseType


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


    def onCalendarReset( self, button, treeView ):
        if self.showOKCancel( treeView, _( "Reset calendars to factory default?" ) ) == Gtk.ResponseType.OK:
            listStore = treeView.get_model().get_model()
            listStore.clear()
            for calendar in self.getCalendars():
                if calendar == IndicatorOnThisDay.DEFAULT_CALENDAR:
                    listStore.append( [ IndicatorOnThisDay.DEFAULT_CALENDAR, Gtk.STOCK_APPLY ] )

                else:
                    listStore.append( [ calendar, None ] )


    def onCalendarRemove( self, button, treeView ):
        model, treeiter = treeView.get_selection().get_selected()
        if treeiter is None:
            self.showMessage( treeView, _( "No calendar has been selected." ) )

        elif model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] in self.getCalendars():
            self.showMessage( treeView, _( "This calendar is part of your system\nand cannot be removed." ), Gtk.MessageType.INFO )

        elif self.showOKCancel( treeView, _( "Remove the selected calendar?" ) ) == Gtk.ResponseType.OK: # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) )


    def onCalendarAdd( self, button, treeView ):
        self.onCalendarDoubleClick( treeView, None, None )


    def onCalendarDoubleClick( self, treeView, rowNumber, treeViewColumn ):
        model, treeiter = treeView.get_selection().get_selected()

        if rowNumber is None: # This is an add.
            isSystemCalendar = False

        else: # This is an edit.
            isSystemCalendar = model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] in self.getCalendars()

        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Calendar file" ) ), False, False, 0 )

        fileEntry = Gtk.Entry()
        fileEntry.set_editable( False )

        if rowNumber: # This is an edit.
            fileEntry.set_text( model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] )
            fileEntry.set_width_chars( len( fileEntry.get_text() ) * 5 / 4 ) # Sometimes the length is shorter than set due to packing, so make it longer.

        fileEntry.set_tooltip_text( _( "The path to a calendar file." ) )
        box.pack_start( fileEntry, True, True, 0 )

        browseButton = Gtk.Button.new_with_label( _( "Browse" ) )
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

        enabledCheckbutton = Gtk.CheckButton.new_with_label( _( "Enabled" ) )
        if rowNumber is None: # This is an add.
            enabledCheckbutton.set_active( True )

        else:
            enabledCheckbutton.set_active( model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED ] == Gtk.STOCK_APPLY )

        grid.attach( enabledCheckbutton, 0, 1, 1, 1 )

        title = _( "Add Calendar" )
        if rowNumber:
            title = _( "Edit Calendar" )

        dialog = self.createDialog( treeView, title, grid )

        # Need to set these here as the dialog had not been created at the point the buttons were defined.
        browseButton.connect( "clicked", self.onBrowseCalendar, dialog, fileEntry )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:

                if not isSystemCalendar and fileEntry.get_text().strip() == "":
                    self.showMessage( dialog, _( "The calendar path cannot be empty." ) )
                    fileEntry.grab_focus()
                    continue

                if not isSystemCalendar and not os.path.exists( fileEntry.get_text().strip() ):
                    self.showMessage( dialog, _( "The calendar path does not exist." ) )
                    fileEntry.grab_focus()
                    continue

                if rowNumber:
                    model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) ) # This is an edit...remove the old value and append new value.

                model.get_model().append( [ fileEntry.get_text().strip(), Gtk.STOCK_APPLY if enabledCheckbutton.get_active() else None ] )

            break

        dialog.destroy()


    def onBrowseCalendar( self, button, addEditDialog, calendarFile ):
        systemCalendars = self.getCalendars()
        dialog = Gtk.FileChooserDialog( _( "Choose a calendar file" ), addEditDialog, Gtk.FileChooserAction.OPEN, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK ) )
        dialog.set_transient_for( addEditDialog )
        dialog.set_filename( calendarFile.get_text() )
        while( True ):
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if dialog.get_filename() in systemCalendars:
                    self.showMessage( dialog, _( "The calendar is part of your system\nand is already included." ), Gtk.MessageType.INFO )

                else:
                    calendarFile.set_text( dialog.get_filename() )
                    break

            else:
                break

        dialog.destroy()


    def loadConfig( self, config ):
        self.calendars = config.get( IndicatorOnThisDay.CONFIG_CALENDARS, [ IndicatorOnThisDay.DEFAULT_CALENDAR ] )
        self.copyToClipboard = config.get( IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD, True )
        self.lines = config.get( IndicatorOnThisDay.CONFIG_LINES, self.getMenuItemsGuess() )
        self.notify = config.get( IndicatorOnThisDay.CONFIG_NOTIFY, True )
        self.searchURL = config.get( IndicatorOnThisDay.CONFIG_SEARCH_URL, IndicatorOnThisDay.SEARCH_URL_DEFAULT )


    def saveConfig( self ):
        return {
            IndicatorOnThisDay.CONFIG_CALENDARS : self.calendars,
            IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD : self.copyToClipboard,
            IndicatorOnThisDay.CONFIG_LINES : self.lines,
            IndicatorOnThisDay.CONFIG_NOTIFY : self.notify,
            IndicatorOnThisDay.CONFIG_SEARCH_URL : self.searchURL,
        }


IndicatorOnThisDay().main()
