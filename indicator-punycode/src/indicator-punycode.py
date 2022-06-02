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


# Application indicator to let a user select a domain name,
# by text highlight or clipboard, then convert between Unicode and ASCII.


INDICATOR_NAME = "indicator-punycode"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gdk", "3.0" )
gi.require_version( "GLib", "2.0" )
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gdk, GLib, Gtk, Notify
from indicatorbase import IndicatorBase

import encodings.idna, re


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
            indicatorName = INDICATOR_NAME,
            version = "1.0.12",
            copyrightStartYear = "2016",
            comments = _( "Convert domain names between Unicode and ASCII." ),
            artwork = [ "Oleg Moiseichuk" ] )

        self.results =  [ ] # List of lists, each sublist contains [ unicode, ascii ].


    def update( self, menu ):
        menuItem = Gtk.MenuItem.new_with_label( _( "Convert" ) )
        menu.append( menuItem )
        menuItem.connect( "activate", self.onConvert )
        self.secondaryActivateTarget = menuItem

        indent = "    "
        for result in self.results:
            menu.append( Gtk.SeparatorMenuItem() )

            menuItem = Gtk.MenuItem( indent + _( "Unicode:  " ) + result[ IndicatorPunycode.RESULTS_UNICODE ] )
            menuItem.connect( "activate", self.pasteToClipboard, result[ IndicatorPunycode.RESULTS_UNICODE ] )
            menu.append( menuItem )

            menuItem = Gtk.MenuItem( indent + _( "ASCII:  " ) + result[ IndicatorPunycode.RESULTS_ASCII ] )
            menuItem.connect( "activate", self.pasteToClipboard, result[ IndicatorPunycode.RESULTS_ASCII ] )
            menu.append( menuItem )


    def onConvert( self, menuItem ): Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).request_text( self.doConversion, None )


    def doConversion( self, clipboard, text, data ):
        if self.inputClipboard:
            text = Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).wait_for_text()

        if text is None:
            if self.inputClipboard:
                message = _( "No text is in the clipboard." )

            else:
                message = _( "No text is highlighted/selected." )

            Notify.Notification.new( _( "Nothing to convert..." ), message, self.icon ).show()

        else:
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

                if len( self.results ) > self.resultHistoryLength:
                    self.results = self.results[ : self.resultHistoryLength ]

                GLib.idle_add( self.pasteToClipboard, None, protocol + convertedText + pathQuery )
                self.requestUpdate()

            except Exception as e:
                self.getLogging().exception( e )
                self.getLogging().error( "Error converting '" + protocol + text + pathQuery + "'." )
                Notify.Notification.new( _( "Error converting..." ), _( "See log for more details." ), self.icon ).show()


    def pasteToClipboard( self, menuItem, text ):
        if self.outputBoth:
            Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( text, -1 )
            Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).set_text( text, -1 )

        else:
            if self.inputClipboard:
                Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( text, -1 )

            else:
                Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).set_text( text, -1 )


    def onPreferences( self, dialog ):
        grid = self.createGrid()

        label = Gtk.Label.new( _( "Input source" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        inputClipboardRadio = Gtk.RadioButton.new_with_label_from_widget( None, _( "Clipboard" ) )
        inputClipboardRadio.set_tooltip_text( _(
            "Input is taken from the clipboard after\n" + \
            "a CTRL-X or CTRL-C (or equivalent)." ) )
        inputClipboardRadio.set_active( self.inputClipboard )
        inputClipboardRadio.set_margin_left( self.INDENT_WIDGET_LEFT )
        grid.attach( inputClipboardRadio, 0, 1, 1, 1 )

        inputPrimaryRadio = Gtk.RadioButton.new_with_label_from_widget( inputClipboardRadio, _( "Primary" ) )
        inputPrimaryRadio.set_tooltip_text( _(
            "Input is taken from the currently\n" + \
            "selected text after a middle mouse\n" + \
            "click of the indicator icon." ) )
        inputPrimaryRadio.set_active( not self.inputClipboard )
        inputPrimaryRadio.set_margin_left( self.INDENT_WIDGET_LEFT )
        grid.attach( inputPrimaryRadio, 0, 2, 1, 1 )

        outputBothCheckbutton = Gtk.CheckButton.new_with_label( _( "Output to clipboard and primary" ) )
        outputBothCheckbutton.set_tooltip_text( _(
            "If checked, the output text is sent\n" + \
            "to both the clipboard and primary.\n\n" + \
            "Otherwise the output is sent back\n" + \
            "only to the input source." ) )
        outputBothCheckbutton.set_active( self.outputBoth )
        outputBothCheckbutton.set_margin_top( 10 )
        grid.attach( outputBothCheckbutton, 0, 3, 1, 1 )

        dropPathQueryCheckbutton = Gtk.CheckButton.new_with_label( _( "Drop path/query in output" ) )
        dropPathQueryCheckbutton.set_tooltip_text( _(
            "If checked, the output text will not\n" + \
            "contain any path/query (if present)." ) )
        dropPathQueryCheckbutton.set_active( self.dropPathQuery )
        dropPathQueryCheckbutton.set_margin_top( 10 )
        grid.attach( dropPathQueryCheckbutton, 0, 4, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Maximum results" ) ), False, False, 0 )

        resultsAmountSpinner = self.createSpinButton(
            self.resultHistoryLength,
            0,
            1000,
            toolTip = _(
                "The number of most recent\n" + \
                "results to show in the menu.\n\n" + \
                "Selecting a menu item which\n" + \
                "contains a result will copy\n" + \
                "the result to the output." ) )

        box.pack_start( resultsAmountSpinner, False, False, 0 )

        grid.attach( box, 0, 5, 1, 1 )

        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.inputClipboard = inputClipboardRadio.get_active()
            self.outputBoth = outputBothCheckbutton.get_active()
            self.dropPathQuery = dropPathQueryCheckbutton.get_active()
            self.resultHistoryLength = resultsAmountSpinner.get_value_as_int()

        return responseType


    def loadConfig( self, config ):
        self.dropPathQuery = config.get( IndicatorPunycode.CONFIG_DROP_PATH_QUERY, False )
        self.inputClipboard = config.get( IndicatorPunycode.CONFIG_INPUT_CLIPBOARD, False )
        self.outputBoth = config.get( IndicatorPunycode.CONFIG_OUTPUT_BOTH, False )
        self.resultHistoryLength = config.get( IndicatorPunycode.CONFIG_RESULT_HISTORY_LENGTH, 3 )


    def saveConfig( self ):
        return {
            IndicatorPunycode.CONFIG_DROP_PATH_QUERY: self.dropPathQuery,
            IndicatorPunycode.CONFIG_INPUT_CLIPBOARD: self.inputClipboard,
            IndicatorPunycode.CONFIG_OUTPUT_BOTH: self.outputBoth,
            IndicatorPunycode.CONFIG_RESULT_HISTORY_LENGTH: self.resultHistoryLength
        }


IndicatorPunycode().main()