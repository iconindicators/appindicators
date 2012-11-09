#!/usr/bin/env python


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


# TODO: There is no Python3 version of Ephem (http://pypi.python.org/pypi/ephem).
# Will attempt to create a PPA package!


from ephem.cities import _city_data

appindicatorImported = True
try:
    from gi.repository import AppIndicator3 as appindicator
except:
    appindicatorImported = False

from gi.repository import GObject as gobject
from gi.repository import Gtk

notifyImported = True
try:
    from gi.repository import Notify
except:
    notifyImported = False

import datetime
import ephem
import json
import locale
import logging
import os
import shutil
import string
import subprocess
import sys


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-lunar"
    VERSION = "1.0.10"
    ICON = NAME
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_CITY_ELEVATION = "cityElevation"
    SETTINGS_CITY_LATITUDE = "cityLatitude"
    SETTINGS_CITY_LONGITUDE = "cityLongitude"
    SETTINGS_CITY_NAME = "cityName"
    SETTINGS_SHOW_HOURLY_WEREWOLF_WARNING = "showHourlyWerewolfWarning"
    SETTINGS_SHOW_ILLUMINATION = "showIllumination"
    SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW = "showNorthernHemisphereView"
    SETTINGS_SHOW_PHASE = "showPhase"
    SETTINGS_SHOW_SUBMENU = "showSubmenu"
    SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE = "werewolfWarningStartIlluminationPercentage"

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

    LUNAR_PHASE_ICONS = {
        LUNAR_PHASE_FULL_MOON : ICON + "-full-moon",
        LUNAR_PHASE_WANING_GIBBOUS : ICON + "-waning-gibbous",
        LUNAR_PHASE_THIRD_QUARTER : ICON + "-third-quarter",
        LUNAR_PHASE_WANING_CRESCENT : ICON + "-waning-crescent",
        LUNAR_PHASE_NEW_MOON : ICON + "-new-moon",
        LUNAR_PHASE_WAXING_CRESCENT : ICON + "-waxing-crescent",
        LUNAR_PHASE_FIRST_QUARTER : ICON + "-first-quarter",
        LUNAR_PHASE_WAXING_GIBBOUS : ICON + "-waxing-gibbous"
    }


    def __init__( self ):
        logging.basicConfig( file = sys.stderr, level = logging.INFO )
        self.loadSettings()
        self.dialog = None

        if notifyImported == True:
            Notify.init( IndicatorLunar.NAME )

        # One of the install dependencies for Debian/Ubuntu is that appindicator exists.
        # However the appindicator only works under Ubuntu Unity - we need to default to GTK icon if not running Unity (say Lubuntu).
        global appindicatorImported
        unityIsInstalled = os.getenv( "XDG_CURRENT_DESKTOP" )
        if unityIsInstalled is None:
            appindicatorImported = False
        elif str( unityIsInstalled ).lower() != "Unity".lower():
            appindicatorImported = False

        # Create the status icon...either Unity or GTK.
        if appindicatorImported == True:
            self.indicator = appindicator.Indicator.new( IndicatorLunar.NAME, "", appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling...
#            self.indicator.set_menu( self.menu )
        else:
            self.menu = Gtk.Menu() # Set an empty menu to get things rolling...
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.update()
        gobject.timeout_add( 60 * 60 * 1000, self.update )
        Gtk.main()


    def update( self ):
        currentDateTime = datetime.datetime.now()
        lunarPhase = self.calculateLunarPhase( currentDateTime )
        percentageIllumination = int( round( ephem.Moon( currentDateTime ).phase ) )

        if self.showIllumination == True and self.showPhase == True:
            labelTooltip = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] + " (" + str( percentageIllumination ) + "%)"
        elif self.showIllumination == True:
            labelTooltip = str( percentageIllumination ) + "%"
        elif self.showPhase == True:
            labelTooltip = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ]
        else:
            labelTooltip = ""

        if appindicatorImported == True:
            self.indicator.set_icon( self.getIconNameForLunarPhase( lunarPhase ) )
            self.indicator.set_label( labelTooltip, "" ) # Second parameter is a guide for how wide the text could get (see label-guide in http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html).
        else:
            self.statusicon.set_from_icon_name( self.getIconNameForLunarPhase( lunarPhase ) )
            self.statusicon.set_tooltip_text( labelTooltip )

        self.buildMenu( currentDateTime, lunarPhase, percentageIllumination )

        phaseIsBetweenNewAndFullInclusive = ( lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON )

        if notifyImported == True and self.showHourlyWerewolfWarning == True and percentageIllumination >= self.werewolfWarningStartIlluminationPercentage and phaseIsBetweenNewAndFullInclusive:
            Notify.Notification.new( "WARNING: Werewolves about!!!", "", IndicatorLunar.LUNAR_PHASE_ICONS[ IndicatorLunar.LUNAR_PHASE_FULL_MOON ] ).show()

        return True # Needed so the timer continues!


    def buildMenu( self, currentDateTime, lunarPhase, percentageIllumination ):
        if appindicatorImported == True:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if we don't do this we get GTK complaints).

        # Create the new menu and populate...
        menu = Gtk.Menu()

        if self.showSubmenu == True:
            indent = ""
        else:
            indent = "    "

        phaseMenuItem = Gtk.MenuItem( "Phase: " + IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] )
        menu.append( phaseMenuItem )

        illuminationMenuItem = Gtk.MenuItem( "Illumination: " + str( percentageIllumination ) + "%" )
        menu.append( illuminationMenuItem )

        constellationMenuItem = Gtk.MenuItem( "Constellation: " + ephem.constellation( ephem.Moon( currentDateTime ) )[ 1 ] )
        menu.append( constellationMenuItem )

        menuItem = Gtk.MenuItem( "Distances:" )
        menu.append( menuItem )

        distanceToEarthInKMMenuItem = Gtk.MenuItem( indent + "Moon to Earth: " + str( int( round( ephem.Moon( currentDateTime ).earth_distance * ephem.meters_per_au / 1000 ) ) ) + " km" )
        distanceToEarthInAUMenuItem = Gtk.MenuItem( indent + "Moon to Earth: " + str( round( ephem.Moon( currentDateTime ).earth_distance, 4 ) ) + " AU" )
        distanceToSunMenuItem = Gtk.MenuItem( indent + "Moon to Sun: " + str( round( ephem.Moon( currentDateTime ).sun_distance, 3 ) )  + " AU" )
        if self.showSubmenu == True:
            subMenu = Gtk.Menu()
            subMenu.append( distanceToEarthInKMMenuItem )
            subMenu.append( distanceToEarthInAUMenuItem )
            subMenu.append( distanceToSunMenuItem )
            menuItem.set_submenu( subMenu )
        else:
            menu.append( distanceToEarthInKMMenuItem )
            menu.append( distanceToEarthInAUMenuItem )
            menu.append( distanceToSunMenuItem )

        menuItem = Gtk.MenuItem( "Next Moon Phases:" )
        menu.append( menuItem )

        newMoonLabel = indent + "New: " + self.trimAndLocalise( ephem.next_new_moon( ephem.now() ) )
        firstQuarterLabel = indent + "First Quarter: " + self.trimAndLocalise( ephem.next_first_quarter_moon( ephem.now() ) )
        fullMoonLabel = indent + "Full: " + self.trimAndLocalise( ephem.next_full_moon( ephem.now() ) )
        thirdQuarterLabel = indent + "Third Quarter: " + self.trimAndLocalise( ephem.next_last_quarter_moon( ephem.now() ) )
        if lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON or lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS:
            # third, new, first, full
            nextMoonOneMenuItem = Gtk.MenuItem( thirdQuarterLabel )
            nextMoonTwoMenuItem = Gtk.MenuItem( newMoonLabel )
            nextMoonThreeMenuItem = Gtk.MenuItem( firstQuarterLabel )
            nextMoonFourMenuItem = Gtk.MenuItem( fullMoonLabel )
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER or lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT:
            # new, first, full, third
            nextMoonOneMenuItem = Gtk.MenuItem( newMoonLabel )
            nextMoonTwoMenuItem = Gtk.MenuItem( firstQuarterLabel )
            nextMoonThreeMenuItem = Gtk.MenuItem( fullMoonLabel )
            nextMoonFourMenuItem = Gtk.MenuItem( thirdQuarterLabel )
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON or lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT:
            # first, full, third, new 
            nextMoonOneMenuItem = Gtk.MenuItem( firstQuarterLabel )
            nextMoonTwoMenuItem = Gtk.MenuItem( fullMoonLabel )
            nextMoonThreeMenuItem = Gtk.MenuItem( thirdQuarterLabel )
            nextMoonFourMenuItem = Gtk.MenuItem( newMoonLabel )
        else: # lunarPhase == LUNAR_PHASE_FIRST_QUARTER or lunarPhase == LUNAR_PHASE_WAXING_GIBBOUS
            # full, third, new, first
            nextMoonOneMenuItem = Gtk.MenuItem( fullMoonLabel )
            nextMoonTwoMenuItem = Gtk.MenuItem( thirdQuarterLabel )
            nextMoonThreeMenuItem = Gtk.MenuItem( newMoonLabel )
            nextMoonFourMenuItem = Gtk.MenuItem( firstQuarterLabel )

        if self.showSubmenu == True:
            subMenu = Gtk.Menu()
            subMenu.append( nextMoonOneMenuItem )
            subMenu.append( nextMoonTwoMenuItem )
            subMenu.append( nextMoonThreeMenuItem )
            subMenu.append( nextMoonFourMenuItem )
            menuItem.set_submenu( subMenu )
        else:
            menu.append( nextMoonOneMenuItem )
            menu.append( nextMoonTwoMenuItem )
            menu.append( nextMoonThreeMenuItem )
            menu.append( nextMoonFourMenuItem )

        city = ephem.city( self.cityName )

        menuItem = Gtk.MenuItem( "Moonrise:" )
        menu.append( menuItem )

        previousMoonriseMenuItem = Gtk.MenuItem( self.getRiseSetText( indent + "Previous ", city.previous_rising, ephem.Moon ) )
        nextMoonriseMenuItem = Gtk.MenuItem( self.getRiseSetText( indent + "Next ", city.next_rising, ephem.Moon ) )

        if self.showSubmenu == True:
            subMenu = Gtk.Menu()
            subMenu.append( previousMoonriseMenuItem )
            subMenu.append( nextMoonriseMenuItem )
            menuItem.set_submenu( subMenu )
        else:
            menu.append( previousMoonriseMenuItem )
            menu.append( nextMoonriseMenuItem )

        menuItem = Gtk.MenuItem( "Moonset:" )
        menu.append( menuItem )

        previousMoonsetMenuItem = Gtk.MenuItem( self.getRiseSetText( indent + "Previous ", city.previous_setting, ephem.Moon ) )
        nextMoonsetMenuItem = Gtk.MenuItem( self.getRiseSetText( indent + "Next ", city.next_setting, ephem.Moon ) )

        if self.showSubmenu == True:
            subMenu = Gtk.Menu()
            subMenu.append( previousMoonsetMenuItem )
            subMenu.append( nextMoonsetMenuItem )
            menuItem.set_submenu( subMenu )
        else:
            menu.append( previousMoonsetMenuItem )
            menu.append( nextMoonsetMenuItem )

        menuItem = Gtk.MenuItem( "Sunrise:" )
        menu.append( menuItem )

        previousSunriseMenuItem = Gtk.MenuItem( self.getRiseSetText( indent + "Previous ", city.previous_rising, ephem.Sun ) )
        nextSunriseMenuItem = Gtk.MenuItem( self.getRiseSetText( indent + "Next ", city.next_rising, ephem.Sun ) )

        if self.showSubmenu == True:
            subMenu = Gtk.Menu()
            subMenu.append( previousSunriseMenuItem )
            subMenu.append( nextSunriseMenuItem )
            menuItem.set_submenu( subMenu )
        else:
            menu.append( previousSunriseMenuItem )
            menu.append( nextSunriseMenuItem )

        menuItem = Gtk.MenuItem( "Sunset:" )
        menu.append( menuItem )

        previousSunsetMenuItem = Gtk.MenuItem( self.getRiseSetText( indent + "Previous ", city.previous_setting, ephem.Sun ) )
        nextSunsetMenuItem = Gtk.MenuItem( self.getRiseSetText( indent + "Next ", city.next_setting, ephem.Sun ) )

        if self.showSubmenu == True:
            subMenu = Gtk.Menu()
            subMenu.append( previousSunsetMenuItem )
            subMenu.append( nextSunsetMenuItem )
            menuItem.set_submenu( subMenu )
        else:
            menu.append( previousSunsetMenuItem )
            menu.append( nextSunsetMenuItem )

        equinox = ephem.next_equinox( ephem.now() )
        solstice = ephem.next_solstice( ephem.now() )
        if equinox < solstice:
            equinoxSolsticeOneMenuItem = Gtk.MenuItem( "Equinox: " + self.trimAndLocalise( equinox ) )
            equinoxSolsticeTwoMenuItem = Gtk.MenuItem( "Solstice: " + self.trimAndLocalise( solstice ) )
        else:
            equinoxSolsticeOneMenuItem = Gtk.MenuItem( "Solstice: " + self.trimAndLocalise( solstice ) )
            equinoxSolsticeTwoMenuItem = Gtk.MenuItem( "Equinox: " + self.trimAndLocalise( equinox ) )

        menu.append( equinoxSolsticeOneMenuItem )
        menu.append( equinoxSolsticeTwoMenuItem )

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

        if appindicatorImported == True:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu

        menu.show_all()


    def getRiseSetText( self, message, risingSettingFunction, sunOrMoon ):
        try:
            return message + self.trimAndLocalise( risingSettingFunction( sunOrMoon() ) )
        except Exception as e:
            return "    " + e.message


    def trimAndLocalise( self, value ):
        return self.trimFractionalSeconds( str( ephem.localtime( value ) ) )


    def trimFractionalSeconds( self, currentDateTimeString ):
        return currentDateTimeString[ 0 : string.rfind( currentDateTimeString, ":" ) + 3 ]


    def calculateLunarPhase( self, currentDateTime ):
        nextFullMoonDate = ephem.next_full_moon( currentDateTime )
        nextNewMoonDate = ephem.next_new_moon( currentDateTime )
        currentMoonPhase = int( round( ephem.Moon( currentDateTime ).phase ) )
        phase = None
        if nextFullMoonDate < nextNewMoonDate:
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


    def getIconNameForLunarPhase( self, lunarPhase ):
        iconName = IndicatorLunar.LUNAR_PHASE_ICONS[ lunarPhase ]
        if self.showNorthernHemisphereView == True:
            if lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS:
                 iconName = IndicatorLunar.LUNAR_PHASE_ICONS[ IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS ]
            elif lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS:
                 iconName = IndicatorLunar.LUNAR_PHASE_ICONS[ IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS ]
            elif lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT:
                 iconName = IndicatorLunar.LUNAR_PHASE_ICONS[ IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT ]
            elif lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT:
                 iconName = IndicatorLunar.LUNAR_PHASE_ICONS[ IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT ]
            elif lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER:
                 iconName = IndicatorLunar.LUNAR_PHASE_ICONS[ IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER ]
            elif lunarPhase == IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER:
                 iconName = IndicatorLunar.LUNAR_PHASE_ICONS[ IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER ]

        return iconName


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def onAbout( self, widget ):
        dialog = Gtk.AboutDialog()
        dialog.set_program_name( IndicatorLunar.NAME )
        dialog.set_comments( IndicatorLunar.AUTHOR + "\n\nCalculations courtesy of Ephem.\n" )
        dialog.set_website( IndicatorLunar.WEBSITE )
        dialog.set_website_label( IndicatorLunar.WEBSITE )
        dialog.set_version( IndicatorLunar.VERSION )
        dialog.set_license( IndicatorLunar.LICENSE )
        dialog.run()
        dialog.destroy()
        dialog = None


    def onPreferences( self, widget ):
        if self.dialog is not None:
            return

        notebook = Gtk.Notebook()

        # First tab - display settings.
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

        showHourlyWerewolfWarningCheckbox = Gtk.CheckButton( "Hourly werewolf warning" )
        showHourlyWerewolfWarningCheckbox.set_active( self.showHourlyWerewolfWarning )
        showHourlyWerewolfWarningCheckbox.set_tooltip_text( "Shows an hourly screen notification when approaching a full moon" )
        grid.attach( showHourlyWerewolfWarningCheckbox, 0, 3, 2, 1 )

        label = Gtk.Label( "  Illumination %" )
        label.set_sensitive( showHourlyWerewolfWarningCheckbox.get_active() )
        label.set_margin_left( 15 )
        grid.attach( label, 0, 4, 1, 1 )

        spinner = Gtk.SpinButton()
        spinner.set_adjustment( Gtk.Adjustment( self.werewolfWarningStartIlluminationPercentage, 0, 100, 1, 5, 0 ) )
        spinner.set_tooltip_text( "The warning will start after the new moon (0%) and commence at the specified illumination" )
        spinner.set_sensitive( showHourlyWerewolfWarningCheckbox.get_active() )
        spinner.set_hexpand( True )
        grid.attach( spinner, 1, 4, 1, 1 )

        showHourlyWerewolfWarningCheckbox.connect( "toggled", self.onShowHourlyWerewolfWarningCheckbox, label, spinner )

        notebook.append_page( grid, Gtk.Label( "Display" ) )

        # Second tab - location.
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

        # Third tab - general settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showAsSubmenusCheckbox = Gtk.CheckButton( "Show as submenus" )
        showAsSubmenusCheckbox.set_active( self.showSubmenu )
        grid.attach( showAsSubmenusCheckbox, 0, 0, 1, 1 )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 1, 1, 1 )

        notebook.append_page( grid, Gtk.Label( "General" ) )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )

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
            self.showHourlyWerewolfWarning = showHourlyWerewolfWarningCheckbox.get_active()
            self.showSubmenu = showAsSubmenusCheckbox.get_active()
            self.werewolfWarningStartIlluminationPercentage = spinner.get_value_as_int()
            
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
        if city != "" and _city_data.has_key( city ):
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


    def onShowHourlyWerewolfWarningCheckbox( self, source, spinner, label ):
        label.set_sensitive( source.get_active() )
        spinner.set_sensitive( source.get_active() )


    def loadSettings( self ):
        self.getDefaultCity()
        self.showHourlyWerewolfWarning = True
        self.showIllumination = True
        self.showNorthernHemisphereView = True
        self.showPhase = True
        self.showSubmenu = False
        self.werewolfWarningStartIlluminationPercentage = 100

        if os.path.isfile( IndicatorLunar.SETTINGS_FILE ):
            try:
                with open( IndicatorLunar.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                global _city_data
                cityElevation = settings.get( IndicatorLunar.SETTINGS_CITY_ELEVATION, _city_data.get( self.cityName )[ 2 ] )
                cityLatitude = settings.get( IndicatorLunar.SETTINGS_CITY_LATITUDE, _city_data.get( self.cityName )[ 0 ] )
                cityLongitude = settings.get( IndicatorLunar.SETTINGS_CITY_LONGITUDE, _city_data.get( self.cityName )[ 1 ] )
                self.cityName = settings.get( IndicatorLunar.SETTINGS_CITY_NAME, self.cityName )
                self.showHourlyWerewolfWarning = settings.get( IndicatorLunar.SETTINGS_SHOW_HOURLY_WEREWOLF_WARNING, self.showHourlyWerewolfWarning )
                self.showIllumination = settings.get( IndicatorLunar.SETTINGS_SHOW_ILLUMINATION, self.showIllumination )
                self.showNorthernHemisphereView = settings.get( IndicatorLunar.SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW, self.showNorthernHemisphereView )
                self.showPhase = settings.get( IndicatorLunar.SETTINGS_SHOW_PHASE, self.showPhase )
                self.showSubmenu = settings.get( IndicatorLunar.SETTINGS_SHOW_SUBMENU, self.showSubmenu )
                self.werewolfWarningStartIlluminationPercentage = settings.get( IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE, self.werewolfWarningStartIlluminationPercentage )

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
                self.cityName = sorted( self.cities.keys(), key = locale.strxfrm )[ 0 ]

        except Exception as e:
            logging.exception( e )
            logging.error( "Error getting default cityName." )
            self.cityName = sorted( self.cities.keys(), key = locale.strxfrm )[ 0 ]


    def saveSettings( self ):
        try:
            settings = {
                IndicatorLunar.SETTINGS_CITY_ELEVATION: _city_data.get( self.cityName )[ 2 ],
                IndicatorLunar.SETTINGS_CITY_LATITUDE: _city_data.get( self.cityName )[ 0 ],
                IndicatorLunar.SETTINGS_CITY_LONGITUDE: _city_data.get( self.cityName )[ 1 ],
                IndicatorLunar.SETTINGS_CITY_NAME: self.cityName,
                IndicatorLunar.SETTINGS_SHOW_HOURLY_WEREWOLF_WARNING: self.showHourlyWerewolfWarning,
                IndicatorLunar.SETTINGS_SHOW_ILLUMINATION: self.showIllumination,
                IndicatorLunar.SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW: self.showNorthernHemisphereView,
                IndicatorLunar.SETTINGS_SHOW_PHASE: self.showPhase,
                IndicatorLunar.SETTINGS_SHOW_SUBMENU: self.showSubmenu,
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE: self.werewolfWarningStartIlluminationPercentage
            }

            with open( IndicatorLunar.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorLunar.SETTINGS_FILE )


if __name__ == "__main__":
    indicator = IndicatorLunar()
    indicator.main()