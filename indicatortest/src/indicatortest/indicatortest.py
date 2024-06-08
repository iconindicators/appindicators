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

gi.require_version( "Gdk", "3.0" )
from gi.repository import Gdk

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

try:
    gi.require_version( "Notify", "0.7" )
except ValueError:
    gi.require_version( "Notify", "0.8" )
from gi.repository import Notify

gi.require_version( "Pango", "1.0" )
from gi.repository import Pango

import platform
from threading import Thread


class IndicatorTest( IndicatorBase ):

    CACHE_ICON_BASENAME = "icon-"
    CACHE_ICON_MAXIMUM_AGE_HOURS = 0

    CONFIG_X = "x"

    LABEL = "Test Indicator"

    def __init__( self ):
        super().__init__( comments = _( "Exercises a range of indicator functionality." ) )
        self.request_mouse_wheel_scroll_events( ( self.on_mouse_wheel_scroll, ) )
        self.flush_cache(
            IndicatorTest.CACHE_ICON_BASENAME,
            IndicatorTest.CACHE_ICON_MAXIMUM_AGE_HOURS )


    def update( self, menu ):
        self.__build_menu( menu )
        self.set_label( IndicatorTest.LABEL )


#TODO Delete
    # def onMouseWheelScroll( self, indicator, delta, scroll_direction ):
    #     self.setLabel( self.__get_current_time() )
    #     print( "Mouse wheel is scrolling..." )


    def on_mouse_wheel_scroll( self, indicator, delta, scroll_direction ):
        self.set_label( self.__get_current_time() )
        print( "Mouse wheel is scrolling..." )


    def __build_menu( self, menu ):
        self.__build_menu_platform_uname( menu )
        self.__build_menu_desktop( menu )
        self.__build_menu_icon( menu )
        self.__build_menu_label_tooltip_osd( menu )
        self.__build_menu_clipboard( menu )
        self.__build_menu_terminal( menu )
        self.__build_menu_execute_command( menu )


    def __build_menu_platform_uname( self, menu ):
        submenu = Gtk.Menu()

        uname = platform.uname()
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + "Machine: " + str( uname.machine ) )
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + "Node: " + str( uname.node ) )
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + "Processor: " + str( uname.processor ) )
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + "Release: " + str( uname.release ) )
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + "System: " + str( uname.system ) )
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + "Version: " + str( uname.version ) )

        self.create_and_append_menuitem( menu, "Platform | Uname" ).set_submenu( submenu )


    def __build_menu_desktop( self, menu ):
        submenu = Gtk.Menu()

        text = \
            self.get_menu_indent() + \
            "Gtk.Settings().get_default().get_property( \"gtk-icon-theme-name\" ): " + \
            Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )

        self.create_and_append_menuitem( submenu, text )

        command = "gsettings get org.gnome.desktop.interface "

        result = self.process_get( command + "icon-theme" ).replace( '"', '' ).replace( '\'', '' ).strip()
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + command + "icon-theme: " + result )

        result = self.process_get( command + "gtk-theme" ).replace( '"', '' ).replace( '\'', '' ).strip()
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + command + "gtk-theme: " + result )

        text = self.get_menu_indent() + "echo $XDG_CURRENT_DESKTOP" + ": " + self.getDesktopEnvironment()
        self.create_and_append_menuitem( submenu, text )

        self.create_and_append_menuitem( menu, "Desktop" ).set_submenu( submenu )


    def __build_menu_icon( self, menu ):
        submenu = Gtk.Menu()

        self.create_and_append_menuitem(
            submenu,
            self.get_menu_indent() + "Reset icon",
            activate_functionandarguments =
                ( lambda menuItem: self.indicator.set_icon_full( self.get_icon_name(), "" ), ) )

        icons = [ "FULL_MOON",
                  "WANING_GIBBOUS",
                  "THIRD_QUARTER",
                  "NEW_MOON",
                  "WAXING_CRESCENT" ]

        for icon in icons:
            self.create_and_append_menuitem(
                submenu,
                self.get_menu_indent() + "Use " + icon + " dynamically created in " + self.get_cache_directory(),
                name = icon,
                activate_functionandarguments = ( self.__use_icon_dynamically_created, ) )

        self.create_and_append_menuitem( menu, "Icon" ).set_submenu( submenu )


    def __build_menu_label_tooltip_osd( self, menu ):
        submenu = Gtk.Menu()

        self.create_and_append_menuitem(
            submenu,
            self.get_menu_indent() + "Reset label",
            activate_functionandarguments = ( lambda menuItem: self.set_label( IndicatorTest.LABEL ), ) )

        self.create_and_append_menuitem(
            submenu,
            self.get_menu_indent() + "Show current time in label",
            activate_functionandarguments = 
                ( lambda menuItem: (
                    print( "secondary activate target / mouse middle click" ),
                    self.set_label( self.__get_current_time() ) ), ),
            is_secondary_activate_target = True )

        self.create_and_append_menuitem(
            submenu,
            self.get_menu_indent() + "Show current time in OSD",
            activate_functionandarguments =
                ( lambda menuItem:
                    Notify.Notification.new( "Current time...", self.__get_current_time(), self.get_icon_name() ).show(), ) )

        self.create_and_append_menuitem( menu, "Label / Tooltip / OSD" ).set_submenu( submenu )


    def __build_menu_clipboard( self, menu ):
        submenu = Gtk.Menu()

        self.create_and_append_menuitem(
            submenu,
            self.get_menu_indent() + _( "Copy current time to clipboard" ),
            activate_functionandarguments =
                ( lambda menuItem: ( 
                    print( "clipboard" ),
                    Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( self.__get_current_time(), -1 ) ), ) )

        self.create_and_append_menuitem( menu, "Clipboard" ).set_submenu( submenu )


    def __build_menu_terminal( self, menu ):
        submenu = Gtk.Menu()

        terminal, executionFlag = self.get_terminal_and_execution_flag()
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + "Terminal: " + str( terminal ) )
        self.create_and_append_menuitem( submenu, self.get_menu_indent() + "Execution flag: " + str( executionFlag ) )

        self.create_and_append_menuitem( menu, "Terminal" ).set_submenu( submenu )


    def __build_menu_execute_command( self, menu ):
        submenu = Gtk.Menu()

        labels = [
            "calendar",
            "fortune",
            "ls",
            "notify-send",
            "paplay",
            "wmctrl" ]

        commands = [
            "calendar -f /usr/share/calendar/calendar.all -A 3",
            "fortune",
            "ls -la",
            f"notify-send -i { self.get_icon_name() } 'summary' 'body'",
            "paplay /usr/share/sounds/freedesktop/stereo/complete.oga",
            "wmctrl -l" ]

        for label, command in zip( labels, commands ):
            self.create_and_append_menuitem(
                submenu,
                self.get_menu_indent() + label,
                activate_functionandarguments =
                    ( lambda menuItem, command = command: self.__execute_command( command ), ) ) # Note command = command to handle lambda late binding.

        self.create_and_append_menuitem( menu, "Execute Terminal Command" ).set_submenu( submenu )


    def __get_current_time( self ):
        return datetime.datetime.now().strftime( "%H:%M:%S" )


    def __use_icon_dynamically_created( self, menuitem ):
        icon_filename = self.write_cache_text(
            self.__get_svg_icon_text( menuitem.get_name(), 35, 65 ),
            IndicatorTest.CACHE_ICON_BASENAME,
            IndicatorBase.EXTENSION_SVG_SYMBOLIC )

        self.indicator.set_icon_full( icon_filename, "" )


    # A direct copy from Indicator Lunar to test
    # dynamically created SVG icons in the user cache.
    #
    # phase The current phase of the moon.
    # illumination_percentage         The brightness ranging from 0 to 100 inclusive.
    #                                 Ignored when phase is full/new or first/third quarter.
    # bright_limb_angle_in_degrees    Bright limb angle, relative to zenith, ranging from 0 to 360 inclusive.
    #                                 Ignored when phase is full/new.
    def __get_svg_icon_text( self, phase, illumination_percentage, bright_limb_angle_in_degrees ):
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
            body = '<path d="M ' + str( width / 2 - radius ) + ' ' + str( height / 2 ) + ' ' + \
                   'A ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + \
                   str( width / 2 + radius ) + ' ' + str( height / 2 )

            if phase == "FIRST_QUARTER" or phase == "THIRD_QUARTER":
                body += ' Z"'

            elif phase == "WANING_CRESCENT" or phase == "WAXING_CRESCENT":
                body += ' A ' + str( radius ) + ' ' + str( radius * ( 50 - illumination_percentage ) / 50 ) + ' 0 0 0 ' + \
                        str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            else: # Waning/Waxing Gibbous
                body += ' A ' + str( radius ) + ' ' + str( radius * ( illumination_percentage - 50 ) / 50 ) + ' 0 0 1 ' + \
                        str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            body += ' transform="rotate(' + str( -bright_limb_angle_in_degrees ) + ' ' + \
                    str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="#' + colour + '" />'

        return '<?xml version="1.0" standalone="no"?>' \
               '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "https://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
               '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100" width="22" height="22">' + body + '</svg>'


    def __execute_command( self, command ):
        terminal, terminal_execution_flag = self.get_terminal_and_execution_flag()
        if terminal is None:
            message = _( "Cannot run script as no terminal and/or terminal execution flag found; please install gnome-terminal." )
            self.getLogging().error( message )
            Notify.Notification.new( "Cannot run script", message, self.get_icon_name() ).show()

        elif self.isTerminalQTerminal():
            # As a result of this issue
            #    https://github.com/lxqt/qterminal/issues/335
            # the default terminal in Lubuntu (qterminal) fails to parse argument.
            # Although a fix has been made, it is unlikely the repository will be updated any time soon.
            # So the quickest/easiest workaround is to install gnome-terminal.
            message = _( "Cannot run script as qterminal incorrectly parses arguments; please install gnome-terminal instead." )
            self.get_logging().error( message )
            Notify.Notification.new( "Cannot run script", message, self.get_icon_name() ).show()

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
                active = self.X )
#TODO Make sure this is converted okay
        # x_checkbutton = Gtk.CheckButton.new_with_label( _( "Enable/disable X" ) )
        # x_checkbutton.set_active( self.X )
        # x_checkbutton.set_tooltip_text( _( "Enable/disable X" ) )
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
                tooltip_text = "Days of week containing an 'n' are bold." )

        # treeView = Gtk.TreeView.new_with_model( store )
        # treeView.expand_all()
        # treeView.set_hexpand( True )
        # treeView.set_vexpand( True )
        # treeView.set_tooltip_text( "Days of week containing an 'n' are bold." )
        #
        # rendererText = Gtk.CellRendererText()
        # treeViewColumn = Gtk.TreeViewColumn( _( "Day of Week" ), rendererText, text = 0 )
        # treeViewColumn.set_expand( True )
        # treeViewColumn.set_cell_data_func( rendererText, self.dataFunction, "" )
        # treeView.append_column( treeViewColumn )
        #
        # scrolledWindow = Gtk.ScrolledWindow()
        # scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        # scrolledWindow.add( treeView )
        #
        # grid.attach( scrolledWindow, 0, 1, 1, 10 )
        grid.attach( scrolledwindow, 0, 1, 1, 10 )

        autostart_checkbox, delay_spinner, box = self.create_autostart_checkbox_and_delay_spinner()
        grid.attach( box, 0, 11, 1, 1 )

        dialog.get_content_area().pack_start( grid, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.X = x_checkbutton.get_active()
            self.set_autostart_and_delay( autostart_checkbox.get_active(), delay_spinner.get_value_as_int() )

        return response_type


    def data_function( self, treeviewcolumn, cell_renderer, tree_model, tree_iter, data ):
        cell_renderer.set_property( "weight", Pango.Weight.NORMAL )
        day_of_week = tree_model.get_value( tree_iter, 0 )
        if 'n' in day_of_week:
            cell_renderer.set_property( "weight", Pango.Weight.BOLD )


    def load_config( self, config ):
        self.X = config.get( IndicatorTest.CONFIG_X, True )


    def save_config( self ):
        return {
            IndicatorTest.CONFIG_X : self.X
        }


IndicatorTest().main()
