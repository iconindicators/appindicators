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


from skyfield import almanac
from skyfield.api import load, Topos

# from skyfield import almanac, positionlib
# from skyfield.api import load, Star, Topos
# from skyfield.data import hipparcos
# from pandas.core.frame import DataFrame

import eclipse, gzip, pytz
# import datetime, ephem, gzip, math, pytz


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


# https://www.cosmos.esa.int/web/hipparcos/common-star-names
# This list contained a duplicate Hipparcos Identifier of 68702 for a star with two common names: Agena and Hadar.
# The official name is Hadar and so Agena has been removed.
STARS_COMMON_NAMES = [ \
    [ "Acamar", 13847 ], \
    [ "Achernar", 7588 ], \
    [ "Acrux", 60718 ], \
    [ "Adhara", 33579 ], \
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


LUNAR_PHASE_FULL_MOON = "FULL_MOON"
LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
LUNAR_PHASE_NEW_MOON = "NEW_MOON"
LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"

PLANET_EARTH = "earth"
PLANET_SATURN = "saturn barycenter"

MOON = "moon"
SUN = "sun"

EPHEMERIS_PLANETS = "skyfield/de438_2019-2023.bsp"
EPHEMERIS_STARS = "skyfield/hip_common_name_stars.dat.gz"

MESSAGE_BODY_ALWAYS_UP = "BODY_ALWAYS_UP"
MESSAGE_SATELLITE_IS_CIRCUMPOLAR = "SATELLITE_IS_CIRCUMPOLAR"


def getAstronomicalInformation( utcNow,
                                latitude, longitude, elevation,
                                planets,
                                stars,
                                satellites, satelliteData,
                                comets, cometData,
                                minorPlanets, minorPlanetData,
                                magnitude ):

    latitude = -38
    print( "latitude", latitude )

    data = { }

    # Used internally to create the observer/city...removed before passing back to the caller.
    data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ] = latitude
    data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ] = longitude
    data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ] = elevation

    timeScale = load.timescale()
    utcNowSkyfield = timeScale.utc( utcNow.replace( tzinfo = pytz.UTC ) ) #TODO In each function, so far, this is converted to a datetime...so maybe just pass in the original?
    ephemerisPlanets = load( EPHEMERIS_PLANETS )
    observer = getSkyfieldObserver( latitude, longitude, elevation, ephemerisPlanets[ PLANET_EARTH ] )
    topos = getSkyfieldTopos( latitude, longitude, elevation )

    __calculateMoon( utcNowSkyfield, data, timeScale, observer, topos, ephemerisPlanets )
#     __calculateSun( ephemNow, data )
#     __calculatePlanets( ephemNow, data, planets )
#     __calculateStars( ephemNow, data, stars )
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.Comet, comets, cometData, magnitude )
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.MinorPlanet, minorPlanets, minorPlanetData, magnitude )
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
def __calculateMoon( utcNow, data, timeScale, observer, topos, ephemeris ):
    key = ( AstronomicalBodyType.Moon, NAME_TAG_MOON )
    moon = ephemeris[ MOON ]
    neverUp = __calculateCommon( utcNow, data, timeScale, observer, topos, ephemeris, moon, AstronomicalBodyType.Moon, NAME_TAG_MOON )

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


# Calculate next eclipse for either the Sun or Moon.
def __calculateEclipse( utcNow, data, astronomicalBodyType, dataTag ):
    eclipseInformation = eclipse.getEclipseForUTC( utcNow, astronomicalBodyType == AstronomicalBodyType.Moon )
    key = ( astronomicalBodyType, dataTag )
    data[ key + ( DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ] + ".0" # Needed to bring the date/time format into line with date/time generated by PyEphem.
    data[ key + ( DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
    data[ key + ( DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
    data[ key + ( DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


def __calculateCommon( utcNow, data, timeScale, observer, topos, ephemeris, body, astronomicalBodyType, nameTag ):
    neverUp = False
    key = ( astronomicalBodyType, nameTag )

    utcNowDateTime = utcNow.utc_datetime()
    t0 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day, utcNowDateTime.hour )
    t1 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day + 1, utcNowDateTime.hour )

    t, y = almanac.find_discrete( t0, t1, almanac.sunrise_sunset( ephemeris, topos ) )
    if t:
        t = t.utc_iso( delimiter = ' ' )
        if y[ 0 ]:
            data[ key + ( DATA_RISE_TIME, ) ] = str( t[ 0 ][ : -1 ] )
            data[ key + ( DATA_SET_TIME, ) ] = str( t[ 1 ][ : -1 ] )

        else:
            data[ key + ( DATA_RISE_TIME, ) ] = str( t[ 1 ][ : -1 ] )
            data[ key + ( DATA_SET_TIME, ) ] = str( t[ 0 ][ : -1 ] )

    else:
        if almanac.sunrise_sunset( ephemeris, topos )( t0 ):
            data[ key + ( DATA_MESSAGE, ) ] = MESSAGE_BODY_ALWAYS_UP
        else:
            neverUp = True

    if not neverUp:
        apparent = observer.at( utcNow ).observe( body ).apparent()
        alt, az, distance = apparent.altaz()
        data[ key + ( DATA_AZIMUTH, ) ] = str( az )
        data[ key + ( DATA_ALTITUDE, ) ] = str( alt )

    return neverUp


def getSkyfieldObserver( latitude, longitude, elevation, earth ):
    return earth + Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )


def getSkyfieldTopos( latitude, longitude, elevation ):
    return Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )


#TODO Keep this here?
def filterStarsByHipparcosIdentifier( hipparcosInputGzipFile, hipparcosOutputGzipFile, hipparcosIdentifiers ):
    try:
        with gzip.open( hipparcosInputGzipFile, "rb" ) as inFile, gzip.open( hipparcosOutputGzipFile, "wb" ) as outFile:
            for line in inFile:
                hip = int( line.decode()[ 9 : 14 ].strip() ) #TODO Was 2 but according to ftp://cdsarc.u-strasbg.fr/cats/I/239/ReadMe it should be 9.
                if hip in hipparcosIdentifiers:
#                     magnitude = int( line.decode()[ 42 : 46 ].strip() ) #TODO This barfs...dunno why as it should be the same as pulling out the hip.
#                     print( hip, magnitude )
                    outFile.write( line )

    except Exception as e:
        print( e ) #TODO Handle betterer.