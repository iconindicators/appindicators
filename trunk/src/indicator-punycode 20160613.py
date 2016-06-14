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


#TODO Update description... want a single short line plus additional lines for more detail.
# Application indicator allowing a user to convert text (typically a UNICODE
# domain name) from the clipboard and convert to/from ASCII (Punycode ) and
# vice versa.


#TODO Update .desktop file comment.


#TODO Update control file description.
# If OSD is used, check what the python OSD depends should be.


#TODO Prior to converting, removing any leading protocol and following trailing slash first,
# then convert, then add back what was removed.
# See email and original code for RE.


#TODO Check emails for clipboard stuff...


INDICATOR_NAME = "indicator-punycode"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import AppIndicator3, Gdk, Gtk

import encodings.idna, json, logging, os, pythonutils


class IndicatorPunycode:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.0"
    ICON = INDICATOR_NAME
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    DESKTOP_FILE = INDICATOR_NAME + ".desktop"

    COMMENTS = _( "Convert between International domain names and Punycode." )
    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_BUFFER_CLIPBOARD = "bufferClipboard"
    SETTINGS_BUFFER_PRIMARY = "bufferPrimary"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorPunycode.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )
        self.dialog = None
        self.results =  [ ] # List of lists, each sublist contains [ unicode, punycode ].
        self.loadSettings()

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

        for result in self.results:
            menu.append( Gtk.SeparatorMenuItem() )

            menuItem = Gtk.MenuItem( "    " + result [ 0 ] )
            menuItem.connect( "activate", self.onPasteToClipboard, result[ 0 ] )
            menu.append( menuItem )

            menuItem = Gtk.MenuItem( "    " + result [ 1 ] )
            menuItem.connect( "activate", self.onPasteToClipboard, result[ 1 ] )
            menu.append( menuItem )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, True, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


#TODO Testing...
# www.Alliancefrançaise.nu
# www.xn--alliancefranaise-npb.nu

# www.xn--bcher-kva.de
# www.bücher.de

    def onConvert( self, widget ): Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).request_text( self.doConversion, None )


    def doConversion( self, clipboard, text, data ):
        print( "Middle mouse click:", text )

        if text is None or len ( text ) == 0:
            text = Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).wait_for_text()
            print( "Clipboard:", text )

        if text is None or len ( text ) == 0:
            print( "TODO: Notify user and log something meaningful." )
        else:
#TODO Check what exceptions are thrown and catch and log/notify.        
            convertedText = ""
            if text.find( "xn--" ) == -1:
                labels = [ ]
                for label in text.split( "." ):    
                    labels.append( ( encodings.idna.ToASCII( encodings.idna.nameprep( label ) ) ) )
                convertedText = str( b'.'.join( labels ), "utf-8" )
                self.results.append( [ text, convertedText ] )
            else:
                for label in text.split( "." ):    
                    convertedText += encodings.idna.ToUnicode( encodings.idna.nameprep( label ) ) + "."

                convertedText = convertedText[ : -1 ]
                self.results.insert( 0, [ convertedText, text ] )

            print( text, convertedText )

            if len( self.results ) > 5: #TODO Make '5' a user preference?
                self.results[ : 5 ]

            self.onPasteToClipboard( None, convertedText )

        self.buildMenu()


    def onPasteToClipboard( self, widget, text ):
        Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).set_text( text, -1 )
#        Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( text, -1 )


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

        # General settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )
        grid.set_row_homogeneous( False )
        grid.set_column_homogeneous( False )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorPunycode.DESKTOP_FILE ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 0, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        self.dialog = Gtk.Dialog( _( "Preferences" ), None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorPunycode.ICON )
        self.dialog.show_all()

        if self.dialog.run() == Gtk.ResponseType.OK:
            with self.lock:
                self.saveSettings()
                pythonutils.setAutoStart( IndicatorPunycode.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
                self.buildMenu()

        self.dialog.destroy()
        self.dialog = None


    def loadSettings( self ):
        if True: return
        self.scripts = [ ]
        self.showScriptDescriptionsAsSubmenus = False
        if os.path.isfile( IndicatorPunycode.SETTINGS_FILE ):
            try:
                with open( IndicatorPunycode.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                scripts = settings.get( IndicatorPunycode.SETTINGS_SCRIPTS, [ ] )
                self.showScriptDescriptionsAsSubmenus = settings.get( IndicatorPunycode.SETTINGS_SHOW_SCRIPT_DESCRIPTIONS_AS_SUBMENUS, self.showScriptDescriptionsAsSubmenus )
                for script in scripts:
                    self.scripts.append( Info( script[ 0 ], script[ 1 ], script[ 2 ], script[ 3 ], bool( script[ 4 ] ) ) )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorPunycode.SETTINGS_FILE )
        else:
            pass


    def saveSettings( self ):
        try:
            scripts = [ ]
            for script in self.scripts:
                scripts.append( [ script.getName(), script.getDescription(), script.getDirectory(), script.getCommand(), script.isTerminalOpen() ] )

            settings = {
                IndicatorPunycode.SETTINGS_SCRIPTS: scripts,
                IndicatorPunycode.SETTINGS_SHOW_SCRIPT_DESCRIPTIONS_AS_SUBMENUS: self.showScriptDescriptionsAsSubmenus
            }

            with open( IndicatorPunycode.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorPunycode.SETTINGS_FILE )


if __name__ == "__main__": IndicatorPunycode().main()
