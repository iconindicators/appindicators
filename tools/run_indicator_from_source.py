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


''' Run one or more indicators from within the source tree. '''


import sys
import threading

from itertools import compress

from . import utils


indicator_to_dependencies = {
    "indicatorlunar" :
        list( compress(
            [ "ephem", "requests", "sgp4",       "skyfield" ],
            [  True,      True,     True,   sys.maxsize > 2**32 ] ) ),
    "indicatorscriptrunner" :
        [ "requests" ],
    "indicatortide" :
        [ "requests" ] }


if __name__ == "__main__":
    indicators_to_process = (
        utils.get_indicators_to_process(
            f"Run one or more indicators from within the source tree.",
            "install" ) )

    for indicator in indicators_to_process:
        command = (
            "for dirs in indicator*; "
            "do if [ ! -f $dirs/src/$dirs/indicatorbase.py ]; "
            "then ln -sr indicatorbase/src/indicatorbase/indicatorbase.py "
            "$dirs/src/$dirs/indicatorbase.py; fi ; done && "
            "for dirs in indicator*; "
            "do if [ ! -f $dirs/src/$dirs/shared.py ]; "
            "then ln -sr indicatorbase/src/indicatorbase/shared.py "
            "$dirs/src/$dirs/shared.py; fi ; done && "
            f"cd { indicator }/src && "
            f"python3 -m { indicator }.{ indicator }" )

        dependencies = [ "pip", f"{ utils.get_pygobject() }" ]
        if indicator in indicator_to_dependencies:
            dependencies += indicator_to_dependencies[ indicator ]

        threading.Thread(
            target = utils.python_run,
            args = ( command, utils.VENV_RUN, *dependencies ) ).start()
