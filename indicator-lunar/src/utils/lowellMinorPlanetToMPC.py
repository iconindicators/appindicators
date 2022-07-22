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


# Convert minor planet data in Lowell format to MPC format.
#
# Lowell format: 
#    https://asteroid.lowell.edu/main/astorb/
#
# MPC format: 
#    https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html


from pathlib import Path

import gzip, sys


# https://www.minorplanetcenter.net/iau/info/PackedDates.html
def getPackedDate( year, month, day ):
    packedYear = year[ 2 : ]
    if int( year ) < 1900:
        packedYear = 'I' + packedYear

    elif int( year ) < 2000:
        packedYear = 'J' + packedYear

    else:
        packedYear = 'K' + packedYear


    def getPackedDayMonth( dayOrMonth ):
        if int( dayOrMonth ) < 10:
            packedDayMonth = str( int( dayOrMonth ) )

        else:
            packedDayMonth = chr( int( dayOrMonth ) - 10 + ord( 'A' ) )

        return packedDayMonth

    packedMonth = getPackedDayMonth( month )
    packedDay = getPackedDayMonth( day )

    return packedYear + packedMonth + packedDay


def justify( stringToJustify, start, end, rightAdjust = True ):
    if rightAdjust:
        stringJustified = stringToJustify.rjust( end - start + 1 )

    else:  
        stringJustified = stringToJustify.ljust( end - start + 1 )

    return stringJustified


def pad( start, end ): return ' ' * ( end - start + 1 )


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
            numberObservations = parts[ 11 ].strip()
            epochDate = parts[ 12 ].strip()
            meanAnomalyEpoch = parts[ 13 ].strip()
            argumentPerihelion = parts[ 14 ].strip()
            longitudeAscendingNode = parts[ 15 ].strip()
            inclinationToEcliptic = parts[ 16 ].strip()
            orbitalEccentricity = parts[ 17 ].strip()
            semimajorAxix = parts[ 18 ].strip()

            components = [
                pad( 1, 7 ), # number or designation packed
                ' ',
                justify( str( round( float( absoluteMagnitude ), 2 ) ), 9, 13 ),
                ' ',
                justify( str( round( float( slopeParameter ), 2 ) ), 15, 19 ),
                ' ',
                justify( getPackedDate( epochDate[ 0 : 4 ], epochDate[ 4 : 6 ], epochDate[ 6 : 8 ] ), 21, 25 ),
                ' ',
                justify( str( round( float( meanAnomalyEpoch ), 5 ) ), 27, 35 ),
                ' ',
                ' ',
                justify( str( round( float( argumentPerihelion ), 5 ) ), 38, 46 ),
                ' ',
                ' ',
                justify( str( round( float( longitudeAscendingNode ), 5 ) ), 49, 57 ),
                ' ',
                ' ',
                justify( str( round( float( inclinationToEcliptic ), 5 ) ), 60, 68 ),
                ' ',
                ' ',
                justify( str( round( float( orbitalEccentricity ), 7 ) ), 71, 79 ),
                ' ',
                pad( 81, 91 ), # mean daily motion
                ' ',
                justify( str( round( float( semimajorAxix ), 7 ) ), 93, 103 ),
                ' ',
                ' ',
                pad( 106, 106 ), # uncertainty parameter
                ' ',
                pad( 108, 116 ), # reference
                ' ',
                justify( numberObservations, 118, 122 ),
                ' ',
                pad( 124, 126 ), # oppositions
                ' ',
                pad( 128, 136 ), # oppositions
                ' ',
                pad( 138, 141 ), # rms residual
                ' ',
                pad( 143, 145 ), # coarse indicator of perturbers
                ' ',
                pad( 147, 149 ), # precise indicator of perturbers
                ' ',
                pad( 151, 160 ), # computer name
                ' ',
                pad( 162, 165 ), # hexdigit flags
                ' ',
                justify( number + ' ' + name, 167, 194, False ),
                pad( 195, 202 ) ] # date last observation

            outputFile.write( ''.join( components ) + '\n' )


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
    if len( sys.argv ) != 3:
        message = \
            "Usage: python3 " + Path(__file__).name + " fileToConvert outputFile" + \
            "\n\nFor example:" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat astorb.txt" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat.gz astorb.txt"

        raise SystemExit( message )

    convert( sys.argv[ 1 ], sys.argv[ 2 ] )