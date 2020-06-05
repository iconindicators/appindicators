#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# https://github.com/skyfielders/python-skyfield/issues/327
# https://rhodesmill.org/skyfield/earth-satellites.html#finding-when-a-satellite-is-in-sunlight
# 
# https://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
# 
# https://spotthestation.nasa.gov/sightings/index.cfm
# https://www.heavens-above.com/PassSummary.aspx
# https://www.n2yo.com/passes/?s=25544
# https://www.satflare.com/track.asp?q=iss
# https://uphere.space/
# https://www.amsat.org/track/
# https://www.calsky.com/cs.cgi?cha=12&sec=4
# 
# https://rhodesmill.org/pyephem/quick.html
# https://rhodesmill.org/pyephem/tutorial.html


import datetime, ephem


from skyfield.api import EarthSatellite, load


passes = 10
lat = -33.87
lon = 151.21
year = 2020
month = 6
day = 5
tle = [ "ISS (ZARYA)",
        "1 25544U 98067A   20157.17043900  .00001189  00000-0  29319-4 0  9996",
        "2 25544  51.6455  47.9439 0001982  29.8888  69.4543 15.49422649230155" ] # Source: https://celestrak.com/NORAD/elements/visual.txt


def getPassesPyEphem():
    now = str( year ) + '/' + str( month ) + '/' + str( day )
    count = 0
    while( count < passes ):
        observer = ephem.Observer()
        observer.lat = str( lat )
        observer.long = str( lon )
        observer.elevation = 0
        observer.pressure = 0
        observer.date = now

        sat = ephem.readtle( tle[ 0 ], tle[ 1 ], tle[ 2 ] )                 
        tr, azr, tt, altt, ts, azs = observer.next_pass( sat )

        observer.date = tt # The satellite's peak (transit).
        sun = ephem.Sun()
        sun.compute( observer )
        sat.compute( observer )
        visible = sat.eclipsed is False and ephem.degrees( '-18' ) < sun.alt < ephem.degrees( '-6' )

        print( tr.datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ), visible )

        now = observer.date.datetime() + datetime.timedelta( minutes = 90 )
        count += 1


def getPassesSkyfield():
    observer = Topos('40.8939 N', '83.8917 W') #TODO Fix
    t0 = ts.utc( year, month, day )
    t1 = ts.utc(2014, 1, 24)
t, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=30.0)
for ti, event in zip(t, events):
    name = ('rise above 30°', 'culminate', 'set below 30°')[event]
    print(ti.utc_jpl(), name)
    
    
    
    observer = ephem.Observer()
    observer.lat = '-33.87'
    observer.long = '151.21'
    observer.elevation = 0
    observer.pressure = 0
    observer.date = now

    sat = ephem.readtle( "ISS (ZARYA)",
                         "1 25544U 98067A   20151.18025309  .00000222  00000-0  12062-4 0  9998",
                         "2 25544  51.6449  77.5932 0002744   5.7692 138.9633 15.49398616229222" )                 

    tr, azr, tt, altt, ts, azs = observer.next_pass( sat )

    observer.date = tt # The satellite's peak (transit).

    sun = ephem.Sun()
    sun.compute( observer )

    sat.compute( observer )
    visible = sat.eclipsed is False and ephem.degrees( '-18' ) < sun.alt < ephem.degrees( '-6' )

    return tr, visible


# getPassesPyEphem()
getPassesSkyfield()