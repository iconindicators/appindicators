#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Download and save to same directory as script:
#    https://celestrak.com/NORAD/elements/visual.txt


from datetime import  timezone
from skyfield.api import EarthSatellite, load, wgs84
from skyfield import almanac
from urllib.request import urlopen
import datetime, ephem, skyfield


def getTLEData():
    tleData = { }
    data = urlopen( "file:./visual.txt" ).read().decode( "utf8" ).splitlines()
    for i in range( 0, len( data ), 3 ):
        name = data[ i ].strip()
        lineOne = data[ i + 1 ].strip()
        lineTwo = data[ i + 2 ].strip()
        number = lineOne[ 2 : 7 ]
        tleData[ number ] = [ name, lineOne, lineTwo ]

    return tleData


def calculateVisiblePassesPyEphem( utcNow, tle ):
    results = [ ]
    ephemNow = ephem.Date( utcNow )
    endDateTime = ephem.Date( ephemNow + ephem.hour * searchDurationInHours ) # Stop looking for passes 36 hours from now.
    currentDateTime = ephemNow
    while currentDateTime < endDateTime:
        city = getCity( currentDateTime )
        earthSatellite = ephem.readtle( tle[ 0 ], tle[ 1 ], tle[ 2 ] )
        earthSatellite.compute( city )
        try:
            nextPass = calculateNextSatellitePass( city, earthSatellite )
            if isSatellitePassValid( nextPass ) and isSatellitePassVisible( nextPass[ 2 ], earthSatellite ):
                riseSet = [ ]
                riseSet.append( nextPass[ 0 ].datetime() )
#                 riseSet.append( str( round( math.degrees( float( repr( nextPass[ 1 ] ) ) ) ) ) + "°" ) #TODO Degrees conversion...may be useful later.
                riseSet.append( repr( nextPass[ 1 ] ) )
                riseSet.append( nextPass[ 4 ].datetime() )
                riseSet.append( repr( nextPass[ 5 ] ) )

                results.append( riseSet )

        except ValueError:
            pass # Satellite is circumpolar so ignore as Skyfield does not distinguish such satellites.

        currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 15 ) # Look for the next pass starting after current set.

    return results


# Due to a change between PyEphem 3.7.6.0 and 3.7.7.0, need to check for passes differently.
#    https://rhodesmill.org/pyephem/CHANGELOG.html#version-3-7-7-0-2019-august-18
#    https://github.com/brandon-rhodes/pyephem/issues/63#issuecomment-144263243
def calculateNextSatellitePass( city, satellite ):
    version = int( ephem.__version__.split( '.' )[ 2 ] )
    if version <= 6:
        nextPass = city.next_pass( satellite )

    else:
        # Must set singlepass = False to avoid the new code in PyEphem (and so behave prior to this change).
        # It is possible a pass is too quick/low and an exception is thrown.
        # https://github.com/brandon-rhodes/pyephem/issues/164
        # https://github.com/brandon-rhodes/pyephem/pull/85/files
        nextPass = city.next_pass( satellite, singlepass = False )

    return nextPass


# Ensure:
#    The satellite pass is numerically valid.
#    Rise time exceeds transit time.
#    Transit time exceeds set time.
def isSatellitePassValid( satellitePass ):
    return satellitePass and \
           len( satellitePass ) == 6 and \
           satellitePass[ 0 ] and \
           satellitePass[ 1 ] and \
           satellitePass[ 2 ] and \
           satellitePass[ 3 ] and \
           satellitePass[ 4 ] and \
           satellitePass[ 5 ] and \
           satellitePass[ 2 ] > satellitePass[ 0 ] and \
           satellitePass[ 4 ] > satellitePass[ 2 ]


# Determine if a satellite pass is visible.
#
#    https://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
#    https://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
#    https://www.celestrak.com/columns/v03n01
def isSatellitePassVisible( passDateTime, satellite ):
    city = getCity( passDateTime )
    city.pressure = 0
    city.horizon = "-0:34"

    satellite.compute( city )
    sun = ephem.Sun()
    sun.compute( city )

    return satellite.eclipsed is False and \
           sun.alt > ephem.degrees( "-18" ) and \
           sun.alt < ephem.degrees( "-6" )


def getCity( date ):
    city = ephem.city( "London" ) # Put in a city name known to exist in PyEphem then doctor to the correct lat/long/elev.
    city.date = date
    city.lat = str( lat )
    city.lon = str( lon )
    city.elev = 0.0

    return city


def calculateVisiblePassesSkyfield( utcNow, tle ): 
    results = [ ]
    location = wgs84.latlon( lat, lon, elev )
    ephemerisPlanets = load( "de421.bsp" )
    timeScale = load.timescale( builtin = True )
    now = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
    nowPlusSearchDuration = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour + searchDurationInHours )
    earthSatellite = EarthSatellite( tle[ 1 ], tle[ 2 ], tle[ 0 ], timeScale )
    t, events = earthSatellite.find_events( location, now, nowPlusSearchDuration, altitude_degrees = 30.0 )
    riseTime = None
    culminateTimes = [ ] # Culminate may occur more than once, so collect them all.
    for ti, event in zip( t, events ):
        if event == 0: # Rise
            riseTime = ti

        elif event == 1: # Culminate
            culminateTimes.append( ti )

        else: # Set
            if riseTime is not None and len( culminateTimes ) > 0:
                for culmination in culminateTimes:
                    if earthSatellite.at( culmination ).is_sunlit( ephemerisPlanets ) and \
                       almanac.dark_twilight_day( ephemerisPlanets, location )( culmination ) < 4:
                        riseSet = [ ]
                        riseSet.append( riseTime.utc_datetime() )
                        alt, az, bodyDistance = ( earthSatellite - location ).at( riseTime ).altaz()
                        riseSet.append( str( az.radians ) )
                        riseSet.append( ti.utc_datetime() )
                        alt, az, bodyDistance = ( earthSatellite - location ).at( ti ).altaz()
                        riseSet.append( str( az.radians ) )

                        results.append( riseSet )
                        break

            riseTime = None
            culminateTimes = [ ]

    return results


def getSunriseSunset( utcNow ):
    timeScale = load.timescale( builtin = True )
    t, y = almanac.find_discrete( timeScale.from_datetime( utcNow ), 
                                  timeScale.from_datetime( utcNow + datetime.timedelta( hours = 24 ) ), 
                                  almanac.sunrise_sunset( load( "de421.bsp" ), wgs84.latlon( lat, lon, elev ) ) )

    if y[ 0 ] == 0:
        sunrise = t.utc_datetime()[ 1 ]
        sunset = t.utc_datetime()[ 0 ]

    else:
        sunrise = t.utc_datetime()[ 0 ]
        sunset = t.utc_datetime()[ 1 ]

    beforeSunrise = ( sunrise - datetime.timedelta( hours = sunriseSunsetWindowInHours ) )
    afterSunset = ( sunset + datetime.timedelta( hours = sunriseSunsetWindowInHours ) )

    return beforeSunrise, sunrise, sunset, afterSunset


def toDateTimeLocal( utcDateTime ): return utcDateTime.replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None )


def validatePasses( number, riseSets, beforeSunrise, sunrise, sunset, afterSunset, isSkyfield ):
    beforeSunrise = toDateTimeLocal( beforeSunrise ).time()
    sunrise = toDateTimeLocal( sunrise ).time()
    sunset = toDateTimeLocal( sunset ).time()
    afterSunset = toDateTimeLocal( afterSunset ).time()
    for riseSet in riseSets:
        satelliteRiseTimeLocal = toDateTimeLocal( riseSet[ 0 ] ).time()
        valid = ( satelliteRiseTimeLocal > beforeSunrise and satelliteRiseTimeLocal < sunrise ) or \
                ( satelliteRiseTimeLocal > sunset and satelliteRiseTimeLocal < afterSunset )

        if not valid:
            print( "Skyfield" if isSkyfield else "PyEphem", number, riseSet )


utcNow = datetime.datetime.strptime( "2021-03-04", "%Y-%m-%d" ).replace( tzinfo = timezone.utc )
lat = -33.8
lon = 151.2
elev = 0.0
searchDurationInHours = 48
sunriseSunsetWindowInHours = 2

print( "pyephem:", ephem.__version__ )
print( "skyfield:", skyfield.__version__ )

beforeSunrise, sunrise, sunset, afterSunset = getSunriseSunset( utcNow )
print( "Local before sunrise:", toDateTimeLocal( beforeSunrise ) )
print( "Local sunrise:", toDateTimeLocal( sunrise ) )
print( "Local sunset", toDateTimeLocal( sunset ) )
print( "Local after sunset", toDateTimeLocal( afterSunset ) )

tleData = getTLEData()
for number in tleData:
    riseSetsPyephem = calculateVisiblePassesPyEphem( utcNow, tleData[ number ] )
    validatePasses( number, riseSetsPyephem, beforeSunrise, sunrise, sunset, afterSunset, False )
    riseSetsSkyfield = calculateVisiblePassesSkyfield( utcNow, tleData[ number ] )
    validatePasses( number, riseSetsPyephem, beforeSunrise, sunrise, sunset, afterSunset, True )    