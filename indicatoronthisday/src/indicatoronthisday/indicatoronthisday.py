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

from .indicatorbase import IndicatorBase

from .event import Event


class IndicatorOnThisDay( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used in the About dialog and the .desktop file.
    INDICATOR_NAME_HUMAN_READABLE = _( "Indicator On This Day" )

    # Used in the .desktop file.
    INDICATOR_CATEGORIES = "Categories=Utility;Amusement"

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
            IndicatorOnThisDay.INDICATOR_NAME_HUMAN_READABLE,
            comments = _( "Calls the 'calendar' program and\ndisplays events in the menu." ) )


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
                    # Don't add the menu item for the new date and
                    # don't add a subsequent event.
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
                            self.copy_to_clipboard_or_primary(
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
                _( "No calendars are enabled!" ) )

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
        for line in self.process_run( command )[ 0 ].splitlines():
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
        notebook.set_margin_bottom( self.INDENT_WIDGET_TOP )

        # Calendars.
        grid, store = (
            self._create_fortune_or_calendar_preferences_panel(
                dialog,
                self.calendars,
                self.get_system_calendars(),
                IndicatorOnThisDay.COLUMN_CALENDAR_FILE,
                IndicatorOnThisDay.COLUMN_ENABLED,
                _( "Calendar" ),
                _( "Double click to edit a calendar." ),
                _( "Choose a calendar file" ),
                _( "This calendar already exists!" ),
                _( "This is a system calendar and cannot be modified." ),
                _( "Add a new calendar." ),
                _( "Remove the selected calendar." ),
                _( "This is a system calendar and cannot be modified." ),
                _( "Remove the selected calendar?" ),
                None ) )

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

        if self.is_clipboard_supported():
            sensitive = not self.copy_to_clipboard

        else:
            sensitive = True

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
                sensitive = sensitive ) )

        row = 1

        if self.is_clipboard_supported():
            grid.attach(
                self.create_box(
                    ( ( Gtk.Label.new( _( "On event click" ) ), False ), ),
                    margin_top = self.INDENT_WIDGET_TOP ),
                0, row, 1, 1 )

            row += 1

            radio_copy_to_clipboard = (
                self.create_radiobutton(
                    None,
                    _( "Copy event to clipboard" ),
                    margin_left = self.INDENT_WIDGET_LEFT,
                    active = self.copy_to_clipboard ) )

            grid.attach( radio_copy_to_clipboard, 0, row, 1, 1 )
            row += 1

            radio_internet_search = (
                self.create_radiobutton(
                    radio_copy_to_clipboard,
                    _( "Search using URL" ),
                    margin_left = self.INDENT_WIDGET_LEFT,
                    active = not self.copy_to_clipboard ) )

            grid.attach( radio_internet_search, 0, row, 1, 1 )
            row += 1

            grid.attach( search_engine_entry, 0, row, 1, 1 )
            search_engine_entry.set_hexpand( True )
            search_engine_entry.set_margin_left(
                self.INDENT_WIDGET_LEFT * 2 ),

            row += 1

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

        else:
            label = (
                Gtk.Label.new( _( "On event click, search using URL" ) ) )

            grid.attach(
                self.create_box(
                    ( ( label, False ), ),
                    margin_top = self.INDENT_WIDGET_TOP ),
                0, row, 1, 1 )

            row += 1

            grid.attach( search_engine_entry, 0, row, 1, 1 )
            search_engine_entry.set_hexpand( True )
            search_engine_entry.set_margin_left(
                self.INDENT_WIDGET_LEFT )

            row += 1

        notify_checkbutton = (
            self.create_checkbutton(
                _( "Notify" ),
                tooltip_text = _(
                    "On startup or when saving preferences,\n" +
                    "show a notification for each of today's events." ),
                margin_top = self.INDENT_WIDGET_TOP,
                active = self.notify ) )

        grid.attach( notify_checkbutton, 0, row, 1, 1 )
        row += 1

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = (
            self.create_preferences_common_widgets() )

        grid.attach( box, 0, row, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.calendars = [ ]
            iter_ = store.get_iter_first()
            while iter_:
                row = store[ iter_ ]
                self.calendars.append(
                    [
                        row[ IndicatorOnThisDay.COLUMN_CALENDAR_FILE ],
                        row[ IndicatorOnThisDay.COLUMN_ENABLED ] ] )

                iter_ = store.iter_next( iter_ )

            self.lines = spinner.get_value_as_int()
            self.search_url = search_engine_entry.get_text().strip()
            self.notify = notify_checkbutton.get_active()

            if self.is_clipboard_supported():
                self.copy_to_clipboard = radio_copy_to_clipboard.get_active()

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


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

        On success returns the full text path to the history calendar.
        Otherwise, returns None.
        '''
        system_calendar_default = (
            Path( IndicatorOnThisDay.SYSTEM_CALENDARS ) / "calendar.history" )

        if system_calendar_default.exists():
            system_calendar_default = str( system_calendar_default )

        else:
            system_calendar_default = None

        return system_calendar_default


    def _upgrade_1_0_17( self ):
        # Prior to 1.0.17, calendars were saved as a list of paths.
        # Convert to new format where each calendar path is stored with a
        # corresponding boolean (whether the calendar is enabled or not).
        if self.calendars:
            calendars = [ ]
            for calendar in self.calendars:
                calendars.append( [ calendar, True ] )

            self.calendars = calendars

        self.request_save_config( 1 )


    def load_config(
        self,
        config ):

        system_calendar_default = self.get_system_calendar_default()
        self.calendars = (
            config.get(
                IndicatorOnThisDay.CONFIG_CALENDARS,
                [ [ system_calendar_default, True ] ] if system_calendar_default
                else [ ] ) )

        version_0_0_0 = self.versiontuple( "0.0.0" )
        version_1_0_17 = self.versiontuple( "1.0.17" )
        version_from_config = (
            self.versiontuple( self.get_version_from_config( config ) ) )

        if version_0_0_0 < version_from_config < version_1_0_17:
            self._upgrade_1_0_17()

        self.copy_to_clipboard = (
            config.get(
                IndicatorOnThisDay.CONFIG_COPY_TO_CLIPBOARD,
                True ) )

        if self.copy_to_clipboard and not self.is_clipboard_supported():
            self.copy_to_clipboard = False

        self.lines = (
            config.get(
                IndicatorOnThisDay.CONFIG_LINES,
                self.get_menuitems_guess() ) )

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
