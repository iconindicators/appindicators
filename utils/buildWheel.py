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


# Build a Python Wheel package for one or more indicators.


#TODO Check that this script builds a complete wheel...what is missing?
#
# Ensure that Indicator Lunar has planets.bsp and stars.dat
# in a directory under the src/indicatorlunar/data or similar.


#TODO Consider renaming files (modules), classes, functions, variables, ..., according to Python standards. 


import argparse
import os
import re
import shutil
import subprocess
import sys

from pathlib import Path

sys.path.append( "indicator-base/src" )
from indicatorbase import indicatorbase


def _intialiseVirtualEnvironment( directoryRelease ):
    directoryVirtualEnvironment = Path( directoryRelease + os.sep + ".venv" )
    if directoryVirtualEnvironment.is_dir():
        print( "Using the virtual environment located at:", directoryVirtualEnvironment )

#TODO Despite seeing
#   Using the virtual environment located at: release/.venv
# the next line is
#   * Creating venv isolated environment...
# Does that mean the venv is still being created?

    else:
        command = \
            "python3 -m venv " + str( directoryVirtualEnvironment ) + " && " + \
            ". ./" + str( directoryVirtualEnvironment ) + "/bin/activate && " + \
            "python3 -m pip install --upgrade build"

        subprocess.call( command, shell = True )

    return directoryVirtualEnvironment


def _getMetadataFromPyprojectToml( indicatorDirectory ):
    patternAuthors = re.compile( "authors = .*" )
    patternDescription = re.compile( "description = .*" )
    patternHomepage = re.compile( "homepage = .*" )
    patternName = re.compile( "name = .*" )
    patternVersion = re.compile( "version = .*" )
    patternEndBracket = re.compile( ']' )

    # Would like to use 'tomlib' but it is only in 3.11 which is unavailable for Ubuntu 20.04.
    processingAuthors = False
    metadata = { }
    for line in open( indicatorDirectory + os.sep + "pyproject.toml" ).readlines():
        if processingAuthors:
            metadata[ "authors" ] += line.rstrip()
            if patternEndBracket.search( line ):
                processingAuthors = False

        matches = patternAuthors.match( line )
        if matches:
            authors = matches.group().split( "authors" )[ 1 ]
            metadata[ "authors" ] = authors[ authors.index( '=' ) + 1 : ].replace( '[', '' ).rstrip()
            if patternEndBracket.search( line ) is None:
                processingAuthors = True

        matches = patternDescription.match( line )
        if matches:
            metadata[ "description" ] = matches.group().split( " = " )[ 1 ][ 1 : -1 ]

        matches = patternHomepage.match( line )
        if matches:
            metadata[ "homepage" ] = matches.group().split( " = " )[ 1 ][ 1 : -1 ]

        matches = patternName.match( line )
        if matches:
            metadata[ "name" ] = matches.group().split( " = " )[ 1 ][ 1 : -1 ]

        matches = patternVersion.match( line )
        if matches:
            metadata[ "version" ] = matches.group().split( " = " )[ 1 ][ 1 : -1 ]

    # Post process authors.
    metadata[ "authors" ] = metadata[ "authors" ].replace( '[', '' ).replace( ']', '' )
    metadata[ "authors" ] = re.split( '[\{\}]', metadata[ "authors" ] )
    tmp = [ ]
    for nameEmail in metadata[ "authors" ]:
        if "name" in nameEmail or "email" in nameEmail:
            tmp.append( nameEmail )

    metadata[ "authors" ] = tmp

    return metadata


def _ensureVersionInChangelogMarkdownMatchesPyprojectToml( changelogMarkdown, versionPyprojectToml ):
    with open( changelogMarkdown, 'r' ) as f:
        contents = f.read().split( "## v" )
        for release in contents[ 1 : ]: # Skip the title line.
            leftParenthesis = release.find( '(' )
            versionChangelogMarkdown = release[ : leftParenthesis - 1 ]
            break

    return versionPyprojectToml == versionChangelogMarkdown


def _removeOldReleasesForIndicator( directoryWheel, indicatorName ):
    for item in Path( directoryWheel ).glob( "*" ):
        if indicatorName in item.name or indicatorName.replace( '-', '_' ) in item.name:
            if item.is_dir():
                shutil.rmtree( str( item ) )

            else:
                os.remove( str( item ) )


def _copyIndicatorDirectoryAndFiles( directoryWheel, indicatorName ):
    directoryIndicator = str( directoryWheel ) + os.sep + indicatorName
    shutil.copytree( indicatorName, directoryIndicator )

#TODO Need to, for now, remove directories/files that should not have been copied across.
    shutil.rmtree( directoryIndicator + os.sep + "icons" )
    shutil.rmtree( directoryIndicator + os.sep + "packaging" )
    shutil.rmtree( directoryIndicator + os.sep + "po" )
    os.remove( directoryIndicator + os.sep + "build-debian" )
    os.remove( directoryIndicator + os.sep + indicatorName + ".py.desktop" )
    if Path( directoryIndicator + os.sep + "src" + os.sep + indicatorName + ".py" ).exists():
        os.remove( directoryIndicator + os.sep + "src" + os.sep + indicatorName + ".py" )

    shutil.copy( "LICENSE.txt", directoryIndicator )
    shutil.copy( "README.md", directoryIndicator )

    shutil.copy(
        "indicator-base/src/indicatorbase/indicatorbase.py",
        directoryIndicator + os.sep + "src" + os.sep + indicatorName.replace( '-', '' ) )


def _processLocale( directoryWheel, indicatorName ):
    directoryIndicator = str( directoryWheel ) + os.sep + indicatorName

    directoryIndicatorLocale = \
        directoryIndicator + os.sep + "src" + os.sep + indicatorName.replace( '-', '' ) + os.sep + "locale"

    directoryIndicatorBaseLocale = \
        "indicator-base" + os.sep + "src" + os.sep + "indicatorbase" + os.sep + "locale"

    # Append translations from indicator-base to POT.
    command = \
        "msgcat --use-first " + \
        directoryIndicatorLocale + os.sep + indicatorName + ".pot " + \
        directoryIndicatorBaseLocale + os.sep + "indicatorbase.pot " + \
        "--output-file=" + directoryIndicatorLocale + os.sep + indicatorName + ".pot"

    subprocess.call( command, shell = True )

    # Append translations from indicatorbase to PO files.
    for po in list( Path( directoryIndicatorLocale ).rglob( "*.po" ) ):
        languageCode = po.parent.parts[ -2 ]

        command = \
            "msgcat --use-first " + \
            str( po ) + " " + \
            directoryIndicatorBaseLocale + os.sep + languageCode + os.sep + "LC_MESSAGES" + os.sep + "indicatorbase.po " + \
            "--output-file=" + str( po )

        subprocess.call( command, shell = True )

    # Create .mo files.
    for po in list( Path( directoryIndicatorLocale ).rglob( "*.po" ) ):
        command = \
            "msgfmt " + str( po ) + \
            " --output-file=" + str( po.parent ) + os.sep + str( po.stem ) + ".mo"

        subprocess.call( command, shell = True )


def _getColoursInHicolorIcon( hicolorIcon ):
    coloursInHicolorIcon = [ ]
    with open( hicolorIcon, 'r' ) as f:
        svgText = f.read()
        for m in re.finditer( r"fill:#", svgText ):
            colour = svgText[ m.start() + 6 : m.start() + 6 + 6 ]
            if colour not in coloursInHicolorIcon:
                coloursInHicolorIcon.append( colour )

    return coloursInHicolorIcon


def _processIcons( directoryWheel, indicatorName ):
    directoryIndicator = str( directoryWheel ) + os.sep + indicatorName

    directoryIndicatorIcons = \
        directoryIndicator + os.sep + "src" + os.sep + indicatorName.replace( '-', '' ) + os.sep + "icons"

    directoryIndicatorIconsHicolor = directoryIndicatorIcons + os.sep + "hicolor"

    for hicolorIcon in list( Path( directoryIndicatorIconsHicolor ).rglob( "*.svg" ) ):
        coloursInHicolorIcon = _getColoursInHicolorIcon( hicolorIcon )
        for themeName in indicatorbase.IndicatorBase.ICON_THEMES:
            directoryIndicatorIconsThemeName = Path( directoryIndicatorIcons + os.sep + themeName )
            if not directoryIndicatorIconsThemeName.exists(): # Must check as Will have been created if there is more than one icon.
                directoryIndicatorIconsThemeName.mkdir( parents = True )

            shutil.copy( hicolorIcon, directoryIndicatorIconsThemeName )

            for colour in coloursInHicolorIcon:
                icon = Path( str( directoryIndicatorIconsThemeName ) + os.sep + hicolorIcon.name )
                with open( icon, 'r' ) as f:
                    fileData = f.read()

                with open( icon, 'w' ) as f:
                    f.write( 
                        fileData.replace(
                            '#' + colour + ';',
                            '#' + indicatorbase.IndicatorBase.ICON_THEMES[ themeName ] + ';' ) )


def _buildWheelForIndicator( directoryVenv, directoryWheel, indicatorName ):
    _removeOldReleasesForIndicator( directoryWheel, indicatorName )
    _copyIndicatorDirectoryAndFiles( directoryWheel, indicatorName )
    _processLocale( directoryWheel, indicatorName )
    _processIcons( directoryWheel, indicatorName )

    command = \
        ". ./" + str( directoryVenv ) + "/bin/activate && " + \
        "cd " + indicatorName + " && " + \
        "python3 -m build --outdir " + "../" + str( directoryWheel ) + \
        " && deactivate" #TODO Check to see this works...but the process will die...so maybe keep the terminal open to see?
                        # https://stackoverflow.com/a/72320297/2156453

#TODO Seems to be an egg left over
    # indicator-test-1.0.6/src/indicator_test.egg-info/
# Maybe there is a build option to not build an egg.
# Is the egg actually required?


    subprocess.call( command, shell = True )

    shutil.rmtree( str( directoryWheel ) + os.sep + indicatorName )


def _buildWheelForIndicators( directoryRelease, indicatorNames ):
    directoryVenv = _intialiseVirtualEnvironment( directoryRelease )

    directoryWheel = Path( directoryRelease + os.sep + "wheel" )
    if not Path( directoryWheel ).is_dir():
        directoryWheel.mkdir( parents = True )

    for indicatorName in indicatorNames:
        pyprojectTomlMetadata = _getMetadataFromPyprojectToml( indicatorName )
        changelogMarkdown = indicatorName + os.sep + "CHANGELOG.md"
        if _ensureVersionInChangelogMarkdownMatchesPyprojectToml( changelogMarkdown, pyprojectTomlMetadata[ "version" ] ):
            _buildWheelForIndicator( directoryVenv, directoryWheel, indicatorName )

        else:
            print( f"Failure for { indicatorName }: The (most recent) version in CHANGELOG.md does not match that in pyproject.toml" )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Create a Python wheel for one or more indicators." )

    parser.add_argument(
        "directoryRelease",
        help = "The output directory for the Python wheel. " +
               "If the directory specified is 'release', " +
               "the Python wheel will be created in 'release/wheel'. " )

    parser.add_argument(
        "indicators",
        nargs = '+',
        help = "The list of indicators (such as indicator-fortune indicator-lunar) to build." )

    if Path( "utils/buildWheelLite.py" ).exists():
        args = parser.parse_args()
        _buildWheelForIndicators( args.directoryRelease, args.indicators )

    else:
        print( "The script must be run from the top level directory (one above utils)." )
        print( "For example:" )
        print( "\tpython3 utils/buildWheelLite.py release indicator-fortune" )