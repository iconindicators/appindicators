#!/usr/bin/env python


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


# TODO: Eventually port from PyGTK to PyGObject - https://live.gnome.org/PyGObject


appindicatorImported = True
try:
    import appindicator
except:
    appindicatorImported = False

import gobject
import gtk
import json
import locale
import logging
import os
import shutil
import subprocess
import sys

from functools import cmp_to_key


class IndicatorVirtualBox:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-virtual-box"
    VERSION = "1.0.15"
    ICON = "indicator-virtual-box"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

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
            self.indicator = appindicator.Indicator( IndicatorVirtualBox.NAME, IndicatorVirtualBox.ICON, appindicator.CATEGORY_APPLICATION_STATUS )
            self.indicator.set_menu( gtk.Menu() ) # Set an empty menu to get things rolling...
            self.buildMenu()
            self.indicator.set_status( appindicator.STATUS_ACTIVE )
        else:
            self.menu = gtk.Menu() # Set an empty menu to get things rolling...
            self.buildMenu()
            self.statusicon = gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorVirtualBox.ICON )
            self.statusicon.set_tooltip( "Virtual Machines" )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.timeoutID = gobject.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.onRefresh )
        gtk.main()


    def buildMenu( self ):
        if appindicatorImported == True:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if we don't do this we get GTK complaints).

        # Create the new menu and populate...
        menu = gtk.Menu()

        if self.isVirtualBoxInstalled():
            self.getVirtualMachines()
            if len( self.virtualMachineNames ) == 0 :
                menu.append( gtk.MenuItem( "(no virtual machines exist)" ) )
            else:
                for virtualMachineName in self.virtualMachineNames:
                    virtualMachineInfo = self.virtualMachineInfos[ virtualMachineName ]
                    if virtualMachineInfo[ 1 ] == True: # VM is running...
                        if self.useRadioIndicator == True:
                            # For backward compatibility allow the user choose the radio indicator AND menu text.
                            vmMenuItem = gtk.RadioMenuItem( None, self.menuTextVirtualMachineRunningBefore + virtualMachineName + self.menuTextVirtualMachineRunningAfter, False )
                            vmMenuItem.set_active( True )
                        else:
                            vmMenuItem = gtk.MenuItem( self.menuTextVirtualMachineRunningBefore + virtualMachineName + self.menuTextVirtualMachineRunningAfter )
                    else:
                        vmMenuItem = gtk.MenuItem( self.menuTextVirtualMachineNotRunningBefore + virtualMachineName + self.menuTextVirtualMachineNotRunningAfter )

                    vmMenuItem.props.name = virtualMachineName
                    vmMenuItem.connect( "activate", self.onStartVirtualMachine )
                    menu.append( vmMenuItem )
        else:
            menu.insert( gtk.MenuItem( "(VirtualBox is not installed)" ), position )

        menu.append( gtk.SeparatorMenuItem() )

        self.virtualBoxMenuItem = gtk.MenuItem( "Launch VirtualBox" )
        self.virtualBoxMenuItem.connect( "activate", self.onLaunchVirtualBox )
        self.virtualBoxMenuItem.set_sensitive( self.isVirtualBoxInstalled( ) )
        menu.append( self.virtualBoxMenuItem )

        preferencesMenuItem = gtk.MenuItem( "Preferences" )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        menu.append( preferencesMenuItem )

        aboutMenuItem = gtk.ImageMenuItem( stock_id = gtk.STOCK_ABOUT )
        aboutMenuItem.connect( "activate", self.onAbout )
        menu.append( aboutMenuItem )

        quitMenuItem = gtk.ImageMenuItem( stock_id = gtk.STOCK_QUIT )
        quitMenuItem.connect( "activate", gtk.main_quit )
        menu.append( quitMenuItem )

        if appindicatorImported == True:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu

        menu.show_all()


    def getVirtualMachines( self ):
        self.virtualMachineNames = [] # Order is that given by the VirtualBox UI.
        self.virtualMachineInfos = {} # 'key' is the virtual machine name; 'value' is the virtual machine uuid and a boolean indicating the running status.

        if not self.isVirtualBoxInstalled():
            return

        # Get the VM uuids and ordering from the VirtualBox UI...
        p = subprocess.Popen( "grep GUI/SelectorVMPositions $HOME/.VirtualBox/VirtualBox.xml", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        virtualMachineUUIDsSorted = list( p.communicate()[ 0 ].rstrip( "\"/>\n" ).split( "value=\"" )[ 1 ].split( "," ) )

        # Get the VM names and uuids...
        p = subprocess.Popen( "VBoxManage list vms", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        uuidToName = {} # Used to map uuid to name.
        for line in p.stdout.readlines():
            info = line[ 1 : -2 ].split( "\" {" )
            self.virtualMachineInfos[ info[ 0 ] ] = [ info[ 1 ], False ]
            uuidToName[ info[ 1 ] ] = info[ 0 ]

        p.wait()

        # Build a list of VM names, sorted by VirtualBox UI order.
        for virtualMachineUUID in virtualMachineUUIDsSorted:
            self.virtualMachineNames.append( uuidToName[ virtualMachineUUID ] )

        # Determine which VMs are running.
        p = subprocess.Popen( "VBoxManage list runningvms", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        for line in p.stdout.readlines():
            info = line[ 1 : -2 ].split( "\" {" )
            del self.virtualMachineInfos[ info[ 0 ] ]
            self.virtualMachineInfos[ info[ 0 ] ] = [ info[ 1 ], True ]

        p.wait()

        # Alphabetically sort...
        if self.sortDefault == False:
            self.virtualMachineNames = sorted( self.virtualMachineNames, key = cmp_to_key( locale.strcoll ) )


    def isVirtualBoxInstalled( self ):
        p = subprocess.Popen( "which VBoxManage", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        return p.communicate()[ 0 ] != ''


    def onRefresh( self ):
        gobject.idle_add( self.buildMenu )
        return True # Must return true so that we continue to be called (http://www.pygtk.org/pygtk2reference/gobject-functions.html#function-gobject--timeout-add).


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
            self.showMessage( gtk.MESSAGE_ERROR, "The VM could not be found - either it has been renamed or deleted.  The list of VMs has been refreshed - please try again." )

        self.onRefresh()


    def showMessage( self, messageType, message ):
        dialog = gtk.MessageDialog( None, 0, messageType, gtk.BUTTONS_OK, message )
        dialog.run()
        dialog.destroy()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            return

        self.dialog = gtk.Dialog( "Preferences", None, 0, ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK ) )

        table = gtk.Table( 13, 2, False )
        table.set_col_spacings( 5 )
        table.set_row_spacings( 5 )

        label = gtk.Label( "VM running:" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 0, 1 )

        label = gtk.Label( "  Text before" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 1, 2 )

        textRunningBefore = gtk.Entry()
        textRunningBefore.set_text( self.menuTextVirtualMachineRunningBefore )
        table.attach( textRunningBefore, 1, 2, 1, 2 )

        label = gtk.Label( "  Text after" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 2, 3 )

        textRunningAfter = gtk.Entry()
        textRunningAfter.set_text( self.menuTextVirtualMachineRunningAfter )
        table.attach( textRunningAfter, 1, 2, 2, 3 )

        table.attach( gtk.Label( "" ), 0, 2, 3, 4 ) # Couldn't figure out how to put in an empty line or padding!

        label = gtk.Label( "VM not running:" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 4, 5 )

        label = gtk.Label( "  Text before" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 5, 6 )

        textNotRunningBefore = gtk.Entry()
        textNotRunningBefore.set_text( self.menuTextVirtualMachineNotRunningBefore )
        table.attach( textNotRunningBefore, 1, 2, 5, 6 )

        label = gtk.Label( "  Text after" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 6, 7 )

        textNotRunningAfter = gtk.Entry()
        textNotRunningAfter.set_text( self.menuTextVirtualMachineNotRunningAfter )
        table.attach( textNotRunningAfter, 1, 2, 6, 7 )

        table.attach( gtk.Label( "" ), 0, 2, 7, 8 ) # Couldn't figure out how to put in an empty line or padding!

        label = gtk.Label( "Refresh interval (minutes)" )
        label.set_alignment( 0, 0.5 )
        table.attach( label, 0, 1, 8, 9 )

        spinner = gtk.SpinButton( gtk.Adjustment( self.refreshIntervalInMinutes, 1, 60, 1, 5, 0 ) )
        spinner.set_tooltip_text( "How often the list of VMs and their running status is automatically updated" )
        table.attach( spinner, 1, 2, 8, 9 )

        table.attach( gtk.Label( "" ), 0, 2, 9, 10 ) # Couldn't figure out how to put in an empty line or padding!

        useRadioCheckbox = gtk.CheckButton( "Use a \"radio button\" to indicate a running VM" )
        useRadioCheckbox.set_active( self.useRadioIndicator )
        table.attach( useRadioCheckbox, 0, 2, 10, 11 )

        sortAlphabeticallyCheckbox = gtk.CheckButton( "Sort VMs alphabetically" )
        sortAlphabeticallyCheckbox.set_tooltip_text( "Unchecked will sort as per VirtualBox UI" )
        sortAlphabeticallyCheckbox.set_active( not self.sortDefault )
        table.attach( sortAlphabeticallyCheckbox, 0, 2, 11, 12 )

        autostartCheckbox = gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorVirtualBox.AUTOSTART_PATH + IndicatorVirtualBox.DESKTOP_FILE ) )
        table.attach( autostartCheckbox, 0, 2, 12, 13 )

        self.dialog.vbox.pack_start( table, True, True, 10 )
        self.dialog.set_border_width( 10 )

        self.dialog.show_all()
        response = self.dialog.run()
        if response == gtk.RESPONSE_OK:
            self.menuTextVirtualMachineRunningBefore = textRunningBefore.get_text()
            self.menuTextVirtualMachineRunningAfter = textRunningAfter.get_text()
            self.menuTextVirtualMachineNotRunningBefore = textNotRunningBefore.get_text()
            self.menuTextVirtualMachineNotRunningAfter = textNotRunningAfter.get_text()
            self.useRadioIndicator = useRadioCheckbox.get_active()
            self.sortDefault = not sortAlphabeticallyCheckbox.get_active()

            self.refreshIntervalInMinutes = spinner.get_value_as_int()
            gobject.source_remove( self.timeoutID )
            self.timeoutID = gobject.timeout_add_seconds( 60 * self.refreshIntervalInMinutes, self.onRefresh )

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
        dialog = gtk.AboutDialog()
        dialog.set_name( IndicatorVirtualBox.NAME )
        dialog.set_version( IndicatorVirtualBox.VERSION )
        dialog.set_comments( IndicatorVirtualBox.AUTHOR )
        dialog.set_license( "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0" )
        dialog.set_website( "https://launchpad.net/~thebernmeister" )
        dialog.run()
        dialog.destroy()
        dialog = None


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, gtk.status_icon_position_menu, 1, gtk.get_current_event_time(), self.statusicon )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, gtk.status_icon_position_menu, button, time, self.statusicon )


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
                with open( IndicatorVirtualBox.SETTINGS_FILE, 'r' ) as f:
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

            with open( IndicatorVirtualBox.SETTINGS_FILE, 'w' ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorVirtualBox.SETTINGS_FILE )


if __name__ == "__main__":
    indicator = IndicatorVirtualBox()
    indicator.main()