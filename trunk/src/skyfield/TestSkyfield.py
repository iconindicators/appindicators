#!/usr/bin/env python3


# Install (and upgrade to) latest skyfield: 
#     sudo pip3 install --upgrade skyfield


# https://github.com/skyfielders/python-skyfield
# 
# http://rhodesmill.org/skyfield/
# http://rhodesmill.org/skyfield/toc.html
# http://rhodesmill.org/skyfield/planets.html
# http://rhodesmill.org/skyfield/api.html
# 
# ftp://ssd.jpl.nasa.gov/pub/eph/planets/README.txt
# ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/ascii_format.txt
#
# Planets
#    https://github.com/skyfielders/python-skyfield/issues/123
#    ftp://ssd.jpl.nasa.gov/pub/eph/planets/bsp/de421.bsp
#    Download de421.bsp and run spkmerge as per the issue 123 to produce "2017-2024.bsp".
#
# Stars
#    http://astronomy.stackexchange.com/questions/13488/where-can-i-find-visualize-planets-stars-moons-etc-positions
#    http://astronomy.stackexchange.com/questions/14119/open-access-table-of-visible-stars-with-magnitude-coordinates-and-possibly-col
#    http://astronomy.stackexchange.com/questions/11334/any-freely-available-large-stellar-spectra-catalog
#    http://simbad.u-strasbg.fr/simbad/sim-id?Ident=BD%2B043561a
#    http://wwwadd.zah.uni-heidelberg.de/datenbanken/aricns/cnspages/4c01453.htm    


# TODO Compute the following to the same level of detail as indicator-lunar:
#    Moon
#    Sun
#    Saturn
#    Orion - Rigel
#    Comet
#    Satellite 


import datetime, ephem, pytz

import ephem
from ephem.cities import _city_data
from ephem.stars import stars

from skyfield.api import load, Star, Topos


def printPairs( *pairs ):
    for i in range( 0, len( pairs ), 2 ):
        print( pairs[ i ] + ": " + str( pairs[ i + 1 ] ) )


def getPyephemObserver( dateTime, latitudeDD, longitudeDD, elevation ):
    observer = ephem.Observer()
    observer.lon = longitudeDD
    observer.lat = latitudeDD
    observer.elevation = elevation
    observer.date = ephem.Date( dateTime )
    return observer


def testPyephemSaturn( utcNow, latitudeDecimal, longitudeDecimal, elevation ):
#TODO Need to get a new observer after the rising/setting computation and before the other calculations.  Perhaps log a bug or question at pyephem.    
    observer = getPyephemObserver( utcNow, latitudeDD, longitudeDD, elevation )
    saturn = ephem.Saturn( observer )
    rising = observer.next_rising( saturn )
    setting = observer.next_setting( saturn )
    saturn = ephem.Saturn( getPyephemObserver( utcNow, latitudeDD, longitudeDD, elevation ) )
    print( "Saturn:" )
    printPairs( "RA", saturn.ra, "DEC", saturn.dec, "AZ", saturn.az, "ALT", saturn.alt, "ED", saturn.earth_distance, "SD", saturn.sun_distance, "PH", saturn.phase, "CON", ephem.constellation( saturn ), "MAG", saturn.mag, "RISE", rising, "SET", setting )


def testPyephem( utcNow, latitudeDD, longitudeDD, elevation ):
    print( utcNow )
    testPyephemSaturn( utcNow, latitudeDD, longitudeDD, elevation )


def getSkyfieldObserver( latitudeDMS, longitudeDMS, elevation, earth ):
    return earth + Topos( latitudeDMS, longitudeDMS, elevation_m = elevation )


def testSkyfieldSaturn( utcNow, latitudeDMS, longitudeDMS, elevation ):
    planets = load( "2017-2024.bsp" ) # TODO Is there a canned list of planets?
    observer = getSkyfieldObserver( latitudeDMS, longitudeDMS, elevation, planets[ "earth" ] )
    saturn = planets[ "saturn barycenter" ]
    astrometric = observer.at( utcNow ).observe( saturn ).apparent()
    alt, az, d = astrometric.altaz()
    ra, dec, d = astrometric.radec()
    print( "Saturn:" )
    printPairs( "RA", ra, "DEC", dec, "AZ", az, "ALT", alt, "ED", d, "SD", "TODO", "PH", "TODO", "CON", "TODO", "MAG", "TODO", "RISE", "TODO", "SET", "TODO" )


def testSkyfield( utcNow, latitudeDMS, longitudeDMS, elevation ):
    utcNowSkyfield = load.timescale().utc( utcNow.replace( tzinfo = pytz.UTC ) )
    print( utcNowSkyfield.utc )
    testSkyfieldSaturn( utcNowSkyfield, latitudeDMS, longitudeDMS, elevation )


def getDMS( latitudeDD, longitudeDD ):
    latitudeDMS = str( abs( float( latitudeDD ) ) ) + " S" if float( latitudeDD ) < 0 else str( float( latitudeDD ) ) + " N"
    longitudeDMS = str( abs( float( longitudeDD ) ) ) + " W" if float( longitudeDD ) < 0 else str( float( longitudeDD ) ) + " E"
    return latitudeDMS, longitudeDMS


latitudeDD = "-33.8"
longitudeDD = "151.2"
elevation = 3.3

utcNow = datetime.datetime.utcnow()

testPyephem( utcNow, latitudeDD, longitudeDD, elevation )
print( "-   -   -   -   -   -" )
latitudeDMS, longitudeDMS = getDMS( latitudeDD, longitudeDD )
testSkyfield( utcNow, latitudeDMS, longitudeDMS, elevation )


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