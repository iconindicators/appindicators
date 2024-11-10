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


"""
Build a Python .whl / .tar.gz for one or more indicators.

To view the contents of a .whl:
   unzip -l indicatortest-1.0.7-py3-none-any.whl

To view the contents of a .tar.gz:
   tar tf indicatortest-1.0.7.tar.gz
"""


import configparser
import re
import shutil
import stat
import subprocess
import sys

from pathlib import Path

import utils
import utils_locale
import utils_readme

sys.path.append( "indicatorbase/src/indicatorbase" )
try:
    import indicatorbase
except ModuleNotFoundError:
    # If the script is called from a directory other than the correct directory,
    # this import will fail before the check for the correct directory can be done,
    # resulting in a "ModuleNotFoundError: No module named 'indicatorbase'"
    # which is a red herring...
    print(
        "indicatorbase could not be found;" + \
        "ensure you are running this script from the correct directory!" )


def _run_checks_on_indicator( indicator_name ):
    paths = [
        Path( '.' ) / "indicatorbase",
        Path( '.' ) / indicator_name,
        Path( '.' ) / "tools" ]

    exclusions = [
        "__pycache__",
        "indicatorlunar/development",
        "indicatorlunar/frink",
        "indicatorlunar/src/indicatorlunar/data" ]

    t_o_d_o = ''.join( [ 't', 'o', 'd', 'o' ] )

    message = ""
    for path in paths:
        for path_ in ( path_.resolve() for path_ in path.glob( '**/*' ) if path_.is_file() and not any( exclusion in str( path_ ) for exclusion in exclusions ) ):
            print( path_ )
            with open( path_, 'r', encoding = "utf-8" ) as f:
                if t_o_d_o in f.read().lower():
                    message += f"\t{ path_ }\n"

    if message:
        message = f"Found one or more { t_o_d_o.upper() }s:\n" + message

    return ""#message #TODO Remove the "" and return the message.


def _chmod( file, user_permission, group_permission, other_permission ):
    Path( file ).chmod( user_permission | group_permission | other_permission )


def _create_pyproject_dot_toml( indicator_name, directory_out ):
    indicator_pyproject_toml = Path( '.' ) / indicator_name / "pyproject.toml"

    config = configparser.ConfigParser()
    with open( indicator_pyproject_toml, encoding = "utf-8" ) as stream:
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
    with open( indicatorbase_pyproject_toml, encoding = "utf-8" ) as f:
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
    with open( out_pyproject_toml, 'w', encoding = "utf-8" ) as f:
        f.write( text + '\n' )

    _chmod(
        out_pyproject_toml,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )

    return out_pyproject_toml, version_indicator_base


def _get_name_categories_comments_from_indicator( indicator_name, directory_indicator ):
    indicator_source = Path( '.' ) / directory_indicator / "src" / indicator_name / ( indicator_name + ".py" )

    name = ""
    categories = ""
    comments = ""
    message = ""
    with open( indicator_source, 'r', encoding = "utf-8" ) as f:
        for line in f:
            if re.search( r"indicator_name_for_desktop_file = _\( ", line ):
                name = line.split( '\"' )[ 1 ].replace( '\"', '' ).strip()

            if re.search( r"indicator_categories = ", line ):
                categories = line.split( '\"' )[ 1 ].replace( '\"', '' ).strip()

            if re.search( r"comments = _\(", line ):
                comments = line.split( '\"' )[ 1 ].replace( '\"', '' ).strip()

    if name == "":
        message += f"ERROR: Unable to obtain 'indicator_name' from \n\t{ indicator_source }"

    if comments == "":
        message += f"ERROR: Unable to obtain 'comments' from the constructor of\n\t{ indicator_source }"

    return name, categories, comments, message


def _create_scripts_for_linux( directory_platform_linux, indicator_name ):

    class SafeDict( dict ):
        '''
        If a shell script contains a variable (of the form ${}),
        the formatter views this as a missing key (unknown text to replace).
        In this case, ignore and return the key so the shell variable remains intact.
        https://stackoverflow.com/a/17215533/2156453
        '''

        def __missing__( self, key ):
            return '{' + key + '}'


    def read_format_write(
            indicatorbase_platform_linux_path,
            source_script_name,
            destination_script_name ):

        with open( indicatorbase_platform_linux_path / source_script_name, 'r', encoding = "utf-8" ) as f:
            script_text = f.read()

        script_text = script_text.format_map( SafeDict( indicator_name = indicator_name ) )

        with open( directory_platform_linux / destination_script_name, 'w', encoding = "utf-8" ) as f:
            f.write( script_text + '\n' )

        _chmod(
            directory_platform_linux / destination_script_name,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR,
            stat.S_IRGRP | stat.S_IXGRP,
            stat.S_IROTH | stat.S_IXOTH )


    indicatorbase_platform_linux_path = \
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "platform" / "linux"

    read_format_write(
        indicatorbase_platform_linux_path,
        "run.sh",
        indicator_name + ".sh" )

    install_script = "install.sh"
    read_format_write(
        indicatorbase_platform_linux_path,
        install_script,
        install_script )

    uninstall_script = "uninstall.sh"
    read_format_write(
        indicatorbase_platform_linux_path,
        uninstall_script,
        uninstall_script )


def _create_symbolic_icons( directory_wheel, indicator_name ):
    directory_icons = directory_wheel / indicator_name / "src" / indicator_name / "icons"
    for hicolor_icon in list( ( Path( '.' ) / directory_icons ).glob( "*.svg" ) ):
        symbolic_icon = directory_icons / ( str( hicolor_icon.name )[ 0 : -4 ] + "-symbolic.svg" )
        shutil.copy( hicolor_icon, symbolic_icon )
        with open( symbolic_icon, 'r', encoding = "utf-8" ) as f:
            svg_text = f.read()
            for m in re.finditer( r"fill:#", svg_text ):
                svg_text = svg_text[ 0 : m.start() + 6 ] + "777777" + svg_text[ m.start() + 6 + 6 : ]

            for m in re.finditer( r"stroke:#", svg_text ):
                svg_text = svg_text[ 0 : m.start() + 6 ] + "777777" + svg_text[ m.start() + 6 + 6 : ]

        with open( symbolic_icon, 'w', encoding = "utf-8" ) as f:
            f.write( svg_text + '\n' )


def _create_dot_desktop(
        directory_platform_linux,
        indicator_name,
        name,
        names_from_mo_files,
        comments,
        comments_from_mo_files,
        categories ):

    indicatorbase_dot_desktop_path = \
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "platform" / "linux" / "indicatorbase.py.desktop"

    dot_desktop_text = ""
    with open( indicatorbase_dot_desktop_path, 'r', encoding = "utf-8" ) as f:
        while line := f.readline():
            if not line.startswith( '#' ):
                dot_desktop_text += line

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
            categories = categories )

    indicator_dot_desktop_path = directory_platform_linux / ( indicator_name + ".py.desktop" )

    with open( indicator_dot_desktop_path, 'w', encoding = "utf-8" ) as f:
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
    with open( changelog_markdown, 'r', encoding = "utf-8" ) as f:
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
            utils_locale.build_locale_release( directory_dist, indicator_name )

            name, categories, comments, message = \
                _get_name_categories_comments_from_indicator(
                    indicator_name, directory_indicator )

            if not message:
                utils_readme.create_readme(
                    directory_indicator,
                    indicator_name,
                    name,
                    authors,
                    start_year )

                command = (
                    f". venv/bin/activate && " +
                    f"python3 -m readme_renderer" +
                    f"    { directory_dist }/{ indicator_name }/README.md" +
                    f"    -o { directory_dist }/{ indicator_name }/src/{ indicator_name }/README.html && " +
                    f"deactivate" )

                subprocess.call( command, shell = True )

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
                    comments_from_mo_files,
                    categories )

                _create_scripts_for_linux( directory_platform_linux, indicator_name )

                _create_symbolic_icons( directory_dist, indicator_name )

    return message


def _build_wheel_for_indicator( directory_release, indicator_name ):
    message = _run_checks_on_indicator( indicator_name )
    if not message:
        directory_dist = Path( '.' ) / directory_release / "wheel" / ( "dist_" + indicator_name )
        if Path( directory_dist ).exists():
            shutil.rmtree( str( directory_dist ) )

        directory_dist.mkdir( parents = True )

        message = _package_source_for_build_wheel_process( directory_dist, indicator_name )
        if not message:
            command = (
                f". venv/bin/activate && " +
                f"python3 -m build --outdir { directory_dist } { directory_dist / indicator_name }" )

            subprocess.call( command, shell = True )

            shutil.rmtree( directory_dist / indicator_name )

    return message


if __name__ == "__main__":
    correct_directory, error_message = \
        utils.is_correct_directory( example_arguments = "release indicatorfortune" )

    if correct_directory:
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
                        "The list of indicators separated by spaces to build." },
                {
                    "indicators" :
                        "+" } )

        utils.initialise_virtual_environment(
            Path( '.' ) / "venv",
            "build",
            "pip",
            "PyGObject",
            "readme_renderer[md]" )

        for indicator in args.indicators:
            error_message = _build_wheel_for_indicator( args.directory_release, indicator )
            if error_message:
                print( error_message )

        # As a convenience, convert the project README.md to README.html
        command_ = (
            f". venv/bin/activate && " +
            f"python3 -m readme_renderer README.md -o README.html && " +
            f"deactivate" )

        subprocess.call( command_, shell = True )

    else:
        print( error_message )
