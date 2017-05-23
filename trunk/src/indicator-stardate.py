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
#  http://developer.gnome.org/gnome-devel-demos
#  http://python-gtk-3-tutorial.readthedocs.org
#  http://wiki.gnome.org/Projects/PyGObject/Threading
#  http://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/AppIndicator3-0.1
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html


INDICATOR_NAME = "indicator-stardate"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )

from gi.repository import AppIndicator3, GLib, Gtk
import datetime, json, logging, os, pythonutils, stardate, threading


class IndicatorStardate:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.34"
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"
    COMMENTS = _( "Shows the current Star Trek™ stardate." )
    CREDITS = [ _( "Based on STARDATES IN STAR TREK FAQ V1.6 by Andrew Main." ) ]

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_PAD_INTEGER = "padInteger"
    SETTINGS_SHOW_CLASSIC = "showClassic"
    SETTINGS_SHOW_ISSUE = "showIssue"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorStardate.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )
        self.dialogLock = threading.Lock()
        self.saveSettingsTimerID = None

        self.loadSettings()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorStardate.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.connect( "scroll-event", self.onMouseWheelScroll )

        self.buildMenu()
        self.update( True )


    def main( self ): Gtk.main()


    def buildMenu( self ):
        menu = Gtk.Menu()
        pythonutils.createPreferencesAboutQuitMenuItems( menu, False, self.onPreferences, self.onAbout, Gtk.main_quit )
        menu.show_all()
        self.indicator.set_menu( menu )


    def update( self, scheduled ):
        with threading.Lock():
            if not scheduled:
                GLib.source_remove( self.updateTimerID )

            # Calculate the current stardate and determine when next to update the stardate based on the stardate fractional period.
            if self.showClassic:
                stardateIssue, stardateInteger, stardateFraction, fractionalPeriod = stardate.getStardateClassic( datetime.datetime.utcnow() )

                # WHEN the stardate calculation is performed is NOT necessarily synchronised with WHEN the stardate actually changes.
                # Therefore update at a faster rate, say at one tenth of the period, but at most once per minute.
                numberOfSecondsToNextUpdate = int( fractionalPeriod / 10 )
                if numberOfSecondsToNextUpdate < 60:
                    numberOfSecondsToNextUpdate = 60

            else:
                stardateIssue = None
                stardateInteger, stardateFraction, fractionalPeriod = stardate.getStardate2009Revised( datetime.datetime.utcnow() )

                # For '2009 revised' the rollover only happens at midnight...so use that for the timer!        
                now = datetime.datetime.utcnow()
                oneSecondAfterMidnight = ( now + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 0, second = 1 )
                numberOfSecondsToNextUpdate = ( oneSecondAfterMidnight - now ).total_seconds()

            self.indicator.set_label( stardate.toStardateString( stardateIssue, stardateInteger, stardateFraction, self.showIssue, self.padInteger ), "" )
            self.updateTimerID = GLib.timeout_add_seconds( numberOfSecondsToNextUpdate, self.update, True )


    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        with threading.Lock():
            # Based on the mouse wheel scroll event (irrespective of direction),
            # cycle through the possible combinations of options for display in the stardate.
            # If showing a 'classic' stardate and padding is not require, ignore the padding option.
            if self.showClassic:
                stardateIssue, stardateInteger, stardateFraction, fractionalPeriod = stardate.getStardateClassic( datetime.datetime.utcnow() )
                paddingRequired = stardate.requiresPadding( stardateIssue, stardateInteger )
                if paddingRequired:
                    if self.showIssue and self.padInteger:
                        self.showIssue = True
                        self.padInteger = False

                    elif self.showIssue and not self.padInteger:
                        self.showIssue = False
                        self.padInteger = True

                    elif not self.showIssue and self.padInteger:
                        self.showIssue = False
                        self.padInteger = False

                    else:
                        self.showIssue = True
                        self.padInteger = True
                        self.showClassic = False # Shown all possible 'classic' options (when padding is required)...now move on to '2009 revised'.

                else:
                    if self.showIssue:
                        self.showIssue = False

                    else:
                        self.showIssue = True
                        self.showClassic = False # Shown all possible 'classic' options (when padding is not required)...now move on to '2009 revised'.

            else:
                self.showIssue = True
                self.padInteger = True
                self.showClassic = True # Have shown the '2009 revised' version, now move on to 'classic'.

            GLib.idle_add( self.update, False )

            if self.saveSettingsTimerID is not None:
                GLib.source_remove( self.saveSettingsTimerID )

            self.saveSettingsTimerID = GLib.timeout_add_seconds( 5, self.saveSettings ) # Defer the save to five seconds in the future - no point doing lots of saves when scrolling the mouse wheel like crazy!


    def onAbout( self, widget ):
        if self.dialogLock.acquire( blocking = False ):
            pythonutils.showAboutDialog(
                [ IndicatorStardate.AUTHOR ],
                IndicatorStardate.COMMENTS, 
                IndicatorStardate.CREDITS,
                _( "Credits" ),
                Gtk.License.GPL_3_0,
                IndicatorStardate.ICON,
                INDICATOR_NAME,
                IndicatorStardate.WEBSITE,
                IndicatorStardate.VERSION,
                _( "translator-credits" ),
                _( "View the" ),
                _( "text file." ),
                _( "changelog" ) )

            self.dialogLock.release()


    def onPreferences( self, widget ):
        if self.dialogLock.acquire( blocking = False ):
            self._onPreferences( widget )
            self.dialogLock.release()


    def _onPreferences( self, widget ):
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showClassicCheckbox = Gtk.CheckButton( _( "Show stardate 'classic'" ) )
        showClassicCheckbox.set_active( self.showClassic )
        showClassicCheckbox.set_tooltip_text( _(
            "If checked, show stardate 'classic' based on\n\n" + \
            "\tSTARDATES IN STAR TREK FAQ V1.6\n\n" + \
            "by Andrew Main.\n\n" + \
            "Otherwise show stardate '2009 revised' based on\n\n" + \
            "\thttp://en.wikipedia.org/wiki/Stardate" ) )
        grid.attach( showClassicCheckbox, 0, 0, 1, 1 )

        showIssueCheckbox = Gtk.CheckButton( _( "Show ISSUE" ) )
        showIssueCheckbox.set_active( self.showIssue )
        showIssueCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        showIssueCheckbox.set_margin_left( 15 )
        showIssueCheckbox.set_tooltip_text( _( "Show the ISSUE of the stardate 'classic'." ) )
        grid.attach( showIssueCheckbox, 0, 1, 1, 1 )

        padIntegerCheckbox = Gtk.CheckButton( _( "Pad INTEGER" ) )
        padIntegerCheckbox.set_active( self.padInteger )
        padIntegerCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        padIntegerCheckbox.set_margin_left( 15 )
        padIntegerCheckbox.set_tooltip_text( _( "Pad the INTEGER part of the stardate 'classic' with leading zeros." ) )
        grid.attach( padIntegerCheckbox, 0, 2, 1, 1 )

        showClassicCheckbox.connect( "toggled", self.onShowClassicCheckbox, showIssueCheckbox, padIntegerCheckbox )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorStardate.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 3, 1, 1 )

        dialog = Gtk.Dialog( _( "Preferences" ), None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorStardate.ICON )
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            self.padInteger = padIntegerCheckbox.get_active()
            self.showClassic = showClassicCheckbox.get_active()
            self.showIssue = showIssueCheckbox.get_active()
            self.saveSettings() # A save timer could still be in force, but let it run as the same global values will just be re-saved.
            pythonutils.setAutoStart( IndicatorStardate.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            GLib.idle_add( self.update, False )

        dialog.destroy()


    def onShowClassicCheckbox( self, source, showIssueCheckbox, padIntegerCheckbox ):
        padIntegerCheckbox.set_sensitive( source.get_active() )
        showIssueCheckbox.set_sensitive( source.get_active() )


    def loadSettings( self ):
        self.padInteger = True
        self.showClassic = True
        self.showIssue = True

        if os.path.isfile( IndicatorStardate.SETTINGS_FILE ):
            try:
                with open( IndicatorStardate.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.padInteger = settings.get( IndicatorStardate.SETTINGS_PAD_INTEGER, self.padInteger )
                self.showClassic = settings.get( IndicatorStardate.SETTINGS_SHOW_CLASSIC, self.showClassic )
                self.showIssue = settings.get( IndicatorStardate.SETTINGS_SHOW_ISSUE, self.showIssue )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorStardate.SETTINGS_FILE )


    def saveSettings( self ):
        self.saveSettingsTimerID = None # Reset the timer ID.

        settings = {
            IndicatorStardate.SETTINGS_PAD_INTEGER: self.padInteger,
            IndicatorStardate.SETTINGS_SHOW_CLASSIC: self.showClassic,
            IndicatorStardate.SETTINGS_SHOW_ISSUE: self.showIssue
        }

        try:
            with open( IndicatorStardate.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorStardate.SETTINGS_FILE )


if __name__ == "__main__": IndicatorStardate().main()