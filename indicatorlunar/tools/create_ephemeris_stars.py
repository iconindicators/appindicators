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
Create a star ephemeris for use in both PyEphem and Skyfield
using stars from PyEphem, keeping only those present in the
IAU CSN Catalog with accompanying HIP and absolute magnitude.
'''


import argparse
import textwrap

from pandas import read_csv
from skyfield.api import Star, load
from skyfield.data import hipparcos

from ephem import stars


# Indices for columns at
#   http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt
IAUCSN_NAME_START = 19
IAUCSN_NAME_END = 36
IAUCSN_HIP_START = 91
IAUCSN_HIP_END = 96


def get_stars_and_hips( iau_catalog_file ):
    stars_from_pyephem = stars.stars.keys()
    stars_and_hips_from_iau = [ ]
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

                        stars_and_hips_from_iau.append( [ name_utf8, hip ] )

                except ValueError:
                    pass

    return stars_and_hips_from_iau


def print_formatted_stars(
    stars_and_hips_,
    star_information_url ):

    print( "Printing formatted stars from", star_information_url )
    for name, hip in stars_and_hips_:
        print(
            "        [ " +
            f"\"{ name.upper() }\"," +
            ( ' ' * ( IAUCSN_NAME_END - IAUCSN_NAME_START - len( name ) + 1 ) ) +
            f"{ str( hip ) }, " +
            ( ' ' * ( IAUCSN_HIP_END - IAUCSN_HIP_START - len( str( hip ) ) + 1 ) ) +
            f"_( \"{ name.title() }\" )," +
            ( ' ' * ( IAUCSN_NAME_END - IAUCSN_NAME_START - len( name ) + 1 ) ) +
            f"_( \"{ name.upper() }\" ) ]," )

    print( "Done" )


def create_ephemeris_skyfield(
    out_file,
    star_ephemeris,
    stars_and_hips_ ):

    print( "Creating", out_file, "for Skyfield..." )
    hipparcos_identifiers = (
        [ star_and_hip[ 1 ] for star_and_hip in stars_and_hips_ ] )

    with load.open( star_ephemeris, "rb" ) as in_file, open( out_file, "wb" ) as f:
        for line in in_file:
            # HIP is located at bytes 9 - 14
            # http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
            hip = int( line.decode()[ 9 - 1 : 14 - 1 + 1 ].strip() )
            if hip in hipparcos_identifiers:
                f.write( line )

    print( "Done" )


def print_ephemeris_pyephem(
    bsp_file,
    star_ephemeris,
    stars_and_hips_ ):
    '''
    Mostly taken from
        https://github.com/brandon-rhodes/pyephem/blob/master/bin/rebuild-star-data
    '''
    print( "Printing ephemeris for PyEphem..." )
    with load.open( star_ephemeris, "rb" ) as f:
        stars_ = hipparcos.load_dataframe( f )
        f.seek( 0 )
        stars_with_spectral_type = (
            read_csv(
                f,
                sep = '|',
                names = hipparcos._COLUMN_NAMES,
                na_values = [ '     ', '       ', '        ', '            ' ],
                low_memory = False, ) )

    stars_with_spectral_type = stars_with_spectral_type.set_index( "HIP" )
    sun_at = load( bsp_file )[ "Sun" ].at( load.timescale().J( 2000.0 ) )
    for name, hip in stars_and_hips_:
        row = stars_.loc[ hip ]
        star = Star.from_dataframe( row )
        right_ascension, declination, _ = sun_at.observe( star ).radec()

        spectral_type = stars_with_spectral_type.loc[ hip ][ "SpType" ]
        if isinstance( spectral_type, str ):
            spectral_type = spectral_type[ : 2 ]

        else:
            # Is NaN; to fix, set to two blank characters (see _libastro.c).
            spectral_type = "  "

        components = [
            name.upper(),
            "f|S|" +
            spectral_type,
            f"{right_ascension.hours:.8f}|{ star.ra_mas_per_year }",
            f"{declination.degrees:.8f}|{ star.dec_mas_per_year }",
            row[ "magnitude" ],
        ]

        line = ','.join( str( item ) for item in components )
        padding = ' ' * ( IAUCSN_NAME_END - IAUCSN_NAME_START - len( name ) + 1 )
        print( "        \"" + name.upper() + "\"" + padding + ": \"" + line + "\"," )

    print( "Done" )


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

            -------------------------------------------------------
            --- INPUT & OUTPUT PATHNAMES CONTAINING SPACES MUST ---
            ---     * BE DOUBLE QUOTED                          ---
            ---     * HAVE SPACES ESCAPED WITH A \              ---
            -------------------------------------------------------
            ''' ) )

    parser = (
        argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = description ) )

    STAR_INFORMATION_URL = (
        "http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt" )

    parser.add_argument(
        "star_information",
        help =
            "A text file containing the list of stars, downloaded from " +
            STAR_INFORMATION_URL + "." )

    STAR_EPHEMERIS_URL = "https://cdsarc.cds.unistra.fr/ftp/cats/I/239/"
    parser.add_argument(
        "star_ephemeris",
        help =
            "A star ephemeris file, typically hip_main.dat downloaded from " +
            STAR_EPHEMERIS_URL + "." )

    PLANET_EPHEMERIS_URL = (
        "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets" )

    parser.add_argument(
        "planet_ephemeris",
        help =
            "A planet ephemeris file in .bsp format, downloaded from " +
            PLANET_EPHEMERIS_URL + "." )

    parser.add_argument(
        "output_filename_for_skyfield_star_ephemeris",
        help = "The output filename for the Skyfield star ephemeris." )

    args = parser.parse_args()

    stars_and_hips = get_stars_and_hips( args.star_information )
    print_formatted_stars( stars_and_hips, STAR_INFORMATION_URL )
    create_ephemeris_skyfield(
        args.output_filename_for_skyfield_star_ephemeris,
        args.star_ephemeris,
        stars_and_hips )

    print_ephemeris_pyephem(
        args.planet_ephemeris,
        args.star_ephemeris,
        stars_and_hips )
