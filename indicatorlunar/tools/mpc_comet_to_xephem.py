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


# Convert comet data in MPC format to XEphem format.
#
# Inspired by:
#    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/tools/mpccomet2edb.pl
#
# MPC format:
#    https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
#
# XEphem format:
#    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501


import argparse


def process_and_write_one_line( line, out_file ):
    if len( line.strip() ) > 0:
        # Field numbers:  0  1   2   3   4   5   6   7   8   9  10  11  12  13  14   15   16   17
        start_indices = [ 1, 5,  6, 15, 20, 23, 31, 42, 52, 62, 72, 82, 86, 88, 92,  97, 103, 160 ]
        end_indices =   [ 4, 5, 12, 18, 21, 29, 39, 49, 59, 69, 79, 85, 87, 89, 95, 100, 158, 168 ]

        # Offset back to zero to match lines read into a string.
        start_indices = [ x - 1 for x in start_indices ]
        end_indices = [ x - 1 for x in end_indices ]

        fields = [ line[ i : j + 1 ] for i, j in zip( start_indices, end_indices ) ] # Inspired by https://stackoverflow.com/a/10851479/2156453
        name = fields[ 16 ].replace( '(', '' ).replace( ')', '' ).strip()
        absolute_magnitude = fields[ 14 ].strip()

        if len( name ) == 0:
            print( "Missing name:\n" + line )

        elif len( absolute_magnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )

        else:
            year = fields[ 3 ].strip()
            month = fields[ 4 ].strip()
            day = fields[ 5 ].strip()
            epoch_date = month + '/' + day + '/' + year

            perihelion_distance = fields[ 6 ].strip()
            orbital_eccentricity = fields[ 7 ].strip()
            argument_perihelion = fields[ 8 ].strip()
            longitude_ascending_node = fields[ 9 ].strip()
            inclination = fields[ 10 ].strip()
            slope_parameter = fields[ 15 ].strip()

            if float( orbital_eccentricity ) < 0.99: # Elliptical orbit.
                mean_anomaly = str( 0.0 )
                mean_distance = str( float( perihelion_distance ) / ( 1.0 - float( orbital_eccentricity ) ) )

                components = [
                    name,
                    'e',
                    inclination,
                    longitude_ascending_node,
                    argument_perihelion,
                    mean_distance,
                    '0',
                    orbital_eccentricity,
                    mean_anomaly,
                    epoch_date,
                    "2000.0",
                    absolute_magnitude,
                    slope_parameter ]

            elif float( orbital_eccentricity ) > 1.0: # Hyperbolic orbit.
                components = [
                    name,
                    'h',
                    epoch_date,
                    inclination,
                    longitude_ascending_node,
                    argument_perihelion,
                    orbital_eccentricity,
                    perihelion_distance,
                    "2000.0",
                    absolute_magnitude,
                    slope_parameter ]

            else: # Parabolic orbit.
                components = [
                    name,
                    'p',
                    epoch_date,
                    inclination,
                    argument_perihelion,
                    perihelion_distance,
                    longitude_ascending_node,
                    "2000.0",
                    absolute_magnitude,
                    slope_parameter ]

            out_file.write( ','.join( components ) + '\n' )


def convert( in_file, out_file ):
    f_in = open( in_file, 'r' )
    f_out = open( out_file, 'w' )
    for line in f_in:
        process_and_write_one_line( line, f_out )

    f_in.close()
    f_out.close()


if __name__ == "__main__":
    description = "Convert a comet text file such as CometEls.txt from MPC to XEphem format."
    parser = argparse.ArgumentParser( description = description )

    parser.add_argument( "in_file", help = "File to convert" )

    parser.add_argument( "out_file", help = "Output file to be created" )

    args = parser.parse_args()
    convert( args.in_file, args.out_file )
