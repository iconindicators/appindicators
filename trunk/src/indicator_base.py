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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Base class for application indicators.


import gi
gi.require_version( "AppIndicator3", "0.1" )

from gi.repository import AppIndicator3, GLib, Gtk
import datetime, gzip, json, logging.handlers, os, shutil, threading


class IndicatorBase:

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    INDENT_WIDGET_LEFT = 20
    JSON_EXTENSION = ".json"
    LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGGING_LEVEL = logging.DEBUG
    USER_DIRECTORY_CONFIG = ".config"
    XDG_KEY_CONFIG = "XDG_CONFIG_HOME"


    def __init__( self, indicatorName, version, copyrightStartYear, comments, artwork = None, creditz = None ):
        self.indicatorName = indicatorName
        self.version = version
        self.copyrightStartYear = copyrightStartYear
        self.comments = comments

        self.desktopFile = self.indicatorName + ".py.desktop"
        self.icon = self.indicatorName
        self.log = os.getenv( "HOME" ) + "/" + self.indicatorName + ".log"
        self.website = "https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa"

        self.authors = [ "Bernard Giannetti" + " " + self.website ]
        self.artwork = artwork if artwork else self.authors
        self.creditz = creditz

        logging.basicConfig( format = IndicatorBase.LOGGING_FORMAT, level = IndicatorBase.LOGGING_LEVEL, handlers = [ TruncatedFileHandler( self.log ) ] )
        self.lock = threading.Lock()
        self.updateTimerID = None #TODO What if an indicator does not use this (then in the about/prefs when we remove it it'll barf).

        self.indicator = AppIndicator3.Indicator.new( self.indicatorName, self.indicatorName, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

        self.__loadConfig()
        self.__update()


    def main( self ): Gtk.main()


    def __update( self ):
        with self.lock:
            menu = Gtk.Menu()
            self.update( menu ) # Call to implementation in indicator.
            self.__finaliseMenu( menu )


    def __finaliseMenu( self, menu ):
        if len( menu.get_children() ) > 0:
            menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.MenuItem.new_with_label( _( "Preferences" ) )
        menuItem.connect( "activate", self.__onPreferences )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "About" ) )
        menuItem.connect( "activate", self.__onAbout )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Quit" ) )
        menuItem.connect( "activate", Gtk.main_quit )
        menu.append( menuItem )

        menu.show_all()
        self.indicator.set_menu( menu )


    def __onAbout( self, widget ):
        if self.lock.acquire( blocking = False ):
            GLib.source_remove( self.updateTimerID )

            aboutDialog = Gtk.AboutDialog()
            aboutDialog.set_artists( self.artwork )
            aboutDialog.set_authors( self.authors )
            aboutDialog.set_comments( self.comments )

            copyrightText = "Copyright \xa9 " + \
                self.copyrightStartYear + \
                "-" + \
                str( datetime.datetime.now().year ) + \
                " " + \
                self.authors[ 0 ].rsplit( ' ', 1 )[ 0 ]

            aboutDialog.set_copyright( copyrightText )
            if self.creditz: aboutDialog.add_credit_section( _( "Credits" ), self.creditz )
            aboutDialog.set_license_type( Gtk.License.GPL_3_0 )
            aboutDialog.set_logo_icon_name( self.indicatorName )
            aboutDialog.set_program_name( self.indicatorName )
            aboutDialog.set_translator_credits( _( "translator-credits" ) )
            aboutDialog.set_version( self.version )
            aboutDialog.set_website( self.website )
            aboutDialog.set_website_label( self.website )

            changeLog = "/tmp/" + self.indicatorName + ".changelog"
            if os.path.isfile( changeLog ):
                os.remove( changeLog )

            changeLogGzipped = "/usr/share/doc/" + self.indicatorName + "/changelog.Debian.gz"
            with gzip.open( changeLogGzipped, 'r' ) as fileIn, open( changeLog, 'wb' ) as fileOut:
                shutil.copyfileobj( fileIn, fileOut )

            errorLog = os.getenv( "HOME" ) + "/" + self.indicatorName + ".log"
            self.__addHyperlinkLabel( aboutDialog, changeLog, _( "View the" ), _( "text file." ), _( "changelog" ) )
            self.__addHyperlinkLabel( aboutDialog, errorLog, _( "View the" ), _( "text file." ), _( "error log" ) )

            aboutDialog.run()
            aboutDialog.hide()

            self.lock.release()
            GLib.idle_add( self.update )


    def __addHyperlinkLabel( self, aboutDialog, filePath, leftText, rightText, anchorText ):
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


    def __onPreferences( self, widget ):
        if self.lock.acquire( blocking = False ):
            GLib.source_remove( self.updateTimerID )
            self.onPreferences() # Call to implementation in indicator.
            self.lock.release()
            GLib.idle_add( self.update )


    def createGrid( self ):
        spacing = 10
        grid = Gtk.Grid()
        grid.set_column_spacing( spacing )
        grid.set_row_spacing( spacing )
        grid.set_margin_left( spacing )
        grid.set_margin_right( spacing )
        grid.set_margin_top( spacing )
        grid.set_margin_bottom( spacing )
        return grid


    def isAutoStart( self ):
        autoStart = False
        try:
            autoStart = os.path.exists( IndicatorBase.AUTOSTART_PATH + self.desktopFile ) and \
                        "X-GNOME-Autostart-enabled=true" in open( IndicatorBase.AUTOSTART_PATH + self.desktopFile ).read()

        except Exception as e:
            logging.exception( e )
            autoStart = False

        return autoStart


    def setAutoStart( self, isSet ):
        if not os.path.exists( IndicatorBase.AUTOSTART_PATH ):
            os.makedirs( IndicatorBase.AUTOSTART_PATH )

        try:
            if isSet:
                shutil.copy( IndicatorBase.DESKTOP_PATH + self.desktopFile, IndicatorBase.AUTOSTART_PATH + self.desktopFile )

            else:
                os.remove( IndicatorBase.AUTOSTART_PATH + self.desktopFile )

        except Exception as e:
            logging.exception( e )


    def getLogging( self ): return logging


    # Read a dictionary of configuration from a JSON text file.
    def __loadConfig( self ):
        configFile = self.__getConfigFile( self.indicatorName, self.indicatorName )
        config = { }
        if os.path.isfile( configFile ):
            try:
                with open( configFile ) as f:
                    config = json.load( f )

            except Exception as e:
                config = { }
                logging.exception( e )
                logging.error( "Error reading configuration: " + configFile )

        self.loadConfig( config ) # Call to implementation in indicator.


    # Write a dictionary of user configuration to a JSON text file.
    def __saveConfig( self ):
        config = self.saveConfig() # Call to implementation in indicator.
        configFile = self.__getConfigFile( self.indicatorName, self.indicatorName )
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
    def __getConfigFile( self, applicationBaseDirectory, configBaseFile ):
        return self.__getUserDirectory( IndicatorBase.XDG_KEY_CONFIG, IndicatorBase.USER_DIRECTORY_CONFIG, applicationBaseDirectory ) + \
               "/" + \
               configBaseFile + \
               IndicatorBase.JSON_EXTENSION


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
    def __getUserDirectory( self, XDGKey, userBaseDirectory, applicationBaseDirectory ):
        if XDGKey in os.environ:
            directory = os.environ[ XDGKey ] + "/" + applicationBaseDirectory

        else:
            directory = os.path.expanduser( "~" ) + "/" + userBaseDirectory + "/" + applicationBaseDirectory

        if not os.path.isdir( directory ):
            os.mkdir( directory )

        return directory


# Log file handler which truncates the file when the file size limit is reached.
#
# References:
#     http://stackoverflow.com/questions/24157278/limit-python-log-file
#     http://svn.python.org/view/python/trunk/Lib/logging/handlers.py?view=markup
class TruncatedFileHandler( logging.handlers.RotatingFileHandler ):
    def __init__( self, filename, maxBytes = 10000 ): super().__init__( filename, "a", maxBytes, 0, None, True )


    def doRollover( self ):
        if self.stream:
            self.stream.close()

        if os.path.exists( self.baseFilename ):
            os.remove( self.baseFilename )

        self.mode = "a"
        self.stream = self._open()