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


# Unity appindicator does not support styles in menu items, so cannot bold/italic
# a VM name when it is running (as originally intended).
# For reference, here is the original code (which works under GTK):
#  menuItem = gtk.MenuItem( "" )
#  menuItem.get_children()[ 0 ].set_use_markup( True )
#  menuItem.get_children()[ 0 ].set_markup( "<b><i>" + "item" + "</i></b>" )


# On Lubuntu 12.10 the following message appears when the indicator is executed:
#   ERROR:root:Could not find any typelib for AppIndicator3
# From https://kororaa.org/forums/viewtopic.php?f=7&t=220#p2343, it (hopefully) is safe to ignore.


from functools import cmp_to_key

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
            if len( self.virtualMachineNames ) == 0 :
                menu.append( Gtk.MenuItem( "(no virtual machines exist)" ) )
            else:
                for virtualMachineName in self.virtualMachineNames:
                    virtualMachineInfo = self.virtualMachineInfos[ virtualMachineName ]
                    if virtualMachineInfo[ 1 ] == True: # VM is running...
                        if self.useRadioIndicator == True:
                            vmMenuItem = Gtk.RadioMenuItem.new_with_label( [], self.menuTextVirtualMachineRunningBefore + virtualMachineName + self.menuTextVirtualMachineRunningAfter )
                            vmMenuItem.set_active( True )
                        else:
                            vmMenuItem = Gtk.MenuItem( self.menuTextVirtualMachineRunningBefore + virtualMachineName + self.menuTextVirtualMachineRunningAfter )
                    else:
                        vmMenuItem = Gtk.MenuItem( self.menuTextVirtualMachineNotRunningBefore + virtualMachineName + self.menuTextVirtualMachineNotRunningAfter )

                    vmMenuItem.props.name = virtualMachineName
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
        # For Python3, need to apply decode to the output of subprocess...
        # http://stackoverflow.com/questions/8652767/python3-subprocess-communicate-example
        return p.communicate()[ 0 ].decode() != ''


    def getVirtualMachines( self ):
        self.virtualMachineNames = [] # The sort order is given by the VirtualBox UI.
        self.virtualMachineInfos = {} # 'key' is the virtual machine name; 'value' is the VM uuid and a boolean for the running status.

        if not self.isVirtualBoxInstalled():
            return

        # Get the name and uuid of every VM...
        p = subprocess.Popen( "VBoxManage list vms", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        uuidToName = {} # Used (below) to map uuid to name.
        for line in p.stdout.readlines():
            info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
            self.virtualMachineInfos[ info[ 0 ] ] = [ info[ 1 ], False ]
            uuidToName[ info[ 1 ] ] = info[ 0 ]
            self.virtualMachineNames.append( info[ 0 ] ) # Used (below) when sorting VMs by VirtualBox UI order.

        p.wait()

        # Determine which VMs are running...
        p = subprocess.Popen( "VBoxManage list runningvms", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        for line in p.stdout.readlines():
            info = str( line.decode() )[ 1 : -2 ].split( "\" {" )
            del self.virtualMachineInfos[ info[ 0 ] ]
            self.virtualMachineInfos[ info[ 0 ] ] = [ info[ 1 ], True ]

        p.wait()

        # Build a list of VM names, sorted by VirtualBox UI order (from the VirtualBox configuration file).  However...
        # If VirtualBox is installed but has not been run, the configuration file probably won't exist.
        # If the ordering of the VMs has not been changed in the VirtualBox GUI, the order section in the configuration file will not exist.
        virtualMachineUUIDsSorted = []
        if os.path.exists( IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION ):
            p = subprocess.Popen( "grep GUI/SelectorVMPositions " + IndicatorVirtualBox.VIRTUAL_BOX_CONFIGURATION, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
            try:
                virtualMachineUUIDsSorted = list( p.communicate()[ 0 ].decode().rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )
            except: # The VM order has never been altered giving an empty result (and exception).
                virtualMachineUUIDsSorted = []

        # Build a list of VM names, sorted by VirtualBox UI order.
        if len( virtualMachineUUIDsSorted ) > 0: # Will be empty if VirtualBox has not been run or the sort order has not been altered.
            self.virtualMachineNames = []
            for virtualMachineUUID in virtualMachineUUIDsSorted:
                self.virtualMachineNames.append( uuidToName[ virtualMachineUUID ] )

        # Alphabetically sort...
        if self.sortDefault == False:
            self.virtualMachineNames = sorted( self.virtualMachineNames, key = cmp_to_key( locale.strcoll ) )


    def onRefresh( self ):
        gobject.idle_add( self.buildMenu )
        return True # Must return true so that we continue to be called (http://www.pygtk.org/pygtk2reference/gobject-functions.html#function-gi--timeout-add).


    def onLaunchVirtualBox( self, widget ):
        subprocess.Popen( "VirtualBox &", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )


    def onStartVirtualMachine( self, widget ):
        virtualMachineName = widget.props.name
        self.getVirtualMachines()
        if ( virtualMachineName in self.virtualMachineInfos ) == True: # It's possible the VM was renamed/deleted within VirtualBox but we've not refreshed yet to discover that change...
            if self.virtualMachineInfos.get( virtualMachineName )[ 1 ] == True:
                windowID = None
                p = subprocess.Popen( "wmctrl -l", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
                for line in p.stdout.readlines():
                    if virtualMachineName in line:
                        windowID = line[ 0 : line.find( " " ) ]

                p.wait()

                if windowID is not None:
                    p = subprocess.Popen( "wmctrl -i -a " + windowID, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
                    p.wait()
            else:
                command = "VBoxManage startvm " + self.virtualMachineInfos.get( virtualMachineName )[ 0 ]
                p = subprocess.Popen( command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
                p.wait()
        else:
            self.showMessage( Gtk.MessageType.ERROR, "The VM could not be found - either it has been renamed or deleted.  The list of VMs has been refreshed - please try again." )

        self.onRefresh()


    def showMessage( self, messageType, message ):
        dialog = Gtk.MessageDialog( None, 0, messageType, Gtk.ButtonsType.OK, message )
        dialog.run()
        dialog.destroy()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            return

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )

        table = Gtk.Table( 13, 2, False )
        table.set_col_spacings( 5 )
        table.set_row_spacings( 5 )

        label = Gtk.Label( "VM running:" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 0, 1 )

        label = Gtk.Label( "  Text before" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 1, 2 )

        textRunningBefore = Gtk.Entry()
        textRunningBefore.set_text( self.menuTextVirtualMachineRunningBefore )
        table.attach( textRunningBefore, 1, 2, 1, 2 )

        label = Gtk.Label( "  Text after" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 2, 3 )

        textRunningAfter = Gtk.Entry()
        textRunningAfter.set_text( self.menuTextVirtualMachineRunningAfter )
        table.attach( textRunningAfter, 1, 2, 2, 3 )

        table.attach( Gtk.Label( "" ), 0, 2, 3, 4 ) # Couldn't figure out how to put in an empty line or padding!

        label = Gtk.Label( "VM not running:" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 4, 5 )

        label = Gtk.Label( "  Text before" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 5, 6 )

        textNotRunningBefore = Gtk.Entry()
        textNotRunningBefore.set_text( self.menuTextVirtualMachineNotRunningBefore )
        table.attach( textNotRunningBefore, 1, 2, 5, 6 )

        label = Gtk.Label( "  Text after" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 6, 7 )

        textNotRunningAfter = Gtk.Entry()
        textNotRunningAfter.set_text( self.menuTextVirtualMachineNotRunningAfter )
        table.attach( textNotRunningAfter, 1, 2, 6, 7 )

        table.attach( Gtk.Label( "" ), 0, 2, 7, 8 ) # Couldn't figure out how to put in an empty line or padding!

        label = Gtk.Label( "Refresh interval (minutes)" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 8, 9 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60, 1, 5, 0 ) )
        spinner.set_tooltip_text( "How often the list of VMs and their running status is automatically updated" )
        table.attach( spinner, 1, 2, 8, 9 )

        table.attach( Gtk.Label( "" ), 0, 2, 9, 10 ) # Couldn't figure out how to put in an empty line or padding!

        useRadioCheckbox = Gtk.CheckButton( "Use a \"radio button\" to indicate a running VM" )
        useRadioCheckbox.set_active( self.useRadioIndicator )
        table.attach( useRadioCheckbox, 0, 2, 10, 11 )

        sortAlphabeticallyCheckbox = Gtk.CheckButton( "Sort VMs alphabetically" )
        sortAlphabeticallyCheckbox.set_tooltip_text( "Unchecked will sort as per VirtualBox UI" )
        sortAlphabeticallyCheckbox.set_active( not self.sortDefault )
        table.attach( sortAlphabeticallyCheckbox, 0, 2, 11, 12 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE ) )
        table.attach( autostartCheckbox, 0, 2, 12, 13 )

        self.dialog.vbox.pack_start( table, True, True, 10 )
        self.dialog.set_border_width( 10 )

        self.dialog.show_all()
        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.menuTextVirtualMachineRunningBefore = textRunningBefore.get_text()
            self.menuTextVirtualMachineRunningAfter = textRunningAfter.get_text()
            self.menuTextVirtualMachineNotRunningBefore = textNotRunningBefore.get_text()
            self.menuTextVirtualMachineNotRunningAfter = textNotRunningAfter.get_text()
            self.useRadioIndicator = useRadioCheckbox.get_active()
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
                IndicatorVirtualBox.SETTINGS_SORT_DEFAULT: self.sortDefault,
                IndicatorVirtualBox.SETTINGS_USE_RADIO_INDICATOR: self.useRadioIndicator
            }

            with open( IndicatorVirtualBox.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorVirtualBox.SETTINGS_FILE )


if __name__ == "__main__":
    indicator = IndicatorVirtualBox()
    indicator.main()