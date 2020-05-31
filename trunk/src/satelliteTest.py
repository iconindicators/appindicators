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


def getNextPass( now ):
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


visiblePasses = 0
now = datetime.datetime.utcnow()
while( visiblePasses < 11 ):
    riseTime, visible = getNextPass( now )
    if visible:
        visiblePasses += 1
        print( riseTime.datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ) )

    now = now + datetime.timedelta( minutes = 90 )