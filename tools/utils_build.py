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
Create a Python3 wheel.

Requires polib to be installed by the calling script.
'''


#TODO There is a (what seems to be mandatory) LICENSE file on the GitHub site
#   https://github.com/iconindicators/appindicators
# so maybe create a mock LICENSE file in the project root and see where it ends
# up in the build.
#
# I think the LICENSE file is redundant for building a wheel though,
# given using the 'license' field in pyproject.toml
#
# So maybe copy whatever GitHub uses and place that at root of project.
# When doing the build, ensure that same file is not part of the orig.tar.gz
# nor the .whl


import configparser
import datetime
import filecmp
import importlib
import os
import re
import shutil
import stat
import sys

from importlib.metadata import version
from pathlib import Path

if "../" not in sys.path:
    sys.path.insert( 0, "../" )

import polib # Installed by the calling script.

from indicatorbase.src.indicatorbase import indicatorbase

from . import utils
from . import utils_readme


def _get_linguas_codes(
    indicator ):

    linguas_codes = [ ]

    file_ = _get_linguas( indicator )
    lines = indicatorbase.IndicatorBase.read_text_file( file_ )
    for line in lines:
        if not line.startswith( '#' ):
            linguas_codes = line.split()

    return linguas_codes


def _get_locale_directory(
    indicator ):

    return Path( '.' ) / indicator / "src" / indicator / "locale"


def _get_linguas(
    indicator ):

    # The LINGUAS file lists each supported language/locale:
    #   http://www.gnu.org/software/gettext/manual/gettext.html#po_002fLINGUAS
    return _get_locale_directory( indicator ) / "LINGUAS"


def _get_current_year():
    return datetime.datetime.now( datetime.timezone.utc ).strftime( '%Y' )


def _get_message(
    stderr_,
    return_code ):

    message = ""
    if stderr_:
        message = stderr_

    else:
        message = f"Return code: { return_code }"

    return message


def _create_update_pot(
    indicator,
    locale_directory,
    authors_emails,
    version_,
    copyright_ ):

    pot_file_new = f"{ locale_directory / indicator }.pot"
    if Path( pot_file_new ).exists():
        pot_file_new = f"{ locale_directory / indicator }.new.pot"

    # Create a POT based on current source:
    #   http://www.gnu.org/software/gettext/manual/gettext.html
    stdout_, stderr_, return_code = (
        indicatorbase.IndicatorBase.process_run(
            "xgettext "
            f"-f { locale_directory / 'POTFILES.in' } "
            f"-D { str( Path( indicator ) / 'src' / indicator ) } "
            f"--copyright-holder='{ authors_emails[ 0 ][ 0 ] }.' "
            f"--package-name={ indicator } "
            f"--package-version={ version_ } "
            f"--msgid-bugs-address='<{ authors_emails[ 0 ][ 1 ] }>' "
            f"-o { pot_file_new }" ) )

    if return_code == 0:
        lines = indicatorbase.IndicatorBase.read_text_file( pot_file_new )
        content = ''.join( lines )
        text = (
            content.
                replace(
                    "SOME DESCRIPTIVE TITLE",
                    f"Portable Object Template for { indicator }" ).
                replace(
                    f"YEAR { authors_emails[ 0 ][ 0 ] }",
                    copyright_ ).
                replace(
                    "FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.\n#\n#, fuzzy",
                    "FIRST AUTHOR <EMAIL@ADDRESS>, YEAR."  ).
                replace(
                    "CHARSET",
                    "UTF-8" ) )

        indicatorbase.IndicatorBase.write_text_file( pot_file_new, text )

        if pot_file_new.endswith( ".new.pot" ):
            pot_file_original = f"{ locale_directory / indicator }.pot"
            original = ""
            lines = indicatorbase.IndicatorBase.read_text_file( pot_file_original )
            for line in lines:
                if "POT-Creation-Date" not in line:
                    original += line

            new = ""
            lines = indicatorbase.IndicatorBase.read_text_file( pot_file_new )
            for line in lines:
                if "POT-Creation-Date" not in line:
                    new += line

            if original == new:
                os.remove( pot_file_new )

            else:
                os.remove( pot_file_original )
                os.rename( pot_file_new, pot_file_original )

        message = ""

    else:
        message = _get_message( stderr_, return_code )

    return message


def _create_po(
    indicator,
    pot_file,
    po_file_original,
    lingua_code ):

    # http://www.gnu.org/software/gettext/manual/gettext.html#Creating
    po_file_original.parents[ 0 ].mkdir(
        parents = True,
        exist_ok = True )

    stdout_, stderr_, return_code = (
        indicatorbase.IndicatorBase.process_run(
            "msginit "
            f"-i { pot_file } "
            f"-o { po_file_original } "
            f"-l { lingua_code } "
            "--no-translator" ) )

    # On success, msginit writes to stderr, rather than stdout,
    # with a return code of 0.
    #
    # On success, the user must update lines in the created .po file,
    # so pass this message back to the user (which will stop the build).
    #
    # On error, report back to the user.
    if return_code == 0:
        message = stderr_

        lines = indicatorbase.IndicatorBase.read_text_file( po_file_original )
        content = ''.join( lines )
        text = (
            content.
                replace(
                    f"Portable Object Template for { indicator }",
                    f"<English language name for { lingua_code }> translation for { indicator }" ).
                replace(
                    f"Automatically generated, { _get_current_year() }",
                    f"<author name> <<author email>>, { _get_current_year() }" ).
                replace(
                    "Last-Translator: Automatically generated",
                    "Last-Translator: <author name> <<author email>>" ).
                replace(
                    "Language-Team: none",
                    f"Language-Team: <English language name for { lingua_code }>" ) )

        indicatorbase.IndicatorBase.write_text_file( po_file_original, text )

        message += "\nYOU MUST UPDATE LINES 1, 4, 11, 12."

    else:
        message = _get_message( stderr_, return_code )

    return message


def _update_po(
    indicator,
    pot_file,
    po_file_original,
    version_,
    copyright_ ):

    po_file_new = str( po_file_original ).replace( '.po', '.new.po' )
    stdout_, stderr_, return_code = (
        indicatorbase.IndicatorBase.process_run(
            f"msgmerge { po_file_original } { pot_file } -o { po_file_new }" ) )

    # On success, msgmerge writes to stderr, rather than stdout,
    # with a return code of 0.
    # The message is of little use to the end user, so is dropped.
    #
    # On error, report back to the user.
    message = ""
    if return_code == 0:
        lines = indicatorbase.IndicatorBase.read_text_file( po_file_new )
        new = ''.join( lines )
        new = (
            re.sub(
                r"Copyright \(C\).*",
                f"Copyright (C) { copyright_ }.",
                new ) )

        new = (
            re.sub(
                "Project-Id-Version.*",
                f"Project-Id-Version: { indicator } { version_ }\\\\n\"",
                new ) )

        indicatorbase.IndicatorBase.write_text_file( po_file_new, new )

        if filecmp.cmp( po_file_original, po_file_new ):
            os.remove( po_file_new )

        else:
            os.remove( po_file_original )
            os.rename( po_file_new, po_file_original )

    else:
        message = _get_message( stderr_, return_code )

    return message


def _create_update_po(
    indicator,
    linguas_codes,
    version_,
    copyright_ ):

    locale_directory = _get_locale_directory( indicator )
    pot_file = locale_directory / ( indicator + ".pot" )
    message = ""
    for lingua_code in linguas_codes:
        po_file_original = (
            locale_directory /
            lingua_code /
            "LC_MESSAGES" /
            ( indicator + ".po" ) )

        if po_file_original.exists():
            message = (
                _update_po(
                    indicator,
                    pot_file,
                    po_file_original,
                    version_,
                    copyright_ ) )

        else:
            message = (
                _create_po(
                    indicator,
                    pot_file,
                    po_file_original,
                    lingua_code ) )

        if message:
            break

    return message


def _update_locale_source(
    indicator,
    authors_emails,
    start_year,
    version_indicator,
    version_indicatorbase ):
    '''
    Create the .pot file for indicatorbase, if required, otherwise update.
    Create the .pot file for indicator, if required, otherwise update.
    '''
    current_year_author = (
        f"{ _get_current_year() } { authors_emails[ 0 ][ 0 ] }" )

    start_year_indicatorbase = "2017"
    copyright_ = f"{ start_year_indicatorbase }-{ current_year_author }"

    message = (
        _create_update_pot(
            "indicatorbase",
            Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "locale",
            authors_emails,
            version_indicatorbase,
            copyright_ ) )

    if not message:
        message = (
            _create_update_po(
                "indicatorbase",
                _get_linguas_codes( "indicatorbase" ),
                version_indicatorbase,
                copyright_ ) )

    if not message:
        copyright_ = f"{ start_year }-{ current_year_author }"

        message = (
            _create_update_pot(
                indicator,
                Path( '.' ) / indicator / "src" / indicator / "locale",
                authors_emails,
                version_indicator,
                copyright_ ) )

    if not message:
        message = (
            _create_update_po(
                indicator,
                _get_linguas_codes( indicator ),
                version_indicator,
                copyright_ ) )

    return message


def _build_locale_for_release(
    directory_release,
    indicator ):
    '''
    Merge indicatorbase .pot with indicator .pot.
    For each locale, merge indicatorbase .po to indicator .po.
    For each .po, create the .mo.
    '''
    directory_indicator_locale = (
        Path( '.' ) / directory_release / indicator / "src" / indicator / "locale" )

    directory_indicator_base_locale = (
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "locale" )

    message = ""

    # Merge indicatorbase POT with indicator POT.
    stdout_, stderr_, return_code = (
        indicatorbase.IndicatorBase.process_run(
            "msgcat --use-first "
            f"{ str( directory_indicator_locale / ( indicator + '.pot' ) ) } "
            f"{ str( directory_indicator_base_locale / 'indicatorbase.pot' ) } "
            f"-o { str( directory_indicator_locale / ( indicator + '.pot' ) ) }" ) )

    if return_code == 0:
        # For each locale, merge indicatorbase PO with indicator PO.
        for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
            language_code = po.parent.parts[ -2 ]
            stdout_, stderr_, return_code = (
                indicatorbase.IndicatorBase.process_run(
                    "msgcat --use-first "
                    f"{ str( po ) } "
                    f"{ str( directory_indicator_base_locale / language_code / 'LC_MESSAGES' / 'indicatorbase.po' ) } "
                    f"-o { str( po ) } " ) )

            if return_code == 0:
                continue

            message = _get_message( stderr_, return_code )
            break

        if return_code == 0:
            # Create .mo file for each locale.
            for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
                stdout_, stderr_, return_code = (
                    indicatorbase.IndicatorBase.process_run(
                        f"msgfmt { str( po ) } "
                        f"-o { str( po.parent / ( str( po.stem ) + '.mo' ) ) }" ) )

                if return_code == 0:
                    continue

                message = _get_message( stderr_, return_code )
                break

    else:
        message = _get_message( stderr_, return_code )

    return message


def _get_msgstr_from_po(
    po,
    msgid ):

    # The comment for indicatorfortune contains text enclosed with ' which
    # must be escaped.
    msgid_escaped = msgid.replace( "\'", "\\\'" )

    msgstr = ""
    for entry in polib.pofile( po ):
        if entry.msgid == msgid_escaped:
            msgstr = entry.msgstr
            break

    return msgstr


#TODO May not be needed but could be useful...
def _markdown_to_html(
    directory_release,
    indicator ):

    readme_md = directory_release / indicator / "README.md"
    command = f"python3 -m tools.markdown_to_html { readme_md }"

    stdout_, stderr_, return_code = (
        utils.python_run(
            command,
            utils.VENV_BUILD ) )

    if return_code == 0:
        readme_html = Path( readme_md.parent / "README.html" )
        readme_html.rename(
            readme_html.parent / "src" / indicator / "README.html" )

        message = ""

    else:
        message = _get_message( stderr_, return_code )

    return message


def _get_translated_names_and_comments_from_po_files(
    directory_indicator_locale,
    name,
    comments ):
    '''
    Retrieve the translated name/comments for each locale.

    Initially used
        gettext.translation( ... ).gettext( ... )
    to read the translation from the .mo files.

    However, when an entry in the .po file is marked as fuzzy,
    the translation will not appear in the .mo file (by default)
    thereby appearing to be seemingly missing.

    Further, some comments use the \n to split a line so as to not
    be too wide for the About dialog.  When a \n is present,
    the comment is not located within the .mo file.

    Instead, use polib to read the translations from the .po files.
    '''
    names_from_po_files = { }
    comments_from_po_files = { }
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        locale = po.parent.parent.stem

        msgstr = _get_msgstr_from_po( po, name )
        if msgstr and msgstr != name:
            names_from_po_files[ locale ] = msgstr

        msgstr = _get_msgstr_from_po( po, comments )
        if msgstr and msgstr != comments:
            comments_from_po_files[ locale ] = msgstr

    return names_from_po_files, comments_from_po_files


def _check_setuptools():
    '''
    PEP 639 allows the license to be specified in the pyproject.toml
    as its own field.

    This only works in setuptools 77.0.3 and later.

    Ensure the build is on a suitable version.

    https://peps.python.org/pep-0621/#license
    https://packaging.python.org/en/latest/guides/writing-pyproject-toml
    '''

    setuptools_installed_version = (
        indicatorbase.IndicatorBase.versiontuple( version( "setuptools" ) ) )

    setuptools_support_for_pep_639 = (
        indicatorbase.IndicatorBase.versiontuple( "77.0.3" ) )

    message = ""
    if setuptools_installed_version < setuptools_support_for_pep_639:
        message = (
            "Cannot build because setuptools is at version "
            f"{ '.'''.join( map( str, setuptools_installed_version ) ) } "
            "yet requires version "
            f"{ '.'''.join( map( str, setuptools_support_for_pep_639 ) ) } "
            "to handle the 'license' field in pyproject.toml." )

    return message


def _check_for_t_o_d_o_s(
    indicator ):
    ''' Check through EVERY file for a T_O_D_O'''

    paths = [
        "indicatorbase",
        indicator,
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
            for file_ in ( Path( '.' ) / path ).resolve().rglob( file_type ):
                lines = indicatorbase.IndicatorBase.read_text_file( file_ )
                if t_o_d_o in ''.join( lines ).lower():
                    message += f"\t{ file_ }\n"

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
    indicator,
    directory_out ):

    indicator_pyproject_toml = (
        Path( '.' ) / indicator / "pyprojectspecific.toml" )

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
        f"\"{ indicator }\"" )

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
            config_indicator.get( "project", "dependencies" ) )

    out_pyproject_toml = directory_out / indicator / "pyproject.toml"

    with open( out_pyproject_toml, 'w', encoding = "utf-8" ) as f:
        config_indicatorbase.write( f )

    _chmod(
        out_pyproject_toml,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )

    return out_pyproject_toml, version_indicatorbase


def _create_manifest_dot_in(
    indicator,
    directory_out ):

    indicatorbase_manifest_in = (
        Path( '.' ) / "indicatorbase" / "MANIFESTbase.in" )

    content = (
        indicatorbase.IndicatorBase.read_text_file( indicatorbase_manifest_in ) )

    manifest_text = ''.join( content ).replace( "{indicator}", indicator )

    indicator_manifest_in = (
        Path( '.' ) / indicator / "MANIFESTspecific.in" )

    if Path( indicator_manifest_in ).exists():
        content = (
            indicatorbase.IndicatorBase.read_text_file( indicator_manifest_in ) )

        manifest_text += ''.join( content ).replace( "{indicator}", indicator )

    release_manifest_in = directory_out / indicator / "MANIFEST.in"

    indicatorbase.IndicatorBase.write_text_file(
        release_manifest_in,
        manifest_text + '\n' )

    _chmod(
        release_manifest_in,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )


def _get_version_in_changelog_markdown(
    changelog_markdown ):

    version_ = ""
    lines = indicatorbase.IndicatorBase.read_text_file( changelog_markdown )
    for line in lines:
        if line.startswith( "## v" ):
            version_ = line.split( ' ' )[ 1 ][ 1 : ]
            break

    return version_


def _create_dot_desktop(
    directory_platform_linux,
    indicator,
    name,
    names_from_po_files,
    comments,
    comments_from_po_files,
    categories ):

    indicatorbase_dot_desktop_path = (
        Path( '.' ) /
        "indicatorbase" /
        "src" /
        "indicatorbase" /
        "platform" /
        "linux" /
        "indicatorbase.py.desktop" )

    dot_desktop_text = ""

    lines = (
        indicatorbase.IndicatorBase.read_text_file(
            indicatorbase_dot_desktop_path ) )

    for line in lines:
        if not line.startswith( '#' ):
            dot_desktop_text += line

    names = name
    for language, name_ in names_from_po_files.items():
        names += f"\nName[{ language }]={ name_ }"

    # Some indicators use a \n to split the comment so not be too long when
    # displayed in the About dialog.
    #
    # For the .desktop file, do not split the comment.
    comments_ = comments.replace( "\\n", ' ' )
    newline = '\n'
    for language, comment in comments_from_po_files.items():
        comments_ += f"\nComment[{ language }]={ comment.replace( newline, ' ' ) }"

    dot_desktop_text = (
        dot_desktop_text.format(
            indicator = indicator,
            names = "Name=" + names,
            comment = "Comment=" + comments_,
            categories = categories ) )

    indicator_dot_desktop_path = (
        directory_platform_linux / ( indicator + ".py.desktop" ) )

    indicatorbase.IndicatorBase.write_text_file(
        indicator_dot_desktop_path,
        dot_desktop_text + '\n' )

    _chmod(
        indicator_dot_desktop_path,
        stat.S_IRUSR | stat.S_IWUSR,
        stat.S_IRGRP,
        stat.S_IROTH )


def _create_scripts_for_linux(
    directory_platform_linux,
    indicator ):

    indicatorbase_platform_linux_path = (
        Path( '.' ) /
        "indicatorbase" /
        "src"
        /
        "indicatorbase" /
        "platform" /
        "linux" )

    def process(
        source_script_name,
        destination_script_name ):

        source = indicatorbase_platform_linux_path / source_script_name
        text = ''.join( indicatorbase.IndicatorBase.read_text_file( source ) )
        text = text.replace( "{indicator}", indicator )
        text = text.replace( "{venv_indicators}", utils.VENV_INSTALL )

        destination = directory_platform_linux / destination_script_name

        indicatorbase.IndicatorBase.write_text_file( destination, text + '\n' )

        _chmod(
            destination,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR,
            stat.S_IRGRP | stat.S_IXGRP,
            stat.S_IROTH | stat.S_IXOTH )


    process( "run.sh", indicator + ".sh" )

    install_script = "install.sh"
    process( install_script, install_script )

    uninstall_script = "uninstall.sh"
    process( uninstall_script, uninstall_script )


def _create_symbolic_icons(
    directory_wheel,
    indicator ):

    regular_expressions = [ r"fill:#", r"stroke:#" ]

    directory_icons = (
        directory_wheel /
        indicator /
        "src" /
        indicator /
        "icons" )

    hicolor_icons = list( ( Path( '.' ) / directory_icons ).glob( "*.svg" ) )

    for hicolor_icon in hicolor_icons:
        symbolic_svg = (
            ''.join( indicatorbase.IndicatorBase.read_text_file( hicolor_icon ) ) )

        for regular_expression in regular_expressions:
            symbolic_svg = (
                re.sub(
                    regular_expression + r"([a-fA-F0-9]){6}",
                    regular_expression + "777777",
                    symbolic_svg ) )

        symbolic_icon = (
            hicolor_icon.parent /
            ( str( hicolor_icon.stem ) + "-symbolic.svg" ) )

        indicatorbase.IndicatorBase.write_text_file(
            symbolic_icon,
            symbolic_svg )


def _package_source(
    directory_dist,
    indicator ):

    directory_indicator = directory_dist / indicator

    # Copy the ENTIRE project across and create a pyproject.toml and MANIFEST.in
    # by combining those from indicatorbase and the indicator to include/exclude
    # files/folders in the build.
    shutil.copytree( indicator, directory_indicator )

    shutil.copy(
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "indicatorbase.py",
        Path( '.' ) / directory_indicator / "src" / indicator )

    pyproject_toml, version_indicator_base = (
        _create_pyproject_dot_toml( indicator, directory_dist ) )

    _create_manifest_dot_in( indicator, directory_dist )

    config = configparser.ConfigParser()
    config.read( pyproject_toml )

    version_from_pyproject_toml = (
        config.get( "project", "version" ).replace( "\"", '' ).strip() )

    changelog_markdown = (
        Path( indicator ) / "src" / indicator / "CHANGELOG.md" )

    version_from_changelog_markdown = (
        _get_version_in_changelog_markdown( changelog_markdown ) )

    message = ""
    if version_from_pyproject_toml != version_from_changelog_markdown:
        message = (
            f"{ indicator }: The most recent version in " +
            "CHANGELOG.md does not match that in pyprojectspecific.toml\n" )

    if not message:
        authors_emails = utils.get_pyproject_toml_authors( config )
        start_year = (
            indicatorbase.IndicatorBase.get_year_in_changelog_markdown(
                changelog_markdown ) )

        message = (
            _update_locale_source(
                indicator,
                authors_emails,
                start_year,
                version_from_pyproject_toml,
                version_indicator_base ) )

    if not message:
        message = _build_locale_for_release( directory_dist, indicator )

    if not message:
        name_human_readable, categories, comments, message = (
            utils.get_name_categories_comments_from_indicator(
                indicator,
                directory_indicator ) )

    if not message:
        utils_readme.build_readme_for_wheel(
            directory_indicator,
            indicator,
            authors_emails,
            start_year )

#TODO I don't think this is required...
        # message = _markdown_to_html( directory_dist, indicator )

    if not message:
        directory_indicator_locale = (
            Path( '.' ) / directory_indicator / "src" / indicator / "locale" )

        names_from_po_files, comments_from_po_files = (
            _get_translated_names_and_comments_from_po_files(
                directory_indicator_locale,
                name_human_readable,
                comments ) )

        directory_platform_linux = (
            directory_dist /
            indicator /
            "src" /
            indicator /
            "platform" /
            "linux" )

        directory_platform_linux.mkdir( parents = True )

        _create_dot_desktop(
            directory_platform_linux,
            indicator,
            name_human_readable,
            names_from_po_files,
            comments,
            comments_from_po_files,
            categories )

        _create_scripts_for_linux(
            directory_platform_linux,
            indicator )

        _create_symbolic_icons(
            directory_dist,
            indicator )

        # If an indicator has a build script located at
        #   { indicator } / tools / _build_wheel.py
        # with a function called
        #   build( out_path )
        # that function will be called now.
        #
        # For example, indicatorlunar's astroskyfield requires planets.bsp
        # and stars.dat to be built and included as part of the wheel which
        # can be done in the indicator's build script.
        #
        # Note that any messages written to stdout by the indicator's build
        # script will appear AFTER the messages written by the Python3 build
        # process despite happening BEFORE!
        indicator_build_script = Path( indicator ) / "tools" / "_build_wheel.py"
        if Path( indicator_build_script ).exists():
            module = f"{ indicator }.tools._build_wheel"
            indicator_build_wheel = importlib.import_module( module )
            out_path = directory_dist / indicator / "src" / indicator
            message = indicator_build_wheel.build( out_path )

    return message


def build_wheel(
    indicator ):
    '''
    Build the wheel for the indicator.
    '''
    message = ""

#TODO Put back in on release
    # message = _check_setuptools()

#TODO Put back in on release
    # if not message:
    #     message = _check_for_t_o_d_o_s( indicator )

    if not message:
        directory_dist = (
            Path( '.' ) /
            utils.RELEASE_DIRECTORY /
            "wheel" /
            ( "dist_" + indicator ) )

        if Path( directory_dist ).exists():
            shutil.rmtree( str( directory_dist ) )

        directory_dist.mkdir( parents = True )

        message = _package_source( directory_dist, indicator )

    if not message:
        command = (
            "python3 -m build --outdir "
            f"{ directory_dist } { directory_dist / indicator }" )

        stdout_, stderr_, return_code = (
            indicatorbase.IndicatorBase.process_run( command ) )

        message = ""
        if return_code == 0:
            message = stdout_

        else:
            message = _get_message( stderr_, return_code )

    sys.stdout.write( message )
