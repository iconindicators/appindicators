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
import sys


class IndicatorLunar:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-lunar"
    VERSION = "1.0.4"
    ICON = "indicator-lunar"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/" + NAME + ".desktop"
    DESKTOP_PATH = "/usr/share/applications/" + NAME + ".desktop"

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
            labelTooltip = IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] + " (" + str( int( ephem.Moon( currentDateTime ).phase ) ) + "%)"
        elif self.showIllumination == True:
            labelTooltip = str( int( ephem.Moon( currentDateTime ).phase ) ) + "%"
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

        self.illuminationMenuItem.set_label( "Illumination: " + str( int( ephem.Moon( currentDateTime ).phase ) ) + "%" )
        self.phaseMenuItem.set_label( "Phase: " + IndicatorLunar.LUNAR_PHASE_NAMES[ lunarPhase ] )
        self.distanceToEarthMenuItem.set_label( "Distance to Earth: " + str( ephem.Moon( currentDateTime ).earth_distance ) + " AU" )
        self.distanceToSunMenuItem.set_label( "Distance to Sun: " + str( ephem.Moon( currentDateTime ).sun_distance ) + " AU" )
        self.constellationMenuItem.set_label( "Constellation: " + ephem.constellation( ephem.Moon( currentDateTime ) )[ 1 ] )

        if pynotifyImported == True and self.showHourlyWerewolfWarning == True and lunarPhase == IndicatorLunar.LUNAR_PHASE_FULL_MOON:
            pynotify.Notification( "Warning: Werewolves about!!!", "", IndicatorLunar.LUNAR_PHASE_ICONS[ IndicatorLunar.LUNAR_PHASE_FULL_MOON ] ).show()

        return True # Needed so the timer continues!


    def calculateLunarPhase( self, currentDateTime ):
        nextFullMoonDate = ephem.next_full_moon( currentDateTime )
        nextNewMoonDate = ephem.next_new_moon( currentDateTime )
        currentMoon = ephem.Moon( currentDateTime )
        lunarPhase = None
        if nextFullMoonDate < nextNewMoonDate:
            # We are somewhere between a new moon and a full moon...
            if( currentMoon.phase > 98 ):
                lunarPhase = IndicatorLunar.LUNAR_PHASE_FULL_MOON
            elif currentMoon.phase <= 98 and currentMoon.phase > 60:
                lunarPhase = IndicatorLunar.LUNAR_PHASE_WAXING_GIBBOUS
            elif currentMoon.phase <= 60 and currentMoon.phase >= 40:
                lunarPhase = IndicatorLunar.LUNAR_PHASE_FIRST_QUARTER
            elif currentMoon.phase < 40 and currentMoon.phase >= 2:
                lunarPhase = IndicatorLunar.LUNAR_PHASE_WAXING_CRESCENT
            else: # currentMoon.phase < 2
                lunarPhase = IndicatorLunar.LUNAR_PHASE_NEW_MOON
        else:
            # We are somewhere between a full moon and the next new moon...
            if( currentMoon.phase > 98 ):
                lunarPhase = IndicatorLunar.LUNAR_PHASE_FULL_MOON
            elif currentMoon.phase <= 98 and currentMoon.phase > 60:
                lunarPhase = IndicatorLunar.LUNAR_PHASE_WANING_GIBBOUS
            elif currentMoon.phase <= 60 and currentMoon.phase >= 40:
                lunarPhase = IndicatorLunar.LUNAR_PHASE_THIRD_QUARTER
            elif currentMoon.phase < 40 and currentMoon.phase >= 2:
                lunarPhase = IndicatorLunar.LUNAR_PHASE_WANING_CRESCENT
            else: # currentMoon.phase < 2
                lunarPhase = IndicatorLunar.LUNAR_PHASE_NEW_MOON

        return lunarPhase


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

        self.distanceToEarthMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.distanceToEarthMenuItem )

        self.distanceToSunMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.distanceToSunMenuItem )

        self.constellationMenuItem = gtk.MenuItem( "" )
        self.menu.append( self.constellationMenuItem )

        self.menu.append( gtk.SeparatorMenuItem() )

        showPhaseMenuItem = gtk.CheckMenuItem( "Show phase" )
        showPhaseMenuItem.set_active( self.showPhase )
        showPhaseMenuItem.connect( "activate", self.onShowPhase )
        self.menu.append( showPhaseMenuItem )

        showIlluminationMenuItem = gtk.CheckMenuItem( "Show illumination" )
        showIlluminationMenuItem.set_active( self.showIllumination )
        showIlluminationMenuItem.connect( "activate", self.onShowIllumination )
        self.menu.append( showIlluminationMenuItem )

        showNorthernHemisphereViewMenuItem = gtk.CheckMenuItem( "Northern hemisphere view" )
        showNorthernHemisphereViewMenuItem.set_active( self.showNorthernHemisphereView )
        showNorthernHemisphereViewMenuItem.connect( "activate", self.onShowNorthernHemisphereView )
        self.menu.append( showNorthernHemisphereViewMenuItem )

        showHourlyWerewolfWarningMenuItem = gtk.CheckMenuItem( "Hourly werewolf warning" )
        showHourlyWerewolfWarningMenuItem.set_active( self.showHourlyWerewolfWarning )
        showHourlyWerewolfWarningMenuItem.connect( "activate", self.onShowHourlyWerewolfWarning )
        self.menu.append( showHourlyWerewolfWarningMenuItem )

        autoStartMenuItem = gtk.CheckMenuItem( "Autostart" )
        autoStartMenuItem.set_active( os.path.exists( IndicatorLunar.AUTOSTART_PATH ) )
        autoStartMenuItem.connect( "activate", self.onAutoStart )
        self.menu.append( autoStartMenuItem )

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
        dialog.set_website( "https://launchpad.net/~thebernmeister/+archive/indicator-lunar" )
        dialog.run()
        dialog.destroy()


    def onShowHourlyWerewolfWarning( self, widget ):
        self.showHourlyWerewolfWarning = widget.active
        self.saveSettings()
        self.update()


    def onShowIllumination( self, widget ):
        self.showIllumination = widget.active
        self.saveSettings()
        self.update()


    def onShowNorthernHemisphereView( self, widget ):
        self.showNorthernHemisphereView = widget.active
        self.saveSettings()
        self.update()


    def onShowPhase( self, widget ):
        self.showPhase = widget.active
        self.saveSettings()
        self.update()


    def onAutoStart( self, widget ):
        if widget.active:
            try:
                shutil.copy( IndicatorLunar.DESKTOP_PATH, IndicatorLunar.AUTOSTART_PATH )
            except Exception as e:
                logging.exception( e )
        else:
            try:
                os.remove( IndicatorLunar.AUTOSTART_PATH )
            except: pass


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