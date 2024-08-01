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


# Upload the Python wheel for an indicator to PyPI.
#
#   https://twine.readthedocs.io/en/latest/
#   https://packaging.python.org/en/latest/tutorials/packaging-projects/


import subprocess

import utils


if __name__ == "__main__":
    if utils.is_correct_directory( "./tools/upload_wheel.py", "release/wheel/dist_indicatorfortune" ):
        args = \
            utils.initialiase_parser_and_get_arguments(
                "Upload to PyPI a Python .whl/.tar.gz for an indicator.",
                ( "directory_dist", ),
                { "directory_dist" : "The directory containing the indicator's .whl/.tar.gz (and NO OTHER FILES)." } )

        utils.intialise_virtual_environment( "pip", "twine" )

        print( "(the password starts with 'pypi-')" )
        command = \
            f". ./venv/bin/activate && " + \
            f"python3 -m twine upload --username __token__ { args.directory_dist }/*"

        subprocess.call( command, shell = True )
