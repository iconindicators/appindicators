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


import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
import datetime, gzip, json, logging.handlers, os, pickle, shutil, subprocess


AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"

CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"

INDENT_WIDGET_LEFT = 20
INDENT_TEXT_LEFT = 25

JSON_EXTENSION = ".json"

LOGGING_BASIC_CONFIG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGING_BASIC_CONFIG_LEVEL = logging.DEBUG

TERMINAL_GNOME = "gnome-terminal"
TERMINAL_LXDE = "lxterminal"
TERMINAL_XFCE = "xfce4-terminal"

URL_TIMEOUT_IN_SECONDS = 2

USER_DIRECTORY_CACHE = ".cache"
USER_DIRECTORY_CONFIG = ".config"

XDG_KEY_CACHE = "XDG_CACHE_HOME"
XDG_KEY_CONFIG = "XDG_CONFIG_HOME"


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


#TODO STILL NEEDED?
# Returns True if a number; False otherwise.
def isNumber( numberAsString ):
    try:
        float( numberAsString )
        return True
    except ValueError:
        return False


#TODO STILL NEEDED?
# Return the full path and name of the executable for the current terminal; None on failure.
def getTerminal():
    terminal = processGet( "which " + TERMINAL_GNOME )
    if terminal is None:
        terminal = processGet( "which " + TERMINAL_LXDE )

        if terminal is None:
            terminal = processGet( "which " + TERMINAL_XFCE )

    if terminal is not None:
        terminal = terminal.strip()

    if terminal == "":
        terminal = None

    return terminal


#TODO STILL NEEDED?
# Return the execution flag for the given terminal; None on failure. 
def getTerminalExecutionFlag( terminal ): 
    executionFlag = None
    if terminal is not None:
        if terminal.endswith( TERMINAL_GNOME ):
            executionFlag = "--"
        elif terminal.endswith( TERMINAL_LXDE ):
            executionFlag = "-e"
        elif terminal.endswith( TERMINAL_XFCE ):
            executionFlag = "-x"

    return executionFlag


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


#TODO STILL NEEDED?
# Takes a Gtk.TextView and returns the containing text, avoiding the additional calls to get the start/end positions.
def getTextViewText( textView ): return textView.get_buffer().get_text( textView.get_buffer().get_start_iter(), textView.get_buffer().get_end_iter(), True )


# Listens to checkbox events and toggles the visibility of the widgets.
def onCheckbox( self, *widgets ):
    for widget in widgets:
        widget.set_sensitive( self.get_active() )


#TODO STILL NEEDED?
# Listens to radio events and toggles the visibility of the widgets.
def onRadio( self, *widgets ):
    for widget in widgets:
        widget.set_sensitive( self.get_active() )


def createGrid():
    spacing = 10
    grid = Gtk.Grid()
    grid.set_column_spacing( spacing )
    grid.set_row_spacing( spacing )
    grid.set_margin_left( spacing )
    grid.set_margin_right( spacing )
    grid.set_margin_top( spacing )
    grid.set_margin_bottom( spacing )
    return grid


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


def getThemeName(): return Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )


#TODO Verify this works for indicator lunar still.  
#TODO Need a header comment specifying the expectation that a tag with the colour is present in the SVG file.
def getThemeColour( iconName, logging ):
    iconFilenameForCurrentTheme = "/usr/share/icons/" + getThemeName() + "/scalable/apps/" + iconName + ".svg"
    try:
        with open( iconFilenameForCurrentTheme, "r" ) as file:
            data = file.read()
            index = data.find( "style=\"fill:#" )
            themeColour = data[ index + 13 : index + 19 ]

    except Exception as e:
        logging.exception( e )
        logging.error( "Error reading SVG icon: " + iconFilenameForCurrentTheme )
        themeColour = "fff200" # Default to hicolor.

    return themeColour


def isUbuntu1604(): return processGet( "lsb_release -sc" ).strip() == "xenial"


# Provides indent spacing for menu items,
# given Ubuntu 16.04 (Unity) and Ubuntu 18.04+ (GNOME Shell) differences.
def indent( indentUnity, indentGnomeShell ):
    INDENT = "      "
    if isUbuntu1604():
        indent = INDENT * indentUnity
    else:
        indent = INDENT * indentGnomeShell

    return indent


# Makes a guess at how many menu items will fit into an indicator menu. 
#
# By experiment under Unity, a screen height of 900 pixels accommodates 37 menu items before a scroll bar appears.
# For an initial guess, compute a divisor: 900 / 37 = 25.
#
# For GNOME Shell, the equivalent divisor is 36.
def getMenuItemsGuess(): 
    if isUbuntu1604():
        guess = Gtk.Window().get_screen().get_height() / 25
    else:
        guess = Gtk.Window().get_screen().get_height() / 36

    return guess


#TODO Add notes about assumption of program name matching error log file (and its location),
#and changelog file name/location...
#...anything else?
# Icon name is same as program name
#
# Shows an about dialog.
#
# Uses GPL 3.0
def showAboutDialog(
        programName, # Program name.
        authors, # List of authors.
        comments, # Comments.
        copyrightStartYear,
        website, # Website URL (used on click).
        version, # String of the numeric program version.
        creditsPeople = None, # List of credits.
        copyrightName = None,  #TODO Default to author if single (not a list)
        artists = None ): # List of artists.   #TODO Default to authors

        copyrightText = "Copyright \xa9 " + \
                    copyrightStartYear + \
                    "-" + \
                    str( datetime.datetime.now().year ) + \
                    " " + \
                    authors[ 0 ] if copyrightName is None and len( authors ) > 1 else "TODO Fix this!"#TODO Not going to work if authors has a email/url.

        aboutDialog = Gtk.AboutDialog()

        aboutDialog.set_artists( authors if artists is None else artists )
        aboutDialog.set_authors( authors )
        aboutDialog.set_comments( comments )
        aboutDialog.set_copyright( copyrightText )
        aboutDialog.add_credit_section( _( "Credits" ), creditsPeople ) #TODO Check that None can be passed in.
        aboutDialog.set_license_type( Gtk.License.GPL_3_0 )
        aboutDialog.set_logo_icon_name( programName )
        aboutDialog.set_program_name( programName )
        aboutDialog.set_translator_credits( _( "translator-credits" ) )
        aboutDialog.set_version( version )
        aboutDialog.set_website( website )
        aboutDialog.set_website_label( website )

        changeLog = "/tmp/" + programName + ".changelog"
        if os.path.isfile( changeLog ):
            os.remove( changeLog )

        with gzip.open( "/usr/share/doc/" + programName + "/changelog.Debian.gz", 'r' ) as fileIn, open( changeLog, 'wb' ) as fileOut:
            shutil.copyfileobj( fileIn, fileOut )

        errorLog = os.getenv( "HOME" ) + "/" + programName + ".log"


        def addHyperlinkLabel( filePath, leftText, rightText, anchorText ):
            if os.path.exists( filePath ):
                notebookOrStack = aboutDialog.get_content_area().get_children()[ 0 ].get_children()[ 2 ]
                if type( notebookOrStack ).__name__ == "Notebook":
                    notebookOrStack = notebookOrStack.get_nth_page( 0 )
                else: # Stack
                    notebookOrStack = notebookOrStack.get_children()[ 0 ]

                toolTip = "file://" + filePath
                label = Gtk.Label()
                label.set_markup( leftText + " <a href=\'" + "file://" + filePath + "\' title=\'" + toolTip + "\'>" + anchorText + "</a> " + rightText )
                label.show()
                notebookOrStack.add( label )

        addHyperlinkLabel( changeLog, _( "View the" ), _( "text file." ), _( "changelog" ) )
        addHyperlinkLabel( errorLog, _( "View the" ), _( "text file." ), _( "error log" ) )

        aboutDialog.run()
        aboutDialog.hide()


def showAboutDialogORIG(
        authors, # List of authors.
        artists, # List of artists.
        comments, # Comments.
        copyrightName,
        copyrightStartYear,
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
        changeLogLabelAnchor, # The anchor text of the hyperlink in the changelog label.
        errorLog, # Path to the log file (whether or not the actual file exists).
        errorLogLabelBeforeLink, # Text to the left of the hyperlink in the errorlog label.
        errorLogLabelAfterLink, # Text to the right of the hyperlink in the errorlog label.
        errorLogLabelAnchor ): # The anchor text of the hyperlink in the errorlog label.

        aboutDialog = Gtk.AboutDialog()

        aboutDialog.set_artists( artists )
        aboutDialog.set_authors( authors )
        aboutDialog.set_comments( comments )
        aboutDialog.set_copyright( "Copyright \xa9 " + copyrightStartYear + "-" + str( datetime.datetime.now().year ) + " " + copyrightName )
        aboutDialog.add_credit_section( creditsLabel, creditsPeople )
        aboutDialog.set_license_type( licenseType )
        aboutDialog.set_logo_icon_name( logoIconName )
        aboutDialog.set_program_name( programName )
        aboutDialog.set_translator_credits( translatorCredit )
        aboutDialog.set_version( version )
        aboutDialog.set_website( website )
        aboutDialog.set_website_label( website )
        aboutDialog.set_translator_credits( translatorCredit )

        changeLog = "/tmp/" + programName + ".changelog"
        if os.path.isfile( changeLog ):
            os.remove( changeLog )

        with gzip.open( "/usr/share/doc/" + programName + "/changelog.Debian.gz", 'r' ) as fileIn, open( changeLog, 'wb' ) as fileOut:
            shutil.copyfileobj( fileIn, fileOut )


        def addHyperlinkLabel( filePath, leftText, rightText, anchorText ):
            if os.path.exists( filePath ):
                notebookOrStack = aboutDialog.get_content_area().get_children()[ 0 ].get_children()[ 2 ]
                if type( notebookOrStack ).__name__ == "Notebook":
                    notebookOrStack = notebookOrStack.get_nth_page( 0 )
                else: # Stack
                    notebookOrStack = notebookOrStack.get_children()[ 0 ]

                toolTip = "file://" + filePath
                label = Gtk.Label()
                label.set_markup( leftText + " <a href=\'" + "file://" + filePath + "\' title=\'" + toolTip + "\'>" + anchorText + "</a> " + rightText )
                label.show()
                notebookOrStack.add( label )


        addHyperlinkLabel( changeLog, changeLogLabelBeforeLink, changeLogLabelAfterLink, changeLogLabelAnchor )
        addHyperlinkLabel( errorLog, errorLogLabelBeforeLink, errorLogLabelAfterLink, errorLogLabelAnchor )

        aboutDialog.run()
        aboutDialog.hide()


# Read a dictionary of configuration from a JSON text file.
#
# applicationBaseDirectory: The directory used as the final part of the overall path.
# configBaseFile: The file name (without extension).
# logging: A valid logger, used on error.
#
# Returns a dictionary of key/value pairs (empty when no file is present or an error occurs).
def loadConfig( applicationBaseDirectory, configBaseFile, logging ):
    configFile = __getConfigFile( applicationBaseDirectory, configBaseFile )
    config = { }
    if os.path.isfile( configFile ):
        try:
            with open( configFile ) as f:
                config = json.load( f )

        except Exception as e:
            config = { }
            logging.exception( e )
            logging.error( "Error reading configuration: " + configFile )

    return config


# Write a dictionary of user configuration to a JSON text file.
#
# config: of key/value pairs.
# applicationBaseDirectory: The directory used as the final part of the overall path.
# configBaseFile: The file name (without extension).
# logging: A valid logger, used on error.
def saveConfig( config, applicationBaseDirectory, configBaseFile, logging ):
    configFile = __getConfigFile( applicationBaseDirectory, configBaseFile )
    success = True
    try:
        with open( configFile, "w" ) as f:
            f.write( json.dumps( config ) )
 
    except Exception as e:
        logging.exception( e )
        logging.error( "Error writing configuration: " + configFile )
        success = False

    return success


# Obtain the path to the user configuration JSON file, creating if necessary the underlying path.
#
# applicationBaseDirectory: The directory path used as the final part of the overall path.
# configBaseFile: The file name (without extension).
def __getConfigFile( applicationBaseDirectory, configBaseFile ):
    return __getUserDirectory( XDG_KEY_CONFIG, USER_DIRECTORY_CONFIG, applicationBaseDirectory ) + "/" + configBaseFile + JSON_EXTENSION


# Obtain the full path to a cache file, creating if necessary the underlying path.
#
# applicationBaseDirectory: The directory path used as the final part of the overall path.
# filename: The file name.
def getCachePathname( applicationBaseDirectory, filename ):
    return __getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory ) + "/" + filename


# Read a text file from the cache.
#
# applicationBaseDirectory: The directory used as the final part of the overall path.
# fileName: The file name of the text file.
# logging: A valid logger, used on error.
#
# Returns the text contents or None on error.
def readCacheText( applicationBaseDirectory, fileName, logging ):
    cacheFile = __getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory ) + "/" + fileName
    text = None
    if os.path.isfile( cacheFile ):
        try:
            with open( cacheFile, "r" ) as f:
                text = f.read()

        except Exception as e:
            text = None
            logging.exception( e )
            logging.error( "Error reading from cache: " + cacheFile )

    if text is None or len( text ) == 0: # Return either None or non-empty text.
        text = None

    return text


# Write a text file to the cache.
#
# applicationBaseDirectory: The directory used as the final part of the overall path.
# fileName: The file name of the text file.
# text: The text to write.
# logging: A valid logger, used on error.
def writeCacheText( applicationBaseDirectory, fileName, text, logging ):
    success = True
    cacheFile = __getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory ) + "/" + fileName
    try:
        with open( cacheFile, "w" ) as f:
            f.write( text )

    except Exception as e:
        logging.exception( e )
        logging.error( "Error writing to cache: " + cacheFile )
        success = False

    return success


# Read the most recent binary object from the cache.
#
# applicationBaseDirectory: The directory used as the final part of the overall path.
# baseName: The text used to form the file name, typically the name of the calling application.
# logging: A valid logger, used on error.
#
# All files in cache directory are filtered based on the pattern
#     ${XDGKey}/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
# or
#     ~/.cache/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
#
# For example, for an application 'apple', the first file will pass through, whilst the second is filtered out
#    ~/.cache/fred/apple-20170629174950
#    ~/.cache/fred/orange-20170629174951
#
# Files which pass the filter are sorted by date/time and the most recent file is read.
#
# Returns the binary object; None when no suitable cache file exists; None on error and logs.
def readCacheBinary( applicationBaseDirectory, baseName, logging ):
    cacheDirectory = __getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
    data = None
    theFile = ""
    for file in os.listdir( cacheDirectory ):
        if file.startswith( baseName ) and file > theFile:
            theFile = file

    if theFile: # A value of "" evaluates to False.
        filename = cacheDirectory + "/" + theFile
        try:
            with open( filename, "rb" ) as f:
                data = pickle.load( f )

        except Exception as e:
            data = None
            logging.exception( e )
            logging.error( "Error reading from cache: " + filename )

    return data


# Writes an object as a binary file.
#
# binaryData: The object to write.
# applicationBaseDirectory: The directory used as the final part of the overall path.
# baseName: The text used to form the file name, typically the name of the calling application.
# logging: A valid logger, used on error.
#
# The object will be written to the cache directory using the pattern
#     ${XDGKey}/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
# or
#     ~/.cache/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
#
# Returns True on success; False otherwise.
def writeCacheBinary( binaryData, applicationBaseDirectory, baseName, logging ):
    success = True
    cacheDirectory = __getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
    filename = cacheDirectory + "/" + baseName + datetime.datetime.utcnow().strftime( CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
    try:
        with open( filename, "wb" ) as f:
            pickle.dump( binaryData, f )

    except Exception as e:
        logging.exception( e )
        logging.error( "Error writing to cache: " + filename )
        success = False

    return success


# Remove a file from the cache.
#
# applicationBaseDirectory: The directory used as the final part of the overall path.
# fileName: The file to remove.
#
# The file removed will be either
#     ${XDGKey}/applicationBaseDirectory/fileName
# or
#     ~/.cache/applicationBaseDirectory/fileName
def removeFileFromCache( applicationBaseDirectory, fileName ):
    cacheDirectory = __getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
    for file in os.listdir( cacheDirectory ):
        if file == fileName:
            os.remove( cacheDirectory + "/" + file )


# Removes out of date cache files.
#
# applicationBaseDirectory: The directory used as the final part of the overall path.
# baseName: The text used to form the file name, typically the name of the calling application.
# cacheMaximumAgeInHours: Anything older than the maximum age (hours) is deleted.
#
# Any file in the cache directory matching the pattern
#     ${XDGKey}/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
# or
#     ~/.cache/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
# and is older than the cache maximum age is discarded.
def removeOldFilesFromCache( applicationBaseDirectory, baseName, cacheMaximumAgeInHours ):
    cacheDirectory = __getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
    cacheMaximumAgeDateTime = datetime.datetime.utcnow() - datetime.timedelta( hours = cacheMaximumAgeInHours )
    for file in os.listdir( cacheDirectory ):
        if file.startswith( baseName ):
            fileDateTime = datetime.datetime.strptime( file[ len( baseName ) : ], CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )            
            if fileDateTime < cacheMaximumAgeDateTime:
                os.remove( cacheDirectory + "/" + file )


# Obtain (and create if not present) the directory for configuration, cache or similar.
#
# XDGKey: The XDG environment variable used to obtain the base directory of the configuration/cache.
#         https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
# userBaseDirectory: The directory name used to hold the configuration/cache
#                    (used when the XDGKey is not present in the environment).
# applicationBaseDirectory: The directory name at the end of the final user directory to specify the application.
#
# The full directory path will be either
#    ${XDGKey}/applicationBaseDirectory
# or
#    ~/.userBaseDirectory/applicationBaseDirectory
def __getUserDirectory( XDGKey, userBaseDirectory, applicationBaseDirectory ):
    if XDGKey in os.environ:
        directory = os.environ[ XDGKey ] + "/" + applicationBaseDirectory
    else:
        directory = os.path.expanduser( "~" ) + "/" + userBaseDirectory + "/" + applicationBaseDirectory

    if not os.path.isdir( directory ):
        os.mkdir( directory )

    return directory


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