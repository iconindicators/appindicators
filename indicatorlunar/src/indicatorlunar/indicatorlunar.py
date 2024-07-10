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


#TODO On the laptop I think the update does not work
# when the preferences is opened.
# The menu does not initially go grey
# and then on hitting OK,
# the menu does not get restored.
# Difficult to reproduce.


# Application indicator for the home astronomer.


from indicatorbase import IndicatorBase # MUST BE THE FIRST IMPORT!

import datetime
import gi

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

import locale
import math
import re
import requests
import webbrowser

from dataproviderapparentmagnitude import DataProviderApparentMagnitude
from dataprovidergeneralperturbation import DataProviderGeneralPerturbation
from dataproviderorbitalelement import DataProviderOrbitalElement, OE

import eclipse


class IndicatorLunar( IndicatorBase ):
    # Unused within the indicator; used by build_wheel.py when building the .desktop file.
    indicator_name_for_desktop_file = _( "Indicator Lunar" )

    # Allow switching between backends.
    astro_backend_pyephem = "AstroPyEphem"
    astro_backend_skyfield = "AstroSkyfield"
    astro_backend_name = astro_backend_pyephem
    astro_backend = getattr( __import__( astro_backend_name.lower() ), astro_backend_name )

    CONFIG_CITY_ELEVATION = "cityElevation"
    CONFIG_CITY_LATITUDE = "cityLatitude"
    CONFIG_CITY_LONGITUDE = "cityLongitude"
    CONFIG_CITY_NAME = "cityName"
    CONFIG_COMETS = "comets"
    CONFIG_COMETS_ADD_NEW = "cometsAddNew"
    CONFIG_MAGNITUDE = "magnitude"
    CONFIG_MINOR_PLANETS = "minorPlanets"
    CONFIG_MINOR_PLANETS_ADD_NEW = "minorPlanetsAddNew"
    CONFIG_HIDE_BODIES_BELOW_HORIZON = "hideBodiesBelowHorizon"
    CONFIG_INDICATOR_TEXT = "indicatorText"
    CONFIG_INDICATOR_TEXT_SEPARATOR = "indicatorTextSeparator"
    CONFIG_PLANETS = "planets"
    CONFIG_SATELLITE_NOTIFICATION_MESSAGE = "satelliteNotificationMessage"
    CONFIG_SATELLITE_NOTIFICATION_SUMMARY = "satelliteNotificationSummary"
    CONFIG_SATELLITE_LIMIT_START = "satelliteLimitStart"
    CONFIG_SATELLITE_LIMIT_END = "satelliteLimitEnd"
    CONFIG_SATELLITES = "satellites"
    CONFIG_SATELLITES_ADD_NEW = "satellitesAddNew"
    CONFIG_SATELLITES_SORT_BY_DATE_TIME = "satellitesSortByDateTime"
    CONFIG_SHOW_RISE_WHEN_SET_BEFORE_SUNSET = "showRiseWhenSetBeforeSunset"
    CONFIG_SHOW_SATELLITE_NOTIFICATION = "showSatelliteNotification"
    CONFIG_SHOW_WEREWOLF_WARNING = "showWerewolfWarning"
    CONFIG_STARS = "stars"
    CONFIG_WEREWOLF_WARNING_MESSAGE = "werewolfWarningMessage"
    CONFIG_WEREWOLF_WARNING_SUMMARY = "werewolfWarningSummary"

    CREDIT_COMETS = _( "Comet data by Comet Observation Database. https://cobs.si" )
    CREDIT_ECLIPSES = _( "Eclipse predictions by Fred Espenak, NASA/GSFC Emeritus. https://eclipse.gsfc.nasa.gov" )
    CREDIT_ECLIPSE_SOLAR_ONLY = _( "Solar eclipse predictions by Fred Espenak, NASA/GSFC Emeritus. https://eclipse.gsfc.nasa.gov" )
    CREDIT_MINOR_PLANETS = _( "Minor Planet data by Lowell Minor Planet Services. https://asteroid.lowell.edu" )
    CREDIT_SATELLITES = _( "Satellite data by Celestrak. https://celestrak.org" )
    if astro_backend_name == astro_backend_pyephem:
        CREDIT = [ astro_backend.get_credit(),
                  CREDIT_COMETS,
                  CREDIT_ECLIPSES,
                  CREDIT_MINOR_PLANETS,
                  CREDIT_SATELLITES ]

    else:
        CREDIT = [ astro_backend.get_credit(),
                  CREDIT_COMETS,
                  CREDIT_ECLIPSE_SOLAR_ONLY,
                  CREDIT_MINOR_PLANETS,
                  CREDIT_SATELLITES ]

    DATA_INDEX_BODY_TYPE = 0
    DATA_INDEX_BODY_NAME = 1
    DATA_INDEX_DATA_NAME = 2

    DATE_TIME_FORMAT_HHcolonMM = "%H:%M" # Used in the display of the satellite rise notification.
    DATE_TIME_FORMAT_YYYYdashMMdashDDspacespaceHHcolonMM = "%Y-%m-%d  %H:%M" # Used to display any body's rise/set in the menu.

    ICON_CACHE_BASENAME = "icon-"
    ICON_CACHE_MAXIMUM_AGE_HOURS = 1 # Keep icons around for an hour to allow multiple instances to run (when testing for example).

    INDICATOR_TEXT_DEFAULT = " [" + astro_backend.NAME_TAG_MOON + " " + astro_backend.DATA_TAG_PHASE + "]"
    INDICATOR_TEXT_SEPARATOR_DEFAULT = ", "

    BODY_TAGS_TRANSLATIONS = \
        dict(
            list( astro_backend.NAME_TAG_MOON_TRANSLATION.items() ) +
            list( astro_backend.PLANET_TAGS_TRANSLATIONS.items() ) +
            [ x for x in zip( astro_backend.get_star_names(), astro_backend.get_star_tag_translations() ) ] +
            list( astro_backend.NAME_TAG_SUN_TRANSLATION.items() ) )

    CACHE_VERSION = "-96-"

    COMET_CACHE_APPARENT_MAGNITUDE_BASENAME = "comet-apparentmagnitude" + CACHE_VERSION
    COMET_CACHE_ORBITAL_ELEMENT_BASENAME = "comet-orbitalelement" + '-' + astro_backend_name.lower() + CACHE_VERSION
    COMET_CACHE_MAXIMUM_AGE_HOURS = 96
    COMET_DATA_TYPE = \
        OE.DataType.XEPHEM_COMET \
        if astro_backend_name == astro_backend_pyephem else \
        OE.DataType.SKYFIELD_COMET

    MINOR_PLANET_CACHE_APPARENT_MAGNITUDE_BASENAME = "minorplanet-apparentmagnitude" + CACHE_VERSION
    MINOR_PLANET_CACHE_ORBITAL_ELEMENT_BASENAME = \
        "minorplanet-orbitalelement" + '-' + astro_backend_name.lower() + CACHE_VERSION
    MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS = 96
    MINOR_PLANET_DATA_TYPE = \
        OE.DataType.XEPHEM_MINOR_PLANET \
        if astro_backend_name == astro_backend_pyephem else \
        OE.DataType.SKYFIELD_MINOR_PLANET

    SATELLITE_CACHE_BASENAME = "satellite-generalperturbation" + CACHE_VERSION
    SATELLITE_CACHE_EXTENSION = ".xml"
    SATELLITE_CACHE_MAXIMUM_AGE_HOURS = 48

    SATELLITE_NOTIFICATION_MESSAGE_DEFAULT = \
        _( "Rise Time: " ) + astro_backend.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n" + \
        _( "Rise Azimuth: " ) + astro_backend.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\n" + \
        _( "Set Time: " ) + astro_backend.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n" + \
        _( "Set Azimuth: " ) + astro_backend.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION

    SATELLITE_NOTIFICATION_SUMMARY_DEFAULT = \
        astro_backend.SATELLITE_TAG_NAME + " : " + \
        astro_backend.SATELLITE_TAG_NUMBER + " : " + \
        astro_backend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR + " " + _( "now rising..." )

    # The satellite menu contains the satellite number then satellite name,
    # followed by other items depending on the satellite's status (rising, in transit or always up).
    SATELLITE_MENU_NUMBER = 0
    SATELLITE_MENU_NAME = 1

    SATELLITE_MENU_RISE_DATE_TIME = 2
    SATELLITE_MENU_RISE_AZIMUTH = 3
    SATELLITE_MENU_SET_DATE_TIME = 4
    SATELLITE_MENU_SET_AZIMUTH = 5

    SATELLITE_MENU_AZIMUTH = 2
    SATELLITE_MENU_ALTITUDE = 3

    SEARCH_URL_COMET_DATABASE = "https://cobs.si/api/comet.api?des="
    SEARCH_URL_COMET_ID = "https://cobs.si/comet/"
    SEARCH_URL_MINOR_PLANET = "https://asteroid.lowell.edu/astinfo/"
    SEARCH_URL_MOON = "https://solarsystem.nasa.gov/moons/earths-moon"
    SEARCH_URL_PLANET = "https://solarsystem.nasa.gov/planets/"
    SEARCH_URL_SATELLITE = "https://www.heavens-above.com/PassSummary.aspx?"
    SEARCH_URL_STAR = "https://simbad.u-strasbg.fr/simbad/sim-id?Ident=HIP+"
    SEARCH_URL_SUN = "https://solarsystem.nasa.gov/solar-system/sun"

    WEREWOLF_WARNING_MESSAGE_DEFAULT = _( "                                          ...werewolves about ! ! !" )
    WEREWOLF_WARNING_SUMMARY_DEFAULT = _( "W  A  R  N  I  N  G" )


    def __init__( self ):
        super().__init__(
            debug = True, # TODO Remove for production.
            comments = _( "Displays lunar, solar, planetary, minor planet, comet, star and satellite information." ),
            creditz = IndicatorLunar.CREDIT )

        # Dictionary to hold currently calculated (and previously calculated) astronomical data.
        # Key: combination of three tags: body type, body name and data name.
        # Value: a string for all data types, EXCEPT for date/time which is a Python datetime in UTC with timezone.
        # Previous data is used for satellite transits.
        self.data = None
        self.data_previous = None

        self.comet_orbital_element_data = { } # Key: comet designation; Value: OE object.  Can be empty but never None.
        self.minor_planet_apparent_magnitude_data = { } # Key: minor planet designation; Value AM object.  Can be empty but never None.
        self.minor_planet_orbital_element_data = { } # Key: minor planet designation; Value: OE object.  Can be empty but never None.
        self.satellite_general_perturbation_data = { } # Key: satellite number; Value: GP object.  Can be empty but never None.
        self.satellite_previous_notifications = [ ]

        self.last_full_moon_notfication = \
            datetime.datetime.now( datetime.timezone.utc ) - datetime.timedelta( hours = 1 )

        self.icon_satellite = self.get_icon_name().replace( "-symbolic", "satellite-symbolic" )

        self.flush_the_cache()
        self.initialise_download_counts_and_cache_date_times()

        # On comet lookup and download of comet / minor planet data,
        # an unnecessary log message is created, so ignore.
        self.get_logging().getLogger( "urllib3" ).propagate = False


    def flush_the_cache( self ):
        self.flush_cache(
            IndicatorLunar.COMET_CACHE_ORBITAL_ELEMENT_BASENAME,
            IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS )

        self.flush_cache(
            IndicatorLunar.ICON_CACHE_BASENAME,
            IndicatorLunar.ICON_CACHE_MAXIMUM_AGE_HOURS )

        self.flush_cache(
            IndicatorLunar.MINOR_PLANET_CACHE_APPARENT_MAGNITUDE_BASENAME,
            IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )

        self.flush_cache(
            IndicatorLunar.MINOR_PLANET_CACHE_ORBITAL_ELEMENT_BASENAME,
            IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )

        self.flush_cache(
            IndicatorLunar.SATELLITE_CACHE_BASENAME,
            IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS )


    def initialise_download_counts_and_cache_date_times( self ):
        self.download_count_apparent_magnitude = 0
        self.download_count_comet = 0
        self.download_count_minor_planet = 0
        self.download_count_satellite = 0

        utc_now = datetime.datetime.now( datetime.timezone.utc )
        self.next_download_time_apparent_magnitude = utc_now
        self.next_download_time_comet = utc_now
        self.next_download_time_minor_planet = utc_now
        self.next_download_time_satellite = utc_now


    def update( self, menu ):
        utc_now = datetime.datetime.now( datetime.timezone.utc )

        # Update comet minor planet and satellite cached data.
        self.update_data( utc_now )

        # Update backend.
        self.data_previous = self.data
        self.data = \
            IndicatorLunar.astro_backend.calculate(
                utc_now,
                self.latitude, self.longitude, self.elevation,
                self.planets,
                self.stars,
                self.satellites, self.satellite_general_perturbation_data,
                *self.convert_start_hour_and_end_hour_to_date_time_in_utc(
                    self.satellite_limit_start, self.satellite_limit_end ),
                self.comets, self.comet_orbital_element_data, None,
                self.minor_planets, self.minor_planet_orbital_element_data, self.minor_planet_apparent_magnitude_data,
                self.magnitude,
                self.get_logging() )

        if self.data_previous is None: # Happens only on first run or when the user alters the satellite visibility window.
            self.data_previous = self.data

        # Update frontend.
        if self.is_debug():
            self.create_and_append_menuitem(
                menu,
                IndicatorLunar.astro_backend_name + ": " + IndicatorLunar.astro_backend.get_version() )

        self.update_menu( menu, utc_now )
        self.set_label( self.process_tags() )

        if self.is_icon_update_supported():
            self.update_icon()

        if self.show_werewolf_warning:
            self.notification_full_moon()

        if self.show_satellite_notification:
            self.notification_satellites()

        return self.get_next_update_time_in_seconds()


    def update_data( self, utc_now ):
        # Update comet data.
        self.comet_orbital_element_data, self.download_count_comet, self.next_download_time_comet = \
            self.__update_data(
                utc_now,
                self.comet_orbital_element_data,
                IndicatorLunar.COMET_CACHE_ORBITAL_ELEMENT_BASENAME,
                IndicatorBase.EXTENSION_TEXT,
                IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS,
                self.download_count_comet,
                self.next_download_time_comet,
                DataProviderOrbitalElement.download,
                [ IndicatorLunar.COMET_DATA_TYPE, IndicatorLunar.astro_backend.MAGNITUDE_MAXIMUM ],
                DataProviderOrbitalElement.load,
                [ IndicatorLunar.COMET_DATA_TYPE ] )

        if self.comets_add_new:
            self.add_new_bodies( self.comet_orbital_element_data, self.comets )

        # Update minor planet data.
        self.minor_planet_orbital_element_data, self.download_count_minor_planet, self.next_download_time_minor_planet = \
            self.__update_data(
                utc_now,
                self.minor_planet_orbital_element_data,
                IndicatorLunar.MINOR_PLANET_CACHE_ORBITAL_ELEMENT_BASENAME,
                IndicatorBase.EXTENSION_TEXT, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS,
                self.download_count_minor_planet,
                self.next_download_time_minor_planet,
                DataProviderOrbitalElement.download,
                [ IndicatorLunar.MINOR_PLANET_DATA_TYPE, IndicatorLunar.astro_backend.MAGNITUDE_MAXIMUM ],
                DataProviderOrbitalElement.load,
                [ IndicatorLunar.MINOR_PLANET_DATA_TYPE ] )

        if self.minor_planets_add_new:
            self.add_new_bodies( self.minor_planet_orbital_element_data, self.minor_planets )

        # Update minor planet apparent magnitudes.
        self.minor_planet_apparent_magnitude_data, self.download_count_apparent_magnitude, self.next_download_time_apparent_magnitude = \
            self.__update_data(
                utc_now,
                self.minor_planet_apparent_magnitude_data,
                IndicatorLunar.MINOR_PLANET_CACHE_APPARENT_MAGNITUDE_BASENAME,
                IndicatorBase.EXTENSION_TEXT, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS,
                self.download_count_apparent_magnitude,
                self.next_download_time_apparent_magnitude,
                DataProviderApparentMagnitude.download,
                [ False, IndicatorLunar.astro_backend.MAGNITUDE_MAXIMUM ],
                DataProviderApparentMagnitude.load,
                [ ] )

        # Update satellite data.
        self.satellite_general_perturbation_data, self.download_count_satellite, self.next_download_time_satellite = \
            self.__update_data(
                utc_now,
                self.satellite_general_perturbation_data,
                IndicatorLunar.SATELLITE_CACHE_BASENAME,
                IndicatorLunar.SATELLITE_CACHE_EXTENSION,
                IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS,
                self.download_count_satellite,
                self.next_download_time_satellite,
                DataProviderGeneralPerturbation.download,
                [ ],
                DataProviderGeneralPerturbation.load,
                [ ] )

        if self.satellites_add_new:
            self.add_new_bodies( self.satellite_general_perturbation_data, self.satellites )


    # Get the data from the cache, or if stale, download from the source.
    def __update_data(
            self, utc_now, current_data,
            cache_basename, cache_extension, cache_maximum_age,
            download_count, next_download_time,
            download_data_function, download_data_additional_arguments,
            load_data_function, load_data_additional_arguments ):

        if self.is_cache_stale( utc_now, cache_basename, cache_maximum_age ):
            fresh_data = { }
            if next_download_time < utc_now: # Download is allowed (do not want to annoy third-party data provider).
                download_data_filename = self.get_cache_filename_with_timestamp( cache_basename, cache_extension )
                if download_data_function( download_data_filename, self.get_logging(), *download_data_additional_arguments ):
                    download_count = 0
                    next_download_time = utc_now + datetime.timedelta( hours = cache_maximum_age )
                    fresh_data = load_data_function( download_data_filename, self.get_logging(), *load_data_additional_arguments )

                else:
                    download_count += 1
                    next_download_time = self.__get_next_download_time( utc_now, download_count ) # Download failed for some reason; retry at a later time.

        else:
            # Cache is not stale; only load off disk as necessary.
            if current_data:
                fresh_data = current_data

            else:
                download_data_filename = self.get_cache_newest_filename( cache_basename ) # Should NOT return None as the cache was checked for staleness above.
                fresh_data = load_data_function( download_data_filename, self.get_logging(), *load_data_additional_arguments )

        return fresh_data, download_count, next_download_time


    def __get_next_download_time( self, utc_now, download_count ):
        next_download_time = utc_now + datetime.timedelta( minutes = 60 * 24 ) # Worst case scenario for retrying downloads: every 24 hours.
        time_interval_in_minutes = {
            1 : 5,
            2 : 15,
            3 : 60 }

        if download_count in time_interval_in_minutes:
            next_download_time = utc_now + datetime.timedelta( minutes = time_interval_in_minutes[ download_count ] )

        return next_download_time


    def add_new_bodies( self, data, bodies ):
        for body in data:
            if body not in bodies:
                bodies.append( body )


    # Process text containing pairs of [ ], optionally surrounded by { }, typically used for display in the indicator's label.
    #
    # The text may contain tags, delimited by '[' and ']' to be processed by the caller.
    # The caller must provide a 'process tags' function, taking optional arguments.
    #
    # Free text may be associated with any number of tags, all of which are to be enclosed with '{' and '}'.
    # If all tags within '{' and '}' are not replaced, all text (and tags) within is removed.
    # This ensures a tag which cannot be processed does not cause the text to hang around.
    #
    # The 'process tags' function is passed the text along with optional arguments and
    # must then return the processed text.
    def process_tags( self ):
        # Handle [ ].
        # There may still be tags left in as a result of say a satellite or comet dropping out.
        # Remaining tags are moped up at the end.
        processed_text = self.indicator_text
        for key in self.data.keys():
            tag = "[" + key[ IndicatorLunar.DATA_INDEX_BODY_NAME ] + " " + key[ IndicatorLunar.DATA_INDEX_DATA_NAME ] + "]"
            if tag in processed_text:
                data = self.format_data( key[ IndicatorLunar.DATA_INDEX_DATA_NAME ], self.data[ key ] )
                processed_text = processed_text.replace( tag, data )

        # Handle text enclosed by { }.
        i = 0
        last_separator_index = -1 # Track the last insertion point of the separator so it can be removed.
        tag_regular_expression = "\[[^\[\]]*\]"
        while( i < len( processed_text ) ):
            if processed_text[ i ] == '{':
                j = i + 1
                while( j < len( processed_text ) ):
                    if processed_text[ j ] == '}':
                        text = processed_text[ i + 1 : j ] # Text between braces.
                        text_minus_unknown_tags = re.sub( tag_regular_expression, "", text ) # Text between braces with outstanding/unknown tags removed.
                        if len( text ) and text == text_minus_unknown_tags: # Text is not empty and no unknown tags found, so keep this text.
                            processed_text = processed_text[ 0 : i ] + processed_text[ i + 1 : j ] + self.indicator_text_separator + processed_text[ j + 1 : ]
                            last_separator_index = j - 1

                        else: # Empty text or there was one or more unknown tags found, so drop the text.
                            processed_text = processed_text[ 0 : i ] + processed_text[ j + 1 : ]

                        i -= 1
                        break

                    j += 1

            i += 1

        if last_separator_index > -1:
            processed_text = processed_text[ 0 : last_separator_index ] + processed_text[ last_separator_index + len( self.indicator_text_separator ) : ] # Remove the last separator.

        processed_text = re.sub( tag_regular_expression, "", processed_text ) # Remove remaining tags (not removed because they were not contained within { }).
        return processed_text


    def get_next_update_time_in_seconds( self ):
        date_times = [ ]
        for key in self.data:
            data_name = key[ IndicatorLunar.DATA_INDEX_DATA_NAME ]
            if key[ IndicatorLunar.DATA_INDEX_BODY_TYPE ] == IndicatorLunar.astro_backend.BodyType.SATELLITE:
                if data_name == IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME:
                    date_time = self.data[ key ]
                    date_time_minus_four_minutes = date_time - datetime.timedelta( minutes = 4 ) # Set an earlier time for the rise to ensure the rise and set are displayed.
                    date_times.append( date_time_minus_four_minutes )

                elif data_name == IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME:
                    date_times.append( self.data[ key ] )

            else:
                if data_name == IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_DATE_TIME or \
                   data_name == IndicatorLunar.astro_backend.DATA_TAG_EQUINOX or \
                   data_name == IndicatorLunar.astro_backend.DATA_TAG_FIRST_QUARTER or \
                   data_name == IndicatorLunar.astro_backend.DATA_TAG_FULL or \
                   data_name == IndicatorLunar.astro_backend.DATA_TAG_NEW or \
                   data_name == IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME or \
                   data_name == IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME or \
                   data_name == IndicatorLunar.astro_backend.DATA_TAG_SOLSTICE or \
                   data_name == IndicatorLunar.astro_backend.DATA_TAG_THIRD_QUARTER:
                    date_times.append( self.data[ key ] )

        utc_now = datetime.datetime.now( datetime.timezone.utc )
        utc_now_plus_one_minute = utc_now + datetime.timedelta( minutes = 1 ) # Ensure updates don't happen more frequently than every minute.
        next_update_time = utc_now + datetime.timedelta( minutes = 20 ) # Do an update at most twenty minutes from now (keeps the moon icon and data fresh).
        next_update_in_seconds = int( math.ceil( ( next_update_time - utc_now ).total_seconds() ) )
        for date_time in sorted( date_times ):
            if date_time > next_update_time:
                break

            if date_time > utc_now_plus_one_minute:
                next_update_time = date_time
                next_update_in_seconds = int( math.ceil( ( next_update_time - utc_now ).total_seconds() ) )
                break

        return next_update_in_seconds


    def update_menu( self, menu, utc_now ):
        self.update_menu_moon( menu )
        self.update_menu_sun( menu )
        self.update_menu_planets_minor_planets_comets_stars( menu, _( "Planets" ), self.planets, None, IndicatorLunar.astro_backend.BodyType.PLANET )
        self.update_menu_planets_minor_planets_comets_stars( menu, _( "Minor Planets" ), self.minor_planets, self.minor_planet_orbital_element_data, IndicatorLunar.astro_backend.BodyType.MINOR_PLANET )
        self.update_menu_planets_minor_planets_comets_stars( menu, _( "Comets" ), self.comets, self.comet_orbital_element_data, IndicatorLunar.astro_backend.BodyType.COMET )
        self.update_menu_planets_minor_planets_comets_stars( menu, _( "Stars" ), self.stars, None, IndicatorLunar.astro_backend.BodyType.STAR )
        self.update_menu_satellites( menu, utc_now )


    def update_icon( self ):
        # Ideally overwrite the icon with the same name each time.
        # Due to a bug, the icon name must change between calls to set the icon.
        # So change the name each time incorporating the current date/time.
        #    https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620
        #    http://askubuntu.com/questions/490634/application-indicator-icon-not-changing-until-clicked
        key = ( IndicatorLunar.astro_backend.BodyType.MOON, IndicatorLunar.astro_backend.NAME_TAG_MOON )
        phase = self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_PHASE, ) ]
        illumination_percentage = int( round( float( self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_ILLUMINATION, ) ] ) ) )
        bright_limb_angle_in_degrees = int( math.degrees( float( self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_BRIGHT_LIMB, ) ] ) ) )

        svg_icon_text = \
            self.get_svg_icon_text(
                phase,
                illumination_percentage,
                bright_limb_angle_in_degrees )

        icon_filename = \
            self.write_cache_text(
                svg_icon_text,
                IndicatorLunar.ICON_CACHE_BASENAME,
                IndicatorBase.EXTENSION_SVG_SYMBOLIC )

        self.set_icon( icon_filename )


    def notification_full_moon( self ):
        utc_now = datetime.datetime.now( datetime.timezone.utc )
        key = ( IndicatorLunar.astro_backend.BodyType.MOON, IndicatorLunar.astro_backend.NAME_TAG_MOON )
        illumination_percentage = int( round( float( self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_ILLUMINATION, ) ] ) ) )
        phase = self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_PHASE, ) ]

        if ( phase == IndicatorLunar.astro_backend.LUNAR_PHASE_WAXING_GIBBOUS or phase == IndicatorLunar.astro_backend.LUNAR_PHASE_FULL_MOON ) and \
           illumination_percentage >= 96 and \
           ( ( self.last_full_moon_notfication + datetime.timedelta( hours = 1 ) ) < utc_now ):

            summary = self.werewolf_warning_summary
            if self.werewolf_warning_summary == "":
                summary = " " # The notification summary text cannot be empty (at least on Unity).

            self.show_notification(
                summary,
                self.werewolf_warning_message,
                icon = self.create_full_moon_icon() )

            self.last_full_moon_notfication = utc_now


    def create_full_moon_icon( self ):
        return \
            self.write_cache_text(
                self.get_svg_icon_text( IndicatorLunar.astro_backend.LUNAR_PHASE_FULL_MOON, None, None ),
                IndicatorLunar.ICON_CACHE_BASENAME,
                IndicatorBase.EXTENSION_SVG_SYMBOLIC )


    def notification_satellites( self ):
        INDEX_NUMBER = 0
        INDEX_RISE_TIME = 1
        satellite_current_notifications = [ ]

        utc_now = datetime.datetime.now( datetime.timezone.utc )
        for number in self.satellites:
            key = ( IndicatorLunar.astro_backend.BodyType.SATELLITE, number )
            if ( key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_AZIMUTH, ) ) in self.data and number not in self.satellite_previous_notifications: # About to rise and no notification already sent.
                rise_time = self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ]
                if ( rise_time - datetime.timedelta( minutes = 2 ) ) <= utc_now: # Two minute buffer.
                    satellite_current_notifications.append( [ number, rise_time ] )
                    self.satellite_previous_notifications.append( number )

            if ( key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ) in self.data:
                set_time = self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ]
                if number in self.satellite_previous_notifications and set_time < utc_now: # Notification has been sent and satellite has now set.
                    self.satellite_previous_notifications.remove( number )

        satellite_current_notifications = \
            sorted( satellite_current_notifications, key = lambda x: ( x[ INDEX_RISE_TIME ], x[ INDEX_NUMBER ] ) )

        for number, rise_time in satellite_current_notifications:
            self.__notification_satellite( number )


    def __notification_satellite( self, number ):
        key = ( IndicatorLunar.astro_backend.BodyType.SATELLITE, number )

        rise_time = \
            self.format_data(
                IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME,
                self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ],
                IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )

        rise_azimuth = \
            self.format_data(
                IndicatorLunar.astro_backend.DATA_TAG_RISE_AZIMUTH,
                self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_AZIMUTH, ) ],
                IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )

        set_time = \
            self.format_data(
                IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME,
                self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ],
                IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )

        set_azimuth = \
            self.format_data(
                IndicatorLunar.astro_backend.DATA_TAG_SET_AZIMUTH,
                self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_AZIMUTH, ) ],
                IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )

        summary = \
            self.satellite_notification_summary. \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_NAME, self.satellite_general_perturbation_data[ number ].get_name() ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_NUMBER, self.satellite_general_perturbation_data[ number ].get_number() ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satellite_general_perturbation_data[ number ].get_international_designator() ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_RISE_AZIMUTH, rise_azimuth ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_RISE_TIME, rise_time ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_SET_AZIMUTH, set_azimuth ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_SET_TIME, set_time ) + \
            " " # The notification summary text must not be empty (at least on Unity).

        message = \
            self.satellite_notification_message. \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_NAME, self.satellite_general_perturbation_data[ number ].get_name() ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_NUMBER, self.satellite_general_perturbation_data[ number ].get_number() ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satellite_general_perturbation_data[ number ].get_international_designator() ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_RISE_AZIMUTH, rise_azimuth ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_RISE_TIME, rise_time ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_SET_AZIMUTH, set_azimuth ). \
            replace( IndicatorLunar.astro_backend.SATELLITE_TAG_SET_TIME, set_time )

        self.show_notification( summary, message, icon = self.icon_satellite )


    def update_menu_moon( self, menu ):
        submenu = Gtk.Menu()
        if self.__update_menu_common( submenu, IndicatorLunar.astro_backend.BodyType.MOON, IndicatorLunar.astro_backend.NAME_TAG_MOON, self.get_menu_indent(), IndicatorLunar.SEARCH_URL_MOON, ( self.get_on_click_menuitem_open_browser_function(), ) ):
            self.create_and_append_menuitem( menu, _( "Moon" ) ).set_submenu( submenu )
            submenu.append( Gtk.SeparatorMenuItem() )
            key = ( IndicatorLunar.astro_backend.BodyType.MOON, IndicatorLunar.astro_backend.NAME_TAG_MOON )

            self.create_and_append_menuitem(
                submenu,
                self.get_menu_indent() +
                _( "Phase: " ) +
                self.format_data( IndicatorLunar.astro_backend.DATA_TAG_PHASE, self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_PHASE, ) ] ),
                name = IndicatorLunar.SEARCH_URL_MOON,
                activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            self.create_and_append_menuitem(
                submenu,
                self.get_menu_indent() + _( "Next Phases" ),
                name = IndicatorLunar.SEARCH_URL_MOON,
                activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            # The phase (illumination) is rounded and so a given phase is entered earlier than what occurs in reality.
            next_phases = [ ]
            next_phases.append(
                [ self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_FIRST_QUARTER, ) ],
                 _( "First Quarter: " ), key + ( IndicatorLunar.astro_backend.DATA_TAG_FIRST_QUARTER, ) ] )

            next_phases.append(
                [ self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_FULL, ) ],
                _( "Full: " ), key + ( IndicatorLunar.astro_backend.DATA_TAG_FULL, ) ] )

            next_phases.append(
                [ self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_NEW, ) ],
                _( "New: " ), key + ( IndicatorLunar.astro_backend.DATA_TAG_NEW, ) ] )

            next_phases.append(
                [ self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_THIRD_QUARTER, ) ],
                _( "Third Quarter: " ), key + ( IndicatorLunar.astro_backend.DATA_TAG_THIRD_QUARTER, ) ] )

            for date_time, display_text, key in sorted( next_phases, key = lambda pair: pair[ 0 ] ): # Sort by date of each phase (the first element).
                label = \
                    self.get_menu_indent( indent = 2 ) + \
                    display_text + \
                    self.format_data( key[ IndicatorLunar.DATA_INDEX_DATA_NAME ], self.data[ key ] )

                self.create_and_append_menuitem(
                    submenu,
                    label,
                    name = IndicatorLunar.SEARCH_URL_MOON,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            self.__update_menu_eclipse( submenu, IndicatorLunar.astro_backend.BodyType.MOON, IndicatorLunar.astro_backend.NAME_TAG_MOON, IndicatorLunar.SEARCH_URL_MOON )


    def update_menu_sun( self, menu ):
        submenu = Gtk.Menu()
        if self.__update_menu_common( submenu, IndicatorLunar.astro_backend.BodyType.SUN, IndicatorLunar.astro_backend.NAME_TAG_SUN, self.get_menu_indent(), IndicatorLunar.SEARCH_URL_SUN, ( self.get_on_click_menuitem_open_browser_function(), ) ):
            self.create_and_append_menuitem( menu, _( "Sun" ) ).set_submenu( submenu )
            submenu.append( Gtk.SeparatorMenuItem() )
            key = ( IndicatorLunar.astro_backend.BodyType.SUN, IndicatorLunar.astro_backend.NAME_TAG_SUN )

            equinox_label = \
                self.get_menu_indent() + \
                _( "Equinox: " ) + \
                self.format_data( IndicatorLunar.astro_backend.DATA_TAG_EQUINOX, self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_EQUINOX, ) ] )

            solstice_label = \
                self.get_menu_indent() + \
                _( "Solstice: " ) + \
                self.format_data( IndicatorLunar.astro_backend.DATA_TAG_SOLSTICE, self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SOLSTICE, ) ] )

            if self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_EQUINOX, ) ] < self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SOLSTICE, ) ]:
                self.create_and_append_menuitem(
                    submenu,
                    equinox_label,
                    name = IndicatorLunar.SEARCH_URL_SUN,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

                self.create_and_append_menuitem(
                    submenu,
                    solstice_label,
                    name = IndicatorLunar.SEARCH_URL_SUN,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            else:
                self.create_and_append_menuitem(
                    submenu,
                    solstice_label,
                    name = IndicatorLunar.SEARCH_URL_SUN,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

                self.create_and_append_menuitem(
                    submenu,
                    equinox_label,
                    name = IndicatorLunar.SEARCH_URL_SUN,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            self.__update_menu_eclipse( submenu, IndicatorLunar.astro_backend.BodyType.SUN, IndicatorLunar.astro_backend.NAME_TAG_SUN, IndicatorLunar.SEARCH_URL_SUN )


    def __update_menu_eclipse( self, menu, body_type, name_tag, url ):
        menu.append( Gtk.SeparatorMenuItem() )
        key = ( body_type, name_tag )

        self.create_and_append_menuitem(
            menu,
            self.get_menu_indent() + _( "Eclipse" ),
            name = url,
            activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

        self.create_and_append_menuitem(
            menu,
            self.get_menu_indent( indent = 2 ) +
            _( "Date/Time: " ) +
            self.format_data( IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_DATE_TIME, self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_DATE_TIME, ) ] ),
            name = url,
            activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

        self.create_and_append_menuitem(
            menu,
            self.get_menu_indent( indent = 2 ) +
            _( "Type: " ) +
            self.format_data( IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_TYPE, self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_TYPE, ) ] ),
            name = url,
            activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

        if key + ( IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_LATITUDE, ) in self.data: # PyEphem uses the NASA Eclipse data which contains latitude/longitude; Skyfield does not.
            latitude = \
                self.format_data(
                    IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_LATITUDE,
                    self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_LATITUDE, ) ] )

            longitude = \
                self.format_data(
                    IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_LONGITUDE,
                    self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_LONGITUDE, ) ] )

            self.create_and_append_menuitem(
                menu,
                self.get_menu_indent( indent = 2 ) + _( "Latitude/Longitude: " ) + latitude + " " + longitude,
                name = url,
                activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )



#TODO Not sure if needed for comets...see below.
    def get_on_click_function_comet( self, menuitem ):
        try:
            object_id = str( requests.get( menuitem.get_name() ).json()[ "object" ][ "id" ] )  #TODO Use the get_name()?
            webbrowser.open( IndicatorLunar.SEARCH_URL_COMET_ID + object_id )
        except Exception:
            pass # Ignore because the network/site is down; or perhaps a bad comet designation which has already been logged.


    def update_menu_planets_minor_planets_comets_stars( self, menu, menu_label, bodies, bodies_data, body_type ):

        #TODO Rename to Python standard?
        def getMenuItemNameFunction():
            if body_type == IndicatorLunar.astro_backend.BodyType.PLANET:
                menuitem_name_function = lambda name: IndicatorLunar.SEARCH_URL_PLANET + name.lower()

            elif body_type == IndicatorLunar.astro_backend.BodyType.MINOR_PLANET:
                menuitem_name_function = (
                    lambda name:
                        IndicatorLunar.SEARCH_URL_MINOR_PLANET +
                        IndicatorLunar.__get_minor_planet_designation_for_lowell_lookup( name ) )

            elif body_type == IndicatorLunar.astro_backend.BodyType.COMET:
                menuitem_name_function = (
                    lambda name:
                        IndicatorLunar.SEARCH_URL_COMET_DATABASE +
                        IndicatorLunar.__get_comet_designation_for_cobs_lookup( name, self.get_logging() ) )

            elif body_type == IndicatorLunar.astro_backend.BodyType.STAR:
                menuitem_name_function = (
                    lambda name:
                        IndicatorLunar.SEARCH_URL_STAR +
                        str( IndicatorLunar.astro_backend.get_star_hip( name ) ) )

            return menuitem_name_function

#TODO Sort out for comets
        # def __getOnClickFunctionComet( self, menuItem ):
        #     try:
        #         objectId = str( requests.get( menuItem.props.name ).json()[ "object" ][ "id" ] )  #TODO Use the get_name()?
        #         webbrowser.open( IndicatorLunar.SEARCH_URL_COMET_ID + objectId )
        #
        #     except Exception:
        #         pass # Ignore because the network/site is down; or perhaps a bad comet designation which has already been logged.


        def get_on_click_function():
            on_click_function = ( self.get_on_click_menuitem_open_browser_function(), )
#TODO Need to test this...            
            # if body_type == IndicatorLunar.astro_backend.BodyType.COMET:
            #     on_click_function = ( self.getOnClickFunctionComet(), )

            return on_click_function


#TODO Why are there commented out if/elif?
        def get_display_name_function():
            # if body_type == IndicatorLunar.astro_backend.BodyType.PLANET: display_name_function = getDisplayNamePlanet
            if body_type == IndicatorLunar.astro_backend.BodyType.PLANET:
                display_name_function = \
                    lambda name: IndicatorLunar.astro_backend.PLANET_NAMES_TRANSLATIONS[ name ]

            # elif body_type == IndicatorLunar.astro_backend.BodyType.MINOR_PLANET: display_name_function = getDisplayNameMinorPlanet
            elif body_type == IndicatorLunar.astro_backend.BodyType.MINOR_PLANET:
                display_name_function = lambda name: bodies_data[ name ].getName()

            # elif body_type == IndicatorLunar.astro_backend.BodyType.COMET: display_name_function = getDisplayNameComet
            elif body_type == IndicatorLunar.astro_backend.BodyType.COMET:
                display_name_function = lambda name: bodies_data[ name ].getName()

            # elif body_type == IndicatorLunar.astro_backend.BodyType.STAR: display_name_function = getDisplayNameStar
            elif body_type == IndicatorLunar.astro_backend.BodyType.STAR:
                display_name_function = \
                    lambda name: IndicatorLunar.astro_backend.get_star_name_translation( name )

            return display_name_function


        menuitem_name_function = getMenuItemNameFunction()#TODO Rename to Python standard?
        on_click_function = get_on_click_function()
        display_name_function = get_display_name_function()
        indent = self.get_menu_indent()
        indent_double = self.get_menu_indent( indent = 2 )
        submenu = Gtk.Menu()
        for name in bodies:
            current = len( submenu )
            menuitem_name = menuitem_name_function( name )
            if self.__update_menu_common( submenu, body_type, name, indent_double, menuitem_name, on_click_function ):
                display_name = display_name_function( name )
                self.create_and_insert_menuitem(
                    submenu,
                    indent + display_name,
                    current,
                    name = menuitem_name,
                    activate_functionandarguments = on_click_function )

                submenu.append( Gtk.SeparatorMenuItem() )

        if len( submenu.get_children() ) > 0:
            self.create_and_append_menuitem( menu, menu_label ).set_submenu( submenu )


    # Retrieve a comet's designation for lookup at the Comet Observation Database.
    #
    # https://minorplanetcenter.net//iau/lists/CometResolution.html
    # https://minorplanetcenter.net/iau/info/CometNamingGuidelines.html
    # http://www.icq.eps.harvard.edu/cometnames.html
    # https://en.wikipedia.org/wiki/Naming_of_comets
    # https://slate.com/technology/2013/11/comet-naming-a-quick-guide.html
    @staticmethod
    def __get_comet_designation_for_cobs_lookup( name, logging ):
        if name[ 0 ].isnumeric():
            # Examples:
                # 1P/Halley
                # 332P/Ikeya-Murakami
                # 332P-B/Ikeya-Murakami
                # 332P-C/Ikeya-Murakami
                # 1I/`Oumuamua
                # 282P
            slash = name.find( '/' )
            if slash == -1:
                designation = name

            else:
                designation = name.split( '/' )[ 0 ]

        elif name[ 0 ].isalpha():
            # Examples:
                # C/1995 O1 (Hale-Bopp)
                # P/1998 VS24 (LINEAR)
                # P/2011 UA134 (Spacewatch-PANSTARRS)
                # C/2019 Y4-D (ATLAS)
                # A/2018 V3
                # P/2020 M2
            if '(' in name:
                designation = name.split( '(' )[ 0 ]

            else:
                designation = name

        else:
            logging.error( "Unknown designation for comet: " + name )
            designation = ''

        return designation.strip()


    # Retrieve a minor planet's designation for lookup at the Lowell Minor Planet Services.
    #
    # https://www.iau.org/public/themes/naming/
    # https://minorplanetcenter.net/iau/info/DesDoc.html
    # https://minorplanetcenter.net/iau/info/PackedDes.html
    @staticmethod
    def __get_minor_planet_designation_for_lowell_lookup( name ):
        # Examples:
        #   55 Pandora
        #   84 Klio
        #   311 Claudia
        return name.split()[ 1 ].strip()


    # For the given body, creates the menu items relating to rise/set/azimuth/altitude.
    def __update_menu_common(
            self,
            menu,
            body_type,
            name_tag,
            indent,
            menuitem_name,
            on_click_function_and_arguments ):

        key = ( body_type, name_tag )
        appended = False
        if key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) in self.data: # This body rises/sets.
            if self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ] < self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ]: # Body will rise.
                if not self.hide_bodies_below_horizon:
                    self.__update_menuitems_rise_azimuth_altitude_set( menu, key, indent, menuitem_name, on_click_function_and_arguments, True, False )
                    appended = True

            else: # Body will set.
                if self.show_rise_when_set_before_sunset:
                    target_body_type = \
                        body_type == IndicatorLunar.astro_backend.BodyType.COMET or \
                        body_type == IndicatorLunar.astro_backend.BodyType.MINOR_PLANET or \
                        body_type == IndicatorLunar.astro_backend.BodyType.PLANET or \
                        body_type == IndicatorLunar.astro_backend.BodyType.STAR
                    key_sun = ( IndicatorLunar.astro_backend.BodyType.SUN, IndicatorLunar.astro_backend.NAME_TAG_SUN )
                    sun_rise = self.data[ key_sun + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ]
                    sun_set = self.data[ key_sun + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ]
                    if target_body_type and sun_set < sun_rise and self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ] < sun_set:
                        if not self.hide_bodies_below_horizon:
                            self.__update_menuitems_rise_azimuth_altitude_set( menu, key, indent, menuitem_name, on_click_function_and_arguments, True, False )
                            appended = True

                    else:
                        self.__update_menuitems_rise_azimuth_altitude_set( menu, key, indent, menuitem_name, on_click_function_and_arguments, False, True )
                        appended = True

                else:
                    self.__update_menuitems_rise_azimuth_altitude_set( menu, key, indent, menuitem_name, on_click_function_and_arguments, False, True )
                    appended = True

        elif key + ( IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH, ) in self.data: # Body is 'always up'.
            self.__update_menuitems_rise_azimuth_altitude_set( menu, key, indent, menuitem_name, on_click_function_and_arguments, False, False )
            appended = True

        return appended


    def __update_menuitems_rise_azimuth_altitude_set(
            self,
            menu,
            key,
            indent,
            menuitem_name,
            on_click_function_and_arguments,
            is_rise, is_set ):

        if is_rise:
            self.create_and_append_menuitem(
                menu,
                indent +
                _( "Rise: " ) +
                self.format_data( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ] ),
                name = menuitem_name,
                activate_functionandarguments = on_click_function_and_arguments )

        else:
            self.create_and_append_menuitem(
                menu,
                indent +
                _( "Azimuth: " ) +
                self.format_data( IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH, self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH, ) ] ),
                name = menuitem_name,
                activate_functionandarguments = on_click_function_and_arguments )

            self.create_and_append_menuitem(
                menu,
                indent +
                _( "Altitude: " ) +
                self.format_data( IndicatorLunar.astro_backend.DATA_TAG_ALTITUDE, self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_ALTITUDE, ) ] ),
                name = menuitem_name,
                activate_functionandarguments = on_click_function_and_arguments )

            if is_set:
                self.create_and_append_menuitem(
                    menu,
                    indent +
                    _( "Set: " ) +
                    self.format_data( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ] ),
                    name = menuitem_name,
                    activate_functionandarguments = on_click_function_and_arguments )


    # Display the rise/set information for each satellite.
    #
    # If a satellite is in transit OR will rise within the next five minutes,
    # show next rise/set.  Otherwise, show next rise.
    #
    # Next rise/set:
    #
    #                            R       S                           Satellite will rise within the five minute window; display next rise/set.
    #                            R               S                   Satellite will rise within the five minute window; display next rise/set.
    #                                            R       S           Satellite will rise after five minute window; display next rise; check if in previous transit.
    #                   ^                    ^
    #                utc_now             utc_now + 5
    #
    # When ( R < utc_now + 5 ) display next rise/set.
    # Otherwise, display next rise and check previous transit in case still underway.
    #
    # Previous rise/set:
    #
    #    R       S                                                   Satellite has set; display next rise/set.
    #    R                       S                                   Satellite in transit; display previous rise/set.
    #    R                                           S               Satellite in transit; display previous rise/set.
    #                            R       S                           Satellite will rise within the five minute window; display previous rise/set.
    #                            R                   S               Satellite will rise within the five minute window; display previous rise/set.
    #                                                R       S       Satellite will rise after five minute window; display next rise.
    #                   ^                    ^
    #                utc_now             utc_now + 5
    #
    # When ( R < utc_now + 5 ) AND ( S > utc_now ) display previous rise/set.
    def update_menu_satellites( self, menu, utc_now ):
        satellites = [ ]
        satellites_polar = [ ]
        utc_now_plus_five_minutes = utc_now + datetime.timedelta( minutes = 5 )

        for number in self.satellites:
            key = ( IndicatorLunar.astro_backend.BodyType.SATELLITE, number )
            if key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) in self.data: # Satellite rises/sets.
                if self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ] < utc_now_plus_five_minutes: # Satellite will rise within the next five minutes.
                    satellites.append( [
                        number,
                        self.satellite_general_perturbation_data[ number ].get_name(),
                        self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ],
                        self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_AZIMUTH, ) ],
                        self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ],
                        self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_AZIMUTH, ) ] ] )

                else: # Satellite will rise more than five minutes from now; look at previous transit.
                    if key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) in self.data_previous:
                        in_transit = \
                            self.data_previous[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ] < utc_now_plus_five_minutes and \
                            self.data_previous[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ] > utc_now

                        if in_transit:
                            satellites.append( [
                                number,
                                self.satellite_general_perturbation_data[ number ].get_name(),
                                self.data_previous[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ],
                                self.data_previous[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_AZIMUTH, ) ],
                                self.data_previous[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, ) ],
                                self.data_previous[ key + ( IndicatorLunar.astro_backend.DATA_TAG_SET_AZIMUTH, ) ] ] )

                        else: # Previous transit is complete (and too far back in the past to be applicable), so show next pass.
                            satellites.append( [
                                number,
                                self.satellite_general_perturbation_data[ number ].get_name(),
                                self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ] ] )

                    else: # No previous transit, show next pass.
                        satellites.append( [
                            number,
                            self.satellite_general_perturbation_data[ number ].get_name(),
                            self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, ) ] ] )

            elif key + ( IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH, ) in self.data: # Satellite is polar (always up).
                satellites_polar.append( [
                    number,
                    self.satellite_general_perturbation_data[ number ].get_name(),
                    self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH, ) ],
                    self.data[ key + ( IndicatorLunar.astro_backend.DATA_TAG_ALTITUDE, ) ] ] )

        if satellites:
            if self.satellites_sort_by_date_time:
                satellites = sorted(
                    satellites,
                    key = lambda x: (
                        x[ IndicatorLunar.SATELLITE_MENU_RISE_DATE_TIME ],
                        x[ IndicatorLunar.SATELLITE_MENU_NAME ],
                        x[ IndicatorLunar.SATELLITE_MENU_NUMBER ] ) )

            else: # Sort by name then number.
                satellites = sorted(
                    satellites,
                    key = lambda x: (
                        x[ IndicatorLunar.SATELLITE_MENU_NAME ],
                        x[ IndicatorLunar.SATELLITE_MENU_NUMBER ] ) )

            self.__update_menu_satellites( menu, _( "Satellites" ), satellites )

        if satellites_polar:
            satellites_polar = sorted(
                satellites_polar,
                key = lambda x: (
                    x[ IndicatorLunar.SATELLITE_MENU_NAME ],
                    x[ IndicatorLunar.SATELLITE_MENU_NUMBER ] ) ) # Sort by name then number.

            self.__update_menu_satellites( menu, _( "Satellites (Polar)" ), satellites_polar )


    def __update_menu_satellites( self, menu, label, satellites ):
        submenu = Gtk.Menu()
        self.create_and_append_menuitem( menu, label ).set_submenu( submenu )
        indent = self.get_menu_indent()
        indent_double = self.get_menu_indent( indent = 2 )
        indent_triple = self.get_menu_indent( indent = 3 )
        for info in satellites:
            number = info[ IndicatorLunar.SATELLITE_MENU_NUMBER ]
            name = info[ IndicatorLunar.SATELLITE_MENU_NAME ]
            url = IndicatorLunar.SEARCH_URL_SATELLITE + "lat=" + str( self.latitude ) + "&lng=" + str( self.longitude ) + "&satid=" + number
            label = indent + name + " : " + number + " : " + self.satellite_general_perturbation_data[ number ].get_international_designator()
            self.create_and_append_menuitem(
                submenu,
                label,
                name = url,
                activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            if len( info ) == 3: # Satellite yet to rise.
                data = self.format_data( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, info[ IndicatorLunar.SATELLITE_MENU_RISE_DATE_TIME ] )
                self.create_and_append_menuitem(
                    submenu,
                    indent_double + _( "Rise Date/Time: " ) + data,
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            elif len( info ) == 4: # Circumpolar (always up).
                data = self.format_data( IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH, info[ IndicatorLunar.SATELLITE_MENU_AZIMUTH ] )
                self.create_and_append_menuitem(
                    submenu,
                    indent_double + _( "Azimuth: " ) + data,
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

                data = self.format_data( IndicatorLunar.astro_backend.DATA_TAG_ALTITUDE, info[ IndicatorLunar.SATELLITE_MENU_ALTITUDE ] )
                self.create_and_append_menuitem(
                    submenu,
                    indent_double + _( "Altitude: " ) + data,
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            else: # Satellite is in transit.
                self.create_and_append_menuitem(
                    submenu,
                    indent_double + _( "Rise" ),
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

                data = self.format_data( IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME, info[ IndicatorLunar.SATELLITE_MENU_RISE_DATE_TIME ] )
                self.create_and_append_menuitem(
                    submenu,
                    indent_triple + _( "Date/Time: " ) + data,
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

                data = self.format_data( IndicatorLunar.astro_backend.DATA_TAG_RISE_AZIMUTH, info[ IndicatorLunar.SATELLITE_MENU_RISE_AZIMUTH ] )
                self.create_and_append_menuitem(
                    submenu,
                    indent_triple + _( "Azimuth: " ) + data,
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

                self.create_and_append_menuitem(
                    submenu,
                    indent_double + _( "Set" ),
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

                data = self.format_data( IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME, info[ IndicatorLunar.SATELLITE_MENU_SET_DATE_TIME ] )
                self.create_and_append_menuitem(
                    submenu,
                    indent_triple + _( "Date/Time: " ) + data,
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

                data = self.format_data( IndicatorLunar.astro_backend.DATA_TAG_SET_AZIMUTH, info[ IndicatorLunar.SATELLITE_MENU_SET_AZIMUTH ] )
                self.create_and_append_menuitem(
                    submenu,
                    indent_triple + _( "Azimuth: " ) + data,
                    name = url,
                    activate_functionandarguments = ( self.get_on_click_menuitem_open_browser_function(), ) )

            separator = Gtk.SeparatorMenuItem()
            submenu.append( separator )

        submenu.remove( separator )


    def format_data( self, data_tag, data, date_time_format = None ):
        display_data = None

        if data_tag == IndicatorLunar.astro_backend.DATA_TAG_ALTITUDE or \
           data_tag == IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH or \
           data_tag == IndicatorLunar.astro_backend.DATA_TAG_RISE_AZIMUTH or \
           data_tag == IndicatorLunar.astro_backend.DATA_TAG_SET_AZIMUTH:
            display_data = str( round( math.degrees( float( data ) ) ) ) + "°"

        elif data_tag == IndicatorLunar.astro_backend.DATA_TAG_BRIGHT_LIMB:
            display_data = str( int( float( data ) ) ) + "°"

        elif data_tag == IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_DATE_TIME or \
             data_tag == IndicatorLunar.astro_backend.DATA_TAG_EQUINOX or \
             data_tag == IndicatorLunar.astro_backend.DATA_TAG_FIRST_QUARTER or \
             data_tag == IndicatorLunar.astro_backend.DATA_TAG_FULL or \
             data_tag == IndicatorLunar.astro_backend.DATA_TAG_NEW or \
             data_tag == IndicatorLunar.astro_backend.DATA_TAG_RISE_DATE_TIME or \
             data_tag == IndicatorLunar.astro_backend.DATA_TAG_SET_DATE_TIME or \
             data_tag == IndicatorLunar.astro_backend.DATA_TAG_SOLSTICE or \
             data_tag == IndicatorLunar.astro_backend.DATA_TAG_THIRD_QUARTER:
                if date_time_format is None:
                    display_data = self.to_local_date_time_string( data, IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspacespaceHHcolonMM )

                else:
                    display_data = self.to_local_date_time_string( data, date_time_format )

        elif data_tag == IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_LATITUDE:
            latitude = data
            if latitude[ 0 ] == "-":
                display_data = latitude[ 1 : ] + "° " + _( "S" )

            else:
                display_data = latitude + "° " +_( "N" )

        elif data_tag == IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_LONGITUDE:
            longitude = data
            if longitude[ 0 ] == "-":
                display_data = longitude[ 1 : ] + "° " + _( "E" )

            else:
                display_data = longitude + "° " +_( "W" )

        elif data_tag == IndicatorLunar.astro_backend.DATA_TAG_ECLIPSE_TYPE:
            display_data = eclipse.get_eclipse_type_as_text( data )

        elif data_tag == IndicatorLunar.astro_backend.DATA_TAG_ILLUMINATION:
            display_data = data + "%"

        elif data_tag == IndicatorLunar.astro_backend.DATA_TAG_PHASE:
            display_data = IndicatorLunar.astro_backend.LUNAR_PHASE_NAMES_TRANSLATIONS[ data ]

        if display_data is None:
            display_data = "" # Better to show nothing than let None slip through and crash.
            self.get_logging().error( "Unknown data tag: " + data_tag )

        return display_data


    # Converts a UTC date/time to a local date/time string in the given format.
    def to_local_date_time_string( self, utc_date_time, output_format ):
        return utc_date_time.astimezone().strftime( output_format )


    # https://stackoverflow.com/a/64097432/2156453
    # https://medium.com/@eleroy/10-things-you-need-to-know-about-date-and-time-in-python-with-datetime-pytz-dateutil-timedelta-309bfbafb3f7
    def convert_start_hour_and_end_hour_to_date_time_in_utc( self, start_hour, end_hour ):
        start_hour_as_datetime_in_utc = \
            datetime.datetime.now().astimezone().replace( hour = start_hour ).astimezone( datetime.timezone.utc )

        end_hour_as_datetime_in_utc = \
            datetime.datetime.now().astimezone().replace( hour = end_hour ).astimezone( datetime.timezone.utc )

        return start_hour_as_datetime_in_utc, end_hour_as_datetime_in_utc


    # Creates the SVG icon text representing the moon given the illumination and bright limb angle.
    #
    # phase
    #   The current phase of the moon.
    # illumination percentage
    #   The brightness ranging from 0 to 100 inclusive.
    #   Ignored when phase is full/new or first/third quarter.
    # bright limb angle in degrees
    #   Bright limb angle, relative to zenith, ranging from 0 to 360 inclusive.
    #   Ignored when phase is full/new.
    def get_svg_icon_text( self, phase, illumination_percentage, bright_limb_angle_in_degrees ):
        width = 100
        height = width
        radius = float( width / 2 )
        colour = "777777"
        if phase == IndicatorLunar.astro_backend.LUNAR_PHASE_FULL_MOON or phase == IndicatorLunar.astro_backend.LUNAR_PHASE_NEW_MOON:
            body = '<circle cx="' + str( width / 2 ) + '" cy="' + str( height / 2 ) + '" r="' + str( radius )
            if phase == IndicatorLunar.astro_backend.LUNAR_PHASE_NEW_MOON:
                body += '" fill="#' + colour + '" fill-opacity="0.0" />'

            else: # Full
                body += '" fill="#' + colour + '" />'

        else: # First/Third Quarter or Waning/Waxing Crescent or Waning/Waxing Gibbous
            body = \
                '<path d="M ' + str( width / 2 - radius ) + ' ' + str( height / 2 ) + ' ' + \
                'A ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + \
                str( width / 2 + radius ) + ' ' + str( height / 2 )

            if phase == IndicatorLunar.astro_backend.LUNAR_PHASE_FIRST_QUARTER or phase == IndicatorLunar.astro_backend.LUNAR_PHASE_THIRD_QUARTER:
                body += ' Z"'

            elif phase == IndicatorLunar.astro_backend.LUNAR_PHASE_WANING_CRESCENT or phase == IndicatorLunar.astro_backend.LUNAR_PHASE_WAXING_CRESCENT:
                body += \
                    ' A ' + str( radius ) + ' ' + str( radius * ( 50 - illumination_percentage ) / 50 ) + ' 0 0 0 ' + \
                    str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            else: # Waning/Waxing Gibbous
                body += \
                    ' A ' + str( radius ) + ' ' + str( radius * ( illumination_percentage - 50 ) / 50 ) + ' 0 0 1 ' + \
                    str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            body += \
                ' transform="rotate(' + str( -bright_limb_angle_in_degrees ) + ' ' + \
                str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="#' + colour + '" />'

        return \
            '<?xml version="1.0" standalone="no"?>' \
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "https://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100" width="22" height="22">' + body + '</svg>'


    def on_preferences( self, dialog ):
        notebook = Gtk.Notebook()

        PAGE_ICON = 0
        PAGE_MENU = 1
        PAGE_NATURAL_BODIES = 2
        PAGE_SATELLITES = 3
        PAGE_NOTIFICATIONS = 4
        PAGE_LOCATION = 5

        # Icon text.
        grid = self.create_grid()

        indicator_text = \
            self.create_entry(
                "",
                tooltip_text = _(
                    "The text shown next to the indicator icon,\n" +
                    "or tooltip where applicable.\n\n" +
                    "The icon text may contain text and/or\n" +
                    "tags from the table below.\n\n" +
                    "To associate text with one or more tags,\n" +
                    "enclose the text and tag(s) within { }.\n\n" +
                    "For example\n\n" +
                    "\t{The sun will rise at [SUN RISE DATE TIME]}\n\n" +
                    "If any tag contains no data at render time,\n" +
                    "the tag will be removed.\n\n" +
                    "If a removed tag is within { }, the tag and\n" +
                    "text will be removed.\n\n" +
                    "Not supported on all desktops." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Icon Text" ) ), False ),
                    ( indicator_text, True ) ) ),
            0, 0, 1, 1 )

        indicator_text_separator = \
            self.create_entry(
                self.indicator_text_separator,
                tooltip_text = _( "The separator will be added between pairs of { }." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Separator" ) ), False ),
                    ( indicator_text_separator, False ) ) ),
            0, 1, 1, 1 )

        # Treeview to display attributes of selected/checked bodies.
        # If a body's magnitude passes through the magnitude filter,
        # all attributes (rise/set/az/alt) will be displayed in this table,
        # irrespective of the setting to hide bodies below the horizon.
        COLUMN_MODEL_TAG = 0
        COLUMN_MODEL_TRANSLATED_TAG = 1
        COLUMN_MODEL_VALUE = 2

        COLUMN_VIEW_TRANSLATED_TAG = 1
        COLUMN_VIEW_VALUE = 2

        display_tags_store = Gtk.ListStore( str, str, str ) # Tag, translated tag, value.
        self.initialise_display_tags_store( display_tags_store )

        indicator_text.set_text(
            self.translate_tags(
                display_tags_store,
                True,
                self.indicator_text ) ) # Translate tags into local language.

        treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                Gtk.TreeModelSort( model = display_tags_store ),
                ( _( "Tag" ), _( "Value" ) ),
                (
                    ( Gtk.CellRendererText(), "text", COLUMN_MODEL_TRANSLATED_TAG ),
                    ( Gtk.CellRendererText(), "text", COLUMN_MODEL_VALUE ) ),
                sortcolumnviewids_columnmodelids = (
                    ( COLUMN_VIEW_TRANSLATED_TAG, COLUMN_MODEL_TRANSLATED_TAG ),
                    ( COLUMN_VIEW_VALUE, COLUMN_MODEL_VALUE ) ),
                tooltip_text = _( "Double click to add a tag to the icon text." ),
                rowactivatedfunctionandarguments = ( self.on_tags_values_double_click, COLUMN_MODEL_TRANSLATED_TAG, indicator_text ) )

        grid.attach( scrolledwindow, 0, 2, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Icon" ) ) )

        # Menu.
        grid = self.create_grid()

        show_rise_when_set_before_sunset_checkbutton = \
            self.create_checkbutton(
                _( "Show rise when set is before sunset" ),
                tooltip_text = _(
                    "If a body sets before sunset,\n" +
                    "show the body's next rise instead\n" +
                    "(excludes satellites)." ),
                active = self.show_rise_when_set_before_sunset )

        grid.attach( show_rise_when_set_before_sunset_checkbutton, 0, 0, 1, 1 )

        hide_bodies_below_the_horizon_checkbutton = \
            self.create_checkbutton(
                _( "Hide bodies below the horizon" ),
                tooltip_text = _(
                    "Hide a body if it is yet to rise\n" +
                    "(excludes satellites)." ),
                active = self.hide_bodies_below_horizon )

        grid.attach( hide_bodies_below_the_horizon_checkbutton, 0, 1, 1, 1 )

        spinner_magnitude = \
            self.create_spinbutton(
                self.magnitude,
                int( IndicatorLunar.astro_backend.MAGNITUDE_MINIMUM ),
                int( IndicatorLunar.astro_backend.MAGNITUDE_MAXIMUM ),
                page_increment = 5,
                tooltip_text = _(
                    "A body with a fainter magnitude will be hidden\n" +
                    "(excludes satellites)." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Hide bodies fainter than magnitude" ) ), False ),
                    ( spinner_magnitude, False ) ),
                    margin_top = 5,
                    margin_left = 5 ),
            0, 2, 1, 1 )

        minor_planets_add_new_checkbutton = \
            self.create_checkbutton(
                _( "Add new minor planets" ),
                tooltip_text = _( "All minor planets are automatically added." ),
                margin_top = 5,
                active = self.minor_planets_add_new )

        grid.attach( minor_planets_add_new_checkbutton, 0, 3, 1, 1 )

        comets_add_new_checkbutton = \
            self.create_checkbutton(
                _( "Add new comets" ),
                tooltip_text = _( "All comets are automatically added." ),
                margin_top = 5,
                active = self.comets_add_new )

        grid.attach( comets_add_new_checkbutton, 0, 4, 1, 1 )

        satellites_add_new_checkbox = \
            self.create_checkbutton(
                _( "Add new satellites" ),
                tooltip_text = _( "All satellites are automatically added." ),
                margin_top = 5,
                active = self.satellites_add_new )

        grid.attach( satellites_add_new_checkbox, 0, 5, 1, 1 )

        sort_satellites_by_date_time_checkbutton = \
            self.create_checkbutton(
                _( "Sort satellites by rise date/time" ),
                tooltip_text = _(
                    "If checked, satellites are sorted\n" +
                    "by rise date/time.\n\n" +
                    "Otherwise, satellites are sorted\n" +
                    "by Name then Number." ),
                margin_top = 5,
                active = self.satellites_sort_by_date_time )

        grid.attach( sort_satellites_by_date_time_checkbutton, 0, 6, 1, 1 )

        spinner_satellite_limit_start = \
            self.create_spinbutton(
                self.satellite_limit_start,
                0,
                23,
                page_increment = 4,
                tooltip_text = _( "Show satellite passes after this hour (inclusive)" ) )

        spinner_satellite_limit_end = \
            self.create_spinbutton(
                self.satellite_limit_end,
                0,
                23,
                page_increment = 4,
                tooltip_text = _( "Show satellite passes before this hour (inclusive)" ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Show satellites passes from" ) ), False ),
                    ( spinner_satellite_limit_start, False ),
                    ( Gtk.Label.new( _( "to" ) ), False ),
                    ( spinner_satellite_limit_end, False ) ),
                margin_top = 5,
                margin_left = 5 ),
            0, 7, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )

        # Planets / minor planets / comets / stars.

        NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW = 0
        NATURAL_BODY_MODEL_COLUMN_NAME = 1
        NATURAL_BODY_MODEL_COLUMN_TRANSLATED_NAME = 2

        NATURAL_BODY_VIEW_COLUMN_HIDE_SHOW = 0
        NATURAL_BODY_VIEW_COLUMN_TRANSLATED_NAME = 1

        planet_store = Gtk.ListStore( bool, str, str ) # Show/hide, planet name (not displayed), translated planet name.
        for planet_name in IndicatorLunar.astro_backend.PLANETS:
            planet_store.append( [
                planet_name in self.planets,
                planet_name,
                IndicatorLunar.astro_backend.PLANET_NAMES_TRANSLATIONS[ planet_name ] ] )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect(
            "toggled",
            self.on_natural_body_checkbox,
            planet_store,
            NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW )

        treeview, scrolledwindow_planets = \
            self.create_treeview_within_scrolledwindow(
                planet_store,
                ( "", _( "Planets" ), ),
                (
                    ( renderer_toggle, "active", NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ),
                    ( Gtk.CellRendererText(), "text", NATURAL_BODY_MODEL_COLUMN_TRANSLATED_NAME ) ),
                alignments_columnviewids = ( ( 0.5, NATURAL_BODY_VIEW_COLUMN_HIDE_SHOW ), ),
                tooltip_text = _(
                    "Check a planet to display in the menu.\n\n" +
                    "Clicking the header of the first column\n" +
                    "will toggle all checkboxes." ),
                clickablecolumnviewids_functionsandarguments = (
                (
                    NATURAL_BODY_VIEW_COLUMN_HIDE_SHOW,
                    ( self.on_columnheader, planet_store, NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ), ), ) )

        minor_planet_store = Gtk.ListStore( bool, str, str ) # Show/hide, minor planet name, human readable name.
        #TODO Is the below comment/check valid...?  Why have the full check for the tooltip below?
        if self.minor_planet_apparent_magnitude_data: # No need to also check for orbital element data; either have both or neither.
            for minor_planet in sorted( self.minor_planet_orbital_element_data.keys() ):
                minor_planet_store.append( [
                    minor_planet in self.minor_planets,
                    minor_planet,
                    self.minor_planet_orbital_element_data[ minor_planet ].get_name() ] )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect(
            "toggled",
            self.on_natural_body_checkbox,
            minor_planet_store,
            NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW )

        treeview, scrolledwindow_minor_planets = \
            self.create_treeview_within_scrolledwindow(
                minor_planet_store,
                ( "", _( "Minor Planets" ), ),
                (
                    ( renderer_toggle, "active", NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ),
                    ( Gtk.CellRendererText(), "text", NATURAL_BODY_MODEL_COLUMN_TRANSLATED_NAME ) ),
                alignments_columnviewids = ( ( 0.5, NATURAL_BODY_VIEW_COLUMN_HIDE_SHOW ), ),
                tooltip_text = _(
                    "Check a minor planet to display in the menu.\n\n" +
                    "Clicking the header of the first column\n" +
                    "will toggle all checkboxes." )
                    if self.minor_planet_orbital_element_data and self.minor_planet_apparent_magnitude_data else _(
                    "Minor planet data is unavailable;\n" +
                    "the source could not be reached,\n" +
                    "or no data was available, or the data\n" +
                    "was completely filtered by magnitude." ),
                clickablecolumnviewids_functionsandarguments = (
                (
                    NATURAL_BODY_VIEW_COLUMN_HIDE_SHOW,
                    ( self.on_columnheader, minor_planet_store, NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ), ), ) )

        comet_store = Gtk.ListStore( bool, str, str ) # Show/hide, comet name, human readable name.
#TODO Check for data present as minor planets above?        
        for comet in sorted( self.comet_orbital_element_data.keys() ):
            comet_store.append( [
                comet in self.comets,
                comet,
                self.comet_orbital_element_data[ comet ].get_name() ] )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect(
            "toggled",
            self.on_natural_body_checkbox,
            comet_store,
            NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW )

        treeview, scrolledwindow_comets = \
            self.create_treeview_within_scrolledwindow(
                comet_store,
                ( "", _( "Comets" ), ),
                (
                    ( renderer_toggle, "active", NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ),
                    ( Gtk.CellRendererText(), "text", NATURAL_BODY_MODEL_COLUMN_TRANSLATED_NAME ) ),
                alignments_columnviewids = ( ( 0.5, NATURAL_BODY_VIEW_COLUMN_HIDE_SHOW ), ),
                tooltip_text = _(
                    "Check a comet to display in the menu.\n\n" +
                    "Clicking the header of the first column\n" +
                    "will toggle all checkboxes." )
                    if self.comet_orbital_element_data else _(
                    "Comet data is unavailable; the source\n" +
                    "could not be reached, or no data was\n" +
                    "available from the source, or the data\n" +
                    "was completely filtered by magnitude." ),
                clickablecolumnviewids_functionsandarguments = (
                (
                    NATURAL_BODY_VIEW_COLUMN_HIDE_SHOW,
                    ( self.on_columnheader, comet_store, NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ), ), ) )

        stars = [ ]
        for star_name in IndicatorLunar.astro_backend.get_star_names():
            stars.append( [
                star_name in self.stars,
                star_name,
                IndicatorLunar.astro_backend.get_star_name_translation( star_name ) ] )

        star_store = Gtk.ListStore( bool, str, str ) # Show/hide, star name, star translated name.
        for star in sorted( stars, key = lambda x: ( x[ 2 ] ) ): # Sort by translated star name.
            star_store.append( star )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect(
            "toggled",
            self.on_natural_body_checkbox,
            star_store,
            NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW )

        treeview, scrolledwindow_stars = \
            self.create_treeview_within_scrolledwindow(
                star_store,
                ( "", _( "Stars" ), ),
                (
                    ( renderer_toggle, "active", NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ),
                    ( Gtk.CellRendererText(), "text", NATURAL_BODY_MODEL_COLUMN_TRANSLATED_NAME ) ),
                alignments_columnviewids = ( ( 0.5, NATURAL_BODY_VIEW_COLUMN_HIDE_SHOW ), ),
                tooltip_text = _(
                    "Check a star to display in the menu.\n\n" +
                    "Clicking the header of the first column\n" +
                    "will toggle all checkboxes." ),
                clickablecolumnviewids_functionsandarguments = (
                (
                    NATURAL_BODY_VIEW_COLUMN_HIDE_SHOW,
                    ( self.on_columnheader, star_store, NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ), ), ) )

        notebook.append_page(
            self.create_box(
                (
                    ( scrolledwindow_planets, True ),
                    ( scrolledwindow_minor_planets, True ),
                    ( scrolledwindow_comets, True ),
                    ( scrolledwindow_stars, True ) ),
                spacing = 20 ),
            Gtk.Label.new( _( "Natural Bodies" ) ) )

        # Satellites.

        SATELLITE_MODEL_COLUMN_HIDE_SHOW = 0
        SATELLITE_MODEL_COLUMN_NAME = 1
        SATELLITE_MODEL_COLUMN_NUMBER = 2
        SATELLITE_MODEL_COLUMN_INTERNATIONAL_DESIGNATOR = 3

        SATELLITE_VIEW_COLUMN_HIDE_SHOW = 0
        SATELLITE_VIEW_COLUMN_NAME = 1
        SATELLITE_VIEW_COLUMN_NUMBER = 2
        SATELLITE_VIEW_COLUMN_INTERNATIONAL_DESIGNATOR = 3

        satellite_store = Gtk.ListStore( bool, str, str, str ) # Show/hide, name, number, international designator.
        for satellite in self.satellite_general_perturbation_data:
            satellite_store.append( [
                satellite in self.satellites,
                self.satellite_general_perturbation_data[ satellite ].get_name(),
                satellite,
                self.satellite_general_perturbation_data[ satellite ].get_international_designator() ] )

        satellite_store_sort = Gtk.TreeModelSort( model = satellite_store )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect(
            "toggled",
            self.on_satellite_checkbox,
            satellite_store,
            satellite_store_sort,
            SATELLITE_MODEL_COLUMN_HIDE_SHOW )

        treeview, scrolledwindow = \
            self.create_treeview_within_scrolledwindow(
                satellite_store_sort,
                ( "", _( "Name" ), _( "Number" ), _( "International Designator" ) ),
                (
                    ( renderer_toggle, "active", SATELLITE_MODEL_COLUMN_HIDE_SHOW ),
                    ( Gtk.CellRendererText(), "text", SATELLITE_MODEL_COLUMN_NAME ),
                    ( Gtk.CellRendererText(), "text", SATELLITE_MODEL_COLUMN_NUMBER ),
                    ( Gtk.CellRendererText(), "text", SATELLITE_MODEL_COLUMN_INTERNATIONAL_DESIGNATOR ) ),
                alignments_columnviewids = ( ( 0.5, SATELLITE_VIEW_COLUMN_HIDE_SHOW ), ),
                sortcolumnviewids_columnmodelids = (
                    ( SATELLITE_VIEW_COLUMN_NAME, SATELLITE_MODEL_COLUMN_NAME ),
                    ( SATELLITE_VIEW_COLUMN_NUMBER, SATELLITE_MODEL_COLUMN_NUMBER ),
                    ( SATELLITE_VIEW_COLUMN_INTERNATIONAL_DESIGNATOR, SATELLITE_MODEL_COLUMN_INTERNATIONAL_DESIGNATOR ) ),
                tooltip_text = _(
                    "Check a satellite to display in the menu.\n\n" +
                    "Clicking the header of the first column\n" +
                    "will toggle all checkboxes." )
                    if self.satellite_general_perturbation_data else _(
                    "Satellite data is unavailable;\n" +
                    "the source could not be reached,\n" +
                    "or data was available." ),
                clickablecolumnviewids_functionsandarguments = (
                (
                    SATELLITE_VIEW_COLUMN_HIDE_SHOW,
                    ( self.on_columnheader, satellite_store, SATELLITE_MODEL_COLUMN_HIDE_SHOW ), ), ) )

        notebook.append_page(
            self.create_box( ( ( scrolledwindow, True ), ) ),
            Gtk.Label.new( _( "Satellites" ) ) )

        # Notifications (satellite and full moon).
        notify_osd_information = _( "For formatting, refer to https://wiki.ubuntu.com/NotifyOSD" )

        grid = self.create_grid()

        satellite_tag_translations = self.list_of_lists_to_liststore( IndicatorLunar.astro_backend.SATELLITE_TAG_TRANSLATIONS )
        message_text = self.translate_tags( satellite_tag_translations, True, self.satellite_notification_message )
        summary_text = self.translate_tags( satellite_tag_translations, True, self.satellite_notification_summary )
        tooltip_common = \
            IndicatorLunar.astro_backend.SATELLITE_TAG_NAME_TRANSLATION + "\n\t" + \
            IndicatorLunar.astro_backend.SATELLITE_TAG_NUMBER_TRANSLATION + "\n\t" + \
            IndicatorLunar.astro_backend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n\t" + \
            IndicatorLunar.astro_backend.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.astro_backend.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n\t" + \
            IndicatorLunar.astro_backend.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION + "\n\t" + \
            IndicatorLunar.astro_backend.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n\t" + \
            _( notify_osd_information )

        summary_tooltip = _(
            "The summary for the satellite rise notification.\n\n" +  "Available tags:\n\t" ) + \
            tooltip_common

        message_tooltip = _(
            "The message for the satellite rise notification.\n\n" + "Available tags:\n\t" ) + \
            tooltip_common

        # Additional lines are added to the message to ensure the textview for the message text is not too small.
        show_satellite_notification_checkbox, satellite_notification_summary_text, satellite_notification_messaget_ext = \
            self.create_notification_panel(
                grid,
                0,
                _( "Satellite rise" ),
                _( "Screen notification when a satellite rises above the horizon." ),
                self.show_satellite_notification,
                _( "Summary" ),
                summary_text,
                summary_tooltip,
                _( "Message" ) + "\n \n \n \n ",
                message_text,
                message_tooltip,
                _( "Test" ),
                _( "Show the notification using the current summary/message." ),
                False )

        # Additional lines are added to the message to ensure the textview for the message text is not too small.
        show_werewolf_warning_checkbox, werewolf_notification_summary_text, werewolf_notification_message_text = \
            self.create_notification_panel(
                grid,
                4,
                _( "Werewolf warning" ),
                _( "Hourly screen notification leading up to full moon." ),
                self.show_werewolf_warning,
                _( "Summary" ),
                self.werewolf_warning_summary,
                _( "Hourly screen notification leading up to full moon." ),
                _( "Message" ) + "\n \n ",
                self.werewolf_warning_message,
                _( "The message for the werewolf notification.\n\n" ) + notify_osd_information,
                _( "Test" ), _( "Show the notification using the current summary/message." ),
                True )

        show_werewolf_warning_checkbox.set_margin_top( 10 )

        notebook.append_page( grid, Gtk.Label.new( _( "Notifications" ) ) )

        # Location.
        grid = self.create_grid()

        cities = IndicatorLunar.astro_backend.get_cities()
        if self.city not in cities:
            cities.append( self.city )
            cities = sorted( cities, key = locale.strxfrm )

        city = \
            self.create_comboboxtext(
                cities,
                tooltip_text = _(
                    "Choose a city from the list.\n" +
                    "Or, add in your own city name." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "City" ) ), False ),
                    ( city, False ) ),
                    margin_top = 5 ),
            0, 0, 1, 1 )
        
        latitude = \
            self.create_entry(
                str( self.latitude ),
                tooltip_text = _( "Latitude of your location in decimal degrees." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Latitude" ) ), False ),
                    ( latitude, False ) ),
                    margin_top = 5 ),
            0, 1, 1, 1 )

        longitude = \
            self.create_entry(
                str( self.longitude ),
                tooltip_text = _( "Longitude of your location in decimal degrees." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Longitude" ) ), False ),
                    ( longitude, False ) ),
                    margin_top = 5 ),
            0, 2, 1, 1 )

        elevation = \
            self.create_entry(
                str( self.elevation ),
                tooltip_text = _( "Height in metres above sea level." ) )

        grid.attach(
            self.create_box(
                (
                    ( Gtk.Label.new( _( "Elevation" ) ), False ),
                    ( elevation, False ) ),
                    margin_top = 5 ),
            0, 3, 1, 1 )

        city.connect( "changed", self.on_city_changed, latitude, longitude, elevation )
        city.set_active( cities.index( self.city ) )

        # Must set the values here AFTER city is selected,
        # as the user may set a different latitude/longitude/elevation
        # to that defaulted with the city.
        latitude.set_text( str( self.latitude ) )
        longitude.set_text( str( self.longitude ) )
        elevation.set_text( str( self.elevation ) )

        autostart_checkbox, delay_spinner, box = self.create_autostart_checkbox_and_delay_spinner()
        box.set_margin_top( 30 ) # Put some distance from the prior section.
        grid.attach( box, 0, 4, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Location" ) ) )

        dialog.get_content_area().pack_start( notebook, True, True, 0 )
        dialog.show_all()

        while True:
            response_type = dialog.run()
            if response_type != Gtk.ResponseType.OK:
                break

            city_value = city.get_active_text()
            if city_value == "":
                notebook.set_current_page( PAGE_LOCATION )
                self.show_dialog_ok( dialog, _( "City cannot be empty." ) )
                city.grab_focus()
                continue

            latitude_value = latitude.get_text().strip()
            if latitude_value == "" or not self.is_number( latitude_value ) or float( latitude_value ) > 90 or float( latitude_value ) < -90:
                notebook.set_current_page( PAGE_LOCATION )
                self.show_dialog_ok( dialog, _( "Latitude must be a number between 90 and -90 inclusive." ) )
                latitude.grab_focus()
                continue

            longitude_value = longitude.get_text().strip()
            if longitude_value == "" or not self.is_number( longitude_value ) or float( longitude_value ) > 180 or float( longitude_value ) < -180:
                notebook.set_current_page( PAGE_LOCATION )
                self.show_dialog_ok( dialog, _( "Longitude must be a number between 180 and -180 inclusive." ) )
                longitude.grab_focus()
                continue

            elevation_value = elevation.get_text().strip()
            if elevation_value == "" or not self.is_number( elevation_value ) or float( elevation_value ) > 10000 or float( elevation_value ) < 0:
                notebook.set_current_page( PAGE_LOCATION )
                self.show_dialog_ok( dialog, _( "Elevation must be a number between 0 and 10000 inclusive." ) )
                elevation.grab_focus()
                continue

            if spinner_satellite_limit_start.get_value_as_int() >= spinner_satellite_limit_end.get_value_as_int():
                notebook.set_current_page( PAGE_MENU )
                self.show_dialog_ok( dialog, _( "The start hour for satellite passes must be lower than the end hour." ) )
                spinner_satellite_limit_start.grab_focus()
                continue

            self.indicator_text = self.translate_tags( display_tags_store, False, indicator_text.get_text() )
            self.indicator_text_separator = indicator_text_separator.get_text()
            self.show_rise_when_set_before_sunset = show_rise_when_set_before_sunset_checkbutton.get_active()
            self.hide_bodies_below_horizon = hide_bodies_below_the_horizon_checkbutton.get_active()
            self.magnitude = spinner_magnitude.get_value_as_int()
            self.comets_add_new = comets_add_new_checkbutton.get_active() # The update will add in new comets.
            self.minor_planets_add_new = minor_planets_add_new_checkbutton.get_active() # The update will add in new minor planets.
            self.satellites_sort_by_date_time = sort_satellites_by_date_time_checkbutton.get_active()
            self.satellites_add_new = satellites_add_new_checkbox.get_active() # The update will add in new satellites.

            # If the user changes the visibility window for satellites,
            # the previous set of transits may no longer match the new window.
            # One solution is to attempt to filter out those transits which do not match.
            # A simpler solution is to erase the previous transits.
            if self.satellite_limit_start != spinner_satellite_limit_start.get_value_as_int() or \
               self.satellite_limit_end != spinner_satellite_limit_end.get_value_as_int():
                self.data_previous = None

            self.satellite_limit_start = spinner_satellite_limit_start.get_value_as_int()
            self.satellite_limit_end = spinner_satellite_limit_end.get_value_as_int()

            self.planets = [ ]
            for row in planet_store:
                if row[ NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ]:
                    self.planets.append( row[ NATURAL_BODY_MODEL_COLUMN_NAME ] )

            self.stars = [ ]
            for row in star_store:
                if row[ NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ]:
                    self.stars.append( row[ NATURAL_BODY_MODEL_COLUMN_NAME ] )

            # If the option to add new comets is checked, this will be handled out in the main update loop.
            # Otherwise, update the list of checked comets (ditto for minor planets and satellites).
            self.comets = [ ]
            if not self.comets_add_new:
                for comet in comet_store:
                    if comet[ NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ]:
                        self.comets.append( comet[ NATURAL_BODY_MODEL_COLUMN_NAME ] )

            self.minor_planets = [ ]
            if not self.minor_planets_add_new:
                for minor_planet in minor_planet_store:
                    if minor_planet[ NATURAL_BODY_MODEL_COLUMN_HIDE_SHOW ]:
                        self.minor_planets.append( minor_planet[ NATURAL_BODY_MODEL_COLUMN_NAME ] )

            self.satellites = [ ]
            if not self.satellites_add_new:
                for satellite in satellite_store:
                    if satellite[ SATELLITE_MODEL_COLUMN_HIDE_SHOW ]:
                        self.satellites.append( satellite[ SATELLITE_MODEL_COLUMN_NUMBER ] )

            self.show_satellite_notification = show_satellite_notification_checkbox.get_active()
            if not show_satellite_notification_checkbox.get_active(): self.satellite_previous_notifications = { }
            self.satellite_notification_summary = self.translate_tags( satellite_tag_translations, False, satellite_notification_summary_text.get_text() )
            self.satellite_notification_message = self.translate_tags( satellite_tag_translations, False, self.get_textview_text( satellite_notification_messaget_ext ) )

            self.show_werewolf_warning = show_werewolf_warning_checkbox.get_active()
            self.werewolf_warning_summary = werewolf_notification_summary_text.get_text()
            self.werewolf_warning_message = self.get_textview_text( werewolf_notification_message_text )

            self.city = city_value
            self.latitude = float( latitude_value )
            self.longitude = float( longitude_value )
            self.elevation = float( elevation_value )

            self.set_autostart_and_delay( autostart_checkbox.get_active(), delay_spinner.get_value_as_int() )
            break

        return response_type


    def initialise_display_tags_store( self, display_tags_store ):
        items = [ [ IndicatorLunar.astro_backend.BodyType.MOON, IndicatorLunar.astro_backend.NAME_TAG_MOON, IndicatorLunar.astro_backend.DATA_TAGS_MOON ],
                  [ IndicatorLunar.astro_backend.BodyType.SUN, IndicatorLunar.astro_backend.NAME_TAG_SUN, IndicatorLunar.astro_backend.DATA_TAGS_SUN ] ]

        for item in items:
            body_type = item[ IndicatorLunar.DATA_INDEX_BODY_TYPE ]
            body_tag = item[ IndicatorLunar.DATA_INDEX_BODY_NAME ]
            data_tags = item[ IndicatorLunar.DATA_INDEX_DATA_NAME ]
            if ( body_type, body_tag, IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                for data_tag in data_tags:
                    translated_tag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ body_tag ] + " " + IndicatorLunar.astro_backend.DATA_TAGS_TRANSLATIONS[ data_tag ]
                    value = ""
                    key = ( body_type, body_tag, data_tag )
                    if key in self.data:
                        value = self.format_data( data_tag, self.data[ key ] )
                        display_tags_store.append( [ body_tag + " " + data_tag, translated_tag, value ] )

        items = [ [ IndicatorLunar.astro_backend.BodyType.PLANET, IndicatorLunar.astro_backend.PLANETS, IndicatorLunar.astro_backend.DATA_TAGS_PLANET ],
                  [ IndicatorLunar.astro_backend.BodyType.STAR, IndicatorLunar.astro_backend.get_star_names(), IndicatorLunar.astro_backend.DATA_TAGS_STAR ] ]

        for item in items:
            body_type = item[ IndicatorLunar.DATA_INDEX_BODY_TYPE ]
            body_tags = item[ IndicatorLunar.DATA_INDEX_BODY_NAME ]
            data_tags = item[ IndicatorLunar.DATA_INDEX_DATA_NAME ]
            for body_tag in body_tags:
                if ( body_type, body_tag, IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                    for data_tag in data_tags:
                        translated_tag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ body_tag ] + " " + IndicatorLunar.astro_backend.DATA_TAGS_TRANSLATIONS[ data_tag ]
                        value = ""
                        key = ( body_type, body_tag, data_tag )
                        if key in self.data:
                            value = self.format_data( data_tag, self.data[ key ] )
                            display_tags_store.append( [ body_tag + " " + data_tag, translated_tag, value ] )

        items = [ [ IndicatorLunar.astro_backend.BodyType.COMET, self.comet_orbital_element_data, IndicatorLunar.astro_backend.DATA_TAGS_COMET ],
                  [ IndicatorLunar.astro_backend.BodyType.MINOR_PLANET, self.minor_planet_orbital_element_data, IndicatorLunar.astro_backend.DATA_TAGS_MINOR_PLANET ] ]

        for item in items:
            body_type = item[ IndicatorLunar.DATA_INDEX_BODY_TYPE ]
            body_tags = item[ IndicatorLunar.DATA_INDEX_BODY_NAME ]
            data_tags = item[ IndicatorLunar.DATA_INDEX_DATA_NAME ]
            for body_tag in body_tags:
                if ( body_type, body_tag, IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                    for data_tag in data_tags:
                        translated_tag = body_tag + " " + IndicatorLunar.astro_backend.DATA_TAGS_TRANSLATIONS[ data_tag ]
                        value = ""
                        key = ( body_type, body_tag, data_tag )
                        if key in self.data:
                            value = self.format_data( data_tag, self.data[ key ] )
                            display_tags_store.append( [ body_tag + " " + data_tag, translated_tag, value ] )

        body_type = IndicatorLunar.astro_backend.BodyType.SATELLITE
        for body_tag in self.satellite_general_perturbation_data:
            # Add this body's attributes ONLY if data is present.
            rise_is_present = \
                ( body_type, body_tag, IndicatorLunar.astro_backend.DATA_TAG_RISE_AZIMUTH ) in self.data or \
                ( body_type, body_tag, IndicatorLunar.astro_backend.DATA_TAG_AZIMUTH ) in self.data

            if rise_is_present:
                for data_tag in IndicatorLunar.astro_backend.DATA_TAGS_SATELLITE:
                    value = ""
                    name = self.satellite_general_perturbation_data[ body_tag ].get_name()
                    international_designator = self.satellite_general_perturbation_data[ body_tag ].get_international_designator()
                    translated_tag = name + " : " + body_tag + " : " + international_designator + " " + IndicatorLunar.astro_backend.DATA_TAGS_TRANSLATIONS[ data_tag ]
                    key = ( IndicatorLunar.astro_backend.BodyType.SATELLITE, body_tag, data_tag )
                    if key in self.data:
                        value = self.format_data( data_tag, self.data[ key ] )
                        display_tags_store.append( [ body_tag + " " + data_tag, translated_tag, value ] )


    def translate_tags( self, tags_list_store, original_to_local, text ):
        # The tags list store contains at least 2 columns; additional columns may exist,
        # depending on the tags list store provided by the caller, but are ignored.
        # First column contains the original/untranslated tags.
        # Second column contains the translated tags.
        if original_to_local:
            i = 0
            j = 1

        else:
            i = 1
            j = 0

        translated_text = text
        tags = re.findall( "\[([^\[^\]]+)\]", translated_text )
        for tag in tags:
            iterator = tags_list_store.get_iter_first()
            while iterator:
                row = tags_list_store[ iterator ]
                if row[ i ] == tag:
                    translated_text = translated_text.replace( "[" + tag + "]", "[" + row[ j ] + "]" )
                    iterator = None # Break and move on to next tag.

                else:
                    iterator = tags_list_store.iter_next( iterator )

        return translated_text


    def on_tags_values_double_click(
            self,
            tree,
            row_number,
            treeviewcolumn,
            translated_tag_column_index,
            indicator_textentry ):

        model, treeiter = tree.get_selection().get_selected()
#TODO Should we do something where the selection is converted from view to model?
#Probably not as we get the treeiter and model above.
# But check  translatedtagcolumnindex and ensure it is correct for indexing into the model.
        indicator_textentry.insert_text(
            "[" + model[ treeiter ][ translated_tag_column_index ] + "]", indicator_textentry.get_position() )


#TODO Hopefully delete
    # def createTreeView( self, listStore, toolTipText, columnHeaderText, columnIndex ):
    #     COLUMN_INDEX_TOGGLE = 0
    #     COLUMN_INDEX_DATA = 1
    #
    #     def on_natural_body_checkbox( cellRendererToggle, row, listStore ):
    #         listStore[ row ][ COLUMN_INDEX_TOGGLE ] = not listStore[ row ][ COLUMN_INDEX_TOGGLE ]
    #
    #
    #     tree = Gtk.TreeView.new_with_model( listStore )
    #     tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
    #     tree.set_tooltip_text( toolTipText )
    #     tree.set_hexpand( True )
    #     tree.set_vexpand( True )
    #
    #     renderer_toggle = Gtk.CellRendererToggle()
    #     renderer_toggle.connect( "toggled", on_natural_body_checkbox, listStore )
    #     treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = COLUMN_INDEX_TOGGLE )
    #     treeViewColumn.set_clickable( True )
    #     treeViewColumn.connect( "clicked", self.on_columnheader, listStore )
    #     tree.append_column( treeViewColumn )
    #
    #     tree.append_column( Gtk.TreeViewColumn( columnHeaderText, Gtk.CellRendererText(), text = columnIndex ) )
    #     tree.get_column( COLUMN_INDEX_DATA ).set_expand( True )
    #
    #     scrolledWindow = Gtk.ScrolledWindow()
    #     scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
    #     scrolledWindow.add( tree )
    #
    #     return scrolledWindow


    def on_natural_body_checkbox( self, cell_renderer_toggle, row, liststore, natural_body_model_column_hide_show ):
        liststore[ row ][ natural_body_model_column_hide_show ] = \
            not liststore[ row ][ natural_body_model_column_hide_show ]


    def on_satellite_checkbox(
            self,
            cell_renderer_toggle,
            row,
            datastore,
            sortstore,
            satellite_model_column_hide_show ):
        actual_row = sortstore.convert_path_to_child_path( Gtk.TreePath.new_from_string( row ) ) # Convert sorted model index to underlying (child) model index.
        datastore[ actual_row ][ satellite_model_column_hide_show ] = \
            not datastore[ actual_row ][ satellite_model_column_hide_show ]


    def on_columnheader( self, treeviewcolumn, datastore, datastore_column_hide_show ):
        at_least_one_item_checked = False
        at_least_one_item_unchecked = False
        for row in range( len( datastore ) ):
            if datastore[ row ][ datastore_column_hide_show ]:
                at_least_one_item_checked = True

            if not datastore[ row ][ datastore_column_hide_show ]:
                at_least_one_item_unchecked = True

        if at_least_one_item_checked and at_least_one_item_unchecked: # Mix of values checked and unchecked, so check all.
            value = True

        elif at_least_one_item_checked: # No items checked (so all are unchecked), so check all.
            value = False

        else: # No items unchecked (so all are checked), so uncheck all.
            value = True

        for row in range( len( datastore ) ):
            datastore[ row ][ 0 ] = value


    def create_notification_panel(
            self,
            grid, grid_start_index,
            checkbox_label, checkbox_tooltip, checkbox_is_active,
            summary_label, summary_text, summary_tooltip,
            message_label, message_text, message_tooltip,
            test_button_text, test_button_tooltip,
            is_moon_notification ):

        checkbutton = \
            self.create_checkbutton(
                checkbox_label,
                tooltip_text = checkbox_tooltip,
                active = checkbox_is_active )

        grid.attach( checkbutton, 0, grid_start_index, 1, 1 )

        summary_text_entry = \
            self.create_entry(
                summary_text,
                tooltip_text = summary_tooltip )

        box = \
            self.create_box(
                (
                    ( Gtk.Label.new( summary_label ), False ),
                    ( summary_text_entry, True ) ),
                    sensitive = checkbutton.get_active(),
                    margin_left = IndicatorBase.INDENT_WIDGET_LEFT )

        grid.attach( box, 0, grid_start_index + 1, 1, 1 )

        checkbutton.connect( "toggled", self.on_radio_or_checkbox, True, box )

        message_text_view = \
            self.create_textview(
                text = message_text,
                tooltip_text = message_tooltip,
                editable = False )

        box = \
            self.create_box(
                (
                    ( Gtk.Label.new( message_label ), False ),
                    ( self.create_scrolledwindow( message_text_view ), True ) ),
                sensitive = checkbutton.get_active(),
                margin_left = IndicatorBase.INDENT_WIDGET_LEFT )
        
        grid.attach( box, 0, grid_start_index + 2, 1, 1 )

        checkbutton.connect( "toggled", self.on_radio_or_checkbox, True, box )

        test = \
            self.create_button(
                test_button_text,
                tooltip_text = test_button_tooltip,
                sensitive = checkbutton.get_active(),
                clicked_functionandarguments = (
                    self.on_test_notification_clicked,
                    summary_text_entry, message_text_view, is_moon_notification ) )

        test.set_halign( Gtk.Align.END )       
        grid.attach( test, 0, grid_start_index + 3, 1, 1 )

        checkbutton.connect( "toggled", self.on_radio_or_checkbox, True, test )

        return checkbutton, summary_text_entry, message_text_view


    def on_test_notification_clicked(
            self,
            button,
            summary_entry,
            message_text_view,
            is_moon_notification ):

        summary = summary_entry.get_text()
        message = self.get_textview_text( message_text_view )

        if is_moon_notification:
            self.show_notification( summary, message, icon = self.create_full_moon_icon() )

        else:
            def replace_tags( text ):
                return \
                    text. \
                    replace( IndicatorLunar.astro_backend.SATELLITE_TAG_NAME_TRANSLATION, "ISS (ZARYA)" ). \
                    replace( IndicatorLunar.astro_backend.SATELLITE_TAG_NUMBER_TRANSLATION, "25544" ). \
                    replace( IndicatorLunar.astro_backend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION, "1998-067A" ). \
                    replace( IndicatorLunar.astro_backend.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION, "123°" ). \
                    replace( IndicatorLunar.astro_backend.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.to_local_date_time_string( datetime.datetime.now( datetime.timezone.utc ).replace( tzinfo = None ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) ). \
                    replace( IndicatorLunar.astro_backend.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                    replace( IndicatorLunar.astro_backend.SATELLITE_TAG_SET_TIME_TRANSLATION, self.to_local_date_time_string( datetime.datetime.now( datetime.timezone.utc ).replace( tzinfo = None ) + datetime.timedelta( minutes = 10 ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) )

            summary = replace_tags( summary ) + " " # The notification summary text must not be empty (at least on Unity).
            message = replace_tags( message )
            self.show_notification( summary, message, icon = self.icon_satellite )


    def on_city_changed( self, combobox, latitude, longitude, elevation ):
        city = combobox.get_active_text()
        if city in IndicatorLunar.astro_backend.get_cities():
            the_latitude, the_longitude, the_elevation = \
                IndicatorLunar.astro_backend.get_latitude_longitude_elevation( city )

            latitude.set_text( str( the_latitude ) )
            longitude.set_text( str( the_longitude ) )
            elevation.set_text( str( the_elevation ) )


    def get_default_city( self ):
        try:
            timezone = self.process_get( "cat /etc/timezone" )
            the_city = None
            cities = IndicatorLunar.astro_backend.get_cities()
            for city in cities:
                if city in timezone:
                    the_city = city
                    break

            if the_city is None or not the_city:
                the_city = cities[ 0 ] # No city found, so choose first city by default.

        except Exception as e:
            self.get_logging().exception( e )
            self.get_logging().error( "Error getting default city." )
            the_city = cities[ 0 ] # Some error occurred, so choose first city by default.

        return the_city


    def load_config( self, config ):
        self.city = config.get( IndicatorLunar.CONFIG_CITY_NAME ) # Returns None if the key is not found.
        if self.city is None:
            self.city = self.get_default_city()
            self.latitude, self.longitude, self.elevation = \
                IndicatorLunar.astro_backend.get_latitude_longitude_elevation( self.city )

        else:
            self.elevation = config.get( IndicatorLunar.CONFIG_CITY_ELEVATION )
            self.latitude = config.get( IndicatorLunar.CONFIG_CITY_LATITUDE )
            self.longitude = config.get( IndicatorLunar.CONFIG_CITY_LONGITUDE )

        self.comets = config.get( IndicatorLunar.CONFIG_COMETS, [ ] )
        self.comets_add_new = config.get( IndicatorLunar.CONFIG_COMETS_ADD_NEW, False )

        self.hide_bodies_below_horizon = config.get( IndicatorLunar.CONFIG_HIDE_BODIES_BELOW_HORIZON, False )

        self.indicator_text = config.get( IndicatorLunar.CONFIG_INDICATOR_TEXT, IndicatorLunar.INDICATOR_TEXT_DEFAULT )
        self.indicator_text_separator = config.get( IndicatorLunar.CONFIG_INDICATOR_TEXT_SEPARATOR, IndicatorLunar.INDICATOR_TEXT_SEPARATOR_DEFAULT )

        self.minor_planets = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS, [ ] )
        self.minor_planets_add_new = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS_ADD_NEW, False )

        self.magnitude = config.get( IndicatorLunar.CONFIG_MAGNITUDE, 3 ) # Although a value of 6 is visible with the naked eye, that gives too many minor planets initially.

        self.planets = config.get( IndicatorLunar.CONFIG_PLANETS, IndicatorLunar.astro_backend.PLANETS )

        self.satellite_limit_start = config.get( IndicatorLunar.CONFIG_SATELLITE_LIMIT_START, 16 ) # 4pm
        self.satellite_limit_end = config.get( IndicatorLunar.CONFIG_SATELLITE_LIMIT_END, 22 ) # 10pm
        self.satellite_notification_message = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE, IndicatorLunar.SATELLITE_NOTIFICATION_MESSAGE_DEFAULT )
        self.satellite_notification_summary = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY, IndicatorLunar.SATELLITE_NOTIFICATION_SUMMARY_DEFAULT )
        self.satellites = config.get( IndicatorLunar.CONFIG_SATELLITES, [ ] )
        self.satellites_add_new = config.get( IndicatorLunar.CONFIG_SATELLITES_ADD_NEW, False )
        self.satellites_sort_by_date_time = config.get( IndicatorLunar.CONFIG_SATELLITES_SORT_BY_DATE_TIME, True )

        self.show_rise_when_set_before_sunset = config.get( IndicatorLunar.CONFIG_SHOW_RISE_WHEN_SET_BEFORE_SUNSET, False )
        self.show_satellite_notification = config.get( IndicatorLunar.CONFIG_SHOW_SATELLITE_NOTIFICATION, False )
        self.show_werewolf_warning = config.get( IndicatorLunar.CONFIG_SHOW_WEREWOLF_WARNING, True )

        self.stars = config.get( IndicatorLunar.CONFIG_STARS, [ ] )

        self.werewolf_warning_message = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE, IndicatorLunar.WEREWOLF_WARNING_MESSAGE_DEFAULT )
        self.werewolf_warning_summary = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY, IndicatorLunar.WEREWOLF_WARNING_SUMMARY_DEFAULT )


    def save_config( self ):
        if self.comets_add_new:
            comets = [ ]

        else:
            comets = self.comets # Only write out the list of comets if the user elects to not add new.

        if self.minor_planets_add_new:
            minor_planets = [ ]

        else:
            minor_planets = self.minor_planets # Only write out the list of minor planets if the user elects to not add new.

        if self.satellites_add_new:
            satellites = [ ]

        else:
            satellites = self.satellites # Only write out the list of satellites if the user elects to not add new.

        return {
            IndicatorLunar.CONFIG_CITY_ELEVATION : self.elevation,
            IndicatorLunar.CONFIG_CITY_LATITUDE : self.latitude,
            IndicatorLunar.CONFIG_CITY_LONGITUDE : self.longitude,
            IndicatorLunar.CONFIG_CITY_NAME : self.city,
            IndicatorLunar.CONFIG_COMETS : comets,
            IndicatorLunar.CONFIG_COMETS_ADD_NEW : self.comets_add_new,
            IndicatorLunar.CONFIG_HIDE_BODIES_BELOW_HORIZON : self.hide_bodies_below_horizon,
            IndicatorLunar.CONFIG_INDICATOR_TEXT : self.indicator_text,
            IndicatorLunar.CONFIG_INDICATOR_TEXT_SEPARATOR : self.indicator_text_separator,
            IndicatorLunar.CONFIG_MINOR_PLANETS : minor_planets,
            IndicatorLunar.CONFIG_MINOR_PLANETS_ADD_NEW : self.minor_planets_add_new,
            IndicatorLunar.CONFIG_MAGNITUDE : self.magnitude,
            IndicatorLunar.CONFIG_PLANETS : self.planets,
            IndicatorLunar.CONFIG_SATELLITE_LIMIT_START : self.satellite_limit_start,
            IndicatorLunar.CONFIG_SATELLITE_LIMIT_END : self.satellite_limit_end,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE : self.satellite_notification_message,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY : self.satellite_notification_summary,
            IndicatorLunar.CONFIG_SATELLITES : satellites,
            IndicatorLunar.CONFIG_SATELLITES_ADD_NEW : self.satellites_add_new,
            IndicatorLunar.CONFIG_SATELLITES_SORT_BY_DATE_TIME : self.satellites_sort_by_date_time,
            IndicatorLunar.CONFIG_SHOW_RISE_WHEN_SET_BEFORE_SUNSET : self.show_rise_when_set_before_sunset,
            IndicatorLunar.CONFIG_SHOW_SATELLITE_NOTIFICATION : self.show_satellite_notification,
            IndicatorLunar.CONFIG_SHOW_WEREWOLF_WARNING : self.show_werewolf_warning,
            IndicatorLunar.CONFIG_STARS : self.stars,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE : self.werewolf_warning_message,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY : self.werewolf_warning_summary
        }


IndicatorLunar().main()
