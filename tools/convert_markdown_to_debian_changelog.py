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


# Read in a CHANGELOG.md convert back out to a Debian format changelog.


# Online markdown viewers/editors:
#   https://stackedit.io/app
#   https://markdownlivepreview.com/


import argparsei
import textwrap

from datetime import datetime


_distributionsAndEndOfLifeDates = {
    "lucid"   : "2013-05-09",
    "precise" : "2017-04-28",
    "trusty"  : "2019-04-25",
    "xenial"  : "2021-04-30",
    "bionic"  : "2023-05-31",
    "focal"   : "2025-05-29",
    "jammy"   : "2027-06-01",
    "noble"   : "2029-05-31" }


def _getDistributionForDate( yyyyDASHmmDASHdd  ):
    d = None
    for distribution, endOfLifeDate in _distributionsAndEndOfLifeDates.items():
        if yyyyDASHmmDASHdd < endOfLifeDate:
            d = distribution
            break

    return d


def _wrapText( textToWrap, width, initialIndent, subsequentIndent ):
    return \
        textwrap.wrap(
            textToWrap, 
            width = width, 
            initial_indent = initialIndent, 
            subsequent_indent = subsequentIndent )


def processRelease( packageName, release, name, email ):
    plaintext = '\n\n\n'

    leftParenthesis = release.find( '(' )
    version = release[ : leftParenthesis - 1 ]
    yearMonthDay = release[ leftParenthesis + 1 : leftParenthesis + 1 + 10 ]

    distribution =_getDistributionForDate( yearMonthDay )

    plaintext += packageName + " (" + version + "-1) " + distribution + "; urgency=low\n"

    remainingLines = release.split( '\n' )[ 2 : ]
    i = 0
    while i < len( remainingLines ):
        if remainingLines[ i ].startswith( "- " ):
            wrappedText = _wrapText( remainingLines[ i ][ 2 : ], 80, "  * ", "\n    " )
            plaintext += '\n' + ''.join( wrappedText )

        elif remainingLines[ i ].startswith( "  - " ):
            wrappedText = _wrapText( remainingLines[ i ][ 4 : ], 80, "      * ", "\n        " )
            plaintext += '\n' + ''.join( wrappedText )

        elif remainingLines[ i ].startswith( "            " ):
            plaintext += '\n' + remainingLines[ i ][ 4 : ]

        elif remainingLines[ i ].startswith( "        " ):
            plaintext += '\n' + remainingLines[ i ]

        elif remainingLines[ i ].startswith( "    " ):
            wrappedText = _wrapText( remainingLines[ i ][ 4 : ], 80, "    ", "\n    " )
            plaintext += '\n' + ''.join( wrappedText )

        i += 1

    # Note the hack below using '-' to omit leading zero from day of month.
    #   https://stackoverflow.com/a/42709606/2156453
    plaintext += \
        '\n\n' + \
        " -- " + name + " <" + email + ">  " + \
        datetime.strptime( yearMonthDay, "%Y-%m-%d" ).strftime( "%a, %-d %b %Y" ) + \
        " 00:00:00 +0000"

    return plaintext


def processMarkdownChangelog( packageName, changelogMarkdown, changelogDebian, name, email ):
    plaintext = ""
    with open( changelogMarkdown, 'r' ) as f:
        contents = f.read().split( "## v" )
        for release in contents[ 1 : ]: # Skip the title line.
            if len( release ) > 0:
                plaintext += processRelease( packageName, release, name, email )

    with open( changelogDebian, 'w' ) as f:
        f.write( plaintext[ 3 : ] + '\n' )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Convert a CHANGELOG.md to Debian format." )

    parser.add_argument(
        "packageName",
        help = "The package name (for example, indicator-lunar)." )

    parser.add_argument(
        "changelogMarkdown",
        help = "The full path to the input CHANGELOG.md file to convert." )

    parser.add_argument(
        "changelogDebian",
        help = "The full path to the output Debian changelog to create." )

    parser.add_argument(
        "name",
        help = "The name to use at the end of each entry." )

    parser.add_argument(
        "email",
        help = "The email to use at the end of each entry." )

    args = parser.parse_args()
    processMarkdownChangelog(
        args.packageName,
        args.changelogMarkdown,
        args.changelogDebian,
        args.name,
        args.email )
