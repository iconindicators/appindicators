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


#TODO This script does not (yet) include the icons/po/mo stuff,
# so does not technically create a true whl.
#
# Am moving toward building a full wheel...to include icons/mo.
# If that works and can access icons/mo, 
# then likely can solely have the indicators deployed via PyPI.
#
# In that case, Indicator Lunar requires planets.bsp and stars.dat
# to be created during the build process and copied (then removed)
# to the src/indicatorlunar directory (and included in the pyproject.toml).


import argparse, os, shutil, subprocess

from pathlib import Path


def _buildWheelForIndicators( directoryRelease, indicatorNames ):
    directoryVenv = Path( directoryRelease + os.sep + ".venv" )
    if directoryVenv.is_dir():
        print( "- - - - - - - - - - - - - - - - - - - - -" )
        print( "Using the venv located at:", directoryVenv )
        print( "- - - - - - - - - - - - - - - - - - - - -" )

    else:
        command = \
            "python3 -m venv " + str( directoryVenv ) + " && " + \
            ". ./" + str( directoryVenv ) + "/bin/activate && " + \
            "python3 -m pip install --upgrade build"

        subprocess.call( command, shell = True )

    directoryWheel = Path( directoryRelease + os.sep + "wheel" )
    if not Path( directoryWheel ).is_dir():
        directoryWheel.mkdir( parents = True )

    for indicatorName in indicatorNames:
        for wheel in list( Path( directoryWheel ).glob( "*.whl" ) ):
            if indicatorName.replace( '-', '_' ) in wheel.name:
                os.remove( wheel )

        for origTarGz in list( Path( directoryWheel ).glob( "*.tar.gz" ) ):
            if indicatorName in origTarGz.name:
                os.remove( origTarGz )

        licenseText = "LICENSE.txt"
        shutil.copy( licenseText, indicatorName )

        readmeMarkdown = "README.md"
        shutil.copy( readmeMarkdown, indicatorName )

        indicatorBaseSource = "indicator-base/src/indicatorbase/indicatorbase.py"
        indicatorBaseDestination = indicatorName + os.sep + "src" + os.sep + indicatorName.replace( '-', '' )
        shutil.copy( indicatorBaseSource, indicatorBaseDestination )

        command = \
            ". ./" + str( directoryVenv ) + "/bin/activate && " + \
            "cd " + indicatorName + " && " + \
            "python3 -m build --outdir " + "../" + str( directoryWheel )

        subprocess.call( command, shell = True )

        os.remove( indicatorName + os.sep + licenseText )
        os.remove( indicatorName + os.sep + readmeMarkdown )
        os.remove( indicatorBaseDestination + os.sep + "indicatorbase.py" )

        for egg in list( Path( indicatorName + os.sep + "src" ).glob( "*.egg-info" ) ):
            shutil.rmtree( egg )


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
