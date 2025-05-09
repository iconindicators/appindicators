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
Convert:
    Minor planets from Lowell Observatory to Skyfield / XEphem format.
    Minor planets file from Minor Planet Center to XEphem format.
    Comets file from Minor Planet Center to XEphem format.

Formats:
    https://asteroid.lowell.edu/astorb/
    https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
    https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501

  References:
    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/auxil/astorb2edb.pl
    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/auxil/mpcorb2edb.pl
    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/tools/mpccomet2edb.pl
'''


import argparse
import gzip
import textwrap


def get_unpacked_date(
    packed_date ):
    '''
    https://www.minorplanetcenter.net/iau/info/PackedDates.html
    '''

    def get_month_or_day_from_packed(
        packed_month_or_day ):

        if packed_month_or_day.isdigit():
            month_or_day = str( packed_month_or_day )

        else:
            month_or_day = str( ord( packed_month_or_day ) - ord( 'A' ) + 10 )

        return month_or_day


    century = packed_date[ 0 ]
    last_two_digits_of_year = packed_date[ 1 : 3 ]
    if century == 'I':
        year = 1800 + int( last_two_digits_of_year )

    elif century == 'J':
        year = 1900 + int( last_two_digits_of_year )

    else: # Assume K
        year = 2000 + int( last_two_digits_of_year )

    month = get_month_or_day_from_packed( packed_date[ 3 ] )
    day = get_month_or_day_from_packed( packed_date[ 4 ] )
    return month + '/' + day + '/' + str( year )


def get_packed_date(
    year,
    month,
    day ):
    '''
    https://www.minorplanetcenter.net/iau/info/PackedDates.html
    '''
    packed_year = year[ 2 : ]
    if int( year ) < 1900:
        packed_year = 'I' + packed_year

    elif int( year ) < 2000:
        packed_year = 'J' + packed_year

    else:
        packed_year = 'K' + packed_year


    def get_packed_day_month(
        day_or_month ):

        if int( day_or_month ) < 10:
            packed_day_month = str( int( day_or_month ) )

        else:
            packed_day_month = chr( int( day_or_month ) - 10 + ord( 'A' ) )

        return packed_day_month

    packed_month = get_packed_day_month( month )
    packed_day = get_packed_day_month( day )

    return packed_year + packed_month + packed_day


def process_line_and_write_lowell_minorplanet(
    line,
    output_file,
    to_skyfield ):
    '''
    https://asteroid.lowell.edu/astorb/
    https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501
    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/auxil/astorb2edb.pl
    '''
    # Field numbers:  1  2   3   4   5   6   7   8   9  10   11   12   13   14   15   16   17   18   19   20   21   22   23   24   25
    start_indices = [ 1, 8, 27, 43, 50, 55, 60, 66, 74, 96, 101, 107, 116, 127, 138, 149, 159, 170, 182, 191, 200, 208, 217, 234, 251 ]
    start_indices = [ x - 1 for x in start_indices ] # Offset back to zero to match each line read into a string.

    # Inspired by https://stackoverflow.com/a/10851479/2156453
    fields = (
        [ "OFFSET TO ALIGN WITH FIELD NUMBERING" ] +
        [ line[ i : j ] for i, j in zip( start_indices, start_indices[ 1 : ] + [ None ] ) ] )

    number = fields[ 1 ].strip()
    name = fields[ 2 ].strip()
    h = fields[ 4 ].strip()
    g = fields[ 5 ].strip()

    if len( name ) == 0:
        print( "Missing name:\n" + line )

    elif len( h ) == 0:
        print( "Missing H:\n" + line )

    elif len( g ) == 0:
        print( "Missing G:\n" + line )

    else:
        number_observations = fields[ 11 ].strip()
        epoch_date = fields[ 12 ].strip()
        mean_anomaly_epoch = fields[ 13 ].strip()
        argument_perihelion = fields[ 14 ].strip()
        longitude_ascending_node = fields[ 15 ].strip()
        inclination_to_ecliptic = fields[ 16 ].strip()
        orbital_eccentricity = fields[ 17 ].strip()
        semimajor_axis = fields[ 18 ].strip()

        if to_skyfield:
            components = [
                ' ' * 7, # number or designation packed
                ' ', # 8
                str( round( float( h ), 2 ) ).rjust( 5 ),
                ' ', # 14
                str( round( float( g ), 2 ) ).rjust( 5 ),
                ' ', # 20
                get_packed_date( epoch_date[ 0 : 4 ], epoch_date[ 4 : 6 ], epoch_date[ 6 : 8 ] ).rjust( 5 ),
                ' ', # 26
                str( round( float( mean_anomaly_epoch ), 5 ) ).rjust( 9 ),
                ' ', # 36
                ' ', # 37
                str( round( float( argument_perihelion ), 5 ) ).rjust( 9 ),
                ' ', # 47
                ' ', # 48
                str( round( float( longitude_ascending_node ), 5 ) ).rjust( 9 ),
                ' ', # 58
                ' ', # 59
                str( round( float( inclination_to_ecliptic ), 5 ) ).rjust( 9 ),
                ' ', # 69
                ' ', # 70
                str( round( float( orbital_eccentricity ), 7 ) ).rjust( 9 ),
                ' ', # 80
                ' ' * 11, # mean daily motion
                ' ', # 92
                str( round( float( semimajor_axis ), 7 ) ).rjust( 11 ),
                ' ', # 104
                ' ', # 105
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

            separator = ''

        else: # To XEphem
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
                epoch_date[ 4 : 6 ] + '/' + epoch_date[ 6 : 8 ] + '/' + epoch_date[ 0 : 4 ],
                "2000.0",
                h,
                g ]

            separator = ','

        output_file.write( separator.join( components ) + '\n' )


def process_line_and_write_minorplanetcenter_minorplanet_to_xephem(
    line,
    output_file ):
    '''
    https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501
    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/auxil/mpcorb2edb.pl
    '''
    # Field numbers:  0   1   2   3   4   5   6   7   8   9   10   11   12   13   14   15   16   17   18   19   20   21   22
    start_indices = [ 1,  9, 15, 21, 27, 38, 49, 60, 71, 81,  93, 106, 108, 118, 124, 128, 138, 143, 147, 151, 162, 167, 195 ]
    end_indices =   [ 7, 13, 19, 25, 35, 46, 57, 68, 79, 91, 103, 106, 116, 122, 126, 136, 141, 145, 149, 160, 165, 194, 202 ]

    # Offset back to zero to match lines read into a string.
    start_indices = [ x - 1 for x in start_indices ]
    end_indices = [ x - 1 for x in end_indices ]

    # Inspired by https://stackoverflow.com/a/10851479/2156453
    fields = [ line[ i : j + 1 ] for i, j in zip( start_indices, end_indices ) ]

    name = fields[ 21 ].replace( '(', '' ).replace( ')', '' ).strip()
    h = fields[ 1 ].strip()
    g = fields[ 2 ].strip()

    if len( name ) == 0:
        print( "Missing name:\n" + line )

    elif len( h ) == 0:
        print( "Missing H:\n" + line )

    elif len( g ) == 0:
        print( "Missing G:\n" + line )

    else:
        epoch_packed = fields[ 3 ].strip()
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
            get_unpacked_date( epoch_packed ),
            "2000.0",
            h,
            g ]

        output_file.write( ','.join( components ) + '\n' )


def process_line_and_write_minorplanetcenter_comet_to_xephem(
    line,
    output_file ):
    '''
    https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
    https://xephem.github.io/XEphem/Site/help/xephem.html#mozTocId468501
    https://github.com/XEphem/XEphem/blob/main/GUI/xephem/tools/mpccomet2edb.pl
    '''
    # Field numbers:  0  1   2   3   4   5   6   7   8   9  10  11  12  13  14   15   16   17
    start_indices = [ 1, 5,  6, 15, 20, 23, 31, 42, 52, 62, 72, 82, 86, 88, 92,  97, 103, 160 ]
    end_indices =   [ 4, 5, 12, 18, 21, 29, 39, 49, 59, 69, 79, 85, 87, 89, 95, 100, 158, 168 ]

    # Offset back to zero to match lines read into a string.
    start_indices = [ x - 1 for x in start_indices ]
    end_indices = [ x - 1 for x in end_indices ]

    # Inspired by https://stackoverflow.com/a/10851479/2156453
    fields = [ line[ i : j + 1 ] for i, j in zip( start_indices, end_indices ) ]

    name = fields[ 16 ].replace( '(', '' ).replace( ')', '' ).strip()

    # The perl script reference refers to H, G in reverse to that specified in
    # the comet format.
    h = fields[ 14 ].strip()
    g = fields[ 15 ].strip()

    if len( name ) == 0:
        print( "Missing name:\n" + line )

    elif len( h ) == 0:
        print( "Missing H:\n" + line )

    elif len( g ) == 0:
        print( "Missing G:\n" + line )

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

        if float( orbital_eccentricity ) < 0.99: # Elliptical orbit.
            components = [
                name,
                'e',
                inclination,
                longitude_ascending_node,
                argument_perihelion,
                str( float( perihelion_distance ) / ( 1.0 - float( orbital_eccentricity ) ) ),
                '0',
                orbital_eccentricity,
                '0',
                epoch_date,
                "2000.0",
                h,
                g ]

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
                h,
                g ]

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
                h,
                g ]

        output_file.write( ','.join( components ) + '\n' )


def convert(
    option,
    in_file,
    out_file ):

    def process(
        f_in,
        f_out ):

        functions = {
            1 : process_line_and_write_lowell_minorplanet,
            2 : process_line_and_write_lowell_minorplanet,
            3 : process_line_and_write_minorplanetcenter_minorplanet_to_xephem,
            4 : process_line_and_write_minorplanetcenter_comet_to_xephem }

        parameters = {
            1 : ( f_out, True ),
            2 : ( f_out, False ),
            3 : ( f_out, ),
            4 : ( f_out, ) }

        for line in f_in:
            if len( line.strip() ) > 0:
                functions[ option ]( line, *parameters[ option ] )


    with open( out_file, 'w', encoding = "utf-8" ) as f_out:
        if in_file.endswith( ".gz" ):
            with gzip.open( in_file, 'rt' ) as f_in:
                process( f_in, f_out )

        else:
            with open( in_file, 'r', encoding = "utf-8" ) as f_in:
                process( f_in, f_out )


if __name__ == "__main__":
    description = (
        textwrap.dedent( '''\
            Convert an ephemeris file for minor planets or comets...

            1) Convert a minor planets file from Lowell Observatory
               (such as astorb.dat or astorb.dat.gz) to Skyfield format.

            2) Convert a minor planets file from Lowell Observatory
               (such as astorb.dat or astorb.dat.gz) to XEphem format.

            3) Convert a minor planets file from Minor Planet Center
               (such as MPCORB.DAT or MPCORB.DAT.gz) to XEphem format.

            4) Convert a comets file from Minor Planet Center
               (such as CometEls.txt) to XEphem format.

            An input file ending in .gz will be treated as a gzip file;
            otherwise the input file will be treated as text.

            The output will ALWAYS be written to a text file.

            ------------------------------------------------------------------------
            --- INPUT & OUTPUT PATHNAMES CONTAINING SPACES MUST BE DOUBLE QUOTED ---
            ------------------------------------------------------------------------''' ) )

    parser = (
        argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = description ) )

    parser.add_argument( "option", type = int, choices = [ 1, 2, 3, 4 ] )

    parser.add_argument( "in_file", help = "File to convert" )

    parser.add_argument( "out_file", help = "Output file to be created" )

    args = parser.parse_args()
    convert( args.option, args.in_file, args.out_file )
