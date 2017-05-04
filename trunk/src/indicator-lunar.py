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


# Application indicator which displays lunar, solar, planetary, star, comet and satellite information.


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
#  http://www.flaticon.com/search/satellite


INDICATOR_NAME = "indicator-lunar"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "Notify", "0.7" )

#TODO Clean up.
from gi.repository import AppIndicator3, GLib, GObject, Gtk, Notify
from threading import Thread
from urllib.request import urlopen
import calendar, copy, datetime, eclipse, glob, json, locale, logging, math, os, pickle, pythonutils, re, satellite, shutil, sys, tempfile, threading, time, webbrowser

try:
    import ephem
    from ephem.cities import _city_data
    from ephem.stars import stars
except:
    pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "You must also install python3-ephem!" ), INDICATOR_NAME )
    sys.exit()


class AstronomicalBodyType: Comet, Moon, Planet, PlanetaryMoon, Satellite, Star, Sun = range( 7 )


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.73"
    ICON = INDICATOR_NAME
    ICON_BASE_NAME = "." + INDICATOR_NAME + "-illumination-icon-"
    ICON_BASE_PATH = tempfile.gettempdir()
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    CACHE_PATH = os.getenv( "HOME" ) + "/.cache/" + INDICATOR_NAME + "/"
    SVG_FULL_MOON_FILE = ICON_BASE_PATH + "/." + INDICATOR_NAME + "-fullmoon-icon" + ".svg"
    SVG_SATELLITE_ICON = INDICATOR_NAME + "-satellite"
    URL_TIMEOUT_IN_SECONDS = 2

    ABOUT_COMMENTS = _( "Displays lunar, solar, planetary, comet, star and satellite information." )
    ABOUT_CREDIT_BRIGHT_LIMB = _( "Bright Limb from 'Astronomical Algorithms' by Jean Meeus." )
    ABOUT_CREDIT_ECLIPSE = _( "Eclipse information by Fred Espenak and Jean Meeus. http://eclipse.gsfc.nasa.gov" )
    ABOUT_CREDIT_PYEPHEM = _( "Calculations courtesy of PyEphem/XEphem. http://rhodesmill.org/pyephem" )
    ABOUT_CREDIT_COMET = _( "Comet OE data by Minor Planet Center. http://www.minorplanetcenter.net" )
    ABOUT_CREDIT_SATELLITE = _( "Satellite TLE data by Dr T S Kelso. http://www.celestrak.com" )
    ABOUT_CREDIT_TROPICAL_SIGN = _( "Tropical Sign by Ignius Drake." )
    ABOUT_CREDITS = [ ABOUT_CREDIT_PYEPHEM, ABOUT_CREDIT_ECLIPSE, ABOUT_CREDIT_TROPICAL_SIGN, ABOUT_CREDIT_BRIGHT_LIMB, ABOUT_CREDIT_SATELLITE, ABOUT_CREDIT_COMET ]

    DATE_TIME_FORMAT_HHcolonMMcolonSS = "%H:%M:%S"
    DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSSdotFLOAT = "%Y-%m-%d %H:%M:%S.%f"

    DISPLAY_NEEDS_REFRESH = _( "(needs refresh)" )
    INDENT = "    "

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"

    SETTINGS_CITY_ELEVATION = "cityElevation"
    SETTINGS_CITY_LATITUDE = "cityLatitude"
    SETTINGS_CITY_LONGITUDE = "cityLongitude"
    SETTINGS_CITY_NAME = "cityName"
    SETTINGS_COMET_OE_URL = "cometOEURL"
    SETTINGS_COMETS = "comets"
    SETTINGS_COMETS_ADD_NEW = "cometsAddNew"
    SETTINGS_COMETS_MAGNITUDE = "cometsMagnitude"
    SETTINGS_HIDE_BODY_IF_NEVER_UP = "hideBodyIfNeverUp"
    SETTINGS_INDICATOR_TEXT = "indicatorText"
    SETTINGS_GROUP_STARS_BY_CONSTELLATION = "groupStarsByConstellation"
    SETTINGS_HIDE_SATELLITE_IF_NO_VISIBLE_PASS = "hideSatelliteIfNoVisiblePass"
    SETTINGS_PLANETS = "planets"
    SETTINGS_SATELLITE_NOTIFICATION_MESSAGE = "satelliteNotificationMessage"
    SETTINGS_SATELLITE_NOTIFICATION_SUMMARY = "satelliteNotificationSummary"
    SETTINGS_SATELLITE_TLE_URL = "satelliteTLEURL"
    SETTINGS_SATELLITES = "satellites"
    SETTINGS_SATELLITES_ADD_NEW = "satellitesAddNew"
    SETTINGS_SATELLITES_SORT_BY_DATE_TIME = "satellitesSortByDateTime"
    SETTINGS_SHOW_COMETS_AS_SUBMENU = "showCometsAsSubmenu"
    SETTINGS_SHOW_MOON = "showMoon"
    SETTINGS_SHOW_PLANETS_AS_SUBMENU = "showPlanetsAsSubmenu"
    SETTINGS_SHOW_SATELLITE_NOTIFICATION = "showSatelliteNotification"
    SETTINGS_SHOW_SATELLITES_AS_SUBMENU = "showSatellitesAsSubmenu"
    SETTINGS_SHOW_STARS_AS_SUBMENU = "showStarsAsSubmenu"
    SETTINGS_SHOW_SUN = "showSun"
    SETTINGS_SHOW_WEREWOLF_WARNING = "showWerewolfWarning"
    SETTINGS_STARS = "stars"
    SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE = "werewolfWarningStartIlluminationPercentage"
    SETTINGS_WEREWOLF_WARNING_MESSAGE = "werewolfWarningMessage"
    SETTINGS_WEREWOLF_WARNING_SUMMARY = "werewolfWarningSummary"

    TRUE_TEXT = "True"
    FALSE_TEXT = "False"

    TRUE_TEXT_TRANSLATION = _( "True" )
    FALSE_TEXT_TRANSLATION = _( "False" )

    DATA_ALTITUDE = "ALTITUDE"
    DATA_AZIMUTH = "AZIMUTH"
    DATA_BRIGHT_LIMB = "BRIGHT LIMB"
    DATA_CONSTELLATION = "CONSTELLATION"
    DATA_DAWN = "DAWN"
    DATA_DECLINATION = "DECLINATION"
    DATA_DISTANCE_TO_EARTH = "DISTANCE TO EARTH"
    DATA_DISTANCE_TO_EARTH_KM = "DISTANCE TO EARTH KM"
    DATA_DISTANCE_TO_SUN = "DISTANCE TO SUN"
    DATA_DUSK = "DUSK"
    DATA_EARTH_TILT = "EARTH TILT"
    DATA_EARTH_VISIBLE = "EARTH VISIBLE"
    DATA_ECLIPSE_DATE_TIME = "ECLIPSE DATE TIME"
    DATA_ECLIPSE_LATITUDE = "ECLIPSE LATITUDE"
    DATA_ECLIPSE_LONGITUDE = "ECLIPSE LONGITUDE"
    DATA_ECLIPSE_TYPE = "ECLIPSE TYPE"
    DATA_ELEVATION = "ELEVATION" # Only used for the CITY "body" tag.
    DATA_EQUINOX = "EQUINOX"
    DATA_FIRST_QUARTER = "FIRST QUARTER"
    DATA_FULL = "FULL"
    DATA_ILLUMINATION = "ILLUMINATION"
    DATA_LATITUDE = "LATITUDE" # Only used for the CITY "body" tag.
    DATA_LONGITUDE = "LONGITUDE" # Only used for the CITY "body" tag.
    DATA_MAGNITUDE = "MAGNITUDE"
    DATA_MESSAGE = "MESSAGE"
    DATA_NAME = "NAME" # Only used for the CITY "body" tag.
    DATA_NEW = "NEW"
    DATA_PHASE = "PHASE"
    DATA_RIGHT_ASCENSION = "RIGHT ASCENSION"
    DATA_RISE_AZIMUTH = "RISE AZIMUTH"
    DATA_RISE_TIME = "RISE TIME"
    DATA_SET_AZIMUTH = "SET AZIMUTH"
    DATA_SET_TIME = "SET TIME"
    DATA_SOLSTICE = "SOLSTICE"
    DATA_SUN_TILT = "SUN TILT"
    DATA_THIRD_QUARTER = "THIRD QUARTER"
    DATA_TROPICAL_SIGN_NAME = "TROPICAL SIGN NAME"
    DATA_TROPICAL_SIGN_DEGREE = "TROPICAL SIGN DEGREE"
    DATA_TROPICAL_SIGN_MINUTE = "TROPICAL SIGN MINUTE"
    DATA_VISIBLE = "VISIBLE"
    DATA_X_OFFSET = "X OFFSET"
    DATA_Y_OFFSET = "Y OFFSET"
    DATA_Z_OFFSET = "Z OFFSET"

    DATA_TAGS_ALL = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_BRIGHT_LIMB,
        DATA_CONSTELLATION,
        DATA_DAWN,
        DATA_DECLINATION,
        DATA_DISTANCE_TO_EARTH,
        DATA_DISTANCE_TO_EARTH_KM,
        DATA_DISTANCE_TO_SUN,
        DATA_DUSK,
        DATA_EARTH_TILT,
        DATA_EARTH_VISIBLE,
        DATA_ECLIPSE_DATE_TIME,
        DATA_ECLIPSE_LATITUDE,
        DATA_ECLIPSE_LONGITUDE,
        DATA_ECLIPSE_TYPE,
        DATA_ELEVATION,
        DATA_EQUINOX,
        DATA_FIRST_QUARTER,
        DATA_FULL,
        DATA_ILLUMINATION,
        DATA_LATITUDE,
        DATA_LONGITUDE,
        DATA_MAGNITUDE,
        DATA_MESSAGE,
        DATA_NAME,
        DATA_NEW,
        DATA_PHASE,
        DATA_RIGHT_ASCENSION,
        DATA_RISE_AZIMUTH,
        DATA_RISE_TIME,
        DATA_SET_AZIMUTH,
        DATA_SET_TIME,
        DATA_SOLSTICE,
        DATA_SUN_TILT,
        DATA_THIRD_QUARTER,
        DATA_TROPICAL_SIGN_NAME,
        DATA_TROPICAL_SIGN_DEGREE,
        DATA_TROPICAL_SIGN_MINUTE,
        DATA_VISIBLE,
        DATA_X_OFFSET,
        DATA_Y_OFFSET,
        DATA_Z_OFFSET ]
    
    DATA_TAGS_MOON = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_CONSTELLATION,
        DATA_DECLINATION,
        DATA_ECLIPSE_DATE_TIME,
        DATA_ECLIPSE_LATITUDE,
        DATA_ECLIPSE_LONGITUDE,
        DATA_ECLIPSE_TYPE,
        DATA_MAGNITUDE,
        DATA_MESSAGE,
        DATA_RIGHT_ASCENSION,
        DATA_RISE_TIME,
        DATA_SET_TIME,
        DATA_TROPICAL_SIGN_NAME,
        DATA_TROPICAL_SIGN_DEGREE,
        DATA_TROPICAL_SIGN_MINUTE ]

    DATA_TAGS_COMET = [
        DATA_RISE_AZIMUTH,
        DATA_RISE_TIME,
        DATA_SET_AZIMUTH,
        DATA_SET_TIME ]

    DATA_TAGS_PLANET = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_BRIGHT_LIMB,
        DATA_CONSTELLATION,
        DATA_DECLINATION,
        DATA_DISTANCE_TO_EARTH,
        DATA_DISTANCE_TO_SUN,
        DATA_ILLUMINATION,
        DATA_MAGNITUDE,
        DATA_MESSAGE,
        DATA_RIGHT_ASCENSION,
        DATA_RISE_TIME,
        DATA_SET_TIME,
        DATA_TROPICAL_SIGN_NAME,
        DATA_TROPICAL_SIGN_DEGREE,
        DATA_TROPICAL_SIGN_MINUTE ]

    DATA_TAGS_PLANETARY_MOON = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_DECLINATION,
        DATA_EARTH_VISIBLE,
        DATA_RIGHT_ASCENSION,
        DATA_X_OFFSET,
        DATA_Y_OFFSET,
        DATA_Z_OFFSET ]

    DATA_TAGS_SATELLITE = [
        DATA_RISE_AZIMUTH,
        DATA_RISE_TIME,
        DATA_SET_AZIMUTH,
        DATA_SET_TIME,
        DATA_VISIBLE ]

    DATA_TAGS_STAR = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_CONSTELLATION,
        DATA_DECLINATION,
        DATA_MAGNITUDE,
        DATA_MESSAGE,
        DATA_RIGHT_ASCENSION,
        DATA_RISE_TIME,
        DATA_SET_TIME,
        DATA_TROPICAL_SIGN_NAME,
        DATA_TROPICAL_SIGN_DEGREE,
        DATA_TROPICAL_SIGN_MINUTE ]

    DATA_TAGS_SUN = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_CONSTELLATION,
        DATA_DAWN,
        DATA_DECLINATION,
        DATA_DUSK,
        DATA_ECLIPSE_DATE_TIME,
        DATA_ECLIPSE_LATITUDE,
        DATA_ECLIPSE_LONGITUDE,
        DATA_ECLIPSE_TYPE,
        DATA_EQUINOX,
        DATA_MAGNITUDE,
        DATA_MESSAGE,
        DATA_RIGHT_ASCENSION,
        DATA_RISE_TIME,
        DATA_SET_TIME,
        DATA_SOLSTICE,
        DATA_TROPICAL_SIGN_NAME,
        DATA_TROPICAL_SIGN_DEGREE,
        DATA_TROPICAL_SIGN_MINUTE ]

    DATA_TAGS_TRANSLATIONS = {
        DATA_ALTITUDE                   : _( "ALTITUDE" ),
        DATA_AZIMUTH                    : _( "AZIMUTH" ),
        DATA_BRIGHT_LIMB                : _( "BRIGHT LIMB" ),
        DATA_CONSTELLATION              : _( "CONSTELLATION" ),
        DATA_DAWN                       : _( "DAWN" ),
        DATA_DECLINATION                : _( "DECLINATION" ),
        DATA_DISTANCE_TO_EARTH          : _( "DISTANCE TO EARTH" ),
        DATA_DISTANCE_TO_EARTH_KM       : _( "DISTANCE TO EARTH KM" ),
        DATA_DISTANCE_TO_SUN            : _( "DISTANCE TO SUN" ),
        DATA_DUSK                       : _( "DUSK" ),
        DATA_EARTH_TILT                 : _( "EARTH TILT" ),
        DATA_EARTH_VISIBLE              : _( "EARTH VISIBLE" ),
        DATA_ECLIPSE_DATE_TIME          : _( "ECLIPSE DATE TIME" ),
        DATA_ECLIPSE_LATITUDE           : _( "ECLIPSE LATITUDE" ),
        DATA_ECLIPSE_LONGITUDE          : _( "ECLIPSE LONGITUDE" ),
        DATA_ECLIPSE_TYPE               : _( "ECLIPSE TYPE" ),
        DATA_ELEVATION                  : _( "ELEVATION" ),
        DATA_EQUINOX                    : _( "EQUINOX" ),
        DATA_FIRST_QUARTER              : _( "FIRST QUARTER" ),
        DATA_FULL                       : _( "FULL" ),
        DATA_ILLUMINATION               : _( "ILLUMINATION" ),
        DATA_LATITUDE                   : _( "LATITUDE" ),
        DATA_LONGITUDE                  : _( "LONGITUDE" ),
        DATA_MAGNITUDE                  : _( "MAGNITUDE" ),
        DATA_MESSAGE                    : _( "MESSAGE" ),
        DATA_NAME                       : _( "NAME" ), # Only used for CITY "body" tag.
        DATA_NEW                        : _( "NEW" ),
        DATA_PHASE                      : _( "PHASE" ),
        DATA_RIGHT_ASCENSION            : _( "RIGHT ASCENSION" ),
        DATA_RISE_AZIMUTH               : _( "RISE AZIMUTH" ),
        DATA_RISE_TIME                  : _( "RISE TIME" ),
        DATA_SET_AZIMUTH                : _( "SET AZIMUTH" ),
        DATA_SET_TIME                   : _( "SET TIME" ),
        DATA_SOLSTICE                   : _( "SOLSTICE" ),
        DATA_SUN_TILT                   : _( "SUN TILT" ),
        DATA_THIRD_QUARTER              : _( "THIRD QUARTER" ),
        DATA_TROPICAL_SIGN_NAME         : _( "TROPICAL SIGN NAME" ),
        DATA_TROPICAL_SIGN_DEGREE       : _( "TROPICAL SIGN DEGREE" ),
        DATA_TROPICAL_SIGN_MINUTE       : _( "TROPICAL SIGN MINUTE" ),
        DATA_VISIBLE                    : _( "VISIBLE" ),
        DATA_X_OFFSET                   : _( "X OFFSET" ),
        DATA_Y_OFFSET                   : _( "Y OFFSET" ),
        DATA_Z_OFFSET                   : _( "Z OFFSET" ) }

    # Translated constellations.
    # Sourced from cns_namemap in ephem/libastro/constel.c
    CONSTELLATIONS_TRANSLATIONS = {
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

    CITY_TAG = "CITY"
    CITY_TAG_TRANSLATION = { CITY_TAG : _( "CITY" ) }

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

    PLANET_AND_MOON_NAMES_TRANSLATIONS = {
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

    PLANET_AND_MOON_TAGS_TRANSLATIONS = {
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
    STAR_NAMES_TRANSLATIONS = {
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
    STAR_TAGS_TRANSLATIONS = {
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

    BODY_TAGS_TRANSLATIONS = dict(
        list( CITY_TAG_TRANSLATION.items() ) + 
        list( MOON_TAG_TRANSLATION.items() ) + 
        list( PLANET_AND_MOON_TAGS_TRANSLATIONS.items() ) + 
        list( STAR_TAGS_TRANSLATIONS.items() ) + 
        list( SUN_TAG_TRANSLATION.items() ) )

    STARS_BY_CONSTELLATION = {
        "Andromeda":        [ "Almach", "Mirach", "Sirrah" ],
        "Aries":            [ "Hamal" ],
        "Aquarius":         [ "Sadalmelik" ],
        "Aquila":           [ "Alshain", "Altair", "Tarazed" ],
        "Auriga":           [ "Menkalinan", "Elnath", "Capella" ],
        "Bootes":           [ "Arcturus", "Izar" ],
        "Canis Major":      [ "Adara", "Sirius", "Mirzam", "Wezen" ],
        "Canis Minor":      [ "Procyon" ],
        "Carina":           [ "Canopus" ],
        "Cassiopeia":       [ "Schedar", "Caph" ],
        "Centaurus":        [ "Agena" ],
        "Cepheus":          [ "Alderamin", "Alfirk" ],
        "Cetus":            [ "Menkar" ],
        "Corona Borealis":  [ "Alphecca" ],
        "Corvus":           [ "Gienah Corvi", "Minkar" ],
        "Crux":             [ "Mimosa" ],
        "Cygnus":           [ "Sadr", "Albereo", "Deneb" ],
        "Draco":            [ "Etamin", "Thuban" ],
        "Eridanus":         [ "Achernar", "Zaurak" ],
        "Gemini":           [ "Castor", "Alhena", "Pollux" ],
        "Grus":             [ "Alnair" ],
        "Hercules":         [ "Rasalgethi" ],
        "Hydra":            [ "Alphard" ],
        "Leo":              [ "Algieba", "Denebola", "Regulus" ],
        "Lepus":            [  "Nihal", "Arneb" ],
        "Lyra":             [ "Sheliak", "Sulafat", "Vega" ],
        "Ophiuchus":        [ "Rasalhague", "Cebalrai" ],
        "Orion":            [ "Alnilam", "Mintaka", "Saiph", "Alnitak", "Betelgeuse", "Bellatrix", "Rigel" ],
        "Pavo":             [ "Peacock" ],
        "Pegasus":          [ "Scheat", "Algenib", "Enif", "Markab" ],
        "Perseus":          [ "Algol" ],
        "Piscis Austrinus": [ "Fomalhaut" ],
        "Puppis":           [ "Naos" ],
        "Sagittarius":      [ "Arkab Prior", "Arkab Posterior", "Rukbat", "Nunki", "Kaus Australis" ],
        "Scorpius":         [ "Antares", "Shaula" ],
        "Serpens Caput":    [ "Unukalhai" ],
        "Taurus":           [ "Taygeta", "Alcyone", "Atlas", "Aldebaran", "Merope", "Electra", "Maia" ],
        "Ursa Major":       [ "Phecda", "Alioth", "Dubhe", "Megrez", "Alcaid", "Alcor", "Mizar", "Merak" ],
        "Ursa Minor":       [ "Polaris", "Kochab" ],
        "Virgo":            [ "Vindemiatrix", "Spica" ] }


    LUNAR_PHASE_FULL_MOON = "FULL_MOON"
    LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
    LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
    LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
    LUNAR_PHASE_NEW_MOON = "NEW_MOON"
    LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
    LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
    LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"

    LUNAR_PHASE_NAMES_TRANSLATIONS = {
        LUNAR_PHASE_FULL_MOON       : _( "Full Moon" ),
        LUNAR_PHASE_WANING_GIBBOUS  : _( "Waning Gibbous" ),
        LUNAR_PHASE_THIRD_QUARTER   : _( "Third Quarter" ),
        LUNAR_PHASE_WANING_CRESCENT : _( "Waning Crescent" ),
        LUNAR_PHASE_NEW_MOON        : _( "New Moon" ),
        LUNAR_PHASE_WAXING_CRESCENT : _( "Waxing Crescent" ),
        LUNAR_PHASE_FIRST_QUARTER   : _( "First Quarter" ),
        LUNAR_PHASE_WAXING_GIBBOUS  : _( "Waxing Gibbous" )
    }

    COMET_OE_CACHE_BASENAME = "comet-oe-"
    COMET_OE_CACHE_MAXIMUM_AGE_HOURS = 30
    COMET_OE_URL = "http://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt"
    COMET_OE_DOWNLOAD_PERIOD_HOURS = 30

    COMET_ON_CLICK_URL = "http://www.minorplanetcenter.net/db_search/show_object?utf8=%E2%9C%93&object_id="

    SATELLITE_TAG_NAME = "[NAME]"
    SATELLITE_TAG_NUMBER = "[NUMBER]"
    SATELLITE_TAG_INTERNATIONAL_DESIGNATOR = "[INTERNATIONAL DESIGNATOR]"
    SATELLITE_TAG_RISE_AZIMUTH = "[RISE AZIMUTH]"
    SATELLITE_TAG_RISE_TIME = "[RISE TIME]"
    SATELLITE_TAG_SET_AZIMUTH = "[SET AZIMUTH]"
    SATELLITE_TAG_SET_TIME = "[SET TIME]"
    SATELLITE_TAG_VISIBLE = "[VISIBLE]"

    SATELLITE_TAG_NAME_TRANSLATION = "[" + _( "NAME" ) + "]"
    SATELLITE_TAG_NUMBER_TRANSLATION = "[" + _( "NUMBER" ) + "]"
    SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION = "[" + _( "INTERNATIONAL DESIGNATOR" ) + "]"
    SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION = "[" + _( "RISE AZIMUTH" ) + "]"
    SATELLITE_TAG_RISE_TIME_TRANSLATION = "[" + _( "RISE TIME" ) + "]"
    SATELLITE_TAG_SET_AZIMUTH_TRANSLATION = "[" + _( "SET AZIMUTH" ) + "]"
    SATELLITE_TAG_SET_TIME_TRANSLATION = "[" + _( "SET TIME" ) + "]"
    SATELLITE_TAG_VISIBLE_TRANSLATION = "[" + _( "VISIBLE" ) + "]"

    SATELLITE_TAG_TRANSLATIONS = Gtk.ListStore( str, str ) # Tag, translated tag.
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_NAME.strip( "[]" ), SATELLITE_TAG_NAME_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_NUMBER.strip( "[]" ), SATELLITE_TAG_NUMBER_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_INTERNATIONAL_DESIGNATOR.strip( "[]" ), SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_RISE_AZIMUTH.strip( "[]" ), SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_RISE_TIME.strip( "[]" ), SATELLITE_TAG_RISE_TIME_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_SET_AZIMUTH.strip( "[]" ), SATELLITE_TAG_SET_AZIMUTH_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_SET_TIME.strip( "[]" ), SATELLITE_TAG_SET_TIME_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_VISIBLE.strip( "[]" ), SATELLITE_TAG_VISIBLE_TRANSLATION.strip( "[]" ) ] )

    SATELLITE_TLE_CACHE_BASENAME = "satellite-tle-"
    SATELLITE_TLE_CACHE_MAXIMUM_AGE_HOURS = 18
    SATELLITE_TLE_DOWNLOAD_PERIOD_HOURS = 18
    SATELLITE_TLE_URL = "http://celestrak.com/NORAD/elements/visual.txt"

    SATELLITE_ON_CLICK_URL = "http://www.n2yo.com/satellite/?s=" + SATELLITE_TAG_NUMBER
    SATELLITE_MENU_TEXT = SATELLITE_TAG_NAME + " : " + SATELLITE_TAG_NUMBER + " : " + SATELLITE_TAG_INTERNATIONAL_DESIGNATOR
    SATELLITE_NOTIFICATION_SUMMARY_DEFAULT = SATELLITE_TAG_NAME + _( " now rising..." )
    SATELLITE_NOTIFICATION_MESSAGE_DEFAULT = \
        _( "Number: " ) + SATELLITE_TAG_NUMBER_TRANSLATION + "\n" + \
        _( "International Designator: " ) + SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n" + \
        _( "Rise Time: " ) + SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n" + \
        _( "Rise Azimuth: " ) + SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n" + \
        _( "Set Time: " ) + SATELLITE_TAG_SET_TIME_TRANSLATION + "\n" + \
        _( "Set Azimuth: " ) + SATELLITE_TAG_SET_AZIMUTH_TRANSLATION

    TROPICAL_SIGNS = [ "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces" ]
    TROPICAL_SIGN_TRANSLATIONS = {
        "Aries"         : _( "Aries" ),
        "Taurus"        : _( "Taurus" ),
        "Gemini"        : _( "Gemini" ),
        "Cancer"        : _( "Cancer" ),
        "Leo"           : _( "Leo" ),
        "Virgo"         : _( "Virgo" ),
        "Libra"         : _( "Libra" ),
        "Scorpio"       : _( "Scorpio" ),
        "Sagittarius"   : _( "Sagittarius" ),
        "Capricorn"     : _( "Capricorn" ),
        "Aquarius"      : _( "Aquarius" ),
        "Pisces"        : _( "Pisces" ) }

    WEREWOLF_WARNING_MESSAGE_DEFAULT = _( "                                          ...werewolves about ! ! !" )
    WEREWOLF_WARNING_SUMMARY_DEFAULT = _( "W  A  R  N  I  N  G" )

    INDICATOR_TEXT_DEFAULT = "[" + MOON_TAG + " " + DATA_PHASE + "]"

    MESSAGE_BODY_ALWAYS_UP = _( "Always Up!" )
    MESSAGE_BODY_NEVER_UP = _( "Never Up!" )
    MESSAGE_DATA_BAD_DATA = _( "Bad data!" )
    MESSAGE_DATA_CANNOT_ACCESS_DATA_SOURCE = _( "Cannot access the data source\n<a href=\'{0}'>{0}</a>" )
    MESSAGE_DATA_NO_DATA = _( "No data!" )
    MESSAGE_DATA_NO_DATA_FOUND_AT_SOURCE = _( "No data found at\n<a href=\'{0}'>{0}</a>" )
    MESSAGE_SATELLITE_IS_CIRCUMPOLAR = _( "Satellite is circumpolar." )
    MESSAGE_SATELLITE_NEVER_RISES = _( "Satellite never rises." )
    MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME = _( "No passes within the next two days." )
    MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS = _( "Unable to compute next pass!" )
    MESSAGE_SATELLITE_VALUE_ERROR = _( "ValueError" )

    # Used to tell the function which gets and formats data to format in a different manner for a different source.
    SOURCE_SATELLITE_NOTIFICATION = 0


    def __init__( self ):
        self.data = { } # Key is a tuple of AstronomicalBodyType, a data tag (upper case( and data tag (upper case).  Value is the data ready for display.
        self.cometOEData = { } # Key is the comet name, upper cased; value is the comet data string.  Can be empty but never None.
        self.satelliteNotifications = { }
        self.satelliteTLEData = { } # Key: ( satellite name upper cased, satellite number ) ; Value: satellite.TLE object.  Can be empty but never None.

        self.toggleCometsTable = True
        self.togglePlanetsTable = True
        self.toggleSatellitesTable = True
        self.toggleStarsTable = True

        self.previousLunarIlluminationPercentage = -1
        self.previousLunarBrightLimbAngle = -1
        self.previousThemeName = ""

        if not os.path.exists( IndicatorLunar.CACHE_PATH ):
            os.makedirs( IndicatorLunar.CACHE_PATH )

        GObject.threads_init()
        self.lock = threading.Lock()

        filehandler = pythonutils.TruncatedFileHandler( IndicatorLunar.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )
        Notify.init( INDICATOR_NAME )

        # Initialise last update date/times to the past...
        self.lastUpdateCometOE = datetime.datetime.utcnow() - datetime.timedelta( hours = 1000 )
        self.lastUpdateSatelliteTLE = datetime.datetime.utcnow() - datetime.timedelta( hours = 1000 )
        self.lastFullMoonNotfication = datetime.datetime.utcnow() - datetime.timedelta( hours = 1000 )

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, "", AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_icon_theme_path( IndicatorLunar.ICON_BASE_PATH )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

        self.loadSettings()
        self.update()


    def main( self ): Gtk.main()


    def update( self ): Thread( target = self.updateBackend ).start()


    def updateBackend( self ):
        if self.lock.acquire( blocking = False ):
            self.updateCometOEData()
            self.updateSatelliteTLEData() 

            self.data.clear() # Must clear the data on each update, otherwise data will accumulate (if a planet/star/satellite was added then removed, the computed data remains).     
            self.data[ ( None, IndicatorLunar.CITY_TAG, IndicatorLunar.DATA_NAME ) ] = self.cityName

            global _city_data
            self.data[ ( None, IndicatorLunar.CITY_TAG, IndicatorLunar.DATA_LATITUDE ) ] = str( round( float( _city_data.get( self.cityName )[ 0 ] ), 1 ) )
            self.data[ ( None, IndicatorLunar.CITY_TAG, IndicatorLunar.DATA_LONGITUDE ) ] = str( round( float( _city_data.get( self.cityName )[ 1 ] ), 1 ) )
            self.data[ ( None, IndicatorLunar.CITY_TAG, IndicatorLunar.DATA_ELEVATION ) ] = str( _city_data.get( self.cityName )[ 2 ] )

            ephemNow = ephem.now() # UTC, used in all calculations.  When it comes time to display, conversion to local time takes place.
            self.updateAstronomicalInformation( ephemNow, self.hideBodyIfNeverUp, self.cometsMagnitude, self.hideSatelliteIfNoVisiblePass )
            GLib.idle_add( self.updateFrontend, ephemNow )


    def updateFrontend( self, ephemNow ):
        self.nextUpdate = str( datetime.datetime.utcnow() + datetime.timedelta( hours = 1000 ) ) # Set a bogus date/time in the future.
        self.updateMenu()
        self.updateIconAndLabel( ephemNow )

        if self.showWerewolfWarning:
            self.notificationFullMoon( ephemNow )

        if self.showSatelliteNotification:
            self.notificationSatellite()

        self.nextUpdate = self.toDateTime( self.nextUpdate ) # Parse from string back into a datetime.
        nextUpdateInSeconds = int( ( self.nextUpdate - datetime.datetime.utcnow() ).total_seconds() )

        # Ensure the update period is positive, at most every minute and at least every hour.
        if nextUpdateInSeconds < 60:
            nextUpdateInSeconds = 60
        elif nextUpdateInSeconds > ( 60 * 60 ):
            nextUpdateInSeconds = ( 60 * 60 )

        self.eventSourceID = GLib.timeout_add_seconds( nextUpdateInSeconds, self.update )
        self.lock.release()


    def updateMenu( self ):
        menu = Gtk.Menu()
        self.updateMoonMenu( menu )
        self.updateSunMenu( menu )
        self.updatePlanetsMenu( menu )
        self.updateStarsMenu( menu )
        self.updateCometsMenu( menu )
        self.updateSatellitesMenu( menu )
        pythonutils.createPreferencesAboutQuitMenuItems( menu, len( menu.get_children() ) > 0, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()
        self.menu = menu


    def getDisplayData( self, key, source = None ):
        displayData = None
        if key[ 2 ] == IndicatorLunar.DATA_ALTITUDE or \
           key[ 2 ] == IndicatorLunar.DATA_AZIMUTH or \
           key[ 2 ] == IndicatorLunar.DATA_RISE_AZIMUTH or \
           key[ 2 ] == IndicatorLunar.DATA_SET_AZIMUTH:
            if source is None:
                displayData = str( self.getDecimalDegrees( self.data[ key ], False, 0 ) ) + "° (" + self.trimDecimal( self.data[ key ] ) + ")"
            elif source == IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION:
                displayData = str( self.getDecimalDegrees( self.data[ key ], False, 0 ) ) + "°"

        elif key[ 2 ] == IndicatorLunar.DATA_BRIGHT_LIMB or \
             key[ 2 ] == IndicatorLunar.DATA_EARTH_TILT or \
             key[ 2 ] == IndicatorLunar.DATA_SUN_TILT or \
             key[ 2 ] == IndicatorLunar.DATA_TROPICAL_SIGN_DEGREE:
            displayData = self.data[ key ] + "°"

        elif key[ 2 ] == IndicatorLunar.DATA_CONSTELLATION:
            displayData = IndicatorLunar.CONSTELLATIONS_TRANSLATIONS[ self.data[ key ] ]

        elif key[ 2 ] == IndicatorLunar.DATA_DAWN or \
             key[ 2 ] == IndicatorLunar.DATA_DUSK or \
             key[ 2 ] == IndicatorLunar.DATA_ECLIPSE_DATE_TIME or \
             key[ 2 ] == IndicatorLunar.DATA_EQUINOX or \
             key[ 2 ] == IndicatorLunar.DATA_FIRST_QUARTER or \
             key[ 2 ] == IndicatorLunar.DATA_FULL or \
             key[ 2 ] == IndicatorLunar.DATA_NEW or \
             key[ 2 ] == IndicatorLunar.DATA_RISE_TIME or \
             key[ 2 ] == IndicatorLunar.DATA_SET_TIME or \
             key[ 2 ] == IndicatorLunar.DATA_SOLSTICE or \
             key[ 2 ] == IndicatorLunar.DATA_THIRD_QUARTER:
                if source is None:
                    displayData = self.getLocalDateTime( self.data[ key ] )
                elif source == IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION:
                    displayData = self.getLocalDateTime( self.data[ key ], IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS )

        elif key[ 2 ] == IndicatorLunar.DATA_DECLINATION:
            dec = self.data[ key ]
            if self.getDecimalDegrees( self.data[ key ], False, 0 ) < 0.0:
                dec = dec [ 1 : ]
                direction = _( "S" )
            else:
                direction = _( "N" )

            displayData = str( self.getDecimalDegrees( dec, False, 0 ) ) + "° " + direction + " (" + self.trimDecimal( self.data[ key ] ) + ")"

        elif key[ 2 ] == IndicatorLunar.DATA_DISTANCE_TO_EARTH or \
             key[ 2 ] == IndicatorLunar.DATA_DISTANCE_TO_SUN:
            displayData = self.data[ key ] + " " + _( "ua" )

        elif key[ 2 ] == IndicatorLunar.DATA_DISTANCE_TO_EARTH_KM:
            displayData = str( locale.format( "%d", int( self.data[ key ] ), grouping = True ) ) + " " + _( "km" )

        elif key[ 2 ] == IndicatorLunar.DATA_EARTH_VISIBLE or \
             key[ 2 ] == IndicatorLunar.DATA_VISIBLE:
            if self.data[ key ] == IndicatorLunar.TRUE_TEXT:
                displayData = IndicatorLunar.TRUE_TEXT_TRANSLATION
            else:
                displayData = IndicatorLunar.FALSE_TEXT_TRANSLATION

        elif key[ 2 ] == IndicatorLunar.DATA_ECLIPSE_LATITUDE:
            latitude = self.data[ key ]
            if latitude[ 0 ] == "-":
                displayData = latitude[ 1 : ] + "° " + _( "S" )
            else:
                displayData = latitude + "° " +_( "N" )

        elif key[ 2 ] == IndicatorLunar.DATA_ECLIPSE_LONGITUDE:
            longitude = self.data[ key ]
            if longitude[ 0 ] == "-":
                displayData = longitude[ 1 : ] + "° " + _( "E" )
            else:
                displayData = longitude + "° " +_( "W" )

        elif key[ 2 ] == IndicatorLunar.DATA_ECLIPSE_TYPE:
            if self.data[ key ] == eclipse.ECLIPSE_TYPE_ANNULAR:
                displayData = _( "Annular" )
            elif self.data[ key ] == eclipse.ECLIPSE_TYPE_HYBRID:
                displayData = _( "Hybrid (Annular/Total)" )
            elif self.data[ key ] == eclipse.ECLIPSE_TYPE_PARTIAL:
                displayData = _( "Partial" )
            elif self.data[ key ] == eclipse.ECLIPSE_TYPE_PENUMBRAL:
                displayData = _( "Penumbral" )
            else: # Assume eclipse.ECLIPSE_TYPE_TOTAL:
                displayData = _( "Total" )

        elif key[ 2 ] == IndicatorLunar.DATA_ELEVATION:
            displayData = self.data[ key ] + " " + _( "m" )

        elif key[ 2 ] == IndicatorLunar.DATA_ILLUMINATION:
            displayData = self.data[ key ] + "%"

        elif key[ 2 ] == IndicatorLunar.DATA_LATITUDE or \
             key[ 2 ] == IndicatorLunar.DATA_LONGITUDE:
            displayData = self.data[ key ] + "°"

        elif key[ 2 ] == IndicatorLunar.DATA_MAGNITUDE:
            displayData = self.data[ key ]

        elif key[ 2 ] == IndicatorLunar.DATA_MESSAGE:
            displayData = self.data[ key ]

        elif key[ 2 ] == IndicatorLunar.DATA_PHASE:
            displayData = IndicatorLunar.LUNAR_PHASE_NAMES_TRANSLATIONS[ self.data[ key ] ]

        elif key[ 2 ] == IndicatorLunar.DATA_NAME:
            displayData = self.data[ key ]

        elif key[ 2 ] == IndicatorLunar.DATA_RIGHT_ASCENSION:
            displayData = str( self.getDecimalDegrees( self.data[ key ], True, 0 ) ) + "° (" + self.trimDecimal( self.data[ key ] ) + ")" 

        elif key[ 2 ] == IndicatorLunar.DATA_TROPICAL_SIGN_NAME:
            displayData = IndicatorLunar.TROPICAL_SIGN_TRANSLATIONS[ self.data[ key ] ] 

        elif key[ 2 ] == IndicatorLunar.DATA_TROPICAL_SIGN_MINUTE:
            displayData = self.data[ key ] + "'"

        elif key[ 2 ] == IndicatorLunar.DATA_X_OFFSET or \
             key[ 2 ] == IndicatorLunar.DATA_Y_OFFSET or \
             key[ 2 ] == IndicatorLunar.DATA_Z_OFFSET:
            displayData = self.data[ key ]

        if displayData is None:
            logging.error( "Unknown/unhandled key: " + key )

        return displayData # Returning None is not good but better to let it crash and find out about it than hide the problem.


    # Converts a UTC datetime string in the format 2015-05-11 22:51:42.429093 to local datetime string.
    def getLocalDateTime( self, utcDateTimeString, formatString = None ):
        utcDateTime = self.toDateTime( utcDateTimeString )
        timestamp = calendar.timegm( utcDateTime.timetuple() )
        localDateTime = datetime.datetime.fromtimestamp( timestamp )
        localDateTime.replace( microsecond = utcDateTime.microsecond )
        localDateTimeString = str( localDateTime )
        if formatString is not None and formatString == IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS:
            localDateTimeString = localDateTime.strftime( IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS )

        return localDateTimeString


    # Takes a string in the format of HH:MM:SS.S and converts to degrees (°) in decimal. 
    def getDecimalDegrees( self, stringInput, isHours, roundAmount ):
        t = tuple( stringInput.split( ":" ) )
        x = ( float( t[ 2 ] ) / 60.0 + float( t[ 1 ] ) ) / 60.0 + abs( float( t[ 0 ] ) )
        if isHours:
            x = x * 15.0

        y = float( t[ 0 ] )
        if roundAmount == 0:
            decimalDegrees = round( math.copysign( x, y ) )
        else:
            decimalDegrees = round( math.copysign( x, y ), roundAmount )

        return decimalDegrees


    def trimDecimal( self, stringInput ): return re.sub( "\.(\d+)", "", stringInput )


    def updateIconAndLabel( self, ephemNow ):
        # Substitute tags for values.
        parsedOutput = self.indicatorText
        for key in self.data.keys():
            if "[" + key[ 1 ] + " " + key[ 2 ] + "]" in parsedOutput:
                parsedOutput = parsedOutput.replace( "[" + key[ 1 ] + " " + key[ 2 ] + "]", self.getDisplayData( key ) )

        # If the underlying object has been unchecked or the object (satellite/comet) no longer exists,
        # a tag for this object will not be substituded; so remove.
        parsedOutput = re.sub( "\[[^\[^\]]*\]", "", parsedOutput )
        self.indicator.set_label( parsedOutput, "" ) # Second parameter is a label-guide: http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html

        moon = ephem.Moon( self.getCity( ephemNow ) )
        lunarIlluminationPercentage = int( self.getPhase( moon ) )
        lunarBrightLimbAngle = int( round( self.getZenithAngleOfBrightLimb( self.getCity( ephemNow ), moon ) ) )
        themeName = self.getThemeName()
        noChange = \
            lunarBrightLimbAngle == self.previousLunarBrightLimbAngle and \
            lunarIlluminationPercentage == self.previousLunarIlluminationPercentage and \
            themeName == self.previousThemeName

        if not noChange:
            self.previousLunarBrightLimbAngle = lunarBrightLimbAngle
            self.previousLunarIlluminationPercentage = lunarIlluminationPercentage
            self.previousThemeName = themeName
            self.purgeIcons()
            iconName = self.getIconName()
            self.createIcon( lunarIlluminationPercentage, lunarBrightLimbAngle, self.getIconFilename( iconName ) )
            self.indicator.set_icon( iconName )


    def notificationFullMoon( self, ephemNow ):
        lunarIlluminationPercentage = int( self.getPhase( ephem.Moon( self.getCity( ephemNow ) ) ) )
        lunarPhase = self.getLunarPhase( ephemNow, lunarIlluminationPercentage )
        phaseIsBetweenNewAndFullInclusive = \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON )

        if phaseIsBetweenNewAndFullInclusive and \
           lunarIlluminationPercentage >= self.werewolfWarningStartIlluminationPercentage and \
           ( ( self.lastFullMoonNotfication + datetime.timedelta( hours = 1 ) ) < datetime.datetime.utcnow() ):

            summary = self.werewolfWarningSummary
            if self.werewolfWarningSummary == "":
                summary = " " # The notification summary text cannot be empty (at least on Unity).

            self.createIcon( 100, None, IndicatorLunar.SVG_FULL_MOON_FILE )
            Notify.Notification.new( summary, self.werewolfWarningMessage, IndicatorLunar.SVG_FULL_MOON_FILE ).show()
            os.remove( IndicatorLunar.SVG_FULL_MOON_FILE )
            self.lastFullMoonNotfication = datetime.datetime.utcnow()


    def notificationSatellite( self ):
        # Create a list of satellite name/number and rise times to then either sort by name/number or rise time.
        satelliteNameNumberRiseTimes = [ ]
        for satelliteName, satelliteNumber, in self.satellites:
            key = ( AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )
            if ( key + ( IndicatorLunar.DATA_RISE_TIME, ) ) in self.data: # Assume all other information is present!
               satelliteNameNumberRiseTimes.append( [ satelliteName, satelliteNumber, self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] ] )

        if self.satellitesSortByDateTime:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 2 ], x[ 0 ], x[ 1 ] ) )
        else:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 0 ], x[ 1 ], x[ 2 ] ) )

        utcNow = str( datetime.datetime.utcnow() )
        for satelliteName, satelliteNumber, riseTime in satelliteNameNumberRiseTimes:
            key = ( AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )

            if ( satelliteName, satelliteNumber ) in self.satelliteNotifications:
                # There has been a previous notification for this satellite.
                # Ensure that the current rise/set matches that of the previous notification.
                # Due to a quirk of the astro backend, the date/time may not match exactly (be out by a few seconds or more).
                # So need to ensure that the current rise/set and the previous rise/set overlap to be sure it is the same transit.
                currentRise = self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ]
                currentSet = self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ]
                previousRise, previousSet = self.satelliteNotifications[ ( satelliteName, satelliteNumber ) ]
                overlap = ( currentRise < previousSet ) and ( currentSet > previousRise )
                if overlap:
                    continue

            # Ensure the current time is within the rise/set...
            # Subtract a minute from the rise time to force the notification to take place just prior to the satellite rise.
            riseTimeMinusOneMinute = str( self.toDateTime( self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] ) - datetime.timedelta( minutes = 1 ) )
            if utcNow < riseTimeMinusOneMinute or \
               utcNow > self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ]:
                continue

            self.satelliteNotifications[ ( satelliteName, satelliteNumber ) ] = ( self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ], self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] )

            # Parse the satellite summary/message to create the notification...
            riseTime = self.getDisplayData( key + ( IndicatorLunar.DATA_RISE_TIME, ), IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION )
            riseAzimuth = self.getDisplayData( key + ( IndicatorLunar.DATA_RISE_AZIMUTH, ), IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION )
            setTime = self.getDisplayData( key + ( IndicatorLunar.DATA_SET_TIME, ), IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION )
            setAzimuth = self.getDisplayData( key + ( IndicatorLunar.DATA_SET_AZIMUTH, ), IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION )
            tle = self.satelliteTLEData[ ( satelliteName, satelliteNumber ) ]

            summary = self.satelliteNotificationSummary. \
                      replace( IndicatorLunar.SATELLITE_TAG_NAME, tle.getName() ). \
                      replace( IndicatorLunar.SATELLITE_TAG_NUMBER, tle.getNumber() ). \
                      replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, tle.getInternationalDesignator() ). \
                      replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
                      replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME, riseTime ). \
                      replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
                      replace( IndicatorLunar.SATELLITE_TAG_SET_TIME, setTime ). \
                      replace( IndicatorLunar.SATELLITE_TAG_VISIBLE, self.getDisplayData( key + ( IndicatorLunar.DATA_VISIBLE, ) ) )

            if summary == "":
                summary = " " # The notification summary text must not be empty (at least on Unity).

            message = self.satelliteNotificationMessage. \
                      replace( IndicatorLunar.SATELLITE_TAG_NAME, tle.getName() ). \
                      replace( IndicatorLunar.SATELLITE_TAG_NUMBER, tle.getNumber() ). \
                      replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, tle.getInternationalDesignator() ). \
                      replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
                      replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME, riseTime ). \
                      replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
                      replace( IndicatorLunar.SATELLITE_TAG_SET_TIME, setTime ). \
                      replace( IndicatorLunar.SATELLITE_TAG_VISIBLE, self.getDisplayData( key + ( IndicatorLunar.DATA_VISIBLE, ) ) )

            Notify.Notification.new( summary, message, IndicatorLunar.SVG_SATELLITE_ICON ).show()


    def updateMoonMenu( self, menu ):
        if self.showMoon and not self.hideBody( AstronomicalBodyType.Moon, IndicatorLunar.MOON_TAG, self.hideBodyIfNeverUp ):
            key = ( AstronomicalBodyType.Moon, IndicatorLunar.MOON_TAG )
            menuItem = Gtk.MenuItem( _( "Moon" ) )
            menu.append( menuItem )
            self.updateCommonMenu( menuItem, AstronomicalBodyType.Moon, IndicatorLunar.MOON_TAG )
            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
            menuItem.get_submenu().append( Gtk.MenuItem( _( "Phase: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_PHASE, ) ) ) )
            menuItem.get_submenu().append( Gtk.MenuItem( _( "Next Phases" ) ) )

            # Determine which phases occur by date rather than using the phase calculated.
            # The phase (illumination) rounds numbers and so a given phase is entered earlier than what is correct.
            nextPhases = [ ]
            nextPhases.append( [ self.data[ key + ( IndicatorLunar.DATA_FIRST_QUARTER, ) ], _( "First Quarter: " ), key + ( IndicatorLunar.DATA_FIRST_QUARTER, ) ] )
            nextPhases.append( [ self.data[ key + ( IndicatorLunar.DATA_FULL, ) ], _( "Full: " ), key + ( IndicatorLunar.DATA_FULL, ) ] )
            nextPhases.append( [ self.data[ key + ( IndicatorLunar.DATA_THIRD_QUARTER, ) ], _( "Third Quarter: " ), key + ( IndicatorLunar.DATA_THIRD_QUARTER, ) ] )
            nextPhases.append( [ self.data[ key + ( IndicatorLunar.DATA_NEW, ) ], _( "New: " ), key + ( IndicatorLunar.DATA_NEW, ) ] )

            nextPhases = sorted( nextPhases, key = lambda tuple: tuple[ 0 ] )
            for dateTime, displayText, key in nextPhases:
                menuItem.get_submenu().append( Gtk.MenuItem( IndicatorLunar.INDENT + displayText + self.getDisplayData( key ) ) )
                self.nextUpdate = self.getSmallestDateTime( self.nextUpdate, dateTime )

            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
            self.updateEclipseMenu( menuItem.get_submenu(), AstronomicalBodyType.Moon, IndicatorLunar.MOON_TAG )


    def updateSunMenu( self, menu ):
        if self.showSun and not self.hideBody( AstronomicalBodyType.Sun, IndicatorLunar.SUN_TAG, self.hideBodyIfNeverUp ):
            key = ( AstronomicalBodyType.Sun, IndicatorLunar.SUN_TAG )
            menuItem = Gtk.MenuItem( _( "Sun" ) )
            menu.append( menuItem )
            self.updateCommonMenu( menuItem, AstronomicalBodyType.Sun, IndicatorLunar.SUN_TAG )
            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )

            # Solstice/Equinox.
            equinox = self.data[ key + ( IndicatorLunar.DATA_EQUINOX, ) ]
            solstice = self.data[ key + ( IndicatorLunar.DATA_SOLSTICE, ) ]
            self.nextUpdate = self.getSmallestDateTime( equinox, self.getSmallestDateTime( self.nextUpdate, solstice ) )
            if equinox < solstice:
                menuItem.get_submenu().append( Gtk.MenuItem( _( "Equinox: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_EQUINOX, ) ) ) )
                menuItem.get_submenu().append( Gtk.MenuItem( _( "Solstice: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_SOLSTICE, ) ) ) )
            else:
                menuItem.get_submenu().append( Gtk.MenuItem( _( "Solstice: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_SOLSTICE, ) ) ) )
                menuItem.get_submenu().append( Gtk.MenuItem( _( "Equinox: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_EQUINOX, ) ) ) )

            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
            self.updateEclipseMenu( menuItem.get_submenu(), AstronomicalBodyType.Sun, IndicatorLunar.SUN_TAG )


    def updateEclipseMenu( self, menu, astronomicalBodyType, dataTag ):
        key = ( astronomicalBodyType, dataTag )
        menu.append( Gtk.MenuItem( _( "Eclipse" ) ) )
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Date/Time: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_ECLIPSE_DATE_TIME, ) ) ) )
        latitude = self.getDisplayData( key + ( IndicatorLunar.DATA_ECLIPSE_LATITUDE, ) )
        longitude = self.getDisplayData( key + ( IndicatorLunar.DATA_ECLIPSE_LONGITUDE, ) )
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Latitude/Longitude: " ) + latitude + " " + longitude ) )
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Type: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_ECLIPSE_TYPE, ) ) ) )


    def updatePlanetsMenu( self, menu ):
        planets = [ ]
        for planetName in self.planets:
            if not self.hideBody( AstronomicalBodyType.Planet, planetName.upper(), self.hideBodyIfNeverUp ):
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
                    menuItem = Gtk.MenuItem( IndicatorLunar.PLANET_AND_MOON_NAMES_TRANSLATIONS[ planetName ] )
                    subMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + IndicatorLunar.PLANET_AND_MOON_NAMES_TRANSLATIONS[ planetName ] )
                    menu.append( menuItem )

                self.updateCommonMenu( menuItem, AstronomicalBodyType.Planet, dataTag )

                # Planetary moons.
                if planetName in IndicatorLunar.PLANET_MOONS:
                    menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
                    menuItem.get_submenu().append( Gtk.MenuItem( _( "Major Moons" ) ) )
                    self.updatePlanetMoonsMenu( menuItem, IndicatorLunar.PLANET_MOONS[ planetName ] )


    def updatePlanetMoonsMenu( self, menuItem, moonNames ):
        moonNamesTranslated = [ ] # Lists the moon names in alphabetical order in the local language.
        for moonName in moonNames:
            moonNamesTranslated.append( [ moonName, IndicatorLunar.PLANET_AND_MOON_NAMES_TRANSLATIONS[ moonName ] ] )

        moonNamesTranslated = sorted( moonNamesTranslated, key = lambda x: ( x[ 1 ] ) )
        for moonName, moonNameTranslated in moonNamesTranslated:
            moonMenuItem = Gtk.MenuItem( IndicatorLunar.INDENT + IndicatorLunar.PLANET_AND_MOON_NAMES_TRANSLATIONS[ moonName ] )
            menuItem.get_submenu().append( moonMenuItem )

            dataTag = moonName.upper()
            subMenu = Gtk.Menu()
            self.updateRightAscensionDeclinationAzimuthAltitudeMenu( subMenu, AstronomicalBodyType.PlanetaryMoon, dataTag )
            subMenu.append( Gtk.SeparatorMenuItem() )

            subMenu.append( Gtk.MenuItem( _( "Earth Visible: " ) + self.getDisplayData( ( AstronomicalBodyType.PlanetaryMoon, dataTag, IndicatorLunar.DATA_EARTH_VISIBLE ) ) ) )
            subMenu.append( Gtk.SeparatorMenuItem() )

            subMenu.append( Gtk.MenuItem( _( "Offset from Planet (in planet radii)" ) ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "X: " ) + self.getDisplayData( ( AstronomicalBodyType.PlanetaryMoon, dataTag, IndicatorLunar.DATA_X_OFFSET ) ) ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Y: " ) + self.getDisplayData( ( AstronomicalBodyType.PlanetaryMoon, dataTag, IndicatorLunar.DATA_Y_OFFSET ) ) ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Z: " ) + self.getDisplayData( ( AstronomicalBodyType.PlanetaryMoon, dataTag, IndicatorLunar.DATA_Z_OFFSET ) ) ) )
            moonMenuItem.set_submenu( subMenu )


    def updateStarsMenu( self, menu ):
        stars = [ ] # List of lists.  Each sublist contains the star name followed by the translated name.
        for starName in self.stars:
            key = ( AstronomicalBodyType.Star, starName.upper() )
            if key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data and \
               self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_BODY_NEVER_UP and \
               self.hideBodyIfNeverUp:
                continue

            stars.append( [ starName, IndicatorLunar.STAR_NAMES_TRANSLATIONS[ starName ] ] )

        if len( stars ) > 0:
            starsMenuItem = Gtk.MenuItem( _( "Stars" ) )
            menu.append( starsMenuItem )

            if self.showStarsAsSubMenu:
                starsSubMenu = Gtk.Menu()
                starsMenuItem.set_submenu( starsSubMenu )

            if self.groupStarsByConstellation:
                constellations = { }
                for starName, starNameTranslated in stars:
                    constellationTranslated = self.getDisplayData( ( AstronomicalBodyType.Star, starName.upper(), IndicatorLunar.DATA_CONSTELLATION ) )
                    if constellationTranslated not in constellations:
                        constellations[ constellationTranslated ] = [ ]

                    constellations[ constellationTranslated ].append( [ starName, starNameTranslated ] )

                for constellationTranslated in sorted( constellations ):
                    if self.showStarsAsSubMenu:
                        constellationMenuItem = Gtk.MenuItem( constellationTranslated )
                        starsSubMenu.append( constellationMenuItem )
                        constellationSubMenu = Gtk.Menu()
                        constellationMenuItem.set_submenu( constellationSubMenu )
                    else:
                        menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + constellationTranslated )
                        menu.append( menuItem )

                    stars = sorted( constellations[ constellationTranslated ], key = lambda x: ( x[ 1 ] ) )
                    for starName, starNameTranslated in stars:
                        dataTag = starName.upper()
                        if self.showStarsAsSubMenu:
                            menuItem = Gtk.MenuItem( starNameTranslated )
                            constellationSubMenu.append( menuItem )
                        else:
                            menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + IndicatorLunar.INDENT + starNameTranslated )
                            menu.append( menuItem )
  
                        self.updateCommonMenu( menuItem, AstronomicalBodyType.Star, dataTag )
            else:
                stars = sorted( stars, key = lambda x: ( x[ 1 ] ) )
                for starName, starNameTranslated in stars:
                    dataTag = starName.upper()
                    if self.showStarsAsSubMenu:
                        menuItem = Gtk.MenuItem( starNameTranslated )
                        starsSubMenu.append( menuItem )
                    else:
                        menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + starNameTranslated )
                        menu.append( menuItem )

                    self.updateCommonMenu( menuItem, AstronomicalBodyType.Star, dataTag )


    def updateCometsMenu( self, menu ):
        comets = [ ]
        for comet in self.comets:
            key = ( AstronomicalBodyType.Comet, comet )
            if key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data and \
               self.hideBodyIfNeverUp and \
               (
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_BODY_NEVER_UP or \
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_DATA_BAD_DATA or \
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_DATA_NO_DATA
               ):
                continue # Skip comets which are never up or have no data or have bad data AND the user wants to hide comets on such conditions.

            if key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data or \
               key + ( IndicatorLunar.DATA_RISE_TIME, ) in self.data:
                comets.append( comet ) # Either key must be present - otherwise the comet has been dropped due to having too large a magnitude.

        if len( comets ) > 0:
            menuItem = Gtk.MenuItem( _( "Comets" ) )
            menu.append( menuItem )
            if self.showCometsAsSubMenu:
                cometsSubMenu = Gtk.Menu()
                menuItem.set_submenu( cometsSubMenu )

            for key in sorted( comets ): # Sorting by key also sorts the display name identically.
                if key in self.cometOEData:
                    displayName = self.getCometDisplayName( self.cometOEData[ key ] )
                else:
                    displayName = key # There is a comet but no data for it.

                if self.showCometsAsSubMenu:
                    menuItem = Gtk.MenuItem( displayName )
                    cometsSubMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + displayName )
                    menu.append( menuItem )

                # Comet data may not exist or comet data exists but is bad.
                cometDataIsMissingOrBad = ( key not in self.cometOEData ) or \
                                          ( key in self.cometOEData and ( AstronomicalBodyType.Comet, key, IndicatorLunar.DATA_MESSAGE ) in self.data )

                if cometDataIsMissingOrBad:
                    subMenu = Gtk.Menu()
                    subMenu.append( Gtk.MenuItem( self.getDisplayData( ( AstronomicalBodyType.Comet, key, IndicatorLunar.DATA_MESSAGE ) ) ) )
                    menuItem.set_submenu( subMenu )
                else:
                    self.updateCommonMenu( menuItem, AstronomicalBodyType.Comet, key )
                    self.addOnCometHandler( menuItem.get_submenu(), key )


    def addOnCometHandler( self, subMenu, comet ):
        for child in subMenu.get_children():
            child.set_name( comet )
            child.connect( "activate", self.onComet )


    def onComet( self, widget ):
        if "(" in widget.props.name:
            objectID = widget.props.name[ : widget.props.name.find( "(" ) ].strip()
        else:
            objectID = widget.props.name[ : widget.props.name.find( "/" ) ].strip()

        url = IndicatorLunar.COMET_ON_CLICK_URL + objectID.replace( "/", "%2F" ).replace( " ", "+" )
        if len( url ) > 0:
            webbrowser.open( url )


    def updateCommonMenu( self, menuItem, astronomicalBodyType, dataTag ):
        key = ( astronomicalBodyType, dataTag )
        subMenu = Gtk.Menu()

        if astronomicalBodyType == AstronomicalBodyType.Moon or \
           astronomicalBodyType == AstronomicalBodyType.Planet:
            subMenu.append( Gtk.MenuItem( _( "Illumination: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_ILLUMINATION, ) ) ) )

        if ( astronomicalBodyType == AstronomicalBodyType.Star and not self.groupStarsByConstellation ) or not astronomicalBodyType == AstronomicalBodyType.Star:
            subMenu.append( Gtk.MenuItem( _( "Constellation: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_CONSTELLATION, ) ) ) )

        subMenu.append( Gtk.MenuItem( _( "Magnitude: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_MAGNITUDE, ) ) ) )

        if astronomicalBodyType == AstronomicalBodyType.Moon or \
           astronomicalBodyType == AstronomicalBodyType.Planet or \
           astronomicalBodyType == AstronomicalBodyType.Star or \
           astronomicalBodyType == AstronomicalBodyType.Sun:
            tropicalSignName = self.getDisplayData( key + ( IndicatorLunar.DATA_TROPICAL_SIGN_NAME, ) ) 
            tropicalSignDegree = self.getDisplayData( key + ( IndicatorLunar.DATA_TROPICAL_SIGN_DEGREE, ) )
            tropicalSignMinute = self.getDisplayData( key + ( IndicatorLunar.DATA_TROPICAL_SIGN_MINUTE, ) )
            subMenu.append( Gtk.MenuItem( _( "Tropical Sign: " ) + tropicalSignName + " " + tropicalSignDegree + tropicalSignMinute ) )

        if astronomicalBodyType == AstronomicalBodyType.Moon:
            subMenu.append( Gtk.MenuItem( _( "Distance to Earth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_DISTANCE_TO_EARTH_KM, ) ) ) )

        if astronomicalBodyType == AstronomicalBodyType.Moon or \
           astronomicalBodyType == AstronomicalBodyType.Comet or \
           astronomicalBodyType == AstronomicalBodyType.Planet or \
           astronomicalBodyType == AstronomicalBodyType.Sun:
            subMenu.append( Gtk.MenuItem( _( "Distance to Earth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_DISTANCE_TO_EARTH, ) ) ) )

        if astronomicalBodyType == AstronomicalBodyType.Moon or \
           astronomicalBodyType == AstronomicalBodyType.Comet or \
           astronomicalBodyType == AstronomicalBodyType.Planet:
            subMenu.append( Gtk.MenuItem( _( "Distance to Sun: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_DISTANCE_TO_SUN, ) ) ) )

        if astronomicalBodyType == AstronomicalBodyType.Moon or \
           astronomicalBodyType == AstronomicalBodyType.Planet:
            subMenu.append( Gtk.MenuItem( _( "Bright Limb: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_BRIGHT_LIMB, ) ) ) )

        if astronomicalBodyType == AstronomicalBodyType.Planet and \
           dataTag == IndicatorLunar.PLANET_SATURN.upper():
            subMenu.append( Gtk.MenuItem( _( "Earth Tilt: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_EARTH_TILT, ) ) ) )
            subMenu.append( Gtk.MenuItem( _( "Sun Tilt: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_SUN_TILT, ) ) ) )

        subMenu.append( Gtk.SeparatorMenuItem() )
        self.updateRightAscensionDeclinationAzimuthAltitudeMenu( subMenu, astronomicalBodyType, dataTag )
        subMenu.append( Gtk.SeparatorMenuItem() )

        if key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data:
            subMenu.append( Gtk.MenuItem( self.getDisplayData( key + ( IndicatorLunar.DATA_MESSAGE, ) ) ) )
        else:
            data = [ ]
            data.append( [ key + ( IndicatorLunar.DATA_RISE_TIME, ), _( "Rise: " ), self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] ] )
            data.append( [ key + ( IndicatorLunar.DATA_SET_TIME, ), _( "Set: " ), self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] ] )
            self.nextUpdate = self.getSmallestDateTime( self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ], self.getSmallestDateTime( self.nextUpdate, self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] ) )

            if astronomicalBodyType == AstronomicalBodyType.Sun:
                data.append( [ key + ( IndicatorLunar.DATA_DAWN, ), _( "Dawn: " ), self.data[ key + ( IndicatorLunar.DATA_DAWN, ) ] ] )
                data.append( [ key + ( IndicatorLunar.DATA_DUSK, ), _( "Dusk: " ), self.data[ key + ( IndicatorLunar.DATA_DUSK, ) ] ] )
                self.nextUpdate = self.getSmallestDateTime( self.data[ key + ( IndicatorLunar.DATA_DAWN, ) ], self.getSmallestDateTime( self.nextUpdate, self.data[ key + ( IndicatorLunar.DATA_DUSK, ) ] ) )

            data = sorted( data, key = lambda x: ( x[ 2 ] ) )
            for key, text, dateTime in data:
                subMenu.append( Gtk.MenuItem( text + self.getDisplayData( key ) ) )

        menuItem.set_submenu( subMenu )


    def updateRightAscensionDeclinationAzimuthAltitudeMenu( self, menu, astronomicalBodyType, dataTag ):
        key = ( astronomicalBodyType, dataTag )
        menu.append( Gtk.MenuItem( _( "Azimuth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_AZIMUTH, ) ) ) )
        menu.append( Gtk.MenuItem( _( "Altitude: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_ALTITUDE, ) ) ) )
        menu.append( Gtk.SeparatorMenuItem() )
        menu.append( Gtk.MenuItem( _( "Right Ascension: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_RIGHT_ASCENSION, ) ) ) )
        menu.append( Gtk.MenuItem( _( "Declination: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_DECLINATION, ) ) ) )


    def updateSatellitesMenu( self, menu ):
        menuTextSatelliteNameNumberRiseTimes = [ ]
        for satelliteName, satelliteNumber in self.satellites: # key is satellite name/number.
            key = ( AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )
            if key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data and \
               self.hideSatelliteIfNoVisiblePass and \
               (
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_DATA_NO_DATA or \
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_SATELLITE_NEVER_RISES or \
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME or \
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS or \
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_SATELLITE_VALUE_ERROR
               ):
                continue

            if key + ( IndicatorLunar.DATA_RISE_TIME, ) in self.data:
                internationalDesignator = self.satelliteTLEData[ ( satelliteName, satelliteNumber ) ].getInternationalDesignator()
                riseTime = self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ]
            elif key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data and \
                 self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] != IndicatorLunar.MESSAGE_DATA_NO_DATA: # Any message other than "no data" will have satellite TLE data.
                internationalDesignator = self.satelliteTLEData[ ( satelliteName, satelliteNumber ) ].getInternationalDesignator()
                riseTime = self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ]
            else:
                internationalDesignator = "" # No TLE data so cannot retrieve any information about the satellite.
                riseTime = self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ]

            menuText = IndicatorLunar.SATELLITE_MENU_TEXT.replace( IndicatorLunar.SATELLITE_TAG_NAME, satelliteName ) \
                                                         .replace( IndicatorLunar.SATELLITE_TAG_NUMBER, satelliteNumber ) \
                                                         .replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, internationalDesignator )

            menuTextSatelliteNameNumberRiseTimes.append( [ menuText, satelliteName, satelliteNumber, riseTime ] )

        if len( menuTextSatelliteNameNumberRiseTimes ) > 0:
            if self.satellitesSortByDateTime:
                menuTextSatelliteNameNumberRiseTimes = sorted( menuTextSatelliteNameNumberRiseTimes, key = lambda x: ( x[ 3 ], x[ 0 ], x[ 1 ], x[ 2 ] ) )
            else:
                menuTextSatelliteNameNumberRiseTimes = sorted( menuTextSatelliteNameNumberRiseTimes, key = lambda x: ( x[ 0 ], x[ 1 ], x[ 2 ], x[ 3 ] ) )

            satellitesMenuItem = Gtk.MenuItem( _( "Satellites" ) )
            menu.append( satellitesMenuItem )
            if self.showSatellitesAsSubMenu:
                satellitesSubMenu = Gtk.Menu()
                satellitesMenuItem.set_submenu( satellitesSubMenu )

            now = str( datetime.datetime.utcnow() )
            for menuText, satelliteName, satelliteNumber, riseTime in menuTextSatelliteNameNumberRiseTimes: # key is satellite name/number.
                key = ( AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )
                subMenu = Gtk.Menu()
                if key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data:
                    if self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_SATELLITE_IS_CIRCUMPOLAR:
                        subMenu.append( Gtk.MenuItem( _( "Azimuth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_AZIMUTH, ) ) ) )
                        subMenu.append( Gtk.MenuItem( _( "Declination: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_DECLINATION, ) ) ) )

                    subMenu.append( Gtk.MenuItem( self.getDisplayData( key + ( IndicatorLunar.DATA_MESSAGE, ) ) ) )
                else:
                    subMenu.append( Gtk.MenuItem( _( "Rise" ) ) )
                    subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Date/Time: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_RISE_TIME, ) ) ) )
                    subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Azimuth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_RISE_AZIMUTH, ) ) ) )

                    subMenu.append( Gtk.MenuItem( _( "Set" ) ) )
                    subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Date/Time: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_SET_TIME, ) ) ) )
                    subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Azimuth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_SET_AZIMUTH, ) ) ) )

                    if not self.hideSatelliteIfNoVisiblePass:
                        subMenu.append( Gtk.MenuItem( _( "Visible: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_VISIBLE, ) ) ) )

                    # Add the rise to the next update, ensuring it is not in the past.
                    # Subtract a minute from the rise time to spoof the next update to happen earlier.
                    # This allows the update to occur and satellite notification to take place just prior to the satellite rise.
                    riseTimeMinusOneMinute = str( self.toDateTime( self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] ) - datetime.timedelta( minutes = 1 ) )
                    if riseTimeMinusOneMinute > now:
                        self.nextUpdate = self.getSmallestDateTime( riseTimeMinusOneMinute, self.nextUpdate )

                    # Add the set time to the next update, ensuring it is not in the past.
                    if self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] > now:
                        self.nextUpdate = self.getSmallestDateTime( self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ], self.nextUpdate )

                self.addOnSatelliteHandler( subMenu, satelliteName, satelliteNumber )

                if self.showSatellitesAsSubMenu:
                    menuItem = Gtk.MenuItem( menuText )
                    satellitesSubMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + menuText )
                    menu.append( menuItem )

                menuItem.set_submenu( subMenu )


    # Have found (very seldom) that a date/time may be generated from the pyephem backend with the .%f component
    # which may mean the value is zero but pyephem dropped it.
    # However this means the format does not match and parsing into a DateTime object fails.
    # So pre-check for .%f and if missing, add in ".0" to keep the parsing happy.
    def toDateTime( self, dateTimeAsString ):
        s = dateTimeAsString
        if re.search( r"\.\d+$", s ) is None:
            s += ".0"

        return datetime.datetime.strptime( s, IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSSdotFLOAT )


    # Compare two string dates in the format YYYY MM DD HH:MM:SS, returning the earliest.
    def getSmallestDateTime( self, firstDateTimeAsString, secondDateTimeAsString ):
        if firstDateTimeAsString < secondDateTimeAsString:
            return firstDateTimeAsString

        return secondDateTimeAsString


    def addOnSatelliteHandler( self, subMenu, satelliteName, satelliteNumber ):
        for child in subMenu.get_children():
            child.set_name( satelliteName + "-----" + satelliteNumber ) # Cannot pass the tuple - must be a string.
            child.connect( "activate", self.onSatellite )


    def onSatellite( self, widget ):
        satelliteTLE = self.satelliteTLEData.get( tuple( widget.props.name.split( "-----" ) ) )

        url = IndicatorLunar.SATELLITE_ON_CLICK_URL. \
              replace( IndicatorLunar.SATELLITE_TAG_NAME, satelliteTLE.getName() ). \
              replace( IndicatorLunar.SATELLITE_TAG_NUMBER, satelliteTLE.getNumber() ). \
              replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, satelliteTLE.getInternationalDesignator() )

        if len( url ) > 0:
            webbrowser.open( url )


    def updateCometOEData( self ):
        if datetime.datetime.utcnow() < ( self.lastUpdateCometOE + datetime.timedelta( hours = IndicatorLunar.COMET_OE_DOWNLOAD_PERIOD_HOURS ) ):
            return

        # The download period and cache age are the same, which means
        # when a update needs to be done, the cache age has also expired,
        # requiring a download, rendering the cache pointless.
        # The cache becomes useful only when the indicator is restarted
        # before the download period has expired.
        # The cache attempts to avoid the download source blocking a user
        # as a ressult of too many downloads in a given period.
        self.cometOEData, cacheDateTime = self.readFromCache( IndicatorLunar.COMET_OE_CACHE_BASENAME, datetime.datetime.now() - datetime.timedelta( hours = IndicatorLunar.COMET_OE_CACHE_MAXIMUM_AGE_HOURS ) ) # Returned data is either None or non-empty.
        if self.cometOEData is None:
            # Cache returned no result so download from the source.
            self.cometOEData = self.getCometOEData( self.cometOEURL )
            if self.cometOEData is None:
                self.cometOEData = { }
                summary = _( "Error Retrieving Comet OE Data" )
                message = _( "The comet OE data source could not be reached." )
                Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()
            elif len( self.cometOEData ) == 0:
                summary = _( "Empty Comet OE Data" )
                message = _( "The comet OE data retrieved was empty." )
                Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()
            else:
                self.writeToCache( self.cometOEData, IndicatorLunar.COMET_OE_CACHE_BASENAME )

            # Even if the data download failed or was empty, don't do another download until the required time elapses...don't want to bother the source!
            self.lastUpdateCometOE = datetime.datetime.utcnow()
        else:
            # Set the next update to occur when the cache is due to expire.
            self.lastUpdateCometOE = datetime.datetime.strptime( cacheDateTime, IndicatorLunar.DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + datetime.timedelta( hours = IndicatorLunar.COMET_OE_CACHE_MAXIMUM_AGE_HOURS )

        if self.cometsAddNew:
            self.addNewComets()


    def updateSatelliteTLEData( self ):
        if datetime.datetime.utcnow() < ( self.lastUpdateSatelliteTLE + datetime.timedelta( hours = IndicatorLunar.SATELLITE_TLE_DOWNLOAD_PERIOD_HOURS ) ):
            return

        # The download period and cache age are the same, which means
        # when a update needs to be done, the cache age has also expired,
        # requiring a download, rendering the cache pointless.
        # The cache becomes useful only when the indicator is restarted
        # before the download period has expired.
        # The cache attempts to avoid the download source blocking a user
        # as a ressult of too many downloads in a given period.
        self.satelliteTLEData, cacheDateTime = self.readFromCache( IndicatorLunar.SATELLITE_TLE_CACHE_BASENAME, datetime.datetime.now() - datetime.timedelta( hours = IndicatorLunar.SATELLITE_TLE_CACHE_MAXIMUM_AGE_HOURS ) ) # Returned data is either None or non-empty.
        if self.satelliteTLEData is None:
            # Cache returned no result so download from the source.
            self.satelliteTLEData = self.getSatelliteTLEData( self.satelliteTLEURL )
            if self.satelliteTLEData is None:
                self.satelliteTLEData = { }
                summary = _( "Error Retrieving Satellite TLE Data" )
                message = _( "The satellite TLE data source could not be reached." )
                Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()
            elif len( self.satelliteTLEData ) == 0:
                summary = _( "Empty Satellite TLE Data" )
                message = _( "The satellite TLE data retrieved was empty." )
                Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()
            else:
                self.writeToCache( self.satelliteTLEData, IndicatorLunar.SATELLITE_TLE_CACHE_BASENAME )

            # Even if the data download failed or was empty, don't do another download until the required time elapses...don't want to bother the source!
            self.lastUpdateSatelliteTLE = datetime.datetime.utcnow()
        else:
            # Set the next update to occur when the cache is due to expire.
            self.lastUpdateSatelliteTLE = datetime.datetime.strptime( cacheDateTime, IndicatorLunar.DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + datetime.timedelta( hours = IndicatorLunar.SATELLITE_TLE_CACHE_MAXIMUM_AGE_HOURS )

        if self.satellitesAddNew:
            self.addNewSatellites()


    # Creates an SVG icon file representing the moon given the illumination and bright limb angle.
    #
    #    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
    #
    #    brightLimbAngleInDegrees The angle of the bright limb, relative to zenith, ranging from 0 to 360 inclusive.
    #                             Ignored if illuminationPercentage is 0 or 100.
    def createIcon( self, illuminationPercentage, brightLimbAngleInDegrees, svgFilename ):
        width = 100
        height = 100
        radius = float( width / 2 ) * 0.8 # The radius of the moon should have the full moon take up most of the viewing area but with a boundary.
        colour = self.getThemeColour()
        if illuminationPercentage == 0 or illuminationPercentage == 100:
            svgStart = '<circle cx="' + str( width / 2 ) + '" cy="' + str( height / 2 ) + '" r="' + str( radius )

            if illuminationPercentage == 0: # New
                svg = svgStart + '" fill="none" stroke="#' + colour + '" stroke-width="2" />'
            else: # Full
                svg = svgStart + '" fill="#' + colour + '" />'

        else:
            svgStart = '<path d="M ' + str( width / 2 ) + ' ' + str( height / 2 ) + ' h-' + str( radius ) + ' a ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + str( radius * 2 ) + ' 0'
            svgEnd = ' transform="rotate(' + str( brightLimbAngleInDegrees * -1 ) + ' ' + str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="#' + colour + '" />'

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

        try:
            with open( svgFilename, "w" ) as f:
                f.write( header + svg + footer )
                f.close()

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing: " + svgFilename )



    def getThemeName( self ): return Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )


    def getThemeColour( self ):
        iconFilenameForCurrentTheme = "/usr/share/icons/" + self.getThemeName() + "/scalable/apps/" + IndicatorLunar.ICON + ".svg"
        try:
            with open( iconFilenameForCurrentTheme, "r" ) as file:
                data = file.read()
                index = data.find( "style=\"fill:#" )
                themeColour = data[ index + 13 : index + 19 ]

        except Exception as e:
            logging.exception( e )
            logging.error( "Error reading SVG icon: " + iconFilenameForCurrentTheme )
            themeColour = "fff200" # Default to hicolor.

        return themeColour


    # Ideally should be able to create the icon with the same name each time.
    # Due to a bug, the icon name must change between calls to setting the icon.
    # So change the name each time - using the current date/time.
    #    https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620
    #    http://askubuntu.com/questions/490634/application-indicator-icon-not-changing-until-clicked
    def getIconName( self ): return IndicatorLunar.ICON_BASE_NAME + str( datetime.datetime.utcnow().strftime( "%y%m%d%H%M%S" ) )


    def getIconFilename( self, iconName ): return IndicatorLunar.ICON_BASE_PATH + "/" + iconName + ".svg"


    def purgeIcons( self ):
        oldIcons = glob.glob( IndicatorLunar.ICON_BASE_PATH + "/" + IndicatorLunar.ICON_BASE_NAME + "*" )
        for oldIcon in oldIcons:
            os.remove( oldIcon )


    def updateAstronomicalInformation( self, ephemNow, hideBodyIfNeverUp, hideCometGreaterThanMagnitude, hideSatelliteIfNoVisiblePass ):
        self.updateMoon( ephemNow, hideBodyIfNeverUp )
        self.updateSun( ephemNow, hideBodyIfNeverUp )
        self.updatePlanets( ephemNow, hideBodyIfNeverUp )
        self.updateStars( ephemNow, hideBodyIfNeverUp )
        self.updateComets( ephemNow, hideBodyIfNeverUp, hideCometGreaterThanMagnitude )
        self.updateSatellites( ephemNow, hideSatelliteIfNoVisiblePass )


    # http://www.ga.gov.au/geodesy/astro/moonrise.jsp
    # http://futureboy.us/fsp/moon.fsp
    # http://www.geoastro.de/moondata/index.html
    # http://www.geoastro.de/SME/index.htm
    # http://www.geoastro.de/elevazmoon/index.htm
    # http://www.geoastro.de/altazsunmoon/index.htm
    # http://www.geoastro.de/sundata/index.html
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    def updateMoon( self, ephemNow, hideIfNeverUp ):
        if self.showMoon:
            self.updateCommon( ephem.Moon( self.getCity( ephemNow ) ), AstronomicalBodyType.Moon, IndicatorLunar.MOON_TAG, ephemNow, hideIfNeverUp )
            if not self.hideBody( AstronomicalBodyType.Moon, IndicatorLunar.MOON_TAG, hideIfNeverUp ):
                key = ( AstronomicalBodyType.Moon, IndicatorLunar.MOON_TAG )
                lunarIlluminationPercentage = int( self.data[ key  + ( IndicatorLunar.DATA_ILLUMINATION, ) ] )
                self.data[ key + ( IndicatorLunar.DATA_PHASE, ) ] = self.getLunarPhase( ephemNow, lunarIlluminationPercentage )
                self.data[ key + ( IndicatorLunar.DATA_FIRST_QUARTER, ) ] = str( ephem.next_first_quarter_moon( ephemNow ).datetime() )
                self.data[ key + ( IndicatorLunar.DATA_FULL, ) ] = str( ephem.next_full_moon( ephemNow ).datetime() )
                self.data[ key + ( IndicatorLunar.DATA_THIRD_QUARTER, ) ] = str( ephem.next_last_quarter_moon( ephemNow ).datetime() )
                self.data[ key + ( IndicatorLunar.DATA_NEW, ) ] = str( ephem.next_new_moon( ephemNow ).datetime() )
                self.updateEclipse( ephemNow, AstronomicalBodyType.Moon, IndicatorLunar.MOON_TAG )


    # Get the lunar phase for the given date/time and illumination percentage.
    #
    #    ephemNow Date/time.
    #    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
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


    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    # http://www.ga.gov.au/geodesy/astro/sunrise.jsp
    # http://www.geoastro.de/elevaz/index.htm
    # http://www.geoastro.de/SME/index.htm
    # http://www.geoastro.de/altazsunmoon/index.htm
    # http://futureboy.us/fsp/sun.fsp
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    def updateSun( self, ephemNow, hideIfNeverUp ):
        if self.showSun:
            city = self.getCity( ephemNow )
            sun = ephem.Sun( city )
            self.updateCommon( sun, AstronomicalBodyType.Sun, IndicatorLunar.SUN_TAG, ephemNow, hideIfNeverUp )
            if not self.hideBody( AstronomicalBodyType.Sun, IndicatorLunar.SUN_TAG, hideIfNeverUp ):
                key = ( AstronomicalBodyType.Sun, IndicatorLunar.SUN_TAG )
                try:
                    # Dawn/Dusk.
                    city = self.getCity( ephemNow )
                    city.horizon = '-6' # -6 = civil twilight, -12 = nautical, -18 = astronomical (http://stackoverflow.com/a/18622944/2156453)
                    dawn = city.next_rising( sun, use_center = True )
                    dusk = city.next_setting( sun, use_center = True )
                    self.data[ key + ( IndicatorLunar.DATA_DAWN, ) ] = str( dawn.datetime() )
                    self.data[ key + ( IndicatorLunar.DATA_DUSK, ) ] = str( dusk.datetime() )

                except ( ephem.AlwaysUpError, ephem.NeverUpError ):
                    pass # No need to add a message here as update common would already have done so.

                equinox = ephem.next_equinox( ephemNow )
                solstice = ephem.next_solstice( ephemNow )
                self.data[ key + ( IndicatorLunar.DATA_EQUINOX, ) ] = str( equinox.datetime() )
                self.data[ key + ( IndicatorLunar.DATA_SOLSTICE, ) ] = str( solstice.datetime() )

                self.updateEclipse( ephemNow, AstronomicalBodyType.Sun, IndicatorLunar.SUN_TAG )


    def updateEclipse( self, ephemNow, astronomicalBodyType, dataTag ):
        if dataTag == IndicatorLunar.SUN_TAG:
            eclipseInformation = eclipse.getEclipseForUTC( ephemNow.datetime(), False )
        else:
            eclipseInformation = eclipse.getEclipseForUTC( ephemNow.datetime(), True )

        if eclipseInformation is None:
            logging.error( "No eclipse information found!" )
        else:
            key = ( astronomicalBodyType, dataTag )
            self.data[ key + ( IndicatorLunar.DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ] + ".0" # Needed to bring the date/time format into line with date/time generated by PyEphem.
            self.data[ key + ( IndicatorLunar.DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
            self.data[ key + ( IndicatorLunar.DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ] 
            self.data[ key + ( IndicatorLunar.DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


    # http://www.geoastro.de/planets/index.html
    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    def updatePlanets( self, ephemNow, hideIfNeverUp ):
        for planetName in self.planets:
            planet = getattr( ephem, planetName )() # Dynamically instantiate the planet object.
            planet.compute( self.getCity( ephemNow ) )
            self.updateCommon( planet, AstronomicalBodyType.Planet, planetName.upper(), ephemNow, hideIfNeverUp )
            if not self.hideBody( AstronomicalBodyType.Planet, planetName.upper(), hideIfNeverUp ):
                if planetName == IndicatorLunar.PLANET_SATURN:
                    key = ( AstronomicalBodyType.Planet, planetName.upper() )
                    self.data[ key + ( IndicatorLunar.DATA_EARTH_TILT, ) ] = str( round( math.degrees( planet.earth_tilt ), 1 ) )
                    self.data[ key + ( IndicatorLunar.DATA_SUN_TILT, ) ] = str( round( math.degrees( planet.sun_tilt ), 1 ) )

                city = self.getCity( ephemNow )
                if planetName in IndicatorLunar.PLANET_MOONS:
                    for moonName in IndicatorLunar.PLANET_MOONS[ planetName ]:
                        moon = getattr( ephem, moonName )() # Dynamically instantiate the moon object.
                        moon.compute( city )
                        self.updateRightAscensionDeclinationAzimuthAltitude( moon, AstronomicalBodyType.PlanetaryMoon, moonName.upper() )
                        key = ( AstronomicalBodyType.PlanetaryMoon, moonName.upper() )
                        self.data[ key + ( IndicatorLunar.DATA_EARTH_VISIBLE, ) ] = str( bool( moon.earth_visible ) )
                        self.data[ key + ( IndicatorLunar.DATA_X_OFFSET, ) ] = str( round( moon.x, 1 ) )
                        self.data[ key + ( IndicatorLunar.DATA_Y_OFFSET, ) ] = str( round( moon.y, 1 ) )
                        self.data[ key + ( IndicatorLunar.DATA_Z_OFFSET, ) ] = str( round( moon.z, 1 ) )


    # http://aa.usno.navy.mil/data/docs/mrst.php
    def updateStars( self, ephemNow, hideIfNeverUp ):
        for starName in self.stars:
            star = ephem.star( starName )
            star.compute( self.getCity( ephemNow ) )
            self.updateCommon( star, AstronomicalBodyType.Star, star.name.upper(), ephemNow, hideIfNeverUp )


    # Computes the rise/set and other information for comets.
    #
    # http://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
    # http://www.minorplanetcenter.net/iau/Ephemerides/Soft03.html        
    def updateComets( self, ephemNow, hideIfNeverUp, hideIfGreaterThanMagnitude ):
        for key in self.comets:
            if key in self.cometOEData:
                comet = ephem.readdb( self.cometOEData[ key ] )
                comet.compute( self.getCity( ephemNow ) )
                if math.isnan( comet.earth_distance ) or math.isnan( comet.phase ) or math.isnan( comet.size ) or math.isnan( comet.sun_distance ): # Have found tha data file may contain ***** in lieu of actual data!
                    self.data[ ( AstronomicalBodyType.Comet, key, IndicatorLunar.DATA_MESSAGE ) ] = IndicatorLunar.MESSAGE_DATA_BAD_DATA
                else:
                    if float( comet.mag ) <= float( hideIfGreaterThanMagnitude ):
                        self.updateCommon( comet, AstronomicalBodyType.Comet, key, ephemNow, hideIfNeverUp )
            else:
                self.data[ ( AstronomicalBodyType.Comet, key, IndicatorLunar.DATA_MESSAGE ) ] = IndicatorLunar.MESSAGE_DATA_NO_DATA


    # Calculates the common attributes such as rise/set, illumination, constellation, magnitude, tropical sign, distance, bright limb angle and RA/Dec/Az/Alt.
    # Data tags such as RISE_TIME and/or MESSAGE will be added to the data dict.
    def updateCommon( self, body, astronomicalBodyType, dataTag, ephemNow, hideIfNeverUp ):
        key = ( astronomicalBodyType, dataTag )
        try:
            city = self.getCity( ephemNow )
            rising = city.next_rising( body )
            setting = city.next_setting( body )
            self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] = str( rising.datetime() )
            self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] = str( setting.datetime() )

        except ephem.AlwaysUpError:
            self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] = IndicatorLunar.MESSAGE_BODY_ALWAYS_UP

        except ephem.NeverUpError:
            self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] = IndicatorLunar.MESSAGE_BODY_NEVER_UP

        if not self.hideBody( astronomicalBodyType, dataTag, hideIfNeverUp ):
            body.compute( self.getCity( ephemNow ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.

            if astronomicalBodyType == AstronomicalBodyType.Moon or \
               astronomicalBodyType == AstronomicalBodyType.Planet:
                self.data[ key + ( IndicatorLunar.DATA_ILLUMINATION, ) ] = str( self.getPhase( body ) )

            self.data[ key + ( IndicatorLunar.DATA_CONSTELLATION, ) ] = ephem.constellation( body )[ 1 ]
            self.data[ key + ( IndicatorLunar.DATA_MAGNITUDE, ) ] = str( round( body.mag, 1 ) )

            if astronomicalBodyType != AstronomicalBodyType.Comet:
                tropicalSignName, tropicalSignDegree, tropicalSignMinute = self.getTropicalSign( body, ephemNow )
                self.data[ key + ( IndicatorLunar.DATA_TROPICAL_SIGN_NAME, ) ] = tropicalSignName
                self.data[ key + ( IndicatorLunar.DATA_TROPICAL_SIGN_DEGREE, ) ] = tropicalSignDegree
                self.data[ key + ( IndicatorLunar.DATA_TROPICAL_SIGN_MINUTE, ) ] = tropicalSignMinute

            if astronomicalBodyType == AstronomicalBodyType.Moon:
                self.data[ key + ( IndicatorLunar.DATA_DISTANCE_TO_EARTH_KM, ) ] = str( round( body.earth_distance * ephem.meters_per_au / 1000 ) )
                self.data[ key + ( IndicatorLunar.DATA_DISTANCE_TO_EARTH, ) ] = str( round( body.earth_distance, 5 ) )
                self.data[ key + ( IndicatorLunar.DATA_DISTANCE_TO_SUN, ) ] = str( round( body.sun_distance, 2 ) )

            if astronomicalBodyType == AstronomicalBodyType.Comet or \
               astronomicalBodyType == AstronomicalBodyType.Planet:
                self.data[ key + ( IndicatorLunar.DATA_DISTANCE_TO_EARTH, ) ] = str( round( body.earth_distance, 1 ) )
                self.data[ key + ( IndicatorLunar.DATA_DISTANCE_TO_SUN, ) ] = str( round( body.sun_distance, 1 ) )

            if astronomicalBodyType == AstronomicalBodyType.Sun:
                self.data[ key + ( IndicatorLunar.DATA_DISTANCE_TO_EARTH, ) ] = str( round( body.earth_distance, 2 ) )

            if astronomicalBodyType == AstronomicalBodyType.Moon or \
               astronomicalBodyType == AstronomicalBodyType.Planet:
                self.data[ key + ( IndicatorLunar.DATA_BRIGHT_LIMB, ) ] = str( round( self.getZenithAngleOfBrightLimb( self.getCity( ephemNow ), body ) ) )

            self.updateRightAscensionDeclinationAzimuthAltitude( body, astronomicalBodyType, dataTag )


    def hideBody( self, astronomicalBodyType, dataTag, hideIfNeverUp ):
        key = ( astronomicalBodyType, dataTag, IndicatorLunar.DATA_MESSAGE )
        return \
            key in self.data and \
            self.data[ key ] == IndicatorLunar.MESSAGE_BODY_NEVER_UP and \
            hideIfNeverUp


    def getPhase( self, body ): return round( body.phase )


    # Compute the right ascension, declination, azimuth and altitude for a body.
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    def updateRightAscensionDeclinationAzimuthAltitude( self, body, astronomicalBodyType, dataTag ):
        key = ( astronomicalBodyType, dataTag )
        self.data[ key + ( IndicatorLunar.DATA_RIGHT_ASCENSION, ) ] = str( body.ra )
        self.data[ key + ( IndicatorLunar.DATA_DECLINATION, ) ] = str( body.dec )
        self.data[ key + ( IndicatorLunar.DATA_AZIMUTH, ) ] = str( body.az )
        self.data[ key + ( IndicatorLunar.DATA_ALTITUDE, ) ] = str( body.alt )


    # Code courtesy of Ignius Drake.
    def getTropicalSign( self, body, ephemNow ):
        ( year, month, day ) = ephemNow.triple()
        epochAdjusted = float( year ) + float( month ) / 12.0 + float( day ) / 365.242
        ephemNowDate = str( ephemNow ).split( " " )

        bodyCopy = body.copy() # Computing the tropical sign changes the body's date/time/epoch (shared by other downstream calculations), so make a copy of the body and use that.
        bodyCopy.compute( ephemNowDate[ 0 ], epoch = str( epochAdjusted ) )
        planetCoordinates = str( ephem.Ecliptic( bodyCopy ).lon ).split( ":" )

        if float( planetCoordinates[ 2 ] ) > 30:
            planetCoordinates[ 1 ] = str( int ( planetCoordinates[ 1 ] ) + 1 )

        tropicalSignDegree = int( planetCoordinates[ 0 ] ) % 30
        tropicalSignMinute = str( planetCoordinates[ 1 ] )
        tropicalSignIndex = int( planetCoordinates[ 0 ] ) / 30
        tropicalSignName = IndicatorLunar.TROPICAL_SIGNS[ int( tropicalSignIndex ) ]

        return ( tropicalSignName, str( tropicalSignDegree ), tropicalSignMinute )


    # Compute the bright limb angle (relative to zenith) between the sun and a planetary body.
    # Measured in degrees counter clockwise from a positive y axis.
    #
    # References:
    #  'Astronomical Algorithms' Second Edition by Jean Meeus (chapters 14 and 48).
    #  'Practical Astronomy with Your Calculator' by Peter Duffett-Smith (chapters 59 and 68).
    #  http://www.geoastro.de/moonlibration/ (pictures of moon are wrong but the data is correct).
    #  http://www.geoastro.de/SME/
    #  http://futureboy.us/fsp/moon.fsp
    #  http://www.timeanddate.com/moon/australia/sydney
    #
    # Other references...
    #  http://www.mat.uc.pt/~efemast/help/en/lua_fas.htm
    #  https://sites.google.com/site/astronomicalalgorithms
    #  http://stackoverflow.com/questions/13463965/pyephem-sidereal-time-gives-unexpected-result
    #  https://github.com/brandon-rhodes/pyephem/issues/24
    #  http://stackoverflow.com/questions/13314626/local-solar-time-function-from-utc-and-longitude/13425515#13425515
    #  http://astro.ukho.gov.uk/data/tn/naotn74.pdf
    def getZenithAngleOfBrightLimb( self, city, body ):
        sun = ephem.Sun( city )

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
        y = math.cos( sun.dec ) * math.sin( sun.ra - body.ra )
        x = math.cos( body.dec ) * math.sin( sun.dec ) - math.sin( body.dec ) * math.cos( sun.dec ) * math.cos( sun.ra - body.ra )
        positionAngleOfBrightLimb = math.atan2( y, x )

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
        hourAngle = city.sidereal_time() - body.ra
        y = math.sin( hourAngle )
        x = math.tan( city.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
        parallacticAngle = math.atan2( y, x )

        return math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )


    # Uses TLE data collated by Dr T S Kelso (http://celestrak.com/NORAD/elements) with PyEphem to compute satellite rise/pass/set times.
    #
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
    #
    # Therefore...
    #    If a satellite is yet to rise, show the upcoming rise/set time.
    #    If a satellite is currently passing over, show the rise/set time for that pass.
    #
    # This allows the user to see the rise/set time for the current pass as it is happening.
    # When the pass completes and an update occurs, the rise/set for the next pass will be displayed.
    def updateSatellites( self, ephemNow, hideIfNoVisiblePass ):
        for key in self.satellites:
            if key in self.satelliteTLEData:
                self.calculateNextSatellitePass( ephemNow, key, self.satelliteTLEData[ key ], hideIfNoVisiblePass )
            else:
                self.data[ ( AstronomicalBodyType.Satellite, " ".join( key ), IndicatorLunar.DATA_MESSAGE ) ] = IndicatorLunar.MESSAGE_DATA_NO_DATA


    def calculateNextSatellitePass( self, ephemNow, key, satelliteTLE, hideOnNoVisiblePass ):
        key = ( AstronomicalBodyType.Satellite, " ".join( key ) )
        currentDateTime = ephemNow
        endDateTime = ephem.Date( ephemNow + ephem.hour * 24 * 2 ) # Stop looking for passes 2 days from ephemNow.
        message = None
        while currentDateTime < endDateTime:
            city = self.getCity( currentDateTime )
            satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
            satellite.compute( city )
            try:
                nextPass = city.next_pass( satellite )

            except ValueError:
                if satellite.circumpolar:
                    self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] = IndicatorLunar.MESSAGE_SATELLITE_IS_CIRCUMPOLAR
                    self.data[ key + ( IndicatorLunar.DATA_AZIMUTH, ) ] = str( satellite.az )
                    self.data[ key + ( IndicatorLunar.DATA_DECLINATION, ) ] = str( satellite.dec )
                elif satellite.neverup:
                    message = IndicatorLunar.MESSAGE_SATELLITE_NEVER_RISES
                else:
                    message = IndicatorLunar.MESSAGE_SATELLITE_VALUE_ERROR

                break

            if not self.isSatellitePassValid( nextPass ):
                message = IndicatorLunar.MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS
                break

            # The pass is valid.  If the satellite is currently passing, work out when it rose...
            if nextPass[ 0 ] > nextPass[ 4 ]: # The rise time is after set time, so the satellite is currently passing.
                setTime = nextPass[ 4 ]
                nextPass = self.calculateSatellitePassForRisingPriorToNow( currentDateTime, satelliteTLE )
                if nextPass is None:
                    currentDateTime = ephem.Date( setTime + ephem.minute * 30 ) # Could not determine the rise, so look for the next pass.
                    continue

            # Now have a satellite rise/transit/set; determine if the pass is visible (and if the user wants only visible passes).
            passIsVisible = self.isSatellitePassVisible( satellite, nextPass[ 2 ] )
            if hideOnNoVisiblePass and not passIsVisible:
                currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )
                continue

            # The pass is visible and the user wants only visible passes OR the user wants any pass...
            self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] = str( nextPass[ 0 ].datetime() )
            self.data[ key + ( IndicatorLunar.DATA_RISE_AZIMUTH, ) ] = str( nextPass[ 1 ] )
            self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] = str( nextPass[ 4 ].datetime() )
            self.data[ key + ( IndicatorLunar.DATA_SET_AZIMUTH, ) ] = str( nextPass[ 5 ] )
            self.data[ key + ( IndicatorLunar.DATA_VISIBLE, ) ] = str( passIsVisible )

            break

        if currentDateTime >= endDateTime:
            message = IndicatorLunar.MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME

        if message is not None:
            self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] = message


    def calculateSatellitePassForRisingPriorToNow( self, ephemNow, satelliteTLE ):
        currentDateTime = ephem.Date( ephemNow - ephem.minute ) # Start looking from one minute ago.
        endDateTime = ephem.Date( ephemNow - ephem.hour * 1 ) # Only look back an hour for the rise time (then just give up).
        nextPass = None
        while currentDateTime > endDateTime:
            city = self.getCity( currentDateTime )
            satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
            satellite.compute( city )
            try:
                nextPass = city.next_pass( satellite )
                if not self.isSatellitePassValid( nextPass ):
                    nextPass = None
                    break # Unlikely to happen but better to be safe and check!

                if nextPass[ 0 ] < nextPass[ 4 ]:
                    break

                currentDateTime = ephem.Date( currentDateTime - ephem.minute )

            except:
                nextPass = None
                break # This should never happen as the satellite has a rise and set (is not circumpolar or never up).

        return nextPass


    def isSatellitePassValid( self, satellitePass ):
        return \
            satellitePass is not None and \
            len( satellitePass ) == 6 and \
            satellitePass[ 0 ] is not None and \
            satellitePass[ 1 ] is not None and \
            satellitePass[ 2 ] is not None and \
            satellitePass[ 3 ] is not None and \
            satellitePass[ 4 ] is not None and \
            satellitePass[ 5 ] is not None


    # Determine if a satellite pass is visible or not...
    #
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

        return satellite.eclipsed is False and \
               sun.alt > ephem.degrees( "-18" ) and \
               sun.alt < ephem.degrees( "-6" )


    # Used to instantiate a new city object/observer.
    # Typically after calculations (or exceptions) the city date is altered.
    def getCity( self, date = None ):
        city = ephem.city( self.cityName )
        if date is not None:
            city.date = date

        return city


    def onAbout( self, widget ):
        pythonutils.setAllMenuItemsSensitive( self.menu, False )
        dialog = pythonutils.createAboutDialog(
            [ IndicatorLunar.AUTHOR ],
            IndicatorLunar.ABOUT_COMMENTS, 
            IndicatorLunar.ABOUT_CREDITS,
            _( "Credits" ),
            Gtk.License.GPL_3_0,
            IndicatorLunar.ICON,
            INDICATOR_NAME,
            IndicatorLunar.WEBSITE,
            IndicatorLunar.VERSION,
            _( "translator-credits" ),
            _( "View the" ),
            _( "text file." ),
            _( "changelog" ) )

        dialog.run()
        dialog.destroy()
        pythonutils.setAllMenuItemsSensitive( self.menu, True )


    def waitForUpdateToFinish( self, widget ):
        while not self.lock.acquire( blocking = False ):
            time.sleep( 1 )

        GLib.idle_add( self.onPreferencesInternal, widget )        


#TODO Can we just turn off the Prefernces/About whilst an update is underway?
# Look at PPA...the update is delayed if Prefs are open...do something similar here?
#Also need to check if an update is underway and if so, alert the user (either use existing waitForUpdateToFinish or just tell user they can try later).
#May not need to worry about an update occurring whilst Pref/About open (or maybe just Pref) as Pref remove the timer ID.
    def onPreferences( self, widget ):
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
        pythonutils.setAllMenuItemsSensitive( self.menu, False )
        GLib.source_remove( self.eventSourceID ) # Ensure no update occurs whilst the preferences are open.

        TAB_ICON = 0
        TAB_MENU = 1
        TAB_PLANETS_STARS = 2
        TAB_COMETS = 3
        TAB_SATELLITES = 4
        TAB_NOTIFICATIONS = 5
        TAB_GENERAL = 6

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
        indicatorText.set_tooltip_text( _(
            "The text shown next to the indicator icon\n" + \
            "(or shown as a tooltip, where applicable).\n\n" + \
            "If a body is unchecked or no longer exists\n" + \
            "(such as a comet/satellite not on the list),\n" + \
            "the tag will be automatically removed." ) )
        box.pack_start( indicatorText, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        self.tagsAdded = { } # A list would use less memory, but a dict (after running timing tests) is significantly faster!
        self.tagsRemoved = { } # See above!

        COLUMN_TAG = 0
        COLUMN_TRANSLATED_TAG = 1
        COLUMN_VALUE = 2
        displayTagsStore = Gtk.ListStore( str, str, str ) # Tag, translated tag, value.
        tags = re.split( "(\[[^\[^\]]+\])", self.indicatorText )
        for key in self.data.keys():
            hideMessage = self.data[ key ] == IndicatorLunar.MESSAGE_BODY_NEVER_UP or \
                      self.data[ key ] == IndicatorLunar.MESSAGE_DATA_BAD_DATA or \
                      self.data[ key ] == IndicatorLunar.MESSAGE_DATA_NO_DATA or \
                      self.data[ key ] == IndicatorLunar.MESSAGE_SATELLITE_NEVER_RISES or \
                      self.data[ key ] == IndicatorLunar.MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME or \
                      self.data[ key ] == IndicatorLunar.MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS or \
                      self.data[ key ] == IndicatorLunar.MESSAGE_SATELLITE_VALUE_ERROR

            hideBody = self.hideBodyIfNeverUp or self.hideSatelliteIfNoVisiblePass

            if hideMessage and hideBody:
                continue

            self.appendToDisplayTagsStore( key, self.getDisplayData( key ), displayTagsStore )
            tag = "[" + key[ 1 ] + " " + key[ 2 ] + "]"
            if tag in tags:
                i = tags.index( tag )
                tags[ i ] = ""

        unknownTags = [ ]
        for tag in tags:
            if re.match( "\[[^\[^\]]+\]", tag ) is not None:
                self.indicatorText = self.indicatorText.replace( tag, "" )

        indicatorText.set_text( self.translateTags( displayTagsStore, True, self.indicatorText ) ) # Need to translate the tags into the local language.

        displayTagsStoreSort = Gtk.TreeModelSort( model = displayTagsStore )
        displayTagsStoreSort.set_sort_column_id( COLUMN_TRANSLATED_TAG, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( displayTagsStoreSort )
        tree.set_hexpand( True )
        tree.set_vexpand( True )

        treeViewColumn = Gtk.TreeViewColumn( _( "Tag" ), Gtk.CellRendererText(), text = COLUMN_TRANSLATED_TAG )
        treeViewColumn.set_sort_column_id( COLUMN_TRANSLATED_TAG )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Value" ), Gtk.CellRendererText(), text = COLUMN_VALUE )
        treeViewColumn.set_sort_column_id( COLUMN_VALUE )
        tree.append_column( treeViewColumn )

        tree.set_tooltip_text( _(
            "Double click to add a\n" + \
            "tag to the icon text." ) )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onTagDoubleClick, COLUMN_TRANSLATED_TAG, indicatorText )

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
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( _( "Show" ) )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 0, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 40 ) # Bug in Python - must specify the parameter names!
        box.set_margin_left( 20 )

        showMoonCheckbox = Gtk.CheckButton( _( "Moon" ) )
        showMoonCheckbox.set_active( self.showMoon )
        showMoonCheckbox.set_tooltip_text( _( "Show the moon." ) )
        showMoonCheckbox.connect( "toggled", self.onMoonSunToggled, IndicatorLunar.MOON_TAG, AstronomicalBodyType.Moon )
        box.pack_start( showMoonCheckbox, False, False, 0 )

        showSunCheckbox = Gtk.CheckButton( _( "Sun" ) )
        showSunCheckbox.set_active( self.showSun )
        showSunCheckbox.set_tooltip_text( _( "Show the sun." ) )
        showSunCheckbox.connect( "toggled", self.onMoonSunToggled, IndicatorLunar.SUN_TAG, AstronomicalBodyType.Sun )
        box.pack_start( showSunCheckbox, False, False, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        label = Gtk.Label( _( "Show as submenus" ) )
        label.set_halign( Gtk.Align.START )
        label.set_margin_top( 10 )
        grid.attach( label, 0, 2, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 40 ) # Bug in Python - must specify the parameter names!
        box.set_margin_left( 20 )

        showPlanetsAsSubmenuCheckbox = Gtk.CheckButton( _( "Planets" ) )
        showPlanetsAsSubmenuCheckbox.set_active( self.showPlanetsAsSubMenu )
        showPlanetsAsSubmenuCheckbox.set_tooltip_text( _( "Show planets as submenus." ) )
        box.pack_start( showPlanetsAsSubmenuCheckbox, False, False, 0 )

        showStarsAsSubmenuCheckbox = Gtk.CheckButton( _( "Stars" ) )
        showStarsAsSubmenuCheckbox.set_tooltip_text( _( "Show stars as submenus." ) )
        showStarsAsSubmenuCheckbox.set_active( self.showStarsAsSubMenu )
        box.pack_start( showStarsAsSubmenuCheckbox, False, False, 0 )

        showCometsAsSubmenuCheckbox = Gtk.CheckButton( _( "Comets" ) )
        showCometsAsSubmenuCheckbox.set_tooltip_text( _( "Show comets as submenus." ) )
        showCometsAsSubmenuCheckbox.set_active( self.showCometsAsSubMenu )
        box.pack_start( showCometsAsSubmenuCheckbox, False, False, 0 )

        showSatellitesAsSubmenuCheckbox = Gtk.CheckButton( _( "Satellites" ) )
        showSatellitesAsSubmenuCheckbox.set_active( self.showSatellitesAsSubMenu )
        showSatellitesAsSubmenuCheckbox.set_tooltip_text( _( "Show satellites as submenus." ) )
        box.pack_start( showSatellitesAsSubmenuCheckbox, False, False, 0 )

        grid.attach( box, 0, 3, 1, 1 )

        hideBodyIfNeverUpCheckbox = Gtk.CheckButton( _( "Hide bodies which are 'never up'" ) )
        hideBodyIfNeverUpCheckbox.set_margin_top( 10 )
        hideBodyIfNeverUpCheckbox.set_active( self.hideBodyIfNeverUp )
        hideBodyIfNeverUpCheckbox.set_tooltip_text( _( 
            "If checked, only planets, moon,\n" + \
            "sun, comets and stars which\n" + \
            "rise/set or are 'always up'\n" + \
            "will be shown.\n\n" + \
            "Otherwise, all bodies are shown.\n" + \
            "When showing all bodies, there may\n" + \
            "be a lot of information displayed\n" + \
            "which could impact the indicator's\n" + \
            "performance." ) )
        grid.attach( hideBodyIfNeverUpCheckbox, 0, 4, 1, 1 )

        groupStarsByConstellationCheckbox = Gtk.CheckButton( _( "Group stars by constellation" ) )
        groupStarsByConstellationCheckbox.set_margin_top( 10 )
        groupStarsByConstellationCheckbox.set_active( self.groupStarsByConstellation )
        groupStarsByConstellationCheckbox.set_tooltip_text( _( 
            "By default, stars are listed\n" + \
            "alphabetically by name.\n\n" + \
            "When checked, stars will be\n" + \
            "grouped into their respective\n" + \
            "constellations and listed\n" + \
            "alphabetically by star name\n" + \
            "within each group." ) )
        grid.attach( groupStarsByConstellationCheckbox, 0, 5, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 6 ) # Bug in Python - must specify the parameter names!
        box.set_margin_top( 10 )

        label = Gtk.Label( _( "Hide comets greater than magnitude" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        spinnerCometMagnitude = Gtk.SpinButton()
        spinnerCometMagnitude.set_numeric( True )
        spinnerCometMagnitude.set_update_policy( Gtk.SpinButtonUpdatePolicy.IF_VALID )
        spinnerCometMagnitude.set_adjustment( Gtk.Adjustment( self.cometsMagnitude, -30, 30, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerCometMagnitude.set_value( self.cometsMagnitude ) # ...so need to force the initial value by explicitly setting it.
        spinnerCometMagnitude.set_tooltip_text( _( 
            "Comets with a magnitude greater\n" + \
            "than that specified are hidden.\n\n" + \
            "If a high magnitude value is set,\n" + \
            "there may be a lot of information\n" + \
            "displayed impacting the indicator's\n" + \
            "performance." ) )

        box.pack_start( spinnerCometMagnitude, False, False, 0 )

        grid.attach( box, 0, 6, 1, 1 )

        cometsAddNewCheckbox = Gtk.CheckButton( _( "Automatically add new comets" ) )
        cometsAddNewCheckbox.set_margin_top( 10 )
        cometsAddNewCheckbox.set_active( self.cometsAddNew )
        cometsAddNewCheckbox.set_tooltip_text( _(
            "If checked, new comets in the\n" + \
            "downloaded data will be added\n" + \
            "to the list of checked comets.\n\n" + \
            "In addition, any comets\n" + \
            "unchecked will become checked." ) )
        grid.attach( cometsAddNewCheckbox, 0, 7, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 6 ) # Bug in Python - must specify the parameter names!
        box.set_margin_top( 10 )

        sortSatellitesByDateTimeCheckbox = Gtk.CheckButton( _( "Sort satellites by rise date/time" ) )
        sortSatellitesByDateTimeCheckbox.set_margin_top( 10 )
        sortSatellitesByDateTimeCheckbox.set_active( self.satellitesSortByDateTime )
        sortSatellitesByDateTimeCheckbox.set_tooltip_text( _(
            "If checked, satellites will be\n" + \
            "sorted by rise date/time.\n\n" + \
            "Otherwise, satellites are sorted\n" + \
            "alphabetically by Name, Number\n" + \
            "and then International Designator." ) )
        grid.attach( sortSatellitesByDateTimeCheckbox, 0, 8, 1, 1 )

        hideSatelliteIfNoVisiblePassCheckbox = Gtk.CheckButton( _( "Hide satellites which have no upcoming visible pass" ) )
        hideSatelliteIfNoVisiblePassCheckbox.set_margin_top( 10 )
        hideSatelliteIfNoVisiblePassCheckbox.set_active( self.hideSatelliteIfNoVisiblePass )
        hideSatelliteIfNoVisiblePassCheckbox.set_tooltip_text( _( 
            "If checked, only satellites with an\n" + \
            "upcoming visible pass are displayed.\n\n" + \
            "Otherwise, all passes, visible or\n" + \
            "not, are shown (including error\n" + \
            "messages).\n\n" + \
            "If non-visible passes are shown,\n" + \
            "there may be a lot of information\n" + \
            "displayed impacting the indicator's\n" + \
            "performance." ) )

        grid.attach( hideSatelliteIfNoVisiblePassCheckbox, 0, 9, 1, 1 )

        satellitesAddNewCheckbox = Gtk.CheckButton( _( "Automatically add new satellites" ) )
        satellitesAddNewCheckbox.set_margin_top( 10 )
        satellitesAddNewCheckbox.set_active( self.satellitesAddNew )
        satellitesAddNewCheckbox.set_tooltip_text( _( 
            "If checked, new satellites in the\n" + \
            "downloaded data will be added to\n" + \
            "the list of checked satellites.\n\n" + \
            "In addition, any satellites which\n" + \
            "are currently unchecked will\n" + \
            "become checked." ) )
        grid.attach( satellitesAddNewCheckbox, 0, 10, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Menu" ) ) )

        # Planets/Stars.
        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 15 ) # Bug in Python - must specify the parameter names!

        planetStore = Gtk.ListStore( bool, str, str ) # Show/hide, planet name (not displayed), translated planet name.
        for planetName in IndicatorLunar.PLANETS:
            planetStore.append( [ planetName in self.planets, planetName, IndicatorLunar.PLANET_AND_MOON_NAMES_TRANSLATIONS[ planetName ] ] )

        tree = Gtk.TreeView( planetStore )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( _( 
            "Check a planet (or dwarf planet)\n" + \
            "to display in the menu.\n\n" + \
            "Clicking the header of the first\n" + \
            "column toggles all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onPlanetToggled, planetStore )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, planetStore, None, displayTagsStore, AstronomicalBodyType.Planet )
        tree.append_column( treeViewColumn )

        tree.append_column( Gtk.TreeViewColumn( _( "Planet" ), Gtk.CellRendererText(), text = 2 ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER )
        scrolledWindow.add( tree )

        box.pack_start( scrolledWindow, True, True, 0 )

        stars = [ ] # List of lists, each sublist containing star is checked flag, star name, star translated name, constellation translated name.
        for starName in IndicatorLunar.STAR_NAMES_TRANSLATIONS.keys():
            starTranslated = IndicatorLunar.STAR_NAMES_TRANSLATIONS[ starName ]
            constellation = [ k for k, v in IndicatorLunar.STARS_BY_CONSTELLATION.items() if starName in v ][ 0 ]
            constellationTranslated = IndicatorLunar.CONSTELLATIONS_TRANSLATIONS[ constellation ]
            stars.append( [ starName in self.stars, starName, starTranslated, constellationTranslated ] )

        stars = sorted( stars, key = lambda x: ( x[ 2 ] ) )
        starStore = Gtk.ListStore( bool, str, str, str ) # Show/hide, star name (not displayed), translated star name, constellation translated name.
        for star in stars:
            starStore.append( star )

        starStoreSort = Gtk.TreeModelSort( model = starStore )
        starStoreSort.set_sort_column_id( 2, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( starStoreSort )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( _( 
            "Check a star to display in the menu.\n\n" + \
            "Clicking the header of the first\n" + \
            "column toggles all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, starStore, starStoreSort, AstronomicalBodyType.Star )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, starStore, starStoreSort, displayTagsStore, AstronomicalBodyType.Star )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Star" ), Gtk.CellRendererText(), text = 2 )
        treeViewColumn.set_sort_column_id( 2 )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Constellation" ), Gtk.CellRendererText(), text = 3 )
        treeViewColumn.set_sort_column_id( 3 )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        box.pack_start( scrolledWindow, True, True, 0 )

        notebook.append_page( box, Gtk.Label( _( "Planets / Stars" ) ) )

        # Comets.
        cometGrid = Gtk.Grid()
        cometGrid.set_row_spacing( 10 )
        cometGrid.set_margin_bottom( 10 )

        cometStore = Gtk.ListStore( bool, str ) # Show/hide, comet name.
        cometStoreSort = Gtk.TreeModelSort( model = cometStore )
        cometStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( cometStoreSort )
        tree.set_tooltip_text( _(
            "Check a comet to display\n" + \
            "in the menu.\n\n" + \
            "Clicking the header of\n" + \
            "the first column toggles\n" + \
            "all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, cometStore, cometStoreSort, AstronomicalBodyType.Comet )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, cometStore, cometStoreSort, displayTagsStore, AstronomicalBodyType.Comet )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = 1 )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( tree )
        cometGrid.attach( scrolledWindow, 0, 0, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL, spacing = 6 ) # Bug in Python - must specify the parameter names!
        box.set_margin_top( 10 )
        box.set_margin_left( 10 )
        box.set_margin_right( 10 )

        label = Gtk.Label( _( "Comet OE data" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        self.cometOEDataNew = None
        self.cometOEURLNew = None

        cometURLEntry = Gtk.Entry()
        cometURLEntry.set_text( self.cometOEURL )
        cometURLEntry.set_hexpand( True )
        cometURLEntry.set_tooltip_text( _(
            "The URL from which to source\n" + \
            "comet OE data. For a local\n" + \
            "file, use 'file:///' and the\n" + \
            "filename.\n\n" + \
            "If you change the URL, you must\n" + \
            "fetch the new data.\n\n" + \
            "To disable, set a bogus URL such\n" + \
            "as 'http://'." ) )
        box.pack_start( cometURLEntry, True, True, 0 )

        fetch = Gtk.Button( _( "Fetch" ) )
        fetch.set_tooltip_text( _(
            "Retrieve the comet OE data from\n" + \
            "the URL. If the URL is empty,\n" + \
            "the default URL will be used.\n\n" + \
            "If using the default URL, the\n" + \
            "download may be blocked to avoid\n" + \
            "burdening the data source." ) )
        fetch.connect( "clicked",
                       self.onFetchCometSatelliteData,
                       cometURLEntry,
                       cometGrid,
                       cometStore,
                       AstronomicalBodyType.Comet,
                       IndicatorLunar.COMET_OE_URL,
                       IndicatorLunar.COMET_OE_CACHE_BASENAME,
                       IndicatorLunar.COMET_OE_CACHE_MAXIMUM_AGE_HOURS,
                       self.lastUpdateCometOE,
                       IndicatorLunar.COMET_OE_DOWNLOAD_PERIOD_HOURS,
                       _( "Comet data fetch aborted" ),
                       _( "To avoid taxing the data source, the download was aborted. The next time the download will occur will be at {0}." ),
                       self.getCometOEData )
        box.pack_start( fetch, False, False, 0 )

        cometGrid.attach( box, 0, 1, 1, 1 )

        label = Gtk.Label()
        label.set_margin_left( 10 )
        label.set_margin_right( 10 )
        label.set_justify( Gtk.Justification.CENTER )
        
        cometGrid.attach( label, 0, 2, 1, 1 )

        notebook.append_page( cometGrid, Gtk.Label( _( "Comets" ) ) )

        # Satellites.
        satelliteGrid = Gtk.Grid()
        satelliteGrid.set_row_spacing( 10 )
        satelliteGrid.set_margin_bottom( 10 )

        satelliteStore = Gtk.ListStore( bool, str, str, str ) # Show/hide, name, number, international designator.
        satelliteStoreSort = Gtk.TreeModelSort( model = satelliteStore )
        satelliteStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( satelliteStoreSort )
        tree.set_tooltip_text( _( 
            "Check a satellite to display in\n" + \
            "the menu.\n\n" + \
            "Clicking the header of the first\n" + \
            "column toggles all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, satelliteStore, satelliteStoreSort, AstronomicalBodyType.Satellite )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, satelliteStore, satelliteStoreSort, displayTagsStore, AstronomicalBodyType.Satellite )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = 1 )
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

        self.satelliteTLEDataNew = None
        self.satelliteTLEURLNew = None

        TLEURLEntry = Gtk.Entry()
        TLEURLEntry.set_text( self.satelliteTLEURL )
        TLEURLEntry.set_hexpand( True )
        TLEURLEntry.set_tooltip_text( _( 
            "The URL from which to source the\n" + \
            "satellite TLE data.\n" + \
            "For a local file, use 'file:///'\n" + \
            "and the filename.\n\n" + \
            "If you change the URL, you must\n" + \
            "fetch the new data.\n\n" + \
            "To disable, set a bogus URL such\n" + \
            "as 'http://'" ) )
        box.pack_start( TLEURLEntry, True, True, 0 )

        fetch = Gtk.Button( _( "Fetch" ) )
        fetch.set_tooltip_text( _(
            "Retrieve the satellite TLE data\n" + \
            "from the URL.\n" + \
            "If the URL is empty, the default\n" + \
            "URL will be used.\n\n" + \
            "If using the default URL, the\n" + \
            "download may be\n" + \
            "blocked to avoid burdening the\n" + \
            "data source." ) )
        fetch.connect( "clicked",
                       self.onFetchCometSatelliteData,
                       TLEURLEntry,
                       satelliteGrid,
                       satelliteStore,
                       AstronomicalBodyType.Satellite,
                       IndicatorLunar.SATELLITE_TLE_URL,
                       IndicatorLunar.SATELLITE_TLE_CACHE_BASENAME,
                       IndicatorLunar.SATELLITE_TLE_CACHE_MAXIMUM_AGE_HOURS,
                       self.lastUpdateSatelliteTLE,
                       IndicatorLunar.SATELLITE_TLE_DOWNLOAD_PERIOD_HOURS,
                       _( "Satellite TLE data fetch aborted" ),
                       _( "To avoid taxing the data source, the download was aborted. The next time the download will occur will be at {0}." ),
                       self.getSatelliteTLEData )

        box.pack_start( fetch, False, False, 0 )

        satelliteGrid.attach( box, 0, 1, 1, 1 )

        label = Gtk.Label()
        label.set_margin_left( 10 )
        label.set_margin_right( 10 )
        label.set_justify( Gtk.Justification.CENTER )
        
        satelliteGrid.attach( label, 0, 2, 1, 1 )

        notebook.append_page( satelliteGrid, Gtk.Label( _( "Satellites" ) ) )

        # OSD (satellite and full moon).
        notifyOSDInformation = _( "For formatting, refer to https://wiki.ubuntu.com/NotifyOSD" )

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
        satelliteNotificationSummaryText.set_text( self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, True, self.satelliteNotificationSummary ) )
        satelliteNotificationSummaryText.set_tooltip_text( _(
            "The summary for the satellite rise\n" + \
            "notification. Available tags:\n\t" ) + \
            IndicatorLunar.SATELLITE_TAG_NAME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NUMBER_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_VISIBLE_TRANSLATION + "\n\n" + \
            _( notifyOSDInformation ) )

        grid.attach( satelliteNotificationSummaryText, 1, 1, 1, 1 )

        showSatelliteNotificationCheckbox.connect( "toggled", pythonutils.onCheckbox, label, satelliteNotificationSummaryText )

        label = Gtk.Label( _( "Message" ) )
        label.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        label.set_halign( Gtk.Align.START )
        label.set_margin_left( 25 )
        label.set_valign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        satelliteNotificationMessageText = Gtk.TextView()
        satelliteNotificationMessageText.get_buffer().set_text( self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, True, self.satelliteNotificationMessage ) )
        satelliteNotificationMessageText.set_tooltip_text( _(
            "The message for the satellite rise\n" + \
            "notification. Available tags:\n\t" ) + \
            IndicatorLunar.SATELLITE_TAG_NAME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NUMBER_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_VISIBLE_TRANSLATION + "\n\n" + \
            _( notifyOSDInformation ) )

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
        test.connect( "clicked", self.onTestNotificationClicked, satelliteNotificationSummaryText, satelliteNotificationMessageText, False )
        test.set_tooltip_text( _(
            "Show the notification bubble.\n" + \
            "Tags will be substituted with\n" + \
            "mock text." ) )
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
        werewolfNotificationSummaryText.set_tooltip_text( _( "The summary for the werewolf notification.\n\n" ) + notifyOSDInformation )
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
        werewolfNotificationMessageText.set_tooltip_text( _( "The message for the werewolf notification.\n\n" ) + notifyOSDInformation )
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
        test.connect( "clicked", self.onTestNotificationClicked, werewolfNotificationSummaryText, werewolfNotificationMessageText, True )
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
            "Choose a city from the list.\n" + \
            "Or, add in your own city name." ) )
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
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorLunar.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 4, 2, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        dialog = Gtk.Dialog( _( "Preferences" ), None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorLunar.ICON )
        dialog.show_all()

        # The visibility of some GUI objects must be determined AFTER the dialog is shown.
        self.updateCometSatellitePreferencesTab( cometGrid, cometStore, self.cometOEData, self.comets, cometURLEntry.get_text().strip(), AstronomicalBodyType.Comet )
        self.updateCometSatellitePreferencesTab( satelliteGrid, satelliteStore, self.satelliteTLEData, self.satellites, TLEURLEntry.get_text().strip(), AstronomicalBodyType.Satellite )

        # Last thing to do after everything else is built.
        notebook.connect( "switch-page", self.onSwitchPage, displayTagsStore )

        while True:
            if dialog.run() != Gtk.ResponseType.OK:
                break

            cityValue = city.get_active_text()
            if cityValue == "":
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "City cannot be empty." ), INDICATOR_NAME )
                notebook.set_current_page( TAB_GENERAL )
                city.grab_focus()
                continue

            latitudeValue = latitude.get_text().strip()
            if latitudeValue == "" or not pythonutils.isNumber( latitudeValue ) or float( latitudeValue ) > 90 or float( latitudeValue ) < -90:
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "Latitude must be a number between 90 and -90 inclusive." ), INDICATOR_NAME )
                notebook.set_current_page( TAB_GENERAL )
                latitude.grab_focus()
                continue

            longitudeValue = longitude.get_text().strip()
            if longitudeValue == "" or not pythonutils.isNumber( longitudeValue ) or float( longitudeValue ) > 180 or float( longitudeValue ) < -180:
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "Longitude must be a number between 180 and -180 inclusive." ), INDICATOR_NAME )
                notebook.set_current_page( TAB_GENERAL )
                longitude.grab_focus()
                continue

            elevationValue = elevation.get_text().strip()
            if elevationValue == "" or not pythonutils.isNumber( elevationValue ) or float( elevationValue ) > 10000 or float( elevationValue ) < 0:
                pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "Elevation must be a number between 0 and 10000 inclusive." ), INDICATOR_NAME )
                notebook.set_current_page( TAB_GENERAL )
                elevation.grab_focus()
                continue

            self.indicatorText = self.translateTags( displayTagsStore, False, indicatorText.get_text().strip() )
            self.showMoon = showMoonCheckbox.get_active()
            self.showSun = showSunCheckbox.get_active()
            self.showPlanetsAsSubMenu = showPlanetsAsSubmenuCheckbox.get_active()
            self.showStarsAsSubMenu = showStarsAsSubmenuCheckbox.get_active()
            self.showCometsAsSubMenu = showCometsAsSubmenuCheckbox.get_active()
            self.showSatellitesAsSubMenu = showSatellitesAsSubmenuCheckbox.get_active()
            self.hideBodyIfNeverUp = hideBodyIfNeverUpCheckbox.get_active()
            self.groupStarsByConstellation = groupStarsByConstellationCheckbox.get_active()
            self.cometsMagnitude = spinnerCometMagnitude.get_value_as_int()
            self.cometsAddNew = cometsAddNewCheckbox.get_active()
            self.satellitesSortByDateTime = sortSatellitesByDateTimeCheckbox.get_active()
            self.hideSatelliteIfNoVisiblePass = hideSatelliteIfNoVisiblePassCheckbox.get_active()
            self.satellitesAddNew = satellitesAddNewCheckbox.get_active()

            self.planets = [ ]
            for row in planetStore:
                if row[ 0 ]:
                    self.planets.append( row[ 1 ] )

            self.stars = [ ]
            for row in starStore:
                if row[ 0 ]:
                    self.stars.append( row[ 1 ] )

            if self.cometOEURLNew is not None: # The URL is initialsed to None.  If it is not None, a fetch has taken place.
                self.cometOEURL = self.cometOEURLNew # The URL may or may not be valid, but it will not be None.
                if self.cometOEDataNew is None:
                    self.cometOEData = { } # The retrieved data was bad, so reset to empty data.
                else:
                    self.cometOEData = self.cometOEDataNew # The retrieved data is good (but still could be empty).

                self.writeToCache( self.cometOEData, IndicatorLunar.COMET_OE_CACHE_BASENAME )
                self.lastUpdateCometOE = datetime.datetime.utcnow()

            self.comets = [ ]
            if self.cometsAddNew:
                self.addNewComets()
            else:
                for comet in cometStore:
                    if comet[ 0 ]:
                        self.comets.append( comet[ 1 ].upper() )

            if self.satelliteTLEURLNew is not None: # The URL is initialsed to None.  If it is not None, a fetch has taken place.
                self.satelliteTLEURL = self.satelliteTLEURLNew # The URL may or may not be valie, but it will not be None.
                if self.satelliteTLEDataNew is None:
                    self.satelliteTLEData = { } # The retrieved data was bad, so reset to empty data.
                else:
                    self.satelliteTLEData = self.satelliteTLEDataNew # The retrieved data is good (but still could be empty).

                self.writeToCache( self.satelliteTLEData, IndicatorLunar.SATELLITE_TLE_CACHE_BASENAME )
                self.lastUpdateSatelliteTLE = datetime.datetime.utcnow()

            self.satellites = [ ]
            if self.satellitesAddNew:
                self.addNewSatellites()
            else:
                for satellite in satelliteStore:
                    if satellite[ 0 ]:
                        self.satellites.append( ( satellite[ 1 ].upper(), satellite[ 2 ] ) )

            self.showSatelliteNotification = showSatelliteNotificationCheckbox.get_active()
            self.satelliteNotificationSummary = self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, False, satelliteNotificationSummaryText.get_text() )
            self.satelliteNotificationMessage = self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, False, pythonutils.getTextViewText( satelliteNotificationMessageText ) )

            self.showWerewolfWarning = showWerewolfWarningCheckbox.get_active()
            self.werewolfWarningStartIlluminationPercentage = spinner.get_value_as_int()
            self.werewolfWarningSummary = werewolfNotificationSummaryText.get_text()
            self.werewolfWarningMessage = pythonutils.getTextViewText( werewolfNotificationMessageText )

            self.cityName = cityValue
            _city_data[ self.cityName ] = ( str( latitudeValue ), str( longitudeValue ), float( elevationValue ) )

            self.saveSettings()
            pythonutils.setAutoStart( IndicatorLunar.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            break

        self.lock.release()
        self.update() #TODO Why do the update even when cancel?  If decide to only update on OK, need to call update after the lock is released.
        pythonutils.setAllMenuItemsSensitive( self.menu, True )


    def appendToDisplayTagsStore( self, key, value, displayTagsStore ):
        astronomicalBodyType = key[ 0 ]
        bodyTag = key[ 1 ]
        dataTag = key[ 2 ]

        isCometOrSatellite = \
            astronomicalBodyType is not None and \
            ( astronomicalBodyType == AstronomicalBodyType.Comet or astronomicalBodyType == AstronomicalBodyType.Satellite )

        if isCometOrSatellite:
            translatedTag = bodyTag + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ] # Don't translate the names of the comets/satellites.
        else:
            translatedTag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ bodyTag  ] + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ] # Translate names of planets/starts, etc.

        displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, value ] )


    def translateTags( self, tagsStore, originalToLocal, text ):
        # The tags store contains at least 2 columns (if more, those columns are ignored).
        # First column contains the original/untranslated tags.
        # Second column contains the translated tags.
        # Depending on the direction the translation, one of the columns contains the source tags to match.
        if originalToLocal:
            i = 0
            j = 1
        else:
            i = 1
            j = 0

        translatedText = text
        tags = re.findall( "\[([^\[^\]]+)\]", translatedText )
        for tag in tags:
            iter = tagsStore.get_iter_first()
            while iter is not None:
                row = tagsStore[ iter ]
                if row[ i ] == tag:
                    translatedText = translatedText.replace( "[" + tag + "]", "[" + row[ j ] + "]" )
                    iter = None # Break and move on to next tag.
                else:
                    iter = tagsStore.iter_next( iter )

        return translatedText


    def onTagDoubleClick( self, tree, rowNumber, treeViewColumn, translatedTagColumnIndex, indicatorTextEntry ):
        model, treeiter = tree.get_selection().get_selected()
        indicatorTextEntry.insert_text( "[" + model[ treeiter ][ translatedTagColumnIndex ] + "]", indicatorTextEntry.get_position() )


    def onMoonSunToggled( self, widget, moonSunTag, astronomicalBodyType ): self.checkboxToggled( moonSunTag, astronomicalBodyType, widget.get_active() )


    def onPlanetToggled( self, widget, row, dataStore ):
        dataStore[ row ][ 0 ] = not dataStore[ row ][ 0 ]
        self.checkboxToggled( dataStore[ row ][ 1 ].upper(), AstronomicalBodyType.Planet, dataStore[ row ][ 0 ] )
        planetName = dataStore[ row ][ 1 ]
        if planetName in IndicatorLunar.PLANET_MOONS:
            for moonName in IndicatorLunar.PLANET_MOONS[ planetName ]:
                self.checkboxToggled( moonName.upper(), AstronomicalBodyType.PlanetaryMoon, dataStore[ row ][ 0 ] )


    def onCometStarSatelliteToggled( self, widget, row, dataStore, sortStore, astronomicalBodyType ):
        actualRow = sortStore.convert_path_to_child_path( Gtk.TreePath.new_from_string( row ) ) # Convert sorted model index to underlying (child) model index.
        dataStore[ actualRow ][ 0 ] = not dataStore[ actualRow ][ 0 ]
        if astronomicalBodyType == AstronomicalBodyType.Comet:
            bodyTag = dataStore[ actualRow ][ 1 ].upper()
        if astronomicalBodyType == AstronomicalBodyType.Satellite:
            bodyTag = dataStore[ actualRow ][ 1 ] + " " + dataStore[ actualRow ][ 2 ]
        else: # Assume star.
            bodyTag = dataStore[ actualRow ][ 1 ].upper()

        self.checkboxToggled( bodyTag, astronomicalBodyType, dataStore[ actualRow ][ 0 ] )


    def updateCometSatellitePreferencesTab( self, grid, dataStore, data, bodies, url, astronomicalBodyType ):
        dataStore.clear()
        if data is None:
            message = IndicatorLunar.MESSAGE_DATA_CANNOT_ACCESS_DATA_SOURCE.format( url )
        elif len( data ) == 0:
            message = IndicatorLunar.MESSAGE_DATA_NO_DATA_FOUND_AT_SOURCE.format( url )
        else:
            message = None
            if astronomicalBodyType == AstronomicalBodyType.Satellite:
                for key in data:
                    tle = data[ key ]
                    checked = ( tle.getName().upper(), tle.getNumber() ) in bodies
                    dataStore.append( [ checked, tle.getName(), tle.getNumber(), tle.getInternationalDesignator() ] )
            else:
                for key in data:
                    oe = data[ key ]
                    dataStore.append( [ key in bodies, self.getCometDisplayName( oe ) ] )

        # Hide/show the label and scrolled window as appropriate.
        # Ideally grid.get_child_at() should be used to get the Label and ScrolledWindow...but this does not work on Ubuntu 12.04.
        for child in grid.get_children():
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


    def onFetchCometSatelliteData( self,
                                   button, entry, grid, store, 
                                   astronomicalBodyType, 
                                   dataURL, 
                                   cacheBasename, cacheMaximumAgeHours, lastUpdate, downloadPeriodHours, 
                                   summary, message, 
                                   getDataFunction ):
        # Flush comet/satellite data.
        for key in list( self.data ): # Gets the keys and allows iteration with removal.
            if key[ 0 ] == astronomicalBodyType:
                self.data.pop( key )

        for key in list( self.tagsAdded ):
            if key[ 0 ] == astronomicalBodyType:
                self.tagsAdded.pop( t, None )

        for key in list( self.tagsRemoved ):
            if key[ 0 ] == astronomicalBodyType:
                self.tagsRemoved.pop( t, None )

        if entry.get_text().strip() == "":
            entry.set_text( dataURL )

        urlNew = entry.get_text().strip()

        # If the URL is the default, use the cache to avoid annoying the default data source.
        if urlNew == dataURL:
            dataNew, cacheDateTime = self.readFromCache( cacheBasename, datetime.datetime.now() - datetime.timedelta( hours = cacheMaximumAgeHours ) ) # Returned data is either None or non-empty.
            if dataNew is None:
                # No cache data (either too old or just not there), so download only if it won't exceed the download time limit.
                if datetime.datetime.utcnow() < ( lastUpdate + datetime.timedelta( hours = downloadPeriodHours ) ):
                    nextDownload = str( lastUpdate + datetime.timedelta( hours = downloadPeriodHours ) )
                    Notify.Notification.new( summary, message.format( nextDownload[ 0 : nextDownload.index( "." ) ] ), IndicatorLunar.ICON ).show()
                else:
                    dataNew = getDataFunction( urlNew ) # The comet/satellite data can be None, empty or non-empty.
        else:
            dataNew = getDataFunction( urlNew ) # The comet/satellite data can be None, empty or non-empty.

        self.updateCometSatellitePreferencesTab( grid, store, dataNew, [ ], urlNew, astronomicalBodyType )

        # Assign back to original bodies...
        if astronomicalBodyType == AstronomicalBodyType.Comet:
            self.cometOEURLNew = urlNew
            self.cometOEDataNew = dataNew
        else: # Assume it's a satellite.
            self.satelliteTLEURLNew = urlNew
            self.satelliteTLEDataNew = dataNew


    def checkboxToggled( self, bodyTag, astronomicalBodyType, checked ):
        # Maintain a record of bodies which are checked and unchecked by the user.
        # This allows the update of the table in the first tab to happen quickly, rather than doing a slow update on a per-check basis.
        # Use hashtables (dicts) to maintain the record of checked and unchecked bodies - no need to store a value, so None is used.
        # Pass in None when doing a pop as it is possible was already checked.
        t = ( astronomicalBodyType, bodyTag )
        if checked:
            self.tagsRemoved.pop( t, None )
            self.tagsAdded[ t ] = None
        else:
            self.tagsRemoved[ t ] = None
            self.tagsAdded.pop( t, None )


    def onColumnHeaderClick( self, widget, dataStore, sortStore, displayTagsStore, astronomicalBodyType ):
        if astronomicalBodyType == AstronomicalBodyType.Planet:
            toggle = self.togglePlanetsTable
            self.togglePlanetsTable = not self.togglePlanetsTable
            for row in range( len( dataStore ) ):
                dataStore[ row ][ 0 ] = bool( not toggle )
                self.onPlanetToggled( widget, row, dataStore )

        elif astronomicalBodyType == AstronomicalBodyType.Comet or \
             astronomicalBodyType == AstronomicalBodyType.Satellite or \
             astronomicalBodyType == AstronomicalBodyType.Star:
            if astronomicalBodyType == AstronomicalBodyType.Comet:
                toggle = self.toggleCometsTable
                self.toggleCometsTable = not self.toggleCometsTable
            elif astronomicalBodyType == AstronomicalBodyType.Satellite:
                toggle = self.toggleSatellitesTable
                self.toggleSatellitesTable = not self.toggleSatellitesTable
            else:
                toggle = self.toggleStarsTable
                self.toggleStarsTable = not self.toggleStarsTable

            for row in range( len( dataStore ) ):
                dataStore[ row ][ 0 ] = bool( not toggle )
                row = str( sortStore.convert_child_path_to_path( Gtk.TreePath.new_from_string( str( row ) ) ) ) # Need to convert the data store row to the sort store row.
                self.onCometStarSatelliteToggled( widget, row, dataStore, sortStore, astronomicalBodyType )


    def onTestNotificationClicked( self, button, summaryEntry, messageTextView, isFullMoon ):
        summary = summaryEntry.get_text()
        message = pythonutils.getTextViewText( messageTextView )

        if isFullMoon:
            svgFile = IndicatorLunar.SVG_FULL_MOON_FILE
            self.createIcon( 100, None, svgFile )
        else:
            svgFile = IndicatorLunar.SVG_SATELLITE_ICON
            utcNow = str( datetime.datetime.utcnow() )
            utcNowPlusTenMinutes = str( datetime.datetime.utcnow() + datetime.timedelta( minutes = 10 ) )

            # Mock data...
            summary = summary. \
                replace( IndicatorLunar.SATELLITE_TAG_NAME_TRANSLATION, "ISS (ZARYA)" ). \
                replace( IndicatorLunar.SATELLITE_TAG_NUMBER_TRANSLATION, "25544" ). \
                replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION, "1998-067A" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION, "123°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.getLocalDateTime( utcNow, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION, self.getLocalDateTime( utcNowPlusTenMinutes, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_VISIBLE_TRANSLATION, IndicatorLunar.TRUE_TEXT_TRANSLATION )

            message = message. \
                replace( IndicatorLunar.SATELLITE_TAG_NAME_TRANSLATION, "ISS (ZARYA)" ). \
                replace( IndicatorLunar.SATELLITE_TAG_NUMBER_TRANSLATION, "25544" ). \
                replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION, "1998-067A" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION, "123°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.getLocalDateTime( utcNow, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION, self.getLocalDateTime( utcNowPlusTenMinutes, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_VISIBLE_TRANSLATION, IndicatorLunar.TRUE_TEXT_TRANSLATION )

        if summary == "":
            summary = " " # The notification summary text must not be empty (at least on Unity).

        Notify.Notification.new( summary, message, svgFile ).show()

        if isFullMoon:
            os.remove( svgFile )


    def onCityChanged( self, combobox, latitude, longitude, elevation ):
        city = combobox.get_active_text()
        global _city_data
        if city != "" and city in _city_data:
            latitude.set_text( _city_data.get( city )[ 0 ] )
            longitude.set_text( _city_data.get( city )[ 1 ] )
            elevation.set_text( str( _city_data.get( city )[ 2 ] ) )


    def onSwitchPage( self, notebook, page, pageNumber, displayTagsStore ):
        if pageNumber == 0: # User has clicked the first tab.
            displayTagsStore.clear() # List of lists, each sublist contains the tag, translated tag, value.

            # Only add tags for data which has not been removed.
            for key in self.data.keys():
                hideMessage = self.data[ key ] == IndicatorLunar.MESSAGE_BODY_NEVER_UP or \
                          self.data[ key ] == IndicatorLunar.MESSAGE_DATA_BAD_DATA or \
                          self.data[ key ] == IndicatorLunar.MESSAGE_DATA_NO_DATA or \
                          self.data[ key ] == IndicatorLunar.MESSAGE_SATELLITE_NEVER_RISES or \
                          self.data[ key ] == IndicatorLunar.MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME or \
                          self.data[ key ] == IndicatorLunar.MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS or \
                          self.data[ key ] == IndicatorLunar.MESSAGE_SATELLITE_VALUE_ERROR

                hideBody = self.hideBodyIfNeverUp or self.hideSatelliteIfNoVisiblePass

                if hideMessage and hideBody:
                    continue

                astronomicalBodyType = key[ 0 ]
                bodyTag = key[ 1 ]

                if ( astronomicalBodyType, bodyTag ) not in self.tagsRemoved and \
                   ( astronomicalBodyType, bodyTag ) not in self.tagsAdded:
                    self.appendToDisplayTagsStore( key, self.getDisplayData( key ), displayTagsStore )

            # Add tags for newly checked items (duplicates have been avoided by the above code).
            for key in self.tagsAdded:
                astronomicalBodyType = key[ 0 ]
                bodyTag = key[ 1 ]
                if astronomicalBodyType == AstronomicalBodyType.Comet:
                    tags = IndicatorLunar.DATA_TAGS_COMET
                elif astronomicalBodyType == AstronomicalBodyType.Moon:
                    tags = IndicatorLunar.DATA_TAGS_MOON
                elif astronomicalBodyType == AstronomicalBodyType.Planet:
                    tags = IndicatorLunar.DATA_TAGS_PLANET
                    if bodyTag == IndicatorLunar.PLANET_SATURN.upper():
                        tags.append( IndicatorLunar.DATA_EARTH_TILT )
                        tags.append( IndicatorLunar.DATA_SUN_TILT )
                elif astronomicalBodyType == AstronomicalBodyType.PlanetaryMoon:
                    tags = IndicatorLunar.DATA_TAGS_PLANETARY_MOON
                elif astronomicalBodyType == AstronomicalBodyType.Satellite:
                    tags = IndicatorLunar.DATA_TAGS_SATELLITE
                elif astronomicalBodyType == AstronomicalBodyType.Star:
                    tags = IndicatorLunar.DATA_TAGS_STAR
                elif astronomicalBodyType == AstronomicalBodyType.Sun:
                    tags = IndicatorLunar.DATA_TAGS_SUN

                for tag in tags:
                    self.appendToDisplayTagsStore( key + ( tag, ), IndicatorLunar.DISPLAY_NEEDS_REFRESH, displayTagsStore )


    def addNewSatellites( self ):
        for key in self.satelliteTLEData:
            if key not in self.satellites:
                self.satellites.append( key )


    def addNewComets( self ):
        for key in self.cometOEData:
            if key not in self.comets:
                self.comets.append( key )


    def getCometDisplayName( self, comet ): return comet[ 0 : comet.index( "," ) ]


    # Returns a dict/hashtable of the comets (comets) data from the specified URL (may be empty).
    # Key: comet name, upper cased ; Value: entire comet string.
    # On error, returns None.
    def getCometOEData( self, url ):
        try:
            # Comets are read from a URL which assumes the XEphem format.
            # For example
            #
            #    C/2002 Y1 (Juels-Holvorcem),e,103.7816,166.2194,128.8232,242.5695,0.0002609,0.99705756,0.0000,04/13.2508/2003,2000,g  6.5,4.0
            #
            # from which the first field (up to the first ',') is the name.
            cometOEData = { }
            data = urlopen( url, timeout = IndicatorLunar.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
            for i in range( 0, len( data ) ):
                if not data[ i ].startswith( "#" ):
                    cometName = data[ i ][ 0 : data[ i ].index( "," ) ] 
                    cometOEData[ cometName.upper() ] = data[ i ]

        except Exception as e:
            cometOEData = None # Indicates error.
            logging.exception( e )
            logging.error( "Error retrieving comet OE data from " + str( url ) )

        return cometOEData


    # Returns a dict/hashtable of the satellite TLE data from the specified URL (may be empty).
    # Key: ( satellite name, satellite number ) ; Value: satellite.TLE object.
    # On error, returns None.
    def getSatelliteTLEData( self, url ):
        try:
            satelliteTLEData = { }
            data = urlopen( url, timeout = IndicatorLunar.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
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
            timezone = pythonutils.processGet( "cat /etc/timezone" )
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
        self.groupStarsByConstellation = False
        self.hideBodyIfNeverUp = True
        self.hideSatelliteIfNoVisiblePass = True
        self.indicatorText = IndicatorLunar.INDICATOR_TEXT_DEFAULT
        self.comets = [ ]
        self.cometsAddNew = False
        self.cometsMagnitude = 6 # More or less what's visible with the naked eye or binoculars.
        self.cometOEURL = IndicatorLunar.COMET_OE_URL

        self.planets = [ ]
        for planetName in IndicatorLunar.PLANETS:
            self.planets.append( planetName )

        self.satelliteNotificationMessage = IndicatorLunar.SATELLITE_NOTIFICATION_MESSAGE_DEFAULT
        self.satelliteNotificationSummary = IndicatorLunar.SATELLITE_NOTIFICATION_SUMMARY_DEFAULT
        self.satelliteTLEURL = IndicatorLunar.SATELLITE_TLE_URL
        self.satellites = [ ]
        self.satellitesAddNew = False
        self.satellitesSortByDateTime = True
        self.showMoon = True
        self.showCometsAsSubMenu = True
        self.showPlanetsAsSubMenu = False
        self.showSatelliteNotification = True
        self.showSatellitesAsSubMenu = True
        self.showStarsAsSubMenu = True
        self.showSun = True
        self.showWerewolfWarning = True
        self.stars = [ ]
        self.werewolfWarningStartIlluminationPercentage = 99
        self.werewolfWarningMessage = IndicatorLunar.WEREWOLF_WARNING_MESSAGE_DEFAULT
        self.werewolfWarningSummary = IndicatorLunar.WEREWOLF_WARNING_SUMMARY_DEFAULT

        if not os.path.isfile( IndicatorLunar.SETTINGS_FILE ):
            return

        try:
            with open( IndicatorLunar.SETTINGS_FILE, "r" ) as f:
                settings = json.load( f )

            global _city_data
            cityElevation = settings.get( IndicatorLunar.SETTINGS_CITY_ELEVATION, _city_data.get( self.cityName )[ 2 ] )
            cityLatitude = settings.get( IndicatorLunar.SETTINGS_CITY_LATITUDE, _city_data.get( self.cityName )[ 0 ] )
            cityLongitude = settings.get( IndicatorLunar.SETTINGS_CITY_LONGITUDE, _city_data.get( self.cityName )[ 1 ] )
            self.cityName = settings.get( IndicatorLunar.SETTINGS_CITY_NAME, self.cityName )
            _city_data[ self.cityName ] = ( str( cityLatitude ), str( cityLongitude ), float( cityElevation ) ) # Insert/overwrite the cityName and information into the cities.

            self.groupStarsByConstellation = settings.get( IndicatorLunar.SETTINGS_GROUP_STARS_BY_CONSTELLATION, self.groupStarsByConstellation )
            self.hideBodyIfNeverUp = settings.get( IndicatorLunar.SETTINGS_HIDE_BODY_IF_NEVER_UP, self.hideBodyIfNeverUp )
            self.hideSatelliteIfNoVisiblePass = settings.get( IndicatorLunar.SETTINGS_HIDE_SATELLITE_IF_NO_VISIBLE_PASS, self.hideSatelliteIfNoVisiblePass )
            self.indicatorText = settings.get( IndicatorLunar.SETTINGS_INDICATOR_TEXT, self.indicatorText )
            self.cometOEURL = settings.get( IndicatorLunar.SETTINGS_COMET_OE_URL, self.cometOEURL )
            self.comets = settings.get( IndicatorLunar.SETTINGS_COMETS, self.comets )
            self.cometsAddNew = settings.get( IndicatorLunar.SETTINGS_COMETS_ADD_NEW, self.cometsAddNew )
            self.cometsMagnitude = settings.get( IndicatorLunar.SETTINGS_COMETS_MAGNITUDE, self.cometsMagnitude )
            self.planets = settings.get( IndicatorLunar.SETTINGS_PLANETS, self.planets )
            self.satelliteNotificationMessage = settings.get( IndicatorLunar.SETTINGS_SATELLITE_NOTIFICATION_MESSAGE, self.satelliteNotificationMessage )
            self.satelliteNotificationSummary = settings.get( IndicatorLunar.SETTINGS_SATELLITE_NOTIFICATION_SUMMARY, self.satelliteNotificationSummary )
            self.satelliteTLEURL = settings.get( IndicatorLunar.SETTINGS_SATELLITE_TLE_URL, self.satelliteTLEURL )

            self.satellites = settings.get( IndicatorLunar.SETTINGS_SATELLITES, self.satellites )
            self.satellites = [ tuple( l ) for l in self.satellites ] # Converts from a list of lists to a list of tuples...go figure!

            self.satellitesAddNew = settings.get( IndicatorLunar.SETTINGS_SATELLITES_ADD_NEW, self.satellitesAddNew )
            self.satellitesSortByDateTime = settings.get( IndicatorLunar.SETTINGS_SATELLITES_SORT_BY_DATE_TIME, self.satellitesSortByDateTime )
            self.showMoon = settings.get( IndicatorLunar.SETTINGS_SHOW_MOON, self.showMoon )
            self.showCometsAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_COMETS_AS_SUBMENU, self.showCometsAsSubMenu )
            self.showPlanetsAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_PLANETS_AS_SUBMENU, self.showPlanetsAsSubMenu )
            self.showSatelliteNotification = settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITE_NOTIFICATION, self.showSatelliteNotification )
            self.showSatellitesAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITES_AS_SUBMENU, self.showSatellitesAsSubMenu )
            self.showStarsAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_STARS_AS_SUBMENU, self.showStarsAsSubMenu )
            self.showSun = settings.get( IndicatorLunar.SETTINGS_SHOW_SUN, self.showSun )
            self.showWerewolfWarning = settings.get( IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING, self.showWerewolfWarning )
            self.stars = settings.get( IndicatorLunar.SETTINGS_STARS, self.stars )
            self.werewolfWarningStartIlluminationPercentage = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE, self.werewolfWarningStartIlluminationPercentage )
            self.werewolfWarningMessage = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_MESSAGE, self.werewolfWarningMessage )
            self.werewolfWarningSummary = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_SUMMARY, self.werewolfWarningSummary )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error reading settings: " + IndicatorLunar.SETTINGS_FILE )


    def saveSettings( self ):
        if self.cometsAddNew:
            comets = [ ] 
        else:
            comets = self.comets # Only write out the list of comets if the user elects to not add new.

        if self.satellitesAddNew:
            satellites = [ ]
        else:
            satellites = self.satellites # Only write out the list of satellites if the user elects to not add new.

        try:
            settings = {
                IndicatorLunar.SETTINGS_CITY_ELEVATION: _city_data.get( self.cityName )[ 2 ],
                IndicatorLunar.SETTINGS_CITY_LATITUDE: _city_data.get( self.cityName )[ 0 ],
                IndicatorLunar.SETTINGS_CITY_LONGITUDE: _city_data.get( self.cityName )[ 1 ],
                IndicatorLunar.SETTINGS_CITY_NAME: self.cityName,
                IndicatorLunar.SETTINGS_GROUP_STARS_BY_CONSTELLATION: self.groupStarsByConstellation,
                IndicatorLunar.SETTINGS_HIDE_BODY_IF_NEVER_UP: self.hideBodyIfNeverUp,
                IndicatorLunar.SETTINGS_HIDE_SATELLITE_IF_NO_VISIBLE_PASS: self.hideSatelliteIfNoVisiblePass,
                IndicatorLunar.SETTINGS_INDICATOR_TEXT: self.indicatorText,
                IndicatorLunar.SETTINGS_COMET_OE_URL: self.cometOEURL,
                IndicatorLunar.SETTINGS_COMETS: comets,
                IndicatorLunar.SETTINGS_COMETS_ADD_NEW: self.cometsAddNew,
                IndicatorLunar.SETTINGS_COMETS_MAGNITUDE: self.cometsMagnitude,
                IndicatorLunar.SETTINGS_PLANETS: self.planets,
                IndicatorLunar.SETTINGS_SATELLITE_NOTIFICATION_MESSAGE: self.satelliteNotificationMessage,
                IndicatorLunar.SETTINGS_SATELLITE_NOTIFICATION_SUMMARY: self.satelliteNotificationSummary,
                IndicatorLunar.SETTINGS_SATELLITE_TLE_URL: self.satelliteTLEURL,
                IndicatorLunar.SETTINGS_SATELLITES: satellites,
                IndicatorLunar.SETTINGS_SATELLITES_ADD_NEW: self.satellitesAddNew,
                IndicatorLunar.SETTINGS_SATELLITES_SORT_BY_DATE_TIME: self.satellitesSortByDateTime,
                IndicatorLunar.SETTINGS_SHOW_MOON: self.showMoon,
                IndicatorLunar.SETTINGS_SHOW_COMETS_AS_SUBMENU: self.showCometsAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_PLANETS_AS_SUBMENU: self.showPlanetsAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_SATELLITE_NOTIFICATION: self.showSatelliteNotification,
                IndicatorLunar.SETTINGS_SHOW_SATELLITES_AS_SUBMENU: self.showSatellitesAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_STARS_AS_SUBMENU: self.showStarsAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_SUN: self.showSun,
                IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING: self.showWerewolfWarning,
                IndicatorLunar.SETTINGS_STARS: self.stars,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE: self.werewolfWarningStartIlluminationPercentage,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_MESSAGE: self.werewolfWarningMessage,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_SUMMARY: self.werewolfWarningSummary
            }

            with open( IndicatorLunar.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorLunar.SETTINGS_FILE )


    # Writes the data (dict) to the cache.
    def writeToCache( self, data, baseName ):
        filename = IndicatorLunar.CACHE_PATH + baseName + datetime.datetime.now().strftime( IndicatorLunar.DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
        try:
            with open( filename, "wb" ) as f:
                pickle.dump( data, f )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing to cache: " + filename )


    # Reads the most recent file from the cache for the given base name (tle or oe).
    # Removes out of date cache files.
    #
    # Returns a tuple of the data (either None or a non-empty dict) and the corresponding date/time as string (either None or the date/time).
    def readFromCache( self, baseName, cacheMaximumDateTime ):
        # Read all files in the cache and keep a list of those which match the base name.
        # Any file matching the base name but is older than the cache maximum date/time id deleted.
        cacheMaximumDateTimeString = cacheMaximumDateTime.strftime( IndicatorLunar.DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
        files = [ ]
        for file in os.listdir( IndicatorLunar.CACHE_PATH ):
            if file.startswith( baseName ):
                fileDateTime = file[ file.index( baseName ) + len( baseName ) : ]
                if fileDateTime < cacheMaximumDateTimeString:
                    os.remove( IndicatorLunar.CACHE_PATH + file )
                else:
                    files.append( file )

        # Sort the matching files by date.  All file(s) will be newer than the cache maximum date/time.
        files.sort()
        data = None
        dateTime = None
        for file in reversed( files ): # Look at the most recent file first.
            filename = IndicatorLunar.CACHE_PATH + file
            try:
                with open( filename, "rb" ) as f:
                    data = pickle.load( f )

                if data is not None and len( data ) > 0:
                    dateTime = file[ len( baseName ) : ]
                    break

            except Exception as e:
                data = None
                dateTime = None
                logging.exception( e )
                logging.error( "Error reading from cache: " + filename )

        # Only return None or non-empty.
        if data is None or len( data ) == 0:
            data = None
            dateTime = None

        return ( data, dateTime )


if __name__ == "__main__": IndicatorLunar().main()