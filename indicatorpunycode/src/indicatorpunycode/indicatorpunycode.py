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
import re

gi.require_version( "Gdk", "3.0" )
from gi.repository import Gdk

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

try:
    gi.require_version( "Notify", "0.7" )
except ValueError:
    gi.require_version( "Notify", "0.8" )
from gi.repository import Notify


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
        self.createAndAppendMenuItem(
            menu,
            _( "Convert" ),
            onClickFunction = lambda menuItem: self.onConvert(),
            isSecondaryActivateTarget = True )

        indent = self.getMenuIndent()
        for result in self.results:
            menu.append( Gtk.SeparatorMenuItem() )

            self.createAndAppendMenuItem(
                menu,
                indent + _( "Unicode:  " ) + result[ IndicatorPunycode.RESULTS_UNICODE ],
                onClickFunction = lambda menuItem, result = result: self.sendResultsToOutput( result[ IndicatorPunycode.RESULTS_UNICODE ] ) ) # Note result = result to handle lambda late binding.

            self.createAndAppendMenuItem(
                menu,
                indent + _( "ASCII:  " ) + result[ IndicatorPunycode.RESULTS_ASCII ],
                onClickFunction = lambda menuItem, result = result: self.sendResultsToOutput( result[ IndicatorPunycode.RESULTS_ASCII ] ) ) # Note result = result to handle lambda late binding.


    def onConvert( self ):
        summary =_( "Nothing to convert..." )
        if self.inputClipboard:
            text = Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).wait_for_text()
            if text is None:
                Notify.Notification.new( summary, _( "No text is in the clipboard." ), self.get_icon_name() ).show()

            else:
                self.__doConversion( text )

        else:
            # https://lazka.github.io/pgi-docs/#Gtk-3.0/classes/Clipboard.html#Gtk.Clipboard.request_text
            def clipboardTextReceivedFunc( clipboard, text, data ):
                if text is None:
                    Notify.Notification.new( summary, _( "No text is highlighted/selected." ), self.get_icon_name() ).show()

                else:
                    self.__doConversion( text )

            Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).request_text( clipboardTextReceivedFunc, None )


    def __doConversion( self, text ):
        protocol = ""
        result = re.split( r"(^.*//)", text )
        if len( result ) == 3:
            protocol = result[ 1 ]
            text = result[ 2 ]

        pathQuery = ""
        result = re.split( r"(/.*$)", text )
        if len( result ) == 3:
            text = result[ 0 ]
            if not self.dropPathQuery:
                pathQuery = result[ 1 ]

        try:
            convertedText = ""
            if text.find( "xn--" ) == -1:
                labels = [ ]
                for label in text.split( "." ):
                    labels.append( ( encodings.idna.ToASCII( encodings.idna.nameprep( label ) ) ) )

                convertedText = str( b'.'.join( labels ), "utf-8" )
                result = [ protocol + text + pathQuery, protocol + convertedText + pathQuery ]

            else:
                for label in text.split( "." ):
                    convertedText += encodings.idna.ToUnicode( encodings.idna.nameprep( label ) ) + "."

                convertedText = convertedText[ : -1 ]
                result = [ protocol + convertedText + pathQuery, protocol + text + pathQuery ]

            if result in self.results:
                self.results.remove( result )

            self.results.insert( 0, result )

            self.cullResults()

            self.sendResultsToOutput( protocol + convertedText + pathQuery )
            self.requestUpdate()

        except Exception as e:
            self.getLogging().exception( e )
            self.getLogging().error( "Error converting '" + protocol + text + pathQuery + "'." )
            Notify.Notification.new( _( "Error converting..." ), _( "See log for more details." ), self.get_icon_name() ).show()


    def cullResults( self ):
        if len( self.results ) > self.resultHistoryLength:
            self.results = self.results[ : self.resultHistoryLength ]


    def sendResultsToOutput( self, text ):
        if self.outputBoth:
            Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( text, -1 )
            Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).set_text( text, -1 )

        else:
            if self.inputClipboard:
                Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( text, -1 )

            else:
                Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).set_text( text, -1 )


    def onPreferences( self, dialog ):
        grid = self.create_grid()

        label = Gtk.Label.new( _( "Input source" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        # inputClipboardRadio = Gtk.RadioButton.new_with_label_from_widget( None, _( "Clipboard" ) )
        # inputClipboardRadio.set_tooltip_text( _( "Input is taken from the clipboard." ) )
        # inputClipboardRadio.set_active( self.inputClipboard )
        # inputClipboardRadio.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( inputClipboardRadio, 0, 1, 1, 1 )
#TODO Check above.
        inputClipboardRadio = \
            self.create_radiobutton(
                None,
                _( "Clipboard" ),
                tooltip_text = _( "Input is taken from the clipboard." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.inputClipboard )

        grid.attach( inputClipboardRadio, 0, 1, 1, 1 )

        # inputPrimaryRadio = Gtk.RadioButton.new_with_label_from_widget( inputClipboardRadio, _( "Primary" ) )
        # inputPrimaryRadio.set_tooltip_text( _( "Input is taken from the currently selected text." ) )
        # inputPrimaryRadio.set_active( not self.inputClipboard )
        # inputPrimaryRadio.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        # grid.attach( inputPrimaryRadio, 0, 2, 1, 1 )
#TODO Check above.
        inputPrimaryRadio = \
            self.create_radiobutton(
                inputClipboardRadio,
                _( "Primary" ),
                tooltip_text = _( "Input is taken from the currently selected text." ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = not self.inputClipboard )

        grid.attach( inputPrimaryRadio, 0, 2, 1, 1 )

        outputBothCheckbutton = \
            self.create_checkbutton(
                _( "Output to clipboard and primary" ),
                _( "If checked, the converted text is sent\n" + \
                   "to both the clipboard and primary.\n\n" + \
                   "Otherwise the converted text is sent\n" + \
                   "only to the input source." ),
                margin_top = 10,
                active = self.outputBoth )
#TODO Make sure this is converted okay
        # outputBothCheckbutton = Gtk.CheckButton.new_with_label( _( "Output to clipboard and primary" ) )
        # outputBothCheckbutton.set_tooltip_text( _(
        #     "If checked, the converted text is sent\n" + \
        #     "to both the clipboard and primary.\n\n" + \
        #     "Otherwise the converted text is sent\n" + \
        #     "only to the input source." ) )
        # outputBothCheckbutton.set_active( self.outputBoth )
        # outputBothCheckbutton.set_margin_top( 10 )
        # grid.attach( outputBothCheckbutton, 0, 3, 1, 1 )

        dropPathQueryCheckbutton = \
            self.create_checkbutton(
                _( "Drop path/query in output" ),
                _( "If checked, the output text will not\n" + \
                   "contain any path/query (if present)." ),
                margin_top = 10,
                active = self.dropPathQuery )
#TODO Make sure this is converted okay
        # dropPathQueryCheckbutton = Gtk.CheckButton.new_with_label( _( "Drop path/query in output" ) )
        # dropPathQueryCheckbutton.set_tooltip_text( _(
        #     "If checked, the output text will not\n" + \
        #     "contain any path/query (if present)." ) )
        # dropPathQueryCheckbutton.set_active( self.dropPathQuery )
        # dropPathQueryCheckbutton.set_margin_top( 10 )
        grid.attach( dropPathQueryCheckbutton, 0, 4, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Maximum results" ) ), False, False, 0 )

        resultsAmountSpinner = \
            self.create_spinbutton(
                self.resultHistoryLength,
                0,
                1000,
                tooltip_text = _( "The number of most recent\n" + \
                                  "results to show in the menu.\n\n" + \
                                  "Selecting a menu item which\n" + \
                                  "contains a result will copy\n" + \
                                  "the result to the output." ) )

        box.pack_start( resultsAmountSpinner, False, False, 0 )

        grid.attach( box, 0, 5, 1, 1 )

        autostartCheckbox, delaySpinner, box = self.createAutostartCheckboxAndDelaySpinner()
        grid.attach( box, 0, 6, 1, 1 )

        # dialog.vbox.pack_start( grid, True, True, 0 )#TODO What is vbox?  It is present on all indicators...what is it?
        # I think I can use get_content_area() instead after reading
        # https://lazka.github.io/pgi-docs/Gtk-3.0/classes/Dialog.html#Gtk.Dialog.get_content_area
        # If true, roll out to all vbox calls.
        dialog.get_content_area().pack_start( grid, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.inputClipboard = inputClipboardRadio.get_active()
            self.outputBoth = outputBothCheckbutton.get_active()
            self.dropPathQuery = dropPathQueryCheckbutton.get_active()
            self.resultHistoryLength = resultsAmountSpinner.get_value_as_int()
            self.setAutostartAndDelay( autostartCheckbox.get_active(), delaySpinner.get_value_as_int() )
            self.cullResults()

        return responseType


    def loadConfig( self, config ):
        self.dropPathQuery = config.get( IndicatorPunycode.CONFIG_DROP_PATH_QUERY, False )
        self.inputClipboard = config.get( IndicatorPunycode.CONFIG_INPUT_CLIPBOARD, False )
        self.outputBoth = config.get( IndicatorPunycode.CONFIG_OUTPUT_BOTH, False )
        self.resultHistoryLength = config.get( IndicatorPunycode.CONFIG_RESULT_HISTORY_LENGTH, 3 )


    def saveConfig( self ):
        return {
            IndicatorPunycode.CONFIG_DROP_PATH_QUERY : self.dropPathQuery,
            IndicatorPunycode.CONFIG_INPUT_CLIPBOARD : self.inputClipboard,
            IndicatorPunycode.CONFIG_OUTPUT_BOTH : self.outputBoth,
            IndicatorPunycode.CONFIG_RESULT_HISTORY_LENGTH : self.resultHistoryLength
        }


IndicatorPunycode().main()
