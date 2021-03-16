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


#TODO Do timing between each set of object types (planets, starts, comets, minor planets and satellites)
# comparing the time in PyEphem to that in Skyfield.


#TODO Have noticed the cache file sizes differ between PyEphem and Skyfield (comets / minor planets).
# Once Skyfield's orbital element engine is fixed so that it runs in similar time to PyEphem,
# print out the list of comets / minor planets that make the cut for magnitude filtering and compare.
# Determine why there are file size differences.


# When creating the stars/planets ephemerides (functions at the end of the file),
# uncomment the lines below as they are required!
# import gettext
# gettext.install( "astroskyfield" )


try:
    from skyfield import almanac, constants, eclipselib
    from skyfield.api import EarthSatellite, load, Star, wgs84
    from skyfield.data import hipparcos, mpc
    from skyfield.magnitudelib import planetary_magnitude
    import skyfield
    available = True

except ImportError:
    available = False

from distutils.version import LooseVersion

import astrobase, datetime, eclipse, importlib, io, locale, math, orbitalelement


class AstroSkyfield( astrobase.AstroBase ):

    __SKYFIELD_REQUIRED_VERSION = "1.35" # Required version, or better.

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


    # Unlike PyEphem, Skyfield does not provide a list of stars.
    #
    # However there is a list of named stars in the file skyfield/named_stars.py
    # which was sourced from the (now deleted) Wikipedia page "Hipparcos Catalogue":
    #    https://web.archive.org/web/20131012032059/https://en.wikipedia.org/wiki/List_of_stars_in_the_Hipparcos_Catalogue
    #
    # This list contains duplicates, misspellings and is not in use:
    #    https://github.com/skyfielders/python-skyfield/issues/304
    #
    # Consequently, use the more reliable and recent source from the ESA Hipparcos catalogue:
    #    https://www.cosmos.esa.int/web/hipparcos/common-star-names
    #
    # If this list is modified, regenerate the stars.dat.gz file.
    astrobase.AstroBase.STARS.extend( [
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
        "ZAURAK",
        "3C 273" ] )

    astrobase.AstroBase.STARS_TO_HIP.update( {
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
        "ZAURAK"            :   18543,
        "3C 273"            :   60936 } )

    astrobase.AstroBase.STAR_NAMES_TRANSLATIONS.update( {
        astrobase.AstroBase.STARS[ 0 ]  :   _( "Acamar" ),
        astrobase.AstroBase.STARS[ 1 ]  :   _( "Achernar" ),
        astrobase.AstroBase.STARS[ 2 ]  :   _( "Acrux" ),
        astrobase.AstroBase.STARS[ 3 ]  :   _( "Adhara" ),
        astrobase.AstroBase.STARS[ 4 ]  :   _( "Agena" ),
        astrobase.AstroBase.STARS[ 5 ]  :   _( "Albireo" ),
        astrobase.AstroBase.STARS[ 6 ]  :   _( "Alcor" ),
        astrobase.AstroBase.STARS[ 7 ]  :   _( "Alcyone" ),
        astrobase.AstroBase.STARS[ 8 ]  :   _( "Aldebaran" ),
        astrobase.AstroBase.STARS[ 9 ]  :   _( "Alderamin" ),
        astrobase.AstroBase.STARS[ 10 ] :   _( "Algenib" ),
        astrobase.AstroBase.STARS[ 11 ] :   _( "Algieba" ),
        astrobase.AstroBase.STARS[ 12 ] :   _( "Algol" ),
        astrobase.AstroBase.STARS[ 13 ] :   _( "Alhena" ),
        astrobase.AstroBase.STARS[ 14 ] :   _( "Alioth" ),
        astrobase.AstroBase.STARS[ 15 ] :   _( "Alkaid" ),
        astrobase.AstroBase.STARS[ 16 ] :   _( "Almaak" ),
        astrobase.AstroBase.STARS[ 17 ] :   _( "Alnair" ),
        astrobase.AstroBase.STARS[ 18 ] :   _( "Alnath" ),
        astrobase.AstroBase.STARS[ 19 ] :   _( "Alnilam" ),
        astrobase.AstroBase.STARS[ 20 ] :   _( "Alnitak" ),
        astrobase.AstroBase.STARS[ 21 ] :   _( "Alphard" ),
        astrobase.AstroBase.STARS[ 22 ] :   _( "Alphekka" ),
        astrobase.AstroBase.STARS[ 23 ] :   _( "Alpheratz" ),
        astrobase.AstroBase.STARS[ 24 ] :   _( "Alshain" ),
        astrobase.AstroBase.STARS[ 25 ] :   _( "Altair" ),
        astrobase.AstroBase.STARS[ 26 ] :   _( "Ankaa" ),
        astrobase.AstroBase.STARS[ 27 ] :   _( "Antares" ),
        astrobase.AstroBase.STARS[ 28 ] :   _( "Arcturus" ),
        astrobase.AstroBase.STARS[ 29 ] :   _( "Arneb" ),
        astrobase.AstroBase.STARS[ 30 ] :   _( "Babcock's Star" ),
        astrobase.AstroBase.STARS[ 31 ] :   _( "Barnard's Star" ),
        astrobase.AstroBase.STARS[ 32 ] :   _( "Bellatrix" ),
        astrobase.AstroBase.STARS[ 33 ] :   _( "Betelgeuse" ),
        astrobase.AstroBase.STARS[ 34 ] :   _( "Campbell's Star" ),
        astrobase.AstroBase.STARS[ 35 ] :   _( "Canopus" ),
        astrobase.AstroBase.STARS[ 36 ] :   _( "Capella" ),
        astrobase.AstroBase.STARS[ 37 ] :   _( "Caph" ),
        astrobase.AstroBase.STARS[ 38 ] :   _( "Castor" ),
        astrobase.AstroBase.STARS[ 39 ] :   _( "Cor Caroli" ),
        astrobase.AstroBase.STARS[ 40 ] :   _( "Cyg X-1" ),
        astrobase.AstroBase.STARS[ 41 ] :   _( "Deneb" ),
        astrobase.AstroBase.STARS[ 42 ] :   _( "Denebola" ),
        astrobase.AstroBase.STARS[ 43 ] :   _( "Diphda" ),
        astrobase.AstroBase.STARS[ 44 ] :   _( "Dubhe" ),
        astrobase.AstroBase.STARS[ 45 ] :   _( "Enif" ),
        astrobase.AstroBase.STARS[ 46 ] :   _( "Etamin" ),
        astrobase.AstroBase.STARS[ 47 ] :   _( "Fomalhaut" ),
        astrobase.AstroBase.STARS[ 48 ] :   _( "Groombridge 1830" ),
        astrobase.AstroBase.STARS[ 49 ] :   _( "Hadar" ),
        astrobase.AstroBase.STARS[ 50 ] :   _( "Hamal" ),
        astrobase.AstroBase.STARS[ 51 ] :   _( "Izar" ),
        astrobase.AstroBase.STARS[ 52 ] :   _( "Kapteyn's Star" ),
        astrobase.AstroBase.STARS[ 53 ] :   _( "Kaus Australis" ),
        astrobase.AstroBase.STARS[ 54 ] :   _( "Kocab" ),
        astrobase.AstroBase.STARS[ 55 ] :   _( "Kruger 60" ),
        astrobase.AstroBase.STARS[ 56 ] :   _( "Luyten's Star" ),
        astrobase.AstroBase.STARS[ 57 ] :   _( "Markab" ),
        astrobase.AstroBase.STARS[ 58 ] :   _( "Megrez" ),
        astrobase.AstroBase.STARS[ 59 ] :   _( "Menkar" ),
        astrobase.AstroBase.STARS[ 60 ] :   _( "Merak" ),
        astrobase.AstroBase.STARS[ 61 ] :   _( "Mintaka" ),
        astrobase.AstroBase.STARS[ 62 ] :   _( "Mira" ),
        astrobase.AstroBase.STARS[ 63 ] :   _( "Mirach" ),
        astrobase.AstroBase.STARS[ 64 ] :   _( "Mirphak" ),
        astrobase.AstroBase.STARS[ 65 ] :   _( "Mizar" ),
        astrobase.AstroBase.STARS[ 66 ] :   _( "Nihal" ),
        astrobase.AstroBase.STARS[ 67 ] :   _( "Nunki" ),
        astrobase.AstroBase.STARS[ 68 ] :   _( "Phad" ),
        astrobase.AstroBase.STARS[ 69 ] :   _( "Pleione" ),
        astrobase.AstroBase.STARS[ 70 ] :   _( "Polaris" ),
        astrobase.AstroBase.STARS[ 71 ] :   _( "Pollux" ),
        astrobase.AstroBase.STARS[ 72 ] :   _( "Procyon" ),
        astrobase.AstroBase.STARS[ 73 ] :   _( "Proxima" ),
        astrobase.AstroBase.STARS[ 74 ] :   _( "Rasalgethi" ),
        astrobase.AstroBase.STARS[ 75 ] :   _( "Rasalhague" ),
        astrobase.AstroBase.STARS[ 76 ] :   _( "Red Rectangle" ),
        astrobase.AstroBase.STARS[ 77 ] :   _( "Regulus" ),
        astrobase.AstroBase.STARS[ 78 ] :   _( "Rigel" ),
        astrobase.AstroBase.STARS[ 79 ] :   _( "Rigil Kent" ),
        astrobase.AstroBase.STARS[ 80 ] :   _( "Sadalmelik" ),
        astrobase.AstroBase.STARS[ 81 ] :   _( "Saiph" ),
        astrobase.AstroBase.STARS[ 82 ] :   _( "Scheat" ),
        astrobase.AstroBase.STARS[ 83 ] :   _( "Shaula" ),
        astrobase.AstroBase.STARS[ 84 ] :   _( "Shedir" ),
        astrobase.AstroBase.STARS[ 85 ] :   _( "Sheliak" ),
        astrobase.AstroBase.STARS[ 86 ] :   _( "Sirius" ),
        astrobase.AstroBase.STARS[ 87 ] :   _( "Spica" ),
        astrobase.AstroBase.STARS[ 88 ] :   _( "Tarazed" ),
        astrobase.AstroBase.STARS[ 89 ] :   _( "Thuban" ),
        astrobase.AstroBase.STARS[ 90 ] :   _( "Unukalhai" ),
        astrobase.AstroBase.STARS[ 91 ] :   _( "Van Maanen 2" ),
        astrobase.AstroBase.STARS[ 92 ] :   _( "Vega" ),
        astrobase.AstroBase.STARS[ 93 ] :   _( "Vindemiatrix" ),
        astrobase.AstroBase.STARS[ 94 ] :   _( "Zaurak" ),
        astrobase.AstroBase.STARS[ 95 ] :   _( "3C 273" ) } )

    # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
    astrobase.AstroBase.STAR_TAGS_TRANSLATIONS.update( {
        astrobase.AstroBase.STARS[ 0 ]  :   _( "ACAMAR" ),
        astrobase.AstroBase.STARS[ 1 ]  :   _( "ACHERNAR" ),
        astrobase.AstroBase.STARS[ 2 ]  :   _( "ACRUX" ),
        astrobase.AstroBase.STARS[ 3 ]  :   _( "ADHARA" ),
        astrobase.AstroBase.STARS[ 4 ]  :   _( "AGENA" ),
        astrobase.AstroBase.STARS[ 5 ]  :   _( "ALBIREO" ),
        astrobase.AstroBase.STARS[ 6 ]  :   _( "ALCOR" ),
        astrobase.AstroBase.STARS[ 7 ]  :   _( "ALCYONE" ),
        astrobase.AstroBase.STARS[ 8 ]  :   _( "ALDEBARAN" ),
        astrobase.AstroBase.STARS[ 9 ]  :   _( "ALDERAMIN" ),
        astrobase.AstroBase.STARS[ 10 ] :   _( "ALGENIB" ),
        astrobase.AstroBase.STARS[ 11 ] :   _( "ALGIEBA" ),
        astrobase.AstroBase.STARS[ 12 ] :   _( "ALGOL" ),
        astrobase.AstroBase.STARS[ 13 ] :   _( "ALHENA" ),
        astrobase.AstroBase.STARS[ 14 ] :   _( "ALIOTH" ),
        astrobase.AstroBase.STARS[ 15 ] :   _( "ALKAID" ),
        astrobase.AstroBase.STARS[ 16 ] :   _( "ALMAAK" ),
        astrobase.AstroBase.STARS[ 17 ] :   _( "ALNAIR" ),
        astrobase.AstroBase.STARS[ 18 ] :   _( "ALNATH" ),
        astrobase.AstroBase.STARS[ 19 ] :   _( "ALNILAM" ),
        astrobase.AstroBase.STARS[ 20 ] :   _( "ALNITAK" ),
        astrobase.AstroBase.STARS[ 21 ] :   _( "ALPHARD" ),
        astrobase.AstroBase.STARS[ 22 ] :   _( "ALPHEKKA" ),
        astrobase.AstroBase.STARS[ 23 ] :   _( "ALPHERATZ" ),
        astrobase.AstroBase.STARS[ 24 ] :   _( "ALSHAIN" ),
        astrobase.AstroBase.STARS[ 25 ] :   _( "ALTAIR" ),
        astrobase.AstroBase.STARS[ 26 ] :   _( "ANKAA" ),
        astrobase.AstroBase.STARS[ 27 ] :   _( "ANTARES" ),
        astrobase.AstroBase.STARS[ 28 ] :   _( "ARCTURUS" ),
        astrobase.AstroBase.STARS[ 29 ] :   _( "ARNEB" ),
        astrobase.AstroBase.STARS[ 30 ] :   _( "BABCOCK'S STAR" ),
        astrobase.AstroBase.STARS[ 31 ] :   _( "BARNARD'S STAR" ),
        astrobase.AstroBase.STARS[ 32 ] :   _( "BELLATRIX" ),
        astrobase.AstroBase.STARS[ 33 ] :   _( "BETELGEUSE" ),
        astrobase.AstroBase.STARS[ 34 ] :   _( "CAMPBELL'S STAR" ),
        astrobase.AstroBase.STARS[ 35 ] :   _( "CANOPUS" ),
        astrobase.AstroBase.STARS[ 36 ] :   _( "CAPELLA" ),
        astrobase.AstroBase.STARS[ 37 ] :   _( "CAPH" ),
        astrobase.AstroBase.STARS[ 38 ] :   _( "CASTOR" ),
        astrobase.AstroBase.STARS[ 39 ] :   _( "COR CAROLI" ),
        astrobase.AstroBase.STARS[ 40 ] :   _( "CYG X-1" ),
        astrobase.AstroBase.STARS[ 41 ] :   _( "DENEB" ),
        astrobase.AstroBase.STARS[ 42 ] :   _( "DENEBOLA" ),
        astrobase.AstroBase.STARS[ 43 ] :   _( "DIPHDA" ),
        astrobase.AstroBase.STARS[ 44 ] :   _( "DUBHE" ),
        astrobase.AstroBase.STARS[ 45 ] :   _( "ENIF" ),
        astrobase.AstroBase.STARS[ 46 ] :   _( "ETAMIN" ),
        astrobase.AstroBase.STARS[ 47 ] :   _( "FOMALHAUT" ),
        astrobase.AstroBase.STARS[ 48 ] :   _( "GROOMBRIDGE 1830" ),
        astrobase.AstroBase.STARS[ 49 ] :   _( "HADAR" ),
        astrobase.AstroBase.STARS[ 50 ] :   _( "HAMAL" ),
        astrobase.AstroBase.STARS[ 51 ] :   _( "IZAR" ),
        astrobase.AstroBase.STARS[ 52 ] :   _( "KAPTEYN'S STAR" ),
        astrobase.AstroBase.STARS[ 53 ] :   _( "KAUS AUSTRALIS" ),
        astrobase.AstroBase.STARS[ 54 ] :   _( "KOCAB" ),
        astrobase.AstroBase.STARS[ 55 ] :   _( "KRUGER 60" ),
        astrobase.AstroBase.STARS[ 56 ] :   _( "LUYTEN'S STAR" ),
        astrobase.AstroBase.STARS[ 57 ] :   _( "MARKAB" ),
        astrobase.AstroBase.STARS[ 58 ] :   _( "MEGREZ" ),
        astrobase.AstroBase.STARS[ 59 ] :   _( "MENKAR" ),
        astrobase.AstroBase.STARS[ 60 ] :   _( "MERAK" ),
        astrobase.AstroBase.STARS[ 61 ] :   _( "MINTAKA" ),
        astrobase.AstroBase.STARS[ 62 ] :   _( "MIRA" ),
        astrobase.AstroBase.STARS[ 63 ] :   _( "MIRACH" ),
        astrobase.AstroBase.STARS[ 64 ] :   _( "MIRPHAK" ),
        astrobase.AstroBase.STARS[ 65 ] :   _( "MIZAR" ),
        astrobase.AstroBase.STARS[ 66 ] :   _( "NIHAL" ),
        astrobase.AstroBase.STARS[ 67 ] :   _( "NUNKI" ),
        astrobase.AstroBase.STARS[ 68 ] :   _( "PHAD" ),
        astrobase.AstroBase.STARS[ 69 ] :   _( "PLEIONE" ),
        astrobase.AstroBase.STARS[ 70 ] :   _( "POLARIS" ),
        astrobase.AstroBase.STARS[ 71 ] :   _( "POLLUX" ),
        astrobase.AstroBase.STARS[ 72 ] :   _( "PROCYON" ),
        astrobase.AstroBase.STARS[ 73 ] :   _( "PROXIMA" ),
        astrobase.AstroBase.STARS[ 74 ] :   _( "RASALGETHI" ),
        astrobase.AstroBase.STARS[ 75 ] :   _( "RASALHAGUE" ),
        astrobase.AstroBase.STARS[ 76 ] :   _( "RED RECTANGLE" ),
        astrobase.AstroBase.STARS[ 77 ] :   _( "REGULUS" ),
        astrobase.AstroBase.STARS[ 78 ] :   _( "RIGEL" ),
        astrobase.AstroBase.STARS[ 79 ] :   _( "RIGIL KENT" ),
        astrobase.AstroBase.STARS[ 80 ] :   _( "SADALMELIK" ),
        astrobase.AstroBase.STARS[ 81 ] :   _( "SAIPH" ),
        astrobase.AstroBase.STARS[ 82 ] :   _( "SCHEAT" ),
        astrobase.AstroBase.STARS[ 83 ] :   _( "SHAULA" ),
        astrobase.AstroBase.STARS[ 84 ] :   _( "SHEDIR" ),
        astrobase.AstroBase.STARS[ 85 ] :   _( "SHELIAK" ),
        astrobase.AstroBase.STARS[ 86 ] :   _( "SIRIUS" ),
        astrobase.AstroBase.STARS[ 87 ] :   _( "SPICA" ),
        astrobase.AstroBase.STARS[ 88 ] :   _( "TARAZED" ),
        astrobase.AstroBase.STARS[ 89 ] :   _( "THUBAN" ),
        astrobase.AstroBase.STARS[ 90 ] :   _( "UNUKALHAI" ),
        astrobase.AstroBase.STARS[ 91 ] :   _( "VAN MAANEN 2" ),
        astrobase.AstroBase.STARS[ 92 ] :   _( "VEGA" ),
        astrobase.AstroBase.STARS[ 93 ] :   _( "VINDEMIATRIX" ),
        astrobase.AstroBase.STARS[ 94 ] :   _( "ZAURAK" ),
        astrobase.AstroBase.STARS[ 95 ] :   _( "3C 273" ) } )

    # Taken from ephem/cities.py as Skyfield does not provide a list of cities.
    #    https://github.com/skyfielders/python-skyfield/issues/316
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
    def calculate( utcNow,
                   latitude, longitude, elevation,
                   planets,
                   stars,
                   satellites, satelliteData,
                   comets, cometData,
                   minorPlanets, minorPlanetData,
                   magnitudeMaximum,
                   logging ):

        data = { }

        timeScale = load.timescale( builtin = True )
        now = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
        nowPlusThirtySixHours = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour + 36 )
        nowPlusTwoDays = timeScale.utc( utcNow.year, utcNow.month, utcNow.day + 2 )
        nowPlusThirtyOneDays = timeScale.utc( utcNow.year, utcNow.month, utcNow.day + 31 )
        nowPlusSevenMonths = timeScale.utc( utcNow.year, utcNow.month + 7, utcNow.day )
        nowPlusOneYear = timeScale.utc( utcNow.year + 1, utcNow.month, utcNow.day )

        location = wgs84.latlon( latitude, longitude, elevation )
        ephemerisPlanets = load( AstroSkyfield.__EPHEMERIS_PLANETS )
        locationAtNow = ( ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ] + location ).at( now )

        AstroSkyfield.__calculateMoon( now, nowPlusTwoDays, nowPlusThirtyOneDays, nowPlusOneYear, data, location, locationAtNow, latitude, longitude, ephemerisPlanets )
        AstroSkyfield.__calculateSun( now, nowPlusTwoDays, nowPlusSevenMonths, data, location, locationAtNow, ephemerisPlanets )
        AstroSkyfield.__calculatePlanets( now, nowPlusTwoDays, data, location, locationAtNow, ephemerisPlanets, planets, magnitudeMaximum )

        with load.open( AstroSkyfield.__EPHEMERIS_STARS ) as f:
            ephemerisStars = hipparcos.load_dataframe( f )

        AstroSkyfield.__calculateStars( now, nowPlusTwoDays, data, location, locationAtNow, ephemerisPlanets, ephemerisStars, stars, magnitudeMaximum )

        AstroSkyfield.__calculateOrbitalElements( now, nowPlusTwoDays, data, timeScale, location, locationAtNow, ephemerisPlanets,
                                                  astrobase.AstroBase.BodyType.COMET, comets, cometData, magnitudeMaximum,
                                                  logging )

        AstroSkyfield.__calculateOrbitalElements( now, nowPlusTwoDays, data, timeScale, location, locationAtNow, ephemerisPlanets,
                                                  astrobase.AstroBase.BodyType.MINOR_PLANET, minorPlanets, minorPlanetData, magnitudeMaximum,
                                                  logging )

        AstroSkyfield.__calculateSatellites( now, nowPlusThirtySixHours, data, timeScale, location, locationAtNow, ephemerisPlanets, satellites, satelliteData )

        return data


    @staticmethod
    def getAvailabilityMessage():
        message = None
        if not available:
            message = _( "Skyfield could not be found. Install using:\n\n" + \
                         "sudo apt-get install -y python3-pip\nsudo pip3 install --upgrade jplephem numpy pandas pip pytz skyfield" )

        return message


    @staticmethod
    def getCities(): return sorted( AstroSkyfield._city_data.keys(), key = locale.strxfrm )


    @staticmethod
    def getCredit(): return _( "Calculations courtesy of Skyfield. https://rhodesmill.org/skyfield" )


    @staticmethod
    def getLatitudeLongitudeElevation( city ): return AstroSkyfield._city_data.get( city )[ 0 ], \
                                                      AstroSkyfield._city_data.get( city )[ 1 ], \
                                                      AstroSkyfield._city_data.get( city )[ 2 ]


#TODO Issue logged with regard to slow speed of processing comets / minor planets:
# https://github.com/skyfielders/python-skyfield/issues/490
    @staticmethod
    def getOrbitalElementsLessThanMagnitude( utcNow, orbitalElementData, magnitudeMaximum, bodyType, latitude, longitude, elevation, logging ):
        # Skyfield loads the orbital element data into a dataframe from a file.
        # Need to take the orbital element data and write to a memory file object.
        with io.BytesIO() as f:
            for value in orbitalElementData.values():
                f.write( ( value.getData() + '\n' ).encode() )

            f.seek( 0 )

            if bodyType == astrobase.AstroBase.BodyType.COMET:
                dataframe = mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )
                orbitCalculationFunction = "comet_orbit"

            else:
                dataframe = mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
                orbitCalculationFunction = "mpcorb_orbit"

                # Remove bad data https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
                dataframe = dataframe[ ~dataframe.semimajor_axis_au.isnull() ]

#TODO Can this be rewritten as per the calculate orbital elements function below?
        results = { }
        ephemerisPlanets = load( AstroSkyfield.__EPHEMERIS_PLANETS )
        timeScale = load.timescale( builtin = True )
        t = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
        sun = ephemerisPlanets[ AstroSkyfield.__SUN ]
        earth = ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ]
        location = wgs84.latlon( latitude, longitude, elevation )
        alt, az, earthSunDistance = ( earth + location ).at( t ).observe( sun ).apparent().altaz()
        for name, row in dataframe.iterrows():
            body = sun + getattr( importlib.import_module( "skyfield.data.mpc" ), orbitCalculationFunction )( row, timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )
            ra, dec, earthBodyDistance = ( earth + location ).at( t ).observe( body ).radec()
            ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()

            try:
                if orbitCalculationFunction == "comet_orbit":
                    message = "Error computing apparent magnitude for comet: " + name
                    apparentMagnitude = astrobase.AstroBase.getApparentMagnitude_gk( row[ "magnitude_g" ], row[ "magnitude_k" ], 
                                                                                     earthBodyDistance.au, sunBodyDistance.au )

                else:
                    message = "Error computing apparent magnitude for minor planet: " + name
                    apparentMagnitude = astrobase.AstroBase.getApparentMagnitude_HG( row[ "magnitude_H" ], row[ "magnitude_G" ], 
                                                                                     earthBodyDistance.au, sunBodyDistance.au, earthSunDistance.au )

                if apparentMagnitude and apparentMagnitude >= astrobase.AstroBase.MAGNITUDE_MINIMUM and apparentMagnitude <= magnitudeMaximum:
                    results[ name.upper() ] = orbitalElementData[ name.upper() ]

            except Exception as e:
                logging.error( message )
                logging.exception( e )

        return results


    @staticmethod
    def getVersionMessage():
        message = None
        if LooseVersion( skyfield.__version__ ) < LooseVersion( AstroSkyfield.__SKYFIELD_REQUIRED_VERSION ):
            message = _( "Skyfield must be version {0} or greater. Please upgrade:\n\n" + \
                         "sudo apt-get install -y python3-pip\nsudo pip3 install --upgrade jplephem numpy pandas pip pytz skyfield" ).format( AstroSkyfield.__SKYFIELD_REQUIRED_VERSION )

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
    def __calculateMoon( utcNow, utcNowPlusTwoDays, utcNowPlusThirtyOneDays, utcNowPlusOneYear, data, location, locationAtNow, latitude, longitude, ephemerisPlanets ):
        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        illumination = int( almanac.fraction_illuminated( ephemerisPlanets, AstroSkyfield.__MOON, utcNow ) * 100 )
        data[ key + ( astrobase.AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( illumination ) # Needed for icon.

        sunRA, sunDec, earthDistance = locationAtNow.observe( ephemerisPlanets[ AstroSkyfield.__SUN ] ).apparent().radec()
        moonRA, moonDec, earthDistance = locationAtNow.observe( ephemerisPlanets[ AstroSkyfield.__MOON ] ).apparent().radec()
        brightLimb = astrobase.AstroBase.getZenithAngleOfBrightLimb( utcNow.utc_datetime(), 
                                                                     sunRA.radians, sunDec.radians, 
                                                                     moonRA.radians, moonDec.radians, 
                                                                     math.radians( latitude ), math.radians( longitude ) )
        data[ key + ( astrobase.AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( brightLimb ) # Needed for icon.

        t, y = almanac.find_discrete( utcNow, utcNowPlusThirtyOneDays, almanac.moon_phases( ephemerisPlanets ) )
        moonPhases = [ almanac.MOON_PHASES[ yi ] for yi in y ]
        moonPhaseDateTimes = t.utc_datetime()
        nextNewMoonDateTime = moonPhaseDateTimes[ moonPhases.index( almanac.MOON_PHASES[ 0 ] ) ] # New moon.
        nextFullMoonDateTime = moonPhaseDateTimes[ moonPhases.index( almanac.MOON_PHASES[ 2 ] ) ] # Full moon.
        lunarPhase = astrobase.AstroBase.getLunarPhase( int( float ( illumination ) ), nextFullMoonDateTime, nextNewMoonDateTime )
        data[ key + ( astrobase.AstroBase.DATA_TAG_PHASE, ) ] = lunarPhase # Need for notification.

        neverUp = AstroSkyfield.__calculateCommon( utcNow, utcNowPlusTwoDays,
                                                   data, ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON ),
                                                   location, locationAtNow,
                                                   ephemerisPlanets,
                                                   ephemerisPlanets[ AstroSkyfield.__MOON ] )

        if not neverUp:
            data[ key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 1 ] ) ) ] )
            data[ key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 2 ] ) ) ] )
            data[ key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 3 ] ) ) ] )
            data[ key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ] = astrobase.AstroBase.toDateTimeString( moonPhaseDateTimes[ ( moonPhases.index( almanac.MOON_PHASES[ 0 ] ) ) ] )

            t, y, details = eclipselib.lunar_eclipses( utcNow, utcNowPlusOneYear, ephemerisPlanets )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = t[ 0 ].utc_strftime( astrobase.AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipselib.LUNAR_ECLIPSES[ y[ 0 ] ]


    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    # http://www.ga.gov.au/geodesy/astro/sunrise.jsp
    # http://www.geoastro.de/elevaz/index.htm
    # http://www.geoastro.de/SME/index.htm
    # http://www.geoastro.de/altazsunmoon/index.htm
    # http://futureboy.us/fsp/sun.fsp
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    @staticmethod
    def __calculateSun( utcNow, utcNowPlusTwoDays, utcNowPlusSevenMonths, data, location, locationAtNow, ephemerisPlanets ):
        neverUp = AstroSkyfield.__calculateCommon( utcNow, utcNowPlusTwoDays, 
                                                   data, ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN ), 
                                                   location, locationAtNow,
                                                   ephemerisPlanets, ephemerisPlanets[ AstroSkyfield.__SUN ] )

        if not neverUp:
            key = ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )
            t, y = almanac.find_discrete( utcNow, utcNowPlusSevenMonths, almanac.seasons( ephemerisPlanets ) )
            t = t.utc_datetime()
            if almanac.SEASON_EVENTS[ 0 ] in almanac.SEASON_EVENTS[ y[ 0 ] ] or almanac.SEASON_EVENTS[ 2 ] in almanac.SEASON_EVENTS[ y[ 0 ] ]:
                data[ key + ( astrobase.AstroBase.DATA_TAG_EQUINOX, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_SOLSTICE, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )

            else:
                data[ key + ( astrobase.AstroBase.DATA_TAG_SOLSTICE, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_EQUINOX, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )

#TODO Once solar eclipses are implemented in Skyfield, replace the code below with similar functionality to lunar eclipses above.        
            dateTime, eclipseType, latitude, longitude = eclipse.getEclipse( utcNow.utc_datetime(), False )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTime
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseType
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude



    # http://www.geoastro.de/planets/index.html
    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    @staticmethod
    def __calculatePlanets( utcNow, utcNowPlusTwoDays, data, location, locationAtNow, ephemerisPlanets, planets, magnitudeMaximum ):
        for planet in planets:
            if planet == astrobase.AstroBase.PLANET_MERCURY or \
               planet == astrobase.AstroBase.PLANET_VENUS or \
               planet == astrobase.AstroBase.PLANET_JUPITER or \
               planet == astrobase.AstroBase.PLANET_URANUS:
                apparentMagnitude = planetary_magnitude( ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ].at( utcNow ).observe( ephemerisPlanets[ AstroSkyfield.__PLANET_MAPPINGS[ planet ] ] ) )

            else:
                #TODO Hard coded until Skyfield calculates apparent magnitude...
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
                AstroSkyfield.__calculateCommon( utcNow, utcNowPlusTwoDays,
                                                 data, ( astrobase.AstroBase.BodyType.PLANET, planet ),
                                                 location, locationAtNow,
                                                 ephemerisPlanets, ephemerisPlanets[ AstroSkyfield.__PLANET_MAPPINGS[ planet ] ] )


    @staticmethod
    def __calculateStars( utcNow, utcNowPlusTwoDays, data, location, locationAtNow, ephemerisPlanets, ephemerisStars, stars, magnitudeMaximum ):
        for star in stars:
            if star in astrobase.AstroBase.STARS:
                theStar = ephemerisStars.loc[ astrobase.AstroBase.STARS_TO_HIP[ star ] ]
                if theStar.magnitude <= magnitudeMaximum:
                    AstroSkyfield.__calculateCommon( utcNow, utcNowPlusTwoDays,
                                                     data, ( astrobase.AstroBase.BodyType.STAR, star ),
                                                     location, locationAtNow,
                                                     ephemerisPlanets, Star.from_dataframe( theStar ) )


    @staticmethod
    def __calculateOrbitalElements( utcNow, utcNowPlusTwoDays, data, timeScale, location, locationAtNow, ephemerisPlanets, bodyType, orbitalElements, orbitalElementData, magnitudeMaximum, logging ):
        # Skyfield loads the orbital element data into a dataframe from a file.
        # Need to take the orbital element data and write to a memory file object.
        with io.BytesIO() as f:
            for key in orbitalElements:
                if key in orbitalElementData:
                    f.write( ( orbitalElementData[ key ].getData() + '\n' ).encode() )

            f.seek( 0 )

            if bodyType == astrobase.AstroBase.BodyType.COMET:
                dataframe = mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )
                orbitCalculationFunction = "comet_orbit"
                message = "Error computing apparent magnitude for comet: "

            else:
                dataframe = mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
                orbitCalculationFunction = "mpcorb_orbit"
                message = "Error computing apparent magnitude for minor planet: "

#TODO The block below is identical save for one line in the above function getOrbitalElementsLessThanMagnitude.
# Maybe have a nested function in each which implements the single differing line and pass that in to a third function which implements the common code block?
        alt, az, earthSunDistance = ( ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ] + location ).at( utcNow ).observe( ephemerisPlanets[ AstroSkyfield.__SUN ] ).apparent().altaz()
        for name, row in dataframe.iterrows():
            body = ephemerisPlanets[ AstroSkyfield.__SUN ] + getattr( importlib.import_module( "skyfield.data.mpc" ), orbitCalculationFunction )( row, timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )
            ra, dec, earthBodyDistance = ( ephemerisPlanets[ AstroSkyfield.__PLANET_EARTH ] + location ).at( utcNow ).observe( body ).radec()
            ra, dec, sunBodyDistance = ephemerisPlanets[ AstroSkyfield.__SUN ].at( utcNow ).observe( body ).radec()

            try:
                if orbitCalculationFunction == "comet_orbit":
                    apparentMagnitude = astrobase.AstroBase.getApparentMagnitude_gk( row[ "magnitude_g" ], row[ "magnitude_k" ], 
                                                                                     earthBodyDistance.au, sunBodyDistance.au )

                else:
                    apparentMagnitude = astrobase.AstroBase.getApparentMagnitude_HG( row[ "magnitude_H" ], row[ "magnitude_G" ], 
                                                                                     earthBodyDistance.au, sunBodyDistance.au, earthSunDistance.au )

                if apparentMagnitude and apparentMagnitude >= astrobase.AstroBase.MAGNITUDE_MINIMUM and apparentMagnitude <= magnitudeMaximum:
                    AstroSkyfield.__calculateCommon( utcNow, utcNowPlusTwoDays, data, ( bodyType, key ), location, locationAtNow, ephemerisPlanets, body )

            except Exception as e:
                logging.error( message + name )
                logging.exception( e )


    @staticmethod
    def __calculateCommon( utcNow, utcNowPlusTwoDays, data, key, location, locationAtNow, ephemerisPlanets, body ):
        neverUp = False
        t, y = almanac.find_discrete( utcNow, utcNowPlusTwoDays, almanac.risings_and_settings( ephemerisPlanets, body, location ) )
        if len( t ) >= 2: # Ensure there is at least one rise and one set.
            t = t.utc_datetime()
            if y[ 0 ]:
                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )

            else:
                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 1 ] )
                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( t[ 0 ] )

            alt, az, bodyDistance = locationAtNow.observe( body ).apparent().altaz()
            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

        else:
            if almanac.risings_and_settings( ephemerisPlanets, body, location )( utcNow ): # Body is up (and so always up).
                alt, az, bodyDistance = locationAtNow.observe( body ).apparent().altaz()
                data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
                data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

            else:
                neverUp = True # Body is down (and so never up).

        return neverUp


    # Refer to
    #    https://github.com/skyfielders/python-skyfield/issues/327
    #
    # Use TLE data collated by Dr T S Kelso
    # http://celestrak.com/NORAD/elements
    #
    # Other sources/background:
    #    http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
    #    http://spotthestation.nasa.gov/sightings
    #    http://www.n2yo.com
    #    http://www.heavens-above.com
    #    http://in-the-sky.org
    #    https://uphere.space/satellites
    #    https://www.amsat.org/track
    #    https://tracksat.space
    #    https://g7vrd.co.uk/public-satellite-pass-rest-api    
    @staticmethod
#TODO Seems to calculate some passes very late after sunset (or very early before sunrise) when the satellite surely cannot be sunlit.
# https://github.com/skyfielders/python-skyfield/issues/558    
    def __calculateSatellites( utcNow, utcNowPlusThirtySixHours, data, timeScale, location, ephemerisPlanets, satellites, satelliteData ):
        for satellite in satellites:
            if satellite in satelliteData:
                foundVisiblePass = False
                earthSatellite = EarthSatellite( satelliteData[ satellite ].getLine1(), satelliteData[ satellite ].getLine2(), satelliteData[ satellite ].getName(), timeScale )
                t, events = earthSatellite.find_events( location, utcNow, utcNowPlusThirtySixHours, altitude_degrees = 30.0 ) # https://github.com/skyfielders/python-skyfield/issues/327#issuecomment-675123392
                riseTime = None
                culminateTimes = [ ] # Culminate may occur more than once, so collect them all.
                for ti, event in zip( t, events ):
                    if event == 0: # Rise
                        riseTime = ti

                    elif event == 1: # Culminate
                        culminateTimes.append( ti )

                    else: # Set
                        if riseTime is not None and len( culminateTimes ) > 0:
                            for culmination in culminateTimes:
                                if earthSatellite.at( culmination ).is_sunlit( ephemerisPlanets ) and \
                                   almanac.dark_twilight_day( ephemerisPlanets, location )( culmination ) < 4:
                                    key = ( astrobase.AstroBase.BodyType.SATELLITE, satellite )
                                    data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( riseTime.utc_datetime() )
                                    alt, az, bodyDistance = ( earthSatellite - location ).at( riseTime ).altaz()
                                    data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH, ) ] = str( az.radians )
                                    data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( ti.utc_datetime() )
                                    alt, az, bodyDistance = ( earthSatellite - location ).at( ti ).altaz()
                                    data[ key + ( astrobase.AstroBase.DATA_TAG_SET_AZIMUTH, ) ] = str( az.radians )
                                    foundVisiblePass = True
                                    break

                            riseTime = None
                            culminateTimes = [ ]

                        else:
                            riseTime = None
                            culminateTimes = [ ]

                    if foundVisiblePass:
                        break


    # Load the Hipparcos catalogue and filter out stars not on common name list:
    #    https://www.cosmos.esa.int/web/hipparcos/common-star-names
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
        with load.open( catalogue, "rb" ) as inFile, gzip.open( AstroSkyfield.__EPHEMERIS_STARS, "wb" ) as outFile:
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
    # The ephemeris date range is from the date of creation plus ten years.
    #
    # Alternate method to create the ephemeris, download a .bsp and use spkmerge to create a smaller subset.
    # Refer to
    #    https://github.com/skyfielders/python-skyfield/issues/123
    #    https://github.com/skyfielders/python-skyfield/issues/231#issuecomment-450507640
    @staticmethod
    def createEphemerisPlanets():
        from dateutil.relativedelta import relativedelta
        import os, subprocess, urllib

        ephemerisFile = "de438.bsp"
        ephemerisURL = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/" + ephemerisFile
        if not os.path.isfile( ephemerisFile ):
            print( "Could not locate", ephemerisFile )
            print( "Downloading planet ephemeris..." )
            urllib.request.urlretrieve ( ephemerisURL, ephemerisFile )

        if os.path.isfile( AstroSkyfield.__EPHEMERIS_PLANETS ):
            os.remove( AstroSkyfield.__EPHEMERIS_PLANETS )

        today = datetime.date.today()
        oneMonthPriorToToday = today - relativedelta( months = 1 ) # Start earlier than today (calculations such as lunar eclipses search from prior to the start date).
        fiveYearsFromToday = today.replace( year = today.year + 5 )
        dateFormat = "%Y/%m/%d"
        command = "python3 -m jplephem excerpt " + \
                  oneMonthPriorToToday.strftime( dateFormat ) + " " + \
                  fiveYearsFromToday.strftime( dateFormat ) + " " + \
                  ephemerisFile + " " + AstroSkyfield.__EPHEMERIS_PLANETS

        try:
            print( "Creating planet ephemeris..." )
            print( "\t", command )
            subprocess.call( command, shell = True )
            completed = True

        except subprocess.CalledProcessError as e:
            print( e )
            completed = False

        if completed:
            print( "Created", AstroSkyfield.__EPHEMERIS_PLANETS )


# Functions to create the stars/planets ephemerides.
# Must uncomment the gettext lines at the top of the file!
# AstroSkyfield.createEphemerisStars()
# AstroSkyfield.createEphemerisPlanets()