#!/usr/bin/env python3


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


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  https://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/api/AppIndicator3_0.1/classes/Indicator.html
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-14.04


INDICATOR_NAME = "indicator-fortune"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import AppIndicator3, Gdk, GLib, Gtk, Notify

import json, locale, logging, os, pythonutils, re, shutil


class IndicatorFortune:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.18"
    ICON = INDICATOR_NAME
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    DESKTOP_FILE = INDICATOR_NAME + ".desktop"

    DEFAULT_FORTUNE = [ "/usr/share/games/fortunes", True ]
    NOTIFICATION_SUMMARY = _( "Fortune. . ." )

    COMMENTS = _( "Calls the 'fortune' program displaying the result in the on-screen notification." )

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_FORTUNES = "fortunes"
    SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON = "middleMouseClickOnIcon"
    SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_NEW = 1
    SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST = 2
    SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST = 3
    SETTINGS_NOTIFICATION_SUMMARY = "notificationSummary"
    SETTINGS_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    SETTINGS_SKIP_FORTUNE_CHARACTER_COUNT = "skipFortuneCharacterCount"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorFortune.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )
        self.dialog = None
        self.clipboard = Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD )
        self.fortune = ""
        self.loadSettings()
        Notify.init( INDICATOR_NAME )

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorFortune.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.set_menu( self.buildMenu() )
        self.update()
        self.timeoutID = GLib.timeout_add_seconds( self.refreshIntervalInMinutes * 60, self.update )


    def main( self ): Gtk.main()


    def update( self ):
        self.refreshFortune()

        notificationSummary = self.notificationSummary
        if notificationSummary == "":
            notificationSummary = " " # Can't be empty text.

        Notify.Notification.new( notificationSummary, self.fortune, IndicatorFortune.ICON ).show()

        return True


    def buildMenu( self ):
        menu = Gtk.Menu()

        menuItem = Gtk.MenuItem( _( "New Fortune" ) )
        menuItem.connect( "activate", self.onShowFortune, True )
        menu.append( menuItem )
        if self.middleMouseClickOnIcon == IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_NEW:
            self.indicator.set_secondary_activate_target( menuItem )

        menuItem = Gtk.MenuItem( _( "Copy Last Fortune" ) )
        menuItem.connect( "activate", self.onCopyLastFortune )
        menu.append( menuItem )
        if self.middleMouseClickOnIcon == IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST:
            self.indicator.set_secondary_activate_target( menuItem )

        menuItem = Gtk.MenuItem( _( "Show Last Fortune" ) )
        menuItem.connect( "activate", self.onShowFortune, False )
        menu.append( menuItem )
        if self.middleMouseClickOnIcon == IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST:
            self.indicator.set_secondary_activate_target( menuItem )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, True, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()
        return menu


    def refreshFortune( self ):
        if len( self.fortunes ) == 0:
            self.fortune = _( "No fortunes defined!" )
        else:
            fortuneLocations = " "
            for fortuneLocation in self.fortunes:
                if fortuneLocation[ 1 ]:
                    if( os.path.isdir( fortuneLocation[ 0 ] ) ):
                        fortuneLocations += "'" + fortuneLocation[ 0 ].rstrip( "/" ) + "/" + "' " # Remove all trailing slashes, then add one in as 'fortune' needs it! 
                    else:
                        fortuneLocations += "'" + fortuneLocation[ 0 ].replace( ".dat", "" ) + "' " # 'fortune' doesn't want the extension.

            if fortuneLocations == " ":
                self.fortune = _( "No fortunes enabled!" )
            else:
                while True:
                    self.fortune = pythonutils.processGet( "fortune" + fortuneLocations )
                    if len( self.fortune ) > self.skipFortuneCharacterCount: # If the fortune exceeds the user-specified character limit, John West it...
                        continue

                    break


    def onShowFortune( self, widget, showNew ):
        if showNew:
            self.refreshFortune()

        notificationSummary = self.notificationSummary
        if notificationSummary == "":
            notificationSummary = " "

        Notify.Notification.new( notificationSummary, self.fortune, IndicatorFortune.ICON ).show()


    def onCopyLastFortune( self, widget ): self.clipboard.set_text( self.fortune, -1 )


    def onAbout( self, widget ):
        if self.dialog is None:
            self.dialog = pythonutils.AboutDialog( 
                INDICATOR_NAME,
                IndicatorFortune.COMMENTS, 
                IndicatorFortune.WEBSITE, 
                IndicatorFortune.WEBSITE, 
                IndicatorFortune.VERSION, 
                Gtk.License.GPL_3_0, 
                IndicatorFortune.ICON,
                [ IndicatorFortune.AUTHOR ],
                "",
                "",
                "/usr/share/doc/" + INDICATOR_NAME + "/changelog.Debian.gz",
                _( "Change _Log" ),
                _( "translator-credits" ),
                logging )

            self.dialog.run()
            self.dialog.destroy()
            self.dialog = None
        else:
            self.dialog.present()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        notebook = Gtk.Notebook()

        # Fortune file settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )
        grid.set_row_homogeneous( False )
        grid.set_column_homogeneous( False )

        store = Gtk.ListStore( str, str ) # Path to fortune file, tick icon (Gtk.STOCK_APPLY) or None.
        store.set_sort_column_id( 0, Gtk.SortType.ASCENDING )
        for fortune in self.fortunes:
            if fortune[ 1 ]:
                store.append( [ fortune[ 0 ], Gtk.STOCK_APPLY ] )
            else:
                store.append( [ fortune[ 0 ], None ] )

        tree = Gtk.TreeView( store )
        tree.expand_all()
        tree.set_hexpand( True )
        tree.set_vexpand( True )
        tree.append_column( Gtk.TreeViewColumn( _( "Fortune File/Directory" ), Gtk.CellRendererText(), text = 0 ) )
        tree.append_column( Gtk.TreeViewColumn( _( "Enabled" ), Gtk.CellRendererPixbuf(), stock_id = 1 ) )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onFortuneDoubleClick )
        tree.set_tooltip_text( _(
            "Double click to edit a fortune.\n\n" + \
            "Basic English language fortunes\n" + \
            "are installed by default.\n\n" + \
            "However, there may be be other\n" + \
            "fortune packages available,\n" + \
            "in addition to fortunes in your\n" + \
            "native language." ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        grid.attach( scrolledWindow, 0, 0, 1, 1 )

        hbox = Gtk.Box( spacing = 6 )
        hbox.set_homogeneous( True )

        addButton = Gtk.Button( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new fortune location." ) )
        addButton.connect( "clicked", self.onFortuneAdd, tree )
        hbox.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected fortune location." ) )
        removeButton.connect( "clicked", self.onFortuneRemove, tree )
        hbox.pack_start( removeButton, True, True, 0 )

        resetButton = Gtk.Button( _( "Reset" ) )
        resetButton.set_tooltip_text( _( "Reset to factory default." ) )
        resetButton.connect( "clicked", self.onFortuneReset, tree )
        hbox.pack_start( resetButton, True, True, 0 )

        hbox.set_halign( Gtk.Align.CENTER )
        grid.attach( hbox, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Fortunes" ) ) )

        # General settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( _( "Refresh interval (minutes)" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        spinnerRefreshInterval = Gtk.SpinButton()
        spinnerRefreshInterval.set_adjustment( Gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60 * 24, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerRefreshInterval.set_value( self.refreshIntervalInMinutes ) # ...so need to force the initial value by explicitly setting it.
        spinnerRefreshInterval.set_tooltip_text( _( "How often a fortune is displayed." ) )
        grid.attach( spinnerRefreshInterval, 1, 0, 1, 1 )

        label = Gtk.Label( _( "Notification summary" ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 1, 1, 1 )

        notificationSummary = Gtk.Entry()
        notificationSummary.set_text( self.notificationSummary )
        notificationSummary.set_tooltip_text( _( "The summary text for the notification." ) )
        notificationSummary.set_hexpand( True )
        notificationSummary.set_margin_top( 10 )
        grid.attach( notificationSummary, 1, 1, 1, 1 )

        label = Gtk.Label( _( "Message character limit" ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 2, 1, 1 )

        spinnerCharacterCount = Gtk.SpinButton()
        spinnerCharacterCount.set_adjustment( Gtk.Adjustment( self.skipFortuneCharacterCount, 1, 1000, 1, 50, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerCharacterCount.set_value( self.skipFortuneCharacterCount ) # ...so need to force the initial value by explicitly setting it.
        spinnerCharacterCount.set_tooltip_text( _(
            "If the fortune exceeds the limit,\n" + \
            "a new fortune is created.\n\n" + \
            "Do not set too low (below 50)\n" + \
            "as many fortunes may be dropped,\n" + \
            "resulting in excessive calls to\n" + \
            "the 'fortune' program." ) )
        spinnerCharacterCount.set_margin_top( 10 )
        grid.attach( spinnerCharacterCount, 1, 2, 1, 1 )

        label = Gtk.Label( _( "Middle mouse click of the icon" ) )
        label.set_tooltip_text( _( "Not supported on all versions/derivatives of Ubuntu!" ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 3, 2, 1 )

        radioMiddleMouseClickNewFortune = Gtk.RadioButton.new_with_label_from_widget( None, _( "Show a new fortune" ) )
        radioMiddleMouseClickNewFortune.set_active( self.middleMouseClickOnIcon == IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_NEW )
        radioMiddleMouseClickNewFortune.set_margin_left( 15 )
        grid.attach( radioMiddleMouseClickNewFortune, 0, 4, 2, 1 )

        radioMiddleMouseClickCopyLastFortune = Gtk.RadioButton.new_with_label_from_widget( radioMiddleMouseClickNewFortune, _( "Copy current fortune to clipboard" ) )
        radioMiddleMouseClickCopyLastFortune.set_active( self.middleMouseClickOnIcon == IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST )
        radioMiddleMouseClickCopyLastFortune.set_margin_left( 15 )
        grid.attach( radioMiddleMouseClickCopyLastFortune, 0, 5, 2, 1 )

        radioMiddleMouseClickShowLastFortune = Gtk.RadioButton.new_with_label_from_widget( radioMiddleMouseClickNewFortune, _( "Show current fortune" ) )
        radioMiddleMouseClickShowLastFortune.set_active( self.middleMouseClickOnIcon == IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST )
        radioMiddleMouseClickShowLastFortune.set_margin_left( 15 )
        grid.attach( radioMiddleMouseClickShowLastFortune, 0, 6, 2, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorFortune.DESKTOP_FILE ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 7, 2, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        self.dialog = Gtk.Dialog( _( "Preferences" ), None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorFortune.ICON )
        self.dialog.show_all()

        if self.dialog.run() == Gtk.ResponseType.OK:
            if radioMiddleMouseClickNewFortune.get_active():
                self.middleMouseClickOnIcon = IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_NEW
            elif radioMiddleMouseClickCopyLastFortune.get_active():
                self.middleMouseClickOnIcon = IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_COPY_LAST
            else:
                self.middleMouseClickOnIcon = IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_SHOW_LAST

            self.refreshIntervalInMinutes = spinnerRefreshInterval.get_value_as_int()
            self.skipFortuneCharacterCount = spinnerCharacterCount.get_value_as_int()
            self.notificationSummary = notificationSummary.get_text()

            GLib.source_remove( self.timeoutID )
            self.timeoutID = GLib.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.update )

            self.fortunes = [ ]
            treeiter = store.get_iter_first()
            while treeiter != None:
                if store[ treeiter ][ 1 ] == Gtk.STOCK_APPLY:
                    self.fortunes.append( [ store[ treeiter ][ 0 ], True ] )
                else:
                    self.fortunes.append( [ store[ treeiter ][ 0 ], False ] )

                treeiter = store.iter_next( treeiter )

            self.saveSettings()
            pythonutils.setAutoStart( IndicatorFortune.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            self.indicator.set_menu( self.buildMenu() ) # Results in an assertion which turns out is caused by self.indicator.set_secondary_activate_target( menuItem ) which does not go away even if calling via GLib.idle_add.

        self.dialog.destroy()
        self.dialog = None


    def onFortuneReset( self, button, tree ):
        if pythonutils.showOKCancel( None, _( "Reset fortunes to factory default?" ) ) == Gtk.ResponseType.OK:
            model, treeiter = tree.get_selection().get_selected()
            model.clear()
            model.append( [ IndicatorFortune.DEFAULT_FORTUNE[ 0 ], Gtk.STOCK_APPLY ]  ) # Cannot set True into the model, so need to do this silly thing to get "True" into the model!


    def onFortuneRemove( self, button, tree ):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter is None:
            pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, _( "No fortune has been selected for removal." ) )
        elif pythonutils.showOKCancel( None, _( "Remove the selected fortune?" ) ) == Gtk.ResponseType.OK: # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            model.remove( treeiter )


    def onFortuneAdd( self, button, tree ): self.onFortuneDoubleClick( tree, None, None )


    def onFortuneDoubleClick( self, tree, rowNumber, treeViewColumn ):
        model, treeiter = tree.get_selection().get_selected()

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( _( "Fortune file/directory" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        fortuneFileDirectory = Gtk.Entry()
        fortuneFileDirectory.set_width_chars( 20 )

        if rowNumber is None: # This is an add.
            fortuneFileDirectory.set_text( IndicatorFortune.DEFAULT_FORTUNE[ 0 ] )
        else: # This is an edit.
            fortuneFileDirectory.set_text( model[ treeiter ][ 0 ] )

        fortuneFileDirectory.set_width_chars( len( fortuneFileDirectory.get_text() ) * 5 / 4 ) # Sometimes the length is shorter than set due to packing, so make it longer.
        fortuneFileDirectory.set_tooltip_text( _(
            "The full path to a fortune .dat file,\n" + \
            "or a directory which contains fortune\n" + \
            ".dat files.\n\n" + \
            "Ensure the corresponding fortune text\n" + \
            "file(s) is present!" ) )
        fortuneFileDirectory.set_hexpand( True ) # Only need to set this once and all objects will expand.
        grid.attach( fortuneFileDirectory, 1, 0, 1, 1 )

        hbox = Gtk.Box( spacing = 6 )
        hbox.set_homogeneous( True )

        browseFileButton = Gtk.Button( _( "File" ) )
        browseFileButton.set_tooltip_text( _(
            "Choose a fortune .dat file.\n" + \
            "Ensure the corresponding text\n" + \
            "file is present!" ) )
        hbox.pack_start( browseFileButton, True, True, 0 )

        browseDirectoryButton = Gtk.Button( _( "Directory" ) )
        browseDirectoryButton.set_tooltip_text( _(
            "Choose a directory containing a\n" + \
            "fortune .dat file(s).\n" + \
            "Ensure the corresponding text\n" + \
            "file(s) is present!" ) )
        hbox.pack_start( browseDirectoryButton, True, True, 0 )

        hbox.set_halign( Gtk.Align.END )
        grid.attach( hbox, 0, 1, 2, 1 )

        enabledCheckbox = Gtk.CheckButton( _( "Enabled" ) )
        enabledCheckbox.set_tooltip_text( _(
            "Ensure the fortune file/directory\n" + \
            "works by running it through 'fortune'\n" + \
            "in a terminal." ) )
        if rowNumber is not None: # This is an edit.
            enabledCheckbox.set_active( model[ treeiter ][ 1 ] == Gtk.STOCK_APPLY )

        grid.attach( enabledCheckbox, 0, 2, 1, 1 )

        title = _( "Fortune Properties" )
        if rowNumber is None:
            title = _( "Add Fortune" )

        dialog = Gtk.Dialog( title, self.dialog, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorFortune.ICON )

        # Need to set these here as the dialog had not been created at the point the buttons were defined.
        browseFileButton.connect( "clicked", self.onBrowseFortune, dialog, fortuneFileDirectory, True )
        browseDirectoryButton.connect( "clicked", self.onBrowseFortune, dialog, fortuneFileDirectory, False )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:

                if fortuneFileDirectory.get_text().strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The fortune path cannot be empty." ) )
                    fortuneFileDirectory.grab_focus()
                    continue
    
                if not os.path.exists( fortuneFileDirectory.get_text().strip() ):
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The fortune path does not exist." ) )
                    fortuneFileDirectory.grab_focus()
                    continue

                if rowNumber is not None:
                    model.remove( treeiter ) # This is an edit...remove the old value and append new value.  
    
                if enabledCheckbox.get_active():
                    model.append( [ fortuneFileDirectory.get_text().strip(), Gtk.STOCK_APPLY ] )
                else:
                    model.append( [ fortuneFileDirectory.get_text().strip(), None ] )

            break

        dialog.destroy()


    def onBrowseFortune( self, fileOrDirectoryButton, addEditDialog, fortuneFileDirectory, isFile ):
        if isFile:
            title = _( "Choose a fortune .dat file" )
            action = Gtk.FileChooserAction.OPEN
        else:
            title = _( "Choose a directory containing a fortune .dat file(s)" )
            action = Gtk.FileChooserAction.SELECT_FOLDER

        dialog = Gtk.FileChooserDialog( title, addEditDialog, action, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK ) )
        dialog.set_modal( True ) # TODO: This seems to have no effect - the underlying add/edit dialog is still clickable.
        dialog.set_filename( fortuneFileDirectory.get_text() )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            fortuneFileDirectory.set_text( dialog.get_filename() )

        dialog.destroy()


    def loadSettings( self ):
        self.fortunes = [ IndicatorFortune.DEFAULT_FORTUNE ]
        self.middleMouseClickOnIcon = IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON_NEW
        self.notificationSummary = IndicatorFortune.NOTIFICATION_SUMMARY
        self.refreshIntervalInMinutes = 15
        self.skipFortuneCharacterCount = 360 # From experimentation, about 45 characters per line, but with word boundaries maintained, say 40 characters per line (with at most 9 lines).

        if os.path.isfile( IndicatorFortune.SETTINGS_FILE ):
            try:
                with open( IndicatorFortune.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.fortunes = settings.get( IndicatorFortune.SETTINGS_FORTUNES, self.fortunes )
                if self.fortunes == [ ]:
                    self.fortunes = [ IndicatorFortune.DEFAULT_FORTUNE ]

                self.fortunes.sort( key = lambda x: x[ 0 ] )

                self.middleMouseClickOnIcon = settings.get( IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON, self.middleMouseClickOnIcon )
                self.notificationSummary = settings.get( IndicatorFortune.SETTINGS_NOTIFICATION_SUMMARY, self.notificationSummary )
                self.refreshIntervalInMinutes = settings.get( IndicatorFortune.SETTINGS_REFRESH_INTERVAL_IN_MINUTES, self.refreshIntervalInMinutes )
                self.skipFortuneCharacterCount = settings.get( IndicatorFortune.SETTINGS_SKIP_FORTUNE_CHARACTER_COUNT, self.skipFortuneCharacterCount )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorFortune.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorFortune.SETTINGS_FORTUNES: self.fortunes,
                IndicatorFortune.SETTINGS_MIDDLE_MOUSE_CLICK_ON_ICON: self.middleMouseClickOnIcon,
                IndicatorFortune.SETTINGS_NOTIFICATION_SUMMARY: self.notificationSummary,
                IndicatorFortune.SETTINGS_REFRESH_INTERVAL_IN_MINUTES: self.refreshIntervalInMinutes,
                IndicatorFortune.SETTINGS_SKIP_FORTUNE_CHARACTER_COUNT: self.skipFortuneCharacterCount
            }

            with open( IndicatorFortune.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorFortune.SETTINGS_FILE )


if __name__ == "__main__": IndicatorFortune().main()