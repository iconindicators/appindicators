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

#TODO Maybe include twilight?
# https://github.com/skyfielders/python-skyfield/issues/225


from datetime import timedelta

from skyfield import almanac
from skyfield.api import EarthSatellite, load, Star, Topos
from skyfield.constants import DEG2RAD
from skyfield.data import hipparcos
from skyfield.nutationlib import iau2000b

import astrobase, eclipse, gzip, math, pytz, orbitalelement, twolineelement


class AstroSkyfield( astrobase.AstroBase ):


#TODO Need to map internally the planet names.
#TODO The indicator frontend expects just the planet names, capitalised similar to pyephem...can we internally here have a mapping?
# PLANET_MERCURY = "MERCURY BARYCENTER"
# PLANET_EARTH = "EARTH"
# PLANET_VENUS = "VENUS BARYCENTER"
# PLANET_MARS = "MARS BARYCENTER"
# PLANET_JUPITER = "JUPITER BARYCENTER"
# PLANET_SATURN = "SATURN BARYCENTER"
# PLANET_URANUS = "URANUS BARYCENTER"
# PLANET_NEPTUNE = "NEPTUNE BARYCENTER"
# PLANET_PLUTO = "PLUTO BARYCENTER"


    # Sourced from skyfield/named_stars.py
    STARS = [
        "ACHERNAR",
        "ACRUX",
        "ADHARA",
        "AGENA",
        "ALBIREO",
        "ALCOR",
        "ALDEBARAN",
        "ALDERAMIN",
        "ALGENIB",
        "ALGIEBA",
        "ALGOL",
        "ALHENA",
        "ALIOTH",
        "ALKAID",
        "ALMACH",
        "ALNAIR",
        "ALNILAM",
        "ALNITAK",
        "ALPHARD",
        "ALPHECCA",
        "ALPHERATZ",
        "ALTAIR",
        "ALUDRA",
        "ANKAA",
        "ANTARES",
        "ARCTURUS",
        "ARIDED",
        "ARIDIF",
        "ASPIDISKE",
        "ATRIA",
        "AVIOR",
        "BECRUX",
        "BELLATRIX",
        "BENETNASH",
        "BETELGEUSE",
        "BIRDUN",
        "CANOPUS",
        "CAPELLA",
        "CAPH",
        "CASTOR",
        "DENEB KAITOS",
        "DENEB",
        "DENEBOLA",
        "DIPHDA",
        "DSCHUBBA",
        "DUBHE",
        "DURRE MENTHOR",
        "ELNATH",
        "ENIF",
        "ETAMIN",
        "FOMALHAUT",
        "FORAMEN",
        "GACRUX",
        "GEMMA",
        "GIENAH",
        "GIRTAB",
        "GRUID",
        "HADAR",
        "HAMAL",
        "HERSCHEL'S GARNET STAR",
        "IZAR",
        "KAUS AUSTRALIS",
        "KOCHAB",
        "KOO SHE",
        "MARCHAB",
        "MARFIKENT",
        "MARKAB",
        "MEGREZ",
        "MEN",
        "MENKALINAN",
        "MENKENT",
        "MERAK",
        "MIAPLACIDUS",
        "MIMOSA",
        "MINTAKA",
        "MIRA",
        "MIRACH",
        "MIRFAK",
        "MIRZAM",
        "MIZAR",
        "MUHLIFEIN",
        "MURZIM",
        "NAOS",
        "NUNKI",
        "PEACOCK",
        "PHAD",
        "PHECDA",
        "POLARIS",
        "POLLUX",
        "PROCYON",
        "RAS ALHAGUE",
        "RASALHAGUE",
        "REGOR",
        "REGULUS",
        "RIGEL KENT",
        "RIGEL",
        "RIGIL KENTAURUS",
        "SABIK",
        "SADIRA",
        "SADR",
        "SAIPH",
        "SARGAS",
        "SCHEAT",
        "SCHEDAR",
        "SCUTULUM",
        "SHAULA",
        "SIRIUS",
        "SIRRAH",
        "SOUTH STAR",
        "SPICA",
        "SUHAIL",
        "THUBAN",
        "TOLIMAN",
        "TSEEN SHE",
        "TSIH",
        "TURAIS",
        "VEGA",
        "WEI",
        "WEZEN" ]


    __STARS_TO_HIP = {
        "ACHERNAR" :                7588,
        "ACRUX" :                   60718,
        "ADHARA" :                  33579,
        "AGENA" :                   68702,
        "ALBIREO" :                 95947,
        "ALCOR" :                   65477,
        "ALDEBARAN" :               21421,
        "ALDERAMIN" :               105199,
        "ALGENIB" :                 15863,
        "ALGIEBA" :                 50583,
        "ALGOL" :                   14576,
        "ALHENA" :                  31681,
        "ALIOTH" :                  62956,
        "ALKAID" :                  67301,
        "ALMACH" :                  9640,
        "ALNAIR" :                  109268,
        "ALNILAM" :                 26311,
        "ALNITAK" :                 26727,
        "ALPHARD" :                 46390,
        "ALPHECCA" :                76267,
        "ALPHERATZ" :               677,
        "ALTAIR" :                  97649,
        "ALUDRA" :                  35904,
        "ANKAA" :                   2081,
        "ANTARES" :                 80763,
        "ARCTURUS" :                69673,
        "ARIDED" :                  102098,
        "ARIDIF" :                  102098,
        "ASPIDISKE" :               45556,
        "ATRIA" :                   82273,
        "AVIOR" :                   41037,
        "BECRUX" :                  62434,
        "BELLATRIX" :               25336,
        "BENETNASH" :               67301,
        "BETELGEUSE" :              27989,
        "BIRDUN" :                  66657,
        "CANOPUS" :                 30438,
        "CAPELLA" :                 24608,
        "CAPH" :                    746,
        "CASTOR" :                  36850,
        "DENEB" :                   102098,
        "DENEB KAITOS" :            3419,
        "DENEBOLA" :                57632,
        "DIPHDA" :                  3419,
        "DSCHUBBA" :                78401,
        "DUBHE" :                   54061,
        "DURRE MENTHOR" :           8102,
        "ELNATH" :                  25428,
        "ENIF" :                    107315,
        "ETAMIN" :                  87833,
        "FOMALHAUT" :               113368,
        "FORAMEN" :                 93308,
        "GACRUX" :                  61084,
        "GEMMA" :                   76267,
        "GIENAH" :                  102488,
        "GIRTAB" :                  86228,
        "GRUID" :                   112122,
        "HADAR" :                   68702,
        "HAMAL" :                   9884,
        "HERSCHEL'S GARNET STAR" :  107259,
        "IZAR" :                    72105,
        "KAUS AUSTRALIS" :          90185,
        "KOCHAB" :                  72607,
        "KOO SHE" :                 42913,
        "MARCHAB" :                 113963,
        "MARFIKENT" :               71352,
        "MARKAB" :                  45941,
        "MEGREZ" :                  59774,
        "MEN" :                     71860,
        "MENKALINAN" :              28360,
        "MENKENT" :                 68933,
        "MERAK" :                   53910,
        "MIAPLACIDUS" :             45238,
        "MIMOSA" :                  62434,
        "MINTAKA" :                 25930,
        "MIRA" :                    10826,
        "MIRACH" :                  5447,
        "MIRFAK" :                  15863,
        "MIRZAM" :                  30324,
        "MIZAR" :                   65378,
        "MUHLIFEIN" :               61932,
        "MURZIM" :                  30324,
        "NAOS" :                    39429,
        "NUNKI" :                   92855,
        "PEACOCK" :                 100751,
        "PHAD" :                    58001,
        "PHECDA" :                  58001,
        "POLARIS" :                 11767,
        "POLLUX" :                  37826,
        "PROCYON" :                 37279,
        "RAS ALHAGUE" :             86032,
        "RASALHAGUE" :              86032,
        "REGOR" :                   39953,
        "REGULUS" :                 49669,
        "RIGEL" :                   24436,
        "RIGEL KENT" :              71683,
        "RIGIL KENTAURUS" :         71683,
        "SABIK" :                   84012,
        "SADIRA" :                  16537,
        "SADR" :                    100453,
        "SAIPH" :                   27366,
        "SARGAS" :                  86228,
        "SCHEAT" :                  113881,
        "SCHEDAR" :                 3179,
        "SCUTULUM" :                45556,
        "SHAULA" :                  85927,
        "SIRIUS" :                  32349,
        "SIRRAH" :                  677,
        "SOUTH STAR" :              104382,
        "SPICA" :                   65474,
        "SUHAIL" :                  44816,
        "THUBAN" :                  68756,
        "TOLIMAN" :                 71683,
        "TSEEN SHE" :               93308,
        "TSIH" :                    4427,
        "TURAIS" :                  45556,
        "VEGA" :                    91262,
        "WEI" :                     82396,
        "WEZEN" :                   34444 }


EPHEMERIS_PLANETS = "de438_2019-2023.bsp" # Refer to https://github.com/skyfielders/python-skyfield/issues/123
EPHEMERIS_STARS = "hip_common_name_stars.dat.gz"


#TODO Pyephem can return fractional seconds in rise/set date/times...so they have been removed...
# ...not sure if skyfield will/could have the same problem.


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
                                magnitude,
                                hideIfBelowHorizon ):

    data = { }
    timeScale = load.timescale()
    utcNowSkyfield = timeScale.utc( utcNow.replace( tzinfo = pytz.UTC ) ) #TODO In each function, so far, this is converted to a datetime...so maybe just pass in the original?
    ephemerisPlanets = load( EPHEMERIS_PLANETS )
    observer = __getSkyfieldObserver( latitude, longitude, elevation, ephemerisPlanets[ PLANET_EARTH ] )

    __calculateMoon( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets, hideIfBelowHorizon )
    __calculateSun( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets, hideIfBelowHorizon )
    __calculatePlanets( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets, planets, hideIfBelowHorizon )
    with load.open( EPHEMERIS_STARS ) as f:
        ephemerisStars = hipparcos.load_dataframe( f )

    __calculateStars( utcNowSkyfield, data, timeScale, observer, ephemerisStars, stars, hideIfBelowHorizon )

#     Comet https://github.com/skyfielders/python-skyfield/issues/196
#     utcNow = datetime.datetime.utcnow()
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.Comet, comets, cometData, magnitude, hideIfBelowHorizon )
#     print( "updateComets:", ( datetime.datetime.utcnow() - utcNow ) )
#     utcNow = datetime.datetime.utcnow()
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.MinorPlanet, minorPlanets, minorPlanetData, magnitude, hideIfBelowHorizon )
#     print( "updateMinorPlanets:", ( datetime.datetime.utcnow() - utcNow ) )

#     Satellite https://github.com/skyfielders/python-skyfield/issues/115
#     utcNow = datetime.datetime.utcnow()
    __calculateSatellites( utcNowSkyfield, data, timeScale, satellites, satelliteData )
#     print( "updateSatellites:", ( datetime.datetime.utcnow() - utcNow ) )

    return data


# http://www.ga.gov.au/geodesy/astro/moonrise.jsp
# http://futureboy.us/fsp/moon.fsp
# http://www.geoastro.de/moondata/index.html
# http://www.geoastro.de/SME/index.htm
# http://www.geoastro.de/elevazmoon/index.htm
# http://www.geoastro.de/altazsunmoon/index.htm
# http://www.geoastro.de/sundata/index.html
# http://www.satellite-calculations.com/Satellite/suncalc.htm
def __calculateMoon( utcNow, data, timeScale, observer, ephemeris, hideIfBelowHorizon ):
    key = ( AstronomicalBodyType.Moon, NAME_TAG_MOON )
    moon = ephemeris[ "MOON" ]
    neverUp = __calculateCommon( utcNow, data, timeScale, observer, moon, AstronomicalBodyType.Moon, NAME_TAG_MOON )

    illumination = str( int( almanac.fraction_illuminated( ephemeris, "MOON", utcNow ) * 100 ) ) # Needed for icon.
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

    data[ key + ( DATA_BRIGHT_LIMB, ) ] = str( int( round( __getZenithAngleOfBrightLimb( utcNow, observer, ephemeris[ "SUN" ], moon ) ) ) ) # Needed for icon.

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
def __getZenithAngleOfBrightLimb( utcNow, observer, sun, body ):

    # Get the latitude/longitude...there has to be a Topos object in the observer, because that is how Skyfield works!
    for thing in observer.positives:
        if isinstance( thing, Topos ):
            latitude = thing.latitude
            longitude = thing.longitude
            break

    sunRA, sunDec, earthDistance = observer.at( utcNow ).observe( sun ).apparent().radec()
    bodyRA, bodyDec, earthDistance = observer.at( utcNow ).observe( body ).apparent().radec()

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
    y = math.cos( sunDec.radians ) * math.sin( sunRA.radians - bodyRA.radians )
    x = math.sin( sunDec.radians ) * math.cos( bodyDec.radians ) - math.cos( sunDec.radians ) * math.sin( bodyDec.radians ) * math.cos( sunRA.radians - bodyRA.radians )
    positionAngleOfBrightLimb = math.atan2( y, x )

#TODO Are the comments below still valid?
    # Astronomical Algorithms by Jean Meeus, Second Edition, page 92.
    # https://tycho.usno.navy.mil/sidereal.html
    # http://www.wwu.edu/skywise/skymobile/skywatch.html
    # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
    observerSiderealTime = 15.0 * DEG2RAD * utcNow.gast + longitude.radians # From skyfield.earthlib.py
    hourAngle = observerSiderealTime - bodyRA.radians

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
    y = math.sin( hourAngle )
    x = math.tan( latitude.radians ) * math.cos( bodyDec.radians ) - math.sin( bodyDec.radians ) * math.cos( hourAngle )
    parallacticAngle = math.atan2( y, x )

    return ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi )


def __calculateSun( utcNow, data, timeScale, observer, ephemeris, hideIfBelowHorizon ):
    sun = ephemeris[ "SUN" ]
    neverUp = __calculateCommon( utcNow, data, timeScale, observer, sun, AstronomicalBodyType.Sun, NAME_TAG_SUN )
    if not neverUp:
#TODO Skyfield does not calculate dawn/dusk, but there is a workaround
# https://github.com/skyfielders/python-skyfield/issues/225
        __calculateEclipse( utcNow.utc_datetime().replace( tzinfo = None ), data, AstronomicalBodyType.Sun, NAME_TAG_SUN )


# Calculate next eclipse for the Sun or Moon.
def __calculateEclipse( utcNow, data, bodyType, dataTag ):
    eclipseInformation = eclipse.getEclipseForUTC( utcNow, bodyType == AstronomicalBodyType.Moon )
    key = ( bodyType, dataTag )
    data[ key + ( DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ] + ".0" # Needed to bring the date/time format into line with date/time generated by PyEphem.
    data[ key + ( DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
    data[ key + ( DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
    data[ key + ( DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


def __calculatePlanets( utcNow, data, timeScale, observer, ephemeris, planets, hideIfBelowHorizon ):
    for planet in planets:
        __calculateCommon( utcNow, data, timeScale, observer, ephemeris[ planet ], AstronomicalBodyType.Planet, planet )


#TODO According to 
#     https://github.com/skyfielders/python-skyfield/issues/39
#     https://github.com/skyfielders/python-skyfield/pull/40
# skyfield might support somehow star names out of the box...
# ...so that means taking the data, selecting only ephemerisStars of magnitude 2.5 or so and keep those.
# See revision 999 for code to filter ephemerisStars by magnitude.
def __calculateStars( utcNow, data, timeScale, observer, ephemeris, stars, hideIfBelowHorizon ):
    for star in stars:
#         mag = ephemeris.loc[ STARS[ star ] ].magnitude #TODO Leave here as we may need to compute the magnitude for the front end to submenu by mag.
        __calculateCommon( utcNow, data, timeScale, observer, Star.from_dataframe( ephemeris.loc[ STARS[ star ] ] ), AstronomicalBodyType.Star, star )


#TODO  
# https://github.com/skyfielders/python-skyfield/issues/196#issuecomment-418139819
# The MPC might provide comet / minor planet data in a different format which Skyfield can read.
def __calculateCometsOrMinorPlanets( utcNow, data, timeScale, observer, ephemeris, cometsOrMinorPlanets, cometOrMinorPlanetData, magnitude, hideIfBelowHorizon ):
    pass
#     for star in stars:
#         mag = ephemeris.loc[ STARS[ star ] ].magnitude #TODO Leave here as we may need to compute the magnitude for the front end to submenu by mag.
#         __calculateCommon( utcNow, data, timeScale, observer, Star.from_dataframe( ephemeris.loc[ STARS[ star ] ] ), AstronomicalBodyType.Star, star )


def __calculateCommon( utcNow, data, timeScale, observer, body, astronomicalBodyType, nameTag ):
    neverUp = False
    key = ( astronomicalBodyType, nameTag )

    utcNowDateTime = utcNow.utc_datetime()
    t0 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day, utcNowDateTime.hour )
    t1 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day + 2, utcNowDateTime.hour ) # Look two days ahead as one day ahead may miss the next rise or set.

    t, y = almanac.find_discrete( t0, t1, __bodyrise_bodyset( observer, body ) ) # Original Skyfield function only supports sun rise/set, so have generalised to any body.
    if t:
        t = t.utc_iso( delimiter = ' ' )
        if y[ 0 ]:
            data[ key + ( DATA_RISE_DATE_TIME, ) ] = str( t[ 0 ][ : -1 ] )
            data[ key + ( DATA_SET_DATE_TIME, ) ] = str( t[ 1 ][ : -1 ] )

        else:
            data[ key + ( DATA_RISE_DATE_TIME, ) ] = str( t[ 1 ][ : -1 ] )
            data[ key + ( DATA_SET_DATE_TIME, ) ] = str( t[ 0 ][ : -1 ] )

    else:
        if __bodyrise_bodyset( observer, body )( t0 ): # Taken and modified from Skyfield almanac.find_discrete.
            pass # Body is up (and so always up).
        else:
            neverUp = True # Body is down (and so never up). 

    if not neverUp:
        apparent = observer.at( utcNow ).observe( body ).apparent()
        alt, az, bodyDistance = apparent.altaz()
        data[ key + ( DATA_AZIMUTH, ) ] = str( az.radians )
        data[ key + ( DATA_ALTITUDE, ) ] = str( alt.radians )

    return neverUp


#TODO Only called in one place...and if so, just move the code in place and delete this function.
def __getSkyfieldObserver( latitude, longitude, elevation, earth ):
    return earth + Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )


#TODO Not used...delete?
# def __getSkyfieldTopos( latitude, longitude, elevation ):
#     return Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )


#TODO Have copied the code from skyfield/almanac.py as per
# https://github.com/skyfielders/python-skyfield/issues/226
# to compute rise/set for any body.
#
# Returns true if the body is up at the time give; false if down.
def __bodyrise_bodyset( observer, body ):

    def is_body_up_at( t ):
        t._nutation_angles = iau2000b( t.tt )
        return observer.at( t ).observe( body ).apparent().altaz()[ 0 ].degrees > -0.8333

    is_body_up_at.rough_period = 0.5

    return is_body_up_at


#TODO Might be useful:https://github.com/skyfielders/python-skyfield/issues/242

# Use TLE data collated by Dr T S Kelso (http://celestrak.com/NORAD/elements) with PyEphem to compute satellite rise/pass/set times.
#
# Other sources/background:
#   http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
#   http://spotthestation.nasa.gov/sightings
#   http://www.n2yo.com
#   http://www.heavens-above.com
#   http://in-the-sky.org
#
# For planets/stars, the immediate next rise/set time is shown.
# If already above the horizon, the set time is shown followed by the rise time for the following pass.
# This makes sense as planets/stars are slow moving.
#
# However, as satellites are faster moving and pass several times a day, a different approach is used.
# When a notification is displayed indicating a satellite is now passing overhead,
# the user would want to see the rise/set for the current pass (rather than the set for the current pass and rise for the next pass).
#
# Therefore...
#    If a satellite is yet to rise, show the upcoming rise/set time.
#    If a satellite is currently passing over, show the rise/set time for that pass.
#
# This allows the user to see the rise/set time for the current pass as it is happening.
# When the pass completes and an update occurs, the rise/set for the next pass will be displayed.
def __calculateSatellites( utcNow, data, timeScale, satellites, satelliteData ):
    for key in satellites:
        if key in satelliteData:
            __calculateNextSatellitePass( utcNow, data, timeScale, key, satelliteData[ key ] )


def __calculateNextSatellitePass( utcNow, data, timeScale, key, satelliteTLE ):
    key = ( AstronomicalBodyType.Satellite, " ".join( key ) )
    currentDateTime = utcNow.J
    endDateTime = timeScale.utc( ( utcNow.utc_datetime() + timedelta( days = 24 * 2 ) ).replace( tzinfo = pytz.UTC ) ).J #TODO Maybe pass this in as it won't change per satellite.

#TODO rise/set not yet implemented in Skyfield
# https://github.com/skyfielders/python-skyfield/issues/115
#     while currentDateTime < endDateTime:
#         satellite = EarthSatellite( satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2(), satelliteTLE.getTLETitle() )

#         city = __getCity( data, currentDateTime )
#         satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
#         satellite.compute( city )
#         try:
#             nextPass = city.next_pass( satellite )
# 
#         except ValueError:
#             if satellite.circumpolar:
#                 data[ key + ( DATA_MESSAGE, ) ] = MESSAGE_SATELLITE_IS_CIRCUMPOLAR
#                 data[ key + ( DATA_AZIMUTH, ) ] = str( satellite.az )
# 
#             break
# 
#         if not __isSatellitePassValid( nextPass ):
#             break
# 
#         # The pass is valid.  If the satellite is currently passing, work out when it rose...
#         if nextPass[ 0 ] > nextPass[ 4 ]: # The rise time is after set time, so the satellite is currently passing.
#             setTime = nextPass[ 4 ]
#             nextPass = __calculateSatellitePassForRisingPriorToNow( currentDateTime, data, satelliteTLE )
#             if nextPass is None:
#                 currentDateTime = ephem.Date( setTime + ephem.minute * 30 ) # Could not determine the rise, so look for the next pass.
#                 continue
# 
#         # Now have a satellite rise/transit/set; determine if the pass is visible.
#         passIsVisible = __isSatellitePassVisible( data, nextPass[ 2 ], satellite )
#         if not passIsVisible:
#             currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )
#             continue
# 
#         # The pass is visible and the user wants only visible passes OR the user wants any pass...
#         data[ key + ( DATA_RISE_DATE_TIME, ) ] = str( nextPass[ 0 ].datetime() )
#         data[ key + ( DATA_RISE_AZIMUTH, ) ] = str( nextPass[ 1 ] )
#         data[ key + ( DATA_SET_DATE_TIME, ) ] = str( nextPass[ 4 ].datetime() )
#         data[ key + ( DATA_SET_AZIMUTH, ) ] = str( nextPass[ 5 ] )
# 
#         break
# 
# 
# def __calculateSatellitePassForRisingPriorToNow( ephemNow, data, satelliteTLE ):
#     currentDateTime = ephem.Date( ephemNow - ephem.minute ) # Start looking from one minute ago.
#     endDateTime = ephem.Date( ephemNow - ephem.hour * 1 ) # Only look back an hour for the rise time (then just give up).
#     nextPass = None
#     while currentDateTime > endDateTime:
#         city = __getCity( data, currentDateTime )
#         satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
#         satellite.compute( city )
#         try:
#             nextPass = city.next_pass( satellite )
#             if not __isSatellitePassValid( nextPass ):
#                 nextPass = None
#                 break # Unlikely to happen but better to be safe and check!
# 
#             if nextPass[ 0 ] < nextPass[ 4 ]:
#                 break
# 
#             currentDateTime = ephem.Date( currentDateTime - ephem.minute )
# 
#         except:
#             nextPass = None
#             break # This should never happen as the satellite has a rise and set (is not circumpolar or never up).
# 
#     return nextPass
# 
# 
# def __isSatellitePassValid( satellitePass ):
#     return \
#         satellitePass is not None and \
#         len( satellitePass ) == 6 and \
#         satellitePass[ 0 ] is not None and \
#         satellitePass[ 1 ] is not None and \
#         satellitePass[ 2 ] is not None and \
#         satellitePass[ 3 ] is not None and \
#         satellitePass[ 4 ] is not None and \
#         satellitePass[ 5 ] is not None
# 
# 
# # Determine if a satellite pass is visible or not...
# #
# #    http://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
# #    http://www.celestrak.com/columns/v03n01
# #    http://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
# def __isSatellitePassVisible( data, passDateTime, satellite ):
#     city = __getCity( data, passDateTime )
#     city.pressure = 0
#     city.horizon = "-0:34"
# 
#     satellite.compute( city )
#     sun = ephem.Sun()
#     sun.compute( city )
# 
#     return satellite.eclipsed is False and \
#            sun.alt > ephem.degrees( "-18" ) and \
#            sun.alt < ephem.degrees( "-6" )


# If all stars in the Skyfield catalogue were included, up to a limit of magnitude 15,
# there would be over 100,000 stars and is impractical.
#
# Instead, present the user with the "common name" stars, see link below.
#
# Load the Skyfield catalogue of stars and filter out those not listed as "common name".
# The final list of stars range in magnitude up to around 12.
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
#                 magnitude = float( line.decode()[ 42 : 46 ].strip() )
                outFile.write( line )

    print( "Done" )

#createListOfCommonNamedStars() # Uncomment to create list of stars.