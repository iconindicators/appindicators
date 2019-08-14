#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Calculate astronomical information using Skyfield.


#TODO Can pip3 be run from the install?
# Install (and upgrade to) latest skyfield: 
#     sudo apt-get install python3-pip
#     sudo pip3 install --upgrade skyfield
#     sudo pip3 install --upgrade pytz
#     sudo pip3 install --upgrade pandas


from skyfield import almanac
from skyfield.api import load, Star, Topos
from skyfield.data import hipparcos
from skyfield.nutationlib import iau2000b

import eclipse, gzip, pytz
# import datetime, math


class AstronomicalBodyType: Comet, MinorPlanet, Moon, Planet, Satellite, Star, Sun = range( 7 )


DATA_ALTITUDE = "ALTITUDE"
DATA_AZIMUTH = "AZIMUTH"
DATA_BRIGHT_LIMB = "BRIGHT LIMB" # Used for creating an icon; not intended for display to the user.
DATA_DAWN = "DAWN"
DATA_DUSK = "DUSK"
DATA_ECLIPSE_DATE_TIME = "ECLIPSE DATE TIME"
DATA_ECLIPSE_LATITUDE = "ECLIPSE LATITUDE"
DATA_ECLIPSE_LONGITUDE = "ECLIPSE LONGITUDE"
DATA_ECLIPSE_TYPE = "ECLIPSE TYPE"
DATA_ELEVATION = "ELEVATION" # Internally used for city.
DATA_FIRST_QUARTER = "FIRST QUARTER"
DATA_FULL = "FULL"
DATA_ILLUMINATION = "ILLUMINATION" # Used for creating an icon; not intended for display to the user.
DATA_LATITUDE = "LATITUDE" # Internally used for city.
DATA_LONGITUDE = "LONGITUDE" # Internally used for city.
DATA_MESSAGE = "MESSAGE"
DATA_NEW = "NEW"
DATA_PHASE = "PHASE"
DATA_RISE_AZIMUTH = "RISE AZIMUTH"
DATA_RISE_TIME = "RISE TIME"
DATA_SET_AZIMUTH = "SET AZIMUTH"
DATA_SET_TIME = "SET TIME"
DATA_THIRD_QUARTER = "THIRD QUARTER"

DATA_TAGS = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_BRIGHT_LIMB,
    DATA_DAWN,
    DATA_DUSK,
    DATA_ECLIPSE_DATE_TIME,
    DATA_ECLIPSE_LATITUDE,
    DATA_ECLIPSE_LONGITUDE,
    DATA_ECLIPSE_TYPE,
    DATA_FIRST_QUARTER,
    DATA_FULL,
    DATA_ILLUMINATION,
    DATA_MESSAGE,
    DATA_NEW,
    DATA_PHASE,
    DATA_RISE_AZIMUTH,
    DATA_RISE_TIME,
    DATA_SET_AZIMUTH,
    DATA_SET_TIME,
    DATA_THIRD_QUARTER ]

DATA_COMET = [
    DATA_MESSAGE,
    DATA_RISE_AZIMUTH,
    DATA_RISE_TIME,
    DATA_SET_AZIMUTH,
    DATA_SET_TIME ]

DATA_MINOR_PLANET = [
    DATA_MESSAGE,
    DATA_RISE_AZIMUTH,
    DATA_RISE_TIME,
    DATA_SET_AZIMUTH,
    DATA_SET_TIME ]

DATA_MOON = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_BRIGHT_LIMB,
    DATA_ECLIPSE_DATE_TIME,
    DATA_ECLIPSE_LATITUDE,
    DATA_ECLIPSE_LONGITUDE,
    DATA_ECLIPSE_TYPE,
    DATA_ILLUMINATION,
    DATA_MESSAGE,
    DATA_PHASE,
    DATA_RISE_TIME,
    DATA_SET_TIME ]

DATA_PLANET = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_MESSAGE,
    DATA_RISE_TIME,
    DATA_SET_TIME ]

DATA_SATELLITE = [
    DATA_MESSAGE,
    DATA_RISE_AZIMUTH,
    DATA_RISE_TIME,
    DATA_SET_AZIMUTH,
    DATA_SET_TIME ]

DATA_STAR = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_MESSAGE,
    DATA_RISE_TIME,
    DATA_SET_TIME ]

DATA_SUN = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_DAWN,
    DATA_DUSK,
    DATA_ECLIPSE_DATE_TIME,
    DATA_ECLIPSE_LATITUDE,
    DATA_ECLIPSE_LONGITUDE,
    DATA_ECLIPSE_TYPE,
    DATA_MESSAGE,
    DATA_RISE_TIME,
    DATA_SET_TIME ]

NAME_TAG_CITY = "CITY"
NAME_TAG_MOON = "MOON"
NAME_TAG_SUN = "SUN"

MOON = "MOON"
SUN = "SUN"

PLANET_MERCURY = "MERCURY BARYCENTER"
PLANET_EARTH = "EARTH"
PLANET_VENUS = "VENUS BARYCENTER"
PLANET_MARS = "MARS BARYCENTER"
PLANET_JUPITER = "JUPITER BARYCENTER"
PLANET_SATURN = "SATURN BARYCENTER"
PLANET_URANUS = "URANUS BARYCENTER"
PLANET_NEPTUNE = "NEPTUNE BARYCENTER"
PLANET_PLUTO = "PLUTO BARYCENTER"

PLANETS = [ PLANET_MERCURY, PLANET_VENUS, PLANET_MARS, PLANET_JUPITER, PLANET_SATURN, PLANET_URANUS, PLANET_NEPTUNE, PLANET_PLUTO ]

LUNAR_PHASE_FULL_MOON = "FULL_MOON"
LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
LUNAR_PHASE_NEW_MOON = "NEW_MOON"
LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"

# https://www.cosmos.esa.int/web/hipparcos/common-star-names
# This list contained a duplicate Hipparcos Identifier of 68702 for a star with two common names: Agena and Hadar.
# The official name is Hadar and so Agena has been removed.
STARS = {
    "Acamar"            : 13847,
    "Achernar"          : 7588,
    "Acrux"             : 60718,
    "Adhara"            : 33579,
    "Albireo"           : 95947,
    "Alcor"             : 65477,
    "Alcyone"           : 17702,
    "Aldebaran"         : 21421,
    "Alderamin"         : 105199,
    "Algenib"           : 1067,
    "Algieba"           : 50583,
    "Algol"             : 14576,
    "Alhena"            : 31681,
    "Alioth"            : 62956,
    "Alkaid"            : 67301,
    "Almaak"            : 9640,
    "Alnair"            : 109268,
    "Alnath"            : 25428,
    "Alnilam"           : 26311,
    "Alnitak"           : 26727,
    "Alphard"           : 46390,
    "Alphekka"          : 76267,
    "Alpheratz"         : 677,
    "Alshain"           : 98036,
    "Altair"            : 97649,
    "Ankaa"             : 2081,
    "Antares"           : 80763,
    "Arcturus"          : 69673,
    "Arneb"             : 25985,
    "Babcock's star"    : 112247,
    "Barnard's star"    : 87937,
    "Bellatrix"         : 25336,
    "Betelgeuse"        : 27989,
    "Campbell's star"   : 96295,
    "Canopus"           : 30438,
    "Capella"           : 24608,
    "Caph"              : 746,
    "Castor"            : 36850,
    "Cor Caroli"        : 63125,
    "Cyg X-1"           : 98298,
    "Deneb"             : 102098,
    "Denebola"          : 57632,
    "Diphda"            : 3419,
    "Dubhe"             : 54061,
    "Enif"              : 107315,
    "Etamin"            : 87833,
    "Fomalhaut"         : 113368,
    "Groombridge 1830"  : 57939,
    "Hadar"             : 68702,
    "Hamal"             : 9884,
    "Izar"              : 72105,
    "Kapteyn's star"    : 24186,
    "Kaus Australis"    : 90185,
    "Kocab"             : 72607,
    "Kruger 60"         : 110893,
    "Luyten's star"     : 36208,
    "Markab"            : 113963,
    "Megrez"            : 59774,
    "Menkar"            : 14135,
    "Merak"             : 53910,
    "Mintaka"           : 25930,
    "Mira"              : 10826,
    "Mirach"            : 5447,
    "Mirphak"           : 15863,
    "Mizar"             : 65378,
    "Nihal"             : 25606,
    "Nunki"             : 92855,
    "Phad"              : 58001,
    "Pleione"           : 17851,
    "Polaris"           : 11767,
    "Pollux"            : 37826,
    "Procyon"           : 37279,
    "Proxima"           : 70890,
    "Rasalgethi"        : 84345,
    "Rasalhague"        : 86032,
    "Red Rectangle"     : 30089,
    "Regulus"           : 49669,
    "Rigel"             : 24436,
    "Rigil Kent"        : 71683,
    "Sadalmelik"        : 109074,
    "Saiph"             : 27366,
    "Scheat"            : 113881,
    "Shaula"            : 85927,
    "Shedir"            : 3179,
    "Sheliak"           : 92420,
    "Sirius"            : 32349,
    "Spica"             : 65474,
    "Tarazed"           : 97278,
    "Thuban"            : 68756,
    "Unukalhai"         : 77070,
    "Van Maanen 2"      : 3829,
    "Vega"              : 91262,
    "Vindemiatrix"      : 63608,
    "Zaurak"            : 18543,
    "3C 273"            : 60936 }

EPHEMERIS_PLANETS = "de438_2019-2023.bsp" # Refer to https://github.com/skyfielders/python-skyfield/issues/123
EPHEMERIS_STARS = "hip_common_name_stars.dat.gz"

MESSAGE_BODY_ALWAYS_UP = "BODY_ALWAYS_UP"
MESSAGE_SATELLITE_IS_CIRCUMPOLAR = "SATELLITE_IS_CIRCUMPOLAR"


#TODO Might need to cache deltat.data and deltat.preds as the backend website was down and I couldn't get them except at a backup site.
# What other files are downloaded?  Need to also grab: https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat  Be careful...this file expires!


# TODO Use
#    https://ssd.jpl.nasa.gov/horizons.cgi
# to verify results.
def getAstronomicalInformation( utcNow,
                                latitude, longitude, elevation,
                                planets,
                                stars,
                                satellites, satelliteData,
                                comets, cometData,
                                minorPlanets, minorPlanetData,
                                magnitude ):

    data = { }

    # Used internally to create the observer/city...removed before passing back to the caller.
    data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ] = latitude
    data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ] = longitude
    data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ] = elevation

    timeScale = load.timescale()
    utcNowSkyfield = timeScale.utc( utcNow.replace( tzinfo = pytz.UTC ) ) #TODO In each function, so far, this is converted to a datetime...so maybe just pass in the original?
    ephemerisPlanets = load( EPHEMERIS_PLANETS )
    observer = __getSkyfieldObserver( latitude, longitude, elevation, ephemerisPlanets[ PLANET_EARTH ] )

    __calculateMoon( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets )
    __calculateSun( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets )
    __calculatePlanets( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets, PLANETS ) # TODO Should use passed in list of planets eventually.

    with load.open( EPHEMERIS_STARS ) as f:
        ephemerisStars = hipparcos.load_dataframe( f )

    stars = list( STARS )#TODO Testing
    __calculateStars( utcNowSkyfield, data, timeScale, observer, ephemerisStars, stars ) #TODO Ensure passed in stars match those in STARS

#     Comet https://github.com/skyfielders/python-skyfield/issues/196
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.Comet, comets, cometData, magnitude )
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.MinorPlanet, minorPlanets, minorPlanetData, magnitude )

#     Satellite https://github.com/skyfielders/python-skyfield/issues/115
#     __calculateSatellites( ephemNow, data, satellites, satelliteData )

    del data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ]
    del data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ]
    del data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ]

    return data


# http://www.ga.gov.au/geodesy/astro/moonrise.jsp
# http://futureboy.us/fsp/moon.fsp
# http://www.geoastro.de/moondata/index.html
# http://www.geoastro.de/SME/index.htm
# http://www.geoastro.de/elevazmoon/index.htm
# http://www.geoastro.de/altazsunmoon/index.htm
# http://www.geoastro.de/sundata/index.html
# http://www.satellite-calculations.com/Satellite/suncalc.htm
def __calculateMoon( utcNow, data, timeScale, observer, ephemeris ):
    key = ( AstronomicalBodyType.Moon, NAME_TAG_MOON )
    moon = ephemeris[ MOON ]
    neverUp = __calculateCommon( utcNow, data, timeScale, observer, moon, AstronomicalBodyType.Moon, NAME_TAG_MOON )

    illumination = almanac.fraction_illuminated( ephemeris, MOON, utcNow ) * 100 # Needed for icon.
    data[ key + ( DATA_ILLUMINATION, ) ] = str( illumination ) # Needed for icon.

    utcNowDateTime = utcNow.utc_datetime()
    t0 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day )
    t1 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month + 2, 1 ) # Ideally would just like to add one month, but not sure what happens if today's date is say the 31st and the next month is say February.
#TODO Test the above line for Feb.
# https://rhodesmill.org/skyfield/almanac.html
    t, y = almanac.find_discrete( t0, t1, almanac.moon_phases( ephemeris ) )
    moonPhases = [ almanac.MOON_PHASES[ yi ] for yi in y ]
    moonPhaseDateTimes = t.utc_datetime()
    nextNewMoonDateTime = moonPhaseDateTimes [ ( moonPhases.index( "New Moon" ) ) ]
    nextFullMoonDateTime = moonPhaseDateTimes [ ( moonPhases.index( "Full Moon" ) ) ]
    data[ key + ( DATA_PHASE, ) ] = __getLunarPhase( int( float ( illumination ) ), nextFullMoonDateTime, nextNewMoonDateTime ) # Need for notification.

#TODO
#     zenithAngleOfBrightLimb = str( getZenithAngleOfBrightLimbSkyfield( timeScale, utcNow, ephemeris, observer, ra, dec ) )
#     data[ key + ( DATA_BRIGHT_LIMB, ) ] = str( int( round( __getZenithAngleOfBrightLimb( ephemNow, data, ephem.Moon() ) ) ) ) # Pass in a clean instance (just to be safe).  Needed for icon.

    if not neverUp:
        moonPhaseDateTimes = t.utc_iso()
        nextNewMoonISO = moonPhaseDateTimes [ ( moonPhases.index( "New Moon" ) ) ]
        nextFirstQuarterISO = moonPhaseDateTimes[ ( moonPhases.index( "First Quarter" ) ) ]
        nextThirdQuarterISO = moonPhaseDateTimes [ ( moonPhases.index( "Last Quarter" ) ) ]
        nextFullMoonISO = moonPhaseDateTimes [ ( moonPhases.index( "Full Moon" ) ) ]

        data[ key + ( DATA_FIRST_QUARTER, ) ] = nextFirstQuarterISO
        data[ key + ( DATA_FULL, ) ] = nextFullMoonISO
        data[ key + ( DATA_THIRD_QUARTER, ) ] = nextThirdQuarterISO
        data[ key + ( DATA_NEW, ) ] = nextNewMoonISO

        __calculateEclipse( utcNow.utc_datetime().replace( tzinfo = None ), data, AstronomicalBodyType.Moon, NAME_TAG_MOON )


# Get the lunar phase for the given date/time and illumination percentage.
#
#    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
#    nextFullMoonDate The date of the next full moon.
#    nextNewMoonDate The date of the next new moon.
def __getLunarPhase( illuminationPercentage, nextFullMoonDate, nextNewMoonDate ):
    phase = None
    if nextFullMoonDate < nextNewMoonDate: # No need for these dates to be localised...just need to know which date is before the other.
        # Between a new moon and a full moon...
        if( illuminationPercentage > 99 ):
            phase = LUNAR_PHASE_FULL_MOON
        elif illuminationPercentage <= 99 and illuminationPercentage > 50:
            phase = LUNAR_PHASE_WAXING_GIBBOUS
        elif illuminationPercentage == 50:
            phase = LUNAR_PHASE_FIRST_QUARTER
        elif illuminationPercentage < 50 and illuminationPercentage >= 1:
            phase = LUNAR_PHASE_WAXING_CRESCENT
        else: # illuminationPercentage < 1
            phase = LUNAR_PHASE_NEW_MOON
    else:
        # Between a full moon and the next new moon...
        if( illuminationPercentage > 99 ):
            phase = LUNAR_PHASE_FULL_MOON
        elif illuminationPercentage <= 99 and illuminationPercentage > 50:
            phase = LUNAR_PHASE_WANING_GIBBOUS
        elif illuminationPercentage == 50:
            phase = LUNAR_PHASE_THIRD_QUARTER
        elif illuminationPercentage < 50 and illuminationPercentage >= 1:
            phase = LUNAR_PHASE_WANING_CRESCENT
        else: # illuminationPercentage < 1
            phase = LUNAR_PHASE_NEW_MOON

    return phase


def __calculateSun( utcNow, data, timeScale, observer, ephemeris ):
    sun = ephemeris[ SUN ]
    neverUp = __calculateCommon( utcNow, data, timeScale, observer, sun, AstronomicalBodyType.Sun, NAME_TAG_SUN )
    if not neverUp:
#TODO Skyfield does not calculate dawn/dusk, but there is a workaround
# https://github.com/skyfielders/python-skyfield/issues/225
        __calculateEclipse( utcNow.utc_datetime().replace( tzinfo = None ), data, AstronomicalBodyType.Sun, NAME_TAG_SUN )


# Calculate next eclipse for the Sun or Moon.
def __calculateEclipse( utcNow, data, astronomicalBodyType, dataTag ):
    eclipseInformation = eclipse.getEclipseForUTC( utcNow, astronomicalBodyType == AstronomicalBodyType.Moon )
    key = ( astronomicalBodyType, dataTag )
    data[ key + ( DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ] + ".0" # Needed to bring the date/time format into line with date/time generated by PyEphem.
    data[ key + ( DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
    data[ key + ( DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
    data[ key + ( DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


def __calculatePlanets( utcNow, data, timeScale, observer, ephemeris, planets ):
    for planet in planets:
        __calculateCommon( utcNow, data, timeScale, observer, ephemeris[ planet ], AstronomicalBodyType.Planet, planet )


#TODO According to 
#     https://github.com/skyfielders/python-skyfield/issues/39
#     https://github.com/skyfielders/python-skyfield/pull/40
# skyfield might support somehow star names out of the box...
# ...so that means taking the data, selecting only ephemerisStars of magnitude 2.5 or so and keep those.
# See revision 999 for code to filter ephemerisStars by magnitude.
def __calculateStars( utcNow, data, timeScale, observer, ephemeris, stars ):
    for star in stars:
        __calculateCommon( utcNow, data, timeScale, observer, Star.from_dataframe( ephemeris.loc[ STARS[ star ] ] ), AstronomicalBodyType.Star, star )


def __calculateCommon( utcNow, data, timeScale, observer, body, astronomicalBodyType, nameTag ):
    neverUp = False
    key = ( astronomicalBodyType, nameTag )

    utcNowDateTime = utcNow.utc_datetime()
    t0 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day, utcNowDateTime.hour )
    t1 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day + 1, utcNowDateTime.hour )

#     t, y = almanac.find_discrete( t0, t1, almanac.sunrise_sunset( ephemeris, topos ) )  #TODO Original Skyfield function only supports sun rise/set.
    t, y = almanac.find_discrete( t0, t1, __bodyrise_bodyset( observer, body ) )
    if t:
        t = t.utc_iso( delimiter = ' ' )
        if y[ 0 ]:
            data[ key + ( DATA_RISE_TIME, ) ] = str( t[ 0 ][ : -1 ] )
            data[ key + ( DATA_SET_TIME, ) ] = str( t[ 1 ][ : -1 ] )

        else:
            data[ key + ( DATA_RISE_TIME, ) ] = str( t[ 1 ][ : -1 ] )
            data[ key + ( DATA_SET_TIME, ) ] = str( t[ 0 ][ : -1 ] )

    else:
#        if almanac.sunrise_sunset( ephemeris, topos )( t0 ): #TODO Original Skyfield function only supports sun rise/set.
        if __bodyrise_bodyset( observer, body )( t0 ):
            data[ key + ( DATA_MESSAGE, ) ] = MESSAGE_BODY_ALWAYS_UP
        else:
            neverUp = True

    if not neverUp:
        apparent = observer.at( utcNow ).observe( body ).apparent()
        alt, az, distance = apparent.altaz()
        data[ key + ( DATA_AZIMUTH, ) ] = str( az )
        data[ key + ( DATA_ALTITUDE, ) ] = str( alt )

    return neverUp


#TODO Only called in one place...and if so, just move the code in place and delete this function.
def __getSkyfieldObserver( latitude, longitude, elevation, earth ):
    return earth + Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )


#TODO Not used...delete?
def __getSkyfieldTopos( latitude, longitude, elevation ):
    return Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )


#TODO Have copied the code from skyfield/almanac.py as per
# https://github.com/skyfielders/python-skyfield/issues/226
# to compute rise/set for any body.
def __bodyrise_bodyset( observer, body ):

    def is_body_up_at( t ):
        t._nutation_angles = iau2000b( t.tt )
        return observer.at( t ).observe( body ).apparent().altaz()[ 0 ].degrees > -0.8333

    is_body_up_at.rough_period = 0.5

    return is_body_up_at


# Loads the Skyfield catalogue of stars and filters out those not listed as common named.
# The final list of stars range in magnitude up to around 12.
# The catalogue contains at least 1500 stars of magnitude 5 or less which are not common named.
# Including those stars, or even all stars up to say magnitude 15 say, totals over 100,000 and is impractical.
#
# Common name stars:
#     https://www.cosmos.esa.int/web/hipparcos/common-star-names
#
# Format of Skyfield catalogue:
#     ftp://cdsarc.u-strasbg.fr/cats/I/239/ReadMe
def createListOfCommonNamedStars():
    import os.path
    catalogue = hipparcos.URL[ hipparcos.URL.rindex( "/" ) + 1 : ] # First time Skyfield is run, the catalogue is downloaded.
    if not os.path.isfile( catalogue ):
        print( "Downloading star catalogue..." )
        load.open( hipparcos.URL )
        print( "Done" )

    print( "Creating list of common-named stars..." )
    hipparcosIdentifiers = list( STARS.values() )
    with gzip.open( catalogue, "rb" ) as inFile, gzip.open( EPHEMERIS_STARS, "wb" ) as outFile:
        for line in inFile:
            hip = int( line.decode()[ 8 : 14 ].strip() )
            if hip in hipparcosIdentifiers:
                outFile.write( line )

    print( "Done" )

createListOfCommonNamedStars()



# Compute the bright limb angle (relative to zenith) between the sun and a planetary body (typically the moon).
# Measured in degrees counter clockwise from a positive y axis.
#
# References:
#  'Astronomical Algorithms' Second Edition by Jean Meeus (chapters 14 and 48).
#  'Practical Astronomy with Your Calculator' by Peter Duffett-Smith (chapters 59 and 68).
#  http://www.geoastro.de/moonlibration/ (pictures of moon are wrong but the data is correct).
#  http://www.geoastro.de/SME/
#  http://futureboy.us/fsp/moon.fsp
#  http://www.timeanddate.com/moon/australia/sydney
#  https://www.calsky.com/cs.cgi?cha=6&sec=1
#
# Other references...
#  http://www.mat.uc.pt/~efemast/help/en/lua_fas.htm
#  https://sites.google.com/site/astronomicalalgorithms
#  http://stackoverflow.com/questions/13463965/pyephem-sidereal-time-gives-unexpected-result
#  https://github.com/brandon-rhodes/pyephem/issues/24
#  http://stackoverflow.com/questions/13314626/local-solar-time-function-from-utc-and-longitude/13425515#13425515
#  http://astro.ukho.gov.uk/data/tn/naotn74.pdf
# def __getZenithAngleOfBrightLimb( ephemNow, data, body ):
#     city = __getCity( data, ephemNow )
#     sun = ephem.Sun( city )
#     body.compute( city )
# 
#     # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
#     y = math.cos( sun.dec ) * math.sin( sun.ra - body.ra )
#     x = math.sin( sun.dec ) * math.cos( body.dec ) - math.cos( sun.dec ) * math.sin( body.dec ) * math.cos( sun.ra - body.ra )
#     positionAngleOfBrightLimb = math.atan2( y, x )
# 
#     # Astronomical Algorithms by Jean Meeus, Second Edition, page 92.
#     # https://tycho.usno.navy.mil/sidereal.html
#     # http://www.wwu.edu/skywise/skymobile/skywatch.html
#     # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
#     hourAngle = city.sidereal_time() - body.ra
# 
#     # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
#     y = math.sin( hourAngle )
#     x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
#     parallacticAngle = math.atan2( y, x )
# 
#     return math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )
# 
# 
# 
# 
# 
# #TOOO Reading on how to maybe calculate hour angle, sidereal time and so on...
# # https://www.madinstro.net/sundry/navcel.html
# # https://www.quora.com/How-do-I-calculate-the-hour-angle
# # https://astronomy.stackexchange.com/questions/12666/calculation-of-hour-angle
# # https://nptel.ac.in/courses/105107122/modules/module8/html/11.htm
# # https://astro.unl.edu/classaction/animations/200level/siderealTimeAndHourAngleDemo.html
# # http://faculty.virginia.edu/skrutskie/ASTR3130/notes/astr3130_week02.pdf
# # http://sundials.org/index.php/teachers-corner/sundial-mathematics
# # https://journal.hautehorlogerie.org/en/pilot-watches-mastering-the-hour-angle-ii/
# # https://en.wikipedia.org/wiki/Hour_angle
# # https://astronavigationdemystified.com/local-hour-angle-and-greenwich-hour-angle/
# 
# 
# def getZenithAngleOfBrightLimbSkyfield( timeScale, utcNow, ephemeris, observer, bodyRA, bodyDec, ):
#     sunRA, sunDec, earthDistance = observer.at( utcNow ).observe( ephemeris[ SKYFIELD_PLANET_SUN ] ).apparent().radec()
# 
#     # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
#     y = math.cos( sunDec.radians ) * math.sin( sunRA.radians - bodyRA.radians )
#     x = math.sin( sunDec.radians ) * math.cos( bodyDec.radians ) - math.cos( sunDec.radians ) * math.sin( bodyDec.radians ) * math.cos( sunRA.radians - bodyRA.radians )
#     positionAngleOfBrightLimb = math.atan2( y, x )
# 
#     # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
# 
# #TODO Is this screwing up the timescale?
# #     print( "Local sidereal time:", timeScale.utc( utcNow.replace( tzinfo = pytz.timezone( "Australia/Sydney" ) ) ).gmst )
# 
# 
# #     print( "GMST", load.timescale().now().gmst )
# #     print( "GMST", utcNow.gmst )
# 
# #     https://stackoverflow.com/questions/25837452/python-get-current-time-in-right-timezone
#     from datetime import datetime, timezone, timedelta
#     utc_dt = datetime.now( timezone.utc ) # UTC time
#     dt = utc_dt.astimezone() # local time
# #     print( "UTC with timezone information:", utc_dt )
# #     print( "Local time with timezone information:", dt )
# 
#     zzz = timeScale.utc( dt )
# #     print( "UTC from time object:", zzz )
# #     print( "GMST:", zzz.gmst )
# 
#     from skyfield.units import Angle
#     longitude = None
#     for positive in observer.positives:
#         if type( positive ).__name__ == "Topos":
#             longitude = positive.longitude
#             break
# 
#     import numpy
# #     print( "GMST", utcNow.gmst, type( utcNow.gmst ) )
#     print( "GMST (hours)", utcNow.gmst, type( utcNow.gmst ) )
# #     print( "GMST radians", numpy.radians( utcNow.gmst ), type( numpy.radians( utcNow.gmst ) ) )
# #     print( "GMST angle", Angle( hours = utcNow.gmst ), Angle( hours = utcNow.gmst ) )
#     print( "Longitude", longitude, type( longitude ) ) 
#     print( "Longitude (degrees)", longitude._degrees, type( longitude ) ) 
#     print( "Longitude as time", longitude._degrees * 24.0 / 360.0 )
# #     print( "Longitude radians", longitude.radians, type( longitude.radians ) ) 
# #     print( "Longitude degrees", longitude.degrees, type( longitude.degrees ) ) 
#     print( "bodyRA", bodyRA, type( bodyRA ) )
# #     print( "bodyRA radians", bodyRA.radians, type( bodyRA.radians ) )
#     print( "bodyRA hours", bodyRA._hours, type( bodyRA._hours) )
# #     hourAngle = numpy.radians( utcNow.gmst ) - longitude.radians - bodyRA.radians
# #     print( "hour angle", numpy.radians( hourAngle ) )
#     hourAngle = utcNow.gmst - ( - 24.0 * longitude._degrees / 360.0 ) - bodyRA._hours
#     print( "hour angle", hourAngle )
# #     hourAngle = Angle( hours = utcNow.gmst ) - longitude - bodyRA
# #     print( "hour angle", hourAngle )
# 
#     import time
#     print( "Local time zone:", time.strftime( "%z" ) )
#     print( "Local time zone:", timezone( timedelta( seconds =- time.timezone ) ) )
# 
# #     from time import gmtime, strftime
# #     print(strftime("%z", gmtime()))
# #     import time; print( time.tzname )
# #     print( time.tzname[time.daylight] )
# #     print( time.localtime().tm_isdst )
# #     print( datetime.datetime.now(datetime.timezone.utc).astimezone().tzname() )
# #     print( pytz.all_timezones )
# #     utcNowSkyfield = timeScale.utc( load.timescale().now().replace( tzinfo = pytz.UTC ) )
# #     print( "Timescale now tzinfo utc gmst", utcNowSkyfield.gmst )
#     
#     
# #     sss = timeScale.utc( datetime.datetime.utcnow() )
# #     print( "Timescale datetime utc now gmst", sss.gmst )
# 
# 
# #     hourAngle = city.sidereal_time() - bodyRA
# #     y = math.sin( hourAngle )
# #     x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
# #     parallacticAngle = math.atan2( y, x )
# 
# #     hourAngleNEW = observerSiderealTime - bodyRA
# #     yNEW = math.sin( hourAngleNEW )
# #     xNEW = math.tan( observerLatitude ) * math.cos( bodyDec ) - math.sin( bodyDec ) * math.cos( hourAngleNEW )
# #     parallacticAngleNEW = math.atan2( yNEW, xNEW )
# 
# #     orig = math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )
# #     new = math.degrees( ( positionAngleOfBrightLimbNEW - parallacticAngleNEW ) % ( 2.0 * math.pi ) )
# #     return math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )
#     return ""
# 
# 
# def testSiderealTime():
#     madrid = ephem.city('Madrid')
#     madrid.date = '1978/10/3 11:32'
#     print( "Madrid", madrid.sidereal_time())
# 
# 
#     madrid = ephem.city('Sydney')
#     madrid.date = '1978/10/3 11:32'
#     print( "Sydney", madrid.sidereal_time())
# 
# 
#     ts = load.timescale()
#     t = ts.utc(1978, 10, 3,11,32, 0)
#     st = t.gmst
#     print( st )
# 
# #TODO May help...
# # https://stackoverflow.com/questions/53240745/pyephem-ra-dec-to-gha-dec
# # https://stackoverflow.com/questions/13664935/is-this-how-to-compute-greenwich-hour-angle-with-pyephem-under-python-3
# 
#     print( load.timescale().now().gmst )
# 
#     sss = ts.utc( utcNow.replace( tzinfo = pytz.UTC ) )
#     sss = ts.utc( datetime.datetime.utcnow() )
#     print( sss.gmst )
# 
#     import sys
#     sys.exit()
# 
#     ephemeris = load( SKYFIELD_EPHEMERIS_PLANETS )
#     sun = ephemeris[ SKYFIELD_PLANET_SUN ]
# 
#     observer = getSkyfieldObserver( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres, ephemeris[ SKYFIELD_PLANET_EARTH ] )
#     timescale = load.timescale()
#     utcNowSkyfield = timescale.utc( utcNow.replace( tzinfo = pytz.UTC ) )
#     apparent = observer.at( utcNowSkyfield ).observe( sun ).apparent()
#     alt, az, earthDistance = apparent.altaz()
#     sunRA, sunDEC, earthDistance = apparent.radec()
# 
#     thePlanet = ephemeris[ SKYFIELD_PLANET_SATURN ]
#     apparent = observer.at( utcNowSkyfield ).observe( thePlanet ).apparent()
#     ra, dec, earthDistance = apparent.radec()
# 
#     observerSiderealTime = utcNowSkyfield.gmst
# 
# 
#     observer = getPyephemObserver( utcNow, latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres )
#     city = ephem.city( "Sydney" )
#     city.date = utcNow
#     sun = ephem.Sun( observer )
#     saturn = ephem.Saturn( observer )
# 
#     ephemeris = load( SKYFIELD_EPHEMERIS_PLANETS )
#     sun = ephemeris[ SKYFIELD_PLANET_SUN ]
# 
#     observer = getSkyfieldObserver( latitudeDecimalDegrees, longitudeDecimalDegrees, elevationMetres, ephemeris[ SKYFIELD_PLANET_EARTH ] )
#     timescale = load.timescale()
#     utcNowSkyfield = timescale.utc( utcNow.replace( tzinfo = pytz.UTC ) )
#     apparent = observer.at( utcNowSkyfield ).observe( sun ).apparent()
#     sunRA, sunDEC, earthDistance = apparent.radec()
# 
#     apparent = observer.at( utcNowSkyfield ).observe( ephemeris[ SKYFIELD_PLANET_SATURN ] ).apparent()
#     ra, dec, earthDistance = apparent.radec()
# 
# # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
# # http://astro.subhashbose.com/siderealtime/
# # http://www.wwu.edu/skywise/skymobile/skywatch.html
# # http://www.jgiesen.de/astro/astroJS/siderealClock/
# # http://neoprogrammics.com/sidereal_time_calculator/index.php   <------ does not match the other sites.
#     observerSiderealTime = utcNowSkyfield.gmst
#     print( city.sidereal_time() )
#     print( '%.6f' % city.sidereal_time() )
#     print( observerSiderealTime )
# 
#     print( timescale.utc( utcNow.replace( tzinfo = pytz.timezone( "Australia/Sydney" ) ) ).gmst )
#     print( timescale.utc( utcNow.replace( tzinfo = pytz.timezone( "Australia/Sydney" ) ) ).gast )
