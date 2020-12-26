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


# Application indicator which displays lunar, solar, planetary, star,
# comet, minor planet and satellite information.


INDICATOR_NAME = "indicator-lunar"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )

from gi.repository import Gtk, Notify

import astrobase, datetime, eclipse, indicatorbase, locale, math, orbitalelement, re, sys, twolineelement, webbrowser


class IndicatorLunar( indicatorbase.IndicatorBase ):

    # Allow switching between backends.
    astroBackendPyEphem = "AstroPyEphem"
    astroBackendSkyfield = "AstroSkyfield"
    astroBackendName = astroBackendPyEphem
    astroBackend = getattr( __import__( astroBackendName.lower() ), astroBackendName )

    if astroBackend.getAvailabilityMessage() is not None:
        dialog = Gtk.MessageDialog( Gtk.Dialog(), Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, astroBackend.getAvailabilityMessage() )
        dialog.set_title( INDICATOR_NAME )
        dialog.run()
        dialog.destroy()
        sys.exit()

    if astroBackend.getVersionMessage() is not None:
        dialog = Gtk.MessageDialog( Gtk.Dialog(), Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, astroBackend.getVersionMessage() )
        dialog.set_title( INDICATOR_NAME )
        dialog.run()
        dialog.destroy()
        sys.exit()

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
    CONFIG_INDICATOR_TEXT_SEPARATOR = "indicatorTextSeparator"
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

    ICON_CACHE_BASENAME = "icon-"
    ICON_CACHE_MAXIMUM_AGE_HOURS = 0
    ICON_EXTENSION = "svg"
    ICON_FULL_MOON = ICON_CACHE_BASENAME + "fullmoon-" # Dynamically created in the user cache directory.
    ICON_SATELLITE = INDICATOR_NAME + "-satellite" # Located in /usr/share/icons

    INDICATOR_TEXT_DEFAULT = " [" + astrobase.AstroBase.NAME_TAG_MOON + " " + astrobase.AstroBase.DATA_TAG_PHASE + "]"
    INDICATOR_TEXT_SEPARATOR_DEFAULT = ", "

    DATE_TIME_FORMAT_HHcolonMM = "%H:%M"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspacespaceHHcolonMM = "%Y-%m-%d  %H:%M"

    BODY_TAGS_TRANSLATIONS = dict(
        list( astrobase.AstroBase.NAME_TAG_MOON_TRANSLATION.items() ) +
        list( astrobase.AstroBase.PLANET_TAGS_TRANSLATIONS.items() ) +
        list( astrobase.AstroBase.STAR_TAGS_TRANSLATIONS.items() ) +
        list( astrobase.AstroBase.NAME_TAG_SUN_TRANSLATION.items() ) )

    COMET_CACHE_BASENAME = "comet-oe-"
    COMET_CACHE_MAXIMUM_AGE_HOURS = 96
    if astroBackendName == astroBackendPyEphem:
        COMET_DATA_URL = "https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt"

    else:
        COMET_DATA_URL = "https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt"

    MINOR_PLANET_CACHE_BASENAMES = [ "minorplanet-oe-" + "bright-",
                                     "minorplanet-oe-" + "critical-",
                                     "minorplanet-oe-" + "distant-",
                                     "minorplanet-oe-" + "unusual-" ]
    MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS = 96
    if astroBackendName == astroBackendPyEphem:
        MINOR_PLANET_DATA_URLS = [ "https://minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft03Bright.txt",
                                   "https://minorplanetcenter.net/iau/Ephemerides/CritList/Soft03CritList.txt",
                                   "https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft03Distant.txt",
                                   "https://minorplanetcenter.net/iau/Ephemerides/Unusual/Soft03Unusual.txt" ]

    else:
        MINOR_PLANET_DATA_URLS = [ "https://minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft00Bright.txt",
                                   "https://minorplanetcenter.net/iau/Ephemerides/CritList/Soft00CritList.txt",
                                   "https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft00Distant.txt",
                                   "https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft00Unusual.txt" ]

    SATELLITE_CACHE_BASENAME = "satellite-tle-"
    SATELLITE_CACHE_MAXIMUM_AGE_HOURS = 48
    SATELLITE_DATA_URL = "https://celestrak.com/NORAD/elements/visual.txt"
    SATELLITE_NOTIFICATION_MESSAGE_DEFAULT = _( "Rise Time: " ) + astrobase.AstroBase.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n" + \
                                             _( "Rise Azimuth: " ) + astrobase.AstroBase.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\n" + \
                                             _( "Set Time: " ) + astrobase.AstroBase.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n" + \
                                             _( "Set Azimuth: " ) + astrobase.AstroBase.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION
    SATELLITE_NOTIFICATION_SUMMARY_DEFAULT = astrobase.AstroBase.SATELLITE_TAG_NAME + " : " + \
                                             astrobase.AstroBase.SATELLITE_TAG_NUMBER + " : " + \
                                             astrobase.AstroBase.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR + _( " now rising..." )

    SEARCH_URL_DWARF_PLANET = "https://solarsystem.nasa.gov/planets/dwarf-planets/"
    SEARCH_URL_COMET_AND_MINOR_PLANET = "https://www.minorplanetcenter.net/db_search/show_object?utf8=%E2%9C%93&object_id="
    SEARCH_URL_MOON = "https://solarsystem.nasa.gov/moons/earths-moon"
    SEARCH_URL_PLANET = "https://solarsystem.nasa.gov/planets/"
    SEARCH_URL_SATELLITE = "https://www.n2yo.com/satellite/?s="
    SEARCH_URL_STAR = "https://simbad.u-strasbg.fr/simbad/sim-id?Ident=HIP+"
    SEARCH_URL_SUN = "https://solarsystem.nasa.gov/solar-system/sun"

    WEREWOLF_WARNING_MESSAGE_DEFAULT = _( "                                          ...werewolves about ! ! !" )
    WEREWOLF_WARNING_SUMMARY_DEFAULT = _( "W  A  R  N  I  N  G" )


    def __init__( self ):
        super().__init__(
            indicatorName = INDICATOR_NAME,
            version = "1.0.86",
            copyrightStartYear = "2012",
            comments = _( "Displays lunar, solar, planetary, comet, minor planet, star and satellite information." ),
            creditz = [ IndicatorLunar.astroBackend.getCredit(),
                        _( "Eclipse information by Fred Espenak and Jean Meeus. https://eclipse.gsfc.nasa.gov" ),
                        _( "Satellite TLE data by Dr T S Kelso. https://www.celestrak.com" ),
                        _( "Comet and Minor Planet OE data by Minor Planet Center. https://www.minorplanetcenter.net" ) ] )


        utcNow = datetime.datetime.utcnow()

        self.cometData = { } # Key: comet name, upper cased; Value: orbitalelement.OE object.  Can be empty but never None.
        self.minorPlanetData = { } # Key: minor planet name, upper cased; Value: orbitalelement.OE object.  Can be empty but never None.
        self.satelliteData = { } # Key: satellite number; Value: twolineelement.TLE object.  Can be empty but never None.
        self.satellitePreviousNotifications = [ ]

        self.lastFullMoonNotfication = utcNow - datetime.timedelta( hours = 1 )

        self.__removePreviousVersionCacheFiles()
        self.__swapCacheFiles() #TODO Only for me!
        self.flushCache()
        self.initialiseDownloadCountsAndCacheDateTimes( utcNow )


    #TODO Start of temporary hack...remove in later release.
    # Cache data formats for comets and minor planets changed between version 84 and 85, so remove old format files.
    #
    # A new attribute, dataType, and a new inner class, DataType, were added to orbitalelement.
    # Need to remove old versions of data in this format.
    def __removePreviousVersionCacheFiles( self ):
        import os, pickle
        cachePath = self.getCachePath( "" )
        for file in os.listdir( cachePath ):
            if file.startswith( IndicatorLunar.COMET_CACHE_BASENAME ) or file[ 0 : file.rfind( "-" ) + 1 ] in IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES:
                with open( cachePath + file, "rb" ) as f:
                    data = pickle.load( f )
                    if data and not hasattr( next( iter( data.values() ) ), "dataType" ): 
                        os.remove( cachePath + file )


    #TODO Used to swap between PyEphem data files and Skyfield data files from the Minor Planet Center.
    def __swapCacheFiles( self ):
        data = self.readCacheBinary( IndicatorLunar.COMET_CACHE_BASENAME )
        if data is not None:
            import glob, os, shutil
            if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendSkyfield and \
               next( iter( data.values() ) ).dataType == orbitalelement.OE.DataType.XEPHEM_COMET:
                print( "Swapping Skyfield for XEphem" )
                shutil.rmtree( self.getCachePath( "" ) + "xephem", ignore_errors = True )
                os.mkdir( self.getCachePath( "" ) + "xephem" )

                for data in glob.glob( self.getCachePath( "" ) + "comet*" ):
                    shutil.move( data, self.getCachePath( "" ) + "xephem" )

                for data in glob.glob( self.getCachePath( "" ) + "minorplanet*" ):
                    shutil.move( data, self.getCachePath( "" ) + "xephem" )

                if os.path.isdir( self.getCachePath( "" ) + "skyfield" ):
                    for data in glob.glob( self.getCachePath( "" ) + "skyfield/*" ):
                        shutil.move( data, self.getCachePath( "" ) )

            elif IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendPyEphem and \
               next( iter( data.values() ) ).dataType == orbitalelement.OE.DataType.SKYFIELD_COMET:
                print( "Swapping XEphem for Skyfield" )
                shutil.rmtree( self.getCachePath( "" ) + "skyfield", ignore_errors = True )
                os.mkdir( self.getCachePath( "" ) + "skyfield" )
                for data in glob.glob( self.getCachePath( "" ) + "comet*" ):
                    shutil.move( data, self.getCachePath( "" ) + "skyfield" )

                for data in glob.glob( self.getCachePath( "" ) + "minorplanet*" ):
                    shutil.move( data, self.getCachePath( "" ) + "skyfield" )

                if os.path.isdir( self.getCachePath( "" ) + "xephem" ):
                    for data in glob.glob( self.getCachePath( "" ) + "xephem/*" ):
                        shutil.move( data, self.getCachePath( "" ) )


    def flushCache( self ):
#TODO Testing...put back!        
#         self.removeOldFilesFromCache( IndicatorLunar.ICON_CACHE_BASENAME, IndicatorLunar.ICON_CACHE_MAXIMUM_AGE_HOURS )
#         self.removeOldFilesFromCache( IndicatorLunar.ICON_FULL_MOON, IndicatorLunar.ICON_CACHE_MAXIMUM_AGE_HOURS )
        self.removeOldFilesFromCache( IndicatorLunar.COMET_CACHE_BASENAME, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS )
        self.removeOldFilesFromCache( IndicatorLunar.SATELLITE_CACHE_BASENAME, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS )
        for cacheBaseName in IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES:
            self.removeOldFilesFromCache( cacheBaseName, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )


    def initialiseDownloadCountsAndCacheDateTimes( self, utcNow ):
        self.downloadCountComet = 0
        self.downloadCountMinorPlanetBright = 0
        self.downloadCountMinorPlanetCritical = 0
        self.downloadCountMinorPlanetDistant = 0
        self.downloadCountMinorPlanetUnusual = 0
        self.downloadCountSatellite = 0

        self.nextDownloadTimeComet = utcNow
        self.nextDownloadTimeMinorPlanetBright = utcNow
        self.nextDownloadTimeMinorPlanetCritical = utcNow
        self.nextDownloadTimeMinorPlanetDistant = utcNow
        self.nextDownloadTimeMinorPlanetUnusual = utcNow
        self.nextDownloadTimeSatellite = utcNow

        self.cacheDateTimeComet = self.getCacheDateTime( IndicatorLunar.COMET_CACHE_BASENAME, utcNow - datetime.timedelta( hours = ( IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )
        self.cacheDateTimeMinorPlanetBright = self.getCacheDateTime( IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES[ 0 ], utcNow - datetime.timedelta( hours = ( IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )
        self.cacheDateTimeMinorPlanetCritical = self.getCacheDateTime( IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES[ 1 ], utcNow - datetime.timedelta( hours = ( IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )
        self.cacheDateTimeMinorPlanetDistant = self.getCacheDateTime( IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES[ 2 ], utcNow - datetime.timedelta( hours = ( IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )
        self.cacheDateTimeMinorPlanetUnusual = self.getCacheDateTime( IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES[ 3 ], utcNow - datetime.timedelta( hours = ( IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )
        self.cacheDateTimeSatellite = self.getCacheDateTime( IndicatorLunar.SATELLITE_CACHE_BASENAME, utcNow - datetime.timedelta( hours = ( IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )


    def update( self, menu ):
        utcNow = datetime.datetime.utcnow()

        magnitudeFilterAdditionalArguments = [ ]
        if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendSkyfield:
            magnitudeFilterAdditionalArguments = [ self.latitude, self.longitude, self.elevation, self.getLogging() ]

        # Update comet data.
        dataType = orbitalelement.OE.DataType.XEPHEM_COMET
        if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendSkyfield:
            dataType = orbitalelement.OE.DataType.SKYFIELD_COMET
            magnitudeFilterAdditionalArguments = [ astrobase.AstroBase.BodyType.COMET, self.latitude, self.longitude, self.elevation ]

        self.cometData, self.cacheDateTimeComet, self.downloadCountComet, self.nextDownloadTimeComet = \
            self.updateData( utcNow,
                             self.cacheDateTimeComet, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.COMET_CACHE_BASENAME,
                             orbitalelement.download, [ IndicatorLunar.COMET_DATA_URL, dataType, self.getLogging() ], self.downloadCountComet, self.nextDownloadTimeComet,
                             IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )

        if self.cometsAddNew:
            self.addNewBodies( self.cometData, self.comets )

        # Update minor planet data.
        self.minorPlanetData = { }

        dataType = orbitalelement.OE.DataType.XEPHEM_MINOR_PLANET
        if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendSkyfield:
            dataType = orbitalelement.OE.DataType.SKYFIELD_MINOR_PLANET
            magnitudeFilterAdditionalArguments = [ astrobase.AstroBase.BodyType.MINOR_PLANET, self.latitude, self.longitude, self.elevation, self.getLogging() ]

        minorPlanetData, self.cacheDateTimeMinorPlanetBright, self.downloadCountMinorPlanetBright, self.nextDownloadTimeMinorPlanetBright = \
            self.updateData( utcNow,
                             self.cacheDateTimeMinorPlanetBright, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES[ 0 ],
                             orbitalelement.download, [ IndicatorLunar.MINOR_PLANET_DATA_URLS[ 0 ], dataType, self.getLogging() ], self.downloadCountMinorPlanetBright, self.nextDownloadTimeMinorPlanetBright,
                             IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )

        self.minorPlanetData.update( minorPlanetData )

        minorPlanetData, self.cacheDateTimeMinorPlanetCritical, self.downloadCountMinorPlanetCritical, self.nextDownloadTimeMinorPlanetCritical = \
            self.updateData( utcNow,
                             self.cacheDateTimeMinorPlanetCritical, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES[ 1 ],
                             orbitalelement.download, [ IndicatorLunar.MINOR_PLANET_DATA_URLS[ 1 ], dataType, self.getLogging( )], self.downloadCountMinorPlanetCritical, self.nextDownloadTimeMinorPlanetCritical,
                             IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )

        self.minorPlanetData.update( minorPlanetData )

        minorPlanetData, self.cacheDateTimeMinorPlanetDistant, self.downloadCountMinorPlanetDistant, self.nextDownloadTimeMinorPlanetDistant = \
            self.updateData( utcNow,
                             self.cacheDateTimeMinorPlanetDistant, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES[ 2 ],
                             orbitalelement.download, [ IndicatorLunar.MINOR_PLANET_DATA_URLS[ 2 ], dataType, self.getLogging( ) ], self.downloadCountMinorPlanetDistant, self.nextDownloadTimeMinorPlanetDistant,
                             IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )

        self.minorPlanetData.update( minorPlanetData )

        minorPlanetData, self.cacheDateTimeMinorPlanetUnusual, self.downloadCountMinorPlanetUnusual, self.nextDownloadTimeMinorPlanetUnusual = \
            self.updateData( utcNow,
                             self.cacheDateTimeMinorPlanetUnusual, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.MINOR_PLANET_CACHE_BASENAMES[ 3 ],
                             orbitalelement.download, [ IndicatorLunar.MINOR_PLANET_DATA_URLS[ 3 ], dataType, self.getLogging( ) ], self.downloadCountMinorPlanetUnusual, self.nextDownloadTimeMinorPlanetUnusual,
                             IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )

        self.minorPlanetData.update( minorPlanetData )

        if self.minorPlanetsAddNew:
            self.addNewBodies( self.minorPlanetData, self.minorPlanets )

        # Update satellite data.
        self.satelliteData, self.cacheDateTimeSatellite, self.downloadCountSatellite, self.nextDownloadTimeSatellite = \
            self.updateData( utcNow,
                             self.cacheDateTimeSatellite, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.SATELLITE_CACHE_BASENAME,
                             twolineelement.download, [ IndicatorLunar.SATELLITE_DATA_URL, self.getLogging() ], self.downloadCountSatellite, self.nextDownloadTimeSatellite,
                             None, [ ] )

        if self.satellitesAddNew:
            self.addNewBodies( self.satelliteData, self.satellites )

        # Update backend.
        self.data = IndicatorLunar.astroBackend.calculate(
            utcNow,
            self.latitude, self.longitude, self.elevation,
            self.planets,
            self.stars,
            self.satellites, self.satelliteData,
            self.comets, self.cometData,
            self.minorPlanets, self.minorPlanetData,
            self.magnitude,
            self.getLogging() )

        # Update frontend.
        menu.append( Gtk.MenuItem.new_with_label( IndicatorLunar.astroBackendName ) )#TODO Debug
        self.updateMenu( menu )
        self.updateLabel()
        self.updateIcon()

        if self.showWerewolfWarning:
            self.notificationFullMoon()

        if self.showSatelliteNotification:
            self.notificationSatellites()

        return self.getNextUpdateTimeInSeconds()


    # Get the data from the cache, or if stale, download from the source.
    #
    # Returns a dictionary (may be empty).
    def updateData( self, utcNow,
                    cacheDateTime, cacheMaximumAge, cacheBaseName,
                    downloadDataFunction, downloadDataArguments,
                    downloadCount, nextDownloadTime,
                    magnitudeFilterFunction, magnitudeFilterAdditionalArguments ):

        if cacheBaseName != IndicatorLunar.SATELLITE_CACHE_BASENAME: return { }, cacheDateTime, downloadCount, nextDownloadTime #TODO Testing

        if utcNow < ( cacheDateTime + datetime.timedelta( hours = cacheMaximumAge ) ):
            data = self.readCacheBinary( cacheBaseName )

        else:
            data = { }
            if nextDownloadTime < utcNow:
                data = downloadDataFunction( *downloadDataArguments )
                downloadCount += 1
                if data:
                    if magnitudeFilterFunction:
                        data = magnitudeFilterFunction( utcNow, data, astrobase.AstroBase.MAGNITUDE_MAXIMUM, *magnitudeFilterAdditionalArguments )
 
                    self.writeCacheBinary( cacheBaseName, data )
                    downloadCount = 0
                    cacheDateTime = self.getCacheDateTime( cacheBaseName )
                    nextDownloadTime = utcNow + datetime.timedelta( hours = cacheMaximumAge )
 
                else:
                    nextDownloadTime = self.getNextDownloadTime( utcNow, downloadCount ) # Download failed for some reason; retry at a later time...
 
        return data, cacheDateTime, downloadCount, nextDownloadTime


    def getNextDownloadTime( self, utcNow, downloadCount ):
        nextDownloadTime = utcNow + datetime.timedelta( minutes = 60 * 24 ) # Worst case scenario for retrying downloads: every 24 hours.
        timeIntervalInMinutes = { 1 : 5,
                                  2 : 15,
                                  3 : 60 }

        if downloadCount in timeIntervalInMinutes:
            nextDownloadTime = utcNow + datetime.timedelta( minutes = timeIntervalInMinutes[ downloadCount ] )

        return nextDownloadTime


    def addNewBodies( self, data, bodies ):
        for body in data:
            if body not in bodies:
                bodies.append( body )


    def getNextUpdateTimeInSeconds( self ):
        utcNow = datetime.datetime.utcnow()

        # Do an update at least hourly so the moon icon reflects reality.
        # This also ensures the download of comet/minor planet/satellite data occurs no more than an hour from when they are supposed to happen.
        nextUpdateTime = utcNow + datetime.timedelta( hours = 1 )

        for key in self.data:
            dateTimeAttributeExceptRiseDateTime = \
                key[ 2 ] == astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME or \
                key[ 2 ] == astrobase.AstroBase.DATA_TAG_EQUINOX or \
                key[ 2 ] == astrobase.AstroBase.DATA_TAG_FIRST_QUARTER or \
                key[ 2 ] == astrobase.AstroBase.DATA_TAG_FULL or \
                key[ 2 ] == astrobase.AstroBase.DATA_TAG_NEW or \
                key[ 2 ] == astrobase.AstroBase.DATA_TAG_SET_DATE_TIME or \
                key[ 2 ] == astrobase.AstroBase.DATA_TAG_SOLSTICE or \
                key[ 2 ] == astrobase.AstroBase.DATA_TAG_THIRD_QUARTER

            riseDateTimeAtributeAndShowBodiesBelowHorizon = \
                key[ 2 ] == astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME and not self.hideBodiesBelowHorizon

            if dateTimeAttributeExceptRiseDateTime or riseDateTimeAtributeAndShowBodiesBelowHorizon:
                dateTime = datetime.datetime.strptime( self.data[ key ], astrobase.AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )
                if dateTime < nextUpdateTime:
                    nextUpdateTime = dateTime

        nextUpdateInSeconds = int( ( nextUpdateTime - utcNow ).total_seconds() )
        if nextUpdateInSeconds <= 60:
            nextUpdateInSeconds = 60 # Give at least a minute between updates, to avoid consuming resources.

        return nextUpdateInSeconds


    def updateMenu( self, menu ):
        self.updateMenuMoon( menu )
        self.updateMenuSun( menu )
        self.updateMenuPlanets( menu )
        self.updateMenuStars( menu )
        self.updateMenuCometsMinorPlanets( menu, astrobase.AstroBase.BodyType.COMET )
        self.updateMenuCometsMinorPlanets( menu, astrobase.AstroBase.BodyType.MINOR_PLANET)
        self.updateMenuSatellites( menu )


    def updateLabel( self ):
        # Substitute data tags '[' and ']' for values.
        label = self.indicatorText

        for key in self.data.keys():
            if "[" + key[ 1 ] + " " + key[ 2 ] + "]" in label:
                label = label.replace( "[" + key[ 1 ] + " " + key[ 2 ] + "]", self.getDisplayData( key ) )

        # Handle any free text '{' and '}'.
        i = 0
        start = i
        result = ""
        lastSeparatorIndex = -1 # Need to track the last insertion point of the separator so it can be removed.
        while( i < len( label ) ):
            if label[ i ] == '{':
                j = i + 1
                while( j < len( label ) ):
                    if label[ j ] == '}':
                        freeText = label[ i + 1 : j ]
                        freeTextMinusUnknownTags = re.sub( "\[[^\[^\]]*\]", "", freeText )
                        if freeText == freeTextMinusUnknownTags: # No unused tags were found.
                            result += label[ start : i ] + freeText + self.indicatorTextSeparator
                            lastSeparatorIndex = len( result ) - len( self.indicatorTextSeparator )

                        else:
                            result += label[ start : i ]

                        i = j
                        start = i + 1
                        break

                    j += 1

            i += 1

        if lastSeparatorIndex > -1:
            result = result[ 0 : lastSeparatorIndex ] # Remove the last separator.

        result += label[ start : i ]

        self.indicator.set_label( result, "" )
        self.indicator.set_title( result ) # Needed for Lubuntu/Xubuntu.


    def updateIcon( self ):
        # Ideally overwrite the icon with the same name each time.
        # Due to a bug, the icon name must change between calls to setting the icon.
        # So change the name each time - using the current date/time.
        #    https://bugs.launchpad.net/ubuntu/+source/libappindicator/+bug/1337620
        #    http://askubuntu.com/questions/490634/application-indicator-icon-not-changing-until-clicked
        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( astrobase.AstroBase.DATA_TAG_ILLUMINATION, ) ] )
        lunarBrightLimbAngleInDegrees = int( math.degrees( float( self.data[ key + ( astrobase.AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] ) ) )
        svgIconText = self.createIconText( lunarIlluminationPercentage, lunarBrightLimbAngleInDegrees )
        iconFilename = self.writeCacheText( IndicatorLunar.ICON_CACHE_BASENAME, svgIconText, False, IndicatorLunar.ICON_EXTENSION )
        self.indicator.set_icon_full( iconFilename, "" )


    def notificationFullMoon( self ):
        utcNow = datetime.datetime.utcnow()
        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        lunarIlluminationPercentage = int( self.data[ key + ( astrobase.AstroBase.DATA_TAG_ILLUMINATION, ) ] )
        lunarPhase = self.data[ key + ( astrobase.AstroBase.DATA_TAG_PHASE, ) ]

        if ( lunarPhase == astrobase.AstroBase.LUNAR_PHASE_WAXING_GIBBOUS or lunarPhase == astrobase.AstroBase.LUNAR_PHASE_FULL_MOON ) and \
           lunarIlluminationPercentage >= 96 and \
           ( ( self.lastFullMoonNotfication + datetime.timedelta( hours = 1 ) ) < utcNow ):

            summary = self.werewolfWarningSummary
            if self.werewolfWarningSummary == "":
                summary = " " # The notification summary text cannot be empty (at least on Unity).

            self.createFullMoonIcon()
            Notify.Notification.new( summary, self.werewolfWarningMessage, IndicatorLunar.ICON_FULL_MOON ).show()
            self.lastFullMoonNotfication = utcNow


    def createFullMoonIcon( self ):
        return self.writeCacheText( IndicatorLunar.ICON_FULL_MOON,
                                    self.createIconText( 100, None ),
                                    False,
                                    IndicatorLunar.ICON_EXTENSION )


    def notificationSatellites( self ):
        utcNow = datetime.datetime.utcnow()
        satelliteCurrentNotifications = [ ]
        for number in self.satellites:
            key = ( astrobase.AstroBase.BodyType.SATELLITE, number )
            if ( key + ( astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH, ) ) in self.data and number not in self.satellitePreviousNotifications: # About to rise and no notification already sent.
                riseTime = datetime.datetime.strptime( self.data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ],
                                                       astrobase.AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )

                if ( riseTime - datetime.timedelta( minutes = 2 ) ) <= utcNow: # Two minute buffer.
                    satelliteCurrentNotifications.append( [ number, riseTime ] )
                    self.satellitePreviousNotifications.append( number )

            if ( key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ) in self.data:
                setTime = datetime.datetime.strptime( self.data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ],
                                                  astrobase.AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )

                if number in self.satellitePreviousNotifications and setTime < utcNow: # Notification has been sent and satellite has now set.
                    self.satellitePreviousNotifications.remove( number )

        for number, riseTime in sorted( satelliteCurrentNotifications, key = lambda x: ( x[ 1 ], x[ 0 ] ) ):
            key = ( astrobase.AstroBase.BodyType.SATELLITE, number )
            riseTime = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            riseAzimuth = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            setTime = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )
            setAzimuth = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_AZIMUTH, ), IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM )

            summary = self.satelliteNotificationSummary. \
                      replace( astrobase.AstroBase.SATELLITE_TAG_NAME, self.satelliteData[ number ].getName() ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_NUMBER, self.satelliteData[ number ].getNumber() ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satelliteData[ number ].getInternationalDesignator() ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_RISE_TIME, riseTime ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_SET_TIME, setTime ) + \
                      " " # The notification summary text must not be empty (at least on Unity).

            message = self.satelliteNotificationMessage. \
                      replace( astrobase.AstroBase.SATELLITE_TAG_NAME, self.satelliteData[ number ].getName() ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_NUMBER, self.satelliteData[ number ].getNumber() ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satelliteData[ number ].getInternationalDesignator() ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_RISE_TIME, riseTime ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
                      replace( astrobase.AstroBase.SATELLITE_TAG_SET_TIME, setTime )

            Notify.Notification.new( summary, message, IndicatorLunar.ICON_SATELLITE ).show()


    def updateMenuMoon( self, menu ):
        key = ( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON )
        if self.display( astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON ):
            menuItem = self.createMenuItem( menu, _( "Moon" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            self.updateMenuCommon( subMenu, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON, 0, 1, IndicatorLunar.SEARCH_URL_MOON )
            self.createMenuItem( subMenu, self.indent( 0, 1 ) + _( "Phase: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_PHASE, ) ), IndicatorLunar.SEARCH_URL_MOON )
            self.createMenuItem( subMenu, self.indent( 0, 1 ) + _( "Next Phases" ), IndicatorLunar.SEARCH_URL_MOON )

            # Determine which phases occur by date rather than using the phase calculated.
            # The phase (illumination) rounds numbers and so a given phase is entered earlier than what is correct.
            nextPhases = [ ]
            nextPhases.append( [ self.data[ key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ], _( "First Quarter: " ), key + ( astrobase.AstroBase.DATA_TAG_FIRST_QUARTER, ) ] )
            nextPhases.append( [ self.data[ key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ], _( "Full: " ), key + ( astrobase.AstroBase.DATA_TAG_FULL, ) ] )
            nextPhases.append( [ self.data[ key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ], _( "New: " ), key + ( astrobase.AstroBase.DATA_TAG_NEW, ) ] )
            nextPhases.append( [ self.data[ key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ], _( "Third Quarter: " ), key + ( astrobase.AstroBase.DATA_TAG_THIRD_QUARTER, ) ] )
            indent = self.indent( 1, 2 )
            for dateTime, displayText, key in sorted( nextPhases, key = lambda pair: pair[ 0 ] ):
                self.createMenuItem( subMenu, indent + displayText + self.getDisplayData( key ), IndicatorLunar.SEARCH_URL_MOON )

            self.updateMenuEclipse( subMenu, astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON, IndicatorLunar.SEARCH_URL_MOON )


    def updateMenuSun( self, menu ):
        key = ( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN )
        if self.display( astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN ):
            menuItem = self.createMenuItem( menu, _( "Sun" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            self.updateMenuCommon( subMenu, astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN, 0, 1, IndicatorLunar.SEARCH_URL_SUN )
            self.createMenuItem( subMenu, self.indent( 0, 1 ) + _( "Equinox: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_EQUINOX, ) ), IndicatorLunar.SEARCH_URL_SUN )
            self.createMenuItem( subMenu, self.indent( 0, 1 ) + _( "Solstice: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SOLSTICE, ) ), IndicatorLunar.SEARCH_URL_SUN )
            self.updateMenuEclipse( subMenu, astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN, IndicatorLunar.SEARCH_URL_SUN )


    def updateMenuEclipse( self, menu, bodyType, nameTag, url ):
        key = ( bodyType, nameTag )
        self.createMenuItem( menu, self.indent( 0, 1 ) + _( "Eclipse" ), url )
        self.createMenuItem( menu, self.indent( 1, 2 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ), url )
        self.createMenuItem( menu, self.indent( 1, 2 ) + _( "Type: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ), url )
        if key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) in self.data: # PyEphem uses the NASA Eclipse data which contains latitude/longitude; Skyfield does not.
            latitude = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) )
            longitude = self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) )
            self.createMenuItem( menu, self.indent( 1, 2 ) + _( "Latitude/Longitude: " ) + latitude + " " + longitude, url )


    def updateMenuPlanets( self, menu ):
        planets = [ ]
        for planet in self.planets:
            if self.display( astrobase.AstroBase.BodyType.PLANET, planet ):
                planets.append( [ planet, astrobase.AstroBase.PLANET_NAMES_TRANSLATIONS[ planet ] ] )

        if planets:
            menuItem = self.createMenuItem( menu, _( "Planets" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for name, translatedName in planets:
                if name == astrobase.AstroBase.PLANET_PLUTO:
                    url = IndicatorLunar.SEARCH_URL_DWARF_PLANET + name.lower()

                else:
                    url = IndicatorLunar.SEARCH_URL_PLANET + name.lower()

                self.createMenuItem( subMenu, self.indent( 0, 1 ) + translatedName, url )
                self.updateMenuCommon( subMenu, astrobase.AstroBase.BodyType.PLANET, name, 1, 2, url )
                separator = Gtk.SeparatorMenuItem()
                subMenu.append( separator )

            subMenu.remove( separator )


    def updateMenuStars( self, menu ):
        stars = [ ]
        for star in self.stars:
            if self.display( astrobase.AstroBase.BodyType.STAR, star ):
                stars.append( [ star, astrobase.AstroBase.STAR_NAMES_TRANSLATIONS[ star ] ] )

        if stars:
            menuItem = self.createMenuItem( menu, _( "Stars" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for name, translatedName in stars:
                url = IndicatorLunar.SEARCH_URL_STAR + str( IndicatorLunar.astroBackend.STARS_TO_HIP[ name ] )
                self.createMenuItem( subMenu, self.indent( 0, 1 ) + translatedName, url )
                self.updateMenuCommon( subMenu, astrobase.AstroBase.BodyType.STAR, name, 1, 2, url )
                separator = Gtk.SeparatorMenuItem()
                subMenu.append( separator )

            subMenu.remove( separator )


    def updateMenuCometsMinorPlanets( self, menu, bodyType ):
        orbitalElements = [ ]
        for body in ( self.comets if bodyType == astrobase.AstroBase.BodyType.COMET else self.minorPlanets ):
            if self.display( bodyType, body ):
                orbitalElements.append( body )

        if orbitalElements:
            menuItem = self.createMenuItem( menu, _( "Comets" ) if bodyType == astrobase.AstroBase.BodyType.COMET else _( "Minor Planets" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for name in sorted( orbitalElements ):
                url = IndicatorLunar.SEARCH_URL_COMET_AND_MINOR_PLANET + self.getCometMinorPlanetOnClickURL( name, bodyType )
                self.createMenuItem( subMenu, self.indent( 0, 1 ) + name, url )
                self.updateMenuCommon( subMenu, bodyType, name, 1, 2, url )
                separator = Gtk.SeparatorMenuItem()
                subMenu.append( separator )

            subMenu.remove( separator )


    # https://www.iau.org/public/themes/naming
    # https://minorplanetcenter.net/iau/info/CometNamingGuidelines.html
    def getCometMinorPlanetOnClickURL( self, name, bodyType ):
        if bodyType == astrobase.AstroBase.BodyType.COMET:
            if "(" in name: # P/1997 T3 (Lagerkvist-Carsenty)
                hip = name[ : name.find( "(" ) ].strip()

            else:
                postSlash = name[ name.find( "/" ) + 1 : ]
                if re.search( '\d', postSlash ): # C/1931 AN
                    hip = name

                else: # 97P/Metcalf-Brewington
                    hip = name[ : name.find( "/" ) ].strip()

        else:
            components = name.split( ' ' )
            if components[ 0 ].isnumeric() and components[ 1 ].isalpha(): # 433 Eros
                hip = components[ 0 ]

            elif components[ 0 ].isnumeric() and components[ 1 ].isnumeric(): # 465402 2008 HW1
                hip = components[ 0 ]

            elif components[ 0 ].isnumeric() and components[ 1 ].isalnum(): # 1999 KL17
                hip = components[ 0 ] + " " + components[ 1 ]

            else: # 229762 G!kunll'homdima
                hip = components[ 0 ]

        return hip


    # Determine if a body should be displayed taking into account:
    #
    #    The user preference for hiding a body if the body is below the horizon.
    #    The astro backend behaviour:
    #        The rise/set/az/alt is present for a body which will rise and set.
    #        The az/alt is present for a body which is always up.
    #        No data will be present for a body which is never up.
    def display( self, bodyType, nameTag ):
        displayBody = False
        key = ( bodyType, nameTag )
        if ( bodyType, nameTag, astrobase.AstroBase.DATA_TAG_AZIMUTH ) in self.data: # Body will rise or set or is 'always up'.
            displayBody = True
            if ( bodyType, nameTag, astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME ) in self.data:
                if self.data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] < self.data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ]:
                    displayBody = not self.hideBodiesBelowHorizon

        return displayBody


    def updateMenuCommon( self, menu, bodyType, nameTag, indentUnity, indentGnomeShell, onClickURL = "" ):
        key = ( bodyType, nameTag )
        indent = self.indent( indentUnity, indentGnomeShell )
        if key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) in self.data: # Implies this body rises/sets (not always up).
            if self.data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] < self.data[ key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ]:
                self.createMenuItem( menu, indent + _( "Rise: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ), onClickURL )

            else:
                self.createMenuItem( menu, indent + _( "Set: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ), onClickURL )
                self.createMenuItem( menu, indent + _( "Azimuth: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ), onClickURL )
                self.createMenuItem( menu, indent + _( "Altitude: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ), onClickURL )

        else: # Body is always up.
            self.createMenuItem( menu, indent + _( "Azimuth: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ), onClickURL )
            self.createMenuItem( menu, indent + _( "Altitude: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ), onClickURL )


    def updateMenuSatellites( self, menu ):
        satellites = [ ]
        satellitesPolar = [ ]
        if self.satellitesSortByDateTime:
            for number in self.satellites:
                key = ( astrobase.AstroBase.BodyType.SATELLITE, number )
                if key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) in self.data:
                    satellites.append( [ number, self.satelliteData[ number ].getName(), self.data[ key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] ] )

                elif key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) in self.data:
                    satellitesPolar.append( [ number, self.satelliteData[ number ].getName(), None ] )

            satellites = sorted( satellites, key = lambda x: ( x[ 2 ], x[ 0 ], x[ 1 ] ) )
            satellitesPolar = sorted( satellitesPolar, key = lambda x: ( x[ 1 ], x[ 0 ] ) ) # Sort by name then number.

        else:
            for number in self.satellites:
                key = ( astrobase.AstroBase.BodyType.SATELLITE, number )
                if key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) in self.data or key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) in self.data:
                    satellites.append( [ number, self.satelliteData[ number ].getName(), None ] )

            satellites = sorted( satellites, key = lambda x: ( x[ 1 ], x[ 0 ] ) ) # Sort by name then number.

        if satellites:
            self.__updateMenuSatellites( menu, _( "Satellites" ), satellites )

        if satellitesPolar:
            self.__updateMenuSatellites( menu, _( "Satellites (Polar)" ), satellitesPolar )


    def __updateMenuSatellites( self, menu, label, satellites ):
        menuItem = self.createMenuItem( menu, label )
        subMenu = Gtk.Menu()
        menuItem.set_submenu( subMenu )
        utcNowPlusFiveMinutes = datetime.datetime.utcnow() + datetime.timedelta( minutes = 5 )
        for number, name, riseDateTime in satellites:
            url = IndicatorLunar.SEARCH_URL_SATELLITE + number
            menuItem = self.createMenuItem( subMenu, self.indent( 0, 1 ) + name + " : " + number + " : " + self.satelliteData[ number ].getInternationalDesignator(), url )
            key = ( astrobase.AstroBase.BodyType.SATELLITE, number )
            if key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) in self.data: # Satellite will rise or is in transit.

                if datetime.datetime.strptime( riseDateTime, astrobase.AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS ) < utcNowPlusFiveMinutes:
                    self.createMenuItem( subMenu, self.indent( 1, 2 ) + _( "Rise" ), url )
                    self.createMenuItem( subMenu, self.indent( 2, 3 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ), url )
                    self.createMenuItem( subMenu, self.indent( 2, 3 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH, ) ), url )
                    self.createMenuItem( subMenu, self.indent( 1, 2 ) + _( "Set" ), url )
                    self.createMenuItem( subMenu, self.indent( 2, 3 ) + _( "Date/Time: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_DATE_TIME, ) ), url )
                    self.createMenuItem( subMenu, self.indent( 2, 3 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_SET_AZIMUTH, ) ), url )

                else:
                    self.createMenuItem( subMenu, self.indent( 1, 2 ) + _( "Rise Date/Time: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_RISE_DATE_TIME, ) ), url )

            else: # Polar (always up).
                self.createMenuItem( subMenu, self.indent( 1, 2 ) + _( "Azimuth: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_AZIMUTH, ) ), url )
                self.createMenuItem( subMenu, self.indent( 1, 2 ) + _( "Altitude: " ) + self.getDisplayData( key + ( astrobase.AstroBase.DATA_TAG_ALTITUDE, ) ), url )

            separator = Gtk.SeparatorMenuItem()
            subMenu.append( separator )

        subMenu.remove( separator )


    def createMenuItem( self, menu, label, onClickURL = "" ):
        menuItem = Gtk.MenuItem.new_with_label( label )
        menu.append( menuItem )
        if onClickURL:
            menuItem.set_name( onClickURL )
            menuItem.connect( "activate", self.onMenuItemClick )

        return menuItem


    def onMenuItemClick( self, widget ): webbrowser.open( widget.props.name )


    def getDisplayData( self, key, dateTimeFormat = None ):
        displayData = None

        if key[ 2 ] == astrobase.AstroBase.DATA_TAG_ALTITUDE or \
           key[ 2 ] == astrobase.AstroBase.DATA_TAG_AZIMUTH or \
           key[ 2 ] == astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH or \
           key[ 2 ] == astrobase.AstroBase.DATA_TAG_SET_AZIMUTH:
            displayData = str( round( math.degrees( float( self.data[ key ] ) ) ) ) + "°"

        elif key[ 2 ] == astrobase.AstroBase.DATA_TAG_BRIGHT_LIMB:
            displayData = str( int( float( self.data[ key ] ) ) ) + "°"

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
                    displayData = self.toLocalDateTimeString( self.data[ key ], IndicatorLunar.DATE_TIME_FORMAT_YYYYdashMMdashDDspacespaceHHcolonMM )

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

        elif key[ 2 ] == astrobase.AstroBase.DATA_TAG_ILLUMINATION:
            displayData = self.data[ key ] + "%"

        elif key[ 2 ] == astrobase.AstroBase.DATA_TAG_PHASE:
            displayData = astrobase.AstroBase.LUNAR_PHASE_NAMES_TRANSLATIONS[ self.data[ key ] ]

        if displayData is None:
            displayData = "" # Better to show nothing than let None slip through and crash.
            self.getLogging().error( "Unknown key: " + str( key ) )

        return displayData


    # Converts a UTC date/time string to a local date/time string in the given format.
    def toLocalDateTimeString( self, utcDateTimeString, outputFormat ):
        utcDateTime = datetime.datetime.strptime( utcDateTimeString, astrobase.AstroBase.DATE_TIME_FORMAT_YYYYcolonMMcolonDDspaceHHcolonMMcolonSS )
        localDateTime = utcDateTime.replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None )
        return localDateTime.strftime( outputFormat )


    # Creates the SVG icon text representing the moon given the illumination and bright limb angle.
    #
    #    illuminationPercentage The brightness ranging from 0 to 100 inclusive.
    #
    #    brightLimbAngleInDegrees The angle of the bright limb, relative to zenith, ranging from 0 to 360 inclusive.
    #                             Ignored if illuminationPercentage is 0 or 100.
    def createIconText( self, illuminationPercentage, brightLimbAngleInDegrees ):
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
                   'A ' + str( radius ) + ' ' + str( radius ) + ' 0 0 1 ' + str( width / 2 + radius ) + ' ' + str( height / 2 )
            if illuminationPercentage == 50: # Quarter
                body += ' Z"'

            elif illuminationPercentage < 50: # Crescent
                body += ' A ' + str( radius ) + ' ' + str( radius * ( 50 - illuminationPercentage ) / 50 ) + ' 0 0 0 ' + str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            else: # Gibbous
                body += ' A ' + str( radius ) + ' ' + str( radius * ( illuminationPercentage - 50 ) / 50 ) + ' 0 0 1 ' + str( width / 2 - radius ) + ' ' + str( height / 2 ) + '"'

            body += ' transform="rotate(' + str( -brightLimbAngleInDegrees ) + ' ' + str( width / 2 ) + ' ' + str( height / 2 ) + ')" fill="#' + colour + '" />'

        return '<?xml version="1.0" standalone="no"?>' \
               '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "https://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
               '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100">' + body + '</svg>'


    def onPreferences( self, dialog ):
        notebook = Gtk.Notebook()

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
        grid.attach( scrolledWindow, 0, 2, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Icon" ) ) )

        # Menu.
        grid = self.createGrid()

        hideBodiesBelowTheHorizonCheckbox = Gtk.CheckButton.new_with_label( _( "Hide bodies below the horizon" ) )
        hideBodiesBelowTheHorizonCheckbox.set_active( self.hideBodiesBelowHorizon )
        hideBodiesBelowTheHorizonCheckbox.set_tooltip_text( _(
            "If checked, all bodies below the horizon\n" + \
            "are hidden (excludes satellites)." ) )
        grid.attach( hideBodiesBelowTheHorizonCheckbox, 0, 0, 1, 1 )

        cometsAddNewCheckbox = Gtk.CheckButton.new_with_label( _( "Add new comets" ) )
        cometsAddNewCheckbox.set_margin_top( 10 )
        cometsAddNewCheckbox.set_active( self.cometsAddNew )
        cometsAddNewCheckbox.set_tooltip_text( _( "If checked, all comets are added." ) )
        grid.attach( cometsAddNewCheckbox, 0, 1, 1, 1 )

        minorPlanetsAddNewCheckbox = Gtk.CheckButton.new_with_label( _( "Add new minor planets" ) )
        minorPlanetsAddNewCheckbox.set_margin_top( 10 )
        minorPlanetsAddNewCheckbox.set_active( self.minorPlanetsAddNew )
        minorPlanetsAddNewCheckbox.set_tooltip_text( _( "If checked, all minor planets are added." ) )
        grid.attach( minorPlanetsAddNewCheckbox, 0, 2, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label.new( _( "Hide bodies greater than magnitude" ) ), False, False, 0 )

        spinnerMagnitude = Gtk.SpinButton()
        spinnerMagnitude.set_numeric( True )
        spinnerMagnitude.set_update_policy( Gtk.SpinButtonUpdatePolicy.IF_VALID )
        spinnerAdjustment = Gtk.Adjustment.new( self.magnitude, int( astrobase.AstroBase.MAGNITUDE_MINIMUM ), int( astrobase.AstroBase.MAGNITUDE_MAXIMUM ), 1, 5, 0 )
        spinnerMagnitude.set_adjustment( spinnerAdjustment )
        spinnerMagnitude.set_value( self.magnitude ) # In Ubuntu 13.10, the initial value set by the adjustment would not appear, so force by explicitly setting.
        spinnerMagnitude.set_tooltip_text( _(
            "Planets, stars, comets and minor planets\n" + \
            "exceeding the magnitude will be hidden." ) )

        box.pack_start( spinnerMagnitude, False, False, 0 )
        grid.attach( box, 0, 3, 1, 1 )

        satellitesAddNewCheckbox = Gtk.CheckButton.new_with_label( _( "Add new satellites" ) )
        satellitesAddNewCheckbox.set_margin_top( 10 )
        satellitesAddNewCheckbox.set_active( self.satellitesAddNew )
        satellitesAddNewCheckbox.set_tooltip_text( _( "If checked, all satellites are added." ) )
        grid.attach( satellitesAddNewCheckbox, 0, 4, 1, 1 )

        sortSatellitesByDateTimeCheckbox = Gtk.CheckButton.new_with_label( _( "Sort satellites by rise date/time" ) )
        sortSatellitesByDateTimeCheckbox.set_margin_top( 10 )
        sortSatellitesByDateTimeCheckbox.set_active( self.satellitesSortByDateTime )
        sortSatellitesByDateTimeCheckbox.set_tooltip_text( _(
            "If checked, satellites are sorted\n" + \
            "by rise date/time.\n\n" + \
            "Otherwise satellites are sorted\n" + \
            "by Name then Number." ) )
        grid.attach( sortSatellitesByDateTimeCheckbox, 0, 5, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )

        # Planets/Stars.
        box = Gtk.Box( spacing = 20 )

        planetStore = Gtk.ListStore( bool, str, str ) # Show/hide, planet name (not displayed), translated planet name.
        for planetName in astrobase.AstroBase.PLANETS:
            planetStore.append( [ planetName in self.planets, planetName, astrobase.AstroBase.PLANET_NAMES_TRANSLATIONS[ planetName ] ] )

        toolTipText = _( "Check a planet to display in the menu." ) + "\n\n" + \
                      _( "Clicking the header of the first column\n" + \
                         "will toggle all checkboxes." )

        box.pack_start( self.createTreeView( planetStore, toolTipText, _( "Planet" ), 2 ), True, True, 0 )

        stars = [ ] # List of lists, each sublist containing star is checked flag, star name, star translated name.
        for starName in astrobase.AstroBase.STAR_NAMES_TRANSLATIONS.keys():
            stars.append( [ starName in self.stars, starName, astrobase.AstroBase.STAR_NAMES_TRANSLATIONS[ starName ] ] )

        starStore = Gtk.ListStore( bool, str, str ) # Show/hide, star name (not displayed), star translated name.
        for star in sorted( stars, key = lambda x: ( x[ 2 ] ) ):
            starStore.append( star )

        toolTipText = _( "Check a star to display in the menu." ) + "\n\n" + \
                      _( "Clicking the header of the first column\n" + \
                         "will toggle all checkboxes." )

        box.pack_start( self.createTreeView( starStore, toolTipText, _( "Star" ), 2 ), True, True, 0 )

        notebook.append_page( box, Gtk.Label.new( _( "Planets / Stars" ) ) )

        # Comets and minor planets.
        box = Gtk.Box( spacing = 20 )

        cometStore = Gtk.ListStore( bool, str ) # Show/hide, comet name.
        for comet in sorted( self.cometData.keys() ):
            cometStore.append( [ comet in self.comets, comet ] )

        if self.cometData:
            toolTipText = _( "Check a comet to display in the menu." ) + "\n\n" + \
                          _( "Clicking the header of the first column\n" + \
                             "will toggle all checkboxes." )

        else:
            toolTipText = _(
                "Comet data is unavailable; the source\n" + \
                "could not be reached, or no data was\n" + \
                "available from the source, or the data\n" + \
                "was completely filtered by magnitude." )

        box.pack_start( self.createTreeView( cometStore, toolTipText, _( "Comet" ), 1 ), True, True, 0 )

        minorPlanetStore = Gtk.ListStore( bool, str ) # Show/hide, minor planet name.
        for minorPlanet in sorted( self.minorPlanetData.keys() ):
            minorPlanetStore.append( [ minorPlanet in self.minorPlanets, minorPlanet ] )

        if self.minorPlanetData:
            toolTipText = _( "Check a minor planet to display in the menu." ) + "\n\n" + \
                          _( "Clicking the header of the first column\n" + \
                             "will toggle all checkboxes." )

        else:
            toolTipText = _(
                "Minor planet data is unavailable;\n" + \
                "the source could not be reached,\n" + \
                "or no data was available, or the data\n" + \
                "was completely filtered by magnitude." )

        box.pack_start( self.createTreeView( minorPlanetStore, toolTipText, _( "Minor Planet" ), 1 ), True, True, 0 )

        notebook.append_page( box, Gtk.Label.new( _( "Comets / Minor Planets" ) ) )

        # Satellites.
        box = Gtk.Box()

        satelliteStore = Gtk.ListStore( bool, str, str, str ) # Show/hide, name, number, international designator.
        for satellite in self.satelliteData:
            satelliteStore.append( [ satellite in self.satellites,
                                     self.satelliteData[ satellite ].getName(),
                                     satellite, self.satelliteData[ satellite ].getInternationalDesignator() ] )

        satelliteStoreSort = Gtk.TreeModelSort( model = satelliteStore )
        satelliteStoreSort.set_sort_column_id( 1, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView.new_with_model( satelliteStoreSort )
        if self.satelliteData:
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

        notebook.append_page( box, Gtk.Label.new( _( "Satellites" ) ) )

        # Notifications (satellite and full moon).
        notifyOSDInformation = _( "For formatting, refer to https://wiki.ubuntu.com/NotifyOSD" )

        grid = self.createGrid()

        satelliteTagTranslations = self.listOfListsToListStore( astrobase.AstroBase.SATELLITE_TAG_TRANSLATIONS )
        messageText = self.translateTags( satelliteTagTranslations, True, self.satelliteNotificationMessage )
        summaryText = self.translateTags( satelliteTagTranslations, True, self.satelliteNotificationSummary )
        toolTipCommon = astrobase.AstroBase.SATELLITE_TAG_NAME_TRANSLATION + "\n\t" + \
                        astrobase.AstroBase.SATELLITE_TAG_NUMBER_TRANSLATION + "\n\t" + \
                        astrobase.AstroBase.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION + "\n\t" + \
                        astrobase.AstroBase.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\t" + \
                        astrobase.AstroBase.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n\t" + \
                        astrobase.AstroBase.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION + "\n\t" + \
                        astrobase.AstroBase.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n\t" + \
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

        box.pack_start( Gtk.Label.new( _( "Latitude" ) ), False, False, 0 )

        latitude = Gtk.Entry()
        latitude.set_tooltip_text( _( "Latitude of your location in decimal degrees." ) )
        box.pack_start( latitude, False, False, 0 )
        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )

        box.pack_start( Gtk.Label.new( _( "Longitude" ) ), False, False, 0 )

        longitude = Gtk.Entry()
        longitude.set_tooltip_text( _( "Longitude of your location in decimal degrees." ) )
        box.pack_start( longitude, False, False, 0 )
        grid.attach( box, 0, 2, 1, 1 )

        box = Gtk.Box( spacing = 6 )

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

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

        dialog.vbox.pack_start( notebook, True, True, 0 )
        dialog.show_all()

        while True:
            responseType = dialog.run()
            if responseType != Gtk.ResponseType.OK:
                break

            cityValue = city.get_active_text()
            if cityValue == "":
                notebook.set_current_page( notebook.get_n_pages() - 1 )
                self.showMessage( dialog, _( "City cannot be empty." ) )
                city.grab_focus()
                continue

            latitudeValue = latitude.get_text().strip()
            if latitudeValue == "" or not self.isNumber( latitudeValue ) or float( latitudeValue ) > 90 or float( latitudeValue ) < -90:
                notebook.set_current_page( notebook.get_n_pages() - 1 )
                self.showMessage( dialog, _( "Latitude must be a number between 90 and -90 inclusive." ) )
                latitude.grab_focus()
                continue

            longitudeValue = longitude.get_text().strip()
            if longitudeValue == "" or not self.isNumber( longitudeValue ) or float( longitudeValue ) > 180 or float( longitudeValue ) < -180:
                notebook.set_current_page( notebook.get_n_pages() - 1 )
                self.showMessage( dialog, _( "Longitude must be a number between 180 and -180 inclusive." ) )
                longitude.grab_focus()
                continue

            elevationValue = elevation.get_text().strip()
            if elevationValue == "" or not self.isNumber( elevationValue ) or float( elevationValue ) > 10000 or float( elevationValue ) < 0:
                notebook.set_current_page( notebook.get_n_pages() - 1 )
                self.showMessage( dialog, _( "Elevation must be a number between 0 and 10000 inclusive." ) )
                elevation.grab_focus()
                continue

            self.indicatorText = self.translateTags( displayTagsStore, False, indicatorText.get_text() )
            self.indicatorTextSeparator = indicatorTextSeparator.get_text()
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
        items = [ [ astrobase.AstroBase.BodyType.MOON, astrobase.AstroBase.NAME_TAG_MOON, astrobase.AstroBase.DATA_TAGS_MOON ],
                  [ astrobase.AstroBase.BodyType.SUN, astrobase.AstroBase.NAME_TAG_SUN, astrobase.AstroBase.DATA_TAGS_SUN ] ]

        for item in items:
            bodyType = item[ 0 ]
            bodyTag = item[ 1 ]
            dataTags = item[ 2 ]
            if ( bodyType, bodyTag, astrobase.AstroBase.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                for dataTag in dataTags:
                    translatedTag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ bodyTag ] + " " + astrobase.AstroBase.DATA_TAGS_TRANSLATIONS[ dataTag ]
                    value = ""
                    key = ( bodyType, bodyTag, dataTag )
                    if key in self.data:
                        value = self.getDisplayData( key )
                        displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, value ] )

        items = [ [ astrobase.AstroBase.BodyType.PLANET, astrobase.AstroBase.PLANETS, astrobase.AstroBase.DATA_TAGS_PLANET ],
                  [ astrobase.AstroBase.BodyType.STAR, astrobase.AstroBase.STARS, astrobase.AstroBase.DATA_TAGS_STAR ] ]

        for item in items:
            bodyType = item[ 0 ]
            bodyTags = item[ 1 ]
            dataTags = item[ 2 ]
            for bodyTag in bodyTags:
                if ( bodyType, bodyTag, astrobase.AstroBase.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                    for dataTag in dataTags:
                        translatedTag = IndicatorLunar.BODY_TAGS_TRANSLATIONS[ bodyTag ] + " " + astrobase.AstroBase.DATA_TAGS_TRANSLATIONS[ dataTag ]
                        value = ""
                        key = ( bodyType, bodyTag, dataTag )
                        if key in self.data:
                            value = self.getDisplayData( key )
                            displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, value ] )

        items = [ [ astrobase.AstroBase.BodyType.COMET, self.cometData, astrobase.AstroBase.DATA_TAGS_COMET ],
                  [ astrobase.AstroBase.BodyType.MINOR_PLANET, self.minorPlanetData, astrobase.AstroBase.DATA_TAGS_MINOR_PLANET ] ]

        for item in items:
            bodyType = item[ 0 ]
            bodyTags = item[ 1 ]
            dataTags = item[ 2 ]
            for bodyTag in bodyTags:
                if ( bodyType, bodyTag, astrobase.AstroBase.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                    for dataTag in dataTags:
                        translatedTag = bodyTag + " " + astrobase.AstroBase.DATA_TAGS_TRANSLATIONS[ dataTag ]
                        value = ""
                        key = ( bodyType, bodyTag, dataTag )
                        if key in self.data:
                            value = self.getDisplayData( key )
                            displayTagsStore.append( [ bodyTag + " " + dataTag, translatedTag, value ] )

        bodyType = astrobase.AstroBase.BodyType.SATELLITE
        for bodyTag in self.satelliteData:
            if ( bodyType, bodyTag, astrobase.AstroBase.DATA_TAG_RISE_AZIMUTH ) in self.data or ( bodyType, bodyTag, astrobase.AstroBase.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                for dataTag in astrobase.AstroBase.DATA_TAGS_SATELLITE:
                    value = ""
                    name = self.satelliteData[ bodyTag ].getName()
                    internationalDesignator = self.satelliteData[ bodyTag ].getInternationalDesignator()
                    translatedTag = name + " : " + bodyTag + " : " + internationalDesignator + " " + astrobase.AstroBase.DATA_TAGS_TRANSLATIONS[ dataTag ]
                    key = ( astrobase.AstroBase.BodyType.SATELLITE, bodyTag, dataTag )
                    if key in self.data:
                        value = self.getDisplayData( key )
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

        def toggleCheckbox( cellRendererToggle, row, listStore ): listStore[ row ][ 0 ] = not listStore[ row ][ 0 ]

        tree = Gtk.TreeView.new_with_model( listStore )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( toolTipText )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", toggleCheckbox, listStore )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = 0 )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, listStore )
        tree.append_column( treeViewColumn )

        tree.append_column( Gtk.TreeViewColumn( columnHeaderText, Gtk.CellRendererText(), text = columnIndex ) )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )

        return scrolledWindow


    def onSatelliteCheckbox( self, cellRendererToggle, row, dataStore, sortStore ):
        actualRow = sortStore.convert_path_to_child_path( Gtk.TreePath.new_from_string( row ) ) # Convert sorted model index to underlying (child) model index.
        dataStore[ actualRow ][ 0 ] = not dataStore[ actualRow ][ 0 ]


    def onColumnHeaderClick( self, treeviewColumn, dataStore ):
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


    def createNotificationPanel( self,
                                 grid, gridStartIndex,
                                 checkboxLabel, checkboxTooltip, checkboxIsActive,
                                 summaryLabel, summaryText, summaryTooltip,
                                 messageLabel, messageText, messageTooltip,
                                 testButtonText, testButtonTooltip,
                                 isMoonNotification ):

        checkbox = Gtk.CheckButton.new_with_label( checkboxLabel )
        checkbox.set_active( checkboxIsActive )
        checkbox.set_tooltip_text( checkboxTooltip )
        grid.attach( checkbox, 0, gridStartIndex, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( self.INDENT_TEXT_LEFT )

        label = Gtk.Label.new( summaryLabel )
        box.pack_start( label, False, False, 0 )

        summaryTextEntry = Gtk.Entry()
        summaryTextEntry.set_text( summaryText )
        summaryTextEntry.set_tooltip_text( summaryTooltip )
        box.pack_start( summaryTextEntry, True, True, 0 )
        box.set_sensitive( checkbox.get_active() )
        grid.attach( box, 0, gridStartIndex + 1, 1, 1 )

        checkbox.connect( "toggled", self.onCheckbox, box )

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
        box.set_sensitive( checkbox.get_active() )
        grid.attach( box, 0, gridStartIndex + 2, 1, 1 )

        checkbox.connect( "toggled", self.onCheckbox, box )

        test = Gtk.Button.new_with_label( testButtonText )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( checkbox.get_active() )
        test.connect( "clicked", self.onTestNotificationClicked, summaryTextEntry, messageTextView, isMoonNotification )
        test.set_tooltip_text( testButtonTooltip )
        grid.attach( test, 0, gridStartIndex + 3, 1, 1 )

        checkbox.connect( "toggled", self.onCheckbox, test )

        return checkbox, summaryTextEntry, messageTextView


    def onTestNotificationClicked( self, button, summaryEntry, messageTextView, isMoonNotification ):
        summary = summaryEntry.get_text()
        message = self.getTextViewText( messageTextView )

        if isMoonNotification:
            svgFile = self.createFullMoonIcon()

        else:
            # Create mock data.
            utcNow = str( datetime.datetime.utcnow() )
            if utcNow.index( '.' ) > -1:
                utcNow = utcNow.split( '.' )[ 0 ] # Remove fractional seconds.

            utcNowPlusTenMinutes = str( datetime.datetime.utcnow() + datetime.timedelta( minutes = 10 ) )
            if utcNowPlusTenMinutes.index( '.' ) > -1:
                utcNowPlusTenMinutes = utcNowPlusTenMinutes.split( '.' )[ 0 ] # Remove fractional seconds.

            def replaceTags( text ): return text. \
                replace( astrobase.AstroBase.SATELLITE_TAG_NAME_TRANSLATION, "ISS (ZARYA)" ). \
                replace( astrobase.AstroBase.SATELLITE_TAG_NUMBER_TRANSLATION, "25544" ). \
                replace( astrobase.AstroBase.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR_TRANSLATION, "1998-067A" ). \
                replace( astrobase.AstroBase.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION, "123°" ). \
                replace( astrobase.AstroBase.SATELLITE_TAG_RISE_TIME_TRANSLATION, self.toLocalDateTimeString( utcNow, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) ). \
                replace( astrobase.AstroBase.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION, "321°" ). \
                replace( astrobase.AstroBase.SATELLITE_TAG_SET_TIME_TRANSLATION, self.toLocalDateTimeString( utcNowPlusTenMinutes, IndicatorLunar.DATE_TIME_FORMAT_HHcolonMM ) )

            summary = replaceTags( summary ) + " " # The notification summary text must not be empty (at least on Unity).
            message = replaceTags( message )
            svgFile = IndicatorLunar.ICON_SATELLITE

        Notify.Notification.new( summary, message, svgFile ).show()


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
            IndicatorLunar.CONFIG_INDICATOR_TEXT_SEPARATOR: self.indicatorTextSeparator,
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