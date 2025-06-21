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


def _create_ephemeris_planets( out_path ):
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

        out_path_ = Path( out_path ) / "data"
        if not Path( out_path_ ).exists():
            out_path_.mkdir( parents = True )

        out_bsp = out_path_ / "planets.bsp"

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


def build( out_path ):
    print( "indicator build script")
    message = ""

    # Build planets.bsp
    command = "python3 -m pip install --upgrade jplephem python-dateutil"
    stdout_, stderr_, return_code = (
        utils.python_run(
            command,
            utils.VENV_BUILD,
            activate_deactivate = False ) )

    if stderr_:
        message = stderr_

    if return_code == 0:
        message = _create_ephemeris_planets( out_path )
        if not message:
            print( "build stars!!!!!!!!!!!!!!!!!!!!!!!!!!!!") #TODO Build stars.dat
            # message = _create_ephemeris_stars( out_path )

    else:
        # Non-zero return code indicating an error.
        # If stderr is empty, use the return code as the returned message.
        if not stderr_:
            message = f"Return code: { return_code }"

    return message
