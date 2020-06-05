#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# https://spotthestation.nasa.gov/sightings/index.cfm
# https://www.heavens-above.com/PassSummary.aspx
# https://www.n2yo.com/passes/?s=25544
# https://www.satflare.com/track.asp?q=iss
# https://uphere.space/
# https://www.amsat.org/track/
# https://www.calsky.com/cs.cgi?cha=12&sec=4


import datetime, ephem
from skyfield.api import EarthSatellite, load, Topos


lat = -33.87
lon = 151.21

yearStart = 2020
monthStart = 6
dayStart = 5

yearEnd = 2020
monthEnd = 6
dayEnd = 7

# Source: https://celestrak.com/NORAD/elements/visual.txt
tle = [ "ISS (ZARYA)",
        "1 25544U 98067A   20157.17043900  .00001189  00000-0  29319-4 0  9996",
        "2 25544  51.6455  47.9439 0001982  29.8888  69.4543 15.49422649230155" ]


# https://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
def getPassesPyEphem():
    now = str( yearStart ) + '/' + str( monthStart  ) + '/' + str( dayStart )
    while( ephem.date( now ).datetime() < datetime.datetime( yearEnd, monthEnd, dayEnd ) ):
        observer = ephem.Observer()
        observer.lat = str( lat )
        observer.long = str( lon )
        observer.elevation = 0
        observer.pressure = 0
        observer.date = now

        sat = ephem.readtle( tle[ 0 ], tle[ 1 ], tle[ 2 ] )                 
        tr, azr, tt, altt, ts, azs = observer.next_pass( sat )

        observer.date = tt
        sun = ephem.Sun()
        sun.compute( observer )
        sat.compute( observer )
        visible = sat.eclipsed is False and ephem.degrees( '-18' ) < sun.alt < ephem.degrees( '-6' )
        print( tr.datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ), visible )
        now = observer.date.datetime() + datetime.timedelta( minutes = 90 )


def getPassesSkyfield():
    observer = Topos( str( abs( lat ) ) + ( ' N' if lat >= 0 else ' S' ), str( abs( lon ) ) + ( ' W' if lat >= 0 else ' E' ) )
    ts = load.timescale()
    satellite = EarthSatellite( tle[ 1 ], tle[ 2 ], tle[ 0 ], ts )
    t0 = ts.utc( yearStart, monthStart, dayStart )
    t1 = ts.utc( yearEnd, monthEnd, dayEnd )
    t, events = satellite.find_events( observer, t0, t1, altitude_degrees = 30.0 )
    for ti, event in zip( t, events ):
        if event == 0:
            print( ti.utc_datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ) )


getPassesPyEphem()
getPassesSkyfield()