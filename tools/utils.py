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


''' Functions common to scripts. '''


import argparse
import inspect
import subprocess

from pathlib import Path


def is_correct_directory(
    example_arguments = None ):
    correct_directory = (
        Path.cwd()
        ==
        Path( inspect.stack()[ 1 ].filename ).parent.parent.absolute() )

    message = ""
    if not correct_directory:
        path_of_caller_parts = Path( inspect.stack()[ 1 ].filename ).parts
        script_path_and_name = (
            Path( '.' ) / path_of_caller_parts[ -2 ] / path_of_caller_parts[ -1 ] )

        message = (
            f"The script must be run from the top level directory (one above tools).\n"
            f"For example:\n"
            f"\tpython3 { script_path_and_name } { '' if example_arguments is None else example_arguments }" )

    return correct_directory, message


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

    if not venv_directory.is_dir():
        command = f"python3 -m venv { venv_directory }"
        subprocess.call( command, shell = True )

    command = (
        f". { venv_directory.absolute() / 'bin' / 'activate' } && " + \
        f"python3 -m pip install --upgrade --force-reinstall { ' '.join( modules_to_install ) }" )

    subprocess.call( command, shell = True )
