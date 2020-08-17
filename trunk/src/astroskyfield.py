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


#TODO If/when Skyfield replaces PyEphem, need to remove python3-ephem from debian/control.
# Need to add anything else, say pip3?
# sudo apt install python3-pip


# Required by the functions at the end to create the stars/planet ephemerides; uncomment as needed!
# import gettext
# gettext.install( "astroskyfield" )


try:
    from skyfield import almanac, constants
    from skyfield.api import load, Star, Topos
    from skyfield.data import hipparcos, mpc
    from skyfield.magnitudelib import planetary_magnitude
    available = True

except ImportError:
    available = False

import astrobase, io, locale, orbitalelement


class AstroSkyfield( astrobase.AstroBase ):

    __EPHEMERIS_PLANETS = "planets.bsp"
    __EPHEMERIS_STARS = "stars.dat.gz"


    # Name tags for bodies.
    __MOON = "MOON"
    __SUN = "SUN"

    __PLANET_EARTH = "EARTH"

    __PLANET_MAPPINGS = {
        astrobase.AstroBase.PLANET_MERCURY : "MERCURY BARYCENTER",
        astrobase.AstroBase.PLANET_VENUS   : "VENUS BARYCENTER",
        astrobase.AstroBase.PLANET_MARS    : "MARS BARYCENTER",
        astrobase.AstroBase.PLANET_JUPITER : "JUPITER BARYCENTER",
        astrobase.AstroBase.PLANET_SATURN  : "SATURN BARYCENTER",
        astrobase.AstroBase.PLANET_URANUS  : "URANUS BARYCENTER",
        astrobase.AstroBase.PLANET_NEPTUNE : "NEPTUNE BARYCENTER",
        astrobase.AstroBase.PLANET_PLUTO   : "PLUTO BARYCENTER" }


    # Taken from skyfield/named_stars.py
    astrobase.AstroBase.STARS.extend( [
        "ACHERNAR",
        "ACRUX",
        "ADHARA",
        "AGENA",
        "ALBIREO",
        "ALCOR",
        "ALDEBARAN",
        "ALDERAMIN",
        "ALGENIB",
        "ALGIEBA",
        "ALGOL",
        "ALHENA",
        "ALIOTH",
        "ALKAID",
        "ALMACH",
        "ALNAIR",
        "ALNILAM",
        "ALNITAK",
        "ALPHARD",
        "ALPHECCA",
        "ALPHERATZ",
        "ALTAIR",
        "ALUDRA",
        "ANKAA",
        "ANTARES",
        "ARCTURUS",
        "ARIDED",
        "ARIDIF",
        "ASPIDISKE",
        "ATRIA",
        "AVIOR",
        "BECRUX",
        "BELLATRIX",
        "BENETNASH",
        "BETELGEUSE",
        "BIRDUN",
        "CANOPUS",
        "CAPELLA",
        "CAPH",
        "CASTOR",
        "DENEB KAITOS",
        "DENEB",
        "DENEBOLA",
        "DIPHDA",
        "DSCHUBBA",
        "DUBHE",
        "DURRE MENTHOR",
        "ELNATH",
        "ENIF",
        "ETAMIN",
        "FOMALHAUT",
        "FORAMEN",
        "GACRUX",
        "GEMMA",
        "GIENAH",
        "GIRTAB",
        "GRUID",
        "HADAR",
        "HAMAL",
        "HERSCHEL'S GARNET STAR",
        "IZAR",
        "KAUS AUSTRALIS",
        "KOCHAB",
        "KOO SHE",
        "MARCHAB",
        "MARFIKENT",
        "MARKAB",
        "MEGREZ",
        "MEN",
        "MENKALINAN",
        "MENKENT",
        "MERAK",
        "MIAPLACIDUS",
        "MIMOSA",
        "MINTAKA",
        "MIRA",
        "MIRACH",
        "MIRFAK",
        "MIRZAM",
        "MIZAR",
        "MUHLIFEIN",
        "MURZIM",
        "NAOS",
        "NUNKI",
        "PEACOCK",
        "PHAD",
        "PHECDA",
        "POLARIS",
        "POLLUX",
        "PROCYON",
        "RAS ALHAGUE",
        "RASALHAGUE",
        "REGOR",
        "REGULUS",
        "RIGEL KENT",
        "RIGEL",
        "RIGIL KENTAURUS",
        "SABIK",
        "SADIRA",
        "SADR",
        "SAIPH",
        "SARGAS",
        "SCHEAT",
        "SCHEDAR",
        "SCUTULUM",
        "SHAULA",
        "SIRIUS",
        "SIRRAH",
        "SOUTH STAR",
        "SPICA",
        "SUHAIL",
        "THUBAN",
        "TOLIMAN",
        "TSEEN SHE",
        "TSIH",
        "TURAIS",
        "VEGA",
        "WEI",
        "WEZEN" ] )

    astrobase.AstroBase.STARS_TO_HIP.update( {
        "ACHERNAR":               7588,
        "ACRUX":                  60718,
        "ADHARA":                 33579,
        "AGENA":                  68702,
        "ALBIREO":                95947,
        "ALCOR":                  65477,
        "ALDEBARAN":              21421,
        "ALDERAMIN":              105199,
        "ALGENIB":                15863,
        "ALGIEBA":                50583,
        "ALGOL":                  14576,
        "ALHENA":                 31681,
        "ALIOTH":                 62956,
        "ALKAID":                 67301,
        "ALMACH":                 9640,
        "ALNAIR":                 109268,
        "ALNILAM":                26311,
        "ALNITAK":                26727,
        "ALPHARD":                46390,
        "ALPHECCA":               76267,
        "ALPHERATZ":              677,
        "ALTAIR":                 97649,
        "ALUDRA":                 35904,
        "ANKAA":                  2081,
        "ANTARES":                80763,
        "ARCTURUS":               69673,
        "ARIDED":                 102098,
        "ARIDIF":                 102098,
        "ASPIDISKE":              45556,
        "ATRIA":                  82273,
        "AVIOR":                  41037,
        "BECRUX":                 62434,
        "BELLATRIX":              25336,
        "BENETNASH":              67301,
        "BETELGEUSE":             27989,
        "BIRDUN":                 66657,
        "CANOPUS":                30438,
        "CAPELLA":                24608,
        "CAPH":                   746,
        "CASTOR":                 36850,
        "DENEB":                  102098,
        "DENEB KAITOS":           3419,
        "DENEBOLA":               57632,
        "DIPHDA":                 3419,
        "DSCHUBBA":               78401,
        "DUBHE":                  54061,
        "DURRE MENTHOR":          8102,
        "ELNATH":                 25428,
        "ENIF":                   107315,
        "ETAMIN":                 87833,
        "FOMALHAUT":              113368,
        "FORAMEN":                93308,
        "GACRUX":                 61084,
        "GEMMA":                  76267,
        "GIENAH":                 102488,
        "GIRTAB":                 86228,
        "GRUID":                  112122,
        "HADAR":                  68702,
        "HAMAL":                  9884,
        "HERSCHEL'S GARNET STAR": 107259,
        "IZAR":                   72105,
        "KAUS AUSTRALIS":         90185,
        "KOCHAB":                 72607,
        "KOO SHE":                42913,
        "MARCHAB":                113963,
        "MARFIKENT":              71352,
        "MARKAB":                 45941,
        "MEGREZ":                 59774,
        "MEN":                    71860,
        "MENKALINAN":             28360,
        "MENKENT":                68933,
        "MERAK":                  53910,
        "MIAPLACIDUS":            45238,
        "MIMOSA":                 62434,
        "MINTAKA":                25930,
        "MIRA":                   10826,
        "MIRACH":                 5447,
        "MIRFAK":                 15863,
        "MIRZAM":                 30324,
        "MIZAR":                  65378,
        "MUHLIFEIN":              61932,
        "MURZIM":                 30324,
        "NAOS":                   39429,
        "NUNKI":                  92855,
        "PEACOCK":                100751,
        "PHAD":                   58001,
        "PHECDA":                 58001,
        "POLARIS":                11767,
        "POLLUX":                 37826,
        "PROCYON":                37279,
        "RAS ALHAGUE":            86032,
        "RASALHAGUE":             86032,
        "REGOR":                  39953,
        "REGULUS":                49669,
        "RIGEL":                  24436,
        "RIGEL KENT":             71683,
        "RIGIL KENTAURUS":        71683,
        "SABIK":                  84012,
        "SADIRA":                 16537,
        "SADR":                   100453,
        "SAIPH":                  27366,
        "SARGAS":                 86228,
        "SCHEAT":                 113881,
        "SCHEDAR":                3179,
        "SCUTULUM":               45556,
        "SHAULA":                 85927,
        "SIRIUS":                 32349,
        "SIRRAH":                 677,
        "SOUTH STAR":             104382,
        "SPICA":                  65474,
        "SUHAIL":                 44816,
        "THUBAN":                 68756,
        "TOLIMAN":                71683,
        "TSEEN SHE":              93308,
        "TSIH":                   4427,
        "TURAIS":                 45556,
        "VEGA":                   91262,
        "WEI":                    82396,
        "WEZEN":                  34444 } )

    astrobase.AstroBase.STAR_NAMES_TRANSLATIONS.update( {
        astrobase.AstroBase.STARS[ 0 ]   : _( "Achernar" ),
        astrobase.AstroBase.STARS[ 1 ]   : _( "Acrux" ),
        astrobase.AstroBase.STARS[ 2 ]   : _( "Adhara" ),
        astrobase.AstroBase.STARS[ 3 ]   : _( "Agena" ),
        astrobase.AstroBase.STARS[ 4 ]   : _( "Albireo" ),
        astrobase.AstroBase.STARS[ 5 ]   : _( "Alcor" ),
        astrobase.AstroBase.STARS[ 6 ]   : _( "Aldebaran" ),
        astrobase.AstroBase.STARS[ 7 ]   : _( "Alderamin" ),
        astrobase.AstroBase.STARS[ 8 ]   : _( "Algenib" ),
        astrobase.AstroBase.STARS[ 9 ]   : _( "Algieba" ),
        astrobase.AstroBase.STARS[ 10 ]  : _( "Algol" ),
        astrobase.AstroBase.STARS[ 11 ]  : _( "Alhena" ),
        astrobase.AstroBase.STARS[ 12 ]  : _( "Alioth" ),
        astrobase.AstroBase.STARS[ 13 ]  : _( "Alkaid" ),
        astrobase.AstroBase.STARS[ 14 ]  : _( "Almach" ),
        astrobase.AstroBase.STARS[ 15 ]  : _( "Alnair" ),
        astrobase.AstroBase.STARS[ 16 ]  : _( "Alnilam" ),
        astrobase.AstroBase.STARS[ 17 ]  : _( "Alnitak" ),
        astrobase.AstroBase.STARS[ 18 ]  : _( "Alphard" ),
        astrobase.AstroBase.STARS[ 19 ]  : _( "Alphecca" ),
        astrobase.AstroBase.STARS[ 20 ]  : _( "Alpheratz" ),
        astrobase.AstroBase.STARS[ 21 ]  : _( "Altair" ),
        astrobase.AstroBase.STARS[ 22 ]  : _( "Aludra" ),
        astrobase.AstroBase.STARS[ 23 ]  : _( "Ankaa" ),
        astrobase.AstroBase.STARS[ 24 ]  : _( "Antares" ),
        astrobase.AstroBase.STARS[ 25 ]  : _( "Arcturus" ),
        astrobase.AstroBase.STARS[ 26 ]  : _( "Arided" ),
        astrobase.AstroBase.STARS[ 27 ]  : _( "Aridif" ),
        astrobase.AstroBase.STARS[ 28 ]  : _( "Aspidiske" ),
        astrobase.AstroBase.STARS[ 29 ]  : _( "Atria" ),
        astrobase.AstroBase.STARS[ 30 ]  : _( "Avior" ),
        astrobase.AstroBase.STARS[ 31 ]  : _( "Becrux" ),
        astrobase.AstroBase.STARS[ 32 ]  : _( "Bellatrix" ),
        astrobase.AstroBase.STARS[ 33 ]  : _( "Benetnash" ),
        astrobase.AstroBase.STARS[ 34 ]  : _( "Betelgeuse" ),
        astrobase.AstroBase.STARS[ 35 ]  : _( "Birdun" ),
        astrobase.AstroBase.STARS[ 36 ]  : _( "Canopus" ),
        astrobase.AstroBase.STARS[ 37 ]  : _( "Capella" ),
        astrobase.AstroBase.STARS[ 38 ]  : _( "Caph" ),
        astrobase.AstroBase.STARS[ 39 ]  : _( "Castor" ),
        astrobase.AstroBase.STARS[ 40 ]  : _( "Deneb Kaitos" ),
        astrobase.AstroBase.STARS[ 41 ]  : _( "Deneb" ),
        astrobase.AstroBase.STARS[ 42 ]  : _( "Denebola" ),
        astrobase.AstroBase.STARS[ 43 ]  : _( "Diphda" ),
        astrobase.AstroBase.STARS[ 44 ]  : _( "Dschubba" ),
        astrobase.AstroBase.STARS[ 45 ]  : _( "Dubhe" ),
        astrobase.AstroBase.STARS[ 46 ]  : _( "Durre Menthor" ),
        astrobase.AstroBase.STARS[ 47 ]  : _( "Elnath" ),
        astrobase.AstroBase.STARS[ 48 ]  : _( "Enif" ),
        astrobase.AstroBase.STARS[ 49 ]  : _( "Etamin" ),
        astrobase.AstroBase.STARS[ 50 ]  : _( "Fomalhaut" ),
        astrobase.AstroBase.STARS[ 51 ]  : _( "Foramen" ),
        astrobase.AstroBase.STARS[ 52 ]  : _( "Gacrux" ),
        astrobase.AstroBase.STARS[ 53 ]  : _( "Gemma" ),
        astrobase.AstroBase.STARS[ 54 ]  : _( "Gienah" ),
        astrobase.AstroBase.STARS[ 55 ]  : _( "Girtab" ),
        astrobase.AstroBase.STARS[ 56 ]  : _( "Gruid" ),
        astrobase.AstroBase.STARS[ 57 ]  : _( "Hadar" ),
        astrobase.AstroBase.STARS[ 58 ]  : _( "Hamal" ),
        astrobase.AstroBase.STARS[ 59 ]  : _( "Herschel's Garnet Star" ),
        astrobase.AstroBase.STARS[ 60 ]  : _( "Izar" ),
        astrobase.AstroBase.STARS[ 61 ]  : _( "Kaus Australis" ),
        astrobase.AstroBase.STARS[ 62 ]  : _( "Kochab" ),
        astrobase.AstroBase.STARS[ 63 ]  : _( "Koo She" ),
        astrobase.AstroBase.STARS[ 64 ]  : _( "Marchab" ),
        astrobase.AstroBase.STARS[ 65 ]  : _( "Marfikent" ),
        astrobase.AstroBase.STARS[ 66 ]  : _( "Markab" ),
        astrobase.AstroBase.STARS[ 67 ]  : _( "Megrez" ),
        astrobase.AstroBase.STARS[ 68 ]  : _( "Men" ),
        astrobase.AstroBase.STARS[ 69 ]  : _( "Menkalinan" ),
        astrobase.AstroBase.STARS[ 70 ]  : _( "Menkent" ),
        astrobase.AstroBase.STARS[ 71 ]  : _( "Merak" ),
        astrobase.AstroBase.STARS[ 72 ]  : _( "Miaplacidus" ),
        astrobase.AstroBase.STARS[ 73 ]  : _( "Mimosa" ),
        astrobase.AstroBase.STARS[ 74 ]  : _( "Mintaka" ),
        astrobase.AstroBase.STARS[ 75 ]  : _( "Mira" ),
        astrobase.AstroBase.STARS[ 76 ]  : _( "Mirach" ),
        astrobase.AstroBase.STARS[ 77 ]  : _( "Mirfak" ),
        astrobase.AstroBase.STARS[ 78 ]  : _( "Mirzam" ),
        astrobase.AstroBase.STARS[ 79 ]  : _( "Mizar" ),
        astrobase.AstroBase.STARS[ 80 ]  : _( "Muhlifein" ),
        astrobase.AstroBase.STARS[ 81 ]  : _( "Murzim" ),
        astrobase.AstroBase.STARS[ 82 ]  : _( "Naos" ),
        astrobase.AstroBase.STARS[ 83 ]  : _( "Nunki" ),
        astrobase.AstroBase.STARS[ 84 ]  : _( "Peacock" ),
        astrobase.AstroBase.STARS[ 85 ]  : _( "Phad" ),
        astrobase.AstroBase.STARS[ 86 ]  : _( "Phecda" ),
        astrobase.AstroBase.STARS[ 87 ]  : _( "Polaris" ),
        astrobase.AstroBase.STARS[ 88 ]  : _( "Pollux" ),
        astrobase.AstroBase.STARS[ 89 ]  : _( "Procyon" ),
        astrobase.AstroBase.STARS[ 90 ]  : _( "Ras Alhague" ),
        astrobase.AstroBase.STARS[ 91 ]  : _( "Rasalhague" ),
        astrobase.AstroBase.STARS[ 92 ]  : _( "Regor" ),
        astrobase.AstroBase.STARS[ 93 ]  : _( "Regulus" ),
        astrobase.AstroBase.STARS[ 94 ]  : _( "Rigel Kent" ),
        astrobase.AstroBase.STARS[ 95 ]  : _( "Rigel" ),
        astrobase.AstroBase.STARS[ 96 ]  : _( "Rigil Kentaurus" ),
        astrobase.AstroBase.STARS[ 97 ]  : _( "Sabik" ),
        astrobase.AstroBase.STARS[ 98 ]  : _( "Sadira" ),
        astrobase.AstroBase.STARS[ 99 ]  : _( "Sadr" ),
        astrobase.AstroBase.STARS[ 100 ] : _( "Saiph" ),
        astrobase.AstroBase.STARS[ 101 ] : _( "Sargas" ),
        astrobase.AstroBase.STARS[ 102 ] : _( "Scheat" ),
        astrobase.AstroBase.STARS[ 103 ] : _( "Schedar" ),
        astrobase.AstroBase.STARS[ 104 ] : _( "Scutulum" ),
        astrobase.AstroBase.STARS[ 105 ] : _( "Shaula" ),
        astrobase.AstroBase.STARS[ 106 ] : _( "Sirius" ),
        astrobase.AstroBase.STARS[ 107 ] : _( "Sirrah" ),
        astrobase.AstroBase.STARS[ 108 ] : _( "South Star" ),
        astrobase.AstroBase.STARS[ 109 ] : _( "Spica" ),
        astrobase.AstroBase.STARS[ 110 ] : _( "Suhail" ),
        astrobase.AstroBase.STARS[ 111 ] : _( "Thuban" ),
        astrobase.AstroBase.STARS[ 112 ] : _( "Toliman" ),
        astrobase.AstroBase.STARS[ 113 ] : _( "Tseen She" ),
        astrobase.AstroBase.STARS[ 114 ] : _( "Tsih" ),
        astrobase.AstroBase.STARS[ 115 ] : _( "Turais" ),
        astrobase.AstroBase.STARS[ 116 ] : _( "Vega" ),
        astrobase.AstroBase.STARS[ 117 ] : _( "Wei" ),
        astrobase.AstroBase.STARS[ 118 ] : _( "Wezen" ) } )

    # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
    astrobase.AstroBase.STAR_TAGS_TRANSLATIONS.update( {
        astrobase.AstroBase.STARS[ 0 ]   : _( "ACHERNAR" ),
        astrobase.AstroBase.STARS[ 1 ]   : _( "ACRUX" ),
        astrobase.AstroBase.STARS[ 2 ]   : _( "ADHARA" ),
        astrobase.AstroBase.STARS[ 3 ]   : _( "AGENA" ),
        astrobase.AstroBase.STARS[ 4 ]   : _( "ALBIREO" ),
        astrobase.AstroBase.STARS[ 5 ]   : _( "ALCOR" ),
        astrobase.AstroBase.STARS[ 6 ]   : _( "ALDEBARAN" ),
        astrobase.AstroBase.STARS[ 7 ]   : _( "ALDERAMIN" ),
        astrobase.AstroBase.STARS[ 8 ]   : _( "ALGENIB" ),
        astrobase.AstroBase.STARS[ 9 ]   : _( "ALGIEBA" ),
        astrobase.AstroBase.STARS[ 10 ]  : _( "ALGOL" ),
        astrobase.AstroBase.STARS[ 11 ]  : _( "ALHENA" ),
        astrobase.AstroBase.STARS[ 12 ]  : _( "ALIOTH" ),
        astrobase.AstroBase.STARS[ 13 ]  : _( "ALKAID" ),
        astrobase.AstroBase.STARS[ 14 ]  : _( "ALMACH" ),
        astrobase.AstroBase.STARS[ 15 ]  : _( "ALNAIR" ),
        astrobase.AstroBase.STARS[ 16 ]  : _( "ALNILAM" ),
        astrobase.AstroBase.STARS[ 17 ]  : _( "ALNITAK" ),
        astrobase.AstroBase.STARS[ 18 ]  : _( "ALPHARD" ),
        astrobase.AstroBase.STARS[ 19 ]  : _( "ALPHECCA" ),
        astrobase.AstroBase.STARS[ 20 ]  : _( "ALPHERATZ" ),
        astrobase.AstroBase.STARS[ 21 ]  : _( "ALTAIR" ),
        astrobase.AstroBase.STARS[ 22 ]  : _( "ALUDRA" ),
        astrobase.AstroBase.STARS[ 23 ]  : _( "ANKAA" ),
        astrobase.AstroBase.STARS[ 24 ]  : _( "ANTARES" ),
        astrobase.AstroBase.STARS[ 25 ]  : _( "ARCTURUS" ),
        astrobase.AstroBase.STARS[ 26 ]  : _( "ARIDED" ),
        astrobase.AstroBase.STARS[ 27 ]  : _( "ARIDIF" ),
        astrobase.AstroBase.STARS[ 28 ]  : _( "ASPIDISKE" ),
        astrobase.AstroBase.STARS[ 29 ]  : _( "ATRIA" ),
        astrobase.AstroBase.STARS[ 30 ]  : _( "AVIOR" ),
        astrobase.AstroBase.STARS[ 31 ]  : _( "BECRUX" ),
        astrobase.AstroBase.STARS[ 32 ]  : _( "BELLATRIX" ),
        astrobase.AstroBase.STARS[ 33 ]  : _( "BENETNASH" ),
        astrobase.AstroBase.STARS[ 34 ]  : _( "BETELGEUSE" ),
        astrobase.AstroBase.STARS[ 35 ]  : _( "BIRDUN" ),
        astrobase.AstroBase.STARS[ 36 ]  : _( "CANOPUS" ),
        astrobase.AstroBase.STARS[ 37 ]  : _( "CAPELLA" ),
        astrobase.AstroBase.STARS[ 38 ]  : _( "CAPH" ),
        astrobase.AstroBase.STARS[ 39 ]  : _( "CASTOR" ),
        astrobase.AstroBase.STARS[ 40 ]  : _( "DENEB KAITOS" ),
        astrobase.AstroBase.STARS[ 41 ]  : _( "DENEB" ),
        astrobase.AstroBase.STARS[ 42 ]  : _( "DENEBOLA" ),
        astrobase.AstroBase.STARS[ 43 ]  : _( "DIPHDA" ),
        astrobase.AstroBase.STARS[ 44 ]  : _( "DSCHUBBA" ),
        astrobase.AstroBase.STARS[ 45 ]  : _( "DUBHE" ),
        astrobase.AstroBase.STARS[ 46 ]  : _( "DURRE MENTHOR" ),
        astrobase.AstroBase.STARS[ 47 ]  : _( "ELNATH" ),
        astrobase.AstroBase.STARS[ 48 ]  : _( "ENIF" ),
        astrobase.AstroBase.STARS[ 49 ]  : _( "ETAMIN" ),
        astrobase.AstroBase.STARS[ 50 ]  : _( "FOMALHAUT" ),
        astrobase.AstroBase.STARS[ 51 ]  : _( "FORAMEN" ),
        astrobase.AstroBase.STARS[ 52 ]  : _( "GACRUX" ),
        astrobase.AstroBase.STARS[ 53 ]  : _( "GEMMA" ),
        astrobase.AstroBase.STARS[ 54 ]  : _( "GIENAH" ),
        astrobase.AstroBase.STARS[ 55 ]  : _( "GIRTAB" ),
        astrobase.AstroBase.STARS[ 56 ]  : _( "GRUID" ),
        astrobase.AstroBase.STARS[ 57 ]  : _( "HADAR" ),
        astrobase.AstroBase.STARS[ 58 ]  : _( "HAMAL" ),
        astrobase.AstroBase.STARS[ 59 ]  : _( "HERSCHEL'S GARNET STAR" ),
        astrobase.AstroBase.STARS[ 60 ]  : _( "IZAR" ),
        astrobase.AstroBase.STARS[ 61 ]  : _( "KAUS AUSTRALIS" ),
        astrobase.AstroBase.STARS[ 62 ]  : _( "KOCHAB" ),
        astrobase.AstroBase.STARS[ 63 ]  : _( "KOO SHE" ),
        astrobase.AstroBase.STARS[ 64 ]  : _( "MARCHAB" ),
        astrobase.AstroBase.STARS[ 65 ]  : _( "MARFIKENT" ),
        astrobase.AstroBase.STARS[ 66 ]  : _( "MARKAB" ),
        astrobase.AstroBase.STARS[ 67 ]  : _( "MEGREZ" ),
        astrobase.AstroBase.STARS[ 68 ]  : _( "MEN" ),
        astrobase.AstroBase.STARS[ 69 ]  : _( "MENKALINAN" ),
        astrobase.AstroBase.STARS[ 70 ]  : _( "MENKENT" ),
        astrobase.AstroBase.STARS[ 71 ]  : _( "MERAK" ),
        astrobase.AstroBase.STARS[ 72 ]  : _( "MIAPLACIDUS" ),
        astrobase.AstroBase.STARS[ 73 ]  : _( "MIMOSA" ),
        astrobase.AstroBase.STARS[ 74 ]  : _( "MINTAKA" ),
        astrobase.AstroBase.STARS[ 75 ]  : _( "MIRA" ),
        astrobase.AstroBase.STARS[ 76 ]  : _( "MIRACH" ),
        astrobase.AstroBase.STARS[ 77 ]  : _( "MIRFAK" ),
        astrobase.AstroBase.STARS[ 78 ]  : _( "MIRZAM" ),
        astrobase.AstroBase.STARS[ 79 ]  : _( "MIZAR" ),
        astrobase.AstroBase.STARS[ 80 ]  : _( "MUHLIFEIN" ),
        astrobase.AstroBase.STARS[ 81 ]  : _( "MURZIM" ),
        astrobase.AstroBase.STARS[ 82 ]  : _( "NAOS" ),
        astrobase.AstroBase.STARS[ 83 ]  : _( "NUNKI" ),
        astrobase.AstroBase.STARS[ 84 ]  : _( "PEACOCK" ),
        astrobase.AstroBase.STARS[ 85 ]  : _( "PHAD" ),
        astrobase.AstroBase.STARS[ 86 ]  : _( "PHECDA" ),
        astrobase.AstroBase.STARS[ 87 ]  : _( "POLARIS" ),
        astrobase.AstroBase.STARS[ 88 ]  : _( "POLLUX" ),
        astrobase.AstroBase.STARS[ 89 ]  : _( "PROCYON" ),
        astrobase.AstroBase.STARS[ 90 ]  : _( "RAS ALHAGUE" ),
        astrobase.AstroBase.STARS[ 91 ]  : _( "RASALHAGUE" ),
        astrobase.AstroBase.STARS[ 92 ]  : _( "REGOR" ),
        astrobase.AstroBase.STARS[ 93 ]  : _( "REGULUS" ),
        astrobase.AstroBase.STARS[ 94 ]  : _( "RIGEL KENT" ),
        astrobase.AstroBase.STARS[ 95 ]  : _( "RIGEL" ),
        astrobase.AstroBase.STARS[ 96 ]  : _( "RIGIL KENTAURUS" ),
        astrobase.AstroBase.STARS[ 97 ]  : _( "SABIK" ),
        astrobase.AstroBase.STARS[ 98 ]  : _( "SADIRA" ),
        astrobase.AstroBase.STARS[ 99 ]  : _( "SADR" ),
        astrobase.AstroBase.STARS[ 100 ] : _( "SAIPH" ),
        astrobase.AstroBase.STARS[ 101 ] : _( "SARGAS" ),
        astrobase.AstroBase.STARS[ 102 ] : _( "SCHEAT" ),
        astrobase.AstroBase.STARS[ 103 ] : _( "SCHEDAR" ),
        astrobase.AstroBase.STARS[ 104 ] : _( "SCUTULUM" ),
        astrobase.AstroBase.STARS[ 105 ] : _( "SHAULA" ),
        astrobase.AstroBase.STARS[ 106 ] : _( "SIRIUS" ),
        astrobase.AstroBase.STARS[ 107 ] : _( "SIRRAH" ),
        astrobase.AstroBase.STARS[ 108 ] : _( "SOUTH STAR" ),
        astrobase.AstroBase.STARS[ 109 ] : _( "SPICA" ),
        astrobase.AstroBase.STARS[ 110 ] : _( "SUHAIL" ),
        astrobase.AstroBase.STARS[ 111 ] : _( "THUBAN" ),
        astrobase.AstroBase.STARS[ 112 ] : _( "TOLIMAN" ),
        astrobase.AstroBase.STARS[ 113 ] : _( "TSEEN SHE" ),
        astrobase.AstroBase.STARS[ 114 ] : _( "TSIH" ),
        astrobase.AstroBase.STARS[ 115 ] : _( "TURAIS" ),
        astrobase.AstroBase.STARS[ 116 ] : _( "VEGA" ),
        astrobase.AstroBase.STARS[ 117 ] : _( "WEI" ),
        astrobase.AstroBase.STARS[ 118 ] : _( "WEZEN" ) } )


    # Taken from ephem/cities.py as Skyfield will not provide a list of cities.
    #    https://github.com/skyfielders/python-skyfield/issues/316
    _city_data = {
        "Abu Dhabi" :        ( 24.4666667, 54.3666667, 6.296038 ),
        "Adelaide" :         ( -34.9305556, 138.6205556, 49.098354 ),
        "Almaty" :           ( 43.255058, 76.912628, 785.522156 ),
        "Amsterdam" :        ( 52.3730556, 4.8922222, 14.975505 ),
        "Antwerp" :          ( 51.21992, 4.39625, 7.296879 ),
        "Arhus" :            ( 56.162939, 10.203921, 26.879421 ),
        "Athens" :           ( 37.97918, 23.716647, 47.597061 ),
        "Atlanta" :          ( 33.7489954, -84.3879824, 319.949738 ),
        "Auckland" :         ( -36.8484597, 174.7633315, 21.000000 ),
        "Baltimore" :        ( 39.2903848, -76.6121893, 10.258920 ),
        "Bangalore" :        ( 12.9715987, 77.5945627, 911.858398 ),
        "Bangkok" :          ( 13.7234186, 100.4762319, 4.090096 ),
        "Barcelona" :        ( 41.387917, 2.1699187, 19.991053 ),
        "Beijing" :          ( 39.904214, 116.407413, 51.858883 ),
        "Berlin" :           ( 52.5234051, 13.4113999, 45.013939 ),
        "Birmingham" :       ( 52.4829614, -1.893592, 141.448563 ),
        "Bogota" :           ( 4.5980556, -74.0758333, 2614.037109 ),
        "Bologna" :          ( 44.4942191, 11.3464815, 72.875923 ),
        "Boston" :           ( 42.3584308, -71.0597732, 15.338848 ),
        "Bratislava" :       ( 48.1483765, 17.1073105, 155.813446 ),
        "Brazilia" :         ( -14.235004, -51.92528, 259.063477 ),
        "Brisbane" :         ( -27.4709331, 153.0235024, 28.163914 ),
        "Brussels" :         ( 50.8503, 4.35171, 26.808620 ),
        "Bucharest" :        ( 44.437711, 26.097367, 80.407768 ),
        "Budapest" :         ( 47.4984056, 19.0407578, 106.463295 ),
        "Buenos Aires" :     ( -34.6084175, -58.3731613, 40.544090 ),
        "Cairo" :            ( 30.064742, 31.249509, 20.248013 ),
        "Calgary" :          ( 51.045, -114.0572222, 1046.000000 ),
        "Cape Town" :        ( -33.924788, 18.429916, 5.838447 ),
        "Caracas" :          ( 10.491016, -66.902061, 974.727417 ),
        "Chicago" :          ( 41.8781136, -87.6297982, 181.319290 ),
        "Cleveland" :        ( 41.4994954, -81.6954088, 198.879639 ),
        "Cologne" :          ( 50.9406645, 6.9599115, 59.181450 ),
        "Colombo" :          ( 6.927468, 79.848358, 9.969995 ),
        "Columbus" :         ( 39.9611755, -82.9987942, 237.651932 ),
        "Copenhagen" :       ( 55.693403, 12.583046, 6.726723 ),
        "Dallas" :           ( 32.802955, -96.769923, 154.140625 ),
        "Detroit" :          ( 42.331427, -83.0457538, 182.763428 ),
        "Dresden" :          ( 51.0509912, 13.7336335, 114.032356 ),
        "Dubai" :            ( 25.2644444, 55.3116667, 8.029230 ),
        "Dublin" :           ( 53.344104, -6.2674937, 8.214323 ),
        "Dusseldorf" :       ( 51.2249429, 6.7756524, 43.204800 ),
        "Edinburgh" :        ( 55.9501755, -3.1875359, 84.453995 ),
        "Frankfurt" :        ( 50.1115118, 8.6805059, 106.258285 ),
        "Geneva" :           ( 46.2057645, 6.141593, 379.026245 ),
        "Genoa" :            ( 44.4070624, 8.9339889, 35.418076 ),
        "Glasgow" :          ( 55.8656274, -4.2572227, 38.046883 ),
        "Gothenburg" :       ( 57.6969943, 11.9865, 15.986326 ),
        "Guangzhou" :        ( 23.129163, 113.264435, 18.892920 ),
        "Hamburg" :          ( 53.5538148, 9.9915752, 5.104634 ),
        "Hanoi" :            ( 21.0333333, 105.85, 20.009024 ),
        "Helsinki" :         ( 60.1698125, 24.9382401, 7.153307 ),
        "Ho Chi Minh City" : ( 10.75918, 106.662498, 10.757121 ),
        "Hong Kong" :        ( 22.396428, 114.109497, 321.110260 ),
        "Houston" :          ( 29.7628844, -95.3830615, 6.916622 ),
        "Istanbul" :         ( 41.00527, 28.97696, 37.314278 ),
        "Jakarta" :          ( -6.211544, 106.845172, 10.218226 ),
        "Johannesburg" :     ( -26.1704415, 27.9717606, 1687.251099 ),
        "Kansas City" :      ( 39.1066667, -94.6763889, 274.249390 ),
        "Kiev" :             ( 50.45, 30.5233333, 157.210175 ),
        "Kuala Lumpur" :     ( 3.139003, 101.686855, 52.271698 ),
        "Leeds" :            ( 53.7996388, -1.5491221, 47.762367 ),
        "Lille" :            ( 50.6371834, 3.0630174, 28.139490 ),
        "Lima" :             ( -12.0433333, -77.0283333, 154.333740 ),
        "Lisbon" :           ( 38.7070538, -9.1354884, 2.880179 ),
        "London" :           ( 51.5001524, -0.1262362, 14.605533 ),
        "Los Angeles" :      ( 34.0522342, -118.2436849, 86.847092 ),
        "Luxembourg" :       ( 49.815273, 6.129583, 305.747925 ),
        "Lyon" :             ( 45.767299, 4.8343287, 182.810547 ),
        "Madrid" :           ( 40.4166909, -3.7003454, 653.005005 ),
        "Manchester" :       ( 53.4807125, -2.2343765, 57.892406 ),
        "Manila" :           ( 14.5833333, 120.9666667, 3.041384 ),
        "Marseille" :        ( 43.2976116, 5.3810421, 24.785774 ),
        "Melbourne" :        ( -37.8131869, 144.9629796, 27.000000 ),
        "Mexico City" :      ( 19.4270499, -99.1275711, 2228.146484 ),
        "Miami" :            ( 25.7889689, -80.2264393, 0.946764 ),
        "Milan" :            ( 45.4636889, 9.1881408, 122.246513 ),
        "Minneapolis" :      ( 44.9799654, -93.2638361, 253.002655 ),
        "Montevideo" :       ( -34.8833333, -56.1666667, 45.005032 ),
        "Montreal" :         ( 45.5088889, -73.5541667, 16.620916 ),
        "Moscow" :           ( 55.755786, 37.617633, 151.189835 ),
        "Mumbai" :           ( 19.0176147, 72.8561644, 12.408822 ),
        "Munich" :           ( 48.1391265, 11.5801863, 523.000000 ),
        "New Delhi" :        ( 28.635308, 77.22496, 213.999054 ),
        "New York" :         ( 40.7143528, -74.0059731, 9.775694 ),
        "Osaka" :            ( 34.6937378, 135.5021651, 16.347811 ),
        "Oslo" :             ( 59.9127263, 10.7460924, 10.502326 ),
        "Paris" :            ( 48.8566667, 2.3509871, 35.917042 ),
        "Philadelphia" :     ( 39.952335, -75.163789, 12.465688 ),
        "Prague" :           ( 50.0878114, 14.4204598, 191.103485 ),
        "Richmond" :         ( 37.542979, -77.469092, 63.624462 ),
        "Rio de Janeiro" :   ( -22.9035393, -43.2095869, 9.521935 ),
        "Riyadh" :           ( 24.6880015, 46.7224333, 613.475281 ),
        "Rome" :             ( 41.8954656, 12.4823243, 19.704413 ),
        "Rotterdam" :        ( 51.924216, 4.481776, 2.766272 ),
        "San Francisco" :    ( 37.7749295, -122.4194155, 15.557819 ),
        "Santiago" :         ( -33.4253598, -70.5664659, 665.926880 ),
        "Sao Paulo" :        ( -23.5489433, -46.6388182, 760.344849 ),
        "Seattle" :          ( 47.6062095, -122.3320708, 53.505501 ),
        "Seoul" :            ( 37.566535, 126.9779692, 41.980915 ),
        "Shanghai" :         ( 31.230393, 121.473704, 15.904707 ),
        "Singapore" :        ( 1.352083, 103.819836, 57.821636 ),
        "St. Petersburg" :   ( 59.939039, 30.315785, 11.502971 ),
        "Stockholm" :        ( 59.3327881, 18.0644881, 25.595907 ),
        "Stuttgart" :        ( 48.7771056, 9.1807688, 249.205185 ),
        "Sydney" :           ( -33.8599722, 151.2111111, 3.341026 ),
        "Taipei" :           ( 25.091075, 121.5598345, 32.288563 ),
        "Tashkent" :         ( 41.2666667, 69.2166667, 430.668427 ),
        "Tehran" :           ( 35.6961111, 51.4230556, 1180.595947 ),
        "Tel Aviv" :         ( 32.0599254, 34.7851264, 21.114218 ),
        "The Hague" :        ( 52.0698576, 4.2911114, 3.686689 ),
        "Tijuana" :          ( 32.533489, -117.018204, 22.712011 ),
        "Tokyo" :            ( 35.6894875, 139.6917064, 37.145370 ),
        "Toronto" :          ( 43.6525, -79.3816667, 90.239403 ),
        "Turin" :            ( 45.0705621, 7.6866186, 234.000000 ),
        "Utrecht" :          ( 52.0901422, 5.1096649, 7.720881 ),
        "Vancouver" :        ( 49.248523, -123.1088, 70.145927 ),
        "Vienna" :           ( 48.20662, 16.38282, 170.493149 ),
        "Warsaw" :           ( 52.2296756, 21.0122287, 115.027786 ),
        "Washington" :       ( 38.8951118, -77.0363658, 7.119641 ),
        "Wellington" :       ( -41.2924945, 174.7732353, 17.000000 ),
        "Zurich" :           ( 47.3833333, 8.5333333, 405.500916 ) }


    @staticmethod
    def calculate( utcNow,
                   latitude, longitude, elevation,
                   planets,
                   stars,
                   satellites, satelliteData,
                   comets, cometData,
                   minorPlanets, minorPlanetData,
                   magnitudeMaximum ):

        data = { }
        timeScale = load.timescale( builtin = True )
        topos = Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )
        ephemerisPlanets = load( AstroSkyfield.__EPHEMERIS_PLANETS )

        AstroSkyfield.__calculateMoon( utcNow, data, timeScale, topos, ephemerisPlanets )
        AstroSkyfield.__calculateSun( utcNow, data, timeScale, topos, ephemerisPlanets )
        AstroSkyfield.__calculatePlanets( utcNow, data, timeScale, topos, ephemerisPlanets, planets, magnitudeMaximum )

        with load.open( AstroSkyfield.__EPHEMERIS_STARS ) as f:
            ephemerisStars = hipparcos.load_dataframe( f )

        AstroSkyfield.__calculateStars( utcNow, data, timeScale, topos, ephemerisPlanets, ephemerisStars, stars, magnitudeMaximum )

        AstroSkyfield.__calculateCometsOrMinorPlanets( utcNow, data, timeScale, topos, ephemerisPlanets,
                                                       astrobase.AstroBase.BodyType.COMET, comets, cometData, magnitudeMaximum )

        AstroSkyfield.__calculateCometsOrMinorPlanets( utcNow, data, timeScale, topos, ephemerisPlanets,
                                                       astrobase.AstroBase.BodyType.MINOR_PLANET, minorPlanets, minorPlanetData, magnitudeMaximum )

        AstroSkyfield.__calculateSatellites( utcNow, data, timeScale, topos, ephemerisPlanets, satellites, satelliteData )

        return data


    @staticmethod
    def getCities(): return sorted( AstroSkyfield._city_data.keys(), key = locale.strxfrm )


    @staticmethod
    def getLatitudeLongitudeElevation( city ): return AstroSkyfield._city_data.get( city )[ 0 ], \
                                                      AstroSkyfield._city_data.get( city )[ 1 ], \
                                                      AstroSkyfield._city_data.get( city )[ 2 ]


    @staticmethod
    def getOrbitalElementsLessThanMagnitude( orbitalElementData, magnitudeMaximum, utcNow, latitude, longitude, elevation ):
        timeScale = load.timescale( builtin = True )
        t = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
        ephemerisPlanets = load( AstroSkyfield.__EPHEMERIS_PLANETS )
        sun = ephemerisPlanets[ "sun" ]
        earth = ephemerisPlanets[ "earth" ]
        topos = Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )
        alt, az, earthSunDistance = ( earth + topos ).at( t ).observe( sun ).apparent().altaz()
        results = { }
        for key in orbitalElementData:
            with io.BytesIO( orbitalElementData[ key ].getData().encode() ) as f:
                if orbitalElementData[ key ].getDataType() == orbitalelement.OE.DataType.SKYFIELD_COMET:
                    dataframe = mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )
                    body = sun + mpc.comet_orbit( dataframe.loc[ orbitalElementData[ key ].getName() ], timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )

                else:
                    dataframe = mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
                    body = sun + mpc.mpcorb_orbit( dataframe.loc[ orbitalElementData[ key ].getName() ], timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )
 
            ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()
            ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()
 
            apparentMagnitude = astrobase.AstroBase.getApparentMagnitude_HG( dataframe.loc[ orbitalElementData[ key ].getName() ][ "magnitude_H" ], 
                                                                             dataframe.loc[ orbitalElementData[ key ].getName() ][ "magnitude_G" ], 
                                                                             earthBodyDistance.au, 
                                                                             sunBodyDistance.au, 
                                                                             earthSunDistance.au )

            if apparentMagnitude >= astrobase.AstroBase.MAGNITUDE_MINIMUM and apparentMagnitude <= magnitudeMaximum:
                results[ key ] = orbitalElementData[ key ]

        print( len( orbitalElementData ), len( results ) )#TODO Testing
        return results


#TODO Test for getting comet and minor planet computations without using a dataframe.
# Unfortunately the dataframe makes little difference.  The time is consumed deeper within Skyfield.
    @staticmethod
#     def getOrbitalElementsLessThanMagnitudeWithoutDataframe( orbitalElementData, magnitudeMaximum, utcNow, latitude, longitude, elevation ):
#         timeScale = load.timescale( builtin = True )
#         t = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
#         ephemerisPlanets = load( AstroSkyfield.__EPHEMERIS_PLANETS )
#         sun = ephemerisPlanets[ "sun" ]
#         earth = ephemerisPlanets[ "earth" ]
#         topos = Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )
#         alt, az, earthSunDistance = ( earth + topos ).at( t ).observe( sun ).apparent().altaz()
#         results = { }
#         for key in orbitalElementData:
#             if orbitalElementData[ key ].getDataType() == orbitalelement.OE.DataType.SKYFIELD_COMET:
#                 body = sun + mpc.comet_orbit_without_dataframe( orbitalElementData[ key ].getData(), timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )
# 
#             else:
#                 pass
# 
#             ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()
#             ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()
# 
#             apparentMagnitude = astrobase.AstroBase.getApparentMagnitude_HG( float( orbitalElementData[ key ].getData()[ 91 : 95 + 1 ] ), 
#                                                                              float( orbitalElementData[ key ].getData()[ 96 : 100 + 1 ] ), 
#                                                                              earthBodyDistance.au, 
#                                                                              sunBodyDistance.au, 
#                                                                              earthSunDistance.au )
# 
# 
#             if apparentMagnitude >= astrobase.AstroBase.MAGNITUDE_MINIMUM and apparentMagnitude <= magnitudeMaximum:
#                 results[ key ] = orbitalElementData[ key ]
# 
#         return results


    #TODO Used to test without using a dataframe...needs to be pasted into skyfield's mpc.py
#     def comet_orbit_without_dataframe( data, ts, gm_km3_s2 ):
#         e = float( data[ 41 : 49 + 1 ] )
#         if e == 1.0:
#             p = float( data[ 30 : 39 + 1 ] ) / 2
#     
#         else:
#             a = float( data[ 30 : 39 + 1 ] ) / ( 1.0 - e )
#             p = a * ( 1.0 - e * e )
#     
#         t_perihelion = ts.tt( int( data[ 14 : 18 + 1 ] ), int( data[ 19 : 21 + 1 ] ), float( data[ 22 : 29 + 1 ] ) )
#     
#         comet = _KeplerOrbit._from_mean_anomaly(
#             p,
#             e,
#             float( data[ 71 : 79 + 1 ] ),
#             float( data[ 61 : 69 + 1 ] ),
#             float( data[ 51 : 59 + 1 ] ),
#             0.0,
#             t_perihelion,
#             gm_km3_s2,
#             10,
#             data[ 102 : 158 + 1 ],
#         )
#     
#         comet._rotation = inertial_frames[ "ECLIPJ2000" ].T
#         return comet


    @staticmethod
    def getCredit(): return _( "Calculations courtesy of Skyfield. https://rhodesmill.org/skyfield" )


    @staticmethod
    def getAvailabilityMessage():
        message = None
        if not available:
            message = _( "Skyfield could not be found. Install using:\n\n" + \
                         "sudo apt-get install -y python3-pip\nsudo pip3 install --upgrade jplephem numpy pandas pip pytz skyfield" )
        return message


    # http://www.ga.gov.au/geodesy/astro/moonrise.jsp
    # http://futureboy.us/fsp/moon.fsp
    # http://www.geoastro.de/moondata/index.html
    # http://www.geoastro.de/SME/index.htm
    # http://www.geoastro.de/elevazmoon/index.htm
    # http://www.geoastro.de/altazsunmoon/index.htm
    # http://www.geoastro.de/sundata/index.html
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    @staticmethod
    def __calculateMoon( utcNow, data, timeScale, topos, ephemerisPlanets ):
        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        moon = ephemerisPlanets[ AstroSkyfield.__MOON ]

        t0 = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
        illumination = int( almanac.fraction_illuminated( ephemerisPlanets, AstroSkyfield.__MOON, t0 ) * 100 )
        data[ key + ( astrobase.AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( illumination ) # Needed for icon.

        observer = ( ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ] + topos )
        sunRA, sunDec, earthDistance = observer.at( t0 ).observe( ephemerisPlanets[ AstroSkyfield.__SUN ] ).apparent().radec()
        moonRA, moonDec, earthDistance = observer.at( t0 ).observe( moon ).apparent().radec()
        latitude, longitude = AstroSkyfield.__getLatitudeLongitude( observer )
        brightLimb = astrobase.AstroBase.getZenithAngleOfBrightLimb( utcNow, sunRA.radians, sunDec.radians, moonRA.radians, moonDec.radians, latitude, longitude )
        data[ key + ( astrobase.AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( brightLimb ) # Needed for icon.

        t1 = timeScale.utc( utcNow.year, utcNow.month, utcNow.day + 31 )
        t, y = almanac.find_discrete( t0, t1, almanac.moon_phases( ephemerisPlanets ) )
        moonPhases = [ almanac.MOON_PHASES[ yi ] for yi in y ]
        moonPhaseDateTimes = t.utc_datetime()
        nextNewMoonDateTime = moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 0 ] ) ) ] # New moon.
        nextFullMoonDateTime = moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 2 ] ) ) ] # Full moon.
        lunarPhase = astrobase.AstroBase.getLunarPhase( int( float ( illumination ) ), nextFullMoonDateTime, nextNewMoonDateTime )
        data[ key + ( astrobase.AstroBase.DATA_TAG_PHASE, ) ] = lunarPhase # Need for notification.

        neverUp = AstroSkyfield.__calculateCommon( utcNow, data, timeScale, topos, ephemerisPlanets,
                                                   moon, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )

        if not neverUp:
            data[ key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 1 ] ) ) ] )
            data[ key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 2 ] ) ) ] )
            data[ key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 3 ] ) ) ] )
            data[ key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 0 ] ) ) ] )

            astrobase.AstroBase.getEclipse( utcNow, data, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )


    @staticmethod
    def __calculateSun( utcNow, data, timeScale, topos, ephemerisPlanets ):
        neverUp = AstroSkyfield.__calculateCommon( utcNow, data, timeScale, topos, ephemerisPlanets,
                                                   ephemerisPlanets[ AstroSkyfield.__SUN ], astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )

        if not neverUp:
            key = ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )
            t0 = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
            t1 = timeScale.utc( utcNow.year, utcNow.month + 7 )
            t, y = almanac.find_discrete( t0, t1, almanac.seasons( ephemerisPlanets ) )
            t = t.utc_datetime()
            if almanac.SEASON_EVENTS[ 0 ] in almanac.SEASON_EVENTS[ y[ 0 ] ] or almanac.SEASON_EVENTS[ 2 ] in almanac.SEASON_EVENTS[ y[ 0 ] ]:
                data[ key + ( astrobase.AstroBase.DATA_TAG_EQUINOX, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_SOLSTICE, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )

            else:
                data[ key + ( astrobase.AstroBase.DATA_TAG_SOLSTICE, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_EQUINOX, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )

            astrobase.AstroBase.getEclipse( utcNow, data, astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )


    @staticmethod
    def __calculatePlanets( utcNow, data, timeScale, topos, ephemerisPlanets, planets, magnitudeMaximum ):
        t = timeScale.utc( utcNow.year, utcNow.month, utcNow.day )
        for planet in planets:
            if planet == astrobase.AstroBase.PLANET_MERCURY or \
               planet == astrobase.AstroBase.PLANET_VENUS or \
               planet == astrobase.AstroBase.PLANET_JUPITER or \
               planet == astrobase.AstroBase.PLANET_URANUS:
                apparentMagnitude = planetary_magnitude( ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ].at( t ).observe( ephemerisPlanets[ AstroSkyfield.__PLANET_MAPPINGS[ planet ] ] ) )

            else:
                #TODO Hard coded for now until Skyfield can provide calculated apparent magnitude...
                # https://github.com/skyfielders/python-skyfield/issues/210
                # https://rhodesmill.org/skyfield/api.html#skyfield.magnitudelib.planetary_magnitude
                if planet == astrobase.AstroBase.PLANET_MARS:
                    apparentMagnitude = -3.0

                elif planet == astrobase.AstroBase.PLANET_SATURN:
                    apparentMagnitude = 0.0

                elif planet == astrobase.AstroBase.PLANET_NEPTUNE:
                    apparentMagnitude = 8.0

                elif planet == astrobase.AstroBase.PLANET_PLUTO:
                    apparentMagnitude = 14.0

            if apparentMagnitude <= magnitudeMaximum:
                AstroSkyfield.__calculateCommon( utcNow, data, timeScale, topos, ephemerisPlanets,
                                                 ephemerisPlanets[ AstroSkyfield.__PLANET_MAPPINGS[ planet ] ], astrobase.AstroBase.BodyType.PLANET, planet )


    #TODO According to
    #     https://github.com/skyfielders/python-skyfield/issues/39
    #     https://github.com/skyfielders/python-skyfield/pull/40
    # Skyfield might eventually support star names out of the box.
    @staticmethod
    def __calculateStars( utcNow, data, timeScale, topos, ephemerisPlanets, ephemerisStars, stars, magnitudeMaximum ):
        for star in stars:
            if star in astrobase.AstroBase.STARS:
                theStar = ephemerisStars.loc[ astrobase.AstroBase.STARS_TO_HIP[ star ] ]
                if theStar.magnitude <= magnitudeMaximum:
                    AstroSkyfield.__calculateCommon( utcNow, data, timeScale, topos, ephemerisPlanets,
                                                     Star.from_dataframe( theStar ), astrobase.AstroBase.BodyType.STAR, star )


    @staticmethod
    def __calculateCometsOrMinorPlanets( utcNow, data, timeScale, topos, ephemerisPlanets, bodyType, cometsOrMinorPlanets, cometOrMinorPlanetData, magnitudeMaximum ):
        t = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
        sun = ephemerisPlanets[ "sun" ]
        earth = ephemerisPlanets[ "earth" ]
        alt, az, earthSunDistance = ( earth + topos ).at( t ).observe( sun ).apparent().altaz()
        for key in cometsOrMinorPlanets:
            if key in cometOrMinorPlanetData:
                with io.BytesIO( cometOrMinorPlanetData[ key ].getData().encode() ) as f:
                    if cometOrMinorPlanetData[ key ].getDataType() == orbitalelement.OE.DataType.SKYFIELD_COMET:
                        dataframe = mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )
                        body = sun + mpc.comet_orbit( dataframe.loc[ cometOrMinorPlanetData[ key ].getName() ], timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )

                    else:
                        dataframe = mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
                        body = sun + mpc.mpcorb_orbit( dataframe.loc[ cometOrMinorPlanetData[ key ].getName() ], timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )

                ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()
                ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()

                apparentMagnitude = astrobase.AstroBase.getApparentMagnitude_HG( dataframe.loc[ cometOrMinorPlanetData[ key ].getName() ][ "magnitude_H" ], 
                                                                                 dataframe.loc[ cometOrMinorPlanetData[ key ].getName() ][ "magnitude_G" ], 
                                                                                 earthBodyDistance.au, 
                                                                                 sunBodyDistance.au, 
                                                                                 earthSunDistance.au )

                if apparentMagnitude >= astrobase.AstroBase.MAGNITUDE_MINIMUM and apparentMagnitude <= magnitudeMaximum:
                    AstroSkyfield.__calculateCommon( utcNow, data, timeScale, topos, ephemerisPlanets, body, bodyType, key )
                    print( cometOrMinorPlanetData[ key ].getName(), apparentMagnitude )#TODO Testing


    @staticmethod
    def __calculateCommon( utcNow, data, timeScale, topos, ephemerisPlanets, body, bodyType, nameTag ):
        neverUp = False
        key = ( bodyType, nameTag )
        t0 = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
        t1 = timeScale.utc( utcNow.year, utcNow.month, utcNow.day + 2 )
        t, y = almanac.find_discrete( t0, t1, almanac.risings_and_settings( ephemerisPlanets, body, topos ) )
        if len( t ) >= 2: # Ensure there is at least one rise and one set.
            t = t.utc_datetime()
            if y[ 0 ]:
                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )

            else:
                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )

            alt, az, bodyDistance = ( ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ] + topos ).at( t0 ).observe( body ).apparent().altaz()
            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

        else:
            if almanac.risings_and_settings( ephemerisPlanets, body, topos )( t0 ): # Body is up (and so always up).
                alt, az, bodyDistance = ( ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ] + topos ).at( t0 ).observe( body ).apparent().altaz()
                data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
                data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

            else:
                neverUp = True # Body is down (and so never up).

        return neverUp


#TODO...
# https://rhodesmill.org/skyfield/earth-satellites.html
# https://rhodesmill.org/skyfield/api-satellites.html
# https://github.com/skyfielders/python-skyfield/issues/327
# https://github.com/redraw/satellite-passes-api/blob/ffab732e20f6db0503d8e14be3e546ea35a50924/app/tracker.py#L28
    @staticmethod
    def __calculateSatellites( utcNow, data, timeScale, topos, ephemerisPlanets, satellites, satelliteData ):
        for key in satellites:
            if key in satelliteData:
                pass


    # Returns the latitude and longitude of the observer (or topos), in radians.
    @staticmethod
    def __getLatitudeLongitude( observer ):
        for thing in observer.positives: # If an observer is passed in, a Topos object will be contained within.
            if isinstance( thing, Topos ):
                latitude = thing.latitude.radians
                longitude = thing.longitude.radians
                break

        return latitude, longitude


    # If all stars in the Hipparcos catalogue were included, capped to magnitude 15,
    # there would be over 100,000 stars which is impractical.
    #
    # Instead, could use a list of "common name" stars, referred to in
    #     https://www.cosmos.esa.int/web/hipparcos/common-star-names.
    #
    # However, Skyfield also has an internal list of named stars so use that for now.
    #
    # Load the Hipparcos catalogue and filter out stars that are not on our list (common name or named).
    #
    # Format of Hipparcos catalogue:
    #     ftp://cdsarc.u-strasbg.fr/cats/I/239/ReadMe
    @staticmethod
    def createEphemerisStars():
        import gzip, os

        catalogue = hipparcos.URL[ hipparcos.URL.rindex( "/" ) + 1 : ]
        if not os.path.isfile( catalogue ):
            print( "Downloading star catalogue..." )
            load.open( hipparcos.URL )

        hipparcosIdentifiers = list( AstroSkyfield.STARS_TO_HIP.values() )
        if os.path.isfile( AstroSkyfield.__EPHEMERIS_STARS ):
            os.remove( AstroSkyfield.__EPHEMERIS_STARS )

        print( "Creating list of stars..." )
        with gzip.open( catalogue, "rb" ) as inFile, gzip.open( AstroSkyfield.__EPHEMERIS_STARS, "wb" ) as outFile:
            for line in inFile:
                hip = int( line.decode()[ 8 : 14 ].strip() ) # Magnitude can be found at indices [ 42 : 46 ].
                if hip in hipparcosIdentifiers:
                    outFile.write( line )

        print( "Created", AstroSkyfield.__EPHEMERIS_STARS )


    # Create the planet ephemeris from online source:
    #     https://github.com/skyfielders/python-skyfield/issues/123
    #     ftp://ssd.jpl.nasa.gov/pub/eph/planets/README.txt
    #     ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/ascii_format.txt
    #
    # The ephemeris date range is from the date of creation plus one year.
    #
    # Alternate method to create the ephemeris, download a .bsp and use spkmerge to create a smaller subset.
    # Refer to https://github.com/skyfielders/python-skyfield/issues/123
    # https://github.com/skyfielders/python-skyfield/issues/231#issuecomment-450507640
    @staticmethod
    def createEphemerisPlanets():
        import datetime, os, subprocess

        if os.path.isfile( AstroSkyfield.__EPHEMERIS_PLANETS ):
            os.remove( AstroSkyfield.__EPHEMERIS_PLANETS )

        today = datetime.date.today()
        oneYearFromToday = today.replace( year = today.year + 1 )
        planetEphemeris = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de438.bsp"
        dateFormat = "%Y/%m/%d"
        command = "python3 -m jplephem excerpt " + \
                  today.strftime( dateFormat ) + " " + \
                  oneYearFromToday.strftime( dateFormat ) + " " + \
                  planetEphemeris + " " + AstroSkyfield.__EPHEMERIS_PLANETS

        try:
            print( "Creating planet ephemeris..." )
            subprocess.call( command, shell = True )
            completed = True

        except subprocess.CalledProcessError as e:
            print( e )
            completed = False

        if completed:
            print( "Created", AstroSkyfield.__EPHEMERIS_PLANETS )


# Functions to create the stars/planet ephemerides; uncomment the gettext lines at the top!
# AstroSkyfield.createEphemerisStars()
# AstroSkyfield.createEphemerisPlanets()