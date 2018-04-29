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


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  http://wiki.gnome.org/Projects/PyGObject/Threading
#  http://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/AppIndicator3-0.1
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html


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
    VERSION = "1.0.7"
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"
    COMMENTS = _( "Run a terminal command or script from an indicator." )

    CONFIG_HIDE_GROUPS = "hideGroups"
    CONFIG_SCRIPT_GROUP_DEFAULT = "scriptGroupDefault"
    CONFIG_SCRIPT_NAME_DEFAULT = "scriptNameDefault"
    CONFIG_SCRIPTS = "scripts"
    CONFIG_SHOW_SCRIPTS_IN_SUBMENUS = "showScriptsInSubmenus"

    COMMAND_NOTIFY_TAG_SCRIPT_NAME = "[SCRIPT_NAME]"
    COMMAND_NOTIFY = "notify-send -i " + ICON + " \\\"" + COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\\\" \\\"" + _( "...has completed." ) + "\\\""
    COMMAND_SOUND = "paplay /usr/share/sounds/freedesktop/stereo/complete.oga"


    def __init__( self ):
        logging.basicConfig( format = pythonutils.LOGGING_BASIC_CONFIG_FORMAT, level = pythonutils.LOGGING_BASIC_CONFIG_LEVEL, handlers = [ pythonutils.TruncatedFileHandler( IndicatorScriptRunner.LOG ) ] )
        self.dialogLock = threading.Lock()

        self.loadConfig()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorScriptRunner.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

        self.buildMenu()


    def main( self ): Gtk.main()


    def buildMenu( self ):
        menu = Gtk.Menu()

        if self.showScriptsInSubmenus:
            scriptsGroupedByName = self.getScriptsByGroup( self.scripts )
            for group in sorted( scriptsGroupedByName.keys(), key = str.lower ):
                menuItem = Gtk.MenuItem( group )
                menu.append( menuItem )
                subMenu = Gtk.Menu()
                menuItem.set_submenu( subMenu )
                self.addScriptsToMenu( scriptsGroupedByName[ group ], group, subMenu, "" )
        else:
            if self.hideGroups:
                for script in sorted( self.scripts, key = lambda script: script.getName().lower() ):
                    self.addScriptsToMenu( [ script ], script.getGroup(), menu, "" )

            else:
                scriptsGroupedByName = self.getScriptsByGroup( self.scripts )
                for group in sorted( scriptsGroupedByName.keys(), key = str.lower ):
                    menu.append( Gtk.MenuItem( group + "..." ) )
                    self.addScriptsToMenu( scriptsGroupedByName[ group ], group, menu, "        " )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, len( self.scripts ) > 0, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def addScriptsToMenu( self, scripts, group, menu, indent ):
        scripts.sort( key = lambda script: script.getName().lower() )
        for script in scripts:
            menuItem = Gtk.MenuItem( indent + script.getName() )
            menuItem.connect( "activate", self.onScript, script )
            menu.append( menuItem )
            if group == self.scriptGroupDefault and script.getName() == self.scriptNameDefault:
                self.indicator.set_secondary_activate_target( menuItem )


    def onScript( self, widget, script ):
        command = "x-terminal-emulator -e ${SHELL}'"

        if script.getDirectory() == "":
            command += " -c cd\ .;\""
        else:
            command += " -c cd\ " + script.getDirectory() + ";\""

        command += script.getCommand()

        if script.getShowNotification():
            command += " && " + IndicatorScriptRunner.COMMAND_NOTIFY.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME, script.getName() )

        if script.getPlaySound():
            command += " && " + IndicatorScriptRunner.COMMAND_SOUND

        command += "\";'"

        if script.isTerminalOpen():
            command += "${SHELL}"

        Thread( target = pythonutils.processCall, args = ( command, ) ).start()


    def onAbout( self, widget ):
        if self.dialogLock.acquire( blocking = False ):
            pythonutils.showAboutDialog(
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

            self.dialogLock.release()


    def onPreferences( self, widget ):
        if self.dialogLock.acquire( blocking = False ):
            self._onPreferences( widget )
            self.dialogLock.release()


    def _onPreferences( self, widget ):
        self.defaultScriptGroupCurrent = self.scriptGroupDefault
        self.defaultScriptNameCurrent = self.scriptNameDefault

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

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Group" ) ), False, False, 0 )

        scriptGroupComboBox = Gtk.ComboBoxText()
        scriptGroupComboBox.set_entry_text_column( 0 )
        scriptGroupComboBox.set_tooltip_text( _(
            "The group to which a script belongs.\n\n" + \
            "If a default script is specified,\n" + \
            "the group to which the script belongs\n" + \
            "will be initially selected." ) )

        box.pack_start( scriptGroupComboBox, True, True, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        scriptNameListStore = Gtk.ListStore( str, str, str, str, str ) # Script names, tick icon for terminal open, tick icon for play sound, tick icon for show notification, tick icon for default script.
        scriptNameListStore.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        scriptNameTreeView = Gtk.TreeView( scriptNameListStore )
        scriptNameTreeView.set_hexpand( True )
        scriptNameTreeView.set_vexpand( True )
        scriptNameTreeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        scriptNameTreeView.connect( "row-activated", self.onScriptNameDoubleClick, scriptGroupComboBox, copyOfScripts )
        scriptNameTreeView.set_tooltip_text( _(
            "List of scripts within the same group.\n\n" + \
            "If a default script has been nominated,\n" + \
            "that script will be initially selected." ) )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = 0 )
        treeViewColumn.set_expand( True )
        scriptNameTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Terminal" ), Gtk.CellRendererPixbuf(), stock_id = 1 )
        treeViewColumn.set_expand( False )
        scriptNameTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = 2 )
        treeViewColumn.set_expand( False )
        scriptNameTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = 3 )
        treeViewColumn.set_expand( False )
        scriptNameTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Default" ), Gtk.CellRendererPixbuf(), stock_id = 4 )
        treeViewColumn.set_expand( False )
        scriptNameTreeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( scriptNameTreeView )
        scrolledWindow.set_margin_top( 10 )

        grid.attach( scrolledWindow, 0, 1, 1, 15 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Directory" ) ), False, False, 0 )

        directoryEntry = Gtk.Entry()
        directoryEntry.set_tooltip_text( _( "The directory from which the script/command is executed." ) )
        directoryEntry.set_editable( False )

        box.pack_start( directoryEntry, True, True, 0 )

        grid.attach( box, 0, 16, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label( _( "Command" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        commandTextView = Gtk.TextView()
        commandTextView.set_tooltip_text( _( "The terminal script/command, along with any arguments." ) )
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
        addButton.connect( "clicked", self.onScriptAdd, copyOfScripts, scriptGroupComboBox, scriptNameTreeView )
        box.pack_start( addButton, True, True, 0 )

        editButton = Gtk.Button( _( "Edit" ) )
        editButton.set_tooltip_text( _( "Edit the selected script." ) )
        editButton.connect( "clicked", self.onScriptEdit, copyOfScripts, scriptGroupComboBox, scriptNameTreeView )
        box.pack_start( editButton, True, True, 0 )

        copyButton = Gtk.Button( _( "Copy" ) )
        copyButton.set_tooltip_text( _( "Duplicate the selected script." ) )
        copyButton.connect( "clicked", self.onScriptCopy, copyOfScripts, scriptGroupComboBox, scriptNameTreeView )
        box.pack_start( copyButton, True, True, 0 )

        removeButton = Gtk.Button( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected script." ) )
        removeButton.connect( "clicked", self.onScriptRemove, copyOfScripts, scriptGroupComboBox, scriptNameTreeView, directoryEntry, commandTextView )
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

        label = Gtk.Label( _( "Display" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        radioShowScriptsSubmenu = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show scripts in submenus" ) )
        radioShowScriptsSubmenu.set_tooltip_text( _( "Scripts of the same group are shown in submenus." ) )
        radioShowScriptsSubmenu.set_active( self.showScriptsInSubmenus )
        radioShowScriptsSubmenu.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )
        grid.attach( radioShowScriptsSubmenu, 0, 1, 1, 1 )

        radioShowScriptsIndented = Gtk.RadioButton.new_with_label_from_widget( radioShowScriptsSubmenu, _( "Show scripts grouped" ) )
        radioShowScriptsIndented.set_tooltip_text( _( "Scripts are shown within their respective group." ) )
        radioShowScriptsIndented.set_active( not self.showScriptsInSubmenus )
        radioShowScriptsIndented.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )
        grid.attach( radioShowScriptsIndented, 0, 2, 1, 1 )

        hideGroupsCheckbox = Gtk.CheckButton( _( "Hide groups" ) )
        hideGroupsCheckbox.set_active( self.hideGroups )
        hideGroupsCheckbox.set_sensitive( not self.showScriptsInSubmenus )
        hideGroupsCheckbox.set_margin_left( pythonutils.INDENT_WIDGET_LEFT * 2 )
        hideGroupsCheckbox.set_tooltip_text( _(
            "If checked, only scripts names are displayed.\n\n" + \
            "Otherwise, script names are indented within each group." ) )

        grid.attach( hideGroupsCheckbox, 0, 3, 1, 1 )

        radioShowScriptsSubmenu.connect( "toggled", self.onDisplayCheckboxes, radioShowScriptsSubmenu, hideGroupsCheckbox )
        radioShowScriptsIndented.connect( "toggled", self.onDisplayCheckboxes, radioShowScriptsSubmenu, hideGroupsCheckbox )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorScriptRunner.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 4, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        scriptGroupComboBox.connect( "changed", self.onScriptGroup, copyOfScripts, scriptNameListStore, scriptNameTreeView )
        scriptNameTreeView.get_selection().connect( "changed", self.onScriptName, scriptGroupComboBox, directoryEntry, commandTextView, copyOfScripts )
        self.populateScriptGroupCombo( copyOfScripts, scriptGroupComboBox, scriptNameTreeView, None, None )

        dialog = Gtk.Dialog( _( "Preferences" ), None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorScriptRunner.ICON )
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            self.showScriptsInSubmenus = radioShowScriptsSubmenu.get_active()
            self.hideGroups = hideGroupsCheckbox.get_active()
            self.scripts = copyOfScripts
            if len( self.scripts ) == 0:
                self.scriptGroupDefault = ""
                self.scriptNameDefault = ""
            else:
                self.scriptGroupDefault = self.defaultScriptGroupCurrent
                self.scriptNameDefault = self.defaultScriptNameCurrent

            self.saveConfig()
            pythonutils.setAutoStart( IndicatorScriptRunner.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            GLib.idle_add( self.buildMenu )

        dialog.destroy()


    def onDisplayCheckboxes( self, source, radioShowScriptsSubmenu, hideGroupsCheckbox ):
        hideGroupsCheckbox.set_sensitive( not radioShowScriptsSubmenu.get_active() )


    def onScriptGroup( self, scriptGroupComboBox, scripts, scriptNameListStore, scriptNameTreeView ):
        scriptGroup = scriptGroupComboBox.get_active_text()
        scriptNameListStore.clear()

        scriptNames = [ ]
        for script in scripts:
            if script.getGroup() == scriptGroup:
                scriptNames.append( script.getName() )

        scriptNames = sorted( scriptNames, key = str.lower )

        for scriptName in scriptNames:
            terminalOpen = None
            if self.getScript( scripts, scriptGroup, scriptName ).isTerminalOpen():
                terminalOpen = Gtk.STOCK_APPLY

            playSound = None
            if self.getScript( scripts, scriptGroup, scriptName ).getPlaySound():
                playSound = Gtk.STOCK_APPLY

            showNotification = None
            if self.getScript( scripts, scriptGroup, scriptName ).getShowNotification():
                showNotification = Gtk.STOCK_APPLY

            defaultScript = None
            if scriptGroup == self.defaultScriptGroupCurrent and scriptName == self.defaultScriptNameCurrent:
                defaultScript = Gtk.STOCK_APPLY

            scriptNameListStore.append( [ scriptName, terminalOpen, playSound, showNotification, defaultScript ] )

        scriptNameTreeView.get_selection().select_path( 0 )
        scriptNameTreeView.scroll_to_cell( Gtk.TreePath.new_from_string( "0" ) )


    def onScriptName( self, scriptNameTreeSelection, scriptGroupComboBox, directoryEntry, commandTextView, scripts ):
        scriptGroup = scriptGroupComboBox.get_active_text()
        model, treeiter = scriptNameTreeSelection.get_selected()
        if treeiter is not None:
            scriptName = model[ treeiter ][ 0 ]
            theScript = self.getScript( scripts, scriptGroup, scriptName )
            if theScript is not None:
                directoryEntry.set_text( theScript.getDirectory() )
                commandTextView.get_buffer().set_text( theScript.getCommand() )


    def onScriptCopy( self, button, scripts, scriptGroupComboBox, scriptNameTreeView ):
        scriptGroup = scriptGroupComboBox.get_active_text()
        model, treeiter = scriptNameTreeView.get_selection().get_selected()
        if scriptGroup is not None and treeiter is not None:
            scriptName = model[ treeiter ][ 0 ]
            script = self.getScript( scripts, scriptGroup, scriptName )

            grid = Gtk.Grid()
            grid.set_column_spacing( 10 )
            grid.set_row_spacing( 10 )
            grid.set_margin_left( 10 )
            grid.set_margin_right( 10 )
            grid.set_margin_top( 10 )
            grid.set_margin_bottom( 10 )

            box = Gtk.Box( spacing = 6 )

            box.pack_start( Gtk.Label( _( "Group" ) ), False, False, 0 )

            scriptGroupCombo = Gtk.ComboBoxText.new_with_entry()
            scriptGroupCombo.set_hexpand( True ) # Only need to set this once and all objects will expand.
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

            box.pack_start( Gtk.Label( _( "Name" ) ), False, False, 0 )

            scriptNameEntry = Gtk.Entry()
            scriptNameEntry.set_tooltip_text( _( "The name of the script." ) )
            scriptNameEntry.set_text( script.getName() )
            box.pack_start( scriptNameEntry, True, True, 0 )

            grid.attach( box, 0, 1, 1, 1 )

            dialog = Gtk.Dialog( _( "Copy Script" ), None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
            dialog.vbox.pack_start( grid, True, True, 0 )
            dialog.set_border_width( 5 )
            dialog.set_icon_name( IndicatorScriptRunner.ICON )

            while True:
                dialog.show_all()
                if dialog.run() == Gtk.ResponseType.OK:
                    if scriptGroupCombo.get_active_text().strip() == "":
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The group cannot be empty." ), INDICATOR_NAME )
                        scriptGroupCombo.grab_focus()
                        continue

                    if scriptNameEntry.get_text().strip() == "":
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The name cannot be empty." ), INDICATOR_NAME )
                        scriptNameEntry.grab_focus()
                        continue

                    if self.getScript( scripts, scriptGroupCombo.get_active_text().strip(), scriptNameEntry.get_text().strip() ) is not None:
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "A script of the same group and name already exists." ), INDICATOR_NAME )
                        scriptGroupCombo.grab_focus()
                        continue

                    newScript = Info( scriptGroupCombo.get_active_text().strip(),
                                      scriptNameEntry.get_text().strip(), 
                                      script.getDirectory(),
                                      script.getCommand(),
                                      script.isTerminalOpen() )

                    newScript.setPlaySound( script.getPlaySound() )
                    newScript.setShowNotification( script.getShowNotification() )

                    scripts.append( newScript )
                    self.populateScriptGroupCombo( scripts, scriptGroupComboBox, scriptNameTreeView, newScript.getGroup(), newScript.getName() )

                break

            dialog.destroy()


    def onScriptRemove( self, button, scripts, scriptGroupComboBox, scriptNameTreeView, directoryEntry, commandTextView ):
        scriptGroup = scriptGroupComboBox.get_active_text()
        model, treeiter = scriptNameTreeView.get_selection().get_selected()
        if scriptGroup is not None and treeiter is not None:
            scriptName = model[ treeiter ][ 0 ]
            theScript = self.getScript( scripts, scriptGroup, scriptName )
            if pythonutils.showOKCancel( None, _( "Remove the selected script?" ), INDICATOR_NAME ) == Gtk.ResponseType.OK:
                i = 0
                for script in scripts:
                    if script.getGroup() == scriptGroup and script.getName() == scriptName:
                        del scripts[ i ]
                        if scriptGroup not in self.getScriptsByGroup( scripts ):
                            scriptGroup = None

                        self.populateScriptGroupCombo( scripts, scriptGroupComboBox, scriptNameTreeView, scriptGroup, None )
                        if len( scripts ) == 0:
                            directoryEntry.set_text( "" )
                            commandTextView.get_buffer().set_text( "" )

                        break

                    i += 1


    def onScriptAdd( self, button, scripts, scriptGroupComboBox, scriptNameTreeView ):
        self.addEditScript( Info( "", "", "", "", False ), scripts, scriptGroupComboBox, scriptNameTreeView )


    def onScriptNameDoubleClick( self, scriptNameTreeView, scriptNameTreePath, scriptNameTreeViewColumn, scriptGroupComboBox, scripts ):
        self.onScriptEdit( None, scripts, scriptGroupComboBox, scriptNameTreeView )


    def onScriptEdit( self, button, scripts, scriptGroupComboBox, scriptNameTreeView ):
        scriptGroup = scriptGroupComboBox.get_active_text()
        model, treeiter = scriptNameTreeView.get_selection().get_selected()
        if scriptGroup is not None and treeiter is not None:
            scriptName = model[ treeiter ][ 0 ]
            theScript = self.getScript( scripts, scriptGroup, scriptName )
            self.addEditScript( theScript, scripts, scriptGroupComboBox, scriptNameTreeView )


    def addEditScript( self, script, scripts, scriptGroupComboBox, scriptNameTreeView ):
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Group" ) ), False, False, 0 )

        scriptGroupCombo = Gtk.ComboBoxText.new_with_entry()
        scriptGroupCombo.set_tooltip_text( _(
            "The group to which the script belongs.\n\n" + \
            "Choose an existing group or enter a new one." ) )

        groups = sorted( self.getScriptsByGroup( scripts ).keys(), key = str.lower )
        for group in groups:
            scriptGroupCombo.append_text( group )

        if script.getGroup() == "": 
            scriptGroupCombo.set_active( scriptGroupComboBox.get_active() )
        else:
            scriptGroupCombo.set_active( groups.index( script.getGroup() ) )

        box.pack_start( scriptGroupCombo, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Name" ) ), False, False, 0 )

        scriptNameEntry = Gtk.Entry()
        scriptNameEntry.set_tooltip_text( _( "The name of the script." ) )
        scriptNameEntry.set_text( script.getName() )

        box.pack_start( scriptNameEntry, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Directory" ) ), False, False, 0 )

        scriptDirectoryEntry = Gtk.Entry()
        scriptDirectoryEntry.set_text( script.getDirectory() )
        scriptDirectoryEntry.set_tooltip_text( _( "The directory from which the script/command is executed." ) )

        box.pack_start( scriptDirectoryEntry, True, True, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label( _( "Command" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        commandTextView = Gtk.TextView()
        commandTextView.set_tooltip_text( _( "The terminal script/command, along with any arguments." ) )
        commandTextView.set_wrap_mode( Gtk.WrapMode.WORD )
        commandTextView.get_buffer().set_text( script.getCommand() )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( commandTextView )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )

        box.pack_start( scrolledWindow, True, True, 0 )
        grid.attach( box, 0, 3, 1, 20 )

        terminalCheckbox = Gtk.CheckButton( _( "Leave terminal open" ) )
        terminalCheckbox.set_tooltip_text( _( "Leave the terminal open after the script completes." ) )
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
        defaultScriptCheckbox.set_active( script.getGroup() == self.defaultScriptGroupCurrent and script.getName() == self.defaultScriptNameCurrent )
        defaultScriptCheckbox.set_tooltip_text( _(
            "If checked, this script will be run on a\n" + \
            "middle mouse click of the indicator icon.\n\n" + \
            "Only one script can be the default." ) )

        grid.attach( defaultScriptCheckbox, 0, 26, 1, 1 )

        title = _( "Edit Script" )
        if script.getGroup() == "":
            title = _( "Add Script" )

        dialog = Gtk.Dialog( title, None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorScriptRunner.ICON )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if scriptGroupCombo.get_active_text().strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The group cannot be empty." ), INDICATOR_NAME )
                    scriptGroupCombo.grab_focus()
                    continue

                if scriptNameEntry.get_text().strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The name cannot be empty." ), INDICATOR_NAME )
                    scriptNameEntry.grab_focus()
                    continue

                if pythonutils.getTextViewText( commandTextView ).strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The command cannot be empty." ), INDICATOR_NAME )
                    commandTextView.grab_focus()
                    continue

                if script.getGroup() == "": # Adding a new script - check for duplicate.
                    if self.getScript( scripts, scriptGroupCombo.get_active_text().strip(), scriptNameEntry.get_text().strip() ) is not None:
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "A script of the same group and name already exists." ), INDICATOR_NAME )
                        scriptGroupCombo.grab_focus()
                        continue

                else: # Editing an existing script.
                    if script.isIdentical( Info( scriptGroupCombo.get_active_text().strip(), scriptNameEntry.get_text().strip(), scriptDirectoryEntry.get_text().strip(), pythonutils.getTextViewText( commandTextView ).strip(), terminalCheckbox.get_active() ) ):
                        pass # No change to the script, so should exit, but continue to handle the default script checkbox.

                    elif scriptGroupCombo.get_active_text().strip() == script.getGroup() and scriptNameEntry.get_text().strip() == script.getName():
                        pass # The group/name have not changed, but other parts have - so there is no chance of a clash.

                    else: # At this point either the script group or name has changed or both (and possibly the other script parameters). 
                        duplicate = False
                        for scriptInList in scripts:
                            if not scriptInList.isIdentical( script ):
                                if scriptGroupCombo.get_active_text().strip() == scriptInList.getGroup() and scriptNameEntry.get_text().strip() == scriptInList.getName():
                                    duplicate = True
                                    break

                        if duplicate:
                            pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "A script of the same group and name already exists." ), INDICATOR_NAME )
                            scriptGroupCombo.grab_focus()
                            continue

                    # Remove the existing script.
                    i = 0
                    for scriptInList in scripts:
                        if script.getGroup() == scriptInList.getGroup() and script.getName() == scriptInList.getName():
                            break

                        i += 1

                    del scripts[ i ]

                # The new script or the edit.
                newScript = Info( scriptGroupCombo.get_active_text().strip(),
                                  scriptNameEntry.get_text().strip(), 
                                  scriptDirectoryEntry.get_text().strip(),
                                  pythonutils.getTextViewText( commandTextView ).strip(),
                                  terminalCheckbox.get_active() )

                newScript.setPlaySound( soundCheckbox.get_active() )
                newScript.setShowNotification( notificationCheckbox.get_active() )

                scripts.append( newScript )

                if defaultScriptCheckbox.get_active():
                    self.defaultScriptGroupCurrent = scriptGroupCombo.get_active_text().strip()
                    self.defaultScriptNameCurrent = scriptNameEntry.get_text().strip()
                else:
                    if self.defaultScriptGroupCurrent == scriptGroupCombo.get_active_text().strip() and self.defaultScriptNameCurrent == scriptNameEntry.get_text().strip():
                        self.defaultScriptGroupCurrent = ""
                        self.defaultScriptNameCurrent = ""

                self.populateScriptGroupCombo( scripts, scriptGroupComboBox, scriptNameTreeView, newScript.getGroup(), newScript.getName() )

            break

        dialog.destroy()


    def getScript( self, scripts, scriptGroup, scriptName ):
        theScript = None
        for script in scripts:
            if script.getGroup() == scriptGroup and script.getName() == scriptName:
                theScript = script
                break

        return theScript


    # Script group/name must be valid OR group is None (name is ignored) OR group is valid and name is None.
    def populateScriptGroupCombo( self, scripts, scriptGroupComboBox, scriptNameTreeView, scriptGroup, scriptName ): 
        scriptGroupComboBox.remove_all()
        groups = sorted( self.getScriptsByGroup( scripts ), key = str.lower )
        for group in groups:
            scriptGroupComboBox.append_text( group )

        if scriptGroup is None:
            groupIndex = 0
            scriptIndex = 0
        else:
            if scriptName is None:
                groupIndex = groups.index( scriptGroup )
                scriptIndex = 0
            else:
                groupIndex = groups.index( scriptGroup )
                scriptNames = [ ]
                for script in scripts:
                    if script.getGroup() == scriptGroup:
                        scriptNames.append( script.getName() )

                scriptNames = sorted( scriptNames, key = str.lower )
                scriptIndex = scriptNames.index( scriptName )

        scriptGroupComboBox.set_active( groupIndex )
        scriptNameTreeView.get_selection().select_path( scriptIndex )


    def getScriptsByGroup( self, scripts ):
        scriptsGroupedByName = { }
        for script in scripts:
            if script.getGroup() not in scriptsGroupedByName:
                scriptsGroupedByName[ script.getGroup() ] = [ ]

            scriptsGroupedByName[ script.getGroup() ].append( script )

        return scriptsGroupedByName


    def loadConfig( self ):
        self.scriptGroupDefault = ""
        self.scriptNameDefault = ""
        self.scripts = [ ]
        self.showScriptsInSubmenus = False
        self.hideGroups = False

        config = pythonutils.loadConfig( INDICATOR_NAME, INDICATOR_NAME, logging )
        if len( config ) > 0:
            self.hideGroups = config.get( IndicatorScriptRunner.CONFIG_HIDE_GROUPS, self.hideGroups )
            self.scriptGroupDefault = config.get( IndicatorScriptRunner.CONFIG_SCRIPT_GROUP_DEFAULT, self.scriptGroupDefault )
            self.scriptNameDefault = config.get( IndicatorScriptRunner.CONFIG_SCRIPT_NAME_DEFAULT, self.scriptNameDefault )
            self.showScriptsInSubmenus = config.get( IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS, self.showScriptsInSubmenus )

            scripts = config.get( IndicatorScriptRunner.CONFIG_SCRIPTS, [ ] )
            defaultScriptFound = False
            for script in scripts:
                if script[ 0 ] == self.scriptGroupDefault and script[ 1 ] == self.scriptNameDefault:
                    defaultScriptFound = True

                self.scripts.append( Info( script[ 0 ], script[ 1 ], script[ 2 ], script[ 3 ], bool( script[ 4 ] ) ) )

                # Handle additions to scripts: show notification and play sound.
                if len( script ) == 7:
                    self.scripts[ -1 ].setPlaySound( script[ 5 ] )
                    self.scripts[ -1 ].setShowNotification( script[ 6 ] )

            if not defaultScriptFound:
                self.scriptGroupDefault = ""
                self.scriptNameDefault = ""

        else:
            self.scripts = [ ]
            self.scripts.append( Info( "Network", "Ping Google", "", "ping -c 3 www.google.com", False ) )
            self.scripts.append( Info( "Network", "Public IP address", "", "notify-send -i " + IndicatorScriptRunner.ICON + " \\\"Public IP address: $(wget http://ipinfo.io/ip -qO -)\\\"", False ) )
            self.scripts.append( Info( "Network", "Up or down", "", "if wget -qO /dev/null google.com > /dev/null; then notify-send -i " + IndicatorScriptRunner.ICON + " \\\"Internet is UP\\\"; else notify-send \\\"Internet is DOWN\\\"; fi", False ) )
            self.scriptGroupDefault = self.scripts[ -1 ].getGroup()
            self.scriptNameDefault = self.scripts[ -1 ].getName()
            self.scripts.append( Info( "Update", "autoclean | autoremove | update | dist-upgrade", "", "sudo apt-get autoclean && sudo apt-get -y autoremove && sudo apt-get update && sudo apt-get -y dist-upgrade", True ) )
            self.scripts[ -1 ].setPlaySound( True )
            self.scripts[ -1 ].setShowNotification( True )


    def saveConfig( self ):
        scripts = [ ]
        for script in self.scripts:
            scripts.append( [ script.getGroup(), script.getName(), script.getDirectory(), script.getCommand(), script.isTerminalOpen(), script.getPlaySound(), script.getShowNotification() ] )

        config = {
            IndicatorScriptRunner.CONFIG_HIDE_GROUPS: self.hideGroups,
            IndicatorScriptRunner.CONFIG_SCRIPT_GROUP_DEFAULT: self.scriptGroupDefault,
            IndicatorScriptRunner.CONFIG_SCRIPT_NAME_DEFAULT: self.scriptNameDefault,
            IndicatorScriptRunner.CONFIG_SCRIPTS: scripts,
            IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS: self.showScriptsInSubmenus
        }

        pythonutils.saveConfig( config, INDICATOR_NAME, INDICATOR_NAME, logging )


if __name__ == "__main__": IndicatorScriptRunner().main()