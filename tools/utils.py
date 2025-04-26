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


''' Functions common to tools. '''


import argparse
import subprocess

from pathlib import Path


# The virtual environment into which indicator are installed,
# either via PyPI or a local wheel.
VENV_INSTALL = "$HOME/.local/venv_indicators"


def initialiase_parser_and_get_arguments(
    description,
    argument_names,
    argument_helps = None,
    argument_nargs = None ):

    if argument_helps is None:
        argument_helps = { }

    if argument_nargs is None:
        argument_nargs = { }

    parser = argparse.ArgumentParser( description = description )
    for argument_name in argument_names:
        parser.add_argument(
            argument_name,
            help = argument_helps.get( argument_name ),
            nargs = argument_nargs.get( argument_name ) )

    return parser.parse_args()


def initialise_virtual_environment(
    venv_directory,
    *modules_to_install ):

    if not Path( venv_directory ).is_dir():
        command = f"python3 -m venv { venv_directory }"
        subprocess.run( command, shell = True, check = False )

    command = (
        f". { venv_directory }/bin/activate && " + \
        f"python3 -m pip install --upgrade --force-reinstall { ' '.join( modules_to_install ) }" )

    subprocess.run( command, shell = True, check = False )
