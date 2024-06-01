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


# Application indicator which displays fortunes.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import codecs
import gi
import os

gi.require_version( "Gdk", "3.0" )
from gi.repository import Gdk

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

try:
    gi.require_version( "Notify", "0.7" )
except ValueError:
    gi.require_version( "Notify", "0.8" )
from gi.repository import Notify

from pathlib import Path


class IndicatorFortune( IndicatorBase ):

    CONFIG_FORTUNES = "fortunes"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON = "middleMouseClickOnIcon"
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW = 1
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST = 2
    CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST = 3
    CONFIG_NOTIFICATION_SUMMARY = "notificationSummary"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SKIP_FORTUNE_CHARACTER_COUNT = "skipFortuneCharacterCount"

    fortune_debian = "/usr/share/games/fortunes"
    if Path( fortune_debian ).exists():
        DEFAULT_FORTUNE = [ fortune_debian, Gtk.STOCK_APPLY ]

    else:
        fortune_fedora = "/usr/share/games/fortune"
        DEFAULT_FORTUNE = [ fortune_fedora, Gtk.STOCK_APPLY ]

    HISTORY_FILE = "fortune-history.txt"

    NOTIFICATION_SUMMARY = _( "Fortune. . ." )
    NOTIFICATION_WARNING_FLAG = "%%%%%" # If present at the start of the current fortune,
                                        # the notification summary should be emitted as a warning
                                        # (rather than a regular fortune).

    # Fortune treeview columns; one to one mapping between data model and view.
    COLUMN_FILE_OR_DIRECTORY = 0 # Either the fortune filename or directory.
    COLUMN_ENABLED = 1 # Icon name for the APPLY icon when the fortune is enabled; None otherwise.


    def __init__( self ):
        super().__init__(
            comments = _( "Calls the 'fortune' program displaying the result in the on-screen notification." ) )

        self.removeFileFromCache( IndicatorFortune.HISTORY_FILE )


    def update( self, menu ):
        self.buildMenu( menu )
        # self.refreshAndShowFortune()#TODO Put back
        return int( self.refreshIntervalInMinutes ) * 60


    def buildMenu( self, menu ):
        self.create_and_append_menuitem(
            menu,
            _( "New Fortune" ),
            activate_function_and_arguments = ( lambda menuItem: self.refreshAndShowFortune(), ),
            isSecondaryActivateTarget = ( self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW ) )

        self.create_and_append_menuitem(
            menu,
            _( "Copy Last Fortune" ),
            activate_function_and_arguments = ( lambda menuItem: Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( self.fortune, -1 ), ),
            isSecondaryActivateTarget = ( self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST ) )

        self.create_and_append_menuitem(
            menu,
            _( "Show Last Fortune" ),
            activate_function_and_arguments = ( lambda menuItem: self.showFortune(), ),
            isSecondaryActivateTarget = ( self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST ) )

        menu.append( Gtk.SeparatorMenuItem() )

        self.create_and_append_menuitem(
            menu,
            _( "History" ),
            activate_function_and_arguments = ( lambda menuItem: self.showHistory(), ) )


    def showHistory( self ):
        textView = Gtk.TextView()
        textView.set_editable( False )
        textView.get_buffer().set_text( self.readCacheTextWithoutTimestamp( IndicatorFortune.HISTORY_FILE ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( textView )

        # Scroll to the end...strange way of doing so!
        # https://stackoverflow.com/questions/5218948/how-to-auto-scroll-a-gtk-scrolledwindow
        def textViewChanged( textView, rectangle ):
            adjustment = textView.get_parent().get_vadjustment()
            adjustment.set_value( adjustment.get_upper() - adjustment.get_page_size() )

        textView.connect( "size-allocate", textViewChanged )

        box = Gtk.Box()
        box.pack_start( scrolledWindow, True, True, 0 )

        self.createDialogExternalToAboutOrPreferences( None, _( "Fortune History for Session" ), box, True )


    def refreshFortune( self ):
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
                    history = self.readCacheTextWithoutTimestamp( IndicatorFortune.HISTORY_FILE )
                    if history is None:
                        history = ""

                    # Remove characters/glyphs which appear as hexadecimal.  Refer to:
                    #     https://askubuntu.com/questions/827193/detect-missing-glyphs-in-text
                    #
                    # Examples:
                    #     Ask not for whom the <CONTROL-G> tolls.
                    #         *** System shutdown message from root ***
                    #     It's a very *__UN*lucky week in which to be took dead.   <--- On Debian 12 this is x0008
                    output = ""
                    for c in self.fortune:
                        if codecs.encode( str.encode( c ), "hex" ) == b'07' or \
                           codecs.encode( str.encode( c ), "hex" ) == b'08':
                            continue

                        output += c

                    self.fortune = output
                    self.writeCacheTextWithoutTimestamp( history + self.fortune + "\n\n", IndicatorFortune.HISTORY_FILE )
                    break


    def showFortune( self ):
        if self.fortune.startswith( IndicatorFortune.NOTIFICATION_WARNING_FLAG ):
            notificationSummary = _( "WARNING. . ." )

        else:
            notificationSummary = self.notificationSummary
            if notificationSummary == "":
                notificationSummary = " "

        Notify.Notification.new(
            notificationSummary,
            self.fortune.strip( IndicatorFortune.NOTIFICATION_WARNING_FLAG ),
            self.get_icon_name() ).show()


    def refreshAndShowFortune( self ):
        self.refreshFortune()
        self.showFortune()


    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

        # Fortune file.
        grid = self.create_grid()

        store = Gtk.ListStore( str, str ) # Path to fortune; tick icon (Gtk.STOCK_APPLY) or error icon (Gtk.STOCK_DIALOG_ERROR) or None.
        for location, enabled in self.fortunes:
            if os.path.isfile( location ) or os.path.isdir( location ):
                store.append( [ location, Gtk.STOCK_APPLY if enabled else None ] )

            else:
                store.append( [ location, Gtk.STOCK_DIALOG_ERROR ] )

        # storeSort = Gtk.TreeModelSort( model = store )
        # storeSort.set_sort_column_id( 0, Gtk.SortType.ASCENDING )  #TODO Should the 0 be IndicatorFortune.COLUMN_FILE_OR_DIRECTORY??? 

        treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                Gtk.TreeModelSort( model = store ),
                ( _( "Fortune File/Directory" ), _( "Enabled" ) ),
                (
                    ( Gtk.CellRendererText(), "text", IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ),
                    ( Gtk.CellRendererPixbuf(), "stock_id", IndicatorFortune.COLUMN_ENABLED ) ),
                alignments_columnviewids = ( ( 0.5, IndicatorFortune.COLUMN_ENABLED ), ),
                sortcolumnviewids_columnmodelids = (
                    ( IndicatorFortune.COLUMN_FILE_OR_DIRECTORY, IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ),
                    ( IndicatorFortune.COLUMN_ENABLED, IndicatorFortune.COLUMN_ENABLED ) ),
                tooltip_text = _(
                    "Double click to edit a fortune.\n\n" + \
                    "English language fortunes are\n" + \
                    "installed by default.\n\n" + \
                    "There may be other fortune\n" + \
                    "packages available in your\n" + \
                    "native language." ),
                rowactivatedfunctionandarguments = ( self.onFortuneDoubleClick, ) )

        # tree = Gtk.TreeView.new_with_model( storeSort )
        # tree.expand_all()
        # tree.set_hexpand( True ) #TODO Can these be added to the scrolledWindow instead?
        # tree.set_vexpand( True )

        # treeViewColumn = \
        #     Gtk.TreeViewColumn(
        #         _( "Fortune File/Directory" ),
        #         Gtk.CellRendererText(),
        #         text = IndicatorFortune.COLUMN_FILE_OR_DIRECTORY )

        # treeViewColumn.set_sort_column_id( 0 )
        # treeViewColumn.set_expand( True )
        # tree.append_column( treeViewColumn )

        # treeViewColumn = Gtk.TreeViewColumn( _( "Enabled" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorFortune.COLUMN_ENABLED )
        # treeViewColumn.set_sort_column_id( 1 )
        # treeViewColumn.set_expand( True )
        # treeViewColumn.set_alignment( 0.5 )
        # tree.append_column( treeViewColumn )

        # tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        # tree.connect( "row-activated", self.onFortuneDoubleClick )
        # tree.set_tooltip_text( _(
        #     "Double click to edit a fortune.\n\n" + \
        #     "English language fortunes are\n" + \
        #     "installed by default.\n\n" + \
        #     "There may be other fortune\n" + \
        #     "packages available in your\n" + \
        #     "native language." ) )

        # scrolledWindow = Gtk.ScrolledWindow()
        # scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        # scrolledWindow.add( tree )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True ) #TODO What does homogeneous mean?

        # addButton = Gtk.Button.new_with_label( _( "Add" ) )
        # addButton.set_tooltip_text( _( "Add a new fortune location." ) )
        # addButton.connect( "clicked", self.onFortuneAdd, tree )
        # box.pack_start( addButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Add" ),
                tooltip_text = _( "Add a new fortune location." ),
                clicked_function_and_arguments = ( self.onFortuneAdd, treeview ) ),
            True,
            True,
            0 )

        # removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        # removeButton.set_tooltip_text( _( "Remove the selected fortune location." ) )
        # removeButton.connect( "clicked", self.onFortuneRemove, tree )
        # box.pack_start( removeButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Remove" ),
                tooltip_text = _( "Remove the selected fortune location." ),
                clicked_function_and_arguments = ( self.onFortuneRemove, treeview ) ),
            True,
            True,
            0 )

        # resetButton = Gtk.Button.new_with_label( _( "Reset" ) )
        # resetButton.set_tooltip_text( _( "Reset to factory default." ) )
        # resetButton.connect( "clicked", self.onFortuneReset, tree )
        # box.pack_start( resetButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        box.pack_start(
            self.create_button(
                _( "Reset" ),
                tooltip_text = _( "Reset to factory default." ),
                clicked_function_and_arguments = ( self.onFortuneReset, treeview ) ),
            True,
            True,
            0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Fortunes" ) ) )


        # General.
        grid = self.create_grid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Refresh interval (minutes)" ) ), False, False, 0 )

        spinnerRefreshInterval = \
            self.create_spinbutton(
                self.refreshIntervalInMinutes,
                1,
                60 * 24,
                tooltip_text = _( "How often a fortune is displayed." ) )

        box.pack_start( spinnerRefreshInterval, False, False, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Notification summary" ) ), False, False, 0 )

        notificationSummary = Gtk.Entry()
        notificationSummary.set_text( self.notificationSummary )
        notificationSummary.set_tooltip_text( _( "The summary text for the notification." ) )
        box.pack_start( notificationSummary, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Message character limit" ) ), False, False, 0 )

        spinnerCharacterCount = \
            self.create_spinbutton(
                self.skipFortuneCharacterCount,
                1,
                1000,
                tooltip_text = _(
                    "If the fortune exceeds the limit,\n" +                                  
                    "a new fortune is created.\n\n" + \
                    "Do not set too low (below 50) as\n" + \
                    "many fortunes may be dropped,\n" + \
                    "resulting in excessive calls to the\n" + \
                    "'fortune' program." ) )

        box.pack_start( spinnerCharacterCount, False, False, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        label = Gtk.Label.new( _( "Middle mouse click of the icon" ) )
        label.set_tooltip_text( _( "Not supported on all desktops." ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 3, 1, 1 )

        # radioMiddleMouseClickNewFortune = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show a new fortune" ) )
        # radioMiddleMouseClickNewFortune.set_active(
        #     self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )
        #
        # radioMiddleMouseClickNewFortune.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( radioMiddleMouseClickNewFortune, 0, 4, 1, 1 )
#TODO Check above.
        radioMiddleMouseClickNewFortune = \
            self.create_radiobutton(
                None,
                _( "Show a new fortune" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )

        grid.attach( radioMiddleMouseClickNewFortune, 0, 4, 1, 1 )

        # radioMiddleMouseClickCopyLastFortune = \
        #     Gtk.RadioButton.new_with_label_from_widget(
        #         radioMiddleMouseClickNewFortune,
        #         _( "Copy current fortune to clipboard" ) )
        #
        # radioMiddleMouseClickCopyLastFortune.set_active(
        #     self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )
        #
        # radioMiddleMouseClickCopyLastFortune.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( radioMiddleMouseClickCopyLastFortune, 0, 5, 1, 1 )
#TODO Check above.
        radioMiddleMouseClickCopyLastFortune = \
            self.create_radiobutton(
                radioMiddleMouseClickNewFortune,
                _( "Copy current fortune to clipboard" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )

        grid.attach( radioMiddleMouseClickCopyLastFortune, 0, 5, 1, 1 )

        # radioMiddleMouseClickShowLastFortune = \
        #     Gtk.RadioButton.new_with_label_from_widget(
        #         radioMiddleMouseClickNewFortune,
        #         _( "Show current fortune" ) )
        #
        # radioMiddleMouseClickShowLastFortune.set_active(
        #     self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )
        #
        # radioMiddleMouseClickShowLastFortune.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( radioMiddleMouseClickShowLastFortune, 0, 6, 1, 1 )
#TODO Check above.
        radioMiddleMouseClickShowLastFortune = \
            self.create_radiobutton(
                radioMiddleMouseClickNewFortune,
                _( "Show current fortune" ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.middleMouseClickOnIcon == IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )

        grid.attach( radioMiddleMouseClickShowLastFortune, 0, 6, 1, 1 )

        autostartCheckbox, delaySpinner, box = self.createAutostartCheckboxAndDelaySpinner()
        grid.attach( box, 0, 7, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
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
                if store[ treeiter ][ IndicatorFortune.COLUMN_ENABLED ] == Gtk.STOCK_APPLY:
                    self.fortunes.append( [ store[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ], True ] )

                else:
                    self.fortunes.append( [ store[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ], False ] )

                treeiter = store.iter_next( treeiter )

            self.setAutostartAndDelay( autostartCheckbox.get_active(), delaySpinner.get_value_as_int() )

        return responseType


    def onFortuneReset( self, button, treeView ):
        if self.showOKCancel( treeView, _( "Reset fortunes to factory default?" ) ) == Gtk.ResponseType.OK:
            listStore = treeView.get_model().get_model()
            listStore.clear()
            listStore.append( IndicatorFortune.DEFAULT_FORTUNE  ) # Cannot set True into the model, so need to do this silly thing to get "True" into the model!


    def onFortuneRemove( self, button, treeView ):
        model, treeiter = treeView.get_selection().get_selected()
        if treeiter is None:
            self.showMessage( treeView, _( "No fortune has been selected for removal." ) ) #TODO If we switch to using BROWSE over SINGLE for all treeviews, can remove this type of check....except if there is no data present!  Need testing!

        elif model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] == IndicatorFortune.DEFAULT_FORTUNE:
            self.showMessage( treeView, _( "This is the default fortune and cannot be deleted." ), Gtk.MessageType.INFO )

        elif self.showOKCancel( treeView, _( "Remove the selected fortune?" ) ) == Gtk.ResponseType.OK:
            model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) )


    def onFortuneAdd( self, button, treeView ):
        self.onFortuneDoubleClick( treeView, None, None )


    def onFortuneDoubleClick( self, treeView, rowNumber, treeViewColumn ):
        model, treeiter = treeView.get_selection().get_selected()

        grid = self.create_grid()

        title = _( "Add Fortune" )
        if rowNumber:
            title = _( "Edit Fortune" )

        dialog = self.createDialog( treeView, title, grid ) #TODO Can this be moved up the top so the buttons are created last and can put the clicked stuff into the new function?

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True )

        box.pack_start( Gtk.Label.new( _( "Fortune file/directory" ) ), False, False, 0 )

        fortuneFileDirectory = Gtk.Entry()
        fortuneFileDirectory.set_editable( False )

        if rowNumber: # This is an edit.
            fortuneFileDirectory.set_text( model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] )
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
            isSystemFortune = \
                model[ treeiter ][ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] == IndicatorFortune.DEFAULT_FORTUNE

        # browseFileButton = Gtk.Button.new_with_label( _( "File" ) )
        # browseFileButton.set_sensitive( not isSystemFortune )
        # if isSystemFortune:
        #     browseFileButton.set_tooltip_text( _(
        #         "This fortune is part of your\n" + \
        #         "system and cannot be modified." ) )
        #
        # else:
        #     browseFileButton.set_tooltip_text( _(
        #         "Choose a fortune .dat file.\n\n" + \
        #         "Ensure the corresponding text\n" + \
        #         "file is present." ) )
        #
        # box.pack_start( browseFileButton, True, True, 0 )
#TODO Ensure this was converted correctly.
        browseFileButton = \
            self.create_button(
                _( "File" ),
                tooltip_text = _(
                    "This fortune is part of your\n" + \
                    "system and cannot be modified." ) \
                    if isSystemFortune else _(
                    "Choose a fortune .dat file.\n\n" + \
                    "Ensure the corresponding text\n" + \
                    "file is present." ),
                sensitive = not isSystemFortune,
                clicked_function_and_arguments = ( self.onBrowseFortune, dialog, fortuneFileDirectory, True ) )

        box.pack_start( browseFileButton, True, True, 0 )

        # browseDirectoryButton = Gtk.Button.new_with_label( _( "Directory" ) )
        # browseDirectoryButton.set_sensitive( not isSystemFortune )
        # if isSystemFortune:
        #     browseDirectoryButton.set_tooltip_text( _(
        #         "This fortune is part of your\n" + \
        #         "system and cannot be modified." ) )
        #
        # else:
        #     browseDirectoryButton.set_tooltip_text( _(
        #         "Choose a directory containing\n" + \
        #         "a fortune .dat file(s).\n\n" + \
        #         "Ensure the corresponding text\n" + \
        #         "file is present." ) )
#TODO Ensure this was converted correctly.
        browseDirectoryButton = \
            self.create_button(
                _( "Directory" ),
                tooltip_text = _( 
                    "This fortune is part of your\n" + \
                    "system and cannot be modified." ) \
                    if isSystemFortune else _(
                    "Choose a directory containing\n" + \
                    "a fortune .dat file(s).\n\n" + \
                    "Ensure the corresponding text\n" + \
                    "file is present." ),
                sensitive = not isSystemFortune,
                clicked_function_and_arguments = ( self.onBrowseFortune, dialog, fortuneFileDirectory, False ) )

        box.pack_start( browseDirectoryButton, True, True, 0 )

        box.set_halign( Gtk.Align.END )

        grid.attach( box, 0, 1, 1, 1 )

        enabledCheckbox = \
            self.create_checkbutton(
                _( "Enabled" ),
                tooltip_text = _(
                    "Ensure the fortune file/directory\n" + \
                    "works by running through 'fortune'\n" + \
                    "in a terminal." ) )
#TODO Ensure above converted correctly.
        # enabledCheckbox = Gtk.CheckButton.new_with_label( _( "Enabled" ) )True
        # enabledCheckbox.set_tooltip_text( _(
        #     "Ensure the fortune file/directory\n" + \
        #     "works by running through 'fortune'\n" + \
        #     "in a terminal." ) )
        #
        # enabledCheckbox.set_active( True ) # This is an add.
        if rowNumber: # This is an edit.
            enabledCheckbox.set_active( model[ treeiter ][ IndicatorFortune.COLUMN_ENABLED ] == Gtk.STOCK_APPLY )

        grid.attach( enabledCheckbox, 0, 2, 1, 1 )

#TODO Moved to top to see if buttons can have the connect in their definitions rather than external.
        # title = _( "Add Fortune" )
        # if rowNumber:
        #     title = _( "Edit Fortune" )
        #
        # dialog = self.createDialog( treeView, title, grid ) #TODO Can this be moved up the top so the buttons are created last and can put the clicked stuff into the new function?

        # browseFileButton.connect( "clicked", self.onBrowseFortune, dialog, fortuneFileDirectory, True )
        # browseDirectoryButton.connect( "clicked", self.onBrowseFortune, dialog, fortuneFileDirectory, False )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:

                if fortuneFileDirectory.get_text().strip() == "": # Will occur if the user does a browse, cancels the browse and hits okay.
                    self.showMessage( dialog, _( "The fortune path cannot be empty." ) )
                    fortuneFileDirectory.grab_focus()
                    continue

                if rowNumber:
                    model.get_model().remove( model.convert_iter_to_child_iter( treeiter ) ) # This is an edit...remove the old value.

                model.get_model().append(
                    [ fortuneFileDirectory.get_text().strip(),
                     Gtk.STOCK_APPLY if enabledCheckbox.get_active() else None ] )

            break

        dialog.destroy()


    def onBrowseFortune( self, fileOrDirectoryButton, addEditDialog, fortuneFileDirectory, isFile ):
        title = _( "Choose a directory containing a fortune .dat file(s)" )
        action = Gtk.FileChooserAction.SELECT_FOLDER
        if isFile:
            title = _( "Choose a fortune .dat file" )
            action = Gtk.FileChooserAction.OPEN

        dialog = \
            Gtk.FileChooserDialog(
                title = title,
                parent = addEditDialog,
                action = action )

        dialog.add_buttons = ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK )

        dialog.set_transient_for( addEditDialog )
        dialog.set_filename( fortuneFileDirectory.get_text() )
        while( True ):
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if dialog.get_filename().startswith( IndicatorFortune.DEFAULT_FORTUNE[ IndicatorFortune.COLUMN_FILE_OR_DIRECTORY ] ):
                    self.showMessage(
                        dialog,
                        _( "The fortune is part of your system and is already included." ),
                        Gtk.MessageType.INFO )

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
            IndicatorFortune.CONFIG_FORTUNES : self.fortunes,
            IndicatorFortune.CONFIG_MIDDLE_MOUSE_CLICK_ON_ICON  : self.middleMouseClickOnIcon,
            IndicatorFortune.CONFIG_NOTIFICATION_SUMMARY  : self.notificationSummary,
            IndicatorFortune.CONFIG_REFRESH_INTERVAL_IN_MINUTES  : self.refreshIntervalInMinutes,
            IndicatorFortune.CONFIG_SKIP_FORTUNE_CHARACTER_COUNT  : self.skipFortuneCharacterCount
        }


IndicatorFortune().main()
