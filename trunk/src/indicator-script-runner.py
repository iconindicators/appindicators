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


#TODO Need a timer per background script, measured in minutes, which is the frequency of script execution.


INDICATOR_NAME = "indicator-script-runner"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )

from gi.repository import Gtk, Pango
from script import Info
from threading import Thread

import copy, indicatorbase, re


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
    COMMAND_NOTIFY_FOREGROUND = "notify-send -i " + INDICATOR_NAME + " \"" + COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" \"" + _( "...has completed." ) + "\""
    COMMAND_NOTIFY = "notify-send -i " + INDICATOR_NAME + " \"" + COMMAND_NOTIFY_TAG_SCRIPT_NAME + "\" \"" + _( "...has completed." ) + "\""
    COMMAND_SOUND = "paplay /usr/share/sounds/freedesktop/stereo/complete.oga"

#TODO Likely needed for background scripts.  Need better names?
    INDICATOR_TEXT_DEFAULT = "" #TODO Possible to have a sample background script and therefore a sample label?
    INDICATOR_TEXT_SEPARATOR_DEFAULT = " | "

    # Columns for the date model used by...
    #    the table to display all scripts;
    #    the table to display background scripts.
    COLUMN_TAG_GROUP_INTERNAL = 0 # Never shown; used when the script group is needed by decision logic yet not displayed.
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
            comments = _( "Run a terminal command or script from an indicator." ) )


    def update( self, menu ):
        print()#TODO debugging
        self.updateMenu( menu )
        self.updateLabel()

#TODO Need to figure out the update timing for each of the background scripts...
        # return int( 60 * self.refreshIntervalInMinutes )
#
# Would make life simple if there was one update time for all background scripts, set by the user (for example every five minutes or every hour).
# What happens if a user really wants to run one script every five minutes and another every hour (or less)?  Need a per script solution.
#
# During initialisation, for each background script
#    Set a last update update time in the past
#    Set the script output to be None
#
# During an update cycle...
#    If a background script's last update time is less than (or equal to) the current time,
#        run that script and save the output.
#    If a background script's last update time is greater than the current time,
#        retrieve the saved output.
#    
# At the end of each update cycle...
#    If a background script's update time is less than (or equal to) the current time,
#        get the interval and set the new update time to be the current time plus the interval.
#    If a background script's update time is greater than the current time,
#        do nothing.
#    Find the smallest update time in all background scripts and
#    set the next update to be from the the smallest update time less the current time.
#    NEED TO DO SOME SORT OF CHECK ENSURING THE SMALLEST UPDATE TIME IS IN FACT GREATER THAN THE CURRENT TIME.
#    MAYBE HAVE A SMALLEST HARD LIMIT OF ONE MINUTE?
# 
# When the Preferences are OK'd, do a normal update.
# WHAT HAPPENS IF THE PREFERENCES ARE KEPT OPEN WHILST AN UPDATE SHOULD HAVE OCCURRED
# BUT THE UPDATE WERE SUSPENDED?
# MAYBE KEEP THE NEXT UPDATE TIME AROUND IN THE PREFERENCES AND DO A CHECK?
# AT THE END OF THE UPDATE, KEEP THE NEXT UPDATE AMOUNT (AS A TIME) FOR THE PREFERENCES TO ACCESS?
# OR CAN THIS BE STORED WITHIN THE BASE CLASS?  Use self.nextUpdateTime


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
            command += "; " + IndicatorScriptRunner.COMMAND_NOTIFY.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME, script.getName() )

        if script.getPlaySound():
            command += "; " + IndicatorScriptRunner.COMMAND_SOUND

        if script.getTerminalOpen():
            command += "; ${SHELL}"

        command += "'"
        Thread( target = self.processCall, args = ( command, ) ).start()


#TODO Compare this function with that in Indicator Lunar.  
#Is it possible to pull this into Indicate Base, passing in the smarts for running scripts as an argument?
    def updateLabel( self ):
        label = self.indicatorText

        # Capture any whitespace at the start which the user intends for padding.
        whitespaceAtStart = ""
        match = re.search( "^\s*", label )
        if match:
            whitespaceAtStart = match.group( 0 )

        # Capture any whitespace at the end which the user intends for padding.
        whitespaceAtEnd = ""
        match = re.search( "\s*$", label )
        if match:
            whitespaceAtEnd = match.group( 0 )

        # Run each background script present in the label...
        for script in self.scripts:
            if script.getBackground():
#TODO Cannot simply run each background script...need to respect the timer for each script.
#So perhaps cache each script's result.
#When we come to this point, (somehow) determine which script we should be running (because its timer expired)
#and pull results from the other scripts from the cache.
                if "[" + script.getGroup() + "::" + script.getName() + "]" in label:
                    commandResult = self.processGet( script.getCommand() ).strip()
                    if script.getPlaySound() and commandResult:
                        self.processCall( IndicatorScriptRunner.COMMAND_SOUND )
        
                    if script.getShowNotification() and commandResult:
                        notificationCommand = IndicatorScriptRunner.COMMAND_NOTIFY_BACKGROUND
                        notificationCommand = notificationCommand.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_NAME, script.getName().replace( '-', '\\-' ) )
                        notificationCommand = notificationCommand.replace( IndicatorScriptRunner.COMMAND_NOTIFY_TAG_SCRIPT_RESULT, commandResult.replace( '-', '\\-' ) )
                        self.processCall( notificationCommand )
        
                    label = label.replace( "[" + script.getGroup() + "::" + script.getName() + "]", commandResult )

        # Handle any free text '{' and '}'.
        i = 0
        start = i
        result = ""
        lastSeparatorIndex = -1 # Need to track the last insertion point of the separator so it can be removed.
        tagRegularExpression = "\[[^\[^\]]*\]"
        while( i < len( label ) ):
            if label[ i ] == '{':
                j = i + 1
                while( j < len( label ) ):
                    if label[ j ] == '}':
                        freeText = label[ i + 1 : j ]
                        freeTextMinusUnknownTags = re.sub( tagRegularExpression, "", freeText )
                        if freeText == freeTextMinusUnknownTags and len( freeTextMinusUnknownTags ): # No unused tags were found.  Also handle when a script returns an empty string.
                            result += label[ start : i ] + freeText + self.indicatorTextSeparator
                            lastSeparatorIndex = len( result ) - len( self.indicatorTextSeparator )

                        else:
                            result += label[ start : i ]

                        i = j
                        start = i + 1
                        break

                    j += 1

            i += 1

        if lastSeparatorIndex > -1:
            result = result[ 0 : lastSeparatorIndex ] # Remove the last separator.

        result += label[ start : i ]

        # Remove remaining tags and any whitespace resulting from removed tags.
        result = re.sub( tagRegularExpression, "", result ).strip()

        # Replace start and end whitespace.
        result = whitespaceAtStart + result + whitespaceAtEnd

        self.indicator.set_label( result, "" )
        self.indicator.set_title( result ) # Needed for Lubuntu/Xubuntu.


#TODO When an add/edit/remove/copy occurs, update each of the treeviews and rejig the indicator text tags.
    def onPreferences( self, dialog ):
        self.defaultScriptGroupCurrent = self.scriptGroupDefault
        self.defaultScriptNameCurrent = self.scriptNameDefault
        copyOfScripts = copy.deepcopy( self.scripts )

        notebook = Gtk.Notebook()

        # Scripts.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        treeStore = Gtk.TreeStore( str, str, str, str, str, str, str, str, str )

        treeView = Gtk.TreeView.new_with_model( treeStore )
        treeView.set_hexpand( True )
        treeView.set_vexpand( True )
        treeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE ) #TODO Using BROWSE instead of SINGLE seems to disallow unselecting...which is good...but test!!!
        treeView.connect( "row-activated", self.onScriptDoubleClick, copyOfScripts )
        treeView.set_tooltip_text( _(
            "List of scripts within the same group.\n\n" + \
            "If a default script has been nominated,\n" + \
            "that script will be initially selected." ) )
#TODO The tooltip above needs rewriting.  Doesn't appear that we now select any script by default.

        treeViewColumn = Gtk.TreeViewColumn( _( "Group" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_TAG_GROUP )
        treeViewColumn.set_expand( False )
        treeView.append_column( treeViewColumn )

        rendererText = Gtk.CellRendererText()
        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), rendererText, text = IndicatorScriptRunner.COLUMN_TAG_NAME, weight_set = True )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionText )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_SOUND )
        treeViewColumn.set_expand( False )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_NOTIFICATION )
        treeViewColumn.set_expand( False )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Background" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_BACKGROUND )
        treeViewColumn.set_expand( False )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Terminal" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorScriptRunner.COLUMN_TAG_TERMINAL )
        treeViewColumn.set_expand( False )
        treeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Interval" ) )
        treeViewColumn.set_expand( False )

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

        self.populateScriptsTreeStore( copyOfScripts, treeStore, treeView )
        treeView.expand_all()

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

#TODO Need a comment as to why this is here.
        treeView.connect( "cursor-changed", self.onScriptSelection, commandTextView, copyOfScripts )

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
        addButton.connect( "clicked", self.onScriptAdd, copyOfScripts, treeView )
        box.pack_start( addButton, True, True, 0 )

        editButton = Gtk.Button.new_with_label( _( "Edit" ) )
        editButton.set_tooltip_text( _( "Edit the selected script." ) )
        editButton.connect( "clicked", self.onScriptEdit, copyOfScripts, treeView )
        box.pack_start( editButton, True, True, 0 )

        copyButton = Gtk.Button.new_with_label( _( "Copy" ) )
        copyButton.set_tooltip_text( _( "Duplicate the selected script." ) )
        copyButton.connect( "clicked", self.onScriptCopy, copyOfScripts, treeView )
        box.pack_start( copyButton, True, True, 0 )

        removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected script." ) )
        removeButton.connect( "clicked", self.onScriptRemove, copyOfScripts, treeView, commandTextView )
        box.pack_start( removeButton, True, True, 0 )

#TODO HOw to rename a group (if at all)?

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 30, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Scripts" ) ) )

        # Menu settings.
        grid = self.createGrid()

        radioShowScriptsSubmenu = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show scripts in submenus" ) )
        radioShowScriptsSubmenu.set_tooltip_text( _( "Scripts of the same group are shown in submenus." ) )
        radioShowScriptsSubmenu.set_active( self.showScriptsInSubmenus )
        grid.attach( radioShowScriptsSubmenu, 0, 0, 1, 1 )

        radioShowScriptsIndented = Gtk.RadioButton.new_with_label_from_widget( radioShowScriptsSubmenu, _( "Show scripts grouped" ) )
        radioShowScriptsIndented.set_tooltip_text( _( "Scripts are shown within their respective group." ) )
        radioShowScriptsIndented.set_active( not self.showScriptsInSubmenus )
        grid.attach( radioShowScriptsIndented, 0, 1, 1, 1 )

        hideGroupsCheckbox = Gtk.CheckButton.new_with_label( _( "Hide groups" ) )
        hideGroupsCheckbox.set_active( self.hideGroups )
        hideGroupsCheckbox.set_sensitive( not self.showScriptsInSubmenus )
        hideGroupsCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        hideGroupsCheckbox.set_tooltip_text( _(
            "If checked, only script names are displayed.\n\n" + \
            "Otherwise, script names are indented within each group." ) )

        radioShowScriptsIndented.connect( "toggled", self.onRadio, hideGroupsCheckbox )

        grid.attach( hideGroupsCheckbox, 0, 2, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )

        # Label settings.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Icon Text" ) ), False, False, 0 )

        indicatorText = Gtk.Entry()
#TODO Check this tooltip.
        indicatorText.set_tooltip_text( _(
            "The text shown next to the indicator icon,\n" + \
            "or tooltip where applicable.\n\n" + \
            "The icon text can contain text and tags\n" + \
            "from the table below.\n\n" + \
            "To associate text with one or more tags,\n" + \
            "enclose the text and tag(s) within { }.\n\n" + \
            "For example\n\n" + \
            "\t{The sun will rise at [SUN RISE DATE TIME]}\n\n" + \
            "If any tag contains no data at render time,\n" + \
            "the tag will be removed.\n\n" + \
            "If a removed tag is within { }, the tag and\n" + \
            "text will be removed." ) )
        box.pack_start( indicatorText, True, True, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Separator" ) ), False, False, 0 )

        indicatorTextSeparator = Gtk.Entry()
        indicatorTextSeparator.set_text( self.indicatorTextSeparator )
        indicatorTextSeparator.set_tooltip_text( _( "The separator will be added between pairs of { }." ) )
        box.pack_start( indicatorTextSeparator, False, False, 0 )
        grid.attach( box, 0, 1, 1, 1 )

        backgroundScriptsTreeStore = Gtk.TreeStore( str, str, str )

        backgroundScriptsTreeView = Gtk.TreeView.new_with_model( backgroundScriptsTreeStore )
        backgroundScriptsTreeView.set_hexpand( True )
        backgroundScriptsTreeView.set_vexpand( True )
        backgroundScriptsTreeView.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        backgroundScriptsTreeView.connect( "row-activated", self.onBackgroundScriptDoubleClick, indicatorText, copyOfScripts )
        backgroundScriptsTreeView.set_tooltip_text( _(
            "List of scripts within the same group.\n\n" + \
            "If a default script has been nominated,\n" + \
            "that script will be initially selected." ) )
#TODO Fix the tooltip above.  No default script is selected.

        treeViewColumn = Gtk.TreeViewColumn( _( "Group" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_TAG_GROUP )
        treeViewColumn.set_expand( False )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = IndicatorScriptRunner.COLUMN_TAG_NAME )
        treeViewColumn.set_expand( False )
        backgroundScriptsTreeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( backgroundScriptsTreeView )

        self.populateBackgroundScriptsTreeStore( copyOfScripts, backgroundScriptsTreeStore, backgroundScriptsTreeView )
        backgroundScriptsTreeView.expand_all()

        grid.attach( scrolledWindow, 0, 2, 1, 20 )

        notebook.append_page( grid, Gtk.Label.new( _( "Label" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.showScriptsInSubmenus = radioShowScriptsSubmenu.get_active()
            self.hideGroups = hideGroupsCheckbox.get_active()
            self.scripts = copyOfScripts
            if len( self.scripts ) == 0:
                self.scriptGroupDefault = ""
                self.scriptNameDefault = ""

            else:
                self.scriptGroupDefault = self.defaultScriptGroupCurrent
                self.scriptNameDefault = self.defaultScriptNameCurrent

        return responseType


    # Renders the script name bold when the (foreground) script is default.
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
        scriptGroup = treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_TAG_GROUP_INTERNAL )
        scriptName = treeModel.get_value( treeIter, IndicatorScriptRunner.COLUMN_TAG_NAME )
        if scriptGroup == self.scriptGroupDefault and scriptName == self.scriptNameDefault:
            cellRenderer.set_property( "weight", Pango.Weight.BOLD )


    # Renderer for the Interval column.
    #    For a background script, the value will be a number (as text) for the interval in minutes.
    #    For a foreground script, the interval does not apply and so a dash icon is rendered.
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
            if isinstance( cellRenderer, Gtk.CellRendererPixbuf ):
                pass

            else:
                cellRenderer.set_visible( False )


    def populateScriptsTreeStore( self, scripts, treeStore, treeView ):
        treeStore.clear()
        scriptsByGroup = self.getScriptsByGroup( scripts )
        scriptGroups = sorted( scriptsByGroup.keys(), key = str.lower )

        for scriptGroup in scriptGroups:
            parent = treeStore.append( None, [ scriptGroup, scriptGroup, None, None, None, None, None, None, None ] )

            for script in scriptsByGroup[ scriptGroup ]:
                playSound = Gtk.STOCK_APPLY if script.getPlaySound() else None
                showNotification = Gtk.STOCK_APPLY if script.getShowNotification() else None
                background = Gtk.STOCK_APPLY if script.getBackground() else None

                if script.getBackground():
                    terminalOpen = Gtk.STOCK_REMOVE
                    intervalInMinutes = script.getIntervalInMinutes()
                    intervalInMinutesDash = None

                else:
                    terminalOpen = Gtk.STOCK_APPLY if script.getTerminalOpen() else None
                    intervalInMinutes = None
                    intervalInMinutesDash = Gtk.STOCK_REMOVE

                treeStore.append( parent, [ scriptGroup, None, script.getName(), playSound, showNotification, background, terminalOpen, intervalInMinutes, intervalInMinutesDash ] )

# https://lazka.github.io/pgi-docs/Gtk-3.0/classes/TreePath.html#Gtk.TreePath.new_from_string
#TODO Figure out how to select the first script, not the first group...or is this not an issue?
        # treePath = Gtk.TreePath.new_from_string( "0:1" )
        # treeView.get_selection().select_path( treePath )
        # treeView.set_cursor( treePath, None, False )
        # treeView.scroll_to_cell( treePath )


    def populateBackgroundScriptsTreeStore( self, scripts, treeStore, treeView ):
        treeStore.clear()
        scriptsByGroup = self.getScriptsByGroup( scripts, False, True )
        scriptGroups = sorted( scriptsByGroup.keys(), key = str.lower )

        for scriptGroup in scriptGroups:
            parent = treeStore.append( None, [ scriptGroup, scriptGroup, None ] )

            for script in scriptsByGroup[ scriptGroup ]:
                treeStore.append( parent, [ scriptGroup, None, script.getName() ] )

# https://lazka.github.io/pgi-docs/Gtk-3.0/classes/TreePath.html#Gtk.TreePath.new_from_string
#TODO Figure out how to select the first script, not the first group...or is this not an issue?
        # treePath = Gtk.TreePath.new_from_string( "0" )
        # treeView.get_selection().select_path( treePath )
        # treeView.scroll_to_cell( treePath )


    def onScriptSelection( self, treeSelection, textView, scripts ):
        model, treeiter = treeSelection.get_selection().get_selected_rows()
        if treeiter:
            scriptGroup = model[ treeiter ][ IndicatorScriptRunner.COLUMN_TAG_GROUP_INTERNAL ]
            scriptName = model[ treeiter ][ IndicatorScriptRunner.COLUMN_TAG_NAME ]
            theScript = self.getScript( scripts, scriptGroup, scriptName )
            commandText = ""
            if theScript:
                commandText = theScript.getCommand()

            textView.get_buffer().set_text( commandText )

#TODO Figure out how to trap when a row is unhighlighted.
# When a row is clicked or CTRL + clicked, a selection event is fired and the row selection count is one.
# So no idea how to discern between these two events. 
#May NOT need to do this if setting BROWSE works out (stops a user from unselecting).
            # textView.get_buffer().set_text( "" )


    def onScriptDoubleClick( self, treeView, treePath, treeViewColumn, scripts ):
        group, name = self.__getGroupNameFromTreeView( treeView )
        if group and name:
            theScript = self.getScript( scripts, group, name )
            if theScript:
                self.onScriptEdit( None, scripts, treeView )


    def onBackgroundScriptDoubleClick( self, treeView, treePath, treeViewColumn, textEntry, scripts ):
        group, name = self.__getGroupNameFromTreeView( treeView )
        if group and name:
            theScript = self.getScript( scripts, scriptGroup, scriptName )
            if theScript:
                textEntry.insert_text( "[" + model[ treeiter ][ IndicatorScriptRunner.COLUMN_TAG_NAME ] + "]", textEntry.get_position() )


    def onScriptCopy( self, button, scripts, treeView ):
        group, name = self.__getGroupNameFromTreeView( treeView )
        if group and name:
            script = self.getScript( scripts, scriptGroup, scriptName )

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

            dialog = self.createDialog( scriptNameTreeView, _( "Copy Script" ), grid )
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

#TODO Need to either pass in the treeStores or get it from the treeViews and then how to select the copied script.
#                     self.populateScriptsTreeStore( scripts, treeStore, treeView )
#                     self.populateBackgroundScriptsTreeStore( scripts, treeStore, treeView ):

                break

            dialog.destroy()


    def onScriptRemove( self, button, scripts, treeView, commandTextView ):
        group, name = self.__getGroupNameFromTreeView( treeView )
        if group and name:
            if self.showOKCancel( scriptNameTreeView, _( "Remove the selected script?" ) ) == Gtk.ResponseType.OK:
                i = 0
                for script in scripts:
                    if script.getGroup() == scriptGroup and script.getName() == scriptName:
                        del scripts[ i ]

#TODO Need to either pass in the treeStores or get it from the treeViews and then how to select the group of the deleted script...unless the group is also gone.
# Maybe just select first or nothing?
#                         self.populateScriptsTreeStore( scripts, treeStore, treeView )
#                         self.populateBackgroundScriptsTreeStore( scripts, treeStore, treeView ):
                        break

                    i += 1


    def onScriptAdd( self, button, scripts, treeView ):
        self.__addEditScript( Info( "", "", "", False, False, False, False, 1 ), scripts, treeView )


    def onScriptEdit( self, button, scripts, treeView ):
        group, name = self.__getGroupNameFromTreeView( treeView )
        if group and name:
            theScript = self.getScript( scripts, group, name )
            self.__addEditScript( theScript, scripts, treeView )


    def __addEditScript( self, script, scripts, treeView ):
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
            model, treeiter = treeView.get_selection().get_selected()
            if treeiter:
                scriptGroup = model[ treeiter ][ IndicatorScriptRunner.COLUMN_TAG_GROUP_INTERNAL ]
                index = groups.index( scriptGroup )

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
        soundCheckbox.set_tooltip_text( _( "Play a beep on script completion." ) )
        soundCheckbox.set_active( script.getPlaySound() )

        grid.attach( soundCheckbox, 0, 22, 1, 1 )

        notificationCheckbox = Gtk.CheckButton.new_with_label( _( "Show notification" ) )
        notificationCheckbox.set_tooltip_text( _( "Show a notification on script completion." ) )
        notificationCheckbox.set_active( script.getShowNotification() )

        grid.attach( notificationCheckbox, 0, 23, 1, 1 )

        backgroundCheckbox = Gtk.CheckButton.new_with_label( _( "Background script" ) )
        backgroundCheckbox.set_tooltip_text( _(
            "If checked, this script will run in background,\n" + \
            "the results optionally displayed in the icon text.\n\n" + \
            "Otherwise the script will appear in the menu." ) )

        grid.attach( backgroundCheckbox, 0, 24, 1, 1 )

        terminalCheckbox = Gtk.CheckButton.new_with_label( _( "Leave terminal open" ) )
        terminalCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        terminalCheckbox.set_tooltip_text( _( "Leave the terminal open after the script completes." ) )
        terminalCheckbox.set_active( script.getTerminalOpen() )

        grid.attach( terminalCheckbox, 0, 25, 1, 1 )

        defaultScriptCheckbox = Gtk.CheckButton.new_with_label( _( "Default script" ) )
        defaultScriptCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        defaultScriptCheckbox.set_active( script.getGroup() == self.defaultScriptGroupCurrent and script.getName() == self.defaultScriptNameCurrent )
        defaultScriptCheckbox.set_tooltip_text( _(
            "If checked, this script will be run on a\n" + \
            "middle mouse click of the indicator icon.\n\n" + \
            "Only one script can be the default." ) )

        grid.attach( defaultScriptCheckbox, 0, 26, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_WIDGET_LEFT * 1.4 ) # Want to align the box with the previous checkboxes.

        box.pack_start( Gtk.Label.new( _( "Interval (minutes)" ) ), False, False, 0 )

        backgroundScriptIntervalSpinner = Gtk.SpinButton()
        backgroundScriptIntervalSpinner.set_adjustment( Gtk.Adjustment.new( script.getIntervalInMinutes(), 1, 10000, 1, 1, 0 ) )
        backgroundScriptIntervalSpinner.set_value( script.getIntervalInMinutes() )
        backgroundScriptIntervalSpinner.set_tooltip_text( _(
            "The number of most recent\n" + \
            "results to show in the menu.\n\n" + \
            "Selecting a menu item which\n" + \
            "contains a result will copy\n" + \
            "the result to the output." ) ) #TODO Fix
        box.pack_start( backgroundScriptIntervalSpinner, False, False, 0 )

        grid.attach( box, 0, 27, 1, 1 )

        backgroundCheckbox.connect( "toggled", self.onCheckboxInverse, terminalCheckbox)
        backgroundCheckbox.connect( "toggled", self.onCheckboxInverse, defaultScriptCheckbox )
        backgroundCheckbox.connect( "toggled", self.onCheckbox, box )
        backgroundCheckbox.set_active( script.getBackground() )

        dialog = self.createDialog( treeView, _( "Add Script" ) if add else _( "Edit Script" ), grid )
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

                #TODO Select group and script name.
                # self.populateScriptGroupCombo( scripts, scriptGroupComboBox, scriptTreeView, newScript.getGroup(), newScript.getName() )

            break

        dialog.destroy()


    def getScript( self, scripts, scriptGroup, scriptName ):
        theScript = None
        for script in scripts:
            if script.getGroup() == scriptGroup and script.getName() == scriptName:
                theScript = script
                break

        return theScript


    def getScriptsByGroup( self, scripts, foreground = True, background = True ):
        scriptsByGroup = { }
        for script in scripts:
            if ( foreground and not script.getBackground() ) or ( background and script.getBackground() ):
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
        # In version 16 background script functionality was added.
        # All scripts prior to this change are deemed to be foreground scripts.
        # For each script, set a flag and a dummy value for interval.
        convertedScripts = [ ]
        for script in scripts:
            convertedScript = [ ]
            convertedScript.append( script[ 0 ] )
            convertedScript.append( script[ 1 ] )
            convertedScript.append( script[ 2 ] )
            convertedScript.append( script[ 3 ] )
            convertedScript.append( script[ 4 ] )
            convertedScript.append( script[ 5 ] )
            convertedScript.append( False ) # Indicates this is a foreground script.
            convertedScript.append( -1 ) # For a foreground script, the interval is ignored.
            convertedScripts.append( convertedScript )

        return convertedScripts


    def loadConfig( self, config ):
        self.hideGroups = config.get( IndicatorScriptRunner.CONFIG_HIDE_GROUPS, False )
        self.indicatorText = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT, IndicatorScriptRunner.INDICATOR_TEXT_DEFAULT ) #TODO Better name?
        self.indicatorTextSeparator = config.get( IndicatorScriptRunner.CONFIG_INDICATOR_TEXT_SEPARATOR, IndicatorScriptRunner.INDICATOR_TEXT_SEPARATOR_DEFAULT ) #TODO Need a better name?
        self.scriptGroupDefault = config.get( IndicatorScriptRunner.CONFIG_SCRIPT_GROUP_DEFAULT, "" )
        self.scriptNameDefault = config.get( IndicatorScriptRunner.CONFIG_SCRIPT_NAME_DEFAULT, "" )
        self.showScriptsInSubmenus = config.get( IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS, False )

        self.scripts = [ ]
        if config:
            scripts = config.get( IndicatorScriptRunner.CONFIG_SCRIPTS, [ ] )

            # Temporarily needed until the version number is saved into the config.
            if config.get( self.CONFIG_VERSION ) is None:
                if scripts and len( scripts[ 0 ] ) == 7:
                    scripts = self.__convertFromVersion13ToVersion14( scripts )
                    self.requestSaveConfig()

                if scripts and len( scripts[ 0 ] ) == 6 and version is None:
                    scripts = self.__convertFromVersion15ToVersion16( scripts )
                    self.requestSaveConfig()

            defaultScriptFound = False
            for script in scripts:
                if script[ 0 ] == self.scriptGroupDefault and script[ 1 ] == self.scriptNameDefault and not script[ 6 ]:
                    defaultScriptFound = True

                self.scripts.append( Info( script[ 0 ], script[ 1 ], script[ 2 ], bool( script[ 3 ] ), bool( script[ 4 ] ), bool( script[ 5 ] ), bool( script[ 6 ] ), script[ 7 ] ) )

            if not defaultScriptFound:
                self.scriptGroupDefault = ""
                self.scriptNameDefault = ""

#TODO Testing
            self.scripts.append( Info( "Network", "Internet Down", "if wget -qO /dev/null google.com > /dev/null; then echo \"\"; else echo \"Internet is DOWN\"; fi", False, True, True, True, 60 ) )
            self.scripts.append( Info( "System", "Available Memory", "echo \"Free memory: $(expr \( `cat /proc/meminfo | grep MemAvailable | tr -d -c 0-9` / 1024 \))\" MB", False, False, False, True, 5 ) )

        else:
            self.scripts.append( Info( "Network", "Ping Google", "ping -c 3 www.google.com", False, False, False, False, -1 ) )
            self.scripts.append( Info( "Network", "Public IP address", "notify-send -i " + self.icon + " \"Public IP address: $(wget https://ipinfo.io/ip -qO -)\"", False, False, False, False, -1 ) )
            self.scripts.append( Info( "Network", "Up or down", "if wget -qO /dev/null google.com > /dev/null; then notify-send -i " + self.icon + " \"Internet is UP\"; else notify-send \"Internet is DOWN\"; fi", False, False, False, False, -1 ) )
            self.scriptGroupDefault = self.scripts[ -1 ].getGroup()
            self.scriptNameDefault = self.scripts[ -1 ].getName()
            self.scripts.append( Info( "Update", "autoclean | autoremove | update | dist-upgrade", "sudo apt-get autoclean && sudo apt-get -y autoremove && sudo apt-get update && sudo apt-get -y dist-upgrade", True, True, True, False, -1 ) )



#TODO Will need example of background scripts.
            self.scripts.append( Info( "Network", "Internet Down", "if wget -qO /dev/null google.com > /dev/null; then echo \"\"; else echo \"Internet is DOWN\"; fi", False, True, True, True, 60 ) )
            self.scripts.append( Info( "System", "Available Memory", "echo \"Free memory: $(expr \( `cat /proc/meminfo | grep MemAvailable | tr -d -c 0-9` / 1024 \))\" MB", False, False, False, True, 5 ) )


#TODO Do a request save (always)?
            self.requestSaveConfig()

#TODO Testing for background scripts...
        # self.scripts.append( Info( "Background", "StackExchange", "python3 /home/bernard/Programming/getStackExchange.py", False, False, False, True, 60 ) )
        # self.scripts.append( Info( "Background", "Bitcoin", "python3 /home/bernard/Programming/getBitcoin.py", False, False, False, True, 5 ) )
        # self.scripts.append( Info( "Background", "Log", "python3 /home/bernard/Programming/checkIndicatorLog.py", False, False, False, True, 60 ) )


#TODO Need to read this from config...and also save it out!
        # self.indicatorText = " {[Background::StackExchange]}{[Background::Bitcoin]}{[Background::Log]}"
        self.indicatorText = " {[Network::Up or down (background)]}{[System::Available Memory]}"


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
            IndicatorScriptRunner.CONFIG_SCRIPT_GROUP_DEFAULT: self.scriptGroupDefault,
            IndicatorScriptRunner.CONFIG_SCRIPT_NAME_DEFAULT: self.scriptNameDefault,
            IndicatorScriptRunner.CONFIG_SCRIPTS: scripts,
            IndicatorScriptRunner.CONFIG_SHOW_SCRIPTS_IN_SUBMENUS: self.showScriptsInSubmenus
        }


IndicatorScriptRunner().main()