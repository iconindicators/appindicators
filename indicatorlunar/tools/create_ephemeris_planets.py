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


# Create a planet ephemeris for use in Skyfield which commences from
# today's date to end at the specified number of years from today.
#
# The start date is actually wound back one month to take into account
# a quirk of the Skyfield lunar eclipse algorithm.
#
# This script essentially wraps up the following command:
#
#    python3 -m jplephem excerpt startDate endDate inFile.bsp outFile.bsp
#
# Requires jplephem:
#    https://pypi.org/project/jplephem
#
# BSP files:
#    https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets
#
# References:
#    https://github.com/skyfielders/python-skyfield/issues/123
#    https://github.com/skyfielders/python-skyfield/issues/531
#    ftp://ssd.jpl.nasa.gov/pub/eph/planets/README.txt
#    ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/ascii_format.txt
#
# Alternately to running this script, download a .bsp and
# use spkmerge to create a smaller subset:
#    https://github.com/skyfielders/python-skyfield/issues/123
#    https://github.com/skyfielders/python-skyfield/issues/231#issuecomment-450507640


import argparse
import datetime
import subprocess

from dateutil.relativedelta import relativedelta


def createEphemerisPlanets( inBsp, outBsp, years ):
    today = datetime.date.today()
    startDate = today - relativedelta( months = 1 )
    endDate = today.replace( year = today.year + years )
    dateFormat = "%Y/%m/%d"
    command = \
        "python3 -m jplephem excerpt " + \
        startDate.strftime( dateFormat ) + " " + \
        endDate.strftime( dateFormat ) + " " + \
        inBsp + " " + outBsp
    print( "Processing...\n\t", command )
    subprocess.call( command, shell = True )
    print( "Created", outBsp )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Reduce the date range of a .bsp from today to a specified number of years from today." )

    parser.add_argument(
        "inBSP",
        help = "The .bsp file to reduce, such as de440s.bsp." )

    parser.add_argument(
        "outBSP",
        help = "The .bsp file to be created with reduced date range, such as planets.bsp." )

    parser.add_argument(
        "years",
        help = "The number of years from today to include in the output .bsp." )

    args = parser.parse_args()

    createEphemerisPlanets( args.inBSP, args.outBSP, int( args.years ) )
