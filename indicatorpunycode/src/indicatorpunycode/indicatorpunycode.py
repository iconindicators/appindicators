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
#
# Testing on Ubuntu 22.04 / 24.04, Debian 11 / 12 and Fedora 38 / 38 / 40
# reveals the clipboard/primary input and output works on Wayland
# intermittently (at best) and therefore is deemed unsupported.

from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import encodings.idna
import gi
import re

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk


class IndicatorPunycode( IndicatorBase ):
    # Unused within the indicator; used by build_wheel.py when building the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Punycode" )
    indicator_categories = "Categories=Utility"

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


#TODO For Wayland, try wl-clipboard
#   https://github.com/bugaevc/wl-clipboard
# which may at least get the clipboard going.
# Available it seems on all supported distros:
#   https://packages.ubuntu.com/search?suite=focal&searchon=names&keywords=wl-clipboard
#   https://packages.debian.org/search?keywords=wl-clipboard&searchon=names&suite=all&section=all
#   https://packages.fedoraproject.org/pkgs/wl-clipboard/wl-clipboard/
#   https://software.opensuse.org/package/wl-clipboard
#   https://archlinux.org/packages/extra/x86_64/wl-clipboard/


#TODO New...may not be needed now Wayland works.  Maybe only needed for old Budgie 20.04?
        self.create_and_append_menuitem(
            menu,
            _( "Convert via dialog" ),
            activate_functionandarguments = ( lambda menuitem: self.on_convert_via_dialog( menuitem ), ) )

        for result in self.results:
            menu.append( Gtk.SeparatorMenuItem() )

            self.create_and_append_menuitem(
                menu,
                _( "Unicode:  " ) + result[ IndicatorPunycode.RESULTS_UNICODE ],
                activate_functionandarguments = (
                    lambda menuitem, result = result: # Need result = result to handle lambda late binding.
                        self.send_results_to_output( result[ IndicatorPunycode.RESULTS_UNICODE ] ), ),
                indent = ( 1, 1 ) )

            self.create_and_append_menuitem(
                menu,
                _( "ASCII:  " ) + result[ IndicatorPunycode.RESULTS_ASCII ],
                activate_functionandarguments = (
                    lambda menuitem, result = result:
                        self.send_results_to_output( result[ IndicatorPunycode.RESULTS_ASCII ] ), ),
                indent = ( 1, 1 ) )


    def on_convert( self ):
        summary =_( "Nothing to convert..." )
        if self.input_clipboard:
            text = self.copy_from_selection_clipboard()
            if text is None:
                self.show_notification( summary, _( "No text is in the clipboard." ) )

            else:
                self._do_conversion( text )

        else:
            # https://lazka.github.io/pgi-docs/#Gtk-3.0/classes/Clipboard.html#Gtk.Clipboard.request_text
            def clipboard_text_received_function( clipboard, text, data ):
                if text is None:
                    self.show_notification( summary, _( "No text is highlighted/selected." ) )

                else:
                    self._do_conversion( text )

            self.copy_from_selection_primary( ( clipboard_text_received_function, None ) )


#TODO New    May not be needed now Wayland works...only for distros with no response to middle mouse click perhaps?
    def on_convert_via_dialog( self, menuitem ):
        self.set_menu_sensitivity( False )
        self.indicator.set_secondary_activate_target( None )

        dialog = self.create_dialog( menuitem, _( "Convert via dialog" ) )

        grid = self.create_grid()

        original_text_entry = \
            self.create_entry(
                "",
                tooltip_text = _( "TODO" ) )  #TODO Need to let the user know that punycoded text must start with xn--

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Original Text" ) ), False ),
                    ( original_text_entry, False ) ) ),
            0, 0, 1, 1 )

        dialog.get_content_area().pack_start( grid, True, True, 0 )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if original_text_entry.get_text().strip() == "":
                    self.show_dialog_ok( dialog, _( "The text to convert cannot be empty." ) )
                    original_text_entry.grab_focus()
                    continue

                else:
                    self._do_conversion( original_text_entry.get_text().strip() )

            break

        dialog.destroy()
        self.set_menu_sensitivity( True )
        self.indicator.set_secondary_activate_target( self.secondary_activate_target )


    def _do_conversion( self, text ):
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
                    "Input is taken from the clipboard." ),
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
                    "only to the input source." ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP,
                active = self.output_both )

        grid.attach( output_both_checkbutton, 0, 3, 1, 1 )

        drop_path_query_checkbutton = \
            self.create_checkbutton(
                _( "Drop path/query in output" ),
                tooltip_text = _(
                    "If checked, the output text will not\n" +
                    "contain any path/query (if present)." ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP,
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
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, 5, 1, 1 )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = \
            self.create_preferences_common_widgets()

        grid.attach( box, 0, 6, 1, 1 )

        dialog.get_content_area().pack_start( grid, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.input_clipboard = input_clipboard_radio.get_active()
            self.output_both = output_both_checkbutton.get_active()
            self.drop_path_query = drop_path_query_checkbutton.get_active()
            self.result_history_length = results_amount_spinner.get_value_as_int()

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

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
