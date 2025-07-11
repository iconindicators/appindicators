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

from indicatorbase.src.indicatorbase import indicatorbase


# The directory of a .whl release.
RELEASE_DIRECTORY = "release"

# The virtual environment used when building the wheel et al.
VENV_BUILD = "venv_build"


# The virtual environment used when running an indicator.
VENV_RUN = "venv_run"


# The virtual environment into which indicators are installed.
VENV_INSTALL = "$HOME/.local/venv_indicators"


def is_debian11_or_debian12():
    '''
    Return True if running on Debian 11 or Debian 12; False otherwise.
    '''
    etc_os_release = indicatorbase.IndicatorBase.get_etc_os_release()
    return (
        'ID=debian' in etc_os_release
        and (
            'VERSION_ID="11"' in etc_os_release
            or
            'VERSION_ID="12"' in etc_os_release ) )


def is_ubuntu2004_or_is_ubuntu2204_or_ubuntu2404():
    '''
    Return True if running on Ubuntu 20.04 to Ubuntu 24.04, inclusive,
    or derivative distributions.

    False otherwise.
    '''
    etc_os_release = indicatorbase.IndicatorBase.get_etc_os_release()

    is_ubuntu = (
        'ID=ubuntu' in etc_os_release
        and (
            'VERSION_ID="20.04"' in etc_os_release
            or
            'VERSION_ID="22.04"' in etc_os_release
            or
            'VERSION_ID="24.04"' in etc_os_release ) )

    # Linux Mint is different to all other Ubuntu derivatives.
    is_linux_mint = (
        'ID=linuxmint' in etc_os_release
        and (
            'UBUNTU_CODENAME=focal' in etc_os_release
            or
            'UBUNTU_CODENAME=jammy' in etc_os_release
            or
            'UBUNTU_CODENAME=noble' in etc_os_release ) )

    return is_ubuntu or is_linux_mint


def get_pygobject():
    '''
    PyGObject is required for running an indicator.

    On Debian based distributions, the most recent version of PyGObject
    requires libgirepository-2.0-dev, which is only available on
    Ubuntu 24.04+ and Debian 13+.

    For Debian 11/12 and Ubuntu 20.04/22.04/24.04, PyGObject must be pinned
    to version 3.50.1.

    This issue came to light through
        https://github.com/beeware/toga/issues/3143
        https://gitlab.gnome.org/GNOME/pygobject/-/blob/main/NEWS
    '''
    pygobject_needs_to_be_pinned = (
        is_debian11_or_debian12()
        or
        is_ubuntu2004_or_is_ubuntu2204_or_ubuntu2404() )

    if pygobject_needs_to_be_pinned:
        # Escape the < otherwise it will be interpreted as a redirect.
        pygobject = r"PyGObject\<=3.50.1"

    else:
        pygobject = "PyGObject"

    return pygobject


def python_run(
    command,
    venv_directory,
    *modules_to_install,
    force_reinstall = False ):
    '''
    Creates the Python3 virtual environment if it does not exist,
    installs modules specified and runs the Python3 command,
    returning stdout, stderr and the return code as a tuple.

    Note that --force-reinstall could be removed in the future:
        https://github.com/pypa/pip/issues/8238
    '''
    commands = [ ]

    venv_directory_ = venv_directory
    if "$HOME" in venv_directory_:
        venv_directory_ = (
            Path( venv_directory_.replace( "$HOME", '~' ) ).expanduser() )

    if not Path( venv_directory_ ).is_dir():
        commands.append( f"python3 -m venv { venv_directory }" )

    # https://docs.python.org/3/library/venv.html#how-venvs-work
    if sys.prefix == sys.base_prefix:
        commands.append( f". { venv_directory }/bin/activate" )

    if modules_to_install:
        commands.append(
            "python3 -m pip install --upgrade"
            f"{ ' --force-reinstall' if force_reinstall else '' } "
            f"{ ' '.join( modules_to_install ) }" )

    if command:
        commands.append( f"{ command }" )

    if sys.prefix == sys.base_prefix:
        commands.append( "deactivate" )

    command_ = " && ".join( commands )

    print( f"\n\nExecuting command:\n\n{ command_ }\n\n" )

    return indicatorbase.IndicatorBase.process_run( command_ )


def print_stdout_stderr_return_code(
    stdout_,
    stderr_,
    return_code ):
    '''
    Print either stdout or stderr along with the (non-zero) return code.

    Return True if the return code is 0; False otherwise.
    '''
    if return_code == 0:
        print( stdout_ )

    else:
        print( f"\n\nstderr:\n{ stderr_ }" )
        print( f"\n\nReturn code:\n{ return_code }" )

    return return_code == 0


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
    '''
    TODO
    '''
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


def get_indicators_to_process(
    description,
    last_word ):
    ''' Returns the list of indicators on the command line. '''
    return (
        get_arguments(
            description,
            ( "indicators", ),
            {
                "indicators" :
                    f"List of indicators separated by spaces to { last_word }." },
            {
                "indicators" :
                    "+" } ) ).indicators
