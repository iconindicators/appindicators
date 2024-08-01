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


#TODO For RAM/HDD on laptop:
#    notify-send "System Usage:" "RAM: $( free | grep Mem | awk ' { printf "%.0f\n", $3/$2*100 } ' )%  HDD: $( df -h /dev/sda1 | grep sda1 | awk ' { print $5 } '  )"
#
# See if it works also on desktop.
#
# Only flashes up a console on the desktop (same as laptop I think)...
# and does not show a notification...
#
# Original...
# notify-send \"System Usage:\" \"RAM: $(free | awk '\\''/Mem/ { printf \"%.0f\\n\", $3/$2*100 }'\\'')%    HDD: $(df -h /dev/sda2 | awk '\\''/sda2/ { print $5 } '\\'' ) \"
#
# New...
# notify-send \"System Usage:\" \"RAM: $( free | grep Mem | awk ' { printf \"%.0f\\n\", $3/$2*100 } ' )%  HDD: $( df -h /dev/sda1 | grep sda1 | awk ' { print $5 } '  )\"


#TODO Got this on laptop:
#
# Script runner log for check Hotmail:
#
# 2024-07-26 23:22:10,916 - root - ERROR - Command 'python3 /home/bernard/Programming/checkHotmail.py' returned non-zero exit status 1.
# 2024-07-26 23:22:10,919 - root - ERROR - b'Traceback (most recent call last):\n  File "/home/bernard/Programming/checkHotmail.py", line 72, in <module>\n    connection.logout()\n    ^^^^^^^^^^\nNameError: name \'connection\' is not defined\n'


#TODO On laptop
# With a foreground script, checking "leave terminal open"
# does not leave terminal open (on laptop Debian 12)
# Same on desktop...at least for the ram/hdd script/command.


#TODO
# Got this in the error log on the laptop...
# don't know if caused when there was no internet connection.
#
'''
2024-07-21 18:40:28,274 - root - ERROR - Command 'python3 /home/bernard/Programming/checkHotmail.py' returned non-zero exit status 1.
2024-07-21 18:40:28,300 - root - ERROR - b'Traceback (most recent call last):\n  File "/home/bernard/Programming/checkHotmail.py", line 72, in <module>\n    connection.logout()\n    ^^^^^^^^^^\nNameError: name \'connection\' is not defined\n'
'''


# Application indicator to run a terminal command or script from an indicator.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import concurrent.futures
import copy
import datetime
import gi
import math

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

gi.require_version( "Pango", "1.0" )
from gi.repository import Pango

from threading import Thread

from script import Background, NonBackground


class IndicatorScriptRunner( IndicatorBase ):
    # Unused within the indicator; used by build_wheel.py when building the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Script Runner" )

    CONFIG_HIDE_GROUPS = "hideGroups"
    CONFIG_INDICATOR_TEXT = "indicatorText"
    CONFIG_INDICATOR_TEXT_SEPARATOR = "indicatorTextSeparator"
    CONFIG_SCRIPTS_BACKGROUND = "scriptsBackground"
    CONFIG_SCRIPTS_NON_BACKGROUND = "scriptsNonBackground"
    CONFIG_SEND_COMMAND_TO_LOG = "sendCommandToLog"
    CONFIG_SHOW_SCRIPTS_IN_SUBMENUS = "showScriptsInSubmenus"

    COMMAND_NOTIFY_TAG_SCRIPT_NAME = "[SCRIPT_NAME]"
    COMMAND_NOTIFY_TAG_SCRIPT_RESULT = "[SCRIPT_RESULT]"
    COMMAND_SOUND = "paplay /usr/share/sounds/freedesktop/stereo/complete.oga"

    COLUMN_MODEL_GROUP = 0 # Group name when displaying a group; empty when displaying a script.
    COLUMN_MODEL_NAME = 1 # Script name.
    COLUMN_MODEL_SOUND = 2 # Icon name for the APPLY icon; None otherwise.
    COLUMN_MODEL_NOTIFICATION = 3 # Icon name for the APPLY icon; None otherwise.
    COLUMN_MODEL_BACKGROUND = 4 # Icon name for the APPLY icon; None otherwise.
    COLUMN_MODEL_TERMINAL = 5 # Icon name for the APPLY icon; None otherwise.
    COLUMN_MODEL_INTERVAL = 6 # Numeric amount as a string.
    COLUMN_MODEL_FORCE_UPDATE = 7 # Icon name for the APPLY icon; None otherwise.

    COLUMN_VIEW_SCRIPTS_ALL_GROUP = 0 # Group name when displaying a group; empty when displaying a script.
    COLUMN_VIEW_SCRIPTS_ALL_NAME = 1 # Script name.
    COLUMN_VIEW_SCRIPTS_ALL_SOUND = 2 # Icon name for the APPLY icon; None otherwise.
    COLUMN_VIEW_SCRIPTS_ALL_NOTIFICATION = 3 # Icon name for the APPLY icon; None otherwise.
    COLUMN_VIEW_SCRIPTS_ALL_BACKGROUND = 4 # Icon name for the APPLY icon; None otherwise.
    COLUMN_VIEW_SCRIPTS_ALL_TERMINAL = 5 # Icon name for the APPLY icon; None otherwise.
    COLUMN_VIEW_SCRIPTS_ALL_INTERVAL = 6 # Numeric amount as a string.
    COLUMN_VIEW_SCRIPTS_ALL_FORCE_UPDATE = 7 # Icon name for the APPLY icon; None otherwise.

    COLUMN_VIEW_SCRIPTS_BACKGROUND_GROUP = 0 # Group name when displaying a group; empty when displaying a script.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_NAME = 1 # Script name.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_SOUND = 2 # Icon name for the APPLY icon; None otherwise.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_NOTIFICATION = 3 # Icon name for the APPLY icon; None otherwise.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_INTERVAL = 4 # Numeric amount as a string.
    COLUMN_VIEW_SCRIPTS_BACKGROUND_FORCE_UPDATE = 5 # Icon name for the APPLY icon; None otherwise.

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

        self.command_notify_background = \
            "notify-send -i " + self.get_icon_name() + \
            " \"" + IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" " + \
            "\"" + IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_RESULT + "\""

        self.command_notify_nonbackground = \
            "notify-send -i " + self.get_icon_name() + \
            " \"" + IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" " + \
            "\"" + _( "...has completed." ) + "\""


    def update( self, menu ):
        today = datetime.datetime.now()
        self.update_menu( menu )
        self.update_background_scripts( today )
        self.set_label( self.process_tags() )

        # Calculate next update...
        next_update = today + datetime.timedelta( hours = 100 ) # Set an update time well into the future.
        for script in self.scripts:
            key = self.__create_key( script.get_group(), script.get_name() )

            if type( script ) is Background and \
               self.background_script_next_update_time[ key ] < next_update and \
               self.is_background_script_in_indicator_text( script ):
                next_update = self.background_script_next_update_time[ key ]

        next_update_in_seconds = int( math.ceil( ( next_update - today ).total_seconds() ) )
        return 60 if next_update_in_seconds < 60 else next_update_in_seconds


    def update_menu( self, menu ):
        if self.show_scripts_in_submenus:
            scripts_by_group = self.get_scripts_by_group( self.scripts, True, False )
            for group in sorted( scripts_by_group.keys(), key = str.lower ):
                submenu = Gtk.Menu()
                self.create_and_append_menuitem( menu, group ).set_submenu( submenu )
                self.add_scripts_to_menu( scripts_by_group[ group ], submenu, indent = ( 1, 0 ) )

        else:
            if self.hide_groups:
                for script in sorted( self.scripts, key = lambda script: script.get_name().lower() ):
                    if type( script ) is NonBackground:
                        self.add_scripts_to_menu( [ script ], menu, indent = ( 0, 0 ) )

            else:
                scripts_by_group = self.get_scripts_by_group( self.scripts, True, False )
                for group in sorted( scripts_by_group.keys(), key = str.lower ):
                    self.create_and_append_menuitem( menu, group )
                    self.add_scripts_to_menu( scripts_by_group[ group ], menu, indent = ( 1, 1 ) )


    def add_scripts_to_menu( self, scripts, menu, indent ):
        scripts.sort( key = lambda script: script.get_name().lower() )
        for script in scripts:
            menuitem = \
                self.create_and_append_menuitem(
                    menu,
                    script.get_name(),
                    activate_functionandarguments = (
                        lambda menuitem, script = script:
                            self.on_script_menuitem( script ), ), # Note script = script to handle lambda late binding.
                    indent = indent )

            if script.get_default():
                self.set_secondary_activate_target( menuitem )


    def on_script_menuitem( self, script ):
        terminal, terminal_execution_flag = self.get_terminal_and_execution_flag()
        if terminal is None:
            message = _( "Cannot run script as no terminal and/or terminal execution flag found; please install gnome-terminal." )
            self.get_logging().error( message )
            self.show_notification( "Cannot run script", message )

        elif self.is_terminal_qterminal( terminal ):
            # As a result of this issue
            #    https://github.com/lxqt/qterminal/issues/335
            # the default terminal in Lubuntu (qterminal) fails to parse argument.
            # Although a fix has been made, it is unlikely the repository will be updated any time soon.
            # So the quickest/easiest workaround is to install gnome-terminal.
            message = _( "Cannot run script as qterminal incorrectly parses arguments; please install gnome-terminal instead." )
            self.get_logging().error( message )
            self.show_notification( "Cannot run script", message )

        else:
            command = terminal + " " + terminal_execution_flag + " ${SHELL} -c '"
            command += script.get_command()

            if script.get_show_notification():
                notification = \
                    self.command_notify_nonbackground.replace(
                        IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME,
                        script.get_name() )

                command += "; " + notification

            if script.get_play_sound():
                command += "; " + IndicatorScriptRunner.COMMAND_SOUND

            if script.get_terminal_open():
                command += "; cd $HOME; ${SHELL}"

            command += "'"

            if self.send_command_to_log:
                self.get_logging().debug( script.get_group() + " | " + script.get_name() + ": " + command )

            Thread( target = self.process_call, args = ( command, ) ).start()


    def update_background_scripts( self, now ):
        if True: return # TODO Remove
        background_scripts_to_execute = [ ]
        for script in self.scripts:
            if type( script ) is Background and self.is_background_script_in_indicator_text( script ):
                # Script is background AND present in the indicator text, so is a potential candidate to be updated...
                key = self.__create_key( script.get_group(), script.get_name() )
                if ( self.background_script_next_update_time[ key ] < now ) or \
                   ( script.get_force_update() and self.background_script_results[ key ] ):
                    background_scripts_to_execute.append( script )

        # Based on example from
        #    https://docs.python.org/3.6/library/concurrent.futures.html#threadpoolexecutor-example
        with concurrent.futures.ThreadPoolExecutor( max_workers = 5 ) as executor:
            future_to_script = {
                executor.submit(
                    self.__update_background_script,
                    script,
                    now ): script for script in background_scripts_to_execute }

            for future in concurrent.futures.as_completed( future_to_script ):
                script = future_to_script[ future ]
                key = future.result()
                command_result = self.background_script_results[ key ]

                if script.get_play_sound() and command_result:
                    self.process_call( IndicatorScriptRunner.COMMAND_SOUND )

                if script.get_show_notification() and command_result:
                    notification_command = self.command_notify_background
                    notification_command = \
                        notification_command.replace(
                            IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME,
                            script.get_name().replace( '-', '\\-' ) )

                    notification_command = \
                        notification_command.replace(
                            IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_RESULT,
                            command_result.replace( '-', '\\-' ) )

                    self.process_call( notification_command )


    def __update_background_script( self, script, now ):
        if self.send_command_to_log:
            self.get_logging().debug(
                script.get_group() + " | " + script.get_name() + ": " + script.get_command() )

        command_result = self.process_get( script.get_command(), log_non_zero_error_code = True ) # When calling a user script, always want to log out any errors (from non-zero return codes).
        key = self.__create_key( script.get_group(), script.get_name() )
        self.background_script_results[ key ] = command_result
        self.background_script_next_update_time[ key ] = \
            now + datetime.timedelta( minutes = script.get_interval_in_minutes() )

        return key


    def process_tags( self ):
        indicator_text_processed = self.indicator_text
        for script in self.scripts:
            key = self.__create_key( script.get_group(), script.get_name() )
            if type( script ) is Background and "[" + key + "]" in indicator_text_processed:
                command_result = self.background_script_results[ key ]
                if command_result is None: # Background script failed so leave the tag in place for the user to see.
                    indicator_text_processed = \
                        indicator_text_processed.replace(
                            "[" + key + "]",
                            "[" + key + "]" + self.indicator_text_separator )

                elif command_result: # Non-empty result so replace tag and tack on a separator.
                    indicator_text_processed = \
                        indicator_text_processed.replace(
                            "[" + key + "]",
                            command_result + self.indicator_text_separator )

                else: # No result, so remove tag but no need for separator.
                    indicator_text_processed = \
                        indicator_text_processed.replace(
                            "[" + key + "]",
                            command_result )

        return indicator_text_processed[ 0 : - len( self.indicator_text_separator ) ] # Trim last separator.


    def on_preferences( self, dialog ):
        copy_of_scripts = copy.deepcopy( self.scripts )

        notebook = Gtk.Notebook()

        # Scripts.
        grid = self.create_grid()

        # Define these here so that widgets can connect to handle events.
        indicator_text_entry = \
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
                    "Not supported on all desktops." ) )

        command_text_view = \
            self.create_textview(
                tooltip_text = _( "The terminal script/command, along with any arguments." ),
                editable = False )

        treestore = Gtk.TreeStore( str, str, str, str, str, str, str, str )

        treestore_background_scripts_filter = treestore.filter_new()
        treestore_background_scripts_filter.set_visible_func( self.background_scripts_filter_func, copy_of_scripts )

        background_scripts_treeview, background_scripts_scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                treestore_background_scripts_filter,
                (
                    _( "Group" ),
                    _( "Name" ),
                    _( "Sound" ),
                    _( "Notification" ),
                    _( "Interval" ),
                    _( "Force Update" ) ),
                (
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_GROUP ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_NAME ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_SOUND ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_NOTIFICATION ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_INTERVAL ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_FORCE_UPDATE ) ),
                alignments_columnviewids = (
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_BACKGROUND_SOUND ),
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_BACKGROUND_NOTIFICATION ),
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_BACKGROUND_INTERVAL ),
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_BACKGROUND_FORCE_UPDATE) ),
                tooltip_text = _( "Double click on a script to add to the icon text." ),
                rowactivatedfunctionandarguments = (
                    self.on_background_script_double_click, indicator_text_entry ), )

        renderer_column_name_text = Gtk.CellRendererText()

        scripts_treeview, scripts_scrolledwindow = \
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
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_GROUP ),
                    ( renderer_column_name_text, "text", IndicatorScriptRunner.COLUMN_MODEL_NAME ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_SOUND ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_NOTIFICATION ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_TERMINAL ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_INTERVAL ),
                    ( Gtk.CellRendererText(), "text", IndicatorScriptRunner.COLUMN_MODEL_FORCE_UPDATE ) ),
                alignments_columnviewids = (
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_SOUND ),
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_NOTIFICATION ),
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_BACKGROUND ),
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_TERMINAL ),
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_INTERVAL ),
                    ( 0.5, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_FORCE_UPDATE ) ),
                celldatafunctionandarguments_renderers_columnviewids = (
                    ( ( self.data_function_column_name_renderer, copy_of_scripts ), renderer_column_name_text, IndicatorScriptRunner.COLUMN_VIEW_SCRIPTS_ALL_NAME ), ),
                tooltip_text = _(
                    "Double-click to edit a script.\n\n" +
                    "If an attribute does not apply to a script,\n" +
                    "a dash is displayed.\n\n" +
                    "If a non-background script is checked as\n" +
                    "default, the name will appear in bold." ),
                cursorchangedfunctionandarguments = (
                    self.on_script_selection, command_text_view, copy_of_scripts ),
                rowactivatedfunctionandarguments = (
                    self.on_script_double_click, background_scripts_treeview, indicator_text_entry, copy_of_scripts ), )

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

        box = \
            self.create_buttons_in_box(
                (
                    _( "Add" ),
                    _( "Edit" ),
                    _( "Copy" ),
                    _( "Remove" ) ),
                (
                    _( "Add a new script." ),
                    _( "Edit the selected script." ),
                    _( "Duplicate the selected script." ),
                    _( "Remove the selected script." ) ),
                (
                    ( self.on_script_add, copy_of_scripts, scripts_treeview, background_scripts_treeview ),
                    ( self.on_script_edit, copy_of_scripts, scripts_treeview, background_scripts_treeview, indicator_text_entry ),
                    ( self.on_script_copy, copy_of_scripts, scripts_treeview, background_scripts_treeview ),
                    ( self.on_script_remove, copy_of_scripts, scripts_treeview, background_scripts_treeview, indicator_text_entry ) ) )

        box.set_margin_top( 10 )
        grid.attach( box, 0, 31, 1, 1 )

        send_command_to_log_checkbutton = \
            self.create_checkbutton(
                _( "Send command to log" ),
                tooltip_text = _(
                    "When a script is run,\n" +
                    "send the command to the log\n" +
                    "(located in your home directory)." ),
                active = self.send_command_to_log )

        grid.attach( send_command_to_log_checkbutton, 0, 32, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Scripts" ) ) )

        # Menu settings.
        grid = self.create_grid()

        radio_show_scripts_submenu = \
            self.create_radiobutton(
                None,
                _( "Show non-background scripts in sub-menus" ),
                active = self.show_scripts_in_submenus )

        grid.attach( radio_show_scripts_submenu, 0, 0, 1, 1 )

        radio_show_scripts_indented = \
            self.create_radiobutton(
                radio_show_scripts_submenu,
                _( "Show non-background scripts indented by group" ),
                active = not self.show_scripts_in_submenus )

        grid.attach( radio_show_scripts_indented, 0, 1, 1, 1 )

        hide_groups_checkbutton = \
            self.create_checkbutton(
                _( "Hide groups" ),
                tooltip_text = _(
                    "If checked, only script names are displayed.\n" +
                    "Otherwise, script names are indented\n" +
                    "within their respective group." ),
                sensitive = not self.show_scripts_in_submenus,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.hide_groups )

        radio_show_scripts_indented.connect( "toggled", self.on_radio_or_checkbox, True, hide_groups_checkbutton )

        grid.attach( hide_groups_checkbutton, 0, 2, 1, 1 )

        autostart_checkbox, delay_spinner, box = self.create_autostart_checkbox_and_delay_spinner()
        box.set_margin_top( 30 ) # Put some distance from the prior section.
        grid.attach( box, 0, 3, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )

        # Icon text settings.
        grid = self.create_grid()

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Icon Text" ) ), False ),
                    ( indicator_text_entry, True ) ) ),
            0, 0, 1, 1 )

        indicator_text_separator_entry = \
            self.create_entry(
                self.indicator_text_separator,
                tooltip_text = _( "The separator will be added between script tags." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Separator" ) ), False ),
                    ( indicator_text_separator_entry, False ) ) ),
            0, 1, 1, 1 )

        self.populate_treestore_and_select_script(
            scripts_treeview, background_scripts_treeview, copy_of_scripts, "", "" )

        grid.attach( background_scripts_scrolledwindow, 0, 2, 1, 20 )

        notebook.append_page( grid, Gtk.Label.new( _( "Icon" ) ) )

        # Workaround for odd focus behaviour; in the Preferences dialog, when
        # switching tabs, the TextEntry on the third tab would have the focus and
        # highlight the text.  If the user hits the space bar (or any regular key),
        # the text would be overwritten.
        # Refer to:
        #    https://stackoverflow.com/questions/68931638/remove-focus-from-textentry
        #    https://gitlab.gnome.org/GNOME/gtk/-/issues/4249
        notebook.connect( "switch-page", lambda notebook, page, page_number: notebook.grab_focus() )
        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.scripts = copy_of_scripts
            self.send_command_to_log = send_command_to_log_checkbutton.get_active()
            self.show_scripts_in_submenus = radio_show_scripts_submenu.get_active()
            self.hide_groups = hide_groups_checkbutton.get_active()
            self.indicator_text = indicator_text_entry.get_text()
            self.indicator_text_separator = indicator_text_separator_entry.get_text()
            self.initialise_background_scripts()
            self.set_autostart_and_delay( autostart_checkbox.get_active(), delay_spinner.get_value_as_int() )

        return response_type


    def background_scripts_filter_func( self, model, treeiter, scripts ):
        group = model[ treeiter ][ IndicatorScriptRunner.COLUMN_MODEL_GROUP ]
        if group is None:
            show = model[ treeiter ][ IndicatorScriptRunner.COLUMN_MODEL_BACKGROUND ] == '✔'

        else:
            background_scripts_by_group = \
                self.get_scripts_by_group( scripts, non_background = False, background = True )

            if group in background_scripts_by_group:
                show = len( background_scripts_by_group[ group ] ) > 0

            else:
                show = False

        return show


    # If/when a non-background script is default, render the script name bold.
    def data_function_column_name_renderer(
        self,
        treeviewcolumn,
        cell_renderer,
        treemodel,
        treeiter,
        scripts ):

        cell_renderer.set_property( "weight", Pango.Weight.NORMAL )
        name = treemodel.get_value( treeiter, IndicatorScriptRunner.COLUMN_MODEL_NAME )
        if name:
            group = \
                treemodel.get_value(
                    treemodel.iter_parent( treeiter ),
                    IndicatorScriptRunner.COLUMN_MODEL_GROUP )

            script = self.get_script( scripts, group, name )
            if type( script ) is NonBackground and script.get_default():
                cell_renderer.set_property( "weight", Pango.Weight.BOLD )


#TODO Might be helpful later...
#    https://discourse.gnome.org/t/migrating-gtk3-treestore-to-gtk4-liststore-and-handling-child-rows/12159/2
    def populate_treestore_and_select_script(
        self,
        treeview_all_scripts,
        treeview_background_scripts,
        scripts,
        select_group,
        select_script ):

        treestore = treeview_all_scripts.get_model()
        treestore.clear()

        scripts_by_group = self.get_scripts_by_group( scripts, non_background = True, background = True )
        groups = sorted( scripts_by_group.keys(), key = str.lower )
        for group in groups:
            row = [ group, None, None, None, None, None, None, None ]
            parent = treestore.append( None, row )
            for script in sorted( scripts_by_group[ group ], key = lambda script: script.get_name().lower() ):
                row = [
                   None, # Don't add in the group name here as it will be displayed.
                   script.get_name(),
                   '✔' if script.get_play_sound() else None,
                   '✔' if script.get_show_notification() else None,
                   '✔' if type( script ) is Background else None,
                   '—'
                   if type( script ) is Background else
                   ( '✔' if script.get_terminal_open() else None ),
                   str( script.get_interval_in_minutes() ) 
                   if type( script ) is Background else
                   '—',
                   ( '✔' if script.get_force_update() else None ) 
                   if type( script ) is Background else
                   '—' ]

                treestore.append( parent, row )

        treeview_background_scripts.get_model().refilter()

        if scripts:
            background_scripts_by_group = self.get_scripts_by_group( scripts, non_background = False, background = True )
            background_groups = sorted( background_scripts_by_group.keys(), key = str.lower )
            self.__expand_trees_and_select(
                treeview_all_scripts,
                treeview_background_scripts,
                select_group,
                select_script,
                scripts_by_group,
                groups,
                background_groups )


    def __expand_trees_and_select(
            self,
            treeview_all_scripts,
            treeview_background_scripts,
            select_group,
            select_script,
            scripts_by_group,
            groups,
            background_groups ):


        def build_path_and_select_group_and_script( treeview, groups ):
            path_as_string = "0:0"
            if select_group:
                try:
                    group_index = groups.index( select_group )
                    scripts_for_group = scripts_by_group[ select_group ]
                    i = 0
                    for script in sorted( scripts_for_group, key = lambda script: script.get_name().lower() ):
                        if select_script == script.get_name():
                            path_as_string = str( group_index ) + ":" + str( i )
                            break

                        i += 1

                except ValueError:
                    # Occurs when a group/script selected in the all scripts treeview
                    # does not exist in the background scripts treeview,
                    # so accept the default (select first item using 0:0).
                    pass


            treeview.expand_all()
            treepath = Gtk.TreePath.new_from_string( path_as_string )
            treeview.get_selection().select_path( treepath )
            treeview.set_cursor( treepath, None, False )
            if len( treeview.get_model() ):
                treeview.scroll_to_cell( treepath ) # Doesn't like to be called when empty.

        build_path_and_select_group_and_script( treeview_all_scripts, groups )
        build_path_and_select_group_and_script( treeview_background_scripts, background_groups )


    def on_script_selection( self, treeview, textview, scripts ):
        group, name = self.__get_group_name_from_treeview( treeview )
        command_text = ""
        if group and name:
            command_text = self.get_script( scripts, group, name ).get_command()

        textview.get_buffer().set_text( command_text )


    def on_script_double_click(
            self,
            scripts_treeview,
            treepath,
            treeviewcolumn,
            background_scripts_treeview,
            textentry,
            scripts ):

        self.on_script_edit(
            None,
            scripts,
            scripts_treeview,
            background_scripts_treeview,
            textentry )


    def on_background_script_double_click(
            self,
            treeview,
            treepath,
            treeviewcolumn,
            textentry ):

        group, name = self.__get_group_name_from_treeview( treeview )
        if group and name:
            textentry.insert_text(
                "[" + self.__create_key( group, name ) + "]", textentry.get_position() )


    def on_script_copy(
            self,
            button,
            scripts,
            scripts_treeview,
            background_scripts_treeview ):

        group, name = self.__get_group_name_from_treeview( scripts_treeview )
        if group and name:
            script = self.get_script( scripts, group, name )

            grid = self.create_grid()

            groups = sorted( self.get_scripts_by_group( scripts ).keys(), key = str.lower )
            script_group_combo = \
                self.create_comboboxtext(
                      groups,
                      tooltip_text = _(
                          "The group to which the script belongs.\n\n" +
                          "Choose an existing group or enter a new one." ),
                      active = groups.index( script.get_group() ) )

            grid.attach(
                self.create_box(
                    (
                        ( Gtk.Label.new( _( "Group" ) ), False ),
                        ( script_group_combo, True ) ) ),
                0, 0, 1, 1 )

            script_name_entry = \
                self.create_entry(
                    script.get_name(),
                    tooltip_text = _( "The name of the script." ) )

            grid.attach(
                self.create_box(
                    (
                        ( Gtk.Label.new( _( "Name" ) ), False ),
                        ( script_name_entry, True ) ),
                    margin_top = 10 ),
                0, 1, 1, 1 )

            dialog = \
                self.create_dialog(
                    scripts_treeview,
                    _( "Copy Script" ),
                    content_widget = grid )

            while True:
                dialog.show_all()
                if dialog.run() == Gtk.ResponseType.OK:
                    if script_group_combo.get_active_text().strip() == "":
                        self.show_dialog_ok( dialog, _( "The group cannot be empty." ) )
                        script_group_combo.grab_focus()
                        continue

                    if script_name_entry.get_text().strip() == "":
                        self.show_dialog_ok( dialog, _( "The name cannot be empty." ) )
                        script_name_entry.grab_focus()
                        continue

                    if self.get_script( scripts, script_group_combo.get_active_text().strip(), script_name_entry.get_text().strip() ):
                        self.show_dialog_ok( dialog, _( "A script of the same group and name already exists." ) )
                        script_group_combo.grab_focus()
                        continue

                    if type( script ) is Background:
                        new_script = Background(
                            script_group_combo.get_active_text().strip(),
                            script_name_entry.get_text().strip(),
                            script.get_command(),
                            script.get_play_sound(),
                            script.get_show_notification(),
                            script.get_interval_in_minutes(),
                            script.get_force_update() )

                    else:
                        new_script = NonBackground(
                            script_group_combo.get_active_text().strip(),
                            script_name_entry.get_text().strip(),
                            script.get_command(),
                            script.get_play_sound(),
                            script.get_show_notification(),
                            script.get_terminal_open(),
                            False )

                    scripts.append( new_script )

                    self.populate_treestore_and_select_script(
                        scripts_treeview,
                        background_scripts_treeview,
                        scripts,
                        new_script.get_group(),
                        new_script.get_name() )

                break

            dialog.destroy()


    def update_indicator_textentry( self, textentry, old_tag, new_tag ):
        if new_tag:
            textentry.set_text( textentry.get_text().replace( "[" + old_tag + "]", "[" + new_tag + "]" ) )

        else:
            textentry.set_text( textentry.get_text().replace( "[" + old_tag + "]", "" ) )


    def on_script_remove(
            self,
            button,
            scripts,
            scripts_treeview,
            background_scripts_treeview,
            textentry ):

        group, name = self.__get_group_name_from_treeview( scripts_treeview )
        if group and name:
            if self.show_dialog_ok_cancel( scripts_treeview, _( "Remove the selected script?" ) ) == Gtk.ResponseType.OK:
                i = 0
                for script in scripts:
                    if script.get_group() == group and script.get_name() == name:
                        del scripts[ i ]
                        self.populate_treestore_and_select_script(
                            scripts_treeview,
                            background_scripts_treeview,
                            scripts,
                            "",
                            "" )

                        self.update_indicator_textentry( textentry, self.__create_key( group, name ), "" )
                        break

                    i += 1


    def on_script_add(
            self,
            button,
            scripts,
            scripts_treeview,
            background_scripts_treeview ):

        self.__add_edit_script( None, scripts, scripts_treeview, background_scripts_treeview )


    def on_script_edit(
            self,
            button,
            scripts,
            scripts_treeview,
            background_scripts_treeview,
            textentry ):

        group, name = self.__get_group_name_from_treeview( scripts_treeview )
        if group and name:
            the_script = self.get_script( scripts, group, name )
            edited_script = \
                self.__add_edit_script(
                    the_script,
                    scripts, scripts_treeview,
                    background_scripts_treeview )

            if edited_script:
                if type( the_script ) is Background and type( edited_script ) is NonBackground:
                    old_tag = self.__create_key( group, name )
                    self.update_indicator_textentry( textentry, old_tag, "" )

                if not( group == edited_script.get_group() and name == edited_script.get_name() ):
                    old_tag = self.__create_key( group, name )
                    new_tag = self.__create_key( edited_script.get_group(), edited_script.get_name() )
                    self.update_indicator_textentry( textentry, old_tag, new_tag )


    def __add_edit_script(
            self,
            script,
            scripts,
            scripts_treeview,
            background_scripts_treeview ):

        groups = sorted( self.get_scripts_by_group( scripts ).keys(), key = str.lower )

        add = True if script is None else False
        if add:
            index = 0
            model, treeiter = scripts_treeview.get_selection().get_selected()
            if treeiter:
                group = model[ treeiter ][ IndicatorScriptRunner.COLUMN_MODEL_GROUP ]
                if group is None: # A script is selected, so find the parent group.
                    parent = scripts_treeview.get_model().iter_parent( treeiter )
                    group = model[ parent ][ IndicatorScriptRunner.COLUMN_MODEL_GROUP ]

                index = groups.index( group )

        else:
            index = groups.index( script.get_group() )

        group_combo = \
            self.create_comboboxtext(
                groups,
                tooltip_text = _(
                    "The group to which the script belongs.\n\n" +
                    "Choose an existing group or enter a new one." ),
                active = index )

        grid = self.create_grid()

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Group" ) ), False ),
                    ( group_combo, True ) ) ),
            0, 0, 1, 1 )

        name_entry = \
            self.create_entry(
                "" if add else script.get_name(),
                tooltip_text = _( "The name of the script." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Name" ) ), False ),
                    ( name_entry, True ) ),
                margin_top = 10 ),
            0, 1, 1, 1 )

        grid.attach(
            self.create_box(
                ( ( Gtk.Label.new( _( "Command" ) ), False ), ),
                margin_top = 10 ),
            0, 2, 1, 1 )

        command_text_view = \
            self.create_textview(
                text = "" if add else script.get_command(),
                tooltip_text = _( "The terminal script/command, along with any arguments." ) )

        grid.attach(
            self.create_box(
                ( ( self.create_scrolledwindow( command_text_view ), True ), ) ),
            0, 3, 1, 10 )

        sound_checkbutton = \
            self.create_checkbutton(
                _( "Play sound" ),
                tooltip_text = _(
                    "For non-background scripts, play a sound\n" +
                    "on script completion.\n\n" +
                    "For background scripts, play a sound\n" +
                    "only if the script returns non-empty text." ),
                active = False if add else script.get_play_sound() )

        grid.attach( sound_checkbutton, 0, 13, 1, 1 )

        notification_checkbutton = \
            self.create_checkbutton(
                _( "Show notification" ),
                tooltip_text = _(
                    "For non-background scripts, show a\n" +
                    "notification on script completion.\n\n" +
                    "For background scripts, show a notification\n" +
                    "only if the script returns non-empty text." ),
                active = False if add else script.get_show_notification() )

        grid.attach( notification_checkbutton, 0, 14, 1, 1 )

        script_non_background_radio = \
            self.create_radiobutton(
                None,
                _( "Non-background" ),
                tooltip_text = _(
                    "Non-background scripts are displayed\n" +
                    "in the menu and run when the user\n" +
                    "clicks on the corresponding menu item." ),
                active = True if add else type( script ) is NonBackground )

        grid.attach( script_non_background_radio, 0, 15, 1, 1 )

        terminal_checkbutton = \
            self.create_checkbutton(
                _( "Leave terminal open" ),
                tooltip_text = _( "Leave the terminal open on script completion." ),
                sensitive = True if add else type( script ) is NonBackground,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = False if add else type( script ) is NonBackground and script.get_terminal_open() )

        grid.attach( terminal_checkbutton, 0, 16, 1, 1 )

        default_script_checkbutton = \
            self.create_checkbutton(
                _( "Default script" ),
                tooltip_text = _(
                    "One script may be set as default\n" +
                    "which is run on a middle mouse\n" +
                    "click of the indicator icon.\n\n" +
                    "Not supported on all desktops." ),
                sensitive = True if add else type( script ) is NonBackground,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = False if add else type( script ) is NonBackground and script.get_default() )

        grid.attach( default_script_checkbutton, 0, 17, 1, 1 )

        script_background_radio = \
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
                active = False if add else type( script ) is Background )

        grid.attach( script_background_radio, 0, 18, 1, 1 )

        interval_spinner = \
            self.create_spinbutton(
                script.get_interval_in_minutes() if type( script ) is Background else 60,
                1,
                10000,
                page_increment = 100,
                tooltip_text = _( "Interval, in minutes, between runs." ) )

        label_and_interval_spinner_box = \
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Interval" ) ), False ),
                    ( interval_spinner, False ) ),
                sensitive = False if add else type( script ) is Background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT * 1.4 ) # Approximate alignment with the checkboxes above.

        grid.attach( label_and_interval_spinner_box, 0, 19, 1, 1 )

        force_update_checkbutton = \
            self.create_checkbutton(
                _( "Force update" ),
                tooltip_text = _(
                    "If the script returns non-empty text\n" +
                    "on its update, the script will run\n" +
                    "on the next update of ANY script." ),
                sensitive = True if add else type( script ) is Background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = False if add else type( script ) is Background and script.get_force_update() )

        grid.attach( force_update_checkbutton, 0, 20, 1, 1 )

        script_non_background_radio.connect(
            "toggled",
            self.on_radio_or_checkbox, True, terminal_checkbutton, default_script_checkbutton )

        script_non_background_radio.connect(
            "toggled",
            self.on_radio_or_checkbox, False, label_and_interval_spinner_box, force_update_checkbutton )

        script_background_radio.connect(
            "toggled",
            self.on_radio_or_checkbox, True, label_and_interval_spinner_box, force_update_checkbutton )

        script_background_radio.connect(
            "toggled",
            self.on_radio_or_checkbox, False, terminal_checkbutton, default_script_checkbutton )

        dialog = \
            self.create_dialog(
                scripts_treeview,
                _( "Add Script" ) if add else _( "Edit Script" ),
                content_widget = grid )

        new_script = None
        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if group_combo.get_active_text().strip() == "":
                    self.show_dialog_ok( dialog, _( "The group cannot be empty." ) )
                    group_combo.grab_focus()
                    continue

                if name_entry.get_text().strip() == "":
                    self.show_dialog_ok( dialog, _( "The name cannot be empty." ) )
                    name_entry.grab_focus()
                    continue

                if self.get_textview_text( command_text_view ).strip() == "":
                    self.show_dialog_ok( dialog, _( "The command cannot be empty." ) )
                    command_text_view.grab_focus()
                    continue

                # Check for duplicates...
                #    For an add, find an existing script with the same group/name.
                #    For an edit, the group and/or name must change (and then match with an existing script other than the original).
                script_of_same_name_and_group_exists = \
                    self.get_script(
                        scripts,
                        group_combo.get_active_text().strip(),
                        name_entry.get_text().strip() ) is not None

                edited_script_group_or_name_different = \
                    not add and \
                    (
                        group_combo.get_active_text().strip() != script.get_group() or \
                        name_entry.get_text().strip() != script.get_name() )

                if ( add or edited_script_group_or_name_different ) and script_of_same_name_and_group_exists:
                    self.show_dialog_ok( dialog, _( "A script of the same group and name already exists." ) )
                    group_combo.grab_focus()
                    continue

                # For an edit, remove the original script...
                if not add:
                    i = 0
                    for skript in scripts:
                        if script.get_group() == skript.get_group() and script.get_name() == skript.get_name():
                            break

                        i += 1

                    del scripts[ i ]

                # If this script is marked as default (and is non-background),
                # check for an existing default script and if found, undefault it...
                if script_non_background_radio.get_active() and default_script_checkbutton.get_active():
                    i = 0
                    for skript in scripts:
                        if type( skript ) is NonBackground and skript.get_default():
                            undefault_script = NonBackground(
                                skript.get_group(),
                                skript.get_name(),
                                skript.get_command(),
                                skript.get_play_sound(),
                                skript.get_show_notification(),
                                skript.get_terminal_open(),
                                False )

                            del scripts[ i ]
                            scripts.append( undefault_script )
                            break

                        i += 1

                # Create new script (add or edit) and add to scripts...
                if script_background_radio.get_active():
                    new_script = Background(
                        group_combo.get_active_text().strip(),
                        name_entry.get_text().strip(),
                        self.get_textview_text( command_text_view ).strip(),
                        sound_checkbutton.get_active(),
                        notification_checkbutton.get_active(),
                        interval_spinner.get_value_as_int(),
                        force_update_checkbutton.get_active() )

                else:
                    new_script = NonBackground(
                        group_combo.get_active_text().strip(),
                        name_entry.get_text().strip(),
                        self.get_textview_text( command_text_view ).strip(),
                        sound_checkbutton.get_active(),
                        notification_checkbutton.get_active(),
                        terminal_checkbutton.get_active(),
                        default_script_checkbutton.get_active() )

                scripts.append( new_script )

                self.populate_treestore_and_select_script(
                    scripts_treeview,
                    background_scripts_treeview,
                    scripts,
                    new_script.get_group(),
                    new_script.get_name() )

            break

        dialog.destroy()
        return new_script


    def get_script( self, scripts, group, name ):
        the_script = None
        for script in scripts:
            if script.get_group() == group and script.get_name() == name:
                the_script = script
                break

        return the_script


    def get_scripts_by_group( self, scripts, non_background = True, background = True ):
        scripts_by_group = { }
        for script in scripts:
            if ( non_background and type( script ) is NonBackground ) or ( background and type( script ) is Background ):
                if script.get_group() not in scripts_by_group:
                    scripts_by_group[ script.get_group() ] = [ ]

                scripts_by_group[ script.get_group() ].append( script )

        return scripts_by_group


    def __get_group_name_from_treeview( self, treeview ):
        group = None
        name = None
        model, treeiter = treeview.get_selection().get_selected()
        if treeiter:
            group = model[ treeiter ][ IndicatorScriptRunner.COLUMN_MODEL_GROUP ]
            if group is None:
                parent = treeview.get_model().iter_parent( treeiter )
                group = model[ parent ][ IndicatorScriptRunner.COLUMN_MODEL_GROUP ]
                name = model[ treeiter ][ IndicatorScriptRunner.COLUMN_MODEL_NAME ]

        return group, name


    # Each time a background script is run, cache the result.
    #
    # If for example, one script has an interval of five minutes and another script is hourly,
    # the hourly script should only be run hourly,
    # so use a cached result when the quicker script is run.
    #
    # Initialise the cache results and set a next update time in the past
    # to force all (background) scripts to update first time.
    def initialise_background_scripts( self ):
        self.background_script_results = { }
        self.background_script_next_update_time = { }
        today = datetime.datetime.now()
        for script in self.scripts:
            if type( script ) is Background:
                key = self.__create_key( script.get_group(), script.get_name() )
                self.background_script_results[ key ] = None
                self.background_script_next_update_time[ key ] = today


    def __create_key( self, group, name ):
        return group + "::" + name


    def is_background_script_in_indicator_text( self, script ):
        return '[' + self.__create_key( script.get_group(), script.get_name() ) + ']' in self.indicator_text


    def load_config( self, config ):
        self.hide_groups = config.get( IndicatorScriptRunner.CONFIG_HIDE_GROUPS, False )
        self.indicator_text = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT, "" )
        self.indicator_text_separator = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR, " | " )
        self.send_command_to_log = config.get( IndicatorScriptRunner.CONFIG_SEND_COMMAND_TO_LOG, False )
        self.show_scripts_in_submenus = config.get( IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS, False )

        self.scripts = [ ]
        if config:
            scripts_non_background = config.get( self.CONFIG_SCRIPTS_NON_BACKGROUND, [ ] )
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

        else:
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
                    "notify-send -i " + self.get_icon_name() + " \"Public IP address: $(wget https://ipinfo.io/ip -qO -)\"",
                    False, False, False, False ) )

            self.scripts.append(
                NonBackground(
                    "Network",
                    "Up or down", "if wget -qO /dev/null google.com > /dev/null; then notify-send -i " + self.get_icon_name() + " \"Internet is UP\"; else notify-send \"Internet is DOWN\"; fi",
                    False, False, False, True ) )

            self.scripts.append(
                NonBackground(
                    "Update",
                    "autoclean | autoremove | update | dist-upgrade", "sudo apt-get autoclean && sudo apt-get -y autoremove && sudo apt-get update && sudo apt-get -y dist-upgrade",
                    True, True, True, False ) )

            # Example background scripts.
            self.scripts.append(
                Background(
                    "Network",
                    "Internet Down", "if wget -qO /dev/null google.com > /dev/null; then echo \"\"; else echo \"Internet is DOWN\"; fi",
                    False, True, 60, True ) )

            self.scripts.append(
                Background(
                    "System",
                    "Available Memory", "echo \"Free Memory: \"$(expr $( cat /proc/meminfo | grep MemAvailable | tr -d -c 0-9 ) / 1024)\" MB\"",
                    False, False, 5, False ) )

            self.indicator_text = " [Network::Internet Down][System::Available Memory]"

            self.request_save_config()

        self.initialise_background_scripts()


    def save_config( self ):
        scripts_background = [ ]
        scripts_non_background = [ ]
        for script in self.scripts:
            if type( script ) is Background:
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
            IndicatorScriptRunner.CONFIG_HIDE_GROUPS : self.hide_groups,
            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT : self.indicator_text,
            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR : self.indicator_text_separator,
            IndicatorScriptRunner.CONFIG_SCRIPTS_BACKGROUND : scripts_background,
            IndicatorScriptRunner.CONFIG_SCRIPTS_NON_BACKGROUND : scripts_non_background,
            IndicatorScriptRunner.CONFIG_SEND_COMMAND_TO_LOG : self.send_command_to_log,
            IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS : self.show_scripts_in_submenus
        }


IndicatorScriptRunner().main()
