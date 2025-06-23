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
'''


#TODO 
# Will need a main
# https://stackoverflow.com/questions/59703821/import-module-without-running-it
# in the files/modules that create planets/stars
#
# Given importing a module will run that module unless there is a __main__,
# check all the scripts with a _ in tools and lunar/tools.  
# See if _build_wheel.py is being run twice by build_wheel.py.
#
# Check all scripts in tools or indicatorlunar/tools.


#TODO This will unlikely not work on 32 bit due to numpy et al...
# so maybe put in a check to not run this script on 32 bit (just pass).
# But somehow need to let the user know without passing a message back which
# causes the build to abort.

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


import datetime
import gettext
import sys

from pathlib import Path

if '../../' not in sys.path:  #TODO Check that the path here matches the path in the next line for all scripts/places.
    sys.path.insert( 0, '../../' )

from tools import utils

# Needed otherwise '_' will be undefined when importing AstroBase.  
gettext.install( "indicatorlunar.tools._build_wheel" )
from indicatorlunar.src.indicatorlunar.astrobase import AstroBase 


'''
The source ephemeris for planets (.bsp) and stars (.dat)
which must be present at
    indicatorlunar/src/indicatorlunar/data

Sources:
    bsp:
        https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets
    
    hip_main.dat:
        https://cdsarc.cds.unistra.fr/ftp/cats/I/239/hip_main.dat
'''
IN_BSP = "de442s.bsp"
HIP_MAIN_DAT = "hip_main.dat" 


def _initialise():
    ''' Install dependencies into the Python3 virtual environment. '''
    command = "python3 -m pip install --upgrade jplephem python-dateutil skyfield"
    message = ""
    stdout_, stderr_, return_code = (
        utils.python_run(
            command,
            utils.VENV_BUILD,
            activate_deactivate = False ) )

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

        # Must import this here rather than the top.
        #
        # If the virtual environment does not have python-dateutil installed
        # at run-time, the import will fail.
        from dateutil.relativedelta import relativedelta #TODO Comment why this is here.

        today = datetime.date.today()
        start_date = today - relativedelta( months = 1 )
        end_date = today.replace( year = today.year + years_from_today )
        date_format = "%Y/%m/%d"

        command = (
            f"python3 -m jplephem excerpt "
            f"{ start_date.strftime( date_format ) } "
            f"{ end_date.strftime( date_format ) } "
            f"{ in_bsp } { data_path / 'planets.bsp' }" )

        stdout_, stderr_, return_code = (
            utils.python_run(
                command,
                utils.VENV_BUILD,
                activate_deactivate = False ) )

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
    ''' Create a star ephemeris for astroskyfield. '''
    message = ""
    hip_main_dat = data_path / HIP_MAIN_DAT
    if hip_main_dat.exists():

        # Must import this here rather than the top.
        #
        # If the virtual environment does not have skyfield installed
        # at run-time, the import will fail.
        from skyfield.api import load

        hips = [ star[ 1 ] for star in AstroBase.STARS ]
        with load.open( str( hip_main_dat ), 'r' ) as f_in:
            with open( data_path / "stars.dat", 'w' ) as f_out:
                for line in f_in:
                    # HIP is located at bytes 9 - 14
                    #    http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
                    hip = int( line[ 9 - 1 : 14 - 1 + 1 ].strip() )
                    if hip in hips:
                        f_out.write( line )

    else:
        message = f"Cannot locate { hip_main_dat }"

    return message


def build( out_path ):
    ''' Called by the build wheel process. '''
    if True: return "" #TODO Remove this line if including astroskyfield et al.
    
    message = ""

    # On 32 bit, numpy, used by skyfield and jplephem to create stars.dat and
    # planets.bsp respectively, will not install, so skip.
    #
    # https://stackoverflow.com/a/9964440/2156453
    # https://docs.python.org/3/library/platform.html#cross-platform
    # https://docs.python.org/3/library/sys.html#sys.maxsize
    if sys.maxsize > 2**32:
        data_path = Path( out_path ) / "data"
        message = _initialise()
        if not message:
            message = _create_ephemeris_planets( data_path )
            if not message:
                message = _create_ephemeris_stars( data_path )

    else:
        print(
            "WARNING: THIS IS A 32 BIT OPERATING SYSTEM,\n"
            "NEITHER PLANETS.BSP NOR STARS.DAT HAVE BEEN BUILT!" )

    return message
