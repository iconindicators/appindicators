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


from skyfield.api import load, Star

planets = load( "de421.bsp" )
earth = planets[ "earth" ]
moon = planets[ "moon" ]
mars = planets[ "mars" ]

timeScale = load.timescale()
now = timeScale.now()

home = earth.topos( "33.8599722 S", "151.2111111 E" )

apparent = home.at( now ).observe( mars ).apparent()

alt, az, distance = apparent.altaz()
print(alt.dstr())
print(az.dstr())
print(distance)


# print( "Mars astrometric:", home.at( now ).observe( mars ) )
# apparent = home.at( now ).observe (mars ).apparent()
# 
# 
# 
# 
# barnard = Star( ra_hours = ( 17, 57, 48.49803 ), dec_degrees = ( 4, 41, 36.2072 ) )
# 
# astrometric = earth.at( now ).observe( barnard )
# apparent = earth.at( now ).observe( barnard ).apparent()
# 
# astrometric = home.at( now ).observe( barnard )
# apparent = home.at( now ).observe( barnard ).apparent()

