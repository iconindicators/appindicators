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


# Application indicator which displays/controls VirtualBox™ virtual machines.


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  https://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/api/AppIndicator3_0.1/classes/Indicator.html
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-14.04


#TODO Is this still relevant?
# Have noticed that if a VM exists in a group and there is another VM of the same name but not in a group
# and the group is then ungrouped, the VirtualBox UI doesn't handle it well...
# ...the UI keeps the group and the VM within it (but removes all unique VMs from the group).
# The VirtualBox.xml file does seem to reflect the change (and the indicator obeys this file).


#TODO Old comment...use this to test!
# Sometimes the VirtualBox.xml file does not accurately reflect changes made in the VirtualBox GUI...
#
#    If a VM is added to a group and then group is ungrouped, the GUI/GroupDefinition remains, listing that VM.  
#    If another VM is created, the GUI/GroupDefinitions only lists the original/first VM...giving an incorrect reading.
#
#    If a VM is created and added to a group and a VM is later created of the same name but not in a group,
#    that new VM is not listed (and neither are subsequent VMs).
#
# So take what information the groups gave and append to that the VMs which are missing (from the backend information).


INDICATOR_NAME = "indicator-virtual-box"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import AppIndicator3, GLib, Gtk
from threading import Thread

import gzip, json, locale, logging, os, pythonutils, re, shutil, sys, time, virtualmachine


class IndicatorVirtualBox:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.38"
    ICON = INDICATOR_NAME
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    DESKTOP_FILE = INDICATOR_NAME + ".desktop"

    VIRTUAL_BOX_CONFIGURATION_4_DOT_3_OR_GREATER = os.getenv( "HOME" ) + "/.config/VirtualBox/VirtualBox.xml"
    VIRTUAL_BOX_CONFIGURATION_PRIOR_4_DOT_3 = os.getenv( "HOME" ) + "/.VirtualBox/VirtualBox.xml"
    VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION = "4.3" # Configuration file location and format changed at this version (https://www.virtualbox.org/manual/ch10.html#idp99351072).

    VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT = "VBoxManage startvm %VM%"
    VIRTUAL_MACHINE_STARTUP_MINIMUM_DELAY_IN_SECONDS = 5

    COMMENTS = _( " Shows VirtualBox™ virtual machines and allows them to be started." )

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
        virtualMachines = self.getVirtualMachines()
        Thread( target = self.autoStartVirtualMachines, args = ( virtualMachines, ) ).start()
        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorVirtualBox.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.buildMenu( virtualMachines )
        self.timeoutID = GLib.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.onRefresh )


    def main( self ): Gtk.main()


#TODO Might need to block the preferences until this is finished?
# Rather than lockout, maybe rebuild the menu with a flag to enable the prefernces menu item?
# Or just enable the preferences item?
# What is bad if the prefs are opened (and modified/saved) if we are still autostarting?
    def autoStartVirtualMachines( self, virtualMachines ):
        for virtualMachine in virtualMachines:
            if self.isAutostart( virtualMachine.getUUID() ):
                self.startVirtualMachine( virtualMachine, virtualMachines, self.delayBetweenAutoStartInSeconds )


    def buildMenu( self, virtualMachines ):
        menu = Gtk.Menu()
        if self.isVirtualBoxInstalled():
            if len( virtualMachines ) == 0:
                menu.append( Gtk.MenuItem( _( "(no virtual machines exist)" ) ) ) #TODO Test...
            else:
                if self.showSubmenu == True:
                    stack = [ ]
                    currentMenu = menu
                    for i in range( len( virtualMachines ) ):
                        virtualMachine = virtualMachines[ i ]
                        while virtualMachine.getIndent() < len( stack ):
                            currentMenu = stack.pop()

                        if virtualMachine.isGroup():
                            menuItem = Gtk.MenuItem( virtualMachine.getName()[ virtualMachine.getName().rfind( "/" ) + 1 : ] )
                            currentMenu.append( menuItem )
                            subMenu = Gtk.Menu()
                            menuItem.set_submenu( subMenu )
                            stack.append( currentMenu )
                            currentMenu = subMenu
                        else:
                            currentMenu.append( self.createMenuItemForVirtualMachine( virtualMachine, "" ) )
                else:
                    for virtualMachine in virtualMachines:
                        indent = "    " * virtualMachine.getIndent()
                        if virtualMachine.isGroup():
                            menu.append( Gtk.MenuItem( indent + virtualMachine.getName()[ virtualMachine.getName().rfind( "/" ) + 1 : ] ) )
                        else:
                            menu.append( self.createMenuItemForVirtualMachine( virtualMachine, indent ) )

            menu.append( Gtk.SeparatorMenuItem() )
            menuItem = Gtk.MenuItem( _( "Launch VirtualBox Manager" ) )
            menuItem.connect( "activate", self.onLaunchVirtualBoxManager )
            menu.append( menuItem )
            
        else:
            menu.insert( Gtk.MenuItem( _( "(VirtualBox is not installed)" ) ), 0 )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, False, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def createMenuItemForVirtualMachine( self, virtualMachine, indent ):
        if virtualMachine.isRunning(): # No need to check if this is a group...groups never "run" and this function should only be called for a VM and never a group.
            menuItem = Gtk.RadioMenuItem.new_with_label( [], indent + virtualMachine.getName() )
            menuItem.set_active( True )
        else:
            menuItem = Gtk.MenuItem( indent + virtualMachine.getName() )

        menuItem.props.name = virtualMachine.getUUID()
        menuItem.connect( "activate", self.onVirtualMachine )
        return menuItem


    def onLaunchVirtualBoxManager( self, widget ):
        p = pythonutils.callProcess( 'wmctrl -l | grep "Oracle VM VirtualBox Manager"' ) #TODO Check this works in Russian!
        result = p.communicate()[ 0 ].decode()
        p.wait()
        if result == "":
            pythonutils.callProcess( "VirtualBox &" )
        else:
            windowID = result[ 0 : result.find( " " ) ]
            pythonutils.callProcess( "wmctrl -i -a " + windowID ).wait()


    def onVirtualMachine( self, widget ):
        virtualMachines = self.getVirtualMachines()
        virtualMachine = self.getVirtualMachine( widget.props.name, virtualMachines )
        self.startVirtualMachine( virtualMachine, virtualMachines, IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_MINIMUM_DELAY_IN_SECONDS )


    def isVirtualBoxInstalled( self ): return pythonutils.callProcess( "which VBoxManage" ).communicate()[ 0 ].decode() != ''


    def getVirtualBoxVersion( self ): return pythonutils.callProcess( "VBoxManage --version" ).communicate()[ 0 ].decode().strip()


    def getVirtualMachines( self ):
        virtualMachines = [ ]
        if self.isVirtualBoxInstalled():
            virtualMachinesFromVBoxManage = self.getVirtualMachinesFromVBoxManage() # Does not contain group information, nor sort order.
            if len( virtualMachinesFromVBoxManage ) > 0:
                if self.getVirtualBoxVersion() < IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION:
                    virtualMachinesFromConfig = self.getVirtualMachinesFromConfigPrior4dot3()
                else:
                    virtualMachinesFromConfig = self.getVirtualMachinesFromConfig4dot3()

                # Going forward, the virtual machine infos from the config is the definitive list of VMs (and groups if any).
                virtualMachines = virtualMachinesFromConfig

                # The virtual machine infos from the config do not contain the names of virtual machines.
                # Obtain the names from the virtual machine infos from VBoxManage.
                for virtualmachineFromVBoxManage in virtualMachinesFromVBoxManage:
                    for virtualMachine in virtualMachines:
                        if virtualmachineFromVBoxManage.getUUID() == virtualMachine.getUUID():
                            virtualMachine.setName( virtualmachineFromVBoxManage.getName() )
                            break

#TODO What about VMs from the config which are not in the backend?  This is an error right?  Can it ever happen?
#maybe log these as warnings?

                # Determine which VMs are running.
                p = pythonutils.callProcess( "VBoxManage list runningvms" )
                for line in p.stdout.readlines():
                    try:
                        info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
                        for virtualMachine in virtualMachines:
                            if virtualMachine.getUUID() == info[ 1 ]:
                                virtualMachine.setRunning()
                    except:
                        pass # Sometimes VBoxManage emits a warning message along with the VM information.

                p.wait()

                # Alphabetically sort...
                if self.sortDefault == False and not self.groupsExist( virtualMachines ):
                    virtualMachines = sorted( virtualMachines, key = lambda virtualMachine: virtualMachine.name )

        return virtualMachines


    # The returned list of virtualmachine.Info objects does not include any groups (if present) nor any order set by the user in the GUI.
    def getVirtualMachinesFromVBoxManage( self ):
        p = pythonutils.callProcess( "VBoxManage list vms" )
        virtualMachines = []
        for line in p.stdout.readlines():
            try:
                info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
                virtualMachine = virtualmachine.Info( info[ 0 ], False, info[ 1 ], 0 )
                virtualMachines.append( virtualMachine )
            except:
                pass # Sometimes VBoxManage emits a warning message along with the VM information.

        p.wait()
        return virtualMachines


    def getVirtualMachinesFromConfigPrior4dot3( self ):
        virtualMachines = []
        p = pythonutils.callProcess( "grep GUI/SelectorVMPositions " + IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_PRIOR_4_DOT_3 )
        try:
            uuids = list( p.communicate()[ 0 ].decode().rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )
            for uuid in uuids:
                virtualMachines.append( virtualmachine.Info( "", False, uuid, 0 ) )                
        except:
#TODO Should something be logged?
            virtualMachines = [] # The VM order has never been altered giving an empty result (and exception).

        return virtualMachines


    def getVirtualMachinesFromConfig4dot3( self ):
        virtualMachines = []
        try:
            with open( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_4_DOT_3_OR_GREATER, "r" ) as f:
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
#TODO Should something be logged?
            virtualMachines = []

        return virtualMachines


    def groupsExist( self, virtualMachines ):
        for virtualMachine in virtualMachines:
            if virtualMachine.isGroup():
                return True

        return False


    def onRefresh( self ):
        GLib.idle_add( self.buildMenu, self.getVirtualMachines() )
        return True # http://www.pygtk.org/pygtk2reference/gobject-functions.html#function-gi--timeout-add


#TODO Not sure if this delay (user specified between auto start multiple vms) is the same as delaying to give VBoxManage time to refresh...think!
    def startVirtualMachine( self, virtualMachine, virtualMachines, delayInSeconds ):
        if virtualMachine is None:
            pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "The VM could not be found - either it has been renamed or deleted.  The list of VMs has been refreshed - please try again." ) )

        elif virtualMachine.isRunning(): # Attempt to use the window manager to bring the VM window to the front.
            if self.isVirtualMachineNameUnique( virtualMachine.getName(), virtualMachines ):
                windowID = None
                p = pythonutils.callProcess( "wmctrl -l" )
                for line in p.stdout.readlines():
                    lineAsString = str( line.decode() )
                    if virtualMachine.getName() in lineAsString:
                        windowID = lineAsString[ 0 : lineAsString.find( " " ) ]
                        break

                p.wait()

                if windowID is None:
                    pythonutils.showMessage( None, Gtk.MessageType.WARNING, _( "The VM is running but its window could not be found - perhaps it is running headless." ) )
                else:
                    pythonutils.callProcess( "wmctrl -i -a " + windowID ).wait()

            else:
                pythonutils.showMessage( None, Gtk.MessageType.WARNING, _( "There is more than one VM with the same name - unfortunately your VM cannot be uniquely identified." ) )

        else: # Run the VM!
            try:
                startCommand = self.getStartCommand( virtualMachine.getUUID() ).replace( "%VM%", virtualMachine.getUUID() ) + " &"
                pythonutils.callProcess( startCommand ).wait()

                # The start command returns immediately due to '&', so give VBoxManage a moment to catch up and refresh.
                # Use the specified delay but don't delay less than the minimum.
                if delayInSeconds < IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_MINIMUM_DELAY_IN_SECONDS:
                    time.sleep( IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_MINIMUM_DELAY_IN_SECONDS )
                else:
                    time.sleep( delayInSeconds )

            except Exception as e:
                logging.exception( e )
                pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "The VM '{0}' could not be started - check the log file: {1}" ).format( virtualMachine.getUUID(), IndicatorVirtualBox.LOG ) )

        self.onRefresh()


    def getVirtualMachine( self, uuid, virtualMachines ):
        for virtualMachine in virtualMachines:
            if virtualMachine.getUUID() == uuid:
                return virtualMachine

        return None


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
            self.dialog = pythonutils.AboutDialog( 
                INDICATOR_NAME,
                IndicatorVirtualBox.COMMENTS, 
                IndicatorVirtualBox.WEBSITE, 
                IndicatorVirtualBox.WEBSITE, 
                IndicatorVirtualBox.VERSION, 
                Gtk.License.GPL_3_0, 
                IndicatorVirtualBox.ICON,
                [ IndicatorVirtualBox.AUTHOR ],
                "",
                "",
                "/usr/share/doc/" + INDICATOR_NAME + "/changelog.Debian.gz",
                _( "Change _Log" ),
                _( "translator-credits" ),
                logging )

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
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )
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

        if self.getVirtualBoxVersion() < IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION:
            grid.attach( sortAlphabeticallyCheckbox, 0, 0, 2, 1 )
        else:
            if self.groupsExist( virtualMachines ):
                grid.attach( showAsSubmenusCheckbox, 0, 0, 2, 1 ) # TODO Test for when groups don't exist...does the dialog look odd?

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
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorVirtualBox.DESKTOP_FILE ) )
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
            self.timeoutID = GLib.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.onRefresh )

            self.virtualMachinePreferences.clear()
            self.updateVirtualMachinePreferences( store, tree.get_model().get_iter_first() )
            self.saveSettings()
            pythonutils.setAutoStart( IndicatorVirtualBox.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            self.onRefresh()

        self.dialog.destroy()
        self.dialog = None


    def updateVirtualMachinePreferences( self, store, treeiter ):
        while treeiter is not None:
            isVM = store[ treeiter ][ 3 ] != "" # UUID is not empty, so this is a VM and not a group.
            isAutostart = store[ treeiter ][ 1 ] == "gtk-apply"
            isDefaultStartCommand = store[ treeiter ][ 2 ] == IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_COMMAND_DEFAULT
            if ( isVM and isAutostart ) or ( isVM and not isDefaultStartCommand ): # Only record VMs with different settings to default.
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
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The start command cannot be empty." ) )
                startCommand.grab_focus()
                continue

            if not "%VM%" in startCommand.get_text().strip():
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The start command must contain %VM% which is substituted for the VM name/id." ) )
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