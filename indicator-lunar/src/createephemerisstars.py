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

import argparse, textwrap


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
    print( "Printing formatted stars from", starInformationURL )
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

    print( "Done" )


def createEphemerisSkyfield( outFile, starEphemeris, starsAndHIPs ):
    print( "Creating", outFile, "for Skyfield..." )
    hipparcosIdentifiers = [ starAndHIP[ 1 ] for starAndHIP in starsAndHIPs ]
    with load.open( starEphemeris, "rb" ) as inFile, open( outFile, "wb" ) as f:
        for line in inFile:
            hip = int( line.decode()[ 9 - 1 : 14 - 1 + 1 ].strip() ) # HIP is located at bytes 9 - 14, http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
            if hip in hipparcosIdentifiers:
                f.write( line )

    print( "Done" )


# Mostly taken from https://github.com/brandon-rhodes/pyephem/blob/master/bin/rebuild-star-data
def printEphemerisPyEphem( bspFile , starEphemeris, starsAndHIPs ):
    print( "Printing ephemeris for PyEphem..." )
    with load.open( starEphemeris, "rb" ) as f:
        stars = hipparcos.load_dataframe( f )
        f.seek( 0 )
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
        absoluteMagnitude = row[ "magnitude" ]
        star = Star.from_dataframe( row )
        rightAscension, declination, _ = sunAt.observe( star ).radec()

        rowWithSpectralType = starsWithSpectralType.loc[ hip ]
        spectralType = rowWithSpectralType[ "SpType" ]
        if isinstance( spectralType, str ):
            spectralType = spectralType[ : 2 ]   

        else:
            spectralType = "  "  # Is NaN; to fix, set to two blank characters (see _libastro.c).

        components = [
            name.upper(),
            "f|S|" +
            spectralType,
            '%.8f' % rightAscension.hours + '|' + str( star.ra_mas_per_year ),
            '%.8f' % declination.degrees + '|' + str( star.dec_mas_per_year ),
            absoluteMagnitude,
        ]

        line = ','.join( str( item ) for item in components )
        print( "        \"" + name.upper() + "\"" + ( ' ' * ( nameEnd - nameStart - len( name ) + 1 ) ) + ": \"" + line + "\"," )

    print( "Done" )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = textwrap.dedent( '''\
            Takes the star information and:
            1) Prints a list of star names, corresponding HIP and star name for translation (as a Python list of lists).
            2) Creates a star ephemeris file for Skyfield.
            3) Prints stars and corresponding PyEphem format ephemeris (as a Python dictionary).

            For example: python3 %(prog)s IAU-CSN.txt hip_main.dat 15.0 de421.bsp stars.dat''' ) )

    starInformationURL = "http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt"
    parser.add_argument( "starInformation", help = "The list of stars, downloaded from " + starInformationURL + " and saved as a text file." )

    starEphemerisURL = "https://cdsarc.cds.unistra.fr/ftp/cats/I/239/"
    parser.add_argument( "starEphemeris", help = "A star ephemeris file, typically named hip_main.dat and downloaded from " + starEphemerisURL + "." )

    parser.add_argument( "starMaximumAbsoluteMagnitude", help = "Any star which has an absolute magnitude exceeding this number will be dropped." )

    planetEphemerisURL = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets"
    parser.add_argument( "planetEphemeris", help = "A planet ephemeris file in .bsp format, downloaded from " + planetEphemerisURL + "." )

    parser.add_argument( "outputFilenameForSkyfieldStarEphemeris", help = "The output filename for the Skyfield star ephemeris." )
    args = parser.parse_args()

    starsAndHIPS = getStarsAndHIPs( args.starInformation, float( args.starMaximumAbsoluteMagnitude ) )
    printFormattedStars( starsAndHIPS )
    createEphemerisSkyfield( args.outputFilenameForSkyfieldStarEphemeris, args.starEphemeris, starsAndHIPS )
    printEphemerisPyEphem( args.planetEphemeris, args.starEphemeris, starsAndHIPS )