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


import gettext
gettext.install( "astroskyfield" )

from skyfield.api import load
from skyfield.data import hipparcos

import argparse, astroskyfield


if __name__ == "__main__":
    hipMainDotDat = "hip_main.dat"
    commonStarNames = "https://www.cosmos.esa.int/web/hipparcos/common-star-names"
    parser = argparse.ArgumentParser(
        description = "Create a star ephemeris from " + hipMainDotDat + " containing commonly named stars listed at " + commonStarNames + ". " + \
                      "If the file " + hipMainDotDat + " is not in the current directory, you may obtain from " + hipparcos.URL + ". " + \
                      "Otherwise, " + hipMainDotDat + " will be obtained automatically." )
    parser.add_argument( "outFile", help = "The output file." )
    args = parser.parse_args()

    print( "Creating stars ephemeris..." )
    hipparcosIdentifiers = list( astroskyfield.AstroSkyfield.STARS_TO_HIP.values() )
    with load.open( hipMainDotDat, "rb" ) as inFile, open( args.outFile, "wb" ) as outFile:
        for line in inFile:
            hip = int( line.decode()[ 9 - 1 : 14 - 1 + 1 ].strip() ) # HIP is located at bytes 9 - 14, http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
            if hip in hipparcosIdentifiers:
                outFile.write( line )

    print( "Created", args.outFile )