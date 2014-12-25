#!/usr/bin/env python3


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


# Application indicator which displays/controls VirtualBox virtual machines.


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  https://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/api/AppIndicator3_0.1/classes/Indicator.html
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-14.04


# Have noticed that if a VM exists in a group and there is another VM of the same name but not in a group
# and the group is then ungrouped, the VirtualBox UI doesn't handle it well...
# ...the UI keeps the group and the VM within it (but removes all unique VMs from the group).
# The VirtualBox.xml file does seem to reflect the change (and the indicator obeys this file).


from gi.repository import AppIndicator3, GLib, Gtk

import gzip, json, locale, logging, os, pythonutils, re, shutil, subprocess, sys, time, virtualmachine


class IndicatorVirtualBox:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-virtual-box"
    VERSION = "1.0.36"
    ICON = NAME
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    # Seems that the configuration file has moved between versions of VirtualBox.
    # In fact the config file can exist in TWO places simultaneously...
    # ...with one file containing group information and the other file containing non-group information.
    VIRTUAL_BOX_CONFIGURATION_A = os.getenv( "HOME" ) + "/.config/VirtualBox/VirtualBox.xml"
    VIRTUAL_BOX_CONFIGURATION_B = os.getenv( "HOME" ) + "/.VirtualBox/VirtualBox.xml"

    VIRTUAL_MACHINE_STARTUP_DELAY_IN_SECONDS = 5

    COMMENTS = " Shows VirtualBox™ virtual machines and allows them to be started."

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_DELAY_BETWEEN_AUTO_START = "delayBetweenAutoStartInSeconds"
    SETTINGS_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    SETTINGS_SHOW_SUBMENU = "showSubmenu"
    SETTINGS_SORT_DEFAULT = "sortDefault"
    SETTINGS_VIRTUAL_MACHINE_PREFERENCES = "virtualMachinePreferences"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorVirtualBox.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )

        self.loadSettings()
        self.dialog = None

        # Start up VMs...
        self.getVirtualMachines()
        previousVMNeededStarting = False
        for virtualMachineInfo in self.virtualMachineInfos:
            if virtualMachineInfo.getAutoStart():
                if previousVMNeededStarting and not virtualMachineInfo.isRunning:
                    time.sleep( self.delayBetweenAutoStartInSeconds )

                previousVMNeededStarting = not virtualMachineInfo.isRunning

                # Create a dummy widget (radio button) and use that to kick off the start VM function...
                radioButton = Gtk.RadioButton.new_with_label_from_widget( None, "" )                    
                radioButton.props.name = virtualMachineInfo.getUUID()
                self.onStartVirtualMachine( radioButton, False )

        self.indicator = AppIndicator3.Indicator.new( IndicatorVirtualBox.NAME, IndicatorVirtualBox.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling!
        self.buildMenu()


    def main( self ):
        self.timeoutID = GLib.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.onRefresh )
        Gtk.main()


    def buildMenu( self ):
        menu = Gtk.Menu()
        if self.isVirtualBoxInstalled():
            self.getVirtualMachines()
            if len( self.virtualMachineInfos ) == 0:
                menu.append( Gtk.MenuItem( "(no virtual machines exist)" ) )
            else:
                if self.showSubmenu == True:
                    stack = [ ]
                    currentMenu = menu
                    for i in range( len( self.virtualMachineInfos ) ):
                        virtualMachineInfo = self.virtualMachineInfos[ i ]
                        if virtualMachineInfo.getIndent() < len( stack ):
                            currentMenu = stack.pop() # We previously added a VM in a group and now we are adding a VM at the same indent as the group.

                        if virtualMachineInfo.isGroup():
                            menuItem = Gtk.MenuItem( virtualMachineInfo.getName() )

                            currentMenu.append( menuItem )
                            subMenu = Gtk.Menu()
                            menuItem.set_submenu( subMenu )
                            stack.append( currentMenu ) # Whatever we create next is a child of this group, so save the current menu.
                            currentMenu = subMenu
                        else:
                            if virtualMachineInfo.isRunning: # No need to check if this is a group...groups never "run"!
                                menuItem = Gtk.RadioMenuItem.new_with_label( [], virtualMachineInfo.getName() )
                                menuItem.set_active( True )
                            else:
                                menuItem = Gtk.MenuItem( virtualMachineInfo.getName() )

                            menuItem.props.name = virtualMachineInfo.getUUID()
                            menuItem.connect( "activate", self.onStartVirtualMachine, True )
                            currentMenu.append( menuItem )
                else:
                    for virtualMachineInfo in self.virtualMachineInfos:
                        indent = "    " * virtualMachineInfo.getIndent()
                        if virtualMachineInfo.isGroup():
                            vmMenuItem = Gtk.MenuItem( indent + virtualMachineInfo.getName() )
                        else:
                            if virtualMachineInfo.isRunning:
                                vmMenuItem = Gtk.RadioMenuItem.new_with_label( [], indent + virtualMachineInfo.getName() )
                                vmMenuItem.set_active( True )
                            else:
                                vmMenuItem = Gtk.MenuItem( indent + virtualMachineInfo.getName() )
    
                            vmMenuItem.props.name = virtualMachineInfo.getUUID()
                            vmMenuItem.connect( "activate", self.onStartVirtualMachine, True )

                        menu.append( vmMenuItem )

            menu.append( Gtk.SeparatorMenuItem() )

            self.virtualBoxMenuItem = Gtk.MenuItem( "Launch VirtualBox Manager" )
            self.virtualBoxMenuItem.connect( "activate", self.onLaunchVirtualBox )
            menu.append( self.virtualBoxMenuItem )
        else:
            menu.insert( Gtk.MenuItem( "(VirtualBox is not installed)" ), 0 )
            menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
        menuItem.connect( "activate", self.onPreferences )
        menu.append( menuItem )

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        menuItem.connect( "activate", self.onAbout )
        menu.append( menuItem )

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        menuItem.connect( "activate", Gtk.main_quit )
        menu.append( menuItem )

        self.indicator.set_menu( menu )
        menu.show_all()


    def isVirtualBoxInstalled( self ):
        p = subprocess.Popen( "which VBoxManage", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        return p.communicate()[ 0 ].decode() != ''


    def getVirtualMachines( self ):
        self.virtualMachineInfos = [ ] # A list of VirtualBox items.

        if not self.isVirtualBoxInstalled(): return

        self.virtualMachineInfos = self.getVirtualMachinesFromBackend()
        if len( self.virtualMachineInfos ) == 0: return

        # We have a list of VMs and UUIDs - now obtain groups or sort order.
        # The configuration file can exist in different locations depending on the version of VirtualBox.
        # Further, two config files can be in active use simultaneously - one for groups and the other for general GUI.
        # So need to parse both files...if they exist.
        virtualMachineInfosA = self.getVirtualMachinesFromConfigFile( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_A ) 
        virtualMachineInfosB = self.getVirtualMachinesFromConfigFile( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_B ) 

        # Information from config A takes precedence over config B as it appears config A is what the latest VirtualBox release uses.
        # If neither config has information, use what was obtained from the backend.
        if len( virtualMachineInfosA ) > 0 or len( virtualMachineInfosB ) > 0:
            if len( virtualMachineInfosA ) > 0:
                self.virtualMachineInfos = virtualMachineInfosA
            else:
                self.virtualMachineInfos = virtualMachineInfosB

        # Determine which VMs are running...
        p = subprocess.Popen( "VBoxManage list runningvms", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        for line in p.stdout.readlines():
            try:
                info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
                for virtualMachineInfo in self.virtualMachineInfos:
                    if virtualMachineInfo.getUUID() == info[ 1 ]:
                        virtualMachineInfo.setRunning()
            except: pass # Sometimes VBoxManage emits a warning message along with the VM information.

        p.wait()

        # Alphabetically sort...
        if self.sortDefault == False and not self.groupsExist():
            self.virtualMachineInfos = sorted( self.virtualMachineInfos, key = lambda virtualMachineInfo: virtualMachineInfo.name )

        # Add to each VM its properties (autostart and the start command).
        for uuid in self.virtualMachinePreferences:
            virtualMachineInfo = self.getVirtualMachineInfo( uuid )
            if virtualMachineInfo is not None:
                virtualMachineInfo.setAutoStart( self.virtualMachinePreferences[ uuid ][ 0 ] == Gtk.STOCK_APPLY )
                virtualMachineInfo.setStartCommand( self.virtualMachinePreferences[ uuid ][ 1 ] )


    # Obtain a list of VMs using VBoxManage.
    # This does not include any groups (if present) nor any order set by the user in the GUI.
    def getVirtualMachinesFromBackend( self ):
        p = subprocess.Popen( "VBoxManage list vms", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        virtualMachineInfos = []
        for line in p.stdout.readlines():
            try:
                info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
                virtualMachineInfo = virtualmachine.Info( info[ 0 ], False, info[ 1 ], 0 )
                virtualMachineInfos.append( virtualMachineInfo )
            except: pass # Sometimes VBoxManage emits a warning message along with the VM information.

        p.wait()
        return virtualMachineInfos


    # Parse the specified VirtualBox.xml file to obtain a list of VMs together with groups or sort order. 
    def getVirtualMachinesFromConfigFile( self, configFile ):
        virtualMachineInfos = [ ]
        if os.path.exists( configFile ):
            virtualMachineInfos = self.parseGroupDefinitions( configFile, "GUI/GroupDefinitions/", 0 ) # Attempt to get the groups and UUIDs.
            if len( virtualMachineInfos ) == 0: # There was no group data, so attempt to get UI sort order...
                virtualMachineInfos = self.parseSelectorVMPositions( configFile )

            if len( virtualMachineInfos ) > 0:
                # Sometimes the VirtualBox.xml file does not accurately reflect changes made in the VirtualBox GUI...
                #
                #    If a VM is added to a group and then group is ungrouped, the GUI/GroupDefinition remains, listing that VM.  
                #    If another VM is created, the GUI/GroupDefinitions only lists the original/first VM...giving an incorrect reading.
                #
                #    If a VM is created and added to a group and a VM is later created of the same name but not in a group,
                #    that new VM is not listed (and neither are subsequent VMs).
                #
                # So take what information the groups gave and append to that the VMs which are missing (from the backend information).
                for virtualMachineInfoFromBackEnd in self.virtualMachineInfos:
                    found = False
                    for virtualMachineInfo in virtualMachineInfos:
                        if virtualMachineInfoFromBackEnd.getUUID() == virtualMachineInfo.getUUID():
                            found = True
                            break

                    if found == False:
                        virtualMachineInfos.append( virtualMachineInfoFromBackEnd )

                # Now have a list of group names and VM UUIDs OR a list of VM UUIDs.
                # The VM names though are not present, so get the VM names from the list from the backend...
                for virtualMachineInfoFromBackEnd in self.virtualMachineInfos:
                    for virtualMachineInfo in virtualMachineInfos:
                        if virtualMachineInfoFromBackEnd.getUUID() == virtualMachineInfo.getUUID():
                            virtualMachineInfo.setName( virtualMachineInfoFromBackEnd.getName() )
                            break

        return virtualMachineInfos


    # Obtain a list of VMs and their sort order by parsing the specified VirtualBox.xml configuration file.
    # This approach works when no groups have been created by the user or the version of VirtualBox does not support groups.
    def parseSelectorVMPositions( self, configFile ):
        virtualMachineInfos = []
        p = subprocess.Popen( "grep GUI/SelectorVMPositions " + configFile, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        try:
            uuids = list( p.communicate()[ 0 ].decode().rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )
            for uuid in uuids:
                virtualMachineInfo = virtualmachine.Info( "", False, uuid, 0 )
                virtualMachineInfos.append( virtualMachineInfo )                
        except: virtualMachineInfos = [] # The VM order has never been altered giving an empty result (and exception).
            
        return virtualMachineInfos


    # Obtain a list of VMs including group names and group structure by parsing the specified VirtualBox.xml configuration file.
    # The returned information contains no VM names - these need to be filled in by the caller.
    def parseGroupDefinitions( self, configFile, grepString, indentAmount ):
        virtualMachineInfos = []
        p = subprocess.Popen( "grep \"" + grepString + "\\\"\" " + configFile, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        try:
            items = list( p.communicate()[ 0 ].decode().rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )
            for item in items:
                itemName = str( item ).split( "=" )[ 1 ] 
                if str( item ).startswith( "go" ) or str( item ).startswith( "gc" ):
                    virtualMachineInfo = virtualmachine.Info( itemName, True, "", indentAmount ) # For a group there is no UUID.
                    virtualMachineInfos.append( virtualMachineInfo )
                    if grepString.endswith( "/" ):
                        virtualMachineInfos += self.parseGroupDefinitions( configFile, grepString + itemName, indentAmount + 1 )
                    else:
                        virtualMachineInfos += self.parseGroupDefinitions( configFile, grepString + "/" + itemName, indentAmount + 1 )
                else:
                    virtualMachineInfo = virtualmachine.Info( "", False, itemName, indentAmount ) # This is a VM: we have it's UUID but not its name...so the caller needs to add it in.
                    virtualMachineInfos.append( virtualMachineInfo )

        except: virtualMachineInfos = []

        return virtualMachineInfos


    def groupsExist( self ):
        for virtualMachineInfo in self.virtualMachineInfos:
            if virtualMachineInfo.isGroup(): return True

        return False


    def onRefresh( self ):
        GLib.idle_add( self.buildMenu )
        return True # Must return true so that we continue to be called (http://www.pygtk.org/pygtk2reference/gobject-functions.html#function-gi--timeout-add).


    def onLaunchVirtualBox( self, widget ):
        p = subprocess.Popen( 'wmctrl -l | grep "Oracle VM VirtualBox Manager"', shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        result = p.communicate()[ 0 ].decode()
        p.wait()
        if result == "":
            subprocess.Popen( "VirtualBox &", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        else:
            windowID = result[ 0 : result.find( " " ) ]
            p = subprocess.Popen( "wmctrl -i -a " + windowID, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
            p.wait()


    def onStartVirtualMachine( self, widget, doRefresh ):
        if doRefresh: self.getVirtualMachines() # Refresh the VMs as the list could have changed (deletion, creation, rename) since the last refresh.

        virtualMachineUUID = widget.props.name
        virtualMachineInfo = self.getVirtualMachineInfo( virtualMachineUUID )
        virtualMachineName = virtualMachineInfo.getName()
        if virtualMachineName is None:
            pythonutils.showMessage( None, Gtk.MessageType.ERROR, "The VM could not be found - either it has been renamed or deleted.  The list of VMs has been refreshed - please try again." )
        elif virtualMachineInfo.isRunning:
            if self.duplicateVirtualMachineNameExists( virtualMachineName ):
                pythonutils.showMessage( None, Gtk.MessageType.ERROR, "There is more than one VM with the same name - unfortunately your VM cannot be uniquely identified." )
            else:
                windowID = None
                p = subprocess.Popen( "wmctrl -l", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
                for line in p.stdout.readlines():
                    lineAsString = str( line.decode() )
                    if virtualMachineName in lineAsString:
                        windowID = lineAsString[ 0 : lineAsString.find( " " ) ]

                p.wait()

                if windowID is None:
                    pythonutils.showMessage( None, Gtk.MessageType.ERROR, "The VM is running but its window could not be found - perhaps it is running headless" )
                else:
                    # If the VM is running headless then there will be no window to display...
                    p = subprocess.Popen( "wmctrl -i -a " + windowID, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
                    p.wait()
        else:
            try:
                startCommand = virtualMachineInfo.getStartCommand().replace( "%VM%", virtualMachineInfo.getUUID() ) + " &"
                p = subprocess.Popen( startCommand, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
                p.wait()

                # Since the start command returns immediately, the running status (from VBoxManage) may not be updated as yet.
                # Pause after kicking off the VM to give VBoxManage a chance to catch up...
                # ...then when the indicator is updated, we (hopefully) will be updated correctly!
                time.sleep( IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_DELAY_IN_SECONDS )

            except Exception as e:
                pythonutils.showMessage( None, Gtk.MessageType.ERROR, "The VM '" + virtualMachineInfo.getName() + "' could not be started - check the log file: " + IndicatorVirtualBox.LOG )
                logging.exception( e )

        if doRefresh: self.onRefresh()


    def getVirtualMachineInfo( self, virtualMachineUUID ):
        for virtualMachineInfo in self.virtualMachineInfos:
            if virtualMachineInfo.getUUID() == virtualMachineUUID:
                return virtualMachineInfo

        return None


    def duplicateVirtualMachineNameExists( self, virtualMachineName ):
        count = 0
        for virtualMachineInfo in self.virtualMachineInfos:
            if virtualMachineInfo.getName() == virtualMachineName:
                count += 1

        return count > 1


    def onPreferences( self, widget ):
        self.getVirtualMachines() # Refresh the VMs as the list could have changed (deletion, creation, rename) since the last refresh.

        if self.dialog is not None:
            self.dialog.present()
            return

        notebook = Gtk.Notebook()

        # List of VMs.
        stack = [ ]
        store = Gtk.TreeStore( str, str, str, str ) # Name of VM/Group, tick icon (Gtk.STOCK_APPLY) or None for autostart of VM, VM start command, VM/Group UUID.
        parent = None
        for virtualMachineInfo in self.virtualMachineInfos:
            if virtualMachineInfo.getIndent() < len( stack ): parent = stack.pop() # We previously added a VM in a group and now we are adding a VM at the same indent as the group.

            if virtualMachineInfo.isGroup():
                stack.append( parent )
                parent = store.append( parent, [ virtualMachineInfo.getName(), None, "", virtualMachineInfo.getUUID() ] )
            else:
                if virtualMachineInfo.getAutoStart():
                    store.append( parent, [ virtualMachineInfo.getName(), Gtk.STOCK_APPLY, virtualMachineInfo.getStartCommand(), virtualMachineInfo.getUUID() ] )
                else:
                    store.append( parent, [ virtualMachineInfo.getName(), None, virtualMachineInfo.getStartCommand(), virtualMachineInfo.getUUID() ] )

        tree = Gtk.TreeView( store )
        tree.expand_all()
        tree.set_hexpand( True )
        tree.set_vexpand( True )
        tree.append_column( Gtk.TreeViewColumn( "Virtual Machine", Gtk.CellRendererText(), text = 0 ) )
        tree.append_column( Gtk.TreeViewColumn( "Autostart", Gtk.CellRendererPixbuf(), stock_id = 1 ) )
        tree.append_column( Gtk.TreeViewColumn( "Start Command", Gtk.CellRendererText(), text = 2 ) )
        tree.set_tooltip_text( "Double click to edit a VM's properties." )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onVMDoubleClick )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( tree )
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )

        notebook.append_page( scrolledWindow, Gtk.Label( "Virtual Machines" ) )

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

        showAsSubmenusCheckbox = Gtk.CheckButton( "Show groups as submenus" )
        showAsSubmenusCheckbox.set_tooltip_text(
            "Groups can be shown with their VMs in submenus,\n" + \
            "or shown with their VMs as an indented list." )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )

        sortAlphabeticallyCheckbox = Gtk.CheckButton( "Sort VMs alphabetically" )
        sortAlphabeticallyCheckbox.set_tooltip_text( 
            "VMs can be sorted alphabetically or\n" + \
            "as set in the VirtualBox Manager." )
        sortAlphabeticallyCheckbox.set_active( not self.sortDefault )

        # Only show one of these, depending if groups are present or not...
        if self.groupsExist():
            grid.attach( showAsSubmenusCheckbox, 0, 0, 2, 1 )
        else:
            grid.attach( sortAlphabeticallyCheckbox, 0, 0, 2, 1 )

        label = Gtk.Label( "Refresh interval (minutes)" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        spinnerRefreshInterval = Gtk.SpinButton()
        spinnerRefreshInterval.set_adjustment( Gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerRefreshInterval.set_value( self.refreshIntervalInMinutes ) # ...so need to force the initial value by explicitly setting it.
        spinnerRefreshInterval.set_tooltip_text( "How often the list of VMs and\nrunning status is updated." )
        grid.attach( spinnerRefreshInterval, 1, 1, 1, 1 )

        label = Gtk.Label( "Startup delay (seconds)" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        spinnerDelay = Gtk.SpinButton()
        spinnerDelay.set_adjustment( Gtk.Adjustment( self.delayBetweenAutoStartInSeconds, 1, 60, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerDelay.set_value( self.delayBetweenAutoStartInSeconds ) # ...so need to force the initial value by explicitly setting it.
        spinnerDelay.set_tooltip_text( "Amount of time to wait from\nstarting one VM to the next." )
        grid.attach( spinnerDelay, 1, 2, 1, 1 )

        autostartIndicatorCheckbox = Gtk.CheckButton( "Autostart" )
        autostartIndicatorCheckbox.set_tooltip_text( "Run the indicator automatically." )
        autostartIndicatorCheckbox.set_active( os.path.exists( IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE ) )
        grid.attach( autostartIndicatorCheckbox, 0, 3, 2, 1 )

        notebook.append_page( grid, Gtk.Label( "General" ) )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
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

            self.updateVirtualMachinePreferences( store, tree.get_model().get_iter_first() )

            self.saveSettings()

            if not os.path.exists( IndicatorVirtualBox.AUTOSTART_PATH ): os.makedirs( IndicatorVirtualBox.AUTOSTART_PATH )

            if autostartIndicatorCheckbox.get_active():
                try: shutil.copy( IndicatorVirtualBox.DESKTOP_PATH + IndicatorVirtualBox.DESKTOP_FILE, IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE )
                except Exception as e: logging.exception( e )
            else:
                try: os.remove( IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE )
                except: pass

            self.onRefresh()

        self.dialog.destroy()
        self.dialog = None


    def updateVirtualMachinePreferences( self, store, treeiter ):
        while treeiter != None:
            if store[ treeiter ][ 3 ] != "": # UUID is not empty, so this is a VM and not a group...
                self.virtualMachinePreferences[ store[ treeiter ][ 3 ] ] = [ store[ treeiter ][ 1 ], store[ treeiter ][ 2 ] ]

            if store.iter_has_child( treeiter ):
                childiter = store.iter_children( treeiter )
                self.updateVirtualMachinePreferences( store, childiter )

            treeiter = store.iter_next( treeiter )


    def onVMDoubleClick( self, tree, rowNumber, treeViewColumn ):
        model, treeiter = tree.get_selection().get_selected()

        if treeiter == None: return

        if model[ treeiter ][ 3 ] == "": return # The 4th element is the UUID for a VM/group.  If the UUID is empty, this is a group.

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( "Start Command" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        startCommand = Gtk.Entry()
        startCommand.set_width_chars( 20 )
        if model[ treeiter ][ 2 ] is not None:
            startCommand.set_text( model[ treeiter ][ 2 ] )
            startCommand.set_width_chars( len( model[ treeiter ][ 2 ] ) * 5 / 4 ) # Sometimes the length is shorter than set due to packing, so make it longer.

        startCommand.set_tooltip_text( "The terminal command to start the VM such as\n\t'VBoxManage startvm %VM%' or\n\t'VBoxHeadless --startvm %VM% --vrde off'" )
        startCommand.set_hexpand( True ) # Only need to set this once and all objects will expand.
        grid.attach( startCommand, 1, 0, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_tooltip_text( "Run the VM when the indicator starts" )
        autostartCheckbox.set_active( model[ treeiter ][ 1 ] is not None and model[ treeiter ][ 1 ] == Gtk.STOCK_APPLY )
        grid.attach( autostartCheckbox, 0, 1, 2, 1 )

        # Would be nice to be able to bring this dialog to front (like the others)...but too much mucking around for little gain!
        dialog = Gtk.Dialog( "VM Properties", self.dialog, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorVirtualBox.ICON )

        while True:
            dialog.show_all()

            if dialog.run() != Gtk.ResponseType.OK: break

            if startCommand.get_text().strip() == "":
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, "The start command cannot be empty." )
                startCommand.grab_focus()
                continue

            if not "%VM%" in startCommand.get_text().strip():
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, "The start command must contain %VM% which is substituted for the VM name/id." )
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


    def onAbout( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.dialog = pythonutils.AboutDialog( 
               IndicatorVirtualBox.NAME,
               IndicatorVirtualBox.COMMENTS, 
               IndicatorVirtualBox.WEBSITE, 
               IndicatorVirtualBox.WEBSITE, 
               IndicatorVirtualBox.VERSION, 
               Gtk.License.GPL_3_0, 
               IndicatorVirtualBox.ICON,
               [ IndicatorVirtualBox.AUTHOR ],
               "",
               "",
               "/usr/share/doc/" + IndicatorVirtualBox.NAME + "/changelog.Debian.gz",
               logging )

        self.dialog.run()
        self.dialog.destroy()
        self.dialog = None


    def loadSettings( self ):
        self.delayBetweenAutoStartInSeconds = 30
        self.refreshIntervalInMinutes = 15
        self.showSubmenu = False
        self.sortDefault = True
        self.virtualMachinePreferences = { } # Store information about VMs, not groups. Key is VM UUID; value is [ autostart (bool), start command (str) ]

        if os.path.isfile( IndicatorVirtualBox.SETTINGS_FILE ):
            try:
                with open( IndicatorVirtualBox.SETTINGS_FILE, "r" ) as f: settings = json.load( f )

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

            with open( IndicatorVirtualBox.SETTINGS_FILE, "w" ) as f: f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorVirtualBox.SETTINGS_FILE )


if __name__ == "__main__": IndicatorVirtualBox().main()