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


#TODO Better description.
# Calculate astronomical information using PyEphem.


from abc import ABC, abstractmethod
from enum import Enum

import eclipse


class AstroBase( ABC ):

    class BodyType( Enum ):
        COMET = 0
        MINOR_PLANET = 1,
        MOON = 2
        PLANET = 3,
        SATELLITE = 4,
        STAR = 5,
        SUN = 6


#TODO Need a comment.
#TODO Ensure both backends use all tags.
#TODO Maybe rename to DATA_TAG_...?  Need to do it here and in indicator and astorpyephem and astroskyfield.
    DATA_TAG_ALTITUDE = "ALTITUDE"
    DATA_TAG_AZIMUTH = "AZIMUTH"
    DATA_TAG_BRIGHT_LIMB = "BRIGHT LIMB" # Used for creating an icon; not intended for display to the user.
    DATA_TAG_ECLIPSE_DATE_TIME = "ECLIPSE DATE TIME"
    DATA_TAG_ECLIPSE_LATITUDE = "ECLIPSE LATITUDE"
    DATA_TAG_ECLIPSE_LONGITUDE = "ECLIPSE LONGITUDE"
    DATA_TAG_ECLIPSE_TYPE = "ECLIPSE TYPE"
    DATA_TAG_ELEVATION = "ELEVATION" # Internally used for city in astropyephem.
    DATA_TAG_EQUINOX = "EQUINOX"
    DATA_TAG_FIRST_QUARTER = "FIRST QUARTER"
    DATA_TAG_FULL = "FULL"
    DATA_TAG_ILLUMINATION = "ILLUMINATION" # Used for creating an icon; not intended for display to the user.
    DATA_TAG_LATITUDE = "LATITUDE" # Internally used for city in astropyephem.
    DATA_TAG_LONGITUDE = "LONGITUDE" # Internally used for city in astropyephem.
    DATA_TAG_NEW = "NEW"
    DATA_TAG_PHASE = "PHASE"
    DATA_TAG_RISE_AZIMUTH = "RISE AZIMUTH"
    DATA_TAG_RISE_DATE_TIME = "RISE DATE TIME"
    DATA_TAG_SET_AZIMUTH = "SET AZIMUTH"
    DATA_TAG_SET_DATE_TIME = "SET DATE TIME"
    DATA_TAG_SOLSTICE = "SOLSTICE"
    DATA_TAG_THIRD_QUARTER = "THIRD QUARTER"

    DATA_TAGS_INTERNAL = [
        DATA_TAG_BRIGHT_LIMB,
        DATA_TAG_ILLUMINATION ]

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
        DATA_TAG_ECLIPSE_DATE_TIME,
        DATA_TAG_ECLIPSE_LATITUDE,
        DATA_TAG_ECLIPSE_LONGITUDE,
        DATA_TAG_ECLIPSE_TYPE,
        DATA_TAG_FIRST_QUARTER,
        DATA_TAG_FULL,
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


#TODO Need a description
#TODO Remove TAG?  Data tags don't have TAG in them.
    NAME_TAG_CITY = "CITY"
    NAME_TAG_MOON = "MOON"
    NAME_TAG_SUN = "SUN"


#TODO Need a description
    PLANET_MERCURY = "MERCURY"
    PLANET_VENUS = "VENUS"
    PLANET_MARS = "MARS"
    PLANET_JUPITER = "JUPITER"
    PLANET_SATURN = "SATURN"
    PLANET_URANUS = "URANUS"
    PLANET_NEPTUNE = "NEPTUNE"
    PLANET_PLUTO = "PLUTO"

    PLANETS = [ PLANET_MERCURY, PLANET_VENUS, PLANET_MARS, PLANET_JUPITER, PLANET_SATURN, PLANET_URANUS, PLANET_NEPTUNE, PLANET_PLUTO ]


    LUNAR_PHASE_FULL_MOON = "FULL_MOON"
    LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
    LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
    LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
    LUNAR_PHASE_NEW_MOON = "NEW_MOON"
    LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
    LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
    LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"


#TODO Need to make it obvious this is abstract...how?
#TODO Comment how teh star names should be fully capitalised.
    STARS = [ ]


    MAGNITUDE_MAXIMUM = 15.0 # No point going any higher for the typical home astronomer.
    MAGNITUDE_MINIMUM = -10.0 # Have found magnitudes in comet OE data which are, erroneously, brighter than the sun, so set a lower limit.

    DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS = "%Y-%m-%d %H:%M:%S"


    # Returns a dictionary with astronomical information:
    #     Key is a tuple of BodyType, a name tag and a data tag.
    #     Value is the calculated astronomical information as a string.
    #
    # If a body is never up, no data is added.
    # If a body is always up, azimuth/altitude are added.
    # If the body is below the horizon, only the rise date/time is added.
    # If the body is above the horizon, set date/time and azimuth/altitude are added.
    #
    # NOTE: Any error when computing a body or if a body never rises, no result is added for that body.
    @staticmethod
    @abstractmethod
    def getAstronomicalInformation( utcNow,
                                    latitude, longitude, elevation,
                                    planets,
                                    stars,
                                    satellites, satelliteData,
                                    comets, cometData,
                                    minorPlanets, minorPlanetData,
                                    magnitudeMaximum,
                                    hideIfBelowHorizon ): return { }


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
    def calculateEclipse( utcNow, data, bodyType, dataTag ):
        eclipseInformation = eclipse.getEclipse( utcNow, bodyType == AstroBase.BodyType.MOON )
        key = ( bodyType, dataTag )
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ]
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


    @staticmethod
#TODO This works for pyephem...but does it work for skyfield (that is, does skyfield have a different format)?
    def toDateTimeString( dateTime ): return dateTime.strftime( AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )