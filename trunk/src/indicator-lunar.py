#!/usr/bin/env python3


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


# Application indicator which displays lunar, solar, planetary, star, orbital element and satellite information.


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  https://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/api/AppIndicator3_0.1/classes/Indicator.html
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-14.04
#  https://wiki.gnome.org/Projects/PyGObject/Threading
#  https://wiki.gnome.org/Projects/PyGObject
#  http://lazka.github.io/pgi-docs


INDICATOR_NAME = "indicator-lunar"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import AppIndicator3, GLib, GObject, Gtk, Notify
from threading import Thread
from urllib.request import urlopen
import copy, datetime, eclipse, json, locale, logging, math, os, pythonutils, re, satellite, shutil, subprocess, sys, tempfile, threading, time, webbrowser

try:
    import ephem
    from ephem.cities import _city_data
    from ephem.stars import stars
except:
    pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "You must also install python3-ephem!" ) )
    sys.exit()


class AstronomicalObjectType: Moon, OrbitalElement, Planet, PlanetaryMoon, Satellite, Star, Sun = range( 7 )


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.57"
    ICON_STATE = True # https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620
    ICON = INDICATOR_NAME
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = INDICATOR_NAME + ".desktop"
    SVG_FULL_MOON_FILE = tempfile.gettempdir() + "/" + "." + INDICATOR_NAME + "-fullmoon-icon" + ".svg"
    SVG_SATELLITE_ICON = INDICATOR_NAME + "-satellite"

    ABOUT_COMMENTS = _( "Displays lunar, solar, planetary, orbital element, star and satellite information." )
    ABOUT_CREDIT_BRIGHT_LIMB = _( "Bright Limb from 'Astronomical Algorithms' by Jean Meeus." )
    ABOUT_CREDIT_ECLIPSE = _( "Eclipse information by Fred Espenak and Jean Meeus. http://eclipse.gsfc.nasa.gov" )
    ABOUT_CREDIT_PYEPHEM = _( "Calculations courtesy of PyEphem/XEphem. http://rhodesmill.org/pyephem" )
    ABOUT_CREDIT_ORBITAL_ELEMENTS = _( "Orbital element data by Minor Planet Center. http://www.minorplanetcenter.net" )
    ABOUT_CREDIT_SATELLITE = _( "Satellite TLE data by Dr T S Kelso. http://www.celestrak.com" )
    ABOUT_CREDIT_TROPICAL_SIGN = _( "Tropical Sign by Ignius Drake." )
    ABOUT_CREDITS = [ ABOUT_CREDIT_PYEPHEM, ABOUT_CREDIT_ECLIPSE, ABOUT_CREDIT_TROPICAL_SIGN, ABOUT_CREDIT_BRIGHT_LIMB, ABOUT_CREDIT_SATELLITE, ABOUT_CREDIT_ORBITAL_ELEMENTS ]

    DISPLAY_NEEDS_REFRESH = _( "(needs refresh)" )
    INDENT = "    "

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"

    SETTINGS_CITY_ELEVATION = "cityElevation"
    SETTINGS_CITY_LATITUDE = "cityLatitude"
    SETTINGS_CITY_LONGITUDE = "cityLongitude"
    SETTINGS_CITY_NAME = "cityName"
    SETTINGS_HIDE_BODY_IF_NEVER_UP = "hideBodyIfNeverUp"
    SETTINGS_INDICATOR_TEXT = "indicatorText"
    SETTINGS_HIDE_SATELLITE_IF_NO_VISIBLE_PASS = "hideSatelliteIfNoVisiblePass"
    SETTINGS_ORBITAL_ELEMENT_URL = "orbitalElementURL"
    SETTINGS_ORBITAL_ELEMENTS = "orbitalElements"
    SETTINGS_ORBITAL_ELEMENTS_ADD_NEW = "orbitalElementsAddNew"
    SETTINGS_ORBITAL_ELEMENTS_MAGNITUDE = "orbitalElementsMagnitude"
    SETTINGS_PLANETS = "planets"
    SETTINGS_SATELLITE_MENU_TEXT = "satelliteMenuText"
    SETTINGS_SATELLITE_NOTIFICATION_MESSAGE = "satelliteNotificationMessage"
    SETTINGS_SATELLITE_NOTIFICATION_SUMMARY = "satelliteNotificationSummary"
    SETTINGS_SATELLITE_ON_CLICK_URL = "satelliteOnClickURL"
    SETTINGS_SATELLITE_TLE_URL = "satelliteTLEURL"
    SETTINGS_SATELLITES = "satellites"
    SETTINGS_SATELLITES_ADD_NEW = "satellitesAddNew"
    SETTINGS_SATELLITES_SORT_BY_DATE_TIME = "satellitesSortByDateTime"
    SETTINGS_SHOW_ORBITAL_ELEMENTS_AS_SUBMENU = "showOrbitalElementsAsSubmenu"
    SETTINGS_SHOW_PLANETS_AS_SUBMENU = "showPlanetsAsSubmenu"
    SETTINGS_SHOW_SATELLITE_NOTIFICATION = "showSatelliteNotification"
    SETTINGS_SHOW_SATELLITES_AS_SUBMENU = "showSatellitesAsSubmenu"
    SETTINGS_SHOW_STARS_AS_SUBMENU = "showStarsAsSubmenu"
    SETTINGS_SHOW_WEREWOLF_WARNING = "showWerewolfWarning"
    SETTINGS_STARS = "stars"
    SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE = "werewolfWarningStartIlluminationPercentage"
    SETTINGS_WEREWOLF_WARNING_MESSAGE = "werewolfWarningMessage"
    SETTINGS_WEREWOLF_WARNING_SUMMARY = "werewolfWarningSummary"

    DATA_ALTITUDE = "ALTITUDE"
    DATA_AZIMUTH = "AZIMUTH"
    DATA_BRIGHT_LIMB = "BRIGHT LIMB"
    DATA_CITY_NAME = "CITY NAME"
    DATA_CONSTELLATION = "CONSTELLATION"
    DATA_DAWN = "DAWN"
    DATA_DECLINATION = "DECLINATION"
    DATA_DISTANCE_TO_EARTH = "DISTANCE TO EARTH"
    DATA_DISTANCE_TO_SUN = "DISTANCE TO SUN"
    DATA_DUSK = "DUSK"
    DATA_EARTH_VISIBLE = "EARTH VISIBLE"
    DATA_ECLIPSE_DATE_TIME = "ECLIPSE DATE TIME"
    DATA_ECLIPSE_LATITUDE_LONGITUDE = "ECLIPSE LATITUDE LONGITUDE"
    DATA_ECLIPSE_TYPE = "ECLIPSE TYPE"
    DATA_EQUINOX = "EQUINOX"
    DATA_FIRST_QUARTER = "FIRST QUARTER"
    DATA_FULL = "FULL"
    DATA_ILLUMINATION = "ILLUMINATION"
    DATA_MAGNITUDE = "MAGNITUDE"
    DATA_MESSAGE = "MESSAGE"
    DATA_X_OFFSET = "X OFFSET"
    DATA_Y_OFFSET = "Y OFFSET"
    DATA_Z_OFFSET = "Z OFFSET"
    DATA_NEW = "NEW"
    DATA_PHASE = "PHASE"
    DATA_RIGHT_ASCENSION = "RIGHT ASCENSION"
    DATA_RISE_AZIMUTH = "RISE AZIMUTH"
    DATA_RISE_TIME = "RISE TIME"
    DATA_SET_AZIMUTH = "SET AZIMUTH"
    DATA_SET_TIME = "SET TIME"
    DATA_SOLSTICE = "SOLSTICE"
    DATA_THIRD_QUARTER = "THIRD QUARTER"
    DATA_TROPICAL_SIGN = "TROPICAL SIGN"
    DATA_VISIBLE = "VISIBLE"

    DATA_TAGS = {
        DATA_ALTITUDE                   : _( "ALTITUDE" ),
        DATA_AZIMUTH                    : _( "AZIMUTH" ),
        DATA_BRIGHT_LIMB                : _( "BRIGHT LIMB" ),
        DATA_CITY_NAME                  : _( "CITY NAME" ),
        DATA_CONSTELLATION              : _( "CONSTELLATION" ),
        DATA_DAWN                       : _( "DAWN" ),
        DATA_DECLINATION                : _( "DECLINATION" ),
        DATA_DISTANCE_TO_EARTH          : _( "DISTANCE TO EARTH" ),
        DATA_DISTANCE_TO_SUN            : _( "DISTANCE TO SUN" ),
        DATA_DUSK                       : _( "DUSK" ),
        DATA_EARTH_VISIBLE              : _( "EARTH VISIBLE" ),
        DATA_ECLIPSE_DATE_TIME          : _( "ECLIPSE DATE TIME" ),
        DATA_ECLIPSE_LATITUDE_LONGITUDE : _( "ECLIPSE LATITUDE LONGITUDE" ),
        DATA_ECLIPSE_TYPE               : _( "ECLIPSE TYPE" ),
        DATA_EQUINOX                    : _( "EQUINOX" ),
        DATA_FIRST_QUARTER              : _( "FIRST QUARTER" ),
        DATA_FULL                       : _( "FULL" ),
        DATA_ILLUMINATION               : _( "ILLUMINATION" ),
        DATA_MAGNITUDE                  : _( "MAGNITUDE" ),
        DATA_MESSAGE                    : _( "MESSAGE" ),
        DATA_X_OFFSET                   : _( "X OFFSET" ),
        DATA_Y_OFFSET                   : _( "Y OFFSET" ),
        DATA_Z_OFFSET                   : _( "Z OFFSET" ),
        DATA_NEW                        : _( "NEW" ),
        DATA_PHASE                      : _( "PHASE" ),
        DATA_RIGHT_ASCENSION            : _( "RIGHT ASCENSION" ),
        DATA_RISE_AZIMUTH               : _( "RISE AZIMUTH" ),
        DATA_RISE_TIME                  : _( "RISE TIME" ),
        DATA_SET_AZIMUTH                : _( "SET AZIMUTH" ),
        DATA_SET_TIME                   : _( "SET TIME" ),
        DATA_SOLSTICE                   : _( "SOLSTICE" ),
        DATA_THIRD_QUARTER              : _( "THIRD QUARTER" ),
        DATA_TROPICAL_SIGN              : _( "TROPICAL SIGN" ),
        DATA_VISIBLE                    : _( "VISIBLE" ) }

    # Translated constellations.
    # Sourced from cns_namemap in ephem/libastro/constel.c
    CONSTELLATIONS = {
        "Andromeda"           : _( "Andromeda" ),
        "Antlia"              : _( "Antlia" ),
        "Apus"                : _( "Apus" ),
        "Aquila"              : _( "Aquila" ),
        "Aquarius"            : _( "Aquarius" ),
        "Ara"                 : _( "Ara" ),
        "Aries"               : _( "Aries" ),
        "Auriga"              : _( "Auriga" ),
        "Bootes"              : _( "Bootes" ),
        "Canis Major"         : _( "Canis Major" ),
        "Canis Minor"         : _( "Canis Minor" ),
        "Canes Venatici"      : _( "Canes Venatici" ),
        "Caelum"              : _( "Caelum" ),
        "Camelopardalis"      : _( "Camelopardalis" ),
        "Capricornus"         : _( "Capricornus" ),
        "Carina"              : _( "Carina" ),
        "Cassiopeia"          : _( "Cassiopeia" ),
        "Centaurus"           : _( "Centaurus" ),
        "Cepheus"             : _( "Cepheus" ),
        "Cetus"               : _( "Cetus" ),
        "Chamaeleon"          : _( "Chamaeleon" ),
        "Circinus"            : _( "Circinus" ),
        "Cancer"              : _( "Cancer" ),
        "Columba"             : _( "Columba" ),
        "Coma Berenices"      : _( "Coma Berenices" ),
        "Corona Australis"    : _( "Corona Australis" ),
        "Corona Borealis"     : _( "Corona Borealis" ),
        "Crater"              : _( "Crater" ),
        "Crux"                : _( "Crux" ),
        "Corvus"              : _( "Corvus" ),
        "Cygnus"              : _( "Cygnus" ),
        "Delphinus"           : _( "Delphinus" ),
        "Dorado"              : _( "Dorado" ),
        "Draco"               : _( "Draco" ),
        "Equuleus"            : _( "Equuleus" ),
        "Eridanus"            : _( "Eridanus" ),
        "Fornax"              : _( "Fornax" ),
        "Gemini"              : _( "Gemini" ),
        "Grus"                : _( "Grus" ),
        "Hercules"            : _( "Hercules" ),
        "Horologium"          : _( "Horologium" ),
        "Hydra"               : _( "Hydra" ),
        "Hydrus"              : _( "Hydrus" ),
        "Indus"               : _( "Indus" ),
        "Leo Minor"           : _( "Leo Minor" ),
        "Lacerta"             : _( "Lacerta" ),
        "Leo"                 : _( "Leo" ),
        "Lepus"               : _( "Lepus" ),
        "Libra"               : _( "Libra" ),
        "Lupus"               : _( "Lupus" ),
        "Lynx"                : _( "Lynx" ),
        "Lyra"                : _( "Lyra" ),
        "Mensa"               : _( "Mensa" ),
        "Microscopium"        : _( "Microscopium" ),
        "Monoceros"           : _( "Monoceros" ),
        "Musca"               : _( "Musca" ),
        "Norma"               : _( "Norma" ),
        "Octans"              : _( "Octans" ),
        "Ophiuchus"           : _( "Ophiuchus" ),
        "Orion"               : _( "Orion" ),
        "Pavo"                : _( "Pavo" ),
        "Pegasus"             : _( "Pegasus" ),
        "Perseus"             : _( "Perseus" ),
        "Phoenix"             : _( "Phoenix" ),
        "Pictor"              : _( "Pictor" ),
        "Piscis Austrinus"    : _( "Piscis Austrinus" ),
        "Pisces"              : _( "Pisces" ),
        "Puppis"              : _( "Puppis" ),
        "Pyxis"               : _( "Pyxis" ),
        "Reticulum"           : _( "Reticulum" ),
        "Sculptor"            : _( "Sculptor" ),
        "Scorpius"            : _( "Scorpius" ),
        "Scutum"              : _( "Scutum" ),
        "Serpens Caput"       : _( "Serpens Caput" ),
        "Sextans"             : _( "Sextans" ),
        "Sagitta"             : _( "Sagitta" ),
        "Sagittarius"         : _( "Sagittarius" ),
        "Taurus"              : _( "Taurus" ),
        "Telescopium"         : _( "Telescopium" ),
        "Triangulum Australe" : _( "Triangulum Australe" ),
        "Triangulum"          : _( "Triangulum" ),
        "Tucana"              : _( "Tucana" ),
        "Ursa Major"          : _( "Ursa Major" ),
        "Ursa Minor"          : _( "Ursa Minor" ),
        "Vela"                : _( "Vela" ),
        "Virgo"               : _( "Virgo" ),
        "Volans"              : _( "Volans" ),
        "Vulpecula"           : _( "Vulpecula" ),
        "Serpens Cauda"       : _( "Serpens Cauda" ) }

    MOON_TAG = "MOON"
    MOON_TAG_TRANSLATION = { MOON_TAG : _( "MOON" ) }

    SUN_TAG = "SUN"
    SUN_TAG_TRANSLATION = { SUN_TAG : _( "SUN" ) }

    PLANET_MERCURY = "Mercury"
    PLANET_VENUS = "Venus"
    PLANET_MARS = "Mars"
    PLANET_JUPITER = "Jupiter"
    PLANET_SATURN = "Saturn"
    PLANET_URANUS = "Uranus"
    PLANET_NEPTUNE = "Neptune"
    PLANET_PLUTO = "Pluto"

    MOON_JUPITER_CALLISTO = "Callisto"
    MOON_JUPITER_EUROPA = "Europa"
    MOON_JUPITER_GANYMEDE = "Ganymede"
    MOON_JUPITER_IO = "Io"

    MOON_MARS_DEIMOS = "Deimos"
    MOON_MARS_PHOBOS = "Phobos"

    MOON_SATURN_DIONE = "Dione"
    MOON_SATURN_ENCELADUS = "Enceladus"
    MOON_SATURN_HYPERION = "Hyperion"
    MOON_SATURN_IAPETUS = "Iapetus"
    MOON_SATURN_MIMAS = "Mimas"
    MOON_SATURN_RHEA = "Rhea"
    MOON_SATURN_TETHYS = "Tethys"
    MOON_SATURN_TITAN = "Titan"

    MOON_URANUS_ARIEL = "Ariel"
    MOON_URANUS_MIRANDA = "Miranda"
    MOON_URANUS_OBERON = "Oberon"
    MOON_URANUS_TITANIA = "Titania"
    MOON_URANUS_UMBRIEL = "Umbriel"

    PLANETS = [ PLANET_MERCURY, PLANET_VENUS, PLANET_MARS, PLANET_JUPITER, PLANET_SATURN, PLANET_URANUS, PLANET_NEPTUNE, PLANET_PLUTO ]

    PLANET_MOONS = { 
        PLANET_JUPITER : [ MOON_JUPITER_CALLISTO, MOON_JUPITER_EUROPA, MOON_JUPITER_GANYMEDE, MOON_JUPITER_IO ],
        PLANET_MARS : [ MOON_MARS_DEIMOS, MOON_MARS_PHOBOS ],
        PLANET_SATURN : [ MOON_SATURN_DIONE, MOON_SATURN_ENCELADUS, MOON_SATURN_HYPERION, MOON_SATURN_IAPETUS, MOON_SATURN_MIMAS, MOON_SATURN_RHEA, MOON_SATURN_TETHYS, MOON_SATURN_TITAN ],
        PLANET_URANUS : [ MOON_URANUS_ARIEL, MOON_URANUS_MIRANDA, MOON_URANUS_OBERON, MOON_URANUS_TITANIA, MOON_URANUS_UMBRIEL ] }

    PLANET_AND_MOON_NAMES = {
        PLANET_MERCURY        : _( "Mercury" ),
        PLANET_VENUS          : _( "Venus" ),
        PLANET_MARS           : _( "Mars" ),
        PLANET_JUPITER        : _( "Jupiter" ), 
        PLANET_SATURN         : _( "Saturn" ),
        PLANET_URANUS         : _( "Uranus" ),
        PLANET_NEPTUNE        : _( "Neptune" ),
        PLANET_PLUTO          : _( "Pluto" ),
    
        MOON_MARS_DEIMOS      : _( "Deimos" ),
        MOON_MARS_PHOBOS      : _( "Phobos" ),
    
        MOON_JUPITER_CALLISTO : _( "Callisto" ),
        MOON_JUPITER_EUROPA   : _( "Europa" ),
        MOON_JUPITER_GANYMEDE : _( "Ganymede" ),
        MOON_JUPITER_IO       : _( "Io" ),
    
        MOON_SATURN_DIONE     : _( "Dione" ),
        MOON_SATURN_ENCELADUS : _( "Enceladus" ),
        MOON_SATURN_HYPERION  : _( "Hyperion" ),
        MOON_SATURN_IAPETUS   : _( "Iapetus" ),
        MOON_SATURN_MIMAS     : _( "Mimas" ),
        MOON_SATURN_RHEA      : _( "Rhea" ),
        MOON_SATURN_TETHYS    : _( "Tethys" ),
        MOON_SATURN_TITAN     : _( "Titan" ),
    
        MOON_URANUS_ARIEL     : _( "Ariel" ),
        MOON_URANUS_MIRANDA   : _( "Miranda" ),
        MOON_URANUS_OBERON    : _( "Oberon" ),
        MOON_URANUS_TITANIA   : _( "Titania" ),
        MOON_URANUS_UMBRIEL   : _( "Umbriel" ) }

    PLANET_AND_MOON_TAGS = {
        "MERCURY"   : _( "MERCURY" ), 
        "VENUS"     : _( "VENUS" ), 
        "MARS"      : _( "MARS" ), 
        "JUPITER"   : _( "JUPITER" ), 
        "SATURN"    : _( "SATURN" ), 
        "URANUS"    : _( "URANUS" ), 
        "NEPTUNE"   : _( "NEPTUNE" ), 
        "PLUTO"     : _( "PLUTO" ), 

        "DEIMOS"    : _( "DEIMOS" ), 
        "PHOBOS"    : _( "PHOBOS" ), 

        "CALLISTO"  : _( "CALLISTO" ), 
        "EUROPA"    : _( "EUROPA" ), 
        "GANYMEDE"  : _( "GANYMEDE" ), 
        "IO"        : _( "IO" ), 

        "DIONE"     : _( "DIONE" ), 
        "ENCELADUS" : _( "ENCELADUS" ), 
        "HYPERION"  : _( "HYPERION" ), 
        "IAPETUS"   : _( "IAPETUS" ), 
        "MIMAS"     : _( "MIMAS" ), 
        "RHEA"      : _( "RHEA" ), 
        "TETHYS"    : _( "TETHYS" ), 
        "TITAN"     : _( "TITAN" ), 

        "ARIEL"     : _( "ARIEL" ), 
        "MIRANDA"   : _( "MIRANDA" ), 
        "OBERON"    : _( "OBERON" ), 
        "TITANIA"   : _( "TITANIA" ), 
        "UMBRIEL"   : _( "UMBRIEL" ) }

    # Translated star names.
    # Sourced from cns_namemap in ephem.stars.stars
    STAR_NAMES = {
        "Achernar"        : _( "Achernar" ), 
        "Adara"           : _( "Adara" ), 
        "Agena"           : _( "Agena" ), 
        "Albereo"         : _( "Albereo" ), 
        "Alcaid"          : _( "Alcaid" ), 
        "Alcor"           : _( "Alcor" ), 
        "Alcyone"         : _( "Alcyone" ), 
        "Aldebaran"       : _( "Aldebaran" ), 
        "Alderamin"       : _( "Alderamin" ), 
        "Alfirk"          : _( "Alfirk" ), 
        "Algenib"         : _( "Algenib" ), 
        "Algieba"         : _( "Algieba" ), 
        "Algol"           : _( "Algol" ), 
        "Alhena"          : _( "Alhena" ), 
        "Alioth"          : _( "Alioth" ), 
        "Almach"          : _( "Almach" ), 
        "Alnair"          : _( "Alnair" ), 
        "Alnilam"         : _( "Alnilam" ), 
        "Alnitak"         : _( "Alnitak" ), 
        "Alphard"         : _( "Alphard" ), 
        "Alphecca"        : _( "Alphecca" ), 
        "Alshain"         : _( "Alshain" ), 
        "Altair"          : _( "Altair" ), 
        "Antares"         : _( "Antares" ), 
        "Arcturus"        : _( "Arcturus" ), 
        "Arkab Posterior" : _( "Arkab Posterior" ), 
        "Arkab Prior"     : _( "Arkab Prior" ), 
        "Arneb"           : _( "Arneb" ), 
        "Atlas"           : _( "Atlas" ), 
        "Bellatrix"       : _( "Bellatrix" ), 
        "Betelgeuse"      : _( "Betelgeuse" ), 
        "Canopus"         : _( "Canopus" ), 
        "Capella"         : _( "Capella" ), 
        "Caph"            : _( "Caph" ), 
        "Castor"          : _( "Castor" ), 
        "Cebalrai"        : _( "Cebalrai" ), 
        "Deneb"           : _( "Deneb" ), 
        "Denebola"        : _( "Denebola" ), 
        "Dubhe"           : _( "Dubhe" ), 
        "Electra"         : _( "Electra" ), 
        "Elnath"          : _( "Elnath" ), 
        "Enif"            : _( "Enif" ), 
        "Etamin"          : _( "Etamin" ), 
        "Fomalhaut"       : _( "Fomalhaut" ), 
        "Gienah Corvi"    : _( "Gienah Corvi" ), 
        "Hamal"           : _( "Hamal" ), 
        "Izar"            : _( "Izar" ), 
        "Kaus Australis"  : _( "Kaus Australis" ), 
        "Kochab"          : _( "Kochab" ), 
        "Maia"            : _( "Maia" ), 
        "Markab"          : _( "Markab" ), 
        "Megrez"          : _( "Megrez" ), 
        "Menkalinan"      : _( "Menkalinan" ), 
        "Menkar"          : _( "Menkar" ), 
        "Merak"           : _( "Merak" ), 
        "Merope"          : _( "Merope" ), 
        "Mimosa"          : _( "Mimosa" ), 
        "Minkar"          : _( "Minkar" ), 
        "Mintaka"         : _( "Mintaka" ), 
        "Mirach"          : _( "Mirach" ), 
        "Mirzam"          : _( "Mirzam" ), 
        "Mizar"           : _( "Mizar" ), 
        "Naos"            : _( "Naos" ), 
        "Nihal"           : _( "Nihal" ), 
        "Nunki"           : _( "Nunki" ), 
        "Peacock"         : _( "Peacock" ), 
        "Phecda"          : _( "Phecda" ), 
        "Polaris"         : _( "Polaris" ), 
        "Pollux"          : _( "Pollux" ), 
        "Procyon"         : _( "Procyon" ), 
        "Rasalgethi"      : _( "Rasalgethi" ), 
        "Rasalhague"      : _( "Rasalhague" ), 
        "Regulus"         : _( "Regulus" ), 
        "Rigel"           : _( "Rigel" ), 
        "Rukbat"          : _( "Rukbat" ), 
        "Sadalmelik"      : _( "Sadalmelik" ), 
        "Sadr"            : _( "Sadr" ), 
        "Saiph"           : _( "Saiph" ), 
        "Scheat"          : _( "Scheat" ), 
        "Schedar"         : _( "Schedar" ), 
        "Shaula"          : _( "Shaula" ), 
        "Sheliak"         : _( "Sheliak" ), 
        "Sirius"          : _( "Sirius" ), 
        "Sirrah"          : _( "Sirrah" ), 
        "Spica"           : _( "Spica" ), 
        "Sulafat"         : _( "Sulafat" ), 
        "Tarazed"         : _( "Tarazed" ), 
        "Taygeta"         : _( "Taygeta" ), 
        "Thuban"          : _( "Thuban" ), 
        "Unukalhai"       : _( "Unukalhai" ), 
        "Vega"            : _( "Vega" ), 
        "Vindemiatrix"    : _( "Vindemiatrix" ), 
        "Wezen"           : _( "Wezen" ), 
        "Zaurak"          : _( "Zaurak" ) }

    # Data tag star names.
    # Sourced from cns_namemap in ephem.stars.stars
    STAR_TAGS = {
        "ACHERNAR"        : _( "ACHERNAR" ), 
        "ADARA"           : _( "ADARA" ), 
        "AGENA"           : _( "AGENA" ), 
        "ALBEREO"         : _( "ALBEREO" ), 
        "ALCAID"          : _( "ALCAID" ), 
        "ALCOR"           : _( "ALCOR" ), 
        "ALCYONE"         : _( "ALCYONE" ), 
        "ALDEBARAN"       : _( "ALDEBARAN" ), 
        "ALDERAMIN"       : _( "ALDERAMIN" ), 
        "ALFIRK"          : _( "ALFIRK" ), 
        "ALGENIB"         : _( "ALGENIB" ), 
        "ALGIEBA"         : _( "ALGIEBA" ), 
        "ALGOL"           : _( "ALGOL" ), 
        "ALHENA"          : _( "ALHENA" ), 
        "ALIOTH"          : _( "ALIOTH" ), 
        "ALMACH"          : _( "ALMACH" ), 
        "ALNAIR"          : _( "ALNAIR" ), 
        "ALNILAM"         : _( "ALNILAM" ), 
        "ALNITAK"         : _( "ALNITAK" ), 
        "ALPHARD"         : _( "ALPHARD" ), 
        "ALPHECCA"        : _( "ALPHECCA" ), 
        "ALSHAIN"         : _( "ALSHAIN" ), 
        "ALTAIR"          : _( "ALTAIR" ), 
        "ANTARES"         : _( "ANTARES" ), 
        "ARCTURUS"        : _( "ARCTURUS" ), 
        "ARKAB POSTERIOR" : _( "ARKAB POSTERIOR" ), 
        "ARKAB PRIOR"     : _( "ARKAB PRIOR" ), 
        "ARNEB"           : _( "ARNEB" ), 
        "ATLAS"           : _( "ATLAS" ), 
        "BELLATRIX"       : _( "BELLATRIX" ), 
        "BETELGEUSE"      : _( "BETELGEUSE" ), 
        "CANOPUS"         : _( "CANOPUS" ), 
        "CAPELLA"         : _( "CAPELLA" ), 
        "CAPH"            : _( "CAPH" ), 
        "CASTOR"          : _( "CASTOR" ), 
        "CEBALRAI"        : _( "CEBALRAI" ), 
        "DENEB"           : _( "DENEB" ), 
        "DENEBOLA"        : _( "DENEBOLA" ), 
        "DUBHE"           : _( "DUBHE" ), 
        "ELECTRA"         : _( "ELECTRA" ), 
        "ELNATH"          : _( "ELNATH" ), 
        "ENIF"            : _( "ENIF" ), 
        "ETAMIN"          : _( "ETAMIN" ), 
        "FOMALHAUT"       : _( "FOMALHAUT" ), 
        "GIENAH CORVI"    : _( "GIENAH CORVI" ), 
        "HAMAL"           : _( "HAMAL" ), 
        "IZAR"            : _( "IZAR" ), 
        "KAUS AUSTRALIS"  : _( "KAUS AUSTRALIS" ), 
        "KOCHAB"          : _( "KOCHAB" ), 
        "MAIA"            : _( "MAIA" ), 
        "MARKAB"          : _( "MARKAB" ), 
        "MEGREZ"          : _( "MEGREZ" ), 
        "MENKALINAN"      : _( "MENKALINAN" ), 
        "MENKAR"          : _( "MENKAR" ), 
        "MERAK"           : _( "MERAK" ), 
        "MEROPE"          : _( "MEROPE" ), 
        "MIMOSA"          : _( "MIMOSA" ), 
        "MINKAR"          : _( "MINKAR" ), 
        "MINTAKA"         : _( "MINTAKA" ), 
        "MIRACH"          : _( "MIRACH" ), 
        "MIRZAM"          : _( "MIRZAM" ), 
        "MIZAR"           : _( "MIZAR" ), 
        "NAOS"            : _( "NAOS" ), 
        "NIHAL"           : _( "NIHAL" ), 
        "NUNKI"           : _( "NUNKI" ), 
        "PEACOCK"         : _( "PEACOCK" ), 
        "PHECDA"          : _( "PHECDA" ), 
        "POLARIS"         : _( "POLARIS" ), 
        "POLLUX"          : _( "POLLUX" ), 
        "PROCYON"         : _( "PROCYON" ), 
        "RASALGETHI"      : _( "RASALGETHI" ), 
        "RASALHAGUE"      : _( "RASALHAGUE" ), 
        "REGULUS"         : _( "REGULUS" ), 
        "RIGEL"           : _( "RIGEL" ), 
        "RUKBAT"          : _( "RUKBAT" ), 
        "SADALMELIK"      : _( "SADALMELIK" ), 
        "SADR"            : _( "SADR" ), 
        "SAIPH"           : _( "SAIPH" ), 
        "SCHEAT"          : _( "SCHEAT" ), 
        "SCHEDAR"         : _( "SCHEDAR" ), 
        "SHAULA"          : _( "SHAULA" ), 
        "SHELIAK"         : _( "SHELIAK" ), 
        "SIRIUS"          : _( "SIRIUS" ), 
        "SIRRAH"          : _( "SIRRAH" ), 
        "SPICA"           : _( "SPICA" ), 
        "SULAFAT"         : _( "SULAFAT" ), 
        "TARAZED"         : _( "TARAZED" ), 
        "TAYGETA"         : _( "TAYGETA" ), 
        "THUBAN"          : _( "THUBAN" ), 
        "UNUKALHAI"       : _( "UNUKALHAI" ), 
        "VEGA"            : _( "VEGA" ), 
        "VINDEMIATRIX"    : _( "VINDEMIATRIX" ), 
        "WEZEN"           : _( "WEZEN" ), 
        "ZAURAK"          : _( "ZAURAK" ) }

    BODY_TAGS = dict(
        list( PLANET_AND_MOON_TAGS.items() ) + 
        list( STAR_TAGS.items() ) + 
        list( MOON_TAG_TRANSLATION.items() )+ 
        list( SUN_TAG_TRANSLATION.items() ) )

    LUNAR_PHASE_FULL_MOON = "FULL_MOON"
    LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
    LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
    LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
    LUNAR_PHASE_NEW_MOON = "NEW_MOON"
    LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
    LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
    LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"

    LUNAR_PHASE_NAMES = {
        LUNAR_PHASE_FULL_MOON       : _( "Full Moon" ),
        LUNAR_PHASE_WANING_GIBBOUS  : _( "Waning Gibbous" ),
        LUNAR_PHASE_THIRD_QUARTER   : _( "Third Quarter" ),
        LUNAR_PHASE_WANING_CRESCENT : _( "Waning Crescent" ),
        LUNAR_PHASE_NEW_MOON        : _( "New Moon" ),
        LUNAR_PHASE_WAXING_CRESCENT : _( "Waxing Crescent" ),
        LUNAR_PHASE_FIRST_QUARTER   : _( "First Quarter" ),
        LUNAR_PHASE_WAXING_GIBBOUS  : _( "Waxing Gibbous" )
    }

    ORBITAL_ELEMENT_DATA_URL = "http://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt"

    SATELLITE_TAG_NAME = "[NAME]"
    SATELLITE_TAG_NUMBER = "[NUMBER]"
    SATELLITE_TAG_INTERNATIONAL_DESIGNATOR = "[INTERNATIONAL DESIGNATOR]"
    SATELLITE_TAG_RISE_AZIMUTH = "[RISE AZIMUTH]"
    SATELLITE_TAG_RISE_TIME = "[RISE TIME]"
    SATELLITE_TAG_SET_AZIMUTH = "[SET AZIMUTH]"
    SATELLITE_TAG_SET_TIME = "[SET TIME]"
    SATELLITE_TAG_VISIBLE = "[VISIBLE]"

    SATELLITE_TLE_URL = "http://celestrak.com/NORAD/elements/visual.txt"
    SATELLITE_ON_CLICK_URL = "http://www.n2yo.com/satellite/?s=" + SATELLITE_TAG_NUMBER

    SATELLITE_MENU_TEXT_DEFAULT = SATELLITE_TAG_NAME + " - " + SATELLITE_TAG_NUMBER
    SATELLITE_NOTIFICATION_SUMMARY_DEFAULT = SATELLITE_TAG_NAME + " : " + SATELLITE_TAG_NUMBER + " : " + SATELLITE_TAG_INTERNATIONAL_DESIGNATOR
    SATELLITE_NOTIFICATION_MESSAGE_DEFAULT = \
        "Rise Time: " + SATELLITE_TAG_RISE_TIME + \
        "\nRise Azimuth: " + SATELLITE_TAG_RISE_AZIMUTH + \
        "\nSet Time: " + SATELLITE_TAG_SET_TIME + \
        "\nSet Azimuth: " + SATELLITE_TAG_SET_AZIMUTH

    WEREWOLF_WARNING_MESSAGE_DEFAULT = _( "                                          ...werewolves about ! ! !" )
    WEREWOLF_WARNING_SUMMARY_DEFAULT = _( "W  A  R  N  I  N  G" )

    INDICATOR_TEXT_DEFAULT = "[" + MOON_TAG + " " + DATA_PHASE + "]"

    MESSAGE_BODY_ALWAYS_UP = _( "Always Up!" )
    MESSAGE_BODY_NEVER_UP = _( "Never Up!" )
    MESSAGE_ORBITAL_ELEMENT_NO_DATA = _( "No orbital element data!" )
    MESSAGE_SATELLITE_IS_CIRCUMPOLAR = _( "Satellite is circumpolar." )
    MESSAGE_SATELLITE_NEVER_RISES = _( "Satellite never rises." )
    MESSAGE_SATELLITE_NO_PASSES_WITHIN_NEXT_TEN_DAYS = _( "No passes within the next 10 days." )
    MESSAGE_SATELLITE_NO_TLE_DATA = _( "No TLE data!" )
    MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS = _( "Unable to compute next pass!" )
    MESSAGE_SATELLITE_VALUE_ERROR = _( "ValueError" )


    def __init__( self ):
        self.dialog = None
        self.data = { } # Key is each a data tag, upper case, naming the type of data combined with the source of the data; value is the data ready for display.
        self.orbitalElementData = { } # Key is the orbital element name, upper cased; value is the orbital element data string.
        self.satelliteNotifications = { }
        self.satelliteTLEData = { }

        self.toggleOrbitalElementsTable = False
        self.togglePlanetsTable = False
        self.toggleSatellitesTable = False
        self.toggleStarsTable = False

        GObject.threads_init()
        self.lock = threading.Lock()

        filehandler = pythonutils.TruncatedFileHandler( IndicatorLunar.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )
        Notify.init( INDICATOR_NAME )

        self.lastUpdateOrbitalElement = datetime.datetime.now() - datetime.timedelta( hours = 24 ) # Set the last orbital element update in the past so an update occurs. 
        self.lastUpdateTLE = datetime.datetime.now() - datetime.timedelta( hours = 24 ) # Set the last TLE update in the past so an update occurs. 
        self.lastFullMoonNotfication = ephem.Date( "2000/01/01" ) # Set a date way back in the past...

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, "", AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_icon_theme_path( tempfile.gettempdir() )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

        self.loadSettings()
        self.update()


    def main( self ): Gtk.main()


    def update( self ): Thread( target = self.updateBackend ).start()


    def updateBackend( self ):
        if not self.lock.acquire( False ): return

        self.toggleIconState()
        self.updateOrbitalElementData()
        self.updateSatelliteTLEData()

        # Reset data on each update...
        self.data = { } # Must reset the data on each update, otherwise data will accumulate (if a planet/star/satellite was added then removed, the computed data remains).
        self.data[ ( "", IndicatorLunar.DATA_CITY_NAME ) ] = self.cityName # Need to add a dummy "" as a second element to the list to match the format of all other data.
        self.nextUpdates = [ ] # Stores the date/time for each upcoming rise/set/phase...used to find the date/time closest to now and that will be the next time for an update.

        ephemNow = ephem.now() # UTC, used in all calculations.  When it comes time to display, conversion to local time takes place.

        lunarIlluminationPercentage = int( round( ephem.Moon( self.getCity( ephemNow ) ).phase ) )
        lunarPhase = self.getLunarPhase( ephemNow, lunarIlluminationPercentage )

        self.updateMoon( ephemNow, lunarPhase )
        self.updateSun( ephemNow )
        self.updatePlanets( ephemNow )
        self.updateStars( ephemNow )
        self.updateOrbitalElements( ephemNow )
        self.updateSatellites( ephemNow ) 

        GLib.idle_add( self.updateFrontend, ephemNow, lunarPhase, lunarIlluminationPercentage )


    def updateFrontend( self, ephemNow, lunarPhase, lunarIlluminationPercentage ):
        self.updateMenu( ephemNow, lunarPhase )
        self.updateIcon( ephemNow, lunarIlluminationPercentage )
        self.fullMoonNotification( ephemNow, lunarPhase, lunarIlluminationPercentage )
        self.satelliteNotification( ephemNow )

        self.nextUpdates.sort()
        nextUpdateInSeconds = int( ( ephem.localtime( self.nextUpdates[ 0 ] ) - ephem.localtime( ephemNow ) ).total_seconds() )

        # Ensure the update period is positive, at most every minute and at least every hour.
        if nextUpdateInSeconds < 60:
            nextUpdateInSeconds = 60
        elif nextUpdateInSeconds > ( 60 * 60 ):
            nextUpdateInSeconds = ( 60 * 60 )

        self.eventSourceID = GLib.timeout_add_seconds( nextUpdateInSeconds, self.update )
        self.lock.release()


    def updateMenu( self, ephemNow, lunarPhase ):
        menu = Gtk.Menu()

        self.updateMoonMenu( menu )
        self.updateSunMenu( menu )
        self.updatePlanetsMenu( menu )
        self.updateStarsMenu( menu )
        self.updateOrbitalElementsMenu( menu )
        self.updateSatellitesMenu( menu )

        menu.append( Gtk.SeparatorMenuItem() )

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
        menuItem.connect( "activate", self.onPreferences )
        menu.append( menuItem )

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        menuItem.connect( "activate", self.onAbout )
        menu.append( menuItem )

        menuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        menuItem.connect( "activate", Gtk.main_quit )
        menu.append( menuItem )

        self.indicator.set_menu( menu )
        menu.show_all()


    def updateIcon( self, ephemNow, lunarIlluminationPercentage ):
        parsedOutput = self.indicatorText
        for key in self.data.keys():
            parsedOutput = parsedOutput.replace( "[" + " ".join( key ) + "]", self.data[ key ] )

        self.createIcon( lunarIlluminationPercentage, self.getBrightLimbAngleRelativeToZenith( self.getCity( ephemNow ), ephem.Moon( self.getCity( ephemNow ) ) ) )
        self.indicator.set_icon( self.getIconName() )
        self.indicator.set_label( parsedOutput, "" ) # Second parameter is a label-guide: http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html


    def fullMoonNotification( self, ephemNow, lunarPhase, lunarIlluminationPercentage ):
        if not self.showWerewolfWarning: return

        if lunarIlluminationPercentage < self.werewolfWarningStartIlluminationPercentage: return

        if ( ephem.Date( self.lastFullMoonNotfication + ephem.hour ) > ephemNow ): return

        phaseIsBetweenNewAndFullInclusive = ( lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON )

        if not phaseIsBetweenNewAndFullInclusive: return

        summary = self.werewolfWarningSummary
        if self.werewolfWarningSummary == "":
            summary = " " # The notification summary text cannot be empty (at least on Unity).

        Notify.Notification.new( summary, self.werewolfWarningMessage, self.getIconFile() ).show()
        self.lastFullMoonNotfication = ephemNow


    def satelliteNotification( self, ephemNow ):
        if not self.showSatelliteNotification: return

        # Create a list of satellite name/number and rise times to then either sort by name/number or rise time.
        satelliteNameNumberRiseTimes = [ ]
        for key in self.satellites:
            if ( key + ( IndicatorLunar.DATA_RISE_TIME, ) ) in self.data: # Assume all other information is present!
                satelliteNameNumberRiseTimes.append( [ key, self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] ] )

        if self.satellitesSortByDateTime:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 1 ], x[ 0 ] ) )
        else:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 0 ], x[ 1 ] ) )

        ephemNowInLocalTime = ephem.Date( self.localiseAndTrim( ephemNow ) )
        for key, riseTime in satelliteNameNumberRiseTimes:

            # Ensure the current time is within the rise/set...
            if ephemNowInLocalTime < ephem.Date( self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] ) or \
               ephemNowInLocalTime > ephem.Date( self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] ): continue

            # Show the notification for the particular satellite only once per pass...
            if key in self.satelliteNotifications and ephemNowInLocalTime < ephem.Date( self.satelliteNotifications[ key ] ):
                continue

            self.satelliteNotifications[ key ] = self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] # Ensures the notification happens once per satellite pass.

            # Parse the satellite summary/message to create the notification...
            riseTime = self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ]
            degreeSymbolIndex = self.data[ key + ( IndicatorLunar.DATA_RISE_AZIMUTH, ) ].index( "°" )
            riseAzimuth = self.data[ key + ( IndicatorLunar.DATA_RISE_AZIMUTH, ) ][ 0 : degreeSymbolIndex + 1 ]

            setTime = self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ]
            degreeSymbolIndex = self.data[ key + ( IndicatorLunar.DATA_SET_AZIMUTH, ) ].index( "°" )
            setAzimuth = self.data[ key + ( IndicatorLunar.DATA_SET_AZIMUTH, ) ][ 0 : degreeSymbolIndex + 1 ]

            tle = self.satelliteTLEData[ key ]
            summary = self.satelliteNotificationSummary. \
                replace( IndicatorLunar.SATELLITE_TAG_NAME, tle.getName() ). \
                replace( IndicatorLunar.SATELLITE_TAG_NUMBER, key[ 1 ] ). \
                replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, tle.getInternationalDesignator() ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME, riseTime ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME, setTime ). \
                replace( IndicatorLunar.SATELLITE_TAG_VISIBLE, self.data[ key + ( IndicatorLunar.DATA_VISIBLE, ) ] )

            if summary == "": summary = " " # The notification summary text must not be empty (at least on Unity).

            message = self.satelliteNotificationMessage. \
                replace( IndicatorLunar.SATELLITE_TAG_NAME, tle.getName() ). \
                replace( IndicatorLunar.SATELLITE_TAG_NUMBER, key[ 1 ] ). \
                replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, tle.getInternationalDesignator() ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME, riseTime ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME, setTime ). \
                replace( IndicatorLunar.SATELLITE_TAG_VISIBLE, self.data[ key + ( IndicatorLunar.DATA_VISIBLE, ) ] )

            Notify.Notification.new( summary, message, IndicatorLunar.SVG_SATELLITE_ICON ).show()


    def updateMoonMenu( self, menu ):
        if ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_MESSAGE ) in self.data or \
           ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_RISE_TIME ) in self.data:

            menuItem = Gtk.MenuItem( _( "Moon" ) )
            menu.append( menuItem )

            self.updateCommonMenu( menuItem, AstronomicalObjectType.Moon, IndicatorLunar.MOON_TAG )
            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )

            menuItem.get_submenu().append( Gtk.MenuItem( _( "Phase: " ) + self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_PHASE ) ] ) )

            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
            menuItem.get_submenu().append( Gtk.MenuItem( _( "Next Phases" ) ) )

            # Determine which phases occur by date rather than using the phase calculated.
            # The phase (illumination) rounds numbers and so a given phase is entered earlier than what is correct.
            nextPhases = [ ]
            nextPhases.append( [ self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_FIRST_QUARTER ) ], _( "First Quarter: " ) ] )
            nextPhases.append( [ self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_FULL ) ], _( "Full: " ) ] )
            nextPhases.append( [ self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_THIRD_QUARTER ) ], _( "Third Quarter: " ) ] )
            nextPhases.append( [ self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_NEW ) ], _( "New: " ) ] )

            nextPhases = sorted( nextPhases, key = lambda tuple: tuple[ 0 ] )
            for phaseInformation in nextPhases:
                menuItem.get_submenu().append( Gtk.MenuItem( IndicatorLunar.INDENT + phaseInformation[ 1 ] + phaseInformation[ 0 ] ) )

            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
            self.updateEclipseMenu( menuItem.get_submenu(), IndicatorLunar.MOON_TAG )


    def updateSunMenu( self, menu ):
        if ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_MESSAGE ) in self.data or \
           ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_RISE_TIME ) in self.data:
            menuItem = Gtk.MenuItem( _( "Sun" ) )
            menu.append( menuItem )

            self.updateCommonMenu( menuItem, AstronomicalObjectType.Sun, IndicatorLunar.SUN_TAG )
            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )

            # Solstice/Equinox.
            equinox = self.data[ ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_EQUINOX ) ]
            solstice = self.data[ ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_SOLSTICE ) ]
            if equinox < solstice:
                menuItem.get_submenu().append( Gtk.MenuItem( _( "Equinox: " ) + equinox ) )
                menuItem.get_submenu().append( Gtk.MenuItem( _( "Solstice: " ) + solstice ) )
            else:
                menuItem.get_submenu().append( Gtk.MenuItem( _( "Solstice: " ) + solstice ) )
                menuItem.get_submenu().append( Gtk.MenuItem( _( "Equinox: " ) + equinox ) )

            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
            self.updateEclipseMenu( menuItem.get_submenu(), IndicatorLunar.SUN_TAG )


    def updatePlanetsMenu( self, menu ):
        planets = [ ]
        for planetName in self.planets:
            dataTag = planetName.upper()
            if ( dataTag, IndicatorLunar.DATA_MESSAGE ) in self.data or \
               ( dataTag, IndicatorLunar.DATA_RISE_TIME ) in self.data:
                planets.append( planetName )

        if len( planets ) > 0:
            menuItem = Gtk.MenuItem( _( "Planets" ) )
            menu.append( menuItem )

            if self.showPlanetsAsSubMenu:
                subMenu = Gtk.Menu()
                menuItem.set_submenu( subMenu )

            for planetName in planets:
                dataTag = planetName.upper()
                if self.showPlanetsAsSubMenu:
                    menuItem = Gtk.MenuItem( IndicatorLunar.PLANET_AND_MOON_NAMES[ planetName ] )
                    subMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + IndicatorLunar.PLANET_AND_MOON_NAMES[ planetName ] )
                    menu.append( menuItem )

                self.updateCommonMenu( menuItem, AstronomicalObjectType.Planet, dataTag )

                # Update moons.
                if planetName in IndicatorLunar.PLANET_MOONS:
                    menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
                    menuItem.get_submenu().append( Gtk.MenuItem( _( "Major Moons" ) ) )
                    self.updatePlanetMoonsMenu( menuItem, IndicatorLunar.PLANET_MOONS[ planetName ] )


    def updatePlanetMoonsMenu( self, menuItem, moonNames ):
        for moonName in moonNames:
            moonMenuItem = Gtk.MenuItem( IndicatorLunar.INDENT + IndicatorLunar.PLANET_AND_MOON_NAMES[ moonName ] )
            menuItem.get_submenu().append( moonMenuItem )

            dataTag = moonName.upper()
            subMenu = Gtk.Menu()
            self.updateRightAscensionDeclinationAzimuthAltitudeMenu( subMenu, dataTag )
            subMenu.append( Gtk.SeparatorMenuItem() )

            subMenu.append( Gtk.MenuItem( _( "Earth Visible: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_EARTH_VISIBLE ) ] ) )
            subMenu.append( Gtk.SeparatorMenuItem() )

            subMenu.append( Gtk.MenuItem( _( "Offset from Planet (in planet radii)" ) ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "X: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_X_OFFSET ) ] ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Y: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_Y_OFFSET ) ] ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Z: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_Z_OFFSET ) ] ) )

            moonMenuItem.set_submenu( subMenu )


    def updateStarsMenu( self, menu ):
        stars = [ ] # List of lists.  Each sublist contains the star name followed by the translated name.
        for starName in self.stars:
            dataTag = starName.upper()
            if ( dataTag, IndicatorLunar.DATA_MESSAGE ) in self.data or \
               ( dataTag, IndicatorLunar.DATA_RISE_TIME ) in self.data:
                stars.append( [ starName, IndicatorLunar.STAR_NAMES[ starName ] ] )

        if len( stars ) > 0:
            menuItem = Gtk.MenuItem( _( "Stars" ) )
            menu.append( menuItem )

            if self.showStarsAsSubMenu:
                subMenu = Gtk.Menu()
                menuItem.set_submenu( subMenu )

            stars = sorted( stars, key = lambda x: ( x[ 1 ] ) )
            for starName, starNameTranslated in stars:
                dataTag = starName.upper()
                if self.showStarsAsSubMenu:
                    menuItem = Gtk.MenuItem( starNameTranslated )
                    subMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + starNameTranslated )
                    menu.append( menuItem )

                self.updateCommonMenu( menuItem, AstronomicalObjectType.Star, dataTag )


    def updateOrbitalElementsMenu( self, menu ):
        orbitalElements = [ ]
        for key in self.orbitalElements:
            if ( key, IndicatorLunar.DATA_MESSAGE ) in self.data or \
               ( key, IndicatorLunar.DATA_RISE_TIME ) in self.data:
                orbitalElements.append( key )

        if len( orbitalElements ) > 0:
            menuItem = Gtk.MenuItem( _( "Orbital Elements" ) )
            menu.append( menuItem )

            if self.showOrbitalElementsAsSubMenu:
                orbitalElementsSubMenu = Gtk.Menu()
                menuItem.set_submenu( orbitalElementsSubMenu )

            for key in sorted( orbitalElements ): # Fortunately sorting by key also sorts the display name identically!
                displayName = self.getOrbitalElementDisplayName( self.orbitalElementData[ key ] )
                if self.showOrbitalElementsAsSubMenu:
                    menuItem = Gtk.MenuItem( displayName )
                    orbitalElementsSubMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + displayName )
                    menu.append( menuItem )

                self.updateCommonMenu( menuItem, AstronomicalObjectType.OrbitalElement, key )


    def updateCommonMenu( self, menuItem, astronomicalObjectType, dataTag ):
        subMenu = Gtk.Menu()

        if astronomicalObjectType == AstronomicalObjectType.Moon or astronomicalObjectType == AstronomicalObjectType.Planet:
            subMenu.append( Gtk.MenuItem( _( "Illumination: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_ILLUMINATION ) ] ) )

        subMenu.append( Gtk.MenuItem( _( "Constellation: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_CONSTELLATION ) ] ) )
        subMenu.append( Gtk.MenuItem( _( "Magnitude: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_MAGNITUDE ) ] ) )

        if astronomicalObjectType == AstronomicalObjectType.Moon or \
           astronomicalObjectType == AstronomicalObjectType.Planet or \
           astronomicalObjectType == AstronomicalObjectType.Star or \
           astronomicalObjectType == AstronomicalObjectType.Sun:
            subMenu.append( Gtk.MenuItem( _( "Tropical Sign: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_TROPICAL_SIGN ) ] ) )

        if astronomicalObjectType == AstronomicalObjectType.Moon or \
           astronomicalObjectType == AstronomicalObjectType.OrbitalElement or \
           astronomicalObjectType == AstronomicalObjectType.Planet or \
           astronomicalObjectType == AstronomicalObjectType.Sun:
            subMenu.append( Gtk.MenuItem( _( "Distance to Earth: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_DISTANCE_TO_EARTH ) ] ) )

        if astronomicalObjectType == AstronomicalObjectType.Moon or \
           astronomicalObjectType == AstronomicalObjectType.OrbitalElement or \
           astronomicalObjectType == AstronomicalObjectType.Planet:
            subMenu.append( Gtk.MenuItem( _( "Distance to Sun: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_DISTANCE_TO_SUN ) ] ) )

        if astronomicalObjectType == AstronomicalObjectType.Moon or astronomicalObjectType == AstronomicalObjectType.Planet:            
            subMenu.append( Gtk.MenuItem( _( "Bright Limb: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_BRIGHT_LIMB ) ] ) )

        subMenu.append( Gtk.SeparatorMenuItem() )

        self.updateRightAscensionDeclinationAzimuthAltitudeMenu( subMenu, dataTag )

        subMenu.append( Gtk.SeparatorMenuItem() )

        if ( dataTag, IndicatorLunar.DATA_MESSAGE ) in self.data:
            subMenu.append( Gtk.MenuItem( self.data[ ( dataTag, IndicatorLunar.DATA_MESSAGE ) ] ) )
        else:
            data = [ ]
            data.append( [ self.data[ ( dataTag, IndicatorLunar.DATA_RISE_TIME ) ], _( "Rise: " ) ] )
            data.append( [ self.data[ ( dataTag, IndicatorLunar.DATA_SET_TIME ) ], _( "Set: " ) ] )

            if astronomicalObjectType == AstronomicalObjectType.Sun:
                data.append( [ self.data[ ( dataTag, IndicatorLunar.DATA_DAWN ) ], _( "Dawn: " ) ] )
                data.append( [ self.data[ ( dataTag, IndicatorLunar.DATA_DUSK ) ], _( "Dusk: " ) ] )

            data = sorted( data, key = lambda x: ( x[ 0 ] ) )

            for dateTime, text in data:
                subMenu.append( Gtk.MenuItem( text + dateTime ) )

        menuItem.set_submenu( subMenu )


    def updateSatellitesMenu( self, menu ):
        # For each satellite, first determine if there is calculated data present (may have been dropped).
        # Then, parse the menu text to replace tags with values.
        # Then, build a list of satellites, including rise time (or message), to allow sorting.
        menuTextSatelliteNameNumberRiseTimes = [ ]
        for key in self.satellites: # key is satellite name/number.
            if key not in self.satelliteTLEData:
                continue # This is (likely) a satellite from a previous run which is not in the current TLE data.

            if ( key + ( IndicatorLunar.DATA_MESSAGE, ) ) not in self.data and \
               ( key + ( IndicatorLunar.DATA_RISE_TIME, ) ) not in self.data:
                continue # No data for this satellite - likely it has been dropped by the backend. 

            tle = self.satelliteTLEData[ key ]
            menuText = self.satelliteMenuText.replace( IndicatorLunar.SATELLITE_TAG_NAME, tle.getName() ) \
                                             .replace( IndicatorLunar.SATELLITE_TAG_NUMBER, tle.getNumber() ) \
                                             .replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, tle.getInternationalDesignator() )

            # Add in the rise time to allow sorting by rise time.
            # If there is a message present, then no rise time will exist (so add the message in lieu of the rise time).
            # The (text) message gets sorted after the (numeric) rise time.
            if ( key + ( IndicatorLunar.DATA_MESSAGE, ) ) in self.data:
                riseTime = self.data[ ( key + ( IndicatorLunar.DATA_MESSAGE, ) ) ]
            else:
                riseTime = self.data[ ( key + ( IndicatorLunar.DATA_RISE_TIME, ) ) ]

            menuTextSatelliteNameNumberRiseTimes.append( [ menuText, key, riseTime ] )

        if len( menuTextSatelliteNameNumberRiseTimes ) > 0:
            if self.satellitesSortByDateTime: # Sort by menu text or by rise time...
                menuTextSatelliteNameNumberRiseTimes = sorted( menuTextSatelliteNameNumberRiseTimes, key = lambda x: ( x[ 2 ], x[ 0 ], x[ 1 ] ) )
            else:
                menuTextSatelliteNameNumberRiseTimes = sorted( menuTextSatelliteNameNumberRiseTimes, key = lambda x: ( x[ 0 ], x[ 1 ], x[ 2 ] ) )

            # Build the menu...
            satellitesMenuItem = Gtk.MenuItem( _( "Satellites" ) )

            if self.showSatellitesAsSubMenu:
                satellitesSubMenu = Gtk.Menu()
                satellitesMenuItem.set_submenu( satellitesSubMenu )

            firstRun = True
            for menuText, key, RiseTime in menuTextSatelliteNameNumberRiseTimes: # key is satellite name/number.
                subMenu = Gtk.Menu()
                if ( key + ( IndicatorLunar.DATA_MESSAGE, ) ) in self.data:
                    subMenu.append( Gtk.MenuItem( self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] ) )
                    if self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_SATELLITE_IS_CIRCUMPOLAR:
                        subMenu.append( Gtk.MenuItem( _( "Azimuth: " ) + self.data[ key + ( IndicatorLunar.DATA_AZIMUTH, ) ] ) )
                        subMenu.append( Gtk.MenuItem( _( "Declination: " ) + self.data[ key + ( IndicatorLunar.DATA_DECLINATION, ) ] ) )
                else:
                    subMenu.append( Gtk.MenuItem( _( "Rise" ) ) )
                    subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Date/Time: " ) + self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] ) )
                    subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Azimuth: " ) + self.data[ key + ( IndicatorLunar.DATA_RISE_AZIMUTH, ) ] ) )
                    subMenu.append( Gtk.MenuItem( _( "Set" ) ) )
                    subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Date/Time: " ) + self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] ) )
                    subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Azimuth: " ) + self.data[ key + ( IndicatorLunar.DATA_SET_AZIMUTH, ) ] ) )

                    if not self.hideSatelliteIfNoVisiblePass:
                        subMenu.append( Gtk.MenuItem( _( "Visible: " ) + self.data[ key + ( IndicatorLunar.DATA_VISIBLE, ) ] ) )

                self.addOnSatelliteHandler( subMenu, key )

                if firstRun:
                    firstRun = False
                    menu.append( satellitesMenuItem )

                if self.showSatellitesAsSubMenu:
                    menuItem = Gtk.MenuItem( menuText )
                    satellitesSubMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + menuText )
                    menu.append( menuItem )

                menuItem.set_submenu( subMenu )


    def addOnSatelliteHandler( self, subMenu, key ):
        for child in subMenu.get_children():
            child.set_name( str( key ) ) # Cannot pass the tuple - must be a string.
            child.connect( "activate", self.onSatellite )


    def onSatellite( self, widget ):
        t = tuple( widget.props.name.replace( "('", "" ).replace( "')", "" ).split( "', '" ) ) # Need to convert from string back to tuple.
        satelliteTLE = self.satelliteTLEData.get( t )

        url = self.satelliteOnClickURL. \
            replace( IndicatorLunar.SATELLITE_TAG_NAME, satelliteTLE.getName() ). \
            replace( IndicatorLunar.SATELLITE_TAG_NUMBER, satelliteTLE.getNumber() ). \
            replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, satelliteTLE.getInternationalDesignator() )

        if len( url ) > 0: webbrowser.open( url )


    def updateRightAscensionDeclinationAzimuthAltitudeMenu( self, menu, dataTag ):
        menu.append( Gtk.MenuItem( _( "Right Ascension: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_RIGHT_ASCENSION ) ] ) )
        menu.append( Gtk.MenuItem( _( "Declination: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_DECLINATION ) ] ) )
        menu.append( Gtk.MenuItem( _( "Azimuth: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_AZIMUTH ) ] ) )
        menu.append( Gtk.MenuItem( _( "Altitude: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_ALTITUDE ) ] ) )


    def updateEclipseMenu( self, menu, dataTag ):
        menu.append( Gtk.MenuItem( _( "Eclipse" ) ) )
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Date/Time: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_ECLIPSE_DATE_TIME ) ] ) )
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Latitude/Longitude: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_ECLIPSE_LATITUDE_LONGITUDE ) ] ) )
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Type: " ) + self.data[ ( dataTag, IndicatorLunar.DATA_ECLIPSE_TYPE ) ] ) )


    def updateSatelliteTLEData( self ):
        # Update the satellite TLE data at most every 12 hours.
        # If the data is invalid, use the TLE data from the previous run.
        if datetime.datetime.now() > ( self.lastUpdateTLE + datetime.timedelta( hours = 12 ) ):
            satelliteTLEData = self.getSatelliteTLEData( self.satelliteTLEURL )
            if satelliteTLEData is None:
                summary = _( "Error Retrieving Satellite TLE Data" )
                message = _( "The satellite TLE data source could not be reached.  Previous TLE data will be used, if available." )
                Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()
            elif len( satelliteTLEData ) == 0:
                summary = _( "Empty Satellite TLE Data" )
                message = _( "The satellite TLE data retrieved is empty.  Previous TLE data will be used, if available." )
                Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()
            else:
                self.satelliteTLEData = satelliteTLEData

                # Add in any new satellites based on the user preference.
                if self.satellitesAddNew:
                    for key in self.satelliteTLEData:
                        if key not in self.satellites:
                            self.satellites.append( key )

                    self.saveSettings()

            self.lastUpdateTLE = datetime.datetime.now()


    def updateOrbitalElementData( self ):
        # Update the orbital element data at most every 24 hours.
        # If the data is invalid, use the orbital element data from the previous run.
        if datetime.datetime.now() > ( self.lastUpdateOrbitalElement + datetime.timedelta( hours = 24 ) ):
            orbitalElementData = self.getOrbitalElementData( self.orbitalElementURL )
            if orbitalElementData is None:
                summary = _( "Error Retrieving Orbital Element Data" )
                message = _( "The orbital element data source could not be reached.  Previous orbital element data will be used, if available." )
                Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()
            elif len( orbitalElementData ) == 0:
                summary = _( "Empty Orbital Element Data" )
                message = _( "The orbital element data retrieved is empty.  Previous orbital element data will be used, if available." )
                Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()
            else:
                self.orbitalElementData = orbitalElementData

                # Add in any new orbital elements based on the user preference.
                if self.orbitalElementsAddNew:
                    for key in self.orbitalElementData:
                        if key not in self.orbitalElements:
                            self.orbitalElements.append( key )

                    self.saveSettings()

            self.lastUpdateOrbitalElement = datetime.datetime.now()


    # http://www.ga.gov.au/geodesy/astro/moonrise.jsp
    def updateMoon( self, ephemNow, lunarPhase ):
        if self.updateCommon( ephem.Moon( self.getCity( ephemNow ) ), AstronomicalObjectType.Moon, IndicatorLunar.MOON_TAG, ephemNow ):

            self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_PHASE ) ] = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ]
            self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_FIRST_QUARTER ) ] = self.localiseAndTrim( ephem.next_first_quarter_moon( ephemNow ) )
            self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_FULL ) ] = self.localiseAndTrim( ephem.next_full_moon( ephemNow ) )
            self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_THIRD_QUARTER ) ] = self.localiseAndTrim( ephem.next_last_quarter_moon( ephemNow ) )
            self.data[ ( IndicatorLunar.MOON_TAG, IndicatorLunar.DATA_NEW ) ] = self.localiseAndTrim( ephem.next_new_moon( ephemNow ) )

            self.nextUpdates.append( ephem.next_first_quarter_moon( ephemNow ) )
            self.nextUpdates.append( ephem.next_full_moon( ephemNow ) )
            self.nextUpdates.append( ephem.next_last_quarter_moon( ephemNow ) )
            self.nextUpdates.append( ephem.next_new_moon( ephemNow ) )

            self.updateEclipse( ephemNow, IndicatorLunar.MOON_TAG )


    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    # http://www.ga.gov.au/geodesy/astro/sunrise.jsp
    def updateSun( self, ephemNow ):
        city = self.getCity( ephemNow )
        sun = ephem.Sun( city )
        if self.updateCommon( sun, AstronomicalObjectType.Sun, IndicatorLunar.SUN_TAG, ephemNow ):

            # Dawn/Dusk.
            try:
                city = self.getCity( ephemNow )
                city.horizon = '-6' # -6 = civil twilight, -12 = nautical, -18 = astronomical (http://stackoverflow.com/a/18622944/2156453)
                dawn = city.next_rising( sun, use_center = True )
                dusk = city.next_setting( sun, use_center = True )
                self.data[ ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_DAWN ) ] = self.localiseAndTrim( dawn )
                self.data[ ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_DUSK ) ] = self.localiseAndTrim( dusk )
                self.nextUpdates.append( dawn )
                self.nextUpdates.append( dusk )
            except ephem.AlwaysUpError: self.data[ ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_MESSAGE ) ] = IndicatorLunar.MESSAGE_BODY_ALWAYS_UP
            except ephem.NeverUpError:
                if not self.hideBodyIfNeverUp:
                    self.data[ ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_MESSAGE ) ] = IndicatorLunar.MESSAGE_BODY_NEVER_UP

            # Solstice/Equinox.
            equinox = ephem.next_equinox( ephemNow )
            self.data[ ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_EQUINOX ) ] = self.localiseAndTrim( equinox )
            solstice = ephem.next_solstice( ephemNow )
            self.data[ ( IndicatorLunar.SUN_TAG, IndicatorLunar.DATA_SOLSTICE ) ] = self.localiseAndTrim( solstice )
            self.nextUpdates.append( equinox )
            self.nextUpdates.append( solstice )

            self.updateEclipse( ephemNow, IndicatorLunar.SUN_TAG )


    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    def updatePlanets( self, ephemNow ):
        for planetName in self.planets:
            planet = getattr( ephem, planetName )() # Dynamically instantiate the planet object.
            planet.compute( self.getCity( ephemNow ) )
            if self.updateCommon( planet, AstronomicalObjectType.Planet, planetName.upper(), ephemNow ):
                city = self.getCity( ephemNow )
                if planetName in IndicatorLunar.PLANET_MOONS:
                    for moonName in IndicatorLunar.PLANET_MOONS[ planetName ]:
                        moon = getattr( ephem, moonName )() # Dynamically instantiate the moon object.
                        moon.compute( city )
                        self.updateRightAscensionDeclinationAzimuthAltitude( moon, moonName.upper() )
                        self.data[ ( moonName.upper(), IndicatorLunar.DATA_EARTH_VISIBLE ) ] = str( bool( moon.earth_visible ) )
                        self.data[ ( moonName.upper(), IndicatorLunar.DATA_X_OFFSET ) ] = str( round( moon.x, 1 ) )
                        self.data[ ( moonName.upper(), IndicatorLunar.DATA_Y_OFFSET ) ] = str( round( moon.y, 1 ) )
                        self.data[ ( moonName.upper(), IndicatorLunar.DATA_Z_OFFSET ) ] = str( round( moon.z, 1 ) )


    # http://aa.usno.navy.mil/data/docs/mrst.php
    def updateStars( self, ephemNow ):
        for starName in self.stars:
            star = ephem.star( starName )
            star.compute( self.getCity( ephemNow ) )
            self.updateCommon( star, AstronomicalObjectType.Star, star.name.upper(), ephemNow )


    # Computes the rise/set and other information for orbital elements, such as comets.
    # http://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
    # http://www.minorplanetcenter.net/iau/Ephemerides/Soft03.html        
    def updateOrbitalElements( self, ephemNow ):
        for key in self.orbitalElements:
            if key in self.orbitalElementData:
                orbitalElement = ephem.readdb( self.orbitalElementData[ key ] )
                orbitalElement.compute( self.getCity( ephemNow ) )
                if float( orbitalElement.mag ) <= float( self.orbitalElementsMagnitude ):
                    self.updateCommon( orbitalElement, AstronomicalObjectType.OrbitalElement, key, ephemNow )
            else:
                if not self.hideBodyIfNeverUp:
                    self.data[ ( key, IndicatorLunar.DATA_MESSAGE ) ] = IndicatorLunar.MESSAGE_ORBITAL_ELEMENT_NO_DATA


    # Calculates common items such as rise/set, illumination, constellation, magnitude, tropical sign, distance to earth/sun, bright limb angle.
    # Returns
    #    True if all calculations were performed (the body either rises/sets or is always up).
    #    False if the body never rises, informing the caller that perhaps subsequent calculations should be aborted.
    def updateCommon( self, body, astronomicalObjectType, dataTag, ephemNow ):
        continueCalculations = True
        try:
            city = self.getCity( ephemNow )
            rising = city.next_rising( body )
            setting = city.next_setting( body )
            self.data[ ( dataTag, IndicatorLunar.DATA_RISE_TIME ) ] = str( self.localiseAndTrim( rising ) )
            self.data[ ( dataTag, IndicatorLunar.DATA_SET_TIME ) ] = str( self.localiseAndTrim( setting ) )
            self.nextUpdates.append( rising )
            self.nextUpdates.append( setting )

        except ephem.AlwaysUpError:
            self.data[ ( dataTag, IndicatorLunar.DATA_MESSAGE ) ] = IndicatorLunar.MESSAGE_BODY_ALWAYS_UP

        except ephem.NeverUpError:
            if self.hideBodyIfNeverUp:
                continueCalculations = False
            else:
                self.data[ ( dataTag, IndicatorLunar.DATA_MESSAGE ) ] = IndicatorLunar.MESSAGE_BODY_NEVER_UP

        if continueCalculations:
            body.compute( self.getCity( ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.

            if astronomicalObjectType == AstronomicalObjectType.Moon or astronomicalObjectType == AstronomicalObjectType.Planet:
                self.data[ ( dataTag, IndicatorLunar.DATA_ILLUMINATION ) ] = str( int( round( body.phase ) ) ) + "%"

            self.data[ ( dataTag, IndicatorLunar.DATA_CONSTELLATION ) ] = IndicatorLunar.CONSTELLATIONS[ ephem.constellation( body )[ 1 ] ]
            self.data[ ( dataTag, IndicatorLunar.DATA_MAGNITUDE ) ] = str( body.mag )

            if astronomicalObjectType != AstronomicalObjectType.OrbitalElement:
                self.data[ ( dataTag, IndicatorLunar.DATA_TROPICAL_SIGN ) ] = self.getTropicalSign( body, ephemNow )

            if astronomicalObjectType == AstronomicalObjectType.Moon or \
               astronomicalObjectType == AstronomicalObjectType.OrbitalElement or \
               astronomicalObjectType == AstronomicalObjectType.Planet or \
               astronomicalObjectType == AstronomicalObjectType.Sun:
                self.data[ ( dataTag, IndicatorLunar.DATA_DISTANCE_TO_EARTH ) ] = str( round( body.earth_distance, 4 ) ) + " " + _( "ua" )

            if astronomicalObjectType == AstronomicalObjectType.Moon or \
               astronomicalObjectType == AstronomicalObjectType.OrbitalElement or \
               astronomicalObjectType == AstronomicalObjectType.Planet:
                self.data[ ( dataTag, IndicatorLunar.DATA_DISTANCE_TO_SUN ) ] = str( round( body.sun_distance, 4 ) ) + " " + _( "ua" )

            if astronomicalObjectType == AstronomicalObjectType.Moon or astronomicalObjectType == AstronomicalObjectType.Planet:
                self.data[ ( dataTag, IndicatorLunar.DATA_BRIGHT_LIMB ) ] = str( round( self.getBrightLimbAngleRelativeToZenith( self.getCity( ephemNow ), body ) ) ) + "°"

            self.updateRightAscensionDeclinationAzimuthAltitude( body, dataTag )

        return continueCalculations


    # Uses TLE data collated by Dr T S Kelso (http://celestrak.com/NORAD/elements) with PyEphem to compute satellite rise/pass/set times.
    # Other sources/background:
    #   http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
    #   http://spotthestation.nasa.gov/sightings
    #   http://www.n2yo.com
    #   http://www.heavens-above.com
    #   http://in-the-sky.org
    #
    # For planets/stars, the immediately next rise/set time is shown.
    # If already above the horizon, the set time is shown followed by the rise time for the following pass.
    # This makes sense as planets/stars are slow moving.
    #
    # However, as satellites are faster moving and pass several times a day, a different approach is used.
    # When a notification is displayed indicating a satellite is now passing overhead,
    # the user may want to see the rise/set for the current pass (rather than the set for the current pass and rise for the next pass).
    # Therefore...
    #    If a satellite is yet to rise, show the upcoming rise/set time.
    #    If a satellite is currently passing over, show the rise/set time for that pass.
    # This allows the user to see the rise/set time for the current pass as it is happening.
    # When the pass completes and an update occurs, the rise/set for the next pass will be displayed.
    def updateSatellites( self, ephemNow ):
        for key in self.satellites:
            if key in self.satelliteTLEData:
                self.calculateNextSatellitePass( ephemNow, key, self.satelliteTLEData[ key ] )
            else:
                if not self.hideSatelliteIfNoVisiblePass:
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] = IndicatorLunar.MESSAGE_SATELLITE_NO_TLE_DATA


    def calculateNextSatellitePass( self, ephemNow, key, satelliteTLE ):
        currentDateTime = ephemNow
        endDateTime = ephem.Date( ephemNow + ephem.hour * 24 * 10 ) # Stop looking for passes 10 days from ephemNow.
        message = None
        while currentDateTime < endDateTime:
            city = self.getCity( currentDateTime )
            satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
            satellite.compute( city )
            try: nextPass = city.next_pass( satellite )
            except ValueError:
                if satellite.circumpolar:
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] = IndicatorLunar.MESSAGE_SATELLITE_IS_CIRCUMPOLAR
                    self.data[ key + ( IndicatorLunar.DATA_AZIMUTH, ) ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( satellite.az ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( satellite.az ) ) + ")"
                    self.data[ key + ( IndicatorLunar.DATA_DECLINATION, ) ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( satellite.dec ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( satellite.dec ) ) + ")"
                elif satellite.neverup:
                    message = IndicatorLunar.MESSAGE_SATELLITE_NEVER_RISES
                else:
                    message = IndicatorLunar.MESSAGE_SATELLITE_VALUE_ERROR

                break

            if not self.isSatellitePassValid( nextPass ):
                message = IndicatorLunar.MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS
                break

            # Need to get the rise/transit/set for the satellite.
            # If the satellite is passing, need to work out when it rose...
            if nextPass[ 0 ] > nextPass[ 4 ]:
                # The rise time is after set time, meaning the satellite is current passing.
                setTime = nextPass[ 4 ]
                nextPass = self.calculateSatellitePassForRisingPriorToNow( currentDateTime, key, satelliteTLE )
                if nextPass is None:
                    currentDateTime = ephem.Date( setTime + ephem.minute * 30 ) # Could not determine the rise, so look for the next pass.
                    continue

            # Now have a satellite rise/transit/set; determine if the pass is visible (and if the user wants only visible passes).
            passIsVisible = self.isSatellitePassVisible( satellite, nextPass[ 2 ] )
            if self.hideSatelliteIfNoVisiblePass and not passIsVisible:
                currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )
                continue

            # The pass is visible and the user wants only visible passes OR the user wants any pass...
            self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] = self.localiseAndTrim( nextPass[ 0 ] )
            self.data[ key + ( IndicatorLunar.DATA_RISE_AZIMUTH, ) ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 1 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 1 ] ) ) + ")"
            self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] = self.localiseAndTrim( nextPass[ 4 ] )
            self.data[ key + ( IndicatorLunar.DATA_SET_AZIMUTH, ) ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 5 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 5 ] ) ) + ")"
            self.data[ key + ( IndicatorLunar.DATA_VISIBLE, ) ] = str( passIsVisible ) # Put this in as it's likely needed in the notification.

            self.nextUpdates.append( nextPass[ 4 ] )
            if ephem.Date( nextPass[ 0 ] ) > currentDateTime:
                self.nextUpdates.append( nextPass[ 0 ] ) # No point adding a time in the past.

            break

            currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )

        if currentDateTime >= endDateTime:
            message = IndicatorLunar.MESSAGE_SATELLITE_NO_PASSES_WITHIN_NEXT_TEN_DAYS

        if message is not None and not self.hideSatelliteIfNoVisiblePass:
            self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] = message


    def calculateSatellitePassForRisingPriorToNow( self, ephemNow, key, satelliteTLE ):
        currentDateTime = ephem.Date( ephemNow - ephem.minute ) # Start looking from one minute ago.
        endDateTime = ephem.Date( ephemNow - ephem.hour * 1 ) # Only look back an hour for the rise time (then just give up).
        while currentDateTime > endDateTime:
            city = self.getCity( currentDateTime )
            satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
            satellite.compute( city )
            try:
                nextPass = city.next_pass( satellite )
                if not self.isSatellitePassValid( nextPass ): return None # Unlikely to happen but better to be safe!

                if nextPass[ 0 ] < nextPass[ 4 ]: return nextPass

                currentDateTime = ephem.Date( currentDateTime - ephem.minute )

            except: return None # This should never happen as the satellite has a rise and set (is not circumpolar or never up).


    def isSatellitePassValid( self, satellitePass ):
        return satellitePass is not None and \
            len( satellitePass ) == 6 and \
            satellitePass[ 0 ] is not None and \
            satellitePass[ 1 ] is not None and \
            satellitePass[ 2 ] is not None and \
            satellitePass[ 3 ] is not None and \
            satellitePass[ 4 ] is not None and \
            satellitePass[ 5 ] is not None


    # Determine if a satellite pass is visible or not...
    #    http://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
    #    http://www.celestrak.com/columns/v03n01
    #    http://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
    def isSatellitePassVisible( self, satellite, passDateTime ):
        city = self.getCity( passDateTime )
        city.pressure = 0
        city.horizon = "-0:34"

        satellite.compute( city )
        sun = ephem.Sun()
        sun.compute( city )

        return ( satellite.eclipsed is False ) and ( sun.alt > ephem.degrees( "-18" ) ) and ( sun.alt < ephem.degrees( "-6" ) )


    # Compute the right ascension, declination, azimuth and altitude for a body.
    def updateRightAscensionDeclinationAzimuthAltitude( self, body, dataTag ):
        self.data[ ( dataTag, IndicatorLunar.DATA_RIGHT_ASCENSION ) ] = str( round( self.convertHoursMinutesSecondsToDecimalDegrees( body.g_ra ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.g_ra ) ) + ")"

        direction = _( "N" )
        if body.g_dec < 0.0: direction = _( "S" )

        self.data[ ( dataTag, IndicatorLunar.DATA_DECLINATION ) ] = str( abs( round( self.convertDegreesMinutesSecondsToDecimalDegrees( body.g_dec ), 2 ) ) ) + "° " + direction + " (" + re.sub( "\.(\d+)", "", str( body.g_dec ) ) + ")"
        self.data[ ( dataTag, IndicatorLunar.DATA_AZIMUTH ) ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( body.az ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.az ) ) + ")"
        self.data[ ( dataTag, IndicatorLunar.DATA_ALTITUDE ) ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( body.alt ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.alt ) ) + ")"


    def updateEclipse( self, ephemNow, dataTag ):
        if dataTag == IndicatorLunar.SUN_TAG:
            eclipseInformation = eclipse.getSolarEclipseForUTC( ephemNow.datetime() )
        else:
            eclipseInformation = eclipse.getLunarEclipseForUTC( ephemNow.datetime() )

        if eclipseInformation is None:
            logging.error( "No eclipse information found!" )
        else:
            eclipseType = None
            if   eclipseInformation[ 1 ] == eclipse.EclipseType.Annular: eclipseType = _( "Annular" )
            elif eclipseInformation[ 1 ] == eclipse.EclipseType.Hybrid: eclipseType = _( "Hybrid (Annular/Total)" )
            elif eclipseInformation[ 1 ] == eclipse.EclipseType.Partial: eclipseType = _( "Partial" )
            elif eclipseInformation[ 1 ] == eclipse.EclipseType.Penumbral: eclipseType = _( "Penumbral" )
            elif eclipseInformation[ 1 ] == eclipse.EclipseType.Total: eclipseType = _( "Total" )

            northOrSouth = None
            if   eclipseInformation[ 3 ] == eclipse.CardinalDirection.N: northOrSouth = _( "N" )
            elif eclipseInformation[ 3 ] == eclipse.CardinalDirection.S: northOrSouth = _( "S" )

            eastOrWest = None
            if   eclipseInformation[ 5 ] == eclipse.CardinalDirection.E: eastOrWest = _( "E" )
            elif eclipseInformation[ 5 ] == eclipse.CardinalDirection.W: eastOrWest = _( "W" )

            if eclipseType is None:
                logging.error( "Unknown eclipse type", eclipseInformation )
            elif northOrSouth is None:
                logging.error( "Unknown latitude cardinal direction", eclipseInformation )
            elif eastOrWest is None:
                logging.error( "Unknown longitude cardinal direction", eclipseInformation )
            else:
                localisedAndTrimmedDateTime = self.localiseAndTrim( ephem.Date( eclipseInformation[ 0 ] ) )
                self.data[ ( dataTag, IndicatorLunar.DATA_ECLIPSE_DATE_TIME ) ] = localisedAndTrimmedDateTime
                self.data[ ( dataTag, IndicatorLunar.DATA_ECLIPSE_LATITUDE_LONGITUDE ) ] = eclipseInformation[ 2 ] + " " + northOrSouth + " " + eclipseInformation[ 4 ] + " " + eastOrWest 
                self.data[ ( dataTag, IndicatorLunar.DATA_ECLIPSE_TYPE ) ] = eclipseType


    # Takes a float pyEphem DateTime and converts to local time, trims off fractional seconds and returns a string.
    def localiseAndTrim( self, ephemDateTime ):
        localtimeString = str( ephem.localtime( ephemDateTime ) )
        return localtimeString[ 0 : localtimeString.rfind( ":" ) + 3 ]


    def getLunarPhase( self, ephemNow, illuminationPercentage ):
        nextFullMoonDate = ephem.next_full_moon( ephemNow )
        nextNewMoonDate = ephem.next_new_moon( ephemNow )
        phase = None
        if nextFullMoonDate < nextNewMoonDate: # No need for these dates to be localised...just need to know which date is before the other.
            # Between a new moon and a full moon...
            if( illuminationPercentage > 99 ):
                phase = IndicatorLunar.LUNAR_PHASE_FULL_MOON
            elif illuminationPercentage <= 99 and illuminationPercentage > 50:
                phase = IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS
            elif illuminationPercentage == 50:
                phase = IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER
            elif illuminationPercentage < 50 and illuminationPercentage >= 1:
                phase = IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT
            else: # illuminationPercentage < 1
                phase = IndicatorLunar.LUNAR_PHASE_NEW_MOON
        else:
            # Between a full moon and the next new moon...
            if( illuminationPercentage > 99 ):
                phase = IndicatorLunar.LUNAR_PHASE_FULL_MOON
            elif illuminationPercentage <= 99 and illuminationPercentage > 50:
                phase = IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS
            elif illuminationPercentage == 50:
                phase = IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER
            elif illuminationPercentage < 50 and illuminationPercentage >= 1:
                phase = IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT
            else: # illuminationPercentage < 1
                phase = IndicatorLunar.LUNAR_PHASE_NEW_MOON

        return phase

    # Code courtesy of Ignius Drake.
    def getTropicalSign( self, body, ephemNow ):
        signList = [ _( "Aries" ), _( "Taurus" ), _( "Gemini" ), _( "Cancer" ), _( "Leo" ), _( "Virgo" ), _( "Libra" ), _( "Scorpio" ), _( "Sagittarius" ), _( "Capricorn" ), _( "Aquarius" ), _( "Pisces" ) ]

        ( year, month, day ) = ephemNow.triple()
        epochAdjusted = float( year ) + float( month ) / 12.0 + float( day ) / 365.242
        ephemNowDate = str( ephemNow ).split( " " )

        bodyCopy = self.getBodyCopy( body ) # Used to workaround https://github.com/brandon-rhodes/pyephem/issues/44 until a formal release of pyephem is made.
#         bodyCopy = body.copy() # Computing the tropical sign changes the body's date/time/epoch (shared by other downstream calculations), so make a copy of the body and use that.
        bodyCopy.compute( ephemNowDate[ 0 ], epoch = str( epochAdjusted ) )
        planetCoordinates = str( ephem.Ecliptic( bodyCopy ).lon ).split( ":" )

        if float( planetCoordinates[ 2 ] ) > 30:
            planetCoordinates[ 1 ] = str( int ( planetCoordinates[ 1 ] ) + 1 )

        planetSignDegree = int( planetCoordinates[ 0 ] ) % 30
        planetSignMinute = str( planetCoordinates[ 1 ] )
        planetSignIndex = int( planetCoordinates[ 0 ] ) / 30
        planetSignName = signList[ int( planetSignIndex ) ]

        return planetSignName + " " + str( planetSignDegree ) + "° " + planetSignMinute + "'"


    # Used to workaround https://github.com/brandon-rhodes/pyephem/issues/44 until a formal release of pyephem is made.
    def getBodyCopy( self, body ):
        bodyName = body.name
        bodyCopy = None

        if bodyName == "Sun": bodyCopy = ephem.Sun()
        elif bodyName == "Moon": bodyCopy = ephem.Moon()
        elif bodyName == "Mercury": bodyCopy = ephem.Mercury()
        elif bodyName == "Venus": bodyCopy = ephem.Venus()
        elif bodyName == "Mars": bodyCopy = ephem.Mars()
        elif bodyName == "Jupiter": bodyCopy = ephem.Jupiter()
        elif bodyName == "Saturn": bodyCopy = ephem.Saturn()
        elif bodyName == "Uranus": bodyCopy = ephem.Uranus()
        elif bodyName == "Neptune": bodyCopy = ephem.Neptune()
        elif bodyName == "Pluto": bodyCopy = ephem.Pluto()
        else: bodyCopy = ephem.star( bodyName ) # If not the sun/moon/planet, assume a star.

        return bodyCopy


    # Compute the bright limb angle (relative to zenith) between the sun and a planetary bodyCopy.
    # Measured in degrees counter clockwise from a positive y axis.
    #
    # References:
    #  'Astronomical Algorithms' by Jean Meeus (chapters 14 and 48).
    #  'Practical Astronomy with Your Calculator' by Peter Duffett-Smith (chapters 59 and 68).
    #  http://www.geoastro.de/moonlibration/
    #  http://www.geoastro.de/SME/
    #  http://futureboy.us/fsp/moon.fsp
    #
    # Other references...
    #  http://www.nightskynotebook.com/Moon.php
    #  http://www.calsky.com/cs.cgi/Moon/6
    #  http://www.calsky.com/cs.cgi/Sun/3
    #  https://github.com/soniakeys/meeus
    #  http://godoc.org/github.com/soniakeys/meeus
    #  https://sites.google.com/site/astronomicalalgorithms
    #  http://stackoverflow.com/questions/13463965/pyephem-sidereal-time-gives-unexpected-result
    #  https://github.com/brandon-rhodes/pyephem/issues/24
    #  http://stackoverflow.com/questions/13314626/local-solar-time-function-from-utc-and-longitude/13425515#13425515
    #  http://web.archiveorange.com/archive/v/74jMQyHUOwbskBYwisCl
    #  https://github.com/brandon-rhodes/pyephem/issues/24
    def getBrightLimbAngleRelativeToZenith( self, city, body ):
        sun = ephem.Sun( city )

        # Using the Apparent Geocentric Position as this is closest to the Meeus example 25.a for RA/Dec.
        sunRA = math.radians( self.convertHoursMinutesSecondsToDecimalDegrees( sun.g_ra ) )
        sunDec = math.radians( self.convertDegreesMinutesSecondsToDecimalDegrees( sun.g_dec ) )
        bodyRA = math.radians( self.convertHoursMinutesSecondsToDecimalDegrees( body.g_ra ) )
        bodyDec = math.radians( self.convertDegreesMinutesSecondsToDecimalDegrees( body.g_dec ) )

        y = math.cos( sunDec ) * math.sin( sunRA - bodyRA )
        x = math.cos( bodyDec ) * math.sin( sunDec ) - math.sin( bodyDec ) * math.cos( sunDec ) * math.cos( sunRA - bodyRA )
        brightLimbAngle = math.degrees( math.atan2( y, x ) )

        hourAngle = math.radians( self.convertHoursMinutesSecondsToDecimalDegrees( city.sidereal_time() ) ) - bodyRA
        y = math.sin( hourAngle )
        x = math.tan( math.radians( self.convertDegreesMinutesSecondsToDecimalDegrees( city.lat ) ) ) * math.cos( bodyDec ) - math.sin( bodyDec ) * math.cos( hourAngle )
        parallacticAngle = math.degrees( math.atan2( y, x ) )

        zenithAngle = brightLimbAngle - parallacticAngle
        if zenithAngle < 0.0: zenithAngle += 360.0

        return zenithAngle


    def convertHoursMinutesSecondsToDecimalDegrees( self, hms ):
        t = tuple( str( hms ).split( ":" ) )
        x = ( float( t[ 2 ] ) / 60.0 + float( t[ 1 ] ) ) / 60.0 + abs( float( t[ 0 ] ) ) * 15.0
        y = float( t[ 0 ] )
        return math.copysign( x, y )


    def convertDegreesMinutesSecondsToDecimalDegrees( self, dms ):
        t = tuple( str( dms ).split( ":" ) )
        x = ( float( t[ 2 ] ) / 60.0 + float( t[ 1 ] ) ) / 60.0 + abs( float( t[ 0 ] ) )
        y = float( t[ 0 ] )
        return math.copysign( x, y )


    # Used to instantiate a new city object/observer.
    # Typically after calculations (or exceptions) the city date is altered.
    def getCity( self, date = None ):
        city = ephem.city( self.cityName )
        if date is not None: city.date = date
        return city


    # Creates an SVG icon file representing the moon given the illumination and bright limb angle (relative to zenith).
    #    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
    #    brightLimbAngleInDegrees The angle of the (relative to zenith) bright limb ranging from 0 to 360 inclusive.
    #                             If the bright limb is None, a full moon will be rendered and saved to a full moon file (for the notification).
    def createIcon( self, illuminationPercentage, brightLimbAngleInDegrees ):
        # Size of view box.
        width = 100
        height = 100

        # The radius of the moon should have the full moon take up most of the viewing area but with a boundary.
        # A radius of 50 is too big and 25 is too small...so compute a radius half way between, based on the width/height of the viewing area.
        radius = float ( str( ( width / 2 ) - ( ( width / 2 ) - ( width / 4 ) ) / 2 ) )

        if illuminationPercentage == 0 or illuminationPercentage == 100:
            svgStart = '<circle cx="' + str( width / 2 ) + '" cy="' + str( height / 2 ) + '" r="' + str( radius )

            if illuminationPercentage == 0: # New
                svg = svgStart + '" fill="none" stroke="' + pythonutils.getColourForIconTheme() + '" stroke-width="2" />'
            else: # Full
                svg = svgStart + '" fill="' + pythonutils.getColourForIconTheme() + '" />'

        else:
            svgStart = '<path d="M ' + str( width / 2 ) + ' ' + str( height / 2 ) + ' h-' + str( radius ) + ' a ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + str( radius * 2 ) + ' 0'

            svgEnd = ' transform="rotate(' + str( brightLimbAngleInDegrees * -1 ) + ' ' + str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="' + pythonutils.getColourForIconTheme() + '" />'

            if illuminationPercentage == 50: # Quarter
                svg = svgStart + '"' + svgEnd
            elif illuminationPercentage < 50: # Crescent
                svg = svgStart + ' a ' + str( radius ) + ' ' + str( ( 50 - illuminationPercentage ) / 50.0 * radius ) + ' 0 0 0 ' + str( radius * 2 * -1 ) + ' + 0"' + svgEnd 
            else: # Gibbous
                svg = svgStart + ' a ' + str( radius ) + ' ' + str( ( illuminationPercentage - 50 ) / 50.0 * radius ) + ' 0 1 1 ' + str( radius * 2 * -1 ) + ' + 0"' + svgEnd

        header = '<?xml version="1.0" standalone="no"?>' \
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100">'

        footer = '</svg>'

        if brightLimbAngleInDegrees is None:
            filename = IndicatorLunar.SVG_FULL_MOON_FILE
        else:
            filename = self.getIconFile()

        try:
            with open( filename, "w" ) as f:
                f.write( header + svg + footer )
                f.close()

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing SVG: " + filename )


    def getIconName( self ):
        iconName = "." + INDICATOR_NAME + "-illumination-icon"
        return ( iconName + "-1" ) if IndicatorLunar.ICON_STATE else ( iconName + "-2" )


    def getIconFile( self ): return tempfile.gettempdir() + "/" + self.getIconName() + ".svg"


    # Hideous workaround because setting the icon with the same name does not change the icon any more.
    # So alternate the name of the icon!
    # https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620
    # http://askubuntu.com/questions/490634/application-indicator-icon-not-changing-until-clicked
    def toggleIconState( self ): IndicatorLunar.ICON_STATE = not IndicatorLunar.ICON_STATE


    def onAbout( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.dialog = pythonutils.AboutDialog( 
            INDICATOR_NAME,
            IndicatorLunar.ABOUT_COMMENTS, 
            IndicatorLunar.WEBSITE, 
            IndicatorLunar.WEBSITE, 
            IndicatorLunar.VERSION, 
            Gtk.License.GPL_3_0, 
            IndicatorLunar.ICON,
            [ IndicatorLunar.AUTHOR ],
            IndicatorLunar.ABOUT_CREDITS,
            _( "Credits" ),
            "/usr/share/doc/" + INDICATOR_NAME + "/changelog.Debian.gz",
            _( "Change _Log" ),
            _( "translator-credits" ),
            logging )

        self.dialog.run()
        self.dialog.destroy()
        self.dialog = None


    def waitForUpdateToFinish( self, widget ):
        while not self.lock.acquire( blocking = False ):
            time.sleep( 1 )

        GLib.idle_add( self.onPreferencesInternal, widget )        


    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        # If the preferences were open and accessing the backend data (self.data) and an update occurs, that's not good.
        # So ensure that no update is occurring...if it is, wait for it to end.
        if self.lock.acquire( blocking = False ):
            self.onPreferencesInternal( widget )
        else:
            summary = _( "Preferences unavailable..." )
            message = _( "The lunar indicator is momentarily refreshing; preferences will be available shortly." )
            Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()
            Thread( target = self.waitForUpdateToFinish, args = ( widget, ) ).start()


    def onPreferencesInternal( self, widget ):
        GLib.source_remove( self.eventSourceID ) # Ensure no update occurs whilst the preferences are open.

        notebook = Gtk.Notebook()

        # Icon.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_top( 10 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( 10 )
        box.set_margin_right( 10 )

        label = Gtk.Label( _( "Icon Text" ) )
        box.pack_start( label, False, False, 0 )

        indicatorText = Gtk.Entry()
        indicatorText.set_text( self.indicatorText ) #TODO Does this text need to be converted into translated tags?
        indicatorText.set_tooltip_text( _( "The text shown next to the indicator icon\n(or shown as a tooltip, where applicable)." ) )
        box.pack_start( indicatorText, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        displayTagsStore = Gtk.ListStore( str, str, str ) # Tag, translated tag, value.
        self.updateDisplayTags( displayTagsStore, None, None )
        displayTagsStoreSort = Gtk.TreeModelSort( model = displayTagsStore )
        displayTagsStoreSort.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( displayTagsStoreSort )
        tree.set_hexpand( True )
        tree.set_vexpand( True )

        treeViewColumn = Gtk.TreeViewColumn( _( "Tag" ), Gtk.CellRendererText(), text = 1 ) 
        treeViewColumn.set_sort_column_id( 0 )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Value" ), Gtk.CellRendererText(), text = 2 ) 
        treeViewColumn.set_sort_column_id( 1 )
        tree.append_column( treeViewColumn )

        tree.set_tooltip_text( _( 
            "Double click to add a tag to the\n" + \
            "indicator text.\n\n" + \
            "Depending on the menu options,\n" + \
            "items such as comets which exceed\n" + \
            "magnitude or satellites with no\n" + \
            "visible pass are omitted." ) )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onIndicatorTextTagDoubleClick, indicatorText )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Icon" ) ) )

        # Menu.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 15 )
        grid.set_margin_bottom( 15 )

        label = Gtk.Label( _( "Show as submenus" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 40 ) # Bug in Python - must specify the parameter names!
        box.set_margin_left( 20 )

        showPlanetsAsSubmenuCheckbox = Gtk.CheckButton( ( "Planets" ) )
        showPlanetsAsSubmenuCheckbox.set_active( self.showPlanetsAsSubMenu )
        showPlanetsAsSubmenuCheckbox.set_tooltip_text( _( "Show planets (excluding moon/sun) as submenus." ) )
        box.pack_start( showPlanetsAsSubmenuCheckbox, False, False, 0 )

        showStarsAsSubmenuCheckbox = Gtk.CheckButton( _( "Stars" ) )
        showStarsAsSubmenuCheckbox.set_tooltip_text( _( "Show stars as submenus." ) )
        showStarsAsSubmenuCheckbox.set_active( self.showStarsAsSubMenu )
        box.pack_start( showStarsAsSubmenuCheckbox, False, False, 0 )

        showOrbitalElementsAsSubmenuCheckbox = Gtk.CheckButton( _( "Orbital elements" ) )
        showOrbitalElementsAsSubmenuCheckbox.set_tooltip_text( _( "Show orbital elements as submenus." ) )
        showOrbitalElementsAsSubmenuCheckbox.set_active( self.showOrbitalElementsAsSubMenu )
        box.pack_start( showOrbitalElementsAsSubmenuCheckbox, False, False, 0 )

        showSatellitesAsSubmenuCheckbox = Gtk.CheckButton( _( "Satellites" ) )
        showSatellitesAsSubmenuCheckbox.set_active( self.showSatellitesAsSubMenu )
        showSatellitesAsSubmenuCheckbox.set_tooltip_text( _( "Show satellites as submenus." ) )
        box.pack_start( showSatellitesAsSubmenuCheckbox, False, False, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        hideBodyIfNeverUpCheckbox = Gtk.CheckButton( _( "Hide bodies which are 'never up'" ) )
        hideBodyIfNeverUpCheckbox.set_margin_top( 15 )
        hideBodyIfNeverUpCheckbox.set_active( self.hideBodyIfNeverUp )
        hideBodyIfNeverUpCheckbox.set_tooltip_text( _( 
            "If checked, only planets, moon, sun,\n" + \
            "orbital elements and stars which rise/set\n" + \
            "or are 'always up' will be shown.\n\n" + \
            "Otherwise all bodies are shown." ) )
        grid.attach( hideBodyIfNeverUpCheckbox, 0, 2, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 6 ) # Bug in Python - must specify the parameter names!
        box.set_margin_top( 15 )

        label = Gtk.Label( _( "Hide orbital elements greater than magnitude" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        spinnerOrbitalElementMagnitude = Gtk.SpinButton()
        spinnerOrbitalElementMagnitude.set_numeric( True )
        spinnerOrbitalElementMagnitude.set_update_policy( Gtk.SpinButtonUpdatePolicy.IF_VALID )
        spinnerOrbitalElementMagnitude.set_adjustment( Gtk.Adjustment( self.orbitalElementsMagnitude, -30, 30, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerOrbitalElementMagnitude.set_value( self.orbitalElementsMagnitude ) # ...so need to force the initial value by explicitly setting it.
        spinnerOrbitalElementMagnitude.set_tooltip_text( _( "Orbital elements with a magnitude greater\nthan that specified will not be shown." ) )

        box.pack_start( spinnerOrbitalElementMagnitude, False, False, 0 )

        grid.attach( box, 0, 3, 1, 1 )

        orbitalElementsAddNewCheckbox = Gtk.CheckButton( _( "Automatically add new orbital elements" ) )
        orbitalElementsAddNewCheckbox.set_margin_top( 15 )
        orbitalElementsAddNewCheckbox.set_active( self.orbitalElementsAddNew )
        orbitalElementsAddNewCheckbox.set_tooltip_text( _( 
            "If checked, new orbital elements in the\n" + \
            "downloaded data will be added to your\n" + \
            "list of checked orbital elements." ) )
        grid.attach( orbitalElementsAddNewCheckbox, 0, 4, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 6 ) # Bug in Python - must specify the parameter names!
        box.set_margin_top( 15 )

        label = Gtk.Label( _( "Satellite menu text" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        satelliteMenuText = Gtk.Entry()
        satelliteMenuText.set_text( self.satelliteMenuText )
        satelliteMenuText.set_hexpand( True )
        satelliteMenuText.set_tooltip_text( 
             "The text for each satellite item in the menu.\n\n" + \
             "Available tags:\n\t" + \
             IndicatorLunar.SATELLITE_TAG_NAME + "\n\t" + \
             IndicatorLunar.SATELLITE_TAG_NUMBER + "\n\t" + \
             IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR )

        box.pack_start( satelliteMenuText, True, True, 0 )

        grid.attach( box, 0, 5, 1, 1 )

        sortSatellitesByDateTimeCheckbox = Gtk.CheckButton( _( "Sort satellites by rise date/time" ) )
        sortSatellitesByDateTimeCheckbox.set_margin_top( 15 )
        sortSatellitesByDateTimeCheckbox.set_active( self.satellitesSortByDateTime )
        sortSatellitesByDateTimeCheckbox.set_tooltip_text( _( 
            "By default, satellites are sorted\n" + \
            "alphabetically by menu text.\n\n" + \
            "If checked, satellites will be\nsorted by rise date/time." ) )
        grid.attach( sortSatellitesByDateTimeCheckbox, 0, 6, 1, 1 )

        hideSatelliteIfNoVisiblePassCheckbox = Gtk.CheckButton( _( "Hide satellites which have no upcoming visible pass" ) )
        hideSatelliteIfNoVisiblePassCheckbox.set_margin_top( 15 )
        hideSatelliteIfNoVisiblePassCheckbox.set_active( self.hideSatelliteIfNoVisiblePass )
        hideSatelliteIfNoVisiblePassCheckbox.set_tooltip_text( _( 
            "If checked, only satellites with an\n" + \
            "upcoming visible pass are displayed.\n\n" + \
            "Otherwise, all passes, visible or not,\n" + \
            "are shown (including error messages)." ) )
        grid.attach( hideSatelliteIfNoVisiblePassCheckbox, 0, 7, 1, 1 )

        satellitesAddNewCheckbox = Gtk.CheckButton( _( "Automatically add new satellites" ) )
        satellitesAddNewCheckbox.set_margin_top( 15 )
        satellitesAddNewCheckbox.set_active( self.satellitesAddNew )
        satellitesAddNewCheckbox.set_tooltip_text( _( 
            "If checked, new satellites in the TLE data will\n" + \
            "be added to your list of checked satellites." ) )
        grid.attach( satellitesAddNewCheckbox, 0, 8, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 6 ) # Bug in Python - must specify the parameter names!
        box.set_margin_top( 15 )

        label = Gtk.Label( _( "Satellite 'on-click' URL" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        satelliteURLText = Gtk.Entry()
        satelliteURLText.set_text( self.satelliteOnClickURL )
        satelliteURLText.set_hexpand( True )
        satelliteURLText.set_tooltip_text( 
            "The URL used to lookup a satellite\n" + \
            "(in the default browser) when any of\n" + \
            "the satellite's child items are selected\n" + \
            "from the menu.\n\n" + \
            "If empty, no lookup will be done.\n\n" + \
            "Available tags:\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NAME + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NUMBER + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR )

        box.pack_start( satelliteURLText, True, True, 0 )

        reset = Gtk.Button( _( "Reset" ) )
        reset.connect( "clicked", self.onResetSatelliteOnClickURL, satelliteURLText )
        reset.set_tooltip_text( _( "Reset the satellite look-up URL to factory default." ) )
        box.pack_start( reset, False, False, 0 )

        grid.attach( box, 0, 9, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Menu" ) ) )

        # Planets/Stars.
        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 15 ) # Bug in Python - must specify the parameter names!

        planetStore = Gtk.ListStore( bool, str, str ) # Show/hide, planet name (not displayed), translated planet name.
        for planetName in IndicatorLunar.PLANETS:
            planetStore.append( [ planetName in self.planets, planetName, IndicatorLunar.PLANET_AND_MOON_NAMES[ planetName ] ] )

        tree = Gtk.TreeView( planetStore )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( _( 
            "Check a planet (or dwarf planet)\n" + \
            "to display in the menu.\n\n" + \
            "Clicking the header of the first\n" + \
            "column toggles all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onPlanetToggled, planetStore, displayTagsStore )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onToggle, planetStore, AstronomicalObjectType.Planet )
        tree.append_column( treeViewColumn )

        tree.append_column( Gtk.TreeViewColumn( _( "Planet" ), Gtk.CellRendererText(), text = 2 ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER )
        scrolledWindow.add( tree )

        box.pack_start( scrolledWindow, True, True, 0 )

        stars = [ ] # List of lists, each sublist containing star is checked flag, star name, star translated name.
        for starName in IndicatorLunar.STAR_NAMES.keys():
            stars.append( [ starName in self.stars, starName, IndicatorLunar.STAR_NAMES[ starName ] ] )

        stars = sorted( stars, key = lambda x: ( x[ 2 ] ) )
        starStore = Gtk.ListStore( bool, str, str ) # Show/hide, star name (not displayed), translated star name.
        for star in stars:
            starStore.append( star )

        tree = Gtk.TreeView( starStore )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( _( 
            "Check a star to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "toggles all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onStarToggled, starStore, displayTagsStore )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onToggle, starStore, AstronomicalObjectType.Star )
        tree.append_column( treeViewColumn )

        tree.append_column( Gtk.TreeViewColumn( _( "Star" ), Gtk.CellRendererText(), text = 2 ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        box.pack_start( scrolledWindow, True, True, 0 )

        notebook.append_page( box, Gtk.Label( _( "Planets / Stars" ) ) )

        # Orbital elements.
        orbitalElementGrid = Gtk.Grid()
        orbitalElementGrid.set_row_spacing( 10 )
        orbitalElementGrid.set_margin_bottom( 10 )

        orbitalElementStore = Gtk.ListStore( bool, str ) # Show/hide, orbital element name.

        orbitalElementStoreSort = Gtk.TreeModelSort( model = orbitalElementStore )
        orbitalElementStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( orbitalElementStoreSort )
        tree.set_tooltip_text( _( 
            "Check an orbital element to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "toggles all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onOrbitalElementToggled, orbitalElementStore, displayTagsStore, orbitalElementStoreSort )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onToggle, orbitalElementStore, AstronomicalObjectType.OrbitalElement )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = 1 )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( tree )
        orbitalElementGrid.attach( scrolledWindow, 0, 0, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 6 ) # Bug in Python - must specify the parameter names!
        box.set_margin_top( 10 )
        box.set_margin_left( 10 )
        box.set_margin_right( 10 )

        label = Gtk.Label( _( "Orbital element data" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        # Need a local copy of the orbital element URL and orbital element data.
        self.orbitalElementDataNew = self.orbitalElementData
        self.orbitalElementURLNew = self.orbitalElementURL

        orbitalElementURLEntry = Gtk.Entry()
        orbitalElementURLEntry.set_text( self.orbitalElementURL )
        orbitalElementURLEntry.set_hexpand( True )
        orbitalElementURLEntry.set_tooltip_text( _( 
            "The URL from which to source orbital element data.\n" + \
            "To specify a local file, use 'file:///'.\n\n" + \
            "The orbital element data will be automatically\n" + \
            "loaded each time the indicator is started\n" + \
            "and approximately every 24 hours thereafter." ) )
        box.pack_start( orbitalElementURLEntry, True, True, 0 )

        fetch = Gtk.Button( _( "Fetch" ) )
        fetch.set_tooltip_text( _( 
            "Retrieve the orbital element data from the URL.\n" + \
            "If the URL is empty, the default URL will be used." ) )
        fetch.connect( "clicked", self.onFetchOrbitalElementURL, orbitalElementURLEntry, orbitalElementGrid, orbitalElementStore, displayTagsStore )
        box.pack_start( fetch, False, False, 0 )

        orbitalElementGrid.attach( box, 0, 1, 1, 1 )

        label = Gtk.Label()
        label.set_margin_left( 10 )
        label.set_margin_right( 10 )
        label.set_justify( Gtk.Justification.CENTER )
        
        orbitalElementGrid.attach( label, 0, 2, 1, 1 )

        notebook.append_page( orbitalElementGrid, Gtk.Label( _( "Orbital Elements" ) ) )

        # Satellites.
        satelliteGrid = Gtk.Grid()
        satelliteGrid.set_row_spacing( 10 )
        satelliteGrid.set_margin_bottom( 10 )

        satelliteStore = Gtk.ListStore( bool, str, str, str ) # Show/hide, name, number, international designator.

        satelliteStoreSort = Gtk.TreeModelSort( model = satelliteStore )
        satelliteStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( satelliteStoreSort )
        tree.set_tooltip_text( _( 
            "Check a satellite to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "toggles all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onSatelliteToggled, satelliteStore, displayTagsStore, satelliteStoreSort )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onToggle, satelliteStore, AstronomicalObjectType.Satellite )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Satellite Name" ), Gtk.CellRendererText(), text = 1 )
        treeViewColumn.set_sort_column_id( 1 )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Number" ), Gtk.CellRendererText(), text = 2 ) 
        treeViewColumn.set_sort_column_id( 2 )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "International Designator" ), Gtk.CellRendererText(), text = 3 ) 
        treeViewColumn.set_sort_column_id( 3 )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( tree )
        satelliteGrid.attach( scrolledWindow, 0, 0, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 6 ) # Bug in Python - must specify the parameter names!
        box.set_margin_top( 10 )
        box.set_margin_left( 10 )
        box.set_margin_right( 10 )

        label = Gtk.Label( _( "Satellite TLE data" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        # Need a local copy of the satellite TLE URL and satellite TLE data.
        self.satelliteTLEDataNew = self.satelliteTLEData
        self.satelliteTLEURLNew = self.satelliteTLEURL

        TLEURLEntry = Gtk.Entry()
        TLEURLEntry.set_text( self.satelliteTLEURL )
        TLEURLEntry.set_hexpand( True )
        TLEURLEntry.set_tooltip_text( _( 
            "The URL from which to source TLE satellite data.\n" + \
            "To specify a local file, use 'file:///'.\n\n" + \
            "The satellite TLE data will be automatically\n" + \
            "loaded each time the indicator is started\n" + \
            "and approximately every 12 hours thereafter." ) )
        box.pack_start( TLEURLEntry, True, True, 0 )

        fetch = Gtk.Button( _( "Fetch" ) )
        fetch.set_tooltip_text( _( 
            "Retrieve the TLE data from the specified URL.\n" + \
            "If the URL is empty, the default URL will be used." ) )
        fetch.connect( "clicked", self.onFetchSatelliteTLEURL, TLEURLEntry, satelliteGrid, satelliteStore, displayTagsStore )
        box.pack_start( fetch, False, False, 0 )

        satelliteGrid.attach( box, 0, 1, 1, 1 )

        label = Gtk.Label()
        label.set_margin_left( 10 )
        label.set_margin_right( 10 )
        label.set_justify( Gtk.Justification.CENTER )
        
        satelliteGrid.attach( label, 0, 2, 1, 1 )

        notebook.append_page( satelliteGrid, Gtk.Label( _( "Satellites" ) ) )

        # OSD (satellite and full moon).
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showSatelliteNotificationCheckbox = Gtk.CheckButton( _( "Satellite rise" ) )
        showSatelliteNotificationCheckbox.set_active( self.showSatelliteNotification )
        showSatelliteNotificationCheckbox.set_tooltip_text( _( "Screen notification when a satellite rises above the horizon." ) )
        grid.attach( showSatelliteNotificationCheckbox, 0, 0, 2, 1 )
 
        label = Gtk.Label( _( "Summary" ) )
        label.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        label.set_halign( Gtk.Align.START )
        label.set_margin_left( 25 )
        grid.attach( label, 0, 1, 1, 1 )

        satelliteNotificationSummaryText = Gtk.Entry()
        satelliteNotificationSummaryText.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        satelliteNotificationSummaryText.set_text( self.satelliteNotificationSummary )
        satelliteNotificationSummaryText.set_tooltip_text(
            "The summary for the satellite rise notification.\n\n" + \
            "Available tags:\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NAME + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NUMBER + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_TIME + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_TIME + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_VISIBLE + \
            "\n\nFor formatting, refer to https://wiki.ubuntu.com/NotifyOSD" )

        grid.attach( satelliteNotificationSummaryText, 1, 1, 1, 1 )

        showSatelliteNotificationCheckbox.connect( "toggled", pythonutils.onCheckbox, label, satelliteNotificationSummaryText )

        label = Gtk.Label( _( "Message" ) )
        label.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        label.set_halign( Gtk.Align.START )
        label.set_margin_left( 25 )
        label.set_valign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        satelliteNotificationMessageText = Gtk.TextView()
        satelliteNotificationMessageText.get_buffer().set_text( self.satelliteNotificationMessage )
        satelliteNotificationMessageText.set_tooltip_text(
            "The message for the satellite rise notification.\n\n" + \
            "Available tags:\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NAME + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NUMBER + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_TIME + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_TIME + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_VISIBLE + \
            "\n\nFor formatting, refer to https://wiki.ubuntu.com/NotifyOSD" )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( satelliteNotificationMessageText )
        grid.attach( scrolledWindow, 1, 2, 1, 1 )

        showSatelliteNotificationCheckbox.connect( "toggled", pythonutils.onCheckbox, label, scrolledWindow )

        test = Gtk.Button( _( "Test" ) )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        test.connect( "clicked", self.onTestClicked, satelliteNotificationSummaryText, satelliteNotificationMessageText, False )
        test.set_tooltip_text( _( "Show the notification bubble.\nTags will be substituted with mock text." ) )
        grid.attach( test, 1, 3, 1, 1 )

        showSatelliteNotificationCheckbox.connect( "toggled", pythonutils.onCheckbox, test, test )

        separator = Gtk.Separator.new( Gtk.Orientation.HORIZONTAL )
        grid.attach( separator, 0, 4, 2, 1 )

        showWerewolfWarningCheckbox = Gtk.CheckButton( _( "Werewolf warning" ) )
        showWerewolfWarningCheckbox.set_active( self.showWerewolfWarning )
        showWerewolfWarningCheckbox.set_tooltip_text( _( 
            "Screen notification (approximately hourly)\n" + \
            "at full moon (or leading up to)." ) )
        grid.attach( showWerewolfWarningCheckbox, 0, 5, 2, 1 )

        label = Gtk.Label( _( "Illumination" ) )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        label.set_halign( Gtk.Align.START )
        label.set_margin_left( 25 )
        grid.attach( label, 0, 6, 1, 1 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.werewolfWarningStartIlluminationPercentage, 0, 100, 1, 0, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinner.set_value( self.werewolfWarningStartIlluminationPercentage ) # ...so need to force the initial value by explicitly setting it.
        spinner.set_tooltip_text( _( 
            "The notification commences at the\n" + \
            "specified illumination (%),\n" + \
            "starting after a new moon (0%)." ) )
        spinner.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        grid.attach( spinner, 1, 6, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, label, spinner )

        label = Gtk.Label( _( "Summary" ) )
        label.set_margin_left( 25 )
        label.set_halign( Gtk.Align.START )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        grid.attach( label, 0, 7, 1, 1 )

        werewolfNotificationSummaryText = Gtk.Entry()
        werewolfNotificationSummaryText.set_text( self.werewolfWarningSummary )
        werewolfNotificationSummaryText.set_tooltip_text( _( 
            "The summary for the werewolf notification.\n\n" + \
            "For formatting, refer to https://wiki.ubuntu.com/NotifyOSD" ) )
        werewolfNotificationSummaryText.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        grid.attach( werewolfNotificationSummaryText, 1, 7, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, label, werewolfNotificationSummaryText )

        label = Gtk.Label( _( "Message" ) )
        label.set_margin_left( 25 )
        label.set_halign( Gtk.Align.START )
        label.set_valign( Gtk.Align.START )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        grid.attach( label, 0, 8, 1, 1 )

        werewolfNotificationMessageText = Gtk.TextView()
        werewolfNotificationMessageText.get_buffer().set_text( self.werewolfWarningMessage )
        werewolfNotificationMessageText.set_tooltip_text( _( 
            "The message for the werewolf notification.\n\n" + \
            "For formatting, refer to https://wiki.ubuntu.com/NotifyOSD" ) )
        werewolfNotificationMessageText.set_sensitive( showWerewolfWarningCheckbox.get_active() )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( werewolfNotificationMessageText )
        grid.attach( scrolledWindow, 1, 8, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, label, werewolfNotificationMessageText )

        test = Gtk.Button( _( "Test" ) )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        test.connect( "clicked", self.onTestClicked, werewolfNotificationSummaryText, werewolfNotificationMessageText, True )
        test.set_tooltip_text( _( "Show the notification using the current settings." ) )
        grid.attach( test, 1, 9, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, test, test )

        notebook.append_page( grid, Gtk.Label( _( "Notifications" ) ) )

        # Location.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( _( "City" ) )
        label.set_halign( Gtk.Align.START )

        grid.attach( label, 0, 0, 1, 1 )

        global _city_data
        cities = sorted( _city_data.keys(), key = locale.strxfrm )
        city = Gtk.ComboBoxText.new_with_entry()
        city.set_tooltip_text( _( 
            "To reset the cities to default lat/long/elev,\n" + \
            "add a bogus city and restart the indicator." ) )
        for c in cities:
            city.append_text( c )

        grid.attach( city, 1, 0, 1, 1 )

        label = Gtk.Label( _( "Latitude (DD)" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        latitude = Gtk.Entry()
        latitude.set_tooltip_text( _( "Latitude of your location in decimal degrees." ) )
        grid.attach( latitude, 1, 1, 1, 1 )

        label = Gtk.Label( _( "Longitude (DD)" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        longitude = Gtk.Entry()
        longitude.set_tooltip_text( _( "Longitude of your location in decimal degrees." ) )
        grid.attach( longitude, 1, 2, 1, 1 )

        label = Gtk.Label( _( "Elevation (m)" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        elevation = Gtk.Entry()
        elevation.set_tooltip_text( _( "Height in metres above sea level." ) )
        grid.attach( elevation, 1, 3, 1, 1 )

        city.connect( "changed", self.onCityChanged, latitude, longitude, elevation )
        city.set_active( cities.index( self.cityName ) )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( os.path.exists( IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE ) )
        autostartCheckbox.set_margin_top( 20 )
        grid.attach( autostartCheckbox, 0, 4, 2, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        self.dialog = Gtk.Dialog( _( "Preferences" ), None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorLunar.ICON )
        self.dialog.show_all()

        # Some GUI elements will be hidden, which must be done after the dialog is shown.
        self.updateOrbitalElementPreferencesTab( orbitalElementGrid, orbitalElementStore, self.orbitalElementData, self.orbitalElements, orbitalElementURLEntry.get_text().strip() )
        self.updateSatellitePreferencesTab( satelliteGrid, satelliteStore, self.satelliteTLEData, self.satellites, TLEURLEntry.get_text().strip() )

        while True:
            if self.dialog.run() != Gtk.ResponseType.OK: break

            if satelliteMenuText.get_text().strip() == "":
                pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, _( "Satellite menu text cannot be empty." ) )
                notebook.set_current_page( 1 )
                satelliteMenuText.grab_focus()
                continue

            cityValue = city.get_active_text()
            if cityValue == "":
                pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, _( "City cannot be empty." ) )
                notebook.set_current_page( 5 )
                city.grab_focus()
                continue

            latitudeValue = latitude.get_text().strip()
            if latitudeValue == "" or not pythonutils.isNumber( latitudeValue ) or float( latitudeValue ) > 90 or float( latitudeValue ) < -90:
                pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, _( "Latitude must be a number between 90 and -90 inclusive." ) )
                notebook.set_current_page( 5 )
                latitude.grab_focus()
                continue

            longitudeValue = longitude.get_text().strip()
            if longitudeValue == "" or not pythonutils.isNumber( longitudeValue ) or float( longitudeValue ) > 180 or float( longitudeValue ) < -180:
                pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, _( "Longitude must be a number between 180 and -180 inclusive." ) )
                notebook.set_current_page( 5 )
                longitude.grab_focus()
                continue

            elevationValue = elevation.get_text().strip()
            if elevationValue == "" or not pythonutils.isNumber( elevationValue ) or float( elevationValue ) > 10000 or float( elevationValue ) < 0:
                pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, _( "Elevation must be a number number between 0 and 10000 inclusive." ) )
                notebook.set_current_page( 5 )
                elevation.grab_focus()
                continue

# TODO Need to parse this to swap out the translated tags.
#Make use of the list store somehow???
#Maybe the same functionality can be used for the actual icon text tag substitution?
#             self.indicatorText = indicatorText.get_text().strip()
            self.showPlanetsAsSubMenu = showPlanetsAsSubmenuCheckbox.get_active()
            self.showStarsAsSubMenu = showStarsAsSubmenuCheckbox.get_active()
            self.showOrbitalElementsAsSubMenu = showOrbitalElementsAsSubmenuCheckbox.get_active()
            self.orbitalElementsAddNew = orbitalElementsAddNewCheckbox.get_active()
            self.orbitalElementsMagnitude = spinnerOrbitalElementMagnitude.get_value_as_int()
            self.hideBodyIfNeverUp = hideBodyIfNeverUpCheckbox.get_active()
            self.satelliteMenuText = satelliteMenuText.get_text().strip()
            self.showSatellitesAsSubMenu = showSatellitesAsSubmenuCheckbox.get_active()
            self.satellitesAddNew = satellitesAddNewCheckbox.get_active()
            self.satellitesSortByDateTime = sortSatellitesByDateTimeCheckbox.get_active()
            self.hideSatelliteIfNoVisiblePass = hideSatelliteIfNoVisiblePassCheckbox.get_active()
            self.satelliteOnClickURL = satelliteURLText.get_text().strip()

            self.planets = [ ]
            for row in planetStore:
                if row[ 0 ]: self.planets.append( row[ 1 ] )

            self.stars = [ ]
            for row in starStore:
                if row[ 0 ]: self.stars.append( row[ 1 ] )

            if self.orbitalElementURLNew is not None: # The URL will only be None on intialisation.
                self.orbitalElementURL = self.orbitalElementURLNew # The URL could still be invalid, but it will not be None.
  
            if self.orbitalElementDataNew is None:
                self.orbitalElementData = { } # The retrieved orbital element data was bad, so reset to empty data.
            else:
                self.orbitalElementData = self.orbitalElementDataNew # The retrieved orbital element data is good (but still could be empty).

            self.orbitalElements = [ ]
            for orbitalElement in orbitalElementStore:
                if orbitalElement[ 0 ]:
                    self.orbitalElements.append( orbitalElement[ 1 ].upper() )

            if self.satelliteTLEURLNew is not None: # The URL will only be None on intialisation.
                self.satelliteTLEURL = self.satelliteTLEURLNew # The URL could still be invalid, but it will not be None.
  
            if self.satelliteTLEDataNew is None:
                self.satelliteTLEData = { } # The retrieved TLE data was bad, so reset to empty data.
            else:
                self.satelliteTLEData = self.satelliteTLEDataNew # The retrieved TLE data is good (but still could be empty).

            self.satellites = [ ]
            for satelliteTLE in satelliteStore:
                if satelliteTLE[ 0 ]:
                    self.satellites.append( ( satelliteTLE[ 1 ].upper(), satelliteTLE[ 2 ] ) )

            self.showSatelliteNotification = showSatelliteNotificationCheckbox.get_active()
            self.satelliteNotificationSummary = satelliteNotificationSummaryText.get_text()
            self.satelliteNotificationMessage = pythonutils.getTextViewText( satelliteNotificationMessageText )

            self.showWerewolfWarning = showWerewolfWarningCheckbox.get_active()
            self.werewolfWarningStartIlluminationPercentage = spinner.get_value_as_int()
            self.werewolfWarningSummary = werewolfNotificationSummaryText.get_text()
            self.werewolfWarningMessage = pythonutils.getTextViewText( werewolfNotificationMessageText )

            self.cityName = cityValue
            _city_data[ self.cityName ] = ( str( latitudeValue ), str( longitudeValue ), float( elevationValue ) )

            self.saveSettings()

            if not os.path.exists( IndicatorLunar.AUTOSTART_PATH ): os.makedirs( IndicatorLunar.AUTOSTART_PATH )
            if autostartCheckbox.get_active():
                try:
                    shutil.copy( IndicatorLunar.DESKTOP_PATH + IndicatorLunar.DESKTOP_FILE, IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE )
                except Exception as e:
                    logging.exception( e )
            else:
                try:
                    os.remove( IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE )
                except: pass

            self.data = { } # Erase the data as the user may have changed the satellites and/or location.
            break

        self.lock.release()
        self.update()
        self.dialog.destroy()
        self.dialog = None


    # Refreshes the display tags with all data.
    # If the user has done a fetch of new satellite or orbital element data, the new data is added instead.
    def updateDisplayTags( self, displayTagsStore, satelliteTLEData, orbitalElementData ):
        displayTagsStore.clear() # List of lists, each sublist contains the tag, translated tag, value.
        for key in self.data.keys():
            if ( key[ 0 ], key[ 1 ] ) in self.satellites: # This key refers to a satellite.
                if satelliteTLEData is None:
                    displayTagsStore.append( [ " ".join( key ), " ".join( key ), self.data[ key ] ] )
            elif ( key[ 0 ] ) in self.orbitalElements: # This key refers to an orbital element.
                if orbitalElementData is None:
                    displayTagsStore.append( [ " ".join( key ), " ".join( key ), self.data[ key ] ] )
            else:
                # Neither satellite nor orbital element.
                if key[ 1 ] == IndicatorLunar.DATA_CITY_NAME: # Special case: the city name data tag has no associated body tag.
                    displayTagsStore.append( [ key[ 1 ], IndicatorLunar.DATA_TAGS[ key[ 1 ] ], self.data[ key ] ] )
                else:
                    displayTagsStore.append( [ " ".join( key ), IndicatorLunar.BODY_TAGS[ key[ 0 ] ] + " " + IndicatorLunar.DATA_TAGS[ key[ 1 ] ], self.data[ key ] ] )

        # Check if new satellite TLE data is being added...
        if satelliteTLEData is not None:
            for key in satelliteTLEData:
                displayTagsStore.append( [ " ".join( key ), " ".join( key ), IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )

        # Check if new orbital element data is being added...
        if orbitalElementData is not None:
            for key in orbitalElementData:
                displayTagsStore.append( [ key, key, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )


    def onToggle( self, widget, dataStore, astronomicalObjectType ):
        if astronomicalObjectType == AstronomicalObjectType.OrbitalElement:
            self.toggleOrbitalElementsTable = not self.toggleOrbitalElementsTable
            toggle = self.toggleOrbitalElementsTable

        elif astronomicalObjectType == AstronomicalObjectType.Planet:
            self.togglePlanetsTable = not self.togglePlanetsTable
            toggle = self.togglePlanetsTable

        elif astronomicalObjectType == AstronomicalObjectType.Satellite:
            self.toggleSatellitesTable = not self.toggleSatellitesTable
            toggle = self.toggleSatellitesTable

        else: # Assume stars. 
            self.toggleStarsTable = not self.toggleStarsTable
            toggle = self.toggleStarsTable

        for row in dataStore:
            row[ 0 ] = toggle


    def updateOrbitalElementPreferencesTab( self, grid, orbitalElementStore, orbitalElementData, orbitalElements, url ):
        if orbitalElementData is None:
            message = "Cannot access the orbital element data source\n<a href=\'" + url + "'>" + url + "</a>"
        elif len( orbitalElementData ) == 0:
            message = "No orbital element data found at\n<a href=\'" + url + "'>" + url + "</a>"
        else:
            orbitalElementStore.clear()
            message = None
            for key in orbitalElementData:
                orbitalElement = orbitalElementData[ key ]
                displayName = self.getOrbitalElementDisplayName( orbitalElement )
                orbitalElementStore.append( [ key in orbitalElements, displayName ] )

        # Ideally grid.get_child_at() should be used to get the Label and ScrolledWindow...but this does not work on Ubuntu 12.04.
        children = grid.get_children()
        for child in children:
            if child.__class__.__name__ == "Label":
                if message is None:
                    child.hide()
                else:
                    child.show()
                    child.set_markup( message )
            elif child.__class__.__name__ == "ScrolledWindow":
                if message is None:
                    child.show()
                else:
                    child.hide()


    def updateSatellitePreferencesTab( self, grid, satelliteStore, satelliteTLEData, satellites, url ):
        if satelliteTLEData is None:
            message = "Cannot access the TLE data source\n<a href=\'" + url + "'>" + url + "</a>"
        elif len( satelliteTLEData ) == 0:
            message = "No TLE data found at\n<a href=\'" + url + "'>" + url + "</a>"
        else:
            satelliteStore.clear()
            message = None
            for key in satelliteTLEData:
                tle = satelliteTLEData[ key ]
                checked = ( tle.getName().upper(), tle.getNumber() ) in satellites
                satelliteStore.append( [ checked, tle.getName(), tle.getNumber(), tle.getInternationalDesignator() ] )

        children = grid.get_children()
        for child in children:
            if child.__class__.__name__ == "Label":
                if message is None:
                    child.hide()
                else:
                    child.show()
                    child.set_markup( message )
            elif child.__class__.__name__ == "ScrolledWindow":
                if message is None:
                    child.show()
                else:
                    child.hide()


    def onIndicatorTextTagDoubleClick( self, tree, rowNumber, treeViewColumn, indicatorTextEntry ):
        model, treeiter = tree.get_selection().get_selected()
        indicatorTextEntry.insert_text( "[" + model[ treeiter ][ 1 ] + "]", indicatorTextEntry.get_position() )


    def onResetSatelliteOnClickURL( self, button, textEntry ): textEntry.set_text( IndicatorLunar.SATELLITE_ON_CLICK_URL )


    def onFetchOrbitalElementURL( self, button, entry, grid, orbitalElementStore, displayTagsStore ):
        if entry.get_text().strip() == "":
            entry.set_text( IndicatorLunar.ORBITAL_ELEMENT_DATA_URL )

        self.orbitalElementURLNew = entry.get_text().strip()
        self.orbitalElementDataNew = self.getOrbitalElementData( self.orbitalElementURLNew ) # The orbital element data can be None, empty or non-empty.

        # When fetching new data, by default check all the data.
        orbitalElements = [ ]
        if self.orbitalElementDataNew is not None:
            for key in self.orbitalElementDataNew:
                orbitalElements.append( key )

        self.updateOrbitalElementPreferencesTab( grid, orbitalElementStore, self.orbitalElementDataNew, orbitalElements, self.orbitalElementURLNew )
        self.updateDisplayTags( displayTagsStore, None, self.orbitalElementDataNew )


    def onFetchSatelliteTLEURL( self, button, entry, grid, satelliteStore, displayTagsStore ):
        if entry.get_text().strip() == "":
            entry.set_text( IndicatorLunar.SATELLITE_TLE_URL )

        self.satelliteTLEURLNew = entry.get_text().strip()
        self.satelliteTLEDataNew = self.getSatelliteTLEData( self.satelliteTLEURLNew ) # The TLE data can be None, empty or non-empty.

        # When fetching new data, by default check all the data.
        satellites = [ ]
        if self.satelliteTLEDataNew is not None:
            for key in self.satelliteTLEDataNew:
                satellites.append( key )

        self.updateSatellitePreferencesTab( grid, satelliteStore, self.satelliteTLEDataNew, satellites, self.satelliteTLEURLNew )
        self.updateDisplayTags( displayTagsStore, self.satelliteTLEDataNew, None )


    def onTestClicked( self, button, summaryEntry, messageTextView, isFullMoon ):
        summary = summaryEntry.get_text()
        message = pythonutils.getTextViewText( messageTextView )

        if isFullMoon:
            self.createIcon( 100, None )
            svgFile = IndicatorLunar.SVG_FULL_MOON_FILE
        else:
            svgFile = IndicatorLunar.SVG_SATELLITE_ICON

            # Mock data...
            summary = summary. \
                replace( IndicatorLunar.SATELLITE_TAG_NAME, "ISS (ZARYA)" ). \
                replace( IndicatorLunar.SATELLITE_TAG_NUMBER, "25544" ). \
                replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, "1998-067A" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH, "123.45°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME, self.localiseAndTrim( ephem.now() ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH, "321.54°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME, self.localiseAndTrim( ephem.Date( ephem.now() + 10 * ephem.minute ) ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_VISIBLE, "True" )

            message = message. \
                replace( IndicatorLunar.SATELLITE_TAG_NAME, "ISS (ZARYA)" ). \
                replace( IndicatorLunar.SATELLITE_TAG_NUMBER, "25544" ). \
                replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, "1998-067A" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH, "123.45°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME, self.localiseAndTrim( ephem.now() ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH, "321.54°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME, self.localiseAndTrim( ephem.Date( ephem.now() + 10 * ephem.minute ) ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_VISIBLE, "True" )

        if summary == "": summary = " " # The notification summary text must not be empty (at least on Unity).

        Notify.Notification.new( summary, message, svgFile ).show()

        if isFullMoon: os.remove( svgFile )


    def onPlanetToggled( self, widget, 
                         path, # Index to the selected row in the table. 
                         planetStore, # List of lists, each sublist contains checked flag, planet name, translated planet name.
                         displayTagsStore ): # List of lists, each sublist contains the tag, translated tag, value.
        planetStore[ path ][ 0 ] = not planetStore[ path ][ 0 ]
        planetName = planetStore[ path ][ 1 ].upper()

        if planetStore[ path ][ 0 ]: # Item has been checked, so add in a default value for each tag.
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_ILLUMINATION, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_ILLUMINATION ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_CONSTELLATION, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_CONSTELLATION ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_MAGNITUDE, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_MAGNITUDE ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_TROPICAL_SIGN, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_TROPICAL_SIGN ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_DISTANCE_TO_EARTH, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_DISTANCE_TO_EARTH ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_DISTANCE_TO_SUN, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_DISTANCE_TO_SUN ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_BRIGHT_LIMB, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_BRIGHT_LIMB ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_RIGHT_ASCENSION, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_RIGHT_ASCENSION ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_DECLINATION, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_DECLINATION ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_AZIMUTH, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_AZIMUTH ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_ALTITUDE, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_ALTITUDE ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )

            if ( planetName, IndicatorLunar.DATA_MESSAGE ) in self.data:
                displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_MESSAGE, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_MESSAGE ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            else:
                displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_RISE_TIME, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_RISE_TIME ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
                displayTagsStore.append( [ planetName + " " + IndicatorLunar.DATA_SET_TIME, IndicatorLunar.PLANET_AND_MOON_TAGS[ planetName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_SET_TIME ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
        else: # Item has been unchecked, so remove.
            iter = displayTagsStore.get_iter_first()
            while iter is not None:
                if displayTagsStore[ iter ][ 0 ].startswith( planetName ):
                    if displayTagsStore.remove( iter ) == False: iter = None # Remove returns True if there are more items (and iter automatically moves to that item).
                else:
                    iter = displayTagsStore.iter_next( iter )


    def onStarToggled( self, widget, 
                       path, # Index to the selected row in the table. 
                       starStore, # List of lists, each sublist contains checked flag, star name, translated star name.
                       displayTagsStore ): # List of lists, each sublist contains the tag, translated tag, value.
        starStore[ path ][ 0 ] = not starStore[ path ][ 0 ]
        starName = starStore[ path ][ 1 ].upper()

        if starStore[ path ][ 0 ]: # Item has been checked, so add in a default value for each tag.
            displayTagsStore.append( [ starName + " " + IndicatorLunar.DATA_CONSTELLATION, IndicatorLunar.STAR_TAGS[ starName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_CONSTELLATION ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + " " + IndicatorLunar.DATA_MAGNITUDE, IndicatorLunar.STAR_TAGS[ starName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_MAGNITUDE ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + " " + IndicatorLunar.DATA_RIGHT_ASCENSION, IndicatorLunar.STAR_TAGS[ starName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_RIGHT_ASCENSION ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + " " + IndicatorLunar.DATA_DECLINATION, IndicatorLunar.STAR_TAGS[ starName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_DECLINATION ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + " " + IndicatorLunar.DATA_AZIMUTH, IndicatorLunar.STAR_TAGS[ starName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_AZIMUTH ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + " " + IndicatorLunar.DATA_ALTITUDE, IndicatorLunar.STAR_TAGS[ starName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_ALTITUDE ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )

            if ( starName, IndicatorLunar.DATA_MESSAGE ) in self.data:
                displayTagsStore.append( [ starName + " " + IndicatorLunar.DATA_MESSAGE, IndicatorLunar.STAR_TAGS[ starName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_MESSAGE ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            else:
                displayTagsStore.append( [ starName + " " + IndicatorLunar.DATA_RISE_TIME, IndicatorLunar.STAR_TAGS[ starName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_RISE_TIME ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
                displayTagsStore.append( [ starName + " " + IndicatorLunar.DATA_SET_TIME, IndicatorLunar.STAR_TAGS[ starName ] + " " + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_SET_TIME ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
        else: # Item has been unchecked, so remove.
            iter = displayTagsStore.get_iter_first()
            while iter is not None:
                if displayTagsStore[ iter ][ 0 ].startswith( starName ):
                    if displayTagsStore.remove( iter ) == False: iter = None # Remove returns True if there are more items (and iter automatically moves to that item).
                else:
                    iter = displayTagsStore.iter_next( iter )


    def onOrbitalElementToggled( self, widget, path, orbitalElementStore, displayTagsStore, orbitalElementStoreSort ):
        childPath = orbitalElementStoreSort.convert_path_to_child_path( Gtk.TreePath.new_from_string( path ) ) # Convert sorted model index to underlying (child) model index.
        orbitalElementStore[ childPath ][ 0 ] = not orbitalElementStore[ childPath ][ 0 ]
        orbitalElementName = orbitalElementStore[ childPath ][ 1 ].upper() + " "

        if orbitalElementStore[ childPath ][ 1 ]:
            displayTagsStore.append( [ orbitalElementName + IndicatorLunar.DATA_RISE_TIME, orbitalElementName + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_RISE_TIME ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ orbitalElementName + IndicatorLunar.DATA_RISE_AZIMUTH, orbitalElementName + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_RISE_AZIMUTH ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ orbitalElementName + IndicatorLunar.DATA_SET_TIME, orbitalElementName + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_SET_TIME ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ orbitalElementName + IndicatorLunar.DATA_SET_AZIMUTH, orbitalElementName + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_SET_AZIMUTH ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
        else:
            iter = displayTagsStore.get_iter_first()
            while iter is not None:
                if displayTagsStore[ iter ][ 0 ].startswith( orbitalElementName ):
                    if displayTagsStore.remove( iter ) == False: iter = None # Remove returns True if there are more items (and iter automatically moves to that item).
                else:
                    iter = displayTagsStore.iter_next( iter )


    def onSatelliteToggled( self, widget, path, satelliteStore, displayTagsStore, satelliteStoreSort ):
        childPath = satelliteStoreSort.convert_path_to_child_path( Gtk.TreePath.new_from_string( path ) ) # Convert sorted model index to underlying (child) model index.
        satelliteStore[ childPath ][ 0 ] = not satelliteStore[ childPath ][ 0 ]
        satelliteNameNumber = satelliteStore[ childPath ][ 1 ].upper() + " " + satelliteStore[ childPath ][ 2 ] + " "

        if satelliteStore[ childPath ][ 2 ]:
            displayTagsStore.append( [ satelliteNameNumber + IndicatorLunar.DATA_RISE_TIME, satelliteNameNumber + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_RISE_TIME ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ satelliteNameNumber + IndicatorLunar.DATA_RISE_AZIMUTH, satelliteNameNumber + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_RISE_AZIMUTH ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ satelliteNameNumber + IndicatorLunar.DATA_SET_TIME, satelliteNameNumber + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_SET_TIME ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ satelliteNameNumber + IndicatorLunar.DATA_SET_AZIMUTH, satelliteNameNumber + IndicatorLunar.DATA_TAGS[ IndicatorLunar.DATA_SET_AZIMUTH ], IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
        else:
            iter = displayTagsStore.get_iter_first()
            while iter is not None:
                if displayTagsStore[ iter ][ 0 ].startswith( satelliteNameNumber ):
                    if displayTagsStore.remove( iter ) == False: iter = None # Remove returns True if there are more items (and iter automatically moves to that item).
                else:
                    iter = displayTagsStore.iter_next( iter )


    def onCityChanged( self, combobox, latitude, longitude, elevation ):
        city = combobox.get_active_text()
        global _city_data
        if city != "" and city in _city_data:
            latitude.set_text( _city_data.get( city )[ 0 ] )
            longitude.set_text( _city_data.get( city )[ 1 ] )
            elevation.set_text( str( _city_data.get( city )[ 2 ] ) )


    # Returns a dict/hashtable of the orbital elements (comets) data from the specified URL (may be empty).
    # On error, returns None.
    def getOrbitalElementData( self, url ):
        try:
            # Orbital elements are read from a URL which assumes the XEphem format.
            # For example
            #    C/2002 Y1 (Juels-Holvorcem),e,103.7816,166.2194,128.8232,242.5695,0.0002609,0.99705756,0.0000,04/13.2508/2003,2000,g  6.5,4.0
            # in which the first field (up to the first ',' is the name.
            # Any line beginninng with a '#' is considered a comment and ignored.
            orbitalElementsData = { } # Key: orbital element name, upper cased ; Value: entire orbital element string.
            data = urlopen( url ).read().decode( "utf8" ).splitlines()
            for i in range( 0, len( data ) ):
                if not data[ i ].startswith( "#" ):
                    orbitalElementName = data[ i ][ 0 : data[ i ].index( "," ) ] 
                    orbitalElementsData[ orbitalElementName.upper() ] = data[ i ]

        except Exception as e:
            orbitalElementsData = None # Indicates error.
            logging.exception( e )
            logging.error( "Error retrieving orbital element data from " + str( url ) )

        return orbitalElementsData


    def getOrbitalElementDisplayName( self, orbitalElement ): return orbitalElement[ 0 : orbitalElement.index( "," ) ]


    # Returns a dict/hashtable of the satellite TLE data from the specified URL (may be empty).
    # On error, returns None.
    def getSatelliteTLEData( self, url ):
        try:
            satelliteTLEData = { } # Key: ( satellite name, satellite number ) ; Value: satellite.TLE object.
            data = urlopen( url ).read().decode( "utf8" ).splitlines()
            for i in range( 0, len( data ), 3 ):
                tle = satellite.TLE( data[ i ].strip(), data[ i + 1 ].strip(), data[ i + 2 ].strip() )
                satelliteTLEData[ ( tle.getName().upper(), tle.getNumber() ) ] = tle

        except Exception as e:
            satelliteTLEData = None # Indicates error.
            logging.exception( e )
            logging.error( "Error retrieving satellite TLE data from " + str( url ) )

        return satelliteTLEData


    def getDefaultCity( self ):
        try:
            p = subprocess.Popen( "cat /etc/timezone", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
            timezone = p.communicate()[ 0 ].decode()
            self.cityName = None
            global _city_data
            for city in _city_data.keys():
                if city in timezone:
                    self.cityName = city
                    break

            if self.cityName is None or self.cityName == "":
                self.cityName = sorted( _city_data.keys(), key = locale.strxfrm )[ 0 ]

        except Exception as e:
            logging.exception( e )
            logging.error( "Error getting default city." )
            self.cityName = sorted( _city_data.keys(), key = locale.strxfrm )[ 0 ]


    def loadSettings( self ):
        self.getDefaultCity()
        self.hideBodyIfNeverUp = True
        self.hideSatelliteIfNoVisiblePass = True
        self.indicatorText = IndicatorLunar.INDICATOR_TEXT_DEFAULT
        self.orbitalElements = [ ]
        self.orbitalElementsAddNew = False
        self.orbitalElementsMagnitude = 6 # More or less what's visible with the naked eye or binoculars.
        self.orbitalElementURL = IndicatorLunar.ORBITAL_ELEMENT_DATA_URL

        self.planets = [ ]
        for planetName in IndicatorLunar.PLANETS:
            self.planets.append( planetName )

        self.satelliteMenuText = IndicatorLunar.SATELLITE_MENU_TEXT_DEFAULT
        self.satelliteNotificationMessage = IndicatorLunar.SATELLITE_NOTIFICATION_MESSAGE_DEFAULT
        self.satelliteNotificationSummary = IndicatorLunar.SATELLITE_NOTIFICATION_SUMMARY_DEFAULT
        self.satelliteOnClickURL = IndicatorLunar.SATELLITE_ON_CLICK_URL
        self.satelliteTLEURL = IndicatorLunar.SATELLITE_TLE_URL
        self.satellites = [ ]
        self.satellitesAddNew = False
        self.satellitesSortByDateTime = True
        self.showOrbitalElementsAsSubMenu = True
        self.showPlanetsAsSubMenu = False
        self.showSatelliteNotification = True
        self.showSatellitesAsSubMenu = True
        self.showStarsAsSubMenu = True
        self.showWerewolfWarning = True
        self.stars = [ ]
        self.werewolfWarningStartIlluminationPercentage = 99
        self.werewolfWarningMessage = IndicatorLunar.WEREWOLF_WARNING_MESSAGE_DEFAULT
        self.werewolfWarningSummary = IndicatorLunar.WEREWOLF_WARNING_SUMMARY_DEFAULT

        if not os.path.isfile( IndicatorLunar.SETTINGS_FILE ): return

        try:
            with open( IndicatorLunar.SETTINGS_FILE, "r" ) as f: settings = json.load( f )

            global _city_data
            cityElevation = settings.get( IndicatorLunar.SETTINGS_CITY_ELEVATION, _city_data.get( self.cityName )[ 2 ] )
            cityLatitude = settings.get( IndicatorLunar.SETTINGS_CITY_LATITUDE, _city_data.get( self.cityName )[ 0 ] )
            cityLongitude = settings.get( IndicatorLunar.SETTINGS_CITY_LONGITUDE, _city_data.get( self.cityName )[ 1 ] )
            self.cityName = settings.get( IndicatorLunar.SETTINGS_CITY_NAME, self.cityName )
            _city_data[ self.cityName ] = ( str( cityLatitude ), str( cityLongitude ), float( cityElevation ) ) # Insert/overwrite the cityName and information into the cities.

            self.hideBodyIfNeverUp = settings.get( IndicatorLunar.SETTINGS_HIDE_BODY_IF_NEVER_UP, self.hideBodyIfNeverUp )
            self.hideSatelliteIfNoVisiblePass = settings.get( IndicatorLunar.SETTINGS_HIDE_SATELLITE_IF_NO_VISIBLE_PASS, self.hideSatelliteIfNoVisiblePass )
            self.indicatorText = settings.get( IndicatorLunar.SETTINGS_INDICATOR_TEXT, self.indicatorText )
            self.orbitalElementURL = settings.get( IndicatorLunar.SETTINGS_ORBITAL_ELEMENT_URL, self.orbitalElementURL )
            self.orbitalElements = settings.get( IndicatorLunar.SETTINGS_ORBITAL_ELEMENTS, self.orbitalElements )
            self.orbitalElementsAddNew = settings.get( IndicatorLunar.SETTINGS_ORBITAL_ELEMENTS_ADD_NEW, self.orbitalElementsAddNew )
            self.orbitalElementsMagnitude = settings.get( IndicatorLunar.SETTINGS_ORBITAL_ELEMENTS_MAGNITUDE, self.orbitalElementsMagnitude )
            self.planets = settings.get( IndicatorLunar.SETTINGS_PLANETS, self.planets )
            self.satelliteMenuText = settings.get( IndicatorLunar.SETTINGS_SATELLITE_MENU_TEXT, self.satelliteMenuText )
            self.satelliteNotificationMessage = settings.get( IndicatorLunar.SETTINGS_SATELLITE_NOTIFICATION_MESSAGE, self.satelliteNotificationMessage )
            self.satelliteNotificationSummary = settings.get( IndicatorLunar.SETTINGS_SATELLITE_NOTIFICATION_SUMMARY, self.satelliteNotificationSummary )
            self.satelliteOnClickURL = settings.get( IndicatorLunar.SETTINGS_SATELLITE_ON_CLICK_URL, self.satelliteOnClickURL )
            self.satelliteTLEURL = settings.get( IndicatorLunar.SETTINGS_SATELLITE_TLE_URL, self.satelliteTLEURL )

            self.satellites = settings.get( IndicatorLunar.SETTINGS_SATELLITES, self.satellites )
            self.satellites = [ tuple( l ) for l in self.satellites ] # Converts from a list of lists to a list of tuples...go figure!

            self.satellitesAddNew = settings.get( IndicatorLunar.SETTINGS_SATELLITES_ADD_NEW, self.satellitesAddNew )
            self.satellitesSortByDateTime = settings.get( IndicatorLunar.SETTINGS_SATELLITES_SORT_BY_DATE_TIME, self.satellitesSortByDateTime )
            self.showOrbitalElementsAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_ORBITAL_ELEMENTS_AS_SUBMENU, self.showOrbitalElementsAsSubMenu )
            self.showPlanetsAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_PLANETS_AS_SUBMENU, self.showPlanetsAsSubMenu )
            self.showSatelliteNotification = settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITE_NOTIFICATION, self.showSatelliteNotification )
            self.showSatellitesAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITES_AS_SUBMENU, self.showSatellitesAsSubMenu )
            self.showStarsAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_STARS_AS_SUBMENU, self.showStarsAsSubMenu )
            self.showWerewolfWarning = settings.get( IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING, self.showWerewolfWarning )
            self.stars = settings.get( IndicatorLunar.SETTINGS_STARS, self.stars )
            self.werewolfWarningStartIlluminationPercentage = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE, self.werewolfWarningStartIlluminationPercentage )
            self.werewolfWarningMessage = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_MESSAGE, self.werewolfWarningMessage )
            self.werewolfWarningSummary = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_SUMMARY, self.werewolfWarningSummary )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error reading settings: " + IndicatorLunar.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorLunar.SETTINGS_CITY_ELEVATION: _city_data.get( self.cityName )[ 2 ],
                IndicatorLunar.SETTINGS_CITY_LATITUDE: _city_data.get( self.cityName )[ 0 ],
                IndicatorLunar.SETTINGS_CITY_LONGITUDE: _city_data.get( self.cityName )[ 1 ],
                IndicatorLunar.SETTINGS_CITY_NAME: self.cityName,
                IndicatorLunar.SETTINGS_HIDE_BODY_IF_NEVER_UP: self.hideBodyIfNeverUp,
                IndicatorLunar.SETTINGS_HIDE_SATELLITE_IF_NO_VISIBLE_PASS: self.hideSatelliteIfNoVisiblePass,
                IndicatorLunar.SETTINGS_INDICATOR_TEXT: self.indicatorText,
                IndicatorLunar.SETTINGS_ORBITAL_ELEMENT_URL: self.orbitalElementURL,
                IndicatorLunar.SETTINGS_ORBITAL_ELEMENTS: self.orbitalElements,
                IndicatorLunar.SETTINGS_ORBITAL_ELEMENTS_ADD_NEW: self.orbitalElementsAddNew,
                IndicatorLunar.SETTINGS_ORBITAL_ELEMENTS_MAGNITUDE: self.orbitalElementsMagnitude,
                IndicatorLunar.SETTINGS_PLANETS: self.planets,
                IndicatorLunar.SETTINGS_SATELLITE_MENU_TEXT: self.satelliteMenuText,
                IndicatorLunar.SETTINGS_SATELLITE_NOTIFICATION_MESSAGE: self.satelliteNotificationMessage,
                IndicatorLunar.SETTINGS_SATELLITE_NOTIFICATION_SUMMARY: self.satelliteNotificationSummary,
                IndicatorLunar.SETTINGS_SATELLITE_ON_CLICK_URL: self.satelliteOnClickURL,
                IndicatorLunar.SETTINGS_SATELLITE_TLE_URL: self.satelliteTLEURL,
                IndicatorLunar.SETTINGS_SATELLITES: self.satellites,
                IndicatorLunar.SETTINGS_SATELLITES_ADD_NEW: self.satellitesAddNew,
                IndicatorLunar.SETTINGS_SATELLITES_SORT_BY_DATE_TIME: self.satellitesSortByDateTime,
                IndicatorLunar.SETTINGS_SHOW_ORBITAL_ELEMENTS_AS_SUBMENU: self.showOrbitalElementsAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_PLANETS_AS_SUBMENU: self.showPlanetsAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_SATELLITE_NOTIFICATION: self.showSatelliteNotification,
                IndicatorLunar.SETTINGS_SHOW_SATELLITES_AS_SUBMENU: self.showSatellitesAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_STARS_AS_SUBMENU: self.showStarsAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING: self.showWerewolfWarning,
                IndicatorLunar.SETTINGS_STARS: self.stars,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE: self.werewolfWarningStartIlluminationPercentage,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_MESSAGE: self.werewolfWarningMessage,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_SUMMARY: self.werewolfWarningSummary
            }

            with open( IndicatorLunar.SETTINGS_FILE, "w" ) as f: f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorLunar.SETTINGS_FILE )


if __name__ == "__main__": IndicatorLunar().main()