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
Uninstall one or more indicators, including the .desktop, run script, icons,
.config and .cache.

Remove the virtual environment if no further indicators are installed.
'''


from . import utils


if __name__ == "__main__":
    indicators_to_process = (
        utils.get_indicators_to_process(
            f"Uninstall one or more indicators, from the Python3 virtual "
            f"environment at { utils.VENV_INSTALL } including the "  #TODO This can be $HOME
            ".desktop, run script, icons, .config and .cache.  "
            "If all indicators have been uninstalled, the virtual environment "
            "will also be removed.",
            "uninstall" ) )

#TODO Test on Debian 32 bit
    for indicator in indicators_to_process:
        command = (
            f"$(ls -d { utils.VENV_INSTALL }/lib/python3.* | head -1)/"  #TODO This can be $HOME
            f"site-packages/{ indicator }/platform/linux/uninstall.sh && "
            f"python3 -m pip uninstall --yes { indicator } && "
            f"count=$(python3 -m pip --disable-pip-version-check list | "
            f"grep -o \"indicator\" | wc -l) && "
            f"if [ \"$count\" -eq \"0\" ]; "
            f"then rm -f -r { utils.VENV_INSTALL }; fi" )

        utils.python_run( command, utils.VENV_INSTALL )
