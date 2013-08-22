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


# Application indicator which displays lunar information.


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


try:
    from gi.repository import AppIndicator3 as appindicator
except:
    pass

from gi.repository import GLib, Gtk

notifyImported = True
try:
    from gi.repository import Notify
except:
    notifyImported = False

import datetime, json, locale, logging, os, shutil, subprocess, sys

try:
    import ephem
    from ephem.cities import _city_data
except:
    dialog = Gtk.MessageDialog( None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "You must also install python3-ephem!" )
    dialog.set_title( "indicator-lunar" )
    dialog.run()
    sys.exit()


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-lunar"
    VERSION = "1.0.25"
    ICON = NAME
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"
    SVG_ICON = "." + NAME + "-illumination-icon"
    SVG_FILE = os.getenv( "HOME" ) + "/" + SVG_ICON + ".svg"

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_CITY_ELEVATION = "cityElevation"
    SETTINGS_CITY_LATITUDE = "cityLatitude"
    SETTINGS_CITY_LONGITUDE = "cityLongitude"
    SETTINGS_CITY_NAME = "cityName"
    SETTINGS_SHOW_WEREWOLF_WARNING = "showWerewolfWarning"
    SETTINGS_SHOW_ILLUMINATION = "showIllumination"
    SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW = "showNorthernHemisphereView"
    SETTINGS_SHOW_PHASE = "showPhase"
    SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE = "werewolfWarningStartIlluminationPercentage"
    SETTINGS_WEREWOLF_WARNING_TEXT_BODY = "werewolfWarningTextBody"
    SETTINGS_WEREWOLF_WARNING_TEXT_SUMMARY = "werewolfWarningTextSummary"

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

    WEREWOLF_WARNING_TEXT_BODY = "...werewolves about!!!"
    WEREWOLF_WARNING_TEXT_SUMMARY = "WARNING..."


    def __init__( self ):
        filehandler = logging.FileHandler( filename = IndicatorLunar.LOG, mode = "a", delay = True )
        logging.basicConfig( format = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s", 
                             datefmt = "%H:%M:%S", level = logging.DEBUG,
                             handlers = [ filehandler ] )

        self.dialog = None
        self.loadSettings()

        if notifyImported:
            Notify.init( IndicatorLunar.NAME )

        # Attempt to create an AppIndicator3...if it fails, default to a GTK indicator.
        # I've found that on Lubuntu 12.04 the AppIndicator3 gets created but does not work properly...
        # ...the icon cannot be updated dynamically and tooltip/label does not display.
        # The workaround for this is to force the GTK indicator to be created (as per the except below) for Lubuntu 12.04.
        # For now ignore Lubuntu 12.04 (and presumably Xubuntu 12.04)...
        # ...if a user screams, put in an option to allow the user to specify which indicator type to use.
        try:
            self.appindicatorImported = True
            self.indicator = appindicator.Indicator.new( IndicatorLunar.NAME, "", appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_icon_theme_path( os.getenv( "HOME" ) )
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling...
        except:
            self.appindicatorImported = False
            self.menu = Gtk.Menu() # Set an empty menu to get things rolling...
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.update()
        Gtk.main()


    def update( self ):
        ephemNow = ephem.now()

        lunarPhase = self.calculateLunarPhase( ephemNow )
        moon = ephem.Moon( ephemNow )
        percentageIllumination = int( round( moon.phase ) )

        self.buildMenu( lunarPhase, ephemNow )

        # Determine the content of the indicator (label, tooltip, etc).
        if self.showIllumination and self.showPhase:
            labelTooltip = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] + " (" + str( percentageIllumination ) + "%)"
        elif self.showIllumination:
            labelTooltip = str( percentageIllumination ) + "%"
        elif self.showPhase:
            labelTooltip = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ]
        else:
            labelTooltip = ""

        # Set the icon/label handling the Unity and non-Unity cases...
        self.createIconForLunarPhase( lunarPhase, percentageIllumination )
        if self.appindicatorImported:
            self.indicator.set_icon( IndicatorLunar.SVG_ICON )
            self.indicator.set_label( labelTooltip, "" ) # Second parameter is a guide for how wide the text could get (see label-guide in http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html).
        else:
            self.statusicon.set_from_file( IndicatorLunar.SVG_FILE )
            self.statusicon.set_tooltip_text( labelTooltip )

        phaseIsBetweenNewAndFullInclusive = ( lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON )

        # Show the full moon indicator when the user setting is enabled and the phase and illumination percentage are appropriate.
        if notifyImported and \
            self.showWerewolfWarning and \
            percentageIllumination >= self.werewolfWarningStartIlluminationPercentage and \
            phaseIsBetweenNewAndFullInclusive:

            # The notification summary text must not be empty (at least on Unity).
            summary = self.werewolfWarningTextSummary
            if self.werewolfWarningTextSummary == "":
                summary = " "

            Notify.Notification.new( summary, self.werewolfWarningTextBody, IndicatorLunar.SVG_FILE ).show()


    def buildMenu( self, lunarPhase, ephemNow ):
        nextUpdates = [ ] # Stores the date/time for each upcoming rise/set/phase...used to find the date/time closest to now and that will be the next time for an update.

        if self.appindicatorImported:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if we don't do this we get GTK complaints).
        menu = Gtk.Menu()
        city = ephem.city( self.cityName )
        indent = "    "

        # Moon
        menuItem = Gtk.MenuItem( "Moon" )
        menu.append( menuItem )
        self.createPlanetSubmenu( menuItem, city, ephem.Moon( ephemNow ), nextUpdates )
        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
        menuItem.get_submenu().append( Gtk.MenuItem( "Phase: " + IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] ) )
        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )
        menuItem.get_submenu().append( Gtk.MenuItem( "Next Phases" ) )

        # Need to work out which phases occur by date rather than using the phase we calculate since the phase (illumination) rounds numbers
        # and so we enter a phase earlier than what is official.
        nextPhases = [ ]
        nextPhases.append( [ self.localiseAndTrim( ephem.next_first_quarter_moon( ephemNow ) ), "First Quarter: " ] )
        nextPhases.append( [ self.localiseAndTrim( ephem.next_full_moon( ephemNow ) ), "Full: " ] )
        nextPhases.append( [ self.localiseAndTrim( ephem.next_last_quarter_moon( ephemNow ) ), "Third Quarter: " ] )
        nextPhases.append( [ self.localiseAndTrim( ephem.next_new_moon( ephemNow ) ), "New: " ] )
        nextPhases = sorted( nextPhases, key = lambda tuple: tuple[ 0 ] )
        for phaseInformation in nextPhases:
            menuItem.get_submenu().append( Gtk.MenuItem( indent + phaseInformation[ 1 ] + phaseInformation[ 0 ] ) )

        nextUpdates.append( ephem.next_first_quarter_moon( ephemNow ) )
        nextUpdates.append( ephem.next_full_moon( ephemNow ) )
        nextUpdates.append( ephem.next_last_quarter_moon( ephemNow ) )
        nextUpdates.append( ephem.next_new_moon( ephemNow ) )

        # Sun
        menuItem = Gtk.MenuItem( "Sun" )
        menu.append( menuItem )

        subMenu = Gtk.Menu()
        menuItem.set_submenu( subMenu )

        sun = ephem.Sun( ephemNow )

        subMenu.append( Gtk.MenuItem( "Constellation: " + ephem.constellation( sun )[ 1 ] ) )
        subMenu.append( Gtk.MenuItem( "Distance to Earth: " + str( round( sun.earth_distance, 4 ) ) + " AU" ) )

        subMenu.append( Gtk.SeparatorMenuItem() )
        rising = city.next_rising( sun )
        setting = city.next_setting( sun )
        if rising > setting:
            subMenu.append( Gtk.MenuItem( "Set: " + self.localiseAndTrim( setting ) ) )
            subMenu.append( Gtk.MenuItem( "Rise: " + self.localiseAndTrim( rising ) ) )
        else:
            subMenu.append( Gtk.MenuItem( "Rise: " + self.localiseAndTrim( rising ) ) )
            subMenu.append( Gtk.MenuItem( "Set: " + self.localiseAndTrim( setting ) ) )

        nextUpdates.append( rising )
        nextUpdates.append( setting )

        subMenu.append( Gtk.SeparatorMenuItem() )

        # Solstice/Equinox
        equinox = ephem.next_equinox( ephemNow )
        solstice = ephem.next_solstice( ephemNow )
        if equinox < solstice:
            subMenu.append( Gtk.MenuItem( "Equinox: " + self.localiseAndTrim( equinox ) ) )
            subMenu.append( Gtk.MenuItem( "Solstice: " + self.localiseAndTrim( solstice ) ) )
        else:
            subMenu.append( Gtk.MenuItem( "Solstice: " + self.localiseAndTrim( solstice ) ) ) 
            subMenu.append( Gtk.MenuItem( "Equinox: " + self.localiseAndTrim( equinox ) ) )

        nextUpdates.append( equinox )
        nextUpdates.append( solstice )

        # Planets
        menu.append( Gtk.MenuItem( "Planets" ) )

        planets = [
            [ "Mercury", ephem.Mercury( ephemNow ) ], 
            [ "Venus", ephem.Venus( ephemNow ) ], 
            [ "Mars", ephem.Mars( ephemNow ) ], 
            [ "Jupiter", ephem.Jupiter( ephemNow ) ], 
            [ "Saturn", ephem.Saturn( ephemNow ) ], 
            [ "Uranus", ephem.Uranus( ephemNow ) ], 
            [ "Neptune", ephem.Neptune( ephemNow ) ], 
            [ "Pluto", ephem.Pluto( ephemNow ) ] ]

        for planet in planets:
            menuItem = Gtk.MenuItem( indent + planet[ 0 ] )
            self.createPlanetSubmenu( menuItem, city, planet[ 1 ], nextUpdates )
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
        # Add a 10 second buffer because the update sometimes happened fractionally earlier (due to truncating the fractional time component).
        nextUpdates.sort()
        nextUpdateInSeconds = int ( ( ephem.localtime( nextUpdates[ 0 ] ) - ephem.localtime( ephemNow ) ).total_seconds() ) + 10
        if nextUpdateInSeconds < 60: # Ensure the update period is positive and not too frequent...
            nextUpdateInSeconds = 60

        if nextUpdateInSeconds > ( 60 * 60 ): # Ensure the update period is at least hourly...
            nextUpdateInSeconds = ( 60 * 60 )

        GLib.timeout_add_seconds( nextUpdateInSeconds, self.update )


    def createPlanetSubmenu( self, planetMenuItem, city, planet, nextUpdates ):
        subMenu = Gtk.Menu()
        subMenu.append( Gtk.MenuItem( "Illumination: " + str( int( round( planet.phase ) ) ) + "%" ) )
        subMenu.append( Gtk.MenuItem( "Constellation: " + ephem.constellation( planet )[ 1 ] ) )
        subMenu.append( Gtk.MenuItem( "Distance to Earth: " + str( round( planet.earth_distance, 4 ) ) + " AU" ) )
        subMenu.append( Gtk.MenuItem( "Distance to Sun: " + str( round( planet.sun_distance, 4 ) ) + " AU" ) )
        subMenu.append( Gtk.SeparatorMenuItem() )

        # Must compute the previous information (illumination, constellation, phase and so on BEFORE rising/setting).
        # For some reason the values, most notably phase, are different (and wrong) if calculated AFTER rising/setting are calculated.
        rising = city.next_rising( planet )
        setting = city.next_setting( planet )
        if rising > setting:
            subMenu.append( Gtk.MenuItem( "Set: " + self.localiseAndTrim( setting ) ) )
            subMenu.append( Gtk.MenuItem( "Rise: " + self.localiseAndTrim( rising ) ) )
        else:
            subMenu.append( Gtk.MenuItem( "Rise: " + self.localiseAndTrim( rising ) ) )
            subMenu.append( Gtk.MenuItem( "Set: " + self.localiseAndTrim( setting ) ) )

        planetMenuItem.set_submenu( subMenu )

        nextUpdates.append( rising )
        nextUpdates.append( setting )


    # Takes a float and converts to local time, trims off fractional seconds and returns a string.
    def localiseAndTrim( self, value ):
        localtimeString = str( ephem.localtime( value ) )
        return localtimeString[ 0 : localtimeString.rfind( ":" ) + 3 ]


    def calculateLunarPhase( self, ephemNow ):
        nextFullMoonDate = ephem.next_full_moon( ephemNow )
        nextNewMoonDate = ephem.next_new_moon( ephemNow )
        moon = ephem.Moon( ephemNow )
        currentMoonPhase = int( round( ( moon.phase ) ) )
        phase = None
        if nextFullMoonDate < nextNewMoonDate: # No need for these dates to be localised...just need to know which one is before the other.
            # We are somewhere between a new moon and a full moon...
            if( currentMoonPhase > 99 ):
                phase = IndicatorLunar.LUNAR_PHASE_FULL_MOON
            elif currentMoonPhase <= 99 and currentMoonPhase > 50:
                phase = IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS
            elif currentMoonPhase == 50:
                phase = IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER
            elif currentMoonPhase < 50 and currentMoonPhase >= 1:
                phase = IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT
            else: # currentMoonPhase < 1
                phase = IndicatorLunar.LUNAR_PHASE_NEW_MOON
        else:
            # We are somewhere between a full moon and the next new moon...
            if( currentMoonPhase > 99 ):
                phase = IndicatorLunar.LUNAR_PHASE_FULL_MOON
            elif currentMoonPhase <= 99 and currentMoonPhase > 50:
                phase = IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS
            elif currentMoonPhase == 50:
                phase = IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER
            elif currentMoonPhase < 50 and currentMoonPhase >= 1:
                phase = IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT
            else: # currentMoonPhase < 1
                phase = IndicatorLunar.LUNAR_PHASE_NEW_MOON

        return phase


    def createIconForLunarPhase( self, lunarPhase, illumination ):
        if lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON:
            svg = self.getNewMoonSVG()
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON:
            svg = self.getFullMoonSVG()
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER or lunarPhase == IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER:
            svg = self.getQuarterMoonSVG( lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER, self.showNorthernHemisphereView )
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT or \
            lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT or \
            lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS or \
            lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS:
            svg = self.getCrescentGibbousMoonSVG( 
                illumination,
                lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT or lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS, 
                self.showNorthernHemisphereView,
                lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT or lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT )

        try:
            with open( IndicatorLunar.SVG_FILE, "w" ) as f:
                f.write( svg )
                f.close()

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing SVG: " + IndicatorLunar.SVG_FILE )


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def onAbout( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.dialog = Gtk.AboutDialog()
        self.dialog.set_program_name( IndicatorLunar.NAME )
        self.dialog.set_comments( IndicatorLunar.AUTHOR + "\n\nCalculations courtesy of Ephem.\n" )
        self.dialog.set_website( IndicatorLunar.WEBSITE )
        self.dialog.set_website_label( IndicatorLunar.WEBSITE )
        self.dialog.set_version( IndicatorLunar.VERSION )
        self.dialog.set_license( IndicatorLunar.LICENSE )
        self.dialog.set_icon_name( Gtk.STOCK_ABOUT )
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

        showPhaseCheckbox = Gtk.CheckButton( "Show phase" )
        showPhaseCheckbox.set_active( self.showPhase )
        grid.attach( showPhaseCheckbox, 0, 0, 2, 1 )

        showIlluminationCheckbox = Gtk.CheckButton( "Show illumination" )
        showIlluminationCheckbox.set_active( self.showIllumination )
        grid.attach( showIlluminationCheckbox, 0, 1, 2, 1 )

        showNorthernHemisphereViewCheckbox = Gtk.CheckButton( "Northern hemisphere view" )
        showNorthernHemisphereViewCheckbox.set_active( self.showNorthernHemisphereView )
        grid.attach( showNorthernHemisphereViewCheckbox, 0, 2, 2, 1 )

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
        spinner.set_adjustment( Gtk.Adjustment( self.werewolfWarningStartIlluminationPercentage, 0, 100, 1, 5, 0 ) )
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
        body.set_tooltip_text( "The body text for the werewolf notification" )
        body.set_sensitive( showWerewolfWarningCheckbox.get_active() )
        grid.attach( body, 1, 3, 1, 1 )

        showWerewolfWarningCheckbox.connect( "toggled", self.onShowWerewolfWarningCheckbox, label, body )

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
        grid.add( label )

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
        grid.attach( latitude, 1, 1, 1, 1 )

        label = Gtk.Label( "Longitude (DD)" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 2, 1, 1 )

        longitude = Gtk.Entry()
        grid.attach( longitude, 1, 2, 1, 1 )

        label = Gtk.Label( "Elevation (m)" )
        label.set_halign( Gtk.Align.START )
        grid.attach( label, 0, 3, 1, 1 )

        elevation = Gtk.Entry()
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
                self.showMessage( Gtk.MessageType.ERROR, "City cannot be empty." )
                city.grab_focus()
                continue

            latitudeValue = latitude.get_text().strip()
            if latitudeValue == "" or not self.isNumber( latitudeValue ) or float( latitudeValue ) > 90 or float( latitudeValue ) < -90:
                self.showMessage( Gtk.MessageType.ERROR, "Latitude must be a number between 90 and -90 inclusive." )
                latitude.grab_focus()
                continue

            longitudeValue = longitude.get_text().strip()
            if longitudeValue == "" or not self.isNumber( longitudeValue ) or float( longitudeValue ) > 180 or float( longitudeValue ) < -180:
                self.showMessage( Gtk.MessageType.ERROR, "Longitude must be a number between 180 and -180 inclusive." )
                longitude.grab_focus()
                continue

            elevationValue = elevation.get_text().strip()
            if elevationValue == "" or not self.isNumber( elevationValue ) or float( elevationValue ) > 10000 or float( elevationValue ) < 0:
                self.showMessage( Gtk.MessageType.ERROR, "Elevation must be a number number between 0 and 10000 inclusive." )
                elevation.grab_focus()
                continue

            self.showPhase = showPhaseCheckbox.get_active()
            self.showIllumination = showIlluminationCheckbox.get_active()
            self.showNorthernHemisphereView = showNorthernHemisphereViewCheckbox.get_active()
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


    def onCityChanged( self, combobox, latitude, longitude, elevation ):
        city = combobox.get_active_text()
        global _city_data
        if city != "" and city in _city_data:
            latitude.set_text( _city_data.get( city )[ 0 ] )
            longitude.set_text( _city_data.get( city )[ 1 ] )
            elevation.set_text( str( _city_data.get( city )[ 2 ] ) )


    def isNumber( self, string ):
        try:
            float( string )
            return True
        except ValueError:
            return False


    def showMessage( self, messageType, message ):
        dialog = Gtk.MessageDialog( None, 0, messageType, Gtk.ButtonsType.OK, message )
        dialog.run()
        dialog.destroy()


    def onShowWerewolfWarningCheckbox( self, source, spinner, label ):
        label.set_sensitive( source.get_active() )
        spinner.set_sensitive( source.get_active() )


    def loadSettings( self ):
        self.getDefaultCity()
        self.showWerewolfWarning = True
        self.showIllumination = True
        self.showNorthernHemisphereView = True
        self.showPhase = True
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
                self.showWerewolfWarning = settings.get( IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING, self.showWerewolfWarning )
                self.showIllumination = settings.get( IndicatorLunar.SETTINGS_SHOW_ILLUMINATION, self.showIllumination )
                self.showNorthernHemisphereView = settings.get( IndicatorLunar.SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW, self.showNorthernHemisphereView )
                self.showPhase = settings.get( IndicatorLunar.SETTINGS_SHOW_PHASE, self.showPhase )
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
                IndicatorLunar.SETTINGS_SHOW_WEREWOLF_WARNING: self.showWerewolfWarning,
                IndicatorLunar.SETTINGS_SHOW_ILLUMINATION: self.showIllumination,
                IndicatorLunar.SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW: self.showNorthernHemisphereView,
                IndicatorLunar.SETTINGS_SHOW_PHASE: self.showPhase,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE: self.werewolfWarningStartIlluminationPercentage,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_TEXT_BODY: self.werewolfWarningTextBody,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_TEXT_SUMMARY: self.werewolfWarningTextSummary
            }

            with open( IndicatorLunar.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorLunar.SETTINGS_FILE )


    def getCrescentGibbousMoonSVG( self, illumination, waning, northernHemisphere, crescent ):
        radius = float( self.getMoonRadius() )
        diameter = 2 * radius

        # http://en.wikipedia.org/wiki/Crescent
        if crescent:
            ellipseRadiusX = radius * ( 1 - illumination / 50 )
        else:
            ellipseRadiusX = radius * ( illumination / 50 - 1 )

        # http://www.w3.org/TR/SVG/paths.html#PathDataEllipticalArcCommands
        if( northernHemisphere == True and waning == True ) or ( northernHemisphere == False and waning == False ):
            sweepFlagCircle = str( 0 )
            sweepFlagEllipse = str( 1 ) if crescent else str( 0 )
        else:
            sweepFlagCircle = str( 1 )
            sweepFlagEllipse = str( 0 ) if crescent else str( 1 )

        if( northernHemisphere == True and waning == True ) or ( northernHemisphere == False and waning == False ):
            x = 50
        else:
            # Northern and waxing OR southern and waning...
            if crescent:
                x = ( 50 - radius )
            else:
                x = ( 50 - radius ) + abs( ellipseRadiusX ) # Gibbous

        circle = 'a' + str( radius ) + ',' + str( radius ) + ' 0 0,' + sweepFlagCircle + ' 0,' + str( diameter )
        ellipse = 'a' + str( ellipseRadiusX ) + ',' + str( radius ) + ' 0 0,' + sweepFlagEllipse + ' 0,-' + str( diameter )
        svg = '<path d="M ' + str( x ) + ' 50 v-' + str( radius ) + ' ' + circle + ' ' + ellipse + ' " fill="' + self.getColourForIconTheme() + '" />'

        if crescent:
            width = radius + 2 * ( 50 - radius )
        else:
            width = radius + abs( ellipseRadiusX ) + 2 * ( 50 - radius ) # Gibbous

        return self.getSVGHeader( width ) + svg + self.getSVGFooter()


    def getQuarterMoonSVG( self, first, northernHemisphere ):
        radius = float( self.getMoonRadius() )
        diameter = 2 * radius

        # http://www.w3.org/TR/SVG/paths.html#PathDataEllipticalArcCommands
        if( first == True and northernHemisphere == True ) or ( first == False and northernHemisphere == False ):
            x = 50 - radius
            sweepFlag = str( 1 )
        else:
            x = 50
            sweepFlag = str( 0 )

        svg = '<path d="M ' + str( x ) + ' 50 v-' + str( radius ) + ' a' + str( radius ) + ',' + str( radius ) + ' 0 0,' + sweepFlag + ' 0,' + str( diameter ) + ' z" fill="' + self.getColourForIconTheme() + '" />'
        return self.getSVGHeader( ( 50 - radius ) + 50 ) + svg + self.getSVGFooter()


    def getFullMoonSVG( self ):
        svg = '<circle cx="50" cy="50" r="' + self.getMoonRadius() + '" fill="' + self.getColourForIconTheme() + '" />'
        return self.getSVGHeader( 100 ) + svg + self.getSVGFooter()


    def getNewMoonSVG( self ):
        svg = '<circle cx="50" cy="50" r="' + self.getMoonRadius() + '" fill="none" stroke="' + self.getColourForIconTheme() + '" stroke-width="2" />'
        return self.getSVGHeader( 100 ) + svg + self.getSVGFooter()


    def getSVGHeader( self, width ):
        return '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 ' + str( width ) + ' 100">'


    def getSVGFooter( self ): return '</svg>'


    def getMoonRadius( self ): return str( ( 50 - 25 ) / 2 + 25 ) # A radius of 50 is too big and 25 is too small, so choose half way!


    def getColourForIconTheme( self ):
        iconTheme = self.getIconTheme()
        if iconTheme is None:
            return "#fff200" # Use hicolor as a default.

        if iconTheme == "elementary":
            return "#f4f4f4"

        if iconTheme == "lubuntu":
            return "#5a5a5a"

        if iconTheme == "ubuntu-mono-dark":
            return "#dfdbd2"

        if iconTheme == "ubuntu-mono-light":
            return "#3c3c3c"

        return "#fff200" # Use hicolor as a default


    def getIconTheme( self ): return Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )


if __name__ == "__main__": IndicatorLunar().main()