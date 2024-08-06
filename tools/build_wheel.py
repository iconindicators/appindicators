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


import gettext
import re
import shutil
import stat
import subprocess
import sys

from pathlib import Path

sys.path.append( "indicatorbase/src/indicatorbase" )
import indicatorbase

import utils_locale
import utils_readme
import utils #TODO Maybe rename to utils_general?



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


#TODO Hopefully goes
# def _update_locale( indicator_name ):
#     message = ""
#     command = [
#         f"python3",
#         f"./tools/build_locale.py",
#         f"{ indicator_name }" ]
#
#     result = subprocess.run( command, capture_output = True, text = True )
#     if result.stdout:
#         message = result.stdout
#
#     return message


#TODO Might end up switching to utils version.
def _chmod( file, user_permission, group_permission, other_permission ):
    Path( file ).chmod( user_permission | group_permission | other_permission )


def _get_name_and_comments_from_indicator( indicator_name, directory_indicator ):
    indicator_source = Path( '.' ) / directory_indicator / "src" / indicator_name / ( indicator_name + ".py" )

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


# def _create_pyproject_dot_toml( indicator_name, directory_dist ):
#     indicator_pyproject_toml_path = Path( '.' ) / directory_dist / indicator_name / "pyproject.toml"
#     classifiers = ""
#     dependencies = ""
#     description = ""
#     version = ""
#
# #TODO If the build_readme et al change to access the modified pyprojectbase.toml and pyproject.toml per indicator,
# # need to likely check this code so that the parsing works as I have moved ']' to the end of the previous line.
# #
# # OR, can I use configparser??? 
#     import configparser
#     pyproject_toml = indicator_pyproject_toml_path
#     config = configparser.ConfigParser()
#     with open( pyproject_toml ) as stream:
#         config.read_string( "[top]\n" + stream.read() ) 
#
#     version = config[ "top" ][ "version" ]
#     print( version )
#     description = config[ "top" ][ "description" ]
#     print( description )
#     classifiers = config[ "top" ][ "classifiers" ]
#     print( classifiers )
#
#     if "dependencies" in config[ "top" ]:
#         dependencies = config[ "top" ][ "dependencies" ]
#         print( dependencies )
#
#     print( "----------------------------" )
#
#
#     with open( indicator_pyproject_toml_path, 'r' ) as f:
#         for line in f:
#             if line.startswith( "description" ):
#                 # The description may contain a ' which must be replaced with "
#                 # as it causes an error when parsing the pyproject.toml.
#                 description = line.split( '=' )[ 1 ].replace( '\"', '' ).replace( '\'', '\"' ).strip()
#
#             elif line.startswith( "version" ):            
#                 version = line.split( '=' )[ 1 ].replace( '\"', '' ).strip()
#
#             elif line.startswith( "classifiers" ):
#                 next_line = next( f )
#                 while not next_line.startswith( ']' ):
#                     classifiers += next_line
#                     next_line = next( f )
#
#                 if classifiers:
#                     classifiers = ',\n' + classifiers.rstrip()
#
#             elif line.startswith( "dependencies" ):
#                 next_line = next( f )
#                 while not next_line.startswith( ']' ):
#                     dependencies += next_line
#                     next_line = next( f )
#
#                 if dependencies:
#                     dependencies = ',\n' + dependencies.rstrip()
#
#     indicatorbase_pyproject_toml_path = Path( '.' ) / "indicatorbase" / "pyprojectbase.toml"
#     indicatorbase_pyproject_toml_text = ""
#     with open( indicatorbase_pyproject_toml_path ) as f:
#         for line in f:
#             if not line.startswith( '#' ):
#                 indicatorbase_pyproject_toml_text += line
#
#     indicatorbase_pyproject_toml_text = \
#         indicatorbase_pyproject_toml_text.replace( "{classifiers}", classifiers )
#
#     indicatorbase_pyproject_toml_text = \
#         indicatorbase_pyproject_toml_text.replace( "{dependencies}", dependencies )
#
#     indicatorbase_pyproject_toml_text = \
#         indicatorbase_pyproject_toml_text.replace( "{indicator_name}", indicator_name )
#
#     project_name_version_description = \
#         "[project]\n" + \
#         "name = \'" + indicator_name + '\'\n' + \
#         "version = \'" + version + '\'\n' + \
#         "description = \'" + description + '\''
#
#     indicatorbase_pyproject_toml_text = \
#         indicatorbase_pyproject_toml_text.replace( "[project]", project_name_version_description )
#
#     with open( indicator_pyproject_toml_path, 'w' ) as f:
#         f.write( indicatorbase_pyproject_toml_text + '\n' )
#
#     _chmod(
#         indicator_pyproject_toml_path,
#         stat.S_IRUSR | stat.S_IWUSR,
#         stat.S_IRGRP,
#         stat.S_IROTH )


#TODO SHould this go into build_locale or whatever it will be named?
# def _process_locale( directory_dist, indicator_name ):
#     directory_indicator = Path( '.' ) / directory_dist / indicator_name
#     directory_indicator_locale = Path( '.' ) / directory_indicator / "src" / indicator_name / "locale"
#     directory_indicator_base_locale = Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "locale"
#
#     # Append translations from indicatorbase to POT.
#     command = \
#         "msgcat --use-first " + \
#         str( directory_indicator_locale / ( indicator_name + ".pot" ) ) + " " + \
#         str( directory_indicator_base_locale / "indicatorbase.pot" ) + \
#         " --output-file=" + str( directory_indicator_locale / ( indicator_name + ".pot" ) )
#
#     subprocess.call( command, shell = True )
#
#     # Append translations from indicatorbase to PO files.
#     for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
#         language_code = po.parent.parts[ -2 ]
#
#         command = \
#             "msgcat --use-first " + \
#             str( po ) + " " + \
#             str( directory_indicator_base_locale / language_code / "LC_MESSAGES" / "indicatorbase.po" ) + \
#             " --output-file=" + str( po )
#
#         subprocess.call( command, shell = True )
#
#     # Create .mo files.
#     for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
#         command = \
#             "msgfmt " + str( po ) + \
#             " --output-file=" + str( po.parent / ( str( po.stem ) + ".mo" ) )
#
#         subprocess.call( command, shell = True )


# Moved to utils_locale
# def _get_names_and_comments_from_mo_files(
#         indicator_name,
#         directory_indicator_locale,
#         name,
#         comments ):
#
#     names_from_mo_files = { }
#     comments_from_mo_files = { }
#     for mo in list( Path( directory_indicator_locale ).rglob( "*.mo" ) ):
#         locale = mo.parent.parent.stem
#
#         # https://stackoverflow.com/questions/54638570/extract-single-translation-from-gettext-po-file-from-shell
#         # https://www.reddit.com/r/learnpython/comments/jkun99/how_do_i_load_a_specific_mo_file_by_giving_its
#         # https://stackoverflow.com/questions/53316631/unable-to-use-gettext-to-retrieve-the-translated-string-in-mo-files
#         translation = \
#             gettext.translation(
#                 indicator_name,
#                 localedir = directory_indicator_locale,
#                 languages = [ locale ] )
#
#         translated_string = translation.gettext( name )
#
#         if translated_string != name:
#             names_from_mo_files[ locale ] = translated_string
#
#         translated_string = translation.gettext( comments )
#
#         if translated_string != comments:
#             comments_from_mo_files[ locale ] = translated_string
#
#     return names_from_mo_files, comments_from_mo_files


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


#TODO Need to do the checks below in the function below after pyproject.toml is built.
    # version_from_pyproject_toml = \
    #     _get_value_for_single_line_tag_from_pyproject_toml(
    #         Path( '.' ) / indicator_name / 'pyproject.toml',
    #         "version" )
    #
    # version_from_changelog_markdown = \
    #     _get_version_in_changelog_markdown(
    #         Path( '.' ) / indicator_name / "src" / indicator_name / "CHANGELOG.md" )
    #
    # if version_from_pyproject_toml == version_from_changelog_markdown:
        # message = f"{ indicator_name }: The (most recent) version in CHANGELOG.md does not match that in pyproject.toml\n"
def _package_source_for_build_wheel_process( directory_dist, indicator_name ):
    # By using copytree, the ENTIRE project is copied across;
    # however, the pyproject.toml explicitly defines what files/folders
    # are included in the build (and conversely what is excluded).
    directory_indicator = directory_dist / indicator_name
    shutil.copytree( indicator_name, directory_indicator )

    # Remove any .whl
    for wheel in ( Path( '.' ) / directory_indicator / "src" / indicator_name ).glob( "*.whl" ):
        wheel.unlink()

    # Remove any __pycache__
    for pycache in ( Path( '.' ) / directory_indicator / "src" / indicator_name ).glob( "__pycache__" ):
        shutil.rmtree( pycache )

    shutil.copy(
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "indicatorbase.py",
        Path( '.' ) / directory_indicator / "src" / indicator_name )

    # _create_pyproject_dot_toml( indicator_name, directory_dist )
    pyproject_toml = utils._create_pyproject_dot_toml( indicator_name, directory_dist )  #TODO This might go back into this function from utils!

    authors = utils.get_pyproject_toml_authors( pyproject_toml )
    version = utils.get_pyproject_toml_version( pyproject_toml )

    start_year = \
        indicatorbase.IndicatorBase.get_year_in_changelog_markdown(
            Path( indicator_name ) / "src" / indicator_name / "CHANGELOG.md" )

    message = \
        utils_locale.update_locale_source(
            indicator_name,
            authors,
            start_year,
            version )
#TODO Handle message...abort on not ""?

#Not sure where this should be moved to...but is in the middle of update locale and build locale.
# Also, needs to be a call to a function in utils_readme I think?
    # command = "python3 ./tools/build_readme.py " + str( directory_indicator ) + ' ' + indicator_name
    # subprocess.call( command, shell = True )
    utils_readme.create_readme( directory_indicator, indicator_name, authors, start_year )

    directory_platform_linux = directory_dist / indicator_name / "src" / indicator_name / "platform" / "linux"
    directory_platform_linux.mkdir( parents = True )

    # _process_locale( directory_dist, indicator_name )
    utils_locale.build_locale_release( directory_dist, indicator_name )

    name, comments = \
        _get_name_and_comments_from_indicator(
            indicator_name, directory_indicator )

    directory_indicator_locale = Path( '.' ) / directory_indicator / "src" / indicator_name / "locale"

    names_from_mo_files, comments_from_mo_files = \
        utils_locale.get_names_and_comments_from_mo_files(
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


#TODO This could use ConfigParser.
# def _get_value_for_single_line_tag_from_pyproject_toml( pyproject_toml, tag ):
#     # Would like to use
#     #   https://docs.python.org/3/library/tomllib.html
#     # but it is only in 3.11 which is unavailable for Ubuntu 20.04.
#     value = ""
#     pattern_tag = re.compile( f"{ tag } = .*" )
#     for line in open( pyproject_toml ).readlines():
#         matches = pattern_tag.match( line )
#         if matches:
#             value = matches.group().split( " = " )[ 1 ][ 1 : -1 ]
#             break
#
#     return value


# def _get_version_in_changelog_markdown( changelog_markdown ):
#     version = ""
#     with open( changelog_markdown, 'r' ) as f:
#         for line in f.readlines():
#             if line.startswith( "## v" ):
#                 version = line.split( ' ' )[ 1 ][ 1 : ]
#                 break
#
#     return version


#TODO Delete hopefully.
# def _build_wheel_for_indicatorORIG( directory_release, indicator_name ):
#     message = ""
#
# #TODO I think better to build the pyproject.toml first, then get the version number.
# # Or perhaps can use configparser over the indicator pyproejct.toml fragment?
# # But that's another function...!
#     version_from_pyproject_toml = \
#         _get_value_for_single_line_tag_from_pyproject_toml(
#             Path( '.' ) / indicator_name / 'pyproject.toml',
#             "version" )
#
#     version_from_changelog_markdown = \
#         _get_version_in_changelog_markdown(
#             Path( '.' ) / indicator_name / "src" / indicator_name / "CHANGELOG.md" )
#
#     if version_from_pyproject_toml == version_from_changelog_markdown:
#         message = _run_checks_specific_to_indicator( indicator_name )
#         if not message:
#             message = _update_locale( indicator_name )
#             if not message:
#                 directory_dist = Path( '.' ) / directory_release / "wheel" / ( "dist_" + indicator_name )
#                 if Path( directory_dist ).is_dir():
#                     shutil.rmtree( str( directory_dist ) )
#
#                 directory_dist.mkdir( parents = True )
#
#                 if _package_source_for_build_wheel_process( directory_dist, indicator_name ):
#                     command = \
#                         f". ./venv/bin/activate && " + \
#                         f"python3 -m build --outdir { directory_dist } { directory_dist / indicator_name }"
#
#                     subprocess.call( command, shell = True )
#                     shutil.rmtree( directory_dist / indicator_name )
#
#     else:
#         message = f"{ indicator_name }: The (most recent) version in CHANGELOG.md does not match that in pyproject.toml\n"
#
#     return message




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

#TODO I think better to build the pyproject.toml first, then get the version number.
# Or perhaps can use configparser over the indicator pyproejct.toml fragment?
# But that's another function...!
#
#I think the stuff below needs to go into 
#   _package_source_for_build_wheel_process()
    # version_from_pyproject_toml = \
    #     _get_value_for_single_line_tag_from_pyproject_toml(
    #         Path( '.' ) / indicator_name / 'pyproject.toml',
    #         "version" )
    #
    # version_from_changelog_markdown = \
    #     _get_version_in_changelog_markdown(
    #         Path( '.' ) / indicator_name / "src" / indicator_name / "CHANGELOG.md" )
    #
    # if version_from_pyproject_toml == version_from_changelog_markdown:
        # message = f"{ indicator_name }: The (most recent) version in CHANGELOG.md does not match that in pyproject.toml\n"

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
