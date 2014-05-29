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


#TODO Search for next pass and similar...do I need to catch valueerror?  
# Related to circumpolar error
# http://rhodesmill.org/pyephem/quick.html 


# TODO Perhaps it's possible to distinguish a visible transit from all transits.
# http://stackoverflow.com/questions/12845908/horizon-for-earth-satellites
# http://www.sharebrained.com/2011/10/18/track-the-iss-pyephem/
# http://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible


#TODO Could make the rise/set for satellites show all transits for the next 5 days or whatever the upper limit is using the TLE.
# Compare results against heavensabove or "nyse". 


# TODO Check other places for rise/set calculations ... need to guard against ValueError (AlwaysUp and NeverUp)?
#Test for a location near the poles.


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
    VERSION = "1.0.42"
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
    SETTINGS_PLANETS = "planets"
    SETTINGS_SATELLITES = "satellites"
    SETTINGS_SHOW_SATELLITE_NOTIFICATION = "showSatelliteNotification"
    SETTINGS_SHOW_SATELLITE_NUMBER = "showSatelliteNumber"
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

    SATELLITE_TEXT_SUMMARY = "      ...is in transit!"
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


    def __init__( self ):
        filehandler = logging.FileHandler( filename = IndicatorLunar.LOG, mode = "a", delay = True )
        logging.basicConfig( format = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                             datefmt = "%H:%M:%S", level = logging.DEBUG,
                             handlers = [ filehandler ] )

        self.dialog = None
        self.data = { }
        self.dataPrevious = { }

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
#TODO Somehow ensure that a given satellite only notifies once per transit.
        # Satellite notification.
        # Need to use data from the previous run as the rise/set is always the .....
        # If the satellite is up and the calculations are updated, the current rise/set will be overwritten with the next rise/set.
#TODO Once the satellite menu stuff is done (keep a rise/set time for the duration of the transit) then revisit this and make sure it's okay.        
#         if notifyImported and self.showSatelliteNotification:
#             ephemNowInLocalTime = ephem.Date( self.localiseAndTrim( ephemNow ) )
#             for satelliteNameNumber in self.satellites:
#                 riseTimeKey = self.getSatelliteNameNumber( satelliteNameNumber[ 0 ], ( satelliteNameNumber[ 1 ] ) ) + " RISE TIME"
#                 setTimeKey = self.getSatelliteNameNumber( satelliteNameNumber[ 0 ], ( satelliteNameNumber[ 1 ] ) ) + " SET TIME"
#                 if riseTimeKey in self.data and ephemNowInLocalTime > ephem.Date( self.data[ riseTimeKey ] ) and setTimeKey in self.data and ephemNowInLocalTime < ephem.Date( self.data[ setTimeKey ] ):
#                     if self.showSatelliteNumber:
#                         Notify.Notification.new( satelliteNameNumber[ 0 ] + " - " + satelliteNameNumber[ 1 ], IndicatorLunar.SATELLITE_TEXT_SUMMARY, IndicatorLunar.SVG_SATELLITE_ICON ).show()
#                     else:
#                         Notify.Notification.new( satelliteNameNumber[ 0 ], IndicatorLunar.SATELLITE_TEXT_SUMMARY, IndicatorLunar.SVG_SATELLITE_ICON ).show()

        # Update the satellite TLE data at most every 12 hours.
        if datetime.datetime.now() > ( self.lastUpdateTLE + datetime.timedelta( hours = 12 ) ): self.getSatelliteTLEData() 

        # Reset the data on each update, otherwise data will accumulate (if a star/satellite was added then removed, the computed data remains).
        self.dataPrevious = self.data
        self.data = { }

        # This is UTC used in all calculations.  When it comes time to display, it is converted to local time.
        ephemNow = ephem.now()

        city = ephem.city( self.cityName )
        city.date = ephemNow
        self.data[ "CITY NAME" ] = self.cityName

        lunarIlluminationPercentage = int( round( ephem.Moon( city ).phase ) )
        lunarPhase = self.getLunarPhase( ephemNow, lunarIlluminationPercentage )

        self.buildMenu( city, ephemNow, lunarPhase )

        # Parse the display pattern and show it...
        #
        # For Ubuntu (Unity), an icon and label can co-exist and there is no tooltip. The icon is always to the right of the label.
        # On Ubuntu 13.10 (might be a bug), an icon must be displayed, so if no icon tag is present, display a 1 pixel SVG.
        #
        # On non Unity (Lubuntu, etc), only an icon can be displayed - text is shown as a tooltip.
        parsedOutput = self.displayPattern
        for key in self.data.keys():
            parsedOutput = parsedOutput.replace( "[" + key + "]", self.data[ key ] )

        self.createIcon( lunarIlluminationPercentage, self.getBrightLimbAngleRelativeToZenith( city, ephem.Moon( city ) ) )
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


    def buildMenu( self, city, ephemNow, lunarPhase ):
        nextUpdates = [ ] # Stores the date/time for each upcoming rise/set/phase...used to find the date/time closest to now and that will be the next time for an update.

        if self.appindicatorImported:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if not, GTK complains).
        menu = Gtk.Menu()

        self.createMoonMenu( menu, city, nextUpdates, ephemNow, lunarPhase )

        self.createSunMenu( menu, city, nextUpdates, ephemNow )
        
        # Planets
        if len( self.planets ) > 0:
            menu.append( Gtk.MenuItem( "Planets" ) )

            for planet in IndicatorLunar.PLANETS:
                if planet[ 0 ] in self.planets:
                    menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + planet[ 0 ] )
                    menu.append( menuItem )
                    planet[ 1 ].compute( city )
                    self.createBodyMenu( menuItem, city, planet[ 1 ], nextUpdates, ephemNow )

        self.createStarsMenu( menu, city )

        self.createSatellitesMenu( menu, city, nextUpdates )

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

        print( datetime.datetime.now(), nextUpdateInSeconds)  #TODO Remove!
        GLib.timeout_add_seconds( nextUpdateInSeconds, self.update )


    def createMoonMenu( self, menu, city, nextUpdates, ephemNow, lunarPhase ):
        menuItem = Gtk.MenuItem( "Moon" )
        menu.append( menuItem )

        self.createBodyMenu( menuItem, city, ephem.Moon( city ), nextUpdates, ephemNow )

        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )

        self.data[ "MOON PHASE" ] = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ]
        menuItem.get_submenu().append( Gtk.MenuItem( "Phase: " + self.data[ "MOON PHASE" ] ) )

        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
        menuItem.get_submenu().append( Gtk.MenuItem( "Next Phases" ) )

        # Determine which phases occur by date rather than using the phase calculated
        # as the phase (illumination) rounds numbers and so a given phase is entered earlier than what is official.
        nextPhases = [ ]

        self.data[ "MOON FIRST QUARTER" ] = self.localiseAndTrim( ephem.next_first_quarter_moon( ephemNow ) )
        nextPhases.append( [ self.data[ "MOON FIRST QUARTER" ], "First Quarter: " ] )

        self.data[ "MOON FULL" ] = self.localiseAndTrim( ephem.next_full_moon( ephemNow ) )
        nextPhases.append( [ self.data[ "MOON FULL" ], "Full: " ] )

        self.data[ "MOON THIRD QUARTER" ] = self.localiseAndTrim( ephem.next_last_quarter_moon( ephemNow ) )
        nextPhases.append( [ self.data[ "MOON THIRD QUARTER" ], "Third Quarter: " ] )

        self.data[ "MOON NEW" ] = self.localiseAndTrim( ephem.next_new_moon( ephemNow ) )
        nextPhases.append( [ self.data[ "MOON NEW" ], "New: " ] )

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


    def createSunMenu( self, menu, city, nextUpdates, ephemNow ):
        menuItem = Gtk.MenuItem( "Sun" )
        menu.append( menuItem )

        subMenu = Gtk.Menu()
        menuItem.set_submenu( subMenu )

        sun = ephem.Sun( city )

        self.data[ "SUN CONSTELLATION" ] = ephem.constellation( sun )[ 1 ]
        subMenu.append( Gtk.MenuItem( "Constellation: " + self.data[ "SUN CONSTELLATION" ] ) )

        self.data[ "SUN TROPICAL SIGN" ] = self.getTropicalSign( sun, ephemNow )
        subMenu.append( Gtk.MenuItem( "Tropical Sign: " + self.data[ "SUN TROPICAL SIGN" ] ) )

        self.data[ "SUN DISTANCE TO EARTH" ] = str( round( sun.earth_distance, 4 ) ) + " AU"
        subMenu.append( Gtk.MenuItem( "Distance to Earth: " + self.data[ "SUN DISTANCE TO EARTH" ] ) )

        subMenu.append( Gtk.SeparatorMenuItem() )

        self.createRADecAzAltMagMenu( subMenu, sun )

        subMenu.append( Gtk.SeparatorMenuItem() )

        # Rising/Setting.
        rising = city.next_rising( sun )
        self.data[ "SUN NEXT RISING" ] = self.localiseAndTrim( rising )
        setting = city.next_setting( sun )
        self.data[ "SUN NEXT SETTING" ] = self.localiseAndTrim( setting )
        if rising > setting:
            subMenu.append( Gtk.MenuItem( "Set: " + self.data[ "SUN NEXT SETTING" ] ) )
            subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ "SUN NEXT RISING" ] ) )
        else:
            subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ "SUN NEXT RISING" ] ) )
            subMenu.append( Gtk.MenuItem( "Set: " + self.data[ "SUN NEXT SETTING" ] ) )

        nextUpdates.append( rising )
        nextUpdates.append( setting )

        subMenu.append( Gtk.SeparatorMenuItem() )

        # Solstice/Equinox.
        equinox = ephem.next_equinox( ephemNow )
        self.data[ "SUN EQUINOX" ] = self.localiseAndTrim( equinox )
        solstice = ephem.next_solstice( ephemNow )
        self.data[ "SUN SOLSTICE" ] = self.localiseAndTrim( solstice )
        if equinox < solstice:
            subMenu.append( Gtk.MenuItem( "Equinox: " + self.data[ "SUN EQUINOX" ] ) )
            subMenu.append( Gtk.MenuItem( "Solstice: " + self.data[ "SUN SOLSTICE" ] ) )
        else:
            subMenu.append( Gtk.MenuItem( "Solstice: " + self.data[ "SUN SOLSTICE" ] ) )
            subMenu.append( Gtk.MenuItem( "Equinox: " + self.data[ "SUN EQUINOX" ] ) )

        nextUpdates.append( equinox )
        nextUpdates.append( solstice )

        # Eclipse.
        eclipseInformation = eclipse.getSolarEclipseForUTC( ephemNow.datetime() )
        if eclipseInformation is not None:
            subMenu.append( Gtk.SeparatorMenuItem() )
            self.createEclipseMenu( subMenu, eclipseInformation, "SUN" )


    def createBodyMenu( self, bodyMenuItem, city, body, nextUpdates, ephemNow ):
        subMenu = Gtk.Menu()

        self.data[ body.name.upper() + " ILLUMINATION" ] = str( int( round( body.phase ) ) ) + "%"
        subMenu.append( Gtk.MenuItem( "Illumination: " + self.data[ body.name.upper() + " ILLUMINATION" ] ) )

        self.data[ body.name.upper() + " CONSTELLATION" ] = ephem.constellation( body )[ 1 ]
        subMenu.append( Gtk.MenuItem( "Constellation: " + self.data[ body.name.upper() + " CONSTELLATION" ] ) )

        self.data[ body.name.upper() + " TROPICAL SIGN" ] = self.getTropicalSign( body, ephemNow )
        subMenu.append( Gtk.MenuItem( "Tropical Sign: " + self.data[ body.name.upper() + " TROPICAL SIGN" ] ) )

        self.data[ body.name.upper() + " DISTANCE TO EARTH" ] = str( round( body.earth_distance, 4 ) ) + " AU"
        subMenu.append( Gtk.MenuItem( "Distance to Earth: " + self.data[ body.name.upper() + " DISTANCE TO EARTH" ] ) )

        self.data[ body.name.upper() + " DISTANCE TO SUN" ] = str( round( body.sun_distance, 4 ) ) + " AU"
        subMenu.append( Gtk.MenuItem( "Distance to Sun: " + self.data[ body.name.upper() + " DISTANCE TO SUN" ] ) )

        self.data[ body.name.upper() + " BRIGHT LIMB" ] = str( round( self.getBrightLimbAngleRelativeToZenith( city, body ) ) ) + "°"
        subMenu.append( Gtk.MenuItem( "Bright Limb: " + self.data[ body.name.upper() + " BRIGHT LIMB" ] ) )

        subMenu.append( Gtk.SeparatorMenuItem() )

        self.createRADecAzAltMagMenu( subMenu, body )

        subMenu.append( Gtk.SeparatorMenuItem() )

        # Must compute the previous information (illumination, constellation, phase and so on BEFORE rising/setting).
        # For some reason the values, most notably phase, are different (and wrong) if calculated AFTER rising/setting are calculated.
        rising = city.next_rising( body )
        self.data[ body.name.upper() + " RISING" ] = str( self.localiseAndTrim( rising ) )
        setting = city.next_setting( body )
        self.data[ body.name.upper() + " SETTING" ] = str( self.localiseAndTrim( setting ) )
        if rising > setting:
            subMenu.append( Gtk.MenuItem( "Set: " + self.data[ body.name.upper() + " SETTING" ] ) )
            subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ body.name.upper() + " RISING" ] ) )
        else:
            subMenu.append( Gtk.MenuItem( "Rise: " + self.data[ body.name.upper() + " RISING" ] ) )
            subMenu.append( Gtk.MenuItem( "Set: " + self.data[ body.name.upper() + " SETTING" ] ) )

        bodyMenuItem.set_submenu( subMenu )

        nextUpdates.append( rising )
        nextUpdates.append( setting )


    # The rise/set times for stars are not included in the display.
    # Depending on the star/city combination, some stars are always up or never up (particularly at high latitudes).
    def createStarsMenu( self, menu, city ):
        if len( self.stars ) == 0: return

        menuItem = Gtk.MenuItem( "Stars" )
        menu.append( menuItem )

        for starName in self.stars:
            menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + starName )
            menu.append( menuItem )

            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )

            star = ephem.star( starName )
            star.compute( city )

            self.createRADecAzAltMagMenu( subMenu, star )


    # Uses TLE data collated by Dr T S Kelso (http://celestrak.com/NORAD/elements) with PyEphem to compute satellite rise/transit/set times.
    # Other sources/background:
    #   http://spotthestation.nasa.gov/sightings
    #   http://www.n2yo.com/passes/?s=25544
    #   http://www.heavens-above.com/
    def createSatellitesMenuORIGINAL( self, menu, city, nextUpdates ):
        if len( self.satellites ) == 0: return

        if len( self.satelliteTLEData ) == 0: return # No point adding "non information" to the menu.  The preferences will tell the user there is a problem.

        menuItem = Gtk.MenuItem( "Satellites" )
        menu.append( menuItem )

        for satelliteNameNumber in sorted( self.satellites, key = lambda x: ( x[ 0 ], x[ 1 ] ) ):
            if self.showSatelliteNumber:
                menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + satelliteNameNumber[ 0 ] + " - " + satelliteNameNumber[ 1 ] )
            else:
                menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + satelliteNameNumber[ 0 ] )

            menu.append( menuItem )

            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )

            key = self.getSatelliteNameNumber( satelliteNameNumber[ 0 ], satelliteNameNumber[ 1 ] )
            if key in self.satelliteTLEData:
                satelliteInfo = self.satelliteTLEData[ key ]
                nextPass = None
                try:
                    nextPass = city.next_pass( ephem.readtle( satelliteInfo.getName(), satelliteInfo.getTLELine1(), satelliteInfo.getTLELine2() ) )
                except ValueError as e:
#TODO Possible to have a better error message?  
#Can't determine if the error is always up or ever up (or something else). 
                    subMenu.append( Gtk.MenuItem( "No rise/set information." ) ) # Occurs when the satellite is always up or never up.
                    continue

#TODO Somehow ensure that a given satellite only notifies once per transit.

#TODO An update occurs as a result of the rise time and the new rise/set time overwrite the current rise/set time.
#                 ephemNowInLocalTime = ephem.Date( self.localiseAndTrim( ephemNow ) )

                tag = self.getSatelliteNameNumber( satelliteNameNumber[ 0 ], satelliteNameNumber[ 1 ] )

                subMenu.append( Gtk.MenuItem( "Rise" ) )

                self.data[ tag + " RISE TIME" ] =  self.localiseAndTrim( nextPass[ 0 ] )
                subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Time: " + self.data[ tag + " RISE TIME" ] ) )

                self.data[ tag + " RISE AZIMUTH" ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 1 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 1 ] ) ) + ")"
                subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Azimuth: " + self.data[ tag + " RISE AZIMUTH" ] ) )

                subMenu.append( Gtk.SeparatorMenuItem() )

                subMenu.append( Gtk.MenuItem( "Set" ) )

                self.data[ tag + " SET TIME" ] =  self.localiseAndTrim( nextPass[ 4 ] )
                subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Time: " + self.data[ tag + " SET TIME" ] ) )

                self.data[ tag + " SET AZIMUTH" ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 5 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 5 ] ) ) + ")"
                subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Azimuth: " + self.data[ tag + " SET AZIMUTH" ] ) )

                nextUpdates.append( nextPass[ 0 ] )
                nextUpdates.append( nextPass[ 4 ] )
            else:
                subMenu.append( Gtk.MenuItem( "No data!" ) )


    # Uses TLE data collated by Dr T S Kelso (http://celestrak.com/NORAD/elements) with PyEphem to compute satellite rise/transit/set times.
    # Other sources/background:
    #   http://spotthestation.nasa.gov/sightings
    #   http://www.n2yo.com/passes/?s=25544
    #   http://www.heavens-above.com/
    #
    # For planets/stars, the next rise/set time is shown.
    # If already above the horizon, the set time is shown followed by the rise time for the next pass.
    # This makes sense as planets/stars are slow moving.
    # As satellites are faster moving and pass several times a day, a different approach is used.
    # When a notification is displayed indicating a satellite is now passing overhead,
    # the user may want to see the rise/set for the current pass (rather than the set for the current pass and rise for the next pass).
    # Therefore when doing an update...
    # If a satellite is yet to rise, show the upcoming rise/set time.
    # If a satellite is currently passing over, show the rise/set time for that pass.
    # This allows the user to see the rise/set time for the current pass as it is happening.
    # When the pass completes and an update occurs, the rise/set for the next pass will be displayed.
    def createSatellitesMenu( self, menu, city, nextUpdates ):
        if len( self.satellites ) == 0: return

        if len( self.satelliteTLEData ) == 0: return # No point adding "non information" to the menu.  The preferences will tell the user there is a problem.

        menuItem = Gtk.MenuItem( "Satellites" )
        menu.append( menuItem )

        for satelliteNameNumber in sorted( self.satellites, key = lambda x: ( x[ 0 ], x[ 1 ] ) ):
            if self.showSatelliteNumber:
                menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + satelliteNameNumber[ 0 ] + " - " + satelliteNameNumber[ 1 ] )
            else:
                menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + satelliteNameNumber[ 0 ] )

            menu.append( menuItem )

            subMenu = Gtk.Menu()
            menuItem.set_submenu( subMenu )

            key = self.getSatelliteNameNumber( satelliteNameNumber[ 0 ], satelliteNameNumber[ 1 ] )
            if not key in self.satelliteTLEData:
                subMenu.append( Gtk.MenuItem( "No data!" ) )
                continue

            satelliteInfo = self.satelliteTLEData[ key ]
            nextPass = None
            try:
                nextPass = city.next_pass( ephem.readtle( satelliteInfo.getName(), satelliteInfo.getTLELine1(), satelliteInfo.getTLELine2() ) )
            except ValueError:
                subMenu.append( Gtk.MenuItem( "Never rises or never sets." ) ) # Occurs when the satellite is always up or never up.
                continue

            if nextPass[ 0 ] < nextPass[ 4 ]:
                # The satellite is below the horizon.
                self.data[ key + " RISE TIME" ] =  self.localiseAndTrim( nextPass[ 0 ] )
                self.data[ key + " RISE AZIMUTH" ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 1 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 1 ] ) ) + ")"
                self.data[ key + " SET TIME" ] =  self.localiseAndTrim( nextPass[ 4 ] )
                self.data[ key + " SET AZIMUTH" ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 5 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 5 ] ) ) + ")"

                nextUpdates.append( nextPass[ 0 ] )
                nextUpdates.append( nextPass[ 4 ] )
            else:
                # The satellite is passing over and so the calculated rise time is for the next pass.
                # Obtain the rise time/azimuth from the previous run.
                if ( key + " RISE TIME" ) in self.dataPrevious and ( key + " RISE AZIMUTH" ) in self.dataPrevious:
                    # The data from the previous run is available...
                    self.data[ key + " RISE TIME" ] =  self.dataPrevious[ key + " RISE TIME" ]
                    self.data[ key + " RISE AZIMUTH" ] =  self.dataPrevious[ key + " RISE AZIMUTH" ]
                    self.data[ key + " SET TIME" ] =  self.localiseAndTrim( nextPass[ 4 ] )
                    self.data[ key + " SET AZIMUTH" ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 5 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 5 ] ) ) + ")"

                    nextUpdates.append( nextPass[ 4 ] ) # Don't add the rise time as it is in the past!
                else:
                    # There is no previous data (typically because this is the first run).
                    # So just use the next pass.
                    difference = nextPass[ 0 ] - nextPass[ 4 ] # Date/time difference between the current set and next rise.
                    ephemFuture = ephem.Date( city.date + ( difference / 2.0 ) ) # Set a future date to be half the difference between the set time and the next rise time.
                    cityFuture = ephem.Observer()
                    cityFuture.lat = city.lat
                    cityFuture.long = city.long
                    cityFuture.elevation = city.elevation
                    cityFuture.date = ephemFuture
                    try:
                        nextPass = cityFuture.next_pass( ephem.readtle( satelliteInfo.getName(), satelliteInfo.getTLELine1(), satelliteInfo.getTLELine2() ) )
                    except ValueError:
                        subMenu.append( Gtk.MenuItem( "Never rises or never sets." ) ) # Occurs when the satellite is always up or never up.
                        continue

                    self.data[ key + " RISE TIME" ] =  self.localiseAndTrim( nextPass[ 0 ] )
                    self.data[ key + " RISE AZIMUTH" ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 1 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 1 ] ) ) + ")"
                    self.data[ key + " SET TIME" ] =  self.localiseAndTrim( nextPass[ 4 ] )
                    self.data[ key + " SET AZIMUTH" ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( nextPass[ 5 ] ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( nextPass[ 5 ] ) ) + ")"

                    nextUpdates.append( nextPass[ 0 ] )
                    nextUpdates.append( nextPass[ 4 ] )

            # Build the menu...
            subMenu.append( Gtk.MenuItem( "Rise" ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Time: " + self.data[ key + " RISE TIME" ] ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Azimuth: " + self.data[ key + " RISE AZIMUTH" ] ) )

            subMenu.append( Gtk.SeparatorMenuItem() )

            subMenu.append( Gtk.MenuItem( "Set" ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Time: " + self.data[ key + " SET TIME" ] ) )
            subMenu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Azimuth: " + self.data[ key + " SET AZIMUTH" ] ) )


    # Returns the string
    #    satelliteName - satelliteNumber
    # useful for keys into a dict/hashtable and for display.
    def getSatelliteNameNumber( self, satelliteName, satelliteNumber ): return satelliteName + " - " + satelliteNumber


    def createEclipseMenu( self, menu, eclipse, label ):
        menu.append( Gtk.MenuItem( "Eclipse" ) )

        localisedAndTrimmedDateTime = self.localiseAndTrim( ephem.Date( eclipse[ 0 ] ) )

        self.data[ label + " ECLIPSE DATE TIME" ] = localisedAndTrimmedDateTime
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Date/Time: " + localisedAndTrimmedDateTime ) )

        self.data[ label + " ECLIPSE LATITUDE LONGITUDE" ] = eclipse[ 2 ] + " " + eclipse[ 3 ]
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Latitude/Longitude: " + eclipse[ 2 ] + " " + eclipse[ 3 ] ) )

        self.data[ label + " ECLIPSE TYPE" ] = eclipse[ 1 ]
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Type: " + eclipse[ 1 ] ) )


    # Compute the right ascension, declination, azimuth, altitude and magnitude for a body.
    def createRADecAzAltMagMenu( self, menu, body ):
        self.data[ body.name.upper() + " RIGHT ASCENSION" ] = str( round( self.convertHoursMinutesSecondsToDecimalDegrees( body.g_ra ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.g_ra ) ) + ")"
        menu.append( Gtk.MenuItem( "Right Ascension: " + self.data[ body.name.upper() + " RIGHT ASCENSION" ] ) )

        direction = "N"
        if body.g_dec < 0.0:
            direction = "S"

        self.data[ body.name.upper() + " DECLINATION" ] = str( abs( round( self.convertDegreesMinutesSecondsToDecimalDegrees( body.g_dec ), 2 ) ) ) + "° " + direction + " (" + re.sub( "\.(\d+)", "", str( body.g_dec ) ) + ")"
        menu.append( Gtk.MenuItem( "Declination: " + self.data[ body.name.upper() + " DECLINATION" ] ) )

        self.data[ body.name.upper() + " AZIMUTH" ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( body.az ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.az ) ) + ")"
        menu.append( Gtk.MenuItem( "Azimuth: " + self.data[ body.name.upper() + " AZIMUTH" ] ) )

        self.data[ body.name.upper() + " ALTITUDE" ] = str( round( self.convertDegreesMinutesSecondsToDecimalDegrees( body.alt ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.alt ) ) + ")"
        menu.append( Gtk.MenuItem( "Altitude: " + self.data[ body.name.upper() + " ALTITUDE" ] ) )

        self.data[ body.name.upper() + " MAGNITUDE" ] = str( body.mag )
        menu.append( Gtk.MenuItem( "Magnitude: " + self.data[ body.name.upper() + " MAGNITUDE" ] ) )


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

        displayTagsStore = Gtk.ListStore( str, str ) # Tag, value.
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
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 0, 1, 1 )

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
        grid.attach( scrolledWindow, 0, 0, 1, 1 )

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
            label.set_markup( "Unable to download the satellite data!\nCheck that <a href=\'" + IndicatorLunar.SATELLITE_TLE_URL + "'>" + IndicatorLunar.SATELLITE_TLE_URL + "</a> is available.\n" )
            label.set_margin_left( 25 )
            label.set_halign( Gtk.Align.START )
            grid.attach( label, 0, 0, 1, 1 )
        else:
            showSatelliteNumberCheckbox = Gtk.CheckButton( "Show Satellite Number" )
            showSatelliteNumberCheckbox.set_active( self.showSatelliteNumber )
            showSatelliteNumberCheckbox.set_tooltip_text( "Include the satellite number in the menu" )
            grid.attach( showSatelliteNumberCheckbox, 0, 0, 1, 1 )
    
            showSatelliteNotificationCheckbox = Gtk.CheckButton( "Rise Time Notification" )
            showSatelliteNotificationCheckbox.set_active( self.showSatelliteNotification )
            showSatelliteNotificationCheckbox.set_tooltip_text( "Screen notification when a satellite rises above the horizon." )
            grid.attach( showSatelliteNotificationCheckbox, 0, 1, 1, 1 )
    
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
    
            tree.set_tooltip_text( "Check a satellite/station/rocket to display in the menu." )
            tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
    
            scrolledWindow = Gtk.ScrolledWindow()
            scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
            scrolledWindow.add( tree )
            grid.attach( scrolledWindow, 0, 2, 1, 1 )

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
                self.showSatelliteNotification = showSatelliteNotificationCheckbox.get_active()
                self.showSatelliteNumber = showSatelliteNumberCheckbox.get_active()
                self.satellites = [ ]
                for satelliteInfo in satelliteStore:
                    if satelliteInfo[ 2 ]: self.satellites.append( [ satelliteInfo[ 0 ], satelliteInfo[ 1 ] ] )

            self.displayPattern = displayPattern.get_text()
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
            displayTagsStore.append( [ planetName + " ILLUMINATION", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " CONSTELLATION", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " TROPICAL SIGN", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " DISTANCE TO EARTH", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " DISTANCE TO SUN", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " BRIGHT LIMB", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " RISING", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ planetName + " SETTING", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
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
            displayTagsStore.append( [ starName + " RIGHT ASCENSION", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + " DECLINATION", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + " AZIMUTH", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + " ALTITUDE", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ starName + " MAGNITUDE", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
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
        tag = self.getSatelliteNameNumber( satelliteStore[ childPath ][ 0 ].upper(), satelliteStore[ childPath ][ 1 ] )

        if satelliteStore[ childPath ][ 1 ]:
            displayTagsStore.append( [ tag + " RISE TIME", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ tag + " RISE AZIMUTH", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ tag + " SET TIME", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
            displayTagsStore.append( [ tag + " SET AZIMUTH", IndicatorLunar.DISPLAY_NEEDS_REFRESH ] )
        else:
            iter = displayTagsStore.get_iter_first()
            while iter is not None:
                if displayTagsStore[ iter ][ 0 ].startswith( tag ):
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
#TODO Remove after testing.
#        
#         self.satelliteTLEData = { }
#         self.satelliteTLEData.append( "ISS (ZARYA)" + " - " + "25544", satellite.Info( 
#            "ISS (ZARYA)", 
#            "1 25544U 98067A   14144.25429147  .00013298  00000-0  23626-3 0  3470" ,
#            "2 25544  51.6479 218.2294 0003503  34.9920  27.7254 15.50515783887617" ) )
#         self.lastUpdateTLE = datetime.datetime.now()
#         if True: return

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
        self.satellites = [ ]
        self.showSatelliteNotification = True
        self.showSatelliteNumber = False
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
                self.planets = settings.get( IndicatorLunar.SETTINGS_PLANETS, self.planets )
                self.satellites = settings.get( IndicatorLunar.SETTINGS_SATELLITES, self.satellites )
                self.showSatelliteNotification = settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITE_NOTIFICATION, self.showSatelliteNotification )
                self.showSatelliteNumber = settings.get( IndicatorLunar.SETTINGS_SHOW_SATELLITE_NUMBER, self.showSatelliteNumber )
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
                IndicatorLunar.SETTINGS_PLANETS: self.planets,
                IndicatorLunar.SETTINGS_SATELLITES: self.satellites,
                IndicatorLunar.SETTINGS_SHOW_SATELLITE_NOTIFICATION: self.showSatelliteNotification,
                IndicatorLunar.SETTINGS_SHOW_SATELLITE_NUMBER: self.showSatelliteNumber,
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


if __name__ == "__main__": 
    
#     gatech = ephem.Observer()
#     gatech.lon, gatech.lat = '-84.39733', '33.775867'
#     iss = ephem.readtle(
#                         "ISS (ZARYA)",
#                         "1 25544U 98067A   03097.78853147  .00021906  00000-0  28403-3 0  8652",
#                         "2 25544  51.6361  13.7980 0004256  35.6671  59.2566 15.58778559250029")
 
#     gatech.date = '2003/3/23'
#     iss.compute(gatech)
#     print( iss.rise_time, iss.transit_time, iss.set_time )
#    2003/3/23 00:00:44 2003/3/23 00:03:22 2003/3/23 00:06:00    
#  
#     gatech.date = '2003/3/23 00:01:30'
#     iss.compute(gatech)
#     print( iss.rise_time, iss.transit_time, iss.set_time )
#     
#     gatechCopy = gatech
#     gatechCopy.date = '2003/3/23 06:01:30'
#     iss.compute(gatechCopy)
#     print( iss.rise_time, iss.transit_time, iss.set_time )
# 
#     iss.compute(gatech)
#     print( iss.rise_time, iss.transit_time, iss.set_time )

    IndicatorLunar().main()