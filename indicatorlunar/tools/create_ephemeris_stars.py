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
Create a star ephemeris for astropyephem and astroskyfield
using stars from PyEphem, retaining only those stars present in
the IAU CSN Catalog, with accompanying HIP and absolute magnitude.
'''

#TODO On Debian 32 bit on the VM, the import of pandas, skyfield and ephem
# did not work...but works on Ubuntu...is this because these are already installed
# and on the OS path on Ubuntu?
#
# Need to make a change so that any errors (import or otherwise) show on the console.


#TODO Given that pandas and numpy (through skyfield) are used in this script,
# test to see if works on 32 bit (both laptop and VM),
# which may require version pinning.
#
# May also require pinning for Ubuntu 20.04 (using an old Python3 version).
#
# If ultimately does not work on 32 bit,
# put in a note in the comment header and the parser description.
#
# Pandas 2.0.0 supports python3.8+ and numpy 1.20.3 so only good for ubuntu 20.04+
# 
# Pandas 2.1.0 supports python3.9+ and numpy 1.22.4 so only good for ubuntu 22.04+
# 
# Check for Fedora, Manjaro and openSUSE!
#
# Test running this script from installed in .venv_indicators


import argparse
import sys
import textwrap

from pandas import read_csv

from skyfield.api import Star, load
from skyfield.data import hipparcos

from ephem import stars

if "../" not in sys.path:
    sys.path.insert( 0, "../../" ) # Allows calls to IndicatorBase.

from indicatorbase.src.indicatorbase.indicatorbase import IndicatorBase


# Indices for columns at
#   http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt
IAUCSN_NAME_START = 19
IAUCSN_NAME_END = 36
IAUCSN_HIP_START = 91
IAUCSN_HIP_END = 96


def _get_names_to_hips( iau_catalog_file ):
    '''
    Reads the IAU Catalog of Star Names file and returns a dictionary:
        Key: star name (string(
        Value: HIP (int)
    '''
    stars_from_pyephem = stars.stars.keys()
    names_to_hips = { }
    with open( iau_catalog_file, 'r', encoding = "utf-8" ) as f_in:
        for line in f_in:
            if not ( line.startswith( '#' ) or line.startswith( '$' ) ):
                try:
                    start = IAUCSN_NAME_START - 1
                    end = IAUCSN_NAME_END - 1 + 1
                    name_utf8 = line[ start : end ].strip()
                    if name_utf8 in stars_from_pyephem:
                        start = IAUCSN_HIP_START - 1
                        end = IAUCSN_HIP_END - 1 + 1
                        hip = int( line[ start : end ] )

                        names_to_hips[ name_utf8 ] = hip

                except ValueError:
                    pass

    return names_to_hips


def _print_formatted_stars(
    names_to_hips ):

    print( f"List of stars for AstroBase:" )
    name_length = IAUCSN_NAME_END - IAUCSN_NAME_START
    hip_length = IAUCSN_HIP_END - IAUCSN_HIP_START
    for name in sorted( names_to_hips.keys() ):
        hip = names_to_hips[ name ]
        spacing_name = ' ' * ( name_length - len( name ) - 1 )
        spacing_hip = ' ' * ( hip_length - len( str( hip ) ) + 1 )
        print(
            "        [ " +
            f"\"{ name.upper() }\",{ spacing_name }" +
            f"{ str( hip ) }, { spacing_hip }" +
            f"_( \"{ name.title() }\" ),{ spacing_name }" +
            f"_( \"{ name.upper() }\" ) ]," )

    print( "Done" )


def _create_ephemeris_skyfield(
    out_file,
    star_ephemeris,
    hipparcos_identifiers ):

    print( f"Creating { out_file } for Skyfield..." )
    with load.open( star_ephemeris, "rb" ) as in_file, open( out_file, "wb" ) as f:
        for line in in_file:
            # HIP is located at bytes 9 - 14
            #    http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
            hip = int( line.decode()[ 9 - 1 : 14 - 1 + 1 ].strip() )
            if hip in hipparcos_identifiers:
                f.write( line )

    print( "Done" )


def _print_ephemeris_pyephem(
    planet_ephemeris,
    star_ephemeris,
    names_to_hips ):
    '''
    Taken from
        https://github.com/brandon-rhodes/pyephem/blob/master/bin/rebuild-star-data
    '''
    print( "Ephemeris for PyEphem..." )

    with load.open( star_ephemeris ) as f:
        dataframe = hipparcos.load_dataframe( f )

    # Required to obtain spectral type as this is dropped from the above load.
    with load.open( star_ephemeris ) as f:
        dataframe_raw = (
            read_csv(
                f,
                sep = '|',
                names = hipparcos._COLUMN_NAMES,
                na_values = [ '     ', '       ', '        ', '            ' ],
                low_memory = False ) )

        dataframe_raw = dataframe_raw.set_index( "HIP" )

    timescale = load.timescale().J( 2000.0 )
    sun_at = load( planet_ephemeris )[ "Sun" ].at( timescale )

    results = [ ]
    for name in sorted( list( names_to_hips.keys() ) ):
        hip = names_to_hips[ name ]
        row = dataframe.loc[ hip ]
        star = Star.from_dataframe( row )
        right_ascension, declination, _ = sun_at.observe( star ).radec()

        components = [
            name.upper(),
            "f|S|" +
            dataframe_raw.loc[ hip ][ "SpType" ][ : 2 ],
            f"{right_ascension.hours:.8f}|{ star.ra_mas_per_year }",
            f"{declination.degrees:.8f}|{ star.dec_mas_per_year }",
            row[ "magnitude"] ]

        line = ','.join( str( item ) for item in components )
        results.append(
            f"        \"{ name.upper() }\" :\n            \"{ line }\"," )

    results.sort()
    results[ -1 ] = results[ -1 ][ 0 : -1 ] # Trim last ,
    print( *results, sep = '\n' )
    print( "Done" )


def _create_ephemeris_stars(
        output_filename_for_skyfield_star_ephemeris,
        planet_ephemeris,
        star_ephemeris,
        iau_catalog_file ):

    names_to_hips = _get_names_to_hips( iau_catalog_file )

    _print_formatted_stars( names_to_hips )

    _create_ephemeris_skyfield(
        output_filename_for_skyfield_star_ephemeris,
        star_ephemeris,
        list( names_to_hips.values() ) )

    _print_ephemeris_pyephem(
        planet_ephemeris,
        star_ephemeris,
        names_to_hips )


if __name__ == "__main__":
    description = (
        textwrap.dedent(
            r'''
            Takes the star information and:
            1) Prints a list of star names, corresponding HIP and star name
               for translation (as a Python list of lists).
            2) Creates a star ephemeris file for Skyfield.
            3) Prints a star ephemeris for PyEphem as a Python dictionary.

            For example:
                python3 %(prog)s IAU-CSN.txt hip_main.dat de421.bsp stars.dat

            Input and output pathnames which contain spaces must:
                - Be double quoted
                - Have spaces escaped with a \
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
            "A star ephemeris file, typically hip_main.dat downloaded from " +
            "https://cdsarc.cds.unistra.fr/ftp/cats/I/239" )

    parser.add_argument(
        "planet_ephemeris",
        help =
            "A planet ephemeris file in .bsp format, downloaded from " +
            "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets" )

    parser.add_argument(
        "output_filename_for_skyfield_star_ephemeris",
        help = "The output filename for the Skyfield star ephemeris." )

    args = parser.parse_args()

    command = (
        "python3 -c \"import create_ephemeris_stars; "
        f"create_ephemeris_stars._create_ephemeris_stars( "
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
