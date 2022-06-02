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


# Read in MPCORB.DAT and for each body, compute the apparent magnitude over a period using PyEphem.
# If a body's apparent magnitude is less than the maximum specified at any point, keep the body.
#
# The MCPORB.DAT data which is in MPC format, must first be converted to XEphem format.
# Refer to https://github.com/XEphem/XEphem/blob/main/GUI/xephem/tools/mpccomet2edb.pl
#
# MPC format: 
#    https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
#
# XEphem format:
#    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501


import datetime, ephem


# https://www.minorplanetcenter.net/iau/info/PackedDates.html
centuryMap = { 'I': 1800, 'J': 1900, 'K': 2000 }


# https://www.minorplanetcenter.net/iau/info/PackedDates.html
def getUnpackedDate( i ): return str( i ) if i.isdigit() else str( ord( i ) - ord( 'A' ) + 10 )


def mpcToXEphem( line ):
    xEphemLine = ""
    name = line[ 167 - 1 : 194 ].replace( '(', '' ).replace( ')', '' ).strip()
    absoluteMagnitude = line[ 9 - 1 : 13 ].strip()
    inclinationToEcliptic = line[ 60 - 1 : 68 ].strip()
    longitudeAscendingNode = line[ 49 - 1 : 57 ].strip()
    argumentPerihelion = line[ 38 - 1 : 46 ].strip()
    semimajorAxix = line[ 93 - 1 : 103 ].strip()
    orbitalEccentricity = line[ 71 - 1 : 79 ].strip()
    meanAnomalyEpoch = line[ 27 - 1 : 35 ].strip()
    slopeParamenter = line[ 15 - 1 : 19 ].strip()

    century = line[ 21 - 1 : 21 ].strip()
    lastTwoDigitsOfYear = line[ 22 - 1 : 23 ].strip()
    year = str( centuryMap[ century ] + int( lastTwoDigitsOfYear ) )
    month = getUnpackedDate( line[ 24 - 1 : 24 ].strip() )
    day = getUnpackedDate( line[ 25 - 1 : 25 ].strip() )
    epochDate = month + '/' + day + '/' + year

    xEphemLine = [
        name, 'e', inclinationToEcliptic, longitudeAscendingNode,
        argumentPerihelion, semimajorAxix, '0', orbitalEccentricity,
        meanAnomalyEpoch, epochDate, "2000.0", absoluteMagnitude, slopeParamenter ]

    xEphemLine = ','.join( xEphemLine )

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

inFile = "MPCORB.DAT"
outFile = inFile[ 0 : -4 ] + "-FILTERED-BY-APPARENT-MAGNITUDE-" + str( int( apparentMagnitudeMaximum ) ) + ".DAT"
startDate = datetime.datetime.utcnow()
endDate = startDate + datetime.timedelta( days = 366 * durationInYears )
with open( inFile, 'r' ) as fIn, open( outFile, 'w' ) as fOut:
    city = ephem.city( "London" ) # Use any city; makes no difference to obtain the apparent magnitude.
    header = ""
    endOfHeader = False
    for line in fIn:
        if endOfHeader:
            if len( line.strip() ) == 0:
                continue

            name = line[ 167 - 1 : 194 ].replace( '(', '' ).replace( ')', '' ).strip()
            if len( name ) == 0:
                print( "Missing name:\n" + line )
                continue

            absoluteMagnitude = line[ 9 - 1 : 13 ].strip()
            if len( absoluteMagnitude ) == 0:
                print( "Missing absolute magnitude:\n" + line )
                continue

            apparentMagnitude = getApparentMagnitudeOverPeriod( mpcToXEphem( line ), startDate, endDate, city, apparentMagnitudeMaximum, intervalInDaysBetweenBodyCompute )
            if apparentMagnitude < apparentMagnitudeMaximum:
                fOut.write( line )

        else:
            header += line
            if line.startswith( "----------" ):
                endOfHeader = True
                fOut.write( header )