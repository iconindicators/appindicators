#!/usr/bin/env python3

# Use
#    https://ssd.jpl.nasa.gov/horizons.cgi
# to verify results.


# Install (and upgrade to) latest skyfield: 
#     sudo apt-get install python3-pip
#     sudo pip3 install --upgrade skyfield
#     sudo pip install --upgrade pytz

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



# https://stackoverflow.com/questions/28867022/python-convert-au-to-km


import datetime, ephem, math, pytz

from ephem.cities import _city_data
from ephem.stars import stars

from skyfield import almanac, positionlib
from skyfield.api import load, Star, Topos
from skyfield.data import hipparcos


# Must get a new observer after a rising/setting computation and before a calculations for a new body.    
def getPyephemObserver( now, latitudeDD, longitudeDD, elevation ):
    observer = ephem.Observer()
    observer.lat = str( latitudeDD )
    observer.lon = str( longitudeDD )
    observer.elevation = elevation
    observer.date = ephem.Date( now )
    return observer


TROPICAL_SIGNS = [ "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces" ]


# Code courtesy of Ignius Drake.
def getTropicalSign( body, ephemNow, now ):

    ( year, month, day ) = ephemNow.triple()
    timeDelta = datetime.timedelta( days = now.day, hours = now.hour, minutes = now.minute, seconds = now.second, microseconds = now.microsecond )
    yearWithFractionalDateTime = timeDelta.total_seconds() / datetime.timedelta( days = 1 ).total_seconds()

    epochAdjustedNew = float( now.year ) + float( now.month ) / 12.0 + float( yearWithFractionalDateTime ) / 365.242

    x = load.timescale().utc( now.year, month = now.month, day = yearWithFractionalDateTime )

    epochAdjusted = float( year ) + float( month ) / 12.0 + float( day ) / 365.242
    ephemNowDate = str( ephemNow ).split( " " )

    bodyCopy = body.copy() # Computing the tropical sign changes the body's date/time/epoch (shared by other downstream calculations), so make a copy of the body and use that.
    bodyCopy.compute( ephemNowDate[ 0 ], epoch = str( epochAdjusted ) )
    planetCoordinates = str( ephem.Ecliptic( bodyCopy ).lon ).split( ":" )

    ephemeris = load( "2017-2024.bsp" )
    observer = getSkyfieldObserver( latitudeDD, longitudeDD, elevation, ephemeris[ SKYFIELD_PLANET_EARTH ] )
    thePlanet = ephemeris[ SKYFIELD_PLANET_SATURN ]
    timescale = load.timescale()
    y = observer.at( timescale.utc( utcNow.replace( tzinfo = pytz.UTC ) ) ).observe( thePlanet ).apparent().ecliptic_latlon( epoch = x )


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


def getZenithAngleOfBrightLimbNEW( city, body, sunRA, sunDec, bodyRA, bodyDec, observerLatitude, observerSiderealTime ):
    sun = ephem.Sun( city )

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
    y = math.cos( sun.dec ) * math.sin( sun.ra - body.ra )
    x = math.cos( body.dec ) * math.sin( sun.dec ) - math.sin( body.dec ) * math.cos( sun.dec ) * math.cos( sun.ra - body.ra )
    positionAngleOfBrightLimb = math.atan2( y, x )

    yNEW = math.cos( sunDec ) * math.sin( sunRA - bodyRA )
    xNEW = math.cos( bodyDec ) * math.sin( sunDec ) - math.sin( bodyDec ) * math.cos( sunDec ) * math.cos( sunRA - bodyRA )
    positionAngleOfBrightLimbNEW = math.atan2( yNEW, xNEW )

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
    citySiderealTime = city.sidereal_time()
    c = math.radians( citySiderealTime )
    bodyRAinRadians = math.radians( body.ra )
    hourAngle = citySiderealTime - body.ra
    y = math.sin( hourAngle )
    x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
    parallacticAngle = math.atan2( y, x )

    hourAngleNEW = observerSiderealTime - bodyRA
    yNEW = math.sin( hourAngleNEW )
    xNEW = math.tan( observerLatitude ) * math.cos( bodyDec ) - math.sin( bodyDec ) * math.cos( hourAngleNEW )
    parallacticAngleNEW = math.atan2( yNEW, xNEW )

    orig = math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )
    new = math.degrees( ( positionAngleOfBrightLimbNEW - parallacticAngleNEW ) % ( 2.0 * math.pi ) )
    return math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )


def testPyephemPlanet( observer, planet ):
    planet.compute( observer )

    # Must retrieve the az/alt/ra/dec BEFORE rise/set is computed as the values get clobbered.
    result = \
        "Illumination: " + str( planet.phase ), \
        "Constellation: " + str( ephem.constellation( planet ) ), \
        "Magnitude: " + str( planet.mag ), \
        "Tropical Sign: TODO", \
        "Distance to Earth: " + str( planet.earth_distance ), \
        "Distance to Sun: " + str( planet.sun_distance ), \
        "Bright Limb: " + str( "TODO" ), \
        "Azimuth: " + str( planet.az ), \
        "Altitude: " + str( planet.alt ), \
        "Right Ascension: " + str( planet.ra ), \
        "Declination: " + str( planet.dec )

    try:
        result += \
            "Rise: " + str( observer.next_rising( planet ) ), \
            "Set: " + str( observer.next_setting( planet ) )

    except ephem.AlwaysUpError:
        result += "Rise/Set: Always Up"

    except ephem.NeverUpError:
        result += "Rise/Set: Never Up"

#TODO
#     if planet.name == "Saturn":
#         result += str( planet.earth_tilt ), str( planet.sun_tilt )

    return result


def testPyephemSun( now, observer ):
    sun = ephem.Sun( observer )

    return \
        "Constellation: " + str( ephem.constellation( sun ) ), \
        "Magnitude: " + str( sun.mag ), \
        "Tropical Sign: TODO", \
        "Distance to Earth: " + str( sun.earth_distance ), \
        "Azimuth: " + str( sun.az ), \
        "Altitude: " + str( sun.alt ), \
        "Right Ascension: " + str( sun.ra ), \
        "Declination: " + str( sun.dec ), \
        "Dawn: TODO", \
        "Rise: " + str( observer.next_rising( sun ).datetime() ), \
        "Set: " + str( observer.next_setting( sun ).datetime() ), \
        "Dusk: TODO", \
        "Solstice: " + str( ephem.next_solstice( now ) ), \
        "Equinox: " + str( ephem.next_equinox( now ) ), \
        "Eclipse Date/Time, Latitude/Longitude, Type: TODO"


def testPyephem( now, latitudeDD, longitudeDD, elevation ):
    print( "=======" )
    print( "PyEphem" )
    print( "=======" )
    print()

#     madrid = ephem.city('Madrid')
#     madrid.date = '1978/10/3 11:32'
#     print( "Madrid", madrid.sidereal_time())


#     madrid = ephem.city('Sydney')
#     madrid.date = '1978/10/3 11:32'
#     print( "Sydney", madrid.sidereal_time())


#     ts = load.timescale()
#     t = ts.utc(1978, 10, 3,11,32, 0)
#     st = t.gmst
#     print( st )

#     print( load.timescale().now().gmst )

#     sss = ts.utc( utcNow.replace( tzinfo = pytz.UTC ) )
#     sss = ts.utc( datetime.datetime.utcnow() )
#     print( sss.gmst )

#     import sys
#     sys.exit()

#     ephemeris = load( "2017-2024.bsp" )
#     sun = ephemeris[ SKYFIELD_PLANET_SUN ]

#     observer = getSkyfieldObserver( latitudeDD, longitudeDD, elevation, ephemeris[ SKYFIELD_PLANET_EARTH ] )
#     timescale = load.timescale()
#     utcNowSkyfield = timescale.utc( utcNow.replace( tzinfo = pytz.UTC ) )
#     apparent = observer.at( utcNowSkyfield ).observe( sun ).apparent()
#     alt, az, earthDistance = apparent.altaz()
#     sunRA, sunDEC, earthDistance = apparent.radec()

#     thePlanet = ephemeris[ SKYFIELD_PLANET_SATURN ]
#     apparent = observer.at( utcNowSkyfield ).observe( thePlanet ).apparent()
#     ra, dec, earthDistance = apparent.radec()

#     observerSiderealTime = utcNowSkyfield.gmst




    observer = getPyephemObserver( now, latitudeDD, longitudeDD, elevation )
    print( testPyephemSun( now, observer ) )

    observer = getPyephemObserver( now, latitudeDD, longitudeDD, elevation )
    print( testPyephemPlanet( observer, ephem.Saturn( observer ) ) )

#     observer = getPyephemObserver( utcNow, latitudeDD, longitudeDD, elevation )
#     tropicalSignName, tropicalSignDegree, tropicalSignMinute = getTropicalSign( ephem.Saturn( observer ), ephem.Date( utcNow ), utcNow )
#     print( tropicalSignName, tropicalSignDegree, tropicalSignMinute )

#     observer = getPyephemObserver( now, latitudeDD, longitudeDD, elevation )
#     city = ephem.city( "Sydney" )
#     city.date = now
#     sun = ephem.Sun( observer )
#     saturn = ephem.Saturn( observer )

    
#     ephemeris = load( "2017-2024.bsp" )
#     sun = ephemeris[ SKYFIELD_PLANET_SUN ]

#     observer = getSkyfieldObserver( latitudeDD, longitudeDD, elevation, ephemeris[ SKYFIELD_PLANET_EARTH ] )
#     timescale = load.timescale()
#     utcNowSkyfield = timescale.utc( utcNow.replace( tzinfo = pytz.UTC ) )
#     apparent = observer.at( utcNowSkyfield ).observe( sun ).apparent()
#     alt, az, earthDistance = apparent.altaz()
#     sunRA, sunDEC, earthDistance = apparent.radec()
    
#     thePlanet = ephemeris[ SKYFIELD_PLANET_SATURN ]
#     apparent = observer.at( utcNowSkyfield ).observe( thePlanet ).apparent()
#     ra, dec, earthDistance = apparent.radec()

#     observerSiderealTime = utcNowSkyfield.gmst
#     bl = getZenithAngleOfBrightLimbNEW( city, saturn, sunRA.radians, sunDEC.radians, ra.radians, dec.radians, math.radians( latitudeDD ), observerSiderealTime )
#     print()


#     with load.open( hipparcos.URL ) as f:
#         stars = hipparcos.load_dataframe( f )

#     stars = stars[ stars[ "magnitude" ] <= 2 ]
#     stars = stars[ stars[ "magnitude" ] <= 4.3 ]
#     print( "After filtering, there are {} stars".format( len( stars ) ) )


def getSkyfieldObserver( latitudeDD, longitudeDD, elevation, earth ):
    return earth + Topos( latitude_degrees = latitudeDD, longitude_degrees = longitudeDD, elevation_m = elevation )


def getSkyfieldTopos( latitudeDD, longitudeDD, elevation ):
    return Topos( latitude_degrees = latitudeDD, longitude_degrees = longitudeDD, elevation_m = elevation )


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

    result = \
        "Illumination: " + str( illumination ), \
        "Constellation: " + str( "TODO" ), \
        "Magnitude: TODO https://github.com/skyfielders/python-skyfield/issues/210", \
        "Tropical Sign: TODO", \
        "Distance to Earth: " + str( earthDistance ), \
        "Distance to Sun: " + str( sunDistance ), \
        "Bright Limb: " + str( "TODO" ), \
        "Azimuth: " + str( az.dms() ), \
        "Altitude: " + str( alt.dms() ), \
        "Right Ascension: " + str( ra.hms() ), \
        "Declination: " + str( dec.dms() ), \
        "Rise: TODO", \
        "Set: TODO"

    return result


def testSkyfieldSun( timeScale, utcNow, ephemeris, observer, topos ):
    sun = ephemeris[ SKYFIELD_PLANET_SUN ]
    apparent = observer.at( utcNow ).observe( sun ).apparent()
    alt, az, earthDistance = apparent.altaz()
    ra, dec, earthDistance = apparent.radec()

    t0 = timeScale.utc( utcNow.utc_datetime().year, utcNow.utc_datetime().month, utcNow.utc_datetime().day )
    t1 = timeScale.utc( utcNow.utc_datetime().year, utcNow.utc_datetime().month, utcNow.utc_datetime().day + 1 )
    t, y = almanac.find_discrete( t0, t1, almanac.sunrise_sunset( ephemeris, topos ) )

    print(t.utc_iso())
    print(y)

    if y[ 0 ]:
        rise = t[ 0 ].utc_iso( ' ' )
        set = t[ 1 ].utc_iso( ' ' )
    else:
        rise = t[ 1 ].utc_iso( ' ' )
        set = t[ 0 ].utc_iso( ' ' )

#TODO Rise/set does not match pyephem!

    t0 = timeScale.utc( utcNow.utc_datetime().year, utcNow.utc_datetime().month, utcNow.utc_datetime().day )
    t1 = timeScale.utc( utcNow.utc_datetime().year + 1, utcNow.utc_datetime().month, utcNow.utc_datetime().day )
    t, y = almanac.find_discrete( t0, t1, almanac.seasons( ephemeris ) )

    if "Equinox" in almanac.SEASON_EVENTS[ y[ 0 ] ]:
        equinox = t[ 0 ].utc_iso(' ' )
        solstice = t[ 1 ].utc_iso(' ' )
    else:
        solstice = t[ 0 ].utc_iso(' ' )
        equinox = t[ 1 ].utc_iso(' ' )

    return \
        "Constellation: TODO", \
        "Magnitude: TODO https://github.com/skyfielders/python-skyfield/issues/210", \
        "Tropical Sign: TODO", \
        "Distance to Earth: " + str( earthDistance ), \
        "Azimuth: " + str( az.dms() ), \
        "Altitude: " + str( alt.dms() ), \
        "Right Ascension: " + str( ra.hms() ), \
        "Declination: " + str( dec.dms() ), \
        "Dawn: TODO", \
        "Rise: " + str( rise ), \
        "Set: " + str( set ), \
        "Dusk: TODO", \
        "Solstice: " + solstice, \
        "Equinox: " + equinox, \
        "Eclipse Date/Time, Latitude/Longitude, Type: TODO"


def testSkyfield( utcNow, latitudeDD, longitudeDD, elevation ):
    print( "========" )
    print( "Skyfield" )
    print( "========" )
    print()

    timeScale = load.timescale()
    utcNowSkyfield = timeScale.utc( utcNow.replace( tzinfo = pytz.UTC ) )
#     print( utcNowSkyfield.utc )

#TODO This ephemeris contains only planets...what about stars and planetary moons?
    ephemeris = load( "2017-2024.bsp" )

#     print( ephemeris[ "saturn barycenter" ].target_name )
#     for planet in ephemeris.names():
#         print( planet )
#         thing = ephemeris[ planet ]
#         print( thing.target, thing.target_name )

    observer = getSkyfieldObserver( latitudeDD, longitudeDD, elevation, ephemeris[ SKYFIELD_PLANET_EARTH ] )
    topos = getSkyfieldTopos( latitudeDD, longitudeDD, elevation )
    print( testSkyfieldSun( timeScale, utcNowSkyfield, ephemeris, observer, topos ) )

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

# indicator-lunar revision 755 changed from local date/time to UTC for calculations (I think).

now = datetime.datetime.utcnow()
print( now )

testPyephem( now, latitudeDD, longitudeDD, elevation )
print()
print()
testSkyfield( now, latitudeDD, longitudeDD, elevation )


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