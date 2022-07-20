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


# Convert minor planet data in Lowell format to XEphem format.
#
# Inspired by:
#    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/auxil/astorb2edb.pl
#
# Lowell format: 
#    https://asteroid.lowell.edu/main/astorb/
#
# XEphem format:
#    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501


from pathlib import Path

import gzip, sys


def processAndWriteOneLine( line, indices, outputFile ):
    if len( line.strip() ) > 0:
        parts = [ "OFFSET FOR ZEROTH FIELD" ] + [ line[ i : j ] for i, j in zip( indices, indices[ 1 : ] + [ None ] ) ] # Inspired by https://stackoverflow.com/a/10851479/2156453

        number = parts[ 1 ].strip()
        name = parts[ 2 ].strip()
        absoluteMagnitude = parts[ 4 ].strip()

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            slopeParameter = parts[ 5 ].strip()
            epochDate = parts[ 12 ].strip()
            meanAnomalyEpoch = parts[ 13 ].strip()
            argumentPerihelion = parts[ 14 ].strip()
            longitudeAscendingNode = parts[ 15 ].strip()
            inclinationToEcliptic = parts[ 16 ].strip()
            orbitalEccentricity = parts[ 17 ].strip()
            semimajorAxix = parts[ 18 ].strip()

            components = [
                number + " " + name,
                'e',
                inclinationToEcliptic,
                longitudeAscendingNode,
                argumentPerihelion,
                semimajorAxix,
                '0',
                orbitalEccentricity,
                meanAnomalyEpoch,
                epochDate[ 4 : 6 ] + '/' + epochDate[ 6 : ] + '/' + epochDate[ 0 : 4 ],
                "2000.0",
                absoluteMagnitude,
                slopeParameter ]

            outputFile.write( ','.join( components ) + '\n' )


def convert( inFile, outFile ):
    indices = [ 1, 8, 27, 43, 50, 55, 60, 66, 74, 96, 101, 107, 116, 127, 138, 149, 159, 170, 182, 191, 200, 208, 217, 234, 251 ]
    indices = [ x - 1 for x in indices ] # Offset back to zero to match each line read into a string.

    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )

    else:
        fIn = open( inFile, 'r' )

    fOut = open( outFile, 'w' )
    for line in fIn:
        processAndWriteOneLine( line, indices, fOut )

    fIn.close()
    fOut.close()


if __name__ == "__main__":
    if len( sys.argv ) != 3:
        message = \
            "Usage: python3 " + Path(__file__).name + " fileToConvert outputFile" + \
            "\n\nFor example:" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat astorb.edb" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat.gz astorb.edb"
    
        raise SystemExit( message )
    
    convert( sys.argv[ 1 ], sys.argv[ 2 ] )