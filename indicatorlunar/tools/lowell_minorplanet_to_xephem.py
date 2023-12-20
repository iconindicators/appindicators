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


import argparse
import gzip


def processAndWriteOneLine( line, outputFile ):
    if len( line.strip() ) > 0:
        startIndices = [ 1, 8, 27, 43, 49, 55, 60, 66, 71, 96, 101, 107, 116, 127, 138, 148, 159, 169, 183, 192, 200, 209, 218, 235, 252 ]
        startIndices = [ x - 1 for x in startIndices ] # Offset back to zero to match each line read into a string.

        parts = [ "OFFSET TO ALIGN WITH FIELD NUMBERING" ] + \
                [ line[ i : j ] for i, j in zip( startIndices, startIndices[ 1 : ] + [ None ] ) ] # Inspired by https://stackoverflow.com/a/10851479/2156453

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
            semimajorAxis = parts[ 18 ].strip()

            components = [
                ( number + ' ' + name ).strip(),
                'e',
                inclinationToEcliptic,
                longitudeAscendingNode,
                argumentPerihelion,
                semimajorAxis,
                '0',
                orbitalEccentricity,
                meanAnomalyEpoch,
                epochDate[ 4 : 6 ] + '/' + epochDate[ 6 : ] + '/' + epochDate[ 0 : 4 ],
                "2000.0",
                absoluteMagnitude,
                slopeParameter ]

            outputFile.write( ','.join( components ) + '\n' )


def convert( inFile, outFile ):
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )

    else:
        fIn = open( inFile, 'r' )

    fOut = open( outFile, 'w' )
    for line in fIn:
        processAndWriteOneLine( line, fOut )

    fIn.close()
    fOut.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Convert a minor planet text file such as astorb.dat or astorb.dat.gz from Lowell to XEphem format. " + \
                      "If the file ends in '.gz' the file will be treated as a gzip file; otherwise the file is assumed to be text." )
    parser.add_argument( "inFile", help = "File to convert" )
    parser.add_argument( "outFile", help = "Output file to be created" )
    args = parser.parse_args()
    convert( args.inFile, args.outFile )
