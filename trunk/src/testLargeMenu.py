#!/usr/bin/env python3


# A large frontend menu refreshing every minute makes a SIGNIFICANT impact on the indicator!!!


from gi.repository import AppIndicator3, GLib, GObject, Gtk
from threading import Thread
import datetime


class TestLargeMenu:

    def __init__( self ):
        self.data = { } 
        GObject.threads_init()
        self.indicator = AppIndicator3.Indicator.new( "testLargeMenu", "indicator-lunar", AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.update()


    def main( self ): Gtk.main()


    def update( self ): Thread( target = self.updateBackend ).start()


    def updateBackend( self ):
        print( "updateBackend - start ", datetime.datetime.now() )

        self.data.clear()
        self.data[ 0 ] = 0

        GLib.idle_add( self.updateFrontend )
#         print( "updateBackend - end   ", datetime.datetime.now() )


    def updateFrontend( self ):
#         print( "updateFrontend - start", datetime.datetime.now() )
        self.updateMenu()
        self.eventSourceID = GLib.timeout_add_seconds( 120, self.update )
        print( "updateFrontend - end  ", datetime.datetime.now() )
        print()


    def updateMenu( self ):
        menu = Gtk.Menu()

        for i in range( 20 ):
            menuItem = Gtk.MenuItem( str( i + 1 ) )
            menu.append( menuItem )

            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for j in range( 100 ):
                menuItem = Gtk.MenuItem( str( j + 1 ) )
                subMenu.append( menuItem )

                subSubMenu = Gtk.Menu()
                menuItem.set_submenu( subSubMenu )
                for k in range( 10 ):
                    menuItem = Gtk.MenuItem( str( k + 1 ) )
                    subSubMenu.append( menuItem )

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        menuItem.connect( "activate", Gtk.main_quit )
        menu.append( menuItem )

        self.indicator.set_menu( menu )
        menu.show_all()


if __name__ == "__main__": TestLargeMenu().main()