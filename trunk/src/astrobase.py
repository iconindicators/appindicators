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


#TODO Can this be an enum as per the PPA class?
#TODO This may not even be needed.
# class EngineType: PyEphem, Skyfield = range( 2 )


#TODO Can this be an enum as per the PPA class?
class BodyType: Comet, MinorPlanet, Moon, Planet, Satellite, Star, Sun = range( 7 )


class AstroBase:

#TODO Need a comment.
#TODO Ensure both backends use all tags.
    DATA_ALTITUDE = "ALTITUDE"
    DATA_AZIMUTH = "AZIMUTH"
    DATA_BRIGHT_LIMB = "BRIGHT LIMB" # Used for creating an icon; not intended for display to the user.
    DATA_ECLIPSE_DATE_TIME = "ECLIPSE DATE TIME"
    DATA_ECLIPSE_LATITUDE = "ECLIPSE LATITUDE"
    DATA_ECLIPSE_LONGITUDE = "ECLIPSE LONGITUDE"
    DATA_ECLIPSE_TYPE = "ECLIPSE TYPE"
    DATA_ELEVATION = "ELEVATION" # Internally used for city.
    DATA_EQUINOX = "EQUINOX"
    DATA_FIRST_QUARTER = "FIRST QUARTER"
    DATA_FULL = "FULL"
    DATA_ILLUMINATION = "ILLUMINATION" # Used for creating an icon; not intended for display to the user.
    DATA_LATITUDE = "LATITUDE" # Internally used for city.
    DATA_LONGITUDE = "LONGITUDE" # Internally used for city.
    DATA_NEW = "NEW"
    DATA_PHASE = "PHASE"
    DATA_RISE_AZIMUTH = "RISE AZIMUTH"
    DATA_RISE_DATE_TIME = "RISE DATE TIME"
    DATA_SET_AZIMUTH = "SET AZIMUTH"
    DATA_SET_DATE_TIME = "SET DATE TIME"
    DATA_SOLSTICE = "SOLSTICE"
    DATA_THIRD_QUARTER = "THIRD QUARTER"

    DATA_INTERNAL = [
        DATA_BRIGHT_LIMB,
        DATA_ILLUMINATION ]

    DATA_COMET = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_RISE_DATE_TIME,
        DATA_SET_DATE_TIME ]

    DATA_MINOR_PLANET = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_RISE_DATE_TIME,
        DATA_SET_DATE_TIME ]

    DATA_MOON = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_ECLIPSE_DATE_TIME,
        DATA_ECLIPSE_LATITUDE,
        DATA_ECLIPSE_LONGITUDE,
        DATA_ECLIPSE_TYPE,
        DATA_FIRST_QUARTER,
        DATA_FULL,
        DATA_NEW,
        DATA_PHASE,
        DATA_RISE_DATE_TIME,
        DATA_SET_DATE_TIME,
        DATA_THIRD_QUARTER ]

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
        DATA_EQUINOX,
        DATA_RISE_DATE_TIME,
        DATA_SET_DATE_TIME,
        DATA_SOLSTICE ]


#TODO Need a description
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


    MAGNITUDE_MAXIMUM = 15.0 # No point going any higher for the typical home astronomer.
    MAGNITUDE_MINIMUM = -10.0 # Have found magnitudes in comet OE data which are, erroneously, brighter than the sun, so set a lower limit.

#Where is this used?
#     DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS = "%Y-%m-%d %H:%M:%S"


    # Returns a dictionary with astronomical information:
    #     Key is a tuple of AstronomicalBodyType, a name tag and a data tag.
    #     Value is the data as a string.
    #
    # If a body is never up, no data is added.
    # If a body is always up, azimuth/altitude are added.
    # If the body is below the horizon, only the rise date/time is added.
    # If the body is above the horizon, set date/time and azimuth/altitude are added.
    #
    # NOTE: Any error when computing a body or if a body never rises, no result is added for that body.
    @staticmethod
    def getAstronomicalInformation( utcNow,
                                    latitude, longitude, elevation,
                                    planets,
                                    stars,
                                    satellites, satelliteData,
                                    comets, cometData,
                                    minorPlanets, minorPlanetData,
                                    magnitude,
                                    hideIfBelowHorizon ):

        return { }


    # Return a list of cities, sorted alphabetically, sensitive to locale.
    @staticmethod
    def getCities(): return [ ]


    # Get the lunar phase for the given date/time and illumination percentage.
    #
    #    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
    #    nextFullMoonDate The date of the next full moon.
    #    nextNewMoonDate The date of the next new moon.
    @staticmethod
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
    @staticmethod
    def __calculateEclipse( utcNow, data, astronomicalBodyType, dataTag ):
        eclipseInformation = eclipse.getEclipseForUTC( utcNow, astronomicalBodyType == AstronomicalBodyType.Moon )
        key = ( astronomicalBodyType, dataTag )
        data[ key + ( DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ]
        data[ key + ( DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
        data[ key + ( DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
        data[ key + ( DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


    @staticmethod
    def __toDateTimeString( dateTime ): return dateTime.strftime( DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )