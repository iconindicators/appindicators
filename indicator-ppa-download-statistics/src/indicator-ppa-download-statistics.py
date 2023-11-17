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


# Application indicator which displays PPA download statistics.


INDICATOR_NAME = "indicator-ppa-download-statistics"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )

from copy import deepcopy
from gi.repository import Gtk
from indicatorbase import IndicatorBase
from ppa import Filters, PPA, PublishedBinary
from urllib.request import urlopen

import concurrent.futures, json, locale, tempfile, webbrowser


class IndicatorPPADownloadStatistics( IndicatorBase ):

    CONFIG_COMBINE_PPAS = "combinePPAs"
    CONFIG_FILTERS = "filters"
    CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC = "ignoreVersionArchitectureSpecific"
    CONFIG_LOW_BANDWIDTH = "lowBandwidth"
    CONFIG_PPAS = "ppas"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_SORT_BY_DOWNLOAD = "sortByDownload"
    CONFIG_SORT_BY_DOWNLOAD_AMOUNT = "sortByDownloadAmount"

    SERIES = [
        "noble",
        "mantic",
        "lunar",
        "kinetic",
        "jammy",
        "impish",
        "hirsute",
        "groovy",
        "focal",
        "eoan",
        "disco",
        "cosmic",
        "bionic",
        "artful",
        "zesty",
        "yakkety",
        "xenial",
        "wily",
        "vivid",
        "utopic",
        "trusty",
        "saucy",
        "raring",
        "quantal",
        "precise",
        "oneiric",
        "natty",
        "maverick",
        "lucid",
        "karmic",
        "jaunty",
        "intrepid",
        "hardy",
        "gutsy",
        "feisty",
        "edgy",
        "dapper",
        "breezy",
        "hoary",
        "warty" ]

    ARCHITECTURES = [ "amd64", "i386" ]

    MESSAGE_ERROR_RETRIEVING_PPA = _( "(error retrieving PPA)" )
    MESSAGE_NO_PUBLISHED_BINARIES = _( "(no published binaries)" )
    MESSAGE_NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED = _( "(no published binaries and/or completely filtered)" )
    MESSAGE_PUBLISHED_BINARIES_COMPLETELY_FILTERED = _( "(published binaries completely filtered)" )

    # Data model columns used in the Preferences dialog.
    COLUMN_USER = 0
    COLUMN_NAME = 1
    COLUMN_SERIES = 2
    COLUMN_ARCHITECTURE = 3
    COLUMN_FILTER_TEXT = 4


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.80",
            copyrightStartYear = "2012",
            comments = _( "Display the total downloads of PPAs." ) )


    def update( self, menu ):
        self.downloadPPAStatistics()
        self.buildMenu( menu )
        return 6 * 60 * 60 # Update every six hours.


    def buildMenu( self, menu ):
        ppas = deepcopy( self.ppas ) # Take a copy as the combine mechanism can alter the PPA series/architecture.

        if self.combinePPAs:
            ppas = self.combine( ppas )

        if self.sortByDownload:
            for ppa in ppas:
                ppa.sortPublishedBinariesByDownloadCountAndClip( self.sortByDownloadAmount )

        if self.showSubmenu:
            indent = self.getMenuIndent()
            for ppa in ppas:
                menuItem = Gtk.MenuItem.new_with_label( ppa.getDescriptor() )
                menu.append( menuItem )
                subMenu = Gtk.Menu()
                if ppa.getStatus() == PPA.Status.OK:
                    publishedBinaries = ppa.getPublishedBinaries( True )
                    for publishedBinary in publishedBinaries:
                        self.createMenuItemForPublishedBinary( subMenu, indent, ppa, publishedBinary )
                        menuItem.set_submenu( subMenu )

                else:
                    self.createMenuItemForStatusMessage( subMenu, indent, ppa )
                    menuItem.set_submenu( subMenu )

        else:
            indent = self.getMenuIndent()
            for ppa in ppas:
                menuItem = Gtk.MenuItem.new_with_label( ppa.getDescriptor() )
                menu.append( menuItem )
                menuItem.set_name( ppa.getDescriptor() )
                menuItem.connect( "activate", self.onPPA )
                if ppa.getStatus() == PPA.Status.OK:
                    publishedBinaries = ppa.getPublishedBinaries( True )
                    for publishedBinary in publishedBinaries:
                        self.createMenuItemForPublishedBinary( menu, indent, ppa, publishedBinary )

                else:
                    self.createMenuItemForStatusMessage( menu, indent, ppa )

            # When only one PPA is present, enable middle mouse click on the icon to open the PPA in the browser.
            if len( ppas ) == 1:
                self.secondaryActivateTarget = menuItem


    def createMenuItemForPublishedBinary( self, menu, indent, ppa, publishedBinary ):
        label = indent + publishedBinary.getPackageName()
        if publishedBinary.getPackageVersion() is None:
            label += ":  " + str( publishedBinary.getDownloadCount() )

        else:
            label += " " + publishedBinary.getPackageVersion() + ":  " + str( publishedBinary.getDownloadCount() )

        menuItem = Gtk.MenuItem.new_with_label( label )
        menuItem.set_name( ppa.getDescriptor() )
        menuItem.connect( "activate", self.onPPA )
        menu.append( menuItem )


    def createMenuItemForStatusMessage( self, menu, indent, ppa ):
        if ppa.getStatus() == PPA.Status.ERROR_RETRIEVING_PPA:
            message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_RETRIEVING_PPA

        elif ppa.getStatus() == PPA.Status.NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED:
            message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED

        elif ppa.getStatus() == PPA.Status.NO_PUBLISHED_BINARIES:
            message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES

        elif ppa.getStatus() == PPA.Status.PUBLISHED_BINARIES_COMPLETELY_FILTERED:
            message = IndicatorPPADownloadStatistics.MESSAGE_PUBLISHED_BINARIES_COMPLETELY_FILTERED

        menuItem = Gtk.MenuItem.new_with_label( indent + message )
        menu.append( menuItem )


    def combine( self, ppas ):
        # Match up identical PPAs: two PPAs are deemed to match if their 'PPA User | PPA Name' are identical.
        combinedPPAs = { }
        for ppa in ppas:
            key = ppa.getUser() + " | " + ppa.getName()
            if key in combinedPPAs:
                if ppa.getStatus() == PPA.Status.ERROR_RETRIEVING_PPA or combinedPPAs[ key ].getStatus() == PPA.Status.ERROR_RETRIEVING_PPA:
                    combinedPPAs[ key ].setStatus( PPA.Status.ERROR_RETRIEVING_PPA )

                elif ppa.getStatus() == PPA.Status.OK or combinedPPAs[ key ].getStatus() == PPA.Status.OK:
                    combinedPPAs[ key ].addPublishedBinaries( ppa.getPublishedBinaries() )
                    combinedPPAs[ key ].setStatus( PPA.Status.OK )

                elif ppa.getStatus() == combinedPPAs[ key ].getStatus(): # Both are filtered or both have no published binaries.
                    pass # Nothing to do.

                else: # One is completely filtered and the other has no published binaries.
                    combinedPPAs[ key ].setStatus( PPA.Status.NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED )

            else: # No previous match for this PPA.
                combinedPPAs[ key ] = ppa

        # The combined PPAs either have:
        #    A status of error, or completely filtered, or no published binaries or,
        #    a status of OK with a concatenation of all published binaries from PPAs with the same PPA user/name.
        ppas = [ ]
        for ppa in combinedPPAs.values():
            if ppa.getStatus() == PPA.Status.ERROR_RETRIEVING_PPA or \
               ppa.getStatus() == PPA.Status.NO_PUBLISHED_BINARIES or \
               ppa.getStatus() == PPA.Status.NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED or \
               ppa.getStatus() == PPA.Status.PUBLISHED_BINARIES_COMPLETELY_FILTERED:

               ppas.append( PPA( ppa.getUser(), ppa.getName(), None, None ) )
               ppas[ -1 ].setStatus( ppa.getStatus() )

            else:
                temp = { }
                for publishedBinary in ppa.getPublishedBinaries():
                    key = publishedBinary.getPackageName() + " | " + publishedBinary.getPackageVersion()
                    if publishedBinary.isArchitectureSpecific():
                        if self.ignoreVersionArchitectureSpecific:
                            key = publishedBinary.getPackageName() # Key only contains name.

                        # Add up the download count from each published binary of the same key (package name OR package name and package version).
                        if key in temp:
                            newPublishedBinary = \
                                PublishedBinary(
                                    temp[ key ].getPackageName(),
                                    temp[ key ].getPackageVersion(),
                                    temp[ key ].getDownloadCount() + publishedBinary.getDownloadCount(),
                                    temp[ key ].isArchitectureSpecific )

                            temp[ key ] = newPublishedBinary

                        else:
                            temp[ key ] = publishedBinary
                            if self.ignoreVersionArchitectureSpecific:
                                newPublishedBinary = \
                                    PublishedBinary(
                                        temp[ key ].getPackageName(),
                                        None,
                                        temp[ key ].getDownloadCount(),
                                        temp[ key ].isArchitectureSpecific )

                                temp[ key ] = newPublishedBinary

                    else:
                        if key not in temp:
                            temp[ key ] = publishedBinary

                ppas.append( PPA( ppa.getUser(), ppa.getName(), None, None ) )
                ppas[ -1 ].setStatus( PPA.Status.OK )
                for key in temp:
                    ppas[ -1 ].addPublishedBinary( temp[ key ] )

        PPA.sort( self.ppas )
        return ppas


    def onPPA( self, widget ):
        url = "https://launchpad.net/~"
        firstPipe = str.find( widget.props.name, "|" )
        ppaUser = widget.props.name[ 0 : firstPipe ].strip()
        secondPipe = str.find( widget.props.name, "|", firstPipe + 1 )
        if secondPipe == -1:
            # This is a combined PPA...
            ppaName = widget.props.name[ firstPipe + 1 : ].strip()
            url += ppaUser + "/+archive/ubuntu/" + ppaName
            if widget.props.name != widget.get_label(): # Use the menu item label to specify the package name.
                url += "/+packages?field.name_filter=" + widget.get_label().split()[ 0 ] + "&field.status_filter=published&field.series_filter="

        else:
            ppaName = widget.props.name[ firstPipe + 1 : secondPipe ].strip()
            thirdPipe = str.find( widget.props.name, "|", secondPipe + 1 )
            series = widget.props.name[ secondPipe + 1 : thirdPipe ].strip()
            url += ppaUser + "/+archive/ubuntu/" + ppaName
            if widget.props.name == widget.get_label():
                url += "?field.series_filter=" + series

            else: # Use the menu item label to specify the package name.
                url += "/+packages?field.name_filter=" + widget.get_label().split()[ 0 ] + "&field.status_filter=published&field.series_filter=" + series

        webbrowser.open( url )


    # Get a list of the published binaries for each PPA.
    # From that extract the ID for each binary which is then used to get the download count for each binary.
    # The ID is the number at the end of self_link.
    # The published binary object looks like this...
    # {
    #     "total_size": 4,
    #     "start": 0,
    #     "entries": [
    #     {
    #         "distro_arch_series_link": "https://api.launchpad.net/1.0/ubuntu/precise/i386",
    #         "removal_comment": null,
    #         "display_name": "indicator-lunar 1.0.9-1 in precise i386",
    #         "date_made_pending": null,
    #         "date_superseded": null,
    #         "priority_name": "OPTIONAL",
    #         "http_etag": "\"94b9873b47426c010c4117854c67c028f1acc969-771acce030b1683dc367b5cbf79376d386e7f3b3\"",
    #         "self_link": "https://api.launchpad.net/1.0/~thebernmeister/+archive/ppa/+binarypub/28105302",
    #         "binary_package_version": "1.0.9-1",
    #         "resource_type_link": "https://api.launchpad.net/1.0/#binary_package_publishing_history",
    #         "component_name": "main",
    #         "status": "Published",
    #         "date_removed": null,
    #         "pocket": "Release",
    #         "date_published": "2012-08-09T10:30:49.572656+00:00",
    #         "removed_by_link": null, "section_name": "python",
    #         "date_created": "2012-08-09T10:27:31.762212+00:00",
    #         "binary_package_name": "indicator-lunar",
    #         "archive_link": "https://api.launchpad.net/1.0/~thebernmeister/+archive/ppa",
    #         "architecture_specific": false,
    #         "scheduled_deletion_date": null
    #     }
    #     {
    #     ,...
    # }
    #
    # References:
    #     http://launchpad.net/+apidoc
    #     http://help.launchpad.net/API/launchpadlib
    #     http://help.launchpad.net/API/Hacking
    def downloadPPAStatistics( self ):
        for ppa in self.ppas:
            ppa.setStatus( PPA.Status.NEEDS_DOWNLOAD )
            if self.filters.hasFilter( ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() ):
                hasPublishedBinaries = self.hasPublishedBinaries( ppa )
                if hasPublishedBinaries is None:
                    ppa.setStatus( PPA.Status.ERROR_RETRIEVING_PPA )

                elif hasPublishedBinaries:
                    for theFilter in self.filters.getFilterText( ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() ):
                        self.getPublishedBinaries( ppa, theFilter )
                        if ppa.getStatus() == PPA.Status.ERROR_RETRIEVING_PPA:
                            break # No point continuing with each filter.

                    if not( ppa.getStatus() == PPA.Status.ERROR_RETRIEVING_PPA ):
                        if ppa.getPublishedBinaries():
                            ppa.setStatus( PPA.Status.OK )

                        else:
                            ppa.setStatus( PPA.Status.PUBLISHED_BINARIES_COMPLETELY_FILTERED )

                else:
                    ppa.setStatus( PPA.Status.NO_PUBLISHED_BINARIES )

            else:
                self.getPublishedBinaries( ppa, "" )
                if not ( ppa.getStatus() == PPA.Status.ERROR_RETRIEVING_PPA ):
                    if ppa.getPublishedBinaries():
                        ppa.setStatus( PPA.Status.OK )

                    else:
                        ppa.setStatus( PPA.Status.NO_PUBLISHED_BINARIES )


    def hasPublishedBinaries( self, ppa ):
        url = \
            "https://api.launchpad.net/1.0/~" + \
            ppa.getUser() + "/+archive/ubuntu/" + \
            ppa.getName() + "?ws.op=getPublishedBinaries" + \
            "&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + ppa.getSeries() + "/" + \
            ppa.getArchitecture() + "&status=Published" + \
            "&exact_match=false&ordered=false"

        try:
            publishedBinaries = json.loads( urlopen( url, timeout = IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ) )
            hasPublisedBinaries = publishedBinaries[ "total_size" ] > 0

        except Exception as e:
            hasPublisedBinaries = None
            self.getLogging().error( "Problem with " + url )
            self.getLogging().exception( e )

        return hasPublisedBinaries


    # Use a thread pool executer to get the download counts for each published binary.
    # References:
    #    https://docs.python.org/3/library/concurrent.futures.html
    #    https://pymotw.com/3/concurrent.futures
    #    http://www.dalkescientific.com/writings/diary/archive/2012/01/19/concurrent.futures.html
    def getPublishedBinaries( self, ppa, filterText ):
        url = \
            "https://api.launchpad.net/1.0/~" + \
            ppa.getUser() + "/+archive/ubuntu/" + \
            ppa.getName() + "?ws.op=getPublishedBinaries" + \
            "&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + ppa.getSeries() + "/" + \
            ppa.getArchitecture() + "&status=Published" + \
            "&exact_match=false&ordered=false&binary_name=" + filterText # A filterText of "" equates to no filterText.

        pageNumber = 1
        publishedBinariesPerPage = 75 # Results are presented in at most 75 per page.
        publishedBinaryCounter = 0
        totalPublishedBinaries = publishedBinaryCounter + 1 # Set to a value greater than publishedBinaryCounter to ensure the loop executes at least once.
        while( publishedBinaryCounter < totalPublishedBinaries and ppa.getStatus() == PPA.Status.NEEDS_DOWNLOAD ): # Keep going if there are more downloads and no error has occurred.
            try:
                currentURL =  url + "&ws.start=" + str( publishedBinaryCounter )
                publishedBinaries = json.loads( urlopen( currentURL, timeout = IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ) )

            except Exception as e:
                self.getLogging().error( "Problem with " + currentURL )
                self.getLogging().exception( e )
                ppa.setStatus( PPA.Status.ERROR_RETRIEVING_PPA )
                publishedBinaryCounter = totalPublishedBinaries
                continue

            totalPublishedBinaries = publishedBinaries[ "total_size" ]
            if totalPublishedBinaries == 0:
                publishedBinaryCounter = totalPublishedBinaries
                continue

            numberPublishedBinariesCurrentPage = publishedBinariesPerPage
            if( pageNumber * publishedBinariesPerPage ) > totalPublishedBinaries:
                numberPublishedBinariesCurrentPage = totalPublishedBinaries - ( ( pageNumber - 1 ) * publishedBinariesPerPage )

            with concurrent.futures.ThreadPoolExecutor( max_workers = 1 if self.lowBandwidth else 3 ) as executor:
                {
                    executor.submit( self.getDownloadCount, ppa, publishedBinaries, i ):
                        i for i in range( numberPublishedBinariesCurrentPage )
                }

            publishedBinaryCounter += publishedBinariesPerPage
            pageNumber += 1


    def getDownloadCount( self, ppa, publishedBinaries, i ):
        if ppa.getStatus() == PPA.Status.NEEDS_DOWNLOAD: # Use the status to cancel downloads if an error occurred.
            try:
                indexLastSlash = publishedBinaries[ "entries" ][ i ][ "self_link" ].rfind( "/" )
                packageId = publishedBinaries[ "entries" ][ i ][ "self_link" ][ indexLastSlash + 1 : ]
                url = \
                    "https://api.launchpad.net/1.0/~" + \
                    ppa.getUser() + "/+archive/ubuntu/" + \
                    ppa.getName() + "/+binarypub/" + \
                    packageId + "?ws.op=getDownloadCount"

                downloadCount = json.loads( urlopen( url, timeout = IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ) )
                if str( downloadCount ).isnumeric():
                    packageName = publishedBinaries[ "entries" ][ i ][ "binary_package_name" ]
                    packageVersion = publishedBinaries[ "entries" ][ i ][ "binary_package_version" ]
                    architectureSpecific = publishedBinaries[ "entries" ][ i ][ "architecture_specific" ]
                    ppa.addPublishedBinary( PublishedBinary( packageName, packageVersion, downloadCount, architectureSpecific ) )

                else:
                    self.getLogging().error( "The download count at the URL was not numeric: " + url )
                    ppa.setStatus( PPA.Status.ERROR_RETRIEVING_PPA )

            except Exception as e:
                self.getLogging().error( "Problem with " + url )
                self.getLogging().exception( e )
                ppa.setStatus( PPA.Status.ERROR_RETRIEVING_PPA )


    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

        # PPAs.
        grid = self.createGrid()

        ppaStore = Gtk.ListStore( str, str, str, str ) # PPA user, name, series, architecture.
        for ppa in self.ppas:
            ppaStore.append( [ ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() ] )

        ppaTree = Gtk.TreeView.new_with_model( ppaStore )
        ppaTree.set_hexpand( True )
        ppaTree.set_vexpand( True )
        ppaTree.append_column( Gtk.TreeViewColumn( _( "PPA User" ), Gtk.CellRendererText(), text = 0 ) )
        ppaTree.append_column( Gtk.TreeViewColumn( _( "PPA Name" ), Gtk.CellRendererText(), text = 1 ) )
        ppaTree.append_column( Gtk.TreeViewColumn( _( "Series" ), Gtk.CellRendererText(), text = 2 ) )
        ppaTree.append_column( Gtk.TreeViewColumn( _( "Architecture" ), Gtk.CellRendererText(), text = 3 ) )
        ppaTree.set_tooltip_text( _( "Double click to edit a PPA." ) )
        ppaTree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        ppaTree.connect( "row-activated", self.onPPADoubleClick )
        for column in ppaTree.get_columns():
            column.set_expand( True )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( ppaTree )
        grid.attach( scrolledWindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )
        box.set_halign( Gtk.Align.CENTER )

        addButton = Gtk.Button.new_with_label( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new PPA." ) )
        addButton.connect( "clicked", self.onPPAAdd, ppaTree )
        box.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected PPA." ) )
        removeButton.connect( "clicked", self.onPPARemove, ppaTree )
        box.pack_start( removeButton, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "PPAs" ) ) )

        # Filters.
        grid = self.createGrid()

        filterStore = Gtk.ListStore( str, str, str, str, str ) # PPA user, name, series, architecture, filter text.
        for user, name, series, architecture in self.filters.getUserNameSeriesArchitecture():
            filterText = self.filters.getFilterText( user, name, series, architecture )
            filterStore.append( [ user, name, series, architecture, "\n".join( filterText ) ] )

        filterTree = Gtk.TreeView.new_with_model( filterStore )
        filterTree.set_hexpand( True )
        filterTree.set_vexpand( True )
        filterTree.append_column( Gtk.TreeViewColumn( _( "PPA User" ), Gtk.CellRendererText(), text = 0 ) )
        filterTree.append_column( Gtk.TreeViewColumn( _( "PPA Name" ), Gtk.CellRendererText(), text = 1 ) )
        filterTree.append_column( Gtk.TreeViewColumn( _( "Series" ), Gtk.CellRendererText(), text = 2 ) )
        filterTree.append_column( Gtk.TreeViewColumn( _( "Architecture" ), Gtk.CellRendererText(), text = 3 ) )
        filterTree.append_column( Gtk.TreeViewColumn( _( "Filter" ), Gtk.CellRendererText(), text = 4 ) )
        filterTree.set_tooltip_text( _( "Double click to edit a filter." ) )
        filterTree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        filterTree.connect( "row-activated", self.onFilterDoubleClick, ppaTree )
        for column in filterTree.get_columns():
            column.set_expand( True )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( filterTree )
        grid.attach( scrolledWindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )
        box.set_halign( Gtk.Align.CENTER )

        addButton = Gtk.Button.new_with_label( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new filter." ) )
        addButton.connect( "clicked", self.onFilterAdd, filterTree, ppaTree )
        box.pack_start( addButton, True, True, 0 )

        removeButton = Gtk.Button.new_with_label( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected filter." ) )
        removeButton.connect( "clicked", self.onFilterRemove, filterTree )
        box.pack_start( removeButton, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Filters" ) ) )

        # General settings.
        grid = self.createGrid()

        showAsSubmenusCheckbutton = Gtk.CheckButton.new_with_label( _( "Show PPAs as submenus" ) )
        showAsSubmenusCheckbutton.set_tooltip_text( _(
            "The download statistics for each PPA\n" + \
            "are shown in a separate submenu." ) )
        showAsSubmenusCheckbutton.set_active( self.showSubmenu )
        grid.attach( showAsSubmenusCheckbutton, 0, 0, 1, 1 )

        combinePPAsCheckbutton = Gtk.CheckButton.new_with_label( _( "Combine PPAs" ) )
        combinePPAsCheckbutton.set_tooltip_text( _(
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
        combinePPAsCheckbutton.set_active( self.combinePPAs )
        combinePPAsCheckbutton.set_margin_top( 10 )
        grid.attach( combinePPAsCheckbutton, 0, 1, 1, 1 )

        ignoreVersionArchitectureSpecificCheckbutton = Gtk.CheckButton.new_with_label( _( "Ignore version for architecture specific" ) )
        ignoreVersionArchitectureSpecificCheckbutton.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        ignoreVersionArchitectureSpecificCheckbutton.set_tooltip_text( _(
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
        ignoreVersionArchitectureSpecificCheckbutton.set_active( self.ignoreVersionArchitectureSpecific )
        ignoreVersionArchitectureSpecificCheckbutton.set_sensitive( combinePPAsCheckbutton.get_active() )
        grid.attach( ignoreVersionArchitectureSpecificCheckbutton, 0, 2, 1, 1 )

        combinePPAsCheckbutton.connect( "toggled", self.onRadioOrCheckbox, True, ignoreVersionArchitectureSpecificCheckbutton )

        sortByDownloadCheckbutton = Gtk.CheckButton.new_with_label( _( "Sort by download" ) )
        sortByDownloadCheckbutton.set_tooltip_text( _( "Sort by download count within each PPA." ) )
        sortByDownloadCheckbutton.set_active( self.sortByDownload )
        sortByDownloadCheckbutton.set_margin_top( 10 )
        grid.attach( sortByDownloadCheckbutton, 0, 3, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        label = Gtk.Label.new( _( "Clip amount" ) )
        label.set_sensitive( sortByDownloadCheckbutton.get_active() )
        label.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        box.pack_start( label, False, False, 0 )

        spinner = self.createSpinButton(
            self.sortByDownloadAmount,
            0,
            10000,
            1,
            100,
            _( "Limit the number of entries\n" + \
               "when sorting by download.\n\n" + \
               "A value of zero will not clip." ) )

        spinner.set_sensitive( sortByDownloadCheckbutton.get_active() )
        box.pack_start( spinner, False, False, 0 )

        grid.attach( box, 0, 4, 1, 1 )

        sortByDownloadCheckbutton.connect( "toggled", self.onRadioOrCheckbox, True, label, spinner )

        lowBandwidthCheckbutton = Gtk.CheckButton.new_with_label( _( "Low bandwidth" ) )
        lowBandwidthCheckbutton.set_tooltip_text( _( "Enable if your internet connection is slow." ) )
        lowBandwidthCheckbutton.set_active( self.lowBandwidth )
        lowBandwidthCheckbutton.set_margin_top( 10 )
        grid.attach( lowBandwidthCheckbutton, 0, 5, 1, 1 )

        autostartCheckbox, delaySpinner, box = self.createAutostartCheckboxAndDelaySpinner()
        grid.attach( box, 0, 6, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.showSubmenu = showAsSubmenusCheckbutton.get_active()
            self.combinePPAs = combinePPAsCheckbutton.get_active()
            self.ignoreVersionArchitectureSpecific = ignoreVersionArchitectureSpecificCheckbutton.get_active()
            self.lowBandwidth = lowBandwidthCheckbutton.get_active()
            self.sortByDownload = sortByDownloadCheckbutton.get_active()
            self.sortByDownloadAmount = spinner.get_value_as_int()

            self.ppas = [ ]
            treeiter = ppaStore.get_iter_first()
            while treeiter != None:
                self.ppas.append(
                    PPA(
                        ppaStore[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ],
                        ppaStore[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ],
                        ppaStore[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ],
                        ppaStore[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] ) )
                treeiter = ppaStore.iter_next( treeiter )

            PPA.sort( self.ppas )

            self.filters = Filters()
            treeiter = filterStore.get_iter_first()
            while treeiter != None:
                self.filters.addFilter(
                    filterStore[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ],
                    filterStore[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ],
                    filterStore[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ],
                    filterStore[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ],
                    filterStore[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ].split() )
                treeiter = filterStore.iter_next( treeiter )

            self.setAutostartAndDelay( autostartCheckbox.get_active(), delaySpinner.get_value_as_int() )
        return responseType


    def onPPARemove( self, button, tree ):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter is None:
            self.showMessage( tree, _( "No PPA has been selected for removal." ) )

        else:
            # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            if self.showOKCancel( tree, _( "Remove the selected PPA?" ) ) == Gtk.ResponseType.OK:
                model.remove( treeiter )


    def onPPAAdd( self, button, tree ):
        self.onPPADoubleClick( tree, None, None )


    def onPPADoubleClick( self, tree, rowNumber, treeViewColumn ):
        model, treeiter = tree.get_selection().get_selected()

        grid = self.createGrid()

        label = Gtk.Label.new( _( "PPA User" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        if len( model ) > 0:
            ppaUsers = [ ]
            for row in range( len( model ) ):
                if model[ row ][ IndicatorPPADownloadStatistics.COLUMN_USER ] not in ppaUsers:
                    ppaUsers.append( model[ row ][ IndicatorPPADownloadStatistics.COLUMN_USER ] )

            ppaUsers.sort( key = locale.strxfrm )

            ppaUser = Gtk.ComboBoxText.new_with_entry()
            for item in ppaUsers:
                ppaUser.append_text( item )

            if rowNumber:
                ppaUser.set_active( ppaUsers.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] ) ) # This is an edit.

        else:
            ppaUser = Gtk.Entry() # There are no PPAs present - adding the first PPA.

        ppaUser.set_hexpand( True ) # Only need to set this once and all objects will expand.

        grid.attach( ppaUser, 1, 0, 1, 1 )

        label = Gtk.Label.new( _( "PPA Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        if len( model ) > 0:
            ppaNames = [ ]
            for row in range( len( model ) ):
                if model[ row ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] not in ppaNames:
                    ppaNames.append( model[ row ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] )

            ppaNames.sort( key = locale.strxfrm )

            ppaName = Gtk.ComboBoxText.new_with_entry()
            for item in ppaNames:
                ppaName.append_text( item )

            if rowNumber:
                ppaName.set_active( ppaNames.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) ) # This is an edit.

        else:
            ppaName = Gtk.Entry() # There are no PPAs present - adding the first PPA.

        grid.attach( ppaName, 1, 1, 1, 1 )

        label = Gtk.Label.new( _( "Series" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        series = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.SERIES:
            series.append_text( item )

        if rowNumber:
            series.set_active( IndicatorPPADownloadStatistics.SERIES.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] ) )

        else:
            series.set_active( 0 )

        grid.attach( series, 1, 2, 1, 1 )

        label = Gtk.Label.new( _( "Architecture" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        architectures = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.ARCHITECTURES:
            architectures.append_text( item )

        if rowNumber:
            architectures.set_active( IndicatorPPADownloadStatistics.ARCHITECTURES.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] ) )

        else:
            architectures.set_active( 0 )

        grid.attach( architectures, 1, 3, 1, 1 )

        title = _( "Add PPA" )
        if rowNumber:
            title = _( "Edit PPA" )

        dialog = self.createDialog( tree, title, grid )
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
                    self.showMessage( dialog, _( "PPA user cannot be empty." )  )
                    ppaUser.grab_focus()
                    continue

                if ppaNameValue == "":
                    self.showMessage( dialog, _( "PPA name cannot be empty." ) )
                    ppaName.grab_focus()
                    continue

                # Ensure there is no duplicate...
                if ( rowNumber is None and len( model ) > 0 ) or ( rowNumber and len( model ) > 1 ):
                    # Doing an add and there's at least one PPA OR doing an edit and there's at least two PPAs...
                    if rowNumber is None: # Doing an add, so data has changed.
                        dataHasBeenChanged = True

                    else: # Doing an edit, so check to see if there the data has actually been changed...
                        dataHasBeenChanged = not ( \
                            ppaUserValue == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] and \
                            ppaNameValue == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] and \
                            series.get_active_text() == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] and \
                            architectures.get_active_text() == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] )

                    if dataHasBeenChanged:
                        duplicate = False
                        for row in range( len( model ) ):
                            if ppaUserValue == model[ row ][ IndicatorPPADownloadStatistics.COLUMN_USER ] and \
                               ppaNameValue == model[ row ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] and \
                               series.get_active_text() == model[ row ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] and \
                               architectures.get_active_text() == model[ row ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ]:

                                duplicate = True
                                break

                        if duplicate:
                            self.showMessage( dialog, _( "Duplicates disallowed - there is an identical PPA!" ) )
                            continue

                # Update the model...
                if rowNumber:
                    model.remove( treeiter ) # This is an edit...remove the old value and append new value.

                model.append( [ ppaUserValue, ppaNameValue, series.get_active_text(), architectures.get_active_text() ] )

            break

        dialog.destroy()


    def onFilterRemove( self, button, tree ):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter is None:
            self.showMessage( tree, _( "No filter has been selected for removal." ) )

        else:
            # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            if self.showOKCancel( tree, _( "Remove the selected filter?" ) ) == Gtk.ResponseType.OK:
                model.remove( treeiter )


    def onFilterAdd( self, button, filterTree, ppaTree ):
        if len( ppaTree.get_model() ) == 0:
            self.showMessage( filterTree, _( "Please add a PPA first!" ) )

        else:
            # If the number of filters equals the number of PPA User/Names, cannot add a filter!
            ppaUsersNames = [ ]
            for ppa in range( len( ppaTree.get_model() ) ):
                ppaUserName = \
                    ppaTree.get_model()[ ppa ][ IndicatorPPADownloadStatistics.COLUMN_USER ] + \
                    " | " + \
                    ppaTree.get_model()[ ppa ][ IndicatorPPADownloadStatistics.COLUMN_NAME ]

                if not ppaUserName in ppaUsersNames:
                    ppaUsersNames.append( ppaUserName )

            if len( filterTree.get_model() ) == len( ppaUsersNames ):
                self.showMessage( filterTree, _( "Only one filter per PPA User/Name." ), Gtk.MessageType.INFO )

            else:
                self.onFilterDoubleClick( filterTree, None, None, ppaTree )


    def onFilterDoubleClick( self, filterTree, rowNumber, treeViewColumnm, ppaTree ):
        filterTreeModel, filterTreeIter = filterTree.get_selection().get_selected()
        ppaTreeModel, ppaTreeIter = ppaTree.get_selection().get_selected()

        grid = self.createGrid()

        label = Gtk.Label.new( _( "PPA User/Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        ppaUsersNames = Gtk.ComboBoxText.new()
        if rowNumber is None: # Adding
            temp = [ ] # Used to ensure duplicates are not added.
            for ppa in range( len( ppaTreeModel ) ): # List of PPA User/Names from the list of PPAs in the preferences.
                ppaUserName = ppaTreeModel[ ppa ][ IndicatorPPADownloadStatistics.COLUMN_USER ] + " | " + ppaTreeModel[ ppa ][ IndicatorPPADownloadStatistics.COLUMN_NAME ]
                if ppaUserName in temp:
                    continue

                # Ensure the PPA User/Name is not present in the list of filters in the preferences.
                inFilterList = False
                for theFilter in range( len( filterTreeModel ) ):
                    if ppaUserName in filterTreeModel[ theFilter ][ IndicatorPPADownloadStatistics.COLUMN_USER ]:
                        inFilterList = True
                        break

                if not inFilterList:
                    ppaUsersNames.append_text( ppaUserName )
                    temp.append( ppaUserName )

        else:
            ppaUsersNames.append_text( filterTreeModel[ filterTreeIter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] )

        ppaUsersNames.set_hexpand( True )
        ppaUsersNames.set_active( 0 )

        grid.attach( ppaUsersNames, 1, 0, 1, 1 )

        label = Gtk.Label.new( _( "Filter Text" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 2, 1 )

        box = Gtk.Box( spacing = 0 )

        label = Gtk.Label.new( "\n\n\n\n\n" ) # Padding to ensure the textview for the message text is not too small.
        label.set_valign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

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

        if rowNumber:
            textview.get_buffer().set_text( filterTreeModel[ filterTreeIter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) # This is an edit.

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( textview )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        box.pack_start( scrolledWindow, True, True, 0 )

        grid.attach( box, 0, 3, 2, 1 )

        title = _( "Edit Filter" )
        if rowNumber is None:
            title = _( "Add Filter" )

        dialog = self.createDialog( filterTree, title, grid )
        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                buffer = textview.get_buffer()
                filterText = buffer.get_text( buffer.get_start_iter(), buffer.get_end_iter(), False )
                filterText = "\n".join( filterText.split() )
                if len( filterText ) == 0:
                    self.showMessage( dialog, _( "Please enter filter text!" ) )
                    continue

                # Update the model...
                if rowNumber:
                    filterTreeModel.remove( filterTreeIter ) # This is an edit...remove the old value and append new value.

                filterTreeModel.append( [ ppaUsersNames.get_active_text(), filterText ] )

            break

        dialog.destroy()


    def loadConfig( self, config ):
        self.combinePPAs = config.get( IndicatorPPADownloadStatistics.CONFIG_COMBINE_PPAS, False )
        self.ignoreVersionArchitectureSpecific = config.get( IndicatorPPADownloadStatistics.CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC, True )
        self.lowBandwidth = config.get( IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH, False )
        self.showSubmenu = config.get( IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU, False )
        self.sortByDownload = config.get( IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD, False )
        self.sortByDownloadAmount = config.get( IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT, 5 )

        if config:
            self.ppas = [ ]
            ppas = config.get( IndicatorPPADownloadStatistics.CONFIG_PPAS, [ ] )
            for ppa in ppas:
                user = ppa[ IndicatorPPADownloadStatistics.COLUMN_USER ]
                name = ppa[ IndicatorPPADownloadStatistics.COLUMN_NAME ]
                series = ppa[ IndicatorPPADownloadStatistics.COLUMN_SERIES ]
                architecture = ppa[ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ]
                self.ppas.append( PPA( user, name, series, architecture ) )

            PPA.sort( self.ppas )

            self.filters = Filters()
            filters = config.get( IndicatorPPADownloadStatistics.CONFIG_FILTERS, [ ] )
            for theFilter in filters:
                user = theFilter[ IndicatorPPADownloadStatistics.COLUMN_USER ]
                name = theFilter[ IndicatorPPADownloadStatistics.COLUMN_NAME ]
                series = theFilter[ IndicatorPPADownloadStatistics.COLUMN_SERIES ]
                architecture = theFilter[ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ]
                filterText = theFilter[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ]
                self.filters.addFilter( user, name, series, architecture, filterText )

        else:
            self.ppas = [ ]
            self.ppas.append( PPA( "thebernmeister", "ppa", "jammy", "amd64" ) )

            filterText = [
                "indicator-fortune",
                "indicator-lunar",
                "indicator-on-this-day",
                "indicator-ppa-download-statistics",
                "indicator-punycode",
                "indicator-script-runner",
                "indicator-stardate",
                "indicator-tide",
                "indicator-virtual-box" ]

            self.filters = Filters()
            self.filters.addFilter( "thebernmeister", "ppa", "jammy", "amd64", filterText )
            self.requestSaveConfig()


    def saveConfig( self ):
        ppas = [ ]
        for ppa in self.ppas:
            ppas.append( [ ppa.getUser(), ppa.getName(), ppa.getSeries(), ppa.getArchitecture() ] )

        filters = [ ]
        for user, name, series, architecture in self.filters.getUserNameSeriesArchitecture():
            filterText = self.filters.getFilterText( user, name, series, architecture )
            filters.append( [ user, name, series, architecture, filterText ] )

        return {
            IndicatorPPADownloadStatistics.CONFIG_COMBINE_PPAS : self.combinePPAs,
            IndicatorPPADownloadStatistics.CONFIG_FILTERS : filters,
            IndicatorPPADownloadStatistics.CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC : self.ignoreVersionArchitectureSpecific,
            IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH : self.lowBandwidth,
            IndicatorPPADownloadStatistics.CONFIG_PPAS : ppas,
            IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU : self.showSubmenu,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD : self.sortByDownload,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT : self.sortByDownloadAmount
        }


IndicatorPPADownloadStatistics().main()
