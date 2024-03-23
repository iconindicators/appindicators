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


# Create the .desktop file dynanamically...
# ...these are the entries for the Name (and any translations) for each indicator.
indicator_name_to_desktop_file_names = {
    "indicatorfortune" :
        [ "Name=Indicator Fortune",
          "Name[ru]=Индикатор изречений" ],

    "indicatorlunar" :
        [ "Name=Indicator Lunar",
          "Name[ru]=Лунный индикатор" ],

    "indicatoronthisday" :
        [ "Name=Indicator On This Day",
          "Name[ru]=Индикатор событий дня" ],

    "indicatorppadownloadstatistics" :
        [ "Name=Indicator PPA Download Statistics",
          "Name[cs]=PPA indikátor statisktik stahování",
          "Name[ru]=Индикатор статистики закачек из PPA" ],

    "indicatorpunycode" :
        [ "Name=Indicator Punycode",
          "Name[ru]=Индикатор Punycode-конвертер" ],

    "indicatorscriptrunner" :
        [ "Name=Indicator Script Runner",
          "Name[ru]=Индикатор запуска сценариев" ],

    "indicatorstardate" :
        [ "Name=Indicator Stardate",
          "Name[ru]=Индикатор звёздной даты" ],

    "indicatortest" :
        [ "Name=Indicator Test" ],

    "indicatortide" :
        [ "Name=Indicator Tide",
          "Name[ru]=Индикатор приливов" ],

    "indicatorvirtualbox" :
        [ "Name=Indicator VirtualBox™",
          "Name[ru]=Индикатор VirtualBox™" ] }


# Create the .desktop file dynanamically...
# ...these are the entries for the Categories for each indicator.
indicator_name_to_desktop_file_categories = {
    "indicatorfortune" : "Categories=Utility;Amusement",
    "indicatorlunar" : "Categories=Science;Astronomy",
    "indicatoronthisday" : "Categories=Utility;Amusement",
    "indicatorppadownloadstatistics" : "Categories=Utility",
    "indicatorpunycode" : "Categories=Utility",
    "indicatorscriptrunner" : "Categories=Utility",
    "indicatorstardate" : "Categories=Utility;Amusement",
    "indicatortest" : "Categories=Utility",
    "indicatortide" : "Categories=Utility",
    "indicatorvirtualbox" : "Categories=Utility" }


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


#TODO Remove eventually
def _create_dot_desktopOLD( directory_packaging_linux, indicator_name ):
    dot_desktop_path = str( directory_packaging_linux ) + "/" + indicator_name + ".py.desktop"

    name_entries = ""
    for name_entry in indicator_name_to_desktop_file_names[ indicator_name ]:
        name_entries += name_entry + "\n"

    name_entries = name_entries[ 0 : -1 ] # Drop last newline.

    dot_desktop_contents = (
        f"# To validate this file:\n"
        f"#   desktop-file-validate { indicator_name }.py.desktop\n"
        f"#\n"
        f"# To install or update this file, although the\n"
        f"# operating system should update by default and\n"
        f"# certainly will update on a logout/login or restart:\n"
        f"#   xdg-desktop-menu install --novendor { indicator_name }.py.desktop\n"
        f"[Desktop Entry]\n"
        f"Type=Application\n"
        f"{ name_entries }\n"
        f"Icon={ indicator_name }\n"
        f"Exec=sh -c \"\$HOME/.local/bin/{ indicator_name }.sh\"\n"
        f"{ indicator_name_to_desktop_file_categories[ indicator_name ] }\n"
        f"X-GNOME-Autostart-enabled=true\n"
        f"X-GNOME-Autostart-Delay=0\n"
        f"\n" )

    with open( dot_desktop_path, 'w' ) as f:
        f.write( dot_desktop_contents )

    os.chmod(
        dot_desktop_path,
        stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH |
        stat.S_IWUSR | stat.S_IWGRP |
        stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH )


def _create_dot_desktop( directory_platform_linux, indicator_name ):
    indicatorbase_dot_desktop_path = "indicatorbase/src/indicatorbase/platform/linux/indicatorbase.py.desktop"
    with open( indicatorbase_dot_desktop_path, 'r' ) as f:
        dot_desktop_text = f.read()

    dot_desktop_text = dot_desktop_text.format(
                        indicator_name = indicator_name,
                        categories = indicator_name_to_desktop_file_categories[ indicator_name ],
                        names = '\n'.join( indicator_name_to_desktop_file_names[ indicator_name ] ) )

    indicator_dot_desktop_path = str( directory_platform_linux ) + "/" + indicator_name + ".py.desktop"
    with open( indicator_dot_desktop_path, 'w' ) as f:
        f.write( dot_desktop_text )

    os.chmod(
        indicator_dot_desktop_path,
        stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH |
        stat.S_IWUSR | stat.S_IWGRP |
        stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH )


#TODO Delete eventually
def _create_run_scriptOLD( directory_packaging_linux, indicator_name ):
    run_script_path = str( directory_packaging_linux ) + "/" + indicator_name + ".sh"

    run_script_contents = (
        f"#!/bin/sh\n\n"
        f"cd $HOME && \\\n"
        f". .local/venv_{ indicator_name }/bin/activate && \\\n"
        f"python3 $(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/ { indicator_name }.py && \\\n"
        f"deactivate\n" )

    with open( run_script_path, 'w' ) as f:
        f.write( run_script_contents )

    os.chmod(
        run_script_path,
        stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH |
        stat.S_IWUSR | stat.S_IWGRP |
        stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH )


def _create_run_script( directory_platform_linux, indicator_name ):
    indicatorbase_run_script_path = "indicatorbase/src/indicatorbase/platform/linux/indicatorbase.sh"
    with open( indicatorbase_run_script_path, 'r' ) as f:
        run_script_text = f.read()

    run_script_text = run_script_text.format( indicator_name = indicator_name )

    indicator_run_script_path = str( directory_platform_linux ) + "/" + indicator_name + ".sh"
    with open( indicator_run_script_path, 'w' ) as f:
        f.write( run_script_text )

    os.chmod(
        indicator_run_script_path,
        stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH |
        stat.S_IWUSR | stat.S_IWGRP |
        stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH )


def _create_pyproject_dot_toml( directory_dist, indicator_name ):
    classifiers = ""
    dependencies = ""
    description = ""
    version = ""
    indicator_pyproject_toml_path = str( directory_dist ) + "/" + indicator_name + "/" + "pyproject.toml"
    with open( indicator_pyproject_toml_path, 'r' ) as f:
        for line in f:
            if line.startswith( "description" ):
                description = line.split( '=' )[ 1 ].replace( '\"', '' ).strip()

            elif line.startswith( "version" ):
                version = line.split( '=' )[ 1 ].replace( '\"', '' ).strip()

            elif line.startswith( "classifiers" ):
                next_line = next( f )
                while not next_line.startswith( ']' ):
                    classifiers += next_line
                    next_line = next( f )

                if classifiers:
                    classifiers = ',\n' + classifiers.rstrip()

            elif line.startswith( "dependencies" ):
                next_line = next( f )
                while not next_line.startswith( ']' ):
                    dependencies += next_line
                    next_line = next( f )

                if dependencies:
                    dependencies = ',\n' + dependencies.rstrip()

    indicatorbase_pyproject_toml_path = "indicatorbase/pyprojectbase.toml"
    with open( indicatorbase_pyproject_toml_path, 'r' ) as f:
        indicatorbase_pyproject_toml_text = f.read()

    indicatorbase_pyproject_toml_text = indicatorbase_pyproject_toml_text.replace(
                                            "{classifiers}", classifiers )

    indicatorbase_pyproject_toml_text = indicatorbase_pyproject_toml_text.replace(
                                            "{dependencies}", dependencies )

    indicatorbase_pyproject_toml_text = indicatorbase_pyproject_toml_text.replace(
                                            "{indicator_name}", indicator_name )

    project_name_version_description = \
        "[project]\n" + \
        "name = \'" + indicator_name + '\'\n' + \
        "version = \'" + version + '\'\n' + \
        "description = \'" + description + '\''

    indicatorbase_pyproject_toml_text = indicatorbase_pyproject_toml_text.replace(
                                            "[project]", project_name_version_description )

    with open( indicator_pyproject_toml_path, 'w' ) as f:
        f.write( indicatorbase_pyproject_toml_text )

    os.chmod(
        indicator_pyproject_toml_path,
        stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH |
        stat.S_IWUSR | stat.S_IWGRP |
        stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH )


def _copy_indicator_directory_and_files( directory_dist, indicator_name ):

    # By using copytree, the ENTIRE project is copied across...
    # ...however the pyproject.toml explicitly defines what files/folders
    # are included in the build (and conversely what is excluded).
    directory_indicator = str( directory_dist ) + os.sep + indicator_name
    shutil.copytree( indicator_name, directory_indicator )

    # Remove any .whl
    for item in Path( directory_indicator + "/src/" + indicator_name ).glob( "*.whl" ):
        os.remove( item )

    # Remove any __pycache__
    for item in Path( directory_indicator + "/src/" + indicator_name ).glob( "__pycache__" ):
        shutil.rmtree( item )

    shutil.copy(
        "indicatorbase/src/indicatorbase/indicatorbase.py",
        directory_indicator + "/src/" + indicator_name )

    _create_pyproject_dot_toml( directory_dist, indicator_name )

    command = "python3 tools/build_readme.py " + directory_indicator + ' ' + indicator_name
    subprocess.call( command, shell = True )

    directory_platform_linux = Path( str( directory_dist ) + "/" + indicator_name + "/src/" + indicator_name + "/platform/linux" )
    directory_platform_linux.mkdir( parents = True )

    _create_dot_desktop( directory_platform_linux, indicator_name )
    _create_run_script( directory_platform_linux, indicator_name )


def _process_locale( directory_dist, indicator_name ):
    directoryIndicator = str( directory_dist ) + os.sep + indicator_name
    directoryIndicatorLocale = directoryIndicator + "/src/" + indicator_name + "/locale"
    directoryIndicatorBaseLocale = "indicatorbase/src/indicatorbase/locale"

    # Append translations from indicatorbase to POT.
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


#TODO Given this function, does this mean we only need the hicolor icon
# and the symbolic icon will be created here?
def _create_symbolic_icons( directoryWheel, indicatorName ):
    directoryIcons = str( directoryWheel ) + "/" + indicatorName + "/src/" + indicatorName + "/icons"
    print( directoryIcons )
    for hicolorIcon in list( Path( directoryIcons ).glob( "*.svg" ) ):
        symbolic_icon = directoryIcons + "/" + str( hicolorIcon.name )[ 0 : -4 ] + "-symbolic.svg"
        shutil.copy( hicolorIcon, symbolic_icon )
        with open( symbolic_icon, 'r' ) as f:
            svgText = f.read()
            for m in re.finditer( r"fill:#", svgText ):
                svgText = svgText[ 0 : m.start() + 6 ] + "777777" + svgText[ m.start() + 6 + 6 : ]

            for m in re.finditer( r"stroke:#", svgText ):
                svgText = svgText[ 0 : m.start() + 6 ] + "777777" + svgText[ m.start() + 6 + 6 : ]

        with open( symbolic_icon, 'w' ) as f:
            f.write( svgText )


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
            _create_symbolic_icons( directory_dist, indicator_name )

            _intialise_virtual_environment()

            command = \
                ". ./venv/bin/activate && " + \
                "cd " + str( directory_dist ) + os.sep + indicator_name + " && " + \
                "python3 -m build --outdir ../"

#TODO Put back
#            subprocess.call( command, shell = True )

#TODO Put back
#            shutil.rmtree( str( directory_dist ) + os.sep + indicator_name )

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
            message = _build_wheel_for_indicator( args.directoryRelease, indicator_name )
            if message:
                print( message )

    else:
        print(
            f"The script must be run from the top level directory (one above utils).\n"
            f"For example:\n"
            f"\tpython3 { script_path_and_name } release indicatorfortune" )
