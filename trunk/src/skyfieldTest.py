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
mars = planets[ "mars" ]

timeScale = load.timescale()
now = timeScale.now()
barycentric = mars.at( now )

astrometric = earth.at( now ).observe( mars )
apparent = earth.at( now ).observe( mars ).apparent()

boston = earth.topos( "42.3583 N", "71.0603 W" )
astrometric = boston.at( now ).observe( mars )
apparent = boston.at( now ).observe (mars ).apparent()

barnard = Star( ra_hours = ( 17, 57, 48.49803 ), dec_degrees = ( 4, 41, 36.2072 ) )

astrometric = earth.at( now ).observe( barnard )
apparent = earth.at( now ).observe( barnard ).apparent()

astrometric = boston.at( now ).observe( barnard )
apparent = boston.at( now ).observe( barnard ).apparent()

t = timeScale.utc( 1980, 1, 1 )
print( earth.at( t ).position.au )
print( mars.at( t ).position.au )