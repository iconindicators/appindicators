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


# Calculate astronomical information using Skyfield.


#TODO Can pip3 be run from the install?
# Possible ways to have PIP stuff installed with the DEB/PPA:
# https://unix.stackexchange.com/questions/347649/how-to-add-a-python-package-dependance-to-a-debian-package
# https://www.debian.org/doc/manuals/maint-guide/dreq.en.html#control
# https://askubuntu.com/questions/327543/how-can-a-debian-package-install-python-modules-from-pypi
# https://wiki.debian.org/Python/Pybuild
#
# Alternatively, maybe put in a note at the top of the PPA page and/or
# when the indicator runs, do some sort of check to see if the stuff is installed and correct versions
# and if not, fire off a notification to the user and log the install sequence in the log.
#
# Also can put information in the AskUbuntu page.
#
# Install (and upgrade to) latest skyfield: 
#     sudo apt-get install python3-pip
#     sudo pip3 install --upgrade skyfield
#     sudo pip3 install --upgrade pytz
#     sudo pip3 install --upgrade pandas


from datetime import timedelta

from skyfield import almanac
from skyfield.api import EarthSatellite, load, Star, Topos
from skyfield.constants import DEG2RAD
from skyfield.data import hipparcos
from skyfield.nutationlib import iau2000b

import astrobase, datetime, gzip, math, os, pytz, orbitalelement, subprocess, twolineelement


class AstroSkyfield( astrobase.AstroBase ):

    # Ephemerides
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


#TODO Check the function at the end which creates the hip data...it should use this list as the source for the star names.
#TODO In the file named_stars, the function at the bottom is deprecated...so are these named stars defunct?
# https://github.com/skyfielders/python-skyfield/issues/304
    # Sourced from skyfield/named_stars.py
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

    astrobase.AstroBase.STARS_TO_HIP.update( STARS_TO_HIP = {
        "ACHERNAR" :               588,
        "ACRUX" :                  718,
        "ADHARA" :                 3579,
        "AGENA" :                  8702,
        "ALBIREO" :                5947,
        "ALCOR" :                  5477,
        "ALDEBARAN" :              1421,
        "ALDERAMIN" :              5199,
        "ALGENIB" :                5863,
        "ALGIEBA" :                583,
        "ALGOL" :                  4576,
        "ALHENA" :                 1681,
        "ALIOTH" :                 2956,
        "ALKAID" :                 7301,
        "ALMACH" :                 640,
        "ALNAIR" :                 9268,
        "ALNILAM" :                6311,
        "ALNITAK" :                6727,
        "ALPHARD" :                6390,
        "ALPHECCA" :               6267,
        "ALPHERATZ" :              77,
        "ALTAIR" :                 7649,
        "ALUDRA" :                 5904,
        "ANKAA" :                  81,
        "ANTARES" :                763,
        "ARCTURUS" :               9673,
        "ARIDED" :                 2098,
        "ARIDIF" :                 2098,
        "ASPIDISKE" :              5556,
        "ATRIA" :                  2273,
        "AVIOR" :                  1037,
        "BECRUX" :                 2434,
        "BELLATRIX" :              5336,
        "BENETNASH" :              7301,
        "BETELGEUSE" :             7989,
        "BIRDUN" :                 6657,
        "CANOPUS" :                438,
        "CAPELLA" :                4608,
        "CAPH" :                   46,
        "CASTOR" :                 6850,
        "DENEB" :                  2098,
        "DENEB KAITOS" :           419,
        "DENEBOLA" :               7632,
        "DIPHDA" :                 419,
        "DSCHUBBA" :               8401,
        "DUBHE" :                  4061,
        "DURRE MENTHOR" :          102,
        "ELNATH" :                 5428,
        "ENIF" :                   7315,
        "ETAMIN" :                 7833,
        "FOMALHAUT" :              13368,
        "FORAMEN" :                3308,
        "GACRUX" :                 1084,
        "GEMMA" :                  6267,
        "GIENAH" :                 2488,
        "GIRTAB" :                 6228,
        "GRUID" :                  12122,
        "HADAR" :                  8702,
        "HAMAL" :                  884,
        "HERSCHEL'S GARNET STAR" : 7259,
        "IZAR" :                   2105,
        "KAUS AUSTRALIS" :         185,
        "KOCHAB" :                 2607,
        "KOO SHE" :                2913,
        "MARCHAB" :                13963,
        "MARFIKENT" :              1352,
        "MARKAB" :                 5941,
        "MEGREZ" :                 9774,
        "MEN" :                    1860,
        "MENKALINAN" :             8360,
        "MENKENT" :                8933,
        "MERAK" :                  3910,
        "MIAPLACIDUS" :            5238,
        "MIMOSA" :                 2434,
        "MINTAKA" :                5930,
        "MIRA" :                   826,
        "MIRACH" :                 447,
        "MIRFAK" :                 5863,
        "MIRZAM" :                 324,
        "MIZAR" :                  5378,
        "MUHLIFEIN" :              1932,
        "MURZIM" :                 324,
        "NAOS" :                   9429,
        "NUNKI" :                  2855,
        "PEACOCK" :                751,
        "PHAD" :                   8001,
        "PHECDA" :                 8001,
        "POLARIS" :                1767,
        "POLLUX" :                 7826,
        "PROCYON" :                7279,
        "RAS ALHAGUE" :            6032,
        "RASALHAGUE" :             6032,
        "REGOR" :                  9953,
        "REGULUS" :                9669,
        "RIGEL" :                  4436,
        "RIGEL KENT" :             1683,
        "RIGIL KENTAURUS" :        1683,
        "SABIK" :                  4012,
        "SADIRA" :                 6537,
        "SADR" :                   453,
        "SAIPH" :                  7366,
        "SARGAS" :                 6228,
        "SCHEAT" :                 13881,
        "SCHEDAR" :                179,
        "SCUTULUM" :               5556,
        "SHAULA" :                 5927,
        "SIRIUS" :                 2349,
        "SIRRAH" :                 77,
        "SOUTH STAR" :             4382,
        "SPICA" :                  5474,
        "SUHAIL" :                 4816,
        "THUBAN" :                 8756,
        "TOLIMAN" :                1683,
        "TSEEN SHE" :              3308,
        "TSIH" :                   427,
        "TURAIS" :                 5556,
        "VEGA" :                   1262,
        "WEI" :                    2396,
        "WEZEN" :                  4444 } )

    astrobase.AstroBase.STAR_NAMES_TRANSLATIONS.update( {
        astrobase.AstroBase.STARS[ 0 ]    : _( "Achernar" ),
        astrobase.AstroBase.STARS[ 1 ]    : _( "Acrux" ),
        astrobase.AstroBase.STARS[ 2 ]    : _( "Adhara" ),
        astrobase.AstroBase.STARS[ 3 ]    : _( "Agena" ),
        astrobase.AstroBase.STARS[ 4 ]    : _( "Albireo" ),
        astrobase.AstroBase.STARS[ 5 ]    : _( "Alcor" ),
        astrobase.AstroBase.STARS[ 6 ]    : _( "Aldebaran" ),
        astrobase.AstroBase.STARS[ 7 ]    : _( "Alderamin" ),
        astrobase.AstroBase.STARS[ 8 ]    : _( "Algenib" ),
        astrobase.AstroBase.STARS[ 9 ]    : _( "Algieba" ),
        astrobase.AstroBase.STARS[ 10 ]   : _( "Algol" ),
        astrobase.AstroBase.STARS[ 11 ]   : _( "Alhena" ),
        astrobase.AstroBase.STARS[ 12 ]   : _( "Alioth" ),
        astrobase.AstroBase.STARS[ 13 ]   : _( "Alkaid" ),
        astrobase.AstroBase.STARS[ 14 ]   : _( "Almach" ),
        astrobase.AstroBase.STARS[ 15 ]   : _( "Alnair" ),
        astrobase.AstroBase.STARS[ 16 ]   : _( "Alnilam" ),
        astrobase.AstroBase.STARS[ 17 ]   : _( "Alnitak" ),
        astrobase.AstroBase.STARS[ 18 ]   : _( "Alphard" ),
        astrobase.AstroBase.STARS[ 19 ]   : _( "Alphecca" ),
        astrobase.AstroBase.STARS[ 20 ]   : _( "Alpheratz" ),
        astrobase.AstroBase.STARS[ 21 ]   : _( "Altair" ),
        astrobase.AstroBase.STARS[ 22 ]   : _( "Aludra" ),
        astrobase.AstroBase.STARS[ 23 ]   : _( "Ankaa" ),
        astrobase.AstroBase.STARS[ 24 ]   : _( "Antares" ),
        astrobase.AstroBase.STARS[ 25 ]   : _( "Arcturus" ),
        astrobase.AstroBase.STARS[ 26 ]   : _( "Arided" ),
        astrobase.AstroBase.STARS[ 27 ]   : _( "Aridif" ),
        astrobase.AstroBase.STARS[ 28 ]   : _( "Aspidiske" ),
        astrobase.AstroBase.STARS[ 29 ]   : _( "Atria" ),
        astrobase.AstroBase.STARS[ 30 ]   : _( "Avior" ),
        astrobase.AstroBase.STARS[ 31 ]   : _( "Becrux" ),
        astrobase.AstroBase.STARS[ 32 ]   : _( "Bellatrix" ),
        astrobase.AstroBase.STARS[ 33 ]   : _( "Benetnash" ),
        astrobase.AstroBase.STARS[ 34 ]   : _( "Betelgeuse" ),
        astrobase.AstroBase.STARS[ 35 ]   : _( "Birdun" ),
        astrobase.AstroBase.STARS[ 36 ]   : _( "Canopus" ),
        astrobase.AstroBase.STARS[ 37 ]   : _( "Capella" ),
        astrobase.AstroBase.STARS[ 38 ]   : _( "Caph" ),
        astrobase.AstroBase.STARS[ 39 ]   : _( "Castor" ),
        astrobase.AstroBase.STARS[ 40 ]   : _( "Deneb Kaitos" ),
        astrobase.AstroBase.STARS[ 41 ]   : _( "Deneb" ),
        astrobase.AstroBase.STARS[ 42 ]   : _( "Denebola" ),
        astrobase.AstroBase.STARS[ 43 ]   : _( "Diphda" ),
        astrobase.AstroBase.STARS[ 44 ]   : _( "Dschubba" ),
        astrobase.AstroBase.STARS[ 45 ]   : _( "Dubhe" ),
        astrobase.AstroBase.STARS[ 46 ]   : _( "Durre Menthor" ),
        astrobase.AstroBase.STARS[ 47 ]   : _( "Elnath" ),
        astrobase.AstroBase.STARS[ 48 ]   : _( "Enif" ),
        astrobase.AstroBase.STARS[ 49 ]   : _( "Etamin" ),
        astrobase.AstroBase.STARS[ 50 ]   : _( "Fomalhaut" ),
        astrobase.AstroBase.STARS[ 51 ]   : _( "Foramen" ),
        astrobase.AstroBase.STARS[ 52 ]   : _( "Gacrux" ),
        astrobase.AstroBase.STARS[ 53 ]   : _( "Gemma" ),
        astrobase.AstroBase.STARS[ 54 ]   : _( "Gienah" ),
        astrobase.AstroBase.STARS[ 55 ]   : _( "Girtab" ),
        astrobase.AstroBase.STARS[ 56 ]   : _( "Gruid" ),
        astrobase.AstroBase.STARS[ 57 ]   : _( "Hadar" ),
        astrobase.AstroBase.STARS[ 58 ]   : _( "Hamal" ),
        astrobase.AstroBase.STARS[ 59 ]   : _( "Herschel's Garnet Star" ),
        astrobase.AstroBase.STARS[ 60 ]   : _( "Izar" ),
        astrobase.AstroBase.STARS[ 61 ]   : _( "Kaus Australis" ),
        astrobase.AstroBase.STARS[ 62 ]   : _( "Kochab" ),
        astrobase.AstroBase.STARS[ 63 ]   : _( "Koo She" ),
        astrobase.AstroBase.STARS[ 64 ]   : _( "Marchab" ),
        astrobase.AstroBase.STARS[ 65 ]   : _( "Marfikent" ),
        astrobase.AstroBase.STARS[ 66 ]   : _( "Markab" ),
        astrobase.AstroBase.STARS[ 67 ]   : _( "Megrez" ),
        astrobase.AstroBase.STARS[ 68 ]   : _( "Men" ),
        astrobase.AstroBase.STARS[ 69 ]   : _( "Menkalinan" ),
        astrobase.AstroBase.STARS[ 70 ]   : _( "Menkent" ),
        astrobase.AstroBase.STARS[ 71 ]   : _( "Merak" ),
        astrobase.AstroBase.STARS[ 72 ]   : _( "Miaplacidus" ),
        astrobase.AstroBase.STARS[ 73 ]   : _( "Mimosa" ),
        astrobase.AstroBase.STARS[ 74 ]   : _( "Mintaka" ),
        astrobase.AstroBase.STARS[ 75 ]   : _( "Mira" ),
        astrobase.AstroBase.STARS[ 76 ]   : _( "Mirach" ),
        astrobase.AstroBase.STARS[ 77 ]   : _( "Mirfak" ),
        astrobase.AstroBase.STARS[ 78 ]   : _( "Mirzam" ),
        astrobase.AstroBase.STARS[ 79 ]   : _( "Mizar" ),
        astrobase.AstroBase.STARS[ 80 ]   : _( "Muhlifein" ),
        astrobase.AstroBase.STARS[ 81 ]   : _( "Murzim" ),
        astrobase.AstroBase.STARS[ 82 ]   : _( "Naos" ),
        astrobase.AstroBase.STARS[ 83 ]   : _( "Nunki" ),
        astrobase.AstroBase.STARS[ 84 ]   : _( "Peacock" ),
        astrobase.AstroBase.STARS[ 85 ]   : _( "Phad" ),
        astrobase.AstroBase.STARS[ 86 ]   : _( "Phecda" ),
        astrobase.AstroBase.STARS[ 87 ]   : _( "Polaris" ),
        astrobase.AstroBase.STARS[ 88 ]   : _( "Pollux" ),
        astrobase.AstroBase.STARS[ 89 ]   : _( "Procyon" ),
        astrobase.AstroBase.STARS[ 90 ]   : _( "Ras Alhague" ),
        astrobase.AstroBase.STARS[ 91 ]   : _( "Rasalhague" ),
        astrobase.AstroBase.STARS[ 92 ]   : _( "Regor" ),
        astrobase.AstroBase.STARS[ 93 ]   : _( "Regulus" ),
        astrobase.AstroBase.STARS[ 94 ]   : _( "Rigel Kent" ),
        astrobase.AstroBase.STARS[ 95 ]   : _( "Rigel" ),
        astrobase.AstroBase.STARS[ 96 ]   : _( "Rigil Kentaurus" ),
        astrobase.AstroBase.STARS[ 97 ]   : _( "Sabik" ),
        astrobase.AstroBase.STARS[ 98 ]   : _( "Sadira" ),
        astrobase.AstroBase.STARS[ 99 ]   : _( "Sadr" ),
        astrobase.AstroBase.STARS[ 100 ]  : _( "Saiph" ),
        astrobase.AstroBase.STARS[ 101 ]  : _( "Sargas" ),
        astrobase.AstroBase.STARS[ 102 ]  : _( "Scheat" ),
        astrobase.AstroBase.STARS[ 103 ]  : _( "Schedar" ),
        astrobase.AstroBase.STARS[ 104 ]  : _( "Scutulum" ),
        astrobase.AstroBase.STARS[ 105 ]  : _( "Shaula" ),
        astrobase.AstroBase.STARS[ 106 ]  : _( "Sirius" ),
        astrobase.AstroBase.STARS[ 107 ]  : _( "Sirrah" ),
        astrobase.AstroBase.STARS[ 108 ]  : _( "South Star" ),
        astrobase.AstroBase.STARS[ 109 ]  : _( "Spica" ),
        astrobase.AstroBase.STARS[ 110 ]  : _( "Suhail" ),
        astrobase.AstroBase.STARS[ 111 ]  : _( "Thuban" ),
        astrobase.AstroBase.STARS[ 112 ]  : _( "Toliman" ),
        astrobase.AstroBase.STARS[ 113 ]  : _( "Tseen She" ),
        astrobase.AstroBase.STARS[ 114 ]  : _( "Tsih" ),
        astrobase.AstroBase.STARS[ 115 ]  : _( "Turais" ),
        astrobase.AstroBase.STARS[ 116 ]  : _( "Vega" ),
        astrobase.AstroBase.STARS[ 117 ]  : _( "Wei" ),
        astrobase.AstroBase.STARS[ 118 ]  : _( "Wezen" ) } )

    # Corresponding tags which reflect each data tag made visible to the user in the Preferences. 
    astrobase.AstroBase.STAR_TAGS_TRANSLATIONS.update( {
        astrobase.AstroBase.STARS[ 0 ]    : _( "ACHERNAR" ),                   
        astrobase.AstroBase.STARS[ 1 ]    : _( "ACRUX" ),                      
        astrobase.AstroBase.STARS[ 2 ]    : _( "ADHARA" ),                     
        astrobase.AstroBase.STARS[ 3 ]    : _( "AGENA" ),                      
        astrobase.AstroBase.STARS[ 4 ]    : _( "ALBIREO" ),                    
        astrobase.AstroBase.STARS[ 5 ]    : _( "ALCOR" ),                      
        astrobase.AstroBase.STARS[ 6 ]    : _( "ALDEBARAN" ),                  
        astrobase.AstroBase.STARS[ 7 ]    : _( "ALDERAMIN" ),                  
        astrobase.AstroBase.STARS[ 8 ]    : _( "ALGENIB" ),                    
        astrobase.AstroBase.STARS[ 9 ]    : _( "ALGIEBA" ),                    
        astrobase.AstroBase.STARS[ 10 ]   : _( "ALGOL" ),                      
        astrobase.AstroBase.STARS[ 11 ]   : _( "ALHENA" ),                     
        astrobase.AstroBase.STARS[ 12 ]   : _( "ALIOTH" ),                     
        astrobase.AstroBase.STARS[ 13 ]   : _( "ALKAID" ),                     
        astrobase.AstroBase.STARS[ 14 ]   : _( "ALMACH" ),                     
        astrobase.AstroBase.STARS[ 15 ]   : _( "ALNAIR" ),                     
        astrobase.AstroBase.STARS[ 16 ]   : _( "ALNILAM" ),                    
        astrobase.AstroBase.STARS[ 17 ]   : _( "ALNITAK" ),                    
        astrobase.AstroBase.STARS[ 18 ]   : _( "ALPHARD" ),                    
        astrobase.AstroBase.STARS[ 19 ]   : _( "ALPHECCA" ),                   
        astrobase.AstroBase.STARS[ 20 ]   : _( "ALPHERATZ" ),                  
        astrobase.AstroBase.STARS[ 21 ]   : _( "ALTAIR" ),                     
        astrobase.AstroBase.STARS[ 22 ]   : _( "ALUDRA" ),                     
        astrobase.AstroBase.STARS[ 23 ]   : _( "ANKAA" ),                      
        astrobase.AstroBase.STARS[ 24 ]   : _( "ANTARES" ),                    
        astrobase.AstroBase.STARS[ 25 ]   : _( "ARCTURUS" ),                   
        astrobase.AstroBase.STARS[ 26 ]   : _( "ARIDED" ),                     
        astrobase.AstroBase.STARS[ 27 ]   : _( "ARIDIF" ),                     
        astrobase.AstroBase.STARS[ 28 ]   : _( "ASPIDISKE" ),                  
        astrobase.AstroBase.STARS[ 29 ]   : _( "ATRIA" ),                      
        astrobase.AstroBase.STARS[ 30 ]   : _( "AVIOR" ),                      
        astrobase.AstroBase.STARS[ 31 ]   : _( "BECRUX" ),                     
        astrobase.AstroBase.STARS[ 32 ]   : _( "BELLATRIX" ),                  
        astrobase.AstroBase.STARS[ 33 ]   : _( "BENETNASH" ),                  
        astrobase.AstroBase.STARS[ 34 ]   : _( "BETELGEUSE" ),                 
        astrobase.AstroBase.STARS[ 35 ]   : _( "BIRDUN" ),                     
        astrobase.AstroBase.STARS[ 36 ]   : _( "CANOPUS" ),                    
        astrobase.AstroBase.STARS[ 37 ]   : _( "CAPELLA" ),                    
        astrobase.AstroBase.STARS[ 38 ]   : _( "CAPH" ),                       
        astrobase.AstroBase.STARS[ 39 ]   : _( "CASTOR" ),                     
        astrobase.AstroBase.STARS[ 40 ]   : _( "DENEB KAITOS" ),               
        astrobase.AstroBase.STARS[ 41 ]   : _( "DENEB" ),                      
        astrobase.AstroBase.STARS[ 42 ]   : _( "DENEBOLA" ),                   
        astrobase.AstroBase.STARS[ 43 ]   : _( "DIPHDA" ),                     
        astrobase.AstroBase.STARS[ 44 ]   : _( "DSCHUBBA" ),                   
        astrobase.AstroBase.STARS[ 45 ]   : _( "DUBHE" ),                      
        astrobase.AstroBase.STARS[ 46 ]   : _( "DURRE MENTHOR" ),              
        astrobase.AstroBase.STARS[ 47 ]   : _( "ELNATH" ),                     
        astrobase.AstroBase.STARS[ 48 ]   : _( "ENIF" ),                       
        astrobase.AstroBase.STARS[ 49 ]   : _( "ETAMIN" ),                     
        astrobase.AstroBase.STARS[ 50 ]   : _( "FOMALHAUT" ),                  
        astrobase.AstroBase.STARS[ 51 ]   : _( "FORAMEN" ),                    
        astrobase.AstroBase.STARS[ 52 ]   : _( "GACRUX" ),                     
        astrobase.AstroBase.STARS[ 53 ]   : _( "GEMMA" ),                      
        astrobase.AstroBase.STARS[ 54 ]   : _( "GIENAH" ),                     
        astrobase.AstroBase.STARS[ 55 ]   : _( "GIRTAB" ),                     
        astrobase.AstroBase.STARS[ 56 ]   : _( "GRUID" ),                      
        astrobase.AstroBase.STARS[ 57 ]   : _( "HADAR" ),                      
        astrobase.AstroBase.STARS[ 58 ]   : _( "HAMAL" ),                      
        astrobase.AstroBase.STARS[ 59 ]   : _( "HERSCHEL'S GARNET STAR" ),     
        astrobase.AstroBase.STARS[ 60 ]   : _( "IZAR" ),                       
        astrobase.AstroBase.STARS[ 61 ]   : _( "KAUS AUSTRALIS" ),             
        astrobase.AstroBase.STARS[ 62 ]   : _( "KOCHAB" ),                     
        astrobase.AstroBase.STARS[ 63 ]   : _( "KOO SHE" ),                    
        astrobase.AstroBase.STARS[ 64 ]   : _( "MARCHAB" ),                    
        astrobase.AstroBase.STARS[ 65 ]   : _( "MARFIKENT" ),                  
        astrobase.AstroBase.STARS[ 66 ]   : _( "MARKAB" ),                     
        astrobase.AstroBase.STARS[ 67 ]   : _( "MEGREZ" ),                     
        astrobase.AstroBase.STARS[ 68 ]   : _( "MEN" ),                        
        astrobase.AstroBase.STARS[ 69 ]   : _( "MENKALINAN" ),                 
        astrobase.AstroBase.STARS[ 70 ]   : _( "MENKENT" ),                    
        astrobase.AstroBase.STARS[ 71 ]   : _( "MERAK" ),                      
        astrobase.AstroBase.STARS[ 72 ]   : _( "MIAPLACIDUS" ),                
        astrobase.AstroBase.STARS[ 73 ]   : _( "MIMOSA" ),                     
        astrobase.AstroBase.STARS[ 74 ]   : _( "MINTAKA" ),                    
        astrobase.AstroBase.STARS[ 75 ]   : _( "MIRA" ),                       
        astrobase.AstroBase.STARS[ 76 ]   : _( "MIRACH" ),                     
        astrobase.AstroBase.STARS[ 77 ]   : _( "MIRFAK" ),                     
        astrobase.AstroBase.STARS[ 78 ]   : _( "MIRZAM" ),                     
        astrobase.AstroBase.STARS[ 79 ]   : _( "MIZAR" ),                      
        astrobase.AstroBase.STARS[ 80 ]   : _( "MUHLIFEIN" ),                  
        astrobase.AstroBase.STARS[ 81 ]   : _( "MURZIM" ),                     
        astrobase.AstroBase.STARS[ 82 ]   : _( "NAOS" ),                       
        astrobase.AstroBase.STARS[ 83 ]   : _( "NUNKI" ),                      
        astrobase.AstroBase.STARS[ 84 ]   : _( "PEACOCK" ),                    
        astrobase.AstroBase.STARS[ 85 ]   : _( "PHAD" ),                       
        astrobase.AstroBase.STARS[ 86 ]   : _( "PHECDA" ),                     
        astrobase.AstroBase.STARS[ 87 ]   : _( "POLARIS" ),                    
        astrobase.AstroBase.STARS[ 88 ]   : _( "POLLUX" ),                     
        astrobase.AstroBase.STARS[ 89 ]   : _( "PROCYON" ),                    
        astrobase.AstroBase.STARS[ 90 ]   : _( "RAS ALHAGUE" ),                
        astrobase.AstroBase.STARS[ 91 ]   : _( "RASALHAGUE" ),                 
        astrobase.AstroBase.STARS[ 92 ]   : _( "REGOR" ),                      
        astrobase.AstroBase.STARS[ 93 ]   : _( "REGULUS" ),                    
        astrobase.AstroBase.STARS[ 94 ]   : _( "RIGEL KENT" ),                 
        astrobase.AstroBase.STARS[ 95 ]   : _( "RIGEL" ),                      
        astrobase.AstroBase.STARS[ 96 ]   : _( "RIGIL KENTAURUS" ),            
        astrobase.AstroBase.STARS[ 97 ]   : _( "SABIK" ),                      
        astrobase.AstroBase.STARS[ 98 ]   : _( "SADIRA" ),                     
        astrobase.AstroBase.STARS[ 99 ]   : _( "SADR" ),                       
        astrobase.AstroBase.STARS[ 100 ]  : _( "SAIPH" ),                      
        astrobase.AstroBase.STARS[ 101 ]  : _( "SARGAS" ),                     
        astrobase.AstroBase.STARS[ 102 ]  : _( "SCHEAT" ),                     
        astrobase.AstroBase.STARS[ 103 ]  : _( "SCHEDAR" ),                    
        astrobase.AstroBase.STARS[ 104 ]  : _( "SCUTULUM" ),                   
        astrobase.AstroBase.STARS[ 105 ]  : _( "SHAULA" ),                     
        astrobase.AstroBase.STARS[ 106 ]  : _( "SIRIUS" ),                     
        astrobase.AstroBase.STARS[ 107 ]  : _( "SIRRAH" ),                     
        astrobase.AstroBase.STARS[ 108 ]  : _( "SOUTH STAR" ),                 
        astrobase.AstroBase.STARS[ 109 ]  : _( "SPICA" ),                      
        astrobase.AstroBase.STARS[ 110 ]  : _( "SUHAIL" ),                     
        astrobase.AstroBase.STARS[ 111 ]  : _( "THUBAN" ),                     
        astrobase.AstroBase.STARS[ 112 ]  : _( "TOLIMAN" ),                    
        astrobase.AstroBase.STARS[ 113 ]  : _( "TSEEN SHE" ),                  
        astrobase.AstroBase.STARS[ 114 ]  : _( "TSIH" ),                       
        astrobase.AstroBase.STARS[ 115 ]  : _( "TURAIS" ),                     
        astrobase.AstroBase.STARS[ 116 ]  : _( "VEGA" ),                       
        astrobase.AstroBase.STARS[ 117 ]  : _( "WEI" ),                        
        astrobase.AstroBase.STARS[ 118 ]  : _( "WEZEN" ) } )                   


#TODO Pyephem can return fractional seconds in rise/set date/times...so they have been removed...
# ...not sure if skyfield will/could have the same problem.


#TODO Might need to cache deltat.data and deltat.preds as the backend website was down and I couldn't get them except at a backup site.
# What other files are downloaded?  Need to also grab: https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat  Be careful...this file expires!
#Seems skyfield has changed the way data is loaded with a tag to say not to do a download (use old file).
#There is a ticket about this...but cannot find it right now.


# TODO Verify results: https://ssd.jpl.nasa.gov/horizons.cgi
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
        timeScale = load.timescale()
        utcNowSkyfield = timeScale.utc( utcNow.replace( tzinfo = pytz.UTC ) ) #TODO In each function, so far, this is converted to a datetime...so maybe just pass in the original?
        ephemerisPlanets = load( AstroSkyfield.__EPHEMERIS_PLANETS )
        observer = AstroSkyfield.__getSkyfieldObserver( latitude, longitude, elevation, ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ] )

        AstroSkyfield.__calculateMoon( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets )
        AstroSkyfield.__calculateSun( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets )
        AstroSkyfield.__calculatePlanets( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets, planets )
        with load.open( AstroSkyfield.__EPHEMERIS_STARS ) as f:
            ephemerisStars = hipparcos.load_dataframe( f )

        AstroSkyfield.__calculateStars( utcNowSkyfield, data, timeScale, observer, ephemerisStars, stars )

#     Comet https://github.com/skyfielders/python-skyfield/issues/196
#     utcNow = datetime.datetime.utcnow()
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.Comet, comets, cometData, magnitudeMaximum )
#     print( "updateComets:", ( datetime.datetime.utcnow() - utcNow ) )
#     utcNow = datetime.datetime.utcnow()
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.MinorPlanet, minorPlanets, minorPlanetData, magnitudeMaximum )
#     print( "updateMinorPlanets:", ( datetime.datetime.utcnow() - utcNow ) )

#     Satellite https://github.com/skyfielders/python-skyfield/issues/115
#     utcNow = datetime.datetime.utcnow()
        AstroSkyfield.__calculateSatellites( utcNowSkyfield, data, timeScale, satellites, satelliteData )
#     print( "updateSatellites:", ( datetime.datetime.utcnow() - utcNow ) )

        return data


    # http://www.ga.gov.au/geodesy/astro/moonrise.jsp
    # http://futureboy.us/fsp/moon.fsp
    # http://www.geoastro.de/moondata/index.html
    # http://www.geoastro.de/SME/index.htm
    # http://www.geoastro.de/elevazmoon/index.htm
    # http://www.geoastro.de/altazsunmoon/index.htm
    # http://www.geoastro.de/sundata/index.html
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    @staticmethod
    def __calculateMoon( utcNow, data, timeScale, observer, ephemeris ):
        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        moon = ephemeris[ AstroSkyfield.__MOON ]
        neverUp = AstroSkyfield.__calculateCommon( utcNow, data, timeScale, observer, moon, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )

        illumination = str( int( almanac.fraction_illuminated( ephemeris, AstroSkyfield.__MOON, utcNow ) * 100 ) ) # Needed for icon.
        data[ key + ( astrobase.AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( illumination ) # Needed for icon.

        utcNowDateTime = utcNow.utc_datetime()
        t0 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day )
        t1 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month + 2, 1 ) # Ideally would just like to add one month, but not sure what happens if today's date is say the 31st and the next month is say February.
#TODO Test the above line for Feb.
# https://rhodesmill.org/skyfield/almanac.html
        t, y = almanac.find_discrete( t0, t1, almanac.moon_phases( ephemeris ) )
        moonPhases = [ almanac.MOON_PHASES[ yi ] for yi in y ]
        moonPhaseDateTimes = t.utc_datetime()
        nextNewMoonDateTime = moonPhaseDateTimes [ ( moonPhases.index( "New Moon" ) ) ] #TODO SHould not have text here...figure out the correct way to do it.
        nextFullMoonDateTime = moonPhaseDateTimes [ ( moonPhases.index( "Full Moon" ) ) ]
        data[ key + ( astrobase.AstroBase.DATA_TAG_PHASE, ) ] = astrobase.AstroBase.getLunarPhase( int( float ( illumination ) ), nextFullMoonDateTime, nextNewMoonDateTime ) # Need for notification.

        data[ key + ( astrobase.AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( int( round( AstroSkyfield.__getZenithAngleOfBrightLimb( utcNow, observer, ephemeris[ AstroSkyfield.__SUN ], moon ) ) ) ) # Needed for icon.

        if not neverUp:
            moonPhaseDateTimes = t.utc_iso()
            nextNewMoonISO = moonPhaseDateTimes [ ( moonPhases.index( "New Moon" ) ) ] #TODO See above TODO about having text here.
            nextFirstQuarterISO = moonPhaseDateTimes[ ( moonPhases.index( "First Quarter" ) ) ]
            nextThirdQuarterISO = moonPhaseDateTimes [ ( moonPhases.index( "Last Quarter" ) ) ]
            nextFullMoonISO = moonPhaseDateTimes [ ( moonPhases.index( "Full Moon" ) ) ]

            data[ key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = nextFirstQuarterISO
            data[ key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ] = nextFullMoonISO
            data[ key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = nextThirdQuarterISO
            data[ key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ] = nextNewMoonISO

            astrobase.AstroBase.getEclipse( utcNow.utc_datetime().replace( tzinfo = None ), data, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )


    # Compute the bright limb angle (relative to zenith) between the sun and a planetary body (typically the moon).
    # Measured in degrees counter clockwise from a positive y axis.
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
    @staticmethod
#TODO Can this method be made to be generic so that pyephem can use it?
#The only sticking point here is utcNow.gast which is a skyfield thing...need to be able to compute the hour angle and/or sidereal time.
    def __getZenithAngleOfBrightLimb( utcNow, observer, sun, body ):

        # Get the latitude/longitude...there has to be a Topos object in the observer, because that is how Skyfield works!
        for thing in observer.positives:
            if isinstance( thing, Topos ):
                latitude = thing.latitude
                longitude = thing.longitude
                break

        sunRA, sunDec, earthDistance = observer.at( utcNow ).observe( sun ).apparent().radec()
        bodyRA, bodyDec, earthDistance = observer.at( utcNow ).observe( body ).apparent().radec()

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
        y = math.cos( sunDec.radians ) * math.sin( sunRA.radians - bodyRA.radians )
        x = math.sin( sunDec.radians ) * math.cos( bodyDec.radians ) - math.cos( sunDec.radians ) * math.sin( bodyDec.radians ) * math.cos( sunRA.radians - bodyRA.radians )
        positionAngleOfBrightLimb = math.atan2( y, x )

    #TODO Are the comments below still valid?
        # Astronomical Algorithms by Jean Meeus, Second Edition, page 92.
        # https://tycho.usno.navy.mil/sidereal.html
        # http://www.wwu.edu/skywise/skymobile/skywatch.html
        # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
        observerSiderealTime = 15.0 * DEG2RAD * utcNow.gast + longitude.radians # From skyfield.earthlib.py
        hourAngle = observerSiderealTime - bodyRA.radians

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
        y = math.sin( hourAngle )
        x = math.tan( latitude.radians ) * math.cos( bodyDec.radians ) - math.sin( bodyDec.radians ) * math.cos( hourAngle )
        parallacticAngle = math.atan2( y, x )

        return ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi )


    @staticmethod
    def __calculateSun( utcNow, data, timeScale, observer, ephemeris ):
        sun = ephemeris[ AstroSkyfield.__SUN ]
        neverUp = AstroSkyfield.__calculateCommon( utcNow, data, timeScale, observer, sun, astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )
        if not neverUp:
#TODO Skyfield does not calculate dawn/dusk, but there is a workaround
# https://github.com/skyfielders/python-skyfield/issues/225
            astrobase.AstroBase.getEclipse( utcNow.utc_datetime().replace( tzinfo = None ), data, astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )
#TODO What about solstice/equinox?            


    @staticmethod
    def __calculatePlanets( utcNow, data, timeScale, observer, ephemeris, planets ):
        for planet in planets:
            AstroSkyfield.__calculateCommon( utcNow, data, timeScale, observer, ephemeris[ AstroSkyfield.__PLANET_MAPPINGS[ planet ] ], astrobase.AstroBase.BodyType.PLANET, planet )


    #TODO According to 
    #     https://github.com/skyfielders/python-skyfield/issues/39
    #     https://github.com/skyfielders/python-skyfield/pull/40
    # skyfield might support somehow star names out of the box...
    # ...so that means taking the data, selecting only ephemerisStars of magnitude 2.5 or so and keep those.
    # See revision 999 for code to filter ephemerisStars by magnitude.
    @staticmethod
    def __calculateStars( utcNow, data, timeScale, observer, ephemeris, stars ):
        for star in stars:
    #         mag = ephemeris.loc[ STARS[ star ] ].magnitude #TODO Leave here as we may need to compute the magnitude for the front end to submenu by mag.
#TODO Not sure which below is correct...need to change star name to HIP?
#             AstroSkyfield.__calculateCommon( utcNow, data, timeScale, observer, Star.from_dataframe( ephemeris.loc[ astrobase.AstroBase.STARS[ star ] ] ), astrobase.BodyType.STAR, star )
            hip = AstroSkyfield.STARS_TO_HIP[ star ]
            s = Star.from_dataframe( ephemeris.loc[ AstroSkyfield.STARS_TO_HIP[ star ] ] )
            AstroSkyfield.__calculateCommon( utcNow, data, timeScale, observer, Star.from_dataframe( ephemeris.loc[ AstroSkyfield.STARS_TO_HIP[ star ] ] ), astrobase.AstroBase.BodyType.STAR, star )


    #TODO  
    # https://github.com/skyfielders/python-skyfield/issues/196#issuecomment-418139819
    # The MPC might provide comet / minor planet data in a different format which Skyfield can read.
    @staticmethod
    def __calculateCometsOrMinorPlanets( utcNow, data, timeScale, observer, ephemeris, cometsOrMinorPlanets, cometOrMinorPlanetData, magnitudeMaximum ):
        pass
    #     for star in stars:
    #         mag = ephemeris.loc[ STARS[ star ] ].magnitude #TODO Leave here as we may need to compute the magnitude for the front end to submenu by mag.
    #         AstroSkyfield__calculateCommon( utcNow, data, timeScale, observer, Star.from_dataframe( ephemeris.loc[ STARS[ star ] ] ), AstronomicalBodyType.Star, star )


    @staticmethod
#TODO Double check this as we removed the parameter hideIfBelowTheHorizon.    
    def __calculateCommon( utcNow, data, timeScale, observer, body, astronomicalBodyType, nameTag ):
        neverUp = False
        key = ( astronomicalBodyType, nameTag )

        utcNowDateTime = utcNow.utc_datetime()
        t0 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day, utcNowDateTime.hour )
        t1 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day + 2, utcNowDateTime.hour ) # Look two days ahead as one day ahead may miss the next rise or set.

        t, y = almanac.find_discrete( t0, t1, AstroSkyfield.__bodyrise_bodyset( observer, body ) ) # Original Skyfield function only supports sun rise/set, so have generalised to any body.
        if t:
            t = t.utc_iso( delimiter = ' ' )
            if y[ 0 ]:
                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = str( t[ 0 ][ : -1 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = str( t[ 1 ][ : -1 ] )

            else:
                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = str( t[ 1 ][ : -1 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = str( t[ 0 ][ : -1 ] )

        else:
            if AstroSkyfield.__bodyrise_bodyset( observer, body )( t0 ): # Taken and modified from Skyfield almanac.find_discrete.
                pass # Body is up (and so always up).

            else:
                neverUp = True # Body is down (and so never up). 

        if not neverUp:
            apparent = observer.at( utcNow ).observe( body ).apparent()
            alt, az, bodyDistance = apparent.altaz()
            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

        return neverUp


    #TODO Only called in one place...and if so, just move the code in place and delete this function.
#TODO Rename to getObserver.
    @staticmethod
    def __getSkyfieldObserver( latitude, longitude, elevation, earth ):
        return earth + Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )


    #TODO Have copied the code from skyfield/almanac.py as per
    # https://github.com/skyfielders/python-skyfield/issues/226
    # to compute rise/set for any body.
    #
    # Returns true if the body is up at the time give; false if down.
    @staticmethod
#TODO I believe skyfield now provides this function...so this could eventually go.
    def __bodyrise_bodyset( observer, body ):

        def is_body_up_at( t ):
            t._nutation_angles = iau2000b( t.tt )
            return observer.at( t ).observe( body ).apparent().altaz()[ 0 ].degrees > -0.8333

        is_body_up_at.rough_period = 0.5

        return is_body_up_at


#TODO Might be useful:https://github.com/skyfielders/python-skyfield/issues/242

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
    @staticmethod
    def __calculateSatellites( utcNow, data, timeScale, satellites, satelliteData ):
        for key in satellites:
            if key in satelliteData:
                __calculateNextSatellitePass( utcNow, data, timeScale, key, satelliteData[ key ] )


def __calculateNextSatellitePass( utcNow, data, timeScale, key, satelliteTLE ):
    key = ( astrobase.AstroBase.BodyType.Satellite, " ".join( key ) )
    currentDateTime = utcNow.J
    endDateTime = timeScale.utc( ( utcNow.utc_datetime() + timedelta( days = 24 * 2 ) ).replace( tzinfo = pytz.UTC ) ).J #TODO Maybe pass this in as it won't change per satellite.

#TODO rise/set not yet implemented in Skyfield
# https://github.com/skyfielders/python-skyfield/issues/115
#     while currentDateTime < endDateTime:
#         satellite = EarthSatellite( satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2(), satelliteTLE.getTLETitle() )

#         city = __getCity( data, currentDateTime )
#         satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
#         satellite.compute( city )
#         try:
#             nextPass = city.next_pass( satellite )
# 
#         except ValueError:
#             if satellite.circumpolar:
#                 data[ key + ( DATA_MESSAGE, ) ] = MESSAGE_SATELLITE_IS_CIRCUMPOLAR
#                 data[ key + ( DATA_AZIMUTH, ) ] = str( satellite.az )
# 
#             break
# 
#         if not __isSatellitePassValid( nextPass ):
#             break
# 
#         # The pass is valid.  If the satellite is currently passing, work out when it rose...
#         if nextPass[ 0 ] > nextPass[ 4 ]: # The rise time is after set time, so the satellite is currently passing.
#             setTime = nextPass[ 4 ]
#             nextPass = __calculateSatellitePassForRisingPriorToNow( currentDateTime, data, satelliteTLE )
#             if nextPass is None:
#                 currentDateTime = ephem.Date( setTime + ephem.minute * 30 ) # Could not determine the rise, so look for the next pass.
#                 continue
# 
#         # Now have a satellite rise/transit/set; determine if the pass is visible.
#         passIsVisible = __isSatellitePassVisible( data, nextPass[ 2 ], satellite )
#         if not passIsVisible:
#             currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )
#             continue
# 
#         # The pass is visible and the user wants only visible passes OR the user wants any pass...
#         data[ key + ( DATA_RISE_DATE_TIME, ) ] = str( nextPass[ 0 ].datetime() )
#         data[ key + ( DATA_RISE_AZIMUTH, ) ] = str( nextPass[ 1 ] )
#         data[ key + ( DATA_SET_DATE_TIME, ) ] = str( nextPass[ 4 ].datetime() )
#         data[ key + ( DATA_SET_AZIMUTH, ) ] = str( nextPass[ 5 ] )
# 
#         break
# 
# 
# def __calculateSatellitePassForRisingPriorToNow( ephemNow, data, satelliteTLE ):
#     currentDateTime = ephem.Date( ephemNow - ephem.minute ) # Start looking from one minute ago.
#     endDateTime = ephem.Date( ephemNow - ephem.hour * 1 ) # Only look back an hour for the rise time (then just give up).
#     nextPass = None
#     while currentDateTime > endDateTime:
#         city = __getCity( data, currentDateTime )
#         satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
#         satellite.compute( city )
#         try:
#             nextPass = city.next_pass( satellite )
#             if not __isSatellitePassValid( nextPass ):
#                 nextPass = None
#                 break # Unlikely to happen but better to be safe and check!
# 
#             if nextPass[ 0 ] < nextPass[ 4 ]:
#                 break
# 
#             currentDateTime = ephem.Date( currentDateTime - ephem.minute )
# 
#         except:
#             nextPass = None
#             break # This should never happen as the satellite has a rise and set (is not circumpolar or never up).
# 
#     return nextPass
# 
# 
# def __isSatellitePassValid( satellitePass ):
#     return \
#         satellitePass is not None and \
#         len( satellitePass ) == 6 and \
#         satellitePass[ 0 ] is not None and \
#         satellitePass[ 1 ] is not None and \
#         satellitePass[ 2 ] is not None and \
#         satellitePass[ 3 ] is not None and \
#         satellitePass[ 4 ] is not None and \
#         satellitePass[ 5 ] is not None
# 
# 
# # Determine if a satellite pass is visible or not...
# #
# #    http://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
# #    http://www.celestrak.com/columns/v03n01
# #    http://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
# def __isSatellitePassVisible( data, passDateTime, satellite ):
#     city = __getCity( data, passDateTime )
#     city.pressure = 0
#     city.horizon = "-0:34"
# 
#     satellite.compute( city )
#     sun = ephem.Sun()
#     sun.compute( city )
# 
#     return satellite.eclipsed is False and \
#            sun.alt > ephem.degrees( "-18" ) and \
#            sun.alt < ephem.degrees( "-6" )


    # If all stars in the Hipparcos catalogue were included, capped to magnitude 15,
    # there would be over 100,000 stars which is impractical.
    #
    # Instead, present the user with the "common name" stars,
    #     https://www.cosmos.esa.int/web/hipparcos/common-star-names.
    #
    # Load the Hipparcos catalogue and filter out those not "common name".
    # The final list of stars range in magnitude up to around 12.
    #
    # Format of Hipparcos catalogue:
    #     ftp://cdsarc.u-strasbg.fr/cats/I/239/ReadMe
    def createStarEphemeris():
        catalogue = hipparcos.URL[ hipparcos.URL.rindex( "/" ) + 1 : ]
        if not os.path.isfile( catalogue ):
            print( "Downloading star catalogue..." )
            load.open( hipparcos.URL )

        print( "Creating list of common-named stars..." )
        hipparcosIdentifiers = list( AstroSkyfield.STARS_TO_HIP.values() )
        with gzip.open( catalogue, "rb" ) as inFile, gzip.open( AstroSkyfield.__EPHEMERIS_STARS, "wb" ) as outFile:
            for line in inFile:
                hip = int( line.decode()[ 8 : 14 ].strip() ) # Magnitude can be found at columns indices [ 42 : 46 ].
                if hip in hipparcosIdentifiers:
                    outFile.write( line )

        print( "Done" )


#TODO Need header.
# TODO Refer to https://github.com/skyfielders/python-skyfield/issues/123
# Still need all the naif...tls stuff and spkmerge stuff now that we use jplephem?
    def createPlanetEphemeris():
        today = datetime.date.today()
        dateFormat = "%Y/%m/%d"
        firstOfThisMonth = datetime.date( today.year, today.month, 1 ).strftime( dateFormat )
        oneYearFromNow = datetime.date( today.year + 1, today.month + 1, 1 ).strftime( dateFormat )
#TODO Test for month = 12 and ensure that the year/month roll over correctly (to year + 1 and January).

#TODO URL reference for this ... from the skyfield docs?
        planetEphemeris = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de438.bsp"
        outputEphemeris = "planets.bsp"

        command = "python3 -m jplephem excerpt " + firstOfThisMonth + " " + oneYearFromNow + " " + planetEphemeris + " " + outputEphemeris

        try:
            print( "Creating planet ephemeris..." )
            subprocess.call( command, shell = True )
            print( "Done" ) #TODO This prints even if an error/exception occurs...

        except subprocess.CalledProcessError as e:
            print( e )


# createStarEphemeris()
# createPlanetEphemeris()