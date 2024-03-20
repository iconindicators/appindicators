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


# Base class for calculating astronomical information.


# References:
#    https://ssd.jpl.nasa.gov/horizons.cgi
#    https://stellarium-web.org/
#    https://theskylive.com/
#    https://www.wolframalpha.com
#    https://www.ga.gov.au/scientific-topics/astronomical
#    https://futureboy.us/fsp/moon.fsp
#    https://futureboy.us/fsp/sun.fsp
#    https://www.satellite-calculations.com/
#    https://aa.usno.navy.mil/data/docs/mrst.php
#    https://celestrak.org/columns/v03n01
#    https://celestrak.org/NORAD/elements
#    https://www.n2yo.com
#    https://www.heavens-above.com
#    https://in-the-sky.org
#    https://uphere.space
#    https://www.amsat.org/track
#    https://tracksat.space


import datetime
import math

from abc import ABC, abstractmethod
from enum import Enum


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


    # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
    DATA_TAGS_TRANSLATIONS = {
        DATA_TAG_ALTITUDE           : _( "ALTITUDE" ),
        DATA_TAG_AZIMUTH            : _( "AZIMUTH" ),
        DATA_TAG_BRIGHT_LIMB        : _( "BRIGHT LIMB" ),
        DATA_TAG_ECLIPSE_DATE_TIME  : _( "ECLIPSE DATE TIME" ),
        DATA_TAG_ECLIPSE_LATITUDE   : _( "ECLIPSE LATITUDE" ),
        DATA_TAG_ECLIPSE_LONGITUDE  : _( "ECLIPSE LONGITUDE" ),
        DATA_TAG_ECLIPSE_TYPE       : _( "ECLIPSE TYPE" ),
        DATA_TAG_EQUINOX            : _( "EQUINOX" ),
        DATA_TAG_FIRST_QUARTER      : _( "FIRST QUARTER" ),
        DATA_TAG_ILLUMINATION       : _( "ILLUMINATION" ),
        DATA_TAG_FULL               : _( "FULL" ),
        DATA_TAG_NEW                : _( "NEW" ),
        DATA_TAG_PHASE              : _( "PHASE" ),
        DATA_TAG_RISE_AZIMUTH       : _( "RISE AZIMUTH" ),
        DATA_TAG_RISE_DATE_TIME     : _( "RISE DATE TIME" ),
        DATA_TAG_SET_AZIMUTH        : _( "SET AZIMUTH" ),
        DATA_TAG_SET_DATE_TIME      : _( "SET DATE TIME" ),
        DATA_TAG_SOLSTICE           : _( "SOLSTICE" ),
        DATA_TAG_THIRD_QUARTER      : _( "THIRD QUARTER" ) }


    # Data tags of attributes for each of the body types.
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

    PLANETS = [ PLANET_MERCURY, PLANET_VENUS, PLANET_MARS, PLANET_JUPITER, PLANET_SATURN, PLANET_URANUS, PLANET_NEPTUNE ]

    PLANET_NAMES_TRANSLATIONS = {
        PLANET_MERCURY  : _( "Mercury" ),
        PLANET_VENUS    : _( "Venus" ),
        PLANET_MARS     : _( "Mars" ),
        PLANET_JUPITER  : _( "Jupiter" ),
        PLANET_SATURN   : _( "Saturn" ),
        PLANET_URANUS   : _( "Uranus" ),
        PLANET_NEPTUNE  : _( "Neptune" ) }

    # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
    PLANET_TAGS_TRANSLATIONS = {
        PLANET_MERCURY  : _( "MERCURY" ),
        PLANET_VENUS    : _( "VENUS" ),
        PLANET_MARS     : _( "MARS" ),
        PLANET_JUPITER  : _( "JUPITER" ),
        PLANET_SATURN   : _( "SATURN" ),
        PLANET_URANUS   : _( "URANUS" ),
        PLANET_NEPTUNE  : _( "NEPTUNE" ) }


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


    __STARS_INDEX_NAME = 0
    __STARS_INDEX_HIP = 1
    __STARS_INDEX_NAME_TRANSLATION = 2
    __STARS_INDEX_TAG_TRANSLATION = 3


    # PyEphem provides a list of stars and data, whereas Skyfield does not.
    # Over the years, the PyEphem stars has accumulated duplicates and misspellings,
    # which must be kept for backward compatibility.
    #
    # Several possibilities are available for creating a new list of stars...
    #
    #    http://fer3.com/arc/imgx/Bowditch-American-Practical-Navigator-2002-(2004).pdf
    #    https://en.wikipedia.org/wiki/List_of_stars_for_navigation
    #        Contains a list of around 58 navigational stars.
    #        Unknown if this is northern hemisphere centric as the source is American.
    #        PyEphem contains all these stars.
    #
    #    http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt
    #        Contains official names and corresponding HIPs.
    #        Unfortunately too many stars, resulting in updating too frequently
    #        and there is no easy/obvious way to cull to a manageable size.
    #
    #    https://www.cosmos.esa.int/web/hipparcos/common-star-names
    #        Contains around 96 stars, with some names misspelt.
    #        Not all stars in PyEphem are present in this list.
    #
    # Ultimately, start with PyEphem's list of stars and drop those which are not
    # listed in the IAU CSN Catalog.
    #
    # DO NOT EDIT: Content must be created using 'createephemerisstars.py'.
    STARS = [
        [ "ACAMAR",            13847,  _( "Acamar" ),            _( "ACAMAR" ) ],
        [ "ACHERNAR",          7588,   _( "Achernar" ),          _( "ACHERNAR" ) ],
        [ "ACRUX",             60718,  _( "Acrux" ),             _( "ACRUX" ) ],
        [ "ADHARA",            33579,  _( "Adhara" ),            _( "ADHARA" ) ],
        [ "ALCOR",             65477,  _( "Alcor" ),             _( "ALCOR" ) ],
        [ "ALCYONE",           17702,  _( "Alcyone" ),           _( "ALCYONE" ) ],
        [ "ALDEBARAN",         21421,  _( "Aldebaran" ),         _( "ALDEBARAN" ) ],
        [ "ALDERAMIN",         105199, _( "Alderamin" ),         _( "ALDERAMIN" ) ],
        [ "ALFIRK",            106032, _( "Alfirk" ),            _( "ALFIRK" ) ],
        [ "ALGENIB",           1067,   _( "Algenib" ),           _( "ALGENIB" ) ],
        [ "ALGIEBA",           50583,  _( "Algieba" ),           _( "ALGIEBA" ) ],
        [ "ALGOL",             14576,  _( "Algol" ),             _( "ALGOL" ) ],
        [ "ALHENA",            31681,  _( "Alhena" ),            _( "ALHENA" ) ],
        [ "ALIOTH",            62956,  _( "Alioth" ),            _( "ALIOTH" ) ],
        [ "ALKAID",            67301,  _( "Alkaid" ),            _( "ALKAID" ) ],
        [ "ALMACH",            9640,   _( "Almach" ),            _( "ALMACH" ) ],
        [ "ALNAIR",            109268, _( "Alnair" ),            _( "ALNAIR" ) ],
        [ "ALNILAM",           26311,  _( "Alnilam" ),           _( "ALNILAM" ) ],
        [ "ALNITAK",           26727,  _( "Alnitak" ),           _( "ALNITAK" ) ],
        [ "ALPHARD",           46390,  _( "Alphard" ),           _( "ALPHARD" ) ],
        [ "ALPHECCA",          76267,  _( "Alphecca" ),          _( "ALPHECCA" ) ],
        [ "ALPHERATZ",         677,    _( "Alpheratz" ),         _( "ALPHERATZ" ) ],
        [ "ALSHAIN",           98036,  _( "Alshain" ),           _( "ALSHAIN" ) ],
        [ "ALTAIR",            97649,  _( "Altair" ),            _( "ALTAIR" ) ],
        [ "ANKAA",             2081,   _( "Ankaa" ),             _( "ANKAA" ) ],
        [ "ANTARES",           80763,  _( "Antares" ),           _( "ANTARES" ) ],
        [ "ARCTURUS",          69673,  _( "Arcturus" ),          _( "ARCTURUS" ) ],
        [ "ARKAB POSTERIOR",   95294,  _( "Arkab Posterior" ),   _( "ARKAB POSTERIOR" ) ],
        [ "ARKAB PRIOR",       95241,  _( "Arkab Prior" ),       _( "ARKAB PRIOR" ) ],
        [ "ARNEB",             25985,  _( "Arneb" ),             _( "ARNEB" ) ],
        [ "ATLAS",             17847,  _( "Atlas" ),             _( "ATLAS" ) ],
        [ "ATRIA",             82273,  _( "Atria" ),             _( "ATRIA" ) ],
        [ "AVIOR",             41037,  _( "Avior" ),             _( "AVIOR" ) ],
        [ "BELLATRIX",         25336,  _( "Bellatrix" ),         _( "BELLATRIX" ) ],
        [ "BETELGEUSE",        27989,  _( "Betelgeuse" ),        _( "BETELGEUSE" ) ],
        [ "CANOPUS",           30438,  _( "Canopus" ),           _( "CANOPUS" ) ],
        [ "CAPELLA",           24608,  _( "Capella" ),           _( "CAPELLA" ) ],
        [ "CAPH",              746,    _( "Caph" ),              _( "CAPH" ) ],
        [ "CASTOR",            36850,  _( "Castor" ),            _( "CASTOR" ) ],
        [ "CEBALRAI",          86742,  _( "Cebalrai" ),          _( "CEBALRAI" ) ],
        [ "DENEB",             102098, _( "Deneb" ),             _( "DENEB" ) ],
        [ "DENEBOLA",          57632,  _( "Denebola" ),          _( "DENEBOLA" ) ],
        [ "DIPHDA",            3419,   _( "Diphda" ),            _( "DIPHDA" ) ],
        [ "DUBHE",             54061,  _( "Dubhe" ),             _( "DUBHE" ) ],
        [ "ELECTRA",           17499,  _( "Electra" ),           _( "ELECTRA" ) ],
        [ "ELNATH",            25428,  _( "Elnath" ),            _( "ELNATH" ) ],
        [ "ELTANIN",           87833,  _( "Eltanin" ),           _( "ELTANIN" ) ],
        [ "ENIF",              107315, _( "Enif" ),              _( "ENIF" ) ],
        [ "FOMALHAUT",         113368, _( "Fomalhaut" ),         _( "FOMALHAUT" ) ],
        [ "GACRUX",            61084,  _( "Gacrux" ),            _( "GACRUX" ) ],
        [ "GIENAH",            59803,  _( "Gienah" ),            _( "GIENAH" ) ],
        [ "HADAR",             68702,  _( "Hadar" ),             _( "HADAR" ) ],
        [ "HAMAL",             9884,   _( "Hamal" ),             _( "HAMAL" ) ],
        [ "IZAR",              72105,  _( "Izar" ),              _( "IZAR" ) ],
        [ "KAUS AUSTRALIS",    90185,  _( "Kaus Australis" ),    _( "KAUS AUSTRALIS" ) ],
        [ "KOCHAB",            72607,  _( "Kochab" ),            _( "KOCHAB" ) ],
        [ "MAIA",              17573,  _( "Maia" ),              _( "MAIA" ) ],
        [ "MARKAB",            113963, _( "Markab" ),            _( "MARKAB" ) ],
        [ "MEGREZ",            59774,  _( "Megrez" ),            _( "MEGREZ" ) ],
        [ "MENKALINAN",        28360,  _( "Menkalinan" ),        _( "MENKALINAN" ) ],
        [ "MENKAR",            14135,  _( "Menkar" ),            _( "MENKAR" ) ],
        [ "MENKENT",           68933,  _( "Menkent" ),           _( "MENKENT" ) ],
        [ "MERAK",             53910,  _( "Merak" ),             _( "MERAK" ) ],
        [ "MEROPE",            17608,  _( "Merope" ),            _( "MEROPE" ) ],
        [ "MIAPLACIDUS",       45238,  _( "Miaplacidus" ),       _( "MIAPLACIDUS" ) ],
        [ "MIMOSA",            62434,  _( "Mimosa" ),            _( "MIMOSA" ) ],
        [ "MINTAKA",           25930,  _( "Mintaka" ),           _( "MINTAKA" ) ],
        [ "MIRACH",            5447,   _( "Mirach" ),            _( "MIRACH" ) ],
        [ "MIRFAK",            15863,  _( "Mirfak" ),            _( "MIRFAK" ) ],
        [ "MIRZAM",            30324,  _( "Mirzam" ),            _( "MIRZAM" ) ],
        [ "MIZAR",             65378,  _( "Mizar" ),             _( "MIZAR" ) ],
        [ "NAOS",              39429,  _( "Naos" ),              _( "NAOS" ) ],
        [ "NIHAL",             25606,  _( "Nihal" ),             _( "NIHAL" ) ],
        [ "NUNKI",             92855,  _( "Nunki" ),             _( "NUNKI" ) ],
        [ "PEACOCK",           100751, _( "Peacock" ),           _( "PEACOCK" ) ],
        [ "PHECDA",            58001,  _( "Phecda" ),            _( "PHECDA" ) ],
        [ "POLARIS",           11767,  _( "Polaris" ),           _( "POLARIS" ) ],
        [ "POLLUX",            37826,  _( "Pollux" ),            _( "POLLUX" ) ],
        [ "PROCYON",           37279,  _( "Procyon" ),           _( "PROCYON" ) ],
        [ "RASALGETHI",        84345,  _( "Rasalgethi" ),        _( "RASALGETHI" ) ],
        [ "RASALHAGUE",        86032,  _( "Rasalhague" ),        _( "RASALHAGUE" ) ],
        [ "REGULUS",           49669,  _( "Regulus" ),           _( "REGULUS" ) ],
        [ "RIGEL",             24436,  _( "Rigel" ),             _( "RIGEL" ) ],
        [ "RIGIL KENTAURUS",   71683,  _( "Rigil Kentaurus" ),   _( "RIGIL KENTAURUS" ) ],
        [ "RUKBAT",            95347,  _( "Rukbat" ),            _( "RUKBAT" ) ],
        [ "SABIK",             84012,  _( "Sabik" ),             _( "SABIK" ) ],
        [ "SADALMELIK",        109074, _( "Sadalmelik" ),        _( "SADALMELIK" ) ],
        [ "SADR",              100453, _( "Sadr" ),              _( "SADR" ) ],
        [ "SAIPH",             27366,  _( "Saiph" ),             _( "SAIPH" ) ],
        [ "SCHEAT",            113881, _( "Scheat" ),            _( "SCHEAT" ) ],
        [ "SCHEDAR",           3179,   _( "Schedar" ),           _( "SCHEDAR" ) ],
        [ "SHAULA",            85927,  _( "Shaula" ),            _( "SHAULA" ) ],
        [ "SHELIAK",           92420,  _( "Sheliak" ),           _( "SHELIAK" ) ],
        [ "SIRIUS",            32349,  _( "Sirius" ),            _( "SIRIUS" ) ],
        [ "SPICA",             65474,  _( "Spica" ),             _( "SPICA" ) ],
        [ "SUHAIL",            44816,  _( "Suhail" ),            _( "SUHAIL" ) ],
        [ "SULAFAT",           93194,  _( "Sulafat" ),           _( "SULAFAT" ) ],
        [ "TARAZED",           97278,  _( "Tarazed" ),           _( "TARAZED" ) ],
        [ "TAYGETA",           17531,  _( "Taygeta" ),           _( "TAYGETA" ) ],
        [ "THUBAN",            68756,  _( "Thuban" ),            _( "THUBAN" ) ],
        [ "UNUKALHAI",         77070,  _( "Unukalhai" ),         _( "UNUKALHAI" ) ],
        [ "VEGA",              91262,  _( "Vega" ),              _( "VEGA" ) ],
        [ "VINDEMIATRIX",      63608,  _( "Vindemiatrix" ),      _( "VINDEMIATRIX" ) ],
        [ "WEZEN",             34444,  _( "Wezen" ),             _( "WEZEN" ) ],
        [ "ZAURAK",            18543,  _( "Zaurak" ),            _( "ZAURAK" ) ],
        [ "ZUBENELGENUBI",     72622,  _( "Zubenelgenubi" ),     _( "ZUBENELGENUBI" ) ] ]


    SATELLITE_SEARCH_DURATION_HOURS = 75 # Number of hours to search from 'now' for visible satellite passes.

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
    MAGNITUDE_MAXIMUM = 15.0 # No point going any higher for the typical home astronomer.
    MAGNITUDE_MINIMUM = -10.0 # Have found (erroneous) magnitudes in comet OE data which are brighter than the sun, so set a lower limit.


    # Returns a dictionary with astronomical information:
    #     Key is a tuple of a BodyType, a name tag and a data tag.
    #     Value is the calculated astronomical information as a string.
    #
    # Latitude, longitude are floating point numbers representing decimal degrees.
    # Elevation is a floating point number representing metres above sea level.
    # Maximum magnitude applies to planets, stars, comets and minor planets.
    #
    # If a body is never up, no data is added.
    # If a body is always up, the current azimuth/altitude are added.
    # If the body will rise/set, the next rise date/time, next set date/time and current azimuth/altitude are added.
    # For satellites, a satellite which is yet to rise or in transit will have the rise and set date/time and azimuth/altitude.
    # For a polar satellite, only the azimuth/altitude is added.
    #
    # NOTE: Any error when computing a body no result is added for that body.
    @staticmethod
    @abstractmethod
    def calculate(
            utcNow,
            latitude, longitude, elevation,
            planets,
            stars,
            satellites, satelliteData, startHourAsDateTimeInUTC, endHourAsDateTimeInUTC,
            comets, cometData, cometApparentMagnitudeData,
            minorPlanets, minorPlanetData, minorPlanetApparentMagnitudeData,
            apparentMagnitudeMaximum,
            logging = None ):
        return { }


    # Return a list of cities, sorted alphabetically, sensitive to locale.
    @staticmethod
    @abstractmethod
    def getCities():
        return [ ]


    # Returns a string specifying third party credit; otherwise an empty string.
    # Format is a credit string followed by an optional URL.
    @staticmethod
    @abstractmethod
    def getCredit():
        return ""


    # Returns a tuple of floats of the latitude, longitude and elevation for the city.
    @staticmethod
    @abstractmethod
    def getLatitudeLongitudeElevation( city ):
        return 0.0, 0.0, 0.0


    # Returns the version of the underlying astronomical library.
    @staticmethod
    @abstractmethod
    def getVersion():
        return None


    @staticmethod
    def __getStarRow( star ):
        return next( i for i in AstroBase.STARS if i[ AstroBase.__STARS_INDEX_NAME ] == star )


    @staticmethod
    def getStarHIP( star ):
        return AstroBase.__getStarRow( star )[ AstroBase.__STARS_INDEX_HIP ]


    @staticmethod
    def getStarNameTranslation( star ):
        return AstroBase.__getStarRow( star )[ AstroBase.__STARS_INDEX_NAME_TRANSLATION ]


    @staticmethod
    def getStarTagTranslation( star ):
        return AstroBase.__getStarRow( star )[ AstroBase.__STARS_INDEX_TAG_TRANSLATION ]


    @staticmethod
    def getStarNames():
        return [ i[ AstroBase.__STARS_INDEX_NAME ] for i in AstroBase.STARS ]


    @staticmethod
    def getStarHIPs():
        return [ i[ AstroBase.__STARS_INDEX_HIP ] for i in AstroBase.STARS ]


    @staticmethod
    def getStarTagTranslations():
        return [ i[ AstroBase.__STARS_INDEX_TAG_TRANSLATION ] for i in AstroBase.STARS ]


    # Calculate apparent magnitude.
    #
    # May throw a value error or similar if bad numbers/calculations occur.
    #
    # https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId564354
    @staticmethod
    def getApparentMagnitude_gk( g_absoluteMagnitude, k_luminosityIndex, bodyEarthDistanceAU, bodySunDistanceAU ):
        return \
            g_absoluteMagnitude + \
            5 * math.log10( bodyEarthDistanceAU ) + \
            2.5 * k_luminosityIndex * math.log10( bodySunDistanceAU )


    # Calculate apparent magnitude.
    #
    # May throw a value error or similar if bad numbers/calculations occur.
    #
    # https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId564354
    # https://www.britastro.org/asteroids/dymock4.pdf
    @staticmethod
    def getApparentMagnitude_HG( H_absoluteMagnitude, G_slope, bodyEarthDistanceAU, bodySunDistanceAU, earthSunDistanceAU ):
        # The division may result in a number greater than 1 in the fifth or sixth decimal place
        # and when the arccos is executed, throws:
        #
        #    'ValueError: math domain error'
        #
        # A solution posted in
        #
        #    https://math.stackexchange.com/questions/4060964/floating-point-division-resulting-in-a-value-exceeding-1-but-should-be-equal-to
        #
        # suggests setting an upper bound to the division with a value +/- 1.0.
        # However, the subsequent value for beta is zero and feeding into tan( 0 ) yields zero and the immediate logarithm is undefined!
        # Not really sure what can be done, or should be done;
        # leave things as they are and the caller can catch the error/exception.
        numerator = \
            bodySunDistanceAU * bodySunDistanceAU + \
            bodyEarthDistanceAU * bodyEarthDistanceAU - \
            earthSunDistanceAU * earthSunDistanceAU

        denominator = 2 * bodySunDistanceAU * bodyEarthDistanceAU
        beta = math.acos( numerator / denominator )

        psi_t = math.exp( math.log( math.tan( beta / 2.0 ) ) * 0.63 )
        Psi_1 = math.exp( -3.33 * psi_t )
        psi_t = math.exp( math.log( math.tan( beta / 2.0 ) ) * 1.22 )
        Psi_2 = math.exp( -1.87 * psi_t )

        apparentMagnitude = \
            H_absoluteMagnitude + \
            5.0 * math.log10( bodySunDistanceAU * bodyEarthDistanceAU ) - \
            2.5 * math.log10( ( 1 - G_slope ) * Psi_1 + G_slope * Psi_2 )

        return apparentMagnitude


    # Get the lunar phase.
    #
    #    illuminationPercentage The brightness from 0 to 100 inclusive.
    #    nextFullMoonDate The date of the next full moon.
    #    nextNewMoonDate The date of the next new moon.
    @staticmethod
    def getLunarPhase( illuminationPercentage, nextFullMoonDate, nextNewMoonDate ):
        if illuminationPercentage >= 99:
            phase = AstroBase.LUNAR_PHASE_FULL_MOON

        elif illuminationPercentage <= 1:
            phase = AstroBase.LUNAR_PHASE_NEW_MOON

        else: # 1 < illuminationPercentage < 99
            betweenNewAndFull = nextNewMoonDate > nextFullMoonDate
            if illuminationPercentage > 51:
                if betweenNewAndFull:
                    phase = AstroBase.LUNAR_PHASE_WAXING_GIBBOUS
                else:
                    phase = AstroBase.LUNAR_PHASE_WANING_GIBBOUS

            elif illuminationPercentage < 49:
                if betweenNewAndFull:
                    phase = AstroBase.LUNAR_PHASE_WAXING_CRESCENT
                else:
                    phase = AstroBase.LUNAR_PHASE_WANING_CRESCENT

            else:
                if betweenNewAndFull:
                    phase = AstroBase.LUNAR_PHASE_FIRST_QUARTER
                else:
                    phase = AstroBase.LUNAR_PHASE_THIRD_QUARTER

        return phase


    # Compute the sidereal decimal time for the given longitude (in floating point radians).
    #
    # Reference:
    #  'Practical Astronomy with Your Calculator' by Peter Duffett-Smith.
    @staticmethod
    def getSiderealTime( utcNow, longitude ):
        # Find the Julian date.  Section 4 of the reference.
        # Assume the date is always later than 15th October, 1582.
        y = utcNow.year
        m = utcNow.month
        d = \
            utcNow.day + \
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
    # Measured in radians, counter clockwise from a positive y axis.
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
    def getZenithAngleOfBrightLimb( utcNow, sunRA, sunDec, bodyRA, bodyDec, observerLat, observerLon ):
        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
        y = math.cos( sunDec ) * math.sin( sunRA - bodyRA )
        x = math.sin( sunDec ) * math.cos( bodyDec ) - math.cos( sunDec ) * math.sin( bodyDec ) * math.cos( sunRA - bodyRA )
        positionAngleOfBrightLimb = math.atan2( y, x )

        # Multiply by 15 to convert from decimal time to decimal degrees; section 22 of Practical Astronomy with Your Calculator.
        localSiderealTime = math.radians( AstroBase.getSiderealTime( utcNow, observerLon ) * 15 )

        # Astronomical Algorithms by Jean Meeus, Second Edition, page 92.
        # https://tycho.usno.navy.mil/sidereal.html
        # http://www.wwu.edu/skywise/skymobile/skywatch.html
        # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
        hourAngle = localSiderealTime - bodyRA

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
        y = math.sin( hourAngle )
        x = math.tan( observerLat ) * math.cos( bodyDec ) - math.sin( bodyDec ) * math.cos( hourAngle )
        parallacticAngle = math.atan2( y, x )

        return ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi )


    # Take a start/end date/time in UTC to define a search window for a satellite transit
    # and determine where a given start/end hour will overlap.
    #
    # Used, for example, to limit satellite passes dusk.
    #
    # The start hour (as date/time in UTC) < end hour (as date/time UTC).
    @staticmethod
    def getStartEndWindows( startDateTime, endDateTime, startHourAsDateTime, endHourAsDateTime ):
        #   SH            EH
        #                 SH            EH
        #                               SH            EH
        #                                             SH            EH
        #                                                           SH            EH
        #                        X------------------------X
        #                 StartDateTime                   EndDateTime
        windows = [ ]

        current = startDateTime - datetime.timedelta( days = 1 )
        end = endDateTime + datetime.timedelta( days = 1 )

        while current < end:
            if startHourAsDateTime < startDateTime:
                if endHourAsDateTime < startDateTime:
                    pass

                else:
                    windows.append( [ startDateTime, endHourAsDateTime ] )

            else:
                if startHourAsDateTime < endDateTime:
                    if endHourAsDateTime < endDateTime:
                        windows.append( [ startHourAsDateTime, endHourAsDateTime ] )

                    else:
                        windows.append( [ startHourAsDateTime, endDateTime ] )

            current = current + datetime.timedelta( days = 1 )
            startHourAsDateTime = startHourAsDateTime + datetime.timedelta( days = 1 )
            endHourAsDateTime = endHourAsDateTime + datetime.timedelta( days = 1 )

        return windows


    # Retrieve a comet's designation from the full name,
    # from both MPC and XEphem formatted data files from
    # the Minor Planet Center or Comet Observation Database.
    #
    # https://minorplanetcenter.net//iau/lists/CometResolution.html
    # https://minorplanetcenter.net/iau/info/CometNamingGuidelines.html
    # http://www.icq.eps.harvard.edu/cometnames.html
    # https://en.wikipedia.org/wiki/Naming_of_comets
    # https://slate.com/technology/2013/11/comet-naming-a-quick-guide.html
    @staticmethod
    def getDesignationComet( name ):
        if name[ 0 ].isnumeric():
            # Examples:
                # 1P/Halley
                # 332P/Ikeya-Murakami
                # 332P-B/Ikeya-Murakami
                # 332P-C/Ikeya-Murakami
                # 1I/`Oumuamua
            slash = name.find( '/' )
            if slash == -1:
                # Special case for '282P' which is MPC format, whereas the XEphem format is '282P/'.
                designation = name

            else:
                dash = name[ 0 : slash ].find( '-' )
                if dash == -1:
                    designation = name[ 0 : slash ]

                else:
                    designation = name[ 0 : dash ]

        elif name[ 0 ].isalpha():
            # Examples:
                # C/1995 O1 (Hale-Bopp)
                # P/1998 VS24 (LINEAR)
                # P/2011 UA134 (Spacewatch-PANSTARRS)
                # A/2018 V3
                # C/2019 Y4-D (ATLAS)
            designation = ' '.join( name.split()[ 0 : 2 ] )

        else:
            designation = -1

        return designation


    # Retrieve a minor planet's designation from the full name,
    # from both MPC and XEphem formatted data files from the Minor Planet Center.
    #
    # https://www.iau.org/public/themes/naming/
    # https://minorplanetcenter.net/iau/info/DesDoc.html
    # https://minorplanetcenter.net/iau/info/PackedDes.html
    @staticmethod
    def getDesignationMinorPlanet( name ):
        # XEphem examples:                MPC examples:
        #     1 Ceres                         (1) Ceres
        #
        #     1915 1953 EA                    (1915)
        #
        #     944 Hidalgo                     (944) Hidalgo
        #     15788 1993 SB                   (15788)
        #     1993 RP                         1993 RP
        #
        #     433 Eros                        (433) Eros
        #     3102 Krok                       (3102) Krok
        #     7236 1987 PA                    (7236)
        #     1979 XB                         1979 XB
        #     3271 Ul                         (3271) Ul
        components = name.split()
        components[ 0 ] = components[ 0 ].strip( '(' ).strip( ')' )

        isProvisionalDesignation = \
            len( components ) == 2 and \
            len( components[ 0 ] ) == 4 and components[ 0 ].isnumeric() and \
            ( ( len( components[ 1 ] ) == 2 and components[ 1 ].isalpha() and components[ 1 ].isupper() ) or \
              ( len( components[ 1 ] ) > 2 and components[ 1 ][ 0 : 2 ].isalpha() and components[ 1 ][ 0 : 2 ].isupper() and components[ 1 ][ 2 : ].isnumeric() ) )

        if isProvisionalDesignation:
            designation = name

        else:
            designation = components[ 0 ]

        return designation
