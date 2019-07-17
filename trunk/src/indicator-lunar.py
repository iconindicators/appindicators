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
#  http://wiki.gnome.org/Projects/PyGObject/Threading
#  http://wiki.ubuntu.com/NotifyOSD
#  http://lazka.github.io/pgi-docs/AppIndicator3-0.1
#  http://developer.ubuntu.com/api/devel/ubuntu-12.04/python/AppIndicator3-0.1.html
#  http://developer.ubuntu.com/api/devel/ubuntu-13.10/c/AppIndicator3-0.1.html
#  http://www.flaticon.com/search/satellite


#TODO
# On Ubuntu 19.04, new Yaru theme, so hicolor icon appeared:
# 
# 2019-07-13 17:10:02,976 - root - ERROR - [Errno 2] No such file or directory: '/usr/share/icons/Yaru/scalable/apps/indicator-lunar.svg'
# Traceback (most recent call last):
#   File "/usr/share/indicator-lunar/indicator-lunar.py", line 1897, in getThemeColour
#     with open( iconFilenameForCurrentTheme, "r" ) as file:
# FileNotFoundError: [Errno 2] No such file or directory: '/usr/share/icons/Yaru/scalable/apps/indicator-lunar.svg'
# 2019-07-13 17:10:02,989 - root - ERROR - Error reading SVG icon: /usr/share/icons/Yaru/scalable/apps/indicator-lunar.svg


#TODO Have sent a message to MPC to look at the data format as it looks odd for the two dodgy magnitude comets.
#Maybe there is a way to screen out dodgy data?


#TODO Maybe show other stuff for comets?
# https://www.minorplanetcenter.net/iau/Ephemerides/Soft03.html
# But this means changing to the name orbital elements...or maybe leaving comets as is and add a new thing for OE?
# Maybe rename to OE as it catches all (and they are treated identically by PyEphem).
# By extension, allow for multiple URLs for the OEs (see the URL above)?  ... and ditto for satellites?


#TODO Have an option to hide all but the rise time for a non-satellite body if below the horizon?
# Already do this for satellites!


INDICATOR_NAME = "indicator-lunar"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "Notify", "0.7" )

from gi.repository import AppIndicator3, GLib, Gtk, Notify
from urllib.request import urlopen
import calendar, datetime, eclipse, glob, json, locale, logging, math, os, pythonutils, re, satellite, sys, tempfile, threading, webbrowser

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
    VERSION = "1.0.81"
    ICON = INDICATOR_NAME
    ICON_BASE_NAME = "." + INDICATOR_NAME + "-illumination-icon-"
    ICON_BASE_PATH = tempfile.gettempdir()
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    SVG_FULL_MOON_FILE = ICON_BASE_PATH + "/." + INDICATOR_NAME + "-fullmoon-icon" + ".svg"
    SVG_SATELLITE_ICON = INDICATOR_NAME + "-satellite"

    ABOUT_COMMENTS = _( "Displays lunar, solar, planetary, comet, star and satellite information." )
    ABOUT_CREDIT_ECLIPSE = _( "Eclipse information by Fred Espenak and Jean Meeus. http://eclipse.gsfc.nasa.gov" )
    ABOUT_CREDIT_PYEPHEM = _( "Calculations courtesy of PyEphem/XEphem. http://rhodesmill.org/pyephem" )
    ABOUT_CREDIT_COMET = _( "Comet OE data by Minor Planet Center. http://www.minorplanetcenter.net" )
    ABOUT_CREDIT_SATELLITE = _( "Satellite TLE data by Dr T S Kelso. http://www.celestrak.com" )
    ABOUT_CREDITS = [ ABOUT_CREDIT_PYEPHEM, ABOUT_CREDIT_ECLIPSE, ABOUT_CREDIT_SATELLITE, ABOUT_CREDIT_COMET ]

    DATE_TIME_FORMAT_HHcolonMMcolonSS = "%H:%M:%S"
    DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS = "%Y-%m-%d %H:%M:%S"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSSdotFLOAT = "%Y-%m-%d %H:%M:%S.%f"

    DISPLAY_NEEDS_REFRESH = _( "(needs refresh)" )
    INDENT = "    "

    CONFIG_CITY_ELEVATION = "cityElevation"
    CONFIG_CITY_LATITUDE = "cityLatitude"
    CONFIG_CITY_LONGITUDE = "cityLongitude"
    CONFIG_CITY_NAME = "cityName"
    CONFIG_COMET_OE_URL = "cometOEURL"
    CONFIG_COMETS = "comets"
    CONFIG_COMETS_ADD_NEW = "cometsAddNew"
    CONFIG_COMETS_MAGNITUDE = "cometsMagnitude"
    CONFIG_HIDE_BODY_IF_NEVER_UP = "hideBodyIfNeverUp"
    CONFIG_DATE_TIME_FORMAT = "dateTimeFormat"
    CONFIG_INDICATOR_TEXT = "indicatorText"
    CONFIG_PLANETS = "planets"
    CONFIG_SATELLITE_NOTIFICATION_MESSAGE = "satelliteNotificationMessage"
    CONFIG_SATELLITE_NOTIFICATION_SUMMARY = "satelliteNotificationSummary"
    CONFIG_SATELLITE_NOTIFICATION_TIME_FORMAT = "satelliteNotificationTimeFormat"
    CONFIG_SATELLITE_TLE_URL = "satelliteTLEURL"
    CONFIG_SATELLITES = "satellites"
    CONFIG_SATELLITES_ADD_NEW = "satellitesAddNew"
    CONFIG_SATELLITES_SORT_BY_DATE_TIME = "satellitesSortByDateTime"
    CONFIG_SHOW_COMETS_AS_SUBMENU = "showCometsAsSubmenu"
    CONFIG_SHOW_MOON = "showMoon"
    CONFIG_SHOW_PLANETS_AS_SUBMENU = "showPlanetsAsSubmenu"
    CONFIG_SHOW_SATELLITE_NOTIFICATION = "showSatelliteNotification"
    CONFIG_SHOW_SATELLITES_AS_SUBMENU = "showSatellitesAsSubmenu"
    CONFIG_SHOW_STARS_AS_SUBMENU = "showStarsAsSubmenu"
    CONFIG_SHOW_SUN = "showSun"
    CONFIG_SHOW_WEREWOLF_WARNING = "showWerewolfWarning"
    CONFIG_STARS = "stars"
    CONFIG_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE = "werewolfWarningStartIlluminationPercentage"
    CONFIG_WEREWOLF_WARNING_MESSAGE = "werewolfWarningMessage"
    CONFIG_WEREWOLF_WARNING_SUMMARY = "werewolfWarningSummary"

    TRUE_TEXT = "True"
    FALSE_TEXT = "False"

    TRUE_TEXT_TRANSLATION = _( "True" )
    FALSE_TEXT_TRANSLATION = _( "False" )

    DATA_ALTITUDE = "ALTITUDE"
    DATA_AZIMUTH = "AZIMUTH"
    DATA_DAWN = "DAWN"
    DATA_DUSK = "DUSK"
    DATA_ECLIPSE_DATE_TIME = "ECLIPSE DATE TIME"
    DATA_ECLIPSE_LATITUDE = "ECLIPSE LATITUDE"
    DATA_ECLIPSE_LONGITUDE = "ECLIPSE LONGITUDE"
    DATA_ECLIPSE_TYPE = "ECLIPSE TYPE"
    DATA_ELEVATION = "ELEVATION" # Only used for the CITY "body" tag.
    DATA_FIRST_QUARTER = "FIRST QUARTER"
    DATA_FULL = "FULL"
    DATA_LATITUDE = "LATITUDE" # Only used for the CITY "body" tag.
    DATA_LONGITUDE = "LONGITUDE" # Only used for the CITY "body" tag.
    DATA_MESSAGE = "MESSAGE"
    DATA_NAME = "NAME" # Only used for the CITY "body" tag.
    DATA_NEW = "NEW"
    DATA_PHASE = "PHASE"
    DATA_RISE_AZIMUTH = "RISE AZIMUTH"
    DATA_RISE_TIME = "RISE TIME"
    DATA_SET_AZIMUTH = "SET AZIMUTH"
    DATA_SET_TIME = "SET TIME"
    DATA_THIRD_QUARTER = "THIRD QUARTER"

    DATA_TAGS_ALL = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_DAWN,
        DATA_DUSK,
        DATA_ECLIPSE_DATE_TIME,
        DATA_ECLIPSE_LATITUDE,
        DATA_ECLIPSE_LONGITUDE,
        DATA_ECLIPSE_TYPE,
        DATA_ELEVATION,
        DATA_FIRST_QUARTER,
        DATA_FULL,
        DATA_LATITUDE,
        DATA_LONGITUDE,
        DATA_MESSAGE,
        DATA_NAME,
        DATA_NEW,
        DATA_PHASE,
        DATA_RISE_AZIMUTH,
        DATA_RISE_TIME,
        DATA_SET_AZIMUTH,
        DATA_SET_TIME,
        DATA_THIRD_QUARTER ]

    DATA_TAGS_COMET = [
        DATA_MESSAGE,
        DATA_RISE_AZIMUTH,
        DATA_RISE_TIME,
        DATA_SET_AZIMUTH,
        DATA_SET_TIME ]

    DATA_TAGS_MOON = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_ECLIPSE_DATE_TIME,
        DATA_ECLIPSE_LATITUDE,
        DATA_ECLIPSE_LONGITUDE,
        DATA_ECLIPSE_TYPE,
        DATA_MESSAGE,
        DATA_PHASE,
        DATA_RISE_TIME,
        DATA_SET_TIME ]

    DATA_TAGS_PLANET = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_MESSAGE,
        DATA_RISE_TIME,
        DATA_SET_TIME ]

    DATA_TAGS_SATELLITE = [
        DATA_MESSAGE,
        DATA_RISE_AZIMUTH,
        DATA_RISE_TIME,
        DATA_SET_AZIMUTH,
        DATA_SET_TIME ]

    DATA_TAGS_STAR = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_MESSAGE,
        DATA_RISE_TIME,
        DATA_SET_TIME ]

    DATA_TAGS_SUN = [
        DATA_ALTITUDE,
        DATA_AZIMUTH,
        DATA_DAWN,
        DATA_DUSK,
        DATA_ECLIPSE_DATE_TIME,
        DATA_ECLIPSE_LATITUDE,
        DATA_ECLIPSE_LONGITUDE,
        DATA_ECLIPSE_TYPE,
        DATA_MESSAGE,
        DATA_RISE_TIME,
        DATA_SET_TIME ]

    DATA_TAGS_TRANSLATIONS = {
        DATA_ALTITUDE                   : _( "ALTITUDE" ),
        DATA_AZIMUTH                    : _( "AZIMUTH" ),
        DATA_DAWN                       : _( "DAWN" ),
        DATA_DUSK                       : _( "DUSK" ),
        DATA_ECLIPSE_DATE_TIME          : _( "ECLIPSE DATE TIME" ),
        DATA_ECLIPSE_LATITUDE           : _( "ECLIPSE LATITUDE" ),
        DATA_ECLIPSE_LONGITUDE          : _( "ECLIPSE LONGITUDE" ),
        DATA_ECLIPSE_TYPE               : _( "ECLIPSE TYPE" ),
        DATA_ELEVATION                  : _( "ELEVATION" ),
        DATA_FIRST_QUARTER              : _( "FIRST QUARTER" ),
        DATA_FULL                       : _( "FULL" ),
        DATA_LATITUDE                   : _( "LATITUDE" ),
        DATA_LONGITUDE                  : _( "LONGITUDE" ),
        DATA_MESSAGE                    : _( "MESSAGE" ),
        DATA_NAME                       : _( "NAME" ), # Only used for CITY "body" tag.
        DATA_NEW                        : _( "NEW" ),
        DATA_PHASE                      : _( "PHASE" ),
        DATA_RISE_AZIMUTH               : _( "RISE AZIMUTH" ),
        DATA_RISE_TIME                  : _( "RISE TIME" ),
        DATA_SET_AZIMUTH                : _( "SET AZIMUTH" ),
        DATA_SET_TIME                   : _( "SET TIME" ),
        DATA_THIRD_QUARTER              : _( "THIRD QUARTER" ) }

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

    PLANETS = [ PLANET_MERCURY, PLANET_VENUS, PLANET_MARS, PLANET_JUPITER, PLANET_SATURN, PLANET_URANUS, PLANET_NEPTUNE, PLANET_PLUTO ]

    PLANET_NAMES_TRANSLATIONS = {
        PLANET_MERCURY        : _( "Mercury" ),
        PLANET_VENUS          : _( "Venus" ),
        PLANET_MARS           : _( "Mars" ),
        PLANET_JUPITER        : _( "Jupiter" ),
        PLANET_SATURN         : _( "Saturn" ),
        PLANET_URANUS         : _( "Uranus" ),
        PLANET_NEPTUNE        : _( "Neptune" ),
        PLANET_PLUTO          : _( "Pluto" ) }

    PLANET_TAGS_TRANSLATIONS = {
        "MERCURY"   : _( "MERCURY" ),
        "VENUS"     : _( "VENUS" ),
        "MARS"      : _( "MARS" ),
        "JUPITER"   : _( "JUPITER" ),
        "SATURN"    : _( "SATURN" ),
        "URANUS"    : _( "URANUS" ),
        "NEPTUNE"   : _( "NEPTUNE" ),
        "PLUTO"     : _( "PLUTO" ) }

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
        list( PLANET_TAGS_TRANSLATIONS.items() ) +
        list( STAR_TAGS_TRANSLATIONS.items() ) +
        list( SUN_TAG_TRANSLATION.items() ) )

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

    # The download period serves two purposes:
    #    Prevent over-taxing the download source (which may result in being blocked).
    #    Download as often as necessary for accuracy.
    #
    # The cache age ensures the data retrieved from the cache is not stale.
    #
    # The cache has two uses:
    #    Act as a source when restarting the indicator.
    #    Act as a source when offline.
    COMET_OE_CACHE_BASENAME = "comet-oe-"
    COMET_OE_CACHE_MAXIMUM_AGE_HOURS = 30
    COMET_OE_URL = "https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt"
    COMET_OE_DOWNLOAD_PERIOD_HOURS = 24

    COMET_ON_CLICK_URL = "https://www.minorplanetcenter.net/db_search/show_object?utf8=%E2%9C%93&object_id="

    SATELLITE_TAG_NAME = "[NAME]"
    SATELLITE_TAG_NUMBER = "[NUMBER]"
    SATELLITE_TAG_INTERNATIONAL_DESIGNATOR = "[INTERNATIONAL DESIGNATOR]"
    SATELLITE_TAG_RISE_AZIMUTH = "[RISE AZIMUTH]"
    SATELLITE_TAG_RISE_TIME = "[RISE TIME]"
    SATELLITE_TAG_SET_AZIMUTH = "[SET AZIMUTH]"
    SATELLITE_TAG_SET_TIME = "[SET TIME]"

    SATELLITE_TAG_NAME_TRANSLATION = "[" + _( "NAME" ) + "]"
    SATELLITE_TAG_NUMBER_TRANSLATION = "[" + _( "NUMBER" ) + "]"
    SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION = "[" + _( "INTERNATIONAL DESIGNATOR" ) + "]"
    SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION = "[" + _( "RISE AZIMUTH" ) + "]"
    SATELLITE_TAG_RISE_TIME_TRANSLATION = "[" + _( "RISE TIME" ) + "]"
    SATELLITE_TAG_SET_AZIMUTH_TRANSLATION = "[" + _( "SET AZIMUTH" ) + "]"
    SATELLITE_TAG_SET_TIME_TRANSLATION = "[" + _( "SET TIME" ) + "]"

    SATELLITE_TAG_TRANSLATIONS = Gtk.ListStore( str, str ) # Tag, translated tag.
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_NAME.strip( "[]" ), SATELLITE_TAG_NAME_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_NUMBER.strip( "[]" ), SATELLITE_TAG_NUMBER_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_INTERNATIONAL_DESIGNATOR.strip( "[]" ), SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_RISE_AZIMUTH.strip( "[]" ), SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_RISE_TIME.strip( "[]" ), SATELLITE_TAG_RISE_TIME_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_SET_AZIMUTH.strip( "[]" ), SATELLITE_TAG_SET_AZIMUTH_TRANSLATION.strip( "[]" ) ] )
    SATELLITE_TAG_TRANSLATIONS.append( [ SATELLITE_TAG_SET_TIME.strip( "[]" ), SATELLITE_TAG_SET_TIME_TRANSLATION.strip( "[]" ) ] )

    # The download period serves two purposes:
    #    Prevent over-taxing the download source (which may result in being blocked).
    #    Download as often as necessary for accuracy.
    #
    # The cache age ensures the data retrieved from the cache is not stale.
    #
    # The cache has two uses:
    #    Act as a source when restarting the indicator.
    #    Act as a source when offline.
    SATELLITE_TLE_CACHE_BASENAME = "satellite-tle-"
    SATELLITE_TLE_CACHE_MAXIMUM_AGE_HOURS = 18
    SATELLITE_TLE_DOWNLOAD_PERIOD_HOURS = 12
    SATELLITE_TLE_URL = "https://celestrak.com/NORAD/elements/visual.txt"

    SATELLITE_ON_CLICK_URL = "https://www.n2yo.com/satellite/?s=" + SATELLITE_TAG_NUMBER
    SATELLITE_MENU_TEXT = SATELLITE_TAG_NAME + " : " + SATELLITE_TAG_NUMBER + " : " + SATELLITE_TAG_INTERNATIONAL_DESIGNATOR
    SATELLITE_NOTIFICATION_SUMMARY_DEFAULT = SATELLITE_TAG_NAME + _( " now rising..." )
    SATELLITE_NOTIFICATION_MESSAGE_DEFAULT = \
        _( "Number: " ) + SATELLITE_TAG_NUMBER_TRANSLATION + "\n" + \
        _( "International Designator: " ) + SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n" + \
        _( "Rise Time: " ) + SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n" + \
        _( "Rise Azimuth: " ) + SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n" + \
        _( "Set Time: " ) + SATELLITE_TAG_SET_TIME_TRANSLATION + "\n" + \
        _( "Set Azimuth: " ) + SATELLITE_TAG_SET_AZIMUTH_TRANSLATION

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

    # Data is displayed using a default format, but when an alternate format is required, specify using a source below.
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

        logging.basicConfig( format = pythonutils.LOGGING_BASIC_CONFIG_FORMAT, level = pythonutils.LOGGING_BASIC_CONFIG_LEVEL, handlers = [ pythonutils.TruncatedFileHandler( IndicatorLunar.LOG ) ] )

        self.dialogLock = threading.Lock()
        Notify.init( INDICATOR_NAME )

        # Initialise last update date/times to the past...
        self.lastUpdateCometOE = datetime.datetime.utcnow() - datetime.timedelta( hours = 1000 )
        self.lastUpdateSatelliteTLE = datetime.datetime.utcnow() - datetime.timedelta( hours = 1000 )
        self.lastFullMoonNotfication = datetime.datetime.utcnow() - datetime.timedelta( hours = 1000 )

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, "", AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_icon_theme_path( IndicatorLunar.ICON_BASE_PATH )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

        self.loadConfig()
        self.update( True )


    def main( self ): Gtk.main()


    def update( self, scheduled ):
        with threading.Lock():
            if not scheduled:
                GLib.source_remove( self.updateTimerID )

            # Update backend...
            self.updateCometOEData()
            self.updateSatelliteTLEData()

            self.data.clear() # Must clear the data on each update, otherwise data will accumulate (if a planet/star/satellite was added then removed, the computed data remains).     
            self.data[ ( None, IndicatorLunar.CITY_TAG, IndicatorLunar.DATA_NAME ) ] = self.cityName

            global _city_data
            self.data[ ( None, IndicatorLunar.CITY_TAG, IndicatorLunar.DATA_LATITUDE ) ] = str( round( float( _city_data.get( self.cityName )[ 0 ] ), 1 ) )
            self.data[ ( None, IndicatorLunar.CITY_TAG, IndicatorLunar.DATA_LONGITUDE ) ] = str( round( float( _city_data.get( self.cityName )[ 1 ] ), 1 ) )
            self.data[ ( None, IndicatorLunar.CITY_TAG, IndicatorLunar.DATA_ELEVATION ) ] = str( _city_data.get( self.cityName )[ 2 ] )

            # UTC, used in all calculations which is required by pyephem.
            # When it comes time to display, conversion to local time takes place.
            ephemNow = ephem.now()

            self.updateAstronomicalInformation( ephemNow, self.hideBodyIfNeverUp, self.cometsMagnitude )

            # Update frontend...
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

            self.updateTimerID = GLib.timeout_add_seconds( nextUpdateInSeconds, self.update, True )

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

            # Ideally should be able to create the icon with the same name each time.
            # Due to a bug, the icon name must change between calls to setting the icon.
            # So change the name each time - using the current date/time.
            #    https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620
            #    http://askubuntu.com/questions/490634/application-indicator-icon-not-changing-until-clicked
            iconName = IndicatorLunar.ICON_BASE_NAME + str( datetime.datetime.utcnow().strftime( "%y%m%d%H%M%S" ) )
            iconFilename = IndicatorLunar.ICON_BASE_PATH + "/" + iconName + ".svg"
            self.createIcon( lunarIlluminationPercentage, lunarBrightLimbAngle, iconFilename )
            self.indicator.set_icon_full( iconName, "" ) #TODO Not sure why the icon does not appear under Eclipse...have tried this method as set_icon is deprecated.


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
                      replace( IndicatorLunar.SATELLITE_TAG_SET_TIME, setTime )
            if summary == "":
                summary = " " # The notification summary text must not be empty (at least on Unity).

            message = self.satelliteNotificationMessage. \
                      replace( IndicatorLunar.SATELLITE_TAG_NAME, tle.getName() ). \
                      replace( IndicatorLunar.SATELLITE_TAG_NUMBER, tle.getNumber() ). \
                      replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, tle.getInternationalDesignator() ). \
                      replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
                      replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME, riseTime ). \
                      replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
                      replace( IndicatorLunar.SATELLITE_TAG_SET_TIME, setTime )

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
                    menuItem = Gtk.MenuItem( IndicatorLunar.PLANET_NAMES_TRANSLATIONS[ planetName ] )
                    subMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + IndicatorLunar.PLANET_NAMES_TRANSLATIONS[ planetName ] )
                    menu.append( menuItem )

                self.updateCommonMenu( menuItem, AstronomicalBodyType.Planet, dataTag )


    def updateStarsMenu( self, menu ):
        stars = [ ] # List of lists.  Each sublist contains the star name followed by the translated name.
        for starName in self.stars:
            if not self.hideBody( AstronomicalBodyType.Star, starName.upper(), self.hideBodyIfNeverUp ):
                stars.append( [ starName, IndicatorLunar.STAR_NAMES_TRANSLATIONS[ starName ] ] )

        if len( stars ) > 0:
            starsMenuItem = Gtk.MenuItem( _( "Stars" ) )
            menu.append( starsMenuItem )

            if self.showStarsAsSubMenu:
                starsSubMenu = Gtk.Menu()
                starsMenuItem.set_submenu( starsSubMenu )

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
                missing = ( key not in self.cometOEData ) # This scenario should be covered by the 'no data' clause below...but just in case catch it here!

                badData = ( key in self.cometOEData and \
                          ( AstronomicalBodyType.Comet, key, IndicatorLunar.DATA_MESSAGE ) in self.data ) and \
                          self.data[ ( AstronomicalBodyType.Comet, key, IndicatorLunar.DATA_MESSAGE ) ] == IndicatorLunar.MESSAGE_DATA_BAD_DATA

                noData = ( key in self.cometOEData and \
                         ( AstronomicalBodyType.Comet, key, IndicatorLunar.DATA_MESSAGE ) in self.data ) and \
                          self.data[ ( AstronomicalBodyType.Comet, key, IndicatorLunar.DATA_MESSAGE ) ] == IndicatorLunar.MESSAGE_DATA_NO_DATA

                if missing or badData or noData:
                    subMenu = Gtk.Menu()
                    subMenu.append( Gtk.MenuItem( self.getDisplayData( ( AstronomicalBodyType.Comet, key, IndicatorLunar.DATA_MESSAGE ) ) ) )
                    menuItem.set_submenu( subMenu )
                else:
                    self.updateCommonMenu( menuItem, AstronomicalBodyType.Comet, key )

                    # Add handler.
                    for child in menuItem.get_submenu().get_children():
                        child.set_name( key )
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

        # The backend function to update common data may add the "always up" or "never up" messages (and nothing else).
        # Therefore only check for the presence of these two messages.
        if key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data:
            # This function only handles the messages of 'always up' and 'never up'.
            # Other messages are handled by the specific functions (comet, satellite).
            if self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_BODY_ALWAYS_UP or \
               self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_BODY_NEVER_UP:
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
            for theKey, text, dateTime in data:
                subMenu.append( Gtk.MenuItem( text + self.getDisplayData( theKey ) ) )

        subMenu.append( Gtk.SeparatorMenuItem() )

        subMenu.append( Gtk.MenuItem( _( "Azimuth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_AZIMUTH, ) ) ) )
        subMenu.append( Gtk.MenuItem( _( "Altitude: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_ALTITUDE, ) ) ) )

        menuItem.set_submenu( subMenu )


    def updateSatellitesMenu( self, menu ):
        menuTextSatelliteNameNumberRiseTimes = [ ]
        for satelliteName, satelliteNumber in self.satellites: # key is satellite name/number.
            key = ( AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )
            if key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data and \
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

            utcNow = datetime.datetime.utcnow()
            for menuText, satelliteName, satelliteNumber, riseTime in menuTextSatelliteNameNumberRiseTimes: # key is satellite name/number.
                key = ( AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )
                subMenu = Gtk.Menu()
                if key + ( IndicatorLunar.DATA_MESSAGE, ) in self.data:
                    if self.data[ key + ( IndicatorLunar.DATA_MESSAGE, ) ] == IndicatorLunar.MESSAGE_SATELLITE_IS_CIRCUMPOLAR:
                        subMenu.append( Gtk.MenuItem( _( "Azimuth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_AZIMUTH, ) ) ) )

                    subMenu.append( Gtk.MenuItem( self.getDisplayData( key + ( IndicatorLunar.DATA_MESSAGE, ) ) ) )
                else:
#TODO Test this...
#Hide notification and make all passes visible (comment out the check for visible only passes).
#Check the maths for when a satellite is more than two minutes from rising,
#also for a satellite yet to rise,
#also a satellite currently rising.

                    riseTime = self.toDateTime( self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] )
                    dateTimeDifferenceInMinutes = ( riseTime - utcNow ).total_seconds() / 60 # If the satellite is currently rising, we'll get a negative but that's okay.
                    if dateTimeDifferenceInMinutes > 2: # If this satellite will rise more than two minutes from now, then only show the rise time.
                        subMenu.append( Gtk.MenuItem( _( "Rise Date/Time: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_RISE_TIME, ) ) ) )

                    else: # This satellite will rise within the next two minutes, so show all data.
                        subMenu.append( Gtk.MenuItem( _( "Rise" ) ) )
                        subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Date/Time: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_RISE_TIME, ) ) ) )
                        subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Azimuth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_RISE_AZIMUTH, ) ) ) )

                        subMenu.append( Gtk.MenuItem( _( "Set" ) ) )
                        subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Date/Time: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_SET_TIME, ) ) ) )
                        subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + _( "Azimuth: " ) + self.getDisplayData( key + ( IndicatorLunar.DATA_SET_AZIMUTH, ) ) ) )

                    # Add the rise to the next update, ensuring it is not in the past.
                    # Subtract a minute from the rise time to spoof the next update to happen earlier.
                    # This allows the update to occur and satellite notification to take place just prior to the satellite rise.
                    riseTimeMinusOneMinute = self.toDateTime( self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] ) - datetime.timedelta( minutes = 1 )
                    if riseTimeMinusOneMinute > utcNow:
                        self.nextUpdate = self.getSmallestDateTime( str( riseTimeMinusOneMinute ), self.nextUpdate )

                    # Add the set time to the next update, ensuring it is not in the past.
                    if self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] > str( utcNow ):
                        self.nextUpdate = self.getSmallestDateTime( self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ], self.nextUpdate )

                # Add handler.
                for child in subMenu.get_children():
                    child.set_name( satelliteName + "-----" + satelliteNumber ) # Cannot pass the tuple - must be a string.
                    child.connect( "activate", self.onSatellite )

                if self.showSatellitesAsSubMenu:
                    menuItem = Gtk.MenuItem( menuText )
                    satellitesSubMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + menuText )
                    menu.append( menuItem )

                menuItem.set_submenu( subMenu )


    def onSatellite( self, widget ):
        satelliteTLE = self.satelliteTLEData.get( tuple( widget.props.name.split( "-----" ) ) )

        url = IndicatorLunar.SATELLITE_ON_CLICK_URL. \
              replace( IndicatorLunar.SATELLITE_TAG_NAME, satelliteTLE.getName() ). \
              replace( IndicatorLunar.SATELLITE_TAG_NUMBER, satelliteTLE.getNumber() ). \
              replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, satelliteTLE.getInternationalDesignator() )

        if len( url ) > 0:
            webbrowser.open( url )


    def getDisplayData( self, key, source = None ):
        displayData = None
        if key[ 2 ] == IndicatorLunar.DATA_ALTITUDE or \
           key[ 2 ] == IndicatorLunar.DATA_AZIMUTH or \
           key[ 2 ] == IndicatorLunar.DATA_RISE_AZIMUTH or \
           key[ 2 ] == IndicatorLunar.DATA_SET_AZIMUTH:
            displayData = str( self.getDecimalDegrees( self.data[ key ], False, 0 ) ) + "°"

        elif key[ 2 ] == IndicatorLunar.DATA_DAWN or \
             key[ 2 ] == IndicatorLunar.DATA_DUSK or \
             key[ 2 ] == IndicatorLunar.DATA_ECLIPSE_DATE_TIME or \
             key[ 2 ] == IndicatorLunar.DATA_FIRST_QUARTER or \
             key[ 2 ] == IndicatorLunar.DATA_FULL or \
             key[ 2 ] == IndicatorLunar.DATA_NEW or \
             key[ 2 ] == IndicatorLunar.DATA_RISE_TIME or \
             key[ 2 ] == IndicatorLunar.DATA_SET_TIME or \
             key[ 2 ] == IndicatorLunar.DATA_THIRD_QUARTER:
                if source is None:
                    displayData = self.getLocalDateTime( self.data[ key ], self.dateTimeFormat )
                elif source == IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION:
                    displayData = self.getLocalDateTime( self.data[ key ], self.satelliteNotificationTimeFormat )

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

        elif key[ 2 ] == IndicatorLunar.DATA_LATITUDE or \
             key[ 2 ] == IndicatorLunar.DATA_LONGITUDE:
            displayData = self.data[ key ] + "°"

        elif key[ 2 ] == IndicatorLunar.DATA_MESSAGE:
            displayData = self.data[ key ]

        elif key[ 2 ] == IndicatorLunar.DATA_PHASE:
            displayData = IndicatorLunar.LUNAR_PHASE_NAMES_TRANSLATIONS[ self.data[ key ] ]

        elif key[ 2 ] == IndicatorLunar.DATA_NAME:
            displayData = self.data[ key ]

        if displayData is None:
            logging.error( "Unknown/unhandled key: " + key )

        return displayData # Returning None is not good but better to let it crash and find out about it than hide the problem.


    # Converts a UTC datetime string in the format given to local datetime string.
    def getLocalDateTime( self, utcDateTimeString, formatString ):
        utcDateTime = self.toDateTime( utcDateTimeString )
        timestamp = calendar.timegm( utcDateTime.timetuple() )
        localDateTime = datetime.datetime.fromtimestamp( timestamp )
        localDateTime.replace( microsecond = utcDateTime.microsecond )
        localDateTimeString = localDateTime.strftime( formatString )

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


    def toDateTime( self, dateTimeAsString ):
        # Have found (very seldom) that a date/time may be generated from the pyephem backend
        # with the .%f component which may mean the value is zero but pyephem dropped it.
        # However this means the format does not match and parsing into a DateTime object fails.
        # So pre-check for .%f and if missing, add in ".0" to keep the parsing happy.
        s = dateTimeAsString
        if re.search( r"\.\d+$", s ) is None:
            s += ".0"

        return datetime.datetime.strptime( s, IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSSdotFLOAT )


    # Compare two string dates in the format YYYY MM DD HH:MM:SS, returning the earliest.
    def getSmallestDateTime( self, firstDateTimeAsString, secondDateTimeAsString ):
        if firstDateTimeAsString < secondDateTimeAsString:
            return firstDateTimeAsString

        return secondDateTimeAsString


    def updateCometOEData( self ):
        if datetime.datetime.utcnow() > ( self.lastUpdateCometOE + datetime.timedelta( hours = IndicatorLunar.COMET_OE_DOWNLOAD_PERIOD_HOURS ) ):
            pythonutils.removeOldFilesFromCache( INDICATOR_NAME, IndicatorLunar.COMET_OE_CACHE_BASENAME, IndicatorLunar.COMET_OE_CACHE_MAXIMUM_AGE_HOURS )
            self.cometOEData, cacheDateTime = pythonutils.readCacheBinary( INDICATOR_NAME, IndicatorLunar.COMET_OE_CACHE_BASENAME, logging ) # Returned data is either None or non-empty.
            if self.cometOEData is None:
                self.cometOEData = self.getCometOEData( self.cometOEURL ) # Format: http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId468501

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
                    pythonutils.writeCacheBinary( self.cometOEData, INDICATOR_NAME, IndicatorLunar.COMET_OE_CACHE_BASENAME, logging )

                # Even if the data download failed or was empty, don't do another download until the required time elapses...don't want to bother the source!
                self.lastUpdateCometOE = datetime.datetime.utcnow()

            else:
                # Set the next update to occur when the cache is due to expire.
                self.lastUpdateCometOE = datetime.datetime.strptime( cacheDateTime, IndicatorLunar.DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + datetime.timedelta( hours = IndicatorLunar.COMET_OE_CACHE_MAXIMUM_AGE_HOURS )

            if self.cometsAddNew:
                self.addNewComets()


    def updateSatelliteTLEData( self ):
        if datetime.datetime.utcnow() > ( self.lastUpdateSatelliteTLE + datetime.timedelta( hours = IndicatorLunar.SATELLITE_TLE_DOWNLOAD_PERIOD_HOURS ) ):
            pythonutils.removeOldFilesFromCache( INDICATOR_NAME, IndicatorLunar.SATELLITE_TLE_CACHE_BASENAME, IndicatorLunar.SATELLITE_TLE_CACHE_MAXIMUM_AGE_HOURS )
            self.satelliteTLEData, cacheDateTime = pythonutils.readCacheBinary( INDICATOR_NAME, IndicatorLunar.SATELLITE_TLE_CACHE_BASENAME, logging )
            if self.satelliteTLEData is None:
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
                    pythonutils.writeCacheBinary( self.satelliteTLEData, INDICATOR_NAME, IndicatorLunar.SATELLITE_TLE_CACHE_BASENAME, logging )

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


    def purgeIcons( self ):
        oldIcons = glob.glob( IndicatorLunar.ICON_BASE_PATH + "/" + IndicatorLunar.ICON_BASE_NAME + "*" )
        for oldIcon in oldIcons:
            os.remove( oldIcon )


    def updateAstronomicalInformation( self, ephemNow, hideBodyIfNeverUp, hideCometGreaterThanMagnitude ):
        self.updateMoon( ephemNow, hideBodyIfNeverUp )
        self.updateSun( ephemNow, hideBodyIfNeverUp )
        self.updatePlanets( ephemNow, hideBodyIfNeverUp )
        self.updateStars( ephemNow, hideBodyIfNeverUp )
        self.updateComets( ephemNow, hideBodyIfNeverUp, hideCometGreaterThanMagnitude )
        self.updateSatellites( ephemNow )


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
                illuminationPercentage = int( self.getPhase( ephem.Moon( self.getCity( ephemNow ) ) ) )
                self.data[ key + ( IndicatorLunar.DATA_PHASE, ) ] = self.getLunarPhase( ephemNow, illuminationPercentage )
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


    # Calculates the common attributes such as rise/set and azimuth/altitude.
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

            self.data[ key + ( IndicatorLunar.DATA_AZIMUTH, ) ] = str( body.az )
            self.data[ key + ( IndicatorLunar.DATA_ALTITUDE, ) ] = str( body.alt )


    def hideBody( self, astronomicalBodyType, dataTag, hideIfNeverUp ):
        key = ( astronomicalBodyType, dataTag, IndicatorLunar.DATA_MESSAGE )
        return \
            key in self.data and \
            self.data[ key ] == IndicatorLunar.MESSAGE_BODY_NEVER_UP and \
            hideIfNeverUp


    def getPhase( self, body ): return round( body.phase )


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
    #  https://www.calsky.com/cs.cgi?cha=6&sec=1
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
    def updateSatellites( self, ephemNow ):
        for key in self.satellites:
            if key in self.satelliteTLEData:
                self.calculateNextSatellitePass( ephemNow, key, self.satelliteTLEData[ key ] )
            else:
                self.data[ ( AstronomicalBodyType.Satellite, " ".join( key ), IndicatorLunar.DATA_MESSAGE ) ] = IndicatorLunar.MESSAGE_DATA_NO_DATA


    def calculateNextSatellitePass( self, ephemNow, key, satelliteTLE ):
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

            # Now have a satellite rise/transit/set; determine if the pass is visible.
            passIsVisible = self.isSatellitePassVisible( satellite, nextPass[ 2 ] )
            if not passIsVisible:
                currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )
                continue

            # The pass is visible and the user wants only visible passes OR the user wants any pass...
            self.data[ key + ( IndicatorLunar.DATA_RISE_TIME, ) ] = str( nextPass[ 0 ].datetime() )
            self.data[ key + ( IndicatorLunar.DATA_RISE_AZIMUTH, ) ] = str( nextPass[ 1 ] )
            self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] = str( nextPass[ 4 ].datetime() )
            self.data[ key + ( IndicatorLunar.DATA_SET_AZIMUTH, ) ] = str( nextPass[ 5 ] )

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
        if self.dialogLock.acquire( blocking = False ):
            pythonutils.showAboutDialog(
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

            self.dialogLock.release()


    def onPreferences( self, widget ):
        if self.dialogLock.acquire( blocking = False ):
            self._onPreferences( widget )
            self.dialogLock.release()


    def _onPreferences( self, widget ):

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
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Icon Text" ) ), False, False, 0 )

        indicatorText = Gtk.Entry()
        indicatorText.set_tooltip_text( _(
            "The text shown next to the indicator icon,\n" + \
            "or tooltip where applicable.\n\n" + \
            "If a body is unchecked or no longer exists\n" + \
            "such as a comet/satellite not on the list,\n" + \
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

            if hideMessage and self.hideBodyIfNeverUp:
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

        tree.set_tooltip_text( _( "Double click to add a tag to the icon text." ) )
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

        box = Gtk.Box( spacing = 40 )
        box.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )

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

        box = Gtk.Box( spacing = 40 )
        box.set_margin_left( pythonutils.INDENT_WIDGET_LEFT )

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
            "If checked, planets, moon, sun,\n" + \
            "comets and stars which rise/set or\n" + \
            "are 'always up' will only be shown.\n\n" + \
            "Otherwise all bodies are shown.\n\n" + \
            "Does not apply to satellites." ) )
        grid.attach( hideBodyIfNeverUpCheckbox, 0, 4, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.pack_start( Gtk.Label( _( "Date/time format" ) ), False, False, 0 )

        dateTimeFormatEntry = Gtk.Entry()
        dateTimeFormatEntry.set_text( self.dateTimeFormat )
        dateTimeFormatEntry.set_hexpand( True )
        dateTimeFormatEntry.set_tooltip_text( _(
            "Specify the format of attributes containing a date/time.\n\n" + \
            "Refer to http://docs.python.org/3/library/datetime.html" ) )
        box.pack_start( dateTimeFormatEntry, True, True, 0 )

        grid.attach( box, 0, 5, 1, 1 )

        cometsAddNewCheckbox = Gtk.CheckButton( _( "Automatically add new comets" ) )
        cometsAddNewCheckbox.set_margin_top( 10 )
        cometsAddNewCheckbox.set_active( self.cometsAddNew )
        cometsAddNewCheckbox.set_tooltip_text( _(
            "If checked, all comets are added\n" + \
            "to the list of checked comets." ) )
        grid.attach( cometsAddNewCheckbox, 0, 6, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Hide comets greater than magnitude" ) ), False, False, 0 )

        spinnerCometMagnitude = Gtk.SpinButton()
        spinnerCometMagnitude.set_numeric( True )
        spinnerCometMagnitude.set_update_policy( Gtk.SpinButtonUpdatePolicy.IF_VALID )
        spinnerCometMagnitude.set_adjustment( Gtk.Adjustment( self.cometsMagnitude, -30, 30, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerCometMagnitude.set_value( self.cometsMagnitude ) # ...so need to force the initial value by explicitly setting it.
        spinnerCometMagnitude.set_tooltip_text( _(
            "Comets with a magnitude greater\n" + \
            "than that specified are hidden." ) )

        box.pack_start( spinnerCometMagnitude, False, False, 0 )

        grid.attach( box, 0, 7, 1, 1 )

        satellitesAddNewCheckbox = Gtk.CheckButton( _( "Automatically add new satellites" ) )
        satellitesAddNewCheckbox.set_margin_top( 10 )
        satellitesAddNewCheckbox.set_active( self.satellitesAddNew )
        satellitesAddNewCheckbox.set_tooltip_text( _(
            "If checked all satellites are added\n" + \
            "to the list of checked satellites." ) )
        grid.attach( satellitesAddNewCheckbox, 0, 8, 1, 1 )

        sortSatellitesByDateTimeCheckbox = Gtk.CheckButton( _( "Sort satellites by rise date/time" ) )
        sortSatellitesByDateTimeCheckbox.set_margin_top( 10 )
        sortSatellitesByDateTimeCheckbox.set_active( self.satellitesSortByDateTime )
        sortSatellitesByDateTimeCheckbox.set_tooltip_text( _(
            "If checked, satellites are sorted\n" + \
            "by rise date/time.\n\n" + \
            "Otherwise satellites are sorted\n" + \
            "by Name, Number and then\n" + \
            "International Designator." ) )
        grid.attach( sortSatellitesByDateTimeCheckbox, 0, 9, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Menu" ) ) )

        # Planets/Stars.
        box = Gtk.Box( spacing = 20 )

        planetStore = Gtk.ListStore( bool, str, str ) # Show/hide, planet name (not displayed), translated planet name.
        for planetName in IndicatorLunar.PLANETS:
            planetStore.append( [ planetName in self.planets, planetName, IndicatorLunar.PLANET_NAMES_TRANSLATIONS[ planetName ] ] )

        tree = Gtk.TreeView( planetStore )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( _(
            "Check a planet to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." ) )

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

        stars = [ ] # List of lists, each sublist containing star is checked flag, star name, star translated name.
        for starName in IndicatorLunar.STAR_NAMES_TRANSLATIONS.keys():
            starTranslated = IndicatorLunar.STAR_NAMES_TRANSLATIONS[ starName ]
            stars.append( [ starName in self.stars, starName, starTranslated ] )

        stars = sorted( stars, key = lambda x: ( x[ 2 ] ) )
        starStore = Gtk.ListStore( bool, str, str ) # Show/hide, star name (not displayed), star translated name.
        for star in stars:
            starStore.append( star )

        starStoreSort = Gtk.TreeModelSort( model = starStore )
        starStoreSort.set_sort_column_id( 2, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( starStoreSort )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( _(
            "Check a star to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, starStore, starStoreSort, AstronomicalBodyType.Star )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, starStore, starStoreSort, displayTagsStore, AstronomicalBodyType.Star )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Star" ), Gtk.CellRendererText(), text = 2 )
        treeViewColumn.set_sort_column_id( 2 )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        box.pack_start( scrolledWindow, True, True, 0 )

        notebook.append_page( box, Gtk.Label( _( "Planets / Stars" ) ) )

        # Comets.
        cometGrid = Gtk.Grid()
        cometGrid.set_column_spacing( 10 )
        cometGrid.set_row_spacing( 10 )
        cometGrid.set_margin_left( 10 )
        cometGrid.set_margin_right( 10 )
        cometGrid.set_margin_top( 10 )
        cometGrid.set_margin_bottom( 10 )

        cometStore = Gtk.ListStore( bool, str ) # Show/hide, comet name.
        cometStoreSort = Gtk.TreeModelSort( model = cometStore )
        cometStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( cometStoreSort )
        tree.set_tooltip_text( _(
            "Check a comet to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." ) )

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

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Comet OE data" ) ), False, False, 0 )

        self.cometOEDataNew = None
        self.cometOEURLNew = None

        cometURLEntry = Gtk.Entry()
        cometURLEntry.set_text( self.cometOEURL )
        cometURLEntry.set_tooltip_text( _(
            "The URL from which to source\n" + \
            "comet OE data.\n\n" + \
            "To specify a local file, use 'file:///'\n" + \
            "and the filename.\n\n" + \
            "Set a bogus URL such as 'http://'\n" + \
            "to disable." ) )
        box.pack_start( cometURLEntry, True, True, 0 )

        fetch = Gtk.Button( _( "Fetch" ) )
        fetch.set_tooltip_text( _(
            "Retrieve the comet OE data.\n\n" + \
            "If the URL is empty, the default\n" + \
            "URL will be used.\n\n" + \
            "If using the default URL, the\n" + \
            "download may be blocked to\n" + \
            "avoid burdening the source." ) )
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

        notebook.append_page( cometGrid, Gtk.Label( _( "Comets" ) ) )

        # Satellites.
        satelliteGrid = Gtk.Grid()
        satelliteGrid.set_column_spacing( 10 )
        satelliteGrid.set_row_spacing( 10 )
        satelliteGrid.set_margin_left( 10 )
        satelliteGrid.set_margin_right( 10 )
        satelliteGrid.set_margin_top( 10 )
        satelliteGrid.set_margin_bottom( 10 )

        satelliteStore = Gtk.ListStore( bool, str, str, str ) # Show/hide, name, number, international designator.
        satelliteStoreSort = Gtk.TreeModelSort( model = satelliteStore )
        satelliteStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( satelliteStoreSort )
        tree.set_tooltip_text( _(
            "Check a satellite to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." ) )

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

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Satellite TLE data" ) ), False, False, 0 )

        self.satelliteTLEDataNew = None
        self.satelliteTLEURLNew = None

        TLEURLEntry = Gtk.Entry()
        TLEURLEntry.set_text( self.satelliteTLEURL )
        TLEURLEntry.set_hexpand( True )
        TLEURLEntry.set_tooltip_text( _(
            "The URL from which to source\n" + \
            "satellite TLE data.\n\n" + \
            "To specify a local file, use 'file:///'\n" + \
            "and the filename.\n\n" + \
            "Set a bogus URL such as 'http://'\n" + \
            "to disable." ) )
        box.pack_start( TLEURLEntry, True, True, 0 )

        fetch = Gtk.Button( _( "Fetch" ) )
        fetch.set_tooltip_text( _(
            "Retrieve the satellite TLE data.\n\n" + \
            "If the URL is empty, the default\n" + \
            "URL will be used.\n\n" + \
            "If using the default URL, the\n" + \
            "download may be blocked to\n" + \
            "avoid burdening the source." ) )
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
        grid.attach( showSatelliteNotificationCheckbox, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( pythonutils.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Summary" ) )
        label.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        box.pack_start( label, False, False, 0 )

        satelliteNotificationSummaryText = Gtk.Entry()
        satelliteNotificationSummaryText.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        satelliteNotificationSummaryText.set_text( self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, True, self.satelliteNotificationSummary ) )
        satelliteNotificationSummaryText.set_tooltip_text( _(
            "The summary for the satellite rise notification.\n\n" + \
            "Available tags:\n\t" ) + \
            IndicatorLunar.SATELLITE_TAG_NAME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NUMBER_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n\t" + \
            _( notifyOSDInformation ) )

        box.pack_start( satelliteNotificationSummaryText, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        showSatelliteNotificationCheckbox.connect( "toggled", pythonutils.onCheckbox, label, satelliteNotificationSummaryText )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( pythonutils.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Message" ) )
        label.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        label.set_valign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        satelliteNotificationMessageText = Gtk.TextView()
        satelliteNotificationMessageText.get_buffer().set_text( self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, True, self.satelliteNotificationMessage ) )
        satelliteNotificationMessageText.set_tooltip_text( _(
            "The message for the satellite rise notification.\n\n" + \
            "Available tags:\n\t" ) + \
            IndicatorLunar.SATELLITE_TAG_NAME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_NUMBER_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n\t" + \
            _( notifyOSDInformation ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( satelliteNotificationMessageText )
        box.pack_start( scrolledWindow, True, True, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        showSatelliteNotificationCheckbox.connect( "toggled", pythonutils.onCheckbox, label, scrolledWindow )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( pythonutils.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Time format" ) )
        label.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        box.pack_start( label, False, False, 0 )

        satelliteNotificationTimeFormatEntry = Gtk.Entry()
        satelliteNotificationTimeFormatEntry.set_text( self.satelliteNotificationTimeFormat )
        satelliteNotificationTimeFormatEntry.set_hexpand( True )
        satelliteNotificationTimeFormatEntry.set_tooltip_text( _(
            "Specify the format of the rise/set time.\n\n" + \
            "Refer to http://docs.python.org/3/library/datetime.html" ) )
        box.pack_start( satelliteNotificationTimeFormatEntry, True, True, 0 )

        grid.attach( box, 0, 3, 1, 1 )

        test = Gtk.Button( _( "Test" ) )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        test.connect( "clicked", self.onTestNotificationClicked, satelliteNotificationSummaryText, satelliteNotificationMessageText, satelliteNotificationTimeFormatEntry, False )
        test.set_tooltip_text( _(
            "Show the notification bubble.\n" + \
            "Tags will be substituted with\n" + \
            "mock text." ) )
        grid.attach( test, 0, 4, 1, 1 )

        showSatelliteNotificationCheckbox.connect( "toggled", pythonutils.onCheckbox, test, test )

        showWerewolfWarningCheckbox = Gtk.CheckButton( _( "Werewolf warning" ) )
        showWerewolfWarningCheckbox.set_margin_top( 10 )
        showWerewolfWarningCheckbox.set_active( self.showWerewolfWarning )
        showWerewolfWarningCheckbox.set_tooltip_text( _(
            "Hourly screen notification leading up to full moon." ) )
        grid.attach( showWerewolfWarningCheckbox, 0, 5, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( pythonutils.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Illumination (%)" ) )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        box.pack_start( label, False, False, 0 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.werewolfWarningStartIlluminationPercentage, 0, 100, 1, 0, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinner.set_value( self.werewolfWarningStartIlluminationPercentage ) # ...so need to force the initial value by explicitly setting it.
        spinner.set_tooltip_text( _(
            "Notifications are shown from the specified\n" + \
            "illumination, commencing after a new moon." ) )
        spinner.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        box.pack_start( spinner, False, False, 0 )

        grid.attach( box, 0, 6, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, label, spinner )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( pythonutils.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Summary" ) )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        box.pack_start( label, False, False, 0 )

        werewolfNotificationSummaryText = Gtk.Entry()
        werewolfNotificationSummaryText.set_text( self.werewolfWarningSummary )
        werewolfNotificationSummaryText.set_tooltip_text( _( "The summary for the werewolf notification.\n\n" ) + notifyOSDInformation )
        werewolfNotificationSummaryText.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        box.pack_start( werewolfNotificationSummaryText, True, True, 0 )

        grid.attach( box, 0, 7, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, label, werewolfNotificationSummaryText )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( pythonutils.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Message" ) )
        label.set_valign( Gtk.Align.START )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        box.pack_start( label, False, False, 0 )

        werewolfNotificationMessageText = Gtk.TextView()
        werewolfNotificationMessageText.get_buffer().set_text( self.werewolfWarningMessage )
        werewolfNotificationMessageText.set_tooltip_text( _( "The message for the werewolf notification.\n\n" ) + notifyOSDInformation )
        werewolfNotificationMessageText.set_sensitive( showWerewolfWarningCheckbox.get_active() )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( werewolfNotificationMessageText )

        box.pack_start( scrolledWindow, True, True, 0 )

        grid.attach( box, 0, 8, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, label, werewolfNotificationMessageText )

        test = Gtk.Button( _( "Test" ) )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        test.connect( "clicked", self.onTestNotificationClicked, werewolfNotificationSummaryText, werewolfNotificationMessageText, None, True )
        test.set_tooltip_text( _( "Show the notification using the current summary/message." ) )
        grid.attach( test, 0, 9, 1, 1 )

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

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "City" ) ), False, False, 0 )

        global _city_data
        cities = sorted( _city_data.keys(), key = locale.strxfrm )
        city = Gtk.ComboBoxText.new_with_entry()
        city.set_tooltip_text( _(
            "Choose a city from the list.\n" + \
            "Or, add in your own city name." ) )
        for c in cities:
            city.append_text( c )

        box.pack_start( city, False, False, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Latitude (DD)" ) ), False, False, 0 )

        latitude = Gtk.Entry()
        latitude.set_tooltip_text( _( "Latitude of your location in decimal degrees." ) )
        box.pack_start( latitude, False, False, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Longitude (DD)" ) ), False, False, 0 )

        longitude = Gtk.Entry()
        longitude.set_tooltip_text( _( "Longitude of your location in decimal degrees." ) )
        box.pack_start( longitude, False, False, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Elevation (m)" ) ), False, False, 0 )

        elevation = Gtk.Entry()
        elevation.set_tooltip_text( _( "Height in metres above sea level." ) )
        box.pack_start( elevation, False, False, 0 )

        grid.attach( box, 0, 3, 1, 1 )

        city.connect( "changed", self.onCityChanged, latitude, longitude, elevation )
        city.set_active( cities.index( self.cityName ) )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorLunar.DESKTOP_FILE, logging ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 4, 1, 1 )

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

            self.indicatorText = self.translateTags( displayTagsStore, False, indicatorText.get_text() )
            self.dateTimeFormat = dateTimeFormatEntry.get_text().strip()
            self.satelliteNotificationTimeFormat = satelliteNotificationTimeFormatEntry.get_text().strip()
            self.showMoon = showMoonCheckbox.get_active()
            self.showSun = showSunCheckbox.get_active()
            self.showPlanetsAsSubMenu = showPlanetsAsSubmenuCheckbox.get_active()
            self.showStarsAsSubMenu = showStarsAsSubmenuCheckbox.get_active()
            self.showCometsAsSubMenu = showCometsAsSubmenuCheckbox.get_active()
            self.showSatellitesAsSubMenu = showSatellitesAsSubmenuCheckbox.get_active()
            self.hideBodyIfNeverUp = hideBodyIfNeverUpCheckbox.get_active()
            self.cometsMagnitude = spinnerCometMagnitude.get_value_as_int()
            self.cometsAddNew = cometsAddNewCheckbox.get_active()
            self.satellitesSortByDateTime = sortSatellitesByDateTimeCheckbox.get_active()
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

                pythonutils.writeCacheBinary( self.cometOEData, INDICATOR_NAME, IndicatorLunar.COMET_OE_CACHE_BASENAME, logging )
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

                pythonutils.writeCacheBinary( self.satelliteTLEData, INDICATOR_NAME, IndicatorLunar.SATELLITE_TLE_CACHE_BASENAME, logging )
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

            self.saveConfig()
            pythonutils.setAutoStart( IndicatorLunar.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            GLib.idle_add( self.update, False )
            break

        dialog.destroy()


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
            pythonutils.removeOldFilesFromCache( INDICATOR_NAME, cacheBasename, cacheMaximumAgeHours )
            dataNew, cacheDateTime = pythonutils.readCacheBinary( INDICATOR_NAME, cacheBasename, logging ) # Returned data is either None or non-empty.
            if dataNew is None:
                # No cache data (either too old or just not there), so download only if it won't exceed the download time limit.
                if datetime.datetime.utcnow() < ( lastUpdate + datetime.timedelta( hours = downloadPeriodHours ) ):
                    nextDownload = str( lastUpdate + datetime.timedelta( hours = downloadPeriodHours ) )
                    Notify.Notification.new( summary, message.format( nextDownload[ 0 : nextDownload.index( "." ) ] ), IndicatorLunar.ICON ).show()
                else:
                    dataNew = getDataFunction( urlNew ) # The comet/satellite data can be None, empty or non-empty.
        else:
            dataNew = getDataFunction( urlNew ) # The comet/satellite data can be None, empty or non-empty.

        if dataNew is None:
            if astronomicalBodyType == AstronomicalBodyType.Comet:
                summary = _( "Error Retrieving Comet OE Data" )
                message = _( "The comet OE data source could not be reached." )
            else: # Assume it's a satellite.
                summary = _( "Error Retrieving Satellite TLE Data" )
                message = _( "The satellite TLE data source could not be reached." )

            Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()

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


    def onTestNotificationClicked( self, button, summaryEntry, messageTextView, satelliteNotificationTimeFormatEntry, isFullMoon ):
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
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.getLocalDateTime( utcNow, satelliteNotificationTimeFormatEntry.get_text().strip() ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION, self.getLocalDateTime( utcNowPlusTenMinutes, satelliteNotificationTimeFormatEntry.get_text().strip() ) )

            message = message. \
                replace( IndicatorLunar.SATELLITE_TAG_NAME_TRANSLATION, "ISS (ZARYA)" ). \
                replace( IndicatorLunar.SATELLITE_TAG_NUMBER_TRANSLATION, "25544" ). \
                replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION, "1998-067A" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION, "123°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.getLocalDateTime( utcNow, satelliteNotificationTimeFormatEntry.get_text().strip() ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION, self.getLocalDateTime( utcNowPlusTenMinutes, satelliteNotificationTimeFormatEntry.get_text().strip() ) )

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

                if hideMessage and self.hideBodyIfNeverUp:
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
        cometOEData = None # Indicates error.
        if pythonutils.isConnectedToInternet():
            try:
                # Comets are read from a URL which assumes the XEphem format.
                # For example
                #
                #    C/2002 Y1 (Juels-Holvorcem),e,103.7816,166.2194,128.8232,242.5695,0.0002609,0.99705756,0.0000,04/13.2508/2003,2000,g  6.5,4.0
                #
                # from which the first field (up to the first ',') is the name.
                cometOEData = { }
                data = urlopen( url, timeout = pythonutils.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
                for i in range( 0, len( data ) ):
                    if not data[ i ].startswith( "#" ):

                        cometName = re.sub( "\s\s+", "", data[ i ][ 0 : data[ i ].index( "," ) ] ) # Found that the comet name can have multiple whitespace, so remove.
                        cometData = data[ i ][ data[ i ].index( "," ) : ]
                        cometOEData[ cometName.upper() ] = cometName + cometData

            except Exception as e:
                cometOEData = None
                logging.exception( e )
                logging.error( "Error retrieving comet OE data from " + str( url ) )

        return cometOEData


    # Returns a dict/hashtable of the satellite TLE data from the specified URL (may be empty).
    # Key: ( satellite name, satellite number ) ; Value: satellite.TLE object.
    # On error, returns None.
    def getSatelliteTLEData( self, url ):
        satelliteTLEData = None # Indicates error.
        if pythonutils.isConnectedToInternet():
            try:
                satelliteTLEData = { }
                data = urlopen( url, timeout = pythonutils.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
                for i in range( 0, len( data ), 3 ):
                    tle = satellite.TLE( data[ i ].strip(), data[ i + 1 ].strip(), data[ i + 2 ].strip() )
                    satelliteTLEData[ ( tle.getName().upper(), tle.getNumber() ) ] = tle

            except Exception as e:
                satelliteTLEData = None
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


    def loadConfig( self ):
        self.getDefaultCity()

        self.dateTimeFormat = IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS
        self.hideBodyIfNeverUp = True
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
        self.satelliteNotificationTimeFormat = IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS
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

        config = pythonutils.loadConfig( INDICATOR_NAME, INDICATOR_NAME, logging )

        global _city_data
        cityElevation = config.get( IndicatorLunar.CONFIG_CITY_ELEVATION, _city_data.get( self.cityName )[ 2 ] )
        cityLatitude = config.get( IndicatorLunar.CONFIG_CITY_LATITUDE, _city_data.get( self.cityName )[ 0 ] )
        cityLongitude = config.get( IndicatorLunar.CONFIG_CITY_LONGITUDE, _city_data.get( self.cityName )[ 1 ] )
        self.cityName = config.get( IndicatorLunar.CONFIG_CITY_NAME, self.cityName )
        _city_data[ self.cityName ] = ( str( cityLatitude ), str( cityLongitude ), float( cityElevation ) ) # Insert/overwrite the cityName and information into the cities.

        self.dateTimeFormat = config.get( IndicatorLunar.CONFIG_DATE_TIME_FORMAT, self.dateTimeFormat )
        self.hideBodyIfNeverUp = config.get( IndicatorLunar.CONFIG_HIDE_BODY_IF_NEVER_UP, self.hideBodyIfNeverUp )
        self.indicatorText = config.get( IndicatorLunar.CONFIG_INDICATOR_TEXT, self.indicatorText )

        # The Minor Planet Center changed the URL protocol to be https (rather than http).
        # The URLs for OE and TLE are now set to use https.
        # Therefore some users may still have the default URLs in their preferences and if so, convert from http to https.
        originalURL = config.get( IndicatorLunar.CONFIG_COMET_OE_URL, self.cometOEURL ).startswith( "http://" ) and \
                      config.get( IndicatorLunar.CONFIG_COMET_OE_URL, self.cometOEURL ).endswith( IndicatorLunar.COMET_OE_URL[ 5 : ] )

        if not originalURL:
            self.cometOEURL = config.get( IndicatorLunar.CONFIG_COMET_OE_URL, self.cometOEURL )

        self.comets = config.get( IndicatorLunar.CONFIG_COMETS, self.comets )
        self.cometsAddNew = config.get( IndicatorLunar.CONFIG_COMETS_ADD_NEW, self.cometsAddNew )
        self.cometsMagnitude = config.get( IndicatorLunar.CONFIG_COMETS_MAGNITUDE, self.cometsMagnitude )
        self.planets = config.get( IndicatorLunar.CONFIG_PLANETS, self.planets )
        self.satelliteNotificationMessage = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE, self.satelliteNotificationMessage )
        self.satelliteNotificationSummary = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY, self.satelliteNotificationSummary )
        self.satelliteNotificationTimeFormat = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_TIME_FORMAT, self.satelliteNotificationTimeFormat )

        # See comment above for OE URL as to why this code is necessary...
        originalURL = config.get( IndicatorLunar.CONFIG_SATELLITE_TLE_URL, self.satelliteTLEURL ).startswith( "http://" ) and \
                      config.get( IndicatorLunar.CONFIG_SATELLITE_TLE_URL, self.satelliteTLEURL ).endswith( IndicatorLunar.SATELLITE_TLE_URL[ 5 : ] )

        if not originalURL:
            self.satelliteTLEURL = config.get( IndicatorLunar.CONFIG_SATELLITE_TLE_URL, self.satelliteTLEURL )

        self.satellites = config.get( IndicatorLunar.CONFIG_SATELLITES, self.satellites )
        self.satellites = [ tuple( l ) for l in self.satellites ] # Converts from a list of lists to a list of tuples...go figure!

        self.satellitesAddNew = config.get( IndicatorLunar.CONFIG_SATELLITES_ADD_NEW, self.satellitesAddNew )
        self.satellitesSortByDateTime = config.get( IndicatorLunar.CONFIG_SATELLITES_SORT_BY_DATE_TIME, self.satellitesSortByDateTime )
        self.showMoon = config.get( IndicatorLunar.CONFIG_SHOW_MOON, self.showMoon )
        self.showCometsAsSubMenu = config.get( IndicatorLunar.CONFIG_SHOW_COMETS_AS_SUBMENU, self.showCometsAsSubMenu )
        self.showPlanetsAsSubMenu = config.get( IndicatorLunar.CONFIG_SHOW_PLANETS_AS_SUBMENU, self.showPlanetsAsSubMenu )
        self.showSatelliteNotification = config.get( IndicatorLunar.CONFIG_SHOW_SATELLITE_NOTIFICATION, self.showSatelliteNotification )
        self.showSatellitesAsSubMenu = config.get( IndicatorLunar.CONFIG_SHOW_SATELLITES_AS_SUBMENU, self.showSatellitesAsSubMenu )
        self.showStarsAsSubMenu = config.get( IndicatorLunar.CONFIG_SHOW_STARS_AS_SUBMENU, self.showStarsAsSubMenu )
        self.showSun = config.get( IndicatorLunar.CONFIG_SHOW_SUN, self.showSun )
        self.showWerewolfWarning = config.get( IndicatorLunar.CONFIG_SHOW_WEREWOLF_WARNING, self.showWerewolfWarning )
        self.stars = config.get( IndicatorLunar.CONFIG_STARS, self.stars )
        self.werewolfWarningStartIlluminationPercentage = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE, self.werewolfWarningStartIlluminationPercentage )
        self.werewolfWarningMessage = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE, self.werewolfWarningMessage )
        self.werewolfWarningSummary = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY, self.werewolfWarningSummary )


    def saveConfig( self ):
        if self.cometsAddNew:
            comets = [ ]
        else:
            comets = self.comets # Only write out the list of comets if the user elects to not add new.

        if self.satellitesAddNew:
            satellites = [ ]
        else:
            satellites = self.satellites # Only write out the list of satellites if the user elects to not add new.

        config = {
            IndicatorLunar.CONFIG_CITY_ELEVATION: _city_data.get( self.cityName )[ 2 ],
            IndicatorLunar.CONFIG_CITY_LATITUDE: _city_data.get( self.cityName )[ 0 ],
            IndicatorLunar.CONFIG_CITY_LONGITUDE: _city_data.get( self.cityName )[ 1 ],
            IndicatorLunar.CONFIG_CITY_NAME: self.cityName,
            IndicatorLunar.CONFIG_DATE_TIME_FORMAT: self.dateTimeFormat,
            IndicatorLunar.CONFIG_HIDE_BODY_IF_NEVER_UP: self.hideBodyIfNeverUp,
            IndicatorLunar.CONFIG_INDICATOR_TEXT: self.indicatorText,
            IndicatorLunar.CONFIG_COMET_OE_URL: self.cometOEURL,
            IndicatorLunar.CONFIG_COMETS: comets,
            IndicatorLunar.CONFIG_COMETS_ADD_NEW: self.cometsAddNew,
            IndicatorLunar.CONFIG_COMETS_MAGNITUDE: self.cometsMagnitude,
            IndicatorLunar.CONFIG_PLANETS: self.planets,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE: self.satelliteNotificationMessage,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY: self.satelliteNotificationSummary,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_TIME_FORMAT: self.satelliteNotificationTimeFormat,
            IndicatorLunar.CONFIG_SATELLITE_TLE_URL: self.satelliteTLEURL,
            IndicatorLunar.CONFIG_SATELLITES: satellites,
            IndicatorLunar.CONFIG_SATELLITES_ADD_NEW: self.satellitesAddNew,
            IndicatorLunar.CONFIG_SATELLITES_SORT_BY_DATE_TIME: self.satellitesSortByDateTime,
            IndicatorLunar.CONFIG_SHOW_MOON: self.showMoon,
            IndicatorLunar.CONFIG_SHOW_COMETS_AS_SUBMENU: self.showCometsAsSubMenu,
            IndicatorLunar.CONFIG_SHOW_PLANETS_AS_SUBMENU: self.showPlanetsAsSubMenu,
            IndicatorLunar.CONFIG_SHOW_SATELLITE_NOTIFICATION: self.showSatelliteNotification,
            IndicatorLunar.CONFIG_SHOW_SATELLITES_AS_SUBMENU: self.showSatellitesAsSubMenu,
            IndicatorLunar.CONFIG_SHOW_STARS_AS_SUBMENU: self.showStarsAsSubMenu,
            IndicatorLunar.CONFIG_SHOW_SUN: self.showSun,
            IndicatorLunar.CONFIG_SHOW_WEREWOLF_WARNING: self.showWerewolfWarning,
            IndicatorLunar.CONFIG_STARS: self.stars,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE: self.werewolfWarningStartIlluminationPercentage,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE: self.werewolfWarningMessage,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY: self.werewolfWarningSummary
        }

        pythonutils.saveConfig( config, INDICATOR_NAME, INDICATOR_NAME, logging )


if __name__ == "__main__": IndicatorLunar().main()