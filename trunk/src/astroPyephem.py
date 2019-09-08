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


# Calculate astronomical information using PyEphem.


import eclipse, ephem, locale, math, orbitalelement, twolineelement

from ephem.cities import _city_data


class AstronomicalBodyType: Comet, MinorPlanet, Moon, Planet, Satellite, Star, Sun = range( 7 )


#TODO Need to test with a lat/long such that bodies rise/set, always up and never up.


DATA_ALTITUDE = "ALTITUDE"
DATA_AZIMUTH = "AZIMUTH"
DATA_BRIGHT_LIMB = "BRIGHT LIMB" # Used for creating an icon; not intended for display to the user.
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
DATA_MAGNITUDE = "MAGNITUDE"
DATA_NEW = "NEW"
DATA_PHASE = "PHASE"
DATA_RISE_AZIMUTH = "RISE AZIMUTH"
DATA_RISE_DATE_TIME = "RISE DATE TIME"
DATA_SET_AZIMUTH = "SET AZIMUTH"
DATA_SET_DATE_TIME = "SET DATE TIME"
DATA_THIRD_QUARTER = "THIRD QUARTER"

DATA_INTERNAL = [
    DATA_BRIGHT_LIMB,
    DATA_ELEVATION,
    DATA_ILLUMINATION,
    DATA_MAGNITUDE ] #TODO If magnitude is shown in the menu, then maybe this should be available to the user (and not internal).

#TODO Are these sub-lists needed?  They are not referenced in the indicator front end.
DATA_COMET = [
    DATA_RISE_AZIMUTH,
    DATA_RISE_DATE_TIME,
    DATA_SET_AZIMUTH,
    DATA_SET_DATE_TIME ]

DATA_MINOR_PLANET = [
    DATA_RISE_DATE_TIME,
    DATA_SET_AZIMUTH,
    DATA_SET_DATE_TIME ]

DATA_MOON = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_BRIGHT_LIMB,
    DATA_ECLIPSE_DATE_TIME,
    DATA_ECLIPSE_LATITUDE,
    DATA_ECLIPSE_LONGITUDE,
    DATA_ECLIPSE_TYPE,
    DATA_ILLUMINATION,
    DATA_PHASE,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME ]

DATA_PLANET = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME ]

DATA_SATELLITE = [
    DATA_RISE_AZIMUTH,
    DATA_RISE_DATE_TIME,
    DATA_SET_AZIMUTH,
    DATA_SET_DATE_TIME ]

DATA_STAR = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME ]

DATA_SUN = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_ECLIPSE_DATE_TIME,
    DATA_ECLIPSE_LATITUDE,
    DATA_ECLIPSE_LONGITUDE,
    DATA_ECLIPSE_TYPE,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME ]

NAME_TAG_CITY = "CITY"
NAME_TAG_MOON = "MOON"
NAME_TAG_SUN = "SUN"

PLANET_MERCURY = "MERCURY"
PLANET_VENUS = "VENUS"
PLANET_MARS = "MARS"
PLANET_JUPITER = "JUPITER"
PLANET_SATURN = "SATURN"
PLANET_URANUS = "URANUS"
PLANET_NEPTUNE = "NEPTUNE"
PLANET_PLUTO = "PLUTO"

PLANETS = [ PLANET_MERCURY, PLANET_VENUS, PLANET_MARS, PLANET_JUPITER, PLANET_SATURN, PLANET_URANUS, PLANET_NEPTUNE, PLANET_PLUTO ]

# From cns_namemap in ephem.stars.stars
STARS = [
    "ACHERNAR",
    "ADARA",
    "AGENA",
    "ALBEREO",
    "ALCAID",
    "ALCOR",
    "ALCYONE",
    "ALDEBARAN",
    "ALDERAMIN",
    "ALFIRK",
    "ALGENIB",
    "ALGIEBA",
    "ALGOL",
    "ALHENA",
    "ALIOTH",
    "ALMACH",
    "ALNAIR",
    "ALNILAM",
    "ALNITAK",
    "ALPHARD",
    "ALPHECCA",
    "ALSHAIN",
    "ALTAIR",
    "ANTARES",
    "ARCTURUS",
    "ARKAB POSTERIOR",
    "ARKAB PRIOR",
    "ARNEB",
    "ATLAS",
    "BELLATRIX",
    "BETELGEUSE",
    "CANOPUS",
    "CAPELLA",
    "CAPH",
    "CASTOR",
    "CEBALRAI",
    "DENEB",
    "DENEBOLA",
    "DUBHE",
    "ELECTRA",
    "ELNATH",
    "ENIF",
    "ETAMIN",
    "FOMALHAUT",
    "GIENAH CORVI",
    "HAMAL",
    "IZAR",
    "KAUS AUSTRALIS",
    "KOCHAB",
    "MAIA",
    "MARKAB",
    "MEGREZ",
    "MENKALINAN",
    "MENKAR",
    "MERAK",
    "MEROPE",
    "MIMOSA",
    "MINKAR",
    "MINTAKA",
    "MIRACH",
    "MIRZAM",
    "MIZAR",
    "NAOS",
    "NIHAL",
    "NUNKI",
    "PEACOCK",
    "PHECDA",
    "POLARIS",
    "POLLUX",
    "PROCYON",
    "RASALGETHI",
    "RASALHAGUE",
    "REGULUS",
    "RIGEL",
    "RUKBAT",
    "SADALMELIK",
    "SADR",
    "SAIPH",
    "SCHEAT",
    "SCHEDAR",
    "SHAULA",
    "SHELIAK",
    "SIRIUS",
    "SIRRAH",
    "SPICA",
    "SULAFAT",
    "TARAZED",
    "TAYGETA",
    "THUBAN",
    "UNUKALHAI",
    "VEGA",
    "VINDEMIATRIX",
    "WEZEN",
    "ZAURAK" ]

LUNAR_PHASE_FULL_MOON = "FULL_MOON"
LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
LUNAR_PHASE_NEW_MOON = "NEW_MOON"
LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"

MAGNITUDE_MAXIMUM = 15.0 # No point going any higher for the typical home astronomer.
MAGNITUDE_MINIMUM = -10.0 # Have found magnitudes in comet OE data which are brighter than the sun...so set a lower limit.

DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS = "%Y-%m-%d %H:%M:%S"


# Returns a dict with astronomical information...
#     Key is a tuple of AstronomicalBodyType, a name tag and a data tag.
#     Value is the data as a string.
#
# NOTE: Any error when computing a body or if a body never rises, no result is added for that body.
#TODO Consider this...
#If the body is never up, no data added.
#If the body is always up, add az/alt/mag
#If the body is below the horizon, add rise/mag
#If the body is above the horizon, add set/alt/az/mag
#Add this information to the function header.
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
    data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ] = str( latitude )
    data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ] = str( longitude )
    data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ] = str( elevation )

    ephemNow = ephem.Date( utcNow )

    import datetime
    utcNow = datetime.datetime.utcnow()
    __calculateMoon( ephemNow, data )
    print( "updateMoon:", ( datetime.datetime.utcnow() - utcNow ) )

    utcNow = datetime.datetime.utcnow()
    __calculateSun( ephemNow, data )
    print( "updateSun:", ( datetime.datetime.utcnow() - utcNow ) )

    utcNow = datetime.datetime.utcnow()
    __calculatePlanets( ephemNow, data, planets )
    print( "updatePlanets:", ( datetime.datetime.utcnow() - utcNow ) )

    utcNow = datetime.datetime.utcnow()
    __calculateStars( ephemNow, data, stars )
    print( "updateStars:", ( datetime.datetime.utcnow() - utcNow ) )

    utcNow = datetime.datetime.utcnow()
    __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.Comet, comets, cometData, magnitude )
    print( "updateComets:", ( datetime.datetime.utcnow() - utcNow ) )

    utcNow = datetime.datetime.utcnow()
    __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.MinorPlanet, minorPlanets, minorPlanetData, magnitude )
    print( "updateMinorPlanets:", ( datetime.datetime.utcnow() - utcNow ) )

    utcNow = datetime.datetime.utcnow()
    __calculateSatellites( ephemNow, data, satellites, satelliteData )
    print( "updateSatellites:", ( datetime.datetime.utcnow() - utcNow ) )

    del data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ]
    del data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ]
    del data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ]

    return data


# Return a list of cities, sorted alphabetically, sensitive to locale.
def getCities(): return sorted( _city_data.keys(), key = locale.strxfrm )


# Returns the latitude, longitude and elevation for the PyEphem city.
def getLatitudeLongitudeElevation( city ): return float( _city_data.get( city )[ 0 ] ), \
                                                  float( _city_data.get( city )[ 1 ] ), \
                                                  _city_data.get( city )[ 2 ]

# Takes a dictionary of orbital element data (for comets or minor planet),
# in which the key is the body name and value is the orbital element data.
#
# On success, returns a similarly formatted, non-empty, dictionary
# in which each item has a magnitude less than or equal to the maximum magnitude.
# On error or if no data remains (magnitude is too low for example), None is returned.
def getOrbitalElementsLessThanMagnitude( orbitalElementData, maximumMagnitude ):
    results = { }
    for key in orbitalElementData:
        body = ephem.readdb( orbitalElementData[ key ].getData() )
        body.compute( ephem.city( "London" ) ) # Use any city; makes no difference to obtain the magnitude.
        bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
        if not bad and body.mag >= MAGNITUDE_MINIMUM and body.mag <= maximumMagnitude:
            results[ key ] = orbitalElementData[ key ]

    if not results:
        results = None

    return results


# http://www.ga.gov.au/geodesy/astro/moonrise.jsp
# http://futureboy.us/fsp/moon.fsp
# http://www.geoastro.de/moondata/index.html
# http://www.geoastro.de/SME/index.htm
# http://www.geoastro.de/elevazmoon/index.htm
# http://www.geoastro.de/altazsunmoon/index.htm
# http://www.geoastro.de/sundata/index.html
# http://www.satellite-calculations.com/Satellite/suncalc.htm
def __calculateMoon( ephemNow, data ):
    neverUp = __calculateCommon( ephemNow, data, ephem.Moon(), AstronomicalBodyType.Moon, NAME_TAG_MOON )
    moon = ephem.Moon()
    moon.compute( __getCity( data, ephemNow ) )
    key = ( AstronomicalBodyType.Moon, NAME_TAG_MOON )
    data[ key + ( DATA_ILLUMINATION, ) ] = str( int( moon.phase ) ) # Needed for icon.
    data[ key + ( DATA_PHASE, ) ] = __getLunarPhase( int( moon.phase ), ephem.next_full_moon( ephemNow ), ephem.next_new_moon( ephemNow ) ) # Need for notification.
    data[ key + ( DATA_BRIGHT_LIMB, ) ] = str( __getZenithAngleOfBrightLimb( ephemNow, data, ephem.Moon() ) ) # Needed for icon.

#TODO Debug
    print( "Moon illumination:", data[ key + ( DATA_ILLUMINATION, ) ] )
    print( "Moon phase:", data[ key + ( DATA_PHASE, ) ] )
    print( "Moon bright limb (radians):", data[ key + ( DATA_BRIGHT_LIMB, ) ] )
    print( "Moon bright limb (degrees):", math.degrees( float( data[ key + ( DATA_BRIGHT_LIMB, ) ] ) ) )

    if not neverUp:
        data[ key + ( DATA_FIRST_QUARTER, ) ] = __toDateTimeString( ephem.next_first_quarter_moon( ephemNow ).datetime() )
        data[ key + ( DATA_FULL, ) ] = __toDateTimeString( ephem.next_full_moon( ephemNow ).datetime() )
        data[ key + ( DATA_THIRD_QUARTER, ) ] = __toDateTimeString( ephem.next_last_quarter_moon( ephemNow ).datetime() )
        data[ key + ( DATA_NEW, ) ] = __toDateTimeString( ephem.next_new_moon( ephemNow ).datetime() )
        __calculateEclipse( ephemNow.datetime(), data, AstronomicalBodyType.Moon, NAME_TAG_MOON )


# Compute the bright limb angle (relative to zenith) between the sun and a planetary body (typically the moon).
# Measured in radians counter clockwise from a positive y axis.
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
def __getZenithAngleOfBrightLimb( ephemNow, data, body ):
    city = __getCity( data, ephemNow )
    sun = ephem.Sun( city )
    body.compute( city )

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
    y = math.cos( sun.dec ) * math.sin( sun.ra - body.ra )
    x = math.sin( sun.dec ) * math.cos( body.dec ) - math.cos( sun.dec ) * math.sin( body.dec ) * math.cos( sun.ra - body.ra )
    positionAngleOfBrightLimb = math.atan2( y, x )
    print( "Position angle of bright limb (radians):", positionAngleOfBrightLimb ) #TODO Test

    # Astronomical Algorithms by Jean Meeus, Second Edition, page 92.
    # https://tycho.usno.navy.mil/sidereal.html
    # http://www.wwu.edu/skywise/skymobile/skywatch.html
    # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
    hourAngle = city.sidereal_time() - body.ra

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
    y = math.sin( hourAngle )
    x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
    parallacticAngle = math.atan2( y, x )
    print( "Parallactic angle (radians):", parallacticAngle ) #TODO Test

    return ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi )


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


# http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
# http://www.ga.gov.au/geodesy/astro/sunrise.jsp
# http://www.geoastro.de/elevaz/index.htm
# http://www.geoastro.de/SME/index.htm
# http://www.geoastro.de/altazsunmoon/index.htm
# http://futureboy.us/fsp/sun.fsp
# http://www.satellite-calculations.com/Satellite/suncalc.htm
def __calculateSun( ephemNow, data ):
    neverUp = __calculateCommon( ephemNow, data, ephem.Sun(), AstronomicalBodyType.Sun, NAME_TAG_SUN )
    if not neverUp:
        __calculateEclipse( ephemNow.datetime(), data, AstronomicalBodyType.Sun, NAME_TAG_SUN )


# Calculate next eclipse for either the Sun or Moon.
def __calculateEclipse( utcNow, data, astronomicalBodyType, dataTag ):
    eclipseInformation = eclipse.getEclipseForUTC( utcNow, astronomicalBodyType == AstronomicalBodyType.Moon )
    key = ( astronomicalBodyType, dataTag )
    data[ key + ( DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ]
    data[ key + ( DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
    data[ key + ( DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
    data[ key + ( DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


# http://www.geoastro.de/planets/index.html
# http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
def __calculatePlanets( ephemNow, data, planets ):
    print( "Number of planets:", len(planets))#TODO debug
    for planet in planets:
        planetObject = getattr( ephem, planet.title() )()
        __calculateCommon( ephemNow, data, planetObject, AstronomicalBodyType.Planet, planet )


# http://aa.usno.navy.mil/data/docs/mrst.php
def __calculateStars( ephemNow, data, stars ):
    print( "Number of stars:", len(stars))#TODO debug
#     mags = [ 0, 0, 0, 0, 0, 0, 0, 0 ]
    for star in stars:
        starObject = ephem.star( star.title() )
        __calculateCommon( ephemNow, data, starObject, AstronomicalBodyType.Star, star )

#         key = ( AstronomicalBodyType.Star, star, DATA_MAGNITUDE ) 
#         if key in data: 
#             print( data[ key ] ) 
#             mags[ int( float( data[ key ] ) + 2 ) ] += 1 

#     print( "Star mags:", mags ) 


# Compute data for comets or minor planets.
# Reference https://minorplanetcenter.net//iau/Ephemerides/Soft03.html
# The default source for comets is https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
# The default source for minor planets is https://minorplanetcenter.net/iau/Ephemerides/Unusual/Soft03Unusual.txt
# Have tried the other data sources for minor planets (NEOs, centaurs, transneptunians) and none have magnitude less than 6.
def __calculateCometsOrMinorPlanets( ephemNow, data, astronomicalBodyType, cometsOrMinorPlanets, cometOrMinorPlanetData, magnitude ):
#TODO Debug
#     mags = [ 0, 0, 0, 0, 0, 0 ]
#     magsAndAbove = [ 0, 0, 0, 0, 0, 0 ]


#TODO Have noticed that we get a pile of minor planets but all are always above the horizon (except for one that is always up).
#Why are there none below the horzion (with just a rise date/time)?
    for key in cometsOrMinorPlanets:
        if key in cometOrMinorPlanetData:
            body = ephem.readdb( cometOrMinorPlanetData[ key ].getData() )
            body.compute( __getCity( data, ephemNow ) )
            bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
            if not bad and body.mag >= MAGNITUDE_MINIMUM and body.mag <= magnitude:
                __calculateCommon( ephemNow, data, body, astronomicalBodyType, key )

#TODO Debug
#                 mags[ int( body.mag ) ] += 1 
#                 if body.mag <= MAGNITUDE_MINIMUM: print( "Dodgy magnitude:", body.mag )
#                 if float( data[ ( astronomicalBodyType, key, DATA_ALTITUDE ) ] ) > 0:
#                     magsAndAbove[ int( body.mag ) ] += 1


#TODO Debug
#     print( mags )
#     print( magsAndAbove )


def __calculateCommon( ephemNow, data, body, astronomicalBodyType, nameTag ):
    neverUp = False
    key = ( astronomicalBodyType, nameTag )
    try:
        city = __getCity( data, ephemNow )
        rising = city.next_rising( body )
        setting = city.next_setting( body )

        if rising > setting: # Above the horizon.
            data[ key + ( DATA_SET_DATE_TIME, ) ] = __toDateTimeString( setting.datetime() )
        else: # Below the horizon.
            data[ key + ( DATA_RISE_DATE_TIME, ) ] = __toDateTimeString( rising.datetime() )

    except ephem.AlwaysUpError:
        pass

    except ephem.NeverUpError:
        neverUp = True

    if not neverUp:
        if key + ( DATA_RISE_DATE_TIME, ) not in data:
            body.compute( __getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
            data[ key + ( DATA_AZIMUTH, ) ] = str( repr( body.az ) )
            data[ key + ( DATA_ALTITUDE, ) ] = str( repr( body.alt ) )

        if astronomicalBodyType == AstronomicalBodyType.Comet or \
           astronomicalBodyType == AstronomicalBodyType.MinorPlanet or \
           astronomicalBodyType == AstronomicalBodyType.Star:
            data[ key + ( DATA_MAGNITUDE, ) ] = str( body.mag )

#TODO Testing
        if astronomicalBodyType == AstronomicalBodyType.Star:
            print( data[ ( AstronomicalBodyType.Star, nameTag, DATA_MAGNITUDE ) ], int( float( data[ ( AstronomicalBodyType.Star, nameTag, DATA_MAGNITUDE ) ] ) ) )



    return neverUp


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
def __calculateSatellites( ephemNow, data, satellites, satelliteData ):
    for key in satellites:
        if key in satelliteData:
            __calculateNextSatellitePass( ephemNow, data, key, satelliteData[ key ] )


#TODO On Sep 1st I ran the indicator at 3pm and noticed that there were
# satellites currently in transit with a rise date/time of Aug 29 18:40
# and then satellites to rise Aug 30 4:52.
# The TLE cache file had filename of satellite-tle-20190901045141
#So something is wrong...perhaps in the string comparison of dates (might have to use datetime rather than dates).
def __calculateNextSatellitePass( ephemNow, data, key, satelliteTLE ):
    key = ( AstronomicalBodyType.Satellite, key )
    currentDateTime = ephemNow
    endDateTime = ephem.Date( ephemNow + ephem.hour * 24 ) # Stop looking for passes 24 hours from now.
    while currentDateTime < endDateTime:
        city = __getCity( data, currentDateTime )
        satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getLine1(), satelliteTLE.getLine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
        satellite.compute( city )
        try:
            nextPass = city.next_pass( satellite )

        except ValueError:
            if satellite.circumpolar:
#                 print( "circumpolar" )#TODO
                data[ key + ( DATA_AZIMUTH, ) ] = str( str( repr( satellite.az ) ) )
                data[ key + ( DATA_ALTITUDE, ) ] = str( satellite.alt )
            break

        if not __isSatellitePassValid( nextPass ):
            break

        # Determine if the pass is yet to happen or underway...
        if nextPass[ 0 ] > nextPass[ 4 ]: # The rise time is after set time, so the satellite is currently passing.
            setTime = nextPass[ 4 ]
            nextPass = __calculateSatellitePassForRisingPriorToNow( currentDateTime, data, satelliteTLE )
            if nextPass is None:
                currentDateTime = ephem.Date( setTime + ephem.minute * 30 ) # Could not determine the rise, so look for the next pass.
                continue
            
        # The satellite has a rise/transit/set; determine if the pass is visible.
        passIsVisible = __isSatellitePassVisible( data, nextPass[ 2 ], satellite )
        if not passIsVisible:
            currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 ) # Look for the next pass.
            continue

        # If a satellite is in transit or will rise within five minutes of now, then show all information...
        if nextPass[ 0 ] < ( ephem.Date( ephemNow + ephem.minute * 5 ) ):
#             print( "transit" )#TODO
            data[ key + ( DATA_RISE_DATE_TIME, ) ] = __toDateTimeString( nextPass[ 0 ].datetime() )
            data[ key + ( DATA_RISE_AZIMUTH, ) ] = str( repr( nextPass[ 1 ] ) )
            data[ key + ( DATA_SET_DATE_TIME, ) ] = __toDateTimeString( nextPass[ 4 ].datetime() )
            data[ key + ( DATA_SET_AZIMUTH, ) ] = str( repr( nextPass[ 5 ] ) )

        else: # Satellite will rise later, so only add rise time.
#             print( "below horizon" )#TODO
            data[ key + ( DATA_RISE_DATE_TIME, ) ] = __toDateTimeString( nextPass[ 0 ].datetime() )

        break


def __calculateSatellitePassForRisingPriorToNow( ephemNow, data, satelliteTLE ):
    currentDateTime = ephem.Date( ephemNow - ephem.minute ) # Start looking from one minute ago.
    endDateTime = ephem.Date( ephemNow - ephem.hour ) # Only look back an hour for the rise time (then just give up).
    nextPass = None
    while currentDateTime > endDateTime:
        city = __getCity( data, currentDateTime )
        satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getLine1(), satelliteTLE.getLine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
        satellite.compute( city )
        try:
            nextPass = city.next_pass( satellite )
            if not __isSatellitePassValid( nextPass ):
                nextPass = None
                break # Unlikely to happen but better to be safe and check!

            if nextPass[ 0 ] < nextPass[ 4 ]:
                break # Found the rise time!

            currentDateTime = ephem.Date( currentDateTime - ephem.minute )

        except:
            nextPass = None
            break # This should never happen as the satellite has a rise and set (is not circumpolar or never up).

    return nextPass


def __isSatellitePassValid( satellitePass ):
    return \
        satellitePass is not None and \
        len( satellitePass ) == 6 and \
        satellitePass[ 0 ] is not None and \
        satellitePass[ 1 ] is not None and \
        satellitePass[ 2 ] is not None and \
        satellitePass[ 3 ] is not None and \
        satellitePass[ 4 ] is not None and \
        satellitePass[ 5 ] is not None


# Determine if a satellite pass is visible.
#
#    http://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
#    http://www.celestrak.com/columns/v03n01
#    http://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
def __isSatellitePassVisible( data, passDateTime, satellite ):
    city = __getCity( data, passDateTime )
    city.pressure = 0
    city.horizon = "-0:34"

    satellite.compute( city )
    sun = ephem.Sun()
    sun.compute( city )

    return satellite.eclipsed is False and \
           sun.alt > ephem.degrees( "-18" ) and \
           sun.alt < ephem.degrees( "-6" )


def __toDateTimeString( dateTime ): return dateTime.strftime( DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )


def __getCity( data, date ):
    city = ephem.city( "London" ) # Put in a city name known to exist in PyEphem then doctor to the correct lat/long/elev.
    city.date = date
    city.lat = data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ]
    city.lon = data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ]
    city.elev = float( data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ] )

    return city