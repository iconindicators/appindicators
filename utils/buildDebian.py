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


# Build a DEBIAN source package for one or more indicators.
#
# Install the packages:
#   sudo apt install build-essential devscripts dh-make dh-python gpg lintian
#
# Import secret key into gpg.
# In a terminal, change to the directory containing the files
#   asciiArmouredSignature.asc   pubring.pkr   secring.skr
#
# and run
#   gpg --import secring.skr
#
# References:
#   http://askubuntu.com/questions/27715/create-a-deb-package-from-scripts-or-binaries
#   https://fpm.readthedocs.io/
#   http://askubuntu.com/questions/28562/how-do-i-create-a-ppa-for-a-working-program
#   http://askubuntu.com/questions/90764/how-do-i-create-a-deb-package-for-a-single-python-script
#   https://stackoverflow.com/questions/65117979/problems-using-debuild-to-upload-a-python-gtk-program-to-launchpad
#   https://askubuntu.com/questions/399552/how-to-create-a-deb-package-for-a-python3-script
#   http://blog.garethj.com/2009/06/02/building-deb-packages-for-python-applications
#   http://developer.ubuntu.com/packaging/html/debian-dir-overview.html
#   http://help.launchpad.net/Packaging/PPA/Uploading
#   http://help.ubuntu.com/community/PythonRecipes/DebianPackage
#   http://savetheions.com/2010/01/20/packaging-python-applicationsmodules-for-debian
#   http://shallowsky.com/blog/programming/packaging-launchpad-ppas.html
#   http://ubuntulinuxtipstricks.blogspot.com.au/2010/08/is-packaging-new-software-hard.html
#   http://wiki.debian.org/Python/Packaging
#   http://wiki.ubuntu.com/MOTU/School/PackagingWithoutCompiling
#   http://wiki.ubuntu.com/PackagingGuide/HandsOn
#   http://wiki.ubuntu.com/PackagingGuide/Python
#   http://www.debian.org/doc/manuals/maint-guide
#   http://www.debian.org/doc/packaging-manuals/python-policy
#   http://www.debian-administration.org/articles/336
#   http://news.softpedia.com/news/How-to-Repack-Deb-Files-on-Debian-and-Ubuntu-404930.shtml
#   http://blog.packagecloud.io/debian/debuild/packaging/2015/06/08/buildling-deb-packages-with-debuild
#   https://standards.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html
#   https://developer.gnome.org/icon-theme-spec/
#   https://askubuntu.com/questions/30145/ppa-packaging-having-versions-of-packages-for-multiple-distros
#   https://askubuntu.com/questions/144122/when-should-mo-files-be-generated


import sys
sys.path.append( "indicator-base/src" )
from indicatorbase import indicatorbase
# import indicatorbase #TODO Only for testing

from pathlib import Path

import argparse, datetime, os, re, shutil, stat, subprocess, textwrap


#TODO Look at build-debian shell script to see if something has been missed.


def _getMetadataFromPyprojectToml( indicatorDirectory ):
    patternAuthors = re.compile( "authors = .*" )
    patternDescription = re.compile( "description = .*" )
    patternHomepage = re.compile( "homepage = .*" )
    patternName = re.compile( "name = .*" )
    patternVersion = re.compile( "version = .*" )
    patternEndBracket = re.compile( ']' )

    # Would like to use 'tomlib' but it is only in 3.11 and so is unavailable for Ubuntu 20.04.
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


def _createReleaseDirectoryForIndicator( directoryReleaseDebian, indicatorName, version ):
    for item in Path( directoryReleaseDebian ).glob( "*" ):
        if indicatorName in item.name:
            if item.is_dir():
                shutil.rmtree( str( item ) )

            else:
                os.remove( str( item ) )

    directoryReleaseDebianIndicator = Path( directoryReleaseDebian + os.sep + indicatorName + '-' + version )
    directoryReleaseDebianIndicator.mkdir( parents = True )

    return str( directoryReleaseDebianIndicator )


def _chmodReadAndWriteForAll( file ):
    os.chmod(
        file, 
        stat.S_IRUSR | stat.S_IWUSR |
        stat.S_IRGRP | stat.S_IWGRP |
        stat.S_IROTH | stat.S_IWOTH )


def _ensureNoTODOsInSrc( indicatorDirectory ):
    noTODOsFound = True
    filesToCheckForTODOs = [ ]

    filesToCheckForTODOs.append(
        Path( "indicator-base" + os.sep + "src" + os.sep + "indicatorbase" + os.sep + "indicatorbase.py" ) )

    filesToCheckForTODOs += list(
        Path( indicatorDirectory + os.sep + "src" + os.sep + indicatorDirectory.replace( '-', '' ) ).glob( "*.py" ) )

    for file in filesToCheckForTODOs:
        with open( file, 'r' ) as f:
            if re.search( "TODO", f.read(), re.IGNORECASE ) is not None:
                noTODOsFound = False
                print( f.name, "contains one or more TODOs!" )

    return not noTODOsFound #TODO Remove the not!


def _createWheel( directoryIndicator, directoryRelease ):
    command = \
        "python3 " + \
        "utils/buildWheelLite.py " + \
        directoryRelease + ' ' + \
        directoryIndicator

    subprocess.call( command, shell = True )


def _copyMiscellaneous( directoryIndicator, directoryReleaseIndicator, directoryReleaseWheel ):
    shutil.copy( "LICENSE.txt", directoryReleaseIndicator )
    shutil.copy( "README.md", directoryReleaseIndicator )

    shutil.copy( 
        directoryIndicator + os.sep + "packaging" + os.sep + "linux" + os.sep + directoryIndicator + ".py.desktop",
        directoryReleaseIndicator )

    for wheel in list( Path( directoryReleaseWheel ).glob( '*' + directoryIndicator.replace( '-', '_' ) + "*.whl" ) ):
        shutil.copy( str( wheel ), directoryReleaseIndicator )
        break


def _copySource( directoryIndicator, directoryReleaseIndicator ):
    directoryReleaseIndicatorSource = Path( directoryReleaseIndicator + os.sep + "src" )
    directoryReleaseIndicatorSource.mkdir( parents = True )

    shutil.copy( 
        "indicator-base" + os.sep + "src" + os.sep + "indicatorbase" + os.sep + "indicatorbase.py",
        directoryReleaseIndicatorSource )

    directoryIndicatorSource = directoryIndicator + os.sep + "src" + os.sep + directoryIndicator.replace( '-', '' )
    for pythonSource in list( Path( directoryIndicatorSource ).glob( "*.py" ) ):
        shutil.copy( pythonSource, directoryReleaseIndicatorSource )


def _getColoursInHicolorIcon( hicolorIcon ):
    coloursInHicolorIcon = [ ]
    with open( hicolorIcon, 'r' ) as f:
        svgText = f.read()
        for m in re.finditer( r"fill:#", svgText ):
            colour = svgText[ m.start() + 6 : m.start() + 6 + 6 ]
            if colour not in coloursInHicolorIcon:
                coloursInHicolorIcon.append( colour )

    return coloursInHicolorIcon


def _copyHicolorIconsCreateThemedIcons( directoryIndicator, directoryReleaseIndicator ):
    directoryReleaseIndicatorIcons = directoryReleaseIndicator + os.sep + "icons"

    directoryReleaseIndicatorIconsHicolor = Path( directoryReleaseIndicatorIcons + os.sep + "hicolor" )
    directoryReleaseIndicatorIconsHicolor.mkdir( parents = True )

    directoryIndicatorIcons = directoryIndicator + os.sep + "icons"
    for hicolorIcon in list( Path( directoryIndicatorIcons ).rglob( "*.svg" ) ):
        shutil.copy( hicolorIcon, directoryReleaseIndicatorIconsHicolor )

        coloursInHicolorIcon = _getColoursInHicolorIcon( hicolorIcon )
        for themeName in indicatorbase.IndicatorBase.ICON_THEMES:
            directoryReleaseIndicatorIconsTheme = Path( directoryReleaseIndicatorIcons + os.sep + themeName )
            if not directoryReleaseIndicatorIconsTheme.exists(): # Must check as Will have been created if there is more than one icon.
                directoryReleaseIndicatorIconsTheme.mkdir( parents = True )

            shutil.copy( hicolorIcon, directoryReleaseIndicatorIconsTheme )

            for colour in coloursInHicolorIcon:
                icon = Path( str( directoryReleaseIndicatorIconsTheme ) + os.sep + hicolorIcon.name )
                with open( icon, 'r' ) as f:
                    fileData = f.read().replace( '#' + colour + ';', '#' + indicatorbase.IndicatorBase.ICON_THEMES[ themeName ] + ';' )

                with open( icon, 'w' ) as f:
                    f.write( fileData )


def _copyPOCreateMO( directoryIndicator, directoryReleaseIndicator ):
    directoryReleaseIndicatorPO = Path( str( directoryReleaseIndicator ) + os.sep + "po" )
    directoryIndicatorPO = directoryIndicator + os.sep + "po"

    shutil.copytree( directoryIndicatorPO, directoryReleaseIndicatorPO )
    os.remove( str( directoryReleaseIndicatorPO ) + os.sep + "LINGUAS" )
    os.remove( str( directoryReleaseIndicatorPO ) + os.sep + "POTFILES.in" )

    # Append translations from indicator-base to POT.
    command = \
        "msgcat --use-first " + \
        str( directoryReleaseIndicatorPO ) + os.sep + directoryIndicator + ".pot " + \
        "indicator-base" + os.sep + "po" + os.sep + "indicatorbase.pot " + \
        "--output-file=" + str( directoryReleaseIndicatorPO ) + os.sep + directoryIndicator + ".pot"

    subprocess.call( command, shell = True )

    # Append translations from indicatorbase to PO files.
    for po in list( directoryReleaseIndicatorPO.rglob( "*.po" ) ):
        languageCode = po.parent.parts[ -1 ]

        command = \
            "msgcat --use-first " + \
            str( po ) + " " + \
            "indicator-base" + os.sep + "po" + os.sep + languageCode + os.sep + "indicatorbase.po " + \
            "--output-file=" + str( po )

        subprocess.call( command, shell = True )

    # Create .mo files.
    for po in list( directoryReleaseIndicatorPO.rglob( "*.po" ) ):
        command = \
            "msgfmt " + str( po ) + \
            " --output-file=" + str( po.parent ) + os.sep + str( po.stem ) + ".mo"

        subprocess.call( command, shell = True )


def _createOrigTarGz( directoryIndicator, directoryReleaseIndicator, version ):
    command = \
        "tar -czf " + \
        "\"" + directoryIndicator + '_' + version + ".orig.tar.gz" + "\" " + \
        directoryIndicator + '-' + version

    subprocess.call(
        command,
        shell = True,
        cwd = str( Path( directoryReleaseIndicator ).parent ) )


def _copyDebianCopyright( directoryIndicator, directoryReleaseIndicator ):
    # Get start year from CHANGELOG.md (first year of release is next to first release version).
    with open( str( directoryIndicator ) + os.sep + "CHANGELOG.md", 'r' ) as f:
        contents = f.read()
        indexFirstRelease = contents.rfind( "## v" )
        indexLeftParenthesis = contents.find( '(', indexFirstRelease )
        startYear = contents[ indexLeftParenthesis + 1 : indexLeftParenthesis + 1 + 4 ]

    releaseCopyrightFile = directoryReleaseIndicator + os.sep + "debian" + os.sep + "copyright"
    with open( releaseCopyrightFile, 'r' ) as f:
        fileData = \
            f.read() \
            .replace( "%%STARTYEAR%%", startYear ) \
            .replace( "%%ENDYEAR%%", str( datetime.datetime.now().year ) ) # Set end year to current year.

    with open( releaseCopyrightFile, 'w' ) as f:
        f.write( fileData )

    _chmodReadAndWriteForAll( releaseCopyrightFile )


def _copyDebianControl( directoryIndicator, directoryReleaseIndicator, pyprojectTomlMetadata ):
    directoryIndicatorControlConfigurationFile = \
        directoryIndicator + os.sep + "packaging" + os.sep + "linux" + os.sep + "debian" + os.sep + "control.cfg"

    with open( directoryIndicatorControlConfigurationFile, 'r' ) as f:
        # There might be an '=' in the long description, so safest to split on '%%='.
        controlConfiguration = \
            dict( [ [ x[ 0 ] + "%%", x[ 1 ] ]
                    for x in [
                        line.strip().split( "%%=" ) for line in f if len( line.strip() ) > 0 ] ] )

    if "%%DEPENDS%%" in controlConfiguration:
        controlConfiguration[ "%%DEPENDS%%" ] = ', ' + controlConfiguration[ "%%DEPENDS%%" ]

    else:
        controlConfiguration[ "%%DEPENDS%%" ] = ''

    if "%%DESCRIPTION_EXTENDED%%" in controlConfiguration:
        descriptionExtended = ""
        for line in textwrap.wrap( controlConfiguration[ "%%DESCRIPTION_EXTENDED%%" ], 78 ):
            descriptionExtended += ' ' + line + '\n'

        controlConfiguration[ "%%DESCRIPTION_EXTENDED%%" ] = descriptionExtended[ : -1 ] # Remove last newline.

    else:
        controlConfiguration[ "%%DESCRIPTION_EXTENDED%%" ] = ''

    directoryReleaseIndicatorControlFile = directoryReleaseIndicator + os.sep + "debian" + os.sep + "control"
    with open( directoryReleaseIndicatorControlFile, 'r' ) as f:
        nameEmail = pyprojectTomlMetadata[ "authors" ][ 0 ].split( ',' )
        fileData = \
            f.read() \
             .replace( "%%NAME%%", pyprojectTomlMetadata[ "name" ] ) \
             .replace( "%%MAINTAINER_NAME%%", nameEmail[ 0 ].split( '"' )[ 1 ] ) \
             .replace( "%%MAINTAINER_EMAIL%%", nameEmail[ 1 ].split( '"' )[ 1 ] ) \
             .replace( "%%HOMEPAGE%%", pyprojectTomlMetadata[ "homepage" ] ) \
             .replace( "%%DEPENDS%%", controlConfiguration[ "%%DEPENDS%%" ] ) \
             .replace( "%%DESCRIPTION_SINGLE_LINE_SYNOPSIS%%", pyprojectTomlMetadata[ "description" ] ) \
             .replace( "%%DESCRIPTION_EXTENDED%%", controlConfiguration[ "%%DESCRIPTION_EXTENDED%%" ] )

    with open( directoryReleaseIndicatorControlFile, 'w' ) as f:
        f.write( fileData )

    _chmodReadAndWriteForAll( directoryReleaseIndicatorControlFile )


def _createDebianInstall( directoryIndicator, directoryReleaseIndicator, directoryReleaseWheel ):
    # Create the debian/install file and insert paths to:
    #   readme
    #   license
    #   desktop file
    #   all Python files in src
    #   each icon in each theme, to scalable/apps, apps/16, apps/22, apps/24 and apps/48
    #   each mo file
    directoryReleaseIndicatorInstallFile = directoryReleaseIndicator + os.sep + "debian" + os.sep + "install"
    with open( directoryReleaseIndicatorInstallFile, 'w' ) as f:
        f.write( directoryIndicator + ".desktop usr/share/applications\n" )

        usrShareIndicator = " usr/share/" + directoryIndicator + '\n'
        f.write( "LICENSE.txt" + usrShareIndicator )
        f.write( "README.md" + usrShareIndicator )

        for wheel in list( Path( directoryReleaseWheel ).glob( '*' + directoryIndicator.replace( '-', '_' ) + "*.whl" ) ):
            f.write( wheel.name + usrShareIndicator )
            break

        pythonFiles = sorted( list( Path( directoryReleaseIndicator + os.sep + "src" ).glob( "*.py" ) ) )
        for pythonFile in pythonFiles:
            f.write( "src/" + pythonFile.name + usrShareIndicator )

        svgIcons = sorted(
            list( Path( directoryReleaseIndicator + os.sep + "icons" ).rglob( "*.svg" ) ),
            key = lambda x: str( x ).lower() )

        for svgIcon in svgIcons:
            base = "icons/" + svgIcon.parent.parts[ -1 ] + '/' + svgIcon.name + " usr/share/icons/" + svgIcon.parent.parts[ -1 ]
            f.write( base + '/scalable/apps\n' )
            f.write( base + '/apps/16\n' )
            f.write( base + '/apps/22\n' )
            f.write( base + '/apps/24\n' )
            f.write( base + '/apps/24\n' )

        for moFile in sorted( list( Path( directoryReleaseIndicator + os.sep + "po" ).rglob( "*.mo" ) ) ):
            languageCode = moFile.parent.parts[ -1 ]
            f.write( "po/" + languageCode + '/' + moFile.name + " /usr/share/locale/" + languageCode + "/LC_MESSAGES" )

    _chmodReadAndWriteForAll( directoryReleaseIndicatorInstallFile )


def _convertChangelogMarkdownToDebian( indicatorDirectory, releaseDirectoryForIndicator, pyprojectTomlMetadata ):
    nameEmail = pyprojectTomlMetadata[ "authors" ][ 0 ].split( ',' )

    command = \
        "python3 " + \
        "utils/convertMarkdownToDebianChangelog.py " + \
        indicatorDirectory + " " + \
        indicatorDirectory + os.sep + "CHANGELOG.md " + \
        releaseDirectoryForIndicator + os.sep + "debian" + os.sep + "changelog " + \
        '"' + nameEmail[ 0 ].split( '"' )[ 1 ] + "\" " + \
        nameEmail[ 1 ].split( '"' )[ 1 ]

    subprocess.call( command, shell = True )


def _copyDebian( directoryIndicator, directoryReleaseIndicator, directoryReleaseWheel, pyprojectTomlMetadata ):
    # Copy debian/ from indicator-base
    shutil.copytree(
        "indicator-base" + os.sep + "packaging" + os.sep + "linux" + os.sep + "debian",
        directoryReleaseIndicator + os.sep + "debian" )

    directoryIndicatorDebian = directoryIndicator + os.sep + "packaging" + os.sep + "linux" + os.sep + "debian"
    if os.path.exists( directoryIndicatorDebian + os.sep + "postinst" ):
        shutil.copy(
            directoryIndicatorDebian + os.sep + "postinst",
            directoryReleaseIndicator + os.sep + "debian" )

    if os.path.exists( directoryIndicatorDebian + os.sep + "postrm" ):
        shutil.copy(
            directoryIndicatorDebian + os.sep + "postrm",
            directoryReleaseIndicator + os.sep + "debian" )

    _copyDebianCopyright( directoryIndicator, directoryReleaseIndicator )
    _copyDebianControl( directoryIndicator, directoryReleaseIndicator, pyprojectTomlMetadata )
    _createDebianInstall( directoryIndicator, directoryReleaseIndicator, directoryReleaseWheel )
    _convertChangelogMarkdownToDebian( directoryIndicator, directoryReleaseIndicator, pyprojectTomlMetadata )


def _buildDebianSourcePackageForIndicator( directoryRelease, indicatorName ):
    pyprojectTomlMetadata = _getMetadataFromPyprojectToml( indicatorName )
    if pyprojectTomlMetadata:
        changelogMarkdown = indicatorName + os.sep + "CHANGELOG.md"
        if _ensureVersionInChangelogMarkdownMatchesPyprojectToml( changelogMarkdown, pyprojectTomlMetadata[ "version" ] ):

            directoryReleaseDebian = args.directoryRelease + os.sep + "debian"
            directoryReleaseIndicator = \
                _createReleaseDirectoryForIndicator( directoryReleaseDebian, indicatorName, pyprojectTomlMetadata[ "version" ] )

            if _ensureNoTODOsInSrc( indicatorName ):
                directoryReleaseWheel = directoryRelease + os.sep + "wheel"

                _createWheel( indicatorName, directoryRelease )
                _copyMiscellaneous( indicatorName, directoryReleaseIndicator, directoryReleaseWheel )
                _copySource( indicatorName, directoryReleaseIndicator )
                _copyHicolorIconsCreateThemedIcons( indicatorName, directoryReleaseIndicator )
                _copyPOCreateMO( indicatorName, directoryReleaseIndicator )
                _createOrigTarGz( indicatorName, directoryReleaseIndicator, pyprojectTomlMetadata[ "version" ] )

                _copyDebian(
                    indicatorName,
                    directoryReleaseIndicator,
                    directoryReleaseWheel,
                    pyprojectTomlMetadata )

                #TODO Check the parameters passed to debuild...I saw somewhere (cannot recall) slightly different parameters.
# https://help.launchpad.net/Packaging/PPA/BuildingASourcePackage
# I think debuild calls dpkg-buildpackage...
                # subprocess.call( "debuild -S -sa", shell = True, cwd = directoryReleaseIndicator )
                # subprocess.call( "debuild -sa -us -uc", shell = True, cwd = directoryReleaseIndicator ) #TODO Should/how to do a binary build?

                # shutil.rmtree( releaseDirectoryForIndicator )  #TODO Put back in
                pass #TODO Remove

#TODO Maybe print to user that they now should use the upload script...
#   echo -e "\nTo upload to LaunchPad, change to the 'build' directory and run:\n"
#   echo -e "    dput ppa:thebernmeister/ppa ${NAME}_${VERSION}-1_source.changes\n"
# }

        else:
            print( f"Unable to create .deb for { indicatorName }: the (most recent) version in CHANGELOG.md does not match that in pyproject.toml!" )


#TODO Might want a way to allow building a Deb binary?
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Create a Debian source package for one or more indicators." )

    parser.add_argument(
        "directoryRelease",
        help = "The output directory for the Debian source package. " +
               "If the directory specified is 'release', " +
               "the Debian source package will be created in 'release/debian'. " )

    parser.add_argument(
        "indicators",
        nargs = '+',
        help = "The list of indicators (such as indicator-fortune indicator-lunar) to build." )

    if Path( "utils/buildDebian.py" ).exists():
        args = parser.parse_args()

        for indicatorToBuild in args.indicators:
            _buildDebianSourcePackageForIndicator( args.directoryRelease, indicatorToBuild )

    else:
        print( "The script must be run from the top level directory (one above utils)." )
        print( "For example:" )
        print( "\tpython3 utils/buildDebian.py release indicator-fortune" )
