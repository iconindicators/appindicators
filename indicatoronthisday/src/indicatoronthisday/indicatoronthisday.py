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


'''
Application indicator which displays calendar events.

Neither openSUSE nor Manjaro have the 'calendar' package.
Possible options...

1. For openSUSE/Manjaro, this indicator is unsupported.

2. From the post
     https://forums.opensuse.org/t/debian-calendar-equivalent-in-opensuse/171251
   the recommendation is obtain the source code
     https://github.com/openbsd/src/tree/master/usr.bin/calendar
     https://salsa.debian.org/meskes/bsdmainutils/-/tree/master/usr.bin/calendar
   and include the source code/calendars as part of the pip installation,
   then run make as part of the copy files set of instructions.

3. The project
     https://pypi.org/project/bsd-calendar/
   is based on the original calendar program, but modifies date formats.
   This code could be used to create a standalone Python calendar module,
   ultimately released to PyPI.
   Alternatively, incorporate some version of this implementation into the
   indicator, along with calendar files.
'''


import fnmatch
import os
import threading
import time

from datetime import datetime, timedelta
from itertools import chain, groupby
from pathlib import Path

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from indicatorbase import IndicatorBase

from event import Event


class IndicatorOnThisDay( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used when building the wheel to create the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator On This Day" )
    indicator_categories = "Categories=Utility;Amusement"

    CALENDARS_FILENAME = "calendars.txt"

    # Calendar treeview columns; model and view have same columns.
    COLUMN_CALENDAR_FILE = 0 # Path to calendar file.
    COLUMN_ENABLED = 1  # Boolean.

    CONFIG_CALENDARS = "calendars"
    CONFIG_COPY_TO_CLIPBOARD = "copyToClipboard"
    CONFIG_LINES = "lines"
    CONFIG_NOTIFY = "notify"
    CONFIG_SEARCH_URL = "searchURL"

    TAG_EVENT = "["+ _( "EVENT" )+ "]"
    SEARCH_URL_DEFAULT = "https://www.google.com/search?q=" + TAG_EVENT

    SYSTEM_CALENDARS = "/usr/share/calendar"


    def __init__( self ):
        super().__init__(
            comments = _(
                "Calls the 'calendar' program and displays events " +
                "in the menu." ) )


    def update(
        self,
        menu ):

        events = self.get_events()
        self.build_menu( menu, events )

        # Set next update just after midnight.
        today = datetime.now()
        just_after_midnight = (
            today + timedelta( days = 1 ) ).replace(
                hour = 0, minute = 0, second = 5 )

        five_seconds_after_midnight = (
            int( ( just_after_midnight - today ).total_seconds() ) )

        self.request_update( delay = five_seconds_after_midnight )

        if self.notify:
            # Show notifications in a thread to avoid blocking the update.
            threading.Thread(
                target = self._show_notifications,
                args = ( events, today ) ).start()


    def _show_notifications(
        self,
        events,
        today ):

        # Assume the dates in the calendar result are always in short date
        # format irrespective of locale.
        today_in_short_date_format = today.strftime( '%b %d' )

        for event in events:
            if today_in_short_date_format == event.get_date():
                self.show_notification(
                    _( "On this day..." ), event.get_description() )

                # Need a delay otherwise some/most of the notifications will
                # disappear too quickly.
                time.sleep( 3 )


    def build_menu(
        self,
        menu,
        events ):

        menu_item_maximum = self.lines - 3 # Account for About/Preferences/Quit.
        menu_item_count = 0
        last_date = ""
        for event in events:
            if event.get_date() != last_date:
                # Ensure space for the date menu item and an event menu item.
                if ( menu_item_count + 2 ) > menu_item_maximum:
                    # Don't add the menu item for the new date and don't add a
                    # subsequent event.
                    break

                event_date = (
                    self.remove_leading_zero_from_date( event.get_date() ) )

                self.create_and_append_menuitem( menu, event_date )

                last_date = event.get_date()
                menu_item_count += 1

            if self.copy_to_clipboard:
                name = event_date
                activate_functionandarguments = None
                if self.is_clipboard_supported():
                    activate_functionandarguments = (
                        lambda menuitem:
                            self.copy_to_selection(
                                menuitem.get_name() +
                                ' ' +
                                menuitem.get_label().strip() ), )

            else:
                if len( self.search_url ) > 0:
                    date_and_description = (
                        event_date + ' ' + event.get_description() )

                    name = (
                        self.search_url.replace(
                            IndicatorOnThisDay.TAG_EVENT,
                            date_and_description ) )

                    name = name.replace( ' ', '+' )
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), )

                else: # The user has entered an empty URL (no internet search).
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


    def remove_leading_zero_from_date(
        self,
        date_ ):

        _date = date_[ 0 : -3 ] + ' '
        if date_[ -2 ] == '0':
            _date += date_[ -1 ]

        else:
            _date += date_[ -2 : ]

        return _date


    def get_events( self ):
        # Write the path of each calendar file to a temporary file;
        # only need to call calendar once.
        content = ""
        at_least_one_calendar_is_enabled = False
        for calendar, enabled in self.calendars:
            if enabled:
                at_least_one_calendar_is_enabled = True
                if Path( calendar ).is_file():
                    content += "#include <" + calendar + ">\n"

        events_grouped_by_date = [ ]
        if content:
            events_grouped_by_date = self._get_events( content )

        elif at_least_one_calendar_is_enabled:
            self.show_notification(
                _( "Warning" ),
                _( "No enabled calendars have a valid location!" ) )

        else:
            self.show_notification(
                _( "Warning" ),
                _( "No enabled calendars!" ) )

        return events_grouped_by_date


    def _get_events(
        self,
        content ):

        self.write_cache_text_without_timestamp(
            content, IndicatorOnThisDay.CALENDARS_FILENAME )

        # Parse the results from the calendar command into events sorted by
        # date then description.
        command = (
            "calendar -f " +
            str(
                self.get_cache_directory()
                /
                IndicatorOnThisDay.CALENDARS_FILENAME ) +
            " -A 366" )

        events_sorted_by_date = [ ]
        for line in self.process_get( command ).splitlines():
            if line.startswith( '\t' ): # Continuation of the previous event.
                date_ = events_sorted_by_date[ -1 ].get_date()

                description = (
                    events_sorted_by_date[ -1 ].get_description()
                    +
                    " "
                    +
                    line.strip() )

                del events_sorted_by_date[ -1 ]
                events_sorted_by_date.append( Event( date_, description ) )

            else:
                # Start of event: month/day and event are separated by a TAB.
                line = line.split( '\t' )
                date_ = line[ 0 ].replace( '*', '' ).strip()

                # Take the last element as there may be more than one TAB
                # character throwing out the index of the event in the line.
                description = line[ -1 ].strip()

                events_sorted_by_date.append( Event( date_, description ) )

        events_grouped_by_date = [ ]
        grouped_events_sorted_by_date = (
            groupby(
                events_sorted_by_date, key = lambda event: event.get_date() ) )

        for date_, event in grouped_events_sorted_by_date:
            events_grouped_by_date.append(
                sorted(
                    list( event ),
                    key = lambda event: event.get_description() ) )

        return list( chain( *events_grouped_by_date ) )


    def on_preferences(
        self,
        dialog ):

        notebook = Gtk.Notebook()

        # Calendars.
        grid = self.create_grid()

        store = Gtk.ListStore( str, bool )
        for location, enabled in self.calendars:
            if Path( location ).is_file():
                store.append( [ location, enabled ] )

            else:
                store.append( [ location, False ] )

        # Ensure all system calendars are present in the list of calendars,
        # not just those selected/defined by the user.
        for system_calendar in self.get_system_calendars():
            system_calendar_in_user_calendars = (
                [ system_calendar, True ] in self.calendars
                or
                [ system_calendar, False ] in self.calendars )

            if not system_calendar_in_user_calendars:
                store.append( [ system_calendar, False ] )

        store = Gtk.TreeModelSort( model = store )

#TODO Can/should this go into indicatorbase?
# (along with the on_checkbox function below)
# Used by fortune, onthisday, lunar.
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect(
            "toggled",
            self.on_checkbox,
            store,
            IndicatorOnThisDay.COLUMN_ENABLED )

        treeview, scrolledwindow = (
            self.create_treeview_within_scrolledwindow(
                store,
                (
                    _( "Calendar" ),
                    _( "Enabled" ) ),
                (
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorOnThisDay.COLUMN_CALENDAR_FILE ),
                    (
                        renderer_toggle,
                        "active",
                        IndicatorOnThisDay.COLUMN_ENABLED ) ),
                alignments_columnviewids = (
                    ( 0.5, IndicatorOnThisDay.COLUMN_ENABLED ), ),
                sortcolumnviewids_columnmodelids = (
                    (
                        IndicatorOnThisDay.COLUMN_CALENDAR_FILE,
                        IndicatorOnThisDay.COLUMN_CALENDAR_FILE ),
                    (
                        IndicatorOnThisDay.COLUMN_ENABLED,
                        IndicatorOnThisDay.COLUMN_ENABLED ) ),
                tooltip_text = _( "Double click to edit a calendar." ),
                rowactivatedfunctionandarguments =
                    ( self.on_calendar_double_click, dialog ) ) )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        box, add, remove = (
            self.create_buttons_in_box(
                (
                    _( "Add" ),
                    _( "Remove" ) ),
                (
                    _( "Add a new calendar." ),
                    _( "Remove the selected calendar." ) ),
                (
                    ( self.on_calendar_add, treeview ),
                    ( self.on_calendar_remove, treeview ) ) ) )

        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Calendars" ) ) )

        # General.
        grid = self.create_grid()

        spinner = (
            self.create_spinbutton(
                self.lines,
                1,
                1000,
                tooltip_text =
                    _( "The number of menu items available for display." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Lines" ) ), False ),
                    ( spinner, False ) ) ),
            0, 0, 1, 1 )

        grid.attach(
            self.create_box(
                ( ( Gtk.Label.new( _( "On event click" ) ), False ), ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 1, 1, 1 )

        tooltip_text = _( "Copy the event text and date to the clipboard." )
        if self.is_clipboard_supported():
            tooltip_text += _( "\n\nUnsupported on Ubuntun 20.04 on Wayland." )

        radio_copy_to_clipboard = (
            self.create_radiobutton(
                None,
                _( "Copy event to clipboard" ),
                tooltip_text = tooltip_text,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.copy_to_clipboard ) )

        grid.attach( radio_copy_to_clipboard, 0, 2, 1, 1 )

        radio_internet_search = (
            self.create_radiobutton(
                radio_copy_to_clipboard,
                _( "Search event on the internet" ),
                tooltip_text =
                    _( "Search for the event in the default web browser." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = not self.copy_to_clipboard ) )

        grid.attach( radio_internet_search, 0, 3, 1, 1 )

        search_engine_entry = (
            self.create_entry(
                self.search_url,
                tooltip_text = _(
                    "The URL to search for the event.\n\n" +
                    "Use {0} in the URL to specify the\n" +
                    "position of the event text/date.\n\n" +
                    "If the URL is empty and 'search' is selected,\n" +
                    "the search will effectively be ignored.\n\n" +
                    "If the URL is empty and 'copy' is selected,\n" +
                    "the URL is reset back to factory default." ).format(
                        IndicatorOnThisDay.TAG_EVENT ),
                sensitive = not self.copy_to_clipboard ) )

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

        notify_checkbutton = (
            self.create_checkbutton(
                _( "Notify" ),
                tooltip_text = _(
                    "On startup or when saving preferences,\n" +
                    "show a notification for each of today's events." ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP,
                active = self.notify ) )

        grid.attach( notify_checkbutton, 0, 5, 1, 1 )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = (
            self.create_preferences_common_widgets() )

        grid.attach( box, 0, 6, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
#TODO Check below
            self.calendars = [ ]
            treeiter = store.get_iter_first()
            while treeiter is not None:
                row = store[ treeiter ]
                self.fortunes.append(
                    [
                        row[ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ],
                        row[ IndicatorOnThisDay.COLUMN_ENABLED ] ] )

                treeiter = store.iter_next( treeiter )

            self.lines = spinner.get_value_as_int()
            self.copy_to_clipboard = radio_copy_to_clipboard.get_active()
            self.search_url = search_engine_entry.get_text().strip()
            self.notify = notify_checkbutton.get_active()

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


#TODO This will likely go into indicatorbase...
# ...but also check that something similar has not already been done.
    def on_checkbox(
        self,
        cell_renderer_toggle,
        row,
        store,
        checkbox_column_model_id ):

        store_ = store
        if isinstance( store, Gtk.TreeModelSort ):
            store_ = store.get_model()

        store_[ row ][ checkbox_column_model_id ] = (
            not store_[ row ][ checkbox_column_model_id ] )


    def on_event_click_radio(
        self,
        source,
        radio_copy_to_clipboard,
        radio_internet_search,
        search_engine_entry ):

        search_engine_entry.set_sensitive( source == radio_internet_search )
        copy_to_clipboard_and_empty_search = (
            source == radio_copy_to_clipboard
            and
            len( search_engine_entry.get_text() ) == 0 )

        if copy_to_clipboard_and_empty_search:
            search_engine_entry.set_text(
                IndicatorOnThisDay.SEARCH_URL_DEFAULT )


    def on_calendar_remove(
        self,
        button,
        treeview ):

        model, treeiter = treeview.get_selection().get_selected()
        if treeiter is None:
            self.show_dialog_ok(
                treeview, _( "No calendar has been selected for removal." ) )

        else:
#TODO Check this...should it be treeiter or converted iter?
# I suspect this should really be converted iter.
#...or perhaps not.  What is selected is the sorted model which is displayed...
# which is correct.
# But to update the underlying data, need the underlying model and then do a convert of treeiter.
            selected_calendar = (
                model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ] )

            if selected_calendar in self.get_system_calendars():
                self.show_dialog_ok(
                    treeview,
                    _( "This is a system calendar and cannot be removed." ) )

            else:
                response = (
                    self.show_dialog_ok_cancel(
                        treeview,
                        _( "Remove the selected calendar?" ) ) )

                if response == Gtk.ResponseType.OK:
                    model.get_model().remove(
                        model.convert_iter_to_child_iter( treeiter ) )


    def on_calendar_add(
        self,
        button,
        treeview ):

        self._on_calendar_double_click( treeview, None, None )


    def on_calendar_double_click(
        self,
        treeview,
        row_number,
        treeviewcolumn,
        preferences_dialog ):

        model, treeiter = treeview.get_selection().get_selected()
        path = model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ]
        if path == self.get_system_fortune():
            self.show_dialog_ok(
                preferences_dialog,
                _( "This is a system calendar and cannot be modified." ) )

        else:
            self._on_calendar_double_click(
                treeview, row_number, treeviewcolumn )


    def _on_calendar_double_click(
        self,
        treeview,
        row_number,
        treeviewcolumn ):

        model, treeiter = treeview.get_selection().get_selected()
        adding_calendar = row_number is None

        grid = self.create_grid()

        if adding_calendar:
            title = _( "Add Calendar" )

        else:
            title = _( "Edit Calendar" )

        dialog = self.create_dialog( treeview, title, content_widget = grid )

        file_entry = (
            self.create_entry(
                ''
                if adding_calendar
                else
                model[ treeiter ][ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ],  #TODO Should model be model.get_model() or however the treeiter is supposed to be converted?
                tooltip_text = _( "The path to a calendar file." ),
                editable = False,
                make_longer = True ) )

        browse_button = (
            self.create_button(
                _( "Browse" ),
                tooltip_text = _(
                    "Choose a calendar file.\n\n" +
                    "Ensure the calendar file is\n" +
                    "valid by running through\n" +
                    "'calendar' in a terminal." ),
                    clicked_functionandarguments = (
                        self.on_browse_calendar, dialog, file_entry ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Calendar file" ) ), False ),
                    ( file_entry, True ),
                    ( browse_button, False ) ) ),
            0, 0, 1, 1 )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                path = file_entry.get_text().strip()
                if path == "":
                    self.show_dialog_ok(
                        dialog, _( "The calendar path cannot be empty." ) )

                    file_entry.grab_focus()
                    continue

                if IndicatorOnThisDay.SYSTEM_CALENDARS in path:
                    self.show_dialog_ok(
                        dialog,
                        _( "This calendar is part of your system and is "
                           +
                           "already included." ) )

                    continue

                if not adding_calendar: # This is an edit; remove the old path.
                    model.get_model().remove(
                        model.convert_iter_to_child_iter( treeiter ) ) #TODO Check if correct - also see top of function and also remove.

                model.get_model().append( [ path, True ] )

            break

        dialog.destroy()


    def on_browse_calendar(
        self,
        button,
        add_edit_dialog,
        calendar_file ):

        dialog = (
            self.create_filechooser_dialog(
                _( "Choose a calendar file" ),
                add_edit_dialog,
                calendar_file.get_text() ) )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            calendar_file.set_text( dialog.get_filename() )

        dialog.destroy()


    def get_system_calendars( self ):
        '''
        Returns a list of the system calendars; may be empty.
        '''
        calendars = [ ]
        if Path( IndicatorOnThisDay.SYSTEM_CALENDARS ).exists():
            # Ideally use Path.walk() but only available in Python 3.12.
            walk_generator = os.walk( IndicatorOnThisDay.SYSTEM_CALENDARS )
            for root, directories, filenames in walk_generator:
                for filename in fnmatch.filter( filenames, "calendar.*" ):
                    calendars.append( str( Path( root ).joinpath( filename ) ) )

            calendars.sort()

        return calendars


    def get_system_calendar_default( self ):
        '''
        Get the default system calendar.

        On success returns the history calendar.
        Otherwise, returns None.
        '''
        system_calendar_default = (
            Path( IndicatorOnThisDay.SYSTEM_CALENDARS ) / "calendar.history" )

        if not system_calendar_default.exists():
            system_calendar_default = None

        return system_calendar_default


    def load_config(
        self,
        config ):

        system_calendar_default = self.get_system_calendar_default()
        self.calendars = (
            config.get(
                IndicatorOnThisDay.CONFIG_CALENDARS,
                [ system_calendar_default, True ]
                if system_calendar_default
                else
                [ ] ) )

        if self.calendars and isinstance( self.calendars[ 0 ], str ):
            # Prior to 1.0.17, calendars were saved as a list of paths.
            # Convert to new format where each calendar path is save with a
            # corresponding boolean (whether the calendar is enabled or not).
            calendars = [ ]
            for calendar in self.calendars:
                calendars.append( [ calendar, True ] )

            self.calendars = calendars

        self.copy_to_clipboard = (
            config.get(
                IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD,
                True ) )

        self.lines = (
            config.get(
                IndicatorOnThisDay.CONFIG_LINES,
                IndicatorBase.get_menuitems_guess() ) )

        self.notify = config.get( IndicatorOnThisDay.CONFIG_NOTIFY, True )

        self.search_url = (
            config.get(
                IndicatorOnThisDay.CONFIG_SEARCH_URL,
                IndicatorOnThisDay.SEARCH_URL_DEFAULT ) )


    def save_config( self ):
        return {
            IndicatorOnThisDay.CONFIG_CALENDARS:
                self.calendars,

            IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD:
                self.copy_to_clipboard,

            IndicatorOnThisDay.CONFIG_LINES:
                self.lines,

            IndicatorOnThisDay.CONFIG_NOTIFY:
                self.notify,

            IndicatorOnThisDay.CONFIG_SEARCH_URL:
                self.search_url,
        }


IndicatorOnThisDay().main()
