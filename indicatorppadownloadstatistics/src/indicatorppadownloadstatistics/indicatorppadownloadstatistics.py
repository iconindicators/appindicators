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


''' Application indicator which displays PPA download statistics. '''


import concurrent.futures
import locale

from packaging.version import Version
from threading import Lock

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from .indicatorbase import IndicatorBase

from .ppa import PPA, PublishedBinary


class IndicatorPPADownloadStatistics( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used when building the wheel to create the .desktop file.
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

    MESSAGE_ERROR_NETWORK = _( "(network error - check the log)" )
    MESSAGE_ERROR_OTHER = _( "(unknown error - check the log)" )
    MESSAGE_ERROR_TIMEOUT = _( "(timeout error - check the log)" )
    MESSAGE_FILTERED = _( "(published binaries completely filtered)" )
    MESSAGE_NO_PUBLISHED_BINARIES = _( "(no published binaries)" )

    UPDATE_PERIOD = 12 * 60 * 60 # 12 hours in seconds.


    def __init__( self ):
        super().__init__(
            comments = _( "Displays the total downloads of PPAs." ) )

        self.preferences_changed = False


    def update(
        self,
        menu ):

        if self.preferences_changed:
            # One or more PPAs were modified in the Preferences;
            # download only those PPAs.
            self.preferences_changed = False

        else:
            # This is a scheduled update; download all PPAs.
            for ppa in self.ppas:
                ppa.set_status( PPA.Status.NEEDS_DOWNLOAD )

        self.download_ppa_statistics()

        ppas_sorted = (
            PPA.sort_ppas_by_user_then_name_then_published_binaries(
                self.ppas,
                self.sort_by_download,
                self.sort_by_download_amount ) )

        if self.show_submenu:
            self._build_submenu( menu, ppas_sorted )

        else:
            self._build_menu( menu, ppas_sorted )

        return IndicatorPPADownloadStatistics.UPDATE_PERIOD


    def _build_submenu(
        self,
        menu,
        ppas_sorted ):

        for ppa in ppas_sorted:
            submenu = Gtk.Menu()
            self.create_and_append_menuitem(
                menu,
                ppa.get_descriptor() ).set_submenu( submenu )

            if ppa.get_status() == PPA.Status.OK:
                published_binaries = ppa.get_published_binaries()
                for published_binary in published_binaries:
                    self.create_and_append_menuitem(
                        submenu,
                        self._get_label( published_binary ),
                        name =
                            self._get_url_for_published_binary(
                                ppa, published_binary ),
                        activate_functionandarguments = (
                            self.get_on_click_menuitem_open_browser_function(), ),
                        indent = ( 1, 0 ) )

            else:
                self.create_and_append_menuitem(
                    submenu,
                    self._get_status_message( ppa ),
                    name = self._get_url_for_ppa( ppa ),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ),
                    indent = ( 1, 1 ) )


    def _build_menu(
        self,
        menu,
        ppas_sorted ):

        for ppa in ppas_sorted:
            self.create_and_append_menuitem(
                menu,
                ppa.get_descriptor(),
                name = self._get_url_for_ppa( ppa ),
                activate_functionandarguments = (
                    self.get_on_click_menuitem_open_browser_function(), ) )

            if ppa.get_status() == PPA.Status.OK:
                published_binaries = ppa.get_published_binaries()
                for published_binary in published_binaries:
                    self.create_and_append_menuitem(
                        menu,
                        self._get_label( published_binary ),
                        name =
                            self._get_url_for_published_binary(
                                ppa, published_binary ),
                        activate_functionandarguments = (
                            self.get_on_click_menuitem_open_browser_function(), ),
                        indent = ( 1, 1 ) )

            else:
                self.create_and_append_menuitem(
                    menu,
                    self._get_status_message( ppa ),
                    name = self._get_url_for_ppa( ppa ),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ),
                    indent = ( 1, 1 ) )

        # When only one PPA is present, enable a middle mouse click on the icon
        # to open the PPA in the browser.
        if len( self.ppas ) == 1:
            self.set_secondary_activate_target( menu.get_children()[ 0 ] )


    def _get_status_message(
        self,
        ppa ):

        if ppa.get_status() == PPA.Status.ERROR_NETWORK:
            message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_NETWORK

        elif ppa.get_status() == PPA.Status.ERROR_OTHER:
            message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_OTHER

        elif ppa.get_status() == PPA.Status.ERROR_TIMEOUT:
            message = IndicatorPPADownloadStatistics.MESSAGE_ERROR_TIMEOUT

        elif ppa.get_status() == PPA.Status.NO_PUBLISHED_BINARIES:
            message = IndicatorPPADownloadStatistics.MESSAGE_NO_PUBLISHED_BINARIES

        elif ppa.get_status() == PPA.Status.FILTERED:
            message = IndicatorPPADownloadStatistics.MESSAGE_FILTERED

        return message


    def _get_label(
        self,
        published_binary ):

        label = (
            published_binary.get_name() +
            ' ' +
            published_binary.get_version() )

        if published_binary.get_architecture() is not None:
            label += f" ({ published_binary.get_architecture() })"

        return label + " :  " + str( published_binary.get_download_count() )


    def _get_url_for_ppa(
        self,
        ppa ):

        user, name = ppa.get_descriptor().split( " | " )
        return f"https://launchpad.net/~{ user }/+archive/ubuntu/{ name }"


    def _get_url_for_published_binary(
        self,
        ppa,
        published_binary ):

        return (
            f"{ self._get_url_for_ppa( ppa ) }/+packages?" +
            f"field.name_filter={ published_binary.get_name() }&"
            f"field.status_filter=published" )


    def download_ppa_statistics( self ):
        '''
        For each PPA's binary packages, get the download count if required.

        References
            https://launchpad.net/+apidoc/devel.html
            http://help.launchpad.net/API/Hacking
        '''
        for ppa in self.ppas:
            if ppa.get_status() == PPA.Status.NEEDS_DOWNLOAD:
                for filter_text in ppa.get_filters():
                    self._process_ppa_with_filter( ppa, filter_text )
                    if ppa.has_status_error():
                        break

                if ppa.has_status_error():
                    ppa.flush_published_binaries()

                elif ppa.has_published_binaries():
                    ppa.set_status( PPA.Status.OK )

                elif ppa.has_default_filter():
                    # No published binaries as there is no filter in place.
                    ppa.set_status( PPA.Status.NO_PUBLISHED_BINARIES )

                else:
                    # No results passed through filtering.
                    ppa.set_status( PPA.Status.FILTERED )


    def _process_ppa_with_filter(
        self,
        ppa,
        filter_text ):

        '''
        Get the published binaries for the PPA, then for each published binary,
        get the download count.

        A filter_text of "" results to no filtering.
        '''
        published_binaries, self_links = (
            self._get_published_binaries( ppa, filter_text ) )

        if not ppa.has_status_error( ignore_other = True ):
            self._get_download_counts( ppa, published_binaries, self_links )


    def _get_published_binaries(
        self,
        ppa,
        filter_text ):

        url = (
            f"https://api.launchpad.net/1.0/~{ ppa.get_user() }" +
            f"/+archive/ubuntu/{ ppa.get_name() }" +
            f"?ws.op=getPublishedBinaries" +
            f"&status=Published" +
            f"&exact_match=false" +
            f"&ordered=false" +
            f"&binary_name={ filter_text }" )

        published_binaries = [ ]
        self_links = [ ]
        next_collection_link = "next_collection_link"
        while True:
            json, error_network, error_timeout = self.get_json( url )
            if error_network:
                ppa.set_status( PPA.Status.ERROR_NETWORK )
                break

            if error_timeout:
                ppa.set_status( PPA.Status.ERROR_TIMEOUT )
                break

            for entry in json[ "entries" ]:
                architecture = None
                if entry[ "architecture_specific" ]:
                    architecture = entry[ "distro_arch_series_link" ]
                    architecture = architecture.split( '/' )[ -1 ]

                published_binary = (
                    PublishedBinary(
                        entry[ "binary_package_name" ],
                        entry[ "binary_package_version" ],
                        architecture ) )

                if published_binary not in published_binaries:
                    published_binaries.append( published_binary )
                    self_links.append( entry[ "self_link" ] )

            if next_collection_link in json:
                url = json[ next_collection_link ]
                continue

            break

        return published_binaries, self_links


    def _get_download_counts(
        self,
        ppa,
        published_binaries,
        self_links ):

        max_workers = 1 if self.low_bandwidth else 3
        futures = [ ]
        lock = Lock()
        with concurrent.futures.ThreadPoolExecutor( max_workers = max_workers ) as executor:
            for published_binary, self_link in zip( published_binaries, self_links ):
                futures.append(
                    executor.submit(
                        self._get_download_count,
                        self_link + "?ws.op=getDownloadCount",
                        published_binary,
                        ppa,
                        lock ) )

        if not ppa.has_status_error( ignore_other = True ):
            for future, published_binary in zip( futures, published_binaries ):
                if future.exception() is not None:
                    ppa.set_status( PPA.Status.ERROR_OTHER )
                    self.get_logging().exception( future.exception() )
                    break


    def _get_download_count(
        self,
        url,
        published_binary,
        ppa,
        lock ):

        with lock:
            error = ppa.has_status_error( ignore_other = True )

        if not error:
            download_count, error_network, error_timeout = self.get_json( url )
            if error_network:
                with lock:
                    ppa.set_status( PPA.Status.ERROR_NETWORK )

            elif error_timeout:
                with lock:
                    ppa.set_status( PPA.Status.ERROR_TIMEOUT )

            else:
                published_binary.set_download_count( download_count )
                ppa.add_published_binary( published_binary )


    def on_preferences(
        self,
        dialog ):

        notebook = Gtk.Notebook()
        notebook.set_margin_bottom( IndicatorBase.INDENT_WIDGET_TOP )

        invalid_ppas = [ ]

        # PPAs.
        grid = self.create_grid()

        store = Gtk.ListStore( str, str, str ) # User, name, filter.
        for ppa in self.ppas:
            store.append( [
                ppa.get_user(),
                ppa.get_name(),
                '\n'.join( ppa.get_filters() ) ] )

        treeview, scrolledwindow = (
            self.create_treeview_within_scrolledwindow(
                store,
                (
                    _( "User" ),
                    _( "Name" ),
                    _( "Filter" ) ),
                (
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorPPADownloadStatistics.COLUMN_USER ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorPPADownloadStatistics.COLUMN_NAME ),
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ) ),
                default_sort_func = self._ppa_sort,
                tooltip_text = _( "Double click to edit a PPA." ),
                rowactivatedfunctionandarguments = (
                    self.on_ppa_double_click, invalid_ppas ) ) )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        box, add, remove = (
            self.create_buttons_in_box(
                (
                    _( "Add" ),
                    _( "Remove" ) ),
                (
                    _( "Add a new PPA." ),
                    _( "Remove the selected PPA." ) ),
                (
                    None,
                    ( self.on_ppa_remove, treeview, invalid_ppas ) ) ) )

        grid.attach( box, 0, 1, 1, 1 )

        add.connect(
            "clicked", self.on_ppa_add, treeview, remove, invalid_ppas )

        if len( store ):
            treepath = Gtk.TreePath.new_from_string( '0' )
            treeview.get_selection().select_path( treepath )
            treeview.set_cursor( treepath, None, False )

        else:
            remove.set_sensitive( False )

        notebook.append_page( grid, Gtk.Label.new( _( "PPAs" ) ) )

        # General settings.
        grid = self.create_grid()

        show_as_submenus_checkbutton = (
            self.create_checkbutton(
                _( "Show PPAs as submenus" ),
                tooltip_text = _(
                    "The download statistics for each PPA\n" +
                    "are shown in a separate submenu." ),
                active = self.show_submenu ) )

        grid.attach( show_as_submenus_checkbutton, 0, 0, 1, 1 )

        sort_by_download_checkbutton = (
            self.create_checkbutton(
                _( "Sort by download" ),
                tooltip_text = _( "Sort by download count within each PPA." ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP,
                active = self.sort_by_download ) )

        grid.attach( sort_by_download_checkbutton, 0, 1, 1, 1 )

        label = Gtk.Label.new( _( "Clip amount" ) )
        label.set_sensitive( sort_by_download_checkbutton.get_active() )

        spinner = (
            self.create_spinbutton(
                self.sort_by_download_amount,
                0,
                10000,
                page_increment = 100,
                tooltip_text = _(
                    "Limit the number of entries\n" +
                    "when sorting by download.\n\n" +
                    "A value of zero will not clip." ),
                sensitive = sort_by_download_checkbutton.get_active() ) )

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

        low_bandwidth_checkbutton = (
            self.create_checkbutton(
                _( "Low bandwidth" ),
                tooltip_text = _(
                    "Enable if your internet connection is slow." ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP,
                active = self.low_bandwidth ) )

        grid.attach( low_bandwidth_checkbutton, 0, 3, 1, 1 )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = (
            self.create_preferences_common_widgets() )

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

            ppas_original = self.ppas
            self.ppas = [ ]
            treeiter = store.get_iter_first()
            while treeiter is not None:
                ppa = store[ treeiter ]
                self.ppas.append(
                    PPA(
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_USER ],
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) )

                filter_text = (
                    ppa[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ] )
                
                self.ppas[ -1 ].set_filters( filter_text.split( '\n' ) )

                treeiter = store.iter_next( treeiter )

            for ppa in self.ppas:
                if ( ppa.get_user(), ppa.get_name() ) not in invalid_ppas:
                    for ppa_original in ppas_original:
                        if self._ppas_are_identical( ppa, ppa_original ):
                            if not ppa_original.has_status_error():
                                # No download required, but need to copy across
                                # the status and published binaries.
                                ppa.set_status( ppa_original.get_status() )
                                for published_binary in ppa_original.get_published_binaries():
                                    ppa.add_published_binary( published_binary )

                            break

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

            self.preferences_changed = True

        return response_type


    def _ppas_are_identical(
        self,
        ppa1,
        ppa2 ):

        users_equal = ppa1.get_user() == ppa2.get_user()
        names_equal = ppa1.get_name() == ppa2.get_name()
        filters_equal = ppa1.get_filters() == ppa2.get_filters()
        return users_equal and names_equal and filters_equal


    def _ppa_sort(
        self,
        model,
        row1,
        row2,
        user_data ):

        return (
            PPA.compare(
                model.get_value(
                    row1,
                    IndicatorPPADownloadStatistics.COLUMN_USER ),
                model.get_value(
                    row1,
                    IndicatorPPADownloadStatistics.COLUMN_NAME ),
                model.get_value(
                    row2,
                    IndicatorPPADownloadStatistics.COLUMN_USER ),
                model.get_value(
                    row2,
                    IndicatorPPADownloadStatistics.COLUMN_NAME ) ) )


    def on_ppa_remove(
        self,
        button,
        treeview,
        invalid_ppas ):

        response = (
            self.show_dialog_ok_cancel(
                treeview, _( "Remove the selected PPA?" ) ) )

        if response == Gtk.ResponseType.OK:
            model, treeiter = treeview.get_selection().get_selected()
            if len( model ) == 1:
                model.remove( treeiter )
                button.set_sensitive( False )

            else:
                treepath = (
                    Gtk.TreePath.new_from_string(
                        model.get_string_from_iter( treeiter ) ) )

                if not treepath.prev():
                    treepath = Gtk.TreePath.new_from_string( '0' )

                treeview.get_selection().select_path( treepath )
                treeview.set_cursor( treepath, None, False )

                model.get_model().remove( treeiter )


    def on_ppa_add(
        self,
        button_add,
        treeview,
        button_remove,
        invalid_ppas ):

        self.on_ppa_double_click( treeview, None, None, invalid_ppas )
        button_remove.set_sensitive( len( treeview.get_model() ) > 0 )


#TODO Compare against fortune...need another function to wrap around this function?
    def on_ppa_double_click(
        self,
        treeview,
        row_number,
        treeviewcolumn,
        invalid_ppas ):

        model, treeiter = treeview.get_selection().get_selected()
        first_ppa = len( model ) == 0
        adding_ppa = row_number is None

        grid = self.create_grid()

        label = Gtk.Label.new( _( "User" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        if first_ppa:
            ppa_user = self.create_entry( "" )

        else:
            ppa_users = [
                row[ IndicatorPPADownloadStatistics.COLUMN_USER ]
                for row in model ]

            ppa_users = list( set( ppa_users ) )
            ppa_users.sort( key = locale.strxfrm )
            if adding_ppa:
                ppa_users.insert( 0, "" )

            ppa_user = (
                self.create_comboboxtext(
                    ppa_users,
                    active =
                        0
                        if adding_ppa else
                        ppa_users.index(
                            model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] ),
                        editable = True ) )

        grid.attach( ppa_user, 1, 0, 1, 1 )

        label = Gtk.Label.new( _( "Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        if first_ppa:
            ppa_name = self.create_entry( "" )

        else:
            ppa_names = [ row[ IndicatorPPADownloadStatistics.COLUMN_NAME ] for row in model ]
            ppa_names = list( set( ppa_names ) )
            ppa_names.sort( key = locale.strxfrm )
            if adding_ppa:
                ppa_names.insert( 0, "" )

            ppa_name = (
                self.create_comboboxtext(
                    ppa_names,
                    active =
                        0
                        if adding_ppa else
                        ppa_names.index(
                            model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] ),
                        editable = True ) )

        grid.attach( ppa_name, 1, 1, 1, 1 )

        label = Gtk.Label.new( _( "Filter" ) )
        label.set_halign( Gtk.Align.START )
        label.set_valign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        textview = (
            self.create_textview(
                text =
                    ""
                    if adding_ppa else
                    model[
                        treeiter ][
                            IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ],
                tooltip_text = _(
                    "Each line of plain text is compared\n" +
                    "against the name of each built package,\n" +
                    "NOT the package name.\n\n" +
                    "If a built package contains ANY part\n" +
                    "of ANY filter, that package will be\n" +
                    "included in the download statistics.\n\n" +
                    "If a timeout error occurs, filtering\n" +
                    "may help by reducing the quantity of\n"
                    "network requests." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( "\n\n\n\n\n" ), False ),
                    ( self.create_scrolledwindow( textview ), True ) ) ),
                     1, 2, 1, 1 )

        title = _( "Edit PPA" )
        if adding_ppa:
            title = _( "Add PPA" )

        dialog = (
            self.create_dialog(
             treeview,
             title,
             content_widget = grid ) )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:
                if first_ppa:
                    user = ppa_user.get_text().strip()
                    name = ppa_name.get_text().strip()

                else:
                    user = ppa_user.get_active_text().strip()
                    name = ppa_name.get_active_text().strip()

                if user == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "User cannot be empty." )  )

                    ppa_user.grab_focus()
                    continue

                if name == "":
                    self.show_dialog_ok(
                        dialog,
                        _( "Name cannot be empty." ) )

                    ppa_name.grab_focus()
                    continue

                if adding_ppa:
                    user_and_name_in_use = (
                        any(
                            row[ IndicatorPPADownloadStatistics.COLUMN_USER ] == user
                            and
                            row[ IndicatorPPADownloadStatistics.COLUMN_NAME ] == name
                            for row in model ) )

                    if user_and_name_in_use:
                        self.show_dialog_ok(
                            dialog,
                            _( "User and name already in use!" ) )

                        continue

                else:
#TODO Shorten
                    user_is_unchanged = (
                        model[
                            treeiter ][
                                IndicatorPPADownloadStatistics.COLUMN_USER ]
                        == user )

                    name_is_unchanged = (
                        model[
                            treeiter ][
                                IndicatorPPADownloadStatistics.COLUMN_NAME ]
                        == name )

                    if not( user_is_unchanged and name_is_unchanged ):
                        user_exists = False
                        name_exists = False
                        for row in model:
                            user_exists = (
                                row[ IndicatorPPADownloadStatistics.COLUMN_USER ] == user )

                            name_exists = (
                                row[ IndicatorPPADownloadStatistics.COLUMN_NAME ] == name )

                            if user_exists and name_exists:
                                break

                        if user_exists and name_exists:
                            self.show_dialog_ok(
                                dialog,
                                _( "User and name already in use!" ) )

                            continue

                # Remove blank lines.
                filter_text = self.get_textview_text( textview ).split( '\n' )
                filter_text = [ f for f in filter_text if f ]

                duplicates_in_filter_text = (
                    len( filter_text ) > len( set( filter_text ) ) )

                if duplicates_in_filter_text:
                    # Could have removed the duplicates using a set().
                    # However, assume the user made a mistake...
                    self.show_dialog_ok(
                        dialog,
                        _( "Filter text may not contain duplicates." ) )

                    continue

                filter_text_contains_a_space = False
                for filter_ in filter_text:
                    if ' ' in filter_:
                        filter_text_contains_a_space = True
                        break

                if filter_text_contains_a_space:
                    self.show_dialog_ok(
                        dialog,
                        _( "Filter text may not contain spaces." ) )

                    continue

                invalid_ppas.append( (
                    model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ],
                    model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) )

                if not adding_ppa:
                    model.remove( treeiter )

                model.append( [ user, name, '\n'.join( filter_text ) ] )
                invalid_ppas.append( ( user, name ) )

                treepath = 0
                for row in model:
                    user_ = row[ IndicatorPPADownloadStatistics.COLUMN_USER ]
                    name_ = row[ IndicatorPPADownloadStatistics.COLUMN_NAME ]
                    if user == user_ and name == name_:
                        break
                
                    treepath += 1
                
                treepath = Gtk.TreePath.new_from_string( str( treepath ) )
                treeview.get_selection().select_path( treepath )
                treeview.set_cursor( treepath, None, False )

            break

        dialog.destroy()


    def _upgrade_1_0_81(
        self,
        ppas,
        filters ):

        # In version 1.0.81, PPAs changed from
        #   user | name | series | architecture
        # to
        #   user | name | filter
        # and filters which had the format
        #   user | name | series | architecture | filter text
        # no longer exist.
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

        for filter_ in filters:
            user = filter_[ 0 ] # Indices of old format.
            name = filter_[ 1 ]
            filter_text = filter_[ 4 ]

            for ppa in self.ppas:
                if ppa.get_name() == name and ppa.get_user() == user:
                    if ppa.has_default_filter():
                        ppa.set_filters( filter_text )

                    else:
                        ppa.set_filters(
                            list(
                                set(
                                    filter_text + ppa.get_filters() ) ) )

                    break

        self.request_save_config( 1 )


    def load_config(
        self,
        config ):

        self.low_bandwidth = (
            config.get(
                IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH,
                False ) )

        self.show_submenu = (
            config.get(
                IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU,
                True ) )

        self.sort_by_download = (
            config.get(
                IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD,
                False ) )

        self.sort_by_download_amount = (
            config.get(
                IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT,
                5 ) )

        ppas = config.get( IndicatorPPADownloadStatistics.CONFIG_PPAS, [ ] )
        self.ppas = [ ]
#TODO CHeck when a 0.0.0 is returned...that is, no .json or a config without a version.
        version_from_config = Version( self.get_version_from_config( config ) )
        if version_from_config < Version( "1.0.81" ):
            self._upgrade_1_0_81( ppas, config.get( "filters", [ ] ) )

        else:
            for ppa in ppas:
                self.ppas.append(
                    PPA(
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_USER ],
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) )

                self.ppas[ -1 ].set_filters(
                    ppa[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ] )

        if len( self.ppas ) == 0:
            self.ppas = [ PPA( "thebernmeister", "ppa" ) ]
            self.ppas[ 0 ].set_filters( [
                "indicator-fortune",
                "indicator-lunar",
                "indicator-on-this-day",
                "indicator-ppa-download-statistics",
                "indicator-punycode",
                "indicator-script-runner",
                "indicator-stardate",
                "indicator-tide",
                "indicator-virtual-box" ] )


    def save_config( self ):
        ppas = [ ]
        for ppa in self.ppas:
            ppas.append( [
                ppa.get_user(),
                ppa.get_name(),
                ppa.get_filters() ] )

        return {
            IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH:
                self.low_bandwidth,

            IndicatorPPADownloadStatistics.CONFIG_PPAS:
                ppas,

            IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU:
                self.show_submenu,

            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD:
                self.sort_by_download,

            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT:
                self.sort_by_download_amount
        }


IndicatorPPADownloadStatistics().main()
