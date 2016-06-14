#!/usr/bin/env python


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


INDICATOR_NAME = "indicator-punycode"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import AppIndicator3, Gdk, Gtk

import os, re


class IndicatorPunyCode:

    AUTHOR = "Bernard Giannetti, Oleg Moiseichuk"
    VERSION = "1.0.0"
    # Place SVG icon into /usr/share/icons/ubuntu-mono-dark/apps/22/ and run 'sudo update-icon-caches /usr/share/icons/ubuntu-mono-dark/'
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".desktop"
    COMMENTS = _( "Converter between International domain names (IDN)\n" + \
                  "and Punycode-encoded domain names in ASCII." )


    def __init__( self ):
        self.dialog = None
        self.clipboard = Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ) # Change to ( Gdk.SELECTION_CLIPBOARD ) to use clipboard buffer instead

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorPunyCode.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.buildMenu( None, None )


    def main( self ): Gtk.main()


    def buildMenu( self, punyASCII, punyUnicode ):
        menu = Gtk.Menu()

        menuItem = Gtk.MenuItem( _( "Convert the selected URL" ) )
        menuItem.connect( "activate", self.onPunycodeTheClipboard )
        menu.append( menuItem )
        self.indicator.set_secondary_activate_target( menuItem )

        if punyASCII is not None and punyUnicode is not None:
            if len( punyASCII ) > 0 and len( punyUnicode ) > 0:
                menu.append( Gtk.SeparatorMenuItem() )
                menuItem = Gtk.MenuItem( _( "ASCII:  " ) + punyASCII )
                menuItem.connect( "activate", self.pasteToClipboard, punyASCII )
                menu.append( menuItem )

                menuItem = Gtk.MenuItem( _( "IDN:     " ) + punyUnicode )
                menuItem.connect( "activate", self.pasteToClipboard, punyUnicode )
                menu.append( menuItem )
            else:
                # Appears if punyASCII, punyUnicode == ""
                menu.append( Gtk.MenuItem( _( "Error converting URL!" ) ) ) #TODO If this item is selected, maybe rebuild the menu passing in None, None to remove this item?

        self.createPreferencesAboutQuitMenuItems( menu, True, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def onPunycodeTheClipboard( self, widget ): self.clipboard.request_text( self.receiveClipboardText, None )


    def receiveClipboardText( self, clipboard, text, data ):
        if text is None or text == "":
            self.buildMenu( _( "no input" ), _( "no input" ) )
        else:
            text = re.sub( r'\s', "", text )
            catchPrefix = re.match( r'.*//', text )
            if catchPrefix is None:
                prefix = ""
            else:
                prefix = catchPrefix.group()

            text = re.sub( r'^.*//', "", text )
            text = re.sub( r'/$', "", text )
            catchValid = re.search( r'[.]', text )
            if catchValid is None:
                self.buildMenu( _( "invalid input" ), _( "invalid input" ) )
            else:
                catchNonASCII = re.search( r'[^a-zA-Z0-9.-]', text )
                catchACE = re.search( r'xn--', text )
                if catchNonASCII is None and catchACE is None:
                    self.buildMenu( _( "pure ASCII input"), _( "pure ASCII input") )
                else:
                    punyASCII, punyUnicode = self.doPunyCode( text )
                    punyASCII = prefix + punyASCII
                    punyUnicode = prefix + punyUnicode
                    self.buildMenu( punyASCII, punyUnicode )


    def doPunyCode( self, text ):
        # http://www.tutorialspoint.com/python/python_reg_expressions.htm
        selector = re.search( r'xn--', text, re.U )
        if selector:
            punyUnicode = text.decode("utf-8").decode("idna")
            punyASCII = text
        else:
            punyUnicode = text
            punyASCII = text.decode("utf-8").encode("idna")
        return punyASCII, punyUnicode


    def pasteToClipboard( self, widget, text ): self.clipboard.set_text( text, -1 )


    def onAbout( self, widget ):
        if self.dialog is None:
            self.dialog = self.createAboutDialog(
                [ IndicatorPunyCode.AUTHOR ],
                IndicatorPunyCode.COMMENTS, 
                Gtk.License.GPL_3_0,
                IndicatorPunyCode.ICON,
                INDICATOR_NAME,
                IndicatorPunyCode.VERSION,
                _( "translator-credits" ) )

            self.dialog.run()
            self.dialog.destroy()
            self.dialog = None
        else:
            self.dialog.present()


    def createPreferencesAboutQuitMenuItems( self, menu, prependSeparator, onAboutHandler, onQuitHandler ):
        if prependSeparator:
            menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        menuItem.connect( "activate", onAboutHandler )
        menu.append( menuItem )

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        menuItem.connect( "activate", onQuitHandler )
        menu.append( menuItem )


    def createAboutDialog( self,
            authors, # List of authors.
            comments, # Comments.
            licenseType, # Any of Gtk.License.*
            logoIconName, # The name of the image icon - without extension.
            programName, # Program name.
            version, # String of the numeric program version.
            translatorCredit ): # The result of calling _( "translator-credits" ) which returns a string or None.

            aboutDialog = Gtk.AboutDialog()

            aboutDialog.set_authors( authors )
            aboutDialog.set_comments( comments )
            aboutDialog.set_license_type( licenseType )
            aboutDialog.set_logo_icon_name( logoIconName )
            aboutDialog.set_program_name( programName )
            aboutDialog.set_version( version )

            if not( translatorCredit is None or translatorCredit == "" ):
                aboutDialog.set_translator_credits( translatorCredit )

            return aboutDialog


if __name__ == "__main__": IndicatorPunyCode().main()
