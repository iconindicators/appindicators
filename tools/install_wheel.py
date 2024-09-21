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


# Install a Python wheel package for one or more indicators
# to a virtual environment within $HOME/.local/venv_indicators
# and copies across .desktop, run script and icons.


import subprocess

from pathlib import Path

import utils


if __name__ == "__main__":
    if utils.is_correct_directory( example_arguments = "release indicatorfortune" ):
        args = \
            utils.initialiase_parser_and_get_arguments(
                f"Install a Python wheel package for one or more indicators to "
                f"a virtual environment within $HOME/.local/venv_indicators "
                f"and copies across .desktop, run script and icons.",
                ( "directory_release", "indicators" ),
                {
                    "directory_release" :
                        f"The directory containing the Python wheel. "
                        f"If the directory specified is 'release', "
                        "the Python wheel must be located at 'release/wheel'.",
                    "indicators" :
                        f"The list of indicators (such as indicatorfortune "
                        f"indicatorlunar) to install." },
                {
                    "indicators" :
                        "+" } )

        for indicator_name in args.indicators:
            utils.initialise_virtual_environment(
                Path.home() / ".local" / "venv_indicators",
                f"pip",
                f"$(ls -d { args.directory_release }/wheel/dist_{ indicator_name }/{ indicator_name }*.whl | head -1)" )

            command = f"$(ls -d $HOME/.local/venv_indicators/lib/python3.* | head -1)/site-packages/{indicator_name}/platform/linux/install.sh"

            subprocess.call( command, shell = True )
