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
    CONFIG_INDICATOR_TEXT = "indicatorText" #TODO Needed???
    CONFIG_INDICATOR_TEXT_SEPARATOR = "indicatorTextSeparator" #TODO Needed???
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


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.16",
            copyrightStartYear = "2016",
            comments = _( "Run a terminal command or script from an indicator." ) )


    def update( self, menu ):
        self.updateMenu( menu )
        self.updateLabel()


    def updateMenu( self, menu ):
        if self.showScriptsInSubmenus:
            scriptsGroupedByName = self.getScriptsByGroup( self.scripts, True )
            indent = self.indent( 0, 1 )
            for group in sorted( scriptsGroupedByName.keys(), key = str.lower ):
                menuItem = Gtk.MenuItem( group )
                menu.append( menuItem )
                subMenu = Gtk.Menu()
                menuItem.set_submenu( subMenu )
                self.addScriptsToMenu( scriptsGroupedByName[ group ], group, subMenu, indent )
        else:
            if self.hideGroups:
                for script in sorted( self.scripts, key = lambda script: script.getName().lower() ):
                    if not script.getBackground():
                        self.addScriptsToMenu( [ script ], script.getGroup(), menu, "" )

            else:
                scriptsGroupedByName = self.getScriptsByGroup( self.scripts, True )
                indent = self.indent( 1, 1 )
                for group in sorted( scriptsGroupedByName.keys(), key = str.lower ):
                    menu.append( Gtk.MenuItem( group + "..." ) )
                    self.addScriptsToMenu( scriptsGroupedByName[ group ], group, menu, indent )


#TODO If a background script is modified (group name or script name changes or script is removed)
# need to update the tags of scripts in the label to match the change.


    def updateLabel( self ):
        #TODO Need to acquire this from the Preferences
        self.indicatorText = " {[Background::StackExchange]}{[Background::Bitcoin]}{[Background::Log]}"

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

#TODO If we keep sound/notification, need to add to preferences.


#TODO Will need some way to ensure that no background scripts have the same group/name combination.
# Maybe in the preferences when they hit okay and we check the label?
# Need a function to take the group name and script name and combine with :: to standardise?  Might be also used in the preferences?

        # Run each background script present in the label...
        for script in self.scripts:
            if script.getBackground():
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


    def addScriptsToMenu( self, scripts, group, menu, indent ):
        scripts.sort( key = lambda script: script.getName().lower() )
        for script in scripts:

#TODO Not sure to use this or not to display the current default script.
#Ask Oleg.
            # if script.getGroup() == self.scriptGroupDefault and script.getName() == self.scriptNameDefault:
            #     menuItem = Gtk.RadioMenuItem.new_with_label( [ ], indent + script.getName() )
            #     menuItem.set_active( True )
            #
            # else:
            #     menuItem = Gtk.MenuItem.new_with_label( indent + script.getName() )

            menuItem = Gtk.MenuItem.new_with_label( indent + script.getName() )
            menuItem.connect( "activate", self.onScript, script )
            menu.append( menuItem )
            if group == self.scriptGroupDefault and script.getName() == self.scriptNameDefault:
                self.secondaryActivateTarget = menuItem


    def onScript( self, menuItem, script ):
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


    def onPreferences( self, dialog ):
        self.defaultScriptGroupCurrent = self.scriptGroupDefault
        self.defaultScriptNameCurrent = self.scriptNameDefault

        copyOfScripts = copy.deepcopy( self.scripts )
        notebook = Gtk.Notebook()




        # Scripts.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Group" ) ), False, False, 0 )

        scriptGroupComboBox = Gtk.ComboBoxText()
        scriptGroupComboBox.set_entry_text_column( 0 )
        scriptGroupComboBox.set_tooltip_text( _(
            "The group to which a script belongs.\n\n" + \
            "If a default script is specified,\n" + \
            "the group to which the script belongs\n" + \
            "will be initially selected." ) )

#TODO The tooltip above and below...
#Can't find the code which checks to see which, if any, script is the default and then select it.
#If this is the case, remove that part of each tooltip.

        box.pack_start( scriptGroupComboBox, True, True, 0 )
        grid.attach( box, 0, 0, 1, 1 )

#TODO Might be a good idea to define these as constants...so other code does not refer to numbers but rather names.
        # Data model to hold... 
        #    Script group
        #    Script name
        #    tick icon for play sound
        #    tick icon for show notification
        #    tick for background script
        #    terminal open icon (tick icon or remove icon)
        #    interval amount (string)
        #    Remove icon (for when interval amount is not applicable)
        scriptNameListStore = Gtk.ListStore( str, str, str, str, str, str, str, str )
        scriptNameListStore.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        scriptNameTreeView = Gtk.TreeView.new_with_model( scriptNameListStore )
        scriptNameTreeView.set_hexpand( True )
        scriptNameTreeView.set_vexpand( True )
        scriptNameTreeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        scriptNameTreeView.connect( "row-activated", self.onScriptNameDoubleClick, scriptGroupComboBox, copyOfScripts )
        scriptNameTreeView.set_tooltip_text( _(
            "List of scripts within the same group.\n\n" + \
            "If a default script has been nominated,\n" + \
            "that script will be initially selected." ) )

        rendererText = Gtk.CellRendererText()
        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), rendererText, text = 1, weight_set = True )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionText )
        scriptNameTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Sound" ), Gtk.CellRendererPixbuf(), stock_id = 2 )
        treeViewColumn.set_expand( False )
        scriptNameTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Notification" ), Gtk.CellRendererPixbuf(), stock_id = 3 )
        treeViewColumn.set_expand( False )
        scriptNameTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Background" ), Gtk.CellRendererPixbuf(), stock_id = 4 )
        treeViewColumn.set_expand( False )
        scriptNameTreeView.append_column( treeViewColumn )



        treeViewColumn = Gtk.TreeViewColumn( _( "Terminal" ), Gtk.CellRendererPixbuf(), stock_id = 5 )
        treeViewColumn.set_expand( False )
        scriptNameTreeView.append_column( treeViewColumn )

        # treeViewColumn = Gtk.TreeViewColumn( _( "Interval" ), rendererText, text = 6, weight_set = True )
        # treeViewColumn.set_expand( False )
        # treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionText )
        # scriptNameTreeView.append_column( treeViewColumn )

        
        treeViewColumn = Gtk.TreeViewColumn( _( "Interval" ) )
        treeViewColumn.set_expand( False )

        rendererText = Gtk.CellRendererText()
        treeViewColumn.pack_start( rendererText, False )
        treeViewColumn.add_attribute( rendererText, "text", 6 )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunctionCombined )

        rendererPixbuf = Gtk.CellRendererPixbuf()
        treeViewColumn.pack_start( rendererPixbuf, False )
        treeViewColumn.add_attribute( rendererPixbuf, "icon_name", 7 )
        treeViewColumn.set_cell_data_func( rendererPixbuf, self.dataFunctionCombined )

        scriptNameTreeView.append_column( treeViewColumn )

#TODO Can we show the default script in some other way (highlight/bold the row) rather than have an extra column just for a tick?
# https://stackoverflow.com/questions/49836499/make-only-some-rows-bold-in-a-gtk-treeview
# https://python-gtk-3-tutorial.readthedocs.io/en/latest/cellrenderers.html

        # treeViewColumn = Gtk.TreeViewColumn( _( "Default" ), Gtk.CellRendererPixbuf(), stock_id = 4 )
        # treeViewColumn.set_expand( False )
        # scriptNameTreeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( scriptNameTreeView )
        scrolledWindow.set_margin_top( 10 )

        grid.attach( scrolledWindow, 0, 1, 1, 15 )

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label.new( _( "Command" ) )
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
        grid.attach( box, 0, 16, 1, 15 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )
        box.set_homogeneous( True )

        addButton = Gtk.Button.new_with_label( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new script." ) )
        addButton.connect( "clicked", self.onScriptAdd, copyOfScripts, scriptGroupComboBox, scriptNameTreeView )
        box.pack_start( addButton, True, True, 0 )

        editButton = Gtk.Button.new_with_label( _( "Edit" ) )
        editButton.set_tooltip_text( _( "Edit the selected script." ) )
        editButton.connect( "clicked", self.onScriptEdit, copyOfScripts, scriptGroupComboBox, scriptNameTreeView )
        box.pack_start( editButton, True, True, 0 )

        copyButton = Gtk.Button.new_with_label( _( "Copy" ) )
        copyButton.set_tooltip_text( _( "Duplicate the selected script." ) )
        copyButton.connect( "clicked", self.onScriptCopy, copyOfScripts, scriptGroupComboBox, scriptNameTreeView )
        box.pack_start( copyButton, True, True, 0 )

        removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected script." ) )
        removeButton.connect( "clicked", self.onScriptRemove, copyOfScripts, scriptGroupComboBox, scriptNameTreeView, commandTextView )
        box.pack_start( removeButton, True, True, 0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 32, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Scripts" ) ) )




        # Menu settings.
        grid = self.createGrid()

        label = Gtk.Label.new( _( "Display" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        radioShowScriptsSubmenu = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show scripts in submenus" ) )
        radioShowScriptsSubmenu.set_tooltip_text( _( "Scripts of the same group are shown in submenus." ) )
        radioShowScriptsSubmenu.set_active( self.showScriptsInSubmenus )
        radioShowScriptsSubmenu.set_margin_left( self.INDENT_WIDGET_LEFT )
        grid.attach( radioShowScriptsSubmenu, 0, 1, 1, 1 )

        radioShowScriptsIndented = Gtk.RadioButton.new_with_label_from_widget( radioShowScriptsSubmenu, _( "Show scripts grouped" ) )
        radioShowScriptsIndented.set_tooltip_text( _( "Scripts are shown within their respective group." ) )
        radioShowScriptsIndented.set_active( not self.showScriptsInSubmenus )
        radioShowScriptsIndented.set_margin_left( self.INDENT_WIDGET_LEFT )
        grid.attach( radioShowScriptsIndented, 0, 2, 1, 1 )

        hideGroupsCheckbox = Gtk.CheckButton.new_with_label( _( "Hide groups" ) )
        hideGroupsCheckbox.set_active( self.hideGroups )
        hideGroupsCheckbox.set_sensitive( not self.showScriptsInSubmenus )
        hideGroupsCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT * 2 )
        hideGroupsCheckbox.set_tooltip_text( _(
            "If checked, only script names are displayed.\n\n" + \
            "Otherwise, script names are indented within each group." ) )

        grid.attach( hideGroupsCheckbox, 0, 3, 1, 1 )

        radioShowScriptsSubmenu.connect( "toggled", self.onDisplayCheckboxes, radioShowScriptsSubmenu, hideGroupsCheckbox )
        radioShowScriptsIndented.connect( "toggled", self.onDisplayCheckboxes, radioShowScriptsSubmenu, hideGroupsCheckbox )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )



        # General settings.
        grid = self.createGrid()

        label = Gtk.Label.new( _( "Display" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        radioShowScriptsSubmenu = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show scripts in submenus" ) )
        radioShowScriptsSubmenu.set_tooltip_text( _( "Scripts of the same group are shown in submenus." ) )
        radioShowScriptsSubmenu.set_active( self.showScriptsInSubmenus )
        radioShowScriptsSubmenu.set_margin_left( self.INDENT_WIDGET_LEFT )
        grid.attach( radioShowScriptsSubmenu, 0, 1, 1, 1 )

        radioShowScriptsIndented = Gtk.RadioButton.new_with_label_from_widget( radioShowScriptsSubmenu, _( "Show scripts grouped" ) )
        radioShowScriptsIndented.set_tooltip_text( _( "Scripts are shown within their respective group." ) )
        radioShowScriptsIndented.set_active( not self.showScriptsInSubmenus )
        radioShowScriptsIndented.set_margin_left( self.INDENT_WIDGET_LEFT )
        grid.attach( radioShowScriptsIndented, 0, 2, 1, 1 )

        hideGroupsCheckbox = Gtk.CheckButton.new_with_label( _( "Hide groups" ) )
        hideGroupsCheckbox.set_active( self.hideGroups )
        hideGroupsCheckbox.set_sensitive( not self.showScriptsInSubmenus )
        hideGroupsCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT * 2 )
        hideGroupsCheckbox.set_tooltip_text( _(
            "If checked, only script names are displayed.\n\n" + \
            "Otherwise, script names are indented within each group." ) )

        grid.attach( hideGroupsCheckbox, 0, 3, 1, 1 )

        radioShowScriptsSubmenu.connect( "toggled", self.onDisplayCheckboxes, radioShowScriptsSubmenu, hideGroupsCheckbox )
        radioShowScriptsIndented.connect( "toggled", self.onDisplayCheckboxes, radioShowScriptsSubmenu, hideGroupsCheckbox )

        notebook.append_page( grid, Gtk.Label.new( _( "Label" ) ) )

        scriptGroupComboBox.connect( "changed", self.onScriptGroup, copyOfScripts, scriptNameListStore, scriptNameTreeView )
        scriptNameTreeView.get_selection().connect( "changed", self.onScriptName, scriptGroupComboBox, commandTextView, copyOfScripts )
        self.populateScriptGroupCombo( copyOfScripts, scriptGroupComboBox, scriptNameTreeView, None, None )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

#TODO Ensure the default script, if any, is NOT a background script.
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


    # Renders the script name and interval (for background scripts).
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
        cellRenderer.set_property( "xalign", 0.0 )
#TODO May not need this bit.        
        # if treeViewColumn.get_title() == _( "Interval" ):
        #     cellRenderer.set_property( "xalign", 0.5 )

        cellRenderer.set_property( "weight", Pango.Weight.NORMAL )
        scriptGroup = treeModel.get_value( treeIter, 0 )
        scriptName = treeModel.get_value( treeIter, 1 )
        if scriptGroup == self.scriptGroupDefault and scriptName == self.scriptNameDefault:
            cellRenderer.set_property( "weight", Pango.Weight.BOLD )


    # Renders either:
    #    The tick symbol for a foreground script to leave the terminal open,
    #    The interval (number as text) for a background script.
    #
    # Only want to render either the tick symbol OR the text, not both.
    # If the renderer for the item that is not to be displayed is still visible,
    # space is taken up throwing out alignments, so need to hide the unused renderer.
    #
    # https://stackoverflow.com/questions/52798356/python-gtk-treeview-column-data-display
    # https://stackoverflow.com/questions/27745585/show-icon-or-color-in-gtk-treeview-tree
    # https://developer.gnome.org/pygtk/stable/class-gtkcellrenderertext.html
    # https://developer.gnome.org/pygtk/stable/pango-constants.html#pango-alignment-constants
    def dataFunctionCombined( self, treeViewColumn, cellRenderer, treeModel, treeIter, data ):
        cellRenderer.set_visible( True )

        # background = False if treeModel.get_value( treeIter, 4 ) is None else True
        # if background:
        if treeModel.get_value( treeIter, 4 ) == Gtk.STOCK_APPLY:
            if isinstance( cellRenderer, Gtk.CellRendererPixbuf ):
                cellRenderer.set_visible( False )

            else:
                cellRenderer.set_property( "xalign", 0.5 )
                #TODO Probably want the bold/normal stuff here too?  Probably not; a background script cannot be a default script.

        else:
            if isinstance( cellRenderer, Gtk.CellRendererPixbuf ):
                pass

            else:
                cellRenderer.set_visible( False )
        
        
        # background = False if treeModel.get_value( treeIter, 4 ) is None else True
        # if background:
        #     if isinstance( cellRenderer, Gtk.CellRendererPixbuf ):
        #         cellRenderer.set_visible( False )
        #
        #     else:
        #         cellRenderer.set_property( "xalign", 0.5 )
        #         #TODO Probably want the bold/normal stuff here too?  Probably not; a background script cannot be a default script.
        #
        # else:
        #     if isinstance( cellRenderer, Gtk.CellRendererPixbuf ):
        #         pass
        #
        #     else:
        #         cellRenderer.set_visible( False )





#         if isinstance( cellRenderer, Gtk.CellRendererPixbuf ):
#             if background == Gtk.STOCK_APPLY:
#                 cellRenderer.set_visible( False )
#
# #TODO Needed?
#             # else:
#             #     cellRenderer.set_property( "xalign", 0.5 )
#
#         if isinstance( cellRenderer, Gtk.CellRendererText ):
#             cellRenderer.set_property( "weight", Pango.Weight.NORMAL )
#             if background == Gtk.STOCK_APPLY:
#                 cellRenderer.set_property( "xalign", 0.5 )
#
#             else:
#                 cellRenderer.set_visible( False )


    def onDisplayCheckboxes( self, radiobutton, radioShowScriptsSubmenu, hideGroupsCheckbox ):
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
            script = self.getScript( scripts, scriptGroup, scriptName )

            playSound = None
            if script.getPlaySound():
                playSound = Gtk.STOCK_APPLY

            showNotification = None
            if script.getShowNotification():
                showNotification = Gtk.STOCK_APPLY

            background = None
            if script.getBackground():
                background = Gtk.STOCK_APPLY

            # terminalOpen = None
            # if script.getBackground():
            #     terminalOpen = Gtk.STOCK_REMOVE
            #
            # else:
            #     if script.getTerminalOpen():
            #         terminalOpen = Gtk.STOCK_APPLY
            terminalOpen = None
            if script.getTerminalOpen() and not script.getBackground():
                terminalOpen = Gtk.STOCK_APPLY
            if script.getBackground():
                terminalOpen = Gtk.STOCK_REMOVE

            intervalInMinutes = None
            if script.getBackground():
                intervalInMinutes = script.getIntervalInMinutes()

            intervalInMinutesExtra = None
            if not script.getBackground():
                intervalInMinutesExtra = Gtk.STOCK_REMOVE

            # else:
            #     intervalInMinutes = Gtk.STOCK_REMOVE
            # if script.getBackground():
            #     intervalInMinutes = script.getIntervalInMinutes()


# https://thebigdoc.readthedocs.io/en/latest/PyGObject-Tutorial/stock.html#Gtk.STOCK_REMOVE
            scriptNameListStore.append( [ scriptGroup, scriptName, playSound, showNotification, background, terminalOpen, intervalInMinutes, intervalInMinutesExtra ] )


            # iter_child = scriptNameListStore.get_iter_first()
            # while iter_child:
            #     print( 
            #         scriptNameListStore.get_value( iter_child, 0 ),
            #         scriptNameListStore.get_value( iter_child, 1 ),
            #         scriptNameListStore.get_value( iter_child, 2 ),
            #         scriptNameListStore.get_value( iter_child, 3 ),
            #         scriptNameListStore.get_value( iter_child, 4 ),
            #         scriptNameListStore.get_value( iter_child, 5 ),
            #         scriptNameListStore.get_value( iter_child, 6 ) )
            #
            #     iter_child = scriptNameListStore.iter_next(iter_child)

        scriptNameTreeView.get_selection().select_path( 0 )
        scriptNameTreeView.scroll_to_cell( Gtk.TreePath.new_from_string( "0" ) )


    def onScriptName( self, scriptNameTreeSelection, scriptGroupComboBox, commandTextView, scripts ):
        scriptGroup = scriptGroupComboBox.get_active_text()
        model, treeiter = scriptNameTreeSelection.get_selected()
        if treeiter:
            scriptName = model[ treeiter ][ 1 ]
            theScript = self.getScript( scripts, scriptGroup, scriptName )
            if theScript:
                commandTextView.get_buffer().set_text( theScript.getCommand() )


    def onScriptCopy( self, button, scripts, scriptGroupComboBox, scriptNameTreeView ):
        scriptGroup = scriptGroupComboBox.get_active_text()
        model, treeiter = scriptNameTreeView.get_selection().get_selected()
        if scriptGroup and treeiter:
            scriptName = model[ treeiter ][ 1 ]
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
                    self.populateScriptGroupCombo( scripts, scriptGroupComboBox, scriptNameTreeView, newScript.getGroup(), newScript.getName() )

                break

            dialog.destroy()


    def onScriptRemove( self, button, scripts, scriptGroupComboBox, scriptNameTreeView, commandTextView ):
        scriptGroup = scriptGroupComboBox.get_active_text()
        model, treeiter = scriptNameTreeView.get_selection().get_selected()
        if scriptGroup and treeiter:
            scriptName = model[ treeiter ][ 0 ]
            if self.showOKCancel( scriptNameTreeView, _( "Remove the selected script?" ) ) == Gtk.ResponseType.OK:
                i = 0
                for script in scripts:
                    if script.getGroup() == scriptGroup and script.getName() == scriptName:
                        del scripts[ i ]
                        if scriptGroup not in self.getScriptsByGroup( scripts ):
                            scriptGroup = None

                        self.populateScriptGroupCombo( scripts, scriptGroupComboBox, scriptNameTreeView, scriptGroup, None )
                        if len( scripts ) == 0:
                            commandTextView.get_buffer().set_text( "" )

                        break

                    i += 1


    def onScriptAdd( self, button, scripts, scriptGroupComboBox, scriptNameTreeView ):
        self.addEditScript( Info( "", "", "", False, False, False ), scripts, scriptGroupComboBox, scriptNameTreeView )


    def onScriptNameDoubleClick( self, scriptNameTreeView, scriptNameTreePath, scriptNameTreeViewColumn, scriptGroupComboBox, scripts ):
        self.onScriptEdit( None, scripts, scriptGroupComboBox, scriptNameTreeView )


    def onScriptEdit( self, button, scripts, scriptGroupComboBox, scriptNameTreeView ):
        scriptGroup = scriptGroupComboBox.get_active_text()
        model, treeiter = scriptNameTreeView.get_selection().get_selected()
        if scriptGroup and treeiter:
            scriptName = model[ treeiter ][ 0 ]
            theScript = self.getScript( scripts, scriptGroup, scriptName )
            self.addEditScript( theScript, scripts, scriptGroupComboBox, scriptNameTreeView )


    def addEditScript( self, script, scripts, scriptGroupComboBox, scriptNameTreeView ):
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

        if script.getGroup() == "":
            scriptGroupCombo.set_active( scriptGroupComboBox.get_active() )

        else:
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

        terminalCheckbox = Gtk.CheckButton.new_with_label( _( "Leave terminal open" ) )
        terminalCheckbox.set_tooltip_text( _( "Leave the terminal open after the script completes." ) )
        terminalCheckbox.set_active( script.getTerminalOpen() )

        grid.attach( terminalCheckbox, 0, 22, 1, 1 )

        soundCheckbox = Gtk.CheckButton.new_with_label( _( "Play sound" ) )
        soundCheckbox.set_tooltip_text( _( "Play a beep on script completion." ) )
        soundCheckbox.set_active( script.getPlaySound() )

        grid.attach( soundCheckbox, 0, 23, 1, 1 )

        notificationCheckbox = Gtk.CheckButton.new_with_label( _( "Show notification" ) )
        notificationCheckbox.set_tooltip_text( _( "Show a notification on script completion." ) )
        notificationCheckbox.set_active( script.getShowNotification() )

        grid.attach( notificationCheckbox, 0, 24, 1, 1 )

#TODO Need Background checkbox.

        defaultScriptCheckbox = Gtk.CheckButton.new_with_label( _( "Default script" ) )
        defaultScriptCheckbox.set_active( script.getGroup() == self.defaultScriptGroupCurrent and script.getName() == self.defaultScriptNameCurrent )
        defaultScriptCheckbox.set_tooltip_text( _(
            "If checked, this script will be run on a\n" + \
            "middle mouse click of the indicator icon.\n\n" + \
            "Only one script can be the default." ) )

        grid.attach( defaultScriptCheckbox, 0, 25, 1, 1 )

        title = _( "Edit Script" )
        if script.getGroup() == "":
            title = _( "Add Script" )

        dialog = self.createDialog( scriptNameTreeView, title, grid )
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

                if script.getGroup() == "": # Adding a new script - check for duplicate.
                    if self.getScript( scripts, scriptGroupCombo.get_active_text().strip(), scriptNameEntry.get_text().strip() ):
                        self.showMessage( dialog, _( "A script of the same group and name already exists." ) )
                        scriptGroupCombo.grab_focus()
                        continue

                else: # Editing an existing script.
                    if script.isIdentical(
                        Info( scriptGroupCombo.get_active_text().strip(),
                              scriptNameEntry.get_text().strip(),
                              self.getTextViewText( commandTextView ).strip(),
                              terminalCheckbox.get_active(),
                              soundCheckbox.get_active(),
                              notificationCheckbox.get_active() ) ):
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
                            self.showMessage( dialog, _( "A script of the same group and name already exists." ) )
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
                                  self.getTextViewText( commandTextView ).strip(),
                                  terminalCheckbox.get_active(),
                                  soundCheckbox.get_active(),
                                  notificationCheckbox.get_active() )

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


    def getScriptsByGroup( self, scripts, foregroundOnly = False ):
        scriptsGroupedByName = { }
        for script in scripts:
            if foregroundOnly and script.getBackground():
                continue

            if script.getGroup() not in scriptsGroupedByName:
                scriptsGroupedByName[ script.getGroup() ] = [ ]

            scriptsGroupedByName[ script.getGroup() ].append( script )

        return scriptsGroupedByName


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

        else:
            self.scripts.append( Info( "Network", "Ping Google", "ping -c 3 www.google.com", False, False, False, False, -1 ) )
            self.scripts.append( Info( "Network", "Public IP address", "notify-send -i " + self.icon + " \"Public IP address: $(wget https://ipinfo.io/ip -qO -)\"", False, False, False, False, -1 ) )
            self.scripts.append( Info( "Network", "Up or down", "if wget -qO /dev/null google.com > /dev/null; then notify-send -i " + self.icon + " \"Internet is UP\"; else notify-send \"Internet is DOWN\"; fi", False, False, False, False, -1 ) )
            self.scriptGroupDefault = self.scripts[ -1 ].getGroup()
            self.scriptNameDefault = self.scripts[ -1 ].getName()
            self.scripts.append( Info( "Update", "autoclean | autoremove | update | dist-upgrade", "sudo apt-get autoclean && sudo apt-get -y autoremove && sudo apt-get update && sudo apt-get -y dist-upgrade", True, True, True, False, -1 ) )

#TODO Do a request save (always)?
            self.requestSaveConfig()

#TODO Will need example of background scripts.
#Maybe a script that only produces a result if the internet is down?


#TODO Testing for background scripts...
        # self.scripts.append( Info( "Background", "StackExchange", "python3 /home/bernard/Programming/getStackExchange.py", False, False, False, True, 60 ) )
        # self.scripts.append( Info( "Background", "Bitcoin", "python3 /home/bernard/Programming/getBitcoin.py", False, False, False, True, 5 ) )
        # self.scripts.append( Info( "Background", "Log", "python3 /home/bernard/Programming/checkIndicatorLog.py", False, False, False, True, 60 ) )


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