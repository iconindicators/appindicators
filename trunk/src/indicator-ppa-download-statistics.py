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


#TODO Current released version 57 with the sample filter in place DOES NOT find any downloads!
# Removing the filter then works...is this a bug and does it still exist in the new code?


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
    COMMENTS = _( "Shows the total downloads of PPAs." )

    SERIES = [ "artful", "zesty",
              "yakkety", "xenial", "wily", "vivid", "utopic",
              "trusty", "saucy", "raring", "quantal", "precise",
              "oneiric", "natty", "maverick", "lucid", "karmic",
              "jaunty", "intrepid", "hardy", "gutsy", "feisty",
              "edgy", "dapper", "breezy", "hoary", "warty" ]

    ARCHITECTURES = [ "amd64", "i386" ]

    INDENT = "    "
    SVG_ICON = "." + INDICATOR_NAME + "-icon"
    SVG_FILE = os.getenv( "HOME" ) + "/" + SVG_ICON + ".svg"

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

        menuItem = Gtk.MenuItem( IndicatorPPADownloadStatistics.INDENT + self.getStatusMessage( ppa ) )
        menu.append( menuItem )


    def getStatusMessage( self, ppa ):
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

        return message


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
                if ppa.getStatus() == PPA.STATUS_OK and combinedPPAs[ key ].getStatus() == PPA.STATUS_OK:
                    combinedPPAs[ key ].addPublishedBinaries( ppa.getPublishedBinaries() )
                elif combinedPPAs[ key ].getStatus() == PPA.STATUS_OK:
                    combinedPPAs[ key ].setStatus( ppa.getStatus() ) # The current PPA has an error, so that becomes the new status.
                elif combinedPPAs[ key ].getStatus() != ppa.getStatus():
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

        webbrowser.open( url ) # This returns a boolean indicating success or failure - showing the user a message on a false return value causes a lock up!


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
            self.ppas.append( PPA( "thebernmeister", "ppa", "xenial", "amd64" ) )
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


    def getPPADownloadStatisticsNEW( self ):
#         with self.lock:
#             self.downloadInProgress = True

        #TODO Testing...remove
        self.filters[ 'thebernmeister | ppa' ] = [ 
            "indicator-fortune",
            "indicator-lunar",
            "indicator-ppa-download-statistics",
            "indicator-punycode",
            "indicator-script-runner",
            "indicator-stardate",
            "indicator-tide",
            "indicator-virtual-box" ]

        for ppa in self.ppas:
            ppa.setStatus( PPA.STATUS_NEEDS_DOWNLOAD )

            filter = None
            key = ppa.getUser() + " | " + ppa.getName()
            if key in self.filters:
                filter = self.filters.get( key )

            self.getPublishedBinariesNEW( ppa, filter )

            # Have a second attempt at failures...
            if ppa.getStatus() == PPA.STATUS_ERROR_RETRIEVING_PPA:
                ppa.setStatus( PPA.STATUS_NEEDS_DOWNLOAD )
                if key in self.filters:
                    filter = self.filters.get( key )

                self.getPublishedBinariesNEW( ppa, filter )

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

#TODO Test with at least two PPAs.

#TODO Test with a PPA in excess of 75 results...
# https://launchpad.net/~nilarimogard/+archive/ubuntu/webupd8?field.series_filter=xenial
# https://launchpad.net/~nilarimogard/+archive/ubuntu/webupd8?field.series_filter=trusty

        url = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName() + "?ws.op=getPublishedBinaries" + \
              "&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + ppa.getSeries() + "/" + ppa.getArchitecture() + "&status=Published"

#TODO Test filtering!
#         if filter is not None:
#             url += "&exact_match=false&ordered=false&binary_name=" + filter

        if ppa.getUser() == "nilarimogard": return

        pageNumber = 1
        publishedBinariesPerPage = 75 # Results are presented in at most 75 per page.
        publishedBinaryCounter = 0
        totalPublishedBinaries = publishedBinaryCounter + 1 # Set to a value greater than publishedBinaryCounter to ensure the loop executes at least once.
        while( publishedBinaryCounter < totalPublishedBinaries ):
            try:
#                 print( url + "&ws.start=" + str( publishedBinaryCounter ) )
                publishedBinaries = json.loads( urlopen( url + "&ws.start=" + str( publishedBinaryCounter ) ).read().decode( "utf8" ) )
            except Exception as e:
                logging.exception( e )
                ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )
                publishedBinaryCounter = totalPublishedBinaries
                continue

            totalPublishedBinaries = publishedBinaries[ "total_size" ]
            if totalPublishedBinaries == 0:
                ppa.setStatus( PPA.STATUS_NO_PUBLISHED_BINARIES )
                publishedBinaryCounter = totalPublishedBinaries
                continue

            numberPublishedBinariesCurrentPage = publishedBinariesPerPage
            if( pageNumber * publishedBinariesPerPage ) > totalPublishedBinaries:
                numberPublishedBinariesCurrentPage = totalPublishedBinaries - ( ( pageNumber - 1 ) * publishedBinariesPerPage )

            with concurrent.futures.ThreadPoolExecutor( max_workers = 5 ) as executor: # Limit to 5 concurrent requests to not burden LaunchPad.
                results = { executor.submit( getDownloadCountNEW, ppa, publishedBinaries, i, executor ): i for i in range( numberPublishedBinariesCurrentPage ) }
                for result in concurrent.futures.as_completed( results ):
                    pass

#TODO If status is error, then set loop variable to exit loop, else do as below.
            publishedBinaryCounter += publishedBinariesPerPage
            pageNumber += 1

        if ppa.getStatus() != PPA.STATUS_ERROR_RETRIEVING_PPA:
            ppa.setStatus( PPA.STATUS_OK )


# https://api.launchpad.net/1.0/~nilarimogard/+archive/webupd8?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/trusty/amd64&status=Published&ws.start=0
# https://api.launchpad.net/1.0/~nilarimogard/+archive/webupd8?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/trusty/amd64&status=Published&ws.start=75
# https://api.launchpad.net/1.0/~nilarimogard/+archive/webupd8?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/trusty/amd64&status=Published&ws.start=150
# https://api.launchpad.net/1.0/~nilarimogard/+archive/webupd8?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/trusty/amd64&status=Published&ws.start=225
# https://api.launchpad.net/1.0/~thebernmeister/+archive/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/xenial/amd64&status=Published&ws.start=0


def getDownloadCountNEW( ppa, publishedBinaries, i, executor ):
    fail = True
    indexLastSlash = publishedBinaries[ "entries" ][ i ][ "self_link" ].rfind( "/" )
    packageId = publishedBinaries[ "entries" ][ i ][ "self_link" ][ indexLastSlash + 1 : ]
    url = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName() + "/+binarypub/" + packageId + "?ws.op=getDownloadCount"
    try:
        downloadCount = json.loads( urlopen( url ).read().decode( "utf8" ) )
        if str( downloadCount ).isnumeric():
            packageName = publishedBinaries[ "entries" ][ i ][ "binary_package_name" ]
            packageVersion = publishedBinaries[ "entries" ][ i ][ "binary_package_version" ]
            architectureSpecific = publishedBinaries[ "entries" ][ i ][ "architecture_specific" ]
            ppa.addPublishedBinary( PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific ) )
            fail = False
            print( packageName, packageVersion, downloadCount, architectureSpecific )

    except Exception as e:
        logging.exception( e )

    if fail:
        ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )
        executor.shutdown() #TODO Test!

#     print( "getDownloadCount", index, downloadCount )


if __name__ == "__main__": IndicatorPPADownloadStatistics().main()


# audacious 3.9-3~webupd8~trusty1 1023 True
# asunder 2.8-1~webupd8~trusty 14672 True
# albert 0.11.1-1~webupd8~trusty0 518 True
# ap-hotspot 0.3-1~webupd8~4 55622 False
# actionaz 3.8.0-1~webupd8~trusty 1709 True
# audacious-dbg 3.7.2-1~webupd8~trusty0 156 True
# audacious-dev 3.9-3~webupd8~trusty1 15 True
# audacious-plugins-data 3.9-3~webupd8~trusty1 2339 False
# audacious-plugins 3.9-3~webupd8~trusty1 1040 True
# audacious-plugins-dbg 3.9-3~webupd8~trusty1 11 True
# avant-window-navigator 0.4.2~1+gitb8c2248-ubuntu1~trusty1 373 True
# avant-window-navigator-data 0.4.2~1+gitb8c2248-ubuntu1~trusty1 487 False
# awn-applet-awn-notification-daemon 0.4.1~1+git1081e3f-ubuntu2~trusty 151 True
# awn-applet-animal-farm 0.4.1~1+git1081e3f-ubuntu2~trusty 184 False
# awn-applet-awn-system-monitor 0.4.1~1+git1081e3f-ubuntu2~trusty 143 True
# awn-applet-battery-applet 0.4.1~1+git1081e3f-ubuntu2~trusty 194 False
# awn-applet-awnterm 0.4.1~1+git1081e3f-ubuntu2~trusty 143 True
# awn-applet-calendar 0.4.1~1+git1081e3f-ubuntu2~trusty 191 False
# awn-applet-cairo-main-menu 0.4.1~1+git1081e3f-ubuntu2~trusty 155 True
# awn-applet-cairo-clock 0.4.1~1+git1081e3f-ubuntu2~trusty 191 False
# awn-applet-common-folder 0.4.1~1+git1081e3f-ubuntu2~trusty 178 False
# awn-applet-cpufreq 0.4.1~1+git1081e3f-ubuntu2~trusty 201 False
# awn-applet-dialect 0.4.1~1+git1081e3f-ubuntu2~trusty 183 False
# awn-applet-comics 0.4.1~1+git1081e3f-ubuntu2~trusty 183 False
# awn-applet-digital-clock 0.4.1~1+git1081e3f-ubuntu2~trusty 149 True
# awn-applet-dockbarx 0.92-1~webupd8~trusty4 628 False
# awn-applet-file-browser-launcher 0.4.1~1+git1081e3f-ubuntu2~trusty 191 False
# awn-applet-garbage 0.4.1~1+git1081e3f-ubuntu2~trusty 149 True
# awn-applet-hardware-sensors 0.4.1~1+git1081e3f-ubuntu2~trusty 189 False
# awn-applet-feeds 0.4.1~1+git1081e3f-ubuntu2~trusty 184 False
# awn-applet-indicator 0.4.1~1+git1081e3f-ubuntu2~trusty 154 True
# awn-applet-mail 0.4.1~1+git1081e3f-ubuntu2~trusty 179 False
# awn-applet-media-player 0.4.1~1+git1081e3f-ubuntu2~trusty 186 False
# awn-applet-media-icon-applet 0.4.1~1+git1081e3f-ubuntu2~trusty 193 False
# awn-applet-media-control 0.4.1~1+git1081e3f-ubuntu2~trusty 188 False
# awn-applet-notification-area 0.4.1~1+git1081e3f-ubuntu2~trusty 150 True
# awn-applet-pandora 0.4.1~1+git1081e3f-ubuntu2~trusty 191 False
# awn-applet-quit-applet 0.4.1~1+git1081e3f-ubuntu2~trusty 189 False
# awn-applet-radio 0.10-1~webupd8~natty 4631 False
# awn-applet-places 0.4.1~1+git1081e3f-ubuntu2~trusty 146 True
# awn-applet-related 0.4.1~1+git1081e3f-ubuntu2~trusty 151 True
# awn-applet-shinyswitcher 0.4.1~1+git1081e3f-ubuntu2~trusty 155 True
# awn-applet-showdesktop 0.4.1~1+git1081e3f-ubuntu2~trusty 144 True
# awn-applet-stack 0.4.1~1+git1081e3f-ubuntu2~trusty 184 False
# awn-applet-slickswitcher 0.4.1~1+git1081e3f-ubuntu2~trusty 192 False
# awn-applet-sysmon 0.4.1~1+git1081e3f-ubuntu2~trusty 153 True
# awn-applet-thinkhdaps 0.4.1~1+git1081e3f-ubuntu2~trusty 181 False
# awn-applet-todo 0.4.1~1+git1081e3f-ubuntu2~trusty 176 False
# awn-applet-volume-control 0.4.1~1+git1081e3f-ubuntu2~trusty 193 False
# awn-applet-tomboy-applet 0.4.1~1+git1081e3f-ubuntu2~trusty 187 False
# awn-applet-weather 0.4.1~1+git1081e3f-ubuntu2~trusty 192 False
# awn-applet-webapplet 0.4.1~1+git1081e3f-ubuntu2~trusty 145 True
# awn-applet-wm 0.8-0~webupd8~natty 5357 False
# awn-applets-all 0.4.1~1+git1081e3f-ubuntu2~trusty 183 False
# awn-applets-common 0.4.1~1+git1081e3f-ubuntu2~trusty 277 False
# awn-applets-dbg 0.4.1~1+git1081e3f-ubuntu2~trusty 50 True
# awn-settings 0.4.2~1+gitb8c2248-ubuntu1~trusty1 433 False
# browser-plugin-freshplayer-nacl 0.3.6-1~webupd8~trusty6 178 True
# caffeine-plus 2.7.4+git20150326-1~webupd8~trusty1 13033 False
# browser-plugin-freshplayer-libpdf 0.3.6-1~webupd8~trusty6 513 True
# browser-plugin-freshplayer-pepperflash 0.3.6-1~webupd8~trusty6 10070 True
# calise 0.4.0-1~webupd8~raring 1459 True
# cardapio 0.9.202-0recipe887+1~custom~webupd8~trusty2 12064 False
# cardapio-awn 0.9.202-0recipe887+1~custom~webupd8~trusty2 683 False
# cardapio-docky 0.9.202-0recipe887+1~custom~webupd8~trusty2 4406 False
# cardapio-cinnamon 0.9.202-0recipe887+1~custom~webupd8~trusty2 1143 False
# cardapio-gnomepanel 0.9.202-0recipe887+1~custom~webupd8~trusty2 4804 False
# dockbarx 0.92-1~webupd8~trusty4 1172 False
# curseradio 0.2+git20150716-1~webupd8~trusty1 107 False
# cardapio-matepanel 0.9.202-0recipe887+1~custom~webupd8~trusty2 785 False
# cardapio-gnomeshell 0.9.202-0recipe887+1~custom~webupd8~trusty2 799 False
# dockbarx-applet-all 0.92-1~webupd8~trusty4 104 False
# dockbarx-applet-appindicator 0.92-1~webupd8~trusty4 476 False
# dockbarx-applet-battery-status 0.92-1~webupd8~trusty4 487 False
# dockbarx-applet-cardapio 0.92-1~webupd8~trusty4 439 False
# dockbarx-applet-hello-world 0.92-1~webupd8~trusty4 459 False
# dockbarx-applet-volume-control 0.92-1~webupd8~trusty4 486 False
# dockbarx-applet-clock 0.92-1~webupd8~trusty4 485 False
# dockbarx-common 0.92-1~webupd8~trusty4 1218 False
# dockbarx-applet-namebar 0.92-1~webupd8~trusty4 479 False
# dockbarx-dockx 0.92-1~webupd8~trusty4 1207 False
# emerald 0.9.5-0~webupd8~trusty2 10307 True
# dropbox-share 0.6-1~webupd8~0 2176 False
# dockbarx-themes-extra 2.1-1~2 16772 False
# dropbox-index 0.6-1~webupd8~0 2703 False
# encryptcli 0.3.2.5-1~webupd8~trusty0 134 True
# encryptpad 0.3.2.5-1~webupd8~trusty0 131 True
# exaile 3.4.5-1~webupd8~trusty0 7799 False
# exaile-plugin-contextinfo 3.4.5-1~webupd8~trusty0 4033 False
# exaile-plugin-ipod 3.4.5-1~webupd8~trusty0 3649 False
# exaile-plugin-moodbar 3.4.5-1~webupd8~trusty0 3446 False
# flashplugin-fullscreenhack 0.1-1~webupd8~trusty 2848 True
# freshplayerplugin 0.3.6-1~webupd8~trusty6 14118 False
# gloobus-sushi 0.4.5-ubuntu11~ppa335-14.04+1 3019 False
# gnome-subtitles 1.3-1~webupd8~trusty 16341 True
# gnome-window-applets 0.3-1~webupd8~trusty 1074 True
# gnomepanel-applet-dockbarx 0.92-1~webupd8~trusty4 46 False
# grive 0.5.1-1+git20170322~webupd8~trusty0 3745 True
# gloobus-preview 0.4.5-ubuntu11~ppa335-14.04+1 7476 True
# gtk3-nocsd 3-1~webupd8~trusty5 245 False
# guake 0.8.5-1~webupd8~trusty0 5614 True
# indicator-netspeed 0+git20140722-0~webupd8~trusty0 15320 True
# ipad-charge 1.1+git20161017-1~webupd8~trusty1 419 True
# indicator-xkbmod 0.1-1+git20150223~webupd8~trusty2 339 True
# kkedit 0.4.1-1~webupd8~trusty0 126 True
# launcher-list-indicator 0.1+git20161029-0~webupd8~0 408 False
# lcurse 0.2+git20170502-0~webupd8~0 321 False
# launchpad-getkeys 0.3.3-1~webupd8~2 68502 False
# lgogdownloader 2.26-1~webupd8~trusty0 393 True
# libaudclient2 3.4.3-1~webupd8~trusty 1227 True
# libaudcore1 3.4.3-1~webupd8~trusty 776 True
# libaudcore2 3.5.2-1~webupd8~trusty0 16012 True
# libaudcore3 3.7.2-2-1~webupd8~trusty1 12318 True
# libaudcore4 3.9-1~webupd8~trusty0 1418 True
# libaudcore5 3.9-3~webupd8~trusty1 1041 True
# libaudgui3 3.7.2-2-1~webupd8~trusty1 12159 True
# libaudgui5 3.9-3~webupd8~trusty1 1041 True
# libaudqt0 3.7.2-2-1~webupd8~trusty1 12014 True
# libaudqt2 3.9-3~webupd8~trusty1 1041 True
# libaudqt1 3.9-1~webupd8~trusty0 1414 True
# libaudgui4 3.9-1~webupd8~trusty0 1418 True
# libaudtag2 3.7.2-2-1~webupd8~trusty1 12157 True
# libaudtag3 3.9-3~webupd8~trusty1 1042 True
# libawn-doc 0.4.2~1+gitb8c2248-ubuntu1~trusty1 53 False
# libawn-dev 0.4.2~1+gitb8c2248-ubuntu1~trusty1 46 True
# libawn1 0.4.2~1+gitb8c2248-ubuntu1~trusty1 432 True
# libawn1-dbg 0.4.2~1+gitb8c2248-ubuntu1~trusty1 45 True
# libdesktop-agnostic-bin 0.3.94~1+git4d9b6fd-ubuntu0~trusty 364 True
# libdesktop-agnostic-cfg-keyfile 0.3.94~1+git4d9b6fd-ubuntu0~trusty 726 True
# libdesktop-agnostic-data 0.3.94~1+git4d9b6fd-ubuntu0~trusty 1224 True
# libdesktop-agnostic-cfg-gconf 0.3.94~1+git4d9b6fd-ubuntu0~trusty 876 True
# libdesktop-agnostic-dev 0.3.94~1+git4d9b6fd-ubuntu0~trusty 55 True
# libdesktop-agnostic-doc 0.3.94~1+git4d9b6fd-ubuntu0~trusty 48 False
# libdesktop-agnostic-fdo-gio 0.3.94~1+git4d9b6fd-ubuntu0~trusty 149 True
# libdesktop-agnostic-fdo-glib 0.3.94~1+git4d9b6fd-ubuntu0~trusty 265 True
# libdesktop-agnostic-vfs-gio 0.3.94~1+git4d9b6fd-ubuntu0~trusty 1059 True
# libdesktop-agnostic0-dbg 0.3.94~1+git4d9b6fd-ubuntu0~trusty 58 True
# libdesktop-agnostic0 0.3.94~1+git4d9b6fd-ubuntu0~trusty 1236 True
# libemeraldengine-dev 0.9.5-0~webupd8~trusty2 381 True
# libgtk3-nocsd0 3-1~webupd8~trusty5 247 True
# libemeraldengine0 0.9.5-0~webupd8~trusty2 9833 True
# libguess-dev 1.2.1-0~webupd8~trusty 862 True
# libguess1 1.2.1-0~webupd8~trusty 58872 True
# libmowgli-2-0 2.0.0-1~webupd8~trusty 60155 True
# libmowgli-2-dev 2.0.0-1~webupd8~trusty 403 True
# libmowgli-2-0-dbg 2.0.0-1~webupd8~trusty 245 True
# libvdpau-va-gl1 0.4.2-1~webupd8~trusty0 1520 True
# maim 3.4.47-1~webupd8~trusty0 124 True
# mate-multiload-ng-applet 1.5.2-1~webupd8~trusty0 51 True
# mcomix 1.2.1-1~webupd8~trusty1 1502 False
# minitube 2.2-1~webupd8~trusty 15241 True
# multiload-ng-common 1.5.2-1~webupd8~trusty0 187 False
# multiload-ng-standalone 1.5.2-1~webupd8~trusty0 44 True
# multiload-ng-systray 1.5.2-1~webupd8~trusty0 51 True
# multiload-ng-indicator 1.5.2-1~webupd8~trusty0 62 True
# musique 1.3-1~webupd8~trusty 4449 True
# nautilus-columns 0.3.3-1~webupd8~1 3804 False
# nautilus-hide 0.2.1-1~webupd8~trusty 125 False
# ncmpcpp 0.7.7-1~webupd8~trusty 191 True
# nemo-gloobus-sushi 0.1~webupd8+2 3355 False
# nvidia-power-indicator 1.0.0-1~webupd8~1 1363 False
# notifyosdconfig 0.3+22+201404260950~ubuntu14.04.1 1234 True
# penguin-subtitle-player 1.0.1-1~webupd8~trusty0 72 True
# pidgin-hangouts 1.0+hg20170628-1~webupd8~trusty0 122 False
# pidgin-indicator 1.0-1~webupd8~trusty0 2229 True
# pidgin-skypeweb 1.4.0+git20170806-1~webupd8~trusty0 117 False
# prime-indicator 0.1-1+git20150211~webupd8~1 28589 False
# prime-indicator-plus 1.0.3-1~webupd8~2 3347 False
# puddletag 1.2.0-2~webupd8~trusty0 1099 False
# pulseaudio-equalizer 2.7.0.2-4~webupd8~1 65035 False
# purple-funyahoo-plusplus 0.1+git20170706-1~webupd8~trusty0 20 True
# purple-skypeweb 1.4.0+git20170806-1~webupd8~trusty0 95 True
# purple-hangouts 1.0+hg20170628-1~webupd8~trusty0 109 True
# python-awn 0.4.2~1+gitb8c2248-ubuntu1~trusty1 378 True
# python-awn-extras 0.4.1~1+git1081e3f-ubuntu2~trusty 193 True
# python-backports-shutil-get-terminal-size 1.0.0-3~webupd8~trusty1 313 False
# python-backports-shutil-which 3.5.1-1~webupd8~trusty1 322 False
# python-cryptodomex 3.4.3-1~webupd8~trusty8 344 True
# python-cryptodomex-dbg 3.4.3-1~webupd8~trusty8 49 True
# python-desktop-agnostic 0.3.94~1+git4d9b6fd-ubuntu0~trusty 464 True
# python-ephem 3.7.3.4-1~webupd8~raring 1699 True
# python-iso-639 0.4.5-1~webupd8~trusty3 362 False
# python-iso3166 0.8-1~webupd8~trusty 362 False
# python-streamlink 0.7.0-1~webupd8~trusty0 145 False
# python-streamlink-doc 0.7.0-1~webupd8~trusty0 14 False
# python3-cryptodomex-dbg 3.4.3-1~webupd8~trusty8 44 True
# python3-cryptodomex 3.4.3-1~webupd8~trusty8 70 True
# python3-iso-639 0.4.5-1~webupd8~trusty3 53 False
# python3-iso3166 0.8-1~webupd8~trusty 54 False
# qgifer 0.2.3-rc2-1~trusty2+1~webupd8~trusty1 976 True
# python3-streamlink 0.7.0-1~webupd8~trusty0 20 False
# qrazercfg 0.39-1~webupd8~trusty0 90 True
# qrazercfg-applet 0.39-1~webupd8~trusty0 66 True
# qt5ct 0.20-1~webupd8~trusty2 325 True
# radiotray-lite 0.2.18-1~webupd8~trusty0 41 True
# razercfg 0.39-1~webupd8~trusty0 96 True
# rclone-browser 1.2-1~webupd8~trusty0 136 True
# rosa-media-player 1.6.9-1~webupd8~trusty2 1309 True
# screenkey 0.9-1~webupd8~trusty1 480 False
# stream2chromecast 0+git20170109-0~webupd8~0 1378 False
# slop 4.2.20-1~webupd8~trusty1 695 True
# steam-skin-manager 4.2+1-1~webupd8~trusty 2588 True
# snappy 1.0-1~webupd8~trusty 1536 True
# streamlink 0.7.0-1~webupd8~trusty0 144 False
# syncthing-gtk 0.9.2.5-1~webupd8~trusty0 669 False
# syncwall 2.0.0-2~webupd8~trusty2 4193 True
# telegram-purple 1.3.1-1~webupd8~trusty0 566 True
# syspeek 0.3+bzr26-1~webupd8~trusty0 7561 False
# textadept-default-cli 9.3-1~webupd8~0 153 False
# textadept 9.3-1~webupd8~0 361 False
# todo-indicator 0.5.0-1+git20170309~webupd8~0 790 False
# transmageddon 1.0-1~webupd8~trusty 19220 False
# twitch-indicator 0.26-1~webupd8~0 492 False
# unity-reboot 0.2.1-2~webupd8~0 2319 False
# unity-dropbox-share 0.6-1~webupd8~0 1393 False
# viberwrapper-indicator 0.1.1~git20150611~webupd8~0 13085 True
# wimlib-dev 1.8.0-1~webupd8~trusty 204 True
# wimlib-doc 1.7.0-1~webupd8~trusty 194 False
# wimlib-doc 1.8.0-1~webupd8~trusty 747 False
# wimlib9 1.7.0-1~webupd8~trusty 773 True
# wimlib15 1.8.0-1~webupd8~trusty 1897 True
# woeusb 2.1.3-1~webupd8~trusty 1898 True
# wimtools 1.8.0-1~webupd8~trusty 1932 True
# winusb 2.1.3-1~webupd8~trusty 1904 False
# update-java 0.5.2-2~webupd8 88806 False
# xfce4-dockbarx-plugin 0.4.1-1~webupd8~trusty2 996 True
# xfce4-multiload-ng-plugin 1.5.2-1~webupd8~trusty0 86 True
# xournal 4.8.really0.4.8-0~webupd8~trusty1 33143 True
# yarock 1.1.6-1~webupd8~trusty2 272 True
# yad 0.39.0-1~webupd8~trusty0 3155 True
# youtube-dlg 0.3.8-1~webupd8~trusty0 14930 False
# youtube-viewer 3.2.7-1~webupd8~trusty0 500 False
# youtube-dl 1:2017.09.02-1~webupd8~trusty0 1667 False
# indicator-script-runner 1.0.2-1 56 False
# indicator-punycode 1.0.3-1 4 False
# indicator-fortune 1.0.25-1 26 False
# indicator-ppa-download-statistics 1.0.57-1 7 False
# indicator-stardate 1.0.33-1 64 False
# indicator-lunar 1.0.73-1 195 False
# indicator-tide 1.0.7-1 9 False
# indicator-virtual-box 1.0.55-1 470 False
