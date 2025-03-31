#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from _operator import add


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


#TODO When selecting a group, ensure command is cleared.


#TODO When deleting a script,
# if the script's group still exists, maybe
# select the first script of that group.
# Otherwise, select first script.
#
# When add/edit a script, see fortune/onthisday...maybe there is a simpler
# way to select the script (similarly for remove).


#TODO Should really handle double click of a group (which will edit that group name).


#TODO Should really handle copy of a group.


#TODO Should really handle delete of a group.


#TODO Ensure double clicking of a group does nothing...
# ...now it opens up the script edit dialog!
# Assuming we don't want to allow edit/rename of a group.


#TODO If Copy/edit/remove of groups is implemented, add this to changelog.


import concurrent.futures
import copy
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

        copy_of_scripts = copy.deepcopy( self.scripts )  #TODO Is this needed if the treestore is used?

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

        # Rows pertain to a group (showing only the group name) or a script
        # (showing the script name and the script's attributes).
        #
        # Each row additionally contains the group name in the first column,
        # allowing the group to be determined for a row containing a script.
        treestore = Gtk.TreeStore( str, str, str, str, str, str, str, str, str, str, str )
        scripts_by_group = self.get_scripts_by_group( copy_of_scripts )
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
                    None if isinstance( script, Background )
                    else str( script.get_default() ),
                    str( script.get_interval_in_minutes() )
                    if isinstance( script, Background )
                    else '—',
                    (
                        IndicatorBase.TICK_SYMBOL if script.get_force_update()
                        else None ) ]

                treestore.append( parent, row )

        treestore_background_scripts_filter = treestore.filter_new()
        treestore_background_scripts_filter.set_visible_func(
            self._background_scripts_filter, copy_of_scripts )

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
                    self.on_background_script_double_click,
                    indicator_text_entry ), ) )

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
                        (
                            self.column_name_renderer,
                            copy_of_scripts ),
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
                    self.on_script_selection,
                    command_text_view,
                    copy_of_scripts ),
                rowactivatedfunctionandarguments = (
                    self.on_edit,
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

        add.connect(
            "clicked",
            self.on_add,
            scripts_treeview,
            copy_,
            remove )

        copy_.connect( "clicked", self.on_copy, scripts_treeview )

        remove.connect(
            "clicked",
            self.on_remove,
            scripts_treeview,
            indicator_text_entry,
            copy_ )

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
            "toggled", self.on_radio_or_checkbox, True, hide_groups_checkbutton )

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
                tooltip_text = _( "The separator will be added between script tags." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Separator" ) ), False ),
                    ( indicator_text_separator_entry, False ) ) ),
            0, 1, 1, 1 )

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
            self.scripts = copy_of_scripts #TODO Will need to create all scripts from the treestore.
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
        treeiter,
        scripts ):
        '''
        Show a row for a script if the script is background.
        Show a row for a group if the associated script is background.
        '''

        row = model[ treeiter ]
        group = row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP ]
        if group is None:
            # Row is a script.
            show = (
                row[ IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ]
                ==
                IndicatorBase.TICK_SYMBOL )

        else:
            # Row is a group.
            background_scripts_by_group = (
                self.get_scripts_by_group(
                    scripts,
                    non_background = False,
                    background = True ) )

            show = group in background_scripts_by_group

        return show


    def column_name_renderer(
        self,
        treeviewcolumn,
        cell_renderer,
        treemodel,
        treeiter,
        scripts ):
        '''
        Render a script name bold if that script is non-background and default.
        '''

        cell_renderer.set_property( "weight", Pango.Weight.NORMAL )
        name = (
            treemodel.get_value(
                treeiter, IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

        if name:
            group = (
                treemodel.get_value(
                    treemodel.iter_parent( treeiter ),
                    IndicatorScriptRunner.COLUMN_MODEL_GROUP ) )

            script = self.get_script( scripts, group, name )
            if isinstance( script, NonBackground ) and script.get_default():
                cell_renderer.set_property( "weight", Pango.Weight.BOLD )


    def _script_sort(
        self,
        model,
        row1,
        row2,
        user_data ):

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


#TODO HOpefully can delete.
    # def populate_treestore_and_select_script(
    #     self,
    #     treeview_all_scripts,
    #     treeview_background_scripts,
    #     scripts,
    #     select_group,
    #     select_script ):
    #
    #     treestore = treeview_all_scripts.get_model()
    #     treestore.clear()
    #
    #     scripts_by_group = self.get_scripts_by_group( scripts, non_background = True, background = True )
    #     groups = sorted( scripts_by_group.keys(), key = str.lower )
    #     for group in groups:
    #         row = [ group, None, None, None, None, None, None, None ]
    #         parent = treestore.append( None, row )
    #         for script in sorted( scripts_by_group[ group ], key = lambda script: script.get_name().lower() ):
    #             row = [
    #                None, # Don't add in the group name as it will be displayed.
    #                script.get_name(),
    #                IndicatorBase.TICK_SYMBOL if script.get_play_sound() else None,
    #                IndicatorBase.TICK_SYMBOL if script.get_show_notification() else None,
    #                IndicatorBase.TICK_SYMBOL if isinstance( script, Background ) else None,
    #                '—'
    #                if isinstance( script, Background ) else
    #                ( IndicatorBase.TICK_SYMBOL if script.get_terminal_open() else None ),
    #                str( script.get_interval_in_minutes() )
    #                if isinstance( script, Background ) else
    #                '—',
    #                ( IndicatorBase.TICK_SYMBOL if script.get_force_update() else None )
    #                if isinstance( script, Background ) else
    #                '—' ]
    #
    #             treestore.append( parent, row )
    #
    #     treeview_background_scripts.get_model().refilter()
    #
    #     if scripts:
    #         background_scripts_by_group = self.get_scripts_by_group( scripts, non_background = False, background = True )
    #         background_groups = sorted( background_scripts_by_group.keys(), key = str.lower )
    #         self._expand_trees_and_select(
    #             treeview_all_scripts,
    #             treeview_background_scripts,
    #             select_group,
    #             select_script,
    #             scripts_by_group,
    #             groups,
    #             background_groups )


#TODO HOpefully can delete.
    # def _expand_trees_and_select(
    #     self,
    #     treeview_all_scripts,
    #     treeview_background_scripts,
    #     select_group,
    #     select_script,
    #     scripts_by_group,
    #     groups,
    #     background_groups ):
    #
    #     def build_path_and_select_group_and_script( treeview, groups ):
    #         path_as_string = "0:0"
    #         if select_group:
    #             try:
    #                 group_index = groups.index( select_group )
    #                 scripts_for_group = scripts_by_group[ select_group ]
    #                 i = 0
    #                 for script in sorted( scripts_for_group, key = lambda script: script.get_name().lower() ):
    #                     if select_script == script.get_name():
    #                         path_as_string = str( group_index ) + ":" + str( i )
    #                         break
    #
    #                     i += 1
    #
    #             except ValueError:
    #                 # Occurs when a group/script selected in the all scripts treeview
    #                 # does not exist in the background scripts treeview,
    #                 # so accept the default (select first item using 0:0).
    #                 pass
    #
    #         treeview.expand_all()
    #         treepath = Gtk.TreePath.new_from_string( path_as_string )
    #         treeview.get_selection().select_path( treepath )
    #         treeview.set_cursor( treepath, None, False )
    #         if len( treeview.get_model() ):
    #             treeview.scroll_to_cell( treepath ) # Doesn't like to be called when empty.
    #
    #     build_path_and_select_group_and_script( treeview_all_scripts, groups )
    #     build_path_and_select_group_and_script(
    #         treeview_background_scripts, background_groups )


#TODO Needs to change to obtain command text from store.
    def on_script_selection(
        self,
        treeview,
        textview,
        scripts ):

        # group, name = self._get_selected_script( treeview )
        # command_text = ""
        # if group and name:
        #     command_text = self.get_script( scripts, group, name ).get_command()
        #
        # textview.get_buffer().set_text( command_text )
        pass


    def on_background_script_double_click(
        self,
        treeview,
        treepath,
        treeviewcolumn,
        textentry ):

        group, name = self._get_selected_script( treeview )
        if group and name:  #TODO Maybe just check for name; group should ALWAYS be present.
            textentry.insert_text(
                '[' + self._create_key( group, name ) + ']',
                textentry.get_position() )


#TODO Can this be re-written to use treemodel.foreach()?
    def script_exists(
        self,
        group,
        name,
        model ):

        script_exists = False
        iter_groups = model.get_iter_first()
        while iter_groups:
            iter_scripts = model.iter_children( iter_groups )
            while iter_scripts:
                group_ = (
                    model.get_value(
                        iter_scripts,
                        IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

                name_ = (
                    model.get_value(
                        iter_scripts,
                        IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

                script_exists = group == group_ and name == name_
                if script_exists:
                    break

                iter_scripts = model.iter_next( iter_scripts )

            if script_exists:
                break

            iter_groups = model.iter_next( iter_groups )

        return script_exists


    def get_iter_to_script(
        self,
        group,
        name,
        model ):

        iter_to_script = None
        iter_groups = model.get_iter_first()
        while iter_groups:
            iter_scripts = model.iter_children( iter_groups )
            while iter_scripts:
                group_ = (
                    model.get_value(
                        iter_scripts,
                        IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

                name_ = (
                    model.get_value(
                        iter_scripts,
                        IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

                if group == group_ and name == name_:
                    iter_to_script = iter_scripts
                    break

                iter_scripts = model.iter_next( iter_scripts )

            if iter_to_script:
                break

            iter_groups = model.iter_next( iter_groups )

        return iter_to_script


    def get_iter_to_group(
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

            if iter_to_group:
                break

            iter_groups = model.iter_next( iter_groups )

        return iter_to_group


    def on_copy(
        self,
        button,
        treeview ):

        group, name = self._get_selected_script( treeview )
        if name is None:
            self._on_copy_group( group, treeview )

        else:
            self._on_copy_script( group, name, treeview )


    def _on_copy_group(
        self,
        group,
        treeview ):

        model = treeview.get_model()
        groups = [
            row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
            for row in model ]

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
                iter_to_group = self.get_iter_to_group( group, model )
                iter_scripts = model.iter_children( iter_to_group )
                while iter_scripts:
                    model.append(
                        parent,
                        [
                            group_,
                            None,
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_NAME ),
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_COMMAND_HIDDEN ),
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_SOUND ),
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_NOTIFICATION ),
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ),
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_TERMINAL ),
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_DEFAULT_HIDDEN ),
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_INTERVAL ),
                            model.get_value(
                                iter_scripts,
                                IndicatorScriptRunner.COLUMN_MODEL_FORCE_UPDATE ) ] )

                    iter_scripts = model.iter_next( iter_scripts )

                treepath = (
                    Gtk.TreePath.new_from_string(
                        model.get_string_from_iter(
                        self.get_iter_to_group( group_, model ) ) ) )

                treeview.expand_to_path( treepath )
                treeview.get_selection().select_path( treepath )
                treeview.set_cursor( treepath, None, False )
#TODO Selecting a group should clear the command.

                break

        dialog.destroy()


    def _on_copy_script(
        self,
        button,
        group,
        name,
        treeview ):

        group, name = self._get_selected_script( treeview )
        model = treeview.get_model()
        groups = [
            row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
            for row in model ]

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

                if self.script_exists( group_, name_, model ):
                    self.show_dialog_ok(
                        dialog,
                        _( "A script of the same group and name already exists!" ) )

                    script_group_combo.grab_focus()
                    continue

                if group_ not in groups:
                    row = [ group_, group_, None, None, None, None, None, None, None, None, None ]
                    parent = model.append( None, row )

                else:
                    parent = self.get_iter_to_group( group_, model )

#TODO Can this code be put into a function to be called by copy_group and copy_script?
# Maybe also used by edit script/group?
                iter_to_original = self.get_iter_to_script( group, name, model )
                model.append(
                    parent,
                    [
                        group_,
                        None,
                        name_,
                        model.get_value(
                            iter_to_original,
                            IndicatorScriptRunner.COLUMN_MODEL_COMMAND_HIDDEN ),
                        model.get_value(
                            iter_to_original,
                            IndicatorScriptRunner.COLUMN_MODEL_SOUND ),
                        model.get_value(
                            iter_to_original,
                            IndicatorScriptRunner.COLUMN_MODEL_NOTIFICATION ),
                        model.get_value(
                            iter_to_original,
                            IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ),
                        model.get_value(
                            iter_to_original,
                            IndicatorScriptRunner.COLUMN_MODEL_TERMINAL ),
                        model.get_value(
                            iter_to_original,
                            IndicatorScriptRunner.COLUMN_MODEL_DEFAULT_HIDDEN ),
                        model.get_value(
                            iter_to_original,
                            IndicatorScriptRunner.COLUMN_MODEL_INTERVAL ),
                        model.get_value(
                            iter_to_original,
                            IndicatorScriptRunner.COLUMN_MODEL_FORCE_UPDATE ) ] )

                treepath = (
                    Gtk.TreePath.new_from_string(
                        model.get_string_from_iter(
                            self.get_iter_to_script( group_, name_, model ) ) ) )

                treeview.expand_to_path( treepath )
                treeview.get_selection().select_path( treepath )
                treeview.set_cursor( treepath, None, False )
#TODO Ensure that one of the lines above selects the script and
# that in turn shows the command (same command as original script).

                break

        dialog.destroy()


#TODO Hopefully can delete.
#     def on_copyORIGINAL(
#         self,
#         button,
#         treeview ):
#
#         group, name = self._get_selected_script( treeview )
#         model = treeview.get_model()
#         groups = [
#             row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
#             for row in model ]
#
#         script_group_combo = (
#             self.create_comboboxtext(
#                   groups,
#                   tooltip_text = _(
#                       "Choose an existing group or enter a new one." ),
#                   active = groups.index( group ),
#                   editable = True ) )
#
#         grid = self.create_grid()
#
#         grid.attach(
#             self.create_box(
#                 (
#                     ( Gtk.Label.new( _( "Group" ) ), False ),
#                     ( script_group_combo, True ) ) ),
#             0, 0, 1, 1 )
#
#         script_name_entry = self.create_entry( name )
#
#         grid.attach(
#             self.create_box(
#                 (
#                     ( Gtk.Label.new( _( "Name" ) ), False ),
#                     ( script_name_entry, True ) ),
#                 margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
#             0, 1, 1, 1 )
#
#         dialog = (
#             self.create_dialog(
#                 treeview,
#                 _( "Copy Script" ),
#                 content_widget = grid ) )
#
#         while True:
#             dialog.show_all()
#             if dialog.run() == Gtk.ResponseType.OK:
#                 group_ = script_group_combo.get_active_text().strip()
#                 if group_ == "":
#                     self.show_dialog_ok(
#                         dialog,
#                         _( "The group cannot be empty." ) )
#
#                     script_group_combo.grab_focus()
#                     continue
#
#                 name_ = script_name_entry.get_text().strip()
#                 if name_ == "":
#                     self.show_dialog_ok(
#                         dialog,
#                         _( "The name cannot be empty." ) )
#
#                     script_name_entry.grab_focus()
#                     continue
#
#                 if self.script_exists( group_, name_, model ):
#                     self.show_dialog_ok(
#                         dialog,
#                         _( "A script of the same group and name already exists!" ) )
#
#                     script_group_combo.grab_focus()
#                     continue
#
#                 if group_ not in groups:
#                     row = [ group_, group_, None, None, None, None, None, None, None, None ]
#                     parent = model.append( None, row )
#
#                 else:
#                     parent = self.get_iter_to_group( group_, model )
#
#                 iter_to_original = self.get_iter_to_script( group, name, model )
#                 model.append(
#                     parent,
#                     [
#                         group_,
#                         None,
#                         name_,
#                         model.get_value(
#                             iter_to_original,
#                             IndicatorScriptRunner.COLUMN_MODEL_COMMAND_HIDDEN ),
#                         model.get_value(
#                             iter_to_original,
#                             IndicatorScriptRunner.COLUMN_MODEL_SOUND ),
#                         model.get_value(
#                             iter_to_original,
#                             IndicatorScriptRunner.COLUMN_MODEL_NOTIFICATION ),
#                         model.get_value(
#                             iter_to_original,
#                             IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ),
#                         model.get_value(
#                             iter_to_original,
#                             IndicatorScriptRunner.COLUMN_MODEL_TERMINAL ),
#                         model.get_value(
#                             iter_to_original,
#                             IndicatorScriptRunner.COLUMN_MODEL_INTERVAL ),
#                         model.get_value(
#                             iter_to_original,
#                             IndicatorScriptRunner.COLUMN_MODEL_FORCE_UPDATE ) ] )
#
#                 treepath = (
#                     Gtk.TreePath.new_from_string(
#                         model.get_string_from_iter(
#                             self.get_iter_to_script( group_, name_, model ) ) ) )
#
#                 treeview.expand_to_path( treepath )
#                 treeview.get_selection().select_path( treepath )
#                 treeview.set_cursor( treepath, None, False )
# #TODO Ensure that one of the lines above selects the script and
# # that in turn shows the command (same command as original script).
#
#                 break
#
#         dialog.destroy()


    def update_indicator_textentry(
        self,
        textentry,
        old_tag,
        new_tag ):

        old_tag_ = "[" + old_tag + "]"
        if new_tag:
            textentry.set_text(
                textentry.get_text().replace( old_tag_, "[" + new_tag + "]" ) )

        else:
            textentry.set_text(
                textentry.get_text().replace( old_tag_, "" ) )


#TODO Once sorted, remove unused parameters.
#TODO Implement for script and group simultaneously, or instead, have separate functions?
    def on_remove(
        self,
        button_remove,
        treeview,
        textentry,
        button_copy ):

        group, name = self._get_selected_script( treeview )
        model_sort = treeview.get_model()
        if name is None:
            response = (
                self.show_dialog_ok_cancel(
                    treeview,
                    _(
                        "Remove the selected group and\n" +
                        "all scripts within the group?" ) ) )

            if response == Gtk.ResponseType.OK:
                print( f"Remove { group } and all scripts within")
                #TODO Delete group and all scripts within.
                #TODO Select group above if available,
                # then below if available,
                # then disable remove/copy buttons.

        else:
            response = (
                self.show_dialog_ok_cancel(
                    treeview, _( "Remove the selected script?" ) ) )

            if response == Gtk.ResponseType.OK:
                print( f"Remove { name } from { group }")
                # model_sort.get_model().remove(
                #     model_sort.convert_iter_to_child_iter( treeiter_sort ) )


                #TODO Delete script.
                #TODO Delete group if was last script.
                #TODO Select script above if available,
                # then script below if available,
                # then group if available,
                # then group below/above if available,  OR last script above of above group if available,
                # then disable remove/copy buttons.

        if True:
            return

        model_sort, treeiter_sort = treeview.get_selection().get_selected()
        treepath = (
            Gtk.TreePath.new_from_string(
                model_sort.get_string_from_iter( treeiter_sort ) ) )

        group = model_sort[ treeiter_sort ][ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
        script = model_sort[ treeiter_sort ][ IndicatorScriptRunner.COLUMN_MODEL_NAME ]
        if script is None:
            response = (
                self.show_dialog_ok_cancel(
                    treeview,
                    _(
                        "Remove the selected group and\n" +
                        "all scripts within the group?" ) ) )

            if response == Gtk.ResponseType.OK:
                print( f"Remove { group } and all scripts within")
                #TODO Delete group and all scripts within.
                #TODO Select group above if available,
                # then below if available,
                # then disable remove/copy buttons.

        else:
            response = (
                self.show_dialog_ok_cancel(
                    treeview, _( "Remove the selected script?" ) ) )

            if response == Gtk.ResponseType.OK:
                print( f"Remove { script } from { group }")
                has_previous = treepath.prev()

                model_sort.get_model().remove(
                    model_sort.convert_iter_to_child_iter( treeiter_sort ) )


                #TODO Delete script.
                #TODO Delete group if was last script.
                #TODO Select script above if available,
                # then script below if available,
                # then group if available,
                # then group below/above if available,  OR last script above of above group if available,
                # then disable remove/copy buttons.

        if True:
            return

        # has_previous = treepath.prev()
        # if has_previous:
        #     scripts_treeview.get_selection().select_path( treepath )
        #     model, treeiter = scripts_treeview.get_selection().get_selected()
        #     # print( model[ treeiter ][ 8 ] )
        #     print( "has previous" )

        treepath.next()
        treeview.get_selection().select_path( treepath )
        model, treeiter = treeview.get_selection().get_selected()
        # print( model[ treeiter ][ 8 ] )
        print( "has next" )


        if True:
            return



        response = (
            self.show_dialog_ok_cancel(
                treeview, _( "Remove the selected script?" ) ) )

        if response == Gtk.ResponseType.OK:
            model, treeiter = treeview.get_selection().get_selected()
            treepath = (
                Gtk.TreePath.new_from_string(
                    model.get_string_from_iter( treeiter ) ) )

#TODO Remove group if no more scripts.
            while True:
                has_previous = treepath.prev()
                if has_previous:
                    treeview.get_selection().select_path( treepath )
                    model, treeiter = treeview.get_selection().get_selected()

                    if model[ treeiter ][ 0 ] is None:
                        print( model[ treeiter ][ 8 ] + "\t" + model[ treeiter ][ 1 ] )

                    else:
                        print( model[ treeiter ][ 8 ] + "\t" + model[ treeiter ][ 1 ] )

                else:
                    break

            if True:
                return

            has_previous = treepath.prev()  #TODO I think need to keep looking for a prev until we hit a script (not a group or false).
            model.remove( treeiter )
            if has_previous:
                treeview.get_selection().select_path( treepath )
                treeview.set_cursor( treepath, None, False )

#TODO What to select, if anything, in the background scripts treeview?
# Maybe don't need to worry...seems focus is on the icon textentry field.

            else:
                button_remove.set_sensitive( False )
                button_copy.set_sensitive( False )

#TODO Need to refresh/update text entry for icon
            # self.update_indicator_textentry(
            #     textentry, self._create_key( group, name ), "" )


#TODO Delete below I hope.


        # model, treeiter = scripts_treeview.get_selection().get_selected()
        # if treeiter is None:
        #     self.show_dialog_ok(
        #         scripts_treeview,
        #         _( "No script has been selected for removal." ) )
        #
        # else:

        # group, name = self._get_selected_script( scripts_treeview )
        # if group and name:
        #     response = (
        #         self.show_dialog_ok_cancel(
        #             scripts_treeview,
        #             _( "Remove the selected script?" ) ) )
        #
        #     if response == Gtk.ResponseType.OK:
        #         pass #TODO Remove from store
            #TODO Select the previous script or first script.
                # i = 0
                # for script in scripts:
                #     if script.get_group() == group and script.get_name() == name:
                #         del scripts[ i ]
                #         self.populate_treestore_and_select_script(
                #             scripts_treeview,
                #             background_scripts_treeview,
                #             scripts,
                #             "",
                #             "" )
                #
                #         self.update_indicator_textentry(
                #             textentry, self._create_key( group, name ), "" )
                #
                #         break
                #
                #     i += 1

        # else:
        #     self.show_dialog_ok(
        #         scripts_treeview,
        #         _( "No script has been selected for removal." ) )


#TODO Implement
# Check for when we click ADD and a group is selected...
# is this the group we select by default to add in the new script?
# Or just select the first group?
#
# If a script is selected, as above, use that script's group as the default group?
    def on_add(
        self,
        button,
        treeview,
        button_copy,
        button_remove ):

        if True:
            print( "add")
            return

        # self._add_edit_script(
        #     None, scripts, scripts_treeview, background_scripts_treeview )
        self.on_script_edit(
            treeview,
            None,
            None,
            None )

#TODO Need something like this to enable the remove/copy buttons
        # if len( treeview.get_model() ) > 0:
        #     button_remove.set_sensitive( True )




#TODO Delete
#     def on_script_double_click(
#         self,
#         scripts_treeview,
#         treepath,
#         treeviewcolumn,
#         background_scripts_treeview,
#         textentry,
#         scripts ):
#
# #TODO See if feasible that on_script_edit is called directly after a double click...
# #... implies the other functions which call on_script_edit will have to deal with this.
#         self.on_script_edit(
#             None,
#             scripts,
#             scripts_treeview,
#             background_scripts_treeview,
#             textentry )


#     def on_script_edit_DELETE(
#         self,
#
#         scripts_treeview,
#         treepath,
#         treeviewcolumn,
#         background_scripts_treeview,
#         textentry,
#         scripts ):
#
#
# #TODO Original signature which hopefully can go.
#         # button,
#         # scripts,
#         # scripts_treeview,
#         # background_scripts_treeview,
#         # textentry ):
#
#         if True:
#             print( "edit")
#             return
#
#         group, name = self._get_selected_script( scripts_treeview )
#         self.on_script_edit(
#             self.get_script( scripts, group, name ),
#             scripts,
#             scripts_treeview,
#             background_scripts_treeview )
#
#
#
#         # group, name = self._get_selected_script( scripts_treeview )
#         # if group and name:  #TODO Surely don't need to do this if we're double clicking.
#         #     the_script = self.get_script( scripts, group, name )
#         #     edited_script = (
#         #         self._add_edit_script(
#         #             the_script,
#         #             scripts, scripts_treeview,
#         #             background_scripts_treeview ) )
#
# #TODO Copy/move this to function below but only when edit
#             # if edited_script:
#             #     if isinstance( the_script, Background ) and isinstance( edited_script, NonBackground ):
#             #         old_tag = self._create_key( group, name )
#             #         self.update_indicator_textentry( textentry, old_tag, "" )
#             #
#             #     if not( group == edited_script.get_group() and name == edited_script.get_name() ):
#             #         old_tag = self._create_key( group, name )
#             #         new_tag = self._create_key( edited_script.get_group(), edited_script.get_name() )
#             #         self.update_indicator_textentry(
#             #             textentry, old_tag, new_tag )


    def on_edit(
        self,
        treeview,
        treepath,
        treeviewcolumn,
        textentry ):

        model, treeiter = treeview.get_selection().get_selected()
        group = (
            model.get_value(
                treeiter,
                IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ) )

        name = (
            model.get_value(
                treeiter,
                IndicatorScriptRunner.COLUMN_MODEL_NAME ) )

        if name is None:
            self._on_edit_group( group, treeview, textentry )

        else:
            self._on_edit_script( group, name, treeview, textentry )


    def _on_edit_group(
        self,
        group,
        treeview,
        textentry ): #TODO Handle textentry

        model, treeiter = treeview.get_selection().get_selected()

        groups = [
            row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
            for row in model ]

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

#TODO Check this code!
                model.set_value(
                    treeiter,
                    IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN,
                    group_ )

                model.set_value(
                    treeiter,
                    IndicatorScriptRunner.COLUMN_MODEL_GROUP,
                    group_ )

                iter_scripts = model.iter_children( treeiter )
                while iter_scripts:
                    model.set_value(
                        iter_scripts,
                        IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN,
                        group_ )

                    iter_scripts = model.iter_next( iter_scripts )

                treepath = (
                    Gtk.TreePath.new_from_string(
                        model.get_string_from_iter(
                        self.get_iter_to_group( group_, model ) ) ) )

                treeview.expand_to_path( treepath )
                treeview.get_selection().select_path( treepath )
                treeview.set_cursor( treepath, None, False )

                break

        dialog.destroy()


    def _on_edit_script(
        self,
        treeview,
        textentry ):

        group, name = self._get_selected_script( treeview )  #TODO This won't work if we are adding first script ever.
        add = name is None

        model = treeview.get_model()

        groups = [
            row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
            for row in model ]

        index = 0
        if not add:
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

        iter_to_script = self.get_iter_to_script( group, name, model )

        command_text_view = (
            self.create_textview(
                text =
                    "" if add else
                    model.get_value(
                        iter_to_script,
                        IndicatorScriptRunner.COLUMN_MODEL_COMMAND_HIDDEN ),
                tooltip_text = _( "The terminal script/command, along with any arguments." ) ) )

        grid.attach(
            self.create_box(
                ( ( self.create_scrolledwindow( command_text_view ), True ), ) ),
            0, 3, 1, 10 )

        sound_checkbutton = (
            self.create_checkbutton(
                _( "Play sound" ),
                tooltip_text = _(
                    "For non-background scripts, play a sound\n" +
                    "on script completion.\n\n" +
                    "For background scripts, play a sound\n" +
                    "only if the script returns non-empty text." ),
                active =
                    False if add else
                    model.get_value(
                        iter_to_script,
                        IndicatorScriptRunner.COLUMN_MODEL_SOUND ) ) )

        grid.attach( sound_checkbutton, 0, 13, 1, 1 )

        notification_checkbutton = (
            self.create_checkbutton(
                _( "Show notification" ),
                tooltip_text = _(
                    "For non-background scripts, show a\n" +
                    "notification on script completion.\n\n" +
                    "For background scripts, show a notification\n" +
                    "only if the script returns non-empty text." ),
                active =
                    False if add else
                    model.get_value(
                        iter_to_script,
                        IndicatorScriptRunner.COLUMN_MODEL_NOTIFICATION ) ) )

        grid.attach( notification_checkbutton, 0, 14, 1, 1 )

        is_background = (
            model.get_value(
                iter_to_script,
                IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ) )

        script_non_background_radio = (
            self.create_radiobutton(
                None,
                _( "Non-background" ),
                tooltip_text = _(
                    "Non-background scripts are displayed\n" +
                    "in the menu and run when the user\n" +
                    "clicks on the corresponding menu item." ),
                active = True if add else not is_background ) )

        grid.attach( script_non_background_radio, 0, 15, 1, 1 )

        terminal_checkbutton = (
            self.create_checkbutton(
                _( "Leave terminal open" ),
                tooltip_text = _( "Leave the terminal open on script completion." ),
                sensitive = True if add else not is_background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active =
                    False if add else
                    not is_background
                    and
                    model.get_value(
                        iter_to_script,
                        IndicatorScriptRunner.COLUMN_MODEL_TERMINAL ) ) )

        grid.attach( terminal_checkbutton, 0, 16, 1, 1 )

        default_script_checkbutton = (
            self.create_checkbutton(
                _( "Default script" ),
                tooltip_text = _(
                    "One script may be set as default\n" +
                    "which is run on a middle mouse\n" +
                    "click of the indicator icon.\n\n" +
                    "Not supported on all desktops." ),
                sensitive = True if add else not is_background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active =
                    False if add else
                    not is_background
                    and
                    model.get_value(
                        iter_to_script,
                        IndicatorScriptRunner.COLUMN_MODEL_DEFAULT_HIDDEN ) ) )

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
                active = False if add else is_background ) )

        grid.attach( script_background_radio, 0, 18, 1, 1 )

        interval_spinner = (
            self.create_spinbutton(
                model.get_value(
                    iter_to_script,
                    IndicatorScriptRunner.COLUMN_MODEL_INTERVAL )
                if is_background
                else
                60,
                1,
                10000,
                page_increment = 100,
                tooltip_text = _( "Interval, in minutes, between runs." ) ) )

        label_and_interval_spinner_box = (
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Interval" ) ), False ),
                    ( interval_spinner, False ) ),
                sensitive = False if add else is_background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT * 1.4 ) ) # Approximate alignment with the checkboxes above.

        grid.attach( label_and_interval_spinner_box, 0, 19, 1, 1 )

        force_update_checkbutton = (
            self.create_checkbutton(
                _( "Force update" ),
                tooltip_text = _(
                    "If the script returns non-empty text\n" +
                    "on its update, the script will run\n" +
                    "on the next update of ANY script." ),
                sensitive = True if add else is_background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active =
                    False if add
                    else
                        is_background
                        and
                        model.get_value(
                            iter_to_script,
                            IndicatorScriptRunner.COLUMN_MODEL_FORCE_UPDATE ) ) )

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

        new_script = None
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

                script_exists = self.get_iter_to_script( group_, name_, model )  #TODO Check for when None and not None.
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
                    model.remove( iter_to_script )

                is_background_and_default = (
                    script_non_background_radio.get_active()
                    and
                    default_script_checkbutton.get_active() )

                if is_background_and_default:

                    def remove_default( model, treepath, iter ):
                        is_background = (
                            model.get_value(
                                iter,
                                IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ) )

                        if is_background:
                            model.set_value(
                                iter,
                                IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND,
                                False )


                    model.foreach( remove_default )

                if group_ not in groups:
                    row = [ group_, group_, None, None, None, None, None, None, None, None, None ]
                    parent = model.append( None, row )

                else:
                    parent = self.get_iter_to_group( group_, model )

#TODO Can this code be put into a function to be
# called by copy_group and copy_script and here?
                model.append(
                    parent,
                    [
                        group_,
                        None,
                        name_,
                        self.get_textview_text( command_text_view ).strip(),
                        str( sound_checkbutton.get_active() ),
                        str( notification_checkbutton.get_active() ),
                        str( script_background_radio.get_active() ),
                        str( terminal_checkbutton.get_active() )
                        if script_non_background_radio.get_active() else None,
                        str( default_script_checkbutton.get_active() )
                        if script_non_background_radio.get_active() else None,
                        str( interval_spinner.get_value_as_int() )
                        if script_background_radio.get_active() else None,
                        str( force_update_checkbutton.get_active() )
                        if script_background_radio.get_active() else None ] )

                treepath = (
                    Gtk.TreePath.new_from_string(
                        model.get_string_from_iter(
                            self.get_iter_to_script( group_, name_, model ) ) ) )

                treeview.expand_to_path( treepath )
                treeview.get_selection().select_path( treepath )
                treeview.set_cursor( treepath, None, False )
#TODO Ensure that one of the lines above selects the script and
# that in turn shows the command (same command as original script).

            break

        dialog.destroy()
        return new_script


    # def on_script_editORIGINAL(
    #     self,
    #     scripts_treeview,
    #     treepath,
    #     treeviewcolumn,
    #     background_scripts_treeview,
    #     textentry,
    #     scripts ):
    #
    #     script = None
    #     group, name = self._get_selected_script( scripts_treeview )
    #     if group and name:
    #         script = self.get_script( scripts, group, name )
    #
    #     groups = sorted( self.get_scripts_by_group( scripts ).keys(), key = str.lower )
    #
    #     add = script is None
    #     if add:
    #         index = 0
    #         model, treeiter = scripts_treeview.get_selection().get_selected()
    #         if treeiter:
    #             group = model[ treeiter ][ IndicatorScriptRunner.COLUMN_MODEL_GROUP ]
    #             if group is None: # A script is selected, so find the parent group.
    #                 parent = scripts_treeview.get_model().iter_parent( treeiter )
    #                 group = model[ parent ][ IndicatorScriptRunner.COLUMN_MODEL_GROUP ]
    #
    #             index = groups.index( group )
    #
    #     else:
    #         index = groups.index( script.get_group() )
    #
    #     group_combo = (
    #         self.create_comboboxtext(
    #             groups,
    #             tooltip_text = _(
    #                 "The group to which the script belongs.\n\n" +
    #                 "Choose an existing group or enter a new one." ),
    #             active = index,
    #             editable = True ) )
    #
    #     grid = self.create_grid()
    #
    #     grid.attach(
    #         self.create_box(
    #             (
    #                 ( Gtk.Label.new( _( "Group" ) ), False ),
    #                 ( group_combo, True ) ) ),
    #         0, 0, 1, 1 )
    #
    #     name_entry = (
    #         self.create_entry(
    #             "" if add else script.get_name(),
    #             tooltip_text = _( "The name of the script." ) ) )
    #
    #     grid.attach(
    #         self.create_box(
    #             (
    #                 ( Gtk.Label.new( _( "Name" ) ), False ),
    #                 ( name_entry, True ) ),
    #             margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
    #         0, 1, 1, 1 )
    #
    #     grid.attach(
    #         self.create_box(
    #             ( ( Gtk.Label.new( _( "Command" ) ), False ), ),
    #             margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
    #         0, 2, 1, 1 )
    #
    #     command_text_view = (
    #         self.create_textview(
    #             text = "" if add else script.get_command(),
    #             tooltip_text = _( "The terminal script/command, along with any arguments." ) ) )
    #
    #     grid.attach(
    #         self.create_box(
    #             ( ( self.create_scrolledwindow( command_text_view ), True ), ) ),
    #         0, 3, 1, 10 )
    #
    #     sound_checkbutton = (
    #         self.create_checkbutton(
    #             _( "Play sound" ),
    #             tooltip_text = _(
    #                 "For non-background scripts, play a sound\n" +
    #                 "on script completion.\n\n" +
    #                 "For background scripts, play a sound\n" +
    #                 "only if the script returns non-empty text." ),
    #             active = False if add else script.get_play_sound() ) )
    #
    #     grid.attach( sound_checkbutton, 0, 13, 1, 1 )
    #
    #     notification_checkbutton = (
    #         self.create_checkbutton(
    #             _( "Show notification" ),
    #             tooltip_text = _(
    #                 "For non-background scripts, show a\n" +
    #                 "notification on script completion.\n\n" +
    #                 "For background scripts, show a notification\n" +
    #                 "only if the script returns non-empty text." ),
    #             active = False if add else script.get_show_notification() ) )
    #
    #     grid.attach( notification_checkbutton, 0, 14, 1, 1 )
    #
    #     script_non_background_radio = (
    #         self.create_radiobutton(
    #             None,
    #             _( "Non-background" ),
    #             tooltip_text = _(
    #                 "Non-background scripts are displayed\n" +
    #                 "in the menu and run when the user\n" +
    #                 "clicks on the corresponding menu item." ),
    #             active = True if add else isinstance( script, NonBackground ) ) )
    #
    #     grid.attach( script_non_background_radio, 0, 15, 1, 1 )
    #
    #     terminal_checkbutton = (
    #         self.create_checkbutton(
    #             _( "Leave terminal open" ),
    #             tooltip_text = _( "Leave the terminal open on script completion." ),
    #             sensitive = True if add else isinstance( script, NonBackground ),
    #             margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
    #             active = False if add else isinstance( script, NonBackground ) and script.get_terminal_open() ) )
    #
    #     grid.attach( terminal_checkbutton, 0, 16, 1, 1 )
    #
    #     default_script_checkbutton = (
    #         self.create_checkbutton(
    #             _( "Default script" ),
    #             tooltip_text = _(
    #                 "One script may be set as default\n" +
    #                 "which is run on a middle mouse\n" +
    #                 "click of the indicator icon.\n\n" +
    #                 "Not supported on all desktops." ),
    #             sensitive = True if add else isinstance( script, NonBackground ),
    #             margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
    #             active = False if add else isinstance( script, NonBackground ) and script.get_default() ) )
    #
    #     grid.attach( default_script_checkbutton, 0, 17, 1, 1 )
    #
    #     script_background_radio = (
    #         self.create_radiobutton(
    #             script_non_background_radio,
    #             _( "Background" ),
    #             tooltip_text = _(
    #                 "Background scripts automatically run\n" +
    #                 "at the interval specified, but only if\n" +
    #                 "added to the icon text.\n\n" +
    #                 "Any exception which occurs during script\n" +
    #                 "execution will be logged to a file in the\n" +
    #                 "user's home directory and the script tag\n" +
    #                 "will remain in the icon text." ),
    #             active = False if add else isinstance( script, Background ) ) )
    #
    #     grid.attach( script_background_radio, 0, 18, 1, 1 )
    #
    #     interval_spinner = (
    #         self.create_spinbutton(
    #             script.get_interval_in_minutes()
    #             if isinstance( script, Background )
    #             else
    #             60,
    #             1,
    #             10000,
    #             page_increment = 100,
    #             tooltip_text = _( "Interval, in minutes, between runs." ) ) )
    #
    #     label_and_interval_spinner_box = (
    #         self.create_box(
    #             (
    #                 ( Gtk.Label.new( _( "Interval" ) ), False ),
    #                 ( interval_spinner, False ) ),
    #             sensitive = False if add else isinstance( script, Background ),
    #             margin_left = IndicatorBase.INDENT_WIDGET_LEFT * 1.4 ) ) # Approximate alignment with the checkboxes above.
    #
    #     grid.attach( label_and_interval_spinner_box, 0, 19, 1, 1 )
    #
    #     force_update_checkbutton = (
    #         self.create_checkbutton(
    #             _( "Force update" ),
    #             tooltip_text = _(
    #                 "If the script returns non-empty text\n" +
    #                 "on its update, the script will run\n" +
    #                 "on the next update of ANY script." ),
    #             sensitive = True if add else isinstance( script, Background ),
    #             margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
    #             active = False if add else isinstance( script, Background ) and script.get_force_update() ) )
    #
    #     grid.attach( force_update_checkbutton, 0, 20, 1, 1 )
    #
    #     script_non_background_radio.connect(
    #         "toggled",
    #         self.on_radio_or_checkbox,
    #         True,
    #         terminal_checkbutton,
    #         default_script_checkbutton )
    #
    #     script_non_background_radio.connect(
    #         "toggled",
    #         self.on_radio_or_checkbox,
    #         False,
    #         label_and_interval_spinner_box,
    #         force_update_checkbutton )
    #
    #     script_background_radio.connect(
    #         "toggled",
    #         self.on_radio_or_checkbox,
    #         True,
    #         label_and_interval_spinner_box,
    #         force_update_checkbutton )
    #
    #     script_background_radio.connect(
    #         "toggled",
    #         self.on_radio_or_checkbox,
    #         False,
    #         terminal_checkbutton,
    #         default_script_checkbutton )
    #
    #     dialog = (
    #         self.create_dialog(
    #             scripts_treeview,
    #             _( "Add Script" ) if add else _( "Edit Script" ),
    #             content_widget = grid ) )
    #
    #     new_script = None
    #     while True:
    #         dialog.show_all()
    #         if dialog.run() == Gtk.ResponseType.OK:
    #             if group_combo.get_active_text().strip() == "":
    #                 self.show_dialog_ok(
    #                     dialog, _( "The group cannot be empty." ) )
    #
    #                 group_combo.grab_focus()
    #                 continue
    #
    #             if name_entry.get_text().strip() == "":
    #                 self.show_dialog_ok(
    #                     dialog, _( "The name cannot be empty." ) )
    #
    #                 name_entry.grab_focus()
    #                 continue
    #
    #             if self.get_textview_text( command_text_view ).strip() == "":
    #                 self.show_dialog_ok(
    #                     dialog, _( "The command cannot be empty." ) )
    #
    #                 command_text_view.grab_focus()
    #                 continue
    #
    #             # Check for duplicates...
    #             #    For an add, find an existing script with the same group/name.
    #             #    For an edit, the group and/or name must change (and then match with an existing script other than the original).
    #             script_of_same_name_and_group_exists = (
    #                 self.get_script(
    #                     scripts,
    #                     group_combo.get_active_text().strip(),
    #                     name_entry.get_text().strip() ) is not None )
    #
    #             edited_script_group_or_name_different = (
    #                 not add and
    #                 (
    #                     group_combo.get_active_text().strip() != script.get_group() or
    #                     name_entry.get_text().strip() != script.get_name() ) )
    #
    #             if ( add or edited_script_group_or_name_different ) and script_of_same_name_and_group_exists:
    #                 self.show_dialog_ok( dialog, _( "A script of the same group and name already exists." ) )
    #                 group_combo.grab_focus()
    #                 continue
    #
    #             # For an edit, remove the original script...
    #             if not add:
    #                 i = 0
    #                 for skript in scripts:
    #                     if script.get_group() == skript.get_group() and script.get_name() == skript.get_name():
    #                         break
    #
    #                     i += 1
    #
    #                 del scripts[ i ]
    #
    #             # If this script is marked as default (and is non-background),
    #             # check for an existing default script and if found, undefault it...
    #             if script_non_background_radio.get_active() and default_script_checkbutton.get_active():
    #                 i = 0
    #                 for skript in scripts:
    #                     if isinstance( skript, NonBackground ) and skript.get_default():
    #                         undefault_script = NonBackground(
    #                             skript.get_group(),
    #                             skript.get_name(),
    #                             skript.get_command(),
    #                             skript.get_play_sound(),
    #                             skript.get_show_notification(),
    #                             skript.get_terminal_open(),
    #                             False )
    #
    #                         del scripts[ i ]
    #                         scripts.append( undefault_script )
    #                         break
    #
    #                     i += 1
    #
    #             # Create new script (add or edit) and add to scripts...
    #             if script_background_radio.get_active():
    #                 new_script = Background(
    #                     group_combo.get_active_text().strip(),
    #                     name_entry.get_text().strip(),
    #                     self.get_textview_text( command_text_view ).strip(),
    #                     sound_checkbutton.get_active(),
    #                     notification_checkbutton.get_active(),
    #                     interval_spinner.get_value_as_int(),
    #                     force_update_checkbutton.get_active() )
    #
    #             else:
    #                 new_script = NonBackground(
    #                     group_combo.get_active_text().strip(),
    #                     name_entry.get_text().strip(),
    #                     self.get_textview_text( command_text_view ).strip(),
    #                     sound_checkbutton.get_active(),
    #                     notification_checkbutton.get_active(),
    #                     terminal_checkbutton.get_active(),
    #                     default_script_checkbutton.get_active() )
    #
    #             scripts.append( new_script )
    #
    #             self.populate_treestore_and_select_script(
    #                 scripts_treeview,
    #                 background_scripts_treeview,
    #                 scripts,
    #                 new_script.get_group(),
    #                 new_script.get_name() )
    #
    #         break
    #
    #     dialog.destroy()
    #     return new_script


#TODO Who calls this and why/when?
    def get_script(
        self,
        scripts,
        group,
        name ):

        the_script = None
        for script in scripts:
            if script.get_group() == group and script.get_name() == name:
                the_script = script
                break

        return the_script


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


    def _get_selected_script(
        self,
        treeview ):
        '''
        Returns the group and name of the currently selected script.
        Must ONLY be called when at least one script is present.
        '''

        model, treeiter = treeview.get_selection().get_selected()
        row = model[ treeiter ]
        group = row[ IndicatorScriptRunner.COLUMN_MODEL_GROUP_HIDDEN ]
        name = row[ IndicatorScriptRunner.COLUMN_MODEL_NAME ]

        return group, name


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


#TODO Test to see if this returns a boolean...used to not have ( ).
    def is_background_script_in_indicator_text(
        self,
        script ):

        return (
            '[' + self._create_key( script.get_group(), script.get_name() ) + ']'
            in self.indicator_text )


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
