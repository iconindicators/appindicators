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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Astronomical calculation engine for computing lunar, solar, planetary, star, orbital element and satellite information.
# Currently uses PyEphem, http://rhodesmill.org/pyephem, as the underlying engine.


import argparse
import calendar, copy, datetime, eclipse, json, locale, logging, math, os, pickle, pythonutils, re, satellite, shutil, subprocess, sys, tempfile, threading, time


try:
    import ephem
    from ephem.cities import _city_data
    from ephem.stars import stars
except:
    pass #TODO Handle
#     pythonutils.showMessage( None, Gtk.MessageType.ERROR, _( "You must also install python3-ephem!" ) )
#     sys.exit()


class AstroBodyType: Moon, OrbitalElement, Planet, PlanetaryMoon, Satellite, Star, Sun = range( 7 )


class Astro( object ):

    DATA_ALTITUDE = "ALTITUDE"
    DATA_AZIMUTH = "AZIMUTH"
    DATA_BRIGHT_LIMB = "BRIGHT LIMB"
    DATA_CONSTELLATION = "CONSTELLATION"
    DATA_DAWN = "DAWN"
    DATA_DECLINATION = "DECLINATION"
    DATA_DISTANCE_TO_EARTH = "DISTANCE TO EARTH"
    DATA_DISTANCE_TO_EARTH_KM = "DISTANCE TO EARTH KM"
    DATA_DISTANCE_TO_SUN = "DISTANCE TO SUN"
    DATA_DUSK = "DUSK"
    DATA_EARTH_TILT = "EARTH TILT"
    DATA_EARTH_VISIBLE = "EARTH VISIBLE"
    DATA_ECLIPSE_DATE_TIME = "ECLIPSE DATE TIME"
    DATA_ECLIPSE_LATITUDE = "ECLIPSE LATITUDE"
    DATA_ECLIPSE_LONGITUDE = "ECLIPSE LONGITUDE"
    DATA_ECLIPSE_TYPE = "ECLIPSE TYPE"
    DATA_EQUINOX = "EQUINOX"
    DATA_FIRST_QUARTER = "FIRST QUARTER"
    DATA_FULL = "FULL"
    DATA_ILLUMINATION = "ILLUMINATION"
    DATA_MAGNITUDE = "MAGNITUDE"
    DATA_MESSAGE = "MESSAGE"
    DATA_NAME = "NAME" # Only used for the CITY "body" tag.
    DATA_NEW = "NEW"
    DATA_PHASE = "PHASE"
    DATA_RIGHT_ASCENSION = "RIGHT ASCENSION"
    DATA_RISE_AZIMUTH = "RISE AZIMUTH"
    DATA_RISE_TIME = "RISE TIME"
    DATA_SET_AZIMUTH = "SET AZIMUTH"
    DATA_SET_TIME = "SET TIME"
    DATA_SOLSTICE = "SOLSTICE"
    DATA_SUN_TILT = "SUN TILT"
    DATA_THIRD_QUARTER = "THIRD QUARTER"
    DATA_TROPICAL_SIGN_NAME = "TROPICAL SIGN NAME"
    DATA_TROPICAL_SIGN_DEGREE = "TROPICAL SIGN DEGREE"
    DATA_TROPICAL_SIGN_MINUTE = "TROPICAL SIGN MINUTE"
    DATA_VISIBLE = "VISIBLE"
    DATA_X_OFFSET = "X OFFSET"
    DATA_Y_OFFSET = "Y OFFSET"
    DATA_Z_OFFSET = "Z OFFSET"

    MOON_TAG = "MOON"
    SUN_TAG = "SUN"

    PLANET_MERCURY = "Mercury"
    PLANET_VENUS = "Venus"
    PLANET_MARS = "Mars"
    PLANET_JUPITER = "Jupiter"
    PLANET_SATURN = "Saturn"
    PLANET_URANUS = "Uranus"
    PLANET_NEPTUNE = "Neptune"
    PLANET_PLUTO = "Pluto"

    MOON_JUPITER_CALLISTO = "Callisto"
    MOON_JUPITER_EUROPA = "Europa"
    MOON_JUPITER_GANYMEDE = "Ganymede"
    MOON_JUPITER_IO = "Io"

    MOON_MARS_DEIMOS = "Deimos"
    MOON_MARS_PHOBOS = "Phobos"

    MOON_SATURN_DIONE = "Dione"
    MOON_SATURN_ENCELADUS = "Enceladus"
    MOON_SATURN_HYPERION = "Hyperion"
    MOON_SATURN_IAPETUS = "Iapetus"
    MOON_SATURN_MIMAS = "Mimas"
    MOON_SATURN_RHEA = "Rhea"
    MOON_SATURN_TETHYS = "Tethys"
    MOON_SATURN_TITAN = "Titan"

    MOON_URANUS_ARIEL = "Ariel"
    MOON_URANUS_MIRANDA = "Miranda"
    MOON_URANUS_OBERON = "Oberon"
    MOON_URANUS_TITANIA = "Titania"
    MOON_URANUS_UMBRIEL = "Umbriel"

    PLANET_MOONS = { 
        PLANET_JUPITER : [ MOON_JUPITER_CALLISTO, MOON_JUPITER_EUROPA, MOON_JUPITER_GANYMEDE, MOON_JUPITER_IO ],
    PLANET_MARS : [ MOON_MARS_DEIMOS, MOON_MARS_PHOBOS ],
    PLANET_SATURN : [ MOON_SATURN_DIONE, MOON_SATURN_ENCELADUS, MOON_SATURN_HYPERION, MOON_SATURN_IAPETUS, MOON_SATURN_MIMAS, MOON_SATURN_RHEA, MOON_SATURN_TETHYS, MOON_SATURN_TITAN ],
    PLANET_URANUS : [ MOON_URANUS_ARIEL, MOON_URANUS_MIRANDA, MOON_URANUS_OBERON, MOON_URANUS_TITANIA, MOON_URANUS_UMBRIEL ] }

    LUNAR_PHASE_FULL_MOON = "FULL_MOON"
    LUNAR_PHASE_WANING_GIBBOUS = "WANING_GIBBOUS"
    LUNAR_PHASE_THIRD_QUARTER = "THIRD_QUARTER"
    LUNAR_PHASE_WANING_CRESCENT = "WANING_CRESCENT"
    LUNAR_PHASE_NEW_MOON = "NEW_MOON"
    LUNAR_PHASE_WAXING_CRESCENT = "WAXING_CRESCENT"
    LUNAR_PHASE_FIRST_QUARTER = "FIRST_QUARTER"
    LUNAR_PHASE_WAXING_GIBBOUS = "WAXING_GIBBOUS"

    TROPICAL_SIGNS = [ "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces" ]

    #TODO Fix
    MESSAGE_BODY_ALWAYS_UP = "Always Up!"
    #     MESSAGE_BODY_ALWAYS_UP = _( "Always Up!" )
    MESSAGE_BODY_NEVER_UP = "Never Up!"
    #     MESSAGE_BODY_NEVER_UP = _( "Never Up!" )
    MESSAGE_DATA_NO_DATA = "No data!"
    #     MESSAGE_DATA_NO_DATA = _( "No data!" )
    MESSAGE_SATELLITE_IS_CIRCUMPOLAR = "Satellite is circumpolar."
    #     MESSAGE_SATELLITE_IS_CIRCUMPOLAR = _( "Satellite is circumpolar." )
    MESSAGE_SATELLITE_NEVER_RISES = "Satellite never rises."
    #     MESSAGE_SATELLITE_NEVER_RISES = _( "Satellite never rises." )
    MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME = "No passes within the next two days."
    #     MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME = _( "No passes within the next two days." )
    MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS = "Unable to compute next pass!"
    #     MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS = _( "Unable to compute next pass!" )
    MESSAGE_SATELLITE_VALUE_ERROR = "ValueError"
    #     MESSAGE_SATELLITE_VALUE_ERROR = _( "ValueError" )


    # Calculate astronomical information.
    #     latitude      The latitude of your location, enclosed in quotes with a leading space, such as ' -33:52:04'.
    #     longitude     The latitude of your location, enclosed in quotes with a leading space, such as ' 151:12:26'.
    #     elevation     The height, in metres, above sea leavel, such as '58'.
    #     dateTimeUTC   The date/time in UTC, enclosed in quotes in the format YYYY-MM-DD HH:MM:SS, such as '1984-05-30 16:23:45'.
    def __init__( self, latitude, longitude, elevation, dateTimeUTC ):
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.dateTimeUTC = datetime.datetime.strptime( re.sub( "\.(\d+)", "", dateTimeUTC ), "%Y-%m-%d %H:%M:%S" )
        self.data = { }


    def calculate( self ):
        self.calculateMoon()
        self.calculateSun()
# updatePlanets( ephemNow )
# updateStars( ephemNow )
# updateOrbitalElements( ephemNow, self.orbitalElementsMagnitude )
# updateSatellites( ephemNow, self.hideSatelliteIfNoVisiblePass )


    def getCalculatedData( self ): return self.data


    # http://www.ga.gov.au/geodesy/astro/moonrise.jsp
    # http://futureboy.us/fsp/moon.fsp
    # http://www.geoastro.de/moondata/index.html
    # http://www.geoastro.de/SME/index.htm
    # http://www.geoastro.de/elevazmoon/index.htm
    # http://www.geoastro.de/altazsunmoon/index.htm
    # http://www.geoastro.de/sundata/index.html
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    def calculateMoon( self ):
        observer = self.getObserver( None )
        moon = ephem.Moon( observer )
        self.updateCommon( observer, moon, AstroBodyType.Moon, Astro.MOON_TAG )

        lunarIlluminationPercentage = int( round( moon.phase ) )
        key = ( AstroBodyType.Moon, Astro.MOON_TAG )
        self.data[ key + ( Astro.DATA_PHASE, ) ] = self.getLunarPhase( lunarIlluminationPercentage )

        now = ephem.Date( self.dateTimeUTC )
        self.data[ key + ( Astro.DATA_FIRST_QUARTER, ) ] = str( ephem.next_first_quarter_moon( now ).datetime() )
        self.data[ key + ( Astro.DATA_FULL, ) ] = str( ephem.next_full_moon( now ).datetime() )
        self.data[ key + ( Astro.DATA_THIRD_QUARTER, ) ] = str( ephem.next_last_quarter_moon( now ).datetime() )
        self.data[ key + ( Astro.DATA_NEW, ) ] = str( ephem.next_new_moon( now ).datetime() )

        self.updateEclipse( AstroBodyType.Moon, Astro.MOON_TAG )


    def getLunarPhase( self, illuminationPercentage ):
        nextFullMoonDate = ephem.next_full_moon( ephem.Date( self.dateTimeUTC ) )
        nextNewMoonDate = ephem.next_new_moon( ephem.Date( self.dateTimeUTC ) )
        phase = None
        if nextFullMoonDate < nextNewMoonDate: # Between a new moon and a full moon...
            if( illuminationPercentage > 99 ):
                phase = Astro.LUNAR_PHASE_FULL_MOON
            elif illuminationPercentage <= 99 and illuminationPercentage > 50:
                phase = Astro.LUNAR_PHASE_WAXING_GIBBOUS
            elif illuminationPercentage == 50:
                phase = Astro.LUNAR_PHASE_FIRST_QUARTER
            elif illuminationPercentage < 50 and illuminationPercentage >= 1:
                phase = Astro.LUNAR_PHASE_WAXING_CRESCENT
            else: # illuminationPercentage < 1
                phase = Astro.LUNAR_PHASE_NEW_MOON
        else: # Between a full moon and the next new moon...
            if( illuminationPercentage > 99 ):
                phase = Astro.LUNAR_PHASE_FULL_MOON
            elif illuminationPercentage <= 99 and illuminationPercentage > 50:
                phase = Astro.LUNAR_PHASE_WANING_GIBBOUS
            elif illuminationPercentage == 50:
                phase = Astro.LUNAR_PHASE_THIRD_QUARTER
            elif illuminationPercentage < 50 and illuminationPercentage >= 1:
                phase = Astro.LUNAR_PHASE_WANING_CRESCENT
            else: # illuminationPercentage < 1
                phase = Astro.LUNAR_PHASE_NEW_MOON

        return phase


    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    # http://www.ga.gov.au/geodesy/astro/sunrise.jsp
    # http://www.geoastro.de/elevaz/index.htm
    # http://www.geoastro.de/SME/index.htm
    # http://www.geoastro.de/altazsunmoon/index.htm
    # http://futureboy.us/fsp/sun.fsp
    # http://www.satellite-calculations.com/Satellite/suncalc.htm
    def calculateSun( self ):
        observer = self.getObserver( None )
        sun = ephem.Sun( observer )
        self.updateCommon( observer, sun, AstroBodyType.Sun, Astro.SUN_TAG )

        key = ( AstroBodyType.Sun, Astro.SUN_TAG )
        try:
            # Dawn/Dusk.
            observer = self.getObserver( None )
            observer.horizon = '-6' # -6 = civil twilight, -12 = nautical, -18 = astronomical (http://stackoverflow.com/a/18622944/2156453)
            dawn = observer.next_rising( sun, use_center = True )
            dusk = observer.next_setting( sun, use_center = True )
            self.data[ key + ( Astro.DATA_DAWN, ) ] = str( dawn.datetime() )
            self.data[ key + ( Astro.DATA_DUSK, ) ] = str( dusk.datetime() )

        except ephem.AlwaysUpError:
            pass # No need to add a message here as update common would already have done so.

        except ephem.NeverUpError:
            pass # No need to add a message here as update common would already have done so.

        equinox = ephem.next_equinox( self.dateTimeUTC )
        solstice = ephem.next_solstice( self.dateTimeUTC )
        self.data[ key + ( Astro.DATA_EQUINOX, ) ] = str( equinox.datetime() )
        self.data[ key + ( Astro.DATA_SOLSTICE, ) ] = str( solstice.datetime() )

        self.updateEclipse( AstroBodyType.Sun, Astro.SUN_TAG )


    # http://www.geoastro.de/planets/index.html
    # http://www.ga.gov.au/earth-monitoring/astronomical-information/planet-rise-and-set-information.html
    def calculatePlanets( self ):
        for planetName in self.planets:
            planet = getattr( ephem, planetName )() # Dynamically instantiate the planet object.
            planet.compute( self.getCity( ephemNow ) )
            self.updateCommon( planet, AstronomicalObjectType.Planet, planetName.upper(), ephemNow )

            if planetName == Astro.PLANET_SATURN:
                key = ( AstronomicalObjectType.Planet, planetName.upper() )
                self.data[ key + ( Astro.DATA_EARTH_TILT, ) ] = str( round( math.degrees( planet.earth_tilt ), 1 ) )
                self.data[ key + ( Astro.DATA_SUN_TILT, ) ] = str( round( math.degrees( planet.sun_tilt ), 1 ) )

            city = self.getCity( ephemNow )
            if planetName in Astro.PLANET_MOONS:
                for moonName in Astro.PLANET_MOONS[ planetName ]:
                    moon = getattr( ephem, moonName )() # Dynamically instantiate the moon object.
                    moon.compute( city )
                    self.updateRightAscensionDeclinationAzimuthAltitude( moon, AstronomicalObjectType.PlanetaryMoon, moonName.upper() )
                    key = ( AstronomicalObjectType.PlanetaryMoon, moonName.upper() )
                    self.data[ key + ( Astro.DATA_EARTH_VISIBLE, ) ] = str( bool( moon.earth_visible ) )
                    self.data[ key + ( Astro.DATA_X_OFFSET, ) ] = str( round( moon.x, 1 ) )
                    self.data[ key + ( Astro.DATA_Y_OFFSET, ) ] = str( round( moon.y, 1 ) )
                    self.data[ key + ( Astro.DATA_Z_OFFSET, ) ] = str( round( moon.z, 1 ) )


# # http://aa.usno.navy.mil/data/docs/mrst.php
# def updateStars( ephemNow ):
#     for starName in self.stars:
#         star = ephem.star( starName )
#         star.compute( self.getCity( ephemNow ) )
#         self.updateCommon( star, AstronomicalObjectType.Star, star.name.upper(), ephemNow )
# 
# 
# # Computes the rise/set and other information for orbital elements, such as comets.
# #
# # http://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
# # http://www.minorplanetcenter.net/iau/Ephemerides/Soft03.html        
# def updateOrbitalElements( ephemNow, maximumMagnitude ):
#     for key in self.orbitalElements:
#         if key in self.orbitalElementData:
#             orbitalElement = ephem.readdb( self.orbitalElementData[ key ] )
#             orbitalElement.compute( self.getCity( ephemNow ) )
#             if float( orbitalElement.mag ) <= float( maximumMagnitude ):
#                 self.updateCommon( orbitalElement, AstronomicalObjectType.OrbitalElement, key, ephemNow )
#         else:
#             self.data[ ( AstronomicalObjectType.OrbitalElement, key, Astro.DATA_MESSAGE ) ] = Astro.MESSAGE_DATA_NO_DATA


    #Calculates the common attributes such as rise/set, illumination, constellation, magnitude, tropical sign, distance, bright limb angle and RA/Dec/Az/Alt.
    # Data tags such as RISE_TIME or MESSAGE (sometimes both) will ALWAYS be added to the data.
    def updateCommon( self, observer, body, astroBodyType, dataTag ):
        key = ( astroBodyType, dataTag )
        try:
            rising = observer.next_rising( body )
            setting = observer.next_setting( body )
            self.data[ key + ( Astro.DATA_RISE_TIME, ) ] = str( rising.datetime() )
            self.data[ key + ( Astro.DATA_SET_TIME, ) ] = str( setting.datetime() )

        except ephem.AlwaysUpError:
            self.data[ key + ( Astro.DATA_MESSAGE, ) ] = Astro.MESSAGE_BODY_ALWAYS_UP

        except ephem.NeverUpError:
            self.data[ key + ( Astro.DATA_MESSAGE, ) ] = Astro.MESSAGE_BODY_NEVER_UP

        if astroBodyType == AstroBodyType.Moon or \
           astroBodyType == AstroBodyType.Planet:
            self.data[ key + ( Astro.DATA_ILLUMINATION, ) ] = str( int( round( body.phase ) ) )

        self.data[ key + ( Astro.DATA_CONSTELLATION, ) ] = ephem.constellation( body )[ 1 ]
        self.data[ key + ( Astro.DATA_MAGNITUDE, ) ] = str( body.mag )

        if astroBodyType != AstroBodyType.OrbitalElement:
            tropicalSignName, tropicalSignDegree, tropicalSignMinute = self.getTropicalSign( body )
            self.data[ key + ( Astro.DATA_TROPICAL_SIGN_NAME, ) ] = tropicalSignName
            self.data[ key + ( Astro.DATA_TROPICAL_SIGN_DEGREE, ) ] = tropicalSignDegree
            self.data[ key + ( Astro.DATA_TROPICAL_SIGN_MINUTE, ) ] = tropicalSignMinute

        if astroBodyType == AstroBodyType.Moon:
            self.data[ key + ( Astro.DATA_DISTANCE_TO_EARTH_KM, ) ] = str( round( body.earth_distance * ephem.meters_per_au / 1000, 2 ) )

        if astroBodyType == AstroBodyType.Moon or \
           astroBodyType == AstroBodyType.OrbitalElement or \
           astroBodyType == AstroBodyType.Planet or \
           astroBodyType == AstroBodyType.Sun:
            self.data[ key + ( Astro.DATA_DISTANCE_TO_EARTH, ) ] = str( round( body.earth_distance, 4 ) )

        if astroBodyType == AstroBodyType.Moon or \
           astroBodyType == AstroBodyType.OrbitalElement or \
           astroBodyType == AstroBodyType.Planet:
            self.data[ key + ( Astro.DATA_DISTANCE_TO_SUN, ) ] = str( round( body.sun_distance, 4 ) )

        if astroBodyType == AstroBodyType.Moon or \
           astroBodyType == AstroBodyType.Planet:
            self.data[ key + ( Astro.DATA_BRIGHT_LIMB, ) ] = str( round( self.getZenithAngleOfBrightLimb( observer, body ), 1 ) )

        self.updateRightAscensionDeclinationAzimuthAltitude( body, astroBodyType, dataTag )
 

# # Uses TLE data collated by Dr T S Kelso (http://celestrak.com/NORAD/elements) with PyEphem to compute satellite rise/pass/set times.
# #
# # Other sources/background:
# #   http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
# #   http://spotthestation.nasa.gov/sightings
# #   http://www.n2yo.com
# #   http://www.heavens-above.com
# #   http://in-the-sky.org
# #
# # For planets/stars, the immediately next rise/set time is shown.
# # If already above the horizon, the set time is shown followed by the rise time for the following pass.
# # This makes sense as planets/stars are slow moving.
# #
# # However, as satellites are faster moving and pass several times a day, a different approach is used.
# # When a notification is displayed indicating a satellite is now passing overhead,
# # the user may want to see the rise/set for the current pass (rather than the set for the current pass and rise for the next pass).
# #
# # Therefore...
# #    If a satellite is yet to rise, show the upcoming rise/set time.
# #    If a satellite is currently passing over, show the rise/set time for that pass.
# #
# # This allows the user to see the rise/set time for the current pass as it is happening.
# # When the pass completes and an update occurs, the rise/set for the next pass will be displayed.
# def updateSatellites( ephemNow, hideOnNoVisiblePass ):
#     for key in self.satellites:
#         if key in self.satelliteTLEData:
#             self.calculateNextSatellitePass( ephemNow, key, self.satelliteTLEData[ key ], hideOnNoVisiblePass )
#         else:
#             self.data[ ( AstronomicalObjectType.Satellite, " ".join( key ), Astro.DATA_MESSAGE ) ] = Astro.MESSAGE_DATA_NO_DATA
# 
# 
# def calculateNextSatellitePass( ephemNow, key, satelliteTLE, hideOnNoVisiblePass ):
#     key = ( AstronomicalObjectType.Satellite, " ".join( key ) )
#     currentDateTime = ephemNow
#     endDateTime = ephem.Date( ephemNow + ephem.hour * 24 * 2 ) # Stop looking for passes 2 days from ephemNow.
#     message = None
#     while currentDateTime < endDateTime:
#         city = self.getCity( currentDateTime )
#         satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
#         satellite.compute( city )
#         try:
#             nextPass = city.next_pass( satellite )
# 
#         except ValueError:
#             if satellite.circumpolar:
#                 self.data[ key + ( Astro.DATA_MESSAGE, ) ] = Astro.MESSAGE_SATELLITE_IS_CIRCUMPOLAR
#                 self.data[ key + ( Astro.DATA_AZIMUTH, ) ] = str( satellite.az )
#                 self.data[ key + ( Astro.DATA_DECLINATION, ) ] = str( satellite.dec )
#             elif satellite.neverup:
#                 message = Astro.MESSAGE_SATELLITE_NEVER_RISES
#             else:
#                 message = Astro.MESSAGE_SATELLITE_VALUE_ERROR
# 
#             break
# 
#         if not self.isSatellitePassValid( nextPass ):
#             message = Astro.MESSAGE_SATELLITE_UNABLE_TO_COMPUTE_NEXT_PASS
#             break
# 
#         # The pass is valid.  If the satellite is currently passing, work out when it rose...
#         if nextPass[ 0 ] > nextPass[ 4 ]: # The rise time is after set time, so the satellite is currently passing.
#             setTime = nextPass[ 4 ]
#             nextPass = self.calculateSatellitePassForRisingPriorToNow( currentDateTime, satelliteTLE )
#             if nextPass is None:
#                 currentDateTime = ephem.Date( setTime + ephem.minute * 30 ) # Could not determine the rise, so look for the next pass.
#                 continue
# 
#         # Now have a satellite rise/transit/set; determine if the pass is visible (and if the user wants only visible passes).
#         passIsVisible = self.isSatellitePassVisible( satellite, nextPass[ 2 ] )
#         if hideOnNoVisiblePass and not passIsVisible:
#             currentDateTime = ephem.Date( nextPass[ 4 ] + ephem.minute * 30 )
#             continue
# 
#         # The pass is visible and the user wants only visible passes OR the user wants any pass...
#         self.data[ key + ( Astro.DATA_RISE_TIME, ) ] = str( nextPass[ 0 ].datetime() )
#         self.data[ key + ( Astro.DATA_RISE_AZIMUTH, ) ] = str( nextPass[ 1 ] )
#         self.data[ key + ( Astro.DATA_SET_TIME, ) ] = str( nextPass[ 4 ].datetime() )
#         self.data[ key + ( Astro.DATA_SET_AZIMUTH, ) ] = str( nextPass[ 5 ] )
#         self.data[ key + ( Astro.DATA_VISIBLE, ) ] = str( passIsVisible )
# 
#         break
# 
#     if currentDateTime >= endDateTime:
#         message = Astro.MESSAGE_SATELLITE_NO_PASSES_WITHIN_TIME_FRAME
# 
#     if message is not None:
#         self.data[ key + ( Astro.DATA_MESSAGE, ) ] = message
# 
# 
# def calculateSatellitePassForRisingPriorToNow( ephemNow, satelliteTLE ):
#     currentDateTime = ephem.Date( ephemNow - ephem.minute ) # Start looking from one minute ago.
#     endDateTime = ephem.Date( ephemNow - ephem.hour * 1 ) # Only look back an hour for the rise time (then just give up).
#     nextPass = None
#     while currentDateTime > endDateTime:
#         city = self.getCity( currentDateTime )
#         satellite = ephem.readtle( satelliteTLE.getName(), satelliteTLE.getTLELine1(), satelliteTLE.getTLELine2() ) # Need to fetch on each iteration as the visibility check (down below) may alter the object's internals.
#         satellite.compute( city )
#         try:
#             nextPass = city.next_pass( satellite )
#             if not self.isSatellitePassValid( nextPass ):
#                 nextPass = None
#                 break # Unlikely to happen but better to be safe and check!
# 
#             if nextPass[ 0 ] < nextPass[ 4 ]:
#                 break
# 
#             currentDateTime = ephem.Date( currentDateTime - ephem.minute )
# 
#         except:
#             nextPass = None
#             break # This should never happen as the satellite has a rise and set (is not circumpolar or never up).
# 
#     return nextPass
# 
# 
# def isSatellitePassValid( satellitePass ):
#     return \
#         satellitePass is not None and \
#         len( satellitePass ) == 6 and \
#         satellitePass[ 0 ] is not None and \
#         satellitePass[ 1 ] is not None and \
#         satellitePass[ 2 ] is not None and \
#         satellitePass[ 3 ] is not None and \
#         satellitePass[ 4 ] is not None and \
#         satellitePass[ 5 ] is not None
# 
# 
# # Determine if a satellite pass is visible or not...
# #
# #    http://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
# #    http://www.celestrak.com/columns/v03n01
# #    http://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
# def isSatellitePassVisible( satellite, passDateTime ):
#     city = self.getCity( passDateTime )
#     city.pressure = 0
#     city.horizon = "-0:34"
# 
#     satellite.compute( city )
#     sun = ephem.Sun()
#     sun.compute( city )
# 
#     return satellite.eclipsed is False and \
#            sun.alt > ephem.degrees( "-18" ) and \
#            sun.alt < ephem.degrees( "-6" )


    # Compute the right ascension, declination, azimuth and altitude for a body.
    # Right ascension is in the format of 'hours':'minutes of arc':'seconds of arc' whereas
    # declination, azimuth and altitude are in 'degrees':'minutes of arc':'seconds of arc'.
    def updateRightAscensionDeclinationAzimuthAltitude( self, body, astroBodyType, dataTag ):
        body.compute( self.getObserver( None ) ) # Need to recompute the body otherwise the azimuth/altitude are incorrectly calculated.
        key = ( astroBodyType, dataTag )
        
        self.data[ key + ( Astro.DATA_RIGHT_ASCENSION, ) ] = str( body.ra )
        self.data[ key + ( Astro.DATA_DECLINATION, ) ] = str( body.dec )
        self.data[ key + ( Astro.DATA_AZIMUTH, ) ] = str( body.az )
        self.data[ key + ( Astro.DATA_ALTITUDE, ) ] = str( body.alt )


    def updateEclipse( self, astroBodyType, dataTag ):
        if dataTag == Astro.SUN_TAG:
            eclipseInformation = eclipse.getEclipseForUTC( self.dateTimeUTC, False )
        else:
            eclipseInformation = eclipse.getEclipseForUTC( self.dateTimeUTC, True )

        if eclipseInformation is None:
            logging.error( "No eclipse information found!" )
        else:
            key = ( astroBodyType, dataTag )
            self.data[ key + ( Astro.DATA_ECLIPSE_DATE_TIME, ) ] = eclipseInformation[ 0 ]
            self.data[ key + ( Astro.DATA_ECLIPSE_TYPE, ) ] = eclipseInformation[ 1 ]
            self.data[ key + ( Astro.DATA_ECLIPSE_LATITUDE, ) ] = eclipseInformation[ 2 ] 
            self.data[ key + ( Astro.DATA_ECLIPSE_LONGITUDE, ) ] = eclipseInformation[ 3 ]


    # Code courtesy of Ignius Drake.
    def getTropicalSign( self, body ):
        ephemUTC = ephem.Date( self.dateTimeUTC )
        ( year, month, day ) = ephemUTC.triple()
        epochAdjusted = float( year ) + float( month ) / 12.0 + float( day ) / 365.242
        ephemNowDate = str( ephemUTC ).split( " " )

        bodyCopy = self.getBodyCopy( body ) # Used to workaround https://github.com/brandon-rhodes/pyephem/issues/44 until a formal release of pyephem is made.
#         bodyCopy = body.copy() # Computing the tropical sign changes the body's date/time/epoch (shared by other downstream calculations), so make a copy of the body and use that.
        bodyCopy.compute( ephemNowDate[ 0 ], epoch = str( epochAdjusted ) )
        planetCoordinates = str( ephem.Ecliptic( bodyCopy ).lon ).split( ":" )

        if float( planetCoordinates[ 2 ] ) > 30:
            planetCoordinates[ 1 ] = str( int ( planetCoordinates[ 1 ] ) + 1 )

        tropicalSignDegree = int( planetCoordinates[ 0 ] ) % 30
        tropicalSignMinute = str( planetCoordinates[ 1 ] )
        tropicalSignIndex = int( planetCoordinates[ 0 ] ) / 30
        tropicalSignName = Astro.TROPICAL_SIGNS[ int( tropicalSignIndex ) ]

        return ( tropicalSignName, str( tropicalSignDegree ), tropicalSignMinute )


    # Used to workaround https://github.com/brandon-rhodes/pyephem/issues/44 until a formal release of pyephem is made.
    def getBodyCopy( self, body ):
        bodyName = body.name
        bodyCopy = None

        if bodyName == "Sun":
            bodyCopy = ephem.Sun()
        elif bodyName == "Moon":
            bodyCopy = ephem.Moon()
        elif bodyName == "Mercury":
            bodyCopy = ephem.Mercury()
        elif bodyName == "Venus":
            bodyCopy = ephem.Venus()
        elif bodyName == "Mars":
            bodyCopy = ephem.Mars()
        elif bodyName == "Jupiter":
            bodyCopy = ephem.Jupiter()
        elif bodyName == "Saturn":
            bodyCopy = ephem.Saturn()
        elif bodyName == "Uranus":
            bodyCopy = ephem.Uranus()
        elif bodyName == "Neptune":
            bodyCopy = ephem.Neptune()
        elif bodyName == "Pluto":
            bodyCopy = ephem.Pluto()
        else: bodyCopy = ephem.star( bodyName ) # If not the sun/moon/planet, assume a star.

        return bodyCopy


    # Compute the bright limb angle (relative to zenith) between the sun and a planetary body.
    # Measured in degrees counter clockwise from a positive y axis.
    #
    # References:
    #  'Astronomical Algorithms' Second Edition by Jean Meeus (chapters 14 and 48).
    #  'Practical Astronomy with Your Calculator' by Peter Duffett-Smith (chapters 59 and 68).
    #  http://www.geoastro.de/moonlibration/ (pictures of moon are wrong but the data is correct).
    #  http://www.geoastro.de/SME/
    #  http://futureboy.us/fsp/moon.fsp
    #  http://www.timeanddate.com/moon/australia/sydney
    #
    # Other references...
    #  http://www.mat.uc.pt/~efemast/help/en/lua_fas.htm
    #  https://sites.google.com/site/astronomicalalgorithms
    #  http://stackoverflow.com/questions/13463965/pyephem-sidereal-time-gives-unexpected-result
    #  https://github.com/brandon-rhodes/pyephem/issues/24
    #  http://stackoverflow.com/questions/13314626/local-solar-time-function-from-utc-and-longitude/13425515#13425515
    #  http://astro.ukho.gov.uk/data/tn/naotn74.pdf
    def getZenithAngleOfBrightLimb( self, observer, body ):
        sun = ephem.Sun( observer )

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 14.1
        y = math.cos( sun.dec ) * math.sin( sun.ra - body.ra )
        x = math.cos( body.dec ) * math.sin( sun.dec ) - math.sin( body.dec ) * math.cos( sun.dec ) * math.cos( sun.ra - body.ra )
        positionAngleOfBrightLimb = math.atan2( y, x )

        # Astronomical Algorithms by Jean Meeus, Second Edition, Equation 48.5
        hourAngle = observer.sidereal_time() - body.ra
        y = math.sin( hourAngle )
        x = math.tan( observer.lat ) * math.cos( body.dec ) - math.sin( body.dec ) * math.cos( hourAngle )
        parallacticAngle = math.atan2( y, x )

        return math.degrees( ( positionAngleOfBrightLimb - parallacticAngle ) % ( 2.0 * math.pi ) )


    def getObserver( self, dateTimeUTC = None ):
        observer = ephem.Observer()
        observer.lat = self.latitude
        observer.lon = self.longitude
        observer.elevation = self.elevation
        if dateTimeUTC is None:
            observer.date = ephem.Date( self.dateTimeUTC )
        else:
            observer.date = ephem.Date( dateTimeUTC )

        return observer


#TODO Fix!
def writeToFile( data, Ffilename ):
    filename = Ffilename#IndicatorLunar.CACHE_PATH + baseName + datetime.datetime.now().strftime( IndicatorLunar.DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
    try:
        with open( filename, "wb" ) as f:
            pickle.dump( data, f )

    except Exception as e:
        logging.exception( e )
        logging.error( "Error writing to cache: " + filename )


# testing = True
# if testing:
#     a = Astro( "-33:52:04", "151:12:26", 58, "1984-05-30 16:23:45" )
#     a.calculate()
#     print( a.data )
# else:
#     # Must add a space to the lat/long as they could be negative.
#     # http://stackoverflow.com/questions/16174992/cant-get-argparse-to-read-quoted-string-with-dashes-in-it
#     parser = argparse.ArgumentParser( description = "Calculate astronomical information." )
#     parser.add_argument( "latitude", type = str, help = "The latitude of your location, enclosed in quotes with a leading space, such as ' -33:52:04'." )
#     parser.add_argument( "longitude", type = str, help = "The latitude of your location, enclosed in quotes with a leading space, such as ' 151:12:26'." )
#     parser.add_argument( "elevation", type = int, help = "The height, in metres, above sea leavel, such as '58'." )
#     parser.add_argument( "dateTimeUTC", type = str, help = "The date/time in UTC, enclosed in quotes in the format YYYY-MM-DD HH:MM:SS, such as '1984-05-30 16:23:45'." )
#     args = parser.parse_args()
#     
#     astro = Astro( args.latitude.strip(), args.longitude.strip(), args.elevation, args.dateTimeUTC )

#TODO Maybe the Astro class calculates and leaves it all in the data{}
#...then here we write it out using pickle?