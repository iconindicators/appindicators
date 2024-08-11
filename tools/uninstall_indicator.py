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


# Uninstall a Python wheel package for one or more indicators,
# removing the virtual environment within $HOME/.local and
# icons, .desktop and scripts.",


import subprocess

import utils


#TODO Test this command...maybe print it out first.
def _uninstall( directory_release, indicator_name ):
#TODO Fix this command for 
    command = \
cp --remove-destination INDICATOR_PATH/platform/linux/{indicator_name}_uninstall.sh $HOME/.local/bin && \
        f". $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/platform/linux/post_install.sh"

        f". $HOME/.local/venv_{ indicator_name }/bin/activate && " + \
    
        f" && " + \
        f" && " + \
        f"if [ ! -d $HOME/.local/venv_{ indicator_name } ]; then python3 -m venv $HOME/.local/venv_{ indicator_name }; fi && " + \
        f". $HOME/.local/venv_{ indicator_name }/bin/activate && " + \
        f"python3 -m pip install --upgrade --force-reinstall pip $(ls -d { directory_release }/wheel/dist_{ indicator_name }/{ indicator_name }*.whl | head -1) && " + \
        f"deactivate && " + \
        f". $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/platform/linux/post_install.sh"

    subprocess.call( command, shell = True )


if __name__ == "__main__":
    if utils.is_correct_directory( "./tools/install_wheel.py", "release indicatorfortune" ):
        args = \
            utils.initialiase_parser_and_get_arguments(
                "Uninstall a Python wheel package for one or more indicators, removing the virtual environment within $HOME/.local and icons, .desktop and scripts.",
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
            _uninstall( args.directory_release, indicator_name )

        utils.intialise_virtual_environment( "venv", "pip", "twine" )
