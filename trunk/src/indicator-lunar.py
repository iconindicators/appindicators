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


appindicatorImported = True
try:
    import appindicator
except:
    appindicatorImported = False

pynotifyImported = True
try:
    import pynotify
except:
    pynotifyImported = False

import datetime
import ephem
import gobject
import gtk
import json
import logging
import os
import shutil
import string
import sys


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-lunar"
    VERSION = "1.0.9"
    ICON = "indicator-lunar"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_SHOW_HOURLY_WEREWOLF_WARNING = "showHourlyWerewolfWarning"
    SETTINGS_SHOW_ILLUMINATION = "showIllumination"
    SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW = "showNorthernHemisphereView"
    SETTINGS_SHOW_PHASE = "showPhase"

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

        if pynotifyImported == True:
            pynotify.init( IndicatorLunar.NAME )

        # One of the install dependencies for Debian/Ubuntu is that appindicator exists.
        # However the appindicator only works under Ubuntu Unity - we need to default to GTK icon if not running Unity (say Lubuntu).
        global appindicatorImported
        unityIsInstalled = os.getenv( "XDG_CURRENT_DESKTOP" )
        if unityIsInstalled is None:
            appindicatorImported = False
        elif str( unityIsInstalled ).lower() != "Unity".lower():
            appindicatorImported = False

        self.buildMenu()

        # Create the status icon...either Unity or GTK.
        if appindicatorImported == True:
            self.indicator = appindicator.Indicator( IndicatorLunar.NAME, "", appindicator.CATEGORY_APPLICATION_STATUS )
            self.indicator.set_status( appindicator.STATUS_ACTIVE )
            self.indicator.set_menu( self.menu )
        else:
            self.statusicon = gtk.StatusIcon()
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def main( self ):
        self.update()
        gobject.timeout_add_seconds( 60 * 60, self.update )
        gtk.main()


    def update( self ):
        currentDateTime = datetime.datetime.now()
        lunarPhase = self.calculateLunarPhase( currentDateTime )

        if self.showIllumination == True and self.showPhase == True:
            labelTooltip = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] + " (" + str( int( round( ephem.Moon( currentDateTime ).phase ) ) ) + "%)"
        elif self.showIllumination == True:
            labelTooltip = str( int( round( ephem.Moon( currentDateTime ).phase ) ) ) + "%"
        elif self.showPhase == True:
            labelTooltip = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ]
        else:
            labelTooltip = None

        if appindicatorImported == True:
            self.indicator.set_icon( self.getIconNameForLunarPhase( lunarPhase ) )
            self.indicator.set_label( labelTooltip )
        else:
            self.statusicon.set_from_icon_name( self.getIconNameForLunarPhase( lunarPhase ) )
            self.statusicon.set_tooltip( labelTooltip )

        self.phaseMenuItem.set_label( "Phase: " + IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] )
        self.illuminationMenuItem.set_label( "Illumination: " + str( int( round( ephem.Moon( currentDateTime ).phase ) ) ) + "%" )
        self.distanceToEarthInKMMenuItem.set_label( "    Moon to Earth: " + str( int( round( ephem.Moon( currentDateTime ).earth_distance * ephem.meters_per_au / 1000 ) ) ) + " km" )
        self.distanceToEarthInAUMenuItem.set_label( "    Moon to Earth: " + str( round( ephem.Moon( currentDateTime ).earth_distance, 4 ) ) + " AU" )
        self.distanceToSunMenuItem.set_label( "    Moon to Sun: " + str( round( ephem.Moon( currentDateTime ).sun_distance, 3 ) )  + " AU" )
        self.constellationMenuItem.set_label( "Constellation: " + ephem.constellation( ephem.Moon( currentDateTime ) )[ 1 ] )

        newMoonLabel = "    New: " + self.trimFractionalSeconds( str( ephem.next_new_moon( ephem.now() ) ) )
        firstQuarterLabel = "    First Quarter: " + self.trimFractionalSeconds( str( ephem.next_first_quarter_moon( ephem.now() ) ) )
        fullMoonLabel = "    Full: " + self.trimFractionalSeconds( str( ephem.next_full_moon( ephem.now() ) ) )
        thirdQuarterLabel = "    Third Quarter: " + self.trimFractionalSeconds( str( ephem.next_last_quarter_moon( ephem.now() ) ) )
        if lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON or lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS:
            # third, new, first, full
            self.nextMoonOneMenuItem.set_label( thirdQuarterLabel )
            self.nextMoonTwoMenuItem.set_label( newMoonLabel )
            self.nextMoonThreeMenuItem.set_label( firstQuarterLabel )
            self.nextMoonFourMenuItem.set_label( fullMoonLabel )
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER or lunarPhase == IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT:
            # new, first, full, third
            self.nextMoonOneMenuItem.set_label( newMoonLabel )
            self.nextMoonTwoMenuItem.set_label( firstQuarterLabel )
            self.nextMoonThreeMenuItem.set_label( fullMoonLabel )
            self.nextMoonFourMenuItem.set_label( thirdQuarterLabel )
        elif lunarPhase == IndicatorLunar.LUNAR_PHASE_NEW_MOON or lunarPhase == IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT:
            # first, full, third, new 
            self.nextMoonOneMenuItem.set_label( firstQuarterLabel )
            self.nextMoonTwoMenuItem.set_label( fullMoonLabel )
            self.nextMoonThreeMenuItem.set_label( thirdQuarterLabel )
            self.nextMoonFourMenuItem.set_label( newMoonLabel )
        else: # lunarPhase == LUNAR_PHASE_FIRST_QUARTER or lunarPhase == LUNAR_PHASE_WAXING_GIBBOUS
            # full, third, new, first
            self.nextMoonOneMenuItem.set_label( fullMoonLabel )
            self.nextMoonTwoMenuItem.set_label( thirdQuarterLabel )
            self.nextMoonThreeMenuItem.set_label( newMoonLabel )
            self.nextMoonFourMenuItem.set_label( firstQuarterLabel )

        equinox = ephem.next_equinox( ephem.now() )
        solstice = ephem.next_solstice( ephem.now() )
        if equinox < solstice:
            self.equinoxSolsticeOneMenuItem.set_label( "Equinox: " + self.trimFractionalSeconds( str( equinox ) ) )
            self.equinoxSolsticeTwoMenuItem.set_label( "Solstice: " + self.trimFractionalSeconds( str( solstice ) ) )
        else:
            self.equinoxSolsticeOneMenuItem.set_label( "Solstice: " + self.trimFractionalSeconds( str( solstice ) ) )
            self.equinoxSolsticeTwoMenuItem.set_label( "Equinox: " + self.trimFractionalSeconds( str( equinox ) ) )

        if pynotifyImported == True and self.showHourlyWerewolfWarning == True and lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON:
            pynotify.Notification( "Warning: Werewolves about!!!", "", IndicatorLunar.LUNAR_PHASE_ICONS[ IndicatorLunar.LUNAR_PHASE_FULL_MOON ] ).show()

        return True # Needed so the timer continues!


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


    def buildMenu( self ):
        self.menu = gtk.Menu()

        self.phaseMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.phaseMenuItem )

        self.illuminationMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.illuminationMenuItem )

        self.constellationMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.constellationMenuItem )

        self.menu.append( gtk.MenuItem( "Distances:" ) )

        self.distanceToEarthInKMMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.distanceToEarthInKMMenuItem )

        self.distanceToEarthInAUMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.distanceToEarthInAUMenuItem )

        self.distanceToSunMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.distanceToSunMenuItem )

        self.menu.append( gtk.MenuItem( "Next Phases:" ) )

        self.nextMoonOneMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.nextMoonOneMenuItem )

        self.nextMoonTwoMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.nextMoonTwoMenuItem )

        self.nextMoonThreeMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.nextMoonThreeMenuItem )

        self.nextMoonFourMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.nextMoonFourMenuItem )

        self.equinoxSolsticeOneMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.equinoxSolsticeOneMenuItem )

        self.equinoxSolsticeTwoMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.equinoxSolsticeTwoMenuItem )

        self.menu.append( gtk.SeparatorMenuItem() )

        preferencesMenuItem = gtk.MenuItem( "Preferences" )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        self.menu.append( preferencesMenuItem )

        aboutMenuItem = gtk.ImageMenuItem( stock_id = gtk.STOCK_ABOUT )
        aboutMenuItem.connect( "activate", self.onAbout )
        self.menu.append( aboutMenuItem )

        quitMenuItem = gtk.ImageMenuItem( stock_id = gtk.STOCK_QUIT )
        quitMenuItem.connect( "activate", gtk.main_quit )
        self.menu.append( quitMenuItem )

        self.menu.show_all()


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, gtk.status_icon_position_menu, 1, gtk.get_current_event_time(), self.statusicon )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, gtk.status_icon_position_menu, button, time, self.statusicon )


    def onAbout( self, widget ):
        dialog = gtk.AboutDialog()
        dialog.set_name( IndicatorLunar.NAME )
        dialog.set_version( IndicatorLunar.VERSION )
        dialog.set_comments( IndicatorLunar.AUTHOR + "\n\n" + "Calculations courtesy of PyEphem." )
        dialog.set_license( "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0" )
        dialog.set_website( "https://launchpad.net/~thebernmeister" )
        dialog.run()
        dialog.destroy()


    def onPreferences( self, widget ):
        if self.dialog is not None:
            return

        self.dialog = gtk.Dialog( "Preferences", None, 0, ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK ) )

        table = gtk.Table( 5, 1, False )
        table.set_col_spacings( 5 )
        table.set_row_spacings( 5 )

        showPhaseCheckbox = gtk.CheckButton( "Show phase" )
        showPhaseCheckbox.set_active( self.showPhase )
        table.attach( showPhaseCheckbox, 0, 1, 0, 1 )

        showIlluminationCheckbox = gtk.CheckButton( "Show illumination" )
        showIlluminationCheckbox.set_active( self.showIllumination )
        table.attach( showIlluminationCheckbox, 0, 1, 1, 2 )

        showNorthernHemisphereViewCheckbox = gtk.CheckButton( "Northern hemisphere view" )
        showNorthernHemisphereViewCheckbox.set_active( self.showNorthernHemisphereView )
        table.attach( showNorthernHemisphereViewCheckbox, 0, 1, 2, 3 )

        showHourlyWerewolfWarningCheckbox = gtk.CheckButton( "Hourly werewolf warning" )
        showHourlyWerewolfWarningCheckbox.set_active( self.showHourlyWerewolfWarning )
        showHourlyWerewolfWarningCheckbox.set_tooltip_text( "Screen notification on each hour during a full moon" )
        table.attach( showHourlyWerewolfWarningCheckbox, 0, 1, 3, 4 )

        autostartCheckbox = gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorLunar.AUTOSTART_PATH + IndicatorLunar.DESKTOP_FILE ) )
        table.attach( autostartCheckbox, 0, 1, 4, 5 )

        self.dialog.vbox.pack_start( table, True, True, 10 )
        self.dialog.set_border_width( 10 )

        self.dialog.show_all()
        response = self.dialog.run()
        if response == gtk.RESPONSE_OK:
            self.showPhase = showPhaseCheckbox.get_active()
            self.showIllumination = showIlluminationCheckbox.get_active()
            self.showNorthernHemisphereView = showNorthernHemisphereViewCheckbox.get_active()
            self.showHourlyWerewolfWarning = showHourlyWerewolfWarningCheckbox.get_active()
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

        self.dialog.destroy()
        self.dialog = None
        self.update()


    def loadSettings( self ):
        self.showHourlyWerewolfWarning = True
        self.showIllumination = True
        self.showNorthernHemisphereView = True
        self.showPhase = True

        if os.path.isfile( IndicatorLunar.SETTINGS_FILE ):
            try:
                with open( IndicatorLunar.SETTINGS_FILE, 'r' ) as f:
                    settings = json.load( f )

                self.showHourlyWerewolfWarning = settings.get( IndicatorLunar.SETTINGS_SHOW_HOURLY_WEREWOLF_WARNING, self.showHourlyWerewolfWarning )
                self.showIllumination = settings.get( IndicatorLunar.SETTINGS_SHOW_ILLUMINATION, self.showIllumination )
                self.showNorthernHemisphereView = settings.get( IndicatorLunar.SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW, self.showNorthernHemisphereView )
                self.showPhase = settings.get( IndicatorLunar.SETTINGS_SHOW_PHASE, self.showPhase )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorLunar.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorLunar.SETTINGS_SHOW_HOURLY_WEREWOLF_WARNING: self.showHourlyWerewolfWarning,
                IndicatorLunar.SETTINGS_SHOW_ILLUMINATION: self.showIllumination,
                IndicatorLunar.SETTINGS_SHOW_NORTHERN_HEMISPHERE_VIEW: self.showNorthernHemisphereView,
                IndicatorLunar.SETTINGS_SHOW_PHASE: self.showPhase
            }

            with open( IndicatorLunar.SETTINGS_FILE, 'w' ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorLunar.SETTINGS_FILE )


if __name__ == "__main__":
    indicator = IndicatorLunar()
    indicator.main()