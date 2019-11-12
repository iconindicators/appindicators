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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Application indicator for VirtualBox™ virtual machines.


INDICATOR_NAME = "indicator-virtual-box"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gdk", "3.0" )
gi.require_version( "GLib", "2.0" )
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gdk, GLib, Gtk, Notify

import indicatorbase, datetime, os, time, virtualmachine


class IndicatorVirtualBox( indicatorbase.IndicatorBase ):

    CONFIG_DELAY_BETWEEN_AUTO_START = "delayBetweenAutoStartInSeconds"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_VIRTUAL_MACHINE_PREFERENCES = "virtualMachinePreferences"
    CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME = "virtualboxManagerWindowName"

    VIRTUAL_BOX_CONFIGURATION_4_DOT_3_OR_GREATER = os.getenv( "HOME" ) + "/.config/VirtualBox/VirtualBox.xml"
    VIRTUAL_BOX_CONFIGURATION_PRIOR_4_DOT_3 = os.getenv( "HOME" ) + "/.VirtualBox/VirtualBox.xml"
    VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION = "4.3" # Configuration file location and format changed at this version (https://www.virtualbox.org/manual/ch10.html#idp99351072).

    VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT = "VBoxManage startvm %VM%"


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.62",
            copyrightStartYear = "2012",
            comments = _( "Shows VirtualBox™ virtual machines and allows them to be started." ) )

        self.scrollDirectionIsUp = True
        self.scrollUUID = None
        self.dateTimeOfLastNotification = datetime.datetime.now()

        self.requestMouseWheelScrollEvents()

#TODO Not sure why this is commented out.
# Test that autostart works and does not lock up the indicator, or cause delays.
# Also test with a VM that is just a dummy (no actually underlying VM) and so it hands on boot...does this hang the indicator?
#         if self.isVBoxManageInstalled():
#             GLib.idle_add( self.autoStartVirtualMachines )
#             GLib.timeout_add_seconds( 10, self.autoStartVirtualMachines )
#             self.autoStartVirtualMachines()
        self.autoStartRequired = True
        print( "Leaving init" ) #TODO Remove


    def update( self, menu ):
        print( "Doing an update") #TODO Remove
        if self.isVBoxManageInstalled():
            if self.autoStartRequired:
                self.autoStartRequired = False
                self.autoStartVirtualMachines()  #TODO Test this on laptop with a dud VM...does it cause the indicator to hang?

            self.buildMenu( menu )

        else:
            menu.append( Gtk.MenuItem( _( "(VirtualBox™ is not installed)" ) ) )

        print( "Update complete")#TODO Testing
        return int( 60 * self.refreshIntervalInMinutes )


    def buildMenu( self, menu ):
        virtualMachines = self.getVirtualMachines()
        if len( virtualMachines ) == 0:
            menu.append( Gtk.MenuItem( _( "(no virtual machines exist)" ) ) )

        else:
            runningVMNames, runningVMUUIDs = self.getRunningVirtualMachines()
            if self.showSubmenu:
                stack = [ ]
                currentMenu = menu
                for virtualMachine in virtualMachines:
                    while virtualMachine.getIndent() < len( stack ):
                        currentMenu = stack.pop()

                    if virtualMachine.isGroup():
                        menuItem = Gtk.MenuItem( self.indent( 0, virtualMachine.getIndent() ) + virtualMachine.getGroupName() )
                        currentMenu.append( menuItem )
                        subMenu = Gtk.Menu()
                        menuItem.set_submenu( subMenu )
                        stack.append( currentMenu )
                        currentMenu = subMenu

                    else:
                        currentMenu.append( self.createMenuItemForVirtualMachine( virtualMachine, self.indent( 0, virtualMachine.getIndent() ), virtualMachine.getUUID() in runningVMUUIDs ) )

            else:
                for virtualMachine in virtualMachines:
                    indent = self.indent( virtualMachine.getIndent(), virtualMachine.getIndent() )
                    if virtualMachine.isGroup():
                        menu.append( Gtk.MenuItem( indent + virtualMachine.getGroupName() ) )

                    else:
                        menu.append( self.createMenuItemForVirtualMachine( virtualMachine, indent, virtualMachine.getUUID() in runningVMUUIDs ) )

        menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.MenuItem( _( "Launch VirtualBox™ Manager" ) )
        menuItem.connect( "activate", self.onLaunchVirtualBoxManager )
        menu.append( menuItem )
        self.secondaryActivateTarget = menuItem


    def createMenuItemForVirtualMachine( self, virtualMachine, indent, isRunning ):
        if isRunning:
            menuItem = Gtk.RadioMenuItem.new_with_label( [ ], indent + virtualMachine.getName() )
            menuItem.set_active( True )

        else:
            menuItem = Gtk.MenuItem( indent + virtualMachine.getName() )

        menuItem.connect( "activate", self.startVirtualMachine, virtualMachine.getUUID() )
        return menuItem


    def autoStartVirtualMachines( self ):
        for virtualMachine in self.getVirtualMachines():
            if self.isAutostart( virtualMachine.getUUID() ):
                self.startVirtualMachine( None, virtualMachine.getUUID(), False )
                print( "starting VM", virtualMachine.getUUID() )#TODO Testing
                time.sleep( self.delayBetweenAutoStartInSeconds )
                print( "awake")#TODO Testing


    def startVirtualMachine( self, widget, uuid, requiresUpdate = True ):
        runningVMNames, runningVMUUIDs = self.getRunningVirtualMachines()
        if uuid in runningVMUUIDs:
            self.bringWindowToFront( runningVMNames[ runningVMUUIDs.index( uuid ) ] )
            if requiresUpdate:
                self.requestUpdate()

        else:
            result = self.processGet( "VBoxManage list vms | grep " + uuid )
            if result is None or uuid not in result:
                message = _( "The virtual machine could not be found - perhaps it has been renamed or deleted.  The list of virtual machines has been refreshed - please try again." )
                Notify.Notification.new( _( "Error" ), message, self.icon ).show()

            else:
                self.processCall( self.getStartCommand( uuid ).replace( "%VM%", uuid ) + " &" )
                if requiresUpdate:
                    self.requestUpdate( 10 ) # Delay the refresh as the VM will have been started in the background and VBoxManage will not have had time to update.


    def bringWindowToFront( self, virtualMachineName ):
        numberOfWindowsWithTheSameName = self.processGet( 'wmctrl -l | grep "' + virtualMachineName + '" | wc -l' ).strip()
        if numberOfWindowsWithTheSameName == "0":
            message = _( "Unable to find the window for the virtual machine '{0}' - perhaps it is running as headless." ).format( virtualMachineName )
            summary = _( "Warning" )
            self.sendNotificationWithDelay( summary, message )

        elif numberOfWindowsWithTheSameName == "1":
            for line in self.processGet( "wmctrl -l" ).splitlines():
                if virtualMachineName in line:
                    windowID = line[ 0 : line.find( " " ) ]
                    self.processCall( "wmctrl -i -a " + windowID )
                    break

        else:
            message = _( "Unable to bring the virtual machine '{0}' to front as there is more than one window of the same name." ).format( virtualMachineName )
            summary = _( "Warning" )
            self.sendNotificationWithDelay( summary, message )


    # Zealous mouse wheel scrolling can cause too many notifications, subsequently popping the graphics stack!
    # Prevent notifications from appearing until a set time has elapsed since the previous notification.
    def sendNotificationWithDelay( self, summary, message ):
        if( self.dateTimeOfLastNotification + datetime.timedelta( seconds = 10 ) < datetime.datetime.now() ):
            Notify.Notification.new( summary, message, self.icon ).show()
            self.dateTimeOfLastNotification = datetime.datetime.now()


    # It is assumed that VirtualBox is installed!
    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        runningVMNames, runningVMUUIDs = self.getRunningVirtualMachines()
        if len( runningVMUUIDs ) > 0:
            if self.scrollUUID is None or self.scrollUUID not in runningVMUUIDs:
                self.scrollUUID = runningVMUUIDs[ 0 ]

            if scrollDirection == Gdk.ScrollDirection.UP:
                index = ( runningVMUUIDs.index( self.scrollUUID ) + 1 ) % len( runningVMUUIDs )
                self.scrollUUID = runningVMUUIDs[ index ]
                self.scrollDirectionIsUp = True

            else:
                index = ( runningVMUUIDs.index( self.scrollUUID ) - 1 ) % len( runningVMUUIDs )
                self.scrollUUID = runningVMUUIDs[ index ]
                self.scrollDirectionIsUp = False

            self.bringWindowToFront( runningVMNames[ runningVMUUIDs.index( self.scrollUUID ) ] )


    def onLaunchVirtualBoxManager( self, widget ):
        # The executable VirtualBox may exist in different locations, depending on how it was installed.
        # No need to check for a None value as this function will never be called if VBoxManage (VirtualBox) is not installed.
        virtualBoxExecutable = self.processGet( "which VirtualBox" ).strip()

        # The executable for VirtualBox manager was not always appearing in the process list
        # because the executable might be a script which calls another executable.
        # So using processes to find the window kept failing.
        # Instead, now have the user type in the title of the window into the preferences and find the window by that.
        result = self.processGet( "wmctrl -l | grep \"" + self.virtualboxManagerWindowName + "\"" )
        windowID = None
        if result:
            windowID = result.split()[ 0 ]

        if windowID is None or windowID == "":
            self.processCall( virtualBoxExecutable + " &" )

        else:
            self.processCall( "wmctrl -ia " + windowID )


    # Returns a list of running VM names and list of corresponding running VM UUIDs.
    def getRunningVirtualMachines( self ):
        names = [ ]
        uuids = [ ]
        result = self.processGet( "VBoxManage list runningvms" )
        if result:
            for line in result.splitlines():
                try:
                    info = line[ 1 : -1 ].split( "\" {" )
                    names.append( info[ 0 ] )
                    uuids.append( info[ 1 ] )

                except:
                    pass # Sometimes VBoxManage emits a warning message along with the VM information.

        return names, uuids


    # Returns a list of virtualmachine.Info objects reflecting VMs and groups as found via VBoxManage and configuration files.
    def getVirtualMachines( self ):
        virtualMachines = [ ]
        if self.isVBoxManageInstalled():
            version = self.getVirtualBoxVersion()
            if version:
                if version < IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION:
                    virtualMachinesFromConfig = self.__getVirtualMachinesFromConfigPriorTo4dot3()

                else:
                    virtualMachinesFromConfig = self.__getVirtualMachinesFromConfig4dot3OrGreater()

                virtualMachinesFromVBoxManage = self.__getVirtualMachinesFromVBoxManage() # Contains no group information, nor sort order.
                if len( virtualMachinesFromConfig ) == 0: # If the user did not modify VM sort order, there will be no list of VMs in the config file, so use the result from VBoxManage.
                    virtualMachinesFromConfig = virtualMachinesFromVBoxManage

                # Going forward, the virtual machine infos from the config is the definitive list of VMs (and groups, if any).
                virtualMachines = virtualMachinesFromConfig

                # The virtual machine infos from the config do not contain the names of virtual machines.
                # Obtain the names from the virtual machine infos from VBoxManage.
                for virtualmachineFromVBoxManage in virtualMachinesFromVBoxManage:
                    for virtualMachine in virtualMachines:
                        if virtualmachineFromVBoxManage.getUUID() == virtualMachine.getUUID():
                            virtualMachine.setName( virtualmachineFromVBoxManage.getName() )
                            break

        return virtualMachines


    # The returned list of virtualmachine.Info objects does not include any groups (if present) nor any order set by the user in the GUI.
    # Safe to call without checking if VBoxManage is installed.
    def __getVirtualMachinesFromVBoxManage( self ):
        virtualMachines = [ ]
        result = self.processGet( "VBoxManage list vms" )
        if result: # If a VM is corrupt/missing, VBoxManage can give back a spurious (None) result.
            for line in result.splitlines():
                try:
                    info = line[ 1 : -1 ].split( "\" {" )
                    virtualMachine = virtualmachine.Info( info[ 0 ], False, info[ 1 ], 0 )
                    virtualMachines.append( virtualMachine )

                except:
                    pass # Sometimes VBoxManage emits a warning message along with the VM information.

        return virtualMachines


    def __getVirtualMachinesFromConfigPriorTo4dot3( self ):
        virtualMachines = [ ]
        line = self.processGet( "grep GUI/SelectorVMPositions " + IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_PRIOR_4_DOT_3 )
        try:
            uuids = list( line.rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )
            for uuid in uuids:
                virtualMachines.append( virtualmachine.Info( "", False, uuid, 0 ) )                

        except Exception as e:
            self.getLogging().exception( e )
            virtualMachines = [ ] # The VM order has never been altered giving an empty result (and exception).

        return virtualMachines


    def __getVirtualMachinesFromConfig4dot3OrGreater( self ):
        # The config file may exist in one of two places, particularly if the user has done an upgrade or uses an older version of Ubuntu.
        # https://www.virtualbox.org/manual/ch10.html
        configFile = None
        if os.path.isfile( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_4_DOT_3_OR_GREATER ):
            configFile = IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_4_DOT_3_OR_GREATER

        elif os.path.isfile( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_PRIOR_4_DOT_3 ):
            configFile = IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_PRIOR_4_DOT_3

        virtualMachines = [ ]
        if configFile:
            try:
                with open( configFile, "r" ) as f:
                    content = f.readlines()

                # Parse all group definition tags extracting each group name and contents (which may be group names and/or VMs).
                groupDefinitions = { }
                for line in content:
                    if "\"GUI/GroupDefinitions/" in line:
                        parts = line.split( "\"" )
                        groupDefinitions[ parts[ 1 ] ] = parts[ 3 ]

                # Process the top level tag first...
                i = 0
                key = "GUI/GroupDefinitions/"
                if len( groupDefinitions ) > 0 and key in groupDefinitions: 
                    values = groupDefinitions[ key ].split( "," )
                    for value in values:
                        if value.startswith( "go=" ):
                            virtualMachines.insert( i, virtualmachine.Info( key + value.replace( "go=", "" ), True, "", 0 ) )

                        else:
                            virtualMachines.insert( i, virtualmachine.Info( "", False, value.replace( "m=", "" ), 0 ) )
    
                        i += 1

                # Now have a list of virtual machine infos containing top level groups and/or VMs.
                # Process the list and where a group is found, add in its children (groups and/or VMs).
                i = 0
                while i < len( virtualMachines ):
                    if virtualMachines[ i ].isGroup():
                        indent = virtualMachines[ i ].getIndent() + 1
                        key = virtualMachines[ i ].getName()
                        values = groupDefinitions[ key ].split( "," )
                        j = i + 1
                        for value in values:
                            if value.startswith( "go=" ):
                                virtualMachines.insert( j, virtualmachine.Info( key + "/" + value.replace( "go=", "" ), True, "", indent ) )

                            else:
                                virtualMachines.insert( j, virtualmachine.Info( "", False, value.replace( "m=", "" ), indent ) )

                            j += 1

                    i += 1

            except Exception as e:
                self.getLogging().exception( e )
                virtualMachines = [ ]

        return virtualMachines


    # Returns the version number as a string or None if no version could be determined.
    # Safe to call without checking if VBoxManage is installed.
    def getVirtualBoxVersion( self ):
        result = self.processGet( "VBoxManage --version" )
        if result is None: # If a VM is corrupt/missing, VBoxManage may return a spurious (None) result.
            version = None

        else:
            for line in result.splitlines():
                if len( line ) > 0 and line[ 0 ].isdigit(): # The result may include compile warnings in addition to the actual version number or even empty lines.
                    version = line
                    break

        return version


    def isVBoxManageInstalled( self ): 
        isInstalled = False
        result = self.processGet( "which VBoxManage" )
        if result:
            isInstalled = result.find( "VBoxManage" ) > -1

        return isInstalled


    def getStartCommand( self, uuid ):
        if uuid in self.virtualMachinePreferences:
            return self.virtualMachinePreferences[ uuid ][ 1 ]

        return IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT


    def isAutostart( self, uuid ): return uuid in self.virtualMachinePreferences and self.virtualMachinePreferences[ uuid ][ 0 ]


    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

        # List of VMs.
        stack = [ ]
        store = Gtk.TreeStore( str, str, str, str ) # Name of VM/Group, tick icon (Gtk.STOCK_APPLY) or None for autostart of VM, VM start command, UUID.
        parent = None
        virtualMachines = self.getVirtualMachines()
        groupsExist = False
        for virtualMachine in virtualMachines:
            while virtualMachine.getIndent() < len( stack ):
                parent = stack.pop()

            if virtualMachine.isGroup():
                groupsExist = True
                stack.append( parent )
                parent = store.append( parent, [ virtualMachine.getGroupName(), None, "", virtualMachine.getUUID() ] )

            else:
                autoStart = None
                if self.isAutostart( virtualMachine.getUUID() ):
                    autoStart = Gtk.STOCK_APPLY

                store.append( parent, [ virtualMachine.getName(), autoStart, self.getStartCommand( virtualMachine.getUUID() ), virtualMachine.getUUID() ] )

        tree = Gtk.TreeView( store )
        tree.expand_all()
        tree.set_hexpand( True )
        tree.set_vexpand( True )
        tree.append_column( Gtk.TreeViewColumn( _( "Virtual Machine" ), Gtk.CellRendererText(), text = 0 ) )
        tree.append_column( Gtk.TreeViewColumn( _( "Autostart" ), Gtk.CellRendererPixbuf(), stock_id = 1 ) )
        tree.append_column( Gtk.TreeViewColumn( _( "Start Command" ), Gtk.CellRendererText(), text = 2 ) )
        tree.set_tooltip_text( _( "Double click to edit a virtual machine's properties." ) )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onVirtualMachineDoubleClick )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( tree )
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )

        notebook.append_page( scrolledWindow, Gtk.Label( _( "Virtual Machines" ) ) )

        # General settings.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True )

        label = Gtk.Label( _( "VirtualBox™ Manager" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        windowName = Gtk.Entry()
        windowName.set_tooltip_text( _( \
            "The name (window title) of VirtualBox™ Manager.\n" + \
            "You may have to adjust for your local language." ) )
        windowName.set_text( self.virtualboxManagerWindowName )
        box.pack_start( windowName, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        showAsSubmenusCheckbox = Gtk.CheckButton( _( "Show groups as submenus" ) )
        showAsSubmenusCheckbox.set_tooltip_text( _(
            "If checked, groups are shown using submenus.\n\n" + \
            "Otherwise groups are shown as an indented list." ) )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )

        row = 1
        if groupsExist:
            grid.attach( showAsSubmenusCheckbox, 0, row, 1, 1 )
            row += 1

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Refresh interval (minutes)" ) ), False, False, 0 )

        spinnerRefreshInterval = Gtk.SpinButton()
        spinnerRefreshInterval.set_adjustment( Gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerRefreshInterval.set_value( self.refreshIntervalInMinutes ) # ...so need to force the initial value by explicitly setting it.
        spinnerRefreshInterval.set_tooltip_text( _( "How often the list of virtual machines and running status are updated." ) )

        box.pack_start( spinnerRefreshInterval, False, False, 0 )

        grid.attach( box, 0, row, 1, 1 )
        row += 1

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Startup delay (seconds)" ) ), False, False, 0 )

        spinnerDelay = Gtk.SpinButton()
        spinnerDelay.set_adjustment( Gtk.Adjustment( self.delayBetweenAutoStartInSeconds, 1, 60, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerDelay.set_value( self.delayBetweenAutoStartInSeconds ) # ...so need to force the initial value by explicitly setting it.
        spinnerDelay.set_tooltip_text( _( "Amount of time to wait from automatically starting one virtual machine to the next." ) )

        box.pack_start( spinnerDelay, False, False, 0 )

        grid.attach( box, 0, row, 1, 1 )
        row += 1

        autostartCheckbox = self.createAutostartCheckbox() 
        grid.attach( autostartCheckbox, 0, row, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        responseType = dialog.run()
        if responseType == Gtk.ResponseType.OK:
            self.virtualboxManagerWindowName = windowName.get_text().strip()
            self.delayBetweenAutoStartInSeconds = spinnerDelay.get_value_as_int()
            self.showSubmenu = showAsSubmenusCheckbox.get_active()
            self.refreshIntervalInMinutes = spinnerRefreshInterval.get_value_as_int()
            self.virtualMachinePreferences.clear()
            self.updateVirtualMachinePreferences( store, tree.get_model().get_iter_first() )
            self.setAutoStart( autostartCheckbox.get_active() )

        return responseType


    def updateVirtualMachinePreferences( self, store, treeiter ):
        while treeiter:
            isVirtualMachine = store[ treeiter ][ 3 ] != "" # UUID is not empty, so this is a VM and not a group.
            isAutostart = store[ treeiter ][ 1 ] == "gtk-apply"
            isDefaultStartCommand = store[ treeiter ][ 2 ] == IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT
            if ( isVirtualMachine and isAutostart ) or ( isVirtualMachine and not isDefaultStartCommand ): # Only record VMs with different settings to default.
                self.virtualMachinePreferences[ store[ treeiter ][ 3 ] ] = [ store[ treeiter ][ 1 ] == "gtk-apply", store[ treeiter ][ 2 ] ]

            if store.iter_has_child( treeiter ):
                childiter = store.iter_children( treeiter )
                self.updateVirtualMachinePreferences( store, childiter )

            treeiter = store.iter_next( treeiter )


    def onVirtualMachineDoubleClick( self, tree, rowNumber, treeViewColumn ):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter and model[ treeiter ][ 3 ] != "":
            self.editVirtualMachine( tree, model, treeiter )


    def editVirtualMachine( self, tree, model, treeiter ):
        grid = self.createGrid()

        label = Gtk.Label( _( "Start Command" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        startCommand = Gtk.Entry()
        startCommand.set_width_chars( 20 )
        if model[ treeiter ][ 2 ]:
            startCommand.set_text( model[ treeiter ][ 2 ] )
            startCommand.set_width_chars( len( model[ treeiter ][ 2 ] ) * 5 / 4 ) # Sometimes the length is shorter than specified due to packing, so make it longer.

        startCommand.set_tooltip_text( _(
            "The terminal command to start the virtual machine such as\n\n" + \
            "\tVBoxManage startvm %VM%\n" + \
            "or\n" + \
            "\tVBoxHeadless --startvm %VM% --vrde off" ) )
        startCommand.set_hexpand( True ) # Only need to set this once and all objects will expand.
        grid.attach( startCommand, 1, 0, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the virtual machine when the indicator starts." ) )
        autostartCheckbox.set_active( model[ treeiter ][ 1 ] is not None and model[ treeiter ][ 1 ] == Gtk.STOCK_APPLY )
        grid.attach( autostartCheckbox, 0, 1, 2, 1 )

        dialog = self.createDialog( tree, _( "Virtual Machine Properties" ), grid )
        while True:
            dialog.show_all()

            if dialog.run() != Gtk.ResponseType.OK:
                break

            if startCommand.get_text().strip() == "":
                self.showMessage( dialog, _( "The start command cannot be empty." ) )
                startCommand.grab_focus()
                continue

            if not "%VM%" in startCommand.get_text().strip():
                self.showMessage( dialog, _( "The start command must contain %VM% which is substituted for the virtual machine name/id." ) )
                startCommand.grab_focus()
                continue

            # Ideally I'd like to do this...
            #
            #    if autostartCheckbox.get_active():
            #        model[ treeiter ][ 1 ] = Gtk.STOCK_APPLY
            #    else:
            #        model[ treeiter ][ 1 ] = None
            #
            #    model[ treeiter ][ 2 ] = startCommand.get_text().strip()
            #
            # But due to this bug https://bugzilla.gnome.org/show_bug.cgi?id=684094 cannot set the model value to None.
            # So this is the workaround...
            if autostartCheckbox.get_active():
                model.set_value( treeiter, 1, Gtk.STOCK_APPLY )
                model[ treeiter ][ 2 ] = startCommand.get_text().strip()

            else:
                model.insert_after( None, treeiter, [ model[ treeiter ][ 0 ], None, startCommand.get_text().strip(), model[ treeiter ][ 3 ] ] )
                model.remove( treeiter )
    
            break

        dialog.destroy()


    def loadConfig( self, config ):
        self.delayBetweenAutoStartInSeconds = config.get( IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START, 5 )
        self.refreshIntervalInMinutes = config.get( IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES, 15 )
        self.showSubmenu = config.get( IndicatorVirtualBox.CONFIG_SHOW_SUBMENU, False )
        self.virtualMachinePreferences = config.get( IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES, { } ) # Store information about VMs (not groups). Key is VM UUID; value is [ autostart (bool), start command (str) ]
        self.virtualboxManagerWindowName = config.get( IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME, "Oracle VM VirtualBox Manager" )


    def saveConfig( self ):
        return {
            IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START: self.delayBetweenAutoStartInSeconds,
            IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES: self.refreshIntervalInMinutes,
            IndicatorVirtualBox.CONFIG_SHOW_SUBMENU: self.showSubmenu,
            IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES: self.virtualMachinePreferences,
            IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME: self.virtualboxManagerWindowName
        }


IndicatorVirtualBox().main()