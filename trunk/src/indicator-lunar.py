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


# 
# 
# This version contains code to start from NOW and increase time by a certain amount to test the lunar phase/icon change. 
# For debug purposes!!!
# 
# 


try:
    from gi.repository import AppIndicator3 as appindicator
except:
    pass

from gi.repository import GObject as gobject
from gi.repository import Gdk, GdkPixbuf
from gi.repository import Gtk

notifyImported = True
try:
    from gi.repository import Notify
except:
    notifyImported = False

import datetime
import json
import locale
import logging
import os
import shutil
import subprocess
import sys

try:
    import ephem
    from ephem.cities import _city_data
except:
    dialog = Gtk.MessageDialog( None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "You must also install python3-ephem!" )
    dialog.set_title( "indicator-lunar" )
    dialog.run()
    sys.exit()


from datetime import timedelta   #TODO Remove ###################################################################################################################


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-lunar"
    VERSION = "1.0.14"
    ICON = NAME
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
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
    SETTINGS_SHOW_HOURLY_WEREWOLF_WARNING = "showHourlyWerewolfWarning"
    SETTINGS_SHOW_ILLUMINATION = "showIllumination"
    SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW = "showNorthernHemisphereView"
    SETTINGS_SHOW_PHASE = "showPhase"
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


    def __init__( self ):
        logging.basicConfig( file = sys.stderr, level = logging.INFO )
        self.loadSettings()
        self.dialog = None

        if notifyImported == True:
            Notify.init( IndicatorLunar.NAME )

        try:
            self.appindicatorImported = True
            self.indicator = appindicator.Indicator.new( IndicatorLunar.NAME, "", appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_icon_theme_path( os.getenv( "HOME" ) )
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.indicator.set_menu( Gtk.Menu() ) # Set an empty menu to get things rolling...
        except:
#TODO Need to set some additional icon theme path?
            self.appindicatorImported = False
            self.menu = Gtk.Menu() # Set an empty menu to get things rolling...
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )

        print( "appIndicator imported: " + str( self.appindicatorImported ) )
        print( "Theme: " + self.getIconTheme() )

    def main( self ):

        self.now = datetime.datetime.now()
        self.update()
#        gobject.timeout_add_seconds( 60 * 60, self.update )
        gobject.timeout_add_seconds( 1, self.update )
        Gtk.main()


    def update( self ):
        self.now = self.now + timedelta( hours = 17 )
        
        lunarPhase = self.calculateLunarPhase()

        moon = ephem.Moon(self.now)
        moon.compute(self.now)
#        moon = ephem.Moon()
#        moon.compute()
        percentageIllumination = int( round( moon.phase ) )

        print( self.now, percentageIllumination, lunarPhase )

        self.buildMenu( lunarPhase )

        if self.showIllumination == True and self.showPhase == True:
            labelTooltip = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] + " (" + str( percentageIllumination ) + "%)"
        elif self.showIllumination == True:
            labelTooltip = str( percentageIllumination ) + "%"
        elif self.showPhase == True:
            labelTooltip = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ]
        else:
            labelTooltip = ""

        self.createIconForLunarPhase( lunarPhase, percentageIllumination )
        if self.appindicatorImported == True:
            self.indicator.set_icon( IndicatorLunar.SVG_ICON )
            self.indicator.set_label( labelTooltip, "" ) # Second parameter is a guide for how wide the text could get (see label-guide in http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html).
        else:
#TODO Test on Lubuntu 12.04
            self.statusicon.set_from_file( IndicatorLunar.SVG_ICON )
            self.statusicon.set_tooltip_text( labelTooltip )

        phaseIsBetweenNewAndFullInclusive = ( lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS ) or \
            ( lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON )

#TODO Make sure this works on Lubuntu 12.04/12.10
        if notifyImported == True and \
            self.showHourlyWerewolfWarning == True and \
            percentageIllumination >= self.werewolfWarningStartIlluminationPercentage and \
            phaseIsBetweenNewAndFullInclusive:
            Notify.Notification.new( "WARNING: Werewolves about!!!", "", IndicatorLunar.SVG_FILE ).show()

        return True # Needed so the timer continues!


    def buildMenu( self, lunarPhase ):
        if self.appindicatorImported == True:
            menu = self.indicator.get_menu()
        else:
            menu = self.menu

        menu.popdown() # Make the existing menu, if visible, disappear (if we don't do this we get GTK complaints).

        # Create the new menu and populate...
        menu = Gtk.Menu()

        city = ephem.city( self.cityName )
        indent = "    "

        # Moon
        menuItem = Gtk.MenuItem( "Moon" )
        menu.append( menuItem )

        self.createPlanetSubmenu( menuItem, city, ephem.Moon() )

        menuItem.get_submenu().append( Gtk.MenuItem( "Phase: " + IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] ) )

        menuItem.get_submenu().append( Gtk.SeparatorMenuItem() )

        menuItem.get_submenu().append( Gtk.MenuItem( "Next Phases" ) )

        newMoonLabel = indent + "New: " + self.localiseAndTrim( ephem.next_new_moon( ephem.now() ) )
        firstQuarterLabel = indent + "First Quarter: " + self.localiseAndTrim( ephem.next_first_quarter_moon( ephem.now() ) )
        fullMoonLabel = indent + "Full: " + self.localiseAndTrim( ephem.next_full_moon( ephem.now() ) )
        thirdQuarterLabel = indent + "Third Quarter: " + self.localiseAndTrim( ephem.next_last_quarter_moon( ephem.now() ) )
        if lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON or lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS:
            # third, new, first, full
            self.appendToLunarMenu( menuItem.get_submenu(), thirdQuarterLabel, newMoonLabel, firstQuarterLabel, fullMoonLabel )
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER or lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT:
            # new, first, full, third
            self.appendToLunarMenu( menuItem.get_submenu(), newMoonLabel, firstQuarterLabel, fullMoonLabel, thirdQuarterLabel )
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON or lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT:
            # first, full, third, new 
            self.appendToLunarMenu( menuItem.get_submenu(), firstQuarterLabel, fullMoonLabel, thirdQuarterLabel, newMoonLabel )
        else: # lunarPhase == LUNAR_PHASE_FIRST_QUARTER or lunarPhase == LUNAR_PHASE_WAXING_GIBBOUS
            # full, third, new, first
            self.appendToLunarMenu( menuItem.get_submenu(), fullMoonLabel, thirdQuarterLabel, newMoonLabel, firstQuarterLabel )

        # Sun
        menuItem = Gtk.MenuItem( "Sun" )
        menu.append( menuItem )

        subMenu = Gtk.Menu()
        menuItem.set_submenu( subMenu )

        rising = city.next_rising( ephem.Sun() )
        setting = city.next_setting( ephem.Sun() )
        if rising > setting:
            subMenu.append( Gtk.MenuItem( "Set: " + self.localiseAndTrim( setting ) ) )
            subMenu.append( Gtk.MenuItem( "Rise: " + self.localiseAndTrim( rising ) ) )
        else:
            subMenu.append( Gtk.MenuItem( "Rise: " + self.localiseAndTrim( rising ) ) )
            subMenu.append( Gtk.MenuItem( "Set: " + self.localiseAndTrim( setting ) ) )

        subMenu.append( Gtk.SeparatorMenuItem() )

        # Solstice/Equinox
        equinox = ephem.next_equinox( ephem.now() )
        solstice = ephem.next_solstice( ephem.now() )
        if equinox < solstice:
            subMenu.append( Gtk.MenuItem( "Equinox: " + self.localiseAndTrim( equinox ) ) )
            subMenu.append( Gtk.MenuItem( "Solstice: " + self.localiseAndTrim( solstice ) ) )
        else:
            subMenu.append( Gtk.MenuItem( "Solstice: " + self.localiseAndTrim( solstice ) ) ) 
            subMenu.append( Gtk.MenuItem( "Equinox: " + self.localiseAndTrim( equinox ) ) )

        # Planets
        menu.append( Gtk.MenuItem( "Planets" ) )

        planets = [
            [ "Mercury", ephem.Mercury() ], 
            [ "Venus", ephem.Venus() ], 
            [ "Mars", ephem.Mars() ], 
            [ "Jupiter", ephem.Jupiter() ], 
            [ "Saturn", ephem.Saturn() ], 
            [ "Uranus", ephem.Uranus() ], 
            [ "Neptune", ephem.Neptune() ], 
            [ "Pluto", ephem.Pluto() ] ]

        for planet in planets:
            menuItem = Gtk.MenuItem( indent + planet[ 0 ] )
            self.createPlanetSubmenu( menuItem, city, planet[ 1 ] )
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

        if self.appindicatorImported == True:
            self.indicator.set_menu( menu )
        else:
            self.menu = menu

        menu.show_all()


    def appendToLunarMenu( self, submenu, label1, label2, label3, label4 ):
        submenu.append( Gtk.MenuItem( label1 ) )
        submenu.append( Gtk.MenuItem( label2 ) )
        submenu.append( Gtk.MenuItem( label3 ) )
        submenu.append( Gtk.MenuItem( label4 ) )


    def createPlanetSubmenu( self, planetMenuItem, city, planet ):
        planet.compute()

        subMenu = Gtk.Menu()
        subMenu.append( Gtk.MenuItem( "Illumination: " + str( int( round( planet.phase ) ) ) + "%" ) )
        subMenu.append( Gtk.MenuItem( "Constellation: " + ephem.constellation( planet )[ 1 ] ) )
        subMenu.append( Gtk.MenuItem( "Distance to Earth: " + str( round( planet.earth_distance, 4 ) ) + " AU" ) )
        subMenu.append( Gtk.MenuItem( "Distance to Sun: " + str( round( planet.sun_distance, 4 ) ) + " AU" ) )

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


    # Takes a float and converts to local time, trims off fractional seconds and returns a string.
    def localiseAndTrim( self, value ):
        localtimeString = str( ephem.localtime( value ) )
        return localtimeString[ 0 : localtimeString.rfind( ":" ) + 3 ]


    def calculateLunarPhase( self ):
        nextFullMoonDate = ephem.next_full_moon( self.now )
        nextNewMoonDate = ephem.next_new_moon( self.now )
        moon = ephem.Moon( self.now )
        moon.compute( self.now )
#        nextFullMoonDate = ephem.next_full_moon( ephem.now() )
#        nextNewMoonDate = ephem.next_new_moon( ephem.now() )
#        moon = ephem.Moon()
#        moon.compute()
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
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER:
            svg = self.getFirstQuarterMoonSVG( self.showNorthernHemisphereView )
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER:
            svg = self.getThirdQuarterMoonSVG( self.showNorthernHemisphereView )
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

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 0, 1, 1 )

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


    def onShowHourlyWerewolfWarningCheckbox( self, source, spinner, label ):
        label.set_sensitive( source.get_active() )
        spinner.set_sensitive( source.get_active() )


    def loadSettings( self ):
        self.getDefaultCity()
        self.showHourlyWerewolfWarning = True
        self.showIllumination = True
        self.showNorthernHemisphereView = True
        self.showPhase = True
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
                IndicatorLunar.SETTINGS_WEREWOLF_WARNING_START_ILLUMINATION_PERCENTAGE: self.werewolfWarningStartIlluminationPercentage
            }

            with open( IndicatorLunar.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorLunar.SETTINGS_FILE )


    def getCrescentGibbousMoonSVG( self, illumination, waning, northernHemisphere, crescent ):
        # http://www.w3.org/TR/SVG/paths.html#PathDataEllipticalArcCommands
        if ( northernHemisphere == True and waning == True ) or ( northernHemisphere == False and waning == False ):
            sweepFlagCircle = str( 0 )
            sweepFlagEllipse = str( 1 ) if crescent else str( 0 ) 
        else:
            sweepFlagCircle = str( 1 )
            sweepFlagEllipse = str( 0 ) if crescent else str( 1 ) 

        radius = self.getMoonRadius()
        diameter = str( 2 * float( radius ) )

        # http://en.wikipedia.org/wiki/Crescent
        if crescent == True:
            ellipseRadiusX = str( float( radius ) * ( 1 - illumination / 50 ) )
        else:
            ellipseRadiusX = str( float( radius ) * ( illumination / 50 - 1 ) )

        circle = 'a' + radius + ',' + radius + ' 0 0,' + sweepFlagCircle + ' 0,' + diameter
        ellipse = 'a' + ellipseRadiusX + ',' + radius + ' 0 0,' + sweepFlagEllipse + ' 0,-' + diameter
        svg = '<path d="M 50 50 v-' + radius + ' ' + circle + ' ' + ellipse + ' " fill="' + self.getColourForIconTheme() + '" />'
        return self.getSVGHeader() + svg + self.getSVGFooter()


    def getFirstQuarterMoonSVG( self, northernHemisphere ):
        # http://www.w3.org/TR/SVG/paths.html#PathDataEllipticalArcCommands
        if northernHemisphere == True:
            sweepFlag = str( 1 )
        else:
            sweepFlag = str( 0 )

        radius = self.getMoonRadius()
        diameter = str( 2 * float( radius ) )
        svg = '<path d="M 50 50 v-' + radius + ' a' + radius + ',' + radius + ' 0 0,' + sweepFlag + ' 0,' + diameter + ' z" fill="' + self.getColourForIconTheme() + '" />'
        return self.getSVGHeader() + svg + self.getSVGFooter()


    def getThirdQuarterMoonSVG( self, northernHemisphere ):
        return self.getFirstQuarterMoonSVG( not northernHemisphere )


    def getFullMoonSVG( self ):
        svg = '<circle cx="50" cy="50" r="' + self.getMoonRadius() + '" fill="' + self.getColourForIconTheme() + '" />'
        return self.getSVGHeader() + svg + self.getSVGFooter()


    def getNewMoonSVG( self ):
        svg = '<circle cx="50" cy="50" r="' + self.getMoonRadius() + '" fill="none" stroke="' + self.getColourForIconTheme() + '" stroke-width="2" />'
        return self.getSVGHeader() + svg + self.getSVGFooter()


    def getSVGHeader( self ):
        return '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' \
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 100 100">'


    def getSVGFooter( self ):
        return '</svg>'


    def getMoonRadius( self ):
        # A radius of 50 is too big and 25 is too small, so choose half way!
        return str( ( 50 - 25 ) / 2 + 25 )


    def getColourForIconTheme( self ):
        iconTheme = self.getIconTheme()
        if iconTheme is None:
            return "#fff200" # This is hicolor...make it the default.
        elif iconTheme == "elementary":
            return "#f4f4f4"
        elif iconTheme == "lubuntu":
            return "#5a5a5a"
        elif iconTheme == "ubuntu-mono-dark":
            return "#dfdbd2"
        elif iconTheme == "ubuntu-mono-light":
            return "#3c3c3c"
        else:
            return "#fff200" # This is hicolor...make it the default.


#TODO Test this works on Lubuntu 12.04 and Lubuntu 12.10
    def getIconTheme( self ):
        return Gtk.Settings().get_default().get_property( "gtk-icon-theme-name" )


if __name__ == "__main__":
    indicator = IndicatorLunar()
    indicator.main()