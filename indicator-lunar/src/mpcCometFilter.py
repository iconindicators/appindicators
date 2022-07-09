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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Read in Minor Planet's CometEls.txt and for each body, compute the apparent magnitude over a period using PyEphem.
# If a body's apparent magnitude is less than the maximum specified at any point, keep the body.
#
# The CometEls.txt data which is in MPC format, must first be converted to XEphem format.
# Refer to https://github.com/XEphem/XEphem/blob/main/GUI/xephem/tools/mpccomet2edb.pl
#
# MPC format: 
#    https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
#
# XEphem format:
#    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501


import datetime, ephem


def mpcToXEphem( line ):
    xEphemLine = ""
    name = line[ 103 - 1 : 158 ].replace( '(', '' ).replace( ')', '' ).strip()
    absoluteMagnitude = line[ 92 - 1 : 95 ].strip()
    inclination = line[ 72 - 1 : 79 ].strip()
    longitudeAscendingNode = line[ 62 - 1 : 69 ].strip()
    argumentPerihelion = line[ 52 - 1 : 59 ].strip()
    perihelionDistance = line[ 31 - 1 : 39 ].strip()
    orbitalEccentricity = line[ 42 - 1 : 49 ].strip()

    month = line[ 20 - 1 : 21 ].strip()
    day = line[ 23 - 1 : 29 ].strip()
    year = line[ 15 - 1 : 18 ].strip()
    epochDate = month + '/' + day + '/' + year

    slopeParameter = line[ 97 - 1 : 100 ].strip()

    if float( orbitalEccentricity ) < 0.99:
        meanAnomaly = str( 0.0 )
        meanDistance = str( float( perihelionDistance ) / ( 1.0 - float( orbitalEccentricity ) ) )

        components = [
            name, 'e', inclination, longitudeAscendingNode, argumentPerihelion,
            meanDistance, '0', orbitalEccentricity, meanAnomaly,
            epochDate, "2000.0",
            slopeParameter, absoluteMagnitude ]

    elif float( orbitalEccentricity ) > 1.0:
        components = [
            name, 'h', epochDate, inclination,
            longitudeAscendingNode, argumentPerihelion, orbitalEccentricity, 
            perihelionDistance, "2000.0",
            slopeParameter, absoluteMagnitude ]

    else:
        components = [
            name, 'p', epochDate, inclination,
            argumentPerihelion, perihelionDistance, longitudeAscendingNode, 
            "2000.0", slopeParameter, absoluteMagnitude ]

    xEphemLine = ','.join( components )

    return xEphemLine


def getApparentMagnitudeOverPeriod( orbitalElement, startDate, endDate, city, apparentMagnitudeMaximum, intervalInDaysBetweenBodyCompute ):
    currentDate = startDate
    body = ephem.readdb( orbitalElement )
    while currentDate < endDate:
        city.date = currentDate
        body.compute( city )
        if body.mag <= apparentMagnitudeMaximum:
            break

        currentDate += datetime.timedelta( days = intervalInDaysBetweenBodyCompute )

    return body.mag


# The parameters below take approximately 5 minutes to yield 1200 filtered bodies (as of 2022).
apparentMagnitudeMaximum = 15.0 # Upper limit for apparent magnitude.
durationInYears = 1 # Number of years over which to compute apparent magnitude.
intervalInDaysBetweenBodyCompute = 30

inFile = "CometEls.txt"
outFile = inFile[ 0 : -4 ] + "-FILTERED-BY-APPARENT-MAGNITUDE-" + str( int( apparentMagnitudeMaximum ) ) + ".txt"
startDate = datetime.datetime.utcnow()
endDate = startDate + datetime.timedelta( days = 366 * durationInYears )
with open( inFile, 'r' ) as fIn, open( outFile, 'w' ) as fOut:
    city = ephem.city( "London" ) # Use any city; makes no difference to obtain the apparent magnitude.
    for line in fIn:
        if len( line.strip() ) == 0:
            continue

        name = line[ 103 - 1 : 158 ].replace( '(', '' ).replace( ')', '' ).strip()
        if len( name ) == 0:
            print( "Missing name:\n" + line )
            continue

        absoluteMagnitude = line[ 92 - 1 : 95 ].strip()
        if len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )
            continue

        apparentMagnitude = getApparentMagnitudeOverPeriod( mpcToXEphem( line ), startDate, endDate, city, apparentMagnitudeMaximum, intervalInDaysBetweenBodyCompute )
        if apparentMagnitude < apparentMagnitudeMaximum:
            fOut.write( line )