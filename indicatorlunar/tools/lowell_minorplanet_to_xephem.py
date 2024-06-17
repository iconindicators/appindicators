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


# Convert minor planet data in Lowell format to XEphem format.
#
# Inspired by:
#    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/auxil/astorb2edb.pl
#
# Lowell format:
#    https://asteroid.lowell.edu/main/astorb/
#
# XEphem format:
#    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501


import argparse
import gzip


def process_and_write_one_line( line, output_file ):
    if len( line.strip() ) > 0:
        start_indices = [ 1, 8, 27, 43, 49, 55, 60, 66, 71, 96, 101, 107, 116, 127, 138, 148, 159, 169, 183, 192, 200, 209, 218, 235, 252 ]
        start_indices = [ x - 1 for x in start_indices ] # Offset back to zero to match each line read into a string.

        parts = \
            [ "OFFSET TO ALIGN WITH FIELD NUMBERING" ] + \
            [ line[ i : j ] for i, j in zip( start_indices, start_indices[ 1 : ] + [ None ] ) ] # Inspired by https://stackoverflow.com/a/10851479/2156453

        number = parts[ 1 ].strip()
        name = parts[ 2 ].strip()
        absolute_magnitude = parts[ 4 ].strip()

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absolute_magnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            slope_parameter = parts[ 5 ].strip()
            epoch_date = parts[ 12 ].strip()
            mean_anomaly_epoch = parts[ 13 ].strip()
            argument_perihelion = parts[ 14 ].strip()
            longitude_ascending_node = parts[ 15 ].strip()
            inclination_to_ecliptic = parts[ 16 ].strip()
            orbital_eccentricity = parts[ 17 ].strip()
            semimajor_axis = parts[ 18 ].strip()

            components = [
                ( number + ' ' + name ).strip(),
                'e',
                inclination_to_ecliptic,
                longitude_ascending_node,
                argument_perihelion,
                semimajor_axis,
                '0',
                orbital_eccentricity,
                mean_anomaly_epoch,
                epoch_date[ 4 : 6 ] + '/' + epoch_date[ 6 : ] + '/' + epoch_date[ 0 : 4 ],
                "2000.0",
                absolute_magnitude,
                slope_parameter ]

            output_file.write( ','.join( components ) + '\n' )


def convert( in_file, out_file ):
    if in_file.endswith( ".gz" ):
        f_in = gzip.open( in_file, 'rt' )

    else:
        f_in = open( in_file, 'r' )

    f_out = open( out_file, 'w' )
    for line in f_in:
        process_and_write_one_line( line, f_out )

    f_in.close()
    f_out.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = \
            "Convert a minor planet text file such as astorb.dat or astorb.dat.gz from Lowell to XEphem format. " + \
            "If the file ends in '.gz' the file will be treated as a gzip file; otherwise the file is assumed to be text." )
    parser.add_argument( "in_file", help = "File to convert" )
    parser.add_argument( "out_file", help = "Output file to be created" )
    args = parser.parse_args()
    convert( args.in_file, args.out_file )
