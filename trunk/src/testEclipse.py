#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import calendar, datetime


def normaliseDegrees( degrees ): return ( degrees % 360 )


def getEclipseLunarMeeus( utcNow ):
    daysInYear = 365
    if calendar.isleap( utcNow.year ):
        daysInYear = 366

    yearAsDecimal = utcNow.year + ( utcNow.timetuple().tm_yday / daysInYear )
    yearAsDecimal = 1977.13 #TODO Test
    k = ( yearAsDecimal - 2000 ) * 12.3685 # Equation 49.2 
    T =  k /1236.85 # Equation 49.3
    julianEphemerisDays = 2451550.09766 + \
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

    Mprime = 201.5634 + \
             385.81693528 * k + \
             0.0107582 * T * T + \
             0.00001238 * T * T * T - \
             0.000000058 * T * T * T * T # Equation 49.5

    Mprime = normaliseDegrees( Mprime )

    F = 160.7108 + \
        390.67050284 * k - \
        0.0016118 * T * T - \
        0.000000227 * T * T * T + \
        0.000000011 * T * T * T * T # Equation 49.6

    F = normaliseDegrees( F )

    Omega = 124.7746 - \
            1.56375588 * k + \
            0.0020672 * T * T + \
            0.00000215 * T * T * T # Equation 49.7

    Omega = normaliseDegrees( Omega )

    return


getEclipseLunarMeeus( datetime.datetime.utcnow() )