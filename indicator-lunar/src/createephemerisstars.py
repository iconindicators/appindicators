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


# Create a star ephemeris containing stars with a common name.
# The ephemeris for Skyfield is saved to file.
# The ephemeris for PyEphem is printed to screen, suitable for pasting in a Python file.


from pandas import read_csv
from skyfield.api import Star, load
from skyfield.data import hipparcos

import argparse


# Indices for columns at http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt.
nameStart = 19
nameEnd = 36
hipStart = 91
hipEnd = 96
absoluteMagnitudeStart = 82
absoluteMagnitudeEnd = 86


def getStarsAndHIPs( starFile, maximumAbsoluteMagnitude ):
    starsAndHIPs = [ ]
    fIn = open( starFile, 'r' )
    for line in fIn:
        if line.startswith( '#' ) or line.startswith( '$' ):
            continue

        try:
            absoluteMagnitude = float( line[ absoluteMagnitudeStart - 1 : absoluteMagnitudeEnd - 1 + 1 ] )
            if absoluteMagnitude > maximumAbsoluteMagnitude:
                continue 

            nameUTF8 = line[ nameStart - 1 : nameEnd - 1 + 1 ].strip()
            hip = int( line[ hipStart - 1 : hipEnd - 1 + 1 ] )
            starsAndHIPs.append( [ nameUTF8, hip ] )

        except ValueError:
            pass

    fIn.close()

    return starsAndHIPs


def printFormattedStars( starsAndHIPs ):
    print()
    for name, hip in starsAndHIPs:
        print(
            "        [ " + \
            "\"" + name.upper() + "\"," + \
            ( ' ' * ( nameEnd - nameStart - len( name ) + 1 ) ) + \
            str( hip ) + ", " + \
            ( ' ' * ( hipEnd - hipStart - len( str( hip ) ) + 1 ) ) + \
            "_( \"" + name.title() + "\" )," + \
            ( ' ' * ( nameEnd - nameStart - len( name ) + 1 ) ) + \
            "_( \"" + name.upper() + "\" ) ]," )

    print()


def createEphemerisSkyfield( outFile, starEphemeris, starsAndHIPs ):
    print( "Creating stars ephemeris for Skyfield..." )
    hipparcosIdentifiers = [ starAndHIP[ 1 ] for starAndHIP in starsAndHIPs ]
    with load.open( starEphemeris, "rb" ) as inFile, open( outFile, "wb" ) as f:
        for line in inFile:
            hip = int( line.decode()[ 9 - 1 : 14 - 1 + 1 ].strip() ) # HIP is located at bytes 9 - 14, http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
            if hip in hipparcosIdentifiers:
                f.write( line )

    print( "Created", outFile )
    print()


# Mostly taken from https://github.com/brandon-rhodes/pyephem/blob/master/bin/rebuild-star-data
def createEphemerisPyEphem( bspFile , starEphemeris, starsAndHIPs ):
    print( "Creating stars ephemeris for PyEphem..." )
    with load.open( starEphemeris, "rb" ) as f:
        stars = hipparcos.load_dataframe( f )

    with load.open( starEphemeris, "rb" ) as f:
        starsWithSpectralType = read_csv(
            f,
            sep = '|',
            names = hipparcos._COLUMN_NAMES,
            na_values = [ '     ', '       ', '        ', '            ' ],
            low_memory = False,
        )

        starsWithSpectralType = starsWithSpectralType.set_index( "HIP" )

    sunAt = load( bspFile )[ "Sun" ].at( load.timescale().J( 2000.0 ) )
    for name, hip in starsAndHIPs:
        row = stars.loc[ hip ]
        rowWithSpectralType = starsWithSpectralType.loc[ hip ]
        star = Star.from_dataframe( row )
        rightAscension, declination, _ = sunAt.observe( star ).radec()

        spectralType = rowWithSpectralType[ "SpType" ]
        if isinstance( spectralType, str ):
            spectralType = spectralType[ : 2 ]   

        else:
            spectralType = "  "  # From _listastro.c, the spectral code must be two characters.

        components = [
            name.upper(),
            "f|S|" +
            spectralType,
            '%.8f' % rightAscension.hours + '|' + str( star.ra_mas_per_year ),
            '%.8f' % declination.degrees + '|' + str( star.dec_mas_per_year ),
            row[ "magnitude" ],
        ]

        line = ','.join( str( item ) for item in components )
        print( "        \"" + name.upper() + "\"" + ( ' ' * ( nameEnd - nameStart - len( name ) + 1 ) ) + ": \"" + line + "\"," )

    print()


# Sample arguments:
#     IAU-CSN.txt hip_main.dat 15.0 de421.bsp stars.dat
if __name__ == "__main__":
    parser = argparse.ArgumentParser( 
        description = "Using a list of stars, create " + \
                      "1) a star ephemeris for Skyfield, " + \
                      "2) a star ephemeris for PyEphem, " + 
                      "3) a list of stars with corresponding HIP formatted for use in a Python definition." )

    starInformationURL = "http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt"
    parser.add_argument( "starInformation", help = "The list of stars, downloaded from " + starInformationURL + " and saved as a text file." )

    starEphemerisURL = "https://cdsarc.cds.unistra.fr/ftp/cats/I/239/"
    parser.add_argument( "starEphemeris", help = "The star ephemeris file, typically named hip_main.dat and downloaded from " + starEphemerisURL + "." )

    parser.add_argument( "starMaximumAbsoluteMagnitude", help = "Any star wil an absolute magnitude exceeding the maximum specified will be dropped." )

    planetEphemerisURL = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets"
    parser.add_argument( "planetEphemeris", help = "A planet ephemeris file in .bsp format, downloaded from " + planetEphemerisURL + "." )

    parser.add_argument( "outputFilenameForSkyfieldStars", help = "The output file which will contain a subset of hip_main.dat for use in Skyfield." )
    args = parser.parse_args()

    starsAndHIPS = getStarsAndHIPs( args.starInformation, float( args.starMaximumAbsoluteMagnitude ) )
    printFormattedStars( starsAndHIPS )
    createEphemerisSkyfield( args.outputFilenameForSkyfieldStars, args.starEphemeris, starsAndHIPS )
    createEphemerisPyEphem( args.planetEphemeris, args.starEphemeris, starsAndHIPS )