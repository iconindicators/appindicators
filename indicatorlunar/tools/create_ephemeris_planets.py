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
Create a planet ephemeris for use in astroskyfield, from today's date,
ending at a specified number of years from today.

The start date is wound back one month to take into account the Skyfield
lunar eclipse algorithm.

This script essentially wraps up the following command:

    python3 -m jplephem excerpt start_date end_date in_file.bsp out_file.bsp

BSP files:
    https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets

References:
    https://github.com/skyfielders/python-skyfield/issues/123
    https://github.com/skyfielders/python-skyfield/issues/531
    ftp://ssd.jpl.nasa.gov/pub/eph/planets/README.txt
    ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/ascii_format.txt

Alternatively to running this script, download a .bsp and use spkmerge:
    https://github.com/skyfielders/python-skyfield/issues/123
'''


#TODO This script uses Python3, jplephem and numpy. 
#
# Need to verify it works on 32 bit and also Ubuntu 20.04
# as some pinning of versions may need to be done.
#
# https://numpy.org/doc/2.0/release/1.22.0-notes.html
# For 32 bit on Linux, might need to pin numpy to < 1.22.0
#
# https://numpy.org/doc/2.0/release/1.25.0-notes.html
# For Ubuntu 20.04 et al, pin numpy to < 1.25.0 as < Python 3.9 is unsupported.
# 
# Ubuntu 22.04 has python 3.10 so should not need numpy pinning until 3.10 is 
# deprecated or unsupported by numpy.
# 
# Debian 11 has python 3.9 so should not need numpy pinning until 3.9 is
# deprecated or unsupported by numpy.
# 
# Check for Fedora, Manjaro and openSUSE!


#TODO jplephem will install numpy.
# For 32 bit and/or Ubuntu 20.04 might need to explicitly
# list numpy and pin to a version.


import argparse
import datetime
import sys
import textwrap

from dateutil.relativedelta import relativedelta

if '../' not in sys.path:
    sys.path.insert( 0, '../../' )

from tools import utils


if __name__ == "__main__":
    description = (
        textwrap.dedent(
            r'''
            From an existing .bsp, create a new .bsp with a date range starting
            one month prior to today, to the specified number of years from today.

            For example:
                python3 -m %(prog)s de442s.bsp planets.bsp 5

            Ensure that the existing .bsp contains data from
                "one month before today"
            up to
                "today plus the specified years"

            Input and output pathnames which contain spaces must:
                * Be double quoted
                * Have spaces escaped with a \
            ''' ) )

    args = (
        utils.get_arguments(
            description,
            ( "in_bsp", "out_bsp", "years" ),
            {
                "in_bsp":
                    "The input .bsp file.",
                "out_bsp":
                    "The output .bsp file with the specified date range.",
                "years":
                    "The number of years from today the output .bsp will span." },
            formatter_class = argparse.RawDescriptionHelpFormatter ) )

    today = datetime.date.today()
    start_date = today - relativedelta( months = 1 )
    end_date = today.replace( year = today.year + int( args.years ) )
    date_format = "%Y/%m/%d"

    command = (
        "python3 -m jplephem excerpt "
        f"{ start_date.strftime( date_format ) } "
        f"{ end_date.strftime( date_format ) } "
        f"{ args.in_bsp } { args.out_bsp }" )

    utils.python_run(
        command,
        utils.VENV_BUILD,
        "jplephem" )
