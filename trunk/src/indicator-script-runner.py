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


# Application indicator to run a terminal command or script;
# optionally display results in the icon label.



#TODO Turn ON the sound for check log script.
#Place a log file in the home directory.
# Wait for a sound/notification.
# Remove the log file...sound and notification keeps happening!
#
# The cached result of the log file script is simply resused when the next update cycle happens
# (and it is not yet time to re-run the script to get a new value).
# So what to do...?


INDICATOR_NAME = "indicator-script-runner"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )

from gi.repository import Gtk, Pango
from script import Background, NonBackground
from threading import Thread

import copy, datetime, indicatorbase, math


class IndicatorScriptRunner( indicatorbase.IndicatorBase ):

    CONFIG_HIDE_GROUPS = "hideGroups"
    CONFIG_INDICATOR_TEXT = "indicatorText"
    CONFIG_INDICATOR_TEXT_SEPARATOR = "indicatorTextSeparator"
    CONFIG_SCRIPTS_BACKGROUND = "scriptsBackground"
    CONFIG_SCRIPTS_NON_BACKGROUND = "scriptsNonBackground"
    CONFIG_SHOW_SCRIPTS_IN_SUBMENUS = "showScriptsInSubmenus"

    COMMAND_NOTIFY_TAG_SCRIPT_NAME = "[SCRIPT_NAME]"
    COMMAND_NOTIFY_TAG_SCRIPT_RESULT = "[SCRIPT_RESULT]"
    COMMAND_NOTIFY_BACKGROUND = "notify-send -i " + INDICATOR_NAME + " \"" + COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" \"" + COMMAND_NOTIFY_TAG_SCRIPT_RESULT + "\""
    COMMAND_NOTIFY_NON_BACKGROUND = "notify-send -i " + INDICATOR_NAME + " \"" + COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" \"" + _( "...has completed." ) + "\""
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
    COLUMN_REMOVE = 8 # Icon name for the REMOVE icon; None otherwise.

    # Define common indices for the scripts saved in JSON.
    JSON_GROUP = 0
    JSON_NAME = 1
    JSON_COMMAND = 2
    JSON_PLAY_SOUND = 3
    JSON_SHOW_NOTIFICATION = 4

    # Define indices for background scripts saved in JSON.
    JSON_INTERVAL_IN_MINUTES = 5

    # Define indices for non-background scripts saved in JSON.
    JSON_TERMINAL_OPEN = 5
    JSON_DEFAULT = 6


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.16",
            copyrightStartYear = "2016",
            comments = _( "Run a terminal command or script;\noptionally display results in the icon label." ) )


    def update( self, menu ):
        now = datetime.datetime.now()
        self.updateMenu( menu )
        self.updateBackgroundScripts( now )

        # To use the base class process tags functionality, enclose each tag within { }.
        self.setLabel( self.processTags( self.indicatorText.replace( '[', "{[" ).replace( ']', "]}" ), self.indicatorTextSeparator, self.__processTags, now ) )

        # Calculate next update...
        nextUpdate = now + datetime.timedelta( hours = 100 ) # Set an update time well into the (immediate) future.
        for script in self.scripts:
            key = self.__createKey( script.getGroup(), script.getName() )
            if type( script ) == Background and self.backgroundScriptNextUpdateTime[ key ] < nextUpdate:
                nextUpdate = self.backgroundScriptNextUpdateTime[ key ]

        nextUpdateInSeconds = int( math.ceil( ( nextUpdate - now ).total_seconds() ) )
        return 60 if nextUpdateInSeconds < 60 else nextUpdateInSeconds


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
                    if type( script ) != Background:
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
            if script.getDefault():
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
            if type( script ) == Background:
                if self.backgroundScriptNextUpdateTime[ key ] < now:
#TODO Is it feasible to run the background scripts in threads?
# Where have I used threads before?  PPA indicator?
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
        now = arguments[ 0 ] # First and only parameter passed to processTags in base class.
        for script in self.scripts:
            key = self.__createKey( script.getGroup(), script.getName() )
            if type( script ) == Background and "[" + key + "]" in text:
                commandResult = self.backgroundScriptResult[ key ]
                text = text.replace( "[" + key + "]", commandResult )

        return text


#TODO Not sure where the issue is, but open preferences, select a script not already highlighted and switch to the icon tab.
# The indicator text on the icon tab is highlighted...why?
# https://stackoverflow.com/questions/68931638/remove-focus-from-textentry
# https://gitlab.gnome.org/GNOME/gtk/-/issues/1430  Can log a bug to this site if need be.
    def onPreferences( self, dialog ):
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
        treeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        treeView.connect( "row-activated", self.onScriptDoubleClick, backgroundScriptsTreeView, indicatorTextEntry, copyOfScripts )
        treeView.set_tooltip_text( _(
            "Scripts are 'background' or 'non-background'.\n\n" + \
            "Background scripts are executed at intervals,\n" + \
            "the result optionally written to the icon text.\n\n" + \
            "Non-background scripts, listed in the menu,\n" + \
            "are executed when the user selects that script.\n\n" + \
            "If an attribute does not apply to a script,\n" + \
            "a dash is displayed.\n\n" + \
            "If a non-background script is checked as default,\n" + \
            "that script will appear as bold." ) )

        treeViewColumn = Gtk.TreeViewColumn( _( "Group" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_GROUP )
        treeView.append_column( treeViewColumn )

        rendererText = Gtk.CellRendererText()
        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), rendererText, text = IndicatorScriptRunner.COLUMN_NAME, weight_set = True )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionText, copyOfScripts )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_SOUND )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_NOTIFICATION )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Background" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_BACKGROUND )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Terminal" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TERMINAL )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Interval" ) )

        rendererText = Gtk.CellRendererText()
        treeViewColumn.pack_start( rendererText, False )
        treeViewColumn.add_attribute( rendererText, "text", IndicatorScriptRunner.COLUMN_INTERVAL )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionCombined )

        rendererPixbuf = Gtk.CellRendererPixbuf()
        treeViewColumn.pack_start( rendererPixbuf, False )
        treeViewColumn.add_attribute( rendererPixbuf, "icon_name", IndicatorScriptRunner.COLUMN_REMOVE )
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

        radioShowScriptsSubmenu = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show scripts in sub-menus" ) )
        radioShowScriptsSubmenu.set_tooltip_text( _(
            "Non-background scripts of the same\n" + \
            "group are shown in sub-menus." ) )
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
        # indicatorTextEntry.set_receives_default( False )#TODO Testing
        indicatorTextEntry.set_tooltip_text( _(
            "The text shown next to the indicator icon,\n" + \
            "or tooltip where applicable.\n\n" + \
            "A background script must return either:\n" + \
            "\tNon-empty text; or\n" + \
            "\tNon-empty text on success and\n" + \
            "\tempty text otherwise.\n\n" + \
            "A background script which computes free\n" + \
            "memory will always show non-empty text.\n\n" + \
            "A background script which checks for a file\n" + \
            "will show non-empty text if the file exists,\n" + \
            "and show empty text otherwise." ) )

        box.pack_start( indicatorTextEntry, True, True, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Separator" ) ), False, False, 0 )

        indicatorTextSeparatorEntry = Gtk.Entry()
        indicatorTextSeparatorEntry.set_text( self.indicatorTextSeparator )
        indicatorTextSeparatorEntry.set_tooltip_text( _( "The separator will be added between tags." ) )
        box.pack_start( indicatorTextSeparatorEntry, False, False, 0 )
        grid.attach( box, 0, 1, 1, 1 )

        # backgroundScriptsTreeView.set_receives_default( True ) #TODO Testing
        # backgroundScriptsTreeView.set_property( "can-focus", True )#TODO Testing
        backgroundScriptsTreeView.set_hexpand( True )
        backgroundScriptsTreeView.set_vexpand( True )
        backgroundScriptsTreeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        backgroundScriptsTreeView.connect( "row-activated", self.onBackgroundScriptDoubleClick, indicatorTextEntry, copyOfScripts )
        backgroundScriptsTreeView.set_tooltip_text( _(
            "Background scripts by group.\n" + \
            "Double click on a script to\n" + \
            "add to the icon text." ) )

        treeViewColumn = Gtk.TreeViewColumn( _( "Group" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_GROUP )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_NAME )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_SOUND )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_NOTIFICATION )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Interval" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_INTERVAL )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( backgroundScriptsTreeView )

        self.populateBackgroundScriptsTreeStore( copyOfScripts, backgroundScriptsTreeView, "", "" )

        grid.attach( scrolledWindow, 0, 2, 1, 20 )

        tabName = _( "Icon" ) #TODO Not sure if this stays
        notebook.append_page( grid, Gtk.Label.new( tabName ) )

        notebook.connect( "switch-page", self.onSwitchPage, tabName, backgroundScriptsTreeView, indicatorTextEntry )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        # grid.set_focus_child( backgroundScriptsTreeView )#TODO Testing
        # backgroundScriptsTreeView.grab_focus()#TODO Testing

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.scripts = copyOfScripts
            self.showScriptsInSubmenus = radioShowScriptsSubmenu.get_active()
            self.hideGroups = hideGroupsCheckbox.get_active()
            self.indicatorText = indicatorTextEntry.get_text()
            self.indicatorTextSeparator = indicatorTextSeparatorEntry.get_text()
            self.initialiseBackgroundScripts()

        return responseType


#TODO NOt sure if this stays.
    def onSwitchPage( self, notebook, page, pageNumber, tabName, treeView, textEntry ):
        # if notebook.get_tab_label_text( page ) == tabName:
        # treeView.get_parent().grab_focus()
        # treeView.grab_focus()
        # treeView.get_parent().get_parent().set_focus_child( treeView.get_parent() )

        # textEntry.grab_focus_without_selecting()
        #     print( "focus")
        # print( textEntry.has_focus())
        # textEntry.grab_focus_without_selecting()
        
        # if pageNumber == notebook.get_n_pages() - 1:
        #     print( "Last ")
        #
        # print(  treeView.get_parent().get_parent() )
        # print( pageNumber )

        # print( textEntry.get_text())
        # textEntry.select_region( 5, 10  )
        # textEntry.set_position( -1 )
        # print( textEntry.get_overwrite_mode())
        # textEntry.grab_focus_without_selecting()
        # treeView.grab_focus()
        pass


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
    def dataFunctionText( self, treeViewColumn, cellRenderer, treeModel, treeIter, scripts ):
        cellRenderer.set_property( "weight", Pango.Weight.NORMAL )
        group = treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_GROUP_INTERNAL )
        name = treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_NAME )
        script = self.getScript( scripts, group, name )
        if type( script ) == NonBackground and script.getDefault():
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
            parent = treeStore.append( None, [ group, group, None, None, None, None, None, None, None ] )
            for script in sorted( scriptsByGroup[ group ], key = lambda script: script.getName().lower() ):
                playSound = Gtk.STOCK_APPLY if script.getPlaySound() else None
                showNotification = Gtk.STOCK_APPLY if script.getShowNotification() else None
                background = Gtk.STOCK_APPLY if type( script ) == Background else None

                if type( script ) == Background:
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

        if scripts:
            self.expandTreeAndSelect( treeView, selectGroup, selectScript, scriptsByGroup, groups )


    def populateBackgroundScriptsTreeStore( self, scripts, treeView, selectGroup, selectScript ):
        treeStore = treeView.get_model()
        treeStore.clear()
        scriptsByGroup = self.getScriptsByGroup( scripts, False, True )
        groups = sorted( scriptsByGroup.keys(), key = str.lower )
        for group in groups:
            parent = treeStore.append( None, [ group, group, None, None, None, None, None, None ] ) # Unused columns are present, but allows the reuse of the column definitions.

            for script in sorted( scriptsByGroup[ group ], key = lambda script: script.getName().lower() ):
                row = [
                        group,
                        None, 
                        script.getName(), 
                        Gtk.STOCK_APPLY if script.getPlaySound() else None, 
                        Gtk.STOCK_APPLY if script.getShowNotification() else None, 
                        None, 
                        None, 
                        str( script.getIntervalInMinutes() ) ]

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


    # Update the indicator text after script edit/removal; on removal, the new group/name must be set to "".
#TODO Test this; edit a scrpt and remove a script.
    def updateIndicatorTextEntry( self, textEntry, oldGroup, oldName, newGroup, newName ):
        oldKey = self.__createKey( oldGroup, oldName )
        if newGroup and newName: # Script was edited; do tag substitution...
            newKey = self.__createKey( newGroup, newName )
            textEntry.set_text( textEntry.get_text().replace( "[" + oldKey + "]", "[" + newKey + "]" ) )

        else: # Script was removed; do tag removal...
            textEntry.set_text( textEntry.get_text().replace( "[" + oldKey + "]", "" ) )


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

                    if type( script ) == Background:
                        newScript = Background(
                            scriptGroupCombo.get_active_text().strip(),
                            scriptNameEntry.get_text().strip(),
                            script.getCommand(),
                            script.getPlaySound(),
                            script.getShowNotification(),
                            script.getIntervalInMinutes() )

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
                        newScript.getGroup() if type( newScript ) == Background else "", 
                        newScript.getName() if type( newScript ) == Background else "" )

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
                        self.populateScriptsTreeStore( scripts, scriptsTreeView, "", "" )
                        self.populateBackgroundScriptsTreeStore( scripts, backgroundScriptsTreeView, "", "" )
                        self.updateIndicatorTextEntry( textEntry, group, name, "", "" )
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
                self.updateIndicatorTextEntry( textEntry, group, name, editedScript.getGroup(), editedScript.getName() )


    def __addEditScript( self, script, scripts, scriptsTreeView, backgroundScriptsTreeView ):
        add = True if script is None else False

        grid = self.createGrid()

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

        soundCheckbox = Gtk.CheckButton.new_with_label( _( "Play sound" ) )
        soundCheckbox.set_tooltip_text( _(
            "For non-background scripts,\n" + \
            "play a sound on script completion.\n\n" + \
            "For background scripts, play a sound\n" + \
            "if the script returns non-empty text." ) )
        soundCheckbox.set_active( False if add else script.getPlaySound() )

        grid.attach( soundCheckbox, 0, 12, 1, 1 )

        notificationCheckbox = Gtk.CheckButton.new_with_label( _( "Show notification" ) )
        notificationCheckbox.set_tooltip_text( _(
            "For non-background scripts, show a\n" + \
            "notification on script completion.\n\n" + \
            "For background scripts, show a notification\n" + \
            "if the script returns non-empty text." ) )
        notificationCheckbox.set_active( False if add else script.getShowNotification() )

        grid.attach( notificationCheckbox, 0, 13, 1, 1 )

#TODO Consider making this a radio button...
# Logically separates background from non-background attributes,
#which will help if the "exception" checkbox is also added (for background scripts).
        backgroundCheckbox = Gtk.CheckButton.new_with_label( _( "Background script" ) )
        backgroundCheckbox.set_active( False if add else type( script ) == Background )
        backgroundCheckbox.set_tooltip_text( _(
            "If checked, this script will run in background,\n" + \
            "at the interval specified, with the results\n" + \
            "optionally displayed in the icon label.\n\n" + \
            "Otherwise the script will appear in the menu." ) )

        grid.attach( backgroundCheckbox, 0, 14, 1, 1 )

        terminalCheckbox = Gtk.CheckButton.new_with_label( _( "Leave terminal open" ) )
        terminalCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        terminalCheckbox.set_tooltip_text( _(
            "Leave the terminal open on completion\n" + \
            "of non-background scripts." ) )
        terminalCheckbox.set_active( False if add else type( script ) == NonBackground and script.getTerminalOpen() )
        terminalCheckbox.set_sensitive( True if add else type( script ) == NonBackground )

        grid.attach( terminalCheckbox, 0, 15, 1, 1 )

        defaultScriptCheckbox = Gtk.CheckButton.new_with_label( _( "Default script" ) )
        defaultScriptCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        defaultScriptCheckbox.set_active( False if add else type( script ) == NonBackground and script.getDefault() )
        defaultScriptCheckbox.set_sensitive( True if add else type( script ) == NonBackground )
        defaultScriptCheckbox.set_tooltip_text( _(
            "One non-background script can be set as\n" + \
            "the default script which is run on a\n" + \
            "middle mouse click of the indicator icon." ) )

        grid.attach( defaultScriptCheckbox, 0, 16, 1, 1 )

        backgroundCheckbox.connect( "toggled", self.onCheckboxInverse, terminalCheckbox, defaultScriptCheckbox )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_WIDGET_LEFT * 1.4 ) # Approximate alignment with the checkboxes above.

        label = Gtk.Label.new( _( "Interval (minutes)" ) )
        label.set_sensitive( False if add else type( script ) == Background )
        box.pack_start( label, False, False, 0 )

        intervalSpinner = Gtk.SpinButton()
        intervalSpinner.set_adjustment( Gtk.Adjustment.new( script.getIntervalInMinutes() if type( script ) == Background else 60, 1, 10000, 1, 1, 0 ) )
        intervalSpinner.set_value( script.getIntervalInMinutes() if type( script ) == Background else 60 )
        intervalSpinner.set_sensitive( False if add else type( script ) == Background )
        intervalSpinner.set_tooltip_text( _( "Interval between runs of background scripts." ) )
        box.pack_start( intervalSpinner, False, False, 0 )

        grid.attach( box, 0, 17, 1, 1 )

        backgroundCheckbox.connect( "toggled", self.onCheckbox, label, intervalSpinner )

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

                # If this script is marked as default (and is non-background), check for an existing default script and if found, undefault it...
                if not backgroundCheckbox.get_active() and defaultScriptCheckbox.get_active():
                    i = 0
                    for skript in scripts:
                        if type( skript ) == NonBackground and skript.getDefault():
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
                if backgroundCheckbox.get_active():
                    newScript = Background(
                        groupCombo.get_active_text().strip(),
                        nameEntry.get_text().strip(),
                        self.getTextViewText( commandTextView ).strip(),
                        soundCheckbox.get_active(),
                        notificationCheckbox.get_active(),
                        intervalSpinner.get_value_as_int() )

                else:
                    newScript = NonBackground(
                        groupCombo.get_active_text().strip(),
                        nameEntry.get_text().strip(),
                        self.getTextViewText( commandTextView ).strip(),
                        soundCheckbox.get_active(),
                        notificationCheckbox.get_active(),
                        terminalCheckbox.get_active(),
                        defaultScriptCheckbox.get_active() )

                scripts.append( newScript )

                self.populateScriptsTreeStore( scripts, scriptsTreeView, newScript.getGroup(), newScript.getName() )
                self.populateBackgroundScriptsTreeStore(
                    scripts,
                    backgroundScriptsTreeView,
                    newScript.getGroup() if type( newScript ) == Background else "",
                    newScript.getName() if type( newScript ) == Background else "" )

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
            if ( nonBackground and type( script ) == NonBackground ) or ( background and type( script ) == Background ):
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
        self.backgroundScriptResult = { }
        self.backgroundScriptNextUpdateTime = { }
        now = datetime.datetime.now()
        for script in self.scripts:
            if type( script ) == Background:
                self.backgroundScriptResult[ self.__createKey( script.getGroup(), script.getName() ) ] = None
                self.backgroundScriptNextUpdateTime[ self.__createKey( script.getGroup(), script.getName() ) ] = now


    def __createKey( self, group, name ): return group + "::" + name


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
    def __convertFromVersion13ToVersion14( self, scripts ):
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


    # In version 16 background scripts were added.
    # All scripts prior to this change are deemed to be non-background scripts.
    def __convertFromVersion15ToVersion16( self, scripts, groupDefault, nameDefault ):
        nonBackgroundScripts = [ ]
        for script in scripts:
            nonBackgroundScript = [ ]
            nonBackgroundScript.append( script[ 0 ] )
            nonBackgroundScript.append( script[ 1 ] )
            nonBackgroundScript.append( script[ 2 ] )
            nonBackgroundScript.append( script[ 4 ] )
            nonBackgroundScript.append( script[ 5 ] )
            nonBackgroundScript.append( script[ 3 ] )
            nonBackgroundScript.append( script[ 0 ] == groupDefault and script[ 1 ] == nameDefault )

            nonBackgroundScripts.append( nonBackgroundScript )

        # Add in sample background scripts and indicator text,
        # ensuring there is no clash with existing groups! 
        group = "Background Script Examples"
        while True:
            clash = False
            for script in nonBackgroundScripts:
                if script[ 0 ] == group:
                    group += "..."
                    clash = True
                    break

            if not clash:
                break

        backgroundScripts = [ ]
        backgroundScripts.append( [ group, "Internet Down", "if wget -qO /dev/null google.com > /dev/null; then echo \"\"; else echo \"Internet is DOWN\"; fi", True, True, 60 ] )
        backgroundScripts.append( [ group, "Available Memory", "echo \"Free Memory: \"$(expr $( cat /proc/meminfo | grep MemAvailable | tr -d -c 0-9 ) / 1024)\" MB\"", False, False, 5 ] )

        self.indicatorText = " [" + group + "::Internet Down][" + group + "::Available Memory]"

        return nonBackgroundScripts, backgroundScripts


    def loadConfig( self, config ):
        self.hideGroups = config.get( IndicatorScriptRunner.CONFIG_HIDE_GROUPS, False )
        self.indicatorText = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT, "" )
        self.indicatorTextSeparator = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR, " | " )
        self.showScriptsInSubmenus = config.get( IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS, False )

        self.scripts = [ ]
        if config:
            if config.get( self.CONFIG_VERSION ) is None: # Need to do upgrade(s)...
                scripts = config.get( "scripts", [ ] )

                if scripts and len( scripts[ 0 ] ) == 7:
                    scripts = self.__convertFromVersion13ToVersion14( scripts )
                    self.requestSaveConfig()

                if scripts and len( scripts[ 0 ] ) == 6:
                    groupDefault = config.get( "scriptGroupDefault", "" )
                    nameDefault = config.get( "scriptNameDefault", "" )
                    scriptsNonBackground, scriptsBackground = self.__convertFromVersion15ToVersion16( scripts, groupDefault, nameDefault )
                    self.requestSaveConfig()

            else:
                scriptsNonBackground = config.get( self.CONFIG_SCRIPTS_NON_BACKGROUND, [ ] )
                scriptsBackground = config.get( self.CONFIG_SCRIPTS_BACKGROUND, [ ] )

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

            for script in scriptsBackground:
                skript = Background(
                    script[ IndicatorScriptRunner.JSON_GROUP ],
                    script[ IndicatorScriptRunner.JSON_NAME ],
                    script[ IndicatorScriptRunner.JSON_COMMAND ],
                    bool( script[ IndicatorScriptRunner.JSON_PLAY_SOUND ] ),
                    bool( script[ IndicatorScriptRunner.JSON_SHOW_NOTIFICATION ] ),
                    script[ IndicatorScriptRunner.JSON_INTERVAL_IN_MINUTES ] )

                self.scripts.append( skript )

        else:
            # Example non-background scripts.
            self.scripts.append( NonBackground( "Network", "Ping Google", "ping -c 3 www.google.com", False, False, False, False ) )
            self.scripts.append( NonBackground( "Network", "Public IP address", "notify-send -i " + self.icon + " \"Public IP address: $(wget https://ipinfo.io/ip -qO -)\"", False, False, False, False ) )
            self.scripts.append( NonBackground( "Network", "Up or down", "if wget -qO /dev/null google.com > /dev/null; then notify-send -i " + self.icon + " \"Internet is UP\"; else notify-send \"Internet is DOWN\"; fi", False, False, False, True ) )
            self.scripts.append( NonBackground( "Update", "autoclean | autoremove | update | dist-upgrade", "sudo apt-get autoclean && sudo apt-get -y autoremove && sudo apt-get update && sudo apt-get -y dist-upgrade", True, True, True, False ) )

            # Example background scripts.
            self.scripts.append( Background( "Network", "Internet Down", "if wget -qO /dev/null google.com > /dev/null; then echo \"\"; else echo \"Internet is DOWN\"; fi", False, True, 60 ) )
            self.scripts.append( Background( "System", "Available Memory", "echo \"Free Memory: \"$(expr $( cat /proc/meminfo | grep MemAvailable | tr -d -c 0-9 ) / 1024)\" MB\"", False, False, 5 ) )
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
                    script.getIntervalInMinutes() ] )

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
            IndicatorScriptRunner.CONFIG_HIDE_GROUPS: self.hideGroups,
            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT: self.indicatorText,
            IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR: self.indicatorTextSeparator,
            IndicatorScriptRunner.CONFIG_SCRIPTS_BACKGROUND: scriptsBackground,
            IndicatorScriptRunner.CONFIG_SCRIPTS_NON_BACKGROUND: scriptsNonBackground,
            IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS: self.showScriptsInSubmenus
        }


IndicatorScriptRunner().main()