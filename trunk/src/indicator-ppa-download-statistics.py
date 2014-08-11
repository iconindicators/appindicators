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
#  https://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/api/AppIndicator3_0.1/classes/Indicator.html
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-14.04
#  http://launchpad.net/+apidoc
#  http://help.launchpad.net/API/launchpadlib
#  http://help.launchpad.net/API/Hacking


from copy import deepcopy
from gi.repository import AppIndicator3, Gio, GLib, Gtk, Notify
from ppa import PPA, PublishedBinary
from threading import Thread
from urllib.request import urlopen

import itertools, pythonutils, json, locale, logging, operator, os, re, shutil, sys, threading, time, webbrowser


class IndicatorPPADownloadStatistics:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-ppa-download-statistics"
    ICON = NAME
    VERSION = "1.0.43"
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    SERIES = [ "utopic", "trusty", "saucy", "raring", "quantal", "precise", "oneiric", "natty", "maverick", "lucid", "karmic", "jaunty", "intrepid", "hardy", "gutsy", "feisty", "edgy", "dapper", "breezy", "hoary", "warty" ]
    ARCHITECTURES = [ "amd64", "i386" ]

    COMMENTS = "Shows the total downloads of PPAs."
    SVG_ICON = "." + NAME + "-icon"
    SVG_FILE = os.getenv( "HOME" ) + "/" + SVG_ICON + ".svg"

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER = "allowMenuItemsToLaunchBrowser"
    SETTINGS_COMBINE_PPAS = "combinePPAs"
    SETTINGS_FILTERS = "filters"
    SETTINGS_IGNORE_VERSION_ARCHITECTURE_SPECIFIC = "ignoreVersionArchitectureSpecific"
    SETTINGS_PPAS = "ppas"
    SETTINGS_SHOW_NOTIFICATION_ON_UPDATE = "showNotificationOnUpdate"
    SETTINGS_SHOW_SUBMENU = "showSubmenu"
    SETTINGS_SORT_BY_DOWNLOAD = "sortByDownload"
    SETTINGS_SORT_BY_DOWNLOAD_AMOUNT = "sortByDownloadAmount"

    MESSAGE_DOWNLOADING_DATA = "(downloading data...)"
    MESSAGE_ERROR_RETRIEVING_PPA = "(error retrieving PPA)"
    MESSAGE_MULTIPLE_MESSAGES_UNCOMBINE = "(multiple messages - uncombine PPAs)"
    MESSAGE_NO_PUBLISHED_BINARIES = "(no published binaries)"
    MESSAGE_PUBLISHED_BINARIES_COMPLETELY_FILTERED = "(published binaries completely filtered)"


    def __init__( self ):
        self.dialog = None

        GLib.threads_init()
        self.lock = threading.Lock()
        self.downloadInProgress = False
        self.preferencesOpen = False
        Notify.init( IndicatorPPADownloadStatistics.NAME )
        self.quitRequested = False

        filehandler = pythonutils.TruncatedFileHandler( IndicatorPPADownloadStatistics.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )

        self.loadSettings()

        self.indicator = AppIndicator3.Indicator.new( IndicatorPPADownloadStatistics.NAME, IndicatorPPADownloadStatistics.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling!
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.buildMenu()


    def main( self ):
        self.requestPPADownloadAndMenuRefresh( False )
        GLib.timeout_add_seconds( 6 * 60 * 60, self.requestPPADownloadAndMenuRefresh, True ) # Auto update every 6 hours.
        Gtk.main()


    def buildMenu( self ):
        menu = Gtk.Menu()

        # Add PPAs to the menu...
        ppas = deepcopy( self.ppas ) # Leave the original download data as is - makes dynamic (user) changes faster (don't have to re-download).

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
                    if ppa.getStatus() == PPA.STATUS_ERROR_RETRIEVING_PPA: message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_RETRIEVING_PPA
                    elif ppa.getStatus() == PPA.STATUS_NEEDS_DOWNLOAD: message = IndicatorPPADownloadStatistics.MESSAGE_DOWNLOADING_DATA
                    elif ppa.getStatus() == PPA.STATUS_NO_PUBLISHED_BINARIES: message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES
                    elif ppa.getStatus() == PPA.STATUS_PUBLISHED_BINARIES_COMPLETELY_FILTERED: message = IndicatorPPADownloadStatistics.MESSAGE_PUBLISHED_BINARIES_COMPLETELY_FILTERED
                    else: message = IndicatorPPADownloadStatistics.MESSAGE_MULTIPLE_MESSAGES_UNCOMBINE

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
                    if ppa.getStatus() == PPA.STATUS_ERROR_RETRIEVING_PPA: message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_RETRIEVING_PPA
                    elif ppa.getStatus() == PPA.STATUS_NEEDS_DOWNLOAD: message = IndicatorPPADownloadStatistics.MESSAGE_DOWNLOADING_DATA
                    elif ppa.getStatus() == PPA.STATUS_NO_PUBLISHED_BINARIES: message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES
                    elif ppa.getStatus() == PPA.STATUS_PUBLISHED_BINARIES_COMPLETELY_FILTERED: message = IndicatorPPADownloadStatistics.MESSAGE_PUBLISHED_BINARIES_COMPLETELY_FILTERED
                    else: message = IndicatorPPADownloadStatistics.MESSAGE_MULTIPLE_MESSAGES_UNCOMBINE

                    menuItem = Gtk.MenuItem( indent + message )
                    menu.append( menuItem )

        menu.append( Gtk.SeparatorMenuItem() )

        preferencesMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        menu.append( preferencesMenuItem )

        aboutMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        aboutMenuItem.connect( "activate", self.onAbout )
        menu.append( aboutMenuItem )

        quitMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        quitMenuItem.connect( "activate", self.quit )
        menu.append( quitMenuItem )

        self.indicator.set_menu( menu )
        menu.show_all()


    def quit( self, widget ):
        if not self.quitRequested:
            self.quitRequested = True
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

                if publishedBinary.isArchitectureSpecific(): temp[ key ].setDownloadCount( temp[ key ].getDownloadCount() + publishedBinary.getDownloadCount() ) # Append the download count.

            ppa.resetPublishedBinaries()
            for key in temp: ppa.addPublishedBinary( temp[ key ] )
            if ppa.getStatus() == PPA.STATUS_OK: ppa.setStatus( PPA.STATUS_OK ) # This will force the published binaries to be sorted.
            ppas.append( ppa  )

        ppas.sort( key = operator.methodcaller( "getKey" ) )


    def sortByDownloadAndClip( self, ppas ):
        for ppa in ppas: ppa.sortPublishedBinariesByDownloadCountAndClip( self.sortByDownloadAmount )


    def onPPA( self, widget ):
        if self.allowMenuItemsToLaunchBrowser == False: return

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


    def onPreferences( self, widget ):
        if self.downloadInProgress:
            Notify.Notification.new( "Downloading...", "Preferences are currently unavailable.", IndicatorPPADownloadStatistics.ICON ).show()
            return

        if self.dialog is not None:
            self.dialog.present()
            return

        with self.lock: self.preferencesOpen = True

        self.ppasOrFiltersModified = False

        notebook = Gtk.Notebook()

        # First tab - display settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showAsSubmenusCheckbox = Gtk.CheckButton( "Show PPAs as submenus" )
        showAsSubmenusCheckbox.set_tooltip_text( "The download statitics for each PPA are shown in a separate submenu." )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )
        grid.attach( showAsSubmenusCheckbox, 0, 0, 2, 1 )

        combinePPAsCheckbox = Gtk.CheckButton( "Combine PPAs" )
        toolTip = "Combine the statistics of binary packages when the PPA user/name are the same.\n\n"
        toolTip += "When not architecture specific (such as Python),\n"
        toolTip += "if the package names and version numbers of two binary packages are identical,\n"
        toolTip += "the packages are treated as the same package and the download counts are NOT summed.\n\n"
        toolTip += "For architecture specific (such as compiled C),\n"
        toolTip += "if the package names and version numbers of two binary packages are identical,\n"
        toolTip += "the packages are treated as the same package and the download counts ARE summed."
        combinePPAsCheckbox.set_tooltip_text( toolTip )
        combinePPAsCheckbox.set_active( self.combinePPAs )
        grid.attach( combinePPAsCheckbox, 0, 1, 2, 1 )

        ignoreVersionArchitectureSpecificCheckbox = Gtk.CheckButton( "Ignore version for architecture specific" )
        ignoreVersionArchitectureSpecificCheckbox.set_margin_left( 15 )

        toolTip = "For architecture specific, sometimes the same package name\n"
        toolTip += "but different version 'number' is actually the SAME package.\n\n"
        toolTip += "For example, a source C package for both Ubuntu Saucy and Ubuntu Trusty\n"
        toolTip += "will be compiled twice, each with a different version 'number',\n"
        toolTip += "despite being the SAME release.\n\n"
        toolTip += "Checking this option will ignore the version number when\n"
        toolTip += "determining if two architecture specific packages are identical.\n\n"
        toolTip += "The version number is retained only if it is identical\n"
        toolTip += "across ALL instances of a published binary."
        ignoreVersionArchitectureSpecificCheckbox.set_tooltip_text( toolTip )
        ignoreVersionArchitectureSpecificCheckbox.set_active( self.ignoreVersionArchitectureSpecific )
        ignoreVersionArchitectureSpecificCheckbox.set_sensitive( combinePPAsCheckbox.get_active() )
        grid.attach( ignoreVersionArchitectureSpecificCheckbox, 0, 2, 2, 1 )

        combinePPAsCheckbox.connect( "toggled", self.onCombinePPAsCheckbox, ignoreVersionArchitectureSpecificCheckbox )

        sortByDownloadCheckbox = Gtk.CheckButton( "Sort by download" )
        sortByDownloadCheckbox.set_tooltip_text( "Sort by download (highest first) within each PPA." )
        sortByDownloadCheckbox.set_active( self.sortByDownload )
        grid.attach( sortByDownloadCheckbox, 0, 3, 2, 1 )

        label = Gtk.Label( "  Clip amount" )
        label.set_sensitive( sortByDownloadCheckbox.get_active() )
        label.set_margin_left( 15 )
        grid.attach( label, 0, 4, 1, 1 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.sortByDownloadAmount, 0, 10000, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinner.set_value( self.sortByDownloadAmount ) # ...so need to force the initial value by explicitly setting it.
        spinner.set_tooltip_text( "Limit the number of entries when sorting by download.\nA value of zero will not clip." )
        spinner.set_sensitive( sortByDownloadCheckbox.get_active() )
        grid.attach( spinner, 1, 4, 1, 1 )

        sortByDownloadCheckbox.connect( "toggled", self.onClipByDownloadCheckbox, label, spinner )

        showNotificationOnUpdateCheckbox = Gtk.CheckButton( "Notify on update" )
        showNotificationOnUpdateCheckbox.set_tooltip_text( "Show a screen notification when the PPA\ndownload statistics have been updated AND\nare different to the last download." )
        showNotificationOnUpdateCheckbox.set_active( self.showNotificationOnUpdate )
        grid.attach( showNotificationOnUpdateCheckbox, 0, 5, 2, 1 )

        notebook.append_page( grid, Gtk.Label( "Display" ) )

        # Second tab - PPAs.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        ppaStore = Gtk.ListStore( str, str, str, str ) # PPA User, PPA Name, Series, Architecture.
        ppaStore.set_sort_column_id( 0, Gtk.SortType.ASCENDING )
        for ppa in self.ppas: ppaStore.append( [ ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() ] )

        ppaTree = Gtk.TreeView( ppaStore )
        ppaTree.set_hexpand( True )
        ppaTree.set_vexpand( True )
        ppaTree.append_column( Gtk.TreeViewColumn( "PPA User", Gtk.CellRendererText(), text = 0 ) )
        ppaTree.append_column( Gtk.TreeViewColumn( "PPA Name", Gtk.CellRendererText(), text = 1 ) )
        ppaTree.append_column( Gtk.TreeViewColumn( "Series", Gtk.CellRendererText(), text = 2 ) )
        ppaTree.append_column( Gtk.TreeViewColumn( "Architecture", Gtk.CellRendererText(), text = 3 ) )
        ppaTree.set_tooltip_text( "Double click to edit a PPA" )
        ppaTree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        ppaTree.connect( "row-activated", self.onPPADoubleClick )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( ppaTree )
        grid.attach( scrolledWindow, 0, 0, 1, 1 )

        hbox = Gtk.Box( spacing = 6 )
        hbox.set_homogeneous( True )

        addButton = Gtk.Button( "Add" )
        addButton.set_tooltip_text( "Add a new PPA" )
        addButton.connect( "clicked", self.onPPAAdd, ppaTree )
        hbox.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button( "Remove" )
        removeButton.set_tooltip_text( "Remove the selected PPA" )
        removeButton.connect( "clicked", self.onPPARemove, ppaTree )
        hbox.pack_start( removeButton, True, True, 0 )

        hbox.set_halign( Gtk.Align.CENTER )
        grid.attach( hbox, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "PPAs" ) )

        # Third tab - filters.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        filterStore = Gtk.ListStore( str, str ) # 'PPA User | PPA Name', filter text.
        filterStore.set_sort_column_id( 0, Gtk.SortType.ASCENDING )
        for key in sorted( self.filters ): filterStore.append( [ key, "\n".join( self.filters[ key ] ) ] )

        filterTree = Gtk.TreeView( filterStore )
        filterTree.set_grid_lines( Gtk.TreeViewGridLines.HORIZONTAL )
        filterTree.set_hexpand( True )
        filterTree.set_vexpand( True )
        filterTree.append_column( Gtk.TreeViewColumn( "PPA", Gtk.CellRendererText(), text = 0 ) )
        filterTree.append_column( Gtk.TreeViewColumn( "Filter", Gtk.CellRendererText(), text = 1 ) )
        filterTree.set_tooltip_text( "Double click to edit a filter." )
        filterTree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        filterTree.connect( "row-activated", self.onFilterDoubleClick, ppaTree )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( filterTree )
        grid.attach( scrolledWindow, 0, 0, 1, 1 )

        hbox = Gtk.Box( spacing = 6 )
        hbox.set_homogeneous( True )

        addButton = Gtk.Button( "Add" )
        addButton.set_tooltip_text( "Add a new filter" )
        addButton.connect( "clicked", self.onFilterAdd, filterTree, ppaTree )
        hbox.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button( "Remove" )
        removeButton.set_tooltip_text( "Remove the selected filter" )
        removeButton.connect( "clicked", self.onFilterRemove, filterTree )
        hbox.pack_start( removeButton, True, True, 0 )

        hbox.set_halign( Gtk.Align.CENTER )
        grid.attach( hbox, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "Filters" ) )

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
        autostartCheckbox.set_tooltip_text( "Run the indicator automatically" )
        grid.attach( autostartCheckbox, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "General" ) )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorPPADownloadStatistics.ICON )
        self.dialog.show_all()

        if self.dialog.run() == Gtk.ResponseType.OK:

            self.showSubmenu = showAsSubmenusCheckbox.get_active()
            self.combinePPAs = combinePPAsCheckbox.get_active()
            self.ignoreVersionArchitectureSpecific = ignoreVersionArchitectureSpecificCheckbox.get_active()
            self.sortByDownload = sortByDownloadCheckbox.get_active()
            self.sortByDownloadAmount = spinner.get_value_as_int()
            self.showNotificationOnUpdate = showNotificationOnUpdateCheckbox.get_active()
            self.allowMenuItemsToLaunchBrowser = allowMenuItemsToLaunchBrowserCheckbox.get_active()

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

            self.saveSettings()

            if not os.path.exists( IndicatorPPADownloadStatistics.AUTOSTART_PATH ): os.makedirs( IndicatorPPADownloadStatistics.AUTOSTART_PATH )

            if autostartCheckbox.get_active():
                try: shutil.copy( IndicatorPPADownloadStatistics.DESKTOP_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE, IndicatorPPADownloadStatistics.AUTOSTART_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE )
                except Exception as e: logging.exception( e )
            else:
                try: os.remove( IndicatorPPADownloadStatistics.AUTOSTART_PATH + IndicatorPPADownloadStatistics.DESKTOP_FILE )
                except: pass

            GLib.timeout_add_seconds( 1, self.buildMenu )

            if self.ppasOrFiltersModified:
                GLib.timeout_add_seconds( 10, self.requestPPADownloadAndMenuRefresh, False ) # Hopefully 10 seconds is sufficient to rebuild the menu!
                with self.lock: self.downloadInProgress = True # Although the download hasn't actually started, this ensures the preferences cannot be opened until the download completes.

        self.dialog.destroy()
        self.dialog = None
        with self.lock: self.preferencesOpen = False


    def onCombinePPAsCheckbox( self, source, checkbox ): checkbox.set_sensitive( source.get_active() )


    def onClipByDownloadCheckbox( self, source, spinner, label ):
        label.set_sensitive( source.get_active() )
        spinner.set_sensitive( source.get_active() )


    def onPPARemove( self, button, tree ):
        model, treeiter = tree.get_selection().get_selected()

        if treeiter is None:
            pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, "No PPA has been selected for removal." )
            return

        # Prompt the user to remove - only one row can be selected since single selection mode has been set.
        if pythonutils.showOKCancel( self.dialog, "Remove the selected PPA?" ) == Gtk.ResponseType.OK:
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

        label = Gtk.Label( "PPA User" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        if len( model ) > 0:
            ppaUsers = [ ]
            for row in range( len( model ) ):
                if model[ row ][ 0 ] not in ppaUsers:
                    ppaUsers.append( model[ row ][ 0 ] )

            ppaUsers.sort( key = locale.strxfrm )

            ppaUser = Gtk.ComboBoxText.new_with_entry()
            for item in ppaUsers: ppaUser.append_text( item )

            if rowNumber is not None: ppaUser.set_active( ppaUsers.index( model[ treeiter ][ 0 ] ) ) # This is an edit.

        else:
            ppaUser = Gtk.Entry() # There are no PPAs present - adding the first PPA.

        ppaUser.set_hexpand( True ) # Only need to set this once and all objects will expand.

        grid.attach( ppaUser, 1, 0, 1, 1 )

        label = Gtk.Label( "PPA Name" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        if len( model ) > 0:
            ppaNames = [ ] 
            for row in range( len( model ) ):
                if model[ row ][ 1 ] not in ppaNames:
                    ppaNames.append( model[ row ][ 1 ] )

            ppaNames.sort( key = locale.strxfrm )

            ppaName = Gtk.ComboBoxText.new_with_entry()
            for item in ppaNames: ppaName.append_text( item )

            if rowNumber is not None: ppaName.set_active( ppaNames.index( model[ treeiter ][ 1 ] ) ) # This is an edit.

        else:
            ppaName = Gtk.Entry() # There are no PPAs present - adding the first PPA.

        grid.attach( ppaName, 1, 1, 1, 1 )

        label = Gtk.Label( "Series" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        series = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.SERIES:
            series.append_text( item )

        if rowNumber is not None: series.set_active( IndicatorPPADownloadStatistics.SERIES.index( model[ treeiter ][ 2 ] ) )
        else: series.set_active( 0 )

        grid.attach( series, 1, 2, 1, 1 )

        label = Gtk.Label( "Architecture" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        architectures = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.ARCHITECTURES: architectures.append_text( item )

        if rowNumber is not None: architectures.set_active( IndicatorPPADownloadStatistics.ARCHITECTURES.index( model[ treeiter ][ 3 ] ) )
        else: architectures.set_active( 0 )

        grid.attach( architectures, 1, 3, 1, 1 )

        title = "Edit PPA"
        if rowNumber is None: title = "Add PPA"

        dialog = Gtk.Dialog( title, self.dialog, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
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
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, "PPA user cannot be empty." )
                    ppaUser.grab_focus()
                    continue

                if ppaNameValue == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, "PPA name cannot be empty." )
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
                            if \
                                ppaUserValue == model[ row ][ 0 ] and \
                                ppaNameValue == model[ row ][ 1 ] and \
                                series.get_active_text() == model[ row ][ 2 ] and \
                                architectures.get_active_text() == model[ row ][ 3 ]:

                                duplicate = True
                                break

                        if duplicate:
                            pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, "Duplicates disallowed - there is an identical PPA!" )
                            continue

                # Update the model...
                if rowNumber is not None: model.remove( treeiter ) # This is an edit...remove the old value and append new value.  
                model.append( [ ppaUserValue, ppaNameValue, series.get_active_text(), architectures.get_active_text() ] )

                self.ppasOrFiltersModified = True

            break

        dialog.destroy()


    def onFilterRemove( self, button, tree ):
        model, treeiter = tree.get_selection().get_selected()

        if treeiter is None:
            pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, "No filter has been selected for removal." )
            return

        # Prompt the user to remove - only one row can be selected since single selection mode has been set.
        if pythonutils.showOKCancel( self.dialog, "Remove the selected filter?" ) == Gtk.ResponseType.OK:
            model.remove( treeiter )
            self.ppasOrFiltersModified = True


    def onFilterAdd( self, button, filterTree, ppaTree ):
        if len( ppaTree.get_model() ) == 0:
            pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, "Please add a PPA first!" )
        else:

            # If the number of filters equals the number of PPA User/Names, cannot add a filter!
            ppaUsersNames = [ ]
            for ppa in range( len( ppaTree.get_model() ) ):
                ppaUserName = ppaTree.get_model()[ ppa ][ 0 ] + " | " + ppaTree.get_model()[ ppa ][ 1 ]
                if not ppaUserName in ppaUsersNames:
                    ppaUsersNames.append( ppaUserName )

            if len( filterTree.get_model() ) == len( ppaUsersNames ): pythonutils.showMessage( self.dialog, Gtk.MessageType.INFO, "Only one filter per PPA User/Name." )
            else: self.onFilterDoubleClick( filterTree, None, None, ppaTree )


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

        label = Gtk.Label( "PPA User/Name" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        ppaUsersNames = Gtk.ComboBoxText.new()
        if rowNumber is None: # Adding
            temp = [ ] # Used to ensure duplicates are not added.
            for ppa in range( len( ppaTreeModel ) ): # List of PPA User/Names from the list of PPAs in the preferences.
                ppaUserName = ppaTreeModel[ ppa ][ 0 ] + " | " + ppaTreeModel[ ppa ][ 1 ]
                if ppaUserName in temp: continue

                # Ensure the PPA User/Name is not present in the list of filters in the preferences.
                inFilterList = False
                for filter in range( len( filterTreeModel ) ):
                    if ppaUserName in filterTreeModel[ filter ][ 0 ]:
                        inFilterList = True
                        break

                if not inFilterList:                        
                    ppaUsersNames.append_text( ppaUserName )
                    temp.append( ppaUserName )

        else: ppaUsersNames.append_text( filterTreeModel[ filterTreeIter ][ 0 ] )

        ppaUsersNames.set_hexpand( True )
        ppaUsersNames.set_active( 0 )

        grid.attach( ppaUsersNames, 1, 0, 1, 1 )

        label = Gtk.Label( "Filter Text" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 2, 1 )

        textview = Gtk.TextView()
        toolTip = "Each line of text is a single filter which is compared\n" + \
                  "against each package name during download.\n\n" + \
                  "If a package name contains ANY part of ANY filter,\n" + \
                  "that package is included in the download statistics.\n\n" + \
                  "No wildcards nor regular expressions accepted!"

        textview.set_tooltip_text( toolTip )
        if rowNumber is not None: textview.get_buffer().set_text( filterTreeModel[ filterTreeIter ][ 1 ] ) # This is an edit.

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add( textview )
        scrolledwindow.set_hexpand( True )
        scrolledwindow.set_vexpand( True )

        grid.attach( scrolledwindow, 0, 3, 2, 1 )

        title = "Edit Filter"
        if rowNumber is None: title = "Add Filter"

        dialog = Gtk.Dialog( title, self.dialog, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
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
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, "Please enter filter text!" )
                    continue

                # Update the model...
                if rowNumber is not None: filterTreeModel.remove( filterTreeIter ) # This is an edit...remove the old value and append new value.  
                filterTreeModel.append( [ ppaUsersNames.get_active_text(), filterText ] ) 

                self.ppasOrFiltersModified = True

            break

        dialog.destroy()


    def loadSettings( self ):
        self.allowMenuItemsToLaunchBrowser = True
        self.sortByDownload = False
        self.sortByDownloadAmount = 5
        self.combinePPAs = False
        self.ignoreVersionArchitectureSpecific = True
        self.showSubmenu = False
        self.showNotificationOnUpdate = True
        self.filterAtDownload = True

        self.ppas = [ ]
        self.ppasPrevious = [ ] # Used to hold the most recent download for comparison.

        if os.path.isfile( IndicatorPPADownloadStatistics.SETTINGS_FILE ):
            try:
                with open( IndicatorPPADownloadStatistics.SETTINGS_FILE, "r" ) as f: settings = json.load( f )

                ppas = settings.get( IndicatorPPADownloadStatistics.SETTINGS_PPAS, [ ] )
                for ppa in ppas: self.ppas.append( PPA( ppa[ 0 ], ppa[ 1 ], ppa[ 2 ], ppa[ 3 ] ) )

                self.ppas.sort( key = operator.methodcaller( "getKey" ) )

                self.allowMenuItemsToLaunchBrowser = settings.get( IndicatorPPADownloadStatistics.SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER, self.allowMenuItemsToLaunchBrowser )
                self.combinePPAs = settings.get( IndicatorPPADownloadStatistics.SETTINGS_COMBINE_PPAS, self.combinePPAs )
                self.filters = settings.get( IndicatorPPADownloadStatistics.SETTINGS_FILTERS, { } )
                self.ignoreVersionArchitectureSpecific = settings.get( IndicatorPPADownloadStatistics.SETTINGS_IGNORE_VERSION_ARCHITECTURE_SPECIFIC, self.ignoreVersionArchitectureSpecific )
                self.showNotificationOnUpdate = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SHOW_NOTIFICATION_ON_UPDATE, self.showNotificationOnUpdate )
                self.showSubmenu = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SHOW_SUBMENU, self.showSubmenu )
                self.sortByDownload = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD, self.sortByDownload )
                self.sortByDownloadAmount = settings.get( IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD_AMOUNT, self.sortByDownloadAmount )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorPPADownloadStatistics.SETTINGS_FILE )
                self.initialiseDefaultSettings()

        else: self.initialiseDefaultSettings() # No properties file exists, so populate with a sample PPA to give the user an idea of the format.


    def initialiseDefaultSettings( self ):
        self.ppas = [ ]
        self.ppas.append( PPA( "thebernmeister", "ppa", "trusty", "amd64" ) )
        self.filters = { }
        self.filters[ 'thebernmeister | ppa' ] = [ "indicator-fortune", "indicator-lunar", "indicator-ppa-download-statistics", "indicator-stardate", "indicator-virtual-box", "python3-ephem" ]


    def saveSettings( self ):
        try:
            ppas = [ ]
            for ppa in self.ppas: ppas.append( [ ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() ] )

            settings = {
                IndicatorPPADownloadStatistics.SETTINGS_ALLOW_MENU_ITEMS_TO_LAUNCH_BROWSER: self.allowMenuItemsToLaunchBrowser,
                IndicatorPPADownloadStatistics.SETTINGS_FILTERS: self.filters,
                IndicatorPPADownloadStatistics.SETTINGS_COMBINE_PPAS: self.combinePPAs,
                IndicatorPPADownloadStatistics.SETTINGS_IGNORE_VERSION_ARCHITECTURE_SPECIFIC: self.ignoreVersionArchitectureSpecific,
                IndicatorPPADownloadStatistics.SETTINGS_PPAS: ppas,
                IndicatorPPADownloadStatistics.SETTINGS_SHOW_NOTIFICATION_ON_UPDATE: self.showNotificationOnUpdate,
                IndicatorPPADownloadStatistics.SETTINGS_SHOW_SUBMENU: self.showSubmenu,
                IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD: self.sortByDownload,
                IndicatorPPADownloadStatistics.SETTINGS_SORT_BY_DOWNLOAD_AMOUNT: self.sortByDownloadAmount
            }

            with open( IndicatorPPADownloadStatistics.SETTINGS_FILE, "w" ) as f: f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorPPADownloadStatistics.SETTINGS_FILE )


    def requestPPADownloadAndMenuRefresh( self, runAgain ):
        Thread( target = self.getPPADownloadStatistics ).start()
        return runAgain


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
        if self.preferencesOpen:
            # If the user has the preferences open and an automatic update has kicked off, reschedule the update.
            GLib.timeout_add_seconds( 60, self.requestPPADownloadAndMenuRefresh, False )
            return

        with self.lock: self.downloadInProgress = True

        for ppa in self.ppas:
            ppa.setStatus( PPA.STATUS_NEEDS_DOWNLOAD )
            key = ppa.getUser() + " | " + ppa.getName()
            if key in self.filters: self.getPublishedBinariesWithFilters( ppa )
            else: self.getPublishedBinariesNoFilters( ppa )

        # Have a second attempt at failures...
        for ppa in self.ppas:
            if ppa.getStatus() == PPA.STATUS_ERROR_RETRIEVING_PPA:
                ppa.setStatus( PPA.STATUS_NEEDS_DOWNLOAD )
                key = ppa.getUser() + " | " + ppa.getName()
                if key in self.filters: self.getPublishedBinariesWithFilters( ppa )
                else: self.getPublishedBinariesNoFilters( ppa )

        with self.lock: self.downloadInProgress = False

        GLib.idle_add( self.buildMenu )

        if self.showNotificationOnUpdate and not self.quitRequested and self.ppasPrevious != self.ppas:
            Notify.Notification.new( "Statistics downloaded!", "", IndicatorPPADownloadStatistics.ICON ).show()

        self.ppasPrevious = deepcopy( self.ppas ) # Take a copy to be used for comparison on the next download.


    def getPublishedBinariesNoFilters( self, ppa ):
        baseURL = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName() + \
                "?ws.op=getPublishedBinaries" + \
                "&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + ppa.getSeries() + "/" + ppa.getArchitecture() + \
                "&status=Published"

        url = baseURL
        try:
            publishedBinaries = json.loads( urlopen( url ).read().decode( "utf8" ) )
            numberOfPublishedBinaries = publishedBinaries[ "total_size" ]
            if numberOfPublishedBinaries == 0: ppa.setStatus( PPA.STATUS_NO_PUBLISHED_BINARIES )
            else: self.processPublishedBinaries( ppa, baseURL, publishedBinaries, numberOfPublishedBinaries )

        except Exception as e:
            logging.exception( e )
            ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )


    def getPublishedBinariesWithFilters( self, ppa ):
        for filter in self.filters.get( ppa.getUser() + " | " + ppa.getName() ):

            baseURL = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName() + \
                    "?ws.op=getPublishedBinaries" + \
                    "&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + ppa.getSeries() + "/" + ppa.getArchitecture() + \
                    "&status=Published" + \
                    "&exact_match=false" + \
                    "&ordered=false" + \
                    "&binary_name=" + filter

            url = baseURL
            try:
                publishedBinaries = json.loads( urlopen( url ).read().decode( "utf8" ) )
                numberOfPublishedBinaries = publishedBinaries[ "total_size" ]
                if numberOfPublishedBinaries == 0: ppa.setStatus( PPA.STATUS_NO_PUBLISHED_BINARIES )
                else: self.processPublishedBinaries( ppa, baseURL, publishedBinaries, numberOfPublishedBinaries )

            except Exception as e:
                logging.exception( e )
                ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )


    # Takes the published binary and extracts the information needed to get the download count (for each package).
    # The results in a published binary are returned in lots of 75; for more than 75 published binaries, loop to get the remainder.
    def processPublishedBinaries( self, ppa, baseURL, publishedBinaries, numberOfPublishedBinaries ):
        try:
            index = 0
            resultPage = 1
            resultsPerUrl = 75
            threads = []
            for i in range( numberOfPublishedBinaries ):
                if self.quitRequested:
                    self.quit( None )
                    return

                if i == ( resultPage * resultsPerUrl ):
                    # Handle result pages after the first page.
                    url = baseURL + "&ws.start=" + str( resultPage * resultsPerUrl )
                    publishedBinaries = json.loads( urlopen( url ).read().decode( "utf8" ) )
                    resultPage += 1
                    index = 0

                packageName = publishedBinaries[ "entries" ][ index ][ "binary_package_name" ]

                # Limit to 10 concurrent fetches of package download count...
                if len( threads ) > 10:
                    for t in threads: t.join()
                    threads = []

                packageVersion = publishedBinaries[ "entries" ][ index ][ "binary_package_version" ]
                architectureSpecific = publishedBinaries[ "entries" ][ index ][ "architecture_specific" ]
                indexLastSlash = publishedBinaries[ "entries" ][ index ][ "self_link" ].rfind( "/" )
                packageId = publishedBinaries[ "entries" ][ index ][ "self_link" ][ indexLastSlash + 1 : ]

                t = Thread( target = self.getDownloadCount, args = ( ppa, packageName, packageVersion, architectureSpecific, packageId ) )
                t.start()
                threads.append( t )

                index += 1

            for t in threads: t.join() # Wait for remaining threads...

            # The only status the PPA can be at this point is needs download (the initial ppa status) or error retrieving ppa (set by get download count).
            if ppa.getStatus() != PPA.STATUS_ERROR_RETRIEVING_PPA:
                ppa.setStatus( PPA.STATUS_OK )
                if len( ppa.getPublishedBinaries() ) == 0: ppa.setStatus( PPA.STATUS_PUBLISHED_BINARIES_COMPLETELY_FILTERED )

        except Exception as e:
            logging.exception( e )
            ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )


    def getDownloadCount( self, ppa, packageName, packageVersion, architectureSpecific, packageId ):
        url = "https://api.launchpad.net/1.0/~" + ppa.getUser() + "/+archive/" + ppa.getName() + "/+binarypub/" + packageId + "?ws.op=getDownloadCount"

        try:
            downloadCount = json.loads( urlopen( url ).read().decode( "utf8" ) )

            with self.lock:
                if str( downloadCount ).isnumeric(): ppa.addPublishedBinary( PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific ) )
                else: ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )

        except Exception as e:
            logging.exception( e )
            with self.lock: ppa.setStatus( PPA.STATUS_ERROR_RETRIEVING_PPA )


if __name__ == "__main__": IndicatorPPADownloadStatistics().main()