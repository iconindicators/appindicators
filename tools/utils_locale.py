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
Create/update the .pot/.po files for indicatorbase and an indicator's source.
Create merged .pot/.po files and create the .mo file for an indicator's release.

https://www.gnu.org/software/gettext/manual/gettext.html
https://www.gnu.org/software/trans-coord/manual/gnun/html_node/PO-Header.html
https://www.labri.fr/perso/fleury/posts/programming/a-quick-gettext-tutorial.html
'''


import datetime
import filecmp
import os
import re
import sys

from pathlib import Path

if '../' not in sys.path:
    sys.path.insert( 0, '../' ) # Allows calls to IndicatorBase.

from indicatorbase.src.indicatorbase.indicatorbase import IndicatorBase


def _get_linguas_codes(
    indicator_name ):

    lingua_codes = [ ]
    with open( _get_linguas( indicator_name ), 'r', encoding = "utf-8" ) as f:
        for line in f:
            if not line.startswith( '#' ):
                lingua_codes = line.split()

    return lingua_codes


def _get_locale_directory(
    indicator_name ):

    return Path( '.' ) / indicator_name / "src" / indicator_name / "locale"


def _get_linguas(
    indicator_name ):

    # The LINGUAS file lists each supported language/locale:
    #   http://www.gnu.org/software/gettext/manual/gettext.html#po_002fLINGUAS
    return _get_locale_directory( indicator_name ) / "LINGUAS"


def _get_current_year():
    return datetime.datetime.now( datetime.timezone.utc ).strftime( '%Y' )


def _create_update_pot(
    indicator_name,
    locale_directory,
    authors_emails,
    version,
    copyright_ ):

    pot_file_new = f"{ locale_directory / indicator_name }.pot"
    if Path( pot_file_new ).exists():
        pot_file_new = f"{ locale_directory / indicator_name }.new.pot"

    # Create a POT based on current source:
    #   http://www.gnu.org/software/gettext/manual/gettext.html
    IndicatorBase.process_run(
        "xgettext "
        f"-f { locale_directory / 'POTFILES.in' } "
        f"-D { str( Path( indicator_name ) / 'src' / indicator_name ) } "
        f"--copyright-holder='{ authors_emails[ 0 ][ 0 ] }.' "
        f"--package-name={ indicator_name } "
        f"--package-version={ version } "
        f"--msgid-bugs-address='<{ authors_emails[ 0 ][ 1 ] }>' "
        f"-o { pot_file_new }",
        capture_output = False,
        print_ = True )

    with open( pot_file_new, 'r', encoding = "utf-8" ) as r:
        text = (
            r.read().
            replace(
                "SOME DESCRIPTIVE TITLE",
                f"Portable Object Template for { indicator_name }" ).
            replace( f"YEAR { authors_emails[ 0 ][ 0 ] }", copyright_ ).
            replace(
                "FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.\n#\n#, fuzzy",
                "FIRST AUTHOR <EMAIL@ADDRESS>, YEAR."  ).
            replace( "CHARSET", "UTF-8" ) )

    with open( pot_file_new, 'w', encoding = "utf-8" ) as w:
        w.write( text )

    if pot_file_new.endswith( ".new.pot" ):
        pot_file_original = f"{ locale_directory / indicator_name }.pot"
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


def _create_update_po(
    indicator_name,
    linguas_codes,
    version,
    copyright_ ):

    locale_directory = _get_locale_directory( indicator_name )
    pot_file = locale_directory / ( indicator_name + ".pot" )
    for lingua_code in linguas_codes:
        po_file_original = (
            locale_directory /
            lingua_code /
            "LC_MESSAGES" /
            ( indicator_name + ".po" ) )

        if po_file_original.exists():
            po_file_new = str( po_file_original ).replace( '.po', '.new.po' )
            IndicatorBase.process_run(
                f"msgmerge { po_file_original } { pot_file } "
                f"-o { po_file_new }",
                capture_output = False,
                print_ = True )

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
                        f"Project-Id-Version: { indicator_name } { version }\\\\n\"",
                        new ) )

                with open( po_file_new, 'w', encoding = "utf-8" ) as w:
                    w.write( new )

            if filecmp.cmp( po_file_original, po_file_new ):
                os.remove( po_file_new )

            else:
                os.remove( po_file_original )
                os.rename( po_file_new, po_file_original )

        else:
            # http://www.gnu.org/software/gettext/manual/gettext.html#Creating
            po_file_original.parents[ 0 ].mkdir(
                parents = True,
                exist_ok = True )

            IndicatorBase.process_run(
                "msginit "
                f"-i { pot_file } "
                f"-o { po_file_original } "
                f"-l { lingua_code } "
                "--no-translator",
                capture_output = False,
                print_ = True )

            with open( po_file_original, 'r', encoding = "utf-8" ) as r:
                text = (
                    r.read().
                    replace(
                        f"Portable Object Template for { indicator_name }",
                        f"<English language name for { lingua_code }> translation for { indicator_name }" ).
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

            print( "YOU MUST UPDATE LINES 1, 4, 11, 12." )


def _get_msgstr_from_po(
        venv_build,
        po,
        msgid ):

    # The comment for indicatorfortune contains text enclosed with ' which
    # must be escaped.
    msgid_escaped = msgid.replace( "\'", "\\\'" )

    stdout_, stderr_, return_code = (
        IndicatorBase.process_run(
            f". { venv_build }/bin/activate && "
            "python3 -c \""
            "import polib; "
            "[ print( entry.msgstr ) "
            f"for entry in polib.pofile( \'{ po }\' ) "
            f"if entry.msgid == \'{ msgid_escaped }\' ]"
            "\"",
            print_ = True ) )

    if stdout_:
        message = ""
        msgstr = stdout_

    else:
        message = f"Error retrieving\n\t{ msgid }\nfrom\n\t{ po }:\n\n{ stderr_ }"
        msgstr = ""

    return msgstr, message


def update_locale_source(
    indicator_name,
    authors_emails,
    start_year,
    version_indicator,
    version_indicatorbase ):
    '''
    Create the .pot file for indicatorbase, if required, otherwise update.
    Create the .pot file for indicator_name, if required, otherwise update.
    '''

    current_year_author = (
        f"{ _get_current_year() } { authors_emails[ 0 ][ 0 ] }" )

    start_year_indicatorbase = "2017"
    copyright_ = f"{ start_year_indicatorbase }-{ current_year_author }"

    _create_update_pot(
        "indicatorbase",
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "locale",
        authors_emails,
        version_indicatorbase,
        copyright_ )


    _create_update_po(
        "indicatorbase",
        _get_linguas_codes( "indicatorbase" ),
        version_indicatorbase,
        copyright_ )

    copyright_ = f"{ start_year }-{ current_year_author }"

    _create_update_pot(
        indicator_name,
        Path( '.' ) / indicator_name / "src" / indicator_name / "locale",
        authors_emails,
        version_indicator,
        copyright_ )

    _create_update_po(
        indicator_name,
        _get_linguas_codes( indicator_name ),
        version_indicator,
        copyright_ )


def build_locale_for_release(
    directory_release,
    indicator_name ):
    '''
    Merge indicatorbase .pot with indicator_name .pot.
    For each locale, merge indicatorbase .po to indicator_name .po.
    For each .po, create the .mo.
    '''

    directory_indicator_locale = (
        Path( '.' ) / directory_release / indicator_name / "src" / indicator_name / "locale" )

    directory_indicator_base_locale = (
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "locale" )

    # Merge indicatorbase POT with indicator POT.
    IndicatorBase.process_run(
        "msgcat --use-first "
        f"{ str( directory_indicator_locale / ( indicator_name + '.pot' ) ) } "
        f"{ str( directory_indicator_base_locale / 'indicatorbase.pot' ) } "
        f"-o { str( directory_indicator_locale / ( indicator_name + '.pot' ) ) }",
        capture_output = False,
        print_ = True )

    # For each locale, merge indicatorbase PO with indicator PO.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        language_code = po.parent.parts[ -2 ]
        IndicatorBase.process_run(
            "msgcat --use-first "
            f"{ str( po ) } "
            f"{ str( directory_indicator_base_locale / language_code / 'LC_MESSAGES' / 'indicatorbase.po' ) } "
            f"-o { str( po ) } ",
            capture_output = False,
            print_ = True )

    # Create .mo files.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        IndicatorBase.process_run(
            f"msgfmt { str( po ) } "
            f"-o { str( po.parent / ( str( po.stem ) + '.mo' ) ) }",
            capture_output = False,
            print_ = True )


def get_names_and_comments_from_po_files(
    venv_build,
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
        msgstr, error = _get_msgstr_from_po( venv_build, po, name )
        if msgstr:
            if msgstr != name:
                names_from_po_files[ locale ] = msgstr

            msgstr, error = _get_msgstr_from_po( venv_build, po, comments )
            if msgstr:
                if msgstr != comments:
                    comments_from_po_files[ locale ] = msgstr

        if error:
            break

    return names_from_po_files, comments_from_po_files, error
