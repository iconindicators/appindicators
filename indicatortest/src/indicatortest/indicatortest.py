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


#TODO On laptop under wayland playing with clipboard, got these log messages:
#
#  2025-07-14 19:28:19,267 - root - ERROR - Error running: wl-paste --primary
#  2025-07-14 19:28:19,267 - root - ERROR - stderr: No selection
#  2025-07-14 19:28:19,268 - root - ERROR - Return code: 1
#  2025-07-14 19:31:59,843 - root - ERROR - Error running: wl-paste --primary
#  2025-07-14 19:31:59,843 - root - ERROR - stderr: No selection
#  2025-07-14 19:31:59,844 - root - ERROR - Return code: 1


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

from .indicatorbase import IndicatorBase


class IndicatorTest( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used in the About dialog and the .desktop file.
    INDICATOR_NAME_HUMAN_READABLE = _( "Indicator Test" )

    # Used in the .desktop file.
    INDICATOR_CATEGORIES = "Categories=Utility"

    CACHE_ICON_BASENAME = "icon-"
    CACHE_ICON_MAXIMUM_AGE_HOURS = 0

    CONFIG_X = "x"

    LABEL = _( "Test Indicator" )


    def __init__( self ):
        super().__init__(
            IndicatorTest.INDICATOR_NAME_HUMAN_READABLE,
            comments = _( "Exercises a range of indicator functionality." ),
            debug = True )

        self.request_mouse_wheel_scroll_events(
            ( self.on_mouse_wheel_scroll, ) )

        self.flush_cache(
            IndicatorTest.CACHE_ICON_BASENAME,
            IndicatorTest.CACHE_ICON_MAXIMUM_AGE_HOURS )


    def update(
        self,
        menu ):
        '''
        Refresh the indicator.
        '''
        self._build_menu( menu )
        self.set_label_or_tooltip( IndicatorTest.LABEL )


    def on_mouse_wheel_scroll(
        self,
        indicator,
        delta,
        scroll_direction ):
        '''
        Change the indicator label to the current
        '''
        self.set_label_or_tooltip( self._get_current_time() )
        print( "Mouse wheel is scrolling..." )


    def _build_menu(
        self,
        menu ):

        self.create_and_append_menuitem( menu, _( "Information" ) )
        self._build_menu_platform_uname( menu )
        self._build_menu_desktop( menu )
        self._build_menu_icon_theme( menu )
        self._build_menu_terminal( menu )

        menu.append( Gtk.SeparatorMenuItem() )

        self.create_and_append_menuitem( menu, _( "Functionality" ) )
        self._build_menu_icon( menu )
        self._build_menu_label_tooltip_osd( menu )
        self._build_menu_execute_command( menu )

        if self.is_clipboard_supported():
            self._build_menu_clipboard( menu )


    def _build_menu_platform_uname(
        self,
        menu ):

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


    def _build_menu_desktop(
        self,
        menu ):

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


    def _build_menu_icon_theme(
        self,
        menu ):

        submenu = Gtk.Menu()

        property_ = "gtk-icon-theme-name"
        label = (
            f"Gtk.Settings().get_default().get_property( \"{ property_ }\" ): "
            +
            Gtk.Settings().get_default().get_property( f"{ property_ }" ) )

        self.create_and_append_menuitem( submenu, label, indent = ( 2, 0 ) )

        command = "gsettings get org.gnome.desktop.interface "

        result = self.process_run( command + "icon-theme" )[ 0 ]
        result = result.replace( '"', '' ).replace( '\'', '' )
        self.create_and_append_menuitem(
            submenu,
            command + "icon-theme: " + result,
            indent = ( 2, 0 ) )

        result = self.process_run( command + "gtk-theme" )[ 0 ]
        result = result.replace( '"', '' ).replace( '\'', '' )
        self.create_and_append_menuitem(
            submenu,
            command + "gtk-theme: " + result,
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Icon Theme" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_terminal(
        self,
        menu ):

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


    def _build_menu_icon(
        self,
        menu ):

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
                                self._get_third_quarter_svg_icon_text(),
                                IndicatorTest.CACHE_ICON_BASENAME,
                                self.EXTENSION_SVG_SYMBOLIC ) ) ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Icon" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_label_tooltip_osd(
        self,
        menu ):

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


    def _build_menu_clipboard(
        self,
        menu ):

        def primary_received_callback_function( text ):
            if text is None:
                print( "No text is highlighted/selected." )

            else:
                print( f"From primary: { text }" )


        submenu = Gtk.Menu()

        self.create_and_append_menuitem(
            submenu,
            _( "Copy from clipboard" ),
            activate_functionandarguments = (
                lambda menuitem:
                    print(
                        f"From clipboard: { self.copy_from_clipboard() }"), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            submenu,
            _( "Copy from primary" ),
            activate_functionandarguments = (
                lambda menuitem:
                    self. copy_from_primary(
                        primary_received_callback_function ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            submenu,
            _( "Copy current time to clipboard" ),
            activate_functionandarguments = (
                lambda menuitem:
                    self.copy_to_clipboard_or_primary(
                        self._get_current_time() ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            submenu,
            _( "Copy current time to primary" ),
            activate_functionandarguments = (
                lambda menuitem:
                    self.copy_to_clipboard_or_primary(
                        self._get_current_time(), is_primary = True ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Clipboard" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_execute_command(
        self,
        menu ):

        submenu = Gtk.Menu()

        labels = [
            "fortune",
            "ls",
            "notify-send" ]

        commands = [
            "fortune",
            "ls -la",
            f"notify-send -i { self.get_icon_name() } 'summary...' 'body...'" ]

        play_sound_complete_command = self.get_play_sound_complete_command()
        if play_sound_complete_command:
            labels.append( "pw-play / paplay" )
            commands.append( play_sound_complete_command )

        if self.is_calendar_supported():
            labels.insert( 0, "calendar" )
            commands.insert(
                0, "calendar -f /usr/share/calendar/calendar.all -A 3" )

        if self.is_session_type_x11():
            labels.append( "wmctrl" )
            commands.append( "wmctrl -l" )

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


    def _get_third_quarter_svg_icon_text( self ):
        ''' Ripped from indicatorlunar to create third quarter. '''
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


    def _execute_command(
        self,
        command ):

        terminal, terminal_execution_flag = (
            self.get_terminal_and_execution_flag() )

        if terminal is None:
            message = _(
                "Cannot run script as no terminal and/or terminal execution "
                "flag found; please install gnome-terminal." )

            self.get_logging().error( message )
            self.show_notification( "Cannot run script", message )

        elif self.is_qterminal_and_broken( terminal ):
            # As a result of
            #    https://github.com/lxqt/qterminal/issues/335
            # the default terminal in Lubuntu (qterminal) fails to parse the
            # arguments.  Although a fix has been made, it is unlikely the
            # repository will be updated any time soon.  The quickest/easiest
            # workaround is to install gnome-terminal.
            message = _(
                "Cannot run script as qterminal incorrectly parses arguments; "
                "please install gnome-terminal instead." )

            self.get_logging().error( message )
            self.show_notification( "Cannot run script", message )

        else:
            command_ = (
                terminal + " " + terminal_execution_flag + " ${SHELL} -c '"
                +
                command
                + "; ${SHELL}" + "'" )

            Thread(
                target = self.process_run,
                args = ( command_, ) ).start()

            print( "Executing command: " + command_ )


    def on_preferences(
        self,
        dialog ):
        '''
        Display preferences.
        '''
        grid = self.create_grid()

        x_checkbutton = (
            self.create_checkbutton(
                _( "Enable/disable X" ),
                tooltip_text = _( "Enable/disable X" ),
                active = self.x ) )

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
        treeview, scrolledwindow = (
            self.create_treeview_within_scrolledwindow(
                store,
                ( _( "Day of Week" ), ),
                ( ( renderer_text_for_column_dayofweek, "text", 0 ), ),
                celldatafunctionandarguments_renderers_columnviewids = (
                    (
                        ( self.data_function, ),
                        renderer_text_for_column_dayofweek, 0 ), ),
                tooltip_text = _(
                    "Days of week containing an 'n' are bold." ) ) )

        grid.attach( scrolledwindow, 0, 1, 1, 10 )

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = (
            self.create_preferences_common_widgets() )

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
        model,
        iter_,
        data ):
        '''
        References
            https://stackoverflow.com/q/52798356/2156453
            https://stackoverflow.com/q/27745585/2156453
            https://stackoverflow.com/q/49836499/2156453
        '''
        cell_renderer.set_property( "weight", Pango.Weight.NORMAL )
        day_of_week = model.get_value( iter_, 0 )
        if 'n' in day_of_week:
            cell_renderer.set_property( "weight", Pango.Weight.BOLD )


    def load_config(
        self,
        config ):
        '''
        Load configuration.
        '''
        self.x = config.get( IndicatorTest.CONFIG_X, True )


    def save_config( self ):
        '''
        Save configuration.
        '''
        return {
            IndicatorTest.CONFIG_X : self.x
        }


IndicatorTest().main()
