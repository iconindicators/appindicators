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


#TODO
# To update each the .po file for each locale:
#   cd ~/Programming/Indicators/indicatorfortune/src/indicatorfortune/locale
#   msgmerge ru/LC_MESSAGES/indicatorfortune.po indicatorfortune.pot -o ru/LC_MESSAGES/indicatorfortune.po
#
# What about looking at the LINGUAS file;
# if there is no po file for a given language, create it.
# Or instead write a message saying there is no PO file for a given LINGUA entry?
#
#This script should be called as part of the build_wheel in the same way the build_readme.
#
# Once this script is sorted, maybe update the indicatorbase/locale/README
# to say the README is a historical document.


import argparse
import datetime

from pathlib import Path

import subprocess
import sys


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
        indicatorbase.IndicatorBase.get_year_in_changelog_markdown(
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
    for lingua_code in linguas_codes:
        po_file = _get_locale_directory( indicator_name ) / lingua_code / "LC_MESSAGES" / ( indicator_name + ".po" )
        if po_file.exists():
            print( "found " + str( po_file ) )
# msgmerge
#     ru/LC_MESSAGES/indicatorfortune.po
#     indicatorfortune.pot
#     -o ru/LC_MESSAGES/indicatorfortune.po
            pot_file = _get_locale_directory( indicator_name ) / ( indicator_name + ".pot" )
            command = [
                f"msgmerge",
                f"{ po_file }",
                f"{ pot_file }",
                f"--no-location",
                f"--output-file={ po_file }.new.po" ]

            print( command )
            subprocess.run( command )


#TODO Because field values come across from the original PO file to the merged version,
# ensure particular fields have current values.
#   # Copyright (C) 2013-2024 Bernard Giannetti    <---- End year
#   # Oleg Moiseichuk <berroll@mail.ru>, 2015-2024.   <--- End year....maybe not.
#   "Project-Id-Version: indicatorfortune 1.0.41\n"   <---- version


#TODO The
#   "PO-Revision-Date: 2024-07-09 16:04+0300\n"
# will have to change if and only if the merged version is taken over the original...right?


            command = [
                f"diff",
                f"{ po_file }",
                f"{ po_file }.new.po" ]
    
            result = subprocess.run( command, capture_output = True, text = True )
            print( result.stdout )

#TODO Do we first or last or at all update...
#
#    # Copyright (C) 2013-2024 Bernard Giannetti          <---- check/refresh the end date?
#    "Project-Id-Version: indicatorfortune 1.0.44\n"     <------ update version number?
#     "POT-Creation-Date: 2024-07-27 13:15+1000\n"       <---- update date?
#     "PO-Revision-Date: 2024-07-27 13:15+1000\n"       <---- update date?  Maybe ONLY if other changes happen...?


#TODO After all pot/po files are updated,
# maybe look for
#  #~
# and remove.


        else:
            pot_file = _get_locale_directory( indicator_name ) / ( indicator_name + ".pot" )
            command = [
                f"msginit",
                f"--input={ pot_file }",
                f"--output-file={ po_file }.NEW.po",
                f"--locale={ lingua_code }",
                f"--no-translator" ]

            subprocess.run( command )

#TODO Maybe make this message more explicit about what to change...see the README.
            message = f"INFO:\n"
            message += f"\tCreated { po_file } for lingua code '{ lingua_code }'.\n"
            message += f"\tUpdate lines 1, 4, 12, and 13.\n"
            print( message )

# msginit
#   --input=indicatorfortune/src/indicatorfortune/locale/indicatorfortune.pot 
#   --output-file=indicatorfortune/src/indicatorfortune/locale/ru/LC_MESSAGES/indicatorfortune.po
#   --locale=ru 
#   --no-translator


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
