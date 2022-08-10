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


#TODO If/when switching to Skyfield (PyEphem may still be chosen as a backend by the user),
# Will need several changes:
#
#   Add astroskyfield.py to build-debian and debian/install.
#
#   Remove astropyephem.py from build-debian and debian/install (if ONLY running Skyfield).
#
#   Add to debian/postinst the line
#       sudo pip3 install --ignore-installed --upgrade pandas pip skyfield || true
# 
# https://askubuntu.com/questions/260978/add-custom-steps-to-source-packages-debian-package-postinst
# https://askubuntu.com/questions/1263305/launchpad-builderror-cant-locate-debian-debhelper-sequence-python3-pm
#
# Will also need to include the latest versions of planets.bsp and stars.dat (might need add to packaging/debian/install).


# import gettext ; gettext.install( "astroskyfield" ) # Uncomment to create/update the stars/planets ephemerides (see end of the file).

try:
    from skyfield import almanac, constants, eclipselib
    from skyfield.api import EarthSatellite, load, Star, wgs84
    from skyfield.data import hipparcos, mpc
    from skyfield.magnitudelib import planetary_magnitude
    from skyfield.trigonometry import position_angle_of
    import skyfield
    available = True

except ImportError:
    available = False

from astrobase import AstroBase
from distutils.version import LooseVersion

import datetime, eclipse, importlib, io, locale, math


class AstroSkyfield( AstroBase ):

    # Planet epehemeris has been created with a reduced date range:
    #
    #    python3 -m jplephem excerpt startDate_YYYY/MM/DD endDate_YYYY/MM/DD inFile.bsp outFile.bsp
    #
    #    python3 -m jplephem excerpt 2022/07/10 2027/08/10 de440s.bsp planets.bsp
    #
    # Set the start date one month earlier than today to avoid problems:
    #     https://github.com/skyfielders/python-skyfield/issues/531
    #
    # Requires jplephem:
    #    https://pypi.org/project/jplephem
    #
    # Source for input BSP files:
    #    https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets
    #
    # References:
    #    https://github.com/skyfielders/python-skyfield/issues/123
    #    ftp://ssd.jpl.nasa.gov/pub/eph/planets/README.txt
    #    ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/ascii_format.txt
    #
    # Alternate method: Download a .bsp and use spkmerge to create a smaller subset:
    #    https://github.com/skyfielders/python-skyfield/issues/123
    #    https://github.com/skyfielders/python-skyfield/issues/231#issuecomment-450507640
    __EPHEMERIS_PLANETS_FILE = "planets.bsp"
    __EPHEMERIS_PLANETS = load( __EPHEMERIS_PLANETS_FILE )

    __EPHEMERIS_STARS_FILE = "stars.dat" # Created using createEphemerisStars.py to contain only commonly named stars.
    with load.open( __EPHEMERIS_STARS_FILE ) as f:
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


    # Skyfield does not provide a list of stars.
    #
    # However there is a list of named stars in the file skyfield/named_stars.py
    # which was gleaned from the (now deleted) Wikipedia page "Hipparcos Catalogue":
    #    https://web.archive.org/web/20131012032059/https://en.wikipedia.org/wiki/List_of_stars_in_the_Hipparcos_Catalogue
    #
    # Unfortunately, this list contains duplicates, misspellings and is not in use:
    #    https://github.com/skyfielders/python-skyfield/issues/304
    #
    # Better to use the more reliable and recent source from the ESA Hipparcos catalogue:
    #    https://www.cosmos.esa.int/web/hipparcos/common-star-names
    #
    # If the list below is ever modified, regenerate the stars.dat.gz file.
    AstroBase.STARS.extend( [
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


    AstroBase.STARS_TO_HIP.update( {
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


    AstroBase.STAR_NAMES_TRANSLATIONS.update( {
        AstroBase.STARS[ 0 ]  :   _( "Acamar" ),
        AstroBase.STARS[ 1 ]  :   _( "Achernar" ),
        AstroBase.STARS[ 2 ]  :   _( "Acrux" ),
        AstroBase.STARS[ 3 ]  :   _( "Adhara" ),
        AstroBase.STARS[ 4 ]  :   _( "Agena" ),
        AstroBase.STARS[ 5 ]  :   _( "Albireo" ),
        AstroBase.STARS[ 6 ]  :   _( "Alcor" ),
        AstroBase.STARS[ 7 ]  :   _( "Alcyone" ),
        AstroBase.STARS[ 8 ]  :   _( "Aldebaran" ),
        AstroBase.STARS[ 9 ]  :   _( "Alderamin" ),
        AstroBase.STARS[ 10 ] :   _( "Algenib" ),
        AstroBase.STARS[ 11 ] :   _( "Algieba" ),
        AstroBase.STARS[ 12 ] :   _( "Algol" ),
        AstroBase.STARS[ 13 ] :   _( "Alhena" ),
        AstroBase.STARS[ 14 ] :   _( "Alioth" ),
        AstroBase.STARS[ 15 ] :   _( "Alkaid" ),
        AstroBase.STARS[ 16 ] :   _( "Almaak" ),
        AstroBase.STARS[ 17 ] :   _( "Alnair" ),
        AstroBase.STARS[ 18 ] :   _( "Alnath" ),
        AstroBase.STARS[ 19 ] :   _( "Alnilam" ),
        AstroBase.STARS[ 20 ] :   _( "Alnitak" ),
        AstroBase.STARS[ 21 ] :   _( "Alphard" ),
        AstroBase.STARS[ 22 ] :   _( "Alphekka" ),
        AstroBase.STARS[ 23 ] :   _( "Alpheratz" ),
        AstroBase.STARS[ 24 ] :   _( "Alshain" ),
        AstroBase.STARS[ 25 ] :   _( "Altair" ),
        AstroBase.STARS[ 26 ] :   _( "Ankaa" ),
        AstroBase.STARS[ 27 ] :   _( "Antares" ),
        AstroBase.STARS[ 28 ] :   _( "Arcturus" ),
        AstroBase.STARS[ 29 ] :   _( "Arneb" ),
        AstroBase.STARS[ 30 ] :   _( "Babcock's Star" ),
        AstroBase.STARS[ 31 ] :   _( "Barnard's Star" ),
        AstroBase.STARS[ 32 ] :   _( "Bellatrix" ),
        AstroBase.STARS[ 33 ] :   _( "Betelgeuse" ),
        AstroBase.STARS[ 34 ] :   _( "Campbell's Star" ),
        AstroBase.STARS[ 35 ] :   _( "Canopus" ),
        AstroBase.STARS[ 36 ] :   _( "Capella" ),
        AstroBase.STARS[ 37 ] :   _( "Caph" ),
        AstroBase.STARS[ 38 ] :   _( "Castor" ),
        AstroBase.STARS[ 39 ] :   _( "Cor Caroli" ),
        AstroBase.STARS[ 40 ] :   _( "Cyg X-1" ),
        AstroBase.STARS[ 41 ] :   _( "Deneb" ),
        AstroBase.STARS[ 42 ] :   _( "Denebola" ),
        AstroBase.STARS[ 43 ] :   _( "Diphda" ),
        AstroBase.STARS[ 44 ] :   _( "Dubhe" ),
        AstroBase.STARS[ 45 ] :   _( "Enif" ),
        AstroBase.STARS[ 46 ] :   _( "Etamin" ),
        AstroBase.STARS[ 47 ] :   _( "Fomalhaut" ),
        AstroBase.STARS[ 48 ] :   _( "Groombridge 1830" ),
        AstroBase.STARS[ 49 ] :   _( "Hadar" ),
        AstroBase.STARS[ 50 ] :   _( "Hamal" ),
        AstroBase.STARS[ 51 ] :   _( "Izar" ),
        AstroBase.STARS[ 52 ] :   _( "Kapteyn's Star" ),
        AstroBase.STARS[ 53 ] :   _( "Kaus Australis" ),
        AstroBase.STARS[ 54 ] :   _( "Kocab" ),
        AstroBase.STARS[ 55 ] :   _( "Kruger 60" ),
        AstroBase.STARS[ 56 ] :   _( "Luyten's Star" ),
        AstroBase.STARS[ 57 ] :   _( "Markab" ),
        AstroBase.STARS[ 58 ] :   _( "Megrez" ),
        AstroBase.STARS[ 59 ] :   _( "Menkar" ),
        AstroBase.STARS[ 60 ] :   _( "Merak" ),
        AstroBase.STARS[ 61 ] :   _( "Mintaka" ),
        AstroBase.STARS[ 62 ] :   _( "Mira" ),
        AstroBase.STARS[ 63 ] :   _( "Mirach" ),
        AstroBase.STARS[ 64 ] :   _( "Mirphak" ),
        AstroBase.STARS[ 65 ] :   _( "Mizar" ),
        AstroBase.STARS[ 66 ] :   _( "Nihal" ),
        AstroBase.STARS[ 67 ] :   _( "Nunki" ),
        AstroBase.STARS[ 68 ] :   _( "Phad" ),
        AstroBase.STARS[ 69 ] :   _( "Pleione" ),
        AstroBase.STARS[ 70 ] :   _( "Polaris" ),
        AstroBase.STARS[ 71 ] :   _( "Pollux" ),
        AstroBase.STARS[ 72 ] :   _( "Procyon" ),
        AstroBase.STARS[ 73 ] :   _( "Proxima" ),
        AstroBase.STARS[ 74 ] :   _( "Rasalgethi" ),
        AstroBase.STARS[ 75 ] :   _( "Rasalhague" ),
        AstroBase.STARS[ 76 ] :   _( "Red Rectangle" ),
        AstroBase.STARS[ 77 ] :   _( "Regulus" ),
        AstroBase.STARS[ 78 ] :   _( "Rigel" ),
        AstroBase.STARS[ 79 ] :   _( "Rigil Kent" ),
        AstroBase.STARS[ 80 ] :   _( "Sadalmelik" ),
        AstroBase.STARS[ 81 ] :   _( "Saiph" ),
        AstroBase.STARS[ 82 ] :   _( "Scheat" ),
        AstroBase.STARS[ 83 ] :   _( "Shaula" ),
        AstroBase.STARS[ 84 ] :   _( "Shedir" ),
        AstroBase.STARS[ 85 ] :   _( "Sheliak" ),
        AstroBase.STARS[ 86 ] :   _( "Sirius" ),
        AstroBase.STARS[ 87 ] :   _( "Spica" ),
        AstroBase.STARS[ 88 ] :   _( "Tarazed" ),
        AstroBase.STARS[ 89 ] :   _( "Thuban" ),
        AstroBase.STARS[ 90 ] :   _( "Unukalhai" ),
        AstroBase.STARS[ 91 ] :   _( "Van Maanen 2" ),
        AstroBase.STARS[ 92 ] :   _( "Vega" ),
        AstroBase.STARS[ 93 ] :   _( "Vindemiatrix" ),
        AstroBase.STARS[ 94 ] :   _( "Zaurak" ),
        AstroBase.STARS[ 95 ] :   _( "3C 273" ) } )


    # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
    AstroBase.STAR_TAGS_TRANSLATIONS.update( {
        AstroBase.STARS[ 0 ]  :   _( "ACAMAR" ),
        AstroBase.STARS[ 1 ]  :   _( "ACHERNAR" ),
        AstroBase.STARS[ 2 ]  :   _( "ACRUX" ),
        AstroBase.STARS[ 3 ]  :   _( "ADHARA" ),
        AstroBase.STARS[ 4 ]  :   _( "AGENA" ),
        AstroBase.STARS[ 5 ]  :   _( "ALBIREO" ),
        AstroBase.STARS[ 6 ]  :   _( "ALCOR" ),
        AstroBase.STARS[ 7 ]  :   _( "ALCYONE" ),
        AstroBase.STARS[ 8 ]  :   _( "ALDEBARAN" ),
        AstroBase.STARS[ 9 ]  :   _( "ALDERAMIN" ),
        AstroBase.STARS[ 10 ] :   _( "ALGENIB" ),
        AstroBase.STARS[ 11 ] :   _( "ALGIEBA" ),
        AstroBase.STARS[ 12 ] :   _( "ALGOL" ),
        AstroBase.STARS[ 13 ] :   _( "ALHENA" ),
        AstroBase.STARS[ 14 ] :   _( "ALIOTH" ),
        AstroBase.STARS[ 15 ] :   _( "ALKAID" ),
        AstroBase.STARS[ 16 ] :   _( "ALMAAK" ),
        AstroBase.STARS[ 17 ] :   _( "ALNAIR" ),
        AstroBase.STARS[ 18 ] :   _( "ALNATH" ),
        AstroBase.STARS[ 19 ] :   _( "ALNILAM" ),
        AstroBase.STARS[ 20 ] :   _( "ALNITAK" ),
        AstroBase.STARS[ 21 ] :   _( "ALPHARD" ),
        AstroBase.STARS[ 22 ] :   _( "ALPHEKKA" ),
        AstroBase.STARS[ 23 ] :   _( "ALPHERATZ" ),
        AstroBase.STARS[ 24 ] :   _( "ALSHAIN" ),
        AstroBase.STARS[ 25 ] :   _( "ALTAIR" ),
        AstroBase.STARS[ 26 ] :   _( "ANKAA" ),
        AstroBase.STARS[ 27 ] :   _( "ANTARES" ),
        AstroBase.STARS[ 28 ] :   _( "ARCTURUS" ),
        AstroBase.STARS[ 29 ] :   _( "ARNEB" ),
        AstroBase.STARS[ 30 ] :   _( "BABCOCK'S STAR" ),
        AstroBase.STARS[ 31 ] :   _( "BARNARD'S STAR" ),
        AstroBase.STARS[ 32 ] :   _( "BELLATRIX" ),
        AstroBase.STARS[ 33 ] :   _( "BETELGEUSE" ),
        AstroBase.STARS[ 34 ] :   _( "CAMPBELL'S STAR" ),
        AstroBase.STARS[ 35 ] :   _( "CANOPUS" ),
        AstroBase.STARS[ 36 ] :   _( "CAPELLA" ),
        AstroBase.STARS[ 37 ] :   _( "CAPH" ),
        AstroBase.STARS[ 38 ] :   _( "CASTOR" ),
        AstroBase.STARS[ 39 ] :   _( "COR CAROLI" ),
        AstroBase.STARS[ 40 ] :   _( "CYG X-1" ),
        AstroBase.STARS[ 41 ] :   _( "DENEB" ),
        AstroBase.STARS[ 42 ] :   _( "DENEBOLA" ),
        AstroBase.STARS[ 43 ] :   _( "DIPHDA" ),
        AstroBase.STARS[ 44 ] :   _( "DUBHE" ),
        AstroBase.STARS[ 45 ] :   _( "ENIF" ),
        AstroBase.STARS[ 46 ] :   _( "ETAMIN" ),
        AstroBase.STARS[ 47 ] :   _( "FOMALHAUT" ),
        AstroBase.STARS[ 48 ] :   _( "GROOMBRIDGE 1830" ),
        AstroBase.STARS[ 49 ] :   _( "HADAR" ),
        AstroBase.STARS[ 50 ] :   _( "HAMAL" ),
        AstroBase.STARS[ 51 ] :   _( "IZAR" ),
        AstroBase.STARS[ 52 ] :   _( "KAPTEYN'S STAR" ),
        AstroBase.STARS[ 53 ] :   _( "KAUS AUSTRALIS" ),
        AstroBase.STARS[ 54 ] :   _( "KOCAB" ),
        AstroBase.STARS[ 55 ] :   _( "KRUGER 60" ),
        AstroBase.STARS[ 56 ] :   _( "LUYTEN'S STAR" ),
        AstroBase.STARS[ 57 ] :   _( "MARKAB" ),
        AstroBase.STARS[ 58 ] :   _( "MEGREZ" ),
        AstroBase.STARS[ 59 ] :   _( "MENKAR" ),
        AstroBase.STARS[ 60 ] :   _( "MERAK" ),
        AstroBase.STARS[ 61 ] :   _( "MINTAKA" ),
        AstroBase.STARS[ 62 ] :   _( "MIRA" ),
        AstroBase.STARS[ 63 ] :   _( "MIRACH" ),
        AstroBase.STARS[ 64 ] :   _( "MIRPHAK" ),
        AstroBase.STARS[ 65 ] :   _( "MIZAR" ),
        AstroBase.STARS[ 66 ] :   _( "NIHAL" ),
        AstroBase.STARS[ 67 ] :   _( "NUNKI" ),
        AstroBase.STARS[ 68 ] :   _( "PHAD" ),
        AstroBase.STARS[ 69 ] :   _( "PLEIONE" ),
        AstroBase.STARS[ 70 ] :   _( "POLARIS" ),
        AstroBase.STARS[ 71 ] :   _( "POLLUX" ),
        AstroBase.STARS[ 72 ] :   _( "PROCYON" ),
        AstroBase.STARS[ 73 ] :   _( "PROXIMA" ),
        AstroBase.STARS[ 74 ] :   _( "RASALGETHI" ),
        AstroBase.STARS[ 75 ] :   _( "RASALHAGUE" ),
        AstroBase.STARS[ 76 ] :   _( "RED RECTANGLE" ),
        AstroBase.STARS[ 77 ] :   _( "REGULUS" ),
        AstroBase.STARS[ 78 ] :   _( "RIGEL" ),
        AstroBase.STARS[ 79 ] :   _( "RIGIL KENT" ),
        AstroBase.STARS[ 80 ] :   _( "SADALMELIK" ),
        AstroBase.STARS[ 81 ] :   _( "SAIPH" ),
        AstroBase.STARS[ 82 ] :   _( "SCHEAT" ),
        AstroBase.STARS[ 83 ] :   _( "SHAULA" ),
        AstroBase.STARS[ 84 ] :   _( "SHEDIR" ),
        AstroBase.STARS[ 85 ] :   _( "SHELIAK" ),
        AstroBase.STARS[ 86 ] :   _( "SIRIUS" ),
        AstroBase.STARS[ 87 ] :   _( "SPICA" ),
        AstroBase.STARS[ 88 ] :   _( "TARAZED" ),
        AstroBase.STARS[ 89 ] :   _( "THUBAN" ),
        AstroBase.STARS[ 90 ] :   _( "UNUKALHAI" ),
        AstroBase.STARS[ 91 ] :   _( "VAN MAANEN 2" ),
        AstroBase.STARS[ 92 ] :   _( "VEGA" ),
        AstroBase.STARS[ 93 ] :   _( "VINDEMIATRIX" ),
        AstroBase.STARS[ 94 ] :   _( "ZAURAK" ),
        AstroBase.STARS[ 95 ] :   _( "3C 273" ) } )


    # Skyfield does not provide a list of cities.
    #
    # However ephem/cities.py does provide such a list:
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


    # Used to reference city components of latitude, longitude and elevation.
    __CITY_LATITUDE = 0
    __CITY_LONGITUDE = 1
    __CITY_ELEVATION = 2


    # Used to reference Skyfield almanac for moon phases.
    __MOON_PHASE_NEW = 0
    __MOON_PHASE_FIRST_QUARTER = 1
    __MOON_PHASE_FULL = 2
    __MOON_PHASE_LAST_QUARTER = 3


    # Used to reference Skyfield almanac for seasons.
    __SEASON_VERNAL_EQUINOX = 0
    __SEASON_SUMMER_SOLSTICE = 1
    __SEASON_AUTUMNAL_EQUINOX = 2
    __SEASON_WINTER_SOLSTICE = 3


    @staticmethod
    def calculate(
            utcNow,
            latitude, longitude, elevation,
            planets,
            stars,
            satellites, satelliteData, startHour, endHour,
            comets, cometData, cometApparentMagnitudeData,
            minorPlanets, minorPlanetData, minorPlanetApparentMagnitudeData,
            apparentMagnitudeMaximum,
            logging ):

        data = { }

        timeScale = load.timescale( builtin = True )
        now = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
        nowPlusThirtySixHours = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour + 36, utcNow.minute, utcNow.second ) # Rise/set window (the moon rise/set is slightly more than 24 hours).
        nowPlusThirtyOneDays = timeScale.utc( utcNow.year, utcNow.month, utcNow.day + 31, utcNow.hour, utcNow.minute, utcNow.second ) # Moon phases search window.
        nowPlusSevenMonths = timeScale.utc( utcNow.year, utcNow.month + 7, utcNow.hour, utcNow.minute, utcNow.second ) # Solstice/equinox search window.
        nowPlusOneYear = timeScale.utc( utcNow.year + 1, utcNow.month, utcNow.hour, utcNow.minute, utcNow.second ) # Lunar eclipse search window.

        location = wgs84.latlon( latitude, longitude, elevation )
        locationAtNow = ( AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__PLANET_EARTH ] + location ).at( now )

        AstroSkyfield.__calculateMoon( now, nowPlusThirtySixHours, nowPlusThirtyOneDays, nowPlusOneYear, data, locationAtNow )
        AstroSkyfield.__calculateSun( now, nowPlusThirtySixHours, nowPlusSevenMonths, data, locationAtNow )
        AstroSkyfield.__calculatePlanets( now, nowPlusThirtySixHours, data, locationAtNow, planets, apparentMagnitudeMaximum, logging )
        AstroSkyfield.__calculateStars( now, nowPlusThirtySixHours, data, locationAtNow, stars, apparentMagnitudeMaximum )

        AstroSkyfield.__calculateCometsMinorPlanets(
            now, nowPlusThirtySixHours, data, timeScale, locationAtNow,
            AstroBase.BodyType.COMET, comets, cometData, cometApparentMagnitudeData,
            apparentMagnitudeMaximum,
            logging )

        AstroSkyfield.__calculateCometsMinorPlanets(
            now, nowPlusThirtySixHours, data, timeScale, locationAtNow,
            AstroBase.BodyType.MINOR_PLANET, minorPlanets, minorPlanetData, minorPlanetApparentMagnitudeData,
            apparentMagnitudeMaximum,
            logging )

        AstroSkyfield.__calculateSatellites( now, data, timeScale, location, satellites, satelliteData, startHour, endHour )

        return data


    @staticmethod
    def getCities(): return sorted( AstroSkyfield._city_data.keys(), key = locale.strxfrm )


    @staticmethod
    def getCredit(): return _( "Calculations courtesy of Skyfield. https://rhodesmill.org/skyfield" )


    @staticmethod
    def getLatitudeLongitudeElevation( city ):
        return \
            AstroSkyfield._city_data.get( city )[ AstroSkyfield.__CITY_LATITUDE ], \
            AstroSkyfield._city_data.get( city )[ AstroSkyfield.__CITY_LONGITUDE ], \
            AstroSkyfield._city_data.get( city )[ AstroSkyfield.__CITY_ELEVATION ]


    @staticmethod
    def getStatusMessage():
        minimalRequiredVersion = "1.43.1"
        installationCommand = "sudo apt-get install -y python3-pip\nsudo pip3 install --ignore-installed --upgrade pandas pip skyfield"
        message = None
        if not available:
            message = _( "Skyfield could not be found. Install using:\n\n" + installationCommand )

        elif LooseVersion( skyfield.__version__ ) < LooseVersion( minimalRequiredVersion ):
            message = \
                _( "Skyfield must be version {0} or greater. Please upgrade:\n\n" + \
                installationCommand ).format( minimalRequiredVersion )

        return message


    @staticmethod
    def getVersion(): return skyfield.__version__


    @staticmethod
    def __calculateMoon( now, nowPlusThirtySixHours, nowPlusThirtyOneDays, nowPlusOneYear, data, locationAtNow ):
        key = ( AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON )

        moonAtNow = locationAtNow.observe( AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__MOON ] )

        illumination = int( moonAtNow.fraction_illuminated( AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ] ) * 100 )
        data[ key + ( AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( illumination ) # Needed for icon.

        t, y = almanac.find_discrete( now, nowPlusThirtyOneDays, almanac.moon_phases( AstroSkyfield.__EPHEMERIS_PLANETS ) )
        moonPhases = list( y )
        moonPhasesDateTimes = t.utc_datetime()
        lunarPhase = AstroBase.getLunarPhase(
            illumination,
            moonPhasesDateTimes[ moonPhases.index( AstroSkyfield.__MOON_PHASE_FULL ) ],
            moonPhasesDateTimes[ moonPhases.index( AstroSkyfield.__MOON_PHASE_NEW ) ] )
        data[ key + ( AstroBase.DATA_TAG_PHASE, ) ] = lunarPhase # Needed for notification.

        sunAltAz = locationAtNow.observe( AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ] ).apparent().altaz()
        data[ key + ( AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( position_angle_of( moonAtNow.apparent().altaz(), sunAltAz ).radians ) # Needed for icon.

        neverUp = AstroSkyfield.__calculateCommon(
            now, nowPlusThirtySixHours,
            data, ( AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON ),
            locationAtNow,
            AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__MOON ] )

        if not neverUp:
            data[ key + ( AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = \
                AstroBase.toDateTimeString( moonPhasesDateTimes[ moonPhases.index( AstroSkyfield.__MOON_PHASE_FIRST_QUARTER ) ] )

            data[ key + ( AstroBase.DATA_TAG_FULL, ) ] = \
                AstroBase.toDateTimeString( moonPhasesDateTimes[ moonPhases.index( AstroSkyfield.__MOON_PHASE_FULL ) ] )

            data[ key + ( AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = \
                AstroBase.toDateTimeString( moonPhasesDateTimes[ moonPhases.index( AstroSkyfield.__MOON_PHASE_LAST_QUARTER ) ] )

            data[ key + ( AstroBase.DATA_TAG_NEW, ) ] = \
                AstroBase.toDateTimeString( moonPhasesDateTimes[ moonPhases.index( AstroSkyfield.__MOON_PHASE_NEW ) ] )

            t, y, details = eclipselib.lunar_eclipses( now, nowPlusOneYear, AstroSkyfield.__EPHEMERIS_PLANETS ) # Zeroth result in t and y is the first result, so use that.
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = \
                t[ 0 ].utc_strftime( AstroBase.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS )

            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipselib.LUNAR_ECLIPSES[ y[ 0 ] ]


    @staticmethod
    def __calculateSun( now, nowPlusThirtySixHours, nowPlusSevenMonths, data, locationAtNow ):
        neverUp = AstroSkyfield.__calculateCommon(
            now, nowPlusThirtySixHours,
            data, ( AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN ),
            locationAtNow,
            AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ] )

        if not neverUp:
            key = ( AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN )
            t, y = almanac.find_discrete( now, nowPlusSevenMonths, almanac.seasons( AstroSkyfield.__EPHEMERIS_PLANETS ) )
            t = t.utc_datetime()
            if almanac.SEASON_EVENTS[ AstroSkyfield.__SEASON_VERNAL_EQUINOX ] in almanac.SEASON_EVENTS[ y[ 0 ] ] or \
               almanac.SEASON_EVENTS[ AstroSkyfield.__SEASON_AUTUMNAL_EQUINOX ] in almanac.SEASON_EVENTS[ y[ 0 ] ]:
                data[ key + ( AstroBase.DATA_TAG_EQUINOX, ) ] = AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( AstroBase.DATA_TAG_SOLSTICE, ) ] = AstroBase.toDateTimeString( t[ 1 ] )

            else:
                data[ key + ( AstroBase.DATA_TAG_SOLSTICE, ) ] = AstroBase.toDateTimeString( t[ 0 ] )
                data[ key + ( AstroBase.DATA_TAG_EQUINOX, ) ] = AstroBase.toDateTimeString( t[ 1 ] )

#TODO Once solar eclipses are implemented in Skyfield, replace the code below with similar functionality to lunar eclipses above.        
# https://github.com/skyfielders/python-skyfield/issues/445
#TODO Remove the eclipse credit from IndicatorLunar if/when moving EXCLUSIELY to Skyfield and Skyfield computes solar eclipses.
            dateTime, eclipseType, latitude, longitude = eclipse.getEclipse( now.utc_datetime(), False )
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTime
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseType
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude


    @staticmethod
    def __calculatePlanets( now, nowPlusThirtySixHours, data, locationAtNow, planets, apparentMagnitudeMaximum, logging ):
        earthAtNow = AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__PLANET_EARTH ].at( now )
        for planet in planets:
            apparentMagnitude = planetary_magnitude( earthAtNow.observe( AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__PLANET_MAPPINGS[ planet ] ] ) )
            if planet == AstroBase.PLANET_SATURN and math.isnan( apparentMagnitude ):  # Saturn can return NaN...
                apparentMagnitude = 0.46 # Set the mean apparent magnitude (as per Wikipedia).

            if apparentMagnitude <= apparentMagnitudeMaximum:
                AstroSkyfield.__calculateCommon(
                    now, nowPlusThirtySixHours,
                    data, ( AstroBase.BodyType.PLANET, planet ),
                    locationAtNow,
                    AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__PLANET_MAPPINGS[ planet ] ] )


    @staticmethod
    def __calculateStars( now, nowPlusThirtySixHours, data, locationAtNow, stars, apparentMagnitudeMaximum ):
        for star in stars:
            if star in AstroBase.STARS: # Ensure that a star is present if/when switching between PyEphem and Skyfield.
                theStar = AstroSkyfield.__EPHEMERIS_STARS.loc[ AstroBase.STARS_TO_HIP[ star ] ]
                if theStar.magnitude <= apparentMagnitudeMaximum:
                    AstroSkyfield.__calculateCommon(
                        now, nowPlusThirtySixHours,
                        data, ( AstroBase.BodyType.STAR, star ),
                        locationAtNow,
                        Star.from_dataframe( theStar ) )


#TODO Issue logged with regard to slow speed of processing comets / minor planets:
# https://github.com/skyfielders/python-skyfield/issues/490
    @staticmethod
    def __calculateCometsMinorPlanets(
            now, nowPlusThirtySixHours, 
            data, timeScale, locationAtNow,
            bodyType, cometsMinorPlanets, orbitalElementData, apparentMagnitudeData,
            apparentMagnitudeMaximum,
            logging ):

        # Skyfield loads orbital element data into a dataframe from a file; 
        # as the orbital element data is already in memory,
        # write the orbital element data to a memory file object.
        with io.BytesIO() as f:
            if apparentMagnitudeData is None:
                for key in cometsMinorPlanets:
                    if key in orbitalElementData:
                        f.write( ( orbitalElementData[ key ].getData() + '\n' ).encode() )

            else:
                for key in cometsMinorPlanets:
                    if key in orbitalElementData and key in apparentMagnitudeData and float( apparentMagnitudeData[ key ].getApparentMagnitude() ) < apparentMagnitudeMaximum:
                        f.write( ( orbitalElementData[ key ].getData() + '\n' ).encode() )

            f.seek( 0 )

            if bodyType == AstroBase.BodyType.COMET:
                dataframe = mpc.load_comets_dataframe( f )
                orbitCalculationFunction = getattr( importlib.import_module( "skyfield.data.mpc" ), "comet_orbit" )

            else:
                dataframe = mpc.load_mpcorb_dataframe( f )
                orbitCalculationFunction = getattr( importlib.import_module( "skyfield.data.mpc" ), "mpcorb_orbit" )

        dataframe = dataframe.set_index( "designation", drop = False )
        alt, az, earthSunDistance = locationAtNow.observe( AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ] ).apparent().altaz()
        sunAtNow = AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ].at( now )
        for name, row in dataframe.iterrows():
            body = AstroSkyfield.__EPHEMERIS_PLANETS[ AstroSkyfield.__SUN ] + orbitCalculationFunction( row, timeScale, constants.GM_SUN_Pitjeva_2005_km3_s2 )

            if apparentMagnitudeData is None:
                ra, dec, earthBodyDistance = locationAtNow.observe( body ).radec()
                ra, dec, sunBodyDistance = sunAtNow.observe( body ).radec()
                try:
                    if bodyType == AstroBase.BodyType.COMET:
                        # Comparing
                        #
                        #    https://www.minorplanetcenter.net/iau/MPCORB/CometEls.txt
                        #    https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt
                        #
                        # with
                        #
                        #    https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
                        #
                        # it is clear the values for absolute magnitudes are the same for a given comet.
                        # Given that the XEphem values are preceded by a 'g',
                        # the MPC format for comets should use the gk apparent magnitude model.
                        apparentMagnitude = AstroBase.getApparentMagnitude_gk(
                            row[ "magnitude_g" ], row[ "magnitude_k" ],
                            earthBodyDistance.au, sunBodyDistance.au )

                    else:
                        # According to the format,
                        #
                        #    https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
                        #
                        # use the HG apparent magnitude model:
                        apparentMagnitude = AstroBase.getApparentMagnitude_HG(
                            row[ "magnitude_H" ], row[ "magnitude_G" ],
                            earthBodyDistance.au, sunBodyDistance.au, earthSunDistance.au )

                    if apparentMagnitude <= magnitudeMaximum:
                        AstroSkyfield.__calculateCommon( now, nowPlusOneDay, data, ( bodyType, name ), locationAtNow, ephemerisPlanets, body )

                except Exception as e:
                    message = "Error computing apparent magnitude for " + ( "comet: " if bodyType == AstroBase.BodyType.COMET else "minor planet: " ) + name
                    logging.error( message )
                    logging.exception( e )

            else:
                AstroSkyfield.__calculateCommon( now, nowPlusThirtySixHours, data, ( bodyType, name ), locationAtNow, body )


    @staticmethod
    def __calculateCommon( now, nowPlusThirtySixHours, data, key, locationAtNow, body ):
        neverUp = False
        t, y = almanac.find_discrete( now, nowPlusThirtySixHours, almanac.risings_and_settings( AstroSkyfield.__EPHEMERIS_PLANETS, body, locationAtNow.target ) ) # Using 'target' is safe: https://github.com/skyfielders/python-skyfield/issues/567
        if len( t ) >= 2: # Ensure there is at least one rise and one set.
            t = t.utc_datetime()
            if y[ 0 ]:
                riseDateTime = t[ 0 ]
                setDateTime = t[ 1 ]

            else:
                riseDateTime = t[ 1 ]
                setDateTime = t[ 0 ]

            data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = AstroBase.toDateTimeString( riseDateTime )
            data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = AstroBase.toDateTimeString( setDateTime )

            alt, az, earthBodyDistance = locationAtNow.observe( body ).apparent().altaz()
            data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
            data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

        else:
            # There is one rise OR one set OR no rises/sets.
            #
            # If there are no rises/sets, the body is either 'always up' or 'never up'.
            #
            # If there is one rise or one set, this would occur say close to the poles.
            # A body which has been below the horizon for weeks/months and is due to rise,
            # will result in a single value (the rise) and there will be no set.
            # Similarly for a body above the horizon.
            # Treat these single rise/set events as 'always up' or 'never up' (as the case may be)
            # until the body actually rises or sets.
            if almanac.risings_and_settings( AstroSkyfield.__EPHEMERIS_PLANETS, body, locationAtNow.target )( now ): # Body is up (and so always up).
                alt, az, earthBodyDistance = locationAtNow.observe( body ).apparent().altaz()
                data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = str( az.radians )
                data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = str( alt.radians )

            else:
                neverUp = True # Body is down (and so never up).

        return neverUp


    # References:
    #    https://github.com/skyfielders/python-skyfield/issues/327
    #    https://github.com/skyfielders/python-skyfield/issues/558
    @staticmethod
    def __calculateSatellites( now, data, timeScale, location, satellites, satelliteData, startHour, endHour ):
        nowPlusSatelliteSearchDuration = timeScale.utc(
            now.utc.year,
            now.utc.month,
            now.utc.day,
            now.utc.hour + AstroBase.SATELLITE_SEARCH_DURATION_HOURS,
            now.utc.minute,
            now.utc.second )

        isTwilightFunction = almanac.dark_twilight_day( AstroSkyfield.__EPHEMERIS_PLANETS, location )

        for satellite in satellites:
            if satellite in satelliteData:
                earthSatellite = EarthSatellite(
                    satelliteData[ satellite ].getLine1(),
                    satelliteData[ satellite ].getLine2(),
                    satelliteData[ satellite ].getName(),
                    timeScale )

                startDateTime, endDateTime = AstroBase.getAdjustedDateTime(
                    now.utc_datetime(), nowPlusSatelliteSearchDuration.utc_datetime(), startHour, endHour )

                while startDateTime is not None:
                    key = AstroSkyfield.__calculateSatellite(
                        timeScale.from_datetime( startDateTime ),
                        timeScale.from_datetime( endDateTime ),
                        data,
                        timeScale,
                        location,
                        satellite,
                        earthSatellite,
                        isTwilightFunction ) 

                    if key is None:
                        startDateTime, endDateTime = AstroBase.getAdjustedDateTime(
                            endDateTime + datetime.timedelta( minutes = 15 ), nowPlusSatelliteSearchDuration.utc_datetime(), startHour, endHour )

                        continue

                    break


    @staticmethod
#TODO How to determine if a satellite is 'always up' or 'never up'?
# Can something be taken from the calculateCommon() above?
# Be careful about using rise/set code which applies to planets: 
# https://rhodesmill.org/skyfield/almanac.html#sunrise-and-sunset
    def __calculateSatellite( startDateTime, endDateTime, data, timeScale, location, satelliteNumber, earthSatellite, isTwilightFunction ): 
        key, riseTime = None, None
        culminateTimes = [ ] # Culminate may occur more than once, so collect them all.
        t, events = earthSatellite.find_events( location, startDateTime, endDateTime, altitude_degrees = 30.0 ) #TODO Compare the passes with n2y and heavens above...maybe a value of 20 or 25 is better to match against what they calculate?
        for ti, event in zip( t, events ):
            if event == 0: # Rise
                riseTime = ti

            elif event == 1: # Culminate
                culminateTimes.append( ti )

            else: # Set
                if riseTime is not None and culminateTimes:
                    totalSecondsFromRiseToSet = ( ti.utc_datetime() - riseTime.utc_datetime() ).total_seconds()
                    step = 1.0 if ( totalSecondsFromRiseToSet / 10.0 ) < 1.0 else ( totalSecondsFromRiseToSet / 10.0 )
                    timeRange = timeScale.utc( 
                        riseTime.utc.year, 
                        riseTime.utc.month, 
                        riseTime.utc.day, 
                        riseTime.utc.hour, 
                        riseTime.utc.minute, 
                        range( math.ceil( riseTime.utc.second ), math.ceil( totalSecondsFromRiseToSet + riseTime.utc.second ), math.ceil( step ) ) )

                    isTwilightAstronomical = isTwilightFunction( timeRange ) == 1
                    isTwilightNautical = isTwilightFunction( timeRange ) == 2
                    sunlit = earthSatellite.at( timeRange ).is_sunlit( AstroSkyfield.__EPHEMERIS_PLANETS )
                    for twilightAstronomical, twilightNautical, isSunlit in zip( isTwilightAstronomical, isTwilightNautical, sunlit ):
                        if isSunlit and ( twilightAstronomical or twilightNautical ):
                            key = ( AstroBase.BodyType.SATELLITE, satelliteNumber )

                            data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = AstroBase.toDateTimeString( riseTime.utc_datetime() )
                            alt, az, earthSatelliteDistance = ( earthSatellite - location ).at( riseTime ).altaz()
                            data[ key + ( AstroBase.DATA_TAG_RISE_AZIMUTH, ) ] = str( az.radians )

                            data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = AstroBase.toDateTimeString( ti.utc_datetime() )
                            alt, az, earthSatelliteDistance = ( earthSatellite - location ).at( ti ).altaz()
                            data[ key + ( AstroBase.DATA_TAG_SET_AZIMUTH, ) ] = str( az.radians )
                            break

                if key is not None:
                    break

                riseTime = None
                culminateTimes = [ ]

        return key