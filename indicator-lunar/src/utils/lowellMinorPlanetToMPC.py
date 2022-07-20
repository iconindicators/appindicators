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


def processAndWriteOneLineORIGINAL( line, outputFile ):
    if len( line.strip() ) > 0:
        name = line[ 1 - 1 : 26 ].replace( '(', '' ).replace( ')', '' ).strip()
        absoluteMagnitude = line[ 43 - 1 : 49 ].strip()

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            components = [
                " " * ( 7 - 1 + 1 ), # number or designation packed
                str( round( float( absoluteMagnitude ), 2 ) ).rjust( 13 - 9 + 1 ),
                str( round( float( line[ 50 - 1 : 54 ].strip() ), 2 ) ).rjust( 19 - 15 + 1 ), # slope parameter
                getPackedDate( line[ 107 - 1 : 110 ], line[ 111 - 1 : 112 ], line[ 113 - 1 : 114 ] ).rjust( 25 - 21 + 1 ), # packed date
                str( round( float( line[ 116 - 1 : 126 ].strip() ), 5 ) ).rjust( 35 - 27 + 1 ) + ' ', # mean anomaly
                str( round( float( line[ 127 - 1 : 137 ].strip() ), 5 ) ).rjust( 46 - 38 + 1 ) + ' ', # argument of perihelion
                str( round( float( line[ 138 - 1 : 148 ].strip() ), 5 ) ).rjust( 57 - 49 + 1 ) + ' ', # longitude of ascending node
                str( round( float( line[ 149 - 1 : 158 ].strip() ), 5 ) ).rjust( 68 - 60 + 1 ) + ' ', # inclination to the ecliptic
                str( round( float( line[ 159 - 1 : 169 ].strip() ), 7 ) ).rjust( 79 - 71 + 1 ), # orbital eccentricity
                " " * ( 91 - 81 + 1 ), # mean daily motion
                str( round( float( line[ 170 - 1 : 181 ].strip() ), 7 ) ).rjust( 103 - 93 + 1 ) + ' ', # semi major axis
                " " * ( 106 - 106 + 1 ), # uncertainty parameter
                " " * ( 116 - 108 + 1 ), # reference
                line[ 101 - 1 : 106 ].strip().rjust( 122 - 118 + 1 ), # observations
                " " * ( 126 - 124 + 1 ), # oppositions
                " " * ( 128 - 136 + 1 ), # oppositions
                " " * ( 141 - 138 + 1 ), # rms residual
                " " * ( 145 - 143 + 1 ), # coarse indicator of perturbers
                " " * ( 149 - 147 + 1 ), # precise indicator of perturbers
                " " * ( 160 - 151 + 1 ), # computer name
                " " * ( 165 - 162 + 1 ), # hexdigit flags
                name.rjust( 194 - 167 + 1 ),
                " " * ( 202 - 195 + 1 ) ] # date last observation

            outputFile.write( ' '.join( components ) + '\n' )


def convertORIGINAL( inFile, outFile ):
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