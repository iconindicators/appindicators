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


'''
Build a Python .whl and .tar.gz for one or more indicators.

To view the contents of a .whl:
   unzip -l indicatortest-1.0.7-py3-none-any.whl

To view the contents of a .tar.gz:
   tar tf indicatortest-1.0.7.tar.gz
'''


import configparser
import re
import shutil
import stat
import subprocess

from pathlib import Path

from . import utils
from . import utils_locale
from . import utils_readme


VENV_DEVELOPMENT = "./venv_development"


def _check_for_t_o_d_o_s(
    indicator_name ):

    paths = [
        "indicatorbase",
        indicator_name,
        "tools" ]

    file_types = [
        "*.desktop",
        "*.htm*",
        "*.in",
        "LINGUAS",
        "*.md",
        "*.po*",
        "*.py",
        "*.sh",
        "*.svg",
        "*.toml" ]

    t_o_d_o = ''.join( [ 't', 'o', 'd', 'o' ] )

    message = ""
    for path in paths:
        for file_type in file_types:
            for file in ( Path( '.' ) / path ).resolve().rglob( file_type ):
                with open( file, 'r', encoding = "utf-8" ) as f:
                    if t_o_d_o in f.read().lower():
                        message += f"\t{ file }\n"
    if message:
        message = f"Found one or more { t_o_d_o.upper() }s:\n" + message

    return message


def _chmod(
    file_,
    user_permission,
    group_permission,
    other_permission ):

    Path( file_ ).chmod( user_permission | group_permission | other_permission )


def _create_pyproject_dot_toml(
    indicator_name,
    directory_out ):

    indicator_pyproject_toml = (
        Path( '.' ) / indicator_name / "pyprojectspecific.toml" )

    config_indicator = configparser.ConfigParser()
    config_indicator.read( indicator_pyproject_toml )

    indicatorbase_pyproject_toml = (
        Path( '.' ) / "indicatorbase" / "pyprojectbase.toml" )

    config_indicatorbase = configparser.ConfigParser()
    config_indicatorbase.read( indicatorbase_pyproject_toml )

    version_indicatorbase = (
        config_indicatorbase.get( "project", "version" ).replace( '"', '' ) )

    config_indicatorbase.set(
        "project",
        "name",
        f"\"{ indicator_name }\"" )

    config_indicatorbase.set(
        "project",
        "version",
        config_indicator.get( "project", "version" ) )

    config_indicatorbase.set(
        "project",
        "description",
        config_indicator.get( "project", "description" ) )

    if config_indicator.has_option( "project", "classifiers" ):
        config_indicatorbase.set(
            "project",
            "classifiers",
            config_indicatorbase.get( "project", "classifiers" ).replace( ' ]', "," )
            +
            config_indicator.get( "project", "classifiers" ).replace( '[', '' ) )

    if config_indicator.has_option( "project", "dependencies" ):
        config_indicatorbase.set(
            "project",
            "dependencies",
            config_indicatorbase.get( "project", "dependencies" ).replace( ' ]', ',' )
            +
            config_indicator.get( "project", "dependencies" ).replace( '[', '' ) )

    out_pyproject_toml = directory_out / indicator_name / "pyproject.toml"
    with open( out_pyproject_toml, 'w', encoding = "utf-8" ) as f:
        config_indicatorbase.write( f )

    _chmod(
        out_pyproject_toml,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )

    return out_pyproject_toml, version_indicatorbase


def _create_manifest_dot_in(
    indicator_name,
    directory_out ):

    indicatorbase_manifest_in = (
        Path( '.' ) / "indicatorbase" / "MANIFESTbase.in" )

    with open( indicatorbase_manifest_in, 'r', encoding = "utf-8" ) as f:
        manifest_text = f.read().replace( "{indicator_name}", indicator_name )

    indicator_manifest_in = (
        Path( '.' ) / indicator_name / "MANIFESTspecific.in" )

    if Path( indicator_manifest_in ).exists():
        with open( indicator_manifest_in, 'r', encoding = "utf-8" ) as f:
            manifest_text += f.read().replace( "{indicator_name}", indicator_name )

    release_manifest_in = directory_out / indicator_name / "MANIFEST.in"
    with open( release_manifest_in, 'w', encoding = "utf-8" ) as f:
        f.write( manifest_text + '\n' )

    _chmod(
        release_manifest_in,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )


def _get_version_in_changelog_markdown(
    changelog_markdown ):

    version = ""
    with open( changelog_markdown, 'r', encoding = "utf-8" ) as f:
        for line in f.readlines():
            if line.startswith( "## v" ):
                version = line.split( ' ' )[ 1 ][ 1 : ]
                break

    return version


def _get_pyproject_toml_authors(
    pyproject_toml_config ):

    authors = (
        pyproject_toml_config.get( "project", "authors" )
        .replace( '[', '' )
        .replace( ']', '' )
        .replace( '{', '' )
        .replace( '},', '' )
        .replace( '}', '' )
        .strip() )

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


def _get_year_in_changelog_markdown(
    indicator_name ):
    '''
    Obtains the (most recent) year from the CHANGELOG.md.
    
    Typically achieved by calling a function in indicatorbase.
    Unfortunately, seems next to impossible to do so because the import of
    indicatorbase fails.

    Next best thing: call the function through the Python console.

    Returns the most recent year from the CHANGELOG.md and an empty message.
    On error, returns -1 for the year and an non-empty message.
    '''

    result = (
        subprocess.run(
            f". { VENV_DEVELOPMENT }/bin/activate && " +
            f"python3 -c \"from indicatorbase.src.indicatorbase.indicatorbase " +
            f"import IndicatorBase; " +
            f"print( IndicatorBase.get_year_in_changelog_markdown( " +
            f"'{ Path( indicator_name ) }/src/{ indicator_name }/CHANGELOG.md' ) )\"",
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell = True,
            check = False ) )

    stderr_ = result.stderr.decode()
    if stderr_:
        message = f"Unable to obtain year from CHANGELOG.md: { stderr_ }"
        year = -1

    else:
        year = result.stdout.decode().strip()
        message = ""

    return year, message


def _get_name_categories_comments_from_indicator(
    indicator_name,
    directory_indicator ):

    def parse( line ):
        return line.split( '\"' )[ 1 ].replace( '\"', '' ).strip()


    indicator_source = (
        Path( '.' ) / directory_indicator / "src" / indicator_name / ( indicator_name + ".py" ) )  #TODO Can this be split over lines?

    name = ""
    categories = ""
    comments = ""
    message = ""
    with open( indicator_source, 'r', encoding = "utf-8" ) as f:
        for line in f:
            if re.search( r"indicator_name_for_desktop_file = _\( ", line ):
                name = parse( line )

            if re.search( r"indicator_categories = ", line ):
                categories = parse( line )

            if re.search( r"comments = _\(", line ):
                comments = parse( line )

    if name == "":
        message += f"ERROR: Unable to obtain 'indicator_name' from \n\t{ indicator_source }"

    if categories == "":
        message += f"ERROR: Unable to obtain 'categories' from \n\t{ indicator_source }"

    if comments == "":
        message += f"ERROR: Unable to obtain 'comments' from the constructor of\n\t{ indicator_source }"

    return name, categories, comments, message


def _create_dot_desktop(
    directory_platform_linux,
    indicator_name,
    name,
    names_from_po_files,
    comments,
    comments_from_po_files,
    categories ):

    #TODO Testing
    print()
    print( f"names: { names_from_po_files }" )
    print()
    print( f"comments: { comments_from_po_files }" )
    print()

    indicatorbase_dot_desktop_path = (
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "platform" / "linux" / "indicatorbase.py.desktop" )

    dot_desktop_text = ""
    with open( indicatorbase_dot_desktop_path, 'r', encoding = "utf-8" ) as f:
        while line := f.readline():
            if not line.startswith( '#' ):
                dot_desktop_text += line

    names = name
    for language, name_ in names_from_po_files.items():
        names += f"\nName[{ language }]={ name_ }"

#TODO Check with all other indicators if the comments should be split.
    # Comments may contain a '\n' to fit the About dialog; replace with ' '.
    print( comments )
    comments_ = comments.replace( "\\n", ' ' )
    print( comments_ )

    newline = '\n'
    for language, comment in comments_from_po_files.items():
        comments_ += f"\nComment[{ language }]={ comment.replace( newline, ' ' ) }"

    #TODO Testing
    print()
    print( f"names: { names }" )
    print()
    print( f"comments: { comments_ }" )
    print()

    dot_desktop_text = (
        dot_desktop_text.format(
            indicator_name = indicator_name,
            names = "Name=" + names,
            comment = "Comment=" + comments_,
            categories = categories ) )

    indicator_dot_desktop_path = (
        directory_platform_linux / ( indicator_name + ".py.desktop" ) )

    with open( indicator_dot_desktop_path, 'w', encoding = "utf-8" ) as f:
        f.write( dot_desktop_text + '\n' )

    _chmod(
        indicator_dot_desktop_path,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )


def _create_scripts_for_linux(
    directory_platform_linux,
    indicator_name ):

    indicatorbase_platform_linux_path = (
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "platform" / "linux" )

    def process(
        source_script_name,
        destination_script_name ):

        source = indicatorbase_platform_linux_path / source_script_name
        with open( source, 'r', encoding = "utf-8" ) as f:
            text = f.read()

        destination = directory_platform_linux / destination_script_name
        with open( destination, 'w', encoding = "utf-8" ) as f:
            text = text.replace( "{indicator_name}", indicator_name )
            text = text.replace( "{venv_indicators}", utils.VENV_INSTALL )
            f.write( text + '\n' )

        _chmod(
            destination,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR,
            stat.S_IRGRP | stat.S_IXGRP,
            stat.S_IROTH | stat.S_IXOTH )


    process( "run.sh", indicator_name + ".sh" )

    install_script = "install.sh"
    process( install_script, install_script )

    uninstall_script = "uninstall.sh"
    process( uninstall_script, uninstall_script )


#TODO Perhaps create the symbolic icons and commit to repository instead of creating each time?
def _create_symbolic_icons(
    directory_wheel,
    indicator_name ):

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


def _package_source_for_build_wheel_process(
    directory_dist,
    indicator_name ):

    directory_indicator = directory_dist / indicator_name

    # Copy the ENTIRE project across and create a pyproject.toml and MANIFEST.in
    # by combining those from indicatorbase and the indicator to include/exclude
    # files/folders in the build.
    shutil.copytree( indicator_name, directory_indicator )

    shutil.copy(
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "indicatorbase.py",
        Path( '.' ) / directory_indicator / "src" / indicator_name )

    pyproject_toml, version_indicator_base = (
        _create_pyproject_dot_toml(
            indicator_name,
            directory_dist ) )

    _create_manifest_dot_in(
        indicator_name,
        directory_dist )

    config = configparser.ConfigParser()
    config.read( pyproject_toml )

    version_from_pyproject_toml = (
        config.get( "project", "version" ).replace( "\"", '' ).strip() )

    version_from_changelog_markdown = (
        _get_version_in_changelog_markdown(
            Path( '.' ) / indicator_name / "src" / indicator_name / "CHANGELOG.md" ) )

    message = ""
    if version_from_pyproject_toml != version_from_changelog_markdown:
        message = (
            f"{ indicator_name }: The most recent version in " +
            f"CHANGELOG.md does not match that in pyprojectspecific.toml\n" )

    if not message:
        authors = _get_pyproject_toml_authors( config )

        start_year, message = _get_year_in_changelog_markdown( indicator_name )

    if not message:
        utils_locale.update_locale_source(
            indicator_name,
            authors,
            start_year,
            version_from_pyproject_toml,
            version_indicator_base )

        utils_locale.build_locale_for_release(
            directory_dist,
            indicator_name )

        name, categories, comments, message = (
            _get_name_categories_comments_from_indicator(
                indicator_name,
                directory_indicator ) )

    if not message:
        utils_readme.create_readme(
            directory_indicator,
            indicator_name,
            name,
            authors,
            start_year )

        subprocess.run(
            f". { VENV_DEVELOPMENT }/bin/activate && " +
            f"python3 -m readme_renderer " +
            f"{ directory_dist }/{ indicator_name }/README.md " +
            f"-o { directory_dist }/{ indicator_name }/src/{ indicator_name }/README.html",
            shell = True )

        directory_indicator_locale = (
            Path( '.' ) / directory_indicator / "src" / indicator_name / "locale" )

        names_from_po_files, comments_from_po_files, message = (
            utils_locale.get_names_and_comments_from_po_files(
                directory_indicator_locale,
                name,
                comments ) )

    if not message:
        directory_platform_linux = (
            directory_dist / indicator_name / "src" / indicator_name / "platform" / "linux" )

        directory_platform_linux.mkdir( parents = True )

        _create_dot_desktop(
            directory_platform_linux,
            indicator_name,
            name,
            names_from_po_files,
            comments,
            comments_from_po_files,
            categories )

        _create_scripts_for_linux(
            directory_platform_linux,
            indicator_name )

        _create_symbolic_icons(
            directory_dist,
            indicator_name )

    return message


def _build_wheel_for_indicator(
    directory_release,
    indicator_name ):

    # message = _check_for_t_o_d_o_s( indicator_name ) #TODO Uncomment
    message = ""
    if not message:
        directory_dist = Path( '.' ) / directory_release / "wheel" / ( "dist_" + indicator_name )
        if Path( directory_dist ).exists():
            shutil.rmtree( str( directory_dist ) )

        directory_dist.mkdir( parents = True )

        message = _package_source_for_build_wheel_process( directory_dist, indicator_name )

        import sys
        sys.exit()#TODO Testing        

        if not message:
            subprocess.run(
                f". { VENV_DEVELOPMENT }/bin/activate && " +
                f"python3 -m build --outdir { directory_dist } { directory_dist / indicator_name }",
                shell = True )

#TODO Uncomment
#            shutil.rmtree( directory_dist / indicator_name )

    return message


if __name__ == "__main__":
    args = (
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
                    "+" } ) )

    utils.initialise_virtual_environment(
        VENV_DEVELOPMENT,
        "build",
        "packaging",
        "pip",
        "polib",
        "PyGObject",
        "readme_renderer[md]" )

    for indicator in args.indicators:
        error_message = _build_wheel_for_indicator( args.directory_release, indicator )
        if error_message:
            print( error_message )

    subprocess.run(
        f". { VENV_DEVELOPMENT }/bin/activate && " +
        f"python3 -m readme_renderer README.md -o README.html",
        shell = True )
