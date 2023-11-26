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


#TODO Apparently dput can take more than one package at a time to upload...
# ...so maybe use that in this script.
#
# Or maybe no need for a script.
# Instead some documentation on the readme.md about how to build and how to release:
# build uses the script;
# release is just cd into the release/debian directory and dput for each package.
# Maybe then need a separate developers.md page?  


#TODO This was a copy of the build script...will need to be written to 
# take a number of build debian source packages and upload to Launchpad.


#TODO May need some of this for dput/launchpad
# Install the packages:
#   sudo apt install build-essential devscripts dh-make dh-python gpg lintian rsync
#
#
# Import secret key into gpg.  In a terminal, change to the directory containing the files
#
#	'Bernard Giannetti.asc' pubring.pkr secring.skr
#
# and run
#
#	gpg --import secring.skr
#
# References for building a Debian package for PPA...
#    http://askubuntu.com/questions/27715/create-a-deb-package-from-scripts-or-binaries
#    http://askubuntu.com/questions/28562/how-do-i-create-a-ppa-for-a-working-program
#    http://askubuntu.com/questions/90764/how-do-i-create-a-deb-package-for-a-single-python-script
#	 https://stackoverflow.com/questions/65117979/problems-using-debuild-to-upload-a-python-gtk-program-to-launchpad
#	 https://askubuntu.com/questions/399552/how-to-create-a-deb-package-for-a-python3-script
#    http://blog.garethj.com/2009/06/02/building-deb-packages-for-python-applications
#    http://developer.ubuntu.com/packaging/html/debian-dir-overview.html
#    http://help.launchpad.net/Packaging/PPA/Uploading
#    http://help.ubuntu.com/community/PythonRecipes/DebianPackage
#    http://savetheions.com/2010/01/20/packaging-python-applicationsmodules-for-debian
#    http://shallowsky.com/blog/programming/packaging-launchpad-ppas.html
#    http://ubuntulinuxtipstricks.blogspot.com.au/2010/08/is-packaging-new-software-hard.html
#    http://wiki.debian.org/Python/Packaging
#    http://wiki.ubuntu.com/MOTU/School/PackagingWithoutCompiling
#    http://wiki.ubuntu.com/PackagingGuide/HandsOn
#    http://wiki.ubuntu.com/PackagingGuide/Python
#    http://www.debian.org/doc/manuals/maint-guide
#    http://www.debian.org/doc/packaging-manuals/python-policy
#    http://www.debian-administration.org/articles/336
#    http://news.softpedia.com/news/How-to-Repack-Deb-Files-on-Debian-and-Ubuntu-404930.shtml
#    http://blog.packagecloud.io/debian/debuild/packaging/2015/06/08/buildling-deb-packages-with-debuild
#    https://standards.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html
#    https://developer.gnome.org/icon-theme-spec/



from pathlib import Path
from subprocess import call

import argparse, datetime, os, re, shutil, stat, subprocess, sys, textwrap



def _releaseToLaunchpad( releaseDirectoryForIndicator ):
    pass
#TODO Maybe print to user that they now should use the upload script...
#   echo -e "\nTo upload to LaunchPad, change to the 'build' directory and run:\n"
#   echo -e "    dput ppa:thebernmeister/ppa ${NAME}_${VERSION}-1_source.changes\n"
# }


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

        directoryReleaseDebian = args.directoryRelease + os.sep + "debian"
        for indicatorToBuild in args.indicators:
            _buildDebianSourcePackageForIndicator( directoryReleaseDebian, indicatorToBuild )

    else:
        print( "The script must be run from the top level directory (one above utils)." )
        print( "For example:" )
        print( "\tpython3 utils/buildDebian.py release indicator-fortune" )
