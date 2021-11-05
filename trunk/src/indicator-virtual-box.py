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

import datetime, os, time, virtualmachine


class IndicatorVirtualBox( IndicatorBase ):

    CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS = "delayBetweenAutoStartInSeconds"
    CONFIG_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    CONFIG_SHOW_SUBMENU = "showSubmenu"
    CONFIG_VIRTUAL_MACHINE_PREFERENCES = "virtualMachinePreferences"
    CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME = "virtualboxManagerWindowName"

    VIRTUAL_BOX_CONFIGURATION = os.getenv( "HOME" ) + "/.config/VirtualBox/VirtualBox.xml"
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
            version = "1.0.69",
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
                # for item in virtualMachines:
                for item in sorted( virtualMachines, key = lambda item: item.getName().lower() ):
                    if type( item ) == virtualmachine.Group:
                        self.addMenuItemForGroup( menu, item, 0, runningUUIDs )

                    else:
                        self.addMenuItemForVirtualMachine( menu, item, 0, item.getUUID() in runningUUIDs )

            else:
                menu.append( Gtk.MenuItem.new_with_label( _( "(no virtual machines exist)" ) ) )

            menu.append( Gtk.SeparatorMenuItem() )

            menuItem = Gtk.MenuItem.new_with_label( _( "Launch VirtualBox™ Manager" ) )
            menuItem.connect( "activate", self.onLaunchVirtualBoxManager )
            menu.append( menuItem )
            self.secondaryActivateTarget = menuItem

        else:
            menu.append( Gtk.MenuItem.new_with_label( _( "(VirtualBox™ is not installed)" ) ) )


    def addMenuItemForGroup( self, menu, group, level, runningUUIDs ):
        indent = level * self.indent( 0, 1 )
        menuItem = Gtk.MenuItem.new_with_label( indent + group.getName() )
        menu.append( menuItem )

        if self.showSubmenu:
            menu = Gtk.Menu()
            menuItem.set_submenu( menu )

        # for item in group.getItems():
        for item in sorted( group.getItems(), key = lambda item: item.getName().lower() ):
            if type( item ) == virtualmachine.Group:
                self.addMenuItemForGroup( menu, item, level + 1, runningUUIDs )

            else:
                self.addMenuItemForVirtualMachine( menu, item, level + 1, item.getUUID() in runningUUIDs )


    def addMenuItemForVirtualMachine( self, menu, virtualMachine, level, isRunning ):
        indent = level * self.indent( 0, 1 )
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
            if type( item ) == virtualmachine.Group:
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


    # It is assumed that VirtualBox is installed!
    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
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


    def isVirtualMachineRunning( self, uuid ): return self.processGet( "VBoxManage list runningvms | grep " + uuid ) is not None


#     # Returns a list of virtualmachine and group objects reflecting VMs and groups as found via VBoxManage and the configuration file.
#     def getVirtualMachinesORIG( self ):
#         virtualMachines = [ ]
#         if self.isVBoxManageInstalled():
#             virtualMachinesFromVBoxManage = self.__getVirtualMachinesFromVBoxManage()
#             if os.path.isfile( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION ):
#                 try:
#                     with open( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION, 'r' ) as f:
#                         lines = f.readlines()
#
#                     # The VirtualBox configuration file contains lines detailing the groups (if any) and virtual machines.
#                     # This gives the sort of virtual machines and the group to which they belong (if applicable).
#                     # Groups may contain groups and/or virtual machines.
#                     topGroup = virtualmachine.Group( "" ) # Create a dummy group to make it easier to parse the first line of the configuration file.
#                     for line in lines:
#                         if "GUI/GroupDefinitions/" in line:
#                             parts = line.split( "\"" )
#                             groupPath = parts[ 1 ].split( '/' )[ 2 : ]
#                             groupItems = topGroup.getItems()
#                             for groupName in groupPath: # Traverse the paths to find the final group...
#                                 group = next( ( x for x in groupItems if type( x ) == virtualmachine.Group and x.getName() == groupName ), topGroup )
#                                 groupItems = group.getItems()
#
#                             groupNamesAndUUIDs = parts[ 3 ].split( ',' )
#                             if groupNamesAndUUIDs[ 0 ] == "n=GLOBAL": # VirtualBox 6 has added this to the config...not needed by the indicator.
#                                 del groupNamesAndUUIDs[ 0 ]
#
#                             for item in groupNamesAndUUIDs:
#                                 if item.startswith( "go=" ):
#                                     group.addItem( virtualmachine.Group( item.replace( "go=", "" ) ) )
#
# #TODO Temporary fix for Stephane; waiting on him to verify it fixes things.
#                                 elif item.startswith( "gc=" ):
#                                     group.addItem( virtualmachine.Group( item.replace( "gc=", "" ) ) )
#
#                                 else:
#                                     uuid = item.replace( "m=", "" )
#                                     name = next( x for x in virtualMachinesFromVBoxManage if x.getUUID() == uuid ).getName()
#                                     group.addItem( virtualmachine.VirtualMachine( name, uuid ) )
#
#                     virtualMachines = topGroup.getItems() # Return the items (groups and/or virtual machines) of the dummy top group.
#
#                 except Exception as e:
#                     self.getLogging().exception( e )
#                     virtualMachines = [ ]
#
#             else:
#                 virtualMachines = virtualMachinesFromVBoxManage
#
#         return virtualMachines


    # # Returns a list of virtualmachine objects from calling VBoxManage.
    # # Contains no group information, nor sort order which is set by the user in the GUI.
    # # Safe to call without checking if VBoxManage is installed.
    # def __getVirtualMachinesFromVBoxManage( self ):
    #     virtualMachines = [ ]
    #     result = self.processGet( "VBoxManage list vms" )
    #     if result: # If a VM is corrupt/missing, VBoxManage can give back a spurious (None) result.
    #         for line in result.splitlines():
    #             try:
    #                 nameAndUUID = line[ 1 : -1 ].split( "\" {" )
    #                 virtualMachines.append( virtualmachine.VirtualMachine( nameAndUUID[ 0 ], nameAndUUID[ 1 ] ) )
    #
    #             except Exception:
    #                 pass # Sometimes VBoxManage emits a warning message along with the VM information.
    #
    #     return virtualMachines


    def isVBoxManageInstalled( self ):
        isInstalled = False
        result = self.processGet( "which VBoxManage" )
        if result:
            isInstalled = result.find( "VBoxManage" ) > -1

        return isInstalled


#TODO Testing
    def getVirtualMachines( self ):
# ['Windows XP', '/', 'bc161180-2cde-47b1-a3ee-b8c44d335417']
# ['Windows 10', '/New group 4/New group 5', '628a6317-792a-45ff-8f0a-de3227f14724']
# ['Ubuntu 18.04', '/New group 4/New group 5', '54ba0488-739c-4e4a-8aca-eaeb786681d1']
# ['Ubuntu 20.04', '/', 'e1a5e766-27cc-4b13-8c81-b69a5aa5dac7']
# ['MythTV Test', '/', '58aa424b-2ae7-4f60-aca9-feb5642924aa']
# ['MythTV Test 2', '/', '256f0096-c3e5-45e1-85e0-44e85b4cbc1d']
# ['Debian 11', '/', '40793856-737c-4639-b4db-f1b502a6fefd']
# ['A', '/New group', '5c215bb3-412a-4f26-8b61-ca1ca7698266']
# ['B', '/New group 3/New group 2', 'f88b2a8d-eae5-4a6d-add6-9ce0e4065f0f']
# ['C', '/New group 3/New group 2', '3b726c62-146c-469d-844b-2f4ba65f8b04']
# ['D', '/New group 3', '49e274da-a08b-4cd9-8d03-d7a0582bc793']
# ['E', '/New group 3', '4021c780-02b7-428f-9df4-f521e7600123']
# ['AA', '/New group 4', '4a8c1cb3-60dd-47a5-b5a4-f4413d5d3596']

        virtualMachines = [ ]
        if self.isVBoxManageInstalled():
            try:
                def addVirtualMachine( group, name, uuid, groups ):
                    for groupName in groups:
                        theGroup = next( ( x for x in group.getItems() if type( x ) == virtualmachine.Group and x.getName() == groupName ), None )
                        if theGroup is None:
                            theGroup = virtualmachine.Group( groupName )
                            group.addItem( theGroup )

                        group = theGroup

                    group.addItem( virtualmachine.VirtualMachine( name, uuid ) )


                topGroup = virtualmachine.Group( "" ) # Create a dummy group to make it easier to parse the first line of the configuration file.
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

                virtualMachines = topGroup.getItems() # Return the items (groups and/or virtual machines) of the dummy top group.

            except Exception as e:
                self.getLogging().exception( e )
                virtualMachines = [ ]

        return virtualMachines


        
        # s = [ ]
        # listVirtualMachines = self.processGet( "VBoxManage list vms --long" )
        # for line in listVirtualMachines.splitlines():
        #     if line.startswith( "Name:" ):
        #         a = [ ]
        #         a.append( line.split( "Name:" )[ 1 ].strip() )
        #
        #     elif line.startswith( "Groups:" ):
        #         a.append( line.split( "Groups:" )[ 1 ].strip() )
        #
        #     if line.startswith( "UUID:" ):
        #         a.append( line.split( "UUID:" )[ 1 ].strip() )
        #         s.append( a )
        #
        #
        # for item in s:
        #     print( item )

                
        # print( listVirtualMachines )
        # listGroups = self.processGet( "VBoxManage list groups" )
        # print( "--------------------------------------------------------------------------" )
        # print( listGroups )
        # print()
# VBoxManage --help
# VBoxManage list vms
# VBoxManage list groups
# VBoxManage showvminfo 40793856-737c-4639-b4db-f1b502a6fefd
# VBoxManage showvminfo 4021c780-02b7-428f-9df4-f521e7600123
# VBoxManage showvminfo 3b726c62-146c-469d-844b-2f4ba65f8b04
# VBoxManage list vms --long


#
# Name:            Windows XP
# Groups:          /
# Guest OS:        Windows XP (32-bit)
# UUID:            bc161180-2cde-47b1-a3ee-b8c44d335417
# Config file:     /home/bernard/VirtualBox VMs/Windows XP/Windows XP.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/Windows XP/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/Windows XP/Logs
# Hardware UUID:   bc161180-2cde-47b1-a3ee-b8c44d335417
# Memory size:     384MB
# Page Fusion:     off
# VRAM size:       18MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          off
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          off
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             local time
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Legacy
# Effective Paravirt. Provider: None
# State:           powered off (since 2021-10-24T21:45:46.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            IDE
# Storage Controller Type (0):            PIIX4
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  2
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# IDE (0, 0): /home/bernard/VirtualBox VMs/Windows XP/WinXP.vdi (UUID: 1c032e4a-fe2a-4f7d-a70e-80276d062d4d)
# IDE (1, 0): Empty
# NIC 1:           MAC: 080027B56E5A, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: Am79C973, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: AC97, Codec: STAC9700)
# Audio playback:  enabled
# Audio capture:   enabled
# Clipboard Mode:  Bidirectional
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  
#
# Name: 'bernard', Host path: '/home/bernard' (machine mapping), writable
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/Windows XP/Windows XP.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            Windows 10
# Groups:          /
# Guest OS:        Windows 10 (64-bit)
# UUID:            628a6317-792a-45ff-8f0a-de3227f14724
# Config file:     /home/bernard/VirtualBox VMs/Windows 10/Windows 10.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/Windows 10/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/Windows 10/Logs
# Hardware UUID:   628a6317-792a-45ff-8f0a-de3227f14724
# Memory size:     4096MB
# Page Fusion:     off
# VRAM size:       33MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             on
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          off
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): HardDisk
# Boot Device (2): DVD
# Boot Device (3): Not Assigned
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             local time
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     on
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: HyperV
# State:           powered off (since 2020-02-08T22:18:42.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: on
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            IDE Controller
# Storage Controller Type (0):            PIIX4
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  2
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# IDE Controller (0, 0): /home/bernard/VirtualBox VMs/Windows 10/MSEdge - Win10-disk001.vmdk (UUID: 1186d54a-1881-40f5-b262-1eccf606c803)
# NIC 1:           MAC: 0800278EF65B, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: PS/2 Mouse
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           disabled
# Audio playback:  disabled
# Audio capture:   disabled
# Clipboard Mode:  Bidirectional
# Drag and drop Mode: Bidirectional
# VRDE:            enabled (Address 127.0.0.1, Ports 5940, MultiConn: off, ReuseSingleConn: off, Authentication type: null)
# Video redirection: disabled
# VRDE property: TCP/Ports  = "5940"
# VRDE property: TCP/Address = "127.0.0.1"
# USB:             disabled
# EHCI:            disabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  <none>
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/MSEdge - Win10
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    ac_enabled=false
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            Ubuntu 18.04
# Groups:          /
# Guest OS:        Ubuntu (64-bit)
# UUID:            54ba0488-739c-4e4a-8aca-eaeb786681d1
# Config file:     /home/bernard/VirtualBox VMs/Ubuntu 18.04/Ubuntu 18.04.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/Ubuntu 18.04/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/Ubuntu 18.04/Logs
# Hardware UUID:   54ba0488-739c-4e4a-8aca-eaeb786681d1
# Memory size:     2048MB
# Page Fusion:     off
# VRAM size:       16MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          on
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             UTC
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: KVM
# State:           powered off (since 2021-04-26T05:28:08.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            IDE
# Storage Controller Type (0):            PIIX4
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  2
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# Storage Controller Name (1):            SATA
# Storage Controller Type (1):            IntelAhci
# Storage Controller Instance Number (1): 0
# Storage Controller Max Port Count (1):  30
# Storage Controller Port Count (1):      1
# Storage Controller Bootable (1):        on
# IDE (1, 0): /usr/share/virtualbox/VBoxGuestAdditions.iso (UUID: e7d18b27-d3aa-4d3b-ab3b-8d1e8ea88f02)
# SATA (0, 0): /home/bernard/VirtualBox VMs/Ubuntu 18.04/Ubuntu18.04.vdi (UUID: 81680a54-f548-446e-ba50-211a83966216)
# NIC 1:           MAC: 0800274FAB7E, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: AC97, Codec: AD1980)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  
#
# Name: 'Subversion', Host path: '/home/bernard/Programming/Subversion' (machine mapping), writable
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/Ubuntu 18.04/Ubuntu 18.04.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    ac_enabled=false
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            Ubuntu 20.04
# Groups:          /
# Guest OS:        Ubuntu (64-bit)
# UUID:            e1a5e766-27cc-4b13-8c81-b69a5aa5dac7
# Config file:     /home/bernard/VirtualBox VMs/Ubuntu 20.04/Ubuntu 20.04.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/Ubuntu 20.04/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/Ubuntu 20.04/Logs
# Hardware UUID:   e1a5e766-27cc-4b13-8c81-b69a5aa5dac7
# Memory size:     4096MB
# Page Fusion:     off
# VRAM size:       16MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          on
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             UTC
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: KVM
# State:           aborted (since 2021-11-03T08:11:27.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            IDE
# Storage Controller Type (0):            PIIX4
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  2
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# Storage Controller Name (1):            SATA
# Storage Controller Type (1):            IntelAhci
# Storage Controller Instance Number (1): 0
# Storage Controller Max Port Count (1):  30
# Storage Controller Port Count (1):      1
# Storage Controller Bootable (1):        on
# IDE (1, 0): Empty
# SATA (0, 0): /home/bernard/VirtualBox VMs/Ubuntu 20.04/Ubuntu 20.04.vdi (UUID: 30d3f9c7-cafc-416a-ad1a-92421301ea00)
# NIC 1:           MAC: 0800272A5CA7, Attachment: Bridged Interface 'enp2s0', Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: AC97, Codec: AD1980)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  
#
# Name: 'bernard', Host path: '/home/bernard' (machine mapping), writable
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/Ubuntu 20.04/Ubuntu 20.04.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    ac_enabled=false
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            MythTV Test
# Groups:          /
# Guest OS:        Ubuntu (64-bit)
# UUID:            58aa424b-2ae7-4f60-aca9-feb5642924aa
# Config file:     /home/bernard/VirtualBox VMs/MythTV Test/MythTV Test.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/MythTV Test/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/MythTV Test/Logs
# Hardware UUID:   58aa424b-2ae7-4f60-aca9-feb5642924aa
# Memory size:     4096MB
# Page Fusion:     off
# VRAM size:       16MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          on
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             UTC
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: KVM
# State:           powered off (since 2020-05-12T10:26:56.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            IDE
# Storage Controller Type (0):            PIIX4
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  2
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# Storage Controller Name (1):            SATA
# Storage Controller Type (1):            IntelAhci
# Storage Controller Instance Number (1): 0
# Storage Controller Max Port Count (1):  30
# Storage Controller Port Count (1):      1
# Storage Controller Bootable (1):        on
# IDE (1, 0): Empty
# SATA (0, 0): /home/bernard/VirtualBox VMs/MythTV Test/MythTV Test.vdi (UUID: 19bee17d-8a77-49ef-b675-971f131f084e)
# NIC 1:           MAC: 080027D27BE2, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: AC97, Codec: AD1980)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  <none>
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/MythTV Test/MythTV Test.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    ac_enabled=false
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            MythTV Test 2
# Groups:          /
# Guest OS:        Ubuntu (64-bit)
# UUID:            256f0096-c3e5-45e1-85e0-44e85b4cbc1d
# Config file:     /home/bernard/VirtualBox VMs/MythTV Test 2/MythTV Test 2.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/MythTV Test 2/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/MythTV Test 2/Logs
# Hardware UUID:   256f0096-c3e5-45e1-85e0-44e85b4cbc1d
# Memory size:     4096MB
# Page Fusion:     off
# VRAM size:       16MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          on
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             UTC
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: KVM
# State:           powered off (since 2020-05-12T14:23:02.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            IDE
# Storage Controller Type (0):            PIIX4
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  2
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# Storage Controller Name (1):            SATA
# Storage Controller Type (1):            IntelAhci
# Storage Controller Instance Number (1): 0
# Storage Controller Max Port Count (1):  30
# Storage Controller Port Count (1):      1
# Storage Controller Bootable (1):        on
# IDE (1, 0): Empty
# SATA (0, 0): /home/bernard/VirtualBox VMs/MythTV Test 2/MythTV Test 2.vdi (UUID: fbfbdae7-0a71-4384-af7c-f39ceca25041)
# NIC 1:           MAC: 080027299098, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: AC97, Codec: AD1980)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  
#
# Name: 'MythTV', Host path: '/home/bernard/MythTV' (machine mapping), writable
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/MythTV Test 2/MythTV Test 2.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    ac_enabled=false
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            Debian 11
# Groups:          /
# Guest OS:        Debian (64-bit)
# UUID:            40793856-737c-4639-b4db-f1b502a6fefd
# Config file:     /home/bernard/VirtualBox VMs/Debian 11/Debian 11.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/Debian 11/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/Debian 11/Logs
# Hardware UUID:   40793856-737c-4639-b4db-f1b502a6fefd
# Memory size:     3072MB
# Page Fusion:     off
# VRAM size:       16MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          on
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             UTC
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: KVM
# State:           powered off (since 2021-10-30T05:40:47.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            IDE
# Storage Controller Type (0):            PIIX4
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  2
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# Storage Controller Name (1):            SATA
# Storage Controller Type (1):            IntelAhci
# Storage Controller Instance Number (1): 0
# Storage Controller Max Port Count (1):  30
# Storage Controller Port Count (1):      1
# Storage Controller Bootable (1):        on
# IDE (1, 0): /home/bernard/Downloads/debian-11.0.0-amd64-netinst.iso (UUID: 9f5b8789-18fc-4f6c-b7ea-9ed0d1dcbcbe) (temp eject)
# SATA (0, 0): /home/bernard/VirtualBox VMs/Debian 11/Debian 11.vdi (UUID: 5a62ef90-beef-4791-8a79-f786d4ce7458)
# NIC 1:           MAC: 0800271A0258, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: AC97, Codec: AD1980)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  <none>
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/Debian 11/Debian 11.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    ac_enabled=false
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            A
# Groups:          /New group
# Guest OS:        Windows 7 (64-bit)
# UUID:            5c215bb3-412a-4f26-8b61-ca1ca7698266
# Config file:     /home/bernard/VirtualBox VMs/New group/A/A.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/New group/A/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/New group/A/Logs
# Hardware UUID:   5c215bb3-412a-4f26-8b61-ca1ca7698266
# Memory size:     2048MB
# Page Fusion:     off
# VRAM size:       27MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          off
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             local time
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: HyperV
# State:           powered off (since 2021-11-01T01:58:18.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            SATA
# Storage Controller Type (0):            IntelAhci
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  30
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# SATA (1, 0): Empty
# NIC 1:           MAC: 08002750819E, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: HDA, Codec: STAC9221)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  <none>
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/New group/A/A.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            B
# Groups:          /New group 3/New group 2
# Guest OS:        Windows 7 (64-bit)
# UUID:            f88b2a8d-eae5-4a6d-add6-9ce0e4065f0f
# Config file:     /home/bernard/VirtualBox VMs/New group 3/New group 2/B/B.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/New group 3/New group 2/B/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/New group 3/New group 2/B/Logs
# Hardware UUID:   f88b2a8d-eae5-4a6d-add6-9ce0e4065f0f
# Memory size:     2048MB
# Page Fusion:     off
# VRAM size:       27MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          off
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             local time
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: HyperV
# State:           powered off (since 2021-10-31T03:28:06.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            SATA
# Storage Controller Type (0):            IntelAhci
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  30
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# SATA (1, 0): Empty
# NIC 1:           MAC: 0800277859F2, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: HDA, Codec: STAC9221)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  <none>
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/New group 3/New group 2/B/B.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            C
# Groups:          /New group 3/New group 2
# Guest OS:        Windows 7 (64-bit)
# UUID:            3b726c62-146c-469d-844b-2f4ba65f8b04
# Config file:     /home/bernard/VirtualBox VMs/New group 3/New group 2/C/C.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/New group 3/New group 2/C/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/New group 3/New group 2/C/Logs
# Hardware UUID:   3b726c62-146c-469d-844b-2f4ba65f8b04
# Memory size:     2048MB
# Page Fusion:     off
# VRAM size:       27MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          off
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             local time
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: HyperV
# State:           powered off (since 2021-10-28T22:40:26.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            SATA
# Storage Controller Type (0):            IntelAhci
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  30
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# SATA (1, 0): Empty
# NIC 1:           MAC: 08002702FAEF, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: HDA, Codec: STAC9221)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  <none>
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/New group 3/New group 2/C/C.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            D
# Groups:          /New group 3
# Guest OS:        Windows 7 (64-bit)
# UUID:            49e274da-a08b-4cd9-8d03-d7a0582bc793
# Config file:     /home/bernard/VirtualBox VMs/New group 3/D/D.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/New group 3/D/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/New group 3/D/Logs
# Hardware UUID:   49e274da-a08b-4cd9-8d03-d7a0582bc793
# Memory size:     2048MB
# Page Fusion:     off
# VRAM size:       27MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          off
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             local time
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: HyperV
# State:           powered off (since 2021-10-28T22:40:30.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            SATA
# Storage Controller Type (0):            IntelAhci
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  30
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# SATA (1, 0): Empty
# NIC 1:           MAC: 080027B6E73C, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: HDA, Codec: STAC9221)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  <none>
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/New group 3/D/D.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
# Name:            E
# Groups:          /New group 3
# Guest OS:        Windows 7 (64-bit)
# UUID:            4021c780-02b7-428f-9df4-f521e7600123
# Config file:     /home/bernard/VirtualBox VMs/New group 3/E/E.vbox
# Snapshot folder: /home/bernard/VirtualBox VMs/New group 3/E/Snapshots
# Log folder:      /home/bernard/VirtualBox VMs/New group 3/E/Logs
# Hardware UUID:   4021c780-02b7-428f-9df4-f521e7600123
# Memory size:     2048MB
# Page Fusion:     off
# VRAM size:       27MB
# CPU exec cap:    100%
# HPET:            off
# Chipset:         piix3
# Firmware:        BIOS
# Number of CPUs:  1
# PAE:             off
# Long Mode:       on
# Triple Fault Reset: off
# APIC:            on
# X2APIC:          off
# CPUID Portability Level: 0
# CPUID overrides: None
# Boot menu mode:  message and menu
# Boot Device (1): Floppy
# Boot Device (2): DVD
# Boot Device (3): HardDisk
# Boot Device (4): Not Assigned
# ACPI:            on
# IOAPIC:          on
# BIOS APIC mode:  APIC
# Time offset:     0ms
# RTC:             local time
# Hardw. virt.ext: on
# Nested Paging:   on
# Large Pages:     off
# VT-x VPID:       on
# VT-x unr. exec.: on
# Paravirt. Provider: Default
# Effective Paravirt. Provider: HyperV
# State:           powered off (since 2021-10-31T03:28:04.000000000)
# Graphics Controller:         VBoxVGA
# Monitor count:   1
# 3D Acceleration: off
# 2D Video Acceleration: off
# Teleporter Enabled: off
# Teleporter Port: 0
# Teleporter Address: 
# Teleporter Password: 
# Tracing Enabled: off
# Allow Tracing to Access VM: off
# Tracing Configuration: 
# Autostart Enabled: off
# Autostart Delay: 0
# Default Frontend: 
# Storage Controller Name (0):            SATA
# Storage Controller Type (0):            IntelAhci
# Storage Controller Instance Number (0): 0
# Storage Controller Max Port Count (0):  30
# Storage Controller Port Count (0):      2
# Storage Controller Bootable (0):        on
# SATA (1, 0): Empty
# NIC 1:           MAC: 080027EE305B, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
# NIC 1 Settings:  MTU: 0, Socket (send: 64, receive: 64), TCP Window (send:64, receive: 64)
# NIC 2:           disabled
# NIC 3:           disabled
# NIC 4:           disabled
# NIC 5:           disabled
# NIC 6:           disabled
# NIC 7:           disabled
# NIC 8:           disabled
# Pointing Device: USB Tablet
# Keyboard Device: PS/2 Keyboard
# UART 1:          disabled
# UART 2:          disabled
# UART 3:          disabled
# UART 4:          disabled
# LPT 1:           disabled
# LPT 2:           disabled
# Audio:           enabled (Driver: PulseAudio, Controller: HDA, Codec: STAC9221)
# Audio playback:  enabled
# Audio capture:   disabled
# Clipboard Mode:  disabled
# Drag and drop Mode: disabled
# VRDE:            disabled
# USB:             enabled
# EHCI:            enabled
# XHCI:            disabled
#
# USB Device Filters:
#
# <none>
#
# Bandwidth groups:  <none>
#
# Shared folders:  <none>
#
# Capturing:          not active
# Capture audio:      not active
# Capture screens:    0
# Capture file:       /home/bernard/VirtualBox VMs/New group 3/E/E.webm
# Capture dimensions: 1024x768
# Capture rate:       512 kbps
# Capture FPS:        25
# Capture options:    
#
# Guest:
#
# Configured memory balloon size:      0 MB
#
#
#
# --------------------------------------------------------------------------
# "/"
# "/New group"
# "/New group 3"
# "/New group 3/New group 2"
#




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

        def addItemsToStore( parent, items ):
            groupsExist = False
            for item in items:
                if type( item ) == virtualmachine.Group:
                    groupsExist = True
                    addItemsToStore( treeStore.append( parent, [ item.getName(), None, None, None ] ), item.getItems() )

                else:
                    uuid = item.getUUID()
                    treeStore.append( parent, [ item.getName(), Gtk.STOCK_APPLY if self.isAutostart( uuid ) else None, self.getStartCommand( uuid ), uuid ] )

            return groupsExist

        # List of groups and virtual machines.
        treeStore = Gtk.TreeStore( str, str, str, str ) # Group or virtual machine name, autostart, start command, UUID.
        groupsExist = addItemsToStore( None, self.getVirtualMachines() )

        treeView = Gtk.TreeView.new_with_model( treeStore )
        treeView.expand_all()
        treeView.set_hexpand( True )
        treeView.set_vexpand( True )
        treeView.append_column( Gtk.TreeViewColumn( _( "Virtual Machine" ), Gtk.CellRendererText(), text = IndicatorVirtualBox.COLUMN_GROUP_OR_VIRTUAL_MACHNINE_NAME ) )
        treeView.append_column( Gtk.TreeViewColumn( _( "Autostart" ), Gtk.CellRendererPixbuf(), stock_id = IndicatorVirtualBox.COLUMN_AUTOSTART ) )
        treeView.append_column( Gtk.TreeViewColumn( _( "Start Command" ), Gtk.CellRendererText(), text = IndicatorVirtualBox.COLUMN_START_COMMAND ) )
        treeView.set_tooltip_text( _( "Double click to edit a virtual machine's properties." ) )
        treeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        treeView.connect( "row-activated", self.onVirtualMachineDoubleClick )

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
            self.refreshIntervalInMinutes = spinnerRefreshInterval.get_value_as_int()
            self.virtualMachinePreferences.clear()
            self.__updateVirtualMachinePreferences( treeStore, treeView.get_model().get_iter_first() )

        return responseType


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
        self.virtualMachinePreferences = config.get( IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES, { } ) # Store information about VMs.  Key is VM UUID; value is [ autostart (bool), start command (str) ]
        self.virtualboxManagerWindowName = config.get( IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME, "Oracle VM VirtualBox Manager" )


    def saveConfig( self ):
        return {
            IndicatorVirtualBox.CONFIG_DELAY_BETWEEN_AUTO_START_IN_SECONDS: self.delayBetweenAutoStartInSeconds,
            IndicatorVirtualBox.CONFIG_REFRESH_INTERVAL_IN_MINUTES: self.refreshIntervalInMinutes,
            IndicatorVirtualBox.CONFIG_SHOW_SUBMENU: self.showSubmenu,
            IndicatorVirtualBox.CONFIG_VIRTUAL_MACHINE_PREFERENCES: self.virtualMachinePreferences,
            IndicatorVirtualBox.CONFIG_VIRTUALBOX_MANAGER_WINDOW_NAME: self.virtualboxManagerWindowName
        }


IndicatorVirtualBox().main()
