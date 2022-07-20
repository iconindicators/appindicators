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


def test():
    s = 'long string that I want to split up'
    indices = [ 0, 5, 12, 17 ]

    s = "     1 Ceres              L.H. Wasserman   3.33  0.15 0.72 848.4 G?      0   0   0   0   0   0 80714 6778 20220809 334.327376  73.531308  80.266493 10.586785 0.07863562   2.76661907 20220428 1.1E-02  2.4E-07 20220703 2.4E-02 20230320 2.5E-02 20270108 2.7E-02 20320223"
    indices = [ 1, 8, 27, 43, 50, 55, 60, 66, 74, 96, 101, 107, 116, 127, 138, 149, 159, 170, 182, 191, 200, 208, 217, 234, 251 ]
    indices = [ x - 1 for x in indices ]    

    parts = [ s[ i : j ] for i, j in zip( indices, indices[ 1 : ] + [ None ] ) ]
    parts = [ "OFFSET FOR ZEROTH FIELD" ] + [ s[ i : j ] for i, j in zip( indices, indices[ 1 : ] + [ None ] ) ]
    print( parts )


def processAndWriteOneLine( line, indices, outputFile ):
    if len( line.strip() ) > 0:
        parts = [ "OFFSET FOR ZEROTH FIELD" ] + [ line[ i : j ] for i, j in zip( indices, indices[ 1 : ] + [ None ] ) ]

        numberAndName = parts[ 1 ].strip() + " " + parts[ 2 ].strip()
        absoluteMagnitude = parts[ 4 ].strip()

        if len( numberAndName ) == 0:
            print( "Missing numberAndName:\n" + line )

        elif len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            slopeParameter = parts[ 5 ].strip()
            epochDate = parts[ 12 ].strip()
            epochDate = epochDate[ 4 : 6 ] + '/' + epochDate[ 6 : ] + '/' + epochDate[ 0 : 4 ]
            meanAnomalyEpoch = parts[ 13 ].strip()
            argumentPerihelion = parts[ 14 ].strip()
            longitudeAscendingNode = parts[ 15 ].strip()
            inclinationToEcliptic = parts[ 16 ].strip()
            orbitalEccentricity = parts[ 17 ].strip()
            semimajorAxix = parts[ 18 ].strip()

            components = [
                numberAndName, 'e', inclinationToEcliptic, longitudeAscendingNode,
                argumentPerihelion, semimajorAxix, '0', orbitalEccentricity, meanAnomalyEpoch,
                epochDate, "2000.0",
                absoluteMagnitude, slopeParameter ]

            outputFile.write( ','.join( components ) + '\n' )


def convert( inFile, outFile ):
    indices = [ 1, 8, 27, 43, 50, 55, 60, 66, 74, 96, 101, 107, 116, 127, 138, 149, 159, 170, 182, 191, 200, 208, 217, 234, 251 ]
    indices = [ x - 1 for x in indices ]    

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
        name = line[ 1 - 1 : 26 ].strip()
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
            "\n  python3  " + Path(__file__).name + " astorb.dat astorb.edb" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat.gz astorb.edb"
    
        raise SystemExit( message )
    
    convert( sys.argv[ 1 ], sys.argv[ 2 ] )
    
    # test()