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


# Build a Python Wheel package for one or more indicators.
#
# To view the contents of a .whl:
#    unzip -l indicatortest-1.0.7-py3-none-any.whl
#
# To view the contents of a .tar.gz:
#    tar tf indicatortest-1.0.7.tar.gz


import argparse
import os
import re
import shutil
import stat
import subprocess
import sys

from pathlib import Path

sys.path.append( "indicatorbase/src" )
try:
    from indicatorbase import indicatorbase
except ModuleNotFoundError:
    pass # Occurs as the script is run from the incorrect directory and will be caught in main.


def _intialise_virtual_environment():
    if not Path( "venv" ).is_dir():
        command = \
            "python3 -m venv venv && " + \
            ". ./venv/bin/activate && " + \
            "python3 -m pip install --upgrade build pip PyGObject"

        subprocess.call( command, shell = True )


def _run_checks_specific_to_indicator( indicator_name ):
    message = ""
    if "indicatorlunar" in indicator_name:
        #TODO If/when astroskyfield.py is included in the release,
        # (and ephem is dropped),
        # need to include the planets.bsp and stars.dat in the wheel.
        #
        # The astroskyfield.py code assumes planets.bsp/stars.dat are in
        #     indicatorlunar/src/indicatorlunar/data
        # Whilst that directory will be copied across automatically,
        # must also determine planets.bsp/stars.dat are also present.
        # The code below does just that...
        # data_directory =  Path( indicator_name + "/src/indicatorlunar/data" )
        # planets_bsp = Path( str( data_directory ) + "/planets.bsp" )
        # if not planets_bsp.is_file():
        #     message += f"{ indicator_name }: Unable to locate { planets_bsp } - may need to be created - aborting.\n"
        #
        # stars_dat = Path( str( data_directory ) + "/stars.dat" )
        # if not stars_dat.is_file():
        #     message += f"{ indicator_name }: Unable to locate { stars_dat } - may need to be created - aborting.\n"
        #     checks_pass = False

        pass

    return message


def _create_run_script( directory_dist, indicator_name ):
    run_script_path = \
        str( directory_dist ) + "/" + \
        indicator_name + \
        "/src/" + \
        indicator_name + \
        "/packaging/linux/" + \
        indicator_name + ".sh"

    run_script_contents = (
        f"#!/bin/sh\n\n"
        f"cd $HOME/.local && \\\n"
        f". venv_{ indicator_name }/bin/activate && \\\n"
        f"cd venv_{ indicator_name }/lib/python3.*/site-packages/{ indicator_name } && \\\n"
        f"python3 { indicator_name }.py\n" )

    with open( run_script_path, 'w' ) as f:
        f.write( run_script_contents )

    os.chmod(
        run_script_path, 
        stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH |
        stat.S_IWUSR | stat.S_IWGRP |
        stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH )


def _copy_indicator_directory_and_files( directory_dist, indicator_name ):
    directory_indicator = str( directory_dist ) + os.sep + indicator_name
    shutil.copytree( indicator_name, directory_indicator )

    # Remove any .whl 
    for item in Path( directory_indicator + "/src/" + indicator_name ).glob( "*.whl" ):
        os.remove( item )

    # Remove any __pycache__ 
    for item in Path( directory_indicator + "/src/" + indicator_name ).glob( "__pycache__" ):
        shutil.rmtree( item )

    command = "python3 tools/build_readme.py " + directory_indicator + ' ' + indicator_name
    subprocess.call( command, shell = True )

    shutil.copy(
        "indicatorbase/src/indicatorbase/indicatorbase.py",
        directory_indicator + "/src/" + indicator_name )

    _create_run_script( directory_dist, indicator_name )


def _process_locale( directory_dist, indicator_name ):
    directoryIndicator = str( directory_dist ) + os.sep + indicator_name
    directoryIndicatorLocale = directoryIndicator + "/src/" + indicator_name + "/locale"
    directoryIndicatorBaseLocale = "indicatorbase/src/indicatorbase/locale"

    # Append translations from indicator-base to POT.
    command = \
        "msgcat --use-first " + \
        directoryIndicatorLocale + os.sep + indicator_name + ".pot " + \
        directoryIndicatorBaseLocale + "/indicatorbase.pot " + \
        "--output-file=" + directoryIndicatorLocale + os.sep + indicator_name + ".pot"

    subprocess.call( command, shell = True )

    # Append translations from indicatorbase to PO files.
    for po in list( Path( directoryIndicatorLocale ).rglob( "*.po" ) ):
        languageCode = po.parent.parts[ -2 ]

        command = \
            "msgcat --use-first " + \
            str( po ) + " " + \
            directoryIndicatorBaseLocale + os.sep + languageCode + "/LC_MESSAGES/indicatorbase.po " + \
            "--output-file=" + str( po )

        subprocess.call( command, shell = True )

    # Create .mo files.
    for po in list( Path( directoryIndicatorLocale ).rglob( "*.po" ) ):
        command = \
            "msgfmt " + str( po ) + \
            " --output-file=" + str( po.parent ) + os.sep + str( po.stem ) + ".mo"

        subprocess.call( command, shell = True )


def _get_colours_in_hicolor_icon( hicolorIcon ):
    coloursInHicolorIcon = [ ]
    with open( hicolorIcon, 'r' ) as f:
        svgText = f.read()
        for m in re.finditer( r"fill:#", svgText ):
            colour = svgText[ m.start() + 6 : m.start() + 6 + 6 ]
            if colour not in coloursInHicolorIcon:
                coloursInHicolorIcon.append( colour )

    return coloursInHicolorIcon


def _process_icons( directoryWheel, indicatorName ):
    directoryIndicator = str( directoryWheel ) + os.sep + indicatorName
    directoryIndicatorIcons = directoryIndicator + "/src" + os.sep + indicatorName + "/icons"
    directoryIndicatorIconsHicolor = directoryIndicatorIcons + "/hicolor"

    for hicolorIcon in list( Path( directoryIndicatorIconsHicolor ).rglob( "*.svg" ) ):
        coloursInHicolorIcon = _get_colours_in_hicolor_icon( hicolorIcon )
        for themeName in indicatorbase.IndicatorBase.ICON_THEMES:
            directoryIndicatorIconsThemeName = Path( directoryIndicatorIcons + os.sep + themeName )
            if not directoryIndicatorIconsThemeName.exists(): # Must check as will have been created if there is more than one icon.
                directoryIndicatorIconsThemeName.mkdir( parents = True )

            shutil.copy( hicolorIcon, directoryIndicatorIconsThemeName )

            for colour in coloursInHicolorIcon:
                icon = Path( str( directoryIndicatorIconsThemeName ) + os.sep + hicolorIcon.name )
                with open( icon, 'r' ) as f:
                    fileData = f.read()

                with open( icon, 'w' ) as f:
                    f.write( 
                        fileData.replace(
                            '#' + colour + ';',
                            '#' + indicatorbase.IndicatorBase.ICON_THEMES[ themeName ] + ';' ) )


def _build_wheel_for_indicator( directory_release, indicator_name ):
    message = ""
    version_from_pyproject_toml = \
        indicatorbase.IndicatorBase.get_value_for_single_line_tag_from_pyproject_toml(
            indicator_name + '/pyproject.toml',
            "version" )

    version_from_changelog_markdown = \
        indicatorbase.IndicatorBase.get_version_in_changelog_markdown( 
                indicator_name + "/src/" + indicator_name + "/CHANGELOG.md" )

    if version_from_pyproject_toml == version_from_changelog_markdown:
        message = _run_checks_specific_to_indicator( indicator_name )
        if not message:
            directory_dist = Path( directory_release + "/wheel/dist_" + indicator_name )
            if Path( directory_dist ).is_dir():
                shutil.rmtree( str( directory_dist ) )

            directory_dist.mkdir( parents = True )

            _copy_indicator_directory_and_files( directory_dist, indicator_name )
            _process_locale( directory_dist, indicator_name )
            _process_icons( directory_dist, indicator_name )

            _intialise_virtual_environment()

            command = \
                ". ./venv/bin/activate && " + \
                "cd " + str( directory_dist ) + os.sep + indicator_name + " && " + \
                "python3 -m build --outdir ../"

            subprocess.call( command, shell = True )

            shutil.rmtree( str( directory_dist ) + os.sep + indicator_name )

    else:
        message = f"{ indicator_name }: The (most recent) version in CHANGELOG.md does not match that in pyproject.toml\n"

    return message


def _initialise_parser():
    parser = argparse.ArgumentParser(
        description = "Create a Python wheel for one or more indicators." )

    parser.add_argument(
        "directoryRelease",
        help = "The output directory for the Python wheel. " +
               "If the directory specified is 'release', " +
               "the Python wheel will be created in 'release/wheel'. " )

    parser.add_argument(
        "indicators",
        nargs = '+',
        help = "The list of indicators (such as indicatorfortune indicatorlunar) to build." )

    return parser


if __name__ == "__main__":
    parser = _initialise_parser()
    script_path_and_name = "tools/build_wheel.py"
    if Path( script_path_and_name ).exists():
        args = parser.parse_args()
        for indicator_name in args.indicators:
            _build_wheel_for_indicator( args.directoryRelease, indicator_name )

    else:
        print(
            f"The script must be run from the top level directory (one above utils).\n"
            f"For example:\n"
            f"\tpython3 { script_path_and_name } release indicatorfortune" )
