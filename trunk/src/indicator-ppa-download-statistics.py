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


# Application indicator which displays PPA download statistics.


# References:
#  https://launchpad.net/+apidoc/1.0.html
#  https://help.launchpad.net/API/launchpadlib
#  http://developer.ubuntu.com/api/ubuntu-12.04/c/appindicator/index.html
#  https://help.launchpad.net/API/Hacking
#  https://python-gtk-3-tutorial.readthedocs.org
#  http://developer.gnome.org/gtk3/stable/index.html


from copy import deepcopy

try:
    from gi.repository import AppIndicator3 as appindicator
except:
    pass

from gi.repository import GLib
from gi.repository import Gtk
from threading import Thread
from urllib.request import urlopen

import itertools
import json
import locale
import logging
import os
import shutil
import sys
import threading
import time
import webbrowser


class IndicatorPPADownloadStatistics:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-ppa-download-statistics"
    VERSION = "1.0.20"
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    SERIES = [ "raring", "quantal", "precise", "oneiric", "lucid", "hardy" ]
    ARCHITECTURES = [ "amd64", "i386" ]

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_PPAS = "ppas"
    SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER = "allowMenuItemsToLaunchBrowser"
    SETTINGS_SORT_BY_DOWNLOAD = "sortByDownload"
    SETTINGS_SORT_BY_DOWNLOAD_AMOUNT = "sortByDownloadAmount"
    SETTINGS_COMBINE_PPAS = "combinePPAs"
    SETTINGS_SHOW_SUBMENU = "showSubmenu"

    DOWNLOADING_DATA = "(downloading data...)"
    ERROR_RETRIEVING_PPA = "(error retrieving PPA)"


    def __init__( self ):
        self.dialog = None
        self.ppaDownloadStatistics = { }
        self.request = False
        self.updateThread = None

        GLib.threads_init()
        self.lock = threading.Lock()

        logging.basicConfig( file = sys.stderr, level = logging.INFO )
        self.loadSettings()

        try:
            self.appindicatorImported = True
            self.indicator = appindicator.Indicator.new( IndicatorPPADownloadStatistics.NAME, "", appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling...
            self.buildMenu()
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.indicator.set_label( "PPA", "" ) # Second parameter is a guide for how wide the text could get (see label-guide in http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html).
        except:
            self.appindicatorImported = False            
            self.menu = Gtk.Menu() # Set an empty menu to get things rolling...
            self.buildMenu()
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorPPADownloadStatistics.NAME )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.requestPPADownloadAndMenuRefresh()
        GLib.timeout_add_seconds( 6 * 60 * 60, self.requestPPADownloadAndMenuRefresh ) # Auto update every 6 hours.
        Gtk.main()


    def buildMenu( self ):
        if self.appindicatorImported == True:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if we don't do this we get GTK complaints).

        menu = Gtk.Menu()

        # Add PPAs to the menu...
        ppas = self.getPPAsSorted( self.combinePPAs )
        ppaDownloadStatistics = self.ppaDownloadStatistics

        if self.combinePPAs == True:
            ppaDownloadStatistics = self.getCombinedPPAs()

        if self.sortByDownload == True:
            ppaDownloadStatistics = self.getClippedPPAs( ppas, ppaDownloadStatistics )

        indent = "    "
        if self.showSubmenu == True:
            for ppa in ppas:
                publishedBinaryInfos = ppaDownloadStatistics.get( ppa )
                menuItem = Gtk.MenuItem( ppa )
                menu.append( menuItem )
                subMenu = Gtk.Menu()
                if type( publishedBinaryInfos ) is str:
                    subMenuItem = Gtk.MenuItem( publishedBinaryInfos )
                    subMenu.append( subMenuItem )
                    menuItem.set_submenu( subMenu )
                else:
                    for publishedBinaryInfo in publishedBinaryInfos:
                        if publishedBinaryInfo.getPackageVersion() is None:
                            subMenuItem = Gtk.MenuItem( indent + publishedBinaryInfo.getPackageName() + ": " + str( publishedBinaryInfo.getDownloadCount() ) )
                        else:
                            subMenuItem = Gtk.MenuItem( indent + publishedBinaryInfo.getPackageName() + " (" + publishedBinaryInfo.getPackageVersion() + "): " + str( publishedBinaryInfo.getDownloadCount() ) )

                        subMenuItem.set_name( ppa )
                        subMenuItem.connect( "activate", self.onPPA )
                        subMenu.append( subMenuItem )
                        menuItem.set_submenu( subMenu )
        else:
            for ppa in ppas:
                publishedBinaryInfos = ppaDownloadStatistics.get( ppa )
                menuItem = Gtk.MenuItem( ppa )
                menu.append( menuItem )
                menuItem.set_name( ppa )
                menuItem.connect( "activate", self.onPPA )
                if type( publishedBinaryInfos ) is str:
                    menuItem = Gtk.MenuItem( indent + publishedBinaryInfos )
                    menu.append( menuItem )
                else:
                    for publishedBinaryInfo in publishedBinaryInfos:
                        if publishedBinaryInfo.getPackageVersion() is None:
                            menuItem = Gtk.MenuItem( indent + publishedBinaryInfo.getPackageName() + ": " + str( publishedBinaryInfo.getDownloadCount() ) )
                        else:
                            menuItem = Gtk.MenuItem( indent + publishedBinaryInfo.getPackageName() + " (" + publishedBinaryInfo.getPackageVersion() + "): " + str( publishedBinaryInfo.getDownloadCount() ) )

                        menuItem.set_name( ppa )
                        menuItem.connect( "activate", self.onPPA )
                        menu.append( menuItem )

        menu.append( Gtk.SeparatorMenuItem() )

        addMenuItem = Gtk.MenuItem( "Add a PPA" )
        addMenuItem.connect( "activate", self.onAdd )
        menu.append( addMenuItem )

        oneOrMorePPAsExist = len( self.ppaInfos ) > 0
        editMenuItem = Gtk.MenuItem( "Edit a PPA" )
        editMenuItem.set_sensitive( oneOrMorePPAsExist )
        menu.append( editMenuItem )

        if( oneOrMorePPAsExist ):
            subMenu = Gtk.Menu()
            editMenuItem.set_submenu( subMenu )
            for ppa in self.getPPAsSorted( False ):
                subMenuItem = Gtk.MenuItem( ppa )
                subMenuItem.set_name( ppa )
                subMenuItem.connect( "activate", self.onEdit )
                subMenu.append( subMenuItem )

        removeMenuItem = Gtk.MenuItem( "Remove a PPA" )
        removeMenuItem.set_sensitive( oneOrMorePPAsExist )
        menu.append( removeMenuItem )

        if( oneOrMorePPAsExist ):
            subMenu = Gtk.Menu()
            removeMenuItem.set_submenu( subMenu )
            for ppa in self.getPPAsSorted( False ):
                subMenuItem = Gtk.MenuItem( ppa )
                subMenuItem.set_name( ppa )
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

        if self.appindicatorImported == True:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu

        menu.show_all()


    def getCombinedPPAs( self ):
        combinedPPADownloadStatistics = { }
        ppas = self.getPPAsSorted( False )
        architectureIndependentPublishedBinaries = [ ] # Used to manage the download counts of architecture independent published binaries.
        for ppa in ppas:
            combinedKey = ppa[ : ppa.find( " | ", ppa.find( " | " ) + 1 ) ] # The combined ppa is 'ppaUser | ppaName | series | architecture' stripped down to 'ppaUser | ppaName'.
            publishedBinaryInfos = self.ppaDownloadStatistics.get( ppa )

            if type( publishedBinaryInfos ) is str: # This is a string message (either 'downloading data' or 'no information' or 'error retrieving PPA').
                if combinedKey not in combinedPPADownloadStatistics:
                    combinedPPADownloadStatistics[ combinedKey ] = publishedBinaryInfos # Only put in the string message if no other data exists.

                continue

            # Iterate over the published binary infos and combine...
            for publishedBinaryInfo in publishedBinaryInfos:

                # A key to record architecture independent published binary packages which have already been added.
                id_ = combinedKey + publishedBinaryInfo.getPackageName() + publishedBinaryInfo.getPackageVersion() # id is a reserved keyword!

                if combinedKey not in combinedPPADownloadStatistics:
                    # This is the first occurrence of this combined PPA...
                    combinedPublishedBinaryInfo = PublishedBinaryInfo( publishedBinaryInfo.getPackageName(), publishedBinaryInfo.getPackageVersion(), publishedBinaryInfo.getDownloadCount(), publishedBinaryInfo.isArchitectureSpecific() )
                    combinedPPADownloadStatistics[ combinedKey ] = [ combinedPublishedBinaryInfo ]
                    architectureIndependentPublishedBinaries.append( id_ )
                    continue

                # This combined PPA already exists...see if a combined published binary exists which matches the current published binary...
                combinedPublishedBinaryInfos = combinedPPADownloadStatistics.get( combinedKey )
                added = False
                for combinedPublishedBinaryInfo in combinedPublishedBinaryInfos:
                    if publishedBinaryInfo.getPackageName() == combinedPublishedBinaryInfo.getPackageName():
                        # Update the existing combined published binary...
                        # Assume that the architecture specific flag of publishedBinaryInfo always matches that of the combinedPublishedBinaryInfo.
                        if publishedBinaryInfo.isArchitectureSpecific() == True:
                            combinedPublishedBinaryInfo.setDownloadCount( publishedBinaryInfo.getDownloadCount() + combinedPublishedBinaryInfo.getDownloadCount( ) )
                        else:
                            # Architecture independent published binaries with the same name can have different versions.
                            # For example an older version may exist for Natty but a newer version exists for Precise.
                            # In this case the binaries (and their download counts) need to be uniquely counted.
                            if not id_ in architectureIndependentPublishedBinaries:
                                # This published binary has not yet been added in, so add it's download count to the running total.
                                combinedPublishedBinaryInfo.setDownloadCount( publishedBinaryInfo.getDownloadCount() + combinedPublishedBinaryInfo.getDownloadCount( ) )
                                architectureIndependentPublishedBinaries.append( id_ )

                        # If the versions do not match then wipe...
                        if combinedPublishedBinaryInfo.getPackageVersion() is not None: 
                            if publishedBinaryInfo.getPackageVersion() != combinedPublishedBinaryInfo.getPackageVersion():
                                combinedPublishedBinaryInfo.setPackageVersion( None )

                        added = True
                        break

                # This published binary has not yet been added, so append...
                if not added:
                    combinedPublishedBinaryInfo = PublishedBinaryInfo( publishedBinaryInfo.getPackageName(), publishedBinaryInfo.getPackageVersion(), publishedBinaryInfo.getDownloadCount(), publishedBinaryInfo.isArchitectureSpecific() )
                    combinedPublishedBinaryInfos.append( combinedPublishedBinaryInfo )
                    architectureIndependentPublishedBinaries.append( id_ )

        # Sort each list of published binaries...
        for key in combinedPPADownloadStatistics:
            combinedPublishedBinaries = combinedPPADownloadStatistics.get( key )
            if type( combinedPublishedBinaries ) is PublishedBinaryInfo:
                combinedPublishedBinariesNew = sorted( combinedPublishedBinaries, key = lambda combinedPublishedBinary: combinedPublishedBinary.packageName )
                combinedPPADownloadStatistics[ key ] = combinedPublishedBinariesNew

        return combinedPPADownloadStatistics        


    def getClippedPPAs( self, ppas, ppaDownloadStatistics ):
        clippedPPADownloadStatistics = { }
        for ppa in ppas:
            publishedBinaryInfos = ppaDownloadStatistics.get( ppa )
            if type( publishedBinaryInfos ) is str: # This is a string message (either 'downloading data' or 'no information' or 'error retrieving PPA').
                clippedPPADownloadStatistics[ ppa ] = publishedBinaryInfos
                continue

            publishedBinaryInfosSortedByDownloadCount = sorted( ppaDownloadStatistics.get( ppa ), key = lambda publishedBinaryInfo: publishedBinaryInfo.downloadCount, reverse = True )
            clippedPPADownloadStatistics[ ppa ] = publishedBinaryInfosSortedByDownloadCount[ : self.sortByDownloadAmount ]

        return clippedPPADownloadStatistics        


    def getPPAsSorted( self, combined ):
        sortedKeys = [ ] 

        if combined == True:
            for key in list( self.ppaInfos.keys() ):
                combinedKey = key[ : key.find( " | ", key.find( " | " ) + 1 ) ] # The combined key is 'ppaUser | ppaName | series | architecture' stripped down to 'ppaUser | ppaName'.
                if not combinedKey in sortedKeys:
                    sortedKeys.append( combinedKey )
        else:
            for key in list( self.ppaInfos.keys() ):
                sortedKeys.append( key )

        return sorted( sortedKeys, key = locale.strxfrm )


    def getPPAUsersSorted( self ):
        sortedPPAUsers = [ ] 
        for key in list( self.ppaInfos.keys() ):
            ppaUser = self.ppaInfos[ key ].getUser()
            if ppaUser not in sortedPPAUsers:
                sortedPPAUsers.append( ppaUser )

        return sorted( sortedPPAUsers, key = locale.strxfrm )


    def getPPANamesSorted( self ):
        sortedPPANames = [ ] 
        for key in list( self.ppaInfos.keys() ):
            ppaName = self.ppaInfos[ key ].getName()
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
        if secondPipe == -1:
            # This is a combined PPA...
            ppaName = widget.props.name[ firstPipe + 1 : ].strip()
            url = "http://launchpad.net/~" + ppaUser + "/+archive/" + ppaName
        else:
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
        ppa = self.ppaInfos.get( widget.props.name )
        self.addEditPPA( False, ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() )


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

        if len( self.ppaInfos ) > 0:
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

        if len( self.ppaInfos ) > 0:
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

        self.dialog = Gtk.Dialog( title, None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( grid, True, True, 0 )
        self.dialog.set_border_width( 5 )

        while True:
            self.dialog.show_all()
            response = self.dialog.run()

            if response == Gtk.ResponseType.CANCEL:
                break

            if len( self.ppaInfos ) > 0:
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
            if key not in self.ppaInfos: # If there is no change, there is nothing to do...
                if add == True:
                    self.ppaInfos[ key ] = PPAInfo( ppaList[ 0 ], ppaList[ 1 ], ppaList[ 2 ], ppaList[ 3 ] )
                else: # This is an edit
                    oldKey = self.getPPAKey( [ existingPPAUser, existingPPAName, existingSeries, existingArchitecture ] )
                    del self.ppaInfos[ oldKey ]
                    self.ppaInfos[ key ] = PPAInfo( ppaList[ 0 ], ppaList[ 1 ], ppaList[ 2 ], ppaList[ 3 ] )

                self.saveSettings()
                GLib.timeout_add_seconds( 1, self.buildMenu ) # If we update the menu directly, GTK complains that the menu (which kicked off preferences) no longer exists.
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
            del self.ppaInfos[ widget.props.name ]
            self.saveSettings()
            GLib.timeout_add_seconds( 1, self.buildMenu ) # If we update the menu directly, GTK complains that the menu (which kicked off preferences) no longer exists.

            if self.combinePPAs == True: # Only makes sense to do a download if PPAs are combined...
                self.requestPPADownloadAndMenuRefresh()

        self.dialog = None


    def onPreferences( self, widget ):
        if self.dialog is not None:
            return

        notebook = Gtk.Notebook()

        # First tab - display settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showAsSubmenusCheckbox = Gtk.CheckButton( "Show as submenus" )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )
        grid.attach( showAsSubmenusCheckbox, 0, 0, 2, 1 )

        combinaPPAsCheckbox = Gtk.CheckButton( "Combine PPAs" )
        toolTip = "Combines the statistics when the PPA user/name are the same.\n\n"
        toolTip += "If a published binary is architecture specific (such as compiled C), the download counts are summed across all instances of that published binary.\n\n"
        toolTip += "If a published binary is not architecture specific (such as Python), the download counts are only summed when the version of the binary is different.\n\n"
        toolTip += "The version number is retained only if it is identical across all instances of a published binary."
        combinaPPAsCheckbox.set_tooltip_text( toolTip )
        combinaPPAsCheckbox.set_active( self.combinePPAs )
        grid.attach( combinaPPAsCheckbox, 0, 1, 2, 1 )

        sortByDownloadCheckbox = Gtk.CheckButton( "Sort By Download" )
        sortByDownloadCheckbox.set_tooltip_text( "Sort by download within each PPA." )
        sortByDownloadCheckbox.set_active( self.sortByDownload )
        grid.attach( sortByDownloadCheckbox, 0, 2, 2, 1 )

        label = Gtk.Label( "  Clip Amount" )
        label.set_sensitive( sortByDownloadCheckbox.get_active() )
        label.set_margin_left( 15 )
        grid.attach( label, 0, 3, 1, 1 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.sortByDownloadAmount, 0, 10000, 1, 5, 0 ) )
        spinner.set_tooltip_text( "Limit the number of entries when sorting by download." )
        spinner.set_sensitive( sortByDownloadCheckbox.get_active() )
        spinner.set_hexpand( True )
        grid.attach( spinner, 1, 3, 1, 1 )

        sortByDownloadCheckbox.connect( "toggled", self.onClipByDownloadCheckbox, label, spinner )

        notebook.append_page( grid, Gtk.Label( "Display" ) )

        # Second  tab - general settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorPPADownloadStatistics.AUTOSTART_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 0, 1, 1 )

        allowMenuItemsToLaunchBrowserCheckbox = Gtk.CheckButton( "Load PPA page on selection" )
        allowMenuItemsToLaunchBrowserCheckbox.set_tooltip_text( "Clicking a PPA menu item launches the default web browser and loads the PPA home page." )
        allowMenuItemsToLaunchBrowserCheckbox.set_active( self.allowMenuItemsToLaunchBrowser )
        grid.attach( allowMenuItemsToLaunchBrowserCheckbox, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "General" ) )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.showSubmenu = showAsSubmenusCheckbox.get_active()
            self.combinePPAs = combinaPPAsCheckbox.get_active()
            self.sortByDownload = sortByDownloadCheckbox.get_active()
            self.sortByDownloadAmount = spinner.get_value_as_int()
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

            GLib.timeout_add_seconds( 1, self.buildMenu ) # If we update the menu directly, GTK complains that the menu (which kicked off preferences) no longer exists.

        self.dialog.destroy()
        self.dialog = None


    def onClipByDownloadCheckbox( self, source, spinner, label ):
        label.set_sensitive( source.get_active() )
        spinner.set_sensitive( source.get_active() )


    def loadSettings( self ):
        self.allowMenuItemsToLaunchBrowser = True
        self.sortByDownload = False
        self.sortByDownloadAmount = 3
        self.combinePPAs = False
        self.showSubmenu = False
        self.ppaInfos = { }

        if os.path.isfile( IndicatorPPADownloadStatistics.SETTINGS_FILE ):
            try:
                with open( IndicatorPPADownloadStatistics.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                ppas = [ ]
                ppas = settings.get( IndicatorPPADownloadStatistics.SETTINGS_PPAS, ppas )
                for ppaList in ppas:
                    key = self.getPPAKey( ppaList )
                    self.ppaInfos[ key ] = PPAInfo( ppaList[ 0 ], ppaList[ 1 ], ppaList[ 2 ], ppaList[ 3 ] )

                self.allowMenuItemsToLaunchBrowser = settings.get( IndicatorPPADownloadStatistics.SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER, self.allowMenuItemsToLaunchBrowser )
                self.sortByDownload = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD, self.sortByDownload )
                self.sortByDownloadAmount = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD_AMOUNT, self.sortByDownloadAmount )
                self.combinePPAs = settings.get( IndicatorPPADownloadStatistics.SETTINGS_COMBINE_PPAS, self.combinePPAs )
                self.showSubmenu = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SHOW_SUBMENU, self.showSubmenu )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorPPADownloadStatistics.SETTINGS_FILE )
        else:
            # No properties file exists, so populate with a sample PPA to give the user an idea of the format.
            ppaList = [ "thebernmeister", "ppa", "precise", "amd64" ]
            self.ppaInfos[ self.getPPAKey( ppaList ) ] = PPAInfo( ppaList[ 0 ], ppaList[ 1 ], ppaList[ 2 ], ppaList[ 3 ] )

        for key in self.ppaInfos:
            self.ppaDownloadStatistics[ key ] = IndicatorPPADownloadStatistics.DOWNLOADING_DATA


    def saveSettings( self ):
        try:
            ppas = [ ]
            for k, v in list( self.ppaInfos.items() ):
                ppas.append( [ v.getUser(), v.getName(), v.getSeries(), v.getArchitecture() ] )

            settings = {
                IndicatorPPADownloadStatistics.SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER: self.allowMenuItemsToLaunchBrowser,
                IndicatorPPADownloadStatistics.SETTINGS_PPAS: ppas,
                IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD: self.sortByDownload,
                IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD_AMOUNT: self.sortByDownloadAmount,
                IndicatorPPADownloadStatistics.SETTINGS_COMBINE_PPAS: self.combinePPAs,
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
    def getPPADownloadStatistics( self, ppaInfos ):
        ppaDownloadStatistics = { }
        threads = []
        for key in ppaInfos:
            ppaUser = ppaInfos[ key ].getUser()
            ppaName = ppaInfos[ key ].getName()
            series = ppaInfos[ key ].getSeries()
            architecture = ppaInfos[ key ].getArchitecture()

            t = Thread( target = self.getPublishedBinaries, args = ( key, ppaUser, ppaName, series, architecture, ppaDownloadStatistics ), )
            time.sleep( 0.5 ) # Space out the requests...
            threads.append( t )
            t.start()

        for t in threads:
            t.join()

        self.lock.acquire()

        self.ppaDownloadStatistics = ppaDownloadStatistics
        self.updateThread = None
        if self.request == True:
            self.request = False
            self.lock.release()
            self.requestPPADownloadAndMenuRefresh()
        else:
            self.lock.release()

        GLib.idle_add( self.buildMenu )


    def getPublishedBinaries( self, key, ppaUser, ppaName, series, architecture, ppaDownloadStatistics ):
        threads = []
        try:
            url = "https://api.launchpad.net/1.0/~" + ppaUser + "/+archive/" + ppaName + "?ws.op=getPublishedBinaries&status=Published&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + series + "/" + architecture
            publishedBinaries = json.loads( urlopen( url ).read().decode( "utf8" ) )
            numberOfPublishedBinaries = publishedBinaries[ "total_size" ]
            if numberOfPublishedBinaries == 0:
                self.lock.acquire()
                ppaDownloadStatistics[ key ] = "(no information)"
                self.lock.release()
            else:
                # The results are returned in lots of 75...so need to retrieve each lot after the first 75.
                index = 0
                resultPage = 1
                resultsPerUrl = 75
                for i in range( numberOfPublishedBinaries ):
                    if i == ( resultPage * resultsPerUrl ):
                        newURL = url + "&ws.start=" + str( resultPage * resultsPerUrl )
                        publishedBinaries = json.loads( urlopen( newURL ).read().decode( "utf8" ) )
                        resultPage += 1
                        index = 0

                    binaryPackageName = publishedBinaries[ "entries" ][ index ][ "binary_package_name" ]
                    binaryPackageVersion = publishedBinaries[ "entries" ][ index ][ "binary_package_version" ]
                    architectureSpecific = publishedBinaries[ "entries" ][ index ][ "architecture_specific" ]
                    indexLastSlash = publishedBinaries[ "entries" ][ index ][ "self_link" ].rfind( "/" )
                    binaryPackageId = publishedBinaries[ "entries" ][ index ][ "self_link" ][ indexLastSlash + 1 : ]

                    t = Thread( target = self.getDownloadCount, args = ( key, ppaUser, ppaName, binaryPackageName, binaryPackageVersion, architectureSpecific, binaryPackageId, ppaDownloadStatistics ), )
                    time.sleep( 0.5 ) # Space out the requests...
                    threads.append( t )
                    t.start()
                    index += 1

                for t in threads:
                    t.join()

                # The thread responses may not come back in order, so need to sort the packages...
                ppaDownloadStatistics[ key ] = sorted( ppaDownloadStatistics.get( key ), key = lambda publishedBinaryInfo: publishedBinaryInfo.packageName )

        except Exception as e:
            logging.exception( e )
            self.lock.acquire()
            ppaDownloadStatistics[ key ] = IndicatorPPADownloadStatistics.ERROR_RETRIEVING_PPA
            self.lock.release()


    def getDownloadCount( self, key, ppaUser, ppaName, binaryPackageName, binaryPackageVersion, architectureSpecific, binaryPackageId, ppaDownloadStatistics ):
        try:
            url = "https://api.launchpad.net/1.0/~" + ppaUser + "/+archive/" + ppaName + "/+binarypub/" + binaryPackageId + "?ws.op=getDownloadCount"
            downloadCount = json.loads( urlopen( url ).read().decode( "utf8" ) )
            publishedBinaryInfo = PublishedBinaryInfo( binaryPackageName, binaryPackageVersion, downloadCount, architectureSpecific )
            publishedBinaryInfos = ppaDownloadStatistics.get( key )
            if publishedBinaryInfos is None:
                self.lock.acquire()
                ppaDownloadStatistics[ key ] = [ publishedBinaryInfo ]
                self.lock.release()
            else:
                self.lock.acquire()
                publishedBinaryInfos.append( publishedBinaryInfo )
                ppaDownloadStatistics[ key ] = publishedBinaryInfos
                self.lock.release()

        except Exception as e:
            logging.exception( e )
            self.lock.acquire()
            ppaDownloadStatistics[ key ] = IndicatorPPADownloadStatistics.ERROR_RETRIEVING_PPA
            self.lock.release()


    def requestPPADownloadAndMenuRefresh( self ):
        self.lock.acquire()

        if self.updateThread is None:
            self.updateThread = Thread( target = self.getPPADownloadStatistics, args = ( deepcopy( self.ppaInfos ), ) )
            self.updateThread.start()
        else:
            self.request = True

        self.lock.release()
        return True 


class PPAInfo:

    def __init__( self, user, name, series, architecture ):
        self.user = user
        self.name = name
        self.series = series
        self.architecture = architecture


    def getUser( self ):
        return self.user


    def getName( self ):
        return self.name


    def getSeries( self ):
        return self.series


    def getArchitecture( self ):
        return self.architecture


    def __str__( self ):
        return str( self.user ) + " | " + str( self.name ) + " | " + str( self.series ) + " | " + str( self.architecture )


    def __repr__( self ):
        return self.__str__()


class PublishedBinaryInfo:

    def __init__( self, packageName, packageVersion, downloadCount, architectureSpecific ):
        self.packageName = packageName
        self.packageVersion = packageVersion
        self.downloadCount = downloadCount
        self.architectureSpecific = architectureSpecific


    def getPackageName( self ):
        return self.packageName


    def getPackageVersion( self ):
        return self.packageVersion


    def setPackageVersion( self, packageVersion ):
        self.packageVersion = packageVersion


    def getDownloadCount( self ):
        return self.downloadCount


    def setDownloadCount( self, downloadCount ):
        self.downloadCount = downloadCount


    def isArchitectureSpecific( self ):
        return self.architectureSpecific


    def __str__( self ):
        return str( self.packageName ) + " | " + str( self.packageVersion ) + " | " + str( self.downloadCount ) + " | " + str( self.architectureSpecific )


    def __repr__( self ):
        return self.__str__()


if __name__ == "__main__":
    IndicatorPPADownloadStatistics().main()