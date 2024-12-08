#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from _ast import Or


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


""" Application indicator which displays PPA download statistics. """


import concurrent.futures
import locale
import threading
import webbrowser

from copy import deepcopy
from urllib.error import URLError
from urllib.request import urlopen

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from indicatorbase import IndicatorBase

from ppa import Filter, PPA, PublishedBinary


#TODO Consider putting in a check/limit for published binaries
# with say 25 or more entries.
# Will result in a request for the download count for each...


#TODO Do a search for | here and in ppa.py
# and see if it should be used for say keys (when a tuple should be used instead)
# and where else used and if something better could be done...


class IndicatorPPADownloadStatistics( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Unused within the indicator; used by build_wheel.py when building
    # the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator PPA Download Statistics" )
    indicator_categories = "Categories=Utility"

    CONFIG_COMBINE_PPAS = "combinePPAs"
    CONFIG_FILTERS = "filters"
    CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC = "ignoreVersionArchitectureSpecific"
    CONFIG_LOW_BANDWIDTH = "lowBandwidth"
    CONFIG_PPAS = "ppas"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_SORT_BY_DOWNLOAD = "sortByDownload"
    CONFIG_SORT_BY_DOWNLOAD_AMOUNT = "sortByDownloadAmount"

    ARCHITECTURES = [ "amd64", "i386" ]

    # Data model columns used in the Preferences dialog and json config.
    COLUMN_USER = 0
    COLUMN_NAME = 1
    COLUMN_SERIES = 2
    COLUMN_ARCHITECTURE = 3
    COLUMN_FILTER_TEXT = 4

    MESSAGE_ERROR_RETRIEVING_PPA = _( "(error retrieving PPA)" )
    MESSAGE_NO_PUBLISHED_BINARIES = _( "(no published binaries)" )
    MESSAGE_FILTERED = _( "(published binaries completely filtered)" )
    MESSAGE_MIX_OF_OK_NO_PUBLISHED_BINARIES_FILTERED = _( "(multiple messages; uncheck combine to view)" )


    def __init__( self ):
        super().__init__(
            comments = _( "Displays the total downloads of PPAs." ) )

        # The series (name for each Ubuntu release) will be downloaded when the
        # user initiates Add PPA or Edit PPA in the Preferences.
        self.series = [ ]


    def update( self, menu ):
        self.download_ppa_statistics()
        self.build_menu( menu )
        return 6 * 60 * 60 # Update every six hours.


    def build_menu( self, menu ):
        # Pass a copy as combining can alter the series/architecture.
        ppas = deepcopy( self.ppas )

        if self.combine_ppas:
            ppas = self.combine( ppas )

        if self.sort_by_download:
            for ppa in ppas:
                ppa.sort_published_binaries_by_download_count_and_clip(
                    self.sort_by_download_amount )

        if self.show_submenu:
            for ppa in ppas:
                submenu = Gtk.Menu()
                self.create_and_append_menuitem(
                    menu,
                    ppa.get_descriptor() ).set_submenu( submenu )

                if ppa.get_status() == PPA.Status.OK:
                    published_binaries = ppa.get_published_binaries( True )
                    for published_binary in published_binaries:
                        self.create_menuitem_for_published_binary(
                            submenu, ( 1, 0 ), ppa, published_binary )

                else:
                    self.create_and_append_menuitem(
                        submenu,
                        self.get_status_message( ppa ),
                        indent = ( 1, 1 ) )

        else:
            for ppa in ppas:
                self.create_and_append_menuitem(
                    menu,
                    ppa.get_descriptor(),
                    name = ppa.get_descriptor(),
                    activate_functionandarguments = ( self.on_ppa, ) )

                if ppa.get_status() == PPA.Status.OK:
                    published_binaries = ppa.get_published_binaries( True )
                    for published_binary in published_binaries:
                        self.create_menuitem_for_published_binary(
                            menu, ( 1, 1 ), ppa, published_binary )

                else:
                    self.create_and_append_menuitem(
                        menu,
                        self.get_status_message( ppa ),
                        indent = ( 1, 1 ) )

            # When only one PPA is present, enable a middle mouse click
            # on the icon to open the PPA in the browser.
            if len( ppas ) == 1:
                self.set_secondary_activate_target( menu.get_children()[ 0 ] )


    def create_menuitem_for_published_binary(
        self, menu, indent, ppa, published_binary ):

        label = published_binary.get_package_name()
        if published_binary.get_package_version() is not None:
            label += " " + published_binary.get_package_version()

#TODO Check that the space is needed when combined and not combined.
        label += " :  " + str( published_binary.get_download_count() )

        self.create_and_append_menuitem(
            menu,
            label,
            name = ppa.get_descriptor(),
            activate_functionandarguments = ( self.on_ppa, ),
            indent = indent )


    def get_status_message( self, ppa ):
        if ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA:
            message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_RETRIEVING_PPA

        elif ppa.get_status() == PPA.Status.NO_PUBLISHED_BINARIES:
            message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES

        elif ppa.get_status() == PPA.Status.FILTERED:
            message = IndicatorPPADownloadStatistics.MESSAGE_FILTERED

        elif ppa.get_status() == PPA.Status.MIX_OF_OK_NO_PUBLISHED_BINARIES_FILTERED:
            message = IndicatorPPADownloadStatistics.MESSAGE_MIX_OF_OK_NO_PUBLISHED_BINARIES_FILTERED

        return message


    def combine( self, ppas ):
        '''
        Combine PPAs with the same user and name into a single PPA.
        '''
        combined_ppas = { }
        for ppa in ppas:
            key = ( ppa.get_user(), ppa.get_name() )
            if key in combined_ppas:
                error = (
                    ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA or
                    combined_ppas[ key ].get_status() == PPA.Status.ERROR_RETRIEVING_PPA )

                ok = (
                    ppa.get_status() == PPA.Status.OK and
                    combined_ppas[ key ].get_status() == PPA.Status.OK )

                filtered = (
                    ppa.get_status() == PPA.Status.FILTERED and
                    combined_ppas[ key ].get_status() == PPA.Status.FILTERED )

                no_published_binaries = (
                    ppa.get_status() == PPA.Status.NO_PUBLISHED_BINARIES and
                    combined_ppas[ key ].get_status() == PPA.Status.NO_PUBLISHED_BINARIES )

                if error:
                    combined_ppas[ key ].set_status( PPA.Status.ERROR_RETRIEVING_PPA )

                elif filtered or no_published_binaries:
                    pass

                elif ok:
                    self.__merge_ppa( ppa, combined_ppas[ key ] )

                else:
                    # Mix of ok, no published binaries, filtered.
                    combined_ppas.flush_published_binaries()
                    combined_ppas[ key ].set_status(
                        PPA.Status.MIX_OF_OK_NO_PUBLISHED_BINARIES_FILTERED )

            else:
                combined_ppas[ key ] = ppa

        return combined_ppas.values()


#TODO Check and more check!
    def __merge_ppa( self, ppa, combined_ppa ):
        processed = [ ]
        add_to_combined = [ ]
        for published_binary in ppa.get_published_binaries():
            for published_binary_combined in combined_ppa.get_published_binaries():
                same_package_name = (
                    published_binary_combined.get_package_name() ==
                    published_binary.get_package_name() )

                if same_package_name:
                    processed.append( published_binary )

                    both_binary_packages_are_architecture_independent = (
                        not published_binary_combined.is_architecture_specific() and
                        not published_binary.is_architecture_specific() )

                    both_binary_packages_are_architecture_specific = (
                        published_binary_combined.is_architecture_specific() and
                        published_binary.is_architecture_specific() )

                    if both_binary_packages_are_architecture_independent:
                        same_package_version = (
                            published_binary_combined.get_package_version() ==
                            published_binary.get_package_version() )

                        if not same_package_version:
                            add_to_combined.append( published_binary )

                    elif both_binary_packages_are_architecture_specific:
                        pass #TODO

                    else:
                        pass #TODO





                    either_binary_package_is_architecture_specific = (
                        published_binary_combined.is_architecture_specific() or
                        published_binary.is_architecture_specific() )

                    if same_package_version:
                        if either_binary_package_is_architecture_specific:
                            published_binary_combined.set_download_count(
                                published_binary_combined.get_download_count + \
                                published_binary.get_download_count )

                    else:
                        if either_binary_package_is_architecture_specific:
                            if self.ignore_version_architecture_specific:
                                published_binary_combined.set_download_count(
                                    published_binary_combined.get_download_count + \
                                    published_binary.get_download_count )



        for published_binary in add_to_combined:
            #TODO Need to check if there is an existing same name/version (from a previously combined ppa)?
            combined_ppa.add_published_binary( published_binary )

        for published_binary in ppa:
            if published_binary not in processed:
                pass #TODO Need to add to combined ppa


#TODO Double check this...
# Seems to be searching for | but I don't see
# when creating the menu items adding in a | ...
#
# Check ppa.py
#
# I think look for all uses of | and work out how/when it is used.
# Might be able to use a tuple instead (and a join for when used in display).
# Might be able to have a single function to do all of this within ppa.py
    def on_ppa( self, menuitem ):
        url = "https://launchpad.net/~"
        first_pipe = str.find( menuitem.get_name(), "|" )
        ppa_user = menuitem.get_name()[ 0 : first_pipe ].strip()
        second_pipe = str.find( menuitem.get_name(), "|", first_pipe + 1 )
        if second_pipe == -1:
            # This is a combined PPA...
            ppa_name = menuitem.get_name()[ first_pipe + 1 : ].strip()
            url += f"{ ppa_user }/+archive/ubuntu/{ ppa_name }"
            if menuitem.get_name() != menuitem.get_label():
                # Use the menu item label to specify the package name.
                url += \
                    f"/+packages?field.name_filter=" + \
                    f"{ menuitem.get_label().split()[ 0 ] }" + \
                    "&field.status_filter=published&field.series_filter="

        else:
            ppa_name = menuitem.get_name()[ first_pipe + 1 : second_pipe ].strip()
            third_pipe = str.find( menuitem.get_name(), "|", second_pipe + 1 )
            series = menuitem.get_name()[ second_pipe + 1 : third_pipe ].strip()
            url += f"{ ppa_user }/+archive/ubuntu/{ ppa_name }"
            if menuitem.get_name() == menuitem.get_label():
                url += f"?field.series_filter={ series }"

            else: # Use the menu item label to specify the package name.
                url += \
                    "/+packages?field.name_filter=" + \
                    f"{ menuitem.get_label().split()[ 0 ] }"+ \
                    f"&field.status_filter=published&field.series_filter={ series }"

        webbrowser.open( url )


    def get_filters( self, ppa ):
        filters = [ ]
        for f in self.filters:
            match = (
                f.get_user() == ppa.get_user() and
                f.get_name() == ppa.get_name() and
                f.get_series() == ppa.get_series() and
                f.get_architecture() == ppa.get_architecture() )

            if match:
                filters = f.get_text()
                break

        if not filters:
            filters = [ "" ]

        return filters


#TODO For testing combine.
# https://api.launchpad.net/1.0/~thebernmeister/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false
#
# https://api.launchpad.net/1.0/~thebernmeister/+archive/ubuntu/ppa/+binarypub/200273074?ws.op=getDownloadCount
#
# https://api.launchpad.net/1.0/~thebernmeister/+archive/ubuntu/ppa/+binarypub/200273018
#
# https://api.launchpad.net/1.0/~thebernmeister/+archive/ubuntu/ppa/+binarypub/200273018?ws.op=getDownloadCount
#
# https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false&binary_name=linux-image-oem
#
# https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false&binary_name=linux-image
#
# https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false&binary_name=linux-image-oem
#
# https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false


    def download_ppa_statistics( self ):
        '''
        For each PPA's binary packages, get the download count.

        References
            http://launchpad.net/+apidoc
            http://help.launchpad.net/API/launchpadlib
            http://help.launchpad.net/API/Hacking
        '''
        for ppa in self.ppas:
            ppa.set_status( PPA.Status.NEEDS_DOWNLOAD )

            for filter_text in self.get_filters( ppa ):
                self.get_download_counts( ppa, filter_text )
                if ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA:
                    break

            if ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA:
                ppa.flush_published_binaries()

            elif ppa.has_published_binaries():
                ppa.set_status( PPA.Status.OK )

            else:
                if filter_text == "":
                    # No published binaries as there is no filter in place.
                    ppa.set_status( PPA.Status.NO_PUBLISHED_BINARIES )

                else:
                    # No results passed through filtering.
                    ppa.set_status( PPA.Status.FILTERED )


 #TODO For testing.
 # https://api.launchpad.net/1.0/~thebernmeister/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false
 #
 # https://api.launchpad.net/1.0/~thebernmeister/+archive/ubuntu/ppa/+binarypub/200273074?ws.op=getDownloadCount
 #
 # https://api.launchpad.net/1.0/~thebernmeister/+archive/ubuntu/ppa/+binarypub/200273018
 #
 # https://api.launchpad.net/1.0/~thebernmeister/+archive/ubuntu/ppa/+binarypub/200273018?ws.op=getDownloadCount
 #
 # https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false&binary_name=linux-image-oem
 #
 # https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false&binary_name=linux-image
 #
 # https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false&binary_name=linux-image-oem
 #
 # https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false


    def get_download_counts( self, ppa, filter_text ):
        '''
        Get the published binaries for the PPA and then for each published
        binary, get the download count.

        A filter_text of "" equates to no filtering.
        '''
        self_links = [ ]
        binary_package_names = [ ]
        binary_package_versions = [ ]
        architecture_specifics = [ ]

        self.__get_published_binaries(
            ppa,
            filter_text,
            self_links,
            binary_package_names,
            binary_package_versions,
            architecture_specifics )

        if not ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA:
            self.__get_download_counts(
                ppa,
                self_links,
                binary_package_names,
                binary_package_versions,
                architecture_specifics )


    def __get_published_binaries(
            self,
            ppa,
            filter_text,
            self_links,
            binary_package_names,
            binary_package_versions,
            architecture_specifics ):

        url = (
            f"https://api.launchpad.net/1.0/~{ ppa.get_user() }" +
            f"/+archive/ubuntu/{ ppa.get_name() }?ws.op=getPublishedBinaries&" +
            f"distro_arch_series=https://api.launchpad.net/1.0/ubuntu/" +
            f"{ ppa.get_series() }/{ ppa.get_architecture() }" +
            f"&status=Published&exact_match=false&ordered=false" +
            f"&binary_name={ filter_text }" )

        i = 0 #TODO Testing
        next_collection_link = "next_collection_link"
        while True:
            print( f"Get published binaries for { ppa } | { filter_text } | { i }" ) #TODO Testing
            i += 1 #TODO Testing
            published_binaries = self.get_json( url )  #TODO Test with a ppa/archive with NO published binaries....should not get an error...right?
            if published_binaries: #TODO If we have multiple pages, will this be None and then set the status to error below?
                for entry in published_binaries[ "entries" ]: #TODO Test for no entries (filter out with bogus indicator name.
                    self_links.append( entry[ "self_link" ] )
                    binary_package_names.append( entry[ "binary_package_name" ] )
                    binary_package_versions.append( entry[ "binary_package_version" ] )
                    architecture_specifics.append( entry[ "architecture_specific" ] )

                if next_collection_link in published_binaries:
                    url = published_binaries[ next_collection_link ]
                    continue

                break

            else:
                print( "here" ) #TODO Testing...ensure this is not set when the last published binaries page is downloaded.
                ppa.set_status( PPA.Status.ERROR_RETRIEVING_PPA )
                break


    def __get_download_counts(
            self,
            ppa,
            self_links,
            binary_package_names,
            binary_package_versions,
            architecture_specifics ):

        max_workers = 1 if self.low_bandwidth else 4
        download_counts = { }
        with concurrent.futures.ThreadPoolExecutor( max_workers = max_workers ) as executor:
            for i, self_link in enumerate( self_links ):
                download_counts[ i ] = \
                    executor.submit(
                        self.get_json,
                        self_links[ i ] + "?ws.op=getDownloadCount" )

        for i, result in download_counts.items():
            if result.exception() is None:
                ppa.add_published_binary(
                    PublishedBinary(
                        binary_package_names[ i ],
                        binary_package_versions[ i ],
                        result.result(),
                        architecture_specifics[ i ] ) )

            else:
                ppa.set_status( PPA.Status.ERROR_RETRIEVING_PPA )
                break


    def on_preferences( self, dialog ):
        series_download_thread = None
        if not self.series:
            series_download_thread = \
                threading.Thread( target = self.initialise_series )

            series_download_thread.start()

        notebook = Gtk.Notebook()

        # PPAs.
        grid = self.create_grid()

        # PPA user, name, series, architecture.
        ppa_store = Gtk.ListStore( str, str, str, str )

        for ppa in self.ppas:
            ppa_store.append( [
                ppa.get_user(),
                ppa.get_name(),
                ppa.get_series(),
                ppa.get_architecture() ] )

        ppa_treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                ppa_store,
                (
                    _( "PPA User" ),
                    _( "PPA Name" ),
                    _( "Series" ),
                    _( "Architecture" ) ),
                (
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_USER ),
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_NAME ),
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_SERIES ),
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ) ),
                tooltip_text = _( "Double click to edit a PPA." ),
                rowactivatedfunctionandarguments = (
                    self.on_ppa_double_click, series_download_thread ) )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        grid.attach(
            self.create_buttons_in_box(
                (
                    _( "Add" ),
                    _( "Remove" ) ),
                (
                    _( "Add a new PPA." ),
                    _( "Remove the selected PPA." ) ),
                (
                    ( self.on_ppa_add, ppa_treeview, series_download_thread ),
                    ( self.on_ppa_remove, ppa_treeview ) ) ),
            0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "PPAs" ) ) )

        # Filters.
        grid = self.create_grid()

        # PPA user, name, filter text.
        filter_store = Gtk.ListStore( str, str, str )

        for filter_ in self.filters:
            filter_store.append( [
                filter_.get_user(),
                filter_.get_name(),
                "\n".join( filter_.get_text() ) ] )

        filter_treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                filter_store,
                (
                    _( "PPA User" ),
                    _( "PPA Name" ),
                    _( "Filter" ) ),
                (
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_USER ),
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_NAME ),
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ) ),
                tooltip_text = _( "Double click to edit a filter." ),
                rowactivatedfunctionandarguments = ( self.on_filter_double_click, ppa_treeview ) )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        grid.attach(
            self.create_buttons_in_box(
            (
                _( "Add" ),
                _( "Remove" ) ),
            (
                _( "Add a new filter." ),
                _( "Remove the selected filter." ) ),
            (
                ( self.on_filter_add, filter_treeview, ppa_treeview ),
                ( self.on_filter_remove, filter_treeview ) ) ),
            0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Filters" ) ) )

        # General settings.
        grid = self.create_grid()

        show_as_submenus_checkbutton = \
            self.create_checkbutton(
                _( "Show PPAs as submenus" ),
                tooltip_text = _(
                    "The download statistics for each PPA\n" +
                    "are shown in a separate submenu." ),
                active = self.show_submenu )

        grid.attach( show_as_submenus_checkbutton, 0, 0, 1, 1 )

        combine_ppas_checkbutton = \
            self.create_checkbutton(
                _( "Combine PPAs" ),
                tooltip_text = _(
                    "Combine the statistics of binary\n" +
                    "packages when the PPA user/name\n" +
                    "are the same.\n\n" +
                    "Non-architecture specific packages:\n" +
                    "If the package names and version\n" +
                    "numbers of two binary packages are\n" +
                    "identical, the packages are treated\n" +
                    "as the same package and the\n" +
                    "download counts are NOT summed.\n" +
                    "Packages such as Python fall into\n" +
                    "this category.\n\n" +
                    "Architecture specific packages:\n" +
                    "If the package names and version\n" +
                    "numbers of two binary packages are\n" +
                    "identical, the packages are treated\n" +
                    "as the same package and the download\n" +
                    "counts ARE summed.\n" +
                    "Packages such as compiled C fall into\n" +
                    "this category." ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP,
                active = self.combine_ppas )

        grid.attach( combine_ppas_checkbutton, 0, 1, 1, 1 )

        ignore_version_architecture_specific_checkbutton = \
            self.create_checkbutton(
                _( "Ignore version for architecture specific" ),
                tooltip_text = _(
                    "Sometimes architecture specific\n" +
                    "packages with the same package\n" +
                    "name but different version 'number'\n" +
                    "are logically the SAME package.\n\n" +
                    "For example, a C source package for\n" +
                    "both Ubuntu Saucy and Ubuntu Trusty\n" +
                    "will be compiled twice, each with a\n" +
                    "different 'number', despite being\n" +
                    "the SAME release.\n\n" +
                    "Checking this option will ignore the\n" +
                    "version number when determining if\n" +
                    "two architecture specific packages\n" +
                    "are identical.\n\n" +
                    "The version number is retained only\n" +
                    "if it is identical across ALL\n" +
                    "instances of a published binary." ),
                sensitive = combine_ppas_checkbutton.get_active(),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.ignore_version_architecture_specific )

        grid.attach(
            ignore_version_architecture_specific_checkbutton,
            0, 2, 1, 1 )

        combine_ppas_checkbutton.connect(
            "toggled",
            self.on_radio_or_checkbox,
            True,
            ignore_version_architecture_specific_checkbutton )

        sort_by_download_checkbutton = \
            self.create_checkbutton(
                _( "Sort by download" ),
                tooltip_text = _( "Sort by download count within each PPA." ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP,
                active = self.sort_by_download )

        grid.attach( sort_by_download_checkbutton, 0, 3, 1, 1 )

        label = Gtk.Label.new( _( "Clip amount" ) )
        label.set_sensitive( sort_by_download_checkbutton.get_active() )

        spinner = \
            self.create_spinbutton(
                self.sort_by_download_amount,
                0,
                10000,
                page_increment = 100,
                tooltip_text = _(
                    "Limit the number of entries\n" +
                    "when sorting by download.\n\n" +
                    "A value of zero will not clip." ),
                sensitive = sort_by_download_checkbutton.get_active() )

        grid.attach(
            self.create_box(
                (
                    ( label, False ),
                    ( spinner, False ) ),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT ),
            0, 4, 1, 1 )

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
                margin_top = IndicatorBase.INDENT_WIDGET_TOP,
                active = self.low_bandwidth )

        grid.attach( low_bandwidth_checkbutton, 0, 5, 1, 1 )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = \
            self.create_preferences_common_widgets()

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
            while treeiter is not None:
                ppa = ppa_store[ treeiter ]
                self.ppas.append(
                    PPA(
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_USER ],
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_NAME ],
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_SERIES ],
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] ) )

                treeiter = ppa_store.iter_next( treeiter )

            PPA.sort( self.ppas )

            self.filters = [ ]
            treeiter = filter_store.get_iter_first()
            while treeiter is not None:
                filter_ = filter_store[ treeiter ]
                self.filters.append(
                    Filter(
                        filter_[ IndicatorPPADownloadStatistics.COLUMN_USER ],
                        filter_[ IndicatorPPADownloadStatistics.COLUMN_NAME ],
                        filter_[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ].split() ) )

                treeiter = filter_store.iter_next( treeiter )

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


    def initialise_series( self ):
        urls = [
            "https://changelogs.ubuntu.com/meta-release",
            "https://changelogs.ubuntu.com/meta-release-development" ]

        try:
            series = [ ]
            for url in urls:
                with urlopen( url ) as f:
                    for line in f.read().decode().splitlines():
                        if "Dist:" in line:
                            s = line.split()[ 1 ]
                            if s not in series:
                                series.insert( 0, s )

            self.series = series

        except URLError as e:
            self.series = [ ]
            self.get_logging().error( "Error downloading from " + str( url ) )
            self.get_logging().exception( e )


    def check_series_download( self, series_download_thread, treeview ):
        series_is_downloaded_or_did_not_require_downloading = True
        if series_download_thread is not None:
            series_download_thread.join( 5.0 )
            if series_download_thread.is_alive():
                series_is_downloaded_or_did_not_require_downloading = False
                self.show_dialog_ok(
                    treeview,
                    _( f"TODO Need message to say series is unavailable and"
                    f"maybe check log and/or check internet connection or is a slow connection?" ),
                    title = self.indicator_name,
                    message_type = Gtk.MessageType.ERROR )

        return series_is_downloaded_or_did_not_require_downloading


    def on_ppa_remove( self, button, treeview ):
        model, treeiter = treeview.get_selection().get_selected()
        if treeiter is None:
            self.show_dialog_ok(
                treeview,
                _( "No PPA has been selected for removal." ) )

        else:
            response = \
                self.show_dialog_ok_cancel(
                    treeview,
                    _( "Remove the selected PPA?" ) )

            if response == Gtk.ResponseType.OK:
                model.remove( treeiter )


    def on_ppa_add( self, button, treeview, series_download_thread ):
        if self.check_series_download( series_download_thread, treeview ):
            self.on_ppa_add_( button, treeview )
        #TODO Wait until add and edit are finalised and then hopefully
        # the call to check series download is done in only one place.
        #
        # If add and edit are not eventually combined into one function
        # then have on_ppa_add which is called on the Add button press
        # and does the check and if the check passes, calls on_ppa_add_
        # which does the actual add (ditto for edit).


    def on_ppa_add_( self, button, treeview ):
        # self.on_ppa_double_click( treeview, None, None ) #TODO Original...
        grid = self.create_grid()

        label = Gtk.Label.new( _( "PPA User" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        ppa_users = [ ]
        ppa_names = [ ]
        for i, row in enumerate( treeview.get_model() ):
            user = row[ IndicatorPPADownloadStatistics.COLUMN_USER ]
            if user not in ppa_users:
                ppa_users.append( user )

            name = row[ IndicatorPPADownloadStatistics.COLUMN_NAME ]
            if name not in ppa_names:
                ppa_names.append( name )

        ppa_users.sort( key = locale.strxfrm ) #TODO Is this needed anywhere?
        ppa_names.sort( key = locale.strxfrm ) #TODO Is this needed anywhere?

        ppa_user = \
            self.create_comboboxtext(
                ppa_users,
                editable = True )

        grid.attach( ppa_user, 1, 0, 1, 1 )

        label = Gtk.Label.new( _( "PPA Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        ppa_name = \
            self.create_comboboxtext(
                ppa_names,
                editable = True )

        grid.attach( ppa_name, 1, 1, 1, 1 )

        label = Gtk.Label.new( _( "Series" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        ppa_series = \
            self.create_comboboxtext(
                self.series,
                active = 0 )

        grid.attach( ppa_series, 1, 2, 1, 1 )

        label = Gtk.Label.new( _( "Architecture" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        ppa_architectures = \
            self.create_comboboxtext(
                IndicatorPPADownloadStatistics.ARCHITECTURES,
                active = 0 )

        grid.attach( ppa_architectures, 1, 3, 1, 1 )

        dialog = \
            self.create_dialog(
             treeview,
             _( "Add PPA" ),
             content_widget = grid )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                user = ppa_user.get_active_text().strip()
                if user == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "PPA user cannot be empty." )  )

                    ppa_user.grab_focus()
                    continue

                name = ppa_name.get_active_text().strip()
                if name == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "PPA name cannot be empty." ) )

                    ppa_name.grab_focus()
                    continue

                duplicate = False
                for i, row in enumerate( treeview.get_model() ):
                    duplicate = \
                        user == row[ IndicatorPPADownloadStatistics.COLUMN_USER ] and \
                        name == row[ IndicatorPPADownloadStatistics.COLUMN_NAME ] and \
                        ppa_series.get_active_text() == row[ IndicatorPPADownloadStatistics.COLUMN_SERIES ] and \
                        ppa_architectures.get_active_text() == row[ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ]

                    if duplicate:
                        break

                if duplicate:
                    self.show_dialog_ok(
                        dialog,
                        _( "Duplicates disallowed - there is an identical PPA!" ) )

                    continue

                treeview.get_model().append( [
                    user,
                    name,
                    ppa_series.get_active_text(),
                    ppa_architectures.get_active_text() ] )

            break

        dialog.destroy()


    def on_ppa_double_click(
        self,
        treeview,
        row_number,
        treeviewcolumn,
        series_download_thread ):
#TODO Need to pass in the thread and then do a thread.join()
# Maybe join with a timeout?
# Then check that self.series is not None and proceed to edit,
# otherwise message user and return/fail/abort.


        model, treeiter = treeview.get_selection().get_selected()

        grid = self.create_grid()

        label = Gtk.Label.new( _( "PPA User" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        if len( model ) > 0:
            ppa_users = [ ]
            for i, row in enumerate( model ):
                user = row[ IndicatorPPADownloadStatistics.COLUMN_USER ]
                if user not in ppa_users:
                    ppa_users.append( user )

            ppa_users.sort( key = locale.strxfrm ) #TODO Is this needed anywhere?

            ppa_user = \
                self.create_comboboxtext(
                    ppa_users,
                    active =
                        ppa_users.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] )
                        if row_number else
                        -1,
                        editable = True )

        else:
            # There are no PPAs present - adding the first PPA.
            ppa_user = self.create_entry( "" )

        grid.attach( ppa_user, 1, 0, 1, 1 )

        label = Gtk.Label.new( _( "PPA Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        if len( model ) > 0:
            ppa_names = [ ]
            for i, row in enumerate( model ):
                if model[ i ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] not in ppa_names:
                    ppa_names.append(
                        model[ i ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] )

            ppa_names.sort( key = locale.strxfrm )

            ppa_name = \
                self.create_comboboxtext(
                    ppa_names,
                    active =
                        ppa_names.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] )
                        if row_number else
                        -1,
                        editable = True )

        else:
            # There are no PPAs present - adding the first PPA.
            ppa_name = self.create_entry( "" )

        grid.attach( ppa_name, 1, 1, 1, 1 )

        label = Gtk.Label.new( _( "Series" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        series = \
            self.create_comboboxtext(
                self.series,
                active =
                    self.series.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] )
                    if row_number else
                    0 )

        grid.attach( series, 1, 2, 1, 1 )

        label = Gtk.Label.new( _( "Architecture" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        architectures = \
            self.create_comboboxtext(
                IndicatorPPADownloadStatistics.ARCHITECTURES,
                active =
                    IndicatorPPADownloadStatistics.ARCHITECTURES.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] )
                    if row_number else
                    0 )

        grid.attach( architectures, 1, 3, 1, 1 )

        title = _( "Add PPA" )
        if row_number:
            title = _( "Edit PPA" )

        dialog = \
            self.create_dialog(
             treeview,
             title,
             content_widget = grid )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if len( model ) > 0:
                    ppa_user_value = ppa_user.get_active_text().strip()
                    ppa_name_value = ppa_name.get_active_text().strip()

                else:
                    ppa_user_value = ppa_user.get_text().strip()
                    ppa_name_value = ppa_name.get_text().strip()

                if ppa_user_value == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "PPA user cannot be empty." )  )

                    ppa_user.grab_focus()
                    continue

                if ppa_name_value == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "PPA name cannot be empty." ) )

                    ppa_name.grab_focus()
                    continue

                # Ensure there is no duplicate...
                if ( row_number is None and len( model ) > 0 ) or ( row_number and len( model ) > 1 ):
                    # Doing an add and there's at least one PPA OR
                    # doing an edit and there's at least two PPAs...
                    if row_number is None:
                        # Doing an add, so data has changed.
                        data_has_been_changed = True

                    else:
                        # Doing an edit, so check to see if there the
                        # data has actually been changed...
                        data_has_been_changed = not ( \
                            ppa_user_value == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] and \
                            ppa_name_value == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] and \
                            series.get_active_text() == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] and \
                            architectures.get_active_text() == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] )

                    if data_has_been_changed:
                        duplicate = False
                        for i, row in enumerate( model ):
                            if ppa_user_value == model[ i ][ IndicatorPPADownloadStatistics.COLUMN_USER ] and \
                               ppa_name_value == model[ i ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] and \
                               series.get_active_text() == model[ i ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] and \
                               architectures.get_active_text() == model[ i ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ]:

                                duplicate = True
                                break

                        if duplicate:
                            self.show_dialog_ok(
                                dialog,
                                _( "Duplicates disallowed - there is an identical PPA!" ) )

                            continue

                # Update the model...
                if row_number:
                    # This is an edit...remove the old value and
                    # append new value.
                    model.remove( treeiter )

                model.append( [
                    ppa_user_value,
                    ppa_name_value,
                    series.get_active_text(),
                    architectures.get_active_text() ] )

            break

        dialog.destroy()


#TODO Remove
    def on_ppa_double_clickORIGINAL(
        self,
        treeview,
        row_number,
        treeviewcolumn ):

        model, treeiter = treeview.get_selection().get_selected()

        grid = self.create_grid()

        label = Gtk.Label.new( _( "PPA User" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        if len( model ) > 0:
            ppa_users = [ ]
            for i, row in enumerate( model ):
                if model[ i ][ IndicatorPPADownloadStatistics.COLUMN_USER ] not in ppa_users:
                    ppa_users.append(
                        model[ i ][ IndicatorPPADownloadStatistics.COLUMN_USER ] )

            ppa_users.sort( key = locale.strxfrm )

            ppa_user = \
                self.create_comboboxtext(
                    ppa_users,
                    active =
                        ppa_users.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] )
                        if row_number else
                        -1,
                        editable = True )

        else:
            # There are no PPAs present - adding the first PPA.
            ppa_user = self.create_entry( "" )

        grid.attach( ppa_user, 1, 0, 1, 1 )

        label = Gtk.Label.new( _( "PPA Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        if len( model ) > 0:
            ppa_names = [ ]
            for i, row in enumerate( model ):
                if model[ i ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] not in ppa_names:
                    ppa_names.append(
                        model[ i ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] )

            ppa_names.sort( key = locale.strxfrm )

            ppa_name = \
                self.create_comboboxtext(
                    ppa_names,
                    active =
                        ppa_names.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] )
                        if row_number else
                        -1,
                        editable = True )

        else:
            # There are no PPAs present - adding the first PPA.
            ppa_name = self.create_entry( "" )

        grid.attach( ppa_name, 1, 1, 1, 1 )

        label = Gtk.Label.new( _( "Series" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        series = \
            self.create_comboboxtext(
                self.series,
                active =
                    self.series.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] )
                    if row_number else
                    0 )

        grid.attach( series, 1, 2, 1, 1 )

        label = Gtk.Label.new( _( "Architecture" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        architectures = \
            self.create_comboboxtext(
                IndicatorPPADownloadStatistics.ARCHITECTURES,
                active =
                    IndicatorPPADownloadStatistics.ARCHITECTURES.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] )
                    if row_number else
                    0 )

        grid.attach( architectures, 1, 3, 1, 1 )

        title = _( "Add PPA" )
        if row_number:
            title = _( "Edit PPA" )

        dialog = \
            self.create_dialog(
             treeview,
             title,
             content_widget = grid )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if len( model ) > 0:
                    ppa_user_value = ppa_user.get_active_text().strip()
                    ppa_name_value = ppa_name.get_active_text().strip()

                else:
                    ppa_user_value = ppa_user.get_text().strip()
                    ppa_name_value = ppa_name.get_text().strip()

                if ppa_user_value == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "PPA user cannot be empty." )  )

                    ppa_user.grab_focus()
                    continue

                if ppa_name_value == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "PPA name cannot be empty." ) )

                    ppa_name.grab_focus()
                    continue

                # Ensure there is no duplicate...
                if ( row_number is None and len( model ) > 0 ) or ( row_number and len( model ) > 1 ):
                    # Doing an add and there's at least one PPA OR
                    # doing an edit and there's at least two PPAs...
                    if row_number is None:
                        # Doing an add, so data has changed.
                        data_has_been_changed = True

                    else:
                        # Doing an edit, so check to see if there the
                        # data has actually been changed...
                        data_has_been_changed = not ( \
                            ppa_user_value == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] and \
                            ppa_name_value == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] and \
                            series.get_active_text() == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] and \
                            architectures.get_active_text() == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ] )

                    if data_has_been_changed:
                        duplicate = False
                        for i, row in enumerate( model ):
                            if ppa_user_value == model[ i ][ IndicatorPPADownloadStatistics.COLUMN_USER ] and \
                               ppa_name_value == model[ i ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] and \
                               series.get_active_text() == model[ i ][ IndicatorPPADownloadStatistics.COLUMN_SERIES ] and \
                               architectures.get_active_text() == model[ i ][ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ]:

                                duplicate = True
                                break

                        if duplicate:
                            self.show_dialog_ok(
                                dialog,
                                _( "Duplicates disallowed - there is an identical PPA!" ) )

                            continue

                # Update the model...
                if row_number:
                    # This is an edit...remove the old value and
                    # append new value.
                    model.remove( treeiter )

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
            self.show_dialog_ok(
                treeview,
                _( "No filter has been selected for removal." ) )

        else:
            # Prompt the user to remove - only one row can be selected
            # since single selection mode has been set.
            if self.show_dialog_ok_cancel( treeview, _( "Remove the selected filter?" ) ) == Gtk.ResponseType.OK:
                model.remove( treeiter )


    def on_filter_add( self, button, filter_treeview, ppa_treeview ):
        if len( ppa_treeview.get_model() ) == 0:
            self.show_dialog_ok(
                filter_treeview,
                _( "Please add a PPA first!" ) )

        else:
#TODO Check this comment and explain better...
            # If the number of filters equals the number of PPA User/Names,
            # cannot add a filter!
            ppa_users_names = [ ]
            for i, row in enumerate( ppa_treeview.get_model() ):
                ppa_user_name = \
                    row[ IndicatorPPADownloadStatistics.COLUMN_USER ] + \
                    ' | ' + \
                    row[ IndicatorPPADownloadStatistics.COLUMN_NAME ]

                if not ppa_user_name in ppa_users_names:
                    ppa_users_names.append( ppa_user_name )

#TODO Check this logic...is this the correct check to ensure no duplicate filters?
            if len( filter_treeview.get_model() ) == len( ppa_users_names ):
                self.show_dialog_ok(
                    filter_treeview,
                    _( "Only one filter per PPA User/Name." ),
                    message_type = Gtk.MessageType.INFO )

            else:
                self.on_filter_double_click(
                    filter_treeview,
                    None,
                    None,
                    ppa_treeview )


#TODO Double click on an existing filter.
# The filter text says 'ppa'.
# I would have thought the filter text would be the list of filter text shown in the display...?

    def on_filter_double_click(
        self,
        filter_treeview,
        row_number,
        treeviewcolumnm,
        ppa_treeview ):

        filter_model, filter_treeiter = \
            filter_treeview.get_selection().get_selected()

        ppa_model, ppa_treeiter = \
            ppa_treeview.get_selection().get_selected()

        grid = self.create_grid()

        label = Gtk.Label.new( _( "PPA User/Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        ppa_users_names = Gtk.ComboBoxText.new()  #TODO This should use indicatorbase
        if row_number is None: # Adding
            temp = [ ] # Used to ensure duplicates are not added.
            for i, row in enumerate( ppa_model ):
                ppa_user_name = \
                    row[ IndicatorPPADownloadStatistics.COLUMN_USER ] + \
                    ' | ' + \
                    row[ IndicatorPPADownloadStatistics.COLUMN_NAME ]

                if ppa_user_name in temp:
                    continue

                in_filter_list = False
                for i, row in enumerate( filter_model ):
                    if ppa_user_name in row[ IndicatorPPADownloadStatistics.COLUMN_USER ]:
                        in_filter_list = True
                        break

                if not in_filter_list:
                    ppa_users_names.append_text( ppa_user_name )
                    temp.append( ppa_user_name )

        else:
            #TODO Why can I use the row_number rather than filter_treeiter?
            ppa_users_names.append_text(
                filter_model[ filter_treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] + \
                ' | ' + \
                filter_model[ filter_treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] )

        ppa_users_names.set_hexpand( True )
        ppa_users_names.set_active( 0 )

        grid.attach( ppa_users_names, 1, 0, 1, 1 )

        label = Gtk.Label.new( _( "Filter Text" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 2, 1 )

        textview = \
            self.create_textview(
                text =
                    filter_model[ filter_treeiter ][ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ]
                    if row_number else "",
                tooltip_text = _(
                    "Each line of text is a single\n" +
                    "filter which is compared against\n" +
                    "each package during download.\n\n" +
                    "If a package name contains ANY\n" +
                    "part of ANY filter, that package\n" +
                    "is included in the download\n" +
                    "statistics.\n\n" +
                    "Regular expressions and wild\n" +
                    "cards are not accepted!" ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( "\n\n\n\n\n" ), False ), # Padding to ensure the textview for the message text is not too small.
                    ( self.create_scrolledwindow( textview ), True ) ) ),
                     0, 3, 2, 1 )

        title = _( "Edit Filter" )
        if row_number is None:
            title = _( "Add Filter" )

        dialog = \
            self.create_dialog(
                filter_treeview,
                title,
                content_widget = grid )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                buffer = textview.get_buffer()
                filter_text = \
                    buffer.get_text(
                        buffer.get_start_iter(),
                        buffer.get_end_iter(),
                        False )

                filter_text = "\n".join( filter_text.split() )
                if len( filter_text ) == 0:
                    self.show_dialog_ok(
                        dialog,
                        _( "Please enter filter text!" ) )

                    continue

                # Update the model...
                if row_number:
                    # This is an edit...remove the old value and
                    # append new value.
                    filter_model.remove( filter_treeiter )

                filter_model.append( [
                    ppa_users_names.get_active_text(),
                    filter_text ] )

            break

        dialog.destroy()


#TODO When all is sorted out with download and preferences,
# use an old .json from old indicator name with hyphens
# and ensure the old is copied to new location (name without hyphens)
# and loads up.
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

            #TODO Is this needed here?  Figure out when/where sort is needed / not needed.
            PPA.sort( self.ppas )

            self.filters = [ ]
            filters = config.get( IndicatorPPADownloadStatistics.CONFIG_FILTERS, [ ] )
            for filter_ in filters:
                self.filters.append(
                    Filter(
                        filter_[ IndicatorPPADownloadStatistics.COLUMN_USER ],
                        filter_[ IndicatorPPADownloadStatistics.COLUMN_NAME ],
                        filter_[ IndicatorPPADownloadStatistics.COLUMN_SERIES ],
                        filter_[ IndicatorPPADownloadStatistics.COLUMN_ARCHITECTURE ],
                        filter_[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ] ) )


#TODO
            '''
            {"combinePPAs": false, "filters": [["canonical-kernel-team", "ppa", ["linux-image-oem"]]], "ignoreVersionArchitectureSpecific": true, "lowBandwidth": false, "ppas": [["thebernmeister", "ppa", "jammy", "amd64"],["canonical-kernel-team","ppa","focal","amd64"],["thebernmeister", "ppa", "focal", "amd64"]], "showSubmenu": false, "sortByDownload": false, "sortByDownloadAmount": 5, "version": "1.0.81", "checklatestversion": false}


            {"combinePPAs": false, "filters": [["thebernmeister", "ppa", "jammy", "amd64", ["indicator-fortune", "indicator-lunar", "indicator-on-this-day", "indicator-ppa-download-statistics", "indicator-punycode", "indicator-script-runner", "indicator-stardate", "indicator-tide", "indicator-virtual-box"]]], "ignoreVersionArchitectureSpecific": true, "lowBandwidth": false, "ppas": [["thebernmeister", "ppa", "jammy", "amd64"]], "showSubmenu": false, "sortByDownload": false, "sortByDownloadAmount": 5, "version": "1.0.80"}


{"combinePPAs": false, "filters": [["canonical-kernel-team", "ppa", "focal", "amd64", ["linux-image-oem"]]], "ignoreVersionArchitectureSpecific": true, "lowBandwidth": false, "ppas": [["thebernmeister", "ppa", "jammy", "amd64"],["thebernmeister", "ppa", "jammy", "i386"],["thebernmeister", "ppa", "focal", "amd64"],["thebernmeister", "ppa", "focal", "i386"],["thebernmeister", "archive", "focal", "i386"],["thebernmeister", "testing", "focal", "i386"],["thebernmeister", "ppa", "focal", "amd64"],["thebernmeister", "ppa", "jammy", "i386"],["thebernmeister", "ppa", "focal", "i386"],["cubic-wizard", "release", "focal", "amd64"],["cloud-it", "ppa", "focal", "amd64"],["ppa-q", "ppa", "focal", "amd64"],["aggelalex-ppa", "ppa", "focal", "amd64"]], "showSubmenu": false, "sortByDownload": false, "sortByDownloadAmount": 5, "version": "1.0.81", "checklatestversion": false}

            '''

            #TODO Test with empty data.
            # self.ppas = [ ]
            # self.filters = [ ]
            self.combine_ppas = True
            self.show_submenu = True
#,["canonical-kernel-team","ppa","focal","amd64"]

        else:
#TODO Once Ubuntu 20.04 is EOL,
# should really find an alternate default/example PPA and filter.
            user = "thebernmeister"
            name = "ppa"
            series = "jammy"
            architecture = "amd64"

            self.ppas = [ PPA( user, name, series, architecture ) ]

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

            self.filters = [
                Filter( user, name, series, architecture, filter_text ) ]


    def save_config( self ):
        ppas = [ ]
        for ppa in self.ppas:
            ppas.append( [
                ppa.get_user(),
                ppa.get_name(),
                ppa.get_series(),
                ppa.get_architecture() ] )

        filters = [ ]
        for filter_ in self.filters:
            filters.append( [
                filter_.get_user(),
                filter_.get_name(),
                filter_.get_series(),
                filter_.get_architecture(),
                filter_.get_text() ] )

        return {
            IndicatorPPADownloadStatistics.CONFIG_COMBINE_PPAS: self.combine_ppas,
            IndicatorPPADownloadStatistics.CONFIG_FILTERS: filters,
            IndicatorPPADownloadStatistics.CONFIG_IGNORE_VERSION_ARCHITECTURE_SPECIFIC: self.ignore_version_architecture_specific,
            IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH: self.low_bandwidth,
            IndicatorPPADownloadStatistics.CONFIG_PPAS: ppas,
            IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU: self.show_submenu,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD: self.sort_by_download,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT: self.sort_by_download_amount
        }


IndicatorPPADownloadStatistics().main()
