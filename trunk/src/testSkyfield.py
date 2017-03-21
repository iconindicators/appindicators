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
print( latitudeDecimal, longitudeDecimal )

now = ephem.now()
print( now )

observer = ephem.city( cityName )
observer.date = now
mars = ephem.Mars( observer )
print( mars.ra, mars.dec, mars.az, mars.alt )

observer = ephem.city( cityName )
observer.date = now
mars = ephem.Mars( observer )
#print( observer.next_rising( mars ).datetime(), observer.next_setting( mars ).datetime() )


print( "- - - - - - " )


from skyfield.api import load


def toLatitudeLongitude( latitudeDecimal, longitudeDecimal ):
    return \
        str( abs( float( latitudeDecimal ) ) ) + " S" if float( latitudeDecimal ) < 0 else str( float( latitudeDecimal ) ) + " N", \
        str( abs( float( longitudeDecimal ) ) ) + " W" if float( longitudeDecimal ) < 0 else str( float( longitudeDecimal ) ) + " E"


planets = load( "de421.bsp" )
earth = planets[ "earth" ]

latitude, longitude = toLatitudeLongitude( latitudeDecimal, longitudeDecimal )
print( latitude, longitude )

home = earth.topos( latitude, longitude ) # TODO Elevation?

timeScale = load.timescale()
print( now.datetime() )
timeScaleNow = timeScale.utc( now.datetime().replace( tzinfo = pytz.UTC ) )

mars = planets[ "mars" ]
astrometric = home.at( timeScaleNow ).observe( mars )
alt, az, d = astrometric.apparent().altaz()
ra, dec, d = astrometric.apparent().radec()
print( ra, dec, az, alt )