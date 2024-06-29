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


# Application indicator which displays tidal information.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import datetime
import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

import importlib.util
from pathlib import Path
import sys


class IndicatorTide( IndicatorBase ):

    CONFIG_SHOW_AS_SUBMENUS = "showAsSubmenus"
    CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY = "showAsSubmenusExceptFirstDay"
    CONFIG_USER_SCRIPT_CLASS_NAME = "userScriptClassName"
    CONFIG_USER_SCRIPT_PATH_AND_FILENAME = "userScriptPathAndFilename"


    def __init__( self ):
        super().__init__(
            comments = _( "Displays tidal information." ) )


    def update( self, menu ):
        if self.user_script_path_and_filename == "" and self.user_script_class_name == "":
            # First time the indicator is run, or really,
            # when there is no preference/json file,
            # there will be no user script specified,
            # so there will be no tidal data,
            # so do not treat this an exception.
            label = _( "No user script specified!" )
            summary = _( "No user script specified!" )
            message = _( "Please specify a user script and class name in the preferences." )
            menu.append( Gtk.MenuItem.new_with_label( label ) )
            self.show_notification( summary, message )

        else:
            tidal_readings = [ ]
            try:
                spec = \
                    importlib.util.spec_from_file_location(
                        self.user_script_class_name,
                        self.user_script_path_and_filename )

                module = importlib.util.module_from_spec( spec )
                sys.modules[ self.user_script_class_name ] = module
                spec.loader.exec_module( module )
                klazz = getattr( module, self.user_script_class_name )
                tidal_readings = \
                    klazz.get_tide_data( 
                        logging = self.get_logging(), 
                        url_timeout_in_seconds = 20 )

                self.build_menu( menu, tidal_readings )

            except FileNotFoundError:
                label = _( "User script could not be found!" )
                summary = _( "User script could not be found!" )
                message = _( "Please check the user script in the preferences." )

            except AttributeError:
                label = _( "User script class name could not be found!" )
                summary = _( "User script class name could not be found!" )
                message = _( "Please check the user script class name in the preferences." )

            except NotImplementedError:
                label = _( "User function could not be found!" )
                summary = _( "User function could not be found!" )
                message = _( "You must implement the function 'get_tide_data()'." )

            except Exception as e:
                self.get_logging().exception( e )
                label = _( "Error running user script!" )
                summary = _( "Error running user script!" )
                message = _( "Check the log file in your home directory." )
                self.get_logging().error(
                    "Error running user script: " + \
                    self.user_script_path_and_filename + " | " + \
                    self.user_script_class_name )

            if not tidal_readings:
                menu.append( Gtk.MenuItem.new_with_label( label ) )
                self.show_notification( summary, message )

        # Update a little after midnight...best guess as to when the user's data source will update.
        today = datetime.datetime.now()
        five_minutes_after_midnight = ( today + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 5, second = 0 )
        return ( five_minutes_after_midnight - today ).total_seconds()


    def build_menu( self, menu, tidal_readings ):
        indent = ""
        self.port_name = tidal_readings[ 0 ].get_location()
        if self.port_name:
            self.create_and_append_menuitem(
                menu,
                self.port_name,
                name = tidal_readings[ 0 ].get_url(),
                activate_functionandarguments = (
                    self.get_on_click_menuitem_open_browser_function(), ) )

            indent = self.get_menu_indent()

        if self.show_as_submenus:
            if self.show_as_submenus_except_first_day:
                first_date_tidal_readings, after_first_date_tidal_readings = \
                    self.__split_tidal_readings_after_first_date( tidal_readings )

                self.__create_menu_flat( first_date_tidal_readings, menu, indent )
                self.__create_menu_sub( after_first_date_tidal_readings, menu, indent )

            else:
                self.__create_menu_sub( tidal_readings, menu, indent )

        else:
            self.__create_menu_flat( tidal_readings, menu, indent )


    def __create_menu_flat( self, tidal_readings, menu, indent ):
        today_date = ""
        for tidal_reading in tidal_readings:
            if today_date != tidal_reading.get_date():
                shown_today = False

            menu_text = \
                indent + self.get_menu_indent() + \
                ( _( "HIGH" ) if tidal_reading.is_high() else _( "LOW" ) ) + "  " + \
                tidal_reading.get_time() + "  " + tidal_reading.get_level()

            if shown_today:
                self.create_and_append_menuitem(
                    menu,
                    menu_text,
                    name = tidal_reading.get_url(),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ) )

            else:
                self.create_and_append_menuitem(
                    menu,
                    indent + tidal_reading.get_date(),
                    name = tidal_reading.get_url(),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ) )

                self.create_and_append_menuitem(
                    menu,
                    menu_text,
                    name = tidal_reading.get_url(),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ) )

                today_date = tidal_reading.get_date()
                shown_today = True


    def __create_menu_sub( self, tidal_readings, menu, indent ):
        today_date = ""
        shown_today = False
        submenu = None # Only declared here to keep the compiler happy.
        for tidal_reading in tidal_readings:
            if today_date != tidal_reading.get_date():
                shown_today = False

            menu_text = \
                indent + self.get_menu_indent() + \
                ( _( "HIGH" ) if tidal_reading.is_high() else _( "LOW" ) ) + "  " + \
                tidal_reading.get_time() + "  " + tidal_reading.get_level()

            if shown_today:
                self.create_and_append_menuitem(
                    submenu,
                    menu_text,
                    name = tidal_reading.get_url(),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ) )

            else:
                submenu = Gtk.Menu()
                self.create_and_append_menuitem(
                    menu,
                    indent + tidal_reading.get_date() ).set_submenu( submenu )

                self.create_and_append_menuitem(
                    submenu,
                    menu_text,
                    name = tidal_reading.get_url(),
                    activate_functionandarguments = (
                        self.get_on_click_menuitem_open_browser_function(), ) )

                today_date = tidal_reading.get_date()
                shown_today = True


    def __split_tidal_readings_after_first_date( self, tidal_readings ):
        first_date_deadings = [ ]
        after_first_date_readings = [ ]
        for tidal_reading in tidal_readings:
            if tidal_reading.get_date() == tidal_readings[ 0 ].get_date():
                first_date_deadings.append( tidal_reading )

            else:
                after_first_date_readings.append( tidal_reading )

        return first_date_deadings, after_first_date_readings


    def on_preferences( self, dialog ):
        grid = self.create_grid()

        # label = Gtk.Label.new( _( "User Script" ) ) #TODO Maybe put into a box?  Look for other haligns below in rest of code.
        # label.set_halign( Gtk.Align.START )
        # grid.attach( label, 0, 0, 1, 1 )
        box = Gtk.Box( spacing = 6 )#TODO Spacing is irrlevant
        box.pack_start( Gtk.Label.new( _( "User Script" ) ), False, False, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True ) # Only need to set this once and all objects will expand.
        box.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label.new( _( "Path and filename" ) ), False, False, 0 )

        user_script_path_and_filename = \
            self.create_entry(
                self.user_script_path_and_filename,
                tooltip_text = _( "Full path and filename\nof user's Python3 script." ) )

        box.pack_start( user_script_path_and_filename, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( IndicatorBase.INDENT_WIDGET_LEFT )

        box.pack_start( Gtk.Label.new( _( "Class name" ) ), False, False, 0 )

        user_script_class_name = \
            self.create_entry(
                self.user_script_class_name,
                tooltip_text = _(
                    "Class name within the user script\n" + \
                    "which must contain the function\n\n" + \
                    "    get_tide_data()\n\n" + \
                    "implemented by the user to obtain\n" + \
                    "the tidal data." ) )

        box.pack_start( user_script_class_name, True, True, 0 )

        box.set_margin_bottom( 10 )

        grid.attach( box, 0, 2, 1, 1 )

        show_as_submenus_checkbutton = \
            self.create_checkbutton(
                _( "Show as submenus" ),
                tooltip_text = _( "Show each day's tides in a submenu." ),
                active = self.show_as_submenus )

        grid.attach( show_as_submenus_checkbutton, 0, 3, 1, 1 )

        show_as_submenus_except_first_day_checkbutton = \
            self.create_checkbutton(
                _( "Except first day" ),
                tooltip_text = _( "Show the first day's tide in full." ),
                sensitive = show_as_submenus_checkbutton.get_active(),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT,
                active = self.show_as_submenus_except_first_day )

        grid.attach( show_as_submenus_except_first_day_checkbutton, 0, 4, 1, 1 )

        show_as_submenus_checkbutton.connect(
            "toggled",
            self.on_radio_or_checkbox,
            True,
            show_as_submenus_except_first_day_checkbutton )

        autostart_checkbox, delay_spinner, box = self.create_autostart_checkbox_and_delay_spinner()
        grid.attach( box, 0, 5, 1, 1 )

        dialog.get_content_area().pack_start( grid, True, True, 0 )
        dialog.show_all()

        while True:
            response_type = dialog.run()
            if response_type == Gtk.ResponseType.OK:
                self.show_as_submenus = show_as_submenus_checkbutton.get_active()
                self.show_as_submenus_except_first_day = show_as_submenus_except_first_day_checkbutton.get_active()

                if user_script_path_and_filename.get_text() and user_script_class_name.get_text():
                    if not Path( user_script_path_and_filename.get_text().strip() ).is_file():
                        self.show_dialog_ok( dialog, _( "The user script path/filename cannot be found." ) )
                        user_script_path_and_filename.grab_focus()
                        continue

                elif user_script_path_and_filename.get_text() or user_script_class_name.get_text(): # Cannot have one empty and the other not.
                    if not user_script_path_and_filename.get_text():
                        self.show_dialog_ok( dialog, _( "The user script path/filename cannot be empty." ) )
                        user_script_path_and_filename.grab_focus()
                        continue

                    else:
                        self.show_dialog_ok( dialog, _( "The user script class name cannot be empty." ) )
                        user_script_class_name.grab_focus()
                        continue

                self.user_script_path_and_filename = user_script_path_and_filename.get_text().strip()
                self.user_script_class_name = user_script_class_name.get_text().strip()

            self.set_autostart_and_delay( autostart_checkbox.get_active(), delay_spinner.get_value_as_int() )
            break

        return response_type


    def load_config( self, config ):
        self.show_as_submenus = \
            config.get(
                IndicatorTide.CONFIG_SHOW_AS_SUBMENUS,
                True )

        self.show_as_submenus_except_first_day = \
            config.get(
                IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY,
                True )

        self.user_script_path_and_filename = \
            config.get(
                IndicatorTide.CONFIG_USER_SCRIPT_PATH_AND_FILENAME,
                "" )

        self.user_script_class_name = \
            config.get(
                IndicatorTide.CONFIG_USER_SCRIPT_CLASS_NAME,
                "" )


    def save_config( self ):
        return {
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS : self.show_as_submenus,
            IndicatorTide.CONFIG_SHOW_AS_SUBMENUS_EXCEPT_FIRST_DAY : self.show_as_submenus_except_first_day,
            IndicatorTide.CONFIG_USER_SCRIPT_CLASS_NAME : self.user_script_class_name,
            IndicatorTide.CONFIG_USER_SCRIPT_PATH_AND_FILENAME : self.user_script_path_and_filename
        }


IndicatorTide().main()
