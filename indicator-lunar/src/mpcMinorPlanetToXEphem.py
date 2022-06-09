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


import gzip, sys


centuryMap = {
    'I': 1800,
    'J': 1900,
    'K': 2000 }


# https://www.minorplanetcenter.net/iau/info/PackedDates.html
def getUnpackedDate( i ): return str( i ) if i.isdigit() else str( ord( i ) - ord( 'A' ) + 10 )


def processAndWriteOneLine( line, outputFile ):
    if len( line.strip() ) > 0:
        name = line[ 167 - 1 : 194 ].replace( '(', '' ).replace( ')', '' ).strip()
        absoluteMagnitude = line[ 9 - 1 : 13 ].strip() # $H

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            inclinationToEcliptic = line[ 60 - 1 : 68 ].strip() # $i
            longitudeAscendingNode = line[ 49 - 1 : 57 ].strip() # $O
            argumentPerihelion = line[ 38 - 1 : 46 ].strip() # $o
            semimajorAxix = line[ 93 - 1 : 103 ].strip() # $a
            orbitalEccentricity = line[ 71 - 1 : 79 ].strip() # $e
            meanAnomalyEpoch = line[ 27 - 1 : 35 ].strip() # $M
            slopeParamenter = line[ 15 - 1 : 19 ].strip() # $G

            century = line[ 21 - 1 : 21 ].strip() # $cent
            lastTwoDigitsOfYear = line[ 22 - 1 : 23 ].strip() # $TY
            year = str( centuryMap[ century ] + int( lastTwoDigitsOfYear ) ) # $TY
            month = getUnpackedDate( line[ 24 - 1 : 24 ].strip() ) # $TM
            day = getUnpackedDate( line[ 25 - 1 : 25 ].strip() ) # $TD
            epochDate = month + '/' + day + '/' + year

            components = [
                name, 'e', inclinationToEcliptic, longitudeAscendingNode,
                argumentPerihelion, semimajorAxix, '0', orbitalEccentricity, meanAnomalyEpoch,
                epochDate, "2000.0",
                absoluteMagnitude, slopeParamenter ]

            outputFile.write( ','.join( components ) + '\n' )


def convertTXT( inFile ):
    outFile = inFile[ 0 : -3 ] + "edb"
    with open( inFile, 'r' ) as fIn, open( outFile, 'w' ) as fOut:
        for line in fIn:
            processAndWriteOneLine( line, fOut )


def convertMPCORB( inFile ):
    outFile = inFile.replace( "DAT", "edb" )
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'r' )
        fOut = gzip.open( outFile, 'w' )

    else:
        fIn = open( inFile, 'r' )
        fOut = open( outFile, 'w' )

    endOfHeader = False
    for line in fIn:
        if endOfHeader:
            processAndWriteOneLine( line, fOut )

        elif line.startswith( "----------" ):
            endOfHeader = True

    fIn.close()
    fOut.close()


if len( sys.argv ) != 2:
    message = \
        "Usage: python3 mpcMinorPlanetToXEphem.py fileToConvert" + \
        "\n\nFor example:" + \
        "\n  python3 mpcMinorPlanetToXEphem.py MPCORB.DAT" + \
        "\n  python3 mpcMinorPlanetToXEphem.py MPCORB.DAT.gz" + \
        "\n  python3 mpcMinorPlanetToXEphem.py mpcDataAsStraightTextWithoutHeader.txt"

    raise SystemExit( message )

inFile = sys.argv[ 1 ]

if inFile.endswith( ".txt" ):
    convertTXT( inFile )

elif inFile.startswith( "MPCORB.DAT" ):
    convertMPCORB( inFile )

else:
    raise SystemExit( "Unknown input file format." )