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


# Create/update the .pot and .po files for an indicator.
#TODO Update comment


import datetime
import gettext
import subprocess
import sys

from pathlib import Path

# import utils

sys.path.append( "indicatorbase/src/indicatorbase" )
import indicatorbase


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
    return _get_locale_directory( indicator_name ) / "LINGUAS"


def _get_potfiles_dot_in( indicator_name ):
    return _get_locale_directory( indicator_name ) / "POTFILES.in"


def _get_current_year():
    return datetime.datetime.now( datetime.timezone.utc ).strftime( '%Y' )


# def _get_copyright( indicator_name, authors_emails ):
#     start_year = \
#         indicatorbase.IndicatorBase.get_year_in_changelog_markdown(
#             Path( indicator_name ) / "src" / indicator_name / "CHANGELOG.md" )
#
# #TODO Should this include all authors in a line?
# # I've done this somewhere else...
#     # authors_and_emails = indicatorbase.IndicatorBase.get_authors_emails( project_metadata )
#     # authors = [ author_and_email[ 0 ] for author_and_email in authors_and_emails ]
#     # authors = ', '.join( authors )
#     return f"{ start_year }-{ _get_current_year() } { authors_emails[ 0 ] }"


#TODO Needs access to pyproject.toml
# def _get_author_email( project_metadata ):
#     return indicatorbase.IndicatorBase.get_authors_emails( project_metadata )[ 0 ]


def _create_update_pot( indicator_name, locale_directory, authors_emails, version, copyright_ ):
    pot_file = f"{ locale_directory / indicator_name }.pot"

    if Path( pot_file ).exists():
        new_pot_file = f"{ locale_directory / indicator_name }.new.pot"

    else:
        new_pot_file = pot_file

    potfiles_in = locale_directory / "POTFILES.in"
    input_files_search_directory = Path( '.' ) / indicator_name / "src" / indicator_name

    # Use xgettext to create a new POT file and sed to insert some other text.
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


def _create_update_po( indicator_name, linguas_codes, version, copyright_ ):
    message = ""
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
            command = [
                f"msginit",
                f"--input={ pot_file }",
                f"--output-file={ po_file }",
                f"--locale={ lingua_code }",
                f"--no-wrap",
                f"--no-translator" ]

            subprocess.run( command )

            message += f"INFO: Created { po_file } for lingua code '{ lingua_code }'. "
            message += f"Update lines 1, 4, 12, and 13.\n"

    return message


#TODO Remove hpoefully
# def _precheckORIG( indicator_name ):
#     message = ""
#
#     potfiles_dot_in = _get_potfiles_dot_in( indicator_name )
#     if not potfiles_dot_in.exists():
#         message += f"ERROR: Cannot find { potfiles_dot_in }\n" 
#
#     linguas = _get_linguas( indicator_name )
#     if not linguas.exists():
#         message += f"ERROR: Cannot find { linguas }\n" 
#
#     if indicator_name == "indicatorbase":
#         project_metadata = None
#
#     else:
#         project_metadata, error_message = \
#             indicatorbase.IndicatorBase.get_project_metadata(
#                 indicator_name,
#                 from_script = True )
#
#         if error_message:
#             message += f"ERROR: { error_message }\n" 
#
#     return project_metadata, message


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


# if __name__ == "__main__":
#     if utils.is_correct_directory( "./tools/build_locale.py", "release indicatorfortune" ):
#         args = \
#             utils.initialiase_parser_and_get_arguments(
#                 "Create/update the .pot and .po(s) for an indicator.",
#                 ( "indicator_name" ),
#                 { "indicator_name" : "The name of the indicator." } )
#
#         message = _precheck( args.indicator_name )
#         if message:
#             print( message )
#
#         else:
#             message = ""
#
#             author_email = _get_author_email( project_metadata )
#
#             locale_directory = Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "locale"
#             version = "1.0.1"
#             copyright_ = f"2017-{ _get_current_year() } { author_email[ 0 ] }" # First year for translations of indicatorbase.
#             _create_update_pot( "indicatorbase", locale_directory, author_email, version, copyright_ )
#             message += \
#                 _create_update_po( "indicatorbase", _get_linguas_codes( "indicatorbase" ), version, copyright_ )
#
#             locale_directory = Path( '.' ) / args.indicator_name / "src" / args.indicator_name / "locale"
#             version = project_metadata[ 'Version' ]
#             copyright_ = _get_copyright( args.indicator_name, project_metadata )
#             _create_update_pot( args.indicator_name, locale_directory, author_email, version, copyright_ )
#             message += \
#                 _create_update_po( args.indicator_name, _get_linguas_codes( args.indicator_name ), version, copyright_ )
#
#             if message:
#                 print( message )


#TODO This is now causing changes in ONLY the date to POT/PO for indicator fortune.
def update_locale_source( indicator_name, authors_emails, start_year, version ):
    message = _validate_locale_source( indicator_name )
    if message:
        print( message )  #TODO Really just want 'if not message' and run the build_locale...does that test work?

    else:
        message = ""

        current_year_author = f"-{ _get_current_year() } { authors_emails[ 0 ][ 0 ] }"
        copyright_ = f"2017-{ current_year_author }"  #TODO COmment that 2017 is start year for indicatorbase.

        _create_update_pot(
            "indicatorbase",
            Path( '.' ) / "indicatorbase" / "src" / "indicatorbase" / "locale",
            authors_emails,
            "1.0.1",  #TODO Need a comment for this...should this be a variable or property somewhere?  What if it needs to be updated?
            copyright_ )

        message += \
            _create_update_po(
                "indicatorbase",
                _get_linguas_codes( "indicatorbase" ),
                version,
                copyright_ )

        copyright_ = f"{ start_year }-{ current_year_author }"

        _create_update_pot(
            indicator_name,
            Path( '.' ) / indicator_name / "src" / indicator_name / "locale",
            authors_emails,
            version,
            copyright_ )

        message += \
            _create_update_po(
                indicator_name,
                _get_linguas_codes( indicator_name ),
                version,
                copyright_ )

        if message:
            print( message )


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
