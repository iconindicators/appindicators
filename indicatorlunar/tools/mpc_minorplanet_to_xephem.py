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


# Convert minor planet data in MPC format to XEphem format.
#
# Inspired by:
#    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/auxil/mpcorb2edb.pl
#
# MPC format:
#    https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
#
# XEphem format:
#    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501


import argparse
import gzip


century_map = {
    'I': 1800,
    'J': 1900,
    'K': 2000 }


# https://www.minorplanetcenter.net/iau/info/PackedDates.html
def get_unpacked_date( i ): return str( i ) if i.isdigit() else str( ord( i ) - ord( 'A' ) + 10 )


def process_and_write_one_line( line, output_file ):
    if len( line.strip() ) > 0:
        # Field numbers: 0   1   2   3   4   5   6   7   8   9   10   11   12   13   14   15   16   17   18   19   20   21   22
        start_indices = [ 1,  9, 15, 21, 27, 38, 49, 60, 71, 81,  93, 106, 108, 118, 124, 128, 138, 143, 147, 151, 162, 167, 195 ]
        end_indices =   [ 7, 13, 19, 25, 35, 46, 57, 68, 79, 91, 103, 106, 116, 122, 126, 136, 141, 145, 149, 160, 165, 194, 202 ]

        # Offset back to zero to match lines read into a string.
        start_indices = [ x - 1 for x in start_indices ]
        end_indices = [ x - 1 for x in end_indices ]

        fields = [ line[ i : j + 1 ] for i, j in zip( start_indices, end_indices ) ] # Inspired by https://stackoverflow.com/a/10851479/2156453
        name = fields[ 21 ].replace( '(', '' ).replace( ')', '' ).strip()
        absolute_magnitude = fields[ 1 ].strip()

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absolute_magnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            slope_parameter = fields[ 2 ].strip()

            epoch_packed = fields[ 3 ].strip()
            century = epoch_packed[ 0 ]
            last_two_digits_of_year = epoch_packed[ 1 : 3 ]
            year = str( century_map[ century ] + int( last_two_digits_of_year ) )
            month = get_unpacked_date( epoch_packed[ 3 ] )
            day = get_unpacked_date( epoch_packed[ 4 ] )
            epoch_date = month + '/' + day + '/' + year

            mean_anomaly_epoch = fields[ 4 ].strip()
            argument_perihelion = fields[ 5 ].strip()
            longitude_ascending_node = fields[ 6 ].strip()
            inclination_to_ecliptic = fields[ 7 ].strip()
            orbital_eccentricity = fields[ 8 ].strip()
            semimajor_axis = fields[ 10 ].strip()

            components = [
                name,
                'e',
                inclination_to_ecliptic,
                longitude_ascending_node,
                argument_perihelion,
                semimajor_axis,
                '0',
                orbital_eccentricity,
                mean_anomaly_epoch,
                epoch_date,
                "2000.0",
                absolute_magnitude,
                slope_parameter ]

            output_file.write( ','.join( components ) + '\n' )


def convert( in_file, header, out_file ):
    if in_file.endswith( ".gz" ):
        f_in = gzip.open( in_file, 'rt' )

    else:
        f_in = open( in_file, 'r' )

    f_out = open( out_file, 'w' )

    if header:
        end_of_header = False
        for line in f_in:
            if end_of_header:
                process_and_write_one_line( line, f_out )

            elif line.startswith( "----------" ):
                end_of_header = True

    else:
        for line in f_in:
            process_and_write_one_line( line, f_out )

    f_in.close()
    f_out.close()


if __name__ == "__main__":
    description = \
        "Convert a minor planet text file such as MPCORB.DAT or MPCORB.DAT.gz from MPC to XEphem format. " + \
        "If the file ends in '.gz' the file will be treated as a gzip file; otherwise the file is assumed to be text."

    parser = argparse.ArgumentParser( description = description )

    parser.add_argument( "in_file", help = "File to convert" )

    parser.add_argument(
        "--header",
        action = "store_true",
        help = "Only specify this option if the file to convert contains a header, such as MPCORB.DAT or MPCORB.DAT.gz." )

    parser.add_argument( "out_file", help = "Output file to be created" )

    args = parser.parse_args()
    convert( args.in_file, args.header, args.out_file )
