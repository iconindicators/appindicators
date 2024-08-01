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
# to a virtual environment within $HOME/.local.


import subprocess

import utils


def _install_wheel_for_indicator( directory_release, indicator_name ):
    command = \
        f"if [ ! -d $HOME/.local/venv_{ indicator_name } ]; then python3 -m venv $HOME/.local/venv_{ indicator_name }; fi && " + \
        f". $HOME/.local/venv_{ indicator_name }/bin/activate && " + \
        f"python3 -m pip install --upgrade --force-reinstall pip $(ls -d { directory_release }/wheel/dist_{ indicator_name }/{ indicator_name }*.whl | head -1) && " + \
        f"deactivate && " + \
        f"mkdir -p $HOME/.local/bin && " + \
        f"cp --remove-destination $(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/platform/linux/{ indicator_name }.sh $HOME/.local/bin && " + \
        f"mkdir -p $HOME/.local/share/applications && " + \
        f"cp --remove-destination $(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/platform/linux/{ indicator_name }.py.desktop $HOME/.local/share/applications && " + \
        f"mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps && " + \
        f"cp --remove-destination $(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/icons/*.svg $HOME/.local/share/icons/hicolor/scalable/apps"

    subprocess.call( command, shell = True )


if __name__ == "__main__":
    if utils.is_correct_directory( "./tools/install_wheel.py", "release indicatorfortune" ):
        args = \
            utils.initialiase_parser_and_get_arguments(
                "Install a Python wheel package for one or more indicators to a virtual environment within $HOME/.local.",
                ( "directory_release", "indicators" ),
                {
                    "directory_release" :
                        "The directory containing the Python wheel. " +
                        "If the directory specified is 'release', " +
                        "the Python wheel must be located at 'release/wheel'.",
                    "indicators" :
                        "The list of indicators (such as indicatorfortune indicatorlunar) to install." },
                {
                    "indicators" :
                        "+" } )

        for indicator_name in args.indicators:
            _install_wheel_for_indicator( args.directory_release, indicator_name )

        utils.intialise_virtual_environment( "pip", "twine" )
