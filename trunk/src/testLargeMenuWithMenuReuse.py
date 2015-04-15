#!/usr/bin/env python3


# Caching the menuitems and updating just those, rather than rebuilding the menu, still makes a SIGNIFICANT impact on the indicator!!!


from gi.repository import AppIndicator3, GLib, GObject, Gtk
from threading import Thread
import datetime


# WILL NOT WORK FOR SATELLITES WHICH SORT BY RISE TIME WHICH REQUIRES THE MENU TO REBUILT ON EACH REFRESH!!!


# Planets: 10, but say 20 including moon/sun and planetary moons
# Stars: 100
# OE: 785 (but only a couple or so visible)
# Sats: 141
# Total =  20 + 100 + 785 + 141 = 1000 approximately TOTAL items at the second level.
# Assume 10 items at the top/first level, which 1000 / 10 = 100 items at each second level, on average.
# Assume 10 items at each third level.
LEVEL_1 = 10
LEVEL_2 = 100
LEVEL_3 = 10


class TestLargeMenuWithReuse:

    def __init__( self ):
        self.data = { } 
        GObject.threads_init()
        self.indicator = AppIndicator3.Indicator.new( "testLargeMenuWithReuse", "indicator-lunar", AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.buildMenu()
        self.update()


    def main( self ): Gtk.main()


    def buildMenu( self ):
        print( "buildMenu - start     ", datetime.datetime.now() )
        self.menus = { }
        menu = Gtk.Menu()

        for i in range( LEVEL_1 ):
            menuItem = Gtk.MenuItem( str( i + 1 ) )
            menu.append( menuItem )

            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for j in range( LEVEL_2 ):
                menuItem = Gtk.MenuItem( str( j + 1 ) )
                subMenu.append( menuItem )

                subSubMenu = Gtk.Menu()
                menuItem.set_submenu( subSubMenu )
                for k in range( LEVEL_3 ):
                    menuItem = Gtk.MenuItem( "Refreshing..." )
                    subSubMenu.append( menuItem )
                    self.menus[ ( i, j, k ) ] = menuItem

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        menuItem.connect( "activate", Gtk.main_quit )
        menu.append( menuItem )

        self.indicator.set_menu( menu )
        menu.show_all()
        print( "buildMenu - end       ", datetime.datetime.now() )


    def update( self ): Thread( target = self.updateBackend ).start()


    def updateBackend( self ):
        print( "updateBackend - start ", datetime.datetime.now() )

        self.data.clear()
        now = datetime.datetime.now()
        print( "Current time          ", now )
        for i in range( LEVEL_1 ):
            for j in range( LEVEL_2 ):
                for k in range( LEVEL_3 ):
                    self.data[ ( i, j, k ) ] =  str( i + 1 ) + " " + str( j + 1 ) + " " + str( k + 1 ) + " - " + str( now )

        GLib.idle_add( self.updateFrontend )
#         print( "updateBackend - end   ", datetime.datetime.now() )


    def updateFrontend( self ):
#         print( "updateFrontend - start", datetime.datetime.now() )
        self.updateMenu()
        self.eventSourceID = GLib.timeout_add_seconds( 12000, self.update )
        print( "updateFrontend - end  ", datetime.datetime.now() )
        print()


    def updateMenu( self ):
        for i in range( LEVEL_1 ):
            for j in range( LEVEL_2 ):
                for k in range( LEVEL_3 ):
                    menuItem = self.menus[ ( i, j, k ) ]
                    menuItem.set_label( self.data[ i, j, k ] )


if __name__ == "__main__": TestLargeMenuWithReuse().main()