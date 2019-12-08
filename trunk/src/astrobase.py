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
class BodyType: Comet, MinorPlanet, Moon, Planet, Satellite, Star, Sun = range( 7 )


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

NAME_TAG_CITY = "CITY"
NAME_TAG_MOON = "MOON"
NAME_TAG_SUN = "SUN"


PLANET_MERCURY = "MERCURY"
PLANET_VENUS = "VENUS"
PLANET_MARS = "MARS"
PLANET_JUPITER = "JUPITER"
PLANET_SATURN = "SATURN"
PLANET_URANUS = "URANUS"
PLANET_NEPTUNE = "NEPTUNE"
PLANET_PLUTO = "PLUTO"

PLANETS = [ PLANET_MERCURY, PLANET_VENUS, PLANET_MARS, PLANET_JUPITER, PLANET_SATURN, PLANET_URANUS, PLANET_NEPTUNE, PLANET_PLUTO ]




#TODO DOuble check against the original list from pyephem.
# Data is adapted from the version of the Hipparcos star catalog at:
# ftp://adc.gsfc.nasa.gov/pub/adc/archives/catalogs/1/1239/hip_main.dat.gz
# Of the thousand brighest Hipparcos stars, those with proper names
# registered at http://simbad.u-strasbg.fr/simbad/ were chosen.
# """
# 
# db = """\
# Sirrah,f|S|B9,0:08:23.2|135.68,29:05:27|-162.95,2.07,2000,0
# Caph,f|S|F2,0:09:10.1|523.39,59:09:01|-180.42,2.28,2000,0
# Algenib,f|S|B2,0:13:14.2|4.7,15:11:01|-8.24,2.83,2000,0
# Schedar,f|S|K0,0:40:30.4|50.36,56:32:15|-32.17,2.24,2000,0
# Mirach,f|S|M0,1:09:43.8|175.59,35:37:15|-112.23,2.07,2000,0
# Achernar,f|S|B3,1:37:42.8|88.02,-57:14:12|-40.08,0.45,2000,0
# Almach,f|S|B8,2:03:53.9|43.08,42:19:48|-50.85,2.10,2000,0
# Hamal,f|S|K2,2:07:10.3|190.73,23:27:46|-145.77,2.01,2000,0
# Polaris,f|S|F7,2:31:47.1|44.22,89:15:51|-11.74,1.97,2000,0
# Menkar,f|S|M2,3:02:16.8|-11.81,4:05:24|-78.76,2.54,2000,0
# Algol,f|S|B8,3:08:10.1|2.39,40:57:20|-1.44,2.09,2000,0
# Electra,f|S|B6,3:44:52.5|21.55,24:06:48|-44.92,3.72,2000,0
# Taygeta,f|S|B6,3:45:12.5|19.35,24:28:03|-41.63,4.30,2000,0
# Maia,f|S|B8,3:45:49.6|21.09,24:22:04|-45.03,3.87,2000,0
# Merope,f|S|B6,3:46:19.6|21.17,23:56:54|-42.67,4.14,2000,0
# Alcyone,f|S|B7,3:47:29.1|19.35,24:06:19|-43.11,2.85,2000,0
# Atlas,f|S|B8,3:49:09.7|17.77,24:03:13|-44.7,3.62,2000,0
# Zaurak,f|S|M1,3:58:01.7|60.51,-13:30:30|-111.34,2.97,2000,0
# Aldebaran,f|S|K5,4:35:55.2|62.78,16:30:35|-189.36,0.87,2000,0
# Rigel,f|S|B8,5:14:32.3|1.87,-8:12:06|-0.56,0.18,2000,0
# Capella,f|S|M1,5:16:41.3|75.52,45:59:57|-427.13,0.08,2000,0
# Bellatrix,f|S|B2,5:25:07.9|-8.75,6:20:59|-13.28,1.64,2000,0
# Elnath,f|S|B7,5:26:17.5|23.28,28:36:28|-174.22,1.65,2000,0
# Nihal,f|S|G5,5:28:14.7|-5.03,-20:45:33|-85.92,2.81,2000,0
# Mintaka,f|S|O9,5:32:00.4|1.67,-0:17:57|0.56,2.25,2000,0
# Arneb,f|S|F0,5:32:43.8|3.27,-17:49:20|1.54,2.58,2000,0
# Alnilam,f|S|B0,5:36:12.8|1.49,-1:12:07|-1.06,1.69,2000,0
# Alnitak,f|S|O9,5:40:45.5|3.99,-1:56:33|2.54,1.74,2000,0
# Saiph,f|S|B0,5:47:45.4|1.55,-9:40:11|-1.2,2.07,2000,0
# Betelgeuse,f|S|M2,5:55:10.3|27.33,7:24:25|10.86,0.45,2000,0
# Menkalinan,f|S|A2,5:59:31.8|-56.41,44:56:51|-0.88,1.90,2000,0
# Mirzam,f|S|B1,6:22:42.0|-3.45,-17:57:21|-0.47,1.98,2000,0
# Canopus,f|S|F0,6:23:57.1|19.99,-52:41:45|23.67,-0.62,2000,0
# Alhena,f|S|A0,6:37:42.7|-2.04,16:23:58|-66.92,1.93,2000,0
# Sirius,f|S|A0,6:45:09.3|-546.01,-16:42:47|-1223.08,-1.44,2000,0
# Adara,f|S|B2,6:58:37.6|2.63,-28:58:20|2.29,1.50,2000,0
# Wezen,f|S|F8,7:08:23.5|-2.75,-26:23:36|3.33,1.83,2000,0
# Castor,f|S|A2,7:34:36.0|-206.33,31:53:19|-148.18,1.58,2000,0
# Procyon,f|S|F5,7:39:18.5|-716.57,5:13:39|-1034.58,0.40,2000,0
# Pollux,f|S|K0,7:45:19.4|-625.69,28:01:35|-45.95,1.16,2000,0
# Naos,f|S|O5,8:03:35.1|-30.82,-40:00:12|16.77,2.21,2000,0
# Alphard,f|S|K3,9:27:35.3|-14.49,-8:39:31|33.25,1.99,2000,0
# Regulus,f|S|B7,10:08:22.5|-249.4,11:58:02|4.91,1.36,2000,0
# Algieba,f|S|K0,10:19:58.2|310.77,19:50:31|-152.88,2.01,2000,0
# Merak,f|S|A1,11:01:50.4|81.66,56:22:56|33.74,2.34,2000,0
# Dubhe,f|S|F7,11:03:43.8|-136.46,61:45:04|-35.25,1.81,2000,0
# Denebola,f|S|A3,11:49:03.9|-499.02,14:34:20|-113.78,2.14,2000,0
# Phecda,f|S|A0,11:53:49.7|107.76,53:41:41|11.16,2.41,2000,0
# Minkar,f|S|K2,12:10:07.5|-71.52,-22:37:11|10.55,3.02,2000,0
# Megrez,f|S|A3,12:15:25.5|103.56,57:01:57|7.81,3.32,2000,0
# Gienah Corvi,f|S|B8,12:15:48.5|-159.58,-17:32:31|22.31,2.58,2000,0
# Mimosa,f|S|B0,12:47:43.3|-48.24,-59:41:19|-12.82,1.25,2000,0
# Alioth,f|S|A0,12:54:01.6|111.74,55:57:35|-8.99,1.76,2000,0
# Vindemiatrix,f|S|G8,13:02:10.8|-275.05,10:57:33|19.96,2.85,2000,0
# Mizar,f|S|A2,13:23:55.4|121.23,54:55:32|-22.01,2.23,2000,0
# Spica,f|S|B1,13:25:11.6|-42.5,-11:09:40|-31.73,0.98,2000,0
# Alcor,f|S|A5,13:25:13.4|120.35,54:59:17|-16.94,3.99,2000,0
# Alcaid,f|S|B3,13:47:32.5|-121.23,49:18:48|-15.56,1.85,2000,0
# Agena,f|S|B1,14:03:49.4|-33.96,-60:22:23|-25.06,0.61,2000,0
# Thuban,f|S|A0,14:04:23.4|-56.52,64:22:33|17.19,3.67,2000,0
# Arcturus,f|S|K2,14:15:40.3|-1093.45,19:11:14|-1999.4,-0.05,2000,0
# Izar,f|S|A0,14:44:59.3|-50.65,27:04:27|20,2.35,2000,0
# Kochab,f|S|K4,14:50:42.4|-32.29,74:09:20|11.91,2.07,2000,0
# Alphecca,f|S|A0,15:34:41.2|120.38,26:42:54|-89.44,2.22,2000,0
# Unukalhai,f|S|K2,15:44:16.0|134.66,6:25:32|44.14,2.63,2000,0
# Antares,f|S|M1,16:29:24.5|-10.16,-26:25:55|-23.21,1.06,2000,0
# Rasalgethi,f|S|M5,17:14:38.9|-6.71,14:23:25|32.78,2.78,2000,0
# Shaula,f|S|B1,17:33:36.5|-8.9,-37:06:13|-29.95,1.62,2000,0
# Rasalhague,f|S|A5,17:34:56.0|110.08,12:33:38|-222.61,2.08,2000,0
# Cebalrai,f|S|K2,17:43:28.4|-40.67,4:34:01|158.8,2.76,2000,0
# Etamin,f|S|K5,17:56:36.4|-8.52,51:29:20|-23.05,2.24,2000,0
# Kaus Australis,f|S|B9,18:24:10.4|-39.61,-34:23:04|-124.05,1.79,2000,0
# Vega,f|S|A0,18:36:56.2|201.02,38:46:59|287.46,0.03,2000,0
# Sheliak,f|S|A8,18:50:04.8|1.1,33:21:46|-4.46,3.52,2000,0
# Nunki,f|S|B2,18:55:15.9|13.87,-26:17:48|-52.65,2.05,2000,0
# Sulafat,f|S|B9,18:58:56.6|-2.76,32:41:22|1.77,3.25,2000,0
# Arkab Prior,f|S|B9,19:22:38.3|7.31,-44:27:32|-22.43,3.96,2000,0
# Arkab Posterior,f|S|F2,19:23:13.1|92.78,-44:47:59|-53.73,4.27,2000,0
# Rukbat,f|S|B8,19:23:53.2|32.67,-40:36:56|-120.81,3.96,2000,0
# Albereo,f|S|K3,19:30:43.3|-7.09,27:57:35|-5.63,3.05,2000,0
# Tarazed,f|S|K3,19:46:15.6|15.72,10:36:48|-3.08,2.72,2000,0
# Altair,f|S|A7,19:50:46.7|536.82,8:52:03|385.54,0.76,2000,0
# Alshain,f|S|G8,19:55:18.8|46.35,6:24:29|-481.32,3.71,2000,0
# Sadr,f|S|F8,20:22:13.7|2.43,40:15:24|-0.93,2.23,2000,0
# Peacock,f|S|B2,20:25:38.9|7.71,-56:44:06|-86.15,1.94,2000,0
# Deneb,f|S|A2,20:41:25.9|1.56,45:16:49|1.55,1.25,2000,0
# Alderamin,f|S|A7,21:18:34.6|149.91,62:35:08|48.27,2.45,2000,0
# Alfirk,f|S|B2,21:28:39.6|12.6,70:33:39|8.73,3.23,2000,0
# Enif,f|S|K2,21:44:11.1|30.02,9:52:30|1.38,2.38,2000,0
# Sadalmelik,f|S|G2,22:05:47.0|17.9,-0:19:11|-9.93,2.95,2000,0
# Alnair,f|S|B7,22:08:13.9|127.6,-46:57:38|-147.91,1.73,2000,0
# Fomalhaut,f|S|A3,22:57:38.8|329.22,-29:37:19|-164.22,1.17,2000,0
# Scheat,f|S|M2,23:03:46.3|187.76,28:04:57|137.61,2.44,2000,0
# Markab,f|S|B9,23:04:45.6|61.1,15:12:19|-42.56,2.49,2000,0



# From ephem/stars.py
# Star names are capitalised, whereas Pyephem uses titled strings.
# At the API we accept capitalised star names, but internally we title them to satisfy Pyephem.
STARS = [
    "ACHERNAR", 
    "ADHARA", #ADARA 
    "ALBIREO", #ALBEREO 
    "ALKAID", #ALCAID 
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
    "ELTANIN", #ETAMIN
    "FOMALHAUT", 
    "GIENAH CORVI",  #TODO Figure this out.  Not fully sure of the name via wikipedia...and maybe skyfield does not have it. 
    "HADAR", #AGENA
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
    "SIRRAH", # ALPHERATZ
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



#TODO From skyfield:
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