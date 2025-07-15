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


#TODO Test on wayland.


'''
Application indicator which converts domain names between Unicode and ASCII.
'''


import encodings.idna
import re

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from .indicatorbase import IndicatorBase

from .unicodeasciipair import UnicodeAsciiPair


class IndicatorPunycode( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used in the About dialog and the .desktop file.
    INDICATOR_NAME_HUMAN_READABLE = _( "Indicator Punycode" )

    # Used in the .desktop file.
    INDICATOR_CATEGORIES = "Categories=Utility"

    CONFIG_DROP_PATH_QUERY = "dropPathQuery"
    CONFIG_INPUT_CLIPBOARD = "inputClipboard"
    CONFIG_OUTPUT_BOTH = "outputBoth"
    CONFIG_RESULT_HISTORY_LENGTH = "resultHistoryLength"


    def __init__( self ):
        super().__init__(
            IndicatorPunycode.INDICATOR_NAME_HUMAN_READABLE,
            comments = _( "Converts domain names between Unicode and ASCII." ),
            artwork = [ "Oleg Moiseichuk" ] )

        self.unicode_ascii_pairs =  [ ]


    def update(
        self,
        menu ):
        '''
        Refresh the indicator.
        '''
        if self.is_clipboard_supported():
            self.create_and_append_menuitem(
                menu,
                _( "Convert" ),
                activate_functionandarguments = (
                    lambda menuitem: self._on_convert(), ),
                is_secondary_activate_target = True )

            for pairs in self.unicode_ascii_pairs:
                menu.append( Gtk.SeparatorMenuItem() )

                self.create_and_append_menuitem(
                    menu,
                    _( "Unicode:  " ) + pairs.get_unicode(),
                    activate_functionandarguments = (
                        lambda menuitem, text = pairs.get_unicode():
                            self._send_to_output( text ), ),
                    indent = ( 1, 1 ) )

                self.create_and_append_menuitem(
                    menu,
                    _( "ASCII:  " ) + pairs.get_ascii(),
                    activate_functionandarguments = (
                        lambda menuitem, text = pairs.get_ascii():
                            self._send_to_output( text ), ),
                    indent = ( 1, 1 ) )

        else:
            message = _( "Clipboard is unsupported for your session type." )
            self.create_and_append_menuitem( menu, message )
            summary = _(
                "{0} is inoperative..." ).format(
                    IndicatorPunycode.INDICATOR_NAME_HUMAN_READABLE )

            self.show_notification( summary, message )


    def _on_convert( self ):
        summary =_( "Nothing to convert..." )
        if self.input_clipboard:
            text = self.copy_from_clipboard()
            if text is None:
                self.show_notification(
                    summary, _( "No text is in the clipboard." ) )

            else:
                self._do_conversion( text )

        else:
            def primary_received_callback_function( text ):
                if text is None:
                    self.show_notification(
                        summary, _( "No text is highlighted/selected." ) )

                else:
                    self._do_conversion( text )

            self. copy_from_primary(
                primary_received_callback_function )


    def _do_conversion(
        self,
        text ):

        protocol, path_query, text_to_convert = (
            self._get_protocol_path_query_text_to_convert( text ) )

        if text_to_convert.find( "xn--" ) == -1:
            unicode_ascii_pair, output, exception = (
                self._to_ascii( protocol, path_query, text_to_convert ) )

        else:
            unicode_ascii_pair, output, exception = (
                self._to_unicode( protocol, path_query, text_to_convert ) )

        if exception:
            self.show_notification(
                _( "Unable to convert..." ), str( exception ) )

            self.get_logging().exception( exception )
            self.get_logging().error(
                f"UnicodeError - error converting:\n{ text }" )

        else:
            if unicode_ascii_pair in self.unicode_ascii_pairs:
                self.unicode_ascii_pairs.remove( unicode_ascii_pair )

            self.unicode_ascii_pairs.insert( 0, unicode_ascii_pair )
            self._cull_results()
            self._send_to_output( output )
            self.request_update()


    def _get_protocol_path_query_text_to_convert(
        self,
        text ):

        text_to_convert = text
        protocol = ""
        path_query = ""
        result = re.split( r"(^.*//)", text_to_convert )
        if len( result ) == 3:
            # Text is a URL.
            protocol = result[ 1 ]
            text_to_convert = result[ 2 ]
            result = re.split( r"(/.*$)", text_to_convert )
            if len( result ) == 3:
                # URL has a path (which may or may contain a query string).
                text_to_convert = result[ 0 ]
                if not self.drop_path_query:
                    path_query = result[ 1 ]

            else:
                result = re.split( r"\?", text_to_convert )
                if len( result ) == 2:
                # URL contains a query string but no path.
                    text_to_convert = result[ 0 ]
                    if not self.drop_path_query:
                        path_query = '?' + result[ 1 ]

        return protocol, path_query, text_to_convert


    def _to_ascii(
        self,
        protocol,
        path_query,
        text ):

        exception = None
        try:
            parts = [ ]
            for part in text.split( "." ):
                parts.append( (
                    encodings.idna.ToASCII(
                        encodings.idna.nameprep( part ) ) ) )

            unicode_ascii_pair = (
                UnicodeAsciiPair(
                    protocol + text + path_query,
                    protocol + str( b'.'.join( parts ), "utf-8" ) + path_query ) )

            output = unicode_ascii_pair.get_ascii()

        except UnicodeError as e:
            exception = e

        return unicode_ascii_pair, output, exception


    def _to_unicode(
        self,
        protocol,
        path_query,
        text ):

        exception = None
        try:
            parts = [ ]
            for part in text.split( "." ):
                parts.append( (
                    encodings.idna.ToUnicode(
                        encodings.idna.nameprep( part ) ) ) )

            unicode_ascii_pair = (
                UnicodeAsciiPair(
                    protocol + '.'.join( parts ) + path_query,
                    protocol + text + path_query ) )

            output = unicode_ascii_pair.get_unicode()

        except UnicodeError as e:
            exception = e

        return unicode_ascii_pair, output, exception


    def _cull_results( self ):
        if len( self.unicode_ascii_pairs ) > self.result_history_length:
            self.unicode_ascii_pairs = self.unicode_ascii_pairs[ : self.result_history_length ]


    def _send_to_output(
        self,
        text ):

        if self.output_both:
            self.copy_to_clipboard_or_primary( text )
            self.copy_to_clipboard_or_primary( text, is_primary = True )

        elif self.input_clipboard:
            self.copy_to_clipboard_or_primary( text )

        else:
            self.copy_to_clipboard_or_primary( text, is_primary = True )


    def on_preferences(
        self,
        dialog ):
        '''
        Display preferences.
        '''
        grid = self.create_grid()

        row = 0
        if self.is_clipboard_supported():
            grid.attach(
                self.create_box(
                    ( ( Gtk.Label.new( _( "Input source" ) ), False ), ) ),
                0, row, 1, 1 )

            row += 1

        input_clipboard_radio = (
            self.create_radiobutton(
                None,
                _( "Clipboard" ),
                tooltip_text = _(
                    "Input is taken from the clipboard." ),
                margin_left = self.INDENT_WIDGET_LEFT,
                active = self.input_clipboard ) )

        if self.is_clipboard_supported():
            grid.attach( input_clipboard_radio, 0, row, 1, 1 )
            row += 1

        input_primary_radio = (
            self.create_radiobutton(
                input_clipboard_radio,
                _( "Primary" ),
                tooltip_text = _(
                    "Input is taken from the currently selected text." ),
                margin_left = self.INDENT_WIDGET_LEFT,
                active = not self.input_clipboard ) )

        if self.is_clipboard_supported():
            grid.attach( input_primary_radio, 0, row, 1, 1 )
            row += 1

        output_both_checkbutton = (
            self.create_checkbutton(
                _( "Output to clipboard and primary" ),
                tooltip_text = _(
                    "If checked, the converted text is sent\n"
                    "to both the clipboard and primary.\n\n"
                    "Otherwise the converted text is sent\n"
                    "only to the input source." ),
                margin_top = self.INDENT_WIDGET_TOP,
                active = self.output_both ) )

        if self.is_clipboard_supported():
            grid.attach( output_both_checkbutton, 0, row, 1, 1 )
            row += 1

        drop_path_query_checkbutton = (
            self.create_checkbutton(
                _( "Drop path/query in output" ),
                tooltip_text = _(
                    "If checked, the output text will not\n"
                    "contain any path/query (if present)." ),
                margin_top = self.INDENT_WIDGET_TOP,
                active = self.drop_path_query ) )

        if self.is_clipboard_supported():
            grid.attach( drop_path_query_checkbutton, 0, row, 1, 1 )
            row += 1

        results_amount_spinner = (
            self.create_spinbutton(
                self.result_history_length,
                0,
                1000,
                tooltip_text = _(
                    "The number of most recent\n"
                    "results to show in the menu.\n\n"
                    "Selecting a menu item which\n"
                    "contains a result will copy\n"
                    "the result to the output." ) ) )

        if self.is_clipboard_supported():
            grid.attach(
                self.create_box(
                    (
                        ( Gtk.Label.new( _( "Maximum results" ) ), False ),
                        ( results_amount_spinner, False ) ),
                    margin_top = self.INDENT_WIDGET_TOP ),
                0, row, 1, 1 )

            row += 1

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = (
            self.create_preferences_common_widgets() )

        grid.attach( box, 0, row, 1, 1 )

        dialog.get_content_area().pack_start( grid, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.input_clipboard = input_clipboard_radio.get_active()
            self.output_both = output_both_checkbutton.get_active()
            self.drop_path_query = drop_path_query_checkbutton.get_active()
            self.result_history_length = (
                results_amount_spinner.get_value_as_int() )

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

            self._cull_results()

        return response_type


    def load_config(
        self,
        config ):
        '''
        Load configuration.
        '''
        self.drop_path_query = (
            config.get( IndicatorPunycode.CONFIG_DROP_PATH_QUERY, False ) )

        self.input_clipboard = (
            config.get( IndicatorPunycode.CONFIG_INPUT_CLIPBOARD, False ) )

        self.output_both = (
            config.get( IndicatorPunycode.CONFIG_OUTPUT_BOTH, False ) )

        self.result_history_length = (
            config.get( IndicatorPunycode.CONFIG_RESULT_HISTORY_LENGTH, 3 ) )


    def save_config( self ):
        '''
        Save configuration.
        '''
        return {
            IndicatorPunycode.CONFIG_DROP_PATH_QUERY:
                self.drop_path_query,

            IndicatorPunycode.CONFIG_INPUT_CLIPBOARD:
                self.input_clipboard,

            IndicatorPunycode.CONFIG_OUTPUT_BOTH:
                self.output_both,

            IndicatorPunycode.CONFIG_RESULT_HISTORY_LENGTH:
                self.result_history_length
        }


IndicatorPunycode().main()
