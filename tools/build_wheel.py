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


# Build a Python wheel for one or more indicators.
#
# To view the contents of a .whl:
#    unzip -l indicatortest-1.0.7-py3-none-any.whl
#
# To view the contents of a .tar.gz:
#    tar tf indicatortest-1.0.7.tar.gz


import configparser
import re
import shutil
import stat
import subprocess
import sys

from pathlib import Path

sys.path.append( "indicatorbase/src/indicatorbase" )
import indicatorbase

import utils
import utils_locale
import utils_readme


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
        # data_directory = Path( indicator_name ) / "src" / "indicatorlunar" / "data"
        # planets_bsp = data_directory / "planets.bsp"
        # if not planets_bsp.is_file():
        #     message += f"{ indicator_name }: Unable to locate { planets_bsp } - may need to be created - aborting.\n"
        #
        # stars_dat = Path( str( data_directory ) + "/stars.dat" )
        # if not stars_dat.is_file():
        #     message += f"{ indicator_name }: Unable to locate { stars_dat } - may need to be created - aborting.\n"
        #     checks_pass = False

        pass

    return message


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
                if line.startswith( "version = " ):
                    version_indicator_base = line.split( "\"" )[ 1 ]

                else:
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

    out_pyproject_toml = directory_out / indicator_name / "pyproject.toml"
    with open( out_pyproject_toml, 'w' ) as f:
        f.write( text + '\n' )

    _chmod(
        out_pyproject_toml,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )

    return out_pyproject_toml, version_indicator_base


def _get_name_and_comments_from_indicator( indicator_name, directory_indicator ):
    indicator_source = Path( '.' ) / directory_indicator / "src" / indicator_name / ( indicator_name + ".py" )

    name = ""
    comments = ""
    message = ""
    with open( indicator_source, 'r' ) as f:
        for line in f:
            if re.search( r"indicator_name_for_desktop_file = _\( ", line ):
                name = line.split( '\"' )[ 1 ].replace( '\"', '' ).strip()

            if re.search( r"comments = _\(", line ):
                comments = line.split( '\"' )[ 1 ].replace( '\"', '' ).strip()

    if name == "":
        message += f"ERROR: Unable to obtain 'indicator_name' from \n\t{ indicator_source }"

    if comments == "":
        message += f"ERROR: Unable to obtain 'comments' from the constructor of\n\t{ indicator_source }"

    return name, comments, message


def _create_run_script( directory_platform_linux, indicator_name ):
    indicatorbase_run_script_path = \
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "platform" / "linux" / "indicatorbase.sh"

    with open( indicatorbase_run_script_path, 'r' ) as f:
        run_script_text = f.read()

    run_script_text = run_script_text.format( indicator_name = indicator_name )

    indicator_run_script_path = directory_platform_linux / ( indicator_name + ".sh" )
    with open( indicator_run_script_path, 'w' ) as f:
        f.write( run_script_text + '\n' )

    _chmod(
        indicator_run_script_path,
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR,
        stat.S_IRGRP | stat.S_IXGRP,
        stat.S_IROTH | stat.S_IXOTH )


def _create_symbolic_icons( directory_wheel, indicator_name ):
    directory_icons = directory_wheel / indicator_name / "src" / indicator_name / "icons"
    for hicolor_icon in list( ( Path( '.' ) / directory_icons ).glob( "*.svg" ) ):
        symbolic_icon = directory_icons / ( str( hicolor_icon.name )[ 0 : -4 ] + "-symbolic.svg" )
        shutil.copy( hicolor_icon, symbolic_icon )
        with open( symbolic_icon, 'r' ) as f:
            svg_text = f.read()
            for m in re.finditer( r"fill:#", svg_text ):
                svg_text = svg_text[ 0 : m.start() + 6 ] + "777777" + svg_text[ m.start() + 6 + 6 : ]

            for m in re.finditer( r"stroke:#", svg_text ):
                svg_text = svg_text[ 0 : m.start() + 6 ] + "777777" + svg_text[ m.start() + 6 + 6 : ]

        with open( symbolic_icon, 'w' ) as f:
            f.write( svg_text + '\n' )


def _create_dot_desktop(
        directory_platform_linux,
        indicator_name,
        name,
        names_from_mo_files,
        comments,
        comments_from_mo_files ):

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

    indicatorbase_dot_desktop_path = \
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "platform" / "linux" / "indicatorbase.py.desktop"

    with open( indicatorbase_dot_desktop_path, 'r' ) as f:
        dot_desktop_text = f.read()

    names = name
    for language, _name in names_from_mo_files.items():
        names += f"\nName[{ language }]={ _name }"

    newline = '\\n'

    # If the comments are broken up by '\n' to fit the About dialog, replace with ' '.
    comment = comments.replace( newline, ' ' )

    for language, _comment in comments_from_mo_files.items():
        comment += f"\nComment[{ language }]={ _comment.replace( newline, ' ' ) }"

    dot_desktop_text = \
        dot_desktop_text.format(
            indicator_name = indicator_name,
            names = "Name=" + names,
            comment = "Comment=" + comment,
            categories = indicator_name_to_desktop_file_categories[ indicator_name ] )

    indicator_dot_desktop_path = directory_platform_linux / ( indicator_name + ".py.desktop" )

    with open( indicator_dot_desktop_path, 'w' ) as f:
        f.write( dot_desktop_text + '\n' )

    _chmod(
        indicator_dot_desktop_path,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )


def _get_value_from_pyproject_toml( pyproject_toml, key ):
    config = configparser.ConfigParser()
    config.read( pyproject_toml )
    return config[ key[ 0 ] ][ key[ 1 ] ]


def get_pyproject_toml_authors( pyproject_toml ):
    authors = _get_value_from_pyproject_toml( pyproject_toml, ( "project", "authors" ) )
    authors = authors.replace( '[', '' ).replace( ']', '' )
    authors = authors.replace( '{', '' ).replace( '},', '' ).replace( '}', '' ).strip()

    names_emails = [ ]
    for line in authors.split( '\n' ):
        line_ = line.split( '=' )
        if "name" in line and "email" in line:
            name = line_[ 1 ].split( '\"' )[ 1 ]
            email = line_[ 2 ].split( '\"' )[ 1 ]
            names_emails.append( ( name, email ) )

        elif "name" in line:
            name = line_[ 1 ].split( '\"' )[ 1 ]
            names_emails.append( ( name, "" ) )
        
        elif "email" in line:
            email = line_[ 1 ].split( '\"' )[ 1 ]
            names_emails.append( ( "", email ) )

    return tuple( names_emails )


def get_pyproject_toml_version( pyproject_toml ):
    version = _get_value_from_pyproject_toml( pyproject_toml, ( "project", "version" ) )
    return version.replace( '\'', '' ).strip()


def _get_version_in_changelog_markdown( changelog_markdown ):
    version = ""
    with open( changelog_markdown, 'r' ) as f:
        for line in f.readlines():
            if line.startswith( "## v" ):
                version = line.split( ' ' )[ 1 ][ 1 : ]
                break

    return version


def _package_source_for_build_wheel_process( directory_dist, indicator_name ):
    message = ""

    # Using copytree, the ENTIRE project is copied across.
    # However, the pyproject.toml explicitly defines what files/folders
    # are included in the build (and conversely what is excluded).
    directory_indicator = directory_dist / indicator_name
    shutil.copytree( indicator_name, directory_indicator )

    # Remove any __pycache__
    for pycache in ( Path( '.' ) / directory_indicator / "src" / indicator_name ).glob( "__pycache__" ):
        shutil.rmtree( pycache )

    shutil.copy(
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "indicatorbase.py",
        Path( '.' ) / directory_indicator / "src" / indicator_name )

    pyproject_toml, version_indicator_base = \
        _create_pyproject_dot_toml( indicator_name, directory_dist )

    authors = get_pyproject_toml_authors( pyproject_toml )
    version = get_pyproject_toml_version( pyproject_toml )

    version_from_changelog_markdown = \
        _get_version_in_changelog_markdown(
            Path( '.' ) / indicator_name / "src" / indicator_name / "CHANGELOG.md" )

    if version != version_from_changelog_markdown:
        message = f"{ indicator_name }: The (most recent) version in CHANGELOG.md does not match that in pyproject.toml\n"

    else:
        start_year = \
            indicatorbase.IndicatorBase.get_year_in_changelog_markdown(
                Path( indicator_name ) / "src" / indicator_name / "CHANGELOG.md" )

        message = \
            utils_locale.update_locale_source(
                indicator_name,
                authors,
                start_year,
                version,
                version_indicator_base )

        if not message:
            utils_readme.create_readme( directory_indicator, indicator_name, authors, start_year )

            utils_locale.build_locale_release( directory_dist, indicator_name )

            name, comments, message = \
                _get_name_and_comments_from_indicator(
                    indicator_name, directory_indicator )

            if not message:
                directory_indicator_locale = Path( '.' ) / directory_indicator / "src" / indicator_name / "locale"

                names_from_mo_files, comments_from_mo_files = \
                    utils_locale.get_names_and_comments_from_mo_files(
                        indicator_name,
                        directory_indicator_locale,
                        name,
                        comments )

                directory_platform_linux = directory_dist / indicator_name / "src" / indicator_name / "platform" / "linux"
                directory_platform_linux.mkdir( parents = True )

                _create_dot_desktop(
                    directory_platform_linux,
                    indicator_name,
                    name,
                    names_from_mo_files,
                    comments,
                    comments_from_mo_files )

                _create_run_script( directory_platform_linux, indicator_name )

                _create_symbolic_icons( directory_dist, indicator_name )

    return message


def _build_wheel_for_indicator( directory_release, indicator_name ):
    message = _run_checks_specific_to_indicator( indicator_name )
    if not message:
        directory_dist = Path( '.' ) / directory_release / "wheel" / ( "dist_" + indicator_name )
        if Path( directory_dist ).exists():
            shutil.rmtree( str( directory_dist ) )

        directory_dist.mkdir( parents = True )

        message = _package_source_for_build_wheel_process( directory_dist, indicator_name )
        if not message:
            command = \
                f". ./venv/bin/activate && " + \
                f"python3 -m build --outdir { directory_dist } { directory_dist / indicator_name }"

            subprocess.call( command, shell = True )
            shutil.rmtree( directory_dist / indicator_name )

    return message


if __name__ == "__main__":
    if utils.is_correct_directory( "./tools/build_wheel.py", "release indicatorfortune" ):
        args = \
            utils.initialiase_parser_and_get_arguments(
                "Create a Python wheel for one or more indicators.",
                ( "directory_release", "indicators" ),
                {
                    "directory_release" :
                        "The output directory for the Python wheel. " +
                        "If the directory specified is 'release', " +
                        "the Python wheel will be created in 'release/wheel'.",
                    "indicators" :
                        "The list of indicators (such as indicatorfortune indicatorlunar) to build." },
                {
                    "indicators" :
                        "+" } )

        utils.intialise_virtual_environment( "build", "pip", "PyGObject" )
        for indicator_name in args.indicators:
            message = _build_wheel_for_indicator( args.directory_release, indicator_name )
            if message:
                print( message )
