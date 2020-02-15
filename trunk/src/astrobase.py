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


# Base class for calculating astronomical information for use with Indicator Lunar.


from abc import ABC, abstractmethod
from enum import Enum

import eclipse, math


class AstroBase( ABC ):

    class BodyType( Enum ):
        COMET = 0
        MINOR_PLANET = 1
        MOON = 2
        PLANET = 3
        SATELLITE = 4
        STAR = 5
        SUN = 6


    # Data tags representing each of the pieces of calculated astronomical information.
    DATA_TAG_ALTITUDE = "ALTITUDE"
    DATA_TAG_AZIMUTH = "AZIMUTH"
    DATA_TAG_BRIGHT_LIMB = "BRIGHT LIMB" # Used for creating an icon.
    DATA_TAG_ECLIPSE_DATE_TIME = "ECLIPSE DATE TIME"
    DATA_TAG_ECLIPSE_LATITUDE = "ECLIPSE LATITUDE"
    DATA_TAG_ECLIPSE_LONGITUDE = "ECLIPSE LONGITUDE"
    DATA_TAG_ECLIPSE_TYPE = "ECLIPSE TYPE"
    DATA_TAG_EQUINOX = "EQUINOX"
    DATA_TAG_FIRST_QUARTER = "FIRST QUARTER"
    DATA_TAG_FULL = "FULL"
    DATA_TAG_ILLUMINATION = "ILLUMINATION" # Used for creating an icon.
    DATA_TAG_NEW = "NEW"
    DATA_TAG_PHASE = "PHASE" # Used for creating an icon.
    DATA_TAG_RISE_AZIMUTH = "RISE AZIMUTH"
    DATA_TAG_RISE_DATE_TIME = "RISE DATE TIME"
    DATA_TAG_SET_AZIMUTH = "SET AZIMUTH"
    DATA_TAG_SET_DATE_TIME = "SET DATE TIME"
    DATA_TAG_SOLSTICE = "SOLSTICE"
    DATA_TAG_THIRD_QUARTER = "THIRD QUARTER"

    DATA_TAGS_COMET = [
        DATA_TAG_ALTITUDE,
        DATA_TAG_AZIMUTH,
        DATA_TAG_RISE_DATE_TIME,
        DATA_TAG_SET_DATE_TIME ]

    DATA_TAGS_MINOR_PLANET = [
        DATA_TAG_ALTITUDE,
        DATA_TAG_AZIMUTH,
        DATA_TAG_RISE_DATE_TIME,
        DATA_TAG_SET_DATE_TIME ]

    DATA_TAGS_MOON = [
        DATA_TAG_ALTITUDE,
        DATA_TAG_AZIMUTH,
        DATA_TAG_BRIGHT_LIMB,
        DATA_TAG_ECLIPSE_DATE_TIME,
        DATA_TAG_ECLIPSE_LATITUDE,
        DATA_TAG_ECLIPSE_LONGITUDE,
        DATA_TAG_ECLIPSE_TYPE,
        DATA_TAG_FIRST_QUARTER,
        DATA_TAG_FULL,
        DATA_TAG_ILLUMINATION,
        DATA_TAG_NEW,
        DATA_TAG_PHASE,
        DATA_TAG_RISE_DATE_TIME,
        DATA_TAG_SET_DATE_TIME,
        DATA_TAG_THIRD_QUARTER ]

    DATA_TAGS_PLANET = [
        DATA_TAG_ALTITUDE,
        DATA_TAG_AZIMUTH,
        DATA_TAG_RISE_DATE_TIME,
        DATA_TAG_SET_DATE_TIME ]

    DATA_TAGS_SATELLITE = [
        DATA_TAG_RISE_AZIMUTH,
        DATA_TAG_RISE_DATE_TIME,
        DATA_TAG_SET_AZIMUTH,
        DATA_TAG_SET_DATE_TIME ]

    DATA_TAGS_STAR = [
        DATA_TAG_ALTITUDE,
        DATA_TAG_AZIMUTH,
        DATA_TAG_RISE_DATE_TIME,
        DATA_TAG_SET_DATE_TIME ]

    DATA_TAGS_SUN = [
        DATA_TAG_ALTITUDE,
        DATA_TAG_AZIMUTH,
        DATA_TAG_ECLIPSE_DATE_TIME,
        DATA_TAG_ECLIPSE_LATITUDE,
        DATA_TAG_ECLIPSE_LONGITUDE,
        DATA_TAG_ECLIPSE_TYPE,
        DATA_TAG_EQUINOX,
        DATA_TAG_RISE_DATE_TIME,
        DATA_TAG_SET_DATE_TIME,
        DATA_TAG_SOLSTICE ]

    # Corresponding tags which reflect each data tag made visible to the user in the Preferences. 
    DATA_TAGS_TRANSLATIONS = {
        DATA_TAG_ALTITUDE          : _( "ALTITUDE" ),
        DATA_TAG_AZIMUTH           : _( "AZIMUTH" ),
        DATA_TAG_BRIGHT_LIMB       : _( "BRIGHT LIMB" ),
        DATA_TAG_ECLIPSE_DATE_TIME : _( "ECLIPSE DATE TIME" ),
        DATA_TAG_ECLIPSE_LATITUDE  : _( "ECLIPSE LATITUDE" ),
        DATA_TAG_ECLIPSE_LONGITUDE : _( "ECLIPSE LONGITUDE" ),
        DATA_TAG_ECLIPSE_TYPE      : _( "ECLIPSE TYPE" ),
        DATA_TAG_EQUINOX           : _( "EQUINOX" ),
        DATA_TAG_FIRST_QUARTER     : _( "FIRST QUARTER" ),
        DATA_TAG_ILLUMINATION      : _( "ILLUMINATION" ),
        DATA_TAG_FULL              : _( "FULL" ),
        DATA_TAG_NEW               : _( "NEW" ),
        DATA_TAG_PHASE             : _( "PHASE" ),
        DATA_TAG_RISE_AZIMUTH      : _( "RISE AZIMUTH" ),
        DATA_TAG_RISE_DATE_TIME    : _( "RISE DATE TIME" ),
        DATA_TAG_SET_AZIMUTH       : _( "SET AZIMUTH" ),
        DATA_TAG_SET_DATE_TIME     : _( "SET DATE TIME" ),
        DATA_TAG_SOLSTICE          : _( "SOLSTICE" ),
        DATA_TAG_THIRD_QUARTER     : _( "THIRD QUARTER" ) }


    # Tags used to uniquely name particular objects/items.
    NAME_TAG_MOON = "MOON"
    NAME_TAG_SUN = "SUN"

    # Corresponding tags which reflect each data tag made visible to the user in the Preferences. 
    NAME_TAG_MOON_TRANSLATION = { NAME_TAG_MOON : _( "MOON" ) }
    NAME_TAG_SUN_TRANSLATION = { NAME_TAG_SUN : _( "SUN" ) }


    # Each of the planets, used as name tags.
    PLANET_MERCURY = "MERCURY"
    PLANET_VENUS = "VENUS"
    PLANET_MARS = "MARS"
    PLANET_JUPITER = "JUPITER"
    PLANET_SATURN = "SATURN"
    PLANET_URANUS = "URANUS"
    PLANET_NEPTUNE = "NEPTUNE"
    PLANET_PLUTO = "PLUTO"

    PLANETS = [ PLANET_MERCURY, PLANET_VENUS, PLANET_MARS, PLANET_JUPITER, PLANET_SATURN, PLANET_URANUS, PLANET_NEPTUNE, PLANET_PLUTO ]

    PLANET_NAMES_TRANSLATIONS = {
        PLANET_MERCURY : _( "Mercury" ),
        PLANET_VENUS   : _( "Venus" ),
        PLANET_MARS    : _( "Mars" ),
        PLANET_JUPITER : _( "Jupiter" ),
        PLANET_SATURN  : _( "Saturn" ),
        PLANET_URANUS  : _( "Uranus" ),
        PLANET_NEPTUNE : _( "Neptune" ),
        PLANET_PLUTO   : _( "Pluto" ) }

    # Corresponding tags which reflect each data tag made visible to the user in the Preferences. 
    PLANET_TAGS_TRANSLATIONS = {
        PLANET_MERCURY : _( "MERCURY" ),
        PLANET_VENUS   : _( "VENUS" ),
        PLANET_MARS    : _( "MARS" ),
        PLANET_JUPITER : _( "JUPITER" ),
        PLANET_SATURN  : _( "SATURN" ),
        PLANET_URANUS  : _( "URANUS" ),
        PLANET_NEPTUNE : _( "NEPTUNE" ),
        PLANET_PLUTO   : _( "PLUTO" ) }


    # Lunar phases.
    LUNAR_PHASE_FULL_MOON = "FULL_MOON"
    LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
    LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
    LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
    LUNAR_PHASE_NEW_MOON = "NEW_MOON"
    LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
    LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
    LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"

    # Corresponding tags which reflect each data tag made visible to the user in the Preferences. 
    LUNAR_PHASE_NAMES_TRANSLATIONS = {
        LUNAR_PHASE_FULL_MOON       : _( "Full Moon" ),
        LUNAR_PHASE_WANING_GIBBOUS  : _( "Waning Gibbous" ),
        LUNAR_PHASE_THIRD_QUARTER   : _( "Third Quarter" ),
        LUNAR_PHASE_WANING_CRESCENT : _( "Waning Crescent" ),
        LUNAR_PHASE_NEW_MOON        : _( "New Moon" ),
        LUNAR_PHASE_WAXING_CRESCENT : _( "Waxing Crescent" ),
        LUNAR_PHASE_FIRST_QUARTER   : _( "First Quarter" ),
        LUNAR_PHASE_WAXING_GIBBOUS  : _( "Waxing Gibbous" ) }


    # Capitalised names of stars to be populated by implementing class.
    STARS = [ ]

    # Capitalised names of stars and associated HIP numbers to be populated by implementing class.
    STARS_TO_HIP = { }

    # Names of stars (from STARS) and associated English string encapsulated as _( "" ) to be populated by implementing class.
    STAR_NAMES_TRANSLATIONS = { }

    # Names of stars (from STARS) and associated capitalised English string encapsulated as _( "" ) to be populated by implementing class.
    STAR_TAGS_TRANSLATIONS = { }


    SATELLITE_TAG_NAME = "[NAME]"
    SATELLITE_TAG_NUMBER = "[NUMBER]"
    SATELLITE_TAG_INTERNATIONAL_DESIGNATOR = "[INTERNATIONAL DESIGNATOR]"
    SATELLITE_TAG_RISE_AZIMUTH = "[RISE AZIMUTH]"
    SATELLITE_TAG_RISE_TIME = "[RISE TIME]"
    SATELLITE_TAG_SET_AZIMUTH = "[SET AZIMUTH]"
    SATELLITE_TAG_SET_TIME = "[SET TIME]"

    SATELLITE_TAG_NAME_TRANSLATION = "[" + _( "NAME" ) + "]"
    SATELLITE_TAG_NUMBER_TRANSLATION = "[" + _( "NUMBER" ) + "]"
    SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION = "[" + _( "INTERNATIONAL DESIGNATOR" ) + "]"
    SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION = "[" + _( "RISE AZIMUTH" ) + "]"
    SATELLITE_TAG_RISE_TIME_TRANSLATION = "[" + _( "RISE TIME" ) + "]"
    SATELLITE_TAG_SET_AZIMUTH_TRANSLATION = "[" + _( "SET AZIMUTH" ) + "]"
    SATELLITE_TAG_SET_TIME_TRANSLATION = "[" + _( "SET TIME" ) + "]"

    SATELLITE_TAG_TRANSLATIONS = [ ] # List of [ tag, translated tag ] pairs.
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_NAME.strip( "[]" ), SATELLITE_TAG_NAME_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_NUMBER.strip( "[]" ), SATELLITE_TAG_NUMBER_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_INTERNATIONAL_DESIGNATOR.strip( "[]" ), SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_RISE_AZIMUTH.strip( "[]" ), SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_RISE_TIME.strip( "[]" ), SATELLITE_TAG_RISE_TIME_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_SET_AZIMUTH.strip( "[]" ), SATELLITE_TAG_SET_AZIMUTH_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_SET_TIME.strip( "[]" ), SATELLITE_TAG_SET_TIME_TRANSLATION.strip( "[]" ) ] )


    # Miscellaneous.
    DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS = "%Y-%m-%d %H:%M:%S"
    MAGNITUDE_MAXIMUM = 15.0 # No point going any higher for the typical home astronomer.
    MAGNITUDE_MINIMUM = -10.0 # Have found magnitudes in comet OE data which are, erroneously, brighter than the sun, so set a lower limit.


    # Returns a dictionary with astronomical information:
    #     Key is a tuple of BodyType, a name tag and a data tag.
    #     Value is the calculated astronomical information as a string.
    #
    # Latitude, longitude are floating point numbers representing decimal degrees.
    # Elevation is a floating point number representing metres above sea level.
    # Maximum magnitude will applies to planets, stars, comets and minor planets.
    #
    # If a body is never up, no data is added.
    # If a body is always up, the current azimuth/altitude are added.
    # If the body will rise/set, the next rise date/time, next set date/time and current azimuth/altitude are added.
    #
    # NOTE: Any error when computing a body or if a body never rises, no result is added for that body.
    #
    # Results can be verified using Verify results: https://ssd.jpl.nasa.gov/horizons.cgi
    @staticmethod
    @abstractmethod
    def calculate( utcNow,
                   latitude, longitude, elevation,
                   planets,
                   stars,
                   satellites, satelliteData,
                   comets, cometData,
                   minorPlanets, minorPlanetData,
                   magnitudeMaximum ): 
        return { }


    # Return a list of cities, sorted alphabetically, sensitive to locale.
    @staticmethod
    @abstractmethod
    def getCities(): return [ ]


    # Returns a tuple of floats of the latitude, longitude and elevation for the city.
    @staticmethod
    @abstractmethod
    def getLatitudeLongitudeElevation( city ): return 0.0, 0.0, 0.0


    # Takes a dictionary of orbital element data (for comets or minor planets),
    # in which the key is the body name and value is the orbital element data.
    #
    # Returns a dictionary in which each item has a magnitude less than or equal to the maximum magnitude.
    # May be empty.
    @staticmethod
    @abstractmethod
    def getOrbitalElementsLessThanMagnitude( orbitalElementData, maximumMagnitude ): return { }


    # Returns a string specifying any third party credit.
    # Format is a credit string followed by an optional URL.
    @staticmethod
    @abstractmethod
    def getCredit(): return ""


    # Get the lunar phase for the given date/time and illumination percentage.
    #
    #    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
    #    nextFullMoonDate The date of the next full moon.
    #    nextNewMoonDate The date of the next new moon.
    @staticmethod
    def getLunarPhase( illuminationPercentage, nextFullMoonDate, nextNewMoonDate ):
        phase = None
        if nextFullMoonDate < nextNewMoonDate: # Between a new moon and a full moon...
            if( illuminationPercentage > 99 ):
                phase = AstroBase.LUNAR_PHASE_FULL_MOON

            elif illuminationPercentage <= 99 and illuminationPercentage > 50:
                phase = AstroBase.LUNAR_PHASE_WAXING_GIBBOUS

            elif illuminationPercentage == 50:
                phase = AstroBase.LUNAR_PHASE_FIRST_QUARTER

            elif illuminationPercentage < 50 and illuminationPercentage >= 1:
                phase = AstroBase.LUNAR_PHASE_WAXING_CRESCENT

            else: # illuminationPercentage < 1
                phase = AstroBase.LUNAR_PHASE_NEW_MOON

        else: # Between a full moon and the next new moon...
            if( illuminationPercentage > 99 ):
                phase = AstroBase.LUNAR_PHASE_FULL_MOON

            elif illuminationPercentage <= 99 and illuminationPercentage > 50:
                phase = AstroBase.LUNAR_PHASE_WANING_GIBBOUS

            elif illuminationPercentage == 50:
                phase = AstroBase.LUNAR_PHASE_THIRD_QUARTER

            elif illuminationPercentage < 50 and illuminationPercentage >= 1:
                phase = AstroBase.LUNAR_PHASE_WANING_CRESCENT

            else: # illuminationPercentage < 1
                phase = AstroBase.LUNAR_PHASE_NEW_MOON

        return phase


    # Retrieve the next eclipse for either the Sun or Moon.
    @staticmethod
    def getEclipse( utcNow, data, bodyType, dataTag ):
        eclipseInformation = eclipse.getEclipse( utcNow, bodyType == AstroBase.BodyType.MOON )
        key = ( bodyType, dataTag )
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ]
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


    @staticmethod
    def toDateTimeString( dateTime ): return dateTime.strftime( AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )


    # Compute the sidereal time for the given longitude (floating point radians) as a decimal time.
    #
    # Reference:
    #  'Practical Astronomy with Your Calculator' by Peter Duffett-Smith.
    @staticmethod
    def getSiderealTime( utcNow, longitude ):
        # Find the Julian date.  Section 4 of the reference.
        # Assume the date is always later than 15th October, 1582.
        y = utcNow.year
        m = utcNow.month
        d = utcNow.day + \
            ( utcNow.hour / 24 ) + \
            ( utcNow.minute / ( 60 * 24 ) ) + \
            ( utcNow.second / ( 60 * 60 * 24 ) ) + \
            ( utcNow.microsecond / ( 60 * 60 * 24 * 1000 ) )

        if m == 1 or m == 2:
            yPrime = y - 1
            mPrime = m + 12

        else:
            yPrime = y
            mPrime = m

        A = int( yPrime / 100 )
        B = 2 - A + int( A / 4 )
        C = int( 365.25 * yPrime )
        D = int( 30.6001 * ( mPrime + 1 ) )
        julianDate = B + C + D + d + 1720994.5

        # Find universal time.  Section 12 of the reference. 
        S = julianDate - 2451545.0
        T = S / 36525.0
        T0 = ( 6.697374558 + ( 2400.051336 * T ) + ( 0.000025862 * T * T ) ) % 24
        universalTimeDecimal = ( ( ( utcNow.second / 60 ) + utcNow.minute ) / 60 ) + utcNow.hour
        A = universalTimeDecimal * 1.002737909
        greenwichSiderealTimeDecimal = ( A + T0 ) % 24

        # Find local sidereal time.  Section 14 of the reference.
        longitudeInHours = math.degrees( longitude ) / 15

        return ( greenwichSiderealTimeDecimal + longitudeInHours ) % 24 # Local sidereal time as a decimal time.
    
    
    # Compute the bright limb angle (relative to zenith) between the sun and a planetary body (typically the moon).
    # Measured in radians counter clockwise from a positive y axis.
    #
    # Right ascension, declination, latitude and longitude are floating point radians.
    #
    # References:
    #  'Astronomical Algorithms' Second Edition by Jean Meeus (chapters 14 and 48).
    #  'Practical Astronomy with Your Calculator' by Peter Duffett-Smith.
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
    #  http://stackoverflow.com/questions/13314626/local-solar-time-function-from-utc-and-longitudeInDegrees/13425515#13425515
    #  http://astro.ukho.gov.uk/data/tn/naotn74.pdf
    @staticmethod
    def getZenithAngleOfBrightLimb( utcNow, sunRA, sunDec, bodyRA, bodyDec, bodyLat, bodyLong ):
        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
        y = math.cos( sunDec ) * math.sin( sunRA - bodyRA )
        x = math.sin( sunDec ) * math.cos( bodyDec ) - math.cos( sunDec ) * math.sin( bodyDec ) * math.cos( sunRA - bodyRA )
        positionAngleOfBrightLimb = math.atan2( y, x )

        # Multiply by 15 to convert from decimal time to decimal degrees; section 22 of Practical Astronomy with Your Calculator.
        localSiderealTime = math.radians( AstroBase.getSiderealTime( utcNow, bodyLong ) * 15 )

        # Astronomical Algorithms by Jean Meeus, Second Edition, page 92.
        # https://tycho.usno.navy.mil/sidereal.html
        # http://www.wwu.edu/skywise/skymobile/skywatch.html
        # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
        hourAngle = localSiderealTime - bodyRA

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
        y = math.sin( hourAngle )
        x = math.tan( bodyLat ) * math.cos( bodyDec ) - math.sin( bodyDec ) * math.cos( hourAngle )
        parallacticAngle = math.atan2( y, x )

        return ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi )