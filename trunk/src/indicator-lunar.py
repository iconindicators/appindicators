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


# Application indicator which displays lunar, solar and planetary information.


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html


#TODO
# Have noticed that the submenus appear as a single space after a certain amount of time.
# By setting the update interval to every second, it takes a few minutes for the submenus to appear as spaces.
# I've wrapped try/except around each function to see if a message is produced - but so far nothing.
# I've also noticed the VirtualBox indicator menu seems to stop responding over time too...maybe it's a related issue?


try: from gi.repository import AppIndicator3 as appindicator
except: pass

from gi.repository import GLib, Gtk

notifyImported = True
try: from gi.repository import Notify
except: notifyImported = False

import copy, datetime, eclipse, gzip, json, locale, logging, math, os, pythonutils, re, shutil, subprocess, sys

try:
    import ephem
    from ephem.cities import _city_data
except:
    pythonutils.showMessage( None, Gtk.MessageType.ERROR, "You must also install python3-ephem!" )
    sys.exit()


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-lunar"
    VERSION = "1.0.35"
    ICON = NAME
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"
    SVG_ICON = "." + NAME + "-illumination-icon"
    SVG_FILE = os.getenv( "HOME" ) + "/" + SVG_ICON + ".svg"
    SVG_FULL_MOON_FILE = os.getenv( "HOME" ) + "/" + "." + NAME + "-fullmoon-icon" + ".svg"

    COMMENTS = "Shows the moon phase and other astronomical information."
    CREDIT_BRIGHT_LIMB = "Bright Limb from 'Astronomical Algorithms' by Jean Meeus."
    CREDIT_ECLIPSE = "Eclipse information by Fred Espenak and Jean Meeus."
    CREDIT_PYEPHEM = "Calculations courtesy of PyEphem/XEphem."
    CREDIT_TROPICAL_SIGN = "Tropical Sign by Ignius Drake."
    CREDITS = [ CREDIT_PYEPHEM, CREDIT_ECLIPSE, CREDIT_TROPICAL_SIGN, CREDIT_BRIGHT_LIMB ]

    INDENT = "    "

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_CITY_ELEVATION = "cityElevation"
    SETTINGS_CITY_LATITUDE = "cityLatitude"
    SETTINGS_CITY_LONGITUDE = "cityLongitude"
    SETTINGS_CITY_NAME = "cityName"
    SETTINGS_DISPLAY_PATTERN = "displayPattern"
    SETTINGS_SHOW_WEREWOLF_WARNING = "showWerewolfWarning"
    SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE = "werewolfWarningStartIlluminationPercentage"
    SETTINGS_WEREWOLF_WARNING_TEXT_BODY = "werewolfWarningTextBody"
    SETTINGS_WEREWOLF_WARNING_TEXT_SUMMARY = "werewolfWarningTextSummary"

    DISPLAY_PATTERN_DEFAULT = "[MOON PHASE] [MOON ILLUMINATION]"

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


    def __init__( self ):
        filehandler = logging.FileHandler( filename = IndicatorLunar.LOG, mode = "a", delay = True )
        logging.basicConfig( format = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                             datefmt = "%H:%M:%S", level = logging.DEBUG,
                             handlers = [ filehandler ] )

        self.dialog = None
        self.data = { }
        self.loadSettings()

        if notifyImported:
            Notify.init( IndicatorLunar.NAME )

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
        ephemNow = ephem.now() # This is UTC and all calculations using this value convert to local time at display time.

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

        # Show the full moon notification if appropriate...
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

        # Moon
        menuItem = Gtk.MenuItem( "Moon" )
        menu.append( menuItem )
        self.createBodySubmenu( menuItem, city, ephem.Moon( city ), nextUpdates, ephemNow )

        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )

        self.data[ "MOON PHASE" ] = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ]
        menuItem.get_submenu().append( Gtk.MenuItem( "Phase: " + self.data[ "MOON PHASE" ] ) )

        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
        menuItem.get_submenu().append( Gtk.MenuItem( "Next Phases" ) )

        # Determine which phases occur by date rather than using the phase calculated since the phase (illumination) rounds numbers
        # and so we enter a phase earlier than what is official.
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

        eclipseInformation = eclipse.getLunarEclipseForUTC( ephemNow.datetime() )
        if eclipseInformation is not None:
            self.createEclipseMenu( menuItem.get_submenu(), eclipseInformation, "MOON" )

        # Sun
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

        self.createRADecSubMenu( subMenu, sun )

        subMenu.append( Gtk.SeparatorMenuItem() )

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

        # Solstice/Equinox
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

        eclipseInformation = eclipse.getSolarEclipseForUTC( ephemNow.datetime() )
        if eclipseInformation is not None:
            self.createEclipseMenu( subMenu, eclipseInformation, "SUN" )

        # Planets
        menu.append( Gtk.MenuItem( "Planets" ) )

        planets = [
            [ "Mercury", ephem.Mercury( city ) ],
            [ "Venus", ephem.Venus( city ) ],
            [ "Mars", ephem.Mars( city ) ],
            [ "Jupiter", ephem.Jupiter( city ) ],
            [ "Saturn", ephem.Saturn( city ) ],
            [ "Uranus", ephem.Uranus( city ) ],
            [ "Neptune", ephem.Neptune( city ) ],
            [ "Pluto", ephem.Pluto( city ) ] ]

        for planet in planets:
            menuItem = Gtk.MenuItem( IndicatorLunar.INDENT + planet[ 0 ] )
            self.createBodySubmenu( menuItem, city, planet[ 1 ], nextUpdates, ephemNow )
            menu.append( menuItem )

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

        GLib.timeout_add_seconds( nextUpdateInSeconds, self.update )


    def createBodySubmenu( self, bodyMenuItem, city, body, nextUpdates, ephemNow ):
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

        self.createRADecSubMenu( subMenu, body )

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


    def createEclipseMenu( self, menu, eclipse, label ):
        menu.append( Gtk.SeparatorMenuItem() )
        menu.append( Gtk.MenuItem( "Eclipse" ) )

        localisedAndTrimmedDateTime = self.localiseAndTrim( ephem.Date( eclipse[ 0 ] ) )

        self.data[ label + " ECLIPSE DATE TIME" ] = localisedAndTrimmedDateTime
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Date/Time: " + localisedAndTrimmedDateTime ) )

        self.data[ label + " ECLIPSE LATITUDE LONGITUDE" ] = eclipse[ 2 ] + " " + eclipse[ 3 ]
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Latitude/Longitude: " + eclipse[ 2 ] + " " + eclipse[ 3 ] ) )

        self.data[ label + " ECLIPSE TYPE" ] = eclipse[ 1 ]
        menu.append( Gtk.MenuItem( IndicatorLunar.INDENT + "Type: " + eclipse[ 1 ] ) )


    def createRADecSubMenu( self, subMenu, body ):
        self.data[ body.name.upper() + " RIGHT ASCENSION" ] = str( round( self.convertHMSToDecimalDegrees( body.g_ra ), 2 ) ) + "° (" + re.sub( "\.(\d+)", "", str( body.g_ra ) ) + ")"
        subMenu.append( Gtk.MenuItem( "Right Ascension: " + self.data[ body.name.upper() + " RIGHT ASCENSION" ] ) )

        direction = "N"
        if body.g_dec < 0.0:
            direction = "S"

        self.data[ body.name.upper() + " DECLINATION" ] = str( abs( round( self.convertDMSToDecimalDegrees( body.g_dec ), 2 ) ) ) + "° " + direction + " (" + re.sub( "\.(\d+)", "", str( body.g_dec ) ) + ")"
        subMenu.append( Gtk.MenuItem( "Declination: " + self.data[ body.name.upper() + " DECLINATION" ] ) )


    # Takes a float and converts to local time, trims off fractional seconds and returns a string.
    def localiseAndTrim( self, value ):
        localtimeString = str( ephem.localtime( value ) )
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
        signList = [ 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces' ]

        ( year, month, day ) = ephemNow.triple()
        epochAdjusted = float( year ) + float( month ) / 12.0 + float( day ) / 365.242
        ephemNowDate = str( ephemNow ).split( ' ' )

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
        sunRA = math.radians( self.convertHMSToDecimalDegrees( sun.g_ra ) )
        sunDec = math.radians( self.convertDMSToDecimalDegrees( sun.g_dec ) )
        bodyRA = math.radians( self.convertHMSToDecimalDegrees( body.g_ra ) )
        bodyDec = math.radians( self.convertDMSToDecimalDegrees( body.g_dec ) )

        y = math.cos( sunDec ) * math.sin( sunRA - bodyRA )
        x = math.cos( bodyDec ) * math.sin( sunDec ) - math.sin( bodyDec ) * math.cos( sunDec ) * math.cos( sunRA - bodyRA )
        brightLimbAngle = math.degrees( math.atan2( y, x ) )

        hourAngle = math.radians( self.convertHMSToDecimalDegrees( city.sidereal_time() ) ) - bodyRA
        y = math.sin( hourAngle )
        x = math.tan( math.radians( self.convertDMSToDecimalDegrees( city.lat ) ) ) * math.cos( bodyDec ) - math.sin( bodyDec ) * math.cos( hourAngle )
        parallacticAngle = math.degrees( math.atan2( y, x ) )

        zenithAngle = brightLimbAngle - parallacticAngle
        if zenithAngle < 0.0: zenithAngle += 360.0

        return zenithAngle


    def convertHMSToDecimalDegrees( self, hms ):
        t = tuple( str( hms ).split( ":" ) )
        x = ( float( t[ 2 ] ) / 60.0 + float( t[ 1 ] ) ) / 60.0 + abs( float( t[ 0 ] ) ) * 15.0
        y = float( t[ 0 ] )
        return math.copysign( x, y )


    def convertDMSToDecimalDegrees( self, dms ):
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


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


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

        store = Gtk.ListStore( str, str ) # Tag, value.
        for key in sorted( self.data.keys() ):
            store.append( [ key, self.data[ key ] ] )

        tree = Gtk.TreeView( store )
        tree.set_hexpand( True )
        tree.set_vexpand( True )
        tree.append_column( Gtk.TreeViewColumn( "Tag", Gtk.CellRendererText(), text = 0 ) )
        tree.append_column( Gtk.TreeViewColumn( "Value", Gtk.CellRendererText(), text = 1 ) )
        tree.set_tooltip_text( "Double click to add a tag to the display pattern." )
        tree.get_selection().set_mode( Gtk.SelectionMode.SINGLE )
        tree.connect( "row-activated", self.onTagDoubleClick, displayPattern )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( tree )
        grid.attach( scrolledWindow, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "Display" ) )

        # Notification settings.
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

        notebook.append_page( grid, Gtk.Label( "Notification" ) )

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
        autostartCheckbox.set_active( os.path.exists( IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 0, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "General" ) )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorLunar.ICON )

        while True:
            self.dialog.show_all()
            response = self.dialog.run()

            if response == Gtk.ResponseType.CANCEL:
                break

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


    def onTagDoubleClick( self, tree, rowNumber, treeViewColumn, displayPattern ):
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


    def loadSettings( self ):
        self.getDefaultCity()
        self.displayPattern = IndicatorLunar.DISPLAY_PATTERN_DEFAULT
        self.showWerewolfWarning = True
        self.werewolfWarningStartIlluminationPercentage = 100
        self.werewolfWarningTextBody = IndicatorLunar.WEREWOLF_WARNING_TEXT_BODY
        self.werewolfWarningTextSummary = IndicatorLunar.WEREWOLF_WARNING_TEXT_SUMMARY

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
                self.showWerewolfWarning = settings.get( IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING, self.showWerewolfWarning )
                self.werewolfWarningStartIlluminationPercentage = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE, self.werewolfWarningStartIlluminationPercentage )
                self.werewolfWarningTextBody = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_TEXT_BODY, self.werewolfWarningTextBody )
                self.werewolfWarningTextSummary = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_TEXT_SUMMARY, self.werewolfWarningTextSummary )

                # Insert/overwrite the cityName and information into the cities...
                _city_data[ self.cityName ] = ( str( cityLatitude ), str( cityLongitude ), float( cityElevation ) )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorLunar.SETTINGS_FILE )


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
            logging.error( "Error getting default cityName." )
            self.cityName = sorted( _city_data.keys(), key = locale.strxfrm )[ 0 ]


    def saveSettings( self ):
        try:
            settings = {
                IndicatorLunar.SETTINGS_CITY_ELEVATION: _city_data.get( self.cityName )[ 2 ],
                IndicatorLunar.SETTINGS_CITY_LATITUDE: _city_data.get( self.cityName )[ 0 ],
                IndicatorLunar.SETTINGS_CITY_LONGITUDE: _city_data.get( self.cityName )[ 1 ],
                IndicatorLunar.SETTINGS_CITY_NAME: self.cityName,
                IndicatorLunar.SETTINGS_DISPLAY_PATTERN: self.displayPattern,
                IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING: self.showWerewolfWarning,
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