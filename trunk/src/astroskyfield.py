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


# Uncomment the lines below when needing to run the planet/star ephemeris creation functions at the end.
# import gettext
# gettext.install( "astroskyfield" )

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

#TODO Tidy up.
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
        observer = ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ] + \
                   Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )

        AstroSkyfield.__calculateMoon( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets )
        AstroSkyfield.__calculateSun( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets )
        AstroSkyfield.__calculatePlanets( utcNowSkyfield, data, timeScale, observer, ephemerisPlanets, planets )

        with load.open( AstroSkyfield.__EPHEMERIS_STARS ) as f:
            ephemerisStars = hipparcos.load_dataframe( f )

        AstroSkyfield.__calculateStars( utcNowSkyfield, data, timeScale, observer, ephemerisStars, stars )

#TODO
# https://github.com/skyfielders/python-skyfield/issues/11
# https://github.com/skyfielders/python-skyfield/issues/196
# https://github.com/skyfielders/python-skyfield/pull/202
# https://github.com/skyfielders/python-skyfield/issues/305
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.Comet, comets, cometData, magnitudeMaximum )
#     __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.MinorPlanet, minorPlanets, minorPlanetData, magnitudeMaximum )

#TODO https://github.com/skyfielders/python-skyfield/issues/115
        AstroSkyfield.__calculateSatellites( utcNowSkyfield, data, timeScale, satellites, satelliteData )

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

        data[ key + ( astrobase.AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( AstroSkyfield.__getZenithAngleOfBrightLimb( utcNow, observer, ephemeris[ AstroSkyfield.__SUN ], moon ) ) # Needed for icon.

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

        if not neverUp:
            data[ key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( "First Quarter" ) ) ] )
            data[ key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( "Full Moon" ) ) ] )
            data[ key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes [ ( moonPhases.index( "Last Quarter" ) ) ] )
            data[ key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( "New Moon" ) ) ] )

            astrobase.AstroBase.getEclipse( utcNow.utc_datetime().replace( tzinfo = None ), data, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
            #TODO the date/time format does not match that in the indicator.
            #WHat does pyephem do?  Pass in string or a datetime?
            #####IS THIS STILL RELEVENT?  I think it was to do with the toDateTimeString function not being called at the time of writing this TODO.
# ValueError: time data '2020-01-03T04:45:25Z' does not match format '%Y-%m-%d %H:%M:%S'


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
        if not AstroSkyfield.__calculateCommon( utcNow, data, timeScale, observer, ephemeris[ AstroSkyfield.__SUN ], astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN ):
            astrobase.AstroBase.getEclipse( utcNow.utc_datetime().replace( tzinfo = None ), data, astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )

            key = ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )
            utcNowDateTime = utcNow.utc_datetime()
            t0 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day, utcNowDateTime.hour )
            t1 = timeScale.utc( utcNowDateTime.year,  utcNowDateTime.month + 7, utcNowDateTime.day, utcNowDateTime.hour ) # Look seven months ahead.
            t, y = almanac.find_discrete( t0, t1, almanac.seasons( ephemeris ) )
            t = t.utc_datetime()
            if "Equinox" in almanac.SEASON_EVENTS[ y[ 0 ] ]:
                data[ key + ( astrobase.AstroBase.DATA_TAG_EQUINOX, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_SOLSTICE, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )

            else:
                data[ key + ( astrobase.AstroBase.DATA_TAG_SOLSTICE, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_EQUINOX, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )


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
#TODO Guard against unknown stars...will occur when switching between backends.
#For now, do this check here...but really is this the best place or maybe it is the only possible place?
#Maybe the indicator needs to handle this...?   But the indicator should not be expected to expect a change in the list of stars.
            if star in astrobase.AstroBase.STARS:
#         mag = ephemeris.loc[ STARS[ star ] ].magnitude #TODO Leave here as we may need to compute the magnitude for the front end to submenu by mag.
                AstroSkyfield.__calculateCommon( utcNow, data, timeScale, observer, Star.from_dataframe( ephemeris.loc[ astrobase.AstroBase.STARS_TO_HIP[ star ] ] ), astrobase.AstroBase.BodyType.STAR, star )


    # https://github.com/skyfielders/python-skyfield/issues/196#issuecomment-418139819
    # The MPC might provide comet / minor planet data in a different format which Skyfield can read.
    @staticmethod
    def __calculateCometsOrMinorPlanets( utcNow, data, timeScale, observer, ephemeris, cometsOrMinorPlanets, cometOrMinorPlanetData, magnitudeMaximum ):
        pass #TODO


    @staticmethod
    def __calculateCommon( utcNow, data, timeScale, observer, body, astronomicalBodyType, nameTag ):
        neverUp = False
        key = ( astronomicalBodyType, nameTag )
        utcNowDateTime = utcNow.utc_datetime()
        t0 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day, utcNowDateTime.hour )
        t1 = timeScale.utc( utcNowDateTime.year, utcNowDateTime.month, utcNowDateTime.day + 2, utcNowDateTime.hour ) # Look two days ahead as one day ahead may miss the next rise or set.
        t, y = almanac.find_discrete( t0, t1, AstroSkyfield.__bodyrise_bodyset( observer, body ) ) # Original Skyfield function only supports sun rise/set, so have generalised to any body.
        if t:
            t = t.utc_datetime()
            if y[ 0 ]:
                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )

            else:
                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )
                apparent = observer.at( utcNow ).observe( body ).apparent()
                alt, az, bodyDistance = apparent.altaz()
                data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
                data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

        else:
            if AstroSkyfield.__bodyrise_bodyset( observer, body )( t0 ): # Taken and modified from Skyfield almanac.find_discrete.
                # Body is up (and so always up).
                apparent = observer.at( utcNow ).observe( body ).apparent()
                alt, az, bodyDistance = apparent.altaz()
                data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
                data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

            else:
                neverUp = True # Body is down (and so never up). 

        return neverUp


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


#TODO Might be useful:
# https://github.com/skyfielders/python-skyfield/issues/242
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
                AstroSkyfield.__calculateNextSatellitePass( utcNow, data, timeScale, key, satelliteData[ key ] )


    @staticmethod
    def __calculateNextSatellitePass( utcNow, data, timeScale, key, satelliteTLE ):
        pass
#         key = ( astrobase.AstroBase.BodyType.Satellite, " ".join( key ) )
#         currentDateTime = utcNow.J
#         endDateTime = timeScale.utc( ( utcNow.utc_datetime() + timedelta( days = 24 * 2 ) ).replace( tzinfo = pytz.UTC ) ).J #TODO Maybe pass this in as it won't change per satellite.
#TODO rise/set not yet implemented in Skyfield
# https://github.com/skyfielders/python-skyfield/issues/115



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
    @staticmethod
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
    @staticmethod
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


# AstroSkyfield.createStarEphemeris()
# AstroSkyfield.createPlanetEphemeris()