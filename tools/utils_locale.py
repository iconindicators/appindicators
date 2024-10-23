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


# Create/update the .pot/.po files for an indicator's source.
# Build the .pot/.po files for an indicator's wheel release.


import datetime
import gettext
import subprocess

from pathlib import Path


def _get_linguas_codes( indicator_name ):
    lingua_codes = [ ]
    with open( _get_linguas( indicator_name ), 'r' ) as f:
        for line in f:
            if not line.startswith( '#' ):
                lingua_codes = line.split()

    return lingua_codes


def _get_locale_directory( indicator_name ):
    return Path( '.' ) / indicator_name / "src" / indicator_name / "locale"


def _get_linguas( indicator_name ):
    # The LINGUAS file lists each supported language/locale:
    #   http://www.gnu.org/software/gettext/manual/gettext.html#po_002fLINGUAS
    return _get_locale_directory( indicator_name ) / "LINGUAS"


def _get_potfiles_dot_in( indicator_name ):
    return _get_locale_directory( indicator_name ) / "POTFILES.in"


def _get_current_year():
    return datetime.datetime.now( datetime.timezone.utc ).strftime( '%Y' )


def _create_update_pot(
        indicator_name,
        locale_directory,
        authors_emails,
        version,
        copyright_ ):

    pot_file = f"{ locale_directory / indicator_name }.pot"

    if Path( pot_file ).exists():
        new_pot_file = f"{ locale_directory / indicator_name }.new.pot"

    else:
        new_pot_file = pot_file

    potfiles_in = locale_directory / "POTFILES.in"
    input_files_search_directory = Path( '.' ) / indicator_name / "src" / indicator_name

    # Use xgettext to create a new POT file and sed to insert some other text:
    #   http://www.gnu.org/software/gettext/manual/gettext.html#po_002fPOTFILES_002ein
    command = [
        f"xgettext",
        f"--files-from={ potfiles_in }",
        f"--directory={ input_files_search_directory }",
        f"--copyright-holder={ authors_emails[ 0 ][ 0 ] }",
        f"--package-name={ indicator_name }",
        f"--package-version={ version }",
        f"--msgid-bugs-address=<{ authors_emails[ 0 ][ 1 ] }>",
        f"--no-location",
        f"--no-wrap",
        f"--output={ new_pot_file }" ]

    subprocess.run( command )

    some_descriptive_title = f"Portable Object Template for { indicator_name }"

    command = [
        f"sed",
        f"--in-place",
        f"s/SOME DESCRIPTIVE TITLE/{ some_descriptive_title }/",
        f"{ new_pot_file }" ]

    subprocess.run( command )

    command = [
        f"sed",
        f"--in-place",
        f"s/YEAR { authors_emails[ 0 ][ 0 ] }/{ copyright_ }/",
        f"{ new_pot_file }" ]

    subprocess.run( command )

    command = [
        f"sed",
        f"--in-place",
        f"s/CHARSET/UTF-8/",
        f"{ new_pot_file }" ]

    subprocess.run( command )

    # Create the POT if none exists; otherwise, compare the new POT with the original POT...
    if new_pot_file.endswith( ".new.pot" ):
        command = [
            f"sed",
            f"--in-place=.bak",
            f"/POT-Creation-Date/d",
            f"{ pot_file }" ]

        subprocess.run( command )

        command = [
            f"sed",
            f"--in-place=.bak",
            f"/POT-Creation-Date/d",
            f"{ new_pot_file }" ]

        subprocess.run( command )

        command = [
            f"diff",
            f"{ pot_file }",
            f"{ new_pot_file }" ]

        result = subprocess.run( command, capture_output = True, text = True )
        if result.stdout:
            command = [
                f"rm",
                f"{ pot_file }",
                f"{ pot_file }.bak",
                f"{ new_pot_file }" ]

            subprocess.run( command )

            command = [
                f"mv",
                f"{ new_pot_file }.bak",
                f"{ pot_file }" ]

            subprocess.run( command )

        else:
            command = [
                f"rm",
                f"{ pot_file }",
                f"{ new_pot_file }",
                f"{ new_pot_file }.bak" ]

            subprocess.run( command )

            command = [
                f"mv",
                f"{ pot_file }.bak",
                f"{ pot_file }" ]

            subprocess.run( command )


def _create_update_po(
        indicator_name,
        linguas_codes,
        version,
        copyright_,
        start_year ):

    pot_file = _get_locale_directory( indicator_name ) / ( indicator_name + ".pot" )
    for lingua_code in linguas_codes:
        po_file = (
            _get_locale_directory( indicator_name ) / 
            lingua_code / 
            "LC_MESSAGES" / 
            ( indicator_name + ".po" ) )

        if po_file.exists():
            command = [
                f"msgmerge",
                f"{ po_file }",
                f"{ pot_file }",
                f"--no-location",
                f"--no-wrap",
                f"--output-file={ po_file }.new.po" ]

            subprocess.run( command )

            command = [
                f"sed",
                f"--in-place",
                f"/^# Copyright (C)/s/.*/# Copyright (C) { copyright_ }/",
                f"{ po_file }.new.po" ]

            subprocess.run( command )

            # Ensure the Project-Id-Version is latest.
            project_id_version = f"\"Project-Id-Version: { indicator_name } { version }\\\\n\""

            command = [
                f"sed",
                f"--in-place",
                f"/Project-Id-Version/s/.*/{ project_id_version }/",
                f"{ po_file }.new.po" ]

            subprocess.run( command )

            command = [
                f"diff",
                f"{ po_file }",
                f"{ po_file }.new.po" ]

            result = subprocess.run( command, capture_output = True, text = True )
            if result.stdout:
                command = [
                    f"rm",
                    f"{ po_file }" ]

                result = subprocess.run( command )

                command = [
                    f"mv",
                    f"{ po_file }.new.po",
                    f"{ po_file }" ]

                result = subprocess.run( command )

            else:
                command = [
                    f"rm",
                    f"{ po_file }.new.po" ]

                result = subprocess.run( command )

        else:
            # http://www.gnu.org/software/gettext/manual/gettext.html#Creating
            po_file.parents[ 0 ].mkdir( parents = True )

            command = [
                f"msginit",
                f"--input={ pot_file }",
                f"--output-file={ po_file }",
                f"--locale={ lingua_code }",
                f"--no-wrap",
                f"--no-translator" ]

            subprocess.run( command )

            message = ""

            message += f"Update line 1, replacing\n"
            message += f"\t# Portable Object Template for { indicator_name }.\n"
            message += f"with\n"
            message += f"\t# <name of the language in English for { lingua_code }> translation for { indicator_name }.\n\n"

            message += f"Update line 4, replacing\n"
            message += f"\t# Automatically generated, { _get_current_year() }.\n"
            message += f"with\n"
            message += f"\t# <author name> <<author email>>, { start_year }-{ _get_current_year() }.\n\n"

            message += f"Update line 12, replacing\n"
            message += f"\t\"Last-Translator: Automatically generated\\n\"\n"
            message += f"with\n"
            message += f"\t\"Last-Translator: <author name> <<author email>>\\n\"\n\n"

            print( message )


def _validate_locale_source( indicator_name ):
    message = ""

    potfiles_dot_in = _get_potfiles_dot_in( "indicatorbase" )
    if not potfiles_dot_in.exists():
        message += f"ERROR: Cannot find { potfiles_dot_in }\n" 

    potfiles_dot_in = _get_potfiles_dot_in( indicator_name )
    if not potfiles_dot_in.exists():
        message += f"ERROR: Cannot find { potfiles_dot_in }\n" 

    linguas = _get_linguas( "indicatorbase" )
    if not linguas.exists():
        message += f"ERROR: Cannot find { linguas }\n" 

    linguas = _get_linguas( indicator_name )
    if not linguas.exists():
        message += f"ERROR: Cannot find { linguas }\n" 

    return message


def update_locale_source(
    indicator_name,
    authors_emails,
    start_year,
    version_indicator,
    version_indicatorbase):

    message = _validate_locale_source( indicator_name )
    if not message:
        message = ""

        current_year_author = f"{ _get_current_year() } { authors_emails[ 0 ][ 0 ] }"
        copyright_ = f"2017-{ current_year_author }"  # Start year for indicatorbase translations is 2017.

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
            start_year )

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

    return message


def get_names_and_comments_from_mo_files(
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


def build_locale_release( directory_release, indicator_name ):
    directory_indicator = Path( '.' ) / directory_release / indicator_name
    directory_indicator_locale = Path( '.' ) / directory_indicator / "src" / indicator_name / "locale"
    directory_indicator_base_locale = Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "locale"

    # Append translations from indicatorbase to POT.
    command = \
        "msgcat --use-first " + \
        str( directory_indicator_locale / ( indicator_name + ".pot" ) ) + " " + \
        str( directory_indicator_base_locale / "indicatorbase.pot" ) + \
        " --output-file=" + str( directory_indicator_locale / ( indicator_name + ".pot" ) )

    subprocess.call( command, shell = True )

    # Append translations from indicatorbase to PO files.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        language_code = po.parent.parts[ -2 ]

        command = \
            "msgcat --use-first " + \
            str( po ) + " " + \
            str( directory_indicator_base_locale / language_code / "LC_MESSAGES" / "indicatorbase.po" ) + \
            " --output-file=" + str( po )

        subprocess.call( command, shell = True )

    # Create .mo files.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        command = \
            "msgfmt " + str( po ) + \
            " --output-file=" + str( po.parent / ( str( po.stem ) + ".mo" ) )

        subprocess.call( command, shell = True )
