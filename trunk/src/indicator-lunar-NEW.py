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
#MPC responded and they are looking into it.
#
#However given that all other bodies either have a fixed magnitude or none,
# then comets are the only body with a magnitude that we care about.
#Further, if we add minor planets (also from the MPC), then the magnitude problem could get even worse.
#So we could show an OSD when the indicator starts up telling the user of bad mags,
#but we could either show the mag with the comet and/or just in the data list in the preferences.

#TODO Maybe show other stuff for comets?
# https://www.minorplanetcenter.net/iau/Ephemerides/Soft03.html
# But this means changing to the name orbital elements...or maybe leaving comets as is and add a new thing for OE?
# Maybe rename to OE as it catches all (and they are treated identically by PyEphem).
# By extension, allow for multiple URLs for the OEs (see the URL above)?  ... and ditto for satellites?
# https://www.minorplanetcenter.net/iau/Ephemerides/Soft03.html
# Have added in some of the extra MPC data files and found that there are a ton of new visible OEs.
# These could have dodgy magnitudes, as warned on the MPC site...
#...so maybe need some way to flag to the user magnitudes greater than the moon?
# Maybe put in a special subgroup?
# Use the OSD?


#TODO If we want to have multiple source data files for comets (now OEs), then need to maybe also allow this for satellites too.
# COuld do a couple of ways...
# 1) Have a radio button on each of the satellite/comets tabs: one for default data file and one which enables the 
# text field to let the user add ONE text file (so the multiple files by default are hidden from the user).
# Don't like hiding the information from the user.
# 2) Have a button which brings up a text box dialog, not text field, to let a multiline entry,
# so we can have multiple URLs.
# Use a Gtk.TextView?  https://python-gtk-3-tutorial.readthedocs.io/en/latest/gallery.html

#TODO The minor planets file takes a while to load...
#Check if it takes a while to load on startup.
#Check when preferences startup...maybe show teh prefs dialog but make it opaque with a message?
#The toggle to select all takes a while, so maybe remove from comets/sats/minp?


INDICATOR_NAME = "indicator-lunar"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "AppIndicator3", "0.1" )
gi.require_version( "Notify", "0.7" )

from gi.repository import AppIndicator3, GLib, Gtk, Notify
from urllib.request import urlopen
import astro, calendar, datetime, eclipse, glob, locale, logging, math, os, pythonutils, re, satellite, tempfile, threading, webbrowser


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
    ABOUT_CREDIT_COMET = _( "Comet OE data by Minor Planet Center. http://www.minorplanetcenter.net" ) #TODO Add a whole new line for minor planets or add to this line.
    ABOUT_CREDIT_SATELLITE = _( "Satellite TLE data by Dr T S Kelso. http://www.celestrak.com" )
    ABOUT_CREDITS = [ ABOUT_CREDIT_PYEPHEM, ABOUT_CREDIT_ECLIPSE, ABOUT_CREDIT_SATELLITE, ABOUT_CREDIT_COMET ]

    DATE_TIME_FORMAT_HHcolonMMcolonSS = "%H:%M:%S"
    DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS = "%Y-%m-%d %H:%M:%S"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSSdotFLOAT = "%Y-%m-%d %H:%M:%S.%f"

    CONFIG_CITY_ELEVATION = "cityElevation"
    CONFIG_CITY_LATITUDE = "cityLatitude"
    CONFIG_CITY_LONGITUDE = "cityLongitude"
    CONFIG_CITY_NAME = "city"
    CONFIG_COMET_OE_URL = "cometOEURL"
    CONFIG_COMETS = "comets"
    CONFIG_COMETS_ADD_NEW = "cometsAddNew"
    CONFIG_MAGNITUDE = "magnitude"
    CONFIG_MINOR_PLANET_OE_URL = "minorPlanetOEURL"
    CONFIG_MINOR_PLANETS = "minorPlanets"
    CONFIG_MINOR_PLANETS_ADD_NEW = "minorPlanetsAddNew"
    CONFIG_INDICATOR_TEXT = "indicatorText"
    CONFIG_PLANETS = "planets"
    CONFIG_SATELLITE_NOTIFICATION_MESSAGE = "satelliteNotificationMessage"
    CONFIG_SATELLITE_NOTIFICATION_SUMMARY = "satelliteNotificationSummary"
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
    CONFIG_WEREWOLF_WARNING_MESSAGE = "werewolfWarningMessage"
    CONFIG_WEREWOLF_WARNING_SUMMARY = "werewolfWarningSummary"

    DATA_TAGS_TRANSLATIONS = {
        astro.DATA_ALTITUDE             : _( "ALTITUDE" ),
        astro.DATA_AZIMUTH              : _( "AZIMUTH" ),
        astro.DATA_DAWN                 : _( "DAWN" ),
        astro.DATA_DUSK                 : _( "DUSK" ),
        astro.DATA_ECLIPSE_DATE_TIME    : _( "ECLIPSE DATE TIME" ),
        astro.DATA_ECLIPSE_LATITUDE     : _( "ECLIPSE LATITUDE" ),
        astro.DATA_ECLIPSE_LONGITUDE    : _( "ECLIPSE LONGITUDE" ),
        astro.DATA_ECLIPSE_TYPE         : _( "ECLIPSE TYPE" ),
        astro.DATA_FIRST_QUARTER        : _( "FIRST QUARTER" ),
        astro.DATA_FULL                 : _( "FULL" ),
        astro.DATA_MESSAGE              : _( "MESSAGE" ),
        astro.DATA_NEW                  : _( "NEW" ),
        astro.DATA_PHASE                : _( "PHASE" ),
        astro.DATA_RISE_AZIMUTH         : _( "RISE AZIMUTH" ),
        astro.DATA_RISE_TIME            : _( "RISE TIME" ),
        astro.DATA_SET_AZIMUTH          : _( "SET AZIMUTH" ),
        astro.DATA_SET_TIME             : _( "SET TIME" ),
        astro.DATA_THIRD_QUARTER        : _( "THIRD QUARTER" ) }

    CITY_TAG_TRANSLATION = { astro.NAME_TAG_CITY: _( "CITY" ) }
    MOON_TAG_TRANSLATION = { astro.NAME_TAG_MOON : _( "MOON" ) }
    SUN_TAG_TRANSLATION = { astro.NAME_TAG_SUN : _( "SUN" ) }

    PLANET_NAMES_TRANSLATIONS = {
        astro.PLANET_MERCURY    : _( "Mercury" ),
        astro.PLANET_VENUS      : _( "Venus" ),
        astro.PLANET_MARS       : _( "Mars" ),
        astro.PLANET_JUPITER    : _( "Jupiter" ),
        astro.PLANET_SATURN     : _( "Saturn" ),
        astro.PLANET_URANUS     : _( "Uranus" ),
        astro.PLANET_NEPTUNE    : _( "Neptune" ),
        astro.PLANET_PLUTO      : _( "Pluto" ) }

    PLANET_TAGS_TRANSLATIONS = {
        astro.PLANET_MERCURY    : _( "MERCURY" ),
        astro.PLANET_VENUS      : _( "VENUS" ),
        astro.PLANET_MARS       : _( "MARS" ),
        astro.PLANET_JUPITER    : _( "JUPITER" ),
        astro.PLANET_SATURN     : _( "SATURN" ),
        astro.PLANET_URANUS     : _( "URANUS" ),
        astro.PLANET_NEPTUNE    : _( "NEPTUNE" ),
        astro.PLANET_PLUTO      : _( "PLUTO" ) }

    STAR_NAMES_TRANSLATIONS = {
        astro.STARS[ 0 ]    : _( "Achernar" ),
        astro.STARS[ 1 ]    : _( "Adara" ),
        astro.STARS[ 2 ]    : _( "Agena" ),
        astro.STARS[ 3 ]    : _( "Albereo" ),
        astro.STARS[ 4 ]    : _( "Alcaid" ),
        astro.STARS[ 5 ]    : _( "Alcor" ),
        astro.STARS[ 6 ]    : _( "Alcyone" ),
        astro.STARS[ 7 ]    : _( "Aldebaran" ),
        astro.STARS[ 8 ]    : _( "Alderamin" ),
        astro.STARS[ 9 ]    : _( "Alfirk" ),
        astro.STARS[ 10 ]   : _( "Algenib" ),
        astro.STARS[ 11 ]   : _( "Algieba" ),
        astro.STARS[ 12 ]   : _( "Algol" ),
        astro.STARS[ 13 ]   : _( "Alhena" ),
        astro.STARS[ 14 ]   : _( "Alioth" ),
        astro.STARS[ 15 ]   : _( "Almach" ),
        astro.STARS[ 16 ]   : _( "Alnair" ),
        astro.STARS[ 17 ]   : _( "Alnilam" ),
        astro.STARS[ 18 ]   : _( "Alnitak" ),
        astro.STARS[ 19 ]   : _( "Alphard" ),
        astro.STARS[ 20 ]   : _( "Alphecca" ),
        astro.STARS[ 21 ]   : _( "Alshain" ),
        astro.STARS[ 22 ]   : _( "Altair" ),
        astro.STARS[ 23 ]   : _( "Antares" ),
        astro.STARS[ 24 ]   : _( "Arcturus" ),
        astro.STARS[ 25 ]   : _( "Arkab Posterior" ),
        astro.STARS[ 26 ]   : _( "Arkab Prior" ),
        astro.STARS[ 27 ]   : _( "Arneb" ),
        astro.STARS[ 28 ]   : _( "Atlas" ),
        astro.STARS[ 29 ]   : _( "Bellatrix" ),
        astro.STARS[ 30 ]   : _( "Betelgeuse" ),
        astro.STARS[ 31 ]   : _( "Canopus" ),
        astro.STARS[ 32 ]   : _( "Capella" ),
        astro.STARS[ 33 ]   : _( "Caph" ),
        astro.STARS[ 34 ]   : _( "Castor" ),
        astro.STARS[ 35 ]   : _( "Cebalrai" ),
        astro.STARS[ 36 ]   : _( "Deneb" ),
        astro.STARS[ 37 ]   : _( "Denebola" ),
        astro.STARS[ 38 ]   : _( "Dubhe" ),
        astro.STARS[ 39 ]   : _( "Electra" ),
        astro.STARS[ 40 ]   : _( "Elnath" ),
        astro.STARS[ 41 ]   : _( "Enif" ),
        astro.STARS[ 42 ]   : _( "Etamin" ),
        astro.STARS[ 43 ]   : _( "Fomalhaut" ),
        astro.STARS[ 44 ]   : _( "Gienah Corvi" ),
        astro.STARS[ 45 ]   : _( "Hamal" ),
        astro.STARS[ 46 ]   : _( "Izar" ),
        astro.STARS[ 47 ]   : _( "Kaus Australis" ),
        astro.STARS[ 48 ]   : _( "Kochab" ),
        astro.STARS[ 49 ]   : _( "Maia" ),
        astro.STARS[ 50 ]   : _( "Markab" ),
        astro.STARS[ 51 ]   : _( "Megrez" ),
        astro.STARS[ 52 ]   : _( "Menkalinan" ),
        astro.STARS[ 53 ]   : _( "Menkar" ),
        astro.STARS[ 54 ]   : _( "Merak" ),
        astro.STARS[ 55 ]   : _( "Merope" ),
        astro.STARS[ 56 ]   : _( "Mimosa" ),
        astro.STARS[ 57 ]   : _( "Minkar" ),
        astro.STARS[ 58 ]   : _( "Mintaka" ),
        astro.STARS[ 59 ]   : _( "Mirach" ),
        astro.STARS[ 60 ]   : _( "Mirzam" ),
        astro.STARS[ 61 ]   : _( "Mizar" ),
        astro.STARS[ 62 ]   : _( "Naos" ),
        astro.STARS[ 63 ]   : _( "Nihal" ),
        astro.STARS[ 64 ]   : _( "Nunki" ),
        astro.STARS[ 65 ]   : _( "Peacock" ),
        astro.STARS[ 66 ]   : _( "Phecda" ),
        astro.STARS[ 67 ]   : _( "Polaris" ),
        astro.STARS[ 68 ]   : _( "Pollux" ),
        astro.STARS[ 69 ]   : _( "Procyon" ),
        astro.STARS[ 70 ]   : _( "Rasalgethi" ),
        astro.STARS[ 71 ]   : _( "Rasalhague" ),
        astro.STARS[ 72 ]   : _( "Regulus" ),
        astro.STARS[ 73 ]   : _( "Rigel" ),
        astro.STARS[ 74 ]   : _( "Rukbat" ),
        astro.STARS[ 75 ]   : _( "Sadalmelik" ),
        astro.STARS[ 76 ]   : _( "Sadr" ),
        astro.STARS[ 77 ]   : _( "Saiph" ),
        astro.STARS[ 78 ]   : _( "Scheat" ),
        astro.STARS[ 79 ]   : _( "Schedar" ),
        astro.STARS[ 80 ]   : _( "Shaula" ),
        astro.STARS[ 81 ]   : _( "Sheliak" ),
        astro.STARS[ 82 ]   : _( "Sirius" ),
        astro.STARS[ 83 ]   : _( "Sirrah" ),
        astro.STARS[ 84 ]   : _( "Spica" ),
        astro.STARS[ 85 ]   : _( "Sulafat" ),
        astro.STARS[ 86 ]   : _( "Tarazed" ),
        astro.STARS[ 87 ]   : _( "Taygeta" ),
        astro.STARS[ 88 ]   : _( "Thuban" ),
        astro.STARS[ 89 ]   : _( "Unukalhai" ),
        astro.STARS[ 90 ]   : _( "Vega" ),
        astro.STARS[ 91 ]   : _( "Vindemiatrix" ),
        astro.STARS[ 92 ]   : _( "Wezen" ),
        astro.STARS[ 93 ]   : _( "Zaurak" ) }

    STAR_TAGS_TRANSLATIONS = {
        astro.STARS[ 0 ]    : _( "ACHERNAR" ),
        astro.STARS[ 1 ]    : _( "ADARA" ),
        astro.STARS[ 2 ]    : _( "AGENA" ),
        astro.STARS[ 3 ]    : _( "ALBEREO" ),
        astro.STARS[ 4 ]    : _( "ALCAID" ),
        astro.STARS[ 5 ]    : _( "ALCOR" ),
        astro.STARS[ 6 ]    : _( "ALCYONE" ),
        astro.STARS[ 7 ]    : _( "ALDEBARAN" ),
        astro.STARS[ 8 ]    : _( "ALDERAMIN" ),
        astro.STARS[ 9 ]    : _( "ALFIRK" ),
        astro.STARS[ 10 ]   : _( "ALGENIB" ),
        astro.STARS[ 11 ]   : _( "ALGIEBA" ),
        astro.STARS[ 12 ]   : _( "ALGOL" ),
        astro.STARS[ 13 ]   : _( "ALHENA" ),
        astro.STARS[ 14 ]   : _( "ALIOTH" ),
        astro.STARS[ 15 ]   : _( "ALMACH" ),
        astro.STARS[ 16 ]   : _( "ALNAIR" ),
        astro.STARS[ 17 ]   : _( "ALNILAM" ),
        astro.STARS[ 18 ]   : _( "ALNITAK" ),
        astro.STARS[ 19 ]   : _( "ALPHARD" ),
        astro.STARS[ 20 ]   : _( "ALPHECCA" ),
        astro.STARS[ 21 ]   : _( "ALSHAIN" ),
        astro.STARS[ 22 ]   : _( "ALTAIR" ),
        astro.STARS[ 23 ]   : _( "ANTARES" ),
        astro.STARS[ 24 ]   : _( "ARCTURUS" ),
        astro.STARS[ 25 ]   : _( "ARKAB POSTERIOR" ),
        astro.STARS[ 26 ]   : _( "ARKAB PRIOR" ),
        astro.STARS[ 27 ]   : _( "ARNEB" ),
        astro.STARS[ 28 ]   : _( "ATLAS" ),
        astro.STARS[ 29 ]   : _( "BELLATRIX" ),
        astro.STARS[ 30 ]   : _( "BETELGEUSE" ),
        astro.STARS[ 31 ]   : _( "CANOPUS" ),
        astro.STARS[ 32 ]   : _( "CAPELLA" ),
        astro.STARS[ 33 ]   : _( "CAPH" ),
        astro.STARS[ 34 ]   : _( "CASTOR" ),
        astro.STARS[ 35 ]   : _( "CEBALRAI" ),
        astro.STARS[ 36 ]   : _( "DENEB" ),
        astro.STARS[ 37 ]   : _( "DENEBOLA" ),
        astro.STARS[ 38 ]   : _( "DUBHE" ),
        astro.STARS[ 39 ]   : _( "ELECTRA" ),
        astro.STARS[ 40 ]   : _( "ELNATH" ),
        astro.STARS[ 41 ]   : _( "ENIF" ),
        astro.STARS[ 42 ]   : _( "ETAMIN" ),
        astro.STARS[ 43 ]   : _( "FOMALHAUT" ),
        astro.STARS[ 44 ]   : _( "GIENAH CORVI" ),
        astro.STARS[ 45 ]   : _( "HAMAL" ),
        astro.STARS[ 46 ]   : _( "IZAR" ),
        astro.STARS[ 47 ]   : _( "KAUS AUSTRALIS" ),
        astro.STARS[ 48 ]   : _( "KOCHAB" ),
        astro.STARS[ 49 ]   : _( "MAIA" ),
        astro.STARS[ 50 ]   : _( "MARKAB" ),
        astro.STARS[ 51 ]   : _( "MEGREZ" ),
        astro.STARS[ 52 ]   : _( "MENKALINAN" ),
        astro.STARS[ 53 ]   : _( "MENKAR" ),
        astro.STARS[ 54 ]   : _( "MERAK" ),
        astro.STARS[ 55 ]   : _( "MEROPE" ),
        astro.STARS[ 56 ]   : _( "MIMOSA" ),
        astro.STARS[ 57 ]   : _( "MINKAR" ),
        astro.STARS[ 58 ]   : _( "MINTAKA" ),
        astro.STARS[ 59 ]   : _( "MIRACH" ),
        astro.STARS[ 60 ]   : _( "MIRZAM" ),
        astro.STARS[ 61 ]   : _( "MIZAR" ),
        astro.STARS[ 62 ]   : _( "NAOS" ),
        astro.STARS[ 63 ]   : _( "NIHAL" ),
        astro.STARS[ 64 ]   : _( "NUNKI" ),
        astro.STARS[ 65 ]   : _( "PEACOCK" ),
        astro.STARS[ 66 ]   : _( "PHECDA" ),
        astro.STARS[ 67 ]   : _( "POLARIS" ),
        astro.STARS[ 68 ]   : _( "POLLUX" ),
        astro.STARS[ 69 ]   : _( "PROCYON" ),
        astro.STARS[ 70 ]   : _( "RASALGETHI" ),
        astro.STARS[ 71 ]   : _( "RASALHAGUE" ),
        astro.STARS[ 72 ]   : _( "REGULUS" ),
        astro.STARS[ 73 ]   : _( "RIGEL" ),
        astro.STARS[ 74 ]   : _( "RUKBAT" ),
        astro.STARS[ 75 ]   : _( "SADALMELIK" ),
        astro.STARS[ 76 ]   : _( "SADR" ),
        astro.STARS[ 77 ]   : _( "SAIPH" ),
        astro.STARS[ 78 ]   : _( "SCHEAT" ),
        astro.STARS[ 79 ]   : _( "SCHEDAR" ),
        astro.STARS[ 80 ]   : _( "SHAULA" ),
        astro.STARS[ 81 ]   : _( "SHELIAK" ),
        astro.STARS[ 82 ]   : _( "SIRIUS" ),
        astro.STARS[ 83 ]   : _( "SIRRAH" ),
        astro.STARS[ 84 ]   : _( "SPICA" ),
        astro.STARS[ 85 ]   : _( "SULAFAT" ),
        astro.STARS[ 86 ]   : _( "TARAZED" ),
        astro.STARS[ 87 ]   : _( "TAYGETA" ),
        astro.STARS[ 88 ]   : _( "THUBAN" ),
        astro.STARS[ 89 ]   : _( "UNUKALHAI" ),
        astro.STARS[ 90 ]   : _( "VEGA" ),
        astro.STARS[ 91 ]   : _( "VINDEMIATRIX" ),
        astro.STARS[ 92 ]   : _( "WEZEN" ),
        astro.STARS[ 93 ]   : _( "ZAURAK" ) }

    BODY_TAGS_TRANSLATIONS = dict(
        list( CITY_TAG_TRANSLATION.items() ) +
        list( MOON_TAG_TRANSLATION.items() ) +
        list( PLANET_TAGS_TRANSLATIONS.items() ) +
        list( STAR_TAGS_TRANSLATIONS.items() ) +
        list( SUN_TAG_TRANSLATION.items() ) )

    LUNAR_PHASE_NAMES_TRANSLATIONS = {
        astro.LUNAR_PHASE_FULL_MOON         : _( "Full Moon" ),
        astro.LUNAR_PHASE_WANING_GIBBOUS    : _( "Waning Gibbous" ),
        astro.LUNAR_PHASE_THIRD_QUARTER     : _( "Third Quarter" ),
        astro.LUNAR_PHASE_WANING_CRESCENT   : _( "Waning Crescent" ),
        astro.LUNAR_PHASE_NEW_MOON          : _( "New Moon" ),
        astro.LUNAR_PHASE_WAXING_CRESCENT   : _( "Waxing Crescent" ),
        astro.LUNAR_PHASE_FIRST_QUARTER     : _( "First Quarter" ),
        astro.LUNAR_PHASE_WAXING_GIBBOUS    : _( "Waxing Gibbous" )
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

    # The download period serves two purposes:
    #    Prevent over-taxing the download source (which may result in being blocked).
    #    Download as often as necessary for accuracy.
    #
    # The cache age ensures the data retrieved from the cache is not stale.
    #
    # The cache has two uses:
    #    Act as a source when restarting the indicator.
    #    Act as a source when offline.
    MINOR_PLANET_OE_CACHE_BASENAME = "minorplanet-oe-"
    MINOR_PLANET_OE_CACHE_MAXIMUM_AGE_HOURS = 30
    MINOR_PLANET_OE_URL = "https://minorplanetcenter.net/iau/Ephemerides/Unusual/Soft03Unusual.txt"
    MINOR_PLANET_OE_DOWNLOAD_PERIOD_HOURS = 24

#TODO Verify this works.
    MINOR_PLANET_ON_CLICK_URL = "https://www.minorplanetcenter.net/db_search/show_object?utf8=%E2%9C%93&object_id="

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

    INDICATOR_TEXT_DEFAULT = "[" + astro.NAME_TAG_MOON + " " + astro.DATA_PHASE + "]"

#TODO Use astro.
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

#TODO Likley need to put these into a dict, keyed off from the astro messages.
#Then in getdisplaydata for the message type, use the astro.message and pull the translated/text message from this dict.
    MESSAGE_TRANSLATION_BODY_ALWAYS_UP = _( "Always Up!" )
    MESSAGE_TRANSLATION_BODY_NEVER_UP = _( "Never Up!" ) #TODO Needed?  Not if we always drop never up bodies.
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
    
    # Data is displayed using a default format, but when an alternate format is required, specify using a source below.
    SOURCE_SATELLITE_NOTIFICATION = 0


    def __init__( self ):
        self.cometOEData = { } # Key is the comet name, upper cased; value is the comet data string.  Can be empty but never None.
        self.minorPlanetOEData = { } # Key is the minor planet name, upper cased; value is the minor planet data string.  Can be empty but never None.
        self.satelliteTLEData = { } # Key: ( satellite name upper cased, satellite number ) ; Value: satellite.TLE object.  Can be empty but never None.
        self.satelliteNotifications = { }

#TODO Do these need to live here?  Do we need to recall the state globally or maybe just within each calling of prefs?
        self.toggleCometsTable = True
        self.toggleMinorPlanetsTable = True
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
        self.lastUpdateMinorPlanetOE = datetime.datetime.utcnow() - datetime.timedelta( hours = 1000 )
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
            self.updateMinorPlanetOEData()
            self.updateSatelliteTLEData()

            # Key is a tuple of AstronomicalBodyType, a name tag and data tag.
            # Value is the astronomical data (or equivalent) as a string.
            self.data = astro.getAstronomicalInformation( datetime.datetime.utcnow(),
                                                          self.latitude, self.longitude, self.elevation,
                                                          self.planets,
                                                          self.stars,
                                                          self.satellites, self.satelliteTLEData,
                                                          self.comets, self.cometOEData,
                                                          self.minorPlanets, self.minorPlanetOEData,
                                                          self.magnitude )

            # Update frontend...
            self.nextUpdate = str( datetime.datetime.utcnow() + datetime.timedelta( hours = 1000 ) ) # Set a bogus date/time in the future.
            self.updateMenu()
            self.updateIconAndLabel()

            if self.showWerewolfWarning:
                self.notificationFullMoon()

            if self.showSatelliteNotification:
                self.notificationSatellites()

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
        if self.showMoon and not self.bodyNeverUp( astro.AstronomicalBodyType.Moon, astro.NAME_TAG_MOON ):
            self.updateMoonMenu( menu )

        if self.showSun and not self.bodyNeverUp( astro.AstronomicalBodyType.Sun, astro.NAME_TAG_SUN ):
            self.updateSunMenu( menu )

        self.updatePlanetsMenu( menu )
        self.updateStarsMenu( menu )
        self.updateCometsOrMinorPlanetsMenu( menu, astro.AstronomicalBodyType.Comet )
        self.updateCometsOrMinorPlanetsMenu( menu, astro.AstronomicalBodyType.MinorPlanet )
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

        # If the underlying object has been unchecked or the object (satellite/comet) no longer exists,
        # a tag for this object will not be substituded; so remove.
        parsedOutput = re.sub( "\[[^\[^\]]*\]", "", parsedOutput )
        self.indicator.set_label( parsedOutput, "" ) # Second parameter is a label-guide: http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html

        key = ( astro.AstronomicalBodyType.Moon, astro.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( astro.DATA_ILLUMINATION, ) ] )
        lunarBrightLimbAngle = int( self.data[ key + ( astro.DATA_BRIGHT_LIMB, ) ] )

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


    def notificationFullMoon( self ):
        key = ( astro.AstronomicalBodyType.Moon, astro.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( astro.DATA_ILLUMINATION, ) ] )
        lunarBrightLimbAngle = int( self.data[ key + ( astro.DATA_BRIGHT_LIMB, ) ] )
        lunarPhase = self.data[ key + ( astro.DATA_PHASE, ) ]
        werewolfWarningPercentage = 99
        phaseIsBetweenNewAndFullInclusive = \
            ( lunarPhase == astro.LUNAR_PHASE_NEW_MOON ) or \
            ( lunarPhase == astro.LUNAR_PHASE_WAXING_CRESCENT ) or \
            ( lunarPhase == astro.LUNAR_PHASE_FIRST_QUARTER ) or \
            ( lunarPhase == astro.LUNAR_PHASE_WAXING_GIBBOUS ) or \
            ( lunarPhase == astro.LUNAR_PHASE_FULL_MOON )

        if phaseIsBetweenNewAndFullInclusive and \
           lunarIlluminationPercentage >= werewolfWarningPercentage and \
           ( ( self.lastFullMoonNotfication + datetime.timedelta( hours = 1 ) ) < datetime.datetime.utcnow() ):

            summary = self.werewolfWarningSummary
            if self.werewolfWarningSummary == "":
                summary = " " # The notification summary text cannot be empty (at least on Unity).

            self.createIcon( 100, None, IndicatorLunar.SVG_FULL_MOON_FILE )
            Notify.Notification.new( summary, self.werewolfWarningMessage, IndicatorLunar.SVG_FULL_MOON_FILE ).show()
            os.remove( IndicatorLunar.SVG_FULL_MOON_FILE )
            self.lastFullMoonNotfication = datetime.datetime.utcnow()


    def notificationSatellites( self ):
        # Create a list of satellite name/number and rise times to then either sort by name/number or rise time.
        satelliteNameNumberRiseTimes = [ ]
        for satelliteName, satelliteNumber, in self.satellites:
            key = ( astro.AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )
            if ( key + ( astro.DATA_RISE_TIME, ) ) in self.data: # Assume all other information is present!
               satelliteNameNumberRiseTimes.append( [ satelliteName, satelliteNumber, self.data[ key + ( astro.DATA_RISE_TIME, ) ] ] )

        if self.satellitesSortByDateTime:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 2 ], x[ 0 ], x[ 1 ] ) )
        else:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 0 ], x[ 1 ], x[ 2 ] ) )

        utcNow = str( datetime.datetime.utcnow() )
        for satelliteName, satelliteNumber, riseTime in satelliteNameNumberRiseTimes:
            key = ( astro.AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )

            if ( satelliteName, satelliteNumber ) in self.satelliteNotifications:
                # There has been a previous notification for this satellite.
                # Ensure that the current rise/set matches that of the previous notification.
                # Due to a quirk of the astro backend, the date/time may not match exactly (be out by a few seconds or more).
                # So need to ensure that the current rise/set and the previous rise/set overlap to be sure it is the same transit.
                currentRise = self.data[ key + ( astro.DATA_RISE_TIME, ) ]
                currentSet = self.data[ key + ( astro.DATA_SET_TIME, ) ]
                previousRise, previousSet = self.satelliteNotifications[ ( satelliteName, satelliteNumber ) ]
                overlap = ( currentRise < previousSet ) and ( currentSet > previousRise )
                if overlap:
                    continue

            # Ensure the current time is within the rise/set...
            # Subtract a minute from the rise time to force the notification to take place just prior to the satellite rise.
            riseTimeMinusOneMinute = str( self.toDateTime( self.data[ key + ( astro.DATA_RISE_TIME, ) ] ) - datetime.timedelta( minutes = 1 ) )
            if utcNow < riseTimeMinusOneMinute or \
               utcNow > self.data[ key + ( astro.DATA_SET_TIME, ) ]:
                continue

            self.satelliteNotifications[ ( satelliteName, satelliteNumber ) ] = ( self.data[ key + ( astro.DATA_RISE_TIME, ) ], self.data[ key + ( astro.DATA_SET_TIME, ) ] )

            # Parse the satellite summary/message to create the notification...
            riseTime = self.getDisplayData( key + ( astro.DATA_RISE_TIME, ), IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION )
            riseAzimuth = self.getDisplayData( key + ( astro.DATA_RISE_AZIMUTH, ), IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION )
            setTime = self.getDisplayData( key + ( astro.DATA_SET_TIME, ), IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION )
            setAzimuth = self.getDisplayData( key + ( astro.DATA_SET_AZIMUTH, ), IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION )
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
        key = ( astro.AstronomicalBodyType.Moon, astro.NAME_TAG_MOON )

        menuItem = Gtk.MenuItem( _( "Moon" ) )
        menu.append( menuItem )

        self.updateCommonMenu( menuItem, astro.AstronomicalBodyType.Moon, astro.NAME_TAG_MOON, 0, 1 )

        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )

        menuItem.get_submenu().append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Phase: " ) + self.getDisplayData( key + ( astro.DATA_PHASE, ) ) ) )
        menuItem.get_submenu().append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Next Phases" ) ) )

        # Determine which phases occur by date rather than using the phase calculated.
        # The phase (illumination) rounds numbers and so a given phase is entered earlier than what is correct.
        nextPhases = [ ]
        nextPhases.append( [ self.data[ key + ( astro.DATA_FIRST_QUARTER, ) ], _( "First Quarter: " ), key + ( astro.DATA_FIRST_QUARTER, ) ] )
        nextPhases.append( [ self.data[ key + ( astro.DATA_FULL, ) ], _( "Full: " ), key + ( astro.DATA_FULL, ) ] )
        nextPhases.append( [ self.data[ key + ( astro.DATA_THIRD_QUARTER, ) ], _( "Third Quarter: " ), key + ( astro.DATA_THIRD_QUARTER, ) ] )
        nextPhases.append( [ self.data[ key + ( astro.DATA_NEW, ) ], _( "New: " ), key + ( astro.DATA_NEW, ) ] )

        nextPhases = sorted( nextPhases, key = lambda tuple: tuple[ 0 ] )
        indent = pythonutils.indent( 1, 2 )
        for dateTime, displayText, key in nextPhases:
            menuItem.get_submenu().append( Gtk.MenuItem( indent + displayText + self.getDisplayData( key ) ) )
            self.nextUpdate = self.getSmallestDateTime( self.nextUpdate, dateTime )

        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
        self.updateEclipseMenu( menuItem.get_submenu(), astro.AstronomicalBodyType.Moon, astro.NAME_TAG_MOON )


    def updateSunMenu( self, menu ):
        key = ( astro.AstronomicalBodyType.Sun, astro.NAME_TAG_SUN )
        menuItem = Gtk.MenuItem( _( "Sun" ) )
        menu.append( menuItem )
        self.updateCommonMenu( menuItem, astro.AstronomicalBodyType.Sun, astro.NAME_TAG_SUN, 0, 1 )
        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
        self.updateEclipseMenu( menuItem.get_submenu(), astro.AstronomicalBodyType.Sun, astro.NAME_TAG_SUN )


    def updateEclipseMenu( self, menu, astronomicalBodyType, nameTag ):
        key = ( astronomicalBodyType, nameTag )
        if key + ( astro.DATA_MESSAGE, ) in self.data:
            logging.error( "No eclipse information found!" )
        else:
            menu.append( Gtk.MenuItem( pythonutils.indent( 0, 1 ) + _( "Eclipse" ) ) )
            menu.append( Gtk.MenuItem( pythonutils.indent( 1, 2 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astro.DATA_ECLIPSE_DATE_TIME, ) ) ) )
            latitude = self.getDisplayData( key + ( astro.DATA_ECLIPSE_LATITUDE, ) )
            longitude = self.getDisplayData( key + ( astro.DATA_ECLIPSE_LONGITUDE, ) )
            menu.append( Gtk.MenuItem( pythonutils.indent( 1, 2 ) + _( "Latitude/Longitude: " ) + latitude + " " + longitude ) )
            menu.append( Gtk.MenuItem( pythonutils.indent( 1, 2 ) + _( "Type: " ) + self.getDisplayData( key + ( astro.DATA_ECLIPSE_TYPE, ) ) ) )


    def updatePlanetsMenu( self, menu ):
        planets = [ ]
        for planetName in self.planets:
            if self.bodyNeverUp( astro.AstronomicalBodyType.Planet, planetName ):
                continue

            planets.append( planetName )

        if len( planets ) > 0:
            menuItem = Gtk.MenuItem( _( "Planets" ) )
            menu.append( menuItem )

            if self.showPlanetsAsSubMenu:
                subMenu = Gtk.Menu()
                menuItem.set_submenu( subMenu )

            for planetName in planets:
                if self.showPlanetsAsSubMenu:
                    menuItem = Gtk.MenuItem( pythonutils.indent( 0, 1 ) + IndicatorLunar.PLANET_NAMES_TRANSLATIONS[ planetName ] )
                    subMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( pythonutils.indent( 1, 1 ) + IndicatorLunar.PLANET_NAMES_TRANSLATIONS[ planetName ] )
                    menu.append( menuItem )

                self.updateCommonMenu( menuItem, astro.AstronomicalBodyType.Planet, planetName, 0, 2 )


    def updateStarsMenu( self, menu ):
        stars = [ ] # List of lists.  Each sublist contains the star name followed by the translated name.
        for starName in self.stars:
            if self.bodyNeverUp( astro.AstronomicalBodyType.Star, starName ):
                continue

            stars.append( [ starName, IndicatorLunar.STAR_NAMES_TRANSLATIONS[ starName ] ] )

        if len( stars ) > 0:
            starsMenuItem = Gtk.MenuItem( _( "Stars" ) )
            menu.append( starsMenuItem )

            if self.showStarsAsSubMenu:
                starsSubMenu = Gtk.Menu()
                starsMenuItem.set_submenu( starsSubMenu )

            stars = sorted( stars, key = lambda x: ( x[ 1 ] ) )
            for starName, starNameTranslated in stars:
                nameTag = starName.upper()
                if self.showStarsAsSubMenu:
                    menuItem = Gtk.MenuItem( pythonutils.indent( 0, 1 ) + starNameTranslated )
                    starsSubMenu.append( menuItem )

                else:
                    menuItem = Gtk.MenuItem( pythonutils.indent( 1, 1 ) + starNameTranslated )
                    menu.append( menuItem )

                self.updateCommonMenu( menuItem, astro.AstronomicalBodyType.Star, nameTag, 0, 2 )


    def updateCometsOrMinorPlanetsMenu( self, menu, astronomicalBodyType ):
        bodies = [ ]
        for body in self.comets:
            key = ( astronomicalBodyType, body )
            if key + ( astro.DATA_MESSAGE, ) in self.data and \
               (
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_BODY_NEVER_UP or \
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_DATA_BAD_DATA or \
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_DATA_NO_DATA
               ):
                continue # Skip bodies which are never up or have no data or have bad data AND the user wants to hide bodies on such conditions.

#TODO Does this ensure that bodies which are never up will not appear in the menu?  
# Do we need to do checks similar to that for moon/sun or planets/stars?
            if key + ( astro.DATA_MESSAGE, ) in self.data or \
               key + ( astro.DATA_RISE_TIME, ) in self.data:
                bodies.append( body ) # Either key must be present - otherwise the body has been dropped due to having too large a magnitude.

        if len( bodies ) > 0:
            menuItem = Gtk.MenuItem( _( "Comets" ) if astronomicalBodyType == astro.AstronomicalBodyType.Comet else _( "Minor Planets" ) )
            menu.append( menuItem )
            if self.showCometsAsSubMenu:
                subMenu = Gtk.Menu()
                menuItem.set_submenu( subMenu )

            oeData = self.cometOEData if astronomicalBodyType == astro.AstronomicalBodyType.Comet else self.minorPlanetOEData
            showAsSubMenu = self.showCometsAsSubMenu if astronomicalBodyType == astro.AstronomicalBodyType.Comet else self.showMinorPlanetsAsSubMenu
            for key in sorted( bodies ): # Sorting by key also sorts the display name identically.
                if key in oeData:
                    displayName = self.getCometOrMinorPlanetDisplayName( oeData[ key ] )
                else:
                    displayName = key # There is a body but no data for it.

                if showAsSubMenu:
                    menuItem = Gtk.MenuItem( pythonutils.indent( 0, 1 ) + displayName )
                    subMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( pythonutils.indent( 1, 1 ) + displayName )
                    menu.append( menuItem )

                # Comet data may not exist or body data exists but is bad.
                missing = ( key not in oeData ) # This scenario should be covered by the 'no data' clause below...but just in case catch it here!

                badData = ( key in oeData and \
                          ( astronomicalBodyType, key, astro.DATA_MESSAGE ) in self.data ) and \
                          self.data[ ( astronomicalBodyType, key, astro.DATA_MESSAGE ) ] == astro.MESSAGE_DATA_BAD_DATA

                noData = ( key in oeData and \
                         ( astronomicalBodyType, key, astro.DATA_MESSAGE ) in self.data ) and \
                          self.data[ ( astronomicalBodyType, key, astro.DATA_MESSAGE ) ] == astro.MESSAGE_DATA_NO_DATA

                if missing or badData or noData:
                    subMenu = Gtk.Menu()
                    subMenu.append( Gtk.MenuItem( self.getDisplayData( ( astronomicalBodyType, key, astro.DATA_MESSAGE ) ) ) ) #TODO Needs indent?
                    menuItem.set_submenu( subMenu )
                else:
                    self.updateCommonMenu( menuItem, astronomicalBodyType, key, 0, 2 )

                    # Add handler.
                    for child in menuItem.get_submenu().get_children():
                        child.set_name( key )
                        child.connect( "activate", self.onCometOrMinorPlanet, astronomicalBodyType )


#TODO Delete
    def updateCometsMenu( self, menu ):
        comets = [ ]
        for comet in self.comets:
            key = ( astro.AstronomicalBodyType.Comet, comet )
            if key + ( astro.DATA_MESSAGE, ) in self.data and \
               (
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_BODY_NEVER_UP or \
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_DATA_BAD_DATA or \
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_DATA_NO_DATA
               ):
                continue # Skip comets which are never up or have no data or have bad data AND the user wants to hide comets on such conditions.

#TODO Does this ensure that comets which are never up will not appear in the menu?  
# Do we need to do checks similar to that for moon/sun or planets/stars?
            if key + ( astro.DATA_MESSAGE, ) in self.data or \
               key + ( astro.DATA_RISE_TIME, ) in self.data:
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
                    menuItem = Gtk.MenuItem( pythonutils.indent( 0, 1 ) + displayName )
                    cometsSubMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( pythonutils.indent( 1, 1 ) + displayName )
                    menu.append( menuItem )

                # Comet data may not exist or comet data exists but is bad.
                missing = ( key not in self.cometOEData ) # This scenario should be covered by the 'no data' clause below...but just in case catch it here!

                badData = ( key in self.cometOEData and \
                          ( astro.AstronomicalBodyType.Comet, key, astro.DATA_MESSAGE ) in self.data ) and \
                          self.data[ ( astro.AstronomicalBodyType.Comet, key, astro.DATA_MESSAGE ) ] == astro.MESSAGE_DATA_BAD_DATA

                noData = ( key in self.cometOEData and \
                         ( astro.AstronomicalBodyType.Comet, key, astro.DATA_MESSAGE ) in self.data ) and \
                          self.data[ ( astro.AstronomicalBodyType.Comet, key, astro.DATA_MESSAGE ) ] == astro.MESSAGE_DATA_NO_DATA

                if missing or badData or noData:
                    subMenu = Gtk.Menu()
                    subMenu.append( Gtk.MenuItem( self.getDisplayData( ( astro.AstronomicalBodyType.Comet, key, astro.DATA_MESSAGE ) ) ) ) #TODO Needs indent?
                    menuItem.set_submenu( subMenu )
                else:
                    self.updateCommonMenu( menuItem, astro.AstronomicalBodyType.Comet, key, 0, 2 )

                    # Add handler.
                    for child in menuItem.get_submenu().get_children():
                        child.set_name( key )
                        child.connect( "activate", self.onComet )


    def onCometOrMinorPlanet( self, widget, astronomicalBodyType ):
        if "(" in widget.props.name:
            objectID = widget.props.name[ : widget.props.name.find( "(" ) ].strip()
        else:
            objectID = widget.props.name[ : widget.props.name.find( "/" ) ].strip()

        onClickURL = IndicatorLunar.COMET_ON_CLICK_URL if astronomicalBodyType == astro.AstronomicalBodyType.Comet else IndicatorLunar.MINOR_PLANET_ON_CLICK_URL
        url = onClickURL + objectID.replace( "/", "%2F" ).replace( " ", "+" )
        if len( url ) > 0:
            webbrowser.open( url )


#TODO Remove
    def onComet( self, widget ):
        if "(" in widget.props.name:
            objectID = widget.props.name[ : widget.props.name.find( "(" ) ].strip()
        else:
            objectID = widget.props.name[ : widget.props.name.find( "/" ) ].strip()

        url = IndicatorLunar.COMET_ON_CLICK_URL + objectID.replace( "/", "%2F" ).replace( " ", "+" )
        if len( url ) > 0:
            webbrowser.open( url )


    def bodyNeverUp( self, astronomicalBodyType, nameTag ):
        key = ( astronomicalBodyType, nameTag )
        return key + ( astro.DATA_MESSAGE, ) in self.data and self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_BODY_NEVER_UP


    def updateCommonMenu( self, menuItem, astronomicalBodyType, nameTag, indentUnity, indentGnomeShell ):
        key = ( astronomicalBodyType, nameTag )
        subMenu = Gtk.Menu()
        altitude = int( self.getDecimalDegrees( self.data[ key + ( astro.DATA_ALTITUDE, ) ], False, 0 ) )
        indent = pythonutils.indent( indentUnity, indentGnomeShell )

        # The backend function to update common data may add the "always up" or "never up" messages (and nothing else).
        # Therefore only check for the presence of these two messages.
        if key + ( astro.DATA_MESSAGE, ) in self.data:
            if self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_BODY_ALWAYS_UP:
                subMenu.append( Gtk.MenuItem( indent + self.getDisplayData( key + ( astro.DATA_MESSAGE, ) ) ) )
        else:
            data = [ ]
            data.append( [ key + ( astro.DATA_RISE_TIME, ), _( "Rise: " ), self.data[ key + ( astro.DATA_RISE_TIME, ) ] ] )
            self.nextUpdate = self.getSmallestDateTime( self.nextUpdate, self.data[ key + ( astro.DATA_RISE_TIME, ) ] )
            if altitude >= 0:
                data.append( [ key + ( astro.DATA_SET_TIME, ), _( "Set: " ), self.data[ key + ( astro.DATA_SET_TIME, ) ] ] )
                self.nextUpdate = self.getSmallestDateTime( self.nextUpdate, self.data[ key + ( astro.DATA_SET_TIME, ) ] )

            if astronomicalBodyType == astro.AstronomicalBodyType.Sun:
                data.append( [ key + ( astro.DATA_DAWN, ), _( "Dawn: " ), self.data[ key + ( astro.DATA_DAWN, ) ] ] )
                self.nextUpdate = self.getSmallestDateTime( self.nextUpdate, self.data[ key + ( astro.DATA_DAWN, ) ] )
                if altitude >= 0:
                    data.append( [ key + ( astro.DATA_DUSK, ), _( "Dusk: " ), self.data[ key + ( astro.DATA_DUSK, ) ] ] )
                    self.nextUpdate = self.getSmallestDateTime( self.nextUpdate, self.data[ key + ( astro.DATA_DUSK, ) ] )

            data = sorted( data, key = lambda x: ( x[ 2 ] ) )
            for theKey, text, dateTime in data:
                subMenu.append( Gtk.MenuItem( indent + text + self.getDisplayData( theKey ) ) )

        if altitude >= 0:
            subMenu.append( Gtk.SeparatorMenuItem() )
            subMenu.append( Gtk.MenuItem( indent + _( "Azimuth: " ) + self.getDisplayData( key + ( astro.DATA_AZIMUTH, ) ) ) )
            subMenu.append( Gtk.MenuItem( indent + _( "Altitude: " ) + self.getDisplayData( key + ( astro.DATA_ALTITUDE, ) ) ) )

        menuItem.set_submenu( subMenu )


    def updateSatellitesMenu( self, menu ):
        menuTextSatelliteNameNumberRiseTimes = [ ]
        for satelliteName, satelliteNumber in self.satellites: # key is satellite name/number.
            key = ( astro.AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )
            if key + ( astro.DATA_MESSAGE, ) in self.data and \
               (
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_DATA_NO_DATA or \
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_SATELLITE_NEVER_RISES or \
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME or \
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS or \
                    self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_SATELLITE_VALUE_ERROR
               ):
                continue

            if key + ( astro.DATA_RISE_TIME, ) in self.data:
                internationalDesignator = self.satelliteTLEData[ ( satelliteName, satelliteNumber ) ].getInternationalDesignator()
                riseTime = self.data[ key + ( astro.DATA_RISE_TIME, ) ]
            elif key + ( astro.DATA_MESSAGE, ) in self.data and \
                 self.data[ key + ( astro.DATA_MESSAGE, ) ] != astro.MESSAGE_DATA_NO_DATA: # Any message other than "no data" will have satellite TLE data.
                internationalDesignator = self.satelliteTLEData[ ( satelliteName, satelliteNumber ) ].getInternationalDesignator()
                riseTime = self.data[ key + ( astro.DATA_MESSAGE, ) ]
            else:
                internationalDesignator = "" # No TLE data so cannot retrieve any information about the satellite.
                riseTime = self.data[ key + ( astro.DATA_MESSAGE, ) ]

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
            indent = pythonutils.indent( 0, 2 )
            for menuText, satelliteName, satelliteNumber, riseTime in menuTextSatelliteNameNumberRiseTimes: # key is satellite name/number.
                key = ( astro.AstronomicalBodyType.Satellite, satelliteName + " " + satelliteNumber )
                subMenu = Gtk.Menu()
                if key + ( astro.DATA_MESSAGE, ) in self.data:
                    if self.data[ key + ( astro.DATA_MESSAGE, ) ] == astro.MESSAGE_SATELLITE_IS_CIRCUMPOLAR:
                        subMenu.append( Gtk.MenuItem( indent + _( "Azimuth: " ) + self.getDisplayData( key + ( astro.DATA_AZIMUTH, ) ) ) )

                    subMenu.append( Gtk.MenuItem( self.getDisplayData( key + ( astro.DATA_MESSAGE, ) ) ) )
                else:
#TODO Test this...
#Hide notification and make all passes visible (comment out the check for visible only passes).
#Check the maths for when a satellite is more than two minutes from rising,
#also for a satellite yet to rise,
#also a satellite currently rising.

                    riseTime = self.toDateTime( self.data[ key + ( astro.DATA_RISE_TIME, ) ] )
                    dateTimeDifferenceInMinutes = ( riseTime - utcNow ).total_seconds() / 60 # If the satellite is currently rising, we'll get a negative but that's okay.
                    if dateTimeDifferenceInMinutes > 2: # If this satellite will rise more than two minutes from now, then only show the rise time.
                        subMenu.append( Gtk.MenuItem( indent + _( "Rise Date/Time: " ) + self.getDisplayData( key + ( astro.DATA_RISE_TIME, ) ) ) )

                    else: # This satellite will rise within the next two minutes, so show all data.
#TODO Test this during a satellite pass for both GNOME Shell and Unity.
#I suspect Unity needs an extra indent on the date/time and azimuth menu items.
                        subMenu.append( Gtk.MenuItem( indent + _( "Rise" ) ) )
                        subMenu.append( Gtk.MenuItem( indent + indent + pythonutils.indent( 0, 1 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astro.DATA_RISE_TIME, ) ) ) )
                        subMenu.append( Gtk.MenuItem( indent + indent + pythonutils.indent( 0, 1 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astro.DATA_RISE_AZIMUTH, ) ) ) )

                        subMenu.append( Gtk.MenuItem( indent + _( "Set" ) ) )
                        subMenu.append( Gtk.MenuItem( indent + indent + pythonutils.indent( 0, 1 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astro.DATA_SET_TIME, ) ) ) )
                        subMenu.append( Gtk.MenuItem( indent + indent + pythonutils.indent( 0, 1 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astro.DATA_SET_AZIMUTH, ) ) ) )

                    # Add the rise to the next update, ensuring it is not in the past.
                    # Subtract a minute from the rise time to spoof the next update to happen earlier.
                    # This allows the update to occur and satellite notification to take place just prior to the satellite rise.
                    riseTimeMinusOneMinute = self.toDateTime( self.data[ key + ( astro.DATA_RISE_TIME, ) ] ) - datetime.timedelta( minutes = 1 )
                    if riseTimeMinusOneMinute > utcNow:
                        self.nextUpdate = self.getSmallestDateTime( str( riseTimeMinusOneMinute ), self.nextUpdate )

                    # Add the set time to the next update, ensuring it is not in the past.
                    if self.data[ key + ( astro.DATA_SET_TIME, ) ] > str( utcNow ):
                        self.nextUpdate = self.getSmallestDateTime( self.data[ key + ( astro.DATA_SET_TIME, ) ], self.nextUpdate )

                # Add handler.
                for child in subMenu.get_children():
                    child.set_name( satelliteName + "-----" + satelliteNumber ) # Cannot pass the tuple - must be a string.
                    child.connect( "activate", self.onSatellite )

                if self.showSatellitesAsSubMenu:
                    menuItem = Gtk.MenuItem( pythonutils.indent( 0, 1 ) + menuText )
                    satellitesSubMenu.append( menuItem )
                else:
                    menuItem = Gtk.MenuItem( pythonutils.indent( 1, 1 ) + menuText )
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


#TODO Rename the source to better reflect how it affects the date/time format.
    def getDisplayData( self, key, source = None ):
        displayData = None
        if key[ 2 ] == astro.DATA_ALTITUDE or \
           key[ 2 ] == astro.DATA_AZIMUTH or \
           key[ 2 ] == astro.DATA_RISE_AZIMUTH or \
           key[ 2 ] == astro.DATA_SET_AZIMUTH:
            displayData = str( self.getDecimalDegrees( self.data[ key ], False, 0 ) ) + "°"

        elif key[ 2 ] == astro.DATA_DAWN or \
             key[ 2 ] == astro.DATA_DUSK or \
             key[ 2 ] == astro.DATA_ECLIPSE_DATE_TIME or \
             key[ 2 ] == astro.DATA_FIRST_QUARTER or \
             key[ 2 ] == astro.DATA_FULL or \
             key[ 2 ] == astro.DATA_NEW or \
             key[ 2 ] == astro.DATA_RISE_TIME or \
             key[ 2 ] == astro.DATA_SET_TIME or \
             key[ 2 ] == astro.DATA_THIRD_QUARTER:
                if source is None:
                    displayData = self.getLocalDateTime( self.data[ key ], IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS )
                elif source == IndicatorLunar.SOURCE_SATELLITE_NOTIFICATION:
                    displayData = self.getLocalDateTime( self.data[ key ], IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS )

        elif key[ 2 ] == astro.DATA_ECLIPSE_LATITUDE:
            latitude = self.data[ key ]
            if latitude[ 0 ] == "-":
                displayData = latitude[ 1 : ] + "° " + _( "S" )
            else:
                displayData = latitude + "° " +_( "N" )

        elif key[ 2 ] == astro.DATA_ECLIPSE_LONGITUDE:
            longitude = self.data[ key ]
            if longitude[ 0 ] == "-":
                displayData = longitude[ 1 : ] + "° " + _( "E" )
            else:
                displayData = longitude + "° " +_( "W" )

        elif key[ 2 ] == astro.DATA_ECLIPSE_TYPE:
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

        elif key[ 2 ] == astro.DATA_MESSAGE: #TODO Will need to take the message and pull out the translation from a dict.
            displayData = self.data[ key ]

        elif key[ 2 ] == astro.DATA_PHASE:
            displayData = IndicatorLunar.LUNAR_PHASE_NAMES_TRANSLATIONS[ self.data[ key ] ]

        if displayData is None:  # Returning None is not good but better to let it crash and find out about it than hide the problem.
            logging.error( "Unknown/unhandled key: " + key )

        return displayData


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
        # Have found (very seldom) that a date/time may be generated from the PyEphem backend
        # with the .%f component which may mean the value is zero but PyEphem dropped it.
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


#TODO See if this can be combined with the comet function below.
    def updateMinorPlanetOEData( self ):
        if datetime.datetime.utcnow() > ( self.lastUpdateMinorPlanetOE + datetime.timedelta( hours = IndicatorLunar.MINOR_PLANET_OE_DOWNLOAD_PERIOD_HOURS ) ):
            pythonutils.removeOldFilesFromCache( INDICATOR_NAME, IndicatorLunar.MINOR_PLANET_OE_CACHE_BASENAME, IndicatorLunar.MINOR_PLANET_OE_CACHE_MAXIMUM_AGE_HOURS )
            self.minorPlanetOEData, cacheDateTime = pythonutils.readCacheBinary( INDICATOR_NAME, IndicatorLunar.MINOR_PLANET_OE_CACHE_BASENAME, logging ) # Returned data is either None or non-empty.
            if self.minorPlanetOEData is None:
                self.minorPlanetOEData = self.getMinorPlanetOEData( self.minorPlanetOEURL )

                if self.minorPlanetOEData is None:
                    self.minorPlanetOEData = { }
                    summary = _( "Error Retrieving Minor Planet OE Data" ) #TODO New translation
                    message = _( "The minor planet OE data source could not be reached." ) #TODO New translation
                    Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()

                elif len( self.minorPlanetOEData ) == 0:
                    summary = _( "Empty Minor Planet OE Data" ) #TODO New translation
                    message = _( "The minor planet OE data retrieved was empty." ) #TODO New translation
                    Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()

                else:
                    pythonutils.writeCacheBinary( self.minorPlanetOEData, INDICATOR_NAME, IndicatorLunar.MINOR_PLANET_OE_CACHE_BASENAME, logging )

                # Even if the data download failed or was empty, don't do another download until the required time elapses...don't want to bother the source!
                self.lastUpdateMinorPlanetOE = datetime.datetime.utcnow()

            else:
                # Set the next update to occur when the cache is due to expire.
                self.lastUpdateMinorPlanetOE = datetime.datetime.strptime( cacheDateTime, IndicatorLunar.DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + datetime.timedelta( hours = IndicatorLunar.MINOR_PLANET_OE_CACHE_MAXIMUM_AGE_HOURS )

            if self.minorPlanetsAddNew:
                self.addNewMinorPlanets()


    def updateCometOEData( self ):
        if datetime.datetime.utcnow() > ( self.lastUpdateCometOE + datetime.timedelta( hours = IndicatorLunar.COMET_OE_DOWNLOAD_PERIOD_HOURS ) ):
            pythonutils.removeOldFilesFromCache( INDICATOR_NAME, IndicatorLunar.COMET_OE_CACHE_BASENAME, IndicatorLunar.COMET_OE_CACHE_MAXIMUM_AGE_HOURS )
            self.cometOEData, cacheDateTime = pythonutils.readCacheBinary( INDICATOR_NAME, IndicatorLunar.COMET_OE_CACHE_BASENAME, logging ) # Returned data is either None or non-empty.
            if self.cometOEData is None:
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
        TAB_MINOR_PLANETS = 4
        TAB_SATELLITES = 5
        TAB_NOTIFICATIONS = 6
        TAB_GENERAL = 7

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
            if key[ 2 ] == astro.DATA_BRIGHT_LIMB or key[ 2 ] == astro.DATA_ILLUMINATION:
                continue # Some data tags are only present for calculations, not intended for the end user.

            hideMessage = self.data[ key ] == astro.MESSAGE_BODY_NEVER_UP or \
                      self.data[ key ] == astro.MESSAGE_DATA_BAD_DATA or \
                      self.data[ key ] == astro.MESSAGE_DATA_NO_DATA or \
                      self.data[ key ] == astro.MESSAGE_SATELLITE_NEVER_RISES or \
                      self.data[ key ] == astro.MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME or \
                      self.data[ key ] == astro.MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS or \
                      self.data[ key ] == astro.MESSAGE_SATELLITE_VALUE_ERROR

            if hideMessage:
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
        showMoonCheckbox.connect( "toggled", self.onMoonSunToggled, astro.NAME_TAG_MOON, astro.AstronomicalBodyType.Moon )
        box.pack_start( showMoonCheckbox, False, False, 0 )

        showSunCheckbox = Gtk.CheckButton( _( "Sun" ) )
        showSunCheckbox.set_active( self.showSun )
        showSunCheckbox.set_tooltip_text( _( "Show the sun." ) )
        showSunCheckbox.connect( "toggled", self.onMoonSunToggled, astro.NAME_TAG_SUN, astro.AstronomicalBodyType.Sun )
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

#TODO New trans
        showMinorPlanetsAsSubmenuCheckbox = Gtk.CheckButton( _( "Minor Planets" ) )
        showMinorPlanetsAsSubmenuCheckbox.set_tooltip_text( _( "Show minor planets as submenus." ) )
        showMinorPlanetsAsSubmenuCheckbox.set_active( self.showMinorPlanetsAsSubMenu )
        box.pack_start( showMinorPlanetsAsSubmenuCheckbox, False, False, 0 )

        showSatellitesAsSubmenuCheckbox = Gtk.CheckButton( _( "Satellites" ) )
        showSatellitesAsSubmenuCheckbox.set_active( self.showSatellitesAsSubMenu )
        showSatellitesAsSubmenuCheckbox.set_tooltip_text( _( "Show satellites as submenus." ) )
        box.pack_start( showSatellitesAsSubmenuCheckbox, False, False, 0 )
        grid.attach( box, 0, 3, 1, 1 )

        cometsAddNewCheckbox = Gtk.CheckButton( _( "Automatically add new comets" ) )
        cometsAddNewCheckbox.set_margin_top( 10 )
        cometsAddNewCheckbox.set_active( self.cometsAddNew )
        cometsAddNewCheckbox.set_tooltip_text( _(
            "If checked, all comets are added\n" + \
            "to the list of checked comets." ) )
        grid.attach( cometsAddNewCheckbox, 0, 4, 1, 1 )

#TODO New trans
        minorPlanetsAddNewCheckbox = Gtk.CheckButton( _( "Automatically add new minor planets" ) )
        minorPlanetsAddNewCheckbox.set_margin_top( 10 )
        minorPlanetsAddNewCheckbox.set_active( self.minorPlanetsAddNew )
        minorPlanetsAddNewCheckbox.set_tooltip_text( _(
            "If checked, all minor planets are added\n" + \
            "to the list of checked minor planets." ) )
        grid.attach( cometsAddNewCheckbox, 0, 5, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

#TODO Trans
        box.pack_start( Gtk.Label( _( "Hide comets and minor planets greater than magnitude" ) ), False, False, 0 )

#TODO Comet magnitude
#TODO Trans
        spinnerMagnitude = Gtk.SpinButton()
        spinnerMagnitude.set_numeric( True )
        spinnerMagnitude.set_update_policy( Gtk.SpinButtonUpdatePolicy.IF_VALID )
        spinnerMagnitude.set_adjustment( Gtk.Adjustment( self.magnitude, -30, 30, 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerMagnitude.set_value( self.magnitude ) # ...so need to force the initial value by explicitly setting it.
        spinnerMagnitude.set_tooltip_text( _(
            "Comets and minor planets with a magnitude\n" + \
            "greater than that specified are hidden." ) )

        box.pack_start( spinnerMagnitude, False, False, 0 )
        grid.attach( box, 0, 6, 1, 1 )
        
        satellitesAddNewCheckbox = Gtk.CheckButton( _( "Automatically add new satellites" ) )
        satellitesAddNewCheckbox.set_margin_top( 10 )
        satellitesAddNewCheckbox.set_active( self.satellitesAddNew )
        satellitesAddNewCheckbox.set_tooltip_text( _(
            "If checked all satellites are added\n" + \
            "to the list of checked satellites." ) )
        grid.attach( satellitesAddNewCheckbox, 0, 7, 1, 1 )

        sortSatellitesByDateTimeCheckbox = Gtk.CheckButton( _( "Sort satellites by rise date/time" ) )
        sortSatellitesByDateTimeCheckbox.set_margin_top( 10 )
        sortSatellitesByDateTimeCheckbox.set_active( self.satellitesSortByDateTime )
        sortSatellitesByDateTimeCheckbox.set_tooltip_text( _(
            "If checked, satellites are sorted\n" + \
            "by rise date/time.\n\n" + \
            "Otherwise satellites are sorted\n" + \
            "by Name, Number and then\n" + \
            "International Designator." ) )
        grid.attach( sortSatellitesByDateTimeCheckbox, 0, 8, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Menu" ) ) )

        # Planets/Stars.
        box = Gtk.Box( spacing = 20 )

        planetStore = Gtk.ListStore( bool, str, str ) # Show/hide, planet name (not displayed), translated planet name.
        for planetName in astro.PLANETS:
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
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, planetStore, None, displayTagsStore, astro.AstronomicalBodyType.Planet )
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
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, starStore, starStoreSort, astro.AstronomicalBodyType.Star )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, starStore, starStoreSort, displayTagsStore, astro.AstronomicalBodyType.Star )
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
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, cometStore, cometStoreSort, astro.AstronomicalBodyType.Comet )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, cometStore, cometStoreSort, displayTagsStore, astro.AstronomicalBodyType.Comet )
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
                       astro.AstronomicalBodyType.Comet,
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

        # Minor Planets.
        minorPlanetGrid = Gtk.Grid() #TODO Need to add to same place below as cometGrid
        minorPlanetGrid.set_column_spacing( 10 )
        minorPlanetGrid.set_row_spacing( 10 )
        minorPlanetGrid.set_margin_left( 10 )
        minorPlanetGrid.set_margin_right( 10 )
        minorPlanetGrid.set_margin_top( 10 )
        minorPlanetGrid.set_margin_bottom( 10 )

        minorPlanetStore = Gtk.ListStore( bool, str ) # Show/hide, minor planet name.
        minorPlanetStoreSort = Gtk.TreeModelSort( model = minorPlanetStore )
        minorPlanetStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( minorPlanetStoreSort )
        tree.set_tooltip_text( _(
            "Check a minor planet to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, minorPlanetStore, minorPlanetStoreSort, astro.AstronomicalBodyType.MinorPlanet)
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, minorPlanetStore, minorPlanetStoreSort, displayTagsStore, astro.AstronomicalBodyType.MinorPlanet )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = 1 )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( tree )
        minorPlanetGrid.attach( scrolledWindow, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Minor Planet OE data" ) ), False, False, 0 ) #TODO New translation

        self.minorPlanetOEDataNew = None
        self.minorPlanetOEURLNew = None

        minorPlanetURLEntry = Gtk.Entry()
        minorPlanetURLEntry.set_text( self.minorPlanetOEURL )
#TODO New trans.
        minorPlanetURLEntry.set_tooltip_text( _(
            "The URL from which to source\n" + \
            "minor planet OE data.\n\n" + \
            "To specify a local file, use 'file:///'\n" + \
            "and the filename.\n\n" + \
            "Set a bogus URL such as 'http://'\n" + \
            "to disable." ) )
        box.pack_start( minorPlanetURLEntry, True, True, 0 )

        fetch = Gtk.Button( _( "Fetch" ) )
#TODO New tranas.
        fetch.set_tooltip_text( _(
            "Retrieve the minor planet OE data.\n\n" + \
            "If the URL is empty, the default\n" + \
            "URL will be used.\n\n" + \
            "If using the default URL, the\n" + \
            "download may be blocked to\n" + \
            "avoid burdening the source." ) )
        fetch.connect( "clicked",
                       self.onFetchCometSatelliteData,
                       minorPlanetURLEntry,
                       minorPlanetGrid,
                       minorPlanetStore,
                       astro.AstronomicalBodyType.MinorPlanet,
                       IndicatorLunar.MINOR_PLANET_OE_URL,
                       IndicatorLunar.MINOR_PLANET_OE_CACHE_BASENAME,
                       IndicatorLunar.MINOR_PLANET_OE_CACHE_MAXIMUM_AGE_HOURS,
                       self.lastUpdateMinorPlanetOE,
                       IndicatorLunar.MINOR_PLANET_OE_DOWNLOAD_PERIOD_HOURS,
                       _( "Minor planet data fetch aborted" ),# TODO Trnas
                       _( "To avoid taxing the data source, the download was aborted. The next time the download will occur will be at {0}." ),
                       self.getMinorPlanetOEData )
        box.pack_start( fetch, False, False, 0 )
        minorPlanetGrid.attach( box, 0, 1, 1, 1 )

        notebook.append_page( minorPlanetGrid, Gtk.Label( _( "Minor Planets" ) ) ) #TODO New trans.

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
        renderer_toggle.connect( "toggled", self.onCometStarSatelliteToggled, satelliteStore, satelliteStoreSort, astro.AstronomicalBodyType.Satellite )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, satelliteStore, satelliteStoreSort, displayTagsStore, astro.AstronomicalBodyType.Satellite )
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
                       astro.AstronomicalBodyType.Satellite,
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
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "City" ) ), False, False, 0 )

        city = Gtk.ComboBoxText.new_with_entry()
        city.set_tooltip_text( _(
            "Choose a city from the list.\n" + \
            "Or, add in your own city name." ) )

        cities = astro.getCities()
        if self.city not in cities:
            cities.append( self.city )
            cities = sorted( cities, key = locale.strxfrm )

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

        # The visibility of some GUI objects must be determined AFTER the dialog is shown.
#TODO Rename to include Minor Planets
        self.updateCometSatellitePreferencesTab( cometGrid, cometStore, self.cometOEData, self.comets, cometURLEntry.get_text().strip(), astro.AstronomicalBodyType.Comet )
        self.updateCometSatellitePreferencesTab( minorPlanetGrid, minorPlanetStore, self.minorPlanetOEData, self.minorPlanets, minorPlanetURLEntry.get_text().strip(), astro.AstronomicalBodyType.MinorPlanet )
        self.updateCometSatellitePreferencesTab( satelliteGrid, satelliteStore, self.satelliteTLEData, self.satellites, TLEURLEntry.get_text().strip(), astro.AstronomicalBodyType.Satellite )

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
            self.showMoon = showMoonCheckbox.get_active()
            self.showSun = showSunCheckbox.get_active()
            self.showPlanetsAsSubMenu = showPlanetsAsSubmenuCheckbox.get_active()
            self.showStarsAsSubMenu = showStarsAsSubmenuCheckbox.get_active()
            self.showCometsAsSubMenu = showCometsAsSubmenuCheckbox.get_active()
            self.showMinorPlanetsAsSubMenu = showMinorPlanetsAsSubmenuCheckbox.get_active()
            self.showSatellitesAsSubMenu = showSatellitesAsSubmenuCheckbox.get_active()
            self.magnitude = spinnerMagnitude.get_value_as_int()
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

            if self.cometOEURLNew is not None: # The URL is initialised to None.  If it is not None, a fetch has taken place.
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

            if self.satelliteTLEURLNew is not None: # The URL is initialised to None.  If it is not None, a fetch has taken place.
                self.satelliteTLEURL = self.satelliteTLEURLNew # The URL may or may not be valid, but it will not be None.
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
            self.werewolfWarningSummary = werewolfNotificationSummaryText.get_text()
            self.werewolfWarningMessage = pythonutils.getTextViewText( werewolfNotificationMessageText )

            self.city = cityValue
            self.latitude = latitudeValue
            self.longitude = longitudeValue
            self.elevation = elevationValue

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
            ( astronomicalBodyType == astro.AstronomicalBodyType.Comet or astronomicalBodyType == astro.AstronomicalBodyType.MinorPlanet or astronomicalBodyType == astro.AstronomicalBodyType.Satellite )

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
        self.checkboxToggled( dataStore[ row ][ 1 ].upper(), astro.AstronomicalBodyType.Planet, dataStore[ row ][ 0 ] )
        planetName = dataStore[ row ][ 1 ]


#TODO Include MP
    def onCometStarSatelliteToggled( self, widget, row, dataStore, sortStore, astronomicalBodyType ):
        actualRow = sortStore.convert_path_to_child_path( Gtk.TreePath.new_from_string( row ) ) # Convert sorted model index to underlying (child) model index.
        dataStore[ actualRow ][ 0 ] = not dataStore[ actualRow ][ 0 ]
        if astronomicalBodyType == astro.AstronomicalBodyType.Comet:
            bodyTag = dataStore[ actualRow ][ 1 ].upper()
        if astronomicalBodyType == astro.AstronomicalBodyType.Satellite:
            bodyTag = dataStore[ actualRow ][ 1 ] + " " + dataStore[ actualRow ][ 2 ]
        else: # Assume star.
            bodyTag = dataStore[ actualRow ][ 1 ].upper()

        self.checkboxToggled( bodyTag, astronomicalBodyType, dataStore[ actualRow ][ 0 ] )


#TODO Include MP
    def updateCometSatellitePreferencesTab( self, grid, dataStore, data, bodies, url, astronomicalBodyType ):
        dataStore.clear()
        if data is None:
            message = IndicatorLunar.MESSAGE_DATA_CANNOT_ACCESS_DATA_SOURCE.format( url )
        elif len( data ) == 0:
            message = IndicatorLunar.MESSAGE_DATA_NO_DATA_FOUND_AT_SOURCE.format( url )
        else:
            message = None
            if astronomicalBodyType == astro.AstronomicalBodyType.Satellite:
                for key in data:
                    tle = data[ key ]
                    checked = ( tle.getName().upper(), tle.getNumber() ) in bodies
                    dataStore.append( [ checked, tle.getName(), tle.getNumber(), tle.getInternationalDesignator() ] )

            else: # Comet or Minor Planet
                for key in data:
                    oe = data[ key ]
                    dataStore.append( [ key in bodies, self.getCometOrMinorPlanetDisplayName( oe ) ] )

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


#TODO Include MP
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
            if astronomicalBodyType == astro.AstronomicalBodyType.Comet:
                summary = _( "Error Retrieving Comet OE Data" )
                message = _( "The comet OE data source could not be reached." )
            else: # Assume it's a satellite.
                summary = _( "Error Retrieving Satellite TLE Data" )
                message = _( "The satellite TLE data source could not be reached." )

            Notify.Notification.new( summary, message, IndicatorLunar.ICON ).show()

        self.updateCometSatellitePreferencesTab( grid, store, dataNew, [ ], urlNew, astronomicalBodyType )

        # Assign back to original bodies...
        if astronomicalBodyType == astro.AstronomicalBodyType.Comet:
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
        if astronomicalBodyType == astro.AstronomicalBodyType.Planet:
            toggle = self.togglePlanetsTable
            self.togglePlanetsTable = not self.togglePlanetsTable
            for row in range( len( dataStore ) ):
                dataStore[ row ][ 0 ] = bool( not toggle )
                self.onPlanetToggled( widget, row, dataStore )

        elif astronomicalBodyType == astro.AstronomicalBodyType.Comet or \
             astronomicalBodyType == astro.AstronomicalBodyType.MinorPlanet or \
             astronomicalBodyType == astro.AstronomicalBodyType.Satellite or \
             astronomicalBodyType == astro.AstronomicalBodyType.Star:
            if astronomicalBodyType == astro.AstronomicalBodyType.Comet:
                toggle = self.toggleCometsTable
                self.toggleCometsTable = not self.toggleCometsTable
            elif astronomicalBodyType == astro.AstronomicalBodyType.MinorPlanet:
                toggle = self.toggleMinorPlanetsTable
                self.toggleMinorPlanetsTable = not self.toggleMinorPlanetsTable
            elif astronomicalBodyType == astro.AstronomicalBodyType.Satellite:
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
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION, self.getLocalDateTime( utcNowPlusTenMinutes, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS ) )

            message = message. \
                replace( IndicatorLunar.SATELLITE_TAG_NAME_TRANSLATION, "ISS (ZARYA)" ). \
                replace( IndicatorLunar.SATELLITE_TAG_NUMBER_TRANSLATION, "25544" ). \
                replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION, "1998-067A" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION, "123°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.getLocalDateTime( utcNow, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS ) ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                replace( IndicatorLunar.SATELLITE_TAG_SET_TIME_TRANSLATION, self.getLocalDateTime( utcNowPlusTenMinutes, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMMcolonSS ) )

        if summary == "":
            summary = " " # The notification summary text must not be empty (at least on Unity).

        Notify.Notification.new( summary, message, svgFile ).show()

        if isFullMoon:
            os.remove( svgFile )


    def onCityChanged( self, combobox, latitude, longitude, elevation ):
        city = combobox.get_active_text()
        
        #TODO Can the city ever be empty?  So do we need the check below?
        if city != "" and city in astro.getCities(): # Populate the latitude/longitude/elevation if the city exists, otherwise let the user specify.
            theLatitude, theLongitude, theElevation = astro.getLatitudeLongitudeElevation( city )
            latitude.set_text( theLatitude )
            longitude.set_text( theLongitude )
            elevation.set_text( theElevation )


    def onSwitchPage( self, notebook, page, pageNumber, displayTagsStore ):
        if pageNumber == 0: # User has clicked the first tab.
            displayTagsStore.clear() # List of lists, each sublist contains the tag, translated tag, value.

            # Only add tags for data which has not been removed.
            for key in self.data.keys():
                hideMessage = self.data[ key ] == astro.MESSAGE_BODY_NEVER_UP or \
                              self.data[ key ] == astro.MESSAGE_DATA_BAD_DATA or \
                              self.data[ key ] == astro.MESSAGE_DATA_NO_DATA or \
                              self.data[ key ] == astro.MESSAGE_SATELLITE_NEVER_RISES or \
                              self.data[ key ] == astro.MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME or \
                              self.data[ key ] == astro.MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS or \
                              self.data[ key ] == astro.MESSAGE_SATELLITE_VALUE_ERROR

                if hideMessage:
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
                if astronomicalBodyType == astro.AstronomicalBodyType.Comet:
                    tags = IndicatorLunar.DATA_TAGS_COMET
                if astronomicalBodyType == astro.AstronomicalBodyType.MinorPlanet:
                    tags = IndicatorLunar.DATA_TAGS_MINOR_PLANET
                elif astronomicalBodyType == astro.AstronomicalBodyType.Moon:
                    tags = IndicatorLunar.DATA_TAGS_MOON
                elif astronomicalBodyType == astro.AstronomicalBodyType.Planet:
                    tags = IndicatorLunar.DATA_TAGS_PLANET
                    if bodyTag == IndicatorLunar.PLANET_SATURN.upper():
                        tags.append( IndicatorLunar.DATA_EARTH_TILT )
                        tags.append( IndicatorLunar.DATA_SUN_TILT )
                elif astronomicalBodyType == astro.AstronomicalBodyType.Satellite:
                    tags = IndicatorLunar.DATA_TAGS_SATELLITE
                elif astronomicalBodyType == astro.AstronomicalBodyType.Star:
                    tags = IndicatorLunar.DATA_TAGS_STAR
                elif astronomicalBodyType == astro.AstronomicalBodyType.Sun:
                    tags = IndicatorLunar.DATA_TAGS_SUN

                for tag in tags:
                    self.appendToDisplayTagsStore( key + ( tag, ), IndicatorLunar.MESSAGE_DISPLAY_NEEDS_REFRESH, displayTagsStore )


    def addNewSatellites( self ):
        for key in self.satelliteTLEData:
            if key not in self.satellites:
                self.satellites.append( key )


    def addNewComets( self ):
        for key in self.cometOEData:
            if key not in self.comets:
                self.comets.append( key )


    def addNewMinorPlanets( self ):
        for key in self.minorPlanetOEData:
            if key not in self.minorPlanets:
                self.minorPlanets.append( key )


    def getCometOrMinorPlanetDisplayName( self, cometOrMinorPlanet ): return cometOrMinorPlanet[ 0 : cometOrMinorPlanet.index( "," ) ]


#TODO Remove
    def getCometDisplayName( self, comet ): return comet[ 0 : comet.index( "," ) ]


    # Returns a dict/hashtable of the comets (comets) data from the specified URL (may be empty).
    # Key: comet name, upper cased ; Value: entire comet string.
    # On error, returns None.
#TODO Can this be combined to also do comets?
    def getMinorPlanetOEData( self, url ):
        minorPlanetOEData = None # Indicates error.
        if pythonutils.isConnectedToInternet():
            try:
                # Minor planets are read from a URL which assumes the XEphem format.
                # For example
                #
#TODO Fix this line
                #    C/2002 Y1 (Juels-Holvorcem),e,103.7816,166.2194,128.8232,242.5695,0.0002609,0.99705756,0.0000,04/13.2508/2003,2000,g  6.5,4.0
                #
                # from which the first field (up to the first ',') is the name.
                minorPlanetOEData = { }
                data = urlopen( url, timeout = pythonutils.URL_TIMEOUT_IN_SECONDS ).read().decode( "utf8" ).splitlines()
                for i in range( 0, len( data ) ):
                    if not data[ i ].startswith( "#" ):
                        minorPlanetName = re.sub( "\s\s+", "", data[ i ][ 0 : data[ i ].index( "," ) ] ) # Found that the minor planet name can have multiple whitespace, so remove.
                        minorPlanetData = data[ i ][ data[ i ].index( "," ) : ]
                        minorPlanetOEData[ minorPlanetName.upper() ] = minorPlanetName + minorPlanetData

            except Exception as e:
                minorPlanetOEData = None
                logging.exception( e )
                logging.error( "Error retrieving minor planet OE data from " + str( url ) )

        return minorPlanetOEData


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
            theCity = None
            cities = astro.getCities()
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
        self.indicatorText = IndicatorLunar.INDICATOR_TEXT_DEFAULT

        self.comets = [ ]
        self.cometsAddNew = False
        self.cometOEURL = IndicatorLunar.COMET_OE_URL

        self.minorPlanets = [ ]
        self.minorPlanetsAddNew = False
        self.minorPlanetOEURL = IndicatorLunar.MINOR_PLANET_OE_URL

        self.magnitude = 6 # More or less what's visible with the naked eye or binoculars.

        self.planets = [ ]
        for planetName in astro.PLANETS:
            self.planets.append( planetName )

        self.satelliteNotificationMessage = IndicatorLunar.SATELLITE_NOTIFICATION_MESSAGE_DEFAULT
        self.satelliteNotificationSummary = IndicatorLunar.SATELLITE_NOTIFICATION_SUMMARY_DEFAULT
        self.satelliteTLEURL = IndicatorLunar.SATELLITE_TLE_URL
        self.satellites = [ ]
        self.satellitesAddNew = False
        self.satellitesSortByDateTime = True

        self.showMoon = True
        self.showCometsAsSubMenu = True
        self.showMinorPlanetsAsSubMenu = True
        self.showPlanetsAsSubMenu = False
        self.showSatelliteNotification = True
        self.showSatellitesAsSubMenu = True
        self.showStarsAsSubMenu = True
        self.showSun = True
        self.showWerewolfWarning = True

        self.stars = [ ]

        self.werewolfWarningMessage = IndicatorLunar.WEREWOLF_WARNING_MESSAGE_DEFAULT
        self.werewolfWarningSummary = IndicatorLunar.WEREWOLF_WARNING_SUMMARY_DEFAULT

        config = pythonutils.loadConfig( INDICATOR_NAME, INDICATOR_NAME, logging )

        self.city = config.get( IndicatorLunar.CONFIG_CITY_NAME ) # Returns None if the key is not found.
        if self.city is None:
            self.city = self.getDefaultCity()
            self.latitude, self.longitude, self.elevation = astro.getLatitudeLongitudeElevation( self.city )
        else:
            self.elevation = config.get( IndicatorLunar.CONFIG_CITY_ELEVATION )
            self.latitude = config.get( IndicatorLunar.CONFIG_CITY_LATITUDE )
            self.longitude = config.get( IndicatorLunar.CONFIG_CITY_LONGITUDE )

        self.indicatorText = config.get( IndicatorLunar.CONFIG_INDICATOR_TEXT, self.indicatorText )

        self.cometOEURL = config.get( IndicatorLunar.CONFIG_COMET_OE_URL, self.cometOEURL )
        self.comets = config.get( IndicatorLunar.CONFIG_COMETS, self.comets )
        self.cometsAddNew = config.get( IndicatorLunar.CONFIG_COMETS_ADD_NEW, self.cometsAddNew )

        self.minorPlanetOEURL = config.get( IndicatorLunar.MINOR_PLANET_OE_URL, self.minorPlanetOEURL )
        self.minorPlanets = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS, self.minorPlanets )
        self.minorPlanetsAddNew = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS_ADD_NEW, self.minorPlanetsAddNew )

        self.magnitude = config.get( IndicatorLunar.CONFIG_MAGNITUDE, self.magnitude )

        self.planets = config.get( IndicatorLunar.CONFIG_PLANETS, self.planets )

        self.satelliteNotificationMessage = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE, self.satelliteNotificationMessage )
        self.satelliteNotificationSummary = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY, self.satelliteNotificationSummary )
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

        self.werewolfWarningMessage = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE, self.werewolfWarningMessage )
        self.werewolfWarningSummary = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY, self.werewolfWarningSummary )

        #TODO Start of temporary hack...
        # Convert planet/star to upper case.
        # Convert elevation from float to str.
        # Remove this hack after next release.
        tmp = []
        for planet in self.planets:
            tmp.append( planet.upper() )
        self.planets = tmp
        
        tmp = []
        for star in self.stars:
            tmp.append( star.upper() )
        self.stars = tmp

        self.elevation = str( self.elevation )

        self.saveConfig()
        #TODO End of hack!


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
            IndicatorLunar.CONFIG_CITY_ELEVATION: self.elevation,
            IndicatorLunar.CONFIG_CITY_LATITUDE: self.latitude,
            IndicatorLunar.CONFIG_CITY_LONGITUDE: self.longitude,
            IndicatorLunar.CONFIG_CITY_NAME: self.city,
            IndicatorLunar.CONFIG_INDICATOR_TEXT: self.indicatorText,
            IndicatorLunar.CONFIG_COMET_OE_URL: self.cometOEURL,
            IndicatorLunar.CONFIG_COMETS: self.comets,
            IndicatorLunar.CONFIG_COMETS_ADD_NEW: self.cometsAddNew,
            IndicatorLunar.CONFIG_MINOR_PLANET_OE_URL: self.minorPlanetOEURL,
            IndicatorLunar.CONFIG_MINOR_PLANETS: self.minorPlanets,
            IndicatorLunar.CONFIG_MINOR_PLANETS_ADD_NEW: self.minorPlanetsAddNew,
            IndicatorLunar.CONFIG_MAGNITUDE: self.magnitude,
            IndicatorLunar.CONFIG_PLANETS: self.planets,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE: self.satelliteNotificationMessage,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY: self.satelliteNotificationSummary,
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
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE: self.werewolfWarningMessage,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY: self.werewolfWarningSummary
        }

        pythonutils.saveConfig( config, INDICATOR_NAME, INDICATOR_NAME, logging )


if __name__ == "__main__": IndicatorLunar().main()