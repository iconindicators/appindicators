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


#TODO If there is no data to download (no internet) and cache is stale,
# ensure satellites/comets/minorplanets already selected by the user are not dropped.


#TODO Test without internet connection...do so with cached items that are not stale, with cached items that are stale and no cached items.


#TODO When no internet and no cached items, the satellites, comets and minor planets selected by the user might get blown away.
#What to do?  If a user has checked specific items, then losing those because no data is available is not good.
#In this case the update function will/should return { }.


#TODO
# On Ubuntu 19.04, new Yaru theme, so hicolor icon appeared:
# 
# 2019-07-13 17:10:02,976 - root - ERROR - [Errno 2] No such file or directory: '/usr/share/icons/Yaru/scalable/apps/indicator-lunar.svg'
# Traceback (most recent call last):
#   File "/usr/share/indicator-lunar/indicator-lunar.py", line 1897, in getThemeColour
#     with open( iconFilenameForCurrentTheme, "r" ) as file:
# FileNotFoundError: [Errno 2] No such file or directory: '/usr/share/icons/Yaru/scalable/apps/indicator-lunar.svg'
# 2019-07-13 17:10:02,989 - root - ERROR - Error reading SVG icon: /usr/share/icons/Yaru/scalable/apps/indicator-lunar.svg


#TODO Test with very high latitudes (north and south) to force circumpolar satellites and never up.


#TODO Test during dusk/evening to see satellite passes in the menu.
#             from datetime import timezone #TODO Testing for satellites
#             self.data = astroPyephem.getAstronomicalInformation( datetime.datetime( 2019, 8, 29, 9, 0, 0, 0, tzinfo = timezone.utc ),


#TODO If the backend/frontend are updating, and the user clicks on about/prefs, show a notification to tell the user they're blocked?
#What about the other way?  If the about/prefs are open, disable the updates?
#What do the other indicators do (PPA)?


#TODO For the preference to hide an object if yet to rise, does this also, somehow, apply to satellites?


INDICATOR_NAME = "indicator-lunar"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "Notify", "0.7" )

from gi.repository import AppIndicator3, GLib, Gtk, Notify
from threading import Timer
import astroPyephem, datetime, eclipse, glob, locale, logging, math, orbitalelement, os, pythonutils, re, tempfile, threading, twolineelement, webbrowser


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.81"
    ICON = INDICATOR_NAME
    ICON_BASE_NAME = "." + INDICATOR_NAME + "-illumination-icon-"
    ICON_BASE_PATH = tempfile.gettempdir()
    DESKTOP_FILE = INDICATOR_NAME + ".py.desktop"
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

#TODO Put back to 5
    START_UP_DELAY_IN_SECONDS = 1 # Used to delay the update function which potentially takes a long time.

    SVG_FULL_MOON_FILE = ICON_BASE_PATH + "/." + INDICATOR_NAME + "-fullmoon-icon" + ".svg"
    SVG_SATELLITE_ICON = INDICATOR_NAME + "-satellite"

    ABOUT_COMMENTS = _( "Displays lunar, solar, planetary, comet, minor planet, star and satellite information." )
    ABOUT_CREDIT_ECLIPSE = _( "Eclipse information by Fred Espenak and Jean Meeus. http://eclipse.gsfc.nasa.gov" )
    ABOUT_CREDIT_PYEPHEM = _( "Calculations courtesy of PyEphem/XEphem. http://rhodesmill.org/pyephem" )
    ABOUT_CREDIT_COMET = _( "Comet and Minor Planet OE data by Minor Planet Center. http://www.minorplanetcenter.net" )
    ABOUT_CREDIT_SATELLITE = _( "Satellite TLE data by Dr T S Kelso. http://www.celestrak.com" )
    ABOUT_CREDITS = [ ABOUT_CREDIT_PYEPHEM, ABOUT_CREDIT_ECLIPSE, ABOUT_CREDIT_SATELLITE, ABOUT_CREDIT_COMET ]

    DATE_TIME_FORMAT_HHcolonMM = "%H:%M"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMM = "%Y-%m-%d %H:%M:%S" #TODO Ask Oleg if I should drop the seconds or not...does it look odd without seconds?

    CONFIG_CITY_ELEVATION = "cityElevation"
    CONFIG_CITY_LATITUDE = "cityLatitude"
    CONFIG_CITY_LONGITUDE = "cityLongitude"
    CONFIG_CITY_NAME = "city"
    CONFIG_COMETS = "comets"
    CONFIG_COMETS_ADD_NEW = "cometsAddNew"
    CONFIG_MAGNITUDE = "magnitude"
    CONFIG_MINOR_PLANETS = "minorPlanets"
    CONFIG_MINOR_PLANETS_ADD_NEW = "minorPlanetsAddNew"
    CONFIG_HIDE_BODIES_BELOW_HORIZON = "hideBodiesBelowHorizon"
    CONFIG_INDICATOR_TEXT = "indicatorText"
    CONFIG_PLANETS = "planets"
    CONFIG_SATELLITE_NOTIFICATION_MESSAGE = "satelliteNotificationMessage"
    CONFIG_SATELLITE_NOTIFICATION_SUMMARY = "satelliteNotificationSummary"
    CONFIG_SATELLITES = "satellites"
    CONFIG_SATELLITES_ADD_NEW = "satellitesAddNew"
    CONFIG_SATELLITES_SORT_BY_DATE_TIME = "satellitesSortByDateTime"
    CONFIG_SHOW_SATELLITE_NOTIFICATION = "showSatelliteNotification"
    CONFIG_SHOW_WEREWOLF_WARNING = "showWerewolfWarning"
    CONFIG_STARS = "stars"
    CONFIG_WEREWOLF_WARNING_MESSAGE = "werewolfWarningMessage"
    CONFIG_WEREWOLF_WARNING_SUMMARY = "werewolfWarningSummary"

    DATA_TAGS_TRANSLATIONS = {
        astroPyephem.DATA_ALTITUDE             : _( "ALTITUDE" ),
        astroPyephem.DATA_AZIMUTH              : _( "AZIMUTH" ),
        astroPyephem.DATA_ECLIPSE_DATE_TIME    : _( "ECLIPSE DATE TIME" ),
        astroPyephem.DATA_ECLIPSE_LATITUDE     : _( "ECLIPSE LATITUDE" ),
        astroPyephem.DATA_ECLIPSE_LONGITUDE    : _( "ECLIPSE LONGITUDE" ),
        astroPyephem.DATA_ECLIPSE_TYPE         : _( "ECLIPSE TYPE" ),
        astroPyephem.DATA_FIRST_QUARTER        : _( "FIRST QUARTER" ),
        astroPyephem.DATA_FULL                 : _( "FULL" ),
        astroPyephem.DATA_NEW                  : _( "NEW" ),
        astroPyephem.DATA_PHASE                : _( "PHASE" ),
        astroPyephem.DATA_RISE_AZIMUTH         : _( "RISE AZIMUTH" ),
        astroPyephem.DATA_RISE_DATE_TIME       : _( "RISE DATE TIME" ),
        astroPyephem.DATA_SET_AZIMUTH          : _( "SET AZIMUTH" ),
        astroPyephem.DATA_SET_DATE_TIME        : _( "SET DATE TIME" ),
        astroPyephem.DATA_THIRD_QUARTER        : _( "THIRD QUARTER" ) }

    CITY_TAG_TRANSLATION = { astroPyephem.NAME_TAG_CITY: _( "CITY" ) } #TODO Is this needed?
    MOON_TAG_TRANSLATION = { astroPyephem.NAME_TAG_MOON : _( "MOON" ) }
    SUN_TAG_TRANSLATION = { astroPyephem.NAME_TAG_SUN : _( "SUN" ) }

    PLANET_NAMES_TRANSLATIONS = {
        astroPyephem.PLANET_MERCURY    : _( "Mercury" ),
        astroPyephem.PLANET_VENUS      : _( "Venus" ),
        astroPyephem.PLANET_MARS       : _( "Mars" ),
        astroPyephem.PLANET_JUPITER    : _( "Jupiter" ),
        astroPyephem.PLANET_SATURN     : _( "Saturn" ),
        astroPyephem.PLANET_URANUS     : _( "Uranus" ),
        astroPyephem.PLANET_NEPTUNE    : _( "Neptune" ),
        astroPyephem.PLANET_PLUTO      : _( "Pluto" ) }

    PLANET_TAGS_TRANSLATIONS = {
        astroPyephem.PLANET_MERCURY    : _( "MERCURY" ),
        astroPyephem.PLANET_VENUS      : _( "VENUS" ),
        astroPyephem.PLANET_MARS       : _( "MARS" ),
        astroPyephem.PLANET_JUPITER    : _( "JUPITER" ),
        astroPyephem.PLANET_SATURN     : _( "SATURN" ),
        astroPyephem.PLANET_URANUS     : _( "URANUS" ),
        astroPyephem.PLANET_NEPTUNE    : _( "NEPTUNE" ),
        astroPyephem.PLANET_PLUTO      : _( "PLUTO" ) }

    STAR_NAMES_TRANSLATIONS = {
        astroPyephem.STARS[ 0 ]    : _( "Achernar" ),
        astroPyephem.STARS[ 1 ]    : _( "Adara" ),
        astroPyephem.STARS[ 2 ]    : _( "Agena" ),
        astroPyephem.STARS[ 3 ]    : _( "Albereo" ),
        astroPyephem.STARS[ 4 ]    : _( "Alcaid" ),
        astroPyephem.STARS[ 5 ]    : _( "Alcor" ),
        astroPyephem.STARS[ 6 ]    : _( "Alcyone" ),
        astroPyephem.STARS[ 7 ]    : _( "Aldebaran" ),
        astroPyephem.STARS[ 8 ]    : _( "Alderamin" ),
        astroPyephem.STARS[ 9 ]    : _( "Alfirk" ),
        astroPyephem.STARS[ 10 ]   : _( "Algenib" ),
        astroPyephem.STARS[ 11 ]   : _( "Algieba" ),
        astroPyephem.STARS[ 12 ]   : _( "Algol" ),
        astroPyephem.STARS[ 13 ]   : _( "Alhena" ),
        astroPyephem.STARS[ 14 ]   : _( "Alioth" ),
        astroPyephem.STARS[ 15 ]   : _( "Almach" ),
        astroPyephem.STARS[ 16 ]   : _( "Alnair" ),
        astroPyephem.STARS[ 17 ]   : _( "Alnilam" ),
        astroPyephem.STARS[ 18 ]   : _( "Alnitak" ),
        astroPyephem.STARS[ 19 ]   : _( "Alphard" ),
        astroPyephem.STARS[ 20 ]   : _( "Alphecca" ),
        astroPyephem.STARS[ 21 ]   : _( "Alshain" ),
        astroPyephem.STARS[ 22 ]   : _( "Altair" ),
        astroPyephem.STARS[ 23 ]   : _( "Antares" ),
        astroPyephem.STARS[ 24 ]   : _( "Arcturus" ),
        astroPyephem.STARS[ 25 ]   : _( "Arkab Posterior" ),
        astroPyephem.STARS[ 26 ]   : _( "Arkab Prior" ),
        astroPyephem.STARS[ 27 ]   : _( "Arneb" ),
        astroPyephem.STARS[ 28 ]   : _( "Atlas" ),
        astroPyephem.STARS[ 29 ]   : _( "Bellatrix" ),
        astroPyephem.STARS[ 30 ]   : _( "Betelgeuse" ),
        astroPyephem.STARS[ 31 ]   : _( "Canopus" ),
        astroPyephem.STARS[ 32 ]   : _( "Capella" ),
        astroPyephem.STARS[ 33 ]   : _( "Caph" ),
        astroPyephem.STARS[ 34 ]   : _( "Castor" ),
        astroPyephem.STARS[ 35 ]   : _( "Cebalrai" ),
        astroPyephem.STARS[ 36 ]   : _( "Deneb" ),
        astroPyephem.STARS[ 37 ]   : _( "Denebola" ),
        astroPyephem.STARS[ 38 ]   : _( "Dubhe" ),
        astroPyephem.STARS[ 39 ]   : _( "Electra" ),
        astroPyephem.STARS[ 40 ]   : _( "Elnath" ),
        astroPyephem.STARS[ 41 ]   : _( "Enif" ),
        astroPyephem.STARS[ 42 ]   : _( "Etamin" ),
        astroPyephem.STARS[ 43 ]   : _( "Fomalhaut" ),
        astroPyephem.STARS[ 44 ]   : _( "Gienah Corvi" ),
        astroPyephem.STARS[ 45 ]   : _( "Hamal" ),
        astroPyephem.STARS[ 46 ]   : _( "Izar" ),
        astroPyephem.STARS[ 47 ]   : _( "Kaus Australis" ),
        astroPyephem.STARS[ 48 ]   : _( "Kochab" ),
        astroPyephem.STARS[ 49 ]   : _( "Maia" ),
        astroPyephem.STARS[ 50 ]   : _( "Markab" ),
        astroPyephem.STARS[ 51 ]   : _( "Megrez" ),
        astroPyephem.STARS[ 52 ]   : _( "Menkalinan" ),
        astroPyephem.STARS[ 53 ]   : _( "Menkar" ),
        astroPyephem.STARS[ 54 ]   : _( "Merak" ),
        astroPyephem.STARS[ 55 ]   : _( "Merope" ),
        astroPyephem.STARS[ 56 ]   : _( "Mimosa" ),
        astroPyephem.STARS[ 57 ]   : _( "Minkar" ),
        astroPyephem.STARS[ 58 ]   : _( "Mintaka" ),
        astroPyephem.STARS[ 59 ]   : _( "Mirach" ),
        astroPyephem.STARS[ 60 ]   : _( "Mirzam" ),
        astroPyephem.STARS[ 61 ]   : _( "Mizar" ),
        astroPyephem.STARS[ 62 ]   : _( "Naos" ),
        astroPyephem.STARS[ 63 ]   : _( "Nihal" ),
        astroPyephem.STARS[ 64 ]   : _( "Nunki" ),
        astroPyephem.STARS[ 65 ]   : _( "Peacock" ),
        astroPyephem.STARS[ 66 ]   : _( "Phecda" ),
        astroPyephem.STARS[ 67 ]   : _( "Polaris" ),
        astroPyephem.STARS[ 68 ]   : _( "Pollux" ),
        astroPyephem.STARS[ 69 ]   : _( "Procyon" ),
        astroPyephem.STARS[ 70 ]   : _( "Rasalgethi" ),
        astroPyephem.STARS[ 71 ]   : _( "Rasalhague" ),
        astroPyephem.STARS[ 72 ]   : _( "Regulus" ),
        astroPyephem.STARS[ 73 ]   : _( "Rigel" ),
        astroPyephem.STARS[ 74 ]   : _( "Rukbat" ),
        astroPyephem.STARS[ 75 ]   : _( "Sadalmelik" ),
        astroPyephem.STARS[ 76 ]   : _( "Sadr" ),
        astroPyephem.STARS[ 77 ]   : _( "Saiph" ),
        astroPyephem.STARS[ 78 ]   : _( "Scheat" ),
        astroPyephem.STARS[ 79 ]   : _( "Schedar" ),
        astroPyephem.STARS[ 80 ]   : _( "Shaula" ),
        astroPyephem.STARS[ 81 ]   : _( "Sheliak" ),
        astroPyephem.STARS[ 82 ]   : _( "Sirius" ),
        astroPyephem.STARS[ 83 ]   : _( "Sirrah" ),
        astroPyephem.STARS[ 84 ]   : _( "Spica" ),
        astroPyephem.STARS[ 85 ]   : _( "Sulafat" ),
        astroPyephem.STARS[ 86 ]   : _( "Tarazed" ),
        astroPyephem.STARS[ 87 ]   : _( "Taygeta" ),
        astroPyephem.STARS[ 88 ]   : _( "Thuban" ),
        astroPyephem.STARS[ 89 ]   : _( "Unukalhai" ),
        astroPyephem.STARS[ 90 ]   : _( "Vega" ),
        astroPyephem.STARS[ 91 ]   : _( "Vindemiatrix" ),
        astroPyephem.STARS[ 92 ]   : _( "Wezen" ),
        astroPyephem.STARS[ 93 ]   : _( "Zaurak" ) }

    STAR_TAGS_TRANSLATIONS = {
        astroPyephem.STARS[ 0 ]    : _( "ACHERNAR" ),
        astroPyephem.STARS[ 1 ]    : _( "ADARA" ),
        astroPyephem.STARS[ 2 ]    : _( "AGENA" ),
        astroPyephem.STARS[ 3 ]    : _( "ALBEREO" ),
        astroPyephem.STARS[ 4 ]    : _( "ALCAID" ),
        astroPyephem.STARS[ 5 ]    : _( "ALCOR" ),
        astroPyephem.STARS[ 6 ]    : _( "ALCYONE" ),
        astroPyephem.STARS[ 7 ]    : _( "ALDEBARAN" ),
        astroPyephem.STARS[ 8 ]    : _( "ALDERAMIN" ),
        astroPyephem.STARS[ 9 ]    : _( "ALFIRK" ),
        astroPyephem.STARS[ 10 ]   : _( "ALGENIB" ),
        astroPyephem.STARS[ 11 ]   : _( "ALGIEBA" ),
        astroPyephem.STARS[ 12 ]   : _( "ALGOL" ),
        astroPyephem.STARS[ 13 ]   : _( "ALHENA" ),
        astroPyephem.STARS[ 14 ]   : _( "ALIOTH" ),
        astroPyephem.STARS[ 15 ]   : _( "ALMACH" ),
        astroPyephem.STARS[ 16 ]   : _( "ALNAIR" ),
        astroPyephem.STARS[ 17 ]   : _( "ALNILAM" ),
        astroPyephem.STARS[ 18 ]   : _( "ALNITAK" ),
        astroPyephem.STARS[ 19 ]   : _( "ALPHARD" ),
        astroPyephem.STARS[ 20 ]   : _( "ALPHECCA" ),
        astroPyephem.STARS[ 21 ]   : _( "ALSHAIN" ),
        astroPyephem.STARS[ 22 ]   : _( "ALTAIR" ),
        astroPyephem.STARS[ 23 ]   : _( "ANTARES" ),
        astroPyephem.STARS[ 24 ]   : _( "ARCTURUS" ),
        astroPyephem.STARS[ 25 ]   : _( "ARKAB POSTERIOR" ),
        astroPyephem.STARS[ 26 ]   : _( "ARKAB PRIOR" ),
        astroPyephem.STARS[ 27 ]   : _( "ARNEB" ),
        astroPyephem.STARS[ 28 ]   : _( "ATLAS" ),
        astroPyephem.STARS[ 29 ]   : _( "BELLATRIX" ),
        astroPyephem.STARS[ 30 ]   : _( "BETELGEUSE" ),
        astroPyephem.STARS[ 31 ]   : _( "CANOPUS" ),
        astroPyephem.STARS[ 32 ]   : _( "CAPELLA" ),
        astroPyephem.STARS[ 33 ]   : _( "CAPH" ),
        astroPyephem.STARS[ 34 ]   : _( "CASTOR" ),
        astroPyephem.STARS[ 35 ]   : _( "CEBALRAI" ),
        astroPyephem.STARS[ 36 ]   : _( "DENEB" ),
        astroPyephem.STARS[ 37 ]   : _( "DENEBOLA" ),
        astroPyephem.STARS[ 38 ]   : _( "DUBHE" ),
        astroPyephem.STARS[ 39 ]   : _( "ELECTRA" ),
        astroPyephem.STARS[ 40 ]   : _( "ELNATH" ),
        astroPyephem.STARS[ 41 ]   : _( "ENIF" ),
        astroPyephem.STARS[ 42 ]   : _( "ETAMIN" ),
        astroPyephem.STARS[ 43 ]   : _( "FOMALHAUT" ),
        astroPyephem.STARS[ 44 ]   : _( "GIENAH CORVI" ),
        astroPyephem.STARS[ 45 ]   : _( "HAMAL" ),
        astroPyephem.STARS[ 46 ]   : _( "IZAR" ),
        astroPyephem.STARS[ 47 ]   : _( "KAUS AUSTRALIS" ),
        astroPyephem.STARS[ 48 ]   : _( "KOCHAB" ),
        astroPyephem.STARS[ 49 ]   : _( "MAIA" ),
        astroPyephem.STARS[ 50 ]   : _( "MARKAB" ),
        astroPyephem.STARS[ 51 ]   : _( "MEGREZ" ),
        astroPyephem.STARS[ 52 ]   : _( "MENKALINAN" ),
        astroPyephem.STARS[ 53 ]   : _( "MENKAR" ),
        astroPyephem.STARS[ 54 ]   : _( "MERAK" ),
        astroPyephem.STARS[ 55 ]   : _( "MEROPE" ),
        astroPyephem.STARS[ 56 ]   : _( "MIMOSA" ),
        astroPyephem.STARS[ 57 ]   : _( "MINKAR" ),
        astroPyephem.STARS[ 58 ]   : _( "MINTAKA" ),
        astroPyephem.STARS[ 59 ]   : _( "MIRACH" ),
        astroPyephem.STARS[ 60 ]   : _( "MIRZAM" ),
        astroPyephem.STARS[ 61 ]   : _( "MIZAR" ),
        astroPyephem.STARS[ 62 ]   : _( "NAOS" ),
        astroPyephem.STARS[ 63 ]   : _( "NIHAL" ),
        astroPyephem.STARS[ 64 ]   : _( "NUNKI" ),
        astroPyephem.STARS[ 65 ]   : _( "PEACOCK" ),
        astroPyephem.STARS[ 66 ]   : _( "PHECDA" ),
        astroPyephem.STARS[ 67 ]   : _( "POLARIS" ),
        astroPyephem.STARS[ 68 ]   : _( "POLLUX" ),
        astroPyephem.STARS[ 69 ]   : _( "PROCYON" ),
        astroPyephem.STARS[ 70 ]   : _( "RASALGETHI" ),
        astroPyephem.STARS[ 71 ]   : _( "RASALHAGUE" ),
        astroPyephem.STARS[ 72 ]   : _( "REGULUS" ),
        astroPyephem.STARS[ 73 ]   : _( "RIGEL" ),
        astroPyephem.STARS[ 74 ]   : _( "RUKBAT" ),
        astroPyephem.STARS[ 75 ]   : _( "SADALMELIK" ),
        astroPyephem.STARS[ 76 ]   : _( "SADR" ),
        astroPyephem.STARS[ 77 ]   : _( "SAIPH" ),
        astroPyephem.STARS[ 78 ]   : _( "SCHEAT" ),
        astroPyephem.STARS[ 79 ]   : _( "SCHEDAR" ),
        astroPyephem.STARS[ 80 ]   : _( "SHAULA" ),
        astroPyephem.STARS[ 81 ]   : _( "SHELIAK" ),
        astroPyephem.STARS[ 82 ]   : _( "SIRIUS" ),
        astroPyephem.STARS[ 83 ]   : _( "SIRRAH" ),
        astroPyephem.STARS[ 84 ]   : _( "SPICA" ),
        astroPyephem.STARS[ 85 ]   : _( "SULAFAT" ),
        astroPyephem.STARS[ 86 ]   : _( "TARAZED" ),
        astroPyephem.STARS[ 87 ]   : _( "TAYGETA" ),
        astroPyephem.STARS[ 88 ]   : _( "THUBAN" ),
        astroPyephem.STARS[ 89 ]   : _( "UNUKALHAI" ),
        astroPyephem.STARS[ 90 ]   : _( "VEGA" ),
        astroPyephem.STARS[ 91 ]   : _( "VINDEMIATRIX" ),
        astroPyephem.STARS[ 92 ]   : _( "WEZEN" ),
        astroPyephem.STARS[ 93 ]   : _( "ZAURAK" ) }

    BODY_TAGS_TRANSLATIONS = dict(
        list( CITY_TAG_TRANSLATION.items() ) +
        list( MOON_TAG_TRANSLATION.items() ) +
        list( PLANET_TAGS_TRANSLATIONS.items() ) +
        list( STAR_TAGS_TRANSLATIONS.items() ) +
        list( SUN_TAG_TRANSLATION.items() ) )

    LUNAR_PHASE_NAMES_TRANSLATIONS = {
        astroPyephem.LUNAR_PHASE_FULL_MOON         : _( "Full Moon" ),
        astroPyephem.LUNAR_PHASE_WANING_GIBBOUS    : _( "Waning Gibbous" ),
        astroPyephem.LUNAR_PHASE_THIRD_QUARTER     : _( "Third Quarter" ),
        astroPyephem.LUNAR_PHASE_WANING_CRESCENT   : _( "Waning Crescent" ),
        astroPyephem.LUNAR_PHASE_NEW_MOON          : _( "New Moon" ),
        astroPyephem.LUNAR_PHASE_WAXING_CRESCENT   : _( "Waxing Crescent" ),
        astroPyephem.LUNAR_PHASE_FIRST_QUARTER     : _( "First Quarter" ),
        astroPyephem.LUNAR_PHASE_WAXING_GIBBOUS    : _( "Waxing Gibbous" )
    }

    COMET_CACHE_BASENAME = "comet-oe-"
    COMET_CACHE_MAXIMUM_AGE_HOURS = 30
    COMET_DATA_URL = "https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt"

    MINOR_PLANET_CACHE_BASENAMES = [ "minorplanet-oe-" + "bright",
                                     "minorplanet-oe-" + "critical",
                                     "minorplanet-oe-" + "distant",
                                     "minorplanet-oe-" + "unusual" ]
    MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS = 30
    MINOR_PLANET_DATA_URLS = [ "https://minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft03Bright.txt", 
                               "https://minorplanetcenter.net/iau/Ephemerides/CritList/Soft03CritList.txt",
                               "https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft03Distant.txt",
                               "https://minorplanetcenter.net/iau/Ephemerides/Unusual/Soft03Unusual.txt" ]

#TODO Might still end up making a duplicate of this: one for comets and one for minor planets.
    MINOR_PLANET_CENTER_CLICK_URL = "https://www.minorplanetcenter.net/db_search/show_object?utf8=%E2%9C%93&object_id="

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

    SATELLITE_CACHE_BASENAME = "satellite-tle-"
    SATELLITE_CACHE_MAXIMUM_AGE_HOURS = 18
    SATELLITE_DATA_URL = "https://celestrak.com/NORAD/elements/visual.txt"
    SATELLITE_MENU_TEXT = SATELLITE_TAG_NAME + " : " + SATELLITE_TAG_NUMBER + " : " + SATELLITE_TAG_INTERNATIONAL_DESIGNATOR
    SATELLITE_NOTIFICATION_SUMMARY_DEFAULT = SATELLITE_TAG_NAME + _( " now rising..." )
    SATELLITE_NOTIFICATION_MESSAGE_DEFAULT = \
        _( "Number: " ) + SATELLITE_TAG_NUMBER_TRANSLATION + "\n" + \
        _( "International Designator: " ) + SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n" + \
        _( "Rise Time: " ) + SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n" + \
        _( "Rise Azimuth: " ) + SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n" + \
        _( "Set Time: " ) + SATELLITE_TAG_SET_TIME_TRANSLATION + "\n" + \
        _( "Set Azimuth: " ) + SATELLITE_TAG_SET_AZIMUTH_TRANSLATION
    SATELLITE_ON_CLICK_URL = "https://www.n2yo.com/satellite/?s=" + SATELLITE_TAG_NUMBER

    WEREWOLF_WARNING_MESSAGE_DEFAULT = _( "                                          ...werewolves about ! ! !" )
    WEREWOLF_WARNING_SUMMARY_DEFAULT = _( "W  A  R  N  I  N  G" )

    INDICATOR_TEXT_DEFAULT = "[" + astroPyephem.NAME_TAG_MOON + " " + astroPyephem.DATA_PHASE + "]"

#TODO Check which of these are still needed.
    MESSAGE_DATA_BAD_DATA = _( "Bad data!" )
    MESSAGE_DATA_CANNOT_ACCESS_DATA_SOURCE = _( "Cannot access the data source\n<a href=\'{0}'>{0}</a>" )
    MESSAGE_DATA_NO_DATA = _( "No data!" )
    MESSAGE_DATA_NO_DATA_FOUND_AT_SOURCE = _( "No data found at\n<a href=\'{0}'>{0}</a>" )
    MESSAGE_SATELLITE_IS_CIRCUMPOLAR = _( "Satellite is circumpolar." )
    MESSAGE_SATELLITE_NEVER_RISES = _( "Satellite never rises." )
    MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME = _( "No passes within the next two days." )
    MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS = _( "Unable to compute next pass!" )
    MESSAGE_SATELLITE_VALUE_ERROR = _( "ValueError" )

#TODO Likely need to put these into a dict, keyed off from the astro messages.
#Then in getdisplaydata for the message type, use the astroPyephem.message and pull the translated/text message from this dict.
    MESSAGE_TRANSLATION_DATA_BAD_DATA = _( "Bad data!" )
    MESSAGE_TRANSLATION_DATA_CANNOT_ACCESS_DATA_SOURCE = _( "Cannot access the data source\n<a href=\'{0}'>{0}</a>" )
    MESSAGE_TRANSLATION_DATA_NO_DATA = _( "No data!" )
    MESSAGE_TRANSLATION_DATA_NO_DATA_FOUND_AT_SOURCE = _( "No data found at\n<a href=\'{0}'>{0}</a>" )
    MESSAGE_TRANSLATION_SATELLITE_IS_CIRCUMPOLAR = _( "Satellite is circumpolar." )
    MESSAGE_TRANSLATION_SATELLITE_NEVER_RISES = _( "Satellite never rises." )
    MESSAGE_TRANSLATION_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME = _( "No passes within the next two days." )
    MESSAGE_TRANSLATION_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS = _( "Unable to compute next pass!" )
    MESSAGE_TRANSLATION_SATELLITE_VALUE_ERROR = _( "ValueError" )

    MESSAGE_DISPLAY_NEEDS_REFRESH = _( "(needs refresh)" )


    def __init__( self ):
        self.cometData = { } # Key: comet name, upper cased; Value: orbitalelement.OE object.  Can be empty but never None.
        self.minorPlanetData = { } # Key: minor planet name, upper cased; Value: orbitalelement.OE object.  Can be empty but never None.
        self.satelliteData = { } # Key: satellite number; Value: twolineelement.TLE object.  Can be empty but never None.
        self.satelliteNotifications = { }

#TODO Do these need to live here?  Do we need to recall the state globally or maybe just within each calling of prefs? Needed at all?
        self.toggleCometsTable = True
        self.toggleMinorPlanetsTable = True
        self.togglePlanetsTable = True
        self.toggleSatellitesTable = True
        self.toggleStarsTable = True

        logging.basicConfig( format = pythonutils.LOGGING_BASIC_CONFIG_FORMAT, level = pythonutils.LOGGING_BASIC_CONFIG_LEVEL, handlers = [ pythonutils.TruncatedFileHandler( IndicatorLunar.LOG ) ] )

        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorLunar.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_icon_theme_path( IndicatorLunar.ICON_BASE_PATH )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )

        menu = Gtk.Menu()
        menu.append( Gtk.MenuItem( _( "Initialising..." ) ) )
        self.indicator.set_menu( menu )
        menu.show_all()

        self.dialogLock = threading.Lock()
        Notify.init( INDICATOR_NAME )

        pythonutils.removeOldFilesFromCache( INDICATOR_NAME, IndicatorLunar.COMET_CACHE_BASENAME, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS )
        pythonutils.removeOldFilesFromCache( INDICATOR_NAME, IndicatorLunar.SATELLITE_CACHE_BASENAME, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS )
        for cacheBaseName in IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES:
            pythonutils.removeOldFilesFromCache( INDICATOR_NAME, cacheBaseName, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )

        # Remove old icons.
        oldIcons = glob.glob( IndicatorLunar.ICON_BASE_PATH + "/" + IndicatorLunar.ICON_BASE_NAME + "*" )
        for oldIcon in oldIcons:
            os.remove( oldIcon )

#TODO Needed?
        self.lastFullMoonNotfication = datetime.datetime.utcnow() - datetime.timedelta( hours = 1000 )

        self.loadConfig()
        
        GLib.timeout_add_seconds( IndicatorLunar.START_UP_DELAY_IN_SECONDS, self.update )


    def main( self ): Gtk.main()


    def update( self, scheduled = True ):
        with threading.Lock():
            if not scheduled:
                GLib.source_remove( self.updateTimerID )

#TODO Testing
            self.cometsAddNew = True
            self.minorPlanetsAddNew = True
            self.satellitesAddNew = True

            # Update data.
            self.cometData = self.updateData( IndicatorLunar.COMET_CACHE_BASENAME, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS, orbitalelement.download, IndicatorLunar.COMET_DATA_URL, astroPyephem.getOrbitalElementsLessThanMagnitude )
            if self.cometsAddNew:
                self.addNewBodies( self.cometData, self.comets )

            self.minorPlanetData = { }
            for baseName, url in zip( IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES, IndicatorLunar.MINOR_PLANET_DATA_URLS ):
                minorPlanetData = self.updateData( baseName, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, orbitalelement.download, url, astroPyephem.getOrbitalElementsLessThanMagnitude )
                for key in minorPlanetData:
                    if key not in self.minorPlanetData:
                        self.minorPlanetData[ key ] = minorPlanetData[ key ]

            if self.minorPlanetsAddNew:
                self.addNewBodies( self.minorPlanetData, self.minorPlanets )

            self.satelliteData = self.updateData( IndicatorLunar.SATELLITE_CACHE_BASENAME, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS, twolineelement.download, IndicatorLunar.SATELLITE_DATA_URL, None )
            if self.satellitesAddNew:
                self.addNewBodies( self.satelliteData, self.satellites )

            # Key is a tuple of AstronomicalBodyType, a name tag and data tag.
            # Value is the astronomical data (or equivalent) as a string.
            self.data = astroPyephem.getAstronomicalInformation( datetime.datetime.utcnow(),
                                                          self.latitude, self.longitude, self.elevation,
                                                          self.planets,
                                                          self.stars,
                                                          self.satellites, self.satelliteData,
                                                          self.comets, self.cometData,
                                                          self.minorPlanets, self.minorPlanetData,
                                                          self.magnitude,
                                                          self.hideBodiesBelowHorizon )

            # Update frontend.
            self.updateMenu()
            self.updateIconAndLabel()

            if self.showWerewolfWarning:
                self.notificationFullMoon()

#TODO Uncomment when all done...don't forget to test!
#             if self.showSatelliteNotification:
#                 self.notificationSatellites()

            self.updateTimerID = GLib.timeout_add_seconds( self.getNextUpdateTimeInSeconds(), self.update )


    # Get the data from the cache, or if stale, download from the source.
    #
    # Returns a dictionary (may be empty).
    def updateData( self, cacheBaseName, cacheMaximumAgeHours, downloadDataFunction, dataURL, magnitudeFilterFunction = None ):
        data = pythonutils.readCacheBinary( INDICATOR_NAME, cacheBaseName, logging ) # Either valid or None.

#TODO Start of temporary hack...
# Cache data formats changed between version 80 and 81.
#
# Satellites still use the TLE object, but the file name changed from satellite to twolineelement and is deemed an invalid object.
# Therefore reading the cache binary will throw an exception and return None.
# Not a problem as a new version will be downloaded and the cache will eventually clear out.
#
# Comets will successfully read in because their objects (dict, tuple string) are valid.
# Comets are still stored in a dict using a string as key but now with a new OE object as the value, which must be handled.
# This check can be removed in version 82.
        if data is not None and cacheBaseName == IndicatorLunar.COMET_CACHE_BASENAME:
            if not isinstance( next( iter( data.values() ) ), orbitalelement.OE ): # Check that the object loaded from cache matches the new OE object.
                data = None
# End of hack!

        if data is None:
            data = downloadDataFunction( dataURL )
            if magnitudeFilterFunction is not None:
                data = magnitudeFilterFunction( data, astroPyephem.MAGNITUDE_MAXIMUM )

            pythonutils.writeCacheBinary( data, INDICATOR_NAME, cacheBaseName, logging )

        return data


    def getNextUpdateTimeInSeconds( self ):
        utcNow = datetime.datetime.utcnow()
        utcNowString = str( utcNow )
        nextUpdateTime = str( utcNow + datetime.timedelta( hours = 1000 ) ) # Set a bogus date/time in the future.
        for key in self.data:
            if key[ 2 ] == astroPyephem.DATA_ECLIPSE_DATE_TIME or \
               key[ 2 ] == astroPyephem.DATA_FIRST_QUARTER or \
               key[ 2 ] == astroPyephem.DATA_FULL or \
               key[ 2 ] == astroPyephem.DATA_NEW or \
               key[ 2 ] == astroPyephem.DATA_RISE_DATE_TIME or \
               key[ 2 ] == astroPyephem.DATA_SET_DATE_TIME or \
               key[ 2 ] == astroPyephem.DATA_THIRD_QUARTER:

                if self.data[ key ] < nextUpdateTime and self.data[ key ] > utcNowString:
                    nextUpdateTime = self.data[ key ]

#TODO see satellite code in original indicator-lunar 
# Rather than muck around with fudging times (apart from setting the rise time a minute earlier), 
# get the code that works out when to do the next update and ensure
# that the next update time >= utc now 
#  
# # Add the rise to the next update, ensuring it is not in the past.
# # Subtract a minute from the rise time to spoof the next update to happen earlier.
# # This allows the update to occur and satellite notification to take place just prior to the satellite rise.
# riseTimeMinusOneMinute = self.toDateTime( self.data[ key + ( astroPyephem.DATA_RISE_TIME, ) ] ) - datetime.timedelta( minutes = 1 )
# if riseTimeMinusOneMinute > utcNow:
# self.nextUpdate = self.getSmallestDateTime( str( riseTimeMinusOneMinute ), self.nextUpdate )
# 
# # Add the set time to the next update, ensuring it is not in the past.
# if self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ] > str( utcNow ):
# self.nextUpdate = self.getSmallestDateTime( self.data[ key + ( IndicatorLunar.DATA_SET_TIME, ) ], self.nextUpdate )


#TODO Might still need to ensure that the update does not happen too frequently?              
#             nextUpdateInSeconds = int( ( self.toDateTime( self.nextUpdate, IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMM ) - datetime.datetime.utcnow() ).total_seconds() )
# 
#             # Ensure the update period is positive, at most every minute and at least every hour.
#             if nextUpdateInSeconds < 60:
#                 nextUpdateInSeconds = 60
#             elif nextUpdateInSeconds > ( 60 * 60 ):
#                 nextUpdateInSeconds = ( 60 * 60 )

        return 10000 #TODO REturn the calculated value!


    def updateMenu( self ):
        menu = Gtk.Menu()

        utcNow = datetime.datetime.utcnow()
        self.updateMoonMenu( menu )
        self.updateSunMenu( menu )
        self.updatePlanetsMenu( menu )
        self.updateStarsMenu( menu )
        self.updateCometsMinorPlanetsMenu( menu, astroPyephem.AstronomicalBodyType.Comet )
        self.updateCometsMinorPlanetsMenu( menu, astroPyephem.AstronomicalBodyType.MinorPlanet )
        self.updateSatellitesMenu( menu )
        pythonutils.createPreferencesAboutQuitMenuItems( menu, len( menu.get_children() ) > 0, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()


    def updateIconAndLabel( self ):
        # Substitute tags for values.
        parsedOutput = self.indicatorText
        for key in self.data.keys():
            if "[" + key[ 1 ] + " " + key[ 2 ] + "]" in parsedOutput:
                parsedOutput = parsedOutput.replace( "[" + key[ 1 ] + " " + key[ 2 ] + "]", self.getDisplayData( key ) )

#TODO For satellites, tags will contain both the name and number...so ensure satellites work!

        parsedOutput = re.sub( "\[[^\[^\]]*\]", "", parsedOutput ) # Remove unused tags.

        self.indicator.set_label( parsedOutput, "" ) # Second parameter is a label-guide: http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html

        # Ideally should be able to create the icon with the same name each time.
        # Due to a bug, the icon name must change between calls to setting the icon.
        # So change the name each time - using the current date/time.
        #    https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620
        #    http://askubuntu.com/questions/490634/application-indicator-icon-not-changing-until-clicked
        iconFilename = IndicatorLunar.ICON_BASE_PATH + \
                       "/" + \
                       IndicatorLunar.ICON_BASE_NAME + \
                       str( datetime.datetime.utcnow().strftime( "%y%m%d%H%M%S" ) ) + \
                       ".svg"

        key = ( astroPyephem.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( astroPyephem.DATA_ILLUMINATION, ) ] )
        lunarBrightLimbAngleInDegrees = int( math.degrees( float( self.data[ key + ( astroPyephem.DATA_BRIGHT_LIMB, ) ] ) ) )
        self.createIcon( lunarIlluminationPercentage, lunarBrightLimbAngleInDegrees, iconFilename )
        self.indicator.set_icon_full( iconFilename, "" )


#TODO Verify
    def notificationFullMoon( self ):
        key = ( astroPyephem.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( astroPyephem.DATA_ILLUMINATION, ) ] )
        lunarPhase = self.data[ key + ( astroPyephem.DATA_PHASE, ) ]
        phaseIsBetweenNewAndFullInclusive = \
            ( lunarPhase == astroPyephem.LUNAR_PHASE_NEW_MOON ) or \
            ( lunarPhase == astroPyephem.LUNAR_PHASE_WAXING_CRESCENT ) or \
            ( lunarPhase == astroPyephem.LUNAR_PHASE_FIRST_QUARTER ) or \
            ( lunarPhase == astroPyephem.LUNAR_PHASE_WAXING_GIBBOUS ) or \
            ( lunarPhase == astroPyephem.LUNAR_PHASE_FULL_MOON )

        if phaseIsBetweenNewAndFullInclusive and \
           lunarIlluminationPercentage >= 99 and \
           ( ( self.lastFullMoonNotfication + datetime.timedelta( hours = 1 ) ) < datetime.datetime.utcnow() ):

            summary = self.werewolfWarningSummary
            if self.werewolfWarningSummary == "":
                summary = " " # The notification summary text cannot be empty (at least on Unity).

            self.createIcon( 100, None, IndicatorLunar.SVG_FULL_MOON_FILE )
            Notify.Notification.new( summary, self.werewolfWarningMessage, IndicatorLunar.SVG_FULL_MOON_FILE ).show()
            os.remove( IndicatorLunar.SVG_FULL_MOON_FILE ) #TODO Is this a race?  Will the file be deleted before being displayed?
            self.lastFullMoonNotfication = datetime.datetime.utcnow()


#TODO Verify
    def notificationSatellites( self ):
        # Create a list of satellite name/number and rise times to then either sort by name/number or rise time.
        satelliteNameNumberRiseTimes = [ ]
        for satelliteName, satelliteNumber, in self.satellites:
            key = ( astroPyephem.AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )
            if ( key + ( astroPyephem.DATA_RISE_DATE_TIME, ) ) in self.data: # Assume all other information is present!
               satelliteNameNumberRiseTimes.append( [ satelliteName, satelliteNumber, self.data[ key + ( astroPyephem.DATA_RISE_DATE_TIME, ) ] ] )

        if self.satellitesSortByDateTime:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 2 ], x[ 0 ], x[ 1 ] ) )
        else:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 0 ], x[ 1 ], x[ 2 ] ) )

        utcNow = str( datetime.datetime.utcnow() )
        for satelliteName, satelliteNumber, riseTime in satelliteNameNumberRiseTimes:
            key = ( astroPyephem.AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )

            if ( satelliteName, satelliteNumber ) in self.satelliteNotifications:
                # There has been a previous notification for this satellite.
                # Ensure that the current rise/set matches that of the previous notification.
                # Due to a quirk of the astro backend, the date/time may not match exactly (be out by a few seconds or more).
                # So need to ensure that the current rise/set and the previous rise/set overlap to be sure it is the same transit.
                currentRise = self.data[ key + ( astroPyephem.DATA_RISE_DATE_TIME, ) ]
                currentSet = self.data[ key + ( astroPyephem.DATA_SET_DATE_TIME, ) ]
                previousRise, previousSet = self.satelliteNotifications[ ( satelliteName, satelliteNumber ) ]
                overlap = ( currentRise < previousSet ) and ( currentSet > previousRise )
                if overlap:
                    continue


            # Ensure the current time is within the rise/set...
            # Subtract a minute from the rise time to force the notification to take place just prior to the satellite rise.
#TODO Use the function below to convert from string to datetime.
#     def toDateTime( self, dateTimeAsString, formatString ): return datetime.datetime.strptime( dateTimeAsString, formatString )
            riseTimeMinusOneMinute = str( self.toDateTime( self.data[ key + ( astroPyephem.DATA_RISE_DATE_TIME, ) ], IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMM ) - datetime.timedelta( minutes = 1 ) )

#TODO Is using strings safe here or do we need datetime?            
            if utcNow < riseTimeMinusOneMinute or \
               utcNow > self.data[ key + ( astroPyephem.DATA_SET_DATE_TIME, ) ]:
                continue

            self.satelliteNotifications[ ( satelliteName, satelliteNumber ) ] = ( self.data[ key + ( astroPyephem.DATA_RISE_DATE_TIME, ) ], self.data[ key + ( astroPyephem.DATA_SET_DATE_TIME, ) ] )

            # Parse the satellite summary/message to create the notification...
            riseTime = self.getDisplayData( key + ( astroPyephem.DATA_RISE_DATE_TIME, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            riseAzimuth = self.getDisplayData( key + ( astroPyephem.DATA_RISE_AZIMUTH, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            setTime = self.getDisplayData( key + ( astroPyephem.DATA_SET_DATE_TIME, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            setAzimuth = self.getDisplayData( key + ( astroPyephem.DATA_SET_AZIMUTH, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            tle = self.satelliteData[ ( satelliteName, satelliteNumber ) ]

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


    def display( self, astronomicalBodyType, nameTag ):
        return ( astronomicalBodyType, nameTag, astroPyephem.DATA_ALTITUDE ) in self.data or \
               ( astronomicalBodyType, nameTag, astroPyephem.DATA_RISE_DATE_TIME ) in self.data


    def updateMoonMenu( self, menu ):
        key = ( astroPyephem.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON )
        if self.display( astroPyephem.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON ):
            menuItem = Gtk.MenuItem( _( "Moon" ) )
            menu.append( menuItem )
            menu.append( menuItem )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            self.updateCommonMenu( subMenu, astroPyephem.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON, 0, 1 )
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Phase: " ) + self.getDisplayData( key + ( astroPyephem.DATA_PHASE, ) ) ) )
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Next Phases" ) ) )

            # Determine which phases occur by date rather than using the phase calculated.
            # The phase (illumination) rounds numbers and so a given phase is entered earlier than what is correct.
            nextPhases = [ ]
            nextPhases.append( [ self.data[ key + ( astroPyephem.DATA_FIRST_QUARTER, ) ], _( "First Quarter: " ), key + ( astroPyephem.DATA_FIRST_QUARTER, ) ] )
            nextPhases.append( [ self.data[ key + ( astroPyephem.DATA_FULL, ) ], _( "Full: " ), key + ( astroPyephem.DATA_FULL, ) ] )
            nextPhases.append( [ self.data[ key + ( astroPyephem.DATA_THIRD_QUARTER, ) ], _( "Third Quarter: " ), key + ( astroPyephem.DATA_THIRD_QUARTER, ) ] )
            nextPhases.append( [ self.data[ key + ( astroPyephem.DATA_NEW, ) ], _( "New: " ), key + ( astroPyephem.DATA_NEW, ) ] )

            nextPhases = sorted( nextPhases, key = lambda tuple: tuple[ 0 ] )
            indent = pythonutils.indent( 1, 2 )
            for dateTime, displayText, key in nextPhases:
                subMenu.append( Gtk.MenuItem( indent + displayText + self.getDisplayData( key ) ) )

            self.updateEclipseMenu( subMenu, astroPyephem.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON )


    def updateSunMenu( self, menu ):
        key = ( astroPyephem.AstronomicalBodyType.Sun, astroPyephem.NAME_TAG_SUN )
        if self.display( astroPyephem.AstronomicalBodyType.Sun, astroPyephem.NAME_TAG_SUN ):
            menuItem = Gtk.MenuItem( _( "Sun" ) )
            menu.append( menuItem )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            self.updateCommonMenu( subMenu, astroPyephem.AstronomicalBodyType.Sun, astroPyephem.NAME_TAG_SUN, 0, 1 )
            self.updateEclipseMenu( subMenu, astroPyephem.AstronomicalBodyType.Sun, astroPyephem.NAME_TAG_SUN )


    def updateEclipseMenu( self, menu, astronomicalBodyType, nameTag ):
        key = ( astronomicalBodyType, nameTag )
        menu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Eclipse" ) ) )
        menu.append( Gtk.MenuItem( pythonutils.indent( 1, 2 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astroPyephem.DATA_ECLIPSE_DATE_TIME, ) ) ) )
        latitude = self.getDisplayData( key + ( astroPyephem.DATA_ECLIPSE_LATITUDE, ) )
        longitude = self.getDisplayData( key + ( astroPyephem.DATA_ECLIPSE_LONGITUDE, ) )
        menu.append( Gtk.MenuItem( pythonutils.indent( 1, 2 ) + _( "Latitude/Longitude: " ) + latitude + " " + longitude ) )
        menu.append( Gtk.MenuItem( pythonutils.indent( 1, 2 ) + _( "Type: " ) + self.getDisplayData( key + ( astroPyephem.DATA_ECLIPSE_TYPE, ) ) ) )


    def updatePlanetsMenu( self, menu ):
        planets = [ ]
        for planet in self.planets:
            if self.display( astroPyephem.AstronomicalBodyType.Planet, planet ):
                planets.append( [ planet, IndicatorLunar.PLANET_NAMES_TRANSLATIONS[ planet ] ] )

        if planets:
            menuItem = Gtk.MenuItem( _( "Planets" ) )
            menu.append( menuItem )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for name, translatedName in planets:
                subMenu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + translatedName ) )
                self.updateCommonMenu( subMenu, astroPyephem.AstronomicalBodyType.Planet, name, 1, 2 )


    def updateStarsMenu( self, menu ):
        stars = [ ]
        for star in self.stars:
            if self.display( astroPyephem.AstronomicalBodyType.Star, star ):
                stars.append( [ star, IndicatorLunar.STAR_NAMES_TRANSLATIONS[ star ] ] )

        if stars:
            menuItem = Gtk.MenuItem( _( "Stars" ) )
            menu.append( menuItem ) 
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            baseURL = "https://hipparcos-tools.cosmos.esa.int/cgi-bin/HIPcatalogueSearch.pl?hipId="#TODO Add to top of code
            for name, translatedName in stars:
                url = baseURL + str( astroPyephem.STARS_TO_HIPPARCOS_IDENTIFIER[ name ] )
                menuItem = Gtk.MenuItem( pythonutils.indent( 0, 1 ) + translatedName )
                menuItem.set_name( url )
                subMenu.append( menuItem )
                self.updateCommonMenu( subMenu, astroPyephem.AstronomicalBodyType.Star, name, 1, 2, url )

#TODO Put into its own function?
            for child in subMenu.get_children():
                child.connect( "activate", self.onMenuItemClick )


    def updateCometsMinorPlanetsMenu( self, menu, astronomicalBodyType ):
        bodies = [ ]
        for body in self.comets if astronomicalBodyType == astroPyephem.AstronomicalBodyType.Comet else self.minorPlanets:
            if self.display( astronomicalBodyType, body ):
                bodies.append( body )

# TODO The section below is similar enough to planets and stars...can we make a generic function?
        if bodies:
            menuItem = Gtk.MenuItem( _( "Comets" ) if astronomicalBodyType == astroPyephem.AstronomicalBodyType.Comet else _( "Minor Planets" ) )
            menu.append( menuItem )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            baseURL = "https://www.minorplanetcenter.net/db_search/show_object?utf8=%E2%9C%93&object_id=" #TODO Add to top of code
            for name in sorted( bodies ):
                url = self.getCometOrMinorPlanetOnClickURL( name, astronomicalBodyType )
                menuItem = Gtk.MenuItem( pythonutils.indent( 0, 1 ) + name )
                menuItem.set_name( url )
                subMenu.append( menuItem )
                self.updateCommonMenu( subMenu, astronomicalBodyType, name, 1, 2, "TODO" )

            for child in subMenu.get_children():
                child.connect( "activate", self.onMenuItemClick )


#TODO Test to make sure comets work (each clause)
#TODO Need to make it work for minor planets.
# https://www.iau.org/public/themes/naming
# https://minorplanetcenter.net/iau/info/CometNamingGuidelines.html
#TODO Can we put this logic into the main functions of each body and then pass some property down so each menu item gets it?
#Then there will be one single on click function.
    def getCometOrMinorPlanetOnClickURL( self, name, astronomicalBodyType ):
        if astronomicalBodyType == astroPyephem.AstronomicalBodyType.Comet:
            if "(" in name: # P/1997 T3 (Lagerkvist-Carsenty)
                id = name[ : name.find( "(" ) ].strip()

            else:
                postSlash = name[ name.find( "/" ) + 1 : ]
                if re.search( '\d', postSlash ): # C/1931 AN
                    id = name

                else: # 97P/Metcalf-Brewington
                    id = name[ : name.find( "/" ) ].strip()

            url = IndicatorLunar.MINOR_PLANET_CENTER_CLICK_URL + id.replace( "/", "%2F" ).replace( " ", "+" )

        else:
            url = "Minor Planets TODO"

        return url


    def updateCommonMenu( self, subMenu, astronomicalBodyType, nameTag, indentUnity, indentGnomeShell, onClickURL = "" ):
        key = ( astronomicalBodyType, nameTag )
        indent = pythonutils.indent( indentUnity, indentGnomeShell )

        if key + ( astroPyephem.DATA_RISE_DATE_TIME, ) in self.data:
            menuItem = Gtk.MenuItem( indent + _( "Rise: " ) + self.getDisplayData( key + ( astroPyephem.DATA_RISE_DATE_TIME, ) ) )
            if onClickURL: menuItem.set_name( onClickURL )
            subMenu.append( menuItem )

        else:
            if key + ( astroPyephem.DATA_SET_DATE_TIME, ) in self.data:
                menuItem = Gtk.MenuItem( indent + _( "Set: " ) + self.getDisplayData( key + ( astroPyephem.DATA_SET_DATE_TIME, ) ) )
                if onClickURL: menuItem.set_name( onClickURL )
                subMenu.append( menuItem )

            menuItem = Gtk.MenuItem( indent + _( "Azimuth: " ) + self.getDisplayData( key + ( astroPyephem.DATA_AZIMUTH, ) ) )
            if onClickURL: menuItem.set_name( onClickURL )
            subMenu.append( menuItem )

            menuItem = Gtk.MenuItem( indent + _( "Altitude: " ) + self.getDisplayData( key + ( astroPyephem.DATA_ALTITUDE, ) ) )
            if onClickURL: menuItem.set_name( onClickURL )
            subMenu.append( menuItem )


    def onMenuItemClick( self, widget ): webbrowser.open( widget.props.name )


    def updateSatellitesMenu( self, menu ):
        satellites = [ ]
        satellitesCircumpolar = [ ]
        for number in self.satellites:
            key = ( astroPyephem.AstronomicalBodyType.Satellite, number )
            if key + ( astroPyephem.DATA_AZIMUTH, ) in self.data:
                satellitesCircumpolar.append( [ number, self.satelliteData[ number ].getName(), None ] )

            elif key + ( astroPyephem.DATA_RISE_DATE_TIME, ) in self.data:
                satellites.append( [ number, self.satelliteData[ number ].getName(), self.data[ key + ( astroPyephem.DATA_RISE_DATE_TIME, ) ] ] )

#TODO Not sure of the logic here...need to check!
        menuItem = None
        if self.satellitesSortByDateTime and satellites:
            satellites = sorted( satellites, key = lambda x: ( x[ 2 ], x[ 0 ], x[ 1 ] ) )
            menuItem = Gtk.MenuItem( _( "Satellites" ) )

        if self.satellitesSortByDateTime and satellitesCircumpolar:
            satellites = sorted( satellitesCircumpolar, key = lambda x: ( x[ 0 ], x[ 1 ] ) )
            menuItem = Gtk.MenuItem( _( "Satellites (Circumpolar)" ) )

        if not self.satellitesSortByDateTime and ( satellites or satellitesCircumpolar ):
            satellites = sorted( satellites + satellitesCircumpolar, key = lambda x: ( x[ 0 ], x[ 1 ] ) )
            menuItem = Gtk.MenuItem( _( "Satellites" ) )

        if menuItem is None: return #TODO Hack for when there are no satellites.
        menu.append( menuItem )  #TODO If no internet and no cache, then no satellites and the menuItem is never set so is uninitialised.

        theMenu = menu
        indent = 1
        theMenu = Gtk.Menu()
        menuItem.set_submenu( theMenu )
        indent = 0

#         print( "Number of satellites:", len(satellites))#TODO debug
        for number, name, riseDateTime in satellites:
            self.updateSatelliteMenu( theMenu, indent, number )


    def updateSatelliteMenu( self, menu, indent, satelliteNumber ):
        menuText = IndicatorLunar.SATELLITE_MENU_TEXT.replace( IndicatorLunar.SATELLITE_TAG_NAME, self.satelliteData[ satelliteNumber ].getName() ) \
                                                     .replace( IndicatorLunar.SATELLITE_TAG_NUMBER, satelliteNumber ) \
                                                     .replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satelliteData[ satelliteNumber ].getInternationalDesignator() )

        menuItem = Gtk.MenuItem( pythonutils.indent( indent, 1 ) + menuText ) #TODO Indent needs to be adjusted for GNOME Shell.
        menu.append( menuItem )

        subMenu = Gtk.Menu()
        menuItem.set_submenu( subMenu )

        key = ( astroPyephem.AstronomicalBodyType.Satellite, satelliteNumber )
        if key + ( astroPyephem.DATA_AZIMUTH, ) in self.data:
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astroPyephem.DATA_AZIMUTH, ) ) ) )
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Altitude: " ) + self.getDisplayData( key + ( astroPyephem.DATA_ALTITUDE, ) ) ) )

        elif key + ( astroPyephem.DATA_RISE_AZIMUTH, ) in self.data:
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Rise" ) ) )
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 1, 1 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astroPyephem.DATA_RISE_DATE_TIME, ) ) ) )
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 1, 1 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astroPyephem.DATA_RISE_AZIMUTH, ) ) ) )
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Set" ) ) )
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 1, 1 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astroPyephem.DATA_SET_DATE_TIME, ) ) ) )
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 1, 1 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astroPyephem.DATA_SET_AZIMUTH, ) ) ) )

        else:
            subMenu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Rise Date/Time: " ) + self.getDisplayData( key + ( astroPyephem.DATA_RISE_DATE_TIME, ) ) ) )

        # Add handler.
        for child in subMenu.get_children():
            child.set_name( satelliteNumber )
            child.connect( "activate", self.onSatellite )


#TODO Eventually see if this can be combined with the generical onclick function.  OR can it be a lamba thingy?
    def onSatellite( self, widget ):
        satelliteTLE = self.satelliteData.get( widget.props.name )

        url = IndicatorLunar.SATELLITE_ON_CLICK_URL. \
              replace( IndicatorLunar.SATELLITE_TAG_NAME, satelliteTLE.getName() ). \
              replace( IndicatorLunar.SATELLITE_TAG_NUMBER, satelliteTLE.getNumber() ). \
              replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, satelliteTLE.getInternationalDesignator() )

        webbrowser.open( url )


    def getDisplayData( self, key, dateTimeFormat = None ):
        displayData = None

        if key[ 2 ] == astroPyephem.DATA_ALTITUDE or \
           key[ 2 ] == astroPyephem.DATA_AZIMUTH or \
           key[ 2 ] == astroPyephem.DATA_RISE_AZIMUTH or \
           key[ 2 ] == astroPyephem.DATA_SET_AZIMUTH:
            displayData = str( round( math.degrees( float( self.data[ key ] ) ) ) ) + "°"

        elif key[ 2 ] == astroPyephem.DATA_ECLIPSE_DATE_TIME or \
             key[ 2 ] == astroPyephem.DATA_FIRST_QUARTER or \
             key[ 2 ] == astroPyephem.DATA_FULL or \
             key[ 2 ] == astroPyephem.DATA_NEW or \
             key[ 2 ] == astroPyephem.DATA_RISE_DATE_TIME or \
             key[ 2 ] == astroPyephem.DATA_SET_DATE_TIME or \
             key[ 2 ] == astroPyephem.DATA_THIRD_QUARTER:
                if dateTimeFormat is None:
                    displayData = self.toLocalDateTimeString( self.data[ key ], IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMM ).replace( ' ', '  ' ) #TODO Does the double space appear in Unity and GNOME Shell?
                else:
                    displayData = self.toLocalDateTimeString( self.data[ key ], dateTimeFormat ) #TODO Do we need to add the double space as above?

        elif key[ 2 ] == astroPyephem.DATA_ECLIPSE_LATITUDE:
            latitude = self.data[ key ]
            if latitude[ 0 ] == "-":
                displayData = latitude[ 1 : ] + "° " + _( "S" )
            else:
                displayData = latitude + "° " +_( "N" )

        elif key[ 2 ] == astroPyephem.DATA_ECLIPSE_LONGITUDE:
            longitude = self.data[ key ]
            if longitude[ 0 ] == "-":
                displayData = longitude[ 1 : ] + "° " + _( "E" )
            else:
                displayData = longitude + "° " +_( "W" )

        elif key[ 2 ] == astroPyephem.DATA_ECLIPSE_TYPE:
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

        elif key[ 2 ] == astroPyephem.DATA_PHASE:
            displayData = IndicatorLunar.LUNAR_PHASE_NAMES_TRANSLATIONS[ self.data[ key ] ]

        if displayData is None:
            displayData = "" # Better to show nothing and let None slip through and crash.
            logging.error( "Unknown key: " + key )

        return displayData


    # Converts a UTC datetime string to a local datetime string in the given format.
    def toLocalDateTimeString( self, utcDateTimeString, format ):
        utcDateTime = datetime.datetime.strptime( utcDateTimeString, astroPyephem.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )
        localDateTime = utcDateTime.replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None )
        return localDateTime.strftime( format )


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
        colour = pythonutils.getThemeColour( IndicatorLunar.ICON, logging )
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
                _( "changelog" ),
                IndicatorLunar.LOG,
                _( "View the" ),
                _( "text file." ),
                _( "error log" ) )

            self.dialogLock.release()


    def onPreferences( self, widget ):
        if self.dialogLock.acquire( blocking = False ):
            self._onPreferences( widget )
            self.dialogLock.release()


    def _onPreferences( self, widget ):
        TAB_ICON = 0
        TAB_MENU = 1
        TAB_PLANETS_STARS = 2
        TAB_COMETS_MINOR_PLANETS = 3
        TAB_SATELLITES = 4
        TAB_NOTIFICATIONS = 5
        TAB_GENERAL = 6

        notebook = Gtk.Notebook()

        # Icon.
        grid = pythonutils.createGrid()

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

#TODO Hopefully not needed!
        self.tagsAdded = { }
        self.tagsRemoved = { }

#TODO Now that we can drop a body if below the horizon, that body may appear/disappear from the table depending on time of day.
#The moon for example will drop in and out and so too will the tag.
#So maybe don't drop stuff out...and if something is checked (when not checked on creating the dialog), add that object in (with data tags).
        COLUMN_ASTRONOICAL_BODY_TYPE = 0
        COLUMN_TAG = 1
        COLUMN_TRANSLATED_TAG = 2
        COLUMN_VALUE = 3
        displayTagsStore = Gtk.ListStore( int, str, str, str ) # Astronomical body type, tag, translated tag, value.
        tags = re.split( "(\[[^\[^\]]+\])", self.indicatorText )
        for key in self.data.keys():
            if key[ 2 ] not in astroPyephem.DATA_INTERNAL:
                self.appendToDisplayTagsStore( key, self.getDisplayData( key ), displayTagsStore )
#TODO Need to handle satellite tags...
#When to remove the satellite name from the tag?  Here or at render time or when?
                tag = "[" + key[ 1 ] + " " + key[ 2 ] + "]"
                if tag in tags:
                    i = tags.index( tag )
                    tags[ i ] = ""

#TODO Not sure what is happening here?
# Are we stripping tags from the indicator text which no longer appear in the table?
# Maybe just leave the tags there and the user can manually remove after they see displayed?  Ask Oleg.
# Tried the text [DEF][MOON PHASE][ABC] and commented out the code below and the ABC/DEF tags did not appear in the final label.  Why?
#Maybe show the tags in the preferences always, but drop them when rendering?
#Before making changes consider what happens if we leave unknown tags here, but then at render time is that an issue?
#Not sure what to do now...
# Leave tags in here, but what if a user has added in there own tags...can they do that?
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
        grid = pythonutils.createGrid()

        hideBodiesBelowTheHorizonCheckbox = Gtk.CheckButton( _( "Hide bodies below the horizon" ) )
        hideBodiesBelowTheHorizonCheckbox.set_active( self.hideBodiesBelowHorizon )
        hideBodiesBelowTheHorizonCheckbox.set_tooltip_text( _( "If checked, all bodies below the horizon are hidden." ) )
        grid.attach( hideBodiesBelowTheHorizonCheckbox, 0, 0, 1, 1 )

        cometsAddNewCheckbox = Gtk.CheckButton( _( "Add new comets" ) )
        cometsAddNewCheckbox.set_margin_top( 10 )
        cometsAddNewCheckbox.set_active( self.cometsAddNew )
        cometsAddNewCheckbox.set_tooltip_text( _(
            "If checked, all comets are added\n" + \
            "to the list of checked comets." ) )
        grid.attach( cometsAddNewCheckbox, 0, 1, 1, 1 )

        minorPlanetsAddNewCheckbox = Gtk.CheckButton( _( "Add new minor planets" ) )
        minorPlanetsAddNewCheckbox.set_margin_top( 10 )
        minorPlanetsAddNewCheckbox.set_active( self.minorPlanetsAddNew )
        minorPlanetsAddNewCheckbox.set_tooltip_text( _(
            "If checked, all minor planets are added\n" + \
            "to the list of checked minor planets." ) )
        grid.attach( minorPlanetsAddNewCheckbox, 0, 2, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Hide comets and minor planets greater than magnitude" ) ), False, False, 0 )

        spinnerMagnitude = Gtk.SpinButton()
        spinnerMagnitude.set_numeric( True )
        spinnerMagnitude.set_update_policy( Gtk.SpinButtonUpdatePolicy.IF_VALID )
        spinnerMagnitude.set_adjustment( Gtk.Adjustment( self.magnitude, int( astroPyephem.MAGNITUDE_MINIMUM ), int( astroPyephem.MAGNITUDE_MAXIMUM ), 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerMagnitude.set_value( self.magnitude ) # ...so need to force the initial value by explicitly setting it.
        spinnerMagnitude.set_tooltip_text( _(
            "Comets and minor planets with a magnitude\n" + \
            "greater than that specified are hidden." ) )

        box.pack_start( spinnerMagnitude, False, False, 0 )
        grid.attach( box, 0, 3, 1, 1 )

#TODO Ensure this checkbox and that for comets/minorplanets have a listener that checks/unchecks the tables of comets/minorplanets/sats.
        satellitesAddNewCheckbox = Gtk.CheckButton( _( "Add new satellites" ) )
        satellitesAddNewCheckbox.set_margin_top( 10 )
        satellitesAddNewCheckbox.set_active( self.satellitesAddNew )
        satellitesAddNewCheckbox.set_tooltip_text( _(
            "If checked all satellites are added\n" + \
            "to the list of checked satellites." ) )
        grid.attach( satellitesAddNewCheckbox, 0, 4, 1, 1 )

        sortSatellitesByDateTimeCheckbox = Gtk.CheckButton( _( "Sort satellites by rise date/time" ) )
        sortSatellitesByDateTimeCheckbox.set_margin_top( 10 )
        sortSatellitesByDateTimeCheckbox.set_active( self.satellitesSortByDateTime )
        sortSatellitesByDateTimeCheckbox.set_tooltip_text( _(
            "If checked, satellites are sorted\n" + \
            "by rise date/time.\n\n" + \
            "Otherwise satellites are sorted\n" + \
            "by Name, Number and then\n" + \
            "International Designator." ) )
        grid.attach( sortSatellitesByDateTimeCheckbox, 0, 5, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Menu" ) ) )

        # Planets/Stars.
        box = Gtk.Box( spacing = 20 )

        planetStore = Gtk.ListStore( bool, str, str ) # Show/hide, planet name (not displayed), translated planet name.
        for planetName in astroPyephem.PLANETS:
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
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, planetStore, None, displayTagsStore, astroPyephem.AstronomicalBodyType.Planet )
        tree.append_column( treeViewColumn )

        tree.append_column( Gtk.TreeViewColumn( _( "Planet" ), Gtk.CellRendererText(), text = 2 ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER )
        scrolledWindow.add( tree )

        box.pack_start( scrolledWindow, True, True, 0 )

        stars = [ ] # List of lists, each sublist containing star is checked flag, star name, star translated name.
        for starName in IndicatorLunar.STAR_NAMES_TRANSLATIONS.keys():
            stars.append( [ starName in self.stars, starName, IndicatorLunar.STAR_NAMES_TRANSLATIONS[ starName ] ] )

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
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, starStore, starStoreSort, astroPyephem.AstronomicalBodyType.Star )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, starStore, starStoreSort, displayTagsStore, astroPyephem.AstronomicalBodyType.Star )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Star" ), Gtk.CellRendererText(), text = 2 )
        treeViewColumn.set_sort_column_id( 2 )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        box.pack_start( scrolledWindow, True, True, 0 )

        notebook.append_page( box, Gtk.Label( _( "Planets / Stars" ) ) )


#TODO For each of comets, minor planets and satellites, check if the underlying data (tle/oe) is empty or not.  
# If empty, don't show the table but a label with message instead.
#May need to have individual variable names for each of the scrolledWindows to hide/show.
# Or maybe show only the items the user previously selected.
        # Comets.
        box = Gtk.Box( spacing = 20 )

        cometStore = Gtk.ListStore( bool, str ) # Show/hide, comet name.
        for comet in self.cometData:
            cometStore.append( ( comet in self.comets, comet ) )

        cometStoreSort = Gtk.TreeModelSort( model = cometStore )
        cometStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( cometStoreSort )
        tree.set_tooltip_text( _(
            "Check a comet to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, cometStore, cometStoreSort, astroPyephem.AstronomicalBodyType.Comet )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, cometStore, cometStoreSort, displayTagsStore, astroPyephem.AstronomicalBodyType.Comet )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Comet" ), Gtk.CellRendererText(), text = 1 )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( tree )

        box.pack_start( scrolledWindow, True, True, 0 )

        minorPlanetStore = Gtk.ListStore( bool, str ) # Show/hide, minor planet name.
        for minorPlanet in self.minorPlanetData:
            minorPlanetStore.append( ( minorPlanet in self.minorPlanets, minorPlanet ) )

        minorPlanetStoreSort = Gtk.TreeModelSort( model = minorPlanetStore )
        minorPlanetStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( minorPlanetStoreSort )
        tree.set_tooltip_text( _(
            "Check a minor planet to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, minorPlanetStore, minorPlanetStoreSort, astroPyephem.AstronomicalBodyType.MinorPlanet)
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, minorPlanetStore, minorPlanetStoreSort, displayTagsStore, astroPyephem.AstronomicalBodyType.MinorPlanet )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Minor Planet" ), Gtk.CellRendererText(), text = 1 )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( tree )

        box.pack_start( scrolledWindow, True, True, 0 )

        notebook.append_page( box, Gtk.Label( _( "Comets / Minor Planets" ) ) )

        # Satellites.
        box = Gtk.Box()

        satelliteStore = Gtk.ListStore( bool, str, str, str ) # Show/hide, name, number, international designator.
        for satellite in self.satelliteData:
            satelliteStore.append( ( satellite in self.satellites, self.satelliteData[ satellite ].getName(), satellite, self.satelliteData[ satellite ].getInternationalDesignator() ) )

        satelliteStoreSort = Gtk.TreeModelSort( model = satelliteStore )
        satelliteStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( satelliteStoreSort )
        tree.set_tooltip_text( _(
            "Check a satellite to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, satelliteStore, satelliteStoreSort, astroPyephem.AstronomicalBodyType.Satellite )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, satelliteStore, satelliteStoreSort, displayTagsStore, astroPyephem.AstronomicalBodyType.Satellite )
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
        box.pack_start( scrolledWindow, True, True, 0 )

        notebook.append_page( box, Gtk.Label( _( "Satellites" ) ) )

        # OSD (satellite and full moon).
        notifyOSDInformation = _( "For formatting, refer to https://wiki.ubuntu.com/NotifyOSD" )

        grid = pythonutils.createGrid()

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

        label = Gtk.Label( _( "Message" ) + "\n \n \n \n \n " ) #TODO Add comment  
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

        test = Gtk.Button( _( "Test" ) )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        test.connect( "clicked", self.onTestNotificationClicked, satelliteNotificationSummaryText, satelliteNotificationMessageText, False )
        test.set_tooltip_text( _(
            "Show the notification bubble.\n" + \
            "Tags will be substituted with\n" + \
            "mock text." ) )
        grid.attach( test, 0, 3, 1, 1 )

        showSatelliteNotificationCheckbox.connect( "toggled", pythonutils.onCheckbox, test, test )

        showWerewolfWarningCheckbox = Gtk.CheckButton( _( "Werewolf warning" ) )
        showWerewolfWarningCheckbox.set_margin_top( 10 )
        showWerewolfWarningCheckbox.set_active( self.showWerewolfWarning )
        showWerewolfWarningCheckbox.set_tooltip_text( _(
            "Hourly screen notification leading up to full moon." ) )
        grid.attach( showWerewolfWarningCheckbox, 0, 4, 1, 1 )

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
        grid.attach( box, 0, 5, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, label, werewolfNotificationSummaryText )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( pythonutils.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Message" ) + "\n \n " )#TODO Add comment   
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
        grid.attach( box, 0, 6, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, label, werewolfNotificationMessageText )

        test = Gtk.Button( _( "Test" ) )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        test.connect( "clicked", self.onTestNotificationClicked, werewolfNotificationSummaryText, werewolfNotificationMessageText, True )
        test.set_tooltip_text( _( "Show the notification using the current summary/message." ) )
        grid.attach( test, 0, 7, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", pythonutils.onCheckbox, test, test )

        notebook.append_page( grid, Gtk.Label( _( "Notifications" ) ) )

        # Location.
        grid = pythonutils.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "City" ) ), False, False, 0 )

        city = Gtk.ComboBoxText.new_with_entry()
        city.set_tooltip_text( _(
            "Choose a city from the list.\n" + \
            "Or, add in your own city name." ) )

        cities = astroPyephem.getCities()
        if self.city not in cities:
            cities.append( self.city )
            cities = sorted( cities, key = locale.strxfrm )

        for c in cities:
            city.append_text( c )

        box.pack_start( city, False, False, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Latitude" ) ), False, False, 0 )

        latitude = Gtk.Entry()
        latitude.set_tooltip_text( _( "Latitude of your location in decimal degrees." ) )
        box.pack_start( latitude, False, False, 0 )
        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Longitude" ) ), False, False, 0 )

        longitude = Gtk.Entry()
        longitude.set_tooltip_text( _( "Longitude of your location in decimal degrees." ) )
        box.pack_start( longitude, False, False, 0 )
        grid.attach( box, 0, 2, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "Elevation" ) ), False, False, 0 )

        elevation = Gtk.Entry()
        elevation.set_tooltip_text( _( "Height in metres above sea level." ) )
        box.pack_start( elevation, False, False, 0 )
        grid.attach( box, 0, 3, 1, 1 )

        city.connect( "changed", self.onCityChanged, latitude, longitude, elevation )
        city.set_active( cities.index( self.city ) )

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

#TODO If a satellite is added, do we remove the satellite name here, 
# or save it and remove it when displayed (displayed in the Preferences and displayed in the final label)?
#             self.indicatorText = self.translateTags( displayTagsStore, False, indicatorText.get_text() )
            self.hideBodiesBelowHorizon = hideBodiesBelowTheHorizonCheckbox.get_active()
            self.magnitude = spinnerMagnitude.get_value_as_int()
            self.cometsAddNew = cometsAddNewCheckbox.get_active()
            self.minorPlanetsAddNew = minorPlanetsAddNewCheckbox.get_active()
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

#TODO Needed if we already do this in the update?
#             self.comets = [ ]
#             if not self.cometsAddNew:
#                 for comet in cometStore:
#                     if comet[ 0 ]:
#                         self.comets.append( comet[ 1 ].upper() )
# 
#             self.minorPlanets = [ ]
#             if not self.minorPlanetsAddNew:
#                 for minorPlanet in minorPlanetStore:
#                     if minorPlanet[ 0 ]:
#                         self.minorPlanets.append( minorPlanet[ 1 ].upper() )
# 
#             self.satellites = [ ]
#             if not self.satellitesAddNew:
#                 for satellite in satelliteStore:
#                     if satellite[ 0 ]:
#                         self.satellites.append( satellite[ 2 ] )

            self.showSatelliteNotification = showSatelliteNotificationCheckbox.get_active()
            self.satelliteNotificationSummary = self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, False, satelliteNotificationSummaryText.get_text() )
            self.satelliteNotificationMessage = self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, False, pythonutils.getTextViewText( satelliteNotificationMessageText ) )

            self.showWerewolfWarning = showWerewolfWarningCheckbox.get_active()
            self.werewolfWarningSummary = werewolfNotificationSummaryText.get_text()
            self.werewolfWarningMessage = pythonutils.getTextViewText( werewolfNotificationMessageText )

            self.city = cityValue
            self.latitude = float( latitudeValue )
            self.longitude = float( longitudeValue )
            self.elevation = float( elevationValue )

            self.saveConfig()
            pythonutils.setAutoStart( IndicatorLunar.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            GLib.idle_add( self.update, False )
            break

        dialog.destroy()


    def appendToDisplayTagsStore( self, key, value, displayTagsStore ):
        astronomicalBodyType = key[ 0 ]
        bodyTag = key[ 1 ]
        dataTag = key[ 2 ]

        if astronomicalBodyType == astroPyephem.AstronomicalBodyType.Comet or \
           astronomicalBodyType == astroPyephem.AstronomicalBodyType.MinorPlanet: # Don't translate the names of comets or minor planets.
            translatedTag = bodyTag + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ]

        elif astronomicalBodyType == astroPyephem.AstronomicalBodyType.Satellite: # Don't translate names and add in satellite name/designator.
            satelliteName = self.satelliteData[ bodyTag ].getName()
#             satelliteInternationalDesignator = self.satelliteData[ satelliteNumber ].getInternationalDesignator() #TODO NOt sure if we need this.
            translatedTag = satelliteName + " " + bodyTag + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ]

        else:
            translatedTag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ bodyTag ] + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ] # Translate names of planets and stars.

        displayTagsStore.append( [ astronomicalBodyType, bodyTag + " " + dataTag, translatedTag, value ] )


    def translateTags( self, tagsStore, originalToLocal, text ):
        # The tags store contains at least 2 columns (additional columns are ignored).
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


    def onPlanetToggled( self, widget, row, dataStore ):
        dataStore[ row ][ 0 ] = not dataStore[ row ][ 0 ]
        self.checkboxToggled( dataStore[ row ][ 1 ].upper(), astroPyephem.AstronomicalBodyType.Planet, dataStore[ row ][ 0 ] )
        planetName = dataStore[ row ][ 1 ]


#TODO Include MP
#TODO Rename to table toggled or similar?
    def onCometStarSatelliteToggled( self, widget, row, dataStore, sortStore, astronomicalBodyType ):
        actualRow = sortStore.convert_path_to_child_path( Gtk.TreePath.new_from_string( row ) ) # Convert sorted model index to underlying (child) model index.
        dataStore[ actualRow ][ 0 ] = not dataStore[ actualRow ][ 0 ]
        if astronomicalBodyType == astroPyephem.AstronomicalBodyType.Comet:
            bodyTag = dataStore[ actualRow ][ 1 ].upper()
        if astronomicalBodyType == astroPyephem.AstronomicalBodyType.Satellite:
            bodyTag = dataStore[ actualRow ][ 1 ] + " " + dataStore[ actualRow ][ 2 ]
        else: # Assume star.
            bodyTag = dataStore[ actualRow ][ 1 ].upper()

        self.checkboxToggled( bodyTag, astronomicalBodyType, dataStore[ actualRow ][ 0 ] )


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


#TODO When we decide whether to uncheck all or check all, initialise the flag variable in such a way 
# that if all satellites for example are initially checked, then the next click should uncheck all.
#If no satellites are checked, the first click should check all.
#If one or more satellites are checked, the first click should check all.
# Ditto for planets, stars, comets and minor planets.
    def onColumnHeaderClick( self, widget, dataStore, sortStore, displayTagsStore, astronomicalBodyType ):
        if astronomicalBodyType == astroPyephem.AstronomicalBodyType.Planet:
            toggle = self.togglePlanetsTable
            self.togglePlanetsTable = not self.togglePlanetsTable
            for row in range( len( dataStore ) ):
                dataStore[ row ][ 0 ] = bool( not toggle )
                self.onPlanetToggled( widget, row, dataStore )

        elif astronomicalBodyType == astroPyephem.AstronomicalBodyType.Comet or \
             astronomicalBodyType == astroPyephem.AstronomicalBodyType.MinorPlanet or \
             astronomicalBodyType == astroPyephem.AstronomicalBodyType.Satellite or \
             astronomicalBodyType == astroPyephem.AstronomicalBodyType.Star:
            if astronomicalBodyType == astroPyephem.AstronomicalBodyType.Comet:
                toggle = self.toggleCometsTable
                self.toggleCometsTable = not self.toggleCometsTable
            elif astronomicalBodyType == astroPyephem.AstronomicalBodyType.MinorPlanet:
                toggle = self.toggleMinorPlanetsTable
                self.toggleMinorPlanetsTable = not self.toggleMinorPlanetsTable
            elif astronomicalBodyType == astroPyephem.AstronomicalBodyType.Satellite:
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
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.toLocalDateTimeString( utcNow, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION, self.toLocalDateTimeString( utcNowPlusTenMinutes, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) )

            message = message. \
                replace( IndicatorLunar.SATELLITE_TAG_NAME_TRANSLATION, "ISS (ZARYA)" ). \
                replace( IndicatorLunar.SATELLITE_TAG_NUMBER_TRANSLATION, "25544" ). \
                replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION, "1998-067A" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION, "123°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.toLocalDateTimeString( utcNow, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION, self.toLocalDateTimeString( utcNowPlusTenMinutes, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) )

        if summary == "":
            summary = " " # The notification summary text must not be empty (at least on Unity).

        Notify.Notification.new( summary, message, svgFile ).show()

        if isFullMoon:
            os.remove( svgFile )


    def onCityChanged( self, combobox, latitude, longitude, elevation ):
        city = combobox.get_active_text()

#TODO Can the city ever be empty?  So do we need the check below?
        if city != "" and city in astroPyephem.getCities(): # Populate the latitude/longitude/elevation if the city exists, otherwise let the user specify.
            theLatitude, theLongitude, theElevation = astroPyephem.getLatitudeLongitudeElevation( city )
            latitude.set_text( str( theLatitude ) )
            longitude.set_text( str( theLongitude ) )
            elevation.set_text( str( theElevation ) )


#TODO Why not just clear the display tags store and just add stuff as needed?
# Is the code below that much faster than simply clear all and add?
#If we wait until we switch to the first tab to update the table, then need a handle to all the UI elements to poll each of them.
#Maybe pass in lists of elements (list of checkboxes, list of tables/stores, etc)?
    def onSwitchPage( self, notebook, page, pageNumber, displayTagsStore ):
        if True: return
        if pageNumber == 0: # User has clicked the first tab.
            displayTagsStore.clear() # List of lists, each sublist contains the tag, translated tag, value.

            # Only add tags for data which has not been removed.
            for key in self.data.keys():

                astronomicalBodyType = key[ 0 ]
                bodyTag = key[ 1 ]

                if ( astronomicalBodyType, bodyTag ) not in self.tagsRemoved and \
                   ( astronomicalBodyType, bodyTag ) not in self.tagsAdded:
                    self.appendToDisplayTagsStore( key, self.getDisplayData( key ), displayTagsStore )

            # Add tags for newly checked items (duplicates have been avoided by the above code).
            for key in self.tagsAdded:
                astronomicalBodyType = key[ 0 ]
                bodyTag = key[ 1 ]
                if astronomicalBodyType == astroPyephem.AstronomicalBodyType.Comet:
                    tags = IndicatorLunar.DATA_TAGS_COMET
                if astronomicalBodyType == astroPyephem.AstronomicalBodyType.MinorPlanet:
                    tags = IndicatorLunar.DATA_TAGS_MINOR_PLANET
                elif astronomicalBodyType == astroPyephem.AstronomicalBodyType.Moon:
                    tags = IndicatorLunar.DATA_TAGS_MOON
                elif astronomicalBodyType == astroPyephem.AstronomicalBodyType.Planet:
                    tags = IndicatorLunar.DATA_TAGS_PLANET
                elif astronomicalBodyType == astroPyephem.AstronomicalBodyType.Satellite:
                    tags = IndicatorLunar.DATA_TAGS_SATELLITE
                elif astronomicalBodyType == astroPyephem.AstronomicalBodyType.Star:
                    tags = IndicatorLunar.DATA_TAGS_STAR
                elif astronomicalBodyType == astroPyephem.AstronomicalBodyType.Sun:
                    tags = IndicatorLunar.DATA_TAGS_SUN

                for tag in tags:
                    self.appendToDisplayTagsStore( key + ( tag, ), IndicatorLunar.MESSAGE_DISPLAY_NEEDS_REFRESH, displayTagsStore )


    def addNewBodies( self, data, bodies ):
        for body in data:
            if body not in bodies:
                bodies.append( body )


    def getDefaultCity( self ):
        try:
            timezone = pythonutils.processGet( "cat /etc/timezone" )
            theCity = None
            cities = astroPyephem.getCities()
            for city in cities:
                if city in timezone:
                    theCity = city
                    break

            if theCity is None or not theCity:
                theCity = cities[ 0 ]

        except Exception as e:
            logging.exception( e )
            logging.error( "Error getting default city." )
            theCity = cities[ 0 ]

        return theCity


    def loadConfig( self ):
        config = pythonutils.loadConfig( INDICATOR_NAME, INDICATOR_NAME, logging )

        self.city = config.get( IndicatorLunar.CONFIG_CITY_NAME ) # Returns None if the key is not found.
        if self.city is None:
            self.city = self.getDefaultCity()
            self.latitude, self.longitude, self.elevation = astroPyephem.getLatitudeLongitudeElevation( self.city )
        else:
            self.elevation = config.get( IndicatorLunar.CONFIG_CITY_ELEVATION )
            self.latitude = config.get( IndicatorLunar.CONFIG_CITY_LATITUDE )
            self.longitude = config.get( IndicatorLunar.CONFIG_CITY_LONGITUDE )

        self.comets = config.get( IndicatorLunar.CONFIG_COMETS, [ ] )
        self.cometsAddNew = config.get( IndicatorLunar.CONFIG_COMETS_ADD_NEW, False )

        self.hideBodiesBelowHorizon = config.get( IndicatorLunar.CONFIG_HIDE_BODIES_BELOW_HORIZON, True )

        self.indicatorText = config.get( IndicatorLunar.CONFIG_INDICATOR_TEXT, IndicatorLunar.INDICATOR_TEXT_DEFAULT )

        self.minorPlanets = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS, [ ] )
        self.minorPlanetsAddNew = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS_ADD_NEW, False )

        self.magnitude = config.get( IndicatorLunar.CONFIG_MAGNITUDE, 6 ) # More or less what's visible with the naked eye or binoculars.

        self.planets = config.get( IndicatorLunar.CONFIG_PLANETS, astroPyephem.PLANETS[ : 6 ] ) # Drop Neptune and Pluto as not visible with naked eye.

        self.satelliteNotificationMessage = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE, IndicatorLunar.SATELLITE_NOTIFICATION_MESSAGE_DEFAULT )
        self.satelliteNotificationSummary = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY, IndicatorLunar.SATELLITE_NOTIFICATION_SUMMARY_DEFAULT )
        self.satellites = config.get( IndicatorLunar.CONFIG_SATELLITES, [ ] )
        self.satellitesAddNew = config.get( IndicatorLunar.CONFIG_SATELLITES_ADD_NEW, False )
        self.satellitesSortByDateTime = config.get( IndicatorLunar.CONFIG_SATELLITES_SORT_BY_DATE_TIME, True )

        self.showSatelliteNotification = config.get( IndicatorLunar.CONFIG_SHOW_SATELLITE_NOTIFICATION, False )
        self.showWerewolfWarning = config.get( IndicatorLunar.CONFIG_SHOW_WEREWOLF_WARNING, True )

        self.stars = config.get( IndicatorLunar.CONFIG_STARS, [ ] )

        self.werewolfWarningMessage = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE, IndicatorLunar.WEREWOLF_WARNING_MESSAGE_DEFAULT )
        self.werewolfWarningSummary = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY, IndicatorLunar.WEREWOLF_WARNING_SUMMARY_DEFAULT )

#TODO Start of temporary hack...
# Convert lat/long from str to float.
# Convert planet/star to upper case.
# Convert satellites from list of lists of tuple of satellite name and satellite number to list of satellite numbers.
# Remove this hack in release 82 or later.
        self.latitude = float( self.latitude )
        self.longitude = float( self.longitude )

        tmp = [ ]
        for planet in self.planets:
            tmp.append( planet.upper() )
        self.planets = tmp

        tmp = [ ]
        for star in self.stars:
            tmp.append( star.upper() )
        self.stars = tmp

        if self.satellites:
            if isinstance( self.satellites[ 0 ], list ):
                tmp = [ ]
                for satelliteInfo in self.satellites:
                    tmp.append( satelliteInfo[ 1 ] )

                self.satellites = tmp

        self.saveConfig()
# End of hack!


    def saveConfig( self ):
        if self.cometsAddNew:
            comets = [ ]
        else:
            comets = self.comets # Only write out the list of comets if the user elects to not add new.

        if self.minorPlanetsAddNew:
            minorPlanets = [ ]
        else:
            minorPlanets = self.minorPlanets # Only write out the list of minor planets if the user elects to not add new.

        if self.satellitesAddNew:
            satellites = [ ]
        else:
            satellites = self.satellites # Only write out the list of satellites if the user elects to not add new.

        config = {
            IndicatorLunar.CONFIG_CITY_ELEVATION: self.elevation,
            IndicatorLunar.CONFIG_CITY_LATITUDE: self.latitude,
            IndicatorLunar.CONFIG_CITY_LONGITUDE: self.longitude,
            IndicatorLunar.CONFIG_CITY_NAME: self.city,
            IndicatorLunar.CONFIG_COMETS: comets,
            IndicatorLunar.CONFIG_COMETS_ADD_NEW: self.cometsAddNew,
            IndicatorLunar.CONFIG_HIDE_BODIES_BELOW_HORIZON: self.hideBodiesBelowHorizon,
            IndicatorLunar.CONFIG_INDICATOR_TEXT: self.indicatorText,
            IndicatorLunar.CONFIG_MINOR_PLANETS: minorPlanets,
            IndicatorLunar.CONFIG_MINOR_PLANETS_ADD_NEW: self.minorPlanetsAddNew,
            IndicatorLunar.CONFIG_MAGNITUDE: self.magnitude,
            IndicatorLunar.CONFIG_PLANETS: self.planets,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE: self.satelliteNotificationMessage,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY: self.satelliteNotificationSummary,
            IndicatorLunar.CONFIG_SATELLITES: satellites,
            IndicatorLunar.CONFIG_SATELLITES_ADD_NEW: self.satellitesAddNew,
            IndicatorLunar.CONFIG_SATELLITES_SORT_BY_DATE_TIME: self.satellitesSortByDateTime,
            IndicatorLunar.CONFIG_SHOW_SATELLITE_NOTIFICATION: self.showSatelliteNotification,
            IndicatorLunar.CONFIG_SHOW_WEREWOLF_WARNING: self.showWerewolfWarning,
            IndicatorLunar.CONFIG_STARS: self.stars,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE: self.werewolfWarningMessage,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY: self.werewolfWarningSummary
        }

        pythonutils.saveConfig( config, INDICATOR_NAME, INDICATOR_NAME, logging )


if __name__ == "__main__": IndicatorLunar().main()