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
Install a wheel for one or more indicators to a virtual environment at
$HOME/.local/venv_indicators and then run install.sh.
'''


import sys

if '../' not in sys.path:
    sys.path.insert( 0, '../' ) # Allows calls to IndicatorBase.

from indicatorbase.src.indicatorbase.indicatorbase import IndicatorBase

from . import utils


if __name__ == "__main__":
    indicators_to_process = (
        utils.get_indicators_to_process(
            f"Install a Python3 wheel for one or more indicators, at "
            f"{ utils.RELEASE_DIRECTORY }, into a Python3 virtual environment "
            f"at { utils.VENV_INSTALL } and copy across the .desktop, run "
            "script and icons." ) )

    utils.initialise_virtual_environment(
        utils.VENV_INSTALL,
        "pip",
        utils.get_pygobject() )

    for indicator in indicators_to_process:
        utils.initialise_virtual_environment(
            utils.VENV_INSTALL,
            f"$(ls -d { utils.RELEASE_DIRECTORY }/wheel/dist_{ indicator }/{ indicator }*.whl | head -1)",
            force_reinstall = True )

        IndicatorBase.process_run(
            f"$(ls -d { utils.VENV_INSTALL }/lib/python3.* | " +
            f" head -1)/site-packages/{ indicator }/platform/" +
            "linux/install.sh",
            capture_output = False,
            print_ = True )
