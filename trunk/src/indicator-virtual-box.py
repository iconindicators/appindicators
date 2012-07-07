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


# Application indicator to start/stop Virtual Box virtual machines.


# Unity appindicator does not support styles in menu items.
# Therefore, cannot bold/italic a VM name when it is running (as originally intended).
# For reference, here is the original code (which works under GTK):
#  menuItem = gtk.MenuItem( "" )
#  menuItem.get_children()[ 0 ].set_use_markup( True )
#  menuItem.get_children()[ 0 ].set_markup( "<b><i>" + "item" + "</i></b>" )


#TODO Let user specify sort order of VM names - alpha or what VBoxManage gives (matches UI list)


#TODO Let user specify the left/right text of running VMs...or maybe non running VMs too.
#Can we use an image menu item?


appindicatorImported = True
try:
    import appindicator
except:
    appindicatorImported = False

import gobject
import gtk
import logging
import os
import shutil
import subprocess
import sys


class IndicatorVirtualBox:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-virtual-box"
    VERSION = "1.0.1"
    ICON = "indicator-virtual-box"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/" + NAME + ".desktop"
    DESKTOP_PATH = "/usr/share/applications/" + NAME + ".desktop"


    def __init__( self ):
        logging.basicConfig( file = sys.stderr, level = logging.INFO )

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

        refreshMenuItem = gtk.MenuItem( "Refresh" )
        refreshMenuItem.connect( "activate", self.onRefresh )
        menu.append( refreshMenuItem )

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
            virtualMachines = self.getVirtualMachines( False )
            if virtualMachines is None:
                menu.insert( gtk.MenuItem( "(no virtual machines exist)" ), position )
                position += 1
            else:
                virtualMachinesRunning = self.getVirtualMachines( True )
                for vm in virtualMachines:
                    if vm in virtualMachinesRunning:
                        vmMenuItem = gtk.MenuItem( "--- " + vm[ 0 ] + " ---" )
                    else:
                        vmMenuItem = gtk.MenuItem( vm[ 0 ] )

                    vmMenuItem.props.name = vm[ 0 ]
                    vmMenuItem.connect( "activate", self.onStartVirtualMachine )
                    menu.insert( vmMenuItem, position )
                    position += 1
        else:
            menu.insert( gtk.MenuItem( "(VBoxManage is not installed)" ), position )
            position += 1

        menu.show_all()


    def getVirtualMachines( self, isRunning ):
        virtualMachines = []
        command = "VBoxManage list "
        if isRunning == True:
            command += "runningvms"
        else:
            command += "vms"

        p = subprocess.Popen( command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        for line in p.stdout.readlines():
            vm = line[ 1 : -2 ].split( "\" {" )
            virtualMachines.append( vm )

        p.wait()
        return virtualMachines


    def isVirtualBoxInstalled( self ):
        p = subprocess.Popen( "which VBoxManage", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        return p.communicate()[ 0 ] != ''


    def onRefresh( self, widget ):
        gobject.idle_add( self.updateMenu )


    def onStartVirtualMachine( self, widget ):
        vmName = widget.props.name

        virtualMachinesRunning = self.getVirtualMachines( True )
        for vm in virtualMachinesRunning:
            if vm[ 0 ] == vmName:
                self.showMessage( gtk.MESSAGE_WARNING, IndicatorVirtualBox.NAME, "\'" + vmName + "\' is already running!" )
                self.onRefresh( widget ) # Do an update as it's possible the menu is out of date.
                return

        virtualMachines = self.getVirtualMachines( False )
        for vm in virtualMachines:
            if vm[ 0 ] == vmName:
                command = "VBoxManage startvm " + vm[ 1 ]
                p = subprocess.Popen( command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
                p.wait()
                self.onRefresh( widget )
                return


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


if __name__ == "__main__":
    indicator = IndicatorVirtualBox()
    indicator.main()