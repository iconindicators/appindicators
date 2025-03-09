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

#TODO Search all .py for subprocess.run (after above is done)
# and replace all [] with a string and must use shell = True


#TODO Go through all .po and update the first line similarly to
#   # Russian translation for indicatorlunar.
#
# In fact, rename all to .orig or similar
# and generate new .po files to see how they should look.


import datetime
import filecmp
import gettext
import os
import re
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

    # Create a POT based on current source:
    #   http://www.gnu.org/software/gettext/manual/gettext.html
    subprocess.run(
        f"xgettext " +
        f"-f { locale_directory / 'POTFILES.in' } " +
        f"-D { str( Path( indicator_name ) / 'src' / indicator_name ) } " +
        f"--copyright-holder='{ authors_emails[ 0 ][ 0 ] }' " +
        f"--package-name={ indicator_name } " +
        f"--package-version={ version } " +
        f"--msgid-bugs-address='<{ authors_emails[ 0 ][ 1 ] }>' " +
        f"--no-location --no-wrap -o { pot_file_new }",
        shell = True )

    with open( pot_file_new, 'r', encoding = "utf-8" ) as r:
        new = (
            r.read().
            replace(
                "SOME DESCRIPTIVE TITLE",
                f"Portable Object Template for { indicator_name }" ).
            replace( f"YEAR { authors_emails[ 0 ][ 0 ] }", copyright_ ).
            replace( "CHARSET", "UTF-8" ) )

        with open( pot_file_new, 'w', encoding = "utf-8" ) as w:
            w.write( new )

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
    copyright_,
    start_year ):

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
                f"--no-location --no-wrap -o { po_file_new }",
                shell = True )

            project_id_version = (
                f"Project-Id-Version: { indicator_name } { version }\\\\n\"" )

            with open( po_file_new, 'r', encoding = "utf-8" ) as r:
                new = r.read()
                new = re.sub( "Copyright \(C\).*", f"Copyright (C) { copyright_ }", new )
                new = re.sub( "Project-Id-Version.*", f"{ project_id_version }", new )

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
                f"--no-wrap --no-translator",
                shell = True )

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

    import sys
    sys.exit() #TODO Remove


#TODO Check
#TODO Can --output-file be changed to -o ?
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
    subprocess.run(
        "msgcat --use-first " +
        f"{ str( directory_indicator_locale / ( indicator_name + '.pot' ) ) } " +
        f"{ str( directory_indicator_base_locale / 'indicatorbase.pot' ) } " +
        " --output-file=" +
        f"{ str( directory_indicator_locale / ( indicator_name + '.pot' ) ) }",
        shell = True )

    # Append translations from indicatorbase PO to indicator PO for all locales.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        language_code = po.parent.parts[ -2 ]
        subprocess.run(
            f"msgcat --use-first { str( po ) } " +
            f"{ str( directory_indicator_base_locale / language_code / 'LC_MESSAGES' / 'indicatorbase.po' ) }" +
            f" --output-file= + { str( po ) } ",  #TODO What is the extra + for?
            shell = True )

    # Create .mo files.
    for po in list( Path( directory_indicator_locale ).rglob( "*.po" ) ):
        subprocess.run(
            f"msgfmt { str( po ) } " +
            f" --output-file= { str( po.parent / ( str( po.stem ) + '.mo' ) ) }",
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
#
#TODO Maybe put in a check for \n and burp to the user?  
# Do it here or above when the pot/po is generated? 
        translated_string = translation.gettext( comments.replace( '\n', 'XXX' ) )
        print( f"xxxxx  { comments }" )
        print( f"xxxxx  { translated_string }" )
        import sys
        sys.exit()

        if translated_string != comments:
            comments_from_mo_files[ locale ] = translated_string

    return names_from_mo_files, comments_from_mo_files
