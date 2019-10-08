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


# Application indicator which displays fortunes.


INDICATOR_NAME = "indicator-fortune"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gdk", "3.0" )
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gdk, Gtk, Notify

import indicatorbase, os


class IndicatorFortune( indicatorbase.IndicatorBase ):

    CONFIG_FORTUNES = "fortunes"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON = "middleMouseClickOnIcon"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW = 1
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST = 2
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST = 3
    CONFIG_NOTIFICATION_SUMMARY = "notificationSummary"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SKIP_FORTUNE_CHARACTER_COUNT = "skipFortuneCharacterCount"

    DEFAULT_FORTUNE = [ "/usr/share/games/fortunes", Gtk.STOCK_APPLY ]
    HISTORY_FILE = "fortune-history"

    NOTIFICATION_SUMMARY = _( "Fortune. . ." )
    NOTIFICATION_WARNING_FLAG = "%%%%%" # If present at the start of the current fortune, the notification summary should be emitted as a warning (rather than a regular fortune).


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.30",
            copyrightStartYear = "2013",
            comments = _( "Calls the 'fortune' program displaying the result in the on-screen notification." ) )

        self.removeFileFromCache( IndicatorFortune.HISTORY_FILE )


    def update( self, menu ):
        self.buildMenu( menu )
        self.refreshAndShowFortune()
        return int( self.refreshIntervalInMinutes ) * 60


    def buildMenu( self, menu ):
        menuItem = Gtk.MenuItem( _( "New Fortune" ) )
        menuItem.connect( "activate", lambda widget: self.refreshAndShowFortune() )
        menu.append( menuItem )
        if self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW:
            self.indicator.set_secondary_activate_target( menuItem )

        menuItem = Gtk.MenuItem( _( "Copy Last Fortune" ) )
        menuItem.connect( "activate", lambda widget: Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( self.fortune, -1 ) )
        menu.append( menuItem )
        if self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST:
            self.indicator.set_secondary_activate_target( menuItem )

        menuItem = Gtk.MenuItem( _( "Show Last Fortune" ) )
        menuItem.connect( "activate", lambda widget: self.showFortune() )
        menu.append( menuItem )
        if self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST:
            self.indicator.set_secondary_activate_target( menuItem )


#TODO Maybe remove the warning stuff...maybe log?
    def refreshFortune( self ):
        if len( self.fortunes ) == 0:
            self.fortune = IndicatorFortune.NOTIFICATION_WARNING_FLAG + _( "No fortunes are enabled!" )

        else:
            locations = " "
            for location, enabled in self.fortunes:
                if enabled:
                    if os.path.isdir( location ):
                        locations += "'" + location.rstrip( "/" ) + "/" + "' " # Remove all trailing slashes, then add one in as 'fortune' needs it! 

                    elif os.path.isfile( location ):
                        locations += "'" + location.replace( ".dat", "" ) + "' " # 'fortune' doesn't want the extension.

            if locations == " ": # Despite one or more fortunes enabled, none seem to be valid paths/files...
                self.fortune = IndicatorFortune.NOTIFICATION_WARNING_FLAG + _( "No enabled fortunes have a valid location!" )

            else:
                while True:
                    self.fortune = self.processGet( "fortune" + locations )
                    if self.fortune is None: # Occurs when no fortune data is found...
                        self.fortune = IndicatorFortune.NOTIFICATION_WARNING_FLAG + _( "Ensure enabled fortunes contain fortune data!" )
                        break

                    elif len( self.fortune ) <= self.skipFortuneCharacterCount: # If the fortune is within the character limit keep it...
                        history = self.readCacheText( IndicatorFortune.HISTORY_FILE )
                        if history is None:
                            history = ""

                        self.writeCacheText( IndicatorFortune.HISTORY_FILE, history + self.fortune + "\n\n" )
                        break


    def showFortune( self ):
        if self.fortune.startswith( IndicatorFortune.NOTIFICATION_WARNING_FLAG ):
            notificationSummary = _( "WARNING. . ." )

        else:
            notificationSummary = self.notificationSummary
            if notificationSummary == "":
                notificationSummary = " "

        Notify.Notification.new( notificationSummary, self.fortune.strip( IndicatorFortune.NOTIFICATION_WARNING_FLAG ), self.icon ).show()


    def refreshAndShowFortune( self ):
        self.refreshFortune()
        self.showFortune()


    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

        # Fortune file.
        grid = self.createGrid()

        store = Gtk.ListStore( str, str ) # Path to fortune; tick icon (Gtk.STOCK_APPLY) or error icon (Gtk.STOCK_DIALOG_ERROR) or None.
        for location, enabled in self.fortunes:
            if os.path.isfile( location ) or os.path.isdir( location ):
                store.append( [ location, Gtk.STOCK_APPLY if enabled else None ] )

            else:
                store.append( [ location, Gtk.STOCK_DIALOG_ERROR ] )

        storeSort = Gtk.TreeModelSort( model = store )
        storeSort.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( storeSort )
        tree.expand_all()
        tree.set_hexpand( True )
        tree.set_vexpand( True )

        treeViewColumn = Gtk.TreeViewColumn( _( "Fortune File/Directory" ), Gtk.CellRendererText(), text = 0 )
        treeViewColumn.set_sort_column_id( 0 )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Enabled" ), Gtk.CellRendererPixbuf(), stock_id = 1 )
        treeViewColumn.set_sort_column_id( 1 )
        tree.append_column( treeViewColumn )

        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onFortuneDoubleClick )
        tree.set_tooltip_text( _(
            "Double click to edit a fortune.\n\n" + \
            "English language fortunes are\n" + \
            "installed by default.\n\n" + \
            "There may be other fortune\n" + \
            "packages available in your\n" + \
            "native language." ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        grid.attach( scrolledWindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )

        addButton = Gtk.Button( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new fortune location." ) )
        addButton.connect( "clicked", self.onFortuneAdd, tree )
        box.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected fortune location." ) )
        removeButton.connect( "clicked", self.onFortuneRemove, tree )
        box.pack_start( removeButton, True, True, 0 )

        resetButton = Gtk.Button( _( "Reset" ) )
        resetButton.set_tooltip_text( _( "Reset to factory default." ) )
        resetButton.connect( "clicked", self.onFortuneReset, tree )
        box.pack_start( resetButton, True, True, 0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Fortunes" ) ) )

        # General.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Refresh interval (minutes)" ) ), False, False, 0 )

        spinnerRefreshInterval = Gtk.SpinButton()
        spinnerRefreshInterval.set_adjustment( Gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60 * 24, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerRefreshInterval.set_value( self.refreshIntervalInMinutes ) # ...so need to force the initial value by explicitly setting it.
        spinnerRefreshInterval.set_tooltip_text( _( "How often a fortune is displayed." ) )
        box.pack_start( spinnerRefreshInterval, False, False, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Notification summary" ) ), False, False, 0 )

        notificationSummary = Gtk.Entry()
        notificationSummary.set_text( self.notificationSummary )
        notificationSummary.set_tooltip_text( _( "The summary text for the notification." ) )
        notificationSummary.set_hexpand( True )
        box.pack_start( notificationSummary, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Message character limit" ) ), False, False, 0 )

        spinnerCharacterCount = Gtk.SpinButton()
        spinnerCharacterCount.set_adjustment( Gtk.Adjustment( self.skipFortuneCharacterCount, 1, 1000, 1, 50, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerCharacterCount.set_value( self.skipFortuneCharacterCount ) # ...so need to force the initial value by explicitly setting it.
        spinnerCharacterCount.set_tooltip_text( _(
            "If the fortune exceeds the limit,\n" + \
            "a new fortune is created.\n\n" + \
            "Do not set too low (below 50) as\n" + \
            "many fortunes may be dropped,\n" + \
            "resulting in excessive calls to the\n" + \
            "'fortune' program." ) )
        box.pack_start( spinnerCharacterCount, False, False, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        label = Gtk.Label( _( "Middle mouse click of the icon" ) )
        label.set_tooltip_text( _( "Not supported on all versions/derivatives of Ubuntu." ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 3, 1, 1 )

        radioMiddleMouseClickNewFortune = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show a new fortune" ) )
        radioMiddleMouseClickNewFortune.set_active( self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )
        radioMiddleMouseClickNewFortune.set_margin_left( self.INDENT_WIDGET_LEFT )
        grid.attach( radioMiddleMouseClickNewFortune, 0, 4, 1, 1 )

        radioMiddleMouseClickCopyLastFortune = Gtk.RadioButton.new_with_label_from_widget( radioMiddleMouseClickNewFortune, _( "Copy current fortune to clipboard" ) )
        radioMiddleMouseClickCopyLastFortune.set_active( self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )
        radioMiddleMouseClickCopyLastFortune.set_margin_left( self.INDENT_WIDGET_LEFT )
        grid.attach( radioMiddleMouseClickCopyLastFortune, 0, 5, 1, 1 )

        radioMiddleMouseClickShowLastFortune = Gtk.RadioButton.new_with_label_from_widget( radioMiddleMouseClickNewFortune, _( "Show current fortune" ) )
        radioMiddleMouseClickShowLastFortune.set_active( self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )
        radioMiddleMouseClickShowLastFortune.set_margin_left( self.INDENT_WIDGET_LEFT )
        grid.attach( radioMiddleMouseClickShowLastFortune, 0, 6, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( self.isAutoStart() )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 7, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            if radioMiddleMouseClickNewFortune.get_active():
                self.middleMouseClickOnIcon = IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW

            elif radioMiddleMouseClickCopyLastFortune.get_active():
                self.middleMouseClickOnIcon = IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST

            else:
                self.middleMouseClickOnIcon = IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST

            self.refreshIntervalInMinutes = spinnerRefreshInterval.get_value_as_int()
            self.skipFortuneCharacterCount = spinnerCharacterCount.get_value_as_int()
            self.notificationSummary = notificationSummary.get_text()

            self.fortunes = [ ]
            treeiter = store.get_iter_first()
            while treeiter != None:
                if store[ treeiter ][ 1 ] == Gtk.STOCK_APPLY:
                    self.fortunes.append( [ store[ treeiter ][ 0 ], True ] )

                else:
                    self.fortunes.append( [ store[ treeiter ][ 0 ], False ] )

                treeiter = store.iter_next( treeiter )

            self.setAutoStart( autostartCheckbox.get_active() )
            self.requestSaveConfig()


    def onFortuneReset( self, button, treeView ):
        if self.showOKCancel( treeView, _( "Reset fortunes to factory default?" ), INDICATOR_NAME ) == Gtk.ResponseType.OK:
            listStore = treeView.get_model().get_model()
            listStore.clear()
            listStore.append( IndicatorFortune.DEFAULT_FORTUNE  ) # Cannot set True into the model, so need to do this silly thing to get "True" into the model!


    def onFortuneRemove( self, button, treeView ):
        model, treeiter = treeView.get_selection().get_selected()
        if treeiter is None:
            self.showMessage( treeView, Gtk.MessageType.ERROR, _( "No fortune has been selected for removal." ), INDICATOR_NAME )

        elif model[ treeiter ][ 0 ] == IndicatorFortune.DEFAULT_FORTUNE:
            self.showMessage( treeView, Gtk.MessageType.WARNING, _( "This is the default fortune and cannot be deleted." ), INDICATOR_NAME )

        elif self.showOKCancel( treeView, _( "Remove the selected fortune?" ), INDICATOR_NAME ) == Gtk.ResponseType.OK:
            model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) )


    def onFortuneAdd( self, button, treeView ): self.onFortuneDoubleClick( treeView, None, None )


    def onFortuneDoubleClick( self, treeView, rowNumber, treeViewColumn ):
        model, treeiter = treeView.get_selection().get_selected()

        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Fortune file/directory" ) ), False, False, 0 )

        fortuneFileDirectory = Gtk.Entry()
        fortuneFileDirectory.set_editable( False )
        fortuneFileDirectory.set_hexpand( True )

        if rowNumber: # This is an edit.
            fortuneFileDirectory.set_text( model[ treeiter ][ 0 ] )
            fortuneFileDirectory.set_width_chars( len( fortuneFileDirectory.get_text() ) * 5 / 4 ) # Sometimes the length is shorter than set due to packing, so make it longer.

        fortuneFileDirectory.set_tooltip_text( _(
            "The path to a fortune .dat file,\n" + \
            "or a directory containing\n" + \
            "fortune .dat files.\n\n" + \
            "Ensure the corresponding\n" + \
            "fortune text file(s) is present." ) )

        box.pack_start( fortuneFileDirectory, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )

        isSystemFortune = False # This is an add.
        if rowNumber: # This is an edit.
            isSystemFortune = model[ treeiter ][ 0 ] == IndicatorFortune.DEFAULT_FORTUNE

        browseFileButton = Gtk.Button( _( "File" ) )
        browseFileButton.set_sensitive( not isSystemFortune )
        if isSystemFortune:
            browseFileButton.set_tooltip_text( _(
                "This fortune is part of\n" + \
                "your system and cannot be\n" + \
                "modified." ) )

        else:
            browseFileButton.set_tooltip_text( _( 
                "Choose a fortune .dat file.\n\n" + \
                "Ensure the corresponding text\n" + \
                "file is present." ) )

        box.pack_start( browseFileButton, True, True, 0 )

        browseDirectoryButton = Gtk.Button( _( "Directory" ) )
        browseDirectoryButton.set_sensitive( not isSystemFortune )
        if isSystemFortune:
            browseDirectoryButton.set_tooltip_text( _(
                "This fortune is part of\n" + \
                "your system and cannot be\n" + \
                "modified." ) )

        else:
            browseDirectoryButton.set_tooltip_text( _( 
                "Choose a directory containing\n" + \
                "a fortune .dat file(s).\n\n" + \
                "Ensure the corresponding text\n" + \
                "file is present." ) )

        box.pack_start( browseDirectoryButton, True, True, 0 )

        box.set_halign( Gtk.Align.END )

        grid.attach( box, 0, 1, 1, 1 )

        enabledCheckbox = Gtk.CheckButton( _( "Enabled" ) )
        enabledCheckbox.set_tooltip_text( _(
            "Ensure the fortune file/directory\n" + \
            "works by running through 'fortune'\n" + \
            "in a terminal." ) )

        enabledCheckbox.set_active( True ) # This is an add.
        if rowNumber: # This is an edit.
            enabledCheckbox.set_active( model[ treeiter ][ 1 ] == Gtk.STOCK_APPLY )

        grid.attach( enabledCheckbox, 0, 2, 1, 1 )

        title = _( "Add Fortune" )
        if rowNumber:
            title = _( "Edit Fortune" )

        dialog = self.createDialog( title, grid, treeView )

        browseFileButton.connect( "clicked", self.onBrowseFortune, dialog, fortuneFileDirectory, True )
        browseDirectoryButton.connect( "clicked", self.onBrowseFortune, dialog, fortuneFileDirectory, False )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:

                if fortuneFileDirectory.get_text().strip() == "": # Will occur if the user does a browse, cancels the browse and hits okay.
                    self.showMessage( dialog, Gtk.MessageType.ERROR, _( "The fortune path cannot be empty." ), INDICATOR_NAME )
                    fortuneFileDirectory.grab_focus()
                    continue

                if rowNumber:
                    model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) ) # This is an edit...remove the old value.

                model.get_model().append( [ fortuneFileDirectory.get_text().strip(), Gtk.STOCK_APPLY if enabledCheckbox.get_active() else None ] )

            break

        dialog.destroy()


    def onBrowseFortune( self, fileOrDirectoryButton, addEditDialog, fortuneFileDirectory, isFile ):
        title = _( "Choose a directory containing a fortune .dat file(s)" )
        action = Gtk.FileChooserAction.SELECT_FOLDER
        if isFile:
            title = _( "Choose a fortune .dat file" )
            action = Gtk.FileChooserAction.OPEN

        dialog = Gtk.FileChooserDialog( title, addEditDialog, action, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK ) )
        dialog.set_modal( True ) # On Ubuntu 14.04 the underlying add/edit dialog is still clickable, but behaves in Ubuntu 16.04/17.04.
        dialog.set_filename( fortuneFileDirectory.get_text() )
        while( True ):
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if dialog.get_filename().startswith( IndicatorFortune.DEFAULT_FORTUNE[ 0 ] ):
                    self.showMessage( dialog, Gtk.MessageType.INFO, _( "The fortune is part of your system and is already included." ), INDICATOR_NAME )

                else:
                    fortuneFileDirectory.set_text( dialog.get_filename() )
                    break

            else:
                break

        dialog.destroy()


    def loadConfig( self, config ):
        self.fortunes = config.get( IndicatorFortune.CONFIG_FORTUNES, [ IndicatorFortune.DEFAULT_FORTUNE ] )
        self.middleMouseClickOnIcon = config.get( IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON, IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )
        self.notificationSummary = config.get( IndicatorFortune.CONFIG_NOTIFICATION_SUMMARY, IndicatorFortune.NOTIFICATION_SUMMARY )
        self.refreshIntervalInMinutes = config.get( IndicatorFortune.CONFIG_REFRESH_INTERVAL_IN_MINUTES, 15 )
        self.skipFortuneCharacterCount = config.get( IndicatorFortune.CONFIG_SKIP_FORTUNE_CHARACTER_COUNT, 360 ) # From experimentation, about 45 characters per line, but with word boundaries maintained, say 40 characters per line (with at most 9 lines).


    def saveConfig( self ):
        return {
            IndicatorFortune.CONFIG_FORTUNES: self.fortunes,
            IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON: self.middleMouseClickOnIcon,
            IndicatorFortune.CONFIG_NOTIFICATION_SUMMARY: self.notificationSummary,
            IndicatorFortune.CONFIG_REFRESH_INTERVAL_IN_MINUTES: self.refreshIntervalInMinutes,
            IndicatorFortune.CONFIG_SKIP_FORTUNE_CHARACTER_COUNT: self.skipFortuneCharacterCount
        }


IndicatorFortune().main()