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
import gettext
import os
import re
import subprocess

from pathlib import Path

from . import build_wheel


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
    subprocess.run(
        f"xgettext " +
        f"-f { locale_directory / 'POTFILES.in' } " +
        f"-D { str( Path( indicator_name ) / 'src' / indicator_name ) } " +
        f"--copyright-holder='{ authors_emails[ 0 ][ 0 ] }.' " +
        f"--package-name={ indicator_name } " +
        f"--package-version={ version } " +
        f"--msgid-bugs-address='<{ authors_emails[ 0 ][ 1 ] }>' " +
        f"-o { pot_file_new }",
        shell = True )

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

            subprocess.run(
                f"msgmerge { po_file_original } { pot_file } " +
                f"-o { po_file_new }",
                shell = True )

            with open( po_file_new, 'r', encoding = "utf-8" ) as r:
                new = r.read()

                new = (
                    re.sub(
                        "Copyright \(C\).*",
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

            subprocess.run(
                f"msginit " +
                f"-i { pot_file } " +
                f"-o { po_file_original } " +
                f"-l { lingua_code } " +
                f"--no-translator",
                shell = True )

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
                        f"Last-Translator: Automatically generated",
                        f"Last-Translator: <author name> <<author email>>" ).
                    replace(
                        f"Language-Team: none",
                        f"Language-Team: <English language name for { lingua_code }>" ) )

            with open( po_file_original, 'w', encoding = "utf-8" ) as w:
                w.write( text )

            print( f"YOU MUST UPDATE LINES 1, 4, 11, 12." )


def _get_msgstr_from_po( po, msgid ):
    result = (
        subprocess.run(
            f". { build_wheel.VENV_DEVELOPMENT }/bin/activate && " +
            f"python3 -c \"" +
            f"import polib; " +
            f"[ " +
            f"    print( entry.msgstr ) " +
            f"    for entry in polib.pofile( '{ po }' ) " +
            f"    if entry.msgid == '{ msgid }'  ]" +
            f"\"",
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell = True,
            check = False ) )

    stderr_ = result.stderr.decode()
    if stderr_:
        message = f"Error retrieving '{ msgid }' from { po }."
        msgstr = ""

    else:
        msgstr = result.stdout.decode().strip()
        message = ""

    return msgstr, message

    
def update_locale_source(
    indicator_name,
    authors_emails,
    start_year,
    version_indicator,
    version_indicatorbase):
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
    subprocess.run(
        "msgcat --use-first " +
        f"{ str( directory_indicator_locale / ( indicator_name + '.pot' ) ) } " +
        f"{ str( directory_indicator_base_locale / 'indicatorbase.pot' ) } " +
        f"-o { str( directory_indicator_locale / ( indicator_name + '.pot' ) ) }",
        shell = True )

    # For each locale, merge indicatorbase PO with indicator PO.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        language_code = po.parent.parts[ -2 ]
        subprocess.run(
            f"msgcat --use-first " +
            f"{ str( po ) } " +
            f"{ str( directory_indicator_base_locale / language_code / 'LC_MESSAGES' / 'indicatorbase.po' ) } " +
            f"-o { str( po ) } ",
            shell = True )

    # Create .mo files.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        subprocess.run(
            f"msgfmt { str( po ) } " +
            f"-o { str( po.parent / ( str( po.stem ) + '.mo' ) ) }",
            shell = True )


#TODO Check
def get_names_and_comments_from_po_files(
    directory_indicator_locale,
    name,
    comments ):
    '''
    Retrieve the translated name/comments for each locale.
    '''

    names_from_po_files = { }
    comments_from_po_files = { }
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        locale = po.parent.parent.stem

#TODO Keep these links?
        # https://stackoverflow.com/q/54638570/2156453
        # https://www.reddit.com/r/learnpython/comments/jkun99/how_do_i_load_a_specific_mo_file_by_giving_its

#TODO When a .po contains fuzzy, that translation will NOT appear in the .mo
# That means the name/comment may not be found.
# Need to handle.
# Maybe put in a check for \n and burp to the user?
# Do it here or above when the pot/po is generated?
#
# EXPLAIN WHY THIS NEW WAY IS BEING USED.

        msgstr, error = _get_msgstr_from_po( po, name )
        if msgstr:
            if msgstr != name:
                names_from_po_files[ locale ] = msgstr

            msgstr, error = _get_msgstr_from_po( po, comments )
            if msgstr:
                if msgstr != comments:
                    comments_from_po_files[ locale ] = msgstr.replace( '\n', ' ' )

        if error:
            break

#TODO Testing
    print( name )
    print( names_from_po_files )
    print()
    print( comments )
    print( comments_from_po_files )

    return names_from_po_files, comments_from_po_files, error
