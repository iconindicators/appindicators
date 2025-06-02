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
Create a planet ephemeris for use in Skyfield which commences from today's date
and ends at a specified number of years from today.

The start date is wound back one month to take into account a quirk in the
Skyfield lunar eclipse algorithm.

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


#TODO
# venv=venv_xxx && \
# if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
# . ${venv}/bin/activate && \
# python3 -m pip install jplephem && \
# python3 create_ephemeris_planets.py ~/Downloads/de442s.bsp planets.bsp 10 && \
# deactivate

#TODO I don't think it is possible to install jplephem on 32 bit.
# Try running this script (and create ephemeris stars?) on Ubuntu 22.04 or 24.04 in a new, clean venv.
#
# https://numpy.org/doc/2.0/release/1.21.0-notes.html
# For 32 bit on Linux, might need to pin numpy to < 1.22.0
#
# https://numpy.org/doc/2.0/release/1.25.0-notes.html
# For Ubuntu 20.04 et al, pin numpy to < 1.25.0
# 
# Ubuntu 22.04 has python 3.10 so should not need numpy pinning until 3.10 is 
# deprecated or unsupported by numpy.
# 
# Debian 11 has python 3.9 so should not need numpy pinning until 3.9 is
# deprecated or unsupported by numpy.
# 
# Pandas 2.0.0 supports python3.8+ and numpy 1.20.3 so only good for ubuntu 20.04+
# 
# Pandas 2.1.0 supports python3.9+ and numpy 1.22.4 so only good for ubuntu 22.04+
# 
# Test on Debian 12 vm and then Debian 12 32 laptop.
#
# Don't forget to check all of these for Fedora, Manjaro and openSUSE!
#
# 
#
# What about the need to pin
#    requests?
#    sgp4?
# Neither seem to have any issue but test on Debian 32 bit!
#
#
# Further, this pinning may be a normal thing for all indicators...
# The pyproject.tom.specific for lunar may need to change somehow (if skyfield is used)
# and any install instructions will need to include the pinning there,
# rather than in the dependencies of pyproject.toml (which should contain no
# dependencies). 
#
# This script needs to create a venv, install jplephem
# (pinned or not and/or check os version)
# and then run the guts of the script.
#
#
# Undecided if the venv should be created in the indicatorlunar/tools
# directory only for developer's use, or included in the release...
# If part of the release, can use INdicatorbase process_run...but no access
# to utils venv stuff.
# Is it possible to run the script (within the installed .local/venv_indicators)
# activate venv_indicators and run the internals of the script? 
# Then won't need to install jplephem, etc...should already be installed.


import argparse
import datetime
import subprocess
import sys
import textwrap

from dateutil.relativedelta import relativedelta
from pathlib import Path


if '../' not in sys.path:
    sys.path.insert( 0, '../../' ) # Allows calls to IndicatorBase.

from indicatorbase.src.indicatorbase.indicatorbase import IndicatorBase


def _create_ephemeris_planets_OLD(
    in_bsp,
    out_bsp,
    years ):

    today = datetime.date.today()
    start_date = today - relativedelta( months = 1 )
    end_date = today.replace( year = today.year + years )
    date_format = "%Y/%m/%d"

    command = ""
    if not Path( f"{ IndicatorBase.VENV_INSTALL }" ).is_dir():
        command = f"python3 -m venv { IndicatorBase.VENV_INSTALL } && "

    command += (
        f". { IndicatorBase.VENV_INSTALL }/bin/activate && "
        "python3 -m pip install jplephem && "
        "python3 -m jplephem excerpt "
        f"{ start_date.strftime( date_format ) } "
        f"{ end_date.strftime( date_format ) } "
        f"{ in_bsp } { out_bsp } && deactivate" )

    print( "Processing...\n\t", command )
    result = (
        subprocess.run(
            command,
            shell = True,
            capture_output = True ) )

    stdout_ = result.stdout.decode()
    if stdout_:
        print( stdout_ )

    stderr_ = result.stderr.decode()
    if stderr_ :
        print( stderr_ )


def _create_ephemeris_planets_OLD2(
    in_bsp,
    out_bsp,
    years ):

    today = datetime.date.today()
    start_date = today - relativedelta( months = 1 )
    end_date = today.replace( year = today.year + years )
    date_format = "%Y/%m/%d"

    IndicatorBase.initialise_virtual_environment(
        IndicatorBase.VENV_INSTALL,
        "jplephem",
        force_reinstall = False )

    command = ""
    if not Path( f"{ IndicatorBase.VENV_INSTALL }" ).is_dir():
        command = f"python3 -m venv { IndicatorBase.VENV_INSTALL } && "

    command += (
        f". { IndicatorBase.VENV_INSTALL }/bin/activate && "
        "python3 -m pip install jplephem && "
        "python3 -m jplephem excerpt "
        f"{ start_date.strftime( date_format ) } "
        f"{ end_date.strftime( date_format ) } "
        f"{ in_bsp } { out_bsp } && deactivate" )

    print( command )

    # print( "Processing...\n\t", command )
    # result = (
    #     subprocess.run(
    #         command,
    #         shell = True,
    #         capture_output = True ) )
    #
    # stdout_ = result.stdout.decode()
    # if stdout_:
    #     print( stdout_ )
    #
    # stderr_ = result.stderr.decode()
    # if stderr_ :
    #     print( stderr_ )


def _create_ephemeris_planets(
    in_bsp,
    out_bsp,
    years ):

    today = datetime.date.today()
    start_date = today - relativedelta( months = 1 )
    end_date = today.replace( year = today.year + years )
    date_format = "%Y/%m/%d"

    IndicatorBase.run_python_command_in_virtual_environment(
        IndicatorBase.VENV_INSTALL,
        "python3 -m jplephem excerpt "
        f"{ start_date.strftime( date_format ) } "
        f"{ end_date.strftime( date_format ) } { in_bsp } { out_bsp }",
        "jplephem" )


if __name__ == "__main__":
    description = (
        textwrap.dedent(
            r'''
            From an existing .bsp, create a new .bsp with a date range starting
            one month prior to today, to a specified number of years from today.

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

#TODO Somewhere/somehow (maybe in the above description) mention that the
# date range starts from today minus one month so the input .bsp must have
# data to match the range.

#TODO What happens if the input .bsp does not have data for the end date range?

    parser.add_argument( "in_bsp", help = "The input .bsp file." )

    parser.add_argument(
        "out_bsp", help = "The output .bsp file with reduced date range." )

    parser.add_argument(
        "years",
        help = "The number of years from today to include in the output .bsp." )

    args = parser.parse_args()

    _create_ephemeris_planets( args.in_bsp, args.out_bsp, int( args.years ) )
