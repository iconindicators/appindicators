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


# Calculate astronomical information using PyEphem.


from ephem.cities import _city_data

import astrobase, ephem, locale, math, orbitalelement, twolineelement


class AstroPyephem( astrobase.AstroBase ):

    # Taken from ephem/stars.py
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
        "ACHERNAR"        : 7588,
        "ADARA"           : 33579,
        "AGENA"           : 68702,
        "ALBEREO"         : 95947,
        "ALCAID"          : 67301,
        "ALCOR"           : 65477,
        "ALCYONE"         : 17702,
        "ALDEBARAN"       : 21421,
        "ALDERAMIN"       : 105199,
        "ALFIRK"          : 106032,
        "ALGENIB"         : 1067,
        "ALGIEBA"         : 50583,
        "ALGOL"           : 14576,
        "ALHENA"          : 31681,
        "ALIOTH"          : 62956,
        "ALMACH"          : 9640,
        "ALNAIR"          : 109268,
        "ALNILAM"         : 26311,
        "ALNITAK"         : 26727,
        "ALPHARD"         : 46390,
        "ALPHECCA"        : 76267,
        "ALSHAIN"         : 98036,
        "ALTAIR"          : 97649,
        "ANTARES"         : 80763,
        "ARCTURUS"        : 69673,
        "ARKAB POSTERIOR" : 95294,
        "ARKAB PRIOR"     : 95241,
        "ARNEB"           : 25985,
        "ATLAS"           : 17847,
        "BELLATRIX"       : 25336,
        "BETELGEUSE"      : 27989,
        "CANOPUS"         : 30438,
        "CAPELLA"         : 24608,
        "CAPH"            : 746,
        "CASTOR"          : 36850,
        "CEBALRAI"        : 86742,
        "DENEB"           : 102098,
        "DENEBOLA"        : 57632,
        "DUBHE"           : 54061,
        "ELECTRA"         : 17499,
        "ELNATH"          : 25428,
        "ENIF"            : 107315,
        "ETAMIN"          : 87833,
        "FOMALHAUT"       : 113368,
        "GIENAH CORVI"    : 59803,
        "HAMAL"           : 9884,
        "IZAR"            : 72105,
        "KAUS AUSTRALIS"  : 90185,
        "KOCHAB"          : 72607,
        "MAIA"            : 17573,
        "MARKAB"          : 113963,
        "MEGREZ"          : 59774,
        "MENKALINAN"      : 28360,
        "MENKAR"          : 14135,
        "MERAK"           : 53910,
        "MEROPE"          : 17608,
        "MIMOSA"          : 62434,
        "MINKAR"          : 59316,
        "MINTAKA"         : 25930,
        "MIRACH"          : 5447,
        "MIRZAM"          : 30324,
        "MIZAR"           : 65378,
        "NAOS"            : 39429,
        "NIHAL"           : 25606,
        "NUNKI"           : 92855,
        "PEACOCK"         : 100751,
        "PHECDA"          : 58001,
        "POLARIS"         : 11767,
        "POLLUX"          : 37826,
        "PROCYON"         : 37279,
        "RASALGETHI"      : 84345,
        "RASALHAGUE"      : 86032,
        "REGULUS"         : 49669,
        "RIGEL"           : 24436,
        "RUKBAT"          : 95347,
        "SADALMELIK"      : 109074,
        "SADR"            : 100453,
        "SAIPH"           : 27366,
        "SCHEAT"          : 113881,
        "SCHEDAR"         : 3179,
        "SHAULA"          : 85927,
        "SHELIAK"         : 92420,
        "SIRIUS"          : 32349,
        "SIRRAH"          : 677,
        "SPICA"           : 65474,
        "SULAFAT"         : 93194,
        "TARAZED"         : 97278,
        "TAYGETA"         : 17531,
        "THUBAN"          : 68756,
        "UNUKALHAI"       : 77070,
        "VEGA"            : 91262,
        "VINDEMIATRIX"    : 63608,
        "WEZEN"           : 34444,
        "ZAURAK"          : 18543 } )

    astrobase.AstroBase.STAR_NAMES_TRANSLATIONS.update( {
        astrobase.AstroBase.STARS[ 0 ]  : _( "Achernar" ),
        astrobase.AstroBase.STARS[ 1 ]  : _( "Adara" ),
        astrobase.AstroBase.STARS[ 2 ]  : _( "Agena" ),
        astrobase.AstroBase.STARS[ 3 ]  : _( "Albereo" ),
        astrobase.AstroBase.STARS[ 4 ]  : _( "Alcaid" ),
        astrobase.AstroBase.STARS[ 5 ]  : _( "Alcor" ),
        astrobase.AstroBase.STARS[ 6 ]  : _( "Alcyone" ),
        astrobase.AstroBase.STARS[ 7 ]  : _( "Aldebaran" ),
        astrobase.AstroBase.STARS[ 8 ]  : _( "Alderamin" ),
        astrobase.AstroBase.STARS[ 9 ]  : _( "Alfirk" ),
        astrobase.AstroBase.STARS[ 10 ] : _( "Algenib" ),
        astrobase.AstroBase.STARS[ 11 ] : _( "Algieba" ),
        astrobase.AstroBase.STARS[ 12 ] : _( "Algol" ),
        astrobase.AstroBase.STARS[ 13 ] : _( "Alhena" ),
        astrobase.AstroBase.STARS[ 14 ] : _( "Alioth" ),
        astrobase.AstroBase.STARS[ 15 ] : _( "Almach" ),
        astrobase.AstroBase.STARS[ 16 ] : _( "Alnair" ),
        astrobase.AstroBase.STARS[ 17 ] : _( "Alnilam" ),
        astrobase.AstroBase.STARS[ 18 ] : _( "Alnitak" ),
        astrobase.AstroBase.STARS[ 19 ] : _( "Alphard" ),
        astrobase.AstroBase.STARS[ 20 ] : _( "Alphecca" ),
        astrobase.AstroBase.STARS[ 21 ] : _( "Alshain" ),
        astrobase.AstroBase.STARS[ 22 ] : _( "Altair" ),
        astrobase.AstroBase.STARS[ 23 ] : _( "Antares" ),
        astrobase.AstroBase.STARS[ 24 ] : _( "Arcturus" ),
        astrobase.AstroBase.STARS[ 25 ] : _( "Arkab Posterior" ),
        astrobase.AstroBase.STARS[ 26 ] : _( "Arkab Prior" ),
        astrobase.AstroBase.STARS[ 27 ] : _( "Arneb" ),
        astrobase.AstroBase.STARS[ 28 ] : _( "Atlas" ),
        astrobase.AstroBase.STARS[ 29 ] : _( "Bellatrix" ),
        astrobase.AstroBase.STARS[ 30 ] : _( "Betelgeuse" ),
        astrobase.AstroBase.STARS[ 31 ] : _( "Canopus" ),
        astrobase.AstroBase.STARS[ 32 ] : _( "Capella" ),
        astrobase.AstroBase.STARS[ 33 ] : _( "Caph" ),
        astrobase.AstroBase.STARS[ 34 ] : _( "Castor" ),
        astrobase.AstroBase.STARS[ 35 ] : _( "Cebalrai" ),
        astrobase.AstroBase.STARS[ 36 ] : _( "Deneb" ),
        astrobase.AstroBase.STARS[ 37 ] : _( "Denebola" ),
        astrobase.AstroBase.STARS[ 38 ] : _( "Dubhe" ),
        astrobase.AstroBase.STARS[ 39 ] : _( "Electra" ),
        astrobase.AstroBase.STARS[ 40 ] : _( "Elnath" ),
        astrobase.AstroBase.STARS[ 41 ] : _( "Enif" ),
        astrobase.AstroBase.STARS[ 42 ] : _( "Etamin" ),
        astrobase.AstroBase.STARS[ 43 ] : _( "Fomalhaut" ),
        astrobase.AstroBase.STARS[ 44 ] : _( "Gienah Corvi" ),
        astrobase.AstroBase.STARS[ 45 ] : _( "Hamal" ),
        astrobase.AstroBase.STARS[ 46 ] : _( "Izar" ),
        astrobase.AstroBase.STARS[ 47 ] : _( "Kaus Australis" ),
        astrobase.AstroBase.STARS[ 48 ] : _( "Kochab" ),
        astrobase.AstroBase.STARS[ 49 ] : _( "Maia" ),
        astrobase.AstroBase.STARS[ 50 ] : _( "Maastrobase.AstroBase.rkab" ),
        astrobase.AstroBase.STARS[ 51 ] : _( "Megrez" ),
        astrobase.AstroBase.STARS[ 52 ] : _( "Menkalinan" ),
        astrobase.AstroBase.STARS[ 53 ] : _( "Menkar" ),
        astrobase.AstroBase.STARS[ 54 ] : _( "Merak" ),
        astrobase.AstroBase.STARS[ 55 ] : _( "Merope" ),
        astrobase.AstroBase.STARS[ 56 ] : _( "Mimosa" ),
        astrobase.AstroBase.STARS[ 57 ] : _( "Minkar" ),
        astrobase.AstroBase.STARS[ 58 ] : _( "Mintaka" ),
        astrobase.AstroBase.STARS[ 59 ] : _( "Mirach" ),
        astrobase.AstroBase.STARS[ 60 ] : _( "Mirzam" ),
        astrobase.AstroBase.STARS[ 61 ] : _( "Mizar" ),
        astrobase.AstroBase.STARS[ 62 ] : _( "Naos" ),
        astrobase.AstroBase.STARS[ 63 ] : _( "Nihal" ),
        astrobase.AstroBase.STARS[ 64 ] : _( "Nunki" ),
        astrobase.AstroBase.STARS[ 65 ] : _( "Peacock" ),
        astrobase.AstroBase.STARS[ 66 ] : _( "Phecda" ),
        astrobase.AstroBase.STARS[ 67 ] : _( "Polaris" ),
        astrobase.AstroBase.STARS[ 68 ] : _( "Pollux" ),
        astrobase.AstroBase.STARS[ 69 ] : _( "Procyon" ),
        astrobase.AstroBase.STARS[ 70 ] : _( "Rasalgethi" ),
        astrobase.AstroBase.STARS[ 71 ] : _( "Rasalhague" ),
        astrobase.AstroBase.STARS[ 72 ] : _( "Regulus" ),
        astrobase.AstroBase.STARS[ 73 ] : _( "Rigel" ),
        astrobase.AstroBase.STARS[ 74 ] : _( "Rukbat" ),
        astrobase.AstroBase.STARS[ 75 ] : _( "Sadalmelik" ),
        astrobase.AstroBase.STARS[ 76 ] : _( "Sadr" ),
        astrobase.AstroBase.STARS[ 77 ] : _( "Saiph" ),
        astrobase.AstroBase.STARS[ 78 ] : _( "Scheat" ),
        astrobase.AstroBase.STARS[ 79 ] : _( "Schedar" ),
        astrobase.AstroBase.STARS[ 80 ] : _( "Shaula" ),
        astrobase.AstroBase.STARS[ 81 ] : _( "Sheliak" ),
        astrobase.AstroBase.STARS[ 82 ] : _( "Sirius" ),
        astrobase.AstroBase.STARS[ 83 ] : _( "Sirrah" ),
        astrobase.AstroBase.STARS[ 84 ] : _( "Spica" ),
        astrobase.AstroBase.STARS[ 85 ] : _( "Sulafat" ),
        astrobase.AstroBase.STARS[ 86 ] : _( "Tarazed" ),
        astrobase.AstroBase.STARS[ 87 ] : _( "Taygeta" ),
        astrobase.AstroBase.STARS[ 88 ] : _( "Thuban" ),
        astrobase.AstroBase.STARS[ 89 ] : _( "Unukalhai" ),
        astrobase.AstroBase.STARS[ 90 ] : _( "Vega" ),
        astrobase.AstroBase.STARS[ 91 ] : _( "Vindemiatrix" ),
        astrobase.AstroBase.STARS[ 92 ] : _( "Wezen" ),
        astrobase.AstroBase.STARS[ 93 ] : _( "Zaurak" ) } )

    # Corresponding tags which reflect each data tag made visible to the user in the Preferences.
    astrobase.AstroBase.STAR_TAGS_TRANSLATIONS.update( {
        astrobase.AstroBase.STARS[ 0 ]  : _( "ACHERNAR" ),
        astrobase.AstroBase.STARS[ 1 ]  : _( "ADARA" ),
        astrobase.AstroBase.STARS[ 2 ]  : _( "AGENA" ),
        astrobase.AstroBase.STARS[ 3 ]  : _( "ALBEREO" ),
        astrobase.AstroBase.STARS[ 4 ]  : _( "ALCAID" ),
        astrobase.AstroBase.STARS[ 5 ]  : _( "ALCOR" ),
        astrobase.AstroBase.STARS[ 6 ]  : _( "ALCYONE" ),
        astrobase.AstroBase.STARS[ 7 ]  : _( "ALDEBARAN" ),
        astrobase.AstroBase.STARS[ 8 ]  : _( "ALDERAMIN" ),
        astrobase.AstroBase.STARS[ 9 ]  : _( "ALFIRK" ),
        astrobase.AstroBase.STARS[ 10 ] : _( "ALGENIB" ),
        astrobase.AstroBase.STARS[ 11 ] : _( "ALGIEBA" ),
        astrobase.AstroBase.STARS[ 12 ] : _( "ALGOL" ),
        astrobase.AstroBase.STARS[ 13 ] : _( "ALHENA" ),
        astrobase.AstroBase.STARS[ 14 ] : _( "ALIOTH" ),
        astrobase.AstroBase.STARS[ 15 ] : _( "ALMACH" ),
        astrobase.AstroBase.STARS[ 16 ] : _( "ALNAIR" ),
        astrobase.AstroBase.STARS[ 17 ] : _( "ALNILAM" ),
        astrobase.AstroBase.STARS[ 18 ] : _( "ALNITAK" ),
        astrobase.AstroBase.STARS[ 19 ] : _( "ALPHARD" ),
        astrobase.AstroBase.STARS[ 20 ] : _( "ALPHECCA" ),
        astrobase.AstroBase.STARS[ 21 ] : _( "ALSHAIN" ),
        astrobase.AstroBase.STARS[ 22 ] : _( "ALTAIR" ),
        astrobase.AstroBase.STARS[ 23 ] : _( "ANTARES" ),
        astrobase.AstroBase.STARS[ 24 ] : _( "ARCTURUS" ),
        astrobase.AstroBase.STARS[ 25 ] : _( "ARKABPOSTERIOR" ),
        astrobase.AstroBase.STARS[ 26 ] : _( "ARKABPRIOR" ),
        astrobase.AstroBase.STARS[ 27 ] : _( "ARNEB" ),
        astrobase.AstroBase.STARS[ 28 ] : _( "ATLAS" ),
        astrobase.AstroBase.STARS[ 29 ] : _( "BELLATRIX" ),
        astrobase.AstroBase.STARS[ 30 ] : _( "BETELGEUSE" ),
        astrobase.AstroBase.STARS[ 31 ] : _( "CANOPUS" ),
        astrobase.AstroBase.STARS[ 32 ] : _( "CAPELLA" ),
        astrobase.AstroBase.STARS[ 33 ] : _( "CAPH" ),
        astrobase.AstroBase.STARS[ 34 ] : _( "CASTOR" ),
        astrobase.AstroBase.STARS[ 35 ] : _( "CEBALRAI" ),
        astrobase.AstroBase.STARS[ 36 ] : _( "DENEB" ),
        astrobase.AstroBase.STARS[ 37 ] : _( "DENEBOLA" ),
        astrobase.AstroBase.STARS[ 38 ] : _( "DUBHE" ),
        astrobase.AstroBase.STARS[ 39 ] : _( "ELECTRA" ),
        astrobase.AstroBase.STARS[ 40 ] : _( "ELNATH" ),
        astrobase.AstroBase.STARS[ 41 ] : _( "ENIF" ),
        astrobase.AstroBase.STARS[ 42 ] : _( "ETAMIN" ),
        astrobase.AstroBase.STARS[ 43 ] : _( "FOMALHAUT" ),
        astrobase.AstroBase.STARS[ 44 ] : _( "GIENAHCORVI" ),
        astrobase.AstroBase.STARS[ 45 ] : _( "HAMAL" ),
        astrobase.AstroBase.STARS[ 46 ] : _( "IZAR" ),
        astrobase.AstroBase.STARS[ 47 ] : _( "KAUSAUSTRALIS" ),
        astrobase.AstroBase.STARS[ 48 ] : _( "KOCHAB" ),
        astrobase.AstroBase.STARS[ 49 ] : _( "MAIA" ),
        astrobase.AstroBase.STARS[ 50 ] : _( "MARKAB" ),
        astrobase.AstroBase.STARS[ 51 ] : _( "MEGREZ" ),
        astrobase.AstroBase.STARS[ 52 ] : _( "MENKALINAN" ),
        astrobase.AstroBase.STARS[ 53 ] : _( "MENKAR" ),
        astrobase.AstroBase.STARS[ 54 ] : _( "MERAK" ),
        astrobase.AstroBase.STARS[ 55 ] : _( "MEROPE" ),
        astrobase.AstroBase.STARS[ 56 ] : _( "MIMOSA" ),
        astrobase.AstroBase.STARS[ 57 ] : _( "MINKAR" ),
        astrobase.AstroBase.STARS[ 58 ] : _( "MINTAKA" ),
        astrobase.AstroBase.STARS[ 59 ] : _( "MIRACH" ),
        astrobase.AstroBase.STARS[ 60 ] : _( "MIRZAM" ),
        astrobase.AstroBase.STARS[ 61 ] : _( "MIZAR" ),
        astrobase.AstroBase.STARS[ 62 ] : _( "NAOS" ),
        astrobase.AstroBase.STARS[ 63 ] : _( "NIHAL" ),
        astrobase.AstroBase.STARS[ 64 ] : _( "NUNKI" ),
        astrobase.AstroBase.STARS[ 65 ] : _( "PEACOCK" ),
        astrobase.AstroBase.STARS[ 66 ] : _( "PHECDA" ),
        astrobase.AstroBase.STARS[ 67 ] : _( "POLARIS" ),
        astrobase.AstroBase.STARS[ 68 ] : _( "POLLUX" ),
        astrobase.AstroBase.STARS[ 69 ] : _( "PROCYON" ),
        astrobase.AstroBase.STARS[ 70 ] : _( "RASALGETHI" ),
        astrobase.AstroBase.STARS[ 71 ] : _( "RASALHAGUE" ),
        astrobase.AstroBase.STARS[ 72 ] : _( "REGULUS" ),
        astrobase.AstroBase.STARS[ 73 ] : _( "RIGEL" ),
        astrobase.AstroBase.STARS[ 74 ] : _( "RUKBAT" ),
        astrobase.AstroBase.STARS[ 75 ] : _( "SADALMELIK" ),
        astrobase.AstroBase.STARS[ 76 ] : _( "SADR" ),
        astrobase.AstroBase.STARS[ 77 ] : _( "SAIPH" ),
        astrobase.AstroBase.STARS[ 78 ] : _( "SCHEAT" ),
        astrobase.AstroBase.STARS[ 79 ] : _( "SCHEDAR" ),
        astrobase.AstroBase.STARS[ 80 ] : _( "SHAULA" ),
        astrobase.AstroBase.STARS[ 81 ] : _( "SHELIAK" ),
        astrobase.AstroBase.STARS[ 82 ] : _( "SIRIUS" ),
        astrobase.AstroBase.STARS[ 83 ] : _( "SIRRAH" ),
        astrobase.AstroBase.STARS[ 84 ] : _( "SPICA" ),
        astrobase.AstroBase.STARS[ 85 ] : _( "SULAFAT" ),
        astrobase.AstroBase.STARS[ 86 ] : _( "TARAZED" ),
        astrobase.AstroBase.STARS[ 87 ] : _( "TAYGETA" ),
        astrobase.AstroBase.STARS[ 88 ] : _( "THUBAN" ),
        astrobase.AstroBase.STARS[ 89 ] : _( "UNUKALHAI" ),
        astrobase.AstroBase.STARS[ 90 ] : _( "VEGA" ),
        astrobase.AstroBase.STARS[ 91 ] : _( "VINDEMIATRIX" ),
        astrobase.AstroBase.STARS[ 92 ] : _( "WEZEN" ),
        astrobase.AstroBase.STARS[ 93 ] : _( "ZAURAK" ) } )


    # Internally used for city.
    __DATA_TAG_ELEVATION = "ELEVATION"
    __DATA_TAG_LATITUDE = "LATITUDE"
    __DATA_TAG_LONGITUDE = "LONGITUDE"


    # Internally used for city.
    __NAME_TAG_CITY = "CITY"


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

        # Used internally; removed before passing back to the caller.
        data[ ( None, AstroPyephem.__NAME_TAG_CITY, AstroPyephem.__DATA_TAG_LATITUDE ) ] = str( latitude )
        data[ ( None, AstroPyephem.__NAME_TAG_CITY, AstroPyephem.__DATA_TAG_LONGITUDE ) ] = str( longitude )
        data[ ( None, AstroPyephem.__NAME_TAG_CITY, AstroPyephem.__DATA_TAG_ELEVATION ) ] = str( elevation )

        ephemNow = ephem.Date( utcNow )

        AstroPyephem.__calculateMoon( ephemNow, data )
        AstroPyephem.__calculateSun( ephemNow, data )
        AstroPyephem.__calculatePlanets( ephemNow, data, planets, magnitudeMaximum )
        AstroPyephem.__calculateStars( ephemNow, data, stars, magnitudeMaximum )
        AstroPyephem.__calculateCometsOrMinorPlanets( ephemNow, data, astrobase.AstroBase.BodyType.COMET, comets, cometData, magnitudeMaximum )
        AstroPyephem.__calculateCometsOrMinorPlanets( ephemNow, data, astrobase.AstroBase.BodyType.MINOR_PLANET, minorPlanets, minorPlanetData, magnitudeMaximum )
        AstroPyephem.__calculateSatellites( ephemNow, data, satellites, satelliteData )

        del data[ ( None, AstroPyephem.__NAME_TAG_CITY, AstroPyephem.__DATA_TAG_LATITUDE ) ]
        del data[ ( None, AstroPyephem.__NAME_TAG_CITY, AstroPyephem.__DATA_TAG_LONGITUDE ) ]
        del data[ ( None, AstroPyephem.__NAME_TAG_CITY, AstroPyephem.__DATA_TAG_ELEVATION ) ]

        return data


    @staticmethod
    def getCities(): return sorted( _city_data.keys(), key = locale.strxfrm )


    @staticmethod
    def getLatitudeLongitudeElevation( city ): return float( _city_data.get( city )[ 0 ] ), \
                                                      float( _city_data.get( city )[ 1 ] ), \
                                                      _city_data.get( city )[ 2 ]


    @staticmethod
    def getOrbitalElementsLessThanMagnitude( orbitalElementData, maximumMagnitude ):
        results = { }
        for key in orbitalElementData:
            body = ephem.readdb( orbitalElementData[ key ].getData() )
            body.compute( ephem.city( "London" ) ) # Use any city; makes no difference to obtain the magnitude.
            bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
            if not bad and body.mag >= astrobase.AstroBase.MAGNITUDE_MINIMUM and body.mag <= maximumMagnitude:
                results[ key ] = orbitalElementData[ key ]

        return results


    @staticmethod
    def getCredit(): return _( "Calculations courtesy of PyEphem/XEphem. http://rhodesmill.org/pyephem" )


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
        moon.compute( AstroPyephem.__getCity( data, ephemNow ) )
        data[ key + ( astrobase.AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( int( moon.phase ) ) # Needed for icon.
        data[ key + ( astrobase.AstroBase.DATA_TAG_PHASE, ) ] = astrobase.AstroBase.getLunarPhase( int( moon.phase ), ephem.next_full_moon( ephemNow ), ephem.next_new_moon( ephemNow ) ) # Need for notification.

        city = AstroPyephem.__getCity( data, ephemNow )
        sun = ephem.Sun( city )
        moon = ephem.Moon()
        moon.compute( city )
        brightLimb = astrobase.AstroBase.getZenithAngleOfBrightLimb( ephemNow.datetime(), sun.ra, sun.dec, moon.ra, moon.dec, float( city.lat ), float( city.lon ) )
        data[ key + ( astrobase.AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( brightLimb ) # Needed for icon.

        if not AstroPyephem.__calculateCommon( ephemNow, data, ephem.Moon(), astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON ):
            data[ key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_first_quarter_moon( ephemNow ).datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_full_moon( ephemNow ).datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_last_quarter_moon( ephemNow ).datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ] = astrobase.AstroBase.toDateTimeString( ephem.next_new_moon( ephemNow ).datetime() )
            astrobase.AstroBase.getEclipse( ephemNow.datetime(), data, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )


    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    # http://www.ga.gov.au/geodesy/astro/sunrise.jsp
    # http://www.geoastro.de/elevaz/index.htm
    # http://www.geoastro.de/SME/index.htm
    # http://www.geoastro.de/altazsunmoon/index.htm
    # http://futureboy.us/fsp/sun.fsp
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    @staticmethod
    def __calculateSun( ephemNow, data ):
        if not AstroPyephem.__calculateCommon( ephemNow, data, ephem.Sun(), astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN ):
            astrobase.AstroBase.getEclipse( ephemNow.datetime(), data, astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )

            equinox = ephem.next_equinox( ephemNow )
            solstice = ephem.next_solstice( ephemNow )
            key = ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )
            data[ key + ( astrobase.AstroBase.DATA_TAG_EQUINOX, ) ] = astrobase.AstroBase.toDateTimeString( equinox.datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_SOLSTICE, ) ] = astrobase.AstroBase.toDateTimeString( solstice.datetime() )


    # http://www.geoastro.de/planets/index.html
    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    @staticmethod
    def __calculatePlanets( ephemNow, data, planets, magnitudeMaximum ):
        for planet in planets:
            planetObject = getattr( ephem, planet.title() )()
            planetObject.compute( AstroPyephem.__getCity( data, ephemNow ) )
            if planetObject.mag <= magnitudeMaximum:
                AstroPyephem.__calculateCommon( ephemNow, data, planetObject, astrobase.AstroBase.BodyType.PLANET, planet )


    # http://aa.usno.navy.mil/data/docs/mrst.php
    @staticmethod
    def __calculateStars( ephemNow, data, stars, magnitudeMaximum ):
        for star in stars:
            if star in astrobase.AstroBase.STARS: # Ensure that a star is present if/when switching between PyEphem and Skyfield.
                starObject = ephem.star( star.title() )
                starObject.compute( AstroPyephem.__getCity( data, ephemNow ) )
                if starObject.mag <= magnitudeMaximum:
                    AstroPyephem.__calculateCommon( ephemNow, data, starObject, astrobase.AstroBase.BodyType.STAR, star )


    # Compute data for comets or minor planets.
    @staticmethod
    def __calculateCometsOrMinorPlanets( ephemNow, data, bodyType, cometsOrMinorPlanets, cometOrMinorPlanetData, magnitudeMaximum ):
        for key in cometsOrMinorPlanets:
            if key in cometOrMinorPlanetData:
                body = ephem.readdb( cometOrMinorPlanetData[ key ].getData() )
                body.compute( AstroPyephem.__getCity( data, ephemNow ) )
                bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
                if not bad and body.mag <= magnitudeMaximum:
                    AstroPyephem.__calculateCommon( ephemNow, data, body, bodyType, key )


    # Calculates common attributes such as rise/set date/time, azimuth/altitude.
    #
    # Returns True if the body is never up; false otherwise.
    @staticmethod
    def __calculateCommon( ephemNow, data, body, bodyType, nameTag ):
        neverUp = False
        key = ( bodyType, nameTag )
        try:
            city = AstroPyephem.__getCity( data, ephemNow )
            rising = city.next_rising( body )
            setting = city.next_setting( body )
            data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( rising.datetime() )
            data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( setting.datetime() )

            body.compute( AstroPyephem.__getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )

        except ephem.AlwaysUpError:
            body.compute( AstroPyephem.__getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )

        except ephem.NeverUpError:
            neverUp = True

        return neverUp

#TODO Remove if not needed.
    def __calculateCommonORIGINAL( ephemNow, data, body, bodyType, nameTag ):
        neverUp = False
        key = ( bodyType, nameTag )
        try:
            city = AstroPyephem.__getCity( data, ephemNow )
            rising = city.next_rising( body )
            setting = city.next_setting( body )

            if rising > setting: # Above the horizon.
                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( setting.datetime() )
                body.compute( AstroPyephem.__getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
                data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
                data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )

            else: # Below the horizon.
                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( rising.datetime() )

        except ephem.AlwaysUpError:
            body.compute( AstroPyephem.__getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )

        except ephem.NeverUpError:
            neverUp = True

        return neverUp


    # Use TLE data collated by Dr T S Kelso
    # http://celestrak.com/NORAD/elements
    #
    # Other sources/background:
    #   http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
    #   http://spotthestation.nasa.gov/sightings
    #   http://www.n2yo.com
    #   http://www.heavens-above.com
    #   http://in-the-sky.org
    @staticmethod
    def __calculateSatellites( ephemNow, data, satellites, satelliteData ):
        for key in satellites:
            if key in satelliteData:
                tle = satelliteData[ key ]
                key = ( astrobase.AstroBase.BodyType.SATELLITE, key )
                currentDateTime = ephemNow
                endDateTime = ephem.Date( ephemNow + ephem.hour * 36 ) # Stop looking for passes 36 hours from now.
                while currentDateTime < endDateTime:
                    city = AstroPyephem.__getCity( data, currentDateTime )
                    satellite = ephem.readtle( tle.getName(), tle.getLine1(), tle.getLine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
                    satellite.compute( city )
                    try:
                        nextPass = AstroPyephem.__calculateNextPass( city, satellite )
                        if AstroPyephem.__isSatellitePassIsValid( nextPass ) and AstroPyephem.__isSatellitePassVisible( data, nextPass[ 2 ], satellite ):
                            if nextPass[ 0 ] > nextPass[ 4 ]: # The rise time is after set time, so the satellite is currently passing.
                                setTime = nextPass[ 4 ]
                                nextPass = AstroPyephem.__calculateSatellitePassForRisingPriorToNow( currentDateTime, data, tle )
                                if nextPass is None:
                                    currentDateTime = ephem.Date( setTime + ephem.minute * 60 ) # Could not determine the rise, so look for the next pass.
                                    continue

                            # Satellite is yet to rise or is in transit...
                            if nextPass[ 0 ] < ( ephem.Date( ephemNow + ephem.minute * 5 ) ): # Satellite is about to rise or in transit, so show all information.
                                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( nextPass[ 0 ].datetime() )
                                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH, ) ] = repr( nextPass[ 1 ] )
                                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( nextPass[ 4 ].datetime() )
                                data[ key + ( astrobase.AstroBase.DATA_TAG_SET_AZIMUTH, ) ] = repr( nextPass[ 5 ] )

                            else: # Satellite will rise later, so only show rise time.
                                data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = astrobase.AstroBase.toDateTimeString( nextPass[ 0 ].datetime() )

                            break

                        else:
                            currentDateTime = ephem.Date( currentDateTime + ephem.minute * 60 ) # Look for the next pass.

                    except ValueError:
                        if satellite.circumpolar: # Satellite never rises/sets, so can only show current position.
                            data[ key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( satellite.az )
                            data[ key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( satellite.alt )

                        break


    @staticmethod
    def __calculateSatellitePassForRisingPriorToNow( ephemNow, data, satelliteTLE ):
        currentDateTime = ephemNow
        endDateTime = ephem.Date( ephemNow - ephem.hour ) # Only look back an hour for the rise time.
        nextPass = None
        while currentDateTime > endDateTime:
            city = AstroPyephem.__getCity( data, currentDateTime )
            satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getLine1(), satelliteTLE.getLine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
            satellite.compute( city )
            try:
                nextPass = AstroPyephem.__calculateNextPass( city, satellite )
                if AstroPyephem.__isSatellitePassIsValid( nextPass ):
                    if nextPass[ 0 ] < nextPass[ 4 ]:
                        break # Found the rise time!

                    currentDateTime = ephem.Date( currentDateTime - ephem.minute )

                else:
                    nextPass = None
                    break # Unlikely to happen but better to be safe and check!

            except:
                nextPass = None
                break # This should never happen as the satellite has a rise and set (is not polar nor never up).

        return nextPass


    # Due to a change between PyEphem 3.7.6.0 and 3.7.7.0, need to check for passes differently.
    #    https://rhodesmill.org/pyephem/CHANGELOG.html#version-3-7-7-0-2019-august-18
    #    https://github.com/brandon-rhodes/pyephem/issues/63#issuecomment-144263243
    @staticmethod
    def __calculateNextPass( city, satellite ):
        version = int( ephem.__version__.split( '.' )[ 2 ] )
        if version <= 6:
            nextPass = city.next_pass( satellite )

        else:
            nextPass = city.next_pass( satellite, singlepass = False )

        return nextPass


    # Guard against bad TLE data causing spurious results.
    @staticmethod
    def __isSatellitePassIsValid( satellitePass ):
        return satellitePass and \
               len( satellitePass ) == 6 and \
                satellitePass[ 0 ] and \
                satellitePass[ 1 ] and \
                satellitePass[ 2 ] and \
                satellitePass[ 3 ] and \
                satellitePass[ 4 ] and \
                satellitePass[ 5 ]


    # Determine if a satellite pass is visible.
    #
    #    http://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
    #    http://www.celestrak.com/columns/v03n01
    #    http://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
    @staticmethod
    def __isSatellitePassVisible( data, passDateTime, satellite ):
        city = AstroPyephem.__getCity( data, passDateTime )
        city.pressure = 0
        city.horizon = "-0:34"

        satellite.compute( city )
        sun = ephem.Sun()
        sun.compute( city )

        return satellite.eclipsed is False and \
               sun.alt > ephem.degrees( "-18" ) and \
               sun.alt < ephem.degrees( "-6" )


    @staticmethod
    def __getCity( data, date ):
        city = ephem.city( "London" ) # Put in a city name known to exist in PyEphem then doctor to the correct lat/long/elev.
        city.date = date
        city.lat = data[ ( None, AstroPyephem.__NAME_TAG_CITY, AstroPyephem.__DATA_TAG_LATITUDE ) ]
        city.lon = data[ ( None, AstroPyephem.__NAME_TAG_CITY, AstroPyephem.__DATA_TAG_LONGITUDE ) ]
        city.elev = float( data[ ( None, AstroPyephem.__NAME_TAG_CITY, AstroPyephem.__DATA_TAG_ELEVATION ) ] )

        return city