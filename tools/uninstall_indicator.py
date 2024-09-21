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
# $HOME/.local/venv_indicators and .desktop, run script and icons and
# .config/.cache.


import subprocess

import utils


#TODO Need to fix this according to now using a single venv.
if __name__ == "__main__":
    if utils.is_correct_directory( example_arguments = "indicatorfortune" ):
        args = \
            utils.initialiase_parser_and_get_arguments(
                f"Uninstall one or more indicators, including the run script, "
                f"icons, .desktop and .config/.cache. and additionally removing ",
                f"the shared virtual environment $HOME/.local/venv_indicators "
                f"if no indicators are installed.",
                ( "indicators", ),
                {
                    "indicators" :
                        "The list of indicators (such as indicatorfortune indicatorlunar) to uninstall." },
                {
                    "indicators" :
                        "+" } )

        for indicator_name in args.indicators:
            command = \
                f"indicator={indicator_name} && " + \
                f"venv=$HOME/.local/venv_indicators && " + \
                f"$(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator_name}/platform/linux/uninstall.sh && " + \
                . ${venv}/bin/activate && \
                python3 -m pip uninstall --yes ${indicator_name} && \
                count=$(python3 -m pip --disable-pip-version-check list | grep -o "indicator" | wc -l) ; if [ "$count" -eq "0" ]; then rm -f -r ${venv}; fi && \
                deactivate

                
                f"$(ls -d $HOME/.local/venv_{indicator_name}/lib/python3.* | head -1)/site-packages/{indicator_name}/platform/linux/uninstall.sh && " + \
                f"rm -f -r $HOME/.local/venv_{indicator_name}"

            subprocess.call( command, shell = True )
