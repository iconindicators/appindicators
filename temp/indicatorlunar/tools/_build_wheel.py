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
Called by the build wheel process to create the planets.bsp and stars.dat
used in astroskyfield.

It is assumed this script is called from within a Python3 virtual environment.

Running this script on 32 bit will not work correctly; however, the build wheel
will continue without failing.
'''


import gettext
import sys

from datetime import date, timedelta
from pathlib import Path

if '../../' not in sys.path:
    sys.path.insert( 0, '../../' )

from indicatorbase.src.indicatorbase import indicatorbase
from tools import utils

# Needed otherwise '_' will be undefined when importing AstroBase.
gettext.install( "indicatorlunar.tools._build_wheel" )
from indicatorlunar.src.indicatorlunar.astrobase import AstroBase


# The source ephemeris for
#     planets (.bsp)
#     stars (.dat)
# must be present at
#     indicatorlunar/src/indicatorlunar/data
#
# Sources:
#     bsp:
#         https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets
#
#     hip_main.dat:
#         https://cdsarc.cds.unistra.fr/ftp/cats/I/239/hip_main.dat
IN_BSP = "de442s.bsp"
HIP_MAIN_DAT = "hip_main.dat"


def _initialise():
    message = ""
    stdout_, stderr_, return_code = (
        utils.python_run(
            "",
            utils.VENV_BUILD,
            "jplephem" ) )

    if stderr_:
        message = stderr_

    if return_code != 0 and not stderr_:
        # Non-zero return code and stderr is empty,
        # so return the return code.
        message = f"Return code: { return_code }"

    return message


def _create_ephemeris_planets(
    data_path ):
    '''
    Create a planet ephemeris for astroskyfield, from today's date,
    ending at 10 (ten) years from today.

    The start date is wound back one month to take into account the Skyfield
    lunar eclipse algorithm.

    References:
        https://github.com/skyfielders/python-skyfield/issues/123
        https://github.com/skyfielders/python-skyfield/issues/531
    '''
    message = ""
    in_bsp = data_path / IN_BSP
    if in_bsp.exists():
        years_from_today = 10
        today = date.today()
        start_date = today - timedelta( days = 31 )
        end_date = today.replace( year = today.year + years_from_today )
        date_format = "%Y/%m/%d"

        stdout_, stderr_, return_code = (
            utils.python_run(
                f"python3 -m jplephem excerpt "
                f"{ start_date.strftime( date_format ) } "
                f"{ end_date.strftime( date_format ) } "
                f"{ in_bsp } { data_path / 'planets.bsp' }",
                utils.VENV_BUILD ) )

        if stderr_:
            message = stderr_

        if return_code != 0 and not stderr_:
            # Non-zero return code and stderr is empty,
            # so return the return code.
            message = f"Return code: { return_code }"

    else:
        message = f"Cannot locate { in_bsp }"

    return message


def _create_ephemeris_stars(
    data_path ):
    '''
    Create a star ephemeris for astroskyfield.
    '''
    message = ""
    hip_main_dat = data_path / HIP_MAIN_DAT
    if hip_main_dat.exists():
        content = ""
        hips = [ star[ 1 ] for star in AstroBase.STARS ]
        with open( hip_main_dat, 'r', encoding = "utf-8" ) as f:
            for line in f:
                # HIP is located at bytes 9 - 14
                #    http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
                hip = int( line[ 9 - 1 : 14 - 1 + 1 ].strip() )
                if hip in hips:
                    content += line

        indicatorbase.IndicatorBase.write_text_file(
            data_path / "stars.dat",
            content )

    else:
        message = f"Cannot locate { hip_main_dat }"

    return message


def build( out_path ):
    '''
    Called by the build wheel process to build planets.bsp and stars.dat for use
    by astroskyfield.

    Only do the build if astroskyfield is part of the release; otherwise skip.

    Further, the build will only work on 64 bit (based on current understanding)
    because the package numpy, which is used by
        skyfield to create stars.dat
        jplephem to create planets.bsp
    will not install on 32 bit.

    When running on 32 bit, skip building planets.bsp / stars.dat and return
    an empty message so that the build wheel process continues.
    However, emit a warning to the console!
    '''

    manifest_specific_dot_in = (
        Path.cwd() / "indicatorlunar" / "MANIFESTspecific.in" )

    content = (
        indicatorbase.IndicatorBase.read_text_file( manifest_specific_dot_in ) )

    content = ''.join( content )

    message = ""
    if "exclude src/indicatorlunar/astroskyfield.py" not in content:
        if indicatorbase.IndicatorBase.is_64_bit_or_more():
            data_path = Path( out_path ) / "data"
            message = _initialise()
            if not message:
                message = _create_ephemeris_planets( data_path )
                if not message:
                    message = _create_ephemeris_stars( data_path )

        else:
            print(
                "\n\nWARNING: THIS IS A 32 BIT OPERATING SYSTEM,\n"
                "NEITHER PLANETS.BSP NOR STARS.DAT HAVE BEEN BUILT!\n\n" )

    return message
