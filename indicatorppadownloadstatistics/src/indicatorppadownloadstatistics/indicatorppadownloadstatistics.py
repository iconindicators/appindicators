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

from threading import Lock

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from indicatorbase import IndicatorBase

from ppa import PPA, PublishedBinary


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


    def update( self, menu ):
        if self.preferences_changed:
            # One or more PPAs were modified in the Preferences;
            # download only those PPAs.
            self.preferences_changed = False

        else:
            # This is a scheduled update; download all PPAs.
            for ppa in self.ppas:
                ppa.set_status( PPA.Status.NEEDS_DOWNLOAD )

        self.download_ppa_statistics()

        ppas_sorted = \
            PPA.sort_ppas_by_user_then_name_then_published_binaries(
                self.ppas, self.sort_by_download, self.sort_by_download_amount )

        if self.show_submenu:
            self.__build_submenu( menu, ppas_sorted )

        else:
            self.__build_menu( menu, ppas_sorted )

        return IndicatorPPADownloadStatistics.UPDATE_PERIOD


    def __build_submenu( self, menu, ppas_sorted ):
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
                        self.__get_label( published_binary ),
                        name = self.__get_url_for_published_binary( ppa, published_binary ),
                        activate_functionandarguments = (
                            self.get_on_click_menuitem_open_browser_function(), ),
                        indent = ( 1, 0 ) )

            else:
                self.create_and_append_menuitem(
                    submenu,
                    self.__get_status_message( ppa ),
                    name = self.__get_url_for_ppa( ppa ),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ),
                    indent = ( 1, 1 ) )


    def __build_menu( self, menu, ppas_sorted ):
        for ppa in ppas_sorted:
            self.create_and_append_menuitem(
                menu,
                ppa.get_descriptor(),
                name = self.__get_url_for_ppa( ppa ),
                activate_functionandarguments = (
                    self.get_on_click_menuitem_open_browser_function(), ) )

            if ppa.get_status() == PPA.Status.OK:
                published_binaries = ppa.get_published_binaries()
                for published_binary in published_binaries:
                    self.create_and_append_menuitem(
                        menu,
                        self.__get_label( published_binary ),
                        name = self.__get_url_for_published_binary( ppa, published_binary ),
                        activate_functionandarguments = (
                            self.get_on_click_menuitem_open_browser_function(), ),
                        indent = ( 1, 1 ) )

            else:
                self.create_and_append_menuitem(
                    menu,
                    self.__get_status_message( ppa ),
                    name = self.__get_url_for_ppa( ppa ),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ),
                    indent = ( 1, 1 ) )

        # When only one PPA is present, enable a middle mouse click on the
        # icon to open the PPA in the browser.
        if len( self.ppas ) == 1:
            self.set_secondary_activate_target( menu.get_children()[ 0 ] )


    def __get_status_message( self, ppa ):
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


    def __get_label( self, published_binary ):
        return (
            published_binary.get_name() + "  " +
            published_binary.get_version() + " :  " +
            str( published_binary.get_download_count() ) )


    def __get_url_for_ppa( self, ppa ):
        user, name = ppa.get_descriptor().split( " | " )
        return f"https://launchpad.net/~{ user }/+archive/ubuntu/{ name }"


    def __get_url_for_published_binary( self, ppa, published_binary ):
        return (
            f"{ self.__get_url_for_ppa( ppa ) }/+packages?" +
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
                print( f"{ ppa }" )#TODO Testing
                for filter_text in ppa.get_filters():
                    print( f"\t{ filter_text }" )#TODO Testing
                    self.__process_ppa_with_filter( ppa, filter_text )#TODO Put back in!
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


    def __process_ppa_with_filter( self, ppa, filter_text ):
        '''
        Get the published binaries for the PPA, then for each published binary,
        get the download count.

        A filter_text of "" results to no filtering.
        '''
        print( "\t\tGetting published binaries..." )#TODO Test
        published_binaries, self_links = \
            self.__get_published_binaries( ppa, filter_text )

        if not ppa.has_status_error( ignore_other = True ):
            print( f"\t\tGetting { len( published_binaries ) } download counts..." )#TODO Test
            self.__get_download_counts( ppa, published_binaries, self_links )


    def __get_published_binaries( self, ppa, filter_text ):
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
        page = 1#TODO Test
        next_collection_link = "next_collection_link"
        while True:
            print( f"\t\t\tGetting page { page }" ) #TODO Test
            print( f"\t\t\t{ url }" )
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
                    architecture = entry[ "distro_arch_series_link" ].split( '/' )[ -1 ]

                published_binary = \
                    PublishedBinary(
                        entry[ "binary_package_name" ],
                        entry[ "binary_package_version" ],
                        architecture )
                    
                print( published_binary )

#TODO Check this works!
                if published_binary not in published_binaries:
                    published_binaries.append( published_binary )
                    self_links.append( entry[ "self_link" ] )

            if next_collection_link in json:
                url = json[ next_collection_link ]
                page += 1#TODO Test
                continue

            break

        return published_binaries, self_links


    def __get_download_counts( self, ppa, published_binaries, self_links ):
        max_workers = 1 if self.low_bandwidth else 3
        futures = [ ]
        lock = Lock()
        with concurrent.futures.ThreadPoolExecutor( max_workers = max_workers ) as executor:
            for published_binary, self_link in zip( published_binaries, self_links ):
                futures.append(
                    executor.submit(
                        self.__get_download_count,
                        self_link + "?ws.op=getDownloadCount",
                        published_binary,
                        ppa,
                        lock ) )

        if not ppa.has_status_error( ignore_other = True ):
            print( "\t\t\t\tPROCESSING RESULTS" )
            for future, published_binary in zip( futures, published_binaries ):
                if future.exception() is None:
                    self.__add_published_binary_to_ppa( published_binary, ppa )

                else:
                    ppa.set_status( PPA.Status.ERROR_OTHER )
                    self.get_logging().exception( future.exception() )
                    break

        print( "DONE" )


    def __get_download_count( self, url, published_binary, ppa, lock ):
        id_ = url.split( '?' )[ 0 ].split( '/' )[ -1 ]
        print( f"\t\t\t\t{ id_ }" )
        with lock:
            error = ppa.has_status_error( ignore_other = True )

        if not error:
            print( f"\t\t\t\t{ id_ } Getting json..." )
            download_count, error_network, error_timeout = self.get_json( url )
            if error_network:
                with lock:
                    ppa.set_status( PPA.Status.ERROR_NETWORK )
                    print( f"\t\t\t\t{ id_ } ERROR NETWORK" )

            elif error_timeout:
                with lock:
                    ppa.set_status( PPA.Status.ERROR_TIMEOUT )
                    print( f"\t\t\t\t{ id_ } ERROR TIMEOUT" )

            else:
                print( f"\t\t\t\t{ id_ } ...done" )
                published_binary.set_download_count( download_count )

        else:
            print( f"\t\t\t\t{ id_ } Aborting" )


    def __add_published_binary_to_ppa( self, published_binary, ppa ):
        print( f"\t\t\t\t\t{ published_binary }" )
        found = False
        for published_binary_ in ppa.get_published_binaries():
            match = (
                published_binary_.get_name() == published_binary.get_name()
                and
                published_binary_.get_version() == published_binary.get_version()
                and
                published_binary_.get_architecture() == published_binary.get_architecture() )

            if match:
                if published_binary_.get_architecture() is not None:
                    published_binary_.set_download_count(
                        published_binary_.get_download_count()
                        +
                        published_binary.get_download_count() )

                found = True
                break

        if not found:
            ppa.add_published_binary( published_binary )


    def on_preferences( self, dialog ):
        notebook = Gtk.Notebook()
        invalid_ppas = [ ]

        # PPAs.
        grid = self.create_grid()

        # PPA user, name, filter.
        ppa_store = Gtk.ListStore( str, str, str )

        for ppa in self.ppas:
            ppa_store.append( [
                ppa.get_user(),
                ppa.get_name(),
                '\n'.join( ppa.get_filters() ) ] )

        treeview, scrolledwindow = \
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
                default_sort_func = self.__ppa_sort,
                tooltip_text = _( "Double click to edit a PPA." ),
                rowactivatedfunctionandarguments = (
                    self.on_ppa_double_click, invalid_ppas ) )

        grid.attach( scrolledwindow, 0, 0, 1, 1 )

        box, add, remove = \
            self.create_buttons_in_box(
                (
                    _( "Add" ),
                    _( "Remove" ) ),
                (
                    _( "Add a new PPA." ),
                    _( "Remove the selected PPA." ) ),
                (
                    None,
                    ( self.on_ppa_remove, treeview, invalid_ppas ) ) )

        grid.attach( box, 0, 1, 1, 1 )

        # Need to pass in the remove button to the add button handler.
        # However, the remove button has not been created at the point
        # the add button is created.
        add.connect( "clicked", self.on_ppa_add, treeview, remove )

        self.__select_first_ppa_or_disable_remove(
            treeview,
            remove )

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

            ppas_original = self.ppas
            self.ppas = [ ]
            treeiter = ppa_store.get_iter_first()
            while treeiter is not None:
                ppa = ppa_store[ treeiter ]
                self.ppas.append(
                    PPA(
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_USER ],
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) )

                self.ppas[ -1 ].set_filters(
                    ppa[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ].split( '\n' ) )

                treeiter = ppa_store.iter_next( treeiter )

            for ppa in self.ppas:
                if ( ppa.get_user(), ppa.get_name() ) not in invalid_ppas:
                    for ppa_original in ppas_original:
                        if self.__ppas_are_identical( ppa, ppa_original ):
                            if not ppa_original.has_status_error():
                                # No download required, but need to copy across the
                                # status and published binaries.
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


    def __ppas_are_identical( self, ppa1, ppa2 ):
        users_equal = ppa1.get_user() == ppa2.get_user()
        names_equal = ppa1.get_name() == ppa2.get_name()
        filters_equal = ppa1.get_filters() == ppa2.get_filters() #TODO Test this!
        return users_equal and names_equal and filters_equal


    def __ppa_sort( self, model, row1, row2, user_data ):
        return \
            PPA.compare_ppas(
                model.get_value(
                    row1, IndicatorPPADownloadStatistics.COLUMN_USER ),
                model.get_value(
                    row1, IndicatorPPADownloadStatistics.COLUMN_NAME ),
                model.get_value(
                    row2, IndicatorPPADownloadStatistics.COLUMN_USER ),
                model.get_value(
                    row2, IndicatorPPADownloadStatistics.COLUMN_NAME ) )


    def __select_first_ppa_or_disable_remove( self, treeview, button_remove ):
        if len( treeview.get_model() ):
            # Select the first ppa.
            treepath_to_select_first_ppa = Gtk.TreePath.new_from_string( "0" )
            treeview.get_selection().select_path( treepath_to_select_first_ppa )
            treeview.scroll_to_cell(
                path = treepath_to_select_first_ppa,
                use_align = False )

        else:
            # No ppas; disable the Remove button.
            button_remove.set_sensitive( False )


    def on_ppa_remove( self, button, treeview, invalid_ppas ):
        model, treeiter = treeview.get_selection().get_selected()
        response = \
            self.show_dialog_ok_cancel(
                treeview,
                _( "Remove the selected PPA?" ) )

        if response == Gtk.ResponseType.OK:
            invalid_ppas.append( (
                model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ],
                model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) )

            model.remove( treeiter )
            self.__select_first_ppa_or_disable_remove( treeview, button )


    def on_ppa_add( self, button_add, treeview, button_remove ):
        length_before_addition = len( treeview.get_model() )
        self.on_ppa_double_click( treeview, None, None, None )
        if len( treeview.get_model() ) > length_before_addition:
            button_remove.set_sensitive( True )


    def on_ppa_double_click(
            self, treeview, row_number, treeviewcolumn, invalid_ppas ):

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
            ppa_users = list( set( [ row[ IndicatorPPADownloadStatistics.COLUMN_USER ] for row in model ] ) )
            ppa_users.sort( key = locale.strxfrm )
            if adding_ppa:
                ppa_users.insert( 0, "" )

            ppa_user = \
                self.create_comboboxtext(
                    ppa_users,
                    active =
                        0
                        if adding_ppa else
                        ppa_users.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] ),
                        editable = True )

        grid.attach( ppa_user, 1, 0, 1, 1 )

        label = Gtk.Label.new( _( "Name" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        if first_ppa:
            ppa_name = self.create_entry( "" )

        else:
            ppa_names = list( set( [ row[ IndicatorPPADownloadStatistics.COLUMN_NAME ] for row in model ] ) )
            ppa_names.sort( key = locale.strxfrm )
            if adding_ppa:
                ppa_names.insert( 0, "" )


            ppa_name = \
                self.create_comboboxtext(
                    ppa_names,
                    active =
                        0
                        if adding_ppa else
                        ppa_names.index( model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] ),
                        editable = True )

        grid.attach( ppa_name, 1, 1, 1, 1 )

        label = Gtk.Label.new( _( "Filter" ) )
        label.set_halign( Gtk.Align.START )
        label.set_valign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        textview = \
            self.create_textview(
                text =
                    ""
                    if adding_ppa else
                    model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ],
                tooltip_text = _(
                    "Each line is plain text and compared\n" +
                    "against the name of each built package,\n" +
                    "NOT the package name.\n\n" +
                    "If a built package contains ANY part\n" +
                    "of ANY filter, that package will be\n" +
                    "included in the download statistics." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( "\n\n\n\n\n" ), False ), # Ensure the textview for the filter text is not too short.
                    ( self.create_scrolledwindow( textview ), True ) ) ),
                     1, 2, 1, 1 )

        title = _( "Edit PPA" )
        if adding_ppa:
            title = _( "Add PPA" )

        dialog = \
            self.create_dialog(
             treeview,
             title,
             content_widget = grid )

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
                    user_is_unchanged = \
                        model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_USER ] == user

                    name_is_unchanged = \
                        model[ treeiter ][ IndicatorPPADownloadStatistics.COLUMN_NAME ] == name

                    if not( user_is_unchanged and name_is_unchanged ):
                        user_exists = False
                        name_exists = False
                        for row in model:
                            user_exists = \
                                row[ IndicatorPPADownloadStatistics.COLUMN_USER ] == user

                            name_exists = \
                                row[ IndicatorPPADownloadStatistics.COLUMN_NAME ] == name

                            if user_exists and name_exists:
                                break

                        if user_exists and name_exists:
                            self.show_dialog_ok(
                                dialog,
                                _( "User and name already in use!" ) )

                            continue

                filter_text = self.get_textview_text( textview ).split( '\n' )
                filter_text = [ f for f in filter_text if f ] # Remove blank lines.

                duplicates_in_filter_text = (
                    len( filter_text ) > len( set( filter_text ) ) )

                if duplicates_in_filter_text:
                    # Could have removed the duplicates using a set().
                    # Assume the user made a mistake...
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

                # Select the added/edited PPA.
                row_iter = treeview.get_model().get_iter_first()
                while iter:
                    user_ = \
                        treeview.get_model().get_value(
                            row_iter, IndicatorPPADownloadStatistics.COLUMN_USER )

                    name_ = \
                        treeview.get_model().get_value(
                            row_iter, IndicatorPPADownloadStatistics.COLUMN_NAME )

                    if user == user_ and name == name_:
                        treepath_for_row = treeview.get_model().get_path( row_iter )
                        treeview.get_selection().select_path( treepath_for_row )
                        treeview.scroll_to_cell(
                            path = treepath_for_row,
                            use_align = False )

                        break

                    row_iter = treeview.get_model().iter_next( row_iter )

            break

        dialog.destroy()


#TODO For testing:
# {"combinePPAs": false, "filters": [["canonical-kernel-team", "ppa", "focal", "amd64", ["linux-image-oem"]], ["thebernmeister", "ppa", "jammy", "amd64", ["lunar","fortune"]], ["thebernmeister", "ppa", "focal", "amd64", ["tide","test"]] ], "ignoreVersionArchitectureSpecific": true, "lowBandwidth": false, "ppas": [["thebernmeister", "ppa", "jammy", "amd64"],["thebernmeister", "ppa", "jammy", "i386"],["thebernmeister", "ppa", "focal", "amd64"],["thebernmeister", "ppa", "focal", "i386"],["thebernmeister", "archive", "focal", "i386"],["thebernmeister", "testing", "focal", "i386"],["thebernmeister", "ppa", "focal", "amd64"],["thebernmeister", "ppa", "jammy", "i386"],["thebernmeister", "ppa", "focal", "i386"],["canonical-kernel-team", "ppa", "focal", "i386"]], "showSubmenu": true, "sortByDownload": false, "sortByDownloadAmount": 5, "version": "1.0.81", "checklatestversion": false}
#
# https://launchpad.net/~mirabilos/+archive/ubuntu/jdk/+packages
# https://launchpad.net/~t-schutter/+archive/ubuntu/ppa/+packages
# https://launchpad.net/~skunk/+archive/ubuntu/pepper-flash/+packages
# https://launchpad.net/~savoury1/+archive/ubuntu/scribus/+packages
# https://launchpad.net/~cafuego/+archive/ubuntu/inkscape/+packages
# https://launchpad.net/~cafuego/+archive/ubuntu/inkscape/+packages
# https://launchpad.net/~csurbhi/+archive/ubuntu/ppa/+packages
# https://launchpad.net/~guido-iodice/+archive/ubuntu/trusty-updates/+packages
# https://launchpad.net/~unity7maintainers/+archive/ubuntu/unity7-desktop/+packages?field.name_filter=&field.status_filter=published&field.series_filter=focal
# https://launchpad.net/~mc3man/+archive/ubuntu/focal6/+packages


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
                            ppa[ IndicatorPPADownloadStatistics.COLUMN_NAME ] ) )

                    self.ppas[ -1 ].set_filters(
                        ppa[ IndicatorPPADownloadStatistics.COLUMN_FILTER_TEXT ] )

            if ppas and len( ppas[ 0 ] ) == 4:
                # In version 81, PPAs changed from
                #   user / name / series / architecture
                # to
                #   user / name / filter
                # and filters which had the format
                #   user / name / series / architecture / filter text
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

                filters = config.get( "filters", [ ] )
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
                                    list( set( filter_text + ppa.get_filters() ) ) )

                            break

            #TODO Testing
            # self.ppas = [ PPA( "canonical-kernel-team", "ppa" ) ]
#            self.ppas = [ PPA( "mirabilos", "jdk" ) ]

            # self.ppas = [ PPA( "thebernmeister", "ppa" ) ]
            self.ppas = [
                PPA( "thebernmeister", "testing" ),
                PPA( "thebernmeister", "archive" ),
                PPA( "thebernmeister", "ppa" ) ]
            # self.ppas = [ PPA( "thebernmeister", "testing" ) ]
            # self.ppas[ -1 ].set_filters( [ "linux-hwe-5.11" ] )
            # self.ppas = [ PPA( "thebernmeister", "archive" ) ]
            # self.ppas = [ ]
            # self.sort_by_download = True
            # self.sort_by_download_amount = 0
            self.show_submenu = True

        else:
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
            IndicatorPPADownloadStatistics.CONFIG_LOW_BANDWIDTH: self.low_bandwidth,
            IndicatorPPADownloadStatistics.CONFIG_PPAS: ppas,
            IndicatorPPADownloadStatistics.CONFIG_SHOW_SUBMENU: self.show_submenu,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD: self.sort_by_download,
            IndicatorPPADownloadStatistics.CONFIG_SORT_BY_DOWNLOAD_AMOUNT: self.sort_by_download_amount
        }


IndicatorPPADownloadStatistics().main()

# libnvidia-common-565
#
# libnvidia-common-565    565.77-0ubuntu0.24.10.1    None    0
# libnvidia-common-565    565.77-0ubuntu0.24.10.1    None    0
# libnvidia-common-565    565.77-0ubuntu0.24.10.1    None    0
# libnvidia-common-565    565.77-0ubuntu0.24.10.1    None    0
# libnvidia-common-565    565.77-0ubuntu0.24.10.1    None    0
# libnvidia-common-565    565.77-0ubuntu0.24.10.1    None    0
# libnvidia-common-565    565.77-0ubuntu0.24.10.1    None    0
#
# libnvidia-common-565-server    565.57.01-0ubuntu0.20.04.2    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.20.04.2    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.20.04.2    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.20.04.2    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.20.04.2    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.20.04.2    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.20.04.2    None    1
#
# libnvidia-common-565-server    565.57.01-0ubuntu0.22.04.4    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.22.04.4    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.22.04.4    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.22.04.4    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.22.04.4    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.22.04.4    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.22.04.4    None    0
#
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.04.3    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.04.3    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.04.3    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.04.3    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.04.3    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.04.3    None    1
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.04.3    None    1
#
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.10.3    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.10.3    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.10.3    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.10.3    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.10.3    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.10.3    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu0.24.10.3    None    0
#
# libnvidia-common-565-server    565.57.01-0ubuntu1    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu1    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu1    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu1    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu1    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu1    None    0
# libnvidia-common-565-server    565.57.01-0ubuntu1    None    0

# linux-generate-oem
#
# linux-generate-oem-5.14    5.14.0-1059.67    amd64    2
#
# linux-generate-oem-5.17    5.17.0-1033.34    amd64    3
#
# linux-generate-oem-6.0    6.0.0-1018.18    amd64    2
#
# linux-generate-oem-6.1    6.1.0-1035.35    amd64    3
#
# linux-generate-oem-6.10    6.10.0-1006.6    amd64    1
#
# linux-generate-oem-6.11    6.11.0-1011.11    amd64    0
#
# linux-generate-oem-6.5    6.5.0-1027.28    amd64    3
#
# linux-generate-oem-6.8    6.8.0-1018.18    amd64    0


# linux-hwe
#
# linux-hwe-5.11-cloud-tools-5.11.0-61    5.11.0-61.61    amd64    1
#
# linux-hwe-5.11-cloud-tools-common    5.11.0-61.61    None    2
# linux-hwe-5.11-cloud-tools-common    5.11.0-61.61    None    2
# linux-hwe-5.11-cloud-tools-common    5.11.0-61.61    None    2
# linux-hwe-5.11-cloud-tools-common    5.11.0-61.61    None    2
# linux-hwe-5.11-cloud-tools-common    5.11.0-61.61    None    2
# linux-hwe-5.11-cloud-tools-common    5.11.0-61.61    None    2
# linux-hwe-5.11-cloud-tools-common    5.11.0-61.61    None    2
#
# linux-hwe-5.11-headers-5.11.0-61    5.11.0-61.61    None    76
# linux-hwe-5.11-headers-5.11.0-61    5.11.0-61.61    None    76
# linux-hwe-5.11-headers-5.11.0-61    5.11.0-61.61    None    76
# linux-hwe-5.11-headers-5.11.0-61    5.11.0-61.61    None    76
# linux-hwe-5.11-headers-5.11.0-61    5.11.0-61.61    None    76
# linux-hwe-5.11-headers-5.11.0-61    5.11.0-61.61    None    76
# linux-hwe-5.11-headers-5.11.0-61    5.11.0-61.61    None    76
#
# linux-hwe-5.11-source-5.11.0    5.11.0-61.61    None    9
# linux-hwe-5.11-source-5.11.0    5.11.0-61.61    None    9
# linux-hwe-5.11-source-5.11.0    5.11.0-61.61    None    9
# linux-hwe-5.11-source-5.11.0    5.11.0-61.61    None    9
# linux-hwe-5.11-source-5.11.0    5.11.0-61.61    None    9
# linux-hwe-5.11-source-5.11.0    5.11.0-61.61    None    9
# linux-hwe-5.11-source-5.11.0    5.11.0-61.61    None    9
#
# linux-hwe-5.11-tools-5.11.0-61    5.11.0-61.61    amd64    10
# linux-hwe-5.11-tools-5.11.0-61    5.11.0-61.61    arm64    0
# linux-hwe-5.11-tools-5.11.0-61    5.11.0-61.61    armhf    1
# linux-hwe-5.11-tools-5.11.0-61    5.11.0-61.61    ppc64el    1
# linux-hwe-5.11-tools-5.11.0-61    5.11.0-61.61    s390x    1
#
# linux-hwe-5.11-tools-common    5.11.0-61.61    None    6
# linux-hwe-5.11-tools-common    5.11.0-61.61    None    6
# linux-hwe-5.11-tools-common    5.11.0-61.61    None    6
# linux-hwe-5.11-tools-common    5.11.0-61.61    None    6
# linux-hwe-5.11-tools-common    5.11.0-61.61    None    6
# linux-hwe-5.11-tools-common    5.11.0-61.61    None    6
# linux-hwe-5.11-tools-common    5.11.0-61.61    None    6
#
# linux-hwe-5.11-tools-host    5.11.0-61.61    None    2
# linux-hwe-5.11-tools-host    5.11.0-61.61    None    2
# linux-hwe-5.11-tools-host    5.11.0-61.61    None    2
# linux-hwe-5.11-tools-host    5.11.0-61.61    None    2
# linux-hwe-5.11-tools-host    5.11.0-61.61    None    2
# linux-hwe-5.11-tools-host    5.11.0-61.61    None    2
# linux-hwe-5.11-tools-host    5.11.0-61.61    None    2
#
# linux-hwe-5.11-udebs-generic    5.11.0-61.61    amd64    6
# linux-hwe-5.11-udebs-generic    5.11.0-61.61    arm64    5
# linux-hwe-5.11-udebs-generic    5.11.0-61.61    armhf    4
# linux-hwe-5.11-udebs-generic    5.11.0-61.61    ppc64el    6
# linux-hwe-5.11-udebs-generic    5.11.0-61.61    s390x    6
#
# linux-hwe-5.11-udebs-generic-64k    5.11.0-61.61    arm64    5
#
# linux-hwe-5.11-udebs-generic-lpae    5.11.0-61.61    armhf    5
#
# linux-hwe-5.13-cloud-tools-5.13.0-52    5.13.0-52.59~20.04.1    amd64    5
#
# linux-hwe-5.13-cloud-tools-common    5.13.0-52.59~20.04.1    None    4
# linux-hwe-5.13-cloud-tools-common    5.13.0-52.59~20.04.1    None    4
# linux-hwe-5.13-cloud-tools-common    5.13.0-52.59~20.04.1    None    4
# linux-hwe-5.13-cloud-tools-common    5.13.0-52.59~20.04.1    None    4
# linux-hwe-5.13-cloud-tools-common    5.13.0-52.59~20.04.1    None    4
# linux-hwe-5.13-cloud-tools-common    5.13.0-52.59~20.04.1    None    4
# linux-hwe-5.13-cloud-tools-common    5.13.0-52.59~20.04.1    None    4
#
# linux-hwe-5.13-headers-5.13.0-52    5.13.0-52.59~20.04.1    None    178
# linux-hwe-5.13-headers-5.13.0-52    5.13.0-52.59~20.04.1    None    178
# linux-hwe-5.13-headers-5.13.0-52    5.13.0-52.59~20.04.1    None    178
# linux-hwe-5.13-headers-5.13.0-52    5.13.0-52.59~20.04.1    None    178
# linux-hwe-5.13-headers-5.13.0-52    5.13.0-52.59~20.04.1    None    178
# linux-hwe-5.13-headers-5.13.0-52    5.13.0-52.59~20.04.1    None    178
# linux-hwe-5.13-headers-5.13.0-52    5.13.0-52.59~20.04.1    None    178
#
# linux-hwe-5.13-source-5.13.0    5.13.0-52.59~20.04.1    None    8
# linux-hwe-5.13-source-5.13.0    5.13.0-52.59~20.04.1    None    8
# linux-hwe-5.13-source-5.13.0    5.13.0-52.59~20.04.1    None    8
# linux-hwe-5.13-source-5.13.0    5.13.0-52.59~20.04.1    None    8
# linux-hwe-5.13-source-5.13.0    5.13.0-52.59~20.04.1    None    8
# linux-hwe-5.13-source-5.13.0    5.13.0-52.59~20.04.1    None    8
# linux-hwe-5.13-source-5.13.0    5.13.0-52.59~20.04.1    None    8
#
# linux-hwe-5.13-tools-5.13.0-52    5.13.0-52.59~20.04.1    amd64    12
# linux-hwe-5.13-tools-5.13.0-52    5.13.0-52.59~20.04.1    arm64    1
# linux-hwe-5.13-tools-5.13.0-52    5.13.0-52.59~20.04.1    armhf    1
# linux-hwe-5.13-tools-5.13.0-52    5.13.0-52.59~20.04.1    ppc64el    1
# linux-hwe-5.13-tools-5.13.0-52    5.13.0-52.59~20.04.1    s390x    0
#
# linux-hwe-5.13-tools-common    5.13.0-52.59~20.04.1    None    5
# linux-hwe-5.13-tools-common    5.13.0-52.59~20.04.1    None    5
# linux-hwe-5.13-tools-common    5.13.0-52.59~20.04.1    None    5
# linux-hwe-5.13-tools-common    5.13.0-52.59~20.04.1    None    5
# linux-hwe-5.13-tools-common    5.13.0-52.59~20.04.1    None    5
# linux-hwe-5.13-tools-common    5.13.0-52.59~20.04.1    None    5
# linux-hwe-5.13-tools-common    5.13.0-52.59~20.04.1    None    5
#
# linux-hwe-5.13-tools-host    5.13.0-52.59~20.04.1    None    3
# linux-hwe-5.13-tools-host    5.13.0-52.59~20.04.1    None    3
# linux-hwe-5.13-tools-host    5.13.0-52.59~20.04.1    None    3
# linux-hwe-5.13-tools-host    5.13.0-52.59~20.04.1    None    3
# linux-hwe-5.13-tools-host    5.13.0-52.59~20.04.1    None    3
# linux-hwe-5.13-tools-host    5.13.0-52.59~20.04.1    None    3
# linux-hwe-5.13-tools-host    5.13.0-52.59~20.04.1    None    3
#
# linux-hwe-5.13-udebs-generic    5.13.0-52.59~20.04.1    amd64    6
# linux-hwe-5.13-udebs-generic    5.13.0-52.59~20.04.1    arm64    5
# linux-hwe-5.13-udebs-generic    5.13.0-52.59~20.04.1    armhf    6
# linux-hwe-5.13-udebs-generic    5.13.0-52.59~20.04.1    ppc64el    7
# linux-hwe-5.13-udebs-generic    5.13.0-52.59~20.04.1    s390x    8
#
# linux-hwe-5.13-udebs-generic-64k    5.13.0-52.59~20.04.1    arm64    6
#
# linux-hwe-5.13-udebs-generic-lpae    5.13.0-52.59~20.04.1    armhf    4
#
# linux-hwe-5.15-cloud-tools-5.15.0-127    5.15.0-127.137~20.04.1    amd64    2
#
# linux-hwe-5.15-headers-5.15.0-127    5.15.0-127.137~20.04.1    None    26
# linux-hwe-5.15-headers-5.15.0-127    5.15.0-127.137~20.04.1    None    26
# linux-hwe-5.15-headers-5.15.0-127    5.15.0-127.137~20.04.1    None    26
# linux-hwe-5.15-headers-5.15.0-127    5.15.0-127.137~20.04.1    None    26
# linux-hwe-5.15-headers-5.15.0-127    5.15.0-127.137~20.04.1    None    26
# linux-hwe-5.15-headers-5.15.0-127    5.15.0-127.137~20.04.1    None    26
# linux-hwe-5.15-headers-5.15.0-127    5.15.0-127.137~20.04.1    None    26
#
# linux-hwe-5.15-tools-5.15.0-127    5.15.0-127.137~20.04.1    amd64    3
# linux-hwe-5.15-tools-5.15.0-127    5.15.0-127.137~20.04.1    arm64    0
# linux-hwe-5.15-tools-5.15.0-127    5.15.0-127.137~20.04.1    armhf    0
# linux-hwe-5.15-tools-5.15.0-127    5.15.0-127.137~20.04.1    ppc64el    0
# linux-hwe-5.15-tools-5.15.0-127    5.15.0-127.137~20.04.1    s390x    0
#
# linux-hwe-5.17-cloud-tools-5.17.0-15    5.17.0-15.16~22.04.8    amd64    4
#
# linux-hwe-5.17-cloud-tools-common    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-cloud-tools-common    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-cloud-tools-common    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-cloud-tools-common    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-cloud-tools-common    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-cloud-tools-common    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-cloud-tools-common    5.17.0-15.16~22.04.8    None    4
#
# linux-hwe-5.17-headers-5.17.0-15    5.17.0-15.16~22.04.8    None    107
# linux-hwe-5.17-headers-5.17.0-15    5.17.0-15.16~22.04.8    None    107
# linux-hwe-5.17-headers-5.17.0-15    5.17.0-15.16~22.04.8    None    107
# linux-hwe-5.17-headers-5.17.0-15    5.17.0-15.16~22.04.8    None    107
# linux-hwe-5.17-headers-5.17.0-15    5.17.0-15.16~22.04.8    None    107
# linux-hwe-5.17-headers-5.17.0-15    5.17.0-15.16~22.04.8    None    107
# linux-hwe-5.17-headers-5.17.0-15    5.17.0-15.16~22.04.8    None    107
#
# linux-hwe-5.17-tools-5.17.0-15    5.17.0-15.16~22.04.8    amd64    12
# linux-hwe-5.17-tools-5.17.0-15    5.17.0-15.16~22.04.8    arm64    0
# linux-hwe-5.17-tools-5.17.0-15    5.17.0-15.16~22.04.8    armhf    0
# linux-hwe-5.17-tools-5.17.0-15    5.17.0-15.16~22.04.8    ppc64el    0
# linux-hwe-5.17-tools-5.17.0-15    5.17.0-15.16~22.04.8    s390x    0
#
# linux-hwe-5.17-tools-common    5.17.0-15.16~22.04.8    None    6
# linux-hwe-5.17-tools-common    5.17.0-15.16~22.04.8    None    6
# linux-hwe-5.17-tools-common    5.17.0-15.16~22.04.8    None    6
# linux-hwe-5.17-tools-common    5.17.0-15.16~22.04.8    None    6
# linux-hwe-5.17-tools-common    5.17.0-15.16~22.04.8    None    6
# linux-hwe-5.17-tools-common    5.17.0-15.16~22.04.8    None    6
# linux-hwe-5.17-tools-common    5.17.0-15.16~22.04.8    None    6
#
# linux-hwe-5.17-tools-host    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-tools-host    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-tools-host    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-tools-host    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-tools-host    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-tools-host    5.17.0-15.16~22.04.8    None    4
# linux-hwe-5.17-tools-host    5.17.0-15.16~22.04.8    None    4
#
# linux-hwe-5.19-cloud-tools-5.19.0-45    5.19.0-45.46~22.04.1    amd64    1
#
# linux-hwe-5.19-cloud-tools-common    5.19.0-45.46~22.04.1    None    1
# linux-hwe-5.19-cloud-tools-common    5.19.0-45.46~22.04.1    None    1
# linux-hwe-5.19-cloud-tools-common    5.19.0-45.46~22.04.1    None    1
# linux-hwe-5.19-cloud-tools-common    5.19.0-45.46~22.04.1    None    1
# linux-hwe-5.19-cloud-tools-common    5.19.0-45.46~22.04.1    None    1
# linux-hwe-5.19-cloud-tools-common    5.19.0-45.46~22.04.1    None    1
# linux-hwe-5.19-cloud-tools-common    5.19.0-45.46~22.04.1    None    1
#
# linux-hwe-5.19-headers-5.19.0-45    5.19.0-45.46~22.04.1    None    120
# linux-hwe-5.19-headers-5.19.0-45    5.19.0-45.46~22.04.1    None    120
# linux-hwe-5.19-headers-5.19.0-45    5.19.0-45.46~22.04.1    None    120
# linux-hwe-5.19-headers-5.19.0-45    5.19.0-45.46~22.04.1    None    120
# linux-hwe-5.19-headers-5.19.0-45    5.19.0-45.46~22.04.1    None    120
# linux-hwe-5.19-headers-5.19.0-45    5.19.0-45.46~22.04.1    None    120
# linux-hwe-5.19-headers-5.19.0-45    5.19.0-45.46~22.04.1    None    120
#
# linux-hwe-5.19-tools-5.19.0-45    5.19.0-45.46~22.04.1    amd64    5
# linux-hwe-5.19-tools-5.19.0-45    5.19.0-45.46~22.04.1    arm64    1
# linux-hwe-5.19-tools-5.19.0-45    5.19.0-45.46~22.04.1    armhf    1
# linux-hwe-5.19-tools-5.19.0-45    5.19.0-45.46~22.04.1    ppc64el    1
# linux-hwe-5.19-tools-5.19.0-45    5.19.0-45.46~22.04.1    s390x    1
#
# linux-hwe-5.19-tools-common    5.19.0-45.46~22.04.1    None    4
# linux-hwe-5.19-tools-common    5.19.0-45.46~22.04.1    None    4
# linux-hwe-5.19-tools-common    5.19.0-45.46~22.04.1    None    4
# linux-hwe-5.19-tools-common    5.19.0-45.46~22.04.1    None    4
# linux-hwe-5.19-tools-common    5.19.0-45.46~22.04.1    None    4
# linux-hwe-5.19-tools-common    5.19.0-45.46~22.04.1    None    4
# linux-hwe-5.19-tools-common    5.19.0-45.46~22.04.1    None    4
#
# linux-hwe-5.19-tools-host    5.19.0-45.46~22.04.1    None    2
# linux-hwe-5.19-tools-host    5.19.0-45.46~22.04.1    None    2
# linux-hwe-5.19-tools-host    5.19.0-45.46~22.04.1    None    2
# linux-hwe-5.19-tools-host    5.19.0-45.46~22.04.1    None    2
# linux-hwe-5.19-tools-host    5.19.0-45.46~22.04.1    None    2
# linux-hwe-5.19-tools-host    5.19.0-45.46~22.04.1    None    2
# linux-hwe-5.19-tools-host    5.19.0-45.46~22.04.1    None    2
#
# linux-hwe-5.8-cloud-tools-5.8.0-67    5.8.0-67.75    amd64    2
#
# linux-hwe-5.8-cloud-tools-common    5.8.0-67.75    None    5
# linux-hwe-5.8-cloud-tools-common    5.8.0-67.75    None    5
# linux-hwe-5.8-cloud-tools-common    5.8.0-67.75    None    5
# linux-hwe-5.8-cloud-tools-common    5.8.0-67.75    None    5
# linux-hwe-5.8-cloud-tools-common    5.8.0-67.75    None    5
# linux-hwe-5.8-cloud-tools-common    5.8.0-67.75    None    5
# linux-hwe-5.8-cloud-tools-common    5.8.0-67.75    None    5
#
# linux-hwe-5.8-headers-5.8.0-67    5.8.0-67.75    None    86
# linux-hwe-5.8-headers-5.8.0-67    5.8.0-67.75    None    86
# linux-hwe-5.8-headers-5.8.0-67    5.8.0-67.75    None    86
# linux-hwe-5.8-headers-5.8.0-67    5.8.0-67.75    None    86
# linux-hwe-5.8-headers-5.8.0-67    5.8.0-67.75    None    86
# linux-hwe-5.8-headers-5.8.0-67    5.8.0-67.75    None    86
# linux-hwe-5.8-headers-5.8.0-67    5.8.0-67.75    None    86
#
# linux-hwe-5.8-source-5.8.0    5.8.0-67.75    None    15
# linux-hwe-5.8-source-5.8.0    5.8.0-67.75    None    15
# linux-hwe-5.8-source-5.8.0    5.8.0-67.75    None    15
# linux-hwe-5.8-source-5.8.0    5.8.0-67.75    None    15
# linux-hwe-5.8-source-5.8.0    5.8.0-67.75    None    15
# linux-hwe-5.8-source-5.8.0    5.8.0-67.75    None    15
# linux-hwe-5.8-source-5.8.0    5.8.0-67.75    None    15
#
# linux-hwe-5.8-tools-5.8.0-67    5.8.0-67.75    amd64    18
# linux-hwe-5.8-tools-5.8.0-67    5.8.0-67.75    arm64    1
# linux-hwe-5.8-tools-5.8.0-67    5.8.0-67.75    armhf    1
# linux-hwe-5.8-tools-5.8.0-67    5.8.0-67.75    ppc64el    1
# linux-hwe-5.8-tools-5.8.0-67    5.8.0-67.75    s390x    1
#
# linux-hwe-5.8-tools-common    5.8.0-67.75    None    10
# linux-hwe-5.8-tools-common    5.8.0-67.75    None    10
# linux-hwe-5.8-tools-common    5.8.0-67.75    None    10
# linux-hwe-5.8-tools-common    5.8.0-67.75    None    10
# linux-hwe-5.8-tools-common    5.8.0-67.75    None    10
# linux-hwe-5.8-tools-common    5.8.0-67.75    None    10
# linux-hwe-5.8-tools-common    5.8.0-67.75    None    10
#
# linux-hwe-5.8-tools-host    5.8.0-67.75    None    6
# linux-hwe-5.8-tools-host    5.8.0-67.75    None    6
# linux-hwe-5.8-tools-host    5.8.0-67.75    None    6
# linux-hwe-5.8-tools-host    5.8.0-67.75    None    6
# linux-hwe-5.8-tools-host    5.8.0-67.75    None    6
# linux-hwe-5.8-tools-host    5.8.0-67.75    None    6
# linux-hwe-5.8-tools-host    5.8.0-67.75    None    6
#
# linux-hwe-5.8-udebs-generic    5.8.0-67.75    amd64    6
# linux-hwe-5.8-udebs-generic    5.8.0-67.75    arm64    4
# linux-hwe-5.8-udebs-generic    5.8.0-67.75    armhf    8
# linux-hwe-5.8-udebs-generic    5.8.0-67.75    ppc64el    4
# linux-hwe-5.8-udebs-generic    5.8.0-67.75    s390x    5
#
# linux-hwe-5.8-udebs-generic-64k    5.8.0-67.75    arm64    6
#
# linux-hwe-5.8-udebs-generic-lpae    5.8.0-67.75    armhf    4
#
# linux-hwe-6.11-cloud-tools-6.11.0-12    6.11.0-12.13~24.04.1    amd64    1
#
# linux-hwe-6.11-headers-6.11.0-12    6.11.0-12.13~24.04.1    None    25
# linux-hwe-6.11-headers-6.11.0-12    6.11.0-12.13~24.04.1    None    25
# linux-hwe-6.11-headers-6.11.0-12    6.11.0-12.13~24.04.1    None    25
# linux-hwe-6.11-headers-6.11.0-12    6.11.0-12.13~24.04.1    None    25
# linux-hwe-6.11-headers-6.11.0-12    6.11.0-12.13~24.04.1    None    25
# linux-hwe-6.11-headers-6.11.0-12    6.11.0-12.13~24.04.1    None    25
# linux-hwe-6.11-headers-6.11.0-12    6.11.0-12.13~24.04.1    None    25
#
# linux-hwe-6.11-lib-rust-6.11.0-12-generic    6.11.0-12.13~24.04.1    amd64    1
#
# linux-hwe-6.11-tools-6.11.0-12    6.11.0-12.13~24.04.1    amd64    17
# linux-hwe-6.11-tools-6.11.0-12    6.11.0-12.13~24.04.1    arm64    0
# linux-hwe-6.11-tools-6.11.0-12    6.11.0-12.13~24.04.1    armhf    0
# linux-hwe-6.11-tools-6.11.0-12    6.11.0-12.13~24.04.1    ppc64el    0
# linux-hwe-6.11-tools-6.11.0-12    6.11.0-12.13~24.04.1    s390x    0
#
# linux-hwe-6.2-cloud-tools-6.2.0-39    6.2.0-39.40~22.04.1    amd64    3
#
# linux-hwe-6.2-cloud-tools-common    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-cloud-tools-common    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-cloud-tools-common    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-cloud-tools-common    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-cloud-tools-common    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-cloud-tools-common    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-cloud-tools-common    6.2.0-39.40~22.04.1    None    2
#
# linux-hwe-6.2-headers-6.2.0-39    6.2.0-39.40~22.04.1    None    87
# linux-hwe-6.2-headers-6.2.0-39    6.2.0-39.40~22.04.1    None    87
# linux-hwe-6.2-headers-6.2.0-39    6.2.0-39.40~22.04.1    None    87
# linux-hwe-6.2-headers-6.2.0-39    6.2.0-39.40~22.04.1    None    87
# linux-hwe-6.2-headers-6.2.0-39    6.2.0-39.40~22.04.1    None    87
# linux-hwe-6.2-headers-6.2.0-39    6.2.0-39.40~22.04.1    None    87
# linux-hwe-6.2-headers-6.2.0-39    6.2.0-39.40~22.04.1    None    87
#
# linux-hwe-6.2-tools-6.2.0-39    6.2.0-39.40~22.04.1    amd64    3
# linux-hwe-6.2-tools-6.2.0-39    6.2.0-39.40~22.04.1    arm64    0
# linux-hwe-6.2-tools-6.2.0-39    6.2.0-39.40~22.04.1    armhf    0
# linux-hwe-6.2-tools-6.2.0-39    6.2.0-39.40~22.04.1    ppc64el    0
# linux-hwe-6.2-tools-6.2.0-39    6.2.0-39.40~22.04.1    s390x    0
#
# linux-hwe-6.2-tools-common    6.2.0-39.40~22.04.1    None    4
# linux-hwe-6.2-tools-common    6.2.0-39.40~22.04.1    None    4
# linux-hwe-6.2-tools-common    6.2.0-39.40~22.04.1    None    4
# linux-hwe-6.2-tools-common    6.2.0-39.40~22.04.1    None    4
# linux-hwe-6.2-tools-common    6.2.0-39.40~22.04.1    None    4
# linux-hwe-6.2-tools-common    6.2.0-39.40~22.04.1    None    4
# linux-hwe-6.2-tools-common    6.2.0-39.40~22.04.1    None    4
#
# linux-hwe-6.2-tools-host    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-tools-host    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-tools-host    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-tools-host    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-tools-host    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-tools-host    6.2.0-39.40~22.04.1    None    2
# linux-hwe-6.2-tools-host    6.2.0-39.40~22.04.1    None    2
#
# linux-hwe-6.5-cloud-tools-6.5.0-44    6.5.0-44.44~22.04.1    amd64    0
#
# linux-hwe-6.5-cloud-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-cloud-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-cloud-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-cloud-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-cloud-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-cloud-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-cloud-tools-common    6.5.0-44.44~22.04.1    None    0
#
# linux-hwe-6.5-headers-6.5.0-44    6.5.0-44.44~22.04.1    None    79
# linux-hwe-6.5-headers-6.5.0-44    6.5.0-44.44~22.04.1    None    79
# linux-hwe-6.5-headers-6.5.0-44    6.5.0-44.44~22.04.1    None    79
# linux-hwe-6.5-headers-6.5.0-44    6.5.0-44.44~22.04.1    None    79
# linux-hwe-6.5-headers-6.5.0-44    6.5.0-44.44~22.04.1    None    79
# linux-hwe-6.5-headers-6.5.0-44    6.5.0-44.44~22.04.1    None    79
# linux-hwe-6.5-headers-6.5.0-44    6.5.0-44.44~22.04.1    None    79
#
# linux-hwe-6.5-tools-6.5.0-44    6.5.0-44.44~22.04.1    amd64    7
# linux-hwe-6.5-tools-6.5.0-44    6.5.0-44.44~22.04.1    arm64    0
# linux-hwe-6.5-tools-6.5.0-44    6.5.0-44.44~22.04.1    armhf    0
# linux-hwe-6.5-tools-6.5.0-44    6.5.0-44.44~22.04.1    ppc64el    0
# linux-hwe-6.5-tools-6.5.0-44    6.5.0-44.44~22.04.1    s390x    0
#
# linux-hwe-6.5-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-common    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-common    6.5.0-44.44~22.04.1    None    0
#
# linux-hwe-6.5-tools-host    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-host    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-host    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-host    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-host    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-host    6.5.0-44.44~22.04.1    None    0
# linux-hwe-6.5-tools-host    6.5.0-44.44~22.04.1    None    0
#
# linux-hwe-6.8-cloud-tools-6.8.0-50    6.8.0-50.51~22.04.1    amd64    0
#
# linux-hwe-6.8-headers-6.8.0-50    6.8.0-50.51~22.04.1    None    90
# linux-hwe-6.8-headers-6.8.0-50    6.8.0-50.51~22.04.1    None    90
# linux-hwe-6.8-headers-6.8.0-50    6.8.0-50.51~22.04.1    None    90
# linux-hwe-6.8-headers-6.8.0-50    6.8.0-50.51~22.04.1    None    90
# linux-hwe-6.8-headers-6.8.0-50    6.8.0-50.51~22.04.1    None    90
# linux-hwe-6.8-headers-6.8.0-50    6.8.0-50.51~22.04.1    None    90
# linux-hwe-6.8-headers-6.8.0-50    6.8.0-50.51~22.04.1    None    90
#
# linux-hwe-6.8-tools-6.8.0-50    6.8.0-50.51~22.04.1    amd64    72
# linux-hwe-6.8-tools-6.8.0-50    6.8.0-50.51~22.04.1    arm64    6
# linux-hwe-6.8-tools-6.8.0-50    6.8.0-50.51~22.04.1    armhf    0
# linux-hwe-6.8-tools-6.8.0-50    6.8.0-50.51~22.04.1    ppc64el    1
# linux-hwe-6.8-tools-6.8.0-50    6.8.0-50.51~22.04.1    s390x    1
