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


import gettext
gettext.install( "pythonutils" )

from gi.repository import Gtk
import logging.handlers, os, shutil, subprocess, sys


AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"

INDENT_WIDGET_LEFT = 20
INDENT_TEXT_LEFT = 25

LOGGING_BASIC_CONFIG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGING_BASIC_CONFIG_LEVEL = logging.DEBUG


def getVersion(): return "1.0.0"


def processCall( command ):
    try:
        subprocess.call( command, shell = True )
    except subprocess.CalledProcessError:
        pass


# Returns the result of calling the command.  On exception, returns None.
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


def isAutoStart( desktopFile, logging, autoStartPath = AUTOSTART_PATH ):
    try:
        return \
            os.path.exists( autoStartPath + desktopFile ) and \
            "X-GNOME-Autostart-enabled=true" in open( autoStartPath + desktopFile ).read()
    except Exception as e:
        logging.exception( e )
        return False


def setAutoStart( desktopFile, isSet, logging, autoStartPath = AUTOSTART_PATH, desktopPath = "/usr/share/applications/" ):
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


# Shows a message dialog.
#    messageType: One of Gtk.MessageType.INFO, Gtk.MessageType.ERROR, Gtk.MessageType.WARNING, Gtk.MessageType.QUESTION.
def showMessage( parent, messageType, message, title ):
    dialog = Gtk.MessageDialog( parent, Gtk.DialogFlags.MODAL, messageType, Gtk.ButtonsType.OK, message )
    dialog.set_title( title )
    dialog.run()
    dialog.destroy()


# Shows and OK/Cancel dialog prompt and returns either Gtk.ResponseType.OK or Gtk.ResponseType.CANCEL.
def showOKCancel( parent, message, title ):
    dialog = Gtk.MessageDialog( parent, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, message )
    dialog.set_title( title )
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

    menuItem = Gtk.MenuItem.new_with_label( _( "Preferences" ) )
    menuItem.connect( "activate", onPreferencesHandler )
    menu.append( menuItem )

    menuItem = Gtk.MenuItem.new_with_label( _( "About" ) )
    menuItem.connect( "activate", onAboutHandler )
    menu.append( menuItem )

    menuItem = Gtk.MenuItem.new_with_label( _( "Quit" ) )
    menuItem.connect( "activate", onQuitHandler )
    menu.append( menuItem )


def showAboutDialog(
        authors, # List of authors.
        comments, # Comments.
        creditsPeople, # List of credits.
        creditsLabel, # Credit text.
        licenseType, # Any of Gtk.License.*
        logoIconName, # The name of the image icon - without extension.
        programName, # Program name.
        website, # Website URL (used on click).
        version, # String of the numeric program version.
        translatorCredit, # The result of calling _( "translator-credits" ) which returns a string or None.
        changeLogLabelBeforeLink, # Text to the left of the hyperlink in the changelog label.
        changeLogLabelAfterLink, # Text to the right of the hyperlink in the changelog label.
        changeLogLabelAnchor ): # The anchor text of the hyperlink in the changelog label.

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

        if not( translatorCredit is None or translatorCredit == "" ):
            aboutDialog.set_translator_credits( translatorCredit )

        changeLog = os.path.dirname( os.path.abspath( __file__ ) ) + "/changelog"
        if os.path.exists( changeLog ):
            notebookOrStack = aboutDialog.get_content_area().get_children()[ 0 ].get_children()[ 2 ]
            if type( notebookOrStack ).__name__ == "Notebook":
                notebookOrStack = notebookOrStack.get_nth_page( 0 )
            else: # Stack
                notebookOrStack = notebookOrStack.get_children()[ 0 ]

            changeLogLabelToolTip = "file://" + os.path.dirname( os.path.abspath( __file__ ) ) + "/changelog"
            label = Gtk.Label()
            label.set_markup( changeLogLabelBeforeLink + " <a href=\'" + "file://" + changeLog + "\' title=\'" + changeLogLabelToolTip + "\'>" + changeLogLabelAnchor + "</a> " + changeLogLabelAfterLink )
            label.show()
            notebookOrStack.add( label )

        aboutDialog.run()
        aboutDialog.hide()


# Log file handler.  Truncates the file when the file size limit is reached.
# http://stackoverflow.com/questions/24157278/limit-python-log-file
# http://svn.python.org/view/python/trunk/Lib/logging/handlers.py?view=markup
class TruncatedFileHandler( logging.handlers.RotatingFileHandler ):
    def __init__( self, filename, maxBytes = 10000 ): super().__init__( filename, "a", maxBytes, 0, None, True )


    def doRollover( self ):
        if self.stream:
            self.stream.close()

        if os.path.exists( self.baseFilename ):
            os.remove( self.baseFilename )

        self.mode = "a" # Using "w" instead works in the same way as does append...why?  Surely "w" would write from the beginning each time?
        self.stream = self._open()