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

from astrobase import AstroBase
from distutils.version import LooseVersion

import datetime, eclipse, locale, math


class AstroPyEphem( AstroBase ):

    # Taken from ephem/stars.py
    # Version 3.7.7.0 added new stars but must still support 3.7.6.0 for Ubuntu 16.04/18.04.
    if LooseVersion( ephem.__version__ ) < LooseVersion( "3.7.7.0" ):
        AstroBase.STARS.extend( [
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

        AstroBase.STARS_TO_HIP.update( {
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

        AstroBase.STAR_NAMES_TRANSLATIONS.update( {
            AstroBase.STARS[ 0 ]  :   _( "Achernar" ),
            AstroBase.STARS[ 1 ]  :   _( "Adara" ),
            AstroBase.STARS[ 2 ]  :   _( "Agena" ),
            AstroBase.STARS[ 3 ]  :   _( "Albereo" ),
            AstroBase.STARS[ 4 ]  :   _( "Alcaid" ),
            AstroBase.STARS[ 5 ]  :   _( "Alcor" ),
            AstroBase.STARS[ 6 ]  :   _( "Alcyone" ),
            AstroBase.STARS[ 7 ]  :   _( "Aldebaran" ),
            AstroBase.STARS[ 8 ]  :   _( "Alderamin" ),
            AstroBase.STARS[ 9 ]  :   _( "Alfirk" ),
            AstroBase.STARS[ 10 ] :   _( "Algenib" ),
            AstroBase.STARS[ 11 ] :   _( "Algieba" ),
            AstroBase.STARS[ 12 ] :   _( "Algol" ),
            AstroBase.STARS[ 13 ] :   _( "Alhena" ),
            AstroBase.STARS[ 14 ] :   _( "Alioth" ),
            AstroBase.STARS[ 15 ] :   _( "Almach" ),
            AstroBase.STARS[ 16 ] :   _( "Alnair" ),
            AstroBase.STARS[ 17 ] :   _( "Alnilam" ),
            AstroBase.STARS[ 18 ] :   _( "Alnitak" ),
            AstroBase.STARS[ 19 ] :   _( "Alphard" ),
            AstroBase.STARS[ 20 ] :   _( "Alphecca" ),
            AstroBase.STARS[ 21 ] :   _( "Alshain" ),
            AstroBase.STARS[ 22 ] :   _( "Altair" ),
            AstroBase.STARS[ 23 ] :   _( "Antares" ),
            AstroBase.STARS[ 24 ] :   _( "Arcturus" ),
            AstroBase.STARS[ 25 ] :   _( "Arkab Posterior" ),
            AstroBase.STARS[ 26 ] :   _( "Arkab Prior" ),
            AstroBase.STARS[ 27 ] :   _( "Arneb" ),
            AstroBase.STARS[ 28 ] :   _( "Atlas" ),
            AstroBase.STARS[ 29 ] :   _( "Bellatrix" ),
            AstroBase.STARS[ 30 ] :   _( "Betelgeuse" ),
            AstroBase.STARS[ 31 ] :   _( "Canopus" ),
            AstroBase.STARS[ 32 ] :   _( "Capella" ),
            AstroBase.STARS[ 33 ] :   _( "Caph" ),
            AstroBase.STARS[ 34 ] :   _( "Castor" ),
            AstroBase.STARS[ 35 ] :   _( "Cebalrai" ),
            AstroBase.STARS[ 36 ] :   _( "Deneb" ),
            AstroBase.STARS[ 37 ] :   _( "Denebola" ),
            AstroBase.STARS[ 38 ] :   _( "Dubhe" ),
            AstroBase.STARS[ 39 ] :   _( "Electra" ),
            AstroBase.STARS[ 40 ] :   _( "Elnath" ),
            AstroBase.STARS[ 41 ] :   _( "Enif" ),
            AstroBase.STARS[ 42 ] :   _( "Etamin" ),
            AstroBase.STARS[ 43 ] :   _( "Fomalhaut" ),
            AstroBase.STARS[ 44 ] :   _( "Gienah Corvi" ),
            AstroBase.STARS[ 45 ] :   _( "Hamal" ),
            AstroBase.STARS[ 46 ] :   _( "Izar" ),
            AstroBase.STARS[ 47 ] :   _( "Kaus Australis" ),
            AstroBase.STARS[ 48 ] :   _( "Kochab" ),
            AstroBase.STARS[ 49 ] :   _( "Maia" ),
            AstroBase.STARS[ 50 ] :   _( "Markab" ),
            AstroBase.STARS[ 51 ] :   _( "Megrez" ),
            AstroBase.STARS[ 52 ] :   _( "Menkalinan" ),
            AstroBase.STARS[ 53 ] :   _( "Menkar" ),
            AstroBase.STARS[ 54 ] :   _( "Merak" ),
            AstroBase.STARS[ 55 ] :   _( "Merope" ),
            AstroBase.STARS[ 56 ] :   _( "Mimosa" ),
            AstroBase.STARS[ 57 ] :   _( "Minkar" ),
            AstroBase.STARS[ 58 ] :   _( "Mintaka" ),
            AstroBase.STARS[ 59 ] :   _( "Mirach" ),
            AstroBase.STARS[ 60 ] :   _( "Mirzam" ),
            AstroBase.STARS[ 61 ] :   _( "Mizar" ),
            AstroBase.STARS[ 62 ] :   _( "Naos" ),
            AstroBase.STARS[ 63 ] :   _( "Nihal" ),
            AstroBase.STARS[ 64 ] :   _( "Nunki" ),
            AstroBase.STARS[ 65 ] :   _( "Peacock" ),
            AstroBase.STARS[ 66 ] :   _( "Phecda" ),
            AstroBase.STARS[ 67 ] :   _( "Polaris" ),
            AstroBase.STARS[ 68 ] :   _( "Pollux" ),
            AstroBase.STARS[ 69 ] :   _( "Procyon" ),
            AstroBase.STARS[ 70 ] :   _( "Rasalgethi" ),
            AstroBase.STARS[ 71 ] :   _( "Rasalhague" ),
            AstroBase.STARS[ 72 ] :   _( "Regulus" ),
            AstroBase.STARS[ 73 ] :   _( "Rigel" ),
            AstroBase.STARS[ 74 ] :   _( "Rukbat" ),
            AstroBase.STARS[ 75 ] :   _( "Sadalmelik" ),
            AstroBase.STARS[ 76 ] :   _( "Sadr" ),
            AstroBase.STARS[ 77 ] :   _( "Saiph" ),
            AstroBase.STARS[ 78 ] :   _( "Scheat" ),
            AstroBase.STARS[ 79 ] :   _( "Schedar" ),
            AstroBase.STARS[ 80 ] :   _( "Shaula" ),
            AstroBase.STARS[ 81 ] :   _( "Sheliak" ),
            AstroBase.STARS[ 82 ] :   _( "Sirius" ),
            AstroBase.STARS[ 83 ] :   _( "Sirrah" ),
            AstroBase.STARS[ 84 ] :   _( "Spica" ),
            AstroBase.STARS[ 85 ] :   _( "Sulafat" ),
            AstroBase.STARS[ 86 ] :   _( "Tarazed" ),
            AstroBase.STARS[ 87 ] :   _( "Taygeta" ),
            AstroBase.STARS[ 88 ] :   _( "Thuban" ),
            AstroBase.STARS[ 89 ] :   _( "Unukalhai" ),
            AstroBase.STARS[ 90 ] :   _( "Vega" ),
            AstroBase.STARS[ 91 ] :   _( "Vindemiatrix" ),
            AstroBase.STARS[ 92 ] :   _( "Wezen" ),
            AstroBase.STARS[ 93 ] :   _( "Zaurak" ) } )

        # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
        AstroBase.STAR_TAGS_TRANSLATIONS.update( {
            AstroBase.STARS[ 0 ]  :   _( "ACHERNAR" ),
            AstroBase.STARS[ 1 ]  :   _( "ADARA" ),
            AstroBase.STARS[ 2 ]  :   _( "AGENA" ),
            AstroBase.STARS[ 3 ]  :   _( "ALBEREO" ),
            AstroBase.STARS[ 4 ]  :   _( "ALCAID" ),
            AstroBase.STARS[ 5 ]  :   _( "ALCOR" ),
            AstroBase.STARS[ 6 ]  :   _( "ALCYONE" ),
            AstroBase.STARS[ 7 ]  :   _( "ALDEBARAN" ),
            AstroBase.STARS[ 8 ]  :   _( "ALDERAMIN" ),
            AstroBase.STARS[ 9 ]  :   _( "ALFIRK" ),
            AstroBase.STARS[ 10 ] :   _( "ALGENIB" ),
            AstroBase.STARS[ 11 ] :   _( "ALGIEBA" ),
            AstroBase.STARS[ 12 ] :   _( "ALGOL" ),
            AstroBase.STARS[ 13 ] :   _( "ALHENA" ),
            AstroBase.STARS[ 14 ] :   _( "ALIOTH" ),
            AstroBase.STARS[ 15 ] :   _( "ALMACH" ),
            AstroBase.STARS[ 16 ] :   _( "ALNAIR" ),
            AstroBase.STARS[ 17 ] :   _( "ALNILAM" ),
            AstroBase.STARS[ 18 ] :   _( "ALNITAK" ),
            AstroBase.STARS[ 19 ] :   _( "ALPHARD" ),
            AstroBase.STARS[ 20 ] :   _( "ALPHECCA" ),
            AstroBase.STARS[ 21 ] :   _( "ALSHAIN" ),
            AstroBase.STARS[ 22 ] :   _( "ALTAIR" ),
            AstroBase.STARS[ 23 ] :   _( "ANTARES" ),
            AstroBase.STARS[ 24 ] :   _( "ARCTURUS" ),
            AstroBase.STARS[ 25 ] :   _( "ARKAB POSTERIOR" ),
            AstroBase.STARS[ 26 ] :   _( "ARKAB PRIOR" ),
            AstroBase.STARS[ 27 ] :   _( "ARNEB" ),
            AstroBase.STARS[ 28 ] :   _( "ATLAS" ),
            AstroBase.STARS[ 29 ] :   _( "BELLATRIX" ),
            AstroBase.STARS[ 30 ] :   _( "BETELGEUSE" ),
            AstroBase.STARS[ 31 ] :   _( "CANOPUS" ),
            AstroBase.STARS[ 32 ] :   _( "CAPELLA" ),
            AstroBase.STARS[ 33 ] :   _( "CAPH" ),
            AstroBase.STARS[ 34 ] :   _( "CASTOR" ),
            AstroBase.STARS[ 35 ] :   _( "CEBALRAI" ),
            AstroBase.STARS[ 36 ] :   _( "DENEB" ),
            AstroBase.STARS[ 37 ] :   _( "DENEBOLA" ),
            AstroBase.STARS[ 38 ] :   _( "DUBHE" ),
            AstroBase.STARS[ 39 ] :   _( "ELECTRA" ),
            AstroBase.STARS[ 40 ] :   _( "ELNATH" ),
            AstroBase.STARS[ 41 ] :   _( "ENIF" ),
            AstroBase.STARS[ 42 ] :   _( "ETAMIN" ),
            AstroBase.STARS[ 43 ] :   _( "FOMALHAUT" ),
            AstroBase.STARS[ 44 ] :   _( "GIENAH CORVI" ),
            AstroBase.STARS[ 45 ] :   _( "HAMAL" ),
            AstroBase.STARS[ 46 ] :   _( "IZAR" ),
            AstroBase.STARS[ 47 ] :   _( "KAUS AUSTRALIS" ),
            AstroBase.STARS[ 48 ] :   _( "KOCHAB" ),
            AstroBase.STARS[ 49 ] :   _( "MAIA" ),
            AstroBase.STARS[ 50 ] :   _( "MARKAB" ),
            AstroBase.STARS[ 51 ] :   _( "MEGREZ" ),
            AstroBase.STARS[ 52 ] :   _( "MENKALINAN" ),
            AstroBase.STARS[ 53 ] :   _( "MENKAR" ),
            AstroBase.STARS[ 54 ] :   _( "MERAK" ),
            AstroBase.STARS[ 55 ] :   _( "MEROPE" ),
            AstroBase.STARS[ 56 ] :   _( "MIMOSA" ),
            AstroBase.STARS[ 57 ] :   _( "MINKAR" ),
            AstroBase.STARS[ 58 ] :   _( "MINTAKA" ),
            AstroBase.STARS[ 59 ] :   _( "MIRACH" ),
            AstroBase.STARS[ 60 ] :   _( "MIRZAM" ),
            AstroBase.STARS[ 61 ] :   _( "MIZAR" ),
            AstroBase.STARS[ 62 ] :   _( "NAOS" ),
            AstroBase.STARS[ 63 ] :   _( "NIHAL" ),
            AstroBase.STARS[ 64 ] :   _( "NUNKI" ),
            AstroBase.STARS[ 65 ] :   _( "PEACOCK" ),
            AstroBase.STARS[ 66 ] :   _( "PHECDA" ),
            AstroBase.STARS[ 67 ] :   _( "POLARIS" ),
            AstroBase.STARS[ 68 ] :   _( "POLLUX" ),
            AstroBase.STARS[ 69 ] :   _( "PROCYON" ),
            AstroBase.STARS[ 70 ] :   _( "RASALGETHI" ),
            AstroBase.STARS[ 71 ] :   _( "RASALHAGUE" ),
            AstroBase.STARS[ 72 ] :   _( "REGULUS" ),
            AstroBase.STARS[ 73 ] :   _( "RIGEL" ),
            AstroBase.STARS[ 74 ] :   _( "RUKBAT" ),
            AstroBase.STARS[ 75 ] :   _( "SADALMELIK" ),
            AstroBase.STARS[ 76 ] :   _( "SADR" ),
            AstroBase.STARS[ 77 ] :   _( "SAIPH" ),
            AstroBase.STARS[ 78 ] :   _( "SCHEAT" ),
            AstroBase.STARS[ 79 ] :   _( "SCHEDAR" ),
            AstroBase.STARS[ 80 ] :   _( "SHAULA" ),
            AstroBase.STARS[ 81 ] :   _( "SHELIAK" ),
            AstroBase.STARS[ 82 ] :   _( "SIRIUS" ),
            AstroBase.STARS[ 83 ] :   _( "SIRRAH" ),
            AstroBase.STARS[ 84 ] :   _( "SPICA" ),
            AstroBase.STARS[ 85 ] :   _( "SULAFAT" ),
            AstroBase.STARS[ 86 ] :   _( "TARAZED" ),
            AstroBase.STARS[ 87 ] :   _( "TAYGETA" ),
            AstroBase.STARS[ 88 ] :   _( "THUBAN" ),
            AstroBase.STARS[ 89 ] :   _( "UNUKALHAI" ),
            AstroBase.STARS[ 90 ] :   _( "VEGA" ),
            AstroBase.STARS[ 91 ] :   _( "VINDEMIATRIX" ),
            AstroBase.STARS[ 92 ] :   _( "WEZEN" ),
            AstroBase.STARS[ 93 ] :   _( "ZAURAK" ) } )

    else: # 3.7.7.0 or better.
        AstroBase.STARS.extend( [
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

        AstroBase.STARS_TO_HIP.update( {
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

        AstroBase.STAR_NAMES_TRANSLATIONS.update( {
            AstroBase.STARS[ 0 ]      :   _( "Acamar" ),
            AstroBase.STARS[ 1 ]      :   _( "Achernar" ),
            AstroBase.STARS[ 2 ]      :   _( "Acrux" ),
            AstroBase.STARS[ 3 ]      :   _( "Adara" ),
            AstroBase.STARS[ 4 ]      :   _( "Adhara" ),
            AstroBase.STARS[ 5 ]      :   _( "Agena" ),
            AstroBase.STARS[ 6 ]      :   _( "Albereo" ),
            AstroBase.STARS[ 7 ]      :   _( "Alcaid" ),
            AstroBase.STARS[ 8 ]      :   _( "Alcor" ),
            AstroBase.STARS[ 9 ]      :   _( "Alcyone" ),
            AstroBase.STARS[ 10 ]     :   _( "Aldebaran" ),
            AstroBase.STARS[ 11 ]     :   _( "Alderamin" ),
            AstroBase.STARS[ 12 ]     :   _( "Alfirk" ),
            AstroBase.STARS[ 13 ]     :   _( "Algenib" ),
            AstroBase.STARS[ 14 ]     :   _( "Algieba" ),
            AstroBase.STARS[ 15 ]     :   _( "Algol" ),
            AstroBase.STARS[ 16 ]     :   _( "Alhena" ),
            AstroBase.STARS[ 17 ]     :   _( "Alioth" ),
            AstroBase.STARS[ 18 ]     :   _( "Alkaid" ),
            AstroBase.STARS[ 19 ]     :   _( "Almach" ),
            AstroBase.STARS[ 20 ]     :   _( "Alnair" ),
            AstroBase.STARS[ 21 ]     :   _( "Alnilam" ),
            AstroBase.STARS[ 22 ]     :   _( "Alnitak" ),
            AstroBase.STARS[ 23 ]     :   _( "Alphard" ),
            AstroBase.STARS[ 24 ]     :   _( "Alphecca" ),
            AstroBase.STARS[ 25 ]     :   _( "Alpheratz" ),
            AstroBase.STARS[ 26 ]     :   _( "Alshain" ),
            AstroBase.STARS[ 27 ]     :   _( "Altair" ),
            AstroBase.STARS[ 28 ]     :   _( "Ankaa" ),
            AstroBase.STARS[ 29 ]     :   _( "Antares" ),
            AstroBase.STARS[ 30 ]     :   _( "Arcturus" ),
            AstroBase.STARS[ 31 ]     :   _( "Arkab Posterior" ),
            AstroBase.STARS[ 32 ]     :   _( "Arkab Prior" ),
            AstroBase.STARS[ 33 ]     :   _( "Arneb" ),
            AstroBase.STARS[ 34 ]     :   _( "Atlas" ),
            AstroBase.STARS[ 35 ]     :   _( "Atria" ),
            AstroBase.STARS[ 36 ]     :   _( "Avior" ),
            AstroBase.STARS[ 37 ]     :   _( "Bellatrix" ),
            AstroBase.STARS[ 38 ]     :   _( "Betelgeuse" ),
            AstroBase.STARS[ 39 ]     :   _( "Canopus" ),
            AstroBase.STARS[ 40 ]     :   _( "Capella" ),
            AstroBase.STARS[ 41 ]     :   _( "Caph" ),
            AstroBase.STARS[ 42 ]     :   _( "Castor" ),
            AstroBase.STARS[ 43 ]     :   _( "Cebalrai" ),
            AstroBase.STARS[ 44 ]     :   _( "Deneb" ),
            AstroBase.STARS[ 45 ]     :   _( "Denebola" ),
            AstroBase.STARS[ 46 ]     :   _( "Diphda" ),
            AstroBase.STARS[ 47 ]     :   _( "Dubhe" ),
            AstroBase.STARS[ 48 ]     :   _( "Electra" ),
            AstroBase.STARS[ 49 ]     :   _( "Elnath" ),
            AstroBase.STARS[ 50 ]     :   _( "Eltanin" ),
            AstroBase.STARS[ 51 ]     :   _( "Enif" ),
            AstroBase.STARS[ 52 ]     :   _( "Etamin" ),
            AstroBase.STARS[ 53 ]     :   _( "Fomalhaut" ),
            AstroBase.STARS[ 54 ]     :   _( "Formalhaut" ),
            AstroBase.STARS[ 55 ]     :   _( "Gacrux" ),
            AstroBase.STARS[ 56 ]     :   _( "Gienah" ),
            AstroBase.STARS[ 57 ]     :   _( "Gienah Corvi" ),
            AstroBase.STARS[ 58 ]     :   _( "Hadar" ),
            AstroBase.STARS[ 59 ]     :   _( "Hamal" ),
            AstroBase.STARS[ 60 ]     :   _( "Izar" ),
            AstroBase.STARS[ 61 ]     :   _( "Kaus Australis" ),
            AstroBase.STARS[ 62 ]     :   _( "Kochab" ),
            AstroBase.STARS[ 63 ]     :   _( "Maia" ),
            AstroBase.STARS[ 64 ]     :   _( "Markab" ),
            AstroBase.STARS[ 65 ]     :   _( "Megrez" ),
            AstroBase.STARS[ 66 ]     :   _( "Menkalinan" ),
            AstroBase.STARS[ 67 ]     :   _( "Menkar" ),
            AstroBase.STARS[ 68 ]     :   _( "Menkent" ),
            AstroBase.STARS[ 69 ]     :   _( "Merak" ),
            AstroBase.STARS[ 70 ]     :   _( "Merope" ),
            AstroBase.STARS[ 71 ]     :   _( "Miaplacidus" ),
            AstroBase.STARS[ 72 ]     :   _( "Mimosa" ),
            AstroBase.STARS[ 73 ]     :   _( "Minkar" ),
            AstroBase.STARS[ 74 ]     :   _( "Mintaka" ),
            AstroBase.STARS[ 75 ]     :   _( "Mirach" ),
            AstroBase.STARS[ 76 ]     :   _( "Mirfak" ),
            AstroBase.STARS[ 77 ]     :   _( "Mirzam" ),
            AstroBase.STARS[ 78 ]     :   _( "Mizar" ),
            AstroBase.STARS[ 79 ]     :   _( "Naos" ),
            AstroBase.STARS[ 80 ]     :   _( "Nihal" ),
            AstroBase.STARS[ 81 ]     :   _( "Nunki" ),
            AstroBase.STARS[ 82 ]     :   _( "Peacock" ),
            AstroBase.STARS[ 83 ]     :   _( "Phecda" ),
            AstroBase.STARS[ 84 ]     :   _( "Polaris" ),
            AstroBase.STARS[ 85 ]     :   _( "Pollux" ),
            AstroBase.STARS[ 86 ]     :   _( "Procyon" ),
            AstroBase.STARS[ 87 ]     :   _( "Rasalgethi" ),
            AstroBase.STARS[ 88 ]     :   _( "Rasalhague" ),
            AstroBase.STARS[ 89 ]     :   _( "Regulus" ),
            AstroBase.STARS[ 90 ]     :   _( "Rigel" ),
            AstroBase.STARS[ 91 ]     :   _( "Rigil Kentaurus" ),
            AstroBase.STARS[ 92 ]     :   _( "Rukbat" ),
            AstroBase.STARS[ 93 ]     :   _( "Sabik" ),
            AstroBase.STARS[ 94 ]     :   _( "Sadalmelik" ),
            AstroBase.STARS[ 95 ]     :   _( "Sadr" ),
            AstroBase.STARS[ 96 ]     :   _( "Saiph" ),
            AstroBase.STARS[ 97 ]     :   _( "Scheat" ),
            AstroBase.STARS[ 98 ]     :   _( "Schedar" ),
            AstroBase.STARS[ 99 ]     :   _( "Shaula" ),
            AstroBase.STARS[ 100 ]    :   _( "Sheliak" ),
            AstroBase.STARS[ 101 ]    :   _( "Sirius" ),
            AstroBase.STARS[ 102 ]    :   _( "Sirrah" ),
            AstroBase.STARS[ 103 ]    :   _( "Spica" ),
            AstroBase.STARS[ 104 ]    :   _( "Suhail" ),
            AstroBase.STARS[ 105 ]    :   _( "Sulafat" ),
            AstroBase.STARS[ 106 ]    :   _( "Tarazed" ),
            AstroBase.STARS[ 107 ]    :   _( "Taygeta" ),
            AstroBase.STARS[ 108 ]    :   _( "Thuban" ),
            AstroBase.STARS[ 109 ]    :   _( "Unukalhai" ),
            AstroBase.STARS[ 110 ]    :   _( "Vega" ),
            AstroBase.STARS[ 111 ]    :   _( "Vindemiatrix" ),
            AstroBase.STARS[ 112 ]    :   _( "Wezen" ),
            AstroBase.STARS[ 113 ]    :   _( "Zaurak" ),
            AstroBase.STARS[ 114 ]    :   _( "Zubenelgenubi" ) } )

        # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
        AstroBase.STAR_TAGS_TRANSLATIONS.update( {
            AstroBase.STARS[ 0 ]      :   _( "ACAMAR" ),
            AstroBase.STARS[ 1 ]      :   _( "ACHERNAR" ),
            AstroBase.STARS[ 2 ]      :   _( "ACRUX" ),
            AstroBase.STARS[ 3 ]      :   _( "ADARA" ),
            AstroBase.STARS[ 4 ]      :   _( "ADHARA" ),
            AstroBase.STARS[ 5 ]      :   _( "AGENA" ),
            AstroBase.STARS[ 6 ]      :   _( "ALBEREO" ),
            AstroBase.STARS[ 7 ]      :   _( "ALCAID" ),
            AstroBase.STARS[ 8 ]      :   _( "ALCOR" ),
            AstroBase.STARS[ 9 ]      :   _( "ALCYONE" ),
            AstroBase.STARS[ 10 ]     :   _( "ALDEBARAN" ),
            AstroBase.STARS[ 11 ]     :   _( "ALDERAMIN" ),
            AstroBase.STARS[ 12 ]     :   _( "ALFIRK" ),
            AstroBase.STARS[ 13 ]     :   _( "ALGENIB" ),
            AstroBase.STARS[ 14 ]     :   _( "ALGIEBA" ),
            AstroBase.STARS[ 15 ]     :   _( "ALGOL" ),
            AstroBase.STARS[ 16 ]     :   _( "ALHENA" ),
            AstroBase.STARS[ 17 ]     :   _( "ALIOTH" ),
            AstroBase.STARS[ 18 ]     :   _( "ALKAID" ),
            AstroBase.STARS[ 19 ]     :   _( "ALMACH" ),
            AstroBase.STARS[ 20 ]     :   _( "ALNAIR" ),
            AstroBase.STARS[ 21 ]     :   _( "ALNILAM" ),
            AstroBase.STARS[ 22 ]     :   _( "ALNITAK" ),
            AstroBase.STARS[ 23 ]     :   _( "ALPHARD" ),
            AstroBase.STARS[ 24 ]     :   _( "ALPHECCA" ),
            AstroBase.STARS[ 25 ]     :   _( "ALPHERATZ" ),
            AstroBase.STARS[ 26 ]     :   _( "ALSHAIN" ),
            AstroBase.STARS[ 27 ]     :   _( "ALTAIR" ),
            AstroBase.STARS[ 28 ]     :   _( "ANKAA" ),
            AstroBase.STARS[ 29 ]     :   _( "ANTARES" ),
            AstroBase.STARS[ 30 ]     :   _( "ARCTURUS" ),
            AstroBase.STARS[ 31 ]     :   _( "ARKAB POSTERIOR" ),
            AstroBase.STARS[ 32 ]     :   _( "ARKAB PRIOR" ),
            AstroBase.STARS[ 33 ]     :   _( "ARNEB" ),
            AstroBase.STARS[ 34 ]     :   _( "ATLAS" ),
            AstroBase.STARS[ 35 ]     :   _( "ATRIA" ),
            AstroBase.STARS[ 36 ]     :   _( "AVIOR" ),
            AstroBase.STARS[ 37 ]     :   _( "BELLATRIX" ),
            AstroBase.STARS[ 38 ]     :   _( "BETELGEUSE" ),
            AstroBase.STARS[ 39 ]     :   _( "CANOPUS" ),
            AstroBase.STARS[ 40 ]     :   _( "CAPELLA" ),
            AstroBase.STARS[ 41 ]     :   _( "CAPH" ),
            AstroBase.STARS[ 42 ]     :   _( "CASTOR" ),
            AstroBase.STARS[ 43 ]     :   _( "CEBALRAI" ),
            AstroBase.STARS[ 44 ]     :   _( "DENEB" ),
            AstroBase.STARS[ 45 ]     :   _( "DENEBOLA" ),
            AstroBase.STARS[ 46 ]     :   _( "DIPHDA" ),
            AstroBase.STARS[ 47 ]     :   _( "DUBHE" ),
            AstroBase.STARS[ 48 ]     :   _( "ELECTRA" ),
            AstroBase.STARS[ 49 ]     :   _( "ELNATH" ),
            AstroBase.STARS[ 50 ]     :   _( "ELTANIN" ),
            AstroBase.STARS[ 51 ]     :   _( "ENIF" ),
            AstroBase.STARS[ 52 ]     :   _( "ETAMIN" ),
            AstroBase.STARS[ 53 ]     :   _( "FOMALHAUT" ),
            AstroBase.STARS[ 54 ]     :   _( "FORMALHAUT" ),
            AstroBase.STARS[ 55 ]     :   _( "GACRUX" ),
            AstroBase.STARS[ 56 ]     :   _( "GIENAH" ),
            AstroBase.STARS[ 57 ]     :   _( "GIENAH CORVI" ),
            AstroBase.STARS[ 58 ]     :   _( "HADAR" ),
            AstroBase.STARS[ 59 ]     :   _( "HAMAL" ),
            AstroBase.STARS[ 60 ]     :   _( "IZAR" ),
            AstroBase.STARS[ 61 ]     :   _( "KAUS AUSTRALIS" ),
            AstroBase.STARS[ 62 ]     :   _( "KOCHAB" ),
            AstroBase.STARS[ 63 ]     :   _( "MAIA" ),
            AstroBase.STARS[ 64 ]     :   _( "MARKAB" ),
            AstroBase.STARS[ 65 ]     :   _( "MEGREZ" ),
            AstroBase.STARS[ 66 ]     :   _( "MENKALINAN" ),
            AstroBase.STARS[ 67 ]     :   _( "MENKAR" ),
            AstroBase.STARS[ 68 ]     :   _( "MENKENT" ),
            AstroBase.STARS[ 69 ]     :   _( "MERAK" ),
            AstroBase.STARS[ 70 ]     :   _( "MEROPE" ),
            AstroBase.STARS[ 71 ]     :   _( "MIAPLACIDUS" ),
            AstroBase.STARS[ 72 ]     :   _( "MIMOSA" ),
            AstroBase.STARS[ 73 ]     :   _( "MINKAR" ),
            AstroBase.STARS[ 74 ]     :   _( "MINTAKA" ),
            AstroBase.STARS[ 75 ]     :   _( "MIRACH" ),
            AstroBase.STARS[ 76 ]     :   _( "MIRFAK" ),
            AstroBase.STARS[ 77 ]     :   _( "MIRZAM" ),
            AstroBase.STARS[ 78 ]     :   _( "MIZAR" ),
            AstroBase.STARS[ 79 ]     :   _( "NAOS" ),
            AstroBase.STARS[ 80 ]     :   _( "NIHAL" ),
            AstroBase.STARS[ 81 ]     :   _( "NUNKI" ),
            AstroBase.STARS[ 82 ]     :   _( "PEACOCK" ),
            AstroBase.STARS[ 83 ]     :   _( "PHECDA" ),
            AstroBase.STARS[ 84 ]     :   _( "POLARIS" ),
            AstroBase.STARS[ 85 ]     :   _( "POLLUX" ),
            AstroBase.STARS[ 86 ]     :   _( "PROCYON" ),
            AstroBase.STARS[ 87 ]     :   _( "RASALGETHI" ),
            AstroBase.STARS[ 88 ]     :   _( "RASALHAGUE" ),
            AstroBase.STARS[ 89 ]     :   _( "REGULUS" ),
            AstroBase.STARS[ 90 ]     :   _( "RIGEL" ),
            AstroBase.STARS[ 91 ]     :   _( "RIGIL KENTAURUS" ),
            AstroBase.STARS[ 92 ]     :   _( "RUKBAT" ),
            AstroBase.STARS[ 93 ]     :   _( "SABIK" ),
            AstroBase.STARS[ 94 ]     :   _( "SADALMELIK" ),
            AstroBase.STARS[ 95 ]     :   _( "SADR" ),
            AstroBase.STARS[ 96 ]     :   _( "SAIPH" ),
            AstroBase.STARS[ 97 ]     :   _( "SCHEAT" ),
            AstroBase.STARS[ 98 ]     :   _( "SCHEDAR" ),
            AstroBase.STARS[ 99 ]     :   _( "SHAULA" ),
            AstroBase.STARS[ 100 ]    :   _( "SHELIAK" ),
            AstroBase.STARS[ 101 ]    :   _( "SIRIUS" ),
            AstroBase.STARS[ 102 ]    :   _( "SIRRAH" ),
            AstroBase.STARS[ 103 ]    :   _( "SPICA" ),
            AstroBase.STARS[ 104 ]    :   _( "SUHAIL" ),
            AstroBase.STARS[ 105 ]    :   _( "SULAFAT" ),
            AstroBase.STARS[ 106 ]    :   _( "TARAZED" ),
            AstroBase.STARS[ 107 ]    :   _( "TAYGETA" ),
            AstroBase.STARS[ 108 ]    :   _( "THUBAN" ),
            AstroBase.STARS[ 109 ]    :   _( "UNUKALHAI" ),
            AstroBase.STARS[ 110 ]    :   _( "VEGA" ),
            AstroBase.STARS[ 111 ]    :   _( "VINDEMIATRIX" ),
            AstroBase.STARS[ 112 ]    :   _( "WEZEN" ),
            AstroBase.STARS[ 113 ]    :   _( "ZAURAK" ),
            AstroBase.STARS[ 114 ]    :   _( "ZUBENELGENUBI" ) } )


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

    __PYEPHEM_SATELLITE_RISING_DATE = 0
    __PYEPHEM_SATELLITE_RISING_ANGLE = 1
    __PYEPHEM_SATELLITE_CULMINATION_DATE = 2
    __PYEPHEM_SATELLITE_CULMINATION_ANGLE = 3
    __PYEPHEM_SATELLITE_SETTING_DATE = 4
    __PYEPHEM_SATELLITE_SETTING_ANGLE = 5


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
        ephemNow = ephem.Date( utcNow )

        # observer = ephem.city( "London" ) # Any name will do; add in the correct lat/long/elev. 
        # observer.date = ephemNow
        # observer.lat = str( latitude )
        # observer.lon = str( longitude )
        # observer.elev = elevation
        observer = AstroPyEphem.__getObserver( ephemNow, latitude, longitude, elevation )

        # To find a visible satellite pass, need a modified observer.
        # observerVisiblePasses = ephem.city( "London" ) # Any name will do; add in the correct lat/long/elev.
        # observerVisiblePasses.date = ephemNow
        # observerVisiblePasses.lat = str( latitude )
        # observerVisiblePasses.lon = str( longitude )
        # observerVisiblePasses.elev = elevation
        observerVisiblePasses = AstroPyEphem.__getObserver( ephemNow, latitude, longitude, elevation )
        observerVisiblePasses.pressure = 0
        observerVisiblePasses.horizon = "-0:34"

        AstroPyEphem.__calculateMoon( ephemNow, observer, data )
        AstroPyEphem.__calculateSun( ephemNow, observer, data )
        AstroPyEphem.__calculatePlanets( observer, data, planets, magnitudeMaximum )
        AstroPyEphem.__calculateStars( observer, data, stars, magnitudeMaximum )
        AstroPyEphem.__calculateOrbitalElements( observer, data, AstroBase.BodyType.COMET, comets, cometData, magnitudeMaximum )
        AstroPyEphem.__calculateOrbitalElements( observer, data, AstroBase.BodyType.MINOR_PLANET, minorPlanets, minorPlanetData, magnitudeMaximum )
        AstroPyEphem.__calculateSatellites( ephemNow, observer, observerVisiblePasses, data, satellites, satelliteData, startHour, endHour )

        return data


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
        city = ephem.city( "London" ) # Use any city; makes no difference to obtain the magnitude.
        city.date = utcNow
        for key in orbitalElementData:
            body = ephem.readdb( orbitalElementData[ key ].getData() )
            body.compute( city )

            # Have found the data file may contain ***** in lieu of actual data!
            bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance )
            if not bad and body.mag >= AstroBase.MAGNITUDE_MINIMUM and body.mag <= magnitudeMaximum:
                results[ key ] = orbitalElementData[ key ]

        return results


    @staticmethod
    def getStatusMessage():
        minimalRequiredVersion = "3.7.6.0"
        installationCommand = "sudo apt-get install -y python3-ephem"
        message = None
        if not available:
            message = _( "PyEphem could not be found. Install using:\n\n" + installationCommand )

        elif LooseVersion( ephem.__version__ ) < LooseVersion( minimalRequiredVersion ):
            message = \
                _( "PyEphem must be version {0} or greater. Please upgrade:\n\n" + \
               installationCommand ).format( minimalRequiredVersion )

        return message


    @staticmethod
    def getVersion(): return ephem.__version__


    @staticmethod
    def __getObserver( ephemNow, latitude, longitude, elevation ):
        observer = ephem.city( "London" ) # Any name will do; add in the correct lat/long/elev. 
        observer.date = ephemNow
        observer.lat = str( latitude )
        observer.lon = str( longitude )
        observer.elev = elevation
        return observer


    @staticmethod
    def __calculateMoon( ephemNow, observer, data ):
        key = ( AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON )
        moon = ephem.Moon( observer )
        sun = ephem.Sun( observer )

        data[ key + ( AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( int( moon.phase ) ) # Needed for icon.

        phase = AstroBase.getLunarPhase( int( moon.phase ), ephem.next_full_moon( ephemNow ), ephem.next_new_moon( ephemNow ) ) # Need for notification.
        data[ key + ( AstroBase.DATA_TAG_PHASE, ) ] = phase

        brightLimb = AstroBase.getZenithAngleOfBrightLimb( ephemNow.datetime(), sun.ra, sun.dec, moon.ra, moon.dec, float( observer.lat ), float( observer.lon ) )
        data[ key + ( AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( brightLimb ) # Needed for icon.

        if not AstroPyEphem.__calculateCommon( data, observer, moon, AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON ):
            data[ key + ( AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = AstroBase.toDateTimeString( ephem.next_first_quarter_moon( ephemNow ).datetime() )
            data[ key + ( AstroBase.DATA_TAG_FULL, ) ] = AstroBase.toDateTimeString( ephem.next_full_moon( ephemNow ).datetime() )
            data[ key + ( AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = AstroBase.toDateTimeString( ephem.next_last_quarter_moon( ephemNow ).datetime() )
            data[ key + ( AstroBase.DATA_TAG_NEW, ) ] = AstroBase.toDateTimeString( ephem.next_new_moon( ephemNow ).datetime() )

            dateTime, eclipseType, latitude, longitude = eclipse.getEclipse( ephemNow.datetime(), True )
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTime
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseType
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude


    @staticmethod
    def __calculateSun( ephemNow, observer, data ):
        sun = ephem.Sun()
        sun.compute( observer )
        if not AstroPyEphem.__calculateCommon( data, observer, sun, AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN ):
            key = ( AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN )
            equinox = ephem.next_equinox( ephemNow )
            solstice = ephem.next_solstice( ephemNow )
            data[ key + ( AstroBase.DATA_TAG_EQUINOX, ) ] = AstroBase.toDateTimeString( equinox.datetime() )
            data[ key + ( AstroBase.DATA_TAG_SOLSTICE, ) ] = AstroBase.toDateTimeString( solstice.datetime() )

            dateTime, eclipseType, latitude, longitude = eclipse.getEclipse( ephemNow.datetime(), False )
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTime
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseType
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude


    @staticmethod
    def __calculatePlanets( observer, data, planets, magnitudeMaximum ):
        for planet in planets:
            body = getattr( ephem, planet.title() )()
            body.compute( observer )
            if body.mag <= magnitudeMaximum:
                AstroPyEphem.__calculateCommon( data, observer, body, AstroBase.BodyType.PLANET, planet )


    @staticmethod
    def __calculateStars( observer, data, stars, magnitudeMaximum ):
        for star in stars:
            if star in AstroBase.STARS: # Ensure that a star is present if/when switching between PyEphem and Skyfield.
                body = ephem.star( star.title() )
                body.compute( observer )
                if body.mag <= magnitudeMaximum:
                    AstroPyEphem.__calculateCommon( data, observer, body, AstroBase.BodyType.STAR, star )


    @staticmethod
    def __calculateOrbitalElements( observer, data, bodyType, orbitalElements, orbitalElementData, magnitudeMaximum ):
        for key in orbitalElements:
            if key in orbitalElementData:
                body = ephem.readdb( orbitalElementData[ key ].getData() )
                body.compute( observer )
                bad = \
                    math.isnan( body.earth_distance ) or \
                    math.isnan( body.phase ) or \
                    math.isnan( body.size ) or \
                    math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!

                if not bad and body.mag <= magnitudeMaximum:
                    AstroPyEphem.__calculateCommon( data, observer, body, bodyType, key )


    # Calculates common attributes such as rise/set date/time, azimuth/altitude.
    #
    # Returns True if the body is never up; false otherwise.
    @staticmethod
    def __calculateCommon( data, observer, body, bodyType, nameTag ):
        neverUp = False
        key = ( bodyType, nameTag )
        try:
            # Must compute az/alt BEFORE rise/set otherwise results will be incorrect.
            data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
            data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )
            data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = AstroBase.toDateTimeString( observer.next_rising( body ).datetime() )
            data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = AstroBase.toDateTimeString( observer.next_setting( body ).datetime() )

        except ephem.AlwaysUpError:
            body.compute( observer ) # Must recompute otherwise the azimuth/altitude are incorrectly calculated.
            data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
            data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )

        except ephem.NeverUpError:
            neverUp = True

        return neverUp


    @staticmethod
    def __calculateSatellites( ephemNow, observer, observerVisiblePasses, data, satellites, satelliteData, startHour, endHour ):
        finalDateTime = ephem.Date( ephemNow + ephem.hour * AstroBase.SATELLITE_SEARCH_DURATION_HOURS ).datetime().replace( tzinfo = datetime.timezone.utc )
        for satellite in satellites:
            if satellite in satelliteData:
                key = ( AstroBase.BodyType.SATELLITE, satellite )
                earthSatellite = ephem.readtle( satelliteData[ satellite ].getName(), satelliteData[ satellite ].getLine1(), satelliteData[ satellite ].getLine2() )
                startDateTime, endDateTime = AstroBase.getAdjustedDateTime(
                    ephemNow.datetime().replace( tzinfo = datetime.timezone.utc ), finalDateTime, startHour, endHour )

                AstroPyEphem.__calculateSatellite(
                    startDateTime, endDateTime, finalDateTime, startHour, endHour, observer, observerVisiblePasses, data, key, earthSatellite )


    @staticmethod
    def __calculateSatellite( startDateTime, endDateTime, finalDateTime, startHour, endHour, observer, observerVisiblePasses, data, key, earthSatellite ):

        # Typically to search for a visible satellite pass,
        # start from 'now' until 'now' plus search duration,
        # checking each pass as it is calculated for visibility.
        # However, when filtering passes through a start/end window,
        # searching is further bound within each star/end hour pair.
        while startDateTime is not None and startDateTime < endDateTime:
            observer.date = ephem.Date( startDateTime )
            earthSatellite.compute( observer )
            try:
                nextPass = AstroPyEphem.__nextSatellitePass( observer, earthSatellite )
                passIsValid = AstroPyEphem.__isSatellitePassValid( nextPass )
                if passIsValid:
                    passBeforeEndDateTime = nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ].datetime().replace( tzinfo = datetime.timezone.utc ) < endDateTime

                    passIsVisible = AstroPyEphem.__isSatellitePassVisible(
                        observerVisiblePasses, earthSatellite, nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_DATE ] )

                    if passBeforeEndDateTime and passIsVisible:
                        data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = \
                            AstroBase.toDateTimeString( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_DATE ].datetime() )

                        data[ key + ( AstroBase.DATA_TAG_RISE_AZIMUTH, ) ] = repr( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_ANGLE ] )

                        data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = \
                            AstroBase.toDateTimeString( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ].datetime() )

                        data[ key + ( AstroBase.DATA_TAG_SET_AZIMUTH, ) ] = repr( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_ANGLE ] )
                        break

                    # Look for the next pass starting shortly after current set.
                    startDateTime = ephem.Date(
                        nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ] + ephem.minute * 15 ).datetime().replace( tzinfo = datetime.timezone.utc )

                else:
                    # Bad pass data, so look shortly after the current time.
                    startDateTime = ephem.Date( ephem.Date( startDateTime ) + ephem.minute * 15 ).datetime().replace( tzinfo = datetime.timezone.utc )

                startDateTime, endDateTime = AstroBase.getAdjustedDateTime( startDateTime, finalDateTime, startHour, endHour )

            except ValueError:
                if earthSatellite.circumpolar: # Satellite never rises/sets, so can only show current position.
                    data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( earthSatellite.az )
                    data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( earthSatellite.alt )

                break


    # Due to a change between PyEphem 3.7.6.0 and 3.7.7.0, need to check for passes differently.
    #    https://rhodesmill.org/pyephem/CHANGELOG.html#version-3-7-7-0-2019-august-18
    #    https://github.com/brandon-rhodes/pyephem/issues/63#issuecomment-144263243
    @staticmethod
    def __nextSatellitePass( observer, satellite ):
        if LooseVersion( ephem.__version__ ) < LooseVersion( "3.7.7.0" ):
            nextPass = observer.next_pass( satellite )

        else:
            # Must set singlepass = False to avoid the new code in PyEphem (and so behave prior to this change).
            # It is possible a pass is too quick/low and an exception is thrown.
            # https://github.com/brandon-rhodes/pyephem/issues/164
            # https://github.com/brandon-rhodes/pyephem/pull/85/files
            nextPass = observer.next_pass( satellite, singlepass = False )

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
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_ANGLE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_ANGLE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_ANGLE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_DATE ] > satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ] > satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_DATE ]


    # Determine if a satellite pass is visible.
    #
    #    https://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
    #    https://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
    #    https://www.celestrak.com/columns/v03n01
    @staticmethod
    def __isSatellitePassVisible( observerVisiblePasses, satellite, passDateTime ):
        observerVisiblePasses.date = passDateTime

        satellite.compute( observerVisiblePasses )
        sun = ephem.Sun()
        sun.compute( observerVisiblePasses )

        return \
            satellite.eclipsed is False and \
            sun.alt > ephem.degrees( "-18" ) and \
            sun.alt < ephem.degrees( "-6" )