#!/usr/bin/env python3

# Test to show satellite passes...

import datetime, ephem


def get_next_pass( lon, lat, alt, tle, now ):

    sat = ephem.readtle( str( tle[ 0 ] ), str( tle[ 1 ] ), str( tle[ 2 ] ) )

    observer = ephem.Observer()
    observer.lat = str( lat )
    observer.long = str( lon )
    observer.elevation = alt
    observer.pressure = 0
    observer.horizon = '-0:34'
    observer.date = now

    nextPass = observer.next_pass( sat )

    observer.date = nextPass[ 2 ]

    sun = ephem.Sun()
    sun.compute( observer )
    sat.compute( observer )

    visible = sat.eclipsed is False and sun.alt > ephem.degrees( "-18" ) and sun.alt < ephem.degrees( "-6" )

    return {
         "rise_time_utc": nextPass[ 0 ],
         "set_time_utc": nextPass[ 4 ],
         "visible": visible
   }


lon = 151.2
lat = -33.8
alt = 10
tle = [ "ISS (ZARYA)", "1 25544U 98067A   14151.47661569  .00003929  00000-0  75409-4 0  3958", "2 25544  51.6473 182.4298 0004138  53.2082  30.6877 15.50535211888731" ]

now = datetime.datetime.utcnow()
for i in range( 10 ):
    nextPass = get_next_pass( lon, lat, alt, tle, now )
    if nextPass[ "rise_time_utc" ] < nextPass[ "set_time_utc" ] and nextPass[ "visible" ]:
        print( ephem.localtime( nextPass[ "rise_time_utc" ] ) )

    now = nextPass[ "set_time_utc" ].datetime() + datetime.timedelta( minutes = 30 )
