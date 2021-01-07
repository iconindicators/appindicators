#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from skyfield.api import EarthSatellite, load, wgs84
from skyfield import almanac
from urllib.request import urlopen
import datetime, ephem


DATA_TAG_ALTITUDE = "ALTITUDE"
DATA_TAG_AZIMUTH = "AZIMUTH"
DATA_TAG_RISE_AZIMUTH = "RISE AZIMUTH"
DATA_TAG_RISE_DATE_TIME = "RISE DATE TIME"
DATA_TAG_SET_AZIMUTH = "SET AZIMUTH"
DATA_TAG_SET_DATE_TIME = "SET DATE TIME"


def getTLEData():
    tleData = { }
#     data = urlopen( "https://celestrak.com/NORAD/elements/visual.txt" ).read().decode( "utf8" ).splitlines()
    data = urlopen( "file:///home/bernard/Desktop/visual.txt" ).read().decode( "utf8" ).splitlines()
    for i in range( 0, len( data ), 3 ):
        name = data[ i ].strip()
        lineOne = data[ i + 1 ].strip()
        lineTwo = data[ i + 2 ].strip()
        number = lineOne[ 2 : 7 ]
        tleData[ number ] = [ name, lineOne, lineTwo ]

    return tleData


def calculateSatellitesPyEphem( ephemNow, tleData, visible ):
    results = { }
    endDateTime = ephem.Date( ephemNow + ephem.hour * 36 ) # Stop looking for passes 36 hours from now.
    for number in tleData:
        tle = tleData[ number ]
        currentDateTime = ephemNow
        while currentDateTime < endDateTime:
            city = getCity( currentDateTime )
            earthSatellite = ephem.readtle( tle[ 0 ], tle[ 1 ], tle[ 2 ] )
            earthSatellite.compute( city )
            try:
                nextPass = calculateNextSatellitePass( city, earthSatellite )
                if isSatellitePassValid( nextPass ) and ( not visible or visible and isSatellitePassVisible( nextPass[ 2 ], earthSatellite ) ):
                    results[ ( number, DATA_TAG_RISE_DATE_TIME ) ] = toDateTimeLocal( nextPass[ 0 ].datetime() )
                    results[ ( number, DATA_TAG_RISE_AZIMUTH ) ] = repr( nextPass[ 1 ] )
                    results[ ( number, DATA_TAG_SET_DATE_TIME ) ] = toDateTimeLocal( nextPass[ 4 ].datetime() )
                    results[ ( number, DATA_TAG_SET_AZIMUTH ) ] = repr( nextPass[ 5 ] )
                    break

                else:
                    currentDateTime = ephem.Date( currentDateTime + ephem.minute * 60 ) # Look for the next pass.

            except ValueError:
                # Ignore for the purposes of comparison against Skyfield as Skyfield does not distinguish such satellites.
#                 if earthSatellite.circumpolar: # Satellite never rises/sets, so can only show current position.
#                     results[ number + ( DATA_TAG_AZIMUTH, ) ] = repr( earthSatellite.az )
#                     results[ number + ( DATA_TAG_ALTITUDE, ) ] = repr( earthSatellite.alt )
# 
#                 else:
#                     print( "Value error for satellite:", str( number ) )

                break

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


def calculateSatellitesSkyfield( utcNow, tleData, visible ): 
    results = { }
    location = wgs84.latlon( lat, lon, elev )
    ephemerisPlanets = load( "planets.bsp" )
    timeScale = load.timescale( builtin = True )
    now = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
    nowPlusThirtySixHours = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour + 36 )
    for number in tleData:
        tle = tleData[ number ]
        foundPass = False
        earthSatellite = EarthSatellite( tle[ 1 ], tle[ 2 ], tle[ 0 ], timeScale )
        t, events = earthSatellite.find_events( location, now, nowPlusThirtySixHours, altitude_degrees = 10.0 )
        riseTime = None
        culminateTimes = [ ] # Culminate may occur more than once, so collect them all.
        for ti, event in zip( t, events ):
            if event == 0: # Rise
                riseTime = ti

            elif event == 1: # Culminate
                culminateTimes.append( ti )

            else: # Set
                if riseTime is not None and len( culminateTimes ) > 0:
                    if visible:
                        for culmination in culminateTimes:
                            if earthSatellite.at( culmination ).is_sunlit( ephemerisPlanets ) and \
                               almanac.dark_twilight_day( ephemerisPlanets, location )( culmination ) < 4:
                                addToSkyfieldResults( results, number, riseTime, earthSatellite, location, ti )
                                foundPass = True
                                break

                        riseTime = None
                        culminateTimes = [ ]

                    else: # Non visible pass.
                        addToSkyfieldResults( results, number, riseTime, earthSatellite, location, ti )
                        foundPass = True

            if foundPass:
                break

    return results


def addToSkyfieldResults( results, number, riseTime, earthSatellite, location, setTime ):
    results[ ( number, DATA_TAG_RISE_DATE_TIME ) ] = toDateTimeLocal( riseTime.utc_datetime() )
    alt, az, bodyDistance = ( earthSatellite - location ).at( riseTime ).altaz()
    results[ ( number, DATA_TAG_RISE_AZIMUTH ) ] = str( az.radians )
    results[ ( number, DATA_TAG_SET_DATE_TIME ) ] = toDateTimeLocal( setTime.utc_datetime() )
    alt, az, bodyDistance = ( earthSatellite - location ).at( setTime ).altaz()
    results[ ( number, DATA_TAG_SET_AZIMUTH ) ] = str( az.radians )


def toDateTimeLocal( utcDateTime ): return utcDateTime.replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None )


def printRiseSet( pyephemResults, skyfieldResults ):
    for numberTag in pyephemResults:
        if numberTag[ 1 ] == DATA_TAG_RISE_DATE_TIME and numberTag in skyfieldResults:
            print( numberTag[ 0 ] )
            print( pyephemResults[ numberTag ], pyephemResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] )
            print( skyfieldResults[ numberTag ], skyfieldResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] )


def printOverlap( pyephemResults, skyfieldResults ):
    overlap = 0
    for numberTag in pyephemResults:
        if numberTag[ 1 ] == DATA_TAG_RISE_DATE_TIME and numberTag in skyfieldResults and \
           skyfieldResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] > pyephemResults[ numberTag ] and \
           skyfieldResults[ numberTag ] < pyephemResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ]:
            overlap += 1
#             print( pyephemResults[ ( numberTag[ 0 ], DATA_TAG_RISE_DATE_TIME ) ] )
#             print( pyephemResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] )
#             print()

    print( "Satellites:", int( len( skyfieldResults ) / 4 ) )
    print( "Overlap:", overlap )
    print( "Percentage overlap:", int( overlap / ( len( skyfieldResults ) / 4 ) * 100 ) )


def printOverlapNot( pyephemResults, skyfieldResults ):
    for numberTag in pyephemResults:
        if numberTag[ 1 ] == DATA_TAG_RISE_DATE_TIME and numberTag in skyfieldResults:
            if skyfieldResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] < pyephemResults[ numberTag ] or \
               skyfieldResults[ numberTag ] > pyephemResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ]:
                print( numberTag[ 0 ] )
                print( pyephemResults[ ( numberTag[ 0 ], DATA_TAG_RISE_DATE_TIME ) ], pyephemResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] )
                print( skyfieldResults[ ( numberTag[ 0 ], DATA_TAG_RISE_DATE_TIME ) ], skyfieldResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] )
                print()


def printMissing( pyephemResults, skyfieldResults ):
    missingInSkyfield = 0
    for numberTag in pyephemResults:
        if numberTag not in skyfieldResults:
            missingInSkyfield += 1

    missingInPyEphem = 0
    for numberTag in skyfieldResults:
        if numberTag not in pyephemResults:
            missingInPyEphem += 1

    print( "Missing in Skyfield:", missingInSkyfield )
    print( "Missing in PyEphem:", missingInPyEphem )


def printLongTransits( pyephemResults, skyfieldResults, maximumDurationInSeconds ):
    for numberTag in pyephemResults:
        if numberTag[ 1 ] == DATA_TAG_RISE_DATE_TIME:
            timeDelta = pyephemResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] - pyephemResults[ numberTag ]
            if timeDelta.seconds > maximumDurationInSeconds:
                print( numberTag[ 0 ] )
                print( '\t', pyephemResults[ numberTag ], pyephemResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] )
                print( skyfieldResults[ numberTag ], skyfieldResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] )

    for numberTag in skyfieldResults:
        if numberTag[ 1 ] == DATA_TAG_RISE_DATE_TIME:
            timeDelta = skyfieldResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] - skyfieldResults[ numberTag ]
            if timeDelta.seconds > maximumDurationInSeconds:
                print( numberTag[ 0 ] )
                print( pyephemResults[ numberTag ], pyephemResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] )
                print( '\t', skyfieldResults[ numberTag ], skyfieldResults[ ( numberTag[ 0 ], DATA_TAG_SET_DATE_TIME ) ] )


lat = -33.8
lon = 151.2
elev = 0.0
visible = True

tleData = getTLEData()
utcNow = datetime.datetime.utcnow()

pyephemResults = calculateSatellitesPyEphem( ephem.Date( utcNow ), tleData, visible )
skyfieldResults = calculateSatellitesSkyfield( utcNow, tleData, visible )
# printOverlap( pyephemResults, skyfieldResults )
printOverlapNot( pyephemResults, skyfieldResults )
# printMissing( pyephemResults, skyfieldResults )
# printLongTransits( pyephemResults, skyfieldResults, 60 * 20 )
# printRiseSet( pyephemResults, skyfieldResults )

#TODO Look at where there is no overlap and see if all those passes are at sunrise or sunset.

#TODO Look at the overlaps and ensure they are at either sunrise or sunset.



