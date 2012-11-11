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


# Application indicator to display PPA download statistics.
#
# References:
#  https://launchpad.net/+apidoc/1.0.html
#  https://help.launchpad.net/API/launchpadlib
#  http://developer.ubuntu.com/api/ubuntu-12.04/c/appindicator/index.html
#  https://help.launchpad.net/API/Hacking
#  https://python-gtk-3-tutorial.readthedocs.org
#  http://developer.gnome.org/gtk3/stable/index.html

from copy import deepcopy

appindicatorImported = True
try:
    from gi.repository import AppIndicator3 as appindicator
except:
    appindicatorImported = False

from gi.repository import Gdk
from gi.repository import GObject as gobject
from gi.repository import Gtk
from threading import Thread
from urllib.request import urlopen

import json
import locale
import logging
import os
import shutil
import sys
import threading
import webbrowser


class IndicatorPPADownloadStatistics:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-ppa-download-statistics"
    VERSION = "1.0.10"
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    SERIES = [ "raring", "quantal", "precise", "oneiric", "natty", "lucid", "hardy" ]
    ARCHITECTURES = [ "amd64", "i386" ]

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_PPAS = "ppas"
    SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER = "allowMenuItemsToLaunchBrowser"
    SETTINGS_SHOW_SUBMENU = "showSubmenu"


    def __init__( self ):
        self.dialog = None
        self.ppaDownloadStatistics = { }
        self.request = False
        self.updateThread = None

        Gdk.threads_init()
        gobject.threads_init()
        self.lock = threading.Lock()

        logging.basicConfig( file = sys.stderr, level = logging.INFO )
        self.loadSettings()

        # One of the install dependencies for Debian/Ubuntu is that appindicator exists.
        # However the appindicator only works under Ubuntu Unity.
        global appindicatorImported
        unityIsInstalled = os.getenv( "XDG_CURRENT_DESKTOP" )
        if unityIsInstalled is None:
            appindicatorImported = False
        elif str( unityIsInstalled ).lower() != "Unity".lower():
            appindicatorImported = False

        if appindicatorImported == True:
            self.indicator = appindicator.Indicator.new( IndicatorPPADownloadStatistics.NAME, "", appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling...
            self.buildMenu()
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.indicator.set_label( "PPA", "" ) # Second parameter is a guide for how wide the text could get (see label-guide in http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html).
        else:
            self.menu = Gtk.Menu() # Set an empty menu to get things rolling...
            self.buildMenu()
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorPPADownloadStatistics.NAME )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.requestPPADownloadAndMenuRefresh()
        gobject.timeout_add( 6 * 60 * 60 * 1000, self.requestPPADownloadAndMenuRefresh ) # Auto update every 6 hours.
        Gtk.main()


    def buildMenu( self ):
        if appindicatorImported == True:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if we don't do this we get GTK complaints).

        # Create the new menu and populate...
        menu = Gtk.Menu()

        # Add PPAs to the menu (including a separator at the end).
        oneOrMorePPAsExist = len( self.ppas ) > 0
        if( oneOrMorePPAsExist ):
            for key in self.getPPAKeysSorted():
                menuItem = Gtk.MenuItem( key )
                menu.append( menuItem )
                value = self.ppaDownloadStatistics.get( key )
                if self.showSubmenu == True:
                    subMenu = Gtk.Menu()
                    if value is None:
                        subMenuItem = Gtk.MenuItem( "(no information)" )
                        subMenu.append( subMenuItem )
                        menuItem.set_submenu( subMenu )
                    elif len( value ) == 0:
                        subMenuItem = Gtk.MenuItem( "(error retrieving PPA)" )
                        subMenu.append( subMenuItem )
                        menuItem.set_submenu( subMenu )
                    else:
                        for item in value:
                            subMenuItem = Gtk.MenuItem( "   " + item[ 0 ] + " (" + item[ 1 ] + "): " + str( item[ 2 ] ) )
                            subMenuItem.set_name( key )
                            subMenuItem.connect( "activate", self.onPPA )
                            subMenu.append( subMenuItem )
                            menuItem.set_submenu( subMenu )
                else:
                    # When submenus are used, each time a PPA menu item is selected, the webpage is opened...so only provide the browser launch for non submenus (at the PPA level).
                    menuItem.set_name( key )
                    menuItem.connect( "activate", self.onPPA )

                    if value is None:
                        menuItem = Gtk.MenuItem( "   (no information)" )
                        menu.append( menuItem )
                    elif len( value ) == 0:
                        menuItem = Gtk.MenuItem( "   (error retrieving PPA)" )
                        menu.append( menuItem )
                    else:
                        for item in value:
                            menuItem = Gtk.MenuItem( "    " + item[ 0 ] + " (" + item[ 1 ] + "): " + str( item[ 2 ] ) )
                            menuItem.set_name( key )
                            menuItem.connect( "activate", self.onPPA )
                            menu.append( menuItem )

        menu.append( Gtk.SeparatorMenuItem() )

        addMenuItem = Gtk.MenuItem( "Add a PPA" )
        addMenuItem.connect( "activate", self.onAdd )
        menu.append( addMenuItem )

        editMenuItem = Gtk.MenuItem( "Edit a PPA" )
        editMenuItem.set_sensitive( oneOrMorePPAsExist )
        menu.append( editMenuItem )

        if( oneOrMorePPAsExist ):
            subMenu = Gtk.Menu()
            editMenuItem.set_submenu( subMenu )
            for key in self.getPPAKeysSorted():
                subMenuItem = Gtk.MenuItem( key )
                subMenuItem.set_name( key )
                subMenuItem.connect( "activate", self.onEdit )
                subMenu.append( subMenuItem )

        removeMenuItem = Gtk.MenuItem( "Remove a PPA" )
        removeMenuItem.set_sensitive( oneOrMorePPAsExist )
        menu.append( removeMenuItem )

        if( oneOrMorePPAsExist ):
            subMenu = Gtk.Menu()
            removeMenuItem.set_submenu( subMenu )
            for key in self.getPPAKeysSorted():
                subMenuItem = Gtk.MenuItem( key )
                subMenuItem.set_name( key )
                subMenuItem.connect( "activate", self.onRemove )
                subMenu.append( subMenuItem )

        preferencesMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        menu.append( preferencesMenuItem )

        aboutMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        aboutMenuItem.connect( "activate", self.onAbout )
        menu.append( aboutMenuItem )

        quitMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        quitMenuItem.connect( "activate", Gtk.main_quit )
        menu.append( quitMenuItem )

        if appindicatorImported == True:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu

        menu.show_all()


    def getPPAKeysSorted( self ):
        sortedKeys = [] 
        for key in list( self.ppas.keys() ):
            sortedKeys.append( key )

        return sorted( sortedKeys, key = locale.strxfrm )


    def getPPAUsersSorted( self ):
        sortedPPAUsers = [] 
        for key in list( self.ppas.keys() ):
            ppaUser = self.ppas[ key ][ 0 ]
            if ppaUser not in sortedPPAUsers:
                sortedPPAUsers.append( ppaUser )

        return sorted( sortedPPAUsers, key = locale.strxfrm )


    def getPPANamesSorted( self ):
        sortedPPANames = [] 
        for key in list( self.ppas.keys() ):
            ppaName = self.ppas[ key ][ 1 ]
            if ppaName not in sortedPPANames:
                sortedPPANames.append( ppaName )

        return sorted( sortedPPANames, key = locale.strxfrm )


    def getPPAKey( self, ppaList ):
        return str( ppaList[ 0 ] ) + " | " + str( ppaList[ 1 ] ) + " | " + str( ppaList[ 2 ] ) + " | " + str( ppaList[ 3 ] )


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )

    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def onPPA( self, widget ):
        if self.allowMenuItemsToLaunchBrowser == False:
            return

        firstPipe = str.find( widget.props.name, "|" )
        ppaUser = widget.props.name[ 0 : firstPipe ].strip()

        secondPipe = str.find( widget.props.name, "|", firstPipe + 1 )
        ppaName = widget.props.name[ firstPipe + 1 : secondPipe ].strip()

        thirdPipe = str.find( widget.props.name, "|", secondPipe + 1 )
        series = widget.props.name[ secondPipe + 1 : thirdPipe ].strip()

        url = "http://launchpad.net/~" + ppaUser + "/+archive/" + ppaName + "?field.series_filter=" + series
        webbrowser.open( url ) # This returns a boolean - I wanted to message the user on a false return value but popping up a message dialog causes a lock up!


    def onAbout( self, widget ):
        if self.dialog is not None:
            return

        self.dialog = Gtk.AboutDialog()
        self.dialog.set_program_name( IndicatorPPADownloadStatistics.NAME )
        self.dialog.set_comments( IndicatorPPADownloadStatistics.AUTHOR )
        self.dialog.set_website( IndicatorPPADownloadStatistics.WEBSITE )
        self.dialog.set_website_label( IndicatorPPADownloadStatistics.WEBSITE )
        self.dialog.set_version( IndicatorPPADownloadStatistics.VERSION )
        self.dialog.set_license( IndicatorPPADownloadStatistics.LICENSE )
        self.dialog.run()
        self.dialog.destroy()
        self.dialog = None


    def onAutoStart( self, widget ):
        if not os.path.exists( IndicatorPPADownloadStatistics.AUTOSTART_PATH ):
            os.makedirs( IndicatorPPADownloadStatistics.AUTOSTART_PATH )

        if widget.active:
            try:
                shutil.copy( IndicatorPPADownloadStatistics.DESKTOP_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE, IndicatorPPADownloadStatistics.AUTOSTART_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE )
            except Exception as e:
                logging.exception( e )
        else:
            try:
                os.remove( IndicatorPPADownloadStatistics.AUTOSTART_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE )
            except: pass


    def onAdd( self, widget ):
        self.addEditPPA( True, "", "", IndicatorPPADownloadStatistics.SERIES[ 0 ], IndicatorPPADownloadStatistics.ARCHITECTURES[ 0 ] )


    def onEdit( self, widget ):
        ppa = self.ppas.get( widget.props.name )
        self.addEditPPA( False, ppa[ 0 ], ppa[ 1 ], ppa[ 2 ], ppa[ 3 ] )


    def addEditPPA( self, add, existingPPAUser, existingPPAName, existingSeries, existingArchitecture ):
        if self.dialog is not None:
            return

        title = "Add a PPA"
        if add == False:
            title = "Edit PPA"

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( "PPA User" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        if len( self.ppas ) > 0:
            ppaUser = Gtk.ComboBoxText.new_with_entry()
            ppaUsers = self.getPPAUsersSorted()
            for item in ppaUsers:
                ppaUser.append_text( item )

            if add == False:
                ppaUser.set_active( self.getIndexForPPAUser( ppaUsers, existingPPAUser ) )
        else:
            # There are no PPAs present, so we are adding the first PPA.
            ppaUser = Gtk.Entry()

        ppaUser.set_hexpand( True ) # Only need to set this once and all objects will expand.
        grid.attach( ppaUser, 1, 0, 1, 1 )

        label = Gtk.Label( "PPA Name" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        if len( self.ppas ) > 0:
            ppaName = Gtk.ComboBoxText.new_with_entry()
            ppaNames = self.getPPANamesSorted()
            for item in ppaNames:
                ppaName.append_text( item )

            if add == False:
                ppaName.set_active( self.getIndexForPPAName( ppaNames, existingPPAName ) )
        else:
            # There are no PPAs present, so we are adding the first PPA.
            ppaName = Gtk.Entry()

        grid.attach( ppaName, 1, 1, 1, 1 )

        label = Gtk.Label( "Series" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        series = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.SERIES:
            series.append_text( item )

        if add == False:
            series.set_active( self.getIndexForSeries( existingSeries ) )
        else:
            series.set_active( 0 )

        grid.attach( series, 1, 2, 1, 1 )

        label = Gtk.Label( "Architecture" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        architectures = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.ARCHITECTURES:
            architectures.append_text( item )

        if add == False:
            architectures.set_active( self.getIndexForArchitecture( existingArchitecture ) )
        else:
            architectures.set_active( 0 )

        grid.attach( architectures, 1, 3, 1, 1 )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( grid, True, True, 0 )
        self.dialog.set_border_width( 5 )

        while True:
            self.dialog.show_all()
            response = self.dialog.run()

            if response == Gtk.ResponseType.CANCEL:
                break

            if len( self.ppas ) > 0:
                ppaUserValue = ppaUser.get_active_text().strip()
                ppaNameValue = ppaName.get_active_text().strip()
            else:
                ppaUserValue = ppaUser.get_text().strip()
                ppaNameValue = ppaName.get_text().strip()

            if ppaUserValue == "":
                self.showMessage( Gtk.MessageType.ERROR, "PPA user cannot be empty." )
                ppaUser.grab_focus()
                continue

            if ppaNameValue == "":
                self.showMessage( Gtk.MessageType.ERROR, "PPA name cannot be empty." )
                ppaName.grab_focus()
                continue

            ppaList = [ ppaUserValue, ppaNameValue, series.get_active_text(), architectures.get_active_text() ]
            key = self.getPPAKey( ppaList )
            if add == True:
                if key not in self.ppas:
                    self.ppas[ key ] = ppaList
                    self.saveSettings()
                    self.buildMenu() # Update the menu to immediately reflect the change...still need to do a new download.
                    self.requestPPADownloadAndMenuRefresh()
            else: # This is an edit
                if key not in self.ppas:
                    oldKey = self.getPPAKey( [ existingPPAUser, existingPPAName, existingSeries, existingArchitecture ] )
                    del self.ppas[ oldKey ]
                    self.ppas[ key ] = ppaList
                    self.saveSettings()
                    self.buildMenu() # Update the menu to immediately reflect the change...still need to do a new download.
                    self.requestPPADownloadAndMenuRefresh()

            break

        self.dialog.destroy()
        self.dialog = None


    def getIndexForArchitecture( self, architecture ):
        for i in range( len( IndicatorPPADownloadStatistics.ARCHITECTURES ) ):
            if IndicatorPPADownloadStatistics.ARCHITECTURES[ i ] == architecture:
                return i

        return -1 # Should never happen!


    def getIndexForSeries( self, series ):
        for i in range( len( IndicatorPPADownloadStatistics.SERIES ) ):
            if IndicatorPPADownloadStatistics.SERIES[ i ] == series:
                return i

        return -1 # Should never happen!


    def getIndexForPPAUser( self, ppaUsers, ppaUser ):
        for i in range( len( ppaUsers ) ):
            if ppaUsers[ i ] == ppaUser:
                return i

        return -1 # Should never happen!


    def getIndexForPPAName( self, ppaNames, ppaName ):
        for i in range( len( ppaNames ) ):
            if ppaNames[ i ] == ppaName:
                return i

        return -1 # Should never happen!


    def showMessage( self, messageType, message ):
        dialog = Gtk.MessageDialog( None, 0, messageType, Gtk.ButtonsType.OK, message )
        dialog.run()
        dialog.destroy()


    def onRemove( self, widget ):
        if self.dialog is not None:
            return

        self.dialog = Gtk.MessageDialog( None, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, "Remove the PPA '" + widget.props.name + "'?" )
        response = self.dialog.run()
        self.dialog.destroy()
        if response == Gtk.ResponseType.OK:
            del self.ppas[ widget.props.name ]
            self.saveSettings()
            self.buildMenu()

        self.dialog = None


    def onPreferences( self, widget ):
        if self.dialog is not None:
            return

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showAsSubmenusCheckbox = Gtk.CheckButton( "Show as submenus" )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )
        grid.attach( showAsSubmenusCheckbox, 0, 0, 1, 1 )

        allowMenuItemsToLaunchBrowserCheckbox = Gtk.CheckButton( "Load PPA page on selection" )
        allowMenuItemsToLaunchBrowserCheckbox.set_tooltip_text( "Clicking a PPA menu item launches the default web browser and loads the PPA home page." )
        allowMenuItemsToLaunchBrowserCheckbox.set_active( self.allowMenuItemsToLaunchBrowser )
        grid.attach( allowMenuItemsToLaunchBrowserCheckbox, 0, 1, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorPPADownloadStatistics.AUTOSTART_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 2, 1, 1 )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( grid, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.showSubmenu = showAsSubmenusCheckbox.get_active()
            self.allowMenuItemsToLaunchBrowser = allowMenuItemsToLaunchBrowserCheckbox.get_active()
            self.saveSettings()

            if not os.path.exists( IndicatorPPADownloadStatistics.AUTOSTART_PATH ):
                os.makedirs( IndicatorPPADownloadStatistics.AUTOSTART_PATH )

            if autostartCheckbox.get_active():
                try:
                    shutil.copy( IndicatorPPADownloadStatistics.DESKTOP_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE, IndicatorPPADownloadStatistics.AUTOSTART_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE )
                except Exception as e:
                    logging.exception( e )
            else:
                try:
                    os.remove( IndicatorPPADownloadStatistics.AUTOSTART_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE )
                except: pass

        self.dialog.destroy()
        self.dialog = None
        self.buildMenu()


    def loadSettings( self ):
        self.allowMenuItemsToLaunchBrowser = True
        self.showSubmenu = False
        self.ppas = {}

        if os.path.isfile( IndicatorPPADownloadStatistics.SETTINGS_FILE ):
            try:
                with open( IndicatorPPADownloadStatistics.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                ppas = []
                ppas = settings.get( IndicatorPPADownloadStatistics.SETTINGS_PPAS, ppas )
                for ppaList in ppas:
                    key = self.getPPAKey( ppaList )
                    self.ppas[ key ] = ppaList

                self.allowMenuItemsToLaunchBrowser = settings.get( IndicatorPPADownloadStatistics.SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER, self.allowMenuItemsToLaunchBrowser )
                self.showSubmenu = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SHOW_SUBMENU, self.showSubmenu )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorPPADownloadStatistics.SETTINGS_FILE )
        else:
            # No properties file exists, so populate with a sample PPA to give the user an idea of the format.
            ppaList = [ "thebernmeister", "ppa", "quantal", "i386" ]
            self.ppas[ self.getPPAKey( ppaList ) ] = ppaList


    def saveSettings( self ):
        try:
            ppas = []
            for k, v in list( self.ppas.items() ):
                ppas.append( v )

            settings = {
                IndicatorPPADownloadStatistics.SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER: self.allowMenuItemsToLaunchBrowser,
                IndicatorPPADownloadStatistics.SETTINGS_PPAS: ppas,
                IndicatorPPADownloadStatistics.SETTINGS_SHOW_SUBMENU: self.showSubmenu
            }

            with open( IndicatorPPADownloadStatistics.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorPPADownloadStatistics.SETTINGS_FILE )


    # Get a list of the published binaries for each PPA and from that extract the ID for each binary
    # which is then used to get the download count for each binary.  The ID is the number at the end of self_link.
    # The published binary object looks like this...
    #{
    #    "total_size": 4, 
    #    "start": 0, 
    #    "entries": [
    #    {
    #        "distro_arch_series_link": "https://api.launchpad.net/1.0/ubuntu/precise/i386", 
    #        "removal_comment": null, 
    #        "display_name": "indicator-lunar 1.0.9-1 in precise i386", 
    #        "date_made_pending": null, 
    #        "date_superseded": null, 
    #        "priority_name": "OPTIONAL", 
    #        "http_etag": "\"94b9873b47426c010c4117854c67c028f1acc969-771acce030b1683dc367b5cbf79376d386e7f3b3\"", 
    #        "self_link": "https://api.launchpad.net/1.0/~thebernmeister/+archive/ppa/+binarypub/28105302", 
    #        "binary_package_version": "1.0.9-1", 
    #        "resource_type_link": "https://api.launchpad.net/1.0/#binary_package_publishing_history", 
    #        "component_name": "main", 
    #        "status": "Published", 
    #        "date_removed": null, 
    #        "pocket": "Release", 
    #        "date_published": "2012-08-09T10:30:49.572656+00:00", 
    #        "removed_by_link": null, "section_name": "python", 
    #        "date_created": "2012-08-09T10:27:31.762212+00:00", 
    #        "binary_package_name": "indicator-lunar", 
    #        "archive_link": "https://api.launchpad.net/1.0/~thebernmeister/+archive/ppa", 
    #        "architecture_specific": false, 
    #        "scheduled_deletion_date": null
    #    }
    #    {
    #    ,... 
    #}
    def getPPADownloadStatistics( self, ppas ):
        ppaDownloadStatistics = { }
        for ppaKey in ppas:
            ppaUser = ppas[ ppaKey ][ 0 ]
            ppaName = ppas[ ppaKey ][ 1 ]
            series = ppas[ ppaKey ][ 2 ]
            architecture = ppas[ ppaKey ][ 3 ]
            try:
                url = "https://api.launchpad.net/1.0/~" + ppaUser + "/+archive/" + ppaName + "?ws.op=getPublishedBinaries&status=Published&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + series + "/" + architecture
                publishedBinaries = json.loads( urlopen( url ).read().decode( "utf8" ) )
                totalSize = publishedBinaries[ "total_size" ]
                for i in range( totalSize ):
                    binaryPackageName = publishedBinaries[ "entries" ][ i ][ "binary_package_name" ]
                    binaryPackageVersion = publishedBinaries[ "entries" ][ i ][ "binary_package_version" ]
                    indexLastSlash = publishedBinaries[ "entries" ][ i ][ "self_link" ].rfind( "/" )
                    binaryPackageId = publishedBinaries[ "entries" ][ i ][ "self_link" ][ indexLastSlash + 1 : ]
                    url = "https://api.launchpad.net/1.0/~thebernmeister/+archive/ppa/+binarypub/" + binaryPackageId + "?ws.op=getDownloadCount"
                    downloadCount = json.loads( urlopen( url ).read().decode( "utf8" ) )
                    value = ppaDownloadStatistics.get( ppaKey )
                    if value is None:
                        ppaDownloadStatistics[ ppaKey ] = [ [ binaryPackageName, binaryPackageVersion, downloadCount ] ]
                    else:
                        value.append( [ binaryPackageName, binaryPackageVersion, downloadCount ] )
                        ppaDownloadStatistics[ ppaKey ] = value

            except Exception as e:
                ppaDownloadStatistics[ ppaKey ] = [ ]

        self.lock.acquire()

        self.ppaDownloadStatistics = ppaDownloadStatistics
        self.updateThread = None
        if self.request == True:
            self.request = False
            self.lock.release()
            self.requestPPADownloadAndMenuRefresh()
        else:
            self.lock.release()

        gobject.idle_add( self.buildMenu )


    def requestPPADownloadAndMenuRefresh( self ):
        self.lock.acquire()

        if self.updateThread is None:
            self.updateThread = Thread( target = self.getPPADownloadStatistics, args = ( deepcopy( self.ppas ), ) )
            self.updateThread.start()
        else:
            self.request = True

        self.lock.release()
        return True 


if __name__ == "__main__":
    indicator = IndicatorPPADownloadStatistics()
    indicator.main()