#!/usr/bin/env python3

# Use
#    https://ssd.jpl.nasa.gov/horizons.cgi
# to verify results.


# Install (and upgrade to) latest skyfield: 
#     sudo apt-get install python3-pip
#     sudo pip3 install --upgrade skyfield
#     sudo pip install --upgrade pytz
#     sudo pip3 install --upgrade pandas

# https://github.com/skyfielders/python-skyfield
# 
# http://rhodesmill.org/skyfield/
#
# ftp://ssd.jpl.nasa.gov/pub/eph/planets/README.txt
# ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/ascii_format.txt
#
# Planets
#     https://github.com/skyfielders/python-skyfield/issues/123
#     ftp://ssd.jpl.nasa.gov/pub/eph/planets/bsp/de421.bsp   <------------Use 430 as more accurate  https://github.com/skyfielders/python-skyfield/issues/231#issuecomment-450507640
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
# https://stackoverflow.com/questions/53011697/difference-in-sun-earth-distance-with-computedate-and-computeobserver

import datetime, ephem, math, pytz

from ephem.cities import _city_data
from ephem.stars import stars

from skyfield import almanac, positionlib
from skyfield.api import load, Star, Topos
from skyfield.data import hipparcos


# https://www.cosmos.esa.int/web/hipparcos/common-star-names
STARS = [ [ "Acamar", 13847 ], \
          [ "Achernar", 7588 ], \
          [ "Acrux", 60718 ], \
          [ "Adhara", 33579 ], \
          [ "Agena", 68702 ], \
          [ "Albireo", 95947 ], \
          [ "Alcor", 65477 ], \
          [ "Alcyone", 17702 ], \
          [ "Aldebaran", 21421 ], \
          [ "Alderamin", 105199 ], \
          [ "Algenib", 1067 ], \
          [ "Algieba", 50583 ], \
          [ "Algol", 14576 ], \
          [ "Alhena", 31681 ], \
          [ "Alioth", 62956 ], \
          [ "Alkaid", 67301 ], \
          [ "Almaak", 9640 ], \
          [ "Alnair", 109268 ], \
          [ "Alnath", 25428 ], \
          [ "Alnilam", 26311 ], \
          [ "Alnitak", 26727 ], \
          [ "Alphard", 46390 ], \
          [ "Alphekka", 76267 ], \
          [ "Alpheratz", 677 ], \
          [ "Alshain", 98036 ], \
          [ "Altair", 97649 ], \
          [ "Ankaa", 2081 ], \
          [ "Antares", 80763 ], \
          [ "Arcturus", 69673 ], \
          [ "Arneb", 25985 ], \
          [ "Babcock's star", 112247 ], \
          [ "Barnard's star", 87937 ], \
          [ "Bellatrix", 25336 ], \
          [ "Betelgeuse", 27989 ], \
          [ "Campbell's star", 96295 ], \
          [ "Canopus", 30438 ], \
          [ "Capella", 24608 ], \
          [ "Caph", 746 ], \
          [ "Castor", 36850 ], \
          [ "Cor Caroli", 63125 ], \
          [ "Cyg X-1", 98298 ], \
          [ "Deneb", 102098 ], \
          [ "Denebola", 57632 ], \
          [ "Diphda", 3419 ], \
          [ "Dubhe", 54061 ], \
          [ "Enif", 107315 ], \
          [ "Etamin", 87833 ], \
          [ "Fomalhaut", 113368 ], \
          [ "Groombridge 1830", 57939 ], \
          [ "Hadar", 68702 ], \
          [ "Hamal", 9884 ], \
          [ "Izar", 72105 ], \
          [ "Kapteyn's star", 24186 ], \
          [ "Kaus Australis", 90185 ], \
          [ "Kocab", 72607 ], \
          [ "Kruger 60", 110893 ], \
          [ "Luyten's star", 36208 ], \
          [ "Markab", 113963 ], \
          [ "Megrez", 59774 ], \
          [ "Menkar", 14135 ], \
          [ "Merak", 53910 ], \
          [ "Mintaka", 25930 ], \
          [ "Mira", 10826 ], \
          [ "Mirach", 5447 ], \
          [ "Mirphak", 15863 ], \
          [ "Mizar", 65378 ], \
          [ "Nihal", 25606 ], \
          [ "Nunki", 92855 ], \
          [ "Phad", 58001 ], \
          [ "Pleione", 17851 ], \
          [ "Polaris", 11767 ], \
          [ "Pollux", 37826 ], \
          [ "Procyon", 37279 ], \
          [ "Proxima", 70890 ], \
          [ "Rasalgethi", 84345 ], \
          [ "Rasalhague", 86032 ], \
          [ "Red Rectangle", 30089 ], \
          [ "Regulus", 49669 ], \
          [ "Rigel", 24436 ], \
          [ "Rigil Kent", 71683 ], \
          [ "Sadalmelik", 109074 ], \
          [ "Saiph", 27366 ], \
          [ "Scheat", 113881 ], \
          [ "Shaula", 85927 ], \
          [ "Shedir", 3179 ], \
          [ "Sheliak", 92420 ], \
          [ "Sirius", 32349 ], \
          [ "Spica", 65474 ], \
          [ "Tarazed", 97278 ], \
          [ "Thuban", 68756 ], \
          [ "Unukalhai", 77070 ], \
          [ "Van Maanen 2", 3829 ], \
          [ "Vega", 91262 ], \
          [ "Vindemiatrix", 63608 ], \
          [ "Zaurak", 18543 ], \
          [ "3C 273", 60936 ] ]


# Must get a new observer after a rising/setting computation and before calculations for a new body.    
def getPyephemObserver( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres ):
    observer = ephem.Observer()
    observer.lat = str( latitudeDecimalDegrees )
    observer.lon = str( longitudeDecimalDegrees )
    observer.elevation = elevationMetres
    observer.date = ephem.Date( utcNow )
    return observer


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
def getZenithAngleOfBrightLimbPyEphem( city, body ):
    sun = ephem.Sun( city )

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
    y = math.cos( sun.dec ) * math.sin( sun.ra - body.ra )
    x = math.sin( sun.dec ) * math.cos( body.dec ) - math.cos( sun.dec ) * math.sin( body.dec ) * math.cos( sun.ra - body.ra )
    positionAngleOfBrightLimb = math.atan2( y, x )

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
#TODO The city at this point has UTC as the time, but I think needs to change to be local time for the sidereal calculation.
    print( "Local sidereal time (hms):", city.sidereal_time() )
    print( "bodyRA (hms)", body.ra )
    hourAngle = city.sidereal_time() - body.ra
    print( "hour angle", hourAngle )
    y = math.sin( hourAngle )
    x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
    parallacticAngle = math.atan2( y, x )

    return math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )


def getZenithAngleOfBrightLimbSkyfield( timeScale, utcNow, ephemeris, observer, bodyRA, bodyDec, ):
    sunRA, sunDec, earthDistance = observer.at( utcNow ).observe( ephemeris[ SKYFIELD_PLANET_SUN ] ).apparent().radec()

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
    y = math.cos( sunDec.radians ) * math.sin( sunRA.radians - bodyRA.radians )
    x = math.sin( sunDec.radians ) * math.cos( bodyDec.radians ) - math.cos( sunDec.radians ) * math.sin( bodyDec.radians ) * math.cos( sunRA.radians - bodyRA.radians )
    positionAngleOfBrightLimb = math.atan2( y, x )

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1

#TODO Is this screwing up the timescale?
#     print( "Local sidereal time:", timeScale.utc( utcNow.replace( tzinfo = pytz.timezone( "Australia/Sydney" ) ) ).gmst )


#     print( "GMST", load.timescale().now().gmst )
    print( "GMST", utcNow.gmst )

#     https://stackoverflow.com/questions/25837452/python-get-current-time-in-right-timezone
    from datetime import datetime, timezone, timedelta
    utc_dt = datetime.now( timezone.utc ) # UTC time
    dt = utc_dt.astimezone() # local time
    print( "UTC with timezone information:", utc_dt )
    print( "Local time with timezone information:", dt )

    zzz = timeScale.utc( dt )
    print( "UTC from time object:", zzz )
    print( "GMST:", zzz.gmst )

    from skyfield.units import Angle
    longitude = None
    for positive in observer.positives:
        if type( positive ).__name__ == "Topos":
            longitude = positive.longitude
            break

    import numpy
    print( "GMST", utcNow.gmst, type( utcNow.gmst ) )
    print( "GMST (hours)", utcNow.gmst, type( utcNow.gmst ) )
    print( "GMST radians", numpy.radians( utcNow.gmst ), type( numpy.radians( utcNow.gmst ) ) )
    print( "GMST angle", Angle( hours = utcNow.gmst ), Angle( hours = utcNow.gmst ) )
    print( "Longitude", longitude, type( longitude ) ) 
    print( "Longitude radians", longitude.radians, type( longitude.radians ) ) 
    print( "Longitude degrees", longitude.degrees, type( longitude.degrees ) ) 
    print( "bodyRA", bodyRA, type( bodyRA ) )
    print( "bodyRA radians", bodyRA.radians, type( bodyRA.radians ) )
    print( "bodyRA hours", bodyRA._hours, type( bodyRA._hours) )
    hourAngle = numpy.radians( utcNow.gmst ) - longitude.radians - bodyRA.radians
    print( "hour angle", hourAngle )
    hourAngle = utcNow.gmst - ( 1.0 * longitude._degrees ) - bodyRA._hours
    print( "hour angle", numpy.radians( hourAngle ) )
#     hourAngle = Angle( hours = utcNow.gmst ) - longitude - bodyRA
#     print( "hour angle", hourAngle )

    import time
    print( "Local time zone:", time.strftime( "%z" ) )
    print( "Local time zone:", timezone( timedelta( seconds =- time.timezone ) ) )

#     from time import gmtime, strftime
#     print(strftime("%z", gmtime()))
#     import time; print( time.tzname )
#     print( time.tzname[time.daylight] )
#     print( time.localtime().tm_isdst )
#     print( datetime.datetime.now(datetime.timezone.utc).astimezone().tzname() )
#     print( pytz.all_timezones )
#     utcNowSkyfield = timeScale.utc( load.timescale().now().replace( tzinfo = pytz.UTC ) )
#     print( "Timescale now tzinfo utc gmst", utcNowSkyfield.gmst )
    
    
#     sss = timeScale.utc( datetime.datetime.utcnow() )
#     print( "Timescale datetime utc now gmst", sss.gmst )


#     hourAngle = city.sidereal_time() - bodyRA
#     y = math.sin( hourAngle )
#     x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
#     parallacticAngle = math.atan2( y, x )

#     hourAngleNEW = observerSiderealTime - bodyRA
#     yNEW = math.sin( hourAngleNEW )
#     xNEW = math.tan( observerLatitude ) * math.cos( bodyDec ) - math.sin( bodyDec ) * math.cos( hourAngleNEW )
#     parallacticAngleNEW = math.atan2( yNEW, xNEW )

#     orig = math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )
#     new = math.degrees( ( positionAngleOfBrightLimbNEW - parallacticAngleNEW ) % ( 2.0 * math.pi ) )
#     return math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )
    return ""


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

    # Must be the last thing calculated!
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


def testPyephemStar( observer, star ):
    star.compute( observer )

    # Must retrieve the az/alt/ra/dec BEFORE rise/set is computed as the values get clobbered.
    result = \
        "Constellation: " + str( ephem.constellation( star ) ), \
        "Magnitude: " + str( star.mag ), \
        "Tropical Sign: TODO", \
        "Bright Limb: " + str( "TODO" ), \
        "Azimuth: " + str( star.az ), \
        "Altitude: " + str( star.alt ), \
        "Right Ascension: " + str( star.ra ), \
        "Declination: " + str( star.dec )

    # Must be the last thing calculated!
    try:
        result += \
            "Rise: " + str( observer.next_rising( star ) ), \
            "Set: " + str( observer.next_setting( star ) )

    except ephem.AlwaysUpError:
        result += "Rise/Set: Always Up"

    except ephem.NeverUpError:
        result += "Rise/Set: Never Up"

#TODO
#     if planet.name == "Saturn":
#         result += str( planet.earth_tilt ), str( planet.sun_tilt )

    return result


def testPyephemSun( utcNow, observer ):
    # Must retrieve the az/alt/ra/dec BEFORE rise/set is computed as the values get clobbered.
    sun = ephem.Sun( observer )

    result = \
        "Constellation: " + str( ephem.constellation( sun ) ), \
        "Magnitude: " + str( sun.mag ), \
        "Tropical Sign: TODO", \
        "Distance to Earth: " + str( sun.earth_distance ), \
        "Azimuth: " + str( sun.az ), \
        "Altitude: " + str( sun.alt ), \
        "Right Ascension: " + str( sun.ra ), \
        "Declination: " + str( sun.dec );

    solstice = str( ephem.next_solstice( utcNow ) )
    equinox = str( ephem.next_equinox( utcNow ) )

    # Must be the last thing calculated!
    rise = str( observer.next_rising( sun ).datetime() )
    sunset = str( observer.next_setting( sun ).datetime() )

    observer.horizon = '-6' # -6 = civil twilight, -12 = nautical, -18 = astronomical (http://stackoverflow.com/a/18622944/2156453)
    sun = ephem.Sun( observer )
    dawn = str( observer.next_rising( sun, use_center = True ).datetime() )
    dusk = str( observer.next_setting( sun, use_center = True ).datetime() )

    result += \
        "Dawn: " + dawn, \
        "Rise: " + rise, \
        "Set: " + sunset, \
        "Dusk: " + dusk, \
        "Solstice: " + solstice, \
        "Equinox: " + equinox, \
        "Eclipse Date/Time, Latitude/Longitude, Type: TODO";

    return result


def testPyephemMoon( utcNow, observer ):
    # Must retrieve the az/alt/ra/dec BEFORE rise/set is computed as the values get clobbered.
    moon = ephem.Moon( observer )

    result = \
        "Constellation: " + str( ephem.constellation( moon ) ), \
        "Magnitude: " + str( moon.mag ), \
        "Tropical Sign: TODO", \
        "Distance to Earth: " + str( moon.earth_distance ), \
        "Azimuth: " + str( moon.az ), \
        "Altitude: " + str( moon.alt ), \
        "Right Ascension: " + str( moon.ra ), \
        "Declination: " + str( moon.dec );

    zenithAngleOfBrightLimb = str( getZenithAngleOfBrightLimbPyEphem( observer, moon ) )

    # Must be the last thing calculated!
    rise = str( observer.next_rising( moon ).datetime() )
    sunset = str( observer.next_setting( moon ).datetime() )

    result += \
        "Rise: " + rise, \
        "Set: " + sunset, \
        "Eclipse Date/Time, Latitude/Longitude, Type: TODO", \
        "Zenith Angle of Bright Limb: " + zenithAngleOfBrightLimb;

    return result


def testSiderealTime():
    madrid = ephem.city('Madrid')
    madrid.date = '1978/10/3 11:32'
    print( "Madrid", madrid.sidereal_time())


    madrid = ephem.city('Sydney')
    madrid.date = '1978/10/3 11:32'
    print( "Sydney", madrid.sidereal_time())


    ts = load.timescale()
    t = ts.utc(1978, 10, 3,11,32, 0)
    st = t.gmst
    print( st )

    print( load.timescale().now().gmst )

    sss = ts.utc( utcNow.replace( tzinfo = pytz.UTC ) )
    sss = ts.utc( datetime.datetime.utcnow() )
    print( sss.gmst )

    import sys
    sys.exit()

    ephemeris = load( "2017-2024.bsp" )
    sun = ephemeris[ SKYFIELD_PLANET_SUN ]

    observer = getSkyfieldObserver( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres, ephemeris[ SKYFIELD_PLANET_EARTH ] )
    timescale = load.timescale()
    utcNowSkyfield = timescale.utc( utcNow.replace( tzinfo = pytz.UTC ) )
    apparent = observer.at( utcNowSkyfield ).observe( sun ).apparent()
    alt, az, earthDistance = apparent.altaz()
    sunRA, sunDEC, earthDistance = apparent.radec()

    thePlanet = ephemeris[ SKYFIELD_PLANET_SATURN ]
    apparent = observer.at( utcNowSkyfield ).observe( thePlanet ).apparent()
    ra, dec, earthDistance = apparent.radec()

    observerSiderealTime = utcNowSkyfield.gmst


    observer = getPyephemObserver( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )
    city = ephem.city( "Sydney" )
    city.date = utcNow
    sun = ephem.Sun( observer )
    saturn = ephem.Saturn( observer )

    ephemeris = load( "2017-2024.bsp" )
    sun = ephemeris[ SKYFIELD_PLANET_SUN ]

    observer = getSkyfieldObserver( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres, ephemeris[ SKYFIELD_PLANET_EARTH ] )
    timescale = load.timescale()
    utcNowSkyfield = timescale.utc( utcNow.replace( tzinfo = pytz.UTC ) )
    apparent = observer.at( utcNowSkyfield ).observe( sun ).apparent()
    sunRA, sunDEC, earthDistance = apparent.radec()

    apparent = observer.at( utcNowSkyfield ).observe( ephemeris[ SKYFIELD_PLANET_SATURN ] ).apparent()
    ra, dec, earthDistance = apparent.radec()

# https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
# http://astro.subhashbose.com/siderealtime/
# http://www.wwu.edu/skywise/skymobile/skywatch.html
# http://www.jgiesen.de/astro/astroJS/siderealClock/
# http://neoprogrammics.com/sidereal_time_calculator/index.php   <------ does not match the other sites.
    observerSiderealTime = utcNowSkyfield.gmst
    print( city.sidereal_time() )
    print( '%.6f' % city.sidereal_time() )
    print( observerSiderealTime )

    print( timescale.utc( utcNow.replace( tzinfo = pytz.timezone( "Australia/Sydney" ) ) ).gmst )
    print( timescale.utc( utcNow.replace( tzinfo = pytz.timezone( "Australia/Sydney" ) ) ).gast )


def testPyephem( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres ):
    print( "=======" )
    print( "PyEphem" )
    print( "=======" )
    print()

    observer = getPyephemObserver( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )
    print( "Sun:", testPyephemSun( utcNow, observer ) )

    observer = getPyephemObserver( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )
    print( "Saturn:", testPyephemPlanet( observer, ephem.Saturn( observer ) ) )

    observer = getPyephemObserver( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )
    print( "Almach (star):", testPyephemStar( observer, ephem.star( "Almach" ) ) )

    observer = getPyephemObserver( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )
    print( "Moon:", testPyephemMoon( utcNow, observer ) )

#     observer = getPyephemObserver( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )
#     tropicalSignName, tropicalSignDegree, tropicalSignMinute = getTropicalSignPyEphem( ephem.Saturn( observer ), ephem.Date( utcNow ), utcNow )
#     print( tropicalSignName, tropicalSignDegree, tropicalSignMinute )



import gzip
def filterStarsByMagnitudeFromHipparcos( hipparcosInputGzipFile, hipparcosOutputGzipFile, maximumMagnitude ):
    try:
        with gzip.open( hipparcosInputGzipFile, "rb" ) as inFile, gzip.open( hipparcosOutputGzipFile, "wb" ) as outFile:
            for line in inFile:
                if len( line.decode()[ 41 : 46 ].strip() ) > 0 and float( line.decode()[ 41 : 46 ] ) <= float( maximumMagnitude ):
                    outFile.write( line )

    except Exception as e:
        print( e )


def getSkyfieldObserver( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres, earth ):
    return earth + Topos( latitude_degrees = latitudeDecimalDegrees, longitude_degrees = longitudeDecimalDegrees, elevation_m = elevationMetres )


def getSkyfieldTopos( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres ):
    return Topos( latitude_degrees = latitudeDecimalDegrees, longitude_degrees = longitudeDecimalDegrees, elevation_m = elevationMetres )


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


# https://www.cosmos.esa.int/web/hipparcos/search-facility
# https://www.cosmos.esa.int/web/hipparcos/common-star-names
#TODO Add rise/set.
#TODO Add alt, az.  Can these be obtained from ra/dec?
def testSkyfieldStar( utcNow, observer, star ):
    astrometric = observer.at( utcNow ).observe( star )
#     alt, az, earthDistance = astrometric.altaz()
    ra, dec, earthDistance = astrometric.radec()
    
    result = \
        "Constellation: " + str( "TODO" ), \
        "Magnitude: TODO https://github.com/skyfielders/python-skyfield/issues/210", \
        "Tropical Sign: TODO", \
        "Distance to Earth: " + str( earthDistance ), \
        "Bright Limb: " + str( "TODO" ), \
        "Right Ascension: " + str( ra.hms() ), \
        "Declination: " + str( dec.dms() ), \
        "Rise: TODO", \
        "Set: TODO"

    return result


#TODO There is a difference between Az/ALT for the sun between the two systems...
#...yet skyfield agrees with the indicator!
def testSkyfieldSun( timeScale, utcNow, ephemeris, observer, topos ):
    sun = ephemeris[ SKYFIELD_PLANET_SUN ]
    apparent = observer.at( utcNow ).observe( sun ).apparent()
    alt, az, earthDistance = apparent.altaz()
    ra, dec, earthDistance = apparent.radec()

    t0 = timeScale.utc( utcNow.utc_datetime().year, utcNow.utc_datetime().month, utcNow.utc_datetime().day )
    t1 = timeScale.utc( utcNow.utc_datetime().year, utcNow.utc_datetime().month, utcNow.utc_datetime().day + 1 )
    t, y = almanac.find_discrete( t0, t1, almanac.sunrise_sunset( ephemeris, topos ) )

#     print(t.utc_iso())
#     print(y)

    if y[ 0 ]:
        rise = t[ 0 ].utc_iso( ' ' )
        set = t[ 1 ].utc_iso( ' ' )
    else:
        rise = t[ 1 ].utc_iso( ' ' )
        set = t[ 0 ].utc_iso( ' ' )

    print( "Rise: " + rise )
    print( "Set: " + set )

#TODO Rise/set do not always match between pyephem and skyfield!
# Results match when local time and GMT are on the same day...so try very early in morning or immediately after midnight to verify.

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


def testSkyfieldMoon( timeScale, utcNow, ephemeris, observer, topos ):
    moon = ephemeris[ SKYFIELD_PLANET_MOON ]
    apparent = observer.at( utcNow ).observe( moon ).apparent()
    alt, az, earthDistance = apparent.altaz()
    ra, dec, earthDistance = apparent.radec()

    zenithAngleOfBrightLimb = str( getZenithAngleOfBrightLimbSkyfield( timeScale, utcNow, ephemeris, observer, ra, dec ) )

    return \
        "Constellation: TODO", \
        "Magnitude: TODO https://github.com/skyfielders/python-skyfield/issues/210", \
        "Tropical Sign: TODO", \
        "Distance to Earth: " + str( earthDistance ), \
        "Azimuth: " + str( az.dms() ), \
        "Altitude: " + str( alt.dms() ), \
        "Right Ascension: " + str( ra.hms() ), \
        "Declination: " + str( dec.dms() ), \
        "Rise: TODO", \
        "Set: TODO", \
        "Eclipse Date/Time, Latitude/Longitude, Type: TODO"


def testSkyfield( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres ):
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


    observer = getSkyfieldObserver( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres, ephemeris[ SKYFIELD_PLANET_EARTH ] )
    topos = getSkyfieldTopos( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )
    print( testSkyfieldSun( timeScale, utcNowSkyfield, ephemeris, observer, topos ) )
    print( testSkyfieldMoon( timeScale, utcNowSkyfield, ephemeris, observer, topos ) )


#     observer = getSkyfieldObserver( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres, ephemeris[ SKYFIELD_PLANET_EARTH ] )
#     with load.open( "hip_main.2.5.dat.gz" ) as f:
#         star = Star.from_dataframe( hipparcos.load_dataframe( f ).loc[ 21421 ] )
# 
#     print( testSkyfieldStar( utcNowSkyfield, observer, star ) )


#     barnard = Star(ra_hours=(17, 57, 48.49803),
#                dec_degrees=(4, 41, 36.2072),
#                ra_mas_per_year=-798.71,
#                dec_mas_per_year=+10337.77,
#                parallax_mas=545.4,
#                radial_km_per_s=-110.6)


    observer = getSkyfieldObserver( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres, ephemeris[ SKYFIELD_PLANET_EARTH ] )
    print( testSkyfieldPlanet( utcNowSkyfield, ephemeris, observer, SKYFIELD_PLANET_SATURN ) )


    filterStarsByMagnitudeFromHipparcos( "hip_main.dat.gz", "hip_main.2.5.dat.gz", 3 )


#TODO First time star catalog is loaded, takes a lot of time, but subsequent loads are quick.
# So the data must be cached...where?  Raise an issue with Skyfield.
# Seems the load line below pulls the data from ftp://cdsarc.u-strasbg.fr/cats/I/239/hip_main.dat.gz
# New question: if we can pre-load the data file that is good.
# So can we pre-filter the data and only keep that as a file, rather than the whole thing?
#     with load.open( hipparcos.URL ) as f:
#         stars = hipparcos.load_dataframe( f )

    with load.open( "hip_main.2.5.dat.gz" ) as f:
        stars = hipparcos.load_dataframe( f )

    stars = stars[ stars[ "magnitude" ] <= 10 ]
    print( "After filtering, there are {} stars".format( len( stars ) ) )
#Results in 93 stars; same number as PyEphem (not sure how though as PyEphem has stars with magnitude greater than 2.5).






#     print()
#     timeScale = load.timescale()
#     bluffton = Topos('40.8939 N', '83.8917 W')
#     
#     t0 = timeScale.utc(2018, 9, 12, 4)
#     t1 = timeScale.utc(2018, 9, 13, 4)
#     t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(ephemeris, bluffton))
#     
#     print(t.utc_iso())
#     print(y)
#     print()
# 
#     bluffton = Topos('40.8939 N', '83.8917 W')
#     
#     t0 = timeScale.utc(2018, 9, 12)
#     t1 = timeScale.utc(2018, 9, 13)
#     t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(ephemeris, bluffton))
#     
#     print(t.utc_iso())
#     print(y)



# def getPlanetFromEphemeris( ephemeris ):
#     for code in ephemeris.names():
        

SKYFIELD_PLANET_EARTH = "earth"
SKYFIELD_PLANET_MOON = "moon"
SKYFIELD_PLANET_SATURN = "saturn barycenter"
SKYFIELD_PLANET_SUN = "sun"

latitudeDecimalDegrees = -33.8
longitudeDecimalDegrees = 151.2
elevationMetres = 100

#TODO Might need to install pytz to localise the date/time.
# https://rhodesmill.org/skyfield/time.html


# indicator-lunar revision 755 changed from local date/time to UTC for calculations (I think).

utcNow = datetime.datetime.utcnow()
print( utcNow )
print()

testPyephem( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )
print()
print()
testSkyfield( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )


# bl = getZenithAngleOfBrightLimbSkyfield( city, saturn, sunRA.radians, sunDEC.radians, ra.radians, dec.radians, math.radians( latitudeDecimalDegrees ), observerSiderealTime )


# barnard = Star( ra_hours = ( 17, 57, 48.49803 ), dec_degrees = ( 4, 41, 36.2072 ) )
# ts = load.timescale()
# t = ts.utcNow()
# astrometric = observer.at( timeScaleNow ).observe( barnard )
# ra, dec, distance = astrometric.apparent().radec()
# az, az, distance = astrometric.apparent().altaz()
# print(ra, dec, az, alt )


# observer = ephem.city( cityName )
# observer.date = utcNow
# starName = "Cebalrai"
# star = ephem.star( starName )
# star.compute( observer )
# print( star.ra, star.dec, star.az, star.alt )


# List of stars from PyEphem
# Achernar
# Adara
# Agena
# Albereo
# Alcaid
# Alcor
# Alcyone
# Aldebaran
# Alderamin
# Alfirk
# Algenib
# Algieba
# Algol
# Alhena
# Alioth
# Almach
# Alnair
# Alnilam
# Alnitak
# Alphard
# Alphecca
# Alshain
# Altair
# Antares
# Arcturus
# Arkab Posterior
# Arkab Prior
# Arneb
# Atlas
# Bellatrix
# Betelgeuse
# Canopus
# Capella
# Caph
# Castor
# Cebalrai
# Deneb
# Denebola
# Dubhe
# Electra
# Elnath
# Enif
# Etamin
# Fomalhaut
# Gienah Corvi
# Hamal
# Izar
# Kaus Australis
# Kochab
# Maia
# Markab
# Megrez
# Menkalinan
# Menkar
# Merak
# Merope
# Mimosa
# Minkar
# Mintaka
# Mirach
# Mirzam
# Mizar
# Naos
# Nihal
# Nunki
# Peacock
# Phecda
# Polaris
# Pollux
# Procyon
# Rasalgethi
# Rasalhague
# Regulus
# Rigel
# Rukbat
# Sadalmelik
# Sadr
# Saiph
# Scheat
# Schedar
# Shaula
# Sheliak
# Sirius
# Sirrah
# Spica
# Sulafat
# Tarazed
# Taygeta
# Thuban
# Unukalhai
# Vega
# Vindemiatrix
# Wezen
# Zaurak
