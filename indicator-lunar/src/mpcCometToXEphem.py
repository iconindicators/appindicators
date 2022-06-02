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


# Convert comet data in MPC format to XEphem format.
# Inspired by https://github.com/XEphem/XEphem/blob/main/GUI/xephem/tools/mpccomet2edb.pl
#
# MPC format: 
#    https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
#
# XEphem format:
#    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501


import sys


def processAndWriteOneLine( line, outputFile ):
    if len( line.strip() ) > 0:
        name = line[ 103 - 1 : 158 ].replace( '(', '' ).replace( ')', '' ).strip()
        absoluteMagnitude = line[ 92 - 1 : 95 ].strip()

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
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

            outputFile.write( ','.join( components ) + '\n' )


if len( sys.argv ) != 2:
    message = \
        "Usage: python3 MPCCometToXEphem.py fileToConvert" + \
        "\n\nFor example:" + \
        "\n  python3 MPCCometToXEphem.py CometEls.txt"

    raise SystemExit( message )

inFile = sys.argv[ 1 ]
outFile = inFile[ 0 : -3 ] + "edb"
with open( inFile, 'r' ) as fIn, open( outFile, 'w' ) as fOut:
    for line in fIn:
        processAndWriteOneLine( line, fOut )