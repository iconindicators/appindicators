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


# General utilities.


from gi.repository import Gtk

import gzip, logging.handlers, os, re, shutil, subprocess, sys


def processCall( command ):
    try:
        subprocess.call( command, shell = True )
    except subprocess.CalledProcessError:
        pass


def processGet( command ):
    try:
        return subprocess.check_output( command, shell = True, universal_newlines = True )
    except subprocess.CalledProcessError:
        return None


# Returns True if a number; False otherwise.
def isNumber( numberAsString ):
    try:
        float( numberAsString )
        return True

    except ValueError:
        return False


def isAutoStart( desktopFile, autoStartPath = os.getenv( "HOME" ) + "/.config/autostart/" ): return os.path.exists( autoStartPath + desktopFile )


def setAutoStart( desktopFile, isSet, logging, autoStartPath = os.getenv( "HOME" ) + "/.config/autostart/", desktopPath = "/usr/share/applications/" ):
    if not os.path.exists( autoStartPath ):
        os.makedirs( autoStartPath )

    if isSet:
        try:
            shutil.copy( desktopPath + desktopFile, autoStartPath + desktopFile )
        except Exception as e:
            logging.exception( e )
    else:
        try:
            os.remove( autoStartPath + desktopFile )
        except:
            pass


# Returns the colour (as #xxyyzz) for the current GTK icon theme.
def getColourForIconTheme():
    colour = "#fff200" # Use hicolor as a default
    iconTheme = getIconTheme()
    if iconTheme is not None:
        if iconTheme == "elementary":
            colour = "#f4f4f4"
        elif iconTheme == "lubuntu":
            colour = "#5a5a5a"
        elif iconTheme == "ubuntu-mono-dark":
            colour = "#dfdbd2"
        elif iconTheme == "ubuntu-mono-light":
            colour = "#3c3c3c"

    return colour


# Returns the name of the current GTK icon theme.
def getIconTheme(): return Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )


# Shows a message dialog.
#    messageType: One of Gtk.MessageType.INFO, Gtk.MessageType.ERROR, Gtk.MessageType.WARNING, Gtk.MessageType.QUESTION.
#    message: The message.
def showMessage( parent, messageType, message ):
    dialog = Gtk.MessageDialog( parent, Gtk.DialogFlags.MODAL, messageType, Gtk.ButtonsType.OK, message )
    dialog.run()
    dialog.destroy()


# Shows and OK/Cancel dialog prompt and returns either Gtk.ResponseType.OK or Gtk.ResponseType.CANCEL.
def showOKCancel( parent, message ):
    dialog = Gtk.MessageDialog( parent, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, message )
    response = dialog.run()
    dialog.destroy()
    return response


# Takes a Gtk.TextView and returns the containing text, avoiding the additional calls to get the start/end positions.
def getTextViewText( textView ): return textView.get_buffer().get_text( textView.get_buffer().get_start_iter(), textView.get_buffer().get_end_iter(), True )


# Listens to checkbox events and toggles the visibility of the widgets.
def onCheckbox( self, *widgets ):
    for widget in widgets:
        widget.set_sensitive( self.get_active() )


# Listens to radio events and toggles the visibility of the widgets.
def onRadio( self, *widgets ):
    for widget in widgets:
        widget.set_sensitive( self.get_active() )


def createPreferencesAboutQuitMenuItems( menu, prependSeparator, onPreferencesHandler, onAboutHandler, onQuitHandler ):
    if prependSeparator:
        menu.append( Gtk.SeparatorMenuItem() )

    menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
    menuItem.connect( "activate", onPreferencesHandler )
    menu.append( menuItem )

    menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
    menuItem.connect( "activate", onAboutHandler )
    menu.append( menuItem )

    menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
    menuItem.connect( "activate", onQuitHandler )
    menu.append( menuItem )


def createAboutDialog(
        authors, # List of authors.
        comments, # Comments.
        creditsPeople, # List of credits.
        creditsLabel, # Credit text.
        licenseType, # Any of Gtk.License.*
        logoIconName, # The name of the image icon - without extension.
        programName, # Program name.
        website, # Website URL (used on click).
        version, # String of the numeric program version.
        translatorCredit ): # The result of calling _( "translator-credits" ) which returns a string or None.

        aboutDialog = Gtk.AboutDialog()

        if sys.version_info.major == 3 and sys.version_info.minor >= 4:
            aboutDialog.set_authors( authors )
            if len( creditsPeople ) > 0:
                aboutDialog.add_credit_section( creditsLabel, creditsPeople )
        else:
            authorsAndCredits = authors
            for credit in creditsPeople:
                authorsAndCredits.append( credit )

            aboutDialog.set_authors( authorsAndCredits )

        aboutDialog.set_comments( comments )
        aboutDialog.set_license_type( licenseType )
        aboutDialog.set_logo_icon_name( logoIconName )
        aboutDialog.set_program_name( programName )
        aboutDialog.set_version( version )
        aboutDialog.set_website( website )
        aboutDialog.set_website_label( website )

        if translatorCredit is not None:
            aboutDialog.set_translator_credits( translatorCredit )

        return aboutDialog


def createChangeLogScrollableWindow( changeLogPathAndFileName, errorMessage, logging ):
    textView = Gtk.TextView()
    textView.set_editable( False )
    textBuffer = textView.get_buffer()
    textBuffer.set_text( getChangeLog( changeLogPathAndFileName, errorMessage, logging ) )

    scrolledWindow = Gtk.ScrolledWindow()
    scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
    scrolledWindow.set_hexpand( True )
    scrolledWindow.set_vexpand( True )
    scrolledWindow.add( textView )
    scrolledWindow.show_all()
    return scrolledWindow


# Assumes a typical format for a Debian change log file.
def getChangeLog( changeLogPathAndFileName, errorMessage, logging ):
    contents = None
    if os.path.exists( changeLogPathAndFileName ): 
        try:
            with gzip.open( changeLogPathAndFileName, "rb" ) as f:
                changeLogContents = re.split( "\n\n\n", f.read().decode() )

            contents = ""
            for changeLogEntry in changeLogContents:
                changeLogEntry = changeLogEntry.split( "\n" )
                version = changeLogEntry[ 0 ].split( "(" )[ 1 ].split( "-1)" )[ 0 ]
                dateTime = changeLogEntry[ len( changeLogEntry ) - 1 ].split( ">" )[ 1 ].split( "+" )[ 0 ].strip()
                changes = "\n".join( changeLogEntry[ 2 : len( changeLogEntry ) - 2 ] )
                changes = changes.replace( "    ", "     " )
                contents += "Version " + version + " (" + dateTime + ")\n" + changes + "\n\n"

            contents = contents.strip()

        except Exception as e:
            if not logging is None:
                logging.exception( e )
                logging.error( "Error reading change log: " + changeLogPathAndFileName )

            contents = errorMessage

    return contents

# Log file handler.  Truncates the file when the file size limit is reached.
# http://stackoverflow.com/questions/24157278/limit-python-log-file
# http://svn.python.org/view/python/trunk/Lib/logging/handlers.py?view=markup
class TruncatedFileHandler( logging.handlers.RotatingFileHandler ):
    def __init__( self, filename, mode = "a", maxBytes = 0, encoding = None, delay = 0 ):
        super( TruncatedFileHandler, self ).__init__( filename, mode, maxBytes, 0, encoding, delay )


    def doRollover( self ):
        if self.stream:
            self.stream.close()

        if os.path.exists( self.baseFilename ):
            os.remove( self.baseFilename )

        self.mode = "a" # Using "w" instead works in the same way as does append...why?  Surely "w" would write from the beginning each time?
        self.stream = self._open()