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
Application indicator to run a terminal command/script from the indicator menu.
'''


#TODO When a script is selected, change tooltip of Copy button to copy script.
# When a group is selected, change tooltip of Copy button to copy group and scripts within.


#TODO 
# When add/edit a script, see fortune/onthisday...maybe there is a simpler
# way to select the script (similarly for remove).


import concurrent.futures
import datetime
import math

from threading import Thread

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

gi.require_version( "Pango", "1.0" )
from gi.repository import Pango

#from .indicatorbase import IndicatorBase

#from .script import Background, NonBackground, Info
from indicatorbase import IndicatorBase #TODO Restore to above.

from script import Background, NonBackground, Info


class IndicatorScriptRunner( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used when building the wheel to create the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Script Runner" )
    indicator_categories = "Categories=Utility"

    CONFIG_HIDE_GROUPS = "hideGroups"
    CONFIG_INDICATOR_TEXT = "indicatorText"
    CONFIG_INDICATOR_TEXT_SEPARATOR = "indicatorTextSeparator"
    CONFIG_SCRIPTS_BACKGROUND = "scriptsBackground"
    CONFIG_SCRIPTS_NON_BACKGROUND = "scriptsNonBackground"
    CONFIG_SEND_COMMAND_TO_LOG = "sendCommandToLog"
    CONFIG_SHOW_SCRIPTS_IN_SUBMENUS = "showScriptsInSubmenus"

    COMMAND_NOTIFY_TAG_SCRIPT_NAME = "[SCRIPT_NAME]"
    COMMAND_NOTIFY_TAG_SCRIPT_RESULT = "[SCRIPT_RESULT]"

    COLUMN_MODEL_GROUP_HIDDEN = 0
    COLUMN_MODEL_GROUP = 1
    COLUMN_MODEL_NAME = 2
    COLUMN_MODEL_COMMAND_HIDDEN = 3
    COLUMN_MODEL_SOUND = 4
    COLUMN_MODEL_NOTIFICATION = 5
    COLUMN_MODEL_BACKGROUND = 6
    COLUMN_MODEL_TERMINAL = 7
    COLUMN_MODEL_DEFAULT_HIDDEN = 8
    COLUMN_MODEL_INTERVAL = 9
    COLUMN_MODEL_FORCE_UPDATE = 10

    COLUMN_VIEW_SCRIPTS_ALL_GROUP = 0 # Group name or None.
    COLUMN_VIEW_SCRIPTS_ALL_NAME = 1 # Script name.
    COLUMN_VIEW_SCRIPTS_ALL_SOUND = 2 # Tick symbol or None.
    COLUMN_VIEW_SCRIPTS_ALL_NOTIFICATION = 3 # Tick symbol or None.
    COLUMN_VIEW_SCRIPTS_ALL_BACKGROUND = 4 # Tick symbol or None.
    COLUMN_VIEW_SCRIPTS_ALL_TERMINAL = 5 # Tick symbol or None.
    COLUMN_VIEW_SCRIPTS_ALL_INTERVAL = 6 # Numeric amount as a string.
    COLUMN_VIEW_SCRIPTS_ALL_FORCE_UPDATE = 7 # Tick symbol or None.

    COLUMN_VIEW_SCRIPTS_BACKGROUND_GROUP = 0 # Group name or None.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_NAME = 1 # Script name.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_SOUND = 2 # Tick symbol or None.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_NOTIFICATION = 3 # Tick symbol or None.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_INTERVAL = 4 # Numeric amount as a string.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_FORCE_UPDATE = 5 # Tick symbol or None.

    # Indices for the scripts saved in JSON.
    JSON_GROUP = 0
    JSON_NAME = 1
    JSON_COMMAND = 2
    JSON_PLAY_SOUND = 3
    JSON_SHOW_NOTIFICATION = 4

    # Background scripts
    JSON_INTERVAL_IN_MINUTES = 5
    JSON_FORCE_UPDATE = 6

    # Non-background scripts
    JSON_TERMINAL_OPEN = 5
    JSON_DEFAULT = 6


    def __init__( self ):
        super().__init__(
            comments = _( "Runs a terminal command or script;\noptionally display results in the icon label." ) )

        command_notify_common = (
            "notify-send -i " +
            self.get_icon_name() +
            " \"" + IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" " )

        self.command_notify_background = (
            command_notify_common +
            "\"" + IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_RESULT + "\"" )

        self.command_notify_nonbackground = (
            command_notify_common + "\"" + _( "...has completed." ) + "\"" )


    def update(
        self,
        menu ):

        today = datetime.datetime.now()
        self.update_menu( menu )
        # self.update_background_scripts( today )#TODO Uncomment
        self.set_label_or_tooltip( self.process_tags() )

        # Calculate next update; default to well into the future.
        next_update = today + datetime.timedelta( hours = 100 )
        for script in self.scripts:
            key = self._create_key( script.get_group(), script.get_name() )

#TODO Check this...
            is_background_and_update_due_and_in_indicator_text = (
                isinstance( script, Background )
                and
                self.background_script_next_update_time[ key ] < next_update
                and
                self.is_background_script_in_indicator_text( script ) )

            if is_background_and_update_due_and_in_indicator_text:
                next_update = self.background_script_next_update_time[ key ]

        next_update_in_seconds = (
            int( math.ceil( ( next_update - today ).total_seconds() ) ) )

        return 60 if next_update_in_seconds < 60 else next_update_in_seconds


    def update_menu(
        self,
        menu ):

        if self.show_scripts_in_submenus:
            scripts_by_group = self.get_scripts_by_group( self.scripts, True, False )
            for group in sorted( scripts_by_group.keys(), key = str.lower ):
                submenu = Gtk.Menu()
                self.create_and_append_menuitem( menu, group ).set_submenu( submenu )
                self.add_scripts_to_menu(
                    scripts_by_group[ group ], submenu, indent = ( 1, 0 ) )

        else:
            if self.hide_groups:
                for script in sorted( self.scripts, key = lambda script: script.get_name().lower() ):
                    if isinstance( script, NonBackground ):
                        self.add_scripts_to_menu( [ script ], menu, indent = ( 0, 0 ) )

            else:
                scripts_by_group = self.get_scripts_by_group( self.scripts, True, False )
                for group in sorted( scripts_by_group.keys(), key = str.lower ):
                    self.create_and_append_menuitem( menu, group )
                    self.add_scripts_to_menu(
                        scripts_by_group[ group ], menu, indent = ( 1, 1 ) )


    def add_scripts_to_menu(
        self,
        scripts,
        menu,
        indent ):

        scripts.sort( key = lambda script: script.get_name().lower() )
        for script in scripts:
            menuitem = (
                self.create_and_append_menuitem(
                    menu,
                    script.get_name(),
                    activate_functionandarguments = (
                        lambda menuitem, script = script: # script = script for lambda late binding.
                            self.on_script_menuitem( script ), ),
                    indent = indent ) )

            if script.get_default():
                self.set_secondary_activate_target( menuitem )


    def on_script_menuitem(
        self,
        script ):

        terminal, terminal_execution_flag = self.get_terminal_and_execution_flag()
        if terminal is None:
            message = _(
                "Cannot run script as no terminal and/or terminal execution " +
                "flag found; please install gnome-terminal." )

            self.get_logging().error( message )
            self.show_notification( "Cannot run script", message )

        elif self.is_qterminal_and_broken( terminal ):
            # As a result of
            #   https://github.com/lxqt/qterminal/issues/335
            # the default terminal in Lubuntu (qterminal) fails to parse arguments.
            # Although a fix has been made, it is unlikely the repository will be updated any time soon.
            # So the quickest/easiest workaround is to install gnome-terminal.
            message = _(
                "Cannot run script as qterminal incorrectly parses arguments;" +
                " install gnome-terminal instead." )

            self.get_logging().error( message )
            self.show_notification( "Cannot run script", message )

        else:
            command = terminal + " " + terminal_execution_flag + " ${SHELL} -c '"
            command += script.get_command()

            if script.get_show_notification():
                notification = (
                    self.command_notify_nonbackground.replace(
                        IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME,
                        script.get_name() ) )

                command += "; " + notification

            if script.get_play_sound():
                command += "; " + IndicatorBase.get_play_sound_complete_command()

            if script.get_terminal_open():
                command += "; cd $HOME; ${SHELL}"

            command += "'"

            if self.send_command_to_log:
                self.get_logging().debug(
                    script.get_group() + " | " + script.get_name() + ": " + command )

            Thread( target = self.process_call, args = ( command, ) ).start()


    def update_background_scripts(
        self,
        now ):

        background_scripts_to_execute = [ ]
        for script in self.scripts:
#TODO Check logic of this loop and all if tests.
            script_is_background_and_in_indicator_text = (
                isinstance( script, Background )
                and
                self.is_background_script_in_indicator_text( script ) )

            key = self._create_key( script.get_group(), script.get_name() )
            if script_is_background_and_in_indicator_text:
                update_required = (
                    self.background_script_next_update_time[ key ] < now )

                force_update_and_has_results = (
                    script.get_force_update()
                    and
                    self.background_script_results[ key ] )

                if update_required or force_update_and_has_results:
                    background_scripts_to_execute.append( script )

        # Based on example from
        #    https://docs.python.org/3.6/library/concurrent.futures.html
        with concurrent.futures.ThreadPoolExecutor( max_workers = 5 ) as executor:
            future_to_script = {
                executor.submit(
                    self._update_background_script,
                    script,
                    now ): script for script in background_scripts_to_execute }

            for future in concurrent.futures.as_completed( future_to_script ):
                script = future_to_script[ future ]
                key = future.result()
                command_result = self.background_script_results[ key ]

                if script.get_play_sound() and command_result:
                    self.process_call(
                        IndicatorBase.get_play_sound_complete_command() )

                if script.get_show_notification() and command_result:
                    notification_command = self.command_notify_background
                    notification_command = (
                        notification_command.replace(
                            IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME,
                            script.get_name().replace( '-', '\\-' ) ) )

                    notification_command = (
                        notification_command.replace(
                            IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_RESULT,
                            command_result.replace( '-', '\\-' ) ) )

                    self.process_call( notification_command )


    def _update_background_script(
        self,
        script,
        now ):

        if self.send_command_to_log:
            self.get_logging().debug(
                script.get_group() + " | " + script.get_name() + ": " + script.get_command() )

        # When calling a user script, always log any errors from non-zero
        # return codes.
        command_result = (
            self.process_get(
                script.get_command(),
                log_non_zero_error_code = True ) )

        key = self._create_key( script.get_group(), script.get_name() )
        self.background_script_results[ key ] = command_result
        self.background_script_next_update_time[ key ] = (
            now + datetime.timedelta( minutes = script.get_interval_in_minutes() ) )

        return key


    def process_tags( self ):
        indicator_text_processed = self.indicator_text
        for script in self.scripts:
            key = self._create_key( script.get_group(), script.get_name() )
            if isinstance( script, Background ) and "[" + key + "]" in indicator_text_processed:
                command_result = self.background_script_results[ key ]
                if command_result is None:
                    # Background script failed so leave the tag in place for
                    # the user to see.
                    indicator_text_processed = (
                        indicator_text_processed.replace(
                            "[" + key + "]",
                            "[" + key + "]" + self.indicator_text_separator ) )

                elif command_result:
                    # Non-empty result so replace tag and tack on a separator.
                    indicator_text_processed = (
                        indicator_text_processed.replace(
                            "[" + key + "]",
                            command_result + self.indicator_text_separator ) )

                else:
                    # No result, so remove tag but no need for separator.
                    indicator_text_processed = (
                        indicator_text_processed.replace(
                            "[" + key + "]",
                            command_result ) )

        return indicator_text_processed[ 0 : - len( self.indicator_text_separator ) ] # Trim last separator.


    def on_preferences(
        self,
        dialog ):

        notebook = Gtk.Notebook()
        notebook.set_margin_bottom( IndicatorBase.INDENT_WIDGET_TOP )

        # Scripts.
        grid = self.create_grid()

        # Define these widgets here so that events can be connected.
        indicator_text_entry = (
            self.create_entry(
                self.indicator_text,
                tooltip_text = _(
                    "The text shown next to the indicator icon,\n" +
                    "or tooltip where applicable.\n\n" +
                    "A background script must:\n" +
                    "\tAlways return non-empty text; or\n" +
                    "\tReturn non-empty text on success\n" +
                    "\tand empty text otherwise.\n\n" +
                    "Only background scripts added to the\n" +
                    "icon text will be run.\n\n" +
                    "Not supported on all desktops." ) ) )

        command_text_view = (
            self.create_textview(
                tooltip_text = _(
                    "The terminal script/command, along with any arguments." ),
                editable = False ) )

        box, add, copy_, remove = (
            self.create_buttons_in_box(
                (
                    _( "Add" ),
                    _( "Copy" ),
                    _( "Remove" ) ),
                (
                    _( "Add a new script." ),
                    _( "Duplicate the selected script." ),
                    _( "Remove the selected script." ) ),
                (
                    None,
                    None,
                    None ) ) )

        # Rows describe either a
        #   group, showing only the group name,
        # or a
        #   script, showing the script name and the script's attributes,
        #   but not the enclosing group.
        #
        # Each row contains columns hidden from view, used programmatically:
        #   group, script command and script default.
        treestore = Gtk.TreeStore( str, str, str, str, str, str, str, str, str, str, str )
        scripts_by_group = self.get_scripts_by_group( self.scripts )
        for group in scripts_by_group.keys():
            row = [ group, group, None, None, None, None, None, None, None, None, None ]
            parent = treestore.append( None, row )
            for script in scripts_by_group[ group ]:
                row = [
                    group,
                    None,
                    script.get_name(),
                    script.get_command(),
                    IndicatorBase.TICK_SYMBOL if script.get_play_sound()
                    else None,
                    IndicatorBase.TICK_SYMBOL if script.get_show_notification()
                    else None,
                    IndicatorBase.TICK_SYMBOL if isinstance( script, Background )
                    else None,
                    '—' if isinstance( script, Background )
                    else (
                        IndicatorBase.TICK_SYMBOL if script.get_terminal_open()
                        else None
                    ),
                    str( False ) if isinstance( script, Background )
                    else str( script.get_default() ),
                    str( script.get_interval_in_minutes() )
                    if isinstance( script, Background )
                    else '—',
                    (
                        IndicatorBase.TICK_SYMBOL if script.get_force_update()
                        else None )
                    if isinstance( script, Background ) else '—' ]

                treestore.append( parent, row )

        dump = self.dump_treestore( treestore ) #TODO Testing
        print( dump )
        print()

        renderer_column_name_text = Gtk.CellRendererText()

        scripts_treeview, scripts_scrolledwindow = (
            self.create_treeview_within_scrolledwindow(
                treestore,
                (
                    _( "Group" ),
                    _( "Name" ),
                    _( "Sound" ),
                    _( "Notification" ),
                    _( "Background" ),
                    _( "Terminal" ),
                    _( "Interval" ),
                    _( "Force Update" ) ),
                (
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_GROUP ),
                    (
                        renderer_column_name_text,
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_NAME ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_SOUND ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_NOTIFICATION ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_TERMINAL ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_INTERVAL ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_FORCE_UPDATE ) ),
                alignments_columnviewids = (
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_SOUND ),
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_NOTIFICATION ),
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_BACKGROUND ),
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_TERMINAL ),
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_INTERVAL ),
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_FORCE_UPDATE ) ),
                celldatafunctionandarguments_renderers_columnviewids = (
                    (
                        ( self._column_name_renderer, ),
                        renderer_column_name_text,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_NAME ), ),
                default_sort_func = self._script_sort,
                tooltip_text = _(
                    "Double-click to edit a script.\n\n" +
                    "If an attribute does not apply to a script,\n" +
                    "a dash is displayed.\n\n" +
                    "If a non-background script is checked as\n" +
                    "default, the name will appear in bold." ),
                cursorchangedfunctionandarguments = (
                    self._on_row_selection, command_text_view ),
                rowactivatedfunctionandarguments = (
                    self.on_edit,
                    copy_,
                    remove,
                    indicator_text_entry ), ) )

        grid.attach( scripts_scrolledwindow, 0, 0, 1, 20 )

        grid.attach(
            self.create_box(
                ( ( Gtk.Label.new( _( "Command" ) ), False ), ),
                halign = Gtk.Align.START ),
             0, 20, 1, 1 )

        grid.attach(
            self.create_box(
                ( ( self.create_scrolledwindow( command_text_view ), True ), ) ),
             0, 21, 1, 10 )

        add.connect(
            "clicked",
            self.on_add,
            scripts_treeview,
            copy_,
            remove,
            indicator_text_entry )

        copy_.connect( "clicked", self.on_copy, scripts_treeview )

        remove.connect(
            "clicked",
            self.on_remove,
            scripts_treeview,
            copy_,
            indicator_text_entry )

#TODO Can/should this be put into a function to be called at end of remove/add/copy/edit?
        if len( treestore ):
            treepath = Gtk.TreePath.new_from_string( "0:0" )
            scripts_treeview.get_selection().select_path( treepath )
            scripts_treeview.set_cursor( treepath, None, False )

        else:
            copy_.set_sensitive( False )
            remove.set_sensitive( False )

        box.set_margin_top( IndicatorBase.INDENT_WIDGET_TOP )
        grid.attach( box, 0, 31, 1, 1 )

        send_command_to_log_checkbutton = (
            self.create_checkbutton(
                _( "Send command to log" ),
                tooltip_text = _(
                    "When a script is run,\n" +
                    "send the command to the log\n" +
                    "(located in your home directory)." ),
                active = self.send_command_to_log ) )

        grid.attach( send_command_to_log_checkbutton, 0, 32, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Scripts" ) ) )

        # Menu settings.
        grid = self.create_grid()

        grid.attach(
            self.create_box(
                ( ( Gtk.Label.new( _( "Show non-background scripts" ) ), False ), ) ),
            0, 0, 1, 1 )

        radio_show_scripts_submenu = (
            self.create_radiobutton(
                None,
                _( "In sub-menus" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.show_scripts_in_submenus ) )

        grid.attach( radio_show_scripts_submenu, 0, 1, 1, 1 )

        radio_show_scripts_indented = (
            self.create_radiobutton(
                radio_show_scripts_submenu,
                _( "Indented by group" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = not self.show_scripts_in_submenus ) )

        grid.attach( radio_show_scripts_indented, 0, 2, 1, 1 )

        hide_groups_checkbutton = (
            self.create_checkbutton(
                _( "Hide groups" ),
                tooltip_text = _(
                    "If checked, only script names are displayed.\n" +
                    "Otherwise, script names are indented\n" +
                    "within their respective group." ),
                sensitive = not self.show_scripts_in_submenus,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT * 2,
                active = self.hide_groups ) )

        radio_show_scripts_indented.connect(
            "toggled",
            self.on_radio_or_checkbox,
            True,
            hide_groups_checkbutton )

        grid.attach( hide_groups_checkbutton, 0, 3, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )

        # Icon text settings.
        grid = self.create_grid()

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Icon Text" ) ), False ),
                    ( indicator_text_entry, True ) ) ),
            0, 0, 1, 1 )

        indicator_text_separator_entry = (
            self.create_entry(
                self.indicator_text_separator,
                tooltip_text = _(
                    "The separator will be added between script tags." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Separator" ) ), False ),
                    ( indicator_text_separator_entry, False ) ) ),
            0, 1, 1, 1 )

        treestore_background_scripts_filter = treestore.filter_new()
        treestore_background_scripts_filter.set_visible_func(
            self._background_scripts_filter )

        background_scripts_treeview, background_scripts_scrolledwindow = (
            self.create_treeview_within_scrolledwindow(
                Gtk.TreeModelSort.new_with_model(
                    treestore_background_scripts_filter ),
                (
                    _( "Group" ),
                    _( "Name" ),
                    _( "Sound" ),
                    _( "Notification" ),
                    _( "Interval" ),
                    _( "Force Update" ) ),
                (
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_GROUP ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_NAME ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_SOUND ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_NOTIFICATION ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_INTERVAL ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorScriptRunner.COLUMN_MODEL_FORCE_UPDATE ) ),
                alignments_columnviewids = (
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_BACKGROUND_SOUND ),
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_BACKGROUND_NOTIFICATION ),
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_BACKGROUND_INTERVAL ),
                    (
                        0.5,
                        IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_BACKGROUND_FORCE_UPDATE) ),
                default_sort_func = self._script_sort,
                tooltip_text = _(
                    "Double click on a script to add to the icon text." ),
                rowactivatedfunctionandarguments = (
                    self._on_background_script_double_click,
                    indicator_text_entry ), ) )

        grid.attach( background_scripts_scrolledwindow, 0, 2, 1, 20 )

        notebook.append_page( grid, Gtk.Label.new( _( "Icon" ) ) )

        # General settings.
        grid = self.create_grid()

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = (
            self.create_preferences_common_widgets() )

        grid.attach( box, 0, 0, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        # Workaround for odd focus behaviour; in the Preferences dialog,
        # when switching tabs, the TextEntry on the third tab would have
        # the focus and highlight the text.
        # If the user hits the space bar (or any regular key), the text would
        # be overwritten.  Refer to:
        #    https://stackoverflow.com/questions/68931638/remove-focus-from-textentry
        #    https://gitlab.gnome.org/GNOME/gtk/-/issues/4249
        notebook.connect(
            "switch-page",
            lambda notebook, page, page_number: notebook.grab_focus() )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            # self.scripts = copy_of_scripts #TODO Will need to create all scripts from the treestore.
            self.send_command_to_log = send_command_to_log_checkbutton.get_active()
            self.show_scripts_in_submenus = radio_show_scripts_submenu.get_active()
            self.hide_groups = hide_groups_checkbutton.get_active()
            self.indicator_text = indicator_text_entry.get_text()
            self.indicator_text_separator = indicator_text_separator_entry.get_text()
            self.initialise_background_scripts()

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


    def _background_scripts_filter(
        self,
        model,
        iter_,
        data ):
        '''
        Show a row for a group if any script within the group is background.
        Show a row for a script if the script is background.
        '''
        row = model[ iter_ ]
        group = row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP ]
        if group is None:
            background = row[ IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ]
            show = background == IndicatorBase.TICK_SYMBOL

        else:
            show = False
            iter_scripts = model.iter_children( iter_ )
            while iter_scripts:
                row = model[ iter_scripts ]
                background = row[ IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ]
                if background == IndicatorBase.TICK_SYMBOL:
                    show = True
                    break

                iter_scripts = model.iter_next( iter_scripts )

        return show


    def _column_name_renderer(
        self,
        tree_column,
        cell_renderer,
        model,
        iter_,
        data ):
        '''
        Render a script name bold if that script is non-background and default.
        '''
        cell_renderer.set_property( "weight", Pango.Weight.NORMAL )

        default = (
            model.get_value(
                iter_, IndicatorScriptRunner.COLUMN_MODEL_DEFAULT_HIDDEN ) )

        if default and default == "True":
            cell_renderer.set_property( "weight", Pango.Weight.BOLD )


    def _script_sort(
        self,
        model,
        row1,
        row2,
        data ):

        return (
            Info.compare(
                model.get_value(
                    row1, IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ),
                model.get_value(
                    row1, IndicatorScriptRunner.COLUMN_MODEL_NAME ),
                model.get_value(
                    row2, IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ),
                model.get_value(
                    row2, IndicatorScriptRunner.COLUMN_MODEL_NAME ) ) )


    def _on_row_selection(
        self,
        treeview,
        textview ):

        command_text = ""
        model, iter_ = treeview.get_selection().get_selected()
        name = (
            model.get_value( iter_, IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

        if name:
            command_text = (
                model.get_value(
                    iter_, IndicatorScriptRunner.COLUMN_MODEL_COMMAND_HIDDEN ) )

        textview.get_buffer().set_text( command_text )


    def _on_background_script_double_click(
        self,
        treeview,
        path,
        treeviewcolumn,
        textentry ):

        model = treeview.get_model()
        iter_ = model.get_iter( path )
        name = (
            model.get_value( iter_, IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

        if name:
            group = (
                model.get_value(
                    iter_, IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

            textentry.insert_text(
                '[' + self._create_key( group, name ) + ']',
                textentry.get_position() )


    def on_copy(
        self,
        button_copy,
        treeview ):

        model, iter_ = treeview.get_selection().get_selected()
        name = (
            model.get_value( iter_, IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

        group = (
            model.get_value(
                iter_, IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

        groups = [
            row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
            for row in model ]

        if name is None:
            iter_select = (
                self._on_copy_group( treeview, model, iter_, group, groups ) )

        else:
            iter_select = (
                self._on_copy_script(
                    treeview, model, iter_, group, name, groups ) )

        self._update_user_interface( treeview, iter_select )


    def _on_copy_group(
        self,
        treeview,
        model,
        iter_group,
        group,
        groups ):

        grid = self.create_grid()

        group_entry = self.create_entry( group )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Group Name" ) ), False ),
                    ( group_entry, True ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 0, 1, 1 )

        dialog = (
            self.create_dialog(
                treeview,
                _( "Copy Group" ),
                content_widget = grid ) )

        parent = None
        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                group_ = group_entry.get_text().strip()
                if group_ == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "The group cannot be empty." ) )

                    group_entry.grab_focus()
                    continue

                if group_ in groups:
                    self.show_dialog_ok(
                        dialog,
                        _( "The group already exists!" ) )

                    group_entry.grab_focus()
                    continue

                row = [ group_, group_, None, None, None, None, None, None, None, None, None ]
                parent = model.append( None, row )
                iter_scripts = model.iter_children( iter_group )
                while iter_scripts:
                    row = [ group_, None ]
                    for column in range( model.get_n_columns() - 2 ):
                        row.append( model.get_value( iter_scripts, column + 2 ) )

                    model.append( parent, row )
                    iter_scripts = model.iter_next( iter_scripts )

            break

        dialog.destroy()

        dump = self.dump_treestore( model ) #TODO Testing
        print( dump )
        print()

        return parent


    def _on_copy_script(
        self,
        treeview,
        model,
        iter_script,
        group,
        name,
        groups ):

        script_group_combo = (
            self.create_comboboxtext(
                  groups,
                  tooltip_text = _(
                      "Choose an existing group or enter a new one." ),
                  active = groups.index( group ),
                  editable = True ) )

        grid = self.create_grid()

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Group" ) ), False ),
                    ( script_group_combo, True ) ) ),
            0, 0, 1, 1 )

        script_name_entry = self.create_entry( name )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Name" ) ), False ),
                    ( script_name_entry, True ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 1, 1, 1 )

        dialog = (
            self.create_dialog(
                treeview,
                _( "Copy Script" ),
                content_widget = grid ) )

        iter_select = None
        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                group_ = script_group_combo.get_active_text().strip()
                if group_ == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "The group cannot be empty." ) )

                    script_group_combo.grab_focus()
                    continue

                name_ = script_name_entry.get_text().strip()
                if name_ == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "The name cannot be empty." ) )

                    script_name_entry.grab_focus()
                    continue

                if self._get_iter_to_script( group_, name_, model ):
                    self.show_dialog_ok(
                        dialog,
                        _( "A script of the same group and name already exists!" ) )

                    script_group_combo.grab_focus()
                    continue

                if group_ not in groups:
                    row = [ group_, group_, None, None, None, None, None, None, None, None, None ]
                    parent = model.append( None, row )

                else:
                    parent = self._get_iter_to_group( group_, model )

                row = [ group_, None, name_ ]
                for column in range( model.get_n_columns() - 3 ):
                    row.append( model.get_value( iter_script, column + 3 ) )

                iter_select = model.append( parent, row )

            break

        dialog.destroy()

        dump = self.dump_treestore( model ) #TODO Testing
        print( dump )
        print()

        return iter_select


    def on_remove(
        self,
        button_remove,
        treeview,
        button_copy,
        textentry ):

        model, iter_ = treeview.get_selection().get_selected()
        name = (
            model.get_value( iter_, IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

        group = (
            model.get_value(
                iter_, IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

        iter_select = None
        old_tag_new_tag_pairs = None

        if name is None:
            scripts = [ ]
            iter_children = model.iter_children( iter_ )
            while iter_children:
                scripts.append(
                    model.get_value(
                        iter_children,
                        IndicatorScriptRunner.COLUMN_MODEL_NAME)  )

                iter_children = model.iter_next( iter_children )

            iter_select = self._on_remove_group( treeview, model, iter_ )
            old_tag_new_tag_pairs = ( )
            if iter_select:
                for script in scripts:
                    old_tag_new_tag_pairs += (
                        ( self._create_key( group, script ), "" ), )

        else:
            iter_select = self._on_remove_script( treeview, model, iter_ )
            if iter_select:
                old_tag_new_tag_pairs = (
                    ( self._create_key( group, name ), "" ), )

        self._update_user_interface(
            treeview,
            iter_select,
            button_copy = button_copy,
            button_remove = button_remove,
            textentry = textentry,
            old_tag_new_tag_pairs = old_tag_new_tag_pairs )


    def _on_remove_group(
        self,
        treeview,
        model,
        iter_to_group ):

        response = (
            self.show_dialog_ok_cancel(
                treeview,
                _(
                    "Remove the selected group and\n" +
                    "all scripts within the group?" ) ) )

        iter_select = None
        if response == Gtk.ResponseType.OK:
            if len( model ) > 1:
                iter_previous = model.iter_previous( iter_to_group )
                if iter_previous:
                    iter_select = (
                        model.iter_nth_child(
                        iter_previous,
                        model.iter_n_children( iter_previous ) - 1 ) )

                else:
                    iter_select = model.iter_next( iter_to_group )

            model.remove( iter_to_group )

        dump = self.dump_treestore( model ) #TODO Testing
        print( dump )
        print()

        return iter_select


    def _on_remove_script(
        self,
        treeview,
        model,
        iter_to_script ):

        response = (
            self.show_dialog_ok_cancel(
                treeview, _( "Remove the selected script?" ) ) )

        iter_select = None
        if response == Gtk.ResponseType.OK:
            iter_group = model.iter_parent( iter_to_script )
            if model.iter_n_children( iter_group ) > 1:
                iter_previous = model.iter_previous( iter_to_script )
                if iter_previous:
                    iter_select = iter_previous

                else:
                    iter_select = model.iter_next( iter_to_script )

                model.remove( iter_to_script )

            else:
                if len( model ) > 1:
                    iter_previous = model.iter_previous( iter_group )
                    if iter_previous:
                        iter_select = (
                            model.iter_nth_child(
                                iter_previous,
                                model.iter_n_children( iter_previous ) - 1 ) )

                    else:
                        iter_select = iter_group



                model.remove( iter_group )

        dump = self.dump_treestore( model ) #TODO Testing
        print( dump )
        print()

        return iter_select


    def on_edit(
        self,
        treeview,
        treepath,
        treeviewcolumn,
        button_copy,
        button_remove,
        textentry ):

        model, iter_ = treeview.get_selection().get_selected()
        name = (
            model.get_value( iter_, IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

        group = (
            model.get_value(
                iter_, IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

        groups = [
            row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
            for row in model ]

        iter_select = None
        old_tag_new_tag_pairs = None
        if name is None:
            self._on_edit_group( treeview, model, iter_, group, groups )
            group_ = (
                model.get_value(
                    iter_, IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

            if group != group_:
                iter_select = iter_

                iter_scripts = model.iter_children( iter_ )
                old_tag_new_tag_pairs = ( )
                while iter_scripts:
                    background = (
                        model.get_value(
                            iter_scripts,
                            IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ) )

                    if background == IndicatorBase.TICK_SYMBOL:
                        script = (
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

                        old_tag_new_tag_pairs += (
                            (
                                self._create_key( group, script ),
                                self._create_key( group_, script ) ), )

                    iter_scripts = model.iter_next( iter_scripts )

        else:
            background = (
                model.get_value(
                    iter_,
                    IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ) )

            iter_select = (
                self._on_edit_script(
                    treeview, model, iter_, group, name, groups ) )

            if iter_select:
                group_ = (
                    model.get_value(
                        iter_select,
                        IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

                name_ = (
                    model.get_value(
                        iter_select,
                        IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

                background_ = (
                    model.get_value(
                        iter_select,
                        IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ) )

                group_or_name_changed_or_both = group != group or name != name_
                was_background = background == IndicatorBase.TICK_SYMBOL

                no_longer_background = (
                    background == IndicatorBase.TICK_SYMBOL
                    and
                    background_ is None )

                update_indicator_text = (
                    ( group_or_name_changed_or_both and was_background )
                    or
                    no_longer_background )

                if update_indicator_text:
                    old_tag_new_tag_pairs = (
                        (
                            self._create_key( group, name ),
                            self._create_key( group_, name_ ) ), )

        self._update_user_interface(
            treeview,
            iter_select,
            button_copy = button_copy,
            button_remove = button_remove,
            textentry = textentry,
            old_tag_new_tag_pairs = old_tag_new_tag_pairs )


    def _on_edit_group(
        self,
        treeview,
        model,
        iter_group,
        group,
        groups ):

        grid = self.create_grid()

        group_entry = self.create_entry( group )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Group" ) ), False ),
                    ( group_entry, True ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 0, 1, 1 )

        dialog = (
            self.create_dialog(
                treeview,
                _( "Edit Group" ),
                content_widget = grid ) )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                group_ = group_entry.get_text().strip()
                if group_ == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "The group cannot be empty." ) )

                    group_entry.grab_focus()
                    continue

                if group_ in groups:
                    self.show_dialog_ok(
                        dialog,
                        _( "The group already exists!" ) )

                    group_entry.grab_focus()
                    continue

                model.set_value(
                    iter_group,
                    IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN,
                    group_ )

                model.set_value(
                    iter_group,
                    IndicatorScriptRunner.COLUMN_MODEL_GROUP,
                    group_ )

                iter_scripts = model.iter_children( iter_group )
                while iter_scripts:
                    model.set_value(
                        iter_scripts,
                        IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN,
                        group_ )

                    iter_scripts = model.iter_next( iter_scripts )

            break

        dialog.destroy()

        dump = self.dump_treestore( model ) #TODO Testing
        print( dump )
        print()


#TODO
# Check for when we click ADD and a group is selected...
# is this the group we select by default to add in the new script?
# Or just select the first group?
#
# If a script is selected, as above, use that script's group as the default group?
    def on_add(
        self,
        button_add,
        treeview,
        button_copy,
        button_remove ):

        model, iter_ = treeview.get_selection().get_selected()
        group = None
        if iter_:
            group = (
                model.get_value(
                    iter_, IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

        groups = [
            row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
            for row in model ]

        iter_select = (
            self._on_edit_script(
                treeview, treeview.get_model(), None, group, None, groups ) )

        self._update_user_interface(
            treeview,
            iter_select,
            button_copy = button_copy,
            button_remove = button_remove )


#TODO Test when adding very first script (there will be no group to select).
    def _on_edit_script(
        self,
        treeview,
        model,
        iter_script,
        group,
        name,
        groups ):

        add = name is None

        index = 0
        if groups: #TODO Test with no scripts (adding first script).
            index = groups.index( group )

        group_combo = (
            self.create_comboboxtext(
                groups,
                tooltip_text = _(
                    "The group to which the script belongs.\n\n" +
                    "Choose an existing group or enter a new one." ),
                active = index,
                editable = True ) )

        grid = self.create_grid()

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Group" ) ), False ),
                    ( group_combo, True ) ) ),
            0, 0, 1, 1 )

        name_entry = (
            self.create_entry(
                "" if add else name,
                tooltip_text = _( "The name of the script." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Name" ) ), False ),
                    ( name_entry, True ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 1, 1, 1 )

        grid.attach(
            self.create_box(
                ( ( Gtk.Label.new( _( "Command" ) ), False ), ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 2, 1, 1 )

        command_text_view = (
            self.create_textview(
                text =
                    "" if add else
                    model.get_value(
                        iter_script,
                        IndicatorScriptRunner.COLUMN_MODEL_COMMAND_HIDDEN ),
                tooltip_text = _( "The terminal script/command, along with any arguments." ) ) )

        grid.attach(
            self.create_box(
                ( ( self.create_scrolledwindow( command_text_view ), True ), ) ),
            0, 3, 1, 10 )

        active = False
        if not add:
            sound = (
                model.get_value(
                    iter_script, IndicatorScriptRunner.COLUMN_MODEL_SOUND ) )

            active = True if sound else False

        sound_checkbutton = (
            self.create_checkbutton(
                _( "Play sound" ),
                tooltip_text = _(
                    "For non-background scripts, play a sound\n" +
                    "on script completion.\n\n" +
                    "For background scripts, play a sound\n" +
                    "only if the script returns non-empty text." ),
                active = active ) )

        grid.attach( sound_checkbutton, 0, 13, 1, 1 )

        active = False
        if not add:
            notification = (
                model.get_value(
                    iter_script,
                    IndicatorScriptRunner.COLUMN_MODEL_NOTIFICATION ) )

            active = True if notification else False

        notification_checkbutton = (
            self.create_checkbutton(
                _( "Show notification" ),
                tooltip_text = _(
                    "For non-background scripts, show a\n" +
                    "notification on script completion.\n\n" +
                    "For background scripts, show a notification\n" +
                    "only if the script returns non-empty text." ),
                active = active ) )

        grid.attach( notification_checkbutton, 0, 14, 1, 1 )

        is_background = False
        if not add:
            background = (
                model.get_value(
                    iter_script,
                    IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ) )

            is_background = True if background else False

        script_non_background_radio = (
            self.create_radiobutton(
                None,
                _( "Non-background" ),
                tooltip_text = _(
                    "Non-background scripts are displayed\n" +
                    "in the menu and run when the user\n" +
                    "clicks on the corresponding menu item." ),
                active = not is_background ) )

        grid.attach( script_non_background_radio, 0, 15, 1, 1 )

        active = False
        if not add:
            if is_background:
                active = False

            else:
                terminal = (
                    model.get_value(
                        iter_script,
                        IndicatorScriptRunner.COLUMN_MODEL_TERMINAL ) )

                active = True if terminal else False

        terminal_checkbutton = (
            self.create_checkbutton(
                _( "Leave terminal open" ),
                tooltip_text = _( "Leave the terminal open on script completion." ),
                sensitive = not is_background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = active ) )

        grid.attach( terminal_checkbutton, 0, 16, 1, 1 )

        active = False
        if not add:
            if is_background:
                active = False

            else:
                default = (
                    model.get_value(
                        iter_script,
                        IndicatorScriptRunner.COLUMN_MODEL_DEFAULT_HIDDEN ) )

                active = True if default == "True" else False

        default_script_checkbutton = (
            self.create_checkbutton(
                _( "Default script" ),
                tooltip_text = _(
                    "One script may be set as default\n" +
                    "which is run on a middle mouse\n" +
                    "click of the indicator icon.\n\n" +
                    "Not supported on all desktops." ),
                sensitive = not is_background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = active ) )

        grid.attach( default_script_checkbutton, 0, 17, 1, 1 )

        script_background_radio = (
            self.create_radiobutton(
                script_non_background_radio,
                _( "Background" ),
                tooltip_text = _(
                    "Background scripts automatically run\n" +
                    "at the interval specified, but only if\n" +
                    "added to the icon text.\n\n" +
                    "Any exception which occurs during script\n" +
                    "execution will be logged to a file in the\n" +
                    "user's home directory and the script tag\n" +
                    "will remain in the icon text." ),
                active = is_background ) )

        grid.attach( script_background_radio, 0, 18, 1, 1 )

        interval_spinner = (
            self.create_spinbutton(
                int(
                    model.get_value(
                        iter_script,
                        IndicatorScriptRunner.COLUMN_MODEL_INTERVAL ) )
                if is_background else 60,
                1,
                10000,
                page_increment = 100,
                tooltip_text = _( "Interval, in minutes, between runs." ) ) )

        # Set margin left to approximately align with the checkboxes above.
        label_and_interval_spinner_box = (
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Interval" ) ), False ),
                    ( interval_spinner, False ) ),
                sensitive = is_background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT * 1.4 ) )

        grid.attach( label_and_interval_spinner_box, 0, 19, 1, 1 )

        active = False
        if not add:
            if is_background:
                force_update = (
                    model.get_value(
                        iter_script,
                        IndicatorScriptRunner.COLUMN_MODEL_FORCE_UPDATE ) )

                active = True if force_update else False

        force_update_checkbutton = (
            self.create_checkbutton(
                _( "Force update" ),
                tooltip_text = _(
                    "If the script returns non-empty text\n" +
                    "on its update, the script will run\n" +
                    "on the next update of ANY script." ),
                sensitive = is_background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = active ) )

        grid.attach( force_update_checkbutton, 0, 20, 1, 1 )

        script_non_background_radio.connect(
            "toggled",
            self.on_radio_or_checkbox,
            True,
            terminal_checkbutton,
            default_script_checkbutton )

        script_non_background_radio.connect(
            "toggled",
            self.on_radio_or_checkbox,
            False,
            label_and_interval_spinner_box,
            force_update_checkbutton )

        script_background_radio.connect(
            "toggled",
            self.on_radio_or_checkbox,
            True,
            label_and_interval_spinner_box,
            force_update_checkbutton )

        script_background_radio.connect(
            "toggled",
            self.on_radio_or_checkbox,
            False,
            terminal_checkbutton,
            default_script_checkbutton )

        dialog = (
            self.create_dialog(
                treeview,
                _( "Add Script" ) if add else _( "Edit Script" ),
                content_widget = grid ) )

        iter_select = None
        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                group_ = group_combo.get_active_text().strip()
                if group_ == "":
                    self.show_dialog_ok(
                        dialog, _( "The group cannot be empty." ) )

                    group_combo.grab_focus()
                    continue

                name_ = name_entry.get_text().strip()
                if name_ == "":
                    self.show_dialog_ok(
                        dialog, _( "The name cannot be empty." ) )

                    name_entry.grab_focus()
                    continue

                command_ = self.get_textview_text( command_text_view ).strip()
                if command_ == "":
                    self.show_dialog_ok(
                        dialog, _( "The command cannot be empty." ) )

                    command_text_view.grab_focus()
                    continue

                script_exists = self._get_iter_to_script( group_, name_, model )  #TODO Check for when None and not None.
                message = _(
                    "A script of the same group and name already exists." )

                if add:
                    if script_exists:
                        self.show_dialog_ok( dialog, message )
                        group_combo.grab_focus()
                        continue

                else:
                    if ( group != group_ or name != name_ ) and script_exists:
                        self.show_dialog_ok( dialog, message )
                        group_combo.grab_focus()
                        continue

                if not add:
#TODO If this is the last script in this group, will there be a group left over?
# Will occur if the script group is changed (to a new group or another group).
# So maybe before removing the script, get the parent and if the children count
# is 1, then also remove the parent.
#Might be able just to remove the parent.
                    model.remove( iter_script )

                is_non_background_and_default = (
                    script_non_background_radio.get_active()
                    and
                    default_script_checkbutton.get_active() )

                if is_non_background_and_default:
#TODO I created a new non-background script, marked as default,
# but this code did not clear the existing default non-background script.
                    def remove_default( model, path, iter_, data ):
                        model.set_value(
                            iter_,
                            IndicatorScriptRunner.COLUMN_MODEL_DEFAULT_HIDDEN,
                            "False" )


                    model.foreach( remove_default )

                if group_ not in groups:
                    row = [ group_, group_, None, None, None, None, None, None, None, None, None ]
                    parent = model.append( None, row )

                else:
                    parent = self._get_iter_to_group( group_, model )

                row = [
                    group_,
                    None,
                    name_,
                    self.get_textview_text( command_text_view ).strip(),
                    IndicatorBase.TICK_SYMBOL if sound_checkbutton.get_active()
                    else None,
                    IndicatorBase.TICK_SYMBOL if notification_checkbutton.get_active()
                    else None,
                    IndicatorBase.TICK_SYMBOL if script_background_radio.get_active()
                    else None,
                    '—' if script_background_radio.get_active()
                    else (
                        IndicatorBase.TICK_SYMBOL if terminal_checkbutton.get_active()
                        else None
                    ),
                    str( False ) if script_background_radio.get_active()
                    else str( default_script_checkbutton.get_active() ),
                    str( interval_spinner.get_value_as_int() )
                    if script_background_radio.get_active()
                    else '—',
                    (
                        IndicatorBase.TICK_SYMBOL if force_update_checkbutton.get_active()
                        else None )
                    if script_background_radio.get_active() else '—' ]

                iter_select = model.append( parent, row )

            break

        dialog.destroy()

        dump = self.dump_treestore( model ) #TODO Testing
        print( dump )
        print()

        return iter_select


    def _get_iter_to_group(
        self,
        group,
        model ):

        iter_to_group = None
        iter_groups = model.get_iter_first()
        while iter_groups:
            group_ = (
                model.get_value(
                    iter_groups,
                    IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

            if group == group_:
                iter_to_group = iter_groups
                break

            iter_groups = model.iter_next( iter_groups )

        return iter_to_group


    def _get_iter_to_script(
        self,
        group,
        name,
        model ):

        iter_to_script = None
        iter_groups = self._get_iter_to_group( group, model )
        if iter_groups:
            group_ = (
                model.get_value(
                    iter_groups,
                    IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

            if group == group_:
                iter_scripts = model.iter_children( iter_groups )
                while iter_scripts:
                    name_ = (
                        model.get_value(
                            iter_scripts,
                            IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

                    if name == name_:
                        iter_to_script = iter_scripts
                        break

                    iter_scripts = model.iter_next( iter_scripts )

        return iter_to_script


    def get_scripts_by_group(
        self,
        scripts,
        non_background = True,
        background = True ):

        scripts_by_group = { }
        for script in scripts:
            script_is_non_background_and_want_non_background = (
                non_background and isinstance( script, NonBackground ) )

            script_is_background_and_want_background = (
                background and isinstance( script, Background ) )

            want_script = (
                script_is_non_background_and_want_non_background
                or
                script_is_background_and_want_background )

            if want_script:
                if script.get_group() not in scripts_by_group:
                    scripts_by_group[ script.get_group() ] = [ ]

                scripts_by_group[ script.get_group() ].append( script )

        return scripts_by_group


#TODO For testing
    def dump_treestore(
        self,
        model ):


        def dump_treestore_( model, treepath, iter, dump ):
            for i in list( range( 11 ) ):
                dump[ 0 ] += f"{ model.get_value( iter, i ) } | "

            dump[ 0 ] = dump[ 0 ][ 0 : -2 ] + '\n'


        dump = [ "" ]
        model.foreach( dump_treestore_, dump )
        return dump[ 0 ]
        # return ""


    def _update_user_interface(
        self,
        treeview,
        treeiter,
        button_copy = None,
        button_remove = None,
        textentry = None,
        old_tag_new_tag_pairs = None ):

        model = treeview.get_model()

#TODO Check to see who will call this function...
#... surely treeiter will ALWAYS be valid?
        if treeiter:
            treepath = (
                Gtk.TreePath.new_from_string(
                    model.get_string_from_iter( treeiter ) ) )

        else:
            treepath = Gtk.TreePath.new_from_string( "0:0" )

        treeview.expand_to_path( treepath )
        treeview.get_selection().select_path( treepath )
        treeview.set_cursor( treepath, None, False )

        if button_copy:
            button_copy.set_sensitive( len( model ) )

        if button_remove:
            button_remove.set_sensitive( len( model ) )

        if textentry and old_tag_new_tag_pairs:
#TODO Test this section.
            for old_tag, new_tag in old_tag_new_tag_pairs:
                textentry.set_text(
                    textentry.get_text().replace(
                        "[" + old_tag + "]",
                        "[" + new_tag + "]" if new_tag else "" ) )
                print( old_tag )
                print( new_tag )
                print() #TODO Remove


    def initialise_background_scripts( self ):
        '''
        Each time a background script is run, cache the result.

        If for example, one script has an interval of five minutes and another
        script is hourly, the hourly script should only be run hourly, so use a
        cached result when the shorter interval script is run.

        Initialise the cache results and set a next update time in the past to
        force all (background) scripts to update first time.
        '''
        self.background_script_results = { }
        self.background_script_next_update_time = { }
        today = datetime.datetime.now()
        for script in self.scripts:
            if isinstance( script, Background ):
                key = self._create_key( script.get_group(), script.get_name() )
                self.background_script_results[ key ] = None
                self.background_script_next_update_time[ key ] = today


    def _create_key(
            self,
            group,
            name ):

        return group + "::" + name


    def is_background_script_in_indicator_text(
        self,
        script ):

        key = self._create_key( script.get_group(), script.get_name() )
        indicator_text = '[' + key + ']'
        return indicator_text in self.indicator_text


    def load_config(
        self,
        config ):

        self.hide_groups = (
            config.get( IndicatorScriptRunner.CONFIG_HIDE_GROUPS, False ) )

        self.indicator_text = (
            config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT, "" ) )

        self.indicator_text_separator = (
            config.get(
                IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR,
                " | " ) )

        self.send_command_to_log = (
            config.get(
                IndicatorScriptRunner.CONFIG_SEND_COMMAND_TO_LOG, False ) )

        self.show_scripts_in_submenus = (
            config.get(
                IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS, False ) )

        self.scripts = [ ]
        scripts_non_background = (
            config.get( self.CONFIG_SCRIPTS_NON_BACKGROUND, [ ] ) )

        for script in scripts_non_background:
            skript = NonBackground(
                script[ IndicatorScriptRunner.JSON_GROUP ],
                script[ IndicatorScriptRunner.JSON_NAME ],
                script[ IndicatorScriptRunner.JSON_COMMAND ],
                bool( script[ IndicatorScriptRunner.JSON_PLAY_SOUND ] ),
                bool( script[ IndicatorScriptRunner.JSON_SHOW_NOTIFICATION ] ),
                bool( script[ IndicatorScriptRunner.JSON_TERMINAL_OPEN ] ),
                bool( script[ IndicatorScriptRunner.JSON_DEFAULT ] ) )

            self.scripts.append( skript )


        scripts_background = config.get( self.CONFIG_SCRIPTS_BACKGROUND, [ ] )
        for script in scripts_background:
            skript = Background(
                script[ IndicatorScriptRunner.JSON_GROUP ],
                script[ IndicatorScriptRunner.JSON_NAME ],
                script[ IndicatorScriptRunner.JSON_COMMAND ],
                bool( script[ IndicatorScriptRunner.JSON_PLAY_SOUND ] ),
                bool( script[ IndicatorScriptRunner.JSON_SHOW_NOTIFICATION ] ),
                script[ IndicatorScriptRunner.JSON_INTERVAL_IN_MINUTES ],
                bool( script[ IndicatorScriptRunner.JSON_FORCE_UPDATE ] ) )

            self.scripts.append( skript )

        if len( self.scripts) == 0:
            # Example non-background scripts.
            self.scripts.append(
                NonBackground(
                    "Network",
                    "Ping Google",
                    "ping -c 3 www.google.com",
                    False, False, False, False ) )

            self.scripts.append(
                NonBackground(
                    "Network",
                    "Public IP address",
                    "notify-send -i " +
                    self.get_icon_name() +
                    " \"Public IP address: $(wget https://ipinfo.io/ip -qO -)\"",
                    False, False, False, False ) )

            self.scripts.append(
                NonBackground(
                    "Network",
                    "Up or down",
                    "if wget -qO /dev/null google.com > /dev/null; " +
                    "then notify-send -i " + self.get_icon_name() +
                    " \"Internet is UP\"; else notify-send \"Internet is DOWN\"; fi",
                    False, False, False, True ) )

            system_usage = " \"System Usage:\" "
            ram = "\"RAM: $( free | grep Mem | awk \'\\'' { printf \"%.0f\", $3/$2*100 } \'\\'' )%  "
            hdd = "HDD: $( df -h /dev/sda2 | grep sda2 | awk \'\\'' { print $5 } \'\\''  )\""
            self.scripts.append(
                NonBackground(
                    "System",
                    "RAM + HDD (/dev/sda2)",
                    "notify-send -i "
                    +
                    self.get_icon_name()
                    +
                    system_usage
                    +
                    ram
                    +
                    hdd,
                    False, False, False, False ) )

            self.scripts.append(
                NonBackground(
                    "Update",
                    "autoclean | autoremove | update | dist-upgrade",
                    "sudo apt-get autoclean && " +
                    "sudo apt-get -y autoremove && " +
                    "sudo apt-get update && " +
                    "sudo apt-get -y dist-upgrade",
                    True, True, True, False ) )

            # Example background scripts.
            self.scripts.append(
                Background(
                    "Network",
                    "Internet Down",
                    "if wget -qO /dev/null google.com > /dev/null; " +
                    "then echo \"\"; else echo \"Internet is DOWN\"; fi",
                    False, True, 60, True ) )

            self.scripts.append(
                Background(
                    "System",
                    "Available Memory",
                    "echo \"Free Memory: \"$(expr $( cat /proc/meminfo | " +
                    "grep MemAvailable | tr -d -c 0-9 ) / 1024)\" MB\"",
                    False, False, 5, False ) )

            self.indicator_text = (
                " [Network::Internet Down][System::Available Memory]" )

        self.initialise_background_scripts()


    def save_config( self ):
        scripts_background = [ ]
        scripts_non_background = [ ]
        for script in self.scripts:
            if isinstance( script, Background ):
                scripts_background.append( [
                    script.get_group(),
                    script.get_name(),
                    script.get_command(),
                    script.get_play_sound(),
                    script.get_show_notification(),
                    script.get_interval_in_minutes(),
                    script.get_force_update() ] )

            else:
                scripts_non_background.append( [
                    script.get_group(),
                    script.get_name(),
                    script.get_command(),
                    script.get_play_sound(),
                    script.get_show_notification(),
                    script.get_terminal_open(),
                    script.get_default() ] )

        return {
            IndicatorScriptRunner.CONFIG_HIDE_GROUPS:
                self.hide_groups,

            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT:
                self.indicator_text,

            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR:
                self.indicator_text_separator,

            IndicatorScriptRunner.CONFIG_SCRIPTS_BACKGROUND:
                scripts_background,

            IndicatorScriptRunner.CONFIG_SCRIPTS_NON_BACKGROUND:
                scripts_non_background,

            IndicatorScriptRunner.CONFIG_SEND_COMMAND_TO_LOG:
                self.send_command_to_log,

            IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS:
                self.show_scripts_in_submenus
        }


IndicatorScriptRunner().main()
