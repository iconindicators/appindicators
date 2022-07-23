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
#
# Inspired by:
#    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/tools/mpccomet2edb.pl
#
# MPC format: 
#    https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
#
# XEphem format:
#    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501


from pathlib import Path

import sys


def processAndWriteOneLine( line, outFile ):
    if len( line.strip() ) > 0:
        # Field numbers: 0  1   2   3   4   5   6   7   8   9  10  11  12  13  14   15   16   17
        startIndices = [ 1, 5,  6, 15, 20, 23, 31, 42, 52, 62, 72, 82, 86, 88, 92,  97, 103, 160 ]
        endIndices =   [ 4, 5, 12, 18, 21, 29, 39, 49, 59, 69, 79, 85, 87, 89, 95, 100, 158, 168 ]

        # Offset back to zero to match lines read into a string.
        startIndices = [ x - 1 for x in startIndices ]
        endIndices = [ x - 1 for x in endIndices ]

        fields = [ line[ i : j + 1 ] for i, j in zip( startIndices, endIndices ) ] # Inspired by https://stackoverflow.com/a/10851479/2156453
        name = fields[ 16 ].replace( '(', '' ).replace( ')', '' ).strip()
        absoluteMagnitude = fields[ 14 ].strip()

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            year = fields[ 3 ].strip()
            month = fields[ 4 ].strip()
            day = fields[ 5 ].strip()
            epochDate = month + '/' + day + '/' + year

            perihelionDistance = fields[ 6 ].strip()
            orbitalEccentricity = fields[ 7 ].strip()
            argumentPerihelion = fields[ 8 ].strip()
            longitudeAscendingNode = fields[ 9 ].strip()
            inclination = fields[ 10 ].strip()
            slopeParameter = fields[ 15 ].strip()

            if float( orbitalEccentricity ) < 0.99: # Elliptical orbit.
                meanAnomaly = str( 0.0 )
                meanDistance = str( float( perihelionDistance ) / ( 1.0 - float( orbitalEccentricity ) ) )

                components = [
                    name,
                    'e',
                    inclination,
                    longitudeAscendingNode,
                    argumentPerihelion,
                    meanDistance,
                    '0',
                    orbitalEccentricity,
                    meanAnomaly,
                    epochDate,
                    "2000.0",
                    absoluteMagnitude,
                    slopeParameter ]

            elif float( orbitalEccentricity ) > 1.0: # Hyperbolic orbit.
                components = [
                    name,
                    'h',
                    epochDate,
                    inclination,
                    longitudeAscendingNode,
                    argumentPerihelion,
                    orbitalEccentricity, 
                    perihelionDistance,
                    "2000.0",
                    absoluteMagnitude,
                    slopeParameter ]

            else: # Parabolic orbit.
                components = [
                    name,
                    'p',
                    epochDate,
                    inclination,
                    argumentPerihelion,
                    perihelionDistance,
                    longitudeAscendingNode,
                    "2000.0",
                    absoluteMagnitude,
                    slopeParameter ]

            outFile.write( ','.join( components ) + '\n' )


def convert( inFile, outFile ):
    fIn = open( inFile, 'r' )
    fOut = open( outFile, 'w' )
    for line in fIn:
        processAndWriteOneLine( line, fOut )

    fIn.close()
    fOut.close()


if __name__ == "__main__":
    if len( sys.argv ) != 3:
        message = \
            "Usage: python3 " + Path(__file__).name + " fileToConvert outputFile" + \
            "\n\nFor example:" + \
            "\n  python3  " + Path(__file__).name + " CometEls.txt CometEls.edb"

        raise SystemExit( message )

    convert( sys.argv[ 1 ], sys.argv[ 2 ] )