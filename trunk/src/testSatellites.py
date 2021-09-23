#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Download and save to same directory as script:
#    https://celestrak.com/NORAD/elements/visual.txt


from skyfield.api import load, wgs84
from skyfield import almanac
import datetime, math


def findVisiblePassUsingCulminate( now, nowPlusSearchDuration, location, ephemerisPlanets, satellite ): 
    riseTime, riseAz, setTime, setAz = None, None, None, None
    culminateTimes = [ ] # Culminate may occur more than once, so collect them all.
    t, events = satellite.find_events( location, now, nowPlusSearchDuration, altitude_degrees = 30.0 )
    for ti, event in zip( t, events ):
        if event == 0: # Rise
            riseTime = ti

        elif event == 1: # Culminate
            culminateTimes.append( ti )

        else: # Set
            if riseTime is not None and culminateTimes:
                for culmination in culminateTimes:
                    isTwilight = isTwilightFunction( culmination ) == 1 or isTwilightFunction( culmination ) == 2 # 1 = Astronomical, 2 = Nautical
                    if isTwilight and satellite.at( culmination ).is_sunlit( ephemerisPlanets ):
                        alt, riseAz, distance = ( satellite - location ).at( riseTime ).altaz()
                        setTime = ti
                        alt, setAz, distance = ( satellite - location ).at( ti ).altaz()
                        break

            if setTime is not None:
                break

            riseTime = None
            culminateTimes = [ ]

    return riseTime, riseAz, setTime, setAz # If a visible pass is found, setTime is not None; otherwise setTime is None.


def findVisiblePassSteppingBetweenRiseAndSet( now, nowPlusSearchDuration, location, ephemerisPlanets, satellite ): 
    riseTime, riseAz, setTime, setAz = None, None, None, None
    culminateTimes = [ ] # Culminate may occur more than once, so collect them all.
    t, events = satellite.find_events( location, now, nowPlusSearchDuration, altitude_degrees = 30.0 )
    for ti, event in zip( t, events ):
        if event == 0: # Rise
            riseTime = ti

        elif event == 1: # Culminate
            culminateTimes.append( ti )

        else: # Set
            if riseTime is not None and culminateTimes:
                totalSeconds = ( ti.utc_datetime() - riseTime.utc_datetime() ).total_seconds()
                step = 1.0 if ( totalSeconds / 10.0 ) < 1.0 else ( totalSeconds / 10.0 )
                timeRange = timeScale.utc( 
                    riseTime.utc.year, 
                    riseTime.utc.month, 
                    riseTime.utc.day, 
                    riseTime.utc.hour, 
                    riseTime.utc.minute, 
                    range( math.ceil( riseTime.utc.second ), math.ceil( totalSeconds + riseTime.utc.second ), math.ceil( step ) ) )

                isTwilightAstronomical = isTwilightFunction( timeRange ) == 1
                isTwilightNautical = isTwilightFunction( timeRange ) == 2
                sunlit = satellite.at( timeRange ).is_sunlit( ephemerisPlanets )
                for twilightAstronomical, twilightNautical, isSunlit in zip( isTwilightAstronomical, isTwilightNautical, sunlit ):
                    if isSunlit and ( twilightAstronomical or twilightNautical ):
                        alt, riseAz, distance = ( satellite - location ).at( riseTime ).altaz()
                        setTime = ti
                        alt, setAz, distance = ( satellite - location ).at( ti ).altaz()
                        break

            if setTime is not None:
                break

            riseTime = None

    return riseTime, riseAz, setTime, setAz # If a visible pass is found, setTime is not None; otherwise setTime is None.


def toDateTimeLocal( utcDateTime ): return utcDateTime.replace( tzinfo = datetime.timezone.utc ).astimezone( tz = None )


def toDegrees( angleInRadians ): return str( round( math.degrees( float( angleInRadians ) ) ) ) + "°"


lat = -33
lon = 151
elev = 100
searchDuration = 48 # Hours
tleData = "file:///./visual.txt"
ephemerisPlanets = load( "de421.bsp" )

utcNow = datetime.datetime.utcnow()
timeScale = load.timescale( builtin = True )
now = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
nowPlusSearchDuration = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour + searchDuration, utcNow.second )
location = wgs84.latlon( lat, lon, elev )
isTwilightFunction = almanac.dark_twilight_day( ephemerisPlanets, location )

for satellite in load.tle_file( tleData ):
    riseTime, riseAz, setTime, setAz = findVisiblePassUsingCulminate( now, nowPlusSearchDuration, location, ephemerisPlanets, satellite )
    if setTime is not None:
        print( satellite.name + ":" + str( satellite.model.satnum ) + ":" + str( satellite.model.intldesg ) ) 
        print( '\t', toDateTimeLocal( riseTime.utc_datetime() ), '\t', toDegrees( riseAz.radians ) ) 
        print( '\t', toDateTimeLocal( setTime.utc_datetime() ), '\t', toDegrees( setAz.radians ) )

for satellite in load.tle_file( tleData ):
    riseTime, riseAz, setTime, setAz = findVisiblePassSteppingBetweenRiseAndSet( now, nowPlusSearchDuration, location, ephemerisPlanets, satellite )
    if setTime is not None:
        print( satellite.name + ":" + str( satellite.model.satnum ) + ":" + str( satellite.model.intldesg ) ) 
        print( '\t', toDateTimeLocal( riseTime.utc_datetime() ), '\t', toDegrees( riseAz.radians ) ) 
        print( '\t', toDateTimeLocal( setTime.utc_datetime() ), '\t', toDegrees( setAz.radians ) )