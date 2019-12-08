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


#TODO Better description.
# Calculate astronomical information using PyEphem.


#TODO Can this be an enum as per the PPA class?
class EngineType: PyEphem, Skyfield = range( 2 )


#TODO Can this be an enum as per the PPA class?
class BodyType: Comet, MinorPlanet, Moon, Planet, Satellite, Star, Sun = range( 7 )


#TODO Need a comment.
DATA_ALTITUDE = "ALTITUDE"
DATA_AZIMUTH = "AZIMUTH"
DATA_BRIGHT_LIMB = "BRIGHT LIMB" # Used for creating an icon; not intended for display to the user.
DATA_ECLIPSE_DATE_TIME = "ECLIPSE DATE TIME"
DATA_ECLIPSE_LATITUDE = "ECLIPSE LATITUDE"
DATA_ECLIPSE_LONGITUDE = "ECLIPSE LONGITUDE"
DATA_ECLIPSE_TYPE = "ECLIPSE TYPE"
DATA_ELEVATION = "ELEVATION" # Internally used for city.
DATA_EQUINOX = "EQUINOX"
DATA_FIRST_QUARTER = "FIRST QUARTER"
DATA_FULL = "FULL"
DATA_ILLUMINATION = "ILLUMINATION" # Used for creating an icon; not intended for display to the user.
DATA_LATITUDE = "LATITUDE" # Internally used for city.
DATA_LONGITUDE = "LONGITUDE" # Internally used for city.
DATA_NEW = "NEW"
DATA_PHASE = "PHASE"
DATA_RISE_AZIMUTH = "RISE AZIMUTH"
DATA_RISE_DATE_TIME = "RISE DATE TIME"
DATA_SET_AZIMUTH = "SET AZIMUTH"
DATA_SET_DATE_TIME = "SET DATE TIME"
DATA_SOLSTICE = "SOLSTICE"
DATA_THIRD_QUARTER = "THIRD QUARTER"

DATA_INTERNAL = [
    DATA_BRIGHT_LIMB,
    DATA_ILLUMINATION ]

DATA_COMET = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME ]

DATA_MINOR_PLANET = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME ]

DATA_MOON = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_ECLIPSE_DATE_TIME,
    DATA_ECLIPSE_LATITUDE,
    DATA_ECLIPSE_LONGITUDE,
    DATA_ECLIPSE_TYPE,
    DATA_FIRST_QUARTER,
    DATA_FULL,
    DATA_NEW,
    DATA_PHASE,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME,
    DATA_THIRD_QUARTER ]

DATA_PLANET = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME ]

DATA_SATELLITE = [
    DATA_RISE_AZIMUTH,
    DATA_RISE_DATE_TIME,
    DATA_SET_AZIMUTH,
    DATA_SET_DATE_TIME ]

DATA_STAR = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME ]

DATA_SUN = [
    DATA_ALTITUDE,
    DATA_AZIMUTH,
    DATA_ECLIPSE_DATE_TIME,
    DATA_ECLIPSE_LATITUDE,
    DATA_ECLIPSE_LONGITUDE,
    DATA_ECLIPSE_TYPE,
    DATA_EQUINOX,
    DATA_RISE_DATE_TIME,
    DATA_SET_DATE_TIME,
    DATA_SOLSTICE ]


#TODO Need a description
NAME_TAG_CITY = "CITY"
NAME_TAG_MOON = "MOON"
NAME_TAG_SUN = "SUN"


#TODO Need a description
PLANET_MERCURY = "MERCURY"
PLANET_VENUS = "VENUS"
PLANET_MARS = "MARS"
PLANET_JUPITER = "JUPITER"
PLANET_SATURN = "SATURN"
PLANET_URANUS = "URANUS"
PLANET_NEPTUNE = "NEPTUNE"
PLANET_PLUTO = "PLUTO"

PLANETS = [ PLANET_MERCURY, PLANET_VENUS, PLANET_MARS, PLANET_JUPITER, PLANET_SATURN, PLANET_URANUS, PLANET_NEPTUNE, PLANET_PLUTO ]



#TODO Want something like this...
# 
# If engineType == EngineType.PyEphem:
#     STARS = STARS_PYEPHEM
# 
# Else:
#     STARS = STARS_SKYFIELD
#
# May need to instead use a function; not sure if we can have code here.


# Sourced from ephem/stars.py
# Duplications removed and official names used.
__STARS_PYEPHEM = [
    "ACHERNAR",
    "ADHARA",
    "ALBIREO",
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
    "ALPHERATZ", # SIRRAH.
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
    "ELTANIN",
    "FOMALHAUT", 
    "GIENAH CORVI", 
    "HADAR", #AGENA.
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
    "SPICA", 
    "SULAFAT", 
    "TARAZED", 
    "TAYGETA", 
    "THUBAN", 
    "UNUKALHAI", 
    "VEGA",
    "VINDEMIATRIX", 
    "WEZEN", 
    "ZAURAK" ]


# Sourced from skyfield/named_stars.py
# Duplications removed and official names used.
__STARS_SKYFIELD = [
    "ACHERNAR",
    "ACRUX",
    "ADHARA",
    "ALBIREO",
    "ALCOR",
    "ALDEBARAN",
    "ALDERAMIN",
    "ALGENIB",
    "ALGIEBA",
    "ALGOL",
    "ALHENA",
    "ALIOTH",
    "ALKAID", # BENETNASH.
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
    "ASPIDISKE",
    "ATRIA",
    "AVIOR",
    "BECRUX",
    "BELLATRIX",
    "BETELGEUSE",
    "CANOPUS",
    "CAPELLA",
    "CAPH",
    "CASTOR",
    "DENEB" # ARIDED, ARIDIF.
    "DENEB KAITOS",
    "DENEBOLA",
    "DIPHDA",
    "DSCHUBBA",
    "DUBHE",
    "DURRE MENTHOR",
    "ELNATH",
    "ENIF",
    "EPSILON CENTAURI", # BIRDUN.
    "ETAMIN",
    "FOMALHAUT",
    "FORAMEN",
    "GACRUX",
    "GEMMA",
    "GIENAH",
    "GIRTAB",
    "GRUID",
    "HADAR", # AGENA
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
    "MIMOSA", # BECRUX
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
    "RIGEL",
    "RIGEL KENT",
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
    "WEZEN" ]


#TODO From skyfield...many stars here do not appear in the Pyephem list.
#So what to do with those stars?  Can't use them whilst we have Pyephem as the backend.
#If/when we move to skyfield, then modify the list to handle the Skyfield stars.
#But this will prevent (if need be) from switching to Pyephem for testing...think about this. 
# Maybe have a list of stars that are common to both Pyephem and Skyfield and either each backend 
# appends to that list of stars?  Or the common list of stars has the pyephem or skyfield specific stars
# appended by this base class...just not sure how to do that at run time (that is, how do we know
# if we are running a pyephem or skyfield?  Need a flag I suppose).
#
#This list was seeded from
#https://en.wikipedia.org/wiki/List_of_stars_in_the_Hipparcos_Catalogue
named_star_dict= {
 'Achernar': 7588,
 'Acrux': 60718,
 'Adhara': 33579,
 'Agena': 68702,
 'Albireo': 95947,
 'Alcor': 65477,
 'Aldebaran': 21421,
 'Alderamin': 105199,
 'Algenib': 15863,
 'Algieba': 50583,
 'Algol': 14576,
 'Alhena': 31681,
 'Alioth': 62956,
 'Alkaid': 67301,
 'Almach': 9640,
 'Alnair': 109268,
 'Alnilam': 26311,
 'Alnitak': 26727,
 'Alphard': 46390,
 'Alphecca': 76267,
 'Alpheratz': 677,
 'Altair': 97649,
 'Aludra': 35904,
 'Ankaa': 2081,
 'Antares': 80763,
 'Arcturus': 69673,
 'Arided': 102098,
 'Aridif': 102098,
 'Aspidiske': 45556,
 'Atria': 82273,
 'Avior': 41037,
 'Becrux': 62434,
 'Bellatrix': 25336,
 'Benetnash': 67301,
 'Betelgeuse': 27989,
 'Birdun': 66657,
 'Canopus': 30438,
 'Capella': 24608,
 'Caph': 746,
 'Castor': 36850,
 'Deneb': 102098,
 'Deneb Kaitos': 3419,
 'Denebola': 57632,
 'Diphda': 3419,
 'Dschubba': 78401,
 'Dubhe': 54061,
 'Durre Menthor': 8102,
 'Elnath': 25428,
 'Enif': 107315,
 'Etamin': 87833,
 'Fomalhaut': 113368,
 'Foramen': 93308,
 'Gacrux': 61084,
 'Gemma': 76267,
 'Gienah': 102488,
 'Girtab': 86228,
 'Gruid': 112122,
 'Hadar': 68702,
 'Hamal': 9884,
 "Herschel's Garnet Star": 107259,
 'Izar': 72105,
 'Kaus Australis': 90185,
 'Kochab': 72607,
 'Koo She': 42913,
 'Marchab': 113963,
 'Marfikent': 71352,
 'Markab': 45941,
 'Megrez': 59774,
 'Men': 71860,
 'Menkalinan': 28360,
 'Menkent': 68933,
 'Merak': 53910,
 'Miaplacidus': 45238,
 'Mimosa': 62434,
 'Mintaka': 25930,
 'Mira': 10826,
 'Mirach': 5447,
 'Mirfak': 15863,
 'Mirzam': 30324,
 'Mizar': 65378,
 'Muhlifein': 61932,
 'Murzim': 30324,
 'Naos': 39429,
 'Nunki': 92855,
 'Peacock': 100751,
 'Phad': 58001,
 'Phecda': 58001,
 'Polaris': 11767,
 'Pollux': 37826,
 'Procyon': 37279,
 'Ras Alhague': 86032,
 'Rasalhague': 86032,
 'Regor': 39953,
 'Regulus': 49669,
 'Rigel': 24436,
 'Rigel Kent': 71683,
 'Rigil Kentaurus': 71683,
 'Sabik': 84012,
 'Sadira': 16537,
 'Sadr': 100453,
 'Saiph': 27366,
 'Sargas': 86228,
 'Scheat': 113881,
 'Schedar': 3179,
 'Scutulum': 45556,
 'Shaula': 85927,
 'Sirius': 32349,
 'Sirrah': 677,
 'South Star': 104382,
 'Spica': 65474,
 'Suhail': 44816,
 'Thuban': 68756,
 'Toliman': 71683,
 'Tseen She': 93308,
 'Tsih': 4427,
 'Turais': 45556,
 'Vega': 91262,
 'Wei': 82396,
 'Wezen': 34444



#TODO The indicator frontend expects just the star names, capitalised similar to pyephem...can we internally here have a mapping?
# https://www.cosmos.esa.int/web/hipparcos/common-star-names
# This list contained a duplicate Hipparcos Identifier of 68702 for a star with two common names: Agena and Hadar.
# The official name is Hadar and so Agena has been removed.
STARS = {
    "Acamar"            : 13847,
    "Achernar"          : 7588,
    "Acrux"             : 60718,
    "Adhara"            : 33579,
    "Albireo"           : 95947,
    "Alcor"             : 65477,
    "Alcyone"           : 17702,
    "Aldebaran"         : 21421,
    "Alderamin"         : 105199,
    "Algenib"           : 1067,
    "Algieba"           : 50583,
    "Algol"             : 14576,
    "Alhena"            : 31681,
    "Alioth"            : 62956,
    "Alkaid"            : 67301,
    "Almaak"            : 9640,
    "Alnair"            : 109268,
    "Alnath"            : 25428,
    "Alnilam"           : 26311,
    "Alnitak"           : 26727,
    "Alphard"           : 46390,
    "Alphekka"          : 76267,
    "Alpheratz"         : 677,
    "Alshain"           : 98036,
    "Altair"            : 97649,
    "Ankaa"             : 2081,
    "Antares"           : 80763,
    "Arcturus"          : 69673,
    "Arneb"             : 25985,
    "Babcock's star"    : 112247,
    "Barnard's star"    : 87937,
    "Bellatrix"         : 25336,
    "Betelgeuse"        : 27989,
    "Campbell's star"   : 96295,
    "Canopus"           : 30438,
    "Capella"           : 24608,
    "Caph"              : 746,
    "Castor"            : 36850,
    "Cor Caroli"        : 63125,
    "Cyg X-1"           : 98298,
    "Deneb"             : 102098,
    "Denebola"          : 57632,
    "Diphda"            : 3419,
    "Dubhe"             : 54061,
    "Enif"              : 107315,
    "Etamin"            : 87833,
    "Fomalhaut"         : 113368,
    "Groombridge 1830"  : 57939,
    "Hadar"             : 68702,
    "Hamal"             : 9884,
    "Izar"              : 72105,
    "Kapteyn's star"    : 24186,
    "Kaus Australis"    : 90185,
    "Kocab"             : 72607,
    "Kruger 60"         : 110893,
    "Luyten's star"     : 36208,
    "Markab"            : 113963,
    "Megrez"            : 59774,
    "Menkar"            : 14135,
    "Merak"             : 53910,
    "Mintaka"           : 25930,
    "Mira"              : 10826,
    "Mirach"            : 5447,
    "Mirphak"           : 15863,
    "Mizar"             : 65378,
    "Nihal"             : 25606,
    "Nunki"             : 92855,
    "Phad"              : 58001,
    "Pleione"           : 17851,
    "Polaris"           : 11767,
    "Pollux"            : 37826,
    "Procyon"           : 37279,
    "Proxima"           : 70890,
    "Rasalgethi"        : 84345,
    "Rasalhague"        : 86032,
    "Red Rectangle"     : 30089,
    "Regulus"           : 49669,
    "Rigel"             : 24436,
    "Rigil Kent"        : 71683,
    "Sadalmelik"        : 109074,
    "Saiph"             : 27366,
    "Scheat"            : 113881,
    "Shaula"            : 85927,
    "Shedir"            : 3179,
    "Sheliak"           : 92420,
    "Sirius"            : 32349,
    "Spica"             : 65474,
    "Tarazed"           : 97278,
    "Thuban"            : 68756,
    "Unukalhai"         : 77070,
    "Van Maanen 2"      : 3829,
    "Vega"              : 91262,
    "Vindemiatrix"      : 63608,
    "Zaurak"            : 18543,
    "3C 273"            : 60936 }






LUNAR_PHASE_FULL_MOON = "FULL_MOON"
LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
LUNAR_PHASE_NEW_MOON = "NEW_MOON"
LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"

MAGNITUDE_MAXIMUM = 15.0 # No point going any higher for the typical home astronomer.
MAGNITUDE_MINIMUM = -10.0 # Have found magnitudes in comet OE data which are, erroneously, brighter than the sun, so set a lower limit.

DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS = "%Y-%m-%d %H:%M:%S"


# Returns a dictionary with astronomical information:
#     Key is a tuple of AstronomicalBodyType, a name tag and a data tag.
#     Value is the data as a string.
#
# If a body is never up, no data is added.
# If a body is always up, azimuth/altitude are added.
# If the body is below the horizon, only the rise date/time is added.
# If the body is above the horizon, set date/time and azimuth/altitude are added.
#
# NOTE: Any error when computing a body or if a body never rises, no result is added for that body.
def getAstronomicalInformation( utcNow,
                                latitude, longitude, elevation,
                                planets,
                                stars,
                                satellites, satelliteData,
                                comets, cometData,
                                minorPlanets, minorPlanetData,
                                magnitude,
                                hideIfBelowHorizon ):

    data = { }

    # Used internally to create the observer/city...removed before passing back to the caller.
    data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ] = str( latitude )
    data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ] = str( longitude )
    data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ] = str( elevation )

    ephemNow = ephem.Date( utcNow )

    __calculateMoon( ephemNow, data, hideIfBelowHorizon )
    __calculateSun( ephemNow, data, hideIfBelowHorizon )
    __calculatePlanets( ephemNow, data, planets, magnitude, hideIfBelowHorizon )
    __calculateStars( ephemNow, data, stars, magnitude, hideIfBelowHorizon )
    __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.Comet, comets, cometData, magnitude, hideIfBelowHorizon )
    __calculateCometsOrMinorPlanets( ephemNow, data, AstronomicalBodyType.MinorPlanet, minorPlanets, minorPlanetData, magnitude, hideIfBelowHorizon )
    __calculateSatellites( ephemNow, data, satellites, satelliteData )

    del data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ]
    del data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ]
    del data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ]

    return data


# Return a list of cities, sorted alphabetically, sensitive to locale.
def getCities(): return sorted( _city_data.keys(), key = locale.strxfrm )


# Returns the latitude, longitude and elevation for the PyEphem city.
def getLatitudeLongitudeElevation( city ): return float( _city_data.get( city )[ 0 ] ), \
                                                  float( _city_data.get( city )[ 1 ] ), \
                                                  _city_data.get( city )[ 2 ]

# Takes a dictionary of orbital element data (for comets or minor planets),
# in which the key is the body name and value is the orbital element data.
#
# Returns a dictionary in which each item has a magnitude less than or equal to the maximum magnitude.
# May be empty.
def getOrbitalElementsLessThanMagnitude( orbitalElementData, maximumMagnitude ):
    results = { }
    for key in orbitalElementData:
        body = ephem.readdb( orbitalElementData[ key ].getData() )
        body.compute( ephem.city( "London" ) ) # Use any city; makes no difference to obtain the magnitude.
        bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
        if not bad and body.mag >= MAGNITUDE_MINIMUM and body.mag <= maximumMagnitude:
            results[ key ] = orbitalElementData[ key ]

    return results


# http://www.ga.gov.au/geodesy/astro/moonrise.jsp
# http://futureboy.us/fsp/moon.fsp
# http://www.geoastro.de/moondata/index.html
# http://www.geoastro.de/SME/index.htm
# http://www.geoastro.de/elevazmoon/index.htm
# http://www.geoastro.de/altazsunmoon/index.htm
# http://www.geoastro.de/sundata/index.html
# http://www.satellite-calculations.com/Satellite/suncalc.htm
def __calculateMoon( ephemNow, data, hideIfBelowHorizon ):
    key = ( AstronomicalBodyType.Moon, NAME_TAG_MOON )
    hidden = __calculateCommon( ephemNow, data, ephem.Moon(), AstronomicalBodyType.Moon, NAME_TAG_MOON, hideIfBelowHorizon )
    if not hidden:
        data[ key + ( DATA_FIRST_QUARTER, ) ] = __toDateTimeString( ephem.next_first_quarter_moon( ephemNow ).datetime() )
        data[ key + ( DATA_FULL, ) ] = __toDateTimeString( ephem.next_full_moon( ephemNow ).datetime() )
        data[ key + ( DATA_THIRD_QUARTER, ) ] = __toDateTimeString( ephem.next_last_quarter_moon( ephemNow ).datetime() )
        data[ key + ( DATA_NEW, ) ] = __toDateTimeString( ephem.next_new_moon( ephemNow ).datetime() )
        __calculateEclipse( ephemNow.datetime(), data, AstronomicalBodyType.Moon, NAME_TAG_MOON )

    # Used for internal processing; indirectly presented to the user.
    moon = ephem.Moon()
    moon.compute( __getCity( data, ephemNow ) )
    data[ key + ( DATA_ILLUMINATION, ) ] = str( int( moon.phase ) ) # Needed for icon.
    data[ key + ( DATA_PHASE, ) ] = __getLunarPhase( int( moon.phase ), ephem.next_full_moon( ephemNow ), ephem.next_new_moon( ephemNow ) ) # Need for notification.
    data[ key + ( DATA_BRIGHT_LIMB, ) ] = str( __getZenithAngleOfBrightLimb( ephemNow, data, ephem.Moon() ) ) # Needed for icon.


# Compute the bright limb angle (relative to zenith) between the sun and a planetary body (typically the moon).
# Measured in radians counter clockwise from a positive y axis.
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
def __getZenithAngleOfBrightLimb( ephemNow, data, body ):
    city = __getCity( data, ephemNow )
    sun = ephem.Sun( city )
    body.compute( city )

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
    y = math.cos( sun.dec ) * math.sin( sun.ra - body.ra )
    x = math.sin( sun.dec ) * math.cos( body.dec ) - math.cos( sun.dec ) * math.sin( body.dec ) * math.cos( sun.ra - body.ra )
    positionAngleOfBrightLimb = math.atan2( y, x )

    # Astronomical Algorithms by Jean Meeus, Second Edition, page 92.
    # https://tycho.usno.navy.mil/sidereal.html
    # http://www.wwu.edu/skywise/skymobile/skywatch.html
    # https://www.heavens-above.com/whattime.aspx?lat=-33.8675&lng=151.207&loc=Sydney&alt=19&tz=AEST&cul=en
    hourAngle = city.sidereal_time() - body.ra

    # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
    y = math.sin( hourAngle )
    x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
    parallacticAngle = math.atan2( y, x )

    return ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi )


# Get the lunar phase for the given date/time and illumination percentage.
#
#    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
#    nextFullMoonDate The date of the next full moon.
#    nextNewMoonDate The date of the next new moon.
def __getLunarPhase( illuminationPercentage, nextFullMoonDate, nextNewMoonDate ):
    phase = None
    if nextFullMoonDate < nextNewMoonDate: # No need for these dates to be localised...just need to know which date is before the other.
        # Between a new moon and a full moon...
        if( illuminationPercentage > 99 ):
            phase = LUNAR_PHASE_FULL_MOON
        elif illuminationPercentage <= 99 and illuminationPercentage > 50:
            phase = LUNAR_PHASE_WAXING_GIBBOUS
        elif illuminationPercentage == 50:
            phase = LUNAR_PHASE_FIRST_QUARTER
        elif illuminationPercentage < 50 and illuminationPercentage >= 1:
            phase = LUNAR_PHASE_WAXING_CRESCENT
        else: # illuminationPercentage < 1
            phase = LUNAR_PHASE_NEW_MOON
    else:
        # Between a full moon and the next new moon...
        if( illuminationPercentage > 99 ):
            phase = LUNAR_PHASE_FULL_MOON
        elif illuminationPercentage <= 99 and illuminationPercentage > 50:
            phase = LUNAR_PHASE_WANING_GIBBOUS
        elif illuminationPercentage == 50:
            phase = LUNAR_PHASE_THIRD_QUARTER
        elif illuminationPercentage < 50 and illuminationPercentage >= 1:
            phase = LUNAR_PHASE_WANING_CRESCENT
        else: # illuminationPercentage < 1
            phase = LUNAR_PHASE_NEW_MOON

    return phase


# http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
# http://www.ga.gov.au/geodesy/astro/sunrise.jsp
# http://www.geoastro.de/elevaz/index.htm
# http://www.geoastro.de/SME/index.htm
# http://www.geoastro.de/altazsunmoon/index.htm
# http://futureboy.us/fsp/sun.fsp
# http://www.satellite-calculations.com/Satellite/suncalc.htm
def __calculateSun( ephemNow, data, hideIfBelowHorizon ):
    hidden = __calculateCommon( ephemNow, data, ephem.Sun(), AstronomicalBodyType.Sun, NAME_TAG_SUN, hideIfBelowHorizon )
    if not hidden:
        __calculateEclipse( ephemNow.datetime(), data, AstronomicalBodyType.Sun, NAME_TAG_SUN )

        key = ( AstronomicalBodyType.Sun, NAME_TAG_SUN )

        equinox = ephem.next_equinox( ephemNow )
        solstice = ephem.next_solstice( ephemNow )
        data[ key + ( DATA_EQUINOX, ) ] = __toDateTimeString( equinox.datetime() )
        data[ key + ( DATA_SOLSTICE, ) ] = __toDateTimeString( solstice.datetime() )


# Calculate next eclipse for either the Sun or Moon.
def __calculateEclipse( utcNow, data, astronomicalBodyType, dataTag ):
    eclipseInformation = eclipse.getEclipseForUTC( utcNow, astronomicalBodyType == AstronomicalBodyType.Moon )
    key = ( astronomicalBodyType, dataTag )
    data[ key + ( DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ]
    data[ key + ( DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
    data[ key + ( DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ]
    data[ key + ( DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


# http://www.geoastro.de/planets/index.html
# http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
def __calculatePlanets( ephemNow, data, planets, magnitude, hideIfBelowHorizon ):
    for planet in planets:
        planetObject = getattr( ephem, planet.title() )()
        planetObject.compute( __getCity( data, ephemNow ) )
        if planetObject.mag >= MAGNITUDE_MINIMUM and planetObject.mag <= magnitude:
            __calculateCommon( ephemNow, data, planetObject, AstronomicalBodyType.Planet, planet, hideIfBelowHorizon )


# http://aa.usno.navy.mil/data/docs/mrst.php
def __calculateStars( ephemNow, data, stars, magnitude, hideIfBelowHorizon ):
    for star in stars:
        starObject = ephem.star( star.title() )
        starObject.compute( __getCity( data, ephemNow ) )
        if starObject.mag >= MAGNITUDE_MINIMUM and starObject.mag <= magnitude:
            __calculateCommon( ephemNow, data, starObject, AstronomicalBodyType.Star, star, hideIfBelowHorizon )


# Compute data for comets or minor planets.
def __calculateCometsOrMinorPlanets( ephemNow, data, astronomicalBodyType, cometsOrMinorPlanets, cometOrMinorPlanetData, magnitude, hideIfBelowHorizon ):
    for key in cometsOrMinorPlanets:
        if key in cometOrMinorPlanetData:
            body = ephem.readdb( cometOrMinorPlanetData[ key ].getData() )
            body.compute( __getCity( data, ephemNow ) )
            bad = math.isnan( body.earth_distance ) or math.isnan( body.phase ) or math.isnan( body.size ) or math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!
            if not bad and body.mag >= MAGNITUDE_MINIMUM and body.mag <= magnitude:
                __calculateCommon( ephemNow, data, body, astronomicalBodyType, key, hideIfBelowHorizon )


# Calculates common attributes such as rise/set date/time, azimuth/altitude.
#
# If hideIfBelowHorzion is True, if a body is below the horizon (but will rise), that body is dropped (no data stored).
# Otherwise the body will be included.
#
# Returns True if the body was dropped:
#    The body is below the horizon and hideIfBelowHorizon is True.
#    The body is never up.
def __calculateCommon( ephemNow, data, body, astronomicalBodyType, nameTag, hideIfBelowHorizon ):
    dropped = False
    key = ( astronomicalBodyType, nameTag )
    try:
        city = __getCity( data, ephemNow )
        rising = city.next_rising( body )
        setting = city.next_setting( body )

        if rising > setting: # Above the horizon.
            data[ key + ( DATA_SET_DATE_TIME, ) ] = __toDateTimeString( setting.datetime() )
            body.compute( __getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
            data[ key + ( DATA_AZIMUTH, ) ] = str( repr( body.az ) )
            data[ key + ( DATA_ALTITUDE, ) ] = str( repr( body.alt ) )

        else: # Below the horizon.
            if hideIfBelowHorizon:
                dropped = True
            else:
                data[ key + ( DATA_RISE_DATE_TIME, ) ] = __toDateTimeString( rising.datetime() )

    except ephem.AlwaysUpError:
        body.compute( __getCity( data, ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
        data[ key + ( DATA_AZIMUTH, ) ] = str( repr( body.az ) )
        data[ key + ( DATA_ALTITUDE, ) ] = str( repr( body.alt ) )

    except ephem.NeverUpError:
        dropped = True

    return dropped


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
def __calculateSatellites( ephemNow, data, satellites, satelliteData ):
    for key in satellites:
        if key in satelliteData:
            __calculateNextSatellitePass( ephemNow, data, key, satelliteData[ key ] )


#TODO On Sep 1st I ran the indicator at 3pm and noticed that there were
# satellites currently in transit with a rise date/time of Aug 29 18:40
# and then satellites to rise Aug 30 4:52.
# The TLE cache file had filename of satellite-tle-20190901045141
#So something is wrong...perhaps in the string comparison of dates (might have to use datetime rather than dates).
#Maybe this error was due to setting a dodgy date/time in the past (for testing) but using a TLE data file newer than the test time? 
def __calculateNextSatellitePass( ephemNow, data, key, satelliteTLE ):
    key = ( AstronomicalBodyType.Satellite, key )
    currentDateTime = ephemNow
    endDateTime = ephem.Date( ephemNow + ephem.hour * 36 ) # Stop looking for passes 36 hours from now.
    while currentDateTime < endDateTime:
        city = __getCity( data, currentDateTime )
        satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getLine1(), satelliteTLE.getLine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
        satellite.compute( city )
        try:
            nextPass = city.next_pass( satellite )

        except ValueError:
            if satellite.circumpolar:
#                 print( "circumpolar" )#TODO
                data[ key + ( DATA_AZIMUTH, ) ] = str( str( repr( satellite.az ) ) )
                data[ key + ( DATA_ALTITUDE, ) ] = str( satellite.alt )
            break

        if not __isSatellitePassValid( nextPass ):
            break

        # Determine if the pass is yet to happen or underway...
        if nextPass[ 0 ] > nextPass[ 4 ]: # The rise time is after set time, so the satellite is currently passing.
            setTime = nextPass[ 4 ]
            nextPass = __calculateSatellitePassForRisingPriorToNow( currentDateTime, data, satelliteTLE )
            if nextPass is None:
                currentDateTime = ephem.Date( setTime + ephem.minute * 30 ) # Could not determine the rise, so look for the next pass.
                continue
            
        # The satellite has a rise/transit/set; determine if the pass is visible.
        passIsVisible = __isSatellitePassVisible( data, nextPass[ 2 ], satellite )
        if not passIsVisible:
            currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 ) # Look for the next pass.
            continue

        # If a satellite is in transit or will rise within five minutes of now, then show all information...
        if nextPass[ 0 ] < ( ephem.Date( ephemNow + ephem.minute * 5 ) ):
#             print( "transit" )#TODO
            data[ key + ( DATA_RISE_DATE_TIME, ) ] = __toDateTimeString( nextPass[ 0 ].datetime() )
            data[ key + ( DATA_RISE_AZIMUTH, ) ] = str( repr( nextPass[ 1 ] ) )
            data[ key + ( DATA_SET_DATE_TIME, ) ] = __toDateTimeString( nextPass[ 4 ].datetime() )
            data[ key + ( DATA_SET_AZIMUTH, ) ] = str( repr( nextPass[ 5 ] ) )

        else: # Satellite will rise later, so only add rise time.
#             print( "below horizon" )#TODO
            data[ key + ( DATA_RISE_DATE_TIME, ) ] = __toDateTimeString( nextPass[ 0 ].datetime() )

        break


#TODO May not need this any more...
# GitHub issue #63: 
# The rise, culminate, and set returned by next_pass() are now consecutive values for a single pass. 
# Pass singlepass=False to return the original next_rise, next_culminate, next_set even if next_set < next_rise (the satellite is already up).
def __calculateSatellitePassForRisingPriorToNow( ephemNow, data, satelliteTLE ):
    currentDateTime = ephem.Date( ephemNow - ephem.minute ) # Start looking from one minute ago.
    endDateTime = ephem.Date( ephemNow - ephem.hour ) # Only look back an hour for the rise time (then just give up).
    nextPass = None
    while currentDateTime > endDateTime:
        city = __getCity( data, currentDateTime )
        satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getLine1(), satelliteTLE.getLine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
        satellite.compute( city )
        try:
            nextPass = city.next_pass( satellite )
            if not __isSatellitePassValid( nextPass ):
                nextPass = None
                break # Unlikely to happen but better to be safe and check!

            if nextPass[ 0 ] < nextPass[ 4 ]:
                break # Found the rise time!

            currentDateTime = ephem.Date( currentDateTime - ephem.minute )

        except:
            nextPass = None
            break # This should never happen as the satellite has a rise and set (is not circumpolar or never up).

    return nextPass


def __isSatellitePassValid( satellitePass ):
    return \
        satellitePass and \
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
def __isSatellitePassVisible( data, passDateTime, satellite ):
    city = __getCity( data, passDateTime )
    city.pressure = 0
    city.horizon = "-0:34"

    satellite.compute( city )
    sun = ephem.Sun()
    sun.compute( city )

    return satellite.eclipsed is False and \
           sun.alt > ephem.degrees( "-18" ) and \
           sun.alt < ephem.degrees( "-6" )


def __toDateTimeString( dateTime ): return dateTime.strftime( DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )


def __getCity( data, date ):
    city = ephem.city( "London" ) # Put in a city name known to exist in PyEphem then doctor to the correct lat/long/elev.
    city.date = date
    city.lat = data[ ( None, NAME_TAG_CITY, DATA_LATITUDE ) ]
    city.lon = data[ ( None, NAME_TAG_CITY, DATA_LONGITUDE ) ]
    city.elev = float( data[ ( None, NAME_TAG_CITY, DATA_ELEVATION ) ] )

    return city