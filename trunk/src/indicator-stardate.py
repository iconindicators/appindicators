#!/usr/bin/env python


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


# Application indicator which displays an icon and the current stardate.


# TODO: Eventually port from PyGTK to PyGObject - https://live.gnome.org/PyGObject


appindicatorImported = True
try:
    import appindicator
except:
    appindicatorImported = False

import datetime
import gobject
import gtk
import json
import logging
import os
import shutil
import stardate
import sys


class IndicatorStardate:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-stardate"
    VERSION = "1.0.9"
    ICON = "indicator-stardate"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_SHOW_ISSUE = "showIssue"


    def __init__( self ):
        self.dialog = None
        logging.basicConfig( file = sys.stderr, level = logging.INFO )
        self.loadSettings()

        # One of the install dependencies for Debian/Ubuntu is that appindicator exists.
        # However the appindicator only works under Ubuntu Unity - we need to default to GTK icon if not running Unity (say Lubuntu).
        global appindicatorImported
        unityIsInstalled = os.getenv( "XDG_CURRENT_DESKTOP" )
        if unityIsInstalled is None:
            appindicatorImported = False
        elif str( unityIsInstalled ).lower() != "Unity".lower():
            appindicatorImported = False

        self.buildMenu()

        # Create the status icon...either Unity or GTK.
        if appindicatorImported == True:
            self.indicator = appindicator.Indicator( IndicatorStardate.NAME, IndicatorStardate.ICON, appindicator.CATEGORY_APPLICATION_STATUS )
            self.indicator.set_status( appindicator.STATUS_ACTIVE )
            self.indicator.set_menu( self.menu )
        else:
            self.statusicon = gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorStardate.ICON )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.stardate = stardate.Stardate()
        self.update()

        # Use the stardate update period to set a refresh timer.
        # The stardate calculation and WHEN the stardate changes are not synchronised,
        # so update at ten times speed (but no less than once per second).
        period = int( self.stardate.getStardateFractionalPeriod() / 10 ) 
        if period < 1:
            period = 1

        gobject.timeout_add_seconds( period, self.update )

        gtk.main()


    def update( self ):
        self.stardate.setGregorian( datetime.datetime.now() )
        s = self.stardate.toStardateString( False, self.showIssue )

        if appindicatorImported == True:
            self.indicator.set_label( s )
        else:
            self.statusicon.set_tooltip( "Stardate: " + s )
            self.stardateMenuItem.set_label( "Stardate: " + s )

        return True # Needed so the timer continues!


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, gtk.status_icon_position_menu, 1, gtk.get_current_event_time(), self.statusicon )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, gtk.status_icon_position_menu, button, time, self.statusicon )


    def onAbout( self, widget ):
        dialog = gtk.AboutDialog()
        dialog.set_name( IndicatorStardate.NAME )
        dialog.set_version( IndicatorStardate.VERSION )
        dialog.set_comments( IndicatorStardate.AUTHOR )
        dialog.set_license( "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0" )
        dialog.set_website( "https://launchpad.net/~thebernmeister" )
        dialog.run()
        dialog.destroy()


    def buildMenu( self ):
        self.menu = gtk.Menu()

        if appindicatorImported == False:
            image = gtk.Image()
            image.set_from_icon_name( IndicatorStardate.ICON, gtk.ICON_SIZE_MENU )
            self.stardateMenuItem = gtk.ImageMenuItem()
            self.stardateMenuItem.set_image( image )
            self.menu.append( self.stardateMenuItem )
            self.menu.append( gtk.SeparatorMenuItem() )

        preferencesMenuItem = gtk.MenuItem( "Preferences" )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        self.menu.append( preferencesMenuItem )

        aboutMenuItem = gtk.ImageMenuItem( stock_id = gtk.STOCK_ABOUT )
        aboutMenuItem.connect( "activate", self.onAbout )
        self.menu.append( aboutMenuItem )

        quitMenuItem = gtk.ImageMenuItem( stock_id = gtk.STOCK_QUIT )
        quitMenuItem.connect( "activate", gtk.main_quit )
        self.menu.append( quitMenuItem )

        self.menu.show_all()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            return

        self.dialog = gtk.Dialog( "Preferences", None, 0, ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK ) )

        table = gtk.Table( 2, 1, False )
        table.set_col_spacings( 5 )
        table.set_row_spacings( 5 )

        showIssueCheckbox = gtk.CheckButton( "Show Issue" )
        showIssueCheckbox.set_active( self.showIssue )
        table.attach( showIssueCheckbox, 0, 1, 0, 1 )

        autostartCheckbox = gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorStardate.AUTOSTART_PATH + IndicatorStardate.DESKTOP_FILE ) )
        table.attach( autostartCheckbox, 0, 1, 1, 2 )

        self.dialog.vbox.pack_start( table, True, True, 10 )
        self.dialog.set_border_width( 10 )

        self.dialog.show_all()
        response = self.dialog.run()
        if response == gtk.RESPONSE_OK:
            self.showIssue = showIssueCheckbox.get_active()
            self.saveSettings()

            if not os.path.exists( IndicatorStardate.AUTOSTART_PATH ):
                os.makedirs( IndicatorStardate.AUTOSTART_PATH )

            if autostartCheckbox.get_active():
                try:
                    shutil.copy( IndicatorStardate.DESKTOP_PATH + IndicatorStardate.DESKTOP_FILE, IndicatorStardate.AUTOSTART_PATH + IndicatorStardate.DESKTOP_FILE )
                except Exception as e:
                    logging.exception( e )
            else:
                try:
                    os.remove( IndicatorStardate.AUTOSTART_PATH + IndicatorStardate.DESKTOP_FILE )
                except: pass

        self.dialog.destroy()
        self.dialog = None
        self.update()


    def loadSettings( self ):
        self.showIssue = True

        if os.path.isfile( IndicatorStardate.SETTINGS_FILE ):
            try:
                with open( IndicatorStardate.SETTINGS_FILE, 'r' ) as f:
                    settings = json.load( f )

                self.showIssue = settings.get( IndicatorStardate.SETTINGS_SHOW_ISSUE, self.showIssue )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorStardate.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = { IndicatorStardate.SETTINGS_SHOW_ISSUE: self.showIssue }
            with open( IndicatorStardate.SETTINGS_FILE, 'w' ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorStardate.SETTINGS_FILE )


if __name__ == "__main__":
    indicator = IndicatorStardate()
    indicator.main()