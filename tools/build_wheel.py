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


import argparse
import gettext
import os
import re
import shutil
import stat
import subprocess

from pathlib import Path


def _intialise_virtual_environment( *modules_to_install ):
    if not Path( "venv" ).is_dir():
        command = "python3 -m venv venv"
        subprocess.call( command, shell = True )
    
    command = \
        f". ./venv/bin/activate && " + \
        f"python3 -m pip install --upgrade { ' '.join( modules_to_install ) }"

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


def _chmod( file, user_permission, group_permission, other_permission ):
    os.chmod( file, user_permission | group_permission | other_permission )


def _get_name_and_comments_from_indicator( indicator_name, directory_indicator ):
    indicator_source = \
        Path( directory_indicator + "/src/" + indicator_name + '/' + indicator_name + ".py" )

    name = ""
    comments = ""
    with open( indicator_source, 'r' ) as f:
        for line in f:
            if re.search( r"indicator_name_for_desktop_file = _\( ", line ):
                name = line.split( '\"' )[ 1 ].replace( '\"', '' ).strip()

            if re.search( r"comments = _\(", line ):
                comments = line.split( '\"' )[ 1 ].replace( '\"', '' ).strip()

    if name == "":
        # This flags to the user that no name was found,
        # but allows the build to continue...
        print( "----------------------------------------------" )
        print( f"ERROR: Unable to obtain 'indicator_name' from \n\t{ indicator_source }" )
        print( "----------------------------------------------" )

    if comments == "":
        # This flags to the user that no comments was found,
        # but allows the build to continue...
        print( "-----------------------------------------------------------" )
        print( f"ERROR: Unable to obtain 'comments' from the constructor of\n\t{ indicator_source }" )
        print( "-----------------------------------------------------------" )

    return name, comments


def _create_pyproject_dot_toml( indicator_name, directory_dist ):
    indicator_pyproject_toml_path = str( directory_dist ) + "/" + indicator_name + "/pyproject.toml"
    classifiers = ""
    dependencies = ""
    description = ""
    version = ""
    with open( indicator_pyproject_toml_path, 'r' ) as f:
        for line in f:
            if line.startswith( "description" ):
                # The description may contain a ' which must be replaced with "
                # as it causes an error when parsing the pyproject.toml.
                description = line.split( '=' )[ 1 ].replace( '\"', '' ).replace( '\'', '\"' ).strip()

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
    indicatorbase_pyproject_toml_text = ""
    with open( indicatorbase_pyproject_toml_path ) as f:
        for line in f:
            if not line.startswith( '#' ):
                indicatorbase_pyproject_toml_text += line

    indicatorbase_pyproject_toml_text = \
        indicatorbase_pyproject_toml_text.replace( "{classifiers}", classifiers )

    indicatorbase_pyproject_toml_text = \
        indicatorbase_pyproject_toml_text.replace( "{dependencies}", dependencies )

    indicatorbase_pyproject_toml_text = \
        indicatorbase_pyproject_toml_text.replace( "{indicator_name}", indicator_name )

    project_name_version_description = \
        "[project]\n" + \
        "name = \'" + indicator_name + '\'\n' + \
        "version = \'" + version + '\'\n' + \
        "description = \'" + description + '\''

    indicatorbase_pyproject_toml_text = \
        indicatorbase_pyproject_toml_text.replace( "[project]", project_name_version_description )

    with open( indicator_pyproject_toml_path, 'w' ) as f:
        f.write( indicatorbase_pyproject_toml_text + '\n' )

    _chmod(
        indicator_pyproject_toml_path,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )


def _process_locale( directory_dist, indicator_name ):
    directory_indicator = str( directory_dist ) + os.sep + indicator_name
    directory_indicator_locale = directory_indicator + "/src/" + indicator_name + "/locale"
    directory_indicator_base_locale = "indicatorbase/src/indicatorbase/locale"

    # Append translations from indicatorbase to POT.
    command = \
        "msgcat --use-first " + \
        directory_indicator_locale + os.sep + indicator_name + ".pot " + \
        directory_indicator_base_locale + "/indicatorbase.pot " + \
        "--output-file=" + directory_indicator_locale + os.sep + indicator_name + ".pot"

    subprocess.call( command, shell = True )

    # Append translations from indicatorbase to PO files.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        language_code = po.parent.parts[ -2 ]

        command = \
            "msgcat --use-first " + \
            str( po ) + " " + \
            directory_indicator_base_locale + os.sep + language_code + "/LC_MESSAGES/indicatorbase.po " + \
            "--output-file=" + str( po )

        subprocess.call( command, shell = True )

    # Create .mo files.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        command = \
            "msgfmt " + str( po ) + \
            " --output-file=" + str( po.parent ) + os.sep + str( po.stem ) + ".mo"

        subprocess.call( command, shell = True )


def _get_names_and_comments_from_mo_files(
        indicator_name,
        directory_indicator_locale,
        name,
        comments ):

    names_from_mo_files = { }
    comments_from_mo_files = { }
    for mo in list( Path( directory_indicator_locale ).rglob( "*.mo" ) ):
        locale = mo.parent.parent.stem

        # https://stackoverflow.com/questions/54638570/extract-single-translation-from-gettext-po-file-from-shell
        # https://www.reddit.com/r/learnpython/comments/jkun99/how_do_i_load_a_specific_mo_file_by_giving_its
        # https://stackoverflow.com/questions/53316631/unable-to-use-gettext-to-retrieve-the-translated-string-in-mo-files
        translation = \
            gettext.translation(
                indicator_name,
                localedir = directory_indicator_locale,
                languages = [ locale ] )

        translated_string = translation.gettext( name )

        if translated_string != name:
            names_from_mo_files[ locale ] = translated_string

        translated_string = translation.gettext( comments )

        if translated_string != comments:
            comments_from_mo_files[ locale ] = translated_string

    return names_from_mo_files, comments_from_mo_files


def _create_run_script( directory_platform_linux, indicator_name ):
    indicatorbase_run_script_path = "indicatorbase/src/indicatorbase/platform/linux/indicatorbase.sh"
    with open( indicatorbase_run_script_path, 'r' ) as f:
        run_script_text = f.read()

    run_script_text = run_script_text.format( indicator_name = indicator_name )

    indicator_run_script_path = str( directory_platform_linux ) + "/" + indicator_name + ".sh"
    with open( indicator_run_script_path, 'w' ) as f:
        f.write( run_script_text + '\n' )

    _chmod(
        indicator_run_script_path,
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR,
        stat.S_IRGRP | stat.S_IXGRP,
        stat.S_IROTH | stat.S_IXOTH )


def _create_symbolic_icons( directory_wheel, indicator_name ):
    directory_icons = str( directory_wheel ) + "/" + indicator_name + "/src/" + indicator_name + "/icons"
    for hicolor_icon in list( Path( directory_icons ).glob( "*.svg" ) ):
        symbolic_icon = directory_icons + "/" + str( hicolor_icon.name )[ 0 : -4 ] + "-symbolic.svg"
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
        "indicatorbase/src/indicatorbase/platform/linux/indicatorbase.py.desktop"

    with open( indicatorbase_dot_desktop_path, 'r' ) as f:
        dot_desktop_text = f.read()

    names = name
    for language, _name in names_from_mo_files.items():
        names += f"\nName[{ language }]={ _name }"

    newline = '\\n'
    comment = comments.replace( newline, ' ' ) # If an indicator uses a \n to break up the comments (to fit the About dialog), replace with ' '.
    for language, _comment in comments_from_mo_files.items():
        comment += f"\nComment[{ language }]={ _comment.replace( newline, ' ' ) }"

    dot_desktop_text = \
        dot_desktop_text.format(
            indicator_name = indicator_name,
            names = "Name=" + names,
            comment = "Comment=" + comment,
            categories = indicator_name_to_desktop_file_categories[ indicator_name ] )

    indicator_dot_desktop_path = \
        str( directory_platform_linux ) + "/" + indicator_name + ".py.desktop"

    with open( indicator_dot_desktop_path, 'w' ) as f:
        f.write( dot_desktop_text + '\n' )

    _chmod(
        indicator_dot_desktop_path,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )


def _copy_indicator_directory_and_build_release( directory_dist, indicator_name ):
    # By using copytree, the ENTIRE project is copied across;
    # however, the pyproject.toml explicitly defines what files/folders
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

    _create_pyproject_dot_toml( indicator_name, directory_dist )

    command = "python3 tools/build_readme.py " + directory_indicator + ' ' + indicator_name
    subprocess.call( command, shell = True )

    directory_platform_linux = \
        Path( str( directory_dist ) + "/" + indicator_name + "/src/" + indicator_name + "/platform/linux" )

    directory_platform_linux.mkdir( parents = True )

    _process_locale( directory_dist, indicator_name )

    name, comments = \
        _get_name_and_comments_from_indicator(
            indicator_name, directory_indicator )

    directory_indicator_locale = directory_indicator + "/src/" + indicator_name + "/locale"

    names_from_mo_files, comments_from_mo_files = \
        _get_names_and_comments_from_mo_files(
            indicator_name,
            directory_indicator_locale,
            name,
            comments )

    _create_dot_desktop(
        directory_platform_linux,
        indicator_name,
        name,
        names_from_mo_files,
        comments,
        comments_from_mo_files )

    _create_run_script( directory_platform_linux, indicator_name )

    _create_symbolic_icons( directory_dist, indicator_name )
    
    return ( name != "" ) and ( comments != "" )


def _get_value_for_single_line_tag_from_pyproject_toml( pyproject_toml, tag ):
    # Would like to use
    #   https://docs.python.org/3/library/tomllib.html
    # but it is only in 3.11 which is unavailable for Ubuntu 20.04.
    value = ""
    pattern_tag = re.compile( f"{ tag } = .*" )
    for line in open( pyproject_toml ).readlines():
        matches = pattern_tag.match( line )
        if matches:
            value = matches.group().split( " = " )[ 1 ][ 1 : -1 ]
            break

    return value


def _get_version_in_changelog_markdown( changelog_markdown ):
    version = ""
    with open( changelog_markdown, 'r' ) as f:
        for line in f.readlines():
            if line.startswith( "## v" ):
                version = line.split( ' ' )[ 1 ][ 1 : ]
                break

    return version


def _build_wheel_for_indicator( directory_release, indicator_name ):
    message = ""
    version_from_pyproject_toml = \
        _get_value_for_single_line_tag_from_pyproject_toml(
            indicator_name + '/pyproject.toml',
            "version" )

    version_from_changelog_markdown = \
        _get_version_in_changelog_markdown(
            indicator_name + "/src/" + indicator_name + "/CHANGELOG.md" )

    if version_from_pyproject_toml == version_from_changelog_markdown:
        message = _run_checks_specific_to_indicator( indicator_name )
        if not message:
            directory_dist = Path( directory_release + "/wheel/dist_" + indicator_name )
            if Path( directory_dist ).is_dir():
                shutil.rmtree( str( directory_dist ) )

            directory_dist.mkdir( parents = True )

            if _copy_indicator_directory_and_build_release( directory_dist, indicator_name ):
                _intialise_virtual_environment( "build", "pip", "PyGObject" )

                command = \
                    f". ./venv/bin/activate && " + \
                    f"python3 -m build --outdir { str( directory_dist ) } { str( directory_dist ) }/{ indicator_name }"

                subprocess.call( command, shell = True )
                shutil.rmtree( str( directory_dist ) + os.sep + indicator_name )

    else:
        message = f"{ indicator_name }: The (most recent) version in CHANGELOG.md does not match that in pyproject.toml\n"

    return message


def _initialise_parser():
    parser = \
        argparse.ArgumentParser(
            description = "Create a Python wheel for one or more indicators." )

    parser.add_argument(
        "directory_release",
        help = \
            "The output directory for the Python wheel. " +
            "If the directory specified is 'release', " +
            "the Python wheel will be created in 'release/wheel'." )

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
            message = _build_wheel_for_indicator( args.directory_release, indicator_name )
            if message:
                print( message )

    else:
        print(
            f"The script must be run from the top level directory (one above utils).\n"
            f"For example:\n"
            f"\tpython3 { script_path_and_name } release indicatorfortune" )
