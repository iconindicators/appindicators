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


# Create a star ephemeris for use in both PyEphem and Skyfield using stars from PyEphem,
# keeping only those present in the IAU CSN Catalog with accompanying HIP and absolute magnitude.


import argparse
import textwrap

from pandas import read_csv
from skyfield.api import Star, load
from skyfield.data import hipparcos

from ephem import stars


# Indices for columns at http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt.
iaucsn_name_start = 19
iaucsn_name_end = 36
iaucsn_hip_start = 91
iaucsn_hip_end = 96


def get_stars_and_hips( iau_catalog_file ):
    stars_from_pyephem = stars.stars.keys()
    stars_and_hips_from_iau = [ ]
    f_in = open( iau_catalog_file, 'r' )
    for line in f_in:
        if line.startswith( '#' ) or line.startswith( '$' ):
            continue

        try:
            name_utf8 = line[ iaucsn_name_start - 1 : iaucsn_name_end - 1 + 1 ].strip()
            if name_utf8 in stars_from_pyephem:
                hip = int( line[ iaucsn_hip_start - 1 : iaucsn_hip_end - 1 + 1 ] )
                stars_and_hips_from_iau.append( [ name_utf8, hip ] )

        except ValueError:
            pass

    f_in.close()

    return stars_and_hips_from_iau


def print_formatted_stars( stars_and_hips ):
    print( "Printing formatted stars from", star_information_url )
    for name, hip in stars_and_hips:
        print(
            "        [ " + \
            "\"" + name.upper() + "\"," + \
            ( ' ' * ( iaucsn_name_end - iaucsn_name_start - len( name ) + 1 ) ) + \
            str( hip ) + ", " + \
            ( ' ' * ( iaucsn_hip_end - iaucsn_hip_start - len( str( hip ) ) + 1 ) ) + \
            "_( \"" + name.title() + "\" )," + \
            ( ' ' * ( iaucsn_name_end - iaucsn_name_start - len( name ) + 1 ) ) + \
            "_( \"" + name.upper() + "\" ) ]," )

    print( "Done" )


def create_ephemeris_skyfield( out_file, star_ephemeris, stars_and_hips ):
    print( "Creating", out_file, "for Skyfield..." )
    hipparcos_identifiers = [ star_and_hip[ 1 ] for star_and_hip in stars_and_hips ]
    with load.open( star_ephemeris, "rb" ) as in_file, open( out_file, "wb" ) as f:
        for line in in_file:
            hip = int( line.decode()[ 9 - 1 : 14 - 1 + 1 ].strip() ) # HIP is located at bytes 9 - 14, http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
            if hip in hipparcos_identifiers:
                f.write( line )

    print( "Done" )


# Mostly taken from https://github.com/brandon-rhodes/pyephem/blob/master/bin/rebuild-star-data
def print_ephemeris_pyephem( bsp_file , star_ephemeris, stars_and_hips ):
    print( "Printing ephemeris for PyEphem..." )
    with load.open( star_ephemeris, "rb" ) as f:
        stars = hipparcos.load_dataframe( f )
        f.seek( 0 )
        stars_with_spectral_type = \
            read_csv(
                f,
                sep = '|',
                names = hipparcos._COLUMN_NAMES,
                na_values = [ '     ', '       ', '        ', '            ' ],
                low_memory = False,
        )

    stars_with_spectral_type = stars_with_spectral_type.set_index( "HIP" )
    sun_at = load( bsp_file )[ "Sun" ].at( load.timescale().J( 2000.0 ) )
    for name, hip in stars_and_hips:
        row = stars.loc[ hip ]
        star = Star.from_dataframe( row )
        right_ascension, declination, _ = sun_at.observe( star ).radec()

        spectral_type = stars_with_spectral_type.loc[ hip ][ "SpType" ]
        if isinstance( spectral_type, str ):
            spectral_type = spectral_type[ : 2 ]

        else:
            spectral_type = "  "  # Is NaN; to fix, set to two blank characters (see _libastro.c).

        components = [
            name.upper(),
            "f|S|" +
            spectral_type,
            '%.8f' % right_ascension.hours + '|' + str( star.ra_mas_per_year ),
            '%.8f' % declination.degrees + '|' + str( star.dec_mas_per_year ),
            row[ "magnitude" ],
        ]

        line = ','.join( str( item ) for item in components )
        print( "        \"" + name.upper() + "\"" + ( ' ' * ( iaucsn_name_end - iaucsn_name_start - len( name ) + 1 ) ) + ": \"" + line + "\"," )

    print( "Done" )


if __name__ == "__main__":
    description = \
        textwrap.dedent( '''\
            Takes the star information and:
            1) Prints a list of star names, corresponding HIP and star name for translation (as a Python list of lists).
            2) Creates a star ephemeris file for Skyfield.
            3) Prints a star ephemeris for PyEphem as a Python dictionary.
        
            For example: python3 %(prog)s IAU-CSN.txt hip_main.dat de421.bsp stars.dat

            -------------------------------------------------------
            --- INPUT & OUTPUT PATHNAMES CONTAINING SPACES MUST ---
            ---     * BE DOUBLE QUOTED                          ---
            ---     * HAVE SPACES ESCAPED WITH A \              ---
            -------------------------------------------------------''' )

    parser = \
        argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = description )

    star_information_url = "http://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt"
    _help = "A text file containing the list of stars, downloaded from " + star_information_url + "."
    parser.add_argument( "star_information", help = _help )

    star_ephemeris_url = "https://cdsarc.cds.unistra.fr/ftp/cats/I/239/"
    _help = "A star ephemeris file, typically hip_main.dat and downloaded from " + star_ephemeris_url + "."
    parser.add_argument( "star_ephemeris", help = _help )

    planet_ephemeris_url = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets"
    _help = "A planet ephemeris file in .bsp format, downloaded from " + planet_ephemeris_url + "."
    parser.add_argument( "planet_ephemeris", help = _help )

    _help = "The output filename for the Skyfield star ephemeris."
    parser.add_argument( "output_filename_for_skyfield_star_ephemeris", help = _help ) 

    args = parser.parse_args()

    stars_and_hips = get_stars_and_hips( args.star_information )
    print_formatted_stars( stars_and_hips )
    create_ephemeris_skyfield( args.output_filename_for_skyfield_star_ephemeris, args.star_ephemeris, stars_and_hips )
    print_ephemeris_pyephem( args.planet_ephemeris, args.star_ephemeris, stars_and_hips )
