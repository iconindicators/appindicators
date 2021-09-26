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


# Calculate astronomical information using PyEphem.


try:
    from ephem.cities import _city_data
    import ephem
    available = True

except ImportError:
    available = False

from distutils.version import LooseVersion

import astrobase, eclipse, locale, math


class AstroPyEphem( astrobase.AstroBase ):

    __PYEPHEM_INSTALLATION_COMMAND = "sudo apt-get install -y python3-ephem" #TODO If we install Pyephem via PIP this will change...or be removed? Also warn user NOT to install via apt-get?
    __PYEPHEM_REQUIRED_VERSION = "3.7.6.0" # Required version, or better.


    # Taken from ephem/stars.py
    # Version 3.7.7.0 added new stars but must still support 3.7.6.0 for Ubuntu 16.04/18.04.
    if LooseVersion( ephem.__version__ ) < LooseVersion( "3.7.7.0" ):
        astrobase.AstroBase.STARS.extend( [
            "ACHERNAR",
            "ADARA",
            "AGENA",
            "ALBEREO",
            "ALCAID",
            "ALCOR",
            "ALCYONE",
            "ALDEBARAN",
            "ALDERAMIN",
            "ALFIRK",
            "ALGENIB",
            "ALGIEBA",
            "ALGOL",
            "ALHENA",
            "ALIOTH",
            "ALMACH",
            "ALNAIR",
            "ALNILAM",
            "ALNITAK",
            "ALPHARD",
            "ALPHECCA",
            "ALSHAIN",
            "ALTAIR",
            "ANTARES",
            "ARCTURUS",
            "ARKAB POSTERIOR",
            "ARKAB PRIOR",
            "ARNEB",
            "ATLAS",
            "BELLATRIX",
            "BETELGEUSE",
            "CANOPUS",
            "CAPELLA",
            "CAPH",
            "CASTOR",
            "CEBALRAI",
            "DENEB",
            "DENEBOLA",
            "DUBHE",
            "ELECTRA",
            "ELNATH",
            "ENIF",
            "ETAMIN",
            "FOMALHAUT",
            "GIENAH CORVI",
            "HAMAL",
            "IZAR",
            "KAUS AUSTRALIS",
            "KOCHAB",
            "MAIA",
            "MARKAB",
            "MEGREZ",
            "MENKALINAN",
            "MENKAR",
            "MERAK",
            "MEROPE",
            "MIMOSA",
            "MINKAR",
            "MINTAKA",
            "MIRACH",
            "MIRZAM",
            "MIZAR",
            "NAOS",
            "NIHAL",
            "NUNKI",
            "PEACOCK",
            "PHECDA",
            "POLARIS",
            "POLLUX",
            "PROCYON",
            "RASALGETHI",
            "RASALHAGUE",
            "REGULUS",
            "RIGEL",
            "RUKBAT",
            "SADALMELIK",
            "SADR",
            "SAIPH",
            "SCHEAT",
            "SCHEDAR",
            "SHAULA",
            "SHELIAK",
            "SIRIUS",
            "SIRRAH",
            "SPICA",
            "SULAFAT",
            "TARAZED",
            "TAYGETA",
            "THUBAN",
            "UNUKALHAI",
            "VEGA",
            "VINDEMIATRIX",
            "WEZEN",
            "ZAURAK" ] )

        astrobase.AstroBase.STARS_TO_HIP.update( {
            "ACHERNAR"          :   7588,
            "ADARA"             :   33579,
            "AGENA"             :   68702,
            "ALBEREO"           :   95947,
            "ALCAID"            :   67301,
            "ALCOR"             :   65477,
            "ALCYONE"           :   17702,
            "ALDEBARAN"         :   21421,
            "ALDERAMIN"         :   105199,
            "ALFIRK"            :   106032,
            "ALGENIB"           :   1067,
            "ALGIEBA"           :   50583,
            "ALGOL"             :   14576,
            "ALHENA"            :   31681,
            "ALIOTH"            :   62956,
            "ALMACH"            :   9640,
            "ALNAIR"            :   109268,
            "ALNILAM"           :   26311,
            "ALNITAK"           :   26727,
            "ALPHARD"           :   46390,
            "ALPHECCA"          :   76267,
            "ALSHAIN"           :   98036,
            "ALTAIR"            :   97649,
            "ANTARES"           :   80763,
            "ARCTURUS"          :   69673,
            "ARKAB POSTERIOR"   :   95294,
            "ARKAB PRIOR"       :   95241,
            "ARNEB"             :   25985,
            "ATLAS"             :   17847,
            "BELLATRIX"         :   25336,
            "BETELGEUSE"        :   27989,
            "CANOPUS"           :   30438,
            "CAPELLA"           :   24608,
            "CAPH"              :   746,
            "CASTOR"            :   36850,
            "CEBALRAI"          :   86742,
            "DENEB"             :   102098,
            "DENEBOLA"          :   57632,
            "DUBHE"             :   54061,
            "ELECTRA"           :   17499,
            "ELNATH"            :   25428,
            "ENIF"              :   107315,
            "ETAMIN"            :   87833,
            "FOMALHAUT"         :   113368,
            "GIENAH CORVI"      :   59803,
            "HAMAL"             :   9884,
            "IZAR"              :   72105,
            "KAUS AUSTRALIS"    :   90185,
            "KOCHAB"            :   72607,
            "MAIA"              :   17573,
            "MARKAB"            :   113963,
            "MEGREZ"            :   59774,
            "MENKALINAN"        :   28360,
            "MENKAR"            :   14135,
            "MERAK"             :   53910,
            "MEROPE"            :   17608,
            "MIMOSA"            :   62434,
            "MINKAR"            :   59316,
            "MINTAKA"           :   25930,
            "MIRACH"            :   5447,
            "MIRZAM"            :   30324,
            "MIZAR"             :   65378,
            "NAOS"              :   39429,
            "NIHAL"             :   25606,
            "NUNKI"             :   92855,
            "PEACOCK"           :   100751,
            "PHECDA"            :   58001,
            "POLARIS"           :   11767,
            "POLLUX"            :   37826,
            "PROCYON"           :   37279,
            "RASALGETHI"        :   84345,
            "RASALHAGUE"        :   86032,
            "REGULUS"           :   49669,
            "RIGEL"             :   24436,
            "RUKBAT"            :   95347,
            "SADALMELIK"        :   109074,
            "SADR"              :   100453,
            "SAIPH"             :   27366,
            "SCHEAT"            :   113881,
            "SCHEDAR"           :   3179,
            "SHAULA"            :   85927,
            "SHELIAK"           :   92420,
            "SIRIUS"            :   32349,
            "SIRRAH"            :   677,
            "SPICA"             :   65474,
            "SULAFAT"           :   93194,
            "TARAZED"           :   97278,
            "TAYGETA"           :   17531,
            "THUBAN"            :   68756,
            "UNUKALHAI"         :   77070,
            "VEGA"              :   91262,
            "VINDEMIATRIX"      :   63608,
            "WEZEN"             :   34444,
            "ZAURAK"            :   18543 } )

        astrobase.AstroBase.STAR_NAMES_TRANSLATIONS.update( {
            astrobase.AstroBase.STARS[ 0 ]  :   _( "Achernar" ),
            astrobase.AstroBase.STARS[ 1 ]  :   _( "Adara" ),
            astrobase.AstroBase.STARS[ 2 ]  :   _( "Agena" ),
            astrobase.AstroBase.STARS[ 3 ]  :   _( "Albereo" ),
            astrobase.AstroBase.STARS[ 4 ]  :   _( "Alcaid" ),
            astrobase.AstroBase.STARS[ 5 ]  :   _( "Alcor" ),
            astrobase.AstroBase.STARS[ 6 ]  :   _( "Alcyone" ),
            astrobase.AstroBase.STARS[ 7 ]  :   _( "Aldebaran" ),
            astrobase.AstroBase.STARS[ 8 ]  :   _( "Alderamin" ),
            astrobase.AstroBase.STARS[ 9 ]  :   _( "Alfirk" ),
            astrobase.AstroBase.STARS[ 10 ] :   _( "Algenib" ),
            astrobase.AstroBase.STARS[ 11 ] :   _( "Algieba" ),
            astrobase.AstroBase.STARS[ 12 ] :   _( "Algol" ),
            astrobase.AstroBase.STARS[ 13 ] :   _( "Alhena" ),
            astrobase.AstroBase.STARS[ 14 ] :   _( "Alioth" ),
            astrobase.AstroBase.STARS[ 15 ] :   _( "Almach" ),
            astrobase.AstroBase.STARS[ 16 ] :   _( "Alnair" ),
            astrobase.AstroBase.STARS[ 17 ] :   _( "Alnilam" ),
            astrobase.AstroBase.STARS[ 18 ] :   _( "Alnitak" ),
            astrobase.AstroBase.STARS[ 19 ] :   _( "Alphard" ),
            astrobase.AstroBase.STARS[ 20 ] :   _( "Alphecca" ),
            astrobase.AstroBase.STARS[ 21 ] :   _( "Alshain" ),
            astrobase.AstroBase.STARS[ 22 ] :   _( "Altair" ),
            astrobase.AstroBase.STARS[ 23 ] :   _( "Antares" ),
            astrobase.AstroBase.STARS[ 24 ] :   _( "Arcturus" ),
            astrobase.AstroBase.STARS[ 25 ] :   _( "Arkab Posterior" ),
            astrobase.AstroBase.STARS[ 26 ] :   _( "Arkab Prior" ),
            astrobase.AstroBase.STARS[ 27 ] :   _( "Arneb" ),
            astrobase.AstroBase.STARS[ 28 ] :   _( "Atlas" ),
            astrobase.AstroBase.STARS[ 29 ] :   _( "Bellatrix" ),
            astrobase.AstroBase.STARS[ 30 ] :   _( "Betelgeuse" ),
            astrobase.AstroBase.STARS[ 31 ] :   _( "Canopus" ),
            astrobase.AstroBase.STARS[ 32 ] :   _( "Capella" ),
            astrobase.AstroBase.STARS[ 33 ] :   _( "Caph" ),
            astrobase.AstroBase.STARS[ 34 ] :   _( "Castor" ),
            astrobase.AstroBase.STARS[ 35 ] :   _( "Cebalrai" ),
            astrobase.AstroBase.STARS[ 36 ] :   _( "Deneb" ),
            astrobase.AstroBase.STARS[ 37 ] :   _( "Denebola" ),
            astrobase.AstroBase.STARS[ 38 ] :   _( "Dubhe" ),
            astrobase.AstroBase.STARS[ 39 ] :   _( "Electra" ),
            astrobase.AstroBase.STARS[ 40 ] :   _( "Elnath" ),
            astrobase.AstroBase.STARS[ 41 ] :   _( "Enif" ),
            astrobase.AstroBase.STARS[ 42 ] :   _( "Etamin" ),
            astrobase.AstroBase.STARS[ 43 ] :   _( "Fomalhaut" ),
            astrobase.AstroBase.STARS[ 44 ] :   _( "Gienah Corvi" ),
            astrobase.AstroBase.STARS[ 45 ] :   _( "Hamal" ),
            astrobase.AstroBase.STARS[ 46 ] :   _( "Izar" ),
            astrobase.AstroBase.STARS[ 47 ] :   _( "Kaus Australis" ),
            astrobase.AstroBase.STARS[ 48 ] :   _( "Kochab" ),
            astrobase.AstroBase.STARS[ 49 ] :   _( "Maia" ),
            astrobase.AstroBase.STARS[ 50 ] :   _( "Markab" ),
            astrobase.AstroBase.STARS[ 51 ] :   _( "Megrez" ),
            astrobase.AstroBase.STARS[ 52 ] :   _( "Menkalinan" ),
            astrobase.AstroBase.STARS[ 53 ] :   _( "Menkar" ),
            astrobase.AstroBase.STARS[ 54 ] :   _( "Merak" ),
            astrobase.AstroBase.STARS[ 55 ] :   _( "Merope" ),
            astrobase.AstroBase.STARS[ 56 ] :   _( "Mimosa" ),
            astrobase.AstroBase.STARS[ 57 ] :   _( "Minkar" ),
            astrobase.AstroBase.STARS[ 58 ] :   _( "Mintaka" ),
            astrobase.AstroBase.STARS[ 59 ] :   _( "Mirach" ),
            astrobase.AstroBase.STARS[ 60 ] :   _( "Mirzam" ),
            astrobase.AstroBase.STARS[ 61 ] :   _( "Mizar" ),
            astrobase.AstroBase.STARS[ 62 ] :   _( "Naos" ),
            astrobase.AstroBase.STARS[ 63 ] :   _( "Nihal" ),
            astrobase.AstroBase.STARS[ 64 ] :   _( "Nunki" ),
            astrobase.AstroBase.STARS[ 65 ] :   _( "Peacock" ),
            astrobase.AstroBase.STARS[ 66 ] :   _( "Phecda" ),
            astrobase.AstroBase.STARS[ 67 ] :   _( "Polaris" ),
            astrobase.AstroBase.STARS[ 68 ] :   _( "Pollux" ),
            astrobase.AstroBase.STARS[ 69 ] :   _( "Procyon" ),
            astrobase.AstroBase.STARS[ 70 ] :   _( "Rasalgethi" ),
            astrobase.AstroBase.STARS[ 71 ] :   _( "Rasalhague" ),
            astrobase.AstroBase.STARS[ 72 ] :   _( "Regulus" ),
            astrobase.AstroBase.STARS[ 73 ] :   _( "Rigel" ),
            astrobase.AstroBase.STARS[ 74 ] :   _( "Rukbat" ),
            astrobase.AstroBase.STARS[ 75 ] :   _( "Sadalmelik" ),
            astrobase.AstroBase.STARS[ 76 ] :   _( "Sadr" ),
            astrobase.AstroBase.STARS[ 77 ] :   _( "Saiph" ),
            astrobase.AstroBase.STARS[ 78 ] :   _( "Scheat" ),
            astrobase.AstroBase.STARS[ 79 ] :   _( "Schedar" ),
            astrobase.AstroBase.STARS[ 80 ] :   _( "Shaula" ),
            astrobase.AstroBase.STARS[ 81 ] :   _( "Sheliak" ),
            astrobase.AstroBase.STARS[ 82 ] :   _( "Sirius" ),
            astrobase.AstroBase.STARS[ 83 ] :   _( "Sirrah" ),
            astrobase.AstroBase.STARS[ 84 ] :   _( "Spica" ),
            astrobase.AstroBase.STARS[ 85 ] :   _( "Sulafat" ),
            astrobase.AstroBase.STARS[ 86 ] :   _( "Tarazed" ),
            astrobase.AstroBase.STARS[ 87 ] :   _( "Taygeta" ),
            astrobase.AstroBase.STARS[ 88 ] :   _( "Thuban" ),
            astrobase.AstroBase.STARS[ 89 ] :   _( "Unukalhai" ),
            astrobase.AstroBase.STARS[ 90 ] :   _( "Vega" ),
            astrobase.AstroBase.STARS[ 91 ] :   _( "Vindemiatrix" ),
            astrobase.AstroBase.STARS[ 92 ] :   _( "Wezen" ),
            astrobase.AstroBase.STARS[ 93 ] :   _( "Zaurak" ) } )

        # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
        astrobase.AstroBase.STAR_TAGS_TRANSLATIONS.update( {
            astrobase.AstroBase.STARS[ 0 ]  :   _( "ACHERNAR" ),
            astrobase.AstroBase.STARS[ 1 ]  :   _( "ADARA" ),
            astrobase.AstroBase.STARS[ 2 ]  :   _( "AGENA" ),
            astrobase.AstroBase.STARS[ 3 ]  :   _( "ALBEREO" ),
            astrobase.AstroBase.STARS[ 4 ]  :   _( "ALCAID" ),
            astrobase.AstroBase.STARS[ 5 ]  :   _( "ALCOR" ),
            astrobase.AstroBase.STARS[ 6 ]  :   _( "ALCYONE" ),
            astrobase.AstroBase.STARS[ 7 ]  :   _( "ALDEBARAN" ),
            astrobase.AstroBase.STARS[ 8 ]  :   _( "ALDERAMIN" ),
            astrobase.AstroBase.STARS[ 9 ]  :   _( "ALFIRK" ),
            astrobase.AstroBase.STARS[ 10 ] :   _( "ALGENIB" ),
            astrobase.AstroBase.STARS[ 11 ] :   _( "ALGIEBA" ),
            astrobase.AstroBase.STARS[ 12 ] :   _( "ALGOL" ),
            astrobase.AstroBase.STARS[ 13 ] :   _( "ALHENA" ),
            astrobase.AstroBase.STARS[ 14 ] :   _( "ALIOTH" ),
            astrobase.AstroBase.STARS[ 15 ] :   _( "ALMACH" ),
            astrobase.AstroBase.STARS[ 16 ] :   _( "ALNAIR" ),
            astrobase.AstroBase.STARS[ 17 ] :   _( "ALNILAM" ),
            astrobase.AstroBase.STARS[ 18 ] :   _( "ALNITAK" ),
            astrobase.AstroBase.STARS[ 19 ] :   _( "ALPHARD" ),
            astrobase.AstroBase.STARS[ 20 ] :   _( "ALPHECCA" ),
            astrobase.AstroBase.STARS[ 21 ] :   _( "ALSHAIN" ),
            astrobase.AstroBase.STARS[ 22 ] :   _( "ALTAIR" ),
            astrobase.AstroBase.STARS[ 23 ] :   _( "ANTARES" ),
            astrobase.AstroBase.STARS[ 24 ] :   _( "ARCTURUS" ),
            astrobase.AstroBase.STARS[ 25 ] :   _( "ARKAB POSTERIOR" ),
            astrobase.AstroBase.STARS[ 26 ] :   _( "ARKAB PRIOR" ),
            astrobase.AstroBase.STARS[ 27 ] :   _( "ARNEB" ),
            astrobase.AstroBase.STARS[ 28 ] :   _( "ATLAS" ),
            astrobase.AstroBase.STARS[ 29 ] :   _( "BELLATRIX" ),
            astrobase.AstroBase.STARS[ 30 ] :   _( "BETELGEUSE" ),
            astrobase.AstroBase.STARS[ 31 ] :   _( "CANOPUS" ),
            astrobase.AstroBase.STARS[ 32 ] :   _( "CAPELLA" ),
            astrobase.AstroBase.STARS[ 33 ] :   _( "CAPH" ),
            astrobase.AstroBase.STARS[ 34 ] :   _( "CASTOR" ),
            astrobase.AstroBase.STARS[ 35 ] :   _( "CEBALRAI" ),
            astrobase.AstroBase.STARS[ 36 ] :   _( "DENEB" ),
            astrobase.AstroBase.STARS[ 37 ] :   _( "DENEBOLA" ),
            astrobase.AstroBase.STARS[ 38 ] :   _( "DUBHE" ),
            astrobase.AstroBase.STARS[ 39 ] :   _( "ELECTRA" ),
            astrobase.AstroBase.STARS[ 40 ] :   _( "ELNATH" ),
            astrobase.AstroBase.STARS[ 41 ] :   _( "ENIF" ),
            astrobase.AstroBase.STARS[ 42 ] :   _( "ETAMIN" ),
            astrobase.AstroBase.STARS[ 43 ] :   _( "FOMALHAUT" ),
            astrobase.AstroBase.STARS[ 44 ] :   _( "GIENAH CORVI" ),
            astrobase.AstroBase.STARS[ 45 ] :   _( "HAMAL" ),
            astrobase.AstroBase.STARS[ 46 ] :   _( "IZAR" ),
            astrobase.AstroBase.STARS[ 47 ] :   _( "KAUS AUSTRALIS" ),
            astrobase.AstroBase.STARS[ 48 ] :   _( "KOCHAB" ),
            astrobase.AstroBase.STARS[ 49 ] :   _( "MAIA" ),
            astrobase.AstroBase.STARS[ 50 ] :   _( "MARKAB" ),
            astrobase.AstroBase.STARS[ 51 ] :   _( "MEGREZ" ),
            astrobase.AstroBase.STARS[ 52 ] :   _( "MENKALINAN" ),
            astrobase.AstroBase.STARS[ 53 ] :   _( "MENKAR" ),
            astrobase.AstroBase.STARS[ 54 ] :   _( "MERAK" ),
            astrobase.AstroBase.STARS[ 55 ] :   _( "MEROPE" ),
            astrobase.AstroBase.STARS[ 56 ] :   _( "MIMOSA" ),
            astrobase.AstroBase.STARS[ 57 ] :   _( "MINKAR" ),
            astrobase.AstroBase.STARS[ 58 ] :   _( "MINTAKA" ),
            astrobase.AstroBase.STARS[ 59 ] :   _( "MIRACH" ),
            astrobase.AstroBase.STARS[ 60 ] :   _( "MIRZAM" ),
            astrobase.AstroBase.STARS[ 61 ] :   _( "MIZAR" ),
            astrobase.AstroBase.STARS[ 62 ] :   _( "NAOS" ),
            astrobase.AstroBase.STARS[ 63 ] :   _( "NIHAL" ),
            astrobase.AstroBase.STARS[ 64 ] :   _( "NUNKI" ),
            astrobase.AstroBase.STARS[ 65 ] :   _( "PEACOCK" ),
            astrobase.AstroBase.STARS[ 66 ] :   _( "PHECDA" ),
            astrobase.AstroBase.STARS[ 67 ] :   _( "POLARIS" ),
            astrobase.AstroBase.STARS[ 68 ] :   _( "POLLUX" ),
            astrobase.AstroBase.STARS[ 69 ] :   _( "PROCYON" ),
            astrobase.AstroBase.STARS[ 70 ] :   _( "RASALGETHI" ),
            astrobase.AstroBase.STARS[ 71 ] :   _( "RASALHAGUE" ),
            astrobase.AstroBase.STARS[ 72 ] :   _( "REGULUS" ),
            astrobase.AstroBase.STARS[ 73 ] :   _( "RIGEL" ),
            astrobase.AstroBase.STARS[ 74 ] :   _( "RUKBAT" ),
            astrobase.AstroBase.STARS[ 75 ] :   _( "SADALMELIK" ),
            astrobase.AstroBase.STARS[ 76 ] :   _( "SADR" ),
            astrobase.AstroBase.STARS[ 77 ] :   _( "SAIPH" ),
            astrobase.AstroBase.STARS[ 78 ] :   _( "SCHEAT" ),
            astrobase.AstroBase.STARS[ 79 ] :   _( "SCHEDAR" ),
            astrobase.AstroBase.STARS[ 80 ] :   _( "SHAULA" ),
            astrobase.AstroBase.STARS[ 81 ] :   _( "SHELIAK" ),
            astrobase.AstroBase.STARS[ 82 ] :   _( "SIRIUS" ),
            astrobase.AstroBase.STARS[ 83 ] :   _( "SIRRAH" ),
            astrobase.AstroBase.STARS[ 84 ] :   _( "SPICA" ),
            astrobase.AstroBase.STARS[ 85 ] :   _( "SULAFAT" ),
            astrobase.AstroBase.STARS[ 86 ] :   _( "TARAZED" ),
            astrobase.AstroBase.STARS[ 87 ] :   _( "TAYGETA" ),
            astrobase.AstroBase.STARS[ 88 ] :   _( "THUBAN" ),
            astrobase.AstroBase.STARS[ 89 ] :   _( "UNUKALHAI" ),
            astrobase.AstroBase.STARS[ 90 ] :   _( "VEGA" ),
            astrobase.AstroBase.STARS[ 91 ] :   _( "VINDEMIATRIX" ),
            astrobase.AstroBase.STARS[ 92 ] :   _( "WEZEN" ),
            astrobase.AstroBase.STARS[ 93 ] :   _( "ZAURAK" ) } )

    else: # 3.7.7.0 or better.
        astrobase.AstroBase.STARS.extend( [
            "ACAMAR",
            "ACHERNAR",
            "ACRUX",
            "ADARA",
            "ADHARA",
            "AGENA",
            "ALBEREO",
            "ALCAID",
            "ALCOR",
            "ALCYONE",
            "ALDEBARAN",
            "ALDERAMIN",
            "ALFIRK",
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
            "ALSHAIN",
            "ALTAIR",
            "ANKAA",
            "ANTARES",
            "ARCTURUS",
            "ARKAB POSTERIOR",
            "ARKAB PRIOR",
            "ARNEB",
            "ATLAS",
            "ATRIA",
            "AVIOR",
            "BELLATRIX",
            "BETELGEUSE",
            "CANOPUS",
            "CAPELLA",
            "CAPH",
            "CASTOR",
            "CEBALRAI",
            "DENEB",
            "DENEBOLA",
            "DIPHDA",
            "DUBHE",
            "ELECTRA",
            "ELNATH",
            "ELTANIN",
            "ENIF",
            "ETAMIN",
            "FOMALHAUT",
            "FORMALHAUT",
            "GACRUX",
            "GIENAH",
            "GIENAH CORVI",
            "HADAR",
            "HAMAL",
            "IZAR",
            "KAUS AUSTRALIS",
            "KOCHAB",
            "MAIA",
            "MARKAB",
            "MEGREZ",
            "MENKALINAN",
            "MENKAR",
            "MENKENT",
            "MERAK",
            "MEROPE",
            "MIAPLACIDUS",
            "MIMOSA",
            "MINKAR",
            "MINTAKA",
            "MIRACH",
            "MIRFAK",
            "MIRZAM",
            "MIZAR",
            "NAOS",
            "NIHAL",
            "NUNKI",
            "PEACOCK",
            "PHECDA",
            "POLARIS",
            "POLLUX",
            "PROCYON",
            "RASALGETHI",
            "RASALHAGUE",
            "REGULUS",
            "RIGEL",
            "RIGIL KENTAURUS",
            "RUKBAT",
            "SABIK",
            "SADALMELIK",
            "SADR",
            "SAIPH",
            "SCHEAT",
            "SCHEDAR",
            "SHAULA",
            "SHELIAK",
            "SIRIUS",
            "SIRRAH",
            "SPICA",
            "SUHAIL",
            "SULAFAT",
            "TARAZED",
            "TAYGETA",
            "THUBAN",
            "UNUKALHAI",
            "VEGA",
            "VINDEMIATRIX",
            "WEZEN",
            "ZAURAK",
            "ZUBENELGENUBI" ] )

        astrobase.AstroBase.STARS_TO_HIP.update( {
            "ACAMAR"            :   13847,
            "ACHERNAR"          :   7588,
            "ACRUX"             :   60718,
            "ADARA"             :   33579,
            "ADHARA"            :   33579,
            "AGENA"             :   68702,
            "ALBEREO"           :   95947,
            "ALCAID"            :   67301,
            "ALCOR"             :   65477,
            "ALCYONE"           :   17702,
            "ALDEBARAN"         :   21421,
            "ALDERAMIN"         :   105199,
            "ALFIRK"            :   106032,
            "ALGENIB"           :   1067,
            "ALGIEBA"           :   50583,
            "ALGOL"             :   14576,
            "ALHENA"            :   31681,
            "ALIOTH"            :   62956,
            "ALKAID"            :   67301,
            "ALMACH"            :   9640,
            "ALNAIR"            :   109268,
            "ALNILAM"           :   26311,
            "ALNITAK"           :   26727,
            "ALPHARD"           :   46390,
            "ALPHECCA"          :   76267,
            "ALPHERATZ"         :   677,
            "ALSHAIN"           :   98036,
            "ALTAIR"            :   97649,
            "ANKAA"             :   2081,
            "ANTARES"           :   80763,
            "ARCTURUS"          :   69673,
            "ARKAB POSTERIOR"   :   95294,
            "ARKAB PRIOR"       :   95241,
            "ARNEB"             :   25985,
            "ATLAS"             :   17847,
            "ATRIA"             :   82273,
            "AVIOR"             :   41037,
            "BELLATRIX"         :   25336,
            "BETELGEUSE"        :   27989,
            "CANOPUS"           :   30438,
            "CAPELLA"           :   24608,
            "CAPH"              :   746,
            "CASTOR"            :   36850,
            "CEBALRAI"          :   86742,
            "DENEB"             :   102098,
            "DENEBOLA"          :   57632,
            "DIPHDA"            :   3419,
            "DUBHE"             :   54061,
            "ELECTRA"           :   17499,
            "ELNATH"            :   25428,
            "ELTANIN"           :   87833,
            "ENIF"              :   107315,
            "ETAMIN"            :   87833,
            "FOMALHAUT"         :   113368,
            "FORMALHAUT"        :   113368,
            "GACRUX"            :   61084,
            "GIENAH CORVI"      :   59803,
            "GIENAH"            :   59803,
            "HADAR"             :   68702,
            "HAMAL"             :   9884,
            "IZAR"              :   72105,
            "KAUS AUSTRALIS"    :   90185,
            "KOCHAB"            :   72607,
            "MAIA"              :   17573,
            "MARKAB"            :   113963,
            "MEGREZ"            :   59774,
            "MENKALINAN"        :   28360,
            "MENKAR"            :   14135,
            "MENKENT"           :   68933,
            "MERAK"             :   53910,
            "MEROPE"            :   17608,
            "MIAPLACIDUS"       :   45238,
            "MIMOSA"            :   62434,
            "MINKAR"            :   59316,
            "MINTAKA"           :   25930,
            "MIRACH"            :   5447,
            "MIRFAK"            :   15863,
            "MIRZAM"            :   30324,
            "MIZAR"             :   65378,
            "NAOS"              :   39429,
            "NIHAL"             :   25606,
            "NUNKI"             :   92855,
            "PEACOCK"           :   100751,
            "PHECDA"            :   58001,
            "POLARIS"           :   11767,
            "POLLUX"            :   37826,
            "PROCYON"           :   37279,
            "RASALGETHI"        :   84345,
            "RASALHAGUE"        :   86032,
            "REGULUS"           :   49669,
            "RIGEL"             :   24436,
            "RIGIL KENTAURUS"   :   71683,
            "RUKBAT"            :   95347,
            "SABIK"             :   84012,
            "SADALMELIK"        :   109074,
            "SADR"              :   100453,
            "SAIPH"             :   27366,
            "SCHEAT"            :   113881,
            "SCHEDAR"           :   3179,
            "SHAULA"            :   85927,
            "SHELIAK"           :   92420,
            "SIRIUS"            :   32349,
            "SIRRAH"            :   677,
            "SPICA"             :   65474,
            "SUHAIL"            :   44816,
            "SULAFAT"           :   93194,
            "TARAZED"           :   97278,
            "TAYGETA"           :   17531,
            "THUBAN"            :   68756,
            "UNUKALHAI"         :   77070,
            "VEGA"              :   91262,
            "VINDEMIATRIX"      :   63608,
            "WEZEN"             :   34444,
            "ZAURAK"            :   18543,
            "ZUBENELGENUBI"     :   72603 } )

        astrobase.AstroBase.STAR_NAMES_TRANSLATIONS.update( {
            astrobase.AstroBase.STARS[ 0 ]      :   _( "Acamar" ),
            astrobase.AstroBase.STARS[ 1 ]      :   _( "Achernar" ),
            astrobase.AstroBase.STARS[ 2 ]      :   _( "Acrux" ),
            astrobase.AstroBase.STARS[ 3 ]      :   _( "Adara" ),
            astrobase.AstroBase.STARS[ 4 ]      :   _( "Adhara" ),
            astrobase.AstroBase.STARS[ 5 ]      :   _( "Agena" ),
            astrobase.AstroBase.STARS[ 6 ]      :   _( "Albereo" ),
            astrobase.AstroBase.STARS[ 7 ]      :   _( "Alcaid" ),
            astrobase.AstroBase.STARS[ 8 ]      :   _( "Alcor" ),
            astrobase.AstroBase.STARS[ 9 ]      :   _( "Alcyone" ),
            astrobase.AstroBase.STARS[ 10 ]     :   _( "Aldebaran" ),
            astrobase.AstroBase.STARS[ 11 ]     :   _( "Alderamin" ),
            astrobase.AstroBase.STARS[ 12 ]     :   _( "Alfirk" ),
            astrobase.AstroBase.STARS[ 13 ]     :   _( "Algenib" ),
            astrobase.AstroBase.STARS[ 14 ]     :   _( "Algieba" ),
            astrobase.AstroBase.STARS[ 15 ]     :   _( "Algol" ),
            astrobase.AstroBase.STARS[ 16 ]     :   _( "Alhena" ),
            astrobase.AstroBase.STARS[ 17 ]     :   _( "Alioth" ),
            astrobase.AstroBase.STARS[ 18 ]     :   _( "Alkaid" ),
            astrobase.AstroBase.STARS[ 19 ]     :   _( "Almach" ),
            astrobase.AstroBase.STARS[ 20 ]     :   _( "Alnair" ),
            astrobase.AstroBase.STARS[ 21 ]     :   _( "Alnilam" ),
            astrobase.AstroBase.STARS[ 22 ]     :   _( "Alnitak" ),
            astrobase.AstroBase.STARS[ 23 ]     :   _( "Alphard" ),
            astrobase.AstroBase.STARS[ 24 ]     :   _( "Alphecca" ),
            astrobase.AstroBase.STARS[ 25 ]     :   _( "Alpheratz" ),
            astrobase.AstroBase.STARS[ 26 ]     :   _( "Alshain" ),
            astrobase.AstroBase.STARS[ 27 ]     :   _( "Altair" ),
            astrobase.AstroBase.STARS[ 28 ]     :   _( "Ankaa" ),
            astrobase.AstroBase.STARS[ 29 ]     :   _( "Antares" ),
            astrobase.AstroBase.STARS[ 30 ]     :   _( "Arcturus" ),
            astrobase.AstroBase.STARS[ 31 ]     :   _( "Arkab Posterior" ),
            astrobase.AstroBase.STARS[ 32 ]     :   _( "Arkab Prior" ),
            astrobase.AstroBase.STARS[ 33 ]     :   _( "Arneb" ),
            astrobase.AstroBase.STARS[ 34 ]     :   _( "Atlas" ),
            astrobase.AstroBase.STARS[ 35 ]     :   _( "Atria" ),
            astrobase.AstroBase.STARS[ 36 ]     :   _( "Avior" ),
            astrobase.AstroBase.STARS[ 37 ]     :   _( "Bellatrix" ),
            astrobase.AstroBase.STARS[ 38 ]     :   _( "Betelgeuse" ),
            astrobase.AstroBase.STARS[ 39 ]     :   _( "Canopus" ),
            astrobase.AstroBase.STARS[ 40 ]     :   _( "Capella" ),
            astrobase.AstroBase.STARS[ 41 ]     :   _( "Caph" ),
            astrobase.AstroBase.STARS[ 42 ]     :   _( "Castor" ),
            astrobase.AstroBase.STARS[ 43 ]     :   _( "Cebalrai" ),
            astrobase.AstroBase.STARS[ 44 ]     :   _( "Deneb" ),
            astrobase.AstroBase.STARS[ 45 ]     :   _( "Denebola" ),
            astrobase.AstroBase.STARS[ 46 ]     :   _( "Diphda" ),
            astrobase.AstroBase.STARS[ 47 ]     :   _( "Dubhe" ),
            astrobase.AstroBase.STARS[ 48 ]     :   _( "Electra" ),
            astrobase.AstroBase.STARS[ 49 ]     :   _( "Elnath" ),
            astrobase.AstroBase.STARS[ 50 ]     :   _( "Eltanin" ),
            astrobase.AstroBase.STARS[ 51 ]     :   _( "Enif" ),
            astrobase.AstroBase.STARS[ 52 ]     :   _( "Etamin" ),
            astrobase.AstroBase.STARS[ 53 ]     :   _( "Fomalhaut" ),
            astrobase.AstroBase.STARS[ 54 ]     :   _( "Formalhaut" ),
            astrobase.AstroBase.STARS[ 55 ]     :   _( "Gacrux" ),
            astrobase.AstroBase.STARS[ 56 ]     :   _( "Gienah" ),
            astrobase.AstroBase.STARS[ 57 ]     :   _( "Gienah Corvi" ),
            astrobase.AstroBase.STARS[ 58 ]     :   _( "Hadar" ),
            astrobase.AstroBase.STARS[ 59 ]     :   _( "Hamal" ),
            astrobase.AstroBase.STARS[ 60 ]     :   _( "Izar" ),
            astrobase.AstroBase.STARS[ 61 ]     :   _( "Kaus Australis" ),
            astrobase.AstroBase.STARS[ 62 ]     :   _( "Kochab" ),
            astrobase.AstroBase.STARS[ 63 ]     :   _( "Maia" ),
            astrobase.AstroBase.STARS[ 64 ]     :   _( "Markab" ),
            astrobase.AstroBase.STARS[ 65 ]     :   _( "Megrez" ),
            astrobase.AstroBase.STARS[ 66 ]     :   _( "Menkalinan" ),
            astrobase.AstroBase.STARS[ 67 ]     :   _( "Menkar" ),
            astrobase.AstroBase.STARS[ 68 ]     :   _( "Menkent" ),
            astrobase.AstroBase.STARS[ 69 ]     :   _( "Merak" ),
            astrobase.AstroBase.STARS[ 70 ]     :   _( "Merope" ),
            astrobase.AstroBase.STARS[ 71 ]     :   _( "Miaplacidus" ),
            astrobase.AstroBase.STARS[ 72 ]     :   _( "Mimosa" ),
            astrobase.AstroBase.STARS[ 73 ]     :   _( "Minkar" ),
            astrobase.AstroBase.STARS[ 74 ]     :   _( "Mintaka" ),
            astrobase.AstroBase.STARS[ 75 ]     :   _( "Mirach" ),
            astrobase.AstroBase.STARS[ 76 ]     :   _( "Mirfak" ),
            astrobase.AstroBase.STARS[ 77 ]     :   _( "Mirzam" ),
            astrobase.AstroBase.STARS[ 78 ]     :   _( "Mizar" ),
            astrobase.AstroBase.STARS[ 79 ]     :   _( "Naos" ),
            astrobase.AstroBase.STARS[ 80 ]     :   _( "Nihal" ),
            astrobase.AstroBase.STARS[ 81 ]     :   _( "Nunki" ),
            astrobase.AstroBase.STARS[ 82 ]     :   _( "Peacock" ),
            astrobase.AstroBase.STARS[ 83 ]     :   _( "Phecda" ),
            astrobase.AstroBase.STARS[ 84 ]     :   _( "Polaris" ),
            astrobase.AstroBase.STARS[ 85 ]     :   _( "Pollux" ),
            astrobase.AstroBase.STARS[ 86 ]     :   _( "Procyon" ),
            astrobase.AstroBase.STARS[ 87 ]     :   _( "Rasalgethi" ),
            astrobase.AstroBase.STARS[ 88 ]     :   _( "Rasalhague" ),
            astrobase.AstroBase.STARS[ 89 ]     :   _( "Regulus" ),
            astrobase.AstroBase.STARS[ 90 ]     :   _( "Rigel" ),
            astrobase.AstroBase.STARS[ 91 ]     :   _( "Rigil Kentaurus" ),
            astrobase.AstroBase.STARS[ 92 ]     :   _( "Rukbat" ),
            astrobase.AstroBase.STARS[ 93 ]     :   _( "Sabik" ),
            astrobase.AstroBase.STARS[ 94 ]     :   _( "Sadalmelik" ),
            astrobase.AstroBase.STARS[ 95 ]     :   _( "Sadr" ),
            astrobase.AstroBase.STARS[ 96 ]     :   _( "Saiph" ),
            astrobase.AstroBase.STARS[ 97 ]     :   _( "Scheat" ),
            astrobase.AstroBase.STARS[ 98 ]     :   _( "Schedar" ),
            astrobase.AstroBase.STARS[ 99 ]     :   _( "Shaula" ),
            astrobase.AstroBase.STARS[ 100 ]    :   _( "Sheliak" ),
            astrobase.AstroBase.STARS[ 101 ]    :   _( "Sirius" ),
            astrobase.AstroBase.STARS[ 102 ]    :   _( "Sirrah" ),
            astrobase.AstroBase.STARS[ 103 ]    :   _( "Spica" ),
            astrobase.AstroBase.STARS[ 104 ]    :   _( "Suhail" ),
            astrobase.AstroBase.STARS[ 105 ]    :   _( "Sulafat" ),
            astrobase.AstroBase.STARS[ 106 ]    :   _( "Tarazed" ),
            astrobase.AstroBase.STARS[ 107 ]    :   _( "Taygeta" ),
            astrobase.AstroBase.STARS[ 108 ]    :   _( "Thuban" ),
            astrobase.AstroBase.STARS[ 109 ]    :   _( "Unukalhai" ),
            astrobase.AstroBase.STARS[ 110 ]    :   _( "Vega" ),
            astrobase.AstroBase.STARS[ 111 ]    :   _( "Vindemiatrix" ),
            astrobase.AstroBase.STARS[ 112 ]    :   _( "Wezen" ),
            astrobase.AstroBase.STARS[ 113 ]    :   _( "Zaurak" ),
            astrobase.AstroBase.STARS[ 114 ]    :   _( "Zubenelgenubi" ) } )

        # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
        astrobase.AstroBase.STAR_TAGS_TRANSLATIONS.update( {
            astrobase.AstroBase.STARS[ 0 ]      :   _( "ACAMAR" ),
            astrobase.AstroBase.STARS[ 1 ]      :   _( "ACHERNAR" ),
            astrobase.AstroBase.STARS[ 2 ]      :   _( "ACRUX" ),
            astrobase.AstroBase.STARS[ 3 ]      :   _( "ADARA" ),
            astrobase.AstroBase.STARS[ 4 ]      :   _( "ADHARA" ),
            astrobase.AstroBase.STARS[ 5 ]      :   _( "AGENA" ),
            astrobase.AstroBase.STARS[ 6 ]      :   _( "ALBEREO" ),
            astrobase.AstroBase.STARS[ 7 ]      :   _( "ALCAID" ),
            astrobase.AstroBase.STARS[ 8 ]      :   _( "ALCOR" ),
            astrobase.AstroBase.STARS[ 9 ]      :   _( "ALCYONE" ),
            astrobase.AstroBase.STARS[ 10 ]     :   _( "ALDEBARAN" ),
            astrobase.AstroBase.STARS[ 11 ]     :   _( "ALDERAMIN" ),
            astrobase.AstroBase.STARS[ 12 ]     :   _( "ALFIRK" ),
            astrobase.AstroBase.STARS[ 13 ]     :   _( "ALGENIB" ),
            astrobase.AstroBase.STARS[ 14 ]     :   _( "ALGIEBA" ),
            astrobase.AstroBase.STARS[ 15 ]     :   _( "ALGOL" ),
            astrobase.AstroBase.STARS[ 16 ]     :   _( "ALHENA" ),
            astrobase.AstroBase.STARS[ 17 ]     :   _( "ALIOTH" ),
            astrobase.AstroBase.STARS[ 18 ]     :   _( "ALKAID" ),
            astrobase.AstroBase.STARS[ 19 ]     :   _( "ALMACH" ),
            astrobase.AstroBase.STARS[ 20 ]     :   _( "ALNAIR" ),
            astrobase.AstroBase.STARS[ 21 ]     :   _( "ALNILAM" ),
            astrobase.AstroBase.STARS[ 22 ]     :   _( "ALNITAK" ),
            astrobase.AstroBase.STARS[ 23 ]     :   _( "ALPHARD" ),
            astrobase.AstroBase.STARS[ 24 ]     :   _( "ALPHECCA" ),
            astrobase.AstroBase.STARS[ 25 ]     :   _( "ALPHERATZ" ),
            astrobase.AstroBase.STARS[ 26 ]     :   _( "ALSHAIN" ),
            astrobase.AstroBase.STARS[ 27 ]     :   _( "ALTAIR" ),
            astrobase.AstroBase.STARS[ 28 ]     :   _( "ANKAA" ),
            astrobase.AstroBase.STARS[ 29 ]     :   _( "ANTARES" ),
            astrobase.AstroBase.STARS[ 30 ]     :   _( "ARCTURUS" ),
            astrobase.AstroBase.STARS[ 31 ]     :   _( "ARKAB POSTERIOR" ),
            astrobase.AstroBase.STARS[ 32 ]     :   _( "ARKAB PRIOR" ),
            astrobase.AstroBase.STARS[ 33 ]     :   _( "ARNEB" ),
            astrobase.AstroBase.STARS[ 34 ]     :   _( "ATLAS" ),
            astrobase.AstroBase.STARS[ 35 ]     :   _( "ATRIA" ),
            astrobase.AstroBase.STARS[ 36 ]     :   _( "AVIOR" ),
            astrobase.AstroBase.STARS[ 37 ]     :   _( "BELLATRIX" ),
            astrobase.AstroBase.STARS[ 38 ]     :   _( "BETELGEUSE" ),
            astrobase.AstroBase.STARS[ 39 ]     :   _( "CANOPUS" ),
            astrobase.AstroBase.STARS[ 40 ]     :   _( "CAPELLA" ),
            astrobase.AstroBase.STARS[ 41 ]     :   _( "CAPH" ),
            astrobase.AstroBase.STARS[ 42 ]     :   _( "CASTOR" ),
            astrobase.AstroBase.STARS[ 43 ]     :   _( "CEBALRAI" ),
            astrobase.AstroBase.STARS[ 44 ]     :   _( "DENEB" ),
            astrobase.AstroBase.STARS[ 45 ]     :   _( "DENEBOLA" ),
            astrobase.AstroBase.STARS[ 46 ]     :   _( "DIPHDA" ),
            astrobase.AstroBase.STARS[ 47 ]     :   _( "DUBHE" ),
            astrobase.AstroBase.STARS[ 48 ]     :   _( "ELECTRA" ),
            astrobase.AstroBase.STARS[ 49 ]     :   _( "ELNATH" ),
            astrobase.AstroBase.STARS[ 50 ]     :   _( "ELTANIN" ),
            astrobase.AstroBase.STARS[ 51 ]     :   _( "ENIF" ),
            astrobase.AstroBase.STARS[ 52 ]     :   _( "ETAMIN" ),
            astrobase.AstroBase.STARS[ 53 ]     :   _( "FOMALHAUT" ),
            astrobase.AstroBase.STARS[ 54 ]     :   _( "FORMALHAUT" ),
            astrobase.AstroBase.STARS[ 55 ]     :   _( "GACRUX" ),
            astrobase.AstroBase.STARS[ 56 ]     :   _( "GIENAH" ),
            astrobase.AstroBase.STARS[ 57 ]     :   _( "GIENAH CORVI" ),
            astrobase.AstroBase.STARS[ 58 ]     :   _( "HADAR" ),
            astrobase.AstroBase.STARS[ 59 ]     :   _( "HAMAL" ),
            astrobase.AstroBase.STARS[ 60 ]     :   _( "IZAR" ),
            astrobase.AstroBase.STARS[ 61 ]     :   _( "KAUS AUSTRALIS" ),
            astrobase.AstroBase.STARS[ 62 ]     :   _( "KOCHAB" ),
            astrobase.AstroBase.STARS[ 63 ]     :   _( "MAIA" ),
            astrobase.AstroBase.STARS[ 64 ]     :   _( "MARKAB" ),
            astrobase.AstroBase.STARS[ 65 ]     :   _( "MEGREZ" ),
            astrobase.AstroBase.STARS[ 66 ]     :   _( "MENKALINAN" ),
            astrobase.AstroBase.STARS[ 67 ]     :   _( "MENKAR" ),
            astrobase.AstroBase.STARS[ 68 ]     :   _( "MENKENT" ),
            astrobase.AstroBase.STARS[ 69 ]     :   _( "MERAK" ),
            astrobase.AstroBase.STARS[ 70 ]     :   _( "MEROPE" ),
            astrobase.AstroBase.STARS[ 71 ]     :   _( "MIAPLACIDUS" ),
            astrobase.AstroBase.STARS[ 72 ]     :   _( "MIMOSA" ),
            astrobase.AstroBase.STARS[ 73 ]     :   _( "MINKAR" ),
            astrobase.AstroBase.STARS[ 74 ]     :   _( "MINTAKA" ),
            astrobase.AstroBase.STARS[ 75 ]     :   _( "MIRACH" ),
            astrobase.AstroBase.STARS[ 76 ]     :   _( "MIRFAK" ),
            astrobase.AstroBase.STARS[ 77 ]     :   _( "MIRZAM" ),
            astrobase.AstroBase.STARS[ 78 ]     :   _( "MIZAR" ),
            astrobase.AstroBase.STARS[ 79 ]     :   _( "NAOS" ),
            astrobase.AstroBase.STARS[ 80 ]     :   _( "NIHAL" ),
            astrobase.AstroBase.STARS[ 81 ]     :   _( "NUNKI" ),
            astrobase.AstroBase.STARS[ 82 ]     :   _( "PEACOCK" ),
            astrobase.AstroBase.STARS[ 83 ]     :   _( "PHECDA" ),
            astrobase.AstroBase.STARS[ 84 ]     :   _( "POLARIS" ),
            astrobase.AstroBase.STARS[ 85 ]     :   _( "POLLUX" ),
            astrobase.AstroBase.STARS[ 86 ]     :   _( "PROCYON" ),
            astrobase.AstroBase.STARS[ 87 ]     :   _( "RASALGETHI" ),
            astrobase.AstroBase.STARS[ 88 ]     :   _( "RASALHAGUE" ),
            astrobase.AstroBase.STARS[ 89 ]     :   _( "REGULUS" ),
            astrobase.AstroBase.STARS[ 90 ]     :   _( "RIGEL" ),
            astrobase.AstroBase.STARS[ 91 ]     :   _( "RIGIL KENTAURUS" ),
            astrobase.AstroBase.STARS[ 92 ]     :   _( "RUKBAT" ),
            astrobase.AstroBase.STARS[ 93 ]     :   _( "SABIK" ),
            astrobase.AstroBase.STARS[ 94 ]     :   _( "SADALMELIK" ),
            astrobase.AstroBase.STARS[ 95 ]     :   _( "SADR" ),
            astrobase.AstroBase.STARS[ 96 ]     :   _( "SAIPH" ),
            astrobase.AstroBase.STARS[ 97 ]     :   _( "SCHEAT" ),
            astrobase.AstroBase.STARS[ 98 ]     :   _( "SCHEDAR" ),
            astrobase.AstroBase.STARS[ 99 ]     :   _( "SHAULA" ),
            astrobase.AstroBase.STARS[ 100 ]    :   _( "SHELIAK" ),
            astrobase.AstroBase.STARS[ 101 ]    :   _( "SIRIUS" ),
            astrobase.AstroBase.STARS[ 102 ]    :   _( "SIRRAH" ),
            astrobase.AstroBase.STARS[ 103 ]    :   _( "SPICA" ),
            astrobase.AstroBase.STARS[ 104 ]    :   _( "SUHAIL" ),
            astrobase.AstroBase.STARS[ 105 ]    :   _( "SULAFAT" ),
            astrobase.AstroBase.STARS[ 106 ]    :   _( "TARAZED" ),
            astrobase.AstroBase.STARS[ 107 ]    :   _( "TAYGETA" ),
            astrobase.AstroBase.STARS[ 108 ]    :   _( "THUBAN" ),
            astrobase.AstroBase.STARS[ 109 ]    :   _( "UNUKALHAI" ),
            astrobase.AstroBase.STARS[ 110 ]    :   _( "VEGA" ),
            astrobase.AstroBase.STARS[ 111 ]    :   _( "VINDEMIATRIX" ),
            astrobase.AstroBase.STARS[ 112 ]    :   _( "WEZEN" ),
            astrobase.AstroBase.STARS[ 113 ]    :   _( "ZAURAK" ),
            astrobase.AstroBase.STARS[ 114 ]    :   _( "ZUBENELGENUBI" ) } )


    # Internally used for city.
    __DATA_TAG_ELEVATION = "ELEVATION"
    __DATA_TAG_LATITUDE = "LATITUDE"
    __DATA_TAG_LONGITUDE = "LONGITUDE"
    __NAME_TAG_CITY = "CITY"


    # Internally used to reference PyEphem objects.
    __PYEPHEM_CITY_LATITUDE = 0
    __PYEPHEM_CITY_LONGITUDE = 1
    __PYEPHEM_CITY_ELEVATION = 2

    __PYEPHEM_DATE_TUPLE_YEAR = 0
    __PYEPHEM_DATE_TUPLE_MONTH = 1
    __PYEPHEM_DATE_TUPLE_DAY = 2
    __PYEPHEM_DATE_TUPLE_HOUR = 3
    __PYEPHEM_DATE_TUPLE_MINUTE = 4
    __PYEPHEM_DATE_TUPLE_SECOND = 5

    __PYEPHEM_SATELLITE_PASS_RISING_DATE = 0
    __PYEPHEM_SATELLITE_PASS_RISING_ANGLE = 1
    __PYEPHEM_SATELLITE_PASS_CULMINATION_DATE = 2
    __PYEPHEM_SATELLITE_PASS_CULMINATION_ANGLE = 3
    __PYEPHEM_SATELLITE_PASS_SETTING_DATE = 4
    __PYEPHEM_SATELLITE_PASS_SETTING_ANGLE = 5


    @staticmethod
    def calculate(
            utcNow,
            latitude, longitude, elevation,
            planets,
            stars,
            satellites, satelliteData, startHour, endHour,
            comets, cometData,
            minorPlanets, minorPlanetData,
            magnitudeMaximum,
            logging ):

        data = { }

        # Used internally; removed before passing back to the caller.
        data[ ( None, AstroPyEphem.__NAME_TAG_CITY, AstroPyEphem.__DATA_TAG_LATITUDE ) ] = str( latitude )
        data[ ( None, AstroPyEphem.__NAME_TAG_CITY, AstroPyEphem.__DATA_TAG_LONGITUDE ) ] = str( longitude )
        data[ ( None, AstroPyEphem.__NAME_TAG_CITY, AstroPyEphem.__DATA_TAG_ELEVATION ) ] = str( elevation )

        ephemNow = ephem.Date( utcNow )

        AstroPyEphem.__calculateMoon( ephemNow, data )
        AstroPyEphem.__calculateSun( ephemNow, data )
        AstroPyEphem.__calculatePlanets( ephemNow, data, planets, magnitudeMaximum )
        AstroPyEphem.__calculateStars( ephemNow, data, stars, magnitudeMaximum )
        AstroPyEphem.__calculateOrbitalElements( ephemNow, data, astrobase.AstroBase.BodyType.COMET, comets, cometData, magnitudeMaximum )
        AstroPyEphem.__calculateOrbitalElements( ephemNow, data, astrobase.AstroBase.BodyType.MINOR_PLANET, minorPlanets, minorPlanetData, magnitudeMaximum )
        AstroPyEphem.__calculateSatellites( ephemNow, data, satellites, satelliteData, startHour, endHour )

        del data[ ( None, AstroPyEphem.__NAME_TAG_CITY, AstroPyEphem.__DATA_TAG_LATITUDE ) ]
        del data[ ( None, AstroPyEphem.__NAME_TAG_CITY, AstroPyEphem.__DATA_TAG_LONGITUDE ) ]
        del data[ ( None, AstroPyEphem.__NAME_TAG_CITY, AstroPyEphem.__DATA_TAG_ELEVATION ) ]

        return data


    @staticmethod
    def getAvailabilityMessage():
        message = None
        if not available:
            message = _( "PyEphem could not be found. Install using:\n\n" + AstroPyEphem.__PYEPHEM_INSTALLATION_COMMAND )

        return message


    @staticmethod
    def getCities(): return sorted( _city_data.keys(), key = locale.strxfrm )


    @staticmethod
    def getCredit(): return _( "Calculations courtesy of PyEphem/XEphem. https://rhodesmill.org/pyephem" )


    @staticmethod
    def getLatitudeLongitudeElevation( city ):
        return \
            float( _city_data.get( city )[ AstroPyEphem.__PYEPHEM_CITY_LATITUDE ] ), \
            float( _city_data.get( city )[ AstroPyEphem.__PYEPHEM_CITY_LONGITUDE ] ), \
            _city_data.get( city )[ AstroPyEphem.__PYEPHEM_CITY_ELEVATION ]


    @staticmethod
    def getOrbitalElementsLessThanMagnitude( utcNow, orbitalElementData, magnitudeMaximum ):
        results = { }
        for key in orbitalElementData:
            city = ephem.city( "London" ) # Use any city; makes no difference to obtain the magnitude.
            city.date = utcNow
            body = ephem.readdb( orbitalElementData[ key ].getData() )
            body.compute( city )
            bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
            if not bad and body.mag >= astrobase.AstroBase.MAGNITUDE_MINIMUM and body.mag <= magnitudeMaximum:
                results[ key ] = orbitalElementData[ key ]

        return results


    @staticmethod
    def getVersion(): return ephem.__version__


    @staticmethod
    def getVersionMessage():
        message = None
        if LooseVersion( ephem.__version__ ) < LooseVersion( AstroPyEphem.__PYEPHEM_REQUIRED_VERSION ):
            message = \
                _( "PyEphem must be version {0} or greater. Please upgrade:\n\n" + \
                AstroPyEphem.__PYEPHEM_INSTALLATION_COMMAND ).format( AstroPyEphem.__PYEPHEM_REQUIRED_VERSION )

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
    def __calculateMoon( ephemNow, data ):
        # Used for internal processing; indirectly presented to the user.
        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        moon = ephem.Moon()
        moon.compute( AstroPyEphem.__getCity( data, ephemNow ) )
        data[ key + ( astrobase.AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( int( moon.phase ) ) # Needed for icon.

        phase = astrobase.AstroBase.getLunarPhase( int( moon.phase ), ephem.next_full_moon( ephemNow ), ephem.next_new_moon( ephemNow ) ) # Need for notification.
        data[ key + ( astrobase.AstroBase.DATA_TAG_PHASE, ) ] = phase

        city = AstroPyEphem.__getCity( data, ephemNow )
        sun = ephem.Sun( city )
        moon = ephem.Moon()
        moon.compute( city )
        brightLimb = astrobase.AstroBase.getZenithAngleOfBrightLimb( ephemNow.datetime(), sun.ra, sun.dec, moon.ra, moon.dec, float( city.lat ), float( city.lon ) )
        data[ key + ( astrobase.AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( brightLimb ) # Needed for icon.

        if not AstroPyEphem.__calculateCommon( ephemNow, data, ephem.Moon(), astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON ):
            data[ key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_first_quarter_moon( ephemNow ).datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_full_moon( ephemNow ).datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_last_quarter_moon( ephemNow ).datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_new_moon( ephemNow ).datetime() )

            dateTime, eclipseType, latitude, longitude = eclipse.getEclipse( ephemNow.datetime(), True )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTime
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseType
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude


    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    # http://www.ga.gov.au/geodesy/astro/sunrise.jsp
    # http://www.geoastro.de/elevaz/index.htm
    # http://www.geoastro.de/SME/index.htm
    # http://www.geoastro.de/altazsunmoon/index.htm
    # http://futureboy.us/fsp/sun.fsp
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    @staticmethod
    def __calculateSun( ephemNow, data ):
        if not AstroPyEphem.__calculateCommon( ephemNow, data, ephem.Sun(), astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN ):
            key = ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )
            equinox = ephem.next_equinox( ephemNow )
            solstice = ephem.next_solstice( ephemNow )
            data[ key + ( astrobase.AstroBase.DATA_TAG_EQUINOX, ) ] = astrobase.AstroBase.toDateTimeString( equinox.datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_SOLSTICE, ) ] = astrobase.AstroBase.toDateTimeString( solstice.datetime() )

            dateTime, eclipseType, latitude, longitude = eclipse.getEclipse( ephemNow.datetime(), False )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTime
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseType
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude


    # http://www.geoastro.de/planets/index.html
    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    @staticmethod
    def __calculatePlanets( ephemNow, data, planets, magnitudeMaximum ):
        for planet in planets:
            planetObject = getattr( ephem, planet.title() )()
            planetObject.compute( AstroPyEphem.__getCity( data, ephemNow ) )
            if planetObject.mag <= magnitudeMaximum:
                AstroPyEphem.__calculateCommon( ephemNow, data, planetObject, astrobase.AstroBase.BodyType.PLANET, planet )


    # http://aa.usno.navy.mil/data/docs/mrst.php
    @staticmethod
    def __calculateStars( ephemNow, data, stars, magnitudeMaximum ):
        for star in stars:
            if star in astrobase.AstroBase.STARS: # Ensure that a star is present if/when switching between PyEphem and Skyfield.
                starObject = ephem.star( star.title() )
                starObject.compute( AstroPyEphem.__getCity( data, ephemNow ) )
                if starObject.mag <= magnitudeMaximum:
                    AstroPyEphem.__calculateCommon( ephemNow, data, starObject, astrobase.AstroBase.BodyType.STAR, star )


    # Compute data for comets or minor planets.
    @staticmethod
    def __calculateOrbitalElements( ephemNow, data, bodyType, orbitalElements, orbitalElementData, magnitudeMaximum ):
        for key in orbitalElements:
            if key in orbitalElementData:
                body = ephem.readdb( orbitalElementData[ key ].getData() )
                body.compute( AstroPyEphem.__getCity( data, ephemNow ) )
                bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
                if not bad and body.mag <= magnitudeMaximum:
                    AstroPyEphem.__calculateCommon( ephemNow, data, body, bodyType, key )


    # Calculates common attributes such as rise/set date/time, azimuth/altitude.
    #
    # Returns True if the body is never up; false otherwise.
    @staticmethod
    def __calculateCommon( ephemNow, data, body, bodyType, nameTag ):
        neverUp = False
        key = ( bodyType, nameTag )
        try:
            city = AstroPyEphem.__getCity( data, ephemNow )
            data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( city.next_rising( body ).datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( city.next_setting( body ).datetime() )

            body.compute( AstroPyEphem.__getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )

        except ephem.AlwaysUpError:
            body.compute( AstroPyEphem.__getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )

        except ephem.NeverUpError:
            neverUp = True

        return neverUp


    # Refer to
    #    https://github.com/skyfielders/python-skyfield/issues/327
    #    https://github.com/skyfielders/python-skyfield/issues/558
    #    http://www.celestrak.com/columns/v03n01/
    #
    # Use TLE data collated by Dr T S Kelso
    #    http://celestrak.com/NORAD/elements
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
    def __calculateSatellites( ephemNow, data, satellites, satelliteData, startHour, endHour ):
        
        # startHour = 19 # 5am Sydney 
        # endHour = 1 # 11am Sydney 
        
        endDateTime = ephem.Date( ephemNow + ephem.hour * astrobase.AstroBase.SATELLITE_SEARCH_DURATION_HOURS )
        for satellite in satellites:
            if satellite in satelliteData:
                currentDateTime = AstroPyEphem.__adjustCurrentDateTime( ephemNow, startHour, endHour )
                while currentDateTime < endDateTime:
                    city = AstroPyEphem.__getCity( data, currentDateTime )
                    earthSatellite = ephem.readtle( satelliteData[ satellite ].getName(), satelliteData[ satellite ].getLine1(), satelliteData[ satellite ].getLine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
                    earthSatellite.compute( city )
                    key = ( astrobase.AstroBase.BodyType.SATELLITE, satellite )
                    try:
                        nextPass = AstroPyEphem.__calculateNextSatellitePass( city, earthSatellite )
                        if AstroPyEphem.__isSatellitePassValid( nextPass ) and \
                           AstroPyEphem.__isSatetllitePassWithinTimes( nextPass, startHour, endHour ) and \
                           AstroPyEphem.__isSatellitePassVisible( data, nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_CULMINATION_DATE ], earthSatellite ):

                            data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = \
                                astrobase.AstroBase.toDateTimeString( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_RISING_DATE ].datetime() )

                            data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH, ) ] = \
                                repr( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_RISING_ANGLE ] )

                            data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = \
                                astrobase.AstroBase.toDateTimeString( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_SETTING_DATE ].datetime() )

                            data[ key + ( astrobase.AstroBase.DATA_TAG_SET_AZIMUTH, ) ] = repr( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_SETTING_ANGLE ] )
                            break

                        if AstroPyEphem.__isSatellitePassValid( nextPass ):
                            currentDateTime = ephem.Date( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_SETTING_DATE ] + ephem.minute * 15 ) # Look for the next pass starting shortly after current set.

                        else:
                            currentDateTime = ephem.Date( currentDateTime + ephem.minute * 60 ) # Bad pass data, so look one hour after the current time.

                        currentDateTime = AstroPyEphem.__adjustCurrentDateTime( currentDateTime, startHour, endHour )

                    except ValueError:
                        if earthSatellite.circumpolar: # Satellite never rises/sets, so can only show current position.
                            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( earthSatellite.az )
                            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( earthSatellite.alt )

                        break


#TODO Comment!
    @staticmethod
    def __adjustCurrentDateTime( currentDateTime, startHour, endHour ):

# startHour = 19 # 5am Sydney 
# endHour = 3 # 1pm Sydney 

        def setHour( dateTimeTuple, hour ):
            return \
                ephem.Date( 
                    ( dateTimeTuple[ AstroPyEphem.__PYEPHEM_DATE_TUPLE_YEAR ], 
                      dateTimeTuple[ AstroPyEphem.__PYEPHEM_DATE_TUPLE_MONTH ], 
                      dateTimeTuple[ AstroPyEphem.__PYEPHEM_DATE_TUPLE_DAY ], hour, 0, 0 ) )

        currentDateTimeTuple = currentDateTime.tuple()
        currentHour = currentDateTimeTuple[ AstroPyEphem.__PYEPHEM_DATE_TUPLE_HOUR ]
        if startHour < endHour:
            if currentHour < startHour:
                currentDateTime = setHour( currentDateTimeTuple, startHour )

            elif currentHour >= endHour:
                currentDateTime = setHour( currentDateTimeTuple, startHour )
                currentDateTime = ephem.Date( currentDateTime + 1 )

        else:
            if currentHour < endHour:
            
            if currentHour < startHour:
                currentDateTime = setHour( currentDateTimeTuple, startHour )

            elif currentHour >= endHour:
                currentDateTime = setHour( currentDateTimeTuple, startHour )
                currentDateTime = ephem.Date( currentDateTime + 1 )

        return currentDateTime


    # Due to a change between PyEphem 3.7.6.0 and 3.7.7.0, need to check for passes differently.
    #    https://rhodesmill.org/pyephem/CHANGELOG.html#version-3-7-7-0-2019-august-18
    #    https://github.com/brandon-rhodes/pyephem/issues/63#issuecomment-144263243
    @staticmethod
    def __calculateNextSatellitePass( city, satellite ):
        if LooseVersion( ephem.__version__ ) < LooseVersion( "3.7.7.0" ):
            nextPass = city.next_pass( satellite )

        else:
            # Must set singlepass = False to avoid the new code in PyEphem (and so behave prior to this change).
            # It is possible a pass is too quick/low and an exception is thrown.
            # https://github.com/brandon-rhodes/pyephem/issues/164
            # https://github.com/brandon-rhodes/pyephem/pull/85/files
            nextPass = city.next_pass( satellite, singlepass = False )

        return nextPass


    # Ensure:
    #    The satellite pass is numerically valid.
    #    Rise time exceeds transit time.
    #    Transit time exceeds set time.
    @staticmethod
    def __isSatellitePassValid( satellitePass ):
        return \
            satellitePass and \
            len( satellitePass ) == 6 and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_RISING_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_RISING_ANGLE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_CULMINATION_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_CULMINATION_ANGLE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_SETTING_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_SETTING_ANGLE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_CULMINATION_DATE ] > satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_RISING_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_SETTING_DATE ] > satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_CULMINATION_DATE ]


#TODO Comment!
    # Determine if the satellite pass falls anywhere between a start hour and end hour.
    # This is not to determine if a pass is visible; rather it is a hard border for a pass.
    # Given that visibility is determined elsewhere, a pass need not completely fall with the boundary. 
    #
    # The end user will specify the start and end hour in the local time zone.
    # As such, the start and end hour will be converted to UTC,
    # which may result in the start hour coming after the end hour.
    #
    # Scenarios...not to scale!
    #
    #
    # startHour = 6 UTC (4pm Sydney), endHour = 11 UTC (9pm Sydney)
    #            0                6                12                18               0
    #           UTC              UTC               UTC               UTC             UTC
    #        
    #               RISE    SET                                                            Out of bounds
    #               RISE              SET                                                  In bounds
    #               RISE                                   SET                             In bounds
    #                                 RISE                 SET                             In bounds
    #                                                      RISE    SET                     Out of bounds
    #                             ^            ^ 
    #                           START         END
    #
    #
    # startHour = 17 UTC (3am Sydney), endHour = 20 UTC (6am Sydney)
    #            0                6                12                18               0
    #           UTC              UTC               UTC               UTC             UTC
    #        
    #                                               RISE    SET                                     Out of bounds
    #                                               RISE              SET                           In bounds
    #                                                       RISE                     SET            In bounds
    #                                                                 RISE           SET            In bounds
    #                                                                                RISE    SET    Out of bounds
    #                                                             ^            ^ 
    #                                                           START         END
    #
    #
    # startHour = 21 UTC (3am India), endHour = 1 UTC (7am India)
    #            0                6                12                18               0
    #           UTC              UTC               UTC               UTC             UTC
    #        
    #  RISE      SET                                                                                     
    #            RISE        SET                                                                           In bounds
    #            RISE                                                             SET                    In bounds
    #                                    RISE           SET                                                In bounds
    #                                                                RISE            SET                    Out of bounds
    #                                                                            RISE            SET          Out of bounds
    #                 ^                                                      ^ 
    #                END                                                   START
    #
    #
    @staticmethod
    def __isSatetllitePassWithinTimes( satellitePass, startHour, endHour ):
        riseHour = satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_RISING_DATE ].tuple()[ AstroPyEphem.__PYEPHEM_DATE_TUPLE_HOUR ]
        setHour = satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_PASS_SETTING_DATE ].tuple()[ AstroPyEphem.__PYEPHEM_DATE_TUPLE_HOUR ]

#TODO Maybe consider letting a pass through if it starts or ends within the time,
# because the visibility test will remove the pass regardless if not visible.

        if startHour < endHour:
            passWithinTimes = \
                ( riseHour >= startHour and riseHour < endHour ) \ or
                ( setHour >= startHour and setHour < endHour )

        else:
#TODO Need to check this works...but also the >= and <.
            passWithinTimes = \
                ( riseHour >= startHour and riseHour < endHour ) \ or
                ( setHour >= startHour and setHour < endHour )

            passWithinTimes = not ( ( riseHour >= endHour ) and ( setHour < startHour ) )

        return passWithinTimes


    # Determine if a satellite pass is visible.
    #
    #    https://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
    #    https://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
    #    https://www.celestrak.com/columns/v03n01
    @staticmethod
    def __isSatellitePassVisible( data, passDateTime, satellite ):
        city = AstroPyEphem.__getCity( data, passDateTime )
        city.pressure = 0
        city.horizon = "-0:34"

        satellite.compute( city )
        sun = ephem.Sun()
        sun.compute( city )

        return \
            satellite.eclipsed is False and \
            sun.alt > ephem.degrees( "-18" ) and \
            sun.alt < ephem.degrees( "-6" )


    @staticmethod
    def __getCity( data, date ):
        city = ephem.city( "London" ) # Put in a city name known to exist in PyEphem then doctor to the correct lat/long/elev.
        city.date = date
        city.lat = data[ ( None, AstroPyEphem.__NAME_TAG_CITY, AstroPyEphem.__DATA_TAG_LATITUDE ) ]
        city.lon = data[ ( None, AstroPyEphem.__NAME_TAG_CITY, AstroPyEphem.__DATA_TAG_LONGITUDE ) ]
        city.elev = float( data[ ( None, AstroPyEphem.__NAME_TAG_CITY, AstroPyEphem.__DATA_TAG_ELEVATION ) ] )

        return city