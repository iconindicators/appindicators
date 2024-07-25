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


#TODO Amend the changelog.md and/or readme.md
# to mention the clipboard only works under X11?


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

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

import os

from event import Event


class IndicatorOnThisDay( IndicatorBase ):
    # Unused within the indicator; used by build_wheel.py when building the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator On This Day" )

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


    def build_menu( self, menu, events ):
        menu_item_maximum = self.lines - 3 # Less three to account for About, Preferences and Quit.
        menu_item_count = 0
        last_date = ""
        for event in events:
            if event.get_date() != last_date:
                if ( menu_item_count + 2 ) > menu_item_maximum: # Ensure there is room for the date menu item and an event menu item.
                    break # Don't add the menu item for the new date and don't add a subsequent event.

                event_date = self.remove_leading_zero_from_date( event.get_date() )
                self.create_and_append_menuitem( menu, event_date )

                last_date = event.get_date()
                menu_item_count += 1

            if self.copy_to_clipboard:
                name = event_date
                activate_functionandarguments = ( 
                    lambda menuitem:
                        self.copy_to_selection( menuitem.get_name() + ' ' + menuitem.get_label().strip() ), )

            else:
                if len( self.search_url ) > 0:
                    date_and_description = event_date + ' ' + event.get_description()
                    name = self.search_url.replace( IndicatorOnThisDay.TAG_EVENT, date_and_description )
                    name = name.replace( ' ', '+' )
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), )

                else: # The user has entered an empty URL this means "no internet search".
                    name = ""
                    activate_functionandarguments = None

            self.create_and_append_menuitem(
                menu,
                event.get_description(),
                name = name,
                activate_functionandarguments = activate_functionandarguments,
                indent = ( 1, 1 ) )

            menu_item_count += 1
            if menu_item_count == menu_item_maximum:
                break


#TODO Maybe delete
    def build_menuORIGINAL( self, menu, events ):
        menu_item_maximum = self.lines - 3 # Less three to account for About, Preferences and Quit.
        menu_item_count = 0
        last_date = ""
        for event in events:
            if event.get_date() != last_date:
                if ( menu_item_count + 2 ) <= menu_item_maximum: # Ensure there is room for the date menu item and an event menu item.
                    event_date = self.remove_leading_zero_from_date( event.get_date() ) #TODO Should this be one level up?
                    self.create_and_append_menuitem( menu, event_date )

                    # self.create_and_append_menuitem(
                    #     menu,
                    #     self.remove_leading_zero_from_date( event.get_date() ) )

                    last_date = event.get_date()
                    menu_item_count += 1

                else:
                    break # Don't add the menu item for the new date and don't add a subsequent event.

#TODO Check the logic behind the if/elif below...
            if self.copy_to_clipboard:
                name = event_date
                activate_functionandarguments = ( 
                    lambda menuitem:
                        self.copy_to_selection( menuitem.get_name() + ' ' + menuitem.get_label().strip() ), )

                # self.create_and_append_menuitem(
                #     menu,
                #     event.get_description(),
                #     name = name,
                #     activate_functionandarguments = ( 
                #         lambda menuitem:
                #             self.copy_to_selection( menuitem.get_name() + ' ' + menuitem.get_label().strip() ), ),
                #     indent = ( 1, 1 ) )
                
                # self.create_and_append_menuitem(
                #     menu,
                #     event.get_description(),
                #     # name = self.remove_leading_zero_from_date( event.get_date() ), # Allows the month/day to be passed to the copy/search functions below.
                #     name = event_date,  #TODO NOt sure about this comment --->   # Allows the month/day to be passed to the copy/search functions below.
                #     activate_functionandarguments = ( 
                #         lambda menuitem:
                #             self.copy_to_selection( menuitem.get_name() + ' ' + menuitem.get_label().strip() ), ),
                #     indent = ( 1, 1 ) )

            elif len( self.search_url ) > 0: # If the user enters an empty URL this means "no internet search" but also means the clipboard will not be modified.
                # date_and_description = \
                #     self.remove_leading_zero_from_date( event.get_date() ) + \
                #     ' ' + \
                #     event.get_description()
                #
                # url = \
                #     self.search_url.replace(
                #         IndicatorOnThisDay.TAG_EVENT,
                #         date_and_description.replace( ' ', '+' ) )

                date_and_description = event_date + ' ' + event.get_description()

                name = \
                    self.search_url.replace(
                        IndicatorOnThisDay.TAG_EVENT,
                        date_and_description.replace( ' ', '+' ) )

                activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), )

                # self.create_and_append_menuitem(
                #     menu,
                #     event.get_description(),
                #     name = url,
                #     activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ),
                #     indent = ( 1, 1 ) )

            self.create_and_append_menuitem(
                menu,
                event.get_description(),
                name = name,
                activate_functionandarguments = activate_functionandarguments,
                indent = ( 1, 1 ) )

            menu_item_count += 1
            if menu_item_count == menu_item_maximum:
                break


    def remove_leading_zero_from_date( self, date ):
        if date[ -2 ] == '0':
            _date = date[ 0 : -3 ] + ' ' + date[ -1 ]
        
        else:
            _date = date[ 0 : -3 ] + ' ' + date[ -2 : ]

        return _date


    def get_events( self ):
        # Write the path of each calendar file to a temporary file - allows for one call to calendar.
        content = ""
        for calendar in self.calendars:
            if os.path.isfile( calendar ):
                content += "#include <" + calendar + ">\n"

        self.write_cache_text_without_timestamp( content, IndicatorOnThisDay.CALENDARS_FILENAME )

        # Run the calendar command and parse the results.
        events_sorted_by_date = [ ]
        command = \
            "calendar -f " + \
            self.get_cache_directory() + \
            IndicatorOnThisDay.CALENDARS_FILENAME + \
            " -A 366"

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
                events_sorted_by_date_then_description += \
                    sorted(
                        events_sorted_by_date[ i : j ],
                        key = lambda event: event.get_description() )

                break

            if events_sorted_by_date[ j ].get_date() == events_sorted_by_date[ i ].get_date():
                j += 1

            else:
                events_sorted_by_date_then_description += \
                    sorted(
                        events_sorted_by_date[ i : j ],
                        key = lambda event: event.get_description() )

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

        grid.attach( scrolledwindow, 0, 0, 1, 25 )

        box = \
            self.create_buttons_in_box(
                (
                    _( "Add" ),
                    _( "Remove" ),
                    _( "Reset" ) ),
                (
                    _( "Add a new calendar." ),
                    _( "Remove the selected calendar." ),
                    _( "Reset to factory default." ) ),
                (
                    ( self.on_calendar_add, treeview ),
                    ( self.on_calendar_remove, treeview ),
                    ( self.on_calendar_reset, treeview ) ) )
        
        grid.attach( box, 0, 26, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Calendars" ) ) )

        # General settings.
        grid = self.create_grid()

        spinner = \
            self.create_spinbutton(
                self.lines,
                1,
                1000,
                tooltip_text = _( "The number of menu items available for display." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Lines" ) ), False ),
                    ( spinner, False ) ) ),
            0, 0, 1, 1 )

        grid.attach(
            self.create_box(
                ( ( Gtk.Label.new( _( "On event click" ) ), False ), ),
                margin_top = 10 ),
            0, 1, 1, 1 )

        radio_copy_to_clipboard = \
            self.create_radiobutton(
                None,
                _( "Copy event to clipboard" ),
                 tooltip_text = _( "Copy the event text and date to the clipboard." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.copy_to_clipboard )

        grid.attach( radio_copy_to_clipboard, 0, 2, 1, 1 )

        radio_internet_search = \
            self.create_radiobutton(
                radio_copy_to_clipboard,
                _( "Search event on the internet" ),
                tooltip_text = _( "Open the default web browser and search for the event." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = not self.copy_to_clipboard )

        grid.attach( radio_internet_search, 0, 3, 1, 1 )

        search_engine_entry = \
            self.create_entry(
                self.search_url,
                tooltip_text = _(
                    "The URL to search for the event.\n\n" +
                    "Use {0} in the URL to specify the\n" +
                    "position of the event text/date.\n\n" +
                    "If the URL is empty and 'search' is selected,\n" +
                    "the search will effectively be ignored.\n\n" +
                    "If the URL is empty and 'copy' is selected,\n" +
                    "the URL is reset back to factory default." ).format( IndicatorOnThisDay.TAG_EVENT ),
                sensitive = not self.copy_to_clipboard )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "URL" ) ), False ),
                    ( search_engine_entry, True ) ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT * 2 ),
            0, 4, 1, 1 )

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
                    "On startup or when saving preferences,\n" +
                    "show a notification for each of today's events." ),
                margin_top = 10,
                active = self.notify )

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


    def on_event_click_radio(
            self,
            source,
            radio_copy_to_clipboard,
            radio_internet_search,
            search_engine_entry ):

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
        if self.show_dialog_ok_cancel( treeview, _( "Reset calendars to factory default?" ) ) == Gtk.ResponseType.OK:
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
            self.show_dialog_ok( treeview, _( "No calendar has been selected." ) )

        else:
            selected_calendar_path = \
                model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ]

            if selected_calendar_path in self.get_calendars():
                self.show_dialog_ok(
                    treeview,
                    _( "This is a system calendar and cannot be removed." ),
                    message_type = Gtk.MessageType.INFO )

            else:
                response = \
                    self.show_dialog_ok_cancel(
                        treeview,
                        _( "Remove the selected calendar?" ) )

                if response == Gtk.ResponseType.OK:
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

        dialog = self.create_dialog( treeview, title, content_widget = grid )

        file_entry = \
            self.create_entry(
                model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] if row_number else "",
                tooltip_text = _( "The path to a calendar file." ),
                editable = False,
                make_longer = True )

        browse_button = \
            self.create_button(
                _( "Browse" ),
                tooltip_text = _(
                    "This calendar is part of your\n" +
                    "system and cannot be modified." )
                    if is_system_calendar else _(
                    "Choose a calendar file.\n\n" +
                    "Ensure the calendar file is\n" +
                    "valid by running through\n" +
                    "'calendar' in a terminal." ),
                    sensitive = not is_system_calendar,
                    clicked_functionandarguments = ( self.on_browse_calendar, dialog, file_entry ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Calendar file" ) ), False ),
                    ( file_entry, True ),
                    ( browse_button, False ) ) ),
            0, 0, 1, 1 )

        enabled_checkbutton = \
            self.create_checkbutton(
                _( "Enabled" ),
                active = \
                    True
                    if row_number is None else \
                    model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_ENABLED ] == Gtk.STOCK_APPLY )

        grid.attach( enabled_checkbutton, 0, 1, 1, 1 )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if not is_system_calendar and file_entry.get_text().strip() == "":
                    self.show_dialog_ok( dialog, _( "The calendar path cannot be empty." ) )
                    file_entry.grab_focus()
                    continue

                if not is_system_calendar and not os.path.exists( file_entry.get_text().strip() ):
                    self.show_dialog_ok( dialog, _( "The calendar path does not exist." ) )
                    file_entry.grab_focus()
                    continue

                if row_number:
                    # This is an edit...remove the old value and append new value.
                    model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) )

                model.get_model().append( [
                    file_entry.get_text().strip(),
                    Gtk.STOCK_APPLY if enabled_checkbutton.get_active() else None ] )

            break

        dialog.destroy()


    def on_browse_calendar( self, button, add_edit_dialog, calendar_file ):
        system_calendars = self.get_calendars()

        dialog = \
            self.create_filechooser_dialog(
                _( "Choose a calendar file" ),
                add_edit_dialog,
                calendar_file.get_text() )

        while( True ):
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if dialog.get_filename() in system_calendars:
                    self.show_dialog_ok(
                        dialog,
                        _( "The calendar is part of your system\nand is already included." ), 
                        nessage_type = Gtk.MessageType.INFO )

                else:
                    calendar_file.set_text( dialog.get_filename() )
                    break

            else:
                break

        dialog.destroy()


    def load_config( self, config ):
        self.calendars = \
            config.get(
                IndicatorOnThisDay.CONFIG_CALENDARS,
                [ IndicatorOnThisDay.DEFAULT_CALENDAR ] )

        self.copy_to_clipboard = \
            config.get(
                IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD,
                True )

        self.lines = \
            config.get(
                IndicatorOnThisDay.CONFIG_LINES,
                self.get_menuitems_guess() )

        self.notify = config.get( IndicatorOnThisDay.CONFIG_NOTIFY, True )

        self.search_url = \
            config.get(
                IndicatorOnThisDay.CONFIG_SEARCH_URL,
                IndicatorOnThisDay.SEARCH_URL_DEFAULT )


    def save_config( self ):
        return {
            IndicatorOnThisDay.CONFIG_CALENDARS : self.calendars,
            IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD : self.copy_to_clipboard,
            IndicatorOnThisDay.CONFIG_LINES : self.lines,
            IndicatorOnThisDay.CONFIG_NOTIFY : self.notify,
            IndicatorOnThisDay.CONFIG_SEARCH_URL : self.search_url,
        }


IndicatorOnThisDay().main()
