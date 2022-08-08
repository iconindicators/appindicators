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


import argparse, gzip


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
            semimajorAxis = parts[ 18 ].strip()

            components = [
                ' ' * 7, # number or designation packed
                ' ', # 8
                str( round( float( absoluteMagnitude ), 2 ) ).rjust( 5 ),
                ' ', # 14
                str( round( float( slopeParameter ), 2 ) ).rjust( 5 ),
                ' ', # 20
                getPackedDate( epochDate[ 0 : 4 ], epochDate[ 4 : 6 ], epochDate[ 6 : 8 ] ).rjust( 5 ),
                ' ', # 26
                str( round( float( meanAnomalyEpoch ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 36, 37 
                str( round( float( argumentPerihelion ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 47, 48
                str( round( float( longitudeAscendingNode ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 58, 59
                str( round( float( inclinationToEcliptic ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 69, 70
                str( round( float( orbitalEccentricity ), 7 ) ).rjust( 9 ),
                ' ', # 80
                ' ' * 11, # mean daily motion
                ' ', # 92
                str( round( float( semimajorAxis ), 7 ) ).rjust( 11 ),
                ' ' * 2, # 104, 105
                ' ', # uncertainty parameter
                ' ', # 107
                ' ' * 9, # reference
                ' ', # 117
                numberObservations.rjust( 5 ),
                ' ', # 123
                ' ' * 3, # oppositions
                ' ', # 127
                ' ' * ( 4 + 1 + 4 ), # multiple/single oppositions
                ' ', # 137
                ' ' * 4, # rms residual
                ' ', # 142
                ' ' * 3, # coarse indicator of perturbers
                ' ', # 146
                ' ' * 3, # precise indicator of perturbers
                ' ', # 150
                ' ' * 10, # computer name
                ' ', # 161
                ' ' * 4, # hexdigit flags
                ' ', # 166
                ( number + ' ' + name ).strip().ljust( 194 - 167 + 1 ),
                ' ' * 8 ] # date last observation

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
#     if len( sys.argv ) != 3:
#         message = \
#             "Usage: python3 " + Path(__file__).name + " fileToConvert outputFile" + \
#             "\n\nFor example:" + \
#             "\n  python3  " + Path(__file__).name + " astorb.dat astorb.txt" + \
#             "\n  python3  " + Path(__file__).name + " astorb.dat.gz astorb.txt"
#
#         raise SystemExit( message )
#
#     convert( sys.argv[ 1 ], sys.argv[ 2 ] )


    parser = argparse.ArgumentParser(
        description = "Convert a minor planet text file such as astorb.dat or astorb.dat.gz from Lowell to MPC format. " + \
                      "If the file ends in '.gz' the file will be treated as a gzip file; otherwise the file is assumed to be text." )
    parser.add_argument( "inFile", help = "File to convert" )
    parser.add_argument( "outFile", help = "Output file to be created" )
    args = parser.parse_args()
    convert( args.inFile, args.outFile )