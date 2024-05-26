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


# Application indicator to run a terminal command or script from an indicator.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import concurrent.futures
import copy
import datetime
import gi
import math

gi.require_version( "GLib", "2.0" )
from gi.repository import GLib

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

try:
    gi.require_version( "Notify", "0.7" )
except ValueError:
    gi.require_version( "Notify", "0.8" )
from gi.repository import Notify

gi.require_version( "Pango", "1.0" )
from gi.repository import Pango

from threading import Thread

from script import Background, NonBackground


class IndicatorScriptRunner( IndicatorBase ):

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

    # Data model columns used in the Preferences dialog...
    #    in the table to display all scripts;
    #    in the table to display background scripts.
    COLUMN_GROUP_INTERNAL = 0 # Never shown; used when the script group is needed by decision logic.
    COLUMN_GROUP = 1 # Valid when displaying a row containing just the group; otherwise empty when displaying a script name and attributes.
    COLUMN_NAME = 2 # Script name.
    COLUMN_SOUND = 3 # Icon name for the APPLY icon; None otherwise.
    COLUMN_NOTIFICATION = 4 # Icon name for the APPLY icon; None otherwise.
    COLUMN_BACKGROUND = 5 # Icon name for the APPLY icon; None otherwise.
    COLUMN_TERMINAL = 6 # Icon name for the APPLY icon; None otherwise.
    COLUMN_INTERVAL = 7 # Numeric amount as a string.
    COLUMN_FORCE_UPDATE = 8 # Icon name for the APPLY icon; None otherwise.
    COLUMN_REMOVE = 9 # Icon name for the REMOVE icon; None otherwise.

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

        self.command_nofity_background = \
            "notify-send -i " + self.get_icon_name() + \
            " \"" + IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" " + \
            "\"" + IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_RESULT + "\""

        self.command_nofity_nonbackground = \
            "notify-send -i " + self.get_icon_name() + \
            " \"" + IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" " + \
            "\"" + _( "...has completed." ) + "\""


    def update( self, menu ):
        today = datetime.datetime.now()
        self.updateMenu( menu )
        self.updateBackgroundScripts( today )
        self.setLabel( self.processTags() )

        # Calculate next update...
        nextUpdate = today + datetime.timedelta( hours = 100 ) # Set an update time well into the future.
        for script in self.scripts:
            key = self.__createKey( script.getGroup(), script.getName() )

            if type( script ) is Background and \
               self.backgroundScriptNextUpdateTime[ key ] < nextUpdate and \
               self.isBackgroundScriptInIndicatorText( script ):
                nextUpdate = self.backgroundScriptNextUpdateTime[ key ]

        nextUpdateInSeconds = int( math.ceil( ( nextUpdate - today ).total_seconds() ) )
        return 60 if nextUpdateInSeconds < 60 else nextUpdateInSeconds


    def updateMenu( self, menu ):
        if self.showScriptsInSubmenus:
            scriptsByGroup = self.getScriptsByGroup( self.scripts, True, False )
            indent = self.getMenuIndent()
            for group in sorted( scriptsByGroup.keys(), key = str.lower ):
                subMenu = Gtk.Menu()
                self.createAndAppendMenuItem( menu, group ).set_submenu( subMenu )
                self.addScriptsToMenu( scriptsByGroup[ group ], subMenu, indent )

        else:
            if self.hideGroups:
                for script in sorted( self.scripts, key = lambda script: script.getName().lower() ):
                    if type( script ) is NonBackground:
                        self.addScriptsToMenu( [ script ], menu, "" )

            else:
                scriptsByGroup = self.getScriptsByGroup( self.scripts, True, False )
                indent = self.getMenuIndent()
                for group in sorted( scriptsByGroup.keys(), key = str.lower ):
                    self.createAndAppendMenuItem( menu, group + "..." )
                    self.addScriptsToMenu( scriptsByGroup[ group ], menu, indent )


    def addScriptsToMenu( self, scripts, menu, indent ):
        scripts.sort( key = lambda script: script.getName().lower() )
        for script in scripts:
            menuItem = self.createAndAppendMenuItem(
                menu,
                indent + script.getName(),
                onClickFunction = lambda menuItem, script = script: self.onScriptMenuItem( script ) ) # Note script = script to handle lambda late binding.

            if script.getDefault():
                self.secondaryActivateTarget = menuItem


    def onScriptMenuItem( self, script ):
        terminal, terminalExecutionFlag = self.getTerminalAndExecutionFlag()
        if terminal is None:
            message = _( "Cannot run script as no terminal and/or terminal execution flag found; please install gnome-terminal." )
            self.getLogging().error( message )
            Notify.Notification.new( "Cannot run script", message, self.get_icon_name() ).show()

        elif self.isTerminalQTerminal():
            # As a result of this issue
            #    https://github.com/lxqt/qterminal/issues/335
            # the default terminal in Lubuntu (qterminal) fails to parse argument.
            # Although a fix has been made, it is unlikely the repository will be updated any time soon.
            # So the quickest/easiest workaround is to install gnome-terminal.
            message = _( "Cannot run script as qterminal incorrectly parses arguments; please install gnome-terminal instead." )
            self.getLogging().error( message )
            Notify.Notification.new( "Cannot run script", message, self.get_icon_name() ).show()

        else:
            command = terminal + " " + terminalExecutionFlag + " ${SHELL} -c '"
            command += script.getCommand()

            if script.getShowNotification():
                command += "; " + self.command_nofity_nonbackground.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME, script.getName() )

            if script.getPlaySound():
                command += "; " + IndicatorScriptRunner.COMMAND_SOUND

            if script.getTerminalOpen():
                command += "; cd $HOME; ${SHELL}"

            command += "'"

            if self.sendCommandToLog:
                self.getLogging().debug( script.getGroup() + " | " + script.getName() + ": " + command )

            Thread( target = self.processCall, args = ( command, ) ).start()


    def updateBackgroundScripts( self, now ):
        backgroundScriptsToExecute = [ ]
        for script in self.scripts:
            if type( script ) is Background and self.isBackgroundScriptInIndicatorText( script ):
                # Script is background AND present in the indicator text, so is a potential candidate to be updated...
                key = self.__createKey( script.getGroup(), script.getName() )
                if ( self.backgroundScriptNextUpdateTime[ key ] < now ) or \
                   ( script.getForceUpdate() and self.backgroundScriptResults[ key ] ):
                    backgroundScriptsToExecute.append( script )

        # Based on example from
        #    https://docs.python.org/3.6/library/concurrent.futures.html#threadpoolexecutor-example
        with concurrent.futures.ThreadPoolExecutor( max_workers = 5 ) as executor:
            futureToScript = { executor.submit( self.__updateBackgroundScript, script, now ): script for script in backgroundScriptsToExecute }
            for future in concurrent.futures.as_completed( futureToScript ):
                script = futureToScript[ future ]
                key = future.result()
                commandResult = self.backgroundScriptResults[ key ]

                if script.getPlaySound() and commandResult:
                    self.processCall( IndicatorScriptRunner.COMMAND_SOUND )

                if script.getShowNotification() and commandResult:
                    notificationCommand = self.command_nofity_background
                    notificationCommand = notificationCommand.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME, script.getName().replace( '-', '\\-' ) )
                    notificationCommand = notificationCommand.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_RESULT, commandResult.replace( '-', '\\-' ) )
                    self.processCall( notificationCommand )


    def __updateBackgroundScript( self, script, now ):
        if self.sendCommandToLog:
            self.getLogging().debug( script.getGroup() + " | " + script.getName() + ": " + script.getCommand() )

        commandResult = self.processGet( script.getCommand(), logNonZeroErrorCode = True ) # When calling a user script, always want to log out any errors (from non-zero return codes).
        if commandResult:
            commandResult = commandResult.strip()

        else:
            commandResult = None # Indicate downstream an error occurred when running the script.

        key = self.__createKey( script.getGroup(), script.getName() )
        self.backgroundScriptResults[ key ] = commandResult
        self.backgroundScriptNextUpdateTime[ key ] = now + datetime.timedelta( minutes = script.getIntervalInMinutes() )
        return key


    def processTags( self ):
        indicatorTextProcessed = self.indicatorText
        for script in self.scripts:
            key = self.__createKey( script.getGroup(), script.getName() )
            if type( script ) is Background and "[" + key + "]" in indicatorTextProcessed:
                commandResult = self.backgroundScriptResults[ key ]
                if commandResult is None: # Background script failed so leave the tag in place for the user to see.
                    indicatorTextProcessed = indicatorTextProcessed.replace( "[" + key + "]", "[" + key + "]" + self.indicatorTextSeparator )

                elif commandResult: # Non-empty result so replace tag and tack on a separator.
                    indicatorTextProcessed = indicatorTextProcessed.replace( "[" + key + "]", commandResult + self.indicatorTextSeparator )

                else: # No result, so remove tag but no need for separator.
                    indicatorTextProcessed = indicatorTextProcessed.replace( "[" + key + "]", commandResult )

        return indicatorTextProcessed[ 0 : - len( self.indicatorTextSeparator ) ] # Trim last separator.


    def onPreferences( self, dialog ):
        copyOfScripts = copy.deepcopy( self.scripts )

        notebook = Gtk.Notebook()

        # Scripts.
        grid = self.create_grid()

        # Define these here so that widgets can connect to handle events.
        # Contains extra/redundant columns, but allows the reuse of the column definitions.
        backgroundScriptsTreeView = Gtk.TreeView.new_with_model( Gtk.TreeStore( str, str, str, str, str, str, str, str, str ) )
        indicatorTextEntry = Gtk.Entry()

        treeView = Gtk.TreeView.new_with_model( Gtk.TreeStore( str, str, str, str, str, str, str, str, str, str ) )
        treeView.set_hexpand( True )
        treeView.set_vexpand( True )
        treeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        treeView.connect( "row-activated", self.onScriptDoubleClick, backgroundScriptsTreeView, indicatorTextEntry, copyOfScripts )
        treeView.set_tooltip_text( _(
            "Double-click to edit a script.\n\n" + \
            "If an attribute does not apply to a script,\n" + \
            "a dash is displayed.\n\n" + \
            "If a non-background script is checked as\n" + \
            "default, the name will appear in bold." ) )

        treeViewColumn = Gtk.TreeViewColumn( _( "Group" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_GROUP )
        treeViewColumn.set_expand( True )
        treeView.append_column( treeViewColumn )

        rendererText = Gtk.CellRendererText()
        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), rendererText, text = IndicatorScriptRunner.COLUMN_NAME )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionNameColumn, copyOfScripts )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_SOUND )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_NOTIFICATION )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Background" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_BACKGROUND )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Terminal" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TERMINAL )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Interval" ) )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )

        rendererText = Gtk.CellRendererText()
        treeViewColumn.pack_start( rendererText, False )
        treeViewColumn.add_attribute( rendererText, "text", IndicatorScriptRunner.COLUMN_INTERVAL )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionIntervalColumn )

        rendererPixbuf = Gtk.CellRendererPixbuf()
        treeViewColumn.pack_start( rendererPixbuf, False )
        treeViewColumn.add_attribute( rendererPixbuf, "icon_name", IndicatorScriptRunner.COLUMN_REMOVE )
        treeViewColumn.set_cell_data_func( rendererPixbuf, self.dataFunctionIntervalColumn )

        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Force Update" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_FORCE_UPDATE )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
        treeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( treeView )

        grid.attach( scrolledWindow, 0, 0, 1, 20 )

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label.new( _( "Command" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        commandTextView = Gtk.TextView()
        commandTextView.set_tooltip_text( _( "The terminal script/command, along with any arguments." ) )
        commandTextView.set_editable( False )
        commandTextView.set_wrap_mode( Gtk.WrapMode.WORD )

        treeView.connect( "cursor-changed", self.onScriptSelection, treeView, commandTextView, copyOfScripts )
        self.populateScriptsTreeStore( copyOfScripts, treeView, "", "" )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( commandTextView )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )

        box.pack_start( scrolledWindow, True, True, 0 )
        grid.attach( box, 0, 20, 1, 10 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )
        box.set_homogeneous( True )

        # addButton = Gtk.Button.new_with_label( _( "Add" ) )
        # addButton.set_tooltip_text( _( "Add a new script." ) )
        # addButton.connect( "clicked", self.onScriptAdd, copyOfScripts, treeView, backgroundScriptsTreeView )
        # box.pack_start( addButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Add" ),
                _( "Add a new script." ),
                connect_function_and_arguments = (
                    self.onScriptAdd,
                    copyOfScripts, treeView, backgroundScriptsTreeView ) ),
            True,
            True,
            0 )

        # editButton = Gtk.Button.new_with_label( _( "Edit" ) )
        # editButton.set_tooltip_text( _( "Edit the selected script." ) )
        # editButton.connect( "clicked", self.onScriptEdit, copyOfScripts, treeView, backgroundScriptsTreeView, indicatorTextEntry )
        # box.pack_start( editButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Edit" ),
                _( "Edit the selected script." ),
                connect_function_and_arguments = (
                    self.onScriptEdit,
                    copyOfScripts, treeView, backgroundScriptsTreeView, indicatorTextEntry ) ),
            True,
            True,
            0 )

        # copyButton = Gtk.Button.new_with_label( _( "Copy" ) )
        # copyButton.set_tooltip_text( _( "Duplicate the selected script." ) )
        # copyButton.connect( "clicked", self.onScriptCopy, copyOfScripts, treeView, backgroundScriptsTreeView )
        # box.pack_start( copyButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Copy" ),
                _( "Duplicate the selected script." ),
                connect_function_and_arguments = (
                    self.onScriptCopy,
                    copyOfScripts, treeView, backgroundScriptsTreeView ) ),
            True,
            True,
            0 )

        # removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        # removeButton.set_tooltip_text( _( "Remove the selected script." ) )
        # removeButton.connect( "clicked", self.onScriptRemove, copyOfScripts, treeView, backgroundScriptsTreeView, commandTextView, indicatorTextEntry )
        # box.pack_start( removeButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Remove" ),
                _( "Remove the selected script." ),
                connect_function_and_arguments = (
                    self.onScriptRemove,
                    copyOfScripts, treeView, backgroundScriptsTreeView, commandTextView, indicatorTextEntry ) ),
            True,
            True,
            0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 30, 1, 1 )

        sendCommandToLogCheckbutton = \
            self.create_checkbutton(
                _( "Send command to log" ),
                _( "When a script is run,\n" + \
                   "send the command to the log\n" + \
                   "(located in your home directory)." ),
                active = self.sendCommandToLog )
#TODO Make sure this is converted okay
        # sendCommandToLogCheckbutton = Gtk.CheckButton.new_with_label( _( "Send command to log" ) )
        # sendCommandToLogCheckbutton.set_active( self.sendCommandToLog )
        # sendCommandToLogCheckbutton.set_tooltip_text( _(
        #     "When a script is run,\n" + \
        #     "send the command to the log\n" + \
        #     "(located in your home directory)." ) )

        grid.attach( sendCommandToLogCheckbutton, 0, 31, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Scripts" ) ) )

        # Menu settings.
        grid = self.create_grid()

        # radioShowScriptsSubmenu = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show non-background scripts in sub-menus" ) )
        # radioShowScriptsSubmenu.set_active( self.showScriptsInSubmenus )
        # grid.attach( radioShowScriptsSubmenu, 0, 0, 1, 1 )
#TODO Check above.
        radioShowScriptsSubmenu = \
            self.create_radiobutton(
                None,
                _( "Show non-background scripts in sub-menus" ),
                active = self.showScriptsInSubmenus )

        grid.attach( radioShowScriptsSubmenu, 0, 0, 1, 1 )

        # radioShowScriptsIndented = Gtk.RadioButton.new_with_label_from_widget( radioShowScriptsSubmenu, _( "Show non-background scripts indented by group" ) )
        # radioShowScriptsIndented.set_active( not self.showScriptsInSubmenus )
        # grid.attach( radioShowScriptsIndented, 0, 1, 1, 1 )
#TODO Check above.
        radioShowScriptsIndented = \
            self.create_radiobutton(
                radioShowScriptsSubmenu,
                _( "Show non-background scripts indented by group" ),
                active = not self.showScriptsInSubmenus )

        grid.attach( radioShowScriptsIndented, 0, 1, 1, 1 )

        hideGroupsCheckbutton = \
            self.create_checkbutton(
                _( "Hide groups" ),
                _( "If checked, only script names are displayed.\n" + \
                   "Otherwise, script names are indented\n" + \
                   "within their respective group." ),
                not self.showScriptsInSubmenus,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.hideGroups )
#TODO Make sure this is converted okay
        # hideGroupsCheckbutton = Gtk.CheckButton.new_with_label( _( "Hide groups" ) )
        # hideGroupsCheckbutton.set_active( self.hideGroups )
        # hideGroupsCheckbutton.set_sensitive( not self.showScriptsInSubmenus )
        # hideGroupsCheckbutton.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # hideGroupsCheckbutton.set_tooltip_text( _(
        #     "If checked, only script names are displayed.\n" + \
        #     "Otherwise, script names are indented\n" + \
        #     "within their respective group." ) )

        radioShowScriptsIndented.connect( "toggled", self.onRadioOrCheckbox, True, hideGroupsCheckbutton )

        grid.attach( hideGroupsCheckbutton, 0, 2, 1, 1 )

        autostartCheckbox, delaySpinner, box = self.createAutostartCheckboxAndDelaySpinner()
        box.set_margin_top( 30 ) # Put some distance from the prior section.
        grid.attach( box, 0, 3, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )

        # Icon text settings.
        grid = self.create_grid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Icon Text" ) ), False, False, 0 )

        indicatorTextEntry.set_text( self.indicatorText )
        indicatorTextEntry.set_tooltip_text( _(
            "The text shown next to the indicator icon,\n" + \
            "or tooltip where applicable.\n\n" + \
            "A background script must:\n" + \
            "\tAlways return non-empty text; or\n" + \
            "\tReturn non-empty text on success\n" + \
            "\tand empty text otherwise.\n\n" + \
            "Only background scripts added to the\n" + \
            "icon text will be run.\n\n" + \
            "Not supported on all desktops." ) )

        box.pack_start( indicatorTextEntry, True, True, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Separator" ) ), False, False, 0 )

        indicatorTextSeparatorEntry = Gtk.Entry()
        indicatorTextSeparatorEntry.set_text( self.indicatorTextSeparator )
        indicatorTextSeparatorEntry.set_tooltip_text( _( "The separator will be added between script tags." ) )
        box.pack_start( indicatorTextSeparatorEntry, False, False, 0 )
        grid.attach( box, 0, 1, 1, 1 )

        backgroundScriptsTreeView.set_hexpand( True )
        backgroundScriptsTreeView.set_vexpand( True )
        backgroundScriptsTreeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        backgroundScriptsTreeView.connect( "row-activated", self.onBackgroundScriptDoubleClick, indicatorTextEntry, copyOfScripts )
        backgroundScriptsTreeView.set_tooltip_text( _( "Double click on a script to add to the icon text." ) )

        treeViewColumn = Gtk.TreeViewColumn( _( "Group" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_GROUP )
        treeViewColumn.set_expand( True )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_NAME )
        treeViewColumn.set_expand( True )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_SOUND )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_NOTIFICATION )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        renderer = Gtk.CellRendererText()
        renderer.set_property( "xalign", 0.5 )
        treeViewColumn = Gtk.TreeViewColumn( _( "Interval" ), renderer, text = IndicatorScriptRunner.COLUMN_INTERVAL )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Force Update" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_FORCE_UPDATE )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_alignment( 0.5 )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( backgroundScriptsTreeView )

        self.populateBackgroundScriptsTreeStore( copyOfScripts, backgroundScriptsTreeView, "", "" )

        grid.attach( scrolledWindow, 0, 2, 1, 20 )

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

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.scripts = copyOfScripts
            self.sendCommandToLog = sendCommandToLogCheckbutton.get_active()
            self.showScriptsInSubmenus = radioShowScriptsSubmenu.get_active()
            self.hideGroups = hideGroupsCheckbutton.get_active()
            self.indicatorText = indicatorTextEntry.get_text()
            self.indicatorTextSeparator = indicatorTextSeparatorEntry.get_text()
            self.initialiseBackgroundScripts()
            self.setAutostartAndDelay( autostartCheckbox.get_active(), delaySpinner.get_value_as_int() )

        return responseType


    # Renders the script name bold when the (non-background) script is default.
    # Otherwise normal style is used.
    #
    # https://stackoverflow.com/questions/52798356/python-gtk-treeview-column-data-display
    # https://stackoverflow.com/questions/27745585/show-icon-or-color-in-gtk-treeview-tree
    # https://stackoverflow.com/questions/49836499/make-only-some-rows-bold-in-a-gtk-treeview
    # https://lazka.github.io/pgi-docs/Gtk-3.0/classes/TextTag.html
    # https://developer.gnome.org/pygtk/stable/class-gtkcellrenderertext.html
    # https://developer.gnome.org/pygtk/stable/pango-markup-language.html
    # https://developer.gnome.org/pygtk/stable/class-gtkcellrenderertext.html
    # https://developer.gnome.org/pygtk/stable/pango-constants.html#pango-alignment-constants
    def dataFunctionNameColumn( self, treeViewColumn, cellRenderer, treeModel, treeIter, scripts ):
        cellRenderer.set_property( "weight", Pango.Weight.NORMAL )
        group = treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_GROUP_INTERNAL )
        name = treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_NAME )
        script = self.getScript( scripts, group, name )
        if type( script ) is NonBackground and script.getDefault():
            cellRenderer.set_property( "weight", Pango.Weight.BOLD )


    # Renderer for the Interval column.
    #    For a background script, the value will be a number (as text) for the interval in minutes.
    #    For a non-background script, the interval does not apply and so a dash icon is rendered.
    #
    # https://stackoverflow.com/questions/52798356/python-gtk-treeview-column-data-display
    # https://stackoverflow.com/questions/27745585/show-icon-or-color-in-gtk-treeview-tree
    # https://developer.gnome.org/pygtk/stable/class-gtkcellrenderertext.html
    # https://developer.gnome.org/pygtk/stable/pango-constants.html#pango-alignment-constants
    def dataFunctionIntervalColumn( self, treeViewColumn, cellRenderer, treeModel, treeIter, data ):
        cellRenderer.set_visible( True )
        if treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_BACKGROUND ) == Gtk.STOCK_APPLY: # This is a background script.
            if isinstance( cellRenderer, Gtk.CellRendererPixbuf ):
                cellRenderer.set_visible( False )

            else:
                cellRenderer.set_property( "xalign", 0.5 )

        else:
            if isinstance( cellRenderer, Gtk.CellRendererText ):
                cellRenderer.set_visible( False )


    def populateScriptsTreeStore( self, scripts, treeView, selectGroup, selectScript ):
        treeStore = treeView.get_model()
        treeStore.clear()
        scriptsByGroup = self.getScriptsByGroup( scripts )
        groups = sorted( scriptsByGroup.keys(), key = str.lower )
        for group in groups:
            parent = treeStore.append( None, [ group, group, None, None, None, None, None, None, None, None ] )
            for script in sorted( scriptsByGroup[ group ], key = lambda script: script.getName().lower() ):
                playSound = Gtk.STOCK_APPLY if script.getPlaySound() else None
                showNotification = Gtk.STOCK_APPLY if script.getShowNotification() else None
                background = Gtk.STOCK_APPLY if type( script ) is Background else None

                if type( script ) is Background:
                    terminalOpen = Gtk.STOCK_REMOVE
                    intervalInMinutes = str( script.getIntervalInMinutes() )
                    intervalInMinutesDash = None
                    forceUpdate = Gtk.STOCK_APPLY if script.getForceUpdate() else None

                else:
                    terminalOpen = Gtk.STOCK_APPLY if script.getTerminalOpen() else None
                    intervalInMinutes = ""
                    intervalInMinutesDash = Gtk.STOCK_REMOVE
                    forceUpdate = Gtk.STOCK_REMOVE

                treeStore.append(
                    parent,
                    [ group, None, script.getName(), playSound, showNotification, background, terminalOpen, intervalInMinutes, forceUpdate, intervalInMinutesDash ] )

        if scripts:
            self.expandTreeAndSelect( treeView, selectGroup, selectScript, scriptsByGroup, groups )


    def populateBackgroundScriptsTreeStore( self, scripts, treeView, selectGroup, selectScript ):
        treeStore = treeView.get_model()
        treeStore.clear()
        scriptsByGroup = self.getScriptsByGroup( scripts, False, True )
        groups = sorted( scriptsByGroup.keys(), key = str.lower )
        for group in groups:
            parent = treeStore.append( None, [ group, group, None, None, None, None, None, None, None ] ) # Not all columns are used, but allows use of column definitions.

            for script in sorted( scriptsByGroup[ group ], key = lambda script: script.getName().lower() ):
                row = [
                    group,
                    None,
                    script.getName(),
                    Gtk.STOCK_APPLY if script.getPlaySound() else None,
                    Gtk.STOCK_APPLY if script.getShowNotification() else None,
                    None,
                    None,
                    str( script.getIntervalInMinutes() ),
                    Gtk.STOCK_APPLY if script.getForceUpdate() else None ]

                treeStore.append( parent, row )

        if scripts:
            self.expandTreeAndSelect( treeView, selectGroup, selectScript, scriptsByGroup, groups )


    def expandTreeAndSelect( self, treeView, selectGroup, selectScript, scriptsByGroup, groups ):
        pathAsString = "0:0"
        if selectGroup:
            groupIndex = groups.index( selectGroup )
            i = 0
            for script in sorted( scriptsByGroup[ selectGroup ], key = lambda script: script.getName().lower() ):
                if selectScript == script.getName():
                    pathAsString = str( groupIndex ) + ":" + str( i )
                    break

                i += 1

        treeView.expand_all()
        treePath = Gtk.TreePath.new_from_string( pathAsString )
        treeView.get_selection().select_path( treePath )
        treeView.set_cursor( treePath, None, False )
        if len( treeView.get_model() ):
            treeView.scroll_to_cell( treePath ) # Doesn't like to be called when empty.


    def onScriptSelection( self, treeSelection, treeView, textView, scripts ):
        group, name = self.__getGroupNameFromTreeView( treeView )
        commandText = ""
        if group and name:
            commandText = self.getScript( scripts, group, name ).getCommand()

        textView.get_buffer().set_text( commandText )


    def onScriptDoubleClick( self, scriptsTreeView, treePath, treeViewColumn, backgroundScriptsTreeView, textEntry, scripts ):
        self.onScriptEdit( None, scripts, scriptsTreeView, backgroundScriptsTreeView, textEntry )


    def onBackgroundScriptDoubleClick( self, treeView, treePath, treeViewColumn, textEntry, scripts ):
        group, name = self.__getGroupNameFromTreeView( treeView )
        if group and name:
            textEntry.insert_text( "[" + self.__createKey( group, name ) + "]", textEntry.get_position() )


    def onScriptCopy( self, button, scripts, scriptsTreeView, backgroundScriptsTreeView ):
        group, name = self.__getGroupNameFromTreeView( scriptsTreeView )
        if group and name:
            script = self.getScript( scripts, group, name )

            grid = self.create_grid()

            box = Gtk.Box( spacing = 6 )
            box.set_hexpand( True ) # Only need to set this once and all objects will expand.

            box.pack_start( Gtk.Label.new( _( "Group" ) ), False, False, 0 )

            scriptGroupCombo = Gtk.ComboBoxText.new_with_entry()
            scriptGroupCombo.set_tooltip_text( _(
                "The group to which the script belongs.\n\n" + \
                "Choose an existing group or enter a new one." ) )

            groups = sorted( self.getScriptsByGroup( scripts ).keys(), key = str.lower )
            for group in groups:
                scriptGroupCombo.append_text( group )

            scriptGroupCombo.set_active( groups.index( script.getGroup() ) )
            box.pack_start( scriptGroupCombo, True, True, 0 )

            grid.attach( box, 0, 0, 1, 1 )

            box = Gtk.Box( spacing = 6 )
            box.set_margin_top( 10 )

            box.pack_start( Gtk.Label.new( _( "Name" ) ), False, False, 0 )

            scriptNameEntry = Gtk.Entry()
            scriptNameEntry.set_tooltip_text( _( "The name of the script." ) )
            scriptNameEntry.set_text( script.getName() )
            box.pack_start( scriptNameEntry, True, True, 0 )

            grid.attach( box, 0, 1, 1, 1 )

            dialog = self.createDialog( scriptsTreeView, _( "Copy Script" ), grid )
            while True:
                dialog.show_all()
                if dialog.run() == Gtk.ResponseType.OK:
                    if scriptGroupCombo.get_active_text().strip() == "":
                        self.showMessage( dialog, _( "The group cannot be empty." ) )
                        scriptGroupCombo.grab_focus()
                        continue

                    if scriptNameEntry.get_text().strip() == "":
                        self.showMessage( dialog, _( "The name cannot be empty." ) )
                        scriptNameEntry.grab_focus()
                        continue

                    if self.getScript( scripts, scriptGroupCombo.get_active_text().strip(), scriptNameEntry.get_text().strip() ):
                        self.showMessage( dialog, _( "A script of the same group and name already exists." ) )
                        scriptGroupCombo.grab_focus()
                        continue

                    if type( script ) is Background:
                        newScript = Background(
                            scriptGroupCombo.get_active_text().strip(),
                            scriptNameEntry.get_text().strip(),
                            script.getCommand(),
                            script.getPlaySound(),
                            script.getShowNotification(),
                            script.getIntervalInMinutes(),
                            script.getForceUpdate() )

                    else:
                        newScript = NonBackground(
                            scriptGroupCombo.get_active_text().strip(),
                            scriptNameEntry.get_text().strip(),
                            script.getCommand(),
                            script.getPlaySound(),
                            script.getShowNotification(),
                            script.getTerminalOpen(),
                            False )

                    scripts.append( newScript )

                    self.populateScriptsTreeStore( scripts, scriptsTreeView, newScript.getGroup(), newScript.getName() )
                    self.populateBackgroundScriptsTreeStore(
                        scripts,
                        backgroundScriptsTreeView,
                        newScript.getGroup() if type( newScript ) is Background else "",
                        newScript.getName() if type( newScript ) is Background else "" )

                break

            dialog.destroy()


    def updateIndicatorTextEntry( self, textEntry, oldTag, newTag ):
        if newTag:
            textEntry.set_text( textEntry.get_text().replace( "[" + oldTag + "]", "[" + newTag + "]" ) )

        else:
            textEntry.set_text( textEntry.get_text().replace( "[" + oldTag + "]", "" ) )


    def onScriptRemove( self, button, scripts, scriptsTreeView, backgroundScriptsTreeView, commandTextView, textEntry ):
        group, name = self.__getGroupNameFromTreeView( scriptsTreeView )
        if group and name:
            if self.showOKCancel( scriptsTreeView, _( "Remove the selected script?" ) ) == Gtk.ResponseType.OK:
                i = 0
                for script in scripts:
                    if script.getGroup() == group and script.getName() == name:
                        del scripts[ i ]
                        self.populateScriptsTreeStore( scripts, scriptsTreeView, "", "" )
                        self.populateBackgroundScriptsTreeStore( scripts, backgroundScriptsTreeView, "", "" )
                        self.updateIndicatorTextEntry( textEntry, self.__createKey( group, name ), "" )
                        break

                    i += 1


    def onScriptAdd( self, button, scripts, scriptsTreeView, backgroundScriptsTreeView ):
        self.__addEditScript( None, scripts, scriptsTreeView, backgroundScriptsTreeView )


    def onScriptEdit( self, button, scripts, scriptsTreeView, backgroundScriptsTreeView, textEntry ):
        group, name = self.__getGroupNameFromTreeView( scriptsTreeView )
        if group and name:
            theScript = self.getScript( scripts, group, name )
            editedScript = self.__addEditScript( theScript, scripts, scriptsTreeView, backgroundScriptsTreeView )
            if editedScript:
                if type( theScript ) is Background and type( editedScript ) is NonBackground:
                    oldTag = self.__createKey( group, name )
                    self.updateIndicatorTextEntry( textEntry, oldTag, "" )

                if not( group == editedScript.getGroup() and name == editedScript.getName() ):
                    oldTag = self.__createKey( group, name )
                    newTag = self.__createKey( editedScript.getGroup(), editedScript.getName() )
                    self.updateIndicatorTextEntry( textEntry, oldTag, newTag )


    def __addEditScript( self, script, scripts, scriptsTreeView, backgroundScriptsTreeView ):
        add = True if script is None else False

        grid = self.create_grid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Group" ) ), False, False, 0 )

        groupCombo = Gtk.ComboBoxText.new_with_entry()
        groupCombo.set_tooltip_text( _(
            "The group to which the script belongs.\n\n" + \
            "Choose an existing group or enter a new one." ) )

        groups = sorted( self.getScriptsByGroup( scripts ).keys(), key = str.lower )
        for group in groups:
            groupCombo.append_text( group )

        if add:
            index = 0
            model, treeiter = scriptsTreeView.get_selection().get_selected()
            if treeiter:
                group = model[ treeiter ][ IndicatorScriptRunner.COLUMN_GROUP_INTERNAL ]
                index = groups.index( group )

        else:
            index = groups.index( script.getGroup() )

        groupCombo.set_active( index )

        box.pack_start( groupCombo, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Name" ) ), False, False, 0 )

        nameEntry = Gtk.Entry()
        nameEntry.set_tooltip_text( _( "The name of the script." ) )
        nameEntry.set_text( "" if add else script.getName() )

        box.pack_start( nameEntry, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label.new( _( "Command" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        commandTextView = Gtk.TextView()
        commandTextView.set_tooltip_text( _( "The terminal script/command, along with any arguments." ) )
        commandTextView.set_wrap_mode( Gtk.WrapMode.WORD )
        commandTextView.get_buffer().set_text( "" if add else script.getCommand() )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( commandTextView )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )

        box.pack_start( scrolledWindow, True, True, 0 )
        grid.attach( box, 0, 2, 1, 10 )

        soundCheckbutton = \
            self.create_checkbutton(
                _( "Play sound" ),
                _( "For non-background scripts, play a sound\n" + \
                   "on script completion.\n\n" + \
                   "For background scripts, play a sound\n" + \
                   "only if the script returns non-empty text." ),
                active = False if add else script.getPlaySound() )
#TODO Make sure this is converted okay
        # soundCheckbutton = Gtk.CheckButton.new_with_label( _( "Play sound" ) )
        # soundCheckbutton.set_tooltip_text( _(
        #     "For non-background scripts, play a sound\n" + \
        #     "on script completion.\n\n" + \
        #     "For background scripts, play a sound\n" + \
        #     "only if the script returns non-empty text." ) )
        # soundCheckbutton.set_active( False if add else script.getPlaySound() )
        grid.attach( soundCheckbutton, 0, 12, 1, 1 )

        notificationCheckbutton = \
            self.create_checkbutton(
                _( "Show notification" ),
                _( "For non-background scripts, show a\n" + \
                   "notification on script completion.\n\n" + \
                   "For background scripts, show a notification\n" + \
                   "only if the script returns non-empty text." ),
                active = False if add else script.getShowNotification() )
#TODO Make sure this is converted okay
        # notificationCheckbutton = Gtk.CheckButton.new_with_label( _( "Show notification" ) )
        # notificationCheckbutton.set_tooltip_text( _(
        #     "For non-background scripts, show a\n" + \
        #     "notification on script completion.\n\n" + \
        #     "For background scripts, show a notification\n" + \
        #     "only if the script returns non-empty text." ) )
        # notificationCheckbutton.set_active( False if add else script.getShowNotification() )
        grid.attach( notificationCheckbutton, 0, 13, 1, 1 )

        # scriptNonBackgroundRadio = Gtk.RadioButton.new_with_label_from_widget( None, _( "Non-background" ) )
        # scriptNonBackgroundRadio.set_active( True if add else type( script ) is NonBackground )
        # scriptNonBackgroundRadio.set_tooltip_text(
        #     "Non-background scripts are displayed\n" + \
        #     "in the menu and run when the user\n" + \
        #     "clicks on the corresponding menu item." )
        # grid.attach( scriptNonBackgroundRadio, 0, 14, 1, 1 )
#TODO Check above.
        scriptNonBackgroundRadio = \
            self.create_radiobutton(
                None,
                _( "Non-background" ),
                tooltip_text = _( "Non-background scripts are displayed\n" + \
                                  "in the menu and run when the user\n" + \
                                  "clicks on the corresponding menu item." ),
                active = True if add else type( script ) is NonBackground )

        grid.attach( scriptNonBackgroundRadio, 0, 14, 1, 1 )

        terminalCheckbutton = \
            self.create_checkbutton(
                _( "Leave terminal open" ),
                _( "Leave the terminal open on script completion." ),
                True if add else type( script ) is NonBackground,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = False if add else type( script ) is NonBackground and script.getTerminalOpen() )
#TODO Make sure this is converted okay
        # terminalCheckbutton = Gtk.CheckButton.new_with_label( _( "Leave terminal open" ) )
        # terminalCheckbutton.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # terminalCheckbutton.set_tooltip_text( _( "Leave the terminal open on script completion." ) )
        # terminalCheckbutton.set_active( False if add else type( script ) is NonBackground and script.getTerminalOpen() )
        # terminalCheckbutton.set_sensitive( True if add else type( script ) is NonBackground )
        grid.attach( terminalCheckbutton, 0, 15, 1, 1 )

        defaultScriptCheckbutton = \
            self.create_checkbutton(
                _( "Default script" ),
                _( "One script may be set as default\n" + \
                   "which is run on a middle mouse\n" + \
                   "click of the indicator icon.\n\n" + \
                   "Not supported on all desktops." ),
                True if add else type( script ) is NonBackground,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = False if add else type( script ) is NonBackground and script.getDefault() )
#TODO Make sure this is converted okay
        # defaultScriptCheckbutton = Gtk.CheckButton.new_with_label( _( "Default script" ) )
        # defaultScriptCheckbutton.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # defaultScriptCheckbutton.set_active( False if add else type( script ) is NonBackground and script.getDefault() )
        # defaultScriptCheckbutton.set_sensitive( True if add else type( script ) is NonBackground )
        # defaultScriptCheckbutton.set_tooltip_text( _(
        #     "One script may be set as default\n" + \
        #     "which is run on a middle mouse\n" + \
        #     "click of the indicator icon.\n\n" + \
        #     "Not supported on all desktops." ) )
        grid.attach( defaultScriptCheckbutton, 0, 16, 1, 1 )

        # scriptBackgroundRadio = Gtk.RadioButton.new_with_label_from_widget( scriptNonBackgroundRadio, _( "Background" ) )
        # scriptBackgroundRadio.set_active( False if add else type( script ) is Background )
        # scriptBackgroundRadio.set_tooltip_text(
        #     "Background scripts automatically run\n" + \
        #     "at the interval specified, but only if\n" + \
        #     "added to the icon text.\n\n" + \
        #     "Any exception which occurs during script\n" + \
        #     "execution will be logged to a file in the\n" + \
        #     "user's home directory and the script tag\n" + \
        #     "will remain in the icon text." )
        #
        # grid.attach( scriptBackgroundRadio, 0, 17, 1, 1 )
#TODO Check above.
        scriptBackgroundRadio = \
            self.create_radiobutton(
                scriptNonBackgroundRadio,
                _( "Background" ),
                tooltip_text = _( "Background scripts automatically run\n" + \
                                  "at the interval specified, but only if\n" + \
                                  "added to the icon text.\n\n" + \
                                  "Any exception which occurs during script\n" + \
                                  "execution will be logged to a file in the\n" + \
                                  "user's home directory and the script tag\n" + \
                                  "will remain in the icon text." ),
                active = False if add else type( script ) is Background )

        grid.attach( scriptBackgroundRadio, 0, 17, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT * 1.4 ) # Approximate alignment with the checkboxes above.

        label = Gtk.Label.new( _( "Interval" ) )
        label.set_sensitive( False if add else type( script ) is Background )
        box.pack_start( label, False, False, 0 )

        intervalSpinner = \
            self.create_spinbutton(
                script.getIntervalInMinutes() if type( script ) is Background else 60,
                1,
                10000,
                page_increment = 100,
                tooltip_text = _( "Interval, in minutes, between runs." ),
                sensitive = False if add else type( script ) is Background )

        # intervalSpinner.set_sensitive( False if add else type( script ) is Background )#TODO Check above is okay.

        box.pack_start( intervalSpinner, False, False, 0 )

        grid.attach( box, 0, 18, 1, 1 )

        forceUpdateCheckbutton = \
            self.create_checkbutton(
                _( "Force update" ),
                _( "If the script returns non-empty text\n" + \
                   "on its update, the script will run\n" + \
                   "on the next update of ANY script." ),
                True if add else type( script ) is Background,
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = False if add else type( script ) is Background and script.getForceUpdate() )
#TODO Make sure this is converted okay
        # forceUpdateCheckbutton = Gtk.CheckButton.new_with_label( _( "Force update" ) )
        # forceUpdateCheckbutton.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # forceUpdateCheckbutton.set_active( False if add else type( script ) is Background and script.getForceUpdate() )
        # forceUpdateCheckbutton.set_sensitive( True if add else type( script ) is Background )
        # forceUpdateCheckbutton.set_tooltip_text( _(
        #     "If the script returns non-empty text\n" + \
        #     "on its update, the script will run\n" + \
        #     "on the next update of ANY script." ) )
        grid.attach( forceUpdateCheckbutton, 0, 19, 1, 1 )

        scriptNonBackgroundRadio.connect( "toggled", self.onRadioOrCheckbox, True, terminalCheckbutton, defaultScriptCheckbutton )
        scriptNonBackgroundRadio.connect( "toggled", self.onRadioOrCheckbox, False, label, intervalSpinner, forceUpdateCheckbutton )
        scriptBackgroundRadio.connect( "toggled", self.onRadioOrCheckbox, True, label, intervalSpinner, forceUpdateCheckbutton )
        scriptBackgroundRadio.connect( "toggled", self.onRadioOrCheckbox, False, terminalCheckbutton, defaultScriptCheckbutton )

        dialog = self.createDialog( scriptsTreeView, _( "Add Script" ) if add else _( "Edit Script" ), grid )
        newScript = None
        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if groupCombo.get_active_text().strip() == "":
                    self.showMessage( dialog, _( "The group cannot be empty." ) )
                    groupCombo.grab_focus()
                    continue

                if nameEntry.get_text().strip() == "":
                    self.showMessage( dialog, _( "The name cannot be empty." ) )
                    nameEntry.grab_focus()
                    continue

                if self.getTextViewText( commandTextView ).strip() == "":
                    self.showMessage( dialog, _( "The command cannot be empty." ) )
                    commandTextView.grab_focus()
                    continue

                # Check for duplicates...
                #    For an add, find an existing script with the same group/name.
                #    For an edit, the group and/or name must change (and then match with an existing script other than the original).
                scriptOfSameNameAndGroupExists = self.getScript( scripts, groupCombo.get_active_text().strip(), nameEntry.get_text().strip() ) is not None
                editedScriptGroupOrNameDifferent = not add and ( groupCombo.get_active_text().strip() != script.getGroup() or nameEntry.get_text().strip() != script.getName() )
                if ( add or editedScriptGroupOrNameDifferent ) and scriptOfSameNameAndGroupExists:
                    self.showMessage( dialog, _( "A script of the same group and name already exists." ) )
                    groupCombo.grab_focus()
                    continue

                # For an edit, remove the original script...
                if not add:
                    i = 0
                    for skript in scripts:
                        if script.getGroup() == skript.getGroup() and script.getName() == skript.getName():
                            break

                        i += 1

                    del scripts[ i ]

                # If this script is marked as default (and is non-background),
                # check for an existing default script and if found, undefault it...
                if scriptNonBackgroundRadio.get_active() and defaultScriptCheckbutton.get_active():
                    i = 0
                    for skript in scripts:
                        if type( skript ) is NonBackground and skript.getDefault():
                            undefaultScript = NonBackground(
                                skript.getGroup(),
                                skript.getName(),
                                skript.getCommand(),
                                skript.getPlaySound(),
                                skript.getShowNotification(),
                                skript.getTerminalOpen(),
                                False )

                            del scripts[ i ]
                            scripts.append( undefaultScript )
                            break

                        i += 1

                # Create new script (add or edit) and add to scripts...
                if scriptBackgroundRadio.get_active():
                    newScript = Background(
                        groupCombo.get_active_text().strip(),
                        nameEntry.get_text().strip(),
                        self.getTextViewText( commandTextView ).strip(),
                        soundCheckbutton.get_active(),
                        notificationCheckbutton.get_active(),
                        intervalSpinner.get_value_as_int(),
                        forceUpdateCheckbutton.get_active() )

                else:
                    newScript = NonBackground(
                        groupCombo.get_active_text().strip(),
                        nameEntry.get_text().strip(),
                        self.getTextViewText( commandTextView ).strip(),
                        soundCheckbutton.get_active(),
                        notificationCheckbutton.get_active(),
                        terminalCheckbutton.get_active(),
                        defaultScriptCheckbutton.get_active() )

                scripts.append( newScript )

                self.populateScriptsTreeStore( scripts, scriptsTreeView, newScript.getGroup(), newScript.getName() )
                self.populateBackgroundScriptsTreeStore(
                    scripts,
                    backgroundScriptsTreeView,
                    newScript.getGroup() if type( newScript ) is Background else "",
                    newScript.getName() if type( newScript ) is Background else "" )

            break

        dialog.destroy()
        return newScript


    def getScript( self, scripts, group, name ):
        theScript = None
        for script in scripts:
            if script.getGroup() == group and script.getName() == name:
                theScript = script
                break

        return theScript


    def getScriptsByGroup( self, scripts, nonBackground = True, background = True ):
        scriptsByGroup = { }
        for script in scripts:
            if ( nonBackground and type( script ) is NonBackground ) or ( background and type( script ) is Background ):
                if script.getGroup() not in scriptsByGroup:
                    scriptsByGroup[ script.getGroup() ] = [ ]

                scriptsByGroup[ script.getGroup() ].append( script )

        return scriptsByGroup


    def __getGroupNameFromTreeView( self, treeView ):
        group = None
        name = None
        model, treeiter = treeView.get_selection().get_selected()
        if treeiter:
            group = model[ treeiter ][ IndicatorScriptRunner.COLUMN_GROUP_INTERNAL ]
            name = model[ treeiter ][ IndicatorScriptRunner.COLUMN_NAME ]

        return group, name


    # Each time a background script is run, cache the result.
    #
    # If for example, one script has an interval of five minutes and another script is hourly,
    # the hourly script should not be run any more frequently so use a cached result when the quicker script is run.
    #
    # Initialise the cache results and set a next update time in the past to force all (background) scripts to update first time.
    def initialiseBackgroundScripts( self ):
        self.backgroundScriptResults = { }
        self.backgroundScriptNextUpdateTime = { }
        today = datetime.datetime.now()
        for script in self.scripts:
            if type( script ) is Background:
                self.backgroundScriptResults[ self.__createKey( script.getGroup(), script.getName() ) ] = None
                self.backgroundScriptNextUpdateTime[ self.__createKey( script.getGroup(), script.getName() ) ] = today


    def __createKey( self, group, name ):
        return group + "::" + name


    def isBackgroundScriptInIndicatorText( self, script ):
        return '[' + self.__createKey( script.getGroup(), script.getName() ) + ']' in self.indicatorText


    def loadConfig( self, config ):
        self.hideGroups = config.get( IndicatorScriptRunner.CONFIG_HIDE_GROUPS, False )
        self.indicatorText = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT, "" )
        self.indicatorTextSeparator = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR, " | " )
        self.sendCommandToLog = config.get( IndicatorScriptRunner.CONFIG_SEND_COMMAND_TO_LOG, False )
        self.showScriptsInSubmenus = config.get( IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS, False )

        self.scripts = [ ]
        if config:
            scriptsNonBackground = config.get( self.CONFIG_SCRIPTS_NON_BACKGROUND, [ ] )
            for script in scriptsNonBackground:
                skript = NonBackground(
                    script[ IndicatorScriptRunner.JSON_GROUP ],
                    script[ IndicatorScriptRunner.JSON_NAME ],
                    script[ IndicatorScriptRunner.JSON_COMMAND ],
                    bool( script[ IndicatorScriptRunner.JSON_PLAY_SOUND ] ),
                    bool( script[ IndicatorScriptRunner.JSON_SHOW_NOTIFICATION ] ),
                    bool( script[ IndicatorScriptRunner.JSON_TERMINAL_OPEN ] ),
                    bool( script[ IndicatorScriptRunner.JSON_DEFAULT ] ) )

                self.scripts.append( skript )

            scriptsBackground = config.get( self.CONFIG_SCRIPTS_BACKGROUND, [ ] )
            for script in scriptsBackground:
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
            self.scripts.append( NonBackground( "Network", "Ping Google", "ping -c 3 www.google.com", False, False, False, False ) )
            self.scripts.append( NonBackground( "Network", "Public IP address", "notify-send -i " + self.get_icon_name() + " \"Public IP address: $(wget https://ipinfo.io/ip -qO -)\"", False, False, False, False ) )
            self.scripts.append( NonBackground( "Network", "Up or down", "if wget -qO /dev/null google.com > /dev/null; then notify-send -i " + self.get_icon_name() + " \"Internet is UP\"; else notify-send \"Internet is DOWN\"; fi", False, False, False, True ) )
            self.scripts.append( NonBackground( "Update", "autoclean | autoremove | update | dist-upgrade", "sudo apt-get autoclean && sudo apt-get -y autoremove && sudo apt-get update && sudo apt-get -y dist-upgrade", True, True, True, False ) )

            # Example background scripts.
            self.scripts.append( Background( "Network", "Internet Down", "if wget -qO /dev/null google.com > /dev/null; then echo \"\"; else echo \"Internet is DOWN\"; fi", False, True, 60, True ) )
            self.scripts.append( Background( "System", "Available Memory", "echo \"Free Memory: \"$(expr $( cat /proc/meminfo | grep MemAvailable | tr -d -c 0-9 ) / 1024)\" MB\"", False, False, 5, False ) )
            self.indicatorText = " [Network::Internet Down][System::Available Memory]"

            self.requestSaveConfig()

        self.initialiseBackgroundScripts()


    def saveConfig( self ):
        scriptsBackground = [ ]
        scriptsNonBackground = [ ]
        for script in self.scripts:
            if type( script ) == Background:
                scriptsBackground.append( [
                    script.getGroup(),
                    script.getName(),
                    script.getCommand(),
                    script.getPlaySound(),
                    script.getShowNotification(),
                    script.getIntervalInMinutes(),
                    script.getForceUpdate() ] )

            else:
                scriptsNonBackground.append( [
                    script.getGroup(),
                    script.getName(),
                    script.getCommand(),
                    script.getPlaySound(),
                    script.getShowNotification(),
                    script.getTerminalOpen(),
                    script.getDefault() ] )

        return {
            IndicatorScriptRunner.CONFIG_HIDE_GROUPS : self.hideGroups,
            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT : self.indicatorText,
            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR : self.indicatorTextSeparator,
            IndicatorScriptRunner.CONFIG_SCRIPTS_BACKGROUND : scriptsBackground,
            IndicatorScriptRunner.CONFIG_SCRIPTS_NON_BACKGROUND : scriptsNonBackground,
            IndicatorScriptRunner.CONFIG_SEND_COMMAND_TO_LOG : self.sendCommandToLog,
            IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS : self.showScriptsInSubmenus
        }


IndicatorScriptRunner().main()
