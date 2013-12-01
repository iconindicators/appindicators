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


# Before installing, remove fortune-mod and see if that is the only needed dependency.


# Post to Gwibber
#     def share_last_cookie(self, *arg):
#         p = subprocess.Popen(["gwibber-poster", "-w", "-m", self.body])
#         # setup timeout handler to avoid zombies
#         glib.timeout_add_seconds(1, lambda p: p.poll() is None, p)


# Let the user specify a file(s)?


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
    VERSION = "1.0.0"
    ICON = "indicator-lunar"# NAME
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    NOTIFICATION_TEXT_SUMMARY = "Fortune. . ."

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_SHOW_NOTIFICATIONS = "showNotifications"
    SETTINGS_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"


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
            Notify.Notification.new( IndicatorFortune.NOTIFICATION_TEXT_SUMMARY, self.fortune, IndicatorFortune.ICON ).show()

        return True


    def buildMenu( self ):
        self.menu = Gtk.Menu()

        menuItem = Gtk.MenuItem( "One off the top" )
        menuItem.connect( "activate", self.onOneOffTheTop )
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


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def refreshFortune( self ):
        while True:
            self.fortune = ""
            p = subprocess.Popen( "fortune", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
            for line in p.stdout.readlines():
                # Some fortunes contain a line break to fit with 80 characters, so strip the newline character.
                # However some lines need to be on a new line.
                # For example, the author/source line(which starts with a TAB) or question/answer lines (which contain TAB).
                # So if a line contains a TAB, prepend with a newline.
                l = str( line.decode() ).rstrip() + " "
                if l.find( "\t" ) > -1:
                    l = "\n" + l

                print( l )
                self.fortune += l

            p.wait()

            # From experimentation, it seems that 9 lines of 60 characters per line, totaling 540 characters is the maximum.
            # As word boundaries are maintained when the notification is displayed, approximate the text limit to say 50 characters a line.
            if len( self.fortune ) < ( 9 * 50 ):
                break


    def onOneOffTheTop( self, widget ):
        self.refreshFortune()
        Notify.Notification.new( IndicatorFortune.NOTIFICATION_TEXT_SUMMARY, self.fortune, IndicatorFortune.ICON ).show()


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
        spinnerRefreshInterval.set_adjustment( Gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerRefreshInterval.set_value( self.refreshIntervalInMinutes ) # ...so need to force the initial value by explicitly setting it.
        spinnerRefreshInterval.set_tooltip_text( "How often a fortune is displayed" )
        spinnerRefreshInterval.set_hexpand( True )
        grid.attach( spinnerRefreshInterval, 1, 1, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorFortune.AUTOSTART_PATH + IndicatorFortune.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 2, 2, 1 )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( grid, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorFortune.ICON )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.showNotifications = showNotificationCheckbox.get_active()

            self.refreshIntervalInMinutes = spinnerRefreshInterval.get_value_as_int()
            GLib.source_remove( self.timeoutID )
            self.timeoutID = GLib.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.update )

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

        self.dialog.destroy()
        self.dialog = None


    def loadSettings( self ):
        self.refreshIntervalInMinutes = 15
        self.showNotifications = True

        if os.path.isfile( IndicatorFortune.SETTINGS_FILE ):
            try:
                with open( IndicatorFortune.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.refreshIntervalInMinutes = settings.get( IndicatorFortune.SETTINGS_REFRESH_INTERVAL_IN_MINUTES, self.refreshIntervalInMinutes )
                self.showNotifications = settings.get( IndicatorFortune.SETTINGS_SHOW_NOTIFICATIONS, self.showNotifications )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorFortune.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorFortune.SETTINGS_SHOW_NOTIFICATIONS: self.showNotifications,
                IndicatorFortune.SETTINGS_REFRESH_INTERVAL_IN_MINUTES: self.refreshIntervalInMinutes
            }

            with open( IndicatorFortune.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorFortune.SETTINGS_FILE )


if __name__ == "__main__": IndicatorFortune().main()