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

#TODO Can these be ditched?
#         self.isRunning = False
#         self.autoStart = False
#         self.startCommand = "VBoxManage startvm %VM%"




INDICATOR_NAME = "indicator-virtual-box"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import AppIndicator3, GLib, Gtk

import gzip, json, locale, logging, os, pythonutils, re, shutil, sys, time, virtualmachine


class IndicatorVirtualBox:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.38"
    ICON = INDICATOR_NAME
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = INDICATOR_NAME + ".desktop"

    VIRTUAL_BOX_CONFIGURATION_4_DOT_3_OR_GREATER = os.getenv( "HOME" ) + "/.config/VirtualBox/VirtualBox.xml"
    VIRTUAL_BOX_CONFIGURATION_PRIOR_4_DOT_3 = os.getenv( "HOME" ) + "/.VirtualBox/VirtualBox.xml"
    VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION = "4.3" # Configuration file location and format changed at this version (https://www.virtualbox.org/manual/ch10.html#idp99351072).

    VIRTUAL_MACHINE_STARTUP_DELAY_IN_SECONDS = 5

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
        self.loadSettings()
        self.dialog = None

        virtualMachineInfos = self.getVirtualMachines()
        # Start up VMs...
#TODO Maybe do this in a separate thread?  Might need to block the preferences until it's finished.
#Rather than lockout, maybe rebuild the menu with a flag to enable the prefernces menu item?  Or just enable the preferences item?
        previousVMNeededStarting = False
        for virtualMachineInfo in virtualMachineInfos:
            if self.isVirtualMachineAutostart( virtualMachineInfo.getUUID() ):
                if previousVMNeededStarting and not virtualMachineInfo.isRunning:
                    time.sleep( self.delayBetweenAutoStartInSeconds )

                previousVMNeededStarting = not virtualMachineInfo.isRunning

                # Create a dummy widget (radio button) and use that to kick off the start VM function...
                radioButton = Gtk.RadioButton.new_with_label_from_widget( None, "" )                    
                radioButton.props.name = virtualMachineInfo.getUUID()
                self.onStartVirtualMachine( radioButton, False )

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorVirtualBox.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling!
        self.buildMenu( virtualMachineInfos )
        self.timeoutID = GLib.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.onRefresh )

#         menu = self.indicator.get_menu()
#         for menuItem in menu.get_children():
#             if menuItem.__class__.__name__ == "ImageMenuItem" and menuItem.get_label() == "gtk-preferences":
#                 menuItem.set_sensitive( False )


    def main( self ): Gtk.main()


    def buildMenu( self, virtualMachineInfos ):
        menu = Gtk.Menu()
        if self.isVirtualBoxInstalled():
            if len( virtualMachineInfos ) == 0:
                menu.append( Gtk.MenuItem( _( "(no virtual machines exist)" ) ) ) #TODO Test...
            else:
                if self.showSubmenu == True:
                    stack = [ ]
                    currentMenu = menu
                    for i in range( len( virtualMachineInfos ) ):
                        virtualMachineInfo = virtualMachineInfos[ i ]
                        while virtualMachineInfo.getIndent() < len( stack ):
                            currentMenu = stack.pop()

                        if virtualMachineInfo.isGroup():
                            menuItem = Gtk.MenuItem( virtualMachineInfo.getName()[ virtualMachineInfo.getName().rfind( "/" ) + 1 : ] )
                            currentMenu.append( menuItem )
                            subMenu = Gtk.Menu()
                            menuItem.set_submenu( subMenu )
                            stack.append( currentMenu )
                            currentMenu = subMenu
                        else:
                            currentMenu.append( self.createMenuItemForVM( virtualMachineInfo, "" ) )
                else:
                    for virtualMachineInfo in virtualMachineInfos:
                        indent = "    " * virtualMachineInfo.getIndent()
                        if virtualMachineInfo.isGroup():
                            menu.append( Gtk.MenuItem( indent + virtualMachineInfo.getName()[ virtualMachineInfo.getName().rfind( "/" ) + 1 : ] ) )
                        else:
                            menu.append( self.createMenuItemForVM( virtualMachineInfo, indent ) )

            menu.append( Gtk.SeparatorMenuItem() )
            menuItem = Gtk.MenuItem( _( "Launch VirtualBox Manager" ) )
            menuItem.connect( "activate", self.onLaunchVirtualBox )
            menu.append( menuItem )
            
        else:
            menu.insert( Gtk.MenuItem( _( "(VirtualBox is not installed)" ) ), 0 )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, False, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def createMenuItemForVM( self, virtualMachineInfo, indent ):
        if virtualMachineInfo.isRunning: # No need to check if this is a group...groups never "run" and this function should only be called for a VM and never a group.
            menuItem = Gtk.RadioMenuItem.new_with_label( [], indent + virtualMachineInfo.getName() )
            menuItem.set_active( True )
        else:
            menuItem = Gtk.MenuItem( indent + virtualMachineInfo.getName() )

        menuItem.props.name = virtualMachineInfo.getUUID()
        menuItem.connect( "activate", self.onStartVirtualMachine, True )
        return menuItem


    def isVirtualBoxInstalled( self ): return pythonutils.callProcess( "which VBoxManage" ).communicate()[ 0 ].decode() != ''


    def getVirtualBoxVersion( self ): return pythonutils.callProcess( "VBoxManage --version" ).communicate()[ 0 ].decode().strip()


    def getVirtualMachines( self ):
        virtualMachineInfos = [ ]
        if self.isVirtualBoxInstalled():
            virtualMachineInfosFromVBoxManage = self.getVirtualMachinesFromVBoxManage() # Does not contain group information, nor sort order.
            print( virtualMachineInfosFromVBoxManage )
            if len( virtualMachineInfosFromVBoxManage ) > 0:
                if self.getVirtualBoxVersion() < IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_CHANGEOVER_VERSION: #TODO Test this works with different versions.
                    print( "Get config for version less than 4.3" )
                    virtualMachineInfosFromConfig = self.getVirtualMachinesFromConfigPrior4dot3()
                else:
                    print( "Get config for version 4.3+" )
                    virtualMachineInfosFromConfig = self.getVirtualMachinesFromConfig4dot3()

                print( virtualMachineInfosFromConfig )

                # Going forward, the virtual machine infos from the config is the definitive list of VMs (and groups if any).
                virtualMachineInfos = virtualMachineInfosFromConfig

                # The virtual machine infos from the config do not contain the names of virtual machines.
                # Obtain the names from the virtual machine infos from VBoxManage.
                for virtualmachineInfoFromVBoxManage in virtualMachineInfosFromVBoxManage:
                    for virtualMachineInfo in virtualMachineInfos:
                        if virtualmachineInfoFromVBoxManage.getUUID() == virtualMachineInfo.getUUID():
                            virtualMachineInfo.setName( virtualmachineInfoFromVBoxManage.getName() )
                            break

                print( virtualMachineInfos )

                # Determine which VMs are running.
                p = pythonutils.callProcess( "VBoxManage list runningvms" )
                for line in p.stdout.readlines():
                    try:
                        info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
                        for virtualMachineInfo in virtualMachineInfos:
                            if virtualMachineInfo.getUUID() == info[ 1 ]:
                                virtualMachineInfo.setRunning()
                    except:
                        pass # Sometimes VBoxManage emits a warning message along with the VM information.

                p.wait()

#TODO Should this be done in the prefs/menu instead?  If not, where else...not in multiple places!
                # Alphabetically sort...
                if self.sortDefault == False and not self.groupsExist( virtualMachineInfos ):
                    virtualMachineInfos = sorted( virtualMachineInfos, key = lambda virtualMachineInfo: virtualMachineInfo.name )

        return virtualMachineInfos


    # The returned list of virtualmachine.Info objects does not include any groups (if present) nor any order set by the user in the GUI.
    def getVirtualMachinesFromVBoxManage( self ):
        p = pythonutils.callProcess( "VBoxManage list vms" )
        virtualMachineInfos = []
        for line in p.stdout.readlines():
            try:
                info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
                virtualMachineInfo = virtualmachine.Info( info[ 0 ], False, info[ 1 ], 0 )
                virtualMachineInfos.append( virtualMachineInfo )
            except:
                pass # Sometimes VBoxManage emits a warning message along with the VM information.

        p.wait()
        return virtualMachineInfos


    def getVirtualMachinesFromConfigPrior4dot3( self ):
        virtualMachineInfos = []
        p = pythonutils.callProcess( "grep GUI/SelectorVMPositions " + IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION_PRIOR_4_DOT_3 )
        try:
            uuids = list( p.communicate()[ 0 ].decode().rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )
            for uuid in uuids:
                virtualMachineInfos.append( virtualmachine.Info( "", False, uuid, 0 ) )                
        except:
#TODO Should something be logged?
            virtualMachineInfos = [] # The VM order has never been altered giving an empty result (and exception).

        return virtualMachineInfos


    def getVirtualMachinesFromConfig4dot3( self ):
        virtualMachineInfos = []
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
                    virtualMachineInfos.insert( i, virtualmachine.Info( key + value.replace( "go=", "" ), True, "", 0 ) )
                else:
                    virtualMachineInfos.insert( i, virtualmachine.Info( "", False, value.replace( "m=", "" ), 0 ) )

                i += 1

            # Now have a list of virtual machine infos containing top level groups and/or VMs.
            # Process this list and where a group is found, add in its children (groups and/or VMs).
            i = 0
            while i < len( virtualMachineInfos ):
                if virtualMachineInfos[ i ].isGroup():
                    indent = virtualMachineInfos[ i ].getIndent() + 1
                    key = virtualMachineInfos[ i ].getName()
                    values = groupDefinitions[ key ].split( "," )
                    j = i + 1
                    for value in values:
                        if value.startswith( "go=" ):
                            virtualMachineInfos.insert( j, virtualmachine.Info( key + "/" + value.replace( "go=", "" ), True, "", indent ) )
                        else:
                            virtualMachineInfos.insert( j, virtualmachine.Info( "", False, value.replace( "m=", "" ), indent ) )

                        j += 1

                i += 1

        except Exception as e:
#TODO Should something be logged?
            virtualMachineInfos = []

        return virtualMachineInfos


    def groupsExist( self, virtualMachineInfos ):
        for virtualMachineInfo in virtualMachineInfos:
            if virtualMachineInfo.isGroup():
                return True

        return False


    def onRefresh( self ):
        GLib.idle_add( self.buildMenu, self.getVirtualMachines() )
        return True # Must return true so that we continue to be called (http://www.pygtk.org/pygtk2reference/gobject-functions.html#function-gi--timeout-add).


    def onLaunchVirtualBox( self, widget ):
        p = pythonutils.callProcess( 'wmctrl -l | grep "Oracle VM VirtualBox Manager"' ) #TODO Check this works in Russian!
        result = p.communicate()[ 0 ].decode()
        p.wait()
        if result == "":
            pythonutils.callProcess( "VirtualBox &" )
        else:
            windowID = result[ 0 : result.find( " " ) ]
            pythonutils.callProcess( "wmctrl -i -a " + windowID ).wait()


    def onStartVirtualMachine( self, widget, doRefresh ):
#TODO Isn't it too late at this point to do a refresh???        
        if doRefresh:
            self.getVirtualMachines() # Refresh the VMs as the list could have changed (deletion, creation, rename) since the last refresh.

        virtualMachineUUID = widget.props.name
        virtualMachineInfo = self.getVirtualMachineInfo( virtualMachineUUID )
        virtualMachineName = virtualMachineInfo.getName()
        if virtualMachineName is None:
            pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "The VM could not be found - either it has been renamed or deleted.  The list of VMs has been refreshed - please try again." ) )
        elif virtualMachineInfo.isRunning:
            if self.duplicateVirtualMachineNameExists( virtualMachineName ):
                pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "There is more than one VM with the same name - unfortunately your VM cannot be uniquely identified." ) )
            else:
                windowID = None
                p = pythonutils.callProcess( "wmctrl -l" )
                for line in p.stdout.readlines():
                    lineAsString = str( line.decode() )
                    if virtualMachineName in lineAsString:
                        windowID = lineAsString[ 0 : lineAsString.find( " " ) ]

                p.wait()

                if windowID is None:
                    pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "The VM is running but its window could not be found - perhaps it is running headless." ) )
                else:
                    # If the VM is running headless then there will be no window to display...
                    pythonutils.callProcess( "wmctrl -i -a " + windowID ).wait()
        else:
            try:
                startCommand = virtualMachineInfo.getStartCommand().replace( "%VM%", virtualMachineInfo.getUUID() ) + " &"
                pythonutils.callProcess( startCommand ).wait()

                # Since the start command returns immediately, the running status (from VBoxManage) may not be updated as yet.
                # Pause after kicking off the VM to give VBoxManage a chance to catch up...
                # ...then when the indicator is updated, we (hopefully) will be updated correctly!
                time.sleep( IndicatorVirtualBox.VIRTUAL_MACHINE_STARTUP_DELAY_IN_SECONDS )

            except Exception as e:
                logging.exception( e )
                pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "The VM '{0}' could not be started - check the log file: {1}" ).format( virtualMachineInfo.getName(), IndicatorVirtualBox.LOG ) )

        if doRefresh:
            self.onRefresh()


    def isVirtualMachineAutostart( self, uuid ): return uuid in self.virtualMachinePreferences and self.virtualMachinePreferences[ uuid ][ 0 ] == Gtk.STOCK_APPLY


    def getVirtualMachineInfo( self, uuid ):
        for virtualMachineInfo in self.virtualMachineInfos:
            if virtualMachineInfo.getUUID() == uuid:
                return virtualMachineInfo

        return None


#TODO Search for
# self.virtualMachineInfos
# and remove!



#TODO Is this needed?
    def duplicateVirtualMachineNameExists( self, virtualMachineName ):
        count = 0
        for virtualMachineInfo in self.virtualMachineInfos:
            if virtualMachineInfo.getName() == virtualMachineName:
                count += 1

        return count > 1


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
        virtualMachineInfos = self.getVirtualMachines()
        for virtualMachineInfo in virtualMachineInfos:
            while virtualMachineInfo.getIndent() < len( stack ):
                parent = stack.pop()

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
        tree.append_column( Gtk.TreeViewColumn( _( "Virtual Machine" ), Gtk.CellRendererText(), text = 0 ) )
        tree.append_column( Gtk.TreeViewColumn( _( "Autostart" ), Gtk.CellRendererPixbuf(), stock_id = 1 ) )
        tree.append_column( Gtk.TreeViewColumn( _( "Start Command" ), Gtk.CellRendererText(), text = 2 ) )
        tree.set_tooltip_text( _( "Double click to edit a VM's properties." ) )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onVMDoubleClick )

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

        # Only show one of these, depending if groups are present or not...
        if self.groupsExist( virtualMachineInfos ):
            grid.attach( showAsSubmenusCheckbox, 0, 0, 2, 1 )
        else:
            grid.attach( sortAlphabeticallyCheckbox, 0, 0, 2, 1 )

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

        autostartIndicatorCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartIndicatorCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartIndicatorCheckbox.set_active( os.path.exists( IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE ) )
        grid.attach( autostartIndicatorCheckbox, 0, 3, 2, 1 )

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

            self.updateVirtualMachinePreferences( store, tree.get_model().get_iter_first() )

            self.saveSettings()

            if not os.path.exists( IndicatorVirtualBox.AUTOSTART_PATH ):
                os.makedirs( IndicatorVirtualBox.AUTOSTART_PATH )

            if autostartIndicatorCheckbox.get_active():
                try:
                    shutil.copy( IndicatorVirtualBox.DESKTOP_PATH + IndicatorVirtualBox.DESKTOP_FILE, IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE )
                except Exception as e:
                    logging.exception( e )
            else:
                try:
                    os.remove( IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE )
                except:
                    pass

            self.onRefresh()

        self.dialog.destroy()
        self.dialog = None


    def updateVirtualMachinePreferences( self, store, treeiter ):
        while treeiter is not None:
            if store[ treeiter ][ 3 ] != "": # UUID is not empty, so this is a VM and not a group...
                self.virtualMachinePreferences[ store[ treeiter ][ 3 ] ] = [ store[ treeiter ][ 1 ], store[ treeiter ][ 2 ] ]

            if store.iter_has_child( treeiter ):
                childiter = store.iter_children( treeiter )
                self.updateVirtualMachinePreferences( store, childiter )

            treeiter = store.iter_next( treeiter )


    def onVMDoubleClick( self, tree, rowNumber, treeViewColumn ):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter is not None and model[ treeiter ][ 3 ] != "":
            self.editVM( model, treeiter )


    def editVM( self, model, treeiter ):
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
            startCommand.set_width_chars( len( model[ treeiter ][ 2 ] ) * 5 / 4 ) # Sometimes the length is shorter than set due to packing, so make it longer.

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
        self.virtualMachinePreferences = { } # Store information about VMs, not groups. Key is VM UUID; value is [ autostart (bool), start command (str) ]

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