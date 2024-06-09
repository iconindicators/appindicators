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

gi.require_version( "Gdk", "3.0" )
from gi.repository import Gdk

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

try:
    gi.require_version( "Notify", "0.7" )
except ValueError:
    gi.require_version( "Notify", "0.8" )
from gi.repository import Notify

import os
from pathlib import Path


class IndicatorFortune( IndicatorBase ):

    CONFIG_FORTUNES = "fortunes"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON = "middleMouseClickOnIcon"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW = 1
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST = 2
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST = 3
    CONFIG_NOTIFICATION_SUMMARY = "notificationSummary"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SKIP_FORTUNE_CHARACTER_COUNT = "skipFortuneCharacterCount"

    fortune_debian = "/usr/share/games/fortunes"
    if Path( fortune_debian ).exists():
        DEFAULT_FORTUNE = [ fortune_debian, Gtk.STOCK_APPLY ]

    else:
        fortune_fedora = "/usr/share/games/fortune"
        DEFAULT_FORTUNE = [ fortune_fedora, Gtk.STOCK_APPLY ]

    HISTORY_FILE = "fortune-history.txt"

    NOTIFICATION_SUMMARY = _( "Fortune. . ." )

    # If present at the start of the current fortune,
    # the notification summary should be emitted as a warning,
    # rather than a regular fortune.
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
            activate_functionandarguments = ( lambda menuitem: self.refresh_and_show_fortune(), ),
            is_secondary_activate_target =
                ( self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW ) )

        self.create_and_append_menuitem(
            menu,
            _( "Copy Last Fortune" ),
            activate_functionandarguments =
                ( lambda menuitem: Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( self.fortune, -1 ), ),
            is_secondary_activate_target =
                ( self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST ) )

        self.create_and_append_menuitem(
            menu,
            _( "Show Last Fortune" ),
            activate_functionandarguments = ( lambda menuitem: self.show_fortune(), ),
            is_secondary_activate_target =
                ( self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST ) )

        menu.append( Gtk.SeparatorMenuItem() )

        self.create_and_append_menuitem(
            menu,
            _( "History" ),
            activate_functionandarguments = ( lambda menuitem: self.show_history(), ) )


    def show_history( self ):
        textview = Gtk.TextView()
        textview.set_editable( False )
        textview.get_buffer().set_text( self.read_cache_text_without_timestamp( IndicatorFortune.HISTORY_FILE ) )

        #TODO Remove below
        # scrolledWindow = Gtk.ScrolledWindow()
        # scrolledWindow.set_hexpand( True )
        # scrolledWindow.set_vexpand( True )
        # scrolledWindow.add( textView )

        # Scroll to the end...strange way of doing so!
        # https://stackoverflow.com/questions/5218948/how-to-auto-scroll-a-gtk-scrolledwindow
        def textview_changed( textview, rectangle ):
            adjustment = textview.get_parent().get_vadjustment()
            adjustment.set_value( adjustment.get_upper() - adjustment.get_page_size() )

        textview.connect( "size-allocate", textview_changed )

        box = Gtk.Box()
        box.pack_start(
            self.create_scrolledwindow( textview ),
            True,
            True,
            0 )

        self.create_dialog_external( None, _( "Fortune History for Session" ), box, True )


    def refresh_fortune( self ):
        locations = " "
        for location, enabled in self.fortunes:
            if enabled:
                if os.path.isdir( location ):
                    locations += "'" + location.rstrip( "/" ) + "/" + "' " # Remove all trailing slashes, then add one in as 'fortune' needs it!

                elif os.path.isfile( location ):
                    locations += "'" + location.replace( ".dat", "" ) + "' " # 'fortune' doesn't want the extension.

        if locations == " ": # Despite one or more fortunes enabled, none seem to be valid paths/files...
            self.fortune = IndicatorFortune.NOTIFICATION_WARNING_FLAG + _( "No enabled fortunes have a valid location!" )

        else:
            while True:
                self.fortune = self.process_get( "fortune" + locations )
                if self.fortune is None: # Occurs when no fortune data is found...
                    self.fortune = IndicatorFortune.NOTIFICATION_WARNING_FLAG + _( "Ensure enabled fortunes contain fortune data!" )
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

        Notify.Notification.new(
            notification_summary,
            self.fortune.strip( IndicatorFortune.NOTIFICATION_WARNING_FLAG ),
            self.get_icon_name() ).show()


    def refresh_and_show_fortune( self ):
        self.refresh_fortune()
        self.show_fortune()


    def on_preferences( self, dialog ):
        notebook = Gtk.Notebook()

        # Fortune file.
        grid = self.create_grid()

        store = Gtk.ListStore( str, str ) # Path to fortune; tick icon (Gtk.STOCK_APPLY) or error icon (Gtk.STOCK_DIALOG_ERROR) or None.
        for location, enabled in self.fortunes:
            if os.path.isfile( location ) or os.path.isdir( location ):
                store.append( [ location, Gtk.STOCK_APPLY if enabled else None ] )

            else:
                store.append( [ location, Gtk.STOCK_DIALOG_ERROR ] )

#TODO Delete
        # storeSort = Gtk.TreeModelSort( model = store )
        # storeSort.set_sort_column_id( 0, Gtk.SortType.ASCENDING )  #TODO Should the 0 be IndicatorFortune.COLUMN_FILE_OR_DIRECTORY??? 

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
                    "Double click to edit a fortune.\n\n" + \
                    "English language fortunes are\n" + \
                    "installed by default.\n\n" + \
                    "There may be other fortune\n" + \
                    "packages available in your\n" + \
                    "native language." ),
                rowactivatedfunctionandarguments = ( self.on_fortune_double_click, ) )

        # tree = Gtk.TreeView.new_with_model( storeSort )
        # tree.expand_all()
        # tree.set_hexpand( True ) #TODO Can these be added to the scrolledWindow instead?
        # tree.set_vexpand( True )

        # treeViewColumn = \
        #     Gtk.TreeViewColumn(
        #         _( "Fortune File/Directory" ),
        #         Gtk.CellRendererText(),
        #         text = IndicatorFortune.COLUMN_FILE_OR_DIRECTORY )

        # treeViewColumn.set_sort_column_id( 0 )
        # treeViewColumn.set_expand( True )
        # tree.append_column( treeViewColumn )

        # treeViewColumn = Gtk.TreeViewColumn( _( "Enabled" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorFortune.COLUMN_ENABLED )
        # treeViewColumn.set_sort_column_id( 1 )
        # treeViewColumn.set_expand( True )
        # treeViewColumn.set_alignment( 0.5 )
        # tree.append_column( treeViewColumn )

        # tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        # tree.connect( "row-activated", self.on_fortune_double_click )
        # tree.set_tooltip_text( _(
        #     "Double click to edit a fortune.\n\n" + \
        #     "English language fortunes are\n" + \
        #     "installed by default.\n\n" + \
        #     "There may be other fortune\n" + \
        #     "packages available in your\n" + \
        #     "native language." ) )

        # scrolledWindow = Gtk.ScrolledWindow()
        # scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        # scrolledWindow.add( tree )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True ) #TODO What does homogeneous mean?

        # addButton = Gtk.Button.new_with_label( _( "Add" ) )
        # addButton.set_tooltip_text( _( "Add a new fortune location." ) )
        # addButton.connect( "clicked", self.on_fortune_add, tree )
        # box.pack_start( addButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Add" ),
                tooltip_text = _( "Add a new fortune location." ),
                clicked_function_and_arguments = ( self.on_fortune_add, treeview ) ),
            True,
            True,
            0 )

        # removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        # removeButton.set_tooltip_text( _( "Remove the selected fortune location." ) )
        # removeButton.connect( "clicked", self.on_fortune_remove, tree )
        # box.pack_start( removeButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Remove" ),
                tooltip_text = _( "Remove the selected fortune location." ),
                clicked_function_and_arguments = ( self.on_fortune_remove, treeview ) ),
            True,
            True,
            0 )

        # resetButton = Gtk.Button.new_with_label( _( "Reset" ) )
        # resetButton.set_tooltip_text( _( "Reset to factory default." ) )
        # resetButton.connect( "clicked", self.on_fortune_reset, tree )
        # box.pack_start( resetButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Reset" ),
                tooltip_text = _( "Reset to factory default." ),
                clicked_function_and_arguments = ( self.on_fortune_reset, treeview ) ),
            True,
            True,
            0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Fortunes" ) ) )


        # General.
        grid = self.create_grid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Refresh interval (minutes)" ) ), False, False, 0 )

        spinner_refresh_interval = \
            self.create_spinbutton(
                self.refresh_interval_in_minutes,
                1,
                60 * 24,
                tooltip_text = _( "How often a fortune is displayed." ) )

        box.pack_start( spinner_refresh_interval, False, False, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Notification summary" ) ), False, False, 0 )

        notification_summary = Gtk.Entry()
        notification_summary.set_text( self.notification_summary )
        notification_summary.set_tooltip_text( _( "The summary text for the notification." ) )
        box.pack_start( notification_summary, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Message character limit" ) ), False, False, 0 )

        spinner_character_count = \
            self.create_spinbutton(
                self.skip_fortune_character_count,
                1,
                1000,
                tooltip_text = _(
                    "If the fortune exceeds the limit,\n" +                                  
                    "a new fortune is created.\n\n" + \
                    "Do not set too low (below 50) as\n" + \
                    "many fortunes may be dropped,\n" + \
                    "resulting in excessive calls to the\n" + \
                    "'fortune' program." ) )

        box.pack_start( spinner_character_count, False, False, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        label = Gtk.Label.new( _( "Middle mouse click of the icon" ) )
        label.set_tooltip_text( _( "Not supported on all desktops." ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 3, 1, 1 )

        # radio_middle_mouse_click_new_fortune = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show a new fortune" ) )
        # radio_middle_mouse_click_new_fortune.set_active(
        #     self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )
        #
        # radio_middle_mouse_click_new_fortune.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( radio_middle_mouse_click_new_fortune, 0, 4, 1, 1 )
#TODO Check above.
        radio_middle_mouse_click_new_fortune = \
            self.create_radiobutton(
                None,
                _( "Show a new fortune" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )

        grid.attach( radio_middle_mouse_click_new_fortune, 0, 4, 1, 1 )

        # radio_middle_mouse_click_copy_last_fortune = \
        #     Gtk.RadioButton.new_with_label_from_widget(
        #         radio_middle_mouse_click_new_fortune,
        #         _( "Copy current fortune to clipboard" ) )
        #
        # radio_middle_mouse_click_copy_last_fortune.set_active(
        #     self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )
        #
        # radio_middle_mouse_click_copy_last_fortune.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( radio_middle_mouse_click_copy_last_fortune, 0, 5, 1, 1 )
#TODO Check above.
        radio_middle_mouse_click_copy_last_fortune = \
            self.create_radiobutton(
                radio_middle_mouse_click_new_fortune,
                _( "Copy current fortune to clipboard" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )

        grid.attach( radio_middle_mouse_click_copy_last_fortune, 0, 5, 1, 1 )

        # radio_middle_mouse_click_show_last_fortune = \
        #     Gtk.RadioButton.new_with_label_from_widget(
        #         radio_middle_mouse_click_new_fortune,
        #         _( "Show current fortune" ) )
        #
        # radio_middle_mouse_click_show_last_fortune.set_active(
        #     self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )
        #
        # radio_middle_mouse_click_show_last_fortune.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( radio_middle_mouse_click_show_last_fortune, 0, 6, 1, 1 )
#TODO Check above.
        radio_middle_mouse_click_show_last_fortune = \
            self.create_radiobutton(
                radio_middle_mouse_click_new_fortune,
                _( "Show current fortune" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.middle_mouse_click_on_icon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )

        grid.attach( radio_middle_mouse_click_show_last_fortune, 0, 6, 1, 1 )

        autostart_checkbox, delay_spinner, box = self.create_autostart_checkbox_and_delay_spinner()
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

            self.set_autostart_and_delay( autostart_checkbox.get_active(), delay_spinner.get_value_as_int() )

        return response_type


    def on_fortune_reset( self, button, treeview ):
        if self.showOKCancel( treeview, _( "Reset fortunes to factory default?" ) ) == Gtk.ResponseType.OK:
            listStore = treeview.get_model().get_model()
            listStore.clear()
            listStore.append( IndicatorFortune.DEFAULT_FORTUNE  ) # Cannot set True into the model, so need to do this silly thing to get "True" into the model!


    def on_fortune_remove( self, button, treeview ):
        model, treeiter = treeview.get_selection().get_selected()
        if treeiter is None:
            self.show_message( treeview, _( "No fortune has been selected for removal." ) ) #TODO If we switch to using BROWSE over SINGLE for all treeviews, can remove this type of check....except if there is no data present!  Need testing!

        elif model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] == IndicatorFortune.DEFAULT_FORTUNE:
            self.show_message( treeview, _( "This is the default fortune and cannot be deleted." ), Gtk.MessageType.INFO )

        elif self.showOKCancel( treeview, _( "Remove the selected fortune?" ) ) == Gtk.ResponseType.OK:
            model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) )


    def on_fortune_add( self, button, treeview ):
        self.on_fortune_double_click( treeview, None, None )


    def on_fortune_double_click( self, treeview, row_number, treeviewcolumn ):
        model, treeiter = treeview.get_selection().get_selected()

        grid = self.create_grid()

        title = _( "Add Fortune" )
        if row_number:
            title = _( "Edit Fortune" )

        dialog = self.create_dialog( treeview, title, grid )

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True )

        box.pack_start( Gtk.Label.new( _( "Fortune file/directory" ) ), False, False, 0 )

        fortune_file_directory = Gtk.Entry()
        fortune_file_directory.set_editable( False )

        if row_number: # This is an edit.
            fortune_file_directory.set_text( model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] )
            fortune_file_directory.set_width_chars( len( fortune_file_directory.get_text() ) * 5 / 4 ) # Sometimes the length is shorter than set due to packing, so make it longer.

        fortune_file_directory.set_tooltip_text( _(
            "The path to a fortune .dat file,\n" + \
            "or a directory containing\n" + \
            "fortune .dat files.\n\n" + \
            "Ensure the corresponding\n" + \
            "fortune text file(s) is present." ) )

        box.pack_start( fortune_file_directory, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )

        is_system_fortune = False # This is an add.
        if row_number: # This is an edit.
            is_system_fortune = \
                model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] == IndicatorFortune.DEFAULT_FORTUNE

        # browse_file_button = Gtk.Button.new_with_label( _( "File" ) )
        # browse_file_button.set_sensitive( not is_system_fortune )
        # if is_system_fortune:
        #     browse_file_button.set_tooltip_text( _(
        #         "This fortune is part of your\n" + \
        #         "system and cannot be modified." ) )
        #
        # else:
        #     browse_file_button.set_tooltip_text( _(
        #         "Choose a fortune .dat file.\n\n" + \
        #         "Ensure the corresponding text\n" + \
        #         "file is present." ) )
        #
        # box.pack_start( browse_file_button, True, True, 0 )
#TODO Ensure this was converted correctly.
        browse_file_button = \
            self.create_button(
                _( "File" ),
                tooltip_text = _(
                    "This fortune is part of your\n" + \
                    "system and cannot be modified." ) \
                    if is_system_fortune else _(
                    "Choose a fortune .dat file.\n\n" + \
                    "Ensure the corresponding text\n" + \
                    "file is present." ),
                sensitive = not is_system_fortune,
                clicked_functionandarguments = ( self.on_browse_fortune, dialog, fortune_file_directory, True ) )

        box.pack_start( browse_file_button, True, True, 0 )

        # browse_directory_button = Gtk.Button.new_with_label( _( "Directory" ) )
        # browse_directory_button.set_sensitive( not is_system_fortune )
        # if is_system_fortune:
        #     browse_directory_button.set_tooltip_text( _(
        #         "This fortune is part of your\n" + \
        #         "system and cannot be modified." ) )
        #
        # else:
        #     browse_directory_button.set_tooltip_text( _(
        #         "Choose a directory containing\n" + \
        #         "a fortune .dat file(s).\n\n" + \
        #         "Ensure the corresponding text\n" + \
        #         "file is present." ) )
#TODO Ensure this was converted correctly.
        browse_directory_button = \
            self.create_button(
                _( "Directory" ),
                tooltip_text = _( 
                    "This fortune is part of your\n" + \
                    "system and cannot be modified." ) \
                    if is_system_fortune else _(
                    "Choose a directory containing\n" + \
                    "a fortune .dat file(s).\n\n" + \
                    "Ensure the corresponding text\n" + \
                    "file is present." ),
                sensitive = not is_system_fortune,
                clicked_functionandarguments = ( self.on_browse_fortune, dialog, fortune_file_directory, False ) )

        box.pack_start( browse_directory_button, True, True, 0 )

        box.set_halign( Gtk.Align.END )

        grid.attach( box, 0, 1, 1, 1 )

        enabled_checkbox = \
            self.create_checkbutton(
                _( "Enabled" ),
                tooltip_text = _(
                    "Ensure the fortune file/directory\n" + \
                    "works by running through 'fortune'\n" + \
                    "in a terminal." ) )
#TODO Ensure above converted correctly.
        # enabled_checkbox = Gtk.CheckButton.new_with_label( _( "Enabled" ) )True
        # enabled_checkbox.set_tooltip_text( _(
        #     "Ensure the fortune file/directory\n" + \
        #     "works by running through 'fortune'\n" + \
        #     "in a terminal." ) )
        #
        # enabled_checkbox.set_active( True ) # This is an add.
        if row_number: # This is an edit.
            enabled_checkbox.set_active( model[ treeiter ][ IndicatorFortune.COLUMN_ENABLED ] == Gtk.STOCK_APPLY )

        grid.attach( enabled_checkbox, 0, 2, 1, 1 )

#TODO Moved to top to see if buttons can have the connect in their definitions rather than external.
        # title = _( "Add Fortune" )
        # if row_number:
        #     title = _( "Edit Fortune" )
        #
        # dialog = self.create_dialog( treeview, title, grid ) #TODO Can this be moved up the top so the buttons are created last and can put the clicked stuff into the new function?

        # browse_file_button.connect( "clicked", self.on_browse_fortune, dialog, fortune_file_directory, True )
        # browse_directory_button.connect( "clicked", self.on_browse_fortune, dialog, fortune_file_directory, False )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if fortune_file_directory.get_text().strip() == "": # Will occur if the user does a browse, cancels the browse and hits okay.
                    self.show_message( dialog, _( "The fortune path cannot be empty." ) )
                    fortune_file_directory.grab_focus()
                    continue

                if row_number:
                    model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) ) # This is an edit...remove the old value.

                model.get_model().append(
                    [ fortune_file_directory.get_text().strip(),
                     Gtk.STOCK_APPLY if enabled_checkbox.get_active() else None ] )

            break

        dialog.destroy()


    def on_browse_fortune( self, file_or_directory_button, add_edit_dialog, fortune_file_directory, is_file ):
        if is_file:
            title = _( "Choose a fortune .dat file" )
            action = Gtk.FileChooserAction.OPEN

        else:
            title = _( "Choose a directory containing a fortune .dat file(s)" )
            action = Gtk.FileChooserAction.SELECT_FOLDER

        dialog = \
            Gtk.FileChooserDialog(
                title = title,
                parent = add_edit_dialog,
                action = action )

        dialog.add_buttons = (
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK )

        dialog.set_transient_for( add_edit_dialog )
        dialog.set_filename( fortune_file_directory.get_text() )
        while( True ):
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if dialog.get_filename().startswith( IndicatorFortune.DEFAULT_FORTUNE[ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] ):
                    self.show_message(
                        dialog,
                        _( "The fortune is part of your system and is already included." ),
                        Gtk.MessageType.INFO )

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
