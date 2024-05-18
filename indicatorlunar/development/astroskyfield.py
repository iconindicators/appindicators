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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Calculate astronomical information using Skyfield.


#TODO COBS now has a parameter cur-mag to filter the comet downloads by observed magnitude.
# When cur-mag=15 the number of comets is around 22,
# which now, may not be too much to calculate in Skyfield.
# Perhaps do some timing tests...to see how long it takes to process comets (of around 22)
# and whatever the minor planets currently sits at with a maximum apparent magnitude of 15.
# Minor planets is around 560...maybe too much to switch over to Skyfield.


#TODO If/when astroskyfield.py is included in the release,
# put a data directory at
#   indicatorlunar/src/indicatorlunar/data
# with planets.bsp and stars.dat in it (created) ... copied from top level directory.
# Then in pyproject.toml:
#dependencies = [
#  "skyfield",
#  "numpy",
#  "pandas",
#  "PyGObject",
#  "requests",
#  "sgp4"
#]
#
# and
#
#[tool.setuptools.package-data]
#indicatorlunar = [
#  "CHANGELOG.md",
#  "icons/*/*.svg",
#  "data/planets.bsp",
#  "data/stars.dat",
#  "locale/*.pot",
#  "locale/*/LC_MESSAGES/*.mo",
#  "locale/*/LC_MESSAGES/*.po",
#  "packaging/linux/*.desktop",
#  "packaging/linux/*.sh"
#]


import datetime
import io
import locale
import math

from pathlib import Path

import skyfield
from skyfield import almanac, constants, eclipselib
from skyfield.api import EarthSatellite, load, Star, wgs84
from skyfield.data import hipparcos, mpc
from skyfield.magnitudelib import planetary_magnitude
from skyfield.trigonometry import position_angle_of

import eclipse

from astrobase import AstroBase


class AstroSkyfield( AstroBase ):

    # Planets ephemeris must be created using create_ephemeris_planets.py.
    __EPHEMERIS_PLANETS = load( str( Path( __file__ ).parent ) + "/data/planets.bsp" )

    # Stars ephemeris must be created using create_ephemeris_stars.py.
    with load.open( str( Path( __file__ ).parent ) + "/data/stars.dat" ) as f:
        __EPHEMERIS_STARS = hipparcos.load_dataframe( f )


    # Name tags for bodies.
    __MOON = "MOON"
    __SUN = "SUN"

    __PLANET_EARTH = "EARTH"

    __PLANET_MAPPINGS = {
        AstroBase.PLANET_MERCURY : "MERCURY BARYCENTER",
        AstroBase.PLANET_VENUS   : "VENUS BARYCENTER",
        AstroBase.PLANET_MARS    : "MARS BARYCENTER",
        AstroBase.PLANET_JUPITER : "JUPITER BARYCENTER",
        AstroBase.PLANET_SATURN  : "SATURN BARYCENTER",
        AstroBase.PLANET_URANUS  : "URANUS BARYCENTER",
        AstroBase.PLANET_NEPTUNE : "NEPTUNE BARYCENTER" }


    # Skyfield does not provide a list of cities.
    # However ephem/cities.py does provide such a list:
    #    https://github.com/skyfielders/python-skyfield/issues/316
    #
    # Format:
    #    Name: latitude (dec degrees), longitude (dec degrees), elevation (m).
    _city_data = {
        "Abu Dhabi"         :   ( 24.4666667, 54.3666667, 6.296038 ),
        "Adelaide"          :   ( -34.9305556, 138.6205556, 49.098354 ),
        "Almaty"            :   ( 43.255058, 76.912628, 785.522156 ),
        "Amsterdam"         :   ( 52.3730556, 4.8922222, 14.975505 ),
        "Antwerp"           :   ( 51.21992, 4.39625, 7.296879 ),
        "Arhus"             :   ( 56.162939, 10.203921, 26.879421 ),
        "Athens"            :   ( 37.97918, 23.716647, 47.597061 ),
        "Atlanta"           :   ( 33.7489954, -84.3879824, 319.949738 ),
        "Auckland"          :   ( -36.8484597, 174.7633315, 21.000000 ),
        "Baltimore"         :   ( 39.2903848, -76.6121893, 10.258920 ),
        "Bangalore"         :   ( 12.9715987, 77.5945627, 911.858398 ),
        "Bangkok"           :   ( 13.7234186, 100.4762319, 4.090096 ),
        "Barcelona"         :   ( 41.387917, 2.1699187, 19.991053 ),
        "Beijing"           :   ( 39.904214, 116.407413, 51.858883 ),
        "Berlin"            :   ( 52.5234051, 13.4113999, 45.013939 ),
        "Birmingham"        :   ( 52.4829614, -1.893592, 141.448563 ),
        "Bogota"            :   ( 4.5980556, -74.0758333, 2614.037109 ),
        "Bologna"           :   ( 44.4942191, 11.3464815, 72.875923 ),
        "Boston"            :   ( 42.3584308, -71.0597732, 15.338848 ),
        "Bratislava"        :   ( 48.1483765, 17.1073105, 155.813446 ),
        "Brazilia"          :   ( -14.235004, -51.92528, 259.063477 ),
        "Brisbane"          :   ( -27.4709331, 153.0235024, 28.163914 ),
        "Brussels"          :   ( 50.8503, 4.35171, 26.808620 ),
        "Bucharest"         :   ( 44.437711, 26.097367, 80.407768 ),
        "Budapest"          :   ( 47.4984056, 19.0407578, 106.463295 ),
        "Buenos Aires"      :   ( -34.6084175, -58.3731613, 40.544090 ),
        "Cairo"             :   ( 30.064742, 31.249509, 20.248013 ),
        "Calgary"           :   ( 51.045, -114.0572222, 1046.000000 ),
        "Cape Town"         :   ( -33.924788, 18.429916, 5.838447 ),
        "Caracas"           :   ( 10.491016, -66.902061, 974.727417 ),
        "Chicago"           :   ( 41.8781136, -87.6297982, 181.319290 ),
        "Cleveland"         :   ( 41.4994954, -81.6954088, 198.879639 ),
        "Cologne"           :   ( 50.9406645, 6.9599115, 59.181450 ),
        "Colombo"           :   ( 6.927468, 79.848358, 9.969995 ),
        "Columbus"          :   ( 39.9611755, -82.9987942, 237.651932 ),
        "Copenhagen"        :   ( 55.693403, 12.583046, 6.726723 ),
        "Dallas"            :   ( 32.802955, -96.769923, 154.140625 ),
        "Detroit"           :   ( 42.331427, -83.0457538, 182.763428 ),
        "Dresden"           :   ( 51.0509912, 13.7336335, 114.032356 ),
        "Dubai"             :   ( 25.2644444, 55.3116667, 8.029230 ),
        "Dublin"            :   ( 53.344104, -6.2674937, 8.214323 ),
        "Dusseldorf"        :   ( 51.2249429, 6.7756524, 43.204800 ),
        "Edinburgh"         :   ( 55.9501755, -3.1875359, 84.453995 ),
        "Frankfurt"         :   ( 50.1115118, 8.6805059, 106.258285 ),
        "Geneva"            :   ( 46.2057645, 6.141593, 379.026245 ),
        "Genoa"             :   ( 44.4070624, 8.9339889, 35.418076 ),
        "Glasgow"           :   ( 55.8656274, -4.2572227, 38.046883 ),
        "Gothenburg"        :   ( 57.6969943, 11.9865, 15.986326 ),
        "Guangzhou"         :   ( 23.129163, 113.264435, 18.892920 ),
        "Hamburg"           :   ( 53.5538148, 9.9915752, 5.104634 ),
        "Hanoi"             :   ( 21.0333333, 105.85, 20.009024 ),
        "Helsinki"          :   ( 60.1698125, 24.9382401, 7.153307 ),
        "Ho Chi Minh City"  :   ( 10.75918, 106.662498, 10.757121 ),
        "Hong Kong"         :   ( 22.396428, 114.109497, 321.110260 ),
        "Houston"           :   ( 29.7628844, -95.3830615, 6.916622 ),
        "Istanbul"          :   ( 41.00527, 28.97696, 37.314278 ),
        "Jakarta"           :   ( -6.211544, 106.845172, 10.218226 ),
        "Johannesburg"      :   ( -26.1704415, 27.9717606, 1687.251099 ),
        "Kansas City"       :   ( 39.1066667, -94.6763889, 274.249390 ),
        "Kiev"              :   ( 50.45, 30.5233333, 157.210175 ),
        "Kuala Lumpur"      :   ( 3.139003, 101.686855, 52.271698 ),
        "Leeds"             :   ( 53.7996388, -1.5491221, 47.762367 ),
        "Lille"             :   ( 50.6371834, 3.0630174, 28.139490 ),
        "Lima"              :   ( -12.0433333, -77.0283333, 154.333740 ),
        "Lisbon"            :   ( 38.7070538, -9.1354884, 2.880179 ),
        "London"            :   ( 51.5001524, -0.1262362, 14.605533 ),
        "Los Angeles"       :   ( 34.0522342, -118.2436849, 86.847092 ),
        "Luxembourg"        :   ( 49.815273, 6.129583, 305.747925 ),
        "Lyon"              :   ( 45.767299, 4.8343287, 182.810547 ),
        "Madrid"            :   ( 40.4166909, -3.7003454, 653.005005 ),
        "Manchester"        :   ( 53.4807125, -2.2343765, 57.892406 ),
        "Manila"            :   ( 14.5833333, 120.9666667, 3.041384 ),
        "Marseille"         :   ( 43.2976116, 5.3810421, 24.785774 ),
        "Melbourne"         :   ( -37.8131869, 144.9629796, 27.000000 ),
        "Mexico City"       :   ( 19.4270499, -99.1275711, 2228.146484 ),
        "Miami"             :   ( 25.7889689, -80.2264393, 0.946764 ),
        "Milan"             :   ( 45.4636889, 9.1881408, 122.246513 ),
        "Minneapolis"       :   ( 44.9799654, -93.2638361, 253.002655 ),
        "Montevideo"        :   ( -34.8833333, -56.1666667, 45.005032 ),
        "Montreal"          :   ( 45.5088889, -73.5541667, 16.620916 ),
        "Moscow"            :   ( 55.755786, 37.617633, 151.189835 ),
        "Mumbai"            :   ( 19.0176147, 72.8561644, 12.408822 ),
        "Munich"            :   ( 48.1391265, 11.5801863, 523.000000 ),
        "New Delhi"         :   ( 28.635308, 77.22496, 213.999054 ),
        "New York"          :   ( 40.7143528, -74.0059731, 9.775694 ),
        "Osaka"             :   ( 34.6937378, 135.5021651, 16.347811 ),
        "Oslo"              :   ( 59.9127263, 10.7460924, 10.502326 ),
        "Paris"             :   ( 48.8566667, 2.3509871, 35.917042 ),
        "Philadelphia"      :   ( 39.952335, -75.163789, 12.465688 ),
        "Prague"            :   ( 50.0878114, 14.4204598, 191.103485 ),
        "Richmond"          :   ( 37.542979, -77.469092, 63.624462 ),
        "Rio de Janeiro"    :   ( -22.9035393, -43.2095869, 9.521935 ),
        "Riyadh"            :   ( 24.6880015, 46.7224333, 613.475281 ),
        "Rome"              :   ( 41.8954656, 12.4823243, 19.704413 ),
        "Rotterdam"         :   ( 51.924216, 4.481776, 2.766272 ),
        "San Francisco"     :   ( 37.7749295, -122.4194155, 15.557819 ),
        "Santiago"          :   ( -33.4253598, -70.5664659, 665.926880 ),
        "Sao Paulo"         :   ( -23.5489433, -46.6388182, 760.344849 ),
        "Seattle"           :   ( 47.6062095, -122.3320708, 53.505501 ),
        "Seoul"             :   ( 37.566535, 126.9779692, 41.980915 ),
        "Shanghai"          :   ( 31.230393, 121.473704, 15.904707 ),
        "Singapore"         :   ( 1.352083, 103.819836, 57.821636 ),
        "St. Petersburg"    :   ( 59.939039, 30.315785, 11.502971 ),
        "Stockholm"         :   ( 59.3327881, 18.0644881, 25.595907 ),
        "Stuttgart"         :   ( 48.7771056, 9.1807688, 249.205185 ),
        "Sydney"            :   ( -33.8599722, 151.2111111, 3.341026 ),
        "Taipei"            :   ( 25.091075, 121.5598345, 32.288563 ),
        "Tashkent"          :   ( 41.2666667, 69.2166667, 430.668427 ),
        "Tehran"            :   ( 35.6961111, 51.4230556, 1180.595947 ),
        "Tel Aviv"          :   ( 32.0599254, 34.7851264, 21.114218 ),
        "The Hague"         :   ( 52.0698576, 4.2911114, 3.686689 ),
        "Tijuana"           :   ( 32.533489, -117.018204, 22.712011 ),
        "Tokyo"             :   ( 35.6894875, 139.6917064, 37.145370 ),
        "Toronto"           :   ( 43.6525, -79.3816667, 90.239403 ),
        "Turin"             :   ( 45.0705621, 7.6866186, 234.000000 ),
        "Utrecht"           :   ( 52.0901422, 5.1096649, 7.720881 ),
        "Vancouver"         :   ( 49.248523, -123.1088, 70.145927 ),
        "Vienna"            :   ( 48.20662, 16.38282, 170.493149 ),
        "Warsaw"            :   ( 52.2296756, 21.0122287, 115.027786 ),
        "Washington"        :   ( 38.8951118, -77.0363658, 7.119641 ),
        "Wellington"        :   ( -41.2924945, 174.7732353, 17.000000 ),
        "Zurich"            :   ( 47.3833333, 8.5333333, 405.500916 ) }


    @staticmethod
    def calculate(
            utcNow,
            latitude, longitude, elevation,
            planets,
            stars,
            satellites, satelliteData, startHourAsDateTimeInUTC, endHourAsDateTimeInUTC,
            comets, cometData, cometApparentMagnitudeData,
            minorPlanets, minorPlanetData, minorPlanetApparentMagnitudeData,
            apparentMagnitudeMaximum,
            logging ):

        data = { }

        timeScale = load.timescale( builtin = True )
        now = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
        nowPlusTwentyFiveHours = now + datetime.timedelta( hours = 25 ) # Rise/set window for most bodies.

        latitude_longitude_elevation = wgs84.latlon( latitude, longitude, elevation )
        location = AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__PLANET_EARTH ] + \
                   wgs84.latlon( latitude, longitude, elevation )
        locationAtNow = location.at( now )

        AstroSkyfield.__calculateMoon(
            now,
            location, locationAtNow,
            data )
        
        AstroSkyfield.__calculateSun(
            now, nowPlusTwentyFiveHours,
            location, locationAtNow,
            data )
        
        AstroSkyfield.__calculatePlanets(
            now, nowPlusTwentyFiveHours,
            location, locationAtNow,
            data,
            planets,
            apparentMagnitudeMaximum )
        
        AstroSkyfield.__calculateStars(
            now, nowPlusTwentyFiveHours,
            location, locationAtNow,
            data,
            stars,
            apparentMagnitudeMaximum )

        AstroSkyfield.__calculateComets(
            now, timeScale,
            location, locationAtNow,
            data,
            comets, cometData,
            apparentMagnitudeMaximum )

        AstroSkyfield.__calculateMinorPlanets(
            now, timeScale,
            location, locationAtNow,
            data,
            minorPlanets, minorPlanetData,
            apparentMagnitudeMaximum, minorPlanetApparentMagnitudeData )

        AstroSkyfield.__calculateSatellites(
            now, timeScale,
            latitude_longitude_elevation,
            data,
            satellites, satelliteData,
            startHourAsDateTimeInUTC, endHourAsDateTimeInUTC )

        return data


#TODO If/when astroskyfield is activated, uncomment the function below.
# Should be called at the top of indicatorlunar before running the __init()__
# to abort if the planet ephemeris is out of date
# and send the message to alert the user.
# Check old versions of indicatorlunar on how to do this.
# Might need to make check_planet_ephemeris_dates() an abstract function in astrobase
# and so also a dummy function in astropyephem.
#   message = check_planet_ephemeris_dates( load( str( Path( __file__ ).parent ) + "/data/planets.bsp" ) )
    # @staticmethod
    # def check_planet_ephemeris_dates( planet_ephemeris ):
    #     message = ""
    #     segment = planet_ephemeris.segments[ 0 ]
    #     start, end = segment.time_range( load.timescale( builtin = True ) )
    #     start = datetime.datetime.strptime( start.tdb_strftime()[ 0 : 10 ], "%Y-%m-%d" ).replace( tzinfo = datetime.timezone.utc )
    #     end = datetime.datetime.strptime( end.tdb_strftime()[ 0 : 10 ], "%Y-%m-%d" ).replace( tzinfo = datetime.timezone.utc )
    #     utcNow = datetime.datetime.now( datetime.timezone.utc )
    #     if start > ( utcNow - datetime.timedelta( days = 31 * 3 ) ):
    #         message = f"The ephemeris start date {start.date()} must be at least three months before today's date."
    #
    #     if end < ( utcNow + datetime.timedelta( days = 31 * 18 ) ):
    #         if len( message ) > 0:
    #             message += "\n"
    #
    #         message += f"The ephemeris end date {end.date()} must be at least eighteen months after today's date."
    #
    #     if len( message ) == 0:
    #         message = None
    #
    #     return message


    @staticmethod
    def getCities():
        return sorted( AstroSkyfield._city_data.keys(), key = locale.strxfrm )


    @staticmethod
    def getCredit():
        return _( "Calculations courtesy of Skyfield. https://rhodesmill.org/skyfield" )


    @staticmethod
    def getLatitudeLongitudeElevation( city ):
        # Latitude = 0, Longitude = 1, Elevation = 2
        return \
            AstroSkyfield._city_data.get( city )[ 0 ], \
            AstroSkyfield._city_data.get( city )[ 1 ], \
            AstroSkyfield._city_data.get( city )[ 2 ]


    @staticmethod
    def getVersion():
        return skyfield.__version__


    @staticmethod
    def __calculateMoon( now, location, locationAtNow, data ):
        key = ( AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON )

        moonAtNow = locationAtNow.observe( AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__MOON ] )
        moonAtNowApparent = moonAtNow.apparent()

        illumination = moonAtNowApparent.fraction_illuminated( AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ] ) * 100
        data[ key + ( AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( illumination ) # Needed for icon.

        nowPlusThirtyOneDays = now + datetime.timedelta( days = 31 ) # Moon phases search window.
        dateTimes, events = almanac.find_discrete( now, nowPlusThirtyOneDays, almanac.moon_phases( AstroSkyfield.__EPHEMERIS_PLANETS ) )
        eventsToDateTimes = dict( zip( events[ : 4 ], dateTimes[ : 4 ].utc_datetime() ) ) # Take first four events to avoid an unforeseen edge case!

        lunarPhase = AstroBase.getLunarPhase(
            illumination,
            eventsToDateTimes[ almanac.MOON_PHASES.index( "Full Moon" ) ],
            eventsToDateTimes[ almanac.MOON_PHASES.index( "New Moon" ) ] )
        data[ key + ( AstroBase.DATA_TAG_PHASE, ) ] = lunarPhase # Needed for notification.

        sunAltAz = locationAtNow.observe( AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ] ).apparent().altaz()
        data[ key + ( AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( position_angle_of( moonAtNowApparent.altaz(), sunAltAz ).radians ) # Needed for icon.

        neverUp = AstroSkyfield.__calculateCommon(
            now,
            now + datetime.timedelta( hours = 36 ), # Rise/set window for the moon.
            location, locationAtNow,
            data, key, AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__MOON ] )

        if not neverUp:
            data[ key + ( AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = eventsToDateTimes[ almanac.MOON_PHASES.index( "First Quarter" ) ]
            data[ key + ( AstroBase.DATA_TAG_FULL, ) ] = eventsToDateTimes[ almanac.MOON_PHASES.index( "Full Moon" ) ]
            data[ key + ( AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = eventsToDateTimes[ almanac.MOON_PHASES.index( "Last Quarter" ) ]
            data[ key + ( AstroBase.DATA_TAG_NEW, ) ] = eventsToDateTimes[ almanac.MOON_PHASES.index( "New Moon" ) ]

            AstroSkyfield.__calculateEclipse( now, data, key, False )


    @staticmethod
    def __calculateSun( now, nowPlusTwentyFiveHours, location, locationAtNow, data ):
        key = ( AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN )

        neverUp = AstroSkyfield.__calculateCommon(
            now, nowPlusTwentyFiveHours,
            location, locationAtNow,
            data, key, AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ] )

        if not neverUp:
            dateTimes, events = almanac.find_discrete(
                now,
                now + datetime.timedelta( days = 366 / 12 * 7 ), # Solstice/equinox search window.
                almanac.seasons( AstroSkyfield.__EPHEMERIS_PLANETS ) )
            eventsToDateTimes = dict( zip( events[ : 2 ], dateTimes[ : 2 ].utc_datetime() ) ) # Take first two events to avoid an unforeseen edge case!

            if almanac.SEASON_EVENTS_NEUTRAL.index( "March Equinox" ) in eventsToDateTimes:
                keyEquinox = almanac.SEASON_EVENTS_NEUTRAL.index( "March Equinox" )

            else:
                keyEquinox = almanac.SEASON_EVENTS_NEUTRAL.index( "September Equinox" )

            data[ key + ( AstroBase.DATA_TAG_EQUINOX, ) ] = eventsToDateTimes[ keyEquinox ]

            if almanac.SEASON_EVENTS_NEUTRAL.index( "June Solstice" ) in eventsToDateTimes:
                keySolstice = almanac.SEASON_EVENTS_NEUTRAL.index( "June Solstice" )

            else:
                keySolstice = almanac.SEASON_EVENTS_NEUTRAL.index( "December Solstice" )

            data[ key + ( AstroBase.DATA_TAG_SOLSTICE, ) ] = eventsToDateTimes[ keySolstice ]

            AstroSkyfield.__calculateEclipse( now, data, key, True )


    @staticmethod
    def __calculateEclipse( now, data, key, isSolar ):

        # https://rhodesmill.org/skyfield/almanac.html
        def __getNativeEclipseType( skyfieldEclipseType, isLunar ):
            nativeEclipseType = None
            if isLunar:
                if skyfieldEclipseType == eclipselib.LUNAR_ECLIPSES.index( "Partial" ):
                    nativeEclipseType = eclipse.EclipseType.PARTIAL

                elif skyfieldEclipseType == eclipselib.LUNAR_ECLIPSES.index( "Penumbral" ):
                    nativeEclipseType = eclipse.EclipseType.PENUMBRAL

                else: # Total
                    nativeEclipseType = eclipse.EclipseType.TOTAL

            else:
                pass #TODO Implement when Skyfield implements solar eclipses.

            return nativeEclipseType


        if isSolar:
            dateTime, eclipseType, latitude, longitude = eclipse.getEclipseSolar( now.utc_datetime() )
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTime
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseType
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude

#TODO When solar eclipses are implemented,
# swap the code above with the code below and
# update the eclipse credit in the indicator.
# https://github.com/skyfielders/python-skyfield/issues/445
            # dateTimes, events, details = eclipselib.solar_eclipses( now, nowPlusOneYear, AstroSkyfield.__EPHEMERIS_PLANETS )
            # data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTimes[ 0 ].utc_datetime()
            # data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = __getNativeEclipseType( events[ 0 ], False )

        else:
#TODO Submitted a discussion to see if possible to get the lat/long.
# If feasible, add here and remove check in indicator front-end.
# https://github.com/skyfielders/python-skyfield/discussions/801
            nowPlusOneYear = now + datetime.timedelta( days = 366 ) # Eclipse search window.
            dateTimes, events, details = eclipselib.lunar_eclipses( now, nowPlusOneYear, AstroSkyfield.__EPHEMERIS_PLANETS )
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTimes[ 0 ].utc_datetime()
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = __getNativeEclipseType( events[ 0 ], True )


    @staticmethod
    def __calculatePlanets( now, nowPlusTwentyFiveHours, location, locationAtNow, data, planets, apparentMagnitudeMaximum ):
        earthAtNow = AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__PLANET_EARTH ].at( now )
        for planetName in planets:
            planet = AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__PLANET_MAPPINGS[ planetName ] ]
            apparentMagnitude = planetary_magnitude( earthAtNow.observe( planet ) )
            if planetName == AstroBase.PLANET_SATURN and math.isnan( apparentMagnitude ): # Saturn can return NaN...
                apparentMagnitude = 0.46 # Set the mean apparent magnitude (as per Wikipedia).

            if apparentMagnitude <= apparentMagnitudeMaximum:
                AstroSkyfield.__calculateCommon(
                    now, nowPlusTwentyFiveHours,
                    location, locationAtNow,
                    data, ( AstroBase.BodyType.PLANET, planetName ), planet )


    @staticmethod
    def __calculateStars( now, nowPlusTwentyFiveHours, location, locationAtNow, data, stars, apparentMagnitudeMaximum ):
        for star in stars:
            theStar = AstroSkyfield.__EPHEMERIS_STARS.loc[ AstroBase.getStarHIP( star ) ]
            if theStar.magnitude <= apparentMagnitudeMaximum:
                AstroSkyfield.__calculateCommon(
                    now, nowPlusTwentyFiveHours,
                    location, locationAtNow,
                    data, ( AstroBase.BodyType.STAR, star ),
                    Star.from_dataframe( theStar ) )


#TODO Issue logged with regard to slow speed of processing comets / minor planets:
# https://github.com/skyfielders/python-skyfield/issues/490
# https://github.com/skyfielders/python-skyfield/pull/532
# https://github.com/skyfielders/python-skyfield/pull/526
    @staticmethod
    def __calculateComets(
            now, timeScale,
            location, locationAtNow,
            data,
            comets, orbitalElementData,
            apparentMagnitudeMaximum ):

        with io.BytesIO() as f:
            for key in comets:
                if key in orbitalElementData:
                    f.write( ( orbitalElementData[ key ].getData() + '\n' ).encode() )

            f.seek( 0 )

            dataframe = mpc.load_comets_dataframe( f )

        dataframe = dataframe.set_index( "designation", drop = False )

        sun = AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ]
        sunAtNow = sun.at( now )

        # Found that using 25 hours throws a ValueError, so using 48.
        # https://github.com/skyfielders/python-skyfield/issues/959
        nowPlusFortyEightHours = now + datetime.timedelta( hours = 48 )

        for name, row in dataframe.iterrows():
            key = ( AstroBase.BodyType.COMET, name.upper() )
            body = sun + mpc.comet_orbit( row, timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )

            ra, dec, earthBodyDistance = locationAtNow.observe( body ).radec()
            ra, dec, sunBodyDistance = sunAtNow.observe( body ).radec()

            # According to MPC, always use the gk model.
            #   https://github.com/skyfielders/python-skyfield/issues/416
            apparent_magnitude = AstroBase.getApparentMagnitude_gk(
                row[ "magnitude_g" ], row[ "magnitude_k" ],
                earthBodyDistance.au, sunBodyDistance.au )

            if apparent_magnitude < apparentMagnitudeMaximum:
                AstroSkyfield.__calculateCommon(
                    now, nowPlusFortyEightHours,
                    location, locationAtNow,
                    data, key, body )


#TODO Issue logged with regard to slow speed of processing comets / minor planets:
# https://github.com/skyfielders/python-skyfield/issues/490
# https://github.com/skyfielders/python-skyfield/pull/532
# https://github.com/skyfielders/python-skyfield/pull/526
    @staticmethod
    def __calculateMinorPlanets(
            now, timeScale,
            location, locationAtNow,
            data,
            minorPlanets, orbitalElementData,
            apparentMagnitudeMaximum, apparentMagnitudeData ):

        with io.BytesIO() as f:
            for key in minorPlanets:
                if key in orbitalElementData and \
                   key in apparentMagnitudeData and \
                   float( apparentMagnitudeData[ key ].getApparentMagnitude() ) <= apparentMagnitudeMaximum:
                    f.write( ( orbitalElementData[ key ].getData() + '\n' ).encode() )

            f.seek( 0 )
            dataframe = mpc.load_mpcorb_dataframe( f )

        dataframe = dataframe.set_index( "designation", drop = False )
        sun = AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ]
        for name, row in dataframe.iterrows():
            key = ( AstroBase.BodyType.MINOR_PLANET, name.upper() )
            body = sun + mpc.mpcorb_orbit( row, timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )

            # Found that using 25 hours throws a ValueError, so using 48.
            # https://github.com/skyfielders/python-skyfield/issues/959
            nowPlusFortyEightHours = now + datetime.timedelta( hours = 48 )
            AstroSkyfield.__calculateCommon(
                now, nowPlusFortyEightHours,
                location, locationAtNow,
                data, key, body )


    @staticmethod
    def __calculateCommon( now, nowPlusWhatever, location, locationAtNow, data, key, body ):
        neverUp = False

        # https://rhodesmill.org/skyfield/almanac.html#risings-and-settings
        rise_date_time, rises = almanac.find_risings( location, body, now, nowPlusWhatever )
        set_date_time, sets = almanac.find_settings( location, body, now, nowPlusWhatever )

        if rises.item( 0 ) and sets.item( 0 ): # Rises and sets.
            data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = rise_date_time[ 0 ].utc_datetime()
            data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = set_date_time[ 0 ].utc_datetime()

            alt, az, earthBodyDistance = locationAtNow.observe( body ).apparent().altaz()
            data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
            data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

        elif not sets.item( 0 ): # Never sets (always up).
            alt, az, earthBodyDistance = locationAtNow.observe( body ).apparent().altaz()
            data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
            data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

        else: # not rises.item( 0 )
            neverUp = True # Never rises (never up).  It is impossible to be never up AND always up.

        return neverUp


#TODO Read
#    https://rhodesmill.org/skyfield/earth-satellites.html
# and ensure the code below follows the example as best practise.
    # References:
    #    https://github.com/skyfielders/python-skyfield/issues/327
    #    https://github.com/skyfielders/python-skyfield/issues/558
    @staticmethod
    def __calculateSatellites(
            now, timeScale,
            latitude_longitude_elevation,
            data,
            satellites, satelliteData,
            startHourAsDateTimeInUTC, endHourAsDateTimeInUTC ):
        end = now + datetime.timedelta( hours = AstroBase.SATELLITE_SEARCH_DURATION_HOURS )
        windows = AstroBase.getStartEndWindows( now.utc_datetime(), end.utc_datetime(), startHourAsDateTimeInUTC, endHourAsDateTimeInUTC )
        isTwilightFunction = almanac.dark_twilight_day( AstroSkyfield.__EPHEMERIS_PLANETS, latitude_longitude_elevation )
        for satellite in satellites:
            if satellite in satelliteData:
                key = ( AstroBase.BodyType.SATELLITE, satellite )
                earthSatellite = EarthSatellite.from_satrec( satelliteData[ satellite ].getSatelliteRecord(), timeScale )
                for startDateTime, endDateTime in windows:
                    foundPass = AstroSkyfield.__calculateSatellite(
                        timeScale.from_datetime( startDateTime ),
                        timeScale.from_datetime( endDateTime ),
                        timeScale,
                        latitude_longitude_elevation,
                        data,
                        key,
                        earthSatellite,
                        isTwilightFunction )

                    if foundPass:
                        break


    @staticmethod
    def __calculateSatellite(
            startDateTime, endDateTime, timeScale,
            latitude_longitude_elevation,
            data, key,
            earthSatellite,
            isTwilightFunction ):
        foundPass = False
        riseDateTime = None
        culminationDateTimes = [ ] # Culminate may occur more than once, so collect them all.
        dateTimes, events = earthSatellite.find_events( latitude_longitude_elevation, startDateTime, endDateTime, altitude_degrees = 20.0 )
        for dateTime, event in zip( dateTimes, events ):
            if event == 0: # Satellite rose above altitude_degrees.
                riseDateTime = dateTime

            elif event == 1: # Satellite culminated and started to descend again.
                culminationDateTimes.append( dateTime )

            else: # Satellite fell below altitude_degrees.
                if riseDateTime is not None and \
                   culminationDateTimes and \
                   AstroSkyfield.__isSatellitePassVisible( timeScale, riseDateTime, dateTime, isTwilightFunction, earthSatellite ):
                    data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = riseDateTime.utc_datetime()
                    alt, az, earthSatelliteDistance = ( earthSatellite - latitude_longitude_elevation ).at( riseDateTime ).altaz()
                    data[ key + ( AstroBase.DATA_TAG_RISE_AZIMUTH, ) ] = str( az.radians )

                    data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = dateTime.utc_datetime()
                    alt, az, earthSatelliteDistance = ( earthSatellite - latitude_longitude_elevation ).at( dateTime ).altaz()
                    data[ key + ( AstroBase.DATA_TAG_SET_AZIMUTH, ) ] = str( az.radians )

                    foundPass = True
                    break

                riseDateTime = None
                culminationDateTimes = [ ]

        return foundPass


    @staticmethod
    def __isSatellitePassVisible(
            timeScale, startDateTime, endDateTime,
            isTwilightFunction,
            earthSatellite ):
        secondsFromRiseToSet = ( endDateTime.utc_datetime() - startDateTime.utc_datetime() ).total_seconds()
        rangeStart = math.ceil( startDateTime.utc.second )
        rangeEnd = math.ceil( startDateTime.utc.second + secondsFromRiseToSet )
        rangeStep = math.ceil( secondsFromRiseToSet / 60.0 ) # Set a step interval of 60 seconds.
        if rangeStep < 1.0:
            rangeStep = 1.0

        transitRange = timeScale.utc(
            startDateTime.utc.year,
            startDateTime.utc.month,
            startDateTime.utc.day,
            startDateTime.utc.hour,
            startDateTime.utc.minute,
            range( rangeStart, rangeEnd, rangeStep ) )

        isTwilightAstronomical = isTwilightFunction( transitRange ) == 1 # almanac.TWILIGHTS[ 1 ], Astronomical twilight
        isTwilightNautical = isTwilightFunction( transitRange ) == 2 # almanac.TWILIGHTS[ 2 ], Nautical twilight
        isSunlit = earthSatellite.at( transitRange ).is_sunlit( AstroSkyfield.__EPHEMERIS_PLANETS )
        isVisible = False
        for twilightAstronomical, twilightNautical, sunlit in zip( isTwilightAstronomical, isTwilightNautical, isSunlit ):
            if sunlit and ( twilightAstronomical or twilightNautical ):
                isVisible = True
                break

        return isVisible
