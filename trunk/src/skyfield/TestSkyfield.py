#!/usr/bin/env python3

# Use
#    https://ssd.jpl.nasa.gov/horizons.cgi
# to verify results.


# Install (and upgrade to) latest skyfield: 
#     sudo apt-get install python3-pip
#     sudo pip3 install --upgrade skyfield


# https://github.com/skyfielders/python-skyfield
# 
# http://rhodesmill.org/skyfield/
#
# ftp://ssd.jpl.nasa.gov/pub/eph/planets/README.txt
# ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/ascii_format.txt
#
# Planets
#     https://github.com/skyfielders/python-skyfield/issues/123
#     ftp://ssd.jpl.nasa.gov/pub/eph/planets/bsp/de421.bsp
#     Download de421.bsp and run spkmerge as per the issue 123 to produce "2017-2024.bsp".
#
# Stars
#     PyEphem only contains 94 stars.
#     http://www.skyandtelescope.com/astronomy-resources/how-many-stars-night-sky-09172014/
#     http://astronomy.stackexchange.com/questions/13488/where-can-i-find-visualize-planets-stars-moons-etc-positions
#     http://astronomy.stackexchange.com/questions/14119/open-access-table-of-visible-stars-with-magnitude-coordinates-and-possibly-col
#     http://astronomy.stackexchange.com/questions/11334/any-freely-available-large-stellar-spectra-catalog
#     http://simbad.u-strasbg.fr/simbad/sim-id?Ident=BD%2B043561a
#     http://wwwadd.zah.uni-heidelberg.de/datenbanken/aricns/cnspages/4c01453.htm    
#
# Other stuff...
#     https://github.com/oefe/astronomy-notebooks
#     https://github.com/skyfielders/python-skyfield/issues/35
#     https://github.com/skyfielders/python-skyfield/blob/master/skyfield/starlib.py
#     https://github.com/skyfielders/python-skyfield/blob/master/skyfield/data/hipparcos.py


# TODO Compute the following to the same level of detail as indicator-lunar:
#     Moon
#     Sun
#     Saturn + Moons
#     Orion - Rigel
#     Comet
#     Satellite 


#     Attributes which change: 
#         RA/DEC 
#         ALT/AZ 
#         Phase/Illumination 
#         Distance to Earth/Sun 
#         rise/set 
#         moon phase and next phases 
#         solstice/equinox 
#         planetary moons RA/DEC/AZ/ALT/EarthVisible 
#         Saturn earth/sun tilt
#     
#     Attributes which are relatively static:
#         Magnitude
#
#     Attributes which are calculated outside of engine:
#         Bright Limb
#         Tropical Sign
#         Constellation (not applicable to all stars)
#         moon/sun eclipse


import datetime, ephem, pytz

from ephem.cities import _city_data
from ephem.stars import stars

from skyfield import almanac
from skyfield.api import load, Star, Topos


def printPairs( pairs ):
    for i in range( 0, len( pairs ), 2 ):
        print( "\t" + pairs[ i ] + ": " + str( pairs[ i + 1 ] ) )

    print()


# Must get a new observer after a rising/setting computation and before a calculations for a new body.    
def getPyephemObserver( dateTime, latitudeDD, longitudeDD, elevation ):
    observer = ephem.Observer()
    observer.lat = str( latitudeDD )
    observer.lon = str( longitudeDD )
    observer.elevation = elevation
    observer.date = ephem.Date( dateTime )
    return observer


def testPyephemSaturn( utcNow, latitudeDD, longitudeDD, elevation ):
    observer = getPyephemObserver( utcNow, latitudeDD, longitudeDD, elevation )
    saturn = ephem.Saturn( observer )

    # Must grab the az/alt BEFORE rise/set is computed as the values get clobbered.
    pairs = [ "AZ", saturn.az, "ALT", saturn.alt, "RA", saturn.ra, "DEC", saturn.dec, "ED", saturn.earth_distance, "SD", saturn.sun_distance, "PH/IL", saturn.phase, "CON", ephem.constellation( saturn ), "MAG", saturn.mag ]

    try:
        rising = observer.next_rising( saturn )
        setting = observer.next_setting( saturn )
        pairs.extend( ( "RISE", rising, "SET", setting ) )

    except ephem.AlwaysUpError:
        pairs.extend( ( "RISE/SET", "Always Up" ) )

    except ephem.NeverUpError:
        pairs.extend( ( "RISE/SET", "Never Up" ) )

    pairs.extend( ( "ET", saturn.earth_tilt, "ST", saturn.sun_tilt ) )
    print( "Saturn:" )
    printPairs( pairs )


def testPyephem( utcNow, latitudeDD, longitudeDD, elevation ):
    print( "=======" )
    print( "PyEphem" )
    print( "=======\n" )
    print( utcNow, "\n" )
    testPyephemSaturn( utcNow, latitudeDD, longitudeDD, elevation )


def getSkyfieldObserver( latitudeDD, longitudeDD, elevation, earth ):
    return earth + Topos( latitude_degrees = latitudeDD, longitude_degrees = longitudeDD, elevation_m = elevation )


#TODO Add rise/set.
#TODO For Saturn, return the earth/sun tilts.
#TODO Add planetery moons with AZ/ATL/RA/DEC, earth visible, offset from planet.
def testSkyfieldPlanet( utcNow, ephemeris, observer, planet ):
    thePlanet = ephemeris[ planet ]
    apparent = observer.at( utcNow ).observe( thePlanet ).apparent()
    alt, az, earthDistance = apparent.altaz()
    ra, dec, sunDistance = ephemeris[ SKYFIELD_PLANET_SUN ].at( utcNow ).observe( thePlanet ).radec()
    ra, dec, earthDistance = apparent.radec()
    illumination = almanac.fraction_illuminated( ephemeris, planet, utcNow ) * 100
    return az.dms(), alt.dms(), ra.hms(), dec.dms(), earthDistance, sunDistance, illumination, "CON: TODO", "MAG: TODO https://github.com/skyfielders/python-skyfield/issues/210", "RISE: TODO", "SET: TODO"


def testSkyfieldSaturn( utcNow, ephemeris, latitudeDD, longitudeDD, elevation ):
    observer = getSkyfieldObserver( latitudeDD, longitudeDD, elevation, ephemeris[ "earth" ] )
    saturn = ephemeris[ "saturn barycenter" ]
    apparent = observer.at( utcNow ).observe( saturn ).apparent()
    alt, az, earthDistance = apparent.altaz()
    ra, dec, sunDistance = ephemeris[ "sun" ].at( utcNow ).observe( ephemeris[ "saturn barycenter" ] ).radec()
    ra, dec, earthDistance = apparent.radec()
    illumination = almanac.fraction_illuminated( ephemeris, "saturn barycenter", utcNow ) * 100

    print( "Saturn:" )
    printPairs( [ "AZ", az.dms(), "ALT", alt.dms(), "RA", ra.hms(), "DEC", dec.dms(), "ED", earthDistance, "SD", sunDistance, "PH/IL", illumination, "CON", "TODO", "MAG", "TODO https://github.com/skyfielders/python-skyfield/issues/210", "RISE", "TODO", "SET", "TODO", "ET", "TODO", "ST", "TODO" ] )


def testSkyfield( utcNow, latitudeDD, longitudeDD, elevation ):
    utcNowSkyfield = load.timescale().utc( utcNow.replace( tzinfo = pytz.UTC ) )

    print( "========" )
    print( "Skyfield" )
    print( "========\n" )
    print( utcNowSkyfield.utc, "\n" )

#TODO This ephemeris contains only planets...what about stars and planetary moons?
    ephemeris = load( "2017-2024.bsp" )

    testSkyfieldSaturn( utcNowSkyfield, ephemeris, latitudeDD, longitudeDD, elevation )
#     print( ephemeris[ "saturn barycenter" ].target_name )

#     for planet in ephemeris.names():
#         print( planet )
#         thing = ephemeris[ planet ]
#         print( thing.target, thing.target_name )

    observer = getSkyfieldObserver( latitudeDD, longitudeDD, elevation, ephemeris[ SKYFIELD_PLANET_EARTH ] )
    print( testSkyfieldPlanet( utcNowSkyfield, ephemeris, observer, SKYFIELD_PLANET_SATURN ) )


# def getPlanetFromEphemeris( ephemeris ):
#     for code in ephemeris.names():
        

SKYFIELD_PLANET_EARTH = "earth"
SKYFIELD_PLANET_SATURN = "saturn barycenter"
SKYFIELD_PLANET_SUN = "sun"

latitudeDD = -33.8
longitudeDD = 151.2
elevation = 100

utcNow = datetime.datetime.utcnow()
# testPyephem( utcNow, str( latitudeDD ), str( longitudeDD ), elevation )
testPyephem( utcNow, latitudeDD, longitudeDD, elevation )
testSkyfield( utcNow, latitudeDD, longitudeDD, elevation )


# barnard = Star( ra_hours = ( 17, 57, 48.49803 ), dec_degrees = ( 4, 41, 36.2072 ) )
# ts = load.timescale()
# t = ts.now()
# astrometric = observer.at( timeScaleNow ).observe( barnard )
# ra, dec, distance = astrometric.apparent().radec()
# az, az, distance = astrometric.apparent().altaz()
# print(ra, dec, az, alt )


# observer = ephem.city( cityName )
# observer.date = now
# starName = "Cebalrai"
# star = ephem.star( starName )
# star.compute( observer )
# print( star.ra, star.dec, star.az, star.alt )