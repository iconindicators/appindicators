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


def processAndWriteOneLine( line, outputFile ):
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


def convert( inFile ):
    outFile = inFile.replace( "dat", "mpc.dat" )
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'r' )
        outFile = outFile[ 0 : -3 ]

    else:
        fIn = open( inFile, 'r' )

    fOut = open( outFile, 'w' )
    for line in fIn:
        processAndWriteOneLine( line, fOut )

    fIn.close()
    fOut.close()
    return fOut.name


if len( sys.argv ) != 2:
    message = \
        "Usage: python3 " + sys.argv[ 0 ] + " fileToConvert" + \
        "\n\nFor example:" + \
        "\n  python3  " + sys.argv[ 0 ] + " astorb.dat" + \
        "\n  python3  " + sys.argv[ 0 ] + " astorb.dat.gz"

    raise SystemExit( message )

print( "Created", convert( sys.argv[ 1 ] ) )