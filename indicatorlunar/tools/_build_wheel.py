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
TODO Fix this comment
Utility for building a Python3 wheel.

  *** NOT TO BE RUN DIRECTLY ***
'''


import datetime
import sys

from pathlib import Path

if '../../' not in sys.path:  #TODO Check that the path here matches the path in the next line for all scripts/places.
    sys.path.insert( 0, '../../' )

from tools import utils



#TODO Check all of this below...comment too.
# Needed to get over the _ definition not in astrobase.
if '../../' not in sys.path:
    sys.path.insert( 0, '../../' )

import gettext
_ = gettext.gettext

gettext.install( "text" )

from indicatorlunar.src.indicatorlunar.astrobase import AstroBase 



def _create_ephemeris_planets(
    out_path ):

    print( "Finally here")
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

    print( f"Creating stars.dat for astroskyfield..." )
    message = ""
    hip_main_dot_dat = "indicatorlunar/src/indicatorlunar/data/hip_main.dat" #TODO Comment similarly to de442s.bsp
    if Path( hip_main_dot_dat ).exists():
        hips = [ star[ 1 ] for star in AstroBase.STARS ]
        #TODO Comment why these are here and not at top
        from skyfield.api import load

        stars_dot_dat = out_path / "stars.dat"

        with load.open( hip_main_dot_dat, 'r' ) as f_in, open( stars_dot_dat, 'w' ) as f_out:
            for line in f_in:
                # HIP is located at bytes 9 - 14
                #    http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
                hip = int( line[ 9 - 1 : 14 - 1 + 1 ].strip() )
                if hip in hips:
                    f_out.write( line )
    else:
        message = f"Cannot locate { hip_main_dot_dat }"

    return message


# def create_ephemeris_stars(
#     output_filename_for_skyfield_star_ephemeris,
#     planet_ephemeris,
#     star_ephemeris,
#     iau_catalog_file ):
#
#     _create_ephemeris_skyfield(
#         output_filename_for_skyfield_star_ephemeris,
#         star_ephemeris,
#         list( names_to_hips.values() ) )




def build( out_path ):
    print( "indicator build script")
    message = ""

    out_path_ = Path( out_path ) / "data"
    if not Path( out_path_ ).exists():
        out_path_.mkdir( parents = True )

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
