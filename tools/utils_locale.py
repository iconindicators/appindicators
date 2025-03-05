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
'''


import datetime
import gettext
import subprocess

from pathlib import Path


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

    potfiles_in = locale_directory / "POTFILES.in"
    input_files_search_directory = (
        Path( '.' ) / indicator_name / "src" / indicator_name )

    # Use xgettext to create a new POT file and sed to insert some other text:
    #   http://www.gnu.org/software/gettext/manual/gettext.html
    subprocess.run( [
        f"xgettext",
        f"--files-from={ potfiles_in }",
        f"--directory={ input_files_search_directory }",
        f"--copyright-holder={ authors_emails[ 0 ][ 0 ] }",
        f"--package-name={ indicator_name }",
        f"--package-version={ version }",
        f"--msgid-bugs-address=<{ authors_emails[ 0 ][ 1 ] }>",
        f"--no-location",
        f"--no-wrap",
        f"--output={ pot_file_new }" ] )

    some_descriptive_title = f"Portable Object Template for { indicator_name }"
    subprocess.run( [
        f"sed",
        f"--in-place",
        f"s/SOME DESCRIPTIVE TITLE/{ some_descriptive_title }/ ; " +
        f"s/YEAR { authors_emails[ 0 ][ 0 ] }/{ copyright_ }/ ; " +
        f"s/CHARSET/UTF-8/",
        f"{ pot_file_new }" ] )

    if pot_file_new.endswith( ".new.pot" ):
        pot_file_original = f"{ locale_directory / indicator_name }.pot"
        command = [
            f"diff",
            f"<( sed '/POT-Creation-Date/d' { pot_file_original } )",
            f"<( sed '/POT-Creation-Date/d' { pot_file_new } )" ]

        result = subprocess.run( command, capture_output = True, text = True )
        if result.stdout:
            subprocess.run( [
                f"rm",
                f"{ pot_file_original }" ] )

            subprocess.run( [
                f"mv",
                f"{ pot_file_new }",
                f"{ pot_file_original }" ] )

        else:
            subprocess.run( [
                f"rm",
                f"{ pot_file_new }" ] )


def _create_update_po(
    indicator_name,
    linguas_codes,
    version,
    copyright_,
    start_year ):

    locale_directory = _get_locale_directory( indicator_name )
    pot_file = locale_directory / ( indicator_name + ".pot" )
    for lingua_code in linguas_codes:
        po_file = (
            locale_directory /
            lingua_code /
            "LC_MESSAGES" /
            ( indicator_name + ".po" ) )

        po_file_new = str( po_file ).replace( '.po', '.new.po' )

        if po_file.exists():
            subprocess.run( [
                f"msgmerge",
                f"{ po_file }",
                f"{ pot_file }",
                f"--no-location",
                f"--no-wrap",
                f"--output-file={ po_file_new }" ] )

            project_id_version = (
                f"Project-Id-Version: { indicator_name } { version }\\\\n\"" )

            subprocess.run( [
                f"sed",
                f"--in-place",
                f"s/Copyright (C).*/Copyright (C) { copyright_ }/ ; " +
                f"s/Project-Id-Version.*/{ project_id_version }/",
                f"{ po_file_new }" ] )

            command = [
                f"diff",
                f"{ po_file }",
                f"{ po_file_new }" ]

            result = (
                subprocess.run( command, capture_output = True, text = True ) )

            if result.stdout:
                subprocess.run( [
                    f"rm",
                    f"{ po_file }" ] )

                subprocess.run( [
                    f"mv",
                    f"{ po_file_new }",
                    f"{ po_file }" ] )

            else:
                subprocess.run( [
                    f"rm",
                    f"{ po_file_new }" ] )

        else:
            # http://www.gnu.org/software/gettext/manual/gettext.html#Creating
            po_file.parents[ 0 ].mkdir( parents = True, exist_ok = True )

            subprocess.run( [
                f"msginit",
                f"--input={ pot_file }",
                f"--output-file={ po_file }",
                f"--locale={ lingua_code }",
                f"--no-wrap",
                f"--no-translator" ] )

            print(
                f"Line 1: replace\n" +
                f"\t# Portable Object Template for { indicator_name }.\n" +
                f"with\n" +
                f"\t# <name of the language in English for " +
                f"{ lingua_code }> translation for { indicator_name }.\n\n" +

                f"Line 4: replace\n" +
                f"\t# Automatically generated, { _get_current_year() }.\n" +
                f"with\n" +
                f"\t# <author name> <<author email>>, " +
                f"{ start_year }-{ _get_current_year() }.\n\n" +

                f"Line 12: replace\n" +
                f"\t\"Last-Translator: Automatically generated\\n\"\n" +
                f"with\n" +
                f"\t\"Last-Translator: <author name> <<author email>>\\n\"" +
                f"\n\n" +

                f"Line 13: replace\n" +
                f"\t\"Language-Team: none\\n\"\n" +
                f"with\n" +
                f"\t\"Language-Team: <name of the language in English for " +
                f"{ lingua_code }>\\n\"" +
                f"\n\n" )


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
    print( "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" )#TODO Remove
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
        copyright_,
        start_year_indicatorbase )

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
        copyright_,
        start_year )


def build_locale_for_release(
    directory_release,
    indicator_name ):
    '''
    Concatenate indicatorbase .pot to indicator_name .pot.
    Concatenate indicatorbase .po to indicator_name .po for each locale.
    Create the .mo for each .po.
    '''

    directory_indicator_locale = (
        Path( '.' ) / directory_release / indicator_name / "src" / indicator_name / "locale" )

    directory_indicator_base_locale = (
        Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "locale" )

    # Append translations from indicatorbase POT to indicator POT.
    subprocess.call(
        "msgcat --use-first " +
        str( directory_indicator_locale / ( indicator_name + ".pot" ) ) +
        " " +
        str( directory_indicator_base_locale / "indicatorbase.pot" ) +
        " --output-file=" +
        str( directory_indicator_locale / ( indicator_name + ".pot" ) ),
        shell = True )

    # Append translations from indicatorbase PO to indicator PO for all locales.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        language_code = po.parent.parts[ -2 ]
        subprocess.call(
            "msgcat --use-first " +
            str( po ) +
            " " +
            str( directory_indicator_base_locale / language_code / "LC_MESSAGES" / "indicatorbase.po" ) +
            " --output-file=" + str( po ),
            shell = True )

    # Create .mo files.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        subprocess.call(
            "msgfmt " + str( po ) +
            " --output-file=" + str( po.parent / ( str( po.stem ) + ".mo" ) ),
            shell = True )


def get_names_and_comments_from_mo_files(
    indicator_name,
    directory_indicator_locale,
    name,
    comments ):
    '''
    Retrieve the translated name/comments for each locale.
    '''

    names_from_mo_files = { }
    comments_from_mo_files = { }
    for mo in list( Path( directory_indicator_locale ).rglob( "*.mo" ) ):
        locale = mo.parent.parent.stem

        # https://stackoverflow.com/q/54638570/2156453
        # https://stackoverflow.com/q/53316631/2156453
        # https://www.reddit.com/r/learnpython/comments/jkun99/how_do_i_load_a_specific_mo_file_by_giving_its
        translation = (
            gettext.translation(
                indicator_name,
                localedir = directory_indicator_locale,
                languages = [ locale ] ) )

        translated_string = translation.gettext( name )
        print( f"xxxxx  { name }" )
        print( f"xxxxx  { translated_string }" )

        if translated_string != name:
            names_from_mo_files[ locale ] = translated_string

#        translated_string = translation.gettext( comments ) #TODO Original
#TODO I want to figure out why the translation for the comment is not being found
# because of the \m in the comment.
# Translated comments for all other indicators ARE being found...just not script runner.
# I removed the \n from the comment and did a build wheel and the \n still appeared
# so now check if the POT and PO are regenerated.
        translated_string = translation.gettext( comments.replace( '\n', 'XXX' ) )
        print( f"xxxxx  { comments }" )
        print( f"xxxxx  { translated_string }" )
        import sys
        sys.exit()

        if translated_string != comments:
            comments_from_mo_files[ locale ] = translated_string

    return names_from_mo_files, comments_from_mo_files
