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


''' Application indicator for VirtualBox™ virtual machines. '''


import datetime
import time

import gi

gi.require_version( "Gdk", "3.0" )
from gi.repository import Gdk

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

from .indicatorbase import IndicatorBase

from .virtualmachine import Group, VirtualMachine


class IndicatorVirtualBox( IndicatorBase ):
    ''' Main class which encapsulates the indicator. '''

    # Used when building the wheel to create the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator VirtualBox™" )
    indicator_categories = "Categories=Utility"

    CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS = "delayBetweenAutoStartInSeconds"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_SORT_GROUPS_AND_VIRTUAL_MACHINES_EQUALLY = "sortGroupsAndVirtualMachinesEqually"
    CONFIG_VIRTUAL_MACHINE_PREFERENCES = "virtualMachinePreferences"
    CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME = "virtualboxManagerWindowName"

    VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT = "VBoxManage startvm %VM%"

    # Virtual Machine model/view columns.
    COLUMN_GROUP_OR_VIRTUAL_MACHINE_NAME = 0 # Name of group or virtual machine.
    COLUMN_AUTOSTART = 1 # Icon name for the APPLY icon when the virtual machine is to autostart; None otherwise.
    COLUMN_START_COMMAND = 2 # Start command for the virtual machine.
    COLUMN_UUID = 3 # The UUID for the virtual machine (used to identify; not displayed).

    # Indices for preferences list (within a dictionary).
    PREFERENCES_AUTOSTART = 0
    PREFERENCES_START_COMMAND = 1

    MESSAGE_NOT_INSTALLED = _( "VirtualBox™ is not installed" )


    def __init__( self ):
        super().__init__(
            comments = _( "Shows VirtualBox™ virtual machines and\nallows them to be started." ) )

        self.auto_start_required = True
        self.date_time_of_last_notification = datetime.datetime.now()
        self.scroll_direction_is_up = True
        self.scroll_uuid = None

        # A mouse wheel scroll event will use wmctrl to cycle through running
        # virtual machines and attempt to bring each to the front.
        # Under Wayland, wmctrl is not implemented and so it is pointless
        # listening for events which will result in nothing.
        if not self.is_session_type_wayland():
            self.request_mouse_wheel_scroll_events(
                ( self.on_mouse_wheel_scroll, ) )


    def update(
        self,
        menu ):

        virtual_machines = [ ]
        vboxmanage_installed = self.is_vboxmanage_installed()
        if vboxmanage_installed:
            virtual_machines = self.get_virtual_machines()

            # Autostart VMs here rather than in __init__ ensures the indicator
            # icon/menu is displayed without delay.
            if self.auto_start_required:
                self.auto_start_required = False
                self.auto_start_virtual_machines( virtual_machines )

        self.build_menu( menu, vboxmanage_installed, virtual_machines )

        return int( 60 * self.refresh_interval_in_minutes )


    def build_menu(
        self,
        menu,
        vboxmanage_installed,
        virtual_machines ):

        if vboxmanage_installed:
            if virtual_machines:
                running_names, running_uuids = (
                    self.get_running_virtual_machines() )

                self._build_menu(
                    menu, virtual_machines,
                    ( 0, 0 ),
                    running_uuids )

                menu.append( Gtk.SeparatorMenuItem() )

            self.create_and_append_menuitem(
                menu,
                _( "Launch VirtualBox™ Manager" ),
                activate_functionandarguments = (
                    lambda menuitem: self.on_launch_virtual_box_manager(), ),
                is_secondary_activate_target = True )

        else:
            self.create_and_append_menuitem(
                menu, '(' + IndicatorVirtualBox.MESSAGE_NOT_INSTALLED  + ')' )


    def _build_menu(
        self,
        menu,
        items,
        indent,
        running_uuids ):

        sorted_items = (
            Group.sort( items, self.sort_groups_and_virtual_machines_equally ) )

        for item in sorted_items:
            if isinstance( item, Group ):
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


    def _add_group_to_menu(
        self,
        menu,
        group,
        indent ):

        menuitem = (
            self.create_and_append_menuitem(
                menu,
                group.get_name(),
                indent = indent ) )

        if self.show_submenu:
            menu = Gtk.Menu()
            menuitem.set_submenu( menu )

        return menu


    def _add_virtual_machine_to_menu(
        self,
        menu,
        virtual_machine,
        indent,
        is_running ):

        if is_running:
            self.create_and_append_radiomenuitem(
                menu,
                virtual_machine.get_name(),
                activate_functionandarguments = (
                    self._on_virtual_machine, virtual_machine ),
                indent = indent )

        else:
            self.create_and_append_menuitem(
                menu,
                virtual_machine.get_name(),
                activate_functionandarguments = (
                    self._on_virtual_machine, virtual_machine ),
                indent = indent )


    def _on_virtual_machine(
        self,
        menuitem,
        virtual_machine ):

        if self.is_virtual_machine_running( virtual_machine.get_uuid() ):
            self.bring_window_to_front( virtual_machine.get_name() )

        else:
            self.start_virtual_machine( virtual_machine.get_uuid() )
            # Delay the refresh as the VM will have been started in the
            # background and VBoxManage will not have had time to update.
            self.request_update( delay = 10 )


    def auto_start_virtual_machines(
        self,
        virtual_machines ):

        virtual_machines_for_autostart = (
            self._get_virtual_machines_for_autostart( virtual_machines ) )

        # Start up each virtual machine, inserting a delay if the virtual
        # machine was not already running.
        previous_virtual_machine_was_already_running = True
        need_one_last_sleep = False
        for virtual_machine in virtual_machines_for_autostart:
            if self.is_virtual_machine_running( virtual_machine.get_uuid() ):
                self.bring_window_to_front( virtual_machine.get_name() )
                previous_virtual_machine_was_already_running = True

            else:
                if not previous_virtual_machine_was_already_running:
                    time.sleep( self.delay_between_autostart_in_seconds )

                self.start_virtual_machine( virtual_machine.get_uuid() )
                previous_virtual_machine_was_already_running = False
                need_one_last_sleep = True

        if need_one_last_sleep:
            # Delay ensuring the running status of the last virtual machine
            # starts up and is captured in the immediate update.
            time.sleep( 10 )


    def _get_virtual_machines_for_autostart(
        self,
        virtual_machines ):

        virtual_machines_for_autostart = [ ]
        for item in virtual_machines:
            if isinstance( item, Group ):
                virtual_machines_for_autostart += (
                    self._get_virtual_machines_for_autostart(
                        item.get_items() ) )

            else:
                if self.is_autostart( item.get_uuid() ):
                    virtual_machines_for_autostart.append( item )

        return virtual_machines_for_autostart


    def start_virtual_machine(
        self,
        uuid ):

        result = self.process_get( "VBoxManage list vms | grep " + uuid )
        if uuid not in result:
            message = _(
                "The virtual machine could not be found - " +
                "perhaps it has been renamed or deleted.  " +
                "The list of virtual machines has been refreshed - " +
                "please try again." )

            self.show_notification( _( "Error" ), message )

        else:
            self.process_call(
                self.get_start_command( uuid ).replace( "%VM%", uuid ) + " &" )


    def bring_window_to_front(
        self,
        virtual_machine_name,
        delay_in_seconds = 0 ):

        if not self.is_session_type_wayland():
            number_of_windows_with_the_same_name = (
                self.process_get(
                    'wmctrl -l | grep "' +
                    virtual_machine_name + '" | wc -l' ) )

            if number_of_windows_with_the_same_name == "0":
                message = _(
                    "Unable to find the window for the virtual machine '{0}' " +
                    "- perhaps it is running as headless." ).format(
                        virtual_machine_name )

                summary = _( "Warning" )
                self.show_notification_with_delay(
                    summary,
                    message,
                    delay_in_seconds = delay_in_seconds )

            elif number_of_windows_with_the_same_name == "1":
                for line in self.process_get( "wmctrl -l" ).splitlines():
                    if virtual_machine_name in line:
                        window_id = line[ 0 : line.find( " " ) ]
                        self.process_call( "wmctrl -i -a " + window_id )
                        break

            else:
                message = _(
                    "Unable to bring the virtual machine '{0}' to front " +
                    "as there is more than one window " +
                    "with overlapping names." ).format( virtual_machine_name )

                summary = _( "Warning" )
                self.show_notification_with_delay(
                    summary,
                    message,
                    delay_in_seconds = delay_in_seconds )


    def show_notification_with_delay(
        self,
        summary,
        message,
        delay_in_seconds = 0 ):
        '''
        Zealous mouse wheel scrolling can cause too many notifications,
        subsequently popping the graphics stack!
        Prevent notifications from appearing until a set time has elapsed since
        the previous notification.
        '''
        date_time_of_last_notification_plus_delay = (
            self.date_time_of_last_notification
            +
            datetime.timedelta( seconds = delay_in_seconds ) )

        if date_time_of_last_notification_plus_delay < datetime.datetime.now():
            self.show_notification( summary, message )
            self.date_time_of_last_notification = datetime.datetime.now()


    def on_mouse_wheel_scroll(
        self,
        indicator,
        delta,
        scroll_direction ):

        if self.is_vboxmanage_installed():
            running_names, running_uuids = self.get_running_virtual_machines()
            if running_uuids:
                if self.scroll_uuid is None or self.scroll_uuid not in running_uuids:
                    self.scroll_uuid = running_uuids[ 0 ]

                if scroll_direction == Gdk.ScrollDirection.UP:
                    index = (
                        ( running_uuids.index( self.scroll_uuid ) + 1 )
                        %
                        len( running_uuids ) )

                    self.scroll_uuid = running_uuids[ index ]
                    self.scroll_direction_is_up = True

                else:
                    index = (
                        ( running_uuids.index( self.scroll_uuid ) - 1 )
                        %
                        len( running_uuids ) )

                    self.scroll_uuid = running_uuids[ index ]
                    self.scroll_direction_is_up = False

                self.bring_window_to_front(
                    running_names[ running_uuids.index( self.scroll_uuid ) ],
                    10 )


    def on_launch_virtual_box_manager( self ):

        def start_virtualbox_manager():
            self.process_call( self.process_get( "which VirtualBox" ) + " &" )


        if self.is_session_type_wayland():
            # Wayland does not support wmctrl.
            # If the VirtualBox manager is already running,
            # there is no ability to bring to the front.
            # Can only run VirtualBox manager again and again...
            start_virtualbox_manager()

        else:
            # Only want one instance of VirtualBox manager to be running
            # (as a convenience to the user to avoidable multiple versions).
            #
            # The executable for VirtualBox manager does not necessarily appear
            # in the process list because the executable might be a script which
            # calls another executable.
            #
            # Instead, the user specifies the title of the VirtualBox manager
            # window in the preferences and using that, find the window by the
            # window title.
            window_id = None
            command = (
                f"wmctrl -l | grep \"{ self.virtualbox_manager_window_name }\"" )

            result = self.process_get( command )
            if result:
                window_id = result.split()[ 0 ]
                self.process_call( f"wmctrl -ia { window_id }" )

            else:
                start_virtualbox_manager()


    def get_running_virtual_machines( self ):
        '''
        Returns a list of running VM names and list of corresponding
        running VM UUIDs.
        '''
        names = [ ]
        uuids = [ ]
        result = self.process_get( "VBoxManage list runningvms" )
        for line in result.splitlines():
            if line.startswith( '\"' ) and line.endswith( '}' ):
                # VBoxManage may emit a warning message along with the VM
                # information, so check each line as best as possible.
                info = line[ 1 : -1 ].split( "\" {" )
                names.append( info[ 0 ] )
                uuids.append( info[ 1 ] )

        return names, uuids


    def is_virtual_machine_running(
        self,
        uuid ):

        command = "VBoxManage list runningvms | grep " + uuid
        return bool( self.process_get( command ) )


    def get_virtual_machines( self ):

        def add_virtual_machine(
            start_group,
            name,
            uuid,
            groups ):

            current_group = start_group
            for group in groups:
                group_to_find = None
                for item in current_group.get_items():
                    if (
                        isinstance( item, Group )
                        and
                        item.get_name() == group
                    ):
                        group_to_find = item
                        break # Assume group names within a group are unique.

                if group_to_find is None:
                    group_to_find = Group( group )
                    current_group.add_item( group_to_find )

                current_group = group_to_find

            current_group.add_item( VirtualMachine( name, uuid ) )


        top_group = Group( "" )
        command = "VBoxManage list vms --long"
        for line in self.process_get( command ).splitlines():
            if line.startswith( "Name:" ):
                name = line.split( "Name:" )[ 1 ].strip()

            elif line.startswith( "Groups:" ):
                groups = line.split( '/' )[ 1 : ]
                if groups[ 0 ] == '':
                    del groups[ 0 ]

            elif line.startswith( "UUID:" ):
                uuid = line.split( "UUID:" )[ 1 ].strip()
                add_virtual_machine( top_group, name, uuid, groups )

        return top_group.get_items()


    def is_vboxmanage_installed( self ):
        return self.process_get( "which VBoxManage" ).find( "VBoxManage" ) > -1


    def get_start_command(
        self,
        uuid ):

        start_command = IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT
        if uuid in self.virtual_machine_preferences:
            preferences = self.virtual_machine_preferences[ uuid ]
            start_command = preferences[ IndicatorVirtualBox.PREFERENCES_START_COMMAND ]

        return start_command


    def is_autostart(
        self,
        uuid ):

        return (
            uuid in self.virtual_machine_preferences
            and
            self.virtual_machine_preferences[ uuid ][ IndicatorVirtualBox.PREFERENCES_AUTOSTART ] )


    def on_preferences(
        self,
        dialog ):

        notebook = Gtk.Notebook()
        notebook.set_margin_bottom( IndicatorBase.INDENT_WIDGET_TOP )

        # Group name (remaining data is empty).
        #   or
        # Virtual machine name, autostart, start command, UUID.
        treestore = Gtk.TreeStore( str, bool, str, str )

        items = [ ]
        if self.is_vboxmanage_installed():
            items = self.get_virtual_machines()

        groups_exist = self._add_items_to_store( treestore, None, items )

        renderer_autostart = (
            self.create_cell_renderer_toggle_for_checkbox_within_treeview(
                treestore,
                IndicatorVirtualBox.COLUMN_AUTOSTART ) )

        renderer_start_command = Gtk.CellRendererText()
        renderer_start_command.connect(
            "edited",
            self.on_edited_start_command,
            treestore,
            dialog )

        if self.is_vboxmanage_installed():
            if items:
                tooltip_text = _(
                    "Click on a virtual machine's start command to edit.\n\n" +
                    "The start command takes the form:\n\n" +
                    "\tVBoxManage startvm %VM%\n" +
                    "or\n" +
                    "\tVBoxHeadless --startvm %VM% --vrde off\n\n" +
                    "An empty start command resets to default." )

            else:
                tooltip_text = _( "No virtual machines found." )

        else:
            tooltip_text = IndicatorVirtualBox.MESSAGE_NOT_INSTALLED + '.'

        treeview, scrolledwindow = (
            self.create_treeview_within_scrolledwindow(
                treestore,
                (
                    _( "Groups / Virtual Machines" ),
                    _( "Autostart" ),
                    _( "Start Command" ) ),
                (
                    (
                        Gtk.CellRendererText(),
                        "text",
                        IndicatorVirtualBox.COLUMN_GROUP_OR_VIRTUAL_MACHINE_NAME ),
                    (
                        renderer_autostart,
                        "active",
                        IndicatorVirtualBox.COLUMN_AUTOSTART ),
                    (
                        renderer_start_command,
                        "text",
                        IndicatorVirtualBox.COLUMN_START_COMMAND ) ),
                alignments_columnviewids = (
                    ( 0.5, IndicatorVirtualBox.COLUMN_AUTOSTART ), ),
                tooltip_text = tooltip_text,
                celldatafunctionandarguments_renderers_columnviewids = (
                    (
                        ( self.column_renderer_function, ),
                        renderer_autostart,
                        IndicatorVirtualBox.COLUMN_AUTOSTART ),
                    (
                        ( self.column_renderer_function, ),
                        renderer_start_command,
                        IndicatorVirtualBox.COLUMN_START_COMMAND ) ) ) )


        notebook.append_page(
            scrolledwindow, Gtk.Label.new( _( "Virtual Machines" ) ) )

        # General settings.
        grid = self.create_grid()

        window_name = (
            self.create_entry(
                self.virtualbox_manager_window_name,
                tooltip_text = _(
                    "The window title of VirtualBox™ Manager.\n" +
                    "You may have to adjust for your local language.\n\n" +
                    "This is used to bring the VirtualBox™ Manager\n" +
                    "window to the front if already running.\n\n" +
                    "This is unsupported under Wayland." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "VirtualBox™ Manager" ) ), False ),
                    ( window_name, True ) ) ),
            0, 0, 1, 1 )

        sort_groups_and_virtual_machines_equally_checkbox = (
            self.create_checkbutton(
                _( "Sort groups and virtual machines equally" ),
                tooltip_text = _(
                    "If checked, groups and virtual machines\n" +
                    "are sorted without distinction.\n\n" +
                    "Otherwise, groups are sorted first,\n" +
                    "followed by virtual machines." ),
                active = self.sort_groups_and_virtual_machines_equally ) )

        grid.attach(
            sort_groups_and_virtual_machines_equally_checkbox, 0, 1, 1, 1 )

        show_as_submenus_checkbox = (
            self.create_checkbutton(
                _( "Show groups as submenus" ),
                tooltip_text = _(
                    "If checked, groups are shown using submenus.\n\n" +
                    "Otherwise, groups are shown as an indented list." ),
                active = self.show_submenu ) )

        row = 2
        if groups_exist:
            grid.attach( show_as_submenus_checkbox, 0, row, 1, 1 )
            row += 1

        spinner_refresh_interval = (
            self.create_spinbutton(
                self.refresh_interval_in_minutes,
                1,
                60,
                page_increment = 5,
                tooltip_text = _(
                    "How often the list of virtual machines\n" +
                    "and their running status are updated." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Refresh interval (minutes)" ) ), False ),
                    ( spinner_refresh_interval, False ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, row, 1, 1 )
        row += 1

        spinner_delay = (
            self.create_spinbutton(
                self.delay_between_autostart_in_seconds,
                1,
                300,
                page_increment = 30,
                tooltip_text = _(
                    "Amount of time to wait from automatically\n" +
                    "starting one virtual machine to the next." ) ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Startup delay (seconds)" ) ), False ),
                    ( spinner_delay, False ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ),
            0, row, 1, 1 )
        row += 1

        autostart_checkbox, delay_spinner, latest_version_checkbox, box = (
            self.create_preferences_common_widgets() )

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

            self._update_virtual_machine_preferences(
                treestore, treeview.get_model().get_iter_first() )

            self.set_preferences_common_attributes(
                autostart_checkbox.get_active(),
                delay_spinner.get_value_as_int(),
                latest_version_checkbox.get_active() )

        return response_type


    def _add_items_to_store(
        self,
        model,
        parent,
        items ):

        groups_exist = False
        sorted_items = (
            Group.sort( items, self.sort_groups_and_virtual_machines_equally ) )

        for item in sorted_items:
            if isinstance( item, Group ):
                groups_exist = True
                self._add_items_to_store(
                    model,
                    model.append(
                        parent, [ item.get_name(), None, None, None ] ),
                    item.get_items() )

            else:
                row = [
                    item.get_name(),
                    self.is_autostart( item.get_uuid() ),
                    self.get_start_command( item.get_uuid() ),
                    item.get_uuid() ]
                model.append( parent, row )

        return groups_exist


    def column_renderer_function(
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
        uuid = model[ iter_ ][ IndicatorVirtualBox.COLUMN_UUID ]
        treeview = treeviewcolumn.get_tree_view()
        if treeview.get_column( IndicatorVirtualBox.COLUMN_AUTOSTART ) == treeviewcolumn:
            cell_renderer.set_visible( uuid is not None )

        if treeview.get_column( IndicatorVirtualBox.COLUMN_START_COMMAND ) == treeviewcolumn:
            cell_renderer.set_property( "editable", uuid is not None )


    def on_edited_start_command(
        self,
        cell_renderer,
        path,
        text_new,
        model,
        dialog ):

        start_command = text_new.strip()
        if len( start_command ) == 0:
            start_command = (
                IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT )

        if "%VM%" in start_command:
            model[ path ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] = (
                start_command )

        else:
            self.show_dialog_ok(
                dialog,
                _(
                    "The start command must contain\n" +
                    "\t%VM%\n\n" +
                    "which is substituted for the UUID." ) )


    def _update_virtual_machine_preferences(
        self,
        model,
        iter_ ):

        while iter_:
            row = model[ iter_ ]
            is_virtual_machine = row[ IndicatorVirtualBox.COLUMN_UUID ]
            is_autostart = row[ IndicatorVirtualBox.COLUMN_AUTOSTART ]
            is_default_start_command = (
                row[ IndicatorVirtualBox.COLUMN_START_COMMAND ]
                ==
                IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT )
            
            if (
                ( is_virtual_machine and is_autostart )
                or
                ( is_virtual_machine and not is_default_start_command ) ):

                # Only record VMs with different settings to default.
                key = row[ IndicatorVirtualBox.COLUMN_UUID ]
                value = [ is_autostart, row[ IndicatorVirtualBox.COLUMN_START_COMMAND ] ]
                self.virtual_machine_preferences[ key ] = value

            if model.iter_has_child( iter_ ):
                childiter = model.iter_children( iter_ )
                self._update_virtual_machine_preferences( model, childiter )

            iter_ = model.iter_next( iter_ )


    def load_config(
        self,
        config ):

        self.delay_between_autostart_in_seconds = (
            config.get(
                IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS,
                10 ) )

        self.refresh_interval_in_minutes = (
            config.get(
                IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES,
                15 ) )

        self.show_submenu = (
            config.get(
                IndicatorVirtualBox.CONFIG_SHOW_SUBMENU,
                True ) )

        self.sort_groups_and_virtual_machines_equally = (
            config.get(
                IndicatorVirtualBox.CONFIG_SORT_GROUPS_AND_VIRTUAL_MACHINES_EQUALLY,
                True ) )

        # Store information about VMs.
        #   Key is VM UUID
        #   Value is [ autostart (bool), start command (str) ]
        self.virtual_machine_preferences = (
            config.get(
                IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES,
                { } ) )

        self.virtualbox_manager_window_name = (
            config.get(
                IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME,
                "Oracle VM VirtualBox Manager" ) )


    def save_config( self ):
        return {
            IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS:
                self.delay_between_autostart_in_seconds,

            IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES:
                self.refresh_interval_in_minutes,

            IndicatorVirtualBox.CONFIG_SHOW_SUBMENU:
                self.show_submenu,

            IndicatorVirtualBox.CONFIG_SORT_GROUPS_AND_VIRTUAL_MACHINES_EQUALLY:
                self.sort_groups_and_virtual_machines_equally,

            IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES:
                self.virtual_machine_preferences,

            IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME:
                self.virtualbox_manager_window_name
        }


IndicatorVirtualBox().main()
