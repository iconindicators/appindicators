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


# Application indicator which displays the current Star Trek™ stardate.


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  https://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/api/AppIndicator3_0.1/classes/Indicator.html
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-14.04


INDICATOR_NAME = "indicator-stardate"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import AppIndicator3, GLib, Gtk

import datetime, gzip, json, logging, os, pythonutils, re, shutil, stardate, sys


class IndicatorStardate:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.28"
    ICON = INDICATOR_NAME
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    DESKTOP_FILE = INDICATOR_NAME + ".desktop"

    COMMENTS = _( "Shows the current Star Trek™ stardate." )
    CREDITS = [ _( "Based on STARDATES IN STAR TREK FAQ V1.6 by Andrew Main." ) ]

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_PAD_INTEGER = "padInteger"
    SETTINGS_SHOW_CLASSIC = "showClassic"
    SETTINGS_SHOW_ISSUE = "showIssue"
    SETTINGS_SHOW_IN_MENU = "showInMenu"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorStardate.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )

        self.dialog = None
        self.stardateMenuItem = None
        self.loadSettings()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorStardate.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.set_menu( self.buildMenu() )

        self.stardate = stardate.Stardate()
        self.update()

        # Use the stardate update period to set a refresh timer.
        # The stardate calculation and WHEN the stardate changes are not synchronised,
        # so update at ten times speed (but no less than once per second).
        period = int( self.stardate.getStardateFractionalPeriod() / 10 ) 
        if period < 1:
            period = 1

        GLib.timeout_add_seconds( period, self.update )


    def buildMenu( self ):
        menu = Gtk.Menu()

        if self.showInMenu:
            image = Gtk.Image()
            image.set_from_icon_name( IndicatorStardate.ICON, Gtk.IconSize.MENU )
            self.stardateMenuItem = Gtk.ImageMenuItem()
            self.stardateMenuItem.set_image( image )
            menu.append( self.stardateMenuItem )
            menu.append( Gtk.SeparatorMenuItem() )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, False, self.onPreferences, self.onAbout, Gtk.main_quit )
        menu.show_all()
        return menu


    def main( self ): Gtk.main()


    def update( self ):
        self.stardate.setClassic( self.showClassic )
        self.stardate.setGregorian( datetime.datetime.utcnow() )
        s = self.stardate.toStardateString( self.showIssue, self.padInteger )
        self.indicator.set_label( s, "" )
        if self.showInMenu:
            self.stardateMenuItem.set_label( _( "Stardate: {0}" ).format( s ) )

        return True # Needed so the timer continues!


    def onAbout( self, widget ):
        if self.dialog is None:
            self.dialog = pythonutils.createAboutDialog(
                [ IndicatorStardate.AUTHOR ],
                IndicatorStardate.COMMENTS, 
                IndicatorStardate.CREDITS,
                _( "Credits" ),
                Gtk.License.GPL_3_0,
                IndicatorStardate.ICON,
                INDICATOR_NAME,
                IndicatorStardate.WEBSITE,
                IndicatorStardate.VERSION,
                ( "translator-credits" ),
                _( "View the" ),
                _( "text file." ),
                _( "changelog" ) )

            self.dialog.run()
            self.dialog.destroy()
            self.dialog = None
        else:
            self.dialog.present()


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

        showClassicCheckbox = Gtk.CheckButton( _( "Use 'classic' conversion" ) )
        showClassicCheckbox.set_active( self.showClassic )
        showClassicCheckbox.set_tooltip_text( _(
            "Stardate 'classic' is based on\n\n" + \
            "\tSTARDATES IN STAR TREK FAQ V1.6\n\n" + \
            "by Andrew Main.\n\n" + \
            "Otherwise the 2009 revision is used\n" + \
            "(http://en.wikipedia.org/wiki/Stardate)." ) )
        grid.attach( showClassicCheckbox, 0, 0, 2, 1 )

        showIssueCheckbox = Gtk.CheckButton( _( "Show ISSUE" ) )
        showIssueCheckbox.set_active( self.showIssue )
        showIssueCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        showIssueCheckbox.set_margin_left( 15 )
        showIssueCheckbox.set_tooltip_text( _(
            "Show the ISSUE of the stardate\n" + \
            "(only applies to 'classic')." ) )
        grid.attach( showIssueCheckbox, 0, 1, 1, 1 )

        padIntegerCheckbox = Gtk.CheckButton( _( "Pad INTEGER" ) )
        padIntegerCheckbox.set_active( self.padInteger )
        padIntegerCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        padIntegerCheckbox.set_margin_left( 15 )
        padIntegerCheckbox.set_tooltip_text( _(
            "Pad the INTEGER part with leading\n" + \
            "zeros (only applies to 'classic')." ) )
        grid.attach( padIntegerCheckbox, 0, 2, 1, 1 )

        showClassicCheckbox.connect( "toggled", self.onShowClassicCheckbox, showIssueCheckbox, padIntegerCheckbox )

        showInMenuCheckbox = Gtk.CheckButton( _( "Show in menu" ) )
        showInMenuCheckbox.set_active( self.showInMenu )
        showInMenuCheckbox.set_tooltip_text( _(
            "Show the stardate in the menu.\n\n" + \
            "Useful for desktop environments\n" + \
            "which prohibit text labels adjacent\n" + \
            "to the icon." ) )
        showInMenuCheckbox.set_margin_top( 10 )
        grid.attach( showInMenuCheckbox, 0, 3, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorStardate.DESKTOP_FILE ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 4, 2, 1 )

        self.dialog = Gtk.Dialog( _( "Preferences" ), None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( grid, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorStardate.ICON )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.padInteger = padIntegerCheckbox.get_active()
            self.showClassic = showClassicCheckbox.get_active()
            self.showInMenu = showInMenuCheckbox.get_active()
            self.showIssue = showIssueCheckbox.get_active()
            self.saveSettings()
            pythonutils.setAutoStart( IndicatorStardate.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            self.indicator.set_menu( self.buildMenu() )
            self.update()

        self.dialog.destroy()
        self.dialog = None


    def onShowClassicCheckbox( self, source, showIssueCheckbox, padIntegerCheckbox ):
        padIntegerCheckbox.set_sensitive( source.get_active() )
        showIssueCheckbox.set_sensitive( source.get_active() )


    def loadSettings( self ):
        self.padInteger = True
        self.showClassic = True
        self.showInMenu = False
        self.showIssue = True

        if os.path.isfile( IndicatorStardate.SETTINGS_FILE ):
            try:
                with open( IndicatorStardate.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.padInteger = settings.get( IndicatorStardate.SETTINGS_PAD_INTEGER, self.padInteger )
                self.showClassic = settings.get( IndicatorStardate.SETTINGS_SHOW_CLASSIC, self.showClassic )
                self.showInMenu = settings.get( IndicatorStardate.SETTINGS_SHOW_IN_MENU, self.showInMenu )
                self.showIssue = settings.get( IndicatorStardate.SETTINGS_SHOW_ISSUE, self.showIssue )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorStardate.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorStardate.SETTINGS_PAD_INTEGER: self.padInteger,
                IndicatorStardate.SETTINGS_SHOW_CLASSIC: self.showClassic,
                IndicatorStardate.SETTINGS_SHOW_IN_MENU: self.showInMenu,
                IndicatorStardate.SETTINGS_SHOW_ISSUE: self.showIssue
            }
            with open( IndicatorStardate.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorStardate.SETTINGS_FILE )


if __name__ == "__main__": IndicatorStardate().main()