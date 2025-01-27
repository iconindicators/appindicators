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
Uninstall one or more indicators, removing the .desktop, run script
and icons and .config/.cache.  Finally, remove the virtual environment
if no more indicators are installed.
'''


import subprocess

import utils


if __name__ == "__main__":
    correct_directory, message = (
        utils.is_correct_directory( example_arguments = "indicatorfortune" ) )

    if correct_directory:
        args = (
            utils.initialiase_parser_and_get_arguments(
                f"Uninstall one or more indicators, including the run script, "
                f"icons, .desktop and .config/.cache. and additionally removing"
                f" the shared virtual environment $HOME/.local/venv_indicators "
                f"if no indicators are installed.",
                ( "indicators", ),
                {
                    "indicators" :
                        "List of indicators, space separated, to uninstall." },
                {
                    "indicators" :
                        "+" } ) )

        for indicator_name in args.indicators:
            command = (
                f"indicator={indicator_name} && " +
                f"venv=$HOME/.local/venv_indicators && " +
                f"$(ls -d ${{venv}}/lib/python3.* | head -1)/site-packages/" +
                f"{indicator_name}/platform/linux/uninstall.sh && " +
                f". ${{venv}}/bin/activate && " +
                f"python3 -m pip uninstall --yes {indicator_name} && " +
                f"count=$(python3 -m pip --disable-pip-version-check list | " +
                f"grep -o \"indicator\" | wc -l) && " +
                f"deactivate && " +
                f"if [ \"$count\" -eq \"0\" ]; then rm -f -r ${{venv}}; fi" )

            subprocess.call( command, shell = True )

    else:
        print( message )
