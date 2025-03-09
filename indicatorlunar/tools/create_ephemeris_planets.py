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


'''
Create a planet ephemeris for use in Skyfield which commences from
today's date to end at the specified number of years from today.

The start date is wound back one month to take into account a quirk
in the Skyfield lunar eclipse algorithm.

This script essentially wraps up the following command:

    python3 -m jplephem excerpt start_date end_date in_file.bsp out_file.bsp

Requires jplephem:
    https://pypi.org/project/jplephem

BSP files:
    https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets

References:
    https://github.com/skyfielders/python-skyfield/issues/123
    https://github.com/skyfielders/python-skyfield/issues/531
    ftp://ssd.jpl.nasa.gov/pub/eph/planets/README.txt
    ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/ascii_format.txt

Alternately to running this script, download a .bsp and
use spkmerge to create a smaller subset:
    https://github.com/skyfielders/python-skyfield/issues/123
    https://github.com/skyfielders/python-skyfield/issues/231#issuecomment-450507640
'''


import argparse
import datetime
import subprocess
import textwrap

from dateutil.relativedelta import relativedelta


def create_ephemeris_planets(
    in_bsp,
    out_bsp,
    years ):

    today = datetime.date.today()
    start_date = today - relativedelta( months = 1 )
    end_date = today.replace( year = today.year + years )
    date_format = "%Y/%m/%d"

    command = (
        "python3 -m jplephem excerpt " + \
        start_date.strftime( date_format ) + " " + \
        end_date.strftime( date_format ) + " " + \
        in_bsp + " " + out_bsp )

    print( "Processing...\n\t", command )
    subprocess.call( command, shell = True )  #TODO Replace with .run


if __name__ == "__main__":
    description = (
        textwrap.dedent(
            r'''
            From an existing .bsp, create a new .bsp with a date range
            from today to a specified number of years from today.

            For example:
                python3 %(prog)s de421.bsp planets.bsp 5

            -------------------------------------------------------
            --- INPUT & OUTPUT PATHNAMES CONTAINING SPACES MUST ---
            ---     * BE DOUBLE QUOTED                          ---
            ---     * HAVE SPACES ESCAPED WITH A \              ---
            -------------------------------------------------------
            ''' ) )

    parser = (
        argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = description ) )

    parser.add_argument(
        "in_bsp",
        help = "The input .bsp file." )

    parser.add_argument(
        "out_bsp",
        help = "The output .bsp file with reduced date range." )

    parser.add_argument(
        "years",
        help = "The number of years from today to include in the output .bsp." )

    args = parser.parse_args()

    create_ephemeris_planets(
        args.in_bsp,
        args.out_bsp,
        int( args.years ) )
