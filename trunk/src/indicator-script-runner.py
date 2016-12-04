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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Application indicator allowing a user to run a terminal command or script.


# https://developer.gnome.org/gnome-devel-demos
# http://python-gtk-3-tutorial.readthedocs.io
# http://lazka.github.io/pgi-docs


INDICATOR_NAME = "indicator-script-runner"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )

from gi.repository import AppIndicator3, GLib, Gtk
from script import Info
from threading import Thread

import copy, json, logging, os, pythonutils, threading


class IndicatorScriptRunner:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.2"
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    COMMENTS = _( "Run a terminal command or script from a GUI front-end." )

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_SCRIPT_NAME_DEFAULT = "scriptNameDefault"
    SETTINGS_SCRIPT_DESCRIPTION_DEFAULT = "scriptDescriptionDefault"
    SETTINGS_SCRIPTS = "scripts"
    SETTINGS_SHOW_SCRIPT_DESCRIPTIONS_AS_SUBMENUS = "showScriptDescriptionsAsSubmenus"

    COMMAND_NOTIFY_TAG_SCRIPT_NAME = "[SCRIPT_NAME]"
#TODO Unable to put " or ' around the script name/description (although this works directly in a terminal).
# Unable to use HTML for italic/bold.
# Would be nice (more readable) if the script description was quoted.
    COMMAND_NOTIFY = "notify-send -i " + ICON + " \\\"" + COMMAND_NOTIFY_TAG_SCRIPT_NAME + "...\\\" \\\"" + _( "...{0} has completed." ) + "\\\""

#TODO Before playing the audio, need to check if it exists?    
    COMMAND_SOUND = "paplay /usr/share/sounds/freedesktop/stereo/complete.oga"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorScriptRunner.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )
        self.dialog = None
        GLib.threads_init()
        self.lock = threading.Lock()
        self.loadSettings()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorScriptRunner.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.buildMenu()


    def main( self ): Gtk.main()


    def buildMenu( self ):
        scripts = self.getScriptsGroupedByName( self.scripts )
        menu = Gtk.Menu()
        if self.showScriptDescriptionsAsSubmenus:
            for scriptName in sorted( scripts.keys(), key = str.lower ):
                scriptNameMenuItem = Gtk.MenuItem( scriptName )
                subMenu = Gtk.Menu()
                scriptNameMenuItem.set_submenu( subMenu )
                menu.append( scriptNameMenuItem )
                self.addScriptsToMenu( scripts, scriptName, subMenu, "" )
        else:
            for scriptName in sorted( scripts.keys(), key = str.lower ):
                menu.append( Gtk.MenuItem( scriptName + "..." ) )
                self.addScriptsToMenu( scripts, scriptName, menu, "        " )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, len( scripts ) > 0, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()
        return menu


    def addScriptsToMenu( self, scripts, scriptName, menu, indent ):
        scripts[ scriptName ].sort( key = lambda script: script.getDescription().lower() )
        for script in scripts[ scriptName ]:
            menuItem = Gtk.MenuItem( indent + script.getDescription() )
            menuItem.connect( "activate", self.onScript, script )
            menu.append( menuItem )
            if scriptName == self.scriptNameDefault and script.getDescription() == self.scriptDescriptionDefault:
                self.indicator.set_secondary_activate_target( menuItem )


    def onScript( self, widget, script ):
        command = "x-terminal-emulator -e ${SHELL}'"

        if script.getDirectory() == "":
            command += " -c cd\ .;\""
        else:
            command += " -c cd\ " + script.getDirectory() + ";\""

        command += script.getCommand()

        if script.getShowNotification():
             command += " && " + IndicatorScriptRunner.COMMAND_NOTIFY.format( script.getDescription() ).replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME, script.getName() )

        if script.getPlaySound():
             command += " && " + IndicatorScriptRunner.COMMAND_SOUND

        command += "\";'"

        if script.isTerminalOpen():
            command += "${SHELL}"

        Thread( target = pythonutils.processCall, args = ( command, ) ).start()


    def onAbout( self, widget ):
        if self.dialog is None:
            self.dialog = pythonutils.createAboutDialog(
                [ IndicatorScriptRunner.AUTHOR ],
                IndicatorScriptRunner.COMMENTS, 
                [ ],
                "",
                Gtk.License.GPL_3_0,
                IndicatorScriptRunner.ICON,
                INDICATOR_NAME,
                IndicatorScriptRunner.WEBSITE,
                IndicatorScriptRunner.VERSION,
                _( "translator-credits" ),
                _( "View the" ),
                _( "text file." ),
                _( "changelog" ) )

            self.dialog.run()
            self.dialog.destroy()
            self.dialog = None
        else:
            self.dialog.present()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.defaultScriptNameCurrent = self.scriptNameDefault
        self.defaultScriptDescriptionCurrent = self.scriptDescriptionDefault

        copyOfScripts = copy.deepcopy( self.scripts )
        notebook = Gtk.Notebook()

        # User scripts.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )
        grid.set_row_homogeneous( False )
        grid.set_column_homogeneous( False )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Name" ) ), False, False, 0 )

        scriptNameComboBox = Gtk.ComboBoxText()
#TODO Add a tooltip which says the first script will be selected if no default exists).
        scriptNameComboBox.set_tooltip_text( _( "The name of a script object.\n\nScripts may share the same name,\nbut must have a different description." ) )
        scriptNameComboBox.set_entry_text_column( 0 )

        box.pack_start( scriptNameComboBox, True, True, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        scriptDescriptionListStore = Gtk.ListStore( str, str, str, str, str ) # Script descriptions, tick icon for terminal open, tick icon for play sound, tick icon for show notification, tick icon for default script.
        scriptDescriptionListStore.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        scriptDescriptionTreeView = Gtk.TreeView( scriptDescriptionListStore )
#TODO Add a tooltip which says the first script will be selected if no default exists).
        scriptDescriptionTreeView.set_tooltip_text( _( "List of scripts with same name,\nbut different descriptions." ) )
        scriptDescriptionTreeView.set_hexpand( True )
        scriptDescriptionTreeView.set_vexpand( True )
        scriptDescriptionTreeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        scriptDescriptionTreeView.connect( "row-activated", self.onScriptDescriptionDoubleClick, scriptNameComboBox, copyOfScripts )

        treeViewColumn = Gtk.TreeViewColumn( _( "Description" ), Gtk.CellRendererText(), text = 0 )
        treeViewColumn.set_expand( True )
        scriptDescriptionTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Terminal" ), Gtk.CellRendererPixbuf(), stock_id = 1 )
        treeViewColumn.set_expand( False )
        scriptDescriptionTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = 2 )
        treeViewColumn.set_expand( False )
        scriptDescriptionTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = 3 )
        treeViewColumn.set_expand( False )
        scriptDescriptionTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Default" ), Gtk.CellRendererPixbuf(), stock_id = 4 )
        treeViewColumn.set_expand( False )
        scriptDescriptionTreeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( scriptDescriptionTreeView )

        grid.attach( scrolledWindow, 0, 1, 1, 15 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Directory" ) ), False, False, 0 )

        directoryEntry = Gtk.Entry()
        directoryEntry.set_tooltip_text( _( "The directory from which the\nscript/command is executed." ) )
        directoryEntry.set_editable( False )

        box.pack_start( directoryEntry, True, True, 0 )

        grid.attach( box, 0, 16, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label( _( "Command" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        commandTextView = Gtk.TextView()
        commandTextView.set_tooltip_text( _( "The terminal script/command,\nalong with any arguments." ) )
        commandTextView.set_editable( False )
        commandTextView.set_wrap_mode( Gtk.WrapMode.WORD )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( commandTextView )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )

        box.pack_start( scrolledWindow, True, True, 0 )
        grid.attach( box, 0, 17, 1, 15 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )
        box.set_homogeneous( True )

        addButton = Gtk.Button( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new script." ) )
        addButton.connect( "clicked", self.onScriptAdd, copyOfScripts, scriptNameComboBox, scriptDescriptionTreeView )
        box.pack_start( addButton, True, True, 0 )

        editButton = Gtk.Button( _( "Edit" ) )
        editButton.set_tooltip_text( _( "Edit the selected script." ) )
        editButton.connect( "clicked", self.onScriptEdit, copyOfScripts, scriptNameComboBox, scriptDescriptionTreeView )
        box.pack_start( editButton, True, True, 0 )

        copyButton = Gtk.Button( _( "Copy" ) )
        copyButton.set_tooltip_text( _( "Duplicate the selected script." ) )
        copyButton.connect( "clicked", self.onScriptCopy, copyOfScripts, scriptNameComboBox, scriptDescriptionTreeView )
        box.pack_start( copyButton, True, True, 0 )

        removeButton = Gtk.Button( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected script." ) )
        removeButton.connect( "clicked", self.onScriptRemove, copyOfScripts, scriptNameComboBox, scriptDescriptionTreeView, directoryEntry, commandTextView )
        box.pack_start( removeButton, True, True, 0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 32, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Scripts" ) ) )

        # General settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showScriptDescriptionsAsSubmenusCheckbox = Gtk.CheckButton( _( "Show script descriptions as submenus" ) )
        showScriptDescriptionsAsSubmenusCheckbox.set_tooltip_text( _( "When checked, scripts with the same\nname are shown in subgroups.\n\nOtherwise, scripts appear in a single\nlist, grouped by name." ) )
        showScriptDescriptionsAsSubmenusCheckbox.set_active( self.showScriptDescriptionsAsSubmenus )
        showScriptDescriptionsAsSubmenusCheckbox.set_margin_top( 10 )
        grid.attach( showScriptDescriptionsAsSubmenusCheckbox, 0, 0, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorScriptRunner.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        scriptNameComboBox.connect( "changed", self.onScriptName, copyOfScripts, scriptDescriptionListStore, scriptDescriptionTreeView )
        scriptDescriptionTreeView.get_selection().connect( "changed", self.onScriptDescription, scriptNameComboBox, directoryEntry, commandTextView, copyOfScripts )
        self.populateScriptNameCombo( copyOfScripts, scriptNameComboBox, scriptDescriptionTreeView, "", "" )

        self.dialog = Gtk.Dialog( _( "Preferences" ), None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorScriptRunner.ICON )
        self.dialog.show_all()

        if self.dialog.run() == Gtk.ResponseType.OK:
            with self.lock:
                self.preferencesOpen = True
                self.showScriptDescriptionsAsSubmenus = showScriptDescriptionsAsSubmenusCheckbox.get_active()
                self.scripts = copyOfScripts
                if len( self.scripts ) == 0:
                    self.scriptNameDefault = ""
                    self.scriptDescriptionDefault = ""
                else:
                    self.scriptNameDefault = self.defaultScriptNameCurrent
                    self.scriptDescriptionDefault = self.defaultScriptDescriptionCurrent

                self.saveSettings()
                pythonutils.setAutoStart( IndicatorScriptRunner.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
                self.buildMenu()

        self.dialog.destroy()
        self.dialog = None


    def onScriptName( self, scriptNameComboBox, scripts, scriptDescriptionListStore, scriptDescriptionTreeView ):
        scriptName = scriptNameComboBox.get_active_text()
        scriptDescriptionListStore.clear()

        scriptDescriptions = [ ]
        for script in scripts:
            if script.getName() == scriptName:
                scriptDescriptions.append( script.getDescription() )

        scriptDescriptions = sorted( scriptDescriptions, key = str.lower )

        for scriptDescription in scriptDescriptions:
            terminalOpen = None
            if self.getScript( scripts, scriptName, scriptDescription ).isTerminalOpen():
                terminalOpen = Gtk.STOCK_APPLY

            playSound = None
            if self.getScript( scripts, scriptName, scriptDescription ).getPlaySound():
                playSound = Gtk.STOCK_APPLY

            showNotification = None
            if self.getScript( scripts, scriptName, scriptDescription ).getShowNotification():
                showNotification = Gtk.STOCK_APPLY

            defaultScript = None
            if scriptName == self.defaultScriptNameCurrent and scriptDescription == self.defaultScriptDescriptionCurrent:
                defaultScript = Gtk.STOCK_APPLY

            scriptDescriptionListStore.append( [ scriptDescription, terminalOpen, playSound, showNotification, defaultScript ] )

        scriptDescriptionTreeView.get_selection().select_path( 0 )
        scriptDescriptionTreeView.scroll_to_cell( Gtk.TreePath.new_from_string( "0" ) )


    def onScriptDescription( self, scriptDescriptionTreeSelection, scriptNameComboBox, directoryEntry, commandTextView, scripts ):
        scriptName = scriptNameComboBox.get_active_text()
        model, treeiter = scriptDescriptionTreeSelection.get_selected()
        if treeiter is not None:
            scriptDescription = model[ treeiter ][ 0 ]
            theScript = self.getScript( scripts, scriptName, scriptDescription )
            if theScript is not None:
                directoryEntry.set_text( theScript.getDirectory() )
                commandTextView.get_buffer().set_text( theScript.getCommand() )


    def onScriptCopy( self, button, scripts, scriptNameComboBox, scriptDescriptionTreeView ):
        scriptName = scriptNameComboBox.get_active_text()
        model, treeiter = scriptDescriptionTreeView.get_selection().get_selected()
        if scriptName is not None and treeiter is not None:
            scriptDescription = model[ treeiter ][ 0 ]
            script = self.getScript( scripts, scriptName, scriptDescription )

            grid = Gtk.Grid()
            grid.set_column_spacing( 10 )
            grid.set_row_spacing( 10 )
            grid.set_margin_left( 10 )
            grid.set_margin_right( 10 )
            grid.set_margin_top( 10 )
            grid.set_margin_bottom( 10 )

            box = Gtk.Box( spacing = 6 )
            box.set_margin_top( 10 )

            box.pack_start( Gtk.Label( _( "Name" ) ), False, False, 0 )

            scriptNameEntry = Gtk.Entry()
            scriptNameEntry.set_tooltip_text( _( "The name of the script object." ) )
            scriptNameEntry.set_text( script.getName() )
            scriptNameEntry.set_hexpand( True ) # Only need to set this once and all objects will expand.
            box.pack_start( scriptNameEntry, True, True, 0 )

            grid.attach( box, 0, 0, 1, 1 )

            box = Gtk.Box( spacing = 6 )
            box.set_margin_top( 10 )

            box.pack_start( Gtk.Label( _( "Description" ) ), False, False, 0 )

            scriptDescriptionEntry = Gtk.Entry()
            scriptDescriptionEntry.set_tooltip_text( _( "The description of the script object." ) )
            scriptDescriptionEntry.set_text( script.getDescription() )
            box.pack_start( scriptDescriptionEntry, True, True, 0 )

            grid.attach( box, 0, 1, 1, 1 )

            dialog = Gtk.Dialog( _( "Copy Script" ), self.dialog, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
            dialog.vbox.pack_start( grid, True, True, 0 )
            dialog.set_border_width( 5 )
            dialog.set_icon_name( IndicatorScriptRunner.ICON )

            while True:
                dialog.show_all()
                if dialog.run() == Gtk.ResponseType.OK:
                    if scriptNameEntry.get_text().strip() == "":
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The script name cannot be empty." ), INDICATOR_NAME )
                        scriptNameEntry.grab_focus()
                        continue

                    if scriptDescriptionEntry.get_text().strip() == "":
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The script description cannot be empty." ), INDICATOR_NAME )
                        scriptDescriptionEntry.grab_focus()
                        continue

                    if scriptNameEntry.get_text().strip() == scriptName and scriptDescriptionEntry.get_text().strip() == scriptDescription:
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "A script of the same name and description already exists." ), INDICATOR_NAME )
                        scriptNameEntry.grab_focus()
                        continue

                    newScript = Info( scriptNameEntry.get_text().strip(),
                                      scriptDescriptionEntry.get_text().strip(), 
                                      script.getDirectory(),
                                      script.getCommand(),
                                      script.isTerminalOpen() )

                    newScript.setPlaySound( script.getPlaySound() )
                    newScript.setShowNotification( script.getShowNotification() )

                    scripts.append( newScript )
                    self.populateScriptNameCombo( scripts, scriptNameComboBox, scriptDescriptionTreeView, newScript.getName(), newScript.getDescription() )

                break

            dialog.destroy()


    def onScriptRemove( self, button, scripts, scriptNameComboBox, scriptDescriptionTreeView, directoryEntry, commandTextView ):
        scriptName = scriptNameComboBox.get_active_text()
        model, treeiter = scriptDescriptionTreeView.get_selection().get_selected()
        if scriptName is not None and treeiter is not None:
            scriptDescription = model[ treeiter ][ 0 ]
            theScript = self.getScript( scripts, scriptName, scriptDescription )
            if pythonutils.showOKCancel( None, _( "Remove the selected script?" ), INDICATOR_NAME ) == Gtk.ResponseType.OK:
                i = 0
                for script in scripts:
                    if script.getName() == scriptName and script.getDescription() == scriptDescription:
                        break

                    i += 1

                del scripts[ i ]
                self.populateScriptNameCombo( scripts, scriptNameComboBox, scriptDescriptionTreeView, scriptName, "" )
                if len( scripts ) == 0:
                    directoryEntry.set_text( "" )
                    commandTextView.get_buffer().set_text( "" )


    def onScriptAdd( self, button, scripts, scriptNameComboBox, scriptDescriptionTreeView ):
        self.addEditScript( Info( "", "", "", "", False ), scripts, scriptNameComboBox, scriptDescriptionTreeView )


    def onScriptDescriptionDoubleClick( self, scriptDescriptionTreeView, scriptDescriptionTreePath, scriptDescriptionTreeViewColumn, scriptNameComboBox, scripts ):
        self.onScriptEdit( None, scripts, scriptNameComboBox, scriptDescriptionTreeView )


    def onScriptEdit( self, button, scripts, scriptNameComboBox, scriptDescriptionTreeView ):
        scriptName = scriptNameComboBox.get_active_text()
        model, treeiter = scriptDescriptionTreeView.get_selection().get_selected()
        if scriptName is not None and treeiter is not None:
            scriptDescription = model[ treeiter ][ 0 ]
            theScript = self.getScript( scripts, scriptName, scriptDescription )
            self.addEditScript( theScript, scripts, scriptNameComboBox, scriptDescriptionTreeView )


    def addEditScript( self, script, scripts, scriptNameComboBox, scriptDescriptionTreeView ):
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Name" ) ), False, False, 0 )

        scriptNameEntry = Gtk.Entry()
        scriptNameEntry.set_tooltip_text( _( "The name of the script object." ) )
        scriptNameEntry.set_text( script.getName() )

        box.pack_start( scriptNameEntry, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Description" ) ), False, False, 0 )

        scriptDescriptionEntry = Gtk.Entry()
        scriptDescriptionEntry.set_tooltip_text( _( "The description of the script object." ) )
        scriptDescriptionEntry.set_text( script.getDescription() )

        box.pack_start( scriptDescriptionEntry, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Directory" ) ), False, False, 0 )

        scriptDirectoryEntry = Gtk.Entry()
        scriptDirectoryEntry.set_tooltip_text( _( "The directory from which the\nscript/command is executed." ) )
        scriptDirectoryEntry.set_text( script.getDirectory() )

        box.pack_start( scriptDirectoryEntry, True, True, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label( _( "Command" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        commandTextView = Gtk.TextView()
        commandTextView.set_tooltip_text( _( "The terminal script/command,\nalong with any arguments." ) )
        commandTextView.set_wrap_mode( Gtk.WrapMode.WORD )
        commandTextView.get_buffer().set_text( script.getCommand() )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( commandTextView )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )

        box.pack_start( scrolledWindow, True, True, 0 )
        grid.attach( box, 0, 3, 1, 20 )

        terminalCheckbox = Gtk.CheckButton( _( "Leave terminal open" ) )
        terminalCheckbox.set_tooltip_text( _( "Leave the terminal open after\nthe script completes." ) )
        terminalCheckbox.set_active( script.isTerminalOpen() )

        grid.attach( terminalCheckbox, 0, 23, 1, 1 )

        soundCheckbox = Gtk.CheckButton( _( "Play sound" ) )
        soundCheckbox.set_tooltip_text( _( "Play a beep on script completion." ) )
        soundCheckbox.set_active( script.getPlaySound() )

        grid.attach( soundCheckbox, 0, 24, 1, 1 )

        notificationCheckbox = Gtk.CheckButton( _( "Show notification" ) )
        notificationCheckbox.set_tooltip_text( _( "Show a notification on script completion." ) )
        notificationCheckbox.set_active( script.getShowNotification() )

        grid.attach( notificationCheckbox, 0, 25, 1, 1 )

        defaultScriptCheckbox = Gtk.CheckButton( _( "Default script" ) )
        defaultScriptCheckbox.set_active( script.getName() == self.defaultScriptNameCurrent and script.getDescription() == self.defaultScriptDescriptionCurrent )
        defaultScriptCheckbox.set_tooltip_text( _( "If checked, this script will be run\non a middle mouse click of the\nindicator icon.\n\nOnly one script can be the default!" ) )

        grid.attach( defaultScriptCheckbox, 0, 26, 1, 1 )

        title = _( "Edit Script" )
        if script.getName() == "":
            title = _( "Add Script" )

        dialog = Gtk.Dialog( title, self.dialog, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorScriptRunner.ICON )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if scriptNameEntry.get_text().strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The script name cannot be empty." ), INDICATOR_NAME )
                    scriptNameEntry.grab_focus()
                    continue

                if scriptDescriptionEntry.get_text().strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The script description cannot be empty." ), INDICATOR_NAME )
                    scriptDescriptionEntry.grab_focus()
                    continue

                if pythonutils.getTextViewText( commandTextView ).strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The script command cannot be empty." ), INDICATOR_NAME )
                    commandTextView.grab_focus()
                    continue

                if script.getName() == "": # Adding a new script - check for duplicate.
                    if self.getScript( scripts, scriptNameEntry.get_text().strip(), scriptDescriptionEntry.get_text().strip() ) is not None:
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "A script of the same name and description already exists." ), INDICATOR_NAME )
                        scriptNameEntry.grab_focus()
                        continue

                else: # Editing an existing script.
                    if script.isIdentical( Info( scriptNameEntry.get_text().strip(), scriptDescriptionEntry.get_text().strip(), scriptDirectoryEntry.get_text().strip(), pythonutils.getTextViewText( commandTextView ).strip(), terminalCheckbox.get_active() ) ):
                        pass # No change to the script, so should exit, but continue to handle the default script checkbox.

                    elif scriptNameEntry.get_text().strip() == script.getName() and scriptDescriptionEntry.get_text().strip() == script.getDescription():
                        pass # The name/description have not changed, but other parts have - so there is no chance of a clash.

                    else: # At this point either the script name or description has changed or both (and possibly the other script parameters). 
                        duplicate = False
                        for scriptInList in scripts:
                            if not scriptInList.isIdentical( script ):
                                if scriptNameEntry.get_text().strip() == scriptInList.getName() and scriptDescriptionEntry.get_text().strip() == scriptInList.getDescription():
                                    duplicate = True
                                    break

                        if duplicate:
                            pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "A script of the same name and description already exists." ), INDICATOR_NAME )
                            scriptNameEntry.grab_focus()
                            continue

                    # Remove the existing script.
                    i = 0
                    for scriptInList in scripts:
                        if script.getName() == scriptInList.getName() and script.getDescription() == scriptInList.getDescription():
                            break

                        i += 1

                    del scripts[ i ]

                # The new script or the edit.
                newScript = Info( scriptNameEntry.get_text().strip(),
                                  scriptDescriptionEntry.get_text().strip(), 
                                  scriptDirectoryEntry.get_text().strip(),
                                  pythonutils.getTextViewText( commandTextView ).strip(),
                                  terminalCheckbox.get_active() )

                newScript.setPlaySound( soundCheckbox.get_active() )
                newScript.setShowNotification( notificationCheckbox.get_active() )

                scripts.append( newScript )

                if defaultScriptCheckbox.get_active():
                    self.defaultScriptNameCurrent = scriptNameEntry.get_text().strip()
                    self.defaultScriptDescriptionCurrent = scriptDescriptionEntry.get_text().strip()
                else:
                    if self.defaultScriptNameCurrent == scriptNameEntry.get_text().strip() and self.defaultScriptDescriptionCurrent == scriptDescriptionEntry.get_text().strip():
                        self.defaultScriptNameCurrent = ""
                        self.defaultScriptDescriptionCurrent = ""

                self.populateScriptNameCombo( scripts, scriptNameComboBox, scriptDescriptionTreeView, newScript.getName(), newScript.getDescription() )

            break

        dialog.destroy()


    def getScript( self, scripts, scriptName, scriptDescription ):
        theScript = None
        for script in scripts:
            if script.getName() == scriptName and script.getDescription() == scriptDescription:
                theScript = script
                break

        return theScript


    def populateScriptNameComboORIG( self, scripts, scriptNameComboBox, scriptDescriptionTreeView, scriptName, scriptDescription ): # Script name/description must be valid values or "".
        scriptNameComboBox.remove_all()
        for name in sorted( self.getScriptsGroupedByName( scripts ), key = str.lower ):
            scriptNameComboBox.append_text( name )

        if scriptName == "":
            if self.scriptNameDefault == "" :
                scriptNameComboBox.set_active( 0 )
            else:
                i = sorted( self.getScriptsGroupedByName( scripts ), key = str.lower ).index( self.scriptNameDefault )
                scriptNameComboBox.set_active( i )
#TODO Select the script description!
        else:
            i = 0
            iter = scriptNameComboBox.get_model().get_iter_first()
            while iter is not None:
                if scriptNameComboBox.get_model().get_value( iter, 0 ) == scriptName:
                    scriptNameComboBox.set_active( i )
                    break

                iter = scriptNameComboBox.get_model().iter_next( iter )
                i += 1

            if iter is None: # Could not find the script name (happens when the last script of the given name is removed.)
                scriptNameComboBox.set_active( 0 )
            else: # A script name was found and has been selected.
                if scriptDescription == "":
                    scriptDescriptionTreeView.get_selection().select_path( 0 )
                else: # Select the description - the description must exist otherwise there is some coding error elsewhere.
                    i = 0
                    iter = scriptDescriptionTreeView.get_model().get_iter_first()
                    while iter is not None:
                        if scriptDescriptionTreeView.get_model().get_value( iter, 0 ) == scriptDescription:
                            scriptDescriptionTreeView.get_selection().select_path( i )
                            scriptDescriptionTreeView.scroll_to_cell( Gtk.TreePath.new_from_string( str( i ) ) )
                            break

                        iter = scriptDescriptionTreeView.get_model().iter_next( iter )
                        i += 1


#TODO Test every call to this function.
    def populateScriptNameCombo( self, scripts, scriptNameComboBox, scriptDescriptionTreeView, scriptName, scriptDescription ): # Script name/description must be valid values or "".
        scriptNameComboBox.remove_all()
        for name in sorted( self.getScriptsGroupedByName( scripts ), key = str.lower ):
            scriptNameComboBox.append_text( name )

        if scriptName == "":
            scriptName = self.scriptNameDefault
            scriptDescription = self.scriptDescriptionDefault

        try:
            i = sorted( self.getScriptsGroupedByName( scripts ), key = str.lower ).index( scriptName )
            scriptNameComboBox.set_active( i )

            scriptDescriptions = [ ]
            for script in scripts:
                if script.getName() == scriptName:
                    scriptDescriptions.append( script.getDescription() )

            scriptDescriptions = sorted( scriptDescriptions, key = str.lower )
            scriptDescriptionTreeView.get_selection().select_path( scriptDescriptions.index( scriptDescription ) )

        except ValueError: # Triggered when the last script (of a given name) is removed or when there is no default script.
            scriptNameComboBox.set_active( 0 ) #TODO Test this...need to select an empty script description?  The first description should be selected by default.


    def getScriptsGroupedByName( self, scripts ):
        scriptsGroupedByName = { }
        for script in scripts:
            if script.getName() not in scriptsGroupedByName:
                scriptsGroupedByName[ script.getName() ] = [ ]

            scriptsGroupedByName[ script.getName() ].append( script )

        return scriptsGroupedByName


    def loadSettings( self ):
        self.scriptNameDefault = ""
        self.scriptDescriptionDefault = ""
        self.scripts = [ ]
        self.showScriptDescriptionsAsSubmenus = False
        if os.path.isfile( IndicatorScriptRunner.SETTINGS_FILE ):
            try:
                with open( IndicatorScriptRunner.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.scriptNameDefault = settings.get( IndicatorScriptRunner.SETTINGS_SCRIPT_NAME_DEFAULT, self.scriptNameDefault )
                self.scriptDescriptionDefault = settings.get( IndicatorScriptRunner.SETTINGS_SCRIPT_DESCRIPTION_DEFAULT, self.scriptDescriptionDefault )
                scripts = settings.get( IndicatorScriptRunner.SETTINGS_SCRIPTS, [ ] )
                self.showScriptDescriptionsAsSubmenus = settings.get( IndicatorScriptRunner.SETTINGS_SHOW_SCRIPT_DESCRIPTIONS_AS_SUBMENUS, self.showScriptDescriptionsAsSubmenus )
                for script in scripts:
                    self.scripts.append( Info( script[ 0 ], script[ 1 ], script[ 2 ], script[ 3 ], bool( script[ 4 ] ) ) )

                    # Handle additions to scripts: show notification and play sound.
                    if len( script ) == 7:
                        self.scripts[ -1 ].setPlaySound( script[ 5 ] )
                        self.scripts[ -1 ].setShowNotification( script[ 6 ] )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorScriptRunner.SETTINGS_FILE )
        else:
            self.scripts = [ ]
            self.scripts.append( Info( "Network", "Ping Google", "", "ping -c 5 www.google.com", False ) )
            self.scripts.append( Info( "Network", "Public IP address", "", "notify-send -i " + IndicatorScriptRunner.ICON + " \\\"Public IP address: $(wget http://ipinfo.io/ip -qO -)\\\"", False ) )
            self.scripts.append( Info( "Network", "Up or down", "", "if wget -qO /dev/null google.com > /dev/null; then notify-send -i " + IndicatorScriptRunner.ICON + " \\\"Internet is UP\\\"; else notify-send \\\"Internet is DOWN\\\"; fi", False ) )
            self.scriptNameDefault = self.scripts[ -1 ].getName()
            self.scriptDescriptionDefault = self.scripts[ -1 ].getDescription()
            self.scripts.append( Info( "Update", "autoclean | autoremove | update | dist-upgrade", "", "sudo apt-get autoclean && sudo apt-get -y autoremove && sudo apt-get update && sudo apt-get -y dist-upgrade", True ) )
            self.scripts[ -1 ].setPlaySound( True )
            self.scripts[ -1 ].setShowNotification( True )


    def saveSettings( self ):
        try:
            scripts = [ ]
            for script in self.scripts:
                scripts.append( [ script.getName(), script.getDescription(), script.getDirectory(), script.getCommand(), script.isTerminalOpen(), script.getPlaySound(), script.getShowNotification() ] )

            settings = {
                IndicatorScriptRunner.SETTINGS_SCRIPT_NAME_DEFAULT: self.scriptNameDefault,
                IndicatorScriptRunner.SETTINGS_SCRIPT_DESCRIPTION_DEFAULT: self.scriptDescriptionDefault,
                IndicatorScriptRunner.SETTINGS_SCRIPTS: scripts,
                IndicatorScriptRunner.SETTINGS_SHOW_SCRIPT_DESCRIPTIONS_AS_SUBMENUS: self.showScriptDescriptionsAsSubmenus
            }

            with open( IndicatorScriptRunner.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorScriptRunner.SETTINGS_FILE )


if __name__ == "__main__": IndicatorScriptRunner().main()