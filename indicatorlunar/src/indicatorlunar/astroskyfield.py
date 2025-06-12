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


''' Calculate astronomical information using Skyfield. '''


#TODO ALL THE TODOS BELOW IN REGARDS TO 32 BIT, NUMPY, JPLEPHEM AND PANDAS
# NEED TO BE CHECKED AGAINST THE CREATE STARS/PLANETS EPHEMERIS SCRIPTS
# AS THOSE ARE NOW UP TO DATE.


#TODO Do NOT include the tools/scripts in the release.


#TODO Is it possible to do a check to see if the planets.bsp date range is valid?
# That is, starts at least a month before today's date AND runs far enough into
# the future (whatever "far enough" means).
# If the planets.bsp is not okay, then what?
# Flash message to user?
# Autoswitch to astropyephem?
# I think that if planets.bsp is no good, then NONE of the calculations will work!


#TODO Document perhaps in the PyPI page about how to make a new planets.bsp


#TODO
# Is there a need to pin
#    requests
#    sgp4
#
# Neither seem to have any issue but test on Debian 32 bit!


#TODO Determine if 32 or 64 bit:
#    getconf LONG_BIT
# either 32 or 64


#TODO What happens if the planets.bsp start/end date no longer matches with today's date?
# For example, looking for the next eclipse and there is only a month of data left in the bsp?
# How to check for this...?
# What happens if there is 6 months of data but a very high latitude (+- 89)
# and it winter so the sun never rises (or some planet never rises)
# or is summer so the sun never sets (or some planet never sets).
# Is this an issue?
#
# Or a user switches for a new bsp for which it's date range ends before today?
# Maybe just do a date check: end date < today's date is error.
#
# To get the start/end dates:
#
#     from skyfield.api import load
#
#     ts = load.timescale()
#     planets = load(  "../../../IndicatorLunarData/de421.bsp" )
#
#     start, end = planets.segments[ 0 ].time_range( ts )
#     print( start.tdb_strftime().split()[ 0 ] )
#     print( end.tdb_strftime().split()[ 0 ] )
#
# 1849-12-26
# 2150-01-22


#TODO
# Pinning may be a normal thing for all indicators...
# The pyproject.tom.specific for lunar may need to change somehow (if skyfield is used)
# and any install instructions will need to include the pinning there,
# rather than in the dependencies of pyproject.toml (which should contain no
# dependencies). 


#TODO Do I need to explicitly put pandas and/or numpy into the dependencies?
# May need to do so for pinning...but instead, have alternate install instructions.


#TODO
# https://github.com/brandon-rhodes/python-jplephem/issues/60


#TODO Unable to install numpy/pandas on Debian 12 32 bit.
# This means skyfield will not work on 32 bit...
# So figure out what to do if/when astroskyfield is used.
# Keep astropyephem as a separate install for 32 bit?
#
# I thought skyfield needs mumpy and pandas, but only needs numpy (I believe).
# I need pandas for the create stars epehemeris script...so that script will
# run on 32 bit.
# So maybe check again if it is possible to install numpy (pinned or otherwise)
# on 32 bit.
#
# Maybe try on Debian 12 32 bit on the virtual machine?
# Did a 
#   python3 -m pip install numpy
# and successfully installed numpy 2.2.6
# then installed skyfield and ran an example which uses numpy and it worked.
# How the hell does numpy latest version install when supposedly should not
# install from 1.22.0 onwards for 32 bit...?
# https://numpy.org/doc/2.0/release/1.22.0-notes.html
#
# Need to clarify with Numpy; how is it the latest version installed on Debian 12 32 bit...?


#TODO Ran the indicator with skyfield and debug = True and got the following:
# magnitude : timing (seconds)
# 7 : 6
# 8 : 6
# 9 : 6
# 10 : 7
# 11 : 9
# 12 : 16
# 13 : 37
# 14 : 77 
# 15 : 159
#
# Maybe tidy up astroskyfield then do same timing tests...
# ...maybe release indicatorlunar with skyfield instead of pyephem?
# Ask Oleg!
#
# How long does it take to run at mag 7 on laptop?


#TODO If/when astroskyfield is included in the release and ephem is dropped...
#
# In pyprojectspecific.toml, replace
#     dependencies = [
#       "ephem",
#       "requests",
#       "sgp4" ]
# with
#     dependencies = [
#       "numpy",
#       "pandas",    # Needed for mpc (and I think loading stars/planets).
#       "requests",
#       "sgp4",
#       "skyfield" ]
#
# In MANIFESTspecific.in, replace
#     exclude src/indicatorlunar/astroskyfield.py
#     exclude src/indicatorlunar/meteorshowertest.py
# with
#     exclude src/indicatorlunar/meteorshowertest.py
#     recursive-include src/{indicator_name}/data *   <--- Is this needed?  Will the data files be included by default?
#
# Need a check in tools/build_wheel.py to ensure planets.bsp / starts.dat are present?
# Perhaps/hopefully not; instead include these in the MANIFESTspecific.in
# and hopefully if these files are not present, the build gives a warning/error.
#
# Add astroskyfield.py to locale/POTFILES.in.


#TODO Might be able to use new OMM method to load satellite data:
#   https://github.com/skyfielders/python-skyfield/commit/9d4087bb2b8515b6441362fddff8bfe83142de6b


#TODO Might be of use:
#   https://github.com/skyfielders/python-skyfield/issues/996


#TODO Might be of use:
#   https://github.com/skyfielders/python-skyfield/issues/993


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

from . import eclipse

from .astrobase import AstroBase


class AstroSkyfield( AstroBase ):
    ''' Wrapper frontend to the Skyfield library. '''

    # Planets ephemeris MUST be created using create_ephemeris_planets.py.
    _EPHEMERIS_PLANETS = (
        load( str( Path( __file__ ).parent / "data" / "planets.bsp" ) ) )

    # Stars ephemeris MUST be created using create_ephemeris_stars.py.
    ephemeris_stars_path = Path( __file__ ).parent / "data" / "stars.dat"
    with load.open( str( ephemeris_stars_path ) ) as f:
        _EPHEMERIS_STARS = hipparcos.load_dataframe( f )

    # Name tags for bodies.
    _MOON = "MOON"
    _SUN = "SUN"

    _PLANET_EARTH = "EARTH"

    _PLANET_MAPPINGS = {
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
    _CITY_LATITUDE = 0
    _CITY_LONGITUDE = 1
    _CITY_ELEVATION = 2

    _city_data = {
        "Abu Dhabi"        : ( 24.4666667, 54.3666667, 6.296038 ),
        "Adelaide"         : ( -34.9305556, 138.6205556, 49.098354 ),
        "Almaty"           : ( 43.255058, 76.912628, 785.522156 ),
        "Amsterdam"        : ( 52.3730556, 4.8922222, 14.975505 ),
        "Antwerp"          : ( 51.21992, 4.39625, 7.296879 ),
        "Arhus"            : ( 56.162939, 10.203921, 26.879421 ),
        "Athens"           : ( 37.97918, 23.716647, 47.597061 ),
        "Atlanta"          : ( 33.7489954, -84.3879824, 319.949738 ),
        "Auckland"         : ( -36.8484597, 174.7633315, 21.000000 ),
        "Baltimore"        : ( 39.2903848, -76.6121893, 10.258920 ),
        "Bangalore"        : ( 12.9715987, 77.5945627, 911.858398 ),
        "Bangkok"          : ( 13.7234186, 100.4762319, 4.090096 ),
        "Barcelona"        : ( 41.387917, 2.1699187, 19.991053 ),
        "Beijing"          : ( 39.904214, 116.407413, 51.858883 ),
        "Berlin"           : ( 52.5234051, 13.4113999, 45.013939 ),
        "Birmingham"       : ( 52.4829614, -1.893592, 141.448563 ),
        "Bogota"           : ( 4.5980556, -74.0758333, 2614.037109 ),
        "Bologna"          : ( 44.4942191, 11.3464815, 72.875923 ),
        "Boston"           : ( 42.3584308, -71.0597732, 15.338848 ),
        "Bratislava"       : ( 48.1483765, 17.1073105, 155.813446 ),
        "Brazilia"         : ( -14.235004, -51.92528, 259.063477 ),
        "Brisbane"         : ( -27.4709331, 153.0235024, 28.163914 ),
        "Brussels"         : ( 50.8503, 4.35171, 26.808620 ),
        "Bucharest"        : ( 44.437711, 26.097367, 80.407768 ),
        "Budapest"         : ( 47.4984056, 19.0407578, 106.463295 ),
        "Buenos Aires"     : ( -34.6084175, -58.3731613, 40.544090 ),
        "Cairo"            : ( 30.064742, 31.249509, 20.248013 ),
        "Calgary"          : ( 51.045, -114.0572222, 1046.000000 ),
        "Cape Town"        : ( -33.924788, 18.429916, 5.838447 ),
        "Caracas"          : ( 10.491016, -66.902061, 974.727417 ),
        "Chicago"          : ( 41.8781136, -87.6297982, 181.319290 ),
        "Cleveland"        : ( 41.4994954, -81.6954088, 198.879639 ),
        "Cologne"          : ( 50.9406645, 6.9599115, 59.181450 ),
        "Colombo"          : ( 6.927468, 79.848358, 9.969995 ),
        "Columbus"         : ( 39.9611755, -82.9987942, 237.651932 ),
        "Copenhagen"       : ( 55.693403, 12.583046, 6.726723 ),
        "Dallas"           : ( 32.802955, -96.769923, 154.140625 ),
        "Detroit"          : ( 42.331427, -83.0457538, 182.763428 ),
        "Dresden"          : ( 51.0509912, 13.7336335, 114.032356 ),
        "Dubai"            : ( 25.2644444, 55.3116667, 8.029230 ),
        "Dublin"           : ( 53.344104, -6.2674937, 8.214323 ),
        "Dusseldorf"       : ( 51.2249429, 6.7756524, 43.204800 ),
        "Edinburgh"        : ( 55.9501755, -3.1875359, 84.453995 ),
        "Frankfurt"        : ( 50.1115118, 8.6805059, 106.258285 ),
        "Geneva"           : ( 46.2057645, 6.141593, 379.026245 ),
        "Genoa"            : ( 44.4070624, 8.9339889, 35.418076 ),
        "Glasgow"          : ( 55.8656274, -4.2572227, 38.046883 ),
        "Gothenburg"       : ( 57.6969943, 11.9865, 15.986326 ),
        "Guangzhou"        : ( 23.129163, 113.264435, 18.892920 ),
        "Hamburg"          : ( 53.5538148, 9.9915752, 5.104634 ),
        "Hanoi"            : ( 21.0333333, 105.85, 20.009024 ),
        "Helsinki"         : ( 60.1698125, 24.9382401, 7.153307 ),
        "Ho Chi Minh City" : ( 10.75918, 106.662498, 10.757121 ),
        "Hong Kong"        : ( 22.396428, 114.109497, 321.110260 ),
        "Houston"          : ( 29.7628844, -95.3830615, 6.916622 ),
        "Istanbul"         : ( 41.00527, 28.97696, 37.314278 ),
        "Jakarta"          : ( -6.211544, 106.845172, 10.218226 ),
        "Johannesburg"     : ( -26.1704415, 27.9717606, 1687.251099 ),
        "Kansas City"      : ( 39.1066667, -94.6763889, 274.249390 ),
        "Kiev"             : ( 50.45, 30.5233333, 157.210175 ),
        "Kuala Lumpur"     : ( 3.139003, 101.686855, 52.271698 ),
        "Leeds"            : ( 53.7996388, -1.5491221, 47.762367 ),
        "Lille"            : ( 50.6371834, 3.0630174, 28.139490 ),
        "Lima"             : ( -12.0433333, -77.0283333, 154.333740 ),
        "Lisbon"           : ( 38.7070538, -9.1354884, 2.880179 ),
        "London"           : ( 51.5001524, -0.1262362, 14.605533 ),
        "Los Angeles"      : ( 34.0522342, -118.2436849, 86.847092 ),
        "Luxembourg"       : ( 49.815273, 6.129583, 305.747925 ),
        "Lyon"             : ( 45.767299, 4.8343287, 182.810547 ),
        "Madrid"           : ( 40.4166909, -3.7003454, 653.005005 ),
        "Manchester"       : ( 53.4807125, -2.2343765, 57.892406 ),
        "Manila"           : ( 14.5833333, 120.9666667, 3.041384 ),
        "Marseille"        : ( 43.2976116, 5.3810421, 24.785774 ),
        "Melbourne"        : ( -37.8131869, 144.9629796, 27.000000 ),
        "Mexico City"      : ( 19.4270499, -99.1275711, 2228.146484 ),
        "Miami"            : ( 25.7889689, -80.2264393, 0.946764 ),
        "Milan"            : ( 45.4636889, 9.1881408, 122.246513 ),
        "Minneapolis"      : ( 44.9799654, -93.2638361, 253.002655 ),
        "Montevideo"       : ( -34.8833333, -56.1666667, 45.005032 ),
        "Montreal"         : ( 45.5088889, -73.5541667, 16.620916 ),
        "Moscow"           : ( 55.755786, 37.617633, 151.189835 ),
        "Mumbai"           : ( 19.0176147, 72.8561644, 12.408822 ),
        "Munich"           : ( 48.1391265, 11.5801863, 523.000000 ),
        "New Delhi"        : ( 28.635308, 77.22496, 213.999054 ),
        "New York"         : ( 40.7143528, -74.0059731, 9.775694 ),
        "Osaka"            : ( 34.6937378, 135.5021651, 16.347811 ),
        "Oslo"             : ( 59.9127263, 10.7460924, 10.502326 ),
        "Paris"            : ( 48.8566667, 2.3509871, 35.917042 ),
        "Philadelphia"     : ( 39.952335, -75.163789, 12.465688 ),
        "Prague"           : ( 50.0878114, 14.4204598, 191.103485 ),
        "Richmond"         : ( 37.542979, -77.469092, 63.624462 ),
        "Rio de Janeiro"   : ( -22.9035393, -43.2095869, 9.521935 ),
        "Riyadh"           : ( 24.6880015, 46.7224333, 613.475281 ),
        "Rome"             : ( 41.8954656, 12.4823243, 19.704413 ),
        "Rotterdam"        : ( 51.924216, 4.481776, 2.766272 ),
        "San Francisco"    : ( 37.7749295, -122.4194155, 15.557819 ),
        "Santiago"         : ( -33.4253598, -70.5664659, 665.926880 ),
        "Sao Paulo"        : ( -23.5489433, -46.6388182, 760.344849 ),
        "Seattle"          : ( 47.6062095, -122.3320708, 53.505501 ),
        "Seoul"            : ( 37.566535, 126.9779692, 41.980915 ),
        "Shanghai"         : ( 31.230393, 121.473704, 15.904707 ),
        "Singapore"        : ( 1.352083, 103.819836, 57.821636 ),
        "St. Petersburg"   : ( 59.939039, 30.315785, 11.502971 ),
        "Stockholm"        : ( 59.3327881, 18.0644881, 25.595907 ),
        "Stuttgart"        : ( 48.7771056, 9.1807688, 249.205185 ),
        "Sydney"           : ( -33.8599722, 151.2111111, 3.341026 ),
        "Taipei"           : ( 25.091075, 121.5598345, 32.288563 ),
        "Tashkent"         : ( 41.2666667, 69.2166667, 430.668427 ),
        "Tehran"           : ( 35.6961111, 51.4230556, 1180.595947 ),
        "Tel Aviv"         : ( 32.0599254, 34.7851264, 21.114218 ),
        "The Hague"        : ( 52.0698576, 4.2911114, 3.686689 ),
        "Tijuana"          : ( 32.533489, -117.018204, 22.712011 ),
        "Tokyo"            : ( 35.6894875, 139.6917064, 37.145370 ),
        "Toronto"          : ( 43.6525, -79.3816667, 90.239403 ),
        "Turin"            : ( 45.0705621, 7.6866186, 234.000000 ),
        "Utrecht"          : ( 52.0901422, 5.1096649, 7.720881 ),
        "Vancouver"        : ( 49.248523, -123.1088, 70.145927 ),
        "Vienna"           : ( 48.20662, 16.38282, 170.493149 ),
        "Warsaw"           : ( 52.2296756, 21.0122287, 115.027786 ),
        "Washington"       : ( 38.8951118, -77.0363658, 7.119641 ),
        "Wellington"       : ( -41.2924945, 174.7732353, 17.000000 ),
        "Zurich"           : ( 47.3833333, 8.5333333, 405.500916 ) }


    @staticmethod
    def calculate(
        utc_now,
        latitude,
        longitude,
        elevation,
        planets,
        stars,
        satellites,
        satellite_data,
        start_hour_as_date_time_in_utc,
        end_hour_as_date_time_in_utc,
        comets,
        comet_data,
        minor_planets,
        minor_planet_data,
        minor_planet_apparent_magnitude_data,
        apparent_magnitude_maximum,
        logging ):

        data = { }

        timescale = load.timescale( builtin = True ) #TODO Was "timeScale =" so hopefully the rename to timescale does not clash with load.timescale.
        now = (
            timescale.utc(
                utc_now.year,
                utc_now.month,
                utc_now.day,
                utc_now.hour,
                utc_now.minute,
                utc_now.second ) )

        # Rise/set window for most bodies.
        now_plus_twenty_five_hours = now + datetime.timedelta( hours = 25 )

        latitude_longitude_elevation = (
            wgs84.latlon( latitude, longitude, elevation ) )

        location = (
            AstroSkyfield._EPHEMERIS_PLANETS[ AstroSkyfield._PLANET_EARTH ] +
            wgs84.latlon( latitude, longitude, elevation ) )

        location_at_now = location.at( now )

        AstroSkyfield._calculate_moon(
            now,
            location,
            location_at_now,
            data )

        AstroSkyfield._calculate_sun(
            now,
            now_plus_twenty_five_hours,
            location,
            location_at_now,
            data )

        AstroSkyfield._calculate_planets(
            now,
            now_plus_twenty_five_hours,
            location,
            location_at_now,
            data,
            planets,
            apparent_magnitude_maximum )

        AstroSkyfield._calculate_stars(
            now,
            now_plus_twenty_five_hours,
            location,
            location_at_now,
            data,
            stars,
            apparent_magnitude_maximum )

        AstroSkyfield._calculate_comets(
            now,
            timescale,
            location,
            location_at_now,
            data,
            comets,
            comet_data,
            apparent_magnitude_maximum )

        AstroSkyfield._calculate_minor_planets(
            now,
            timescale,
            location,
            location_at_now,
            data,
            minor_planets,
            minor_planet_data,
            apparent_magnitude_maximum,
            minor_planet_apparent_magnitude_data )

        AstroSkyfield._calculate_satellites(
            now,
            timescale,
            latitude_longitude_elevation,
            data,
            satellites,
            satellite_data,
            start_hour_as_date_time_in_utc,
            end_hour_as_date_time_in_utc )

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
    def get_cities():
        return sorted( AstroSkyfield._city_data.keys(), key = locale.strxfrm )


    @staticmethod
    def get_credit():
        return "Skyfield https://github.com/skyfielders/python-skyfield"


    @staticmethod
    def get_latitude_longitude_elevation(
        city ):

        city_ = AstroSkyfield._city_data.get( city )

        return (
            city_[ AstroSkyfield._CITY_LATITUDE ],
            city_[ AstroSkyfield._CITY_LONGITUDE ],
            city_[ AstroSkyfield._CITY_ELEVATION ] )


    @staticmethod
    def get_version():
        return skyfield.__version__


    @staticmethod
    def _calculate_moon(
        now,
        location,
        location_at_now,
        data ):

        key = ( AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON )
        moon = AstroSkyfield._EPHEMERIS_PLANETS[ AstroSkyfield._MOON ]
        moon_at_now_apparent = location_at_now.observe( moon ).apparent()
        sun = AstroSkyfield._EPHEMERIS_PLANETS[ AstroSkyfield._SUN ]

        # Needed for icon.
        illumination = moon_at_now_apparent.fraction_illuminated( sun ) * 100
        data[ key + ( AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( illumination )

        # Moon phases search window.
        now_plus_thirty_one_days = now + datetime.timedelta( days = 31 )

        date_times, events = (
            almanac.find_discrete(
                now,
                now_plus_thirty_one_days,
                almanac.moon_phases( AstroSkyfield._EPHEMERIS_PLANETS ) ) )

        # Take first four events to avoid an unforeseen edge case!
        events_to_date_times = (
            dict( zip( events[ : 4 ], date_times[ : 4 ].utc_datetime() ) ) )

        index_full_moon = almanac.MOON_PHASES.index( "Full Moon" )
        index_new_moon = almanac.MOON_PHASES.index( "New Moon" )
        lunar_phase = (
            AstroBase.get_lunar_phase(
                illumination,
                events_to_date_times[ index_full_moon ],
                events_to_date_times[ index_new_moon ] ) )

        # Needed for notification.
        data[ key + ( AstroBase.DATA_TAG_PHASE, ) ] = lunar_phase

        sun_alt_az = location_at_now.observe( sun ).apparent().altaz()

        # Needed for icon.
        bright_limb = (
            position_angle_of(
                moon_at_now_apparent.altaz(),
                sun_alt_az ) )

        data[ key + ( AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = (
            str( bright_limb.radians ) )

        never_up = (
            AstroSkyfield._calculate_common(
                now,
                now + datetime.timedelta( hours = 36 ), # Rise/set window for the moon.
                location,
                location_at_now,
                data,
                key,
                moon ) )

        if not never_up:
            data[ key + ( AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = (
                events_to_date_times[ almanac.MOON_PHASES.index( "First Quarter" ) ] )

            data[ key + ( AstroBase.DATA_TAG_FULL, ) ] = (
                events_to_date_times[ almanac.MOON_PHASES.index( "Full Moon" ) ] )

            data[ key + ( AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = (
                events_to_date_times[ almanac.MOON_PHASES.index( "Last Quarter" ) ] )

            data[ key + ( AstroBase.DATA_TAG_NEW, ) ] = (
                events_to_date_times[ almanac.MOON_PHASES.index( "New Moon" ) ] )

            AstroSkyfield._calculate_eclipse( now, data, key, False )


    @staticmethod
    def _calculate_sun(
        now,
        now_plus_twenty_five_hours,
        location,
        location_at_now, data ):

        key = ( AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN )

        never_up = (
            AstroSkyfield._calculate_common(
                now,
                now_plus_twenty_five_hours,
                location,
                location_at_now,
                data,
                key,
                AstroSkyfield._EPHEMERIS_PLANETS[ AstroSkyfield._SUN ] ) )

        if not never_up:
            date_times, events = (
                almanac.find_discrete(
                    now,
                    now + datetime.timedelta( days = 366 / 12 * 7 ), # Solstice/equinox search window.
                    almanac.seasons( AstroSkyfield._EPHEMERIS_PLANETS ) ) )

            # Take first two events to avoid an unforeseen edge case!
            events_to_date_times = (
                dict( zip( events[ : 2 ], date_times[ : 2 ].utc_datetime() ) ) )

            index_equinox_march = (
                almanac.SEASON_EVENTS_NEUTRAL.index( "March Equinox" ) )

            if index_equinox_march in events_to_date_times:
                key_equinox = index_equinox_march

            else:
                key_equinox = (
                    almanac.SEASON_EVENTS_NEUTRAL.index( "September Equinox" ) )

            data[ key + ( AstroBase.DATA_TAG_EQUINOX, ) ] = (
                events_to_date_times[ key_equinox ] )

            index_solstice_june = (
                almanac.SEASON_EVENTS_NEUTRAL.index( "June Solstice" ) )

            if index_solstice_june in events_to_date_times:
                key_solstice = index_solstice_june

            else:
                key_solstice = (
                    almanac.SEASON_EVENTS_NEUTRAL.index( "December Solstice" ) )

            data[ key + ( AstroBase.DATA_TAG_SOLSTICE, ) ] = (
                events_to_date_times[ key_solstice ] )

            AstroSkyfield._calculate_eclipse( now, data, key, True )


    @staticmethod
    def _calculate_eclipse(
        now,
        data,
        key,
        is_solar ):

        # https://rhodesmill.org/skyfield/almanac.html
        def _get_native_eclipse_type(
            skyfield_eclipse_type,
            is_lunar ):

            native_eclipse_type = None
            if is_lunar:
                index_eclipse_partial = (
                    eclipselib.LUNAR_ECLIPSES.index( "Partial" ) )

                index_eclipse_penumbral = (
                    eclipselib.LUNAR_ECLIPSES.index( "Penumbral" ) )

                if skyfield_eclipse_type == index_eclipse_partial:
                    native_eclipse_type = eclipse.EclipseType.PARTIAL

                elif skyfield_eclipse_type == index_eclipse_penumbral:
                    native_eclipse_type = eclipse.EclipseType.PENUMBRAL

                else: # Total
                    native_eclipse_type = eclipse.EclipseType.TOTAL

            else:
                pass #TODO Implement when Skyfield implements solar eclipses.

            return native_eclipse_type


        if is_solar:
            date_time, eclipse_type, latitude, longitude = (
                eclipse.get_eclipse_solar( now.utc_datetime() ) )

            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = date_time
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipse_type
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude

#TODO When solar eclipses are implemented,
# swap the code above with the code below and
# update the eclipse credit in the indicator.
# https://github.com/skyfielders/python-skyfield/issues/445
            # dateTimes, events, details = eclipselib.solar_eclipses( now, now_plus_one_year, AstroSkyfield._EPHEMERIS_PLANETS )
            # data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTimes[ 0 ].utc_datetime()
            # data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = _get_native_eclipse_type( events[ 0 ], False )

        else:
#TODO Submitted a discussion to see if possible to get the lat/long.
# If feasible, add here and remove check in indicator front-end.
# https://github.com/skyfielders/python-skyfield/discussions/801
            now_plus_one_year = now + datetime.timedelta( days = 366 ) # Eclipse search window.
            date_times, events, details = (
                eclipselib.lunar_eclipses(
                    now,
                    now_plus_one_year,
                    AstroSkyfield._EPHEMERIS_PLANETS ) )

            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = (
                date_times[ 0 ].utc_datetime() )

            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = (
                _get_native_eclipse_type( events[ 0 ], True ) )


    @staticmethod
    def _calculate_planets(
        now,
        now_plus_twenty_five_hours,
        location,
        location_at_now,
        data,
        planets,
        apparent_magnitude_maximum ):

        earth = AstroSkyfield._EPHEMERIS_PLANETS[ AstroSkyfield._PLANET_EARTH ]
        earth_at_now = earth.at( now )
        for planet_name in planets:
            index_planet = AstroSkyfield._PLANET_MAPPINGS[ planet_name ]
            planet = AstroSkyfield._EPHEMERIS_PLANETS[ index_planet ]
            apparent_magnitude = (
                planetary_magnitude( earth_at_now.observe( planet ) ) )

            is_saturn_bad_apparent_magnitude = (
                planet_name == AstroBase.PLANET_SATURN
                and
                math.isnan( apparent_magnitude ) )

            if is_saturn_bad_apparent_magnitude:
                # Saturn can return NaN; set the mean apparent magnitude.
                apparent_magnitude = 0.46 # Refer to Wikipedia!

            if apparent_magnitude <= apparent_magnitude_maximum:
                AstroSkyfield._calculate_common(
                    now,
                    now_plus_twenty_five_hours,
                    location,
                    location_at_now,
                    data,
                    ( AstroBase.BodyType.PLANET, planet_name ),
                    planet )


    @staticmethod
    def _calculate_stars(
        now,
        now_plus_twenty_five_hours,
        location,
        location_at_now,
        data,
        stars,
        apparent_magnitude_maximum ):

        for star in stars:
            hip = AstroBase.get_star_hip( star )
            star_ = AstroSkyfield._EPHEMERIS_STARS.loc[ hip ]
            if star_.magnitude <= apparent_magnitude_maximum:
                AstroSkyfield._calculate_common(
                    now,
                    now_plus_twenty_five_hours,
                    location,
                    location_at_now,
                    data,
                    ( AstroBase.BodyType.STAR, star ),
                    Star.from_dataframe( star_ ) )


#TODO Issue logged with regard to slow speed of processing comets / minor planets:
# https://github.com/skyfielders/python-skyfield/issues/490
# https://github.com/skyfielders/python-skyfield/pull/532
# https://github.com/skyfielders/python-skyfield/pull/526
    @staticmethod
    def _calculate_comets(
        now,
        timescale,
        location,
        location_at_now,
        data,
        comets,
        orbital_element_data,
        apparent_magnitude_maximum ):

        with io.BytesIO() as f:
            for key in comets:
                if key in orbital_element_data:
                    line = orbital_element_data[ key ].get_data() + '\n'
                    f.write( line.encode() )

            f.seek( 0 )

            dataframe = mpc.load_comets_dataframe( f )

        dataframe = dataframe.set_index( "designation", drop = False )

        sun = AstroSkyfield._EPHEMERIS_PLANETS[ AstroSkyfield._SUN ]
        sun_at_now = sun.at( now )

        # Found that using 25 hours throws a ValueError, so using 48.
        # https://github.com/skyfielders/python-skyfield/issues/959
        now_plus_forty_eight_hours = now + datetime.timedelta( hours = 48 )

        for name, row in dataframe.iterrows():
            key = ( AstroBase.BodyType.COMET, name.upper() )
            body = (
                sun
                +
                mpc.comet_orbit(
                    row,
                    timescale,
                    constants.GM_SUN_Pitjeva_2005_km3_s2 ) )

            ra, dec, earth_body_distance = location_at_now.observe( body ).radec()
            ra, dec, sun_body_distance = sun_at_now.observe( body ).radec()

            # According to MPC, always use the gk model.
            #   https://github.com/skyfielders/python-skyfield/issues/416
            apparent_magnitude = (
                AstroBase.get_apparent_magnitude_gk(
                    row[ "magnitude_g" ], row[ "magnitude_k" ],
                    earth_body_distance.au, sun_body_distance.au ) )

            if apparent_magnitude < apparent_magnitude_maximum:
                AstroSkyfield._calculate_common(
                    now, now_plus_forty_eight_hours,
                    location, location_at_now,
                    data, key, body )


#TODO Issue logged with regard to slow speed of processing comets / minor planets:
# https://github.com/skyfielders/python-skyfield/issues/490
# https://github.com/skyfielders/python-skyfield/pull/532
# https://github.com/skyfielders/python-skyfield/pull/526
    @staticmethod
    def _calculate_minor_planets(
        now,
        timescale,
        location,
        location_at_now,
        data,
        minor_planets,
        orbital_element_data,
        apparent_magnitude_maximum,
        apparent_magnitude_data ):

        with io.BytesIO() as f:
            for key in minor_planets:
                orbital_element_present = key in orbital_element_data
                apparent_magnitude_present = key in apparent_magnitude_data
                if orbital_element_present and apparent_magnitude_present:
                    apparent_magnitude = (
                        float( apparent_magnitude_data[ key ].get_apparent_magnitude() ) )

                    if apparent_magnitude <= apparent_magnitude_maximum:
                        line = orbital_element_data[ key ].get_data() + '\n'
                        f.write( line.encode() )

            f.seek( 0 )
            dataframe = mpc.load_mpcorb_dataframe( f )

        dataframe = dataframe.set_index( "designation", drop = False )
        sun = AstroSkyfield._EPHEMERIS_PLANETS[ AstroSkyfield._SUN ]
        for name, row in dataframe.iterrows():
            key = ( AstroBase.BodyType.MINOR_PLANET, name.upper() )
            body = (
                sun
                +
                mpc.mpcorb_orbit(
                    row,
                    timescale,
                    constants.GM_SUN_Pitjeva_2005_km3_s2 ) )

            # Found that using 25 hours throws a ValueError, so using 48.
            # https://github.com/skyfielders/python-skyfield/issues/959
            now_plus_forty_eight_hours = now + datetime.timedelta( hours = 48 )
            AstroSkyfield._calculate_common(
                now,
                now_plus_forty_eight_hours,
                location,
                location_at_now,
                data,
                key,
                body )


    @staticmethod
    def _calculate_common(
        now,
        now_plus_whatever,
        location,
        location_at_now,
        data,
        key,
        body ):

        never_up = False

        # https://rhodesmill.org/skyfield/almanac.html#risings-and-settings
        rise_date_time, rises = (
            almanac.find_risings( location, body, now, now_plus_whatever ) )

        set_date_time, sets = (
            almanac.find_settings( location, body, now, now_plus_whatever ) )

        if rises.item( 0 ) and sets.item( 0 ): # Rises and sets.
            data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = (
                rise_date_time[ 0 ].utc_datetime() )

            data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = (
                set_date_time[ 0 ].utc_datetime() )

            alt, az, earth_body_distance = (
                location_at_now.observe( body ).apparent().altaz() )

            data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
            data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

        elif not sets.item( 0 ): # Never sets (always up).
            alt, az, earth_body_distance = (
                location_at_now.observe( body ).apparent().altaz() )

            data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
            data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

        else: # not rises.item( 0 )
            # Never rises (never up).
            # It is impossible to be never up AND always up.
            never_up = True

        return never_up


#TODO Read
#    https://rhodesmill.org/skyfield/earth-satellites.html
# and ensure the code below follows the example as best practise.
    # References:
    #    https://github.com/skyfielders/python-skyfield/issues/327
    #    https://github.com/skyfielders/python-skyfield/issues/558
    @staticmethod
    def _calculate_satellites(
        now,
        timescale,
        latitude_longitude_elevation,
        data,
        satellites,
        satellite_data,
        start_hour_as_date_time_in_utc,
        end_hour_as_date_time_in_utc ):

        end = (
            now
            +
            datetime.timedelta(
                hours = AstroBase.SATELLITE_SEARCH_DURATION_HOURS ) )

        windows = (
            AstroBase.get_start_end_windows(
                now.utc_datetime(),
                end.utc_datetime(),
                start_hour_as_date_time_in_utc,
                end_hour_as_date_time_in_utc ) )

        is_twilight_function = (
            almanac.dark_twilight_day(
                AstroSkyfield._EPHEMERIS_PLANETS,
                latitude_longitude_elevation ) )

        for satellite in satellites:
            if satellite in satellite_data:
                key = ( AstroBase.BodyType.SATELLITE, satellite )
                earth_satellite = (
                    EarthSatellite.from_satrec(
                        satellite_data[ satellite ].get_satellite_record(),
                        timescale ) )

                for start_date_time, end_date_time in windows:
                    found_pass = (
                        AstroSkyfield._calculate_satellite(
                            timescale.from_datetime( start_date_time ),
                            timescale.from_datetime( end_date_time ),
                            timescale,
                            latitude_longitude_elevation,
                            data,
                            key,
                            earth_satellite,
                            is_twilight_function ) )

                    if found_pass:
                        break


    @staticmethod
    def _calculate_satellite(
        start_date_time,
        end_date_time,
        timescale,
        latitude_longitude_elevation,
        data,
        key,
        earth_satellite,
        is_twilight_function ):

        found_pass = False
        rise_date_time = None

        # Culminate may occur more than once, so collect them all.
        culmination_date_times = [ ]

        date_times, events = (
            earth_satellite.find_events(
                latitude_longitude_elevation,
                start_date_time,
                end_date_time,
                altitude_degrees = 20.0 ) )

        for date_time, event in zip( date_times, events ):
            if event == 0: # Satellite rose above altitude_degrees.
                rise_date_time = date_time

            elif event == 1: # Satellite culminated and started to descend.
                culmination_date_times.append( date_time )

            else: # Satellite fell below altitude_degrees.
                have_rise_and_culminations = (
                    rise_date_time is not None and culmination_date_times )

                if have_rise_and_culminations:
                    pass_is_visible = (
                        AstroSkyfield._is_satellite_pass_visible(
                            timescale,
                            rise_date_time,
                            date_time,
                            is_twilight_function,
                            earth_satellite ) )

                    if pass_is_visible:
                        data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = (
                            rise_date_time.utc_datetime() )

                        alt, az, earth_satellite_distance = ( earth_satellite - latitude_longitude_elevation ).at( rise_date_time ).altaz()  #TODO Too long

                        data[ key + ( AstroBase.DATA_TAG_RISE_AZIMUTH, ) ] = (
                            str( az.radians ) )

                        data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = (
                            date_time.utc_datetime() )

                        alt, az, earth_satellite_distance = ( earth_satellite - latitude_longitude_elevation ).at( date_time ).altaz()  #TODO Too long
                        data[ key + ( AstroBase.DATA_TAG_SET_AZIMUTH, ) ] = (
                            str( az.radians ) )

                        found_pass = True
                        break

                rise_date_time = None
                culmination_date_times = [ ]

        return found_pass


    @staticmethod
    def _is_satellite_pass_visible(
        timescale,
        start_date_time,
        end_date_time,
        is_twilight_function,
        earth_satellite ):

        seconds_from_rise_to_set = ( end_date_time.utc_datetime() - start_date_time.utc_datetime() ).total_seconds() #TODO Too long
        range_start = math.ceil( start_date_time.utc.second )
        range_end = (
            math.ceil(
                start_date_time.utc.second + seconds_from_rise_to_set ) )

        # Set a step interval of 60 seconds.
        range_step = max( math.ceil( seconds_from_rise_to_set / 60.0 ), 1.0 )

        transit_range = (
            timescale.utc(
                start_date_time.utc.year,
                start_date_time.utc.month,
                start_date_time.utc.day,
                start_date_time.utc.hour,
                start_date_time.utc.minute,
                range( range_start, range_end, range_step ) ) )

        # almanac.TWILIGHTS[ 1 ], Astronomical twilight
        is_twilight_astronomical = is_twilight_function( transit_range ) == 1

        # almanac.TWILIGHTS[ 2 ], Nautical twilight
        is_twilight_nautical = is_twilight_function( transit_range ) == 2

        is_sunlit = (
            earth_satellite.at( transit_range ).is_sunlit(
                AstroSkyfield._EPHEMERIS_PLANETS ) )

        is_visible = False
        z = zip( is_twilight_astronomical, is_twilight_nautical, is_sunlit )
        for twilight_astronomical, twilight_nautical, sunlit in z:
            if sunlit and ( twilight_astronomical or twilight_nautical ):
                is_visible = True
                break

        return is_visible
