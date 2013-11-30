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


# Application indicator which displays fortunes.


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html



# http://ubuntuguide.org/wiki/Fortune

# Before installing, remove fortune-mod and see if that is the only needed dependency.


try:
    from gi.repository import AppIndicator3 as appindicator
except:
    pass

from gi.repository import GLib, Gtk

notifyImported = True
try:
    from gi.repository import Notify
except:
    notifyImported = False

import datetime, json, locale, logging, math, os, shutil, subprocess, sys


class IndicatorFortune:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-fortune"
    VERSION = "1.0.0"
    ICON = NAME
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_SHOW_CLASSIC = "showClassic"
    SETTINGS_SHOW_ISSUE = "showIssue"

    WEREWOLF_WARNING_TEXT_BODY = "                                          ...werewolves about ! ! !"
    WEREWOLF_WARNING_TEXT_SUMMARY = "W  A  R  N  I  N  G"


    def __init__( self ):
        filehandler = logging.FileHandler( filename = IndicatorFortune.LOG, mode = "a", delay = True )
        logging.basicConfig( format = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                             datefmt = "%H:%M:%S", level = logging.DEBUG,
                             handlers = [ filehandler ] )

        self.dialog = None
#         self.loadSettings()

        if notifyImported:
            Notify.init( IndicatorFortune.NAME ) 
# Maybe bail out or do something like bail out if cannot be imported same as ephem.


        # Create the indicator...
        try:
            self.appindicatorImported = True
            self.indicator = appindicator.Indicator.new( IndicatorFortune.NAME, IndicatorFortune.ICON, appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling...
            self.buildMenu()
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
        except:
            self.appindicatorImported = False
            self.menu = Gtk.Menu() # Set an empty menu to get things rolling...
            self.buildMenu()
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorFortune.ICON )
            self.statusicon.set_tooltip_text( "Virtual Machines" )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )



    def main( self ):
        self.update()
#         GLib.timeout_add_seconds( 10, self.update )
        Gtk.main()


    def update( self ):
#         self.buildMenu()

        f = ""
        p = subprocess.Popen( "fortune", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        for line in p.stdout.readlines():
            l = str( line.decode() )
            print( l )
            f += l

        p.wait()

        # The notification summary text must not be empty (at least on Unity).
        Notify.Notification.new( "Fortune. . .", f, IndicatorFortune.ICON ).show()

        
        return True




    def buildMenu( self ):
#TODO Maybe only build the menu like stardate indicator - once only.        
        if self.appindicatorImported:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if we don't do this we get GTK complaints).
        menu = Gtk.Menu()

        menuItem = Gtk.MenuItem( "One off the top" )
        menuItem.connect( "activate", self.onOneOffTheTop )
        menu.append( menuItem )

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

        if self.appindicatorImported:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu

        menu.show_all()


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def getFortune( self ):
        f = ""
        p = subprocess.Popen( "fortune", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        for line in p.stdout.readlines():
            l = str( line.decode() )
            print( l )
            f += l

        p.wait()

        return f


    def onOneOffTheTop( self, widget ):
        Notify.Notification.new( "Fortune. . .", self.getFortune(), IndicatorFortune.ICON ).show()



    def onAbout( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.dialog = Gtk.AboutDialog()
        self.dialog.set_program_name( IndicatorFortune.NAME )
        self.dialog.set_comments( IndicatorFortune.AUTHOR + "\n\nCalculations courtesy of PyEphem/XEphem.\nEclipse information by Fred Espenak and Jean Meeus.\nTropical Sign by Ignius Drake.\n" )
        self.dialog.set_website( IndicatorFortune.WEBSITE )
        self.dialog.set_website_label( IndicatorFortune.WEBSITE )
        self.dialog.set_version( IndicatorFortune.VERSION )
        self.dialog.set_license( IndicatorFortune.LICENSE )
        self.dialog.set_icon_name( Gtk.STOCK_ABOUT )
        self.dialog.run()
        self.dialog.destroy()
        self.dialog = None


    def onPreferences( self, widget ):
        return



    def showMessage( self, messageType, message ):
        dialog = Gtk.MessageDialog( None, 0, messageType, Gtk.ButtonsType.OK, message )
        dialog.run()
        dialog.destroy()


    def loadSettings( self ):
        return


    def saveSettings( self ):
        return


if __name__ == "__main__": IndicatorFortune().main()