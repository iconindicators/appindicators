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


import eclipse, ephem, locale, math, satellite

from ephem.cities import _city_data


class AstronomicalBodyType: Comet, Moon, Planet, Satellite, Star, Sun = range( 6 )


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

MESSAGE_BODY_ALWAYS_UP = "BODY_ALWAYS_UP"
MESSAGE_BODY_NEVER_UP = "BODY_NEVER_UP"
MESSAGE_DATA_BAD_DATA = "DATA_BAD_DATA"
MESSAGE_DATA_NO_DATA = "DATA_NO_DATA"
MESSAGE_SATELLITE_IS_CIRCUMPOLAR = "SATELLITE_IS_CIRCUMPOLAR"
MESSAGE_SATELLITE_NEVER_RISES = "SATELLITE_NEVER_RISES"
MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME = "SATELLITE_NO_PASSES_WITHIN_TIME_FRAME"
MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS = "SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS"
MESSAGE_SATELLITE_VALUE_ERROR = "SATELLITE_VALUE_ERROR"


# Returns a dict with astronomical information...
#     Key is a tuple of AstronomicalBodyType, a name tag and a data tag.
#     Value is the data as a string.
def getAstronomicalInformation( utcNow,
                                latitude, longitude, elevation,
                                planets,
                                stars,
                                satellites, satelliteData,
                                comets, cometData, cometMaximumMagnitude ):

    data = { }

    # Used internally to create the observer/city...removed before passing back to the caller.
    data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ] = latitude
    data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ] = longitude
    data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ] = elevation

    ephemNow = ephem.Date( utcNow )
    __calculateMoon( ephemNow, data )
    __calculateSun( ephemNow, data )
    __calculatePlanets( ephemNow, data, planets )
    __calculateStars( ephemNow, data, stars )
    __calculateComets( ephemNow, data, comets, cometData, cometMaximumMagnitude )
    __calculateSatellites( ephemNow, data, satellites, satelliteData )

    del data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ]
    del data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ]
    del data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ]

    return data


# Return a list of cities, sorted alphabetically, sensitive to locale.
def getCities(): return sorted( _city_data.keys(), key = locale.strxfrm )


# Returns the latitude, longitude and elevation (all as strings) for the PyEphem city.
def getLatitudeLongitudeElevation( city ): return _city_data.get( city )[ 0 ], \
                                                  _city_data.get( city )[ 1 ], \
                                                  str( _city_data.get( city )[ 2 ] )


# http://www.ga.gov.au/geodesy/astro/moonrise.jsp
# http://futureboy.us/fsp/moon.fsp
# http://www.geoastro.de/moondata/index.html
# http://www.geoastro.de/SME/index.htm
# http://www.geoastro.de/elevazmoon/index.htm
# http://www.geoastro.de/altazsunmoon/index.htm
# http://www.geoastro.de/sundata/index.html
# http://www.satellite-calculations.com/Satellite/suncalc.htm
def __calculateMoon( ephemNow, data ):
    __calculateCommon( ephemNow, data, ephem.Moon(), AstronomicalBodyType.Moon, NAME_TAG_MOON )
    key = ( AstronomicalBodyType.Moon, NAME_TAG_MOON )
    moon = ephem.Moon()
    moon.compute( __getCity( data, ephemNow ) )
    data[ key + ( DATA_ILLUMINATION, ) ] = str( int( moon.phase ) )
    data[ key + ( DATA_PHASE, ) ] = __getLunarPhase( ephemNow, int( moon.phase ) )
    data[ key + ( DATA_FIRST_QUARTER, ) ] = str( ephem.next_first_quarter_moon( ephemNow ).datetime() )
    data[ key + ( DATA_FULL, ) ] = str( ephem.next_full_moon( ephemNow ).datetime() )
    data[ key + ( DATA_THIRD_QUARTER, ) ] = str( ephem.next_last_quarter_moon( ephemNow ).datetime() )
    data[ key + ( DATA_NEW, ) ] = str( ephem.next_new_moon( ephemNow ).datetime() )
    data[ key + ( DATA_BRIGHT_LIMB, ) ] = str( int( round( __getZenithAngleOfBrightLimb( ephemNow, data, ephem.Moon() ) ) ) ) # Pass in a clean instance (just to be safe).
    __calculateEclipse( ephemNow, data, AstronomicalBodyType.Moon, NAME_TAG_MOON )


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
def __getZenithAngleOfBrightLimb( ephemNow, data, body ):
    city = __getCity( data, ephemNow )
    sun = ephem.Sun( city )
    body.compute( city )

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
    y = math.cos( sun.dec ) * math.sin( sun.ra - body.ra )
    x = math.sin( sun.dec ) * math.cos( body.dec ) - math.cos( sun.dec ) * math.sin( body.dec ) * math.cos( sun.ra - body.ra )
    positionAngleOfBrightLimb = math.atan2( y, x )

    # Astronomical Algorithms by Jean Meeus, Second Edition, page 92.
    # https://tycho.usno.navy.mil/sidereal.html
    # http://www.wwu.edu/skywise/skymobile/skywatch.html
    # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
    hourAngle = city.sidereal_time() - body.ra

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
    y = math.sin( hourAngle )
    x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
    parallacticAngle = math.atan2( y, x )

    return math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )


# Get the lunar phase for the given date/time and illumination percentage.
#
#    ephemNow Date/time.
#    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
def __getLunarPhase( ephemNow, illuminationPercentage ):
    nextFullMoonDate = ephem.next_full_moon( ephemNow )
    nextNewMoonDate = ephem.next_new_moon( ephemNow )
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
    __calculateCommon( ephemNow, data, ephem.Sun(), AstronomicalBodyType.Sun, NAME_TAG_SUN )
    key = ( AstronomicalBodyType.Sun, NAME_TAG_SUN )
    try:
        # Dawn/Dusk.
        city = __getCity( data, ephemNow )
        city.horizon = '-6' # -6 = civil twilight, -12 = nautical, -18 = astronomical (http://stackoverflow.com/a/18622944/2156453)
        sun = ephem.Sun( city )
        dawn = city.next_rising( sun, use_center = True )
        dusk = city.next_setting( sun, use_center = True )
        data[ key + ( DATA_DAWN, ) ] = str( dawn.datetime() )
        data[ key + ( DATA_DUSK, ) ] = str( dusk.datetime() )

    except ( ephem.AlwaysUpError, ephem.NeverUpError ):
        pass # No need to add a message here as update common would already have done so.

    __calculateEclipse( ephemNow, data, AstronomicalBodyType.Sun, NAME_TAG_SUN )


# Calculate next eclipse for either the Sun or Moon.
def __calculateEclipse( ephemNow, data, astronomicalBodyType, dataTag ):
    eclipseInformation = eclipse.getEclipseForUTC( ephemNow.datetime(), astronomicalBodyType == AstronomicalBodyType.Moon )
    key = ( astronomicalBodyType, dataTag )
    if eclipseInformation is None:
        data[ key + ( DATA_MESSAGE, ) ] = MESSAGE_DATA_NO_DATA
    else:
        key = ( astronomicalBodyType, dataTag )
        data[ key + ( DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ] + ".0" # Needed to bring the date/time format into line with date/time generated by PyEphem.
        data[ key + ( DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
        data[ key + ( DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
        data[ key + ( DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


# http://www.geoastro.de/planets/index.html
# http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
def __calculatePlanets( ephemNow, data, planets ):
    for planet in planets:
        planetObject = getattr( ephem, planet.title() )()
        __calculateCommon( ephemNow, data, planetObject, AstronomicalBodyType.Planet, planet )


# http://aa.usno.navy.mil/data/docs/mrst.php
def __calculateStars( ephemNow, data, stars ):
    for star in stars:
        starObject = ephem.star( star.title() )
        __calculateCommon( ephemNow, data, starObject, AstronomicalBodyType.Star, star )


# http://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
# http://www.minorplanetcenter.net/iau/Ephemerides/Soft03.html
#TODO Check with Oleg...if we do add the abilty for multiple files,
# then rename all stuff to OE...or have a separate thing for comets and so on?
#Problem is if a user adds their own source files, then we don't know what they are...so best to keep as OE.
# Could instead have addition astro body types: NEW, asteroid, minor planets?
#Perhaps instead, keep comets as they are, but add in Minor Planets and can explain that include
# Centaurs, transneptunians and NEOs.
# This list has 4 URLs from the MPC...so how to present that to the user?
# IF we go this way, need a comment somewhere about Pluto living in the Planet tab.
#FIRST thing to do is load each of the minor planet URLs, screen out for magnitude less than 6 and do a count to see if this is worth it!
def __calculateComets( ephemNow, data, comets, cometData, cometMaximumMagnitude ):
    for key in comets:
        if key in cometData:
            comet = ephem.readdb( cometData[ key ] )
            comet.compute( __getCity( data, ephemNow ) )
            if math.isnan( comet.earth_distance ) or math.isnan( comet.phase ) or math.isnan( comet.size ) or math.isnan( comet.sun_distance ): # Have found the data file may contain ***** in lieu of actual data!
                data[ ( AstronomicalBodyType.Comet, key, DATA_MESSAGE ) ] = MESSAGE_DATA_BAD_DATA
            else:
                if float( comet.mag ) <= float( cometMaximumMagnitude ):
                    __calculateCommon( ephemNow, data, comet, AstronomicalBodyType.Comet, key )
        else:
            data[ ( AstronomicalBodyType.Comet, key, DATA_MESSAGE ) ] = MESSAGE_DATA_NO_DATA


def __calculateCommon( ephemNow, data, body, astronomicalBodyType, nameTag ):
    key = ( astronomicalBodyType, nameTag )
    try:
        city = __getCity( data, ephemNow )
        rising = city.next_rising( body )
        setting = city.next_setting( body )
        data[ key + ( DATA_RISE_TIME, ) ] = str( rising.datetime() )
        data[ key + ( DATA_SET_TIME, ) ] = str( setting.datetime() )

    except ephem.AlwaysUpError:
        data[ key + ( DATA_MESSAGE, ) ] = MESSAGE_BODY_ALWAYS_UP

    except ephem.NeverUpError:
        data[ key + ( DATA_MESSAGE, ) ] = MESSAGE_BODY_NEVER_UP

    body.compute( __getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
    data[ key + ( DATA_AZIMUTH, ) ] = str( body.az )
    data[ key + ( DATA_ALTITUDE, ) ] = str( body.alt )


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
        else:
            data[ ( AstronomicalBodyType.Satellite, " ".join( key ), DATA_MESSAGE ) ] = MESSAGE_DATA_NO_DATA


def __calculateNextSatellitePass( ephemNow, data, key, satelliteTLE ):
    key = ( AstronomicalBodyType.Satellite, " ".join( key ) )
    currentDateTime = ephemNow
    endDateTime = ephem.Date( ephemNow + ephem.hour * 24 * 2 ) # Stop looking for passes 2 days from ephemNow.
    message = None
    while currentDateTime < endDateTime:
        city = __getCity( data, currentDateTime )
        satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
        satellite.compute( city )
        try:
            nextPass = city.next_pass( satellite )

        except ValueError:
            if satellite.circumpolar:
                data[ key + ( DATA_MESSAGE, ) ] = MESSAGE_SATELLITE_IS_CIRCUMPOLAR
                data[ key + ( DATA_AZIMUTH, ) ] = str( satellite.az )
            elif satellite.neverup:
                message = MESSAGE_SATELLITE_NEVER_RISES
            else:
                message = MESSAGE_SATELLITE_VALUE_ERROR

            break

        if not __isSatellitePassValid( nextPass ):
            message = MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS
            break

        # The pass is valid.  If the satellite is currently passing, work out when it rose...
        if nextPass[ 0 ] > nextPass[ 4 ]: # The rise time is after set time, so the satellite is currently passing.
            setTime = nextPass[ 4 ]
            nextPass = __calculateSatellitePassForRisingPriorToNow( currentDateTime, data, satelliteTLE )
            if nextPass is None:
                currentDateTime = ephem.Date( setTime + ephem.minute * 30 ) # Could not determine the rise, so look for the next pass.
                continue

        # Now have a satellite rise/transit/set; determine if the pass is visible.
        passIsVisible = __isSatellitePassVisible( data, nextPass[ 2 ], satellite )
        if not passIsVisible:
            currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )
            continue

        # The pass is visible and the user wants only visible passes OR the user wants any pass...
        data[ key + ( DATA_RISE_TIME, ) ] = str( nextPass[ 0 ].datetime() )
        data[ key + ( DATA_RISE_AZIMUTH, ) ] = str( nextPass[ 1 ] )
        data[ key + ( DATA_SET_TIME, ) ] = str( nextPass[ 4 ].datetime() )
        data[ key + ( DATA_SET_AZIMUTH, ) ] = str( nextPass[ 5 ] )

        break

    if currentDateTime >= endDateTime:
        message = MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME

    if message is not None:
        data[ key + ( DATA_MESSAGE, ) ] = message


def __calculateSatellitePassForRisingPriorToNow( ephemNow, data, satelliteTLE ):
    currentDateTime = ephem.Date( ephemNow - ephem.minute ) # Start looking from one minute ago.
    endDateTime = ephem.Date( ephemNow - ephem.hour * 1 ) # Only look back an hour for the rise time (then just give up).
    nextPass = None
    while currentDateTime > endDateTime:
        city = __getCity( data, currentDateTime )
        satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
        satellite.compute( city )
        try:
            nextPass = city.next_pass( satellite )
            if not __isSatellitePassValid( nextPass ):
                nextPass = None
                break # Unlikely to happen but better to be safe and check!

            if nextPass[ 0 ] < nextPass[ 4 ]:
                break

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


# Determine if a satellite pass is visible or not...
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


def __getCity( data, date ):
    city = ephem.city( "London" ) # Put in a city name known to exist in PyEphem then doctor to the correct lat/long/elev.
    city.date = date
    city.lat = data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ]
    city.lon = data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ]
    city.elev = float( data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ] )

    return city


from urllib.request import urlopen
import datetime, pythonutils, re

urls = [ "file:///home/bernard/Desktop/MinorPlanetCenter/Soft03Bright.txt",
         "file:///home/bernard/Desktop/MinorPlanetCenter/Soft03CritList.txt",
         "file:///home/bernard/Desktop/MinorPlanetCenter/Soft03Distant.txt",
         "file:///home/bernard/Desktop/MinorPlanetCenter/Soft03Cmt.txt",
         "file:///home/bernard/Desktop/MinorPlanetCenter/Soft03Unusual.txt" ]

for url in urls:
    print( url, "\n" )
    data = urlopen( url, timeout = pythonutils.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
    for i in range( 0, len( data ) ):
        if not data[ i ].startswith( "#" ):
            cometName = re.sub( "\s\s+", "", data[ i ][ 0 : data[ i ].index( "," ) ] ) # Found that the comet name can have multiple whitespace, so remove.
            comet = ephem.readdb( data[ i ] )
            comet.compute( ephem.city( "Sydney" ) )
            if math.isnan( comet.earth_distance ) or math.isnan( comet.phase ) or math.isnan( comet.size ) or math.isnan( comet.sun_distance ): # Have found the data file may contain ***** in lieu of actual data!
                continue
            else:
                if float( comet.mag ) <= 2.0:
                    print( "\t", cometName, comet.mag )

    print()
