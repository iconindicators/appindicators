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


# Base class for calculating astronomical information for use with Indicator Lunar.


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
#    https://www.celestrak.com/columns/v03n01
#    https://celestrak.com/NORAD/elements
#    https://www.n2yo.com
#    https://www.heavens-above.com
#    https://in-the-sky.org
#    https://uphere.space
#    https://www.amsat.org/track
#    https://tracksat.space


from abc import ABC, abstractmethod
from enum import Enum

import datetime, math


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


    # PyEphem provides a list of stars and data, whereas Skyfield does not.
    # Over the years, the PyEphem stars have contained duplicates and misspellings.
    #
    # Therefore, unify the stars from the ESA Hipparcos catalogue:
    #    https://www.cosmos.esa.int/web/hipparcos/common-star-names
    #
    # To create the star data, refer to createEphemerisStars.py
    #
    # Note that the star "3C 273" has been omitted from this list.
    # In creating the star data for PyEphem, the spectral type is missing for this star
    # implying the data cannot be created for PyEphem.
    STARS = [
        "ACAMAR",
        "ACHERNAR",
        "ACRUX",
        "ADHARA",
        "AGENA",
        "ALBIREO",
        "ALCOR",
        "ALCYONE",
        "ALDEBARAN",
        "ALDERAMIN",
        "ALGENIB",
        "ALGIEBA",
        "ALGOL",
        "ALHENA",
        "ALIOTH",
        "ALKAID",
        "ALMAAK",
        "ALNAIR",
        "ALNATH",
        "ALNILAM",
        "ALNITAK",
        "ALPHARD",
        "ALPHEKKA",
        "ALPHERATZ",
        "ALSHAIN",
        "ALTAIR",
        "ANKAA",
        "ANTARES",
        "ARCTURUS",
        "ARNEB",
        "BABCOCK'S STAR",
        "BARNARD'S STAR",
        "BELLATRIX",
        "BETELGEUSE",
        "CAMPBELL'S STAR",
        "CANOPUS",
        "CAPELLA",
        "CAPH",
        "CASTOR",
        "COR CAROLI",
        "CYG X-1",
        "DENEB",
        "DENEBOLA",
        "DIPHDA",
        "DUBHE",
        "ENIF",
        "ETAMIN",
        "FOMALHAUT",
        "GROOMBRIDGE 1830",
        "HADAR",
        "HAMAL",
        "IZAR",
        "KAPTEYN'S STAR",
        "KAUS AUSTRALIS",
        "KOCAB",
        "KRUGER 60",
        "LUYTEN'S STAR",
        "MARKAB",
        "MEGREZ",
        "MENKAR",
        "MERAK",
        "MINTAKA",
        "MIRA",
        "MIRACH",
        "MIRPHAK",
        "MIZAR",
        "NIHAL",
        "NUNKI",
        "PHAD",
        "PLEIONE",
        "POLARIS",
        "POLLUX",
        "PROCYON",
        "PROXIMA",
        "RASALGETHI",
        "RASALHAGUE",
        "RED RECTANGLE",
        "REGULUS",
        "RIGEL",
        "RIGIL KENT",
        "SADALMELIK",
        "SAIPH",
        "SCHEAT",
        "SHAULA",
        "SHEDIR",
        "SHELIAK",
        "SIRIUS",
        "SPICA",
        "TARAZED",
        "THUBAN",
        "UNUKALHAI",
        "VAN MAANEN 2",
        "VEGA",
        "VINDEMIATRIX",
        "ZAURAK" ]

    # Capitalised names of stars and associated HIP numbers.
    STARS_TO_HIP = {
        "ACAMAR"            :   13847,
        "ACHERNAR"          :   7588,
        "ACRUX"             :   60718,
        "ADHARA"            :   33579,
        "AGENA"             :   68702,
        "ALBIREO"           :   95947,
        "ALCOR"             :   65477,
        "ALCYONE"           :   17702,
        "ALDEBARAN"         :   21421,
        "ALDERAMIN"         :   105199,
        "ALGENIB"           :   1067,
        "ALGIEBA"           :   50583,
        "ALGOL"             :   14576,
        "ALHENA"            :   31681,
        "ALIOTH"            :   62956,
        "ALKAID"            :   67301,
        "ALMAAK"            :   9640,
        "ALNAIR"            :   109268,
        "ALNATH"            :   25428,
        "ALNILAM"           :   26311,
        "ALNITAK"           :   26727,
        "ALPHARD"           :   46390,
        "ALPHEKKA"          :   76267,
        "ALPHERATZ"         :   677,
        "ALSHAIN"           :   98036,
        "ALTAIR"            :   97649,
        "ANKAA"             :   2081,
        "ANTARES"           :   80763,
        "ARCTURUS"          :   69673,
        "ARNEB"             :   25985,
        "BABCOCK'S STAR"    :   112247,
        "BARNARD'S STAR"    :   87937,
        "BELLATRIX"         :   25336,
        "BETELGEUSE"        :   27989,
        "CAMPBELL'S STAR"   :   96295,
        "CANOPUS"           :   30438,
        "CAPELLA"           :   24608,
        "CAPH"              :   746,
        "CASTOR"            :   36850,
        "COR CAROLI"        :   63125,
        "CYG X-1"           :   98298,
        "DENEB"             :   102098,
        "DENEBOLA"          :   57632,
        "DIPHDA"            :   3419,
        "DUBHE"             :   54061,
        "ENIF"              :   107315,
        "ETAMIN"            :   87833,
        "FOMALHAUT"         :   113368,
        "GROOMBRIDGE 1830"  :   57939,
        "HADAR"             :   68702,
        "HAMAL"             :   9884,
        "IZAR"              :   72105,
        "KAPTEYN'S STAR"    :   24186,
        "KAUS AUSTRALIS"    :   90185,
        "KOCAB"             :   72607,
        "KRUGER 60"         :   110893,
        "LUYTEN'S STAR"     :   36208,
        "MARKAB"            :   113963,
        "MEGREZ"            :   59774,
        "MENKAR"            :   14135,
        "MERAK"             :   53910,
        "MINTAKA"           :   25930,
        "MIRA"              :   10826,
        "MIRACH"            :   5447,
        "MIRPHAK"           :   15863,
        "MIZAR"             :   65378,
        "NIHAL"             :   25606,
        "NUNKI"             :   92855,
        "PHAD"              :   58001,
        "PLEIONE"           :   17851,
        "POLARIS"           :   11767,
        "POLLUX"            :   37826,
        "PROCYON"           :   37279,
        "PROXIMA"           :   70890,
        "RASALGETHI"        :   84345,
        "RASALHAGUE"        :   86032,
        "RED RECTANGLE"     :   30089,
        "REGULUS"           :   49669,
        "RIGEL"             :   24436,
        "RIGIL KENT"        :   71683,
        "SADALMELIK"        :   109074,
        "SAIPH"             :   27366,
        "SCHEAT"            :   113881,
        "SHAULA"            :   85927,
        "SHEDIR"            :   3179,
        "SHELIAK"           :   92420,
        "SIRIUS"            :   32349,
        "SPICA"             :   65474,
        "TARAZED"           :   97278,
        "THUBAN"            :   68756,
        "UNUKALHAI"         :   77070,
        "VAN MAANEN 2"      :   3829,
        "VEGA"              :   91262,
        "VINDEMIATRIX"      :   63608,
        "ZAURAK"            :   18543 }

#TODO Do a build and make sure the translations come through.

    # Names of stars (from STARS) and associated English string encapsulated as _( "" ).
    STAR_NAMES_TRANSLATIONS = {
         STARS[ 0 ]  :   _( "Acamar" ),
         STARS[ 1 ]  :   _( "Achernar" ),
         STARS[ 2 ]  :   _( "Acrux" ),
         STARS[ 3 ]  :   _( "Adhara" ),
         STARS[ 4 ]  :   _( "Agena" ),
         STARS[ 5 ]  :   _( "Albireo" ),
         STARS[ 6 ]  :   _( "Alcor" ),
         STARS[ 7 ]  :   _( "Alcyone" ),
         STARS[ 8 ]  :   _( "Aldebaran" ),
         STARS[ 9 ]  :   _( "Alderamin" ),
         STARS[ 10 ] :   _( "Algenib" ),
         STARS[ 11 ] :   _( "Algieba" ),
         STARS[ 12 ] :   _( "Algol" ),
         STARS[ 13 ] :   _( "Alhena" ),
         STARS[ 14 ] :   _( "Alioth" ),
         STARS[ 15 ] :   _( "Alkaid" ),
         STARS[ 16 ] :   _( "Almaak" ),
         STARS[ 17 ] :   _( "Alnair" ),
         STARS[ 18 ] :   _( "Alnath" ),
         STARS[ 19 ] :   _( "Alnilam" ),
         STARS[ 20 ] :   _( "Alnitak" ),
         STARS[ 21 ] :   _( "Alphard" ),
         STARS[ 22 ] :   _( "Alphekka" ),
         STARS[ 23 ] :   _( "Alpheratz" ),
         STARS[ 24 ] :   _( "Alshain" ),
         STARS[ 25 ] :   _( "Altair" ),
         STARS[ 26 ] :   _( "Ankaa" ),
         STARS[ 27 ] :   _( "Antares" ),
         STARS[ 28 ] :   _( "Arcturus" ),
         STARS[ 29 ] :   _( "Arneb" ),
         STARS[ 30 ] :   _( "Babcock's Star" ),
         STARS[ 31 ] :   _( "Barnard's Star" ),
         STARS[ 32 ] :   _( "Bellatrix" ),
         STARS[ 33 ] :   _( "Betelgeuse" ),
         STARS[ 34 ] :   _( "Campbell's Star" ),
         STARS[ 35 ] :   _( "Canopus" ),
         STARS[ 36 ] :   _( "Capella" ),
         STARS[ 37 ] :   _( "Caph" ),
         STARS[ 38 ] :   _( "Castor" ),
         STARS[ 39 ] :   _( "Cor Caroli" ),
         STARS[ 40 ] :   _( "Cyg X-1" ),
         STARS[ 41 ] :   _( "Deneb" ),
         STARS[ 42 ] :   _( "Denebola" ),
         STARS[ 43 ] :   _( "Diphda" ),
         STARS[ 44 ] :   _( "Dubhe" ),
         STARS[ 45 ] :   _( "Enif" ),
         STARS[ 46 ] :   _( "Etamin" ),
         STARS[ 47 ] :   _( "Fomalhaut" ),
         STARS[ 48 ] :   _( "Groombridge 1830" ),
         STARS[ 49 ] :   _( "Hadar" ),
         STARS[ 50 ] :   _( "Hamal" ),
         STARS[ 51 ] :   _( "Izar" ),
         STARS[ 52 ] :   _( "Kapteyn's Star" ),
         STARS[ 53 ] :   _( "Kaus Australis" ),
         STARS[ 54 ] :   _( "Kocab" ),
         STARS[ 55 ] :   _( "Kruger 60" ),
         STARS[ 56 ] :   _( "Luyten's Star" ),
         STARS[ 57 ] :   _( "Markab" ),
         STARS[ 58 ] :   _( "Megrez" ),
         STARS[ 59 ] :   _( "Menkar" ),
         STARS[ 60 ] :   _( "Merak" ),
         STARS[ 61 ] :   _( "Mintaka" ),
         STARS[ 62 ] :   _( "Mira" ),
         STARS[ 63 ] :   _( "Mirach" ),
         STARS[ 64 ] :   _( "Mirphak" ),
         STARS[ 65 ] :   _( "Mizar" ),
         STARS[ 66 ] :   _( "Nihal" ),
         STARS[ 67 ] :   _( "Nunki" ),
         STARS[ 68 ] :   _( "Phad" ),
         STARS[ 69 ] :   _( "Pleione" ),
         STARS[ 70 ] :   _( "Polaris" ),
         STARS[ 71 ] :   _( "Pollux" ),
         STARS[ 72 ] :   _( "Procyon" ),
         STARS[ 73 ] :   _( "Proxima" ),
         STARS[ 74 ] :   _( "Rasalgethi" ),
         STARS[ 75 ] :   _( "Rasalhague" ),
         STARS[ 76 ] :   _( "Red Rectangle" ),
         STARS[ 77 ] :   _( "Regulus" ),
         STARS[ 78 ] :   _( "Rigel" ),
         STARS[ 79 ] :   _( "Rigil Kent" ),
         STARS[ 80 ] :   _( "Sadalmelik" ),
         STARS[ 81 ] :   _( "Saiph" ),
         STARS[ 82 ] :   _( "Scheat" ),
         STARS[ 83 ] :   _( "Shaula" ),
         STARS[ 84 ] :   _( "Shedir" ),
         STARS[ 85 ] :   _( "Sheliak" ),
         STARS[ 86 ] :   _( "Sirius" ),
         STARS[ 87 ] :   _( "Spica" ),
         STARS[ 88 ] :   _( "Tarazed" ),
         STARS[ 89 ] :   _( "Thuban" ),
         STARS[ 90 ] :   _( "Unukalhai" ),
         STARS[ 91 ] :   _( "Van Maanen 2" ),
         STARS[ 92 ] :   _( "Vega" ),
         STARS[ 93 ] :   _( "Vindemiatrix" ),
         STARS[ 94 ] :   _( "Zaurak" ) }

    # Names of stars (from STARS) and associated capitalised English string encapsulated as _( "" ).
    STAR_TAGS_TRANSLATIONS = {
         STARS[ 0 ]  :   _( "ACAMAR" ),
         STARS[ 1 ]  :   _( "ACHERNAR" ),
         STARS[ 2 ]  :   _( "ACRUX" ),
         STARS[ 3 ]  :   _( "ADHARA" ),
         STARS[ 4 ]  :   _( "AGENA" ),
         STARS[ 5 ]  :   _( "ALBIREO" ),
         STARS[ 6 ]  :   _( "ALCOR" ),
         STARS[ 7 ]  :   _( "ALCYONE" ),
         STARS[ 8 ]  :   _( "ALDEBARAN" ),
         STARS[ 9 ]  :   _( "ALDERAMIN" ),
         STARS[ 10 ] :   _( "ALGENIB" ),
         STARS[ 11 ] :   _( "ALGIEBA" ),
         STARS[ 12 ] :   _( "ALGOL" ),
         STARS[ 13 ] :   _( "ALHENA" ),
         STARS[ 14 ] :   _( "ALIOTH" ),
         STARS[ 15 ] :   _( "ALKAID" ),
         STARS[ 16 ] :   _( "ALMAAK" ),
         STARS[ 17 ] :   _( "ALNAIR" ),
         STARS[ 18 ] :   _( "ALNATH" ),
         STARS[ 19 ] :   _( "ALNILAM" ),
         STARS[ 20 ] :   _( "ALNITAK" ),
         STARS[ 21 ] :   _( "ALPHARD" ),
         STARS[ 22 ] :   _( "ALPHEKKA" ),
         STARS[ 23 ] :   _( "ALPHERATZ" ),
         STARS[ 24 ] :   _( "ALSHAIN" ),
         STARS[ 25 ] :   _( "ALTAIR" ),
         STARS[ 26 ] :   _( "ANKAA" ),
         STARS[ 27 ] :   _( "ANTARES" ),
         STARS[ 28 ] :   _( "ARCTURUS" ),
         STARS[ 29 ] :   _( "ARNEB" ),
         STARS[ 30 ] :   _( "BABCOCK'S STAR" ),
         STARS[ 31 ] :   _( "BARNARD'S STAR" ),
         STARS[ 32 ] :   _( "BELLATRIX" ),
         STARS[ 33 ] :   _( "BETELGEUSE" ),
         STARS[ 34 ] :   _( "CAMPBELL'S STAR" ),
         STARS[ 35 ] :   _( "CANOPUS" ),
         STARS[ 36 ] :   _( "CAPELLA" ),
         STARS[ 37 ] :   _( "CAPH" ),
         STARS[ 38 ] :   _( "CASTOR" ),
         STARS[ 39 ] :   _( "COR CAROLI" ),
         STARS[ 40 ] :   _( "CYG X-1" ),
         STARS[ 41 ] :   _( "DENEB" ),
         STARS[ 42 ] :   _( "DENEBOLA" ),
         STARS[ 43 ] :   _( "DIPHDA" ),
         STARS[ 44 ] :   _( "DUBHE" ),
         STARS[ 45 ] :   _( "ENIF" ),
         STARS[ 46 ] :   _( "ETAMIN" ),
         STARS[ 47 ] :   _( "FOMALHAUT" ),
         STARS[ 48 ] :   _( "GROOMBRIDGE 1830" ),
         STARS[ 49 ] :   _( "HADAR" ),
         STARS[ 50 ] :   _( "HAMAL" ),
         STARS[ 51 ] :   _( "IZAR" ),
         STARS[ 52 ] :   _( "KAPTEYN'S STAR" ),
         STARS[ 53 ] :   _( "KAUS AUSTRALIS" ),
         STARS[ 54 ] :   _( "KOCAB" ),
         STARS[ 55 ] :   _( "KRUGER 60" ),
         STARS[ 56 ] :   _( "LUYTEN'S STAR" ),
         STARS[ 57 ] :   _( "MARKAB" ),
         STARS[ 58 ] :   _( "MEGREZ" ),
         STARS[ 59 ] :   _( "MENKAR" ),
         STARS[ 60 ] :   _( "MERAK" ),
         STARS[ 61 ] :   _( "MINTAKA" ),
         STARS[ 62 ] :   _( "MIRA" ),
         STARS[ 63 ] :   _( "MIRACH" ),
         STARS[ 64 ] :   _( "MIRPHAK" ),
         STARS[ 65 ] :   _( "MIZAR" ),
         STARS[ 66 ] :   _( "NIHAL" ),
         STARS[ 67 ] :   _( "NUNKI" ),
         STARS[ 68 ] :   _( "PHAD" ),
         STARS[ 69 ] :   _( "PLEIONE" ),
         STARS[ 70 ] :   _( "POLARIS" ),
         STARS[ 71 ] :   _( "POLLUX" ),
         STARS[ 72 ] :   _( "PROCYON" ),
         STARS[ 73 ] :   _( "PROXIMA" ),
         STARS[ 74 ] :   _( "RASALGETHI" ),
         STARS[ 75 ] :   _( "RASALHAGUE" ),
         STARS[ 76 ] :   _( "RED RECTANGLE" ),
         STARS[ 77 ] :   _( "REGULUS" ),
         STARS[ 78 ] :   _( "RIGEL" ),
         STARS[ 79 ] :   _( "RIGIL KENT" ),
         STARS[ 80 ] :   _( "SADALMELIK" ),
         STARS[ 81 ] :   _( "SAIPH" ),
         STARS[ 82 ] :   _( "SCHEAT" ),
         STARS[ 83 ] :   _( "SHAULA" ),
         STARS[ 84 ] :   _( "SHEDIR" ),
         STARS[ 85 ] :   _( "SHELIAK" ),
         STARS[ 86 ] :   _( "SIRIUS" ),
         STARS[ 87 ] :   _( "SPICA" ),
         STARS[ 88 ] :   _( "TARAZED" ),
         STARS[ 89 ] :   _( "THUBAN" ),
         STARS[ 90 ] :   _( "UNUKALHAI" ),
         STARS[ 91 ] :   _( "VAN MAANEN 2" ),
         STARS[ 92 ] :   _( "VEGA" ),
         STARS[ 93 ] :   _( "VINDEMIATRIX" ),
         STARS[ 94 ] :   _( "ZAURAK" ) }


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
    DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS = "%Y-%m-%d %H:%M:%S"
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


    # If the minimum version of the third party library is met and available, returns None.
    # Otherwise returns an error message.
    @staticmethod
    @abstractmethod
    def getStatusMessage():
        return None


    # Returns the version of the underlying astronomical library.
    @staticmethod
    @abstractmethod
    def getVersion():
        return None


    # Calculate apparent magnitude.
    #
    # May throw a value error or similar if bad numbers/calculations occur.
    #
    # https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
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
    # https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
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


    @staticmethod
    def toDateTimeString( dateTime ):
        return dateTime.strftime( AstroBase.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS )


    # Take a start/end date/time used to search for a satellite transit
    # and determine where a given start/end hour will overlap.
    # 
    # Used to limit satellite passes from say dawn and dusk to just dusk.
    #
    # The start hour (as date/time) < end hour (as date/time).
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