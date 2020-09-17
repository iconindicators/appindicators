#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from enum import Enum

import calendar, datetime, ephem, math


class EclipseType( Enum ):
    CENTRAL = 0
    NONE = 1
    NOT_CENTRAL = 2
    TOTAL = 3
    ANNULAR = 4
    ANNULAR_TOTAL = 5
    PARTIAL = 6


def getMoonDatesForOneYearPyEphem( utcNow, isFullMoon, latitude, longitude, elevation ):
    city = ephem.city( "London" ) # Put in a city name known to exist in PyEphem then doctor to the correct lat/long/elev.
    city.lat = str( latitude )
    city.lon = str( longitude )
    city.elev = elevation

    moon = ephem.Moon()

    dates = [ ]
    date = utcNow
    for i in range( 12 ):
        city.date = ephem.Date( date )
        moon.compute( city )
        if isFullMoon:
            dates.append( ephem.next_full_moon( date ).datetime() )

        else:
            dates.append( ephem.next_new_moon( date ).datetime() )

        date = dates[ -1 ] + datetime.timedelta( days = 1 ) # Look for next full/new moon one starting one day later.

    return dates


def julianDayToGregorian( julianDay ):
    F, Z = math.modf( julianDay + 0.5 )
    if Z < 2299161:
        A = Z

    else:
        alpha = int( ( Z - 1867216.25 ) / 36524.25 )
        A = Z + 1 + alpha - int( alpha / 4 )

    B = A + 1524
    C = int( ( B - 122.1 ) / 365.25 )
    D = int( 365.25 * C )
    E = int( ( B - D ) / 30.6001 )

    dayOfMonth = B - D - int( 30.6001  * E ) + F

    if E < 14:
        month = E - 1

    else:
        month = E - 13

    if month > 2:
        year = C - 4716

    else:
        year = C - 4715

    return datetime.datetime( year, month, 1 ) + datetime.timedelta( days = dayOfMonth - 1 )


# Sammple implementations...not sure which is correct, if any!
# https://github.com/pavolgaj/AstroAlgorithms4Python/blob/master/eclipse.py
# https://github.com/soniakeys/meeus/blob/master/v3/eclipse/eclipse.go
# https://github.com/soniakeys/meeus/blob/master/v3/eclipse/eclipse_test.go
def getType( gamma, u ):
    if math.fabs( gamma ) < 0.9972:
        eclipseType = EclipseType.CENTRAL
        if u < 0:
            eclipseType = EclipseType.TOTAL

        elif u > 0.0047:
            eclipseType = EclipseType.ANNULAR

        else:
            if u < 0.00464 * math.sqrt( 1 - gamma * gamma ):
                eclipseType = EclipseType.ANNULAR_TOTAL

            else:
                eclipseType = EclipseType.ANNULAR

    elif math.fabs( gamma ) > 1.5433 + u:
        eclipseType = EclipseType.NONE

    else: # Not central...partial.
        eclipseType = EclipseType.NOT_CENTRAL
        if math.fabs( gamma ) > 0.9972 and math.fabs( gamma ) < 1.0260:
            pass # Not sure what to do here.

        else:
            eclipseType = EclipseType.PARTIAL

    return eclipseType


# Chapter 54 Astronomical Algorithms, Jean Meeus.
# http://www.agopax.it/Libri_astronomia/Libri_astronomia.html
def getEclipse( utcNow, isSolar, upcomingMoonDates ):
    eclipseDate = None
    date = utcNow
    moonIndex = 0
    while moonIndex <= len( upcomingMoonDates ):
        daysInYear = 365
        if calendar.isleap( date.year ):
            daysInYear = 366

        yearAsDecimal = date.year + ( date.timetuple().tm_yday / daysInYear )
        k = ( yearAsDecimal - 2000 ) * 12.3685 # Equation 49.2
        k = round( k ) # Must be an integer for a New Moon (solar eclipse).
        if not isSolar:
            k += 0.5 # Must be an integer increased by 0.5 for a Full Moon (lunar eclipse).

        T =  k / 1236.85 # Equation 49.3

        JDE =   2451550.09766 \
              + 29.530588861 * k \
              + 0.00015437 * T * T \
              - 0.000000150 * T * T * T \
              + 0.00000000073 * T * T * T * T # Equation 49.1

        E = 1 - 0.002516 * T - 0.0000074 * T * T # Equation 47.6

        M = (  2.5534 \
             + 29.10536570 * k \
             - 0.0000014 * T * T \
             - 0.00000011 * T * T * T ) % 360 # Equation 49.4

        Mdash = (  201.5634 \
                 + 385.81693528 * k \
                 + 0.0107582 * T * T \
                 + 0.00001238 * T * T * T \
                 - 0.000000058 * T * T * T * T ) % 360 # Equation 49.5

        F = (  160.7108 \
             + 390.67050284 * k \
             - 0.0016118 * T * T \
             - 0.000000227 * T * T * T \
             + 0.000000011 * T * T * T * T ) % 360 # Equation 49.6

        noEclipse = math.fabs( math.sin( math.radians( F ) ) ) > 0.36
        if noEclipse:
            date = upcomingMoonDates[ moonIndex ] #TODO Maybe add one day?
            moonIndex += 1
            continue

        omega = (  124.7746 \
                 - 1.56375588 * k \
                 + 0.0020672 * T * T \
                 + 0.00000215 * T * T * T ) % 360 # Equation 49.7

        F1 = F - 0.02665 * math.sin( math.radians( omega ) )

        A1 = 299.77 + 0.107408 * k - 0.009173 * T * T

        # Equation 54.1
        if isSolar:
            correctedJDE = JDE \
                           - 0.4075 * math.sin( math.radians( Mdash ) ) \
                           + 0.1721 * E * math.sin( math.radians( M ) )

        else:
            correctedJDE = JDE \
                           - 0.4065 * math.sin( math.radians( Mdash ) ) \
                           + 0.1727 * E * math.sin( math.radians( M ) )

        correctedJDE +=   0.0161 * math.sin( math.radians( 2 * Mdash ) ) \
                        - 0.0097 * math.sin( math.radians( 2 * F1 ) ) \
                        + 0.0073 * E * math.sin( math.radians( Mdash - M ) ) \
                        - 0.0050 * E * math.sin( math.radians( Mdash + M ) ) \
                        - 0.0023 * math.sin( math.radians( Mdash - 2 * F1 ) ) \
                        + 0.0021 * E * math.sin( math.radians( 2 * M ) ) \
                        + 0.0012 * math.sin( math.radians( Mdash + 2 * F1 ) ) \
                        + 0.0006 * E * math.sin( math.radians( 2 * Mdash + M ) ) \
                        - 0.0004 * math.sin( math.radians( 3 * Mdash ) ) \
                        - 0.0003 * E * math.sin( math.radians( M + 2 * F1 ) ) \
                        + 0.0003 * math.sin( math.radians( A1 ) ) \
                        - 0.0002 * E * math.sin( math.radians( M - 2 * F1 ) ) \
                        - 0.0002 * E * math.sin( math.radians( 2 * Mdash - M ) ) \
                        - 0.0002 * math.sin( math.radians( omega ) )

        eclipseDate = julianDayToGregorian( correctedJDE )

        P =   0.2070 * E * math.sin( math.radians( M ) ) \
            + 0.0024 * E * math.sin( math.radians( 2 * M ) ) \
            - 0.0392 * math.sin( math.radians( Mdash ) ) \
            + 0.0116 * math.sin( math.radians( 2 * Mdash ) ) \
            - 0.0073 * E * math.sin( math.radians( Mdash + M ) ) \
            + 0.0067 * E * math.sin( math.radians( Mdash - M ) ) \
            + 0.0118 * math.sin( math.radians( 2 * F1 ) )

        Q =   5.2207 \
            - 0.0048 * E * math.cos( math.radians( M ) ) \
            + 0.0020 * E * math.cos( math.radians( 2 * M ) ) \
            - 0.3299 * math.cos( math.radians( Mdash ) ) \
            - 0.0060 * E * math.cos( math.radians( Mdash + M ) ) \
            + 0.0041 * E * math.cos( math.radians( Mdash - M ) )

        W = math.fabs( math.cos( math.radians( F1 ) ) )

        gamma = ( P * math.cos( math.radians( F1 ) ) + Q * math.sin( math.radians( F1 ) ) ) * ( 1 - 0.0048 * W )
        
        u =   0.0059 \
            + 0.0046 * E * math.cos( math.radians( M ) ) \
            - 0.0182 * math.cos( math.radians( Mdash ) ) \
            + 0.0004 * math.cos( math.radians( 2 * Mdash ) ) \
            - 0.0005 * math.cos( math.radians( M + Mdash ) )

        eclipseType = getType( gamma, u )

        break

    return eclipseDate, eclipseType


latitude = -33
longitude = 151
elevation = 0

# now = datetime.datetime.strptime( "1997-07-01", "%Y-%m-%d" )
now = datetime.datetime.utcnow()
fullMoonDates = getMoonDatesForOneYearPyEphem( now, True, latitude, longitude, elevation )
newMoonDates = getMoonDatesForOneYearPyEphem( now, False, latitude, longitude, elevation )

print( "Meeus solar eclipse:", getEclipse( now, True, newMoonDates ) )
print( "Meeus lunar eclipse:", getEclipse( now, False, fullMoonDates ) )