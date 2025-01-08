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


''' Application indicator to test stuff. '''


import datetime
import os
import platform
import random

from threading import Thread

import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

gi.require_version( "Pango", "1.0" )
from gi.repository import Pango

from indicatorbase import IndicatorBase


class IndicatorTest( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used when building the wheel to create the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Test" )
    indicator_categories = "Categories=Utility"

    CACHE_ICON_BASENAME = "icon-"
    CACHE_ICON_MAXIMUM_AGE_HOURS = 0

    CONFIG_X = "x"

    LABEL = _( "Test Indicator" )


    def __init__( self ):
        super().__init__(
            comments = _( "Exercises a range of indicator functionality." ),
            debug = True )

        self.request_mouse_wheel_scroll_events(
            ( self.on_mouse_wheel_scroll, ) )

        self.flush_cache(
            IndicatorTest.CACHE_ICON_BASENAME,
            IndicatorTest.CACHE_ICON_MAXIMUM_AGE_HOURS )


    def update( self, menu ):
        self._build_menu( menu )
        self.set_label_or_tooltip( IndicatorTest.LABEL )


    def on_mouse_wheel_scroll( self, indicator, delta, scroll_direction ):
        self.set_label_or_tooltip( self._get_current_time() )
        print( "Mouse wheel is scrolling..." )


    def _build_menu( self, menu ):
        self.create_and_append_menuitem( menu, _( "Information" ) )
        self._build_menu_platform_uname( menu )
        self._build_menu_desktop( menu )
        self._build_menu_icon_theme( menu )
        self._build_menu_terminal( menu )

        menu.append( Gtk.SeparatorMenuItem() )

        self.create_and_append_menuitem( menu, _( "Functionality" ) )
        self._build_menu_icon( menu )
        self._build_menu_label_tooltip_osd( menu )
        self._build_menu_clipboard( menu )
        self._build_menu_execute_command( menu )


    def _build_menu_platform_uname( self, menu ):
        submenu = Gtk.Menu()

        uname = platform.uname()
        labels = (
            _( "Machine: " ) + str( uname.machine ),
            _( "Node: " ) + str( uname.node ),
            _( "Processor: " ) + str( uname.processor ),
            _( "Release: " ) + str( uname.release ),
            _( "System: " ) + str( uname.system ),
            _( "Version: " ) + str( uname.version ) )

        for label in labels:
            self.create_and_append_menuitem(
                submenu, label, indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Platform | Uname" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_desktop( self, menu ):
        submenu = Gtk.Menu()

        label = "echo $XDG_CURRENT_DESKTOP" + ": " + self.get_current_desktop()
        self.create_and_append_menuitem( submenu, label, indent = ( 2, 0 ) )

        label = (
            "os.environ.get( 'DESKTOP_SESSION' ): "
            +
            os.environ.get( "DESKTOP_SESSION" ) )

        self.create_and_append_menuitem( submenu, label, indent = ( 2, 0 ) )

        label = "echo $XDG_SESSION_TYPE" + ": " + self.get_session_type()
        self.create_and_append_menuitem( submenu, label, indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Desktop" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_icon_theme( self, menu ):
        submenu = Gtk.Menu()

        property_ = "gtk-icon-theme-name"
        label = (
            f"Gtk.Settings().get_default().get_property( \"{ property_ }\" ): "
            +
            Gtk.Settings().get_default().get_property( f"{ property_ }" ) )

        self.create_and_append_menuitem( submenu, label, indent = ( 2, 0 ) )

        command = "gsettings get org.gnome.desktop.interface "

        result = self.process_get( command + "icon-theme" )
        result = result.replace( '"', '' ).replace( '\'', '' )
        self.create_and_append_menuitem(
            submenu,
            command + "icon-theme: " + result,
            indent = ( 2, 0 ) )

        result = self.process_get( command + "gtk-theme" )
        result = result.replace( '"', '' ).replace( '\'', '' )
        self.create_and_append_menuitem(
            submenu,
            command + "gtk-theme: " + result,
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Icon Theme" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_terminal( self, menu ):
        submenu = Gtk.Menu()

        terminal, execution_flag = self.get_terminal_and_execution_flag()

        self.create_and_append_menuitem(
            submenu,
            _( "Terminal: " ) + _( "Unknown terminal!" )
            if terminal is None
            else
            str( terminal ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            submenu,
            _( "Execution flag: " ) + _( "Unknown terminal!" )
            if terminal is None
            else
            str( execution_flag ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Terminal" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_icon( self, menu ):
        submenu = Gtk.Menu()

        self.create_and_append_menuitem(
            submenu,
            _( "Reset icon" ),
            activate_functionandarguments = (
                lambda menuitem:
                    self.set_icon( self.get_icon_name() ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            submenu,
            "Dynamically created third quarter icon",
            activate_functionandarguments = (
                lambda menuitem:
                    self.set_icon(
                        str(
                            self.write_cache_text(
                                self.__get_third_quarter_svg_icon_text(),
                                IndicatorTest.CACHE_ICON_BASENAME,
                                IndicatorBase.EXTENSION_SVG_SYMBOLIC ) ) ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Icon" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_label_tooltip_osd( self, menu ):
        submenu = Gtk.Menu()

        self.create_and_append_menuitem(
            submenu,
            _( "Reset label" ),
            activate_functionandarguments = (
                lambda menuitem:
                    self.set_label_or_tooltip( IndicatorTest.LABEL ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            submenu,
            _( "Show current time in label" ),
            activate_functionandarguments = (
                lambda menuitem: (
                    print( "secondary activate target / mouse middle click" ),
                    self.set_label_or_tooltip( self._get_current_time() ) ), ),
            indent = ( 2, 0 ),
            is_secondary_activate_target = True )

        self.create_and_append_menuitem(
            submenu,
            _( "Show current time in OSD" ),
            activate_functionandarguments = (
                lambda menuitem:
                    self.show_notification(
                        _( "Current time..." ), self._get_current_time() ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Label | Tooltip | OSD" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_clipboard( self, menu ):
        submenu = Gtk.Menu()

        message_clipboard_unsupported = (
            f"notify-send -i { self.get_icon_name() } "
            +
            "\"Unsupported\" "
            +
            "\"Clipboard unsupported.\"" )

        self.create_and_append_menuitem(
            submenu,
            _( "Copy current time to clipboard" ),
            activate_functionandarguments = (
                lambda menuitem: (
                    self.copy_to_selection(
                        self._get_current_time() )
                    if self.is_clipboard_supported()
                    else
                    self._execute_command( message_clipboard_unsupported ) ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            submenu,
            _( "Copy current time to primary" ),
            activate_functionandarguments = (
                lambda menuitem: (
                    self.copy_to_selection(
                        self._get_current_time(), is_primary = True )
                    if self.is_clipboard_supported()
                    else
                    self._execute_command( message_clipboard_unsupported ) ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Clipboard" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_execute_command( self, menu ):
        submenu = Gtk.Menu()

        labels = (
            "calendar",
            "fortune",
            "ls",
            "notify-send",
            "paplay",
            "wmctrl" )

        commands = (
            "calendar -f /usr/share/calendar/calendar.all -A 3" \
            if self.is_calendar_supported() else \
            f"notify-send -i { self.get_icon_name() } \"Unsupported\" \"The calendar package is unavailable.\"",
            "fortune",
            "ls -la",
            f"notify-send -i { self.get_icon_name() } \"summary 1 2 3\" \"body 4 5 6\"",
            self.get_play_sound_complete_command(),
            f"notify-send -i { self.get_icon_name() } \"Unsupported\" \"Wayland does not support wmctrl.\"" \
            if self.is_session_type_wayland() else \
            "wmctrl -l" )

        for label, command in zip( labels, commands ):
            self.create_and_append_menuitem(
                submenu,
                label,
                activate_functionandarguments = (
                    # Need command = command to handle lambda late binding.
                    lambda menuitem, command = command:
                        self._execute_command( command ), ),
                indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Execute Terminal Command" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _get_current_time( self ):
        return datetime.datetime.now().strftime( "%H:%M:%S" )


#TODO Delete
    def _use_icon_dynamically_created( self, menuitem ):
        icon_path = \
            self.write_cache_text(
                self.__get_third_quarter_svg_icon_text(),
                IndicatorTest.CACHE_ICON_BASENAME,
                IndicatorBase.EXTENSION_SVG_SYMBOLIC )

        self.set_icon( str( icon_path ) )


#TODO Really need this...?  Just need to make one dynamic icon.
    def _get_svg_icon_textOLF(
            self,
            phase,
            illumination_percentage,
            bright_limb_angle_in_degrees ):
        '''
        More or less a direct copy from indicatorlunar to test dynamically
        created SVG icons in the user cache.

        phase
            The current phase of the moon.
        illumination percentage
            The brightness ranging from 0 to 100 inclusive.
            Ignored when phase is full/new or first/third quarter.
        bright limb angle in degrees
            Bright limb angle, relative to zenith, from 0 to 360 inclusive.
            Ignored when phase is full/new.
        '''
        width = 100
        height = width
        radius = float( width / 2 )
        colour = "777777"
        if phase in { "FULL_MOON", "NEW_MOON" }:
            print( "Full new" )
            body = '<circle cx="' + str( width / 2 ) + '" cy="' + str( height / 2 ) + '" r="' + str( radius )
            if phase == "NEW_MOON":
                body += '" fill="#' + colour + '" fill-opacity="0.0" />'

            else: # Full
                body += '" fill="#' + colour + '" />'

        else: # First/Third Quarter or Waning/Waxing Crescent or Waning/Waxing Gibbous
            print( "first third  crescent gibbous" )
            body = \
                '<path d="M ' + str( width / 2 - radius ) + ' ' + str( height / 2 ) + ' ' + \
                'A ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + \
                str( width / 2 + radius ) + ' ' + str( height / 2 )

            if phase in { "FIRST_QUARTER", "THIRD_QUARTER" }:
                body += ' Z"'
                print( "first third" )

            elif phase in { "WANING_CRESCENT", "WAXING_CRESCENT" }:
                print( "crescent" )
                body += \
                    ' A ' + str( radius ) + ' ' + str( radius * ( 50 - illumination_percentage ) / 50 ) + ' 0 0 0 ' + \
                    str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            else: # Waning/Waxing Gibbous
                print( "gibbous" )
                body += \
                    ' A ' + str( radius ) + ' ' + str( radius * ( illumination_percentage - 50 ) / 50 ) + ' 0 0 1 ' + \
                    str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            body += \
                ' transform="rotate(' + str( -bright_limb_angle_in_degrees ) + ' ' + \
                str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="#' + colour + '" />'

        return \
            '<?xml version="1.0" standalone="no"?>' \
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "https://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100" width="22" height="22">' + body + '</svg>'


    def __get_third_quarter_svg_icon_text( self ):
        ''' Inspired from indicatorlunar to create third quarter. '''
        width = 100
        height = width
        radius = float( width / 2 )
        colour = "777777"
        bright_limb_angle_in_degrees = random.randint( 0, 359 )

        body = (
            '<path d="M ' +
            str( width / 2 - radius ) + ' ' +
            str( height / 2 ) + ' ' +
            'A ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' +
            str( width / 2 + radius ) + ' ' + str( height / 2 ) +
            ' Z" ' +
            'transform="rotate(' + str( -bright_limb_angle_in_degrees ) + ' ' +
            str( width / 2 ) + ' ' +
            str( height / 2 ) + ')" fill="#' + colour + '" />' )

        svg = (
            '<?xml version="1.0" standalone="no"?>'
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" ' +
            '"https://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' +
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" ' +
            'viewBox="0 0 100 100" width="22" height="22">' + body + '</svg>' )

        return svg


    def _execute_command( self, command ):
        terminal, terminal_execution_flag = \
            self.get_terminal_and_execution_flag()

        if terminal is None:
            message = _( "Cannot run script as no terminal and/or terminal execution flag found; please install gnome-terminal." )
            self.get_logging().error( message )
            self.show_notification( "Cannot run script", message )

        elif self.is_qterminal_and_broken( terminal ):
            # As a result of
            #    https://github.com/lxqt/qterminal/issues/335
            # the default terminal in Lubuntu (qterminal) fails to parse the
            # arguments.  Although a fix has been made, it is unlikely the
            # repository will be updated any time soon.  The quickest/easiest
            # workaround is to install gnome-terminal.
            message = _( "Cannot run script as qterminal incorrectly parses arguments; please install gnome-terminal instead." )
            self.get_logging().error( message )
            self.show_notification( "Cannot run script", message )

        else:
            command_ = terminal + " " + terminal_execution_flag + " ${SHELL} -c '"
            command_ += command
            command_ += "; ${SHELL}"
            command_ += "'"
            Thread( target = self.process_call, args = ( command_, ) ).start()
            print( "Executing command: " + command_ )


    def on_preferences( self, dialog ):
        grid = self.create_grid()

        x_checkbutton = \
            self.create_checkbutton(
                _( "Enable/disable X" ),
                tooltip_text = _( "Enable/disable X" ),
                active = self.x )

        grid.attach( x_checkbutton, 0, 0, 1, 1 )

        store = Gtk.ListStore( str )
        store.append( [ "Monday" ] )
        store.append( [ "Tuesday" ] )
        store.append( [ "Wednesday" ] )
        store.append( [ "Thursday" ] )
        store.append( [ "Friday" ] )
        store.append( [ "Saturday" ] )
        store.append( [ "Sunday" ] )

        renderer_text_for_column_dayofweek = Gtk.CellRendererText()
        treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                store,
                ( _( "Day of Week" ), ),
                ( ( renderer_text_for_column_dayofweek, "text", 0 ), ),
                celldatafunctionandarguments_renderers_columnviewids = (
                    (
                        ( self.data_function, "" ),
                        renderer_text_for_column_dayofweek, 0 ), ),
                tooltip_text = _( "Days of week containing an 'n' are bold." ) )

        grid.attach( scrolledwindow, 0, 1, 1, 10 )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = \
            self.create_preferences_common_widgets()

        grid.attach( box, 0, 11, 1, 1 )

        dialog.get_content_area().pack_start( grid, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.x = x_checkbutton.get_active()

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


    def data_function(
        self,
        treeviewcolumn,
        cell_renderer,
        tree_model,
        tree_iter,
        data ):
        '''
        References
            https://stackoverflow.com/questions/52798356/python-gtk-treeview-column-data-display
            https://stackoverflow.com/questions/27745585/show-icon-or-color-in-gtk-treeview-tree
            https://stackoverflow.com/questions/49836499/make-only-some-rows-bold-in-a-gtk-treeview
        '''
        cell_renderer.set_property( "weight", Pango.Weight.NORMAL )
        day_of_week = tree_model.get_value( tree_iter, 0 )
        if 'n' in day_of_week:
            cell_renderer.set_property( "weight", Pango.Weight.BOLD )


    def load_config( self, config ):
        self.x = config.get( IndicatorTest.CONFIG_X, True )


    def save_config( self ):
        return {
            IndicatorTest.CONFIG_X : self.x
        }


IndicatorTest().main()
