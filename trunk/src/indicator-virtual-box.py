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


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  https://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/api/AppIndicator3_0.1/classes/Indicator.html
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-14.04


INDICATOR_NAME = "indicator-virtual-box"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "Notify", "0.7" )

from gi.repository import AppIndicator3, Gdk, GLib, Gtk, Notify
from threading import Thread

import gzip, json, logging, os, pythonutils, re, shutil, sys, time, virtualmachine


class IndicatorVirtualBox:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.53"
    ICON = INDICATOR_NAME
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    VIRTUAL_BOX_CONFIGURATION_4_DOT_3_OR_GREATER = os.getenv( "HOME" ) + "/.config/VirtualBox/VirtualBox.xml"
    VIRTUAL_BOX_CONFIGURATION_4_DOT_3_PRIOR = os.getenv( "HOME" ) + "/.VirtualBox/VirtualBox.xml"
    VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION = "4.3" # Configuration file location and format changed at this version (https://www.virtualbox.org/manual/ch10.html#idp99351072).

    VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT = "VBoxManage startvm %VM%"

    COMMENTS = _( "Shows VirtualBox™ virtual machines and allows them to be started." )

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_DELAY_BETWEEN_AUTO_START = "delayBetweenAutoStartInSeconds"
    SETTINGS_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    SETTINGS_SHOW_SUBMENU = "showSubmenu"
    SETTINGS_SORT_DEFAULT = "sortDefault"
    SETTINGS_VIRTUAL_MACHINE_PREFERENCES = "virtualMachinePreferences"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorVirtualBox.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )
        self.dialog = None
        self.loadSettings()
        Notify.init( INDICATOR_NAME )
        virtualMachines = self.getVirtualMachines()
        Thread( target = self.autoStartVirtualMachines, args = ( virtualMachines, ) ).start()

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorVirtualBox.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.connect( "scroll-event", self.onMouseWheelScroll )

        self.scrollDirectionIsUp = True
        self.scrollUUID = None

        self.buildMenu( virtualMachines )
        self.timeoutID = GLib.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.onRefresh, True )


    def main( self ): Gtk.main()


    def onMouseWheelScroll( self, indicator, delta, scrollDirection ):
        runningVMs = self.getRunningVirtualMachines()
        if len( runningVMs ) > 0:
            if self.scrollUUID is None or self.scrollUUID not in runningVMs:
                self.scrollUUID = runningVMs[ 0 ]

            if scrollDirection == Gdk.ScrollDirection.UP:
                index = ( runningVMs.index( self.scrollUUID ) + 1 ) % len( runningVMs )
                self.scrollUUID = runningVMs[ index ]
                self.scrollDirectionIsUp = True
            else:
                index = ( runningVMs.index( self.scrollUUID ) - 1 ) % len( runningVMs )
                self.scrollUUID = runningVMs[ index ]
                self.scrollDirectionIsUp = False

            self.bringWindowToFront( self.getVirtualMachineNameFromUUID( self.scrollUUID ) )


    def bringWindowToFront( self, virtualMachineName ):
        numberOfWindowsWithTheSameName = pythonutils.processGet( 'wmctrl -l | grep "' + virtualMachineName + '" | wc -l' ).strip()
        if numberOfWindowsWithTheSameName == "0":
            message = _( "The VM '{0}' is running but its window could not be found - perhaps it is running headless." ).format( virtualMachineName )
            Notify.Notification.new( _( "Warning" ), message, IndicatorVirtualBox.ICON ).show()
        elif numberOfWindowsWithTheSameName == "1":
            for line in pythonutils.processGet( "wmctrl -l" ).splitlines():
                if virtualMachineName in line:
                    windowID = line[ 0 : line.find( " " ) ]
                    pythonutils.processCall( "wmctrl -i -a " + windowID )
                    break
        else:
            message = _( "Unable to bring the VM '{0}' to front as there is more than one window with the same name." ).format( virtualMachineName )
            Notify.Notification.new( _( "Warning" ), message, IndicatorVirtualBox.ICON ).show()


    def getVirtualMachineNameFromUUID( self, UUID ):
        name = ""
        result = pythonutils.processGet( "VBoxManage list runningvms | grep " + UUID )
        if result is not None:
            name = result[ 1 : result.find( "\" {" ) ]

        return name


    def buildMenu( self, virtualMachines ):
        menu = Gtk.Menu()
        if self.isVBoxManageInstalled():
            if len( virtualMachines ) == 0:
                menu.append( Gtk.MenuItem( _( "(no virtual machines exist)" ) ) )
            else:
                runningVirtualMachines = self.getRunningVirtualMachines()
                if self.showSubmenu == True:
                    stack = [ ]
                    currentMenu = menu
                    for i in range( len( virtualMachines ) ):
                        virtualMachine = virtualMachines[ i ]
                        while virtualMachine.getIndent() < len( stack ):
                            currentMenu = stack.pop()

                        if virtualMachine.isGroup():
                            menuItem = Gtk.MenuItem( self.getGroupName( virtualMachine ) )
                            currentMenu.append( menuItem )
                            subMenu = Gtk.Menu()
                            menuItem.set_submenu( subMenu )
                            stack.append( currentMenu )
                            currentMenu = subMenu
                        else:
                            currentMenu.append( self.createMenuItemForVirtualMachine( virtualMachine, "", runningVirtualMachines ) )
                else:
                    for virtualMachine in virtualMachines:
                        indent = "    " * virtualMachine.getIndent()
                        if virtualMachine.isGroup():
                            menu.append( Gtk.MenuItem( indent + self.getGroupName( virtualMachine ) ) )
                        else:
                            menu.append( self.createMenuItemForVirtualMachine( virtualMachine, indent, runningVirtualMachines ) )

            menu.append( Gtk.SeparatorMenuItem() )
            menuItem = Gtk.MenuItem( _( "Launch VirtualBox Manager" ) )
            menuItem.connect( "activate", self.onLaunchVirtualBoxManager )
            menu.append( menuItem )
            
        else:
            menu.insert( Gtk.MenuItem( _( "(VirtualBox is not installed)" ) ), 0 )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, False, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def getGroupName( self, virtualMachine ): return virtualMachine.getName()[ virtualMachine.getName().rfind( "/" ) + 1 : ]


    def createMenuItemForVirtualMachine( self, virtualMachine, indent, runningVirtualMachines ):
        if virtualMachine.getUUID() in runningVirtualMachines: # No need to check if this is a group...groups never "run" and this function should only be called for a VM and never a group.
            menuItem = Gtk.RadioMenuItem.new_with_label( [ ], indent + virtualMachine.getName() )
            menuItem.set_active( True )
        else:
            menuItem = Gtk.MenuItem( indent + virtualMachine.getName() )

        menuItem.props.name = virtualMachine.getUUID()
        menuItem.connect( "activate", self.onVirtualMachine )
        return menuItem


    # It is assumed that VirtualBox is installed!
    def onLaunchVirtualBoxManager( self, widget ):
        result = pythonutils.processGet( 'wmctrl -l | grep "`hostname` Oracle VM VirtualBox"' )
        if result is None:
            pythonutils.processCall( "VirtualBox &" )
        else:
            windowID = result[ 0 : result.find( " " ) ]
            pythonutils.processCall( "wmctrl -i -a " + windowID )


    def onVirtualMachine( self, widget ):
        virtualMachine = self.getVirtualMachine( widget.props.name )
        if virtualMachine is None:
            GLib.timeout_add_seconds( 1, self.onRefresh, False )
            message = _( "Missing VM '{0}', UUID '{1}'." ).format( widget.props.label, widget.props.name )
            Notify.Notification.new( _( "Error" ), message, IndicatorVirtualBox.ICON ).show()
            logging.error( "Missing VM '{0}', UUID '{1}'.".format( widget.props.label, widget.props.name ) )
        else:
            self.startVirtualMachine( virtualMachine, 0 ) # Set a zero delay as this is not an autostart.


    def getVirtualMachine( self, uuid ):
        for virtualMachine in self.getVirtualMachines():
            if virtualMachine.getUUID() == uuid:
                return virtualMachine

        return None


    def getVirtualMachines( self ):
        virtualMachines = [ ]
        if self.isVBoxManageInstalled():
            version = self.getVirtualBoxVersion()
            if version is not None:
                if version < IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION:
                    virtualMachinesFromConfig = self.getVirtualMachinesFromConfigPrior4dot3()
                else:
                    virtualMachinesFromConfig = self.getVirtualMachinesFromConfig4dot3()

                virtualMachinesFromVBoxManage = self.getVirtualMachinesFromVBoxManage() # Contains no group information, nor sort order.
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

                # Alphabetically sort...or not.
                if self.sortDefault == False and not self.groupsExist( virtualMachines ):
                    virtualMachines = sorted( virtualMachines, key = lambda virtualMachine: virtualMachine.name )

        return virtualMachines


    def getRunningVirtualMachines( self ):
        runningVirtualMachines = [ ]
        result = pythonutils.processGet( "VBoxManage list runningvms" )
        if result is not None:
            for line in result.splitlines():
                try:
                    info = line[ 1 : -1 ].split( "\" {" )
                    runningVirtualMachines.append( info[ 1 ] )
                except:
                    pass # Sometimes VBoxManage emits a warning message along with the VM information.

        return runningVirtualMachines


    def autoStartVirtualMachines( self, virtualMachines ):
        for virtualMachine in virtualMachines:
            if self.isAutostart( virtualMachine.getUUID() ):
                self.startVirtualMachine( virtualMachine, self.delayBetweenAutoStartInSeconds )


    # Returns the version number as a string or None if no version could be determined.
    # Safe to call without checking if VBoxManage is installed.
    def getVirtualBoxVersion( self ):
        result = pythonutils.processGet( "VBoxManage --version" )
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
        result = pythonutils.processGet( "which VBoxManage" )
        if result is not None:
            isInstalled = result.find( "VBoxManage" ) > -1

        return isInstalled


    # The returned list of virtualmachine.Info objects does not include any groups (if present) nor any order set by the user in the GUI.
    # Safe to call without checking if VBoxManage is installed.
    def getVirtualMachinesFromVBoxManage( self ):
        virtualMachines = [ ]
        result = pythonutils.processGet( "VBoxManage list vms" )
        if result is not None: # If a VM is corrupt/missing, VBoxManage can give back a spurious (None) result.
            for line in result.splitlines():
                try:
                    info = line[ 1 : -1 ].split( "\" {" )
                    virtualMachine = virtualmachine.Info( info[ 0 ], False, info[ 1 ], 0 )
                    virtualMachines.append( virtualMachine )
                except:
                    pass # Sometimes VBoxManage emits a warning message along with the VM information.

        return virtualMachines


    def getVirtualMachinesFromConfigPrior4dot3( self ):
        virtualMachines = [ ]
        line = pythonutils.processGet( "grep GUI/SelectorVMPositions " + IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_4_DOT_3_PRIOR )
        try:
            uuids = list( line.rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )
            for uuid in uuids:
                virtualMachines.append( virtualmachine.Info( "", False, uuid, 0 ) )                

        except Exception as e:
            logging.exception( e )
            virtualMachines = [ ] # The VM order has never been altered giving an empty result (and exception).

        return virtualMachines


    def getVirtualMachinesFromConfig4dot3( self ):
        # The config file may exist in one of two places, particularly if the user has done an upgrade or uses an older version of Ubuntu.
        # https://www.virtualbox.org/manual/ch10.html#idp46730491656240
        configFile = None
        if os.path.isfile( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_4_DOT_3_OR_GREATER ):
            configFile = IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_4_DOT_3_OR_GREATER
        elif os.path.isfile( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_4_DOT_3_PRIOR ):
            configFile = IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_4_DOT_3_PRIOR

        virtualMachines = [ ]
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
            logging.exception( e )
            virtualMachines = [ ]

        return virtualMachines


    def groupsExist( self, virtualMachines ):
        for virtualMachine in virtualMachines:
            if virtualMachine.isGroup():
                return True

        return False


    def startVirtualMachine( self, virtualMachine, delayInSeconds ):
        if virtualMachine is None:
            message = _( "The VM could not be found - perhaps it has been renamed or deleted.  The list of VMs has been refreshed - please try again." )
            Notify.Notification.new( _( "Error" ), message, IndicatorVirtualBox.ICON ).show()

        elif virtualMachine.getUUID() in self.getRunningVirtualMachines():
            self.bringWindowToFront( virtualMachine.getName() )

        else:
            try:
                startCommand = self.getStartCommand( virtualMachine.getUUID() ).replace( "%VM%", virtualMachine.getUUID() ) + " &"
                pythonutils.processCall( startCommand )
                GLib.timeout_add_seconds( 10, self.onRefresh, False ) # Delay the call to refresh (which builds the menu) because the VM will have been started in the background and VBoxManage will not have had time to update.
                if delayInSeconds > 0:
                    time.sleep( delayInSeconds )

            except Exception as e:
                logging.exception( e )
                message = _( "The VM '{0}' could not be started." ).format( virtualMachine.getUUID() )
                Notify.Notification.new( _( "Error" ), message, IndicatorVirtualBox.ICON ).show()


    # repeat: If True, will return True resulting in onRefresh being repeatedly called.  On False, onRefresh will no longer be called.
    def onRefresh( self, repeat ):
        GLib.idle_add( self.buildMenu, self.getVirtualMachines() )
        return repeat # https://developer.gnome.org/pygobject/stable/glib-functions.html


    def getStartCommand( self, uuid ):
        if uuid in self.virtualMachinePreferences:
            return self.virtualMachinePreferences[ uuid ][ 1 ]

        return IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT


    def isAutostart( self, uuid ): return uuid in self.virtualMachinePreferences and self.virtualMachinePreferences[ uuid ][ 0 ]


    def isVirtualMachineNameUnique( self, name, virtualMachines ):
        count = 0
        for virtualMachine in virtualMachines:
            if virtualMachine.getName() == name:
                count += 1

        return count == 1


    def onAbout( self, widget ):
        if self.dialog is None:
            self.dialog = pythonutils.createAboutDialog(
                [ IndicatorVirtualBox.AUTHOR ],
                IndicatorVirtualBox.COMMENTS, 
                [ ],
                "",
                Gtk.License.GPL_3_0,
                IndicatorVirtualBox.ICON,
                INDICATOR_NAME,
                IndicatorVirtualBox.WEBSITE,
                IndicatorVirtualBox.VERSION,
                _( "translator-credits" ),
                _( "View the" ),
                _( "text file." ),
                _( "changelog" ) )

            self.dialog.run()
            self.dialog.destroy()
            self.dialog = None
        else:
            self.dialog.present()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        notebook = Gtk.Notebook()

        # List of VMs.
        stack = [ ]
        store = Gtk.TreeStore( str, str, str, str ) # Name of VM/Group, tick icon (Gtk.STOCK_APPLY) or None for autostart of VM, VM start command, UUID.
        parent = None
        virtualMachines = self.getVirtualMachines()
        for virtualMachine in virtualMachines:
            while virtualMachine.getIndent() < len( stack ):
                parent = stack.pop()

            if virtualMachine.isGroup():
                stack.append( parent )
                parent = store.append( parent, [ virtualMachine.getName(), None, "", virtualMachine.getUUID() ] )
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
        tree.set_tooltip_text( _( "Double click to edit a VM's properties." ) )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onVirtualMachineDoubleClick )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( tree )
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )

        notebook.append_page( scrolledWindow, Gtk.Label( _( "Virtual Machines" ) ) )

        # General settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 20 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )        
        grid.set_margin_bottom( 10 )

        showAsSubmenusCheckbox = Gtk.CheckButton( _( "Show groups as submenus" ) )
        showAsSubmenusCheckbox.set_tooltip_text( _(
            "Groups can be shown with their VMs\n" + \
            "in submenus, or shown with their\n" + \
            "VMs as an indented list." ) )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )

        sortAlphabeticallyCheckbox = Gtk.CheckButton( _( "Sort VMs alphabetically" ) )
        sortAlphabeticallyCheckbox.set_tooltip_text( _(
            "VMs can be sorted alphabetically or\n" + \
            "as set in the VirtualBox Manager." ) )
        sortAlphabeticallyCheckbox.set_active( not self.sortDefault )

        version = self.getVirtualBoxVersion()
        if self.isVBoxManageInstalled() and version is not None:
            if version < IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION:
                grid.attach( sortAlphabeticallyCheckbox, 0, 0, 2, 1 )
            else:
                if self.groupsExist( virtualMachines ):
                    grid.attach( showAsSubmenusCheckbox, 0, 0, 2, 1 )

        label = Gtk.Label( _( "Refresh interval (minutes)" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        spinnerRefreshInterval = Gtk.SpinButton()
        spinnerRefreshInterval.set_adjustment( Gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerRefreshInterval.set_value( self.refreshIntervalInMinutes ) # ...so need to force the initial value by explicitly setting it.
        spinnerRefreshInterval.set_tooltip_text( _(
            "How often the list of VMs and\n" + \
            "running status is updated." ) )
        grid.attach( spinnerRefreshInterval, 1, 1, 1, 1 )

        label = Gtk.Label( _( "Startup delay (seconds)" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        spinnerDelay = Gtk.SpinButton()
        spinnerDelay.set_adjustment( Gtk.Adjustment( self.delayBetweenAutoStartInSeconds, 1, 60, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerDelay.set_value( self.delayBetweenAutoStartInSeconds ) # ...so need to force the initial value by explicitly setting it.
        spinnerDelay.set_tooltip_text( _(
            "Amount of time to wait from\n" + \
            "starting one VM to the next." ) )
        grid.attach( spinnerDelay, 1, 2, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorVirtualBox.DESKTOP_FILE, logging ) )
        grid.attach( autostartCheckbox, 0, 3, 2, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        self.dialog = Gtk.Dialog( _( "Preferences" ), None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorVirtualBox.ICON )
        self.dialog.show_all()

        if self.dialog.run() == Gtk.ResponseType.OK:
            self.delayBetweenAutoStartInSeconds = spinnerDelay.get_value_as_int()
            self.showSubmenu = showAsSubmenusCheckbox.get_active()
            self.sortDefault = not sortAlphabeticallyCheckbox.get_active()

            self.refreshIntervalInMinutes = spinnerRefreshInterval.get_value_as_int()
            GLib.source_remove( self.timeoutID )
            self.timeoutID = GLib.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.onRefresh, True )

            self.virtualMachinePreferences.clear()
            self.updateVirtualMachinePreferences( store, tree.get_model().get_iter_first() )

            self.saveSettings()
            pythonutils.setAutoStart( IndicatorVirtualBox.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            GLib.timeout_add_seconds( 1, self.onRefresh, False )

        self.dialog.destroy()
        self.dialog = None


    def updateVirtualMachinePreferences( self, store, treeiter ):
        while treeiter is not None:
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
        if treeiter is not None and model[ treeiter ][ 3 ] != "":
            self.editVirtualMachine( model, treeiter )


    def editVirtualMachine( self, model, treeiter ):
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( _( "Start Command" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        startCommand = Gtk.Entry()
        startCommand.set_width_chars( 20 )
        if model[ treeiter ][ 2 ] is not None:
            startCommand.set_text( model[ treeiter ][ 2 ] )
            startCommand.set_width_chars( len( model[ treeiter ][ 2 ] ) * 5 / 4 ) # Sometimes the length is shorter than specified due to packing, so make it longer.

        startCommand.set_tooltip_text( _(
            "The terminal command to start the\n" + \
            "VM such as\n" + \
            "\t'VBoxManage startvm %VM%' or\n" + \
            "\t'VBoxHeadless --startvm %VM% --vrde off'" ) )
        startCommand.set_hexpand( True ) # Only need to set this once and all objects will expand.
        grid.attach( startCommand, 1, 0, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the VM when the indicator starts." ) )
        autostartCheckbox.set_active( model[ treeiter ][ 1 ] is not None and model[ treeiter ][ 1 ] == Gtk.STOCK_APPLY )
        grid.attach( autostartCheckbox, 0, 1, 2, 1 )

        # Would be nice to be able to bring this dialog to front (like the others)...but too much mucking around for little gain!
        dialog = Gtk.Dialog( _( "VM Properties" ), self.dialog, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorVirtualBox.ICON )

        while True:
            dialog.show_all()

            if dialog.run() != Gtk.ResponseType.OK:
                break

            if startCommand.get_text().strip() == "":
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The start command cannot be empty." ), INDICATOR_NAME )
                startCommand.grab_focus()
                continue

            if not "%VM%" in startCommand.get_text().strip():
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The start command must contain %VM% which is substituted for the VM name/id." ), INDICATOR_NAME )
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


    def loadSettings( self ):
        self.delayBetweenAutoStartInSeconds = 30
        self.refreshIntervalInMinutes = 15
        self.showSubmenu = False
        self.sortDefault = True
        self.virtualMachinePreferences = { } # Store information about VMs (not groups). Key is VM UUID; value is [ autostart (bool), start command (str) ]

        if os.path.isfile( IndicatorVirtualBox.SETTINGS_FILE ):
            try:
                with open( IndicatorVirtualBox.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.delayBetweenAutoStartInSeconds = settings.get( IndicatorVirtualBox.SETTINGS_DELAY_BETWEEN_AUTO_START, self.delayBetweenAutoStartInSeconds )
                self.refreshIntervalInMinutes = settings.get( IndicatorVirtualBox.SETTINGS_REFRESH_INTERVAL_IN_MINUTES, self.refreshIntervalInMinutes )
                self.showSubmenu = settings.get( IndicatorVirtualBox.SETTINGS_SHOW_SUBMENU, self.showSubmenu )
                self.sortDefault = settings.get( IndicatorVirtualBox.SETTINGS_SORT_DEFAULT, self.sortDefault )
                self.virtualMachinePreferences = settings.get( IndicatorVirtualBox.SETTINGS_VIRTUAL_MACHINE_PREFERENCES, self.virtualMachinePreferences )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorVirtualBox.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorVirtualBox.SETTINGS_DELAY_BETWEEN_AUTO_START: self.delayBetweenAutoStartInSeconds,
                IndicatorVirtualBox.SETTINGS_REFRESH_INTERVAL_IN_MINUTES: self.refreshIntervalInMinutes,
                IndicatorVirtualBox.SETTINGS_SHOW_SUBMENU: self.showSubmenu,
                IndicatorVirtualBox.SETTINGS_SORT_DEFAULT: self.sortDefault,
                IndicatorVirtualBox.SETTINGS_VIRTUAL_MACHINE_PREFERENCES: self.virtualMachinePreferences
            }

            with open( IndicatorVirtualBox.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorVirtualBox.SETTINGS_FILE )


if __name__ == "__main__": IndicatorVirtualBox().main()