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


# Application indicator which displays fortunes.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import codecs
import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from pathlib import Path


class IndicatorFortune( IndicatorBase ):
    # Unused within the indicator; used by build_wheel.py when building the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Fortune" )
    indicator_categories = "Categories=Utility;Amusement"

    CONFIG_FORTUNES = "fortunes"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON = "middleMouseClickOnIcon"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW = 1
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST = 2
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST = 3
    CONFIG_NOTIFICATION_SUMMARY = "notificationSummary"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SKIP_FORTUNE_CHARACTER_COUNT = "skipFortuneCharacterCount"


#TODO When selecting a fortune (via directory, not sure if also via file)
# ensure the fortune checkbox is enabled.


#TODO Manjaro default fortune is in /usr/share/fortune
#TODO openSUSE default fortune is in /usr/share/fortune
    fortune_debian = "/usr/share/games/fortunes"
    fortune_fedora = "/usr/share/games/fortune"
    fortune_manjaro_opensuse = "/usr/share/fortune"
    if Path( fortune_debian ).exists():
        DEFAULT_FORTUNE = [ fortune_debian, Gtk.STOCK_APPLY ]

    elif Path( fortune_fedora ).exists():
        DEFAULT_FORTUNE = [ fortune_fedora, Gtk.STOCK_APPLY ]

#TODO If this is an else but we are not on manjaro/opensuse, then what?
# Otherwise, if this is left as is, then what should the else be?
# Maybe just default to fortune_debian?
    elif Path( fortune_manjaro_opensuse ).exists():
        DEFAULT_FORTUNE = [ fortune_manjaro_opensuse, Gtk.STOCK_APPLY ]

    HISTORY_FILE = "fortune-history.txt"

    NOTIFICATION_SUMMARY = _( "Fortune. . ." )

    # When no fortune is enabled or no fortunes are present in the fortune .dat,
    # this flag is inserted into a dummy fortune to be shown as a notification.
    NOTIFICATION_WARNING_FLAG = "%%%%%"

    # Fortune treeview columns; there is a one to one mapping between model and view.
    COLUMN_FILE_OR_DIRECTORY = 0 # Either the fortune filename or directory.
    COLUMN_ENABLED = 1 # Icon name for the APPLY icon when the fortune is enabled; None otherwise.


    def __init__( self ):
        super().__init__(
            comments = _( "Calls the 'fortune' program displaying the result in the on-screen notification." ) )

        self.remove_file_from_cache( IndicatorFortune.HISTORY_FILE )


    def update( self, menu ):
        self.build_menu( menu )
        self.refresh_and_show_fortune()
        return int( self.refresh_interval_in_minutes ) * 60


    def build_menu( self, menu ):
        self.create_and_append_menuitem(
            menu,
            _( "New Fortune" ),
            activate_functionandarguments = (
                lambda menuitem: self.refresh_and_show_fortune(), ),
            is_secondary_activate_target = (
                self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW ) )

        self.create_and_append_menuitem(
            menu,
            _( "Copy Last Fortune" ),
            activate_functionandarguments = (
                lambda menuitem: self.copy_to_selection( self.fortune ), ),
            is_secondary_activate_target = (
                self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST ) )

        self.create_and_append_menuitem(
            menu,
            _( "Show Last Fortune" ),
            activate_functionandarguments = (
                lambda menuitem: self.show_fortune(), ),
            is_secondary_activate_target = (
                self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST ) )

        menu.append( Gtk.SeparatorMenuItem() )

        self.create_and_append_menuitem(
            menu,
            _( "History" ),
            activate_functionandarguments = (
                lambda menuitem: self.show_history(), ) )


    def show_history( self ):

        # Scroll to the end...strange way of doing so!
        # https://stackoverflow.com/questions/5218948/how-to-auto-scroll-a-gtk-scrolledwindow
        def textview_changed( textview, rectangle ):
            adjustment = textview.get_parent().get_vadjustment()
            adjustment.set_value( adjustment.get_upper() - adjustment.get_page_size() )


        self.set_menu_sensitivity( False )

        textview = \
            self.create_textview(
                text = self.read_cache_text_without_timestamp( IndicatorFortune.HISTORY_FILE ),
                editable = False )

        textview.connect( "size-allocate", textview_changed )

        box = \
            self.create_box(
                ( ( self.create_scrolledwindow( textview ), True ), ),
                spacing = 0 )

        dialog = \
            self.create_dialog(
                None,
                _( "Fortune History for Session" ),
                content_widget = box,
                buttons_responsetypes = ( Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE ),
                default_size = ( IndicatorBase.DIALOG_DEFAULT_WIDTH, IndicatorBase.DIALOG_DEFAULT_HEIGHT ) )

        dialog.show_all()
        dialog.run()
        dialog.destroy()

        self.set_menu_sensitivity( True )


    def refresh_fortune( self ):
        locations = " "
        no_enabled_fortunes = True
        for location, enabled in self.fortunes:
            if enabled:
                no_enabled_fortunes = False
                if Path( location ).is_dir():
                    locations += "'" + location.rstrip( "/" ) + "/" + "' " # Remove all trailing slashes, then add one in as 'fortune' needs it!

                elif Path( location ).is_file():
                    locations += "'" + location.replace( ".dat", "" ) + "' " # 'fortune' doesn't want the extension.

        if no_enabled_fortunes:
            self.fortune = \
                IndicatorFortune.NOTIFICATION_WARNING_FLAG + \
                _( "No enabled fortunes!" )

        else:
            if locations == " ": # Despite one or more fortunes enabled, none seem to be valid paths/files...
                self.fortune = \
                    IndicatorFortune.NOTIFICATION_WARNING_FLAG + \
                    _( "No enabled fortunes have a valid location!" )

            else:
                while True:
                    self.fortune = self.process_get( "fortune" + locations )
                    if self.fortune is None: # Occurs when no fortune data is found...
                        self.fortune = \
                            IndicatorFortune.NOTIFICATION_WARNING_FLAG + \
                            _( "Ensure enabled fortunes contain fortune data!" )

                        break

                    elif len( self.fortune ) <= self.skip_fortune_character_count: # If the fortune is within the character limit keep it...
                        history = self.read_cache_text_without_timestamp( IndicatorFortune.HISTORY_FILE )
                        if history is None:
                            history = ""

                        # Remove characters/glyphs which appear as hexadecimal.  Refer to:
                        #     https://askubuntu.com/questions/827193/detect-missing-glyphs-in-text
                        #
                        # Examples:
                        #     Ask not for whom the <CONTROL-G> tolls.
                        #         *** System shutdown message from root ***
                        #     It's a very *__UN*lucky week in which to be took dead.   <--- On Debian 12 this is x0008
                        output = ""
                        for c in self.fortune:
                            if codecs.encode( str.encode( c ), "hex" ) == b'07' or \
                               codecs.encode( str.encode( c ), "hex" ) == b'08':
                                continue

                            output += c

                        self.fortune = output
                        self.write_cache_text_without_timestamp(
                            history + self.fortune + "\n\n",
                            IndicatorFortune.HISTORY_FILE )

                        break


    def show_fortune( self ):
        if self.fortune.startswith( IndicatorFortune.NOTIFICATION_WARNING_FLAG ):
            notification_summary = _( "WARNING. . ." )

        else:
            notification_summary = self.notification_summary
            if notification_summary == "":
                notification_summary = " "

        self.show_notification(
            notification_summary,
            self.fortune.strip( IndicatorFortune.NOTIFICATION_WARNING_FLAG ) )


    def refresh_and_show_fortune( self ):
        self.refresh_fortune()
        self.show_fortune()


    def on_preferences( self, dialog ):
        notebook = Gtk.Notebook()

        # Fortune file.
        grid = self.create_grid()

        store = Gtk.ListStore( str, str ) # Path to fortune; tick icon (Gtk.STOCK_APPLY) or error icon (Gtk.STOCK_DIALOG_ERROR) or None.
        for location, enabled in self.fortunes:
            if Path( location ).is_file() or Path( location ).is_dir():
                store.append( [ location, Gtk.STOCK_APPLY if enabled else None ] )

            else:
                store.append( [ location, Gtk.STOCK_DIALOG_ERROR ] )

        treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                Gtk.TreeModelSort( model = store ),
                ( _( "Fortune File/Directory" ), _( "Enabled" ) ),
                (
                    ( Gtk.CellRendererText(), "text", IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ),
                    ( Gtk.CellRendererPixbuf(), "stock_id", IndicatorFortune.COLUMN_ENABLED ) ),
                alignments_columnviewids = ( ( 0.5, IndicatorFortune.COLUMN_ENABLED ), ),
                sortcolumnviewids_columnmodelids = (
                    ( IndicatorFortune.COLUMN_FILE_OR_DIRECTORY, IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ),
                    ( IndicatorFortune.COLUMN_ENABLED, IndicatorFortune.COLUMN_ENABLED ) ),
                tooltip_text = _(
                    "Double click to edit a fortune.\n\n" +
                    "English language fortunes are\n" +
                    "installed by default.\n\n" +
                    "There may be other fortune\n" +
                    "packages available in your\n" +
                    "native language." ),
                rowactivatedfunctionandarguments = ( self.on_fortune_double_click, ) )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        box = \
            self.create_buttons_in_box(
                (
                    _( "Add" ),
                    _( "Remove" ),
                    _( "Reset" ) ),
                (
                    _( "Add a new fortune location." ),
                    _( "Remove the selected fortune location." ),
                    _( "Reset to factory default." ) ),
                (
                    ( self.on_fortune_add, treeview ),
                    ( self.on_fortune_remove, treeview ),
                    ( self.on_fortune_reset, treeview ) ) )

        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Fortunes" ) ) )

        # General.
        grid = self.create_grid()

        spinner_refresh_interval = \
            self.create_spinbutton(
                self.refresh_interval_in_minutes,
                1,
                60 * 24,
                tooltip_text = _( "How often a fortune is displayed." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Refresh interval (minutes)" ) ), False ),
                    ( spinner_refresh_interval, False ) ) ),
            0, 0, 1, 1 )

        notification_summary = \
            self.create_entry(
                self.notification_summary,
                tooltip_text = _( "The summary text for the notification." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Notification summary" ) ), False ),
                    ( notification_summary, True ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 1, 1, 1 )

        spinner_character_count = \
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
                    "'fortune' program." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Message character limit" ) ), False ),
                    ( spinner_character_count, False ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 2, 1, 1 )

        grid.attach(
            self.create_box(
                ( ( Gtk.Label.new( _( "Middle mouse click of the icon" ) ), False ), ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 3, 1, 1 )

        radio_middle_mouse_click_new_fortune = \
            self.create_radiobutton(
                None,
                _( "Show a new fortune" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = \
                    self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )

        grid.attach( radio_middle_mouse_click_new_fortune, 0, 4, 1, 1 )

        radio_middle_mouse_click_copy_last_fortune = \
            self.create_radiobutton(
                radio_middle_mouse_click_new_fortune,
                _( "Copy current fortune to clipboard" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = \
                    self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )

        grid.attach( radio_middle_mouse_click_copy_last_fortune, 0, 5, 1, 1 )

        radio_middle_mouse_click_show_last_fortune = \
            self.create_radiobutton(
                radio_middle_mouse_click_new_fortune,
                _( "Show current fortune" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = \
                    self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )

        grid.attach( radio_middle_mouse_click_show_last_fortune, 0, 6, 1, 1 )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = \
            self.create_preferences_common_widgets()

        grid.attach( box, 0, 7, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            if radio_middle_mouse_click_new_fortune.get_active():
                self.middle_mouse_click_on_icon = IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW

            elif radio_middle_mouse_click_copy_last_fortune.get_active():
                self.middle_mouse_click_on_icon = IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST

            else:
                self.middle_mouse_click_on_icon = IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST

            self.refresh_interval_in_minutes = spinner_refresh_interval.get_value_as_int()
            self.skip_fortune_character_count = spinner_character_count.get_value_as_int()
            self.notification_summary = notification_summary.get_text()

            self.fortunes = [ ]
            treeiter = store.get_iter_first()
            while treeiter != None:
                if store[ treeiter ][ IndicatorFortune.COLUMN_ENABLED ] == Gtk.STOCK_APPLY:
                    self.fortunes.append( [ store[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ], True ] )

                else:
                    self.fortunes.append( [ store[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ], False ] )

                treeiter = store.iter_next( treeiter )

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


    def on_fortune_reset( self, button, treeview ):
        if self.show_dialog_ok_cancel( treeview, _( "Reset fortunes to factory default?" ) ) == Gtk.ResponseType.OK:
            liststore = treeview.get_model().get_model()
            liststore.clear()
            liststore.append( IndicatorFortune.DEFAULT_FORTUNE ) # Cannot set True into the model, so need to do this silly thing to get "True" into the model!


    def on_fortune_remove( self, button, treeview ):
        model, treeiter = treeview.get_selection().get_selected()
        if treeiter is None:
            self.show_dialog_ok( treeview, _( "No fortune has been selected for removal." ) )

        else:
            selected_fortune_path = \
                model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ]

            default_fortune_path = \
                IndicatorFortune.DEFAULT_FORTUNE[ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ]

            if selected_fortune_path == default_fortune_path:
                self.show_dialog_ok(
                    treeview,
                    _( "This is the default fortune and cannot be deleted." ),
                    message_type = Gtk.MessageType.INFO )

            else:
                response = \
                    self.show_dialog_ok_cancel(
                        treeview,
                        _( "Remove the selected fortune?" ) )

                if response == Gtk.ResponseType.OK:
                    model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) )


    def on_fortune_add( self, button, treeview ):
        self.on_fortune_double_click( treeview, None, None )


    def on_fortune_double_click( self, treeview, row_number, treeviewcolumn ):
        model, treeiter = treeview.get_selection().get_selected()

        grid = self.create_grid()

        title = _( "Add Fortune" )
        if row_number:
            title = _( "Edit Fortune" )

        dialog = self.create_dialog( treeview, title, content_widget = grid )

        fortune_file_directory = \
            self.create_entry(
                model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] if row_number else "",
                tooltip_text = _(
                    "The path to a fortune .dat file,\n" +
                    "or a directory containing\n" +
                    "fortune .dat files.\n\n" +
                    "Ensure the corresponding\n" +
                    "fortune text file(s) is present." ),
                editable = False,
                make_longer = True )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Fortune file/directory" ) ), False ),
                    ( fortune_file_directory, True ) ) ),
            0, 0, 1, 1 )

        is_system_fortune = False # This is an add.
        if row_number: # This is an edit.
            is_system_fortune = \
                model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] == IndicatorFortune.DEFAULT_FORTUNE

        browse_file_button = \
            self.create_button(
                _( "File" ),
                tooltip_text = _(
                    "This fortune is part of your\n" +
                    "system and cannot be modified." )
                    if is_system_fortune else _(
                    "Choose a fortune .dat file.\n\n" +
                    "Ensure the corresponding text\n" +
                    "file is present." ),
                sensitive = not is_system_fortune,
                clicked_functionandarguments = ( self.on_browse_fortune, dialog, fortune_file_directory, True ) )

        browse_directory_button = \
            self.create_button(
                _( "Directory" ),
                tooltip_text = _(
                    "This fortune is part of your\n" +
                    "system and cannot be modified." )
                    if is_system_fortune else _(
                    "Choose a directory containing\n" +
                    "a fortune .dat file(s).\n\n" +
                    "Ensure the corresponding text\n" +
                    "file is present." ),
                sensitive = not is_system_fortune,
                clicked_functionandarguments = ( self.on_browse_fortune, dialog, fortune_file_directory, False ) )

        grid.attach(
            self.create_box(
                (
                    ( browse_file_button, True ),
                    ( browse_directory_button, True ) ),
                halign = Gtk.Align.END,
                homogeneous = True ),
            0, 1, 1, 1 )

        enabled_checkbox = \
            self.create_checkbutton(
                _( "Enabled" ),
                tooltip_text = _(
                    "Ensure the fortune file/directory\n" +
                    "works by running through 'fortune'\n" +
                    "in a terminal." ),
                active = \
                    True
                    if row_number is None else \
                    model[ treeiter ][ IndicatorFortune.COLUMN_ENABLED ] == Gtk.STOCK_APPLY )

        grid.attach( enabled_checkbox, 0, 2, 1, 1 )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if fortune_file_directory.get_text().strip() == "": # Will occur if the user does a browse: cancels the browse and hits okay.
                    self.show_dialog_ok( dialog, _( "The fortune path cannot be empty." ) )
                    fortune_file_directory.grab_focus()
                    continue

                if row_number: # This is an edit; remove the old value.
                    model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) )

                model.get_model().append( [
                    fortune_file_directory.get_text().strip(),
                    Gtk.STOCK_APPLY if enabled_checkbox.get_active() else None ] )

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

        dialog = \
            self.create_filechooser_dialog(
                title,
                add_edit_dialog,
                fortune_file_directory.get_text(),
                action = action )

        while( True ):
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if dialog.get_filename().startswith( IndicatorFortune.DEFAULT_FORTUNE[ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] ):
                    self.show_dialog_ok(
                        dialog,
                        _( "The fortune is part of your system and is already included." ),
                        message_type = Gtk.MessageType.INFO )

                else:
                    fortune_file_directory.set_text( dialog.get_filename() )
                    break

            else:
                break

        dialog.destroy()


    def load_config( self, config ):
        self.fortunes = \
            config.get(
                IndicatorFortune.CONFIG_FORTUNES,
                [ IndicatorFortune.DEFAULT_FORTUNE ] )

        self.middle_mouse_click_on_icon = \
            config.get(
                IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON,
                IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )

        self.notification_summary = \
            config.get(
                IndicatorFortune.CONFIG_NOTIFICATION_SUMMARY,
                IndicatorFortune.NOTIFICATION_SUMMARY )

        self.refresh_interval_in_minutes = \
            config.get(
                IndicatorFortune.CONFIG_REFRESH_INTERVAL_IN_MINUTES,
                15 )

        self.skip_fortune_character_count = \
            config.get(
                IndicatorFortune.CONFIG_SKIP_FORTUNE_CHARACTER_COUNT,
                360 )   # From experimentation, about 45 characters per line,
                        # but with word boundaries maintained,
                        # say 40 characters per line (with at most 9 lines).


    def save_config( self ):
        return {
            IndicatorFortune.CONFIG_FORTUNES : self.fortunes,
            IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON : self.middle_mouse_click_on_icon,
            IndicatorFortune.CONFIG_NOTIFICATION_SUMMARY : self.notification_summary,
            IndicatorFortune.CONFIG_REFRESH_INTERVAL_IN_MINUTES : self.refresh_interval_in_minutes,
            IndicatorFortune.CONFIG_SKIP_FORTUNE_CHARACTER_COUNT : self.skip_fortune_character_count
        }


IndicatorFortune().main()
