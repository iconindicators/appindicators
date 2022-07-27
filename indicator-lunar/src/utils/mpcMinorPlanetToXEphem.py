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


# Convert minor planet data in MPC format to XEphem format.
#
# Inspired by:
#    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/auxil/mpcorb2edb.pl
#
# MPC format: 
#    https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
#
# XEphem format:
#    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501


from pathlib import Path

import gzip, sys


centuryMap = {
    'I': 1800,
    'J': 1900,
    'K': 2000 }


# https://www.minorplanetcenter.net/iau/info/PackedDates.html
def getUnpackedDate( i ): return str( i ) if i.isdigit() else str( ord( i ) - ord( 'A' ) + 10 )


def processAndWriteOneLine( line, outputFile ):
    if len( line.strip() ) > 0:
        # Field numbers: 0   1   2   3   4   5   6   7   8   9   10   11   12   13   14   15   16   17   18   19   20   21   22
        startIndices = [ 1,  9, 15, 21, 27, 38, 49, 60, 71, 81,  93, 106, 108, 118, 124, 128, 138, 143, 147, 151, 162, 167, 195 ]
        endIndices =   [ 7, 13, 19, 25, 35, 46, 57, 68, 79, 91, 103, 106, 116, 122, 126, 136, 141, 145, 149, 160, 165, 194, 202 ]

        # Offset back to zero to match lines read into a string.
        startIndices = [ x - 1 for x in startIndices ]
        endIndices = [ x - 1 for x in endIndices ]

        fields = [ line[ i : j + 1 ] for i, j in zip( startIndices, endIndices ) ] # Inspired by https://stackoverflow.com/a/10851479/2156453
        name = fields[ 21 ].replace( '(', '' ).replace( ')', '' ).strip()
        absoluteMagnitude = fields[ 1 ].strip()

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            slopeParameter = fields[ 2 ].strip()

            epochPacked = fields[ 3 ].strip()
            century = epochPacked[ 0 ]
            lastTwoDigitsOfYear = epochPacked[ 1 : 3 ]
            year = str( centuryMap[ century ] + int( lastTwoDigitsOfYear ) )
            month = getUnpackedDate( epochPacked[ 3 ] )
            day = getUnpackedDate( epochPacked[ 4 ] )
            epochDate = month + '/' + day + '/' + year

            meanAnomalyEpoch = fields[ 4 ].strip()
            argumentPerihelion = fields[ 5 ].strip()
            longitudeAscendingNode = fields[ 6 ].strip()
            inclinationToEcliptic = fields[ 7 ].strip()
            orbitalEccentricity = fields[ 8 ].strip()
            semimajorAxis = fields[ 10 ].strip()

            components = [
                name,
                'e',
                inclinationToEcliptic,
                longitudeAscendingNode,
                argumentPerihelion,
                semimajorAxis,
                '0',
                orbitalEccentricity,
                meanAnomalyEpoch,
                epochDate,
                "2000.0",
                absoluteMagnitude,
                slopeParameter ]

            outputFile.write( ','.join( components ) + '\n' )


def convert( inFile, hasHeader, outFile ):
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )

    else:
        fIn = open( inFile, 'r' )

    fOut = open( outFile, 'w' )

    if hasHeader:
        endOfHeader = False
        for line in fIn:
            if endOfHeader:
                processAndWriteOneLine( line, fOut )
    
            elif line.startswith( "----------" ):
                endOfHeader = True

    else:
        for line in fIn:
            processAndWriteOneLine( line, fOut )

    fIn.close()
    fOut.close()


if __name__ == "__main__":
    if len( sys.argv ) != 4:
        message = \
            "Usage:" + \
            "\n python3 " + Path(__file__).name + " fileToConvert header=TRUE outputFile" + \
            "\n python3 " + Path(__file__).name + " fileToConvert header=FALSE outputFile" + \
            "\n\nFor example:" + \
            "\n  python3  " + Path(__file__).name + " MPCORB.DAT header=TRUE mpcorb.edb" + \
            "\n  python3  " + Path(__file__).name + " MPCORB.DAT.gz header=TRUE mpcorb.edb" + \
            "\n  python3  " + Path(__file__).name + " NEA.txt header=FALSE NEA.edb" + \
            "\n  python3  " + Path(__file__).name + " PHA.txt header=FALSE PHA.edb" + \
            "\n  python3  " + Path(__file__).name + " DAILY.DAT header=FALSE DAILY.edb" + \
            "\n  python3  " + Path(__file__).name + " Distant.txt header=FALSE Distant.edb" + \
            "\n  python3  " + Path(__file__).name + " Unusual.txt header=FALSE Unusual.edb"

        raise SystemExit( message )
    convert( sys.argv[ 1 ], True if sys.argv[ 2 ].casefold() == "header=TRUE".casefold() else False, sys.argv[ 3 ] )