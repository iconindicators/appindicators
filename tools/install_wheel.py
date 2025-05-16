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


import subprocess

from . import utils


if __name__ == "__main__":
    args = (
        utils.initialiase_parser_and_get_arguments(
            "Install a Python wheel package for one or more indicators to "
            f"a virtual environment within { utils.VENV_INSTALL } "
            "and copy across the .desktop, run script and icons.",
            ( "directory_release", "indicators" ),
            {
                "directory_release" :
                    f"The directory containing the Python wheel. "
                    f"If the directory specified is 'release', "
                    "the Python wheel must be located at 'release/wheel'.",
                "indicators" :
                    f"List of indicators, space separated, to install." },
            {
                "indicators" :
                    "+" } ) )


#TODO Tried to install indicatortest on Ubuntu 24.04 
#into a new .loca/venv_indicators and gi and other packages are not installed...why?
# Need to add PyGObject and packaging to pip below...
# But got some error during install...
#... is that because the pyproject.toml build is locked to an older version of PyGObject?
# Got the error because libgirepository-2.0-dev was not installed.
#
# Another thought; need to change
#
#   "pip",
#
# to
#
#   "pip",
#   "packaging",
#   "PyGObject",
#
# but PyGObject may need to be pinned depending on the version of Ubuntu.
# How to make this script do that automatically...or at least check
# and abort if wrong version?
#
# BIGGER QUESTION: Need a big print at the start of this script (and others???)
# stating that the build/install will only work on Ubuntu?
# That is bad...!
    for indicator_name in args.indicators:
        utils.initialise_virtual_environment(
            utils.VENV_INSTALL,
            "pip",
            f"$(ls -d { args.directory_release }/wheel/dist_{ indicator_name }/{ indicator_name }*.whl | head -1)",
            force_reinstall = True )

        command = (
            f"$(ls -d { utils.VENV_INSTALL }/lib/python3.* | " +
            f" head -1)/site-packages/{ indicator_name }/platform/" +
            "linux/install.sh" )

        subprocess.run( command, shell = True, check = False )
