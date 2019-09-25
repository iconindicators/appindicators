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


INDICATOR_NAME = "indicator-stardate"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import GLib, Gtk

import datetime, indicator_base, stardate
#TODO Should stardate be in a class too?


class IndicatorStardate( indicator_base.IndicatorBase ):

    CONFIG_PAD_INTEGER = "padInteger"
    CONFIG_SHOW_CLASSIC = "showClassic"
    CONFIG_SHOW_ISSUE = "showIssue"


    def __init__( self ):
        super().__init__(
            comments = _( "Shows the current Star Trek™ stardate." ),
            copyrightStartYear = "2012",
            indicatorName = INDICATOR_NAME,
            version = "1.0.38",
            creditz = [ _( "Based on STARDATES IN STAR TREK FAQ V1.6 by Andrew Main." ) ] )

        self.indicator.connect( "scroll-event", self.onMouseWheelScroll )
        self.saveConfigTimerID = None
        self.update()


#TODO Maybe pass in to the init constructor the callback so we don't need to do this...?
    def update( self ): super().update( self.__update )


    def __update( self ):
        super().buildMenu( Gtk.Menu(), False, self.__onPreferences )

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
            numberOfSecondsToNextUpdate = int( ( oneSecondAfterMidnight - now ).total_seconds() )

        self.indicator.set_label( stardate.toStardateString( stardateIssue, stardateInteger, stardateFraction, self.showIssue, self.padInteger ), "" )
        self.updateTimerID = GLib.timeout_add_seconds( numberOfSecondsToNextUpdate, self.update )


    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        with self.lock:
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

            GLib.idle_add( self.update ) #TODO Check this logic and does it interfere with any other update (also check save config in prefs)?

            if self.saveConfigTimerID is not None:
                GLib.source_remove( self.saveConfigTimerID )

            self.saveConfigTimerID = GLib.timeout_add_seconds( 5, self.saveConfig ) # Defer the save to five seconds in the future - no point doing lots of saves when scrolling the mouse wheel like crazy!


    def __onPreferences( self ):
        grid = super().createGrid()

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
        showIssueCheckbox.set_margin_left( super().INDENT_WIDGET_LEFT )
        showIssueCheckbox.set_tooltip_text( _( "Show the ISSUE of the stardate 'classic'." ) )
        grid.attach( showIssueCheckbox, 0, 1, 1, 1 )

        padIntegerCheckbox = Gtk.CheckButton( _( "Pad INTEGER" ) )
        padIntegerCheckbox.set_active( self.padInteger )
        padIntegerCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        padIntegerCheckbox.set_margin_left( super().INDENT_WIDGET_LEFT )
        padIntegerCheckbox.set_tooltip_text( _( "Pad the INTEGER part of the stardate 'classic' with leading zeros." ) )
        grid.attach( padIntegerCheckbox, 0, 2, 1, 1 )

        showClassicCheckbox.connect( "toggled", self.onShowClassicCheckbox, showIssueCheckbox, padIntegerCheckbox )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_active( super().isAutoStart() )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 3, 1, 1 )

        dialog = Gtk.Dialog( _( "Preferences" ), None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
#         dialog.set_icon_name( self.icon ) #TODO Need to set an icon?
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            self.padInteger = padIntegerCheckbox.get_active()
            self.showClassic = showClassicCheckbox.get_active()
            self.showIssue = showIssueCheckbox.get_active()
            self.saveConfig() # A save timer could still be in force, but let it run as the same global values will just be re-saved. #TODO Cancel existing timer?  Think!
            super().setAutoStart( autostartCheckbox.get_active() )

        dialog.destroy()


    def onShowClassicCheckbox( self, source, showIssueCheckbox, padIntegerCheckbox ):
        padIntegerCheckbox.set_sensitive( source.get_active() )
        showIssueCheckbox.set_sensitive( source.get_active() )

    
    def loadConfig( self ):
        config = super().loadConfig()
        self.padInteger = config.get( IndicatorStardate.CONFIG_PAD_INTEGER, True )
        self.showClassic = config.get( IndicatorStardate.CONFIG_SHOW_CLASSIC, True )
        self.showIssue = config.get( IndicatorStardate.CONFIG_SHOW_ISSUE, True )


    def saveConfig( self ):
        self.saveConfigTimerID = None # Reset the timer ID.

        config = {
            IndicatorStardate.CONFIG_PAD_INTEGER: self.padInteger,
            IndicatorStardate.CONFIG_SHOW_CLASSIC: self.showClassic,
            IndicatorStardate.CONFIG_SHOW_ISSUE: self.showIssue
        }

        super().saveConfig( config )


#TODO Sort this out.
# if __name__ == "__main__": IndicatorStardate().main()
IndicatorStardate().main()