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



#TODO Update indicatorbase/src/indicatorbase/locale/README.
# I think the wording and some commands may be out of date.


#TODO This is a new script...a copy of build_readme.py
# Idea is to update POT and PO files as part of the build_wheel.py process...
# But perhaps should be called to run over the src tree and NOT the release tree.
# What is the point of updating the POT/PO files in the release and not the original src?
#
# Can pass some things to xgettext on the command line:
#
#   cd ~/Programming/Indicators/indicatorfortune/src/indicatorfortune
#   xgettext --files-from=locale/POTFILES.in --copyright-holder="Bernard Giannetti" --package-name="indicatorfortune" --package-version="1.0.42" --msgid-bugs-address="<thebernmeister@hotmail.com>" --output=locale/POTFILES.pot && sed -i  's/SOME DESCRIPTIVE TITLE/Portable Object Template for indicatorfortune/' locale/POTFILES.pot && sed -i 's/YEAR Bernard Giannetti/2014-2024 Bernard Giannetti/' locale/indicatorfortune.pot && sed -i 's/CHARSET/UTF-8/' locale/indicatorfortune.pot
#
# which creates a new POT file and replaces text such as title, copyright year and charset.
# Need to substitute all the above into a new script.
#
# To update each the .po file for each locale:
#   cd ~/Programming/Indicators/indicatorfortune/src/indicatorfortune/locale
#   msgmerge ru/LC_MESSAGES/indicatorfortune.po indicatorfortune.pot -o ru/LC_MESSAGES/indicatorfortune.po
#
# What about looking at the LINGUAS file;
# if there is no po file for a given language, create it?
# I don't think this is feasible...
# ...there are too many pieces of text to swap out.
# Perhaps the build POT/PO script could make the new PO file and leave it at that.
# Or write a message saying there is no PO file for a given LINGUA entry?
#
# Still not sure when this script should be called...as part of the build_wheel
# in the same way the build_readme is called?
#
#
# Once this script is sorted, maybe update the indicatorbase/locale/README
# to say the README is a historical document.


#TODO One thing to consider is that each time the build occurs and so running this script
# is the pot/po files will be altered with at a minimum, new date/times.
#
# This is not enough to justify having to commit...
# ...so is there a way to deal with this?
# Can only think of when it is time to commit, having to revert each AND EVERY pot/po file...
# pain in the neck!
#
# Maybe search in the file system for pot/po files and then can do a mass revert.
# But still need a way to determine if a file differs only by date/time.
#
# Need to check/verify that doing the update of a POT or PO
# where there are no changes from the source .py file
# that the updated/generated POT/PO files are the same as the originals
# and so that won't trigger a need to do a commit.


# Create a README.md for an indicator from text common to all indicators and text
# specific to the indicator, drawn from the indicator's CHANGELOG.md and pyproject.toml.
#
#   https://github.github.com/gfm
#
# When testing/editing, to render out in HTML:
#   python3 -m pip install --upgrade readme_renderer readme_renderer[md]
#   python3 tools/build_readme.py release indicatortest
#   python3 -m readme_renderer release/README.md -o release/README.html
#
# References
#   https://pycairo.readthedocs.io
#   https://pygobject.readthedocs.io


import argparse
import datetime
# import re
import sys

# import os
from pathlib import Path

import subprocess


#TODO I think this works in both eclipse and from terminal...
# double check and if all good, fix also in build_readme.py and elsewhere.
sys.path.append( "indicatorbase/src/indicatorbase" )
try:
    # from indicatorbase import indicatorbase
    import indicatorbase

except ModuleNotFoundError as e:
    # print( "from indicatorbase import indicatorbase" )
    print( e )
    # pass # Occurs as the script is run from the incorrect directory and will be caught in main.

# try:
#     import indicatorbase
#
# except ModuleNotFoundError as e:
#     print( "import indicatorbase" )
#     print( e )
#     pass # Occurs as the script is run from the incorrect directory and will be caught in main.


def _create_update_pot( indicator_name, project_metadata ):
    author_email = indicatorbase.IndicatorBase.get_authors_emails( project_metadata )[ 0 ]

    locale_directory = Path( '.' ) / indicator_name / "src" / indicator_name / "locale"

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
        f"--copyright-holder={ author_email[ 0 ] }",
        f"--package-name={ indicator_name }",
        f"--package-version={ project_metadata[ 'Version' ] }",
        f"--msgid-bugs-address=<{ author_email[ 1 ] }>",
        f"--no-location",
        f"--output={ new_pot_file }" ]

    subprocess.run( command )

    some_descriptive_title = f"Portable Object Template for { indicator_name }"

    command = [
        f"sed",
        f"--in-place",
        f"s/SOME DESCRIPTIVE TITLE/{ some_descriptive_title }/",
        f"{ new_pot_file }" ]

    subprocess.run( command )

    start_year = \
        indicatorbase.IndicatorBase.get_first_year_or_last_year_in_changelog_markdown(
            indicator_name + '/src/' + indicator_name + '/CHANGELOG.md' )

    end_year = datetime.datetime.now( datetime.timezone.utc ).strftime( '%Y' )

    copyright_ = f"{ start_year }-{ end_year } { author_email[ 0 ] }"
    command = [
        f"sed",
        f"--in-place",
        f"s/YEAR { author_email[ 0 ] }/{ copyright_ }/",
        f"{ new_pot_file }" ]

    subprocess.run( command )

    command = [
        f"sed",
        f"--in-place",
        f"s/CHARSET/UTF-8/",
        f"{ new_pot_file }" ]

    subprocess.run( command )

    # If originally there was no POT file, a POT is created and job done.
    # Otherwise, need to compare the old POT to the new POT...
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


def _create_update_po( indicator_name ):
    linguas_codes = _get_linguas_codes( indicator_name )
    for linguas_code in linguas_codes:
        po_file = _get_locale_directory( indicator_name ) / linguas_code / "LC_MESSAGES" / ( indicator_name + ".po" )
        if ( po_file ).exists():
            print( "found " + str( po_file ) )
            pass#TODO Update po...!

        else:
            print( "missing " + str( po_file ) )
            #TODO Create the po...!

            pot_file = _get_locale_directory( indicator_name ) / ( indicator_name + ".pot" )
            command = [
                f"msginit",
                f"--input={ pot_file }",
                f"--output-file={ po_file }",
                f"--locale={ linguas_code }",
                f"--no-translator" ]

            print( command )

        pot_file = _get_locale_directory( indicator_name ) / ( indicator_name + ".pot" )
        command = [
            f"msginit",
            f"--input={ pot_file }",
            f"--output-file={ po_file }",
            f"--locale={ linguas_code }",
            f"--no-translator" ]

        print( ' '.join( command ) )
# msginit --input=indicatorfortune/src/indicatorfortune/locale/indicatorfortune.pot --output-file=indicatorfortune/src/indicatorfortune/locale/ru/LC_MESSAGES/indicatorfortune.po --locale=ru --no-translator
# msginit
#   --input=indicatorfortune/src/indicatorfortune/locale/indicatorfortune.pot 
#   --output-file=indicatorfortune/src/indicatorfortune/locale/ru/LC_MESSAGES/indicatorfortune.po
#   --locale=ru 
#   --no-translator


        # f"--files-from={ potfiles_in }",
        # f"--directory={ input_files_search_directory }",
        # f"--copyright-holder={ author_email[ 0 ] }",
        # f"--package-name={ indicator_name }",
        # f"--package-version={ project_metadata[ 'Version' ] }",
        # f"--msgid-bugs-address=<{ author_email[ 1 ] }>",
        # f"--no-location",

                

def _precheck( indicator_name ):
    message = ""

    potfiles_dot_in = _get_potfiles_dot_in( indicator_name )
    if not potfiles_dot_in.exists():
        message += f"ERROR: Cannot find { potfiles_dot_in }\n" 

    linguas = _get_linguas( indicator_name )
    if not linguas.exists():
        message += f"ERROR: Cannot find { linguas }\n" 

#TODO Check there are no directories under locale NOT in LINGUAS (this is a warning).
# This could be a missing language not present in LINGUAS.

    project_metadata, error_message = \
        indicatorbase.IndicatorBase.get_project_metadata(
            indicator_name,
            from_build_script = True )

    if error_message:
        #TODO Check this message being printed.
        message += f"ERROR:\n{ error_message }\n" 

    return project_metadata, message


def _initialise_parser():
    parser = \
        argparse.ArgumentParser(
            description = "Create README.md for an indicator." ) #TODO Fix

    parser.add_argument(
        "indicator_name",
        help = "The name of the indicator." )

    return parser


#TODO This will not work with indicatorbase as there is no wheel file.
#
# Maybe when the pot is created for a given indicator,
# do a create/update for indicatorbase?
# But indicatorbase should already exist...?
#
# Then similarly for the po files for the indicator;
# update the po files for indicatorbase.
if __name__ == "__main__":
    parser = _initialise_parser()
    script_path_and_name = "tools/build_locale.py"
    if Path( script_path_and_name ).exists():
        args = parser.parse_args()
        project_metadata, message = _precheck( args.indicator_name )
        if message:
            print( message )

        else:
            _create_update_pot( args.indicator_name, project_metadata )
            _create_update_po( args.indicator_name )

    else:
        print(
            f"The script must be run from the top level directory (one above utils).\n"
            f"For example:\n"
            f"\tpython3 { script_path_and_name } release indicatorfortune" )
