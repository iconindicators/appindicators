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


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

from copy import deepcopy
import concurrent.futures
import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

import json
import locale
from urllib.request import urlopen
import webbrowser

from ppa import Filters, PPA, PublishedBinary


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
        "oracular",
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
            comments = _( "Displays the total downloads of PPAs." ) )


    def update( self, menu ):
        self.download_ppa_statistics()
        self.build_menu( menu )
        return 6 * 60 * 60 # Update every six hours.


    def build_menu( self, menu ):
        ppas = deepcopy( self.ppas ) # Take a copy as the combine mechanism can alter the PPA series/architecture.

        if self.combine_ppas:
            ppas = self.combine( ppas )

        if self.sort_by_download:
            for ppa in ppas:
                ppa.sort_published_binaries_by_download_count_and_clip( self.sort_by_download_amount )

        if self.show_submenu:
            indent = self.get_menu_indent()
            for ppa in ppas:
                menuitem = self.create_and_append_menuitem( menu, ppa.get_descriptor() )

                submenu = Gtk.Menu()
                if ppa.get_status() == PPA.Status.OK:
                    published_binaries = ppa.get_published_binaries( True )
                    for published_binary in published_binaries:
                        self.create_menuitem_for_published_binary( submenu, indent, ppa, published_binary )
                        menuitem.set_submenu( submenu )

                else:
                    self.create_menuitem_for_status_message( submenu, indent, ppa )
                    menuitem.set_submenu( submenu )

        else:
            indent = self.get_menu_indent()
            for ppa in ppas:
                self.create_and_append_menuitem(
                    menu,
                    ppa.get_descriptor(),
                    name = ppa.get_descriptor(),
                    activate_functionandarguments = ( self.on_ppa, ) )

                if ppa.get_status() == PPA.Status.OK:
                    published_binaries = ppa.get_published_binaries( True )
                    for published_binary in published_binaries:
                        self.create_menuitem_for_published_binary( menu, indent, ppa, published_binary )

                else:
                    self.create_menuitem_for_status_message( menu, indent, ppa )

            # When only one PPA is present, enable a middle mouse click
            # on the icon to open the PPA in the browser.
            if len( ppas ) == 1:
                self.set_secondary_activate_target( menu.get_children()[ 0 ] )


    def create_menuitem_for_published_binary( self, menu, indent, ppa, published_binary ):
        label = indent + published_binary.get_package_name()
        if published_binary.get_package_version() is None:
            label += ":  " + str( published_binary.get_download_count() )

        else:
            label += \
                " " + published_binary.get_package_version() + ":  " + \
                str( published_binary.get_download_count() )

        self.create_and_append_menuitem(
            menu,
            label,
            name = ppa.get_descriptor(),
            activate_functionandarguments = ( self.on_ppa, ) )


    def create_menuitem_for_status_message( self, menu, indent, ppa ):
        if ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA:
            message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_RETRIEVING_PPA

        elif ppa.get_status() == PPA.Status.NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED:
            message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED

        elif ppa.get_status() == PPA.Status.NO_PUBLISHED_BINARIES:
            message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES

        elif ppa.get_status() == PPA.Status.PUBLISHED_BINARIES_COMPLETELY_FILTERED:
            message = IndicatorPPADownloadStatistics.MESSAGE_PUBLISHED_BINARIES_COMPLETELY_FILTERED

        self.create_and_append_menuitem( menu, indent + message )


    def combine( self, ppas ):
        # Match up identical PPAs: two PPAs are deemed to match if their 'PPA User | PPA Name' are identical.
        combined_ppas = { }
        for ppa in ppas:
            key = ppa.get_user() + " | " + ppa.get_name()
            if key in combined_ppas:
                if ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA or combined_ppas[ key ].get_status() == PPA.Status.ERROR_RETRIEVING_PPA:
                    combined_ppas[ key ].set_status( PPA.Status.ERROR_RETRIEVING_PPA )

                elif ppa.get_status() == PPA.Status.OK or combined_ppas[ key ].get_status() == PPA.Status.OK:
                    combined_ppas[ key ].add_published_binaries( ppa.get_published_binaries() )
                    combined_ppas[ key ].set_status( PPA.Status.OK )

                elif ppa.get_status() == combined_ppas[ key ].get_status(): # Both are filtered or both have no published binaries.
                    pass # Nothing to do.

                else: # One is completely filtered and the other has no published binaries.
                    combined_ppas[ key ].set_status( PPA.Status.NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED )

            else: # No previous match for this PPA.
                combined_ppas[ key ] = ppa

        # The combined PPAs either have:
        #    A status of error, or completely filtered, or no published binaries or,
        #    a status of OK with a concatenation of all published binaries from PPAs with the same PPA user/name.
        ppas = [ ]
        for ppa in combined_ppas.values():
            if ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA or \
               ppa.get_status() == PPA.Status.NO_PUBLISHED_BINARIES or \
               ppa.get_status() == PPA.Status.NO_PUBLISHED_BINARIES_AND_OR_COMPLETELY_FILTERED or \
               ppa.get_status() == PPA.Status.PUBLISHED_BINARIES_COMPLETELY_FILTERED:

                ppas.append( PPA( ppa.get_user(), ppa.get_name(), None, None ) )
                ppas[ -1 ].set_status( ppa.get_status() )

            else:
                temp = { }
                for published_binary in ppa.get_published_binaries():
                    key = published_binary.get_package_name() + " | " + published_binary.get_package_version()
                    if published_binary.is_architecture_specific():
                        if self.ignore_version_architecture_specific:
                            key = published_binary.get_package_name() # Key only contains name.

                        # Add up the download count from each published binary of the same key (package name OR package name and package version).
                        if key in temp:
                            new_published_binary = \
                                PublishedBinary(
                                    temp[ key ].get_package_name(),
                                    temp[ key ].get_package_version(),
                                    temp[ key ].get_download_count() + published_binary.get_download_count(),
                                    temp[ key ].is_architecture_specific )

                            temp[ key ] = new_published_binary

                        else:
                            temp[ key ] = published_binary
                            if self.ignore_version_architecture_specific:
                                new_published_binary = \
                                    PublishedBinary(
                                        temp[ key ].get_package_name(),
                                        None,
                                        temp[ key ].get_download_count(),
                                        temp[ key ].is_architecture_specific )

                                temp[ key ] = new_published_binary

                    else:
                        if key not in temp:
                            temp[ key ] = published_binary

                ppas.append( PPA( ppa.get_user(), ppa.get_name(), None, None ) )
                ppas[ -1 ].set_status( PPA.Status.OK )
                for key in temp:
                    ppas[ -1 ].add_published_binary( temp[ key ] )

        PPA.sort( self.ppas )
        return ppas


    def on_ppa( self, menuitem ):
        url = "https://launchpad.net/~"
        first_pipe = str.find( menuitem.get_name(), "|" )
        ppa_user = menuitem.get_name()[ 0 : first_pipe ].strip()
        second_pipe = str.find( menuitem.get_name(), "|", first_pipe + 1 )
        if second_pipe == -1:
            # This is a combined PPA...
            ppa_name = menuitem.get_name()[ first_pipe + 1 : ].strip()
            url += ppa_user + "/+archive/ubuntu/" + ppa_name
            if menuitem.get_name() != menuitem.get_label(): # Use the menu item label to specify the package name.
                url += "/+packages?field.name_filter=" + menuitem.get_label().split()[ 0 ] + "&field.status_filter=published&field.series_filter="

        else:
            ppa_name = menuitem.get_name()[ first_pipe + 1 : second_pipe ].strip()
            third_pipe = str.find( menuitem.get_name(), "|", second_pipe + 1 )
            series = menuitem.get_name()[ second_pipe + 1 : third_pipe ].strip()
            url += ppa_user + "/+archive/ubuntu/" + ppa_name
            if menuitem.get_name() == menuitem.get_label():
                url += "?field.series_filter=" + series

            else: # Use the menu item label to specify the package name.
                url += "/+packages?field.name_filter=" + menuitem.get_label().split()[ 0 ] + "&field.status_filter=published&field.series_filter=" + series

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
    def download_ppa_statistics( self ):
        for ppa in self.ppas:
            ppa.set_status( PPA.Status.NEEDS_DOWNLOAD )
            if self.filters.has_filter( ppa.get_user(), ppa.get_name(), ppa.get_series(), ppa.get_architecture() ):
                has_published_binaries = self.has_published_binaries( ppa )
                if has_published_binaries is None:
                    ppa.set_status( PPA.Status.ERROR_RETRIEVING_PPA )

                elif has_published_binaries:
                    for the_filter in self.filters.get_filter_text( ppa.get_user(), ppa.get_name(), ppa.get_series(), ppa.get_architecture() ):
                        self.get_published_binaries( ppa, the_filter )
                        if ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA:
                            break # No point continuing with each filter.

                    if not( ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA ):
                        if ppa.get_published_binaries():
                            ppa.set_status( PPA.Status.OK )

                        else:
                            ppa.set_status( PPA.Status.PUBLISHED_BINARIES_COMPLETELY_FILTERED )

                else:
                    ppa.set_status( PPA.Status.NO_PUBLISHED_BINARIES )

            else:
                self.get_published_binaries( ppa, "" )
                if not ( ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA ):
                    if ppa.get_published_binaries():
                        ppa.set_status( PPA.Status.OK )

                    else:
                        ppa.set_status( PPA.Status.NO_PUBLISHED_BINARIES )


    def has_published_binaries( self, ppa ):
        url = \
            "https://api.launchpad.net/1.0/~" + \
            ppa.get_user() + "/+archive/ubuntu/" + \
            ppa.get_name() + "?ws.op=getPublishedBinaries" + \
            "&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + ppa.get_series() + "/" + \
            ppa.get_architecture() + "&status=Published" + \
            "&exact_match=false&ordered=false"

        try:
            published_binaries = \
                json.loads(
                    urlopen(
                        url,
                        timeout = IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ) )

            has_publised_binaries = published_binaries[ "total_size" ] > 0

        except Exception as e:
            has_publised_binaries = None
            self.get_logging().error( "Problem with " + url )
            self.get_logging().exception( e )

        return has_publised_binaries


    # Use a thread pool executer to get the download counts for each published binary.
    # References:
    #    https://docs.python.org/3/library/concurrent.futures.html
    #    https://pymotw.com/3/concurrent.futures
    #    http://www.dalkescientific.com/writings/diary/archive/2012/01/19/concurrent.futures.html
    def get_published_binaries( self, ppa, filter_text ):
        url = \
            "https://api.launchpad.net/1.0/~" + \
            ppa.get_user() + "/+archive/ubuntu/" + \
            ppa.get_name() + "?ws.op=getPublishedBinaries" + \
            "&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" + ppa.get_series() + "/" + \
            ppa.get_architecture() + "&status=Published" + \
            "&exact_match=false&ordered=false&binary_name=" + filter_text # A filterText of "" equates to no filterText.

        page_number = 1
        published_binaries_per_page = 75 # Results are presented in at most 75 per page.
        published_binary_counter = 0
        total_published_binaries = published_binary_counter + 1 # Set to a value greater than published_binary_counter to ensure the loop executes at least once.
        while( published_binary_counter < total_published_binaries and ppa.get_status() == PPA.Status.NEEDS_DOWNLOAD ): # Keep going if there are more downloads and no error has occurred.
            try:
                current_url =  url + "&ws.start=" + str( published_binary_counter )
                published_binaries = \
                    json.loads(
                        urlopen(
                            current_url,
                            timeout = IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ) )

            except Exception as e:
                self.get_logging().error( "Problem with " + current_url )
                self.get_logging().exception( e )
                ppa.set_status( PPA.Status.ERROR_RETRIEVING_PPA )
                published_binary_counter = total_published_binaries
                continue

            total_published_binaries = published_binaries[ "total_size" ]
            if total_published_binaries == 0:
                published_binary_counter = total_published_binaries
                continue

            number_published_binaries_current_page = published_binaries_per_page
            if( page_number * published_binaries_per_page ) > total_published_binaries:
                number_published_binaries_current_page = \
                    total_published_binaries - ( ( page_number - 1 ) * published_binaries_per_page )

            max_workers = 1 if self.low_bandwidth else 3
            with concurrent.futures.ThreadPoolExecutor( max_workers = max_workers ) as executor:
                {
                    executor.submit( self.get_download_count, ppa, published_binaries, i ):
                        i for i in range( number_published_binaries_current_page )
                }

            published_binary_counter += published_binaries_per_page
            page_number += 1


    def get_download_count( self, ppa, published_binaries, i ):
        if ppa.get_status() == PPA.Status.NEEDS_DOWNLOAD: # Use the status to cancel downloads if an error occurred.
            try:
                index_last_slash = published_binaries[ "entries" ][ i ][ "self_link" ].rfind( "/" )
                package_id = published_binaries[ "entries" ][ i ][ "self_link" ][ index_last_slash + 1 : ]
                url = \
                    "https://api.launchpad.net/1.0/~" + \
                    ppa.get_user() + "/+archive/ubuntu/" + \
                    ppa.get_name() + "/+binarypub/" + \
                    package_id + "?ws.op=getDownloadCount"

                download_count = \
                    json.loads(
                        urlopen(
                            url,
                            timeout = IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ) )

                if str( download_count ).isnumeric():
                    package_name = published_binaries[ "entries" ][ i ][ "binary_package_name" ]
                    package_version = published_binaries[ "entries" ][ i ][ "binary_package_version" ]
                    architecture_specific = published_binaries[ "entries" ][ i ][ "architecture_specific" ]
                    ppa.add_published_binary(
                        PublishedBinary(
                            package_name,
                            package_version,
                            download_count,
                            architecture_specific ) )

                else:
                    self.get_logging().error( "The download count at the URL was not numeric: " + url )
                    ppa.set_status( PPA.Status.ERROR_RETRIEVING_PPA )

            except Exception as e:
                self.get_logging().error( "Problem with " + url )
                self.get_logging().exception( e )
                ppa.set_status( PPA.Status.ERROR_RETRIEVING_PPA )


    def on_preferences( self, dialog ):
        notebook = Gtk.Notebook()

        # PPAs.
        grid = self.create_grid()

        ppa_store = Gtk.ListStore( str, str, str, str ) # PPA user, name, series, architecture.
        for ppa in self.ppas:
            ppa_store.append( [ ppa.get_user(), ppa.get_name(), ppa.get_series(), ppa.get_architecture() ] )

        ppa_treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                ppa_store,
                (
                    _( "PPA User" ),
                    _( "PPA Name" ),
                    _( "Series" ),
                    _( "Architecture" ) ),
                (
                    ( Gtk.CellRendererText(), "text", 0 ),
                    ( Gtk.CellRendererText(), "text", 1 ),
                    ( Gtk.CellRendererText(), "text", 2 ),
                    ( Gtk.CellRendererText(), "text", 3 ) ),
                tooltip_text = _( "Double click to edit a PPA." ),
                rowactivatedfunctionandarguments = ( self.on_ppa_double_click, ) )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )  #TODO Why need this?
        box.set_halign( Gtk.Align.CENTER )

        box.pack_start(
            self.create_button(
                _( "Add" ),
                tooltip_text = _( "Add a new PPA." ),
                clicked_functionandarguments = ( self.on_ppa_add, ppa_treeview ) ),
            True,
            True,
            0 )

        box.pack_start(
            self.create_button(
                _( "Remove" ),
                tooltip_text = _( "Remove the selected PPA." ),
                clicked_functionandarguments = ( self.on_ppa_remove, ppa_treeview ) ),
            True,
            True,
            0 )

        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "PPAs" ) ) )

        # Filters.
        grid = self.create_grid()

        filter_store = Gtk.ListStore( str, str, str, str, str ) # PPA user, name, series, architecture, filter text.
        for user, name, series, architecture in self.filters.get_user_name_series_architecture():
            filter_text = \
                self.filters.get_filter_text(
                    user,
                    name,
                    series,
                    architecture )

            filter_store.append(
                [
                    user,
                    name,
                    series,
                    architecture,
                    "\n".join( filter_text ) ] )

        filter_treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                filter_store,
                (
                    _( "PPA User" ),
                    _( "PPA Name" ),
                    _( "Series" ),
                    _( "Architecture" ),
                    _( "Filter" ) ),
                (
                    ( Gtk.CellRendererText(), "text", 0 ),
                    ( Gtk.CellRendererText(), "text", 1 ),
                    ( Gtk.CellRendererText(), "text", 2 ),
                    ( Gtk.CellRendererText(), "text", 3 ),
                    ( Gtk.CellRendererText(), "text", 4 ) ),
                tooltip_text = _( "Double click to edit a filter." ),
                rowactivatedfunctionandarguments = ( self.on_filter_double_click, ppa_treeview ) )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )  #TODO Why have this?
        box.set_halign( Gtk.Align.CENTER )

        box.pack_start(
            self.create_button(
                _( "Add" ),
                tooltip_text = _( "Add a new filter." ),
                clicked_functionandarguments = ( self.on_filter_add, filter_treeview, ppa_treeview ) ),
            True,
            True,
            0 )

        box.pack_start(
            self.create_button(
                _( "Remove" ),
                tooltip_text = _( "Remove the selected filter." ),
                clicked_functionandarguments = ( self.on_filter_remove, filter_treeview ) ),
            True,
            True,
            0 )

        grid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Filters" ) ) )

        # General settings.
        grid = self.create_grid()

        show_as_submenus_checkbutton = \
            self.create_checkbutton(
                _( "Show PPAs as submenus" ),
                tooltip_text = _(
                    "The download statistics for each PPA\n" + \
                    "are shown in a separate submenu." ),
                active = self.show_submenu )

        grid.attach( show_as_submenus_checkbutton, 0, 0, 1, 1 )

        combine_ppas_checkbutton = \
            self.create_checkbutton(
                _( "Combine PPAs" ),
                tooltip_text = _(
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
                    "this category." ),
                margin_top = 10,
                active = self.combine_ppas )

        grid.attach( combine_ppas_checkbutton, 0, 1, 1, 1 )

        ignore_version_architecture_specific_checkbutton = \
            self.create_checkbutton(
                _( "Ignore version for architecture specific" ),
                tooltip_text = _(
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
                    "instances of a published binary." ),
                sensitive = combine_ppas_checkbutton.get_active(),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.ignore_version_architecture_specific )

        grid.attach( ignore_version_architecture_specific_checkbutton, 0, 2, 1, 1 )

#TODO Can or should this be moved up or down?
        combine_ppas_checkbutton.connect(
            "toggled",
            self.on_radio_or_checkbox,
            True,
            ignore_version_architecture_specific_checkbutton )

        sort_by_download_checkbutton = \
            self.create_checkbutton(
                _( "Sort by download" ),
                tooltip_text = _( "Sort by download count within each PPA." ),
                margin_top = 10,
                active = self.sort_by_download )

        grid.attach( sort_by_download_checkbutton, 0, 3, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        label = Gtk.Label.new( _( "Clip amount" ) )
        label.set_sensitive( sort_by_download_checkbutton.get_active() )
        label.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )
        box.pack_start( label, False, False, 0 )

        spinner = \
            self.create_spinbutton(
                self.sort_by_download_amount,
                0,
                10000,
                page_increment = 100,
                tooltip_text = _(
                    "Limit the number of entries\n" + \
                    "when sorting by download.\n\n" + \
                    "A value of zero will not clip." ),
                sensitive = sort_by_download_checkbutton.get_active() )

        box.pack_start( spinner, False, False, 0 )

        grid.attach( box, 0, 4, 1, 1 )

#TODO Can/should this be moved up/down?
        sort_by_download_checkbutton.connect(
            "toggled",
            self.on_radio_or_checkbox,
            True,
            label,
            spinner )

        low_bandwidth_checkbutton = \
            self.create_checkbutton(
                _( "Low bandwidth" ),
                tooltip_text = _( "Enable if your internet connection is slow." ),
                margin_top = 10,
                active = self.low_bandwidth )

        grid.attach( low_bandwidth_checkbutton, 0, 5, 1, 1 )

        autostart_checkbox, delay_spinner, box = self.create_autostart_checkbox_and_delay_spinner()
        grid.attach( box, 0, 6, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.show_submenu = show_as_submenus_checkbutton.get_active()
            self.combine_ppas = combine_ppas_checkbutton.get_active()
            self.ignore_version_architecture_specific = ignore_version_architecture_specific_checkbutton.get_active()
            self.low_bandwidth = low_bandwidth_checkbutton.get_active()
            self.sort_by_download = sort_by_download_checkbutton.get_active()
            self.sort_by_download_amount = spinner.get_value_as_int()

            self.ppas = [ ]
            treeiter = ppa_store.get_iter_first()
            while treeiter != None:
                self.ppas.append(
                    PPA(
                        ppa_store[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ],
                        ppa_store[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ],
                        ppa_store[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ],
                        ppa_store[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] ) )

                treeiter = ppa_store.iter_next( treeiter )

            PPA.sort( self.ppas )

            self.filters = Filters()
            treeiter = filter_store.get_iter_first()
            while treeiter != None:
                self.filters.add_filter(
                    filter_store[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ],
                    filter_store[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ],
                    filter_store[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ],
                    filter_store[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ],
                    filter_store[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ].split() )

                treeiter = filter_store.iter_next( treeiter )

            self.set_autostart_and_delay( autostart_checkbox.get_active(), delay_spinner.get_value_as_int() )

        return response_type


    def on_ppa_remove( self, button, treeview ):
        model, treeiter = treeview.get_selection().get_selected()
        if treeiter is None:
            self.show_dialog_ok( treeview, _( "No PPA has been selected for removal." ) )

        else:
            # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            if self.show_dialog_ok_cancel( treeview, _( "Remove the selected PPA?" ) ) == Gtk.ResponseType.OK:
                model.remove( treeiter )


    def on_ppa_add( self, button, treeview ):
        self.on_ppa_double_click( treeview, None, None )


    def on_ppa_double_click( self, treeview, row_number, treeViewColumn ):
        model, treeiter = treeview.get_selection().get_selected()

        grid = self.create_grid()

        label = Gtk.Label.new( _( "PPA User" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        if len( model ) > 0:
            ppa_users = [ ]
            for row in range( len( model ) ):
                if model[ row ][ IndicatorPPADownloadStatistics.COLUMN_USER ] not in ppa_users:
                    ppa_users.append( model[ row ][ IndicatorPPADownloadStatistics.COLUMN_USER ] )

            ppa_users.sort( key = locale.strxfrm )

            ppa_user = Gtk.ComboBoxText.new_with_entry()
            for item in ppa_users:
                ppa_user.append_text( item )

            if row_number:
                ppa_user.set_active( ppa_users.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] ) ) # This is an edit.

        else:
            ppa_user = Gtk.Entry() # There are no PPAs present - adding the first PPA.

        ppa_user.set_hexpand( True ) # Only need to set this once and all objects will expand.

        grid.attach( ppa_user, 1, 0, 1, 1 )

        label = Gtk.Label.new( _( "PPA Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        if len( model ) > 0:
            ppa_names = [ ]
            for row in range( len( model ) ):
                if model[ row ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] not in ppa_names:
                    ppa_names.append( model[ row ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] )

            ppa_names.sort( key = locale.strxfrm )

            ppa_name = Gtk.ComboBoxText.new_with_entry()
            for item in ppa_names:
                ppa_name.append_text( item )

            if row_number:
                ppa_name.set_active( ppa_names.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) ) # This is an edit.

        else:
            ppaName = Gtk.Entry() # There are no PPAs present - adding the first PPA.

        grid.attach( ppaName, 1, 1, 1, 1 )

        label = Gtk.Label.new( _( "Series" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        series = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.SERIES:
            series.append_text( item )

        if row_number:
            series.set_active(
                IndicatorPPADownloadStatistics.SERIES.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] ) )

        else:
            series.set_active( 0 )

        grid.attach( series, 1, 2, 1, 1 )

        label = Gtk.Label.new( _( "Architecture" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        architectures = Gtk.ComboBoxText()
        for item in IndicatorPPADownloadStatistics.ARCHITECTURES:
            architectures.append_text( item )

        if row_number:
            architectures.set_active(
                IndicatorPPADownloadStatistics.ARCHITECTURES.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] ) )

        else:
            architectures.set_active( 0 )

        grid.attach( architectures, 1, 3, 1, 1 )

        title = _( "Add PPA" )
        if row_number:
            title = _( "Edit PPA" )

        dialog = self.createDialog( treeview, title, grid )
        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if len( model ) > 0:
                    ppa_user_value = ppa_user.get_active_text().strip()
                    ppa_name_value = ppaName.get_active_text().strip()

                else:
                    ppa_user_value = ppa_user.get_text().strip()
                    ppa_name_value = ppaName.get_text().strip()

                if ppa_user_value == "":
                    self.show_dialog_ok( dialog, _( "PPA user cannot be empty." )  )
                    ppa_user.grab_focus()
                    continue

                if ppa_name_value == "":
                    self.show_dialog_ok( dialog, _( "PPA name cannot be empty." ) )
                    ppaName.grab_focus()
                    continue

                # Ensure there is no duplicate...
                if ( row_number is None and len( model ) > 0 ) or ( row_number and len( model ) > 1 ):
                    # Doing an add and there's at least one PPA OR doing an edit and there's at least two PPAs...
                    if row_number is None: # Doing an add, so data has changed.
                        data_has_been_changed = True

                    else: # Doing an edit, so check to see if there the data has actually been changed...
                        data_has_been_changed = not ( \
                            ppa_user_value == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] and \
                            ppa_name_value == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] and \
                            series.get_active_text() == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] and \
                            architectures.get_active_text() == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] )

                    if data_has_been_changed:
                        duplicate = False
                        for row in range( len( model ) ):
                            if ppa_user_value == model[ row ][ IndicatorPPADownloadStatistics.COLUMN_USER ] and \
                               ppa_name_value == model[ row ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] and \
                               series.get_active_text() == model[ row ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] and \
                               architectures.get_active_text() == model[ row ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ]:

                                duplicate = True
                                break

                        if duplicate:
                            self.show_dialog_ok( dialog, _( "Duplicates disallowed - there is an identical PPA!" ) )
                            continue

                # Update the model...
                if row_number:
                    model.remove( treeiter ) # This is an edit...remove the old value and append new value.

                model.append( [
                    ppa_user_value,
                    ppa_name_value,
                    series.get_active_text(),
                    architectures.get_active_text() ] )

            break

        dialog.destroy()


    def on_filter_remove( self, button, treeview ):
        model, treeiter = treeview.get_selection().get_selected()
        if treeiter is None:
            self.show_dialog_ok( treeview, _( "No filter has been selected for removal." ) )

        else:
            # Prompt the user to remove - only one row can be selected since single selection mode has been set.
            if self.show_dialog_ok_cancel( treeview, _( "Remove the selected filter?" ) ) == Gtk.ResponseType.OK:
                model.remove( treeiter )


    def on_filter_add( self, button, filter_treeview, ppa_treeview ):
        if len( ppa_treeview.get_model() ) == 0:
            self.show_dialog_ok( filter_treeview, _( "Please add a PPA first!" ) )

        else:
            # If the number of filters equals the number of PPA User/Names, cannot add a filter!
            ppa_users_names = [ ]
            for ppa in range( len( ppa_treeview.get_model() ) ):
                ppa_user_name = \
                    ppa_treeview.get_model()[ ppa ][ IndicatorPPADownloadStatistics.COLUMN_USER ] + \
                    " | " + \
                    ppa_treeview.get_model()[ ppa ][ IndicatorPPADownloadStatistics.COLUMN_NAME ]

                if not ppa_user_name in ppa_users_names:
                    ppa_users_names.append( ppa_user_name )

            if len( filter_treeview.get_model() ) == len( ppa_users_names ):
                self.show_dialog_ok( filter_treeview, _( "Only one filter per PPA User/Name." ), Gtk.MessageType.INFO )

            else:
                self.on_filter_double_click( filter_treeview, None, None, ppa_treeview )


    def on_filter_double_click( self, filter_treeview, row_number, treeviewcolumnm, ppa_treeview ):
        filter_model, filter_treeiter = filter_treeview.get_selection().get_selected()
        ppa_model, ppa_treeiter = ppa_treeview.get_selection().get_selected()

        grid = self.create_grid()

        label = Gtk.Label.new( _( "PPA User/Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        ppa_users_names = Gtk.ComboBoxText.new()
        if row_number is None: # Adding
            temp = [ ] # Used to ensure duplicates are not added.
            for ppa in range( len( ppa_model ) ): # List of PPA User/Names from the list of PPAs in the preferences.
                ppa_user_name = \
                    ppa_model[ ppa ][ IndicatorPPADownloadStatistics.COLUMN_USER ] + " | " + \
                    ppa_model[ ppa ][ IndicatorPPADownloadStatistics.COLUMN_NAME ]

                if ppa_user_name in temp:
                    continue

                # Ensure the PPA User/Name is not present in the list of filters in the preferences.
                inFilterList = False
                for theFilter in range( len( filter_model ) ):
                    if ppa_user_name in filter_model[ theFilter ][ IndicatorPPADownloadStatistics.COLUMN_USER ]:
                        inFilterList = True
                        break

                if not inFilterList:
                    ppa_users_names.append_text( ppa_user_name )
                    temp.append( ppa_user_name )

        else:
            ppa_users_names.append_text(
                filter_model[ filter_treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] )

        ppa_users_names.set_hexpand( True )
        ppa_users_names.set_active( 0 )

        grid.attach( ppa_users_names, 1, 0, 1, 1 )

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

        if row_number:
            textview.get_buffer().set_text(
                filter_model[ filter_treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) # This is an edit.

        box.pack_start( self.create_scrolledwindow( textview ), True, True, 0 )

        grid.attach( box, 0, 3, 2, 1 )

        title = _( "Edit Filter" )
        if row_number is None:
            title = _( "Add Filter" )

        dialog = self.create_dialog( filter_treeview, title, grid )
        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                buffer = textview.get_buffer()
                filter_text = buffer.get_text( buffer.get_start_iter(), buffer.get_end_iter(), False )
                filter_text = "\n".join( filter_text.split() )
                if len( filter_text ) == 0:
                    self.show_dialog_ok( dialog, _( "Please enter filter text!" ) )
                    continue

                # Update the model...
                if row_number:
                    filter_model.remove( filter_treeiter ) # This is an edit...remove the old value and append new value.

                filter_model.append( [
                    ppa_users_names.get_active_text(),
                    filter_text ] )

            break

        dialog.destroy()


    def load_config( self, config ):
        self.combine_ppas = config.get( IndicatorPPADownloadStatistics.CONFIG_COMBINE_PPAS, False )
        self.ignore_version_architecture_specific = config.get( IndicatorPPADownloadStatistics.CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC, True )
        self.low_bandwidth = config.get( IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH, False )
        self.show_submenu = config.get( IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU, False )
        self.sort_by_download = config.get( IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD, False )
        self.sort_by_download_amount = config.get( IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT, 5 )

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
            for the_filter in filters:
                user = the_filter[ IndicatorPPADownloadStatistics.COLUMN_USER ]
                name = the_filter[ IndicatorPPADownloadStatistics.COLUMN_NAME ]
                series = the_filter[ IndicatorPPADownloadStatistics.COLUMN_SERIES ]
                architecture = the_filter[ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ]
                filter_text = the_filter[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ]
                self.filters.add_filter( user, name, series, architecture, filter_text )

        else:
            self.ppas = [ ]
            self.ppas.append( PPA( "thebernmeister", "ppa", "jammy", "amd64" ) )

            filter_text = [
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
            self.filters.add_filter( "thebernmeister", "ppa", "jammy", "amd64", filter_text )
            self.request_save_config()


    def save_config( self ):
        ppas = [ ]
        for ppa in self.ppas:
            ppas.append( [ ppa.get_user(), ppa.get_name(), ppa.get_series(), ppa.get_architecture() ] )

        filters = [ ]
        for user, name, series, architecture in self.filters.get_user_name_series_architecture():
            filter_text = self.filters.get_filter_text( user, name, series, architecture )
            filters.append( [ user, name, series, architecture, filter_text ] )

        return {
            IndicatorPPADownloadStatistics.CONFIG_COMBINE_PPAS : self.combine_ppas,
            IndicatorPPADownloadStatistics.CONFIG_FILTERS : filters,
            IndicatorPPADownloadStatistics.CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC : self.ignore_version_architecture_specific,
            IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH : self.low_bandwidth,
            IndicatorPPADownloadStatistics.CONFIG_PPAS : ppas,
            IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU : self.show_submenu,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD : self.sort_by_download,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT : self.sort_by_download_amount
        }


IndicatorPPADownloadStatistics().main()
