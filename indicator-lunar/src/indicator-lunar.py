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
#
# Due to suspected stale data, computing the apparent magnitude for comets and
# minor planets is no longer reliable.  As such, comet and minor planet
# functionality has been disabled.


#TODO Ensure all files written out (cached download data, images, etc) contain a file extension ( .txt, .svg, ...).


#TODO Given the MPC files for comets and minor planets cannot be used to determine apparent magnitude,
# either drop comets and minor planets, or...
# Find external sources (websites) which use better/reliable data to compute apparent magnitude
# and list the currently visible comets / minor planets (along with the apparent magnitude).
# From this list (should be at most twenty bodies of each type), can then interrogate the MPC
# online ephemeris service to get the orbital elements for these bodies.
# As the CometEls.txt is a small file, could just use that...but if going to the trouble
# for minor planets, may as well do the same for comets...and may be able to get get both in one http transfer.
#
# Do we still need to save orbital elements in different formats (one for PyEphem and one for Skyfield)?
#
# Will need to save a list of the currently visible comets and minor planets (maybe keep in a single list).
#
# Instead of getting the list of visible comets / minor planets from one website,
# maybe get from multiple sites and then take subset/overlap to only show those bodies
# which are deemed visible by several sites (majority rules).
#
# Probably need to update the visibility list weekly at least, maybe every second day.
# Only need the orbital elements on a weekly or even monthly basis.
#
# For asteroids, look at using https://asteroid.lowell.edu/main/astorb/
#
# For comets, hopefully will use https://cobs.si/help/cobs_api/elements_api/ with a new API on the way.


#TODO Consider add an option to show rise/set/az/alt for natural bodies only during night time.
# https://telescopenights.com/stars-in-the-daytime/
# Excludes the sun and moon (maybe mercury?).
# Could either use an hourly window similar to that in satellites, or
# a check box that simply defaults to one hour before sunset and one hour after sunrise as the visible window.
#
# Unsure how, if at all, this interacts with the preference "hide bodies below the horizon".
#
# If this goes ahead, consider moving the start/end hour window functionality out of each backend and into the frontend.
# So calculate the satellite passes and screen out those not within the desired window and calculate again moving the start date/time forward to the next window.
# Continue until the start date/time exceeds a few days (no more than three days or whatever we use in the backend).


INDICATOR_NAME = "indicator-lunar"
import gettext
gettext.install( INDICATOR_NAME )

import gi
gi.require_version( "Gtk", "3.0" )
gi.require_version( "Notify", "0.7" )


from gi.repository import Gtk, Notify
from indicatorbase import IndicatorBase

import datetime, eclipse, locale, math, orbitalelement, re, sys, twolineelement, webbrowser


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
    CONFIG_SATELLITE_LIMIT_START = "satelliteLimitStart"
    CONFIG_SATELLITE_LIMIT_END = "satelliteLimitEnd"
    CONFIG_SATELLITES = "satellites"
    CONFIG_SATELLITES_ADD_NEW = "satellitesAddNew"
    CONFIG_SATELLITES_SORT_BY_DATE_TIME = "satellitesSortByDateTime"
    CONFIG_SHOW_SATELLITE_NOTIFICATION = "showSatelliteNotification"
    CONFIG_SHOW_WEREWOLF_WARNING = "showWerewolfWarning"
    CONFIG_STARS = "stars"
    CONFIG_WEREWOLF_WARNING_MESSAGE = "werewolfWarningMessage"
    CONFIG_WEREWOLF_WARNING_SUMMARY = "werewolfWarningSummary"

    DATA_INDEX_BODY_TYPE = 0
    DATA_INDEX_BODY_NAME = 1
    DATA_INDEX_DATA_NAME = 2

    DATE_TIME_FORMAT_HHcolonMM = "%H:%M"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspacespaceHHcolonMM = "%Y-%m-%d  %H:%M"

    EXTENSION_SVG = ".svg" #TODO Put these into Indicator Base?  Where else are extensions used?
    EXTENSION_TEXT = ".txt"

    ICON_CACHE_BASENAME = "icon-"
    ICON_CACHE_MAXIMUM_AGE_HOURS = 1 # Keep icons around for an hour to allow multiple instances to run (when testing for example).
    ICON_FULL_MOON = ICON_CACHE_BASENAME + "fullmoon-" # Dynamically created in the user cache directory.
    ICON_SATELLITE = INDICATOR_NAME + "-satellite" # Located in /usr/share/icons

    INDICATOR_TEXT_DEFAULT = " [" + astroBackend.NAME_TAG_MOON + " " + astroBackend.DATA_TAG_PHASE + "]"
    INDICATOR_TEXT_SEPARATOR_DEFAULT = ", "

    DATE_TIME_FORMAT_HHcolonMM = "%H:%M"
    DATE_TIME_FORMAT_YYYYdashMMdashDDspacespaceHHcolonMM = "%Y-%m-%d  %H:%M"

    BODY_TAGS_TRANSLATIONS = dict(
        list( astroBackend.NAME_TAG_MOON_TRANSLATION.items() ) +
        list( astroBackend.PLANET_TAGS_TRANSLATIONS.items() ) +
        list( astroBackend.STAR_TAGS_TRANSLATIONS.items() ) +
        list( astroBackend.NAME_TAG_SUN_TRANSLATION.items() ) )

#TODO For comets, minor planets and satellites,
# given the (eventual) change from binary to text files in the cache,
# likely need to change the cache basename (satellite-tle changes to satellites-tle or similar for example)
# so that old versions can be deleted or figure out how to distinguish a binary file from a text
# and delete if binary.
    COMET_CACHE_BASENAME = "comet-oe-" + astroBackendName.lower() + "-"
    COMET_CACHE_MAXIMUM_AGE_HOURS = 96

    COMET_DATA_URL = "https://www.minorplanetcenter.net/iau/Ephemerides/Comets/"
    if astroBackendName == astroBackendPyEphem:
        COMET_DATA_URL+= "Soft03Cmt.txt"

    else:
        COMET_DATA_URL+= "Soft00Cmt.txt"

    MINOR_PLANET_CACHE_BASENAME = "minorplanet-oe-"
    MINOR_PLANET_CACHE_BASENAME_BRIGHT = MINOR_PLANET_CACHE_BASENAME + "bright-" + astroBackendName.lower() + "-"
    MINOR_PLANET_CACHE_BASENAME_CRITICAL = MINOR_PLANET_CACHE_BASENAME + "critical-" + astroBackendName.lower() + "-"
    MINOR_PLANET_CACHE_BASENAME_DISTANT = MINOR_PLANET_CACHE_BASENAME + "distant-" + astroBackendName.lower() + "-"
    MINOR_PLANET_CACHE_BASENAME_UNUSUAL = MINOR_PLANET_CACHE_BASENAME + "unusual-" + astroBackendName.lower() + "-"

    MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS = 96

    MINOR_PLANET_DATA_URL = "https://minorplanetcenter.net/iau/Ephemerides/"
    if astroBackendName == astroBackendPyEphem:
        MINOR_PLANET_DATA_URL_BRIGHT = MINOR_PLANET_DATA_URL + "Bright/2018/Soft03Bright.txt"
        MINOR_PLANET_DATA_URL_CRITICAL = MINOR_PLANET_DATA_URL + "CritList/Soft03CritList.txt"
        MINOR_PLANET_DATA_URL_DISTANT = MINOR_PLANET_DATA_URL + "Distant/Soft03Distant.txt"
        MINOR_PLANET_DATA_URL_UNUSUAL = MINOR_PLANET_DATA_URL + "Unusual/Soft03Unusual.txt"

    else:
        MINOR_PLANET_DATA_URL_BRIGHT = MINOR_PLANET_DATA_URL + "Bright/2018/Soft00Bright.txt"
        MINOR_PLANET_DATA_URL_CRITICAL = MINOR_PLANET_DATA_URL + "CritList/Soft00CritList.txt"
        MINOR_PLANET_DATA_URL_DISTANT = MINOR_PLANET_DATA_URL + "Distant/Soft00Distant.txt"
        MINOR_PLANET_DATA_URL_UNUSUAL = MINOR_PLANET_DATA_URL + "Unusual/Soft00Unusual.txt"

    SATELLITE_CACHE_BASENAME = "satellite-tle-"
    SATELLITE_CACHE_MAXIMUM_AGE_HOURS = 48
    SATELLITE_DATA_URL = "https://celestrak.com/NORAD/elements/visual.txt"
    SATELLITE_NOTIFICATION_MESSAGE_DEFAULT = \
        _( "Rise Time: " ) + astroBackend.SATELLITE_TAG_RISE_TIME_TRANSLATION + "\n" + \
        _( "Rise Azimuth: " ) + astroBackend.SATELLITE_TAG_RISE_AZIMUTH_TRANSLATION + "\n\n" + \
        _( "Set Time: " ) + astroBackend.SATELLITE_TAG_SET_TIME_TRANSLATION + "\n" + \
        _( "Set Azimuth: " ) + astroBackend.SATELLITE_TAG_SET_AZIMUTH_TRANSLATION
    SATELLITE_NOTIFICATION_SUMMARY_DEFAULT = \
        astroBackend.SATELLITE_TAG_NAME + " : " + \
        astroBackend.SATELLITE_TAG_NUMBER + " : " + \
        astroBackend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR + _( " now rising..." )

    # Satellite menu contains the satellite number then name,
    # followed by other items depending on the satellite's status
    # (rising, in transit or always up).
    SATELLITE_MENU_NUMBER = 0
    SATELLITE_MENU_NAME = 1

    SATELLITE_MENU_RISE_DATE_TIME = 2
    SATELLITE_MENU_RISE_AZIMUTH = 3
    SATELLITE_MENU_SET_DATE_TIME = 4
    SATELLITE_MENU_SET_AZIMUTH = 5

    SATELLITE_MENU_AZIMUTH = 2 
    SATELLITE_MENU_ALTITUDE = 3

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
            version = "1.0.93",
            copyrightStartYear = "2012",
            comments = _( "Displays lunar, solar, planetary, comet, minor planet, star and satellite information." ),
#TODO Remove the eclipse credit if/when moving exclusively to Skyfield and Skyfield computes solar eclipses.
#TODO Temporarily remove credit for comets and minor planets.
            # creditz =
            #     [ IndicatorLunar.astroBackend.getCredit(),
            #     _( "Eclipse information by Fred Espenak and Jean Meeus. https://eclipse.gsfc.nasa.gov" ),
            #     _( "Satellite TLE data by Dr T S Kelso. https://www.celestrak.com" ),
            #     _( "Comet and Minor Planet OE data by Minor Planet Center. https://www.minorplanetcenter.net" ) ] )
            creditz =
                [ IndicatorLunar.astroBackend.getCredit(),
                _( "Eclipse information by Fred Espenak and Jean Meeus. https://eclipse.gsfc.nasa.gov" ),
                _( "Satellite TLE data by Dr T S Kelso. https://www.celestrak.com" ) ] )

        self.debug = True #TODO Testing

        # Dictionary to hold currently calculated (and previously calculated) astronomical data.
        # Key is a combination of three tags: body type, body name and data name.
        # Value is a string, regardless being numerical or not.
        # Previous data is used for satellite transits.
        self.data = None
        self.dataPrevious = None

        self.cometData = { } # Key: comet name, upper cased; Value: orbitalelement.OE object.  Can be empty but never None.
        self.minorPlanetData = { } # Key: minor planet name, upper cased; Value: orbitalelement.OE object.  Can be empty but never None.
        self.satelliteData = { } # Key: satellite number; Value: twolineelement.TLE object.  Can be empty but never None.
        self.satellitePreviousNotifications = [ ]

        self.lastFullMoonNotfication = datetime.datetime.utcnow() - datetime.timedelta( hours = 1 )

        self.__removeCacheFilesVersion89() # Cache data filenames changed in version 90, so remove old versions.
        self.flushTheCache()
        self.initialiseDownloadCountsAndCacheDateTimes()


    def __removeCacheFilesVersion89( self ):
        self.flushCache( "comet-oe-", 0 )
        self.flushCache( "minorplanet-oe-bright-", 0 )
        self.flushCache( "minorplanet-oe-critical-", 0 )
        self.flushCache( "minorplanet-oe-distant-", 0 )
        self.flushCache( "minorplanet-oe-unusual-", 0 )


    def flushTheCache( self ):
        self.flushCache( IndicatorLunar.ICON_CACHE_BASENAME, IndicatorLunar.ICON_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.ICON_FULL_MOON, IndicatorLunar.ICON_CACHE_MAXIMUM_AGE_HOURS ) #TODO Hopefully moon will become a regular, timestamped icon/file and so can remove this.
        self.flushCache( IndicatorLunar.COMET_CACHE_BASENAME, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_BRIGHT, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_CRITICAL, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_DISTANT, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_UNUSUAL, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS )
        self.flushCache( IndicatorLunar.SATELLITE_CACHE_BASENAME, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS )


    def initialiseDownloadCountsAndCacheDateTimes( self ):
        utcNow = datetime.datetime.utcnow() 

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

        self.cacheDateTimeComet = self.getCacheDateTime( 
            IndicatorLunar.COMET_CACHE_BASENAME, 
            utcNow - datetime.timedelta( hours = ( IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )

        self.cacheDateTimeMinorPlanetBright = self.getCacheDateTime( 
            IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_BRIGHT, 
            utcNow - datetime.timedelta( hours = ( IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )

        self.cacheDateTimeMinorPlanetCritical = self.getCacheDateTime( 
            IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_CRITICAL, 
            utcNow - datetime.timedelta( hours = ( IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )

        self.cacheDateTimeMinorPlanetDistant = self.getCacheDateTime( 
            IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_DISTANT, 
            utcNow - datetime.timedelta( hours = ( IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )

        self.cacheDateTimeMinorPlanetUnusual = self.getCacheDateTime( 
            IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_UNUSUAL, 
            utcNow - datetime.timedelta( hours = ( IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )

        self.cacheDateTimeSatellite = self.getCacheDateTime( 
            IndicatorLunar.SATELLITE_CACHE_BASENAME, 
            utcNow - datetime.timedelta( hours = ( IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS * 2 ) ) )


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
            self.satellites, self.satelliteData, self.convertLocalHourToUTC( self.satelliteLimitStart ), self.convertLocalHourToUTC( self.satelliteLimitEnd ),
            self.comets, self.cometData,
            self.minorPlanets, self.minorPlanetData,
            self.magnitude,
            self.getLogging() )

        if self.dataPrevious is None: # Happens only on first run.
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
        if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendSkyfield:
            dataType = orbitalelement.OE.DataType.SKYFIELD_COMET
            magnitudeFilterAdditionalArguments = [ IndicatorLunar.astroBackend.BodyType.COMET, self.latitude, self.longitude, self.elevation, self.getLogging() ]

        else:
            dataType = orbitalelement.OE.DataType.XEPHEM_COMET
            magnitudeFilterAdditionalArguments = [ ]

        # self.cometData, self.cacheDateTimeComet, self.downloadCountComet, self.nextDownloadTimeComet = self.__updateData( 
        #     utcNow,
        #     self.cacheDateTimeComet, IndicatorLunar.COMET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.COMET_CACHE_BASENAME,
        #     orbitalelement.download, [ IndicatorLunar.COMET_DATA_URL, dataType, self.getLogging() ],
        #     self.downloadCountComet, self.nextDownloadTimeComet,
        #     IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )

        # if self.cometsAddNew:
        #     self.addNewBodies( self.cometData, self.comets )

        # Update minor planet data.
        self.minorPlanetData = { }
        magnitudeFilterAdditionalArguments = [ ]
        dataType = orbitalelement.OE.DataType.XEPHEM_MINOR_PLANET
        if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendSkyfield:
            dataType = orbitalelement.OE.DataType.SKYFIELD_MINOR_PLANET
            magnitudeFilterAdditionalArguments = [ IndicatorLunar.astroBackend.BodyType.MINOR_PLANET, self.latitude, self.longitude, self.elevation, self.getLogging() ]

        else:
            dataType = orbitalelement.OE.DataType.XEPHEM_MINOR_PLANET
            magnitudeFilterAdditionalArguments = [ ]

        # minorPlanetData, self.cacheDateTimeMinorPlanetBright, self.downloadCountMinorPlanetBright, self.nextDownloadTimeMinorPlanetBright = self.__updateData( 
        #     utcNow,
        #     self.cacheDateTimeMinorPlanetBright, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_BRIGHT,
        #     orbitalelement.download, [ IndicatorLunar.MINOR_PLANET_DATA_URL_BRIGHT, dataType, self.getLogging() ],
        #     self.downloadCountMinorPlanetBright, self.nextDownloadTimeMinorPlanetBright,
        #     IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )
        
        # self.minorPlanetData.update( minorPlanetData )
        
        # minorPlanetData, self.cacheDateTimeMinorPlanetCritical, self.downloadCountMinorPlanetCritical, self.nextDownloadTimeMinorPlanetCritical = self.__updateData( 
        #     utcNow,
        #     self.cacheDateTimeMinorPlanetCritical, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_CRITICAL,
        #     orbitalelement.download, [ IndicatorLunar.MINOR_PLANET_DATA_URL_CRITICAL, dataType, self.getLogging( )],
        #     self.downloadCountMinorPlanetCritical, self.nextDownloadTimeMinorPlanetCritical,
        #     IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )
        
        # self.minorPlanetData.update( minorPlanetData )
        
        # minorPlanetData, self.cacheDateTimeMinorPlanetDistant, self.downloadCountMinorPlanetDistant, self.nextDownloadTimeMinorPlanetDistant = self.__updateData( 
        #     utcNow,
        #     self.cacheDateTimeMinorPlanetDistant, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_DISTANT,
        #     orbitalelement.download, [ IndicatorLunar.MINOR_PLANET_DATA_URL_DISTANT, dataType, self.getLogging( ) ],
        #     self.downloadCountMinorPlanetDistant, self.nextDownloadTimeMinorPlanetDistant,
        #     IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )
        
        # self.minorPlanetData.update( minorPlanetData )

        # minorPlanetData, self.cacheDateTimeMinorPlanetUnusual, self.downloadCountMinorPlanetUnusual, self.nextDownloadTimeMinorPlanetUnusual = self.__updateData( 
        #     utcNow,
        #     self.cacheDateTimeMinorPlanetUnusual, IndicatorLunar.MINOR_PLANET_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.MINOR_PLANET_CACHE_BASENAME_UNUSUAL,
        #     orbitalelement.download, [ IndicatorLunar.MINOR_PLANET_DATA_URL_UNUSUAL, dataType, self.getLogging( ) ],
        #     self.downloadCountMinorPlanetUnusual, self.nextDownloadTimeMinorPlanetUnusual,
        #     IndicatorLunar.astroBackend.getOrbitalElementsLessThanMagnitude, magnitudeFilterAdditionalArguments )

        # self.minorPlanetData.update( minorPlanetData )

        # if self.minorPlanetsAddNew:
        #     self.addNewBodies( self.minorPlanetData, self.minorPlanets )

        # Update satellite data.
        self.satelliteData, self.cacheDateTimeSatellite, self.downloadCountSatellite, self.nextDownloadTimeSatellite = self.__updateData( 
            utcNow,
            self.cacheDateTimeSatellite, IndicatorLunar.SATELLITE_CACHE_MAXIMUM_AGE_HOURS, IndicatorLunar.SATELLITE_CACHE_BASENAME,
            twolineelement.download, [ IndicatorLunar.SATELLITE_DATA_URL, self.getLogging() ],
            self.downloadCountSatellite,self.nextDownloadTimeSatellite,
            None, [ ] )

        if self.satellitesAddNew:
            self.addNewBodies( self.satelliteData, self.satellites )


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


    # Get the data from the cache, or if stale, download from the source.
    #
    # Returns a dictionary (may be empty). #TODO Update this!
#TODO Maybe reverse the sense of this function...
# Download first (if needed) then save to cache (run magnitude filtering if specified).
# Read from cache (if needed)
# Return data (assuming data was passed in and can be just returned if no download and no cache read is required).
#
#TODO Need to take into account when the indicator is running for some time (longer than a cache interval)...?
# Need to always check the cache before just simply just sending back the passed in data (and may need to do a fresh download)?
#If this logic is valid, implement first before any minor planet / comet changes. 
    def __updateData(
            self, utcNow,
            cacheDateTime, cacheMaximumAge, cacheBaseName,
            downloadDataFunction, downloadDataArguments,
            downloadCount, nextDownloadTime,
            magnitudeFilterFunction, magnitudeFilterAdditionalArguments ):

        if utcNow < ( cacheDateTime + datetime.timedelta( hours = cacheMaximumAge ) ):
#TODO Change to readCacheTextWithTimestamp()
            data = self.readCacheBinary( cacheBaseName )

        else:
            data = { }
            if nextDownloadTime < utcNow:
                data = downloadDataFunction( *downloadDataArguments )
                downloadCount += 1
                if data:
                    if magnitudeFilterFunction:
                        data = magnitudeFilterFunction( utcNow, data, IndicatorLunar.astroBackend.MAGNITUDE_MAXIMUM, *magnitudeFilterAdditionalArguments )

                    self.writeCacheBinary( cacheBaseName, data ) #TODO Change to writeCacheTextWithTimestamp()
                    downloadCount = 0
                    cacheDateTime = self.getCacheDateTime( cacheBaseName )
                    nextDownloadTime = utcNow + datetime.timedelta( hours = cacheMaximumAge )
 
                else:
                    nextDownloadTime = self.getNextDownloadTime( utcNow, downloadCount ) # Download failed for some reason; retry at a later time...
 
        return data, cacheDateTime, downloadCount, nextDownloadTime


#TODO Not finished and likely very wrong...wait until comet and minor planet new sources are found and settled upon.
    def __updateDataNEW(
            self, utcNow, data,
            cacheDateTime, cacheMaximumAge, cacheBaseName, cacheExtension,
            downloadCount, nextDownloadTime,
            downloadDataFunction, downloadDataArguments,
            formatConversionFunction,
            magnitudeFilterFunction, magnitudeFilterAdditionalArguments,
            toTextFunction, toTextAdditionalArgunemts,
            toObjectFunction, toObjectAdditionalArgunemts ):

        if ( cacheDateTime + datetime.timedelta( hours = cacheMaximumAge ) ) < utcNow: # Cache is stale.
            downloadedData = { }
            if nextDownloadTime < utcNow: # Download is overdue.
                downloadedData = downloadDataFunction( *downloadDataArguments )
                downloadCount += 1
                if downloadedData:
                    # if formatConversionFunction:
                    #     downloadedData = formatConversionFunction( downloadedData )
                    #
                    # if magnitudeFilterFunction:
                    #     downloadedData = magnitudeFilterFunction( utcNow, downloadedData, IndicatorLunar.astroBackend.MAGNITUDE_MAXIMUM, *magnitudeFilterAdditionalArguments )

                    self.writeCacheTextWithTimestamp( toTextFunction( downloadedData, *toTextAdditionalArgunemts ), cacheBaseName, cacheExtension )
                    downloadCount = 0
                    cacheDateTime = self.getCacheDateTime( cacheBaseName )
                    nextDownloadTime = utcNow + datetime.timedelta( hours = cacheMaximumAge )
                    data = downloadedData

                else:
                    nextDownloadTime = self.getNextDownloadTime( utcNow, downloadCount ) # Download failed for some reason; retry at a later time...

        else: # Cache is fresh.
            if not data: # No data passed in, so read from cache.
                data = toObjectFunction( self.readCacheTextWithTimestamp( cacheBaseName, cacheExtension ), *toObjectAdditionalArgunemts )

        return data, cacheDateTime, downloadCount, nextDownloadTime


    def getNextDownloadTime( self, utcNow, downloadCount ):
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
        self.updateMenuPlanets( menu )
        self.updateMenuStars( menu )
        self.updateMenuCometsMinorPlanets( menu, IndicatorLunar.astroBackend.BodyType.COMET )
        self.updateMenuCometsMinorPlanets( menu, IndicatorLunar.astroBackend.BodyType.MINOR_PLANET)
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
        svgIconText = self.createIconText( lunarIlluminationPercentage, lunarBrightLimbAngleInDegrees )
        iconFilename = self.writeCacheTextWithTimestamp( svgIconText, IndicatorLunar.ICON_CACHE_BASENAME, IndicatorLunar.EXTENSION_SVG )
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

            self.createFullMoonIcon()
            Notify.Notification.new( summary, self.werewolfWarningMessage, IndicatorLunar.ICON_FULL_MOON ).show()
            self.lastFullMoonNotfication = utcNow


#TODO The full moon icon does appear in the notification (at least in the previous release).
#TODO Why give the full moon icon it's own name?  Can't the format of icon-YYYYMMDDHHMMSS.svg be used?
    def createFullMoonIcon( self ):
        return self.writeCacheText( self.createIconText( 100, None ), IndicatorLunar.ICON_FULL_MOON + IndicatorLunar.EXTENSION_SVG )


    def notificationSatellites( self ):
        utcNow = datetime.datetime.utcnow()

        INDEX_NUMBER = 0
        INDEX_RISE_TIME = 1
        satelliteCurrentNotifications = [ ]

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
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NAME, self.satelliteData[ number ].getName() ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NUMBER, self.satelliteData[ number ].getNumber() ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satelliteData[ number ].getInternationalDesignator() ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_TIME, riseTime ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_TIME, setTime ) + \
                " " # The notification summary text must not be empty (at least on Unity).

            message = \
                self.satelliteNotificationMessage. \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NAME, self.satelliteData[ number ].getName() ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_NUMBER, self.satelliteData[ number ].getNumber() ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_INTERNATIONAL_DESIGNATOR, self.satelliteData[ number ].getInternationalDesignator() ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_AZIMUTH, riseAzimuth ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_RISE_TIME, riseTime ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_AZIMUTH, setAzimuth ). \
                replace( IndicatorLunar.astroBackend.SATELLITE_TAG_SET_TIME, setTime )

            Notify.Notification.new( summary, message, IndicatorLunar.ICON_SATELLITE ).show()


    def updateMenuMoon( self, menu ):
        key = ( IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON )
        if self.display( IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON ):
            menuItem = self.createMenuItem( menu, _( "Moon" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            self.updateMenuCommon( subMenu, IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON, 1, IndicatorLunar.SEARCH_URL_MOON )

            self.createMenuItem(
                subMenu,
                self.getMenuIndent( 1 ) + \
                _( "Phase: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_PHASE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_PHASE, ) ] ),
                IndicatorLunar.SEARCH_URL_MOON )

            self.createMenuItem( subMenu, self.getMenuIndent( 1 ) + _( "Next Phases" ), IndicatorLunar.SEARCH_URL_MOON )

            # Determine which phases occur by date rather than using the phase calculated.
            # The phase (illumination) rounds numbers and so a given phase is entered earlier than what is correct.
            INDEX_KEY = 0
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

            indent = self.getMenuIndent( 2 )
            for dateTime, displayText, key in sorted( nextPhases, key = lambda pair: pair[ INDEX_KEY ] ):
                self.createMenuItem(
                    subMenu,
                    indent + \
                    displayText + \
                    self.formatData( key[ IndicatorLunar.DATA_INDEX_DATA_NAME ], self.data[ key ] ),
                    IndicatorLunar.SEARCH_URL_MOON )

            self.updateMenuEclipse( subMenu, IndicatorLunar.astroBackend.BodyType.MOON, IndicatorLunar.astroBackend.NAME_TAG_MOON, IndicatorLunar.SEARCH_URL_MOON )


    def updateMenuSun( self, menu ):
        key = ( IndicatorLunar.astroBackend.BodyType.SUN, IndicatorLunar.astroBackend.NAME_TAG_SUN )
        if self.display( IndicatorLunar.astroBackend.BodyType.SUN, IndicatorLunar.astroBackend.NAME_TAG_SUN ):
            menuItem = self.createMenuItem( menu, _( "Sun" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            self.updateMenuCommon( subMenu, IndicatorLunar.astroBackend.BodyType.SUN, IndicatorLunar.astroBackend.NAME_TAG_SUN, 1, IndicatorLunar.SEARCH_URL_SUN )

            self.createMenuItem(
                subMenu,
                self.getMenuIndent( 1 ) + \
                _( "Equinox: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_EQUINOX, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_EQUINOX, ) ] ),
                IndicatorLunar.SEARCH_URL_SUN )

            self.createMenuItem(
                subMenu,
                self.getMenuIndent( 1 ) + \
                _( "Solstice: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_SOLSTICE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SOLSTICE, ) ] ),
                IndicatorLunar.SEARCH_URL_SUN )

            self.updateMenuEclipse( subMenu, IndicatorLunar.astroBackend.BodyType.SUN, IndicatorLunar.astroBackend.NAME_TAG_SUN, IndicatorLunar.SEARCH_URL_SUN )


    def updateMenuEclipse( self, menu, bodyType, nameTag, url ):
        key = ( bodyType, nameTag )
        self.createMenuItem( menu, self.getMenuIndent( 1 ) + _( "Eclipse" ), url )

        self.createMenuItem(
            menu,
            self.getMenuIndent( 2 ) + \
            _( "Date/Time: " ) + \
            self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_DATE_TIME, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_DATE_TIME, ) ] ),
            url )

        self.createMenuItem(
            menu,
            self.getMenuIndent( 2 ) + \
            _( "Type: " ) + \
            self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_TYPE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_TYPE, ) ] ),
            url )

        if key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LATITUDE, ) in self.data: # PyEphem uses the NASA Eclipse data which contains latitude/longitude; Skyfield does not.
            latitude = self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LATITUDE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LATITUDE, ) ] )
            longitude = self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LONGITUDE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ECLIPSE_LONGITUDE, ) ] )
            self.createMenuItem( menu, self.getMenuIndent( 2 ) + _( "Latitude/Longitude: " ) + latitude + " " + longitude, url )


    def updateMenuPlanets( self, menu ):
        planets = [ ]
        for planet in self.planets:
            if self.display( IndicatorLunar.astroBackend.BodyType.PLANET, planet ):
                planets.append( [ planet, IndicatorLunar.astroBackend.PLANET_NAMES_TRANSLATIONS[ planet ] ] )

        if planets:
            menuItem = self.createMenuItem( menu, _( "Planets" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for name, translatedName in planets:
                if name == IndicatorLunar.astroBackend.PLANET_PLUTO:
                    url = IndicatorLunar.SEARCH_URL_DWARF_PLANET + name.lower()

                else:
                    url = IndicatorLunar.SEARCH_URL_PLANET + name.lower()

                self.createMenuItem( subMenu, self.getMenuIndent( 1 ) + translatedName, url )
                self.updateMenuCommon( subMenu, IndicatorLunar.astroBackend.BodyType.PLANET, name, 2, url )
                separator = Gtk.SeparatorMenuItem()
                subMenu.append( separator )

            subMenu.remove( separator )


    def updateMenuStars( self, menu ):
        stars = [ ]
        for star in self.stars:
            if self.display( IndicatorLunar.astroBackend.BodyType.STAR, star ):
                stars.append( [ star, IndicatorLunar.astroBackend.STAR_NAMES_TRANSLATIONS[ star ] ] )

        if stars:
            menuItem = self.createMenuItem( menu, _( "Stars" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            for name, translatedName in stars:
                url = IndicatorLunar.SEARCH_URL_STAR + str( IndicatorLunar.astroBackend.STARS_TO_HIP[ name ] )
                self.createMenuItem( subMenu, self.getMenuIndent( 1 ) + translatedName, url )
                self.updateMenuCommon( subMenu, IndicatorLunar.astroBackend.BodyType.STAR, name, 2, url )
                separator = Gtk.SeparatorMenuItem()
                subMenu.append( separator )

            subMenu.remove( separator )


    def updateMenuCometsMinorPlanets( self, menu, bodyType ):
        orbitalElements = [ ]
        for body in ( self.comets if bodyType == IndicatorLunar.astroBackend.BodyType.COMET else self.minorPlanets ):
            if self.display( bodyType, body ):
                orbitalElements.append( body )

        if orbitalElements:
            menuItem = self.createMenuItem( menu, _( "Comets" ) if bodyType == IndicatorLunar.astroBackend.BodyType.COMET else _( "Minor Planets" ) )
            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )
            if bodyType == IndicatorLunar.astroBackend.BodyType.COMET:
                data = self.cometData
                designationFunction = IndicatorLunar.astroBackend.getDesignationComet
                dataType = orbitalelement.OE.DataType.XEPHEM_COMET \
                    if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendPyEphem else orbitalelement.OE.DataType.SKYFIELD_COMET

            else: # MINOR_PLANET
                data = self.minorPlanetData
                designationFunction = IndicatorLunar.astroBackend.getDesignationMinorPlanet
                dataType = orbitalelement.OE.DataType.XEPHEM_MINOR_PLANET \
                    if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendPyEphem else orbitalelement.OE.DataType.SKYFIELD_MINOR_PLANET

            for name in sorted( orbitalElements ):
                humanReadableName = orbitalelement.getName( data[ name ].getData(), dataType )
                url = IndicatorLunar.SEARCH_URL_COMET_AND_MINOR_PLANET + designationFunction( humanReadableName )
                self.createMenuItem( subMenu, self.getMenuIndent( 1 ) + humanReadableName, url )
                self.updateMenuCommon( subMenu, bodyType, name, 2, url )
                separator = Gtk.SeparatorMenuItem()
                subMenu.append( separator )

            subMenu.remove( separator )


    # Determine if a body should be displayed taking into account:
    #
    #    The user preference for hiding a body if the body is below the horizon.
    #
    #    The astro backend behaviour:
    #        The rise/set/az/alt is present for a body which rises and sets.
    #        The az/alt is present for a body 'always up'.
    #        No data is present for a body 'never up'.
    def display( self, bodyType, bodyName ):
        displayBody = False
        key = ( bodyType, bodyName )
        if key + ( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, ) in self.data: # Body will rise or set or is 'always up'.
            displayBody = True
            if key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) in self.data:
                if self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] < self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ]:
                    displayBody = not self.hideBodiesBelowHorizon

        return displayBody


    def updateMenuCommon( self, menu, bodyType, nameTag, indent, onClickURL = "" ):
        key = ( bodyType, nameTag )
        indent = self.getMenuIndent( indent )
        if key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) in self.data: # Implies this body rises/sets (not always up).
            if self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] < self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ]:
                self.createMenuItem(
                    menu,
                    indent + \
                    _( "Rise: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] ),
                    onClickURL )

            else:
                self.createMenuItem(
                    menu,
                    indent + \
                    _( "Azimuth: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, ) ] ),
                    onClickURL )
        
                self.createMenuItem(
                    menu,
                    indent + \
                    _( "Altitude: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, ) ] ),
                    onClickURL )
        
                self.createMenuItem(
                    menu,
                    indent + \
                    _( "Set: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ] ),
                    onClickURL )
        
        else: # Body is always up.
            self.createMenuItem(
                menu,
                indent + \
                _( "Azimuth: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, ) ] ),
                onClickURL )
        
            self.createMenuItem(
                menu,
                indent + \
                _( "Altitude: " ) + \
                self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, ) ] ),
                onClickURL )


    # Display the rise/set information for each satellite.
    #
    # If a satellite is in transit OR will rise within the next five minutes, show the rise and set information.
    # Otherwise, just show the next rise. 
    #
    # Next rise/set relative to UTC now:
    #
    #                            R       S                           Satellite will rise within the five minute window; display rise/set information.
    #                            R               S                   Satellite will rise within the five minute window; display rise/set information.
    #                                            R       S           Satellite will rise after five minute window; display rise information.  Check for a previous transit.
    #                   ^                    ^
    #                utcNow             utcNow + 5
    #
    # When ( R < utcNow + 5 ) display rise/set information.
    # Otherwise, display rise information.
    #
    # Previous rise/set relative to UTC now:
    #
    #    R       S                                                   Satellite has set; look to next transit.
    #    R                       S                                   Satellite in transit; display rise/set information.
    #    R                                           S               Satellite in transit; display rise/set information.
    #                            R       S                           Satellite will rise within the five minute window; display rise/set information.
    #                            R                   S               Satellite will rise within the five minute window; display rise/set information.
    #                                                R       S       Satellite will rise after five minute window; display rise information.
    #                   ^                    ^
    #                utcNow             utcNow + 5
    #
    # When ( R < utcNow + 5 ) AND ( S > utcNow ) display rise/set information.
    def updateMenuSatellites( self, menu, utcNow ):
        satellites = [ ]
        satellitesPolar = [ ]
        now = IndicatorLunar.astroBackend.toDateTimeString( utcNow )
        nowPlusFiveMinutes = IndicatorLunar.astroBackend.toDateTimeString( utcNow + datetime.timedelta( minutes = 5 ) )
        visibleStartHour, visibleEndHour = IndicatorLunar.astroBackend.getAdjustedDateTime(
            utcNow.replace( tzinfo = datetime.timezone.utc ),
            utcNow.replace( tzinfo = datetime.timezone.utc ) + datetime.timedelta( days = 1 ),
            self.satelliteLimitStart,
            self.satelliteLimitEnd )

        for number in self.satellites:
            key = ( IndicatorLunar.astroBackend.BodyType.SATELLITE, number )
            if key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) in self.data: # Satellite rises/sets...
                if self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] < nowPlusFiveMinutes: # Satellite will rise within the next five minutes...
                    satellites.append( [
                        number,
                        self.satelliteData[ number ].getName(),
                        self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ],
                        self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH, ) ],
                        self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ],
                        self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_AZIMUTH, ) ] ] )

                else: # Satellite will rise five minutes or later from now; look at previous rise to see if the satellite is in transit and within start/end hour...
                    if key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) in self.dataPrevious:
                        inTransit = \
                            self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] < nowPlusFiveMinutes and \
                            self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ] > now

                        # If the user changed the hourly start/end between previous calculation and now, the previous pass may now be invalid, so cannot use it.
                        withinLimit = \
                            self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] >= IndicatorLunar.astroBackend.toDateTimeString( visibleStartHour ) and \
                            self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ] <= IndicatorLunar.astroBackend.toDateTimeString( visibleEndHour )

                        if inTransit and withinLimit:
                            satellites.append( [
                                number,
                                self.satelliteData[ number ].getName(), 
                                self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ],
                                self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH, ) ],
                                self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, ) ],
                                self.dataPrevious[ key + ( IndicatorLunar.astroBackend.DATA_TAG_SET_AZIMUTH, ) ] ] )

                        else: # Previous transit is complete or invalid, so show next pass...
                            satellites.append( [
                                number,
                                self.satelliteData[ number ].getName(),
                                self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] ] )

                    else: # No previous transit (this should not happen), so show next pass...
                        satellites.append( [
                            number,
                            self.satelliteData[ number ].getName(),
                            self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, ) ] ] )

            elif key + ( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, ) in self.data: # Satellite is circumpolar (always up)...
                satellitesPolar.append( [
                    number,
                    self.satelliteData[ number ].getName(),
                    self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, ) ],
                    self.data[ key + ( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, ) ] ] )

        if satellites:
            if self.satellitesSortByDateTime:
                satellites = sorted(
                    satellites,
                    key = lambda x: ( x[ IndicatorLunar.SATELLITE_MENU_RISE_DATE_TIME ], x[ IndicatorLunar.SATELLITE_MENU_NAME ], x[ IndicatorLunar.SATELLITE_MENU_NUMBER ] ) )

            else: # Sort by name/number.
                satellites = sorted(
                    satellites,
                    key = lambda x: ( x[ IndicatorLunar.SATELLITE_MENU_NAME ], x[ IndicatorLunar.SATELLITE_MENU_NUMBER ] ) ) # Sort by name then number.

            self.__updateMenuSatellites( menu, _( "Satellites" ), satellites )

        if satellitesPolar:
            satellitesPolar = sorted(
                satellitesPolar,
                key = lambda x: ( x[ IndicatorLunar.SATELLITE_MENU_NAME ], x[ IndicatorLunar.SATELLITE_MENU_NUMBER ] ) ) # Sort by name then number.

            self.__updateMenuSatellites( menu, _( "Satellites (Polar)" ), satellitesPolar )


    def __updateMenuSatellites( self, menu, label, satellites ):
        menuItem = self.createMenuItem( menu, label )
        subMenu = Gtk.Menu()
        menuItem.set_submenu( subMenu )
        for info in satellites:
            number = info[ IndicatorLunar.SATELLITE_MENU_NUMBER ]
            name = info[ IndicatorLunar.SATELLITE_MENU_NAME ]
            key = ( IndicatorLunar.astroBackend.BodyType.SATELLITE, number )
            url = IndicatorLunar.SEARCH_URL_SATELLITE + number
            menuItem = self.createMenuItem( subMenu, self.getMenuIndent( 1 ) + name + " : " + number + " : " + self.satelliteData[ number ].getInternationalDesignator(), url )
            if len( info ) == 3: # Satellite yet to rise.
                self.createMenuItem(
                    subMenu,
                    self.getMenuIndent( 2 ) + \
                    _( "Rise Date/Time: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, info[ IndicatorLunar.SATELLITE_MENU_RISE_DATE_TIME ] ),
                    url )

            elif len( info ) == 4: # Circumpolar (always up).
                self.createMenuItem(
                    subMenu,
                    self.getMenuIndent( 2 ) + \
                    _( "Azimuth: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH, info[ IndicatorLunar.SATELLITE_MENU_AZIMUTH ] ) ,
                    url )

                self.createMenuItem(
                    subMenu,
                    self.getMenuIndent( 2 ) + \
                    _( "Altitude: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_ALTITUDE, info[ IndicatorLunar.SATELLITE_MENU_ALTITUDE ] ),
                    url )

            else: # Satellite is in transit.
                self.createMenuItem( subMenu, self.getMenuIndent( 2 ) + _( "Rise" ), url )

                self.createMenuItem(
                    subMenu,
                    self.getMenuIndent( 3 ) + \
                    _( "Date/Time: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_RISE_DATE_TIME, info[ IndicatorLunar.SATELLITE_MENU_RISE_DATE_TIME ] ),
                    url )

                self.createMenuItem(
                    subMenu,
                    self.getMenuIndent( 3 ) + \
                    _( "Azimuth: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH, info[ IndicatorLunar.SATELLITE_MENU_RISE_AZIMUTH ] ),
                    url )

                self.createMenuItem( subMenu, self.getMenuIndent( 2 ) + _( "Set" ), url )

                self.createMenuItem(
                    subMenu,
                    self.getMenuIndent( 3 ) + \
                     _( "Date/Time: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_SET_DATE_TIME, info[ IndicatorLunar.SATELLITE_MENU_SET_DATE_TIME ] ),
                    url )

                self.createMenuItem(
                    subMenu,
                    self.getMenuIndent( 3 ) + \
                    _( "Azimuth: " ) + \
                    self.formatData( IndicatorLunar.astroBackend.DATA_TAG_SET_AZIMUTH, info[ IndicatorLunar.SATELLITE_MENU_SET_AZIMUTH ] ),
                    url )

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
    def convertLocalHourToUTC( self, localHour ):
        return datetime.datetime.now().replace( hour = localHour ).astimezone( datetime.timezone.utc ).hour


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

        hideBodiesBelowTheHorizonCheckbutton = Gtk.CheckButton.new_with_label( _( "Hide bodies below the horizon" ) )
        hideBodiesBelowTheHorizonCheckbutton.set_active( self.hideBodiesBelowHorizon )
        hideBodiesBelowTheHorizonCheckbutton.set_tooltip_text( _(
            "If checked, all bodies below the horizon\n" + \
            "are hidden (excludes satellites)." ) )
        grid.attach( hideBodiesBelowTheHorizonCheckbutton, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_left( 5 )
        box.set_margin_top( 5 )

        box.pack_start( Gtk.Label.new( _( "Hide bodies greater than magnitude" ) ), False, False, 0 )
        # toolTip = _( "Planets, stars, comets and minor planets\nexceeding the magnitude will be hidden." ) #TODO May or may not be put back to this.
        toolTip = _( "Planets and stars exceeding the\n magnitude will be hidden." )
        spinnerMagnitude = self.createSpinButton(
            self.magnitude, int( IndicatorLunar.astroBackend.MAGNITUDE_MINIMUM ), int( IndicatorLunar.astroBackend.MAGNITUDE_MAXIMUM ), 1, 5, toolTip )

        box.pack_start( spinnerMagnitude, False, False, 0 )
        grid.attach( box, 0, 1, 1, 1 )

        cometsAddNewCheckbutton = Gtk.CheckButton.new_with_label( _( "Add new comets" ) )
        cometsAddNewCheckbutton.set_margin_top( 5 )
        cometsAddNewCheckbutton.set_active( self.cometsAddNew )
        cometsAddNewCheckbutton.set_tooltip_text( _( "If checked, all comets are added." ) )
        # grid.attach( cometsAddNewCheckbutton, 0, 2, 1, 1 )

        minorPlanetsAddNewCheckbutton = Gtk.CheckButton.new_with_label( _( "Add new minor planets" ) )
        minorPlanetsAddNewCheckbutton.set_margin_top( 5 )
        minorPlanetsAddNewCheckbutton.set_active( self.minorPlanetsAddNew )
        minorPlanetsAddNewCheckbutton.set_tooltip_text( _( "If checked, all minor planets are added." ) )
        # grid.attach( minorPlanetsAddNewCheckbutton, 0, 3, 1, 1 )

        satellitesAddNewCheckbox = Gtk.CheckButton.new_with_label( _( "Add new satellites" ) )
        satellitesAddNewCheckbox.set_margin_top( 5 )
        satellitesAddNewCheckbox.set_active( self.satellitesAddNew )
        satellitesAddNewCheckbox.set_tooltip_text( _( "If checked, all satellites are added." ) )
        grid.attach( satellitesAddNewCheckbox, 0, 4, 1, 1 )

        sortSatellitesByDateTimeCheckbutton = Gtk.CheckButton.new_with_label( _( "Sort satellites by rise date/time" ) )
        sortSatellitesByDateTimeCheckbutton.set_margin_top( 5 )
        sortSatellitesByDateTimeCheckbutton.set_active( self.satellitesSortByDateTime )
        sortSatellitesByDateTimeCheckbutton.set_tooltip_text( _(
            "If checked, satellites are sorted\n" + \
            "by rise date/time.\n\n" + \
            "Otherwise satellites are sorted\n" + \
            "by Name then Number." ) )
        grid.attach( sortSatellitesByDateTimeCheckbutton, 0, 5, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 5 )
        box.set_margin_left( 5 )

        box.pack_start( Gtk.Label.new( _( "Show satellites passes from" ) ), False, False, 0 )

        spinnerSatelliteLimitStart = self.createSpinButton( self.satelliteLimitStart, 0, 23, 1, 4, _( "Show satellite passes after this hour (inclusive)" ) )
        box.pack_start( spinnerSatelliteLimitStart, False, False, 0 )

        box.pack_start( Gtk.Label.new( _( "to" ) ), False, False, 0 )

        spinnerSatelliteLimitEnd = self.createSpinButton( self.satelliteLimitEnd, 0, 23, 1, 4, _( "Show satellite passes before this hour (inclusive)" ) )
        box.pack_start( spinnerSatelliteLimitEnd, False, False, 0 )

        grid.attach( box, 0, 6, 1, 1 )

        notebook.append_page( grid, Gtk.Label.new( _( "Menu" ) ) )

        # Planets/Stars.
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

        box.pack_start( self.createTreeView( planetStore, toolTipText, _( "Planet" ), PLANET_STORE_INDEX_TRANSLATED_NAME ), True, True, 0 )

        stars = [ ] # List of lists, each sublist containing star is checked flag, star name, star translated name.
        for starName in IndicatorLunar.astroBackend.STAR_NAMES_TRANSLATIONS.keys():
            stars.append( [ starName in self.stars, starName, IndicatorLunar.astroBackend.STAR_NAMES_TRANSLATIONS[ starName ] ] )

        STAR_STORE_INDEX_HIDE_SHOW = 0
        STAR_STORE_INDEX_NAME = 1
        STAR_STORE_INDEX_TRANSLATED_NAME = 2
        starStore = Gtk.ListStore( bool, str, str ) # Show/hide, star name (not displayed), star translated name.
        for star in sorted( stars, key = lambda x: ( x[ 2 ] ) ): # Sort by translated star name.
            starStore.append( star )

        toolTipText = _( "Check a star to display in the menu." ) + "\n\n" + \
                      _( "Clicking the header of the first column\n" + \
                         "will toggle all checkboxes." )

        box.pack_start( self.createTreeView( starStore, toolTipText, _( "Star" ), STAR_STORE_INDEX_TRANSLATED_NAME ), True, True, 0 )

        notebook.append_page( box, Gtk.Label.new( _( "Planets / Stars" ) ) )

        # Comets and minor planets.
        box = Gtk.Box( spacing = 20 )

        COMET_STORE_INDEX_HIDE_SHOW = 0
        COMET_STORE_INDEX_NAME = 1
        COMET_STORE_INDEX_HUMAN_READABLE_NAME = 2
        cometStore = Gtk.ListStore( bool, str, str ) # Show/hide, comet name, human readable name.
        dataType = orbitalelement.OE.DataType.XEPHEM_COMET \
            if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendPyEphem else orbitalelement.OE.DataType.SKYFIELD_COMET
        for comet in sorted( self.cometData.keys() ):
            cometStore.append( [ comet in self.comets, comet, orbitalelement.getName( self.cometData[ comet ].getData(), dataType ) ] )

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

        box.pack_start( self.createTreeView( cometStore, toolTipText, _( "Comet" ), COMET_STORE_INDEX_HUMAN_READABLE_NAME ), True, True, 0 )

        MINOR_PLANET_STORE_INDEX_HIDE_SHOW = 0
        MINOR_PLANET_STORE_INDEX_NAME = 1
        MINOR_PLANET_STORE_INDEX_HUMAN_READABLE_NAME = 2
        minorPlanetStore = Gtk.ListStore( bool, str, str ) # Show/hide, minor planet name, human readable name.
        dataType = orbitalelement.OE.DataType.XEPHEM_MINOR_PLANET \
            if IndicatorLunar.astroBackendName == IndicatorLunar.astroBackendPyEphem else orbitalelement.OE.DataType.SKYFIELD_MINOR_PLANET
        for minorPlanet in sorted( self.minorPlanetData.keys() ):
            minorPlanetStore.append( [ minorPlanet in self.minorPlanets, minorPlanet, orbitalelement.getName( self.minorPlanetData[ minorPlanet ].getData(), dataType ) ] )

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

        box.pack_start( self.createTreeView( minorPlanetStore, toolTipText, _( "Minor Planet" ), MINOR_PLANET_STORE_INDEX_HUMAN_READABLE_NAME ), True, True, 0 )

        # notebook.append_page( box, Gtk.Label.new( _( "Comets / Minor Planets" ) ) )

        # Satellites.
        box = Gtk.Box()

        SATELLITE_STORE_INDEX_HIDE_SHOW = 0
        SATELLITE_STORE_INDEX_NAME = 1
        SATELLITE_STORE_INDEX_NUMBER = 2
        SATELLITE_STORE_INDEX_INTERNATIONAL_DESIGNATOR = 3
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
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = SATELLITE_STORE_INDEX_HIDE_SHOW )
        treeViewColumn.set_clickable( True )
        treeViewColumn.connect( "clicked", self.onColumnHeaderClick, satelliteStore )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Name" ), Gtk.CellRendererText(), text = SATELLITE_STORE_INDEX_NAME )
        treeViewColumn.set_sort_column_id( 1 )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Number" ), Gtk.CellRendererText(), text = SATELLITE_STORE_INDEX_NUMBER )
        treeViewColumn.set_sort_column_id( 2 )
        tree.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "International Designator" ), Gtk.CellRendererText(), text = SATELLITE_STORE_INDEX_INTERNATIONAL_DESIGNATOR )
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

        notebook.append_page( grid, Gtk.Label.new( _( "General" ) ) )

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
            self.hideBodiesBelowHorizon = hideBodiesBelowTheHorizonCheckbutton.get_active()
            self.magnitude = spinnerMagnitude.get_value_as_int()
            self.cometsAddNew = cometsAddNewCheckbutton.get_active() # The update will add in new comets.
            self.minorPlanetsAddNew = minorPlanetsAddNewCheckbutton.get_active() # The update will add in new minor planets.
            self.satellitesSortByDateTime = sortSatellitesByDateTimeCheckbutton.get_active()
            self.satellitesAddNew = satellitesAddNewCheckbox.get_active() # The update will add in new satellites.
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
                        self.comets.append( comet[ COMET_STORE_INDEX_NAME ].upper() )

            self.minorPlanets = [ ]
            if not self.minorPlanetsAddNew:
                for minorPlanet in minorPlanetStore:
                    if minorPlanet[ MINOR_PLANET_STORE_INDEX_HIDE_SHOW ]:
                        self.minorPlanets.append( minorPlanet[ MINOR_PLANET_STORE_INDEX_NAME ].upper() )

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
                  [ IndicatorLunar.astroBackend.BodyType.STAR, IndicatorLunar.astroBackend.STARS, IndicatorLunar.astroBackend.DATA_TAGS_STAR ] ]

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

        items = [ [ IndicatorLunar.astroBackend.BodyType.COMET, self.cometData, IndicatorLunar.astroBackend.DATA_TAGS_COMET ],
                  [ IndicatorLunar.astroBackend.BodyType.MINOR_PLANET, self.minorPlanetData, IndicatorLunar.astroBackend.DATA_TAGS_MINOR_PLANET ] ]

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
        for bodyTag in self.satelliteData:
            if ( bodyType, bodyTag, IndicatorLunar.astroBackend.DATA_TAG_RISE_AZIMUTH ) in self.data or ( bodyType, bodyTag, IndicatorLunar.astroBackend.DATA_TAG_AZIMUTH ) in self.data: # Only add this body's attributes if there is data present.
                for dataTag in IndicatorLunar.astroBackend.DATA_TAGS_SATELLITE:
                    value = ""
                    name = self.satelliteData[ bodyTag ].getName()
                    internationalDesignator = self.satelliteData[ bodyTag ].getInternationalDesignator()
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

        def toggleCheckbox( cellRendererToggle, row, listStore ): listStore[ row ][ COLUMN_INDEX_TOGGLE ] = not listStore[ row ][ COLUMN_INDEX_TOGGLE ]

        tree = Gtk.TreeView.new_with_model( listStore )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.set_tooltip_text( toolTipText )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", toggleCheckbox, listStore )
        treeViewColumn = Gtk.TreeViewColumn( "", renderer_toggle, active = COLUMN_INDEX_TOGGLE )
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
            svgFile = self.createFullMoonIcon()

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
                theCity = cities[ 0 ] # No city found, so choose first city by default.

        except Exception as e:
            self.getLogging().exception( e )
            self.getLogging().error( "Error getting default city." )
            theCity = cities[ 0 ] # Some error occurred, so choose first city by default.

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

        self.planets = config.get( IndicatorLunar.CONFIG_PLANETS, IndicatorLunar.astroBackend.PLANETS[ : 6 ] ) # Drop Neptune and Pluto as not visible with naked eye.

        self.satelliteLimitStart = config.get( IndicatorLunar.CONFIG_SATELLITE_LIMIT_START, 16 ) # 4pm
        self.satelliteLimitEnd = config.get( IndicatorLunar.CONFIG_SATELLITE_LIMIT_END, 22 ) # 10pm
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
            IndicatorLunar.CONFIG_SATELLITE_LIMIT_START: self.satelliteLimitStart,
            IndicatorLunar.CONFIG_SATELLITE_LIMIT_END: self.satelliteLimitEnd,
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
