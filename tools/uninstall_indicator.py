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


#TODO Test this.


'''
Uninstall one or more indicators, including the .desktop, run script, icons,
.config and .cache.

Remove the virtual environment if no further indicators are installed.
'''


import sys

if "../" not in sys.path:
    sys.path.insert( 0, "../" ) # Allows calls to IndicatorBase.

from indicatorbase.src.indicatorbase.indicatorbase import IndicatorBase

from . import utils


if __name__ == "__main__":
    indicators_to_process = (
        utils.get_indicators_to_process(
            f"Uninstall one or more indicators, from the Python3 virtual "
            f"environment at { IndicatorBase.VENV_INSTALL } including the "
            ".desktop, run script, icons, .config and .cache.  "
            "If all indicators have been uninstalled, the virtual environment "
            "will also be removed." ) )

#TODO Test on Ubuntu 20.04
#TODO Test on Debian 32 bit
    for indicator in indicators_to_process:
        #TODO Could/should the command be split into 3:
        #    Run process to run uninstall.sh
        #    Run python pip uninstall
        #    Remove venv install dir
        # Would need to check return value on each and only call next on success.
        # Only need to do the check for no more indicators once.
        command = (
            f"$(ls -d { IndicatorBase.VENV_INSTALL }/lib/python3.* | head -1)/"
            f"site-packages/{ indicator }/platform/linux/uninstall.sh && "
            f". { IndicatorBase.VENV_INSTALL }/bin/activate && "
            f"python3 -m pip uninstall --yes { indicator } && "
            f"count=$(python3 -m pip --disable-pip-version-check list | "
            f"grep -o \"indicator\" | wc -l) && "
            f"deactivate && "
            f"if [ \"$count\" -eq \"0\" ]; "
            f"then rm -f -r { IndicatorBase.VENV_INSTALL }; fi" )

        IndicatorBase.python_run( command, IndicatorBase.VENV_INSTALL )
