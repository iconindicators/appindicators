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


#TODO Put in a full description of usage
# and how it relates to other scripts in utils as necessary/applicable. 




#TODO 
# May need this part still...get from buildDebian.py
#
# Import secret key into gpg.  In a terminal, change to the directory containing the files
#
#	'Bernard Giannetti.asc' pubring.pkr secring.skr
#
# and run
#
#	gpg --import secring.skr
#
# Perhaps print to screen the need for gpg etc?


import argparse

from pathlib import Path


def _getReleaseCommandForIndicator( directoryDebianSourcePackages, indicatorToRelease, foundChanges, missingChanges ):
    changesFilesForIndicator = [ ] # There may be more than once source package for the indicator.
    for item in Path( directoryDebianSourcePackages ).glob( "*.changes" ):
        if indicatorToRelease in item.name:
            changesFilesForIndicator.append( item )

    if changesFilesForIndicator:
        foundChanges.append( sorted( changesFilesForIndicator )[ -1 ] ) # Take the highest version.

    else:
        missingChanges.append( indicatorToRelease )


#TODO Rename and change description, etc, etc...
# I think it safer to print the upload command and the user can copy/paste.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Print the command to upload a Debian source package for one or more indicators to LaunchPad/PPA." )

    parser.add_argument(
        "directoryDebianSourcePackages",
        help = "The directory containing the Debian source package(s)." )

    parser.add_argument(
        "indicators",
        nargs = '+',
        help = "The list of indicators (such as indicator-fortune indicator-lunar)." )

#TODO Rename according to new script name.
    if Path( "utils/releaseDebianToLaunchpad.py" ).exists():
        args = parser.parse_args()

        foundChanges = [ ]
        missingChanges = [ ]
        for indicatorToRelease in args.indicators:
            _getReleaseCommandForIndicator( args.directoryDebianSourcePackages, indicatorToRelease, foundChanges, missingChanges )

        if missingChanges:
            print( "\nNo .changes files found in\n\n\t", args.directoryDebianSourcePackages, "\nfor" )
            for missingChange in missingChanges:
                print( '\t', indicatorToRelease )

        print( '\n' * 2 )

        if foundChanges:
            print( "To upload to LaunchPad, change to the directory\n\n\t", args.directoryDebianSourcePackages, "\n\nand run\n" )
            for foundChange in foundChanges:
                print( "\tdput ppa:thebernmeister/ppa", foundChange.name ) 

    # command = "dput ppa:thebernmeister/ppa ${NAME}_${VERSION}-1_source.changes"

    else:
        print( "The script must be run from the top level directory (one above utils)." )
        print( "For example:" )
#TODO Rename according to new script name.
        print( "\tpython3 utils/releaseDebianToLaunchpad.py release/debian indicator-fortune" )
