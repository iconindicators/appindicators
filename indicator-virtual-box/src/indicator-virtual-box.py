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


INDICATOR_NAME = "indicator-virtual-box"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gdk", "3.0" )
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gdk, Gtk, Notify
from indicatorbase import IndicatorBase
from virtualmachine import Group, VirtualMachine

import datetime, os, time


class IndicatorVirtualBox( IndicatorBase ):

    CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS = "delayBetweenAutoStartInSeconds"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_SORT_GROUPS_AND_VIRTUAL_MACHINES_EQUALLY = "sortGroupsAndVirtualMachinesEqually"
    CONFIG_VIRTUAL_MACHINE_PREFERENCES = "virtualMachinePreferences"
    CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME = "virtualboxManagerWindowName"

    VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT = "VBoxManage startvm %VM%"

    # Data model columns used in the Preferences dialog.
    COLUMN_GROUP_OR_VIRTUAL_MACHNINE_NAME = 0 # Either the group or name of the virtual machine.
    COLUMN_AUTOSTART = 1 # Icon name for the APPLY icon when the virtual machine is to autostart; None otherwise.
    COLUMN_START_COMMAND = 2 # Start command for the virtual machine.
    COLUMN_UUID = 3 # The UUID for the virtual machine (used to identify; not displayed).

    # Indices for preferences list (within a dictionary).
    PREFERENCES_AUTOSTART = 0
    PREFERENCES_START_COMMAND = 1


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.71",
            copyrightStartYear = "2012",
            comments = _( "Shows VirtualBox™ virtual machines and allows them to be started." ) )

        self.autoStartRequired = True
        self.dateTimeOfLastNotification = datetime.datetime.now()
        self.scrollDirectionIsUp = True
        self.scrollUUID = None

        self.requestMouseWheelScrollEvents()


    def update( self, menu ):
        if self.autoStartRequired: # Start VMs here so that the indicator icon is displayed immediately.
            self.autoStartRequired = False
            if self.isVBoxManageInstalled():
                self.autoStartVirtualMachines()

        self.buildMenu( menu )

        return int( 60 * self.refreshIntervalInMinutes )


    def buildMenu( self, menu ):
        if self.isVBoxManageInstalled():
            virtualMachines = self.getVirtualMachines()
            if virtualMachines:
                runningNames, runningUUIDs = self.getRunningVirtualMachines()
                self.__buildMenu( menu, self.getVirtualMachines(), 0, runningUUIDs )

            else:
                menu.append( Gtk.MenuItem.new_with_label( _( "(no virtual machines exist)" ) ) )

            menu.append( Gtk.SeparatorMenuItem() )

            menuItem = Gtk.MenuItem.new_with_label( _( "Launch VirtualBox™ Manager" ) )
            menuItem.connect( "activate", self.onLaunchVirtualBoxManager )
            menu.append( menuItem )
            self.secondaryActivateTarget = menuItem

        else:
            menu.append( Gtk.MenuItem.new_with_label( _( "(VirtualBox™ is not installed)" ) ) )


    def __buildMenu( self, menu, items, indent, runningUUIDs ):
        if self.sortGroupsAndVirtualMachinesEqually:
            sortedItems = sorted( items, key = lambda x: ( x.getName().lower() ) )

        else:
            sortedItems = sorted( items, key = lambda x: ( type( x ) is not Group, x.getName().lower() ) ) # Checking if an item is a group results in True (1) or False (0).

        for item in sortedItems:
            if type( item ) is Group:
                self.__buildMenu(
                    self.__addGroupToMenu( menu, item, indent, runningUUIDs ),
                    item.getItems(),
                    indent + 1,
                    runningUUIDs )

            else:
                self.__addVirtualMachineToMenu( menu, item, indent, item.getUUID() in runningUUIDs )


    def __addGroupToMenu( self, menu, group, level, runningUUIDs ):
        indent = level * self.getMenuIndent( 1 )
        menuItem = Gtk.MenuItem.new_with_label( indent + group.getName() )
        menu.append( menuItem )

        if self.showSubmenu:
            menu = Gtk.Menu()
            menuItem.set_submenu( menu )

        return menu


    def __addVirtualMachineToMenu( self, menu, virtualMachine, level, isRunning ):
        indent = level * self.getMenuIndent( 1 )
        if isRunning:
            menuItem = Gtk.RadioMenuItem.new_with_label( [ ], indent + virtualMachine.getName() )
            menuItem.set_active( True )

        else:
            menuItem = Gtk.MenuItem.new_with_label( indent + virtualMachine.getName() )

        menuItem.connect( "activate", self._onVirtualMachine, virtualMachine )
        menu.append( menuItem )


    def _onVirtualMachine( self, widget, virtualMachine ):
        if self.isVirtualMachineRunning( virtualMachine.getUUID() ):
            self.bringWindowToFront( virtualMachine.getName() )
            self.requestUpdate( 1 )

        else:
            self.startVirtualMachine( virtualMachine.getUUID() )
            self.requestUpdate( 10 ) # Delay the refresh as the VM will have been started in the background and VBoxManage will not have had time to update.


    def autoStartVirtualMachines( self ):
        virtualMachinesForAutoStart = [ ]
        self.__getVirtualMachinesForAutoStart( self.getVirtualMachines(), virtualMachinesForAutoStart )
        previousVirtualMachineWasAlreadyRunning = True
        while len( virtualMachinesForAutoStart ) > 0: # Start up each virtual machine and only insert the time delay if a machine was not already running.
            virtualMachine = virtualMachinesForAutoStart.pop()
            if self.isVirtualMachineRunning( virtualMachine.getUUID() ):
                self.bringWindowToFront( virtualMachine.getName() )
                previousVirtualMachineWasAlreadyRunning = True

            else:
                if not previousVirtualMachineWasAlreadyRunning:
                    time.sleep( self.delayBetweenAutoStartInSeconds )

                self.startVirtualMachine( virtualMachine.getUUID() )
                previousVirtualMachineWasAlreadyRunning = False


    def __getVirtualMachinesForAutoStart( self, virtualMachines, virtualMachinesForAutoStart ):
        for item in virtualMachines:
            if type( item ) is Group:
                self.__getVirtualMachinesForAutoStart( item.getItems(), virtualMachinesForAutoStart )

            else:
                if self.isAutostart( item.getUUID() ):
                    virtualMachinesForAutoStart.append( item )


    def startVirtualMachine( self, uuid ):
        result = self.processGet( "VBoxManage list vms | grep " + uuid )
        if result is None or uuid not in result:
            message = _( "The virtual machine could not be found - perhaps it has been renamed or deleted.  The list of virtual machines has been refreshed - please try again." )
            Notify.Notification.new( _( "Error" ), message, self.icon ).show()

        else:
            self.processCall( self.getStartCommand( uuid ).replace( "%VM%", uuid ) + " &" )


    def bringWindowToFront( self, virtualMachineName, delayInSeconds = 0 ):
        numberOfWindowsWithTheSameName = self.processGet( 'wmctrl -l | grep "' + virtualMachineName + '" | wc -l' ).strip()
        if numberOfWindowsWithTheSameName == "0":
            message = _( "Unable to find the window for the virtual machine '{0}' - perhaps it is running as headless." ).format( virtualMachineName )
            summary = _( "Warning" )
            self.sendNotificationWithDelay( summary, message, delayInSeconds )

        elif numberOfWindowsWithTheSameName == "1":
            for line in self.processGet( "wmctrl -l" ).splitlines():
                if virtualMachineName in line:
                    windowID = line[ 0 : line.find( " " ) ]
                    self.processCall( "wmctrl -i -a " + windowID )
                    break

        else:
            message = _( "Unable to bring the virtual machine '{0}' to front as there is more than one window with overlapping names." ).format( virtualMachineName )
            summary = _( "Warning" )
            self.sendNotificationWithDelay( summary, message, delayInSeconds )


    # Zealous mouse wheel scrolling can cause too many notifications, subsequently popping the graphics stack!
    # Prevent notifications from appearing until a set time has elapsed since the previous notification.
    def sendNotificationWithDelay( self, summary, message, delayInSeconds = 0 ):
        if( self.dateTimeOfLastNotification + datetime.timedelta( seconds = delayInSeconds ) < datetime.datetime.now() ):
            Notify.Notification.new( summary, message, self.icon ).show()
            self.dateTimeOfLastNotification = datetime.datetime.now()


    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        if self.isVBoxManageInstalled():
            runningNames, runningUUIDs = self.getRunningVirtualMachines()
            if runningUUIDs:
                if self.scrollUUID is None or self.scrollUUID not in runningUUIDs:
                    self.scrollUUID = runningUUIDs[ 0 ]

                if scrollDirection == Gdk.ScrollDirection.UP:
                    index = ( runningUUIDs.index( self.scrollUUID ) + 1 ) % len( runningUUIDs )
                    self.scrollUUID = runningUUIDs[ index ]
                    self.scrollDirectionIsUp = True

                else:
                    index = ( runningUUIDs.index( self.scrollUUID ) - 1 ) % len( runningUUIDs )
                    self.scrollUUID = runningUUIDs[ index ]
                    self.scrollDirectionIsUp = False

                self.bringWindowToFront( runningNames[ runningUUIDs.index( self.scrollUUID ) ], 10 )


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


    def isVirtualMachineRunning( self, uuid ):
        return self.processGet( "VBoxManage list runningvms | grep " + uuid ) is not None


    def getVirtualMachines( self ):
        virtualMachines = [ ]
        try:
            def addVirtualMachine( group, name, uuid, groups ):
                for groupName in groups:
                    theGroup = next( ( x for x in group.getItems() if type( x ) is Group and x.getName() == groupName ), None )
                    if theGroup is None:
                        theGroup = Group( groupName )
                        group.addItem( theGroup )

                    group = theGroup

                group.addItem( VirtualMachine( name, uuid ) )


            topGroup = Group( "" ) # Only needed whilst parsing results from VBoxManage...
            listVirtualMachines = self.processGet( "VBoxManage list vms --long" )
            for line in listVirtualMachines.splitlines():
                if line.startswith( "Name:" ):
                    name = line.split( "Name:" )[ 1 ].strip()

                elif line.startswith( "Groups:" ):
                    groups = line.split( '/' )[ 1 : ]
                    if groups[ 0 ] == '':
                        del groups[ 0 ]

                elif line.startswith( "UUID:" ):
                    uuid = line.split( "UUID:" )[ 1 ].strip()
                    addVirtualMachine( topGroup, name, uuid, groups )

            virtualMachines = topGroup.getItems()

        except Exception as e:
            self.getLogging().exception( e )
            virtualMachines = [ ]

        return virtualMachines


    def isVBoxManageInstalled( self ):
        isInstalled = False
        result = self.processGet( "which VBoxManage" )
        if result:
            isInstalled = result.find( "VBoxManage" ) > -1

        return isInstalled


    def getStartCommand( self, uuid ):
        startCommand = IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT
        if uuid in self.virtualMachinePreferences:
            startCommand = self.virtualMachinePreferences[ uuid ][ IndicatorVirtualBox.PREFERENCES_START_COMMAND ]

        return startCommand


    def isAutostart( self, uuid ):
        return \
            uuid in self.virtualMachinePreferences and \
            self.virtualMachinePreferences[ uuid ][ IndicatorVirtualBox.PREFERENCES_AUTOSTART ]


    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

        # List of groups and virtual machines.
        treeStore = Gtk.TreeStore( str, str, str, str ) # Group or virtual machine name, autostart, start command, UUID.
        groupsExist = self.__addItemsToStore( treeStore, None, self.getVirtualMachines() if self.isVBoxManageInstalled() else [ ] )

        treeView = Gtk.TreeView.new_with_model( treeStore )
        treeView.expand_all()
        treeView.set_hexpand( True )
        treeView.set_vexpand( True )
        treeView.append_column( Gtk.TreeViewColumn( _( "Virtual Machine" ), Gtk.CellRendererText(), text = IndicatorVirtualBox.COLUMN_GROUP_OR_VIRTUAL_MACHNINE_NAME ) )
        treeView.append_column( Gtk.TreeViewColumn( _( "Autostart" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorVirtualBox.COLUMN_AUTOSTART ) ) # Column 1
        treeView.append_column( Gtk.TreeViewColumn( _( "Start Command" ), Gtk.CellRendererText(), text = IndicatorVirtualBox.COLUMN_START_COMMAND ) )
        treeView.set_tooltip_text( _( "Double click to edit a virtual machine's properties." ) )
        treeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        treeView.connect( "row-activated", self.onVirtualMachineDoubleClick )
        for column in treeView.get_columns():
            column.set_expand( True )

        treeView.get_column( 1 ).set_alignment( 0.5 ) # Autostart.

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( treeView )
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
            "The window title of VirtualBox™ Manager.\n" + \
            "You may have to adjust for your local language." ) )
        windowName.set_text( self.virtualboxManagerWindowName )
        box.pack_start( windowName, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        sortGroupsAndVirtualMachinesEquallyCheckbox = Gtk.CheckButton.new_with_label( _( "Sort groups and virtual machines equally" ) )
        sortGroupsAndVirtualMachinesEquallyCheckbox.set_tooltip_text( _(
            "If checked, groups and virtual machines\n" + \
            "are sorted without distinction.\n\n" + \
            "Otherwise, groups are sorted first,\n" + \
            "followed by virtual machines." ) )
        sortGroupsAndVirtualMachinesEquallyCheckbox.set_active( self.sortGroupsAndVirtualMachinesEqually )

        grid.attach( sortGroupsAndVirtualMachinesEquallyCheckbox, 0, 1, 1, 1 )

        showAsSubmenusCheckbox = Gtk.CheckButton.new_with_label( _( "Show groups as submenus" ) )
        showAsSubmenusCheckbox.set_tooltip_text( _(
            "If checked, groups are shown using submenus.\n\n" + \
            "Otherwise, groups are shown as an indented list." ) )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )

        row = 2
        if groupsExist:
            grid.attach( showAsSubmenusCheckbox, 0, row, 1, 1 )
            row += 1

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Refresh interval (minutes)" ) ), False, False, 0 )

        spinnerRefreshInterval = self.createSpinButton(
            self.refreshIntervalInMinutes,
            1,
            60,
            pageIncrement = 5,
            toolTip = _(
                "How often the list of virtual machines\n" + \
                "and their running status are updated." ) )

        box.pack_start( spinnerRefreshInterval, False, False, 0 )

        grid.attach( box, 0, row, 1, 1 )
        row += 1

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Startup delay (seconds)" ) ), False, False, 0 )

        spinnerDelay = self.createSpinButton(
            self.delayBetweenAutoStartInSeconds,
            1,
            300,
            pageIncrement = 30,
            toolTip = _(
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
            self.sortGroupsAndVirtualMachinesEqually = sortGroupsAndVirtualMachinesEquallyCheckbox.get_active()
            self.refreshIntervalInMinutes = spinnerRefreshInterval.get_value_as_int()
            self.virtualMachinePreferences.clear()
            self.__updateVirtualMachinePreferences( treeStore, treeView.get_model().get_iter_first() )

        return responseType


    def __addItemsToStore( self, treeStore, parent, items ):
        groupsExist = False
        if self.sortGroupsAndVirtualMachinesEqually:
            sortedItems = sorted( items, key = lambda x: ( x.getName().lower() ) )

        else:
            sortedItems = sorted( items, key = lambda x: ( type( x ) is not Group, x.getName().lower() ) ) # Checking if an item is a group results in True (1) or False (0).

        for item in sortedItems:
            if type( item ) is Group:
                groupsExist = True
                self.__addItemsToStore(
                    treeStore,
                    treeStore.append( parent, [ item.getName(), None, None, None ] ),
                    item.getItems() )

            else:
                row = [
                    item.getName(),
                    Gtk.STOCK_APPLY if self.isAutostart( item.getUUID() ) else None,
                    self.getStartCommand( item.getUUID() ),
                    item.getUUID() ]
                treeStore.append( parent, row )

        return groupsExist


    def __updateVirtualMachinePreferences( self, treeStore, treeiter ):
        while treeiter:
            isVirtualMachine = treeStore[ treeiter ][ IndicatorVirtualBox.COLUMN_UUID ]
            isAutostart = treeStore[ treeiter ][ IndicatorVirtualBox.COLUMN_AUTOSTART ] == Gtk.STOCK_APPLY
            isDefaultStartCommand = treeStore[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] == IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT
            if ( isVirtualMachine and isAutostart ) or ( isVirtualMachine and not isDefaultStartCommand ): # Only record VMs with different settings to default.
                key = treeStore[ treeiter ][ IndicatorVirtualBox.COLUMN_UUID ]
                value = [ isAutostart, treeStore[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] ]
                self.virtualMachinePreferences[ key ] = value

            if treeStore.iter_has_child( treeiter ):
                childiter = treeStore.iter_children( treeiter )
                self.__updateVirtualMachinePreferences( treeStore, childiter )

            treeiter = treeStore.iter_next( treeiter )


    def onVirtualMachineDoubleClick( self, tree, rowNumber, treeViewColumn ):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter and model[ treeiter ][ IndicatorVirtualBox.COLUMN_UUID ]:
            self.editVirtualMachine( tree, model, treeiter )


    def editVirtualMachine( self, tree, model, treeiter ):
        grid = self.createGrid()

        label = Gtk.Label.new( _( "Start Command" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        startCommand = Gtk.Entry()
        startCommand.set_width_chars( 20 )
        if model[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ]:
            startCommand.set_text( model[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] )
            startCommand.set_width_chars( len( model[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] ) * 5 / 4 ) # Sometimes the length is shorter than specified due to packing, so make it longer.

        startCommand.set_tooltip_text( _(
            "The terminal command to start the virtual machine such as\n\n" + \
            "\tVBoxManage startvm %VM%\n" + \
            "or\n" + \
            "\tVBoxHeadless --startvm %VM% --vrde off" ) )
        startCommand.set_hexpand( True ) # Only need to set this once and all objects will expand.
        grid.attach( startCommand, 1, 0, 1, 1 )

        autostartCheckbutton = Gtk.CheckButton.new_with_label( _( "Autostart" ) )
        autostartCheckbutton.set_tooltip_text( _( "Run the virtual machine when the indicator starts." ) )
        autostartCheckbutton.set_active(
            model[ treeiter ][ IndicatorVirtualBox.COLUMN_AUTOSTART ] is not None and
            model[ treeiter ][ IndicatorVirtualBox.COLUMN_AUTOSTART ] == Gtk.STOCK_APPLY )
        grid.attach( autostartCheckbutton, 0, 1, 2, 1 )

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

            model[ treeiter ][ IndicatorVirtualBox.COLUMN_AUTOSTART ] = Gtk.STOCK_APPLY if autostartCheckbutton.get_active() else None
            model[ treeiter ][ IndicatorVirtualBox.COLUMN_START_COMMAND ] = startCommand.get_text().strip()

            break

        dialog.destroy()


    def loadConfig( self, config ):
        self.delayBetweenAutoStartInSeconds = config.get( IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS, 10 )
        self.refreshIntervalInMinutes = config.get( IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES, 15 )
        self.showSubmenu = config.get( IndicatorVirtualBox.CONFIG_SHOW_SUBMENU, False )
        self.sortGroupsAndVirtualMachinesEqually = config.get( IndicatorVirtualBox.CONFIG_SORT_GROUPS_AND_VIRTUAL_MACHINES_EQUALLY, True )
        self.virtualMachinePreferences = config.get( IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES, { } ) # Store information about VMs.  Key is VM UUID; value is [ autostart (bool), start command (str) ]
        self.virtualboxManagerWindowName = config.get( IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME, "Oracle VM VirtualBox Manager" )


    def saveConfig( self ):
        return {
            IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS : self.delayBetweenAutoStartInSeconds,
            IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES : self.refreshIntervalInMinutes,
            IndicatorVirtualBox.CONFIG_SHOW_SUBMENU : self.showSubmenu,
            IndicatorVirtualBox.CONFIG_SORT_GROUPS_AND_VIRTUAL_MACHINES_EQUALLY : self.sortGroupsAndVirtualMachinesEqually,
            IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES : self.virtualMachinePreferences,
            IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME : self.virtualboxManagerWindowName
        }


IndicatorVirtualBox().main()