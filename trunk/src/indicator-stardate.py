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


# Application indicator which displays the current stardate.


appindicatorImported = True
try:
    from gi.repository import AppIndicator3 as appindicator
except:
    appindicatorImported = False

from gi.repository import GObject as gobject
from gi.repository import Gtk

import datetime
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
    ICON = NAME
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    WEBSITE = "https://launchpad.net/~thebernmeister"

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
            self.indicator = appindicator.Indicator.new( IndicatorStardate.NAME, IndicatorStardate.ICON, appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.indicator.set_menu( self.menu )
        else:
            self.statusicon = Gtk.StatusIcon()
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

        gobject.timeout_add( period * 1000, self.update )

        Gtk.main()


    def update( self ):
        self.stardate.setGregorian( datetime.datetime.now() )
        s = self.stardate.toStardateString( False, self.showIssue )

        if appindicatorImported == True:
            self.indicator.set_label( s, "" ) # Second parameter is a guide for how wide the text could get (see label-guide in http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html).
        else:
            self.statusicon.set_tooltip_text( "Stardate: " + s )
            self.stardateMenuItem.set_label( "Stardate: " + s )

        return True # Needed so the timer continues!


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def onAbout( self, widget ):
        dialog = Gtk.AboutDialog()
        dialog.set_program_name( IndicatorStardate.NAME )
        dialog.set_comments( IndicatorStardate.AUTHOR + "\n\nBased on STARDATES IN STAR TREK FAQ V1.6\n" )
        dialog.set_website( IndicatorStardate.WEBSITE )
        dialog.set_website_label( IndicatorStardate.WEBSITE )
        dialog.set_version( IndicatorStardate.VERSION )
        dialog.set_license( IndicatorStardate.LICENSE )
        dialog.run()
        dialog.destroy()
        dialog = None


    def buildMenu( self ):
        self.menu = Gtk.Menu()

        if appindicatorImported == False:
            image = Gtk.Image()
            image.set_from_icon_name( IndicatorStardate.ICON, Gtk.IconSize.MENU )
            self.stardateMenuItem = Gtk.ImageMenuItem()
            self.stardateMenuItem.set_image( image )
            self.menu.append( self.stardateMenuItem )
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


    def onPreferences( self, widget ):
        if self.dialog is not None:
            return

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showIssueCheckbox = Gtk.CheckButton( "Show Issue" )
        showIssueCheckbox.set_active( self.showIssue )
        grid.attach( showIssueCheckbox, 0, 0, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorStardate.AUTOSTART_PATH + IndicatorStardate.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 1, 1, 1 )

        self.dialog.vbox.pack_start( grid, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
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
                with open( IndicatorStardate.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.showIssue = settings.get( IndicatorStardate.SETTINGS_SHOW_ISSUE, self.showIssue )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorStardate.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = { IndicatorStardate.SETTINGS_SHOW_ISSUE: self.showIssue }
            with open( IndicatorStardate.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorStardate.SETTINGS_FILE )


if __name__ == "__main__":
    indicator = IndicatorStardate()
    indicator.main()