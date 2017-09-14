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


# Application indicator which displays PPA download statistics.


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://developer.gnome.org/gnome-devel-demos
#  http://python-gtk-3-tutorial.readthedocs.org
#  http://wiki.gnome.org/Projects/PyGObject/Threading
#  http://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/AppIndicator3-0.1
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://launchpad.net/+apidoc
#  http://help.launchpad.net/API/launchpadlib
#  http://help.launchpad.net/API/Hacking


INDICATOR_NAME = "indicator-ppa-download-statistics"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "Notify", "0.7" )

from copy import deepcopy
from gi.repository import AppIndicator3, GLib, Gtk, Notify
from ppa import PPA, PublishedBinary
from threading import Thread
from urllib.request import urlopen
import concurrent.futures, json, locale, logging, operator, os, pythonutils, threading, webbrowser


class IndicatorPPADownloadStatistics:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.58"
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"
    COMMENTS = _( "Diaplay the total downloads of PPAs." )

    SERIES = [ "artful", "zesty",
              "yakkety", "xenial", "wily", "vivid", "utopic",
              "trusty", "saucy", "raring", "quantal", "precise",
              "oneiric", "natty", "maverick", "lucid", "karmic",
              "jaunty", "intrepid", "hardy", "gutsy", "feisty",
              "edgy", "dapper", "breezy", "hoary", "warty" ]

    ARCHITECTURES = [ "amd64", "i386" ]

    INDENT = "    "

    CONFIG_COMBINE_PPAS = "combinePPAs"
    CONFIG_FILTERS = "filters"
    CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC = "ignoreVersionArchitectureSpecific"
    CONFIG_PPAS = "ppas"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_SORT_BY_DOWNLOAD = "sortByDownload"
    CONFIG_SORT_BY_DOWNLOAD_AMOUNT = "sortByDownloadAmount"

    MESSAGE_DOWNLOADING_DATA = _( "(downloading data...)" )
    MESSAGE_ERROR_RETRIEVING_PPA = _( "(error retrieving PPA)" )
    MESSAGE_MULTIPLE_MESSAGES_UNCOMBINE = _( "(multiple messages - uncombine PPAs)" )
    MESSAGE_NO_PUBLISHED_BINARIES = _( "(no published binaries)" )
    MESSAGE_PUBLISHED_BINARIES_COMPLETELY_FILTERED = _( "(published binaries completely filtered)" )


    def __init__( self ):
        logging.basicConfig( format = pythonutils.LOGGING_BASIC_CONFIG_FORMAT, level = pythonutils.LOGGING_BASIC_CONFIG_LEVEL, handlers = [ pythonutils.TruncatedFileHandler( IndicatorPPADownloadStatistics.LOG ) ] )

        self.downloading = False
        self.downloadInProgress = False
#         self.preferencesOpen = False
        self.quitRequested = False

        self.dialogLock = threading.Lock()
        self.lock = threading.Lock() #TODO Needed by whom, if at all?
        Notify.init( INDICATOR_NAME )
        pythonutils.migrateConfig( INDICATOR_NAME ) # Migrate old user configuration to new location.
        self.loadConfig()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorPPADownloadStatistics.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

#         self.buildMenu() # Menu will initially contain a download status message.
        self.update( True )
#         self.buildMenu()
#         self.requestPPADownloadAndMenuRefresh( False )
#         GLib.timeout_add_seconds( 6 * 60 * 60, self.requestPPADownloadAndMenuRefresh, True ) # Auto update every six hours.

#TODO Make sure the seconds param passed to GLib.timeout_add_seconds has int( )


    def main( self ): Gtk.main()


#TODO...
#
# Init - set PPA status to need download; build menu
#      - kick off download; build menu after download
#
# Scheduled update - kick off download; build menu after download
#
# Preferences change - set PPA status to need download; build menu
#                    - kick off download; build menu after download
#
# Saving preferences whilst a download is underway - cancel current download and kick off new one?
# User quits while download is underway - monitor a flag and cancel download ASAP.


    def update( self, scheduled ):
        with threading.Lock():
#             if not scheduled:
#                 GLib.source_remove( self.updateTimerID )

#TODO Cancel existing download if underway.            
#TODO Perhaps here have a simple build Menu that just has the About/Pref/Quit and a message "downloading..."?
            self.buildMenu() # Menu will initially contain a download status message as the PPA data should (must) be empty of statistics.  #TODO How to enforce this?
            self.downloading = True
#             Thread( target = self.getPPADownloadStatistics ).start()
            Thread( target = self.getPPADownloadStatisticsNEW ).start()
#             self.requestPPADownloadAndMenuRefresh( False )
#             GLib.timeout_add_seconds( 6 * 60 * 60, self.requestPPADownloadAndMenuRefresh, True ) # Auto update every six hours.

#             self.buildMenu()
#             self.updateTimerID = GLib.timeout_add_seconds( self.fiveSecondsAfterMidnight(), self.update, True )


    def buildMenu( self ):
        menu = Gtk.Menu()
        ppas = deepcopy( self.ppas ) # Leave the original download data as is - makes dynamic (user) changes faster (don't have to re-download).

        if self.combinePPAs:
            self.combine( ppas )

        if self.sortByDownload:
            self.sortByDownloadAndClip( ppas )

        if self.showSubmenu:
            for ppa in ppas:
                menuItem = Gtk.MenuItem( ppa.getKey() )
                menu.append( menuItem )
                subMenu = Gtk.Menu()
                if ppa.getStatus() == PPA.STATUS_OK:
                    publishedBinaries = ppa.getPublishedBinaries()
                    for publishedBinary in publishedBinaries:
                        self.createMenuItemForPublishedBinary( subMenu, ppa, publishedBinary )
                        menuItem.set_submenu( subMenu )
                else:
                    self.createMenuItemForStatusMessage( subMenu, ppa )
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
                        self.createMenuItemForPublishedBinary( menu, ppa, publishedBinary )
                else:
                    self.createMenuItemForStatusMessage( menu, ppa )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, True, self.onPreferences, self.onAbout, self.quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def createMenuItemForPublishedBinary( self, menu, ppa, publishedBinary ):
        label = IndicatorPPADownloadStatistics.INDENT + publishedBinary.getPackageName()
        if publishedBinary.getPackageVersion() is None:
            label += ":  " + str( publishedBinary.getDownloadCount() )
        else:
            label += " " + publishedBinary.getPackageVersion() + ":  " + str( publishedBinary.getDownloadCount() )

        menuItem = Gtk.MenuItem( label )
        menuItem.set_name( ppa.getKey() )
        menuItem.connect( "activate", self.onPPA )
        menu.append( menuItem )


    def createMenuItemForStatusMessage( self, menu, ppa ):
        if ppa.getStatus() == PPA.STATUS_ERROR_RETRIEVING_PPA:
            message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_RETRIEVING_PPA
        elif ppa.getStatus() == PPA.STATUS_NEEDS_DOWNLOAD:
            message = IndicatorPPADownloadStatistics.MESSAGE_DOWNLOADING_DATA
        elif ppa.getStatus() == PPA.STATUS_NO_PUBLISHED_BINARIES:
            message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES
        elif ppa.getStatus() == PPA.STATUS_PUBLISHED_BINARIES_COMPLETELY_FILTERED:
            message = IndicatorPPADownloadStatistics.MESSAGE_PUBLISHED_BINARIES_COMPLETELY_FILTERED
        else:
            message = IndicatorPPADownloadStatistics.MESSAGE_MULTIPLE_MESSAGES_UNCOMBINE

        menuItem = Gtk.MenuItem( IndicatorPPADownloadStatistics.INDENT + message )
        menu.append( menuItem )


    def quit( self, widget ):
        if not self.quitRequested:
            self.quitRequested = True  #TODO What is the logic here?
            Gtk.main_quit()


    def combine( self, ppas ):
        combinedPPAs = { } # Key is the PPA simple key; value is the combined ppa (the series/architecture are set to None).

        # Match up identical PPAs: two PPAs are deemed to match if their 'PPA User | PPA Name' are identical.
        for ppa in ppas:
            key = ppa.getUser() + " | " + ppa.getName()
            if key in combinedPPAs:
                if ppa.getStatus() == combinedPPAs[ key ].getStatus():
                    combinedPPAs[ key ].addPublishedBinaries( ppa.getPublishedBinaries() )
                elif combinedPPAs[ key ].getStatus() == PPA.STATUS_OK:
                    combinedPPAs[ key ].setStatus( ppa.getStatus() ) # The current PPA has an error, so that becomes the new status.
                else:
                    combinedPPAs[ key ].setStatus( PPA.STATUS_MULTIPLE_ERRORS ) # The combined PPA and the current PPA have different errors, so set a combined error.

            else:
                # No previous match for this PPA.
                ppa.nullifyArchitectureSeries()
                combinedPPAs[ key ] = ppa

        # The combined ppas either have:
        #    An error status (and no published binaries) or,
        #    An OK status are a concatenation of all published binaries from ppas with the same PPA User/Name.
        del ppas[ : ] # Remove all elements (and keep reference to original variable).
        for ppa in combinedPPAs.values():
            temp = { }
            for publishedBinary in ppa.getPublishedBinaries():
                key = publishedBinary.getPackageName() + " | " + publishedBinary.getPackageVersion()
                if publishedBinary.isArchitectureSpecific() and self.ignoreVersionArchitectureSpecific:
                    key = publishedBinary.getPackageName() # The key for architecture specific drops the version number.
                    publishedBinary.setPackageVersion( None )

                if not key in temp:
                    temp[ key ] = publishedBinary
                    continue

                if publishedBinary.isArchitectureSpecific():
                    temp[ key ].setDownloadCount( temp[ key ].getDownloadCount() + publishedBinary.getDownloadCount() ) # Append the download count.

            ppa.resetPublishedBinaries()
            for key in temp:
                ppa.addPublishedBinary( temp[ key ] )

            if ppa.getStatus() == PPA.STATUS_OK:
                ppa.setStatus( PPA.STATUS_OK ) # This will force the published binaries to be sorted.

            ppas.append( ppa  )

        ppas.sort( key = operator.methodcaller( "getKey" ) )


    def sortByDownloadAndClip( self, ppas ):
        for ppa in ppas:
            ppa.sortPublishedBinariesByDownloadCountAndClip( self.sortByDownloadAmount )


    def onPPA( self, widget ):
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

        webbrowser.open( url ) # This returns a boolean indicating success or failure; showing the user a message on a false return value causes a lock up!


    def onAbout( self, widget ):
        if self.dialogLock.acquire( blocking = False ):
            pythonutils.showAboutDialog(
                [ IndicatorPPADownloadStatistics.AUTHOR ],
                IndicatorPPADownloadStatistics.COMMENTS, 
                [ ],
                "",
                Gtk.License.GPL_3_0,
                IndicatorPPADownloadStatistics.ICON,
                INDICATOR_NAME,
                IndicatorPPADownloadStatistics.WEBSITE,
                IndicatorPPADownloadStatistics.VERSION,
                _( "translator-credits" ),
                _( "View the" ),
                _( "text file." ),
                _( "changelog" ) )

            self.dialogLock.release()


    def onPreferences( self, widget ):
#         if self.downloadInProgress:
#             Notify.Notification.new( _( "Downloading data..." ), _( "Preferences are currently unavailable." ), IndicatorPPADownloadStatistics.ICON ).show()
#             return
# 
        if self.dialogLock.acquire( blocking = False ):
            self._onPreferences( widget )
            self.dialogLock.release()


    def _onPreferences( self, widget ):
#         if self.downloadInProgress:
#             Notify.Notification.new( _( "Downloading data..." ), _( "Preferences are currently unavailable." ), IndicatorPPADownloadStatistics.ICON ).show()
#             return
# 
#         with self.lock:
#             self.preferencesOpen = True #TODO Maybe when an update occurs, disable the menu (except quit).  If a dialog (about/pref) is already open, delay the update?

        self.ppasOrFiltersModified = False

        notebook = Gtk.Notebook()

        # PPAs.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        ppaStore = Gtk.ListStore( str, str, str, str ) # PPA User, PPA Name, Series, Architecture.
        ppaStore.set_sort_column_id( 0, Gtk.SortType.ASCENDING )
        for ppa in self.ppas:
            ppaStore.append( [ ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() ] )

        ppaTree = Gtk.TreeView( ppaStore )
        ppaTree.set_hexpand( True )
        ppaTree.set_vexpand( True )
        ppaTree.append_column( Gtk.TreeViewColumn( _( "PPA User" ), Gtk.CellRendererText(), text = 0 ) )
        ppaTree.append_column( Gtk.TreeViewColumn( _( "PPA Name" ), Gtk.CellRendererText(), text = 1 ) )
        ppaTree.append_column( Gtk.TreeViewColumn( _( "Series" ), Gtk.CellRendererText(), text = 2 ) )
        ppaTree.append_column( Gtk.TreeViewColumn( _( "Architecture" ), Gtk.CellRendererText(), text = 3 ) )
        ppaTree.set_tooltip_text( _( "Double click to edit a PPA." ) )
        ppaTree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        ppaTree.connect( "row-activated", self.onPPADoubleClick )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( ppaTree )
        grid.attach( scrolledWindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )
        box.set_halign( Gtk.Align.CENTER )

        addButton = Gtk.Button( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new PPA." ) )
        addButton.connect( "clicked", self.onPPAAdd, ppaTree )
        box.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected PPA." ) )
        removeButton.connect( "clicked", self.onPPARemove, ppaTree )
        box.pack_start( removeButton, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "PPAs" ) ) )

        # Filters.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        filterStore = Gtk.ListStore( str, str ) # 'PPA User | PPA Name', filter text.
        filterStore.set_sort_column_id( 0, Gtk.SortType.ASCENDING )
        for key in sorted( self.filters ):
            filterStore.append( [ key, "\n".join( self.filters[ key ] ) ] )

        filterTree = Gtk.TreeView( filterStore )
        filterTree.set_grid_lines( Gtk.TreeViewGridLines.HORIZONTAL )
        filterTree.set_hexpand( True )
        filterTree.set_vexpand( True )
        filterTree.append_column( Gtk.TreeViewColumn( _( "PPA" ), Gtk.CellRendererText(), text = 0 ) )
        filterTree.append_column( Gtk.TreeViewColumn( _( "Filter" ), Gtk.CellRendererText(), text = 1 ) )
        filterTree.set_tooltip_text( _( "Double click to edit a filter." ) )
        filterTree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        filterTree.connect( "row-activated", self.onFilterDoubleClick, ppaTree )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( filterTree )
        grid.attach( scrolledWindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )
        box.set_halign( Gtk.Align.CENTER )

        addButton = Gtk.Button( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new filter." ) )
        addButton.connect( "clicked", self.onFilterAdd, filterTree, ppaTree )
        box.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected filter." ) )
        removeButton.connect( "clicked", self.onFilterRemove, filterTree )
        box.pack_start( removeButton, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Filters" ) ) )

        # General settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showAsSubmenusCheckbox = Gtk.CheckButton( _( "Show PPAs as submenus" ) )
        showAsSubmenusCheckbox.set_tooltip_text( _(
            "The download statistics for each PPA\n" + \
            "are shown in a separate submenu." ) )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )
        grid.attach( showAsSubmenusCheckbox, 0, 0, 1, 1 )

        combinePPAsCheckbox = Gtk.CheckButton( _( "Combine PPAs" ) )
        combinePPAsCheckbox.set_tooltip_text( _(
            "Combine the statistics of binary\n" + \
            "packages when the PPA user/name\n" + \
            "are the same.\n\n" + \
            "Non-architecture specific packages:\n" + \
            "If the package names and version\n" + \
            "numbers of two binary packages are\n" + \
            "identical, the packages are treated\n" + \
            "as the same package and the\n" + \
            "download counts are NOT summed.\n" + \
            "Packages such as Python fall into\n" + \
            "this category.\n\n" + \
            "Architecture specific packages:\n" + \
            "If the package names and version\n" + \
            "numbers of two binary packages are\n" + \
            "identical, the packages are treated\n" + \
            "as the same package and the download\n" + \
            "counts ARE summed.\n" + \
            "Packages such as compiled C fall into\n" + \
            "this category." ) )
        combinePPAsCheckbox.set_active( self.combinePPAs )
        combinePPAsCheckbox.set_margin_top( 10 )
        grid.attach( combinePPAsCheckbox, 0, 1, 1, 1 )

        ignoreVersionArchitectureSpecificCheckbox = Gtk.CheckButton( _( "Ignore version for architecture specific" ) )
        ignoreVersionArchitectureSpecificCheckbox.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )
        ignoreVersionArchitectureSpecificCheckbox.set_tooltip_text( _(
            "Sometimes architecture specific\n" + \
            "packages with the same package\n" + \
            "name but different version 'number'\n" + \
            "are logically the SAME package.\n\n" + \
            "For example, a C source package for\n" + \
            "both Ubuntu Saucy and Ubuntu Trusty\n" + \
            "will be compiled twice, each with a\n" + \
            "different 'number', despite being\n" + \
            "the SAME release.\n\n" + \
            "Checking this option will ignore the\n" + \
            "version number when determining if\n" + \
            "two architecture specific packages\n" + \
            "are identical.\n\n" + \
            "The version number is retained only\n" + \
            "if it is identical across ALL\n" + \
            "instances of a published binary." ) )
        ignoreVersionArchitectureSpecificCheckbox.set_active( self.ignoreVersionArchitectureSpecific )
        ignoreVersionArchitectureSpecificCheckbox.set_sensitive( combinePPAsCheckbox.get_active() )
        grid.attach( ignoreVersionArchitectureSpecificCheckbox, 0, 2, 1, 1 )

        combinePPAsCheckbox.connect( "toggled", self.onCombinePPAsCheckbox, ignoreVersionArchitectureSpecificCheckbox )

        sortByDownloadCheckbox = Gtk.CheckButton( _( "Sort by download" ) )
        sortByDownloadCheckbox.set_tooltip_text( _( "Sort by download count within each PPA." ) )
        sortByDownloadCheckbox.set_active( self.sortByDownload )
        sortByDownloadCheckbox.set_margin_top( 10 )
        grid.attach( sortByDownloadCheckbox, 0, 3, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        label = Gtk.Label( _( "  Clip amount" ) )
        label.set_sensitive( sortByDownloadCheckbox.get_active() )
        label.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )
        box.pack_start( label, False, False, 0 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.sortByDownloadAmount, 0, 10000, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinner.set_value( self.sortByDownloadAmount ) # ...so need to force the initial value by explicitly setting it.
        spinner.set_tooltip_text( _(
            "Limit the number of entries\n" + \
            "when sorting by download.\n\n" + \
            "A value of zero will not clip." ) )
        spinner.set_sensitive( sortByDownloadCheckbox.get_active() )
        box.pack_start( spinner, False, False, 0 )

        grid.attach( box, 0, 4, 1, 1 )

        sortByDownloadCheckbox.connect( "toggled", self.onClipByDownloadCheckbox, label, spinner )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorPPADownloadStatistics.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 5, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        dialog = Gtk.Dialog( _( "Preferences" ), None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorPPADownloadStatistics.ICON )
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            self.showSubmenu = showAsSubmenusCheckbox.get_active()
            self.combinePPAs = combinePPAsCheckbox.get_active()
            self.ignoreVersionArchitectureSpecific = ignoreVersionArchitectureSpecificCheckbox.get_active()
            self.sortByDownload = sortByDownloadCheckbox.get_active()
            self.sortByDownloadAmount = spinner.get_value_as_int()

#TODO Check indenting...
# Seems that adding a PPA and clicking OK doesn't actually save!
            if self.ppasOrFiltersModified:
                # Only save the PPAs/filters if modified - avoids a re-download.
                # On a PPA remove, a re-download really doesn't need to occur...but it's a PITA to sort that one out!
                self.ppas = [ ]
                treeiter = ppaStore.get_iter_first()
                while treeiter != None:
                    self.ppas.append( PPA( ppaStore[ treeiter ][ 0 ], ppaStore[ treeiter ][ 1 ], ppaStore[ treeiter ][ 2 ], ppaStore[ treeiter ][ 3 ] ) )
                    treeiter = ppaStore.iter_next( treeiter )

                self.ppas.sort( key = operator.methodcaller( "getKey" ) )

                self.filters = { }
                treeiter = filterStore.get_iter_first()
                while treeiter != None:
                    self.filters[ filterStore[ treeiter ][ 0 ] ] = filterStore[ treeiter ][ 1 ].split()
                    treeiter = filterStore.iter_next( treeiter )

            self.saveConfig()
            pythonutils.setAutoStart( IndicatorPPADownloadStatistics.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            GLib.idle_add( self.update, False )

#             GLib.timeout_add_seconds( 1, self.buildMenu )

#             if self.ppasOrFiltersModified:
#                 GLib.timeout_add_seconds( 10, self.requestPPADownloadAndMenuRefresh, False ) # Hopefully 10 seconds is sufficient to rebuild the menu!
#                 with self.lock:
#                     self.downloadInProgress = True # Although the download hasn't actually started, this ensures the preferences cannot be opened until the download completes.

        dialog.destroy()
#         with self.lock:
#             self.preferencesOpen = False


    def onCombinePPAsCheckbox( self, source, checkbox ): checkbox.set_sensitive( source.get_active() )


    def onClipByDownloadCheckbox( self, source, spinner, label ):
        label.set_sensitive( source.get_active() )
        spinner.set_sensitive( source.get_active() )


    def onPPARemove( self, button, tree ):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter is None:
            pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "No PPA has been selected for removal." ), INDICATOR_NAME )
        else:
            # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            if pythonutils.showOKCancel( None, _( "Remove the selected PPA?" ), INDICATOR_NAME ) == Gtk.ResponseType.OK:
                model.remove( treeiter )
                self.ppasOrFiltersModified = True


    def onPPAAdd( self, button, tree ): self.onPPADoubleClick( tree, None, None )


    def onPPADoubleClick( self, tree, rowNumber, treeViewColumn ):
        model, treeiter = tree.get_selection().get_selected()

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( _( "PPA User" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        if len( model ) > 0:
            ppaUsers = [ ]
            for row in range( len( model ) ):
                if model[ row ][ 0 ] not in ppaUsers:
                    ppaUsers.append( model[ row ][ 0 ] )

            ppaUsers.sort( key = locale.strxfrm )

            ppaUser = Gtk.ComboBoxText.new_with_entry()
            for item in ppaUsers:
                ppaUser.append_text( item )

            if rowNumber is not None:
                ppaUser.set_active( ppaUsers.index( model[ treeiter ][ 0 ] ) ) # This is an edit.

        else:
            ppaUser = Gtk.Entry() # There are no PPAs present - adding the first PPA.

        ppaUser.set_hexpand( True ) # Only need to set this once and all objects will expand.

        grid.attach( ppaUser, 1, 0, 1, 1 )

        label = Gtk.Label( _( "PPA Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        if len( model ) > 0:
            ppaNames = [ ] 
            for row in range( len( model ) ):
                if model[ row ][ 1 ] not in ppaNames:
                    ppaNames.append( model[ row ][ 1 ] )

            ppaNames.sort( key = locale.strxfrm )

            ppaName = Gtk.ComboBoxText.new_with_entry()
            for item in ppaNames:
                ppaName.append_text( item )

            if rowNumber is not None:
                ppaName.set_active( ppaNames.index( model[ treeiter ][ 1 ] ) ) # This is an edit.

        else:
            ppaName = Gtk.Entry() # There are no PPAs present - adding the first PPA.

        grid.attach( ppaName, 1, 1, 1, 1 )

        label = Gtk.Label( _( "Series" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        series = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.SERIES:
            series.append_text( item )

        if rowNumber is not None:
            series.set_active( IndicatorPPADownloadStatistics.SERIES.index( model[ treeiter ][ 2 ] ) )
        else:
            series.set_active( 0 )

        grid.attach( series, 1, 2, 1, 1 )

        label = Gtk.Label( _( "Architecture" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        architectures = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.ARCHITECTURES:
            architectures.append_text( item )

        if rowNumber is not None:
            architectures.set_active( IndicatorPPADownloadStatistics.ARCHITECTURES.index( model[ treeiter ][ 3 ] ) )
        else:
            architectures.set_active( 0 )

        grid.attach( architectures, 1, 3, 1, 1 )

        title = _( "Edit PPA" )
        if rowNumber is None:
            title = _( "Add PPA" )

        dialog = Gtk.Dialog( title, None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorPPADownloadStatistics.ICON )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if len( model ) > 0:
                    ppaUserValue = ppaUser.get_active_text().strip()
                    ppaNameValue = ppaName.get_active_text().strip()
                else:
                    ppaUserValue = ppaUser.get_text().strip()
                    ppaNameValue = ppaName.get_text().strip()

                if ppaUserValue == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "PPA user cannot be empty." ), INDICATOR_NAME )
                    ppaUser.grab_focus()
                    continue

                if ppaNameValue == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "PPA name cannot be empty." ), INDICATOR_NAME )
                    ppaName.grab_focus()
                    continue

                # Ensure there is no duplicate...
                if ( rowNumber is None and len( model ) > 0 ) or ( rowNumber is not None and len( model ) > 1 ):
                    # Doing an add and there's at least one PPA OR doing an edit and there's at least two PPAs...
                    if rowNumber is None: # Doing an add, so data has changed.
                        dataHasBeenChanged = True
                    else: # Doing an edit, so check to see if there the data has actually been changed...
                        dataHasBeenChanged = not ( \
                            ppaUserValue == model[ treeiter ][ 0 ] and \
                            ppaNameValue == model[ treeiter ][ 1 ] and \
                            series.get_active_text() == model[ treeiter ][ 2 ] and \
                            architectures.get_active_text() == model[ treeiter ][ 3 ] )

                    if dataHasBeenChanged:
                        duplicate = False
                        for row in range( len( model ) ):
                            if ppaUserValue == model[ row ][ 0 ] and \
                               ppaNameValue == model[ row ][ 1 ] and \
                               series.get_active_text() == model[ row ][ 2 ] and \
                               architectures.get_active_text() == model[ row ][ 3 ]:

                                duplicate = True
                                break

                        if duplicate:
                            pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "Duplicates disallowed - there is an identical PPA!" ), INDICATOR_NAME )
                            continue

                # Update the model...
                if rowNumber is not None:
                    model.remove( treeiter ) # This is an edit...remove the old value and append new value.  

                model.append( [ ppaUserValue, ppaNameValue, series.get_active_text(), architectures.get_active_text() ] )
                self.ppasOrFiltersModified = True

            break

        dialog.destroy()


    def onFilterRemove( self, button, tree ):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter is None:
            pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "No filter has been selected for removal." ), INDICATOR_NAME )
        else:
            # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            if pythonutils.showOKCancel( None, _( "Remove the selected filter?" ), INDICATOR_NAME ) == Gtk.ResponseType.OK:
                model.remove( treeiter )
                self.ppasOrFiltersModified = True


    def onFilterAdd( self, button, filterTree, ppaTree ):
        if len( ppaTree.get_model() ) == 0:
            pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "Please add a PPA first!" ), INDICATOR_NAME )
        else:
            # If the number of filters equals the number of PPA User/Names, cannot add a filter!
            ppaUsersNames = [ ]
            for ppa in range( len( ppaTree.get_model() ) ):
                ppaUserName = ppaTree.get_model()[ ppa ][ 0 ] + " | " + ppaTree.get_model()[ ppa ][ 1 ]
                if not ppaUserName in ppaUsersNames:
                    ppaUsersNames.append( ppaUserName )

            if len( filterTree.get_model() ) == len( ppaUsersNames ):
                pythonutils.showMessage( None, Gtk.MessageType.INFO, _( "Only one filter per PPA User/Name." ), INDICATOR_NAME )
            else:
                self.onFilterDoubleClick( filterTree, None, None, ppaTree )


    def onFilterDoubleClick( self, filterTree, rowNumber, treeViewColumnm, ppaTree ):
        filterTreeModel, filterTreeIter = filterTree.get_selection().get_selected()
        ppaTreeModel, ppaTreeIter = ppaTree.get_selection().get_selected()

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( _( "PPA User/Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        ppaUsersNames = Gtk.ComboBoxText.new()
        if rowNumber is None: # Adding
            temp = [ ] # Used to ensure duplicates are not added.
            for ppa in range( len( ppaTreeModel ) ): # List of PPA User/Names from the list of PPAs in the preferences.
                ppaUserName = ppaTreeModel[ ppa ][ 0 ] + " | " + ppaTreeModel[ ppa ][ 1 ]
                if ppaUserName in temp:
                    continue

                # Ensure the PPA User/Name is not present in the list of filters in the preferences.
                inFilterList = False
                for filter in range( len( filterTreeModel ) ):
                    if ppaUserName in filterTreeModel[ filter ][ 0 ]:
                        inFilterList = True
                        break

                if not inFilterList:                        
                    ppaUsersNames.append_text( ppaUserName )
                    temp.append( ppaUserName )

        else:
            ppaUsersNames.append_text( filterTreeModel[ filterTreeIter ][ 0 ] )

        ppaUsersNames.set_hexpand( True )
        ppaUsersNames.set_active( 0 )

        grid.attach( ppaUsersNames, 1, 0, 1, 1 )

        label = Gtk.Label( _( "Filter Text" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 2, 1 )

        textview = Gtk.TextView()
        textview.set_tooltip_text( _(
            "Each line of text is a single\n" + \
            "filter which is compared against\n" + \
            "each package during download.\n\n" + \
            "If a package name contains ANY\n" + \
            "part of ANY filter, that package\n" + \
            "is included in the download\n" + \
            "statistics.\n\n" + \
            "Regular expressions and wild\n" + \
            "cards are not accepted!" ) )

        if rowNumber is not None:
            textview.get_buffer().set_text( filterTreeModel[ filterTreeIter ][ 1 ] ) # This is an edit.

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add( textview )
        scrolledwindow.set_hexpand( True )
        scrolledwindow.set_vexpand( True )

        grid.attach( scrolledwindow, 0, 3, 2, 1 )

        title = _( "Edit Filter" )
        if rowNumber is None:
            title = _( "Add Filter" )

        dialog = Gtk.Dialog( title, None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorPPADownloadStatistics.ICON )
        dialog.set_default_size( -1, 350 ) # Set a height otherwise the textview is only a couple of lines high.

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                buffer = textview.get_buffer()
                filterText = buffer.get_text( buffer.get_start_iter(), buffer.get_end_iter(), False )
                filterText = "\n".join( filterText.split() )
                if len( filterText ) == 0:
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "Please enter filter text!" ), INDICATOR_NAME )
                    continue

                # Update the model...
                if rowNumber is not None:
                    filterTreeModel.remove( filterTreeIter ) # This is an edit...remove the old value and append new value.  

                filterTreeModel.append( [ ppaUsersNames.get_active_text(), filterText ] ) 
                self.ppasOrFiltersModified = True

            break

        dialog.destroy()


    def loadConfig( self ):
        self.sortByDownload = False
        self.sortByDownloadAmount = 5
        self.combinePPAs = False
        self.ignoreVersionArchitectureSpecific = True
        self.showSubmenu = False
        self.filterAtDownload = True

        self.ppas = [ ]
        self.ppasPrevious = [ ] # Used to hold the most recent download for comparison.
        self.filters = { }

        config = pythonutils.loadConfig( INDICATOR_NAME, INDICATOR_NAME, logging )
        if len( config ) == 0:
            self.ppas.append( PPA( "thebernmeister", "ppa", "artful", "amd64" ) )
            self.filters[ 'thebernmeister | ppa' ] = [ 
                "indicator-fortune",
                "indicator-lunar",
                "indicator-ppa-download-statistics",
                "indicator-punycode",
                "indicator-script-runner",
                "indicator-stardate",
                "indicator-tide",
                "indicator-virtual-box" ]
#TODO Add final name of indicator-calendar
        else:
            ppas = config.get( IndicatorPPADownloadStatistics.CONFIG_PPAS, [ ] )
            for ppa in ppas:
                self.ppas.append( PPA( ppa[ 0 ], ppa[ 1 ], ppa[ 2 ], ppa[ 3 ] ) )

            self.ppas.sort( key = operator.methodcaller( "getKey" ) )

            self.combinePPAs = config.get( IndicatorPPADownloadStatistics.CONFIG_COMBINE_PPAS, self.combinePPAs )
            self.filters = config.get( IndicatorPPADownloadStatistics.CONFIG_FILTERS, { } )
            self.ignoreVersionArchitectureSpecific = config.get( IndicatorPPADownloadStatistics.CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC, self.ignoreVersionArchitectureSpecific )
            self.showSubmenu = config.get( IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU, self.showSubmenu )
            self.sortByDownload = config.get( IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD, self.sortByDownload )
            self.sortByDownloadAmount = config.get( IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT, self.sortByDownloadAmount )


    def saveConfig( self ):
        ppas = [ ]
        for ppa in self.ppas:
            ppas.append( [ ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() ] )

        config = {
            IndicatorPPADownloadStatistics.CONFIG_FILTERS: self.filters,
            IndicatorPPADownloadStatistics.CONFIG_COMBINE_PPAS: self.combinePPAs,
            IndicatorPPADownloadStatistics.CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC: self.ignoreVersionArchitectureSpecific,
            IndicatorPPADownloadStatistics.CONFIG_PPAS: ppas,
            IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU: self.showSubmenu,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD: self.sortByDownload,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT: self.sortByDownloadAmount
        }

        pythonutils.saveConfig( config, INDICATOR_NAME, INDICATOR_NAME, logging )


#     def requestPPADownloadAndMenuRefresh( self, runAgain ):
#         Thread( target = self.getPPADownloadStatistics ).start()
#         return runAgain
#TODO Can the scheduling of the next update happen here, rather than in the init?
#Might have to take a parameter -IMMEDIATE or a TIME FROM NOW.


#TODO In the update method up top, could call getPPADownloadStatistics in a thread (as currently done)
# but then join on the thread to wait for it to finish and then build the menu.
# This means the download functionality is separated from the menu stuff.
# Make sure the code does not block (so whilst waiting for the join, can the user still operate the menu)...or should the menu be blocked?                


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
#         with self.lock:
#             self.downloadInProgress = True

        for ppa in self.ppas:
            ppa.setStatus( PPA.STATUS_NEEDS_DOWNLOAD )
            key = ppa.getUser() + " | " + ppa.getName()
            if key in self.filters:
                self.getPublishedBinariesWithFilters( ppa )
            else:
                self.getPublishedBinariesNoFilters( ppa )

        # Have a second attempt at failures...
        for ppa in self.ppas:
            if ppa.getStatus() == PPA.STATUS_ERROR_RETRIEVING_PPA:
                ppa.setStatus( PPA.STATUS_NEEDS_DOWNLOAD )
                key = ppa.getUser() + " | " + ppa.getName()
                if key in self.filters:
                    self.getPublishedBinariesWithFilters( ppa )
                else:
                    self.getPublishedBinariesNoFilters( ppa )

        with self.lock:
            self.downloadInProgress = False

        GLib.idle_add( self.buildMenu )

        if not self.quitRequested and self.ppasPrevious != self.ppas: #TODO Handle
            Notify.Notification.new( _( "Statistics downloaded!" ), "", IndicatorPPADownloadStatistics.ICON ).show()

        self.ppasPrevious = deepcopy( self.ppas ) # Take a copy to be used for comparison on the next download.


    def getPublishedBinariesNoFilters( self, ppa ):
        try:
            url = self.getLaunchPadURL( ppa, None, None )
            publishedBinaries = json.loads( urlopen( url ).read().decode( "utf8" ) )
            numberOfPublishedBinaries = publishedBinaries[ "total_size" ]
            if numberOfPublishedBinaries == 0:
                ppa.setStatus( PPA.STATUS_NO_PUBLISHED_BINARIES )
            else:
                self.processPublishedBinaries( ppa, url, publishedBinaries, numberOfPublishedBinaries )

        except Exception as e:
            logging.exception( e )
            ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )


    def getPublishedBinariesWithFilters( self, ppa ):
        noPublishedBinaries = True
        for filter in self.filters.get( ppa.getUser() + " | " + ppa.getName() ):
            try:
                url = self.getLaunchPadURL( ppa, None, filter )
                publishedBinaries = json.loads( urlopen( url ).read().decode( "utf8" ) )
                numberOfPublishedBinaries = publishedBinaries[ "total_size" ]
                if numberOfPublishedBinaries > 0: # Only fetch if there is data, that is, was not filtered.
                    noPublishedBinaries = False
                    self.processPublishedBinaries( ppa, url, publishedBinaries, numberOfPublishedBinaries )

            except Exception as e:
                logging.exception( e )
                ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )

        if noPublishedBinaries: # Will occur if all the data was filtered.
            ppa.setStatus( PPA.STATUS_NO_PUBLISHED_BINARIES )


    # Takes a published binary and extracts the information needed to get the download count (for each package).
    # The results in a published binary are returned in lots of 75;
    # for more than 75 published binaries, loop to get the remainder.
    def processPublishedBinaries( self, ppa, baseURL, publishedBinaries, numberOfPublishedBinaries ):
        try:
            resultIndexPerPage = 0
            resultPage = 1
            resultsPerUrl = 75
            threads = [ ]
            for resultCount in range( numberOfPublishedBinaries ):
                if self.quitRequested: #TODO Handle
                    self.quit( None )
                    return

                if resultCount == ( resultPage * resultsPerUrl ):
                    # Handle result pages after the first page.
                    url = baseURL + "&ws.start=" + str( resultPage * resultsPerUrl )
                    publishedBinaries = json.loads( urlopen( url ).read().decode( "utf8" ) )
                    resultPage += 1
                    resultIndexPerPage = 0

                packageName = publishedBinaries[ "entries" ][ resultIndexPerPage ][ "binary_package_name" ]

                # Limit the number of concurrent fetches...
                if len( threads ) > 5:
                    for t in threads:
                        t.join()

                    threads = [ ]

                packageVersion = publishedBinaries[ "entries" ][ resultIndexPerPage ][ "binary_package_version" ]
                architectureSpecific = publishedBinaries[ "entries" ][ resultIndexPerPage ][ "architecture_specific" ]
                indexLastSlash = publishedBinaries[ "entries" ][ resultIndexPerPage ][ "self_link" ].rfind( "/" )
                packageId = publishedBinaries[ "entries" ][ resultIndexPerPage ][ "self_link" ][ indexLastSlash + 1 : ]

                t = Thread( target = self.getDownloadCount, args = ( ppa, packageName, packageVersion, architectureSpecific, packageId ) )
                t.start()
                threads.append( t )
                resultIndexPerPage += 1

            for t in threads:
                t.join() # Wait for remaining threads...

            # The only status the PPA can be at this point is error retrieving ppa (set by get download count).
            if ppa.getStatus() != PPA.STATUS_ERROR_RETRIEVING_PPA:
                ppa.setStatus( PPA.STATUS_OK )
                if len( ppa.getPublishedBinaries() ) == 0: #TODO Is is possible for non filtered to hit this?
                    ppa.setStatus( PPA.STATUS_PUBLISHED_BINARIES_COMPLETELY_FILTERED )

        except Exception as e:
            logging.exception( e )
            ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )


    def getDownloadCount( self, ppa, packageName, packageVersion, architectureSpecific, packageId ):
        with threading.Lock():
            status = ppa.getStatus() # If the status is set to error by another download (of this PPA), abort...

        if status != PPA.STATUS_ERROR_RETRIEVING_PPA:
            try:
                downloadCount = json.loads( urlopen( self.getLaunchPadURL( ppa, packageId, None ) ).read().decode( "utf8" ) )
                if str( downloadCount ).isnumeric():
                    ppa.addPublishedBinary( PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific ) )
                else:
                    ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )
    
            except Exception as e:
                logging.exception( e )
                ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )


    def getPublishedBinaries( self, ppa, filter ):
        if filter is None:
            baseURL = self.getLaunchPadURL( ppa, None, None )
        else:
            baseURL = self.getLaunchPadURL( ppa, None, filter )

        count = 0
        while( count < numberOfPublishedBinaries ):
            try:
                publishedBinaries = json.loads( urlopen( url + "&ws.start=" + str( count ) ).read().decode( "utf8" ) )
                numberOfPublishedBinaries = publishedBinaries[ "total_size" ]
                if numberOfPublishedBinaries == 0:
                    ppa.setStatus( PPA.STATUS_NO_PUBLISHED_BINARIES )
                else:
                    self.processPublishedBinariesNEW( ppa, publishedBinaries, numberOfPublishedBinaries )

                count += 75 # The number of results per page.

            except Exception as e:
                logging.exception( e )
                ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )
                count = numberOfPublishedBinaries # Terminate the loop.


    # ppa: the current PPA.
    # One of packageId or filter must be None.
    # If packageId is None, filter must be a string OR None.
    # If filter is None, packageId must be a string.
    def getLaunchPadURL( self, ppa, packageId, filter ):
        url = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName()
        if packageId is None:
            url += "?ws.op=getPublishedBinaries" + \
                   "&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + ppa.getSeries() + "/" + ppa.getArchitecture() + \
                   "&status=Published"

            if filter is not None:
                url += "&exact_match=false" + \
                       "&ordered=false" + \
                       "&binary_name=" + filter

        else:
            url += "/+binarypub/" + packageId + "?ws.op=getDownloadCount"

        return url


    # Takes a published binary and extracts the information needed to get the download publishedBinaryCounter (for each package).
    # The results in a published binary are returned in lots of 75;
    # for more than 75 published binaries, loop to get the remainder.
    def processPublishedBinariesNEW( self, ppa, publishedBinaries, numberOfPublishedBinaries ):
        import concurrent.futures.ThreadPoolExecutor
        try:
            resultIndexOnPage = 0
            threads = [ ]
            for resultCount in range( numberOfPublishedBinaries ):
#                 if self.quitRequested: #TODO Handle
#                     self.quit( None )
#                     return

                packageName = publishedBinaries[ "entries" ][ resultIndexOnPage ][ "binary_package_name" ]

                # Limit the number of concurrent fetches...
                if len( threads ) > 5:
                    for t in threads:
                        t.join()

                    threads = [ ]

                packageVersion = publishedBinaries[ "entries" ][ resultIndexOnPage ][ "binary_package_version" ]
                architectureSpecific = publishedBinaries[ "entries" ][ resultIndexOnPage ][ "architecture_specific" ]
                indexLastSlash = publishedBinaries[ "entries" ][ resultIndexOnPage ][ "self_link" ].rfind( "/" )
                packageId = publishedBinaries[ "entries" ][ resultIndexOnPage ][ "self_link" ][ indexLastSlash + 1 : ]

                t = Thread( target = self.getDownloadCountNEW, args = ( ppa, packageName, packageVersion, architectureSpecific, packageId ) )
                t.start()
                threads.append( t )
                resultIndexOnPage += 1

            for t in threads:
                t.join() # Wait for remaining threads...

            # The only status the PPA can be at this point is error retrieving ppa (set by get download count).
            if ppa.getStatus() != PPA.STATUS_ERROR_RETRIEVING_PPA:
                ppa.setStatus( PPA.STATUS_OK )
                if len( ppa.getPublishedBinaries() ) == 0: #TODO Is is possible for non filtered to hit this?
                    ppa.setStatus( PPA.STATUS_PUBLISHED_BINARIES_COMPLETELY_FILTERED )

        except Exception as e:
            logging.exception( e )
            ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )


#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################


    def getPPADownloadStatisticsNEW( self ):
#         with self.lock:
#             self.downloadInProgress = True

        for ppa in self.ppas:
            filters = [ "" ] # To match all published binary names an empty string can be used.
            key = ppa.getUser() + " | " + ppa.getName()
            if key in self.filters:
                filters = self.filters.get( key )

            ppa.setStatus( PPA.STATUS_NEEDS_DOWNLOAD )
            for filter in filters:
                self.getPublishedBinariesNEW( ppa, filter )
                if ppa.getStatus() == PPA.STATUS_ERROR_RETRIEVING_PPA:
                    break # No point continuing...

            if ppa.getStatus() == PPA.STATUS_OK and len( ppa.getPublishedBinaries() ) == 0: # No error but check for no results...
                if filters[ 0 ] == "": # No filtering was used for this PPA.
                    ppa.setStatus( PPA.STATUS_NO_PUBLISHED_BINARIES )
                else:
                    ppa.setStatus( PPA.STATUS_PUBLISHED_BINARIES_COMPLETELY_FILTERED )

#         with self.lock:
#             self.downloadInProgress = False

        GLib.idle_add( self.buildMenu )

        if not self.quitRequested and self.ppasPrevious != self.ppas: #TODO Handle
            Notify.Notification.new( _( "Statistics downloaded!" ), "", IndicatorPPADownloadStatistics.ICON ).show()

        self.ppasPrevious = deepcopy( self.ppas ) # Take a copy to be used for comparison on the next download.


    # Use a thread pool executer to get the download count within each published binary.
    # References:
    #    https://docs.python.org/3/library/concurrent.futures.html
    #    https://pymotw.com/3/concurrent.futures
    #    http://www.dalkescientific.com/writings/diary/archive/2012/01/19/concurrent.futures.html
    def getPublishedBinariesNEW( self, ppa, filter ):
        url = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName() + "?ws.op=getPublishedBinaries" + \
              "&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + ppa.getSeries() + "/" + ppa.getArchitecture() + "&status=Published" + \
              "&exact_match=false&ordered=false&binary_name=" + filter

#         if ppa.getUser() == "nilarimogard": return #TODO Testing

        pageNumber = 1
        publishedBinariesPerPage = 75 # Results are presented in at most 75 per page.
        publishedBinaryCounter = 0
        totalPublishedBinaries = publishedBinaryCounter + 1 # Set to a value greater than publishedBinaryCounter to ensure the loop executes at least once.
        while( publishedBinaryCounter < totalPublishedBinaries and ppa.getStatus() == PPA.STATUS_NEEDS_DOWNLOAD ): # Keep going if there are more downloads and no error has occurred.
            try:
                publishedBinaries = json.loads( urlopen( url + "&ws.start=" + str( publishedBinaryCounter ) ).read().decode( "utf8" ) )
            except Exception as e:
                logging.exception( e )
                ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )
                publishedBinaryCounter = totalPublishedBinaries
                continue

            totalPublishedBinaries = publishedBinaries[ "total_size" ]
            if totalPublishedBinaries == 0:
                publishedBinaryCounter = totalPublishedBinaries
                continue

            numberPublishedBinariesCurrentPage = publishedBinariesPerPage
            if( pageNumber * publishedBinariesPerPage ) > totalPublishedBinaries:
                numberPublishedBinariesCurrentPage = totalPublishedBinaries - ( ( pageNumber - 1 ) * publishedBinariesPerPage )

            maxWorkers = 10 if totalPublishedBinaries < 10 else 5 # If the total is fewer than 10, grab all in one batch, otherwise limit to 5 concurrent requests.
            with concurrent.futures.ThreadPoolExecutor( max_workers = maxWorkers ) as executor:
                results = { executor.submit( getDownloadCountNEW, ppa, publishedBinaries, i, executor ): i for i in range( numberPublishedBinariesCurrentPage ) }
                for result in concurrent.futures.as_completed( results ):
                    pass

            publishedBinaryCounter += publishedBinariesPerPage
            pageNumber += 1

        if ppa.getStatus() == PPA.STATUS_NEEDS_DOWNLOAD: # If the initial status is still present then all is good.
            ppa.setStatus( PPA.STATUS_OK )


def getDownloadCountNEW( ppa, publishedBinaries, i, executor ):
    if ppa.getStatus() == PPA.STATUS_NEEDS_DOWNLOAD: # Use the status to cancel downloads if an error occurred.
        try:
            indexLastSlash = publishedBinaries[ "entries" ][ i ][ "self_link" ].rfind( "/" )
            packageId = publishedBinaries[ "entries" ][ i ][ "self_link" ][ indexLastSlash + 1 : ]
            url = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName() + "/+binarypub/" + packageId + "?ws.op=getDownloadCount"

            downloadCount = json.loads( urlopen( url ).read().decode( "utf8" ) )
            if str( downloadCount ).isnumeric():
                packageName = publishedBinaries[ "entries" ][ i ][ "binary_package_name" ]
                packageVersion = publishedBinaries[ "entries" ][ i ][ "binary_package_version" ]
                architectureSpecific = publishedBinaries[ "entries" ][ i ][ "architecture_specific" ]
                ppa.addPublishedBinary( PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific ) )

            else:
                ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )

        except Exception as e:
            logging.exception( e )
            ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )


if __name__ == "__main__": IndicatorPPADownloadStatistics().main()