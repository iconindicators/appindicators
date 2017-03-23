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
#     https://github.com/skyfielders/python-skyfield/issues/123
#
# Stars
#     http://astronomy.stackexchange.com/questions/13488/where-can-i-find-visualize-planets-stars-moons-etc-positions
#     http://astronomy.stackexchange.com/questions/14119/open-access-table-of-visible-stars-with-magnitude-coordinates-and-possibly-col
#     http://astronomy.stackexchange.com/questions/11334/any-freely-available-large-stellar-spectra-catalog
#     http://simbad.u-strasbg.fr/simbad/sim-id?Ident=BD%2B043561a
#     http://wwwadd.zah.uni-heidelberg.de/datenbanken/aricns/cnspages/4c01453.htm    


# TODO Compute the following to the same level of detail as indicator-lunar:
#     Moon
#     Sun
#     Saturn
#     Orion - Rigel
#     Comet
#     Satellite 


import datetime, ephem, pytz

import ephem
from ephem.cities import _city_data
from ephem.stars import stars

from skyfield.api import load, Star


def getPyephemObserver( dateTime, latitudeDecimal, longitudeDecimal, elevation ):
    observer = ephem.Observer()
    observer.lon = longitudeDecimal
    observer.lat = latitudeDecimal
    observer.elevation = elevation
    observer.date = ephem.Date( dateTime )
    return observer


def testPyephem( dateTime, latitudeDecimal, longitudeDecimal, elevation ):
    print( dateTime )

#TODO Need to get a new observer after the risiing/setting computation and before the other calculations.  Perhaps log a bug or question at pyephem.    
    observer = getPyephemObserver( dateTime, latitudeDecimal, longitudeDecimal, elevation )
    saturn = ephem.Saturn( observer )
    rising = observer.next_rising( saturn )
    setting = observer.next_setting( saturn )

    saturn = ephem.Saturn( getPyephemObserver( dateTime, latitudeDecimal, longitudeDecimal, elevation ) )
    print( saturn.ra, saturn.dec, saturn.az, saturn.alt, saturn.earth_distance, saturn.sun_distance, saturn.phase, ephem.constellation( saturn ), saturn.mag, rising, setting, sep = "\n" )


def getSkyfieldObserver( latitudeDecimal, longitudeDecimal, elevation, earth ):
    latitude = str( abs( float( latitudeDecimal ) ) ) + " S" if float( latitudeDecimal ) < 0 else str( float( latitudeDecimal ) ) + " N"
    longitude = str( abs( float( longitudeDecimal ) ) ) + " W" if float( longitudeDecimal ) < 0 else str( float( longitudeDecimal ) ) + " E"
    return earth.topos( latitude, longitude, elevation_m = elevation )


def testSkyfield( dateTime, latitudeDecimal, longitudeDecimal, elevation ):
    now = load.timescale().utc( dateTime.replace( tzinfo = pytz.UTC ) )
    print( now.utc )

    planets = load( "2017-2024.bsp" ) # TODO Is there a canned list of planets?
    observer = getSkyfieldObserver( latitudeDecimal, longitudeDecimal, elevation, planets[ "earth" ] )
    saturn = planets[ "saturn barycenter" ]
    astrometric = observer.at( now ).observe( saturn ).apparent()
    alt, az, d = astrometric.altaz()
    ra, dec, d = astrometric.radec()
    print( ra, dec, az, alt, d, "TODO: sun distance", "TODO: phase/illumination", "TODO: constellation", "TODO: magnitude", "TODO: rising", "TODO: setting", sep = "\n" )


latitudeDecimal = "-33.8"
longitudeDecimal = "151.2"
elevation = 3.3
now = datetime.datetime.utcnow()

testPyephem( now, latitudeDecimal, longitudeDecimal, elevation )
print( "-   -   -   -   -   -" )
testSkyfield( now, latitudeDecimal, longitudeDecimal, elevation )


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