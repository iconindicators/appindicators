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


# Application indicator which converts domain names between Unicode and ASCII.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import encodings.idna
import gi

gi.require_version( "Gdk", "3.0" )
from gi.repository import Gdk

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

try:
    gi.require_version( "Notify", "0.7" )
except ValueError:
    gi.require_version( "Notify", "0.8" )
from gi.repository import Notify

import re


class IndicatorPunycode( IndicatorBase ):

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
            activate_functionandarguments = ( lambda menuItem: self.on_convert(), ),
            is_secondary_activate_target = True )

        indent = self.get_menu_indent()
        for result in self.results:
            menu.append( Gtk.SeparatorMenuItem() )

            self.create_and_append_menuitem(
                menu,
                indent + _( "Unicode:  " ) + result[ IndicatorPunycode.RESULTS_UNICODE ],
                activate_functionandarguments =
                    ( lambda menuItem, result = result:
                        self.send_results_to_output( result[ IndicatorPunycode.RESULTS_UNICODE ] ), ) ) # Note result = result to handle lambda late binding.

            self.create_and_append_menuitem(
                menu,
                indent + _( "ASCII:  " ) + result[ IndicatorPunycode.RESULTS_ASCII ],
                activate_functionandarguments =
                    ( lambda menuItem, result = result:
                        self.send_results_to_output( result[ IndicatorPunycode.RESULTS_ASCII ] ), ) ) # Note result = result to handle lambda late binding.


    def on_convert( self ):
        summary =_( "Nothing to convert..." )
        if self.input_clipboard:
            text = Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).wait_for_text()
            if text is None:
                Notify.Notification.new( summary, _( "No text is in the clipboard." ), self.get_icon_name() ).show()

            else:
                self.__do_conversion( text )

        else:
            # https://lazka.github.io/pgi-docs/#Gtk-3.0/classes/Clipboard.html#Gtk.Clipboard.request_text
            def clipboard_text_received_function( clipboard, text, data ):
                if text is None:
                    Notify.Notification.new( summary, _( "No text is highlighted/selected." ), self.get_icon_name() ).show()

                else:
                    self.__do_conversion( text )

            Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).request_text( clipboard_text_received_function, None )


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
            Notify.Notification.new(
                _( "Error converting..." ),
                _( "See log for more details." ),
                self.get_icon_name() ).show()


    def cull_results( self ):
        if len( self.results ) > self.result_history_length:
            self.results = self.results[ : self.result_history_length ]


    def send_results_to_output( self, text ):
        if self.output_both:
            Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( text, -1 )
            Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).set_text( text, -1 )

        else:
            if self.input_clipboard:
                Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( text, -1 )

            else:
                Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).set_text( text, -1 )


    def on_preferences( self, dialog ):
        grid = self.create_grid()

        label = Gtk.Label.new( _( "Input source" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        # input_clipboard_radio = Gtk.RadioButton.new_with_label_from_widget( None, _( "Clipboard" ) )
        # input_clipboard_radio.set_tooltip_text( _( "Input is taken from the clipboard." ) )
        # input_clipboard_radio.set_active( self.input_clipboard )
        # input_clipboard_radio.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( input_clipboard_radio, 0, 1, 1, 1 )
#TODO Check above.
        input_clipboard_radio = \
            self.create_radiobutton(
                None,
                _( "Clipboard" ),
                tooltip_text = _( "Input is taken from the clipboard." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.input_clipboard )

        grid.attach( input_clipboard_radio, 0, 1, 1, 1 )

        # input_primary_radio = Gtk.RadioButton.new_with_label_from_widget( input_clipboard_radio, _( "Primary" ) )
        # input_primary_radio.set_tooltip_text( _( "Input is taken from the currently selected text." ) )
        # input_primary_radio.set_active( not self.input_clipboard )
        # input_primary_radio.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( input_primary_radio, 0, 2, 1, 1 )
#TODO Check above.
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
                    "If checked, the converted text is sent\n" + \
                    "to both the clipboard and primary.\n\n" + \
                    "Otherwise the converted text is sent\n" + \
                    "only to the input source." ),
                margin_top = 10,
                active = self.output_both )
#TODO Make sure this is converted okay
        # output_both_checkbutton = Gtk.CheckButton.new_with_label( _( "Output to clipboard and primary" ) )
        # output_both_checkbutton.set_tooltip_text( _(
        #     "If checked, the converted text is sent\n" + \
        #     "to both the clipboard and primary.\n\n" + \
        #     "Otherwise the converted text is sent\n" + \
        #     "only to the input source." ) )
        # output_both_checkbutton.set_active( self.output_both )
        # output_both_checkbutton.set_margin_top( 10 )
        # grid.attach( output_both_checkbutton, 0, 3, 1, 1 )

        drop_path_query_checkbutton = \
            self.create_checkbutton(
                _( "Drop path/query in output" ),
                tooltip_text = _(
                    "If checked, the output text will not\n" + \
                    "contain any path/query (if present)." ),
                margin_top = 10,
                active = self.drop_path_query )
#TODO Make sure this is converted okay
        # drop_path_query_checkbutton = Gtk.CheckButton.new_with_label( _( "Drop path/query in output" ) )
        # drop_path_query_checkbutton.set_tooltip_text( _(
        #     "If checked, the output text will not\n" + \
        #     "contain any path/query (if present)." ) )
        # drop_path_query_checkbutton.set_active( self.drop_path_query )
        # drop_path_query_checkbutton.set_margin_top( 10 )
        grid.attach( drop_path_query_checkbutton, 0, 4, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Maximum results" ) ), False, False, 0 )

        results_amount_spinner = \
            self.create_spinbutton(
                self.result_history_length,
                0,
                1000,
                tooltip_text = _(
                    "The number of most recent\n" + \
                    "results to show in the menu.\n\n" + \
                    "Selecting a menu item which\n" + \
                    "contains a result will copy\n" + \
                    "the result to the output." ) )

        box.pack_start( results_amount_spinner, False, False, 0 )

        grid.attach( box, 0, 5, 1, 1 )

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
