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


# Application indicator for VirtualBox™ virtual machines.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import datetime
import gi
import time

gi.require_version( "Gdk", "3.0" )
from gi.repository import Gdk

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from virtualmachine import Group, VirtualMachine


class IndicatorVirtualBox( IndicatorBase ):
    # Unused within the indicator; used by build_wheel.py when building the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator VirtualBox™" )

    CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS = "delayBetweenAutoStartInSeconds"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_SORT_GROUPS_AND_VIRTUAL_MACHINES_EQUALLY = "sortGroupsAndVirtualMachinesEqually"
    CONFIG_VIRTUAL_MACHINE_PREFERENCES = "virtualMachinePreferences"
    CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME = "virtualboxManagerWindowName"

    VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT = "VBoxManage startvm %VM%"

    # Virtual Machine treeview columns; one to one mapping between data model and view.
    COLUMN_GROUP_OR_VIRTUAL_MACHINE_NAME = 0 # Either the group or name of the virtual machine.
    COLUMN_AUTOSTART = 1 # Icon name for the APPLY icon when the virtual machine is to autostart; None otherwise.
    COLUMN_START_COMMAND = 2 # Start command for the virtual machine.
    COLUMN_UUID = 3 # The UUID for the virtual machine (used to identify; not displayed).

    # Indices for preferences list (within a dictionary).
    PREFERENCES_AUTOSTART = 0
    PREFERENCES_START_COMMAND = 1


    def __init__( self ):
        super().__init__(
            comments = _( "Shows VirtualBox™ virtual machines and allows them to be started." ) )

        self.auto_start_required = True
        self.date_time_of_last_notification = datetime.datetime.now()
        self.scroll_direction_is_up = True
        self.scroll_uuid = None

        self.request_mouse_wheel_scroll_events( ( self.on_mouse_wheel_scroll, ) )


    def update( self, menu ):
        if self.auto_start_required: # Start VMs here so that the indicator icon is displayed immediately.
            self.auto_start_required = False
            if self.is_vbox_manage_installed():
                self.auto_start_virtual_machines()

        self.build_menu( menu )

        return int( 60 * self.refresh_interval_in_minutes )


    def build_menu( self, menu ):
        if self.is_vbox_manage_installed():
            virtual_machines = self.get_virtual_machines()
            if virtual_machines:
                running_names, running_uuids = self.get_running_virtual_machines()

                self._build_menu(
                    menu, self.get_virtual_machines(),
                    ( 0, 0 ),
                    running_uuids )

            else:
                menu.append( Gtk.MenuItem.new_with_label( _( "(no virtual machines exist)" ) ) )

            menu.append( Gtk.SeparatorMenuItem() )

            self.create_and_append_menuitem(
                menu,
                _( "Launch VirtualBox™ Manager" ),
                activate_functionandarguments = (
                    lambda menuitem: self.on_launch_virtual_box_manager(), ),
                is_secondary_activate_target = True )

        else:
            self.create_and_append_menuitem(
                menu,
                _( "(VirtualBox™ is not installed)" ) )


    def _build_menu( self, menu, items, indent, running_uuids ):
        if self.sort_groups_and_virtual_machines_equally:
            sorted_items = \
                sorted(
                    items,
                    key = lambda x: ( x.get_name().lower() ) )

        else:
            sorted_items = \
                sorted(
                    items,
                    key = lambda x: ( type( x ) is not Group, x.get_name().lower() ) ) # Checking if an item is a group results in True (1) or False (0).

        for item in sorted_items:
            if type( item ) is Group:
                self._build_menu(
                    self._add_group_to_menu( menu, item, indent ),
                    item.get_items(),
                    ( indent[ 0 ] + 1, indent[ 1 ] + 1 ),
                    running_uuids )

            else:
                self._add_virtual_machine_to_menu(
                    menu,
                    item,
                    indent,
                    item.get_uuid() in running_uuids )


    def _add_group_to_menu( self, menu, group, indent ):
        menuitem = \
            self.create_and_append_menuitem(
                menu,
                group.get_name(),
                indent = indent )

        if self.show_submenu:
            menu = Gtk.Menu()
            menuitem.set_submenu( menu )

        return menu


    def _add_virtual_machine_to_menu( self, menu, virtual_machine, indent, is_running ):
        if is_running:
            self.create_and_append_radiomenuitem(
                menu,
                virtual_machine.get_name(),
                activate_functionandarguments = ( self._on_virtual_machine, virtual_machine ),
                indent = indent )

        else:
            self.create_and_append_menuitem(
                menu,
                virtual_machine.get_name(),
                activate_functionandarguments = ( self._on_virtual_machine, virtual_machine ),
                indent = indent )


    def _on_virtual_machine( self, menuitem, virtual_machine ):
        if self.is_virtual_machine_running( virtual_machine.get_uuid() ):
            self.bring_window_to_front( virtual_machine.get_name() )

        else:
            self.start_virtual_machine( virtual_machine.get_uuid() )
            self.request_update( delay = 10 ) # Delay the refresh as the VM will have been started in the background and VBoxManage will not have had time to update.


    def auto_start_virtual_machines( self ):
        virtual_machines_for_autostart = [ ]
        self._get_virtual_machines_for_autostart(
            self.get_virtual_machines(),
            virtual_machines_for_autostart )

        previous_virtual_machine_was_already_running = True
        while len( virtual_machines_for_autostart ) > 0: # Start up each virtual machine and only insert the time delay if a machine was not already running.
            virtual_machine = virtual_machines_for_autostart.pop()
            if self.is_virtual_machine_running( virtual_machine.get_uuid() ):
                self.bring_window_to_front( virtual_machine.get_name() )
                previous_virtual_machine_was_already_running = True

            else:
                if not previous_virtual_machine_was_already_running:
                    time.sleep( self.delay_between_autostart_in_seconds )

                self.start_virtual_machine( virtual_machine.get_uuid() )
                previous_virtual_machine_was_already_running = False


    def _get_virtual_machines_for_autostart(
            self,
            virtual_machines,
            virtual_machines_for_autostart ):

        for item in virtual_machines:
            if type( item ) is Group:
                self._get_virtual_machines_for_autostart(
                    item.get_items(),
                    virtual_machines_for_autostart )

            else:
                if self.is_autostart( item.get_uuid() ):
                    virtual_machines_for_autostart.append( item )


    def start_virtual_machine( self, uuid ):
        result = self.process_get( "VBoxManage list vms | grep " + uuid )
        if result is None or uuid not in result:
            message = _( "The virtual machine could not be found - perhaps it has been renamed or deleted.  The list of virtual machines has been refreshed - please try again." )
            self.show_notification( _( "Error" ), message )

        else:
            self.process_call( self.get_start_command( uuid ).replace( "%VM%", uuid ) + " &" )


    def bring_window_to_front( self, virtual_machine_name, delay_in_seconds = 0 ):
        number_of_windows_with_the_same_name = \
            self.process_get( 'wmctrl -l | grep "' + virtual_machine_name + '" | wc -l' )

        if number_of_windows_with_the_same_name == "0":
            message = _( "Unable to find the window for the virtual machine '{0}' - perhaps it is running as headless." ).format( virtual_machine_name )
            summary = _( "Warning" )
            self.show_notification_with_delay( summary, message, delay_in_seconds = delay_in_seconds )

        elif number_of_windows_with_the_same_name == "1":
            for line in self.process_get( "wmctrl -l" ).splitlines():
                if virtual_machine_name in line:
                    window_id = line[ 0 : line.find( " " ) ]
                    self.process_call( "wmctrl -i -a " + window_id )
                    break

        else:
            message = _( "Unable to bring the virtual machine '{0}' to front as there is more than one window with overlapping names." ).format( virtual_machine_name )
            summary = _( "Warning" )
            self.show_notification_with_delay( summary, message, delay_in_seconds = delay_in_seconds )


    # Zealous mouse wheel scrolling can cause too many notifications, subsequently popping the graphics stack!
    # Prevent notifications from appearing until a set time has elapsed since the previous notification.
    def show_notification_with_delay( self, summary, message, delay_in_seconds = 0 ):
        date_time_of_last_notification_plus_delay = \
            self.date_time_of_last_notification + datetime.timedelta( seconds = delay_in_seconds )

        if( date_time_of_last_notification_plus_delay < datetime.datetime.now() ):
            self.show_notification( summary, message )
            self.date_time_of_last_notification = datetime.datetime.now()


    def on_mouse_wheel_scroll( self, indicator, delta, scroll_direction ):
        if self.is_vbox_manage_installed():
            running_names, running_uuids = self.get_running_virtual_machines()
            if running_uuids:
                if self.scroll_uuid is None or self.scroll_uuid not in running_uuids:
                    self.scroll_uuid = running_uuids[ 0 ]

                if scroll_direction == Gdk.ScrollDirection.UP:
                    index = ( running_uuids.index( self.scroll_uuid ) + 1 ) % len( running_uuids )
                    self.scroll_uuid = running_uuids[ index ]
                    self.scroll_direction_is_up = True

                else:
                    index = ( running_uuids.index( self.scroll_uuid ) - 1 ) % len( running_uuids )
                    self.scroll_uuid = running_uuids[ index ]
                    self.scroll_direction_is_up = False

                self.bring_window_to_front( running_names[ running_uuids.index( self.scroll_uuid ) ], 10 )


    def on_launch_virtual_box_manager( self ):
        # The executable for VirtualBox manager does not necessarily appear in the process
        # list because the executable might be a script which calls another executable.
        # Instead, have the user specify the title of the VirtualBox manager window into
        # the preferences and find the window by the window title.
        window_id = None
        result = self.process_get( "wmctrl -l | grep \"" + self.virtualbox_manager_window_name + "\"" )
        if result:
            window_id = result.split()[ 0 ]

        if window_id is None or window_id == "":
            self.process_call( self.process_get( "which VirtualBox" ) + " &" )

        else:
            self.process_call( "wmctrl -ia " + window_id )


    # Returns a list of running VM names and list of corresponding running VM UUIDs.
    def get_running_virtual_machines( self ):
        names = [ ]
        uuids = [ ]
        result = self.process_get( "VBoxManage list runningvms" )
        if result:
            for line in result.splitlines():
                try:
                    info = line[ 1 : -1 ].split( "\" {" )
                    names.append( info[ 0 ] )
                    uuids.append( info[ 1 ] )

                except Exception:
                    pass # Sometimes VBoxManage emits a warning message along with the VM information.

        return names, uuids


    def is_virtual_machine_running( self, uuid ):
        return self.process_get( "VBoxManage list runningvms | grep " + uuid ) is not None


    def get_virtual_machines( self ):
        virtual_machines = [ ]
        try:
            def add_virtual_machine( group, name, uuid, groups ):
                for group_name in groups:
                    the_group = next( ( x for x in group.get_items() if type( x ) is Group and x.get_name() == group_name ), None )
                    if the_group is None:
                        the_group = Group( group_name )
                        group.add_item( the_group )

                    group = the_group

                group.add_item( VirtualMachine( name, uuid ) )


            top_group = Group( "" ) # Only needed whilst parsing results from VBoxManage...
            for line in self.process_get( "VBoxManage list vms --long" ).splitlines():
                if line.startswith( "Name:" ):
                    name = line.split( "Name:" )[ 1 ].strip()

                elif line.startswith( "Groups:" ):
                    groups = line.split( '/' )[ 1 : ]
                    if groups[ 0 ] == '':
                        del groups[ 0 ]

                elif line.startswith( "UUID:" ):
                    uuid = line.split( "UUID:" )[ 1 ].strip()
                    add_virtual_machine( top_group, name, uuid, groups )

            virtual_machines = top_group.get_items()

        except Exception as e:
            self.get_logging().exception( e )
            virtual_machines = [ ]

        return virtual_machines


    def is_vbox_manage_installed( self ):
        is_installed = False
        result = self.process_get( "which VBoxManage" )
        if result:
            is_installed = result.find( "VBoxManage" ) > -1

        return is_installed


    def get_start_command( self, uuid ):
        start_command = IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT
        if uuid in self.virtual_machine_preferences:
            start_command = self.virtual_machine_preferences[ uuid ][ IndicatorVirtualBox.PREFERENCES_START_COMMAND ]

        return start_command


    def is_autostart( self, uuid ):
        return \
            uuid in self.virtual_machine_preferences and \
            self.virtual_machine_preferences[ uuid ][ IndicatorVirtualBox.PREFERENCES_AUTOSTART ]


    def on_preferences( self, dialog ):
        notebook = Gtk.Notebook()

        # List of groups and virtual machines.
        treestore = Gtk.TreeStore( str, str, str, str ) # Group or virtual machine name, autostart, start command, UUID.

        items = [ ]
        if self.is_vbox_manage_installed():
            items = self.get_virtual_machines()

        groups_exist = self._add_items_to_store( treestore, None, items )

        treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                treestore,
                ( _( "Virtual Machine" ), _( "Autostart" ), _( "Start Command" ) ),
                (
                    ( Gtk.CellRendererText(), "text", IndicatorVirtualBox.COLUMN_GROUP_OR_VIRTUAL_MACHINE_NAME ),
                    ( Gtk.CellRendererPixbuf(), "stock_id", IndicatorVirtualBox.COLUMN_AUTOSTART ),
                    ( Gtk.CellRendererText(), "text", IndicatorVirtualBox.COLUMN_START_COMMAND ) ),
                alignments_columnviewids = ( ( 0.5, IndicatorVirtualBox.COLUMN_AUTOSTART ), ),
                tooltip_text = _( "Double click to edit a virtual machine's properties." ),
                rowactivatedfunctionandarguments = ( self.on_virtual_machine_double_click, ) )

        notebook.append_page( scrolledwindow, Gtk.Label.new( _( "Virtual Machines" ) ) )

        # General settings.
        grid = self.create_grid()

        window_name = \
            self.create_entry(
                self.virtualbox_manager_window_name,
                tooltip_text = _(
                    "The window title of VirtualBox™ Manager.\n" +
                    "You may have to adjust for your local language.\n\n" +
                    "This is used to bring the VirtualBox™ Manager\n" +
                    "window to the front if already running." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "VirtualBox™ Manager" ) ), False ),
                    ( window_name, True ) ) ),
            0, 0, 1, 1 )

        sort_groups_and_virtual_machines_equally_checkbox = \
            self.create_checkbutton(
                _( "Sort groups and virtual machines equally" ),
                tooltip_text = _(
                    "If checked, groups and virtual machines\n" +
                    "are sorted without distinction.\n\n" +
                    "Otherwise, groups are sorted first,\n" +
                    "followed by virtual machines." ),
                active = self.sort_groups_and_virtual_machines_equally )

        grid.attach( sort_groups_and_virtual_machines_equally_checkbox, 0, 1, 1, 1 )

        show_as_submenus_checkbox = \
            self.create_checkbutton(
                _( "Show groups as submenus" ),
                tooltip_text = _(
                    "If checked, groups are shown using submenus.\n\n" +
                    "Otherwise, groups are shown as an indented list." ),
                active = self.show_submenu )

        row = 2
        if groups_exist:
            grid.attach( show_as_submenus_checkbox, 0, row, 1, 1 )
            row += 1

        spinner_refresh_interval = \
            self.create_spinbutton(
                self.refresh_interval_in_minutes,
                1,
                60,
                page_increment = 5,
                tooltip_text = _(
                    "How often the list of virtual machines\n" +
                    "and their running status are updated." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Refresh interval (minutes)" ) ), False ),
                    ( spinner_refresh_interval, False ) ),
                margin_top = 10 ),
            0, row, 1, 1 )
        row += 1

        spinner_delay = \
            self.create_spinbutton(
                self.delay_between_autostart_in_seconds,
                1,
                300,
                page_increment = 30,
                tooltip_text = _(
                    "Amount of time to wait from automatically\n" +
                    "starting one virtual machine to the next." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Startup delay (seconds)" ) ), False ),
                    ( spinner_delay, False ) ), 
                margin_top = 10 ),
            0, row, 1, 1 )
        row += 1

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = \
            self.create_preferences_common_widgets()

        grid.attach( box, 0, row, 1, 1 )
        row += 1

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        response_type = dialog.run()
        if response_type == Gtk.ResponseType.OK:
            self.virtualbox_manager_window_name = window_name.get_text().strip()
            self.delay_between_autostart_in_seconds = spinner_delay.get_value_as_int()
            self.show_submenu = show_as_submenus_checkbox.get_active()
            self.sort_groups_and_virtual_machines_equally = sort_groups_and_virtual_machines_equally_checkbox.get_active()
            self.refresh_interval_in_minutes = spinner_refresh_interval.get_value_as_int()
            self.virtual_machine_preferences.clear()
            self._update_virtual_machine_preferences( treestore, treeview.get_model().get_iter_first() )

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


    def _add_items_to_store( self, treestore, parent, items ):
        groups_exist = False
        if self.sort_groups_and_virtual_machines_equally:
            sorted_items = sorted( items, key = lambda x: ( x.get_name().lower() ) )

        else:
            sorted_items = sorted( items, key = lambda x: ( type( x ) is not Group, x.get_name().lower() ) ) # Checking if an item is a group results in True (1) or False (0).

        for item in sorted_items:
            if type( item ) is Group:
                groups_exist = True
                self._add_items_to_store(
                    treestore,
                    treestore.append( parent, [ item.get_name(), None, None, None ] ),
                    item.get_items() )

            else:
                row = [
                    item.get_name(),
                    Gtk.STOCK_APPLY if self.is_autostart( item.get_uuid() ) else None,
                    self.get_start_command( item.get_uuid() ),
                    item.get_uuid() ]
                treestore.append( parent, row )

        return groups_exist


    def _update_virtual_machine_preferences( self, treestore, treeiter ):
        while treeiter:
            is_virtual_machine = treestore[ treeiter ][ IndicatorVirtualBox.COLUMN_UUID ]
            is_autostart = treestore[ treeiter ][ IndicatorVirtualBox.COLUMN_AUTOSTART ] == Gtk.STOCK_APPLY
            is_default_start_command = treestore[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] == IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT
            if ( is_virtual_machine and is_autostart ) or ( is_virtual_machine and not is_default_start_command ): # Only record VMs with different settings to default.
                key = treestore[ treeiter ][ IndicatorVirtualBox.COLUMN_UUID ]
                value = [ is_autostart, treestore[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] ]
                self.virtual_machine_preferences[ key ] = value

            if treestore.iter_has_child( treeiter ):
                childiter = treestore.iter_children( treeiter )
                self._update_virtual_machine_preferences( treestore, childiter )

            treeiter = treestore.iter_next( treeiter )


    def on_virtual_machine_double_click( self, tree, row_number, treeviewcolumn ):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter and model[ treeiter ][ IndicatorVirtualBox.COLUMN_UUID ]:
            self.edit_virtual_machine( tree, model, treeiter )


    def edit_virtual_machine( self, tree, model, treeiter ):
        grid = self.create_grid()

        start_command = \
            self.create_entry(
                model[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] if model[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] else "",
                tooltip_text = _(
                    "The terminal command to start the virtual machine such as\n\n" +
                    "\tVBoxManage startvm %VM%\n" +
                    "or\n" +
                    "\tVBoxHeadless --startvm %VM% --vrde off" ),
                make_longer = True )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Start Command" ) ), False ),
                    ( start_command, True ) ) ),
            0, 0, 2, 1 )

        autostart_checkbutton = \
            self.create_checkbutton(
                _( "Autostart" ),
                tooltip_text = _( "Run the virtual machine when the indicator starts." ),
                active = \
                    model[ treeiter ][ IndicatorVirtualBox.COLUMN_AUTOSTART ] is not None and
                    model[ treeiter ][ IndicatorVirtualBox.COLUMN_AUTOSTART ] == Gtk.STOCK_APPLY )

        grid.attach( autostart_checkbutton, 0, 1, 2, 1 )

        dialog = self.create_dialog( tree, _( "Virtual Machine Properties" ), content_widget = grid )
        while True:
            dialog.show_all()

            if dialog.run() != Gtk.ResponseType.OK:
                break

            if start_command.get_text().strip() == "":
                self.show_dialog_ok( dialog, _( "The start command cannot be empty." ) )
                start_command.grab_focus()
                continue

            if not "%VM%" in start_command.get_text().strip():
                message = _( "The start command must contain %VM% which is substituted for the virtual machine name/id." )
                self.show_dialog_ok( dialog, message )
                start_command.grab_focus()
                continue

            model[ treeiter ][ IndicatorVirtualBox.COLUMN_AUTOSTART ] = Gtk.STOCK_APPLY if autostart_checkbutton.get_active() else None
            model[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] = start_command.get_text().strip()

            break

        dialog.destroy()


    def load_config( self, config ):
        self.delay_between_autostart_in_seconds = \
            config.get(
                IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS,
                10 )

        self.refresh_interval_in_minutes = \
            config.get(
                IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES,
                15 )

        self.show_submenu = \
            config.get(
                IndicatorVirtualBox.CONFIG_SHOW_SUBMENU,
                False )

        self.sort_groups_and_virtual_machines_equally = \
            config.get(
                IndicatorVirtualBox.CONFIG_SORT_GROUPS_AND_VIRTUAL_MACHINES_EQUALLY,
                True )

        self.virtual_machine_preferences = \
            config.get(
                IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES,
                { } ) # Store information about VMs.  Key is VM UUID; value is [ autostart (bool), start command (str) ]

        self.virtualbox_manager_window_name = \
            config.get(
                IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME,
                "Oracle VM VirtualBox Manager" )


    def save_config( self ):
        return {
            IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS : self.delay_between_autostart_in_seconds,
            IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES : self.refresh_interval_in_minutes,
            IndicatorVirtualBox.CONFIG_SHOW_SUBMENU : self.show_submenu,
            IndicatorVirtualBox.CONFIG_SORT_GROUPS_AND_VIRTUAL_MACHINES_EQUALLY : self.sort_groups_and_virtual_machines_equally,
            IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES : self.virtual_machine_preferences,
            IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME : self.virtualbox_manager_window_name
        }


IndicatorVirtualBox().main()
