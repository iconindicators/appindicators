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
Backend which creates the list of stars for astrobase and the star ephemerides
for astropyephem and astroskyfield.

                      *** NOT TO BE RUN DIRECTLY ***
'''


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


def _get_names_to_hips( iau_catalog_file ):
    '''
    Return a dictionary of star name (str) to HIP (int) for each star in the
    IAU Catalog of Star Names also present in the PyEphem list of stars.
    '''
    stars_from_pyephem = stars.stars.keys()
    names_to_hips = { }
    with open( iau_catalog_file, 'r', encoding = "utf-8" ) as f:
        for line in f:
            if not ( line.startswith( '#' ) or line.startswith( '$' ) ):
                try:
                    start = IAUCSN_NAME_START - 1
                    end = IAUCSN_NAME_END - 1 + 1
                    name = line[ start : end ].strip()
                    if name in stars_from_pyephem:
                        start = IAUCSN_HIP_START - 1
                        end = IAUCSN_HIP_END - 1 + 1
                        hip = int( line[ start : end ] )
                        names_to_hips[ name ] = hip

                except ValueError:
                    pass

    return names_to_hips


def _print_formatted_stars(
    names_to_hips ):

    print( f"\nList of stars for astrobase:" )
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

    print( "Done\n" )


def _create_ephemeris_skyfield(
    out_file,
    star_ephemeris,
    hipparcos_identifiers ):

    print( f"Creating { out_file } for astroskyfield..." )
    with load.open( star_ephemeris, 'r' ) as in_file, open( out_file, 'w' ) as f:
        for line in in_file:
            # HIP is located at bytes 9 - 14
            #    http://cdsarc.u-strasbg.fr/ftp/cats/I/239/ReadMe
            hip = int( line[ 9 - 1 : 14 - 1 + 1 ].strip() )
            if hip in hipparcos_identifiers:
                f.write( line )

    print( "Done\n" )


def _print_ephemeris_pyephem(
    planet_ephemeris,
    star_ephemeris,
    names_to_hips ):
    '''
    Taken from
        https://github.com/brandon-rhodes/pyephem/blob/master/bin/rebuild-star-data
    '''
    print( "Ephemeris for astropyephem..." )

    with load.open( star_ephemeris, 'r' ) as f:
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
    print( "Done\n" )


def create_ephemeris_stars(
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
