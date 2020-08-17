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


lat = -33
lon = 151
elev = 0
start = datetime.datetime.utcnow()
duration = 10


# https://celestrak.com/NORAD/elements/visual.txt
tle = [ "ISS (ZARYA)",
        "1 25544U 98067A   20230.44286670  .00000191  00000-0  11560-4 0  9992",
        "2 25544  51.6456  45.3129 0001685  35.7517  64.2421 15.49165392241518" ]


# https://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
# https://stackoverflow.com/questions/25966098/pyephem-next-pass-function-returns-different-result
def getPassesPyEphem():
    print( "ISS passes calculated from PyEphem:" )
    now = start
    while( now < ( start + datetime.timedelta( days = 2 ) ) ):
        observer = ephem.Observer()
        observer.lat = str( lat )
        observer.long = str( lon )
        observer.elevation = elev
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


def getPassesSkyfieldORIGINAL():
    print( "ISS passes calculated from Skyfield:" )
    observer = Topos( str( abs( lat ) ) + ( ' N' if lat >= 0 else ' S' ), str( abs( lon ) ) + ( ' E' if lon >= 0 else ' W' ) )
    ts = load.timescale()
    satellite = EarthSatellite( tle[ 1 ], tle[ 2 ], tle[ 0 ], ts )
    t0 = ts.utc( yearStart, monthStart, dayStart )
    t1 = ts.utc( yearEnd, monthEnd, dayEnd )
    t, events = satellite.find_events( observer, t0, t1, altitude_degrees = 30.0 )
    for ti, event in zip( t, events ):
        if event == 0:
            print( ti.utc_datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ), "False" )


# https://rhodesmill.org/skyfield/earth-satellites.html
# https://rhodesmill.org/skyfield/api-satellites.html
# https://github.com/skyfielders/python-skyfield/issues/327
# https://github.com/redraw/satellite-passes-api/blob/ffab732e20f6db0503d8e14be3e546ea35a50924/app/tracker.py#L28
def getPassesSkyfield():
    print( "ISS passes calculated from Skyfield:" )
    observer = Topos( str( abs( lat ) ) + ( ' N' if lat >= 0 else ' S' ), str( abs( lon ) ) + ( ' E' if lon >= 0 else ' W' ) )
    ts = load.timescale()
    satellite = EarthSatellite( tle[ 1 ], tle[ 2 ], tle[ 0 ], ts )
    t0 = ts.utc( yearStart, monthStart, dayStart )
    t1 = ts.utc( yearEnd, monthEnd, dayEnd )
    t, events = satellite.find_events( observer, t0, t1, altitude_degrees = 30.0 )
    passes = [ ]
    rise = False
    set = False
    culminate = False

    print( events )
    events = ''.join( str( i ) for i in events )
    events += "zzz"
    events = "aaa" + events 
    print( events )
    pattern = "(01+2)"

    import re
#     print( re.findall( pattern, events ) )
    print( re.split( pattern, events ) )

#     print( ''.join( str( i ) for i in events ) )
#     i = 0
#     while i < len( events ):
#         if events[ i ] == 0: # Rise
#             pass
# 
#         elif events[ i ] == 1: # Culminate
#             pass
# 
#         else: # Set
#             pass
# 
#         print( events[ i ] )
#         i += 1
    
    
#     for ti, event in zip( t, events ):
#         if event == 0:
#             print( ti.utc_datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ), "False" )


#     timeScale = load.timescale( builtin = True )
#     two_hours = timeScale.utc(2014, 1, 20, 0, range(0, 120, 20))
#     topos = Topos( latitude_degrees = lat, longitude_degrees = lon, elevation_m = elev )
#     ephemerisPlanets = load( "planets.bsp" )


def getPassesSkyfieldNEW():
    ephemeris = load( "de421.bsp" )
    observer = Topos( str( abs( lat ) ) + ( ' N' if lat >= 0 else ' S' ), str( abs( lon ) ) + ( ' E' if lon >= 0 else ' W' ) )
    ts = load.timescale()
    t0 = ts.utc( start.year, start.month, start.day )
    end = start + datetime.timedelta( days = duration )
    t1 = ts.utc( end.year, end.month, end.day )
    satellite = EarthSatellite( tle[ 1 ], tle[ 2 ], tle[ 0 ], ts )
    t, events = satellite.find_events( observer, t0, t1, altitude_degrees = 30.0 )
    rise = None
    culminate = None
    for ti, event in zip( t, events ):
        if event == 0: # Rise
            rise = ti

        elif event == 1: # Culminate (only the last culmination is taken if there happens to be more than one)
            culminate = ti

        else: # Set
            if rise is not None and culminate is not None and satellite.at( culminate ).is_sunlit( ephemeris ):
                print( rise.utc_datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ) )
                rise = None
                culminate = None


# getPassesPyEphem()
# print()
# getPassesSkyfield()
getPassesSkyfieldNEW()