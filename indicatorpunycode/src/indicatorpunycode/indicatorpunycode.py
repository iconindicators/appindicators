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


#TODO
# 2024-07-21 12:07:37,131 - root - ERROR - label empty or too long
# Traceback (most recent call last):
#   File "/home/bernard/.local/venv_indicatorpunycode/lib/python3.8/site-packages/indicatorpunycode/indicatorpunycode.py", line 129, in __do_conversion
#     labels.append( ( encodings.idna.ToASCII( encodings.idna.nameprep( label ) ) ) )
#   File "/usr/lib/python3.8/encodings/idna.py", line 71, in ToASCII
#     raise UnicodeError("label empty or too long")
# UnicodeError: label empty or too long
# 2024-07-21 12:07:37,148 - root - ERROR - Error converting '    # indicatorppadownloadstatistics
#     #   Top level: menuitems with NO indent or one level of indent needed; OR
#     #              submenus with NO indent needed.
#     #   Within submenus
#     #       Under GNOME, need one level of indent for menuitems.
#     #       Under Kubuntu, need NO indent for menuitems with submenus; one level of indent with no submenus.
#     # 
# '.
#
#
#
# I selected some text and clicked convert and got an OSD message and the above log message.
# But the preference for the input was clipboard...so maybe need to guard against an empty clipboard.



#TODO Amend the changelog.md and/or readme.md
# to mention the clipboard only works under X11?


#TODO On Debian 12, when selecting text and either middle mouse click or select convert
# (from primary, not clipboard), get a message "no text is highlight/selected".
# HOwever this seems intermittent...seemed to get it to work once...
# maybe switching from primary to clipboard and back again via the preferences.


# Application indicator which converts domain names between Unicode and ASCII.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import encodings.idna
import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

import re


class IndicatorPunycode( IndicatorBase ):
    # Unused within the indicator; used by build_wheel.py when building the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Punycode" )

    CONFIG_DROP_PATH_QUERY = "dropPathQuery"
    CONFIG_INPUT_CLIPBOARD = "inputClipboard"
    CONFIG_OUTPUT_BOTH = "outputBoth"
    CONFIG_RESULT_HISTORY_LENGTH = "resultHistoryLength"

    # Results are stored in two element sublists.
    RESULTS_UNICODE = 0
    RESULTS_ASCII = 1


    def __init__( self ):
        super().__init__(
            comments = _( "Converts domain names between Unicode and ASCII." ),
            artwork = [ "Oleg Moiseichuk" ] )

        self.results =  [ ] # List of lists, each sublist contains [ unicode, ascii ].


    def update( self, menu ):
        self.create_and_append_menuitem(
            menu,
            _( "Convert" ),
            activate_functionandarguments = ( lambda menuitem: self.on_convert(), ),
            is_secondary_activate_target = True )

        indent = self.get_menu_indent()
        for result in self.results:
            menu.append( Gtk.SeparatorMenuItem() )

            self.create_and_append_menuitem(
                menu,
                indent + _( "Unicode:  " ) + result[ IndicatorPunycode.RESULTS_UNICODE ],
                activate_functionandarguments = (
                    lambda menuitem, result = result: # Need result = result to handle lambda late binding.
                        self.send_results_to_output( result[ IndicatorPunycode.RESULTS_UNICODE ] ), ) )

            self.create_and_append_menuitem(
                menu,
                indent + _( "ASCII:  " ) + result[ IndicatorPunycode.RESULTS_ASCII ],
                activate_functionandarguments = (
                    lambda menuitem, result = result:
                        self.send_results_to_output( result[ IndicatorPunycode.RESULTS_ASCII ] ), ) )


    def on_convert( self ):
        summary =_( "Nothing to convert..." )
        if self.input_clipboard:
            text = self.copy_from_selection_clipboard()
            if text is None:
                self.show_notification( summary, _( "No text is in the clipboard." ) )

            else:
                self.__do_conversion( text )

        else:
            # https://lazka.github.io/pgi-docs/#Gtk-3.0/classes/Clipboard.html#Gtk.Clipboard.request_text
            def clipboard_text_received_function( clipboard, text, data ):
                if text is None:
                    self.show_notification( summary, _( "No text is highlighted/selected." ) )

                else:
                    self.__do_conversion( text )

            self.copy_from_selection_primary( ( clipboard_text_received_function, None ) )


    def __do_conversion( self, text ):
        protocol = ""
        result = re.split( r"(^.*//)", text )
        if len( result ) == 3:
            protocol = result[ 1 ]
            text = result[ 2 ]

        path_query = ""
        result = re.split( r"(/.*$)", text )
        if len( result ) == 3:
            text = result[ 0 ]
            if not self.drop_path_query:
                path_query = result[ 1 ]

        try:
            converted_text = ""
            if text.find( "xn--" ) == -1:
                labels = [ ]
                for label in text.split( "." ):
                    labels.append( ( encodings.idna.ToASCII( encodings.idna.nameprep( label ) ) ) )

                converted_text = str( b'.'.join( labels ), "utf-8" )
                result = [ protocol + text + path_query, protocol + converted_text + path_query ]

            else:
                for label in text.split( "." ):
                    converted_text += encodings.idna.ToUnicode( encodings.idna.nameprep( label ) ) + "."

                converted_text = converted_text[ : -1 ]
                result = [ protocol + converted_text + path_query, protocol + text + path_query ]

            if result in self.results:
                self.results.remove( result )

            self.results.insert( 0, result )

            self.cull_results()

            self.send_results_to_output( protocol + converted_text + path_query )
            self.request_update()

        except Exception as e:
            self.get_logging().exception( e )
            self.get_logging().error( "Error converting '" + protocol + text + path_query + "'." )
            self.show_notification( _( "Error converting..." ), _( "See log for more details." ) )


    def cull_results( self ):
        if len( self.results ) > self.result_history_length:
            self.results = self.results[ : self.result_history_length ]


    def send_results_to_output( self, text ):
        if self.output_both:
            self.copy_to_selection( text )
            self.copy_to_selection( text, is_primary = True )

        else:
            if self.input_clipboard:
                self.copy_to_selection( text )

            else:
                self.copy_to_selection( text, is_primary = True )


    def on_preferences( self, dialog ):
        grid = self.create_grid()

        grid.attach(
            self.create_box( ( ( Gtk.Label.new( _( "Input source" ) ), False ), ) ),
            0, 0, 1, 1 )

        input_clipboard_radio = \
            self.create_radiobutton(
                None,
                _( "Clipboard" ),
                tooltip_text = _(
                    "Input is taken from the clipboard.\n\n" +
                    "Only works under X11." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.input_clipboard )

        grid.attach( input_clipboard_radio, 0, 1, 1, 1 )

        input_primary_radio = \
            self.create_radiobutton(
                input_clipboard_radio,
                _( "Primary" ),
                tooltip_text = _( "Input is taken from the currently selected text." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = not self.input_clipboard )

        grid.attach( input_primary_radio, 0, 2, 1, 1 )

        output_both_checkbutton = \
            self.create_checkbutton(
                _( "Output to clipboard and primary" ),
                tooltip_text = _(
                    "If checked, the converted text is sent\n" +
                    "to both the clipboard and primary.\n\n" +
                    "Otherwise the converted text is sent\n" +
                    "only to the input source.\n\n" +
                    "Sending the output to the clipboard\n" +
                    "only works under X11." ),
                margin_top = 10,
                active = self.output_both )

        grid.attach( output_both_checkbutton, 0, 3, 1, 1 )

        drop_path_query_checkbutton = \
            self.create_checkbutton(
                _( "Drop path/query in output" ),
                tooltip_text = _(
                    "If checked, the output text will not\n" +
                    "contain any path/query (if present)." ),
                margin_top = 10,
                active = self.drop_path_query )

        grid.attach( drop_path_query_checkbutton, 0, 4, 1, 1 )

        results_amount_spinner = \
            self.create_spinbutton(
                self.result_history_length,
                0,
                1000,
                tooltip_text = _(
                    "The number of most recent\n" +
                    "results to show in the menu.\n\n" +
                    "Selecting a menu item which\n" +
                    "contains a result will copy\n" +
                    "the result to the output." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Maximum results" ) ), False ),
                    ( results_amount_spinner, False ) ),
                margin_top = 10 ),
            0, 5, 1, 1 )

        autostart_checkbox, delay_spinner, box = self.create_autostart_checkbox_and_delay_spinner()
        grid.attach( box, 0, 6, 1, 1 )

        dialog.get_content_area().pack_start( grid, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.input_clipboard = input_clipboard_radio.get_active()
            self.output_both = output_both_checkbutton.get_active()
            self.drop_path_query = drop_path_query_checkbutton.get_active()
            self.result_history_length = results_amount_spinner.get_value_as_int()
            self.set_autostart_and_delay( autostart_checkbox.get_active(), delay_spinner.get_value_as_int() )
            self.cull_results()

        return response_type


    def load_config( self, config ):
        self.drop_path_query = config.get( IndicatorPunycode.CONFIG_DROP_PATH_QUERY, False )
        self.input_clipboard = config.get( IndicatorPunycode.CONFIG_INPUT_CLIPBOARD, False )
        self.output_both = config.get( IndicatorPunycode.CONFIG_OUTPUT_BOTH, False )
        self.result_history_length = config.get( IndicatorPunycode.CONFIG_RESULT_HISTORY_LENGTH, 3 )


    def save_config( self ):
        return {
            IndicatorPunycode.CONFIG_DROP_PATH_QUERY : self.drop_path_query,
            IndicatorPunycode.CONFIG_INPUT_CLIPBOARD : self.input_clipboard,
            IndicatorPunycode.CONFIG_OUTPUT_BOTH : self.output_both,
            IndicatorPunycode.CONFIG_RESULT_HISTORY_LENGTH : self.result_history_length
        }


IndicatorPunycode().main()
