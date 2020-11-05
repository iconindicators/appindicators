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


# Application indicator which displays the current Star Trek™ stardate.


INDICATOR_NAME = "indicator-stardate"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "GLib", "2.0" )
gi.require_version( "Gtk", "3.0" )

from gi.repository import GLib, Gtk

import datetime, indicatorbase, stardate


class IndicatorStardate( indicatorbase.IndicatorBase ):

    CONFIG_PAD_INTEGER = "padInteger"
    CONFIG_SHOW_CLASSIC = "showClassic"
    CONFIG_SHOW_ISSUE = "showIssue"


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.40",
            copyrightStartYear = "2012",
            comments = _( "Shows the current Star Trek™ stardate." ),
            creditz = [ _( "STARDATES IN STAR TREK FAQ by Andrew Main. http://www.faqs.org/faqs/star-trek/stardates" ),
                        _( "Wikipedia::Stardate" "https://en.wikipedia.org/wiki/Stardate" ) ] )

        self.requestMouseWheelScrollEvents()
        self.saveConfigTimerID = None


    def update( self, menu ):
        now = datetime.datetime.utcnow()
        if self.showClassic:
            stardateIssue, stardateInteger, stardateFraction = stardate.getStardateClassic( now )
            numberOfSecondsToNextUpdate = stardate.getNextUpdateInSeconds( now, True )

        else:
            stardateIssue = None
            stardateInteger, stardateFraction = stardate.getStardate2009Revised( now )
            numberOfSecondsToNextUpdate = stardate.getNextUpdateInSeconds( now, False )

        self.indicator.set_label( stardate.toStardateString( stardateIssue, stardateInteger, stardateFraction, self.showIssue, self.padInteger ), "" )
        self.indicator.set_title( stardate.toStardateString( stardateIssue, stardateInteger, stardateFraction, self.showIssue, self.padInteger ) ) # Needed for Lubuntu/Xubuntu.
        return numberOfSecondsToNextUpdate


    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        # Based on the mouse wheel scroll event (irrespective of direction),
        # cycle through the possible combinations of options for display in the stardate.
        # If showing a 'classic' stardate and padding is not required, ignore the padding option.
        if self.showClassic:
            stardateIssue, stardateInteger, stardateFraction = stardate.getStardateClassic( datetime.datetime.utcnow() )
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

        self.requestUpdate()

        if self.saveConfigTimerID:
            GLib.source_remove( self.saveConfigTimerID )

        # Defer the save; this avoids multiple saves when scrolling the mouse wheel like crazy!
        self.saveConfigTimerID = self.requestSaveConfig( 10 )


    def onPreferences( self, dialog ):
        grid = self.createGrid()

        showClassicCheckbox = Gtk.CheckButton.new_with_label( _( "Show stardate 'classic'" ) )
        showClassicCheckbox.set_active( self.showClassic )
        showClassicCheckbox.set_tooltip_text( _(
            "If checked, show stardate 'classic' based on\n\n" + \
            "\tSTARDATES IN STAR TREK FAQ by Andrew Main.\n\n" + \
            "Otherwise show stardate '2009 revised' based on\n\n" + \
            "\thttps://en.wikipedia.org/wiki/Stardate" ) )
        grid.attach( showClassicCheckbox, 0, 0, 1, 1 )

        showIssueCheckbox = Gtk.CheckButton.new_with_label( _( "Show ISSUE" ) )
        showIssueCheckbox.set_active( self.showIssue )
        showIssueCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        showIssueCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        showIssueCheckbox.set_tooltip_text( _( "Show the ISSUE of the stardate 'classic'." ) )
        grid.attach( showIssueCheckbox, 0, 1, 1, 1 )

        padIntegerCheckbox = Gtk.CheckButton.new_with_label( _( "Pad INTEGER" ) )
        padIntegerCheckbox.set_active( self.padInteger )
        padIntegerCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        padIntegerCheckbox.set_margin_left( self.INDENT_WIDGET_LEFT )
        padIntegerCheckbox.set_tooltip_text( _( "Pad the INTEGER part of the stardate 'classic' with leading zeros." ) )
        grid.attach( padIntegerCheckbox, 0, 2, 1, 1 )

        showClassicCheckbox.connect( "toggled", self.onShowClassicCheckbox, showIssueCheckbox, padIntegerCheckbox )

        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.padInteger = padIntegerCheckbox.get_active()
            self.showClassic = showClassicCheckbox.get_active()
            self.showIssue = showIssueCheckbox.get_active()

        return responseType


    def onShowClassicCheckbox( self, source, showIssueCheckbox, padIntegerCheckbox ):
        padIntegerCheckbox.set_sensitive( source.get_active() )
        showIssueCheckbox.set_sensitive( source.get_active() )


    def loadConfig( self, config ):
        self.padInteger = config.get( IndicatorStardate.CONFIG_PAD_INTEGER, True )
        self.showClassic = config.get( IndicatorStardate.CONFIG_SHOW_CLASSIC, True )
        self.showIssue = config.get( IndicatorStardate.CONFIG_SHOW_ISSUE, True )


    def saveConfig( self ):
        self.saveConfigTimerID = None # Reset the timer ID.

        return {
            IndicatorStardate.CONFIG_PAD_INTEGER: self.padInteger,
            IndicatorStardate.CONFIG_SHOW_CLASSIC: self.showClassic,
            IndicatorStardate.CONFIG_SHOW_ISSUE: self.showIssue
        }


IndicatorStardate().main()