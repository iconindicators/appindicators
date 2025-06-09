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
From the intersection of stars from the IAU CSN Catalog and PyEphem create...
    A list of stars for astrobase, with accompanying HIP.
    Ephemeris data for astropyephem.
    An ephemeris file for astroskyfield.
'''


#TODO Works on Debian 32 bit on the VM, but not on the laptop 
# (build error during the install of numpy, et al).
# Based on reading of numpy/pandas, should not install on 32 bit.
# Need more investigation...


#TODO May need to add to documentation notes about pinning numpy/pandas to 
# particular versions given Python versions may no longer be supported
# (for Ubuntu 20.04) and for 32 bit.
#
# Pandas 2.0.0 supports python3.8+ and numpy 1.20.3 so only good for ubuntu 20.04+
# 
# Pandas 2.1.0 supports python3.9+ and numpy 1.22.4 so only good for ubuntu 22.04+
# 
# Check for Fedora, Manjaro and openSUSE!


import argparse
import sys
import textwrap

if '../' not in sys.path:
    sys.path.insert( 0, '../../' ) # Allows calls to IndicatorBase.

from indicatorbase.src.indicatorbase.indicatorbase import IndicatorBase


if __name__ == "__main__":
    description = (
        textwrap.dedent(
            r'''
            Using a list of stars from IAU CSN:
            1) Prints a list of star names, corresponding HIP and star name
               for translation (as a Python3 list of lists) for astrobase.
            2) Creates a star ephemeris file for astroskyfield.
            3) Prints a star ephemeris for astropyephem as a Python3 dictionary.

            For example:
                python3 %(prog)s IAU-CSN.txt hip_main.dat de442s.bsp stars.dat

            Input and output pathnames which contain spaces must:
                * Be double quoted
                * Have spaces escaped with a \
            ''' ) )

    parser = (
        argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = description ) )

    parser.add_argument(
        "iau_catalog_file",
        help =
            "A text file containing the list of stars, downloaded from " +
            "http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt" )

    parser.add_argument(
        "star_ephemeris",
        help =
            "A star ephemeris file, typically hip_main.dat, downloaded from " +
            "https://cdsarc.cds.unistra.fr/ftp/cats/I/239" )

    parser.add_argument(
        "planet_ephemeris",
        help =
            "A planet ephemeris file in .bsp format, downloaded from " +
            "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets" )

    parser.add_argument(
        "output_filename_for_astroskyfield_star_ephemeris",
        help = "The output filename for the astroskyfield star ephemeris." )

    args = parser.parse_args()

    command = (
        "python3 -c \"import utils_ephemeris; "
        f"utils_ephemeris.create_ephemeris_stars( "
        f"\\\"{ args.output_filename_for_skyfield_star_ephemeris }\\\", "
        f"\\\"{ args.planet_ephemeris }\\\", "
        f"\\\"{ args.star_ephemeris }\\\", "
        f"\\\"{ args.iau_catalog_file }\\\" )\"" )

    IndicatorBase.run_python_command_in_virtual_environment(
        IndicatorBase.VENV_INSTALL,
        command,
        "ephem",
        "pandas",
        "skyfield" )
