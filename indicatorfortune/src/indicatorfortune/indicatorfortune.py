#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#TODO In onthisday, I had a set of user calendars and system calendars...
# but not so in fortune.
# How to ensure the system fortune is always present in the preferences?


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


import codecs

from pathlib import Path

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from indicatorbase import IndicatorBase

from fortune import Fortune


class IndicatorFortune( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used when building the wheel to create the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Fortune" )
    indicator_categories = "Categories=Utility;Amusement"

    # Fortune treeview columns; model and view have same columns.
    COLUMN_FILE_OR_DIRECTORY = 0 # Either the fortune filename or directory.
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


    def __init__( self ):
        super().__init__(
            comments = _(
                "Calls the 'fortune' program displaying the result in the " +
                "on-screen notification." ) )

        self.remove_file_from_cache( IndicatorFortune.HISTORY_FILE )


    def update(
        self,
        menu ):

#TODO Testing...uncomment the next two lines
        # self.refresh_fortune()
        # self.show_fortune()
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
                if Path( location ).is_dir():
                    locations.append( " '" + location + "/' " )

                elif Path( location ).is_file():
                    locations.append(
                        " '" + location.replace( ".dat", "" ) + "' " )

                else:
                    self.get_logging().error(
                        f"Cannot locate fortune path { location }" )

        summary = _( "WARNING. . ." )
        if locations:
            while True:
                command = "fortune" + ''.join( locations )
                fortune = self.process_get( command )
                if not fortune: # No fortune data found.
                    message = _( "Ensure enabled fortunes contain data!" )
                    break

                if len( fortune ) <= self.skip_fortune_character_count:
                    history = (
                        self.read_cache_text_without_timestamp(
                            IndicatorFortune.HISTORY_FILE ) )

                    # Remove characters/glyphs which appear as hexadecimal.
                    #    https://askubuntu.com/q/827193
                    #
                    # Examples (On Debian 12 x0007 is x0008):
                    #    Ask not for whom the <CONTROL-G> tolls.
                    #        *** System shutdown message from root
                    #    It's a very *__UN*lucky week in which to be took
                    output = ""
                    for c in fortune:
                        char_as_hex = codecs.encode( str.encode( c ), "hex" )
                        if char_as_hex == b'07' or char_as_hex == b'08':
                            continue

                        output += c

                    message = output
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

        # Scroll to the end:
        #   https://stackoverflow.com/q/5218948/2156453
        def textview_changed(
            textview,
            rectangle ):

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
        grid = self.create_grid()

        store = Gtk.ListStore( str, bool )
        for location, enabled in self.fortunes:
            store.append( [ location, enabled ] )

        # Ensure the system fortune is present in the list of fortunes,
        # not just those selected/defined by the user.
        system_fortune = self.get_system_fortune()
        system_fortune_in_user_fortunes = (
            [ system_fortune, True ] in self.fortunes
            or
            [ system_fortune, False ] in self.fortunes )

        if not system_fortune_in_user_fortunes:
            store.append( [ system_fortune, False ] )

        store = Gtk.TreeModelSort( model = store )
#TODO Need an option to pass in perhaps to the treeview create function for this?
#TODO Maybe rename the parameters in the treeview create function such that
# the stuff for letting a user sort columns is named to be clear
# and the stuff for letting the user click on a column header is also clear.
        store.set_sort_column_id( IndicatorFortune.COLUMN_FILE_OR_DIRECTORY, Gtk.SortType.ASCENDING )

#TODO Can/should this go into indicatorbase?
# (along with the on_checkbox function below)
# Used by fortune, onthisday, lunar.
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect(
            "toggled",
            self.on_checkbox,
            store,
            IndicatorFortune.COLUMN_ENABLED )

        treeview, scrolledwindow = (
            self.create_treeview_within_scrolledwindow(
                store,
                (
                    _( "Fortune File/Directory" ),
                    _( "Enabled" ) ),
                (
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ),
                    (
                        renderer_toggle,
                        "active",
                        IndicatorFortune.COLUMN_ENABLED ) ),
                alignments_columnviewids = (
                    ( 0.5, IndicatorFortune.COLUMN_ENABLED ), ),
                # sortcolumnviewids_columnmodelids = (
                #     (
                #         IndicatorFortune.COLUMN_FILE_OR_DIRECTORY,
                #         IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ),
                #     (
                #         IndicatorFortune.COLUMN_ENABLED,
                #         IndicatorFortune.COLUMN_ENABLED ) ),
                tooltip_text = _(
                    "Double click to edit a fortune.\n\n" +
                    "English language fortunes are\n" +
                    "installed by default.\n\n" +
                    "There may be other fortune\n" +
                    "packages available in your\n" +
                    "native language." ),
                rowactivatedfunctionandarguments =
                    ( self.on_fortune_double_click, dialog ) ) )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        box, add, remove = (
            self.create_buttons_in_box(
                (
                    _( "Add" ),
                    _( "Remove" ) ),
                (
                    _( "Add a new fortune location." ),
                    _( "Remove the selected fortune location." ) ),
                (
                    ( self.on_fortune_add, treeview ),
                    ( self.on_fortune_remove, treeview ) ) ) )

        grid.attach( box, 0, 1, 1, 1 )

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

        tooltip_text = ""
        if not self.is_clipboard_supported():
            tooltip_text += _( "Unsupported on Ubuntun 20.04 on Wayland." )

        active_ = (
            self.middle_mouse_click_on_icon
            ==
            IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )

        radio_middle_mouse_click_copy_last_fortune = (
            self.create_radiobutton(
                radio_middle_mouse_click_new_fortune,
                _( "Copy current fortune to clipboard" ),
                tooltip_text = tooltip_text,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = active_ ) )

        grid.attach( radio_middle_mouse_click_copy_last_fortune, 0, 5, 1, 1 )

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

        grid.attach( radio_middle_mouse_click_show_last_fortune, 0, 6, 1, 1 )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = (
            self.create_preferences_common_widgets() )

        grid.attach( box, 0, 7, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
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

            self.fortunes = [ ]
            treeiter = store.get_iter_first()
            while treeiter is not None:
                row = store[ treeiter ]
                self.fortunes.append(
                    [
                        row[ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ],
                        row[ IndicatorFortune.COLUMN_ENABLED ] ] )

                treeiter = store.iter_next( treeiter )

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
        path,
        store,
        checkbox_model_column_id ):

        path_ = path
        store_ = store
        if isinstance( store, Gtk.TreeModelSort ):  #TODO Need to handle filter?
            path_ = store_.convert_path_to_child_path( Gtk.TreePath.new_from_string( path_ ) )
            store_ = store_.get_model()

        store_[ path_ ][ checkbox_model_column_id ] = (
            not store_[ path_ ][ checkbox_model_column_id ] )


    def on_fortune_remove(
        self,
        button,
        treeview ):

        model, treeiter = treeview.get_selection().get_selected()
        if treeiter is None:
            self.show_dialog_ok(
                treeview, _( "No fortune has been selected for removal." ) )

        else:
#TODO Check this...should it be treeiter or converted iter?
# I suspect this should really be converted iter.
#...or perhaps not.  What is selected is the sorted model which is displayed...
# which is correct.
# But to update the underlying data, need the underlying model and then do a convert of treeiter.
            selected_fortune = (
                model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] )

            if selected_fortune == self.get_system_fortune():
                self.show_dialog_ok(
                    treeview,
                    _( "This is the system fortune and cannot be removed." ) )

            else:
                response = (
                    self.show_dialog_ok_cancel(
                        treeview,
                        _( "Remove the selected fortune?" ) ) )

                if response == Gtk.ResponseType.OK:
                    model.get_model().remove(
                        model.convert_iter_to_child_iter( treeiter ) )


    def on_fortune_add(
        self,
        button,
        treeview ):

        self._on_fortune_double_click( treeview, None, None )


    def on_fortune_double_click(
        self,
        treeview,
        row_number,
        treeviewcolumn,
        preferences_dialog ):

        model, treeiter = treeview.get_selection().get_selected()
        path = model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ]
        if path == self.get_system_fortune():
            self.show_dialog_ok(
                preferences_dialog,
                _( "This is the system fortune and cannot be modified." ) )

        else:
            self._on_fortune_double_click(
                treeview, row_number, treeviewcolumn )


    def _on_fortune_double_click(
        self,
        treeview,
        row_number,
        treeviewcolumn ):

        model, treeiter = treeview.get_selection().get_selected()
        adding_fortune = row_number is None

        grid = self.create_grid()

        if adding_fortune:
            title = _( "Add Fortune" )

        else:
            title = _( "Edit Fortune" )

        dialog = self.create_dialog( treeview, title, content_widget = grid )

        fortune_file_directory = (
            self.create_entry(
                ''
                if adding_fortune
                else
                model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ],  #TODO Should model be model.get_model() or however the treeiter is supposed to be converted?
                tooltip_text = _(
                    "The path to a fortune .dat file,\n" +
                    "or a directory containing\n" +
                    "fortune .dat files.\n\n" +
                    "Ensure the corresponding\n" +
                    "fortune text file(s) is present." ),
                editable = False,
                make_longer = True ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Fortune file/directory" ) ), False ),
                    ( fortune_file_directory, True ) ) ),
            0, 0, 1, 1 )

        browse_file_button = (
            self.create_button(
                _( "File" ),
                tooltip_text = _(
                    "Choose a fortune .dat file.\n\n" +
                    "Ensure the corresponding text\n" +
                    "file is present." ),
                clicked_functionandarguments = (
                    self.on_browse_fortune,
                    dialog,
                    fortune_file_directory,
                    True ) ) )

        browse_directory_button = (
            self.create_button(
                _( "Directory" ),
                tooltip_text = _(
                    "Choose a directory containing\n" +
                    "a fortune .dat file(s).\n\n" +
                    "Ensure the corresponding text\n" +
                    "file is present." ),
                clicked_functionandarguments = (
                    self.on_browse_fortune,
                    dialog,
                    fortune_file_directory,
                    False ) ) )

        grid.attach(
            self.create_box(
                (
                    ( browse_file_button, True ),
                    ( browse_directory_button, True ) ),
                halign = Gtk.Align.END,
                homogeneous = True ),
            0, 1, 1, 1 )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                path = fortune_file_directory.get_text().strip()
                if path == "":
                    self.show_dialog_ok(
                        dialog, _( "The fortune path cannot be empty." ) )

                    fortune_file_directory.grab_focus()
                    continue

                if self.get_system_fortune() in path:
                    self.show_dialog_ok(
                        dialog,
                        _(
                            "This fortune is part of your system and is " +
                            "already included." ) )

                    continue

                if not adding_fortune: # This is an edit; remove the old path.
                    model.get_model().remove(
                        model.convert_iter_to_child_iter( treeiter ) ) #TODO Check if correct - also see top of function and also remove.

                model.get_model().append( [ path, True ] )

            break

        dialog.destroy()


    def on_browse_fortune(
        self,
        file_or_directory_button,
        add_edit_dialog,
        fortune_file_directory,
        is_file ):

        if is_file:
            title = _( "Choose a fortune .dat file" )
            action = Gtk.FileChooserAction.OPEN

        else:
            title = _( "Choose a directory containing a fortune .dat file(s)" )
            action = Gtk.FileChooserAction.SELECT_FOLDER

        dialog = (
            self.create_filechooser_dialog(
                title,
                add_edit_dialog,
                fortune_file_directory.get_text(),
                action = action ) )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            fortune_file_directory.set_text( dialog.get_filename() )

        dialog.destroy()


    def get_system_fortune( self ):
        SYSTEM_FORTUNE_DEBIAN = "/usr/share/games/fortunes"
        SYSTEM_FORTUNE_FEDORA = "/usr/share/games/fortune"
        SYSTEM_FORTUNE_MANJARO = "/usr/share/fortune"
        SYSTEM_FORTUNE_OPENSUSE = "/usr/share/fortune"

        system_fortune = None
        if Path( SYSTEM_FORTUNE_DEBIAN ).exists():
            system_fortune = SYSTEM_FORTUNE_DEBIAN

        elif Path( SYSTEM_FORTUNE_FEDORA ).exists():
            system_fortune = SYSTEM_FORTUNE_FEDORA

        elif Path( SYSTEM_FORTUNE_MANJARO ).exists():
            system_fortune = SYSTEM_FORTUNE_MANJARO

        elif Path( SYSTEM_FORTUNE_OPENSUSE ).exists():
            system_fortune = SYSTEM_FORTUNE_OPENSUSE

        return system_fortune


    def load_config(
        self,
        config ):

        self.fortunes = (
            config.get(
                IndicatorFortune.CONFIG_FORTUNES,
                [ self.get_system_fortune(), True ]
                if self.get_system_fortune()
                else
                [ ] ) )

        # self.fortunes.append( [ "/home/bernard/Downloads", True ] ) #TODO Testing
        # self.fortunes.append( [ "/home/bernard/Programming", False ] ) #TODO Testing
        # self.fortunes.append( [ "/home/bernard/UnknownDirectory", True ] ) #TODO Testing
        # self.fortunes.append( [ "/home/bernard/AnotherUnknownDirectory", False ] ) #TODO Testing

        self.middle_mouse_click_on_icon = (
            config.get(
                IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON,
                IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST ) )

        self.notification_summary = (
            config.get(
                IndicatorFortune.CONFIG_NOTIFICATION_SUMMARY,
                IndicatorFortune.NOTIFICATION_SUMMARY ) )

        # Prior to 1.0.44 it was possible for the user to set an empty
        # notification summary which was amended from "" to " " prior to the
        # notification being displayed.
        #
        # Now the preferences checks for "" and sets to " " on a save.
        #
        # However it is possible a user has "" still saved in their properties
        # file, so need this check here.
        if self.notification_summary == "":
            self.notification_summary = " "

        self.refresh_interval_in_minutes = (
            config.get(
                IndicatorFortune.CONFIG_REFRESH_INTERVAL_IN_MINUTES,
                15 ) )

        # From experimentation, estimate around 45 characters per line.
        # However, to ensure word boundaries are maintained,
        # reduce to 40 characters per line (with at most 9 lines).
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
