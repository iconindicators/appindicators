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
import datetime, json, logging.handlers, os, pickle, shutil, subprocess, sys


AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"

CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"

INDENT_WIDGET_LEFT = 20
INDENT_TEXT_LEFT = 25

JSON_EXTENSION = ".json"

LOGGING_BASIC_CONFIG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGING_BASIC_CONFIG_LEVEL = logging.DEBUG

USER_DIRECTORY_CACHE = ".cache"
USER_DIRECTORY_CONFIG = ".config"

XDG_KEY_CACHE = "XDG_CACHE_HOME"
XDG_KEY_CONFIG = "XDG_CONFIG_HOME"


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


# Read a dict of configuration from a JSON text file.
#
# applicationBaseDirectory: The directory path used as the final part of the overall path.
# configBaseFile: The file name (without extension).
# logging: Used to log.
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
# applicationBaseDirectory: The directory path used as the final part of the overall path.
# configBaseFile: The file name (without extension).
# logging: Used to log.
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


# Move the configuration file from user home (original and incorrect location)
# to new location ONLY if the new location does not contain a configuration file.
#
# name The application name, which was used as the base name of the configuration file
# in the user's home directory, and will now be used as the base directory name in the
# new configuration location in addition to the base name of the configuration file.
def migrateConfig( applicationName ):
    oldConfigFile = os.path.expanduser( "~" ) + "/." + applicationName + JSON_EXTENSION
    newConfigFile = _getConfigFile( applicationName, applicationName )
    if os.path.isfile( oldConfigFile ) and not os.path.isfile( newConfigFile ):
        os.rename( oldConfigFile, newConfigFile )


# Obtain the user configuration JSON file, creating if necessary the underlying directory.
#
# applicationBaseDirectory: The directory path used as the final part of the overall path.
# configBaseFile: The file name (without extension).
def _getConfigFile( applicationBaseDirectory, configBaseFile ):
    return _getUserDirectory( XDG_KEY_CONFIG, USER_DIRECTORY_CONFIG, applicationBaseDirectory ) + "/" + configBaseFile + JSON_EXTENSION


#TODO Fix header
# Read a dict of ?????/ from a JSON text file.
#
# applicationBaseDirectory: The directory path used as the final part of the overall path.
# configBaseFile: The file name (without extension).
# logging: Used to log.
#
# Returns a dict of key/value pairs (empty when no file is present or an error occurs).
def readCacheText( applicationBaseDirectory, fileName, logging ):
    cacheFile = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory ) + "/" + fileName
    text = ""
    if os.path.isfile( cacheFile ):
        try:
            with open( cacheFile, "r" ) as f:
                text = f.read()
        except Exception as e:
            logging.exception( e )
            logging.error( "Error reading from cache: " + cacheFile )

    return text


#TODO Fix header.
# Writes text to a file in the cache.
#
# data: The object to write.
# cachePath: File system path to the directory location of the cache.
# baseName: Text used, along with a timestamp, to form the binary file name.
# cacheMaximumDateTime: If any file is older than the date/time,
#                       in format CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS, 
#                       the file will be discarded.  
#
# For the application "fred" to write the objects "maryDict" and "janeDict":
#
#    writeToCache( maryDict, ~/.cache/fred/, mary, logging )
#    writeToCache( janeDict, ~/.cache/fred/, jane, logging )
#
# resulting in binary files written (with timestamps):
#
#    ~/.cache/fred/mary-20170629174950
#    ~/.cache/fred/jane-20170629174951
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


#TODO Fix header.
# Reads the most recent file from the cache for the given base name.
#
# cachePath: File system path to the directory location of the cache.
# baseName: Text used, along with a timestamp, to form the binary file name.
# cacheMaximumDateTime: If any file is older than the date/time,
#                       in format CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS, 
#                       the file will be discarded.  
#
# Returns a tuple of the data (either None or the object) and the corresponding date/time as string (either None or the date/time).
def readCacheBinary( applicationBaseDirectory, baseName, cacheMaximumDateTime, logging ):

#TODO Verify this function works!
    
    cacheDirectory = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )

    # Read all files in the cache and note those which match the base name.
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
    if data is None or len( data ) == 0: #TODO Return None or [] instead?  Is it possible to end up with None?
        data = None
        dateTime = None

    return ( data, dateTime )


#TODO Fix header.
# Remove a file from the cache.
#
# applicationBaseDirectory: File system path to the directory location of the cache.
# fileName: Text used, along with a timestamp, to form the binary file name.
def removeFileFromCache( applicationBaseDirectory, fileName ):
    cacheDirectory = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
    for file in os.listdir( cacheDirectory ):
        if file == fileName:
            os.remove( cacheDirectory + "/" + file )


#TODO Fix header.
#TODO Add comment on the file name format: baseNamecacheMaximumDateTime ...might need a hypen in between...which means callers need to drop their hyphen.  Maybe!
#TODO Ensure this works using new directory system.
# Removes out of date cache files.
#
# cachePath: File system path to the directory location of the cache.
# baseName: Text used, along with a timestamp, to form the binary file name.
# cacheMaximumDateTime: If any file is older than the date/time,
#                       in format CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS, 
#                       the file will be discarded.  
def removeOldFilesFromCache( applicationBaseDirectory, baseName, cacheMaximumDateTime ):
    cacheDirectory = _getUserDirectory( XDG_KEY_CACHE, USER_DIRECTORY_CACHE, applicationBaseDirectory )
    cacheMaximumDateTimeString = cacheMaximumDateTime.strftime( CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
    for file in os.listdir( cacheDirectory ):
        if file.startswith( baseName ):
            fileDateTime = file[ len( baseName ) : ]
            if fileDateTime < cacheMaximumDateTimeString:
                os.remove( cacheDirectory + "/" + file )


# Obtain (and create if not present) the directory for application config, cache or similar.
#
# XDGKey: The XDG environment variable used to obtain the base directory of the config/cache.
#         https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
# userBaseDirectory: The directory name used to hold the config/cache (used when the XDGKey is not present in the environment).
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


# Writes an object as a binary file.
#
# data: The object to write.
# cachePath: File system path to the directory location of the cache.
# baseName: Text used, along with a timestamp, to form the binary file name.
# cacheMaximumDateTime: If any file is older than the date/time,
#                       in format CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS, 
#                       the file will be discarded.  
#
# For the application "fred" to write the objects "maryDict" and "janeDict":
#
#    writeToCache( maryDict, ~/.cache/fred/, mary, logging )
#    writeToCache( janeDict, ~/.cache/fred/, jane, logging )
#
# resulting in binary files written (with timestamps):
#
#    ~/.cache/fred/mary-20170629174950
#    ~/.cache/fred/jane-20170629174951
def writeToCache( data, cachePath, baseName, cacheMaximumDateTime, logging ):
    __createCache( cachePath )

    # Read all files in the cache and keep a list of those which match the base name.
    __clearCache( cachePath, baseName, cacheMaximumDateTime )

    filename = cachePath + baseName + datetime.datetime.now().strftime( CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
    try:
        with open( filename, "wb" ) as f:
            pickle.dump( data, f )

    except Exception as e:
        logging.exception( e )
        logging.error( "Error writing to cache: " + filename )


# Reads the most recent file from the cache for the given base name.
# Removes out of date cache files.
#
# cachePath: File system path to the directory location of the cache.
# baseName: Text used, along with a timestamp, to form the binary file name.
# cacheMaximumDateTime: If any file is older than the date/time,
#                       in format CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS, 
#                       the file will be discarded.  
#
# Returns a tuple of the data (either None or the object) and the corresponding date/time as string (either None or the date/time).
def readFromCache( cachePath, baseName, cacheMaximumDateTime, logging ):
    __createCache( cachePath )
    
    # Read all files in the cache and keep a list of those which match the base name.
    __clearCache( cachePath, baseName, cacheMaximumDateTime )

    # Any file matching the base name is kept.
    files = [ ]
    for file in os.listdir( cachePath ):
        if file.startswith( baseName ):
            files.append( file )

    # Sort the matching files by date - all file(s) will be newer than the cache maximum date/time.
    files.sort()
    data = None
    dateTime = None
    for file in reversed( files ): # Look at the most recent file first.
        filename = cachePath + file
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
    if data is None or len( data ) == 0:
        data = None
        dateTime = None

    return ( data, dateTime )


# Removes out of date cache files.
#
# cachePath: File system path to the directory location of the cache.
# baseName: Text used, along with a timestamp, to form the binary file name.
# cacheMaximumDateTime: If any file is older than the date/time,
#                       in format CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS, 
#                       the file will be discarded.  
def __clearCache( cachePath, baseName, cacheMaximumDateTime ):#TODO Need a new version that doesn't take the cache path and call it removeFromCache (if possible).
    # Read all files in the cache and any file matching the base name but older than the cache maximum date/time id deleted.
    cacheMaximumDateTimeString = cacheMaximumDateTime.strftime( CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
    for file in os.listdir( cachePath ):
        if file.startswith( baseName ):
            fileDateTime = file[ file.index( baseName ) + len( baseName ) : ]
            if fileDateTime < cacheMaximumDateTimeString:
                os.remove( cachePath + file )


# Creates the cache.
#
# cachePath: File system path to the directory location of the cache.
def __createCache( cachePath ):
    if not os.path.exists( cachePath ):
        os.makedirs( cachePath )


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