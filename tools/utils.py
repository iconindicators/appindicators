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
import sys

from pathlib import Path

if "../" not in sys.path:
    sys.path.insert( 0, "../" )

from indicatorbase.src.indicatorbase import shared


''' The directory of a .whl release. '''
RELEASE_DIRECTORY = "release"

''' The virtual environment used when building the wheel et al. '''
VENV_BUILD = "venv_build"


''' The virtual environment into which indicators are installed. '''
VENV_INSTALL = Path.home() / ".local" / "venv_indicators"


def is_debian11_or_debian12():
    etc_os_release = shared.get_etc_os_release( print_ = True )
    return (
        'ID=debian' in etc_os_release
        and (
            'VERSION_ID="11"' in etc_os_release
            or
            'VERSION_ID="12"' in etc_os_release ) )


def is_ubuntu2004_or_is_ubuntu2204_or_ubuntu2404():
    etc_os_release = shared.get_etc_os_release( print_ = True )
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
        # Need to escape the < otherwise it will be interpreted as a redirect.
        pygobject = r"PyGObject\<=3.50.0"

    else:
        pygobject = "PyGObject"

    return pygobject


def markdown_to_html( markdown, html ):
    # This import, if at the top, will cause the calling function/module
    # to fail as readme_renderer.markdown will not yet have been installed.
    # The caller will first create a virtual environment and install
    # readme_renderer.markdown and then this function may be safely called.
    from readme_renderer.markdown import render
#TODO Given the import above is here and not at the top of the file,
# perhaps create _markdown_to_html.py which contains just this function
# and import.
# How will/would this affect build_wheel (or really _build_wheel)?
    with open( markdown, encoding = "utf-8" ) as f_in:
        with open( html, 'w', encoding = "utf-8" ) as f_out:
            f_out.write( render( f_in.read(), variant = "CommonMark" ) )


def python_run(
    command,
    venv_directory,
    *modules_to_install,
    force_reinstall = False ):  #TODO Is this needed?  Maybe always set to False?
    '''
    Creates the Python3 virtual environment if it does not exist,
    installs modules specified and runs the Python3 command,
    printing to stdout and stderr.
    '''
    command_ = ""
    if not Path( f"{ venv_directory }" ).is_dir():
        command_ += f"python3 -m venv { venv_directory } && "

    command_ += f". { venv_directory }/bin/activate && "

    if len( modules_to_install ):
        command_ += (
            "python3 -m pip install --upgrade "
            f"{ '--force-reinstall' if force_reinstall else '' } "  #TODO Needed?  If not, remove space at end after --upgrade.
            f"{ ' '.join( modules_to_install ) } && " )

    command_ += f"{ command } && deactivate"

    print()
    print( command_ )#TODO Testing.  Maybe make this an option?
    print()

    shared.process_run( command_, print_ = True )


def _get_parser(
    description,
    formatter_class = argparse.ArgumentDefaultsHelpFormatter ):
    '''
    Create an argument parser, setting:
        The program name without the .py extension.
        The usage using including the -m parameter for module.
    '''

    # The module (file) name, without the .py extension.
    module = sys.argv[ 0 ].split( '/' )[ -1 ].split( '.' )[ 0 ]

    return (
        argparse.ArgumentParser(
            prog = module,
            usage = f"python3 -m { module } [options]",
            description = description,
            formatter_class = formatter_class ) )


def get_arguments(
    description,
    argument_names,
    argument_helps = None,
    argument_nargs = None,
    formatter_class = argparse.ArgumentDefaultsHelpFormatter ):

    if argument_helps is None:
        argument_helps = { }

    if argument_nargs is None:
        argument_nargs = { }

    parser = _get_parser( description, formatter_class )

    for argument_name in argument_names:
        parser.add_argument(
            argument_name,
            help = argument_helps.get( argument_name ),
            nargs = argument_nargs.get( argument_name ) )

    return parser.parse_args()


def get_indicators_to_process( description ):
    ''' Returns the list of indicators on the command line. '''
    return (
        get_arguments(
            description,
            ( "indicators", ),
            {
                "indicators" :
                    "The list of indicators separated by spaces to uninstall." },
            {
                "indicators" :
                    "+" } ) ).indicators
