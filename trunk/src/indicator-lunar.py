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


# Application indicator which displays lunar, solar, planetary, star and satellite information.


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html


try: from gi.repository import AppIndicator3 as appindicator
except: pass

from gi.repository import GLib, Gtk

notifyImported = True
try: from gi.repository import Notify
except: notifyImported = False

from urllib.request import urlopen

import copy, datetime, eclipse, gzip, json, locale, logging, math, os, pythonutils, re, satellite, shutil, subprocess, sys

try:
    import ephem
    from ephem.cities import _city_data
    from ephem.stars import stars
except:
    pythonutils.showMessage( None, Gtk.MessageType.ERROR, "You must also install python3-ephem!" )
    sys.exit()


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-lunar"
    VERSION = "1.0.45"
    ICON = NAME
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"
    SVG_ICON = "." + NAME + "-illumination-icon"
    SVG_FILE = os.getenv( "HOME" ) + "/" + SVG_ICON + ".svg"
    SVG_FULL_MOON_FILE = os.getenv( "HOME" ) + "/" + "." + NAME + "-fullmoon-icon" + ".svg"
    SVG_SATELLITE_ICON = NAME + "-satellite"

    COMMENTS = "Displays the moon phase and other astronomical information."
    CREDIT_BRIGHT_LIMB = "Bright Limb from 'Astronomical Algorithms' by Jean Meeus."
    CREDIT_ECLIPSE = "Eclipse information by Fred Espenak and Jean Meeus. http://eclipse.gsfc.nasa.gov"
    CREDIT_PYEPHEM = "Calculations courtesy of PyEphem/XEphem. http://rhodesmill.org/pyephem"
    CREDIT_SATELLITE = "Satellite TLE data by Dr T S Kelso. http://www.celestrak.com"
    CREDIT_TROPICAL_SIGN = "Tropical Sign by Ignius Drake."
    CREDITS = [ CREDIT_PYEPHEM, CREDIT_ECLIPSE, CREDIT_TROPICAL_SIGN, CREDIT_BRIGHT_LIMB, CREDIT_SATELLITE ]

    INDENT = "    "

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_CITY_ELEVATION = "cityElevation"
    SETTINGS_CITY_LATITUDE = "cityLatitude"
    SETTINGS_CITY_LONGITUDE = "cityLongitude"
    SETTINGS_CITY_NAME = "cityName"
    SETTINGS_DISPLAY_PATTERN = "displayPattern"
    SETTINGS_ONLY_SHOW_VISIBLE_SATELLITE_PASSES = "onlyShowVisibleSatellitePasses"
    SETTINGS_PLANETS = "planets"
    SETTINGS_SATELLITES = "satellites"
    SETTINGS_SHOW_PLANETS_AS_SUBMENU = "showPlanetsAsSubmenu"
    SETTINGS_SHOW_SATELLITE_NOTIFICATION = "showSatelliteNotification"
    SETTINGS_SHOW_SATELLITE_NUMBER = "showSatelliteNumber"
    SETTINGS_SHOW_SATELLITE_SUBSEQUENT_PASSES = "showSatelliteSubsequentPasses"
    SETTINGS_SHOW_SATELLITES_AS_SUBMENU = "showSatellitesAsSubmenu"
    SETTINGS_SHOW_STARS_AS_SUBMENU = "showStarsAsSubmenu"
    SETTINGS_SHOW_WEREWOLF_WARNING = "showWerewolfWarning"
    SETTINGS_STARS = "stars"
    SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE = "werewolfWarningStartIlluminationPercentage"
    SETTINGS_WEREWOLF_WARNING_TEXT_BODY = "werewolfWarningTextBody"
    SETTINGS_WEREWOLF_WARNING_TEXT_SUMMARY = "werewolfWarningTextSummary"

    DISPLAY_PATTERN_DEFAULT = "[MOON PHASE] [MOON ILLUMINATION]"
    DISPLAY_NEEDS_REFRESH = "(needs refresh)"

    LUNAR_PHASE_FULL_MOON = "FULL_MOON"
    LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
    LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
    LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
    LUNAR_PHASE_NEW_MOON = "NEW_MOON"
    LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
    LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
    LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"

    LUNAR_PHASE_NAMES = {
        LUNAR_PHASE_FULL_MOON : "Full Moon",
        LUNAR_PHASE_WANING_GIBBOUS : "Waning Gibbous",
        LUNAR_PHASE_THIRD_QUARTER : "Third Quarter",
        LUNAR_PHASE_WANING_CRESCENT : "Waning Crescent",
        LUNAR_PHASE_NEW_MOON : "New Moon",
        LUNAR_PHASE_WAXING_CRESCENT : "Waxing Crescent",
        LUNAR_PHASE_FIRST_QUARTER : "First Quarter",
        LUNAR_PHASE_WAXING_GIBBOUS : "Waxing Gibbous"
    }

    WEREWOLF_WARNING_TEXT_BODY = "                                          ...werewolves about ! ! !"
    WEREWOLF_WARNING_TEXT_SUMMARY = "W  A  R  N  I  N  G"

    SATELLITE_TEXT_SUMMARY = "                                          ...is above the horizon!"
    SATELLITE_TLE_URL = "http://celestrak.com/NORAD/elements/visual.txt"

    PLANETS = [
        [ "Mercury", ephem.Mercury() ],
        [ "Venus", ephem.Venus() ],
        [ "Mars", ephem.Mars() ],
        [ "Jupiter", ephem.Jupiter() ],
        [ "Saturn", ephem.Saturn() ],
        [ "Uranus", ephem.Uranus() ],
        [ "Neptune", ephem.Neptune() ],
        [ "Pluto", ephem.Pluto() ] ]

    TAG_ALTITUDE = " ALTITUDE"
    TAG_AZIMUTH = " AZIMUTH"
    TAG_BRIGHT_LIMB = " BRIGHT LIMB"
    TAG_CONSTELLATION = " CONSTELLATION"
    TAG_DECLINATION = " DECLINATION"
    TAG_DISTANCE_TO_EARTH = " DISTANCE TO EARTH"
    TAG_DISTANCE_TO_SUN = " DISTANCE TO SUN"
    TAG_ILLUMINATION = " ILLUMINATION"
    TAG_MAGNITUDE = " MAGNITUDE"
    TAG_RIGHT_ASCENSION = " RIGHT ASCENSION"
    TAG_RISE_AZIMUTH = " RISE AZIMUTH"
    TAG_RISE_TIME = " RISE TIME"
    TAG_SET_AZIMUTH = " SET AZIMUTH"
    TAG_SET_TIME = " SET TIME"
    TAG_TROPICAL_SIGN = " TROPICAL SIGN"
    TAG_VISIBLE = " VISIBLE"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorLunar.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )

        self.dialog = None
        self.data = { }
        self.dataPrevious = { }
        self.satelliteNotifications = { }

        self.getSatelliteTLEData()
        self.loadSettings()

        if notifyImported: Notify.init( IndicatorLunar.NAME )

        # Create an AppIndicator3 indicator...if it fails, create a GTK indicator.
        # On Lubuntu 12.04 the AppIndicator3 is created (the icon displays).
        # However, the tooltip does not display and text cannot be written to the label next to the icon.
        try:
            self.appindicatorImported = True
            self.indicator = appindicator.Indicator.new( IndicatorLunar.NAME, "", appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_icon_theme_path( os.getenv( "HOME" ) )
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling...
        except Exception as e:
            logging.exception( e )
            logging.info( "Unable to create AppIndicator - creating GTK Status Icon instead." )
            self.appindicatorImported = False
            self.menu = Gtk.Menu() # Set an empty menu to get things rolling...
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.update()
        Gtk.main()


    def update( self ):
        # Update the satellite TLE data at most every 12 hours.
        if datetime.datetime.now() > ( self.lastUpdateTLE + datetime.timedelta( hours = 12 ) ): self.getSatelliteTLEData() 

        # UTC is used in all calculations.  When it comes time to display, conversion to local time takes place.
        ephemNow = ephem.now()

        # Satellite notification.
        if notifyImported and self.showSatelliteNotification:
            ephemNowInLocalTime = ephem.Date( self.localiseAndTrim( ephemNow ) )
            for satelliteNameNumber in sorted( self.satellites, key = lambda x: ( x[ 0 ], x[ 1 ] ) ):

                # Is there a rise/set time for the current satellite...
                riseTimeKey = self.getSatelliteNameNumber( satelliteNameNumber[ 0 ], ( satelliteNameNumber[ 1 ] ) ) + IndicatorLunar.TAG_RISE_TIME
                setTimeKey = self.getSatelliteNameNumber( satelliteNameNumber[ 0 ], ( satelliteNameNumber[ 1 ] ) ) + IndicatorLunar.TAG_SET_TIME
                if not ( riseTimeKey in self.data and setTimeKey in self.data ):
                    continue

                # Ensure the current time is within the rise/set...
                if not ( ephemNowInLocalTime > ephem.Date( self.data[ riseTimeKey ] ) and ephemNowInLocalTime < ephem.Date( self.data[ setTimeKey ] ) ):
                    continue

                # Show a notification for the satellite, but only once per pass...
                key = self.getSatelliteNameNumber( satelliteNameNumber[ 0 ], satelliteNameNumber[ 1 ] )
                if key in self.satelliteNotifications and ephemNowInLocalTime < ephem.Date( self.satelliteNotifications[ key ] ):
                    continue

                self.satelliteNotifications[ key ] = self.data[ setTimeKey ] # Flag to ensure the notification happens once per satellite's pass.

                if self.showSatelliteNumber:
                    Notify.Notification.new( satelliteNameNumber[ 0 ] + " - " + satelliteNameNumber[ 1 ], IndicatorLunar.SATELLITE_TEXT_SUMMARY, IndicatorLunar.SVG_SATELLITE_ICON ).show()
                else:
                    Notify.Notification.new( satelliteNameNumber[ 0 ], IndicatorLunar.SATELLITE_TEXT_SUMMARY, IndicatorLunar.SVG_SATELLITE_ICON ).show()

        # Reset the data on each update, otherwise data will accumulate (if a star/satellite was added then removed, the computed data remains).
        self.dataPrevious = self.data
        self.data = { }

        self.data[ "CITY NAME" ] = self.cityName

        lunarIlluminationPercentage = int( round( ephem.Moon( self.getCity( ephemNow ) ).phase ) )
        lunarPhase = self.getLunarPhase( ephemNow, lunarIlluminationPercentage )

        self.buildMenu( ephemNow, lunarPhase )

        # Parse the display pattern and show it...
        #
        # For Ubuntu (Unity), an icon and label can co-exist and there is no tooltip. The icon is always to the right of the label.
        # On Ubuntu 13.10 (might be a bug), an icon must be displayed, so if no icon tag is present, display a 1 pixel SVG.
        #
        # On non Unity (Lubuntu, etc), only an icon can be displayed - text is shown as a tooltip.
        parsedOutput = self.displayPattern
        for key in self.data.keys():
            parsedOutput = parsedOutput.replace( "[" + key + "]", self.data[ key ] )

        self.createIcon( lunarIlluminationPercentage, self.getBrightLimbAngleRelativeToZenith( self.getCity( ephemNow ), ephem.Moon( self.getCity( ephemNow ) ) ) )
        if self.appindicatorImported:
            self.indicator.set_icon( IndicatorLunar.SVG_ICON )
            self.indicator.set_label( parsedOutput, "" ) # Second parameter is a guide for how wide the text could get (see label-guide in http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html).
        else:
            self.statusicon.set_from_file( IndicatorLunar.SVG_FILE )
            self.statusicon.set_tooltip_text( parsedOutput )

        # Full moon notification.
        phaseIsBetweenNewAndFullInclusive = ( lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON )

        if notifyImported and \
            self.showWerewolfWarning and \
            lunarIlluminationPercentage >= self.werewolfWarningStartIlluminationPercentage and \
            phaseIsBetweenNewAndFullInclusive:

            # The notification summary text must not be empty (at least on Unity).
            summary = self.werewolfWarningTextSummary
            if self.werewolfWarningTextSummary == "":
                summary = " "

            Notify.Notification.new( summary, self.werewolfWarningTextBody, IndicatorLunar.SVG_FILE ).show()


    def buildMenu( self, ephemNow, lunarPhase ):
        nextUpdates = [ ] # Stores the date/time for each upcoming rise/set/phase...used to find the date/time closest to now and that will be the next time for an update.

        if self.appindicatorImported:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if not, GTK complains).
        menu = Gtk.Menu()

        self.createMoonMenu( menu, nextUpdates, ephemNow, lunarPhase )

        self.createSunMenu( menu, nextUpdates, ephemNow )

        # Planets
        # Reference:
        #    http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
        if len( self.planets ) > 0:
            planetsMenuItem = Gtk.MenuItem( "Planets" )
            menu.append( planetsMenuItem )

            if self.showPlanetsAsSubMenu:
                planetsSubMenu = Gtk.Menu()
                planetsMenuItem.set_submenu( planetsSubMenu )

            for planet in IndicatorLunar.PLANETS:
                if planet[ 0 ] in self.planets:
                    if self.showPlanetsAsSubMenu:
                        menuItem = Gtk.MenuItem( planet[ 0 ] )
                        planetsSubMenu.append( menuItem )
                    else:
                        menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + planet[ 0 ] )
                        menu.append( menuItem )

                    planet[ 1 ].compute( self.getCity( ephemNow ) )
                    self.createBodyMenu( menuItem, planet[ 1 ], nextUpdates, ephemNow )

        self.createStarsMenu( ephemNow, menu, nextUpdates )

        self.createSatellitesMenu( ephemNow, menu, nextUpdates )

        menu.append( Gtk.SeparatorMenuItem() )

        preferencesMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        menu.append( preferencesMenuItem )

        aboutMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        aboutMenuItem.connect( "activate", self.onAbout )
        menu.append( aboutMenuItem )

        quitMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        quitMenuItem.connect( "activate", Gtk.main_quit )
        menu.append( quitMenuItem )

        if self.appindicatorImported:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu

        menu.show_all()

        # Work out when to do the next update...
        # Need to pass an integer to GLib.timeout_add_seconds.
        # Add a 10 second buffer because the update can occur slightly earlier (due to truncating the fractional time component).
        nextUpdates.sort()
        nextUpdateInSeconds = int ( ( ephem.localtime( nextUpdates[ 0 ] ) - ephem.localtime( ephemNow ) ).total_seconds() ) + 10
        if nextUpdateInSeconds < 60: # Ensure the update period is positive and not too frequent...
            nextUpdateInSeconds = 60

        if nextUpdateInSeconds > ( 60 * 60 ): # Ensure the update period is at least hourly...
            nextUpdateInSeconds = ( 60 * 60 )

        self.eventSourceID = GLib.timeout_add_seconds( nextUpdateInSeconds, self.update )


    # Reference:
    #    http://www.ga.gov.au/geodesy/astro/moonrise.jsp
    def createMoonMenu( self, menu, nextUpdates, ephemNow, lunarPhase ):
        city = self.getCity( ephemNow )

        menuItem = Gtk.MenuItem( "Moon" )
        menu.append( menuItem )

        self.createBodyMenu( menuItem, ephem.Moon( city ), nextUpdates, ephemNow )

        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )

        TAG_MOON_PHASE = "MOON PHASE"
        self.data[ TAG_MOON_PHASE ] = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ]
        menuItem.get_submenu().append( Gtk.MenuItem( "Phase: " + self.data[ TAG_MOON_PHASE ] ) )

        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
        menuItem.get_submenu().append( Gtk.MenuItem( "Next Phases" ) )

        # Determine which phases occur by date rather than using the phase calculated.
        # The phase (illumination) rounds numbers and so a given phase is entered earlier than what is correct.
        nextPhases = [ ]

        TAG_MOON_FIRST_QUARTER = "MOON FIRST QUARTER"
        self.data[ TAG_MOON_FIRST_QUARTER ] = self.localiseAndTrim( ephem.next_first_quarter_moon( ephemNow ) )
        nextPhases.append( [ self.data[ TAG_MOON_FIRST_QUARTER ], "First Quarter: " ] )

        TAG_MOON_FULL = "MOON FULL"
        self.data[ TAG_MOON_FULL ] = self.localiseAndTrim( ephem.next_full_moon( ephemNow ) )
        nextPhases.append( [ self.data[ TAG_MOON_FULL ], "Full: " ] )

        TAG_MOON_THIRD_QUARTER = "MOON THIRD QUARTER"
        self.data[ TAG_MOON_THIRD_QUARTER ] = self.localiseAndTrim( ephem.next_last_quarter_moon( ephemNow ) )
        nextPhases.append( [ self.data[ TAG_MOON_THIRD_QUARTER ], "Third Quarter: " ] )

        TAG_MOON_NEW = "MOON NEW"
        self.data[ TAG_MOON_NEW ] = self.localiseAndTrim( ephem.next_new_moon( ephemNow ) )
        nextPhases.append( [ self.data[ TAG_MOON_NEW ], "New: " ] )

        nextPhases = sorted( nextPhases, key = lambda tuple: tuple[ 0 ] )
        for phaseInformation in nextPhases:
            menuItem.get_submenu().append( Gtk.MenuItem( IndicatorLunar.INDENT + phaseInformation[ 1 ] + phaseInformation[ 0 ] ) )

        nextUpdates.append( ephem.next_first_quarter_moon( ephemNow ) )
        nextUpdates.append( ephem.next_full_moon( ephemNow ) )
        nextUpdates.append( ephem.next_last_quarter_moon( ephemNow ) )
        nextUpdates.append( ephem.next_new_moon( ephemNow ) )

        # Eclipse.
        eclipseInformation = eclipse.getLunarEclipseForUTC( ephemNow.datetime() )
        if eclipseInformation is not None:
            menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
            self.createEclipseMenu( menuItem.get_submenu(), eclipseInformation, "MOON" )


    # References:
    #    http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    #    http://www.ga.gov.au/geodesy/astro/sunrise.jsp
    def createSunMenu( self, menu, nextUpdates, ephemNow ):
        TAG_SUN = "SUN"

        city = self.getCity( ephemNow )

        menuItem = Gtk.MenuItem( "Sun" )
        menu.append( menuItem )

        subMenu = Gtk.Menu()
        menuItem.set_submenu( subMenu )

        sun = ephem.Sun( city )

        self.data[ TAG_SUN + IndicatorLunar.TAG_CONSTELLATION ] = ephem.constellation( sun )[ 1 ]
        subMenu.append( Gtk.MenuItem( "Constellation: " + self.data[ TAG_SUN + IndicatorLunar.TAG_CONSTELLATION ] ) )

#TODO Since upgrading to Ephem 3.7.5.3, a segmentation fault occurs after getTropicalSign returns...why?
#         self.data[ TAG_SUN + IndicatorLunar.TAG_TROPICAL_SIGN ] = self.getTropicalSign( sun, ephemNow )
#         subMenu.append( Gtk.MenuItem( "Tropical Sign: " + self.data[ TAG_SUN + IndicatorLunar.TAG_TROPICAL_SIGN ] ) )

        self.data[ TAG_SUN + IndicatorLunar.TAG_DISTANCE_TO_EARTH ] = str( round( sun.earth_distance, 4 ) ) + " AU"
        subMenu.append( Gtk.MenuItem( "Distance to Earth: " + self.data[ TAG_SUN + IndicatorLunar.TAG_DISTANCE_TO_EARTH ] ) )

        subMenu.append( Gtk.SeparatorMenuItem() )

        self.createRADecAzAltMagMenu( subMenu, sun )

        subMenu.append( Gtk.SeparatorMenuItem() )

        # Rising/Setting.
        try:
            city = self.getCity( ephemNow )
            rising = city.next_rising( sun )
            self.data[ TAG_SUN + IndicatorLunar.TAG_RISE_TIME ] = self.localiseAndTrim( rising )
            setting = city.next_setting( sun )
            self.data[ TAG_SUN + IndicatorLunar.TAG_SET_TIME ] = self.localiseAndTrim( setting )
            if rising > setting:
                subMenu.append( Gtk.MenuItem( "Set: " + self.data[ TAG_SUN + IndicatorLunar.TAG_SET_TIME ] ) )
                subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ TAG_SUN + IndicatorLunar.TAG_RISE_TIME ] ) )
            else:
                subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ TAG_SUN + IndicatorLunar.TAG_RISE_TIME ] ) )
                subMenu.append( Gtk.MenuItem( "Set: " + self.data[ TAG_SUN + IndicatorLunar.TAG_SET_TIME ] ) )

            nextUpdates.append( rising )
            nextUpdates.append( setting )

        except ephem.AlwaysUpError:
            subMenu.append( Gtk.MenuItem( "Always Up!" ) )
        except ephem.NeverUpError:
            subMenu.append( Gtk.MenuItem( "Never Up!" ) )

        subMenu.append( Gtk.SeparatorMenuItem() )

        # Solstice/Equinox.
        TAG_SUN_EQUINOX = "SUN EQUINOX"
        TAG_SUN_SOLSTICE = "SUN SOLSTICE"
        equinox = ephem.next_equinox( ephemNow )
        self.data[ TAG_SUN_EQUINOX ] = self.localiseAndTrim( equinox )
        solstice = ephem.next_solstice( ephemNow )
        self.data[ TAG_SUN_SOLSTICE ] = self.localiseAndTrim( solstice )
        if equinox < solstice:
            subMenu.append( Gtk.MenuItem( "Equinox: " + self.data[ TAG_SUN_EQUINOX ] ) )
            subMenu.append( Gtk.MenuItem( "Solstice: " + self.data[ TAG_SUN_SOLSTICE ] ) )
        else:
            subMenu.append( Gtk.MenuItem( "Solstice: " + self.data[ TAG_SUN_SOLSTICE ] ) )
            subMenu.append( Gtk.MenuItem( "Equinox: " + self.data[ TAG_SUN_EQUINOX ] ) )

        nextUpdates.append( equinox )
        nextUpdates.append( solstice )

        # Eclipse.
        eclipseInformation = eclipse.getSolarEclipseForUTC( ephemNow.datetime() )
        if eclipseInformation is not None:
            subMenu.append( Gtk.SeparatorMenuItem() )
            self.createEclipseMenu( subMenu, eclipseInformation, TAG_SUN )


    def createBodyMenu( self, bodyMenuItem, body, nextUpdates, ephemNow ):
        subMenu = Gtk.Menu()

        self.data[ body.name.upper() + IndicatorLunar.TAG_ILLUMINATION ] = str( int( round( body.phase ) ) ) + "%"
        subMenu.append( Gtk.MenuItem( "Illumination: " + self.data[ body.name.upper() + IndicatorLunar.TAG_ILLUMINATION ] ) )

        self.data[ body.name.upper() + IndicatorLunar.TAG_CONSTELLATION ] = ephem.constellation( body )[ 1 ]
        subMenu.append( Gtk.MenuItem( "Constellation: " + self.data[ body.name.upper() + IndicatorLunar.TAG_CONSTELLATION ] ) )

#TODO Since upgrading to Ephem 3.7.5.3, a segmentation fault occurs after getTropicalSign returns...why?
#         self.data[ body.name.upper() + IndicatorLunar.TAG_TROPICAL_SIGN ] = self.getTropicalSign( body, ephemNow )
#         subMenu.append( Gtk.MenuItem( "Tropical Sign: " + self.data[ body.name.upper() + IndicatorLunar.TAG_TROPICAL_SIGN ] ) )

        self.data[ body.name.upper() + IndicatorLunar.TAG_DISTANCE_TO_EARTH ] = str( round( body.earth_distance, 4 ) ) + " AU"
        subMenu.append( Gtk.MenuItem( "Distance to Earth: " + self.data[ body.name.upper() + IndicatorLunar.TAG_DISTANCE_TO_EARTH ] ) )

        self.data[ body.name.upper() + IndicatorLunar.TAG_DISTANCE_TO_SUN ] = str( round( body.sun_distance, 4 ) ) + " AU"
        subMenu.append( Gtk.MenuItem( "Distance to Sun: " + self.data[ body.name.upper() + IndicatorLunar.TAG_DISTANCE_TO_SUN ] ) )

        self.data[ body.name.upper() + IndicatorLunar.TAG_BRIGHT_LIMB ] = str( round( self.getBrightLimbAngleRelativeToZenith( self.getCity( ephemNow ), body ) ) ) + "°"
        subMenu.append( Gtk.MenuItem( "Bright Limb: " + self.data[ body.name.upper() + IndicatorLunar.TAG_BRIGHT_LIMB ] ) )

        subMenu.append( Gtk.SeparatorMenuItem() )

        self.createRADecAzAltMagMenu( subMenu, body )

        subMenu.append( Gtk.SeparatorMenuItem() )

        # Must compute the previous information (illumination, constellation, phase and so on BEFORE rising/setting).
        # For some reason the values, most notably phase, are different (and wrong) if calculated AFTER rising/setting are calculated.
        try:
            TAG_BODY_RISE_TIME = body.name.upper() + IndicatorLunar.TAG_RISE_TIME
            TAG_BODY_SET_TIME = body.name.upper() + IndicatorLunar.TAG_SET_TIME

            city = self.getCity( ephemNow )
            rising = city.next_rising( body )
            setting = city.next_setting( body )
            self.data[ TAG_BODY_RISE_TIME ] = str( self.localiseAndTrim( rising ) )
            self.data[ TAG_BODY_SET_TIME ] = str( self.localiseAndTrim( setting ) )
            if rising > setting:
                subMenu.append( Gtk.MenuItem( "Set: " + self.data[ TAG_BODY_SET_TIME ] ) )
                subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ TAG_BODY_RISE_TIME ] ) )
            else:
                subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ TAG_BODY_RISE_TIME ] ) )
                subMenu.append( Gtk.MenuItem( "Set: " + self.data[ TAG_BODY_SET_TIME ] ) )

            nextUpdates.append( rising )
            nextUpdates.append( setting )

        except ephem.AlwaysUpError:
            subMenu.append( Gtk.MenuItem( "Always Up!" ) )
        except ephem.NeverUpError:
            subMenu.append( Gtk.MenuItem( "Never Up!" ) )

        bodyMenuItem.set_submenu( subMenu )


    # Reference:
    #    http://aa.usno.navy.mil/data/docs/mrst.php
    def createStarsMenu( self, ephemNow, menu, nextUpdates ):
        if len( self.stars ) == 0: return

        menuItem = Gtk.MenuItem( "Stars" )
        menu.append( menuItem )

        if self.showStarsAsSubMenu:
            starsSubMenu = Gtk.Menu()
            menuItem.set_submenu( starsSubMenu )

        for starName in self.stars:

            if self.showStarsAsSubMenu:
                menuItem = Gtk.MenuItem( starName )
                starsSubMenu.append( menuItem )
            else:
                menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + starName )
                menu.append( menuItem )

            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )

            city = self.getCity( ephemNow )
            star = ephem.star( starName )
            star.compute( city )

            self.data[ star.name.upper() + IndicatorLunar.TAG_CONSTELLATION ] = ephem.constellation( star )[ 1 ]
            subMenu.append( Gtk.MenuItem( "Constellation: " + self.data[ star.name.upper() + IndicatorLunar.TAG_CONSTELLATION ] ) )

            self.createRADecAzAltMagMenu( subMenu, star )

            subMenu.append( Gtk.SeparatorMenuItem() )

            # Rising/Setting.
            try:
                rising = city.next_rising( star )
                self.data[ star.name.upper() + IndicatorLunar.TAG_RISE_TIME ] = self.localiseAndTrim( rising )
                setting = city.next_setting( star )
                self.data[ star.name.upper() + IndicatorLunar.TAG_SET_TIME ] = self.localiseAndTrim( setting )
                if rising > setting:
                    subMenu.append( Gtk.MenuItem( "Set: " + self.data[ star.name.upper() + IndicatorLunar.TAG_SET_TIME ] ) )
                    subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ star.name.upper() + IndicatorLunar.TAG_RISE_TIME ] ) )
                else:
                    subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ star.name.upper() + IndicatorLunar.TAG_RISE_TIME ] ) )
                    subMenu.append( Gtk.MenuItem( "Set: " + self.data[ star.name.upper() + IndicatorLunar.TAG_SET_TIME ] ) )

                nextUpdates.append( rising )
                nextUpdates.append( setting )

            except ephem.AlwaysUpError:
                subMenu.append( Gtk.MenuItem( "Always Up!" ) )
            except ephem.NeverUpError:
                subMenu.append( Gtk.MenuItem( "Never Up!" ) )


    # Uses TLE data collated by Dr T S Kelso (http://celestrak.com/NORAD/elements) with PyEphem to compute satellite rise/transit/set times.
    # Other sources/background:
    #   http://spotthestation.nasa.gov/sightings
    #   http://www.n2yo.com/passes/?s=25544
    #   http://www.heavens-above.com/
    #
    # For planets/stars, the next rise/set time is shown.
    # If already above the horizon, the set time is shown followed by the rise time for the next pass.
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
    def createSatellitesMenu( self, ephemNow, menu, nextUpdates ):
        if len( self.satellites ) == 0: return

        if len( self.satelliteTLEData ) == 0: return # No point adding "non information" to the menu.  The preferences will tell the user there is a problem.

        menuItem = Gtk.MenuItem( "Satellites" )
        menu.append( menuItem )

        if self.showSatellitesAsSubMenu:
            satellitesSubMenu = Gtk.Menu()
            menuItem.set_submenu( satellitesSubMenu )

        for satelliteNameNumber in sorted( self.satellites, key = lambda x: ( x[ 0 ], x[ 1 ] ) ):
            if self.showSatelliteNumber:
                menuText = satelliteNameNumber[ 0 ] + " - " + satelliteNameNumber[ 1 ]
            else:
                menuText = satelliteNameNumber[ 0 ]

            if self.showSatellitesAsSubMenu:
                menuItem = Gtk.MenuItem( menuText )
                satellitesSubMenu.append( menuItem )
            else:
                menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + menuText )
                menu.append( menuItem )

            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )

            key = self.getSatelliteNameNumber( satelliteNameNumber[ 0 ], satelliteNameNumber[ 1 ] )
            if not key in self.satelliteTLEData:
                subMenu.append( Gtk.MenuItem( "No TLE data!" ) )
                continue

            self.calculateNextSatellitePass( ephemNow, key, subMenu, nextUpdates )


    def calculateNextSatellitePass( self, ephemNow, satelliteNameNumber, menu, nextUpdates ):
        satelliteInfo = self.satelliteTLEData[ satelliteNameNumber ]
        foundPass = False
        nextPass = None # Initialised here so it is in scope for the subsequent pass calculations.       
        currentDateTime = ephemNow
        endDateTime = ephem.Date( ephemNow + ephem.hour * 24 * 10 ) # Stop looking for transits 10 days from ephemNow.
        while currentDateTime < endDateTime:
            city = self.getCity( currentDateTime )
            satellite = ephem.readtle( satelliteInfo.getName(), satelliteInfo.getTLELine1(), satelliteInfo.getTLELine2() ) # Need to fetch on each iteration as the visibility check may alter the object's internals. 
            nextPass = None
            try: nextPass = city.next_pass( satellite )
            except ValueError:
                menu.append( Gtk.MenuItem( "Never rises or never sets." ) ) # The satellite is always up or never up.
                break

            if not self.nextPassIsValid( nextPass ):
                menu.append( Gtk.MenuItem( "Unable to compute next transit!" ) )
                break

            if nextPass[ 0 ] < nextPass[ 4 ]: # The satellite is below the horizon.
                passIsVisible = self.isSatellitePassVisible( satellite, nextPass[ 2 ] )
                if self.onlyShowVisibleSatellitePasses and not passIsVisible:
                    currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )
                    continue

                self.data[ satelliteNameNumber + IndicatorLunar.TAG_RISE_TIME ] = self.localiseAndTrim( nextPass[ 0 ] )
                self.data[ satelliteNameNumber + IndicatorLunar.TAG_RISE_AZIMUTH ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 1 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 1 ] ) ) + ")"
                self.data[ satelliteNameNumber + IndicatorLunar.TAG_SET_TIME ] = self.localiseAndTrim( nextPass[ 4 ] )
                self.data[ satelliteNameNumber + IndicatorLunar.TAG_SET_AZIMUTH ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 5 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 5 ] ) ) + ")"
                self.data[ satelliteNameNumber + IndicatorLunar.TAG_VISIBLE ] = str( passIsVisible )

                nextUpdates.append( nextPass[ 0 ] )
                nextUpdates.append( nextPass[ 4 ] )

                foundPass = True
                break

            # The satellite is in transit and so the rise time is for the next pass - use the rise/set from the previous run.
            if ( satelliteNameNumber + IndicatorLunar.TAG_RISE_TIME ) in self.dataPrevious: # Assume rest of data is also present!
                # The data from the previous run is available...
                self.data[ satelliteNameNumber + IndicatorLunar.TAG_RISE_TIME ] = self.dataPrevious[ satelliteNameNumber + IndicatorLunar.TAG_RISE_TIME ]
                self.data[ satelliteNameNumber + IndicatorLunar.TAG_RISE_AZIMUTH ] = self.dataPrevious[ satelliteNameNumber + IndicatorLunar.TAG_RISE_AZIMUTH ]
                self.data[ satelliteNameNumber + IndicatorLunar.TAG_SET_TIME ] = self.dataPrevious[ satelliteNameNumber + IndicatorLunar.TAG_SET_TIME ]
                self.data[ satelliteNameNumber + IndicatorLunar.TAG_SET_AZIMUTH ] = self.dataPrevious[ satelliteNameNumber + IndicatorLunar.TAG_SET_AZIMUTH ]
                self.data[ satelliteNameNumber + IndicatorLunar.TAG_VISIBLE ] = self.dataPrevious[ satelliteNameNumber + IndicatorLunar.TAG_VISIBLE ]

                nextUpdates.append( nextPass[ 4 ] ) # Don't add the rise time as it is in the past!

                foundPass = True
                break

            # There is no previous data (as this is the first run and the satellite is in transit), so look for the next pass.
            currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )

        if currentDateTime < endDateTime and foundPass:
            menu.append( Gtk.MenuItem( "Rise: " + self.data[ satelliteNameNumber + IndicatorLunar.TAG_RISE_TIME ] ) )
            menu.append( Gtk.MenuItem( "Azimuth: " + self.data[ satelliteNameNumber + IndicatorLunar.TAG_RISE_AZIMUTH ] ) )
            menu.append( Gtk.MenuItem( "Set: " + self.data[ satelliteNameNumber + IndicatorLunar.TAG_SET_TIME ] ) )
            menu.append( Gtk.MenuItem( "Azimuth: " + self.data[ satelliteNameNumber + IndicatorLunar.TAG_SET_AZIMUTH ] ) )
            menu.append( Gtk.MenuItem( "Visible: " + self.data[ satelliteNameNumber + IndicatorLunar.TAG_VISIBLE ] ) )

            if self.showSatelliteSubsequentPasses: self.calculateSatelliteSubsequentPasses( ephemNow, satelliteInfo, menu, nextPass[ 4 ] )

        if currentDateTime >= endDateTime and not foundPass:
            menu.append( Gtk.MenuItem( "No transits within the next 10 days." ) )


    def calculateSatelliteSubsequentPasses( self, ephemNow, satelliteInfo, menu, lastPassDateTime ):
        currentDateTime = ephem.Date( lastPassDateTime + ephem.minute * 30 ) # Start looking for transits after the last set.
        endDateTime = ephem.Date( ephemNow + ephem.hour * 24 * 10 ) # Stop looking for transits 10 days from ephemNow.
        numberPasses = 5 # Compute at most the next 5 transits.
        count = 0
        while count < numberPasses and currentDateTime < endDateTime:
            city = self.getCity( currentDateTime )
            satellite = ephem.readtle( satelliteInfo.getName(), satelliteInfo.getTLELine1(), satelliteInfo.getTLELine2() ) # Need to fetch on each iteration as the visibility check may alter the object's internals. 
            try:
                nextPass = city.next_pass( satellite )
                if not self.nextPassIsValid( nextPass ): break

                if nextPass[ 0 ] >= nextPass[ 4 ]: break # Shouldn't happen but sometimes Ephem yields strange results!

                isVisible = self.isSatellitePassVisible( satellite, nextPass[ 2 ] )
                if ( self.onlyShowVisibleSatellitePasses and isVisible ) or not self.onlyShowVisibleSatellitePasses:
                    menu.append( Gtk.MenuItem( "" ) )
                    menu.append( Gtk.MenuItem( "Rise: " + self.localiseAndTrim( nextPass[ 0 ] ) ) )
                    menu.append( Gtk.MenuItem( "Azimuth: " + str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 1 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 1 ] ) ) + ")" ) )
                    menu.append( Gtk.MenuItem( "Set: " + self.localiseAndTrim( nextPass[ 4 ] ) ) )
                    menu.append( Gtk.MenuItem( "Azimuth: " + str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 5 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 1 ] ) ) + ")" ) )
                    menu.append( Gtk.MenuItem( "Visible: " + str( isVisible ) ) )
    
                    count += 1

                currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )

            except ValueError: break # Occurs when the satellite is never up or always up.  Unfortunately cannot distinguish which. 


    # Distinguishes visible transits from all transits...
    #    http://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
    #    http://www.celestrak.com/columns/v03n01
    #    http://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
    def isSatellitePassVisible( self, satellite, transitDateTime ):
        city = self.getCity( transitDateTime )
        city.pressure = 0
        city.horizon = "-0:34"

        satellite.compute( city )
        sun = ephem.Sun()
        sun.compute( city )

        return satellite.eclipsed is False and \
            sun.alt > ephem.degrees( "-18" ) and \
            sun.alt < ephem.degrees( "-6" )


    def nextPassIsValid( self, nextPass ):
        return nextPass is not None and \
            len( nextPass ) == 6 and \
            nextPass[ 0 ] is not None and \
            nextPass[ 1 ] is not None and \
            nextPass[ 2 ] is not None and \
            nextPass[ 3 ] is not None and \
            nextPass[ 4 ] is not None and \
            nextPass[ 5 ] is not None


    # Returns the string
    #    satelliteName - satelliteNumber
    # useful for keys into a dict/hashtable and for display.
    def getSatelliteNameNumber( self, satelliteName, satelliteNumber ): return satelliteName + " - " + satelliteNumber


    def createEclipseMenu( self, menu, eclipseData, bodyTag ):
        menu.append( Gtk.MenuItem( "Eclipse" ) )

        localisedAndTrimmedDateTime = self.localiseAndTrim( ephem.Date( eclipseData[ 0 ] ) )

        self.data[ bodyTag + " ECLIPSE DATE TIME" ] = localisedAndTrimmedDateTime
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Date/Time: " + localisedAndTrimmedDateTime ) )

        self.data[ bodyTag + " ECLIPSE LATITUDE LONGITUDE" ] = eclipseData[ 2 ] + " " + eclipseData[ 3 ]
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Latitude/Longitude: " + eclipseData[ 2 ] + " " + eclipseData[ 3 ] ) )

        self.data[ bodyTag + " ECLIPSE TYPE" ] = eclipseData[ 1 ]
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Type: " + eclipseData[ 1 ] ) )


    # Compute the right ascension, declination, azimuth, altitude and magnitude for a body.
    def createRADecAzAltMagMenu( self, menu, body ):
        self.data[ body.name.upper() + IndicatorLunar.TAG_RIGHT_ASCENSION ] = str( round( self.convertHoursMinutesSecondsToDecimalDegrees( body.g_ra ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.g_ra ) ) + ")"
        menu.append( Gtk.MenuItem( "Right Ascension: " + self.data[ body.name.upper() + IndicatorLunar.TAG_RIGHT_ASCENSION ] ) )

        direction = "N"
        if body.g_dec < 0.0:
            direction = "S"

        self.data[ body.name.upper() + IndicatorLunar.TAG_DECLINATION ] = str( abs( round( self.convertDegreesMinutesSecondsToDecimalDegrees( body.g_dec ), 2 ) ) ) + "° " + direction + " (" + re.sub( "\.(\d+)", "", str( body.g_dec ) ) + ")"
        menu.append( Gtk.MenuItem( "Declination: " + self.data[ body.name.upper() + IndicatorLunar.TAG_DECLINATION ] ) )

        self.data[ body.name.upper() + IndicatorLunar.TAG_AZIMUTH ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( body.az ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.az ) ) + ")"
        menu.append( Gtk.MenuItem( "Azimuth: " + self.data[ body.name.upper() + IndicatorLunar.TAG_AZIMUTH ] ) )

        self.data[ body.name.upper() + IndicatorLunar.TAG_ALTITUDE ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( body.alt ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.alt ) ) + ")"
        menu.append( Gtk.MenuItem( "Altitude: " + self.data[ body.name.upper() + IndicatorLunar.TAG_ALTITUDE ] ) )

        self.data[ body.name.upper() + IndicatorLunar.TAG_MAGNITUDE ] = str( body.mag )
        menu.append( Gtk.MenuItem( "Magnitude: " + self.data[ body.name.upper() + IndicatorLunar.TAG_MAGNITUDE ] ) )


    # Takes a float and converts to local time, trims off fractional seconds and returns a string.
    def localiseAndTrim( self, pyEphemDateTime ):
        localtimeString = str( ephem.localtime( pyEphemDateTime ) )
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
        signList = [ "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces" ]

        ( year, month, day ) = ephemNow.triple()
        epochAdjusted = float( year ) + float( month ) / 12.0 + float( day ) / 365.242
        ephemNowDate = str( ephemNow ).split( " " )

        bodyCopy = body.copy() # Computing the tropical sign changes the body's date/time/epoch (shared by other downstream calculations), so make a copy of the body and use that.
        bodyCopy.compute( ephemNowDate[ 0 ], epoch = str( epochAdjusted ) )
        planetCoordinates = str( ephem.Ecliptic( bodyCopy ).lon ).split( ":" )

        if float( planetCoordinates[ 2 ] ) > 30:
            planetCoordinates[ 1 ] = str( int ( planetCoordinates[ 1 ] ) + 1 )

        planetSignDegree = int( planetCoordinates[ 0 ] ) % 30
        planetSignMinute = str( planetCoordinates[ 1 ] )
        planetSignIndex = int( planetCoordinates[ 0 ] ) / 30
        planetSignName = signList[ int( planetSignIndex ) ]

        return planetSignName + " " + str( planetSignDegree ) + "° " + planetSignMinute + "'"


    # Compute the bright limb angle (relative to zenith) between the sun and a planetary body.
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

        if brightLimbAngleInDegrees is None: filename = IndicatorLunar.SVG_FULL_MOON_FILE
        else: filename = IndicatorLunar.SVG_FILE
        try:
            with open( filename, "w" ) as f:
                f.write( header + svg + footer )
                f.close()

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing SVG: " + filename )


    def handleLeftClick( self, icon ): self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )


    def handleRightClick( self, icon, button, time ): self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def onAbout( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.dialog = pythonutils.AboutDialog( 
               IndicatorLunar.NAME,
               IndicatorLunar.COMMENTS, 
               IndicatorLunar.WEBSITE, 
               IndicatorLunar.WEBSITE, 
               IndicatorLunar.VERSION, 
               Gtk.License.GPL_3_0, 
               IndicatorLunar.ICON,
               [ IndicatorLunar.AUTHOR ],
               IndicatorLunar.CREDITS,
               "Credits",
               "/usr/share/doc/" + IndicatorLunar.NAME + "/changelog.Debian.gz",
               logging )

        self.dialog.run()
        self.dialog.destroy()
        self.dialog = None


    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        notebook = Gtk.Notebook()

        # Display settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        hbox = Gtk.Box( spacing = 6 )

        label = Gtk.Label( "Display pattern" )
        hbox.pack_start( label, False, False, 0 )

        displayPattern = Gtk.Entry()
        displayPattern.set_text( self.displayPattern )
        displayPattern.set_tooltip_text( "The text shown next to the icon (or tooltip, where applicable)" )
        hbox.pack_start( displayPattern, True, True, 0 )

        grid.attach( hbox, 0, 0, 1, 1 )

        displayTagsStore = Gtk.ListStore( str, str ) # Display tag, value.
        for key in sorted( self.data.keys() ):
            displayTagsStore.append( [ key, self.data[ key ] ] )

        displayTagsStoreSort = Gtk.TreeModelSort( displayTagsStore )
        displayTagsStoreSort.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        tree = Gtk.TreeView( displayTagsStoreSort )
        tree.set_hexpand( True )
        tree.set_vexpand( True )
        tree.append_column( Gtk.TreeViewColumn( "Tag", Gtk.CellRendererText(), text = 0 ) )

        tree.append_column( Gtk.TreeViewColumn( "Value", Gtk.CellRendererText(), text = 1 ) )
        tree.set_tooltip_text( "Double click to add a tag to the display pattern." )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onDisplayTagDoubleClick, displayPattern )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "Display" ) )

        # Planet settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        hbox = Gtk.Box( spacing = 6 )

        showPlanetsAsSubmenuCheckbox = Gtk.CheckButton( "Show planets as submenus" )
        showPlanetsAsSubmenuCheckbox.set_active( self.showPlanetsAsSubMenu )
        showPlanetsAsSubmenuCheckbox.set_tooltip_text( "Show each planet in its own submenu." )
        grid.attach( showPlanetsAsSubmenuCheckbox, 0, 0, 1, 1 )

        planetStore = Gtk.ListStore( str, bool ) # Planet name, show/hide.
        for planet in IndicatorLunar.PLANETS: # Don't sort, rather keep the natural order.
            planetStore.append( [ planet[ 0 ], planet[ 0 ] in self.planets ] )

        tree = Gtk.TreeView( planetStore )
        tree.set_hexpand( True )
        tree.set_vexpand( True )

        tree.append_column( Gtk.TreeViewColumn( "Star", Gtk.CellRendererText(), text = 0 ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onPlanetToggled, planetStore, displayTagsStore )
        tree.append_column( Gtk.TreeViewColumn( "Display", renderer_toggle, active = 1 ) )

        tree.set_tooltip_text( "Check a planet to display in the menu." )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER )
        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "Planets" ) )

        # Star settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        hbox = Gtk.Box( spacing = 6 )

        showStarsAsSubmenuCheckbox = Gtk.CheckButton( "Show stars as submenus" )
        showStarsAsSubmenuCheckbox.set_tooltip_text( "Show each star in its own submenu." )
        showStarsAsSubmenuCheckbox.set_active( self.showStarsAsSubMenu )
        grid.attach( showStarsAsSubmenuCheckbox, 0, 0, 1, 1 )

        starStore = Gtk.ListStore( str, bool ) # Star name, show/hide.
        for star in sorted( ephem.stars.stars ):
            starStore.append( [ star, star in self.stars ] )

        tree = Gtk.TreeView( starStore )
        tree.set_hexpand( True )
        tree.set_vexpand( True )

        tree.append_column( Gtk.TreeViewColumn( "Star", Gtk.CellRendererText(), text = 0 ) )

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect( "toggled", self.onStarToggled, starStore, displayTagsStore )
        tree.append_column( Gtk.TreeViewColumn( "Display", renderer_toggle, active = 1 ) )

        tree.set_tooltip_text( "Check a star to display in the menu." )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "Stars" ) )

        # Satellite settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        hbox = Gtk.Box( spacing = 6 )

        if len( self.satelliteTLEData ) == 0:
            # Error downloading data.
            label = Gtk.Label()
            label.set_markup( "Unable to download the satellite data!\n\nCheck that <a href=\'" + IndicatorLunar.SATELLITE_TLE_URL + "'>" + IndicatorLunar.SATELLITE_TLE_URL + "</a> is available.\n" )
            label.set_margin_left( 25 )
            label.set_halign( Gtk.Align.START )
            grid.attach( label, 0, 0, 1, 1 )
        else:
            showSatelliteNumberCheckbox = Gtk.CheckButton( "Show satellite number" )
            showSatelliteNumberCheckbox.set_active( self.showSatelliteNumber )
            showSatelliteNumberCheckbox.set_tooltip_text( "Include the satellite number in the menu/notification." )
            grid.attach( showSatelliteNumberCheckbox, 0, 0, 1, 1 )

            showSatellitesAsSubmenuCheckbox = Gtk.CheckButton( "Show as submenus" )
            showSatellitesAsSubmenuCheckbox.set_active( self.showSatellitesAsSubMenu )
            showSatellitesAsSubmenuCheckbox.set_tooltip_text( "Show each satellite in its own submenu." )
            grid.attach( showSatellitesAsSubmenuCheckbox, 0, 1, 1, 1 )

            showSatellitePassesVisibleCheckbox = Gtk.CheckButton( "Only show visible passes" )
            showSatellitePassesVisibleCheckbox.set_active( self.onlyShowVisibleSatellitePasses )
            showSatellitePassesVisibleCheckbox.set_tooltip_text( "Only display information for visible passes." )
            grid.attach( showSatellitePassesVisibleCheckbox, 0, 2, 1, 1 )

            showSatelliteSubsequentPassesCheckbox = Gtk.CheckButton( "Show subsequent passes" )
            showSatelliteSubsequentPassesCheckbox.set_active( self.showSatelliteSubsequentPasses )
            showSatelliteSubsequentPassesCheckbox.set_tooltip_text( "Show passes following the current." )
            grid.attach( showSatelliteSubsequentPassesCheckbox, 2, 0, 1, 1 )

            showSatelliteNotificationCheckbox = Gtk.CheckButton( "Notification on rise" )
            showSatelliteNotificationCheckbox.set_active( self.showSatelliteNotification )
            showSatelliteNotificationCheckbox.set_tooltip_text( "Screen notification when a satellite rises above the horizon." )
            grid.attach( showSatelliteNotificationCheckbox, 2, 1, 1, 1 )

            satelliteStore = Gtk.ListStore( str, str, bool ) # Satellite name, satellite number, show/hide.
            for key in self.satelliteTLEData:
                satelliteInfo = self.satelliteTLEData[ key ]
                satelliteStore.append( [ satelliteInfo.getName(), satelliteInfo.getNumber(), [ satelliteInfo.getName(), satelliteInfo.getNumber() ] in self.satellites ] )

            satelliteStoreSort = Gtk.TreeModelSort( satelliteStore )
            satelliteStoreSort.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

            tree = Gtk.TreeView( satelliteStoreSort )
            tree.set_hexpand( True )
            tree.set_vexpand( True )
    
            tree.append_column( Gtk.TreeViewColumn( "Name", Gtk.CellRendererText(), text = 0 ) )
            tree.append_column( Gtk.TreeViewColumn( "Number", Gtk.CellRendererText(), text = 1 ) )
    
            renderer_toggle = Gtk.CellRendererToggle()
            renderer_toggle.connect( "toggled", self.onSatelliteToggled, satelliteStore, displayTagsStore, satelliteStoreSort )
            tree.append_column( Gtk.TreeViewColumn( "Display", renderer_toggle, active = 2 ) )
    
            tree.set_tooltip_text( "Check a satellite, station or rocket booster to display in the menu." )
            tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
    
            scrolledWindow = Gtk.ScrolledWindow()
            scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
            scrolledWindow.add( tree )
            grid.attach( scrolledWindow, 0, 3, 3, 1 )

            separator = Gtk.Separator.new( Gtk.Orientation.VERTICAL )
            grid.attach( separator, 1, 0, 1, 3 )

        notebook.append_page( grid, Gtk.Label( "Satellites" ) )

        # Full Moon notification settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showWerewolfWarningCheckbox = Gtk.CheckButton( "Werewolf warning" )
        showWerewolfWarningCheckbox.set_active( self.showWerewolfWarning )
        showWerewolfWarningCheckbox.set_tooltip_text( "Screen notification (approximately hourly) at full moon (or leading up to)" )
        grid.attach( showWerewolfWarningCheckbox, 0, 0, 2, 1 )

        label = Gtk.Label( "Illumination %" )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        label.set_margin_left( 25 )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.werewolfWarningStartIlluminationPercentage, 0, 100, 1, 0, 0 ) ) # In Ubuntu 13.10 the initial value set by the adjustment would not appear...
        spinner.set_value( self.werewolfWarningStartIlluminationPercentage ) # ...so need to force the initial value by explicitly setting it.
        spinner.set_tooltip_text( "The warning commences at the specified illumination - starting after a new moon (0%)" )
        spinner.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        spinner.set_hexpand( True )
        grid.attach( spinner, 1, 1, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", self.onShowWerewolfWarningCheckbox, label, spinner )

        label = Gtk.Label( "Summary" )
        label.set_margin_left( 25 )
        label.set_halign( Gtk.Align.START )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        grid.attach( label, 0, 2, 1, 1 )

        summary = Gtk.Entry()
        summary.set_text( self.werewolfWarningTextSummary )
        summary.set_width_chars( len( self.werewolfWarningTextSummary.strip() ) * 3 / 2 ) # Any whitespace throws off the width, so trim them and base the width of the non-whitespace text.
        summary.set_tooltip_text( "The summary text for the werewolf notification" )
        summary.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        grid.attach( summary, 1, 2, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", self.onShowWerewolfWarningCheckbox, label, summary )

        label = Gtk.Label( "Body" )
        label.set_margin_left( 25 )
        label.set_halign( Gtk.Align.START )
        label.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        grid.attach( label, 0, 3, 1, 1 )

        body = Gtk.Entry()
        body.set_text( self.werewolfWarningTextBody )
        body.set_width_chars( len( self.werewolfWarningTextBody.strip() ) * 3 / 2 ) # Any whitespace throws off the width, so trim them and base the width of the non-whitespace text.
        body.set_tooltip_text( "The body text for the werewolf notification" )
        body.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        grid.attach( body, 1, 3, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", self.onShowWerewolfWarningCheckbox, label, body )

        test = Gtk.Button( "Test" )
        test.set_halign( Gtk.Align.END )
        test.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        if notifyImported:
            test.connect( "clicked", self.onTestClicked, summary, body )
            test.set_tooltip_text( "Show the notification bubble" )
        else:
            test.set_sensitive( False )
            test.set_tooltip_text( "Notifications are not possible on your system" )

        grid.attach( test, 1, 4, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", self.onShowWerewolfWarningCheckbox, test, test )

        notebook.append_page( grid, Gtk.Label( "Full Moon" ) )

        # Location settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        label = Gtk.Label( "City" )
        label.set_halign( Gtk.Align.START )

        grid.attach( label, 0, 0, 1, 1 )

        global _city_data
        cities = sorted( _city_data.keys(), key = locale.strxfrm )
        city = Gtk.ComboBoxText.new_with_entry()
        city.set_tooltip_text( "To reset the cities (with factory lat/long/elev), create a bogus city and restart the indicator" )
        city.set_hexpand( True ) # Only need to set this once and all objects will expand.
        for c in cities:
            city.append_text( c )

        grid.attach( city, 1, 0, 1, 1 )

        label = Gtk.Label( "Latitude (DD)" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 1, 1, 1 )

        latitude = Gtk.Entry()
        latitude.set_tooltip_text( "Latitude of your location in decimal degrees" )
        grid.attach( latitude, 1, 1, 1, 1 )

        label = Gtk.Label( "Longitude (DD)" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        longitude = Gtk.Entry()
        longitude.set_tooltip_text( "Longitude of your location in decimal degrees" )
        grid.attach( longitude, 1, 2, 1, 1 )

        label = Gtk.Label( "Elevation (m)" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        elevation = Gtk.Entry()
        elevation.set_tooltip_text( "Height in metres above sea level" )
        grid.attach( elevation, 1, 3, 1, 1 )

        city.connect( "changed", self.onCityChanged, latitude, longitude, elevation )
        city.set_active( cities.index( self.cityName ) )

        notebook.append_page( grid, Gtk.Label( "Location" ) )

        # General settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_tooltip_text( "Run the indicator automatically" )
        autostartCheckbox.set_active( os.path.exists( IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 0, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "General" ) )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorLunar.ICON )

        while True:
            self.dialog.show_all()
            if self.dialog.run() != Gtk.ResponseType.OK: break

            cityValue = city.get_active_text()
            if cityValue == "":
                pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, "City cannot be empty." )
                city.grab_focus()
                continue

            latitudeValue = latitude.get_text().strip()
            if latitudeValue == "" or not pythonutils.isNumber( latitudeValue ) or float( latitudeValue ) > 90 or float( latitudeValue ) < -90:
                pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, "Latitude must be a number between 90 and -90 inclusive." )
                latitude.grab_focus()
                continue

            longitudeValue = longitude.get_text().strip()
            if longitudeValue == "" or not pythonutils.isNumber( longitudeValue ) or float( longitudeValue ) > 180 or float( longitudeValue ) < -180:
                pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, "Longitude must be a number between 180 and -180 inclusive." )
                longitude.grab_focus()
                continue

            elevationValue = elevation.get_text().strip()
            if elevationValue == "" or not pythonutils.isNumber( elevationValue ) or float( elevationValue ) > 10000 or float( elevationValue ) < 0:
                pythonutils.showMessage( self.dialog, Gtk.MessageType.ERROR, "Elevation must be a number number between 0 and 10000 inclusive." )
                elevation.grab_focus()
                continue

            self.planets = [ ]
            for planetInfo in planetStore:
                if planetInfo[ 1 ]: self.planets.append( planetInfo[ 0 ] )

            self.stars = [ ]
            for starInfo in starStore:
                if starInfo[ 1 ]: self.stars.append( starInfo[ 0 ] )

            if len( self.satelliteTLEData ) == 0:
                # No satellite TLE data exists (due to a download error).
                # Fudge the last update to be in the past to force a download.
                # Don't initialise the list of satellites the user has chosen as this data is still valid despite a failed download.
                self.lastUpdateTLE = datetime.datetime.now() - datetime.timedelta( hours = 24 )
            else:
                self.onlyShowVisibleSatellitePasses = showSatellitePassesVisibleCheckbox.get_active()
                self.showSatellitesAsSubMenu = showSatellitesAsSubmenuCheckbox.get_active()
                self.showSatelliteSubsequentPasses = showSatelliteSubsequentPassesCheckbox.get_active()
                self.showSatelliteNotification = showSatelliteNotificationCheckbox.get_active()
                self.showSatelliteNumber = showSatelliteNumberCheckbox.get_active()
                self.satellites = [ ]
                for satelliteInfo in satelliteStore:
                    if satelliteInfo[ 2 ]: self.satellites.append( [ satelliteInfo[ 0 ], satelliteInfo[ 1 ] ] )

            self.displayPattern = displayPattern.get_text()
            self.showPlanetsAsSubMenu = showPlanetsAsSubmenuCheckbox.get_active()
            self.showStarsAsSubMenu = showStarsAsSubmenuCheckbox.get_active()
            self.showWerewolfWarning = showWerewolfWarningCheckbox.get_active()
            self.werewolfWarningStartIlluminationPercentage = spinner.get_value_as_int()
            self.werewolfWarningTextSummary = summary.get_text()
            self.werewolfWarningTextBody = body.get_text()

            self.cityName = cityValue
            _city_data[ self.cityName ] = ( str( latitudeValue ), str( longitudeValue ), float( elevationValue ) )

            self.saveSettings()

            if not os.path.exists( IndicatorLunar.AUTOSTART_PATH ):
                os.makedirs( IndicatorLunar.AUTOSTART_PATH )

            if autostartCheckbox.get_active():
                try:
                    shutil.copy( IndicatorLunar.DESKTOP_PATH + IndicatorLunar.DESKTOP_FILE, IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE )
                except Exception as e:
                    logging.exception( e )
            else:
                try:
                    os.remove( IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE )
                except: pass

            GLib.source_remove( self.eventSourceID )
            self.update()
            break

        self.dialog.destroy()
        self.dialog = None


    def onDisplayTagDoubleClick( self, tree, rowNumber, treeViewColumn, displayPattern ):
        model, treeiter = tree.get_selection().get_selected()
        displayPattern.insert_text( "[" + model[ treeiter ][ 0 ] + "]", displayPattern.get_position() )


    def onTestClicked( self, button, summary, body ):
        self.createIcon( 100, None )

        # The notification summary text must not be empty (at least on Unity).
        if summary.get_text() == "":
            Notify.Notification.new( " ", body.get_text(), IndicatorLunar.SVG_FULL_MOON_FILE ).show()
        else:
            Notify.Notification.new( summary.get_text(), body.get_text(), IndicatorLunar.SVG_FULL_MOON_FILE ).show()

        os.remove( IndicatorLunar.SVG_FULL_MOON_FILE )


    def onPlanetToggled( self, widget, path, planetStore, displayTagsStore ):
        planetStore[ path ][ 1 ] = not planetStore[ path ][ 1 ]
        planetName = planetStore[ path ][ 0 ].upper()

        if planetStore[ path ][ 1 ]:
            displayTagsStore.append( [ planetName + IndicatorLunar.TAG_ILLUMINATION, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + IndicatorLunar.TAG_CONSTELLATION, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + IndicatorLunar.TAG_TROPICAL_SIGN, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + IndicatorLunar.TAG_DISTANCE_TO_EARTH, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + IndicatorLunar.TAG_DISTANCE_TO_SUN, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + IndicatorLunar.TAG_BRIGHT_LIMB, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + IndicatorLunar.TAG_RISE_TIME, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + IndicatorLunar.TAG_SET_TIME, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
        else:
            iter = displayTagsStore.get_iter_first()
            while iter is not None:
                if displayTagsStore[ iter ][ 0 ].startswith( planetName ):
                    if displayTagsStore.remove( iter ) == False: iter = None # Remove returns True if there are more items (and iter automatically moves to that item).
                else:
                    iter = displayTagsStore.iter_next( iter )


    def onStarToggled( self, widget, path, starStore, displayTagsStore ):
        starStore[ path ][ 1 ] = not starStore[ path ][ 1 ]
        starName = starStore[ path ][ 0 ].upper()

        if starStore[ path ][ 1 ]:
            displayTagsStore.append( [ starName + IndicatorLunar.TAG_RIGHT_ASCENSION, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + IndicatorLunar.TAG_DECLINATION, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + IndicatorLunar.TAG_AZIMUTH, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + IndicatorLunar.TAG_ALTITUDE, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + IndicatorLunar.TAG_MAGNITUDE, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
        else:
            iter = displayTagsStore.get_iter_first()
            while iter is not None:
                if displayTagsStore[ iter ][ 0 ].startswith( starName ):
                    if displayTagsStore.remove( iter ) == False: iter = None # Remove returns True if there are more items (and iter automatically moves to that item).
                else:
                    iter = displayTagsStore.iter_next( iter )


    def onSatelliteToggled( self, widget, path, satelliteStore, displayTagsStore, satelliteStoreSort ):
        # Convert the index in the sorted model to the index in the underlying (child) modeel.
        childPath = satelliteStoreSort.convert_path_to_child_path( Gtk.TreePath.new_from_string( path ) )

        satelliteStore[ childPath ][ 2 ] = not satelliteStore[ childPath ][ 2 ]
        key = self.getSatelliteNameNumber( satelliteStore[ childPath ][ 0 ].upper(), satelliteStore[ childPath ][ 1 ] )

        if satelliteStore[ childPath ][ 1 ]:
            displayTagsStore.append( [ key + IndicatorLunar.TAG_RISE_TIME, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ key + IndicatorLunar.TAG_RISE_AZIMUTH, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ key + IndicatorLunar.TAG_SET_TIME, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ key + IndicatorLunar.TAG_SET_AZIMUTH, IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
        else:
            iter = displayTagsStore.get_iter_first()
            while iter is not None:
                if displayTagsStore[ iter ][ 0 ].startswith( key ):
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


    def onShowWerewolfWarningCheckbox( self, source, widget1, widget2 ):
        widget1.set_sensitive( source.get_active() )
        widget2.set_sensitive( source.get_active() )


    def getSatelliteTLEData( self ):
        try:
            self.satelliteTLEData = { } # Key 'satellite name - satellite number'; value satellite.Info object.
            data = urlopen( IndicatorLunar.SATELLITE_TLE_URL ).read().decode( "utf8" ).splitlines()
            for i in range( 0, len( data ), 3 ):
                satelliteInfo = satellite.Info( data[ i ].strip(), data[ i + 1 ].strip(), data[ i + 2 ].strip() )
                key = self.getSatelliteNameNumber( satelliteInfo.getName(), satelliteInfo.getNumber() )
                self.satelliteTLEData[ key ] = satelliteInfo

        except Exception as e:
            self.satelliteTLEData = { } # Empty data indicates error.
            logging.exception( e )
            logging.error( "Error downloading satellite TLE data from " + IndicatorLunar.SATELLITE_TLE_URL )

        self.lastUpdateTLE = datetime.datetime.now()


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
        self.displayPattern = IndicatorLunar.DISPLAY_PATTERN_DEFAULT
        self.onlyShowVisibleSatellitePasses = False
        self.satellites = [ ]
        self.showPlanetsAsSubMenu = False
        self.showSatelliteNotification = True
        self.showSatelliteNumber = False
        self.showSatelliteSubsequentPasses = False
        self.showSatellitesAsSubMenu = False
        self.showStarsAsSubMenu = False
        self.showWerewolfWarning = True
        self.stars = [ ]
        self.werewolfWarningStartIlluminationPercentage = 100
        self.werewolfWarningTextBody = IndicatorLunar.WEREWOLF_WARNING_TEXT_BODY
        self.werewolfWarningTextSummary = IndicatorLunar.WEREWOLF_WARNING_TEXT_SUMMARY

        # By default, all planets should be displayed, unless the user chooses otherwise.
        self.planets = [ ]
        for planet in IndicatorLunar.PLANETS:
            self.planets.append( planet[ 0 ] )

        if os.path.isfile( IndicatorLunar.SETTINGS_FILE ):
            try:
                with open( IndicatorLunar.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                global _city_data
                cityElevation = settings.get( IndicatorLunar.SETTINGS_CITY_ELEVATION, _city_data.get( self.cityName )[ 2 ] )
                cityLatitude = settings.get( IndicatorLunar.SETTINGS_CITY_LATITUDE, _city_data.get( self.cityName )[ 0 ] )
                cityLongitude = settings.get( IndicatorLunar.SETTINGS_CITY_LONGITUDE, _city_data.get( self.cityName )[ 1 ] )
                self.cityName = settings.get( IndicatorLunar.SETTINGS_CITY_NAME, self.cityName )
                self.displayPattern = settings.get( IndicatorLunar.SETTINGS_DISPLAY_PATTERN, self.displayPattern )
                self.onlyShowVisibleSatellitePasses = settings.get( IndicatorLunar.SETTINGS_ONLY_SHOW_VISIBLE_SATELLITE_PASSES, self.onlyShowVisibleSatellitePasses )
                self.planets = settings.get( IndicatorLunar.SETTINGS_PLANETS, self.planets )
                self.satellites = settings.get( IndicatorLunar.SETTINGS_SATELLITES, self.satellites )
                self.showPlanetsAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_PLANETS_AS_SUBMENU, self.showPlanetsAsSubMenu )
                self.showSatelliteNotification = settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITE_NOTIFICATION, self.showSatelliteNotification )
                self.showSatelliteNumber = settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITE_NUMBER, self.showSatelliteNumber )
                self.showSatelliteSubsequentPasses= settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITE_SUBSEQUENT_PASSES, self.showSatelliteSubsequentPasses )
                self.showSatellitesAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITES_AS_SUBMENU, self.showSatellitesAsSubMenu )
                self.showStarsAsSubMenu = settings.get( IndicatorLunar.SETTINGS_SHOW_STARS_AS_SUBMENU, self.showStarsAsSubMenu )
                self.showWerewolfWarning = settings.get( IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING, self.showWerewolfWarning )
                self.stars = settings.get( IndicatorLunar.SETTINGS_STARS, self.stars )
                self.werewolfWarningStartIlluminationPercentage = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE, self.werewolfWarningStartIlluminationPercentage )
                self.werewolfWarningTextBody = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_TEXT_BODY, self.werewolfWarningTextBody )
                self.werewolfWarningTextSummary = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_TEXT_SUMMARY, self.werewolfWarningTextSummary )

                # Insert/overwrite the cityName and information into the cities...
                _city_data[ self.cityName ] = ( str( cityLatitude ), str( cityLongitude ), float( cityElevation ) )

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
                IndicatorLunar.SETTINGS_DISPLAY_PATTERN: self.displayPattern,
                IndicatorLunar.SETTINGS_ONLY_SHOW_VISIBLE_SATELLITE_PASSES: self.onlyShowVisibleSatellitePasses,
                IndicatorLunar.SETTINGS_PLANETS: self.planets,
                IndicatorLunar.SETTINGS_SATELLITES: self.satellites,
                IndicatorLunar.SETTINGS_SHOW_PLANETS_AS_SUBMENU: self.showPlanetsAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_SATELLITE_NOTIFICATION: self.showSatelliteNotification,
                IndicatorLunar.SETTINGS_SHOW_SATELLITE_NUMBER: self.showSatelliteNumber,
                IndicatorLunar.SETTINGS_SHOW_SATELLITE_SUBSEQUENT_PASSES: self.showSatelliteSubsequentPasses,
                IndicatorLunar.SETTINGS_SHOW_SATELLITES_AS_SUBMENU: self.showSatellitesAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_STARS_AS_SUBMENU: self.showStarsAsSubMenu,
                IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING: self.showWerewolfWarning,
                IndicatorLunar.SETTINGS_STARS: self.stars,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE: self.werewolfWarningStartIlluminationPercentage,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_TEXT_BODY: self.werewolfWarningTextBody,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_TEXT_SUMMARY: self.werewolfWarningTextSummary
            }

            with open( IndicatorLunar.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorLunar.SETTINGS_FILE )


if __name__ == "__main__": IndicatorLunar().main()