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
#  http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html


try:
    from gi.repository import AppIndicator3 as appindicator
except:
    pass

from gi.repository import Gdk, GLib, Gtk

import json, logging, os, shutil, subprocess, sys

try:
    from gi.repository import Notify
except:
    dialog = Gtk.MessageDialog( None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "The package gi.repository.Notify must be installed!" )
    dialog.set_title( "indicator-fortune" )
    dialog.run()
    sys.exit()


class IndicatorFortune:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-fortune"
    VERSION = "1.0.3"

    ICON = NAME
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    DEFAULT_FORTUNE = [ "/usr/share/games/fortunes", True ]
    NOTIFICATION_SUMMARY = "Fortune. . ."

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_FORTUNES = "fortunes"
    SETTINGS_NOTIFICATION_SUMMARY = "notificationSummary"
    SETTINGS_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    SETTINGS_SHOW_NOTIFICATIONS = "showNotifications"
    SETTINGS_SKIP_FORTUNE_CHARACTER_COUNT = "skipFortuneCharacterCount"


    def __init__( self ):
        filehandler = logging.FileHandler( filename = IndicatorFortune.LOG, mode = "a", delay = True )
        logging.basicConfig( format = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                             datefmt = "%H:%M:%S", level = logging.DEBUG,
                             handlers = [ filehandler ] )

        self.dialog = None
        self.clipboard = Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD )
        self.fortune = ""
        self.loadSettings()
        Notify.init( IndicatorFortune.NAME )

        try:
            self.appindicatorImported = True
            self.indicator = appindicator.Indicator.new( IndicatorFortune.NAME, IndicatorFortune.ICON, appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.buildMenu()
            self.indicator.set_menu( self.menu )
        except:
            self.appindicatorImported = False            
            self.buildMenu()
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorFortune.ICON )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.update()
        self.timeoutID = GLib.timeout_add_seconds( self.refreshIntervalInMinutes * 60, self.update )
        Gtk.main()


    def update( self ):
        self.refreshFortune()

        if self.showNotifications:
            notificationSummary = self.notificationSummary
            if notificationSummary == "":
                notificationSummary = " "

            Notify.Notification.new( notificationSummary, self.fortune, IndicatorFortune.ICON ).show()

        return True


    def buildMenu( self ):
        self.menu = Gtk.Menu()

        menuItem = Gtk.MenuItem( "New fortune" )
        menuItem.connect( "activate", self.newFortune )
        self.menu.append( menuItem )

        menuItem = Gtk.MenuItem( "Copy last fortune" )
        menuItem.connect( "activate", self.onCopyLastFortune )
        self.menu.append( menuItem )

        self.menu.append( Gtk.SeparatorMenuItem() )

        preferencesMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        self.menu.append( preferencesMenuItem )

        aboutMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        aboutMenuItem.connect( "activate", self.onAbout )
        self.menu.append( aboutMenuItem )

        quitMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        quitMenuItem.connect( "activate", Gtk.main_quit )
        self.menu.append( quitMenuItem )

        self.menu.show_all()


    def refreshFortune( self ):
        if len( self.fortunes ) == 0:
            self.fortune = "No fortunes defined!"
            return

        fortuneLocations = " "
        for fortuneLocation in self.fortunes:
            if fortuneLocation[ 1 ]:
                if( os.path.isdir( fortuneLocation[ 0 ] ) ):
                    fortuneLocations += "'" + fortuneLocation[ 0 ].rstrip( "/" ) + "/" + "' " # Remove any/all trailing slashes, then add one in as 'fortune' needs it! 
                else:
                    fortuneLocations += "'" + fortuneLocation[ 0 ].rstrip( ".dat" ) + "' " # 'fortune' doesn't want the extension.

        if fortuneLocations == " ":
            self.fortune = "No fortunes enabled!"
            return

        while True:
            self.fortune = ""
            p = subprocess.Popen( "fortune" + fortuneLocations, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
            for line in p.stdout.readlines():
                self.fortune += str( line.decode() )

            p.wait()

            # If the fortune exceeds the limits, John West it...
            if len( self.fortune ) > self.skipFortuneCharacterCount:
                continue

            break


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def newFortune( self, widget ):
        self.refreshFortune()

        notificationSummary = self.notificationSummary
        if notificationSummary == "":
            notificationSummary = " "

        Notify.Notification.new( notificationSummary, self.fortune, IndicatorFortune.ICON ).show()


    def onCopyLastFortune( self, widget ):
        self.clipboard.set_text( self.fortune, -1 )


    def onAbout( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return
 
        self.dialog = Gtk.AboutDialog()
        self.dialog.set_program_name( IndicatorFortune.NAME )
        self.dialog.set_comments( IndicatorFortune.AUTHOR )
        self.dialog.set_website( IndicatorFortune.WEBSITE )
        self.dialog.set_website_label( IndicatorFortune.WEBSITE )
        self.dialog.set_version( IndicatorFortune.VERSION )
        self.dialog.set_license( IndicatorFortune.LICENSE )
        self.dialog.set_icon_name( Gtk.STOCK_ABOUT )
        self.dialog.run()
        self.dialog.destroy()
        self.dialog = None


    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        notebook = Gtk.Notebook()

        # First tab - display settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showNotificationCheckbox = Gtk.CheckButton( "Show screen notification" )
        showNotificationCheckbox.set_active( self.showNotifications )
        showNotificationCheckbox.set_tooltip_text( "Show fortunes in notification bubble" )
        grid.attach( showNotificationCheckbox, 0, 0, 2, 1 )

        label = Gtk.Label( "Refresh interval (minutes)" )
        grid.attach( label, 0, 1, 1, 1 )

        spinnerRefreshInterval = Gtk.SpinButton()
        spinnerRefreshInterval.set_adjustment( Gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60 * 24, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerRefreshInterval.set_value( self.refreshIntervalInMinutes ) # ...so need to force the initial value by explicitly setting it.
        spinnerRefreshInterval.set_tooltip_text( "How often a fortune is displayed" )
        spinnerRefreshInterval.set_hexpand( True )
        grid.attach( spinnerRefreshInterval, 1, 1, 1, 1 )

        label = Gtk.Label( "Character limit" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        spinnerCharacterCount = Gtk.SpinButton()
        spinnerCharacterCount.set_adjustment( Gtk.Adjustment( self.skipFortuneCharacterCount, 1, 1000, 1, 50, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerCharacterCount.set_value( self.skipFortuneCharacterCount ) # ...so need to force the initial value by explicitly setting it.
        spinnerCharacterCount.set_tooltip_text( "Rejects a fortune if it exceeds the character count - don't set too low (below 50) as many fortunes may not appear causing excessive calls to 'fortune'" )
        spinnerCharacterCount.set_hexpand( True )
        grid.attach( spinnerCharacterCount, 1, 2, 1, 1 )

        label = Gtk.Label( "Notification summary" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        notificationSummary = Gtk.Entry()
        notificationSummary.set_text( self.notificationSummary )
        notificationSummary.set_tooltip_text( "The summary text for the notification" )
        grid.attach( notificationSummary, 1, 3, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "Display" ) )

        # Second tab - fortune file settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )
        grid.set_row_homogeneous( False )
        grid.set_column_homogeneous( False )

        store = Gtk.ListStore( str, str ) # Path to fortune file, tick icon (Gtk.STOCK_APPLY) or None for enabled.
        for fortune in self.fortunes:
            if fortune[ 1 ]:
                store.append( [ fortune[ 0 ], Gtk.STOCK_APPLY ] )
            else:
                store.append( [ fortune[ 0 ], None ] )

        tree = Gtk.TreeView( store )
        tree.set_hexpand( True )
        tree.set_vexpand( True )
        tree.append_column( Gtk.TreeViewColumn( "Fortune File/Directory", Gtk.CellRendererText(), text = 0 ) )
        tree.append_column( Gtk.TreeViewColumn( "Enabled", Gtk.CellRendererPixbuf(), stock_id = 1 ) )
        tree.get_column( 0 ).set_sort_column_id( 0 )
        tree.set_tooltip_text( "Double click to edit a fortune's properties" )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onFortuneDoubleClick )

        scrolledWindow = Gtk.ScrolledWindow()

        # The treeview won't expand to show all data, even for a small amount of data.
        # So only add scrollbars if there is a lot of data...greater than 15 say...
        if len( self.fortunes ) <= 15:
            scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER )
        else:
            scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )

        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 0, 1, 1 )

        hbox = Gtk.Box( spacing = 6 )
        hbox.set_homogeneous( True )

        addButton = Gtk.Button( "Add" )
        addButton.connect( "clicked", self.onFortuneAdd, tree )
        hbox.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button( "Remove" )
        removeButton.connect( "clicked", self.onFortuneRemove, tree )
        hbox.pack_start( removeButton, True, True, 0 )

        resetButton = Gtk.Button( "Reset" )
        resetButton.connect( "clicked", self.onFortuneReset, tree )
        hbox.pack_start( resetButton, True, True, 0 )

        grid.attach( hbox, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "Fortunes" ) )

        # Third tab - general settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_tooltip_text( "Run the indicator automatically" )
        autostartCheckbox.set_active( os.path.exists( IndicatorFortune.AUTOSTART_PATH + IndicatorFortune.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 0, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "General" ) )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorFortune.ICON )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.showNotifications = showNotificationCheckbox.get_active()
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

            if not os.path.exists( IndicatorFortune.AUTOSTART_PATH ):
                os.makedirs( IndicatorFortune.AUTOSTART_PATH )

            if autostartCheckbox.get_active():
                try:
                    shutil.copy( IndicatorFortune.DESKTOP_PATH + IndicatorFortune.DESKTOP_FILE, IndicatorFortune.AUTOSTART_PATH + IndicatorFortune.DESKTOP_FILE )
                except Exception as e:
                    logging.exception( e )
            else:
                try:
                    os.remove( IndicatorFortune.AUTOSTART_PATH + IndicatorFortune.DESKTOP_FILE )
                except: pass

            self.update()

        self.dialog.destroy()
        self.dialog = None


    def onFortuneReset( self, button, tree ):
        dialog = Gtk.MessageDialog( None, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, "Reset fortunes to factory default?" )
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            model, treeiter = tree.get_selection().get_selected()
            model.clear()
            model.append( [ IndicatorFortune.DEFAULT_FORTUNE[ 0 ], Gtk.STOCK_APPLY ]  ) # Cannot set True into the model, so need to do this silly thing to get "True" into the model!


    def onFortuneRemove( self, button, tree ):
        model, treeiter = tree.get_selection().get_selected()

        if treeiter is None:
            self.showMessage( Gtk.MessageType.ERROR, "No fortune has been selected for removal." )
            return

        # Prompt the user to remove - only one row can be selected since single selection mode has been set.
        dialog = Gtk.MessageDialog( None, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, "Remove the selected fortune?" )
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            model.remove( treeiter )


    def onFortuneAdd( self, button, tree ):
        self.onFortuneDoubleClick( tree, None, None )


    def onFortuneDoubleClick( self, tree, rowNumber, treeViewColumn ):
        model, treeiter = tree.get_selection().get_selected()

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( "Fortune file/directory" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        # Would be nice to use a file chooser but a file chooser can only choose a file OR a folder at a given time.
        # So would need two buttons - one to launch a file chooser and one to launch a folder chooser.
        # Bit of overkill for something so simple...maybe one day!
        fortuneFileDirectory = Gtk.Entry()
        fortuneFileDirectory.grab_focus()

        if rowNumber is not None: # This is an edit.
            fortuneFileDirectory.set_text( model[ treeiter ][ 0 ] )

        fortuneFileDirectory.set_tooltip_text( "The full path to a fortune .dat file OR a directory containing fortune .dat files.  The corresponding text file(s) must also be present!" )
        fortuneFileDirectory.set_hexpand( True ) # Only need to set this once and all objects will expand.
        grid.attach( fortuneFileDirectory, 1, 0, 1, 1 )

        enabledCheckbox = Gtk.CheckButton( "Enabled" )
        enabledCheckbox.set_tooltip_text( "Include this fortune" )

        enabledCheckbox.set_active( True )
        if rowNumber is not None: # This is an edit.
            enabledCheckbox.set_active( model[ treeiter ][ 1 ] == Gtk.STOCK_APPLY )

        grid.attach( enabledCheckbox, 0, 1, 2, 1 )

        # Would be nice to be able to bring this dialog to front (like the others)...but too much mucking around for little gain!
        title = "Fortune Properties"
        if rowNumber is None:
            title = "Add Fortune"

        dialog = Gtk.Dialog( title, None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorFortune.ICON )

        while True:
            dialog.show_all()
            response = dialog.run()

            if response == Gtk.ResponseType.CANCEL:
                break

            if fortuneFileDirectory.get_text().strip() == "":
                self.showMessage( Gtk.MessageType.ERROR, "The fortune path cannot be empty." )
                fortuneFileDirectory.grab_focus()
                continue

            if not os.path.exists( fortuneFileDirectory.get_text().strip() ):
                self.showMessage( Gtk.MessageType.ERROR, "The fortune path does not exist." )
                fortuneFileDirectory.grab_focus()
                continue

            # Update the data model...
            # Due to this bug https://bugzilla.gnome.org/show_bug.cgi?id=684094 cannot set the model value to None.
            # See more detail in the VirtualBox indicator.
            if rowNumber is not None:
                # This is an edit.
                if enabledCheckbox.get_active():
                    model.set_value( treeiter, 1, Gtk.STOCK_APPLY )
                    model[ treeiter ][ 0 ] = fortuneFileDirectory.get_text().strip()
                else:
                    model.insert_after( treeiter, [ fortuneFileDirectory.get_text().strip(), None ] )
                    model.remove( treeiter )
            else:
                if enabledCheckbox.get_active():
                    model.append( [ fortuneFileDirectory.get_text().strip(), Gtk.STOCK_APPLY ] )
                else:
                    model.append( [ fortuneFileDirectory.get_text().strip(), None ] )

            break

        dialog.destroy()


    def showMessage( self, messageType, message ):
        dialog = Gtk.MessageDialog( None, 0, messageType, Gtk.ButtonsType.OK, message )
        dialog.run()
        dialog.destroy()


    def loadSettings( self ):
        self.fortunes = [ IndicatorFortune.DEFAULT_FORTUNE ]
        self.notificationSummary = IndicatorFortune.NOTIFICATION_SUMMARY
        self.refreshIntervalInMinutes = 15
        self.showNotifications = True
        self.skipFortuneCharacterCount = 500 # From experimentation, about 60 characters per line, but with word boundaries being kept, about 50 characters per line (at most 10 lines).

        if os.path.isfile( IndicatorFortune.SETTINGS_FILE ):
            try:
                with open( IndicatorFortune.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.fortunes = settings.get( IndicatorFortune.SETTINGS_FORTUNES, self.fortunes )
                if self.fortunes == [ ]:
                    self.fortunes = [ IndicatorFortune.DEFAULT_FORTUNE ]

                self.notificationSummary = settings.get( IndicatorFortune.SETTINGS_NOTIFICATION_SUMMARY, self.notificationSummary )
                self.refreshIntervalInMinutes = settings.get( IndicatorFortune.SETTINGS_REFRESH_INTERVAL_IN_MINUTES, self.refreshIntervalInMinutes )
                self.showNotifications = settings.get( IndicatorFortune.SETTINGS_SHOW_NOTIFICATIONS, self.showNotifications )
                self.skipFortuneCharacterCount = settings.get( IndicatorFortune.SETTINGS_SKIP_FORTUNE_CHARACTER_COUNT, self.skipFortuneCharacterCount )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorFortune.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorFortune.SETTINGS_FORTUNES: self.fortunes,
                IndicatorFortune.SETTINGS_NOTIFICATION_SUMMARY: self.notificationSummary,
                IndicatorFortune.SETTINGS_SHOW_NOTIFICATIONS: self.showNotifications,
                IndicatorFortune.SETTINGS_REFRESH_INTERVAL_IN_MINUTES: self.refreshIntervalInMinutes,
                IndicatorFortune.SETTINGS_SKIP_FORTUNE_CHARACTER_COUNT: self.skipFortuneCharacterCount
            }

            with open( IndicatorFortune.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorFortune.SETTINGS_FILE )


if __name__ == "__main__": IndicatorFortune().main()