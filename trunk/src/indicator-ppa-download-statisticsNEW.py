#
#
#  {"ppas": [["noobslab", "indicators", "precise", "i386"],["noobslab", "indicators", "raring", "i386"],["noobslab", "indicators", "raring", "amd64"], ["whoopie79", "ppa", "precise", "i386"], ["thebernmeister", "ppa", "quantal", "amd64"], ["thebernmeister", "ppa", "precise", "amd64"], ["noobslab", "indicators", "quantal", "i386"], ["noobslab", "indicators", "precise", "amd64"], ["thebernmeister", "ppa", "raring", "amd64"], ["thebernmeister", "ppa", "raring", "i386"], ["thebernmeister", "ppa", "saucy", "i386"], ["thebernmeister", "ppa", "quantal", "i386"], ["thebernmeister", "ppa", "saucy", "amd64"],
# ["thebernmeister", "ppa", "precise", "i386"], 
# ["guido-iodice", "precise-updates", "precise", "amd64"],
# ["guido-iodice", "precise-updates", "precise", "i386"], 
# ["erdie1", "ppa", "precise", "amd64"],
# ["erdie1", "ppa", "precise", "i386"], 
# ["guido-iodice", "raring-quasi-rolling", "raring", "amd64"],
# ["guido-iodice", "raring-quasi-rolling", "raring", "i386"], 
# 
# 
# 
# 
# ["noobslab", "indicators", "quantal", "amd64"]
# 
# 
# 
# ], "sortByDownloadAmount": 10, "sortByDownload": false, "allowMenuItemsToLaunchBrowser": true, "showSubmenu": false, "combinePPAs": true}
#
#



#         self.filters[ 'noobslab | indicators' ] = [ "indicator-fortune", "indicator-lunar", "indicator-ppa-download-statistics", "indicator-stardate", "indicator-virtual-box", "python3-ephem" ]
#         self.filters[ 'whoopie79 | ppa' ] = [ "indicator-fortune", "indicator-lunar", "indicator-ppa-download-statistics", "indicator-stardate", "indicator-virtual-box", "python3-ephem" ]


# {"ppas": [["noobslab", "indicators", "precise", "i386"],["noobslab", "indicators", "raring", "i386"],["noobslab", "indicators", "raring", "amd64"], ["whoopie79", "ppa", "precise", "i386"], ["thebernmeister", "ppa", "quantal", "amd64"], ["thebernmeister", "ppa", "precise", "amd64"], ["noobslab", "indicators", "quantal", "i386"], ["noobslab", "indicators", "precise", "amd64"], ["thebernmeister", "ppa", "raring", "amd64"], ["thebernmeister", "ppa", "raring", "i386"], ["thebernmeister", "ppa", "saucy", "i386"], ["thebernmeister", "ppa", "quantal", "i386"], ["thebernmeister", "ppa", "saucy", "amd64"], ["thebernmeister", "ppa", "precise", "i386"], ["noobslab", "indicators", "quantal", "amd64"]], "sortByDownloadAmount": 4, "sortByDownload": true, "allowMenuItemsToLaunchBrowser": true, "showSubmenu": false, "combinePPAs": false}

#{"ppas": [  ["thebernmeister", "ppa", "quantal", "amd64"], ["thebernmeister", "ppa", "precise", "amd64"],  ["thebernmeister", "ppa", "raring", "amd64"], ["thebernmeister", "ppa", "raring", "i386"], ["thebernmeister", "ppa", "saucy", "i386"], ["thebernmeister", "ppa", "quantal", "i386"], ["thebernmeister", "ppa", "saucy", "amd64"], ["thebernmeister", "ppa", "precise", "i386"] ], "sortByDownloadAmount": 10, "sortByDownload": false, "allowMenuItemsToLaunchBrowser": true, "showSubmenu": true, "combinePPAs": true}

# {"ppas": [["noobslab", "indicators", "precise", "i386"],["noobslab", "indicators", "raring", "i386"],["noobslab", "indicators", "raring", "amd64"], ["whoopie79", "ppa", "precise", "i386"], ["thebernmeister", "ppa", "quantal", "amd64"], ["thebernmeister", "ppa", "precise", "amd64"], ["noobslab", "indicators", "quantal", "i386"], ["noobslab", "indicators", "precise", "amd64"], ["thebernmeister", "ppa", "raring", "amd64"], ["thebernmeister", "ppa", "raring", "i386"], ["thebernmeister", "ppa", "saucy", "i386"], ["thebernmeister", "ppa", "quantal", "i386"], ["thebernmeister", "ppa", "saucy", "amd64"], ["thebernmeister", "ppa", "precise", "i386"], ["noobslab", "indicators", "quantal", "amd64"]], "sortByDownloadAmount": 10, "sortByDownload": false, "allowMenuItemsToLaunchBrowser": true, "showSubmenu": false, "combinePPAs": true}



#TODO Sleep between some threads?  Somehow lighten the breadth of the load.
# Maybe do one PPA at a time...then copy the results out and do the next PPA? 
# How to avoid calling the menu to build itself whilst its currently building itself?
# 
# Load settings.
#    PPA object initialised with PPA info but no PBs.  
#    Deep copy PPA object to PPAForMenu.
# Build menu.
#    Grab lock.
#    Use PPAForMenu to update menu.
#    Release lock.
# Kick off update.
#    Update thread deep copies PPA object to PPAForUpdateThread.
#    For each PPA...
#        Create a new thread (with sleeps) to get the PPA data, placing results into PPAForUpdateThread.
#        When threads finished, grab lock, deep copy PPA data from PPAForUpdateThread to PPAForMenu, release lock, tell menu to update itself in a new thread (GLib).
#    
# PREVENT USER accessing GUI during update???  
# Maybe disable the menu items?  
# How/when to reenable?  
# When the update thread fully finishes?
# Maybe the build menu method needs a boolean parameter - enable/disable items?
#
# By updating a PPA at a time, does this effect combining?
   

#TODO Depending on the error (if it's a download error), do a redownload of that PPA?


# TODO Need to sort the filter text with each filter.


# TODO Have a sample filter with the sample ppa?


# TODO Test "if A == False" is the same as "if not A".


# TODO When combining, need an option which says if two published binaries have the same package name
# and are architecture dependent, combine only if the version numbers match (or perhaps, ignore version numbers for architecture dependent).
# The dropper package from NoobsLab is NOT architecture specific and multiple version appear.
# So maybe just have a setting "Ignore versions" and nothing to do with architecture specificity.
# Maybe two checkboxes indented under Combine: Ignore Version for Architecture Dependent, Ignore Version for Architecture Independent? 


# TODO Modify the build script and packaging, etc, etc to include the utils.


# TODO Need a preferences tab for filters...
# Perhaps also the add/remove/edit stuff could also be put into the preferences? 


# TODO Add a PPA (after initial PPAs have done their download) and ensure the "downloading now" is shown.


# TODO Possible to have an ignore error...so a PPA with an error is tossed.
# How to let the user know there's an error though?
# If the user unchecks the "hide errors" checkbox, the menu will be rebuilt, with errors displayed
# (and the user may have to uncombine to see message details).


# TODO Perhaps block UI access whilst downloading...
# Can show a message to the user.
# If things are locked when the user is editing/adding/etc and the update kicks off, how to handle this?  Wait?
# Maybe delay for 5 minutes?


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
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html
#  http://launchpad.net/+apidoc
#  http://help.launchpad.net/API/launchpadlib
#  http://help.launchpad.net/API/Hacking


from copy import deepcopy

try:
    from gi.repository import AppIndicator3 as appindicator
except:
    pass

from gi.repository import GLib, Gtk
from threading import Thread
from ppa import PPA, PublishedBinary
from urllib.request import urlopen

import itertools, pythonutils, gzip, json, locale, logging, operator, os, re, shutil, sys, threading, time, webbrowser


class IndicatorPPADownloadStatistics:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-ppa-download-statistics"
    ICON = NAME
    VERSION = "1.0.30"
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    SERIES = [ "trusty", "saucy", "raring", "quantal", "precise", "oneiric", "natty", "maverick", "lucid", "karmic", "jaunty", "intrepid", "hardy", "gutsy", "feisty", "edgy", "dapper", "breezy", "hoary", "warty" ]
    ARCHITECTURES = [ "amd64", "i386" ]

    COMMENTS = "Shows the total downloads of PPAs."
    SVG_ICON = "." + NAME + "-icon"
    SVG_FILE = os.getenv( "HOME" ) + "/" + SVG_ICON + ".svg"

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_PPAS = "ppas"
    SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER = "allowMenuItemsToLaunchBrowser"
    SETTINGS_SORT_BY_DOWNLOAD = "sortByDownload"
    SETTINGS_SORT_BY_DOWNLOAD_AMOUNT = "sortByDownloadAmount"
    SETTINGS_COMBINE_PPAS = "combinePPAs"
    SETTINGS_SHOW_SUBMENU = "showSubmenu"

    MESSAGE_DOWNLOADING_DATA = "(downloading data...)"
    MESSAGE_ERROR_RETRIEVING_PPA = "(error retrieving PPA)"
    MESSAGE_MULTIPLE_MESSAGES_UNCOMBINE = "(multiple messages - uncombine PPAs)"
    MESSAGE_NO_PUBLISHED_BINARIES = "(no published binaries)"


    def __init__( self ):
        self.dialog = None
        self.request = False #TODO Need this?
        self.updateThread = None #TODO Need this?

        GLib.threads_init()
        self.lock = threading.Lock()

        filehandler = logging.FileHandler( filename = IndicatorPPADownloadStatistics.LOG, mode = "a", delay = True )
        logging.basicConfig( format = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s", 
                             datefmt = "%H:%M:%S", level = logging.DEBUG,
                             handlers = [ filehandler ] )

        self.loadSettings()

        try:
            self.appindicatorImported = True
            self.indicator = appindicator.Indicator.new( IndicatorPPADownloadStatistics.NAME, "", appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling...
            self.buildMenu()
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.indicator.set_label( "PPA", "" ) # Second parameter is a guide for how wide the text could get (see label-guide in http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html).

            # Ubuntu 13.10 requires an icon to be set - that is, setting "" as the icon when instantiating the indicator results in a "missing icon" icon.
            # As there is no icon needed (text is the icon), dynamically create a 1 pixel SVG which lives in the user's HOME directory and use that as the icon.
            try:
                with open( IndicatorPPADownloadStatistics.SVG_FILE, "w" ) as f:
                    svg = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
                          '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 1 1"></svg>'
                    f.write( svg )
                    f.close()
                self.indicator.set_icon( IndicatorPPADownloadStatistics.SVG_ICON )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error writing SVG: " + IndicatorPPADownloadStatistics.SVG_FILE )
        except:
            self.appindicatorImported = False            
            self.menu = Gtk.Menu() # Set an empty menu to get things rolling...
            self.buildMenu()
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorPPADownloadStatistics.ICON )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.requestPPADownloadAndMenuRefresh()
        GLib.timeout_add_seconds( 6 * 60 * 60, self.requestPPADownloadAndMenuRefresh ) # Auto update every 6 hours.
        Gtk.main()


    def buildMenu( self ):
        if self.appindicatorImported:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if we don't do this we get GTK complaints).

        menu = Gtk.Menu()

        # Add PPAs to the menu...
        ppas = deepcopy( self.ppasNEW ) # Leave the original download data as is - makes dynamic (user) changes faster (don't have to re-download).

        self.filter( ppas )
        if self.combinePPAs: self.combine( ppas )
        if self.sortByDownload: self.sortByDownloadAndClip( ppas )

        indent = "    "
        if self.showSubmenu:
            for ppa in ppas:
                menuItem = Gtk.MenuItem( ppa.getKey() )
                menu.append( menuItem )
                subMenu = Gtk.Menu()

                if ppa.getStatus() == PPA.STATUS_OK:
                    publishedBinaries = ppa.getPublishedBinaries()
                    for publishedBinary in publishedBinaries:
                        if publishedBinary.getPackageVersion() is None:
                            label = indent + publishedBinary.getPackageName() + ": " + str( publishedBinary.getDownloadCount() )
                        else:
                            label = indent + publishedBinary.getPackageName() + " (" + publishedBinary.getPackageVersion() + "): " + str( publishedBinary.getDownloadCount() )

                        subMenuItem = Gtk.MenuItem( label )
                        subMenuItem.set_name( ppa.getKey() )
                        subMenuItem.connect( "activate", self.onPPA )
                        subMenu.append( subMenuItem )
                        menuItem.set_submenu( subMenu )
                else:
                    if ppa.getStatus() == PPA.STATUS_ERROR_RETRIEVING_PPA:
                        message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_RETRIEVING_PPA
                    elif ppa.getStatus() == PPA.STATUS_NEEDS_DOWNLOAD:
                        message = IndicatorPPADownloadStatistics.MESSAGE_DOWNLOADING_DATA
                    elif ppa.getStatus() == PPA.STATUS_NO_PUBLISHED_BINARIES:
                        message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES
                    else:
# TODO Need to first check if we're combined before saying "uncombine to show the messages"?
# Is it possible to be uncombined and have the multiple errors?
                        message = IndicatorPPADownloadStatistics.MESSAGE_MULTIPLE_MESSAGES_UNCOMBINE

                    subMenuItem = Gtk.MenuItem( indent + message )
                    subMenu.append( subMenuItem )
                    menuItem.set_submenu( subMenu )

        else:
            for ppa in ppas:
                menuItem = Gtk.MenuItem( ppa.getKey() )
                menu.append( menuItem )
                menuItem.set_name( ppa.getKey() )
                menuItem.connect( "activate", self.onPPA )

                if ppa.getStatus() == PPA.STATUS_OK:
                    publishedBinaries = ppa.getPublishedBinaries()
                    for publishedBinary in publishedBinaries:
                        if publishedBinary.getPackageVersion() is None:
                            label = indent + publishedBinary.getPackageName() + ": " + str( publishedBinary.getDownloadCount() )
                        else:
                            label = indent + publishedBinary.getPackageName() + " (" + publishedBinary.getPackageVersion() + "): " + str( publishedBinary.getDownloadCount() )

                        menuItem = Gtk.MenuItem( label )
                        menuItem.set_name( ppa.getKey() )
                        menuItem.connect( "activate", self.onPPA )
                        menu.append( menuItem )
                else:
                    if ppa.getStatus() == PPA.STATUS_ERROR_RETRIEVING_PPA:
                        message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_RETRIEVING_PPA
                    elif ppa.getStatus() == PPA.STATUS_NEEDS_DOWNLOAD:
                        message = IndicatorPPADownloadStatistics.MESSAGE_DOWNLOADING_DATA
                    elif ppa.getStatus() == PPA.STATUS_NO_PUBLISHED_BINARIES:
                        message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES
                    else:
# TODO Need to first check if we're combined before saying "uncombine to show the messages"?
# Is it possible to be uncombined and have the multiple errors?
                        message = IndicatorPPADownloadStatistics.MESSAGE_MULTIPLE_MESSAGES_UNCOMBINE

                    menuItem = Gtk.MenuItem( indent + message )
                    menu.append( menuItem )

        menu.append( Gtk.SeparatorMenuItem() )

        addMenuItem = Gtk.MenuItem( "Add a PPA" )
        addMenuItem.connect( "activate", self.onAdd )
        menu.append( addMenuItem )

        oneOrMorePPAsExist = len( ppas ) > 0
        editMenuItem = Gtk.MenuItem( "Edit a PPA" )
        editMenuItem.set_sensitive( oneOrMorePPAsExist )
        menu.append( editMenuItem )

        if( oneOrMorePPAsExist ):
            subMenu = Gtk.Menu()
            editMenuItem.set_submenu( subMenu )
            for ppa in ppas:
                subMenuItem = Gtk.MenuItem( ppa.getKey() )
                subMenuItem.set_name( ppa.getKey() )
                subMenuItem.connect( "activate", self.onEdit )
                subMenu.append( subMenuItem )

        removeMenuItem = Gtk.MenuItem( "Remove a PPA" )
        removeMenuItem.set_sensitive( oneOrMorePPAsExist )
        menu.append( removeMenuItem )

        if( oneOrMorePPAsExist ):
            subMenu = Gtk.Menu()
            removeMenuItem.set_submenu( subMenu )
            for ppa in ppas:
                subMenuItem = Gtk.MenuItem( ppa.getKey() )
                subMenuItem.set_name( ppa.getKey() )
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

        if self.appindicatorImported:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu

        menu.show_all()


    def filter( self, ppas ):
        for ppa in ppas:
            key = ppa.getUser() + " | " + ppa.getName()
            if not key in self.filters:
                continue

            publishedBinaries = ppa.getPublishedBinaries()
            for i in range( len( publishedBinaries ) - 1, -1, -1 ): # Iterate backwards, enabling a "simpler" way to delete elements.
                publishedBinary = publishedBinaries[ i ]
                match = False
                for filter in self.filters.get( key ):
                    if filter in publishedBinary.getPackageName():
                        match = True
                        break

                if not match:
                    del publishedBinaries[ i ]


    def combine( self, ppas ):
        combinedPPAs = { } # Key is the PPA simple key; value is the combined ppa (the series/architecture are set to None).

        # Match up identical PPAs.  Two PPAs match if their 'PPA User | PPA Name' are identical.
        # If a PPA's status is anything other than OK, that PPA's error status is now THE status for all matching PPAs.
        for ppa in ppas:
            key = ppa.getUser() + " | " + ppa.getName()
            if key in combinedPPAs:
                if ppa.getStatus() == PPA.STATUS_OK and combinedPPAs[ key ].getStatus() == PPA.STATUS_OK:
                    combinedPPAs[ key ].getPublishedBinaries().extend( ppa.getPublishedBinaries() )

                else:
                    # The existing ppa or the current ppa has an error (or both)...
                    if ppa.getStatus() == combinedPPAs[ key ].getStatus():
                        continue # Same error, so nothing to do.

                    elif combinedPPAs[ key ].getStatus() == PPA.STATUS_OK:
                        combinedPPAs[ key ].setStatus( ppa.getStatus() ) # The current PPA has an error, so that becomes the new status.
                        combinedPPAs[ key ].setPublishedBinaries( [ ] )

                    elif ppa.getStatus() != combinedPPAs[ key ].getStatus():
                        combinedPPAs[ key ].setStatus( PPA.STATUS_MULTIPLE_ERRORS ) # The combined PPA and the current PPA have different errors, so set a combined error.

                    else:
                        continue # Current PPA is OK but the existing PPA is in error...so nothing to do but keep the error.

            else:
                # No previous match for this PPA.  Nullify the series/architecture as they are no longer relevent when combined.
                ppa.setSeries( None )
                ppa.setArchitecture( None )
                if ppa.getStatus() != PPA.STATUS_OK:  #TODO Is this necessary?  Surely if there's an error the downloader should wipe the PPA object of PBs?
                    ppa.setPublishedBinaries( [ ] )

                combinedPPAs[ key ] = ppa

# TODO Handle this...
#         self.ignoreVersionInArchitectureSpecific = True
# Assuming for now the version IS ignored in architecture specific.
# See note at top of file.

        # Now have a hash table containing ppas which either have an error status or are a concatenation of all published binaries from ppas with the same PPA User/Name.
        del ppas[ : ] # In place remove all elements.
        for key in combinedPPAs:
            temp = { }
            ppa = combinedPPAs[ key ]
            publishedBinaries = ppa.getPublishedBinaries() # A PPA with a status other than OK will have no published binaries...
            for publishedBinary in publishedBinaries:
                key = publishedBinary.getPackageName() + " | " + publishedBinary.getPackageVersion()
                if publishedBinary.isArchitectureSpecific():
                    key = publishedBinary.getPackageName()
                    publishedBinary.setPackageVersion( None )

                if not key in temp:
                    temp[ key ] = publishedBinary
                    continue

                if publishedBinary.isArchitectureSpecific():
                    temp[ key ].setDownloadCount( temp[ key ].getDownloadCount() + publishedBinary.getDownloadCount() )

            publishedBinaries = [ ]
            for key in temp:
                publishedBinaries.append( temp[ key ] )

            publishedBinaries.sort( key = operator.methodcaller( "__str__" ) )
            ppa.setPublishedBinaries( publishedBinaries )
            ppas.append( ppa  )

        ppas.sort( key = operator.methodcaller( "getKey" ) )


    def sortByDownloadAndClip( self, ppas ):
        for ppa in ppas:
            ppa.getPublishedBinaries().sort( key = operator.methodcaller( "getDownloadCount" ), reverse = True )
            
            if self.sortByDownloadAmount > 0:
                del ppa.getPublishedBinaries()[ self.sortByDownloadAmount : ]


    def getPPAUsersSorted( self ):
        sortedPPAUsers = [ ] 
        for key in list( self.ppas.keys() ):
            ppaUser = self.ppas[ key ].getUser()
            if ppaUser not in sortedPPAUsers:
                sortedPPAUsers.append( ppaUser )

        return sorted( sortedPPAUsers, key = locale.strxfrm )


    def getPPANamesSorted( self ):
        sortedPPANames = [ ] 
        for key in list( self.ppas.keys() ):
            ppaName = self.ppas[ key ].getName()
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

        webbrowser.open( url ) # This returns a boolean - showing the user a message on a false return value causes a lock up!


    def onAbout( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.dialog = pythonutils.AboutDialog( 
               IndicatorPPADownloadStatistics.NAME,
               IndicatorPPADownloadStatistics.COMMENTS, 
               IndicatorPPADownloadStatistics.WEBSITE, 
               IndicatorPPADownloadStatistics.WEBSITE, 
               IndicatorPPADownloadStatistics.VERSION, 
               Gtk.License.GPL_3_0, 
               IndicatorPPADownloadStatistics.ICON,
               [ IndicatorPPADownloadStatistics.AUTHOR ],
               "",
               "",
               "/usr/share/doc/" + IndicatorPPADownloadStatistics.NAME + "/changelog.Debian.gz",
               logging )

        self.dialog.run()
        self.dialog.destroy()
        self.dialog = None



    def onAdd( self, widget ):
        self.addEditPPA( True, "", "", IndicatorPPADownloadStatistics.SERIES[ 0 ], IndicatorPPADownloadStatistics.ARCHITECTURES[ 0 ] )


    def onEdit( self, widget ):
        ppa = self.ppas.get( widget.props.name )
        self.addEditPPA( False, ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() )


    def addEditPPA( self, add, existingPPAUser, existingPPAName, existingSeries, existingArchitecture ):
        if self.dialog is not None:
            segetPPAKeylf.dialog.present()
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

        self.dialog = Gtk.Dialog( title, None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( grid, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorPPADownloadStatistics.ICON )

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
                pythonutils.showMessage( Gtk.MessageType.ERROR, "PPA user cannot be empty." )
                ppaUser.grab_focus()
                continue

            if ppaNameValue == "":
                pythonutils.showMessage( Gtk.MessageType.ERROR, "PPA name cannot be empty." )
                ppaName.grab_focus()
                continue

            ppaList = [ ppaUserValue, ppaNameValue, series.get_active_text(), architectures.get_active_text() ]
            key = self.getPPAKey( ppaList )
            if key not in self.ppas: # If there is no change, there is nothing to do...
                if add:
                    self.ppas[ key ] = PPA( ppaList[ 0 ], ppaList[ 1 ], ppaList[ 2 ], ppaList[ 3 ] )
                else: # This is an edit...we are 'renaming' the PPA key, but the PPA download data is still present under the old key!
                    oldKey = self.getPPAKey( [ existingPPAUser, existingPPAName, existingSeries, existingArchitecture ] )
                    del self.ppas[ oldKey ]
                    self.ppas[ key ] = PPA( ppaList[ 0 ], ppaList[ 1 ], ppaList[ 2 ], ppaList[ 3 ] )

                self.setToDownloadingData()
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


    def onRemove( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.dialog = Gtk.MessageDialog( None, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, "Remove the PPA '" + widget.props.name + "'?" )
        response = self.dialog.run()
        self.dialog.destroy()
        if response == Gtk.ResponseType.OK:
            del self.ppas[ widget.props.name ]
            self.saveSettings()
            self.setToDownloadingData()
            GLib.timeout_add_seconds( 1, self.buildMenu ) # If we update the menu directly, GTK complains that the menu (which kicked off preferences) no longer exists.
            self.requestPPADownloadAndMenuRefresh()

        self.dialog = None


    def onPreferences( self, widget ):

        if self.dialog is not None:
            self.dialog.present()
            return

        notebook = Gtk.Notebook()

        # First tab - PPAs.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

# TODO Add/edit/remove ppas.

        notebook.append_page( grid, Gtk.Label( "PPAs" ) )

        # Second tab - filters.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        store = Gtk.ListStore( str, str ) # 'PPA User | PPA Name', filter text.
        keys = {  }
        for ppa in self.ppasNEW:
            key = ppa.getUser() + " | " + ppa.getName()

            if key in keys:
                continue # Add each 'PPA User | PPA Name' once!

            keys[ key ] = key
            if key in self.filters:
                store.append( [ key, "\n".join( self.filters[ key ] ) ] )
            else:
                store.append( [ key, "" ] )

        tree = Gtk.TreeView( store )
        tree.set_hexpand( True )
        tree.set_vexpand( True )
        tree.append_column( Gtk.TreeViewColumn( "PPA", Gtk.CellRendererText(), text = 0 ) )
        tree.append_column( Gtk.TreeViewColumn( "Filter", Gtk.CellRendererText(), text = 1 ) )
        tree.set_tooltip_text( "Double click to add/modify a filter." )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )

        scrolledWindow = Gtk.ScrolledWindow()

# TODO Not sure about this...
        # The treeview won't expand to show all data, even for a small amount of data.
        # So only add scrollbars if there is a lot of data...greater than 15 say...
#         if len( self.virtualMachineInfos ) <= 15:
#             scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER )
#         else:
#             scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )

        scrolledWindow.set_policy( Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 0, 2, 1 )

        hbox = Gtk.Box( spacing = 6 )

        label = Gtk.Label( "Filter" )
        hbox.pack_start( label, False, False, 0 )

        filterText = Gtk.Entry()
#         filterText.set_text( )
#         filterText.set_tooltip_text( "The text shown next to the icon (or tooltip, where applicable)" )
        hbox.pack_start( filterText, True, True, 0 )

        apply = Gtk.Button( "Apply" )
#         apply.connect( "clicked", self.onApply, filterText )
#         apply.set_tooltip_text( "Notifications are not possible on your system" )

        hbox.pack_start( apply, False, False, 0 )

        grid.attach( hbox, 0, 1, 2, 1 )

#         tree.connect( "row-activated", self.onFilterDoubleClick, filterText )

        notebook.append_page( grid, Gtk.Label( "Filters" ) )

        # Third tab - display settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showAsSubmenusCheckbox = Gtk.CheckButton( "Show PPAs as submenus" )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )
        grid.attach( showAsSubmenusCheckbox, 0, 0, 2, 1 )

        combinePPAsCheckbox = Gtk.CheckButton( "Combine PPAs" )
        toolTip = "Combines the statistics when the PPA user/name are the same.\n\n"
        toolTip += "If a published binary is architecture specific (such as compiled C), the download counts are summed across all instances of that published binary.\n\n"
        toolTip += "If a published binary is not architecture specific (such as Python), the download counts are only summed when the version of the binary is different.\n\n"
        toolTip += "The version number is retained only if it is identical across all instances of a published binary."
        combinePPAsCheckbox.set_tooltip_text( toolTip )
        combinePPAsCheckbox.set_active( self.combinePPAs )
        grid.attach( combinePPAsCheckbox, 0, 1, 2, 1 )

# So maybe just have a setting "Ignore versions" and nothing to do with architecture specificity.
# Maybe two checkboxes indented under Combine: Ignore Version for Architecture Dependent, Ignore Version for Architecture Independent? 

        ignoreVersionArchitectureDependentCheckbox = Gtk.CheckButton( "Ignore Version for Architecture Dependent" )
        ignoreVersionArchitectureDependentCheckbox.set_margin_left( 15 )
        ignoreVersionArchitectureDependentCheckbox.set_tooltip_text( "TODO" ) #TODO
        ignoreVersionArchitectureDependentCheckbox.set_active( True ) #TODO Fix
        grid.attach( ignoreVersionArchitectureDependentCheckbox, 0, 2, 2, 1 )

        ignoreVersionArchitectureIndependentCheckbox = Gtk.CheckButton( "Ignore Version for Architecture Independent" )
        ignoreVersionArchitectureIndependentCheckbox.set_margin_left( 15 )
        ignoreVersionArchitectureIndependentCheckbox.set_tooltip_text( "TODO" ) #TODO
        ignoreVersionArchitectureIndependentCheckbox.set_active( True ) #TODO Fix
        grid.attach( ignoreVersionArchitectureIndependentCheckbox, 0, 3, 2, 1 )

        sortByDownloadCheckbox = Gtk.CheckButton( "Sort By Download" )
        sortByDownloadCheckbox.set_tooltip_text( "Sort by download (highest first) within each PPA." )
        sortByDownloadCheckbox.set_active( self.sortByDownload )
        grid.attach( sortByDownloadCheckbox, 0, 4, 2, 1 )

        label = Gtk.Label( "  Clip Amount" )
        label.set_sensitive( sortByDownloadCheckbox.get_active() )
        label.set_margin_left( 15 )
        grid.attach( label, 0, 5, 1, 1 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.sortByDownloadAmount, 0, 10000, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinner.set_value( self.sortByDownloadAmount ) # ...so need to force the initial value by explicitly setting it.
        spinner.set_tooltip_text( "Limit the number of entries when sorting by download.\nA value of zero will not clip." )
        spinner.set_sensitive( sortByDownloadCheckbox.get_active() )
        spinner.set_hexpand( True )
        grid.attach( spinner, 1, 5, 1, 1 )

        sortByDownloadCheckbox.connect( "toggled", self.onClipByDownloadCheckbox, label, spinner )

        ignoreErrorsCheckbox = Gtk.CheckButton( "Ignore Errors" )
        ignoreErrorsCheckbox.set_tooltip_text( "TODO" )
        ignoreErrorsCheckbox.set_active( True ) #TODO
        grid.attach( ignoreErrorsCheckbox, 0, 6, 2, 1 )

        notebook.append_page( grid, Gtk.Label( "Display" ) )

        # Fourth tab - general settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        allowMenuItemsToLaunchBrowserCheckbox = Gtk.CheckButton( "Open PPA in browser" )
        allowMenuItemsToLaunchBrowserCheckbox.set_tooltip_text( "Clicking a PPA menu item launches the default web browser, loading the PPA's page." )
        allowMenuItemsToLaunchBrowserCheckbox.set_active( self.allowMenuItemsToLaunchBrowser )
        grid.attach( allowMenuItemsToLaunchBrowserCheckbox, 0, 0, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorPPADownloadStatistics.AUTOSTART_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "General" ) )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorPPADownloadStatistics.ICON )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.showSubmenu = showAsSubmenusCheckbox.get_active()
            self.combinePPAs = combinePPAsCheckbox.get_active()
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


#     def onFilterDoubleClick( self, tree, rowNumber, treeViewColumn, displayPattern ):
#         model, treeiter = tree.get_selection().get_selected()
#         displayPattern.insert_text( "[" + model[ treeiter ][ 0 ] + "]", displayPattern.get_position() )


#     def onApply( self, tree, rowNumber, treeViewColumn, displayPattern ):
#         model, treeiter = tree.get_selection().get_selected()
#         displayPattern.insert_text( "[" + model[ treeiter ][ 0 ] + "]", displayPattern.get_position() )


    def loadSettings( self ):
        self.allowMenuItemsToLaunchBrowser = True
        self.sortByDownload = False
        self.sortByDownloadAmount = 3
        self.combinePPAs = False
        self.showSubmenu = False
        self.filters = { }

# TODO Rename - remove the NEW
        self.ppasNEW = [ ]

        if os.path.isfile( IndicatorPPADownloadStatistics.SETTINGS_FILE ):
            try:
                with open( IndicatorPPADownloadStatistics.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                ppas = settings.get( IndicatorPPADownloadStatistics.SETTINGS_PPAS, [ ] )
                for ppa in ppas:
                    self.ppasNEW.append( PPA( ppa[ 0 ], ppa[ 1 ], ppa[ 2 ], ppa[ 3 ] ) )

                self.ppasNEW.sort( key = operator.methodcaller( "getKey" ) )

#TODO Load filters and remove these...
                self.filters[ 'noobslab | indicators' ] = [ "indicator-fortune", "indicator-lunar", "indicator-ppa-download-statistics", "indicator-stardate", "indicator-virtual-box", "python3-ephem" ]
                self.filters[ 'whoopie79 | ppa' ] = [ "indicator-fortune", "indicator-lunar", "indicator-ppa-download-statistics", "indicator-stardate", "indicator-virtual-box", "python3-ephem" ]

                self.allowMenuItemsToLaunchBrowser = settings.get( IndicatorPPADownloadStatistics.SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER, self.allowMenuItemsToLaunchBrowser )
                self.sortByDownload = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD, self.sortByDownload )
                self.sortByDownloadAmount = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD_AMOUNT, self.sortByDownloadAmount )
                self.combinePPAs = settings.get( IndicatorPPADownloadStatistics.SETTINGS_COMBINE_PPAS, self.combinePPAs )
                self.showSubmenu = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SHOW_SUBMENU, self.showSubmenu )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorPPADownloadStatistics.SETTINGS_FILE )
# TODO Delete the settings file...alert the user?                
                self.initialiseDefaultSettings()
        else:
            # No properties file exists, so populate with a sample PPA to give the user an idea of the format.
            self.initialiseDefaultSettings()


    def initialiseDefaultSettings( self ):
        self.ppasNEW = [ ]
        self.ppasNEW.append( PPA( "thebernmeister", "ppa", "precise", "amd64" ) )
        self.filters = { }
        self.filters[ 'thebernmeister | ppa' ] = [ "indicator-fortune", "indicator-lunar", "indicator-ppa-download-statistics", "indicator-stardate", "indicator-virtual-box", "python3-ephem" ]


    def saveSettings( self ):
# TODO...fix!
        try:
            ppas = [ ]
            for k, v in list( self.ppas.items() ):
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


    def requestPPADownloadAndMenuRefresh( self ):
#         self.lock.acquire()
#         Thread( target = self.getPPADownloadStatistics ).start()

# TODO Why need to return?
        return True 


    # Get a list of the published binaries for each PPA.
    # From that extract the ID for each binary which is then used to get the download count for each binary.
    # The ID is the number at the end of self_link.
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
    def getPPADownloadStatistics( self ):
# TODO Maybe the acquire lock should be done here and here only...released at the end of this function?
# The caller might get "interrupted" between creating the thread and starting...
# A user could start an edit/add/remove between create and start (unlikely but possible).
# So what should be done?  Leave the lock in the caller...but that's the only place the lock occurs for the download stuff.
# The update menu code then also grabs/releases the same lock?
        threads = []
        for ppa in self.ppasNEW:
            ppa.reset()
            t = Thread( target = self.getPublishedBinariesOLD, args = ( [ ppa ] ), )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()

        self.lock.release()
        GLib.idle_add( self.buildMenu )


    def getPublishedBinaries( self, ppa ):
        threads = []

        publishedBinariesURL = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName() + \
                "?ws.op=getPublishedBinaries&status=Published&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + \
                ppa.getSeries() + "/" + ppa.getArchitecture()

        try:
            publishedBinaries = json.loads( urlopen( publishedBinariesURL ).read().decode( "utf8" ) )
            numberOfPublishedBinaries = publishedBinaries[ "total_size" ]
            if numberOfPublishedBinaries == 0:
                ppa.setStatus( PPA.STATUS_NO_PUBLISHED_BINARIES )
                ppa.setPublishedBinaries( [ ] )
            else:
                # The results are returned in lots of 75...so need to retrieve each lot after the first 75.
                index = 0
                resultPage = 1
                resultsPerUrl = 75
                for i in range( numberOfPublishedBinaries ):
                    if i == ( resultPage * resultsPerUrl ): # This loops handles results on pages after the first page.
                        newURL = publishedBinariesURL + "&ws.start=" + str( resultPage * resultsPerUrl )
                        publishedBinaries = json.loads( urlopen( newURL ).read().decode( "utf8" ) )
                        resultPage += 1
                        index = 0

                    packageName = publishedBinaries[ "entries" ][ index ][ "binary_package_name" ]
                    packageVersion = publishedBinaries[ "entries" ][ index ][ "binary_package_version" ]
                    architectureSpecific = publishedBinaries[ "entries" ][ index ][ "architecture_specific" ]
                    indexLastSlash = publishedBinaries[ "entries" ][ index ][ "self_link" ].rfind( "/" )
                    packageId = publishedBinaries[ "entries" ][ index ][ "self_link" ][ indexLastSlash + 1 : ]

                    t = Thread( target = self.getDownloadCountOLD, args = ( ppa, packageName, packageVersion, architectureSpecific, packageId ), )
                    threads.append( t )
                    t.start()

                    index += 1

                for t in threads:
                    t.join()

                ppa.noMorePublishedBinariesToAdd()

        except Exception as e:
            logging.exception( e )
            ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )
            ppa.setPublishedBinaries( [ ] )


    def getDownloadCount( self, ppa, packageName, packageVersion, architectureSpecific, packageId ):

        try:
            downloadCountURL = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName() + "/+binarypub/" + packageId + "?ws.op=getDownloadCount"
            downloadCount = json.loads( urlopen( downloadCountURL ).read().decode( "utf8" ) )
            if str( downloadCount ).isnumeric():
                ppa.addPublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific )
            else:
                ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )
                ppa.setPublishedBinaries( [ ] )

        except Exception as e:
            logging.exception( e )
            ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )
            ppa.setPublishedBinaries( [ ] )

if __name__ == "__main__": IndicatorPPADownloadStatistics().main()