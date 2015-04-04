#!/usr/bin/env python3


# A large backend data refreshing every minute makes NO impact on the indicator.


from gi.repository import AppIndicator3, GLib, GObject, Gtk
from threading import Thread
import datetime


class TestLargeData:

    def __init__( self ):
        self.data = { } 
        GObject.threads_init()
        self.indicator = AppIndicator3.Indicator.new( "testLargeData", "indicator-lunar", AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.update()


    def main( self ): Gtk.main()


    def update( self ): Thread( target = self.updateBackend ).start()


    def updateBackend( self ):
        print( "updateBackend - start ", datetime.datetime.now() )

        self.data.clear()
        for i in range( 100000 ):
            self.data[ i ] = i * i

        GLib.idle_add( self.updateFrontend )
#         print( "updateBackend - end   ", datetime.datetime.now() )


    def updateFrontend( self ):
#         print( "updateFrontend - start", datetime.datetime.now() )
        self.updateMenu()
        self.eventSourceID = GLib.timeout_add_seconds( 60, self.update )
        print( "updateFrontend - end  ", datetime.datetime.now() )
        print()


    def updateMenu( self ):
        menu = Gtk.Menu()

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        menuItem.connect( "activate", Gtk.main_quit )
        menu.append( menuItem )

        self.indicator.set_menu( menu )
        menu.show_all()


if __name__ == "__main__": TestLargeData().main()