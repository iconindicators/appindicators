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
#     https://en.wikipedia.org/wiki/Lists_of_stars
#     sudo pip3 install --upgrade pandas
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


#     Attributes calulated/provided by pyephem: 
#         RA/DEC 
#         ALT/AZ 
#         Phase/Illumination 
#         Distance to Earth/Sun 
#         rise/set 
#         moon phase and next phases 
#         solstice/equinox 
#         planetary moons RA/DEC/AZ/ALT/EarthVisible 
#         Saturn earth/sun tilt
#         Magnitude
#
#     Attributes which are calculated independently of pyephem:
#         Bright Limb
#         Tropical Sign
#         Constellation (not applicable to all stars)
#         moon/sun eclipse


import datetime, ephem, math, pytz

from ephem.cities import _city_data
from ephem.stars import stars

from skyfield import almanac
from skyfield.api import load, Star, Topos
from skyfield.data import hipparcos


# Must get a new observer after a rising/setting computation and before a calculations for a new body.    
def getPyephemObserver( dateTime, latitudeDD, longitudeDD, elevation ):
    observer = ephem.Observer()
    observer.lat = str( latitudeDD )
    observer.lon = str( longitudeDD )
    observer.elevation = elevation
    observer.date = ephem.Date( dateTime )
    return observer


TROPICAL_SIGNS = [ "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces" ]


# Code courtesy of Ignius Drake.
def getTropicalSign( body, ephemNow, now ):
    ( year, month, day ) = ephemNow.triple()

    timeDelta = datetime.timedelta( days = now.day, hours = now.hour, minutes = now.minute, seconds = now.second, microseconds = now.microsecond )
    dayWithFractionalHourMinuteSecond = timeDelta.total_seconds() / datetime.timedelta( days = 1 ).total_seconds()

    epochAdjustedNew = float( now.year ) + float( now.month ) / 12.0 + float( dayWithFractionalHourMinuteSecond ) / 365.242
    epochAdjusted = float( year ) + float( month ) / 12.0 + float( day ) / 365.242
    ephemNowDate = str( ephemNow ).split( " " )

    bodyCopy = body.copy() # Computing the tropical sign changes the body's date/time/epoch (shared by other downstream calculations), so make a copy of the body and use that.
    bodyCopy.compute( ephemNowDate[ 0 ], epoch = str( epochAdjusted ) )
    planetCoordinates = str( ephem.Ecliptic( bodyCopy ).lon ).split( ":" )

    if float( planetCoordinates[ 2 ] ) > 30:
        planetCoordinates[ 1 ] = str( int ( planetCoordinates[ 1 ] ) + 1 )

    tropicalSignDegree = int( planetCoordinates[ 0 ] ) % 30
    tropicalSignMinute = str( planetCoordinates[ 1 ] )
    tropicalSignIndex = int( planetCoordinates[ 0 ] ) / 30
    tropicalSignName = TROPICAL_SIGNS[ int( tropicalSignIndex ) ]

    return ( tropicalSignName, str( tropicalSignDegree ), tropicalSignMinute )


def getTropicalSignORIGINAL( body, ephemNow ):
    ( year, month, day ) = ephemNow.triple()
    epochAdjusted = float( year ) + float( month ) / 12.0 + float( day ) / 365.242
    ephemNowDate = str( ephemNow ).split( " " )

    bodyCopy = body.copy() # Computing the tropical sign changes the body's date/time/epoch (shared by other downstream calculations), so make a copy of the body and use that.
    bodyCopy.compute( ephemNowDate[ 0 ], epoch = str( epochAdjusted ) )
    planetCoordinates = str( ephem.Ecliptic( bodyCopy ).lon ).split( ":" )

    if float( planetCoordinates[ 2 ] ) > 30:
        planetCoordinates[ 1 ] = str( int ( planetCoordinates[ 1 ] ) + 1 )

    tropicalSignDegree = int( planetCoordinates[ 0 ] ) % 30
    tropicalSignMinute = str( planetCoordinates[ 1 ] )
    tropicalSignIndex = int( planetCoordinates[ 0 ] ) / 30
    tropicalSignName = TROPICAL_SIGNS[ int( tropicalSignIndex ) ]

    return ( tropicalSignName, str( tropicalSignDegree ), tropicalSignMinute )


    # Compute the bright limb angle (relative to zenith) between the sun and a planetary body.
    # Measured in degrees counter clockwise from a positive y axis.
    #
    # References:
    #  'Astronomical Algorithms' Second Edition by Jean Meeus (chapters 14 and 48).
    #  'Practical Astronomy with Your Calculator' by Peter Duffett-Smith (chapters 59 and 68).
    #  http://www.geoastro.de/moonlibration/ (pictures of moon are wrong but the data is correct).
    #  http://www.geoastro.de/SME/
    #  http://futureboy.us/fsp/moon.fsp
    #  http://www.timeanddate.com/moon/australia/sydney
    #
    # Other references...
    #  http://www.mat.uc.pt/~efemast/help/en/lua_fas.htm
    #  https://sites.google.com/site/astronomicalalgorithms
    #  http://stackoverflow.com/questions/13463965/pyephem-sidereal-time-gives-unexpected-result
    #  https://github.com/brandon-rhodes/pyephem/issues/24
    #  http://stackoverflow.com/questions/13314626/local-solar-time-function-from-utc-and-longitude/13425515#13425515
    #  http://astro.ukho.gov.uk/data/tn/naotn74.pdf
    def getZenithAngleOfBrightLimb( self, city, body ):
        sun = ephem.Sun( city )

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
        y = math.cos( sun.dec ) * math.sin( sun.ra - body.ra )
        x = math.cos( body.dec ) * math.sin( sun.dec ) - math.sin( body.dec ) * math.cos( sun.dec ) * math.cos( sun.ra - body.ra )
        positionAngleOfBrightLimb = math.atan2( y, x )

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
        hourAngle = city.sidereal_time() - body.ra
        y = math.sin( hourAngle )
        x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
        parallacticAngle = math.atan2( y, x )

        return math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )


def testPyephemPlanet( observer, planet ):
    # Must grab the az/alt BEFORE rise/set is computed as the values get clobbered.
    planet.compute( observer )
    result = str( planet.az ), str( planet.alt ), str( planet.ra ), str( planet.dec ), planet.earth_distance, planet.sun_distance, planet.phase, ephem.constellation( planet ), planet.mag

    try:
        rising =  str( observer.next_rising( planet ) )
        setting = str( observer.next_setting( planet ) )
        result += rising, setting

    except ephem.AlwaysUpError:
        result += "Always Up"

    except ephem.NeverUpError:
        result += "Never Up"

    if planet.name == "Saturn":
        result += str( planet.earth_tilt ), str( planet.sun_tilt )

    return result


def testPyephemSun( observer, sun ):
    return str( sun.az ), str( sun.alt ), str( sun.ra ), str( sun.dec ), sun.earth_distance, ephem.constellation( sun ), sun.mag, observer.next_rising( sun ).datetime(), observer.next_setting( sun ).datetime()


def testPyephem( utcNow, latitudeDD, longitudeDD, elevation ):
    print( "=======" )
    print( "PyEphem" )
    print( "=======" )
    print()

    print( utcNow )

    observer = getPyephemObserver( utcNow, latitudeDD, longitudeDD, elevation )
    print( testPyephemSun( observer, ephem.Sun( observer ) ) )

    observer = getPyephemObserver( utcNow, latitudeDD, longitudeDD, elevation )
    print( testPyephemPlanet( observer, ephem.Saturn( observer ) ) )

    observer = getPyephemObserver( utcNow, latitudeDD, longitudeDD, elevation )
    tropicalSignName, tropicalSignDegree, tropicalSignMinute = getTropicalSign( ephem.Saturn( observer ), ephem.Date( utcNow ), utcNow )
    print( tropicalSignName, tropicalSignDegree, tropicalSignMinute )

#     with load.open( hipparcos.URL ) as f:
#         stars = hipparcos.load_dataframe( f )

#     stars = stars[ stars[ "magnitude" ] <= 2 ]
#     stars = stars[ stars[ "magnitude" ] <= 4.3 ]
#     print( "After filtering, there are {} stars".format( len( stars ) ) )


def getSkyfieldObserver( latitudeDD, longitudeDD, elevation, earth ):
    return earth + Topos( latitude_degrees = latitudeDD, longitude_degrees = longitudeDD, elevation_m = elevation )


#TODO Add rise/set.
#TODO For Saturn, return the earth/sun tilts.
#TODO Add planetary moons with AZ/ATL/RA/DEC, earth visible, offset from planet.
def testSkyfieldPlanet( utcNow, ephemeris, observer, planet ):
    thePlanet = ephemeris[ planet ]
    apparent = observer.at( utcNow ).observe( thePlanet ).apparent()
    alt, az, earthDistance = apparent.altaz()
    ra, dec, sunDistance = ephemeris[ SKYFIELD_PLANET_SUN ].at( utcNow ).observe( thePlanet ).radec()
    ra, dec, earthDistance = apparent.radec()
    illumination = almanac.fraction_illuminated( ephemeris, planet, utcNow ) * 100
    return az.dms(), alt.dms(), ra.hms(), dec.dms(), earthDistance, sunDistance, illumination, "CON: TODO", "MAG: TODO https://github.com/skyfielders/python-skyfield/issues/210", "RISE: TODO", "SET: TODO"


def testSkyfieldSun( utcNow, ephemeris, observer ):
    sun = ephemeris[ SKYFIELD_PLANET_SUN ]
    apparent = observer.at( utcNow ).observe( sun ).apparent()
    alt, az, earthDistance = apparent.altaz()
    ra, dec, earthDistance = apparent.radec()
    return az.dms(), alt.dms(), ra.hms(), dec.dms(), earthDistance, "CON: TODO", "MAG: TODO https://github.com/skyfielders/python-skyfield/issues/210", "RISE: TODO", "SET: TODO"


def testSkyfield( utcNow, latitudeDD, longitudeDD, elevation ):
    print( "========" )
    print( "Skyfield" )
    print( "========" )
    print()

    utcNowSkyfield = load.timescale().utc( utcNow.replace( tzinfo = pytz.UTC ) )
    print( utcNowSkyfield.utc )

#TODO This ephemeris contains only planets...what about stars and planetary moons?
    ephemeris = load( "2017-2024.bsp" )

#     print( ephemeris[ "saturn barycenter" ].target_name )
#     for planet in ephemeris.names():
#         print( planet )
#         thing = ephemeris[ planet ]
#         print( thing.target, thing.target_name )

    observer = getSkyfieldObserver( latitudeDD, longitudeDD, elevation, ephemeris[ SKYFIELD_PLANET_EARTH ] )
    print( testSkyfieldSun( utcNowSkyfield, ephemeris, observer ) )

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

#TODO Migh need to install pytz
# https://rhodesmill.org/skyfield/time.html
#to localise the date/time.

utcNow = datetime.datetime.utcnow()
testPyephem( utcNow, latitudeDD, longitudeDD, elevation )
print()
print()
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