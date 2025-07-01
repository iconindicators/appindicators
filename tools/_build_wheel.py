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
Utility for building a Python3 wheel.

  *** NOT TO BE RUN DIRECTLY ***
'''


#TODO
# Add comments to py project toml in regards to why pygobject is not in there
#
# Also somehow want to note why (eventually) ephem and skyfield are not in the toml file.
# Is there a way of extracting a comment from indicator lunar tomll file and
# place it into the main toml?


import configparser
import datetime
import filecmp
import importlib
import os
import re
import shutil
import stat
import sys

# Will be installed by the calling script.
import polib

from pathlib import Path

if "../" not in sys.path:
    sys.path.insert( 0, "../" )

from indicatorbase.src.indicatorbase import indicatorbase

from . import _markdown_to_html
from . import utils
from . import utils_readme


def _get_linguas_codes(
    indicator ):

    linguas_codes = [ ]
    with open( _get_linguas( indicator ), 'r', encoding = "utf-8" ) as f:
        for line in f:
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


def _create_update_pot(
    indicator,
    locale_directory,
    authors_emails,
    version,
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
            f"--package-version={ version } "
            f"--msgid-bugs-address='<{ authors_emails[ 0 ][ 1 ] }>' "
            f"-o { pot_file_new }" ) )

    message = ""
    if stderr_:
        message = stderr_

    elif return_code != 0:
        message = f"Return code: { return_code }"

    if not message:
        with open( pot_file_new, 'r', encoding = "utf-8" ) as r:
            text = (
                r.read().
                replace(
                    "SOME DESCRIPTIVE TITLE",
                    f"Portable Object Template for { indicator }" ).
                replace( f"YEAR { authors_emails[ 0 ][ 0 ] }", copyright_ ).
                replace(
                    "FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.\n#\n#, fuzzy",
                    "FIRST AUTHOR <EMAIL@ADDRESS>, YEAR."  ).
                replace( "CHARSET", "UTF-8" ) )

        with open( pot_file_new, 'w', encoding = "utf-8" ) as w:
            w.write( text )

        if pot_file_new.endswith( ".new.pot" ):
            pot_file_original = f"{ locale_directory / indicator }.pot"
            original = ""
            with open( pot_file_original, 'r', encoding = "utf-8" ) as f:
                for line in f:
                    if "POT-Creation-Date" not in line:
                        original += line

            new = ""
            with open( pot_file_new, 'r', encoding = "utf-8" ) as f:
                for line in f:
                    if "POT-Creation-Date" not in line:
                        new += line

            if original == new:
                os.remove( pot_file_new )

            else:
                os.remove( pot_file_original )
                os.rename( pot_file_new, pot_file_original )

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

    # On success, msginit will write to stderr, rather than stdout,
    # with a return code of 0.  In this case the user will need to
    # update some lines in the created .po file.
    #
    # On error, report back to the user.
    print( f"return code { return_code }")
    if return_code == 0:
        if stdout_:
            message = stdout_.strip()  #TODO Should be empty.
            print( "stdout" )

        else:
            message = stderr_.strip()
            print("stderr")

        print( f"message1: {message}")

    else:
        if stderr_:
            message = stderr_.strip()

        else:
            message = f"Return code: { return_code }"

        print( f"message2: {message}")

    print( f"stdout: {stdout_.strip()}")
    print( f"stderr: {stderr_.strip()}")
    print( f"return code: {return_code}")

    if return_code == 0:
        with open( po_file_original, 'r', encoding = "utf-8" ) as r:
            text = (
                r.read().
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

        with open( po_file_original, 'w', encoding = "utf-8" ) as w:
            w.write( text )

        message += "\nYOU MUST UPDATE LINES 1, 4, 11, 12."
        print( f"message3: {message}")

    return message


def _update_po(
    indicator,
    pot_file,
    po_file_original,
    version,
    copyright_ ):

    po_file_new = str( po_file_original ).replace( '.po', '.new.po' )
    stdout_, stderr_, return_code = (
        indicatorbase.IndicatorBase.process_run(
            f"msgmerge { po_file_original } { pot_file } -o { po_file_new }" ) )
#TODO Print the above line, run from terminal to see the output.

    message = ""
    if stderr_:
        message = stderr_

    elif return_code != 0:
        message = f"Return code: { return_code }"

    else:
        with open( po_file_new, 'r', encoding = "utf-8" ) as r:
            new = r.read()

            new = (
                re.sub(
                    r"Copyright \(C\).*",
                    f"Copyright (C) { copyright_ }.",
                    new ) )

            new = (
                re.sub(
                    "Project-Id-Version.*",
                    f"Project-Id-Version: { indicator } { version }\\\\n\"",
                    new ) )

            with open( po_file_new, 'w', encoding = "utf-8" ) as w:
                w.write( new )

        if filecmp.cmp( po_file_original, po_file_new ):
            os.remove( po_file_new )

        else:
            os.remove( po_file_original )
            os.rename( po_file_new, po_file_original )

    return message


def _create_update_po(
    indicator,
    linguas_codes,
    version,
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
                    version,
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
        
        print( 888888888888888 )
        print( message )
        print( 99999999999999999999)

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

    # Merge indicatorbase POT with indicator POT.
    stdout_, stderr_, return_code = (
        indicatorbase.IndicatorBase.process_run(
            "msgcat --use-first "
            f"{ str( directory_indicator_locale / ( indicator + '.pot' ) ) } "
            f"{ str( directory_indicator_base_locale / 'indicatorbase.pot' ) } "
            f"-o { str( directory_indicator_locale / ( indicator + '.pot' ) ) }" ) )

    if stderr_:
        message = stderr_

    elif return_code != 0:
        message = f"Return code: { return_code }"

    if not message:
        # For each locale, merge indicatorbase PO with indicator PO.
        for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
            language_code = po.parent.parts[ -2 ]
            stdout_, stderr_, return_code = (
                indicatorbase.IndicatorBase.process_run(
                    "msgcat --use-first "
                    f"{ str( po ) } "
                    f"{ str( directory_indicator_base_locale / language_code / 'LC_MESSAGES' / 'indicatorbase.po' ) } "
                    f"-o { str( po ) } " ) )

            if stderr_:
                message = stderr_

            elif return_code != 0:
                message = f"Return code: { return_code }"

            if message:
                break

    if not message:
        # Create .mo files.
        for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
            stdout_, stderr_, return_code = (
                indicatorbase.IndicatorBase.process_run(
                    f"msgfmt { str( po ) } "
                    f"-o { str( po.parent / ( str( po.stem ) + '.mo' ) ) }" ) )

            if stderr_:
                message = stderr_

            elif return_code != 0:
                message = f"Return code: { return_code }"

            if message:
                break

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


def _check_for_t_o_d_o_s(
    indicator ):

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

    with open( indicatorbase_manifest_in, 'r', encoding = "utf-8" ) as f:
        manifest_text = f.read().replace( "{indicator}", indicator )

    indicator_manifest_in = (
        Path( '.' ) / indicator / "MANIFESTspecific.in" )

    if Path( indicator_manifest_in ).exists():
        with open( indicator_manifest_in, 'r', encoding = "utf-8" ) as f:
            manifest_text += f.read().replace( "{indicator}", indicator )

    release_manifest_in = directory_out / indicator / "MANIFEST.in"
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


def _get_name_categories_comments_from_indicator(
    indicator,
    directory_indicator ):

    def parse( line ):
        return line.split( '\"' )[ 1 ].replace( '\"', '' ).strip()


    indicator_source = (
        Path( '.' ) /
        directory_indicator /
        "src" /
        indicator /
        ( indicator + ".py" ) )

    name = ""
    categories = ""
    comments = ""
    message = ""
    with open( indicator_source, 'r', encoding = "utf-8" ) as f:
        for line in f:
            if re.search( r"INDICATOR_NAME_HUMAN_READABLE = _\( ", line ):
                name = parse( line )

            if re.search( r"INDICATOR_CATEGORIES = ", line ):
                categories = parse( line )

            if re.search( r"comments = _\(", line ):
                comments = parse( line )

    if name == "":
        message += f"ERROR: Unable to obtain 'indicator_name' from \n\t{ indicator_source }\n"

    if categories == "":
        message += f"ERROR: Unable to obtain 'categories' from \n\t{ indicator_source }\n"

    if comments == "":
        message += f"ERROR: Unable to obtain 'comments' from the constructor of\n\t{ indicator_source }\n"

    return name, categories, comments, message


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
    with open( indicatorbase_dot_desktop_path, 'r', encoding = "utf-8" ) as f:
        while line := f.readline():
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

    with open( indicator_dot_desktop_path, 'w', encoding = "utf-8" ) as f:
        f.write( dot_desktop_text + '\n' )

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
        with open( source, 'r', encoding = "utf-8" ) as f:
            text = f.read()

        destination = directory_platform_linux / destination_script_name
        with open( destination, 'w', encoding = "utf-8" ) as f:
            text = text.replace( "{indicator}", indicator )
            text = text.replace( "{venv_indicators}", utils.VENV_INSTALL )
            f.write( text + '\n' )

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


#TODO Perhaps create the symbolic icons and commit to repository instead of creating each time?
def _create_symbolic_icons(
    directory_wheel,
    indicator ):

    directory_icons = (
        directory_wheel /
        indicator /
        "src" /
        indicator /
        "icons" )

    for hicolor_icon in list( ( Path( '.' ) / directory_icons ).glob( "*.svg" ) ):
        symbolic_icon = (
            directory_icons
            /
            ( str( hicolor_icon.name )[ 0 : -4 ] + "-symbolic.svg" ) )

        shutil.copy( hicolor_icon, symbolic_icon )
        with open( symbolic_icon, 'r', encoding = "utf-8" ) as f:
            svg_text = f.read()
            for m in re.finditer( r"fill:#", svg_text ):
                svg_text = (
                    svg_text[ 0 : m.start() + 6 ]
                    +
                    "777777"
                    +
                    svg_text[ m.start() + 6 + 6 : ] )

            for m in re.finditer( r"stroke:#", svg_text ):
                svg_text = (
                    svg_text[ 0 : m.start() + 6 ]
                    +
                    "777777"
                    +
                    svg_text[ m.start() + 6 + 6 : ] )

        with open( symbolic_icon, 'w', encoding = "utf-8" ) as f:
            f.write( svg_text + '\n' )


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
        authors = _get_pyproject_toml_authors( config )
        start_year = (
            indicatorbase.IndicatorBase.get_year_in_changelog_markdown(
                changelog_markdown ) )

        message = (
            _update_locale_source(
                indicator,
                authors,
                start_year,
                version_from_pyproject_toml,
                version_indicator_base ) )

    if not message:
        message = _build_locale_for_release( directory_dist, indicator )

    if not message:
        name, categories, comments, message = (
            _get_name_categories_comments_from_indicator(
                indicator,
                directory_indicator ) )

    if not message:
        utils_readme.create_readme(
            directory_indicator,
            indicator,
            name,
            authors,
            start_year )

#TODO Note as of version 43.0
# https://pypi.org/project/readme-renderer/43.0/
# only python 3.8 is supported so may have to pin.
# May need a function similar to get_pygobject()
# https://docs.python.org/3/library/sys.html#sys.version
#
#TODO Test that this works given markdown moved to a backend module.
        _markdown_to_html.markdown_to_html(
            f"{ directory_dist }/{ indicator }/README.md",
            f"{ directory_dist }/{ indicator }/src/{ indicator }/README.html" )

        directory_indicator_locale = (
            Path( '.' ) / directory_indicator / "src" / indicator / "locale" )

        names_from_po_files, comments_from_po_files = (
            _get_translated_names_and_comments_from_po_files(
                directory_indicator_locale,
                name,
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
            name,
            names_from_po_files,
            comments,
            comments_from_po_files,
            categories )

        _create_scripts_for_linux( directory_platform_linux, indicator )
        _create_symbolic_icons( directory_dist, indicator )

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

    # message = _check_for_t_o_d_o_s( indicator ) #TODO Uncomment
    message = ""
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

    print( 1 )
    if not message:
        print( 2 )
        command = (
            "python3 -m build --outdir "
            f"{ directory_dist } { directory_dist / indicator }" )

        stdout_, stderr_, return_code = (
            indicatorbase.IndicatorBase.process_run( command ) )

        print( 3 )
        message = ""
        if stderr_:
            message = stderr_

        elif return_code != 0:
            message = f"Return code: { return_code }"

    else:
        print( 4 )
        print( message )
        print( 5 )

# TODO Uncomment
#    shutil.rmtree( directory_dist / indicator )

#TODO I'm expecting to see more output (from the build command at least)
# but nothing...why?    
    # if message:
    #     print( 5 )
    #     print( message )
    
    return message
