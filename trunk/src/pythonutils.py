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
import datetime, json, logging.handlers, os, pickle, shutil, socket, subprocess, sys


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

URL_TIMEOUT_IN_SECONDS = 10

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


# Returns True if a number; False otherwise.
def isNumber( numberAsString ):
    try:
        float( numberAsString )
        return True
    except ValueError:
        return False


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


def isUbuntu1604(): return processGet( "lsb_release -sc" ).strip() == "xenial"


# Provides indent spacing for menu items,
# given Ubuntu 16.04 (Unity) and Ubuntu 18.04+ (GNOME Shell) differences.
def indent( indentUnity, indentGnomeShell ):
    INDENT = "    -" #TODO The - is for testing.
    if isUbuntu1604():
        indent = INDENT * indentUnity
    else:
        indent = INDENT * indentGnomeShell

    return indent


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


# Read a dict of configuration from a JSON text file.
#
# applicationBaseDirectory: The directory used as the final part of the overall path.
# configBaseFile: The file name (without extension).
# logging: A valid logger, used on error.
#
# Returns a dict of key/value pairs (empty when no file is present or an error occurs).
def loadConfig( applicationBaseDirectory, configBaseFile, logging ):
    configFile = _getConfigFile( applicationBaseDirectory, configBaseFile )
    config = { }
    if os.path.isfile( configFile ):
        try:
            with open( configFile ) as f:
                config = json.load( f )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error reading configuration: " + configFile )

    return config


# Write a dict of user configuration to a JSON text file.
#
# config: dict of key/value pairs.
# applicationBaseDirectory: The directory used as the final part of the overall path.
# configBaseFile: The file name (without extension).
# logging: A valid logger, used on error.
def saveConfig( config, applicationBaseDirectory, configBaseFile, logging ):
    configFile = _getConfigFile( applicationBaseDirectory, configBaseFile )
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
def _getConfigFile( applicationBaseDirectory, configBaseFile ):
    return _getUserDirectory( XDG_KEY_CONFIG, USER_DIRECTORY_CONFIG, applicationBaseDirectory ) + "/" + configBaseFile + JSON_EXTENSION


# Obtain the full path to a cache file, creating if necessary the underlying path.
#
# applicationBaseDirectory: The directory path used as the final part of the overall path.
# filename: The file name.
def getCachePathname( applicationBaseDirectory, filename ):
    return _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory ) + "/" + filename


# Read a text file from the cache.
#
# applicationBaseDirectory: The directory used as the final part of the overall path.
# fileName: The file name of the text file.
# logging: A valid logger, used on error.
#
# Returns the text contents or None on error.
def readCacheText( applicationBaseDirectory, fileName, logging ):
    cacheFile = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory ) + "/" + fileName
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
    cacheFile = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory ) + "/" + fileName
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
# Returns a tuple of the binary object and the (string) date/time, or a tuple of (None, None) on error.
def readCacheBinary( applicationBaseDirectory, baseName, logging ):
    cacheDirectory = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
    files = [ ]
    for file in os.listdir( cacheDirectory ):
        if file.startswith( baseName ):
            files.append( file )

    # Sort the matching files by date - all file(s) will be newer than the cache maximum date/time.
    files.sort()
    data = None
    dateTime = None
    for file in reversed( files ): # Look at the most recent file first.
        filename = cacheDirectory + "/" + file
        try:
            with open( filename, "rb" ) as f:
                data = pickle.load( f )

            if data is not None and len( data ) > 0:
                dateTime = file[ len( baseName ) : ]
                break

        except Exception as e:
            data = None
            dateTime = None
            logging.exception( e )
            logging.error( "Error reading from cache: " + filename )

    # Only return None or non-empty.
    if data is None or len( data ) == 0: # Return None or a non-empty object.
        data = None
        dateTime = None

    return ( data, dateTime )


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
    cacheDirectory = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
    filename = cacheDirectory + "/" + baseName + datetime.datetime.now().strftime( CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
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
    cacheDirectory = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
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
    cacheDirectory = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
    cacheMaximumAgeDateTime = datetime.datetime.now() - datetime.timedelta( hours = cacheMaximumAgeInHours )
    cacheMaximumDateTimeString = cacheMaximumAgeDateTime.strftime( CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
    for file in os.listdir( cacheDirectory ):
        if file.startswith( baseName ):
            fileDateTime = file[ len( baseName ) : ]
            if fileDateTime < cacheMaximumDateTimeString:
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
def _getUserDirectory( XDGKey, userBaseDirectory, applicationBaseDirectory ):
    if XDGKey in os.environ:
        directory = os.environ[ XDGKey ] + "/" + applicationBaseDirectory
    else:
        directory = os.path.expanduser( "~" ) + "/" + userBaseDirectory + "/" + applicationBaseDirectory

    if not os.path.isdir( directory ):
        os.mkdir( directory )

    return directory


# Opens a socket to www.google.com and if successful,
# we are connected to the internet and returns True (False otherwise).
def isConnectedToInternet():
    connected = False
    try:
        socket.create_connection( ( socket.gethostbyname( "www.google.com" ), 80 ), timeout = URL_TIMEOUT_IN_SECONDS ).close()
        connected = True
    except socket.error:
        pass

    return connected


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