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


#TODO Why is 'release' still needed as a parameter to the tools?
# 'release' should be made as the location where releases are always located.


import argparse
import sys

from pathlib import Path

if '../' not in sys.path:
    sys.path.insert( 0, '../' ) # Allows calls to IndicatorBase.

from indicatorbase.src.indicatorbase.indicatorbase import IndicatorBase


# The directory of a .whl release.
RELEASE_DIRECTORY = "release"


# The virtual environment into which indicators are installed,
# via PyPI or a local wheel.
VENV_INSTALL = "$HOME/.local/venv_indicators"


def is_debian11_or_debian12():
    etc_os_release = IndicatorBase.get_etc_os_release( print_ = True )
    return (
        'ID=debian' in etc_os_release
        and (
            'VERSION_ID="11"' in etc_os_release
            or
            'VERSION_ID="12"' in etc_os_release ) )


def is_ubuntu2004_or_is_ubuntu2204_or_ubuntu2404():
    etc_os_release = IndicatorBase.get_etc_os_release( print_ = True )
    return ( (
        'ID=ubuntu' in etc_os_release and (
            'VERSION_ID="20.04"' in etc_os_release
            or
            'VERSION_ID="22.04"' in etc_os_release
            or
            'VERSION_ID="24.04"' in etc_os_release ) )
        or (
        'ID=linuxmint' in etc_os_release and (
            'UBUNTU_CODENAME=focal' in etc_os_release
            or
            'UBUNTU_CODENAME=jammy' in etc_os_release
            or
            'UBUNTU_CODENAME=noble' in etc_os_release ) ) )


def get_pygobject():
    '''
    PyGObject is required for running an indicator.

    On Debian based distributions, the most recent version of PyGObject
    requires libgirepository-2.0-dev, which is only available on Ubuntu 24.04+
    and Debian 13+.

    On Debian 11/12 and Ubuntu 20.04/22.04/24.04, which only have available
    libgirepository1.0-dev, PyGObject must be pinned to version 3.50.0.
    '''
    pygobject_needs_to_be_pinned = (
        is_debian11_or_debian12()
        or
        is_ubuntu2004_or_is_ubuntu2204_or_ubuntu2404() )

    if pygobject_needs_to_be_pinned:
        pygobject = r"PyGObject\<=3.50.0"

    else:
        pygobject = "PyGObject"

    return pygobject


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


def get_indicators_to_process( description ):
    return (
        initialiase_parser_and_get_arguments(
            description,
            ( "indicators", ),
            {
                "indicators" :
                    "The list of indicators separated by spaces to uninstall." },
            {
                "indicators" :
                    "+" } ) ).indicators


def initialise_virtual_environment(
    venv_directory,
    *modules_to_install,
    force_reinstall = False ):

    if not Path( venv_directory ).is_dir():
        IndicatorBase.process_run(
            f"python3 -m venv { venv_directory }", 
            capture_output = False,
            print_ = True )

    IndicatorBase.process_run(
        f". { venv_directory }/bin/activate && "
        "python3 -m pip install --upgrade "
        f"{ '--force-reinstall' if force_reinstall else '' } "
        f"{ ' '.join( modules_to_install ) }",
        capture_output = False,
        print_ = True )
