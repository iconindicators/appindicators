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


# Application indicator allowing a user to run a terminal command or script.


INDICATOR_NAME = "indicator-script-runner"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )

from gi.repository import Gtk, Pango
from script import Info
from threading import Thread

import copy, datetime, indicatorbase


class IndicatorScriptRunner( indicatorbase.IndicatorBase ):

    CONFIG_HIDE_GROUPS = "hideGroups"
    CONFIG_INDICATOR_TEXT = "indicatorText"
    CONFIG_INDICATOR_TEXT_SEPARATOR = "indicatorTextSeparator"
    CONFIG_SCRIPT_GROUP_DEFAULT = "scriptGroupDefault"
    CONFIG_SCRIPT_NAME_DEFAULT = "scriptNameDefault"
    CONFIG_SCRIPTS = "scripts"
    CONFIG_SHOW_SCRIPTS_IN_SUBMENUS = "showScriptsInSubmenus"

    COMMAND_NOTIFY_TAG_SCRIPT_NAME = "[SCRIPT_NAME]"
    COMMAND_NOTIFY_TAG_SCRIPT_RESULT = "[SCRIPT_RESULT]"
    COMMAND_NOTIFY_BACKGROUND = "notify-send -i " + INDICATOR_NAME + " \"" + COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" \"" + COMMAND_NOTIFY_TAG_SCRIPT_RESULT + "\""
    COMMAND_NOTIFY_NON_BACKGROUND = "notify-send -i " + INDICATOR_NAME + " \"" + COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" \"" + _( "...has completed." ) + "\""
    COMMAND_SOUND = "paplay /usr/share/sounds/freedesktop/stereo/complete.oga"

    # Data model columns used by...
    #    the table to display all scripts;
    #    the table to display background scripts.
    COLUMN_TAG_GROUP_INTERNAL = 0 # Never shown; used when the script group is needed by decision logic.
    COLUMN_TAG_GROUP = 1 # Valid when displaying a row containing just the group; otherwise empty when displaying a script name and attributes.
    COLUMN_TAG_NAME = 2 # Script name.
    COLUMN_TAG_SOUND = 3 # Icon name for the APPLY icon; None otherwise.
    COLUMN_TAG_NOTIFICATION = 4 # Icon name for the APPLY icon; None otherwise.
    COLUMN_TAG_BACKGROUND = 5 # Icon name for the APPLY icon; None otherwise.
    COLUMN_TAG_TERMINAL = 6 # Icon name for the APPLY icon; None otherwise.
    COLUMN_TAG_INTERVAL = 7 # Numeric amount as a string.
    COLUMN_TAG_REMOVE = 8 # Icon name for the REMOVE icon; None otherwise.


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.16",
            copyrightStartYear = "2016",
            comments = _( "Run a terminal command or script;\ndisplay script results in the icon label." ) )


    def update( self, menu ):
        self.updateMenu( menu )

        now = datetime.datetime.now()
        self.updateBackgroundScripts( now )
        self.setLabel( self.processTags( self.indicatorText, self.indicatorTextSeparator, self.__processTags, now ) )

        # Calculate next update...
        nextUpdate = now + datetime.timedelta( hours = 100 ) # Set an update time well into the (immediate) future.
        for script in self.scripts:
            key = self.__createKey( script.getGroup(), script.getName() )
            if script.getBackground() and self.backgroundScriptNextUpdateTime[ key ] < nextUpdate:
                nextUpdate = self.backgroundScriptNextUpdateTime[ key ]

        nextUpdateInSeconds = int( ( nextUpdate - now ).total_seconds() )
        return 60 if nextUpdateInSeconds < 60 else nextUpdateInSeconds
#TODO Need to test that the timing works...
# On each run dump the interval for each background script,
# the number of minutes until the next update
# and the time of each update.


    def updateMenu( self, menu ):
        if self.showScriptsInSubmenus:
            scriptsByGroup = self.getScriptsByGroup( self.scripts, True, False )
            indent = self.indent( 0, 1 )
            for group in sorted( scriptsByGroup.keys(), key = str.lower ):
                menuItem = Gtk.MenuItem( group )
                menu.append( menuItem )
                subMenu = Gtk.Menu()
                menuItem.set_submenu( subMenu )
                self.addScriptsToMenu( scriptsByGroup[ group ], group, subMenu, indent )
        else:
            if self.hideGroups:
                for script in sorted( self.scripts, key = lambda script: script.getName().lower() ):
                    if not script.getBackground():
                        self.addScriptsToMenu( [ script ], script.getGroup(), menu, "" )

            else:
                scriptsByGroup = self.getScriptsByGroup( self.scripts, True, False )
                indent = self.indent( 1, 1 )
                for group in sorted( scriptsByGroup.keys(), key = str.lower ):
                    menu.append( Gtk.MenuItem( group + "..." ) )
                    self.addScriptsToMenu( scriptsByGroup[ group ], group, menu, indent )


    def addScriptsToMenu( self, scripts, group, menu, indent ):
        scripts.sort( key = lambda script: script.getName().lower() )
        for script in scripts:
            menuItem = Gtk.MenuItem.new_with_label( indent + script.getName() )
            menuItem.connect( "activate", self.onScriptMenuItem, script )
            menu.append( menuItem )
            if group == self.scriptGroupDefault and script.getName() == self.scriptNameDefault:
                self.secondaryActivateTarget = menuItem


    def onScriptMenuItem( self, menuItem, script ):
        terminal = self.getTerminal()
        terminalExecutionFlag = self.getTerminalExecutionFlag( terminal )
        command = terminal + " " + terminalExecutionFlag + " ${SHELL} -c '"

        command += script.getCommand()

        if script.getShowNotification():
            command += "; " + IndicatorScriptRunner.COMMAND_NOTIFY_NON_BACKGROUND.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME, script.getName() )

        if script.getPlaySound():
            command += "; " + IndicatorScriptRunner.COMMAND_SOUND

        if script.getTerminalOpen():
            command += "; ${SHELL}"

        command += "'"
        Thread( target = self.processCall, args = ( command, ) ).start()


    def updateBackgroundScripts( self, now ):
        for script in self.scripts:
            key = self.__createKey( script.getGroup(), script.getName() )
            if script.getBackground():
                if self.backgroundScriptNextUpdateTime[ key ] < now:
                    commandResult = self.processGet( script.getCommand() ).strip()
                    self.backgroundScriptResult[ key ] = commandResult
                    self.backgroundScriptNextUpdateTime[ key ] = now + datetime.timedelta( minutes = script.getIntervalInMinutes() )

                commandResult = self.backgroundScriptResult[ key ]

                if script.getPlaySound() and commandResult:
                    self.processCall( IndicatorScriptRunner.COMMAND_SOUND )

                if script.getShowNotification() and commandResult:
                    notificationCommand = IndicatorScriptRunner.COMMAND_NOTIFY_BACKGROUND
                    notificationCommand = notificationCommand.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME, script.getName().replace( '-', '\\-' ) )
                    notificationCommand = notificationCommand.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_RESULT, commandResult.replace( '-', '\\-' ) )
                    self.processCall( notificationCommand )


    # Called by base class to process data tags.
    def __processTags( self, textToProcess, arguments ):
        text = textToProcess
        now = arguments[ 0 ]
        for script in self.scripts:
            key = self.__createKey( script.getGroup(), script.getName() )
            if script.getBackground() and "[" + key + "]" in text:
                commandResult = self.backgroundScriptResult[ key ]
                text = text.replace( "[" + key + "]", commandResult )

        return text


    def onPreferences( self, dialog ):
        self.defaultScriptGroupCurrent = self.scriptGroupDefault #TODO Check if all this makes sense...can't we get the default from the current list of scripts (the copy)?
        self.defaultScriptNameCurrent = self.scriptNameDefault
        copyOfScripts = copy.deepcopy( self.scripts )

        notebook = Gtk.Notebook()

        # Scripts.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        # Define these here so that widgets can connect to handle events.        
        backgroundScriptsTreeView = Gtk.TreeView.new_with_model( Gtk.TreeStore( str, str, str, str, str, str, str, str ) ) # Extra redundant columns, but allows the reuse of the column definitions.
        indicatorTextEntry = Gtk.Entry()

        treeView = Gtk.TreeView.new_with_model( Gtk.TreeStore( str, str, str, str, str, str, str, str, str ) )
        treeView.set_hexpand( True )
        treeView.set_vexpand( True )
        treeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE ) #TODO Using BROWSE instead of SINGLE seems to disallow unselecting...which is good...but test!!!
        treeView.connect( "row-activated", self.onScriptDoubleClick, backgroundScriptsTreeView, indicatorTextEntry, copyOfScripts )
        treeView.set_tooltip_text( _(
            "Scripts are 'background' or 'non-background'.\n\n" + \
            "Background scripts are executed at intervals,\n" + \
            "the result optionally written to the label.\n\n" + \
            "Non-background scripts, listed in the menu,\n" + \
            "are executed when the user selects that script.\n\n" + \
            "If an attribute does not apply to a script,\n" + \
            "a dash is displayed.\n\n" + \
            "If a non-background script is checked as default,\n" + \
            "that script will appear as bold." ) )

        treeViewColumn = Gtk.TreeViewColumn( _( "Group" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_TAG_GROUP )
        treeView.append_column( treeViewColumn )

        rendererText = Gtk.CellRendererText()
        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), rendererText, text = IndicatorScriptRunner.COLUMN_TAG_NAME, weight_set = True )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionText )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_SOUND )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_NOTIFICATION )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Background" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_BACKGROUND )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Terminal" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_TERMINAL )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Interval" ) )

        rendererText = Gtk.CellRendererText()
        treeViewColumn.pack_start( rendererText, False )
        treeViewColumn.add_attribute( rendererText, "text", IndicatorScriptRunner.COLUMN_TAG_INTERVAL )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionCombined )

        rendererPixbuf = Gtk.CellRendererPixbuf()
        treeViewColumn.pack_start( rendererPixbuf, False )
        treeViewColumn.add_attribute( rendererPixbuf, "icon_name", IndicatorScriptRunner.COLUMN_TAG_REMOVE )
        treeViewColumn.set_cell_data_func( rendererPixbuf, self.dataFunctionCombined )

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

#TODO Need to capture the event when you CTRL click a script and that unselects the script...should then clear the command text view.
#
# Maybe one of the signals can be used?
# https://lazka.github.io/pgi-docs/Gtk-3.0/classes/TreeView.html#Gtk.TreeView.signals
#
#Maybe not now that BROWSE is used (see TODO above).
        commandTextView = Gtk.TextView()
        commandTextView.set_tooltip_text( _( "The terminal script/command, along with any arguments." ) )
        commandTextView.set_editable( False )
        commandTextView.set_wrap_mode( Gtk.WrapMode.WORD )

        treeView.connect( "cursor-changed", self.onScriptSelection, treeView, commandTextView, copyOfScripts )
        self.populateScriptsTreeStore( copyOfScripts, treeView )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( commandTextView )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )

        box.pack_start( scrolledWindow, True, True, 0 )
        grid.attach( box, 0, 20, 1, 10 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )
        box.set_homogeneous( True )

#TODO Test all of these when no scripts are present.
# Also is it possible to have no script selected (for edit/copy/remove)?
        addButton = Gtk.Button.new_with_label( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new script." ) )
        addButton.connect( "clicked", self.onScriptAdd, copyOfScripts, treeView, backgroundScriptsTreeView )
        box.pack_start( addButton, True, True, 0 )

        editButton = Gtk.Button.new_with_label( _( "Edit" ) )
        editButton.set_tooltip_text( _( "Edit the selected script." ) )
        editButton.connect( "clicked", self.onScriptEdit, copyOfScripts, treeView, backgroundScriptsTreeView, indicatorTextEntry )
        box.pack_start( editButton, True, True, 0 )

        copyButton = Gtk.Button.new_with_label( _( "Copy" ) )
        copyButton.set_tooltip_text( _( "Duplicate the selected script." ) )
        copyButton.connect( "clicked", self.onScriptCopy, copyOfScripts, treeView, backgroundScriptsTreeView )
        box.pack_start( copyButton, True, True, 0 )

        removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected script." ) )
        removeButton.connect( "clicked", self.onScriptRemove, copyOfScripts, treeView, backgroundScriptsTreeView, commandTextView, indicatorTextEntry )
        box.pack_start( removeButton, True, True, 0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 30, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Scripts" ) ) )

        # Menu settings.
        grid = self.createGrid()

        radioShowScriptsSubmenu = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show scripts in submenus" ) )
        radioShowScriptsSubmenu.set_tooltip_text( _(
            "Non-background scripts of the same group\n" + \
            "are shown in submenus." ) )
        radioShowScriptsSubmenu.set_active( self.showScriptsInSubmenus )
        grid.attach( radioShowScriptsSubmenu, 0, 0, 1, 1 )

        radioShowScriptsIndented = Gtk.RadioButton.new_with_label_from_widget( radioShowScriptsSubmenu, _( "Show scripts grouped" ) )
        radioShowScriptsIndented.set_tooltip_text( _(
            "Non-background scripts are shown\n" + \
            "within their respective group." ) )
        radioShowScriptsIndented.set_active( not self.showScriptsInSubmenus )
        grid.attach( radioShowScriptsIndented, 0, 1, 1, 1 )

        hideGroupsCheckbox = Gtk.CheckButton.new_with_label( _( "Hide groups" ) )
        hideGroupsCheckbox.set_active( self.hideGroups )
        hideGroupsCheckbox.set_sensitive( not self.showScriptsInSubmenus )
        hideGroupsCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        hideGroupsCheckbox.set_tooltip_text( _(
            "If checked, only script names are displayed.\n" + \
            "Otherwise, script names are indented within each group.\n\n" + \
            "Applies only to non-background scripts." ) )

        radioShowScriptsIndented.connect( "toggled", self.onRadio, hideGroupsCheckbox )

        grid.attach( hideGroupsCheckbox, 0, 2, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )

        # Icon text settings.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Icon Text" ) ), False, False, 0 )

        indicatorTextEntry.set_text( self.indicatorText )
        indicatorTextEntry.set_tooltip_text( _(
            "The text shown next to the indicator icon,\n" + \
            "or tooltip where applicable.\n\n" + \
            "A background script should either:\n" + \
            "\talways return non-empty text, or\n" + \
            "\treturn non-empty text on success\n" + \
            "\t(and empty text otherwise).\n\n" + \
            "A background script which shows free\n" + \
            "memory will always show a text result.\n\n" + \
            "A background script which checks for a log file\n" + \
            "will only show a text result when the log file\n" + \
            "exists, yet show empty text otherwise.\n\n" + \
            "Enclose a script tag(s) within { } to\n" + \
            "automatically add the separator." ) )

        box.pack_start( indicatorTextEntry, True, True, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Separator" ) ), False, False, 0 )

        indicatorTextSeparatorEntry = Gtk.Entry()
        indicatorTextSeparatorEntry.set_text( self.indicatorTextSeparator ) #TODO Need to capture during OK press.
        indicatorTextSeparatorEntry.set_tooltip_text( _( "The separator will be added between pairs of { }." ) )
        box.pack_start( indicatorTextSeparatorEntry, False, False, 0 )
        grid.attach( box, 0, 1, 1, 1 )

        backgroundScriptsTreeView.set_hexpand( True )
        backgroundScriptsTreeView.set_vexpand( True )
        backgroundScriptsTreeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        backgroundScriptsTreeView.connect( "row-activated", self.onBackgroundScriptDoubleClick, indicatorTextEntry, copyOfScripts )
        backgroundScriptsTreeView.set_tooltip_text( _(
            "Background scripts by group.\n" + \
            "Double click on a script to\n" + \
            "add to the icon text." ) )

        treeViewColumn = Gtk.TreeViewColumn( _( "Group" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_TAG_GROUP )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_TAG_NAME )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_SOUND )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_NOTIFICATION )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Interval" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_TAG_INTERVAL )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( backgroundScriptsTreeView )

        self.populateBackgroundScriptsTreeStore( copyOfScripts, backgroundScriptsTreeView )

        grid.attach( scrolledWindow, 0, 2, 1, 20 )

        notebook.append_page( grid, Gtk.Label.new( _( "Icon" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.scripts = copyOfScripts

            
#TODO Don't see how this works...surely need to iterate through list of scripts and find the script that is default?
            self.scriptGroupDefault = ""
            self.scriptNameDefault = ""
            if self.scripts: #TODO Check logic.
                self.scriptGroupDefault = self.defaultScriptGroupCurrent
                self.scriptNameDefault = self.defaultScriptNameCurrent

            self.showScriptsInSubmenus = radioShowScriptsSubmenu.get_active()
            self.hideGroups = hideGroupsCheckbox.get_active()

            self.indicatorText = indicatorTextEntry.get_text().strip()#TODO Check
            self.indicatorTextSeparator = indicatorTextSeparatorEntry.get_text().strip()#TODO Check

            self.initialiseBackgroundScripts()

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
    def dataFunctionText( self, treeViewColumn, cellRenderer, treeModel, treeIter, data ):
        cellRenderer.set_property( "weight", Pango.Weight.NORMAL )
        group = treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_TAG_GROUP_INTERNAL )
        name = treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_TAG_NAME )
        if group == self.scriptGroupDefault and name == self.scriptNameDefault:
            cellRenderer.set_property( "weight", Pango.Weight.BOLD )


    # Renderer for the Interval column.
    #    For a background script, the value will be a number (as text) for the interval in minutes.
    #    For a non-background script, the interval does not apply and so a dash icon is rendered.
    #
    # https://stackoverflow.com/questions/52798356/python-gtk-treeview-column-data-display
    # https://stackoverflow.com/questions/27745585/show-icon-or-color-in-gtk-treeview-tree
    # https://developer.gnome.org/pygtk/stable/class-gtkcellrenderertext.html
    # https://developer.gnome.org/pygtk/stable/pango-constants.html#pango-alignment-constants
    def dataFunctionCombined( self, treeViewColumn, cellRenderer, treeModel, treeIter, data ):
        cellRenderer.set_visible( True )
        if treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_TAG_BACKGROUND ) == Gtk.STOCK_APPLY: # This is a background script.
            if isinstance( cellRenderer, Gtk.CellRendererPixbuf ):
                cellRenderer.set_visible( False )

            else:
                cellRenderer.set_property( "xalign", 0.5 )

        else:
            if isinstance( cellRenderer, Gtk.CellRendererText ):
                cellRenderer.set_visible( False )


    def populateScriptsTreeStore( self, scripts, treeView ):
        treeStore = treeView.get_model()
        treeStore.clear()
        scriptsByGroup = self.getScriptsByGroup( scripts )
        groups = sorted( scriptsByGroup.keys(), key = str.lower )

        for group in groups:
            parent = treeStore.append( None, [ group, group, None, None, None, None, None, None, None ] )

            for script in scriptsByGroup[ group ]:
                playSound = Gtk.STOCK_APPLY if script.getPlaySound() else None
                showNotification = Gtk.STOCK_APPLY if script.getShowNotification() else None
                background = Gtk.STOCK_APPLY if script.getBackground() else None

                if script.getBackground():
                    terminalOpen = Gtk.STOCK_REMOVE
                    intervalInMinutes = str( script.getIntervalInMinutes() )
                    intervalInMinutesDash = None

                else:
                    terminalOpen = Gtk.STOCK_APPLY if script.getTerminalOpen() else None
                    intervalInMinutes = ""
                    intervalInMinutesDash = Gtk.STOCK_REMOVE

                treeStore.append(
                    parent,
                    [ group, None, script.getName(), playSound, showNotification, background, terminalOpen, intervalInMinutes, intervalInMinutesDash ] )

#TODO Might need to make the code below into a function to allow selecting a script that was just added or copied or edited.
#TODO When the copy script calls this, might be nice to pass in the name of the group/script to select it?
        treeView.expand_all()
        treePath = Gtk.TreePath.new_from_string( "0:0" ) #TODO Is this safe if no scripts are present?
        treeView.get_selection().select_path( treePath )
        treeView.set_cursor( treePath, None, False )
        treeView.scroll_to_cell( treePath ) #TODO Cannot have this when no scripts present.  


    def populateBackgroundScriptsTreeStore( self, scripts, treeView ):
        treeStore = treeView.get_model()
        treeStore.clear()
        scriptsByGroup = self.getScriptsByGroup( scripts, False, True )
        groups = sorted( scriptsByGroup.keys(), key = str.lower )

        # Unused columns are present, but allows the reuse of the column definitions.
        for group in groups:
            parent = treeStore.append( None, [ group, group, None, None, None, None, None, None ] )

            for script in scriptsByGroup[ group ]:
                treeStore.append( 
                    parent,
                    [ group, None, script.getName(), Gtk.STOCK_APPLY if script.getPlaySound() else None, Gtk.STOCK_APPLY if script.getShowNotification() else None, None, None, str( script.getIntervalInMinutes() ) ] )

#TODO Might need to make the code below into a function to allow selecting a script that was just added or copied or edited.
        treeView.expand_all()
#TODO The stuff below is likely not needed since this is only for display (and click) purposes.
        # treePath = Gtk.TreePath.new_from_string( "0:0" ) #TODO Is this safe if no scripts are present?
        # treeView.get_selection().select_path( treePath )
        # treeView.set_cursor( treePath, None, False )
        # treeView.scroll_to_cell( treePath ) #TODO Cannot have this when no scripts present.  


    # Update the indicator text after script edit/removal; on removal, the new group/name must be set to "".
    def updateIndicatorTextEntry( self, textEntry, oldGroup, oldName, newGroup, newName ):
        oldKey = self.__createKey( oldGroup, oldName )
        if newGroup and newName: # Script was edited, so do tag substitution...
            newKey = self.__createKey( newGroup, newName )
            textEntry.set_text( textEntry.get_text().replace( "{[" + oldKey + "]}", "{[" + newKey + "]}" ) )
            textEntry.set_text( textEntry.get_text().replace( "[" + oldKey + "]", "[" + newKey + "]" ) )

        else: # Script was removed, so do tag removal...
            textEntry.set_text( textEntry.get_text().replace( "{[" + oldKey + "]}", "" ) )
            textEntry.set_text( textEntry.get_text().replace( "[" + oldKey + "]", "" ) )


    def onScriptSelection( self, treeSelection, treeView, textView, scripts ):
        group, name = self.__getGroupNameFromTreeView( treeView )
        commandText = ""
        if group and name:
            commandText = self.getScript( scripts, group, name ).getCommand()

        textView.get_buffer().set_text( commandText )
#TODO Need to figure out how to trap when a row is unhighlighted?
# When a row is clicked or CTRL + clicked, a selection event is fired and the row selection count is one.
# So no idea how to discern between these two events. 
#May NOT need to do this if setting BROWSE works out (stops a user from unselecting).


    def onScriptDoubleClick( self, scriptsTreeView, treePath, treeViewColumn, backgroundScriptsTreeView, textEntry, scripts ):
        self.onScriptEdit( None, scripts, scriptsTreeView, backgroundScriptsTreeView, textEntry ) # Check to see if a group was double clicked downstream.  <---TODO What is this?  A TODO missing the TODO...?????


    def onBackgroundScriptDoubleClick( self, treeView, treePath, treeViewColumn, textEntry, scripts ):
        group, name = self.__getGroupNameFromTreeView( treeView )
        if group and name:
            textEntry.insert_text( "[" + self.__createKey( group, name ) + "]", textEntry.get_position() )


    def onScriptCopy( self, button, scripts, scriptsTreeView, backgroundScriptsTreeView ):
        group, name = self.__getGroupNameFromTreeView( scriptsTreeView )
        if group and name:
            script = self.getScript( scripts, group, name )

            grid = self.createGrid()

            box = Gtk.Box( spacing = 6 )

            box.pack_start( Gtk.Label.new( _( "Group" ) ), False, False, 0 )

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

                    newScript = Info( scriptGroupCombo.get_active_text().strip(),
                                      scriptNameEntry.get_text().strip(),
                                      script.getCommand(),
                                      script.getTerminalOpen(),
                                      script.getPlaySound(),
                                      script.getShowNotification(),
                                      script.getBackground(),
                                      script.getIntervalInMinutes() )

                    scripts.append( newScript )

                    self.populateScriptsTreeStore( scripts, scriptsTreeView )
                    self.populateBackgroundScriptsTreeStore( scripts, backgroundScriptsTreeView )

                break

            dialog.destroy()


    def onScriptRemove( self, button, scripts, scriptsTreeView, backgroundScriptsTreeView, commandTextView, textEntry ):
        group, name = self.__getGroupNameFromTreeView( scriptsTreeView )
        if group and name:
            if self.showOKCancel( scriptsTreeView, _( "Remove the selected script?" ) ) == Gtk.ResponseType.OK:
                i = 0
                for script in scripts:
                    if script.getGroup() == group and script.getName() == name:
                        del scripts[ i ]
                        self.populateScriptsTreeStore( scripts, scriptsTreeView )
                        self.populateBackgroundScriptsTreeStore( scripts, backgroundScriptsTreeView )
                        self.updateIndicatorTextEntry( textEntry, group, name, "", "" )                        
                        break

                    i += 1


    def onScriptAdd( self, button, scripts, scriptsTreeView, backgroundScriptsTreeView ):
        self.__addEditScript( Info( "", "", "", False, False, False, False, 1 ), scripts, scriptsTreeView, backgroundScriptsTreeView )


    def onScriptEdit( self, button, scripts, scriptsTreeView, backgroundScriptsTreeView, textEntry ):
        group, name = self.__getGroupNameFromTreeView( scriptsTreeView )
        if group and name:
            theScript = self.getScript( scripts, group, name )
            editedScript = self.__addEditScript( theScript, scripts, scriptsTreeView, backgroundScriptsTreeView )
            if editedScript:
                self.updateIndicatorTextEntry( textEntry, group, name, editedScript.getGroup(), editedScript.getName() )


    def __addEditScript( self, script, scripts, scriptsTreeView, backgroundScriptsTreeView ):
        add = True if script.getGroup() == "" else False

        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Group" ) ), False, False, 0 )

        scriptGroupCombo = Gtk.ComboBoxText.new_with_entry()
        scriptGroupCombo.set_tooltip_text( _(
            "The group to which the script belongs.\n\n" + \
            "Choose an existing group or enter a new one." ) )

        groups = sorted( self.getScriptsByGroup( scripts ).keys(), key = str.lower )
        for group in groups:
            scriptGroupCombo.append_text( group )

        if add:
            index = 0
            model, treeiter = scriptsTreeView.get_selection().get_selected()
            if treeiter:
                group = model[ treeiter ][ IndicatorScriptRunner.COLUMN_TAG_GROUP_INTERNAL ]
                index = groups.index( group )

        else:
            index = groups.index( script.getGroup() )

        scriptGroupCombo.set_active( index )

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

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label.new( _( "Command" ) )
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
        grid.attach( box, 0, 2, 1, 20 )

        soundCheckbox = Gtk.CheckButton.new_with_label( _( "Play sound" ) )
        soundCheckbox.set_tooltip_text( _(
            "For non-background scripts,\n" + \
            "play a beep on script completion.\n\n" + \
            "For background scripts, play a beep\n" + \
            "only if the script returns a result." ) )
        soundCheckbox.set_active( script.getPlaySound() )

        grid.attach( soundCheckbox, 0, 22, 1, 1 )

        notificationCheckbox = Gtk.CheckButton.new_with_label( _( "Show notification" ) )
        notificationCheckbox.set_tooltip_text( _(
            "For non-background scripts, show a\n" + \
            "notification on script completion.\n\n" + \
            "For background scripts, show a notification\n" + \
            "only if the script returns a result." ) )
        notificationCheckbox.set_active( script.getShowNotification() )

        grid.attach( notificationCheckbox, 0, 23, 1, 1 )

        backgroundCheckbox = Gtk.CheckButton.new_with_label( _( "Background script" ) )
        backgroundCheckbox.set_active( script.getBackground() )
        backgroundCheckbox.set_tooltip_text( _(
            "If checked, this script will run in background,\n" + \
            "at the interval specified, with the results\n" + \
            "optionally displayed in the icon label.\n\n" + \
            "Otherwise the script will appear in the menu." ) )

        grid.attach( backgroundCheckbox, 0, 24, 1, 1 )

        terminalCheckbox = Gtk.CheckButton.new_with_label( _( "Leave terminal open" ) )
        terminalCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        terminalCheckbox.set_tooltip_text( _(
            "Leave the terminal open on completion\n" + \
            "of non-background scripts." ) )
        terminalCheckbox.set_active( script.getTerminalOpen() )
        terminalCheckbox.set_sensitive( not script.getBackground() )

        grid.attach( terminalCheckbox, 0, 25, 1, 1 )

        defaultScriptCheckbox = Gtk.CheckButton.new_with_label( _( "Default script" ) )
        defaultScriptCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        defaultScriptCheckbox.set_active( script.getGroup() == self.defaultScriptGroupCurrent and script.getName() == self.defaultScriptNameCurrent )
        defaultScriptCheckbox.set_sensitive( not script.getBackground() )
        defaultScriptCheckbox.set_tooltip_text( _(
            "One non-background script can be set as\n" + \
            "the default script which is run on a\n" + \
            "middle mouse click of the indicator icon." ) )

        grid.attach( defaultScriptCheckbox, 0, 26, 1, 1 )

        backgroundCheckbox.connect( "toggled", self.onCheckboxInverse, terminalCheckbox, defaultScriptCheckbox )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_WIDGET_LEFT * 1.4 ) # Approximate alignment with the checkboxes above.

        label = Gtk.Label.new( _( "Interval (minutes)" ) )
        label.set_sensitive( script.getBackground() )
        box.pack_start( label, False, False, 0 )

        backgroundScriptIntervalSpinner = Gtk.SpinButton()
        backgroundScriptIntervalSpinner.set_adjustment( Gtk.Adjustment.new( script.getIntervalInMinutes(), 1, 10000, 1, 1, 0 ) )
        backgroundScriptIntervalSpinner.set_value( script.getIntervalInMinutes() )
        backgroundScriptIntervalSpinner.set_sensitive( script.getBackground() )
        backgroundScriptIntervalSpinner.set_tooltip_text( _( "Interval between runs of background scripts." ) )
        box.pack_start( backgroundScriptIntervalSpinner, False, False, 0 )

        grid.attach( box, 0, 27, 1, 1 )

        backgroundCheckbox.connect( "toggled", self.onCheckbox, label, backgroundScriptIntervalSpinner )

        dialog = self.createDialog( scriptsTreeView, _( "Add Script" ) if add else _( "Edit Script" ), grid )
        newScript = None
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

                if self.getTextViewText( commandTextView ).strip() == "":
                    self.showMessage( dialog, _( "The command cannot be empty." ) )
                    commandTextView.grab_focus()
                    continue

                if add: # Check for duplicate.
                    if self.getScript( scripts, scriptGroupCombo.get_active_text().strip(), scriptNameEntry.get_text().strip() ):
                        self.showMessage( dialog, _( "A script of the same group and name already exists." ) )
                        scriptGroupCombo.grab_focus()
                        continue

                else: # Edit existing script.
                    if scriptGroupCombo.get_active_text().strip() == script.getGroup() and scriptNameEntry.get_text().strip() == script.getName():
                        pass # Script group/name have not been modified, so this is a replace of an existing script.

                    else: # Check for a duplicate.
                        if self.getScript( scripts, scriptGroupCombo.get_active_text().strip(), scriptNameEntry.get_text().strip() ):
                            self.showMessage( dialog, _( "A script of the same group and name already exists." ) )
                            scriptGroupCombo.grab_focus()
                            continue

                    # Remove the existing script.
                    i = 0
                    for skript in scripts:
                        if script.getGroup() == skript.getGroup() and script.getName() == skript.getName():
                            break

                        i += 1

                    del scripts[ i ]

                # The new script or the edit.
                newScript = Info( scriptGroupCombo.get_active_text().strip(),
                                  scriptNameEntry.get_text().strip(),
                                  self.getTextViewText( commandTextView ).strip(),
                                  terminalCheckbox.get_active(),
                                  soundCheckbox.get_active(),
                                  notificationCheckbox.get_active(),
                                  backgroundCheckbox.get_active(),
                                  backgroundScriptIntervalSpinner.get_value() )

                scripts.append( newScript )

                if defaultScriptCheckbox.get_active() and not backgroundCheckbox.get_active(): #TODO Verify it's not possible to have a background script as default.
                    self.defaultScriptGroupCurrent = scriptGroupCombo.get_active_text().strip()
                    self.defaultScriptNameCurrent = scriptNameEntry.get_text().strip()

                else:
                    if self.defaultScriptGroupCurrent == scriptGroupCombo.get_active_text().strip() and self.defaultScriptNameCurrent == scriptNameEntry.get_text().strip():
                        self.defaultScriptGroupCurrent = ""
                        self.defaultScriptNameCurrent = ""

                self.populateScriptsTreeStore( scripts, scriptsTreeView )
                self.populateBackgroundScriptsTreeStore( scripts, backgroundScriptsTreeView )

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
            if ( nonBackground and not script.getBackground() ) or ( background and script.getBackground() ):
                if script.getGroup() not in scriptsByGroup:
                    scriptsByGroup[ script.getGroup() ] = [ ]

                scriptsByGroup[ script.getGroup() ].append( script )

        return scriptsByGroup


    def __getGroupNameFromTreeView( self, treeView ):
        group = None
        name = None
        model, treeiter = treeView.get_selection().get_selected()
        if treeiter:
            group = model[ treeiter ][ IndicatorScriptRunner.COLUMN_TAG_GROUP_INTERNAL ]
            name = model[ treeiter ][ IndicatorScriptRunner.COLUMN_TAG_NAME ]

        return group, name


    def __convertFromVersion13ToVersion14( self, scripts ):
        # In version 14 the 'directory' attribute was removed.
        # If a value for 'directory' is present, prepend to the 'command'.
        #
        # Map the old format scripts from JSON:
        #
        #    group, name, directory, command, terminalOpen, playSound, showNotification
        #
        # to the new format of script object:
        #
        #    group, name, directory + command, terminalOpen, playSound, showNotification
        convertedScripts = [ ]
        for script in scripts:
            convertedScript = [ ]
            convertedScript.append( script[ 0 ] )
            convertedScript.append( script[ 1 ] )

            if script[ 2 ] == "": # No directory specified, so only take the command.
                convertedScript.append( script[ 3 ] )

            else: # Combine the directory and command.
                convertedScript.append( "cd " + script[ 2 ] + "; " + script[ 3 ] )

            convertedScript.append( script[ 4 ] )
            convertedScript.append( script[ 5 ] )
            convertedScript.append( script[ 6 ] )
            convertedScripts.append( convertedScript )

        return convertedScripts


    def __convertFromVersion15ToVersion16( self, scripts ):
        # In version 16 background script were added.
        # All scripts prior to this change are deemed to be non-background scripts.
        # For each (non-background) script, set a flag and a dummy value for interval.
        convertedScripts = [ ]
        for script in scripts:
            convertedScript = [ ]
            convertedScript.append( script[ 0 ] )
            convertedScript.append( script[ 1 ] )
            convertedScript.append( script[ 2 ] )
            convertedScript.append( script[ 3 ] )
            convertedScript.append( script[ 4 ] )
            convertedScript.append( script[ 5 ] )
            convertedScript.append( False ) # Indicates this is a non-background script.
            convertedScript.append( -1 ) # For a non-background script, the interval is ignored.
            convertedScripts.append( convertedScript )

        # Add in sample background scripts and indicator text...ensuring there is no clash with existing groups! 
        group = "Background Script Examples"
        while True:
            clash = False
            for script in convertedScripts:
                if script[ 0 ] == group:
                    group += "..."
                    clash = True
                    break

            if not clash:
                break

        convertedScripts.append( [ group, "Internet Down", "if wget -qO /dev/null google.com > /dev/null; then echo \"\"; else echo \"Internet is DOWN\"; fi", False, True, True, True, 60 ] )
        convertedScripts.append( [ group, "Available Memory", "echo \"Free Memory: \"$(expr $( cat /proc/meminfo | grep MemAvailable | tr -d -c 0-9 ) / 1024)\" MB\"", False, False, False, True, 5 ] )
        self.indicatorText = " {[" + group + "::Internet Down]}{[" + group + "::Available Memory]}"

        return convertedScripts


    # Each time a background script is run, cache the result.
    #
    # If for example, one script has an interval of five minutes and another script is hourly,
    # the hourly script should not be run any more frequently so use a cached result when the quicker script is run.
    #
    # Initialise the cache results and set a next update time in the past to force all (background) scripts to update first time.
    def initialiseBackgroundScripts( self ):
        self.backgroundScriptResult = { }
        self.backgroundScriptNextUpdateTime = { }
        now = datetime.datetime.now()
        for script in self.scripts:
            if script.getBackground():
                self.backgroundScriptResult[ self.__createKey( script.getGroup(), script.getName() ) ] = None
                self.backgroundScriptNextUpdateTime[ self.__createKey( script.getGroup(), script.getName() ) ] = now


    def __createKey( self, group, name ): return group + "::" + name


    def loadConfig( self, config ):
        self.hideGroups = config.get( IndicatorScriptRunner.CONFIG_HIDE_GROUPS, False )
        self.indicatorText = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT, "" )
        self.indicatorTextSeparator = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR, " | " )
        self.scriptGroupDefault = config.get( IndicatorScriptRunner.CONFIG_SCRIPT_GROUP_DEFAULT, "" )
        self.scriptNameDefault = config.get( IndicatorScriptRunner.CONFIG_SCRIPT_NAME_DEFAULT, "" )
        self.showScriptsInSubmenus = config.get( IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS, False )

        self.scripts = [ ]
        if config:
            scripts = config.get( IndicatorScriptRunner.CONFIG_SCRIPTS, [ ] )

            if config.get( self.CONFIG_VERSION ) is None:
                if scripts and len( scripts[ 0 ] ) == 7:
                    scripts = self.__convertFromVersion13ToVersion14( scripts )
                    self.requestSaveConfig()

                if scripts and len( scripts[ 0 ] ) == 6:
                    scripts = self.__convertFromVersion15ToVersion16( scripts )
                    self.requestSaveConfig()

            defaultScriptFound = False
            for script in scripts:
                if script[ 0 ] == self.scriptGroupDefault and script[ 1 ] == self.scriptNameDefault and not script[ 6 ]:
                    defaultScriptFound = True

                self.scripts.append( Info( script[ 0 ], script[ 1 ], script[ 2 ], bool( script[ 3 ] ), bool( script[ 4 ] ), bool( script[ 5 ] ), bool( script[ 6 ] ), script[ 7 ] ) ) #TODO Is this last item an int?

            if not defaultScriptFound:
                self.scriptGroupDefault = ""
                self.scriptNameDefault = ""

        else:
            # Example non-background scripts.
            self.scripts.append( Info( "Network", "Ping Google", "ping -c 3 www.google.com", False, False, False, False, -1 ) )
            self.scripts.append( Info( "Network", "Public IP address", "notify-send -i " + self.icon + " \"Public IP address: $(wget https://ipinfo.io/ip -qO -)\"", False, False, False, False, -1 ) )
            self.scripts.append( Info( "Network", "Up or down", "if wget -qO /dev/null google.com > /dev/null; then notify-send -i " + self.icon + " \"Internet is UP\"; else notify-send \"Internet is DOWN\"; fi", False, False, False, False, -1 ) )
            self.scriptGroupDefault = self.scripts[ -1 ].getGroup()
            self.scriptNameDefault = self.scripts[ -1 ].getName()
            self.scripts.append( Info( "Update", "autoclean | autoremove | update | dist-upgrade", "sudo apt-get autoclean && sudo apt-get -y autoremove && sudo apt-get update && sudo apt-get -y dist-upgrade", True, True, True, False, -1 ) )

            # Example background scripts.
            self.scripts.append( Info( "Network", "Internet Down", "if wget -qO /dev/null google.com > /dev/null; then echo \"\"; else echo \"Internet is DOWN\"; fi", False, True, True, True, 60 ) )
            self.scripts.append( Info( "System", "Available Memory", "echo \"Free Memory: \"$(expr $( cat /proc/meminfo | grep MemAvailable | tr -d -c 0-9 ) / 1024)\" MB\"", False, False, False, True, 5 ) )
            self.indicatorText = " {[Network::Internet Down]}{[System::Available Memory]}"

            self.requestSaveConfig()

#TODO Testing Remove
#         self.scripts.append( Info( "Network", "Internet Down", "if wget -qO /dev/null google.com > /dev/null; then echo \"\"; else echo \"Internet is DOWN\"; fi", False, True, True, True, 60 ) )
        # self.scripts.append( Info( "System", "Available Memory", "echo \"Free Memory: \"$(expr $( cat /proc/meminfo | grep MemAvailable | tr -d -c 0-9 ) / 1024)\" MB\"", False, False, False, True, 5 ) )

        # self.scripts.append( Info( "Background", "StackExchange", "python3 /home/bernard/Programming/getStackExchange.py", False, False, False, True, 60 ) )
        # self.scripts.append( Info( "Background", "Bitcoin", "python3 /home/bernard/Programming/getBitcoin.py", False, False, False, True, 15 ) )
        # self.scripts.append( Info( "Background", "Log", "python3 /home/bernard/Programming/checkIndicatorLog.py", False, False, True, True, 60 ) )
        # self.scripts.append( Info( "Network", "Internet Running Monthly Quota", "python3 /home/bernard/Programming/getInternetRunningMonthlyQuota.py", False, False, False, False, -1 ) )

        # self.indicatorText = " {[Network::Internet Down]}{[System::Available Memory]}{[Background::StackExchange]}{[Background::Bitcoin]}{[Background::Log]}"
        # self.indicatorText = " {[Network::Internet Down]}{[System::Available Memory]}[System::Available Memory]{[Background::StackExchange]}{[Background::Bitcoin]}{[Background::Log]}{My log output: [Background::Log]}[Background::Log]"
        # self.scripts = []
        # self.scriptGroupDefault = ""
        # self.scriptNameDefault = ""
        print()#TODO debugging

        self.initialiseBackgroundScripts()


    def saveConfig( self ):
        scripts = [ ]
        for script in self.scripts:
            scripts.append( [ 
                script.getGroup(), 
                script.getName(), 
                script.getCommand(), 
                script.getTerminalOpen(), 
                script.getPlaySound(), 
                script.getShowNotification(),
                script.getBackground(),
                script.getIntervalInMinutes() ] )

        return {
            IndicatorScriptRunner.CONFIG_HIDE_GROUPS: self.hideGroups,
            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT: self.indicatorText,
            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR: self.indicatorTextSeparator,
            IndicatorScriptRunner.CONFIG_SCRIPT_GROUP_DEFAULT: self.scriptGroupDefault,
            IndicatorScriptRunner.CONFIG_SCRIPT_NAME_DEFAULT: self.scriptNameDefault,
            IndicatorScriptRunner.CONFIG_SCRIPTS: scripts,
            IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS: self.showScriptsInSubmenus
        }


IndicatorScriptRunner().main()