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
#
# References:
#     http://python-gtk-3-tutorial.readthedocs.org
#     http://wiki.gnome.org/Projects/PyGObject/Threading
#     http://wiki.ubuntu.com/NotifyOSD
#     http://lazka.github.io/pgi-docs/AppIndicator3-0.1


import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "GLib", "2.0" )
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import AppIndicator3, GLib, Gtk, Notify
import datetime, gzip, json, logging.handlers, os, pickle, shutil, subprocess, threading


class IndicatorBase:

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"
    INDENT_TEXT_LEFT = 25
    INDENT_WIDGET_LEFT = 20
    JSON_EXTENSION = ".json"
    TERMINAL_GNOME = "gnome-terminal"
    TERMINAL_LXDE = "lxterminal"
    TERMINAL_XFCE = "xfce4-terminal"
    URL_TIMEOUT_IN_SECONDS = 2


    def __init__( self, indicatorName, version, copyrightStartYear, comments, artwork = None, creditz = None ):
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

        self.lock = threading.Lock()
        self.updateTimerID = None
        self.startingUp = True

        logging.basicConfig( 
            format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
            level = logging.DEBUG, 
            handlers = [ TruncatedFileHandler( self.log ) ] )

        Notify.init( self.indicatorName )

        menu = Gtk.Menu()
#TODO Need to regenerate the POT file and have Oleg translate the string below.
        menu.append( Gtk.MenuItem( _( "Initialising..." ) ) )
        menu.show_all()

        self.indicator = AppIndicator3.Indicator.new( self.indicatorName, self.indicatorName, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.set_menu( menu )

        self.__loadConfig()


    def main( self ):
#         GLib.timeout_add_seconds( 1, self.__update )
#TODO Test this on the laptop and ensure things still work...
        GLib.idle_add( self.__update )

#         self.__update()
#         self.startingUp = False
        Gtk.main()


    def __updateORIG( self ):
        with self.lock:
            menu = Gtk.Menu()
            self.indicator.set_menu( menu )
            nextUpdateInSeconds = self.update( menu ) # Call to implementation in indicator.
            self.__finaliseMenu( menu )
            if nextUpdateInSeconds: # Some indicators don't return a next update time.
                self.updateTimerID = GLib.timeout_add_seconds( nextUpdateInSeconds, self.__update )


    def __updateORIG( self ):
        # Convoluted way to allow the About/Preferences menu items to be disabled during an update.
        # If the update takes place in a single function, the menu items would only be disabled when the function returns.
        # Therefore, do the disable and return immediately, then finish off the update slightly delayed.
        if self.startingUp:
            self.__updateInternal()

        else:
            self.__setAboutPreferencesSensitivity( False )
            GLib.idle_add( self.__updateInternal )


    def __update( self ):
        # If the About/Preferences menu items are disabled as the update kicks off,
        # the user interface will not reflect the change until the update completes.
        # Therefore, disable the About/Preferences menu items and run the remaining update in a new and delayed thread.
        self.__setAboutPreferencesSensitivity( False )
        GLib.timeout_add_seconds( 1, self.__updateInternal )


    def __updateInternal( self ):
        utcNow = datetime.datetime.utcnow() #TODO Remove
        menu = Gtk.Menu()
        nextUpdateInSeconds = self.update( menu ) # Call to implementation in indicator.
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

        self.indicator.set_menu( menu )
        menu.show_all()

        if nextUpdateInSeconds: # Some indicators don't return a next update time.
            self.updateTimerID = GLib.timeout_add_seconds( nextUpdateInSeconds, self.__update )
            self.nextUpdateTime = datetime.datetime.utcnow() + datetime.timedelta( seconds = nextUpdateInSeconds )

        else:
            self.nextUpdateTime = None

#TODO Testing
        print( "Update duration:", ( ( datetime.datetime.utcnow() - utcNow ).total_seconds() ) )
        print( "Next update in seconds:", nextUpdateInSeconds )                
        print( "Next update time:", self.nextUpdateTime )


#TODO If we disable About/Preferences...can we still Quit (during startup for Lunar) or refresh for any indicator?
    def __updateNEW( self ):
#TODO Testing
#         if self.startingUp:
#             print( "__update starting up")
#             menu = Gtk.Menu()
#             menu = self.indicator.get_menu()
#             menuItems = menu.get_children()
#             menuItem = menuItems[ -2 ]
#             menuItems[ -2 ].set_sensitive( False )
#             menuItems[ -3 ].set_sensitive( False )

        with self.lock:
            if not self.startingUp:
#                 self.__setAboutPreferencesSensitivity( False )
                GLib.idle_add( self.__setAboutPreferencesSensitivity, False )
                import time
                time.sleep( 5 )
#                 return #TODO If we return then the about/prefs get disabled.  This means the code below is so intensive, the disabling takes too long to take effect.
#             if not self.startingUp:
#                 print( "__update not starting up")
#                 menu = self.indicator.get_menu()
#                 menuItems = menu.get_children()#         GLib.idle_add( self.internal, toggle )
#                 menuItems[ -2 ].set_sensitive( False ) # About
#                 menuItems[ -3 ].set_sensitive( False ) # Preferences

#             print( "Starting up:", self.startingUp)

            menu = Gtk.Menu()
            nextUpdateInSeconds = self.update( menu ) # Call to implementation in indicator.
            self.__finaliseMenu( menu )
            if nextUpdateInSeconds: # Some indicators don't return a next update time.
                self.updateTimerID = GLib.timeout_add_seconds( nextUpdateInSeconds, self.__update )
                self.nextUpdateTime = datetime.datetime.utcnow() + datetime.timedelta( seconds = nextUpdateInSeconds )

            else:
                self.nextUpdateTime = None

            print( "Next update in seconds:", nextUpdateInSeconds )                
            print( "Next update time:", self.nextUpdateTime )


#TODO SHould this be wrapped in
#             GLib.idle_add( self.requestUpdate )
# as is with request to save config.
# Look at the calls using timeout too.
    def requestUpdate( self ): self.__update()


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

        self.indicator.set_menu( menu )
        menu.show_all()


    def requestMouseWheelScrollEvents( self ): self.indicator.connect( "scroll-event", self.__onMouseWheelScroll )


    def __onMouseWheelScroll( self, indicator, delta, scrollDirection ):
#TODO Why do we have a lock here?
        with self.lock:
            self.onMouseWheelScroll( indicator, delta, scrollDirection )


#TODO Don't like how an update happens...
#...work out why we have to cancel and why we have to do an update.
# 
#
# Currently I have two situations that I have solved, but has the side
# effect you have just mentioned.
# 
# Situation 1: Only allow one of the About OR Preferences to display at a
# time; never simultaneously.  If we allow both to display, the second
# dialog to display grabs the focus from the first dialog to display.
# 
# Situation 2: Most indicators use a timer to run a periodic refresh (of
# the internals and then menu build).  Indicator Lunar is a great
# example.  All indicators except Punycode and Script Runner have
# update/refresh loops.  Now if a user runs the Preferences, I want to
# disable the refresh from happening and then kick off a refresh when the
# Preferences is closed.
# 
# I use a single thread lock to handle both situations, but there are side
# effects:
# 
# Side Effect 1: When the Preferences is closed, if the user clicked
# Cancel, the refresh still kicks off (only refresh if the user changed
# something).
# 
# Side Effect 2: Because of the single thread lock, the About dialog also
# kicks off a refresh when closed.
# 
# So I am rethinking the situation...
# 
# My initial thoughts (scrambled up and unclear at this stage) are:
# 
# 1) I could grey-out (deactivate) the About and Preferences menu items
# when either the About or Preferences is displayed.   This stops the user
# from running the other dialog.  When the dialog is closed, re-enable
# those menu items.
# 
# 2) When the Preferences is opened, disable the update timer (which kicks
# off the refresh).  I think regardless of the user hitting the OK or
# Cancel, I would have to run the update no matter what (too difficult to
# figure out when the update would have occurred in the future).  Maybe I
# can get GTK to give me information about when the update timer was due
# to run.
# 
# 3) If the About dialog is displayed, the update timer can stay in
# place.  So the About dialog is independent of updates.
# 
# 4) If an update is underway (could take a minute or so on my old laptop
# for Indicator Lunar), the Preferences will not display (not sure if I
# should disable Preferences menu item during the update).
# 
# Not sure if the above yet makes sense; only just today started thinking
# about it all.  However I suspect now having a base class makes it so
# much easier to roll out changes like this to all indicators in one go.


# When a refresh happens, disable the Preferences menu item.
# When the refresh finishes, enable the Preferences menu item.
#
# When the About is selected, disable About and Preferences.
# When About is closed, enable About.
# Only enable Preferences if update is not running.
#
# When Preferences is selected, disable About and Preferences.
# When Preferences is closed, enable About.
# If Preferences OK was selected, remove any existing timer and do a refresh.


    def __onAbout( self, widget ):
        self.__setAboutPreferencesSensitivity( False )
#         GLib.timeout_add_seconds( 1, self.__onAboutInternal, widget )
#TODO Test this on the laptop and ensure the menu items are disabled in time!
        GLib.idle_add( self.__onAboutInternal, widget )


    def __onAboutInternal( self, widget ):
#         if self.lock.acquire( blocking = False ):
#             if self.updateTimerID:
#                 GLib.source_remove( self.updateTimerID )

        aboutDialog = Gtk.AboutDialog()
        aboutDialog.set_transient_for( widget.get_parent().get_parent() )
        aboutDialog.set_artists( self.artwork )
        aboutDialog.set_authors( self.authors )
        aboutDialog.set_comments( self.comments )

        copyrightText = \
            "Copyright \xa9 " + \
            self.copyrightStartYear + \
            "-" + \
            str( datetime.datetime.now().year ) + \
            " " + \
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

        self.__setAboutPreferencesSensitivity( True )

#         self.lock.release()
#             GLib.idle_add( self.__update )


    def __onAboutORIG( self, widget ):
        if self.lock.acquire( blocking = False ):
            if self.updateTimerID:
                GLib.source_remove( self.updateTimerID )

            aboutDialog = Gtk.AboutDialog()
            aboutDialog.set_transient_for( widget.get_parent().get_parent() )
            aboutDialog.set_artists( self.artwork )
            aboutDialog.set_authors( self.authors )
            aboutDialog.set_comments( self.comments )

            copyrightText = \
                "Copyright \xa9 " + \
                self.copyrightStartYear + \
                "-" + \
                str( datetime.datetime.now().year ) + \
                " " + \
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
            aboutDialog.hide()

            os.remove( changeLog )

            self.lock.release()
            GLib.idle_add( self.__update )


    def __addHyperlinkLabel( self, aboutDialog, filePath, leftText, anchorText, rightText ):
        notebookOrStack = aboutDialog.get_content_area().get_children()[ 0 ].get_children()[ 2 ]
        if type( notebookOrStack ).__name__ == "Notebook":
            notebookOrStack = notebookOrStack.get_nth_page( 0 )
            print( "Notebook")#TODO Remvoe if not used on both laptop and desktop

        else:
            notebookOrStack = notebookOrStack.get_children()[ 0 ]
            print("Stack") #TODO Remvoe if not used on both laptop and desktop (desktop uses stack).

        toolTip = "file://" + filePath
        label = Gtk.Label()
        label.set_markup( leftText + " <a href=\'" + "file://" + filePath + "\' title=\'" + toolTip + "\'>" + anchorText + "</a> " + rightText )
        label.show()
        notebookOrStack.add( label )


    def __onPreferences( self, widget ):
        self.__setAboutPreferencesSensitivity( False )
#         GLib.timeout_add_seconds( 1, self.__onPreferencesInternal, widget )
#TODO Test this on the laptop and ensure the menu items are disabled in time!
        GLib.idle_add( self.__onPreferencesInternal, widget )


    def __onPreferencesInternal( self, widget ):
#         if self.lock.acquire( blocking = False ): #TODO May not need the locking any more???
        if self.updateTimerID: #TODO Still need this?  If we remove the lock it is possible the update could kick off whilst we are open...that's bad!
            GLib.source_remove( self.updateTimerID ) #TODO Maybe do this in the function above?  If so, make it the first thing to do.

        dialog = self.createDialog( widget, _( "Preferences" ) )
        self.onPreferences( dialog ) # Call to implementation in indicator.
        dialog.destroy()
        self.__setAboutPreferencesSensitivity( True )
#        self.lock.release()
        GLib.idle_add( self.__update ) #TODO Work out if we hit OK and only then do we call update.


    def __onPreferencesORIG( self, widget ):
        print( "__onPreferences")#TODO Testing
        if self.lock.acquire( blocking = False ):
            if self.updateTimerID:
                GLib.source_remove( self.updateTimerID )

            dialog = Gtk.Dialog(
                        _( "Preferences" ),
                        self.__getParent( widget ),
                        Gtk.DialogFlags.MODAL,
                        ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )

            dialog.set_border_width( 5 )
            self.onPreferences( dialog ) # Call to implementation in indicator.
            dialog.destroy()
            self.lock.release()
            GLib.idle_add( self.__update )


#TODO In Punycode, when items are disabled,
# convert is enabled...should I really disable all menu items?
# Best check every indicator!
    def __setAboutPreferencesSensitivity( self, toggle ):
        menuItems = self.indicator.get_menu().get_children()
        if len( menuItems ) > 1: # On the first update, the menu only contains a single "initialising" menu item. 
            menuItems[ -2 ].set_sensitive( toggle ) # About
            menuItems[ -3 ].set_sensitive( toggle ) # Preferences


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


    # Show a message dialog.
    #
    #    messageType: One of Gtk.MessageType.INFO, Gtk.MessageType.ERROR, Gtk.MessageType.WARNING, Gtk.MessageType.QUESTION.
    def showMessage( self, parentWidget, messageType, message, title ):
        dialog = Gtk.MessageDialog( self.__getParent( parentWidget ), Gtk.DialogFlags.MODAL, messageType, Gtk.ButtonsType.OK, message )
        dialog.set_title( title )
        dialog.run()
        dialog.destroy()


    # Show OK/Cancel dialog prompt.  Return either Gtk.ResponseType.OK or Gtk.ResponseType.CANCEL.
    def showOKCancel( self, parentWidget, message, title ):
        dialog = Gtk.MessageDialog( self.__getParent( parentWidget ), Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, message )
        dialog.set_title( title )
        response = dialog.run()
        dialog.destroy()
        return response


    def __getParent( self, widget ):
        parent = widget.get_parent()
        while( parent is not None ):
            if isinstance( parent, ( Gtk.Dialog, Gtk.Window ) ):
                break

            parent = parent.get_parent()

        return parent


    # Takes a Gtk.TextView and returns the containing text, avoiding the additional calls to get the start/end positions.
    def getTextViewText( self, textView ): return textView.get_buffer().get_text( textView.get_buffer().get_start_iter(), textView.get_buffer().get_end_iter(), True )


    # Listens to checkbox events and toggles the visibility of the widgets.
    def onCheckbox( self, *widgets ):
        for widget in widgets:
            widget.set_sensitive( self.get_active() )


    # Listens to radio events and toggles the visibility of the widgets.
    def onRadio( self, *widgets ):
        for widget in widgets:
            widget.set_sensitive( self.get_active() )


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


    # Provides indent spacing for menu items,
    # given Ubuntu 16.04 (Unity) and Ubuntu 18.04+ (GNOME Shell) differences.
    def indent( self, indentUnity, indentGnomeShell ):
        INDENT = "      "
        if self.isUbuntu1604():
            indent = INDENT * indentUnity

        else:
            indent = INDENT * indentGnomeShell

        return indent


    def isAutoStart( self ):
        autoStart = False
        try:
            autoStart = \
                os.path.exists( IndicatorBase.AUTOSTART_PATH + self.desktopFile ) and \
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
                shutil.copy( "/usr/share/applications/" + self.desktopFile, IndicatorBase.AUTOSTART_PATH + self.desktopFile )

            else:
                if os.path.exists( IndicatorBase.AUTOSTART_PATH + self.desktopFile ):
                    os.remove( IndicatorBase.AUTOSTART_PATH + self.desktopFile )

        except Exception as e:
            logging.exception( e )


    def getThemeName( self ): return Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )


#TODO Verify this works for indicator lunar still.  
#TODO Need a header comment specifying the expectation that a tag with the colour is present in the SVG file.
    def getThemeColour( self, iconName ):
        iconFilenameForCurrentTheme = "/usr/share/icons/" + self.getThemeName() + "/scalable/apps/" + iconName + ".svg"
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
        terminal = self.processGet( "which " + IndicatorBase.TERMINAL_GNOME )
        if terminal is None:
            terminal = self.processGet( "which " + IndicatorBase.TERMINAL_LXDE )

            if terminal is None:
                terminal = self.processGet( "which " + IndicatorBase.TERMINAL_XFCE )

        if terminal:
            terminal = terminal.strip()

        if terminal == "":
            terminal = None

        return terminal


    # Return the execution flag for the given terminal; None on failure. 
    def getTerminalExecutionFlag( self, terminal ): 
        executionFlag = None
        if terminal:
            if terminal.endswith( IndicatorBase.TERMINAL_GNOME ):
                executionFlag = "--"

            elif terminal.endswith( IndicatorBase.TERMINAL_LXDE ):
                executionFlag = "-e"

            elif terminal.endswith( IndicatorBase.TERMINAL_XFCE ):
                executionFlag = "-x"

        return executionFlag


    def requestSaveConfig( self ): self.__saveConfig()


    # Read a dictionary of configuration from a JSON text file.
    def __loadConfig( self ):
        configFile = self.__getConfigDirectory() + self.indicatorName + IndicatorBase.JSON_EXTENSION
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
        configFile = self.__getConfigDirectory() + self.indicatorName + IndicatorBase.JSON_EXTENSION
        success = True
        try:
            with open( configFile, "w" ) as f:
                f.write( json.dumps( config ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing configuration: " + configFile )
            success = False

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
                os.remove( cacheDirectory + "/" + file )


    # Removes out of date cache files.
    #
    # baseName: The text used to form the file name, typically the name of the calling application.
    # cacheMaximumAgeInHours: Anything older than the maximum age (hours) is deleted.
    #
    # Any file in the cache directory matching the pattern
    #     ${XDGKey}/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    # or
    #     ~/.cache/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    # and is older than the cache maximum age is discarded.
    def removeOldFilesFromCache( self, baseName, cacheMaximumAgeInHours ):
        cacheDirectory = self.__getCacheDirectory()
        cacheMaximumAgeDateTime = datetime.datetime.utcnow() - datetime.timedelta( hours = cacheMaximumAgeInHours )
        for file in os.listdir( cacheDirectory ):
            if file.startswith( baseName ):
                fileDateTime = datetime.datetime.strptime( file[ len( baseName ) : ], IndicatorBase.CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )            
                if fileDateTime < cacheMaximumAgeDateTime:
                    os.remove( cacheDirectory + "/" + file )


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
    # baseName: The text used to form the file name, typically the name of the calling application.
    #
    # The object will be written to the cache directory using the pattern
    #     ${XDGKey}/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    # or
    #     ~/.cache/applicationBaseDirectory/baseNameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    #
    # Returns True on success; False otherwise.
    def writeCacheBinary( self, binaryData, baseName ):
        success = True
        cacheFile = \
            self.__getCacheDirectory() + \
            baseName + \
            datetime.datetime.utcnow().strftime( IndicatorBase.CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )

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
    # fileName: The file name of the text file.
    # text: The text to write.
    def writeCacheText( self, fileName, text ):
        success = True
        cacheFile = self.__getCacheDirectory() + fileName
        try:
            with open( cacheFile, "w" ) as f:
                f.write( text )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing to cache: " + cacheFile )
            success = False

        return success


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