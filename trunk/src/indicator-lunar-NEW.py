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


# Application indicator which displays lunar, solar, planetary, star,
# comet, minor planet and satellite information.


#In the notifications preferences, there is a tooltip for each the summary and message about formatting.
# Why is this mentioned?  Did the tags (say moon phase) originally get parsed in the notifications?


#TODO This happens in stardate...fix here too. 
# Lubuntu 18.04 - indicator runs and label displays.
# Lubuntu 19.10 - indicator runs, but no label.  Workaround is to use set_title and that creates a tooltip.
# Xubuntu 18.04 - indicator runs, but no label.  Workaround is to use set_title and that creates a tooltip.
# Xubuntu 19.10 - indicator runs, but no label.  Workaround is to use set_title and that creates a tooltip.
# in regards to actually running and whether the label appears (and if not, add a menu item).
#
# Don't want to have an option if possible to add the menu item; rather add automagically.
#     https://askubuntu.com/questions/452182/is-it-possible-to-know-which-recognized-flavor-i-am-running-using-terminal
#     https://unix.stackexchange.com/questions/116539/how-to-detect-the-desktop-environment-in-a-bash-script
#     https://www.howtogeek.com/351361/how-to-check-which-version-of-ubuntu-you-have-installed/
#     https://itsfoss.com/how-to-know-ubuntu-unity-version/



#TODO In indicatorbase for the function
#     def getThemeColour( self, iconName ):
# Verify the function still works as intended.
# Add header comment specifying the expectation that a tag with the colour is present in the SVG file.


#TODO Look into this
# (indicator-lunar-NEW.py:4242): libappindicator-WARNING **: 09:14:30.474: Using '/tmp' paths in SNAP environment will lead to unreadable resources
# Might get resolved if we use the user cache for icons and not /tmp.


#TODO Is there a problem with setting the minimum update time (using the last update of say 2 minutes)
# and then because the user turns off stuff, the update now becomes one minute.
# Does this make sense?


#TODO Update screen shot
# https://askubuntu.com/a/292529/67335


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
#             self.data = astropyephem.AstroPyephem.getAstronomicalInformation( datetime.datetime( 2019, 8, 29, 9, 0, 0, 0, tzinfo = timezone.utc ),


#TODO Given we now use an Enum for bodytype, Moon becomes MOON.
#So may need a hack for this release to read in user icon text and fix any body tags present.


INDICATOR_NAME = "indicator-lunar"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "GLib", "2.0" )
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import GLib, Gtk, Notify

import astrobase, astropyephem, datetime, eclipse, indicatorbase, glob, locale, math, orbitalelement, os, re, tempfile, twolineelement, webbrowser


class IndicatorLunar( indicatorbase.IndicatorBase ):

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

#TODO Instead of this temp dir thing...just use the user cache?
    ICON_BASE_PATH = tempfile.gettempdir()
    ICON_BASE_NAME = ICON_BASE_PATH + "/." + INDICATOR_NAME
    ICON_FULL_MOON = ICON_BASE_NAME + "-fullmoon-icon" + ".svg" # Dynamically created in the temporary directory (typically /tmp).
    ICON_SATELLITE = INDICATOR_NAME + "-satellite" # Located in /usr/share/icons

    DATE_TIME_FORMAT_HHcolonMM = "%H:%M"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMM = "%Y-%m-%d %H:%M"

    DATA_TAGS_TRANSLATIONS = {
        astrobase.AstroBase.DATA_TAG_ALTITUDE          : _( "ALTITUDE" ),
        astrobase.AstroBase.DATA_TAG_AZIMUTH           : _( "AZIMUTH" ),
        astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME : _( "ECLIPSE DATE TIME" ),
        astrobase.AstroBase.DATA_TAG_ECLIPSE_LATITUDE  : _( "ECLIPSE LATITUDE" ),
        astrobase.AstroBase.DATA_TAG_ECLIPSE_LONGITUDE : _( "ECLIPSE LONGITUDE" ),
        astrobase.AstroBase.DATA_TAG_ECLIPSE_TYPE      : _( "ECLIPSE TYPE" ),
        astrobase.AstroBase.DATA_TAG_EQUINOX           : _( "EQUINOX" ),
        astrobase.AstroBase.DATA_TAG_FIRST_QUARTER     : _( "FIRST QUARTER" ),
        astrobase.AstroBase.DATA_TAG_FULL              : _( "FULL" ),
        astrobase.AstroBase.DATA_TAG_NEW               : _( "NEW" ),
        astrobase.AstroBase.DATA_TAG_PHASE             : _( "PHASE" ),
        astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH      : _( "RISE AZIMUTH" ),
        astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME    : _( "RISE DATE TIME" ),
        astrobase.AstroBase.DATA_TAG_SET_AZIMUTH       : _( "SET AZIMUTH" ),
        astrobase.AstroBase.DATA_TAG_SET_DATE_TIME     : _( "SET DATE TIME" ),
        astrobase.AstroBase.DATA_TAG_SOLSTICE          : _( "SOLSTICE" ),
        astrobase.AstroBase.DATA_TAG_THIRD_QUARTER     : _( "THIRD QUARTER" ) }

    NAME_TAG_MOON_TRANSLATION = { astrobase.AstroBase.NAME_TAG_MOON : _( "MOON" ) }
    NAME_TAG_SUN_TRANSLATION = { astrobase.AstroBase.NAME_TAG_SUN : _( "SUN" ) }

    PLANET_NAMES_TRANSLATIONS = {
        astrobase.AstroBase.PLANET_MERCURY : _( "Mercury" ),
        astrobase.AstroBase.PLANET_VENUS   : _( "Venus" ),
        astrobase.AstroBase.PLANET_MARS    : _( "Mars" ),
        astrobase.AstroBase.PLANET_JUPITER : _( "Jupiter" ),
        astrobase.AstroBase.PLANET_SATURN  : _( "Saturn" ),
        astrobase.AstroBase.PLANET_URANUS  : _( "Uranus" ),
        astrobase.AstroBase.PLANET_NEPTUNE : _( "Neptune" ),
        astrobase.AstroBase.PLANET_PLUTO   : _( "Pluto" ) }

    PLANET_TAGS_TRANSLATIONS = {
        astrobase.AstroBase.PLANET_MERCURY : _( "MERCURY" ),
        astrobase.AstroBase.PLANET_VENUS   : _( "VENUS" ),
        astrobase.AstroBase.PLANET_MARS    : _( "MARS" ),
        astrobase.AstroBase.PLANET_JUPITER : _( "JUPITER" ),
        astrobase.AstroBase.PLANET_SATURN  : _( "SATURN" ),
        astrobase.AstroBase.PLANET_URANUS  : _( "URANUS" ),
        astrobase.AstroBase.PLANET_NEPTUNE : _( "NEPTUNE" ),
        astrobase.AstroBase.PLANET_PLUTO   : _( "PLUTO" ) }

    STAR_NAMES_TRANSLATIONS = {
        astropyephem.AstroPyephem.STARS[ 0 ]  : _( "Achernar" ),
        astropyephem.AstroPyephem.STARS[ 1 ]  : _( "Adara" ), 
        astropyephem.AstroPyephem.STARS[ 2 ]  : _( "Agena" ), 
        astropyephem.AstroPyephem.STARS[ 3 ]  : _( "Albereo" ), 
        astropyephem.AstroPyephem.STARS[ 4 ]  : _( "Alcaid" ),
        astropyephem.AstroPyephem.STARS[ 5 ]  : _( "Alcor" ), 
        astropyephem.AstroPyephem.STARS[ 6 ]  : _( "Alcyone" ), 
        astropyephem.AstroPyephem.STARS[ 7 ]  : _( "Aldebaran" ), 
        astropyephem.AstroPyephem.STARS[ 8 ]  : _( "Alderamin" ), 
        astropyephem.AstroPyephem.STARS[ 9 ]  : _( "Alfirk" ),
        astropyephem.AstroPyephem.STARS[ 10 ] : _( "Algenib" ), 
        astropyephem.AstroPyephem.STARS[ 11 ] : _( "Algieba" ), 
        astropyephem.AstroPyephem.STARS[ 12 ] : _( "Algol" ), 
        astropyephem.AstroPyephem.STARS[ 13 ] : _( "Alhena" ),
        astropyephem.AstroPyephem.STARS[ 14 ] : _( "Alioth" ),
        astropyephem.AstroPyephem.STARS[ 15 ] : _( "Almach" ),
        astropyephem.AstroPyephem.STARS[ 16 ] : _( "Alnair" ),
        astropyephem.AstroPyephem.STARS[ 17 ] : _( "Alnilam" ), 
        astropyephem.AstroPyephem.STARS[ 18 ] : _( "Alnitak" ), 
        astropyephem.AstroPyephem.STARS[ 19 ] : _( "Alphard" ), 
        astropyephem.AstroPyephem.STARS[ 20 ] : _( "Alphecca" ),
        astropyephem.AstroPyephem.STARS[ 21 ] : _( "Alshain" ), 
        astropyephem.AstroPyephem.STARS[ 22 ] : _( "Altair" ),
        astropyephem.AstroPyephem.STARS[ 23 ] : _( "Antares" ), 
        astropyephem.AstroPyephem.STARS[ 24 ] : _( "Arcturus" ),
        astropyephem.AstroPyephem.STARS[ 25 ] : _( "Arkab Posterior" ), 
        astropyephem.AstroPyephem.STARS[ 26 ] : _( "Arkab Prior" ), 
        astropyephem.AstroPyephem.STARS[ 27 ] : _( "Arneb" ), 
        astropyephem.AstroPyephem.STARS[ 28 ] : _( "Atlas" ), 
        astropyephem.AstroPyephem.STARS[ 29 ] : _( "Bellatrix" ), 
        astropyephem.AstroPyephem.STARS[ 30 ] : _( "Betelgeuse" ),
        astropyephem.AstroPyephem.STARS[ 31 ] : _( "Canopus" ), 
        astropyephem.AstroPyephem.STARS[ 32 ] : _( "Capella" ), 
        astropyephem.AstroPyephem.STARS[ 33 ] : _( "Caph" ),
        astropyephem.AstroPyephem.STARS[ 34 ] : _( "Castor" ),
        astropyephem.AstroPyephem.STARS[ 35 ] : _( "Cebalrai" ),
        astropyephem.AstroPyephem.STARS[ 36 ] : _( "Deneb" ), 
        astropyephem.AstroPyephem.STARS[ 37 ] : _( "Denebola" ),
        astropyephem.AstroPyephem.STARS[ 38 ] : _( "Dubhe" ), 
        astropyephem.AstroPyephem.STARS[ 39 ] : _( "Electra" ), 
        astropyephem.AstroPyephem.STARS[ 40 ] : _( "Elnath" ),
        astropyephem.AstroPyephem.STARS[ 41 ] : _( "Enif" ),
        astropyephem.AstroPyephem.STARS[ 42 ] : _( "Etamin" ),
        astropyephem.AstroPyephem.STARS[ 43 ] : _( "Fomalhaut" ), 
        astropyephem.AstroPyephem.STARS[ 44 ] : _( "Gienah Corvi" ),
        astropyephem.AstroPyephem.STARS[ 45 ] : _( "Hamal" ), 
        astropyephem.AstroPyephem.STARS[ 46 ] : _( "Izar" ),
        astropyephem.AstroPyephem.STARS[ 47 ] : _( "Kaus Australis" ),
        astropyephem.AstroPyephem.STARS[ 48 ] : _( "Kochab" ),
        astropyephem.AstroPyephem.STARS[ 49 ] : _( "Maia" ),
        astropyephem.AstroPyephem.STARS[ 50 ] : _( "Markab" ),
        astropyephem.AstroPyephem.STARS[ 51 ] : _( "Megrez" ),
        astropyephem.AstroPyephem.STARS[ 52 ] : _( "Menkalinan" ),
        astropyephem.AstroPyephem.STARS[ 53 ] : _( "Menkar" ),
        astropyephem.AstroPyephem.STARS[ 54 ] : _( "Merak" ), 
        astropyephem.AstroPyephem.STARS[ 55 ] : _( "Merope" ),
        astropyephem.AstroPyephem.STARS[ 56 ] : _( "Mimosa" ),
        astropyephem.AstroPyephem.STARS[ 57 ] : _( "Minkar" ),
        astropyephem.AstroPyephem.STARS[ 58 ] : _( "Mintaka" ), 
        astropyephem.AstroPyephem.STARS[ 59 ] : _( "Mirach" ),
        astropyephem.AstroPyephem.STARS[ 60 ] : _( "Mirzam" ),
        astropyephem.AstroPyephem.STARS[ 61 ] : _( "Mizar" ), 
        astropyephem.AstroPyephem.STARS[ 62 ] : _( "Naos" ),
        astropyephem.AstroPyephem.STARS[ 63 ] : _( "Nihal" ), 
        astropyephem.AstroPyephem.STARS[ 64 ] : _( "Nunki" ), 
        astropyephem.AstroPyephem.STARS[ 65 ] : _( "Peacock" ), 
        astropyephem.AstroPyephem.STARS[ 66 ] : _( "Phecda" ),
        astropyephem.AstroPyephem.STARS[ 67 ] : _( "Polaris" ), 
        astropyephem.AstroPyephem.STARS[ 68 ] : _( "Pollux" ),
        astropyephem.AstroPyephem.STARS[ 69 ] : _( "Procyon" ), 
        astropyephem.AstroPyephem.STARS[ 70 ] : _( "Rasalgethi" ),
        astropyephem.AstroPyephem.STARS[ 71 ] : _( "Rasalhague" ),
        astropyephem.AstroPyephem.STARS[ 72 ] : _( "Regulus" ), 
        astropyephem.AstroPyephem.STARS[ 73 ] : _( "Rigel" ), 
        astropyephem.AstroPyephem.STARS[ 74 ] : _( "Rukbat" ),
        astropyephem.AstroPyephem.STARS[ 75 ] : _( "Sadalmelik" ),
        astropyephem.AstroPyephem.STARS[ 76 ] : _( "Sadr" ),
        astropyephem.AstroPyephem.STARS[ 77 ] : _( "Saiph" ), 
        astropyephem.AstroPyephem.STARS[ 78 ] : _( "Scheat" ),
        astropyephem.AstroPyephem.STARS[ 79 ] : _( "Schedar" ), 
        astropyephem.AstroPyephem.STARS[ 80 ] : _( "Shaula" ),
        astropyephem.AstroPyephem.STARS[ 81 ] : _( "Sheliak" ), 
        astropyephem.AstroPyephem.STARS[ 82 ] : _( "Sirius" ),
        astropyephem.AstroPyephem.STARS[ 83 ] : _( "Sirrah" ),
        astropyephem.AstroPyephem.STARS[ 84 ] : _( "Spica" ), 
        astropyephem.AstroPyephem.STARS[ 85 ] : _( "Sulafat" ), 
        astropyephem.AstroPyephem.STARS[ 86 ] : _( "Tarazed" ), 
        astropyephem.AstroPyephem.STARS[ 87 ] : _( "Taygeta" ), 
        astropyephem.AstroPyephem.STARS[ 88 ] : _( "Thuban" ),
        astropyephem.AstroPyephem.STARS[ 89 ] : _( "Unukalhai" ), 
        astropyephem.AstroPyephem.STARS[ 90 ] : _( "Vega" ),
        astropyephem.AstroPyephem.STARS[ 91 ] : _( "Vindemiatrix" ),
        astropyephem.AstroPyephem.STARS[ 92 ] : _( "Wezen" ), 
        astropyephem.AstroPyephem.STARS[ 93 ] : _( "Zaurak" ) }

    STAR_TAGS_TRANSLATIONS = {
        astropyephem.AstroPyephem.STARS[ 0 ]  : _( "ACHERNAR" ),
        astropyephem.AstroPyephem.STARS[ 1 ]  : _( "ADARA" ),
        astropyephem.AstroPyephem.STARS[ 2 ]  : _( "AGENA" ),
        astropyephem.AstroPyephem.STARS[ 3 ]  : _( "ALBEREO" ),
        astropyephem.AstroPyephem.STARS[ 4 ]  : _( "ALCAID" ),
        astropyephem.AstroPyephem.STARS[ 5 ]  : _( "ALCOR" ),
        astropyephem.AstroPyephem.STARS[ 6 ]  : _( "ALCYONE" ),
        astropyephem.AstroPyephem.STARS[ 7 ]  : _( "ALDEBARAN" ),
        astropyephem.AstroPyephem.STARS[ 8 ]  : _( "ALDERAMIN" ),
        astropyephem.AstroPyephem.STARS[ 9 ]  : _( "ALFIRK" ),
        astropyephem.AstroPyephem.STARS[ 10 ] : _( "ALGENIB" ),
        astropyephem.AstroPyephem.STARS[ 11 ] : _( "ALGIEBA" ),
        astropyephem.AstroPyephem.STARS[ 12 ] : _( "ALGOL" ),
        astropyephem.AstroPyephem.STARS[ 13 ] : _( "ALHENA" ),
        astropyephem.AstroPyephem.STARS[ 14 ] : _( "ALIOTH" ),
        astropyephem.AstroPyephem.STARS[ 15 ] : _( "ALMACH" ),
        astropyephem.AstroPyephem.STARS[ 16 ] : _( "ALNAIR" ),
        astropyephem.AstroPyephem.STARS[ 17 ] : _( "ALNILAM" ),
        astropyephem.AstroPyephem.STARS[ 18 ] : _( "ALNITAK" ),
        astropyephem.AstroPyephem.STARS[ 19 ] : _( "ALPHARD" ),
        astropyephem.AstroPyephem.STARS[ 20 ] : _( "ALPHECCA" ),
        astropyephem.AstroPyephem.STARS[ 21 ] : _( "ALSHAIN" ),
        astropyephem.AstroPyephem.STARS[ 22 ] : _( "ALTAIR" ),
        astropyephem.AstroPyephem.STARS[ 23 ] : _( "ANTARES" ),
        astropyephem.AstroPyephem.STARS[ 24 ] : _( "ARCTURUS" ),
        astropyephem.AstroPyephem.STARS[ 25 ] : _( "ARKABPOSTERIOR" ),
        astropyephem.AstroPyephem.STARS[ 26 ] : _( "ARKABPRIOR" ),
        astropyephem.AstroPyephem.STARS[ 27 ] : _( "ARNEB" ),
        astropyephem.AstroPyephem.STARS[ 28 ] : _( "ATLAS" ),
        astropyephem.AstroPyephem.STARS[ 29 ] : _( "BELLATRIX" ),
        astropyephem.AstroPyephem.STARS[ 30 ] : _( "BETELGEUSE" ),
        astropyephem.AstroPyephem.STARS[ 31 ] : _( "CANOPUS" ),
        astropyephem.AstroPyephem.STARS[ 32 ] : _( "CAPELLA" ),
        astropyephem.AstroPyephem.STARS[ 33 ] : _( "CAPH" ),
        astropyephem.AstroPyephem.STARS[ 34 ] : _( "CASTOR" ),
        astropyephem.AstroPyephem.STARS[ 35 ] : _( "CEBALRAI" ),
        astropyephem.AstroPyephem.STARS[ 36 ] : _( "DENEB" ),
        astropyephem.AstroPyephem.STARS[ 37 ] : _( "DENEBOLA" ),
        astropyephem.AstroPyephem.STARS[ 38 ] : _( "DUBHE" ),
        astropyephem.AstroPyephem.STARS[ 39 ] : _( "ELECTRA" ),
        astropyephem.AstroPyephem.STARS[ 40 ] : _( "ELNATH" ),
        astropyephem.AstroPyephem.STARS[ 41 ] : _( "ENIF" ),
        astropyephem.AstroPyephem.STARS[ 42 ] : _( "ETAMIN" ),
        astropyephem.AstroPyephem.STARS[ 43 ] : _( "FOMALHAUT" ),
        astropyephem.AstroPyephem.STARS[ 44 ] : _( "GIENAHCORVI" ),
        astropyephem.AstroPyephem.STARS[ 45 ] : _( "HAMAL" ),
        astropyephem.AstroPyephem.STARS[ 46 ] : _( "IZAR" ),
        astropyephem.AstroPyephem.STARS[ 47 ] : _( "KAUSAUSTRALIS" ),
        astropyephem.AstroPyephem.STARS[ 48 ] : _( "KOCHAB" ),
        astropyephem.AstroPyephem.STARS[ 49 ] : _( "MAIA" ),
        astropyephem.AstroPyephem.STARS[ 50 ] : _( "MARKAB" ),
        astropyephem.AstroPyephem.STARS[ 51 ] : _( "MEGREZ" ),
        astropyephem.AstroPyephem.STARS[ 52 ] : _( "MENKALINAN" ),
        astropyephem.AstroPyephem.STARS[ 53 ] : _( "MENKAR" ),
        astropyephem.AstroPyephem.STARS[ 54 ] : _( "MERAK" ),
        astropyephem.AstroPyephem.STARS[ 55 ] : _( "MEROPE" ),
        astropyephem.AstroPyephem.STARS[ 56 ] : _( "MIMOSA" ),
        astropyephem.AstroPyephem.STARS[ 57 ] : _( "MINKAR" ),
        astropyephem.AstroPyephem.STARS[ 58 ] : _( "MINTAKA" ),
        astropyephem.AstroPyephem.STARS[ 59 ] : _( "MIRACH" ),
        astropyephem.AstroPyephem.STARS[ 60 ] : _( "MIRZAM" ),
        astropyephem.AstroPyephem.STARS[ 61 ] : _( "MIZAR" ),
        astropyephem.AstroPyephem.STARS[ 62 ] : _( "NAOS" ),
        astropyephem.AstroPyephem.STARS[ 63 ] : _( "NIHAL" ),
        astropyephem.AstroPyephem.STARS[ 64 ] : _( "NUNKI" ),
        astropyephem.AstroPyephem.STARS[ 65 ] : _( "PEACOCK" ),
        astropyephem.AstroPyephem.STARS[ 66 ] : _( "PHECDA" ),
        astropyephem.AstroPyephem.STARS[ 67 ] : _( "POLARIS" ),
        astropyephem.AstroPyephem.STARS[ 68 ] : _( "POLLUX" ),
        astropyephem.AstroPyephem.STARS[ 69 ] : _( "PROCYON" ),
        astropyephem.AstroPyephem.STARS[ 70 ] : _( "RASALGETHI" ),
        astropyephem.AstroPyephem.STARS[ 71 ] : _( "RASALHAGUE" ),
        astropyephem.AstroPyephem.STARS[ 72 ] : _( "REGULUS" ),
        astropyephem.AstroPyephem.STARS[ 73 ] : _( "RIGEL" ),
        astropyephem.AstroPyephem.STARS[ 74 ] : _( "RUKBAT" ),
        astropyephem.AstroPyephem.STARS[ 75 ] : _( "SADALMELIK" ),
        astropyephem.AstroPyephem.STARS[ 76 ] : _( "SADR" ),
        astropyephem.AstroPyephem.STARS[ 77 ] : _( "SAIPH" ),
        astropyephem.AstroPyephem.STARS[ 78 ] : _( "SCHEAT" ),
        astropyephem.AstroPyephem.STARS[ 79 ] : _( "SCHEDAR" ),
        astropyephem.AstroPyephem.STARS[ 80 ] : _( "SHAULA" ),
        astropyephem.AstroPyephem.STARS[ 81 ] : _( "SHELIAK" ),
        astropyephem.AstroPyephem.STARS[ 82 ] : _( "SIRIUS" ),
        astropyephem.AstroPyephem.STARS[ 83 ] : _( "SIRRAH" ),
        astropyephem.AstroPyephem.STARS[ 84 ] : _( "SPICA" ),
        astropyephem.AstroPyephem.STARS[ 85 ] : _( "SULAFAT" ),
        astropyephem.AstroPyephem.STARS[ 86 ] : _( "TARAZED" ),
        astropyephem.AstroPyephem.STARS[ 87 ] : _( "TAYGETA" ),
        astropyephem.AstroPyephem.STARS[ 88 ] : _( "THUBAN" ),
        astropyephem.AstroPyephem.STARS[ 89 ] : _( "UNUKALHAI" ),
        astropyephem.AstroPyephem.STARS[ 90 ] : _( "VEGA" ),
        astropyephem.AstroPyephem.STARS[ 91 ] : _( "VINDEMIATRIX" ),
        astropyephem.AstroPyephem.STARS[ 92 ] : _( "WEZEN" ),
        astropyephem.AstroPyephem.STARS[ 93 ] : _( "ZAURAK" ) }

    BODY_TAGS_TRANSLATIONS = dict(
        list( NAME_TAG_MOON_TRANSLATION.items() ) +
        list( PLANET_TAGS_TRANSLATIONS.items() ) +
        list( STAR_TAGS_TRANSLATIONS.items() ) +
        list( NAME_TAG_SUN_TRANSLATION.items() ) )

    LUNAR_PHASE_NAMES_TRANSLATIONS = {
        astrobase.AstroBase.LUNAR_PHASE_FULL_MOON       : _( "Full Moon" ),
        astrobase.AstroBase.LUNAR_PHASE_WANING_GIBBOUS  : _( "Waning Gibbous" ),
        astrobase.AstroBase.LUNAR_PHASE_THIRD_QUARTER   : _( "Third Quarter" ),
        astrobase.AstroBase.LUNAR_PHASE_WANING_CRESCENT : _( "Waning Crescent" ),
        astrobase.AstroBase.LUNAR_PHASE_NEW_MOON        : _( "New Moon" ),
        astrobase.AstroBase.LUNAR_PHASE_WAXING_CRESCENT : _( "Waxing Crescent" ),
        astrobase.AstroBase.LUNAR_PHASE_FIRST_QUARTER   : _( "First Quarter" ),
        astrobase.AstroBase.LUNAR_PHASE_WAXING_GIBBOUS  : _( "Waxing Gibbous" ) }

    COMET_CACHE_BASENAME = "comet-oe-"
    COMET_CACHE_MAXIMUM_AGE_HOURS = 24
    COMET_DATA_URL = "https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt"

    MINOR_PLANET_CACHE_BASENAMES = [ "minorplanet-oe-" + "bright-",
                                     "minorplanet-oe-" + "critical-",
                                     "minorplanet-oe-" + "distant-",
                                     "minorplanet-oe-" + "unusual-" ]
    MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS = 24
    MINOR_PLANET_DATA_URLS = [ "https://minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft03Bright.txt", 
                               "https://minorplanetcenter.net/iau/Ephemerides/CritList/Soft03CritList.txt",
                               "https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft03Distant.txt",
                               "https://minorplanetcenter.net/iau/Ephemerides/Unusual/Soft03Unusual.txt" ]

    MINOR_PLANET_CENTER_SEARCH_URL = "https://www.minorplanetcenter.net/db_search/show_object?utf8=%E2%9C%93&object_id=" # Used to search for minor planets and comets.

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
    SATELLITE_CACHE_MAXIMUM_AGE_HOURS = 12
    SATELLITE_DATA_URL = "https://celestrak.com/NORAD/elements/visual.txt"
    SATELLITE_MENU_TEXT = SATELLITE_TAG_NAME + " : " + SATELLITE_TAG_NUMBER + " : " + SATELLITE_TAG_INTERNATIONAL_DESIGNATOR
    SATELLITE_NOTIFICATION_MESSAGE_DEFAULT = \
        _( "Number: " ) + SATELLITE_TAG_NUMBER_TRANSLATION + "\n" + \
        _( "International Designator: " ) + SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n" + \
        _( "Rise Time: " ) + SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n" + \
        _( "Rise Azimuth: " ) + SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n" + \
        _( "Set Time: " ) + SATELLITE_TAG_SET_TIME_TRANSLATION + "\n" + \
        _( "Set Azimuth: " ) + SATELLITE_TAG_SET_AZIMUTH_TRANSLATION
    SATELLITE_NOTIFICATION_SUMMARY_DEFAULT = SATELLITE_TAG_NAME + _( " now rising..." )
    SATELLITE_ON_CLICK_URL = "https://www.n2yo.com/satellite/?s=" + SATELLITE_TAG_NUMBER

    STAR_SEARCH_URL = "https://hipparcos-tools.cosmos.esa.int/cgi-bin/HIPcatalogueSearch.pl?hipId="

    WEREWOLF_WARNING_MESSAGE_DEFAULT = _( "                                          ...werewolves about ! ! !" )
    WEREWOLF_WARNING_SUMMARY_DEFAULT = _( "W  A  R  N  I  N  G" )

    INDICATOR_TEXT_DEFAULT = " [" + astrobase.AstroBase.NAME_TAG_MOON + " " + astrobase.AstroBase.DATA_TAG_PHASE + "]"


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.81",
            copyrightStartYear = "2012",
            comments = _( "Displays lunar, solar, planetary, comet, minor planet, star and satellite information." ),
            creditz = [ _( "Calculations courtesy of PyEphem/XEphem. http://rhodesmill.org/pyephem" ),
                        _( "Eclipse information by Fred Espenak and Jean Meeus. http://eclipse.gsfc.nasa.gov" ),
                        _( "Satellite TLE data by Dr T S Kelso. http://www.celestrak.com" ),
                        _( "Comet and Minor Planet OE data by Minor Planet Center. http://www.minorplanetcenter.net" ) ] )

        self.cometData = { } # Key: comet name, upper cased; Value: orbitalelement.OE object.  Can be empty but never None.
        self.minorPlanetData = { } # Key: minor planet name, upper cased; Value: orbitalelement.OE object.  Can be empty but never None.
        self.satelliteData = { } # Key: satellite number; Value: twolineelement.TLE object.  Can be empty but never None.
        self.satelliteNotifications = { }

#         self.indicator.set_icon_theme_path( IndicatorLunar.ICON_BASE_PATH ) #TODO Needed?  Maybe needed when setting the icon.
        self.lastFullMoonNotfication = datetime.datetime.utcnow() - datetime.timedelta( hours = 1000 )

        # Flush comet, minor planet and satellite caches.
        self.removeOldFilesFromCache( IndicatorLunar.COMET_CACHE_BASENAME, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS )
        self.removeOldFilesFromCache( IndicatorLunar.SATELLITE_CACHE_BASENAME, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS )
        for cacheBaseName in IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES:
            self.removeOldFilesFromCache( cacheBaseName, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )

        # Remove old icons.
        oldIcons = glob.glob( IndicatorLunar.ICON_BASE_NAME + "*" )
        for oldIcon in oldIcons:
            os.remove( oldIcon )


    def update( self, menu ):
        utcNow = datetime.datetime.utcnow()

        # Update comet, minor planet and satellite data.
        self.cometData = self.updateData( IndicatorLunar.COMET_CACHE_BASENAME, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS, orbitalelement.download, IndicatorLunar.COMET_DATA_URL, astropyephem.AstroPyephem.getOrbitalElementsLessThanMagnitude )
        if self.cometsAddNew:
            self.addNewBodies( self.cometData, self.comets )

        self.minorPlanetData = { }
        for baseName, url in zip( IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES, IndicatorLunar.MINOR_PLANET_DATA_URLS ):
            minorPlanetData = self.updateData( baseName, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, orbitalelement.download, url, astropyephem.AstroPyephem.getOrbitalElementsLessThanMagnitude )
            for key in minorPlanetData:
                if key not in self.minorPlanetData:
                    self.minorPlanetData[ key ] = minorPlanetData[ key ]

        if self.minorPlanetsAddNew:
            self.addNewBodies( self.minorPlanetData, self.minorPlanets )

        self.satelliteData = self.updateData( IndicatorLunar.SATELLITE_CACHE_BASENAME, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS, twolineelement.download, IndicatorLunar.SATELLITE_DATA_URL, None )
        if self.satellitesAddNew:
            self.addNewBodies( self.satelliteData, self.satellites )

        # Update backend.  Returned object is a dictionary:
        #    Key is a tuple of bodyType, a name tag and data tag.
        #    Value is the calculated astronomical data as a string.
        self.data = astropyephem.AstroPyephem.getAstronomicalInformation(
            datetime.datetime.utcnow(),
            self.latitude, self.longitude, self.elevation,
            self.planets,
            self.stars,
            self.satellites, self.satelliteData,
            self.comets, self.cometData,
            self.minorPlanets, self.minorPlanetData,
            self.magnitude,
            self.hideBodiesBelowHorizon )

        # Update frontend.
        self.updateMenu( menu )
        self.updateIconAndLabel()

        if self.showWerewolfWarning:
            self.notificationFullMoon()

#TODO Uncomment when all done...don't forget to test!
#             if self.showSatelliteNotification:
#                 self.notificationSatellites()

        return self.getNextUpdateTimeInSeconds( utcNow )


    # Get the data from the cache, or if stale, download from the source.
    #
    # Returns a dictionary (may be empty).
    def updateData( self, cacheBaseName, cacheMaximumAgeHours, downloadDataFunction, dataURL, magnitudeFilterFunction = None ):
        data = self.readCacheBinary( cacheBaseName ) # Either valid or None.

#TODO Start of temporary hack...
# Cache data formats changed between version 80 and 81.
#
# Satellites still use the TLE object, but the file name changed from satellite to twolineelement and is deemed an invalid object.
# Therefore reading the cache binary will throw an exception and return None.
# Not a problem as a new version will be downloaded and the cache will eventually clear out.
#
# Comets will successfully read in because their objects (dictionary, tuple string) are valid.
# Comets are still stored in a dictionary using a string as key but now with a new OE object as the value, which must be handled.
# This check can be removed in version 82.
        if data and cacheBaseName == IndicatorLunar.COMET_CACHE_BASENAME:
            if not isinstance( next( iter( data.values() ) ), orbitalelement.OE ): # Check that the object loaded from cache matches the new OE object.
                data = None
# End of hack!

        if data is None:
            data = downloadDataFunction( dataURL, self.getLogging() )
            if magnitudeFilterFunction:
                data = magnitudeFilterFunction( data, astrobase.AstroBase.MAGNITUDE_MAXIMUM )

            self.writeCacheBinary( data, cacheBaseName )

        return data


    def getNextUpdateTimeInSeconds( self, startDateTime ):
        utcNow = datetime.datetime.utcnow()
        durationOfLastRunInSeconds = ( utcNow - startDateTime ).total_seconds()
        utcNowPlusLastRun = utcNow + datetime.timedelta( seconds = durationOfLastRunInSeconds )
        nextUpdateTime = utcNow + datetime.timedelta( hours = 1000 ) # Set a bogus date/time in the future.
        for key in self.data:
            if key[ 2 ] == astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME or \
               key[ 2 ] == astrobase.AstroBase.DATA_TAG_EQUINOX or \
               key[ 2 ] == astrobase.AstroBase.DATA_TAG_FIRST_QUARTER or \
               key[ 2 ] == astrobase.AstroBase.DATA_TAG_FULL or \
               key[ 2 ] == astrobase.AstroBase.DATA_TAG_NEW or \
               key[ 2 ] == astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME or \
               key[ 2 ] == astrobase.AstroBase.DATA_TAG_SET_DATE_TIME or \
               key[ 2 ] == astrobase.AstroBase.DATA_TAG_SOLSTICE or \
               key[ 2 ] == astrobase.AstroBase.DATA_TAG_THIRD_QUARTER:

                dateTime = datetime.datetime.strptime( self.data[ key ], astrobase.AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )
                if dateTime > utcNowPlusLastRun and dateTime < nextUpdateTime:
                    nextUpdateTime = dateTime

        return int( ( nextUpdateTime - utcNow ).total_seconds() )


    def updateMenu( self, menu ):
        self.updateMenuMoon( menu )
        self.updateMenuSun( menu )
        self.updateMenuPlanets( menu )
        self.updateMenuStars( menu )
        self.updateMenuCometsMinorPlanets( menu, astrobase.AstroBase.BodyType.COMET )
        self.updateMenuCometsMinorPlanets( menu, astrobase.AstroBase.BodyType.MINOR_PLANET)
        self.updateMenuSatellites( menu )


    def updateIconAndLabel( self ):
        # Substitute tags for values.
        parsedOutput = self.indicatorText
        for key in self.data.keys():
            if "[" + key[ 1 ] + " " + key[ 2 ] + "]" in parsedOutput:
                parsedOutput = parsedOutput.replace( "[" + key[ 1 ] + " " + key[ 2 ] + "]", self.getDisplayData( key ) ) #TODO What if a tag is a satellite rise/set?  This is a different date/time format.

#TODO For satellites, tags will contain both the name and number...so ensure satellites work!

        parsedOutput = re.sub( "\[[^\[^\]]*\]", "", parsedOutput ) # Remove unused tags.

        self.indicator.set_label( parsedOutput, "" )
        self.indicator.set_title( parsedOutput ) # Needed for Lubuntu/Xubuntu.

        # Ideally should be able to create the icon with the same name each time.
        # Due to a bug, the icon name must change between calls to setting the icon.
        # So change the name each time - using the current date/time.
        #    https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620
        #    http://askubuntu.com/questions/490634/application-indicator-icon-not-changing-until-clicked
        iconFilename = IndicatorLunar.ICON_BASE_NAME + "-" + str( datetime.datetime.utcnow().strftime( "%Y%m%d%H%M%S" ) ) + ".svg"

        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( astrobase.AstroBase.DATA_TAG_ILLUMINATION, ) ] )
        lunarBrightLimbAngleInDegrees = int( math.degrees( float( self.data[ key + ( astrobase.AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] ) ) )
        self.createIcon( lunarIlluminationPercentage, lunarBrightLimbAngleInDegrees, iconFilename )
        self.indicator.set_icon_full( iconFilename, "" )


#TODO Verify at next full moon.
    def notificationFullMoon( self ):
        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( astrobase.AstroBase.DATA_TAG_ILLUMINATION, ) ] )
        lunarPhase = self.data[ key + ( astrobase.AstroBase.DATA_TAG_PHASE, ) ]

#TODO Maybe set to 98 rather than 99?
        if ( lunarPhase == astrobase.AstroBase.LUNAR_PHASE_WAXING_GIBBOUS or lunarPhase == astrobase.AstroBase.LUNAR_PHASE_FULL_MOON ) and \
           lunarIlluminationPercentage >= 99 and \
           ( ( self.lastFullMoonNotfication + datetime.timedelta( hours = 1 ) ) < datetime.datetime.utcnow() ):

            summary = self.werewolfWarningSummary
            if self.werewolfWarningSummary == "":
                summary = " " # The notification summary text cannot be empty (at least on Unity).

            if not os.path.exists( IndicatorLunar.ICON_FULL_MOON ):
                self.createIcon( 100, None, IndicatorLunar.ICON_FULL_MOON )

            Notify.Notification.new( summary, self.werewolfWarningMessage, IndicatorLunar.ICON_FULL_MOON ).show()
            self.lastFullMoonNotfication = datetime.datetime.utcnow()


#TODO Verify
    def notificationSatellites( self ):
        # Create a list of satellite name/number and rise times to then either sort by name/number or rise time.
        satelliteNameNumberRiseTimes = [ ]
        for satelliteName, satelliteNumber, in self.satellites:
            key = ( astrobase.AstroBase.BodyType.SATELLITE, satelliteName + " " + satelliteNumber )
            if ( key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ) in self.data: # Assume all other information is present!
               satelliteNameNumberRiseTimes.append( [ satelliteName, satelliteNumber, self.data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] ] )

        if self.satellitesSortByDateTime:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 2 ], x[ 0 ], x[ 1 ] ) )
        else:
            satelliteNameNumberRiseTimes = sorted( satelliteNameNumberRiseTimes, key = lambda x: ( x[ 0 ], x[ 1 ], x[ 2 ] ) )

        utcNow = str( datetime.datetime.utcnow() )
        for satelliteName, satelliteNumber, riseTime in satelliteNameNumberRiseTimes:
            key = ( astrobase.AstroBase.BodyType.SATELLITE, satelliteName + " " + satelliteNumber )

            if ( satelliteName, satelliteNumber ) in self.satelliteNotifications:
                # There has been a previous notification for this satellite.
                # Ensure that the current rise/set matches that of the previous notification.
                # Due to a quirk of the astro backend, the date/time may not match exactly (be out by a few seconds or more).
                # So need to ensure that the current rise/set and the previous rise/set overlap to be sure it is the same transit.
                currentRise = self.data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ]
                currentSet = self.data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ]
                previousRise, previousSet = self.satelliteNotifications[ ( satelliteName, satelliteNumber ) ]
                overlap = ( currentRise < previousSet ) and ( currentSet > previousRise )
                if overlap:
                    continue


            # Ensure the current time is within the rise/set...
            # Subtract a minute from the rise time to force the notification to take place just prior to the satellite rise.
#TODO Use the function below to convert from string to datetime.
#     def toDateTime( self, dateTimeAsString, formatString ): return datetime.datetime.strptime( dateTimeAsString, formatString )
            riseTimeMinusOneMinute = str( self.toDateTime( self.data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ], IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMM ) - datetime.timedelta( minutes = 1 ) )

#TODO Is using strings safe here or do we need datetime?            
            if utcNow < riseTimeMinusOneMinute or \
               utcNow > self.data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ]:
                continue

            self.satelliteNotifications[ ( satelliteName, satelliteNumber ) ] = ( self.data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ], self.data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ] )

            # Parse the satellite summary/message to create the notification...
            riseTime = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            riseAzimuth = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            setTime = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            setAzimuth = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_AZIMUTH, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
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

            Notify.Notification.new( summary, message, IndicatorLunar.ICON_SATELLITE ).show()


    def updateMenuMoon( self, menu ):
        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        if self.display( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON ):
            menuItem = Gtk.MenuItem( _( "Moon" ) )
            menu.append( menuItem )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            self.updateCommonMenu( subMenu, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON, 0, 1 )
            subMenu.append( Gtk.MenuItem( self.indent( 0, 1 ) + _( "Phase: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_PHASE, ) ) ) )
            subMenu.append( Gtk.MenuItem( self.indent( 0, 1 ) + _( "Next Phases" ) ) )

            # Determine which phases occur by date rather than using the phase calculated.
            # The phase (illumination) rounds numbers and so a given phase is entered earlier than what is correct.
            nextPhases = [ ]
            nextPhases.append( [ self.data[ key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ], _( "First Quarter: " ), key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ] )
            nextPhases.append( [ self.data[ key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ], _( "Full: " ), key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ] )
            nextPhases.append( [ self.data[ key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ], _( "Third Quarter: " ), key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ] )
            nextPhases.append( [ self.data[ key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ], _( "New: " ), key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ] )

            nextPhases = sorted( nextPhases, key = lambda tuple: tuple[ 0 ] )
            indent = self.indent( 1, 2 )
            for dateTime, displayText, key in nextPhases:
                subMenu.append( Gtk.MenuItem( indent + displayText + self.getDisplayData( key ) ) )

            self.updateEclipseMenu( subMenu, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )


    def updateMenuSun( self, menu ):
        key = ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )
        if self.display( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN ):
            menuItem = Gtk.MenuItem( _( "Sun" ) )
            menu.append( menuItem )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            self.updateCommonMenu( subMenu, astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN, 0, 1 )
            subMenu.append( Gtk.MenuItem( self.indent( 0, 1 ) + _( "Equinox: " ) + self.getDisplayData( ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN, astrobase.AstroBase.DATA_TAG_EQUINOX ) ) ) )
            subMenu.append( Gtk.MenuItem( self.indent( 0, 1 ) + _( "Solstice: " ) + self.getDisplayData( ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN, astrobase.AstroBase.DATA_TAG_SOLSTICE ) ) ) )
            self.updateEclipseMenu( subMenu, astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )


    def updateEclipseMenu( self, menu, bodyType, nameTag ):
        key = ( bodyType, nameTag )
        menu.append( Gtk.MenuItem( self.indent( 0, 1 ) + _( "Eclipse" ) ) )
        menu.append( Gtk.MenuItem( self.indent( 1, 2 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ) ) )
        latitude = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) )
        longitude = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) )
        menu.append( Gtk.MenuItem( self.indent( 1, 2 ) + _( "Latitude/Longitude: " ) + latitude + " " + longitude ) )
        menu.append( Gtk.MenuItem( self.indent( 1, 2 ) + _( "Type: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ) ) )


    def updateMenuPlanets( self, menu ):
        planets = [ ]
        for planet in self.planets:
            if self.display( astrobase.AstroBase.BodyType.PLANET, planet ):
                planets.append( [ planet, IndicatorLunar.PLANET_NAMES_TRANSLATIONS[ planet ] ] )

        if planets:
            menuItem = Gtk.MenuItem( _( "Planets" ) )
            menu.append( menuItem )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for name, translatedName in planets:
                subMenu.append( Gtk.MenuItem( self.indent( 0, 1 ) + translatedName ) )
                self.updateCommonMenu( subMenu, astrobase.AstroBase.BodyType.PLANET, name, 1, 2 )
                separator = Gtk.SeparatorMenuItem()
                subMenu.append( separator ) 

            subMenu.remove( separator )


    def updateMenuStars( self, menu ):
        stars = [ ]
        for star in self.stars:
            if self.display( astrobase.AstroBase.BodyType.STAR, star ):
                stars.append( [ star, IndicatorLunar.STAR_NAMES_TRANSLATIONS[ star ] ] )

        if stars:
            menuItem = Gtk.MenuItem( _( "Stars" ) )
            menu.append( menuItem ) 
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for name, translatedName in stars:
                url = IndicatorLunar.STAR_SEARCH_URL + str( astropyephem.AstroPyephem.STARS_TO_HIP[ name ] )
                menuItem = Gtk.MenuItem( self.indent( 0, 1 ) + translatedName )
                menuItem.set_name( url )
                subMenu.append( menuItem )
                self.updateCommonMenu( subMenu, astrobase.AstroBase.BodyType.STAR, name, 1, 2, url )
                separator = Gtk.SeparatorMenuItem()
                subMenu.append( separator ) 

            subMenu.remove( separator )

            for child in subMenu.get_children():
                child.connect( "activate", self.onMenuItemClick )


    def updateMenuCometsMinorPlanets( self, menu, bodyType ):
        bodies = [ ]
        for body in self.comets if bodyType == astrobase.AstroBase.BodyType.COMET else self.minorPlanets:
            if self.display( bodyType, body ):
                bodies.append( body )

        if bodies:
            menuItem = Gtk.MenuItem( _( "Comets" ) if bodyType == astrobase.AstroBase.BodyType.COMET else _( "Minor Planets" ) )
            menu.append( menuItem )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for name in sorted( bodies ):
                url = self.getCometMinorPlanetOnClickURL( name, bodyType )
                menuItem = Gtk.MenuItem( self.indent( 0, 1 ) + name )
                menuItem.set_name( url )
                subMenu.append( menuItem )
                self.updateCommonMenu( subMenu, bodyType, name, 1, 2, url )
                separator = Gtk.SeparatorMenuItem()
                subMenu.append( separator ) 

            subMenu.remove( separator )

            for child in subMenu.get_children():
                child.connect( "activate", self.onMenuItemClick )


    # https://www.iau.org/public/themes/naming
    # https://minorplanetcenter.net/iau/info/CometNamingGuidelines.html
    def getCometMinorPlanetOnClickURL( self, name, bodyType ):
        if bodyType == astrobase.AstroBase.BodyType.COMET:
            if "(" in name: # P/1997 T3 (Lagerkvist-Carsenty)
                id = name[ : name.find( "(" ) ].strip()

            else:
                postSlash = name[ name.find( "/" ) + 1 : ]
                if re.search( '\d', postSlash ): # C/1931 AN
                    id = name

                else: # 97P/Metcalf-Brewington
                    id = name[ : name.find( "/" ) ].strip()

        else:
            components = name.split( ' ' )
            if components[ 0 ].isnumeric() and components[ 1 ].isalpha(): # 433 Eros
                id = components[ 0 ] 

            elif components[ 0 ].isnumeric() and components[ 1 ].isnumeric(): # 465402 2008 HW1
                id = components[ 0 ]

            elif components[ 0 ].isnumeric() and components[ 1 ].isalnum(): # 1999 KL17
                id = components[ 0 ] + " " + components[ 1 ]

            else: # 229762 G!kunll'homdima
                id = components[ 0 ] 

        return IndicatorLunar.MINOR_PLANET_CENTER_SEARCH_URL + id.replace( "/", "%2F" ).replace( " ", "+" )


    def updateCommonMenu( self, menu, bodyType, nameTag, indentUnity, indentGnomeShell, onClickURL = "" ):
        key = ( bodyType, nameTag )
        indent = self.indent( indentUnity, indentGnomeShell )

        if key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) in self.data:
            self.createMenuItem( indent + _( "Rise: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ), onClickURL, menu )

        else:
            if key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) in self.data:
                self.createMenuItem( indent + _( "Set: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ), onClickURL, menu )

            self.createMenuItem( indent + _( "Azimuth: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ), onClickURL, menu )
            self.createMenuItem( indent + _( "Altitude: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ), onClickURL, menu )


#TODO Test each clause...will have to adjust date/time and lat/long.
# Circumpolar: Az/Alt
# Yet to rise (more than 5 minutes away): rise date/time
# Yet to rise (less than 5 minutes away) or in transit: rise date/time, set date/time, az/alt.
    def updateMenuSatellites( self, menu ):
        satellites = [ ]
        satellitesCircumpolar = [ ]
        if self.satellitesSortByDateTime:
            for number in self.satellites:
                key = ( astrobase.AstroBase.BodyType.SATELLITE, number )
                if key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) in self.data:
                    satellites.append( [ number, self.satelliteData[ number ].getName(), self.data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] ] )

                elif key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) in self.data:
                    satellitesCircumpolar.append( [ number, self.satelliteData[ number ].getName(), None ] )

            satellites = sorted( satellites, key = lambda x: ( x[ 2 ], x[ 0 ], x[ 1 ] ) )
            satellitesCircumpolar = sorted( satellitesCircumpolar, key = lambda x: ( x[ 0 ], x[ 1 ] ) )

        else:
            for number in self.satellites:
                key = ( astrobase.AstroBase.BodyType.SATELLITE, number )
                if key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) in self.data or key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) in self.data:
                    satellites.append( [ number, self.satelliteData[ number ].getName(), None ] )

            satellites = sorted( satellites, key = lambda x: ( x[ 0 ], x[ 1 ] ) )

        if satellites:
            self.__updateMenuSatellites( menu, _( "Satellites" ), satellites )

        if satellitesCircumpolar:
            self.__updateMenuSatellites( menu, _( "Satellites (Circumpolar)" ), satellitesCircumpolar )


#TODO Test each clause...will have to adjust date/time and lat/long.
# Circumpolar: Az/Alt
# Yet to rise (more than 5 minutes away): rise date/time
# Yet to rise (less than 5 minutes away) or in transit: rise date/time, set date/time, az/alt.
    def __updateMenuSatellites( self, menu, label, satellites ):
        menuItem = Gtk.MenuItem( _( label ) )
        menu.append( menuItem )
        subMenu = Gtk.Menu()
        menuItem.set_submenu( subMenu )
        for number, name, riseDateTime in satellites:
            menuText = IndicatorLunar.SATELLITE_MENU_TEXT.replace( IndicatorLunar.SATELLITE_TAG_NAME, name ) \
                                                         .replace( IndicatorLunar.SATELLITE_TAG_NUMBER, number ) \
                                                         .replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satelliteData[ number ].getInternationalDesignator() )

            url = IndicatorLunar.SATELLITE_ON_CLICK_URL. \
                  replace( IndicatorLunar.SATELLITE_TAG_NAME, name ). \
                  replace( IndicatorLunar.SATELLITE_TAG_NUMBER, number ). \
                  replace( IndicatorLunar.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satelliteData[ number ].getInternationalDesignator() )

            menuItem = Gtk.MenuItem( self.indent( 0, 1 ) + menuText )
            menuItem.set_name( url )
            subMenu.append( menuItem )

            key = ( astrobase.AstroBase.BodyType.SATELLITE, number )
            if key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) in self.data and key + ( astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH, ) in self.data:
                self.createMenuItem( self.indent( 1, 2 ) + _( "Rise" ), url, subMenu )
                self.createMenuItem( self.indent( 2, 3 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ), url, subMenu )
                self.createMenuItem( self.indent( 2, 3 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH, ) ), url, subMenu )
                self.createMenuItem( self.indent( 1, 2 ) + _( "Set" ), url, subMenu )
                self.createMenuItem( self.indent( 2, 3 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ), url, subMenu )
                self.createMenuItem( self.indent( 2, 3 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_AZIMUTH, ) ), url, subMenu )

            elif key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) in self.data:
                self.createMenuItem( self.indent( 1, 2 ) + _( "Rise Date/Time: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ), url, subMenu )

            else:
                self.createMenuItem( self.indent( 1, 2 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ), url, subMenu )
                self.createMenuItem( self.indent( 1, 2 ) + _( "Altitude: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ), url, subMenu )

            separator = Gtk.SeparatorMenuItem()
            subMenu.append( separator ) 

        subMenu.remove( separator )

        for child in subMenu.get_children():
            child.connect( "activate", self.onMenuItemClick )


    def createMenuItem( self, label, onClickURL, menu ):
        menuItem = Gtk.MenuItem( label )
        menu.append( menuItem )
        if onClickURL:
            menuItem.set_name( onClickURL )


    def onMenuItemClick( self, widget ): webbrowser.open( widget.props.name )


    def display( self, bodyType, nameTag ):
        return ( bodyType, nameTag, astrobase.AstroBase.DATA_TAG_ALTITUDE ) in self.data or \
               ( bodyType, nameTag, astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME ) in self.data


    def getDisplayData( self, key, dateTimeFormat = None ):
        displayData = None

        if key[ 2 ] == astrobase.AstroBase.DATA_TAG_ALTITUDE or \
           key[ 2 ] == astrobase.AstroBase.DATA_TAG_AZIMUTH or \
           key[ 2 ] == astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH or \
           key[ 2 ] == astrobase.AstroBase.DATA_TAG_SET_AZIMUTH:
            displayData = str( round( math.degrees( float( self.data[ key ] ) ) ) ) + "°"

        elif key[ 2 ] == astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME or \
             key[ 2 ] == astrobase.AstroBase.DATA_TAG_EQUINOX or \
             key[ 2 ] == astrobase.AstroBase.DATA_TAG_FIRST_QUARTER or \
             key[ 2 ] == astrobase.AstroBase.DATA_TAG_FULL or \
             key[ 2 ] == astrobase.AstroBase.DATA_TAG_NEW or \
             key[ 2 ] == astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME or \
             key[ 2 ] == astrobase.AstroBase.DATA_TAG_SET_DATE_TIME or \
             key[ 2 ] == astrobase.AstroBase.DATA_TAG_SOLSTICE or \
             key[ 2 ] == astrobase.AstroBase.DATA_TAG_THIRD_QUARTER:
                if dateTimeFormat is None:
                    displayData = self.toLocalDateTimeString( self.data[ key ], IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMM ).replace( ' ', '  ' )

                else:
                    displayData = self.toLocalDateTimeString( self.data[ key ], dateTimeFormat )

        elif key[ 2 ] == astrobase.AstroBase.DATA_TAG_ECLIPSE_LATITUDE:
            latitude = self.data[ key ]
            if latitude[ 0 ] == "-":
                displayData = latitude[ 1 : ] + "° " + _( "S" )

            else:
                displayData = latitude + "° " +_( "N" )

        elif key[ 2 ] == astrobase.AstroBase.DATA_TAG_ECLIPSE_LONGITUDE:
            longitude = self.data[ key ]
            if longitude[ 0 ] == "-":
                displayData = longitude[ 1 : ] + "° " + _( "E" )

            else:
                displayData = longitude + "° " +_( "W" )

        elif key[ 2 ] == astrobase.AstroBase.DATA_TAG_ECLIPSE_TYPE:
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

        elif key[ 2 ] == astrobase.AstroBase.DATA_TAG_PHASE:
            displayData = IndicatorLunar.LUNAR_PHASE_NAMES_TRANSLATIONS[ self.data[ key ] ]

        if displayData is None:
            displayData = "" # Better to show nothing than let None slip through and crash.
            self.getLogging().error( "Unknown key: " + key )

        return displayData


    # Converts a UTC datetime string to a local datetime string in the given format.
    def toLocalDateTimeString( self, utcDateTimeString, outputFormat ):
        utcDateTime = datetime.datetime.strptime( utcDateTimeString, astrobase.AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )
        localDateTime = utcDateTime.replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None )
        return localDateTime.strftime( outputFormat )


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
        colour = self.getThemeColour( self.icon )

        if illuminationPercentage == 0 or illuminationPercentage == 100:
            svgStart = '<circle cx="' + str( width / 2 ) + '" cy="' + str( height / 2 ) + '" r="' + str( radius )
            if illuminationPercentage == 0: # New
                svg = svgStart + '" fill="none" stroke="#' + colour + '" stroke-width="2" />'

            else: # Full
                svg = svgStart + '" fill="#' + colour + '" />'

        else:
            svgStart = '<path d="M ' + str( width / 2 ) + ' ' + str( height / 2 ) + ' h-' + str( radius ) + ' a ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + str( radius * 2 ) + ' 0'
            if illuminationPercentage == 50: # Quarter
                svg = svgStart + '"'

            elif illuminationPercentage < 50: # Crescent
                svg = svgStart + ' a ' + str( radius ) + ' ' + str( ( 50 - illuminationPercentage ) / 50.0 * radius ) + ' 0 0 0 ' + str( radius * 2 * -1 ) + ' + 0"'

            else: # Gibbous
                svg = svgStart + ' a ' + str( radius ) + ' ' + str( ( illuminationPercentage - 50 ) / 50.0 * radius ) + ' 0 1 1 ' + str( radius * 2 * -1 ) + ' + 0"'

            svg += ' transform="rotate(' + str( brightLimbAngleInDegrees * -1 ) + ' ' + str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="#' + colour + '" />'

        header = '<?xml version="1.0" standalone="no"?>' \
                 '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
                 '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100">'

        footer = '</svg>'

        try:
            with open( svgFilename, "w" ) as f:
                f.write( header + svg + footer )
                f.close()

        except Exception as e:
            self.getLogging().exception( e )
            self.getLogging().error( "Error writing: " + svgFilename )


    #TODO These two functions are only used by Lunar...so leave them here for now...until icons/themes are sorted.
    def getThemeName( self ): return Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )


    def getThemeColour( self, iconName ):
        iconFilenameForCurrentTheme = "/usr/share/icons/" + self.getThemeName() + "/scalable/apps/" + iconName + ".svg"
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




    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

        # Icon.
        grid = self.createGrid()

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

        COLUMN_TAG = 0
        COLUMN_TRANSLATED_TAG = 1
        COLUMN_VALUE = 2
        displayTagsStore = Gtk.ListStore( str, str, str ) # Tag, translated tag, value.
        self.initialiseDisplayTagsStore( displayTagsStore )

#         tags = re.split( "(\[[^\[^\]]+\])", self.indicatorText )
#         for key in self.data.keys():
#             if key[ 2 ] not in astropyephem.AstroPyephem.DATA_INTERNAL:
#TODO Need to handle satellite tags...
#When to remove the satellite name from the tag?  Here or at render time or when?
#                 tag = "[" + key[ 1 ] + " " + key[ 2 ] + "]"
#                 if tag in tags:
#                     i = tags.index( tag )
#                     tags[ i ] = ""

#TODO What is happening here?
# Are we stripping tags from the indicator text which no longer appear in the table?
# Maybe just leave the tags there and the user can manually remove after they see displayed?  Ask Oleg.
# Tried the text [DEF][MOON PHASE][ABC] and commented out the code below and the ABC/DEF tags did not appear in the final label.  Why?
#Maybe show the tags in the preferences always, but drop them when rendering?
#Before making changes consider what happens if we leave unknown tags here, but then at render time is that an issue?
#Not sure what to do now...
# Leave tags in here, but what if a user has added in there own tags...can they do that?
#         unknownTags = [ ]
#         for tag in tags:
#             if re.match( "\[[^\[^\]]+\]", tag ) is not None:
#                 self.indicatorText = self.indicatorText.replace( tag, "" )

#TODO Assuming any satellite tags will only contain the satellite number (not name and intl desig)
# need to pre-process the indicator text to insert the satellite name and intl desig.
        indicatorText.set_text( self.translateTags( displayTagsStore, True, self.indicatorText ) ) # Translate tags into local language.

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
            "Double click to add a tag to the icon text.\n\n" + \
            "A tag with no value arises if a body is dropped\n" + \
            "due to exceeding magnitude, or below the horizon\n" + \
            "(no set date/time and no azimuth/altitude),\n" + \
            "or above the horizon (no rise date/time)." ) )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onTagDoubleClick, COLUMN_TRANSLATED_TAG, indicatorText )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Icon" ) ) )

        # Menu.
        grid = self.createGrid()

        hideBodiesBelowTheHorizonCheckbox = Gtk.CheckButton( _( "Hide bodies below the horizon" ) )
        hideBodiesBelowTheHorizonCheckbox.set_active( self.hideBodiesBelowHorizon )
        hideBodiesBelowTheHorizonCheckbox.set_tooltip_text( _(
            "If checked, all bodies below the horizon\n" + \
            "are hidden (excludes satellites)." ) )
        grid.attach( hideBodiesBelowTheHorizonCheckbox, 0, 0, 1, 1 )

        cometsAddNewCheckbox = Gtk.CheckButton( _( "Add new comets" ) )
        cometsAddNewCheckbox.set_margin_top( 10 )
        cometsAddNewCheckbox.set_active( self.cometsAddNew )
        cometsAddNewCheckbox.set_tooltip_text( _( "If checked, all comets are added." ) )
        grid.attach( cometsAddNewCheckbox, 0, 1, 1, 1 )

        minorPlanetsAddNewCheckbox = Gtk.CheckButton( _( "Add new minor planets" ) )
        minorPlanetsAddNewCheckbox.set_margin_top( 10 )
        minorPlanetsAddNewCheckbox.set_active( self.minorPlanetsAddNew )
        minorPlanetsAddNewCheckbox.set_tooltip_text( _( "If checked, all minor planets are added." ) )
        grid.attach( minorPlanetsAddNewCheckbox, 0, 2, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Hide bodies greater than magnitude" ) ), False, False, 0 )

        spinnerMagnitude = Gtk.SpinButton()
        spinnerMagnitude.set_numeric( True )
        spinnerMagnitude.set_update_policy( Gtk.SpinButtonUpdatePolicy.IF_VALID )
        spinnerMagnitude.set_adjustment( Gtk.Adjustment( self.magnitude, int( astrobase.AstroBase.MAGNITUDE_MINIMUM ), int( astrobase.AstroBase.MAGNITUDE_MAXIMUM ), 1, 5, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinnerMagnitude.set_value( self.magnitude ) # ...so need to force the initial value by explicitly setting it.
        spinnerMagnitude.set_tooltip_text( _(
            "Planets, stars, comets and minor planets with a\n" + \
            "magnitude greater than that specified are hidden." ) )

        box.pack_start( spinnerMagnitude, False, False, 0 )
        grid.attach( box, 0, 3, 1, 1 )

        satellitesAddNewCheckbox = Gtk.CheckButton( _( "Add new satellites" ) )
        satellitesAddNewCheckbox.set_margin_top( 10 )
        satellitesAddNewCheckbox.set_active( self.satellitesAddNew )
        satellitesAddNewCheckbox.set_tooltip_text( _( "If checked all satellites are added." ) )
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
        for planetName in astrobase.AstroBase.PLANETS:
            planetStore.append( [ planetName in self.planets, planetName, IndicatorLunar.PLANET_NAMES_TRANSLATIONS[ planetName ] ] )

        toolTipText = _(
            "Check a planet to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." )

        box.pack_start( self.createTable( planetStore, toolTipText, _( "Planet" ), 2 ), True, True, 0 )

        stars = [ ] # List of lists, each sublist containing star is checked flag, star name, star translated name.
        for starName in IndicatorLunar.STAR_NAMES_TRANSLATIONS.keys():
            stars.append( [ starName in self.stars, starName, IndicatorLunar.STAR_NAMES_TRANSLATIONS[ starName ] ] )

        stars = sorted( stars, key = lambda x: ( x[ 2 ] ) )
        starStore = Gtk.ListStore( bool, str, str ) # Show/hide, star name (not displayed), star translated name.
        for star in stars:
            starStore.append( star )

        toolTipText = _(
            "Check a star to display in the menu.\n\n" + \
            "Clicking the header of the first column\n" + \
            "will toggle all checkboxes." )

        box.pack_start( self.createTable( starStore, toolTipText, _( "Star" ), 2 ), True, True, 0 )

        notebook.append_page( box, Gtk.Label( _( "Planets / Stars" ) ) )

        # Comets and minor planets.
        box = Gtk.Box( spacing = 20 )

        cometStore = Gtk.ListStore( bool, str ) # Show/hide, comet name.
        for comet in self.cometData:
            cometStore.append( [ comet in self.comets, comet ] )

        if self.cometData:
            toolTipText = _(
                "Check a comet to display in the menu.\n\n" + \
                "Clicking the header of the first column\n" + \
                "will toggle all checkboxes." )

        else:
            toolTipText = _(
                "Comet data is unavailable; the source\n" + \
                "could not be reached, or no data was\n" + \
                "available from the source, or the data\n" + \
                "was completely filtered by magnitude." )

        box.pack_start( self.createTable( cometStore, toolTipText, _( "Comet" ), 1 ), True, True, 0 )

        minorPlanetStore = Gtk.ListStore( bool, str ) # Show/hide, minor planet name.
        for minorPlanet in self.minorPlanetData:
            minorPlanetStore.append( [ minorPlanet in self.minorPlanets, minorPlanet ] )

        if self.minorPlanetData:
            toolTipText = _(
                "Check a minor planet to display in the menu.\n\n" + \
                "Clicking the header of the first column\n" + \
                "will toggle all checkboxes." )

        else:
            toolTipText = _(
                "Minor planet data is unavailable; the source\n" + \
                "could not be reached, or no data was\n" + \
                "available from the source, or the data\n" + \
                "was completely filtered by magnitude." )

        box.pack_start( self.createTable( minorPlanetStore, toolTipText, _( "Minor Planet" ), 1 ), True, True, 0 )

        notebook.append_page( box, Gtk.Label( _( "Comets / Minor Planets" ) ) )

        # Satellites.
        box = Gtk.Box()

        satelliteStore = Gtk.ListStore( bool, str, str, str ) # Show/hide, name, number, international designator.
        for satellite in self.satelliteData:
            satelliteStore.append( [ satellite in self.satellites, self.satelliteData[ satellite ].getName(), satellite, self.satelliteData[ satellite ].getInternationalDesignator() ] )

        satelliteStoreSort = Gtk.TreeModelSort( model = satelliteStore )
        satelliteStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( satelliteStoreSort )
        if self.satelliteData:
            tree.set_tooltip_text( _(
                "Check a satellite to display in the menu.\n\n" + \
                "Clicking the header of the first column\n" + \
                "will toggle all checkboxes." ) )

        else:
            tree.set_tooltip_text( _(
                "Satellite data is unavailable; the\n" + \
                "source could not be reached, or no\n" + \
                "data was available from the source." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCheckbox, satelliteStore, satelliteStoreSort, astrobase.AstroBase.BodyType.SATELLITE)
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, satelliteStore )
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
        scrolledWindow.add( tree )
        box.pack_start( scrolledWindow, True, True, 0 )

        notebook.append_page( box, Gtk.Label( _( "Satellites" ) ) )

        # OSD (satellite and full moon).
        notifyOSDInformation = _( "For formatting, refer to https://wiki.ubuntu.com/NotifyOSD" )

        grid = self.createGrid()

        showSatelliteNotificationCheckbox = Gtk.CheckButton( _( "Satellite rise" ) )
        showSatelliteNotificationCheckbox.set_active( self.showSatelliteNotification )
        showSatelliteNotificationCheckbox.set_tooltip_text( _( "Screen notification when a satellite rises above the horizon." ) )
        grid.attach( showSatelliteNotificationCheckbox, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Summary" ) )
        label.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        box.pack_start( label, False, False, 0 )

        satelliteNotificationSummaryText = Gtk.Entry()
        satelliteNotificationSummaryText.set_text( self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, True, self.satelliteNotificationSummary ) )
        satelliteNotificationSummaryText.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
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

        showSatelliteNotificationCheckbox.connect( "toggled", self.onCheckbox, label, satelliteNotificationSummaryText )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Message" ) + "\n \n \n \n \n " ) # Padding to ensure the textview for the message text is not too small.  
        label.set_valign( Gtk.Align.START )
        label.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
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

        showSatelliteNotificationCheckbox.connect( "toggled", self.onCheckbox, label, scrolledWindow )

        test = Gtk.Button( _( "Test" ) )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( showSatelliteNotificationCheckbox.get_active() )
        test.connect( "clicked", self.onTestNotificationClicked, satelliteNotificationSummaryText, satelliteNotificationMessageText, False )
        test.set_tooltip_text( _(
            "Show the notification bubble.\n" + \
            "Tags will be substituted with\n" + \
            "mock text." ) )
        grid.attach( test, 0, 3, 1, 1 )

        showSatelliteNotificationCheckbox.connect( "toggled", self.onCheckbox, test, test )

        showWerewolfWarningCheckbox = Gtk.CheckButton( _( "Werewolf warning" ) )
        showWerewolfWarningCheckbox.set_margin_top( 10 )
        showWerewolfWarningCheckbox.set_active( self.showWerewolfWarning )
        showWerewolfWarningCheckbox.set_tooltip_text( _( "Hourly screen notification leading up to full moon." ) )
        grid.attach( showWerewolfWarningCheckbox, 0, 4, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Summary" ) )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        box.pack_start( label, False, False, 0 )

        werewolfNotificationSummaryText = Gtk.Entry()
        werewolfNotificationSummaryText.set_text( self.werewolfWarningSummary )
        werewolfNotificationSummaryText.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        werewolfNotificationSummaryText.set_tooltip_text( _( "The summary for the werewolf notification.\n\n" ) + notifyOSDInformation )
        box.pack_start( werewolfNotificationSummaryText, True, True, 0 )
        grid.attach( box, 0, 5, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", self.onCheckbox, label, werewolfNotificationSummaryText )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_TEXT_LEFT )

        label = Gtk.Label( _( "Message" ) + "\n \n " ) # Padding to ensure the textview for the message text is not too small.   
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

        showWerewolfWarningCheckbox.connect( "toggled", self.onCheckbox, label, werewolfNotificationMessageText )

        test = Gtk.Button( _( "Test" ) )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        test.connect( "clicked", self.onTestNotificationClicked, werewolfNotificationSummaryText, werewolfNotificationMessageText, True )
        test.set_tooltip_text( _( "Show the notification using the current summary/message." ) )
        grid.attach( test, 0, 7, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", self.onCheckbox, test, test )

        notebook.append_page( grid, Gtk.Label( _( "Notifications" ) ) )

        # Location.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label( _( "City" ) ), False, False, 0 )

        city = Gtk.ComboBoxText.new_with_entry()
        city.set_tooltip_text( _(
            "Choose a city from the list.\n" + \
            "Or, add in your own city name." ) )

        cities = astropyephem.AstroPyephem.getCities()
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

        autostartCheckbox = self.createAutostartCheckbox() 
        grid.attach( autostartCheckbox, 0, 4, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

#TODO Need a loop still?
        while True:
            responseType = dialog.run()
            if responseType != Gtk.ResponseType.OK:
                break

            cityValue = city.get_active_text()
            if cityValue == "":
                self.showMessage( dialog, _( "City cannot be empty." ) )
                notebook.set_current_page( TAB_GENERAL )
                city.grab_focus()
                continue

            latitudeValue = latitude.get_text().strip()
            if latitudeValue == "" or not self.isNumber( latitudeValue ) or float( latitudeValue ) > 90 or float( latitudeValue ) < -90:
                self.showMessage( dialog, _( "Latitude must be a number between 90 and -90 inclusive." ) )
                notebook.set_current_page( TAB_GENERAL )
                latitude.grab_focus()
                continue

            longitudeValue = longitude.get_text().strip()
            if longitudeValue == "" or not self.isNumber( longitudeValue ) or float( longitudeValue ) > 180 or float( longitudeValue ) < -180:
                self.showMessage( dialog, _( "Longitude must be a number between 180 and -180 inclusive." ) )
                notebook.set_current_page( TAB_GENERAL )
                longitude.grab_focus()
                continue

            elevationValue = elevation.get_text().strip()
            if elevationValue == "" or not self.isNumber( elevationValue ) or float( elevationValue ) > 10000 or float( elevationValue ) < 0:
                self.showMessage( dialog, _( "Elevation must be a number between 0 and 10000 inclusive." ) )
                notebook.set_current_page( TAB_GENERAL )
                elevation.grab_focus()
                continue

#TODO Need a function that finds tags for satellites and then removes the name and int desig.  Do this after the translate function.
#             self.indicatorText = self.translateTags( displayTagsStore, False, indicatorText.get_text() )
            self.hideBodiesBelowHorizon = hideBodiesBelowTheHorizonCheckbox.get_active()
            self.magnitude = spinnerMagnitude.get_value_as_int()
            self.cometsAddNew = cometsAddNewCheckbox.get_active() # The update will add in new comets.
            self.minorPlanetsAddNew = minorPlanetsAddNewCheckbox.get_active() # The update will add in new minor planets.
            self.satellitesSortByDateTime = sortSatellitesByDateTimeCheckbox.get_active()
            self.satellitesAddNew = satellitesAddNewCheckbox.get_active() # The update will add in new satellites.

            self.planets = [ ]
            for row in planetStore:
                if row[ 0 ]:
                    self.planets.append( row[ 1 ] )

            self.stars = [ ]
            for row in starStore:
                if row[ 0 ]:
                    self.stars.append( row[ 1 ] )

            self.comets = [ ]
            if not self.cometsAddNew:
                for comet in cometStore:
                    if comet[ 0 ]:
                        self.comets.append( comet[ 1 ].upper() )
 
            self.minorPlanets = [ ]
            if not self.minorPlanetsAddNew:
                for minorPlanet in minorPlanetStore:
                    if minorPlanet[ 0 ]:
                        self.minorPlanets.append( minorPlanet[ 1 ].upper() )
 
            self.satellites = [ ]
            if not self.satellitesAddNew:
                for satellite in satelliteStore:
                    if satellite[ 0 ]:
                        self.satellites.append( satellite[ 2 ] )

            self.showSatelliteNotification = showSatelliteNotificationCheckbox.get_active()
            self.satelliteNotificationSummary = self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, False, satelliteNotificationSummaryText.get_text() )
            self.satelliteNotificationMessage = self.translateTags( IndicatorLunar.SATELLITE_TAG_TRANSLATIONS, False, self.getTextViewText( satelliteNotificationMessageText ) )

            self.showWerewolfWarning = showWerewolfWarningCheckbox.get_active()
            self.werewolfWarningSummary = werewolfNotificationSummaryText.get_text()
            self.werewolfWarningMessage = self.getTextViewText( werewolfNotificationMessageText )

            self.city = cityValue
            self.latitude = float( latitudeValue )
            self.longitude = float( longitudeValue )
            self.elevation = float( elevationValue )

            self.setAutoStart( autostartCheckbox.get_active() )
            break

        return responseType


#TODO Satellites now have ':' between name, number and intl desig.  
#Check this doesn't break the double click adding to the indicator text.
#Check no satellite contains a : in the name or anywhere...if it does, then what?  Drop it?
#Handle : when converting tags back and forth for the label text (in the preferences and when rendering.
    def initialiseDisplayTagsStore( self, displayTagsStore ):
        # Populate the display store using current data.
        for key in self.data.keys():
            if key[ 2 ] not in astrobase.AstroBase.DATA_TAGS_INTERNAL:

                bodyType = key[ 0 ]
                bodyTag = key[ 1 ]
                dataTag = key[ 2 ]
                value = self.getDisplayData( key )

                if bodyType == astrobase.AstroBase.BodyType.COMET or \
                   bodyType == astrobase.AstroBase.BodyType.MINOR_PLANET: # Don't translate the names.
                    translatedTag = bodyTag + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ]

                elif bodyType == astrobase.AstroBase.BodyType.SATELLITE: # Don't translate names; add in name/designator.
                    satelliteName = self.satelliteData[ bodyTag ].getName()
                    satelliteInternationalDesignator = self.satelliteData[ bodyTag ].getInternationalDesignator()
                    translatedTag = satelliteName + " : " + bodyTag + " : " + satelliteInternationalDesignator + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ]

                else:
                    translatedTag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ bodyTag ] + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ]

                displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, value ] )

        # Add in bodyTags/dataTags which are not present in the current data.
        items = [ [ astrobase.AstroBase.BodyType.COMET, self.cometData, astrobase.AstroBase.DATA_TAGS_COMET ],
                  [ astrobase.AstroBase.BodyType.MINOR_PLANET, self.minorPlanetData, astrobase.AstroBase.DATA_TAGS_MINOR_PLANET ] ]

        for item in items:
            bodyType = item[ 0 ]
            bodyTags = item[ 1 ]
            dataTags = item[ 2 ]
            for bodyTag in bodyTags:
                for dataTag in dataTags:
                    if not ( bodyType, bodyTag, dataTag ) in self.data:
                        translatedTag = bodyTag + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ]
                        displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, "" ] )

        bodyType = astrobase.AstroBase.BodyType.SATELLITE
        for bodyTag in self.satelliteData:
            for dataTag in astrobase.AstroBase.DATA_TAGS_SATELLITE:
                if not ( astrobase.AstroBase.BodyType.SATELLITE, bodyTag, dataTag ) in self.data:
                    satelliteName = self.satelliteData[ bodyTag ].getName()
                    satelliteInternationalDesignator = self.satelliteData[ bodyTag ].getInternationalDesignator()
                    translatedTag = satelliteName + " : " + bodyTag + " : " + satelliteInternationalDesignator + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ]
                    displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, "" ] )

        items = [ [ astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON, astrobase.AstroBase.DATA_TAGS_MOON ],
                  [ astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN, astrobase.AstroBase.DATA_TAGS_SUN ] ]

        for item in items:
            bodyType = item[ 0 ]
            bodyTag = item[ 1 ]
            dataTags = item[ 2 ]
            for dataTag in dataTags:
                if not ( bodyType, bodyTag, dataTag ) in self.data:
                    translatedTag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ bodyTag ] + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ]
                    displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, "" ] )

        items = [ [ astrobase.AstroBase.BodyType.PLANET, astrobase.AstroBase.PLANETS, astrobase.AstroBase.DATA_TAGS_PLANET ],
                  [ astrobase.AstroBase.BodyType.STAR, astrobase.AstroBase.STARS, astrobase.AstroBase.DATA_TAGS_STAR ] ]

        for item in items:
            bodyType = item[ 0 ]
            bodyTags = item[ 1 ]
            dataTags = item[ 2 ]
            for bodyTag in bodyTags:
                for dataTag in dataTags:
                    if not ( bodyType, bodyTag, dataTag ) in self.data:
                        translatedTag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ bodyTag ] + " " + IndicatorLunar.DATA_TAGS_TRANSLATIONS[ dataTag ]
                        displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, "" ] )


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
            while iter:
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


    def createTable( self, listStore, toolTipText, columnHeaderText, columnIndex ):
        tree = Gtk.TreeView( listStore )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( toolTipText )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onCheckbox, listStore, None, None )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, listStore )
        tree.append_column( treeViewColumn )

        tree.append_column( Gtk.TreeViewColumn( columnHeaderText, Gtk.CellRendererText(), text = columnIndex ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        return scrolledWindow


    def onCheckbox( self, widget, row, dataStore, sortStore = None, bodyType = None ):
        if bodyType == astrobase.AstroBase.BodyType.SATELLITE:
            actualRow = sortStore.convert_path_to_child_path( Gtk.TreePath.new_from_string( row ) ) # Convert sorted model index to underlying (child) model index.
            dataStore[ actualRow ][ 0 ] = not dataStore[ actualRow ][ 0 ]

        else: # Planet, star, comet, minor planet.
            dataStore[ row ][ 0 ] = not dataStore[ row ][ 0 ]


    def onColumnHeaderClick( self, widget, dataStore ):
        atLeastOneItemChecked = False
        atLeastOneItemUnchecked = False
        for row in range( len( dataStore ) ):
            if dataStore[ row ][ 0 ]:
                atLeastOneItemChecked = True

            if not dataStore[ row ][ 0 ]:
                atLeastOneItemUnchecked = True

        if atLeastOneItemChecked and atLeastOneItemUnchecked: # Mix of values checked and unchecked, so check all.
            value = True

        elif atLeastOneItemChecked: # No items checked (so all are unchecked), so check all.
            value = False

        else: # No items unchecked (so all are checked), so uncheck all.
            value = True

        for row in range( len( dataStore ) ):
            dataStore[ row ][ 0 ] = value


    def onTestNotificationClicked( self, button, summaryEntry, messageTextView, isFullMoon ):
        summary = summaryEntry.get_text()
        message = self.getTextViewText( messageTextView )

        if isFullMoon:
            if not os.path.exists( IndicatorLunar.ICON_FULL_MOON ):
                svgFile = IndicatorLunar.ICON_FULL_MOON
                self.createIcon( 100, None, svgFile )

        else:
            svgFile = IndicatorLunar.ICON_SATELLITE

            utcNow = str( datetime.datetime.utcnow() )
            if utcNow.index( '.' ) > -1:
                utcNow = utcNow.split( '.' )[ 0 ] # Remove fractional seconds.

            utcNowPlusTenMinutes = str( datetime.datetime.utcnow() + datetime.timedelta( minutes = 10 ) )
            if utcNowPlusTenMinutes.index( '.' ) > -1:
                utcNowPlusTenMinutes = utcNowPlusTenMinutes.split( '.' )[ 0 ] # Remove fractional seconds.

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

#TODO Hit test for werewolf warning and all good.
#Did it a second time and got an error that svgFile was invalid.
# local variable 'svgFile' referenced before assignment
        Notify.Notification.new( summary, message, svgFile ).show()


    def onCityChanged( self, combobox, latitude, longitude, elevation ):
        city = combobox.get_active_text()
        if city in astropyephem.AstroPyephem.getCities(): 
            theLatitude, theLongitude, theElevation = astropyephem.AstroPyephem.getLatitudeLongitudeElevation( city )
            latitude.set_text( str( theLatitude ) )
            longitude.set_text( str( theLongitude ) )
            elevation.set_text( str( theElevation ) )


    def addNewBodies( self, data, bodies ):
        for body in data:
            if body not in bodies:
                bodies.append( body )


    def getDefaultCity( self ):
        try:
            timezone = self.processGet( "cat /etc/timezone" )
            theCity = None
            cities = astropyephem.AstroPyephem.getCities()
            for city in cities:
                if city in timezone:
                    theCity = city
                    break

            if theCity is None or not theCity:
                theCity = cities[ 0 ]

        except Exception as e:
            self.getLogging().exception( e )
            self.getLogging().error( "Error getting default city." )
            theCity = cities[ 0 ]

        return theCity


    def loadConfig( self, config ):
        self.city = config.get( IndicatorLunar.CONFIG_CITY_NAME ) # Returns None if the key is not found.
        if self.city is None:
            self.city = self.getDefaultCity()
            self.latitude, self.longitude, self.elevation = astropyephem.AstroPyephem.getLatitudeLongitudeElevation( self.city )

        else:
            self.elevation = config.get( IndicatorLunar.CONFIG_CITY_ELEVATION )
            self.latitude = config.get( IndicatorLunar.CONFIG_CITY_LATITUDE )
            self.longitude = config.get( IndicatorLunar.CONFIG_CITY_LONGITUDE )

        self.comets = config.get( IndicatorLunar.CONFIG_COMETS, [ ] )
        self.cometsAddNew = config.get( IndicatorLunar.CONFIG_COMETS_ADD_NEW, False )

        self.hideBodiesBelowHorizon = config.get( IndicatorLunar.CONFIG_HIDE_BODIES_BELOW_HORIZON, False )

        self.indicatorText = config.get( IndicatorLunar.CONFIG_INDICATOR_TEXT, IndicatorLunar.INDICATOR_TEXT_DEFAULT )

        self.minorPlanets = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS, [ ] )
        self.minorPlanetsAddNew = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS_ADD_NEW, False )

        self.magnitude = config.get( IndicatorLunar.CONFIG_MAGNITUDE, 4 ) # Although a value of 6 is visible with the naked eye, that gives too many minor planets initially.

        self.planets = config.get( IndicatorLunar.CONFIG_PLANETS, astrobase.AstroBase.PLANETS[ : 6 ] ) # Drop Neptune and Pluto as not visible with naked eye.

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

        self.requestSaveConfig() #TODO Need to do a request here to save.
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

        return {
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


IndicatorLunar().main()