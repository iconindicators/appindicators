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


import pytz, ephem
from ephem.cities import _city_data
from ephem.stars import stars


cityName = "Sydney"
latitudeDecimal = _city_data.get( cityName )[ 0 ]
longitudeDecimal = _city_data.get( cityName )[ 1 ]
elevation = _city_data.get( cityName )[ 2 ]
print( latitudeDecimal, longitudeDecimal, elevation )

now = ephem.now()
print( now )

observer = ephem.city( cityName )
observer.date = now
mars = ephem.Mars( observer )
print( mars.ra, mars.dec, mars.az, mars.alt )
#print( observer.next_rising( mars ).datetime(), observer.next_setting( mars ).datetime() ) #TODO

observer = ephem.city( cityName )
observer.date = now
starName = "Cebalrai"
star = ephem.star( starName )
star.compute( observer )
print( star.ra, star.dec, star.az, star.alt )


print( "- - - - - - " )


from skyfield.api import load, Star


def toLatitudeLongitude( latitudeDecimal, longitudeDecimal ):
    return \
        str( abs( float( latitudeDecimal ) ) ) + " S" if float( latitudeDecimal ) < 0 else str( float( latitudeDecimal ) ) + " N", \
        str( abs( float( longitudeDecimal ) ) ) + " W" if float( longitudeDecimal ) < 0 else str( float( longitudeDecimal ) ) + " E"


planets = load( "2017-2024.bsp" )
# planets = load( "de421.bsp" )
earth = planets[ "earth" ]

latitude, longitude = toLatitudeLongitude( latitudeDecimal, longitudeDecimal )
print( latitude, longitude )

observer = earth.topos( latitude, longitude, elevation_m = elevation )

timeScale = load.timescale()
print( now.datetime() )
timeScaleNow = timeScale.utc( now.datetime().replace( tzinfo = pytz.UTC ) )

mars = planets[ "mars" ]
astrometric = observer.at( timeScaleNow ).observe( mars )
alt, az, d = astrometric.apparent().altaz()
ra, dec, d = astrometric.apparent().radec()
print( ra, dec, az, alt )


barnard = Star( ra_hours = ( 17, 57, 48.49803 ), dec_degrees = ( 4, 41, 36.2072 ) )
ts = load.timescale()
t = ts.now()
astrometric = observer.at( timeScaleNow ).observe( barnard )
ra, dec, distance = astrometric.apparent().radec()
az, az, distance = astrometric.apparent().altaz()
print(ra, dec, az, alt )