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
        self.requestMouseWheelScrollEvents()
        self.flushCache( IndicatorTest.CACHE_ICON_BASENAME, IndicatorTest.CACHE_ICON_MAXIMUM_AGE_HOURS )


    def update( self, menu ):
        self.__buildMenu( menu )
        self.setLabel( IndicatorTest.LABEL )


    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        self.setLabel( self.__getCurrentTime() )
        print( "Mouse wheel is scrolling..." )


    def __buildMenu( self, menu ):
        self.__buildMenuPlatformUname( menu )
        self.__buildMenuDesktop( menu )
        self.__buildMenuIcon( menu )
        self.__buildMenuLabelTooltipOSD( menu )
        self.__buildMenuClipboard( menu )
        self.__buildMenuTerminal( menu )
        self.__buildMenuExecuteCommand( menu )


    def __buildMenuPlatformUname( self, menu ):
        subMenu = Gtk.Menu()

        uname = platform.uname()
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + "Machine: " + str( uname.machine ),  )
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + "Node: " + str( uname.node ) )
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + "Processor: " + str( uname.processor ) )
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + "Release: " + str( uname.release ) )
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + "System: " + str( uname.system ) )
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + "Version: " + str( uname.version ) )

        # menuItem = Gtk.MenuItem.new_with_label( "Platform | Uname" )  #TODO What about things like this?  Use the new createandappend?
        # menuItem.set_submenu( subMenu )
        # menu.append( menuItem )
        self.createAndAppendMenuItem( menu, "Platform | Uname" ).set_submenu( subMenu )


    def __buildMenuDesktop( self, menu ):
        subMenu = Gtk.Menu()

        text = \
            self.getMenuIndent() + \
            "Gtk.Settings().get_default().get_property( \"gtk-icon-theme-name\" ): " + \
            Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )

        self.createAndAppendMenuItem( subMenu, text )

        command = "gsettings get org.gnome.desktop.interface "

        result = self.processGet( command + "icon-theme" ).replace( '"', '' ).replace( '\'', '' ).strip()
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + command + "icon-theme: " + result )

        result = self.processGet( command + "gtk-theme" ).replace( '"', '' ).replace( '\'', '' ).strip()
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + command + "gtk-theme: " + result )

        text = self.getMenuIndent() + "echo $XDG_CURRENT_DESKTOP" + ": " + self.getDesktopEnvironment()
        self.createAndAppendMenuItem( subMenu, text )

        # menuItem = Gtk.MenuItem.new_with_label( "Desktop" )
        # menuItem.set_submenu( subMenu )
        # menu.append( menuItem )
        self.createAndAppendMenuItem( menu, "Desktop" ).set_submenu( subMenu )


    def __buildMenuIcon( self, menu ):
        subMenu = Gtk.Menu()

#TODO Remove
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Use default icon" )
        # menuItem.connect( "activate", lambda widget: self.__useIconDefault() )
        # subMenu.append( menuItem )

#TODO Keeping?  Not if we keep the one below.
        # self.createAndAppendMenuItem(
        #     self.getMenuIndent() + "Use default icon",
        #     subMenu,
        #     onClickFunction = self.__useIconDefault )

#TODO Keeping?
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "Use default icon",
            onClickFunction = lambda widget: self.indicator.set_icon_full( self.get_icon_name(), "" ) )

        cacheDirectory = self.getCacheDirectory()
        icons = [ "FULL_MOON",
                  "WANING_GIBBOUS",
                  "THIRD_QUARTER",
                  "NEW_MOON",
                  "WAXING_CRESCENT" ]

        for icon in icons:
            #TODO Remove
            # menuItem = Gtk.MenuItem.new_with_label(
            #     self.getMenuIndent() + "Use " + icon + " dynamically created in " + cacheDirectory )
            #
            # menuItem.set_name( icon )
            # menuItem.connect( "activate", lambda widget: self.__useIconDynamicallyCreated( widget.props.name ) )
            # subMenu.append( menuItem )

#TODO Keep?
            self.createAndAppendMenuItem(
                subMenu,
                self.getMenuIndent() + "Use " + icon + " dynamically created in " + cacheDirectory,
                name = icon,
                onClickFunction = self.__useIconDynamicallyCreated )

        # menuItem = Gtk.MenuItem.new_with_label( "Icon" )
        # menuItem.set_submenu( subMenu )
        # menu.append( menuItem )
        self.createAndAppendMenuItem( menu, "Icon" ).set_submenu( subMenu )


    def __buildMenuLabelTooltipOSD( self, menu ):
        subMenu = Gtk.Menu()

#TODO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Reset label" )
        # menuItem.connect(
        #     "activate",
        #     lambda widget: (
        #         self.setLabel( IndicatorTest.LABEL ) ) )
        #
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "Reset label",
            onClickFunction = lambda widget: self.setLabel( IndicatorTest.LABEL ) )

#TOOO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Show current time in label" )
        # menuItem.connect(
        #     "activate",
        #     lambda widget: (
        #         print( "secondary activate target / mouse middle click" ),
        #         self.setLabel( self.__getCurrentTime() ) ) )
        #
        # self.secondaryActivateTarget = menuItem
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "Show current time in label",
            onClickFunction = lambda widget: (
                print( "secondary activate target / mouse middle click" ),
                self.setLabel( self.__getCurrentTime() ) ),
            isSecondaryActivateTarget = True )

#TODO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Show current time in OSD" )
        # menuItem.connect(
        #     "activate",
        #     lambda widget: Notify.Notification.new(
        #         "Current time...", self.__getCurrentTime(), self.get_icon_name() ).show() )
        #
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "Show current time in OSD",
            onClickFunction = lambda widget:
                Notify.Notification.new( "Current time...", self.__getCurrentTime(), self.get_icon_name() ).show() )

        # menuItem = Gtk.MenuItem.new_with_label( "Label / Tooltip / OSD" )
        # menuItem.set_submenu( subMenu )
        # menu.append( menuItem )
        self.createAndAppendMenuItem( menu, "Label / Tooltip / OSD" ).set_submenu( subMenu )


    def __buildMenuClipboard( self, menu ):
        subMenu = Gtk.Menu()

#TODO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + _( "Copy current time to clipboard" ) )
        # menuItem.connect( "activate", lambda widget:
        #                   Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( self.__getCurrentTime(), -1 ) )
        #
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + _( "Copy current time to clipboard" ),
            onClickFunction = lambda widget:
                Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).set_text( self.__getCurrentTime(), -1 ) )

        # menuItem = Gtk.MenuItem.new_with_label( "Clipboard" )
        # menuItem.set_submenu( subMenu )
        # menu.append( menuItem )
        self.createAndAppendMenuItem( menu, "Clipboard" ).set_submenu( subMenu )


    def __buildMenuTerminal( self, menu ):
        subMenu = Gtk.Menu()

        terminal, executionFlag = self.getTerminalAndExecutionFlag()
        # subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Terminal: " + str( terminal ) ) ) #TODO Delete?
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + "Terminal: " + str( terminal ) )
        # subMenu.append( Gtk.MenuItem.new_with_label( self.getMenuIndent() + "Execution flag: " + str( executionFlag ) ) ) #TODO Delete?
        self.createAndAppendMenuItem( subMenu, self.getMenuIndent() + "Execution flag: " + str( executionFlag ) )

        # menuItem = Gtk.MenuItem.new_with_label( "Terminal" )
        # menuItem.set_submenu( subMenu )
        # menu.append( menuItem )
        self.createAndAppendMenuItem( menu, "Terminal" ).set_submenu( subMenu )


    def __buildMenuExecuteCommand( self, menu ):
        subMenu = Gtk.Menu()

#TODO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "calendar" )
        # command = "calendar -f /usr/share/calendar/calendar.all -A 3"
        # menuItem.connect( "activate", lambda widget: self.__executeCommand( command ) )
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "calendar",
            onClickFunction = lambda widget: self.__executeCommand( "calendar -f /usr/share/calendar/calendar.all -A 3" ) )

#TODO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "fortune" )
        # menuItem.connect( "activate", lambda widget: self.__executeCommand( "fortune" ) )
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "fortune",
            onClickFunction = lambda widget: self.__executeCommand( "fortune" ) )

#TODO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "ls" )
        # menuItem.connect( "activate", lambda widget: self.__executeCommand( "ls -la" ) )
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "ls",
            onClickFunction = lambda widget: self.__executeCommand( "ls -la" ) )

#TODO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "notify-send" )
        # command = f"notify-send -i { self.get_icon_name() } 'summary' 'body'"
        # menuItem.connect( "activate", lambda widget: self.__executeCommand( command ) )
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "notify-send",
            onClickFunction = lambda widget:
                self.__executeCommand( f"notify-send -i { self.get_icon_name() } 'summary' 'body'" ) )

#TODO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "paplay" )
        # command = "paplay /usr/share/sounds/freedesktop/stereo/complete.oga"
        # menuItem.connect( "activate", lambda widget: self.__executeCommand( command ) )
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "paplay",
            onClickFunction = lambda widget:
                self.__executeCommand( "paplay /usr/share/sounds/freedesktop/stereo/complete.oga" ) )

#TODO Delete
        # menuItem = Gtk.MenuItem.new_with_label( self.getMenuIndent() + "wmctrl" )
        # menuItem.connect( "activate", lambda widget: self.__executeCommand( "wmctrl -l" ) )
        # subMenu.append( menuItem )
        self.createAndAppendMenuItem(
            subMenu,
            self.getMenuIndent() + "wmctrl",
            onClickFunction = lambda widget: self.__executeCommand( "wmctrl -l" ) )

        # menuItem = Gtk.MenuItem.new_with_label( "Execute Terminal Command" )
        # menuItem.set_submenu( subMenu )
        # menu.append( menuItem )
        self.createAndAppendMenuItem( menu, "Execute Terminal Command" ).set_submenu( subMenu )


#TODO Probabaly can delete.
    # def __useIconDefault( self, widget ):
    #     self.indicator.set_icon_full( self.get_icon_name(), "" )


    def __getCurrentTime( self ):
        return datetime.datetime.now().strftime( "%H:%M:%S" )


    def __useIconDynamicallyCreated( self, widget ):
        illuminationPercentage = 35
        brightLimbAngleInDegrees = 65
        svgIconText = self.__getSVGIconText( widget.props.name, illuminationPercentage, brightLimbAngleInDegrees )

        iconFilename = self.writeCacheText(
            svgIconText,
            IndicatorTest.CACHE_ICON_BASENAME,
            IndicatorBase.EXTENSION_SVG_SYMBOLIC )

        self.indicator.set_icon_full( iconFilename, "" )


    # A direct copy from Indicator Lunar to test
    # dynamically created SVG icons in the user cache.
    #
    # phase The current phase of the moon.
    # illuminationPercentage The brightness ranging from 0 to 100 inclusive.
    #                        Ignored when phase is full/new or first/third quarter.
    # brightLimbAngleInDegrees Bright limb angle, relative to zenith, ranging from 0 to 360 inclusive.
    #                          Ignored when phase is full/new.
    def __getSVGIconText( self, phase, illuminationPercentage, brightLimbAngleInDegrees ):
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
                body += ' A ' + str( radius ) + ' ' + str( radius * ( 50 - illuminationPercentage ) / 50 ) + ' 0 0 0 ' + \
                        str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            else: # Waning/Waxing Gibbous
                body += ' A ' + str( radius ) + ' ' + str( radius * ( illuminationPercentage - 50 ) / 50 ) + ' 0 0 1 ' + \
                        str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            body += ' transform="rotate(' + str( -brightLimbAngleInDegrees ) + ' ' + \
                    str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="#' + colour + '" />'

        return '<?xml version="1.0" standalone="no"?>' \
               '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "https://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
               '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100" width="22" height="22">' + body + '</svg>'


    def __executeCommand( self, command ):
        terminal, terminalExecutionFlag = self.getTerminalAndExecutionFlag()
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
            self.getLogging().error( message )
            Notify.Notification.new( "Cannot run script", message, self.get_icon_name() ).show()

        else:
            command_ = terminal + " " + terminalExecutionFlag + " ${SHELL} -c '"
            command_ += command
            command_ += "; ${SHELL}"
            command_ += "'"
            Thread( target = self.processCall, args = ( command_, ) ).start()
            print( "Executing command: " + command_ )


    def onPreferences( self, dialog ):
        grid = self.createGrid()

        xCheckbutton = Gtk.CheckButton.new_with_label( _( "Enable/disable X" ) )
        xCheckbutton.set_active( self.X )
        xCheckbutton.set_tooltip_text( _( "Enable/disable X" ) )
        grid.attach( xCheckbutton, 0, 0, 1, 1 )

        autostartCheckbox, delaySpinner, box = self.createAutostartCheckboxAndDelaySpinner()
        grid.attach( box, 0, 1, 1, 1 )

        store = Gtk.ListStore( str )
        store.append( [ "Monday" ] )
        store.append( [ "Tuesday" ] )
        store.append( [ "Wednesday" ] )
        store.append( [ "Thursday" ] )
        store.append( [ "Friday" ] )
        store.append( [ "Saturday" ] )
        store.append( [ "Sunday" ] )

        treeView = Gtk.TreeView.new_with_model( store )
        treeView.expand_all()
        treeView.set_hexpand( True )
        treeView.set_vexpand( True )
        treeView.set_tooltip_text( "Days of week containing an 'n' are bold." )

        rendererText = Gtk.CellRendererText()
        treeViewColumn = Gtk.TreeViewColumn( _( "Day of Week" ), rendererText, text = 0 )
        treeViewColumn.set_expand( True )
        treeViewColumn.set_cell_data_func( rendererText, self.dataFunction, "" )
        treeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( treeView )

        grid.attach( scrolledWindow, 0, 2, 1, 10 )

        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.X = xCheckbutton.get_active()
            self.setAutostartAndDelay( autostartCheckbox.get_active(), delaySpinner.get_value_as_int() )

        return responseType


    def dataFunction( self, treeViewColumn, cellRenderer, treeModel, treeIter, data ):
        cellRenderer.set_property( "weight", Pango.Weight.NORMAL )
        dayOfWeek = treeModel.get_value( treeIter, 0 )
        if 'n' in dayOfWeek:
            cellRenderer.set_property( "weight", Pango.Weight.BOLD )


    def loadConfig( self, config ):
        self.X = config.get( IndicatorTest.CONFIG_X, True )


    def saveConfig( self ):
        return {
            IndicatorTest.CONFIG_X : self.X
        }


IndicatorTest().main()
