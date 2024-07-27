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
cd indicatorfortune/src/indicatorfortune

xgettext --files-from=locale/POTFILES.in --copyright-holder="Bernard Giannetti" --package-name="indicatorfortune" --package-version="1.0.44" --msgid-bugs-address="<thebernmeister@hotmail.com>" --no-location --output=locale/POTFILES.pot && \
sed -i  's/SOME DESCRIPTIVE TITLE/Portable Object Template for indicatorfortune/' locale/POTFILES.pot && \
sed -i 's/YEAR Bernard Giannetti/2014-2024 Bernard Giannetti/' locale/POTFILES.pot && \
sed -i 's/CHARSET/UTF-8/' locale/POTFILES.pot 
'''

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
# import datetime
# import re
# import sys

import os
from pathlib import Path

import subprocess


# sys.path.append( "indicatorbase/src" )
# try:
#     from indicatorbase import indicatorbase
#
# except ModuleNotFoundError:
#     pass # Occurs as the script is run from the incorrect directory and will be caught in main.


'''
cd indicatorfortune/src/indicatorfortune

xgettext --files-from=locale/POTFILES.in --copyright-holder="Bernard Giannetti" --package-name="indicatorfortune" --package-version="1.0.44" --msgid-bugs-address="<thebernmeister@hotmail.com>" --no-location --output=locale/POTFILES.pot && \
sed -i  's/SOME DESCRIPTIVE TITLE/Portable Object Template for indicatorfortune/' locale/POTFILES.pot && \
sed -i 's/YEAR Bernard Giannetti/2014-2024 Bernard Giannetti/' locale/POTFILES.pot && \
sed -i 's/CHARSET/UTF-8/' locale/POTFILES.pot 
'''

#TODO Above in sed, try  --in-plance instead of -i 


def _create_pot( indicator_name ):
    base_directory = Path.cwd() / indicator_name / "src" / indicator_name
    os.chdir( base_directory )

    copyright_holder = "Bernard Giannetti" #TODO
    package_version = "1.0.44" #TODO
    msgid_bugs_address = "thebernmeister@hotmail.com" #TODO
    start_year = "2014" #TODO
    end_year = "2024" #TODO

    command = \
        f"xgettext " + \
        f"--files-from=locale/POTFILES.in " + \
        f"--copyright-holder=\"{ copyright_holder }\" " + \
        f"--package-name=\"{ indicator_name }\" " + \
        f"--package-version=\"{ package_version }\" " + \
        f"--msgid-bugs-address=\"<{ msgid_bugs_address }>\" " + \
        f"--no-location " + \
        f"--output=locale/{ indicator_name }.new.pot && " + \
        f"sed --in-place 's/SOME DESCRIPTIVE TITLE/Portable Object Template for { indicator_name }/' locale/{ indicator_name }.new.pot && " + \
        f"sed --in-place 's/YEAR { copyright_holder }/{ start_year }-{ end_year } { copyright_holder }/' locale/{ indicator_name }.new.pot && " + \
        f"sed --in-place 's/CHARSET/UTF-8/' locale/{ indicator_name }.new.pot && " + \
        f"sed --in-place=.bak '/POT-Creation-Date/d' locale/{ indicator_name }.new.pot && " + \
        f"sed --in-place=.bak '/POT-Creation-Date/d' locale/{ indicator_name }.pot && " + \
        f"diff locale/{ indicator_name }.pot locale/{ indicator_name }.new.pot"

#    subprocess.call( command, shell = True )
    diff = subprocess.getoutput( command )
    if diff:
        command = \
            f""

    else:
        command = \
            f""

    subprocess.run( command )



def _get_potfiles_dot_in_and_linguas( indicator_name ):
    potfiles_dot_in = Path.cwd() / indicator_name / "src" / indicator_name / "locale/POTFILES.in"
    linguas = Path.cwd() / indicator_name / "src" / indicator_name / "locale/LINGUAS"
    return potfiles_dot_in, linguas


def _precheck( indicator_name ):
    potfiles_dot_in, linguas = _get_potfiles_dot_in_and_linguas( indicator_name )

    message = ""

    if not potfiles_dot_in.exists():
        message += f"ERROR: Cannot find { potfiles_dot_in }\n" 

    if not linguas.exists():
        message += f"ERROR: Cannot find { linguas }\n" 

#TODO Check LINGUAS is not empty.

#TODO Maybe check that there are no other directories under locale NOT in LINGUAS (this is a warning).
# This would be a missing language not present in LINGUAS. 

    return message


def _initialise_parser():
    parser = \
        argparse.ArgumentParser(
            description = "Create README.md for an indicator." ) #TODO Fix

    parser.add_argument(
        "indicator_name",
        help = "The name of the indicator." )

    return parser


if __name__ == "__main__":
    parser = _initialise_parser()
    script_path_and_name = "tools/build_locale.py"
    if Path( script_path_and_name ).exists():
        args = parser.parse_args()
        message = _precheck( args.indicator_name )
        if message:
            print( message )

        else:
            _create_pot( args.indicator_name )

    else:
        print(
            f"The script must be run from the top level directory (one above utils).\n"
            f"For example:\n"
            f"\tpython3 { script_path_and_name } release indicatorfortune" )
