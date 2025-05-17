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


''' Application indicator which displays fortunes. '''


#TODO Test with/without clipboard supported 
# AND
# with/without preference set to copy last.


import fnmatch
import os

from pathlib import Path

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from packaging.version import Version

from .indicatorbase import IndicatorBase

from .fortune import Fortune


class IndicatorFortune( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used in the About dialog and the .desktop file.
    INDICATOR_NAME_HUMAN_READABLE = _( "Indicator Fortune" )

    # Used in the .desktop file.
    INDICATOR_CATEGORIES = "Categories=Utility;Amusement"

    # Fortune treeview columns; model and view have same columns.
    COLUMN_FORTUNE_FILE = 0 # Path to fortune .dat file.
    COLUMN_ENABLED = 1 # Boolean.

    CONFIG_FORTUNES = "fortunes"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON = "middleMouseClickOnIcon"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW = 1
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST = 2
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST = 3
    CONFIG_NOTIFICATION_SUMMARY = "notificationSummary"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SKIP_FORTUNE_CHARACTER_COUNT = "skipFortuneCharacterCount"

    HISTORY_FILE = "fortune-history.txt"

    NOTIFICATION_SUMMARY = _( "Fortune. . ." )

    SYSTEM_FORTUNE_DEBIAN = "/usr/share/games/fortunes"
    SYSTEM_FORTUNE_FEDORA = "/usr/share/games/fortune"
    SYSTEM_FORTUNE_MANJARO = "/usr/share/fortune"
    SYSTEM_FORTUNE_OPENSUSE = "/usr/share/fortune"


    def __init__( self ):
        super().__init__(
            IndicatorFortune.INDICATOR_NAME_HUMAN_READABLE,
            comments = _( "Calls the 'fortune' program displaying the result\nin the on-screen notification." ) )

        self.remove_file_from_cache( IndicatorFortune.HISTORY_FILE )


    def update(
        self,
        menu ):

        self.refresh_fortune()
        self.show_fortune()
        self.build_menu( menu )
        return int( self.refresh_interval_in_minutes ) * 60


    def build_menu(
        self,
        menu ):

        self.create_and_append_menuitem(
            menu,
            _( "New Fortune" ),
            activate_functionandarguments = (
                lambda menuitem: self.refresh_and_show_fortune(), ),
            is_secondary_activate_target = (
                self.middle_mouse_click_on_icon
                ==
                IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW ) )

        if self.is_clipboard_supported():
            self.create_and_append_menuitem(
                menu,
                _( "Copy Last Fortune" ),
                activate_functionandarguments = (
                    lambda menuitem:
                        self.copy_to_selection( self.fortune.get_message() ), ),
                is_secondary_activate_target = (
                    self.middle_mouse_click_on_icon
                    ==
                    IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST ) )

        self.create_and_append_menuitem(
            menu,
            _( "Show Last Fortune" ),
            activate_functionandarguments = (
                lambda menuitem: self.show_fortune(), ),
            is_secondary_activate_target = (
                self.middle_mouse_click_on_icon
                ==
                IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST ) )

        menu.append( Gtk.SeparatorMenuItem() )

        self.create_and_append_menuitem(
            menu,
            _( "History" ),
            activate_functionandarguments = (
                lambda menuitem: self.show_history(), ) )


    def refresh_fortune( self ):
        locations = [ ]
        at_least_one_fortune_is_enabled = False
        for location, enabled in self.fortunes:
            if enabled:
                at_least_one_fortune_is_enabled = True
                if Path( location ).is_file():
                    locations.append(
                        " '" + location.replace( ".dat", "" ) + "' " )

                else:
                    self.get_logging().error(
                        f"Cannot locate fortune path { location }" )

        summary = _( "WARNING. . ." )
        if locations:
            command = "fortune" + ''.join( locations )
            while True:
                fortune_ = self.process_get( command )
                if not fortune_: # No fortune data found.
                    message = _( "Ensure enabled fortunes contain data!" )
                    break

                if len( fortune_ ) <= self.skip_fortune_character_count:
                    history = (
                        self.read_cache_text_without_timestamp(
                            IndicatorFortune.HISTORY_FILE ) )

                    message = fortune_
                    summary = self.notification_summary

                    self.write_cache_text_without_timestamp(
                        history + message + "\n\n",
                        IndicatorFortune.HISTORY_FILE )

                    break

        elif at_least_one_fortune_is_enabled:
            message = _( "No enabled fortunes have a valid location!" )

        else:
            message = _( "No fortunes are enabled!" )

        self.fortune = Fortune( message, summary )


    def show_fortune( self ):
        self.show_notification(
            self.fortune.get_summary(), self.fortune.get_message() )


    def refresh_and_show_fortune( self ):
        self.refresh_fortune()
        self.show_fortune()


    def show_history( self ):

        def textview_changed(
            textview,
            rectangle ):
            '''
            Scrolls to the end:
                https://stackoverflow.com/q/5218948/2156453
            '''

            adjustment = textview.get_parent().get_vadjustment()
            adjustment.set_value(
                adjustment.get_upper() - adjustment.get_page_size() )


        self.set_menu_sensitivity( False )

        textview = (
            self.create_textview(
                text =
                    self.read_cache_text_without_timestamp(
                        IndicatorFortune.HISTORY_FILE ),
                editable = False ) )

        textview.connect( "size-allocate", textview_changed )

        box = (
            self.create_box(
                ( ( self.create_scrolledwindow( textview ), True ), ),
                spacing = 0 ) )

        dialog = (
            self.create_dialog(
                None,
                _( "Fortune History for Session" ),
                content_widget = box,
                buttons_responsetypes =
                    ( Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE ),
                default_size =
                    (
                        IndicatorBase.DIALOG_DEFAULT_WIDTH,
                        IndicatorBase.DIALOG_DEFAULT_HEIGHT ) ) )

        dialog.show_all()
        dialog.run()
        dialog.destroy()

        self.set_menu_sensitivity( True )


    def on_preferences(
        self,
        dialog ):

        notebook = Gtk.Notebook()
        notebook.set_margin_bottom( IndicatorBase.INDENT_WIDGET_TOP )

        # Fortunes.
        file_filter = Gtk.FileFilter()
        file_filter.set_name( "Fortune files" )
        file_filter.add_pattern( "*.dat" )

        grid, store = (
            self._create_fortune_or_calendar_preferences_panel(
                dialog,
                self.fortunes,
                self.get_system_fortunes(),
                IndicatorFortune.COLUMN_FORTUNE_FILE,
                IndicatorFortune.COLUMN_ENABLED,
                _( "Fortune" ),
                _( "Double click to edit a fortune." ),
                _( "Choose a fortune .dat file" ),
                _( "This fortune already exists!" ),
                _( "This is a system fortune and cannot be modified." ),
                _( "Add a new fortune." ),
                _( "Remove the selected fortune." ),
                _( "This is a system fortune and cannot be removed." ),
                _( "Remove the selected fortune?" ),
                file_filter ) )

        notebook.append_page( grid, Gtk.Label.new( _( "Fortunes" ) ) )

        # General.
        grid = self.create_grid()

        spinner_refresh_interval = (
            self.create_spinbutton(
                self.refresh_interval_in_minutes,
                1,
                60 * 24,
                tooltip_text = _( "How often a fortune is displayed." ) ) )

        label = Gtk.Label.new( _( "Refresh interval (minutes)" ) )
        grid.attach(
            self.create_box(
                (
                    ( label, False ),
                    ( spinner_refresh_interval, False ) ) ),
            0, 0, 1, 1 )

        notification_summary = (
            self.create_entry(
                self.notification_summary,
                tooltip_text = _( "The summary text for the notification." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Notification summary" ) ), False ),
                    ( notification_summary, True ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 1, 1, 1 )

        spinner_character_count = (
            self.create_spinbutton(
                self.skip_fortune_character_count,
                1,
                1000,
                tooltip_text = _(
                    "If the fortune exceeds the limit,\n" +
                    "a new fortune is created.\n\n" +
                    "Do not set too low (below 50) as\n" +
                    "many fortunes may be dropped,\n" +
                    "resulting in excessive calls to the\n" +
                    "'fortune' program." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Message character limit" ) ), False ),
                    ( spinner_character_count, False ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 2, 1, 1 )

        label = Gtk.Label.new( _( "Middle mouse click of the icon" ) )

        grid.attach(
            self.create_box(
                ( ( label, False ), ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 3, 1, 1 )

        active_ = (
            self.middle_mouse_click_on_icon
            ==
            IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )

        radio_middle_mouse_click_new_fortune = (
            self.create_radiobutton(
                None,
                _( "Show a new fortune" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = active_ ) )

        grid.attach( radio_middle_mouse_click_new_fortune, 0, 4, 1, 1 )

        row = 5
        active_ = (
            self.middle_mouse_click_on_icon
            ==
            IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )

        radio_middle_mouse_click_copy_last_fortune = (
            self.create_radiobutton(
                radio_middle_mouse_click_new_fortune,
                _( "Copy current fortune to clipboard" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = active_ ) )

        if self.is_clipboard_supported():
            grid.attach( radio_middle_mouse_click_copy_last_fortune, 0, row, 1, 1 )
            row += 1

        active_ = (
            self.middle_mouse_click_on_icon
            ==
            IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )

        radio_middle_mouse_click_show_last_fortune = (
            self.create_radiobutton(
                radio_middle_mouse_click_new_fortune,
                _( "Show current fortune" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = active_ ) )

        grid.attach( radio_middle_mouse_click_show_last_fortune, 0, row, 1, 1 )
        row += 1

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = (
            self.create_preferences_common_widgets() )

        grid.attach( box, 0, row, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.fortunes = [ ]
            iter_ = store.get_iter_first()
            while iter_:
                row = store[ iter_ ]
                self.fortunes.append(
                    [
                        row[ IndicatorFortune.COLUMN_FORTUNE_FILE ],
                        row[ IndicatorFortune.COLUMN_ENABLED ] ] )

                iter_ = store.iter_next( iter_ )

            if radio_middle_mouse_click_new_fortune.get_active():
                self.middle_mouse_click_on_icon = (
                    IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )

            elif radio_middle_mouse_click_copy_last_fortune.get_active():
                self.middle_mouse_click_on_icon = (
                    IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )

            else:
                self.middle_mouse_click_on_icon = (
                    IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )

            self.refresh_interval_in_minutes = (
                spinner_refresh_interval.get_value_as_int() )

            self.skip_fortune_character_count = (
                spinner_character_count.get_value_as_int() )

            self.notification_summary = notification_summary.get_text()
            if self.notification_summary == "":
                self.notification_summary = " "

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


    def _get_system_fortune_path( self ):
        system_fortune_path = None
        if Path( IndicatorFortune.SYSTEM_FORTUNE_DEBIAN ).exists():
            system_fortune_path = IndicatorFortune.SYSTEM_FORTUNE_DEBIAN

        elif Path( IndicatorFortune.SYSTEM_FORTUNE_FEDORA ).exists():
            system_fortune_path = IndicatorFortune.SYSTEM_FORTUNE_FEDORA

        elif Path( IndicatorFortune.SYSTEM_FORTUNE_MANJARO ).exists():
            system_fortune_path = IndicatorFortune.SYSTEM_FORTUNE_MANJARO

        elif Path( IndicatorFortune.SYSTEM_FORTUNE_OPENSUSE ).exists():
            system_fortune_path = IndicatorFortune.SYSTEM_FORTUNE_OPENSUSE

        return system_fortune_path


    def get_system_fortunes( self ):
        '''
        Returns a list of the system fortunes; may be empty.
        '''
        fortunes = [ ]
        system_fortune_path = self._get_system_fortune_path()
        if system_fortune_path:
            # Ideally use Path.walk() but only available in Python 3.12.
            walk_generator = os.walk( system_fortune_path )
            for root, directories, filenames in walk_generator:
                for filename in fnmatch.filter( filenames, "*.dat" ):
                    fortunes.append( str( Path( root ).joinpath( filename ) ) )

            fortunes.sort()

        return fortunes


    def get_system_fortune_default( self ):
        '''
        Get the default system fortune.

        On success returns the full text path to fortunes.dat.
        Otherwise, returns None.
        '''
        system_fortune_path = self._get_system_fortune_path()
        if system_fortune_path:
            system_fortune_default = (
                str( Path( system_fortune_path ) / "fortunes.dat" ) )

        else:
            system_fortune_default = None

        return system_fortune_default


    def _upgrade_1_0_44( self ):
        if self.fortunes:
            # Prior to 1.0.44, fortunes were specified as a directory of .dat
            # files, or as a single .dat file.
            #
            # Fortunes are now specified only as a single .dat file.
            #
            # Any fortune specified as a directory must be converted to
            # individual their respective .dat files within.
            fortunes = [ ]
            for fortune in self.fortunes:
                path = Path( fortune[ 0 ] )
                if path.is_dir():
                    walk_generator = os.walk( path )
                    for root, directories, filenames in walk_generator:
                        for filename in fnmatch.filter( filenames, "*.dat" ):
                            fortunes.append( [
                                str( Path( root ).joinpath( filename ) ),
                                fortune[ 1 ] ] )

                else:
                    fortunes.append( fortune )

            self.fortunes = fortunes

        if self.notification_summary == "":
            # Prior to 1.0.44 it was possible for the user to set an empty
            # notification summary.
            #
            # On some platforms a notification of "" causes an error and so
            # a notification of "" was amended " " prior to display.
            #
            # Now the preferences checks for "" and sets to " " on a save.
            #
            # If a notification in the user properties file is set to "",
            # correct for this here.
            self.notification_summary = " "

        self.request_save_config( 1 )


    def load_config(
        self,
        config ):

        self.fortunes = config.get( IndicatorFortune.CONFIG_FORTUNES, [ ] )

        self.notification_summary = (
            config.get(
                IndicatorFortune.CONFIG_NOTIFICATION_SUMMARY,
                IndicatorFortune.NOTIFICATION_SUMMARY ) )

        version_from_config = Version( self.get_version_from_config( config ) )
        if version_from_config < Version( "1.0.44" ):
            self._upgrade_1_0_44()

        if len( self.fortunes ) == 0:
            system_fortune_default = self.get_system_fortune_default()
            if system_fortune_default:
                self.fortunes = [ [ system_fortune_default, True ] ]

            else:
                self.fortunes = [ ]

        self.middle_mouse_click_on_icon = (
            config.get(
                IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON,
                IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW ) )

        mouse_middle_click_copy_last = (
            self.middle_mouse_click_on_icon
            ==
            IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )

        if mouse_middle_click_copy_last and not self.is_clipboard_supported():
            self.middle_mouse_click_on_icon = (
                IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )

        self.refresh_interval_in_minutes = (
            config.get(
                IndicatorFortune.CONFIG_REFRESH_INTERVAL_IN_MINUTES,
                15 ) )

        # From experimentation, estimate around 45 characters per line.
        # To ensure word boundaries are maintained, reduce to 40 characters,
        # with at most 9 lines.
        self.skip_fortune_character_count = (
            config.get(
                IndicatorFortune.CONFIG_SKIP_FORTUNE_CHARACTER_COUNT,
                360 ) )


    def save_config( self ):
        return {
            IndicatorFortune.CONFIG_FORTUNES: self.fortunes,

            IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON:
                self.middle_mouse_click_on_icon,

            IndicatorFortune.CONFIG_NOTIFICATION_SUMMARY:
                self.notification_summary,

            IndicatorFortune.CONFIG_REFRESH_INTERVAL_IN_MINUTES:
                self.refresh_interval_in_minutes,

            IndicatorFortune.CONFIG_SKIP_FORTUNE_CHARACTER_COUNT:
                self.skip_fortune_character_count
        }


IndicatorFortune().main()
