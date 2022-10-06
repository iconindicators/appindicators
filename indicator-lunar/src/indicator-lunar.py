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


# Application indicator which displays lunar, solar, planetary, minor planet,
# comet, star and satellite information.


#TODO The comets data from COBS does not contain updated absolute magnitude data.
# Also, the data contains spurious data (easier to see in the MPC format).
# Waiting on Jure @ COBS to resolve.


#TODO If comets are unresolved for next release,
# remove 'comet' from the description in debian/control.


#TODO Is it possible/feasible to list meteor showers?
# Daniel Franklin
# git@danielfranklin.id.au
# https://github.com/dfranklinau/astronote/blob/master/astronote/celestial.py
#
# https://www.ta3.sk/IAUC22DB/MDC2022/
# https://www.ta3.sk/IAUC22DB/MDC2022/Roje/roje_lista.php?corobic_roje=1&sort_roje=0
#
# https://www.imo.net/
#
#
# On a quick look, the data from ta3 above could be an ephemeris and be used to compute rise/set/az/alt.
# Issue is visibility..without a magnitude, how to determine if the shower is within range to be visible?


#TODO For satellites and comets / minor planets,
# it is possible a user has checked one body and
# data is updated down the road,
# but that body is no longer present.
# How/when/is that body purged?
#
# Maybe test by either...
#    - Add a dummy item into TLE or OE or AM, then remove.
#    - Add a dummy item to the user preferences of sat/comet/mp.


#TODO Is it possible for apparent magnitude and oe to get out of sync?


INDICATOR_NAME = "indicator-lunar"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )


from dataproviderapparentmagnitude import AM, DataProviderApparentMagnitude
from dataprovidergeneralperturbation import DataProviderGeneralPerturbation, GP
from dataproviderorbitalelement import DataProviderOrbitalElement, OE
from gi.repository import Gtk, Notify
from indicatorbase import IndicatorBase

import datetime, eclipse, locale, math, re, sys, webbrowser


class IndicatorLunar( IndicatorBase ):

    # Allow switching between backends.
    astroBackendPyEphem = "AstroPyEphem"
    astroBackendSkyfield = "AstroSkyfield"
    astroBackendName = astroBackendPyEphem
    astroBackend = getattr( __import__( astroBackendName.lower() ), astroBackendName )

    message = astroBackend.getStatusMessage()
    if message is not None:
        IndicatorBase.showMessageStatic( message, Gtk.MessageType.ERROR, INDICATOR_NAME )
        sys.exit()

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
    CREDIT_ECLIPSES = _( "Eclipse information by Fred Espenak and Jean Meeus. https://eclipse.gsfc.nasa.gov" )
    CREDIT_ECLIPSE_SOLAR_ONLY = _( "Solar eclipse information by Fred Espenak and Jean Meeus. https://eclipse.gsfc.nasa.gov" )
    CREDIT_MINOR_PLANETS = _( "Minor Planet data by Lowell Minor Planet Services. https://asteroid.lowell.edu" )
    CREDIT_SATELLITES = _( "Satellite data by Celestrak. https://www.celestrak.com" )
    if astroBackendName == astroBackendPyEphem:
        CREDIT = [ CREDIT_COMETS, CREDIT_ECLIPSES, CREDIT_MINOR_PLANETS, CREDIT_SATELLITES ] #TODO Remove comets if not ready.

    else:
        CREDIT = [ CREDIT_COMETS, CREDIT_ECLIPSE_SOLAR_ONLY, CREDIT_MINOR_PLANETS, CREDIT_SATELLITES ] #TODO Remove comets if not ready.

    DATA_INDEX_BODY_TYPE = 0
    DATA_INDEX_BODY_NAME = 1
    DATA_INDEX_DATA_NAME = 2

    DATE_TIME_FORMAT_HHcolonMM = "%H:%M"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspacespaceHHcolonMM = "%Y-%m-%d  %H:%M"

    EXTENSION_SVG = ".svg"

    ICON_CACHE_BASENAME = "icon-"
    ICON_CACHE_MAXIMUM_AGE_HOURS = 1 # Keep icons around for an hour to allow multiple instances to run (when testing for example).
    ICON_SATELLITE = INDICATOR_NAME + "-satellite" # Located in /usr/share/icons

    INDICATOR_TEXT_DEFAULT = " [" + astroBackend.NAME_TAG_MOON + " " + astroBackend.DATA_TAG_PHASE + "]"
    INDICATOR_TEXT_SEPARATOR_DEFAULT = ", "

    BODY_TAGS_TRANSLATIONS = dict(
        list( astroBackend.NAME_TAG_MOON_TRANSLATION.items() ) +
        list( astroBackend.PLANET_TAGS_TRANSLATIONS.items() ) +
        [ x for x in zip( astroBackend.getStarNames(), astroBackend.getStarTagTranslations() ) ] +
        list( astroBackend.NAME_TAG_SUN_TRANSLATION.items() ) )

    CACHE_VERSION = "-96-"

    COMET_CACHE_APPARENT_MAGNITUDE_BASENAME = "comet-apparentmagnitude" + CACHE_VERSION
    COMET_CACHE_ORBITAL_ELEMENT_BASENAME = "comet-orbitalelement" + '-' + astroBackendName.lower() + CACHE_VERSION
    COMET_CACHE_MAXIMUM_AGE_HOURS = 96
    COMET_DATA_TYPE = OE.DataType.XEPHEM_COMET if astroBackendName == astroBackendPyEphem else OE.DataType.SKYFIELD_COMET

    MINOR_PLANET_CACHE_APPARENT_MAGNITUDE_BASENAME = "minorplanet-apparentmagnitude" + CACHE_VERSION
    MINOR_PLANET_CACHE_ORBITAL_ELEMENT_BASENAME = "minorplanet-orbitalelement" + '-' + astroBackendName.lower() + CACHE_VERSION
    MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS = 96
    MINOR_PLANET_DATA_TYPE = OE.DataType.XEPHEM_MINOR_PLANET if astroBackendName == astroBackendPyEphem else OE.DataType.SKYFIELD_MINOR_PLANET

    SATELLITE_CACHE_BASENAME = "satellite-generalperturbation" + CACHE_VERSION
    SATELLITE_CACHE_EXTENSION = ".xml"
    SATELLITE_CACHE_MAXIMUM_AGE_HOURS = 48

    SATELLITE_NOTIFICATION_MESSAGE_DEFAULT = \
        _( "Rise Time: " ) + astroBackend.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n" + \
        _( "Rise Azimuth: " ) + astroBackend.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\n" + \
        _( "Set Time: " ) + astroBackend.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n" + \
        _( "Set Azimuth: " ) + astroBackend.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION

    SATELLITE_NOTIFICATION_SUMMARY_DEFAULT = \
        astroBackend.SATELLITE_TAG_NAME + " : " + \
        astroBackend.SATELLITE_TAG_NUMBER + " : " + \
        astroBackend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR + _( " now rising..." )

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

    SEARCH_URL_COMET = "https://www.minorplanetcenter.net/db_search/show_object?utf8=%E2%9C%93&object_id="
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
            indicatorName = INDICATOR_NAME,
            version = "1.0.96",
            copyrightStartYear = "2012",
            comments = _( "Displays lunar, solar, planetary, minor planet, comet, star and satellite information." ), #TODO Remove comet if not available.
            creditz = IndicatorLunar.CREDIT )

        self.debug = True #TODO Testing

        # Dictionary to hold currently calculated (and previously calculated) astronomical data.
        # Key: combination of three tags: body type, body name and data name.
        # Value: a string, regardless being numerical or not.
        # Previous data is used for satellite transits.
        self.data = None
        self.dataPrevious = None

        self.cometOrbitalElementData = { } # Key: comet designation; Value: OE object.  Can be empty but never None.
        self.minorPlanetApparentMagnitudeData = { } # Key: minor planet designation; Value AM object.  Can be empty but never None.
        self.minorPlanetOrbitalElementData = { } # Key: minor planet designation; Value: OE object.  Can be empty but never None.
        self.satelliteGeneralPerturbationData = { } # Key: satellite number; Value: GP object.  Can be empty but never None.
        self.satellitePreviousNotifications = [ ]

        self.lastFullMoonNotfication = datetime.datetime.utcnow() - datetime.timedelta( hours = 1 )

        self.__removeCacheFilesVersion89()
        self.__removeCacheFilesVersion93()
        self.__removeCacheFilesVersion94()
        self.__removeCacheFilesVersion95()
        self.flushTheCache()
        self.initialiseDownloadCountsAndCacheDateTimes()


    def __removeCacheFilesVersion89( self ):
        # In version 90, cache data filenames changed format.
        self.flushCache( "comet-oe-", 0 )
        self.flushCache( "minorplanet-oe-bright-", 0 )
        self.flushCache( "minorplanet-oe-critical-", 0 )
        self.flushCache( "minorplanet-oe-distant-", 0 )
        self.flushCache( "minorplanet-oe-unusual-", 0 )


    def __removeCacheFilesVersion93( self ):
        # In version 94, cache data filenames changed format.
        self.flushCache( "comet-oe-astropyephem-", 0 )
        self.flushCache( "minorplanet-oe-bright-astropyephem-", 0 )
        self.flushCache( "minorplanet-oe-critical-astropyephem-", 0 )
        self.flushCache( "minorplanet-oe-distant-astropyephem-", 0 )
        self.flushCache( "minorplanet-oe-unusual-astropyephem-", 0 )
        self.flushCache( "satellite-tle-", 0 )
        self.flushCache( "satellites-tle-", 0 )

        # In version 94, the full moon icon is now a regular, time-stamped icon.
        self.flushCache( "icon-" + "fullmoon-", 0 )
        self.removeFileFromCache( "icon-" + "fullmoon-" + ".svg" )


    def __removeCacheFilesVersion94( self ):
        # In version 95, cache data filenames changed format.
        self.flushCache( "apparentmagnitude-94-", 0 )
        self.flushCache( "comet-oe-astropyephem-94-", 0 )
        self.flushCache( "minorplanet-oe-astropyephem-94-", 0 )
        self.flushCache( "satellite-tle-94-", 0 )


    def __removeCacheFilesVersion95( self ):
        # In version 95, some cache basenames incorrectly had '--'.
        self.flushCache( "comet-orbitalelement-astropyephem-95-", 0 )
        self.flushCache( "minorplanet-apparentmagnitude--95-", 0 )
        self.flushCache( "minorplanet-orbitalelement-astropyephem-95-", 0 )
        self.flushCache( "satellite-generalperturbation--95-", 0 )


    def flushTheCache( self ):
        self.flushCache( IndicatorLunar.COMET_CACHE_ORBITAL_ELEMENT_BASENAME, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.ICON_CACHE_BASENAME, IndicatorLunar.ICON_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.MINOR_PLANET_CACHE_APPARENT_MAGNITUDE_BASENAME, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.MINOR_PLANET_CACHE_ORBITAL_ELEMENT_BASENAME, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.SATELLITE_CACHE_BASENAME, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS )


    def initialiseDownloadCountsAndCacheDateTimes( self ):
        self.downloadCountApparentMagnitude = 0
        self.downloadCountComet = 0
        self.downloadCountMinorPlanet = 0
        self.downloadCountSatellite = 0

        utcNow = datetime.datetime.utcnow()
        self.nextDownloadTimeApparentMagnitude = utcNow
        self.nextDownloadTimeComet = utcNow
        self.nextDownloadTimeMinorPlanet = utcNow
        self.nextDownloadTimeSatellite = utcNow


    def update( self, menu ):
        utcNow = datetime.datetime.utcnow()

        # Update comet minor planet and satellite cached data.
        self.updateData( utcNow )

        # Update backend.
        self.dataPrevious = self.data
        self.data = IndicatorLunar.astroBackend.calculate(
            utcNow,
            self.latitude, self.longitude, self.elevation,
            self.planets,
            self.stars,
            self.satellites, self.satelliteGeneralPerturbationData,
            *self.convertStartHourAndEndHourToDateTimeInUTC( self.satelliteLimitStart, self.satelliteLimitEnd ),
            self.comets, self.cometOrbitalElementData, None,
            self.minorPlanets, self.minorPlanetOrbitalElementData, self.minorPlanetApparentMagnitudeData,
            self.magnitude,
            self.getLogging() )

        if self.dataPrevious is None: # Happens only on first run or when the user alters the satellite visibility window.
            self.dataPrevious = self.data

        # Update frontend.
        if self.debug:
            menu.append( Gtk.MenuItem.new_with_label( IndicatorLunar.astroBackendName + ": " + IndicatorLunar.astroBackend.getVersion() ) )

        self.updateMenu( menu, utcNow )
        self.setLabel( self.processTags() )
        self.updateIcon()

        if self.showWerewolfWarning:
            self.notificationFullMoon()

        if self.showSatelliteNotification:
            self.notificationSatellites()

        return self.getNextUpdateTimeInSeconds()


    def updateData( self, utcNow ):
        # Update comet data.
#TODO Commented out until comets are resolved.
        # self.cometOrbitalElementData, self.downloadCountComet, self.nextDownloadTimeComet= self.__updateData(
        #     utcNow, self.cometOrbitalElementData,
        #     IndicatorLunar.COMET_CACHE_ORBITAL_ELEMENT_BASENAME, IndicatorBase.EXTENSION_TEXT, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS,
        #     self.downloadCountComet, self.nextDownloadTimeComet,
        #     DataProviderOrbitalElement.download, [ IndicatorLunar.COMET_DATA_TYPE, None ],
        #     DataProviderOrbitalElement.load, [ IndicatorLunar.COMET_DATA_TYPE ] )

        if self.cometsAddNew:
            self.addNewBodies( self.cometOrbitalElementData, self.comets )

        # Update minor planet data.
        self.minorPlanetOrbitalElementData, self.downloadCountMinorPlanet, self.nextDownloadTimeMinorPlanet = self.__updateData(
            utcNow, self.minorPlanetOrbitalElementData,
            IndicatorLunar.MINOR_PLANET_CACHE_ORBITAL_ELEMENT_BASENAME, IndicatorBase.EXTENSION_TEXT, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS,
            self.downloadCountMinorPlanet, self.nextDownloadTimeMinorPlanet,
            DataProviderOrbitalElement.download, [ IndicatorLunar.MINOR_PLANET_DATA_TYPE, IndicatorLunar.astroBackend.MAGNITUDE_MAXIMUM ],
            DataProviderOrbitalElement.load, [ IndicatorLunar.MINOR_PLANET_DATA_TYPE ] )

        if self.minorPlanetsAddNew:
            self.addNewBodies( self.minorPlanetOrbitalElementData, self.minorPlanets )

        # Update minor planet apparent magnitudes.
        self.minorPlanetApparentMagnitudeData, self.downloadCountApparentMagnitude, self.nextDownloadTimeApparentMagnitude = self.__updateData(
            utcNow, self.minorPlanetApparentMagnitudeData,
            IndicatorLunar.MINOR_PLANET_CACHE_APPARENT_MAGNITUDE_BASENAME, IndicatorBase.EXTENSION_TEXT, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS,
            self.downloadCountApparentMagnitude, self.nextDownloadTimeApparentMagnitude,
            DataProviderApparentMagnitude.download, [ False, IndicatorLunar.astroBackend.MAGNITUDE_MAXIMUM ],
            DataProviderApparentMagnitude.load, [ ] )

        # Update satellite data.
        self.satelliteGeneralPerturbationData, self.downloadCountSatellite, self.nextDownloadTimeSatellite = self.__updateData(
            utcNow, self.satelliteGeneralPerturbationData,
            IndicatorLunar.SATELLITE_CACHE_BASENAME, IndicatorLunar.SATELLITE_CACHE_EXTENSION, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS,
            self.downloadCountSatellite, self.nextDownloadTimeSatellite,
            DataProviderGeneralPerturbation.download, [ ],
            DataProviderGeneralPerturbation.load, [ ] )

        if self.satellitesAddNew:
            self.addNewBodies( self.satelliteGeneralPerturbationData, self.satellites )


    # Get the data from the cache, or if stale, download from the source.
    def __updateData(
            self, utcNow, currentData,
            cacheBasename, cacheExtension, cacheMaximumAge,
            downloadCount, nextDownloadTime,
            downloadDataFunction, downloadDataAdditionalArguments,
            loadDataFunction, loadDataAdditionalArguments ):

        if self.isCacheStale( utcNow, cacheBasename, cacheMaximumAge ):
            freshData = { }
            if nextDownloadTime < utcNow: # Download is allowed (do not want to annoy third-party data provider).
                downloadDataFilename = self.getCacheFilenameWithTimestamp( cacheBasename, cacheExtension )
                if downloadDataFunction( downloadDataFilename, self.getLogging(), *downloadDataAdditionalArguments ):
                    downloadCount = 0
                    nextDownloadTime = utcNow + datetime.timedelta( hours = cacheMaximumAge )
                    freshData = loadDataFunction( downloadDataFilename, self.getLogging(), *loadDataAdditionalArguments )

                else:
                    downloadCount += 1
                    nextDownloadTime = self.__getNextDownloadTime( utcNow, downloadCount ) # Download failed for some reason; retry at a later time.

        else:
            # Cache is not stale; only load off disk as necessary.
            if currentData:
                freshData = currentData

            else:
                downloadDataFilename = self.getCacheNewestFilename( cacheBasename ) # Should NOT return None as the cache was checked for staleness above.
                freshData = loadDataFunction( downloadDataFilename, self.getLogging(), *loadDataAdditionalArguments )

        return freshData, downloadCount, nextDownloadTime


    def __getNextDownloadTime( self, utcNow, downloadCount ):
        nextDownloadTime = utcNow + datetime.timedelta( minutes = 60 * 24 ) # Worst case scenario for retrying downloads: every 24 hours.
        timeIntervalInMinutes = {
            1 : 5,
            2 : 15,
            3 : 60 }

        if downloadCount in timeIntervalInMinutes:
            nextDownloadTime = utcNow + datetime.timedelta( minutes = timeIntervalInMinutes[ downloadCount ] )

        return nextDownloadTime


    def addNewBodies( self, data, bodies ):
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
    def processTags( self ):

        # Handle [ ].
        # There may still be tags left in as a result of say a satellite or comet dropping out.
        # Remaining tags are moped up at the end.
        processedText = self.indicatorText
        for key in self.data.keys():
            tag = "[" + key[ IndicatorLunar.DATA_INDEX_BODY_NAME ] + " " + key[ IndicatorLunar.DATA_INDEX_DATA_NAME ] + "]"
            if tag in processedText:
                data = self.formatData( key[ IndicatorLunar.DATA_INDEX_DATA_NAME ], self.data[ key ] )
                processedText = processedText.replace( tag, data )

        # Handle text enclosed by { }.
        i = 0
        lastSeparatorIndex = -1 # Track the last insertion point of the separator so it can be removed.
        tagRegularExpression = "\[[^\[\]]*\]"
        while( i < len( processedText ) ):
            if processedText[ i ] == '{':
                j = i + 1
                while( j < len( processedText ) ):
                    if processedText[ j ] == '}':
                        text = processedText[ i + 1 : j ] # Text between braces.
                        textMinusUnknownTags = re.sub( tagRegularExpression, "", text ) # Text between braces with outstanding/unknown tags removed.
                        if len( text ) and text == textMinusUnknownTags: # Text is not empty and no unknown tags found, so keep this text.
                            processedText = processedText[ 0 : i ] + processedText[ i + 1 : j ] + self.indicatorTextSeparator + processedText[ j + 1 : ]
                            lastSeparatorIndex = j - 1

                        else: # Empty text or there was one or more unknown tags found, so drop the text.
                            processedText = processedText[ 0 : i ] + processedText[ j + 1 : ]

                        i -= 1
                        break

                    j += 1

            i += 1

        if lastSeparatorIndex > -1:
            processedText = processedText[ 0 : lastSeparatorIndex ] + processedText[ lastSeparatorIndex + len( self.indicatorTextSeparator ) : ] # Remove the last separator.

        processedText = re.sub( tagRegularExpression, "", processedText ) # Remove remaining tags (not removed because they were not contained within { }).
        return processedText


    def getNextUpdateTimeInSeconds( self ):
        dateTimes = [ ]
        for key in self.data:
            dataName = key[ IndicatorLunar.DATA_INDEX_DATA_NAME ]
            if key[ IndicatorLunar.DATA_INDEX_BODY_TYPE ] == IndicatorLunar.astroBackend.BodyType.SATELLITE:
                if dataName == IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME:
                    dateTime = datetime.datetime.strptime( self.data[ key ], IndicatorLunar.astroBackend.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS )
                    dateTimeMinusFourMinutes = dateTime - datetime.timedelta( minutes = 4 ) # Set an earlier time for the rise to ensure the rise and set are displayed.
                    dateTimes.append( dateTimeMinusFourMinutes )

                elif dataName == IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME:
                    dateTimes.append( datetime.datetime.strptime( self.data[ key ], IndicatorLunar.astroBackend.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS ) )

            else:
                if dataName == IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_DATE_TIME or \
                   dataName == IndicatorLunar.astroBackend.DATA_TAG_EQUINOX or \
                   dataName == IndicatorLunar.astroBackend.DATA_TAG_FIRST_QUARTER or \
                   dataName == IndicatorLunar.astroBackend.DATA_TAG_FULL or \
                   dataName == IndicatorLunar.astroBackend.DATA_TAG_NEW or \
                   dataName == IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME or \
                   dataName == IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME or \
                   dataName == IndicatorLunar.astroBackend.DATA_TAG_SOLSTICE or \
                   dataName == IndicatorLunar.astroBackend.DATA_TAG_THIRD_QUARTER:
                    dateTimes.append( datetime.datetime.strptime( self.data[ key ], IndicatorLunar.astroBackend.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS ) )

        utcNow = datetime.datetime.utcnow()
        utcNowPlusOneMinute = utcNow + datetime.timedelta( minutes = 1 ) # Ensure updates don't happen more frequently than every minute.
        nextUpdateTime = utcNow + datetime.timedelta( minutes = 20 ) # Do an update at most twenty minutes from now (keeps the moon icon and data fresh).
        nextUpdateInSeconds = int( math.ceil( ( nextUpdateTime - utcNow ).total_seconds() ) )
        for dateTime in sorted( dateTimes ):
            if dateTime > nextUpdateTime:
                break

            if dateTime > utcNowPlusOneMinute:
                nextUpdateTime = dateTime
                nextUpdateInSeconds = int( math.ceil( ( nextUpdateTime - utcNow ).total_seconds() ) )
                break

        return nextUpdateInSeconds


    def updateMenu( self, menu, utcNow ):
        self.updateMenuMoon( menu )
        self.updateMenuSun( menu )
        self.updateMenuPlanetsMinorPlanetsCometsStars( menu, _( "Planets" ), self.planets, IndicatorLunar.astroBackend.BodyType.PLANET )
        self.updateMenuPlanetsMinorPlanetsCometsStars( menu, _( "Minor Planets" ), self.minorPlanets, IndicatorLunar.astroBackend.BodyType.MINOR_PLANET )
        self.updateMenuPlanetsMinorPlanetsCometsStars( menu, _( "Comets" ), self.comets, IndicatorLunar.astroBackend.BodyType.COMET )
        self.updateMenuPlanetsMinorPlanetsCometsStars( menu, _( "Stars" ), self.stars, IndicatorLunar.astroBackend.BodyType.STAR )
        self.updateMenuSatellites( menu, utcNow )


    def updateIcon( self ):
        # Ideally overwrite the icon with the same name each time.
        # Due to a bug, the icon name must change between calls to set the icon.
        # So change the name each time incorporating the current date/time.
        #    https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620
        #    http://askubuntu.com/questions/490634/application-indicator-icon-not-changing-until-clicked
        key = ( IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ILLUMINATION, ) ] )
        lunarBrightLimbAngleInDegrees = int( math.degrees( float( self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_BRIGHT_LIMB, ) ] ) ) )
        svgIconText = self.getSVGIconText( lunarIlluminationPercentage, lunarBrightLimbAngleInDegrees )
        iconFilename = self.writeCacheText( svgIconText, IndicatorLunar.ICON_CACHE_BASENAME, IndicatorLunar.EXTENSION_SVG )
        self.indicator.set_icon_full( iconFilename, "" )


    def notificationFullMoon( self ):
        utcNow = datetime.datetime.utcnow()
        key = ( IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ILLUMINATION, ) ] )
        lunarPhase = self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_PHASE, ) ]

        if ( lunarPhase == IndicatorLunar.astroBackend.LUNAR_PHASE_WAXING_GIBBOUS or lunarPhase == IndicatorLunar.astroBackend.LUNAR_PHASE_FULL_MOON ) and \
           lunarIlluminationPercentage >= 96 and \
           ( ( self.lastFullMoonNotfication + datetime.timedelta( hours = 1 ) ) < utcNow ):

            summary = self.werewolfWarningSummary
            if self.werewolfWarningSummary == "":
                summary = " " # The notification summary text cannot be empty (at least on Unity).

            Notify.Notification.new( summary, self.werewolfWarningMessage, self.createFullMoonIcon() ).show()
            self.lastFullMoonNotfication = utcNow


    def createFullMoonIcon( self ):
        return self.writeCacheText(
            self.getSVGIconText( 100, None ),
            IndicatorLunar.ICON_CACHE_BASENAME,
            IndicatorLunar.EXTENSION_SVG )


    def notificationSatellites( self ):
        INDEX_NUMBER = 0
        INDEX_RISE_TIME = 1
        satelliteCurrentNotifications = [ ]

        utcNow = datetime.datetime.utcnow()
        for number in self.satellites:
            key = ( IndicatorLunar.astroBackend.BodyType.SATELLITE, number )
            if ( key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH, ) ) in self.data and number not in self.satellitePreviousNotifications: # About to rise and no notification already sent.
                riseTime = datetime.datetime.strptime(
                    self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ],
                    IndicatorLunar.astroBackend.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS )

                if ( riseTime - datetime.timedelta( minutes = 2 ) ) <= utcNow: # Two minute buffer.
                    satelliteCurrentNotifications.append( [ number, riseTime ] )
                    self.satellitePreviousNotifications.append( number )

            if ( key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ) in self.data:
                setTime = datetime.datetime.strptime(
                    self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ],
                    IndicatorLunar.astroBackend.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS )

                if number in self.satellitePreviousNotifications and setTime < utcNow: # Notification has been sent and satellite has now set.
                    self.satellitePreviousNotifications.remove( number )

        for number, riseTime in sorted( satelliteCurrentNotifications, key = lambda x: ( x[ INDEX_RISE_TIME ], x[ INDEX_NUMBER ] ) ):
            self.__notificationSatellite( number, riseTime )


    def __notificationSatellite( self, number, riseTime ):
        key = ( IndicatorLunar.astroBackend.BodyType.SATELLITE, number )

        riseTime = self.formatData(
            IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME,
            self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ],
            IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )

        riseAzimuth = self.formatData(
            IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH, 
            self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH, ) ], 
            IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )

        setTime = self.formatData(
            IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME,
            self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ],
            IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )

        setAzimuth = self.formatData(
            IndicatorLunar.astroBackend.DATA_TAG_SET_AZIMUTH,
            self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_AZIMUTH, ) ],
            IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )

        summary = \
            self.satelliteNotificationSummary. \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NAME, self.satelliteGeneralPerturbationData[ number ].getName() ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NUMBER, self.satelliteGeneralPerturbationData[ number ].getNumber() ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satelliteGeneralPerturbationData[ number ].getInternationalDesignator() ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_TIME, riseTime ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_TIME, setTime ) + \
            " " # The notification summary text must not be empty (at least on Unity).

        message = \
            self.satelliteNotificationMessage. \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NAME, self.satelliteGeneralPerturbationData[ number ].getName() ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NUMBER, self.satelliteGeneralPerturbationData[ number ].getNumber() ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satelliteGeneralPerturbationData[ number ].getInternationalDesignator() ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_TIME, riseTime ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
            replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_TIME, setTime )

        Notify.Notification.new( summary, message, IndicatorLunar.ICON_SATELLITE ).show()


    def updateMenuMoon( self, menu ):
        subMenu = Gtk.Menu()
        if self.__updateMenuCommon( subMenu, IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON, self.getMenuIndent( 1 ), IndicatorLunar.SEARCH_URL_MOON ):
            self.createMenuItemAndAppend( menu, _( "Moon" ), "" ).set_submenu( subMenu )
            subMenu.append( Gtk.SeparatorMenuItem() )
            key = ( IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON )

            self.createMenuItemAndAppend(
                subMenu,
                self.getMenuIndent( 1 ) + \
                _( "Phase: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_PHASE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_PHASE, ) ] ),
                IndicatorLunar.SEARCH_URL_MOON )

            self.createMenuItemAndAppend(
                subMenu,
                self.getMenuIndent( 1 ) + _( "Next Phases" ),
                IndicatorLunar.SEARCH_URL_MOON )

            # The phase (illumination) is rounded and so a given phase is entered earlier than what occurs in reality.
            nextPhases = [ ]
            nextPhases.append(
                [ self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_FIRST_QUARTER, ) ],
                 _( "First Quarter: " ), key + ( IndicatorLunar.astroBackend.DATA_TAG_FIRST_QUARTER, ) ] )

            nextPhases.append(
                [ self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_FULL, ) ],
                _( "Full: " ), key + ( IndicatorLunar.astroBackend.DATA_TAG_FULL, ) ] )

            nextPhases.append(
                [ self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_NEW, ) ],
                _( "New: " ), key + ( IndicatorLunar.astroBackend.DATA_TAG_NEW, ) ] )

            nextPhases.append(
                [ self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_THIRD_QUARTER, ) ],
                _( "Third Quarter: " ), key + ( IndicatorLunar.astroBackend.DATA_TAG_THIRD_QUARTER, ) ] )

            for dateTime, displayText, key in sorted( nextPhases, key = lambda pair: pair[ 0 ] ): # Sort by date of each phase (the first element).
                label = self.getMenuIndent( 2 ) + displayText + self.formatData( key[ IndicatorLunar.DATA_INDEX_DATA_NAME ], self.data[ key ] )
                self.createMenuItemAndAppend( subMenu, label, IndicatorLunar.SEARCH_URL_MOON )

            self.__updateMenuEclipse( subMenu, IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON, IndicatorLunar.SEARCH_URL_MOON )


    def updateMenuSun( self, menu ):
        subMenu = Gtk.Menu()
        if self.__updateMenuCommon( subMenu, IndicatorLunar.astroBackend.BodyType.SUN, IndicatorLunar.astroBackend.NAME_TAG_SUN, self.getMenuIndent( 1 ), IndicatorLunar.SEARCH_URL_SUN ):
            self.createMenuItemAndAppend( menu, _( "Sun" ), "" ).set_submenu( subMenu )
            subMenu.append( Gtk.SeparatorMenuItem() )
            key = ( IndicatorLunar.astroBackend.BodyType.SUN, IndicatorLunar.astroBackend.NAME_TAG_SUN )

            equinoxLabel = \
                self.getMenuIndent( 1 ) + \
                _( "Equinox: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_EQUINOX, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_EQUINOX, ) ] )

            solsticeLabel = \
                self.getMenuIndent( 1 ) + \
                _( "Solstice: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_SOLSTICE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SOLSTICE, ) ] )

            if self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_EQUINOX, ) ] < self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SOLSTICE, ) ]:
                self.createMenuItemAndAppend( subMenu, equinoxLabel, IndicatorLunar.SEARCH_URL_SUN )
                self.createMenuItemAndAppend( subMenu, solsticeLabel, IndicatorLunar.SEARCH_URL_SUN )

            else:
                self.createMenuItemAndAppend( subMenu, solsticeLabel, IndicatorLunar.SEARCH_URL_SUN )
                self.createMenuItemAndAppend( subMenu, equinoxLabel, IndicatorLunar.SEARCH_URL_SUN )

            self.__updateMenuEclipse( subMenu, IndicatorLunar.astroBackend.BodyType.SUN, IndicatorLunar.astroBackend.NAME_TAG_SUN, IndicatorLunar.SEARCH_URL_SUN )


    def __updateMenuEclipse( self, menu, bodyType, nameTag, url ):
        menu.append( Gtk.SeparatorMenuItem() )
        key = ( bodyType, nameTag )

        self.createMenuItemAndAppend( menu, self.getMenuIndent( 1 ) + _( "Eclipse" ), url )

        self.createMenuItemAndAppend(
            menu,
            self.getMenuIndent( 2 ) + \
            _( "Date/Time: " ) + \
            self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_DATE_TIME, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_DATE_TIME, ) ] ),
            url )

        self.createMenuItemAndAppend( 
            menu,
            self.getMenuIndent( 2 ) + \
            _( "Type: " ) + \
            self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_TYPE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_TYPE, ) ] ),
            url )

        if key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LATITUDE, ) in self.data: # PyEphem uses the NASA Eclipse data which contains latitude/longitude; Skyfield does not.
            latitude = self.formatData(
                IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LATITUDE,
                self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LATITUDE, ) ] )

            longitude = self.formatData(
                IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LONGITUDE,
                self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LONGITUDE, ) ] )

            self.createMenuItemAndAppend(
                menu,
                self.getMenuIndent( 2 ) + _( "Latitude/Longitude: " ) + latitude + " " + longitude,
                url )


    def updateMenuPlanetsMinorPlanetsCometsStars( self, menu, menuLabel, bodies, bodyType ):

        def getURLPlanet( name ): return IndicatorLunar.SEARCH_URL_PLANET + name.lower()
        def getURLMinorPlanet( name ): return IndicatorLunar.SEARCH_URL_MINOR_PLANET + name
        def getURLComet( name ): return IndicatorLunar.SEARCH_URL_COMET + IndicatorLunar.astroBackend.getDesignationComet( name ) #TODO Test
        def getURLStar( name ): return IndicatorLunar.SEARCH_URL_STAR + str( IndicatorLunar.astroBackend.getStarHIP( name ) )


        def getURLFunction( bodyType ):
            if bodyType == IndicatorLunar.astroBackend.BodyType.PLANET: urlFunction = getURLPlanet
            elif bodyType == IndicatorLunar.astroBackend.BodyType.MINOR_PLANET: urlFunction = getURLMinorPlanet
            elif bodyType == IndicatorLunar.astroBackend.BodyType.COMET: urlFunction = getURLComet
            elif bodyType == IndicatorLunar.astroBackend.BodyType.STAR: urlFunction = getURLStar

            return urlFunction


        def getDisplayNamePlanet( name ): return IndicatorLunar.astroBackend.PLANET_NAMES_TRANSLATIONS[ name ]
        def getDisplayNameMinorPlanet( name ): return name if name[ 0 ].isdigit() else name.title() #TODO Check if this instead can just be the name.
        def getDisplayNameComet( name ): return name if name[ 0 ].isdigit() else name.title()
        def getDisplayNameStar( name ): return IndicatorLunar.astroBackend.getStarNameTranslation( name )


        def getDisplayNameFunction( bodyType ):
            if bodyType == IndicatorLunar.astroBackend.BodyType.PLANET: displayNameFunction = getDisplayNamePlanet
            elif bodyType == IndicatorLunar.astroBackend.BodyType.MINOR_PLANET: displayNameFunction = getDisplayNameMinorPlanet
            elif bodyType == IndicatorLunar.astroBackend.BodyType.COMET: displayNameFunction = getDisplayNameComet
            elif bodyType == IndicatorLunar.astroBackend.BodyType.STAR: displayNameFunction = getDisplayNameStar

            return displayNameFunction


        urlFunction = getURLFunction( bodyType )
        displayNameFunction = getDisplayNameFunction( bodyType )
        indent = self.getMenuIndent( 1 )
        indentDouble = self.getMenuIndent( 2 )
        subMenu = Gtk.Menu()
        for name in bodies:
            current = len( subMenu )
            url = urlFunction( name )
            if self.__updateMenuCommon( subMenu, bodyType, name, indentDouble, url ):
                displayName = displayNameFunction( name )
                self.createMenuItemAndInsert( subMenu, indent + displayName, url, current )
                subMenu.append( Gtk.SeparatorMenuItem() )

        if len( subMenu.get_children() ) > 0:
            self.createMenuItemAndAppend( menu, menuLabel, "" ).set_submenu( subMenu )


#TODO Update
    #    The user preference for hiding a body if the body is below the horizon.
    #
    #    The astro backend behaviour:
    #        The rise/set/az/alt is present for a body which rises and sets.
    #        The az/alt is present for a body 'always up'.
    #        No data is present for a body 'never up'.
    def __updateMenuCommon( self, menu, bodyType, nameTag, indent, onClickURL = "" ):
        key = ( bodyType, nameTag )
        appended = False
        if key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) in self.data: # This body rises/sets.
            if self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] < self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ]: # Body will rise.
                if not self.hideBodiesBelowHorizon:
                    self.__updateMenuItemsRiseAzimuthAltitudeSet( menu, key, indent, onClickURL, True, False )
                    appended = True

            else: # Body will set.
                if self.showRiseWhenSetBeforeSunset:
                    targetBodyType = \
                        bodyType == IndicatorLunar.astroBackend.BodyType.COMET or \
                        bodyType == IndicatorLunar.astroBackend.BodyType.MINOR_PLANET or \
                        bodyType == IndicatorLunar.astroBackend.BodyType.PLANET or \
                        bodyType == IndicatorLunar.astroBackend.BodyType.STAR
                    keySun = ( IndicatorLunar.astroBackend.BodyType.SUN, IndicatorLunar.astroBackend.NAME_TAG_SUN )
                    sunRise = self.data[ keySun + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ]
                    sunSet = self.data[ keySun + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ]
                    if targetBodyType and sunSet < sunRise and self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ] < sunSet:
                        if not self.hideBodiesBelowHorizon:
                            self.__updateMenuItemsRiseAzimuthAltitudeSet( menu, key, indent, onClickURL, True, False )
                            appended = True

                    else:
                        self.__updateMenuItemsRiseAzimuthAltitudeSet( menu, key, indent, onClickURL, False, True )
                        appended = True

                else:
                    self.__updateMenuItemsRiseAzimuthAltitudeSet( menu, key, indent, onClickURL, False, True )
                    appended = True

        elif key + ( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, ) in self.data: # Body is 'always up'.
            self.__updateMenuItemsRiseAzimuthAltitudeSet( menu, key, indent, onClickURL, False, False )
            appended = True

        return appended


    def __updateMenuItemsRiseAzimuthAltitudeSet( self, menu, key, indent, onClickURL, rise, set ):
        if rise:
            self.createMenuItemAndAppend(
                menu,
                indent + \
                _( "Rise: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] ),
                onClickURL )

        else:
            self.createMenuItemAndAppend(
                menu,
                indent + \
                _( "Azimuth: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, ) ] ),
                onClickURL )

            self.createMenuItemAndAppend(
                menu,
                indent + \
                _( "Altitude: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, ) ] ),
                onClickURL )

            if set:
                self.createMenuItemAndAppend(
                    menu,
                    indent + \
                    _( "Set: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ] ),
                    onClickURL )


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
    #                utcNow             utcNow + 5
    #
    # When ( R < utcNow + 5 ) display next rise/set.
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
    #                utcNow             utcNow + 5
    #
    # When ( R < utcNow + 5 ) AND ( S > utcNow ) display previous rise/set.
    def updateMenuSatellites( self, menu, utcNow ):
        satellites = [ ]
        satellitesPolar = [ ]
        now = IndicatorLunar.astroBackend.toDateTimeString( utcNow )
        nowPlusFiveMinutes = IndicatorLunar.astroBackend.toDateTimeString( utcNow + datetime.timedelta( minutes = 5 ) )

        for number in self.satellites:
            key = ( IndicatorLunar.astroBackend.BodyType.SATELLITE, number )
            if key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) in self.data: # Satellite rises/sets.
                if self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] < nowPlusFiveMinutes: # Satellite will rise within the next five minutes.
                    satellites.append( [
                        number,
                        self.satelliteGeneralPerturbationData[ number ].getName(),
                        self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ],
                        self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH, ) ],
                        self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ],
                        self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_AZIMUTH, ) ] ] )

                else: # Satellite will rise more than five minutes from now; look at previous transit.
                    if key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) in self.dataPrevious:
                        inTransit = \
                            self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] < nowPlusFiveMinutes and \
                            self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ] > now

                        if inTransit:
                            satellites.append( [
                                number,
                                self.satelliteGeneralPerturbationData[ number ].getName(),
                                self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ],
                                self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH, ) ],
                                self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ],
                                self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_AZIMUTH, ) ] ] )

                        else: # Previous transit is complete (and too far back in the past to be applicable), so show next pass.
                            satellites.append( [
                                number,
                                self.satelliteGeneralPerturbationData[ number ].getName(),
                                self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] ] )

                    else: # No previous transit, show next pass.
                        satellites.append( [
                            number,
                            self.satelliteGeneralPerturbationData[ number ].getName(),
                            self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] ] )

            elif key + ( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, ) in self.data: # Satellite is polar (always up).
                satellitesPolar.append( [
                    number,
                    self.satelliteGeneralPerturbationData[ number ].getName(),
                    self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, ) ],
                    self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, ) ] ] )

        if satellites:
            if self.satellitesSortByDateTime:
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

            self.__updateMenuSatellites( menu, _( "Satellites" ), satellites )

        if satellitesPolar:
            satellitesPolar = sorted(
                satellitesPolar,
                key = lambda x: ( x[ IndicatorLunar.SATELLITE_MENU_NAME ], x[ IndicatorLunar.SATELLITE_MENU_NUMBER ] ) ) # Sort by name then number.

            self.__updateMenuSatellites( menu, _( "Satellites (Polar)" ), satellitesPolar )


    def __updateMenuSatellites( self, menu, label, satellites ):
        menuItem = self.createMenuItemAndAppend( menu, label, "" )
        subMenu = Gtk.Menu()
        menuItem.set_submenu( subMenu )
        indent = self.getMenuIndent( 1 )
        indentDouble = self.getMenuIndent( 2 )
        indentTriple = self.getMenuIndent( 3 )
        for info in satellites:
            number = info[ IndicatorLunar.SATELLITE_MENU_NUMBER ]
            name = info[ IndicatorLunar.SATELLITE_MENU_NAME ]
            key = ( IndicatorLunar.astroBackend.BodyType.SATELLITE, number )
            url = IndicatorLunar.SEARCH_URL_SATELLITE + "lat=" + str( self.latitude ) + "&lng=" + str( self.longitude ) + "&satid=" + number
            label = indent + name + " : " + number + " : " + self.satelliteGeneralPerturbationData[ number ].getInternationalDesignator()
            menuItem = self.createMenuItemAndAppend( subMenu, label, url )
            if len( info ) == 3: # Satellite yet to rise.
                data = self.formatData( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, info[ IndicatorLunar.SATELLITE_MENU_RISE_DATE_TIME ] )
                self.createMenuItemAndAppend( subMenu, indentDouble + _( "Rise Date/Time: " ) + data, url )

            elif len( info ) == 4: # Circumpolar (always up).
                data = self.formatData( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, info[ IndicatorLunar.SATELLITE_MENU_AZIMUTH ] )
                self.createMenuItemAndAppend( subMenu, indentDouble + _( "Azimuth: " ) + data, url )

                data = self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, info[ IndicatorLunar.SATELLITE_MENU_ALTITUDE ] )
                self.createMenuItemAndAppend( subMenu, indentDouble + _( "Altitude: " ) + data, url )

            else: # Satellite is in transit.
                self.createMenuItemAndAppend( subMenu, indentDouble + _( "Rise" ), url )

                data = self.formatData( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, info[ IndicatorLunar.SATELLITE_MENU_RISE_DATE_TIME ] )
                self.createMenuItemAndAppend( subMenu, indentTriple + _( "Date/Time: " ) + data, url )

                data = self.formatData( IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH, info[ IndicatorLunar.SATELLITE_MENU_RISE_AZIMUTH ] )
                self.createMenuItemAndAppend( subMenu, indentTriple + _( "Azimuth: " ) + data, url )

                self.createMenuItemAndAppend( subMenu, indentDouble + _( "Set" ), url )

                data = self.formatData( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, info[ IndicatorLunar.SATELLITE_MENU_SET_DATE_TIME ] )
                self.createMenuItemAndAppend( subMenu, indentTriple + _( "Date/Time: " ) + data, url )

                data = self.formatData( IndicatorLunar.astroBackend.DATA_TAG_SET_AZIMUTH, info[ IndicatorLunar.SATELLITE_MENU_SET_AZIMUTH ] )
                self.createMenuItemAndAppend( subMenu, indentTriple + _( "Azimuth: " ) + data, url )

            separator = Gtk.SeparatorMenuItem()
            subMenu.append( separator )

        subMenu.remove( separator ) #TODO Now seems silly to have this...can the planets function methodology be used here instead?


    def createMenuItemAndAppend( self, menu, label, onClickURL ):
        menuItem = self.__createMenuItem( label, onClickURL )
        menu.append( menuItem )
        return menuItem


    def createMenuItemAndInsert( self, menu, label, onClickURL, index ):
        menuItem = self.__createMenuItem( label, onClickURL )
        menu.insert( menuItem, index )
        return menuItem


    def __createMenuItem( self, label, onClickURL ):
        menuItem = Gtk.MenuItem.new_with_label( label )
        if onClickURL:
            menuItem.set_name( onClickURL )
            menuItem.connect( "activate", self.onMenuItemClick )

        return menuItem


    def onMenuItemClick( self, widget ): webbrowser.open( widget.props.name )


    def formatData( self, dataTag, data, dateTimeFormat = None ):
        displayData = None

        if dataTag == IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE or \
           dataTag == IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH or \
           dataTag == IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH or \
           dataTag == IndicatorLunar.astroBackend.DATA_TAG_SET_AZIMUTH:
            displayData = str( round( math.degrees( float( data ) ) ) ) + "°"

        elif dataTag == IndicatorLunar.astroBackend.DATA_TAG_BRIGHT_LIMB:
            displayData = str( int( float( data ) ) ) + "°"

        elif dataTag == IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_DATE_TIME or \
             dataTag == IndicatorLunar.astroBackend.DATA_TAG_EQUINOX or \
             dataTag == IndicatorLunar.astroBackend.DATA_TAG_FIRST_QUARTER or \
             dataTag == IndicatorLunar.astroBackend.DATA_TAG_FULL or \
             dataTag == IndicatorLunar.astroBackend.DATA_TAG_NEW or \
             dataTag == IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME or \
             dataTag == IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME or \
             dataTag == IndicatorLunar.astroBackend.DATA_TAG_SOLSTICE or \
             dataTag == IndicatorLunar.astroBackend.DATA_TAG_THIRD_QUARTER:
                if dateTimeFormat is None:
                    displayData = self.toLocalDateTimeString( data, IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspacespaceHHcolonMM )

                else:
                    displayData = self.toLocalDateTimeString( data, dateTimeFormat )

        elif dataTag == IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LATITUDE:
            latitude = data
            if latitude[ 0 ] == "-":
                displayData = latitude[ 1 : ] + "° " + _( "S" )

            else:
                displayData = latitude + "° " +_( "N" )

        elif dataTag == IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LONGITUDE:
            longitude = data
            if longitude[ 0 ] == "-":
                displayData = longitude[ 1 : ] + "° " + _( "E" )

            else:
                displayData = longitude + "° " +_( "W" )

        elif dataTag == IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_TYPE:
            if data == eclipse.ECLIPSE_TYPE_ANNULAR:
                displayData = _( "Annular" )

            elif data == eclipse.ECLIPSE_TYPE_HYBRID:
                displayData = _( "Hybrid (Annular/Total)" )

            elif data == eclipse.ECLIPSE_TYPE_PARTIAL:
                displayData = _( "Partial" )

            elif data == eclipse.ECLIPSE_TYPE_PENUMBRAL:
                displayData = _( "Penumbral" )

            else: # Assume eclipse.ECLIPSE_TYPE_TOTAL:
                displayData = _( "Total" )

        elif dataTag == IndicatorLunar.astroBackend.DATA_TAG_ILLUMINATION:
            displayData = data + "%"

        elif dataTag == IndicatorLunar.astroBackend.DATA_TAG_PHASE:
            displayData = IndicatorLunar.astroBackend.LUNAR_PHASE_NAMES_TRANSLATIONS[ data ]

        if displayData is None:
            displayData = "" # Better to show nothing than let None slip through and crash.
            self.getLogging().error( "Unknown data tag: " + dataTag )

        return displayData


    # Converts a UTC date/time string to a local date/time string in the given format.
    def toLocalDateTimeString( self, utcDateTimeString, outputFormat ):
        utcDateTime = datetime.datetime.strptime( utcDateTimeString, IndicatorLunar.astroBackend.DATE_TIME_FORMAT_YYYYdashMMdashDDspaceHHcolonMMcolonSS )
        localDateTime = utcDateTime.replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None )
        return localDateTime.strftime( outputFormat )


    # https://stackoverflow.com/a/64097432/2156453
    # https://medium.com/@eleroy/10-things-you-need-to-know-about-date-and-time-in-python-with-datetime-pytz-dateutil-timedelta-309bfbafb3f7
    def convertStartHourAndEndHourToDateTimeInUTC( self, startHour, endHour ):
        startHourAsDateTimeInUTC = datetime.datetime.now().replace( hour = startHour ).astimezone( datetime.timezone.utc )
        endHourAsDateTimeInUTC = datetime.datetime.now().replace( hour = endHour ).astimezone( datetime.timezone.utc )
        if endHourAsDateTimeInUTC < startHourAsDateTimeInUTC:
            endHourAsDateTimeInUTC = endHourAsDateTimeInUTC + datetime.timedelta( days = 1 )

        return startHourAsDateTimeInUTC, endHourAsDateTimeInUTC


    # Creates the SVG icon text representing the moon given the illumination and bright limb angle.
    #
    #    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
    #
    #    brightLimbAngleInDegrees The angle of the bright limb, relative to zenith, ranging from 0 to 360 inclusive.
    #                             Ignored if illuminationPercentage is 0 or 100.
    def getSVGIconText( self, illuminationPercentage, brightLimbAngleInDegrees ):
        width = 100
        height = 100
        radius = float( width / 2 ) * 0.8 # Ensure the icon takes up most of the viewing area with a small boundary.
        colour = self.getThemeColour( defaultColour = "fff200" ) # Default to hicolor.

        if illuminationPercentage == 0 or illuminationPercentage == 100:
            body = '<circle cx="' + str( width / 2 ) + '" cy="' + str( height / 2 ) + '" r="' + str( radius )
            if illuminationPercentage == 0: # New
                body += '" fill="none" stroke="#' + colour + '" stroke-width="2" />'

            else: # Full
                body += '" fill="#' + colour + '" />'

        else:
            body = '<path d="M ' + str( width / 2 - radius ) + ' ' + str( height / 2 ) + ' ' + \
                   'A ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + \
                   str( width / 2 + radius ) + ' ' + str( height / 2 )

            if illuminationPercentage == 50: # Quarter
                body += ' Z"'

            elif illuminationPercentage < 50: # Crescent
                body += ' A ' + str( radius ) + ' ' + str( radius * ( 50 - illuminationPercentage ) / 50 ) + ' 0 0 0 ' + \
                        str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            else: # Gibbous
                body += ' A ' + str( radius ) + ' ' + str( radius * ( illuminationPercentage - 50 ) / 50 ) + ' 0 0 1 ' + \
                        str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            body += ' transform="rotate(' + str( -brightLimbAngleInDegrees ) + ' ' + \
                    str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="#' + colour + '" />'

        return '<?xml version="1.0" standalone="no"?>' \
               '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "https://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
               '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100">' + body + '</svg>'


    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

        PAGE_ICON = 0
        PAGE_MENU = 1
        PAGE_PLANETS_STARS = 2
        PAGE_COMETS_MINOR_PLANETS = 3
        PAGE_SATELLITES = 4
        PAGE_NOTIFICATIONS = 5
        PAGE_GENERAL = 6

        # Icon text.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Icon Text" ) ), False, False, 0 )

        indicatorText = Gtk.Entry()
        indicatorText.set_tooltip_text( _(
            "The text shown next to the indicator icon,\n" + \
            "or tooltip where applicable.\n\n" + \
            "The icon text can contain text and tags\n" + \
            "from the table below.\n\n" + \
            "To associate text with one or more tags,\n" + \
            "enclose the text and tag(s) within { }.\n\n" + \
            "For example\n\n" + \
            "\t{The sun will rise at [SUN RISE DATE TIME]}\n\n" + \
            "If any tag contains no data at render time,\n" + \
            "the tag will be removed.\n\n" + \
            "If a removed tag is within { }, the tag and\n" + \
            "text will be removed." ) )
        box.pack_start( indicatorText, True, True, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Separator" ) ), False, False, 0 )

        indicatorTextSeparator = Gtk.Entry()
        indicatorTextSeparator.set_text( self.indicatorTextSeparator )
        indicatorTextSeparator.set_tooltip_text( _( "The separator will be added between pairs of { }." ) )
        box.pack_start( indicatorTextSeparator, False, False, 0 )
        grid.attach( box, 0, 1, 1, 1 )

        # Table to show all attributes of selected/checked bodies.
        # If a body's magnitude passes through the magnitude filter,
        # all attributes (rise/set/az/alt) will be displayed in this table,
        # irrespective of the setting to hide bodies below the horizon. 
        COLUMN_TAG = 0
        COLUMN_TRANSLATED_TAG = 1
        COLUMN_VALUE = 2
        displayTagsStore = Gtk.ListStore( str, str, str ) # Tag, translated tag, value.
        self.initialiseDisplayTagsStore( displayTagsStore )

        indicatorText.set_text( self.translateTags( displayTagsStore, True, self.indicatorText ) ) # Translate tags into local language.

        displayTagsStoreSort = Gtk.TreeModelSort( model = displayTagsStore )
        displayTagsStoreSort.set_sort_column_id( COLUMN_TRANSLATED_TAG, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView.new_with_model( displayTagsStoreSort )
        tree.set_hexpand( True )
        tree.set_vexpand( True )

        treeViewColumn = Gtk.TreeViewColumn( _( "Tag" ), Gtk.CellRendererText(), text = COLUMN_TRANSLATED_TAG )
        treeViewColumn.set_sort_column_id( COLUMN_TRANSLATED_TAG )
        treeViewColumn.set_expand( True )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Value" ), Gtk.CellRendererText(), text = COLUMN_VALUE )
        treeViewColumn.set_sort_column_id( COLUMN_VALUE )
        treeViewColumn.set_expand( True )
        tree.append_column( treeViewColumn )

        tree.set_tooltip_text( _( "Double click to add a tag to the icon text." ) )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onTagDoubleClick, COLUMN_TRANSLATED_TAG, indicatorText )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 2, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Icon" ) ) )

        # Menu.
        grid = self.createGrid()

        showRiseWhenSetBeforeSunsetCheckbutton = Gtk.CheckButton.new_with_label( _( "Show rise when set is before sunset" ) )
        showRiseWhenSetBeforeSunsetCheckbutton.set_active( self.showRiseWhenSetBeforeSunset )
        showRiseWhenSetBeforeSunsetCheckbutton.set_tooltip_text( _(
            "If checked, all bodies below the horizon\n" + \
            "are hidden (excludes satellites)." ) )
#TODO Update tooltip        
        grid.attach( showRiseWhenSetBeforeSunsetCheckbutton, 0, 0, 1, 1 )

        hideBodiesBelowTheHorizonCheckbutton = Gtk.CheckButton.new_with_label( _( "Hide bodies below the horizon" ) )
        hideBodiesBelowTheHorizonCheckbutton.set_active( self.hideBodiesBelowHorizon )
        hideBodiesBelowTheHorizonCheckbutton.set_tooltip_text( _(
            "If checked, all bodies below the horizon\n" + \
            "are hidden (excludes satellites)." ) )
        grid.attach( hideBodiesBelowTheHorizonCheckbutton, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( 5 )
        box.set_margin_top( 5 )

        box.pack_start( Gtk.Label.new( _( "Hide bodies fainter than magnitude" ) ), False, False, 0 )
        toolTip = _( "Planets, stars, comets and minor planets\nwith a fainter magnitude will be hidden." )
        spinnerMagnitude = self.createSpinButton(
            self.magnitude, int( IndicatorLunar.astroBackend.MAGNITUDE_MINIMUM ), int( IndicatorLunar.astroBackend.MAGNITUDE_MAXIMUM ), 1, 5, toolTip )

        box.pack_start( spinnerMagnitude, False, False, 0 )
        grid.attach( box, 0, 2, 1, 1 )

        minorPlanetsAddNewCheckbutton = Gtk.CheckButton.new_with_label( _( "Add new minor planets" ) )
        minorPlanetsAddNewCheckbutton.set_margin_top( 5 )
        minorPlanetsAddNewCheckbutton.set_active( self.minorPlanetsAddNew )
        minorPlanetsAddNewCheckbutton.set_tooltip_text( _( "If checked, all minor planets are added." ) )
        grid.attach( minorPlanetsAddNewCheckbutton, 0, 3, 1, 1 )

        cometsAddNewCheckbutton = Gtk.CheckButton.new_with_label( _( "Add new comets" ) )
        cometsAddNewCheckbutton.set_margin_top( 5 )
        cometsAddNewCheckbutton.set_active( self.cometsAddNew )
        cometsAddNewCheckbutton.set_tooltip_text( _( "If checked, all comets are added." ) )
#TODO Comment out before release if comets unresolved.
        grid.attach( cometsAddNewCheckbutton, 0, 4, 1, 1 )

        satellitesAddNewCheckbox = Gtk.CheckButton.new_with_label( _( "Add new satellites" ) )
        satellitesAddNewCheckbox.set_margin_top( 5 )
        satellitesAddNewCheckbox.set_active( self.satellitesAddNew )
        satellitesAddNewCheckbox.set_tooltip_text( _( "If checked, all satellites are added." ) )
        grid.attach( satellitesAddNewCheckbox, 0, 5, 1, 1 )

        sortSatellitesByDateTimeCheckbutton = Gtk.CheckButton.new_with_label( _( "Sort satellites by rise date/time" ) )
        sortSatellitesByDateTimeCheckbutton.set_margin_top( 5 )
        sortSatellitesByDateTimeCheckbutton.set_active( self.satellitesSortByDateTime )
        sortSatellitesByDateTimeCheckbutton.set_tooltip_text( _(
            "If checked, satellites are sorted\n" + \
            "by rise date/time.\n\n" + \
            "Otherwise satellites are sorted\n" + \
            "by Name then Number." ) )
        grid.attach( sortSatellitesByDateTimeCheckbutton, 0, 6, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 5 )
        box.set_margin_left( 5 )

        box.pack_start( Gtk.Label.new( _( "Show satellites passes from" ) ), False, False, 0 )

        spinnerSatelliteLimitStart = self.createSpinButton( self.satelliteLimitStart, 0, 23, 1, 4, _( "Show satellite passes after this hour (inclusive)" ) )
        box.pack_start( spinnerSatelliteLimitStart, False, False, 0 )

        box.pack_start( Gtk.Label.new( _( "to" ) ), False, False, 0 )

        spinnerSatelliteLimitEnd = self.createSpinButton( self.satelliteLimitEnd, 0, 23, 1, 4, _( "Show satellite passes before this hour (inclusive)" ) )
        box.pack_start( spinnerSatelliteLimitEnd, False, False, 0 )

        grid.attach( box, 0, 7, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )

        # Planets / minor planets / comets / stars.
        box = Gtk.Box( spacing = 20 )

        PLANET_STORE_INDEX_HIDE_SHOW = 0
        PLANET_STORE_INDEX_NAME = 1
        PLANET_STORE_INDEX_TRANSLATED_NAME = 2
        planetStore = Gtk.ListStore( bool, str, str ) # Show/hide, planet name (not displayed), translated planet name.
        for planetName in IndicatorLunar.astroBackend.PLANETS:
            planetStore.append( [ planetName in self.planets, planetName, IndicatorLunar.astroBackend.PLANET_NAMES_TRANSLATIONS[ planetName ] ] )

        toolTipText = _( "Check a planet to display in the menu." ) + "\n\n" + \
                      _( "Clicking the header of the first column\n" + \
                         "will toggle all checkboxes." )

        box.pack_start( self.createTreeView( planetStore, toolTipText, _( "Planets" ), PLANET_STORE_INDEX_TRANSLATED_NAME ), True, True, 0 )

        MINOR_PLANET_STORE_INDEX_HIDE_SHOW = 0
        MINOR_PLANET_STORE_INDEX_NAME = 1
        MINOR_PLANET_STORE_INDEX_HUMAN_READABLE_NAME = 2
        minorPlanetStore = Gtk.ListStore( bool, str, str ) # Show/hide, minor planet name, human readable name.
        dataType = OE.DataType.XEPHEM_MINOR_PLANET \
            if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendPyEphem else OE.DataType.SKYFIELD_MINOR_PLANET
        for minorPlanet in sorted( self.minorPlanetOrbitalElementData.keys() ):
            minorPlanetStore.append( [ minorPlanet in self.minorPlanets, minorPlanet, self.minorPlanetOrbitalElementData[ minorPlanet ].getName() ] )

        if self.minorPlanetOrbitalElementData:
            toolTipText = _( "Check a minor planet to display in the menu." ) + "\n\n" + \
                          _( "Clicking the header of the first column\n" + \
                             "will toggle all checkboxes." )

        else:
            toolTipText = _(
                "Minor planet data is unavailable;\n" + \
                "the source could not be reached,\n" + \
                "or no data was available, or the data\n" + \
                "was completely filtered by magnitude." )

        box.pack_start( self.createTreeView( minorPlanetStore, toolTipText, _( "Minor Planets" ), MINOR_PLANET_STORE_INDEX_HUMAN_READABLE_NAME ), True, True, 0 )

        COMET_STORE_INDEX_HIDE_SHOW = 0
        COMET_STORE_INDEX_NAME = 1
        COMET_STORE_INDEX_HUMAN_READABLE_NAME = 2
        cometStore = Gtk.ListStore( bool, str, str ) # Show/hide, comet name, human readable name.
        dataType = OE.DataType.XEPHEM_COMET \
            if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendPyEphem else OE.DataType.SKYFIELD_COMET
        for comet in sorted( self.cometOrbitalElementData.keys() ):
            cometStore.append( [ comet in self.comets, comet, self.cometOrbitalElementData[ comet ].getName() ] )

        if self.cometOrbitalElementData:
            toolTipText = _( "Check a comet to display in the menu." ) + "\n\n" + \
                          _( "Clicking the header of the first column\n" + \
                             "will toggle all checkboxes." )

        else:
            toolTipText = _(
                "Comet data is unavailable; the source\n" + \
                "could not be reached, or no data was\n" + \
                "available from the source, or the data\n" + \
                "was completely filtered by magnitude." )

#TODO Comment out before release if comets unresolved.
        box.pack_start( self.createTreeView( cometStore, toolTipText, _( "Comets" ), COMET_STORE_INDEX_HUMAN_READABLE_NAME ), True, True, 0 )

        stars = [ ] # List of lists, each sublist containing star is checked flag, star name, star translated name.
        for starName in IndicatorLunar.astroBackend.getStarNames():
            stars.append( [ starName in self.stars, starName, IndicatorLunar.astroBackend.getStarNameTranslation( starName ) ] )

        STAR_STORE_INDEX_HIDE_SHOW = 0
        STAR_STORE_INDEX_NAME = 1
        STAR_STORE_INDEX_TRANSLATED_NAME = 2
        starStore = Gtk.ListStore( bool, str, str ) # Show/hide, star name (not displayed), star translated name.
        for star in sorted( stars, key = lambda x: ( x[ 2 ] ) ): # Sort by translated star name.
            starStore.append( star )

        toolTipText = _( "Check a star to display in the menu." ) + "\n\n" + \
                      _( "Clicking the header of the first column\n" + \
                         "will toggle all checkboxes." )

        box.pack_start( self.createTreeView( starStore, toolTipText, _( "Stars" ), STAR_STORE_INDEX_TRANSLATED_NAME ), True, True, 0 )

        notebook.append_page( box, Gtk.Label.new( _( "Natural Bodies" ) ) )

        # Satellites.
        box = Gtk.Box()

        SATELLITE_STORE_INDEX_HIDE_SHOW = 0
        SATELLITE_STORE_INDEX_NAME = 1
        SATELLITE_STORE_INDEX_NUMBER = 2
        SATELLITE_STORE_INDEX_INTERNATIONAL_DESIGNATOR = 3
        satelliteStore = Gtk.ListStore( bool, str, str, str ) # Show/hide, name, number, international designator.
        for satellite in self.satelliteGeneralPerturbationData:
            satelliteStore.append( [ satellite in self.satellites,
                                     self.satelliteGeneralPerturbationData[ satellite ].getName(),
                                     satellite, self.satelliteGeneralPerturbationData[ satellite ].getInternationalDesignator() ] )

        satelliteStoreSort = Gtk.TreeModelSort( model = satelliteStore )
        satelliteStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView.new_with_model( satelliteStoreSort )
        tree.set_hexpand( True )
        tree.set_vexpand( True )
        if self.satelliteGeneralPerturbationData:
            tree.set_tooltip_text( _( "Check a satellite to display in the menu." ) + "\n\n" + \
                                   _( "Clicking the header of the first column\n" + \
                                      "will toggle all checkboxes." ) )

        else:
            tree.set_tooltip_text( _(
                "Satellite data is unavailable;\n" + \
                "the source could not be reached,\n" + \
                "or data was available." ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onSatelliteCheckbox, satelliteStore, satelliteStoreSort )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = SATELLITE_STORE_INDEX_HIDE_SHOW )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, satelliteStore )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = SATELLITE_STORE_INDEX_NAME )
        treeViewColumn.set_sort_column_id( 1 )
        treeViewColumn.set_expand( True )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Number" ), Gtk.CellRendererText(), text = SATELLITE_STORE_INDEX_NUMBER )
        treeViewColumn.set_sort_column_id( 2 )
        treeViewColumn.set_expand( True )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "International Designator" ), Gtk.CellRendererText(), text = SATELLITE_STORE_INDEX_INTERNATIONAL_DESIGNATOR )
        treeViewColumn.set_sort_column_id( 3 )
        treeViewColumn.set_expand( True )
        tree.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )
        box.pack_start( scrolledWindow, True, True, 0 )

        notebook.append_page( box, Gtk.Label.new( _( "Satellites" ) ) )

        # Notifications (satellite and full moon).
        notifyOSDInformation = _( "For formatting, refer to https://wiki.ubuntu.com/NotifyOSD" )

        grid = self.createGrid()

        satelliteTagTranslations = self.listOfListsToListStore( IndicatorLunar.astroBackend.SATELLITE_TAG_TRANSLATIONS )
        messageText = self.translateTags( satelliteTagTranslations, True, self.satelliteNotificationMessage )
        summaryText = self.translateTags( satelliteTagTranslations, True, self.satelliteNotificationSummary )
        toolTipCommon = IndicatorLunar.astroBackend.SATELLITE_TAG_NAME_TRANSLATION + "\n\t" + \
                        IndicatorLunar.astroBackend.SATELLITE_TAG_NUMBER_TRANSLATION + "\n\t" + \
                        IndicatorLunar.astroBackend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n\t" + \
                        IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\t" + \
                        IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n\t" + \
                        IndicatorLunar.astroBackend.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION + "\n\t" + \
                        IndicatorLunar.astroBackend.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n\t" + \
                        _( notifyOSDInformation )
        summaryTooltip = _( "The summary for the satellite rise notification.\n\n" +  "Available tags:\n\t" ) + toolTipCommon
        messageTooltip = _( "The message for the satellite rise notification.\n\n" + "Available tags:\n\t" ) + toolTipCommon

        # Additional lines are added to the message to ensure the textview for the message text is not too small.
        showSatelliteNotificationCheckbox, satelliteNotificationSummaryText, satelliteNotificationMessageText = \
            self.createNotificationPanel( grid, 0,
                                          _( "Satellite rise" ), _( "Screen notification when a satellite rises above the horizon." ), self.showSatelliteNotification,
                                          _( "Summary" ), summaryText, summaryTooltip,
                                          _( "Message" ) + "\n \n \n \n ", messageText, messageTooltip,
                                          _( "Test" ), _( "Show the notification using the current summary/message." ),
                                          False )

        # Additional lines are added to the message to ensure the textview for the message text is not too small.
        showWerewolfWarningCheckbox, werewolfNotificationSummaryText, werewolfNotificationMessageText = \
            self.createNotificationPanel( grid, 4,
                                          _( "Werewolf warning" ), _( "Hourly screen notification leading up to full moon." ), self.showWerewolfWarning,
                                          _( "Summary" ), self.werewolfWarningSummary, _( "Hourly screen notification leading up to full moon." ),
                                          _( "Message" ) + "\n \n ", self.werewolfWarningMessage, _( "The message for the werewolf notification.\n\n" ) + notifyOSDInformation,
                                          _( "Test" ), _( "Show the notification using the current summary/message." ),
                                          True )

        showWerewolfWarningCheckbox.set_margin_top( 10 )

        notebook.append_page( grid, Gtk.Label.new( _( "Notifications" ) ) )

        # Location.
        grid = self.createGrid()

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 5 )

        box.pack_start( Gtk.Label.new( _( "City" ) ), False, False, 0 )

        city = Gtk.ComboBoxText.new_with_entry()
        city.set_tooltip_text( _(
            "Choose a city from the list.\n" + \
            "Or, add in your own city name." ) )

        cities = IndicatorLunar.astroBackend.getCities()
        if self.city not in cities:
            cities.append( self.city )
            cities = sorted( cities, key = locale.strxfrm )

        for c in cities:
            city.append_text( c )

        box.pack_start( city, False, False, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 5 )

        box.pack_start( Gtk.Label.new( _( "Latitude" ) ), False, False, 0 )

        latitude = Gtk.Entry()
        latitude.set_tooltip_text( _( "Latitude of your location in decimal degrees." ) )
        box.pack_start( latitude, False, False, 0 )
        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 5 )

        box.pack_start( Gtk.Label.new( _( "Longitude" ) ), False, False, 0 )

        longitude = Gtk.Entry()
        longitude.set_tooltip_text( _( "Longitude of your location in decimal degrees." ) )
        box.pack_start( longitude, False, False, 0 )
        grid.attach( box, 0, 2, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 5 )

        box.pack_start( Gtk.Label.new( _( "Elevation" ) ), False, False, 0 )

        elevation = Gtk.Entry()
        elevation.set_tooltip_text( _( "Height in metres above sea level." ) )
        box.pack_start( elevation, False, False, 0 )
        grid.attach( box, 0, 3, 1, 1 )

        city.connect( "changed", self.onCityChanged, latitude, longitude, elevation )
        city.set_active( cities.index( self.city ) )

        latitude.set_text( str( self.latitude ) )
        longitude.set_text( str( self.longitude ) )
        elevation.set_text( str( self.elevation ) )

        notebook.append_page( grid, Gtk.Label.new( _( "Location" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        while True:
            responseType = dialog.run()
            if responseType != Gtk.ResponseType.OK:
                break

            cityValue = city.get_active_text()
            if cityValue == "":
                notebook.set_current_page( PAGE_GENERAL )
                self.showMessage( dialog, _( "City cannot be empty." ) )
                city.grab_focus()
                continue

            latitudeValue = latitude.get_text().strip()
            if latitudeValue == "" or not self.isNumber( latitudeValue ) or float( latitudeValue ) > 90 or float( latitudeValue ) < -90:
                notebook.set_current_page( PAGE_GENERAL )
                self.showMessage( dialog, _( "Latitude must be a number between 90 and -90 inclusive." ) )
                latitude.grab_focus()
                continue

            longitudeValue = longitude.get_text().strip()
            if longitudeValue == "" or not self.isNumber( longitudeValue ) or float( longitudeValue ) > 180 or float( longitudeValue ) < -180:
                notebook.set_current_page( PAGE_GENERAL )
                self.showMessage( dialog, _( "Longitude must be a number between 180 and -180 inclusive." ) )
                longitude.grab_focus()
                continue

            elevationValue = elevation.get_text().strip()
            if elevationValue == "" or not self.isNumber( elevationValue ) or float( elevationValue ) > 10000 or float( elevationValue ) < 0:
                notebook.set_current_page( PAGE_GENERAL )
                self.showMessage( dialog, _( "Elevation must be a number between 0 and 10000 inclusive." ) )
                elevation.grab_focus()
                continue

            if spinnerSatelliteLimitStart.get_value_as_int() >= spinnerSatelliteLimitEnd.get_value_as_int():
                notebook.set_current_page( PAGE_MENU )
                self.showMessage( dialog, _( "The start hour for satellite passes must be lower than the end hour." ) )
                spinnerSatelliteLimitStart.grab_focus()
                continue

            self.indicatorText = self.translateTags( displayTagsStore, False, indicatorText.get_text() )
            self.indicatorTextSeparator = indicatorTextSeparator.get_text()
            self.showRiseWhenSetBeforeSunset = showRiseWhenSetBeforeSunsetCheckbutton.get_active()
            self.hideBodiesBelowHorizon = hideBodiesBelowTheHorizonCheckbutton.get_active()
            self.magnitude = spinnerMagnitude.get_value_as_int()
            self.cometsAddNew = cometsAddNewCheckbutton.get_active() # The update will add in new comets.
            self.minorPlanetsAddNew = minorPlanetsAddNewCheckbutton.get_active() # The update will add in new minor planets.
            self.satellitesSortByDateTime = sortSatellitesByDateTimeCheckbutton.get_active()
            self.satellitesAddNew = satellitesAddNewCheckbox.get_active() # The update will add in new satellites.

            # If the user changes the visibility window for satellites,
            # the previous set of transits may no longer match the new window.
            # One solution is to attempt to filter out those transits which do not match.
            # A simpler solution is to erase the previous transits.
            if self.satelliteLimitStart != spinnerSatelliteLimitStart.get_value_as_int() or \
               self.satelliteLimitEnd != spinnerSatelliteLimitEnd.get_value_as_int():
                self.dataPrevious = None

            self.satelliteLimitStart = spinnerSatelliteLimitStart.get_value_as_int()
            self.satelliteLimitEnd = spinnerSatelliteLimitEnd.get_value_as_int()

            self.planets = [ ]
            for row in planetStore:
                if row[ PLANET_STORE_INDEX_HIDE_SHOW ]:
                    self.planets.append( row[ PLANET_STORE_INDEX_NAME ] )

            self.stars = [ ]
            for row in starStore:
                if row[ STAR_STORE_INDEX_HIDE_SHOW ]:
                    self.stars.append( row[ STAR_STORE_INDEX_NAME ] )

            # If the option to add new comets is checked, this will be handled out in the main update loop.
            # Otherwise, update the list of checked comets (ditto for minor planets and satellites).
            self.comets = [ ]
            if not self.cometsAddNew:
                for comet in cometStore:
                    if comet[ COMET_STORE_INDEX_HIDE_SHOW ]:
                        self.comets.append( comet[ COMET_STORE_INDEX_NAME ] )

            self.minorPlanets = [ ]
            if not self.minorPlanetsAddNew:
                for minorPlanet in minorPlanetStore:
                    if minorPlanet[ MINOR_PLANET_STORE_INDEX_HIDE_SHOW ]:
                        self.minorPlanets.append( minorPlanet[ MINOR_PLANET_STORE_INDEX_NAME ] )

            self.satellites = [ ]
            if not self.satellitesAddNew:
                for satellite in satelliteStore:
                    if satellite[ SATELLITE_STORE_INDEX_HIDE_SHOW ]:
                        self.satellites.append( satellite[ SATELLITE_STORE_INDEX_NUMBER ] )

            self.showSatelliteNotification = showSatelliteNotificationCheckbox.get_active()
            if not showSatelliteNotificationCheckbox.get_active(): self.satellitePreviousNotifications = { }
            self.satelliteNotificationSummary = self.translateTags( satelliteTagTranslations, False, satelliteNotificationSummaryText.get_text() )
            self.satelliteNotificationMessage = self.translateTags( satelliteTagTranslations, False, self.getTextViewText( satelliteNotificationMessageText ) )

            self.showWerewolfWarning = showWerewolfWarningCheckbox.get_active()
            self.werewolfWarningSummary = werewolfNotificationSummaryText.get_text()
            self.werewolfWarningMessage = self.getTextViewText( werewolfNotificationMessageText )

            self.city = cityValue
            self.latitude = float( latitudeValue )
            self.longitude = float( longitudeValue )
            self.elevation = float( elevationValue )

            break

        return responseType


    def initialiseDisplayTagsStore( self, displayTagsStore ):
        items = [ [ IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON, IndicatorLunar.astroBackend.DATA_TAGS_MOON ],
                  [ IndicatorLunar.astroBackend.BodyType.SUN, IndicatorLunar.astroBackend.NAME_TAG_SUN, IndicatorLunar.astroBackend.DATA_TAGS_SUN ] ]

        for item in items:
            bodyType = item[ IndicatorLunar.DATA_INDEX_BODY_TYPE ]
            bodyTag = item[ IndicatorLunar.DATA_INDEX_BODY_NAME ]
            dataTags = item[ IndicatorLunar.DATA_INDEX_DATA_NAME ]
            if ( bodyType, bodyTag, IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                for dataTag in dataTags:
                    translatedTag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ bodyTag ] + " " + IndicatorLunar.astroBackend.DATA_TAGS_TRANSLATIONS[ dataTag ]
                    value = ""
                    key = ( bodyType, bodyTag, dataTag )
                    if key in self.data:
                        value = self.formatData( dataTag, self.data[ key ] )
                        displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, value ] )

        items = [ [ IndicatorLunar.astroBackend.BodyType.PLANET, IndicatorLunar.astroBackend.PLANETS, IndicatorLunar.astroBackend.DATA_TAGS_PLANET ],
                  [ IndicatorLunar.astroBackend.BodyType.STAR, IndicatorLunar.astroBackend.getStarNames(), IndicatorLunar.astroBackend.DATA_TAGS_STAR ] ]

        for item in items:
            bodyType = item[ IndicatorLunar.DATA_INDEX_BODY_TYPE ]
            bodyTags = item[ IndicatorLunar.DATA_INDEX_BODY_NAME ]
            dataTags = item[ IndicatorLunar.DATA_INDEX_DATA_NAME ]
            for bodyTag in bodyTags:
                if ( bodyType, bodyTag, IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                    for dataTag in dataTags:
                        translatedTag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ bodyTag ] + " " + IndicatorLunar.astroBackend.DATA_TAGS_TRANSLATIONS[ dataTag ]
                        value = ""
                        key = ( bodyType, bodyTag, dataTag )
                        if key in self.data:
                            value = self.formatData( dataTag, self.data[ key ] )
                            displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, value ] )

        items = [ [ IndicatorLunar.astroBackend.BodyType.COMET, self.cometOrbitalElementData, IndicatorLunar.astroBackend.DATA_TAGS_COMET ],
                  [ IndicatorLunar.astroBackend.BodyType.MINOR_PLANET, self.minorPlanetOrbitalElementData, IndicatorLunar.astroBackend.DATA_TAGS_MINOR_PLANET ] ]

        for item in items:
            bodyType = item[ IndicatorLunar.DATA_INDEX_BODY_TYPE ]
            bodyTags = item[ IndicatorLunar.DATA_INDEX_BODY_NAME ]
            dataTags = item[ IndicatorLunar.DATA_INDEX_DATA_NAME ]
            for bodyTag in bodyTags:
                if ( bodyType, bodyTag, IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                    for dataTag in dataTags:
                        translatedTag = bodyTag + " " + IndicatorLunar.astroBackend.DATA_TAGS_TRANSLATIONS[ dataTag ]
                        value = ""
                        key = ( bodyType, bodyTag, dataTag )
                        if key in self.data:
                            value = self.formatData( dataTag, self.data[ key ] )
                            displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, value ] )

        bodyType = IndicatorLunar.astroBackend.BodyType.SATELLITE
        for bodyTag in self.satelliteGeneralPerturbationData:
            # Add this body's attributes ONLY if data is present.
            riseIsPresent = \
                ( bodyType, bodyTag, IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH ) in self.data or \
                ( bodyType, bodyTag, IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH ) in self.data

            if riseIsPresent:
                for dataTag in IndicatorLunar.astroBackend.DATA_TAGS_SATELLITE:
                    value = ""
                    name = self.satelliteGeneralPerturbationData[ bodyTag ].getName()
                    internationalDesignator = self.satelliteGeneralPerturbationData[ bodyTag ].getInternationalDesignator()
                    translatedTag = name + " : " + bodyTag + " : " + internationalDesignator + " " + IndicatorLunar.astroBackend.DATA_TAGS_TRANSLATIONS[ dataTag ]
                    key = ( IndicatorLunar.astroBackend.BodyType.SATELLITE, bodyTag, dataTag )
                    if key in self.data:
                        value = self.formatData( dataTag, self.data[ key ] )
                        displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, value ] )


    def translateTags( self, tagsListStore, originalToLocal, text ):
        # The tags list store contains at least 2 columns; additional columns may exist,
        # depending on the tags list store provided by the caller, but are ignored.
        # First column contains the original/untranslated tags.
        # Second column contains the translated tags.
        if originalToLocal:
            i = 0
            j = 1

        else:
            i = 1
            j = 0

        translatedText = text
        tags = re.findall( "\[([^\[^\]]+)\]", translatedText )
        for tag in tags:
            iterator = tagsListStore.get_iter_first()
            while iterator:
                row = tagsListStore[ iterator ]
                if row[ i ] == tag:
                    translatedText = translatedText.replace( "[" + tag + "]", "[" + row[ j ] + "]" )
                    iterator = None # Break and move on to next tag.

                else:
                    iterator = tagsListStore.iter_next( iterator )

        return translatedText


    def onTagDoubleClick( self, tree, rowNumber, treeViewColumn, translatedTagColumnIndex, indicatorTextEntry ):
        model, treeiter = tree.get_selection().get_selected()
        indicatorTextEntry.insert_text( "[" + model[ treeiter ][ translatedTagColumnIndex ] + "]", indicatorTextEntry.get_position() )


    def createTreeView( self, listStore, toolTipText, columnHeaderText, columnIndex ):

        COLUMN_INDEX_TOGGLE = 0
        COLUMN_INDEX_DATA = 1

        def toggleCheckbox( cellRendererToggle, row, listStore ):
            listStore[ row ][ COLUMN_INDEX_TOGGLE ] = not listStore[ row ][ COLUMN_INDEX_TOGGLE ]


        tree = Gtk.TreeView.new_with_model( listStore )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( toolTipText )
        tree.set_hexpand( True )
        tree.set_vexpand( True )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", toggleCheckbox, listStore )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = COLUMN_INDEX_TOGGLE )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, listStore )
        tree.append_column( treeViewColumn )

        tree.append_column( Gtk.TreeViewColumn( columnHeaderText, Gtk.CellRendererText(), text = columnIndex ) )
        tree.get_column( COLUMN_INDEX_DATA ).set_expand( True )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        return scrolledWindow


    def onSatelliteCheckbox( self, cellRendererToggle, row, dataStore, sortStore ):
        actualRow = sortStore.convert_path_to_child_path( Gtk.TreePath.new_from_string( row ) ) # Convert sorted model index to underlying (child) model index.
        COLUMN_INDEX_TOGGLE = 0
        dataStore[ actualRow ][ COLUMN_INDEX_TOGGLE ] = not dataStore[ actualRow ][ COLUMN_INDEX_TOGGLE ]


    def onColumnHeaderClick( self, treeviewColumn, dataStore ):
        COLUMN_INDEX_TOGGLE = 0
        atLeastOneItemChecked = False
        atLeastOneItemUnchecked = False
        for row in range( len( dataStore ) ):
            if dataStore[ row ][ COLUMN_INDEX_TOGGLE ]:
                atLeastOneItemChecked = True

            if not dataStore[ row ][ COLUMN_INDEX_TOGGLE ]:
                atLeastOneItemUnchecked = True

        if atLeastOneItemChecked and atLeastOneItemUnchecked: # Mix of values checked and unchecked, so check all.
            value = True

        elif atLeastOneItemChecked: # No items checked (so all are unchecked), so check all.
            value = False

        else: # No items unchecked (so all are checked), so uncheck all.
            value = True

        for row in range( len( dataStore ) ):
            dataStore[ row ][ 0 ] = value


    def createNotificationPanel(
            self,
            grid, gridStartIndex,
            checkboxLabel, checkboxTooltip, checkboxIsActive,
            summaryLabel, summaryText, summaryTooltip,
            messageLabel, messageText, messageTooltip,
            testButtonText, testButtonTooltip,
            isMoonNotification ):

        checkbutton = Gtk.CheckButton.new_with_label( checkboxLabel )
        checkbutton.set_active( checkboxIsActive )
        checkbutton.set_tooltip_text( checkboxTooltip )
        grid.attach( checkbutton, 0, gridStartIndex, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_TEXT_LEFT )

        label = Gtk.Label.new( summaryLabel )
        box.pack_start( label, False, False, 0 )

        summaryTextEntry = Gtk.Entry()
        summaryTextEntry.set_text( summaryText )
        summaryTextEntry.set_tooltip_text( summaryTooltip )
        box.pack_start( summaryTextEntry, True, True, 0 )
        box.set_sensitive( checkbutton.get_active() )
        grid.attach( box, 0, gridStartIndex + 1, 1, 1 )

        checkbutton.connect( "toggled", self.onRadioOrCheckbox, True, box )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_TEXT_LEFT )

        label = Gtk.Label.new( messageLabel )
        label.set_valign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        messageTextView = Gtk.TextView()
        messageTextView.get_buffer().set_text( messageText )
        messageTextView.set_tooltip_text( messageTooltip )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( messageTextView )
        box.pack_start( scrolledWindow, True, True, 0 )
        box.set_sensitive( checkbutton.get_active() )
        grid.attach( box, 0, gridStartIndex + 2, 1, 1 )

        checkbutton.connect( "toggled", self.onRadioOrCheckbox, True, box )

        test = Gtk.Button.new_with_label( testButtonText )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( checkbutton.get_active() )
        test.connect( "clicked", self.onTestNotificationClicked, summaryTextEntry, messageTextView, isMoonNotification )
        test.set_tooltip_text( testButtonTooltip )
        grid.attach( test, 0, gridStartIndex + 3, 1, 1 )

        checkbutton.connect( "toggled", self.onRadioOrCheckbox, True, test )

        return checkbutton, summaryTextEntry, messageTextView


    def onTestNotificationClicked( self, button, summaryEntry, messageTextView, isMoonNotification ):
        summary = summaryEntry.get_text()
        message = self.getTextViewText( messageTextView )

        if isMoonNotification:
            Notify.Notification.new( summary, message, self.createFullMoonIcon() ).show()

        else:
            # Create mock data.
            utcNow = str( datetime.datetime.utcnow() )
            if utcNow.index( '.' ) > -1:
                utcNow = utcNow.split( '.' )[ 0 ] # Remove fractional seconds.

            utcNowPlusTenMinutes = str( datetime.datetime.utcnow() + datetime.timedelta( minutes = 10 ) )
            if utcNowPlusTenMinutes.index( '.' ) > -1:
                utcNowPlusTenMinutes = utcNowPlusTenMinutes.split( '.' )[ 0 ] # Remove fractional seconds.

            def replaceTags( text ):
                return \
                    text. \
                    replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NAME_TRANSLATION, "ISS (ZARYA)" ). \
                    replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NUMBER_TRANSLATION, "25544" ). \
                    replace( IndicatorLunar.astroBackend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION, "1998-067A" ). \
                    replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION, "123°" ). \
                    replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.toLocalDateTimeString( utcNow, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) ). \
                    replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                    replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_TIME_TRANSLATION, self.toLocalDateTimeString( utcNowPlusTenMinutes, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) )

            summary = replaceTags( summary ) + " " # The notification summary text must not be empty (at least on Unity).
            message = replaceTags( message )
            Notify.Notification.new( summary, message, IndicatorLunar.ICON_SATELLITE ).show()


    def onCityChanged( self, combobox, latitude, longitude, elevation ):
        city = combobox.get_active_text()
        if city in IndicatorLunar.astroBackend.getCities():
            theLatitude, theLongitude, theElevation = IndicatorLunar.astroBackend.getLatitudeLongitudeElevation( city )
            latitude.set_text( str( theLatitude ) )
            longitude.set_text( str( theLongitude ) )
            elevation.set_text( str( theElevation ) )


    def getDefaultCity( self ):
        try:
            timezone = self.processGet( "cat /etc/timezone" )
            theCity = None
            cities = IndicatorLunar.astroBackend.getCities()
            for city in cities:
                if city in timezone:
                    theCity = city
                    break

            if theCity is None or not theCity:
                theCity = cities[ 0 ] # No city found, so choose first city by default.

        except Exception as e:
            self.getLogging().exception( e )
            self.getLogging().error( "Error getting default city." )
            theCity = cities[ 0 ] # Some error occurred, so choose first city by default.

        return theCity


    def __useNewCityNameConfigVersion93( self, config ):
        if self.city is None:
            self.city = config.get( "city" )
            self.requestSaveConfig( delay = 5 )


    def __dropPlutoVersion93( self ):
        if "PLUTO" in self.planets:
            self.planets.remove( "PLUTO" )
            self.requestSaveConfig( delay = 5 )


    def __dropOldStarsVersion96( self ):
        stars = [ ]
        for star in self.stars:
            if star in IndicatorLunar.astroBackend.getStarNames():
                stars.append( star )

        if len( self.stars ) > len( stars ):
            self.stars = stars
            self.requestSaveConfig( delay = 5 )


    def loadConfig( self, config ):
        self.city = config.get( IndicatorLunar.CONFIG_CITY_NAME ) # Returns None if the key is not found.
        self.__useNewCityNameConfigVersion93( config )
        if self.city is None:
            self.city = self.getDefaultCity()
            self.latitude, self.longitude, self.elevation = IndicatorLunar.astroBackend.getLatitudeLongitudeElevation( self.city )

        else:
            self.elevation = config.get( IndicatorLunar.CONFIG_CITY_ELEVATION )
            self.latitude = config.get( IndicatorLunar.CONFIG_CITY_LATITUDE )
            self.longitude = config.get( IndicatorLunar.CONFIG_CITY_LONGITUDE )

        self.comets = config.get( IndicatorLunar.CONFIG_COMETS, [ ] )
        self.cometsAddNew = config.get( IndicatorLunar.CONFIG_COMETS_ADD_NEW, False )

        self.hideBodiesBelowHorizon = config.get( IndicatorLunar.CONFIG_HIDE_BODIES_BELOW_HORIZON, False )

        self.indicatorText = config.get( IndicatorLunar.CONFIG_INDICATOR_TEXT, IndicatorLunar.INDICATOR_TEXT_DEFAULT )
        self.indicatorTextSeparator = config.get( IndicatorLunar.CONFIG_INDICATOR_TEXT_SEPARATOR, IndicatorLunar.INDICATOR_TEXT_SEPARATOR_DEFAULT )

        self.minorPlanets = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS, [ ] )
        self.minorPlanetsAddNew = config.get( IndicatorLunar.CONFIG_MINOR_PLANETS_ADD_NEW, False )

        self.magnitude = config.get( IndicatorLunar.CONFIG_MAGNITUDE, 3 ) # Although a value of 6 is visible with the naked eye, that gives too many minor planets initially.

        self.planets = config.get( IndicatorLunar.CONFIG_PLANETS, IndicatorLunar.astroBackend.PLANETS )
        self.__dropPlutoVersion93()

        self.satelliteLimitStart = config.get( IndicatorLunar.CONFIG_SATELLITE_LIMIT_START, 16 ) # 4pm
        self.satelliteLimitEnd = config.get( IndicatorLunar.CONFIG_SATELLITE_LIMIT_END, 22 ) # 10pm
        self.satelliteNotificationMessage = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE, IndicatorLunar.SATELLITE_NOTIFICATION_MESSAGE_DEFAULT )
        self.satelliteNotificationSummary = config.get( IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY, IndicatorLunar.SATELLITE_NOTIFICATION_SUMMARY_DEFAULT )
        self.satellites = config.get( IndicatorLunar.CONFIG_SATELLITES, [ ] )
        self.satellitesAddNew = config.get( IndicatorLunar.CONFIG_SATELLITES_ADD_NEW, False )
        self.satellitesSortByDateTime = config.get( IndicatorLunar.CONFIG_SATELLITES_SORT_BY_DATE_TIME, True )

        self.showRiseWhenSetBeforeSunset = config.get( IndicatorLunar.CONFIG_SHOW_RISE_WHEN_SET_BEFORE_SUNSET, False )
        self.showSatelliteNotification = config.get( IndicatorLunar.CONFIG_SHOW_SATELLITE_NOTIFICATION, False )
        self.showWerewolfWarning = config.get( IndicatorLunar.CONFIG_SHOW_WEREWOLF_WARNING, True )

        self.stars = config.get( IndicatorLunar.CONFIG_STARS, [ ] )
        self.__dropOldStarsVersion96()

        self.werewolfWarningMessage = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE, IndicatorLunar.WEREWOLF_WARNING_MESSAGE_DEFAULT )
        self.werewolfWarningSummary = config.get( IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY, IndicatorLunar.WEREWOLF_WARNING_SUMMARY_DEFAULT )


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
            IndicatorLunar.CONFIG_CITY_ELEVATION : self.elevation,
            IndicatorLunar.CONFIG_CITY_LATITUDE : self.latitude,
            IndicatorLunar.CONFIG_CITY_LONGITUDE : self.longitude,
            IndicatorLunar.CONFIG_CITY_NAME : self.city,
            IndicatorLunar.CONFIG_COMETS : comets,
            IndicatorLunar.CONFIG_COMETS_ADD_NEW : self.cometsAddNew,
            IndicatorLunar.CONFIG_HIDE_BODIES_BELOW_HORIZON : self.hideBodiesBelowHorizon,
            IndicatorLunar.CONFIG_INDICATOR_TEXT : self.indicatorText,
            IndicatorLunar.CONFIG_INDICATOR_TEXT_SEPARATOR : self.indicatorTextSeparator,
            IndicatorLunar.CONFIG_MINOR_PLANETS : minorPlanets,
            IndicatorLunar.CONFIG_MINOR_PLANETS_ADD_NEW : self.minorPlanetsAddNew,
            IndicatorLunar.CONFIG_MAGNITUDE : self.magnitude,
            IndicatorLunar.CONFIG_PLANETS : self.planets,
            IndicatorLunar.CONFIG_SATELLITE_LIMIT_START : self.satelliteLimitStart,
            IndicatorLunar.CONFIG_SATELLITE_LIMIT_END : self.satelliteLimitEnd,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_MESSAGE : self.satelliteNotificationMessage,
            IndicatorLunar.CONFIG_SATELLITE_NOTIFICATION_SUMMARY : self.satelliteNotificationSummary,
            IndicatorLunar.CONFIG_SATELLITES : satellites,
            IndicatorLunar.CONFIG_SATELLITES_ADD_NEW : self.satellitesAddNew,
            IndicatorLunar.CONFIG_SATELLITES_SORT_BY_DATE_TIME : self.satellitesSortByDateTime,
            IndicatorLunar.CONFIG_SHOW_RISE_WHEN_SET_BEFORE_SUNSET : self.showRiseWhenSetBeforeSunset,
            IndicatorLunar.CONFIG_SHOW_SATELLITE_NOTIFICATION : self.showSatelliteNotification,
            IndicatorLunar.CONFIG_SHOW_WEREWOLF_WARNING : self.showWerewolfWarning,
            IndicatorLunar.CONFIG_STARS : self.stars,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_MESSAGE : self.werewolfWarningMessage,
            IndicatorLunar.CONFIG_WEREWOLF_WARNING_SUMMARY : self.werewolfWarningSummary
        }


IndicatorLunar().main()
