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

if '../../' not in sys.path:  #TODO Check that the path here matches the path in the next line for all occurrences.
    sys.path.insert( 0, '../../' )

from tools import utils


def _create_ephemeris_planets( out_path ):
    print( "Finally here")
    message = ""

    #TODO DOcument 
    in_bsp = "indicatorlunar/src/indicatorlunar/data/de442s.bsp"#TODO Leave as is?  Cannot really be passed in...
    if not Path( in_bsp ).exists():
        message = f"Cannot locate { in_bsp }"

    if not message:
        years_from_today = 10

        out_path_ = Path( out_path ) / "data"
        if not Path( out_path_ ).exists():
            out_path_.mkdir( parents = True )

        out_bsp = out_path_ / "planets.bsp"

        from dateutil.relativedelta import relativedelta #TODO Comment why this is here.
        today = datetime.date.today()
        start_date = today - relativedelta( months = 1 )
        end_date = today.replace( year = today.year + years_from_today )
        date_format = "%Y/%m/%d"

        command = (
            f"python3 -m jplephem excerpt { start_date.strftime( date_format ) } "
            f"{ end_date.strftime( date_format ) } { in_bsp } { out_bsp }" )

        print( command ) #TODO Test

        stdout_, stderr_, return_code = (
            utils.python_run(
                command,
                utils.VENV_BUILD,
                activate_deactivate = False ) )

        if stdout_:
            message = f"THIS IS STDOUT PLANETS: { stdout_ }"
            # message = stdout_

        if stderr_:
            message = f"THIS IS STDERR PLANETS: { stderr_ }"
            # message = stderr_

        print( f"Return code PLANETS: { return_code }")

#TODO Not sure if the text emitted when making planets.bsp which is all good
# should be passed back as a message.
# When all good, want an empty message.
# So maybe check for the return code being 0?
# If not 0, then return what? stdout or stderr?

    return message


def build( out_path ):
    print( "indicator build script")
    message = ""

    #TODO Delete eventually
    # command = (
    #     "python3 -m pip install --upgrade jplephem python-dateutil && "
    #     "python3 -c \"from indicatorlunar.tools import _create_ephemeris_planets; "
    #     f"_create_ephemeris_planets.create_ephemeris_planets( \\\"{ out_path }\\\" )\"" )

    # Build planets.bsp
    command = "python3 -m pip install --upgrade jplephem python-dateutil"
    stdout_, stderr_, return_code = (
        utils.python_run( command, utils.VENV_BUILD ) )

    if stdout_:
        # message = f"THIS IS STDOUT INSTALL: { stdout_ }"
        pass
        # message = stdout_

    if stderr_:
        message = f"THIS IS STDERR INSTALL: { stderr_ }"
        # message = stderr_

    # if return_code == 0:
    #     message = _create_ephemeris_planets( out_path )
    #     if not message:
    #         pass #TODO Create stars.dat
    #         # message = _create_ephemeris_stars( out_path )

    print( f"Return code INSTALL: { return_code }")

    return message
