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


    STARS_INDEX_NAME = 0
    STARS_INDEX_HIP = 1
    STARS_INDEX_NAME_TRANSLATION = 2
    STARS_INDEX_TAG_TRANSLATION = 3

    # PyEphem provides a list of stars and data, whereas Skyfield does not.
    # Over the years, the PyEphem stars have contained duplicates and misspellings.
    #
    # Therefore use the list of named stars at
    #    http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt
    #
    # DO NOT EDIT: Content must be created using 'createephemerisstars.py'.
    STARS = [
        [ "ACAMAR",            13847,  _( "Acamar" ),            _( "ACAMAR" ) ],
        [ "ACHERNAR",          7588,   _( "Achernar" ),          _( "ACHERNAR" ) ],
        [ "ACHIRD",            3821,   _( "Achird" ),            _( "ACHIRD" ) ],
        [ "ACRAB",             78820,  _( "Acrab" ),             _( "ACRAB" ) ],
        [ "ACRUX",             60718,  _( "Acrux" ),             _( "ACRUX" ) ],
        [ "ACUBENS",           44066,  _( "Acubens" ),           _( "ACUBENS" ) ],
        [ "ADHAFERA",          50335,  _( "Adhafera" ),          _( "ADHAFERA" ) ],
        [ "ADHARA",            33579,  _( "Adhara" ),            _( "ADHARA" ) ],
        [ "ADHIL",             6411,   _( "Adhil" ),             _( "ADHIL" ) ],
        [ "AIN",               20889,  _( "Ain" ),               _( "AIN" ) ],
        [ "AINALRAMI",         92761,  _( "Ainalrami" ),         _( "AINALRAMI" ) ],
        [ "ALADFAR",           94481,  _( "Aladfar" ),           _( "ALADFAR" ) ],
        [ "ALASIA",            90004,  _( "Alasia" ),            _( "ALASIA" ) ],
        [ "ALBALDAH",          94141,  _( "Albaldah" ),          _( "ALBALDAH" ) ],
        [ "ALBALI",            102618, _( "Albali" ),            _( "ALBALI" ) ],
        [ "ALBIREO",           95947,  _( "Albireo" ),           _( "ALBIREO" ) ],
        [ "ALCHIBA",           59199,  _( "Alchiba" ),           _( "ALCHIBA" ) ],
        [ "ALCOR",             65477,  _( "Alcor" ),             _( "ALCOR" ) ],
        [ "ALCYONE",           17702,  _( "Alcyone" ),           _( "ALCYONE" ) ],
        [ "ALDEBARAN",         21421,  _( "Aldebaran" ),         _( "ALDEBARAN" ) ],
        [ "ALDERAMIN",         105199, _( "Alderamin" ),         _( "ALDERAMIN" ) ],
        [ "ALDHANAB",          108085, _( "Aldhanab" ),          _( "ALDHANAB" ) ],
        [ "ALDHIBAH",          83895,  _( "Aldhibah" ),          _( "ALDHIBAH" ) ],
        [ "ALDULFIN",          101421, _( "Aldulfin" ),          _( "ALDULFIN" ) ],
        [ "ALFIRK",            106032, _( "Alfirk" ),            _( "ALFIRK" ) ],
        [ "ALGEDI",            100064, _( "Algedi" ),            _( "ALGEDI" ) ],
        [ "ALGENIB",           1067,   _( "Algenib" ),           _( "ALGENIB" ) ],
        [ "ALGIEBA",           50583,  _( "Algieba" ),           _( "ALGIEBA" ) ],
        [ "ALGOL",             14576,  _( "Algol" ),             _( "ALGOL" ) ],
        [ "ALGORAB",           60965,  _( "Algorab" ),           _( "ALGORAB" ) ],
        [ "ALHENA",            31681,  _( "Alhena" ),            _( "ALHENA" ) ],
        [ "ALIOTH",            62956,  _( "Alioth" ),            _( "ALIOTH" ) ],
        [ "ALJANAH",           102488, _( "Aljanah" ),           _( "ALJANAH" ) ],
        [ "ALKAID",            67301,  _( "Alkaid" ),            _( "ALKAID" ) ],
        [ "ALKALUROPS",        75411,  _( "Alkalurops" ),        _( "ALKALUROPS" ) ],
        [ "ALKAPHRAH",         44471,  _( "Alkaphrah" ),         _( "ALKAPHRAH" ) ],
        [ "ALKARAB",           115623, _( "Alkarab" ),           _( "ALKARAB" ) ],
        [ "ALKES",             53740,  _( "Alkes" ),             _( "ALKES" ) ],
        [ "ALMAAZ",            23416,  _( "Almaaz" ),            _( "ALMAAZ" ) ],
        [ "ALMACH",            9640,   _( "Almach" ),            _( "ALMACH" ) ],
        [ "ALNAIR",            109268, _( "Alnair" ),            _( "ALNAIR" ) ],
        [ "ALNASL",            88635,  _( "Alnasl" ),            _( "ALNASL" ) ],
        [ "ALNILAM",           26311,  _( "Alnilam" ),           _( "ALNILAM" ) ],
        [ "ALNITAK",           26727,  _( "Alnitak" ),           _( "ALNITAK" ) ],
        [ "ALNIYAT",           80112,  _( "Alniyat" ),           _( "ALNIYAT" ) ],
        [ "ALPHARD",           46390,  _( "Alphard" ),           _( "ALPHARD" ) ],
        [ "ALPHECCA",          76267,  _( "Alphecca" ),          _( "ALPHECCA" ) ],
        [ "ALPHERATZ",         677,    _( "Alpheratz" ),         _( "ALPHERATZ" ) ],
        [ "ALPHERG",           7097,   _( "Alpherg" ),           _( "ALPHERG" ) ],
        [ "ALRAKIS",           83608,  _( "Alrakis" ),           _( "ALRAKIS" ) ],
        [ "ALRESCHA",          9487,   _( "Alrescha" ),          _( "ALRESCHA" ) ],
        [ "ALRUBA",            86782,  _( "Alruba" ),            _( "ALRUBA" ) ],
        [ "ALSAFI",            96100,  _( "Alsafi" ),            _( "ALSAFI" ) ],
        [ "ALSCIAUKAT",        41075,  _( "Alsciaukat" ),        _( "ALSCIAUKAT" ) ],
        [ "ALSEPHINA",         42913,  _( "Alsephina" ),         _( "ALSEPHINA" ) ],
        [ "ALSHAIN",           98036,  _( "Alshain" ),           _( "ALSHAIN" ) ],
        [ "ALSHAT",            100310, _( "Alshat" ),            _( "ALSHAT" ) ],
        [ "ALTAIR",            97649,  _( "Altair" ),            _( "ALTAIR" ) ],
        [ "ALTAIS",            94376,  _( "Altais" ),            _( "ALTAIS" ) ],
        [ "ALTERF",            46750,  _( "Alterf" ),            _( "ALTERF" ) ],
        [ "ALUDRA",            35904,  _( "Aludra" ),            _( "ALUDRA" ) ],
        [ "ALULA AUSTRALIS",   55203,  _( "Alula Australis" ),   _( "ALULA AUSTRALIS" ) ],
        [ "ALULA BOREALIS",    55219,  _( "Alula Borealis" ),    _( "ALULA BOREALIS" ) ],
        [ "ALYA",              92946,  _( "Alya" ),              _( "ALYA" ) ],
        [ "ALZIRR",            32362,  _( "Alzirr" ),            _( "ALZIRR" ) ],
        [ "AMADIOHA",          29550,  _( "Amadioha" ),          _( "AMADIOHA" ) ],
        [ "ANCHA",             110003, _( "Ancha" ),             _( "ANCHA" ) ],
        [ "ANGETENAR",         13288,  _( "Angetenar" ),         _( "ANGETENAR" ) ],
        [ "ANIARA",            57820,  _( "Aniara" ),            _( "ANIARA" ) ],
        [ "ANKAA",             2081,   _( "Ankaa" ),             _( "ANKAA" ) ],
        [ "ANSER",             95771,  _( "Anser" ),             _( "ANSER" ) ],
        [ "ANTARES",           80763,  _( "Antares" ),           _( "ANTARES" ) ],
        [ "ARCALÍS",           72845,  _( "Arcalís" ),           _( "ARCALÍS" ) ],
        [ "ARCTURUS",          69673,  _( "Arcturus" ),          _( "ARCTURUS" ) ],
        [ "ARKAB POSTERIOR",   95294,  _( "Arkab Posterior" ),   _( "ARKAB POSTERIOR" ) ],
        [ "ARKAB PRIOR",       95241,  _( "Arkab Prior" ),       _( "ARKAB PRIOR" ) ],
        [ "ARNEB",             25985,  _( "Arneb" ),             _( "ARNEB" ) ],
        [ "ASCELLA",           93506,  _( "Ascella" ),           _( "ASCELLA" ) ],
        [ "ASELLUS AUSTRALIS", 42911,  _( "Asellus Australis" ), _( "ASELLUS AUSTRALIS" ) ],
        [ "ASELLUS BOREALIS",  42806,  _( "Asellus Borealis" ),  _( "ASELLUS BOREALIS" ) ],
        [ "ASHLESHA",          43109,  _( "Ashlesha" ),          _( "ASHLESHA" ) ],
        [ "ASPIDISKE",         45556,  _( "Aspidiske" ),         _( "ASPIDISKE" ) ],
        [ "ASTEROPE",          17579,  _( "Asterope" ),          _( "ASTEROPE" ) ],
        [ "ATHEBYNE",          80331,  _( "Athebyne" ),          _( "ATHEBYNE" ) ],
        [ "ATIK",              17448,  _( "Atik" ),              _( "ATIK" ) ],
        [ "ATLAS",             17847,  _( "Atlas" ),             _( "ATLAS" ) ],
        [ "ATRIA",             82273,  _( "Atria" ),             _( "ATRIA" ) ],
        [ "AVIOR",             41037,  _( "Avior" ),             _( "AVIOR" ) ],
        [ "AXÓLOTL",           118319, _( "Axólotl" ),           _( "AXÓLOTL" ) ],
        [ "AYEYARWADY",        13993,  _( "Ayeyarwady" ),        _( "AYEYARWADY" ) ],
        [ "AZELFAFAGE",        107136, _( "Azelfafage" ),        _( "AZELFAFAGE" ) ],
        [ "AZHA",              13701,  _( "Azha" ),              _( "AZHA" ) ],
        [ "AZMIDI",            38170,  _( "Azmidi" ),            _( "AZMIDI" ) ],
        [ "BAEKDU",            73136,  _( "Baekdu" ),            _( "BAEKDU" ) ],
        [ "BARNARD'S STAR",    87937,  _( "Barnard'S Star" ),    _( "BARNARD'S STAR" ) ],
        [ "BATEN KAITOS",      8645,   _( "Baten Kaitos" ),      _( "BATEN KAITOS" ) ],
        [ "BEEMIM",            20535,  _( "Beemim" ),            _( "BEEMIM" ) ],
        [ "BEID",              19587,  _( "Beid" ),              _( "BEID" ) ],
        [ "BELEL",             95124,  _( "Belel" ),             _( "BELEL" ) ],
        [ "BÉLÉNOS",           6643,   _( "Bélénos" ),           _( "BÉLÉNOS" ) ],
        [ "BELLATRIX",         25336,  _( "Bellatrix" ),         _( "BELLATRIX" ) ],
        [ "BETELGEUSE",        27989,  _( "Betelgeuse" ),        _( "BETELGEUSE" ) ],
        [ "BHARANI",           13209,  _( "Bharani" ),           _( "BHARANI" ) ],
        [ "BIBHĀ",             48711,  _( "Bibhā" ),             _( "BIBHĀ" ) ],
        [ "BIHAM",             109427, _( "Biham" ),             _( "BIHAM" ) ],
        [ "BOSONA",            107251, _( "Bosona" ),            _( "BOSONA" ) ],
        [ "BOTEIN",            14838,  _( "Botein" ),            _( "BOTEIN" ) ],
        [ "BRACHIUM",          73714,  _( "Brachium" ),          _( "BRACHIUM" ) ],
        [ "BUBUP",             26380,  _( "Bubup" ),             _( "BUBUP" ) ],
        [ "BUNA",              12191,  _( "Buna" ),              _( "BUNA" ) ],
        [ "BUNDA",             106786, _( "Bunda" ),             _( "BUNDA" ) ],
        [ "CANOPUS",           30438,  _( "Canopus" ),           _( "CANOPUS" ) ],
        [ "CAPELLA",           24608,  _( "Capella" ),           _( "CAPELLA" ) ],
        [ "CAPH",              746,    _( "Caph" ),              _( "CAPH" ) ],
        [ "CASTOR",            36850,  _( "Castor" ),            _( "CASTOR" ) ],
        [ "CASTULA",           4422,   _( "Castula" ),           _( "CASTULA" ) ],
        [ "CEBALRAI",          86742,  _( "Cebalrai" ),          _( "CEBALRAI" ) ],
        [ "CEIBO",             37284,  _( "Ceibo" ),             _( "CEIBO" ) ],
        [ "CELAENO",           17489,  _( "Celaeno" ),           _( "CELAENO" ) ],
        [ "CERVANTES",         86796,  _( "Cervantes" ),         _( "CERVANTES" ) ],
        [ "CHALAWAN",          53721,  _( "Chalawan" ),          _( "CHALAWAN" ) ],
        [ "CHAMUKUY",          20894,  _( "Chamukuy" ),          _( "CHAMUKUY" ) ],
        [ "CHARA",             61317,  _( "Chara" ),             _( "CHARA" ) ],
        [ "CHECHIA",           99894,  _( "Chechia" ),           _( "CHECHIA" ) ],
        [ "CHERTAN",           54879,  _( "Chertan" ),           _( "CHERTAN" ) ],
        [ "CITADELLE",         1547,   _( "Citadelle" ),         _( "CITADELLE" ) ],
        [ "CITALÁ",            33719,  _( "Citalá" ),            _( "CITALÁ" ) ],
        [ "COCIBOLCA",         3479,   _( "Cocibolca" ),         _( "COCIBOLCA" ) ],
        [ "COPERNICUS",        43587,  _( "Copernicus" ),        _( "COPERNICUS" ) ],
        [ "COR CAROLI",        63125,  _( "Cor Caroli" ),        _( "COR CAROLI" ) ],
        [ "CUJAM",             80463,  _( "Cujam" ),             _( "CUJAM" ) ],
        [ "CURSA",             23875,  _( "Cursa" ),             _( "CURSA" ) ],
        [ "DABIH",             100345, _( "Dabih" ),             _( "DABIH" ) ],
        [ "DALIM",             14879,  _( "Dalim" ),             _( "DALIM" ) ],
        [ "DENEB",             102098, _( "Deneb" ),             _( "DENEB" ) ],
        [ "DENEB ALGEDI",      107556, _( "Deneb Algedi" ),      _( "DENEB ALGEDI" ) ],
        [ "DENEBOLA",          57632,  _( "Denebola" ),          _( "DENEBOLA" ) ],
        [ "DIADEM",            64241,  _( "Diadem" ),            _( "DIADEM" ) ],
        [ "DINGOLAY",          54158,  _( "Dingolay" ),          _( "DINGOLAY" ) ],
        [ "DIPHDA",            3419,   _( "Diphda" ),            _( "DIPHDA" ) ],
        [ "DOFIDA",            66047,  _( "Dofida" ),            _( "DOFIDA" ) ],
        [ "DSCHUBBA",          78401,  _( "Dschubba" ),          _( "DSCHUBBA" ) ],
        [ "DUBHE",             54061,  _( "Dubhe" ),             _( "DUBHE" ) ],
        [ "DZIBAN",            86614,  _( "Dziban" ),            _( "DZIBAN" ) ],
        [ "EBLA",              114322, _( "Ebla" ),              _( "EBLA" ) ],
        [ "EDASICH",           75458,  _( "Edasich" ),           _( "EDASICH" ) ],
        [ "ELECTRA",           17499,  _( "Electra" ),           _( "ELECTRA" ) ],
        [ "ELGAFAR",           70755,  _( "Elgafar" ),           _( "ELGAFAR" ) ],
        [ "ELKURUD",           29034,  _( "Elkurud" ),           _( "ELKURUD" ) ],
        [ "ELNATH",            25428,  _( "Elnath" ),            _( "ELNATH" ) ],
        [ "ELTANIN",           87833,  _( "Eltanin" ),           _( "ELTANIN" ) ],
        [ "EMIW",              5529,   _( "Emiw" ),              _( "EMIW" ) ],
        [ "ENIF",              107315, _( "Enif" ),              _( "ENIF" ) ],
        [ "ERRAI",             116727, _( "Errai" ),             _( "ERRAI" ) ],
        [ "FAFNIR",            90344,  _( "Fafnir" ),            _( "FAFNIR" ) ],
        [ "FANG",              78265,  _( "Fang" ),              _( "FANG" ) ],
        [ "FAWARIS",           97165,  _( "Fawaris" ),           _( "FAWARIS" ) ],
        [ "FELIS",             48615,  _( "Felis" ),             _( "FELIS" ) ],
        [ "FELIXVARELA",       2247,   _( "Felixvarela" ),       _( "FELIXVARELA" ) ],
        [ "FLEGETONTE",        57370,  _( "Flegetonte" ),        _( "FLEGETONTE" ) ],
        [ "FOMALHAUT",         113368, _( "Fomalhaut" ),         _( "FOMALHAUT" ) ],
        [ "FORMOSA",           56508,  _( "Formosa" ),           _( "FORMOSA" ) ],
        [ "FULU",              2920,   _( "Fulu" ),              _( "FULU" ) ],
        [ "FUMALSAMAKAH",      113889, _( "Fumalsamakah" ),      _( "FUMALSAMAKAH" ) ],
        [ "FUNI",              61177,  _( "Funi" ),              _( "FUNI" ) ],
        [ "FURUD",             30122,  _( "Furud" ),             _( "FURUD" ) ],
        [ "FUYUE",             87261,  _( "Fuyue" ),             _( "FUYUE" ) ],
        [ "GACRUX",            61084,  _( "Gacrux" ),            _( "GACRUX" ) ],
        [ "GAKYID",            42446,  _( "Gakyid" ),            _( "GAKYID" ) ],
        [ "GIAUSAR",           56211,  _( "Giausar" ),           _( "GIAUSAR" ) ],
        [ "GIENAH",            59803,  _( "Gienah" ),            _( "GIENAH" ) ],
        [ "GINAN",             60260,  _( "Ginan" ),             _( "GINAN" ) ],
        [ "GOMEISA",           36188,  _( "Gomeisa" ),           _( "GOMEISA" ) ],
        [ "GRUMIUM",           87585,  _( "Grumium" ),           _( "GRUMIUM" ) ],
        [ "GUDJA",             77450,  _( "Gudja" ),             _( "GUDJA" ) ],
        [ "GUMALA",            94645,  _( "Gumala" ),            _( "GUMALA" ) ],
        [ "GUNIIBUU",          84405,  _( "Guniibuu" ),          _( "GUNIIBUU" ) ],
        [ "HADAR",             68702,  _( "Hadar" ),             _( "HADAR" ) ],
        [ "HAEDUS",            23767,  _( "Haedus" ),            _( "HAEDUS" ) ],
        [ "HAMAL",             9884,   _( "Hamal" ),             _( "HAMAL" ) ],
        [ "HASSALEH",          23015,  _( "Hassaleh" ),          _( "HASSALEH" ) ],
        [ "HATYSA",            26241,  _( "Hatysa" ),            _( "HATYSA" ) ],
        [ "HELVETIOS",         113357, _( "Helvetios" ),         _( "HELVETIOS" ) ],
        [ "HEZE",              66249,  _( "Heze" ),              _( "HEZE" ) ],
        [ "HOGGAR",            21109,  _( "Hoggar" ),            _( "HOGGAR" ) ],
        [ "HOMAM",             112029, _( "Homam" ),             _( "HOMAM" ) ],
        [ "HUNAHPÚ",           55174,  _( "Hunahpú" ),           _( "HUNAHPÚ" ) ],
        [ "HUNOR",             80076,  _( "Hunor" ),             _( "HUNOR" ) ],
        [ "IKLIL",             78104,  _( "Iklil" ),             _( "IKLIL" ) ],
        [ "ILLYRIAN",          47087,  _( "Illyrian" ),          _( "ILLYRIAN" ) ],
        [ "IMAI",              59747,  _( "Imai" ),              _( "IMAI" ) ],
        [ "INQUILL",           84787,  _( "Inquill" ),           _( "INQUILL" ) ],
        [ "INTAN",             15578,  _( "Intan" ),             _( "INTAN" ) ],
        [ "INTERCRUS",         46471,  _( "Intercrus" ),         _( "INTERCRUS" ) ],
        [ "ITONDA",            108375, _( "Itonda" ),            _( "ITONDA" ) ],
        [ "IZAR",              72105,  _( "Izar" ),              _( "IZAR" ) ],
        [ "JABBAH",            79374,  _( "Jabbah" ),            _( "JABBAH" ) ],
        [ "JISHUI",            37265,  _( "Jishui" ),            _( "JISHUI" ) ],
        [ "KAFFALJIDHMA",      12706,  _( "Kaffaljidhma" ),      _( "KAFFALJIDHMA" ) ],
        [ "KALAUSI",           47202,  _( "Kalausi" ),           _( "KALAUSI" ) ],
        [ "KAMUY",             79219,  _( "Kamuy" ),             _( "KAMUY" ) ],
        [ "KANG",              69427,  _( "Kang" ),              _( "KANG" ) ],
        [ "KARAKA",            76351,  _( "Karaka" ),            _( "KARAKA" ) ],
        [ "KAUS AUSTRALIS",    90185,  _( "Kaus Australis" ),    _( "KAUS AUSTRALIS" ) ],
        [ "KAUS BOREALIS",     90496,  _( "Kaus Borealis" ),     _( "KAUS BOREALIS" ) ],
        [ "KAUS MEDIA",        89931,  _( "Kaus Media" ),        _( "KAUS MEDIA" ) ],
        [ "KAVEH",             92895,  _( "Kaveh" ),             _( "KAVEH" ) ],
        [ "KEID",              19849,  _( "Keid" ),              _( "KEID" ) ],
        [ "KHAMBALIA",         69974,  _( "Khambalia" ),         _( "KHAMBALIA" ) ],
        [ "KITALPHA",          104987, _( "Kitalpha" ),          _( "KITALPHA" ) ],
        [ "KOCHAB",            72607,  _( "Kochab" ),            _( "KOCHAB" ) ],
        [ "KOEIA",             12961,  _( "Koeia" ),             _( "KOEIA" ) ],
        [ "KORNEPHOROS",       80816,  _( "Kornephoros" ),       _( "KORNEPHOROS" ) ],
        [ "KRAZ",              61359,  _( "Kraz" ),              _( "KRAZ" ) ],
        [ "KURHAH",            108917, _( "Kurhah" ),            _( "KURHAH" ) ],
        [ "LA SUPERBA",        62223,  _( "La Superba" ),        _( "LA SUPERBA" ) ],
        [ "LARAWAG",           82396,  _( "Larawag" ),           _( "LARAWAG" ) ],
        [ "LESATH",            85696,  _( "Lesath" ),            _( "LESATH" ) ],
        [ "LIBERTAS",          97938,  _( "Libertas" ),          _( "LIBERTAS" ) ],
        [ "LIESMA",            66192,  _( "Liesma" ),            _( "LIESMA" ) ],
        [ "LILII BOREA",       13061,  _( "Lilii Borea" ),       _( "LILII BOREA" ) ],
        [ "LIONROCK",          110813, _( "Lionrock" ),          _( "LIONROCK" ) ],
        [ "LUCILINBURHUC",     30860,  _( "Lucilinburhuc" ),     _( "LUCILINBURHUC" ) ],
        [ "LUSITÂNIA",         30905,  _( "Lusitânia" ),         _( "LUSITÂNIA" ) ],
        [ "MAASYM",            85693,  _( "Maasym" ),            _( "MAASYM" ) ],
        [ "MACONDO",           52521,  _( "Macondo" ),           _( "MACONDO" ) ],
        [ "MAGO",              24003,  _( "Mago" ),              _( "MAGO" ) ],
        [ "MAHASIM",           28380,  _( "Mahasim" ),           _( "MAHASIM" ) ],
        [ "MAHSATI",           82651,  _( "Mahsati" ),           _( "MAHSATI" ) ],
        [ "MAIA",              17573,  _( "Maia" ),              _( "MAIA" ) ],
        [ "MARFIK",            80883,  _( "Marfik" ),            _( "MARFIK" ) ],
        [ "MARKAB",            113963, _( "Markab" ),            _( "MARKAB" ) ],
        [ "MARKEB",            45941,  _( "Markeb" ),            _( "MARKEB" ) ],
        [ "MARSIC",            79043,  _( "Marsic" ),            _( "MARSIC" ) ],
        [ "MATAR",             112158, _( "Matar" ),             _( "MATAR" ) ],
        [ "MEBSUTA",           32246,  _( "Mebsuta" ),           _( "MEBSUTA" ) ],
        [ "MEGREZ",            59774,  _( "Megrez" ),            _( "MEGREZ" ) ],
        [ "MEISSA",            26207,  _( "Meissa" ),            _( "MEISSA" ) ],
        [ "MEKBUDA",           34088,  _( "Mekbuda" ),           _( "MEKBUDA" ) ],
        [ "MELEPH",            42556,  _( "Meleph" ),            _( "MELEPH" ) ],
        [ "MENKALINAN",        28360,  _( "Menkalinan" ),        _( "MENKALINAN" ) ],
        [ "MENKAR",            14135,  _( "Menkar" ),            _( "MENKAR" ) ],
        [ "MENKENT",           68933,  _( "Menkent" ),           _( "MENKENT" ) ],
        [ "MENKIB",            18614,  _( "Menkib" ),            _( "MENKIB" ) ],
        [ "MERAK",             53910,  _( "Merak" ),             _( "MERAK" ) ],
        [ "MERGA",             72487,  _( "Merga" ),             _( "MERGA" ) ],
        [ "MERIDIANA",         94114,  _( "Meridiana" ),         _( "MERIDIANA" ) ],
        [ "MEROPE",            17608,  _( "Merope" ),            _( "MEROPE" ) ],
        [ "MESARTHIM",         8832,   _( "Mesarthim" ),         _( "MESARTHIM" ) ],
        [ "MIAPLACIDUS",       45238,  _( "Miaplacidus" ),       _( "MIAPLACIDUS" ) ],
        [ "MIMOSA",            62434,  _( "Mimosa" ),            _( "MIMOSA" ) ],
        [ "MINCHIR",           42402,  _( "Minchir" ),           _( "MINCHIR" ) ],
        [ "MINELAUVA",         63090,  _( "Minelauva" ),         _( "MINELAUVA" ) ],
        [ "MINTAKA",           25930,  _( "Mintaka" ),           _( "MINTAKA" ) ],
        [ "MIRA",              10826,  _( "Mira" ),              _( "MIRA" ) ],
        [ "MIRACH",            5447,   _( "Mirach" ),            _( "MIRACH" ) ],
        [ "MIRAM",             13268,  _( "Miram" ),             _( "MIRAM" ) ],
        [ "MIRFAK",            15863,  _( "Mirfak" ),            _( "MIRFAK" ) ],
        [ "MIRZAM",            30324,  _( "Mirzam" ),            _( "MIRZAM" ) ],
        [ "MISAM",             14668,  _( "Misam" ),             _( "MISAM" ) ],
        [ "MIZAR",             65378,  _( "Mizar" ),             _( "MIZAR" ) ],
        [ "MÖNCH",             72339,  _( "Mönch" ),             _( "MÖNCH" ) ],
        [ "MOTHALLAH",         8796,   _( "Mothallah" ),         _( "MOTHALLAH" ) ],
        [ "MOUHOUN",           22491,  _( "Mouhoun" ),           _( "MOUHOUN" ) ],
        [ "MULIPHEIN",         34045,  _( "Muliphein" ),         _( "MULIPHEIN" ) ],
        [ "MUPHRID",           67927,  _( "Muphrid" ),           _( "MUPHRID" ) ],
        [ "MUSCIDA",           41704,  _( "Muscida" ),           _( "MUSCIDA" ) ],
        [ "MUSICA",            103527, _( "Musica" ),            _( "MUSICA" ) ],
        [ "NAHN",              44946,  _( "Nahn" ),              _( "NAHN" ) ],
        [ "NAOS",              39429,  _( "Naos" ),              _( "NAOS" ) ],
        [ "NASHIRA",           106985, _( "Nashira" ),           _( "NASHIRA" ) ],
        [ "NÁSTI",             40687,  _( "Násti" ),             _( "NÁSTI" ) ],
        [ "NATASHA",           48235,  _( "Natasha" ),           _( "NATASHA" ) ],
        [ "NEKKAR",            73555,  _( "Nekkar" ),            _( "NEKKAR" ) ],
        [ "NEMBUS",            7607,   _( "Nembus" ),            _( "NEMBUS" ) ],
        [ "NENQUE",            5054,   _( "Nenque" ),            _( "NENQUE" ) ],
        [ "NERVIA",            32916,  _( "Nervia" ),            _( "NERVIA" ) ],
        [ "NGANURGANITY",      33856,  _( "Nganurganity" ),      _( "NGANURGANITY" ) ],
        [ "NIHAL",             25606,  _( "Nihal" ),             _( "NIHAL" ) ],
        [ "NIKAWIY",           74961,  _( "Nikawiy" ),           _( "NIKAWIY" ) ],
        [ "NOSAXA",            31895,  _( "Nosaxa" ),            _( "NOSAXA" ) ],
        [ "NUNKI",             92855,  _( "Nunki" ),             _( "NUNKI" ) ],
        [ "NUSAKAN",           75695,  _( "Nusakan" ),           _( "NUSAKAN" ) ],
        [ "NUSHAGAK",          13192,  _( "Nushagak" ),          _( "NUSHAGAK" ) ],
        [ "OGMA",              80838,  _( "Ogma" ),              _( "OGMA" ) ],
        [ "OKAB",              93747,  _( "Okab" ),              _( "OKAB" ) ],
        [ "PAIKAUHALE",        81266,  _( "Paikauhale" ),        _( "PAIKAUHALE" ) ],
        [ "PEACOCK",           100751, _( "Peacock" ),           _( "PEACOCK" ) ],
        [ "PHACT",             26634,  _( "Phact" ),             _( "PHACT" ) ],
        [ "PHECDA",            58001,  _( "Phecda" ),            _( "PHECDA" ) ],
        [ "PHERKAD",           75097,  _( "Pherkad" ),           _( "PHERKAD" ) ],
        [ "PHOENICIA",         99711,  _( "Phoenicia" ),         _( "PHOENICIA" ) ],
        [ "PIAUTOS",           40881,  _( "Piautos" ),           _( "PIAUTOS" ) ],
        [ "PINCOYA",           88414,  _( "Pincoya" ),           _( "PINCOYA" ) ],
        [ "PIPIRIMA",          82545,  _( "Pipirima" ),          _( "PIPIRIMA" ) ],
        [ "PLEIONE",           17851,  _( "Pleione" ),           _( "PLEIONE" ) ],
        [ "POERAVA",           116084, _( "Poerava" ),           _( "POERAVA" ) ],
        [ "POLARIS",           11767,  _( "Polaris" ),           _( "POLARIS" ) ],
        [ "POLARIS AUSTRALIS", 104382, _( "Polaris Australis" ), _( "POLARIS AUSTRALIS" ) ],
        [ "POLIS",             89341,  _( "Polis" ),             _( "POLIS" ) ],
        [ "POLLUX",            37826,  _( "Pollux" ),            _( "POLLUX" ) ],
        [ "PORRIMA",           61941,  _( "Porrima" ),           _( "PORRIMA" ) ],
        [ "PRAECIPUA",         53229,  _( "Praecipua" ),         _( "PRAECIPUA" ) ],
        [ "PRIMA HYADUM",      20205,  _( "Prima Hyadum" ),      _( "PRIMA HYADUM" ) ],
        [ "PROCYON",           37279,  _( "Procyon" ),           _( "PROCYON" ) ],
        [ "PROPUS",            29655,  _( "Propus" ),            _( "PROPUS" ) ],
        [ "PROXIMA CENTAURI",  70890,  _( "Proxima Centauri" ),  _( "PROXIMA CENTAURI" ) ],
        [ "RAN",               16537,  _( "Ran" ),               _( "RAN" ) ],
        [ "RANA",              17378,  _( "Rana" ),              _( "RANA" ) ],
        [ "RAPETO",            83547,  _( "Rapeto" ),            _( "RAPETO" ) ],
        [ "RASALAS",           48455,  _( "Rasalas" ),           _( "RASALAS" ) ],
        [ "RASALGETHI",        84345,  _( "Rasalgethi" ),        _( "RASALGETHI" ) ],
        [ "RASALHAGUE",        86032,  _( "Rasalhague" ),        _( "RASALHAGUE" ) ],
        [ "RASTABAN",          85670,  _( "Rastaban" ),          _( "RASTABAN" ) ],
        [ "REGULUS",           49669,  _( "Regulus" ),           _( "REGULUS" ) ],
        [ "REVATI",            5737,   _( "Revati" ),            _( "REVATI" ) ],
        [ "RIGEL",             24436,  _( "Rigel" ),             _( "RIGEL" ) ],
        [ "RIGIL KENTAURUS",   71683,  _( "Rigil Kentaurus" ),   _( "RIGIL KENTAURUS" ) ],
        [ "ROSALÍADECASTRO",   81022,  _( "Rosalíadecastro" ),   _( "ROSALÍADECASTRO" ) ],
        [ "ROTANEV",           101769, _( "Rotanev" ),           _( "ROTANEV" ) ],
        [ "RUCHBAH",           6686,   _( "Ruchbah" ),           _( "RUCHBAH" ) ],
        [ "RUKBAT",            95347,  _( "Rukbat" ),            _( "RUKBAT" ) ],
        [ "SABIK",             84012,  _( "Sabik" ),             _( "SABIK" ) ],
        [ "SACLATENI",         23453,  _( "Saclateni" ),         _( "SACLATENI" ) ],
        [ "SADACHBIA",         110395, _( "Sadachbia" ),         _( "SADACHBIA" ) ],
        [ "SADALBARI",         112748, _( "Sadalbari" ),         _( "SADALBARI" ) ],
        [ "SADALMELIK",        109074, _( "Sadalmelik" ),        _( "SADALMELIK" ) ],
        [ "SADALSUUD",         106278, _( "Sadalsuud" ),         _( "SADALSUUD" ) ],
        [ "SADR",              100453, _( "Sadr" ),              _( "SADR" ) ],
        [ "SAGARMATHA",        56572,  _( "Sagarmatha" ),        _( "SAGARMATHA" ) ],
        [ "SAIPH",             27366,  _( "Saiph" ),             _( "SAIPH" ) ],
        [ "SALM",              115250, _( "Salm" ),              _( "SALM" ) ],
        [ "SĀMAYA",            106824, _( "Sāmaya" ),            _( "SĀMAYA" ) ],
        [ "SARGAS",            86228,  _( "Sargas" ),            _( "SARGAS" ) ],
        [ "SARIN",             84379,  _( "Sarin" ),             _( "SARIN" ) ],
        [ "SCEPTRUM",          21594,  _( "Sceptrum" ),          _( "SCEPTRUM" ) ],
        [ "SCHEAT",            113881, _( "Scheat" ),            _( "SCHEAT" ) ],
        [ "SCHEDAR",           3179,   _( "Schedar" ),           _( "SCHEDAR" ) ],
        [ "SECUNDA HYADUM",    20455,  _( "Secunda Hyadum" ),    _( "SECUNDA HYADUM" ) ],
        [ "SEGIN",             8886,   _( "Segin" ),             _( "SEGIN" ) ],
        [ "SEGINUS",           71075,  _( "Seginus" ),           _( "SEGINUS" ) ],
        [ "SHAM",              96757,  _( "Sham" ),              _( "SHAM" ) ],
        [ "SHAMA",             55664,  _( "Shama" ),             _( "SHAMA" ) ],
        [ "SHARJAH",           79431,  _( "Sharjah" ),           _( "SHARJAH" ) ],
        [ "SHAULA",            85927,  _( "Shaula" ),            _( "SHAULA" ) ],
        [ "SHELIAK",           92420,  _( "Sheliak" ),           _( "SHELIAK" ) ],
        [ "SHERATAN",          8903,   _( "Sheratan" ),          _( "SHERATAN" ) ],
        [ "SIKA",              95262,  _( "Sika" ),              _( "SIKA" ) ],
        [ "SIRIUS",            32349,  _( "Sirius" ),            _( "SIRIUS" ) ],
        [ "SITULA",            111710, _( "Situla" ),            _( "SITULA" ) ],
        [ "SKAT",              113136, _( "Skat" ),              _( "SKAT" ) ],
        [ "SOLARIS",           104780, _( "Solaris" ),           _( "SOLARIS" ) ],
        [ "SPICA",             65474,  _( "Spica" ),             _( "SPICA" ) ],
        [ "STRIBOR",           43674,  _( "Stribor" ),           _( "STRIBOR" ) ],
        [ "SUALOCIN",          101958, _( "Sualocin" ),          _( "SUALOCIN" ) ],
        [ "SUBRA",             47508,  _( "Subra" ),             _( "SUBRA" ) ],
        [ "SUHAIL",            44816,  _( "Suhail" ),            _( "SUHAIL" ) ],
        [ "SULAFAT",           93194,  _( "Sulafat" ),           _( "SULAFAT" ) ],
        [ "SYRMA",             69701,  _( "Syrma" ),             _( "SYRMA" ) ],
        [ "TABIT",             22449,  _( "Tabit" ),             _( "TABIT" ) ],
        [ "TAIYANGSHOU",       57399,  _( "Taiyangshou" ),       _( "TAIYANGSHOU" ) ],
        [ "TAIYI",             63076,  _( "Taiyi" ),             _( "TAIYI" ) ],
        [ "TALITHA",           44127,  _( "Talitha" ),           _( "TALITHA" ) ],
        [ "TANIA AUSTRALIS",   50801,  _( "Tania Australis" ),   _( "TANIA AUSTRALIS" ) ],
        [ "TANIA BOREALIS",    50372,  _( "Tania Borealis" ),    _( "TANIA BOREALIS" ) ],
        [ "TAPECUE",           38041,  _( "Tapecue" ),           _( "TAPECUE" ) ],
        [ "TARAZED",           97278,  _( "Tarazed" ),           _( "TARAZED" ) ],
        [ "TARF",              40526,  _( "Tarf" ),              _( "TARF" ) ],
        [ "TAYGETA",           17531,  _( "Taygeta" ),           _( "TAYGETA" ) ],
        [ "TEGMINE",           40167,  _( "Tegmine" ),           _( "TEGMINE" ) ],
        [ "TEJAT",             30343,  _( "Tejat" ),             _( "TEJAT" ) ],
        [ "TEREBELLUM",        98066,  _( "Terebellum" ),        _( "TEREBELLUM" ) ],
        [ "THEEMIN",           21393,  _( "Theemin" ),           _( "THEEMIN" ) ],
        [ "THUBAN",            68756,  _( "Thuban" ),            _( "THUBAN" ) ],
        [ "TIAKI",             112122, _( "Tiaki" ),             _( "TIAKI" ) ],
        [ "TIANGUAN",          26451,  _( "Tianguan" ),          _( "TIANGUAN" ) ],
        [ "TIANYI",            62423,  _( "Tianyi" ),            _( "TIANYI" ) ],
        [ "TIMIR",             80687,  _( "Timir" ),             _( "TIMIR" ) ],
        [ "TITAWIN",           7513,   _( "Titawin" ),           _( "TITAWIN" ) ],
        [ "TOLIMAN",           71681,  _( "Toliman" ),           _( "TOLIMAN" ) ],
        [ "TONATIUH",          58952,  _( "Tonatiuh" ),          _( "TONATIUH" ) ],
        [ "TORCULAR",          8198,   _( "Torcular" ),          _( "TORCULAR" ) ],
        [ "TUPÃ",              60644,  _( "Tupã" ),              _( "TUPÃ" ) ],
        [ "TUPI",              17096,  _( "Tupi" ),              _( "TUPI" ) ],
        [ "TUREIS",            39757,  _( "Tureis" ),            _( "TUREIS" ) ],
        [ "UKDAH",             47431,  _( "Ukdah" ),             _( "UKDAH" ) ],
        [ "UKLUN",             57291,  _( "Uklun" ),             _( "UKLUN" ) ],
        [ "UNUKALHAI",         77070,  _( "Unukalhai" ),         _( "UNUKALHAI" ) ],
        [ "URUK",              96078,  _( "Uruk" ),              _( "URUK" ) ],
        [ "VEGA",              91262,  _( "Vega" ),              _( "VEGA" ) ],
        [ "VERITATE",          116076, _( "Veritate" ),          _( "VERITATE" ) ],
        [ "VINDEMIATRIX",      63608,  _( "Vindemiatrix" ),      _( "VINDEMIATRIX" ) ],
        [ "WASAT",             35550,  _( "Wasat" ),             _( "WASAT" ) ],
        [ "WAZN",              27628,  _( "Wazn" ),              _( "WAZN" ) ],
        [ "WEZEN",             34444,  _( "Wezen" ),             _( "WEZEN" ) ],
        [ "WURREN",            5348,   _( "Wurren" ),            _( "WURREN" ) ],
        [ "XAMIDIMURA",        82514,  _( "Xamidimura" ),        _( "XAMIDIMURA" ) ],
        [ "XIHE",              91852,  _( "Xihe" ),              _( "XIHE" ) ],
        [ "XUANGE",            69732,  _( "Xuange" ),            _( "XUANGE" ) ],
        [ "YED POSTERIOR",     79882,  _( "Yed Posterior" ),     _( "YED POSTERIOR" ) ],
        [ "YED PRIOR",         79593,  _( "Yed Prior" ),         _( "YED PRIOR" ) ],
        [ "YILDUN",            85822,  _( "Yildun" ),            _( "YILDUN" ) ],
        [ "ZANIAH",            60129,  _( "Zaniah" ),            _( "ZANIAH" ) ],
        [ "ZAURAK",            18543,  _( "Zaurak" ),            _( "ZAURAK" ) ],
        [ "ZAVIJAVA",          57757,  _( "Zavijava" ),          _( "ZAVIJAVA" ) ],
        [ "ZHANG",             48356,  _( "Zhang" ),             _( "ZHANG" ) ],
        [ "ZIBAL",             15197,  _( "Zibal" ),             _( "ZIBAL" ) ],
        [ "ZOSMA",             54872,  _( "Zosma" ),             _( "ZOSMA" ) ],
        [ "ZUBENELGENUBI",     72622,  _( "Zubenelgenubi" ),     _( "ZUBENELGENUBI" ) ],
        [ "ZUBENELHAKRABI",    76333,  _( "Zubenelhakrabi" ),    _( "ZUBENELHAKRABI" ) ],
        [ "ZUBENESCHAMALI",    74785,  _( "Zubeneschamali" ),    _( "ZUBENESCHAMALI" ) ] ]


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


    @staticmethod
    def __getStarRow( star ):
        return next( i for i in AstroBase.STARS if i[ AstroBase.STARS_INDEX_NAME ] == star )


    @staticmethod
    def getStarHIP( star ):
        return AstroBase.__getStarRow( star )[ AstroBase.STARS_INDEX_HIP ]


    @staticmethod
    def getStarNameTranslation( star ):
        return AstroBase.__getStarRow( star )[ AstroBase.STARS_INDEX_NAME_TRANSLATION ]


    @staticmethod
    def getStarTagTranslation( star ):
        return AstroBase.__getStarRow( star )[ AstroBase.STARS_INDEX_TAG_TRANSLATION ]


    @staticmethod
    def getStarNames():
        return [ i[ AstroBase.STARS_INDEX_NAME ] for i in AstroBase.STARS ]


    @staticmethod
    def getStarHIPs():
        return [ i[ AstroBase.STARS_INDEX_HIP ] for i in AstroBase.STARS ]


    @staticmethod
    def getStarTagTranslationPairs():
        return [ ( i[ AstroBase.STARS_INDEX_NAME ], i[ AstroBase.STARS_INDEX_TAG_TRANSLATION ] ) for i in AstroBase.STARS ]


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
