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


#TODO Need to get translation done.


INDICATOR_NAME = "indicator-virtual-box"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gdk", "3.0" )
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gdk, Gtk, Notify

import indicatorbase, datetime, os, time, virtualmachine


class IndicatorVirtualBox( indicatorbase.IndicatorBase ):

    CONFIG_DELAY_BETWEEN_AUTO_START = "delayBetweenAutoStartInSeconds"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_VIRTUAL_MACHINE_PREFERENCES = "virtualMachinePreferences"
    CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME = "virtualboxManagerWindowName"

    VIRTUAL_BOX_CONFIGURATION = os.getenv( "HOME" ) + "/.config/VirtualBox/VirtualBox.xml"
    VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT = "VBoxManage startvm %VM%"


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.67",
            copyrightStartYear = "2012",
            comments = _( "Shows VirtualBox™ virtual machines and allows them to be started." ) )

        self.autoStartRequired = True
        self.dateTimeOfLastNotification = datetime.datetime.now()
        self.scrollDirectionIsUp = True
        self.scrollUUID = None

        self.requestMouseWheelScrollEvents()


    def update( self, menu ):
        virtualMachines = self.getVirtualMachines()

        if self.autoStartRequired and self.isVBoxManageInstalled():
            self.autoStartRequired = False
            self.autoStartVirtualMachines( virtualMachines )

        if self.isVBoxManageInstalled():
            self.buildMenu( menu, virtualMachines )

        else:
            menu.append( Gtk.MenuItem.new_with_label( _( "(VirtualBox™ is not installed)" ) ) )

        return int( 60 * self.refreshIntervalInMinutes )


    def buildMenu( self, menu, virtualMachines ):
        if virtualMachines: #TODO Check this works for empty VMs.
            runningVMNames, runningVMUUIDs = self.getRunningVirtualMachines()
            for item in virtualMachines:
                if type( item ) == virtualmachine.Group:
                    self.addMenuItemForGroupAndChildren( menu, item, 0 )

                else:
                    self.addMenuItemForVirtualMachine( menu, item, 0, item.getUUID() in runningVMUUIDs ) #TODO Maybe pass in runningVMUUIDs into here and the group function so that it can be passed all the way along.

        else:
            menu.append( Gtk.MenuItem.new_with_label( _( "(no virtual machines exist)" ) ) )

        menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.MenuItem.new_with_label( _( "Launch VirtualBox™ Manager" ) )
        menuItem.connect( "activate", self.onLaunchVirtualBoxManager )
        menu.append( menuItem )
        self.secondaryActivateTarget = menuItem


    def addMenuItemForGroupAndChildren( self, menu, group, level ):
        indent = level * self.indent( 0, 1 )
        menuItem = Gtk.MenuItem.new_with_label( indent + "--- " + group.getName() + " ---" ) #TODO Not sure about the --- used to distinguish for groups...ask Oleg.
        menu.append( menuItem )

        if self.showSubmenu:
            menu = Gtk.Menu()
            menuItem.set_submenu( menu )

        for item in group.getItems():
            if type( item ) == virtualmachine.Group:
                self.addMenuItemForGroupAndChildren( menu, item, level + 1 )

            else:
                self.addMenuItemForVirtualMachine( menu, item, level + 1, False ) #TODO Fix: False should be something like item.getUUID() in runningVMUUIDs ) )


    def addMenuItemForVirtualMachine( self, menu, virtualMachine, level, isRunning ):
        indent = level * self.indent( 0, 1 )
        if isRunning:
            menuItem = Gtk.RadioMenuItem.new_with_label( [ ], indent + virtualMachine.getName() )
            menuItem.set_active( True )

        else:
            menuItem = Gtk.MenuItem.new_with_label( indent + virtualMachine.getName() )

        menuItem.connect( "activate", self.startVirtualMachine, virtualMachine.getUUID() )
        menu.append( menuItem )


    def autoStartVirtualMachines( self, virtualMachines ):
        if True: return #TODO Fix below...will need to be recursive!
        for virtualMachine in virtualMachines:
            if self.isAutostart( virtualMachine.getUUID() ):
                time.sleep( self.delayBetweenAutoStartInSeconds )
                self.startVirtualMachine( None, virtualMachine.getUUID(), False )


    def startVirtualMachine( self, menuItem, uuid, requiresUpdate = True ):
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


    def onLaunchVirtualBoxManager( self, menuItem ):
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

                except Exception:
                    pass # Sometimes VBoxManage emits a warning message along with the VM information.

        return names, uuids


    # Returns a list of virtualmachine and group objects reflecting VMs and groups as found via VBoxManage and configuration files.
    def getVirtualMachines( self ):
        virtualMachines = [ ]
        if self.isVBoxManageInstalled():
            virtualMachinesFromVBoxManage = self.getVirtualMachinesFromVBoxManage()

            if os.path.isfile( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION ):
                try:
                    with open( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION, 'r' ) as f:
                        lines = f.readlines()

                    for line in lines:
                        if "GUI/GroupDefinitions/" in line:
                            parts = line.split( "\"" )
                            if parts[ 1 ] == "GUI/GroupDefinitions/": # Top level groups/VMs...add to list.
#TODO Consider creating a group to start with and add all top level items to it.
# At the end of this function, return the top level group's items.
# Then can these two sections be combined?
                                groupNamesAndUUIDs = parts[ 3 ].split( ',' )
                                for item in groupNamesAndUUIDs:
                                    if item.startswith( "go=" ):
                                        virtualMachines.append( virtualmachine.Group( item.replace( "go=", "" ) ) )

                                    else:
                                        uuid = item.replace( "m=", "" )
                                        name = next( x for x in virtualMachinesFromVBoxManage if x.getUUID() == uuid ).getName()
                                        virtualMachines.append( virtualmachine.VirtualMachine( name, uuid ) )

                            else: # Subsequent groups and groups/VMs within...
                                path = parts[ 1 ].split( '/' )[ 2 : ]
                                groupItems = virtualMachines
                                for groupName in path:
                                    group = next( x for x in groupItems if type( x ) == virtualmachine.Group and x.getName() == groupName )
                                    groupItems = group.getItems()

                                groupNamesAndUUIDs = parts[ 3 ].split( ',' )
                                for item in groupNamesAndUUIDs:
                                    if item.startswith( "go=" ):
                                        group.addItem( virtualmachine.Group( item.replace( "go=", "" ) ) )

                                    else:
                                        uuid = item.replace( "m=", "" )
                                        name = next( x for x in virtualMachinesFromVBoxManage if x.getUUID() == uuid ).getName()
                                        group.addItem( virtualmachine.VirtualMachine( name, uuid ) )

                except Exception as e:
                    self.getLogging().exception( e )
                    virtualMachines = [ ]

            else:
                virtualMachines = virtualMachinesFromVBoxManage

        return virtualMachines


    # Returns a list of virtualmachine objects from calling VBoxManage.
    # Contains no group information, nor sort order which is set by the user in the GUI.
    # Safe to call without checking if VBoxManage is installed.
    def getVirtualMachinesFromVBoxManage( self ):
        virtualMachines = [ ]
        result = self.processGet( "VBoxManage list vms" )
        if result: # If a VM is corrupt/missing, VBoxManage can give back a spurious (None) result.
            for line in result.splitlines():
                try:
                    nameAndUUID = line[ 1 : -1 ].split( "\" {" )
                    virtualMachines.append( virtualmachine.VirtualMachine( nameAndUUID[ 0 ], nameAndUUID[ 1 ] ) )

                except Exception:
                    pass # Sometimes VBoxManage emits a warning message along with the VM information.

        return virtualMachines


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
        print()#TODOTesting
        notebook = Gtk.Notebook()

        # List of VMs.
        def addItemsToStore( parent, items ):
            groupsExist = False
            for item in items:
                if type( item ) == virtualmachine.Group:
                    groupsExist = True
                    addItemsToStore( store.append( parent, [ item.getName(), None, None, None ] ), item.getItems() )
    
                else:
                    uuid = item.getUUID()        
                    store.append( parent, [ item.getName(), Gtk.STOCK_APPLY if self.isAutostart( uuid ) else None, self.getStartCommand( uuid ), uuid ] )

            return groupsExist

        store = Gtk.TreeStore( str, str, str, str ) # Group or virtual machine name, autostart, start command, UUID.
        groupsExist = addItemsToStore( None, self.getVirtualMachines() )

        tree = Gtk.TreeView.new_with_model( store )
        tree.expand_all()
        tree.set_hexpand( True )
        tree.set_vexpand( True )
        tree.append_column( Gtk.TreeViewColumn( _( "Virtual Machine" ), Gtk.CellRendererText(), text = 0 ) )
        tree.append_column( Gtk.TreeViewColumn( _( "Autostart" ), Gtk.CellRendererPixbuf(), stock_id = 1 ) )
        tree.append_column( Gtk.TreeViewColumn( _( "Start Command" ), Gtk.CellRendererText(), text = 2 ) )
        tree.set_tooltip_text( _( "Double click to edit a virtual machine's properties." ) )
        tree.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        tree.connect( "row-activated", self.onVirtualMachineDoubleClick )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( tree )
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )

        notebook.append_page( scrolledWindow, Gtk.Label.new( _( "Virtual Machines" ) ) )

        # General settings.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )
        box.set_hexpand( True )

        label = Gtk.Label.new( _( "VirtualBox™ Manager" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        windowName = Gtk.Entry()
        windowName.set_tooltip_text( _( \
            "The name (window title) of VirtualBox™ Manager.\n" + \
            "You may have to adjust for your local language." ) )
        windowName.set_text( self.virtualboxManagerWindowName )
        box.pack_start( windowName, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        showAsSubmenusCheckbox = Gtk.CheckButton.new_with_label( _( "Show groups as submenus" ) )
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

        box.pack_start( Gtk.Label.new( _( "Refresh interval (minutes)" ) ), False, False, 0 )

        spinnerRefreshInterval = Gtk.SpinButton()
        spinnerRefreshInterval.set_adjustment( Gtk.Adjustment.new( self.refreshIntervalInMinutes, 1, 60, 1, 5, 0 ) ) # Initial value is not applied...
        spinnerRefreshInterval.set_value( self.refreshIntervalInMinutes ) # ...so need to explicitly set.
        spinnerRefreshInterval.set_tooltip_text( _(
            "How often the list of virtual machines\n" + \
            "and running status are updated." ) )

        box.pack_start( spinnerRefreshInterval, False, False, 0 )

        grid.attach( box, 0, row, 1, 1 )
        row += 1

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Startup delay (seconds)" ) ), False, False, 0 )

        spinnerDelay = Gtk.SpinButton()
        spinnerDelay.set_adjustment( Gtk.Adjustment.new( self.delayBetweenAutoStartInSeconds, 1, 60, 1, 5, 0 ) ) # Initial value is not applied...
        spinnerDelay.set_value( self.delayBetweenAutoStartInSeconds ) # ...so need to explicitly set.
        spinnerDelay.set_tooltip_text( _(
            "Amount of time to wait from automatically\n" + \
            "starting one virtual machine to the next." ) )

        box.pack_start( spinnerDelay, False, False, 0 )

        grid.attach( box, 0, row, 1, 1 )
        row += 1

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

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

        return responseType


    def updateVirtualMachinePreferences( self, store, treeiter ):
        while treeiter:
            isVirtualMachine = store[ treeiter ][ 3 ] # UUID is not None, so this is a VM and not a group.
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
        if treeiter and model[ treeiter ][ 3 ]:
            self.editVirtualMachine( tree, model, treeiter )


    def editVirtualMachine( self, tree, model, treeiter ):
        grid = self.createGrid()

        label = Gtk.Label.new( _( "Start Command" ) )
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

        autostartCheckbox = Gtk.CheckButton.new_with_label( _( "Autostart" ) )
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
        self.delayBetweenAutoStartInSeconds = config.get( IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START, 10 )
        self.refreshIntervalInMinutes = config.get( IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES, 15 )
        self.showSubmenu = config.get( IndicatorVirtualBox.CONFIG_SHOW_SUBMENU, False )
        self.virtualMachinePreferences = config.get( IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES, { } ) # Store information about VMs.  Key is VM UUID; value is [ autostart (bool), start command (str) ]
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