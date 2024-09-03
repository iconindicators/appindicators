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


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import datetime
import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

import stardate


class IndicatorStardate( IndicatorBase ):
    # Unused within the indicator; used by build_wheel.py when building the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Stardate" )
    indicator_categories = "Categories=Utility;Amusement"

    CONFIG_PAD_INTEGER = "padInteger"
    CONFIG_SHOW_CLASSIC = "showClassic"
    CONFIG_SHOW_ISSUE = "showIssue"


    def __init__( self ):
        super().__init__(
            comments = _( "Shows the current Star Trek™ stardate." ),
            creditz = [
                _( "STARDATES IN STAR TREK FAQ by Andrew Main. http://www.faqs.org/faqs/star-trek/stardates" ),
                _( "Wikipedia::Stardate" "https://en.wikipedia.org/wiki/Stardate" ) ] )

        self.request_mouse_wheel_scroll_events( ( self.on_mouse_wheel_scroll, ) )
        self.save_config_timer_id = None


    def update( self, menu ):
        utc_now = datetime.datetime.now( datetime.timezone.utc )
        if self.show_classic:
            stardate_issue, stardate_integer, stardate_fraction = \
                stardate.get_stardate_classic( utc_now )

            number_of_seconds_to_next_update = \
                stardate.get_next_update_in_seconds( utc_now, True )

        else:
            stardate_issue = None
            stardate_integer, stardate_fraction = \
                stardate.get_stardate_2009_revised( utc_now )

            number_of_seconds_to_next_update = \
                stardate.get_next_update_in_seconds( utc_now, False )

        stardate_string = \
            stardate.to_stardate_string(
                stardate_issue,
                stardate_integer,
                stardate_fraction,
                self.show_issue,
                self.pad_integer )

        if not self.set_label_or_tooltip( stardate_string ):
            menu.append( Gtk.MenuItem.new_with_label( stardate_string ) )
            menu.append( Gtk.SeparatorMenuItem() )

        return number_of_seconds_to_next_update


    def on_mouse_wheel_scroll( self, indicator, delta, scroll_direction ):
        # Cycle through all combinations of options for display of the stardate.
        # If showing a 'classic' stardate and padding is not required, ignore the padding option.
        if self.show_classic:
            stardate_issue, stardate_integer, stardate_fraction = \
                stardate.get_stardate_classic( datetime.datetime.now( datetime.timezone.utc ) )

            padding_required = \
                stardate.requires_padding( stardate_issue, stardate_integer )

            if padding_required:
                if self.show_issue and self.pad_integer:
                    self.show_issue = True
                    self.pad_integer = False

                elif self.show_issue and not self.pad_integer:
                    self.show_issue = False
                    self.pad_integer = True

                elif not self.show_issue and self.pad_integer:
                    self.show_issue = False
                    self.pad_integer = False

                else:
                    self.show_issue = True
                    self.pad_integer = True
                    self.show_classic = False # Shown all possible 'classic' options (when padding is required)...now move on to '2009 revised'.

            else:
                if self.show_issue:
                    self.show_issue = False

                else:
                    self.show_issue = True
                    self.show_classic = False # Shown all possible 'classic' options (when padding is not required)...now move on to '2009 revised'.

        else:
            self.show_issue = True
            self.pad_integer = True
            self.show_classic = True # Have shown the '2009 revised' version, now move on to 'classic'.

        self.request_update( delay = 0 )

        # Defer the save; avoids multiple saves when scrolling the mouse wheel like crazy!
        self.request_save_config( delay = 10 )


    def on_preferences( self, dialog ):
        grid = self.create_grid()

        show_classic_checkbutton = \
            self.create_checkbutton(
                _( "Show stardate 'classic'" ),
                tooltip_text = _(
                    "If checked, show stardate 'classic' based on\n\n" +
                    "\tSTARDATES IN STAR TREK FAQ by Andrew Main.\n\n" +
                    "Otherwise, show stardate '2009 revised' based on\n\n" +
                    "\thttps://en.wikipedia.org/wiki/Stardate" ),
                active = self.show_classic )

        grid.attach( show_classic_checkbutton, 0, 0, 1, 1 )

        show_issue_checkbutton = \
            self.create_checkbutton(
                _( "Show ISSUE" ),
                tooltip_text = _( "Show the ISSUE of the stardate 'classic'." ),
                sensitive = show_classic_checkbutton.get_active(),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.show_issue )

        grid.attach( show_issue_checkbutton, 0, 1, 1, 1 )

        pad_integer_checkbutton = \
            self.create_checkbutton(
                _( "Pad INTEGER" ),
                tooltip_text = _( "Pad the INTEGER part of the stardate 'classic' with leading zeros." ),
                sensitive = show_classic_checkbutton.get_active(),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.pad_integer )

        grid.attach( pad_integer_checkbutton, 0, 2, 1, 1 )

        show_classic_checkbutton.connect(
            "toggled",
            self.on_radio_or_checkbox,
            True,
            show_issue_checkbutton,
            pad_integer_checkbutton )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = \
            self.create_preferences_common_widgets()

        grid.attach( box, 0, 3, 1, 1 )

        dialog.get_content_area().pack_start( grid, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.pad_integer = pad_integer_checkbutton.get_active()
            self.show_classic = show_classic_checkbutton.get_active()
            self.show_issue = show_issue_checkbutton.get_active()

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


    def load_config( self, config ):
        self.pad_integer = config.get( IndicatorStardate.CONFIG_PAD_INTEGER, True )
        self.show_classic = config.get( IndicatorStardate.CONFIG_SHOW_CLASSIC, True )
        self.show_issue = config.get( IndicatorStardate.CONFIG_SHOW_ISSUE, True )


    def save_config( self ):
        self.save_config_timer_id = None # Reset the timer ID.

        return {
            IndicatorStardate.CONFIG_PAD_INTEGER : self.pad_integer,
            IndicatorStardate.CONFIG_SHOW_CLASSIC : self.show_classic,
            IndicatorStardate.CONFIG_SHOW_ISSUE : self.show_issue
        }


IndicatorStardate().main()
