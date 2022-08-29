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


import gettext
gettext.install( "astrobase" )

from astrobase import AstroBase
from pandas import read_csv
from skyfield.api import Star, load
from skyfield.data import hipparcos

import argparse


def createEphemerisSkyfield( outFile ):
    print( "Creating stars ephemeris for Skyfield..." )
    hipparcosIdentifiers = AstroBase.getStarHIPs()
    with load.open( hipMainDotDat, "rb" ) as inFile, open( outFile, "wb" ) as f:
        for line in inFile:
            hip = int( line.decode()[ 9 - 1 : 14 - 1 + 1 ].strip() ) # HIP is located at bytes 9 - 14, http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
            if hip in hipparcosIdentifiers:
                f.write( line )

    print( "Created", outFile )


# Mostly taken from https://github.com/brandon-rhodes/pyephem/blob/master/bin/rebuild-star-data
def createEphemerisPyEphem( bspFile ):
    print( "Creating stars ephemeris for PyEphem..." )
    with load.open( hipMainDotDat, "rb" ) as f:
        stars = hipparcos.load_dataframe( f )

    with load.open( hipMainDotDat, "rb" ) as f:
        starsWithSpectralType = read_csv(
            f,
            sep = '|',
            names = hipparcos._COLUMN_NAMES,
            na_values = [ '     ', '       ', '        ', '            ' ],
            low_memory = False,
        )

        starsWithSpectralType = starsWithSpectralType.set_index( "HIP" )

    sunAt = load( bspFile )[ "Sun" ].at( load.timescale().J( 2000.0 ) )
    for name, hip, translatedName, translatedTag in AstroBase.STARS:
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
            name,
            "f|S|" +
            spectralType,
            '%.8f' % rightAscension.hours + '|' + str( star.ra_mas_per_year ),
            '%.8f' % declination.degrees + '|' + str( star.dec_mas_per_year ),
            row[ "magnitude" ],
        ]

        line = ','.join( str( item ) for item in components )
        print( '"' + line + '",' )  


if __name__ == "__main__":
    hipMainDotDat = "hip_main.dat"
    commonStarNames = "https://www.cosmos.esa.int/web/hipparcos/common-star-names"
    bspURL = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets"
    _description = "Create a star ephemeris for Skyfield and PyEphem containing the commonly named stars listed at " + commonStarNames + ". " + \
                  "The file " + hipMainDotDat + " must be present, available from " + hipparcos.URL + " (otherwise will download automatically). " + \
                  "A .bsp planets ephemeris file must be present, available from " + bspURL + "."

    parser = argparse.ArgumentParser( description = _description )
    parser.add_argument( "bspFile", help = "The .bsp planets ephemeris file." )
    parser.add_argument( "outFileForSkyfield", help = "The output file for use in Skyfield." )
    args = parser.parse_args()

    createEphemerisSkyfield( args.outFileForSkyfield )
    print()
    createEphemerisPyEphem( args.bspFile )