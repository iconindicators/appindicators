#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import calendar, datetime, ephem, math


def getMoonDatesForOneYearPyEphem( utcNow, isFull, latitude, longitude, elevation ):
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
        if isFull:
            dates.append( ephem.next_full_moon( date ).datetime() )

        else:
            dates.append( ephem.next_new_moon( date ).datetime() )

        date = dates[ -1 ] + datetime.timedelta( days = 1 ) # Look for next full/new moon one starting one day later.

    return dates


def normaliseDegrees( degrees ): return ( degrees % 360 )


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

    return


def getEclipseMeeus( utcNow, isSolar, upcomingMoonDates ):
    foundEclipse = False
    date = utcNow
    moonIndex = 0
    while not foundEclipse: #TODO Better loop over the upcoming moon dates instead.
        daysInYear = 365
#TODO Be careful here...if we are toward the end of the year and the next eclipse will be in the following year, may need to adjust the days.
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

        M =   2.5534 \
            + 29.10536570 * k \
            - 0.0000014 * T * T \
            - 0.00000011 * T * T * T # Equation 49.4

        M = normaliseDegrees( M )

        Mdash =   201.5634 \
                + 385.81693528 * k \
                + 0.0107582 * T * T \
                + 0.00001238 * T * T * T \
                - 0.000000058 * T * T * T * T # Equation 49.5

        Mdash = normaliseDegrees( Mdash )

        F =   160.7108 \
            + 390.67050284 * k \
            - 0.0016118 * T * T \
            - 0.000000227 * T * T * T \
            + 0.000000011 * T * T * T * T # Equation 49.6

        F = normaliseDegrees( F )

        noEclipse = math.fabs( math.sin( math.radians( F ) ) ) > 0.36
        if noEclipse:
            date = upcomingMoonDates[ moonIndex ]
            moonIndex += 1
            continue

        omega =   124.7746 \
                - 1.56375588 * k \
                + 0.0020672 * T * T \
                + 0.00000215 * T * T * T # Equation 49.7

        omega = normaliseDegrees( omega )

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

        x = julianDayToGregorian( correctedJDE )

        x = 1
        x+=1

    return


def getEclipseMeeusORIGINAL( utcNow, isSolar, upcomingMoonDates ):
    daysInYear = 365
#TODO Be careful here...if we are toward the end of the year and the next eclipse will be in the following year, may need to adjust the days.
    if calendar.isleap( utcNow.year ):
        daysInYear = 366

    yearAsDecimal = utcNow.year + ( utcNow.timetuple().tm_yday / daysInYear )
    k = ( yearAsDecimal - 2000 ) * 12.3685 # Equation 49.2
    k = round( k ) # Must be an integer for a New Moon (solar eclipse).
    if not isSolar:
        k += 0.5 # Must be an integer increased by 0.5 for a Full Moon (lunar eclipse).

    T =  k /1236.85 # Equation 49.3
    JDE = 2451550.09766 + \
          29.530588861 * k + \
          0.00015437 * T * T - \
          0.000000150 * T * T * T + \
          0.00000000073 * T * T * T * T # Equation 49.1

    E = 1 - 0.002516 * T - 0.0000074 * T * T # Equation 47.6
    M = 2.5534 + \
        29.10536570 * k - \
        0.0000014 * T * T - \
        0.00000011 * T * T * T # Equation 49.4

    M = normaliseDegrees( M )

    Mdash = 201.5634 + \
            385.81693528 * k + \
            0.0107582 * T * T + \
            0.00001238 * T * T * T - \
            0.000000058 * T * T * T * T # Equation 49.5

    Mdash = normaliseDegrees( Mdash )

    F = 160.7108 + \
        390.67050284 * k - \
        0.0016118 * T * T - \
        0.000000227 * T * T * T + \
        0.000000011 * T * T * T * T # Equation 49.6

    F = normaliseDegrees( F )

    noEclipse = math.fabs( math.sin( math.radians( F ) ) ) > 0.36

    omega = 124.7746 - \
            1.56375588 * k + \
            0.0020672 * T * T + \
            0.00000215 * T * T * T # Equation 49.7

    omega = normaliseDegrees( omega )

    F1 = F - 0.02665 * math.sin( math.radians( omega ) )

    A1 = 299.77 + 0.107408 * k - 0.009173 * T * T

    return


latitude = -33
longitude = 151
elevation = 0

utcNow = datetime.datetime.strptime( "1997-07-01", "%Y-%m-%d" )
fullMoonDates = getMoonDatesForOneYearPyEphem( utcNow, True, latitude, longitude, elevation )
newMoonDates = getMoonDatesForOneYearPyEphem( utcNow, False, latitude, longitude, elevation )


getEclipseMeeus( utcNow, False, fullMoonDates )
# getEclipseMeeus( datetime.datetime.strptime( "1993-05-21", "%Y-%m-%d" ), True )
# getEclipseMeeus( datetime.datetime.utcnow(), True )