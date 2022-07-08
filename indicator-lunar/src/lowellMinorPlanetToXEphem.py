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


def processAndWriteOneLine( line, outputFile ):
    if len( line.strip() ) > 0:
        name = line[ 1 - 1 : 26 ].replace( '(', '' ).replace( ')', '' ).strip()
        absoluteMagnitude = line[ 43 - 1 : 49 ].strip() # $H

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            inclinationToEcliptic = line[ 149 - 1 : 158 ].strip() # $i
            longitudeAscendingNode = line[ 138 - 1 : 148 ].strip() # $O
            argumentPerihelion = line[ 127 - 1 : 137 ].strip() # $o
            semimajorAxix = line[ 170 - 1 : 181 ].strip() # $a
            orbitalEccentricity = line[ 159 - 1 : 169 ].strip() # $e
            meanAnomalyEpoch = line[ 116 - 1 : 126 ].strip() # $M
            epochDate = line[ 111 - 1 : 112 ] + '/' + line[ 113 - 1 : 114 ] + '/' + line[ 107 - 1 : 110 ]
            slopeParameter = line[ 50 - 1 : 54 ].strip() # $G

            components = [
                name, 'e', inclinationToEcliptic, longitudeAscendingNode,
                argumentPerihelion, semimajorAxix, '0', orbitalEccentricity, meanAnomalyEpoch,
                epochDate, "2000.0",
                absoluteMagnitude, slopeParameter ]

            outputFile.write( ','.join( components ) + '\n' )


def convert( inFile ):
    outFile = inFile.replace( "dat", "edb" )
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )
        outFile = outFile[ 0 : -3 ]

    else:
        fIn = open( inFile, 'r' )

    fOut = open( outFile, 'w' )
    for line in fIn:
        processAndWriteOneLine( line, fOut )

    fIn.close()
    fOut.close()
    return fOut.name


def main( fileToConvert ):
    outputFilename = convert( fileToConvert )
    return outputFilename


if __name__ == "__main__":
    if len( sys.argv ) != 2:
        message = \
            "Usage: python3 " + Path(__file__).name + " fileToConvert" + \
            "\n\nFor example:" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat.gz"

        raise SystemExit( message )

    print( "Created", main( sys.argv[ 1 ] ) )