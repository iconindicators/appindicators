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


# Functions common to scripts.


import argparse
import configparser
import re
import stat
import subprocess

from pathlib import Path


def _chmod( file, user_permission, group_permission, other_permission ):
    Path( file ).chmod( user_permission | group_permission | other_permission )


def _create_pyproject_dot_toml( indicator_name, directory_out ):
    indicator_pyproject_toml = Path( '.' ) / indicator_name / "pyproject.toml"

    config = configparser.ConfigParser()
    with open( indicator_pyproject_toml ) as stream:
        config.read_string( "[top]\n" + stream.read() ) 

    version = config[ "top" ][ "version" ].replace( '\"', '' ).strip()

    # The description may contain a ' which must be replaced with "
    # as it causes an error when parsing the pyproject.toml.
    description = config[ "top" ][ "description" ].replace( '\"', '' ).replace( '\'', '\"' ).strip()

    classifiers = config[ "top" ][ "classifiers" ].replace( '[', '' ).replace( ']', '' ).strip()
    classifiers = ',\n' + re.sub( "^", "  ", classifiers, flags = re.M )

    dependencies = ""
    if "dependencies" in config[ "top" ]:
        dependencies = config[ "top" ][ "dependencies" ].replace( '[', '' ).replace( ']', '' ).strip()
        dependencies = ',\n' + re.sub( "^", "  ", dependencies, flags = re.M )

    indicatorbase_pyproject_toml = Path( '.' ) / "indicatorbase" / "pyprojectbase.toml"
    text = ""
    with open( indicatorbase_pyproject_toml ) as f:
        for line in f:
            if not line.startswith( '#' ):
                text += line

    text = text.replace( "{classifiers}", classifiers )
    text = text.replace( "{dependencies}", dependencies )
    text = text.replace( "{indicator_name}", indicator_name )

    text = \
        text.replace(
        "[project]", 
        "[project]\n" + \
        "name = \'" + indicator_name + '\'\n' + \
        "version = \'" + version + '\'\n' + \
        "description = \'" + description + '\'' )

    out_pyproject_toml = directory_out / "pyproject.toml"
    with open( out_pyproject_toml, 'w' ) as f:
        f.write( text + '\n' )

    _chmod(
        out_pyproject_toml,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )


def get_values_from_pyproject_toml( pyproject_dot_toml, keys ):
    config = configparser.ConfigParser()
    config.read( pyproject_dot_toml )
    keys_and_values = { }
    for key in keys:
        keys_and_values[ key[ 1 ] ] = config[ key[ 0 ] ][ key[ 1 ] ]

    return keys_and_values


def is_correct_directory( script_path_and_name, script_example_arguments ):
    correct_directory = Path( script_path_and_name ).exists()
    if not correct_directory:
        print(
            f"The script must be run from the top level directory (one above tools).\n"
            f"For example:\n"
            f"\tpython3 { script_path_and_name } { script_example_arguments }" )

    return correct_directory


def initialiase_parser_and_get_arguments(
        description,
        argument_names,
        argument_helps = { },
        argument_nargs = { } ):

    parser = argparse.ArgumentParser( description = description )
    for argument_name in argument_names:
        parser.add_argument(
            argument_name,
            help = argument_helps.get( argument_name ),
            nargs = argument_nargs.get( argument_name ) )

    return parser.parse_args()


def intialise_virtual_environment( *modules_to_install ):
    if not Path( "venv" ).is_dir():
        command = f"python3 -m venv venv"
        subprocess.call( command, shell = True )

    command = \
        f". ./venv/bin/activate && " + \
        f"python3 -m pip install --upgrade { ' '.join( modules_to_install ) }"

    subprocess.call( command, shell = True )
