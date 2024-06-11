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


# Neither openSUSE nor Manjaro have the 'calendar' package.
# Possible options...
#
# 1. For openSUSE/Manjaro (and any others yet to be found),
#    this indicator is unsupported.
#
# 2. From the post
#       https://forums.opensuse.org/t/debian-calendar-equivalent-in-opensuse/171251
#    the recommendation is obtain the source code
#       https://github.com/openbsd/src/tree/master/usr.bin/calendar
#       https://salsa.debian.org/meskes/bsdmainutils/-/tree/master/usr.bin/calendar
#    and include the source code/calendars as part of the pip installation,
#    then run make as part of the copy files set of instructions.
#
# 3. Have found
#       https://pypi.org/project/bsd-calendar/
#    which covers some of the original calendar program, but modifies date formats.
#    This code could be used as a basis create a standalone Python calendar module,
#    ultimately releasing to PyPI.
#    Alternatively, incorporate some version of this implementation into the indicator,
#    along with calendar files.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

from datetime import date, datetime, timedelta
import fnmatch
import gi

gi.require_version( "Gdk", "3.0" )
from gi.repository import Gdk

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

import os

from event import Event


class IndicatorOnThisDay( IndicatorBase ):

    CONFIG_CALENDARS = "calendars"
    CONFIG_COPY_TO_CLIPBOARD = "copyToClipboard"
    CONFIG_LINES = "lines"
    CONFIG_NOTIFY = "notify"
    CONFIG_SEARCH_URL = "searchURL"

    # Calendar treeview columns; one to one mapping between data model and view.
    COLUMN_CALENDAR_FILE = 0 # Path to calendar file.
    COLUMN_CALENDAR_ENABLED = 1 # tick icon (Gtk.STOCK_APPLY) or error icon (Gtk.STOCK_DIALOG_ERROR) or None.

    CALENDARS_FILENAME = "calendars.txt"

    DEFAULT_CALENDAR = "/usr/share/calendar/calendar.history"
    TAG_EVENT = "["+ _( "EVENT" )+ "]"
    SEARCH_URL_DEFAULT = "https://www.google.com/search?q=" + TAG_EVENT


    def __init__( self ):
        super().__init__(
            comments = _( "Calls the 'calendar' program and displays events in the menu." ) )


    def update( self, menu ):
        events = self.get_events()
        self.build_menu( menu, events )

        # Set next update just after midnight.
        today = datetime.now()
        just_after_midnight = ( today + timedelta( days = 1 ) ).replace( hour = 0, minute = 0, second = 5 )
        five_seconds_after_midnight = int( ( just_after_midnight - today ).total_seconds() )
        self.request_update( delay = five_seconds_after_midnight )

        if self.notify:
            today_in_short_date_format = today.strftime( '%b %d' ) # It is assumed/hoped the dates in the calendar result are always short date format irrespective of locale.
            for event in events:
                if today_in_short_date_format == event.get_date():
                    self.show_notification( _( "On this day..." ), event.get_description() )
                    # Notify.Notification.new( _( "On this day..." ), event.get_description(), self.get_icon_name() ).show()#TODO Check


    def build_menu( self, menu, events ):
        menu_item_maximum = self.lines - 3 # Less three to account for About, Preferences and Quit.
        menu_item_count = 0
        last_date = ""
        for event in events:
            if event.get_date() != last_date:
                if ( menu_item_count + 2 ) <= menu_item_maximum: # Ensure there is room for the date menu item and an event menu item.
                    self.create_and_append_menuitem(
                        menu,
                        self.remove_leading_zero_from_date( event.get_date() ) )

                    last_date = event.get_date()
                    menu_item_count += 1

                else:
                    break # Don't add the menu item for the new date and don't add a subsequent event.

            if self.copy_to_clipboard:
                f = lambda menuItem: Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( menuItem.get_name() + ' ' + menuItem.get_label().strip(), -1 )  #TODO Make sure get_labe() is the same as props.label
# Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( widget.props.name + ' ' + widget.props.label.strip(), -1 )

                self.create_and_append_menuitem(
                    menu,
                    self.get_menu_indent() + event.get_description(),
                    name = self.remove_leading_zero_from_date( event.get_date() ), # Allows the month/day to be passed to the copy/search functions below.
                    activate_functionandarguments = ( f, ) ) #TODO Ensure this function 'f' gets called.  The copy does not work on Debian 12.  Is this a wayland thing?  Test on Ubuntu 20.04.  Also document in the README.md for the indicators (via the build_readme.py).

            elif len( self.search_url ) > 0: # If the user enters an empty URL this means "no internet search" but also means the clipboard will not be modified.
                url = self.search_url.replace(
                        IndicatorOnThisDay.TAG_EVENT,
                        ( self.remove_leading_zero_from_date( event.get_date() ) + ' ' + event.get_description() ).replace( ' ', '+' ) )

                self.create_and_append_menuitem(
                    menu,
                    self.get_menu_indent() + event.get_description(),
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            menu_item_count += 1
            if menu_item_count == menu_item_maximum:
                break


    def remove_leading_zero_from_date( self, date ):
        return date[ 0 : -3 ] + ' ' + date[ -1 ] if date[ -2 ] == '0' else date[ 0 : -3 ] + ' ' + date[ -2 : ]


    def get_events( self ):
        # Write the path of each calendar file to a temporary file - allows for one call to calendar.
        content = ""
        for calendar in self.calendars:
            if os.path.isfile( calendar ):
                content += "#include <" +calendar + ">\n"

        self.write_cache_text_without_timestamp( content, IndicatorOnThisDay.CALENDARS_FILENAME )

        # Run the calendar command and parse the results.
        events_sorted_by_date = [ ]
        command = "calendar -f " + self.get_cache_directory() + IndicatorOnThisDay.CALENDARS_FILENAME + " -A 366"
        for line in self.process_get( command ).splitlines():
            if line is None or len( line.strip() ) == 0:
                continue

            if line.startswith( "\t" ): # Continuation of the previous event.
                date = events_sorted_by_date[ -1 ].get_date()
                description = events_sorted_by_date[ -1 ].get_description() + " " + line.strip()
                del events_sorted_by_date[ -1 ]
                events_sorted_by_date.append( Event( date, description ) )

            else:
                line = line.split( "\t" ) # Start of event: the month/day are separated from the event by a TAB.
                date = line[ 0 ].replace( "*", "" ).strip()
                description = line[ -1 ].strip() # Take the last element as there may be more than one TAB character throwing out the index of the event in the line.
                events_sorted_by_date.append( Event( date, description ) )

        # Sort events further by description.
        i = 0
        j = i + 1
        events_sorted_by_date_then_description = [ ]
        while True:
            if j == len( events_sorted_by_date ):
                events_sorted_by_date_then_description += sorted( events_sorted_by_date[ i : j ], key = lambda event: event.get_description() )
                break

            if events_sorted_by_date[ j ].get_date() == events_sorted_by_date[ i ].get_date():
                j += 1

            else:
                events_sorted_by_date_then_description += sorted( events_sorted_by_date[ i : j ], key = lambda event: event.get_description() )
                i = j
                j = i + 1

        # Remove duplicate events.
        events_sorted_by_date_then_description_without_duplicates = [ ]
        for event in events_sorted_by_date_then_description:
            if event not in events_sorted_by_date_then_description_without_duplicates:
                events_sorted_by_date_then_description_without_duplicates.append( event )

        return events_sorted_by_date_then_description_without_duplicates


    def on_preferences( self, dialog ):
        notebook = Gtk.Notebook()

        # Calendar file settings.
        grid = self.create_grid()

        store = Gtk.ListStore( str, str ) # Path to calendar file; tick icon (Gtk.STOCK_APPLY) or error icon (Gtk.STOCK_DIALOG_ERROR) or None.
        for calendar in self.get_calendars():
            if calendar not in self.calendars:
                store.append( [ calendar, None ] )

        for calendar in self.calendars:
            if os.path.isfile( calendar ):
                store.append( [ calendar, Gtk.STOCK_APPLY ] )

            else:
                store.append( [ calendar, Gtk.STOCK_DIALOG_ERROR ] )

        # storeSort = Gtk.TreeModelSort( model = store )
        # storeSort.set_sort_column_id( 0, Gtk.SortType.ASCENDING ) #TODO Should the 0 be IndicatorOnThisDay.COLUMN_CALENDAR_FILE??? 

        treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                Gtk.TreeModelSort( model = store ),
                ( _( "Calendar" ), _( "Enabled" ) ),
                (
                    ( Gtk.CellRendererText(), "text", IndicatorOnThisDay.COLUMN_CALENDAR_FILE ),
                    ( Gtk.CellRendererPixbuf(), "stock_id", IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED ) ),
                alignments_columnviewids = ( ( 0.5, IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED ), ),
                sortcolumnviewids_columnmodelids = (
                    ( IndicatorOnThisDay.COLUMN_CALENDAR_FILE, IndicatorOnThisDay.COLUMN_CALENDAR_FILE ),
                    ( IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED, IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED ) ),
                tooltip_text = _( "Double click to edit a calendar." ),
                rowactivatedfunctionandarguments= ( self.on_calendar_double_click, ) )

        # tree = Gtk.TreeView.new_with_model( storeSort )
        # tree.expand_all()
        # tree.set_hexpand( True )
        # tree.set_vexpand( True )

        # treeViewColumn = Gtk.TreeViewColumn( _( "Calendar" ), Gtk.CellRendererText(), text = IndicatorOnThisDay.COLUMN_CALENDAR_FILE )
        # treeViewColumn.set_sort_column_id( 0 )
        # treeViewColumn.set_expand( True )
        # tree.append_column( treeViewColumn )

        # treeViewColumn = Gtk.TreeViewColumn( _( "Enabled" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED )
        # treeViewColumn.set_sort_column_id( 1 )
        # treeViewColumn.set_expand( True )
        # treeViewColumn.set_alignment( 0.5 )
        # tree.append_column( treeViewColumn )

        # tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        # tree.connect( "row-activated", self.on_calendar_double_click )
        # tree.set_tooltip_text( _( "Double click to edit a calendar." ) )

        # scrolledWindow = Gtk.ScrolledWindow()
        # scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        # scrolledWindow.add( tree )

        # grid.attach( scrolledWindow, 0, 0, 1, 25 )
        grid.attach( scrolledwindow, 0, 0, 1, 25 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )

        # addButton = Gtk.Button.new_with_label( _( "Add" ) )
        # addButton.set_tooltip_text( _( "Add a new calendar." ) )
        # addButton.connect( "clicked", self.on_calendar_add, tree )
        # box.pack_start( addButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Add" ),
                tooltip_text = _( "Add a new calendar." ),
                clicked_functionandarguments = ( self.on_calendar_add, treeview ) ),
            True,
            True,
            0 )

        # removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        # removeButton.set_tooltip_text( _( "Remove the selected calendar." ) )
        # removeButton.connect( "clicked", self.on_calendar_remove, tree )
        # box.pack_start( removeButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Remove" ),
                tooltip_text = _( "Remove the selected calendar." ),
                clicked_functionandarguments = ( self.on_calendar_remove, treeview ) ),
            True,
            True,
            0 )

        # resetButton = Gtk.Button.new_with_label( _( "Reset" ) )
        # resetButton.set_tooltip_text( _( "Reset to factory default." ) )
        # resetButton.connect( "clicked", self.on_calendar_reset, tree )
        # box.pack_start( resetButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Reset" ),
                tooltip_text = _( "Reset to factory default." ),
                clicked_functionandarguments = ( self.on_calendar_reset, treeview ) ),
            True,
            True,
            0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 26, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Calendars" ) ) )

        # General settings.
        grid = self.create_grid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Lines" ) ), False, False, 0 )

        spinner = \
            self.create_spinbutton(
                self.lines,
                1,
                1000,
                tooltip_text = _( "The number of menu items available for display." ) )

        box.pack_start( spinner, False, False, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        label = Gtk.Label.new( _( "On event click" ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 1, 1, 1 )

        # radio_copy_to_clipboard = Gtk.RadioButton.new_with_label_from_widget( None, _( "Copy event to clipboard" ) )
        # radio_copy_to_clipboard.set_tooltip_text( _( "Copy the event text and date to the clipboard." ) )
        # radio_copy_to_clipboard.set_active( self.copy_to_clipboard )
        # radio_copy_to_clipboard.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( radio_copy_to_clipboard, 0, 2, 1, 1 )
#TODO Check above.
        radio_copy_to_clipboard = \
            self.create_radiobutton(
                None,
                _( "Copy event to clipboard" ),
                tooltip_text = _( "Copy the event text and date to the clipboard." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.copy_to_clipboard )

        grid.attach( radio_copy_to_clipboard, 0, 2, 1, 1 )

        # radio_internet_search = Gtk.RadioButton.new_with_label_from_widget( radio_copy_to_clipboard, _( "Search event on the internet" ) )
        # radio_internet_search.set_tooltip_text( _( "Open the default web browser and search for the event." ) )
        # radio_internet_search.set_active( not self.copy_to_clipboard )
        # radio_internet_search.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( radio_internet_search, 0, 3, 1, 1 )
#TODO Check above.
        radio_internet_search = \
            self.create_radiobutton(
                radio_copy_to_clipboard,
                _( "Search event on the internet" ),
                tooltip_text = _( "Open the default web browser and search for the event." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = not self.copy_to_clipboard )

        grid.attach( radio_internet_search, 0, 3, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True )
        box.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT * 2 )

        label = Gtk.Label.new( _( "URL" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        search_engine_entry = Gtk.Entry()
        search_engine_entry.set_tooltip_text( _(
            "The URL to search for the event.\n\n" + \
            "Use {0} in the URL to specify the\n" + \
            "position of the event text/date.\n\n" + \
            "If the URL is empty and 'search' is selected,\n" + \
            "the search will effectively be ignored.\n\n" + \
            "If the URL is empty and 'copy' is selected,\n" + \
            "the URL is reset back to factory default." ).format( IndicatorOnThisDay.TAG_EVENT ) )
        search_engine_entry.set_text( self.search_url )
        search_engine_entry.set_sensitive( not self.copy_to_clipboard )
        box.pack_start( search_engine_entry, True, True, 0 )

        grid.attach( box, 0, 4, 1, 1 )

        radio_copy_to_clipboard.connect(
            "toggled",
            self.on_event_click_radio,
            radio_copy_to_clipboard,
            radio_internet_search,
            search_engine_entry )

        radio_internet_search.connect(
            "toggled",
            self.on_event_click_radio,
            radio_copy_to_clipboard,
            radio_internet_search,
            search_engine_entry )

        notify_checkbutton = \
            self.create_checkbutton(
                _( "Notify" ),
                tooltip_text = _(
                    "On startup or when saving preferences,\n" + \
                    "show a notification for each of today's events." ),
                margin_top = 10,
                active = self.notify )
#TODO Make sure this is converted okay
        # notify_checkbutton = Gtk.CheckButton.new_with_label( _( "Notify" ) )
        # notify_checkbutton.set_tooltip_text( _(
        #     "On startup or when saving preferences,\n" + \
        #     "show a notification for each of today's events." ) )
        # notify_checkbutton.set_active( self.notify )
        # notify_checkbutton.set_margin_top( 10 )
        grid.attach( notify_checkbutton, 0, 5, 1, 1 )

        autostart_checkbox, delay_spinner, box = self.create_autostart_checkbox_and_delay_spinner()
        grid.attach( box, 0, 6, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.lines = spinner.get_value_as_int()

            self.calendars = [ ]
            treeiter = store.get_iter_first()
            while treeiter != None:
                if store[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED ]:
                    self.calendars.append( store[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] )

                treeiter = store.iter_next( treeiter )

            self.copy_to_clipboard = radio_copy_to_clipboard.get_active()
            self.search_url = search_engine_entry.get_text().strip()
            self.notify = notify_checkbutton.get_active()
            self.set_autostart_and_delay( autostart_checkbox.get_active(), delay_spinner.get_value_as_int() )

        return response_type


    def on_event_click_radio( self, source, radio_copy_to_clipboard, radio_internet_search, search_engine_entry ):
        search_engine_entry.set_sensitive( source == radio_internet_search )
        if source == radio_copy_to_clipboard and len( search_engine_entry.get_text() ) == 0:
            search_engine_entry.set_text( IndicatorOnThisDay.SEARCH_URL_DEFAULT )


    def get_calendars( self ):
        calendars = [ ]
        for root, directories, filenames in os.walk( "/usr/share/calendar" ):
            for filename in fnmatch.filter( filenames, "calendar.*" ):
                calendars.append( os.path.join( root, filename ) )

        calendars.sort()
        return calendars


    def on_calendar_reset( self, button, treeview ):
        if self.show_ok_cancel( treeview, _( "Reset calendars to factory default?" ) ) == Gtk.ResponseType.OK:
            liststore = treeview.get_model().get_model()
            liststore.clear()
            for calendar in self.get_calendars():
                if calendar == IndicatorOnThisDay.DEFAULT_CALENDAR:
                    liststore.append( [ IndicatorOnThisDay.DEFAULT_CALENDAR, Gtk.STOCK_APPLY ] )

                else:
                    liststore.append( [ calendar, None ] )


    def on_calendar_remove( self, button, treeview ):
        model, treeiter = treeview.get_selection().get_selected()
        if treeiter is None:
            self.show_message( treeview, _( "No calendar has been selected." ) )

        elif model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] in self.get_calendars():
            self.show_message(
                treeview,
                _( "This calendar is part of your system\nand cannot be removed." ),
                Gtk.MessageType.INFO )

        elif self.show_ok_cancel( treeview, _( "Remove the selected calendar?" ) ) == Gtk.ResponseType.OK: # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) )


    def on_calendar_add( self, button, treeview ):
        self.on_calendar_double_click( treeview, None, None )


    def on_calendar_double_click( self, treeview, row_number, treeviewcolumn ):
        model, treeiter = treeview.get_selection().get_selected()

        if row_number is None: # This is an add.
            is_system_calendar = False

        else: # This is an edit.
            is_system_calendar = model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] in self.get_calendars()

        grid = self.create_grid()

        title = _( "Add Calendar" )
        if row_number:
            title = _( "Edit Calendar" )

        dialog = self.create_dialog( treeview, title, grid )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Calendar file" ) ), False, False, 0 )

        file_entry = Gtk.Entry()
        file_entry.set_editable( False )

        if row_number: # This is an edit.
            file_entry.set_text( model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] )
            file_entry.set_width_chars( len( file_entry.get_text() ) * 5 / 4 ) # Sometimes the length is shorter than set due to packing, so make it longer.

        file_entry.set_tooltip_text( _( "The path to a calendar file." ) )
        box.pack_start( file_entry, True, True, 0 )

        # browse_button = Gtk.Button.new_with_label( _( "Browse" ) )
        # browse_button.set_sensitive( not is_system_calendar )
        # if is_system_calendar:
        #     browse_button.set_tooltip_text( _(
        #         "This calendar is part of your\n" + \
        #         "system and cannot be modified." ) )
        #
        # else:
        #     browse_button.set_tooltip_text( _(
        #         "Choose a calendar file.\n\n" + \
        #         "Ensure the calendar file is\n" + \
        #         "valid by running through\n" + \
        #         "'calendar' in a terminal." ) )
        #
        # box.pack_start( browse_button, False, False, 0 )
        # browse_button.connect( "clicked", self.on_browse_calendar, dialog, file_entry )
#TODO Ensure this was converted correctly.

        box.pack_start(
            self.create_button(
                _( "Browse" ),
                tooltip_text = _(
                    "This calendar is part of your\n" + \
                    "system and cannot be modified." ) \
                    if is_system_calendar else _(
                    "Choose a calendar file.\n\n" + \
                    "Ensure the calendar file is\n" + \
                    "valid by running through\n" + \
                    "'calendar' in a terminal." ),
                    sensitive = not is_system_calendar,
                    clicked_functionandarguments = ( self.on_browse_calendar, dialog, file_entry ) ),
             False,
             False,
             0 )

        grid.attach( box, 0, 0, 1, 1 )

        enabled_checkbutton = self.create_checkbutton( _( "Enabled" ) )
#TODO Make sure this is converted okay
        # enabled_checkbutton = Gtk.CheckButton.new_with_label( _( "Enabled" ) )
        if row_number is None: # This is an add.
            enabled_checkbutton.set_active( True )

        else:
            enabled_checkbutton.set_active( model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED ] == Gtk.STOCK_APPLY )

        grid.attach( enabled_checkbutton, 0, 1, 1, 1 )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if not is_system_calendar and file_entry.get_text().strip() == "":
                    self.show_message( dialog, _( "The calendar path cannot be empty." ) )
                    file_entry.grab_focus()
                    continue

                if not is_system_calendar and not os.path.exists( file_entry.get_text().strip() ):
                    self.show_message( dialog, _( "The calendar path does not exist." ) )
                    file_entry.grab_focus()
                    continue

                if row_number:
                    model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) ) # This is an edit...remove the old value and append new value.

                model.get_model().append( [
                    file_entry.get_text().strip(),
                    Gtk.STOCK_APPLY if enabled_checkbutton.get_active() else None ] )

            break

        dialog.destroy()


    def on_browse_calendar( self, button, add_edit_dialog, calendar_file ):
        system_calendars = self.get_calendars()

#TODO This matches the new code below.
        # dialog = \
        #     Gtk.FileChooserDialog(
        #         title = _( "Choose a calendar file" ),
        #         parent = add_edit_dialog,
        #         action = Gtk.FileChooserAction.OPEN )
        #
        # dialog.add_buttons = ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK )
        # dialog.set_transient_for( add_edit_dialog )
        # dialog.set_filename( calendar_file.get_text() )
        dialog = \
            self.create_filechooser_dialog( 
                _( "Choose a calendar file" ),
                add_edit_dialog,
                calendar_file.get_text() )

        while( True ):
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if dialog.get_filename() in system_calendars:
                    self.show_message( dialog, _( "The calendar is part of your system\nand is already included." ), Gtk.MessageType.INFO )

                else:
                    calendar_file.set_text( dialog.get_filename() )
                    break

            else:
                break

        dialog.destroy()


    def load_config( self, config ):
        self.calendars = config.get( IndicatorOnThisDay.CONFIG_CALENDARS, [ IndicatorOnThisDay.DEFAULT_CALENDAR ] )
        self.copy_to_clipboard = config.get( IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD, True )
        self.lines = config.get( IndicatorOnThisDay.CONFIG_LINES, self.get_menuitems_guess() )
        self.notify = config.get( IndicatorOnThisDay.CONFIG_NOTIFY, True )
        self.search_url = config.get( IndicatorOnThisDay.CONFIG_SEARCH_URL, IndicatorOnThisDay.SEARCH_URL_DEFAULT )


    def save_config( self ):
        return {
            IndicatorOnThisDay.CONFIG_CALENDARS : self.calendars,
            IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD : self.copy_to_clipboard,
            IndicatorOnThisDay.CONFIG_LINES : self.lines,
            IndicatorOnThisDay.CONFIG_NOTIFY : self.notify,
            IndicatorOnThisDay.CONFIG_SEARCH_URL : self.search_url,
        }


IndicatorOnThisDay().main()
