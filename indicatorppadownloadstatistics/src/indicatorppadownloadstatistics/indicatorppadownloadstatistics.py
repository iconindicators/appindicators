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


""" Application indicator which displays PPA download statistics. """


import concurrent.futures
import locale

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from indicatorbase import IndicatorBase

from ppa import PPA, PublishedBinary


#TODO Consider putting in a check/limit for published binaries
# with say 25 or more entries.
# Will result in a request for the download count for each...
# Suggest to user in message to use a filter.


#TODO If a user puts in a ppa with a large number of published binaries (pages,
# the user has no way to make a filter to reduce the result as the download will
# take a long time and/or time out and/or crash.
# Maybe do some sort of check and bail out after 10 pages and/or 25 downloads counts?


#TODO Need to handle a timeout:
#
# thebernmeister | ppa | [ test fortune tide lunar ][]
#     test
#         Getting published binaries...
#         Getting page 1
#         Getting 0 download counts...
#     fortune
#         Getting published binaries...
#         Getting page 1
#         Getting 1 download counts...
#     tide
#         Getting published binaries...
#         Getting page 1
#         Getting 1 download counts...
#     lunar
#         Getting published binaries...
#         Getting page 1
# Traceback (most recent call last):
#   File "/home/bernard/Programming/Indicators/indicatorbase/src/indicatorbase/indicatorbase.py", line 591, in _update
#     next_update_in_seconds = self.update( menu )
#   File "/home/bernard/Programming/Indicators/indicatorppadownloadstatistics/src/indicatorppadownloadstatistics/indicatorppadownloadstatistics.py", line 92, in update
#     self.download_ppa_statistics()
#   File "/home/bernard/Programming/Indicators/indicatorppadownloadstatistics/src/indicatorppadownloadstatistics/indicatorppadownloadstatistics.py", line 233, in download_ppa_statistics
#     self.__process_ppa( ppa, filter_text )
#   File "/home/bernard/Programming/Indicators/indicatorppadownloadstatistics/src/indicatorppadownloadstatistics/indicatorppadownloadstatistics.py", line 263, in __process_ppa
#     self.__get_published_binaries( ppa, filter_text )
#   File "/home/bernard/Programming/Indicators/indicatorppadownloadstatistics/src/indicatorppadownloadstatistics/indicatorppadownloadstatistics.py", line 294, in __get_published_binaries
#     published_binaries = self.get_json( url )  #TODO Test with a ppa/archive with NO published binaries....should not get an error...right?
#   File "/home/bernard/Programming/Indicators/indicatorbase/src/indicatorbase/indicatorbase.py", line 285, in get_json
#     with urlopen( url, timeout = IndicatorBase.TIMEOUT_IN_SECONDS * 2 ) as f: #TODO Maybe allow the timeout to be passed in?
#   File "/usr/lib/python3.8/urllib/request.py", line 222, in urlopen
#     return opener.open(url, data, timeout)
#   File "/usr/lib/python3.8/urllib/request.py", line 525, in open
#     response = self._open(req, data)
#   File "/usr/lib/python3.8/urllib/request.py", line 542, in _open
#     result = self._call_chain(self.handle_open, protocol, protocol +
#   File "/usr/lib/python3.8/urllib/request.py", line 502, in _call_chain
#     result = func(*args)
#   File "/usr/lib/python3.8/urllib/request.py", line 1397, in https_open
#     return self.do_open(http.client.HTTPSConnection, req,
#   File "/usr/lib/python3.8/urllib/request.py", line 1358, in do_open
#     r = h.getresponse()
#   File "/usr/lib/python3.8/http/client.py", line 1348, in getresponse
#     response.begin()
#   File "/usr/lib/python3.8/http/client.py", line 316, in begin
#     version, status, reason = self._read_status()
#   File "/usr/lib/python3.8/http/client.py", line 277, in _read_status
#     line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
#   File "/usr/lib/python3.8/socket.py", line 669, in readinto
#     return self._sock.recv_into(b)
#   File "/usr/lib/python3.8/ssl.py", line 1270, in recv_into
#     return self.read(nbytes, buffer)
#   File "/usr/lib/python3.8/ssl.py", line 1128, in read
#     return self._sslobj.read(len, buffer)
# socket.timeout: The read operation timed out


class IndicatorPPADownloadStatistics( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Unused within the indicator; used by build_wheel.py when building
    # the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator PPA Download Statistics" )
    indicator_categories = "Categories=Utility"

    CONFIG_LOW_BANDWIDTH = "lowBandwidth"
    CONFIG_PPAS = "ppas"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_SORT_BY_DOWNLOAD = "sortByDownload"
    CONFIG_SORT_BY_DOWNLOAD_AMOUNT = "sortByDownloadAmount"

    # Data model columns used in the Preferences dialog and json config.
    COLUMN_USER = 0
    COLUMN_NAME = 1
    COLUMN_FILTER_TEXT = 2

    MESSAGE_ERROR_RETRIEVING_PPA = _( "(error retrieving PPA)" )
    MESSAGE_FILTERED = _( "(published binaries completely filtered)" )
    MESSAGE_NO_PUBLISHED_BINARIES = _( "(no published binaries)" )


    def __init__( self ):
        super().__init__(
            comments = _( "Displays the total downloads of PPAs." ) )


    def update( self, menu ):
        self.download_ppa_statistics()

        PPA.sort( self.ppas ) #TODO Check this does what it appears to do...

        if self.sort_by_download:
            for ppa in self.ppas:
                ppa.sort_published_binaries_by_download_count_and_clip(
                    self.sort_by_download_amount )

        if self.show_submenu:
            self.__build_submenu( menu )

        else:
            self.__build_menu( menu )

        return 6 * 60 * 60 # Update every six hours.


    def __build_submenu( self, menu ):
        for ppa in self.ppas:
            submenu = Gtk.Menu()
            self.create_and_append_menuitem(
                menu,
                ppa.get_descriptor() ).set_submenu( submenu )

            if ppa.get_status() == PPA.Status.OK:
                published_binaries = ppa.get_published_binaries( True )
                for published_binary in published_binaries:
                    self.create_and_append_menuitem(
                        submenu,
                        self.__get_label( published_binary ),
                        name = self.__get_url( ppa ),
                        activate_functionandarguments = (
                            self.get_on_click_menuitem_open_browser_function(), ),
                        indent = ( 1, 0 ) )

            else:
                self.create_and_append_menuitem(
                    submenu,
                    self.__get_status_message( ppa ),
                    name = self.__get_url( ppa ),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ),
                    indent = ( 1, 1 ) )


    def __build_menu( self, menu ):
        for ppa in self.ppas:
            self.create_and_append_menuitem(
                menu,
                ppa.get_descriptor(),
                name = self.__get_url( ppa ),
                activate_functionandarguments = (
                    self.get_on_click_menuitem_open_browser_function(), ) )

            if ppa.get_status() == PPA.Status.OK:
                published_binaries = ppa.get_published_binaries( True )
                for published_binary in published_binaries:
                    self.create_and_append_menuitem(
                        menu,
                        self.__get_label( published_binary ),
                        name = self.__get_url( ppa ),
                        activate_functionandarguments = (
                            self.get_on_click_menuitem_open_browser_function(), ),
                        indent = ( 1, 1 ) )

            else:
                self.create_and_append_menuitem(
                    menu,
                    self.__get_status_message( ppa ),
                    name = self.__get_url( ppa ),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ),
                    indent = ( 1, 1 ) )

        # When only one PPA is present, enable a middle mouse click on the
        # icon to open the PPA in the browser.
        if len( self.ppas ) == 1:
            self.set_secondary_activate_target( menu.get_children()[ 0 ] )


    def __get_status_message( self, ppa ):
        if ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA:
            message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_RETRIEVING_PPA

        elif ppa.get_status() == PPA.Status.NO_PUBLISHED_BINARIES:
            message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES

        elif ppa.get_status() == PPA.Status.FILTERED:
            message = IndicatorPPADownloadStatistics.MESSAGE_FILTERED

        return message


    def __get_label( self, published_binary ):
        return (
            published_binary.get_name() + "  " +
            published_binary.get_version() + " :  " +
            str( published_binary.get_download_count() ) )


    def __get_url( self, ppa ):
        user, name = ppa.get_descriptor().split( " | " )
        return f"https://launchpad.net/~{ user }/+archive/ubuntu/{ name }"


    def download_ppa_statistics( self ):
        '''
        For each PPA's binary packages, get the download count.

        References
            https://launchpad.net/+apidoc/devel.html
            http://help.launchpad.net/API/launchpadlib
            http://help.launchpad.net/API/Hacking
        '''
        for ppa in self.ppas:
            ppa.set_status( PPA.Status.NEEDS_DOWNLOAD )

            print( f"{ ppa }" )#TODO Testing
            for filter_text in ppa.get_filter_text():
                print( f"\t{ filter_text }" )#TODO Testing
                self.__process_ppa( ppa, filter_text )#TODO Put back in
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


    def __process_ppa( self, ppa, filter_text ):
        '''
        Get the published binaries for the PPA and then for each published
        binary, get the download count.

        A filter_text of "" equates to no filtering.
        '''

        print( "\t\tGetting published binaries..." )#TODO Test
        self_links, binary_package_names, binary_package_versions, architectures = \
            self.__get_published_binaries( ppa, filter_text )

        if not ppa.get_status() == PPA.Status.ERROR_RETRIEVING_PPA:
            print( f"\t\tGetting { len( self_links ) } download counts..." )#TODO Test
            self.__get_download_counts(
                ppa,
                self_links,
                binary_package_names,
                binary_package_versions,
                architectures )


    def __get_published_binaries( self, ppa, filter_text ):
        url = (
            f"https://api.launchpad.net/1.0/~{ ppa.get_user() }" +
            f"/+archive/ubuntu/{ ppa.get_name() }" +
            f"?ws.op=getPublishedBinaries" +
            f"&status=Published" +
            f"&exact_match=false" +
            f"&ordered=false" +
            f"&binary_name={ filter_text }" )

        self_links = [ ]
        binary_package_names = [ ]
        binary_package_versions = [ ]
        architectures = [ ]

        page = 1#TODO Test
        next_collection_link = "next_collection_link"
        while True:
            print( f"\t\tGetting page { page }" ) #TODO Test
            published_binaries = self.get_json( url )  #TODO Test with a ppa/archive with NO published binaries....should not get an error...right?
            if published_binaries: #TODO If we have multiple pages, will this be None and then set the status to error below?
                for entry in published_binaries[ "entries" ]: #TODO Test for no entries (filter out with bogus indicator name.
                    architecture = None
                    if entry[ "architecture_specific" ] == "true":
                        architecture = entry[ "distro_arch_series_link" ].split( '/' )[ -1 ]

                    published_binary_exists = \
                        self.__published_binary_exists(
                            entry[ "binary_package_name" ],
                            entry[ "binary_package_version" ],
                            architecture,
                            binary_package_names,
                            binary_package_versions,
                            architectures )

                    if not published_binary_exists:
                        self_links.append( entry[ "self_link" ] )
                        binary_package_names.append( entry[ "binary_package_name" ] )
                        binary_package_versions.append( entry[ "binary_package_version" ] )
                        architectures.append( architecture )

                if next_collection_link in published_binaries:
                    url = published_binaries[ next_collection_link ]
                    page += 1#TODO Test
                    continue

                break

            else:
                print( "here" ) #TODO Testing...ensure this is not set when the last published binaries page is downloaded.
                ppa.set_status( PPA.Status.ERROR_RETRIEVING_PPA )
                break

        return self_links, binary_package_names, binary_package_versions, architectures


    def __published_binary_exists(
            self,
            binary_package_name,
            binary_package_version,
            architecture_specific,
            binary_package_names,
            binary_package_versions,
            architecture_specifics ):

        exists_ = False

        zipped = \
            zip(
                binary_package_names,
                binary_package_versions,
                architecture_specifics )

        for name, version, architecture in zipped:
            match = (
                binary_package_name == name
                and
                binary_package_version == version
                and
                architecture_specific == architecture )

            if match:
                exists_ = True
                break

        return exists_


    def __get_download_counts(
            self,
            ppa,
            self_links,
            binary_package_names,
            binary_package_versions,
            architectures ):

        max_workers = 1 if self.low_bandwidth else 3
        download_counts = { }
        with concurrent.futures.ThreadPoolExecutor( max_workers = max_workers ) as executor:
            for i, self_link in enumerate( self_links ):
                download_counts[ i ] = \
                    executor.submit(
                        self.get_json,
                        self_link + "?ws.op=getDownloadCount" )

        for key_i, value_result in download_counts.items():
            if value_result.exception() is None:
                self.__process_download_count(
                    ppa,
                    binary_package_names[ key_i ],
                    binary_package_versions[ key_i ],
                    False if architectures[ key_i ] is None else True,
                    value_result.result() )

            else:
                ppa.set_status( PPA.Status.ERROR_RETRIEVING_PPA )
                break


    def __process_download_count(
            self,
            ppa,
            binary_package_name,
            binary_package_version,
            architecture_specific,
            download_count ):

        found = False
        for published_binary in ppa.get_published_binaries():
            match = (
                binary_package_name == published_binary.get_name()
                and
                binary_package_version == published_binary.get_version()
                and
                architecture_specific == published_binary.get_architecture_specific() )

            if match:
                found = True
                break

        if found:
            if architecture_specific:
                published_binary.set_download_count(
                    published_binary.get_download_count() + download_count )

        else:
            ppa.add_published_binary(
                PublishedBinary(
                    binary_package_name,
                    binary_package_version,
                    architecture_specific,
                    download_count ) )


    def on_preferences( self, dialog ):
        notebook = Gtk.Notebook()

        # PPAs.
        grid = self.create_grid()

        # PPA user, name, filter.
        ppa_store = Gtk.ListStore( str, str, str )

        for ppa in self.ppas:
            ppa_store.append( [
                ppa.get_user(),
                ppa.get_name(),
                '\n'.join( ppa.get_filter_text() ) ] )

        ppa_treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                ppa_store,
                (
                    _( "User" ),
                    _( "Name" ),
                    _( "Filter" ) ),
                (
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_USER ),
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_NAME ),
                    ( Gtk.CellRendererText(), "text", IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ) ),
                tooltip_text = _( "Double click to edit a PPA." ),
                rowactivatedfunctionandarguments = (
                    self.on_ppa_double_click, ) )

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
                    ( self.on_ppa_add, ppa_treeview ),
                    ( self.on_ppa_remove, ppa_treeview ) ) ),
            0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "PPAs" ) ) )

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

        sort_by_download_checkbutton = \
            self.create_checkbutton(
                _( "Sort by download" ),
                tooltip_text = _( "Sort by download count within each PPA." ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP,
                active = self.sort_by_download )

        grid.attach( sort_by_download_checkbutton, 0, 1, 1, 1 )

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
            0, 2, 1, 1 )

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

        grid.attach( low_bandwidth_checkbutton, 0, 3, 1, 1 )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = \
            self.create_preferences_common_widgets()

        grid.attach( box, 0, 4, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.show_submenu = show_as_submenus_checkbutton.get_active()
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
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ].split() ) ) #TODO Check the filter text is correctly saved, etc.

                treeiter = ppa_store.iter_next( treeiter )

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


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


    def on_ppa_add( self, button, treeview ):
        self.on_ppa_double_click( treeview, None, None )


    def on_ppa_double_click(
        self,
        treeview,
        row_number,
        treeviewcolumn ):

        model, treeiter = treeview.get_selection().get_selected()

        grid = self.create_grid()

        label = Gtk.Label.new( _( "User" ) )
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

        label = Gtk.Label.new( _( "Name" ) )
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

        label = Gtk.Label.new( _( "Filter" ) )
        label.set_halign( Gtk.Align.START )
        label.set_valign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        textview = \
            self.create_textview(
                text =
                    model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ],
                    # model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ],  #TODO Try with just this line (as above)...
                    # if row_number else "", #...hopefully don't need this.
                tooltip_text = _(
                    "Each line is a plain text filter which\n" +
                    "is compared against each package name.\n\n" +
                    "If a package name contains ANY part\n" +
                    "of ANY filter, that package will be\n" +
                    "included in the download statistics." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( "\n\n\n\n\n" ), False ), # Ensure the textview for the filter text is not too short.
                    ( self.create_scrolledwindow( textview ), True ) ) ),
                     1, 2, 1, 1 )

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

                if row_number is None and ppa_user_value

                if ppa_name_value == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "PPA name cannot be empty." ) )

                    ppa_name.grab_focus()
                    continue

                if row_number:
                    pass #TODO Edit

                else:
                    pass #TODO Add...ensure the ppa name


#TODO everything below...
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
                            filter_text.get_active_text() == model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ] )

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


#TODO Delete
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


#TODO For testing:
# {"combinePPAs": false, "filters": [["canonical-kernel-team", "ppa", "focal", "amd64", ["linux-image-oem"]], ["thebernmeister", "ppa", "jammy", "amd64", ["lunar","fortune"]], ["thebernmeister", "ppa", "focal", "amd64", ["tide","test"]] ], "ignoreVersionArchitectureSpecific": true, "lowBandwidth": false, "ppas": [["thebernmeister", "ppa", "jammy", "amd64"],["thebernmeister", "ppa", "jammy", "i386"],["thebernmeister", "ppa", "focal", "amd64"],["thebernmeister", "ppa", "focal", "i386"],["thebernmeister", "archive", "focal", "i386"],["thebernmeister", "testing", "focal", "i386"],["thebernmeister", "ppa", "focal", "amd64"],["thebernmeister", "ppa", "jammy", "i386"],["thebernmeister", "ppa", "focal", "i386"],["canonical-kernel-team", "ppa", "focal", "i386"]], "showSubmenu": true, "sortByDownload": false, "sortByDownloadAmount": 5, "version": "1.0.81", "checklatestversion": false}

#TODO When all is sorted out with download and preferences,
# use an old .json from old indicator name with hyphens
# and ensure the old is copied to new location (name without hyphens)
# and loads up.
    def load_config( self, config ):
        self.low_bandwidth = config.get( IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH, False )
        self.show_submenu = config.get( IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU, False )
        self.sort_by_download = config.get( IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD, False )
        self.sort_by_download_amount = config.get( IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT, 5 )

        if config:
            self.ppas = [ ]
            ppas = config.get( IndicatorPPADownloadStatistics.CONFIG_PPAS, [ ] )
            if ppas and len( ppas[ 0 ] ) == 3:
                for ppa in ppas:
                    self.ppas.append(
                        PPA(
                            ppa[ IndicatorPPADownloadStatistics.COLUMN_USER ],
                            ppa[ IndicatorPPADownloadStatistics.COLUMN_NAME ],
                            ppa[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ] ) )

            if ppas and len( ppas[ 0 ] ) == 4:
                # In version 81, PPAs changed from containing
                #   user / name / series / architecture
                # to
                #   user / name / filter
                for ppa in ppas:
                    user = ppa[ IndicatorPPADownloadStatistics.COLUMN_USER ]
                    name = ppa[ IndicatorPPADownloadStatistics.COLUMN_NAME ]

                    no_duplicate_found = True
                    for ppa_ in self.ppas:
                        if ppa_.get_name() == name and ppa_.get_user() == user:
                            no_duplicate_found = False
                            break

                    if no_duplicate_found:
                        self.ppas.append( PPA( user, name ) )

                filters = config.get( "filters", [ ] )
                for filter_ in filters:
                    user = filter_[ 0 ] # Indices of old format.
                    name = filter_[ 1 ]
                    filter_text = filter_[ 4 ]

                    for ppa in self.ppas:
                        if ppa.get_name() == name and ppa.get_user() == user:
                            if len( ppa.get_filter_text()[ 0 ] ) == 0:
                                new_filter_text = filter_text

                            else:
                                new_filter_text = \
                                    list( set( filter_text + ppa.get_filter_text() ) )

                            ppa.set_filter_text( new_filter_text )
                            break

        else:
#TODO Once Ubuntu 20.04 is EOL,
# should really find an alternate default/example PPA and filter.
# https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false&binary_name=linux-image-oem
# https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false&binary_name=linux-image
# https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false&binary_name=linux-image-oem
# https://api.launchpad.net/1.0/~canonical-kernel-team/+archive/ubuntu/ppa?ws.op=getPublishedBinaries&distro_arch_series=https://api.launchpad.net/1.0/ubuntu/focal/amd64&status=Published&exact_match=false&ordered=false

            user = "thebernmeister"
            name = "ppa"
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

            self.ppas = [ PPA( user, name, filter_text ) ]


    def save_config( self ):
        ppas = [ ]
        for ppa in self.ppas:
            ppas.append( [
                ppa.get_user(),
                ppa.get_name(),
                ppa.get_filter_text() ] )

        return {
            IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH: self.low_bandwidth,
            IndicatorPPADownloadStatistics.CONFIG_PPAS: ppas,
            IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU: self.show_submenu,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD: self.sort_by_download,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT: self.sort_by_download_amount
        }


IndicatorPPADownloadStatistics().main()
