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


from ephem.cities import _city_data

import astrobase, eclipse, ephem, locale, math, orbitalelement, twolineelement


#TODO If we test with Pyephem and select some stars, then switch to Skyfield,
#what happens if a star is in pyephem but not skyfield?
#Each star function needs to guard against this?
#What about comets and other stuff?


#TODO Need to test with a lat/long such that bodies rise/set, always up and never up.


#TODO Maybe include twilight if astroSkyfield can do it?
# https://github.com/skyfielders/python-skyfield/issues/225


class AstroPyephem( astrobase.AstroBase ):


#TODO Need this comment?
# Planet names are capitalised, whereas Pyephem uses titled strings.
# At the API we accept capitalised planet names, but internally we title them to satisfy Pyephem.


    # Taken from ephem/stars.py
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


# Returns a dictionary with astronomical information:
#     Key is a tuple of BodyType, a name tag and a data tag.
#     Value is the data as a string.
#
# If a body is never up, no data is added.
# If a body is always up, azimuth/altitude are added.
# If the body is below the horizon, only the rise date/time is added.
# If the body is above the horizon, set date/time and azimuth/altitude are added.
#
# NOTE: Any error when computing a body or if a body never rises, no result is added for that body.
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

    # Used internally to create the observer/city...removed before passing back to the caller.
    data[ ( None, astrobase.AstroBase.NAME_TAG_CITY, astrobase.AstroBase.DATA_LATITUDE ) ] = str( latitude )
    data[ ( None, astrobase.AstroBase.NAME_TAG_CITY, astrobase.AstroBase.DATA_LONGITUDE ) ] = str( longitude )
    data[ ( None, astrobase.AstroBase.NAME_TAG_CITY, astrobase.AstroBase.DATA_ELEVATION ) ] = str( elevation )

    ephemNow = ephem.Date( utcNow )

    __calculateMoon( ephemNow, data, hideIfBelowHorizon )
    __calculateSun( ephemNow, data, hideIfBelowHorizon )
    __calculatePlanets( ephemNow, data, planets, magnitude, hideIfBelowHorizon )
    __calculateStars( ephemNow, data, stars, magnitude, hideIfBelowHorizon )
    __calculateCometsOrMinorPlanets( ephemNow, data, astrobase.BodyType.COMET, comets, cometData, magnitude, hideIfBelowHorizon )
    __calculateCometsOrMinorPlanets( ephemNow, data, astrobase.BodyType.MINOR_PLANET, minorPlanets, minorPlanetData, magnitude, hideIfBelowHorizon )
    __calculateSatellites( ephemNow, data, satellites, satelliteData )

    del data[ ( None, astrobase.AstroBase.NAME_TAG_CITY, astrobase.AstroBase.DATA_LATITUDE ) ]
    del data[ ( None, astrobase.AstroBase.NAME_TAG_CITY, astrobase.AstroBase.DATA_LONGITUDE ) ]
    del data[ ( None, astrobase.AstroBase.NAME_TAG_CITY, astrobase.AstroBase.DATA_ELEVATION ) ]

    return data


# Return a list of cities, sorted alphabetically, sensitive to locale.
def getCities(): return sorted( _city_data.keys(), key = locale.strxfrm )


# Returns the latitude, longitude and elevation for the PyEphem city.
def getLatitudeLongitudeElevation( city ): return float( _city_data.get( city )[ 0 ] ), \
                                                  float( _city_data.get( city )[ 1 ] ), \
                                                  _city_data.get( city )[ 2 ]


# Takes a dictionary of orbital element data (for comets or minor planets),
# in which the key is the body name and value is the orbital element data.
#
# Returns a dictionary in which each item has a magnitude less than or equal to the maximum magnitude.
# May be empty.
def getOrbitalElementsLessThanMagnitude( orbitalElementData, maximumMagnitude ):
    results = { }
    for key in orbitalElementData:
        body = ephem.readdb( orbitalElementData[ key ].getData() )
        body.compute( ephem.city( "London" ) ) # Use any city; makes no difference to obtain the magnitude.
        bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
        if not bad and body.mag >= astrobase.AstroBase.MAGNITUDE_MINIMUM and body.mag <= maximumMagnitude:
            results[ key ] = orbitalElementData[ key ]

    return results


# http://www.ga.gov.au/geodesy/astro/moonrise.jsp
# http://futureboy.us/fsp/moon.fsp
# http://www.geoastro.de/moondata/index.html
# http://www.geoastro.de/SME/index.htm
# http://www.geoastro.de/elevazmoon/index.htm
# http://www.geoastro.de/altazsunmoon/index.htm
# http://www.geoastro.de/sundata/index.html
# http://www.satellite-calculations.com/Satellite/suncalc.htm
def __calculateMoon( ephemNow, data, hideIfBelowHorizon ):
    key = ( astrobase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
    hidden = __calculateCommon( ephemNow, data, ephem.Moon(), astrobase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON, hideIfBelowHorizon )
    if not hidden:
        data[ key + ( astrobase.AstroBase.DATA_FIRST_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_first_quarter_moon( ephemNow ).datetime() )
        data[ key + ( astrobase.AstroBase.DATA_FULL, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_full_moon( ephemNow ).datetime() )
        data[ key + ( astrobase.AstroBase.DATA_THIRD_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_last_quarter_moon( ephemNow ).datetime() )
        data[ key + ( astrobase.AstroBase.DATA_NEW, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_new_moon( ephemNow ).datetime() )
        __calculateEclipse( ephemNow.datetime(), data, astrobase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )

    # Used for internal processing; indirectly presented to the user.
    moon = ephem.Moon()
    moon.compute( __getCity( data, ephemNow ) )
    data[ key + ( astrobase.AstroBase.DATA_ILLUMINATION, ) ] = str( int( moon.phase ) ) # Needed for icon.
    data[ key + ( astrobase.AstroBase.DATA_PHASE, ) ] = __getLunarPhase( int( moon.phase ), ephem.next_full_moon( ephemNow ), ephem.next_new_moon( ephemNow ) ) # Need for notification.
    data[ key + ( astrobase.AstroBase.DATA_BRIGHT_LIMB, ) ] = str( __getZenithAngleOfBrightLimb( ephemNow, data, ephem.Moon() ) ) # Needed for icon.


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

    # Astronomical Algorithms by Jean Meeus, Second Edition, page 92.
    # https://tycho.usno.navy.mil/sidereal.html
    # http://www.wwu.edu/skywise/skymobile/skywatch.html
    # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
    hourAngle = city.sidereal_time() - body.ra

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
    y = math.sin( hourAngle )
    x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
    parallacticAngle = math.atan2( y, x )

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
            phase = astrobase.AstroBase.LUNAR_PHASE_FULL_MOON
        elif illuminationPercentage <= 99 and illuminationPercentage > 50:
            phase = astrobase.AstroBase.LUNAR_PHASE_WAXING_GIBBOUS
        elif illuminationPercentage == 50:
            phase = astrobase.AstroBase.LUNAR_PHASE_FIRST_QUARTER
        elif illuminationPercentage < 50 and illuminationPercentage >= 1:
            phase = astrobase.AstroBase.LUNAR_PHASE_WAXING_CRESCENT
        else: # illuminationPercentage < 1
            phase = astrobase.AstroBase.LUNAR_PHASE_NEW_MOON
    else:
        # Between a full moon and the next new moon...
        if( illuminationPercentage > 99 ):
            phase = astrobase.AstroBase.LUNAR_PHASE_FULL_MOON
        elif illuminationPercentage <= 99 and illuminationPercentage > 50:
            phase = astrobase.AstroBase.LUNAR_PHASE_WANING_GIBBOUS
        elif illuminationPercentage == 50:
            phase = astrobase.AstroBase.LUNAR_PHASE_THIRD_QUARTER
        elif illuminationPercentage < 50 and illuminationPercentage >= 1:
            phase = astrobase.AstroBase.LUNAR_PHASE_WANING_CRESCENT
        else: # illuminationPercentage < 1
            phase = astrobase.AstroBase.LUNAR_PHASE_NEW_MOON

    return phase


# http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
# http://www.ga.gov.au/geodesy/astro/sunrise.jsp
# http://www.geoastro.de/elevaz/index.htm
# http://www.geoastro.de/SME/index.htm
# http://www.geoastro.de/altazsunmoon/index.htm
# http://futureboy.us/fsp/sun.fsp
# http://www.satellite-calculations.com/Satellite/suncalc.htm
def __calculateSun( ephemNow, data, hideIfBelowHorizon ):
    hidden = __calculateCommon( ephemNow, data, ephem.Sun(), astrobase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN, hideIfBelowHorizon )
    if not hidden:
        __calculateEclipse( ephemNow.datetime(), data, astrobase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )

        key = ( astrobase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )

        equinox = ephem.next_equinox( ephemNow )
        solstice = ephem.next_solstice( ephemNow )
        data[ key + ( astrobase.AstroBase.DATA_EQUINOX, ) ] = astrobase.AstroBase.toDateTimeString( equinox.datetime() )
        data[ key + ( astrobase.AstroBase.DATA_SOLSTICE, ) ] = astrobase.AstroBase.toDateTimeString( solstice.datetime() )


# Calculate next eclipse for either the Sun or Moon.
def __calculateEclipse( utcNow, data, bodyType, dataTag ):
    eclipseInformation = eclipse.getEclipseForUTC( utcNow, bodyType == astrobase.BodyType.MOON )
    key = ( bodyType, dataTag )
    data[ key + ( astrobase.AstroBase.DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ]
    data[ key + ( astrobase.AstroBase.DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
    data[ key + ( astrobase.AstroBase.DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
    data[ key + ( astrobase.AstroBase.DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


# http://www.geoastro.de/planets/index.html
# http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
def __calculatePlanets( ephemNow, data, planets, magnitude, hideIfBelowHorizon ):
    for planet in planets:
        planetObject = getattr( ephem, planet.title() )()
        planetObject.compute( __getCity( data, ephemNow ) )
        if planetObject.mag >= astrobase.AstroBase.MAGNITUDE_MINIMUM and planetObject.mag <= magnitude:
            __calculateCommon( ephemNow, data, planetObject, astrobase.BodyType.PLANET, planet, hideIfBelowHorizon )


# http://aa.usno.navy.mil/data/docs/mrst.php
def __calculateStars( ephemNow, data, stars, magnitude, hideIfBelowHorizon ):
    for star in stars:
        starObject = ephem.star( star.title() )
        starObject.compute( __getCity( data, ephemNow ) )
        if starObject.mag >= astrobase.AstroBase.MAGNITUDE_MINIMUM and starObject.mag <= magnitude:
            __calculateCommon( ephemNow, data, starObject, astrobase.BodyType.STAR, star, hideIfBelowHorizon )


# Compute data for comets or minor planets.
def __calculateCometsOrMinorPlanets( ephemNow, data, bodyType, cometsOrMinorPlanets, cometOrMinorPlanetData, magnitude, hideIfBelowHorizon ):
    for key in cometsOrMinorPlanets:
        if key in cometOrMinorPlanetData:
            body = ephem.readdb( cometOrMinorPlanetData[ key ].getData() )
            body.compute( __getCity( data, ephemNow ) )
            bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
            if not bad and body.mag >= astrobase.AstroBase.MAGNITUDE_MINIMUM and body.mag <= magnitude:
                __calculateCommon( ephemNow, data, body, bodyType, key, hideIfBelowHorizon )


# Calculates common attributes such as rise/set date/time, azimuth/altitude.
#
# If hideIfBelowHorzion is True, if a body is below the horizon (but will rise), that body is dropped (no data stored).
# Otherwise the body will be included.
#
# Returns True if the body was dropped:
#    The body is below the horizon and hideIfBelowHorizon is True.
#    The body is never up.
def __calculateCommon( ephemNow, data, body, bodyType, nameTag, hideIfBelowHorizon ):
    dropped = False
    key = ( bodyType, nameTag )
    try:
        city = __getCity( data, ephemNow )
        rising = city.next_rising( body )
        setting = city.next_setting( body )

        if rising > setting: # Above the horizon.
            data[ key + ( astrobase.AstroBase.DATA_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( setting.datetime() )
            body.compute( __getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
            data[ key + ( astrobase.AstroBase.DATA_AZIMUTH, ) ] = str( repr( body.az ) )
            data[ key + ( astrobase.AstroBase.DATA_ALTITUDE, ) ] = str( repr( body.alt ) )

        else: # Below the horizon.
            if hideIfBelowHorizon:
                dropped = True
            else:
                data[ key + ( astrobase.AstroBase.DATA_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( rising.datetime() )

    except ephem.AlwaysUpError:
        body.compute( __getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
        data[ key + ( astrobase.AstroBase.DATA_AZIMUTH, ) ] = str( repr( body.az ) )
        data[ key + ( astrobase.AstroBase.DATA_ALTITUDE, ) ] = str( repr( body.alt ) )

    except ephem.NeverUpError:
        dropped = True

    return dropped


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
#Maybe this error was due to setting a dodgy date/time in the past (for testing) but using a TLE data file newer than the test time? 
def __calculateNextSatellitePass( ephemNow, data, key, satelliteTLE ):
    key = ( astrobase.BodyType.SATELLITE, key )
    currentDateTime = ephemNow
    endDateTime = ephem.Date( ephemNow + ephem.hour * 36 ) # Stop looking for passes 36 hours from now.
    while currentDateTime < endDateTime:
        city = __getCity( data, currentDateTime )
        satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getLine1(), satelliteTLE.getLine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
        satellite.compute( city )
        try:
            nextPass = city.next_pass( satellite )

        except ValueError:
            if satellite.circumpolar:
#                 print( "circumpolar" )#TODO
                data[ key + ( astrobase.AstroBase.DATA_AZIMUTH, ) ] = str( str( repr( satellite.az ) ) )
                data[ key + ( astrobase.AstroBase.DATA_ALTITUDE, ) ] = str( satellite.alt )
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
            data[ key + ( astrobase.AstroBase.DATA_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( nextPass[ 0 ].datetime() )
            data[ key + ( astrobase.AstroBase.DATA_RISE_AZIMUTH, ) ] = str( repr( nextPass[ 1 ] ) )
            data[ key + ( astrobase.AstroBase.DATA_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( nextPass[ 4 ].datetime() )
            data[ key + ( astrobase.AstroBase.DATA_SET_AZIMUTH, ) ] = str( repr( nextPass[ 5 ] ) )

        else: # Satellite will rise later, so only add rise time.
#             print( "below horizon" )#TODO
            data[ key + ( astrobase.AstroBase.DATA_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( nextPass[ 0 ].datetime() )

        break


#TODO May not need this any more...
# GitHub issue #63: 
# The rise, culminate, and set returned by next_pass() are now consecutive values for a single pass. 
# Pass singlepass=False to return the original next_rise, next_culminate, next_set even if next_set < next_rise (the satellite is already up).
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
        satellitePass and \
        len( satellitePass ) == 6 and \
        satellitePass[ 0 ] and \
        satellitePass[ 1 ] and \
        satellitePass[ 2 ] and \
        satellitePass[ 3 ] and \
        satellitePass[ 4 ] and \
        satellitePass[ 5 ]


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


def __getCity( data, date ):
    city = ephem.city( "London" ) # Put in a city name known to exist in PyEphem then doctor to the correct lat/long/elev.
    city.date = date
    city.lat = data[ ( None, astrobase.AstroBase.NAME_TAG_CITY, astrobase.AstroBase.DATA_LATITUDE ) ]
    city.lon = data[ ( None, astrobase.AstroBase.NAME_TAG_CITY, astrobase.AstroBase.DATA_LONGITUDE ) ]
    city.elev = float( data[ ( None, astrobase.AstroBase.NAME_TAG_CITY, astrobase.AstroBase.DATA_ELEVATION ) ] )

    return city