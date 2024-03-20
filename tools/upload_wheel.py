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


import argparse
import subprocess

from pathlib import Path


def _initialise_parser():
    parser = argparse.ArgumentParser(
        description = "Upload to PyPI a Python .whl/.tar.gz for an indicator." )

    parser.add_argument(
        "directory_dist",
        help = "The directory containing the indicator's .whl/.tar.gz (and NO OTHER FILES)." )

    return parser


if __name__ == "__main__":
    parser = _initialise_parser()
    script_path_and_name = "tools/upload_wheel.py"
    if Path( script_path_and_name ).exists():
        args = parser.parse_args()
        command = \
            "python3 -m venv venv && " + \
            ". ./venv/bin/activate && " + \
            "python3 -m pip install --upgrade pip twine"

        subprocess.call( command, shell = True )

        print( "(the password starts with 'pypi-')" )
        command = \
            f". ./venv/bin/activate && " + \
            f"python3 -m twine upload --username __token__ { args.directory_dist }/*"

        subprocess.call( command, shell = True )

    else:
        print(
            f"The script must be run from the top level directory (one above utils).\n"
            f"For example:\n"
            f"\tpython3 { script_path_and_name } release/wheel/dist_indicatorfortune" )
