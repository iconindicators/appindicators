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
Called by the build wheel process.

Creates the planets.bsp and stars.dat used in astroskyfield.
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


def _create_ephemeris_planets(
    out_path ):
    '''
    TODO NEED ANY OF THIS?
Create a planet ephemeris for astroskyfield, from today's date,
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


            Ensure that the existing .bsp contains data from
                "one month before today"
            up to
                "today plus the specified years"

    '''
    message = ""

    #TODO DOcument 
    in_bsp = "indicatorlunar/src/indicatorlunar/data/de442s.bsp"#TODO Leave as is?  Cannot really be passed in...
    if Path( in_bsp ).exists():
        years_from_today = 10 #TODO Add a comment

        from dateutil.relativedelta import relativedelta #TODO Comment why this is here.

        today = datetime.date.today()
        start_date = today - relativedelta( months = 1 )  #TODO Explain this
        end_date = today.replace( year = today.year + years_from_today )
        date_format = "%Y/%m/%d"

        out_bsp = out_path / "planets.bsp"

        command = (
            f"python3 -m jplephem excerpt { start_date.strftime( date_format ) } "
            f"{ end_date.strftime( date_format ) } { in_bsp } { out_bsp }" )

        # print( command ) #TODO Test

        stdout_, stderr_, return_code = (
            utils.python_run(
                command,
                utils.VENV_BUILD,
                activate_deactivate = False ) )

        if stderr_:
            print( f"THIS IS STDERR PLANETS: { stderr_ }" )#TODO Test
            message = stderr_

        if return_code != 0 and not stderr_:
            # Non-zero return code and stderr is empty,
            # so return the return code.
            message = f"Return code: { return_code }"

    else:
        message = f"Cannot locate { in_bsp }"

    return message


def _create_ephemeris_stars(
    out_path ):
    '''
    TODO Need any of this:
    
                "iau_catalog_file":
                    "A text file containing the list of stars, downloaded from " +
                    "http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt",
                "star_ephemeris":
                    "A star ephemeris file, typically hip_main.dat, downloaded from " +
                    "https://cdsarc.cds.unistra.fr/ftp/cats/I/239",
                "planet_ephemeris":
                    "A planet ephemeris file in .bsp format, downloaded from " +
                    "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets",
                "output_filename_for_astroskyfield_star_ephemeris":
                    "The output filename for the astroskyfield star ephemeris." },
    
    '''
    print( f"Creating stars.dat for astroskyfield..." )
    message = ""
    hip_main_dot_dat = "indicatorlunar/src/indicatorlunar/data/hip_main.dat" #TODO Comment similarly to de442s.bsp
    if Path( hip_main_dot_dat ).exists():
        hips = [ star[ 1 ] for star in AstroBase.STARS ]
        #TODO Comment why these are here and not at top
        from skyfield.api import load
#TODO I think I have forgotten to pip install skyfield as I have for jplephem in planets.

        stars_dot_dat = out_path / "stars.dat"

        with load.open( hip_main_dot_dat, 'r' ) as f_in, open( stars_dot_dat, 'w' ) as f_out:
            for line in f_in:
                # HIP is located at bytes 9 - 14
                #    http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
                hip = int( line[ 9 - 1 : 14 - 1 + 1 ].strip() )
                if hip in hips:
                    f_out.write( line )

        message = "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"

    else:
        message = f"Cannot locate { hip_main_dot_dat }"

    return message


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

def build( out_path ):
    '''
    Creates the 
    '''

    message = ""

    out_path_ = Path( out_path ) / "data"
    if not Path( out_path_ ).exists():
        out_path_.mkdir( parents = True )

#TODO Why is this done here outside of create_planets?
# Can it be moved into create_planets and combined into one call along with jplephem excerpt?
#
# BUT...stars needs skfyfield, so could leave out here and add skyfield.
    command = "python3 -m pip install jplephem python-dateutil" #TODO replace with below
    # command = "python3 -m pip install --upgrade jplephem python-dateutil"
    stdout_, stderr_, return_code = (
        utils.python_run(
            command,
            utils.VENV_BUILD,
            activate_deactivate = False ) )

    if stderr_:
        message = stderr_

    if return_code == 0:
        message = _create_ephemeris_planets( out_path_ )
        if not message:
            print( "build stars!!!!!!!!!!!!!!!!!!!!!!!!!!!!") #TODO Build stars.dat
            message = _create_ephemeris_stars( out_path_ )
        else:
            print( "THERE IS A MESSAFE")

    else:
        # Non-zero return code indicating an error.
        # If stderr is empty, use the return code as the returned message.
        if not stderr_:
            message = f"Return code: { return_code }"

    return message
