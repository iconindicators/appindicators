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


# Application indicator to start (and show running) VirtualBox virtual machines.


# On Lubuntu 12.10 the following message appears when the indicator is executed:
#   ERROR:root:Could not find any typelib for AppIndicator3
# From https://kororaa.org/forums/viewtopic.php?f=7&t=220#p2343, it (hopefully) is safe to ignore.


# Have noticed that if a VM exists in a group there is another VM of the same name but not in a group
# and the group is then ungrouped, the VirtualBox UI doesn't handle it well...
# ...the UI keeps the group and the VM within it (but removes all unique VMs from the group).
# The VirtualBox.xml file does seem to reflect the change and so the indicator obeys this file.

#TODO
#Create a bunch of VMs in 4.2
#Create a VM and add to a group.
#Create a VM with the same name as the VM in the group.
#The new VM does not appear in the list.
#...after this test, ungroup and see what happens to the two same named vms.

#Test with no groups and create two VMs with same name.




#I've noticed a bug myself and not sure if it's related to what you've observed.  
#I'm finding that in 4.2 if I create a bunch of VMs, 
#then create a VM and add to a group and then create a VM of the same name as that VM in the group, 
#the last created VM does not appear.  
#I thought I had managed to handle duplicate VM names...oh well.
#
#As for the things you've mentioned...
#
#I'm looking to see if I can reproduce...there are a lot of combinations (groups, no groups), 
#not to mention 4.1 versus 4.2.  
#What version of VB are you using?
#
#In terms of when alpha sort should apply: If there are no groups present (regardless of 4.1/4.2), 
#then alpha sort makes sense.  
#So yes, grey out the alpha sort option when groups are detected.
#
#If groups are present, then the user can have a flat view or a submenu view.  
#In the flat view, I like the idea of [ ] around a group name - great idea!  
#Also, nice catch on not showing the before/after text on group names.  
#Not sure yet this happens only in the flat view or in the submenu view too but will investigate.  
#I guess if groups are not present I could grey out the option to show in submenus too - make sense?
#
#I had tooltips on the alpha sort and submenu checkboxes to explain what happens...hoped it would do the trick!


#> I have just read your first comment on Sort alphabetically, perhaps
#> gray out the option "Sort VM alphabetically" if groups are present so
#> it can't be clicked.

#> > 1) The option Sort VM alphabetically doesn't seem to work anymore.

#> > 2) Perhaps make the group name enclosed in square brackets [Group] in
#> > flat menu to set it more apart from VMs, and text before/after not
#> > running should not apply for these entries.


#I've attached the latest.  
#The group name now has [ ] either side of the name in the flat view.  
#I've also removed the before/after text from the group name too.
#
#But...I'm now thinking to remove the before/after text completely.
#
#Originally when I created the indicator I didn't think to use a radio button.  
#So I decided to just put in <<< >>> either side of the VM name.  
#Later I realised I could use the radio button but noticed on Lubuntu the radio button looked terrible
#and so I decided to keep the text option too...someone out there might be using it.
#
#But now testing on Lubuntu 12.10 the radio button doesn't look to bad...maybe it's because it's all now Python3/PyGobject.
#
#So I'm thinking to remove the text option ... agree?
#
#If that's the case, I might consider making the group name [ ] thing optional too.
#Maybe another option is only show in flat view?



appindicatorImported = True
try:
    from gi.repository import AppIndicator3 as appindicator
except:
    appindicatorImported = False

from gi.repository import GObject as gobject
from gi.repository import Gtk

import json
import locale
import logging
import os
import shutil
import subprocess
import sys


class IndicatorVirtualBox:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-virtual-box"
    VERSION = "1.0.15"
    ICON = NAME
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"
    VIRTUAL_BOX_CONFIGURATION = os.getenv( "HOME" ) + "/.VirtualBox/VirtualBox.xml"
    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_RUNNING_BEFORE = "menuTextVirtualMachineRunningBefore"
    SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_RUNNING_AFTER = "menuTextVirtualMachineRunningAfter"
    SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_NOT_RUNNING_BEFORE = "menuTextVirtualMachineNotRunningBefore"
    SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_NOT_RUNNING_AFTER = "menuTextVirtualMachineNotRunningAfter"
    SETTINGS_REFRESH_INTERVAL_IN_MINUTES = "refreshIntervalInMinutes"
    SETTINGS_SHOW_SUBMENU = "showSubmenu"
    SETTINGS_SORT_DEFAULT = "sortDefault"
    SETTINGS_USE_RADIO_INDICATOR = "useRadioIndicator"


    def __init__( self ):
        logging.basicConfig( file = sys.stderr, level = logging.INFO )
        self.loadSettings()
        self.dialog = None

        # One of the install dependencies for Debian/Ubuntu is that appindicator exists.
        # However the appindicator only works under Ubuntu Unity - we need to default to GTK icon if not running Unity (say Lubuntu).
        global appindicatorImported
        unityIsInstalled = os.getenv( "XDG_CURRENT_DESKTOP" )
        if unityIsInstalled is None:
            appindicatorImported = False
        elif str( unityIsInstalled ).lower() != "Unity".lower():
            appindicatorImported = False

        # Create the status icon...either Unity or GTK.
        if appindicatorImported == True:
            self.indicator = appindicator.Indicator.new( IndicatorVirtualBox.NAME, IndicatorVirtualBox.ICON, appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling...
            self.buildMenu()
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
        else:
            self.menu = Gtk.Menu() # Set an empty menu to get things rolling...
            self.buildMenu()
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorVirtualBox.ICON )
            self.statusicon.set_tooltip_text( "Virtual Machines" )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.timeoutID = gobject.timeout_add( 1000 * 60 * self.refreshIntervalInMinutes, self.onRefresh )
        Gtk.main()


    def buildMenu( self ):
        if appindicatorImported == True:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if we don't do this we get GTK complaints).

        # Create the new menu and populate...
        menu = Gtk.Menu()
        if self.isVirtualBoxInstalled():
            self.getVirtualMachines()
            if len( self.virtualMachineInfos ) == 0 :
                menu.append( Gtk.MenuItem( "(no virtual machines exist)" ) )
            else:
                if self.showSubmenu == True:
                    stack = []
                    currentMenu = menu
                    for i in range( len( self.virtualMachineInfos ) ):
                        virtualMachineInfo = self.virtualMachineInfos[ i ]
                        if virtualMachineInfo.getIndent() < len( stack ):
                            currentMenu = stack.pop() # We previously added a VM in a group and now we are adding a VM at the same indent as the group.

                        if virtualMachineInfo.isGroup:
                            menuItem = Gtk.MenuItem( virtualMachineInfo.getName() )

                            currentMenu.append( menuItem )
                            subMenu = Gtk.Menu()
                            menuItem.set_submenu( subMenu )
                            stack.append( currentMenu ) # Whatever we create next is a child of this group, so save the current menu.
                            currentMenu = subMenu
                        else:
                            if virtualMachineInfo.isRunning:
                                if self.useRadioIndicator == True:
                                    menuItem = Gtk.RadioMenuItem.new_with_label( [], self.menuTextVirtualMachineRunningBefore + virtualMachineInfo.getName() + self.menuTextVirtualMachineRunningAfter )
                                    menuItem.set_active( True )
                                else:
                                    menuItem = Gtk.MenuItem( self.menuTextVirtualMachineRunningBefore + virtualMachineInfo.getName() + self.menuTextVirtualMachineRunningAfter )
                            else:
                                menuItem = Gtk.MenuItem( self.menuTextVirtualMachineNotRunningBefore + virtualMachineInfo.getName() + self.menuTextVirtualMachineNotRunningAfter )
        
                            menuItem.props.name = virtualMachineInfo.getUUID()
                            menuItem.connect( "activate", self.onStartVirtualMachine )
                            currentMenu.append( menuItem )
                else:
                    for virtualMachineInfo in self.virtualMachineInfos:
                        indent = "    " * virtualMachineInfo.getIndent()
                        if virtualMachineInfo.isRunning:
                            if self.useRadioIndicator == True:
                                vmMenuItem = Gtk.RadioMenuItem.new_with_label( [], self.menuTextVirtualMachineRunningBefore + indent + virtualMachineInfo.getName() + self.menuTextVirtualMachineRunningAfter )
                                vmMenuItem.set_active( True )
                            else:
                                vmMenuItem = Gtk.MenuItem( self.menuTextVirtualMachineRunningBefore + indent + virtualMachineInfo.getName() + self.menuTextVirtualMachineRunningAfter )
                        else:
                            if virtualMachineInfo.isGroup:
                                vmMenuItem = Gtk.MenuItem( indent + "[ " + virtualMachineInfo.getName() + " ]" )
                            else:
                                vmMenuItem = Gtk.MenuItem( self.menuTextVirtualMachineNotRunningBefore + indent + virtualMachineInfo.getName() + self.menuTextVirtualMachineNotRunningAfter )
    
                        if not virtualMachineInfo.isGroup:
                            vmMenuItem.props.name = virtualMachineInfo.getUUID()
                            vmMenuItem.connect( "activate", self.onStartVirtualMachine )
    
                        menu.append( vmMenuItem )

            menu.append( Gtk.SeparatorMenuItem() )

            self.virtualBoxMenuItem = Gtk.MenuItem( "Launch VirtualBox" )
            self.virtualBoxMenuItem.connect( "activate", self.onLaunchVirtualBox )
            menu.append( self.virtualBoxMenuItem )
        else:
            menu.insert( Gtk.MenuItem( "(VirtualBox is not installed)" ), 0 )
            menu.append( Gtk.SeparatorMenuItem() )

        preferencesMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        menu.append( preferencesMenuItem )

        aboutMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        aboutMenuItem.connect( "activate", self.onAbout )
        menu.append( aboutMenuItem )

        quitMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        quitMenuItem.connect( "activate", Gtk.main_quit )
        menu.append( quitMenuItem )

        if appindicatorImported == True:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu

        menu.show_all()


    def isVirtualBoxInstalled( self ):
        p = subprocess.Popen( "which VBoxManage", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        return p.communicate()[ 0 ].decode() != ''


    def getVirtualMachines( self ):
        self.virtualMachineInfos = [] # A list of VirtualBox items.

        if not self.isVirtualBoxInstalled():
            return

        self.virtualMachineInfos = self.getVirtualMachinesFromBackend()
        if len( self.virtualMachineInfos ) == 0:
            return

        # We have a list of VMs and UUIDs...now determine if we have groups or the sort order has been changed...
        if os.path.exists( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION ):
            # Attempt to get the groups and UUIDs...
            grepString = "GUI/GroupDefinitions/"
            virtualMachineInfos = self.getVirtualMachinesFromConfigWithGroups( grepString, 0 )
            if len( virtualMachineInfos ) > 0:
                # There are VMs present but need to double check the count matches that from the backend.
                # I've observed...
                #
                #    If a VM is added to a group and the group then removed/ungrouped, the GUI/GroupDefinition remains, listing that VM.
                #    If another VM is created, the GUI/GroupDefinitions still only lists the original/first VM...giving an incorrect reading.
                #
                #    If a VM is created and added to a group and a VM is later created of the same name but not in a group
                #    then new VM is not listed (and neither are subsequent VMs).
                #
                # So take what information the groups gave and then append to that the VMs which are missing (from the backend information).
                for virtualMachineInfoFromBackEnd in self.virtualMachineInfos:
                    found = False
                    for virtualMachineInfo in virtualMachineInfos:
                        if virtualMachineInfoFromBackEnd.getUUID() == virtualMachineInfo.getUUID():
                            found = True
                            break

                    if found == False:
                        virtualMachineInfos.append( virtualMachineInfoFromBackEnd )
            else:
                # There was no group data, so attempt to get UI sort order...
                virtualMachineInfos = self.getVirtualMachinesFromConfigWithoutGroups()

            # We now have a list of group names and VM UUIDs OR a list of VM UUIDs...
            # However the VM names are not present.
            # Get the VM names from the list from the backend...
            for virtualMachineInfoFromBackEnd in self.virtualMachineInfos:
                for virtualMachineInfo in virtualMachineInfos:
                    if virtualMachineInfoFromBackEnd.getUUID() == virtualMachineInfo.getUUID():
                        virtualMachineInfo.setName( virtualMachineInfoFromBackEnd.getName() )
                        break

            self.virtualMachineInfos = virtualMachineInfos

        # Determine which VMs are running...
        p = subprocess.Popen( "VBoxManage list runningvms", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        for line in p.stdout.readlines():
            info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
            for virtualMachineInfo in self.virtualMachineInfos:
                if virtualMachineInfo.getUUID() == info[ 1 ]:
                    virtualMachineInfo.setRunning()

        p.wait()

        # Alphabetically sort...
        if self.sortDefault == False and not self.groupsExist():
            self.virtualMachineInfos = sorted( self.virtualMachineInfos, key = lambda virtualMachineInfo: virtualMachineInfo.name )


    def groupsExist( self ):
        for virtualMachineInfo in self.virtualMachineInfos:
            if virtualMachineInfo.isGroup:
                return True

        return False


    def getVirtualMachinesFromBackend( self ):
        p = subprocess.Popen( "VBoxManage list vms", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        virtualMachineInfos = []
        for line in p.stdout.readlines():
            info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
            virtualMachineInfo = VirtualMachineInfo( info[ 0 ], False, info[ 1 ], 0 )
            virtualMachineInfos.append( virtualMachineInfo )

        p.wait()
        return virtualMachineInfos


    # Gets a list of VMs.
    def getVirtualMachinesFromConfigWithoutGroups( self ):
        virtualMachineInfos = []
        p = subprocess.Popen( "grep GUI/SelectorVMPositions " + IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        try:
            uuids = list( p.communicate()[ 0 ].decode().rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )
            for uuid in uuids:
                virtualMachineInfos = VirtualMachineInfo( "", False, uuid, 0 )
                virtualMachineInfos.append( virtualMachineInfos )                
        except: # The VM order has never been altered giving an empty result (and exception).
            virtualMachineInfos = []

        return virtualMachineInfos


    # Gets a list of groups/VMs...the VM names are empty and need to be filled in by the caller.
    def getVirtualMachinesFromConfigWithGroups( self, grepString, indentAmount ):
        virtualMachineInfos = []
        p = subprocess.Popen( "grep \"" + grepString + "\\\"\" " + IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        try:
            items = list( p.communicate()[ 0 ].decode().rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )
            for item in items:
                itemName = str( item ).split( "=" )[ 1 ] 
                if str( item ).startswith( "go" ) or str( item ).startswith( "gc" ):
                    virtualMachineInfo = VirtualMachineInfo( itemName, True, "", indentAmount ) # For a group there is no UUID.
                    virtualMachineInfos.append( virtualMachineInfo )
                    if grepString.endswith( "/" ):
                        virtualMachineInfos += self.getVirtualMachinesFromConfigWithGroups( grepString + itemName, indentAmount + 1 )
                    else:
                        virtualMachineInfos += self.getVirtualMachinesFromConfigWithGroups( grepString + "/" + itemName, indentAmount + 1 )
                else:
                    virtualMachineInfo = VirtualMachineInfo( "", False, itemName, indentAmount ) # This is a VM: we have it's UUID but not its name...so the caller needs to add it in.
                    virtualMachineInfos.append( virtualMachineInfo )
        except:
            virtualMachineInfos = []

        return virtualMachineInfos


    def onRefresh( self ):
        gobject.idle_add( self.buildMenu )
        return True # Must return true so that we continue to be called (http://www.pygtk.org/pygtk2reference/gobject-functions.html#function-gi--timeout-add).


    def onLaunchVirtualBox( self, widget ):
        subprocess.Popen( "VirtualBox &", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )


    def onStartVirtualMachine( self, widget ):
        self.getVirtualMachines() # Refresh the VMs as the list could have changed (deletion, creation, rename) since the last refresh.

        virtualMachineUUID = widget.props.name
        virtualMachineInfo = self.getVirtualMachineInfo( virtualMachineUUID )
        virtualMachineName = virtualMachineInfo.getName()
        if virtualMachineName is None:
            self.showMessage( Gtk.MessageType.ERROR, "The VM could not be found - either it has been renamed or deleted.  The list of VMs has been refreshed - please try again." )
        elif virtualMachineInfo.isRunning:
            if self.duplicateVirtualMachineNameExists( virtualMachineName ):
                self.showMessage( Gtk.MessageType.ERROR, "There is more than one VM with the same name - unfortunately your VM cannot be uniquely identified." )
            else:
                windowID = None
                p = subprocess.Popen( "wmctrl -l", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
                for line in p.stdout.readlines():
                    lineAsString = str( line.decode() )
                    if virtualMachineName in lineAsString:
                        windowID = lineAsString[ 0 : lineAsString.find( " " ) ]

                p.wait()

                if windowID is not None:
                    p = subprocess.Popen( "wmctrl -i -a " + windowID, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
                    p.wait()
        else:
            command = "VBoxManage startvm " + virtualMachineUUID
            p = subprocess.Popen( command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
            p.wait()

        self.onRefresh()


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


    def showMessage( self, messageType, message ):
        dialog = Gtk.MessageDialog( None, 0, messageType, Gtk.ButtonsType.OK, message )
        dialog.run()
        dialog.destroy()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            return

        notebook = Gtk.Notebook()

        # First tab - display settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( "VM running:" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 2, 1 )

        label = Gtk.Label( "  Text before" )
        label.set_halign( Gtk.Align.START )
        label.set_margin_left( 15 )
        grid.attach( label, 0, 1, 1, 1 )

        textRunningBefore = Gtk.Entry()
        textRunningBefore.set_text( self.menuTextVirtualMachineRunningBefore )
        textRunningBefore.set_hexpand( True )
        grid.attach( textRunningBefore, 1, 1, 1, 1 )

        label = Gtk.Label( "  Text after" )
        label.set_halign( Gtk.Align.START )
        label.set_margin_left( 15 )
        grid.attach( label, 0, 2, 1, 1 )

        textRunningAfter = Gtk.Entry()
        textRunningAfter.set_text( self.menuTextVirtualMachineRunningAfter )
        grid.attach( textRunningAfter, 1, 2, 1, 1 )

        label = Gtk.Label( "VM not running:" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 2, 1 )

        label = Gtk.Label( "  Text before" )
        label.set_halign( Gtk.Align.START )
        label.set_margin_left( 15 )
        grid.attach( label, 0, 4, 1, 1 )

        textNotRunningBefore = Gtk.Entry()
        textNotRunningBefore.set_text( self.menuTextVirtualMachineNotRunningBefore )
        grid.attach( textNotRunningBefore, 1, 4, 1, 1 )

        label = Gtk.Label( "  Text after" )
        label.set_halign( Gtk.Align.START )
        label.set_margin_left( 15 )
        grid.attach( label, 0, 5, 1, 1 )

        textNotRunningAfter = Gtk.Entry()
        textNotRunningAfter.set_text( self.menuTextVirtualMachineNotRunningAfter )
        grid.attach( textNotRunningAfter, 1, 5, 1, 1 )

        useRadioCheckbox = Gtk.CheckButton( "Use a \"radio button\" to indicate a running VM" )
        useRadioCheckbox.set_active( self.useRadioIndicator )
        grid.attach( useRadioCheckbox, 0, 6, 2, 1 )

        showAsSubmenusCheckbox = Gtk.CheckButton( "Show groups as submenus" )
        showAsSubmenusCheckbox.set_tooltip_text( "Unchecked will show groups using indents - ignored if groups are not present" )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )
        grid.attach( showAsSubmenusCheckbox, 0, 7, 2, 1 )

        sortAlphabeticallyCheckbox = Gtk.CheckButton( "Sort VMs alphabetically" )
        sortAlphabeticallyCheckbox.set_tooltip_text( "Unchecked will sort as per VirtualBox UI - ignored if groups are present" )
        sortAlphabeticallyCheckbox.set_active( not self.sortDefault )
        grid.attach( sortAlphabeticallyCheckbox, 0, 8, 2, 1 )

        notebook.append_page( grid, Gtk.Label( "Display" ) )

        # Second tab - general settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( "Refresh interval (minutes)" )
        grid.attach( label, 0, 0, 1, 1 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60, 1, 5, 0 ) )
        spinner.set_tooltip_text( "How often the list of VMs and their running status is automatically updated" )
        spinner.set_hexpand( True )
        grid.attach( spinner, 1, 0, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 1, 2, 1 )

        notebook.append_page( grid, Gtk.Label( "General" ) )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.menuTextVirtualMachineRunningBefore = textRunningBefore.get_text()
            self.menuTextVirtualMachineRunningAfter = textRunningAfter.get_text()
            self.menuTextVirtualMachineNotRunningBefore = textNotRunningBefore.get_text()
            self.menuTextVirtualMachineNotRunningAfter = textNotRunningAfter.get_text()
            self.useRadioIndicator = useRadioCheckbox.get_active()
            self.showSubmenu = showAsSubmenusCheckbox.get_active()
            self.sortDefault = not sortAlphabeticallyCheckbox.get_active()

            self.refreshIntervalInMinutes = spinner.get_value_as_int()
            gobject.source_remove( self.timeoutID )
            self.timeoutID = gobject.timeout_add( 1000 * 60 * self.refreshIntervalInMinutes, self.onRefresh )

            self.saveSettings()

            if not os.path.exists( IndicatorVirtualBox.AUTOSTART_PATH ):
                os.makedirs( IndicatorVirtualBox.AUTOSTART_PATH )

            if autostartCheckbox.get_active():
                try:
                    shutil.copy( IndicatorVirtualBox.DESKTOP_PATH + IndicatorVirtualBox.DESKTOP_FILE, IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE )
                except Exception as e:
                    logging.exception( e )
            else:
                try:
                    os.remove( IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE )
                except: pass

        self.dialog.destroy()
        self.dialog = None
        self.onRefresh()


    def onAbout( self, widget ):
        dialog = Gtk.AboutDialog()
        dialog.set_program_name( IndicatorVirtualBox.NAME )
        dialog.set_comments( IndicatorVirtualBox.AUTHOR )
        dialog.set_website( IndicatorVirtualBox.WEBSITE )
        dialog.set_website_label( IndicatorVirtualBox.WEBSITE )
        dialog.set_version( IndicatorVirtualBox.VERSION )
        dialog.set_license( IndicatorVirtualBox.LICENSE )
        dialog.run()
        dialog.destroy()
        dialog = None


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )

    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def loadSettings( self ):
        self.menuTextVirtualMachineRunningBefore = ""
        self.menuTextVirtualMachineRunningAfter = ""
        self.menuTextVirtualMachineNotRunningBefore = ""
        self.menuTextVirtualMachineNotRunningAfter = ""
        self.refreshIntervalInMinutes = 15
        self.showSubmenu = False
        self.sortDefault = True
        self.useRadioIndicator = True

        if os.path.isfile( IndicatorVirtualBox.SETTINGS_FILE ):
            try:
                with open( IndicatorVirtualBox.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.menuTextVirtualMachineRunningBefore = settings.get( IndicatorVirtualBox.SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_RUNNING_BEFORE, self.menuTextVirtualMachineRunningBefore )
                self.menuTextVirtualMachineRunningAfter = settings.get( IndicatorVirtualBox.SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_RUNNING_AFTER, self.menuTextVirtualMachineRunningAfter )
                self.menuTextVirtualMachineNotRunningBefore = settings.get( IndicatorVirtualBox.SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_NOT_RUNNING_BEFORE, self.menuTextVirtualMachineNotRunningBefore )
                self.menuTextVirtualMachineNotRunningAfter = settings.get( IndicatorVirtualBox.SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_NOT_RUNNING_AFTER, self.menuTextVirtualMachineNotRunningAfter )
                self.refreshIntervalInMinutes = settings.get( IndicatorVirtualBox.SETTINGS_REFRESH_INTERVAL_IN_MINUTES, self.refreshIntervalInMinutes )
                self.showSubmenu = settings.get( IndicatorVirtualBox.SETTINGS_SHOW_SUBMENU, self.showSubmenu )
                self.sortDefault = settings.get( IndicatorVirtualBox.SETTINGS_SORT_DEFAULT, self.sortDefault )
                self.useRadioIndicator = settings.get( IndicatorVirtualBox.SETTINGS_USE_RADIO_INDICATOR, self.useRadioIndicator )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorVirtualBox.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorVirtualBox.SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_RUNNING_BEFORE: self.menuTextVirtualMachineRunningBefore,
                IndicatorVirtualBox.SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_RUNNING_AFTER: self.menuTextVirtualMachineRunningAfter,
                IndicatorVirtualBox.SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_NOT_RUNNING_BEFORE: self.menuTextVirtualMachineNotRunningBefore,
                IndicatorVirtualBox.SETTINGS_MENU_TEXT_VIRTUAL_MACHINE_NOT_RUNNING_AFTER: self.menuTextVirtualMachineNotRunningAfter,
                IndicatorVirtualBox.SETTINGS_REFRESH_INTERVAL_IN_MINUTES: self.refreshIntervalInMinutes,
                IndicatorVirtualBox.SETTINGS_SHOW_SUBMENU: self.showSubmenu,
                IndicatorVirtualBox.SETTINGS_SORT_DEFAULT: self.sortDefault,
                IndicatorVirtualBox.SETTINGS_USE_RADIO_INDICATOR: self.useRadioIndicator
            }

            with open( IndicatorVirtualBox.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorVirtualBox.SETTINGS_FILE )


class VirtualMachineInfo:

    def __init__( self, name, isGroup, uuid, indent ):
        self.name = name
        self.isGroup = isGroup
        self.uuid = uuid
        self.indent = indent
        self.isRunning = False


    def getName( self ):
        return self.name


    def setName( self, name ):
        self.name = name


    def isGroup( self ):
        return self.isGroup


    def getUUID( self ):
        return self.uuid


    def getIndent( self ):
        return self.indent


    def setRunning( self ):
        self.isRunning = True


    def isRunning( self ):
        return self.isRunning


if __name__ == "__main__":
    indicator = IndicatorVirtualBox()
    indicator.main()