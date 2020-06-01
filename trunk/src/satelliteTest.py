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


tle = [ "ISS (ZARYA)",
        "1 25544U 98067A   20151.18025309  .00000222  00000-0  12062-4 0  9998",
        "2 25544  51.6449  77.5932 0002744   5.7692 138.9633 15.49398616229222" ]                 


def getNextPassPyEphem( now ):
    observer = ephem.Observer()
    observer.lat = '-33.87'
    observer.long = '151.21'
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

    return tr, visible


def getVisiblePassesPyEphem():
    visiblePasses = 0
    now = datetime.datetime.utcnow()
    while( visiblePasses < 11 ):
        riseTime, visible = getNextPassPyEphem( now )
        if visible:
            visiblePasses += 1
            print( riseTime.datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ) )
    
        now = now + datetime.timedelta( minutes = 90 )


def getNextPassSkyfield( now ):
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


def getVisiblePassesSkyfield():
    eph = load('planets.bsp')
    ts = load.timescale()
    satellite = EarthSatellite( tle[ 1 ], tle[ 2 ], tle[ 0 ], ts)
    print( satellite )
    two_hours = ts.utc(2020, 6, 1, 0, range(0, 120, 20))
    sunlit = satellite.at(two_hours).is_sunlit(eph)
    print(sunlit)


    for ti, sunlit_i in zip(two_hours, sunlit):
        print('{}  {} is in {}'.format(
            ti.utc_strftime('%Y-%m-%d %H:%M'),
            satellite.name,
            'sunlight' if sunlit_i else 'shadow',
        ))

#     visiblePasses = 0
#     now = datetime.datetime.utcnow()
#     while( visiblePasses < 11 ):
#         riseTime, visible = getNextPassSkyfield( now )
#         if visible:
#             visiblePasses += 1
#             print( riseTime.datetime().replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None ) )
#     
#         now = now + datetime.timedelta( minutes = 90 )


# getVisiblePassesPyEphem()
getVisiblePassesSkyfield()