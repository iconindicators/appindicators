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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Base class for application indicators.
#
# References:
#     http://python-gtk-3-tutorial.readthedocs.org
#     http://wiki.gnome.org/Projects/PyGObject/Threading
#     http://wiki.ubuntu.com/NotifyOSD
#     http://lazka.github.io/pgi-docs/AppIndicator3-0.1


#TODO Check on Ubuntu 20.04 if there is a dark and light Yaru theme, using tweaks.
# There is a standard, light and dark setting for Yaru.
# However there seems to be only one icon set and the icons don't seem to change when changed from standard to light/dark.
# The icons which are displayed in the indicators (not sure which theme is used) are darker than the Yaru icons for network/audio/power.


#TODO Why do the icons appear to change shade/colour depending on the window touching the top panel or not?
# https://askubuntu.com/questions/1114601/icons-change-colour-on-ubuntu-18-04-depending-on-window-state


import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "GLib", "2.0" )
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from abc import ABC
from gi.repository import AppIndicator3, GLib, Gtk, Notify

import datetime, gzip, json, logging.handlers, os, pickle, shutil, subprocess


class IndicatorBase( ABC ):

    # Private
    __AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    __CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"
    __DIALOG_DEFAULT_HEIGHT = 480
    __DIALOG_DEFAULT_WIDTH = 640
    __JSON_EXTENSION = ".json"
    __TERMINAL_GNOME = "gnome-terminal"
    __TERMINAL_LXDE = "lxterminal"
    __TERMINAL_XFCE = "xfce4-terminal"

    # Public
    INDENT_TEXT_LEFT = 25
    INDENT_WIDGET_LEFT = 20
    URL_TIMEOUT_IN_SECONDS = 5


    def __init__( self, indicatorName, version, copyrightStartYear, comments, artwork = None, creditz = None, debug = False ):
        self.indicatorName = indicatorName
        self.version = version
        self.copyrightStartYear = copyrightStartYear
        self.comments = comments

        self.desktopFile = self.indicatorName + ".py.desktop"
        self.icon = self.indicatorName # Located in /usr/share/icons
        self.log = os.getenv( "HOME" ) + "/" + self.indicatorName + ".log"
        self.website = "https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa"

        self.authors = [ "Bernard Giannetti" + " " + self.website ]
        self.artwork = artwork if artwork else self.authors
        self.creditz = creditz
        self.debug = debug

        self.secondaryActivateTarget = None
        self.updateTimerID = None

        logging.basicConfig(
            format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level = logging.DEBUG,
            handlers = [ TruncatedFileHandler( self.log ) ] )

        Notify.init( self.indicatorName )

        menu = Gtk.Menu()
        menu.append( Gtk.MenuItem.new_with_label( _( "Initialising..." ) ) )
        menu.show_all()

        self.indicator = AppIndicator3.Indicator.new(
                            self.indicatorName, #ID
                            self.indicatorName, # Icon name
                            AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.set_menu( menu )

        self.__loadConfig()


    def main( self ):
        GLib.idle_add( self.__update )
        Gtk.main()


    def __update( self ):
        # If the About/Preferences menu items are disabled as the update kicks off,
        # the user interface will not reflect the change until the update completes.
        # Therefore, disable the About/Preferences menu items and run the remaining update in a new and delayed thread.
        self.__setMenuSensitivity( False )
        GLib.timeout_add_seconds( 1, self.__updateInternal )


    def __updateInternal( self ):
        menu = Gtk.Menu()
        self.secondaryActivateTarget = None
        nextUpdateInSeconds = self.update( menu ) # Call to implementation in indicator.

        if self.debug:
            nextUpdateDateTime = datetime.datetime.now() + datetime.timedelta( seconds = nextUpdateInSeconds )
            menu.prepend( Gtk.MenuItem.new_with_label( "Next update: " + str( nextUpdateDateTime ).split( '.' )[ 0 ] ) )

        if len( menu.get_children() ) > 0:
            menu.append( Gtk.SeparatorMenuItem() )

        # Add in common menu items.
        menuItem = Gtk.MenuItem.new_with_label( _( "Preferences" ) )
        menuItem.connect( "activate", self.__onPreferences )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "About" ) )
        menuItem.connect( "activate", self.__onAbout )
        menu.append( menuItem )

        menuItem = Gtk.MenuItem.new_with_label( _( "Quit" ) )
        menuItem.connect( "activate", Gtk.main_quit )
        menu.append( menuItem )

        self.indicator.set_menu( menu )
        menu.show_all()

        if self.secondaryActivateTarget:
            self.indicator.set_secondary_activate_target( self.secondaryActivateTarget )

        if nextUpdateInSeconds: # Some indicators don't return a next update time.
            self.updateTimerID = GLib.timeout_add_seconds( nextUpdateInSeconds, self.__update )
            self.nextUpdateTime = datetime.datetime.utcnow() + datetime.timedelta( seconds = nextUpdateInSeconds )

        else:
            self.nextUpdateTime = None


    def requestUpdate( self, delay = 0 ): GLib.timeout_add_seconds( delay, self.__update )


    def requestMouseWheelScrollEvents( self ): self.indicator.connect( "scroll-event", self.__onMouseWheelScroll )


    def __onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        # Need to ignore events when Preferences is open or an update is underway.
        # Do so by checking the sensitivity of the Preferences menu item.
        # A side effect is the event will be ignored when About is showing...oh well.
        if self.__getMenuSensitivity():
            self.onMouseWheelScroll( indicator, delta, scrollDirection )


    def __onAbout( self, widget ):
        self.__setMenuSensitivity( False )
        GLib.idle_add( self.__onAboutInternal, widget )


    def __onAboutInternal( self, widget ):
        aboutDialog = Gtk.AboutDialog()
        aboutDialog.set_transient_for( widget.get_parent().get_parent() )
        aboutDialog.set_artists( self.artwork )
        aboutDialog.set_authors( self.authors )
        aboutDialog.set_comments( self.comments )

        copyrightText = "Copyright \xa9 " + \
                        self.copyrightStartYear + "-" + str( datetime.datetime.now().year ) + " " + \
                        self.authors[ 0 ].rsplit( ' ', 1 )[ 0 ]

        aboutDialog.set_copyright( copyrightText )
        aboutDialog.set_license_type( Gtk.License.GPL_3_0 )
        aboutDialog.set_logo_icon_name( self.indicatorName )
        aboutDialog.set_program_name( self.indicatorName )
        aboutDialog.set_translator_credits( _( "translator-credits" ) )
        aboutDialog.set_version( self.version )
        aboutDialog.set_website( self.website )
        aboutDialog.set_website_label( self.website )

        if self.creditz:
            aboutDialog.add_credit_section( _( "Credits" ), self.creditz )

        changeLog = self.__getCacheDirectory() + self.indicatorName + ".changelog"
        changeLogGzipped = "/usr/share/doc/" + self.indicatorName + "/changelog.Debian.gz"
        with gzip.open( changeLogGzipped, 'r' ) as fileIn, open( changeLog, 'wb' ) as fileOut:
            shutil.copyfileobj( fileIn, fileOut )

        self.__addHyperlinkLabel( aboutDialog, changeLog, _( "View the" ), _( "changelog" ), _( "text file." ) )

        errorLog = os.getenv( "HOME" ) + "/" + self.indicatorName + ".log"
        if os.path.exists( errorLog ):
            self.__addHyperlinkLabel( aboutDialog, errorLog, _( "View the" ), _( "error log" ), _( "text file." ) )

        aboutDialog.run()
        aboutDialog.destroy()
        os.remove( changeLog )
        self.__setMenuSensitivity( True )


    def __addHyperlinkLabel( self, aboutDialog, filePath, leftText, anchorText, rightText ):
        toolTip = "file://" + filePath
        markup = leftText + " <a href=\'" + "file://" + filePath + "\' title=\'" + toolTip + "\'>" + anchorText + "</a> " + rightText
        label = Gtk.Label()
        label.set_markup( markup )
        label.show()
        aboutDialog.get_content_area().get_children()[ 0 ].get_children()[ 2 ].get_children()[ 0 ].add( label )


    def __onPreferences( self, widget ):
        if self.updateTimerID:
            GLib.source_remove( self.updateTimerID )
            self.updateTimerID = None

        self.__setMenuSensitivity( False )
        GLib.idle_add( self.__onPreferencesInternal, widget )


    def __onPreferencesInternal( self, widget ):
        dialog = self.createDialog( widget, _( "Preferences" ) )
        responseType = self.onPreferences( dialog ) # Call to implementation in indicator.
        dialog.destroy()
        self.__setMenuSensitivity( True )

        if responseType == Gtk.ResponseType.OK:
            self.__saveConfig()
            GLib.idle_add( self.__update )

        elif self.nextUpdateTime: # User cancelled and there is a next update time present...
            secondsToNextUpdate = ( self.nextUpdateTime - datetime.datetime.utcnow() ).total_seconds()
            if secondsToNextUpdate > 10: # Scheduled update is still in the future (10 seconds or more), so reschedule...
                GLib.timeout_add_seconds( int( secondsToNextUpdate ), self.__update )

            else: # Scheduled update would have already happened, so kick one off now.
                GLib.idle_add( self.__update )


    def __setMenuSensitivity( self, toggle, allMenuItems = False ):
        if allMenuItems:
            for menuItem in self.indicator.get_menu().get_children():
                menuItem.set_sensitive( toggle )

        else:
            menuItems = self.indicator.get_menu().get_children()
            if len( menuItems ) > 1: # On the first update, the menu only contains a single "initialising" menu item. 
                menuItems[ -1 ].set_sensitive( toggle ) # Quit
                menuItems[ -2 ].set_sensitive( toggle ) # About
                menuItems[ -3 ].set_sensitive( toggle ) # Preferences


    def __getMenuSensitivity( self ):
        sensitive = False
        menuItems = self.indicator.get_menu().get_children()
        if len( menuItems ) > 1: # On the first update, the menu only contains a single "initialising" menu item.
            sensitive = menuItems[ -1 ].get_sensitive() # Quit menu item; no need to check for About/Preferences.

        return sensitive


    def createDialog( self, parentWidget, title, grid = None ):
        dialog = Gtk.Dialog(
            title,
            self.__getParent( parentWidget ),
            Gtk.DialogFlags.MODAL,
            ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )

        dialog.set_border_width( 5 )
        if grid:
            dialog.vbox.pack_start( grid, True, True, 0 )

        return dialog


    def createDialogExternalToAboutOrPreferences( self, parentWidget, title, contentWidget, setDefaultSize = False ):
        self.__setMenuSensitivity( False, True )
        GLib.idle_add( self.__createDialogExternalToAboutOrPreferences, parentWidget, title, contentWidget, setDefaultSize )


    def __createDialogExternalToAboutOrPreferences( self, parentWidget, title, contentWidget, setDefaultSize = False ):
        dialog = Gtk.Dialog(
            title,
            self.__getParent( parentWidget ),
            Gtk.DialogFlags.MODAL,
            ( Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE ) )

        if setDefaultSize:
            dialog.set_default_size( IndicatorBase.__DIALOG_DEFAULT_WIDTH, IndicatorBase.__DIALOG_DEFAULT_HEIGHT )

        dialog.set_border_width( 5 )
        dialog.vbox.pack_start( contentWidget, True, True, 0 )
        dialog.show_all()
        dialog.run()
        dialog.destroy()
        self.__setMenuSensitivity( True, True )


    def createAutostartCheckbox( self ):
        autostartCheckbox = Gtk.CheckButton.new_with_label( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( self.isAutoStart() )
        autostartCheckbox.set_margin_top( 10 )
        return autostartCheckbox


    # Show a message dialog.
    #
    #    messageType: One of Gtk.MessageType.INFO, Gtk.MessageType.ERROR, Gtk.MessageType.WARNING, Gtk.MessageType.QUESTION.
    #    title: If None, will default to the indicator name.
    def showMessage( self, parentWidget, message, messageType = Gtk.MessageType.ERROR, title = None ):
        dialog = Gtk.MessageDialog( self.__getParent( parentWidget ), Gtk.DialogFlags.MODAL, messageType, Gtk.ButtonsType.OK, message )
        if title is None:
            dialog.set_title( self.indicatorName )

        else:
            dialog.set_title( title )

        dialog.run()
        dialog.destroy()


    # Show OK/Cancel dialog prompt.
    #
    #    title: If None, will default to the indicator name.
    #
    # Return either Gtk.ResponseType.OK or Gtk.ResponseType.CANCEL.
    def showOKCancel( self, parentWidget, message, title = None ):
        dialog = Gtk.MessageDialog(
                    self.__getParent( parentWidget ),
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.OK_CANCEL,
                    message )

        if title is None:
            dialog.set_title( self.indicatorName )

        else:
            dialog.set_title( title )

        response = dialog.run()
        dialog.destroy()
        return response


    def __getParent( self, widget ):
        parent = widget # Sometimes the widget itself is a Dialog/Window, so no need to get the parent.
        while( parent is not None ):
            if isinstance( parent, ( Gtk.Dialog, Gtk.Window ) ):
                break

            parent = parent.get_parent()

        return parent


    # Takes a Gtk.TextView and returns the containing text, avoiding the additional calls to get the start/end positions.
    def getTextViewText( self, textView ):
        textViewBuffer = textView.get_buffer()
        return textViewBuffer.get_text( textViewBuffer.get_start_iter(), textViewBuffer.get_end_iter(), True )


    # Listens to checkbox events and toggles the visibility of the widgets.
    def onCheckbox( self, checkbox, *widgets ):
        for widget in widgets:
            widget.set_sensitive( checkbox.get_active() )


    # Listens to radio events and toggles the visibility of the widgets.
    def onRadio( self, radio, *widgets ):
        for widget in widgets:
            widget.set_sensitive( radio.get_active() )


    def isUbuntu1604( self ): return self.processGet( "lsb_release -sc" ).strip() == "xenial"


    # Makes a guess at how many menu items will fit into an indicator menu.
    #
    # By experiment under Unity, a screen height of 900 pixels accommodates 37 menu items before a scroll bar appears.
    # For an initial guess, compute a divisor: 900 / 37 = 25.
    #
    # For GNOME Shell, the equivalent divisor is 36.
    def getMenuItemsGuess( self ):
        if self.isUbuntu1604():
            guess = Gtk.Window().get_screen().get_height() / 25

        else:
            guess = Gtk.Window().get_screen().get_height() / 36

        return guess


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


    # Menu item indent spacing, given Ubuntu 16.04 (Unity) and Ubuntu 18.04+ (GNOME Shell) differences.
    def indent( self, indentUnity, indentGnomeShell ):
        INDENT = "      "
        if self.isUbuntu1604():
            indent = INDENT * indentUnity

        else:
            indent = INDENT * indentGnomeShell

        return indent


    def getThemeName( self ): return Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )


    # Get the colour (in hexadecimal) for the current theme.
    # The defaultColour will be returned if the current theme has no colour defined.
    def getThemeColour( self, defaultColour ):
        themeNames = { "Adwaita"                : "bebebe",
                       "elementary-xfce-darker" : "f3f3f3",
                       "Lubuntu"                : "4c4c4c",
                       "ubuntu-mono-dark"       : "dfdbd2",
                       "ubuntu-mono-light"      : "3c3c3c",
                       "Yaru"                   : "dbdbdb" }

        themeName = self.getThemeName()
        if themeName in themeNames:
            themeColour = themeNames[ themeName ]

        else:
            themeColour = defaultColour

        return themeColour


    def isAutoStart( self ):
        try:
            autoStart = \
                os.path.exists( IndicatorBase.__AUTOSTART_PATH + self.desktopFile ) and \
                "X-GNOME-Autostart-enabled=true" in open( IndicatorBase.__AUTOSTART_PATH + self.desktopFile ).read()

        except Exception as e:
            logging.exception( e )
            autoStart = False

        return autoStart


    def setAutoStart( self, isSet ):
        if not os.path.exists( IndicatorBase.__AUTOSTART_PATH ):
            os.makedirs( IndicatorBase.__AUTOSTART_PATH )

        try:
            if isSet:
                shutil.copy( "/usr/share/applications/" + self.desktopFile, IndicatorBase.__AUTOSTART_PATH + self.desktopFile )

            else:
                if os.path.exists( IndicatorBase.__AUTOSTART_PATH + self.desktopFile ):
                    os.remove( IndicatorBase.__AUTOSTART_PATH + self.desktopFile )

        except Exception as e:
            logging.exception( e )


    def getLogging( self ): return logging


    # Returns True if a number; False otherwise.
    def isNumber( self, numberAsString ):
        try:
            float( numberAsString )
            return True

        except ValueError:
            return False


    # Return the full path and name of the executable for the current terminal; None on failure.
    def getTerminal( self ):
        terminal = self.processGet( "which " + IndicatorBase.__TERMINAL_GNOME )
        if terminal is None:
            terminal = self.processGet( "which " + IndicatorBase.__TERMINAL_LXDE )

            if terminal is None:
                terminal = self.processGet( "which " + IndicatorBase.__TERMINAL_XFCE )

        if terminal:
            terminal = terminal.strip()

        if terminal == "":
            terminal = None

        return terminal


    # Return the execution flag for the given terminal; None on failure.
    def getTerminalExecutionFlag( self, terminal ):
        executionFlag = None
        if terminal:
            if terminal.endswith( IndicatorBase.__TERMINAL_GNOME ):
                executionFlag = "--"

            elif terminal.endswith( IndicatorBase.__TERMINAL_LXDE ):
                executionFlag = "-e"

            elif terminal.endswith( IndicatorBase.__TERMINAL_XFCE ):
                executionFlag = "-x"

        return executionFlag


    def listOfListsToListStore( self, listofLists ):
        types = [ ]
        for item in listofLists[ 0 ]:
            types.append( type( item[ 0 ] ) )

        listStore = Gtk.ListStore()
        listStore.set_column_types( types )
        for item in listofLists:
            listStore.append( item )

        return listStore


    def requestSaveConfig( self, delay = 0 ):  GLib.timeout_add_seconds( delay, self.__saveConfig, False )


    # Read a dictionary of configuration from a JSON text file.
    def __loadConfig( self ):
        configFile = self.__getConfigDirectory() + self.indicatorName + IndicatorBase.__JSON_EXTENSION
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
    #
    # returnStatus If True, will return a boolean indicating success/failure.
    #              If False, no return call is made (useful for calls to GLib idle_add/timeout_add_seconds.
    def __saveConfig( self, returnStatus = True ):
        config = self.saveConfig() # Call to implementation in indicator.
        configFile = self.__getConfigDirectory() + self.indicatorName + IndicatorBase.__JSON_EXTENSION
        success = True
        try:
            with open( configFile, "w" ) as f:
                f.write( json.dumps( config ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing configuration: " + configFile )
            success = False

        if returnStatus:
            return success


    # Return the full directory path to the user config directory for the current indicator.
    def __getConfigDirectory( self ): return self.__getUserDirectory( "XDG_CONFIG_HOME", ".config", self.indicatorName )


    # Obtain the full path to a cache file, creating the underlying path if necessary.
    #
    # filename: The file name.
    def getCachePath( self, filename ): return self.__getCacheDirectory() + filename


    # Remove a file from the cache.
    #
    # fileName: The file to remove.
    #
    # The file removed will be either
    #     ${XDGKey}/applicationBaseDirectory/fileName
    # or
    #     ~/.cache/applicationBaseDirectory/fileName
    def removeFileFromCache( self, fileName ):
        cacheDirectory = self.__getCacheDirectory()
        for file in os.listdir( cacheDirectory ):
            if file == fileName:
                os.remove( cacheDirectory + file )


    # Removes out of date cache files.
    #
    # baseName: The text used to form the file name, typically the name of the calling application.
    # cacheMaximumAgeInHours: Anything older than the maximum age (hours) is deleted.
    #
    # Any file in the cache directory matching the pattern
    #
    #     ${XDGKey}/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    # or
    #     ~/.cache/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    #
    # and is older than the cache maximum age is discarded.
    def removeOldFilesFromCache( self, baseName, cacheMaximumAgeInHours ):
        cacheDirectory = self.__getCacheDirectory()
        cacheMaximumAgeDateTime = datetime.datetime.utcnow() - datetime.timedelta( hours = cacheMaximumAgeInHours )
        for file in os.listdir( cacheDirectory ):
            if file.startswith( baseName ): # Sometimes the base name is shared ("icon-" versus "icon-fullmoon-") so use the date/time to ensure the correct group of files.
                dateTime = file[ len( baseName ) : len( baseName ) + 14 ] # YYMMDDHHMMSS is 14 characters.
                if dateTime.isdigit():
                    fileDateTime = datetime.datetime.strptime( dateTime, IndicatorBase.__CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
                    if fileDateTime < cacheMaximumAgeDateTime:
                        os.remove( cacheDirectory + file )


    # Find the date/time of the newest file in the cache matching the basename.
    #
    # baseName: The text used to form the file name, typically the name of the calling application.
    #
    # Returns the datetime of the newest file in the cache.  None if no file can be found.
    def getCacheDateTime( self, baseName ):
        cacheDirectory = self.__getCacheDirectory()
        expiry = None
        theFile = ""
        for file in os.listdir( cacheDirectory ):
            if file.startswith( baseName ) and file > theFile:
                theFile = file

        if theFile: # A value of "" evaluates to False.
            expiry = datetime.datetime.strptime( theFile[ len( theFile ) - 14 : ], IndicatorBase.__CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )

        return expiry


    # Read the most recent binary object from the cache.
    #
    # baseName: The text used to form the file name, typically the name of the calling application.
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
    def readCacheBinary( self, baseName ):
        cacheDirectory = self.__getCacheDirectory()
        data = None
        theFile = ""
        for file in os.listdir( cacheDirectory ):
            if file.startswith( baseName ) and file > theFile:
                theFile = file

        if theFile: # A value of "" evaluates to False.
            filename = cacheDirectory + theFile
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
    # baseName: The text used to form the file name, typically the name of the calling application.
    # binaryData: The object to write.
    #
    # The object will be written to the cache directory using the pattern
    #     ${XDGKey}/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    # or
    #     ~/.cache/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    #
    # Returns True on success; False otherwise.
    def writeCacheBinary( self, baseName, binaryData ):
        success = True
        cacheFile = \
            self.__getCacheDirectory() + \
            baseName + \
            datetime.datetime.utcnow().strftime( IndicatorBase.__CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )

        try:
            with open( cacheFile, "wb" ) as f:
                pickle.dump( binaryData, f )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing to cache: " + cacheFile )
            success = False

        return success


    # Read a text file from the cache.
    #
    # fileName: The file name of the text file.
    #
    # Returns the text contents or None on error.
    def readCacheText( self, fileName ):
        cacheFile = self.__getCacheDirectory() + fileName
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
    # fileNameOrBaseName: The file name of the text file or the base name of the text file.
    # text: The text to write.
    # isFileName: If True (default), the full file name is provided by the caller, otherwise only the base name.
    # extension: The file extension (without period).
    #
    # Returns the full path and file name on success, None otherwise.
    def writeCacheText( self, fileNameOrBaseName, text, isFileName = True, extension = None ):
        if isFileName:
            cacheFile = self.__getCacheDirectory() + fileNameOrBaseName

        else:
            cacheFile = \
                self.__getCacheDirectory() + \
                fileNameOrBaseName + \
                datetime.datetime.utcnow().strftime( IndicatorBase.__CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )

        if extension is not None:
            cacheFile += "." + extension

        try:
            with open( cacheFile, "w" ) as f:
                f.write( text )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing to cache: " + cacheFile )
            cacheFile = None

        return cacheFile


    # Return the full directory path to the user cache directory for the current indicator.
    def __getCacheDirectory( self ): return self.__getUserDirectory( "XDG_CACHE_HOME", ".cache", self.indicatorName )


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
            directory = os.environ[ XDGKey ] + "/" + applicationBaseDirectory + "/"

        else:
            directory = os.path.expanduser( "~" ) + "/" + userBaseDirectory + "/" + applicationBaseDirectory + "/"

        if not os.path.isdir( directory ):
            os.mkdir( directory )

        return directory


    # Calls the command in a new process; quietly fails.
    def processCall( self, command ):
        try:
            subprocess.call( command, shell = True )

        except subprocess.CalledProcessError:
            pass


    # Returns the result of calling the command.  On exception, returns None.
    def processGet( self, command ):
        result = None
        try:
            result = subprocess.check_output( command, shell = True, universal_newlines = True )

        except subprocess.CalledProcessError:
            result = None

        return result


# Log file handler which truncates the file when the file size limit is reached.
#
# References:
#     http://stackoverflow.com/questions/24157278/limit-python-log-file
#     http://svn.python.org/view/python/trunk/Lib/logging/handlers.py?view=markup
class TruncatedFileHandler( logging.handlers.RotatingFileHandler ):
    def __init__( self, filename, maxBytes = 10000 ):
        super().__init__( filename, "a", maxBytes, 0, None, True )


    def doRollover( self ):
        if self.stream:
            self.stream.close()

        if os.path.exists( self.baseFilename ):
            os.remove( self.baseFilename )

        self.mode = "a"
        self.stream = self._open()