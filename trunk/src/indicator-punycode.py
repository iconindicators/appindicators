#!/usr/bin/env python3


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


# Convert domain names between Unicode and ASCII.
# Allows the user to select, by either highlight or clipboard,
# a domain name and convert between Unicode and ASCII.


#TODO Icons.


#TODO POT and RU PO.


INDICATOR_NAME = "indicator-punycode"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import AppIndicator3, Gdk, Gtk, Notify

import encodings.idna, json, logging, os, pythonutils, re


class IndicatorPunycode:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.0"
    ICON = INDICATOR_NAME
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    DESKTOP_FILE = INDICATOR_NAME + ".desktop"

    COMMENTS = _( "Convert domain names between Unicode and ASCII." )
    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_DROP_PATH_QUERY = "dropPathQuery"
    SETTINGS_INPUT_CLIPBOARD = "inputClipboard"
    SETTINGS_OUTPUT_BOTH = "outputBoth"
    SETTINGS_RESULT_HISTORY_LENGTH = "resultHistoryLength"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorPunycode.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )
        self.dialog = None
        self.results =  [ ] # List of lists, each sublist contains [ unicode, ascii ].
        self.loadSettings()
        Notify.init( INDICATOR_NAME )

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorPunycode.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.buildMenu()


    def main( self ): Gtk.main()


    def buildMenu( self ):
        menu = Gtk.Menu()

        menuItem = Gtk.MenuItem( _( "Convert" ) )
        menuItem.connect( "activate", self.onConvert )
        menu.append( menuItem )
        self.indicator.set_secondary_activate_target( menuItem )

        indent = "    "
        for result in self.results:
            menu.append( Gtk.SeparatorMenuItem() )

            menuItem = Gtk.MenuItem( indent + "Unicode:  " + result [ 0 ] )
            menuItem.connect( "activate", self.pasteToClipboard, result[ 0 ] )
            menu.append( menuItem )

            menuItem = Gtk.MenuItem( indent + "ASCII:  " + result [ 1 ] )
            menuItem.connect( "activate", self.pasteToClipboard, result[ 1 ] )
            menu.append( menuItem )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, True, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def onConvert( self, widget ): Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).request_text( self.doConversion, None )


    def doConversion( self, clipboard, text, data ):
        if self.inputClipboard:
            text = Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).wait_for_text()

        if text is None:
            if self.inputClipboard:
                message = _( "No text is in the clipboard." )
            else:
                message = _( "No text is highlighted/selected." )

            Notify.Notification.new( _( "Nothing to convert..." ), message, IndicatorPunycode.ICON ).show()
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
                    self.results.insert( 0, [ protocol + text + pathQuery, protocol + convertedText + pathQuery ] )
                else:
                    for label in text.split( "." ):    
                        convertedText += encodings.idna.ToUnicode( encodings.idna.nameprep( label ) ) + "."

                    convertedText = convertedText[ : -1 ]
                    self.results.insert( 0, [ protocol + convertedText + pathQuery, protocol + text + pathQuery ] )

                if len( self.results ) > self.resultHistoryLength:
                    self.results = self.results[ : self.resultHistoryLength ]

                self.pasteToClipboard( None, protocol + convertedText + pathQuery )
                self.buildMenu()

            except Exception as e:
                logging.exception( e )
                logging.error( "Error converting '" + protocol + text + pathQuery + "'." )
                Notify.Notification.new( _( "Error converting..." ), _( "See log for more details." ), IndicatorPunycode.ICON ).show()


    def pasteToClipboard( self, widget, text ):
        if self.outputBoth:
            Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( text, -1 )
            Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).set_text( text, -1 )
        else:
            if self.inputClipboard:
               Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( text, -1 )
            else:
                Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).set_text( text, -1 )


    def onAbout( self, widget ):
        if self.dialog is None:
            self.dialog = pythonutils.createAboutDialog(
                [ IndicatorPunycode.AUTHOR ],
                IndicatorPunycode.COMMENTS, 
                [ ],
                "",
                Gtk.License.GPL_3_0,
                IndicatorPunycode.ICON,
                INDICATOR_NAME,
                IndicatorPunycode.WEBSITE,
                IndicatorPunycode.VERSION,
                _( "translator-credits" ),
                _( "View the" ),
                _( "text file." ),
                _( "changelog" ) )

            self.dialog.run()
            self.dialog.destroy()
            self.dialog = None
        else:
            self.dialog.present()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        notebook = Gtk.Notebook()

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )
        grid.set_row_homogeneous( False )
        grid.set_column_homogeneous( False )

        label = Gtk.Label( _( "Input source" ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 0, 2, 1 )

        inputClipboardRadio = Gtk.RadioButton.new_with_label_from_widget( None, _( "Clipboard" ) )
        inputClipboardRadio.set_tooltip_text( _(
            "Input is taken from the clipboard\n" + \
            "after a CTRL-X or CTRL-C (or eqivalent)." ) )
        inputClipboardRadio.set_active( self.inputClipboard )
        inputClipboardRadio.set_margin_left( 15 )
        grid.attach( inputClipboardRadio, 0, 1, 2, 1 )

        inputPrimaryRadio = Gtk.RadioButton.new_with_label_from_widget( inputClipboardRadio, _( "Primary" ) )
        inputPrimaryRadio.set_tooltip_text( _(
            "Input is taken from the\n" + \
            "currently highlighted/selected\n" + \
            "text after the user performs\n" + \
            "a middle mouse click." ) )
        inputPrimaryRadio.set_active( not self.inputClipboard )
        inputPrimaryRadio.set_margin_left( 15 )
        grid.attach( inputPrimaryRadio, 0, 2, 2, 1 )

        outputBothCheckbox = Gtk.CheckButton( _( "Output to clipboard and primary" ) )
        outputBothCheckbox.set_tooltip_text( _(
            "If checked, the output text is sent\n" + \
            "to both the clipboard and primary.\n\n" + \
            "Otherwise the output is sent back\n" + \
            "only to the input source." ) )
        outputBothCheckbox.set_active( self.outputBoth )
        outputBothCheckbox.set_margin_top( 10 )
        grid.attach( outputBothCheckbox, 0, 3, 2, 1 )

        dropPathQueryCheckbox = Gtk.CheckButton( _( "Drop path/query in output" ) )
        dropPathQueryCheckbox.set_tooltip_text( _(
            "If checked, the output text will\n" + \
            "not contain any path/query (if present)." ) )
        dropPathQueryCheckbox.set_active( self.dropPathQuery )
        dropPathQueryCheckbox.set_margin_top( 10 )
        grid.attach( dropPathQueryCheckbox, 0, 4, 2, 1 )

        label = Gtk.Label( _( "Maximum results" ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 5, 1, 1 )

        resultsAmountSpinner = Gtk.SpinButton()
        resultsAmountSpinner.set_adjustment( Gtk.Adjustment( self.resultHistoryLength, 0, 1000, 1, 1, 0 ) )
        resultsAmountSpinner.set_value( self.resultHistoryLength )
        resultsAmountSpinner.set_tooltip_text( _(
            "The number of most recent\n" + \
            "results to show in the menu.\n\n" + \
            "Selecting a menu item which\n" + \
            "contains a result will copy\n" + \
            "the result to the output." ) )
        resultsAmountSpinner.set_margin_top( 10 )
        grid.attach( resultsAmountSpinner, 1, 5, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorPunycode.DESKTOP_FILE ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 6, 2, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        self.dialog = Gtk.Dialog( _( "Preferences" ), None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorPunycode.ICON )
        self.dialog.show_all()

        if self.dialog.run() == Gtk.ResponseType.OK:
            self.inputClipboard = inputClipboardRadio.get_active()
            self.outputBoth = outputBothCheckbox.get_active()
            self.dropPathQuery = dropPathQueryCheckbox.get_active()
            self.resultHistoryLength = resultsAmountSpinner.get_value_as_int()
            self.saveSettings()
            pythonutils.setAutoStart( IndicatorPunycode.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            self.buildMenu()

        self.dialog.destroy()
        self.dialog = None


    def loadSettings( self ):
        self.dropPathQuery = False
        self.inputClipboard = False
        self.outputBoth = False
        self.resultHistoryLength = 3
        if os.path.isfile( IndicatorPunycode.SETTINGS_FILE ):
            try:
                with open( IndicatorPunycode.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.dropPathQuery = settings.get( IndicatorPunycode.SETTINGS_DROP_PATH_QUERY, self.dropPathQuery )
                self.inputClipboard = settings.get( IndicatorPunycode.SETTINGS_INPUT_CLIPBOARD, self.inputClipboard )
                self.outputBoth = settings.get( IndicatorPunycode.SETTINGS_OUTPUT_BOTH, self.outputBoth )
                self.resultHistoryLength = settings.get( IndicatorPunycode.SETTINGS_RESULT_HISTORY_LENGTH, self.resultHistoryLength )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorPunycode.SETTINGS_FILE )
        else:
            pass


    def saveSettings( self ):
        try:
            settings = {
                IndicatorPunycode.SETTINGS_DROP_PATH_QUERY: self.dropPathQuery,
                IndicatorPunycode.SETTINGS_INPUT_CLIPBOARD: self.inputClipboard,
                IndicatorPunycode.SETTINGS_OUTPUT_BOTH: self.outputBoth,
                IndicatorPunycode.SETTINGS_RESULT_HISTORY_LENGTH: self.resultHistoryLength
            }

            with open( IndicatorPunycode.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorPunycode.SETTINGS_FILE )


if __name__ == "__main__": IndicatorPunycode().main()