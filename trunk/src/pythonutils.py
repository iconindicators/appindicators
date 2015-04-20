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

import gzip, logging.handlers, os, psutil, re, sys


def getMemoryUsageInMB(): return psutil.Process( os.getpid() ).get_memory_info()[ 0 ] / float( 2 ** 20 )


# Returns True if a number; False otherwise.
def isNumber( numberAsString ):
    try:
        float( numberAsString )
        return True

    except ValueError:
        return False


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


def createPreferencesAboutQuitMenuItems( menu, onPreferencesHandler, onAboutHandler, onQuitHandler ):
    menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
    menuItem.connect( "activate", onPreferencesHandler )
    menu.append( menuItem )

    menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
    menuItem.connect( "activate", onAboutHandler )
    menu.append( menuItem )

    menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
    menuItem.connect( "activate", onQuitHandler )
    menu.append( menuItem )


# A GTK AboutDialog with optional change log displayed in its own tab.
class AboutDialog( Gtk.AboutDialog ):

    def __init__( self, 
        programName, # Program name.
        comments, # Comments.
        website, # Website URL (used on click).
        websiteLabel, # Website (may or may not be the actual URL).
        version, # String of the numeric program version.
        licenseType, # Any of Gtk.License.*
        logoIconName, # The name of the image icon - without extension.
        authors, # List of authors.
        creditsPeople, # List of creditors.
        creditsLabel, # Credit text.
        changeLog, # The full path to the change log; None otherwise.
        changeLogButtonName, # The name of the change log button, optionally including the underscore for the keyboard shortcut.
        translator, # Either the result of calling _( "translator-credits" ) which returns a string or None.
        logging ):# Default Python logging mechanism; None otherwise.

        super( AboutDialog, self ).__init__()

        # The function 'add_credit_section' is/was not available on Ubuntu 12.04 (GTK 3.2 and python 3.2).
        # Previously I was using a try/except to trap a call to 'add_credit_section' - on the except, set the authors a different (older) way.
        # However something has changed and 'add_credit_section' appears to exist but causes a segmentation fault when called.
        # The workaround is to test the python version and use that to discriminate and avoid the try/except.
        # The function 'add_credit_section' IS available on Ubuntu 14.04 (python 3.4).
        if sys.version_info.major == 3 and sys.version_info.minor >= 4:
            self.set_authors( authors )
            self.add_credit_section( creditsLabel, creditsPeople )
        else:
            authorsCredits = authors
            for credit in creditsPeople:
                authorsCredits.append( credit )

            self.set_authors( authorsCredits )

        if translator is not None:
            self.set_translator_credits( translator )

        self.set_comments( comments )
        self.set_license_type( licenseType )
        self.set_logo_icon_name( logoIconName )
        self.set_program_name( programName )
        self.set_version( version )
        self.set_website( website )
        self.set_website_label( websiteLabel )
        self.set_position( Gtk.WindowPosition.CENTER_ALWAYS )
        self.changeLog = changeLog
        self.logging = logging

        notebook = self.get_content_area().get_children()[ 0 ].get_children()[ 2 ]

        # Ensure the credits scrolled window never has a vertical scrollbar.
        creditsTab = notebook.get_nth_page( 1 ) # There should be three tabs/pages, but on Ubuntu 12.04 there is only one for some reason...
        if creditsTab is not None: # ...so the credits TAB can be None!
            children = creditsTab.get_children()
            for child in children:
                if type( child ).__name__ == "ScrolledWindow":
                    child.set_policy( child.get_policy()[ 0 ], Gtk.PolicyType.NEVER ) 

        if changeLog is not None: # If there is no change log this dialog reverts to the AboutDialog.
            self.set_resizable( True )

            textView = Gtk.TextView()
            textView.set_editable( False )
            textBuffer = textView.get_buffer()
            textBuffer.set_text( self.getChangeLog() )

            # Reference https://gitorious.org/ghelp/gtk/raw/5c4f2ef0c1e658827091aadf4fc3c4d5f5964785:gtk/gtkaboutdialog.c
            scrolledWindow = Gtk.ScrolledWindow()
            scrolledWindow.set_shadow_type( Gtk.ShadowType.IN );
            scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
            scrolledWindow.set_hexpand( True )
            scrolledWindow.set_vexpand( True )
            scrolledWindow.add( textView )
            scrolledWindow.show_all()

            changeLogTabIndex = notebook.append_page( scrolledWindow, Gtk.Label( "" ) ) # The tab is hidden so the label contents are irrelevant.

            changeLogButton = Gtk.ToggleButton( changeLogButtonName )
            changeLogButton.set_use_underline( True )
            changeLogButton.show()

            buttonBox = self.get_content_area().get_children()[ 1 ]
            buttonBox.pack_start( changeLogButton, True, True, 0 )
            buttonBox.set_child_secondary( changeLogButton, True )

            buttons = buttonBox.get_children()
            buttonsForToggle = [ ]
            for button in buttons:
                if button != changeLogButton and type( button ) == Gtk.ToggleButton:
                    buttonsForToggle.append( button )
                    button.connect( "toggled", self.onOtherToggledButtons, changeLogButton )

            changeLogButton.connect( "toggled", self.onChangeLogButtonToggled, notebook, changeLogTabIndex, buttonsForToggle )


    def onChangeLogButtonToggled( self, changeLogButton, notebook, changeLogTabIndex, buttonsForToggle ):
        if changeLogButton.get_active():
            if notebook.get_current_page() != 0:
                for button in buttonsForToggle:
                    button.set_active( False )

            notebook.set_current_page( changeLogTabIndex )
        else:
            if notebook.get_current_page() == changeLogTabIndex:
                notebook.set_current_page( 0 )


    def onOtherToggledButtons( self, toggleButton, changeLogButton ):
        if toggleButton.get_active() and changeLogButton.get_active():
            changeLogButton.set_active( False )


    # Assumes a typical format for a Debian change log file.
    def getChangeLog( self ):
        contents = None
        if os.path.exists( self.changeLog ): 
            try:
                with gzip.open( self.changeLog, "rb" ) as f:
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
                if not self.logging is None:
                    self.logging.exception( e )
                    self.logging.error( "Error reading change log: " + self.changeLog )

                contents = "Error reading change log: " + self.changeLog

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