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


# Application indicator to test stuff.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import datetime
import gi
import os
import platform

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

gi.require_version( "Pango", "1.0" )
from gi.repository import Pango

from threading import Thread


class IndicatorTest( IndicatorBase ):
    # Unused within the indicator; used by build_wheel.py when building the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Test" )

    CACHE_ICON_BASENAME = "icon-"
    CACHE_ICON_MAXIMUM_AGE_HOURS = 0

    CONFIG_X = "x"

    LABEL = _( "Test Indicator" )


    def __init__( self ):
        super().__init__(
            comments = _( "Exercises a range of indicator functionality." ),
            debug = True )

        self.request_mouse_wheel_scroll_events( ( self.on_mouse_wheel_scroll, ) )
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
            self.create_and_append_menuitem( submenu, label, indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Platform | Uname" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_desktop( self, menu ):
        submenu = Gtk.Menu()

        text = "echo $XDG_CURRENT_DESKTOP" + ": " + self.get_current_desktop()
        self.create_and_append_menuitem( submenu, text, indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            submenu,
            "os.environ.get( 'DESKTOP_SESSION' ): " + os.environ.get( "DESKTOP_SESSION" ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Desktop" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_icon_theme( self, menu ):
        submenu = Gtk.Menu()

        text = \
            "Gtk.Settings().get_default().get_property( \"gtk-icon-theme-name\" ): " + \
            Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )

        self.create_and_append_menuitem( submenu, text, indent = ( 2, 0 ) )

        command = "gsettings get org.gnome.desktop.interface "

        result = self.process_get( command + "icon-theme" ).replace( '"', '' ).replace( '\'', '' )
        self.create_and_append_menuitem(
            submenu,
            command + "icon-theme: " + result,
            indent = ( 2, 0 ) )

        result = self.process_get( command + "gtk-theme" ).replace( '"', '' ).replace( '\'', '' )
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
            _( "Terminal: " ) + str( terminal ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            submenu,
            _( "Execution flag: " ) + str( execution_flag ),
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

        icons = (
            "FULL_MOON",
            "WANING_GIBBOUS",
            "THIRD_QUARTER",
            "NEW_MOON",
            "WAXING_CRESCENT" )

        for icon in icons:
            label = \
                _( "Show '{0}' rendered to {1}" ).format(
                    icon.replace( '_', ' ' ).title(),
                    self.get_cache_directory() )

            self.create_and_append_menuitem(
                submenu,
                label,
                name = icon,
                activate_functionandarguments = ( self._use_icon_dynamically_created, ),
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
                    self.show_notification( _( "Current time..." ), self._get_current_time() ), ),
            indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Label | Tooltip | OSD" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _build_menu_clipboard( self, menu ):
        submenu = Gtk.Menu()

        self.create_and_append_menuitem(
            submenu,
            _( "Copy current time to clipboard" ),
            activate_functionandarguments = (
                lambda menuitem: ( self.copy_to_selection( self._get_current_time() ) ), ),
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
            "calendar -f /usr/share/calendar/calendar.all -A 3",
            "fortune",
            "ls -la",
            f"notify-send -i { self.get_icon_name() } 'summary' 'body'",
            "paplay /usr/share/sounds/freedesktop/stereo/complete.oga",
            "wmctrl -l" )

        for label, command in zip( labels, commands ):
            self.create_and_append_menuitem(
                submenu,
                label,
                activate_functionandarguments = (
                    lambda menuitem, command = command:  # Need command = command to handle lambda late binding.
                        self._execute_command( command ), ),
                indent = ( 2, 0 ) )

        self.create_and_append_menuitem(
            menu,
            _( "Execute Terminal Command" ),
            indent = ( 1, 1 ) ).set_submenu( submenu )


    def _get_current_time( self ):
        return datetime.datetime.now().strftime( "%H:%M:%S" )


    def _use_icon_dynamically_created( self, menuitem ):
        icon_path = \
            self.write_cache_text(
                self._get_svg_icon_text( menuitem.get_name(), 35, 65 ),
                IndicatorTest.CACHE_ICON_BASENAME,
                IndicatorBase.EXTENSION_SVG_SYMBOLIC )

        self.set_icon( str( icon_path ) )


    # A direct copy from indicatorlunar to test dynamically created SVG icons in the user cache.
    #
    # phase
    #   The current phase of the moon.
    # illumination percentage
    #   The brightness ranging from 0 to 100 inclusive.
    #   Ignored when phase is full/new or first/third quarter.
    # bright limb angle in degrees
    #   Bright limb angle, relative to zenith, ranging from 0 to 360 inclusive.
    #   Ignored when phase is full/new.
    def _get_svg_icon_text( self, phase, illumination_percentage, bright_limb_angle_in_degrees ):
        width = 100
        height = width
        radius = float( width / 2 )
        colour = "777777"
        if phase == "FULL_MOON" or phase == "NEW_MOON":
            body = '<circle cx="' + str( width / 2 ) + '" cy="' + str( height / 2 ) + '" r="' + str( radius )
            if phase == "NEW_MOON":
                body += '" fill="#' + colour + '" fill-opacity="0.0" />'

            else: # Full
                body += '" fill="#' + colour + '" />'

        else: # First/Third Quarter or Waning/Waxing Crescent or Waning/Waxing Gibbous
            body = \
                '<path d="M ' + str( width / 2 - radius ) + ' ' + str( height / 2 ) + ' ' + \
                'A ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + \
                str( width / 2 + radius ) + ' ' + str( height / 2 )

            if phase == "FIRST_QUARTER" or phase == "THIRD_QUARTER":
                body += ' Z"'

            elif phase == "WANING_CRESCENT" or phase == "WAXING_CRESCENT":
                body += \
                    ' A ' + str( radius ) + ' ' + str( radius * ( 50 - illumination_percentage ) / 50 ) + ' 0 0 0 ' + \
                    str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            else: # Waning/Waxing Gibbous
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


    def _execute_command( self, command ):
        terminal, terminal_execution_flag = self.get_terminal_and_execution_flag()
        if terminal is None:
            message = _( "Cannot run script as no terminal and/or terminal execution flag found; please install gnome-terminal." )
            self.get_logging().error( message )
            self.show_notification( "Cannot run script", message )

        elif self.is_qterminal_and_broken( terminal ):
            # As a result of
            #    https://github.com/lxqt/qterminal/issues/335
            # the default terminal in Lubuntu (qterminal) fails to parse argument.
            # Although a fix has been made, it is unlikely the repository will be updated any time soon.
            # So the quickest/easiest workaround is to install gnome-terminal.
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
                    ( ( self.data_function, "" ), renderer_text_for_column_dayofweek, 0 ), ),
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


    # References
    #   https://stackoverflow.com/questions/52798356/python-gtk-treeview-column-data-display
    #   https://stackoverflow.com/questions/27745585/show-icon-or-color-in-gtk-treeview-tree
    #   https://stackoverflow.com/questions/49836499/make-only-some-rows-bold-in-a-gtk-treeview
    def data_function( self, treeviewcolumn, cell_renderer, tree_model, tree_iter, data ):
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
