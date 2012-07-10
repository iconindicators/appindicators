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


# Application indicator to start (and show running) Virtual Box virtual machines.


# Unity appindicator does not support styles in menu items.
# Therefore, cannot bold/italic a VM name when it is running (as originally intended).
# For reference, here is the original code (which works under GTK):
#  menuItem = gtk.MenuItem( "" )
#  menuItem.get_children()[ 0 ].set_use_markup( True )
#  menuItem.get_children()[ 0 ].set_markup( "<b><i>" + "item" + "</i></b>" )


# Ideas...
#
# Option to specify the pre/post menu text of running VMs and possibly non-running VMs too.


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
    VERSION = "1.0.4"
    ICON = "indicator-virtual-box"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/" + NAME + ".desktop"
    DESKTOP_PATH = "/usr/share/applications/" + NAME + ".desktop"

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_SORT_DEFAULT = "sortDefault"


    def __init__( self ):
        logging.basicConfig( file = sys.stderr, level = logging.INFO )
        self.loadSettings()

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
            self.buildMenu()
            self.indicator.set_status( appindicator.STATUS_ACTIVE )
        else:
            self.buildMenu()
            self.statusicon = gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorVirtualBox.ICON )
            self.statusicon.set_tooltip( "Virtual Machines" )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.updateMenu()
        gtk.main()


    def buildMenu( self ):
        menu = gtk.Menu()

        menu.append( gtk.SeparatorMenuItem() )

        self.frontEndMenuItem = gtk.MenuItem( "Frontend" )
        self.frontEndMenuItem.connect( "activate", self.onFrontEnd )
        menu.append( self.frontEndMenuItem )

        refreshMenuItem = gtk.MenuItem( "Refresh" )
        refreshMenuItem.connect( "activate", self.onRefresh )
        menu.append( refreshMenuItem )

        sortMenuItem = gtk.MenuItem( "Sort" )
        menu.append( sortMenuItem )

        subMenu = gtk.Menu()
        sortMenuItem.set_submenu( subMenu )

        sortDefaultMenuItem = gtk.RadioMenuItem( None, "Default", False )
        sortDefaultMenuItem.set_active( self.sortDefault )
        sortDefaultMenuItem.connect( "activate", self.onSortDefault )
        subMenu.append( sortDefaultMenuItem )

        sortAlphabeticallyMenuItem = gtk.RadioMenuItem( sortDefaultMenuItem, "Alphabetically", False )
        sortAlphabeticallyMenuItem.set_active( not self.sortDefault )
        sortAlphabeticallyMenuItem.connect( "activate", self.onSortAlphabetically )
        subMenu.append( sortAlphabeticallyMenuItem )

        autoStartMenuItem = gtk.CheckMenuItem( "Autostart" )
        autoStartMenuItem.set_active( os.path.exists( IndicatorVirtualBox.AUTOSTART_PATH ) )
        autoStartMenuItem.connect( "activate", self.onAutoStart )
        menu.append( autoStartMenuItem )

        aboutMenuItem = gtk.ImageMenuItem( stock_id = gtk.STOCK_ABOUT )
        aboutMenuItem.connect( "activate", self.onAbout )
        menu.append( aboutMenuItem )

        quitMenuItem = gtk.ImageMenuItem( stock_id = gtk.STOCK_QUIT )
        quitMenuItem.connect( "activate", gtk.main_quit )
        menu.append( quitMenuItem )

        menu.show_all()

        if appindicatorImported == True:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu


    def updateMenu( self ):
        if appindicatorImported == True:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.hide() # Safety - hide the menu whilst it is being rebuilt.

        # Remove all VMs from the menu.
        for item in menu.get_children():
            if type( item ) == gtk.SeparatorMenuItem:
                break

            menu.remove( item )

        # Add back in the refreshed list of VMs.
        position = 0
        if self.isVirtualBoxInstalled():
            self.getVirtualMachines()
            if len( self.virtualMachineNames ) == 0 :
                menu.insert( gtk.MenuItem( "(no virtual machines exist)" ), position )
                position += 1
            else:
                for virtualMachineName in self.virtualMachineNames:
                    virtualMachineInfo = self.virtualMachineInfos[ virtualMachineName ]
                    if virtualMachineInfo[ 1 ] == True:
                        vmMenuItem = gtk.MenuItem( "--- " + virtualMachineName + " ---" )
                    else:
                        vmMenuItem = gtk.MenuItem( virtualMachineName )

                    vmMenuItem.props.name = virtualMachineName
                    vmMenuItem.connect( "activate", self.onStartVirtualMachine )
                    menu.insert( vmMenuItem, position )
                    position += 1
        else:
            menu.insert( gtk.MenuItem( "(VirtualBox is not installed)" ), position )
            position += 1

        self.frontEndMenuItem.set_sensitive( self.isVirtualBoxInstalled( ) )

        menu.show_all()


    def getVirtualMachines( self ):
        self.virtualMachineNames = []
        self.virtualMachineInfos = {}

        # Get a list of all virtual machines...
        p = subprocess.Popen( "VBoxManage list vms", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        for line in p.stdout.readlines():
            info = line[ 1 : -2 ].split( "\" {" )

            self.virtualMachineNames.append( info[ 0 ] )

            # Create a hash entry:
            #  key is the virtual machine name.
            #  value is the virutal machine ID and a boolean indicating the running status (false for now).
            self.virtualMachineInfos[ info[ 0 ] ] = [ info[ 1 ], False ]

        p.wait()

        # Get a list of running virtual machines and adjust our information...
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


    def onSortDefault( self, widget ):
        self.sortDefault = True
        self.saveSettings()
        self.onRefresh( widget )


    def onSortAlphabetically( self, widget ):
        self.sortDefault = False
        self.saveSettings()
        self.onRefresh( widget )


    def onRefresh( self, widget ):
        gobject.idle_add( self.updateMenu )


    def onFrontEnd( self, widget ):
        subprocess.Popen( "VirtualBox &", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )


    def onStartVirtualMachine( self, widget ):
        virtualMachineName = widget.props.name
        if self.virtualMachineInfos.get( virtualMachineName )[ 1 ] == True:
            self.showMessage( gtk.MESSAGE_WARNING, IndicatorVirtualBox.NAME, "\'" + virtualMachineName + "\' is already running!" )
        else:
            command = "VBoxManage startvm " + self.virtualMachineInfos.get( virtualMachineName )[ 0 ]
            p = subprocess.Popen( command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
            p.wait()

        self.onRefresh( widget )


    def showMessage( self, messageType, title, message ):
        dialog = gtk.MessageDialog( None, 0, messageType, gtk.BUTTONS_OK, message )
        dialog.set_title( title )
        dialog.run()
        dialog.destroy()


    def onAbout( self, widget ):
        dialog = gtk.AboutDialog()
        dialog.set_name( IndicatorVirtualBox.NAME )
        dialog.set_version( IndicatorVirtualBox.VERSION )
        dialog.set_comments( IndicatorVirtualBox.AUTHOR )
        dialog.set_license( "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0" )
        dialog.set_website( "https://launchpad.net/~thebernmeister/+archive/indicator-virtual-box" )
        dialog.run()
        dialog.destroy()


    def onAutoStart( self, widget ):
        if widget.active:
            try:
                shutil.copy( IndicatorVirtualBox.DESKTOP_PATH, IndicatorVirtualBox.AUTOSTART_PATH )
            except Exception as e:
                logging.exception( e )
        else:
            try:
                os.remove( IndicatorVirtualBox.AUTOSTART_PATH )
            except: pass


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, gtk.status_icon_position_menu, 1, gtk.get_current_event_time(), self.statusicon )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, gtk.status_icon_position_menu, button, time, self.statusicon )


    def loadSettings( self ):
        self.sortDefault = True

        if os.path.isfile( IndicatorVirtualBox.SETTINGS_FILE ):
            try:
                with open( IndicatorVirtualBox.SETTINGS_FILE, 'r' ) as f:
                    settings = json.load( f )

                self.sortDefault = settings.get( IndicatorVirtualBox.SETTINGS_SORT_DEFAULT, self.sortDefault )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorVirtualBox.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorVirtualBox.SETTINGS_SORT_DEFAULT: self.sortDefault
            }

            with open( IndicatorVirtualBox.SETTINGS_FILE, 'w' ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorVirtualBox.SETTINGS_FILE )


if __name__ == "__main__":
    indicator = IndicatorVirtualBox()
    indicator.main()