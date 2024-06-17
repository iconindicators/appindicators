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


# Convert minor planet data in Lowell format to MPC format.
#
# Lowell format:
#    https://asteroid.lowell.edu/main/astorb/
#
# MPC format:
#    https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html


import argparse
import gzip


# https://www.minorplanetcenter.net/iau/info/PackedDates.html
def get_packed_date( year, month, day ):
    packed_year = year[ 2 : ]
    if int( year ) < 1900:
        packed_year = 'I' + packed_year

    elif int( year ) < 2000:
        packed_year = 'J' + packed_year

    else:
        packed_year = 'K' + packed_year


    def get_packed_day_month( day_or_month ):
        if int( day_or_month ) < 10:
            packed_day_month = str( int( day_or_month ) )

        else:
            packed_day_month = chr( int( day_or_month ) - 10 + ord( 'A' ) )

        return packed_day_month

    packed_month = get_packed_day_month( month )
    packed_day = get_packed_day_month( day )

    return packed_year + packed_month + packed_day


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
            number_observations = parts[ 11 ].strip()
            epoch_date = parts[ 12 ].strip()
            mean_anomaly_epoch = parts[ 13 ].strip()
            argument_perihelion = parts[ 14 ].strip()
            longitude_ascending_node = parts[ 15 ].strip()
            inclination_to_ecliptic = parts[ 16 ].strip()
            orbital_eccentricity = parts[ 17 ].strip()
            semimajor_axis = parts[ 18 ].strip()

            components = [
                ' ' * 7, # number or designation packed
                ' ', # 8
                str( round( float( absolute_magnitude ), 2 ) ).rjust( 5 ),
                ' ', # 14
                str( round( float( slope_parameter ), 2 ) ).rjust( 5 ),
                ' ', # 20
                get_packed_date( epoch_date[ 0 : 4 ], epoch_date[ 4 : 6 ], epoch_date[ 6 : 8 ] ).rjust( 5 ),
                ' ', # 26
                str( round( float( mean_anomaly_epoch ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 36, 37
                str( round( float( argument_perihelion ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 47, 48
                str( round( float( longitude_ascending_node ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 58, 59
                str( round( float( inclination_to_ecliptic ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 69, 70
                str( round( float( orbital_eccentricity ), 7 ) ).rjust( 9 ),
                ' ', # 80
                ' ' * 11, # mean daily motion
                ' ', # 92
                str( round( float( semimajor_axis ), 7 ) ).rjust( 11 ),
                ' ' * 2, # 104, 105
                ' ', # uncertainty parameter
                ' ', # 107
                ' ' * 9, # reference
                ' ', # 117
                number_observations.rjust( 5 ),
                ' ', # 123
                ' ' * 3, # oppositions
                ' ', # 127
                ' ' * ( 4 + 1 + 4 ), # multiple/single oppositions
                ' ', # 137
                ' ' * 4, # rms residual
                ' ', # 142
                ' ' * 3, # coarse indicator of perturbers
                ' ', # 146
                ' ' * 3, # precise indicator of perturbers
                ' ', # 150
                ' ' * 10, # computer name
                ' ', # 161
                ' ' * 4, # hexdigit flags
                ' ', # 166
                ( number + ' ' + name ).strip().ljust( 194 - 167 + 1 ),
                ' ' * 8 ] # date last observation

            output_file.write( ''.join( components ) + '\n' )


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
            "Convert a minor planet text file such as astorb.dat or astorb.dat.gz from Lowell to MPC format. " + \
            "If the file ends in '.gz' the file will be treated as a gzip file; otherwise the file is assumed to be text." )
    parser.add_argument( "in_file", help = "File to convert" )
    parser.add_argument( "out_file", help = "Output file to be created" )
    args = parser.parse_args()
    convert( args.in_file, args.out_file )

