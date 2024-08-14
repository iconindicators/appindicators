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


# Uninstall one or more indicators, removing the virtual environment
# within $HOME/.local and .desktop, run script and icons and .config/.cache.


import subprocess

import utils


if __name__ == "__main__":
    if utils.is_correct_directory( "./tools/uninstall_indicator.py", "indicatorfortune" ):
        args = \
            utils.initialiase_parser_and_get_arguments(
                "Uninstall one or more indicators, removing the virtual environment within $HOME/.local and .desktop, run script and icons and .config/.cache.",
                ( "indicators", ),
                {
                    "indicators" :
                        "The list of indicators (such as indicatorfortune indicatorlunar) to uninstall." },
                {
                    "indicators" :
                        "+" } )

        for indicator_name in args.indicators:
            command = \
                f"$(ls -d $HOME/.local/venv_{indicator_name}/lib/python3.* | head -1)/site-packages/{indicator_name}/platform/linux/uninstall.sh && " + \
                f"rm -f -r $HOME/.local/venv_{indicator_name}"

            subprocess.call( command, shell = True )
