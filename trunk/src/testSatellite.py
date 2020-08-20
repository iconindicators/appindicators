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
from skyfield import almanac


lat = -33
lon = 151
elev = 0
start = datetime.datetime.utcnow()
duration = 10


# https://celestrak.com/NORAD/elements/visual.txt
tle = [ "ISS (ZARYA)",
        "1 25544U 98067A   20233.40047826  .00003047  00000-0  63045-4 0  9997",
        "2 25544  51.6452  30.6789 0001426  56.0652 349.4690 15.49180893241971" ]


# https://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
# https://stackoverflow.com/questions/25966098/pyephem-next-pass-function-returns-different-result
def getPassesPyEphem():
    print( "ISS passes calculated from PyEphem:" )
    now = start
    while( now < ( start + datetime.timedelta( days = duration ) ) ):
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
        if sat.eclipsed is False and ephem.degrees( '-18' ) < sun.alt < ephem.degrees( '-6' ):
            print( tr.datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ), azr, "\t", ts.datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ), azs )

        now = observer.date.datetime() + datetime.timedelta( minutes = 90 )


# https://rhodesmill.org/skyfield/earth-satellites.html
# https://rhodesmill.org/skyfield/api-satellites.html
# https://github.com/skyfielders/python-skyfield/issues/327
def getPassesSkyfield():
    print( "ISS passes calculated from Skyfield:" )
    ephemeris = load( "de421.bsp" )
    observer = Topos( str( abs( lat ) ) + ( ' N' if lat >= 0 else ' S' ), str( abs( lon ) ) + ( ' E' if lon >= 0 else ' W' ) )
    ts = load.timescale()
    t0 = ts.utc( start.year, start.month, start.day, start.hour, start.minute )
    end = start + datetime.timedelta( days = duration )
    t1 = ts.utc( end.year, end.month, end.day, end.hour, end.minute )
    satellite = EarthSatellite( tle[ 1 ], tle[ 2 ], tle[ 0 ], ts )
    t, events = satellite.find_events( observer, t0, t1, altitude_degrees = 30 )
    rise = None
    culminate = None
    for ti, event in zip( t, events ):
        if event == 0: # Rise
            rise = ti

        elif event == 1: # Culminate (only the last culmination is taken if there happens to be more than one)
            culminate = ti

        else: # Set
            if rise is not None and culminate is not None and satellite.at( culminate ).is_sunlit( ephemeris ) and almanac.dark_twilight_day( ephemeris, observer )( culminate ) < 3:
                riseAlt, riseAz, riseBodyDistance = ( satellite - observer ).at( rise ).altaz()
                setAlt, setAz, setBodyDistance = ( satellite - observer ).at( ti ).altaz()
                print( rise.utc_datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ), str( riseAz ), "\t", ti.utc_datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ), str( setAz ) )
                rise = None
                culminate = None


getPassesPyEphem()
print()
getPassesSkyfield()