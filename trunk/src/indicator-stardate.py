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


from gi.repository import AppIndicator3, GLib, Gtk

import datetime, gzip, json, logging, os, pythonutils, re, shutil, stardate, sys


class IndicatorStardate:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-stardate"
    VERSION = "1.0.25"
    ICON = NAME
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    COMMENTS = "Shows the current Star Trek™ stardate."
    CREDITS = [ "Based on STARDATES IN STAR TREK FAQ V1.6 by Andrew Main." ]

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
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

        self.indicator = AppIndicator3.Indicator.new( IndicatorStardate.NAME, IndicatorStardate.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.set_menu( self.buildMenu() )


    def buildMenu( self ):
        menu = Gtk.Menu()

        if self.showInMenu:
            image = Gtk.Image()
            image.set_from_icon_name( IndicatorStardate.ICON, Gtk.IconSize.MENU )
            self.stardateMenuItem = Gtk.ImageMenuItem()
            self.stardateMenuItem.set_image( image )
            menu.append( self.stardateMenuItem )
            menu.append( Gtk.SeparatorMenuItem() )

        preferencesMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        menu.append( preferencesMenuItem )

        aboutMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        aboutMenuItem.connect( "activate", self.onAbout )
        menu.append( aboutMenuItem )

        quitMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        quitMenuItem.connect( "activate", Gtk.main_quit )
        menu.append( quitMenuItem )

        menu.show_all()
        return menu


    def main( self ):
        self.stardate = stardate.Stardate()
        self.update()

        # Use the stardate update period to set a refresh timer.
        # The stardate calculation and WHEN the stardate changes are not synchronised,
        # so update at ten times speed (but no less than once per second).
        period = int( self.stardate.getStardateFractionalPeriod() / 10 ) 
        if period < 1: period = 1

        GLib.timeout_add_seconds( period, self.update )
        Gtk.main()


    def update( self ):
        self.stardate.setClassic( self.showClassic )
        self.stardate.setGregorian( datetime.datetime.utcnow() )
        s = self.stardate.toStardateString( self.showIssue, self.padInteger )
        self.indicator.set_label( s, "" )
        if self.showInMenu: self.stardateMenuItem.set_label( "Stardate: " + s )

        return True # Needed so the timer continues!


    def onAbout( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.dialog = pythonutils.AboutDialog( 
               IndicatorStardate.NAME,
               IndicatorStardate.COMMENTS, 
               IndicatorStardate.WEBSITE, 
               IndicatorStardate.WEBSITE, 
               IndicatorStardate.VERSION, 
               Gtk.License.GPL_3_0, 
               IndicatorStardate.ICON,
               [ IndicatorStardate.AUTHOR ],
               IndicatorStardate.CREDITS,
               "Credits",
               "/usr/share/doc/" + IndicatorStardate.NAME + "/changelog.Debian.gz",
               logging )

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

        showClassicCheckbox = Gtk.CheckButton( "Use 'classic' conversion" )
        showClassicCheckbox.set_active( self.showClassic )
        showClassicCheckbox.set_tooltip_text( "Stardate 'classic' is based on\n\tSTARDATES IN STAR TREK FAQ V1.6\nby Andrew Main.\n\nOtherwise the 2009 revised conversion is used\n(http://en.wikipedia.org/wiki/Stardate)." )
        grid.attach( showClassicCheckbox, 0, 0, 2, 1 )

        showIssueCheckbox = Gtk.CheckButton( "Show ISSUE" )
        showIssueCheckbox.set_active( self.showIssue )
        showIssueCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        showIssueCheckbox.set_margin_left( 15 )
        showIssueCheckbox.set_tooltip_text( "Show the ISSUE of the stardate\n(only applies to 'classic')" )
        grid.attach( showIssueCheckbox, 0, 1, 1, 1 )

        padIntegerCheckbox = Gtk.CheckButton( "Pad INTEGER" )
        padIntegerCheckbox.set_active( self.padInteger )
        padIntegerCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        padIntegerCheckbox.set_margin_left( 15 )
        padIntegerCheckbox.set_tooltip_text( "Pad the INTEGER part with leading zeroes\n(only applies to 'classic')" )
        grid.attach( padIntegerCheckbox, 0, 2, 1, 1 )

        showClassicCheckbox.connect( "toggled", self.onShowClassicCheckbox, showIssueCheckbox, padIntegerCheckbox )

        showInMenuCheckbox = Gtk.CheckButton( "Show in menu" )
        showInMenuCheckbox.set_active( self.showInMenu )
        showInMenuCheckbox.set_tooltip_text( "Show the stardate in the menu\n\n(for desktop environments which prohibit\ntext labels adjacent to the icon)" )
        showInMenuCheckbox.set_margin_top( 10 )
        grid.attach( showInMenuCheckbox, 0, 3, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorStardate.AUTOSTART_PATH + IndicatorStardate.DESKTOP_FILE ) )
        autostartCheckbox.set_tooltip_text( "Run the indicator automatically" )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 4, 2, 1 )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
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
                with open( IndicatorStardate.SETTINGS_FILE, "r" ) as f: settings = json.load( f )

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
            with open( IndicatorStardate.SETTINGS_FILE, "w" ) as f: f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorStardate.SETTINGS_FILE )


if __name__ == "__main__": IndicatorStardate().main()